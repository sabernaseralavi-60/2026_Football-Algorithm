"""The manager's tactical board (mechanism-interface.md §2.19, FR-023 to FR-026; data-model.md A8).

Operator: the four-state machine (BUILD_UP, CONTROL, HIGH_PRESS, CHASING), with EMA inputs,
priority guards, hysteresis and dwell. It sets the formation, rho, tau, L, the rate multipliers and
the substitution cap (Feedback-driven adaptive parameter control, state machine; Eiben et al.
1999).

Disablement (TFO-static): this module contains no enable/disable logic itself
(mechanism-interface.md §1); `engine.py` simply never calls `Manager.update()` when
`cfg.enable[manager]` is False, so the manager stays in its initial CONTROL state and CHASING can
never occur.
"""

from __future__ import annotations

import enum
from typing import Mapping

from tfo.config import ManagerConfig, StateParameterVector


class TacticalState(str, enum.Enum):
    BUILD_UP = "BUILD_UP"
    CONTROL = "CONTROL"
    HIGH_PRESS = "HIGH_PRESS"
    CHASING = "CHASING"


def _hysteresis(prev: bool, value: float, enter: float, exit_: float, direction: str) -> bool:
    """A boolean predicate with separate enter/exit thresholds (data-model.md A8 hysteresis)."""
    if direction == "below":
        return value < exit_ if prev else value < enter
    if direction == "above":
        return value > exit_ if prev else value > enter
    raise ValueError(direction)


class Manager:
    def __init__(self, cfg: ManagerConfig, states: Mapping[str, StateParameterVector]):
        self.cfg = cfg
        self.states = states
        self.state = TacticalState.CONTROL
        self.iters_in_state = 0

        self.div_ema: float | None = None
        self.poss_ema: float | None = None
        self.drought = 0

        self._div_low = False
        self._div_high = False
        self._poss_high = False

    def _decide(self, t: float) -> TacticalState:
        premature_collapse = self._div_low and t < self.cfg.t_late
        if self.drought >= self.cfg.g_max or premature_collapse:
            return TacticalState.CHASING
        if self._div_low and t >= self.cfg.t_press and self._poss_high:
            return TacticalState.HIGH_PRESS
        if self._div_high:
            return TacticalState.BUILD_UP
        return TacticalState.CONTROL

    def update(
        self, div: float, poss: float, material_improvement: bool, t: float
    ) -> StateParameterVector:
        """Read div/poss/drought/t (FR-023) and update the state (FR-024, FR-025)."""
        a_div = self.cfg.ema_alpha_div
        a_poss = self.cfg.ema_alpha_poss
        self.div_ema = div if self.div_ema is None else (1 - a_div) * self.div_ema + a_div * div
        self.poss_ema = poss if self.poss_ema is None else (1 - a_poss) * self.poss_ema + a_poss * poss

        self.drought = 0 if material_improvement else self.drought + 1

        self._div_low = _hysteresis(
            self._div_low, self.div_ema, self.cfg.d_low_enter, self.cfg.d_low_exit, "below"
        )
        self._div_high = _hysteresis(
            self._div_high, self.div_ema, self.cfg.d_high_enter, self.cfg.d_high_exit, "above"
        )
        self._poss_high = _hysteresis(
            self._poss_high, self.poss_ema, self.cfg.p_high_enter, self.cfg.p_high_exit, "above"
        )

        self.iters_in_state += 1
        if self.iters_in_state >= self.cfg.dwell_min:
            target = self._decide(t)
            if target != self.state:
                self.state = target
                self.iters_in_state = 0

        return self.states[self.state.value]
