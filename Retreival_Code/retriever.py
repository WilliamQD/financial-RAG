import json
import re
from typing import Tuple, Dict, Any, List, Optional
from pinecone_client import retrieve_from_namespace, retrieve_academic_text, retrieve_academic_text_query
from prompt_builder import build_q1, build_q2
from llm_client import client
from models import ProjectsPayload, Project

# define QUESTION_1, QUESTION_2 here

QUESTION_1 = """
1. Read the Business Description Section: Describe the company’s core business and strategic direction.
2. Read the Management Discussion and Analysis: Analyze the MD&A section to grasp management’s interpretation of past performance, current challenges, and future outlook.
3. Identify Current Investment Focus: Determine the company’s current projects and business model as disclosed in the annual report.
4. Analyze the Market and Competitive Environment: Examine the industry dynamics and competitive environment mentioned in the annual report.

Please provide a detailed report summarizing your findings from these steps.
"""

QUESTION_2 = """
Based on your previous analysis, your next task is to predict the company’s next three potential projects for consideration.

Formatting Guidelines:
  - Return **only** JSON that matches the given schema.
  - Each object must include:
    “PROJECT”: The name of the proposed project.
    “DESCRIPTION”: A brief description of the project.
    “MARKET VALUE”: Estimated market value in million dollars USD.
    “IMPLEMENTATION COST”: Estimated cost to implement the project in million dollars USD. Can be larger than market value.
    “REASONING”: Explanation for why this project is proposed.
      • **In your reasoning**, call out the key drivers—projected revenues, operating expenses (materials, labor), R&D spend, capital intensity, and market conditions—that justify your estimates.
    “CONFIDENCE”: A confidence level in the prediction (0-100).
    “SIMILAR FIRMS”: A list of three public firms engaged in similar businesses, including their names and tickers.
    “PRIORITY”: A priority ranking (1-3). 1 is highest.
    “PRIORITY_REASONING”: Justification for the assigned priority.

Additional Guidance (do **not** include these bullets in your output):
  - Academic studies of Tobin's q (market value / implementation cost) report a distribution with **mean=1.11**, **median=0.57**, **std = 1.91**, and **skewness = 3.76**. 
  - Use your financial judgment—think about sales growth, margin profiles, capital intensity, and risk factors—when assigning each MARKET VALUE and IMPLEMENTATION COST.
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




def extract_q_values(
    projects: List[Project]
) -> Tuple[Optional[float], Optional[float], Optional[float]]:
    """
    Given a list of Project objects, return the three q‑ratios:
      q1 = projects[0].market_value / projects[0].implementation_cost
      q2 = projects[1].market_value / projects[1].implementation_cost
      q3 = projects[2].market_value / projects[2].implementation_cost
    """
    if not projects or len(projects) < 3:
        return None, None, None
    try:
        q1 = projects[0].market_value / projects[0].implementation_cost
        q2 = projects[1].market_value / projects[1].implementation_cost
        q3 = projects[2].market_value / projects[2].implementation_cost
    except Exception:
        return None, None, None
    return q1, q2, q3

def generate_predictions(gvkey, fyear, cusip, comn):
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

    # PART 3: Q1
    q1_prompt = build_q1(
        company_name=comn,
        gvkey=gvkey,
        fyear=fyear,
        item1_and_item7_text=combined_10k,
        conference_call_text=text_conf_call,
        patents_text=patents_text,
        wsj_text=wsj_text,
        academic_research_text=acedemic_research_text,
        question=QUESTION_1
    )
    resp1 = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": q1_prompt}],
        max_tokens=1024,
        temperature=0.0
    )
    answer_q1 = resp1.choices[0].message.content.strip()

    # PART 4: Q2
    chat_hist = f"User asked Q1: {QUESTION_1}\nAssistant answered: {answer_q1}"
    q2_prompt = build_q2(
        chat_history_str=chat_hist,
        question=QUESTION_2
    )
    resp2 = client.beta.chat.completions.parse(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": q2_prompt}],
        max_tokens=1500,
        temperature=0.0,
        response_format=ProjectsPayload
    )
    answer_q2_projects = resp2.choices[0].message.parsed.projects
    answer_q2 = json.loads(resp2.choices[0].message.parsed.model_dump_json())

    # PART 5: extract q1,q2,q3
    q1, q2, q3 = extract_q_values(answer_q2_projects)

    part1_queries_str = "\n\n".join(f"{ns}: {qry}" for ns, qry in part1_queries.items())

    return {
        "gvkey": gvkey,
        "fyear": fyear,
        "part1_queries": part1_queries_str,
        "q1_prompt": q1_prompt,
        "q1_answer": answer_q1,
        "q2_answer": answer_q2,
        "q1": q1,
        "q2": q2,
        "q3": q3
    }