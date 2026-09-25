"""Unit tests for `tfo_bench.manifest` (T091; data-model.md B8)."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

from tfo_bench.manifest import DirtyWorkingTreeError, _TRACKED_LIBRARIES, build_manifest


def test_dirty_working_tree_is_refused_for_non_smoke_runs(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
    subprocess.run(["git", "config", "user.email", "t@example.com"], cwd=repo, check=True)
    subprocess.run(["git", "config", "user.name", "t"], cwd=repo, check=True)
    (repo / "a.txt").write_text("hello")
    subprocess.run(["git", "add", "a.txt"], cwd=repo, check=True)
    subprocess.run(["git", "commit", "-q", "-m", "init"], cwd=repo, check=True)

    # clean tree: non-smoke run is fine
    build_manifest(experiment="main", suite="cec2017", repo_root=repo, require_clean_tree=True)

    # dirty tree: non-smoke run is refused
    (repo / "a.txt").write_text("changed")
    with pytest.raises(DirtyWorkingTreeError):
        build_manifest(experiment="main", suite="cec2017", repo_root=repo, require_clean_tree=True)

    # a smoke run is allowed to proceed with a dirty tree
    manifest = build_manifest(
        experiment="smoke", suite="tuning", repo_root=repo, require_clean_tree=False
    )
    assert manifest.git_dirty is True


def test_fingerprint_includes_every_pinned_library_version():
    manifest = build_manifest(experiment="smoke", suite="tuning", require_clean_tree=False)
    assert set(manifest.library_versions) == set(_TRACKED_LIBRARIES)
    for name in ("numpy", "scipy", "opfunu", "niapy", "cma", "mealpy", "cec2017"):
        assert manifest.library_versions[name] != "not installed", name


def test_write_produces_a_timestamped_json_file(tmp_path):
    manifest = build_manifest(experiment="smoke", suite="tuning", require_clean_tree=False)
    path = manifest.write(tmp_path)
    assert path.exists()
    assert path.parent.name == "manifests"
    data = json.loads(path.read_text())
    assert data["experiment"] == "smoke"
    assert data["suite"] == "tuning"
