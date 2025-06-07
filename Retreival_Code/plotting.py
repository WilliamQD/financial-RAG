import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

def plot_qs(df: pd.DataFrame, path, bins: int = 30):
    """
    Plot separate histograms for combined q’s and each of q1, q2, q3.

    Parameters
    ----------
    df : pd.DataFrame
        Must contain columns 'q1', 'q2', 'q3'.
    path : str
        Path to save the plot image.
    bins : int
        Number of histogram bins.

    Returns
    -------
    matplotlib.figure.Figure, matplotlib.axes.Axes
    """
    # prepare the data series
    q_series = {
        "all qs": pd.concat([
            df["q1"].dropna(),
            df["q2"].dropna(),
            df["q3"].dropna(),
        ], ignore_index=True),
        "q1": df["q1"].dropna(),
        "q2": df["q2"].dropna(),
        "q3": df["q3"].dropna(),
    }

    # calculate summary statistics (mean, median, std, skewness, kurtosis)
    stats = {
    name: {
        "mean":     round(series.mean(), 2),
        "median":   round(series.median(), 2),
        "std":      round(series.std(), 2),
        "skewness": round(series.skew(), 2)
    }
    for name, series in q_series.items()
}

    # convert to DataFrame
    summary_df = pd.DataFrame.from_dict(stats, orient="index",
                                        columns=["mean", "median", "std", "skewness"])
    # save this to CSV 
    summary_path = path.replace(".png", "_summary.csv")
    summary_df.to_csv(summary_path, index=True)
    print(f"Summary statistics saved to {summary_path}")

    # create a 2×2 grid of plots
    fig, axes = plt.subplots(2, 2, figsize=(12, 8))
    axes = axes.flatten()

    for ax, (label, series) in zip(axes, q_series.items()):
        ax.hist(series, bins=bins, edgecolor="black")
        ax.set_title(f"Histogram of {label}")
        ax.set_xlabel("q value")
        ax.set_ylabel("Frequency")

    fig.tight_layout()
    plt.savefig(path, dpi=300)
    plt.show()

# a second plotting that can be used on a csv file directly
def plot_qs_from_csv(csv_path: str, bins: int = 30):
    """
    Load q ratios from a CSV file and plot histograms.

    Parameters
    ----------
    csv_path : str
        Path to the CSV file containing 'q1', 'q2', 'q3' columns.
    bins : int
        Number of histogram bins.
    """
    df = pd.read_csv(csv_path)
    plot_qs(df, path=csv_path.replace(".csv", ".png"), bins=bins)
    print(f"Plot saved to {csv_path.replace('.csv', '.png')}")

if __name__ == '__main__':
    plot_qs_from_csv("/Users/williamzhang/Documents/Research/financial-RAG/Retreival_Code/results/10_2025-06-05-0054.csv", bins=30)
