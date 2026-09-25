"""The CEC-2017 cross-check backend: opfunu, at official numbering (research.md R3).

opfunu renumbers CEC-2017 consecutively after the withdrawn F2 (its F1..F29 are official
F1, F3..F30). `OFFICIAL_TO_OPFUNU` (in `tfo_bench.problems.cec2017`) is the single source of truth
for that mapping; this module re-exports problems keyed by the *official* label so audit code
never has to think about the renumbering.
"""

from __future__ import annotations

import numpy as np

from opfunu.cec_based import cec2017 as _opfunu_cec2017

from tfo_bench.problems.base import Problem
from tfo_bench.problems.cec2017 import OFFICIAL_NUMBERS, OFFICIAL_TO_OPFUNU, function_id

IMPLEMENTATION = "opfunu==1.0.4 (CEC-2017 cross-check)"


def _class_for(official_n: int):
    opfunu_n = OFFICIAL_TO_OPFUNU[official_n]
    return getattr(_opfunu_cec2017, f"F{opfunu_n}2017")


def _make_fn(instance):
    def fn(X: np.ndarray) -> np.ndarray:
        X = np.atleast_2d(X)
        return np.array([instance.evaluate(row) for row in X], dtype=float)

    return fn


def build_problems(D: int = 30) -> dict[str, Problem]:
    problems: dict[str, Problem] = {}
    for n in OFFICIAL_NUMBERS:
        cls = _class_for(n)
        instance = cls(ndim=D)
        fid = function_id(n)
        problems[fid] = Problem(
            problem_id=f"cec2017_{fid}_D{D}_reference",
            suite="cec2017",
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
