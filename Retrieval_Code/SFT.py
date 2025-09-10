import pandas as pd
import os
import json
from tqdm import tqdm
from sklearn.model_selection import train_test_split
from data_loader import load_merged, load_sample, load_comp_total
from prompt_builder import build_financial_data, DEV_MSG
from llm_client import client

# Directory setup
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SFT_DIR = os.path.join(BASE_DIR, "SFT_files")
os.makedirs(SFT_DIR, exist_ok=True)
FILE_IDS_PATH = os.path.join(SFT_DIR, "file_ids.json")

# Prompt template (same as before)
prompt_templates = {"default": """
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
""",
"simple": """
The firm to analyze is {company_name}, identified by the gvkey number {gvkey}. The current year is {fyear}.
=== FINANCIAL DATA FOR {company_name} IN THE CURRENT YEAR ===
Note: MM = million, K = thousand, % = percentage
{financial_data}
=== END OF FINANCIAL DATA ===

=== QUESTION ===
Based on the information, predict the tobin's q for the firm in the current year.
=== END OF QUESTION ===
"""}

# Ground-truth response: use q_tot as the correct answer
def get_ground_truth_response(comp_row):
    return str(comp_row["q_tot"])


def build_and_save(template_name: str, sample_size=10) -> dict:
    """
    Build JSONL files for one template and save train/validation/test splits.
    Returns dict mapping split names to file paths.
    """
    merged = load_merged()
    sample = load_sample()
    comp_total = load_comp_total()
    
    # filter sample
    sizes = [s for s in [10,50,100] if s <= sample_size]
    sub = sample[sample['sample'].isin(sizes)]
    gvkeys = sub['gvkey'].astype(str).str.lstrip('0').astype(int)
    df = merged[merged['gvkey'].isin(gvkeys) & merged['fyear'].between(1993,2022)]

    # build records
    records = []
    tpl = prompt_templates[template_name]
    for _, row in tqdm(df.iterrows(), total=len(df), desc=f"Building {template_name}"):
        gvkey, fyear, comn = row['gvkey'], row['fyear'], row['conm']
        comp_row = comp_total[(comp_total['gvkey']==int(gvkey)) & (comp_total['fyear']==int(fyear))].iloc[0]
        fin = build_financial_data(
            comp_row["firm_asset"], comp_row["firm_sale"], comp_row["firm_emp"],
            comp_row["firm_bkleverage"], comp_row["firm_profitability"], comp_row["firm_roa"], comp_row["firm_cash2at"],
            comp_row["v"], comp_row["k_phys"], comp_row["i_phys"], comp_row["i_int"], comp_row["xrd"], comp_row["i_tot"], comp_row["k_tot"]
        )
        prompt = tpl.format(company_name=comn, gvkey=gvkey, fyear=fyear, financial_data=fin)
        gt = get_ground_truth_response(comp_row)
        records.append({
            "messages": [
                {"role":"developer","content":DEV_MSG["content"]},
                {"role":"user","content":prompt},
                {"role":"assistant","content":gt}
            ]
        })

    # split and write
    train, test = train_test_split(records, test_size=0.3, random_state=42)
    val, test   = train_test_split(test, test_size=0.5, random_state=42)
    data_splits = {'train': train, 'validation': val, 'test': test}
    paths = {}
    for split, recs in data_splits.items():
        fname = f"{split}_{template_name}.jsonl"
        path = os.path.join(SFT_DIR, fname)
        with open(path, 'w', encoding='utf-8') as f:
            for rec in recs:
                f.write(json.dumps(rec, ensure_ascii=False) + "\n")
        print(f"Wrote {len(recs)} to {path}")
        paths[f"{split}_{template_name}"] = path
    return paths


def upload_files(template_name: str, paths: dict) -> dict:
    """
    Upload JSONL files for one template. Returns dict of file IDs.
    If already uploaded, reuses cached IDs.
    """
    if os.path.exists(FILE_IDS_PATH):
        cached = json.load(open(FILE_IDS_PATH, 'r', encoding='utf-8'))
        return {k: v for k, v in cached.items() if k.startswith(f"train_{template_name}") or k.startswith(f"validation_{template_name}") or k.startswith(f"test_{template_name}")}

    ids = {}
    for label, path in paths.items():
        fid = client.files.create(file=open(path,'rb'), purpose='fine-tune').id
        ids[label] = fid
        print(f"Uploaded {label}: {fid}")
    # update cache
    if os.path.exists(FILE_IDS_PATH):
        all_cache = json.load(open(FILE_IDS_PATH, 'r', encoding='utf-8'))
    else:
        all_cache = {}
    all_cache.update(ids)
    with open(FILE_IDS_PATH, 'w', encoding='utf-8') as f:
        json.dump(all_cache, f, ensure_ascii=False, indent=2)
    return ids


def create_supervised_fine_tune(template_name: str, file_ids: dict):
    """
    Create a supervised fine-tuning job for one template.
    """
    train_id = file_ids[f"train_{template_name}"]
    val_id   = file_ids[f"validation_{template_name}"]
    job = client.fine_tuning.jobs.create(
        training_file=train_id,
        validation_file=val_id,
        model="gpt-4.1-mini-2025-04-14",
        seed=42
    )
    print(f"Started SFT job for {template_name}: {job.id}")


# Instead of CLI, call main with desired template
def main(template_name: str = "default"):
    paths = build_and_save(template_name, sample_size=10)
    file_ids = upload_files(template_name, paths)
    # create_supervised_fine_tune(template_name, file_ids)


if __name__ == '__main__':
    # Change the argument here to "simple" or "default" as needed
    main("simple")