"""tfo_bench.problems.reference: independent reference backends, built only for the audit
(cross-validation) and for restoring cells (research.md R3, R4; data-model.md B4).

- `opfunu_cec2017`: the CEC-2017 cross-check, `opfunu==1.0.4` (the same package already used as
  the CEC-2022 *primary*; here it plays the secondary/reference role for CEC-2017).
- `cec2022_c_shim`: the CEC-2022 independent reference, the official C code compiled to a small
  shared library and called through ctypes. Building it requires a C compiler and the organisers'
  source files, so it is optional: importing this subpackage never fails, but
  `cec2022_c_shim.is_available()` reports whether the compiled reference exists, and `audit.py`
  treats "reference not built" as "cross-validation cannot run yet" rather than a crash.
"""
