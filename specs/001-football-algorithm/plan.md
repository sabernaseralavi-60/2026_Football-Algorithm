# Implementation Plan: Total Football Optimizer (TFO), Mechanism Design and Evaluation Programme

**Branch**: `001-football-algorithm`. The feature directory is set by `.specify/feature.json`; the
work is committed on `main`. | **Date**: 2026-09-25 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/001-football-algorithm/spec.md`, together with
[mechanism-map.md](./mechanism-map.md) and [related-work.md](./related-work.md).

**Reading this plan as a research artefact.** The spec reinterpreted Spec Kit's software vocabulary
for a research project, and this plan does the same with the plan template:

- The *project* is a research library, with two parts: the `tfo` algorithm package, and the
  `tfo_bench` benchmark harness with its experiment scripts.
- *Interfaces* are the optimiser call contract, the evaluation ledger, the per-mechanism contract
  and the results CSV schema that every analysis script reads.
- *Performance goals* are measured compute and overhead targets. They are not service-level
  latencies.

## Summary

TFO is a population-based metaheuristic organised around three structural axes. The spec and the
mechanism map commit to 19 mechanisms, each mapped to an operator family:

- *interaction structure*: a formation lattice whose shape is a control variable;
- *search focus*: a ball distinct from the incumbent, moved by threshold-accepted passes, with
  event-triggered counter-attacks;
- *temporal control*: an adaptive manager, event-driven mechanisms and fixed-schedule mechanisms.

TFO-static, the same operator set with the manager switched off, runs in every experiment.

**Technical approach** (see [research.md](./research.md)):

- **Algorithm.** A NumPy-only Python package with the squad stored as structure-of-arrays. There is
  **one module per mechanism**, matching the 19 rows of the mechanism map. Each module is
  switchable by configuration flag and falls back to a documented neutral default (gate G2).
- **Budget accounting.** A dual ledger: an internal per-mechanism account inside TFO, and an
  external counting wrapper around every algorithm. The two make exact, identical evaluation budgets
  mechanically verifiable (G6).
- **Test suites.** CEC-2017 runs on **cec2017-py** (official numbering, vectorised, derived from
  official data) with opfunu as the audit cross-check. CEC-2022 runs on **opfunu**, with the
  **official C code** as the independent audit and restoration reference. The engineering suite is
  the sibling project's seven problems, ported with raw constraints exposed and the shared static
  penalty kept.
- **Baselines.**
  - GA, PSO, GWO and **CA** come from a pinned, verbatim, hash-checked **vendored copy** of the
    sibling's `algorithms.py`.
  - WOA comes from mealpy.
  - L-SHADE comes from niapy, at its own population rule (18·D).
  - CMA-ES comes from pycma, run as **IPOP-CMA-ES**.
- **Protocol.** Seeds use common random numbers (CRN), so paired Wilcoxon signed-rank tests with
  Holm correction are legitimate. The tuning set is disjoint from the test suites. The configuration
  is frozen and tagged, and the runner refuses test-suite runs until then. Ablation runs in two
  stages: exploratory before the freeze, confirmatory after.

## Technical Context

Every field below was marked NEEDS CLARIFICATION when planning began. Each is now resolved; the
research.md decision (R1 to R22) that resolves it is given in brackets.

**Language/Version**: CPython 3.11 [R1]. The reference environment is pinned by
`requirements-lock.txt`.

**Primary Dependencies**:

- **Core.** `numpy`, the only runtime dependency of the `tfo` package.
- **Harness.** `scipy`, `pandas` and `matplotlib`.
- **Benchmark suites.**
  - `cec2017-py` at git commit `424a9fa`: the CEC-2017 primary [R3].
  - `opfunu==1.0.4`: the CEC-2022 primary and the CEC-2017 cross-check [R3, R4].
  - The official CEC-2022 C code, used for the audit and cell restoration only [R4].
- **Baselines.**
  - A vendored copy of sibling `algorithms.py` at commit `96af96b`, for CA, GA, PSO and GWO [R8, R9].
  - `mealpy==3.0.3`, installed `--no-deps`, for WOA.
  - `niapy==2.7.1` for L-SHADE.
  - `cma==4.5.0` for IPOP-CMA-ES.
- **Statistics.** `scipy.stats`, plus an in-house Holm correction with a unit test [R12].
- **Tests.** `pytest` and `hypothesis` [R18].

**Storage**: Flat CSV files, as in the sibling, under `results/raw/<experiment>/<suite>/`. Traces are
compressed as `.csv.gz` with deterministic gzip. Configuration is TOML, read with `tomllib` from the
standard library. Each experiment also writes a JSON manifest [R17]. The schema is in
[contracts/results-schema.md](./contracts/results-schema.md).

**Testing**: `pytest`, in four tiers [R18]:

- **Unit.** One module per mechanism, 19 in all, plus the neutral move, account, clock and manager.
- **Contract.** All 9 roster adapters, plus the ledger, the result schema, information parity and
  the hash of the vendored CA file.
- **Integration.** Switchability (G2), ledger equality and an end-to-end smoke run.
- **Golden.** The engineering port matches the sibling's values.

**Target Platform**: A Linux x86-64 workstation with several cores. Runs are process-parallel with
single-threaded BLAS, and the reference environment is recorded in each manifest [R19, R20].

**Project Type**: A research library (`tfo`) plus a benchmark harness (`tfo_bench`) with thin
command-line experiment scripts (`scripts/`) [R2].

**Performance Goals** [R5, R19, R22]:

- Per-mechanism evaluation allocation is **counted exactly**, not estimated (SC-003).
- Wall-clock cost is **measured** as total time, objective time and overhead, for every roster
  algorithm (FR-037).
- Engineering target: TFO's median overhead is at most 50 µs per evaluation at D = 30.
- The whole programme fits the compute envelope declared in `protocol.toml`, at the budget the
  throughput pilot fixes.

**Constraints**:

- **Budgets.** Every algorithm in a cell gets the identical, exact evaluation budget. The budgets
  are each suite's own official MaxFES, verified against the technical reports [R5]:
  - CEC-2017: 10,000·D, which is 300,000 at D = 30.
  - CEC-2022: 200,000 at D = 10 and 1,000,000 at D = 20 (fixed per dimension, not 10,000·D).
  - Engineering: 10,000·D (no official figure; the CEC-2017 rule is carried over and declared).

  A uniform reduction from a pre-committed list is allowed only if the pilot shows it is needed.
- **Information parity** is enforced by type, through the `ProblemView` capability (FR-031).
- **Tuning** happens only on the disjoint tuning set, and the result is frozen and tagged before any
  test run (FR-040, G3).
- **Seeds.** CRN seeds are committed before any test run [R11].
- No application case study (FR-045).
- The sibling repository is read-only.
- No real names appear in any identifier (Principle VI).

**Scale/Scope** [R5, R14, R15]:

| Block | Cells or problems | Algorithms or variants | Runs | Evaluations |
|---|---|---|---|---|
| CEC-2017 main | 29 at D = 30 | 9 | 7,830 | 2.35 × 10⁹ |
| CEC-2022 main | 24 cells run (12 functions × D ∈ {10, 20}); only validated cells are analysed | 9 | 6,480 | 3.89 × 10⁹ |
| Engineering main | 7 | 9 | 1,890 | 7.8 × 10⁷ |
| Ablation (confirmatory) | 6 | 26 new; full TFO and TFO-static reused | 4,680 | about 1.0 × 10⁹ |
| Sensitivity | 6 | 24 one-at-a-time settings + 8 interaction settings | 5,760 | about 1.2 × 10⁹ |
| ε-line experiment | 7 | TFO and TFO-static with the ε-line | 420 | small |
| Formation takeover (H3) | 3 shapes | selection only | 300 | negligible |
| Timing | 6 | 9 | 540 | subset |

The 9 algorithms are TFO, TFO-static, GWO, PSO, GA, WOA, L-SHADE, CMA-ES and CA. CA is a
SHOULD-level reference comparator. The planning projection is about 200 to 400 core-hours, which
the pilot will replace with a measured figure.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**Pre-design verdict: PASS.** Nothing in the planned architecture violates a principle. One gate
item is open but is not a violation: G1's citation gap, which blocks `/speckit-implement`, not this
phase. The real tensions are recorded in Complexity Tracking below.

### Principles

**I. Operator-Family Grounding (NON-NEGOTIABLE) — PASS.**

- Each of the 19 mechanisms maps one-to-one to a named module: `tfo/archetypes/<archetype>.py`,
  `tfo/tactics/<tactic>.py`, or `tfo/manager.py`.
- It also maps to one evaluation tag and one row of mechanism-map.md
  ([contracts/mechanism-interface.md](./contracts/mechanism-interface.md) §2).
- That contract states each operator without metaphor. This is the seed of the manuscript's
  metaphor-free description.
- The registry (tag → module → family → citation) is the single source for the manuscript's
  operator-family table and the CA overlap audit, so the table cannot drift from the code.
- **Resolved:** positional rotation now cites Janson and Middendorf's H-PSO (2005), verified on
  Crossref (research.md R21).

**II. Ablation-Justified Complexity — PASS** (see Complexity rows 1 and 2).

- `TFOConfig.enable` holds one flag per mechanism, and each disabled mechanism has a documented
  neutral default: clipping, full connectivity, no rollback, a single-member archive, and the neutral
  (1+1)-ES step for archetypes.
- Group-level variants: TFO-static, G-topology, and 7 homogeneous squads.
- **TFO-static appears in every experiment.** Every experiment definition that includes TFO must also
  include TFO-static, and the runner refuses any that does not (SC-010).
- Two-stage ablation (R14): a mechanism that measures negligible gets a written remove-or-justify
  disposition, and is never silently kept.

**III. Benchmark Rigor, Honest Losses, No Cherry-Picking — PASS.**

- **Complete suites.** All 29 CEC-2017 functions, all 24 CEC-2022 cells and all 7 engineering
  problems are run. Cells leave the analysis only through the audit and ND rules, which are
  committed before the runs.
- **Roster.** It includes L-SHADE and CMA-ES. CMA-ES is strengthened to IPOP, which works against
  TFO (R8).
- **Losses.** `pairwise.csv` holds every one of the C(k, 2) pairs in every cell. The table
  generators have no outcome-based filter.
- **Pre-registration.** `protocol.toml`, tagged `prereg-v1`, fixes the error floor, the test,
  zero-handling, the Holm family, the direction rule, the ND rule, the seeds and the budgets.
- **Tuning.** It uses a disjoint tuning set, is frozen and tagged, and the runner enforces the
  freeze. TFO-static is tuned first so that H2 is fair (R13).
- **Tests.** Friedman ranks, plus paired Wilcoxon signed-rank tests with Holm correction. Pairing
  is made legitimate by CRN (R11, R12).

**IV. Reproducibility and Measured, Not Estimated, Cost — PASS** (see Complexity row 3).

- Seeds are derived by CRN and committed.
- Code, seeds, raw per-run CSVs, derived CSVs and the scripts that make tables and figures are all
  committed.
- A dual ledger checks that every run spent exactly the budget.
- The timing study uses `perf_counter_ns` on an idle machine with the process pinned to one core,
  over 10 repetitions.
- `validate_presentation.py` re-checks every rendered table cell against the source CSVs, as in the
  sibling.
- The dependency lockfile and a manifest per experiment are committed.

**V. Data Integrity Before Trust — PASS.**

- The audit sits **between execution and analysis** in the pipeline:
  - `audit_preflight.py` runs before any runs;
  - the below-optimum check runs after them;
  - cross-validation runs on the independent implementation (opfunu for CEC-2017; the official C
    code for CEC-2022).
- Restored cells are re-run on the reference backend.
- The ND rule is mechanical and committed in advance.
- Pre-audit numbers are kept under `results/audit/pre_audit/`.
- Analysis refuses cells that have not been audited (`AuditPendingError`).
- This **closes a gap left by the sibling**, which excluded its failing CEC-2022 cells without
  cross-validating them (R4).

**VI. Anonymized Archetypes — PASS.**

- Archetype, mechanism and tag identifiers form a closed allowlist, defined by the registry
  enumeration and taken from mechanism-map.md's tactical-function names.
- A contract test rejects any mechanism, variant or algorithm identifier that is not on the
  allowlist, whether in code or in the results files.
- Homage sentences exist only in the manuscript. No denylist of real names is written into the
  repository.

**Scope constraints.**

- No application module exists in the tree.
- Information parity is enforced through `ProblemView` (C7).
- The sibling is used only through read-only vendoring; it is never imported or modified.
- Prior-art positioning belongs to the manuscript work.

### Quality gates (in constitutional order)

| Gate | When it applies | How the plan satisfies it | Status at plan time |
|---|---|---|---|
| G1 Mechanism map complete | before `/speckit-implement` | Families: 19 of 19. Operator statements without metaphor: mechanism-interface.md §2, to be expanded into full equations by the first implementation task. Citations: 19 of 19 (rotation added, R21). | Design PASS |
| G2 Switchability | before any benchmark run | `enable` flags and neutral defaults; `tests/integration/test_switchability.py` | Design PASS |
| G3 Tuning frozen | before any test-suite run | `scripts/tune.py` on the tuning set; `config/tfo_frozen.toml` plus tag `tfo-frozen-v1`; the runner's hash guard (`ConfigNotFrozenError`) | Design PASS |
| G4 Hypotheses pre-registered | before any test-suite run | H1 to H5 were committed in spec.md (commit `770f41b`). The operational plan in `config/protocol.toml` is tagged `prereg-v1`, and the runner requires the tag. | Design PASS |
| G5 Integrity audited | before analysis | `cell_audit.csv` state machine (data-model.md B4); analysis guard | Design PASS |
| G6 Budget verified | every run | External and internal ledgers; contract C1 and C8; `validate_results.py` checks 3 to 6 | Design PASS |
| G7 Ablation complete | before any mechanism-level claim | `make_tables.py` refuses to write mechanism-level tables unless all single-off variants, all group variants, TFO-static and full TFO exist for all 6 problems × 30 runs | Design PASS |
| G8 Presentation validated | before submission | `scripts/validate_presentation.py`, following the sibling; it also checks that every loss appears in the main-text tables | Design PASS |

### Post-design re-check (after Phase 1)

The Phase 1 artefacts do not change any verdict above. They add four things:

- a concrete home and test invariant for every mechanism
  ([mechanism-interface.md](./contracts/mechanism-interface.md));
- ledger invariants L1 to L7 ([evaluation-ledger.md](./contracts/evaluation-ledger.md));
- schema checks 1 to 9 ([results-schema.md](./contracts/results-schema.md)), which turn G5, G6 and
  Principle VI into automated checks;
- the audit state machine (data-model.md B4).

**Post-design verdict: PASS**, with one open G1 item. That item and the owner decisions listed under
*Open items* must be closed before `/speckit-implement`.

## Project Structure

### Documentation (this feature)

```text
specs/001-football-algorithm/
├── spec.md                  # /speckit-specify output (committed)
├── mechanism-map.md         # 19 mechanisms → operator families (committed)
├── related-work.md          # prior-art review (committed)
├── checklists/requirements.md
├── plan.md                  # this file
├── research.md              # Phase 0: decisions R1–R22
├── data-model.md            # Phase 1: algorithm state + experiment data entities
├── quickstart.md            # Phase 1: validation/run guide
├── contracts/
│   ├── optimizer-interface.md   # tfo.minimize + harness Optimizer protocol + adapter mapping
│   ├── evaluation-ledger.md     # exact budget accounting, dual ledger, invariants L1–L7
│   ├── mechanism-interface.md   # per-mechanism home, operator, eval charge, neutral default, tests
│   └── results-schema.md        # CSV layout, columns, validation checks
└── tasks.md                 # Phase 2 (/speckit-tasks) — NOT created here
```

### Source code (repository root)

```text
pyproject.toml                    # packages tfo + tfo_bench; pytest config; dependency ranges
requirements-lock.txt             # exact pins (reference environment), incl. cec2017-py@424a9fa
requirements-nodeps.txt           # mealpy==3.0.3 (installed --no-deps)
config/
├── protocol.toml                 # pre-registration: budgets, runs, master seeds, roster, stats plan,
│                                 #   ND rule, audit tolerances, compute envelope, CA ω (tag prereg-v1)
├── tuning_set.toml               # FR-040 tuning set (functions, D ∈ {15, 40}, shifts/rotations seed)
├── tfo_defaults.toml             # provisional defaults + tuning candidate grids
└── tfo_frozen.toml               # written by tune.py, committed, tag tfo-frozen-v1
src/tfo/                          # THE ALGORITHM (numpy only; adoptable standalone)
├── __init__.py                   # minimize, TFOConfig, TFO_STATIC
├── api.py                        # minimize() → TFOResult
├── config.py                     # TFOConfig, enable flags, variant builders, config_hash
├── registry.py                   # mechanism tag ↔ module ↔ family ↔ citation (allowlist; G1/VI)
├── squad.py                      # Squad (SoA), Ball, KeeperArchive, TabuRegister
├── clock.py                      # MatchClock (fixtures by evaluations)
├── account.py                    # EvalAccount: tagging, truncation, incumbent, checkpoints
├── rng.py                        # per-mechanism RNG streams (SeedSequence spawn)
├── engine.py                     # iteration order (mechanism-interface.md §3)
├── manager.py                    # [19] tactical state machine; disabled = TFO-static
├── neutral.py                    # neutral (1+1)-ES fallback move
├── trace.py                      # RunTrace: tactical RLE, per-mechanism counts, summaries
├── archetypes/                   # [1–8]
│   ├── sweeper_keeper.py  zonal_centre_back.py  overlapping_wing_back.py
│   ├── deep_lying_playmaker.py  box_to_box.py  destroyer.py  virtuoso.py  finisher.py
└── tactics/                      # [9–18]
    ├── formation.py  rotation.py  possession.py  pressing.py  counter_attack.py
    └── set_pieces.py  offside.py  substitutions.py  fatigue.py  var_review.py
src/tfo_bench/                    # THE HARNESS
├── ledger.py                     # CountingObjective (external ledger), BudgetExhausted
├── seeds.py                      # CRN seed derivation
├── problems/
│   ├── base.py                   # Problem, ProblemView (unit-box decoder, capability gating)
│   ├── cec2017.py                # cec2017-py backend, official labels F1, F3–F30
│   ├── cec2022.py                # opfunu backend
│   ├── engineering.py            # 7 problems as (cost, G) + shared static penalty
│   ├── tuning.py                 # tuning-set functions + 2 constrained tuning problems
│   └── reference/                # opfunu CEC-2017 cross-check; official-C CEC-2022 ctypes shim
├── algorithms/
│   ├── base.py                   # Optimizer protocol, OptimizeResult, roster registry
│   ├── tfo_adapter.py            # TFO, TFO-static, ablation/sensitivity variants
│   ├── sibling.py                # CA, GA, PSO, GWO adapters over the vendored file
│   ├── woa.py  lshade.py  cmaes.py
│   └── vendor/
│       ├── chess_algorithms_96af96b.py   # verbatim sibling algorithms.py (MIT)
│       └── PROVENANCE.md                 # URL, commit SHA, Zenodo DOI, SHA-256
├── runner.py                     # job enumeration, process pool, single-writer CSV, resume,
│                                 #   G3/G4 guards, TFO-static pairing guard
├── records.py                    # results-schema writers + validators
├── audit.py                      # preflight, below-optimum, cross-validation, ND rule, dispositions
├── stats.py                      # error floor, signed-rank, Holm, W/T/L, Friedman, rank-sum check
├── tables.py  figures.py         # derived CSV → manuscript tables/figures
└── manifest.py                   # environment fingerprint
scripts/                          # thin CLIs, one per experiment (sibling naming)
├── audit_preflight.py  tune.py  pilot.py  run_suite.py  run_ablation.py  run_sensitivity.py
├── run_takeover.py  run_epsilon.py  run_timing.py  analyze.py  validate_results.py
└── compare_runs.py  make_tables.py  make_figures.py  validate_presentation.py
tests/
├── unit/                         # test_<mechanism>.py ×19, test_neutral, test_account, test_clock,
│                                 #   test_manager, test_holm, test_seeds
├── contract/                     # test_optimizer_contract (9 adapters), test_ledger,
│                                 #   test_results_schema, test_information_parity,
│                                 #   test_vendor_integrity, test_identifier_allowlist
├── integration/                  # test_switchability, test_smoke_pipeline, test_reproducibility
└── golden/                       # engineering port fixtures (sibling values), tuning-set optima
results/                          # see contracts/results-schema.md §1 (raw/, audit/, derived/,
                                  #   manifests/, _smoke/ gitignored)
```

**Structure Decision.** The layout uses src-layout packages (`tfo`, `tfo_bench`) with thin scripts.
This deliberately departs from the sibling's flat `src/*.py` (research.md R2), because:

- 19 switchable mechanisms need one traceable, unit-testable home each (G1, G2, User Story 1);
- practitioners must be able to install `tfo` without the benchmark stack (User Story 5).

The sibling's proven conventions are kept: one script per experiment with `--smoke` and `--part`,
flat CSV results, a dedicated audit script, and `validate_presentation.py`. Manuscript sources
(Quarto, as in the sibling) are out of scope for this plan's tree and will be added under `paper/`
when the manuscript work begins.

## Complexity Tracking

> Recorded because the Constitution Check found real tensions that need justification.

| Violation or tension | Why needed | Simpler alternative rejected because |
|---|---|---|
| **1. Surface area: 19 individually switchable mechanisms running on three kinds of clock** (Principle II invites the question whether this much is ornamental) | The spec commits to all 19 (FR-005 to FR-026). The research question is *which* structural axes carry performance, and the ablation is the pruning tool Principle II prescribes. The surface area is contained: one module and one contract per mechanism, isolated RNG streams, and per-mechanism unit tests. | *Starting from a minimal subset* would decide the ablation's outcome without evidence and give up the three-axis claim (and SC-002's family count). *Merging mechanisms into composite operators* would make one-at-a-time ablation impossible (G2, G7). |
| **2. Ablation-driven pruning (Principle II) conflicts with no tuning on test suites (Principle III).** Pruning on test-suite ablation results is itself a form of tuning on the test suites. | A two-stage ablation (R14). Stage A is exploratory, on the **tuning set**, before the freeze, and drives pruning. Stage B is confirmatory, on the six test problems, after the freeze, and is reported as found. A mechanism found negligible in Stage B gets a written remove-or-justify disposition, and any pruned variant is reported in a separately labelled post-hoc table with SC-002 reported again. The headline algorithm is never silently changed. | *Pruning on the test-suite ablation, as the sibling did* leaks test information into the published algorithm. *Never pruning* violates Principle II's "remove or justify". |
| **3. SC-005 and Principle IV: regenerated "identically"** cannot be guaranteed across arbitrary hardware when experiments are re-run. NumPy's SIMD-dispatched maths can differ by 1 ULP between CPUs, and in a stochastic optimiser that can change an acceptance decision. | Two guaranteed levels (R20). (a) Every table value is regenerated identically on any machine from the committed raw CSVs. (b) The raw results are regenerated bit-identically on the recorded reference environment (lockfile, CPU features, `NPY_DISABLE_CPU_FEATURES` fixed). The manuscript's reproducibility statement uses this wording. | *Claiming bit-identical re-execution on any hardware* is unverifiable. *Forcing scalar code paths* costs heavily in throughput and cannot be fully controlled from Python. *A Docker image* pins software but not the CPU; it is provided as a convenience only. |

## Open items (owner action before `/speckit-implement`)

1. ~~**G1: rotation citation.**~~ **Resolved 2026-09-25.** Janson and Middendorf (2005) was
   verified on Crossref and added to `mechanism-map.md` (R21).
2. ~~**Spec discrepancy: CEC-2022 budget.**~~ **Resolved 2026-09-25.** The MaxFES figures were
   verified against the primary reports: CEC-2017 is 10,000·D, and CEC-2022 is 200,000 at D = 10
   and 1,000,000 at D = 20. The spec's Assumptions now state each suite's own rule (R5).
3. ~~**CMA-ES variant.**~~ **Resolved 2026-09-25.** IPOP-CMA-ES is kept as the sole CMA-ES. There
   are two conformance fixes: `restarts=20` so that the budget, not the restart cap, ends every run,
   and a fresh `x0` for each restart. The manuscript footnotes the difference from the sibling's
   plain CMA-ES (R8).
4. **Validated CEC-2022 cell count.** The sibling's figure of 16 cells refers to opfunu at a
   15,000-evaluation budget. TFO's count will come from its own audit, with the cross-validation
   stage the sibling lacked, and may differ.
5. **Carried over from the spec.** Read SLOCA's full text before submission (related-work.md).

## Phase status

- Phase 0 (research.md): **complete**. All NEEDS CLARIFICATION items are resolved (R1 to R22).
- Phase 1 (data-model.md, contracts/ × 4, quickstart.md): **complete**. The Constitution Check has
  been re-run and passes, with the open items above.
- Phase 2 (tasks.md): **not started**. It is the next command, `/speckit-tasks`.
