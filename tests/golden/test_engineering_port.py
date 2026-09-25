"""Golden test: the ported engineering problems match the sibling's read-only module (T076;
research.md R10).

The fixture (`fixtures/engineering_port.json`) was captured once by evaluating the sibling's
`engineering_problems.py` (commit 96af96bbb5ef36514ae11a0cc5695d4a6211d9a4), read-only, at a fixed
set of boundary and random points (see the generation snippet in this file's module docstring
below for exact reproducibility). This test never imports the sibling at run time.

Regeneration snippet (run manually against the sibling checkout if the fixture ever needs
refreshing; not executed by the test suite):

    import sys, json, numpy as np
    sys.path.insert(0, "<path-to-2026_Chess-Algorithm>/src")
    import engineering_problems as ep
    rng = np.random.default_rng(20260925)
    fixtures = {}
    for name, (fn, lb, ub, D, f_ref) in ep.ENGINEERING.items():
        lb, ub = np.asarray(lb), np.asarray(ub)
        pts = [lb.copy(), ub.copy(), (lb + ub) / 2.0] + [
            lb + (ub - lb) * rng.random(D) for _ in range(5)
        ]
        X = np.stack(pts)
        fixtures[name] = {"X": X.tolist(), "penalized_f": np.asarray(fn(X), dtype=float).tolist()}
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest

from tfo_bench.problems import engineering as eng

FIXTURE_PATH = Path(__file__).parent / "fixtures" / "engineering_port.json"


@pytest.fixture(scope="module")
def fixtures():
    with open(FIXTURE_PATH) as fh:
        return json.load(fh)


@pytest.mark.parametrize("name", list(eng.RAW_FUNCTIONS))
def test_port_matches_sibling_to_1e12_relative(fixtures, name):
    data = fixtures[name]
    X = np.asarray(data["X"], dtype=float)
    expected = np.asarray(data["penalized_f"], dtype=float)

    raw_fn = eng.RAW_FUNCTIONS[name]
    cost, G = raw_fn(X)
    got = cost + eng.PENALTY_COEFFICIENT * np.sum(np.maximum(G, 0.0) ** 2, axis=1)

    rel_err = np.abs(got - expected) / np.maximum(1.0, np.abs(expected))
    assert np.all(rel_err <= 1e-12), f"{name}: max relative error {rel_err.max():.3e}"


def test_all_seven_problems_are_ported():
    assert set(eng.RAW_FUNCTIONS) == {
        "WeldedBeam",
        "Spring",
        "PressureVessel",
        "SpeedReducer",
        "ThreeBarTruss",
        "GearTrain",
        "CantileverBeam",
    }
