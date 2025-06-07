import pandas as pd
import os
from tqdm import tqdm
from datetime import datetime
from data_loader import load_merged, load_sample, load_comp_total
from retriever import generate_predictions
from plotting import plot_qs

BASE_DIR    = os.path.dirname(os.path.abspath(__file__))
RESULTS_DIR = os.path.join(BASE_DIR, "results")
os.makedirs(RESULTS_DIR, exist_ok=True)

def main():
    # Load data
    print("Loading data...")
    merged = load_merged()
    sample = load_sample()
    comp_total = load_comp_total()

    # Prepare result DataFrame
    cols = ['gvkey', 'fyear', 
            # 'part1_queries', 
            # 'q1_prompt', 
            # 'q1_answer', 'q2_answer',  # don't need this for now
            'q1', 'q2', 'q3',
            'mkv1', 'cost1', 'mkv2', 'cost2', 'mkv3', 'cost3']
    dtypes = {
        'gvkey': 'int64',
        'fyear': 'int64',
        # 'part1_queries': 'object',
        # 'q1_prompt': 'object',
        # 'q1_answer': 'object',
        # 'q2_answer': 'object',
        'q1': 'float64',
        'q2': 'float64',
        'q3': 'float64',
        'mkv1': 'float64',
        'cost1': 'float64',
        'mkv2': 'float64',
        'cost2': 'float64',
        'mkv3': 'float64',
        'cost3': 'float64'
    }
    results = pd.DataFrame(columns=cols).astype(dtypes)

    # which sample to run
    sample_size = 10

    # include all sample tiers ≤ the chosen size
    available_sizes   = [10, 50, 100]
    selected_sizes    = [s for s in available_sizes if s <= sample_size]
    sub_sample        = sample[sample['sample'].isin(selected_sizes)]

    gvkeys = sub_sample['gvkey'].astype(str).str.lstrip('0').astype(int)   
    df_filtered = merged[
        merged['gvkey'].isin(gvkeys) 
        & merged['fyear'].between(1993, 2022)
    ]

    # set up paths *before* the loop
    ts        = datetime.now().strftime("%Y-%m-%d-%H%M")
    base      = f"{sample_size}_{ts}"
    path      = os.path.join(RESULTS_DIR, base)
    csv_path  = f"{path}.csv"
    plot_path = f"{path}_qs.png"

    # write only header to start
    results.head(0).to_csv(csv_path, index=False)

    to_run = df_filtered

    # Iterate samples and generate predictions
    for _, row in tqdm(to_run.iterrows(), total=len(to_run), desc='Running samples'):
        gvkey = row['gvkey']
        fyear = row['fyear']
        cusip = row['cusip']
        comn = row['conm']
        comp_row = comp_total[(comp_total['gvkey'] == int(gvkey)) & (comp_total['fyear'] == int(fyear))]

        output = generate_predictions(
            gvkey=gvkey,
            fyear=fyear,
            cusip=cusip,
            comn=comn,
            comp_row=comp_row
        )
        # add to in-memory DataFrame
        results.loc[len(results)] = output

        # append just this one row to disk
        pd.DataFrame([output]).to_csv(
            csv_path,
            mode='a',
            header=False,
            index=False
        )
    print(f"Results saved to {csv_path}")

    # Plot and save q ratio densities
    plot_qs(df=results, path=plot_path)
    print(f"Plot saved to {plot_path}")


if __name__ == '__main__':
    main()