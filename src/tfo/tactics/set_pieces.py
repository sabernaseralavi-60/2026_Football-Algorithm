"""Set pieces (mechanism-interface.md §2.14, FR-017).

Operator: every c iterations, run on the incumbent, following a fixed script that alternates
corner, free kick, corner, free kick, and so on.

- Corner: pick a random coordinate pair (j, k) and evaluate the 3x3 orthogonal design over
  {x-h, x, x+h} on those two coordinates: 8 new points.
- Free kick: pick a random unit direction d, evaluate x +/- h*d, and evaluate the vertex of the
  parabola through the three points when it is convex: up to 3 points.

Improvements go to the archive through the account (Fixed-frequency memetic local search:
orthogonal-design sampling, successive parabolic interpolation; Leung & Wang 2001; Brent 1973).
"""

from __future__ import annotations

import numpy as np

from tfo.registry import MechanismTag
from tfo.tactics import offside

_OFFSETS = (-1, 0, 1)


def corner(ctx, rng: np.random.Generator) -> None:
    x = ctx.account.x_best.copy()
    d = x.shape[0]
    if d < 2:
        return  # a coordinate PAIR is not defined in 1-D; nothing to probe
    j, k = rng.choice(d, size=2, replace=False)
    h = ctx.cfg.operators.set_piece_h

    points = []
    for dj in _OFFSETS:
        for dk in _OFFSETS:
            if dj == 0 and dk == 0:
                continue  # the centre point (x itself) is already known; not re-evaluated
            y = x.copy()
            y[j] = y[j] + dj * h
            y[k] = y[k] + dk * h
            points.append(offside.repair(y, x, rng))
    Y = np.stack(points, axis=0)
    ctx.account.evaluate(Y, MechanismTag.SET_PIECES)


def free_kick(ctx, rng: np.random.Generator) -> None:
    x = ctx.account.x_best.copy()
    d = x.shape[0]
    direction = rng.standard_normal(d)
    norm = np.linalg.norm(direction)
    if norm < 1e-12:
        direction = np.zeros(d)
        direction[0] = 1.0
    else:
        direction = direction / norm

    h = ctx.cfg.operators.set_piece_h
    f0 = ctx.account.f_best  # x is the incumbent, so f_best already equals f(x); capture it
    # BEFORE evaluating x +/- h*d, since those calls may themselves update f_best.
    y_minus = offside.repair(x - h * direction, x, rng)
    y_plus = offside.repair(x + h * direction, x, rng)
    f = ctx.account.evaluate(np.stack([y_minus, y_plus]), MechanismTag.SET_PIECES)
    f_minus, f_plus = float(f[0]), float(f[1])

    denom = f_minus + f_plus - 2.0 * f0
    if denom > 0.0:
        t_star = h * (f_minus - f_plus) / (2.0 * denom)
        y_vertex = offside.repair(x + t_star * direction, x, rng)
        ctx.account.evaluate(y_vertex[None, :], MechanismTag.SET_PIECES)


def apply(call_index: int, ctx, rng: np.random.Generator) -> None:
    """The fixed schedule: corner on even call indices, free kick on odd ones. Never adapted."""
    if call_index % 2 == 0:
        corner(ctx, rng)
    else:
        free_kick(ctx, rng)
