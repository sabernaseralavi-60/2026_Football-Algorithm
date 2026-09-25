"""EvalAccount: TFO's internal evaluation ledger (data-model.md A13; evaluation-ledger.md §2)."""

from __future__ import annotations

from typing import Callable

import numpy as np

from tfo.registry import ALL_TAGS, MechanismTag


class BudgetExhausted(Exception):
    """Raised when the evaluation budget is spent (evaluation-ledger.md §2 "Stopping")."""


class EvalAccount:
    """The internal per-mechanism evaluation ledger, TFO-only (data-model.md A13).

    Semantics mirror contracts/evaluation-ledger.md §1's external `CountingObjective`, so that for
    TFO runs L3 ("internal evals_used equals external evals_used") can hold once the external
    ledger exists (out of scope for this pass): batches are truncated exactly at the remaining
    budget, and truncation still raises `BudgetExhausted` after recording the evaluated rows.
    """

    def __init__(
        self,
        budget: int,
        objective: Callable[[np.ndarray], np.ndarray],
        d: int,
        n_checkpoints: int = 100,
    ):
        self.budget = budget
        self._objective = objective
        self.d = d
        self.evals_used = 0
        self.evals_by_tag: dict[MechanismTag, int] = {tag: 0 for tag in ALL_TAGS}
        self.x_best: np.ndarray | None = None
        self.f_best: float = np.inf
        self._n_checkpoints = n_checkpoints
        self.curve = np.full(n_checkpoints, np.inf)
        self._next_checkpoint = 1

    def _checkpoint_target(self, k: int) -> int:
        return int(np.ceil(k * self.budget / self._n_checkpoints))

    def _record_checkpoints(self) -> None:
        while (
            self._next_checkpoint <= self._n_checkpoints
            and self.evals_used >= self._checkpoint_target(self._next_checkpoint)
        ):
            self.curve[self._next_checkpoint - 1] = self.f_best
            self._next_checkpoint += 1

    def _update_incumbent(self, X: np.ndarray, f: np.ndarray) -> None:
        idx = int(np.argmin(f))
        if f[idx] < self.f_best:
            self.f_best = float(f[idx])
            self.x_best = X[idx].copy()

    def evaluate(self, X: np.ndarray, tag: MechanismTag) -> np.ndarray:
        """Evaluate a batch under `tag`, truncating exactly at the remaining budget (L1)."""
        X = np.atleast_2d(X)
        if np.any(X < 0.0) or np.any(X > 1.0):
            raise ValueError("EvalAccount.evaluate: row outside [0, 1]^D (L7)")
        remaining = self.budget - self.evals_used
        if remaining <= 0:
            raise BudgetExhausted()
        m = X.shape[0]
        truncated = m > remaining
        X_eval = X[:remaining] if truncated else X
        f = np.asarray(self._objective(X_eval), dtype=float)
        self.evals_used += X_eval.shape[0]
        self.evals_by_tag[tag] += X_eval.shape[0]
        self._update_incumbent(X_eval, f)
        self._record_checkpoints()
        if truncated:
            raise BudgetExhausted()
        return f

    def record_zero_cost(self, tag: MechanismTag) -> None:
        """Marks that a zero-cost mechanism ran, without charging any evaluations (L6)."""
        self.evals_by_tag.setdefault(tag, 0)
