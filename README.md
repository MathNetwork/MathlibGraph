<div align="center">

# The Network Structure of Mathlib:<br>Software Engineering vs. Mathematical Dependencies

**Xinze Li** &nbsp;&middot;&nbsp; **Nanyun Peng** &nbsp;&middot;&nbsp; **Simone Severini**

University of Toronto &nbsp;&middot;&nbsp; UCLA / Google Cloud &nbsp;&middot;&nbsp; UCL / Google Cloud

</div>

We extract and analyze the dependency structure of Lean 4's [Mathlib](https://github.com/leanprover-community/mathlib4) (308,129 declarations, 8,436,366 edges) as a multi-layer network at the declaration, module, and namespace levels.

## Dataset

**HuggingFace**: [MathNetwork/MathlibGraph](https://huggingface.co/datasets/MathNetwork/MathlibGraph)

Extracted from Mathlib commit [`534cf0b`](https://github.com/leanprover-community/mathlib4/commit/534cf0b) (2 Feb 2026). Contains:
- `mathlib_nodes.csv` — 308,129 declarations with metadata (kind, module, namespace, docstring, etc.)
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
