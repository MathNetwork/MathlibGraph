"""Unified plotting style for all paper figures.

Usage in any script:
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
    from plot_style import setup_style, COLORS, FIGSIZE_SINGLE, FIGSIZE_DOUBLE, FIGSIZE_TRIPLE
"""

import matplotlib
import matplotlib.pyplot as plt


# ── Unified color palette ────────────────────────────────────────────
COLORS = {
    "primary": "#2E86AB",       # steel blue  (in-degree, random removal, main data)
    "secondary": "#E94F37",     # coral red   (out-degree, targeted removal, contrast)
    "tertiary": "#2E8B57",      # sea green   (namespace-level, containment)
    "quaternary": "#F5A623",    # gold        (power-law fits, reference lines)
    "grey": "#888888",          # grey        (baselines, annotations)
}

# ── Standard figure sizes (width, height) in inches ──────────────────
FIGSIZE_SINGLE = (6, 4)        # single-column / standalone
FIGSIZE_DOUBLE = (12, 5)       # double-column / two subplots side by side
FIGSIZE_TRIPLE = (15, 4.5)     # three subplots side by side
FIGSIZE_HEATMAP = (12, 5.5)    # heatmap (needs room for labels)
FIGSIZE_HEATMAP_WIDE = (24, 11)  # side-by-side heatmaps


def setup_style():
    """Apply unified rcParams for all paper figures."""
    matplotlib.use("Agg")

    # ── Font: match LaTeX Computer Modern ──
    plt.rcParams["font.family"] = "serif"
    plt.rcParams["font.serif"] = ["STIX Two Text", "STIXGeneral", "Times New Roman", "DejaVu Serif"]
    plt.rcParams["mathtext.fontset"] = "stix"
    plt.rcParams["text.usetex"] = False

    # ── Font sizes (consistent across all figures) ──
    plt.rcParams["font.size"] = 10
    plt.rcParams["axes.titlesize"] = 11
    plt.rcParams["axes.labelsize"] = 10
    plt.rcParams["xtick.labelsize"] = 9
    plt.rcParams["ytick.labelsize"] = 9
    plt.rcParams["legend.fontsize"] = 9

    # ── Figure output defaults ──
    plt.rcParams["figure.dpi"] = 150
    plt.rcParams["savefig.dpi"] = 300
    plt.rcParams["savefig.format"] = "pdf"
    plt.rcParams["savefig.bbox"] = "tight"
    plt.rcParams["figure.facecolor"] = "white"
    plt.rcParams["axes.facecolor"] = "white"
    plt.rcParams["savefig.facecolor"] = "white"

    # ── Clean style ──
    plt.rcParams["axes.spines.top"] = False
    plt.rcParams["axes.spines.right"] = False
    plt.rcParams["axes.grid"] = False
    plt.rcParams["legend.frameon"] = True
    plt.rcParams["legend.edgecolor"] = "0.8"

    return COLORS
