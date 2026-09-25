"""tasks.md T110 (User Story 1, SC-001): 100% of TFO's mechanisms (19 of 19) appear in the
operator-family table with a named family and at least one canonical citation; zero mechanisms are
unmapped."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

from tfo.registry import all_mechanisms

_SCRIPTS_DIR = Path(__file__).resolve().parents[2] / "scripts"


def _load_script(name: str):
    spec = importlib.util.spec_from_file_location(name, _SCRIPTS_DIR / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def test_all_19_mechanisms_present_with_family_and_citation():
    mechanisms = all_mechanisms()
    assert len(mechanisms) == 19, "100% of TFO's mechanisms (19 of 19)"
    for entry in mechanisms:
        assert entry.family.strip(), f"{entry.display_name} has no operator family"
        assert len(entry.citations) >= 1, f"{entry.display_name} has no canonical citation"


def test_rendered_table_contains_every_mechanism_and_citation():
    make_table = _load_script("make_mechanism_table")
    table = make_table.render_table()
    for entry in all_mechanisms():
        assert entry.display_name in table
        assert entry.family in table
        for citation in entry.citations:
            assert citation in table


def test_table_has_exactly_19_data_rows():
    make_table = _load_script("make_mechanism_table")
    table = make_table.render_table()
    data_rows = [
        line for line in table.strip().splitlines() if line.startswith("|") and not line.startswith("|---")
    ][1:]  # drop the header row
    assert len(data_rows) == 19, "zero mechanisms are unmapped"
