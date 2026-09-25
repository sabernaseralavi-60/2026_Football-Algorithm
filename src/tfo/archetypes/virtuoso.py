"""Virtuoso (mechanism-interface.md §2.7, FR-011).

Operator: a compass poll. Choose k coordinates in random order. For each, poll x +/- h_i*e_j in
turn and accept the first improvement. On success, h_i <- min(2 h_i, h_max). If the whole poll
fails, h_i <- max(h_i/2, h_min) (Compass / generalized pattern search; Hooke & Jeeves 1961;
Torczon 1997).
"""

from __future__ import annotations

import numpy as np

from tfo.registry import MechanismTag
from tfo.tactics import offside


def move(i: int, ctx, rng: np.random.Generator) -> None:
    squad = ctx.squad
    x = squad.X[i]
    d = squad.d
    k = min(ctx.cfg.operators.mesh_k, d)
    h = squad.mesh[i]

    coords = rng.permutation(d)[:k]
    improved = False
    for j in coords:
        for sign in (1.0, -1.0):
            y = x.copy()
            y[j] = y[j] + sign * h
            y = offside.repair(y, x, rng)
            f_y = float(ctx.account.evaluate(y[None, :], MechanismTag.VIRTUOSO)[0])
            if f_y < squad.f[i]:
                squad.update_agent(i, y, f_y)
                improved = True
                break
        if improved:
            break

    if improved:
        squad.mesh[i] = min(2.0 * h, ctx.cfg.operators.mesh_h_max)
    else:
        squad.mesh[i] = max(h / 2.0, ctx.cfg.operators.mesh_h_min)
