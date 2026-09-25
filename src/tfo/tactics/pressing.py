"""Pressing (mechanism-interface.md §2.12, FR-015).

Operator: the pressing set P = {i : ||x_i - x_b|| < rho}, truncated to the floor(0.5*n_out) nearest
agents. Each i in P replaces its archetype move with y = x_b - A (elementwise) |C x_b - x_i|, where
A = 2a r1 - a, C = 2 r2, and a shrinks linearly with t. Accepted greedily (Distance-gated
shrinking-encircling attraction, cf. GWO/WOA encircling; Mirjalili et al. 2014).

Squad indexing convention (data-model.md A1): index 0 is the Sweeper-Keeper; membership is drawn
only from the outfield indices 1..n_out.
"""

from __future__ import annotations

import numpy as np

from tfo.registry import MechanismTag
from tfo.squad import normalized_distance
from tfo.tactics import offside


def membership(ctx) -> list[int]:
    squad = ctx.squad
    ball = ctx.ball
    rho = ctx.state_params.rho
    if rho <= 0.0:
        return []
    outfield_idx = np.arange(1, squad.n)
    dists = normalized_distance(squad.X[outfield_idx], ball.x_b)
    within_mask = dists < rho
    within = outfield_idx[within_mask]
    if within.size == 0:
        return []
    cap = int(np.floor(0.5 * squad.n_out))
    if within.size <= cap:
        return sorted(int(i) for i in within)
    d_within = dists[within_mask]
    order = np.argsort(d_within)[:cap]
    return sorted(int(within[k]) for k in order)


def step(i: int, ctx, rng: np.random.Generator) -> None:
    squad = ctx.squad
    ball = ctx.ball
    x_i = squad.X[i]
    x_b = ball.x_b

    a = 2.0 * (1.0 - ctx.clock.t)  # shrinks linearly with t, from 2 to 0 (GWO convention)
    r1 = rng.random(x_i.shape)
    r2 = rng.random(x_i.shape)
    A = 2.0 * a * r1 - a
    C = 2.0 * r2
    y = x_b - A * np.abs(C * x_b - x_i)

    y = offside.repair(y, x_i, rng)
    f_y = float(ctx.account.evaluate(y[None, :], MechanismTag.PRESSING)[0])
    if f_y <= squad.f[i]:
        squad.update_agent(i, y, f_y)
