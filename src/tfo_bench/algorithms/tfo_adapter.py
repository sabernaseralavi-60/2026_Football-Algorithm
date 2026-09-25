"""tfo_bench.algorithms.tfo_adapter: `TFOAdapter` and the TFO-family variant constructors
(optimizer-interface.md §1, §4; research.md R14)."""

from __future__ import annotations

import numpy as np

import tfo
from tfo.config import TFOConfig
from tfo.registry import ENABLE_TAGS, Archetype, MechanismTag

from tfo_bench.algorithms.base import OptimizeResult
from tfo_bench.ledger import BudgetExhausted
from tfo_bench.problems.base import ProblemView

#: Outfield archetypes only (the Sweeper-Keeper is the goalkeeper role, not swept into the
#: 7 homogeneous-squad variants of research.md R14).
_OUTFIELD_ARCHETYPES = [a for a in Archetype if a != Archetype.SWEEPER_KEEPER]

#: The 18 switchable mechanisms of the one-at-a-time ablation (research.md R14): every ENABLE_TAGS
#: entry except MANAGER, whose off-variant is the separately named "static" (TFO-static).
_ONE_AT_A_TIME_TAGS = [t for t in ENABLE_TAGS if t != MechanismTag.MANAGER]


def _roster_name_for(variant_id: str) -> str:
    if variant_id == "full":
        return "TFO"
    if variant_id == "static":
        return "TFO-static"
    return f"TFO[{variant_id}]"


class TFOAdapter:
    """Wraps `tfo.minimize` (optimizer-interface.md §1) as a roster `Optimizer`."""

    def __init__(self, config: TFOConfig | None = None):
        self.config = config if config is not None else TFOConfig()
        self.variant_id = self.config.variant_id
        self.name = _roster_name_for(self.variant_id)

    def run(self, view: ProblemView, budget: int, seed: int) -> OptimizeResult:
        d = view.D
        lb = np.zeros(d)
        ub = np.ones(d)
        try:
            result = tfo.minimize(view, (lb, ub), budget, seed, self.config)
        except BudgetExhausted:
            # Defensive only: TFO's own internal EvalAccount tracks the identical budget and
            # raises (and engine.py catches) its own `tfo.account.BudgetExhausted` before the
            # external ledger's batches are ever oversized, so this should not normally trigger.
            # Kept because C5 requires every adapter to handle it regardless.
            return OptimizeResult(status="self_terminated", algo_reported_best_f=None, extras={})

        extras = {
            "evals_by_mechanism": dict(result.evals_by_mechanism),
            "tactical_trace": list(result.tactical_trace),
            "summary": dict(result.summary),
            "x_best_real": result.x_best,
            "config_hash": result.config_hash,
        }
        return OptimizeResult(status="ok", algo_reported_best_f=result.f_best, extras=extras)


def full_adapter() -> TFOAdapter:
    return TFOAdapter(TFOConfig())


def static_adapter() -> TFOAdapter:
    return TFOAdapter(tfo.TFO_STATIC)


def one_at_a_time_variants() -> dict[str, TFOAdapter]:
    """The 18 single-mechanism-off variants (research.md R14)."""
    return {
        f"off:{tag.value}": TFOAdapter(TFOConfig().ablate(tag)) for tag in _ONE_AT_A_TIME_TAGS
    }


def g_topology_variant() -> TFOAdapter:
    """Formation replaced by full connectivity AND positional rotation off (research.md R14)."""
    cfg = TFOConfig().ablate(MechanismTag.FORMATION).ablate(MechanismTag.ROTATION)
    return TFOAdapter(cfg)


def homogeneous_variants() -> dict[str, TFOAdapter]:
    """The 7 homogeneous-squad variants, one per outfield archetype (research.md R14)."""
    return {
        f"homog:{a.value.lower()}": TFOAdapter(TFOConfig().homogeneous(a))
        for a in _OUTFIELD_ARCHETYPES
    }


def ablation_variants() -> dict[str, TFOAdapter]:
    """All 20 Stage-B ablation variants: the 18 one-at-a-time + G-topology + (as a convenience;
    full/static are reused from the main run, not re-listed here per research.md R14)."""
    variants = dict(one_at_a_time_variants())
    variants["G-topology"] = g_topology_variant()
    return variants
