"""tfo_bench.algorithms.lshade: `LSHADEAdapter` over niapy's L-SHADE (research.md R8;
optimizer-interface.md §4).

niapy evaluates one candidate row at a time (its `Problem._evaluate` interface), so the wrapper
loops per-row, same as the CEC-2022 opfunu backend. `Task(max_evals=budget)` enforces niapy's own
cap; the ledger's hard stop is independent of it and is what `runs.csv` ultimately reports
(research.md R7).
"""

from __future__ import annotations

import numpy as np
from niapy.algorithms.modified import (
    LpsrSuccessHistoryAdaptiveDifferentialEvolution as _LSHADE,
)
from niapy.problems import Problem as _NiaProblem
from niapy.task import Task as _NiaTask

from tfo_bench.algorithms.base import OptimizeResult
from tfo_bench.ledger import BudgetExhausted
from tfo_bench.problems.base import ProblemView


class _ViewProblem(_NiaProblem):
    def __init__(self, view: ProblemView, dim: int):
        super().__init__(dimension=dim, lower=0.0, upper=1.0)
        self._view = view

    def _evaluate(self, x):
        return float(self._view(np.asarray(x)[None, :])[0])


class LSHADEAdapter:
    name = "L-SHADE"
    variant_id = "default"

    def run(self, view: ProblemView, budget: int, seed: int) -> OptimizeResult:
        D = view.D
        population_size = 18 * D  # research.md R8 / optimizer-interface.md §4
        problem = _ViewProblem(view, D)
        task = _NiaTask(problem=problem, max_evals=budget, enable_logging=False)
        algo = _LSHADE(population_size=population_size, seed=seed)
        try:
            _best_x, best_f = algo.run(task)
        except BudgetExhausted:
            return OptimizeResult(status="ok", algo_reported_best_f=None, extras={})

        status = "ok" if view.evals_used >= budget else "self_terminated"
        return OptimizeResult(status=status, algo_reported_best_f=float(best_f), extras={})
