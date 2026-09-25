"""tfo_bench.manifest: `EnvironmentManifest` (data-model.md B8).

Written once per experiment invocation, to `results/manifests/<experiment>_<suite>_<utc-
timestamp>.json` (results-schema.md §1).
"""

from __future__ import annotations

import hashlib
import json
import os
import platform
import subprocess
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

#: The libraries whose versions are part of the reproducibility fingerprint (data-model.md B8);
#: kept as a plain list (not `importlib.metadata.distributions()`) so the manifest's set of
#: recorded libraries is stable and doesn't silently grow or shrink with unrelated installs.
_TRACKED_LIBRARIES = [
    "numpy",
    "scipy",
    "pandas",
    "matplotlib",
    "opfunu",
    "niapy",
    "cma",
    "mealpy",
    "cec2017",
]


class DirtyWorkingTreeError(Exception):
    """Raised for a non-smoke run when the git working tree is dirty (data-model.md B8)."""


def _git_sha_and_dirty(repo_root: Optional[Path] = None) -> tuple[str, bool]:
    root = str(repo_root) if repo_root is not None else "."
    try:
        sha = (
            subprocess.check_output(["git", "-C", root, "rev-parse", "HEAD"], stderr=subprocess.DEVNULL)
            .decode()
            .strip()
        )
        status = (
            subprocess.check_output(["git", "-C", root, "status", "--porcelain"], stderr=subprocess.DEVNULL)
            .decode()
            .strip()
        )
        return sha, bool(status)
    except Exception:
        return "unknown", True


def _file_sha256(path: Path) -> Optional[str]:
    if not path.exists():
        return None
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _library_versions() -> dict[str, str]:
    import importlib.metadata as md

    versions: dict[str, str] = {}
    for name in _TRACKED_LIBRARIES:
        try:
            versions[name] = md.version(name)
        except md.PackageNotFoundError:
            versions[name] = "not installed"
    return versions


def _cpu_info() -> dict[str, str]:
    return {
        "model": platform.processor() or platform.machine(),
        "machine": platform.machine(),
        "python_version": platform.python_version(),
    }


@dataclass
class EnvironmentManifest:
    experiment: str
    suite: str
    git_sha: str
    git_dirty: bool
    lockfile_sha256: Optional[str]
    config_sha256: Optional[str]
    library_versions: dict[str, str]
    cpu_info: dict[str, str]
    npy_disable_cpu_features: str
    start_time_utc: str
    end_time_utc: Optional[str]
    worker_count: int
    job_count: int

    def to_dict(self) -> dict:
        return asdict(self)

    def write(self, results_root: str | Path) -> Path:
        out_dir = Path(results_root) / "manifests"
        out_dir.mkdir(parents=True, exist_ok=True)
        ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        path = out_dir / f"{self.experiment}_{self.suite}_{ts}.json"
        path.write_text(json.dumps(self.to_dict(), indent=2, sort_keys=True))
        return path


def build_manifest(
    *,
    experiment: str,
    suite: str,
    repo_root: Optional[Path] = None,
    lockfile_path: Optional[Path] = None,
    config_path: Optional[Path] = None,
    worker_count: int = 1,
    job_count: int = 0,
    require_clean_tree: bool = True,
) -> EnvironmentManifest:
    """Builds (but does not write) the manifest for one experiment invocation.

    `require_clean_tree`: a dirty working tree is refused for non-smoke runs (data-model.md B8);
    the runner passes `require_clean_tree=False` only for `experiment == "smoke"` jobs.
    """
    sha, dirty = _git_sha_and_dirty(repo_root)
    if dirty and require_clean_tree:
        raise DirtyWorkingTreeError(
            f"git working tree is dirty (sha={sha}); refused for non-smoke experiment {experiment!r}"
        )
    return EnvironmentManifest(
        experiment=experiment,
        suite=suite,
        git_sha=sha,
        git_dirty=dirty,
        lockfile_sha256=_file_sha256(lockfile_path) if lockfile_path else None,
        config_sha256=_file_sha256(config_path) if config_path else None,
        library_versions=_library_versions(),
        cpu_info=_cpu_info(),
        npy_disable_cpu_features=os.environ.get("NPY_DISABLE_CPU_FEATURES", ""),
        start_time_utc=datetime.now(timezone.utc).isoformat(),
        end_time_utc=None,
        worker_count=worker_count,
        job_count=job_count,
    )
