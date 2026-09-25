"""tasks.md T115 (User Story 1, acceptance scenario 4): for each of the 8 archetypes in
mechanism-map.md's "Archetype inspiration" section, each homage appears as at most one
explanatory sentence, and no real person's name appears in it."""

from __future__ import annotations

import re
from pathlib import Path

from tests.contract.test_identifier_allowlist import _DENYLIST

_MECHANISM_MAP = (
    Path(__file__).resolve().parents[2]
    / "specs"
    / "001-football-algorithm"
    / "mechanism-map.md"
)

_ARCHETYPE_DISPLAY_NAMES = [
    "Sweeper-Keeper",
    "Zonal Centre-Back",
    "Overlapping Wing-Back",
    "Deep-Lying Playmaker",
    "Box-to-Box Engine",
    "Destroyer",
    "Virtuoso",
    "Finisher",
]


def _homage_paragraph() -> str:
    text = _MECHANISM_MAP.read_text(encoding="utf-8")
    marker = "*Archetype inspiration"
    start = text.index(marker)
    end = text.index("## Overlap audit", start)
    return text[start:end]


def _sentences(paragraph: str) -> list[str]:
    # Strip markdown emphasis markers first, since a period can be immediately followed by a
    # closing "*" rather than whitespace (e.g. "individuals).* The Sweeper-Keeper...").
    cleaned = paragraph.replace("*", "")
    return [s.strip() for s in re.split(r"(?<=\.)\s+", cleaned) if s.strip()]


def test_every_archetype_has_exactly_one_homage_sentence():
    paragraph = _homage_paragraph()
    sentences = _sentences(paragraph)
    for name in _ARCHETYPE_DISPLAY_NAMES:
        matching = [s for s in sentences if s.startswith(f"The {name} follows")]
        assert len(matching) == 1, (
            f"{name} must have exactly one homage sentence, found {len(matching)}"
        )


def test_no_real_person_name_in_any_homage_sentence():
    paragraph = _homage_paragraph().lower()
    for name in _DENYLIST:
        assert name not in paragraph, f"denylisted name {name!r} found in the homage paragraph"


def test_homage_paragraph_states_it_is_homage_not_identity():
    paragraph = _homage_paragraph()
    assert "not to individuals" in paragraph
