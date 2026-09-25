"""Unit tests for TFOConfig (tasks.md T009; data-model.md A15)."""

from __future__ import annotations

import hashlib
import json

import pytest

from tfo.config import TFOConfig
from tfo.registry import ENABLE_TAGS, Archetype, MechanismTag


def test_default_config_all_enabled():
    cfg = TFOConfig()
    assert set(cfg.enable.keys()) == set(ENABLE_TAGS)
    assert all(cfg.enable.values()), "Default: all true (data-model.md A15)"
    assert cfg.homogeneous_archetype is None


def test_config_hash_is_sha256_of_canonical_json():
    cfg = TFOConfig()
    expected = hashlib.sha256(
        json.dumps(cfg.to_dict(), sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    assert cfg.config_hash == expected


def test_config_hash_changes_with_content():
    cfg1 = TFOConfig()
    cfg2 = cfg1.ablate(MechanismTag.VIRTUOSO)
    assert cfg1.config_hash != cfg2.config_hash


def test_config_hash_deterministic_for_equal_content():
    cfg1 = TFOConfig()
    cfg2 = TFOConfig()
    assert cfg1.config_hash == cfg2.config_hash


def test_ablate_disables_one_mechanism_only():
    cfg = TFOConfig().ablate(MechanismTag.VIRTUOSO)
    assert cfg.enable[MechanismTag.VIRTUOSO] is False
    for tag in ENABLE_TAGS:
        if tag != MechanismTag.VIRTUOSO:
            assert cfg.enable[tag] is True


def test_ablate_manager_is_tfo_static():
    cfg = TFOConfig().ablate(MechanismTag.MANAGER)
    assert cfg.enable[MechanismTag.MANAGER] is False


def test_ablate_rejects_unknown_mechanism():
    with pytest.raises(ValueError):
        TFOConfig().ablate("not_a_mechanism")


def test_homogeneous_sets_single_archetype():
    cfg = TFOConfig().homogeneous(Archetype.DESTROYER)
    assert cfg.homogeneous_archetype == Archetype.DESTROYER


def test_homogeneous_accepts_string_name():
    cfg = TFOConfig().homogeneous("destroyer")
    assert cfg.homogeneous_archetype == Archetype.DESTROYER


def test_with_overrides_nested_fields_immutably():
    cfg1 = TFOConfig()
    cfg2 = cfg1.with_(operators={"blx_alpha": 0.7})
    assert cfg1.operators.blx_alpha == 0.5
    assert cfg2.operators.blx_alpha == 0.7
    # Unrelated operator fields are preserved from the base config.
    assert cfg2.operators.de_f == cfg1.operators.de_f


def test_config_is_frozen():
    cfg = TFOConfig()
    with pytest.raises(Exception):
        cfg.homogeneous_field_does_not_exist = True  # type: ignore[attr-defined]


def test_from_toml_round_trip(tmp_path):
    toml_path = tmp_path / "cfg.toml"
    toml_path.write_text(
        """
        [operators]
        blx_alpha = 0.65

        [enable]
        virtuoso = false
        """
    )
    cfg = TFOConfig.from_toml(toml_path)
    assert cfg.operators.blx_alpha == 0.65
    assert cfg.enable[MechanismTag.VIRTUOSO] is False
    # Everything else keeps its default.
    assert cfg.enable[MechanismTag.FINISHER] is True
    assert cfg.operators.de_f == TFOConfig().operators.de_f


def test_variant_id_full_and_static():
    assert TFOConfig().variant_id == "full"
    assert TFOConfig().ablate(MechanismTag.MANAGER).variant_id == "static"


def test_variant_id_off_mechanism():
    cfg = TFOConfig().ablate(MechanismTag.VIRTUOSO)
    assert cfg.variant_id == "off:virtuoso"


def test_variant_id_homogeneous():
    cfg = TFOConfig().homogeneous(Archetype.DESTROYER)
    assert cfg.variant_id == "homog:destroyer"
