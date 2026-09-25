"""Finisher (mechanism-interface.md §2.8, FR-012).

Operator: y = x_b + sigma_L * s_i * Levy(beta), a step with Mantegna's heavy-tailed distribution
centred on the ball, accepted greedily. After F_fail consecutive failures, restart from an archive
elite e != the previous restart point, with a small Gaussian offset (Levy-flight (heavy-tailed)
mutation with elite restart; Lee & Yao 2004; Mantegna 1994).
"""

from __future__ import annotations

import math

import numpy as np

from tfo.registry import MechanismTag
from tfo.tactics import offside

_RESTART_OFFSET_SIGMA = 0.01  # judgment call: "a small Gaussian offset" on restart


def levy_step(beta: float, size: int, rng: np.random.Generator) -> np.ndarray:
    """Mantegna's algorithm for symmetric Levy-stable steps."""
    num = math.gamma(1 + beta) * math.sin(math.pi * beta / 2)
    den = math.gamma((1 + beta) / 2) * beta * 2 ** ((beta - 1) / 2)
    sigma_u = (num / den) ** (1 / beta)
    u = rng.normal(0.0, sigma_u, size)
    v = rng.normal(0.0, 1.0, size)
    return u / np.abs(v) ** (1.0 / beta)


def move(i: int, ctx, rng: np.random.Generator) -> None:
    squad = ctx.squad
    ball = ctx.ball
    ops = ctx.cfg.operators

    step = levy_step(ops.levy_beta, squad.d, rng)
    y = ball.x_b + ops.levy_sigma * squad.stamina[i] * step
    y = offside.repair(y, squad.X[i], rng)
    f_y = float(ctx.account.evaluate(y[None, :], MechanismTag.FINISHER)[0])

    if f_y <= squad.f[i]:
        squad.update_agent(i, y, f_y)
        squad.fin_fail[i] = 0
    else:
        squad.fin_fail[i] += 1

    if squad.fin_fail[i] >= ops.finisher_fail_limit:
        elite, elite_idx = ctx.archive.elite_other_than(rng, int(squad.fin_last_restart[i]))
        y2 = elite + rng.normal(0.0, _RESTART_OFFSET_SIGMA, elite.shape)
        y2 = offside.clip(y2)
        f_y2 = float(ctx.account.evaluate(y2[None, :], MechanismTag.FINISHER)[0])
        squad.update_agent(i, y2, f_y2)  # a restart is taken unconditionally
        squad.fin_fail[i] = 0
        squad.fin_last_restart[i] = elite_idx
