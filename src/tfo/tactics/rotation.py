"""Positional rotation (mechanism-interface.md §2.10, FR-022).

Operator: one deep-to-upfield pass per lane: if f(row r) < f(row r+1), with no wrap across the
torus, swap the two agents' slots, and so their archetypes (Rank-based role reassignment
restricted to graph neighbours; Janson & Middendorf 2005).
"""

from __future__ import annotations

from typing import Optional

import numpy as np


def apply(ctx, rng: Optional[np.random.Generator] = None) -> None:
    squad = ctx.squad
    formation = ctx.formation
    slot_to_agent = {int(s): i for i, s in enumerate(squad.slot) if s >= 0}

    for lane in range(formation.lanes):
        for row in range(formation.lines - 1):  # no wrap: never compares row (lines-1) to row 0
            slot_deep = row * formation.lanes + lane
            slot_upfield = (row + 1) * formation.lanes + lane
            if formation.vacant[slot_deep] or formation.vacant[slot_upfield]:
                continue
            agent_deep = slot_to_agent.get(slot_deep)
            agent_upfield = slot_to_agent.get(slot_upfield)
            if agent_deep is None or agent_upfield is None:
                continue
            if squad.f[agent_deep] < squad.f[agent_upfield]:
                squad.slot[agent_deep] = slot_upfield
                squad.slot[agent_upfield] = slot_deep
                slot_to_agent[slot_deep] = agent_upfield
                slot_to_agent[slot_upfield] = agent_deep
