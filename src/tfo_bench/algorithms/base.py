"""tfo_bench.algorithms.base: the harness protocol every roster adapter implements
(optimizer-interface.md §2)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal, Protocol, runtime_checkable

import numpy as np

from tfo_bench.problems.base import ProblemView

#: The 9-algorithm roster labels (optimizer-interface.md §1). TFO family variants use
#: "TFO[<variant_id>]" and are not listed individually here.
ROSTER_LABELS: tuple[str, ...] = (
    "TFO",
    "TFO-static",
    "CA",
    "GA",
    "PSO",
    "GWO",
    "WOA",
    "L-SHADE",
    "CMA-ES (IPOP)",
)


@dataclass(frozen=True)
class OptimizeResult:
    """optimizer-interface.md §2."""

    status: Literal["ok", "self_terminated"]
    algo_reported_best_f: float | None
    extras: dict[str, Any] = field(default_factory=dict)


@runtime_checkable
class Optimizer(Protocol):
    name: str
    variant_id: str

    def run(self, view: ProblemView, budget: int, seed: int) -> OptimizeResult: ...


#: name -> constructor callable, populated by each adapter module's `register()` call so that
#: importing `tfo_bench.algorithms` (or any one adapter module) is enough to discover it. Kept as
#: a plain module-level dict rather than a decorator-based registry, since adapters need
#: constructor arguments (a `TFOConfig`, an overhead ratio omega, ...) that differ per algorithm.
REGISTRY: dict[str, type] = {}


def register(name: str, cls: type) -> None:
    REGISTRY[name] = cls
