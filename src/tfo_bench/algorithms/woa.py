"""tfo_bench.algorithms.woa: `WOAAdapter` over `mealpy.WOA.OriginalWOA` (research.md R8;
optimizer-interface.md §4).

mealpy's own `max_fe` termination was measured to overshoot (research.md R7), so it is passed only
as a redundant, non-binding hint; the ledger's hard stop (`BudgetExhausted`, propagated straight
out of mealpy's `solve()` the moment it fires inside the objective) is what actually enforces the
budget (C1).
"""

from __future__ import annotations

import mealpy
from mealpy.swarm_based import WOA

from tfo_bench.algorithms.base import OptimizeResult
from tfo_bench.ledger import BudgetExhausted
from tfo_bench.problems.base import ProblemView

POP = 30


class WOAAdapter:
    name = "WOA"
    variant_id = "default"

    def run(self, view: ProblemView, budget: int, seed: int) -> OptimizeResult:
        D = view.D

        def obj_func(x):
            return float(view(x)[0])

        problem = {
            "obj_func": obj_func,
            "bounds": mealpy.FloatVar(lb=[0.0] * D, ub=[1.0] * D),
            "minmax": "min",
            "log_to": None,
        }
        epoch = max(1, budget // POP - 1)
        model = WOA.OriginalWOA(epoch=epoch, pop_size=POP)
        try:
            best = model.solve(problem, seed=seed, termination={"max_fe": budget})
        except BudgetExhausted:
            return OptimizeResult(status="ok", algo_reported_best_f=None, extras={})

        status = "ok" if view.evals_used >= budget else "self_terminated"
        return OptimizeResult(
            status=status, algo_reported_best_f=float(best.target.fitness), extras={}
        )
