"""tfo_bench.problems.cec2017: the primary CEC-2017 suite backend (research.md R3).

Primary implementation: `cec2017-py` (tilleyd), pinned to git commit
424a9fa2757914c3e4cfdd8f59a268b1aeb3197f (requirements-lock.txt). Official numbering: F1 and F3 to
F30 (F2 withdrawn, per the organisers).

`cec2017-py`'s own default shift for function n (1-indexed) lives at `transforms.shifts[n - 1]`
for the simple and hybrid functions (n = 1..20), and at `transforms.shifts_cf[n - 21][0]` (the
first sub-component's shift) for the composition functions (n = 21..30); this indexing was
confirmed by reading `cec2017/simple.py`, `cec2017/hybrid.py` and `cec2017/composition.py`
directly (each function's docstring/body shows exactly which shift array and index it defaults
to when `shift=None`).
"""

from __future__ import annotations

from typing import Callable

import numpy as np

try:
    import cec2017.functions as _cec2017_functions
    import cec2017.transforms as _cec2017_transforms
except ImportError as exc:  # pragma: no cover - exercised only when the dependency is missing
    raise ImportError(
        "cec2017.problems.cec2017 requires the 'cec2017-py' package (research.md R3). Install "
        "with: pip install "
        "'git+https://github.com/tilleyd/cec2017-py.git"
        "@424a9fa2757914c3e4cfdd8f59a268b1aeb3197f#egg=cec2017'"
    ) from exc

from tfo_bench.problems.base import Problem

#: Official numbering: F1 and F3 to F30 (F2 withdrawn).
OFFICIAL_NUMBERS: list[int] = [1] + list(range(3, 31))

#: Mapping opfunu uses internally (consecutive numbering after the withdrawal): official n (n>=3)
#: is opfunu's F(n-1); official F1 is opfunu's F1 (research.md R3 "Numbering").
OFFICIAL_TO_OPFUNU: dict[int, int] = {1: 1, **{n: n - 1 for n in range(3, 31)}}

IMPLEMENTATION = "cec2017-py@424a9fa2757914c3e4cfdd8f59a268b1aeb3197f"


def function_id(n: int) -> str:
    return f"F{n:02d}"


def x_star(n: int, D: int) -> np.ndarray:
    """The claimed global optimum location for official function `n` at dimension `D`.

    **F9 special case (verified numerically, not merely assumed).** F9 is "Shifted and Rotated
    Levy". `cec2017.basic.levy` computes `w = 1 + 0.25*(z - 1)`, whose own minimum is at `w = 1`,
    i.e. at z = 1 (a vector of ones) -- *not* at z = 0 like every other simple/hybrid function in
    this package (checked directly: `basic.levy(0) ~= 3.26`, while every other `basic.*` function
    used by F1-F20 gives ~0 at z=0). So F9's claimed optimum is not its shift vector alone; it is
    `shift + rotation^-1 @ ones(D)`. This also required discovering that `transforms.rotations`'
    matrices are not numerically orthogonal here (`R @ R.T` is far from the identity), so the true
    matrix inverse is used rather than the transpose. Evaluating cec2017-py's own `f9` at the
    resulting point gives exactly 900.0 (D=30), confirming this is the actual optimum, not an
    approximation.
    """
    if n == 9:
        shift = np.asarray(_cec2017_transforms.shifts[8][:D], dtype=float)
        rotation = _cec2017_transforms.rotations[D][8]
        return shift + np.linalg.inv(rotation) @ np.ones(D)
    if n <= 20:
        return np.asarray(_cec2017_transforms.shifts[n - 1][:D], dtype=float)
    return np.asarray(_cec2017_transforms.shifts_cf[n - 21][0][:D], dtype=float)


def is_composition(n: int) -> bool:
    return n >= 21


def _make_fn(n: int) -> Callable[[np.ndarray], np.ndarray]:
    raw = getattr(_cec2017_functions, f"f{n}")

    def fn(X: np.ndarray) -> np.ndarray:
        return np.asarray(raw(np.atleast_2d(X)), dtype=float)

    return fn


def build_problems(D: int = 30) -> dict[str, Problem]:
    """One `Problem` per official function label, at dimension `D` (test set: D = 30)."""
    problems: dict[str, Problem] = {}
    for n in OFFICIAL_NUMBERS:
        fid = function_id(n)
        problems[fid] = Problem(
            problem_id=f"cec2017_{fid}_D{D}",
            suite="cec2017",
            name=fid,
            D=D,
            lb=-100.0,
            ub=100.0,
            f_star=float(n * 100),
            fn=_make_fn(n),
            x_star=x_star(n, D),
            implementation=IMPLEMENTATION,
            has_constraints=False,
        )
    return problems
