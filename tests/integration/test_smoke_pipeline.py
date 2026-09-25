"""Integration test (T105): an end-to-end run on one tuning function produces schema-valid
`runs.csv`/`curves.csv`/`mechanism_evals.csv`/`tactical_trace.csv.gz` and passes
`validate_results.py`."""

from __future__ import annotations

import gzip
import sys
from pathlib import Path

from tfo_bench import records, runner

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
import validate_results  # noqa: E402


def test_smoke_pipeline_end_to_end(tmp_path):
    writer = records.ResultsWriter(tmp_path, "smoke", "tuning")

    jobs = runner.enumerate_jobs(
        experiment="smoke",
        suite="tuning",
        function_ids=["Sphere"],
        dim=15,
        algorithms=["TFO", "TFO-static", "GA", "PSO"],
        n_runs=2,
        budget=400,
        master_seed=13579,
    )
    n_ran = runner.run_experiment(jobs, writer, n_workers=1)
    assert n_ran == len(jobs) == 8

    directory = tmp_path / "smoke" / "tuning"
    assert (directory / "runs.csv").exists()
    assert (directory / "curves.csv").exists()
    assert (directory / "mechanism_evals.csv").exists()  # TFO family only, but present
    assert (directory / "tactical_trace.csv.gz").exists()

    # curves.csv has exactly 100 checkpoint columns plus run_key, one row per run
    curve_rows = records.read_csv_rows(directory / "curves.csv")
    assert len(curve_rows) == 8
    assert len(curve_rows[0]) == 101

    # mechanism_evals.csv has all 21 tags for each TFO-family run_key
    mech_rows = records.read_csv_rows(directory / "mechanism_evals.csv")
    tfo_run_keys = {r["run_key"] for r in records.read_csv_rows(directory / "runs.csv") if r["algorithm"] in ("TFO", "TFO-static")}
    for rk in tfo_run_keys:
        tags_for_key = {row["tag"] for row in mech_rows if row["run_key"] == rk}
        assert len(tags_for_key) == 21

    # tactical_trace.csv.gz is readable and has the expected header
    with gzip.open(directory / "tactical_trace.csv.gz", "rt") as fh:
        header = fh.readline().strip().split(",")
    assert header == records.TACTICAL_TRACE_COLUMNS

    issues = validate_results.validate_directory(directory, cell_audit_path=None)
    assert issues == [], issues
