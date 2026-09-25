"""tasks.md T114: `docs/metaphor_free_description.md` contains zero football vocabulary."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
_DOC = _ROOT / "docs" / "metaphor_free_description.md"


def _load_checker():
    spec = importlib.util.spec_from_file_location(
        "check_metaphor_free", _ROOT / "scripts" / "check_metaphor_free.py"
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules["check_metaphor_free"] = module
    spec.loader.exec_module(module)
    return module


def test_doc_exists_and_is_nonempty():
    assert _DOC.exists()
    assert len(_DOC.read_text(encoding="utf-8")) > 500


def test_specification_body_has_no_football_vocabulary():
    checker = _load_checker()
    text = checker.specification_text(_DOC)
    violations = checker.find_violations(text)
    assert violations == [], f"football vocabulary leaked into the specification: {violations}"


def test_checker_actually_detects_a_planted_violation():
    checker = _load_checker()
    planted = "The agent moves the ball toward the goal."
    assert checker.find_violations(planted) != []


def test_appendix_is_excluded_from_the_scan():
    checker = _load_checker()
    full_text = _DOC.read_text(encoding="utf-8")
    assert "Appendix: implementation cross-reference" in full_text
    # The appendix itself legitimately names football-themed module paths (e.g. offside.py); the
    # checker must not scan it, or this test's own fixture would be self-contradictory.
    spec_text = checker.specification_text(_DOC)
    assert "Appendix: implementation cross-reference" not in spec_text
