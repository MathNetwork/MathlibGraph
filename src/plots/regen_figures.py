#!/usr/bin/env python3
"""
Regenerate 4 figures to match unified plot style.
"""

import time
from pathlib import Path
from collections import Counter

from plot_style import setup_style, COLORS, FIGSIZE_SINGLE, FIGSIZE_DOUBLE, FIGSIZE_TRIPLE

COLORS = setup_style()

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import networkx as nx
from datasets import load_dataset

OUTPUT_DIR = Path(__file__).resolve().parent.parent / "paper" / "analysis"


def load_and_build():
    print("Loading data from HuggingFace...")
    t0 = time.time()
    nodes_ds = load_dataset(
        "MathNetwork/MathlibGraph",
        data_files="mathlib_nodes.csv",
        split="train",
    )
    edges_ds = load_dataset(
        "MathNetwork/MathlibGraph",
        data_files="mathlib_edges.csv",
        split="train",
    )
    nodes_df = nodes_ds.to_pandas()
    edges_df = edges_ds.to_pandas()
    print(f"  Downloaded in {time.time() - t0:.1f}s")

    print("Building graph...")
    t0 = time.time()
    G = nx.DiGraph()
    for _, row in nodes_df.iterrows():
        G.add_node(row["name"], kind=row["kind"], module=row["module"])
    node_set = set(G.nodes)
    for _, row in edges_df.iterrows():
        if row["source"] in node_set and row["target"] in node_set:
            G.add_edge(row["source"], row["target"])
    print(f"  Built in {time.time() - t0:.1f}s  ({G.number_of_nodes():,} nodes, {G.number_of_edges():,} edges)")
    return G


def plot_degree_distribution(G, alpha_in, xmin_in, alpha_out, xmin_out):
    """Degree distribution scatter plot -- matching unified style."""
    in_degrees = [d for _, d in G.in_degree() if d > 0]
    out_degrees = [d for _, d in G.out_degree() if d > 0]

    fig, axes = plt.subplots(1, 2, figsize=FIGSIZE_DOUBLE)
    title_fs, label_fs, tick_fs, legend_fs = 14, 12, 11, 11

    # Both panels use red (secondary) for declaration-level G_thm
    for ax, degrees, title, alpha, xmin, alpha_scatter in [
        (axes[0], in_degrees, "In-degree distribution", alpha_in, xmin_in, 0.7),
        (axes[1], out_degrees, "Out-degree distribution", alpha_out, xmin_out, 0.5),
    ]:
        counts = Counter(degrees)
        degs = sorted(counts.keys())
        freqs = [counts[k] for k in degs]

        ax.scatter(degs, freqs, s=12, color=COLORS["secondary"], alpha=alpha_scatter)
        ax.set_xscale("log")
        ax.set_yscale("log")

        # Fix labels
        if "In" in title:
            ax.set_xlabel("In-degree", fontsize=label_fs)
        else:
            ax.set_xlabel("Out-degree", fontsize=label_fs)
        ax.set_ylabel("Count", fontsize=label_fs)
        ax.set_title(title, fontsize=title_fs)
        ax.tick_params(labelsize=tick_fs)

        # Power law reference line
        k_arr = np.array(degs, dtype=float)
        mask = k_arr >= xmin
        if mask.any():
            k_ref = k_arr[mask]
            freq_at_xmin = counts.get(int(xmin), counts.get(min(k for k in degs if k >= xmin), 1))
            ref_line = freq_at_xmin * (k_ref / xmin) ** (-alpha)
            ax.plot(k_ref, ref_line, color=COLORS["quaternary"], linestyle="--",
                    linewidth=1, alpha=0.6,
                    label=f"$k^{{-{alpha:.2f}}}$")
            ax.legend(fontsize=legend_fs)

        ax.grid(True, alpha=0.3, which="both")

    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "thm_degree_distribution.pdf", bbox_inches="tight")
    plt.close()
    print("  Saved: thm_degree_distribution.pdf")


def plot_robustness(csv_path):
    """Robustness curve -- matching unified style."""
    df = pd.read_csv(csv_path)

    fig, ax = plt.subplots(figsize=FIGSIZE_SINGLE)
    title_fs, label_fs, tick_fs, legend_fs = 14, 12, 11, 11

    ax.plot(df["fraction_removed"] * 100, df["random_wcc_ratio"],
            "o-", color=COLORS["secondary"], markersize=4, linewidth=1.5,
            label="Random removal")
    ax.plot(df["fraction_removed"] * 100, df["targeted_wcc_ratio"],
            "s--", color=COLORS["secondary"], markersize=4, linewidth=1.5, alpha=0.5,
            label="Targeted removal (by PageRank)")

    ax.set_xlabel("Fraction of nodes removed (%)", fontsize=label_fs)
    ax.set_ylabel("Largest WCC / Total nodes", fontsize=label_fs)
    ax.set_title(r"Network robustness: $G_{\mathrm{thm}}$", fontsize=title_fs)
    ax.tick_params(labelsize=tick_fs)
    ax.legend(fontsize=legend_fs)
    ax.grid(True, alpha=0.3)
    ax.set_ylim(0, 1.05)

    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "thm_robustness_curve.pdf", bbox_inches="tight")
    plt.close()
    print("  Saved: thm_robustness_curve.pdf")


def main():
    start = time.time()
    OUTPUT_DIR.mkdir(exist_ok=True)

    # Read fit parameters
    fit_df = pd.read_csv(Path(__file__).parent.parent / "output" / "powerlaw_fit_results.csv")
    in_row = fit_df[fit_df["distribution"] == "in_degree"].iloc[0]
    out_row = fit_df[fit_df["distribution"] == "out_degree"].iloc[0]

    # Load graph and plot degree distribution
    G = load_and_build()
    print("\nGenerating degree distribution plot...")
    plot_degree_distribution(G, in_row["alpha"], in_row["xmin"],
                            out_row["alpha"], out_row["xmin"])

    # Plot robustness from existing CSV
    print("Generating robustness plot...")
    robustness_csv = Path(__file__).parent.parent / "output" / "robustness_data.csv"
    plot_robustness(robustness_csv)

    print(f"\nDone in {time.time() - start:.1f}s")


if __name__ == "__main__":
    main()
