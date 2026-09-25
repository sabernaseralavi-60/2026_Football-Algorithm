"""Contract test (tasks.md T112; Principle VI, FR-043, SC-009): every mechanism, variant and
algorithm identifier in code is on the registry's closed allowlist, and none matches a real
person's name, nickname, club, or competition trademark."""

from __future__ import annotations

import re
from pathlib import Path

from tfo.config import TFOConfig
from tfo.registry import IDENTIFIER_ALLOWLIST, REGISTRY, Archetype, MechanismTag

_SRC_TFO = Path(__file__).resolve().parents[2] / "src" / "tfo"

# A representative denylist of real people, clubs and competitions (Principle VI). Not
# exhaustive -- it is the mechanical, committed check this project's tooling can run --
# but it covers the individuals and organisations most likely to leak into football-themed
# code (legendary and current players/managers across eras, major clubs, and competitions).
_DENYLIST = [
    "messi", "ronaldo", "maradona", "pele", "pelé", "beckenbauer", "cruyff", "xavi",
    "iniesta", "busquets", "kroos", "zidane", "neuer", "casillas", "pirlo", "mourinho",
    "guardiola", "klopp", "ferguson", "wenger", "beckham", "mbappe", "mbappé", "haaland",
    "neymar", "modric", "modrić", "de bruyne", "salah", "kane", "lewandowski", "suarez",
    "suárez", "ibrahimovic", "ibrahimović", "totti", "buffon", "maldini", "baresi",
    "beckham", "gerrard", "lampard", "scholes", "giggs", "henry", "vieira", "zico",
    "socrates", "sócrates", "garrincha", "puskas", "puskás", "di stefano", "eusebio",
    "eusébio", "platini", "matthaus", "matthäus", "rummenigge", "van basten", "bergkamp",
    "barcelona", "real madrid", "manchester united", "manchester city", "bayern munich",
    "liverpool fc", "juventus", "ac milan", "inter milan", "chelsea fc", "arsenal fc",
    "fifa", "uefa", "premier league", "champions league", "la liga", "bundesliga",
    "serie a", "world cup",
]


def _all_code_text() -> str:
    chunks = []
    for path in _SRC_TFO.rglob("*.py"):
        chunks.append(path.read_text(encoding="utf-8"))
    return "\n".join(chunks)


def test_registry_identifiers_are_exactly_the_allowlist():
    expected = {tag.value for tag in MechanismTag} | {a.value for a in Archetype} | {
        entry.display_name for entry in REGISTRY.values()
    }
    assert IDENTIFIER_ALLOWLIST == expected


def test_no_denylisted_name_in_registry_identifiers():
    haystack = " ".join(IDENTIFIER_ALLOWLIST).lower()
    for name in _DENYLIST:
        assert name not in haystack, f"denylisted identifier {name!r} found in the allowlist"


def test_no_denylisted_name_anywhere_in_tfo_source():
    code = _all_code_text().lower()
    for name in _DENYLIST:
        # Word-boundary match to avoid incidental substrings (e.g. "totti" inside an unrelated word).
        pattern = r"\b" + re.escape(name) + r"\b"
        assert not re.search(pattern, code), f"denylisted name {name!r} found in src/tfo source"


def test_variant_ids_stay_within_the_allowlist_vocabulary():
    """Every variant_id this pass can produce is built only from registry tag/archetype values."""
    cfg = TFOConfig()
    ids = [cfg.variant_id, cfg.ablate(MechanismTag.VIRTUOSO).variant_id, cfg.ablate(MechanismTag.MANAGER).variant_id]
    ids.append(cfg.homogeneous(Archetype.DESTROYER).variant_id)
    for variant_id in ids:
        # Strip the known prefixes; whatever remains must be a mechanism tag or archetype value.
        for prefix in ("off:", "homog:"):
            if variant_id.startswith(prefix):
                remainder = variant_id[len(prefix) :]
                assert (
                    remainder in {t.value for t in MechanismTag}
                    or remainder in {a.value.lower() for a in Archetype}
                ), f"variant_id {variant_id!r} contains an identifier outside the allowlist"
