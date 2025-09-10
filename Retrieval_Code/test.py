import ollama
from models import create_json_schema, ProjectsPayload
# from prompt_builder import DEV_MSG
# from retriever import QUESTION_1, QUESTION_2

QUESTION_1 = """
1. Read the Business Description Section: Describe the company's core business and strategic direction.
2. Read the Management Discussion and Analysis: Analyze the MD&A section to grasp management's interpretation of past performance, current challenges, and future outlook.
3. Identify Current Investment Focus: Determine the company's current projects and business model as disclosed in the annual report.
4. Analyze the Market and Competitive Environment: Examine the industry dynamics and competitive environment mentioned in the annual report.

Please provide a detailed report summarizing your findings from these steps.
"""

QUESTION_2_mod = """
Based on your previous analysis, predict the company's next best potential project for consideration.

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
def small_test():
    """
    A small test function to interact with the Ollama API.
    """
    # Kick off a streaming call
    stream = ollama.chat(
        model="deepseek-r1",
        messages=[{"role": "user", "content": "Hello"}],
        stream=True
    )
    # Collect the chunks into one string, or print as they arrive:
    full = ""
    for chunk in stream:
        # chunk is a dict like {"message": {"role": "assistant", "content": "<some text>"}, …}
        token = chunk["message"]["content"]
        print(token, end="", flush=True)   # live-print token
        full += token

    print()       # newline
    print("Done!", full)

def mimic_test():
    messages = [
        {"role": "user", "content": "Hello"}
    ]

    # 4) First Chat: simple completion
    messages.append({"role": "user", "content": QUESTION_1})
    resp1 = ollama.chat(
        model="deepseek-r1",
        messages=messages,
        stream=False,
        options={"temperature": 0.5, "num_predict": 40}
    )
    answer_q1 = resp1["message"]["content"]
    print("Q1 Answer:", answer_q1)
    messages.append({"role": "assistant", "content": answer_q1})

    # 5) Second Chat: structured parse
    messages.append({"role": "user", "content": QUESTION_2_mod})
    schema = create_json_schema()
    resp2 = ollama.chat(
        model="deepseek-r1",
        messages=messages,
        format=schema
        # options={"temperature": 0.9, "num_predict": 1500}
    )
    # Validate and extract
    payload = ProjectsPayload.model_validate_json(resp2["message"]["content"])
    answer_q2 = payload.projects
    print("Parsed Projects:", answer_q2)

mimic_test()