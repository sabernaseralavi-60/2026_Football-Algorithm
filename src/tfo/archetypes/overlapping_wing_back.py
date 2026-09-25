"""Overlapping Wing-Back (mechanism-interface.md §2.3, FR-007).

Operator: with probability Jr (the manager scales this rate in CHASING), take the quasi-opposite
point about the squad centroid c: o = 2c - x, then y = c + U(0, 1) (o - c). Keep the better of x
and y. With probability 1 - Jr, apply the neutral move N (Quasi-opposition-based learning,
generation jumping; Tizhoosh 2005; Rahnamayan et al. 2007).
"""

from __future__ import annotations

import numpy as np

from tfo import neutral
from tfo.registry import MechanismTag
from tfo.tactics import offside


def squad_centroid(X_outfield: np.ndarray) -> np.ndarray:
    return X_outfield.mean(axis=0)


def quasi_opposite_jump(c: np.ndarray, x: np.ndarray, rng: np.random.Generator) -> np.ndarray:
    o = 2.0 * c - x
    u = rng.random(c.shape)
    return c + u * (o - c)


def move(i: int, ctx, rng: np.random.Generator) -> None:
    jr = ctx.cfg.operators.jump_rate
    rate_mult = 1.0
    state_params = getattr(ctx, "state_params", None)
    if state_params is not None:
        rate_mult = state_params.rate_multipliers.get("overlapping_wing_back", 1.0)
    jr_effective = min(1.0, jr * rate_mult)

    x_i = ctx.squad.X[i]
    if rng.random() < jr_effective:
        outfield = ctx.squad.X[1:] if ctx.squad.X.shape[0] > 1 else ctx.squad.X
        c = squad_centroid(outfield)
        y = quasi_opposite_jump(c, x_i, rng)
    else:
        y = neutral.propose(x_i, ctx.cfg.operators.neutral_sigma, ctx.squad.stamina[i], rng)

    y = offside.repair(y, x_i, rng)
    f_y = float(ctx.account.evaluate(y[None, :], MechanismTag.OVERLAPPING_WING_BACK)[0])
    if f_y <= ctx.squad.f[i]:
        ctx.squad.update_agent(i, y, f_y)
