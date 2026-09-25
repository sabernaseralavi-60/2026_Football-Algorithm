"""tfo_bench.algorithms.cmaes: `CMAESAdapter`, IPOP-CMA-ES over `cma.fmin2` (research.md R8;
optimizer-interface.md §4).

`restarts=20` cannot bind before any budget used here (research.md R8's check), so the budget is
what ends every run. Results are read **only from the ledger**: `fmin2` with restarts "returns the
best of the last run only" (research.md R8's verified adapter pitfall), which is why
`algo_reported_best_f` here comes from `es.result.fbest` purely as an (untrusted, C4) cross-check,
never as the actual answer.
"""

from __future__ import annotations

import numpy as np
import cma

from tfo_bench.algorithms.base import OptimizeResult
from tfo_bench.ledger import BudgetExhausted
from tfo_bench.problems.base import ProblemView


class CMAESAdapter:
    name = "CMA-ES (IPOP)"
    variant_id = "default"

    def run(self, view: ProblemView, budget: int, seed: int) -> OptimizeResult:
        D = view.D
        rng = np.random.default_rng(seed)

        def x0() -> np.ndarray:
            # research.md R8: "a callable that draws a fresh uniform point per restart", so every
            # IPOP restart begins from a new point rather than all restarts sharing one x0.
            return rng.random(D)

        def parallel_objective(X):
            return list(view(np.asarray(X)))

        seed_i = int(seed) % (2**31 - 1)
        opts = {
            "bounds": [0.0, 1.0],
            "maxfevals": budget,
            "seed": seed_i or 1,
            "verbose": -9,
        }
        try:
            _xbest, es = cma.fmin2(
                None,
                x0,
                0.3,
                opts,
                parallel_objective=parallel_objective,
                restarts=20,
                incpopsize=2,
                bipop=False,
            )
        except BudgetExhausted:
            return OptimizeResult(status="ok", algo_reported_best_f=None, extras={})

        status = "ok" if view.evals_used >= budget else "self_terminated"
        reported = float(es.result.fbest) if es is not None and es.result.fbest is not None else None
        return OptimizeResult(status=status, algo_reported_best_f=reported, extras={})
