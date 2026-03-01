# Comprehensive Analysis: "Growing Mathlib: Maintenance of a Large Scale Mathematical Library" (arXiv 2508.21593)

**Baanen, Ballard, Commelin, Chen, Rothgang, Testa (2025)**

---

## 1. Paper Overview

"Growing Mathlib" is a practitioner-oriented paper by six Mathlib maintainers and contributors describing the strategies the community uses to manage the rapid growth of Mathlib (1.9 million lines of Lean code) while preserving library coherence, reasonable compilation times, and contributor accessibility. The paper's central thesis is that sustained growth of a large formal mathematics library is impossible without pervasive automation across social, organizational, and technical dimensions. The paper covers five interlocking systems: (1) a deprecation system for handling breaking changes caused by constant refactoring; (2) semantic linters that enforce style, naming, import structure, and code quality; (3) compilation speed optimization through conscious typeclass hierarchy redesign, coercion unbundling, and tactic tuning; (4) tracking and addressing technical debt accumulated during the Lean 3-to-4 port; and (5) custom tooling for scaling code review and triage of ~1,500 open pull requests. Unlike our paper, which provides a quantitative structural analysis from the outside, this paper provides the inside view of the engineering decisions and community processes that produce the structure we measure.

---

## 2. Section-by-Section Breakdown

### Section 1: Introduction
- **Key claims:**
  - Mathlib is "perhaps the fastest-growing library of formalised mathematics," now at 1.9 million lines of code.
  - The library's focus on being an "integrated library for mathematics" makes it well-suited for formalizing current research (condensed mathematics, sphere eversion, Ramsey bounds, PFR conjecture, FLT project).
  - Scaling challenges are both technical (compilation speed, code adaptation, technical debt) and social (welcoming communication, mandatory code review, knowledge transfer).
- **Tools/metrics:** 1.9 MLOC figure; mentions Lean theorem prover, Zulip chat, GitHub.

### Section 2: Related Work
- **Key claims:**
  - Compares Mathlib to MML (3.7 MLOC), AFP (4.8 MLOC), and Mathematical Components (150K LOC).
  - MML pioneered mandatory review (2006) and duplicate detection; Isabelle uses custom linters; Rocq switched to GitHub/PR model.
  - There is "still relatively little work describing tools and best practices" for formal library maintenance (citing Ringer et al.).
- **Tools/metrics:** Sizes of competing libraries; references to proof repair tools for Isabelle (Tan et al.) and Rocq (Gopinathan et al.).

### Section 3: The Deprecation System
- **Key claims:**
  - Mathlib undergoes "exceedingly common" generalizations, refactors, and reorganizations; code written for one version may stop compiling.
  - The vast majority of breaking changes are simple renamings of declarations or files.
  - File import processing occurs *before* the deprecation system runs, so renamed modules must be preserved as stubs to avoid build failures.
- **Tools/metrics:** Lean's deprecation markers; deprecated module stubs; grace periods of "several months."

### Section 4: Semantic Linters — **HIGH RELEVANCE**
- **Key claims:**
  - Mathlib uses two linter frameworks: Lean-native syntax linters (26 in Mathlib + 10 from dependencies) and Batteries environment linters (17, all but 2 from Batteries).
  - Import structure linters are critical: "Keeping track of Mathlib's import structure is important for organisation and compilation speed."
  - A Lean module can only be compiled once all its dependencies have been fully checked; the upcoming module system may change this.
- **Tools/metrics:**
  - **shake** (Mario Carneiro): warns about unused imports.
  - **directoryDependency linter**: warns about unintentional dependencies between different areas of Mathlib.
  - **header linter**: ensures files don't import umbrella modules like `Mathlib.lean` or `Mathlib/Tactic.lean`.
  - Footnote: "Lean's upcoming module system will change this trade-off, if and when it is adopted in mathlib."

### Section 5: Speeding Up Mathlib — **HIGH RELEVANCE**
- **Key claims:**
  - Build time increases proportionally with library size; constant attention to slowdown sources is required.
  - Typeclass hierarchy design has dramatic performance consequences: unbundling ordered algebra classes gave a 20% decrease in typeclass inference time and 6% overall speedup; unbundling `FunLike` gave a 33% synthesis speedup and 19% decrease in build instructions.
  - The `simp` tactic accounts for approximately 14% of Mathlib compilation time.
- **Tools/metrics:**
  - **Speedcenter** (VelCom instance): benchmarks all master commits.
  - **fast_instance macro**: normalizes instance declarations; achieved 5% type-checking decrease.
  - Bot reports outliers (>=5% changes) on Zulip.

### Section 6: Tracking and Addressing Technical Debt
- **Key claims:**
  - The Lean 3 to Lean 4 port (2021-2023) generated >5,000 porting notes; roughly 1,500 remain.
  - Monthly Lean 4 releases create ongoing adaptation needs.
  - Specific example of organizational debt: "reorganizing top-level directories: due to Mathlib's age, some of these are not coherent any more."
- **Tools/metrics:**
  - `scripts/technical-debt-metrics.sh`: weekly reports posted to Zulip
  - Dedicated Zulip thread for "less measurable forms of technical and organisational debt"

### Section 7: Scaling Code Review
- **Key claims:**
  - Mandatory code review since inception; ~30 maintainers; ~1,500 open PRs.
  - The PR summary comment "exposes when transitive imports of files change, which is extremely helpful for reviewing import refactoring."
- **Tools/metrics:**
  - **bors bot**: enforces main branch always passes CI.
  - **Triage dashboard**: ~4,500 lines Python + ~1,000 lines shell.
  - **Automatic PR labeling** by mathematical area.

### Section 8: Conclusion
- **Key claims:**
  - Automation is essential across social, organizational, and technical levels.
  - An auto-formatter for Lean would help but is difficult due to Lean's extensibility.

---

## 3. Direct Relevance to Our Paper

### Section 1 (Introduction)
- **Overlap:** Both papers study Mathlib's large-scale structure. Our paper quantifies it; theirs describes the engineering processes behind it.
- **Strengthens our claims:** Their framing of Mathlib as an "integrated library" that must remain "coherent as a whole" directly supports our thesis that organizational structure encodes human cognitive models.
- **No contradictions.**

### Section 3 (Deprecation System)
- **Strengthens our claims:** The fact that Lean processes imports *before* the deprecation system confirms that import structure is a first-class architectural constraint, not merely organizational convenience.

### Section 4 (Semantic Linters) — **KEY SECTION**
- **Direct overlap** with our analysis of import structure, transitive redundancy, and `shake`.
  - Their `shake` description: our 17.5% transitive redundancy measures edges that *survive* shake's pruning.
  - Their `directoryDependency` linter relates to our NMI 0.71 finding (directory boundaries partially but imperfectly contain dependency).
  - Their module system footnote corroborates our Nov 2025 module system discussion.
- **Potential complication:** They frame import management primarily as a compilation speed concern; our paper frames it as revealing divergence between organizational and logical structure. Complementary but different framings — be careful not to overstate "cognitive scaffolding" when maintainers emphasize compilation pragmatics.

### Section 5 (Speeding Up Mathlib) — **KEY SECTION**
- **Strengthens our claims:** Enormous community effort on compilation speed (Speedcenter, monitoring bot, 5-20% improvement refactors) validates our focus on compilation bottlenecks.
- **Adds nuance:** Their optimizations are primarily about *per-declaration* compilation cost (typeclass synthesis), not import graph structure. The "narrow waist" story is more nuanced than import depth alone — per-node costs also matter.

### Section 6 (Technical Debt)
- **Strengthens our claims:** "Due to Mathlib's age, some [top-level directories] are not coherent any more" is direct practitioner confirmation of the organizational divergence we quantify (NMI 0.71).

### Section 7 (Scaling Code Review)
- **Strengthens our claims:** Transitive import changes being highlighted in PR reviews confirms import structure is actively monitored. Automatic PR labeling by area validates directory structure as meaningful organizational system.

---

## 4. Tools and Infrastructure Mentioned

| Tool/Process | Description |
|---|---|
| **shake** (Mario Carneiro) | Detects and warns about unused imports; used in CI. |
| **directoryDependency linter** | Warns about unintentional cross-area dependencies. |
| **header linter** | Ensures files don't import umbrella modules. |
| **deprecatedSyntax linter** | Warns about use of deprecated syntax. |
| **docstring linter** | Checks documentation string formatting. |
| **unusedVariable linter** | Warns about unused hypotheses/variables. |
| **unusedSeqFocus linter** | Identifies unnecessary focusing operators. |
| **unusedTactic linter** | Detects tactics with no effect. |
| **unreachableTactic linter** | Identifies unreachable tactic branches. |
| **setOption linter** | Flags file-wide `set_option maxHeartbeats`. |
| **globalAttributeIn linter** | Warns about non-local attribute scope. |
| **flexible linter** | Warns when rigid tactics follow flexible ones. |
| **multiGoal linter** | Warns about unfocused multi-goal tactics. |
| **missingEnd linter** | Detects `section` without matching `end`. |
| **haveLet linter** | Flags `have`/`let` misuse. |
| **papercut linter** (prototype) | Warns about natural number subtraction. |
| **Speedcenter** (VelCom) | Benchmarking server for all master commits. |
| **fast_instance macro** | Normalizes typeclass instance declarations. |
| **mathport** (Mario Carneiro) | Automatic Lean 3 → Lean 4 translator. |
| **scripts/technical-debt-metrics.sh** | Weekly technical debt reports. |
| **bors bot** | Enforces CI-passing main branch. |
| **maintainer merge** | Reviewer → maintainer notification system. |
| **Automatic PR labeling** | Categorizes PRs by mathematical area. |
| **PR summary comment** | Shows renamed lemmas, import changes, debt deltas. |
| **Triage dashboard** | Custom editorial tool (~5,500 lines) for PR management. |

---

## 5. Key Quotes

**Quote 1 (Import structure and compilation):**
> "A Lean module can only be compiled once all its dependencies have been fully checked: thus, a reasonable import structure enables parallelism and faster overall compilation. It also speeds up local development, as changing multiple files requires less recompilation, and makes it easier to place a new mathematical result."

*Section 4. Directly supports our import DAG analysis. "Makes it easier to place a new mathematical result" hints at navigational role beyond compilation.*

**Quote 2 (Upcoming module system):**
> "Lean's upcoming module system will change this trade-off, if and when it is adopted in mathlib. (Doing so is desirable in principle, but requires a lot of conscious library design work.)"

*Section 4 footnote. Corroborates our Nov 2025 module system discussion. "Requires a lot of conscious library design work" supports analyzing the pre-module-system snapshot.*

**Quote 3 (Directory incoherence as technical debt):**
> "One example [of less measurable technical debt] is reorganizing top-level directories: due to Mathlib's age, some of these are not coherent any more."

*Section 6. Direct practitioner confirmation of our NMI 0.71 finding — directory structure diverges from dependency.*

**Quote 4 (Import changes in review):**
> "[The PR summary comment] also exposes when transitive imports of files change, which is extremely helpful for reviewing import refactoring."

*Section 7. Confirms transitive import structure is actively monitored, supporting our 17.5% transitive redundancy analysis.*

**Quote 5 (Community and coherence):**
> "Mathlib is run by a community of users as an open source project, enabling and encouraging contributions by users with a wide range of backgrounds and expertise. [...] this presents challenges around knowledge transfer and ensuring the library stays coherent as a whole."

*Section 1. Supports our thesis that structure encodes human practice — diverse contributors vs. library coherence produces the patterns we measure.*

**Quote 6 (Compilation speed as constant concern):**
> "Keeping build times manageable requires constant attention to sources of slowdowns and inefficiencies."

*Section 5. Validates our focus on compilation bottlenecks as an ongoing, first-order concern.*

**Quote 7 (Typeclass hierarchy and compilation):**
> "As the typeclass hierarchy grows, synthesis of instances becomes slower since a larger search space needs to be explored. [...] if synthesis fails, tactics can decide to fall back on an alternative proof strategy. Lean's instance synthesis algorithm fails only after exploring the full search space."

*Section 5.1. Adds nuance to our narrow-waist analysis — per-declaration costs also contribute, not just graph depth.*

**Quote 8 (shake and directoryDependency):**
> "Mathlib has two main tools to help with keeping the import structure organised: Mario Carneiro's shake tool warns about unused imports, and the directoryDependency linter warns about unintentional dependencies between different areas of Mathlib."

*Section 4. Essential context: shake operates before our analysis; our 17.5% redundancy survives shake pruning.*

**Quote 9 (Deliberate design):**
> "Speeding up compilation times through conscious library (re-)design."

*Abstract. The word "conscious" confirms Mathlib's structure results from deliberate engineering choices, which is our paper's core claim.*

**Quote 10 (Compilation speedup numbers):**
> "This refactor by Yuyang Zhao resulted in a 20% decrease in typeclass inference time, resulting in a 6% overall speedup to Mathlib compilation."

*Section 5.1. Concrete evidence that structural decisions have measurable compilation impact.*

---

## 6. Citation Gaps

### High Priority (should strongly consider citing)

1. **Klein et al. (2012)** — "Challenges and Experiences in Managing Large-Scale Proofs" — Large Isabelle library management including the Levity tool for moving lemmas between theories. Directly relevant to module organization.

2. **Ringer et al. (2019)** — "QED at Large: A Survey of Engineering of Formally Verified Software" — Canonical proof engineering survey; identifies the gap our work bridges.

3. **Huch and Wenzel (2024)** — "Distributed Parallel Build for the Isabelle Archive of Formal Proofs" — Parallel build scheduling for AFP achieving >100x speedup. Isabelle analog of our compilation parallelism analysis.

4. **Blanchette et al. (2015)** — "Mining the Archive of Formal Proofs" — Closest methodological predecessor: mining structural properties of a formal library.

5. **Bancerek et al. (2018)** — "The Role of the Mizar Mathematical Library for Interactive Proof Development in Mizar" — MML evolution and design principles; comparative context.

6. **Baanen (2022)** — "Use and Abuse of Instance Parameters in the Lean Mathematical Library" — Typeclass design tradeoffs that shape the declaration dependency graph.

### Medium Priority

7. **Zimmermann (2019)** — PhD thesis on collaborative evolution of Rocq's ecosystem.
8. **Luan et al. (2025)** — Empirical study of compatibility issues in Isabelle.
9. **Selsam, Ullrich, de Moura (2020)** — Tabled Typeclass Resolution in Lean 4.

---

## Strategic Implications for Our Paper

1. **Cite prominently** — This is the single most important related work. Inside engineering view complements our outside structural analysis.

2. **Reframe 17.5% redundancy** — Our redundancy is what remains *after* shake pruning, making it more significant: these are imports the community has deliberately retained.

3. **Strengthen narrow-waist analysis** — Cite their specific compilation speedup numbers (6%, 19%, 33%) as evidence that structural decisions have measurable impact.

4. **Use the directory incoherence quote** — Direct practitioner validation of our NMI 0.71 finding.

5. **Add nuance to bottleneck analysis** — Per-declaration costs (typeclass synthesis, definitional equality) also contribute, not just import graph depth.

6. **Corroborate module system discussion** — Their footnote acknowledges the upcoming change and adoption challenges.

7. **Add recommended citations** — Especially Klein et al., Ringer et al., Huch & Wenzel, Blanchette et al.
