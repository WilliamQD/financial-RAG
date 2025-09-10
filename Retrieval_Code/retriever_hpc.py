from typing import Tuple, Dict, Any, List, Optional

from pinecone_client import (
    retrieve_from_namespace,
    retrieve_academic_text,
    retrieve_academic_text_query,
    retrieve_and_rerank,
)
from prompt_builder import build_q1, build_financial_data, DEV_MSG, HIGH_Q_EXAMPLE

# Use the local helpers that talk to your HPC server via /v1/responses
from llm_client_hpc import responses_create_text, responses_parse_local
from models import ProjectsPayload, create_json_schema, create_response_format


# define QUESTION_1, QUESTION_2 here
QUESTION_1 = """
1. Read the Business Description Section: Describe the company's core business and strategic direction.
2. Read the Management Discussion and Analysis: Analyze the MD&A section to grasp management's interpretation of past performance, current challenges, and future outlook.
3. Identify Current Investment Focus: Determine the company's current projects and business model as disclosed in the annual report.
4. Analyze the Market and Competitive Environment: Examine the industry dynamics and competitive environment mentioned in the annual report.

Please provide a detailed report summarizing your findings from these steps.
"""

QUESTION_2 = """
Using the prior analysis you just produced, predict the company's next three potential projects for consideration.

For each project, provide:
- PROJECT: A concise name.
- DESCRIPTION: A brief description.
- MARKET VALUE: An estimated market value in million USD.
- IMPLEMENTATION COST: An estimated cost to implement the project in million USD. Can be larger than market value.
- REASONING: Justify your estimates using key drivers (revenues, expenses, R&D, capital intensity, market conditions).
- CONFIDENCE: Confidence (0-100).
- SIMILAR FIRMS: Three public peers (name + ticker).
- PRIORITY: Rank 1-3.
- PRIORITY_REASONING: Why you chose that priority.

**Guidance** (for your internal reasoning only):
- Tobin's q = market value / implementation cost.
- From academic studies, q has mean≈1.11, median≈0.57, std≈1.91, skew≈3.76.
- Anchor cost/value to the firm's metrics.
"""


def make_conf_call_query(company: str, year: int) -> str:
    """Build a focused conference-call query string."""
    return (
        f"{year} {company} conference call highlights: "
        "financial performance, key strategic priorities"
    )


def make_namespaces_query(
    namespace: str,
    company: str,
    fyear: int,
    conference_call_text: str,
) -> str:
    """
    Memoryless helper:
      Returns one string: 2–3 sentence summary + two keyword queries for a given namespace.
    """
    ns_map = {
        "10K-item1": "10-K MD&A & Business Description",
        "10K-item7": "10-K Financial Notes",
        "patents": "Patent Filings",
        "wsj_frontpage": "WSJ Front Page",
    }
    ns = ns_map[namespace]
    prompt = (
        "You are an expert financial researcher.\n"
        f"Here is {company}’s conference‐call excerpt for fiscal year {fyear}:\n\n"
        f"{conference_call_text or '[No transcript available]'}\n\n"
        "1) Write a 2–3 sentence summary of the key points.\n"
        "2) Then list TWO short keyword queries (4–6 terms each) for retrieving "
        f"from the “{ns}” index.\n"
        "Output one single string: the summary first, then the two queries."
    )

    text = responses_create_text(
        messages=[{"role": "user", "content": prompt}],
        temperature=0.0,
        max_output_tokens=200,
    )
    return text.strip()


def extract_q_values(projects):
    """
    Given a list of Project objects, always return exactly three (q, market_value, cost) tuples:
      [(q1, mk1, cost1), (q2, mk2, cost2), (q3, mk3, cost3)].

    For each i in {0,1,2}:
      - If projects[i] exists and its cost≠0, compute q = mk / cost.
      - Otherwise, return (None, None, None) for that slot.
    """
    results = []
    for i in range(3):
        try:
            proj = projects[i]
            mk = proj.market_value
            cost = proj.implementation_cost
            q = mk / cost
        except (IndexError, AttributeError, ZeroDivisionError, TypeError):
            q = mk = cost = None
        results.append((q, mk, cost))
    return results


def generate_predictions(gvkey, fyear, cusip, comn, comp_row, verbose=False):
    """
    1. Seeds retrieval from conference calls
    2. Generates per-namespace queries (memoryless)
    3. Retrieves 10-K, patents, and WSJ text
    4. Builds Q1 & Q2 prompts and calls the LLM (Q2 is chained to Q1 via messages)
    5. Extracts q1, q2, q3 ratios
    6. Returns a dict of all results
    """
    gvkey_str = str(gvkey)
    print(f"\nProcessing {comn} ({gvkey_str}) in {fyear}\n")

    # PART 1: conference-call seed & namespace queries
    conf_call_query = make_conf_call_query(comn, fyear)
    conf_call_filter = {"fiscal_year": {"$lte": fyear}, "CUSIP": cusip}
    text_conf_call = retrieve_and_rerank(
        query=conf_call_query,
        namespace="conference_call",
        metadata_filter=conf_call_filter,
        top_k=40,
        top_n=10,
    )

    namespaces = ["10K-item1", "10K-item7", "patents", "wsj_frontpage"]
    part1_queries: Dict[str, str] = {}
    for ns in namespaces:
        part1_queries[ns] = make_namespaces_query(ns, comn, fyear, text_conf_call)

    # PART 2: retrieve from each namespace
    item1_text = retrieve_and_rerank(
        query=part1_queries["10K-item1"],
        namespace="10K-item1",
        metadata_filter={"fyear": {"$lte": fyear}, "gvkey": gvkey},
        top_k=40,
        top_n=10,
    )

    item7_text = retrieve_and_rerank(
        query=part1_queries["10K-item7"],
        namespace="10K-item7",
        metadata_filter={"fyear": {"$lte": fyear}, "gvkey": gvkey},
        top_k=40,
        top_n=10,
    )
    combined_10k = "\n----\n".join([item1_text, item7_text])

    patents_text = retrieve_and_rerank(
        query=part1_queries["patents"],
        namespace="patents",
        metadata_filter={"filing_year": {"$lte": fyear}, "gvkey": gvkey_str},
        top_k=20,
        top_n=5,
    )
    wsj_text = retrieve_and_rerank(
        query=part1_queries["wsj_frontpage"],
        namespace="wsj_frontpage",
        metadata_filter={"year": {"$lte": fyear}},
        top_k=20,
        top_n=5,
    )

    academic_research_text = retrieve_academic_text_query()

    if comp_row.empty:
        print(f"No comp data for gvkey={gvkey}, fyear={fyear}")
        financial_data = ""
    else:
        row = comp_row.iloc[0]
        financial_data = build_financial_data(
            row["firm_asset"],
            row["firm_sale"],
            row["firm_emp"],
            row["firm_bkleverage"],
            row["firm_profitability"],
            row["firm_roa"],
            row["firm_cash2at"],
            row["v"],
            row["k_phys"],
            row["i_phys"],
            row["i_int"],
            row["xrd"],
            row["i_tot"],
            row["k_tot"],
            row["q_tot"],
        )

    # -----------------------
    # PART 3: Q1 (standalone)
    # -----------------------
    q1_prompt = build_q1(
        company_name=comn,
        gvkey=gvkey,
        fyear=fyear,
        financial_data=financial_data,
        item1_and_item7_text=combined_10k,
        conference_call_text=text_conf_call,
        patents_text=patents_text,
        wsj_text=wsj_text,
        academic_research_text=academic_research_text,
        question=QUESTION_1,
    )

    messages_q1 = [
        DEV_MSG,                      # your system/priming message
        {"role": "user", "content": q1_prompt},
    ]

    answer_q1 = responses_create_text(
        messages=messages_q1,
        temperature=0.0,
        max_output_tokens=1200,
        # reasoning={"effort": "medium"},  # optional; harmless if server ignores
    )

    # -----------------------
    # PART 4: Q2 (CHAINED)
    # -----------------------
    # Q2 must "see" Q1 → include both q1 prompt and assistant answer before the Q2 user turn.
    messages_q2 = [
        DEV_MSG,  # same system prompt for continuity
        {"role": "user", "content": q1_prompt},           # show what we asked
        {"role": "assistant", "content": answer_q1},      # show model's Q1 answer
        {"role": "user", "content": QUESTION_2},          # now ask Q2
    ]

    answer_q2_payload = responses_parse_local(
        messages=messages_q2,
        schema_model=ProjectsPayload,
        # Keep temperature low for JSON compliance; adjust tokens to your VRAM budget
        temperature=0.2,
        max_output_tokens=1500,
        # Strongly nudge strict JSON adherence
        response_format=create_response_format(),
        # reasoning={"effort": "medium"},  # optional
    )
    answer_q2 = answer_q2_payload.projects

    # PART 5: extract q1,q2,q3, mk1, cost1, mk2, cost2, mk3, cost3
    qs = extract_q_values(answer_q2)
    proj1, proj2, proj3 = qs
    q1, mk1, cost1 = proj1
    q2, mk2, cost2 = proj2
    q3, mk3, cost3 = proj3

    part1_queries_str = "\n\n".join(f"{ns}: {qry}" for ns, qry in part1_queries.items())

    result = {
        "gvkey": gvkey,
        "fyear": fyear,
        "q1": q1,
        "q2": q2,
        "q3": q3,
        "mkv1": mk1,
        "cost1": cost1,
        "mkv2": mk2,
        "cost2": cost2,
        "mkv3": mk3,
        "cost3": cost3,
    }
    if verbose:
        result["part1_queries"] = part1_queries_str
        result["q1_prompt"] = q1_prompt
        result["q1_answer"] = answer_q1
        result["q2_answer"] = answer_q2

    return result


if __name__ == "__main__":
    # Minimal local test for schema wiring (replace QUESTION_2 with your own short payload if desired)
    payload = responses_parse_local(
        messages=[{"role": "user", "content": QUESTION_2}],
        schema_model=ProjectsPayload,
        max_output_tokens=800,
        response_format=create_response_format(),
    )
    print(payload.projects)
    qs = extract_q_values(payload.projects)
