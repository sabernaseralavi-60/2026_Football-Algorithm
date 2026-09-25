"""Possession (mechanism-interface.md §2.11, FR-014).

Operator: a chain of up to L passes. Each pass picks a receiver q from N(carrier) and proposes
x_b' = x_b + U(0, 1)*(x_q - x_b). The pass is retained if f(x_b') <= f_b + tau. The chain ends on a
lost pass, or once N_neutral_max consecutive neutral passes are reached. After R_loss consecutive
lost chains, the ball resets to an archive elite, and the location it leaves goes on the tabu list
(Threshold accepting; Dueck & Scheuer 1990; tau = 0 gives non-regression with neutral drift).
"""

from __future__ import annotations

import numpy as np

from tfo.registry import MechanismTag
from tfo.tactics import offside

_NEUTRAL_TOL = 1e-12


def _slot_to_agent(squad) -> dict[int, int]:
    return {int(s): i for i, s in enumerate(squad.slot) if s >= 0}


def apply(ctx, rng: np.random.Generator) -> None:
    squad = ctx.squad
    ball = ctx.ball
    formation = ctx.formation
    tau = ctx.state_params.tau
    chain_length = ctx.state_params.chain_length
    neutral_max = ctx.cfg.operators.neutral_pass_max
    lost_streak_max = ctx.cfg.operators.lost_streak_max

    slot_to_agent = _slot_to_agent(squad)
    carrier_slot = int(squad.slot[ball.carrier])
    neutral_streak = 0
    chain_lost = False

    for _ in range(chain_length):
        neighbours = formation.neighbours[carrier_slot]
        if not neighbours:
            break
        q_slot = int(rng.choice(neighbours))
        q_idx = slot_to_agent[q_slot]
        x_q = squad.X[q_idx]

        u = rng.random(squad.d)
        candidate = ball.x_b + u * (x_q - ball.x_b)
        candidate = offside.repair(candidate, ball.x_b, rng)
        f_candidate = float(ctx.account.evaluate(candidate[None, :], MechanismTag.POSSESSION)[0])

        ball.passes_tried += 1
        if f_candidate <= ball.f_b + tau:
            ball.passes_retained += 1
            if abs(f_candidate - ball.f_b) < _NEUTRAL_TOL:
                neutral_streak += 1
            else:
                neutral_streak = 0
            ball.x_b = candidate
            ball.f_b = f_candidate
            ball.carrier = q_idx
            carrier_slot = q_slot
            if neutral_streak >= neutral_max:
                break
        else:
            chain_lost = True
            break

    if chain_lost:
        ball.lost_streak += 1
    else:
        ball.lost_streak = 0

    if ball.lost_streak >= lost_streak_max:
        old_location = ball.x_b.copy()
        elite, _ = ctx.archive.elite_other_than(rng, exclude_idx=-1)
        ball.x_b = elite
        ball.f_b = float(ctx.account.evaluate(elite[None, :], MechanismTag.POSSESSION)[0])
        ctx.tabu.add(old_location)
        ball.lost_streak = 0


def apply_disabled(ball, squad) -> None:
    """Disabled default: the ball is not passed. It stays a focal point, set to the best outfield
    agent at 0 evals every iteration."""
    best_idx = int(np.argmin(squad.f))
    ball.x_b = squad.X[best_idx].copy()
    ball.f_b = float(squad.f[best_idx])
    ball.carrier = best_idx
