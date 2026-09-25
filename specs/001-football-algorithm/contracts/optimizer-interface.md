# Contract: Optimizer interface

**Purpose.** Every algorithm in the roster must be interchangeable inside one harness: TFO,
TFO-static, the TFO variants, CA, GA, PSO, GWO, WOA, L-SHADE and CMA-ES (IPOP). There is also a
public entry point so that practitioners can use TFO on its own (User Story 5).

**Consumers.**

- `tfo_bench.runner`, which runs every experiment.
- The contract tests in `tests/contract/`.
- External users of `tfo.minimize`.

## 1. Public TFO entry point (`tfo` package, depends only on NumPy)

```python
def minimize(
    fun: Callable[[np.ndarray], np.ndarray],   # vectorised: (m, D) -> (m,)
    bounds: tuple[ArrayLike, ArrayLike],       # (lb, ub), each shape (D,) or scalar
    budget: int,                               # exact maximum number of objective evaluations
    seed: int,
    config: TFOConfig | None = None,           # None -> packaged frozen defaults (TFO)
    *,
    constraints: Callable[[np.ndarray], np.ndarray] | None = None,  # (m, D) -> (m, n_g); enables ε-line
    callback: Callable[[TFOProgress], None] | None = None,
) -> TFOResult
```

**`TFOResult`** is a frozen dataclass with these fields:

- `x_best` of shape (D,), in real coordinates;
- `f_best`, `evals_used`;
- `evals_by_mechanism: dict[str, int]`;
- `curve` of shape (100,), the best-so-far at k·budget/100 for k = 1, …, 100;
- `tactical_trace: list[TacticalSegment]`;
- `summary: dict` (A14 in data-model.md);
- `config_hash: str`.

`tfo.TFO_STATIC` is a ready-made `TFOConfig` with `enable.manager = False`. `TFOConfig.ablate(...)`,
`.homogeneous(...)` and `.with_(...)` build the variants listed in data-model.md A15.

## 2. Harness protocol (`tfo_bench.algorithms.base`)

```python
class Optimizer(Protocol):
    name: str                 # roster label: "TFO", "TFO-static", "CA", "GA", "PSO", "GWO",
                              # "WOA", "L-SHADE", "CMA-ES (IPOP)", or "TFO[<variant_id>]"
    variant_id: str           # "default" for baselines; data-model A15 ids for TFO
    def run(self, view: ProblemView, budget: int, seed: int) -> OptimizeResult: ...

@dataclass(frozen=True)
class OptimizeResult:
    status: Literal["ok", "self_terminated"]     # "self_terminated" = stopped before the budget by its own rule
    algo_reported_best_f: float | None           # the algorithm's own claim; cross-checked, never trusted
    extras: dict                                 # TFO: evals_by_mechanism, tactical_trace, summary
```

- `view` is a `ProblemView`: a vectorised callable on the **unit box** that is already wrapped by the
  external `CountingObjective`. See [evaluation-ledger.md](./evaluation-ledger.md).
- The final `best_f`, `best_x`, `evals_used` and `curve` are read **from the ledger** by the runner.
  They are never taken from `OptimizeResult`.

## 3. Invariants that every adapter must satisfy

Each invariant is checked by `tests/contract/test_optimizer_contract.py`, parametrised over all
adapters.

| ID | Invariant |
|---|---|
| C1 | `ledger.evals_used ≤ budget` on every run. It equals `budget` unless `status == "self_terminated"`. |
| C2 | Determinism: the same `(view, budget, seed)` gives bit-identical ledger outputs on the reference environment. |
| C3 | Every point the adapter evaluates lies in [0, 1]^D. The ledger asserts this. |
| C4 | `algo_reported_best_f`, when present, is ≥ `ledger.best_f − 1e-12·max(1, abs(ledger.best_f))`. An algorithm cannot claim a value it never evaluated. |
| C5 | The adapter handles `BudgetExhausted` and returns normally. No other exception escapes. |
| C6 | Initial population: the vendored GA, PSO, GWO and CA, and TFO, make `default_rng(seed).random((30, D))` their first draw, so these algorithms share initial populations under common random numbers (CRN, research.md R11). |
| C7 | Information parity: calling `view.constraints` raises `CapabilityError` unless the job's experiment is `epsilon`. |
| C8 | TFO family only: `sum(extras["evals_by_mechanism"].values()) == ledger.evals_used`. |

## 4. Adapter mapping (budget translation)

| Adapter | Underlying call | Budget handling |
|---|---|---|
| `TFOAdapter(config)` | `tfo.minimize(view, (0, 1), budget, seed, config)` | TFO counts natively, and the internal and external counts must agree (C8) |
| `CAAdapter` | vendored `chess_algorithm_v3(fun, 0.0, 1.0, D, 30, iters, rng)` | `iters = ⌊B / (30·(1+ω_D))⌋`, with ω_D frozen in `protocol.toml` (research.md R9); ledger stop at B |
| `GAAdapter`, `PSOAdapter`, `GWOAdapter` | vendored `genetic_algorithm`, `particle_swarm`, `grey_wolf` | `iters` computed from each routine's evaluation pattern (initial evaluations plus per-iteration evaluations) so that its schedule ends at B; ledger stop |
| `WOAAdapter` | `mealpy.WOA.OriginalWOA(epoch=B//30 − 1, pop_size=30).solve(..., termination={"max_fe": B}, seed=seed)` | mealpy's own cap overshoots (measured), so the ledger stop is the binding one |
| `LSHADEAdapter` | `niapy` L-SHADE, `population_size=18·D`, `Task(max_evals=B)` | Linear population reduction uses the true B |
| `CMAESAdapter` | `cma.fmin2(None, x0, 0.3, {"bounds": [0, 1], "maxfevals": B, "seed": seed, "verbose": -9}, parallel_objective=view, restarts=9, incpopsize=2)` | `x0` is drawn from `default_rng(seed)`; ledger stop |

**Pinned versions** (research.md R8): mealpy 3.0.3 (installed `--no-deps`), niapy 2.7.1, cma 4.5.0.
The vendored CA file is pinned by SHA-256 in `vendor/PROVENANCE.md`.

## 5. Errors

| Exception | Raised by | Meaning |
|---|---|---|
| `BudgetExhausted` | the ledger | The budget is spent. This is expected, and adapters catch it. |
| `CapabilityError` | ProblemView | The algorithm asked for information outside its parity level. |
| `ConfigNotFrozenError` | runner | A non-smoke test-suite job was requested with a TFO configuration hash that differs from the file at tag `tfo-frozen-v1` (G3). |
| `AuditPendingError` | analysis | A cell without an admissible audit disposition reached the analysis (G5). |
