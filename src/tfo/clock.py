"""MatchClock: evaluation-driven fixtures and the iteration counter (data-model.md A7)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Optional


@dataclass
class MatchClock:
    budget: int
    n_fixtures: int
    fixture: int = 0
    iteration: int = 0
    evals_used: int = 0

    _rotation: Optional[Callable[[], None]] = field(default=None, repr=False)
    _zonal_redraw: Optional[Callable[[], None]] = field(default=None, repr=False)
    _stamina_recovery: Optional[Callable[[], None]] = field(default=None, repr=False)
    _substitution_cap_reset: Optional[Callable[[], None]] = field(default=None, repr=False)

    @property
    def t(self) -> float:
        """Budget fraction elapsed, evals_used / B, in [0, 1] (data-model.md A7)."""
        if self.budget <= 0:
            return 1.0
        return min(1.0, self.evals_used / self.budget)

    def on_boundary(
        self,
        rotation: Callable[[], None],
        zonal_redraw: Callable[[], None],
        stamina_recovery: Callable[[], None],
        substitution_cap_reset: Callable[[], None],
    ) -> None:
        self._rotation = rotation
        self._zonal_redraw = zonal_redraw
        self._stamina_recovery = stamina_recovery
        self._substitution_cap_reset = substitution_cap_reset

    def _fixture_target(self, k: int) -> float:
        return k * self.budget / self.n_fixtures

    def tick_iteration(self) -> None:
        self.iteration += 1

    def advance(self, evals: int) -> bool:
        """Charge `evals` evaluations; fire the boundary hooks if a fixture ends. Returns whether
        a boundary was crossed (data-model.md A7: "Fixture k ends at the first iteration end with
        evals_used >= k*B/n_fixtures").
        """
        self.evals_used += evals
        target = self._fixture_target(self.fixture + 1)
        crossed = self.fixture < self.n_fixtures and self.evals_used >= target
        if crossed:
            self.fixture += 1
            if self._rotation is not None:
                self._rotation()
            if self._zonal_redraw is not None:
                self._zonal_redraw()
            if self._stamina_recovery is not None:
                self._stamina_recovery()
            if self._substitution_cap_reset is not None:
                self._substitution_cap_reset()
        return crossed
