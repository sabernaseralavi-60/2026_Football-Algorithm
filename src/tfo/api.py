"""tfo.minimize(): the public entry point (optimizer-interface.md §1)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Optional

import numpy as np

from tfo import engine
from tfo.config import TFOConfig
from tfo.trace import TacticalSegment


@dataclass(frozen=True)
class TFOProgress:
    """Passed to the optional `callback` on every engine iteration."""

    iteration: int
    evals_used: int
    f_best: float
    state: str


@dataclass(frozen=True)
class TFOResult:
    """optimizer-interface.md §1."""

    x_best: np.ndarray
    f_best: float
    evals_used: int
    evals_by_mechanism: dict[str, int]
    curve: np.ndarray
    tactical_trace: list[TacticalSegment]
    summary: dict
    config_hash: str


def _resolve_bounds(bounds: tuple, ) -> tuple[np.ndarray, np.ndarray, int]:
    lb, ub = bounds
    lb_arr = np.atleast_1d(np.asarray(lb, dtype=float))
    ub_arr = np.atleast_1d(np.asarray(ub, dtype=float))
    if lb_arr.shape == (1,) and ub_arr.shape == (1,):
        raise ValueError(
            "tfo.minimize: scalar (lb, ub) bounds do not determine the dimension D; "
            "pass array-like bounds of shape (D,) for both lb and ub."
        )
    d = max(lb_arr.shape[0], ub_arr.shape[0])
    lb_arr = np.broadcast_to(lb_arr, (d,)).astype(float)
    ub_arr = np.broadcast_to(ub_arr, (d,)).astype(float)
    return lb_arr, ub_arr, d


def minimize(
    fun: Callable[[np.ndarray], np.ndarray],
    bounds: tuple,
    budget: int,
    seed: int,
    config: Optional[TFOConfig] = None,
    *,
    constraints: Optional[Callable[[np.ndarray], np.ndarray]] = None,
    callback: Optional[Callable[[TFOProgress], None]] = None,
) -> TFOResult:
    """Run TFO standalone (optimizer-interface.md §1). `fun` is vectorised: (m, D) -> (m,), and is
    called in REAL coordinates; `tfo` itself always searches the unit box internally and maps
    through `bounds`.

    Scope note: `constraints` (which would enable the moving offside epsilon-line,
    mechanism-interface.md §2.15) is accepted for interface compatibility, but the epsilon-line's
    end-to-end wiring through every mechanism's accept/reject logic is out of scope for this pass
    (it only matters for the epsilon-experiment jobs of the benchmark harness); passing a non-None
    `constraints` therefore raises `NotImplementedError` rather than silently ignoring it.
    """
    if constraints is not None:
        raise NotImplementedError(
            "tfo.minimize(constraints=...): the epsilon-line's constrained acceptance path is "
            "out of scope for this implementation pass (mechanism #15's epsilon-experiment wiring)."
        )

    lb, ub, d = _resolve_bounds(bounds)
    cfg = config if config is not None else TFOConfig()

    def objective(U: np.ndarray) -> np.ndarray:
        X_real = lb + U * (ub - lb)
        return np.asarray(fun(X_real), dtype=float)

    def _callback_adapter(**kwargs) -> None:
        callback(TFOProgress(**kwargs))

    account, trace, ctx = engine.run(
        cfg,
        objective,
        d=d,
        budget=budget,
        seed=seed,
        callback=_callback_adapter if callback is not None else None,
    )

    x_best_real = lb + account.x_best * (ub - lb) if account.x_best is not None else np.full(d, np.nan)
    total_iterations = trace.segments[-1].iter_end if trace.segments else 0
    tried = ctx.ball.passes_tried
    retained = ctx.ball.passes_retained
    final_possession_rate = retained / tried if tried > 0 else 0.0

    return TFOResult(
        x_best=x_best_real,
        f_best=account.f_best,
        evals_used=account.evals_used,
        evals_by_mechanism={tag.value: count for tag, count in account.evals_by_tag.items()},
        curve=account.curve.copy(),
        tactical_trace=list(trace.segments),
        summary=trace.summary(total_iterations, final_possession_rate),
        config_hash=cfg.config_hash,
    )
