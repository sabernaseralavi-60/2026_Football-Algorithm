"""tfo_bench.algorithms.sibling: CA, GA, PSO, GWO adapters over the vendored sibling file
(optimizer-interface.md §4; research.md R8, R9).

Every vendored routine is called on the **unit box** (`lb=0.0, ub=1.0`), so its first draw is
exactly `default_rng(seed).random((pop, D))` (contract C6), matching TFO's own first draw.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

import numpy as np

from tfo_bench.algorithms.base import OptimizeResult
from tfo_bench.ledger import BudgetExhausted
from tfo_bench.problems.base import ProblemView

_VENDOR_PATH = Path(__file__).parent / "vendor" / "chess_algorithms_96af96b.py"


def _load_vendored_module():
    spec = importlib.util.spec_from_file_location("_chess_algorithms_96af96b", _VENDOR_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


_vendored = _load_vendored_module()

POP = 30


def _view_as_fun(view: ProblemView):
    """The vendored routines call `fun(X)` with X shape (m, D); `view` already has that shape."""

    def fun(X: np.ndarray) -> np.ndarray:
        return np.asarray(view(np.atleast_2d(X)), dtype=float)

    return fun


class _VendoredAdapter:
    """Shared run() body: catch the ledger's BudgetExhausted (raised once the vendored routine's
    own schedule oversteps, or at its very last, over-length iteration) and read nothing from the
    routine's own return value except for a defensive `algo_reported_best_f` cross-check (C4);
    the authoritative best/evals/curve always come from the ledger (optimizer-interface.md §2)."""

    name: str
    variant_id = "default"

    def __init__(self, iters_fn):
        # iters_fn(budget, D) -> the vendored routine's `iters` argument, chosen so its own
        # evaluation schedule ends at (or, for CA, just at/under) budget (research.md R8).
        self._iters_fn = iters_fn

    def _call_vendored(self, fun, D: int, iters: int, rng: np.random.Generator):
        raise NotImplementedError

    def run(self, view: ProblemView, budget: int, seed: int) -> OptimizeResult:
        D = view.D
        fun = _view_as_fun(view)
        rng = np.random.default_rng(seed)
        iters = max(1, self._iters_fn(budget, D))
        try:
            _best_x, best_f, _curve = self._call_vendored(fun, D, iters, rng)
        except BudgetExhausted:
            # The ledger's hard truncation fired mid-schedule: it evaluated exactly the rows that
            # still fit and evals_used is now exactly `budget` (evaluation-ledger.md §1 item 2).
            # This is the schedule "ending at B" by design (research.md R7), not an early stop.
            return OptimizeResult(status="ok", algo_reported_best_f=None, extras={})
        # Completed its own loop without the ledger ever needing to cut it off. For GA/PSO/GWO
        # (iters chosen as the tightest value with pop*(1+iters) >= budget) this reaches budget
        # exactly or overshoots (caught above); for CA (whose iters uses the contract's literal
        # floor of the measured overhead ratio, research.md R9) it may leave an "unspent
        # remainder", which is exactly the `self_terminated` case of C1.
        status = "ok" if view.evals_used >= budget else "self_terminated"
        return OptimizeResult(status=status, algo_reported_best_f=float(best_f), extras={})


def _tight_iters(budget: int, pop: int) -> int:
    """The smallest `iters` with `pop*(1+iters) >= budget` (ceil, minus the initial batch): this
    makes the routine's own internal decay schedules (PSO inertia, GWO's `a`, GA's mutation sigma)
    finish at essentially the budget (research.md R8), while any (sub-`pop`) overshoot is what the
    ledger's exact truncation absorbs (research.md R7) -- never an under-spent remainder."""
    import math

    return max(1, math.ceil(budget / pop) - 1)


class GAAdapter(_VendoredAdapter):
    name = "GA"

    def __init__(self):
        # genetic_algorithm evaluates pop initially, then pop per iteration: pop*(1+iters) ~ B.
        super().__init__(lambda budget, D: _tight_iters(budget, POP))

    def _call_vendored(self, fun, D, iters, rng):
        return _vendored.genetic_algorithm(fun, 0.0, 1.0, D, POP, iters, rng)


class PSOAdapter(_VendoredAdapter):
    name = "PSO"

    def __init__(self):
        super().__init__(lambda budget, D: _tight_iters(budget, POP))

    def _call_vendored(self, fun, D, iters, rng):
        return _vendored.particle_swarm(fun, 0.0, 1.0, D, POP, iters, rng)


class GWOAdapter(_VendoredAdapter):
    name = "GWO"

    def __init__(self):
        super().__init__(lambda budget, D: _tight_iters(budget, POP))

    def _call_vendored(self, fun, D, iters, rng):
        return _vendored.grey_wolf(fun, 0.0, 1.0, D, POP, iters, rng)


class CAAdapter(_VendoredAdapter):
    """`chess_algorithm_v3`, the published adaptive CA (research.md R9).

    CA's own docstring states its overhead (en-passant, windmill, castling, blockade probes) at
    "~12-15% ... vs the pop*iters core budget", plus one extra `pop` evaluations at
    initialisation (opposition-based init, `opp_init=True`, the published default). Concretely,
    its *measured* schedule is `pop*(1 + opp_init) + iters*pop*(1+omega) <= budget` where omega is
    the per-iteration overhead ratio measured empirically on the tuning set and frozen in
    `protocol.toml`; `omega_estimate` defaults to the docstring's own 0.135 (midpoint of 12-15%)
    until `scripts/tune.py` overwrites it with a measured value.
    """

    name = "CA"

    def __init__(self, omega: float = 0.135):
        self.omega = float(omega)
        # optimizer-interface.md §4: iters = floor(B / (30 * (1 + omega))).
        super().__init__(lambda budget, D: int(budget // (POP * (1.0 + self.omega))))

    def _call_vendored(self, fun, D, iters, rng):
        return _vendored.chess_algorithm_v3(fun, 0.0, 1.0, D, POP, iters, rng)
