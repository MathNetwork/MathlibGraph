# LeanScout Data Request: Gaps & Opportunities

## Context

Paper: "Formalization encodes human practice: the network architecture of Mathlib"
Snapshot: commit `534cf0b` (2 Feb 2026)
Current pipeline: `importGraph` (module layer) + `lean4export` + `lean-training-data` (declaration layer)
Collaborator: Adam Topaz — LeanScout (unreleased tool for systematic dataset extraction from Lean libraries)

---

## 1. Current Data Inventory

| Layer | Nodes | Edges | Source Tool |
|-------|-------|-------|-------------|
| Module graph G_module | 7,563 | 23,570 | `importGraph` |
| Declaration graph G_thm | 308,129 | 8,436,366 | `lean-training-data` + `lean4export` |
| Namespace graphs G_ns^(k) | 3,184–15,456 | aggregated from G_thm | derived |
| File-aggregated G_file | 7,563 | 215,211 | derived from G_thm |
| Transitive reduction G_module^- | 7,563 | 19,448 | computed |

Analyses performed: degree distributions, DAG depth profiles, transitive redundancy, containment curves, centrality (in-degree, PageRank, betweenness), Louvain community detection, NMI alignment, robustness, module cohesion, theorem/lemma comparison.

---

## 2. Data Gap Assessment

| Data Type | Status | Impact | LeanScout Feasibility | Priority |
|-----------|--------|--------|-----------------------|----------|
| **Proof vs statement dependency** | Missing | High | High (metaprogramming can inspect type vs proof term) | **1** |
| **Typeclass instance graph** | Partial (hubs identified, not isolated) | High | High (instance resolution is internal to Lean) | **2** |
| **Declaration metadata** (proof size, tactic usage, universe levels) | Missing | Medium-High | High | **3** |
| **Public vs private import distinction** | Missing (snapshot pre-adoption) | High | High (syntax-level extraction) | **4** |
| **Pre-shake import graph** | Missing (only post-shake) | Medium | Medium (need to run without shake, or LeanScout can extract raw imports) | **5** |
| **Temporal/version data** | Missing (single snapshot) | High | Low (requires running across many commits) | 6 |
| **Compilation times per module** | Missing | Medium | Low (not a metaprogramming task) | 7 |
| **Git blame / authorship** | Missing | Medium | Low (git data, not Lean data) | 8 |
| **Shake tool detailed output** | Missing (only aggregate 17.5%) | Medium | Medium (shake is separate tool) | 9 |
| **Tactic-level proof trace** | Missing | Medium | Medium-High (tactic framework is accessible) | 10 |

---

## 3. Detailed Gap Analysis

### Priority 1: Proof vs Statement Dependency

**What we have:** G_thm edges record all premises appearing in the compiled proof term. No distinction between dependencies required by A's *type signature* (statement) and those required by A's *proof body*.

**What we need:** For each edge A → B, a label: `statement` (B appears in the type of A) vs `proof` (B appears only in the proof term of A).

**Why it matters:**
- "Essential" dependencies (statement-level) define the *mathematical structure*; proof dependencies are *proof-technique* choices
- Transitive reduction on statement-only edges would reveal the "skeleton" of mathematical logic, separating it from proof engineering
- Would strengthen the "product vs process" distinction: statement deps = product, proof deps = process
- Could redefine our depth metric: "logical depth" (statement only) vs "proof depth" (full)

**LeanScout feasibility:** High. Lean's kernel distinguishes types from proof terms. Metaprogramming can inspect `ConstantInfo.type` vs `ConstantInfo.value`.

### Priority 2: Typeclass Instance Resolution Graph

**What we have:** Hub nodes identified (OfNat.ofNat: 89,936 in-degree; DFunLike.coe: 65,437). We note a "language infrastructure layer" but can't isolate it.

**What we need:** A separate graph of typeclass instance resolution: for each instance `I : C A`, which class `C` it satisfies and which other instances/classes it depends on. Also: which edges in G_thm are inserted by instance synthesis vs explicitly written.

**Why it matters:**
- Baanen (ITP 2022) shows typeclass design shapes dependency structure significantly
- Could separate "mathematical dependency" from "typeclass plumbing" — two qualitatively different edge types
- Would explain *why* certain hubs have extreme in-degree (instance synthesis inserts them automatically)
- The 29.9% "missing module info" edges in our cross-module analysis may be typeclass-related

**LeanScout feasibility:** High. Lean's typeclass resolution is traceable via metaprogramming. Instance chains are recorded during elaboration.

### Priority 3: Declaration Metadata

**What we have:** Declaration kind (theorem/def/abbrev/constructor/inductive), fully qualified name, premises.

**What we need:**
- **Proof term size** (number of nodes in the expression tree): proxy for proof complexity
- **Tactic usage**: which tactics were used (by name) in the original source, even if compiled away
- **Universe levels**: polymorphism level of each declaration
- **Attribute tags**: `@[simp]`, `@[ext]`, `@[to_additive]`, `@[instance]`, etc.
- **Docstrings**: presence/absence, length

**Why it matters:**
- Proof term size × dependency count could test whether deep declarations have more complex proofs
- `@[to_additive]` tag would precisely quantify the "mirrored results" we discuss qualitatively (§B.2.13)
- `@[simp]` / `@[ext]` tags identify declarations meant for automation, explaining their citation patterns
- Universe levels test whether polymorphic declarations are more heavily cited
- Tactic usage reveals proof methodology patterns invisible in compiled terms

**LeanScout feasibility:** High. All of this is accessible via Lean's `Environment` API.

### Priority 4: Public vs Private Import Graph

**What we have:** All imports treated as public (snapshot predates widespread private import adoption).

**What we need:** For each import edge, whether it is `public import` or `import` (private). Even if most are currently public, the distinction exists in the syntax.

**Why it matters:**
- The paper repeatedly notes our snapshot is "transitional" (Lean 4 module system, Nov 2025)
- Even current partial adoption would show: which modules have started using private imports? What's the pattern?
- Would validate our prediction that private imports reduce transitive visibility
- Enables a "simulated private import" analysis: what would the graph look like if all transitively-redundant imports became private?

**LeanScout feasibility:** High. This is syntax-level information, trivially extractable.

### Priority 5: Pre-Shake Import Graph

**What we have:** Post-shake graph only (17.5% redundancy after shake). We note "raw developer-written redundancy would be higher" but don't quantify it.

**What we need:** The raw import graph before shake removes redundant imports. Or equivalently: the list of imports that shake flags as removable.

**Why it matters:**
- Would let us report both pre-shake and post-shake redundancy: "developers write X% redundant imports; shake removes Y%, leaving Z% intentional redundancy"
- Separates automated vs intentional redundancy — a key distinction for the development ergonomics argument
- Quantifies how much work shake is doing for the library

**LeanScout feasibility:** Medium. LeanScout could extract raw `import` statements from source files before compilation. However, shake itself is a separate linting tool.

---

## 4. Concrete Request for Adam Topaz

### Data extractions (ranked by priority):

1. **Statement vs proof dependency labels**: For each declaration A and each premise B that A depends on, output whether B appears in `A.type` (statement dependency), `A.value` (proof dependency), or both.

2. **Typeclass instance inventory**: For each `instance` declaration, output: (a) which class it provides, (b) which classes/instances it requires, (c) a flag for auto-generated instances. Separately: for each edge in G_thm, whether it was inserted by instance synthesis.

3. **Declaration attribute tags**: For each declaration, output all Lean attributes (`@[simp]`, `@[ext]`, `@[to_additive]`, `@[instance]`, `@[reducible]`, `@[inline]`, etc.). Especially `@[to_additive]` for quantifying mirrored declarations.

4. **Proof term sizes**: For each declaration with a proof term, output the expression tree size (number of `Expr` nodes). No need for full proof terms — just the size count.

5. **Public vs private import flags**: For each `import` statement in each module, whether it is `public import` or plain `import`.

### Technical questions for Adam:

- Can LeanScout distinguish premises that appear in a declaration's *type* from those that appear only in its *proof term*?
- Can LeanScout trace which edges in the dependency graph were inserted by typeclass instance synthesis vs. explicitly written in the source?
- Does LeanScout have access to the pre-elaboration source (for tactic names) or only post-compilation terms?
- Can LeanScout extract universe level constraints per declaration?
- Is it feasible to run LeanScout on historical Mathlib commits (e.g., monthly snapshots over the past year)?

---

## 5. Impact on Paper if Data is Obtained

### Proof vs Statement Dependencies (Priority 1)
- **New analysis**: Split G_thm into G_statement and G_proof. Compare depth, degree distributions, community structure.
- **Strengthens**: "product vs process" framing — statement deps are product, proof deps are process
- **New finding potential**: "X% of edges are proof-only, suggesting the logical skeleton is sparser than the full dependency graph"
- **Effort**: Medium (new analysis section, likely appendix material)

### Typeclass Instance Graph (Priority 2)
- **New analysis**: Separate language-infrastructure edges from mathematical edges. Recompute centrality on math-only graph.
- **Strengthens**: Remark 3.11 (two-layer hub structure) with precise quantification
- **New finding potential**: "Removing typeclass plumbing, the hub structure shifts from language infrastructure to mathematical content"
- **Effort**: Medium (enriches existing analysis, doesn't require restructuring)

### Declaration Attributes (Priority 3)
- **New analysis**: Precise count of `@[to_additive]` mirrors. Simp lemma citation patterns. Instance declaration flow.
- **Strengthens**: Semantic flattening observation with exact numbers instead of qualitative statements
- **Effort**: Low (slot into existing sections)

### Public/Private Import Flags (Priority 4)
- **New analysis**: Current adoption rate. Simulated impact on redundancy and transitivity.
- **Strengthens**: Module system transition discussion with data instead of prediction
- **Effort**: Low (short addition to module graph section)

### Pre-Shake Graph (Priority 5)
- **New analysis**: Pre-shake vs post-shake redundancy comparison.
- **Strengthens**: Development ergonomics argument with precise decomposition
- **Effort**: Low (one additional number + brief discussion)
