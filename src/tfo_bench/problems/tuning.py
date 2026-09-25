"""tfo_bench.problems.tuning: the disjoint tuning set (research.md R13; data-model.md B3; FR-040).

Seven unconstrained functions (Sphere, Schwefel 1.2, Schwefel 2.22, Alpine N.1, Salomon,
Styblinski-Tang, Dixon-Price), each instantiated with its own random shift and (every second
function) a random orthogonal rotation, at D in {15, 40} -- dimensions and functions that no test
suite uses. Plus two constrained problems: CEC-2006 G04 and the tubular column design.

**Judgment call on the shift magnitude (documented, flagged in the implementation report).**
research.md R13 says the shift is drawn "in [-80, 80]^D" and separately that "the box is
[-100, 100]^D, except Styblinski-Tang, which uses [-5, 5]^D." Taken literally, a shift of up to
+/-80 would move Styblinski-Tang's landscape almost entirely outside its own [-5, 5] box. This
implementation resolves the apparent scale mismatch by drawing the shift as a fraction (0.8) of
each function's own box half-width -- i.e. +/-80 for the [-100, 100] box (matching R13's number
exactly) and +/-4 for Styblinski-Tang's [-5, 5] box -- rather than reusing the literal +/-80
figure unscaled for every function.

**Judgment call on G04 and the tubular column optimum.** Both x* values below were obtained by a
local constrained optimisation (SLSQP) from the commonly published starting points, not
transcribed digit-for-digit from a single literature source; G04's converges to the widely-cited
value to 6+ significant figures. `f_star` is this implementation's own evaluation at that x*, kept
self-consistent by construction. Since the tuning set is used only to freeze thresholds
(never reported as a benchmark result), this is judged an acceptable simplification; anyone
extending this file to a formal benchmark suite should re-verify against a primary source first.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Optional

import numpy as np

from tfo_bench.problems.base import Problem

TUNING_MASTER_SEED = 0x7F0BA11 # committed alongside config/protocol.toml (research.md R11)
DIMS = (15, 40)
SHIFT_FRACTION = 0.8  # of the box half-width; see module docstring


# ----------------------------------------------------------------------------------------
# Native (unshifted, unrotated) functions, each with a known z* and f* in "z-space"
# ----------------------------------------------------------------------------------------


def _sphere(Z: np.ndarray) -> np.ndarray:
    return np.sum(Z**2, axis=1)


def _schwefel_1_2(Z: np.ndarray) -> np.ndarray:
    return np.sum(np.cumsum(Z, axis=1) ** 2, axis=1)


def _schwefel_2_22(Z: np.ndarray) -> np.ndarray:
    A = np.abs(Z)
    return np.sum(A, axis=1) + np.prod(A, axis=1)


def _alpine_n1(Z: np.ndarray) -> np.ndarray:
    return np.sum(np.abs(Z * np.sin(Z) + 0.1 * Z), axis=1)


def _salomon(Z: np.ndarray) -> np.ndarray:
    r = np.sqrt(np.sum(Z**2, axis=1))
    return 1.0 - np.cos(2.0 * np.pi * r) + 0.1 * r


#: Global minimiser of 0.5*(z^4 - 16 z^2 + 5 z), the more negative of the derivative's three real
#: roots (computed once, at import time, to full float64 precision -- see module tests).
_ST_Z0 = float(
    min(
        (r.real for r in np.roots([2.0, 0.0, -16.0, 2.5]) if abs(r.imag) < 1e-9),
        key=lambda z: 0.5 * (z**4 - 16.0 * z**2 + 5.0 * z),
    )
)
_ST_F0 = 0.5 * (_ST_Z0**4 - 16.0 * _ST_Z0**2 + 5.0 * _ST_Z0)


def _styblinski_tang(Z: np.ndarray) -> np.ndarray:
    return 0.5 * np.sum(Z**4 - 16.0 * Z**2 + 5.0 * Z, axis=1)


def _dixon_price(Z: np.ndarray) -> np.ndarray:
    term1 = (Z[:, 0] - 1.0) ** 2
    i = np.arange(2, Z.shape[1] + 1, dtype=float)
    terms = i * (2.0 * Z[:, 1:] ** 2 - Z[:, :-1]) ** 2
    return term1 + np.sum(terms, axis=1)


def _dixon_price_z_star(D: int) -> np.ndarray:
    i = np.arange(1, D + 1, dtype=float)
    return 2.0 ** (-((2.0**i - 2.0) / (2.0**i)))


@dataclass(frozen=True)
class _TuningSpec:
    name: str
    native_fn: Callable[[np.ndarray], np.ndarray]
    z_star: Callable[[int], np.ndarray]  # D -> z* (native optimum, pre shift/rotation)
    f_star_native: Callable[[int], float]  # D -> f* (native optimum value; separable, so f(D))
    box_half_width: float  # symmetric box [-hw, hw]^D
    rotate: bool  # whether this function (order-position) receives a random rotation


_ZERO = lambda D: 0.0  # noqa: E731

_TUNING_SPECS: list[_TuningSpec] = [
    _TuningSpec("Sphere", _sphere, lambda D: np.zeros(D), _ZERO, 100.0, rotate=False),
    _TuningSpec("Schwefel1.2", _schwefel_1_2, lambda D: np.zeros(D), _ZERO, 100.0, rotate=True),
    _TuningSpec("Schwefel2.22", _schwefel_2_22, lambda D: np.zeros(D), _ZERO, 100.0, rotate=False),
    _TuningSpec("AlpineN1", _alpine_n1, lambda D: np.zeros(D), _ZERO, 100.0, rotate=True),
    _TuningSpec("Salomon", _salomon, lambda D: np.zeros(D), _ZERO, 100.0, rotate=False),
    _TuningSpec(
        "StyblinskiTang",
        _styblinski_tang,
        lambda D: np.full(D, _ST_Z0),
        lambda D: D * _ST_F0,  # separable: D copies of the 1-D minimum
        5.0,
        rotate=True,
    ),
    _TuningSpec("DixonPrice", _dixon_price, _dixon_price_z_star, _ZERO, 100.0, rotate=False),
]


def _orthogonal_matrix(D: int, rng: np.random.Generator) -> np.ndarray:
    A = rng.standard_normal((D, D))
    Q, R = np.linalg.qr(A)
    return Q @ np.diag(np.sign(np.diag(R)))


def _make_unconstrained_problem(spec: _TuningSpec, D: int, rng: np.random.Generator) -> Problem:
    half_width = spec.box_half_width
    shift = rng.uniform(-SHIFT_FRACTION * half_width, SHIFT_FRACTION * half_width, size=D)
    rotation: Optional[np.ndarray] = _orthogonal_matrix(D, rng) if spec.rotate else None

    def fn(X: np.ndarray) -> np.ndarray:
        X = np.atleast_2d(X)
        Zc = X - shift
        Z = Zc @ rotation if rotation is not None else Zc
        return spec.native_fn(Z)

    z_star = spec.z_star(D)
    x_star = shift + (rotation @ z_star if rotation is not None else z_star)

    return Problem(
        problem_id=f"tuning_{spec.name}_D{D}",
        suite="tuning",
        name=spec.name,
        D=D,
        lb=-half_width,
        ub=half_width,
        f_star=float(spec.f_star_native(D)),
        fn=fn,
        x_star=x_star,
        implementation="tfo_bench.problems.tuning (in-house)",
        has_constraints=False,
    )


# ----------------------------------------------------------------------------------------
# Constrained tuning problems: CEC-2006 G04 and the tubular column design
# ----------------------------------------------------------------------------------------


def _g04(X: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    X = np.atleast_2d(X)
    x1, x2, x3, x4, x5 = (X[:, i] for i in range(5))
    cost = 5.3578547 * x3**2 + 0.8356891 * x1 * x5 + 37.293239 * x1 - 40792.141
    u = 85.334407 + 0.0056858 * x2 * x5 + 0.0006262 * x1 * x4 - 0.0022053 * x3 * x5
    v = 80.51249 + 0.0071317 * x2 * x5 + 0.0029955 * x1 * x2 + 0.0021813 * x3**2
    w = 9.300961 + 0.0047026 * x3 * x5 + 0.0012547 * x1 * x3 + 0.0019085 * x3 * x4
    G = np.stack([u - 92.0, -u, v - 110.0, 90.0 - v, w - 25.0, 20.0 - w], axis=1)
    return cost, G


_G04_X_STAR = np.array([78.0, 33.0, 29.99525602568160, 45.0, 36.77581290578821])
_G04_LB = np.array([78.0, 33.0, 27.0, 27.0, 27.0])
_G04_UB = np.array([102.0, 45.0, 45.0, 45.0, 45.0])


def _tubular_column(X: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    X = np.atleast_2d(X)
    d, t = X[:, 0], X[:, 1]
    P, L, E, sigma_y = 2500.0, 250.0, 0.85e6, 500.0
    cost = 9.8 * d * t + 2.0 * d
    g1 = 1.0 - P / (np.pi * d * t * sigma_y)
    g2 = 1.0 - 8.0 * P * L**2 / (np.pi**3 * E * d * t * (d**2 + t**2))
    g3 = 2.0 / d - 1.0
    g4 = d / 14.0 - 1.0
    g5 = 0.2 / t - 1.0
    g6 = t / 0.8 - 1.0
    G = np.stack([g1, g2, g3, g4, g5, g6], axis=1)
    return cost, G


_TUBE_X_STAR = np.array([5.451156230, 0.291965480])
_TUBE_LB = np.array([2.0, 0.2])
_TUBE_UB = np.array([14.0, 0.8])

PENALTY_COEFFICIENT = 1.0e6


def _penalized(raw_fn):
    def fn(X: np.ndarray) -> np.ndarray:
        cost, G = raw_fn(X)
        return cost + PENALTY_COEFFICIENT * np.sum(np.maximum(G, 0.0) ** 2, axis=1)

    return fn


def _constrained_problem(name: str, raw_fn, D: int, lb, ub, x_star) -> Problem:
    x_star = np.asarray(x_star, dtype=float)
    cost, G = raw_fn(x_star[None, :])
    f_star = float(cost[0] + PENALTY_COEFFICIENT * np.sum(np.maximum(G[0], 0.0) ** 2))

    def constraints_fn(X: np.ndarray) -> np.ndarray:
        _cost, G = raw_fn(X)
        return G

    return Problem(
        problem_id=f"tuning_{name}",
        suite="tuning",
        name=name,
        D=D,
        lb=lb,
        ub=ub,
        f_star=f_star,
        fn=_penalized(raw_fn),
        x_star=x_star,
        implementation="tfo_bench.problems.tuning (in-house; SLSQP-refined optimum)",
        has_constraints=True,
        constraints_fn=constraints_fn,
    )


def build_problems(D: int) -> dict[str, Problem]:
    """The 7 unconstrained tuning functions at dimension `D` (D must be 15 or 40)."""
    if D not in DIMS:
        raise ValueError(f"tuning set dimensions are {DIMS}, got {D}")
    rng = np.random.default_rng(np.random.SeedSequence([TUNING_MASTER_SEED, D]))
    return {spec.name: _make_unconstrained_problem(spec, D, rng) for spec in _TUNING_SPECS}


def build_constrained_problems() -> dict[str, Problem]:
    """The 2 constrained tuning problems (fixed dimension each, no D parameter)."""
    return {
        "G04": _constrained_problem("G04", _g04, 5, _G04_LB, _G04_UB, _G04_X_STAR),
        "TubularColumn": _constrained_problem(
            "TubularColumn", _tubular_column, 2, _TUBE_LB, _TUBE_UB, _TUBE_X_STAR
        ),
    }
