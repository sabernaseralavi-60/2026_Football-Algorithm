"""tfo_bench.problems.base: `Problem`, `ProblemView`, `CapabilityError` (data-model.md B1).

`Problem` is real-coordinates-in, real-objective-out, plus the unit-box decoder. `ProblemView` is
what an algorithm actually receives: a vectorised callable on the unit box, wrapping the external
ledger (contracts/evaluation-ledger.md), with `constraints` gated to the epsilon experiment only
(information parity, C7, FR-031).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Optional

import numpy as np


class CapabilityError(Exception):
    """Raised when an algorithm asks for information outside its information-parity level (C7)."""


@dataclass
class Problem:
    problem_id: str
    suite: str
    name: str
    D: int
    lb: np.ndarray
    ub: np.ndarray
    f_star: Optional[float]
    fn: Callable[[np.ndarray], np.ndarray]
    x_star: Optional[np.ndarray] = None
    implementation: str = ""
    has_constraints: bool = False
    constraints_fn: Optional[Callable[[np.ndarray], np.ndarray]] = None
    n_constraints: int = 0

    def __post_init__(self) -> None:
        self.lb = np.broadcast_to(np.asarray(self.lb, dtype=float), (self.D,)).copy()
        self.ub = np.broadcast_to(np.asarray(self.ub, dtype=float), (self.D,)).copy()
        if self.x_star is not None:
            self.x_star = np.asarray(self.x_star, dtype=float).reshape(self.D)

    # -- coordinate mapping (research.md R6) -----------------------------------------

    def decode(self, U: np.ndarray) -> np.ndarray:
        """x = lb + (ub - lb) * u."""
        U = np.atleast_2d(np.asarray(U, dtype=float))
        return self.lb + (self.ub - self.lb) * U

    def encode(self, X: np.ndarray) -> np.ndarray:
        X = np.atleast_2d(np.asarray(X, dtype=float))
        return (X - self.lb) / (self.ub - self.lb)

    # -- evaluation --------------------------------------------------------------------

    def evaluate(self, X_real: np.ndarray) -> np.ndarray:
        return np.asarray(self.fn(np.atleast_2d(np.asarray(X_real, dtype=float))), dtype=float)

    def evaluate_unit(self, U: np.ndarray) -> np.ndarray:
        return self.evaluate(self.decode(U))

    def constraints_real(self, X_real: np.ndarray) -> np.ndarray:
        if self.constraints_fn is None:
            raise CapabilityError(f"{self.problem_id}: this problem has no constraints")
        return np.asarray(
            self.constraints_fn(np.atleast_2d(np.asarray(X_real, dtype=float))), dtype=float
        )

    def constraints_unit(self, U: np.ndarray) -> np.ndarray:
        return self.constraints_real(self.decode(U))

    @property
    def x_star_unit(self) -> Optional[np.ndarray]:
        if self.x_star is None:
            return None
        return self.encode(self.x_star)[0]


class ProblemView:
    """data-model.md B1: what an algorithm receives. Calling it evaluates through the ledger
    (`ledger_callable`, normally a `tfo_bench.ledger.CountingObjective`); `.constraints` is a
    capability gated to `experiment == "epsilon"` (C7)."""

    def __init__(
        self,
        ledger_callable: Callable[[np.ndarray], np.ndarray],
        problem: Problem,
        experiment: str,
    ):
        self._ledger_callable = ledger_callable
        self.problem = problem
        self.experiment = experiment

    def __call__(self, U: np.ndarray) -> np.ndarray:
        return self._ledger_callable(U)

    @property
    def constraints(self) -> Callable[[np.ndarray], np.ndarray]:
        if self.experiment != "epsilon":
            raise CapabilityError(
                "ProblemView.constraints is available only when the job's experiment is "
                f"'epsilon' (C7); this job's experiment is {self.experiment!r}."
            )
        return self.problem.constraints_unit

    @property
    def D(self) -> int:
        return self.problem.D

    @property
    def evals_used(self) -> int:
        """Delegates to the wrapped ledger's `evals_used` (used by adapters that must tell
        "completed using the full budget" apart from "stopped itself early", C1's `self_terminated`
        case, without needing their own separate counter)."""
        return self._ledger_callable.evals_used
