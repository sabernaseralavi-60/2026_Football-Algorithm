"""The neutral (1+1)-ES fallback move, used by disabled archetypes (mechanism-interface.md §1;
research.md R14).

y = x_i + sigma * s_i * N(0, I), accepted greedily. sigma is the global step scale (operators.
neutral_sigma) and s_i the agent's stamina.
"""

from __future__ import annotations

import numpy as np


def propose(x_i: np.ndarray, sigma: float, stamina_i: float, rng: np.random.Generator) -> np.ndarray:
    """Draw the neutral-move proposal y = x_i + sigma * s_i * N(0, I) (unrepaired)."""
    return x_i + sigma * stamina_i * rng.standard_normal(x_i.shape)
