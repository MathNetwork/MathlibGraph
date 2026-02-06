#!/usr/bin/env python3
"""Analyze the Mathlib import graph from source .lean files."""

import json
import os
import re
from collections import Counter, defaultdict
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import networkx as nx
import numpy as np

MATHLIB_ROOT = Path("/Users/moqian/MathFactor/mathlib4/Mathlib")
OUTPUT_DIR = Path("/Users/moqian/MathFactor/papers/mathlib-graph-structure")

# ---------------------------------------------------------------------------
# 1. Build the import graph from .lean files
# ---------------------------------------------------------------------------

def lean_path_to_module(path: Path) -> str:
    """Convert a .lean file path to a module name."""
    rel = path.relative_to(MATHLIB_ROOT.parent)
    return str(rel).replace("/", ".").removesuffix(".lean")


def parse_imports(path: Path) -> list[str]:
    """Extract imported module names from a .lean file.

    In Lean 4, all import statements must appear at the top of the file,
    after the optional `module` keyword and before any declarations.
    We stop parsing once we hit a non-import, non-comment, non-blank line.
    We also skip block comments (/-  ... -/).
    """
    imports = []
    in_block_comment = 0
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            stripped = line.strip()

            # Track nested block comments (/- ... -/)
            was_in_comment = in_block_comment > 0
            entered_comment = False
            i = 0
            while i < len(stripped):
                if i + 1 < len(stripped) and stripped[i:i+2] == "/-":
                    in_block_comment += 1
                    entered_comment = True
                    i += 2
                elif i + 1 < len(stripped) and stripped[i:i+2] == "-/":
                    in_block_comment = max(0, in_block_comment - 1)
                    i += 2
                else:
                    i += 1

            # Skip lines that are (partially) inside block comments
            if in_block_comment > 0 or was_in_comment or entered_comment:
                continue

            # Skip blank lines and single-line comments
            if not stripped or stripped.startswith("--"):
                continue

            # The `module` keyword
            if stripped.startswith("module"):
                continue

            # Match import lines (with optional `public` and/or `meta`)
            m = re.match(
                r"^(?:public\s+)?(?:meta\s+)?import\s+([\w.]+)", stripped
            )
            if m:
                imports.append(m.group(1))
                continue

            # Any other non-import line means the header is over
            break
    return imports


print("Building import graph from .lean files...")
G = nx.DiGraph()

for lean_file in sorted(MATHLIB_ROOT.rglob("*.lean")):
    mod = lean_path_to_module(lean_file)
    G.add_node(mod)
    for imp in parse_imports(lean_file):
        # Only keep Mathlib-internal edges
        if imp.startswith("Mathlib."):
            G.add_edge(mod, imp)

print(f"  Nodes: {G.number_of_nodes()}, Edges: {G.number_of_edges()}")

# ---------------------------------------------------------------------------
# 2. Basic statistics
# ---------------------------------------------------------------------------

in_degrees = dict(G.in_degree())
out_degrees = dict(G.out_degree())

in_vals = list(in_degrees.values())
out_vals = list(out_degrees.values())

top_in = sorted(in_degrees.items(), key=lambda x: -x[1])[:10]
top_out = sorted(out_degrees.items(), key=lambda x: -x[1])[:10]

basic_stats = {
    "nodes": G.number_of_nodes(),
    "edges": G.number_of_edges(),
    "in_degree": {
        "mean": round(np.mean(in_vals), 2),
        "median": round(float(np.median(in_vals)), 2),
        "max": max(in_vals),
        "top_10": [{"module": m, "in_degree": d} for m, d in top_in],
    },
    "out_degree": {
        "mean": round(np.mean(out_vals), 2),
        "median": round(float(np.median(out_vals)), 2),
        "max": max(out_vals),
        "top_10": [{"module": m, "out_degree": d} for m, d in top_out],
    },
}

# Degree histograms
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4.5))

ax1.hist(in_vals, bins=range(0, max(in_vals) + 2), color="steelblue", edgecolor="white", linewidth=0.3)
ax1.set_xlabel("In-degree")
ax1.set_ylabel("Number of modules")
ax1.set_title("In-degree distribution")
ax1.set_yscale("log")

ax2.hist(out_vals, bins=range(0, max(out_vals) + 2), color="coral", edgecolor="white", linewidth=0.3)
ax2.set_xlabel("Out-degree")
ax2.set_ylabel("Number of modules")
ax2.set_title("Out-degree distribution")
ax2.set_yscale("log")

plt.tight_layout()
plt.savefig(OUTPUT_DIR / "degree_distributions.pdf", bbox_inches="tight")
plt.close()
print("  Saved degree_distributions.pdf")

# ---------------------------------------------------------------------------
# 3. DAG structure
# ---------------------------------------------------------------------------

is_dag = nx.is_directed_acyclic_graph(G)
print(f"  Is DAG: {is_dag}")

longest_path = nx.dag_longest_path(G)
longest_path_length = len(longest_path) - 1

# Topological generations (layers)
layers = list(nx.topological_generations(G))
layer_sizes = [len(layer) for layer in layers]

dag_stats = {
    "is_dag": is_dag,
    "longest_path_length": longest_path_length,
    "longest_path": longest_path,
    "num_layers": len(layers),
    "layer_width_max": max(layer_sizes),
    "layer_width_mean": round(np.mean(layer_sizes), 2),
    "layer_width_median": round(float(np.median(layer_sizes)), 2),
}

# Layer width distribution
fig, ax = plt.subplots(figsize=(10, 4))
ax.bar(range(len(layer_sizes)), layer_sizes, color="seagreen", edgecolor="none")
ax.set_xlabel("Topological layer")
ax.set_ylabel("Number of modules")
ax.set_title("DAG width by topological layer")
plt.tight_layout()
plt.savefig(OUTPUT_DIR / "dag_layer_widths.pdf", bbox_inches="tight")
plt.close()
print("  Saved dag_layer_widths.pdf")

# ---------------------------------------------------------------------------
# 4. Namespace tree vs Import graph
# ---------------------------------------------------------------------------

def top_level_ns(module: str) -> str:
    """Extract top-level namespace: Mathlib.Algebra.* -> Algebra."""
    parts = module.split(".")
    return parts[1] if len(parts) > 1 else parts[0]

intra_count = 0
cross_count = 0
ns_matrix = defaultdict(lambda: defaultdict(int))

for u, v in G.edges():
    ns_u = top_level_ns(u)
    ns_v = top_level_ns(v)
    ns_matrix[ns_u][ns_v] += 1
    if ns_u == ns_v:
        intra_count += 1
    else:
        cross_count += 1

namespace_stats = {
    "intra_namespace_edges": intra_count,
    "cross_namespace_edges": cross_count,
    "intra_ratio": round(intra_count / G.number_of_edges(), 4),
}

# Build heatmap of top-level namespace interactions
all_ns = sorted(set(top_level_ns(n) for n in G.nodes()))
ns_to_idx = {ns: i for i, ns in enumerate(all_ns)}
matrix = np.zeros((len(all_ns), len(all_ns)), dtype=int)
for ns_u, targets in ns_matrix.items():
    for ns_v, count in targets.items():
        matrix[ns_to_idx[ns_u], ns_to_idx[ns_v]] = count

fig, ax = plt.subplots(figsize=(14, 12))
im = ax.imshow(np.log1p(matrix), cmap="YlOrRd", aspect="auto")
ax.set_xticks(range(len(all_ns)))
ax.set_yticks(range(len(all_ns)))
ax.set_xticklabels(all_ns, rotation=90, fontsize=6)
ax.set_yticklabels(all_ns, fontsize=6)
ax.set_xlabel("Imported namespace (target)")
ax.set_ylabel("Importing namespace (source)")
ax.set_title("Cross-namespace import counts (log scale)")
plt.colorbar(im, ax=ax, label="log(1 + edge count)")
plt.tight_layout()
plt.savefig(OUTPUT_DIR / "namespace_heatmap.pdf", bbox_inches="tight")
plt.close()
print("  Saved namespace_heatmap.pdf")

# ---------------------------------------------------------------------------
# 5. Centrality
# ---------------------------------------------------------------------------

print("  Computing PageRank...")
pagerank = nx.pagerank(G)
top_pr = sorted(pagerank.items(), key=lambda x: -x[1])[:20]

print("  Computing betweenness centrality (this may take a while)...")
betweenness = nx.betweenness_centrality(G)
top_bc = sorted(betweenness.items(), key=lambda x: -x[1])[:20]

top_in_20 = sorted(in_degrees.items(), key=lambda x: -x[1])[:20]

# Overlap analysis
set_in = {m for m, _ in top_in_20}
set_pr = {m for m, _ in top_pr}
set_bc = {m for m, _ in top_bc}

centrality_stats = {
    "top_20_in_degree": [{"module": m, "value": d} for m, d in top_in_20],
    "top_20_pagerank": [{"module": m, "value": round(v, 6)} for m, v in top_pr],
    "top_20_betweenness": [{"module": m, "value": round(v, 6)} for m, v in top_bc],
    "overlap": {
        "in_degree_AND_pagerank": sorted(set_in & set_pr),
        "in_degree_AND_betweenness": sorted(set_in & set_bc),
        "pagerank_AND_betweenness": sorted(set_pr & set_bc),
        "all_three": sorted(set_in & set_pr & set_bc),
    },
}

# ---------------------------------------------------------------------------
# 6. Save results
# ---------------------------------------------------------------------------

results = {
    "basic_stats": basic_stats,
    "dag_stats": dag_stats,
    "namespace_stats": namespace_stats,
    "centrality_stats": centrality_stats,
}

with open(OUTPUT_DIR / "analysis_results.json", "w") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

print(f"\nDone! Results saved to {OUTPUT_DIR / 'analysis_results.json'}")
