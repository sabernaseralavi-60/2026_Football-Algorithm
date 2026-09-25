"""tfo_bench.problems.engineering: the 7 ported constrained engineering design problems
(research.md R10).

Ported from the sibling's `engineering_problems.py` at commit 96af96bbb5ef36514ae11a0cc5695d4a
6211d9a4 (read-only reference; the sibling repository is never imported here, per the
constitution's "sibling is a read-only reference" rule). Each problem here returns `(cost, G)`
instead of the sibling's single penalised scalar, so the raw constraint vector `G` is available
through the epsilon-experiment capability (`ProblemView.constraints`) without a second,
divergent formulation (research.md R10's rationale).

The **shared formulation** — the static penalty f = cost + 1e6 * sum(max(0, g_i)^2) — is applied
by `Problem.fn` below, unchanged from the sibling. `f_ref` is the literature best-known value
(orientation only, per data-model.md B4's engineering variant), not a proven optimum.

A golden test (`tests/golden/test_engineering_port.py`) checks this port against fixture values
captured once from the sibling's own module (read-only), to 1e-12 relative.
"""

from __future__ import annotations

from typing import Callable

import numpy as np

from tfo_bench.problems.base import Problem

PENALTY_COEFFICIENT = 1.0e6


def _penalize(cost: np.ndarray, G: np.ndarray) -> np.ndarray:
    return cost + PENALTY_COEFFICIENT * np.sum(np.maximum(G, 0.0) ** 2, axis=1)


# ----------------------------------------------------------------------------------------
# The 7 problems, each: X (m, D) -> (cost (m,), G (m, n_g))
# ----------------------------------------------------------------------------------------


def welded_beam(X: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    X = np.atleast_2d(X)
    h, l, t, b = X[:, 0], X[:, 1], X[:, 2], X[:, 3]
    P, Lc, E, G = 6000.0, 14.0, 30e6, 12e6
    tau_max, sigma_max, delta_max = 13600.0, 30000.0, 0.25

    cost = 1.10471 * h**2 * l + 0.04811 * t * b * (14.0 + l)
    M = P * (Lc + l / 2.0)
    R = np.sqrt(l**2 / 4.0 + ((h + t) / 2.0) ** 2)
    J = 2.0 * (np.sqrt(2.0) * h * l * (l**2 / 12.0 + ((h + t) / 2.0) ** 2))
    tau1 = P / (np.sqrt(2.0) * h * l)
    tau2 = M * R / J
    tau = np.sqrt(tau1**2 + 2.0 * tau1 * tau2 * l / (2.0 * R) + tau2**2)
    sigma = 6.0 * P * Lc / (b * t**2)
    delta = 4.0 * P * Lc**3 / (E * t**3 * b)
    Pc = (
        4.013
        * E
        * np.sqrt(t**2 * b**6 / 36.0)
        / Lc**2
        * (1.0 - t / (2.0 * Lc) * np.sqrt(E / (4.0 * G)))
    )
    Gm = np.stack(
        [
            tau - tau_max,
            sigma - sigma_max,
            h - b,
            0.10471 * h**2 + 0.04811 * t * b * (14.0 + l) - 5.0,
            0.125 - h,
            delta - delta_max,
            P - Pc,
        ],
        axis=1,
    )
    return cost, Gm


def spring(X: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    X = np.atleast_2d(X)
    d, D, N = X[:, 0], X[:, 1], X[:, 2]
    cost = (N + 2.0) * D * d**2
    Gm = np.stack(
        [
            1.0 - D**3 * N / (71785.0 * d**4),
            (4.0 * D**2 - d * D) / (12566.0 * (D * d**3 - d**4)) + 1.0 / (5108.0 * d**2) - 1.0,
            1.0 - 140.45 * d / (D**2 * N),
            (D + d) / 1.5 - 1.0,
        ],
        axis=1,
    )
    return cost, Gm


def pressure_vessel(X: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    X = np.atleast_2d(X)
    Ts, Th, R, L = X[:, 0], X[:, 1], X[:, 2], X[:, 3]
    cost = 0.6224 * Ts * R * L + 1.7781 * Th * R**2 + 3.1661 * Ts**2 * L + 19.84 * Ts**2 * R
    Gm = np.stack(
        [
            -Ts + 0.0193 * R,
            -Th + 0.00954 * R,
            -np.pi * R**2 * L - (4.0 / 3.0) * np.pi * R**3 + 1296000.0,
            L - 240.0,
        ],
        axis=1,
    )
    return cost, Gm


def speed_reducer(X: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    X = np.atleast_2d(X)
    x1, x2, x3, x4, x5, x6, x7 = (X[:, i] for i in range(7))
    cost = (
        0.7854 * x1 * x2**2 * (3.3333 * x3**2 + 14.9334 * x3 - 43.0934)
        - 1.508 * x1 * (x6**2 + x7**2)
        + 7.4777 * (x6**3 + x7**3)
        + 0.7854 * (x4 * x6**2 + x5 * x7**2)
    )
    Gm = np.stack(
        [
            27.0 / (x1 * x2**2 * x3) - 1.0,
            397.5 / (x1 * x2**2 * x3**2) - 1.0,
            1.93 * x4**3 / (x2 * x3 * x6**4) - 1.0,
            1.93 * x5**3 / (x2 * x3 * x7**4) - 1.0,
            np.sqrt((745.0 * x4 / (x2 * x3)) ** 2 + 16.9e6) / (110.0 * x6**3) - 1.0,
            np.sqrt((745.0 * x5 / (x2 * x3)) ** 2 + 157.5e6) / (85.0 * x7**3) - 1.0,
            x2 * x3 / 40.0 - 1.0,
            5.0 * x2 / x1 - 1.0,
            x1 / (12.0 * x2) - 1.0,
            (1.5 * x6 + 1.9) / x4 - 1.0,
            (1.1 * x7 + 1.9) / x5 - 1.0,
        ],
        axis=1,
    )
    return cost, Gm


def three_bar_truss(X: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    X = np.atleast_2d(X)
    x1, x2 = X[:, 0], X[:, 1]
    Lc, P, s = 100.0, 2.0, 2.0
    cost = (2.0 * np.sqrt(2.0) * x1 + x2) * Lc
    den = np.sqrt(2.0) * x1**2 + 2.0 * x1 * x2
    Gm = np.stack(
        [
            (np.sqrt(2.0) * x1 + x2) / np.maximum(den, 1e-12) * P - s,
            x2 / np.maximum(den, 1e-12) * P - s,
            1.0 / np.maximum(np.sqrt(2.0) * x2 + x1, 1e-12) * P - s,
        ],
        axis=1,
    )
    return cost, Gm


def gear_train(X: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    X = np.atleast_2d(X)
    Z = np.round(np.clip(X, 12.0, 60.0))
    x1, x2, x3, x4 = Z[:, 0], Z[:, 1], Z[:, 2], Z[:, 3]
    cost = (1.0 / 6.931 - x1 * x2 / (x3 * x4)) ** 2
    Gm = np.zeros((X.shape[0], 0))
    return cost, Gm


def cantilever_beam(X: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    X = np.atleast_2d(X)
    cost = 0.0624 * X.sum(axis=1)
    g = (
        61.0 / X[:, 0] ** 3
        + 37.0 / X[:, 1] ** 3
        + 19.0 / X[:, 2] ** 3
        + 7.0 / X[:, 3] ** 3
        + 1.0 / X[:, 4] ** 3
        - 1.0
    )
    return cost, g[:, None]


#: name -> (fn, lb, ub, D, f_ref)
_SPECS: dict[str, tuple[Callable, np.ndarray, np.ndarray, int, float]] = {
    "WeldedBeam": (welded_beam, np.array([0.1, 0.1, 0.1, 0.1]), np.array([2.0, 10.0, 10.0, 2.0]), 4, 1.7249),
    "Spring": (spring, np.array([0.05, 0.25, 2.0]), np.array([2.0, 1.3, 15.0]), 3, 0.012665),
    "PressureVessel": (
        pressure_vessel,
        np.array([0.0625, 0.0625, 10.0, 10.0]),
        np.array([6.1875, 6.1875, 200.0, 240.0]),
        4,
        5885.33,
    ),
    "SpeedReducer": (
        speed_reducer,
        np.array([2.6, 0.7, 17.0, 7.3, 7.3, 2.9, 5.0]),
        np.array([3.6, 0.8, 28.0, 8.3, 8.3, 3.9, 5.5]),
        7,
        2994.47,
    ),
    "ThreeBarTruss": (three_bar_truss, np.array([0.0, 0.0]), np.array([1.0, 1.0]), 2, 263.8958),
    "GearTrain": (
        gear_train,
        np.array([12.0, 12.0, 12.0, 12.0]),
        np.array([60.0, 60.0, 60.0, 60.0]),
        4,
        2.7e-12,
    ),
    "CantileverBeam": (
        cantilever_beam,
        np.array([0.01, 0.01, 0.01, 0.01, 0.01]),
        np.array([100.0, 100.0, 100.0, 100.0, 100.0]),
        5,
        1.33996,
    ),
}

IMPLEMENTATION = "tfo_bench-port-of-sibling@96af96b"


def build_problems() -> dict[str, Problem]:
    problems: dict[str, Problem] = {}
    for name, (raw_fn, lb, ub, D, f_ref) in _SPECS.items():

        def make_penalized_fn(fn=raw_fn):
            def penalized(X: np.ndarray) -> np.ndarray:
                cost, G = fn(X)
                return _penalize(np.asarray(cost, dtype=float), np.asarray(G, dtype=float))

            return penalized

        def make_constraints_fn(fn=raw_fn):
            def constraints(X: np.ndarray) -> np.ndarray:
                _cost, G = fn(X)
                return np.asarray(G, dtype=float)

            return constraints

        problems[name] = Problem(
            problem_id=f"engineering_{name}",
            suite="engineering",
            name=name,
            D=D,
            lb=lb,
            ub=ub,
            f_star=f_ref,
            fn=make_penalized_fn(),
            x_star=None,  # literature x_ref is used by the preflight (audit.py), not stored here
            implementation=IMPLEMENTATION,
            has_constraints=True,
            constraints_fn=make_constraints_fn(),
        )
    return problems


#: Exposed for the golden test and the audit module (raw (cost, G) functions, pre-penalty).
RAW_FUNCTIONS: dict[str, Callable] = {
    "WeldedBeam": welded_beam,
    "Spring": spring,
    "PressureVessel": pressure_vessel,
    "SpeedReducer": speed_reducer,
    "ThreeBarTruss": three_bar_truss,
    "GearTrain": gear_train,
    "CantileverBeam": cantilever_beam,
}
SPECS = _SPECS
