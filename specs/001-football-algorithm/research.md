# Phase 0 Research: Total Football Optimizer (TFO)

**Feature**: `001-football-algorithm` | **Date**: 2026-09-25 | **Plan**: [plan.md](./plan.md)

This file settles every item marked NEEDS CLARIFICATION in the plan's Technical Context. Each
decision uses the format Decision / Rationale / Alternatives considered. Three kinds of evidence are
used:

- **Measured.** Probes run during planning in a throwaway virtual environment (Python 3.11.15,
  numpy 2.4.6, scipy 1.17.1, opfunu 1.0.4, mealpy 3.0.3, niapy 2.7.1, cma 4.5.0, cec2017-py at
  commit `424a9fa`). Nothing was installed into the project.
- **Precedent.** The sibling repository `2026_Chess-Algorithm` at commit `96af96b`, read only.
- **Literature.** Canonical sources, cited by author and year.

---

## R1. Language and runtime

- **Decision.** CPython 3.11. The core is NumPy, with the population stored as structure-of-arrays
  (one array per field, see data-model.md).
- **Rationale.**
  - Every dependency this project needs is a Python package: opfunu, cec2017-py, mealpy, niapy and
    pycma.
  - The sibling project's whole pipeline ran on this stack, so the stack is proven for this author
    and this journal target.
  - The full pinned set was installed and run on Python 3.11 during planning.
  - mealpy's declared dependency pins break on Python 3.12 and later. The sibling hit this, and the
    workaround is to install mealpy with `--no-deps`. Staying on 3.11 keeps the sibling's
    already-validated install path.
- **Alternatives considered.**
  - *Julia or C++ for speed.* Rejected. Every baseline would have to be re-implemented, and third-party
    baseline implementations are part of the fairness argument (R8).
  - *Python 3.12 or later.* Rejected for the reference environment only, because of mealpy's
    dependency metadata. The code itself should not depend on the 3.11 version.
  - *Numba JIT for TFO's inner loops.* Deferred. It adds a compiler to the reproducibility surface.
    It is used only if the throughput pilot (R5) shows that TFO's own overhead, not objective
    evaluation, is what drives the compute projection over its limit.

## R2. Code organisation: package layout instead of the sibling's flat scripts

- **Decision.** The code is split into three parts:
  - `src/tfo/`: the algorithm, an installable package that depends only on NumPy.
  - `src/tfo_bench/`: the benchmark harness, covering problems, baseline adapters, ledger, runner,
    audit and statistics.
  - `scripts/`: thin command-line entry points, one per experiment. Their names mirror the sibling's
    (`run_suite.py` corresponds to `cec2017_full_run.py` and the other suite runners,
    `run_ablation.py` to `ablation_study.py`, `validate_presentation.py` to the file of the same
    name).

  A `pyproject.toml` declares both packages.
- **Rationale.**
  - The sibling keeps CA, 12 mechanisms and four baselines in one 1,097-line `algorithms.py`. That
    worked for one function with keyword switches.
  - TFO has 19 mechanisms, and each must be switchable on its own (G2) and testable on its own (User
    Story 1: re-implementable from the description). Each mechanism therefore needs its own named
    unit that traces to one row of mechanism-map.md. A single file cannot give that traceability or
    per-mechanism tests.
  - Separating `tfo` from `tfo_bench` means a practitioner (User Story 5) can adopt TFO without
    installing the benchmark stack.
  - The sibling's proven conventions are kept on purpose:
    - one script per experiment, with the `--smoke` and `--part i/n` flags;
    - flat CSV results;
    - checkpointed single-writer output;
    - a presentation-validation script.
- **Alternatives considered.**
  - *Copy the sibling's flat `src/*.py` layout.* Rejected because of the traceability and testing
    needs above.
  - *One package holding both algorithm and harness.* Rejected because adopters would then have to
    install mealpy, niapy and the other benchmark dependencies.

## R3. CEC-2017 implementation (primary suite and cross-check)

- **Decision.**
  - **Primary: `cec2017-py`** (tilleyd), pinned to git commit
    `424a9fa2757914c3e4cfdd8f59a268b1aeb3197f`. It is not on PyPI.
  - **Cross-check: `opfunu==1.0.4`.**
  - **Last-resort arbiter:** the official C code (Awad et al., 2016), compiled only if the two Python
    ports disagree on a cell.
  - Function labels use the **official numbering**: F1 and F3 to F30, with F2 withdrawn. The docs
    carry a mapping table to opfunu's consecutive numbering, which the sibling used.
- **Rationale.**
  1. *Integrity history.* In opfunu, the sibling found six CEC-2017 labels that failed the optimum
     audit (its F5, F9, F15, F16, F19 and F21). All six passed in cec2017-py and were restored from
     it. cec2017-py is adapted directly from the official C code and data files. Choosing it as the
     primary removes a known source of defects instead of patching around it.
  2. *Numbering.* opfunu renumbers the suite consecutively after the withdrawn F2, so its F*n* is
     official F*(n+1)*. The sibling had to document this pitfall at length. With the official
     numbering, TFO's tables match the CEC report directly.
  3. *Throughput (measured).*
     - cec2017-py is vectorised: it takes an (m, D) array. The official F22 costs about **14 µs per
       evaluation** at D = 30.
     - opfunu evaluates one row at a time, at about **131 µs per evaluation** for the same function.
     - At the official budget (R5), this roughly tenfold difference decides the compute projection.
  4. *Independence.* The audit (Principle V) needs a second, independent implementation. opfunu
     fills that role for all 29 functions. In the sibling it agreed with the official-data
     implementation on 23 of the 29 labels.
- **Alternatives considered.**
  - *opfunu primary, with per-label restoration from cec2017-py as the sibling did.* Rejected. It
    mixes two implementations in one suite and keeps the slower, defect-prone port on the critical
    path.
  - *Official C code as the primary.* Rejected for now. It needs a compiler and a ctypes shim on
    every machine that reproduces the results, and the pure-Python port already derives from it.

## R4. CEC-2022 implementation

- **Decision.**
  - **Primary: `opfunu==1.0.4`**, classes `F12022` to `F122022`, at D ∈ {10, 20}.
  - **Independent reference: the official CEC-2022 C code** (Kumar et al., 2021). It is compiled into
    a small shared library, called through a ctypes shim in `tfo_bench/problems/reference/`, and
    built only for the audit and for restoring cells.
- **Rationale.**
  - No other maintained Python port of CEC-2022 was found. The sibling used opfunu, so the
    "16 validated cells" figure it reported refers to the same code.
  - The sibling **excluded** its six failing CEC-2022 cells without cross-validating them.
    Constitution Principle V and FR-038 require that failing cells first be cross-validated against
    an independent implementation built from official data. The C reference closes that gap.
  - If a cell passes on the reference, it is restored by running it on the reference backend. The
    CEC-2017 restorations in the sibling followed the same pattern.
- **Alternatives considered.**
  - *Excluding failing cells without cross-validation, as the sibling did.* Rejected. It does not
    comply with Principle V.
  - *Official C code as the primary backend (much faster than per-row opfunu).* This is kept as the
    documented fallback, adopted only if the pilot (R5) shows that the CEC-2022 cost at the official
    budget is infeasible. If adopted, opfunu becomes the cross-check.

## R5. Evaluation budgets and the compute envelope

- **Decision.**
  - Budgets are the **official maxima**:
    - CEC-2017: 10,000 × D, which is 300,000 at D = 30.
    - CEC-2022: 200,000 at D = 10 and 1,000,000 at D = 20.
    - Engineering suite: 10,000 × D, which gives 20,000 to 70,000 across the seven problems. There
      is no official figure, so the CEC rule is carried over and declared in the paper.
  - Before any test-suite run, a **throughput pilot** measures per-evaluation cost (objective plus
    algorithm overhead) for every roster algorithm on the tuning set (R13). It then projects the
    programme's total core-hours.
  - If the projection exceeds the compute envelope declared in `config/protocol.toml`, a reduced
    budget applies. Only one reduced multiplier per suite may be used, taken from the pre-committed
    list {1/2, 1/4}. It applies identically to every algorithm and is declared in the paper, as the
    spec's Assumptions require. The reduced budget is then passed to L-SHADE's population-reduction
    schedule and to CMA-ES's restart logic.
  - The final budgets are part of the frozen configuration (gate G3).
- **Rationale.**
  - **Spec discrepancy, resolved (2026-09-25).** The spec's Assumptions used to say "the suite's
    official maximum (10,000 × D evaluations for CEC suites)". That parenthesis held for CEC-2017
    only, and the spec now states each suite's own rule. Both figures were checked against the
    primary PDFs in the organisers' repositories (github.com/P-N-Suganthan):
    - CEC-2017 (`CEC2017-BoundContrained`, "Definitions of CEC2017 benchmark suite final version
      updated.pdf", modified 15 October 2016, §2.1): "MaxFES: 10000*D (Max_FES for 10D = 100000;
      for 30D = 300000; for 50D = 500000; for 100D = 1000000)", with 51 runs per problem.
    - CEC-2022 (`2022-SO-BO`, "CEC2022 TR.pdf", Kumar, Price, Mohamed, Hadi & Suganthan, December
      2021, §2.1): a MaxFES table giving D = 10 → 200,000 and D = 20 → 1,000,000, with 30 runs per
      problem. These are fixed values per dimension, not a multiple of D. Some secondary sources
      misquote them as "2×10⁵×D" and "10⁶×D"; the primary table does not.
  - Order-of-magnitude projection:
    - The main runs total about 6.3 × 10⁹ evaluations: CEC-2017 about 2.35 × 10⁹, CEC-2022 about
      3.9 × 10⁹, engineering negligible.
    - Ablation and sensitivity add about 2.2 × 10⁹ more.
    - At the measured objective costs plus an expected algorithm overhead of 10 to 50 µs per
      evaluation, this comes to roughly 200 to 400 core-hours. CEC-2022 at D = 20 on per-row opfunu
      dominates.
    - That is feasible on one multi-core workstation: about 2 to 4 days on 4 cores, well under a
      day on 16.
    - This projection is a planning figure only. Constitution Principle IV forbids estimates in the
      manuscript, and the pilot replaces it with measurements.
- **Alternatives considered.**
  - *The sibling's 15,000-evaluation budget (pop 30 × 500 iterations).* Rejected. The spec requires
    the official maximum and evaluation matching.
  - *A reduced budget for everything from the start.* Rejected. The spec allows a reduction only
    when compute forces it.

## R6. Search-space normalisation

- **Decision.** Every algorithm searches the unit hypercube [0, 1]^D. A `ProblemView` maps unit
  coordinates to the real box (x = lb + (ub − lb) ⊙ u) before calling the objective. This is the
  sibling's convention.
- **Rationale.**
  - Every CEC box is [−100, 100]^D, which is isotropic, so the map is a uniform affine rescaling and
    does not change the landscape.
  - The engineering boxes are highly anisotropic (for example, 0.05 to 2.0 next to 2 to 15), so
    normalisation gives every algorithm the same well-scaled view.
  - All algorithms receive the same view, which is information parity by construction.
  - TFO's radii (niche radius, pressing radius ρ, transition distance, collision radius) can be
    stated as fractions of the unit box's diagonal √D, independent of the problem.
- **Alternatives considered.** Passing the real bounds to each algorithm. Rejected, because each
  baseline would then need its own step-scale defaults per problem.

## R7. Exact evaluation accounting and hard budget stop

- **Decision.** Evaluations are counted twice, independently.
  1. *External ledger* (`tfo_bench.ledger.CountingObjective`). It wraps the objective for every
     algorithm and is the **sole source of truth** for four things: the final best value, the best
     point, the evaluation count, and the convergence curve. It records the best-so-far at fixed
     checkpoints and the time spent inside objective calls.
     - When a batch would cross the budget, it evaluates only the rows that still fit, records them,
       and then raises `BudgetExhausted`.
     - The algorithm's adapter catches the exception. Results come from the ledger, never from the
       algorithm's own report of its best.
  2. *Internal account* (`tfo.account.EvalAccount`), TFO only. It tags every evaluation with the
     mechanism that requested it, enforces the same budget, and holds the incumbent.
  - For every TFO run, the sum of the internal per-mechanism counts must equal the external count.
    This is asserted and stored as `evals_used` and `evals_internal` (see
    [results-schema](./contracts/results-schema.md)).
- **Rationale (measured).**
  - mealpy's own `max_fe` termination **overshot**: 1,020 actual calls for `max_fe = 1000`, because
    it checks only at epoch boundaries. Library termination criteria therefore cannot guarantee
    SC-003.
  - mealpy and pycma both **propagate** an exception raised inside the objective, at call 501 and
    call 2,009 respectively in the probes. A hard stop by exception therefore works for both.
  - niapy's `Task(max_evals=...)` enforces its own cap, and the ledger counts independently of it.
  - Having two counters turns gate G6 into a per-run automated check.
- **Alternatives considered.**
  - *Trusting each library's termination criterion.* Rejected, because it was measured to
    overshoot.
  - *Returning +inf after the budget is spent instead of raising.* Kept only as a fallback for any
    library found to swallow exceptions. It does not change results, because results come from the
    ledger.

## R8. Baseline implementations

- **Decision.**

| Algorithm | Source | Population | How it maps to the budget |
|---|---|---|---|
| GA, PSO, GWO | Sibling `algorithms.py` (`genetic_algorithm`, `particle_swarm`, `grey_wolf`), **vendored** (R9) | 30 | `iters` derived from the budget and each routine's known evaluation pattern, so that internal schedules (PSO inertia, GWO's *a*) finish exactly at the budget. The ledger stops them exactly. |
| WOA | `mealpy==3.0.3`, `WOA.OriginalWOA` (the sibling's source) | 30 | `epoch = B // 30 − 1`, `termination = {"max_fe": B}`, ledger hard stop |
| L-SHADE | `niapy==2.7.1`, `LpsrSuccessHistoryAdaptiveDifferentialEvolution` (the sibling's source; `pyade` is gone from GitHub) | N_init = 18·D (niapy's default of 540 at D = 30 matches Tanabe & Fukunaga 2014), H = 6, p = 0.11, r_arc = 2.6 | `Task(max_evals=B)`. The linear population reduction is driven by the true budget B. |
| CMA-ES | `cma==4.5.0` (pycma, the reference implementation), used as **IPOP-CMA-ES** (Auger & Hansen 2005) through `cma.fmin2(x0_callable, 0.3, ..., restarts=20, incpopsize=2, parallel_objective=...)` | λ = 4 + ⌊3 ln D⌋ at the start, doubling on each restart | `maxfevals = B`, bounds [0, 1], σ₀ = 0.3, fresh uniform x0 per restart, ledger hard stop |

- **Rationale.**
  - Reusing the sibling's GA, PSO and GWO code keeps the baseline identical across the two papers.
    Readers can then compare CA's and TFO's standings against the same classical algorithms, and
    this code already survived review.
  - WOA, L-SHADE and CMA-ES come from third-party libraries, which answers the objection that the
    authors implemented their own baselines, at least for the strongest rivals.
  - L-SHADE and CMA-ES use their own recommended population rules, as the spec's Assumptions
    require. The sibling instead ran L-SHADE from an initial population of 30.
  - **CMA-ES with restarts (IPOP).** At 200,000 to 1,000,000 evaluations, a single CMA-ES run with
    its stopping criteria disabled (the sibling's setup, which suited 15,000 evaluations) converges
    and then idles away most of the budget. IPOP is how CMA-ES is normally deployed at CEC budgets.
    Principle III requires the strongest representative of each family. The choice works against
    TFO, not for it, since H4 expects TFO to lose. Tables label it "CMA-ES (IPOP)".
  - **Decision confirmed (2026-09-25): keep IPOP-CMA-ES as the only CMA-ES in the roster.**
    - *(a) Standard and well cited.* Auger & Hansen (2005) is verified on Crossref (IEEE CEC 2005,
      vol. 2, pp. 1769–1776, doi:10.1109/CEC.2005.1554902; 610 citing works). pycma implements it
      natively: its `fmin2` documentation says "An IPOP-CMA-ES restart is invoked if
      `restarts > 0`", with `incpopsize=2` as the default population multiplier.
    - *(b) No inconsistency inside this paper.* CA is re-run here from the vendored code (R9) under
      this paper's protocol, so CA and TFO face the same IPOP-CMA-ES at the same budgets and seeds.
      The only thing that changes is cross-paper comparability. The sibling ran plain CMA-ES
      (`sota_algorithms.run_cmaes`: population 30, every stopping criterion disabled, σ₀ = 0.3·range)
      at 15,000 evaluations. CA's published standing against "CMA-ES" therefore cannot be read
      against CA's standing against "CMA-ES (IPOP)" here. The manuscript MUST footnote this at the
      first results table: the variant, the budget and the population rule all differ, and CA's
      numbers in this paper are this paper's re-runs, not quotations from the CA paper.
    - *(c) No test-suite tuning.* Every setting is fixed a priori from pycma's documentation or
      sibling parity, never from test-suite results. λ₀ is pycma's default. `incpopsize=2` is the
      default and Auger & Hansen's factor. σ₀ = 0.3 on the unit box matches the sibling and pycma's
      guidance that σ₀ "should be about 1/4th of the search domain width". Two settings change from
      the earlier draft, both for protocol conformance and not for performance.
      - `restarts=9` becomes `restarts=20`. pycma stops after 1 + `maxrestarts` runs even with
        budget left, which would leave the ledger's 100-point curve (invariant L4) short. Each run
        costs at least one generation of λ₀·2ᵏ evaluations, and λ₀ ≥ 10 at D ≥ 10, so 21 runs need
        more than 2 × 10⁷ evaluations. The cap therefore cannot bind before any budget here. A check
        with pycma 4.5.0 found that the budget, not the cap, already ended every run at the three
        (D, B) pairs on sphere and Rastrigin.
      - `x0` becomes a callable that draws a fresh uniform point per restart, which is the pattern
        pycma's documentation recommends ("to restart from different points (recommended), pass
        `x0` as a callable"). With a fixed array, every restart would begin at the same point.
    - *Adapter pitfall, verified.* With restarts, `fmin2` returns the best of the last run only.
      One test returned f = 2.7 × 10⁴ while the best over all runs was 4.6 × 10⁻¹⁶. Results MUST
      come from the ledger (L5), which already holds.
- **Alternatives considered.**
  - *mealpy's GA, PSO and GWO.* Rejected. They would break baseline identity with the CA paper, and
    mealpy's GA is a different variant.
  - *Plain CMA-ES without restarts.* Rejected as a straw man at these budgets.
  - *Run both plain and IPOP CMA-ES.* Rejected. Plain CMA-ES would be a known-weaker duplicate of
    the same family. It adds nothing to Principle III and would grow every Holm family and the
    compute bill. The footnote above covers the cross-paper link without an extra comparator.
  - *pyade for L-SHADE.* Unavailable. The sibling verified the repository is gone.

## R9. CA as the SHOULD comparator

- **Decision.** Vendor a **verbatim, unmodified copy** of the sibling's `src/algorithms.py` at
  commit `96af96bbb5ef36514ae11a0cc5695d4a6211d9a4` as
  `src/tfo_bench/algorithms/vendor/chess_algorithms_96af96b.py`.
  - Next to it goes a `PROVENANCE.md` giving the source URL, commit SHA, Zenodo DOI
    10.5281/zenodo.22854043, MIT licence notice and SHA-256 of the file.
  - A contract test fails if the file's hash ever changes.
  - The adapter calls `chess_algorithm_v3`, which is the published adaptive CA, at its published
    defaults.
  - CA spends about 12 to 15 % more evaluations than `pop × iters` (its own docstring lists the
    en-passant, windmill, castling and blockade probes). The adapter therefore sets
    `iters = ⌊B / (30 · (1 + ω))⌋`. Here ω is CA's mean overhead ratio, measured on the tuning set
    at each dimension and frozen in `protocol.toml`. The ledger stops CA at exactly B, and any
    unspent remainder is recorded.
- **Rationale.**
  - The two projects are separate git repositories, and the constitution makes the sibling
    read-only.
  - Vendoring is the only option that is self-contained for a third-party reproducer, pinned to the
    exact published code, and requires no change to the sibling.
  - The same file also supplies GA, PSO and GWO (R8), so one pinned copy covers four roster
    algorithms.
  - Calibrating ω keeps CA's schedules from being cut short, which a plain `iters = B / 30` would do.
- **Alternatives considered.**
  - *Adding the sibling's path to `sys.path`.* Rejected. It breaks for anyone without the sibling
    checked out at the same place, and the version is not pinned.
  - *Git submodule.* Rejected. It pulls in the whole paper repository (Quarto sources, submission
    package) for a single file.
  - *Re-implementing CA from its README table.* Rejected. The result would no longer be the
    published CA, and the empirical "not a reskin" test would then compare against an
    approximation.
  - *`pip install git+…`.* Not possible. The sibling is not a package.

## R10. Engineering problems

- **Decision.** Port the sibling's seven problems (`engineering_problems.py` at `96af96b`) into
  `tfo_bench/problems/engineering.py`, refactored so that each problem returns `(cost, G)`: the cost
  and a vector of raw constraint values. The **shared formulation** is the sibling's static penalty,
  unchanged: f = cost + 10⁶ Σ max(0, gᵢ)², with the same bounds, the same rounding in the gear
  train, and the same f_ref values.
  - A golden test proves equivalence. The sibling's module is evaluated once, read-only, on a fixed
    set of random and boundary points, and the values are stored as fixtures. The port must match
    them to 1e-12 relative.
  - Algorithms in the roster receive only the penalised scalar. Raw `G` is available only through a
    capability that is exposed solely in the separately labelled ε-line experiment (FR-031).
  - For every run, the harness computes the true maximum constraint violation of the ledger's best
    point after the run, never during it. Penalty exploitation (a lower penalised value from an
    infeasible point) is therefore visible in the tables.
- **Rationale.**
  - The spec's Assumptions name the sibling's seven problems in its penalty formulation.
  - The refactor to `(cost, G)` is what makes the ε-line experiment possible without a second
    formulation.
  - Recording feasibility after the run follows from the audit logic in R12. Literature f_ref values
    are best-known values, not proven optima, so a run "below f_ref" has to be classified as either a
    genuine improvement or a penalty artefact.
- **Alternatives considered.**
  - *Importing from the sibling.* Rejected for the same reasons as R9.
  - *Vendoring the file verbatim.* Rejected. It exposes only the penalised value, so the ε
    experiment would need a second, divergent formulation.

## R11. Seeds, common random numbers and RNG streams

- **Decision.**
  - Each run's seed is derived as
    `SeedSequence([MASTER_SEED, suite_code, function_id, dim, run]).generate_state(1)[0] & 0x7FFFFFFF`,
    kept nonzero. It is shared by every algorithm and every ablation or sensitivity variant at the
    same (cell, run). This design is known as **common random numbers (CRN)**.
  - `MASTER_SEED` values, one for the test suites and a separate one for the tuning set, are
    committed in `config/protocol.toml` as part of pre-registration (G4).
  - TFO draws its initial population first, as `default_rng(seed).random((30, D))`. That is exactly
    the draw the vendored GA, PSO, GWO and CA make, so these algorithms start from identical
    populations. CA additionally applies its opposition step.
  - Each TFO mechanism draws from its own RNG stream, spawned from `SeedSequence(seed)` at a fixed
    registry index. Switching a mechanism off then does not change the random numbers the other
    mechanisms see.
- **Rationale.**
  - CRN makes pairing by run index a real design feature. It reduces the variance of the paired
    comparisons that FR-032 requires (R12), most strongly for TFO against TFO-static and against
    its ablation variants, which share everything except the switched mechanism.
  - Per-cell seeds avoid the sibling's pattern of one seed per run index across all functions,
    which correlates runs across cells.
  - Committing the seeds before any test run rules out seed shopping.
- **Alternatives considered.**
  - *The sibling's `SEED0 + r`.* Rejected because of the cross-cell correlation.
  - *Independent seeds per algorithm.* Rejected, because it removes the pairing.
  - *One RNG stream shared by all of TFO.* Rejected, because turning off one mechanism would then
    shift every later random draw and add variance to the ablation.

## R12. Statistical analysis plan

- **Decision** (committed to `config/protocol.toml` before any test run).
  1. **Error floor.** error = best_f − f*. Errors below 1e-8 are set to 0, as the CEC-2017 and
     CEC-2022 rules prescribe. The engineering suite has no floor and reports penalised f directly.
  2. **Per-cell pairwise test.** A two-sided Wilcoxon signed-rank test on the 30 final errors
     **paired by run index** (CRN, R11), using `scipy.stats.wilcoxon(zero_method="pratt",
     method="auto")`. If all 30 differences are zero, the outcome is a tie and no test is run.
     - The **Holm** correction (Holm 1979) is applied per cell, over all C(k, 2) pairs of the k
       algorithms in the roster: 36 pairs for 9 algorithms.
     - An outcome is a *win* or *loss* when Holm-adjusted p < 0.05, with its direction given by the
       sign of the median paired difference. Otherwise it is a *tie*.
     - This gives complete win/tie/loss (W/T/L) records for every pair (FR-032, User Story 2).
  3. **Suite level.**
     - Friedman mean ranks over the validated, discriminative cells, blocking by cell, using each
       algorithm's mean error. The Friedman χ² test is reported alongside.
     - Post-hoc: Wilcoxon signed-rank across cells, paired by cell, for each pair of algorithms,
       Holm-corrected. Benavoli et al. (2016) argue against mean-rank post-hoc tests.
  4. **Pre-registered robustness check.** Per-cell Mann–Whitney rank-sum tests (the sibling's
     `ranksums`), Holm-corrected in the same way, reported in the supplement. Any cell where the two
     tests disagree is listed. The signed-rank test is the primary test.
  5. **Non-discriminative rule (FR-039).** A cell is non-discriminative if none of its C(k, 2)
     pairwise tests is significant after Holm correction.
     - Such cells stay in the per-cell W/T/L tables, marked ND.
     - They are excluded from the Friedman ranks, and the ranks with them included are also reported
       in the supplement.
  6. **Audit tolerances (FR-038).**
     - Preflight: |f(x*) − f*| ≤ 1e-6·max(1, |f*|). For composition functions, the function is
       evaluated 1e-6 off the shift point, as the sibling did, to avoid the distance-weight
       singularity.
     - Below-optimum check: the cell fails if any run of any algorithm reaches
       best_f < f* − 1e-6·max(1, |f*|). This is stricter than the sibling's absolute tolerance of
       1.0. A trigger is resolved by cross-validation, never by loosening the tolerance.
  7. **Libraries.** `scipy.stats` (`wilcoxon`, `friedmanchisquare`, `ranksums`). Holm is implemented
     in-house in about ten lines and unit-tested against a published worked example.
- **Rationale.**
  - FR-032 and Constitution Principle III name the Wilcoxon signed-rank test for *paired* multi-run
    data. The sibling actually used the rank-sum test, because its runs were not paired.
  - CRN makes pairing by run index legitimate. It is a genuine blocking factor for algorithms that
    share an initial population, and still a valid test when the pairing carries no information
    (independent pairs under H₀ give symmetric differences).
  - Holm over all pairs within a cell gives one family definition that every pairwise table slices
    consistently. It is more conservative for TFO than a TFO-only family, which is the honest
    direction.
- **Alternatives considered.**
  - *Per-cell rank-sum as the primary test (sibling practice).* Rejected as primary because it
    conflicts with the letter of FR-032. It is kept as the robustness check.
  - *Nemenyi post-hoc via scikit-posthocs.* Rejected. Mean-rank post-hoc tests depend on which other
    algorithms are in the pool (Benavoli et al. 2016).
  - *statsmodels `multipletests`.* Rejected, since it would add a large dependency for a 10-line
    procedure.
  - *A Holm family of TFO against each rival only (8 tests per cell).* Rejected. It is less
    conservative, and the W/T/L tables for non-TFO pairs would then need a different family.

## R13. Tuning set and tuning procedure (FR-040, gate G3)

- **Decision.**
  - **Tuning set.** Seven unconstrained functions that are not basic functions of CEC-2017 or
    CEC-2022: Sphere, Schwefel 1.2, Schwefel 2.22, Alpine N.1, Salomon, Styblinski–Tang and
    Dixon–Price.
    - Each is instantiated with its own random shift in [−80, 80]^D, and every second function also
      gets a random orthogonal rotation. Both come from the tuning master seed.
    - The box is [−100, 100]^D, except Styblinski–Tang, which uses [−5, 5]^D.
    - Dimensions are **D ∈ {15, 40}**. No test suite uses either.
  - Two constrained problems are also included, neither of them among the sibling's seven: CEC-2006
    G04 (Himmelblau's nonlinear problem, 5 variables) and the tubular column design (2 variables).
  - Every tuning function passes the same preflight audit at its known optimum.
  - **Procedure.**
    1. Provisional defaults are grounded in the literature (listed per parameter in data-model.md).
    2. An **exploratory ablation on the tuning set**, the pre-freeze pruning stage (see R14).
    3. **TFO-static is tuned first.** This covers the shared operator parameters and the Control-state
       parameter vector, which is TFO-static's frozen vector.
    4. The manager's other three state vectors and its thresholds are then tuned with those shared
       parameters held fixed.
    5. Each parameter group is tuned by a coordinate-wise search over a pre-declared candidate grid.
       There are at most two sweeps, 15 runs per candidate per tuning problem, and the selection
       criterion is mean Friedman rank across tuning problems. Ties keep the default.
    6. The CA overhead ratio ω (R9) is measured in the same session.
    7. The result is written to `config/tfo_frozen.toml`, committed, and tagged `tfo-frozen-v1`.
    8. The runner refuses any non-smoke test-suite job whose TFO configuration hash differs from the
       tagged file.
- **Rationale.**
  - This follows the spec's definition of a disjoint set of functions and dimensions. It fixes the
    sibling's weakness of checking thresholds on CEC-2017 functions it also reported.
  - Tuning TFO-static first keeps H2 fair. The adaptive layer is then compared against a *tuned*
    static twin, not a straw man.
  - Coordinate-wise search is simple, transparent and easy to audit. Its whole trace is committed
    under `results/raw/tuning/`.
  - Baselines stay at their published defaults. This is a standard asymmetry, and it is reported as
    a threat to validity.
- **Alternatives considered.**
  - *irace (López-Ibáñez et al. 2016).* The gold standard, but it adds an R toolchain to the
    reproducibility surface. It is recorded as the upgrade path if reviewers ask for it.
  - *Optuna TPE.* Rejected. It is less interpretable, and its sampler state is another thing to
    reproduce.
  - *No tuning.* Rejected. The constitution requires the controller thresholds to be calibrated on a
    disjoint set.

## R14. Ablation design (FR-034, FR-035, SC-006, gate G7)

- **Decision.**
  - **Two stages.**
    - *Stage A, exploratory, before the freeze.* One-at-a-time ablation on the tuning set. It
      informs pruning before anything is frozen.
    - *Stage B, confirmatory, after the freeze.* The paper's ablation, run on the six test problems
      below. Its results are reported as they are.
      - A mechanism that Stage B finds negligible (mean error ratio in [0.95, 1.05] with at most one
        significant problem, per SC-006) gets a written *remove or justify* disposition.
      - A removal does **not** silently change the headline algorithm. The pruned variant is
        reported in a clearly labelled post-hoc table, and SC-002's family ratio is reported again.
  - **Variants.** 26 new variants. Full TFO and TFO-static are also in the comparison, but their
    main-run records are reused because they have the same cells, budgets and seeds.
    - 18 single-off variants: the 8 archetypes and 10 switchable tactics.
    - *G-topology*: formation replaced by full connectivity **and** positional rotation off, since
      rotation is defined on the lattice.
    - Seven homogeneous squads, one per outfield archetype. The headline comparison is against the
      best of these, which is the conservative choice.
  - **Problems.** Six problems, at D = 30 for the CEC functions:
    - CEC-2017 F1 (unimodal), F5 (simple multimodal), F14 (hybrid) and F23 (composition), all in
      official numbering. These are the same four functions as the sibling's ablation, labelled
      F1, F4, F13 and F22 in opfunu numbering.
    - Engineering: WeldedBeam and PressureVessel.
  - Each variant gets 30 runs per problem with CRN seeds, so the ratios and tests are paired against
    full TFO's main-run records.
  - **Neutral move.** A disabled archetype falls back to an isotropic Gaussian step,
    y = x + σ·s_i·N(0, I), with greedy acceptance. σ is the global step scale and s_i the agent's
    stamina. This is a (1+1)-ES step (Rechenberg 1973), with no neighbourhood information and no
    extra parameters.
  - **Formation validation (FR-035, H3).** Under selection-only dynamics, each lattice starts with
    one best individual, and each cell takes the best of its von Neumann neighbourhood.
    - Measured quantities: takeover time and the diversity-decay curve.
    - 100 paired runs per shape, paired by the best individual's starting slot.
    - Test: a one-sided signed-rank test in the pre-registered direction (compact < stretched).
- **Rationale.**
  - The constitution requires both ablation-based pruning (Principle II) and no tuning on the test
    suites (Principle III). Pruning on test-suite ablation results would be tuning on the test
    suites. The two-stage design satisfies both (see Complexity Tracking in plan.md).
  - Homogeneous squads have no natural single representative, and choosing the strongest one after
    the fact is conservative against TFO's heterogeneity claim.
  - The neutral move must be the weakest *reasonable* move, not a no-op. A no-op would inflate every
    archetype's apparent contribution.
- **Alternatives considered.**
  - *Test-suite ablation driving pruning (the sibling's practice).* Rejected, because it leaks test
    information into the algorithm.
  - *A single homogeneous variant using a pre-chosen archetype.* Rejected, because the choice would
    be arbitrary.
  - *A no-op neutral move.* Rejected, because it inflates contributions.

## R15. Parameter sensitivity (FR-036, SC-007)

- **Decision.**
  - Twelve parameter groups: archetype fractions; ρ; τ; pass-chain length L; set-piece period c;
    VAR period v; substitution window W; substitution cap; fatigue drain and recovery rates; the
    manager's diversity thresholds; the drought threshold; and dwell/hysteresis.
  - Each group is set **low** and **high** at the ends of its pre-declared tuning grid, which is
    about ×0.5 and ×2 for scalar parameters. Everything else stays frozen.
  - The six ablation problems are used, with 30 CRN runs each.
  - Each group is classified *sensitive* if its mean error ratio falls outside [0.95, 1.05] **and**
    Holm-corrected signed-rank tests are significant on at least 2 of the 6 problems. Otherwise it is
    *robust*.
  - The two most sensitive groups get a 3 × 3 interaction grid (SHOULD in FR-036).
- **Rationale.**
  - The sibling's ratio-plus-significance evidence format is reused, and the classification rule is
    fixed before the results are seen.
  - The manager's thresholds are included, as SC-007 requires (the sibling did not sweep them).
- **Alternatives considered.** Global sensitivity analysis (Sobol indices). Rejected, because its
  cost at these budgets is prohibitive. The spec asks for one-at-a-time plus a two-factor check.

## R16. Formation lattice shapes for a squad of 30

- **Decision.**
  - There are 29 outfield agents, and 29 is prime, so every shape uses 30 slots with **one vacant
    slot**. A vacant slot is skipped: an agent next to it has 3 neighbours, not 4.
  - The lattices are toroidal, so the neighbourhood is von Neumann on a torus. Line semantics come
    from the row index (row 0 is the defensive line, the last row the attacking line), and they are
    used only by Box-to-Box donor choice, rotation and the counter-attack's attacking line.
    Rotation swaps rows r and r+1 only, never across the wrap.
  - Shapes:

    | Shape | Lines × lanes | Grid radius | Ratio (neighbourhood/grid radius) |
    |---|---|---|---|
    | compact | 5 × 6 | 2.217 | 0.403 |
    | balanced | 3 × 10 | 2.986 | 0.300 |
    | stretched | 2 × 15 | 4.350 | 0.206 |

    The von Neumann neighbourhood radius is √0.8 = 0.894. Radii follow Alba & Dorronsoro (2005).

  - For other population sizes (for example, in sensitivity runs), a documented rule picks three
    shapes with minimal vacancy that span the same ordering of ratios.
- **Rationale.**
  - Cellular-EA theory, including takeover time on toroidal grids, is stated for tori (Sarma &
    De Jong 1996; Alba & Dorronsoro 2005; Giacobini et al. 2005). Keeping the torus makes the H3
    prediction a direct test of that theory.
  - The ratio is monotone from compact to stretched, which gives a falsifiable ordering.
- **Alternatives considered.** A non-toroidal pitch (fewer neighbours at the edges). Rejected,
  because it changes the radius formula and weakens the connection to the theory being tested.

## R17. Results storage format

- **Decision.**
  - Flat CSV files, as in the sibling. They live under
    `results/raw/<experiment>/<suite>/`:
    - `runs.csv`: one row per run.
    - `curves.csv`: best-so-far error at 100 checkpoints, k·B/100 for k = 1, …, 100, which includes
      all 14 official CEC recording fractions.
    - `mechanism_evals.csv`: long format.
    - `tactical_trace.csv.gz`: run-length-encoded state segments.
    - `best_x.csv`: engineering and ε experiments only.
  - `.csv.gz` files are written with gzip `mtime=0`, so the bytes are the same every time.
  - Only the parent process writes. Workers return records, and the runner appends, checkpoints and
    resumes by the key (algorithm, cell, run).
  - Each experiment writes a JSON manifest containing: git SHA, SHA-256 of the configuration and of
    the lockfile, platform fingerprint, and start and end times.
- **Rationale.**
  - CSV is diffable and readable by any tool, and the downstream table scripts of the sibling
    pattern can be reused.
  - Estimated committed size is under 100 MB in total. Curve files for the main suites are about
    10 MB each, and traces are compressed.
  - Run-length encoding records every iteration's state without loss (FR-027) at a fraction of the
    size of a per-iteration log.
- **Alternatives considered.**
  - *NumPy `.npz` for raw curves (sibling practice).* Rejected. The files are binary and opaque to
    review and diff.
  - *Parquet or HDF5.* Rejected. They add a dependency and are not text.
  - *SQLite.* Rejected. It is opaque in git.

## R18. Testing strategy

- **Decision.** Tests use `pytest`, plus `hypothesis` for property-based checks of invariants (a test
  dependency only). There are four tiers:
  1. **Unit.** One test module per mechanism (19) plus the neutral move, account, clock and manager.
     Each tests the mechanism's contract invariants on a synthetic squad, as listed in
     [mechanism-interface](./contracts/mechanism-interface.md).
  2. **Contract.** For every one of the 9 roster adapters: budget conformance (`evals_used ≤ B`,
     `== B` unless the algorithm stops itself), determinism (same seed gives identical records),
     results inside the box, and the result-schema checks. The same tier covers the
     information-parity test (constraint capability absent from roster views) and the SHA-256 check
     on the vendored CA file.
  3. **Integration.** Switchability (G2): each flag, once off, gives zero evaluations tagged to its
     mechanism and runs the documented neutral path; TFO-static equals manager-off. Also the smoke
     end-to-end run, and the equality of the two ledgers.
  4. **Golden.** The engineering port matches the sibling's values. Tuning-function optima pass
     preflight.
- **Rationale.** User Story 1 requires each mechanism to be re-implementable from its definition,
  and unit tests against the contract invariants are the executable form of that. Property-based
  tests suit invariants such as "the repair always lands inside the box, between the old position
  and the bound" or "no batch ever exceeds the budget".
- **Alternatives considered.** Only the sibling's `sota_smoke_test.py`-style smoke scripts. Rejected
  as insufficient for 19 separately switchable mechanisms.

## R19. Parallelism and wall-clock timing (FR-037)

- **Decision.**
  - Work is parallelised with `concurrent.futures.ProcessPoolExecutor`. One job is one (algorithm,
    cell, run), seeded independently, so results do not depend on the worker count.
    `OMP_NUM_THREADS`, `OPENBLAS_NUM_THREADS` and `MKL_NUM_THREADS` are all set to 1.
  - The **timing study** runs every roster algorithm on the six ablation problems, 10 repetitions
    each.
    - It runs single-threaded on an otherwise idle machine, pinned to one core with `taskset`.
    - It uses `time.perf_counter_ns` (monotonic).
    - It reports total time, time inside the objective (measured by the ledger), and overhead
      (total minus objective).
    - The manifest records CPU model and flags.
- **Rationale.** This meets FR-037 and the constitution's rule of measured, not estimated, cost.
  Separating objective time from overhead makes "TFO's overhead" a measured number.
- **Alternatives considered.** joblib. Rejected, because the standard library is enough.

## R20. Level of reproducibility (Principle IV, SC-005)

- **Decision.** Reproducibility is guaranteed at two levels.
  - **(a) Analysis.** Every derived table value is regenerated identically on any machine from the
    committed raw CSVs, since the analysis is a deterministic pandas/scipy pipeline.
  - **(b) Experiments.** Raw results are regenerated bit-identically from the committed seeds on the
    **reference environment**: the lockfile plus the CPU feature set recorded in the manifest, with
    `NPY_DISABLE_CPU_FEATURES` fixed in the runner to exclude AVX-512 dispatch.
  - On other hardware, re-running the experiments is expected to reproduce the statistical
    conclusions, but not necessarily every last digit.
- **Rationale.**
  - NumPy's SIMD-dispatched transcendental functions can differ in the last ULP between CPU feature
    levels.
  - In a stochastic optimiser, a 1-ULP difference can flip an acceptance decision, after which the
    trajectory diverges.
  - Claiming bit-identical re-execution on arbitrary hardware would be a claim the project cannot
    verify. This limitation is recorded in plan.md's Complexity Tracking.
- **Alternatives considered.**
  - *A Docker image.* It pins software but not the CPU, so the ULP issue remains. It is still
    provided as a convenience.
  - *Forcing scalar code paths everywhere.* This costs large amounts of throughput and is not fully
    controllable from Python.

## R21. Gate G1 gap: citation for positional rotation

- **Finding.** In `mechanism-map.md`, the positional rotation row names its family ("rank-based role
  reassignment restricted to graph neighbours") but gives **no canonical citation**. Gate G1 needs a
  family, a citation and a metaphor-free definition for every mechanism.
- **Proposed resolution.** Cite the dynamic hierarchy of Hierarchical PSO (Janson & Middendorf,
  2005, *IEEE Trans. SMC-B* 35(6)). There, a particle that is better than its parent in the
  hierarchy swaps places with it. That is a local, pairwise, fitness-triggered swap of structural
  positions, which is exactly this mechanism's operator.
- **Status: resolved (2026-09-25).** The citation was added to `mechanism-map.md`.
  - *Reference verified on Crossref:* S. Janson and M. Middendorf, "A hierarchical particle swarm
    optimizer and its adaptive variant", *IEEE Trans. Syst., Man, Cybern. B*, 35(6):1272–1282,
    2005, doi:10.1109/TSMCB.2005.850530 (299 citing works). Its precursor is Janson & Middendorf,
    IEEE CEC 2003, doi:10.1109/CEC.2003.1299745.
  - *Mechanism verified.* The abstract says the particles sit in a dynamic hierarchy that defines
    the neighbourhood, and "depending on the quality of their so-far best-found solution, the
    particles move up or down the hierarchy". The swap rule was confirmed from an independent
    implementation that cites the paper (MAOS, `HierarchicalTopology.java`: when a child's best
    beats its parent's, the two "swap their places within the hierarchy"). The full text was not
    reachable from this environment, so the exact order of the comparisons inside the paper should
    be read before submission.
  - *Fit.* The fit is good on every defining feature: pairwise, fitness-triggered and restricted to
    adjacent nodes of the interaction structure, and the structural position determines influence
    or role. The differences go in the manuscript's stated-difference column, not the family
    column. H-PSO uses a tree, swaps every iteration, and compares personal bests. TFO uses a
    lines × lanes lattice, swaps only at fixture boundaries, and each swap changes the agent's
    archetype.

## R22. Implementation performance goals

- **Decision.** Two engineering targets. These are not claims for the paper.
  - TFO's median algorithm overhead is **≤ 50 µs per evaluation** at D = 30, excluding objective
    time and measured by the timing harness.
  - The whole programme fits the compute envelope declared in `protocol.toml` at the budget chosen
    by the pilot (R5).
- **Rationale.**
  - Structure-of-arrays storage lets whole-squad operations be vectorised.
  - Per-agent moves that evaluate a single point, such as the Virtuoso's polls, are the risk. They
    are the first candidates for batching, where polls are evaluated as one batch and the first
    improvement is taken in order. Batching keeps the evaluation count honest by charging only up to
    the first improvement, and the evaluations after it are never requested.
  - Numba (R1) is the escape hatch.
- **Alternatives considered.** Setting no target. Rejected, because the compute projection in R5
  depends on this number.

---

## References cited in this file

- Alba, E., & Dorronsoro, B. (2005). The exploration/exploitation tradeoff in dynamic cellular
  genetic algorithms. *IEEE TEVC*, 9(2).
- Auger, A., & Hansen, N. (2005). A restart CMA evolution strategy with increasing population
  size. *IEEE CEC 2005*, 2, 1769–1776. doi:10.1109/CEC.2005.1554902 (verified on Crossref,
  2026-09-25).
- Awad, N. H., Ali, M. Z., Liang, J. J., Qu, B. Y., & Suganthan, P. N. (2016). Problem definitions
  and evaluation criteria for the CEC 2017 special session on single objective real-parameter
  numerical optimization. Technical report. (MaxFES verified against the primary PDF, 2026-09-25.
  That PDF, "final version updated", modified 15 Oct 2016, lists the authors in the order Awad, Ali,
  Suganthan, Liang, Qu. Cite the author order of the version actually used.)
- Benavoli, A., Corani, G., & Mangili, F. (2016). Should we really use post-hoc tests based on
  mean-ranks? *JMLR*, 17.
- Demšar, J. (2006). Statistical comparisons of classifiers over multiple data sets. *JMLR*, 7.
- Derrac, J., García, S., Molina, D., & Herrera, F. (2011). A practical tutorial on the use of
  nonparametric statistical tests... *Swarm and Evolutionary Computation*, 1(1).
- Giacobini, M., Tomassini, M., Tettamanzi, A., & Alba, E. (2005). Selection intensity in cellular
  evolutionary algorithms for regular lattices. *IEEE TEVC*, 9(5).
- Holm, S. (1979). A simple sequentially rejective multiple test procedure. *Scand. J. Statist.*, 6.
- Janson, S., & Middendorf, M. (2005). A hierarchical particle swarm optimizer and its adaptive
  variant. *IEEE Trans. SMC-B*, 35(6), 1272–1282. doi:10.1109/TSMCB.2005.850530 (verified on
  Crossref, 2026-09-25).
- Kumar, A., Price, K. V., Mohamed, A. W., Hadi, A. A., & Suganthan, P. N. (2021). Problem
  definitions and evaluation criteria for the CEC 2022 special session and competition on single
  objective bound constrained numerical optimization. Technical report, NTU Singapore, December
  2021. (Authors and MaxFES verified against the primary PDF, 2026-09-25.)
- López-Ibáñez, M., et al. (2016). The irace package: Iterated racing for automatic algorithm
  configuration. *Operations Research Perspectives*, 3.
- Pratt, J. W. (1959). Remarks on zeros and ties in the Wilcoxon signed rank procedures. *JASA*, 54.
- Rechenberg, I. (1973). *Evolutionsstrategie*. Frommann-Holzboog.
- Sarma, J., & De Jong, K. (1996). An analysis of the effects of neighborhood size and shape on
  local selection algorithms. *PPSN IV*.
- Tanabe, R., & Fukunaga, A. S. (2014). Improving the search performance of SHADE using linear
  population size reduction. *IEEE CEC 2014*.

All references above that are not already in `related-work.md` must be verified (for example, via
Crossref) before they are cited in the manuscript.
