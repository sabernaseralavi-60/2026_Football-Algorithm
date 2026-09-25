"""Regression test for a real numerical bug this project's own audit machinery caught: F9
("Shifted and Rotated Levy") does NOT have its claimed optimum at the raw shift vector, unlike
every other CEC-2017 simple/hybrid function (see `tfo_bench.problems.cec2017.x_star`'s docstring
for the full numerical finding). Locks in the fix so it cannot silently regress.
"""

from __future__ import annotations

from tfo_bench.audit import run_preflight
from tfo_bench.problems import cec2017


def test_f09_preflight_passes_with_the_corrected_optimum():
    problems = cec2017.build_problems(D=30)
    result = run_preflight(problems["F09"])
    assert result.passed, f"F09 preflight failed: f(x*)={result.f_at_xstar} vs f*={result.f_star}"


def test_every_cec2017_function_passes_preflight_at_D30():
    """The full 29-cell preflight sweep (cheap: one evaluation per function, not a benchmark
    run) -- exercises the composition-singularity backoff too."""
    problems = cec2017.build_problems(D=30)
    backoff = [1e-6, 1e-8, 1e-10, 1e-12, 1e-14]
    for n in cec2017.OFFICIAL_NUMBERS:
        fid = cec2017.function_id(n)
        result = run_preflight(
            problems[fid],
            composition_epsilon_backoff=backoff if cec2017.is_composition(n) else None,
        )
        assert result.passed, f"{fid} preflight failed: {result}"
