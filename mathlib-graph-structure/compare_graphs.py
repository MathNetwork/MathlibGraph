#!/usr/bin/env python3
"""Compare our parsed import graph with the importGraph .dot file."""

import re
from pathlib import Path
from collections import Counter

import networkx as nx

MATHLIB_ROOT = Path("/Users/moqian/MathFactor/mathlib4/Mathlib")
DOT_FILE = Path("/Users/moqian/MathFactor/mathlib4/mathlib_import_graph.dot")


# ---------------------------------------------------------------
# 1. Parse the .dot file
# ---------------------------------------------------------------
print("=== Parsing .dot file ===")

G_dot = nx.DiGraph()
non_mathlib_in_dot = set()

with open(DOT_FILE) as f:
    for line in f:
        line = line.strip()
        # Match edge: "A" -> "B"
        m = re.match(r'"([^"]+)"\s*->\s*"([^"]+)"', line)
        if m:
            src, dst = m.group(1), m.group(2)
            # In the dot file, edges are REVERSED: imported -> importing
            # So src is the imported module, dst is the importing module
            # We normalize to our convention: importing -> imported
            G_dot.add_edge(dst, src)
        # Match node declaration: "A" [...]
        elif re.match(r'"([^"]+)"\s*\[', line):
            node = re.match(r'"([^"]+)"', line).group(1)
            G_dot.add_node(node)
            if not node.startswith("Mathlib."):
                non_mathlib_in_dot.add(node)

print(f"Dot file: {G_dot.number_of_nodes()} nodes, {G_dot.number_of_edges()} edges")
if non_mathlib_in_dot:
    print(f"Non-Mathlib nodes in dot: {non_mathlib_in_dot}")
else:
    print("All nodes are Mathlib.* (no non-Mathlib nodes)")


# ---------------------------------------------------------------
# 2. Build our parsed graph
# ---------------------------------------------------------------
print("\n=== Building parsed graph ===")

def parse_imports(path: Path) -> list[str]:
    imports = []
    in_block_comment = 0
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            stripped = line.strip()
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
            if in_block_comment > 0 or was_in_comment or entered_comment:
                continue
            if not stripped or stripped.startswith("--"):
                continue
            if stripped.startswith("module"):
                continue
            m = re.match(
                r"^(?:public\s+)?(?:meta\s+)?import\s+([\w.]+)", stripped
            )
            if m:
                imports.append(m.group(1))
                continue
            break
    return imports


def lean_path_to_module(path: Path) -> str:
    rel = path.relative_to(MATHLIB_ROOT.parent)
    return str(rel).replace("/", ".").removesuffix(".lean")


G_ours = nx.DiGraph()
file_modules = set()

for lean_file in sorted(MATHLIB_ROOT.rglob("*.lean")):
    mod = lean_path_to_module(lean_file)
    file_modules.add(mod)
    G_ours.add_node(mod)

for lean_file in sorted(MATHLIB_ROOT.rglob("*.lean")):
    mod = lean_path_to_module(lean_file)
    for imp in parse_imports(lean_file):
        if imp.startswith("Mathlib.") and imp in file_modules:
            G_ours.add_edge(mod, imp)

print(f"Our graph: {G_ours.number_of_nodes()} nodes, {G_ours.number_of_edges()} edges")


# ---------------------------------------------------------------
# 3. Compare node sets
# ---------------------------------------------------------------
print("\n=== Node comparison ===")
dot_nodes = set(G_dot.nodes())
our_nodes = set(G_ours.nodes())
only_dot = dot_nodes - our_nodes
only_ours = our_nodes - dot_nodes
print(f"Nodes in dot only: {len(only_dot)}")
for n in sorted(only_dot)[:10]:
    print(f"  {n}")
print(f"Nodes in ours only: {len(only_ours)}")
for n in sorted(only_ours)[:10]:
    print(f"  {n}")
print(f"Shared nodes: {len(dot_nodes & our_nodes)}")


# ---------------------------------------------------------------
# 4. Compare edge sets
# ---------------------------------------------------------------
print("\n=== Edge comparison (raw) ===")
dot_edges = set(G_dot.edges())
our_edges = set(G_ours.edges())

only_in_dot = dot_edges - our_edges
only_in_ours = our_edges - dot_edges
shared_edges = dot_edges & our_edges

print(f"Edges in dot only:   {len(only_in_dot)}")
print(f"Edges in ours only:  {len(only_in_ours)}")
print(f"Shared edges:        {len(shared_edges)}")

# Sample edges only in dot
print(f"\nSample edges in dot but not ours (first 15):")
for u, v in sorted(only_in_dot)[:15]:
    in_our_nodes = u in our_nodes and v in our_nodes
    print(f"  {u} -> {v}  (both in our nodes: {in_our_nodes})")

# Sample edges only in ours
print(f"\nSample edges in ours but not dot (first 15):")
for u, v in sorted(only_in_ours)[:15]:
    print(f"  {u} -> {v}")


# ---------------------------------------------------------------
# 5. Transitive reduction of our graph, then compare
# ---------------------------------------------------------------
print("\n=== After transitive reduction of our graph ===")
G_ours_tr = nx.transitive_reduction(G_ours)
# transitive_reduction doesn't preserve node attributes, re-add nodes
G_ours_tr.add_nodes_from(G_ours.nodes())

our_tr_edges = set(G_ours_tr.edges())
print(f"Our TR edges: {len(our_tr_edges)}")

only_in_dot_vs_tr = dot_edges - our_tr_edges
only_in_tr = our_tr_edges - dot_edges
shared_tr = dot_edges & our_tr_edges

print(f"Edges in dot but not our TR: {len(only_in_dot_vs_tr)}")
print(f"Edges in our TR but not dot: {len(only_in_tr)}")
print(f"Shared edges:                {len(shared_tr)}")

# Categorize dot-only edges
print(f"\nAnalyzing {len(only_in_dot_vs_tr)} edges in dot but not our TR:")

# Are they transitive edges in our graph?
tr_removed = our_edges - our_tr_edges  # edges removed by our TR
dot_only_were_transitive = only_in_dot_vs_tr & tr_removed
dot_only_not_in_ours_at_all = only_in_dot_vs_tr - our_edges
dot_only_other = only_in_dot_vs_tr - dot_only_were_transitive - dot_only_not_in_ours_at_all

print(f"  Were in our raw but removed by TR: {len(dot_only_were_transitive)}")
print(f"  Not in our raw graph at all:       {len(dot_only_not_in_ours_at_all)}")
print(f"  Other:                             {len(dot_only_other)}")

if dot_only_not_in_ours_at_all:
    print(f"\n  Edges in dot but NEVER in our graph (first 15):")
    for u, v in sorted(dot_only_not_in_ours_at_all)[:15]:
        u_exists = u in file_modules
        v_exists = v in file_modules
        print(f"    {u} -> {v}  (u exists: {u_exists}, v exists: {v_exists})")


# ---------------------------------------------------------------
# 6. Summary
# ---------------------------------------------------------------
print("\n=== SUMMARY ===")
print(f"Dot file edges:                  {G_dot.number_of_edges()}")
print(f"Our raw edges:                   {G_ours.number_of_edges()}")
print(f"Our TR edges:                    {len(our_tr_edges)}")
print(f"Dot is TR of our raw?            Shared={len(shared_tr)}, "
      f"Dot-only={len(only_in_dot_vs_tr)}, OurTR-only={len(only_in_tr)}")
