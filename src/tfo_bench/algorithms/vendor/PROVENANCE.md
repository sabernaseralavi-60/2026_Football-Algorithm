# Provenance: `chess_algorithms_96af96b.py`

- **Source repository:** `2026_Chess-Algorithm` (the sibling project; read-only reference per the
  constitution's "sibling repository is a read-only reference" rule).
- **Source file:** `src/algorithms.py`
- **Commit SHA:** `96af96bbb5ef36514ae11a0cc5695d4a6211d9a4`
- **Zenodo DOI:** [10.5281/zenodo.22854043](https://doi.org/10.5281/zenodo.22854043)
- **Licence:** MIT (Copyright (c) 2026 Seyed Saber Naseralavi), reproduced from the sibling
  repository's `LICENSE` file.
- **SHA-256 of the vendored file:**
  `0d94c092477e13b4763bd7e08c3e6fb07f994fab5f352c99b2b38ebf10b20529`

This is a **verbatim, unmodified** copy of the sibling's `src/algorithms.py` at the commit above
(research.md R9). A contract test (`tests/contract/test_vendor_integrity.py`) fails if the file's
hash ever changes. It supplies four roster algorithms to `tfo_bench`:

- `chess_algorithm_v3` -> the CA (SHOULD comparator) adapter (`sibling.py`'s `CAAdapter`)
- `genetic_algorithm` -> `GAAdapter`
- `particle_swarm` -> `PSOAdapter`
- `grey_wolf` -> `GWOAdapter`

Regenerate/verify with:

```sh
git -C <path-to-2026_Chess-Algorithm> show 96af96bbb5ef36514ae11a0cc5695d4a6211d9a4:src/algorithms.py \
    | sha256sum
```
