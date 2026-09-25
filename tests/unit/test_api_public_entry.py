"""Unit tests for the public entry point (tasks.md T064; optimizer-interface.md §1)."""

from __future__ import annotations

import subprocess
import sys
import textwrap

import numpy as np


def test_tfo_static_has_manager_disabled():
    import tfo

    assert tfo.TFO_STATIC.enable[tfo.MechanismTag.MANAGER] is False


def test_minimize_returns_tfo_result_with_documented_fields():
    import tfo

    def sphere(X: np.ndarray) -> np.ndarray:
        return np.sum((X - 0.4) ** 2, axis=1)

    bounds = (np.zeros(5), np.ones(5))
    result = tfo.minimize(sphere, bounds=bounds, budget=1500, seed=0, config=None)
    assert isinstance(result.x_best, np.ndarray)
    assert result.x_best.shape == (result.x_best.shape[0],)
    assert isinstance(result.f_best, float)
    assert result.evals_used <= 1500
    assert isinstance(result.evals_by_mechanism, dict)
    assert result.curve.shape == (100,)
    assert isinstance(result.tactical_trace, list)
    assert isinstance(result.summary, dict)
    assert isinstance(result.config_hash, str) and len(result.config_hash) == 64


def test_minimize_maps_unit_box_to_real_bounds():
    import tfo

    d = 4
    lb, ub = -5.0 * np.ones(d), 5.0 * np.ones(d)

    def sphere(X: np.ndarray) -> np.ndarray:
        return np.sum(X**2, axis=1)

    result = tfo.minimize(sphere, bounds=(lb, ub), budget=2000, seed=0, config=None)
    assert np.all(result.x_best >= lb) and np.all(result.x_best <= ub)
    assert result.f_best < 1.0  # should have found something reasonably close to 0


def test_minimize_is_deterministic_given_seed():
    import tfo

    def sphere(X: np.ndarray) -> np.ndarray:
        return np.sum((X - 0.4) ** 2, axis=1)

    bounds = (np.zeros(3), np.ones(3))
    r1 = tfo.minimize(sphere, bounds=bounds, budget=500, seed=7)
    r2 = tfo.minimize(sphere, bounds=bounds, budget=500, seed=7)
    assert r1.f_best == r2.f_best
    assert np.array_equal(r1.x_best, r2.x_best)
    assert r1.config_hash == r2.config_hash


def test_minimize_respects_evaluation_budget_exactly():
    import tfo

    def sphere(X: np.ndarray) -> np.ndarray:
        return np.sum(X**2, axis=1)

    result = tfo.minimize(sphere, bounds=(np.zeros(3), np.ones(3)), budget=777, seed=0)
    assert result.evals_used <= 777
    assert sum(result.evals_by_mechanism.values()) == result.evals_used


def test_scalar_only_bounds_are_rejected_with_a_clear_error():
    """Documented judgment call: optimizer-interface.md §1's signature has no explicit dimension
    parameter, so when BOTH lb and ub are scalar, D cannot be inferred at all; tfo.minimize raises
    a clear ValueError rather than guessing a dimension."""
    import tfo

    def sphere(X: np.ndarray) -> np.ndarray:
        return np.sum(X**2, axis=1)

    import pytest

    with pytest.raises(ValueError):
        tfo.minimize(sphere, bounds=(0.0, 1.0), budget=100, seed=0)


def test_tfo_imports_with_only_numpy_on_the_path():
    """`src/tfo/` must import cleanly with only numpy on the path (T064)."""
    script = textwrap.dedent(
        """
        import sys
        # Simulate an environment with none of tfo_bench's extra dependencies importable, by
        # refusing to import anything other than numpy and the standard library from here on.
        import builtins
        _real_import = builtins.__import__
        _allowed_prefixes = ("tfo", "numpy", "_", "encodings")
        import importlib

        def _guarded_import(name, globals=None, locals=None, fromlist=(), level=0):
            top = name.split(".")[0]
            # A relative import (level > 0, e.g. `from .version import x` inside numpy's own
            # __init__, or `from . import _compiler` inside the stdlib's `re` package) always
            # resolves within a module that was already allowed to import, so it is not itself a
            # new external dependency -- regardless of what its bare `name` looks like.
            if level > 0 or name == "" or top in sys.stdlib_module_names or any(
                name.startswith(p) for p in _allowed_prefixes
            ):
                return _real_import(name, globals, locals, fromlist, level)
            raise ImportError(f"blocked non-stdlib, non-numpy, non-tfo import: {name}")

        builtins.__import__ = _guarded_import
        import tfo
        import numpy as np

        def sphere(X):
            return np.sum(X**2, axis=1)

        result = tfo.minimize(sphere, bounds=(np.zeros(3), np.ones(3)), budget=200, seed=0)
        assert result.evals_used <= 200
        print("OK")
        """
    )
    proc = subprocess.run([sys.executable, "-c", script], capture_output=True, text=True)
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert "OK" in proc.stdout
