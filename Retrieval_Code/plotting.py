import matplotlib.pyplot as plt
import pandas as pd

def prepare_q_series(df: pd.DataFrame) -> dict:
    """
    Build a dict of non-null q-value series.
    """
    return {
        "all qs": pd.concat([
            df["q1"].dropna(),
            df["q2"].dropna(),
            df["q3"].dropna(),
        ], ignore_index=True),
        "q1": df["q1"].dropna(),
        "q2": df["q2"].dropna(),
        "q3": df["q3"].dropna(),
    }

def calculate_summary(q_series: dict) -> pd.DataFrame:
    """
    Given the q_series dict, return a DataFrame with count, mean, median, std, skewness.
    """
    stats = {}
    for name, series in q_series.items():
        stats[name] = {
            "count":    int(series.count()),
            "mean":     round(series.mean(), 2),
            "median":   round(series.median(), 2),
            "std":      round(series.std(), 2),
            "skewness": round(series.skew(), 2),
        }
    return pd.DataFrame.from_dict(stats, orient="index",
                                  columns=["count", "mean", "median", "std", "skewness"])

def plot_qs(q_series: dict, path: str, bins: int = 30):
    """
    Plot a 2x2 grid of histograms from the q_series dict and save to `path`.
    """
    fig, axes = plt.subplots(2, 2, figsize=(12, 8))
    axes = axes.flatten()

    for ax, (label, series) in zip(axes, q_series.items()):
        ax.hist(series, bins=bins, edgecolor="black")
        ax.set_title(f"Histogram of {label}")
        ax.set_xlabel("q value")
        ax.set_ylabel("Frequency")

    fig.tight_layout()
    plt.savefig(path, dpi=300)
    # plt.show()
    # print(f"Plot saved to {path}")

def generate_info(df: pd.DataFrame, total_requested: int, info_path: str):
    """
    Compute how many non-null rows (across q1/q2/q3) you actually got,
    and write samples_requested & non_null_rows to `info_path`.
    """
    non_null_rows = df.dropna(subset=["q1", "q2", "q3"], how="all").shape[0]
    with open(info_path, "w") as f:
        f.write(f"samples_requested: {total_requested}\n")
        f.write(f"non_null_rows:     {non_null_rows}\n")
    # print(f"Run info saved to {info_path}")

def calculate_correlations(
    df: pd.DataFrame,
    actual_col: str = "q_tot",
    pred_cols: list = ["q1", "q2", "q3"]
) -> pd.Series:
    """
    Returns a Series of Pearson correlations between actual_col and each pred_col,
    plus the mean and median of the preds.
    Index will be: q1, q2, q3, mean_pred, median_pred.
    """
    corrs = {}
    # individual draws
    for p in pred_cols:
        corrs[p] = df[p].corr(df[actual_col])
    # ensemble stats
    mean_pred   = df[pred_cols].mean(axis=1)
    median_pred = df[pred_cols].median(axis=1)
    corrs["mean_pred"]   = mean_pred.corr(df[actual_col])
    corrs["median_pred"] = median_pred.corr(df[actual_col])

    return pd.Series(corrs, name="corr_with_q_tot")





# convenience wrapper if you want to go from CSV → summary + plot:
def plot_qs_from_csv(csv_path: str, bins: int = 30):
    df = pd.read_csv(csv_path)
    q_series   = prepare_q_series(df)
    summary_df = calculate_summary(q_series)
    summary_path = csv_path.replace(".csv", "_summary.csv")
    summary_df.to_csv(summary_path)
    print(f"Summary statistics saved to {summary_path}")

    plot_path = csv_path.replace(".csv", ".png")
    plot_qs(q_series, plot_path, bins=bins)


if __name__ == '__main__':
    plot_qs_from_csv("/Users/williamzhang/Documents/Research/financial-RAG/Retreival_Code/results/10_2025-06-05-0054.csv", bins=30)
