"""The CEC-2022 independent reference: the official C code (Kumar et al., 2021), compiled to a
small shared library and called through ctypes (research.md R4).

**Status in this implementation pass: the shared library is not built in this environment.**
This project's own scope notes ("Do NOT actually run the real CEC-2017/CEC-2022/engineering
benchmark experiments") mean no real cross-validation run is due yet either, so the absence of a
compiler toolchain plus the organisers' C source in this sandbox was not chased down. What is
implemented is the *harness*: the ctypes calling convention this shim expects from the compiled
library, and a clean, mechanical `is_available()` gate so `audit.py` can tell "no reference built
yet" apart from "reference disagrees" instead of crashing either way.

**To actually build it** (documented for whoever runs the real programme):
1. Obtain the official CEC-2022 C source (`cec22_test_func.c` and its data files) from the
   organisers' repository (Kumar, Price, Mohamed, Hadi & Suganthan, 2021).
2. Compile it to a shared library exposing a function with this C signature (adapt the organisers'
   `cec22_test_func` entry point to it if the names differ):
       void cec22_test_func(double *x, double *f, int nx, int mx, int func_num);
   (`x`: `mx` rows of `nx` doubies, row-major; `f`: `mx` doubles out; `func_num`: 1..12.)
3. Place the compiled library at the path `CEC2022_C_LIBRARY_PATH` below (or set the
   `TFO_BENCH_CEC2022_C_LIB` environment variable to its path).
"""

from __future__ import annotations

import ctypes
import os
from pathlib import Path
from typing import Optional

import numpy as np

from tfo_bench.problems.base import Problem

CEC2022_C_LIBRARY_PATH = Path(__file__).parent / "vendor" / "libcec22.so"

_F_STAR = {n: v for n, v in zip(range(1, 13), [300, 400, 600, 800, 900, 1800, 2000, 2200, 2300, 2400, 2600, 2700])}


def _library_path() -> Path:
    env = os.environ.get("TFO_BENCH_CEC2022_C_LIB")
    return Path(env) if env else CEC2022_C_LIBRARY_PATH


def is_available() -> bool:
    """Whether the compiled official-C reference library exists on this machine."""
    return _library_path().is_file()


def _load_library() -> ctypes.CDLL:
    path = _library_path()
    if not path.is_file():
        raise FileNotFoundError(
            f"CEC-2022 official-C reference not built: {path} does not exist. See this module's "
            "docstring for the build steps. Cross-validation against it cannot run until then."
        )
    lib = ctypes.CDLL(str(path))
    lib.cec22_test_func.argtypes = [
        ctypes.POINTER(ctypes.c_double),
        ctypes.POINTER(ctypes.c_double),
        ctypes.c_int,
        ctypes.c_int,
        ctypes.c_int,
    ]
    lib.cec22_test_func.restype = None
    return lib


def _make_fn(lib: ctypes.CDLL, func_num: int, D: int):
    def fn(X: np.ndarray) -> np.ndarray:
        X = np.ascontiguousarray(np.atleast_2d(X), dtype=np.float64)
        m = X.shape[0]
        out = np.empty(m, dtype=np.float64)
        lib.cec22_test_func(
            X.ctypes.data_as(ctypes.POINTER(ctypes.c_double)),
            out.ctypes.data_as(ctypes.POINTER(ctypes.c_double)),
            ctypes.c_int(D),
            ctypes.c_int(m),
            ctypes.c_int(func_num),
        )
        return out

    return fn


def build_problems(D: int, x_star_by_function: Optional[dict[int, np.ndarray]] = None) -> dict[str, Problem]:
    """Build the 12 CEC-2022 reference problems from the compiled official-C library.

    `x_star_by_function` supplies the claimed optimum location per function number, since the C
    entry point above exposes no way to query it; the audit driver is expected to pass the same
    x_star used for the primary (opfunu) backend, since both claim the same official optimum.
    Raises `FileNotFoundError` (see `is_available()`) if the library was never built.
    """
    lib = _load_library()
    problems: dict[str, Problem] = {}
    for n in range(1, 13):
        fid = f"F{n:02d}"
        x_star = None if x_star_by_function is None else x_star_by_function.get(n)
        problems[fid] = Problem(
            problem_id=f"cec2022_{fid}_D{D}_reference",
            suite="cec2022",
            name=fid,
            D=D,
            lb=-100.0,
            ub=100.0,
            f_star=float(_F_STAR[n]),
            fn=_make_fn(lib, n, D),
            x_star=x_star,
            implementation="official-C (Kumar et al. 2021) via ctypes",
            has_constraints=False,
        )
    return problems
