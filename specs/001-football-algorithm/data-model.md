# Phase 1 Data Model: Total Football Optimizer (TFO)

**Feature**: `001-football-algorithm` | **Date**: 2026-09-25 | **Plan**: [plan.md](./plan.md)

The entities come from the spec's Key Entities, FR-001 to FR-045, and
[mechanism-map.md](./mechanism-map.md). There are two groups:

- **Algorithm state**, in the `tfo` package. It lives in memory only.
- **Experiment data**, in the `tfo_bench` package. It is persisted as CSV. The column-level contract is
  in [contracts/results-schema.md](./contracts/results-schema.md).

**Notation.**

- n = 30 is the squad size.
- n_out = 29 is the number of outfield agents.
- D is the dimension.
- B is the evaluation budget.
- All positions are in unit-box coordinates, u ∈ [0, 1]^D (research.md R6).
- Distances are Euclidean and are normalised by the box diagonal √D, unless stated otherwise.

Parameter values marked *(prov.)* are provisional planning defaults. The tuning procedure
(research.md R13) replaces them, and they are frozen in `config/tfo_frozen.toml` (gate G3).

---

## Part A: Algorithm state (`src/tfo/`)

### A1. Squad

The population, stored as a **structure of arrays** (one array per field), so that operations over
the whole squad are vectorised. Index 0 is always the Sweeper-Keeper, and indices 1 to n_out are
outfield agents.

| Field | Type / shape | Meaning | Source |
|---|---|---|---|
| `X` | float64 (n, D) | Current positions | FR-001 |
| `f` | float64 (n,) | Current fitness | FR-001 |
| `P`, `f_P` | (n, D), (n,) | Personal bests | spec Key Entities |
| `slot` | int (n,) | Lattice slot index of each outfield agent; −1 for the keeper | FR-001, FR-013 |
| `stamina` | float64 (n,) in [s_min, 1] | Step-scale multiplier | FR-020 |
| `stagnation` | int (n,) | Iterations since `f_P` last improved | FR-019 |
| `mesh` | float64 (n,) in [h_min, h_max] | Virtuoso's mesh size; kept for all agents, since slots rotate | FR-011 |
| `fin_fail`, `fin_last_restart` | int (n,), int (n,) | Finisher's consecutive-failure count and the archive index it last restarted from | FR-012 |
| `X_rev`, `f_rev` | (n, D), (n,) | Snapshot taken at the last VAR review | FR-021 |
| `moved_since_rev` | bool (n,) | Whether a move was accepted since the last review | FR-021 |
| `produced_best_since_rev` | bool (n,) | Whether a move of this agent set a new best-so-far since the last review (aspiration) | FR-021 |

**Validation rules.**

- `X` always lies in [0, 1]^D. The offside repair (A10) guarantees this.
- `f[i] == objective(X[i])` for every i, except that VAR rollback restores a *stored* (X, f) pair at
  no evaluation cost.
- `f_P[i] ≤ f[i]` for every i.
- An agent's archetype is **not** stored on the agent. It is read through `role_sheet[slot[i]]`, so
  rotation changes it (FR-022).

### A2. Archetype and RoleSheet

- **Archetype** is an enumeration with 8 members: `SWEEPER_KEEPER`, `ZONAL_CENTRE_BACK`,
  `OVERLAPPING_WING_BACK`, `DEEP_LYING_PLAYMAKER`, `BOX_TO_BOX`, `DESTROYER`, `VIRTUOSO`,
  `FINISHER`.
  - The identifiers are tactical-function names only (Principle VI; see the allowlist test in plan.md).
  - Each member maps to one module in `tfo/archetypes/` and one row of mechanism-map.md.
- **RoleSheet** maps each slot index to an archetype, for all 30 slots including the vacancy.
  - It is laid out by depth in row-major slot order: zonal centre-backs and wing-backs in the
    lowest slot indices, then the midfield archetypes, then the forward archetypes.
  - It does not change between formations. That keeps the squad's archetype composition fixed when
    the shape changes (FR-013).
- Outfield composition *(prov.)*, n_out = 29: Zonal Centre-Back 4, Overlapping Wing-Back 4,
  Deep-Lying Playmaker 3, Box-to-Box Engine 6, Destroyer 3, Virtuoso 5, Finisher 4. This is the
  sensitivity group "archetype fractions".
- **Homogeneous mode** (ablation, research.md R14): every outfield slot maps to one chosen archetype.

### A3. Formation (lattice shape)

| Field | Meaning |
|---|---|
| `name` | One of `compact`, `balanced`, `stretched` |
| `lines`, `lanes` | Lattice dimensions; `lines × lanes ≥ n_out` |
| `slot_rc` | int (S, 2): (row, column) of each slot in row-major order. Row 0 is the defensive line. |
| `vacant` | bool (S,): slots with no agent |
| `neighbours` | Ragged int table: von Neumann neighbours on the **torus**, with vacant slots skipped |
| `graph_dist` | int (S, S): hop distance on the lattice graph, used by the Deep-Lying Playmaker |
| `ratio` | rad(neighbourhood) ÷ rad(grid) (Alba & Dorronsoro 2005; see the formula below) |

- **Ratio formula.** The radius of a set of n cells is their root-mean-square distance to their
  centroid: rad = √( Σᵢ [(xᵢ − x̄)² + (yᵢ − ȳ)²] / n ). This is the dispersion measure of Sarma &
  De Jong (1996), used as the cellular-EA "ratio" by Alba & Troya (2000) and Alba & Dorronsoro
  (2005, *IEEE TEVC* 9(2):126–142, doi:10.1109/TEVC.2005.843751).
  - The neighbourhood is von Neumann (L5, centre included): rad = √(4/5) = 0.894.
  - The grid radius is taken over **all** lines × lanes cells, vacant slots included, because it
    is a property of the lattice. For a full r × c grid it reduces to
    rad = √(((r² − 1) + (c² − 1)) / 12).
  - Check: the same formula gives the paper's own 400-cell values (20 × 20: 0.110, 10 × 40: 0.075,
    4 × 100: 0.031).
- **Shapes for n = 30** (research.md R16):

  | Shape | Lines × lanes | Grid radius | Ratio |
  |---|---|---|---|
  | compact | 5 × 6 | 2.217 | 0.403 |
  | balanced | 3 × 10 | 2.986 | 0.300 |
  | stretched | 2 × 15 | 4.350 | 0.206 |

  Each shape has exactly one vacancy.
- **Fully connected mode** (the neutral default when the formation is disabled): `neighbours[i]` is
  every other outfield agent, and `graph_dist` is 1 for every pair. The slot rows are kept, so line
  semantics survive.
- **Validation.**
  - Every shape is defined for the configured n.
  - Vacancies = lines × lanes − n_out, with 0 ≤ vacancies < lanes.
  - The ratio is strictly decreasing from compact to balanced to stretched.
  - Changing shape changes `slot_rc` and the neighbour tables only. It never changes `X` or `f`
    (FR-013).

### A4. Ball

| Field | Meaning |
|---|---|
| `x_b`, `f_b` | The ball's position and its evaluated fitness. This is a focal point **distinct from** the incumbent (FR-003). |
| `carrier` | Index of the outfield agent currently holding the ball |
| `passes_tried`, `passes_retained` | Counters for the current window. The EMA of their ratio is the possession rate. |
| `neutral_streak` | Consecutive neutral passes (f unchanged), capped at N_neutral_max *(prov. 5)* |
| `lost_streak` | Consecutive chains that ended in a lost pass. Reaching R_loss *(prov. 3)* triggers a ball reset. |

- **Initialisation.** The ball starts at the best initial outfield agent, with that agent as carrier.
- **Reset.** The ball moves to an archive elite different from its current location. The location
  it leaves becomes a TabuRegister entry.
- **Relocation.** A counter-attack moves the ball to the triggering point and makes that agent the
  carrier.

### A5. KeeperArchive (the Sweeper-Keeper)

| Field | Meaning |
|---|---|
| `A`, `f_A` | Up to K *(prov. 5)* archived points and their fitness values. `A[0]` is always the incumbent best-so-far. |
| `min_sep` | Minimum normalised distance between members *(prov. 0.05)* |

- **Insertion rule.** A point that improves the incumbent always becomes `A[0]`. Any other point
  enters only if:
  - it is better than the worst member, **and**
  - it is at least `min_sep` from every member.

  If it is better than a member but closer than `min_sep` to it, it replaces the nearest such
  member.
- **Invariant.** `f_A[0]` equals the incumbent held by the internal account, so the incumbent is
  never lost (FR-005). This holds even under VAR rollback, because aspiration applies (A12).
- **Disabled.** When the Sweeper-Keeper is switched off, K = 1 (incumbent only), per the spec's
  Section C header.

### A6. TabuRegister

- Holds a FIFO list of up to T_max *(prov. 20)* zone centres with radius r_tabu *(prov. 0.02)*.
- Entries come from two sources: agents substituted out (FR-019) and abandoned ball locations (A4).
- It is read only by the VAR review (FR-021).

### A7. MatchClock

| Field | Meaning |
|---|---|
| `B` | Evaluation budget |
| `n_fixtures` | Number of fixtures *(prov. 20)* |
| `fixture` | Index of the current fixture |
| `iteration` | Iteration counter; one iteration is one engine cycle (see mechanism-interface.md §3) |
| `t` | Budget fraction elapsed, evals_used ÷ B, in [0, 1] |

- **Fixture boundaries are measured in evaluations, not iterations.** Fixture k ends at the first
  iteration end with evals_used ≥ k·B/n_fixtures. The number of evaluations per iteration varies
  with events (bursts, set pieces, substitutions).
- These hooks run at each boundary, in this order:
  1. positional rotation (FR-022);
  2. zonal redraw (FR-006);
  3. stamina recovery (FR-020);
  4. substitution cap reset (FR-019).

### A8. TacticalState and Manager (state machine)

**States.** There are four: `BUILD_UP`, `CONTROL`, `HIGH_PRESS`, `CHASING`. Each state sets one
**StateParameterVector** (FR-024):

| Parameter | BUILD_UP | CONTROL (= TFO-static frozen vector) | HIGH_PRESS | CHASING |
|---|---|---|---|---|
| formation | balanced *(prov.)* | balanced | compact | stretched |
| ρ (pressing radius, normalised) | low | medium | high | 0 (pressing off) |
| τ (retention threshold) | > 0 (neutral drift allowed) | small | 0 | > 0 |
| L (pass-chain length) | medium | medium | long | short |
| archetype rate multipliers | ×1 | ×1 | Virtuoso/Finisher ↑ | Wing-Back jump rate ↑, Deep-Lying Playmaker long-ball rate ↑ |
| substitution cap | base | base | base | base + emergency increment (≤ documented limit) |

All values are provisional. They are tuned under research.md R13, with CONTROL tuned first as
TFO-static.

**Inputs**, read every iteration (FR-023):

- `div`: the EMA of the squad's mean normalised distance to its centroid.
- `poss`: the EMA of the possession rate.
- `drought`: iterations since the last *material* improvement. A material improvement is
  (f_old − f_new) > δ_mat·max(|f_old|, 1e-12), with δ_mat *(prov. 1e-4)*.
- `t`: the budget fraction.

**Transitions.** Guards are checked in priority order. The first guard whose enter-condition holds
decides the target.

1. `drought ≥ G_max` → **CHASING** (the diversification response). It also fires on the
   premature-collapse edge case: `div < d_low` while `t < t_late`.
2. `div < d_low` **and** `t ≥ t_press` **and** `poss ≥ p_high` → **HIGH_PRESS**. HIGH_PRESS is
   never entered before `t_press`, so a collapse early in the run is never read as a cue to
   exploit.
3. `div > d_high` → **BUILD_UP**.
4. Otherwise → **CONTROL**.

**Hysteresis and dwell (FR-025).**

- Every threshold has separate enter and exit values, with exit = enter ± a hysteresis band.
- A state is held for at least `dwell_min` iterations *(prov. 10)*.
- A transition is allowed only if both conditions hold, so the state cannot change on consecutive
  iterations because of noise.
- CHASING exits when a material improvement resets `drought`, subject to the dwell time.

**On a transition:** the new formation is applied (A3 re-lay), and ρ, τ, L, the rate multipliers
and the cap take effect from the next iteration. A new trace segment is opened (A14).

**TFO-static (FR-026).** The manager is disabled. The CONTROL vector is used throughout, and there
is no CHASING response. Event-triggered mechanisms and fixed-schedule mechanisms run exactly as in
TFO.

**Validation.** Tests check two things:

- the dwell and hysteresis properties, under an input sequence that oscillates across a threshold;
- that the CHASING response is present only in TFO.

### A9. Zones (Zonal Centre-Back partition)

- **Zones** are a Latin-hypercube stratification with m strata, where m is the number of Zonal
  Centre-Backs. It is redrawn at every fixture boundary (FR-006).
- For each dimension j there is a random permutation π_j of {0, …, m−1}. Zonal agent k's stratum is
  ∏_j [π_j(k)/m, (π_j(k)+1)/m].
- **Validation.**
  - The m strata are pairwise disjoint.
  - Their projections onto every coordinate tile [0, 1].

### A10. Offside line

- **Repair** (always on for bounds, FR-018). For each coordinate j outside [0, 1]:
  - y_j ← x_j^old + U(0, 1)·(bound_j − x_j^old), where x^old is the agent's previous position and
    bound_j is the bound that was violated.
  - **Disabled:** plain clipping.
- **ε-line.** This exists only in the ε experiment (FR-031).
  - ε(t) = ε₀·(1 − t/T_c)^cp for t < T_c, and 0 afterwards. Default T_c *(prov. 0.8)*
    (Takahama & Sakai 2006).
  - Points are compared by the ε-lexicographic order on (f, v), where v is the violation.
- **Validation.** These are property tests:
  - the repaired point lies in [0, 1]^D;
  - each repaired coordinate lies between x_j^old and the violated bound;
  - points arbitrarily close to a bound remain reachable (the edge case "optimum on or near a
    bound").

### A11. Fatigue

- Stamina drains in proportion to the distance moved: s_i ← max(s_min, s_i − κ·‖Δx‖/√D).
- At each fixture boundary it recovers: s_i ← min(1, s_i + r₀·(1 − t)). Recovery shrinks over the
  run (FR-020).
- Substitutes enter with s = 1.
- **Disabled:** s ≡ 1.

### A12. VAR review

- The review is a deferred audit every v iterations *(prov. 10)* (FR-021). Its inputs are A1's
  `moved_since_rev`, `produced_best_since_rev`, `X_rev`, `f_rev`, the TabuRegister, and, only when
  constraints are exposed, the violation.
- A move fails the review in any of three cases:
  - its endpoint lies within r_tabu of a tabu entry;
  - its endpoint lies within r_coll *(prov. 1e-3)* of another agent (in which case the worse agent's
    move fails);
  - with constraints exposed, the endpoint is truly infeasible although the start was feasible.
- A failing move is rolled back to (`X_rev`, `f_rev`) at **no evaluation cost**, unless
  `produced_best_since_rev` is set (aspiration).
- After the review, the snapshots are refreshed.
- **Disabled:** no rollback.

### A13. EvalAccount (internal ledger)

The internal ledger holds:

- `evals_used`;
- per-mechanism counters `evals_by_tag`;
- the incumbent `(x_best, f_best)`;
- the best-so-far recorded at the 100 checkpoints.

Its tag vocabulary is: `init`; the 19 mechanism tags (8 archetypes and 11 team-level tactics, see
mechanism-interface.md); and `neutral`. The manager, rotation, fatigue and VAR always record zero
evaluations; their tags exist so that zero rows are explicit.

The full behaviour is specified in [contracts/evaluation-ledger.md](./contracts/evaluation-ledger.md).

### A14. RunTrace

- **TacticalSegment** has the fields `(state, iter_start, iter_end, eval_start, eval_end)`. It is a
  run-length encoding of the per-iteration state and is lossless (FR-027).
- **MechanismEvalCount** has the fields `(mechanism_tag, evals)`. The counts sum to `evals_used`.
- **Per-run summaries:** the occupancy fraction of each state, the number of transitions, the number
  of counter-attack events, substitutions, VAR rollbacks and set pieces, and the final possession
  rate.

### A15. TFOConfig and variants

A frozen dataclass, read from TOML. Its `config_hash` is the SHA-256 of the canonical JSON of the
parsed configuration.

| Group | Contents |
|---|---|
| `enable` | 19 booleans, one per mechanism: `manager` plus the 18 switchable mechanisms of FR-034. Default: all true. |
| `homogeneous` | `None`, or an archetype name (R14) |
| `squad` | n, role-sheet composition |
| `states` | The four StateParameterVectors (A8) |
| `manager` | EMA weights, d_low/d_high (enter and exit values), p_high, G_max, δ_mat, t_press, t_late, dwell_min |
| `operators` | Per-mechanism parameters: BLX-α *(prov. 0.5)*, DE F *(prov. 0.5)* and CR *(prov. 0.9)*, jumping rate Jr *(prov. 0.3; Rahnamayan et al. 2008)*, Lévy β *(prov. 1.5; Mantegna 1994)*, Finisher failure limit *(prov. 10)*, mesh bounds and number of polled coordinates k *(prov. 2)*, niche radius *(prov. 0.01)*, pressing cap *(0.5·n_out)*, counter-attack Δ_mat and d_trans, burst length and step decay γ *(prov. 5 and 0.5)*, set-piece period c *(prov. 25)* and step h, W *(prov. 50)*, stamina threshold, substitution cap *(prov. 5 per fixture)*, VAR period v, tabu and collision radii, fatigue κ, r₀ and s_min |
| `constraints` | ε₀, T_c, cp; used only in the ε experiment |

**Named variants** (`variant_id` in the results):

| `variant_id` | Configuration |
|---|---|
| `full` | Everything on |
| `static` | `enable.manager = false` (TFO-static) |
| `off:<mechanism>` | That one mechanism off (18 variants) |
| `G-topology` | Formation and rotation off |
| `homog:<archetype>` | Homogeneous squad (7 variants) |
| `sens:<group>:<low\|high>`, `inter:<g1>=<lvl>,<g2>=<lvl>` | Sensitivity and interaction settings |

**Validation.**

- Test-suite experiments must have `config_hash` equal to that of the file at git tag
  `tfo-frozen-v1` (G3). The runner enforces this.
- Every `off:` variant must name a mechanism that exists in the registry.

---

## Part B: Experiment data (`src/tfo_bench/`, persisted)

### B1. Suite and Problem

- **Suite** is one of `cec2017`, `cec2022`, `engineering`, `tuning`.
- **Problem** has the fields:
  - `problem_id`, `suite`, `name`, `D`;
  - `lb`, `ub` (the real box);
  - `f_star` (the claimed optimum; for engineering, the literature best-known `f_ref`);
  - `x_star` (when known), `implementation` (package and version or commit), and
    `has_constraints`.
- **ProblemView** is what an algorithm receives. It is a vectorised callable u ∈ [0, 1]^{m×D} →
  f ∈ ℝ^m, already wrapped by the external ledger.
  - It exposes a `constraints` capability **only** when the job is an ε-experiment job. This is
    information parity enforced by type (FR-031), and a contract test verifies it.

### B2. BenchmarkCell

- **Key:** `cell_id = <suite>_<Fnn>_D<dd>`, for example `cec2017_F05_D30` or `cec2022_F12_D20`. For
  engineering the form is `engineering_<Name>`.
- **Fields:** `suite`, `function_id` (official numbering for CEC-2017, research.md R3), `D`,
  `budget`, `n_runs` (≥ 30, FR-030), `audit_status`.
- **The test set in scope:**
  - CEC-2017: F1 and F3 to F30 at D = 30, 29 cells.
  - CEC-2022: F1 to F12 at D ∈ {10, 20}, 24 cells run. Only the cells that pass the audit enter the
    analysis.
  - Engineering: 7 cells.

### B3. FunctionPartition (tuning set versus test set)

- **Fields:** `partition` (`tuning` | `test`), `cell_id`, `rationale`.
- **Validation (FR-040).**
  - The tuning and test sets share no (function definition, D) pair. The tuning dimensions {15, 40}
    and the tuning function list are disjoint from the test cells by construction (research.md R13).
  - A test asserts that the intersection is empty.
  - The tuning procedure refuses to load test-partition cells.

### B4. CellAudit

- **Fields:**
  - `cell_id`, `implementation`, `f_star`, `f_at_xstar`, `preflight_abs_err`, `preflight_pass`;
  - `min_best_f_all_runs`, `below_optimum_pass`;
  - `cross_ref_implementation`, `cross_ref_preflight_pass`, `cross_ref_below_optimum_pass`;
  - `disposition`, `evidence_path`, `pre_audit_numbers_path`.
- **State transitions for `disposition`:**

```text
pending --preflight fail--------------------------------> cross_validating
pending --preflight pass--> preflight_ok --runs, no run below f*--> validated
                                          \--any run below f*-----> cross_validating
cross_validating --passes on reference--> restored (re-run on the reference backend)
cross_validating --fails on reference---> excluded (evidence and pre-audit numbers kept)
validated | restored --ND rule (research.md R12) fires--> non_discriminative
```

- **Validation (G5, SC-004).**
  - Analysis refuses any cell whose disposition is not in {validated, restored, non_discriminative}.
    Non-discriminative cells are shown with the marker "ND", ranks excluded.
  - Pre-audit numbers are never deleted.
- **Engineering variant.** The preflight evaluates at the literature best-known x_ref, which must be
  feasible and return f_ref within 1e-4 relative. A run below f_ref is classified by the true
  feasibility of its best point:
  - `improvement` if the point is feasible;
  - `penalty_artifact` if it is not.

  This is reported. It is not grounds for exclusion.

### B5. ExperimentJob

- **Fields:** `experiment`, `suite`, `cell_id`, `algorithm`, `variant_id`, `run`, `seed`, `budget`,
  `config_hash`.
- **Experiments:** `main`, `ablation`, `sensitivity`, `takeover`, `epsilon`, `timing`, `tuning`,
  `pilot`, `smoke`.
- **Validation.**
  - `seed` equals the CRN derivation for (suite, cell, run) (research.md R11). It is identical for
    every algorithm and variant at that key.
  - `budget` equals the protocol budget for the cell, and it is the same for every algorithm (G6).

### B6. RunRecord (one row of `runs.csv`)

- **Contents:** one row per completed job, with the final results taken from the **external ledger**.
  Columns are defined in [contracts/results-schema.md](./contracts/results-schema.md).
- **Companion records**, each linked by `run_key`:
  - `CurveRecord` (100 checkpoints);
  - `MechanismEvalRecord` (TFO family only);
  - `TacticalSegmentRecord` (TFO only; TFO-static records a single CONTROL segment);
  - `BestXRecord` (engineering and ε experiments).
- **Validation (G6, SC-003).**
  - `evals_used ≤ budget` on every row.
  - For the TFO family, `evals_used == evals_internal`.
  - Analysis rejects any file that violates either rule.

### B7. Derived analysis records

- **CellStats:** (cell, algorithm) → best, mean, std, median, worst of the floored error, plus
  `n_runs`.
- **PairwiseTest:** (cell, alg_a, alg_b) → n, the Wilcoxon statistic, p_raw, p_holm, median_diff,
  outcome ∈ {win, tie, loss}, where the outcome is from alg_a's side; also a robustness flag
  comparing against the rank-sum result.
- **SuiteRanks:** (suite, algorithm) → mean Friedman rank, plus χ², p, and the number of cells used.
- **AblationRatio:** (problem, variant) → mean-error ratio against `full`, p_holm, and whether the
  difference is significant.
- **SensitivityClass:** (group) → ratios per problem, significant count, and class ∈
  {sensitive, robust}.
- **TakeoverResult:** (shape, run) → takeover time and the diversity-decay curve.
- **HypothesisVerdict:** (H1 to H5, SC-011 to SC-014) → the criterion, the evidence file and the
  verdict ∈ {confirmed, refuted, partially confirmed}. Every hypothesis must receive a verdict
  (SC-008).

### B8. EnvironmentManifest

Written once per experiment invocation. It holds:

- git SHA and a dirty flag (a dirty working tree is refused for non-smoke runs);
- the SHA-256 of the lockfile and of the configuration;
- the Python, NumPy and SciPy versions, and the versions of the benchmark and baseline libraries;
- CPU model and feature flags, and the `NPY_DISABLE_CPU_FEATURES` value;
- start and end times, the worker count, and the job count.

---

## Relationships

```text
Suite 1─* BenchmarkCell 1─1 CellAudit
BenchmarkCell *─1 FunctionPartition (tuning | test)
BenchmarkCell 1─* ExperimentJob *─1 Algorithm(variant) ; ExperimentJob 1─1 RunRecord
RunRecord 1─1 CurveRecord ; 1─* MechanismEvalRecord ; 1─* TacticalSegmentRecord ; 0..1 BestXRecord
RunRecord *─→ CellStats, PairwiseTest, SuiteRanks, AblationRatio, SensitivityClass → HypothesisVerdict

TFOConfig 1─1 run ─ Squad (n agents) ─ RoleSheet(slot→Archetype) ─ Formation(slot→(row,col), neighbours)
Squad ─ Ball ─ KeeperArchive ─ TabuRegister ─ MatchClock ─ Manager(TacticalState) ─ EvalAccount ─ RunTrace
```
