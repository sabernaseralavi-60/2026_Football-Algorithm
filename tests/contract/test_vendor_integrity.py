"""Contract test: the vendored CA/GA/PSO/GWO file's hash matches PROVENANCE.md (T079;
research.md R9)."""

from __future__ import annotations

import hashlib
import re
from pathlib import Path

VENDOR_DIR = (
    Path(__file__).parent.parent.parent
    / "src"
    / "tfo_bench"
    / "algorithms"
    / "vendor"
)
VENDORED_FILE = VENDOR_DIR / "chess_algorithms_96af96b.py"
PROVENANCE = VENDOR_DIR / "PROVENANCE.md"


def test_vendored_file_hash_matches_provenance():
    text = PROVENANCE.read_text()
    m = re.search(r"SHA-256 of the vendored file:\*\*\s*\n\s*`([0-9a-f]{64})`", text)
    assert m, "PROVENANCE.md must state the vendored file's SHA-256"
    expected = m.group(1)

    actual = hashlib.sha256(VENDORED_FILE.read_bytes()).hexdigest()
    assert actual == expected, (
        f"chess_algorithms_96af96b.py hash changed: expected {expected}, got {actual}. "
        "This file must be a verbatim, unmodified copy of the pinned sibling commit (research.md R9)."
    )


def test_provenance_names_the_pinned_commit_and_doi():
    text = PROVENANCE.read_text()
    assert "96af96bbb5ef36514ae11a0cc5695d4a6211d9a4" in text
    assert "10.5281/zenodo.22854043" in text


def test_vendored_file_defines_the_four_roster_functions():
    ns: dict = {}
    code = VENDORED_FILE.read_text()
    for name in ("chess_algorithm_v3", "genetic_algorithm", "particle_swarm", "grey_wolf"):
        assert f"def {name}(" in code
