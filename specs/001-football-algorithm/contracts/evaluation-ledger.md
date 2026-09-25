# Contract: Evaluation ledger (exact budget accounting)

**Purpose.** This contract makes gate G6 and success criterion SC-003 mechanically checkable, for two
reasons:

- No algorithm may exceed the budget. FR-004, FR-030 and FR-037 require this.
- Every internal TFO probe must be charged to the one budget and attributed to the mechanism that
  made it. FR-004 and FR-027 require this.

There are two independent counters: an external ledger that wraps every algorithm, and an internal
account inside TFO only. For TFO, the two must agree.

## 1. External ledger: `tfo_bench.ledger.CountingObjective`

```python
class CountingObjective:
    def __init__(self, problem: Problem, budget: int, *, checkpoints: int = 100): ...
    def __call__(self, U: np.ndarray) -> np.ndarray   # U: (m, D) or (D,) in unit coords
    evals_used: int
    best_f: float; best_u: np.ndarray                 # best-so-far over ALL evaluated rows
    curve: np.ndarray                                 # (100,) best-so-far error at k·budget/100, k = 1..100
    objective_time_ns: int                            # time spent inside problem.evaluate
```

**Semantics.**

1. The ledger accepts a batch of m rows. Let r = budget − evals_used. If r = 0, it raises
   `BudgetExhausted` without evaluating anything.
2. If m ≤ r, it evaluates all rows. Otherwise it evaluates **only the first r rows**, records them,
   and then raises `BudgetExhausted`. This is truncation exactly at the budget (spec edge case
   "budget exhausted mid-routine").
3. Every evaluated row updates `best_f`, `best_u` and `evals_used`. The ledger records a curve point
   at each checkpoint that a row crosses. The curve value is best_f − f* when f* is known, and the
   penalised f otherwise.
4. It asserts that every row lies in [0, 1]^D (contract C3), then maps the row to real coordinates
   before evaluating it.
5. It times the objective with `time.perf_counter_ns` around the `problem.evaluate` call only.
6. It is used for all algorithms, and its values are the ones persisted in `runs.csv` and
   `curves.csv`.

## 2. Internal account: `tfo.account.EvalAccount` (TFO only)

```python
class EvalAccount:
    def evaluate(self, X: np.ndarray, tag: MechanismTag) -> np.ndarray  # same truncation rule
    evals_used: int
    evals_by_tag: dict[MechanismTag, int]
    x_best: np.ndarray; f_best: float              # the incumbent; feeds KeeperArchive A[0]
```

- **Tags** form a closed enumeration with 21 members:
  - `init`;
  - the 8 archetype tags: `sweeper_keeper`, `zonal_centre_back`, `overlapping_wing_back`,
    `deep_lying_playmaker`, `box_to_box`, `destroyer`, `virtuoso`, `finisher`;
  - the 11 tactic tags: `formation`, `rotation`, `possession`, `pressing`, `counter_attack`,
    `set_pieces`, `offside`, `substitutions`, `fatigue`, `var_review`, `manager`;
  - `neutral`, used by the fallback move of a disabled archetype.

  Tags whose mechanisms never evaluate must end the run with a count of 0. Those mechanisms are
  sweeper_keeper, formation, rotation, offside, fatigue, var_review and manager. Their zero rows are
  still written, so that the allocation table is complete.
- **Incumbent.** Every evaluation that improves the incumbent updates `(x_best, f_best)` *inside
  the account*. A later VAR rollback therefore cannot remove the incumbent (aspiration, FR-021; spec
  edge case).
- **Stopping.** When the account raises `BudgetExhausted`, the engine returns immediately, from any
  depth: in the middle of a chain, a burst, a set piece or a poll sequence.

## 3. Invariants (tests in `tests/unit/test_account.py`, `tests/contract/test_ledger.py`)

| ID | Invariant |
|---|---|
| L1 | `evals_used ≤ budget` after any sequence of calls, including batches larger than the remaining budget. This is property-tested with hypothesis. |
| L2 | `sum(evals_by_tag.values()) == evals_used` (internal account). |
| L3 | For TFO runs, internal `evals_used` equals external `evals_used`. |
| L4 | `curve` is non-increasing and has 100 entries. Entry k (k = 1, …, 100) is the best-so-far after exactly ⌈k·B/100⌉ evaluations. |
| L5 | `best_f` equals the minimum over every value the ledger returned. There is no other source for it. |
| L6 | Zero-cost operations (VAR rollback, formation re-lay, rotation, fatigue, archive update) do not change `evals_used`. |
| L7 | The objective is never called with a row outside [0, 1]^D. |

## 4. Reporting

For every run, the following are persisted:

- `evals_used`, and `evals_internal` (TFO family);
- `objective_time_s` and `wall_time_s`;
- the per-tag counts (`mechanism_evals.csv`).

The manuscript's per-mechanism allocation table (SC-003, User Story 4) is computed as each
mechanism's percentage of B, averaged over runs, with the standard deviation. It is read directly
from these records. No figure is estimated.
