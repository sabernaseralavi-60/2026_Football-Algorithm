"""Contract test for the 9 validation checks of results-schema.md §9 (T086)."""

from __future__ import annotations

import numpy as np
import pytest

from tfo_bench import records


def _valid_record(**overrides):
    kwargs = dict(
        experiment="smoke",
        suite="tuning",
        cell_id="tuning_Sphere_D15",
        function_id="Sphere",
        dim=15,
        algorithm="TFO",
        variant_id="full",
        config_hash="abc",
        run=0,
        seed=42,
        budget=200,
        evals_used=200,
        evals_internal=200,
        status="ok",
        best_f=1.0,
        f_star=0.0,
    )
    kwargs.update(overrides)
    return records.make_run_record(**kwargs)


def _write_valid_results(tmp_path, n_algorithms=2):
    writer = records.ResultsWriter(tmp_path, "smoke", "tuning")
    for i, algo in enumerate(["TFO", "GA"][:n_algorithms]):
        rec = _valid_record(algorithm=algo, variant_id="full" if algo == "TFO" else "default")
        writer.append_run(rec)
        writer.append_curve(rec["run_key"], np.linspace(10, 0, 100))
        if algo == "TFO":
            writer.append_mechanism_evals(rec["run_key"], {"finisher": 200})
    return tmp_path / "smoke" / "tuning"


def test_check1_and_2_valid_directory_has_no_issues(tmp_path):
    directory = _write_valid_results(tmp_path)
    issues = records.validate_runs_csv(directory / "runs.csv")
    assert issues == []


def test_check2_duplicate_run_key_is_caught(tmp_path):
    writer = records.ResultsWriter(tmp_path, "smoke", "tuning")
    rec = _valid_record()
    writer.append_run(rec)
    writer.append_run(rec)  # duplicate run_key
    issues = records.validate_runs_csv(tmp_path / "smoke" / "tuning" / "runs.csv")
    assert any("duplicate run_key" in i for i in issues)


def test_check3_evals_used_exceeding_budget_is_caught(tmp_path):
    writer = records.ResultsWriter(tmp_path, "smoke", "tuning")
    writer.append_run(_valid_record(evals_used=999, budget=200))
    issues = records.validate_runs_csv(tmp_path / "smoke" / "tuning" / "runs.csv")
    assert any("evals_used" in i and ">" in i for i in issues)


def test_check4_evals_internal_mismatch_is_caught(tmp_path):
    writer = records.ResultsWriter(tmp_path, "smoke", "tuning")
    writer.append_run(_valid_record(evals_used=200, evals_internal=150))
    issues = records.validate_runs_csv(tmp_path / "smoke" / "tuning" / "runs.csv")
    assert any("evals_internal" in i for i in issues)


def test_check5_seed_must_match_across_algorithms_in_same_cell_and_run(tmp_path):
    writer = records.ResultsWriter(tmp_path, "smoke", "tuning")
    writer.append_run(_valid_record(algorithm="TFO", seed=1, run=0))
    writer.append_run(_valid_record(algorithm="GA", variant_id="default", seed=2, run=0))
    issues = records.validate_runs_csv(tmp_path / "smoke" / "tuning" / "runs.csv")
    assert any("seed differs" in i for i in issues)


def test_check6_budget_must_match_across_algorithms_in_same_cell(tmp_path):
    writer = records.ResultsWriter(tmp_path, "smoke", "tuning")
    writer.append_run(_valid_record(algorithm="TFO", budget=200))
    writer.append_run(_valid_record(algorithm="GA", variant_id="default", budget=100, evals_used=100))
    issues = records.validate_runs_csv(tmp_path / "smoke" / "tuning" / "runs.csv")
    assert any("budget differs" in i for i in issues)


def test_check7_non_increasing_curve_is_enforced(tmp_path):
    writer = records.ResultsWriter(tmp_path, "smoke", "tuning")
    rec = _valid_record()
    writer.append_run(rec)
    bad_curve = np.concatenate([np.linspace(10, 5, 50), np.linspace(6, 0, 50)])  # increases at 50
    writer.append_curve(rec["run_key"], bad_curve)
    issues = records.validate_curves_csv(
        tmp_path / "smoke" / "tuning" / "runs.csv", tmp_path / "smoke" / "tuning" / "curves.csv"
    )
    assert any("not non-increasing" in i for i in issues)


def test_check9_unknown_algorithm_identifier_is_caught(tmp_path):
    writer = records.ResultsWriter(tmp_path, "smoke", "tuning")
    writer.append_run(_valid_record(algorithm="SomeUnlistedAlgorithm"))
    issues = records.validate_identifiers_csv(tmp_path / "smoke" / "tuning" / "runs.csv")
    assert any("unknown algorithm identifier" in i for i in issues)


def test_check9_all_roster_and_variant_identifiers_are_allowed():
    from tfo_bench.algorithms.base import ROSTER_LABELS

    assert set(ROSTER_LABELS) <= records.ALLOWED_ALGORITHM_NAMES
    assert "full" in records.ALLOWED_VARIANT_IDS
    assert "off:virtuoso" in records.ALLOWED_VARIANT_IDS
    assert "homog:finisher" in records.ALLOWED_VARIANT_IDS


def test_check8_admissible_and_inadmissible_audit_dispositions(tmp_path):
    writer = records.ResultsWriter(tmp_path, "smoke", "tuning")
    writer.append_run(_valid_record(cell_id="cellA"))
    writer.append_run(_valid_record(cell_id="cellB", run=1))

    audit_csv = tmp_path / "cell_audit.csv"
    import csv

    with open(audit_csv, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["cell_id", "disposition"])
        w.writeheader()
        w.writerow({"cell_id": "cellA", "disposition": "validated"})
        w.writerow({"cell_id": "cellB", "disposition": "pending"})

    issues = records.validate_audit_dispositions(
        tmp_path / "smoke" / "tuning" / "runs.csv", audit_csv
    )
    assert any("cellB" in i for i in issues)
    assert not any("cellA" in i for i in issues)
