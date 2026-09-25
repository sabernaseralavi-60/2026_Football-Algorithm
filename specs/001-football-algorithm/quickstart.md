# Quickstart: validating the TFO implementation end to end

**Feature**: `001-football-algorithm` | **Plan**: [plan.md](./plan.md)

This is a run guide. Each step names the command to run and what a correct outcome looks like. It
contains no implementation code; the implementation comes from `tasks.md`. Commands assume the
repository root and the layout in plan.md's Project Structure.

> **Protocol guard (gates G3 and G4).** The smoke runs below have three safeguards against
> calibrating on the test suites before the configuration is frozen:
>
> - They write only to the gitignored `results/_smoke/`.
> - When they touch test-suite cells, the budget is capped at 1,000 evaluations with 2 runs.
> - The tuning procedure never reads that directory.
>
> Any non-smoke run on CEC-2017, CEC-2022 or the engineering suite is refused
> (`ConfigNotFrozenError`) until two git tags exist: `prereg-v1` and `tfo-frozen-v1`.

## 0. Prerequisites

- Linux x86-64, with CPython 3.11 and git. A C compiler is needed only for the CEC-2022 reference
  audit (research.md R4).
- An idle machine for the timing scenario (§9).

## 1. Setup

```bash
python3.11 -m venv .venv && source .venv/bin/activate
pip install -r requirements-lock.txt          # exact pins, incl. cec2017-py @ 424a9fa (git)
pip install --no-deps -r requirements-nodeps.txt   # mealpy==3.0.3 (its metadata pins break otherwise)
pip install -e . --no-deps                    # installs the tfo and tfo_bench packages
```

**Expected:**

- `python -c "import tfo, tfo_bench"` succeeds.
- `python -m tfo_bench.manifest` prints the environment fingerprint: the library versions pinned in
  research.md R8, and the CPU flags.

## 2. Mechanism unit tests (User Story 1; G1 and G2 readiness)

```bash
pytest tests/unit -q
```

**Expected:** all tests pass. There is one test module per mechanism in
[contracts/mechanism-interface.md](./contracts/mechanism-interface.md) §2, which is 19 modules,
plus the neutral move, account, clock and manager.

## 3. Switchability and the TFO-static twin (G2)

```bash
pytest tests/integration/test_switchability.py -q
```

**Expected.** For each of the 18 switchable mechanisms, a short run on a tuning function with that
mechanism off shows three things:

- zero evaluations under the mechanism's tag;
- that the neutral path executed;
- ledger equality (internal evaluation count equals external count).

For TFO-static, the tactical trace is a single `CONTROL` segment, and the counter-attack and set-piece
schedules match TFO's under the same seed.

## 4. Budget and adapter contract for all nine roster algorithms (G6)

```bash
pytest tests/contract -q
```

**Expected.** Contracts C1 to C8 in
[optimizer-interface.md](./contracts/optimizer-interface.md) hold for TFO, TFO-static, CA, GA, PSO,
GWO, WOA, L-SHADE and CMA-ES (IPOP). In particular:

- the ledger shows `evals_used == budget` exactly, including for mealpy WOA, whose own cap
  overshoots;
- the SHA-256 of the vendored CA file matches `PROVENANCE.md`;
- `view.constraints` raises `CapabilityError` outside the ε experiment.

## 5. Benchmark preflight audit (G5, stage a)

```bash
python scripts/audit_preflight.py --suite cec2017
python scripts/audit_preflight.py --suite cec2022
python scripts/audit_preflight.py --suite engineering
python scripts/audit_preflight.py --suite tuning
```

**Expected.**

- `results/audit/cell_audit.csv` has one row per cell, with `preflight_pass` filled in.
- CEC-2017 uses official labels F1 and F3 to F30, from cec2017-py.
- Every CEC-2022 cell that fails in opfunu is listed with `disposition=cross_validating`.
- The engineering rows use the sibling's f_ref values.

## 6. Smoke test: TFO against TFO-static on one CEC-2017 function

```bash
python scripts/run_suite.py --smoke --suite cec2017 --functions F05 \
    --algorithms TFO,TFO-static --runs 2 --out results/_smoke
python scripts/validate_results.py results/_smoke
```

**Expected.**

- `runs.csv` has 4 rows, each with `budget = 1000` and `evals_used = 1000`.
- `evals_internal == evals_used` on every row.
- For the same run index, the `seed` is identical in the TFO and TFO-static rows.
- Every `curves.csv` row is non-increasing.
- `mechanism_evals.csv` has 21 tag rows per run, summing to 1,000.
- `tactical_trace.csv.gz` shows exactly one `CONTROL` segment for each TFO-static run.
- `validate_results.py` exits 0.

## 7. Smoke test: full roster, including CA, and the engineering suite

```bash
python scripts/run_suite.py --smoke --suite cec2017 --functions F01 \
    --algorithms ALL --runs 2 --out results/_smoke
python scripts/run_suite.py --smoke --suite engineering --functions WeldedBeam \
    --algorithms ALL --runs 2 --out results/_smoke
python scripts/validate_results.py results/_smoke
```

**Expected.**

- There are 9 algorithms × 2 runs per cell, and every row has `evals_used ≤ budget`.
- The engineering rows have `max_violation` filled in, and `best_x.csv` holds real-coordinate
  vectors inside the published bounds.

## 8. Analysis pipeline on smoke data

```bash
python scripts/analyze.py --in results/_smoke --out results/_smoke/derived
```

**Expected.**

- `pairwise.csv` has C(9, 2) = 36 rows per cell, with `outcome_a` taking values in
  {win, tie, loss}.
- `ranks.csv` is produced.
- The pipeline refuses to analyse a cell without an audit disposition (`AuditPendingError`). To get
  this far, run it after §5, or pass `--allow-unaudited-smoke`, which is honoured only for
  `_smoke`.

## 9. Determinism and timing

```bash
python scripts/run_suite.py --smoke --suite tuning --functions T_sphere_D15 \
    --algorithms TFO --runs 1 --out results/_smoke/a
python scripts/run_suite.py --smoke --suite tuning --functions T_sphere_D15 \
    --algorithms TFO --runs 1 --out results/_smoke/b
python scripts/compare_runs.py results/_smoke/a results/_smoke/b
python scripts/run_timing.py --smoke
```

**Expected.**

- `compare_runs.py` reports the two runs as bit-identical in `runs.csv` and `curves.csv`, ignoring
  the timing columns.
- The timing smoke reports total time, objective time and overhead per algorithm, all measured with
  a monotonic clock.

## 10. Formation takeover smoke (H3 plumbing)

```bash
python scripts/run_takeover.py --smoke
```

**Expected.** For compact, balanced and stretched, the takeover time and a diversity-decay curve are
written. The ratios printed from the formation module are 0.403, 0.300 and 0.206 (research.md R16).

## 11. Protocol guard

```bash
python scripts/run_suite.py --suite cec2017 --algorithms TFO      # no --smoke
```

**Expected.** Until `prereg-v1` and `tfo-frozen-v1` exist and the configuration hash matches, the
run is refused with `ConfigNotFrozenError`.

## Full reproduction sequence (after the freeze; for reference)

1. `audit_preflight.py` for all suites.
2. `tune.py`: stage-A ablation and tuning on the tuning set, then write `tfo_frozen.toml`, then tag.
3. Pilot, which fixes the budgets.
4. Commit `protocol.toml`, then tag `prereg-v1`.
5. `run_suite.py` for each suite.
6. Stage b of the audit, `analyze.py`.
7. `run_ablation.py`, `run_sensitivity.py`, `run_takeover.py`, `run_epsilon.py`, `run_timing.py`.
8. `make_tables.py`, `make_figures.py`.
9. `validate_presentation.py`.

Each step writes a manifest (data-model.md B8).
