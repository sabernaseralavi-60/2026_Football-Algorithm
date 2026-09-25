"""Unit tests for positional rotation (tasks.md T038; mechanism-interface.md §2.10)."""

from __future__ import annotations

from types import SimpleNamespace

import numpy as np

import tfo.tactics.rotation as rotation
from tfo.tactics.formation import Formation


def _slot_to_agent(squad):
    return {int(s): i for i, s in enumerate(squad.slot) if s >= 0}


class _FakeSquad:
    def __init__(self, n, slot, f):
        self.slot = np.array(slot)
        self.f = np.array(f)
        self.n = n


def test_only_better_deeper_worse_upfield_pairs_swap():
    formation = Formation.build("compact", n_out=29)
    n = 29
    slot = list(range(n))  # agent k occupies slot k
    f = np.zeros(n)
    # Lane 0: rows 0..4 are slots 0, 6, 12, 18, 24. Make row0 (deep) better than row1 (upfield).
    f[0] = 1.0  # slot 0 (row0, deep)
    f[6] = 5.0  # slot 6 (row1, upfield) -- worse
    # Another lane where the deep agent is NOT better: no swap expected there.
    f[1] = 9.0  # slot 1 (row0)
    f[7] = 2.0  # slot 7 (row1) -- better than deep, so no swap (rotation only swaps when deep is
    # strictly better than upfield)

    squad = _FakeSquad(n, slot, f)
    ctx = SimpleNamespace(squad=squad, formation=formation)
    rotation.apply(ctx)

    slot_to_agent_after = _slot_to_agent(squad)
    assert slot_to_agent_after[6] == 0, "the better deep agent advances to the upfield slot"
    assert slot_to_agent_after[0] == 6, "the worse upfield agent drops back"
    # Lane 1 unchanged: deep agent (1) was worse, so no swap.
    assert slot_to_agent_after[1] == 1
    assert slot_to_agent_after[7] == 7


def test_no_wrap_across_torus():
    formation = Formation.build("compact", n_out=29)
    n = 29
    slot = list(range(n))
    f = np.zeros(n)
    # Last row (row 4) vs "row 5" would wrap to row 0 on the torus; rotation must not compare them.
    f[24] = 0.0  # row4, lane0 -- best possible
    f[0] = 100.0  # row0, lane0 -- worst possible
    squad = _FakeSquad(n, slot, f)
    ctx = SimpleNamespace(squad=squad, formation=formation)
    rotation.apply(ctx)
    slot_to_agent_after = _slot_to_agent(squad)
    # If rotation wrapped, agent 24 (best, deepest row) would try to swap into row0's slot; it must
    # not, since row4 -> row0 is only reachable by wrapping.
    assert slot_to_agent_after[24] == 24
    assert slot_to_agent_after[0] == 0


def test_role_sheet_composition_preserved():
    """Rotation swaps `squad.slot` values only; RoleSheet itself (slot -> archetype) never
    changes, so the archetype *composition* across all slots is preserved (data-model.md A2)."""
    from tfo.registry import DEFAULT_ARCHETYPE_COUNTS
    from tfo.squad import RoleSheet

    sheet = RoleSheet.layout(DEFAULT_ARCHETYPE_COUNTS, n_slots=30)
    before = {s: sheet.archetype_at(s) for s in range(30)}

    formation = Formation.build("compact", n_out=29)
    slot = list(range(29))
    f = np.random.default_rng(0).random(29)
    squad = _FakeSquad(29, slot, f)
    ctx = SimpleNamespace(squad=squad, formation=formation)
    rotation.apply(ctx)

    after = {s: sheet.archetype_at(s) for s in range(30)}
    assert before == after, "RoleSheet (slot -> archetype) is never mutated by rotation"
