# The Network Structure of Mathlib: Software Engineering vs. Mathematical Dependencies

Code and data for the paper by Xinze Li, Nanyun Peng, and Simone Severini.

We extract and analyze the dependency structure of Lean 4's [Mathlib](https://github.com/leanprover-community/mathlib4) (308,129 declarations, 8.4M edges) as a multi-layer network at the declaration, module, and namespace levels.

## Dataset

**HuggingFace**: [MathNetwork/MathlibGraph](https://huggingface.co/datasets/MathNetwork/MathlibGraph)

Extracted from Mathlib commit [`534cf0b`](https://github.com/leanprover-community/mathlib4/commit/534cf0b) (2 Feb 2026). Contains:
- `mathlib_nodes.csv` — 317,655 declarations with metadata (kind, module, namespace, docstring, etc.)
- `mathlib_edges.csv` — 8,436,366 dependency edges with `is_explicit` flag (25.8% explicit, 74.2% compiler-inserted)

## Repository Structure

```
├── paper/              # LaTeX source
│   ├── main.tex
│   ├── sections/       # Main + appendix sections
│   └── figures/        # Generated figures (PDF)
├── src/
│   ├── parser/         # Data extraction pipeline (Lean 4 → CSV)
│   ├── analysis/       # Network analysis (degree, centrality, community, cascades)
│   ├── plots/          # Figure generation
│   └── main.py         # Full analysis pipeline
└── data/               # Raw intermediate data (NDJSON)
```

## License

[MIT License](LICENSE)
