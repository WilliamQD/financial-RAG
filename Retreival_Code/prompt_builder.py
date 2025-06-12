# Q1 & Q2 prompt templates and builders

Q1_TEMPLATE = """
You are the CEO of {company_name}, identified by the gvkey number {gvkey}. The current year is {fyear}.
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
    v, k_phys, i_phys, i_int, xrd, i_tot, k_tot
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
        f"Total Capital Stock: {k_tot} MM"
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