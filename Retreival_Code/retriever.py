import json
import re
from typing import Tuple, Dict, Any, List, Optional
from pinecone_client import retrieve_from_namespace, retrieve_academic_text, retrieve_academic_text_query
from prompt_builder import build_q1, build_financial_data
from llm_client import client
from models import ProjectsPayload, Project

# define QUESTION_1, QUESTION_2 here

QUESTION_1 = """
1. Read the Business Description Section: Describe the company's core business and strategic direction.
2. Read the Management Discussion and Analysis: Analyze the MD&A section to grasp management's interpretation of past performance, current challenges, and future outlook.
3. Identify Current Investment Focus: Determine the company's current projects and business model as disclosed in the annual report.
4. Analyze the Market and Competitive Environment: Examine the industry dynamics and competitive environment mentioned in the annual report.

Please provide a detailed report summarizing your findings from these steps.
"""

QUESTION_2 = """
Based on your previous analysis, your next task is to predict the company's next three potential projects for consideration. 

For each project, provide:
- PROJECT: A concise name for the proposed project.
- DESCRIPTION: A brief description of the project.
- MARKET VALUE: An estimated market value in million USD.
- IMPLEMENTATION COST: An estimated cost to implement the project in million USD. Can be larger than market value.
- REASONING: A detailed explanation justifying the project, including key drivers such as projected revenues, operating expenses (materials, labor), R&D spend, capital intensity, and market conditions.
- CONFIDENCE: Your confidence level in the prediction (0-100).
- SIMILAR FIRMS: A list of three public firms engaged in similar businesses, including their names and tickers.
- PRIORITY: A priority ranking (1-3), where 1 is the highest.
- PRIORITY_REASONING: Justification for the assigned priority.

**Guidance for realistic estimation (for reference only, not to appear in output):**
- Tobin's q is (market value / implementation cost). Empirical distribution: mean=1.11, median=0.57, std=1.91, skewness=3.76.
"""



def make_conf_call_query(
    company: str,
    year: int
) -> str:
    """
    Build a focused conference-call query string.
    """
    return (
        f"{year} {company} conference call highlights: "
        "financial performance, key strategic priorities"
    )



def make_namespaces_query(
    namespace: str,
    company: str,
    fyear: int,
    conference_call_text: str
) -> Tuple[str, List[str]]:
    """
    Returns:
      - summary: a 2–3 sentence distillation of the call
      - queries: a list of two short (4–6 term) keyword queries
      - the actual return is combined to a single string for retrieval
    """
    ns_map = {
      "10K-item1": "10‑K MD&A & Business Description",
      "10K-item7": "10‑K Financial Notes",
      "patents":   "Patent Filings",
      "wsj_frontpage": "WSJ Front Page"
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
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.0,
        max_tokens=200
    )
    return resp.choices[0].message.content.strip()




def extract_q_values(projects):
    """
    Given a list of Project objects, always return exactly three (q, market_value, cost) tuples:
      [(q1, mk1, cost1), (q2, mk2, cost2), (q3, mk3, cost3)].

    For each i in {0,1,2}:
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

    

def generate_predictions(gvkey, fyear, cusip, comn, comp_row):
    """
    1. Seeds retrieval from conference calls
    2. Generates per‑namespace queries based on those calls
    3. Retrieves 10-K, patents, and WSJ text
    4. Builds Q1 & Q2 prompts and calls the LLM
    5. Extracts q1, q2, q3 ratios
    6. Returns a dict of all results
    """
    gvkey_str = str(gvkey)

    # a print msg of what year and gvkey we're working with
    print(f"\nProcessing {comn} ({gvkey_str}) in {fyear}\n")

    # PART 1: conference‑call seed & namespace queries
    conf_call_query = make_conf_call_query(comn, fyear)
    conf_call_filter = {"fiscal_year": {"$lte": fyear}, "CUSIP": cusip}
    text_conf_call = retrieve_from_namespace(
        query=conf_call_query,
        namespace="conference_call",
        metadata_filter=conf_call_filter,
        top_k=20
    )

    # Build a set of queries per namespace
    namespaces = ["10K-item1", "10K-item7", "patents", "wsj_frontpage"]
    part1_queries: Dict[str, str] = {}
    for ns in namespaces:
        part1_queries[ns] = make_namespaces_query(ns, comn, fyear, text_conf_call)
    
    # PART 2: retrieve from each namespace
    item1_text = retrieve_from_namespace(
        query=part1_queries["10K-item1"],
        namespace="10K-item1",
        metadata_filter={"fyear": {"$lte": fyear}, "gvkey": gvkey},
        top_k=20
    )

    item7_text = retrieve_from_namespace(
        query=part1_queries["10K-item7"],
        namespace="10K-item7",
        metadata_filter={"fyear": {"$lte": fyear}, "gvkey": gvkey},
        top_k=20
    )
    combined_10k = "\n----\n".join([item1_text, item7_text])

    patents_text = retrieve_from_namespace(
        query=part1_queries["patents"],
        namespace="patents",
        metadata_filter={"filing_year": {"$lte": fyear}, "gvkey": gvkey_str},
        top_k=10
    )
    wsj_text = retrieve_from_namespace(
        query=part1_queries["wsj_frontpage"],
        namespace="wsj_frontpage",
        metadata_filter={"year": {"$lte": fyear}},
        top_k=10
    )

    acedemic_research_text = retrieve_academic_text_query()

    if comp_row.empty:
        print(f"No comp data for gvkey={gvkey}, fyear={fyear}")
        financial_data = ""
    else:
        row = comp_row.iloc[0]
        financial_data = build_financial_data(
            row["firm_asset"],row["firm_sale"],row["firm_emp"],
            row["firm_bkleverage"],row["firm_profitability"],row["firm_roa"],row["firm_cash2at"],
            row["v"],row["k_phys"],row["i_phys"],row["i_int"],row["xrd"],row["i_tot"],row["k_tot"]
        )

    q1_prompt = build_q1(
        company_name=comn,
        gvkey=gvkey,
        fyear=fyear,
        financial_data=financial_data,
        item1_and_item7_text=combined_10k,
        conference_call_text=text_conf_call,
        patents_text=patents_text,
        wsj_text=wsj_text,
        academic_research_text=acedemic_research_text,
        question=QUESTION_1
    )

    resp1 = client.responses.create(
        model="o3-mini",
        reasoning={"effort": "medium"},
        input=[
            {
                "role": "user", 
                "content": q1_prompt
            }
        ],
        # max_tokens=1024,
        # temperature=0.0
    )
    answer_q1 = resp1.output_text.strip()
    first_response_id = resp1.id

    # PART 4: Q2
    resp2 = client.responses.parse(
        model="o3-mini",
        reasoning={"effort": "medium"},
        input=[
            {
                "role": "user", 
                "content": QUESTION_2
            }
        ],
        # max_completion_tokens=1500, # need to figure out how reasoning model max tokens work
        # temperature=0.9, # no temp setting for parse
        text_format=ProjectsPayload,
        previous_response_id=first_response_id
    )
    answer_q2 = resp2.output_parsed.projects

    # PART 5: extract q1,q2,q3, mk1, cost1, mk2, cost2, mk3, cost3
    qs = extract_q_values(answer_q2)
    proj1 = qs[0]
    proj2 = qs[1]
    proj3 = qs[2]
    q1, mk1, cost1 = proj1
    q2, mk2, cost2 = proj2
    q3, mk3, cost3 = proj3


    part1_queries_str = "\n\n".join(f"{ns}: {qry}" for ns, qry in part1_queries.items())

    return {
        "gvkey": gvkey,
        "fyear": fyear,
        # "part1_queries": part1_queries_str, # diagnostic
        # "q1_prompt": q1_prompt, # diagnostic
        # "q1_answer": answer_q1, # diagnostic
        # "q2_answer": answer_q2, # diagnostic
        "q1": q1,
        "q2": q2,
        "q3": q3,
        "mkv1": mk1,
        "cost1": cost1,
        "mkv2": mk2,
        "cost2": cost2,
        "mkv3": mk3,
        "cost3": cost3
    }

if __name__ == "__main__":
    resp2 = client.responses.parse(
        model="o4-mini",
        reasoning={"effort": "medium"},
        input=[
            {
                "role": "user", 
                "content": QUESTION_2
            }
        ],
        # max_completion_tokens=1500,
        # temperature=0.9,
        text_format=ProjectsPayload
    )
    print(resp2.output_parsed.projects)
    answer_q2_projects = resp2.output_parsed.projects
    qs = extract_q_values(answer_q2_projects)