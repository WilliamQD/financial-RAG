import pandas as pd
import os
import json
from tqdm import tqdm
from sklearn.model_selection import train_test_split
from data_loader import load_merged, load_sample, load_comp_total
from prompt_builder import build_financial_data, DEV_MSG
from llm_client import client
from models import create_response_format

BASE_DIR    = os.path.dirname(os.path.abspath(__file__))
RFT_DIR     = os.path.join(BASE_DIR, "RFT_files")

# Prompt template
prompt = """
The firm to analyze is {company_name}, identified by the gvkey number {gvkey}. The current year is {fyear}.
You will be provided several sections of information and based on these information, please perform the tasks at the end and provide detailed analyses.

=== FINANCIAL DATA FOR {company_name} IN THE CURRENT YEAR ===
Note: MM = million, K = thousand, % = percentage
{financial_data}
=== END OF FINANCIAL DATA ===

=== QUESTION ===
Based on the information, predict the company's next three potential projects for consideration.

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
=== END OF QUESTION ===
"""


grader_config = {
    "type": "python",
    "image_tag": "2025-05-08",
    "source": """
from typing import Any, Dict, List

# Helper to compute q for up to three projects
def extract_q_values_json(projects_json: List[Dict[str, Any]]):
    results = []
    # Ensure we always return exactly three slots
    for i in range(3):
        try:
            p    = projects_json[i]
            mk   = p.get("market_value")
            cost = p.get("implementation_cost")
            q    = mk / cost if (isinstance(mk, (int, float)) and cost) else None
        except Exception:
            q = mk = cost = None
        results.append((q, mk, cost))
    return results

def grade(sample: Dict[str, Any], item: Dict[str, Any]) -> float:
    # 1) Safely pull out the JSON the model will produce
    out_json     = sample.get("output_json") or {}
    projects_json = out_json.get("projects", [])

    # 2) Compute individual q’s, then average
    tuples = extract_q_values_json(projects_json)
    qs     = [q for (q, _, _) in tuples if isinstance(q, (int, float))]
    if not qs:
        return 0.0

    q_pred = sum(qs) / len(qs)
    q_true = float(item.get("q_tot", 0.0))

    # 3) Linear 0–1 scoring with threshold R
    R = 2.0
    score = 1.0 - abs(q_pred - q_true) / R
    return max(0.0, score)
"""
}




def main(verbose=False):
    # Load data
    print("Loading data...")
    merged = load_merged()
    sample = load_sample()
    comp_total = load_comp_total()

    sample_size = 10  # which sample to run

    # include all sample tiers ≤ the chosen size
    available_sizes   = [10, 50, 100]
    selected_sizes    = [s for s in available_sizes if s <= sample_size]
    sub_sample        = sample[sample['sample'].isin(selected_sizes)]

    gvkeys = sub_sample['gvkey'].astype(str).str.lstrip('0').astype(int)   
    df_filtered = merged[
        merged['gvkey'].isin(gvkeys) 
        & merged['fyear'].between(1993, 2022)
    ]

    to_run = df_filtered

    records = []
    for _, row in tqdm(to_run.iterrows(), total=len(to_run)):
        gvkey = row['gvkey']
        fyear = row['fyear']
        cusip = row['cusip']
        comn = row['conm']
        comp_row = comp_total[(comp_total['gvkey'] == int(gvkey)) & (comp_total['fyear'] == int(fyear))]

        comp_row = comp_row.iloc[0]
        financial_data = build_financial_data(
            comp_row["firm_asset"],comp_row["firm_sale"],comp_row["firm_emp"],
            comp_row["firm_bkleverage"],comp_row["firm_profitability"],comp_row["firm_roa"],comp_row["firm_cash2at"],
            comp_row["v"],comp_row["k_phys"],comp_row["i_phys"],comp_row["i_int"],comp_row["xrd"],comp_row["i_tot"],comp_row["k_tot"],
            comp_row["q_tot"]
        )
        
        curr_prompt = prompt.format(
            company_name=comn,
            gvkey=gvkey,
            fyear=fyear,
            financial_data=financial_data
        )

        records.append({
        "messages": [
            {"role":"developer", "content":DEV_MSG["content"]},
            {"role":"user", "content":curr_prompt}
        ],
        "q_tot": comp_row["q_tot"]
    })
        
    # train / validation / test split
    train_records, test_records = train_test_split(records, test_size=0.3, random_state=42)
    val_records, test_records = train_test_split(test_records, test_size=0.5, random_state=42)

    # Sample 20 records from training list
    train_records_20 = train_records[:20] if len(train_records) > 20 else train_records

    # Save the records to JSON files
    os.makedirs(RFT_DIR, exist_ok=True)
    for split_name, recs in [
        ("train", train_records),
        ("valid", val_records),
        ("test",  test_records),
        ("train_20", train_records_20)
    ]:
        path = os.path.join(RFT_DIR, f"{split_name}.jsonl")
        with open(path, "w", encoding="utf-8") as f:
            for rec in recs:
                f.write(json.dumps(rec, ensure_ascii=False) + "\n")
        print(f"Wrote {len(recs)} examples to {path}")

def upload_FT_files():
    # upload files to OpenAI finetune
    # Training file
    train_resp = client.files.create(
        file=open(os.path.join(RFT_DIR, "train.jsonl"), "rb"),
        purpose="fine-tune"
    )
    train_file_id = train_resp.id  # e.g. 'file-XYZ'
    # Validation file
    valid_resp = client.files.create(
        file=open(os.path.join(RFT_DIR, "valid.jsonl"), "rb"),
        purpose="fine-tune"
    )
    valid_file_id = valid_resp.id  

    print(f"Uploaded training file: {train_file_id}")
    print(f"Uploaded validation file: {valid_file_id}")
    return train_file_id, valid_file_id


def create_fine_tune():
    response_format = create_response_format()
    # Your grader_config and response_format dicts from earlier
    job = client.fine_tuning.jobs.create(
        training_file='file-LMCGdKgiWK4bPU6ycDXzgJ',
        validation_file='file-EnjtrQ67WY1Wg8DeQ4wP9i',
        model="o4-mini-2025-04-16",
        method={
            "type": "reinforcement",
            "reinforcement": {
                "grader": grader_config,
                "response_format": response_format,
                "hyperparameters": {"reasoning_effort": "low"}
            }
        }
    )
    print("Created RFT job:", job.id) 



if __name__ == '__main__':
    create_fine_tune()