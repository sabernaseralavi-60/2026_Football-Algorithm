"""Integration test (T103; gate G3): `ConfigNotFrozenError` is raised for any non-smoke
CEC-2017/CEC-2022/engineering job before both tags exist, or when the config hash mismatches."""

from __future__ import annotations

from pathlib import Path

import pytest

from tfo.config import TFOConfig
from tfo_bench.runner import (
    ConfigNotFrozenError,
    PreRegistrationRequiredError,
    check_config_frozen,
    check_preregistered,
)


def test_raises_when_frozen_file_does_not_exist(tmp_path):
    missing = tmp_path / "tfo_frozen.toml"
    with pytest.raises(ConfigNotFrozenError):
        check_config_frozen(TFOConfig().config_hash, "main", missing)


def test_raises_when_hash_mismatches(tmp_path):
    frozen_path = tmp_path / "tfo_frozen.toml"
    frozen_path.write_text('rho_note = "not a real TFOConfig, just needs a different hash"\n')
    # Write an actual loadable frozen config, but with a different hash than what we check.
    default_cfg = TFOConfig()
    from scripts.tune import _toml_dump  # reuse the same writer the real script uses

    frozen_path.write_text(_toml_dump(default_cfg.to_dict()))

    different_cfg = TFOConfig().ablate(list(TFOConfig().enable)[0])
    with pytest.raises(ConfigNotFrozenError):
        check_config_frozen(different_cfg.config_hash, "main", frozen_path)


def test_passes_when_hash_matches(tmp_path):
    frozen_path = tmp_path / "tfo_frozen.toml"
    default_cfg = TFOConfig()
    from scripts.tune import _toml_dump

    frozen_path.write_text(_toml_dump(default_cfg.to_dict()))

    check_config_frozen(default_cfg.config_hash, "main", frozen_path)  # must not raise


@pytest.mark.parametrize("experiment", ["smoke", "tuning", "pilot"])
def test_smoke_tuning_pilot_experiments_are_exempt_from_the_freeze_guard(experiment, tmp_path):
    missing = tmp_path / "tfo_frozen.toml"
    check_config_frozen(TFOConfig().config_hash, experiment, missing)  # must not raise


@pytest.mark.parametrize("experiment", ["main", "ablation", "sensitivity", "takeover", "epsilon", "timing"])
def test_every_non_smoke_test_suite_experiment_is_guarded(experiment, tmp_path):
    missing = tmp_path / "tfo_frozen.toml"
    with pytest.raises(ConfigNotFrozenError):
        check_config_frozen(TFOConfig().config_hash, experiment, missing)


def test_G4_preregistration_guard_blocks_non_smoke_jobs_without_the_tag():
    with pytest.raises(PreRegistrationRequiredError):
        check_preregistered("main", git_tags=set())
    check_preregistered("main", git_tags={"prereg-v1"})  # must not raise
    check_preregistered("smoke", git_tags=set())  # exempt experiment, must not raise


def test_both_tags_exist_in_this_repository():
    """This project's own repository is expected to carry both tags once T101 is done."""
    from tfo_bench.runner import get_git_tags

    repo_root = Path(__file__).resolve().parents[2]
    tags = get_git_tags(repo_root)
    assert "prereg-v1" in tags, "config/protocol.toml must be tagged prereg-v1 (gate G4)"
    assert "tfo-frozen-v1" in tags, "config/tfo_frozen.toml must be tagged tfo-frozen-v1 (gate G3)"
