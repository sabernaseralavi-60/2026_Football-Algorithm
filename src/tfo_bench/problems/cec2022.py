"""tfo_bench.problems.cec2022: the primary CEC-2022 suite backend (research.md R4).

Primary implementation: `opfunu==1.0.4`, classes `F12022` to `F122022`, at D in {10, 20}.
opfunu evaluates one row at a time (research.md R3's throughput note), so the wrapper loops.
"""

from __future__ import annotations

from typing import Callable

import numpy as np

try:
    from opfunu.cec_based import cec2022 as _opfunu_cec2022
except ImportError as exc:  # pragma: no cover
    raise ImportError(
        "tfo_bench.problems.cec2022 requires 'opfunu==1.0.4' (research.md R4). "
        "Install with: pip install opfunu==1.0.4"
    ) from exc

from tfo_bench.problems.base import Problem

NUMBERS: list[int] = list(range(1, 13))
SUPPORTED_DIMS = (10, 20)
IMPLEMENTATION = "opfunu==1.0.4"


def function_id(n: int) -> str:
    return f"F{n:02d}"


def _class_for(n: int):
    return getattr(_opfunu_cec2022, f"F{n}2022")


def _make_fn(instance) -> Callable[[np.ndarray], np.ndarray]:
    def fn(X: np.ndarray) -> np.ndarray:
        X = np.atleast_2d(X)
        return np.array([instance.evaluate(row) for row in X], dtype=float)

    return fn


def build_problems(D: int) -> dict[str, Problem]:
    if D not in SUPPORTED_DIMS:
        raise ValueError(f"CEC-2022 test set only defines D in {SUPPORTED_DIMS}, got {D}")
    problems: dict[str, Problem] = {}
    for n in NUMBERS:
        cls = _class_for(n)
        instance = cls(ndim=D)
        fid = function_id(n)
        problems[fid] = Problem(
            problem_id=f"cec2022_{fid}_D{D}",
            suite="cec2022",
            name=fid,
            D=D,
            lb=np.asarray(instance.lb, dtype=float),
            ub=np.asarray(instance.ub, dtype=float),
            f_star=float(instance.f_global),
            fn=_make_fn(instance),
            x_star=np.asarray(instance.x_global, dtype=float),
            implementation=f"{IMPLEMENTATION}:{cls.__name__}",
            has_constraints=False,
        )
    return problems
