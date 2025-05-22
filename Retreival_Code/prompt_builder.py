# Q1 & Q2 prompt templates and builders

Q1_TEMPLATE = """
You are the CEO of {company_name}, identified by the gvkey number {gvkey}. The current year is {fyear}.
You will be provided several sections of information and based on these information, please perform the tasks at the end and provide detailed analyses.

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

Q2_TEMPLATE = """
Based on the chat history and the answer you made before, please perform the tasks at the end and provide detailed analyses.

=== CHAT HISTORY ===
{chat_history_str}
=== END OF CHAT HISTORY ===

=== QUESTION ===
{question}
=== END OF QUESTION ===
"""


def build_q1(
    company_name: str,
    gvkey: int,
    fyear: int,
    item1_and_item7_text: str,
    conference_call_text: str,
    patents_text: str,
    wsj_text: str,
    academic_research_text: str,
    question: str
) -> str:
    """
    Populate the Q1 prompt template using retrieved text from multiple namespaces.
    """
    return Q1_TEMPLATE.format(
        company_name=company_name,
        gvkey=gvkey,
        fyear=fyear,
        item1_and_item7_text=item1_and_item7_text,
        conference_call_text=conference_call_text,
        patents_text=patents_text,
        wsj_text=wsj_text,
        academic_research_text=academic_research_text,
        question=question
    )


def build_q2(chat_history_str, question) -> str:
    return Q2_TEMPLATE.format(chat_history_str=chat_history_str, question=question)