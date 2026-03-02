# MathlibGraph

> Network-theoretic analysis of the dependency structure of formalized mathematics.

This repository contains the research paper and analysis code for studying Mathlib (the mathematical library for Lean 4) as a multi-layer dependency network — comprising the module import graph, the declaration dependency graph, and namespace-level aggregations.

## Repository Structure

```
MathlibGraph/
├── paper/                         # LaTeX paper
│   ├── main.tex                   # Entry point
│   ├── sections/                  # Paper sections
│   └── figures/                   # Generated figures (PDF)
├── src/                           # Analysis code
│   ├── analysis/                  # Analysis modules
│   │   ├── import_graph.py        # Module import graph analysis
│   │   └── import_graph_utils.py  # Utility functions
│   ├── parser/                    # Data extraction
│   │   ├── from_lean4export.py    # NDJSON → nodes.csv
│   │   ├── from_premises.py       # premises → edges.csv
│   │   └── merge.py               # Validation & statistics
│   ├── tests/                     # Tests
│   └── output/                    # Analysis output (JSON)
└── docs/                          # Documentation site (Nextra)
```

## Dataset

**HuggingFace**: [MathNetwork/MathlibGraph](https://huggingface.co/datasets/MathNetwork/MathlibGraph)

Extracted from Mathlib commit [`534cf0b`](https://github.com/leanprover-community/mathlib4/commit/534cf0b) (2 Feb 2026).

## License

Apache License 2.0
