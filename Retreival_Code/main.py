import pandas as pd
import os
from tqdm import tqdm
from datetime import datetime
from data_loader import load_merged, load_sample
from retriever import generate_predictions
from plotting import plot_qs

BASE_DIR    = os.path.dirname(os.path.abspath(__file__))
RESULTS_DIR = os.path.join(BASE_DIR, "results")
os.makedirs(RESULTS_DIR, exist_ok=True)

def main():
    # Load data
    merged = load_merged()
    sample = load_sample()

    # Prepare result DataFrame
    cols = ['gvkey', 'fyear', 'part1_queries', 'q1_prompt', 'q1_answer', 'q2_answer', 'q1', 'q2', 'q3']
    dtypes = {
        'gvkey': 'int64',
        'fyear': 'int64',
        'part1_queries': 'object',
        'q1_prompt': 'object',
        'q1_answer': 'object',
        'q2_answer': 'object',
        'q1': 'float64',
        'q2': 'float64',
        'q3': 'float64'
    }
    results = pd.DataFrame(columns=cols).astype(dtypes)

    # which sample to run
    sample_size = 50

    sub_sample = sample[sample['sample'] == sample_size]
    gvkeys = sub_sample['gvkey'].astype(str).str.lstrip('0').astype(int)   
    df_filtered = merged[
    merged['gvkey'].isin(gvkeys) &
    merged['fyear'].between(1993, 2022)] 
    
    to_run = df_filtered

    # Iterate samples and generate predictions
    for _, row in tqdm(to_run.iterrows(), total=len(to_run), desc='Running samples'):
        gvkey = row['gvkey']
        fyear = row['fyear']
        cusip = row['cusip']
        comn = row['conm']

        output = generate_predictions(
            gvkey=gvkey,
            fyear=fyear,
            cusip=cusip,
            comn=comn
        )
        results.loc[len(results)] = output

    # Save results
    ts   = datetime.now().strftime("%Y-%m-%d-%H%M")
    base = f"{sample_size}_{ts}"
    path = os.path.join(RESULTS_DIR, base)
    csv_path = f"{path}.csv"
    plot_path = f"{path}_qs.png"
    results.to_csv(csv_path, index=False)
    print(f"Results saved to {csv_path}")

    # Plot and save q ratio densities
    plot_qs(df=results, path=plot_path)
    print(f"Plot saved to {plot_path}")


if __name__ == '__main__':
    main()