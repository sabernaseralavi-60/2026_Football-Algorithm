"""Offside line: bound repair and the (epsilon-experiment-only) epsilon-line (mechanism-interface.md
§2.15, FR-018).

Implemented here (ahead of tasks.md's own §2.3 position) because every archetype's `move()` calls
`repair()` on its own proposal before evaluating it ("Candidate proposals... Every proposal passes
through offside.repair(x_new, x_old) before it is evaluated", mechanism-interface.md §1), so the
archetypes structurally depend on this module.

Scope note: the epsilon-line and epsilon-lexicographic comparison are implemented and unit-tested
here (their primitives are part of mechanism #15's contract), but wiring a constraint-violation
vector through every one of the other 18 mechanisms' greedy-accept comparisons -- which only
matters for the epsilon experiment's constrained problems -- is not done, because that experiment
(`tests/.../run_epsilon.py`, `src/tfo_bench`) is explicitly out of scope for this pass. Every
mechanism in this pass compares candidates on plain fitness.
"""

from __future__ import annotations

import numpy as np


def repair(y: np.ndarray, x_old: np.ndarray, rng: np.random.Generator) -> np.ndarray:
    """y_j <- x_old,j + U(0,1)*(bound_j - x_old,j) for every coordinate j outside [0, 1]."""
    y = np.array(y, dtype=float, copy=True)
    x_old = np.asarray(x_old, dtype=float)
    u = rng.random(y.shape)

    below = y < 0.0
    above = y > 1.0
    y[below] = x_old[below] + u[below] * (0.0 - x_old[below])
    y[above] = x_old[above] + u[above] * (1.0 - x_old[above])
    return y


def clip(y: np.ndarray) -> np.ndarray:
    """Disabled neutral default: plain clipping to [0, 1]^D."""
    return np.clip(y, 0.0, 1.0)


def epsilon(t: float, eps0: float, t_c: float, cp: float) -> float:
    """epsilon(t) = eps0 * (1 - t/T_c)^cp for t < T_c, else 0 (Takahama & Sakai 2006)."""
    if t >= t_c:
        return 0.0
    return eps0 * (1.0 - t / t_c) ** cp


def epsilon_lex_better(f_a: float, v_a: float, f_b: float, v_b: float, eps: float) -> str:
    """epsilon-lexicographic order on (f, v): returns "a" or "b", whichever is preferred.

    Both feasible-enough (violation <= eps): compare on f. Otherwise compare on violation first.
    """
    a_ok = v_a <= eps
    b_ok = v_b <= eps
    if a_ok and b_ok:
        return "a" if f_a <= f_b else "b"
    if a_ok != b_ok:
        return "a" if a_ok else "b"
    if v_a != v_b:
        return "a" if v_a < v_b else "b"
    return "a" if f_a <= f_b else "b"
