import pandas as pd
import os
from tqdm import tqdm
from datetime import datetime
from data_loader import load_merged, load_sample, load_comp_total
from retriever import generate_predictions
from plotting import prepare_q_series, calculate_summary, plot_qs, generate_info, calculate_correlations

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
            # 'part1_queries', # diagnostic
            # 'q1_prompt', # diagnostic
            # 'q1_answer', 'q2_answer', # diagnostic
            'q1', 'q2', 'q3',
            'mkv1', 'cost1', 'mkv2', 'cost2', 'mkv3', 'cost3',
            'q_tot']  # total q from comp_total
    dtypes = {
        'gvkey': 'int64',
        'fyear': 'int64',
        # 'part1_queries': 'object', # diagnostic
        # 'q1_prompt': 'object', # diagnostic
        # 'q1_answer': 'object', # diagnostic
        # 'q2_answer': 'object', # diagnostic
        'q1': 'float64',
        'q2': 'float64',
        'q3': 'float64',
        'mkv1': 'float64',
        'cost1': 'float64',
        'mkv2': 'float64',
        'cost2': 'float64',
        'mkv3': 'float64',
        'cost3': 'float64',
        'q_tot': 'float64'
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
    run_dir   = os.path.join(RESULTS_DIR, f"{ts}_{sample_size}")
    os.makedirs(run_dir, exist_ok=True)
    
    csv_path  = os.path.join(run_dir, "results.csv")
    plot_path = os.path.join(run_dir, "qs.png")
    summary_path = os.path.join(run_dir, "summary.csv")
    info_path = os.path.join(run_dir, "info.txt")

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
        output['q_tot'] = comp_row['q_tot'].iloc[0] if not comp_row.empty else float('nan')
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
    q_series      = prepare_q_series(results)
    summary_df    = calculate_summary(q_series)
    summary_df.to_csv(summary_path, index=True)
    corr = calculate_correlations(results)
    corr.to_csv(os.path.join(run_dir, "correlations.csv"), index=True)

    plot_qs(q_series, plot_path, bins=30)
    generate_info(results, total_requested=len(to_run), info_path=info_path)
    print(f"Additional info saved in {run_dir}.")


if __name__ == '__main__':
    main()