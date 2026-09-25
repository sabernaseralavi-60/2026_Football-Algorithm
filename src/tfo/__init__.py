"""tfo: the Total Football Optimizer, a NumPy-only metaheuristic (optimizer-interface.md §1).

`import tfo` pulls in only NumPy and the Python standard library (T064).
"""

from tfo.api import TFOProgress, TFOResult, minimize
from tfo.config import TFO_STATIC, TFOConfig
from tfo.registry import Archetype, MechanismTag

__all__ = [
    "minimize",
    "TFOResult",
    "TFOProgress",
    "TFOConfig",
    "TFO_STATIC",
    "Archetype",
    "MechanismTag",
]
