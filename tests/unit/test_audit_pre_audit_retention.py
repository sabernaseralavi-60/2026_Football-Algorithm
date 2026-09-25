"""Unit test (T095; FR-038, data-model.md B4): "Pre-audit numbers are never deleted" -- a restored
or excluded cell's pre-audit numbers remain readable under `results/audit/pre_audit/<suite>/...`."""

from __future__ import annotations

import csv

from tfo_bench.audit import retain_pre_audit_numbers


def _write_runs_csv(path, rows):
    fieldnames = ["run_key", "cell_id", "algorithm", "best_f"]
    with open(path, "w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def test_pre_audit_numbers_are_copied_and_readable(tmp_path):
    runs_csv = tmp_path / "runs.csv"
    _write_runs_csv(
        runs_csv,
        [
            {"run_key": "main/cellA/TFO/full/0", "cell_id": "cellA", "algorithm": "TFO", "best_f": "1.0"},
            {"run_key": "main/cellA/GA/default/0", "cell_id": "cellA", "algorithm": "GA", "best_f": "2.0"},
            {"run_key": "main/cellB/TFO/full/0", "cell_id": "cellB", "algorithm": "TFO", "best_f": "3.0"},
        ],
    )

    dest = retain_pre_audit_numbers("cellA", "cec2017", runs_csv, tmp_path / "results")

    assert dest.exists()
    assert dest == tmp_path / "results" / "audit" / "pre_audit" / "cec2017" / "cellA.csv"

    with open(dest, newline="") as fh:
        rows = list(csv.DictReader(fh))
    assert len(rows) == 2
    assert {r["algorithm"] for r in rows} == {"TFO", "GA"}
    assert all(r["cell_id"] == "cellA" for r in rows)


def test_pre_audit_numbers_survive_even_when_the_source_runs_csv_is_later_removed(tmp_path):
    runs_csv = tmp_path / "runs.csv"
    _write_runs_csv(
        runs_csv,
        [{"run_key": "main/cellA/TFO/full/0", "cell_id": "cellA", "algorithm": "TFO", "best_f": "1.0"}],
    )
    dest = retain_pre_audit_numbers("cellA", "cec2017", runs_csv, tmp_path / "results")
    runs_csv.unlink()  # simulate the source run directory being cleaned up / superseded later
    assert dest.exists()
    with open(dest, newline="") as fh:
        rows = list(csv.DictReader(fh))
    assert len(rows) == 1
