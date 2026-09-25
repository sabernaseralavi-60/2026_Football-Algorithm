"""Fatigue and fixture congestion (mechanism-interface.md §2.17, FR-020; data-model.md A11).

Operator: drain s_i <- max(s_min, s_i - kappa*||Delta x||/sqrt(D)) after each move; recover
s_i <- min(1, s_i + r0*(1 - t)) at each fixture. Stamina scales every archetype step
(Workload-clocked per-agent step-size annealing; Kirkpatrick et al. 1983).
"""

from __future__ import annotations

import numpy as np


def drain(stamina: float, delta_x_norm: float, kappa: float, s_min: float, d: int) -> float:
    return max(s_min, stamina - kappa * delta_x_norm / np.sqrt(d))


def recover(stamina: float, r0: float, t: float) -> float:
    return min(1.0, stamina + r0 * (1.0 - t))


def drain_agent(squad, i: int, x_before: np.ndarray, kappa: float, s_min: float) -> None:
    delta_norm = float(np.linalg.norm(squad.X[i] - x_before))
    squad.stamina[i] = drain(squad.stamina[i], delta_norm, kappa, s_min, squad.d)


def recover_all(squad, r0: float, t: float) -> None:
    squad.stamina[:] = np.minimum(1.0, squad.stamina + r0 * (1.0 - t))
