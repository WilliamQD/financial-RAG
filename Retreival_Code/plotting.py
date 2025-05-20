import matplotlib.pyplot as plt
import pandas as pd

def plot_qs(df: pd.DataFrame, path, bins: int = 30):
    """
    Plot separate histograms for combined q’s and each of q1, q2, q3.

    Parameters
    ----------
    df : pd.DataFrame
        Must contain columns 'q1', 'q2', 'q3'.
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
