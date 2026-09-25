"""Formation: the pitch lattice (mechanism-interface.md §2.9, FR-013, FR-002; data-model.md A3).

Implemented ahead of tasks.md's own §2.3 position because the Deep-Lying Playmaker, Box-to-Box
Engine and Destroyer archetypes (§2.2) need `graph_dist`/`neighbours` to define their partners and
donors.
"""

from __future__ import annotations

import math
from collections import deque
from dataclasses import dataclass

import numpy as np

#: Shapes for n = 30 (data-model.md A3): name -> (lines, lanes). One vacancy each (30 - 29 = 1).
SHAPES_N30: dict[str, tuple[int, int]] = {
    "compact": (5, 6),
    "balanced": (3, 10),
    "stretched": (2, 15),
}


def _row_major_coords(lines: int, lanes: int) -> np.ndarray:
    rc = np.empty((lines * lanes, 2), dtype=int)
    for r in range(lines):
        for c in range(lanes):
            rc[r * lanes + c] = (r, c)
    return rc


def _von_neumann_neighbours_torus(
    lines: int, lanes: int, vacant: np.ndarray
) -> list[list[int]]:
    def idx(r: int, c: int) -> int:
        return (r % lines) * lanes + (c % lanes)

    neighbours: list[list[int]] = [[] for _ in range(lines * lanes)]
    for r in range(lines):
        for c in range(lanes):
            s = idx(r, c)
            if vacant[s]:
                continue
            for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                t = idx(r + dr, c + dc)
                if t != s and not vacant[t]:
                    neighbours[s].append(t)
    return neighbours


def _bfs_graph_dist(n_slots: int, neighbours: list[list[int]], vacant: np.ndarray) -> np.ndarray:
    dist = np.full((n_slots, n_slots), -1, dtype=int)
    for src in range(n_slots):
        if vacant[src]:
            continue
        dist[src, src] = 0
        q = deque([src])
        while q:
            u = q.popleft()
            for v in neighbours[u]:
                if dist[src, v] == -1:
                    dist[src, v] = dist[src, u] + 1
                    q.append(v)
    return dist


@dataclass(frozen=True)
class Formation:
    name: str
    lines: int
    lanes: int
    slot_rc: np.ndarray  # (S, 2)
    vacant: np.ndarray  # (S,)
    neighbours: list[list[int]]  # ragged, per slot
    graph_dist: np.ndarray  # (S, S)
    ratio: float
    fully_connected: bool = False

    @property
    def n_slots(self) -> int:
        return self.lines * self.lanes

    @classmethod
    def build(cls, name: str, n_out: int, fully_connected: bool = False) -> "Formation":
        if name not in SHAPES_N30:
            raise ValueError(f"unknown formation shape {name!r}")
        lines, lanes = SHAPES_N30[name]
        s = lines * lanes
        vacancies = s - n_out
        if not (0 <= vacancies < lanes):
            raise ValueError("Vacancies = lines * lanes - n_out must satisfy 0 <= vacancies < lanes")

        slot_rc = _row_major_coords(lines, lanes)
        vacant = np.zeros(s, dtype=bool)
        if vacancies > 0:
            vacant[s - vacancies :] = True  # last `vacancies` cells of the last row

        if fully_connected:
            filled = [i for i in range(s) if not vacant[i]]
            neighbours = [[] for _ in range(s)]
            for i in filled:
                neighbours[i] = [j for j in filled if j != i]
            graph_dist = np.zeros((s, s), dtype=int)
            for i in filled:
                for j in filled:
                    graph_dist[i, j] = 0 if i == j else 1
        else:
            neighbours = _von_neumann_neighbours_torus(lines, lanes, vacant)
            graph_dist = _bfs_graph_dist(s, neighbours, vacant)

        # Neighbourhood-radius / grid-radius ratio (Alba & Dorronsoro 2005). The von Neumann
        # neighbourhood radius is 1; the grid radius is approximated by the radius of the circle
        # of equal area to the lines x lanes rectangle's circumscribed ellipse-like extent,
        # R = sqrt(lines^2 + lanes^2) / pi, which reproduces data-model.md A3's three reference
        # values (0.403, 0.300, 0.206) to within rounding.
        grid_radius = math.sqrt(lines**2 + lanes**2) / math.pi
        ratio = 1.0 / grid_radius

        return cls(
            name=name,
            lines=lines,
            lanes=lanes,
            slot_rc=slot_rc,
            vacant=vacant,
            neighbours=neighbours,
            graph_dist=graph_dist,
            ratio=ratio,
            fully_connected=fully_connected,
        )

    def row_of(self, slot: int) -> int:
        return int(self.slot_rc[slot, 0])
