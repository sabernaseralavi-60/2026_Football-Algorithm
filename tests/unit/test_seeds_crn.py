"""Unit test for CRN seed derivation (T068; research.md R11)."""

from __future__ import annotations

from tfo_bench.seeds import derive_seed


def test_same_cell_run_key_gives_identical_seed_across_algorithms_and_variants():
    # `derive_seed` takes no algorithm/variant argument at all: calling it with the same
    # (suite_code, function_id, dim, run) from "different algorithms" is literally the same call,
    # which is exactly what CRN requires.
    master, suite_code, fid, dim, run = 20260101, 1, 5, 30, 3

    seed_for_tfo = derive_seed(master, suite_code, fid, dim, run)
    seed_for_tfo_static = derive_seed(master, suite_code, fid, dim, run)
    seed_for_ca = derive_seed(master, suite_code, fid, dim, run)
    seed_for_ablation_variant = derive_seed(master, suite_code, fid, dim, run)

    assert seed_for_tfo == seed_for_tfo_static == seed_for_ca == seed_for_ablation_variant


def test_seed_changes_with_any_key_component():
    base = derive_seed(1, 1, 1, 30, 0)
    assert derive_seed(2, 1, 1, 30, 0) != base
    assert derive_seed(1, 2, 1, 30, 0) != base
    assert derive_seed(1, 1, 2, 30, 0) != base
    assert derive_seed(1, 1, 1, 15, 0) != base
    assert derive_seed(1, 1, 1, 30, 1) != base


def test_seed_is_always_a_nonzero_31_bit_value():
    for run in range(200):
        s = derive_seed(999, 3, 7, 10, run)
        assert 0 < s <= 0x7FFFFFFF
