# Contract: Results CSV schema

**Purpose.** Every downstream script (statistics, audit, tables, figures, presentation validation)
reads only these files. This contract fixes their locations, their columns, the column types and
the checks run on them. `tfo_bench.records` writes the files, and
`scripts/validate_results.py` checks them. Any schema change bumps `schema_version` and must update
this file in the same commit.

**Conventions.**

- UTF-8, comma-separated, with a header row and `\n` line endings.
- Floats are written with `repr` precision, so they round-trip exactly.
- Missing values are written as an empty field, which pandas reads as NaN.
- `.csv.gz` files are written with gzip `mtime=0`, so their bytes are reproducible.
- Only the parent process writes a given file (research.md R17).

## 1. Layout

```text
results/
├── raw/<experiment>/<suite>/            experiment ∈ {main, ablation, sensitivity, takeover, epsilon,
│   ├── runs.csv                                       timing, tuning, pilot}
│   ├── curves.csv
│   ├── mechanism_evals.csv              (TFO family only)
│   ├── tactical_trace.csv.gz            (TFO family only)
│   └── best_x.csv                       (engineering, epsilon)
├── audit/
│   ├── cell_audit.csv
│   └── pre_audit/<suite>/…              (retained, never deleted — FR-038)
├── derived/<suite>/{cell_stats,pairwise,ranks,ablation_ratios,sensitivity,hypotheses}.csv
├── manifests/<experiment>_<suite>_<utc-timestamp>.json
└── _smoke/                              (gitignored; never read by tuning or analysis)
```

## 2. `runs.csv` (one row per completed run): the primary key is `run_key`

| Column | Type | Rule |
|---|---|---|
| `schema_version` | int | Currently 1 |
| `run_key` | str | `<experiment>/<cell_id>/<algorithm>/<variant_id>/<run>`; unique within the file |
| `experiment` | str | As in the layout above |
| `suite` | str | `cec2017`, `cec2022`, `engineering` or `tuning` |
| `cell_id` | str | data-model.md B2 format |
| `function_id` | str | Official label (for example `F05`), or the engineering problem name |
| `dim` | int | D |
| `algorithm` | str | Roster label (optimizer-interface.md §2) |
| `variant_id` | str | `default` for baselines; data-model.md A15 ids for the TFO family |
| `config_hash` | str | SHA-256 of the algorithm configuration (for TFO, the TFOConfig; for baselines, the adapter parameters) |
| `run` | int | 0 to n_runs − 1 |
| `seed` | int | The common-random-numbers seed (research.md R11); identical across algorithms for the same (cell, run) |
| `budget` | int | The same for every algorithm in the cell |
| `evals_used` | int | From the external ledger; **≤ budget** |
| `evals_internal` | int or empty | TFO family: sum of the account's tags; **== evals_used** |
| `status` | str | `ok` or `self_terminated` |
| `best_f` | float | Raw objective value (penalised for engineering) at the ledger's best |
| `f_star` | float or empty | The claimed optimum (CEC) or f_ref (engineering) |
| `error` | float or empty | `best_f − f_star`, **unfloored**. The 1e-8 floor is applied only in the analysis (research.md R12). |
| `max_violation` | float or empty | Engineering and ε experiments: max(0, max_i g_i(best_x)), computed after the run |
| `wall_time_s` | float | Monotonic |
| `objective_time_s` | float | Time spent inside the objective (ledger) |
| `n_iterations` | int or empty | Iteration-based algorithms |
| `n_state_transitions` | int or empty | TFO |
| `occ_build_up`, `occ_control`, `occ_high_press`, `occ_chasing` | float or empty | TFO: fraction of iterations spent in each state; the four sum to 1 |
| `n_counter_attacks`, `n_substitutions`, `n_var_rollbacks`, `n_set_pieces` | int or empty | TFO family |
| `final_possession_rate` | float or empty | TFO family |

## 3. `curves.csv`

The columns are `run_key`, followed by `c001` to `c100`. `c<k>` is the best-so-far error (or the
penalised f for engineering) after ⌈k·budget/100⌉ evaluations. Each row is non-increasing, and
every `run_key` must also appear in `runs.csv`.

## 4. `mechanism_evals.csv` (long format)

The columns are `run_key`, `tag`, `evals`.

- `tag` takes every value in the 21-member tag enumeration
  ([evaluation-ledger.md](./evaluation-ledger.md) §2), including rows whose value is zero.
- For each `run_key`, Σ `evals` equals `runs.evals_used`.

## 5. `tactical_trace.csv.gz`

The columns are `run_key`, `segment`, `state`, `iter_start`, `iter_end`, `eval_start`, `eval_end`.

- Within each run, segments are contiguous and do not overlap, and together they cover every
  iteration.
- TFO-static runs have exactly one `CONTROL` segment.

## 6. `best_x.csv`

The columns are `run_key`, followed by `x1` to `xD`, in **real** coordinates.

## 7. `audit/cell_audit.csv`

The columns follow data-model.md B4:

- `cell_id`, `implementation`, `f_star`, `f_at_xstar`, `preflight_abs_err`, `preflight_pass`;
- `min_best_f_all_runs`, `below_optimum_pass`;
- `cross_ref_implementation`, `cross_ref_preflight_pass`, `cross_ref_below_optimum_pass`;
- `disposition`, `evidence_path`, `pre_audit_numbers_path`.

## 8. Derived files (regenerable; committed for the paper)

**`cell_stats.csv`** has these columns:

- `cell_id`, `algorithm`, `variant_id`, `n_runs`;
- `best`, `mean`, `std`, `median`, `worst`. These are computed on the error with the 1e-8 floor
  applied.

**`pairwise.csv`** has these columns:

- `cell_id`, `alg_a`, `alg_b`, `n`, `w_stat`;
- `p_raw`, `p_holm`, `median_diff`, `outcome_a` ∈ {win, tie, loss};
- `ranksum_p_holm`, `tests_agree`.

**`ranks.csv`** has these columns:

- `suite`, `dim` (empty for pooled ranks), `algorithm`, `mean_rank`;
- `friedman_chi2`, `friedman_p`, `n_cells`, `nd_cells_excluded`.

**`ablation_ratios.csv`** and **`sensitivity.csv`** have these columns:

- `problem`, `variant_id`, `mean_error_ratio`, `p_holm`, `significant`;
- `class` (sensitivity only).

**`hypotheses.csv`** has these columns:

- `hypothesis` (H1 to H5), `criterion` (SC id), `evidence_file`, `verdict`.

## 9. Validation (`scripts/validate_results.py`; exit code 1 on any failure)

The checks below are enforced at write time where possible, and always before analysis:

1. The columns and types of each file match this contract.
2. `run_key` values are unique.
3. `evals_used ≤ budget` on every row (G6).
4. For the TFO family, `evals_internal == evals_used`, and the per-tag sum matches (G6, SC-003).
5. Within each (cell, run), the seed is identical for every algorithm (research.md R11).
6. Within each cell, the budget is identical for every algorithm (G6).
7. Every curve is non-increasing.
8. Every analysed cell has an admissible audit disposition (G5).
9. The files contain no identifier that is not in the registry allowlist (Principle VI; plan.md).
