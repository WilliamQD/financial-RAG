# Q1 & Q2 prompt templates and builders
DEV_MSG = {
    "role": "developer",
    "content": 
    """You are a financial-services reasoning model.
You perfectly understand how Tobin's q is calculated and what drives it. Tobin's q =  Market Value / Total Capital Stock.
From academic studies, q has mean≈1.11, median≈0.57, std≈1.91, skew≈3.76.
Use the firm's provided metrics as anchors when estimating MARKET VALUE and IMPLEMENTATION COST.
"""
}

HIGH_Q_EXAMPLE = {
    "role":"developer","content": 
    """
Example:

Input:
```Firm Metrics:
  Asset: 5000
  Sales: 3000
  R&D Investment: 400
  Total Capital Stock: 2500
Output JSON:
[
{
"project": "Next-Gen GPU Architecture",
"description": "Develop an advanced GPU optimized for AI workloads across data centers.",
"market_value": 1200,
"implementation_cost": 600,
"tobin_q": 2.0,
"reasoning": "Given R&D spend of 400 (8% of assets) and surging AI demand, a 40% revenue uplift yields 1200 market value; cost aligns with 12% of assets.",
"confidence": 85,
"similar_firms": [
{"name": "AMD", "ticker": "AMD"},
{"name": "Intel", "ticker": "INTC"},
{"name": "NVIDIA", "ticker": "NVDA"}
],
"priority": 1,
"priority_reasoning": "High ROI and aligns with core strengths."
}
]
"""
}


Q1_TEMPLATE = """
The firm to analyze is {company_name}, identified by the gvkey number {gvkey}. The current year is {fyear}.
You will be provided several sections of information and based on these information, please perform the tasks at the end and provide detailed analyses.

=== FINANCIAL DATA FOR {company_name} IN THE CURRENT YEAR ===
Note: MM = million, K = thousand, % = percentage
{financial_data}
=== END OF FINANCIAL DATA ===

=== QUARTER/ANNUAL REPORTS FOR {company_name} IN THE PAST YEARS ===
{item1_and_item7_text}
=== END OF REPORTS ===

=== CONFERENCE CALL EVENT TEXT BY {company_name} IN THE PAST YEARS ===
{conference_call_text}
=== END OF CONFERENCE CALL EVENT TEXT ===

=== PATENTS BY {company_name} IN THE PAST YEARS ===
{patents_text}
=== END OF PATENTS ===

=== WALL STREET JOURNAL FRONT PAGE ARTICLE TEXT IN THE PAST YEARS ===
{wsj_text}
=== END OF ARTICLE ===

=== ACADEMIC RESEARCH TEXT ON TOBIN'S Q RATIO (MARKET VALUE / IMPLEMENTATION COST) ===
{academic_research_text}
=== END OF ACADEMIC RESEARCH TEXT ===

=== QUESTION ===
{question}
=== END OF QUESTION ===
"""

def build_financial_data(
    firm_asset, firm_sale, firm_emp, firm_bkleverage,
    firm_profitability, firm_roa, firm_cash2at,
    v, k_phys, i_phys, i_int, xrd, i_tot, k_tot,
    q_tot = 0
) -> str:
    """
    Assemble all financial metrics into a single string, one per line.
    """
    return (
        f"Asset: {firm_asset} MM\n"
        f"Sales: {firm_sale} MM\n"
        f"Employees: {firm_emp} K\n"
        f"Leverage: {firm_bkleverage} %\n"
        f"Profitability: {firm_profitability} %\n"
        f"Return on Asset: {firm_roa} %\n"
        f"Cash to Asset: {firm_cash2at} %\n"
        f"Market Value: {v} MM\n"
        f"Book Value: {k_phys} MM\n"
        f"Physical Capital Investment: {i_phys} MM\n"
        f"Intangible Capital Investment: {i_int} MM\n"
        f"Research and Development Investment: {xrd} MM\n"
        f"Total Investment: {i_tot} MM\n"
        f"Total Capital Stock: {k_tot} MM\n"
        # f"Tobin's Q Ratio: {q_tot} %"
    )

def build_q1(
    company_name: str,
    gvkey: int,
    fyear: int,
    financial_data: str,
    item1_and_item7_text: str,
    conference_call_text: str,
    patents_text: str,
    wsj_text: str,
    academic_research_text: str,
    question: str
) -> str:
    """
    Populate the Q1 prompt template using retrieved text from multiple namespaces,
    including financial data.
    """
    return Q1_TEMPLATE.format(
        company_name=company_name,
        gvkey=gvkey,
        fyear=fyear,
        financial_data=financial_data,
        item1_and_item7_text=item1_and_item7_text,
        conference_call_text=conference_call_text,
        patents_text=patents_text,
        wsj_text=wsj_text,
        academic_research_text=academic_research_text,
        question=question
    )