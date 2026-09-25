"""Counter-attack (mechanism-interface.md §2.13, FR-016).

Operator: triggered by an event, the same in TFO and TFO-static. The event is an accepted off-ball
move with f(y) < f_b - Delta_mat*max(|f_b|, 1e-12) and ||y - x_b|| > d_trans. The ball moves to y;
the old ball location becomes tabu. Each agent in the attacking line (the last row) then makes a
burst of burst_len steps: y_k = x_b + s0*gamma^k*N(0, I), accepted greedily, and the ball is
updated whenever a step improves on it (Event-triggered basin hopping / iterated-local-search
relocation; Wales & Doye 1997; Lourenco et al. 2003).
"""

from __future__ import annotations

import numpy as np

from tfo.registry import MechanismTag
from tfo.squad import normalized_distance
from tfo.tactics import offside


def check_trigger(y: np.ndarray, f_y: float, ball, ops) -> bool:
    improved_enough = f_y < ball.f_b - ops.counter_attack_delta_mat * max(abs(ball.f_b), 1e-12)
    far_enough = float(normalized_distance(y, ball.x_b)) > ops.counter_attack_d_trans
    return improved_enough and far_enough


def burst_step_scale(k: int, s0: float, gamma: float) -> float:
    return s0 * (gamma**k)


def _attacking_line_agents(formation, squad) -> list[int]:
    last_row = formation.lines - 1
    slot_to_agent = {int(s): i for i, s in enumerate(squad.slot) if s >= 0}
    return [
        agent
        for slot, agent in slot_to_agent.items()
        if formation.row_of(slot) == last_row
    ]


def fire(i: int, y: np.ndarray, f_y: float, ctx, rng: np.random.Generator) -> None:
    """Relocate the ball to (y, f_y) and run the attacking-line burst. Raises `BudgetExhausted`
    (propagated from `ctx.account.evaluate`) exactly when the shared budget runs out mid-burst."""
    ball = ctx.ball
    old_location = ball.x_b.copy()
    ball.x_b = np.array(y, copy=True)
    ball.f_b = f_y
    ball.carrier = i
    ctx.tabu.add(old_location)

    ops = ctx.cfg.operators
    squad = ctx.squad
    for agent in _attacking_line_agents(ctx.formation, squad):
        x_a = squad.X[agent]
        for k in range(ops.burst_len):
            scale = burst_step_scale(k, ops.burst_s0, ops.burst_gamma)
            y_k = x_a + scale * rng.standard_normal(squad.d)
            y_k = offside.repair(y_k, x_a, rng)
            f_yk = float(ctx.account.evaluate(y_k[None, :], MechanismTag.COUNTER_ATTACK)[0])
            if f_yk <= squad.f[agent]:
                squad.update_agent(agent, y_k, f_yk)
                x_a = y_k
            if f_yk < ball.f_b:
                ball.x_b = y_k.copy()
                ball.f_b = f_yk
                ball.carrier = agent


def check_and_fire(i: int, y: np.ndarray, f_y: float, ctx, rng: np.random.Generator) -> bool:
    if not check_trigger(y, f_y, ctx.ball, ctx.cfg.operators):
        return False
    fire(i, y, f_y, ctx, rng)
    return True
