---

description: "Task list for feature 001-football-algorithm"
---

# Tasks: Total Football Optimizer (TFO), Mechanism Design and Evaluation Programme

**Input**: Design documents from `/specs/001-football-algorithm/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/*.md, mechanism-map.md, `.specify/memory/constitution.md`

**Tests**: Included. The constitution's rigor requirements (Principle I re-implementability, Principle
II ablation-justified complexity, Principle IV reproducibility, Principle V data integrity) make
contract tests for all 4 contracts, unit tests for all 19 mechanisms, and data-integrity audit tests
mandatory, not optional. Tests are written before the implementation task(s) that must satisfy them.

**Organization**: Tasks are grouped by the 5 user stories of spec.md, in priority order (P1–P5).
Phase 2 (Foundational) carries almost the entire `tfo` algorithm package and `tfo_bench` harness,
because every user story depends on TFO actually running correctly, its 9-algorithm roster being
budget-conformant, and the data-integrity audit gating analysis. Each story phase then adds the
experiments, statistics, tables, and documents that are specific to that story's Independent Test.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependency on an incomplete task)
- **[Story]**: US1–US5, per spec.md. Setup, Foundational and Polish tasks carry no story label.
- Every task names an exact file path. Where a task implements a field or rule with a stated
  constraint in data-model.md, the constraint is quoted verbatim.

## Path Conventions

Per plan.md's Project Structure: `src/tfo/` (the algorithm, NumPy-only), `src/tfo_bench/` (the
benchmark harness), `scripts/` (thin CLIs), `config/` (TOML configuration), `tests/{unit,contract,
integration,golden}/`, `results/` (raw/audit/derived/manifests, gitignored `_smoke/`).

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: repository scaffolding, pinned dependencies, and the one-off vendoring of the sibling's
baseline code. No mechanism logic is written here.

- [ ] T001 Create the source-tree skeleton per plan.md's Project Structure: `src/tfo/`,
  `src/tfo/archetypes/`, `src/tfo/tactics/`, `src/tfo_bench/`, `src/tfo_bench/problems/`,
  `src/tfo_bench/problems/reference/`, `src/tfo_bench/algorithms/`,
  `src/tfo_bench/algorithms/vendor/`, `scripts/`, `config/`, `tests/unit/`, `tests/contract/`,
  `tests/integration/`, `tests/golden/`, `results/`, each with an `__init__.py` where it is a Python
  package
- [ ] T002 [P] Create `pyproject.toml` declaring the `tfo` and `tfo_bench` packages (src-layout),
  `numpy` as `tfo`'s only runtime dependency, `scipy`/`pandas`/`matplotlib` for `tfo_bench`, and
  `[tool.pytest.ini_options]` markers `unit`, `contract`, `integration`, `golden`
- [ ] T003 [P] Create `requirements-lock.txt` pinning exact versions: `cec2017-py` at git commit
  `424a9fa2757914c3e4cfdd8f59a268b1aeb3197f`, `opfunu==1.0.4`, `niapy==2.7.1`, `cma==4.5.0`,
  `pytest`, `hypothesis`, and the `numpy`/`scipy`/`pandas`/`matplotlib` versions measured during
  planning (research.md's "Measured" environment note)
- [ ] T004 [P] Create `requirements-nodeps.txt` pinning `mealpy==3.0.3`, installed with
  `pip install --no-deps -r requirements-nodeps.txt` because its own dependency metadata breaks on
  Python 3.11+ otherwise (research.md R1)
- [ ] T005 [P] Update `.gitignore`: ignore `results/_smoke/`, `.venv/`, `__pycache__/`, build
  artifacts; keep `results/raw/`, `results/audit/`, `results/derived/`, `results/manifests/` tracked
- [ ] T006 Vendor the sibling's `algorithms.py` at commit `96af96bbb5ef36514ae11a0cc5695d4a6211d9a4`
  verbatim, unmodified, as `src/tfo_bench/algorithms/vendor/chess_algorithms_96af96b.py` (research.md
  R9); the sibling repository itself is read-only and is never imported or modified
- [ ] T007 [P] Write `src/tfo_bench/algorithms/vendor/PROVENANCE.md`: source URL, commit SHA
  `96af96bbb5ef36514ae11a0cc5695d4a6211d9a4`, Zenodo DOI `10.5281/zenodo.22854043`, MIT licence
  notice, and the SHA-256 of the vendored file (research.md R9)
- [ ] T008 [P] Create placeholder `config/protocol.toml`, `config/tuning_set.toml`,
  `config/tfo_defaults.toml`, `config/tfo_frozen.toml`, each with a header comment naming the
  research.md decision (R5, R11, R12, R13) and constitution gate (G3, G4) it will hold once populated
  in Phase 2

**Checkpoint**: repository scaffolding, pins, and the vendored baseline file exist. No algorithm code
yet.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: the `tfo` algorithm package (all 19 mechanisms, engine, manager, public entry point), the
`tfo_bench` harness (ledger, 4 problem suites, 9 baseline adapters, results schema, runner, audit
pipeline), and the pre-registration/tuning-freeze gates. Every user story depends on this phase,
because none of the 5 Independent Tests can run against an algorithm that does not yet execute
correctly, budget-conform, or pass the data-integrity audit.

**⚠️ CRITICAL**: no user-story work can begin until this phase is complete.

### 2.1 Core algorithm state and configuration

- [ ] T009 [P] Unit test `tests/unit/test_config.py`: `TFOConfig` loads from TOML, `config_hash` is
  the SHA-256 of the canonical JSON of the parsed configuration, and `.ablate("virtuoso")`,
  `.homogeneous("destroyer")`, `.with_(...)` build the variants of data-model.md A15
- [ ] T010 [P] Unit test `tests/unit/test_squad.py`: property tests for data-model.md A1's validation
  rules — "`X` always lies in [0, 1]^D", "`f_P[i] ≤ f[i]` for every i", and "An agent's archetype is
  **not** stored on the agent. It is read through `role_sheet[slot[i]]`, so rotation changes it"
- [ ] T011 [P] Unit test `tests/unit/test_clock.py`: "Fixture k ends at the first iteration end with
  evals_used ≥ k·B/n_fixtures", and the four boundary hooks fire in the documented order (rotation,
  zonal redraw, stamina recovery, substitution cap reset)
- [ ] T012 [P] Unit test `tests/unit/test_seeds.py`: per-mechanism RNG streams spawned from
  `SeedSequence(seed)` at fixed registry indices are independent, and disabling one mechanism does
  not shift another mechanism's draws (research.md R11)
- [ ] T013 [P] Unit test `tests/unit/test_account.py` (property-based, `hypothesis`): ledger
  invariants L1 "`evals_used ≤ budget` after any sequence of calls, including batches larger than the
  remaining budget", L2 "`sum(evals_by_tag.values()) == evals_used`", L5 "`best_f` equals the
  minimum over every value the ledger returned. There is no other source for it.", L6 "Zero-cost
  operations (VAR rollback, formation re-lay, rotation, fatigue, archive update) do not change
  `evals_used`", L7 "The objective is never called with a row outside [0, 1]^D"
- [ ] T014 [P] Implement `src/tfo/registry.py`: the mechanism tag ↔ module ↔ family ↔ citation
  registry and the closed 21-member tag enumeration (`init`, the 8 archetype tags, the 11 tactic
  tags, `neutral`); this is the single source for the manuscript's operator-family table and the CA
  overlap audit, and the identifier allowlist for Principle VI
- [ ] T015 [P] Implement `src/tfo/config.py`: the `TFOConfig` frozen dataclass with the `enable`
  (19 booleans, default all true), `homogeneous`, `squad`, `states`, `manager`, `operators`,
  `constraints` groups of data-model.md A15, TOML loading, `config_hash`, and the `.ablate()`,
  `.homogeneous()`, `.with_()` variant builders (makes T009 pass; depends on T014)
- [ ] T016 [P] Implement `src/tfo/squad.py`: Squad structure-of-arrays (`X, f, P, f_P, slot, stamina,
  stagnation, mesh, fin_fail, fin_last_restart, X_rev, f_rev, moved_since_rev,
  produced_best_since_rev`), Ball (A4), KeeperArchive (A5) with the insertion rule "it is better than
  the worst member, **and** it is at least `min_sep` from every member", and TabuRegister (A6)
  (makes T010 pass)
- [ ] T017 [P] Implement `src/tfo/clock.py`: `MatchClock` (`B, n_fixtures, fixture, iteration, t`)
  and the ordered fixture-boundary hooks (makes T011 pass)
- [ ] T018 [P] Implement `src/tfo/rng.py`: per-mechanism RNG stream spawning from `SeedSequence` at
  fixed registry indices (makes T012 pass)
- [ ] T019 Implement `src/tfo/account.py`: `EvalAccount` with `evaluate(X, tag)` truncation-at-budget,
  `evals_by_tag` over the 21-tag enumeration, and the incumbent `(x_best, f_best)` updated on every
  improving evaluation so that "a later VAR rollback therefore cannot remove the incumbent" (makes
  T013 pass; depends on T014)
- [ ] T020 [P] Implement `src/tfo/neutral.py`: the neutral (1+1)-ES fallback move
  `y = x_i + σ·s_i·N(0, I)`, tag `neutral`, greedy acceptance (research.md R14)

### 2.2 Player archetypes (8 mechanisms, FR-005–FR-012)

- [ ] T021 [P] Unit test `tests/unit/test_sweeper_keeper.py`: "`A[0]` always equals the incumbent;
  the separation between members is at least `min_sep`; the archive never exceeds K members"
- [ ] T022 [P] Unit test `tests/unit/test_zonal_centre_back.py`: "every proposal lies inside the
  agent's stratum; after a redraw, the strata are disjoint and their projections tile [0, 1]"
- [ ] T023 [P] Unit test `tests/unit/test_overlapping_wing_back.py`: "y lies coordinate-wise between
  c and o; the keep-better rule holds"
- [ ] T024 [P] Unit test `tests/unit/test_deep_lying_playmaker.py`: "the partner's graph distance is
  at least d_max − 1; y lies in the α-widened box"
- [ ] T025 [P] Unit test `tests/unit/test_box_to_box.py`: "donors come only from N(i) ∪ {i}; x_d's
  line is at most x_a's line"
- [ ] T026 [P] Unit test `tests/unit/test_destroyer.py`: "the better member of each pair is never
  moved; the kicked agent lands outside the niche, or its kick is recorded as failing to leave it"
- [ ] T027 [P] Unit test `tests/unit/test_virtuoso.py`: "the poll stops at the first improvement; the
  expand and contract rules hold; the mesh stays within [h_min, h_max]"
- [ ] T028 [P] Unit test `tests/unit/test_finisher.py`: "jumps are centred on the ball, not on the
  incumbent; a restart never reuses the last restart index when K > 1"
- [ ] T029 [P] Implement `src/tfo/archetypes/sweeper_keeper.py` (mechanism-interface.md §2.1,
  FR-005): bounded distance-diverse archive updated by a hook on every account evaluation, supplying
  ball resets and Finisher restarts (makes T021 pass)
- [ ] T030 [P] Implement `src/tfo/archetypes/zonal_centre_back.py` (§2.2, FR-006): `y ~ U(stratum_k)`
  against the current Latin-hypercube stratification (A9), redrawn at fixture boundaries (makes T022
  pass)
- [ ] T031 [P] Implement `src/tfo/archetypes/overlapping_wing_back.py` (§2.3, FR-007):
  quasi-opposite step about the squad centroid with probability Jr, keep-better rule (makes T023
  pass)
- [ ] T032 [P] Implement `src/tfo/archetypes/deep_lying_playmaker.py` (§2.4, FR-008): BLX-α
  recombination with a partner at graph distance ≥ d_max − 1, the declared long-range exception to
  FR-002 (makes T024 pass)
- [ ] T033 [P] Implement `src/tfo/archetypes/box_to_box.py` (§2.5, FR-009): differential move
  `v = x_nbest(i) + F·(x_d − x_a)` plus binomial crossover (makes T025 pass)
- [ ] T034 [P] Implement `src/tfo/archetypes/destroyer.py` (§2.6, FR-010): niche-pair detection and
  unconditional differential kick of the worse member of each pair (makes T026 pass)
- [ ] T035 [P] Implement `src/tfo/archetypes/virtuoso.py` (§2.7, FR-011): coordinate-wise compass
  poll with per-agent mesh expand-on-success/contract-on-failure (makes T027 pass)
- [ ] T036 [P] Implement `src/tfo/archetypes/finisher.py` (§2.8, FR-012): Lévy(β) jump centred on the
  ball plus elite-restart-after-F_fail-consecutive-failures logic (makes T028 pass)

### 2.3 Team-level tactics (11 mechanisms, FR-013–FR-022)

- [ ] T037 [P] Unit test `tests/unit/test_formation.py`: "the three shapes exist for n; the ratio is
  monotone across them; a re-lay leaves X and f unchanged; the vacancy rule holds", quoting
  data-model.md A3's "Vacancies = lines × lanes − n_out, with 0 ≤ vacancies < lanes" and "The ratio
  is strictly decreasing from compact to balanced to stretched"
- [ ] T038 [P] Unit test `tests/unit/test_rotation.py`: "only better-deeper/worse-upfield pairs swap;
  the role-sheet composition is preserved"
- [ ] T039 [P] Unit test `tests/unit/test_possession.py`: "the τ acceptance rule holds; the
  neutral-pass cap stops plateau loops; receivers are always neighbours of the carrier"
- [ ] T040 [P] Unit test `tests/unit/test_pressing.py`: "the cap on |P| holds; with ρ = 0 no agent
  presses"
- [ ] T041 [P] Unit test `tests/unit/test_counter_attack.py`: "the burst's step sizes decay
  geometrically; the burst is truncated exactly at the budget; the trigger requires both the
  improvement and the distance conditions"
- [ ] T042 [P] Unit test `tests/unit/test_set_pieces.py`: "the schedule and the rotation order are
  fixed; on a 1-D quadratic, the free kick hits the vertex exactly"
- [ ] T043 [P] Unit test `tests/unit/test_offside.py` (property-based): "the repaired point lies in
  [0, 1]^D", "each repaired coordinate lies between x_j^old and the violated bound", and "points
  arbitrarily close to a bound remain reachable" (the "optimum on or near a bound" edge case), plus
  `ε(T_c) = 0`
- [ ] T044 [P] Unit test `tests/unit/test_substitutions.py`: "the cap is honoured; both trigger
  conditions are required; the tabu entry is written"
- [ ] T045 [P] Unit test `tests/unit/test_fatigue.py`: "drain is monotone in distance; recovery
  shrinks with t; substitutes enter with s = 1"
- [ ] T046 [P] Unit test `tests/unit/test_var_review.py`: "the rollback costs 0 evals; aspiration
  keeps a move that set a new best; the incumbent survives any rollback"
- [ ] T047 [P] Unit test `tests/unit/test_manager.py`: "an oscillating input cannot cause state
  changes on consecutive iterations; HIGH_PRESS is never entered before t_press; CHASING is present
  only in TFO"
- [ ] T048 [P] Implement `src/tfo/tactics/formation.py` (§2.9, FR-013, FR-002): lattice shapes,
  toroidal von Neumann neighbour tables, graph distances, fully-connected neutral default (makes
  T037 pass)
- [ ] T049 Implement `src/tfo/tactics/rotation.py` (§2.10, FR-022): deep-to-upfield row swap at
  fixture boundaries, no wrap across the torus (makes T038 pass; depends on T048 for slot/row
  semantics)
- [ ] T050 [P] Implement `src/tfo/tactics/possession.py` (§2.11, FR-014): pass chain with
  τ-threshold retention, neutral-streak cap, R_loss reset (makes T039 pass)
- [ ] T051 [P] Implement `src/tfo/tactics/pressing.py` (§2.12, FR-015): distance-gated pressing set
  capped at ⌊0.5·n_out⌋, shrinking-encircling step (makes T040 pass)
- [ ] T052 [P] Implement `src/tfo/tactics/counter_attack.py` (§2.13, FR-016): event trigger
  `f(y) < f_b − Δ_mat·max(|f_b|, 1e-12)` and `‖y − x_b‖ > d_trans`, ball relocation, geometrically
  decaying burst (makes T041 pass)
- [ ] T053 [P] Implement `src/tfo/tactics/set_pieces.py` (§2.14, FR-017): fixed corner/free-kick
  rotation on a fixed schedule, never adapted (makes T042 pass)
- [ ] T054 [P] Implement `src/tfo/tactics/offside.py` (§2.15, FR-018): bound repair
  `y_j ← x_old,j + U(0,1)·(bound_j − x_old,j)`, plain-clipping neutral default, and the ε-line
  `ε(t) = ε₀(1 − t/T_c)^cp` with ε-lexicographic comparison, active only when constraints are exposed
  (makes T043 pass)
- [ ] T055 [P] Implement `src/tfo/tactics/substitutions.py` (§2.16, FR-019): stagnation+stamina
  trigger, per-fixture cap, tabu-register write on the outgoing position (makes T044 pass)
- [ ] T056 [P] Implement `src/tfo/tactics/fatigue.py` (§2.17, FR-020): distance-proportional drain,
  fixture-boundary recovery that shrinks over the run, full-stamina substitutes (makes T045 pass)
- [ ] T057 [P] Implement `src/tfo/tactics/var_review.py` (§2.18, FR-021): periodic audit against
  tabu/collision/feasibility checks, zero-cost rollback with aspiration (makes T046 pass)
- [ ] T058 Implement `src/tfo/manager.py` (§2.19, FR-023–FR-026): the four-state machine (BUILD_UP,
  CONTROL, HIGH_PRESS, CHASING) with EMA inputs, the priority-ordered guards of data-model.md A8,
  hysteresis/dwell (FR-025), and disablement to the frozen CONTROL vector for TFO-static (makes T047
  pass; depends on T048, T051)

### 2.4 Engine, trace, public entry point

- [ ] T059 [P] Integration test `tests/integration/test_engine_order.py`: the 9-step iteration order
  of mechanism-interface.md §3 is deterministic and pinned
- [ ] T060 [P] Unit test `tests/unit/test_trace.py`: TacticalSegment run-length encoding is lossless
  and contiguous, MechanismEvalCount sums to `evals_used`
- [ ] T061 Implement `src/tfo/engine.py`: the iteration loop of mechanism-interface.md §3, wiring
  every mechanism module behind its `cfg.enable` flag with the documented neutral fallback,
  terminating cleanly on `BudgetExhausted` from any depth (makes T059 pass; depends on T014–T058)
- [ ] T062 [P] Implement `src/tfo/trace.py`: `RunTrace` (TacticalSegment, MechanismEvalCount, the
  per-run summaries of A14) (makes T060 pass)
- [ ] T063 Implement `src/tfo/api.py` and `src/tfo/__init__.py`: `minimize()` returning `TFOResult`
  (`x_best, f_best, evals_used, evals_by_mechanism, curve, tactical_trace, summary, config_hash`) and
  the packaged `TFO_STATIC` config (optimizer-interface.md §1) (depends on T061)
- [ ] T064 [P] Unit test `tests/unit/test_api_public_entry.py`: `tfo.minimize` runs standalone with
  only NumPy on the import path, and `TFO_STATIC` has `enable.manager = False`

### 2.5 External evaluation ledger and CRN seeds

- [ ] T065 [P] Contract test `tests/contract/test_ledger.py`: ledger invariants L3 "For TFO runs,
  internal `evals_used` equals external `evals_used`" and L4 "`curve` is non-increasing and has 100
  entries. Entry k (k = 1, …, 100) is the best-so-far after exactly ⌈k·B/100⌉ evaluations"
- [ ] T066 Implement `src/tfo_bench/ledger.py`: `CountingObjective` (evaluation-ledger.md §1) — batch
  truncation exactly at the budget ("it evaluates only the first r rows, records them, and then
  raises `BudgetExhausted`"), the [0, 1]^D box assertion, the 100-checkpoint curve,
  `objective_time_ns` (makes T065 pass)
- [ ] T067 [P] Implement `src/tfo_bench/seeds.py`: CRN seed derivation
  `SeedSequence([MASTER_SEED, suite_code, function_id, dim, run]).generate_state(1)[0] & 0x7FFFFFFF`,
  kept nonzero, shared across every algorithm and variant at the same (cell, run) (research.md R11)
- [ ] T068 [P] Unit test `tests/unit/test_seeds_crn.py`: the same (suite, cell, run) key yields the
  identical seed for every algorithm and every ablation/sensitivity variant

### 2.6 Benchmark problems (4 suites)

- [ ] T069 [P] Contract test `tests/contract/test_information_parity.py`: "calling `view.constraints`
  raises `CapabilityError` unless the job's experiment is `epsilon`" (C7)
- [ ] T070 Implement `src/tfo_bench/problems/base.py`: `Problem`, `ProblemView` (unit-box decoder
  `x = lb + (ub − lb) ⊙ u`, capability gating for `constraints`) (makes T069 pass; depends on T066)
- [ ] T071 [P] Implement `src/tfo_bench/problems/cec2017.py`: cec2017-py backend at official
  numbering F1, F3–F30, D = 30 (research.md R3)
- [ ] T072 [P] Implement `src/tfo_bench/problems/cec2022.py`: opfunu backend, classes F12022–F122022,
  D ∈ {10, 20} (research.md R4)
- [ ] T073 [P] Implement `src/tfo_bench/problems/engineering.py`: the 7 ported problems returning
  `(cost, G)`, shared static penalty `f = cost + 10⁶ Σ max(0, gᵢ)²`, the same bounds, rounding and
  f_ref values as the sibling (research.md R10)
- [ ] T074 [P] Implement `src/tfo_bench/problems/tuning.py`: the 7 tuning functions (Sphere,
  Schwefel 1.2, Schwefel 2.22, Alpine N.1, Salomon, Styblinski–Tang, Dixon–Price) at D ∈ {15, 40}
  with random shift/rotation, plus CEC-2006 G04 and the tubular column design (research.md R13)
- [ ] T075 [P] Implement `src/tfo_bench/problems/reference/`: the opfunu CEC-2017 cross-check
  wrapper and the official-C CEC-2022 ctypes shim, built only for audit and cell-restoration use
  (research.md R3, R4)
- [ ] T076 [P] Golden test `tests/golden/test_engineering_port.py`: fixed random/boundary points
  evaluated on the sibling's read-only `engineering_problems.py` must match the port "to 1e-12
  relative" (research.md R10)
- [ ] T077 [P] Golden test `tests/golden/test_tuning_optima.py`: every tuning function passes the
  preflight audit at its known optimum

### 2.7 Baseline algorithm adapters and the optimizer contract

- [ ] T078 Contract test `tests/contract/test_optimizer_contract.py`, parametrised over all 9 roster
  adapters (TFO, TFO-static, CA, GA, PSO, GWO, WOA, L-SHADE, CMA-ES (IPOP)): invariants C1 "`ledger.
  evals_used ≤ budget` on every run. It equals `budget` unless `status == \"self_terminated\"`", C2
  determinism, C3 box membership, C4 `algo_reported_best_f ≥ ledger.best_f −
  1e-12·max(1, abs(ledger.best_f))`, C5 exception handling, C6 shared-initial-population, and C8
  "TFO family only: `sum(extras[\"evals_by_mechanism\"].values()) == ledger.evals_used`" (depends on
  T070)
- [ ] T079 [P] Contract test `tests/contract/test_vendor_integrity.py`: the SHA-256 of
  `chess_algorithms_96af96b.py` matches `PROVENANCE.md` (research.md R9)
- [ ] T080 Implement `src/tfo_bench/algorithms/base.py`: the `Optimizer` Protocol, `OptimizeResult`,
  and the roster registry (optimizer-interface.md §2)
- [ ] T081 Implement `src/tfo_bench/algorithms/tfo_adapter.py`: `TFOAdapter(config)` calling
  `tfo.minimize`, plus the ablation/sensitivity variant constructors (depends on T063, T080)
- [ ] T082 [P] Implement `src/tfo_bench/algorithms/sibling.py`: `CAAdapter`, `GAAdapter`,
  `PSOAdapter`, `GWOAdapter` over the vendored file, with `iters` derived per algorithm so each
  schedule ends exactly at the budget (research.md R8, R9) (depends on T006, T080)
- [ ] T083 [P] Implement `src/tfo_bench/algorithms/woa.py`: `WOAAdapter` over
  `mealpy.WOA.OriginalWOA`, `epoch = B // 30 − 1`, `termination={"max_fe": B}`, ledger hard stop
  since mealpy's own cap was measured to overshoot (depends on T080)
- [ ] T084 [P] Implement `src/tfo_bench/algorithms/lshade.py`: `LSHADEAdapter` over niapy's L-SHADE,
  `population_size = 18·D`, `Task(max_evals=B)` (depends on T080)
- [ ] T085 [P] Implement `src/tfo_bench/algorithms/cmaes.py`: `CMAESAdapter` over `cma.fmin2` as
  IPOP-CMA-ES, `restarts=20`, `incpopsize=2`, `x0` a callable drawing a fresh uniform point per
  restart, results read only from the ledger since `fmin2` "returns the best of the last run only"
  (research.md R8) (depends on T080)

### 2.8 Results schema, runner, manifest

- [ ] T086 [P] Contract test `tests/contract/test_results_schema.py`: the 9 validation checks of
  results-schema.md §9
- [ ] T087 Implement `src/tfo_bench/records.py`: writers and validators for `runs.csv`, `curves.csv`,
  `mechanism_evals.csv`, `tactical_trace.csv.gz`, `best_x.csv` per results-schema.md §2–§6, gzip
  `mtime=0` for reproducible bytes (makes T086 pass)
- [ ] T088 [P] Implement `scripts/validate_results.py`: runs the 9 checks of results-schema.md §9
  against a results directory, exit code 1 on any failure
- [ ] T089 Implement `src/tfo_bench/runner.py`: job enumeration (`ExperimentJob` of data-model.md
  B5), a `ProcessPoolExecutor` pool with `OMP_NUM_THREADS`/`OPENBLAS_NUM_THREADS`/`MKL_NUM_THREADS`
  set to 1, single-writer CSV append/checkpoint/resume keyed by (algorithm, cell, run), the G3
  `ConfigNotFrozenError` guard, the G4 pre-registration-tag guard, and the SC-010 guard that refuses
  any experiment definition including TFO without also including TFO-static (depends on T081, T087)
- [ ] T090 [P] Implement `src/tfo_bench/manifest.py`: `EnvironmentManifest` (git SHA and dirty flag,
  lockfile/config SHA-256, library versions, CPU model/flags, `NPY_DISABLE_CPU_FEATURES`, start/end
  times, worker/job counts) per data-model.md B8
- [ ] T091 [P] Unit test `tests/unit/test_manifest.py`: "a dirty working tree is refused for
  non-smoke runs"; the fingerprint includes every pinned library version

### 2.9 Data-integrity audit pipeline

Placed here, immediately after the core algorithm and before any story-specific experiment, per
Principle V ("Data Integrity Before Trust") and the requirement that the audit be an early gate, not
an afterthought.

- [ ] T092 [P] Contract test `tests/contract/test_audit_state_machine.py`: the `CellAudit`
  disposition transitions of data-model.md B4 exactly follow "pending --preflight fail-->
  cross_validating", "pending --preflight pass--> preflight_ok --runs, no run below f*--> validated",
  "--any run below f*--> cross_validating", "cross_validating --passes on reference--> restored",
  "cross_validating --fails on reference--> excluded", "validated | restored --ND rule fires-->
  non_discriminative"
- [ ] T093 Implement `src/tfo_bench/audit.py`: preflight tolerance
  "|f(x*) − f*| ≤ 1e-6·max(1, |f*|)", the below-optimum check
  "best_f < f* − 1e-6·max(1, |f*|)", cross-validation against opfunu (CEC-2017) and the official C
  code (CEC-2022), the mechanical ND rule (research.md R12.5), and the engineering
  `improvement`/`penalty_artifact` classification of B4 (makes T092 pass; depends on T075)
- [ ] T094 [P] Implement `scripts/audit_preflight.py`: runs the preflight stage of `audit.py` for
  each suite and writes `results/audit/cell_audit.csv` with one row per cell
- [ ] T095 [P] Unit test `tests/unit/test_audit_pre_audit_retention.py`: "Pre-audit numbers are never
  deleted" — a restored or excluded cell's pre-audit numbers remain readable under
  `results/audit/pre_audit/<suite>/…`
- [ ] T096 [P] Implement `src/tfo_bench/stats.py`: the error floor (errors below 1e-8 set to 0),
  Wilcoxon signed-rank per cell (`zero_method="pratt"`, stated tie handling for the "ties in paired
  tests" edge case), the Holm correction, Friedman mean ranks, the Mann–Whitney robustness check, and
  the mechanical rule "a cell is non-discriminative if none of its C(k, 2) pairwise tests is
  significant after Holm correction" (research.md R12)
- [ ] T097 [P] Unit test `tests/unit/test_holm.py`: the in-house Holm correction is unit-tested
  against a published worked example (research.md R12.7)
- [ ] T098 Implement `src/tfo_bench/analyze.py`: the generic `runs.csv` → `CellStats`,
  `PairwiseTest`, `SuiteRanks` pipeline, refusing to analyse any cell without an admissible audit
  disposition (`AuditPendingError`, gate G5) (depends on T093, T096)

### 2.10 Pre-registration, tuning freeze, throughput pilot (gates G3, G4)

- [ ] T099 Author `config/protocol.toml` with the full pre-registration content: budgets per suite
  (CEC-2017 10,000·D; CEC-2022 200,000 at D = 10 and 1,000,000 at D = 20; engineering 10,000·D),
  master seeds, the 9-algorithm roster, the statistics plan of research.md R12, the ND rule, audit
  tolerances, the compute envelope, and hypotheses H1–H5 verbatim from spec.md's Assumptions
- [ ] T100 [P] Implement `scripts/tune.py`: the coordinate-wise tuning procedure of research.md R13
  — provisional defaults, the exploratory Stage-A ablation on the tuning set, "TFO-static is tuned
  first" for the CONTROL vector, the remaining three state vectors tuned with shared parameters
  fixed, measurement of CA's overhead ratio ω, writing `config/tfo_frozen.toml` (depends on T081,
  T094)
- [ ] T101 Tag `prereg-v1` on `config/protocol.toml` and `tfo-frozen-v1` on `config/tfo_frozen.toml`,
  and wire the runner's hash guard so a non-smoke test-suite job refuses to run when
  `TFOConfig.config_hash` differs from the tagged file (`ConfigNotFrozenError`) (depends on T089,
  T099, T100)
- [ ] T102 [P] Implement `scripts/pilot.py`: the throughput pilot measuring per-evaluation cost
  (objective plus algorithm overhead) for every roster algorithm on the tuning set, projecting total
  core-hours, and applying the pre-committed {1/2, 1/4} reduction only if the projection exceeds the
  declared compute envelope (research.md R5)
- [ ] T103 [P] Integration test `tests/integration/test_config_freeze_guard.py`:
  `ConfigNotFrozenError` is raised for any non-smoke CEC-2017/CEC-2022/engineering job before both
  tags exist, or when the config hash mismatches

### 2.11 Switchability, smoke pipeline, reproducibility

- [ ] T104 Integration test `tests/integration/test_switchability.py` (gate G2): for each of the 18
  switchable mechanisms, a short tuning-function run with that mechanism off shows "zero evaluations
  under the mechanism's tag", the documented neutral path executed, and ledger equality; for
  TFO-static, the tactical trace is a single `CONTROL` segment matching TFO's counter-attack/set-piece
  schedules under the same seed (depends on T061, T063)
- [ ] T105 Integration test `tests/integration/test_smoke_pipeline.py`: an end-to-end run on one
  tuning function produces schema-valid `runs.csv`/`curves.csv`/`mechanism_evals.csv`/
  `tactical_trace.csv.gz` and passes `validate_results.py` (depends on T087, T088, T089)
- [ ] T106 [P] Integration test `tests/integration/test_reproducibility.py` (contract C2): two runs
  with the same `(view, budget, seed)` give bit-identical ledger outputs on the reference
  environment, with `NPY_DISABLE_CPU_FEATURES` fixed (research.md R20)
- [ ] T107 [P] Implement `scripts/compare_runs.py`: reports two result directories as bit-identical
  in `runs.csv` and `curves.csv`, ignoring timing columns
- [ ] T108 [P] Implement `scripts/run_suite.py`: the thin CLI shared by every suite run —
  `--smoke`, `--part i/n`, `--suite`, `--functions`, `--algorithms`, `--runs`, `--out` — enumerating
  `ExperimentJob`s through `runner.py` (depends on T089)

**Checkpoint**: TFO runs end to end; all 19 mechanisms are independently switchable and unit-tested;
all 9 roster algorithms are budget-conformant under one contract; the audit pipeline gates analysis;
gates G1–G6 are mechanically enforced. User-story implementation can now begin.

---

## Phase 3: User Story 1 - A reviewer audits the metaphor (Priority: P1) 🎯 MVP

**Goal**: hand a reviewer one operator-family table (all 19 mechanisms, family, citation), a
metaphor-free algorithm description, and the CA overlap audit, so the "metaphor exposed" critique is
answered before any experiment is run.

**Independent Test**: give only the mechanism map and the metaphor-free description to a reader
unfamiliar with football; they can state each mechanism's operator family and canonical source, and
re-implement the algorithm without any football term.

- [ ] T109 [P] [US1] Implement `scripts/make_mechanism_table.py`: renders the operator-family table
  (all 19 mechanisms, family, canonical citation) directly from `src/tfo/registry.py`, so the
  manuscript table cannot drift from the code (FR-042, SC-001) (depends on T014)
- [ ] T110 [P] [US1] Unit test `tests/unit/test_mechanism_table_complete.py`: "100% of TFO's
  mechanisms (19 of 19...) appear in the operator-family table with a named family and at least one
  canonical citation; zero mechanisms are unmapped" (SC-001)
- [ ] T111 [P] [US1] Implement `scripts/audit_overlap.py`: computes the CA overlap audit from
  `registry.py` against mechanism-map.md's overlap table, reporting the count of TFO mechanisms in
  families absent from CA — "At least half of TFO's mechanisms belong to operator families absent
  from CA's operator-family table (11 of 19 at design time)" (SC-002) — with a `--post-ablation` mode
  to re-report the ratio after pruning
- [ ] T112 [P] [US1] Contract test `tests/contract/test_identifier_allowlist.py` (Principle VI,
  FR-043, SC-009): every mechanism, variant and algorithm identifier in code and in results files is
  on the registry's closed allowlist, and none matches a real person's name, nickname, club, or
  competition trademark
- [ ] T113 [P] [US1] Write `docs/metaphor_free_description.md`: expands mechanism-interface.md §1–§2
  into a complete equation/pseudocode specification with zero football vocabulary, from which the
  algorithm can be re-implemented (FR-042, acceptance scenario 2)
- [ ] T114 [P] [US1] Implement `scripts/check_metaphor_free.py` and unit test
  `tests/unit/test_metaphor_free.py`: scans `docs/metaphor_free_description.md` against a
  football-word denylist (ball, pitch, keeper, striker, pass, formation, press, offside,
  substitution, fixture, …) and fails if any term appears (depends on T113)
- [ ] T115 [P] [US1] Unit test `tests/unit/test_homage_sentence_cap.py`: for each of the 8 archetypes
  in mechanism-map.md's "Archetype inspiration" section, "each homage appears as at most one
  explanatory sentence", and no real person's name appears in it (acceptance scenario 4)
- [ ] T116 [US1] Assemble `docs/reviewer_audit_packet.md` bundling the rendered operator-family table
  (T109), the metaphor-free description (T113), and the overlap audit (T111) into the single artefact
  the Independent Test hands to an unfamiliar reader (depends on T109, T111, T113)

**Checkpoint**: US1's reviewer audit packet exists and is independently testable without any
benchmark run.

---

## Phase 4: User Story 2 - A researcher positions TFO against strong baselines (Priority: P2)

**Goal**: run the full roster (TFO, TFO-static, GWO, PSO, GA, WOA, L-SHADE, CMA-ES, CA) on the full
usable CEC-2017 suite, the validated CEC-2022 cells, and the 7 engineering problems, with Friedman
ranks and pairwise Wilcoxon/Holm win/tie/loss records, and every loss shown with the same prominence
as every win.

**Independent Test**: from the committed per-run results alone, recompute the Friedman mean ranks and
the per-function win/tie/loss records for every pair of algorithms on each suite, and confirm they
match the manuscript's tables.

- [ ] T117 [US2] Run the CEC-2017 main experiment:
  `python scripts/run_suite.py --suite cec2017 --algorithms ALL` for all 29 functions (F1, F3–F30)
  at D = 30, "at least 30 independent seeded runs per algorithm per cell" (FR-030), writing to
  `results/raw/main/cec2017/`
- [ ] T118 [US2] Run the CEC-2022 main experiment:
  `python scripts/run_suite.py --suite cec2022 --algorithms ALL` for F1–F12 at D ∈ {10, 20} (24
  cells run), restricted at analysis time to audit-validated cells (FR-029), writing to
  `results/raw/main/cec2022/`
- [ ] T119 [US2] Run the engineering main experiment:
  `python scripts/run_suite.py --suite engineering --algorithms ALL` for the 7 problems under the
  shared static-penalty formulation (FR-031), writing to `results/raw/main/engineering/`
- [ ] T120 [US2] Run `python scripts/analyze.py --in results/raw/main --out results/derived/main` to
  produce `cell_stats.csv`, `pairwise.csv` (C(9, 2) = 36 pairs per cell), and `ranks.csv` for all
  three main suites (depends on T117, T118, T119, T098)
- [ ] T121 [P] [US2] Implement the H1 hypothesis-verdict computation in `src/tfo_bench/stats.py`:
  SC-011 "TFO attains the best mean Friedman rank among the classical/moderate group" on CEC-2017,
  and SC-012 the same on validated CEC-2022 cells and the engineering problems "with at most 2
  significant losses in the 35 engineering comparisons against that group", writing the H1 row of
  `hypotheses.csv` (depends on T120)
- [ ] T122 [US2] Implement `src/tfo_bench/tables.py` (main-roster section): per-suite Friedman-rank
  tables and complete per-function/per-cell/per-problem win/tie/loss tables for all 9 algorithms,
  with "every loss of TFO to any roster algorithm on any validated cell" rendered in a main-text
  table, never an appendix (SC-008, acceptance scenario 4) (depends on T120)
- [ ] T123 [P] [US2] Implement `src/tfo_bench/figures.py` (main-roster section): one convergence-curve
  figure per suite, drawn from `curves.csv`
- [ ] T124 [P] [US2] Unit test `tests/unit/test_main_tables_no_loss_filter.py`: the table generator
  applies no outcome-based filter — every row of `pairwise.csv` for a validated cell appears in the
  rendered table regardless of win, tie, or loss
- [ ] T125 [US2] Write `docs/baseline_footnote.md` and wire it into the first results table of
  `tables.py`: "CA's numbers in this paper are this paper's re-runs, not quotations from the CA
  paper", and the CMA-ES (IPOP) versus the sibling's plain-CMA-ES distinction (research.md R8)
  (depends on T122)
- [ ] T126 [US2] Integration test `tests/integration/test_recompute_from_raw.py`: recomputing
  Friedman ranks and per-function win/tie/loss records directly from the committed `runs.csv` files
  reproduces `ranks.csv` and `pairwise.csv` exactly, matching the US2 Independent Test (depends on
  T120)

**Checkpoint**: the full standing comparison exists, with every loss visible and independently
recomputable from raw results.

---

## Phase 5: User Story 3 - A methods researcher attributes performance to mechanisms (Priority: P3)

**Goal**: run the single-mechanism-off variants, the group-level ablations, and TFO-static on the
6-problem ablation set, and validate the formation-topology prediction (H3), so mechanisms can be
kept, pruned, or justified on measured evidence.

**Independent Test**: run the ablation variants and TFO-static on the ablation problem set and check
whether the reported error ratios and significance counts identify which mechanisms are load-bearing.

- [ ] T127 [US3] Run the two-stage ablation, Stage A (exploratory):
  `python scripts/run_ablation.py --stage A` on the tuning set, informing pruning before the freeze
  (research.md R14) (depends on T100)
- [ ] T128 [US3] Implement `scripts/run_ablation.py` (Stage B, confirmatory): enumerate and run the
  26 new variants — "18 single-off variants: the 8 archetypes and 10 switchable tactics", `G-topology`
  (formation and rotation off), and 7 `homog:<archetype>` squads — on the 6 problems (CEC-2017 F1,
  F5, F14, F23 at D = 30; WeldedBeam; PressureVessel), 30 CRN runs each, reusing TFO's and
  TFO-static's main-run records for the same cells/budgets/seeds (FR-034, research.md R14) (depends
  on T101, T081)
- [ ] T129 [P] [US3] Implement the `AblationRatio` computation in `src/tfo_bench/stats.py`: mean-error
  ratio against `full`, Holm-corrected significance, per data-model.md B7, writing
  `ablation_ratios.csv` (depends on T128)
- [ ] T130 [P] [US3] Unit test `tests/unit/test_ablation_disposition.py` (gate G7, SC-006): a
  mechanism whose "mean error ratio lies within [0.95, 1.05] with at most one significant problem"
  receives a remove-or-justify disposition, and is never silently kept
- [ ] T131 [US3] Implement the G7 guard in `src/tfo_bench/tables.py`: table generation "refuses to
  write mechanism-level tables unless all single-off variants, all group variants, TFO-static and
  full TFO exist for all 6 problems × 30 runs" (depends on T129)
- [ ] T132 [US3] Implement `src/tfo_bench/tables.py` (ablation section): the mechanism-level
  contribution table (error ratios, significance counts), the group-level table (TFO-static,
  G-topology, best homogeneous squad), the remove-or-justify disposition table, and a re-report of
  SC-002's family ratio after pruning via `scripts/audit_overlap.py --post-ablation` (depends on
  T130, T131)
- [ ] T133 [US3] Implement `scripts/run_takeover.py` (H3, FR-035): selection-only dynamics on
  compact/balanced/stretched formations, 100 paired runs per shape paired by the best individual's
  starting slot, measuring takeover time and the diversity-decay curve (depends on T048)
- [ ] T134 [P] [US3] Implement the `TakeoverResult` statistic and its one-sided pre-registered test in
  `src/tfo_bench/stats.py`: a signed-rank test in the direction "compact < stretched", writing the H3
  row (SC-014) into `hypotheses.csv` (depends on T133)
- [ ] T135 [P] [US3] Unit test `tests/unit/test_takeover_direction.py`: compact formations show a
  shorter measured takeover time than stretched formations under selection-only dynamics

**Checkpoint**: US3 identifies which mechanisms are load-bearing, with a disposition for every
near-zero mechanism, and H3 confirmed or refuted.

---

## Phase 6: User Story 4 - An independent group reproduces and trusts the numbers (Priority: P4)

**Goal**: let a third party regenerate every table and figure from committed seeds and code, confirm
no algorithm had a budget advantage, and confirm no result rests on a defective benchmark function.

**Independent Test**: follow the documented reproduction sequence on a clean machine and compare the
regenerated tables with the committed ones; inspect the audit records for each benchmark cell.

- [ ] T136 [US4] Implement `scripts/validate_presentation.py` (gate G8): re-checks every rendered
  table cell and in-text number against the committed source CSVs, and additionally checks that
  "every loss appears in the main-text tables" (depends on T122, T132)
- [ ] T137 [P] [US4] Integration test `tests/integration/test_presentation_validation.py`: a
  deliberately mismatched table cell is detected by `validate_presentation.py` with a nonzero exit
  code
- [ ] T138 [US4] Implement `scripts/reproduce.sh` (or a documented `make reproduce` target) encoding
  quickstart.md's "Full reproduction sequence" end to end on a clean checkout: audit preflight → tune
  → pilot → tag → run_suite → audit Stage B → analyze → ablation/sensitivity/takeover/epsilon/timing
  → tables/figures → validate_presentation
- [ ] T139 [P] [US4] Implement `scripts/make_budget_report.py`: from `mechanism_evals.csv` and
  `runs.csv`, computes TFO's per-mechanism evaluation allocation "as percentages of the budget,
  averaged over runs, with the standard deviation" (SC-003), and confirms "no algorithm exceeds the
  shared budget in any run"
- [ ] T140 [P] [US4] Unit test `tests/unit/test_budget_report_no_overrun.py`: across every row of
  every main-suite `runs.csv`, `evals_used ≤ budget` holds and, for the TFO family,
  `evals_internal == evals_used` (SC-003)
- [ ] T141 [US4] Implement `scripts/make_audit_report.py`: renders `results/audit/cell_audit.csv` and
  the retained `pre_audit/` numbers into a reviewer-readable table listing, for every cell used in any
  analysis, its disposition and, for restored/excluded cells, its cross-validation evidence and
  pre-audit numbers (SC-004) (depends on T093)
- [ ] T142 [US4] Write `docs/reproduction_guide.md`: the documented reproduction sequence a third
  party follows on a clean machine, cross-referenced to quickstart.md, satisfying the US4 Independent
  Test verbatim
- [ ] T143 [P] [US4] Integration test `tests/integration/test_clean_checkout_smoke.py`: following
  `docs/reproduction_guide.md`'s smoke-scope steps on a freshly cloned checkout reproduces
  `results/_smoke` outputs bit-identically

**Checkpoint**: a third party can regenerate and audit every reported number without trusting the
authors.

---

## Phase 7: User Story 5 - A practitioner adopts TFO with default settings (Priority: P5)

**Goal**: name which settings matter and which are safe to leave at their defaults, and report the
offside ε-line's effect separately from the shared penalty formulation.

**Independent Test**: read the parameter-sensitivity results and check that they name the settings
that matter, the settings that can be left at their defaults, and the direction of any headroom.

- [ ] T144 [US5] Implement `scripts/run_sensitivity.py` (FR-036, research.md R15): one-at-a-time
  low/high sweep of the 12 parameter groups (archetype fractions; ρ; τ; pass-chain length L;
  set-piece period c; VAR period v; substitution window W; substitution cap; fatigue drain and
  recovery rates; the manager's diversity thresholds; the drought threshold; dwell/hysteresis) on the
  6 ablation problems, 30 CRN runs each (depends on T101, T081)
- [ ] T145 [P] [US5] Implement the `SensitivityClass` computation in `src/tfo_bench/stats.py`:
  classify each group "*sensitive* if its mean error ratio falls outside [0.95, 1.05] **and**
  Holm-corrected signed-rank tests are significant on at least 2 of the 6 problems", otherwise
  *robust*, writing `sensitivity.csv` (SC-007) (depends on T144)
- [ ] T146 [P] [US5] Unit test `tests/unit/test_sensitivity_classification_rule.py`: the
  sensitive/robust classification is applied mechanically per the rule above, and covers "the
  manager's thresholds, which the sibling project did not sweep" (SC-007)
- [ ] T147 [US5] Extend `scripts/run_sensitivity.py` with the 3×3 interaction grid for the two most
  sensitive groups (FR-036, SHOULD) (depends on T145)
- [ ] T148 [US5] Implement `src/tfo_bench/tables.py` (sensitivity section): the parameter-sensitivity
  table naming every group's classification, ratio and significance evidence per problem (SC-007,
  acceptance scenario 1) (depends on T145)
- [ ] T149 [US5] Implement `scripts/run_epsilon.py` (FR-031, acceptance scenario 2): runs TFO and
  TFO-static with the offside ε-line enabled on the 7 engineering problems through the `constraints`
  capability, reporting the effect "relative to the shared penalty formulation... in a separate,
  clearly labelled experiment" (depends on T054, T081)
- [ ] T150 [P] [US5] Unit test `tests/unit/test_epsilon_experiment_isolated.py`: ε-line results never
  enter the US2 main roster tables, and `view.constraints` is reachable only for
  `experiment == "epsilon"` jobs
- [ ] T151 [US5] Write `docs/adoption_guide.md`: names the settings that matter and those safe to
  leave at their defaults, with the direction of any headroom, directly answering the US5 Independent
  Test (depends on T148, T149)

**Checkpoint**: a practitioner has a validated default configuration and a named list of settings
that matter.

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: measured cost, final audit and presentation passes, and manuscript housekeeping that
spans more than one story.

- [ ] T152 [P] Implement `scripts/run_timing.py` (FR-037, research.md R19): every roster algorithm on
  the 6 ablation problems, 10 repetitions each, single-threaded and pinned to one core with
  `taskset`, `time.perf_counter_ns`, reporting total/objective/overhead time; the manifest records CPU
  model and flags
- [ ] T153 [P] Unit test `tests/unit/test_timing_overhead_target.py`: TFO's median measured overhead
  (research.md R22) is reported at D = 30, stated as a measured engineering figure, never an
  estimate, per the constitution's Principle IV ban on estimated overheads
- [ ] T154 [P] Run `scripts/audit_preflight.py` and the full Stage-B audit (below-optimum check plus
  cross-validation) across all suites after the main/ablation/sensitivity runs complete, updating
  `results/audit/cell_audit.csv` to its final state
- [ ] T155 [P] Implement any remaining cross-cutting tables/figures in `src/tfo_bench/tables.py` /
  `figures.py` not covered by a specific story: the environment-manifest summary table and the
  compute-envelope table from `scripts/pilot.py`
- [ ] T156 Run `scripts/validate_presentation.py` end to end over the complete committed results tree
  and fix any reported mismatch before proceeding
- [ ] T157 [P] Update `related-work.md`: read SLOCA's full text and resolve the open item "SLOCA's
  full text MUST still be read before submission" from spec.md's Assumptions and plan.md's Open items
- [ ] T158 [P] Write `docs/submission_checklist.md`: for each of the constitution's 6 principles and
  8 gates, record the evidence file that satisfies it, per the constitution's Governance section
- [ ] T159 [P] Run `pytest -q` across all four tiers (unit, contract, integration, golden) and confirm
  100% pass before tagging a release candidate
- [ ] T160 Run the full quickstart.md validation sequence (§0–§11) end to end on a clean environment
  and record the outcome in `docs/reproduction_guide.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: no dependencies; can start immediately.
- **Foundational (Phase 2)**: depends on Setup (T006's vendored file is needed by T082; T008's config
  placeholders are populated by T099–T100). **Blocks all 5 user stories.**
- **User Stories (Phases 3–7)**: all depend on Foundational (Phase 2) completion, specifically on the
  engine (T061), the public API (T063), the audit pipeline (T093, T098), and the pre-registration/
  freeze gates (T101) for any test-suite run. Within Foundational, the mechanism modules (2.2, 2.3)
  must exist before the engine (2.4); the ledger (2.5) and problems (2.6) must exist before the
  adapters and their contract test (2.7); the schema/runner (2.8) must exist before the audit's own
  I/O (2.9) and before the freeze/pilot gates (2.10); the freeze (T101) must exist before any main,
  ablation, sensitivity, takeover or epsilon run in Phases 4–7.
- **US1 (P3, Phase 3)**: needs only the registry (T014) and the mechanism map/config docs; it does not
  need any benchmark run, and can proceed the moment Foundational's 2.1–2.4 sub-sections land.
- **US2 (Phase 4)**: needs the full roster of adapters (2.7), the runner (2.8), the audit (2.9), and
  the freeze (2.10).
- **US3 (Phase 5)**: needs the freeze (T101) and the TFO adapter's variant builders (T081); reuses
  US2's main-run records for `full` and `static` at the same cells (no hard dependency on Phase 4's
  completion, only on the same records existing before T128's comparison).
- **US4 (Phase 6)**: needs US2's and US3's table-generation code (T122, T132) to validate against, so
  it is naturally sequenced after Phases 4–5, though its own scripts (`validate_presentation.py`,
  `make_budget_report.py`) could be written earlier and pointed at smoke data.
- **US5 (Phase 7)**: needs the freeze (T101) and the TFO adapter (T081); independent of US2/US3/US4's
  results, so it can run in parallel with them once Foundational is done.
- **Polish (Phase 8)**: depends on every story phase whose output it validates or times (T152, T156
  in particular need the main/ablation/sensitivity results to exist).

### User Story Dependencies

- **US1 (P1)**: no dependency on other stories. The most independent of the five — almost pure
  documentation and static checks over the registry.
- **US2 (P2)**: no dependency on US1, US3, US4 or US5's outputs, only on Foundational.
- **US3 (P3)**: reuses US2's main-run records for `full`/`static` (same cells, budgets, seeds) rather
  than depending on US2's *code*; if US2 has not yet run those cells, US3 must run them itself for the
  6 ablation problems.
- **US4 (P4)**: reads US2's and US3's table-generation code and output to validate them; logically
  follows both, though its own machinery is independently buildable.
- **US5 (P5)**: no dependency on US2/US3/US4; only on Foundational.

### Within Each User Story

- Tests are written and expected to fail before their implementation task.
- Experiment-running tasks precede the statistics tasks that consume their output.
- Statistics tasks precede the table/figure tasks that render them.
- Story complete before moving to the next priority, when working sequentially.

### Parallel Opportunities

- All Setup tasks marked [P] (T002–T005, T007–T008) can run in parallel once T001 exists.
- Within each Foundational sub-section, all mechanism/problem/adapter test tasks marked [P] can run
  in parallel with each other, and likewise for the paired implementation tasks (different files).
- Once Foundational (Phase 2) is complete, US1 and US5 can start immediately in parallel with US2,
  since neither depends on the main-suite results. US3 can start as soon as the freeze (T101) lands.
- Within US2, T121 (H1 stats) and T123 (figures) and T124 (test) can run in parallel once T120 is
  done, since they touch different files.
- Within US3, T129 (ablation stats) can run in parallel with T133 (takeover script), since they touch
  different files and address independent acceptance scenarios (mechanism attribution vs. H3).

---

## Parallel Example: Foundational, player archetypes (2.2)

```bash
# Launch all 8 archetype unit tests together (different files, no cross-dependency):
Task: "Unit test tests/unit/test_sweeper_keeper.py"
Task: "Unit test tests/unit/test_zonal_centre_back.py"
Task: "Unit test tests/unit/test_overlapping_wing_back.py"
Task: "Unit test tests/unit/test_deep_lying_playmaker.py"
Task: "Unit test tests/unit/test_box_to_box.py"
Task: "Unit test tests/unit/test_destroyer.py"
Task: "Unit test tests/unit/test_virtuoso.py"
Task: "Unit test tests/unit/test_finisher.py"

# Then launch all 8 archetype implementations together (each makes its own test pass):
Task: "Implement src/tfo/archetypes/sweeper_keeper.py"
Task: "Implement src/tfo/archetypes/zonal_centre_back.py"
Task: "Implement src/tfo/archetypes/overlapping_wing_back.py"
Task: "Implement src/tfo/archetypes/deep_lying_playmaker.py"
Task: "Implement src/tfo/archetypes/box_to_box.py"
Task: "Implement src/tfo/archetypes/destroyer.py"
Task: "Implement src/tfo/archetypes/virtuoso.py"
Task: "Implement src/tfo/archetypes/finisher.py"
```

## Parallel Example: User Story 1

```bash
# Launch US1's independent doc/script/test tasks together once T014 (registry) exists:
Task: "Implement scripts/make_mechanism_table.py"
Task: "Unit test tests/unit/test_mechanism_table_complete.py"
Task: "Implement scripts/audit_overlap.py"
Task: "Contract test tests/contract/test_identifier_allowlist.py"
Task: "Write docs/metaphor_free_description.md"
Task: "Unit test tests/unit/test_homage_sentence_cap.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup.
2. Complete Phase 2: Foundational, at least through 2.1–2.4 (core state, all 19 mechanisms, engine,
   public API) — US1 does not need the harness (2.5–2.11), only the algorithm and its registry.
3. Complete Phase 3: User Story 1.
4. **STOP and VALIDATE**: hand `docs/reviewer_audit_packet.md` to a reader unfamiliar with football
   and check the Independent Test.
5. This is the MVP: the metaphor-exposed critique is answered before a single benchmark run.

### Incremental Delivery

1. Setup + Foundational (all 100 tasks, including the harness) → foundation ready for every story.
2. Add US1 → validate independently → the reviewer audit packet is deliverable on its own.
3. Add US2 → validate independently → the standing comparison against strong baselines is deliverable.
4. Add US3 → validate independently → the mechanism attribution and H3 verdict are deliverable.
5. Add US4 → validate independently → third-party reproduction and integrity trust are deliverable.
6. Add US5 → validate independently → the practitioner adoption guide is deliverable.
7. Phase 8 Polish closes out timing, final audit, presentation validation, and submission checklist.

### Parallel Team Strategy

With multiple contributors, after Foundational is complete:

- One contributor: US1 (documentation and static checks — fastest to close).
- One contributor: US2 (main suite runs — longest wall-clock, start earliest).
- One contributor: US5 (sensitivity and epsilon — independent of US2/US3).
- US3 waits only on the pre-registration freeze (T101), then proceeds in parallel with US2.
- US4 is naturally last, since its Independent Test validates US2's and US3's own output, but its
  scripts (`validate_presentation.py`, `make_budget_report.py`) can be written early against smoke
  data and pointed at the real results once they exist.

---

## Notes

- [P] tasks touch different files and have no dependency on an incomplete task.
- [USn] maps a task to spec.md's user story n for traceability.
- Foundational (Phase 2) is large by design: per the constitution's Operator-Family Grounding and
  Ablation-Justified Complexity principles, all 19 mechanisms need one independently switchable,
  independently testable module each, and every user story depends on the algorithm running
  correctly under the exact, dual-ledger evaluation budget before any story-specific claim can be
  made.
- Quoted text in task descriptions is verbatim from data-model.md, the contracts, or spec.md, per the
  requirement that field- and invariant-level constraints not be left to implementation-time
  discretion.
- Commit after each task or logical group. Stop at any checkpoint to validate a story independently.
- Avoid: vague tasks, same-file conflicts inside a claimed [P] pair, and cross-story dependencies that
  would break a story's independent testability.
