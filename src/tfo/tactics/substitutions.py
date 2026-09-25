"""Substitutions (mechanism-interface.md §2.16, FR-019).

Operator: an agent with stagnation >= W and stamina < s_sub is replaced by u ~ U[0, 1]^D, with
stamina 1 and fresh counters and mesh, up to the cap for the current fixture. CHASING raises the
cap by a bounded increment. The outgoing position goes on the tabu list (Stagnation-triggered
random immigrants, capped; Grefenstette 1992).
"""

from __future__ import annotations

import numpy as np

from tfo.registry import MechanismTag


def apply(
    ctx, rng: np.random.Generator, cap_override: int | None = None, start_index: int = 0
) -> list[int]:
    """Substitute eligible agents, up to the cap. `start_index` excludes the keeper (index 0) when
    called on the real Squad (engine.py passes `start_index=1`); it defaults to 0 so this function
    is directly unit-testable on a squad of outfield-only agents."""
    squad = ctx.squad
    ops = ctx.cfg.operators
    cap = cap_override if cap_override is not None else ops.substitution_cap

    eligible = [
        i
        for i in range(start_index, squad.X.shape[0])
        if squad.stagnation[i] >= ops.substitution_window
        and squad.stamina[i] < ops.stamina_sub_threshold
    ]

    substituted: list[int] = []
    for i in eligible:
        if len(substituted) >= cap:
            break
        outgoing = squad.X[i].copy()
        ctx.tabu.add(outgoing)

        u = rng.random(squad.d)
        f_u = float(ctx.account.evaluate(u[None, :], MechanismTag.SUBSTITUTIONS)[0])
        squad.X[i] = u
        squad.f[i] = f_u
        squad.P[i] = u
        squad.f_P[i] = f_u
        squad.stamina[i] = 1.0
        squad.stagnation[i] = 0
        squad.mesh[i] = ops.mesh_h_init
        squad.fin_fail[i] = 0
        squad.fin_last_restart[i] = -1
        substituted.append(i)

    return substituted
