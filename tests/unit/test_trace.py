"""Unit tests for RunTrace (tasks.md T060; data-model.md A14)."""

from __future__ import annotations

from tfo.registry import MechanismTag
from tfo.trace import RunTrace


def test_tactical_segments_are_lossless_and_contiguous():
    trace = RunTrace()
    states = ["CONTROL", "CONTROL", "CONTROL", "HIGH_PRESS", "HIGH_PRESS", "CONTROL"]
    evals_used = 0
    for it, state in enumerate(states):
        evals_used += 3
        trace.record_iteration(state, it, evals_used)

    # Reconstruct the per-iteration state sequence from the segments and check it matches exactly
    # (losslessness), and that segments partition [0, N) with no gaps or overlaps (contiguity).
    reconstructed = [None] * len(states)
    for seg in trace.segments:
        assert seg.iter_start < seg.iter_end
        for it in range(seg.iter_start, seg.iter_end):
            assert reconstructed[it] is None, "segments must not overlap"
            reconstructed[it] = seg.state
    assert reconstructed == states

    covered = sorted((seg.iter_start, seg.iter_end) for seg in trace.segments)
    assert covered[0][0] == 0
    assert covered[-1][1] == len(states)
    for (s1, e1), (s2, e2) in zip(covered, covered[1:]):
        assert e1 == s2, "no gaps between segments"


def test_transitions_counted():
    trace = RunTrace()
    for it, state in enumerate(["CONTROL", "CONTROL", "HIGH_PRESS", "CONTROL"]):
        trace.record_iteration(state, it, it)
    assert trace.transitions == 2


def test_mechanism_eval_count_sums_to_evals_used():
    trace = RunTrace()
    evals_by_tag = {tag: 0 for tag in MechanismTag}
    evals_by_tag[MechanismTag.VIRTUOSO] = 40
    evals_by_tag[MechanismTag.FINISHER] = 60
    trace.finalize_mechanism_evals(evals_by_tag)
    assert sum(trace.mechanism_evals.values()) == 100


def test_summary_reports_occupancy_fractions():
    trace = RunTrace()
    for it, state in enumerate(["CONTROL"] * 3 + ["HIGH_PRESS"] * 1):
        trace.record_iteration(state, it, it)
    summary = trace.summary(total_iterations=4, final_possession_rate=0.5)
    assert summary["occupancy"]["CONTROL"] == 0.75
    assert summary["occupancy"]["HIGH_PRESS"] == 0.25
    assert summary["n_transitions"] == 1
    assert summary["final_possession_rate"] == 0.5
