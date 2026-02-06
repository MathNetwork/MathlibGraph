#!/usr/bin/env python3
"""Analyze the difference between our parser (23,570 edges) and importGraph (20,948 edges)."""

import json
import re
from pathlib import Path
from collections import Counter

import networkx as nx

MATHLIB_ROOT = Path("/Users/moqian/MathFactor/mathlib4/Mathlib")


def lean_path_to_module(path: Path) -> str:
    rel = path.relative_to(MATHLIB_ROOT.parent)
    return str(rel).replace("/", ".").removesuffix(".lean")


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


# Build raw graph (Mathlib-internal only)
print("Building raw import graph...")
G = nx.DiGraph()
file_modules = set()

for lean_file in sorted(MATHLIB_ROOT.rglob("*.lean")):
    mod = lean_path_to_module(lean_file)
    file_modules.add(mod)
    G.add_node(mod)

for lean_file in sorted(MATHLIB_ROOT.rglob("*.lean")):
    mod = lean_path_to_module(lean_file)
    for imp in parse_imports(lean_file):
        if imp.startswith("Mathlib.") and imp in file_modules:
            G.add_edge(mod, imp)

print(f"Raw graph: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")

# -------------------------------------------------------------------
# 1. Count non-Mathlib imports (excluded by importGraph)
# -------------------------------------------------------------------
print("\n--- Non-Mathlib imports (excluded by importGraph) ---")
non_mathlib = Counter()
for lean_file in sorted(MATHLIB_ROOT.rglob("*.lean")):
    mod = lean_path_to_module(lean_file)
    for imp in parse_imports(lean_file):
        if not imp.startswith("Mathlib."):
            prefix = imp.split(".")[0]
            non_mathlib[prefix] += 1

for prefix, count in non_mathlib.most_common():
    print(f"  {prefix}: {count} edges")
print(f"  Total non-Mathlib: {sum(non_mathlib.values())}")
print(f"  (These are already excluded from our 23,570)")

# -------------------------------------------------------------------
# 2. Count edges to modules not in file_modules
# -------------------------------------------------------------------
print("\n--- Edges to non-existent Mathlib modules ---")
dangling = 0
for lean_file in sorted(MATHLIB_ROOT.rglob("*.lean")):
    mod = lean_path_to_module(lean_file)
    for imp in parse_imports(lean_file):
        if imp.startswith("Mathlib.") and imp not in file_modules:
            dangling += 1
            if dangling <= 10:
                print(f"  {mod} -> {imp} (not a file)")
print(f"  Total dangling: {dangling}")

# -------------------------------------------------------------------
# 3. Transitive reduction
# -------------------------------------------------------------------
print("\n--- Transitive reduction ---")
G_reduced = nx.transitive_reduction(G)
print(f"After transitive reduction: {G_reduced.number_of_nodes()} nodes, {G_reduced.number_of_edges()} edges")
print(f"Edges removed by TR: {G.number_of_edges() - G_reduced.number_of_edges()}")
print(f"Difference from importGraph (20,948): {G_reduced.number_of_edges() - 20948}")

# -------------------------------------------------------------------
# 4. Check if importGraph also excludes Init
# -------------------------------------------------------------------
print("\n--- Init module analysis ---")
init_in = G.in_degree("Mathlib.Init") if "Mathlib.Init" in G else 0
init_out = G.out_degree("Mathlib.Init") if "Mathlib.Init" in G else 0
print(f"Mathlib.Init in-degree: {init_in}")
print(f"Mathlib.Init out-degree: {init_out}")

# Graph without Init
G_no_init = G.copy()
if "Mathlib.Init" in G_no_init:
    G_no_init.remove_node("Mathlib.Init")
print(f"\nWithout Mathlib.Init: {G_no_init.number_of_nodes()} nodes, {G_no_init.number_of_edges()} edges")

G_no_init_reduced = nx.transitive_reduction(G_no_init)
print(f"Without Init + TR: {G_no_init_reduced.number_of_nodes()} nodes, {G_no_init_reduced.number_of_edges()} edges")
print(f"Difference from importGraph (20,948): {G_no_init_reduced.number_of_edges() - 20948}")

# -------------------------------------------------------------------
# 5. Summary
# -------------------------------------------------------------------
print("\n=== Summary ===")
print(f"Our raw edges:                  {G.number_of_edges()}")
print(f"After transitive reduction:     {G_reduced.number_of_edges()}")
print(f"Without Init + TR:              {G_no_init_reduced.number_of_edges()}")
print(f"importGraph reported:           20,948")
