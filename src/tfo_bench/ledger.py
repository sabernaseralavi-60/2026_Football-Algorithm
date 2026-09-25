"""tfo_bench.ledger: the external evaluation ledger (contracts/evaluation-ledger.md §1).

`CountingObjective` is the sole source of truth, for every algorithm in the roster, of the final
best value, the best point, the evaluation count and the convergence curve (research.md R7).
"""

from __future__ import annotations

import time
from typing import Optional

import numpy as np


class BudgetExhausted(Exception):
    """Raised by the ledger when its budget is spent (evaluation-ledger.md §1, item 1-2).

    Adapters (optimizer-interface.md §5) catch this exception and return normally (C5).
    """


class CountingObjective:
    """Wraps a `Problem` for one run, charging every call against `budget` (invariants L1-L7).

    `problem` must expose `evaluate_unit(U) -> f` (unit-box in, real objective out) and an
    optional `f_star` attribute (evaluation-ledger.md §1, item 3: "the curve value is best_f - f*
    when f* is known, and the penalised f otherwise").
    """

    def __init__(self, problem, budget: int, *, checkpoints: int = 100):
        self.problem = problem
        self.budget = int(budget)
        if self.budget < 0:
            raise ValueError("CountingObjective: budget must be >= 0")
        self._n_checkpoints = int(checkpoints)
        self.evals_used = 0
        self.best_f: float = np.inf
        self.best_u: Optional[np.ndarray] = None
        self.curve = np.full(self._n_checkpoints, np.inf, dtype=float)
        self._next_checkpoint = 1
        self.objective_time_ns = 0

    # -- checkpoints ---------------------------------------------------------------

    def _checkpoint_target(self, k: int) -> int:
        return int(np.ceil(k * self.budget / self._n_checkpoints))

    def _curve_value(self) -> float:
        f_star = getattr(self.problem, "f_star", None)
        if f_star is not None:
            return self.best_f - float(f_star)
        return self.best_f

    def _record_checkpoints(self) -> None:
        while (
            self._next_checkpoint <= self._n_checkpoints
            and self.evals_used >= self._checkpoint_target(self._next_checkpoint)
        ):
            self.curve[self._next_checkpoint - 1] = self._curve_value()
            self._next_checkpoint += 1

    def finalize(self) -> None:
        """For a `self_terminated` run: forward-fill any checkpoints past the point where the
        algorithm stopped itself, so `curve` still has exactly 100 non-increasing entries
        (invariant L4). This is a documented judgment call: L4's literal wording only defines
        checkpoints that were actually reached; a self-terminated run never reaches the later
        ones, and the curve must still be reported with 100 entries (results-schema.md §3)."""
        while self._next_checkpoint <= self._n_checkpoints:
            self.curve[self._next_checkpoint - 1] = self._curve_value()
            self._next_checkpoint += 1

    # -- the callable ----------------------------------------------------------------

    def __call__(self, U: np.ndarray) -> np.ndarray:
        U = np.atleast_2d(np.asarray(U, dtype=float))
        if U.size and (np.any(U < 0.0) or np.any(U > 1.0)):
            raise ValueError("CountingObjective: row outside [0, 1]^D (L7, C3)")
        remaining = self.budget - self.evals_used
        if remaining <= 0:
            raise BudgetExhausted()
        m = U.shape[0]
        truncated = m > remaining
        U_eval = U[:remaining] if truncated else U

        t0 = time.perf_counter_ns()
        f = np.asarray(self.problem.evaluate_unit(U_eval), dtype=float)
        self.objective_time_ns += time.perf_counter_ns() - t0

        self.evals_used += U_eval.shape[0]
        for row in range(U_eval.shape[0]):
            if f[row] < self.best_f:
                self.best_f = float(f[row])
                self.best_u = U_eval[row].copy()
        self._record_checkpoints()

        if truncated:
            raise BudgetExhausted()
        return f
