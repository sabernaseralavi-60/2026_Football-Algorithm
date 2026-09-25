"""Formation: the pitch lattice (mechanism-interface.md §2.9, FR-013, FR-002; data-model.md A3).

Implemented ahead of tasks.md's own §2.3 position because the Deep-Lying Playmaker, Box-to-Box
Engine and Destroyer archetypes (§2.2) need `graph_dist`/`neighbours` to define their partners and
donors.
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass

import numpy as np

#: Shapes for n = 30 (data-model.md A3): name -> (lines, lanes). One vacancy each (30 - 29 = 1).
SHAPES_N30: dict[str, tuple[int, int]] = {
    "compact": (5, 6),
    "balanced": (3, 10),
    "stretched": (2, 15),
}


#: Offsets of the von Neumann (NEWS / "L5") neighbourhood, centre included.
_VON_NEUMANN_L5: tuple[tuple[int, int], ...] = ((0, 0), (-1, 0), (1, 0), (0, -1), (0, 1))


def dispersion_radius(points: np.ndarray) -> float:
    """Radius of a set of 2-D cells: root-mean-square distance to their centroid,

        rad = sqrt( sum_i [(x_i - x_bar)^2 + (y_i - y_bar)^2] / n ).

    This is the dispersion measure of Sarma & De Jong (1996), used for neighbourhoods and grids
    in cellular EAs by Alba & Troya (2000) and Alba & Dorronsoro (2005, IEEE TEVC 9(2):126-142,
    doi:10.1109/TEVC.2005.843751).
    """
    pts = np.asarray(points, dtype=float)
    centred = pts - pts.mean(axis=0)
    return float(np.sqrt(np.sum(centred**2) / len(pts)))


def cellular_ratio(lines: int, lanes: int) -> float:
    """Alba & Dorronsoro (2005) ratio: rad(von Neumann L5 neighbourhood) / rad(lines x lanes grid).

    rad(L5) = sqrt(4/5) = 0.894. For a full r x c grid the closed form is
    rad = sqrt(((r^2 - 1) + (c^2 - 1)) / 12). The grid radius is a property of the lattice, so it
    is taken over every cell of the lines x lanes grid, vacant slots included. The formula
    reproduces the paper's own values for 400 cells (20x20: 0.110, 10x40: 0.075, 4x100: 0.031) and
    data-model.md A3's values for n = 30 (5x6: 0.403, 3x10: 0.300, 2x15: 0.206).
    """
    grid = _row_major_coords(lines, lanes)
    return dispersion_radius(np.array(_VON_NEUMANN_L5)) / dispersion_radius(grid)


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

        ratio = cellular_ratio(lines, lanes)

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
