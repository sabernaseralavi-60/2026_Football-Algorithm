<!--
SYNC IMPACT REPORT
==================
Version change: (unversioned raw template) -> 1.0.0
Bump rationale: first ratification. Every placeholder is replaced with project-specific governance,
so this is the initial MAJOR release rather than an amendment.

Modified principles (template slot -> ratified title):
  - [PRINCIPLE_1_NAME] -> I. Operator-Family Grounding (NON-NEGOTIABLE)
  - [PRINCIPLE_2_NAME] -> II. Ablation-Justified Complexity
  - [PRINCIPLE_3_NAME] -> III. Benchmark Rigor, Honest Losses, No Cherry-Picking
  - [PRINCIPLE_4_NAME] -> IV. Reproducibility and Measured, Not Estimated, Cost
  - [PRINCIPLE_5_NAME] -> V. Data Integrity Before Trust
Added principles:
  - VI. Anonymized Archetypes (a sixth principle; the template's five slots were extended)
Added sections:
  - Research Scope and Constraints      (template [SECTION_2_NAME])
  - Research Workflow and Quality Gates (template [SECTION_3_NAME])
  - Governance (filled from [GOVERNANCE_RULES])
Removed sections: none.

Templates requiring updates:
  - .specify/templates/plan-template.md      OK, no edit needed: its "Constitution Check" gate is
                                             derived at runtime from this file (Gates G1-G8 below).
  - .specify/templates/spec-template.md      OK, no edit needed: the research reinterpretation of
                                             users/requirements/success criteria is done per spec.
  - .specify/templates/tasks-template.md     OK, no edit needed.
  - .specify/templates/checklist-template.md OK, no edit needed.

Deferred items / TODOs: none. No placeholder was intentionally left unresolved.
Note: the Spec Kit skill describes this report as scratch material normally removed before commit;
it is retained here at the project owner's explicit request.
-->

# Total Football Optimizer (TFO) Research Constitution

## Core Principles

### I. Operator-Family Grounding (NON-NEGOTIABLE)

- Every mechanism that appears in the algorithm, whether a player archetype or a team-level tactic,
  MUST be mapped in a single reviewer-facing table to a named operator family from the established
  metaheuristics literature, with at least one canonical citation for that family.
- Every mechanism MUST be defined mathematically in operator terms. The football vocabulary is a
  labelling layer only: the paper MUST contain a metaphor-free description (pseudocode or equations)
  from which the algorithm can be re-implemented without reading any football term.
- A mechanism that cannot be mapped to a recognised operator family MUST NOT be claimed as novel
  on the strength of its metaphor. It is either mapped, reframed as a documented composition of
  mapped families, or removed.
- Where a mechanism shares its operator family with a mechanism of the sibling Chess Algorithm
  (CA), the overlap MUST be stated plainly, and the claimed difference (trigger, scope, or
  interaction structure) MUST be named.

Rationale: the "metaphor exposed" critique of nature- and game-inspired metaheuristics is the first
objection any Q1 reviewer raises. The sibling CA paper survived it only because its table let a
reviewer see every operator for what it is. TFO inherits that discipline without exception.

### II. Ablation-Justified Complexity

- A mechanism stays in the published algorithm only if a controlled ablation shows that it earns
  its keep: a measurable, statistically tested contribution on at least one problem class, or a
  documented, pre-stated role (for example, feasibility handling) that the ablation confirms.
- Every mechanism MUST be individually switchable, and the one-at-a-time ablation MUST cover every
  switchable mechanism. Because one-at-a-time ablation hides mechanisms with overlapping function,
  group-level ablations (the whole adaptive layer; the whole formation topology; the whole
  archetype roster) MUST also be run.
- The ablation twin TFO-static, the identical operator set with the adaptive control layer switched
  off, MUST be carried through every experiment in the paper, never only a subset.
- Mechanisms that measure near-zero contribution MUST be reported as such, then either removed or
  retained with an explicit written justification. They MUST NOT be silently kept to pad novelty.

Rationale: an algorithm with many named mechanisms invites the objection that most are ornamental.
Answering that objection with measurements, including unflattering ones, is what makes the
remaining claims credible.

### III. Benchmark Rigor, Honest Losses, No Cherry-Picking

- Results MUST be reported on complete, validated suites: the full usable CEC-2017 suite, every
  validated CEC-2022 function-dimension cell, and the full set of classic constrained engineering
  design problems chosen for the study. Selecting functions after seeing results is prohibited.
- The comparison roster MUST include classical baselines (GWO, PSO, GA, WOA) and competition-grade
  adaptive optimizers (L-SHADE, CMA-ES), so that TFO is judged against the strongest members of the
  operator families it borrows from, not only against other metaphor-derived methods.
- Losses MUST be reported plainly, in the same tables and with the same prominence as wins, with
  complete per-function win/tie/loss records. Expected losses MUST be stated before the runs
  (pre-registration of hypotheses) and confirmed or refuted afterwards, never argued away.
- Parameters and controller thresholds MUST be calibrated on a tuning set disjoint from the test
  suites and frozen before any test-suite run. Tuning on the reported benchmark is prohibited.
- Statistical claims MUST use non-parametric tests appropriate to paired multi-run data
  (Friedman mean ranks; Wilcoxon signed-rank with a multiple-comparison correction).

Rationale: the sibling paper's standing rests on reporting that it loses to L-SHADE and CMA-ES and
on a structural niche to GA. Honest negative results are the evidence that the positive ones were
not selected.

### IV. Reproducibility and Measured, Not Estimated, Cost

- Every run MUST be driven by a fixed, recorded random seed. Code, seeds, raw per-run results, and
  the scripts that generate every table and figure MUST be committed so that a third party can
  regenerate the paper's numbers.
- Evaluation cost MUST be counted exactly by a wrapper that intercepts every objective call, for
  every algorithm. Every algorithm MUST receive the identical maximum number of function
  evaluations per cell; any internal probes (possession passes, set pieces, bursts) are paid from
  that same budget. Estimated overheads ("roughly ten percent") are prohibited in the manuscript.
- Wall-clock timing, when reported, MUST be measured on an otherwise idle machine with a monotonic
  timer over repeated runs.
- Every number in the manuscript MUST be traceable to a committed source file, and a presentation
  validation step MUST re-check each rendered table cell against its source data before submission.

Rationale: the sibling paper replaced an estimated overhead with a measured one only late in its
life, and still ran on iteration-matched rather than evaluation-matched budgets. TFO starts from
exact, evaluation-matched accounting so that no result can be attributed to a budget advantage.

### V. Data Integrity Before Trust

- Before any benchmark result is analysed, every benchmark function or function-dimension cell
  MUST pass an integrity audit: (a) the implementation evaluated at its claimed global optimum
  returns the claimed optimal value; (b) no run of any algorithm attains a value better than the
  claimed optimum, which would be a definitional impossibility.
- A cell that fails the audit MUST be cross-validated against an independent reference
  implementation built from official data. It is restored only if it passes there; otherwise it is
  excluded, and the exclusion and its evidence are documented.
- Non-discriminative cells MUST be identified by a mechanical rule stated before the results are
  seen, not by judgement after the fact.
- Pre-audit (unaudited) numbers MUST be retained on record, never quietly deleted.

Rationale: the sibling project found six CEC-2017 labels and six CEC-2022 cells that failed exactly
this audit in a widely used benchmark port. Results computed on a defective function are not
evidence of anything.

### VI. Anonymized Archetypes

- Inspiration from recognisable real-world playing styles is welcome and MAY be acknowledged
  candidly, in at most one explanatory sentence per archetype, as an homage to a style of play.
- The formal terminology (archetype names, mechanism names, symbols, equation labels, table rows,
  figure labels, and code identifiers) MUST NOT use the name, nickname, image, or likeness of any
  real person, living or deceased, and MUST NOT use club or competition trademarks.
- Archetypes MUST be defined by tactical function (for example, "deep-lying playmaker"), never by
  reference to an individual's career or identity.

Rationale: a submitted paper must not build its formal vocabulary around real people. Generic
tactical roles carry the same intuition, just as the sibling paper used chess concepts rather than
players' names.

## Research Scope and Constraints

- In scope: the design of TFO's mechanisms and player archetypes; its adaptive control layer and the
  TFO-static ablation twin; and a benchmark programme consisting of the full CEC-2017 suite, the
  validated CEC-2022 cells, and classic constrained engineering design problems, together with
  granular ablation, parameter sensitivity, measured cost, and benchmark integrity audits.
- Out of scope: any real-world application case study. The classic constrained engineering design
  problems are benchmarks, not case studies, and no application section is to be designed or added
  without a MAJOR amendment of this constitution.
- Information parity: every algorithm in a comparison MUST see the same problem formulation and the
  same information about it. Where TFO has a mechanism that needs extra information (for example, a
  raw constraint-violation vector), that mechanism is evaluated in a separate, clearly labelled
  experiment and never mixed into the roster tables.
- Prior-art positioning: the manuscript MUST explicitly position TFO against existing sport- and
  league-inspired metaheuristics and against the sibling CA, stating what is structurally new.
- The sibling repository (2026_Chess-Algorithm) is a read-only reference. Its lessons may be
  adopted; its files MUST NOT be modified from this project.

## Research Workflow and Quality Gates

Work proceeds through the Spec Kit sequence (specify, clarify, plan, tasks, implement). The plan's
Constitution Check MUST verify the following gates, in order:

- G1 Mechanism map complete: every mechanism has a family, a citation, and a metaphor-free
  definition (Principle I) before implementation begins.
- G2 Switchability: every mechanism and the adaptive layer can be disabled independently
  (Principle II) before any benchmark run.
- G3 Tuning frozen: parameters and thresholds are calibrated on the disjoint tuning set and frozen,
  with the frozen configuration committed, before any test-suite run (Principle III).
- G4 Hypotheses pre-registered: expected wins and expected losses are committed before test-suite
  runs (Principle III).
- G5 Integrity audited: every benchmark cell passes or is dispositioned under Principle V before its
  results enter any analysis.
- G6 Budget verified: exact evaluation counts confirm identical budgets for every algorithm in every
  cell (Principle IV).
- G7 Ablation complete: one-at-a-time, group-level, and TFO-static results exist for every mechanism
  before any mechanism-level claim is written (Principle II).
- G8 Presentation validated: every table cell and in-text number is re-checked against committed
  source data, and every loss is present in the main text (Principles III and IV).

A gate that cannot be passed MUST be recorded in the plan's Complexity Tracking table with the
reason and the simpler alternative that was rejected.

## Governance

- This constitution supersedes informal practice for this project. Specs, plans, tasks, and the
  manuscript MUST comply with it, and reviews of any of them MUST check compliance explicitly.
- Amendments are made by editing this file through the Spec Kit constitution workflow, with a Sync
  Impact Report describing the change, and are committed with a message naming the new version.
- Versioning follows semantic versioning. MAJOR: removal or redefinition of a principle or a scope
  change (for example, adding an application case study). MINOR: a new principle, section, or gate,
  or materially expanded guidance. PATCH: clarification or wording that does not change meaning.
- Compliance review: before submission, each principle and gate is checked against the manuscript
  and repository, and the outcome is recorded in the submission checklist.

**Version**: 1.0.0 | **Ratified**: 2026-09-24 | **Last Amended**: 2026-09-24
