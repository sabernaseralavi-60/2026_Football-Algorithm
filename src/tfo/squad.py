"""Squad (structure-of-arrays), Ball, KeeperArchive, TabuRegister (data-model.md A1, A2, A4-A6)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Mapping, Optional, Sequence

import numpy as np

from tfo.registry import Archetype

# Depth ordering used to lay the RoleSheet out "by depth in row-major slot order": zonal
# centre-backs and wing-backs in the lowest slot indices, then midfield archetypes, then forward
# archetypes (data-model.md A2).
_DEPTH_ORDER: tuple[Archetype, ...] = (
    Archetype.ZONAL_CENTRE_BACK,
    Archetype.OVERLAPPING_WING_BACK,
    Archetype.DEEP_LYING_PLAYMAKER,
    Archetype.BOX_TO_BOX,
    Archetype.DESTROYER,
    Archetype.VIRTUOSO,
    Archetype.FINISHER,
)


def normalized_distance(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """Euclidean distance normalised by the box diagonal sqrt(D) (data-model.md Notation)."""
    d = a.shape[-1]
    return np.linalg.norm(a - b, axis=-1) / np.sqrt(d)


@dataclass
class RoleSheet:
    """slot index -> Archetype (or None for the vacancy). Fixed across formation re-lays (A2)."""

    _by_slot: tuple[Optional[Archetype], ...]

    def archetype_at(self, slot: int) -> Optional[Archetype]:
        return self._by_slot[slot]

    @property
    def n_slots(self) -> int:
        return len(self._by_slot)

    def slots_of(self, archetype: Archetype) -> tuple[int, ...]:
        """Ascending slot indices holding `archetype`."""
        return tuple(s for s, a in enumerate(self._by_slot) if a == archetype)

    def ordinal_within(self, archetype: Archetype, slot: int) -> int:
        """This slot's 0-based rank among all slots holding `archetype` (ascending slot index)."""
        return self.slots_of(archetype).index(slot)

    @classmethod
    def layout(cls, role_counts: Mapping[Archetype, int], n_slots: int) -> "RoleSheet":
        n_out = sum(role_counts.values())
        if n_out > n_slots:
            raise ValueError("role_counts total exceeds n_slots")
        ordered: list[Optional[Archetype]] = []
        for archetype in _DEPTH_ORDER:
            ordered.extend([archetype] * role_counts.get(archetype, 0))
        # Any archetype not in the canonical depth order (shouldn't happen with the closed
        # 8-member enum minus the keeper) is appended defensively.
        for archetype, count in role_counts.items():
            if archetype not in _DEPTH_ORDER:
                ordered.extend([archetype] * count)
        ordered.extend([None] * (n_slots - len(ordered)))
        return cls(tuple(ordered))


@dataclass
class Squad:
    """Structure-of-arrays population (data-model.md A1). Index 0 is the Sweeper-Keeper."""

    X: np.ndarray
    f: np.ndarray
    P: np.ndarray
    f_P: np.ndarray
    slot: np.ndarray
    stamina: np.ndarray
    stagnation: np.ndarray
    mesh: np.ndarray
    fin_fail: np.ndarray
    fin_last_restart: np.ndarray
    X_rev: np.ndarray
    f_rev: np.ndarray
    moved_since_rev: np.ndarray
    produced_best_since_rev: np.ndarray

    @property
    def n(self) -> int:
        return self.X.shape[0]

    @property
    def d(self) -> int:
        return self.X.shape[1]

    @classmethod
    def initialize(
        cls,
        n: int,
        d: int,
        rng: np.random.Generator,
        mesh_init: float,
        stamina_init: float = 1.0,
    ) -> "Squad":
        X = rng.random((n, d))
        f = np.full(n, np.inf)
        return cls(
            X=X,
            f=f.copy(),
            P=X.copy(),
            f_P=f.copy(),
            slot=np.arange(-1, n - 1, dtype=int),  # slot[0] = -1 (keeper); 0..n_out-1 outfield
            stamina=np.full(n, stamina_init),
            stagnation=np.zeros(n, dtype=int),
            mesh=np.full(n, mesh_init),
            fin_fail=np.zeros(n, dtype=int),
            fin_last_restart=np.full(n, -1, dtype=int),
            X_rev=X.copy(),
            f_rev=f.copy(),
            moved_since_rev=np.zeros(n, dtype=bool),
            produced_best_since_rev=np.zeros(n, dtype=bool),
        )

    def set_initial_fitness(self, f: np.ndarray) -> None:
        self.f[:] = f
        self.f_P[:] = f
        self.P[:] = self.X
        self.X_rev[:] = self.X
        self.f_rev[:] = f

    def update_agent(self, i: int, x_new: np.ndarray, f_new: float) -> bool:
        """Write agent i's current position/fitness and its personal best if improved.

        Returns True iff this is a personal-best improvement.
        """
        self.X[i] = x_new
        self.f[i] = f_new
        self.moved_since_rev[i] = True
        improved = f_new <= self.f_P[i]
        if improved:
            self.P[i] = x_new
            self.f_P[i] = f_new
            self.stagnation[i] = 0
        else:
            self.stagnation[i] += 1
        return improved

    def rollback(self, i: int) -> None:
        """VAR rollback (A12): restore the last-review snapshot at no evaluation cost."""
        self.X[i] = self.X_rev[i]
        self.f[i] = self.f_rev[i]

    def refresh_review_snapshot(self) -> None:
        self.X_rev[:] = self.X
        self.f_rev[:] = self.f
        self.moved_since_rev[:] = False
        self.produced_best_since_rev[:] = False

    def validate(self) -> None:
        """Assertions for the data-model.md A1 validation rules (used by tests and sanity checks)."""
        assert np.all(self.X >= 0.0) and np.all(self.X <= 1.0), "X must lie in [0, 1]^D"
        assert np.all(self.f_P <= self.f + 1e-12), "f_P[i] <= f[i] for every i"


@dataclass
class Ball:
    """data-model.md A4."""

    x_b: np.ndarray
    f_b: float
    carrier: int
    passes_tried: int = 0
    passes_retained: int = 0
    neutral_streak: int = 0
    lost_streak: int = 0


class KeeperArchive:
    """Sweeper-Keeper's bounded, distance-diverse archive (data-model.md A5)."""

    def __init__(self, k: int, min_sep: float, d: int):
        self.k = max(1, k)
        self.min_sep = min_sep
        self.d = d
        self.A: np.ndarray = np.zeros((0, d))
        self.f_A: np.ndarray = np.zeros((0,))

    @property
    def size(self) -> int:
        return self.f_A.shape[0]

    def _append(self, x: np.ndarray, f: float) -> None:
        self.A = np.vstack([self.A, x[None, :]])
        self.f_A = np.append(self.f_A, f)

    def on_evaluation(self, x: np.ndarray, f: float, is_new_incumbent: bool) -> None:
        """Update the archive on every account evaluation (mechanism-interface.md §2.1)."""
        if is_new_incumbent:
            if self.size == 0:
                self._append(x, f)
            else:
                self.A[0] = x
                self.f_A[0] = f
            return
        if self.k <= 1 or self.size == 0:
            # Disabled (K = 1): incumbent only; A[0] is maintained solely via is_new_incumbent.
            return
        dists = normalized_distance(self.A, x)
        within = dists < self.min_sep
        if np.any(within):
            idx = int(np.argmin(dists))
            if f < self.f_A[idx]:
                self.A[idx] = x
                self.f_A[idx] = f
            return
        if self.size < self.k:
            self._append(x, f)
            return
        worst_idx = int(np.argmax(self.f_A))
        if f < self.f_A[worst_idx]:
            self.A[worst_idx] = x
            self.f_A[worst_idx] = f

    def elite_other_than(self, rng: np.random.Generator, exclude_idx: int) -> tuple[np.ndarray, int]:
        """A random archive elite different from `exclude_idx` (ball reset / Finisher restart)."""
        if self.size <= 1:
            return self.A[0].copy(), 0
        choices = [i for i in range(self.size) if i != exclude_idx]
        idx = int(rng.choice(choices))
        return self.A[idx].copy(), idx


class TabuRegister:
    """FIFO tabu-zone register (data-model.md A6)."""

    def __init__(self, t_max: int, r_tabu: float, d: int):
        self.t_max = t_max
        self.r_tabu = r_tabu
        self.d = d
        self._centres: list[np.ndarray] = []

    def __len__(self) -> int:
        return len(self._centres)

    def add(self, x: np.ndarray) -> None:
        self._centres.append(np.array(x, copy=True))
        if len(self._centres) > self.t_max:
            self._centres.pop(0)

    def is_tabu(self, x: np.ndarray) -> bool:
        if not self._centres:
            return False
        centres = np.stack(self._centres)
        return bool(np.any(normalized_distance(centres, x) < self.r_tabu))
