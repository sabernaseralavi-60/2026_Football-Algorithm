"""TFOConfig: the frozen, hashable configuration dataclass (data-model.md A15).

Every *(prov.)* numeric default named in data-model.md is set here from the literal value the
spec gives. Where data-model.md names a parameter but leaves its provisional value to the tuning
procedure without a stated number (research.md R13), a reasonable default is chosen and documented
inline with ``# judgment call:`` so it is not mistaken for a value the spec itself fixed. All such
defaults are placeholders until ``scripts/tune.py`` (out of scope for this pass) freezes
``config/tfo_frozen.toml`` at gate G3.
"""

from __future__ import annotations

import hashlib
import json
import tomllib
from dataclasses import dataclass, field, fields, is_dataclass, replace
from pathlib import Path
from typing import Any, Mapping

from tfo.registry import ENABLE_TAGS, Archetype, DEFAULT_ARCHETYPE_COUNTS, MechanismTag

_PACKAGE_ROOT = Path(__file__).resolve().parent


def _tag(value: str | MechanismTag) -> MechanismTag:
    if isinstance(value, MechanismTag):
        return value
    try:
        return MechanismTag(value)
    except ValueError as exc:
        raise ValueError(f"{value!r} is not a known mechanism tag") from exc


def _archetype(value: str | Archetype) -> Archetype:
    if isinstance(value, Archetype):
        return value
    try:
        return Archetype(value.upper())
    except ValueError as exc:
        raise ValueError(f"{value!r} is not a known archetype") from exc


# --------------------------------------------------------------------------------------
# Nested, frozen parameter groups
# --------------------------------------------------------------------------------------


@dataclass(frozen=True)
class SquadConfig:
    n: int = 30
    role_counts: Mapping[Archetype, int] = field(
        default_factory=lambda: dict(DEFAULT_ARCHETYPE_COUNTS)
    )

    def __post_init__(self) -> None:
        object.__setattr__(self, "role_counts", dict(self.role_counts))
        if sum(self.role_counts.values()) != self.n - 1:
            raise ValueError("role_counts must sum to n_out = n - 1 (data-model.md A1/A2)")


@dataclass(frozen=True)
class StateParameterVector:
    """One row of data-model.md A8's StateParameterVector table."""

    formation: str
    rho: float  # pressing radius, normalised
    tau: float  # retention threshold
    chain_length: int  # L, pass-chain length
    rate_multipliers: Mapping[str, float] = field(default_factory=dict)
    substitution_cap_increment: int = 0

    def __post_init__(self) -> None:
        object.__setattr__(self, "rate_multipliers", dict(self.rate_multipliers))


@dataclass(frozen=True)
class ManagerConfig:
    """data-model.md A8/A15: EMA weights, hysteresis-banded thresholds, dwell."""

    ema_alpha_div: float = 0.10  # judgment call: EMA smoothing weight for diversity
    ema_alpha_poss: float = 0.10  # judgment call: EMA smoothing weight for possession rate
    d_low_enter: float = 0.05  # judgment call: numeric value of "d_low" (enter)
    d_low_exit: float = 0.08  # judgment call: hysteresis exit for d_low
    d_high_enter: float = 0.35  # judgment call: numeric value of "d_high" (enter)
    d_high_exit: float = 0.30  # judgment call: hysteresis exit for d_high
    p_high_enter: float = 0.60  # judgment call: numeric value of "p_high" (enter)
    p_high_exit: float = 0.50  # judgment call: hysteresis exit for p_high
    g_max: int = 50  # judgment call: drought threshold (iterations) for CHASING
    delta_mat: float = 1e-4  # data-model.md A8: delta_mat (prov.)
    t_press: float = 0.20  # judgment call: budget fraction before HIGH_PRESS is eligible
    t_late: float = 0.10  # judgment call: "late" cutoff for the premature-collapse edge case
    dwell_min: int = 10  # data-model.md A8: dwell_min (prov.)


@dataclass(frozen=True)
class OperatorConfig:
    """data-model.md A15's `operators` group: per-mechanism parameters."""

    blx_alpha: float = 0.5  # BLX-alpha (Deep-Lying Playmaker)
    de_f: float = 0.5  # DE F (Box-to-Box, Destroyer)
    de_cr: float = 0.9  # DE CR (Box-to-Box)
    jump_rate: float = 0.3  # Jr (Overlapping Wing-Back; Rahnamayan et al. 2008)
    levy_beta: float = 1.5  # Levy beta (Finisher; Mantegna 1994)
    levy_sigma: float = 0.01  # judgment call: Finisher's Levy step scale sigma_L
    finisher_fail_limit: int = 10  # F_fail (Finisher)
    mesh_h_min: float = 1e-6  # judgment call: Virtuoso mesh lower bound
    mesh_h_max: float = 0.10  # judgment call: Virtuoso mesh upper bound
    mesh_h_init: float = 0.01  # judgment call: Virtuoso mesh initial value
    mesh_k: int = 2  # number of polled coordinates (Virtuoso; prov.)
    niche_radius: float = 0.01  # r_niche (Destroyer; prov.)
    neutral_sigma: float = 0.10  # judgment call: global step scale sigma for the neutral move
    counter_attack_delta_mat: float = 1e-4  # judgment call: Delta_mat (counter-attack trigger)
    counter_attack_d_trans: float = 0.20  # judgment call: d_trans (counter-attack trigger)
    burst_len: int = 5  # burst length (prov.)
    burst_gamma: float = 0.5  # step decay gamma (prov.)
    burst_s0: float = 0.10  # judgment call: initial burst step scale s0
    set_piece_period: int = 25  # c (prov.)
    set_piece_h: float = 0.05  # judgment call: set-piece probe step h
    neutral_pass_max: int = 5  # N_neutral_max (prov.)
    lost_streak_max: int = 3  # R_loss (prov.)
    var_review_period: int = 10  # v (prov.)
    tabu_radius: float = 0.02  # r_tabu (prov.)
    tabu_max: int = 20  # T_max (prov.)
    collision_radius: float = 1e-3  # r_coll (prov.)
    fatigue_kappa: float = 0.05  # judgment call: kappa (fatigue drain rate)
    fatigue_r0: float = 0.5  # judgment call: r0 (fatigue recovery rate)
    stamina_min: float = 0.2  # judgment call: s_min
    stamina_sub_threshold: float = 0.4  # judgment call: s_sub (substitution stamina gate)
    substitution_cap: int = 5  # per fixture (prov.)
    substitution_window: int = 50  # W, stagnation window (prov.)
    archive_k: int = 5  # KeeperArchive size K (prov.)
    archive_min_sep: float = 0.05  # min_sep (prov.)
    n_fixtures: int = 20  # data-model.md A7 (prov.)


@dataclass(frozen=True)
class ConstraintConfig:
    """data-model.md A15's `constraints` group; used only in the epsilon experiment."""

    eps0: float = 1.0  # judgment call: epsilon_0
    t_c: float = 0.8  # T_c (Takahama & Sakai 2006; prov.)
    cp: float = 5.0  # judgment call: cp exponent


def _default_states() -> dict[str, StateParameterVector]:
    # Numeric values for rho/tau/chain_length/rate_multipliers are judgment calls: data-model.md
    # A8 gives only qualitative labels (low/medium/high, short/medium/long) for the provisional
    # StateParameterVector; the tuning procedure (research.md R13) replaces all of these.
    return {
        "BUILD_UP": StateParameterVector(
            formation="balanced", rho=0.05, tau=0.01, chain_length=5,
        ),
        "CONTROL": StateParameterVector(
            formation="balanced", rho=0.15, tau=0.001, chain_length=5,
        ),
        "HIGH_PRESS": StateParameterVector(
            formation="compact", rho=0.30, tau=0.0, chain_length=10,
            rate_multipliers={"virtuoso": 1.5, "finisher": 1.5},
        ),
        "CHASING": StateParameterVector(
            formation="stretched", rho=0.0, tau=0.01, chain_length=2,
            rate_multipliers={"overlapping_wing_back": 2.0, "deep_lying_playmaker": 2.0},
            substitution_cap_increment=2,
        ),
    }


# --------------------------------------------------------------------------------------
# TFOConfig
# --------------------------------------------------------------------------------------


@dataclass(frozen=True)
class TFOConfig:
    """data-model.md A15.

    Note on naming: data-model.md A15 names both a *state field* ("`homogeneous`: `None`, or an
    archetype name") and, in optimizer-interface.md §1, a *builder method* spelled
    ``.homogeneous(...)``. Python cannot give one attribute both meanings on a frozen dataclass, so
    (documented judgment call) the state is held in ``homogeneous_archetype`` and ``.homogeneous(...)``
    is the builder method the contract names; ``to_dict()``/``config_hash`` still serialise it under
    the key ``homogeneous``, matching data-model.md's schema.
    """

    enable: Mapping[MechanismTag, bool] = field(
        default_factory=lambda: {tag: True for tag in ENABLE_TAGS}
    )
    homogeneous_archetype: Archetype | None = None
    squad: SquadConfig = field(default_factory=SquadConfig)
    states: Mapping[str, StateParameterVector] = field(default_factory=_default_states)
    manager: ManagerConfig = field(default_factory=ManagerConfig)
    operators: OperatorConfig = field(default_factory=OperatorConfig)
    constraints: ConstraintConfig = field(default_factory=ConstraintConfig)

    def __post_init__(self) -> None:
        enable = {_tag(k): bool(v) for k, v in dict(self.enable).items()}
        missing = set(ENABLE_TAGS) - set(enable)
        for tag in missing:
            enable[tag] = True
        unknown = set(enable) - set(ENABLE_TAGS)
        if unknown:
            raise ValueError(f"enable contains unknown mechanism tags: {unknown}")
        object.__setattr__(self, "enable", dict(enable))
        object.__setattr__(self, "states", dict(self.states))
        if self.homogeneous_archetype is not None:
            object.__setattr__(
                self, "homogeneous_archetype", _archetype(self.homogeneous_archetype)
            )

    # -- serialisation -------------------------------------------------------------

    def to_dict(self) -> dict[str, Any]:
        d = _to_jsonable(self)
        d["homogeneous"] = d.pop("homogeneous_archetype")
        return d

    @property
    def config_hash(self) -> str:
        canonical = json.dumps(self.to_dict(), sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()

    @classmethod
    def from_toml(cls, path: str | Path) -> "TFOConfig":
        with open(path, "rb") as fh:
            data = tomllib.load(fh)
        return cls.from_dict(data)

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "TFOConfig":
        base = cls()
        kwargs: dict[str, Any] = {}
        if "enable" in data:
            merged = dict(base.enable)
            merged.update({_tag(k): bool(v) for k, v in data["enable"].items()})
            kwargs["enable"] = merged
        if "homogeneous" in data and data["homogeneous"] is not None:
            kwargs["homogeneous_archetype"] = _archetype(data["homogeneous"])
        for group_name, group_cls in (
            ("squad", SquadConfig),
            ("manager", ManagerConfig),
            ("operators", OperatorConfig),
            ("constraints", ConstraintConfig),
        ):
            if group_name in data:
                current = getattr(base, group_name)
                kwargs[group_name] = replace(current, **data[group_name])
        if "states" in data:
            merged_states = dict(base.states)
            for name, overrides in data["states"].items():
                merged_states[name] = replace(merged_states[name], **overrides)
            kwargs["states"] = merged_states
        return replace(base, **kwargs)

    # -- variant builders (data-model.md A15 "Named variants") ----------------------

    def ablate(self, mechanism: str | MechanismTag) -> "TFOConfig":
        """Disable a single mechanism (data-model.md A15 `off:<mechanism>`, or `static` for manager)."""
        tag = _tag(mechanism)
        new_enable = dict(self.enable)
        new_enable[tag] = False
        return replace(self, enable=new_enable)

    def homogeneous(self, archetype: str | Archetype) -> "TFOConfig":
        """optimizer-interface.md §1's `.homogeneous(...)` builder (data-model.md A15 `homog:<archetype>`)."""
        return replace(self, homogeneous_archetype=_archetype(archetype))

    def with_(self, **overrides: Any) -> "TFOConfig":
        """Override one or more top-level or nested-group fields immutably."""
        kwargs: dict[str, Any] = {}
        for key, value in overrides.items():
            if key in {"enable", "homogeneous_archetype"}:
                kwargs[key] = value
                continue
            current = getattr(self, key, None)
            if is_dataclass(current) and isinstance(value, Mapping):
                kwargs[key] = replace(current, **value)
            else:
                kwargs[key] = value
        return replace(self, **kwargs)

    @property
    def variant_id(self) -> str:
        """data-model.md A15's `variant_id`, for the mechanisms this pass implements."""
        if not self.enable[MechanismTag.MANAGER]:
            others_off = [
                t for t in ENABLE_TAGS if t != MechanismTag.MANAGER and not self.enable[t]
            ]
            if not others_off and self.homogeneous_archetype is None:
                return "static"
        off = [t for t in ENABLE_TAGS if not self.enable[t]]
        if len(off) == 1:
            return f"off:{off[0].value}"
        if (
            not self.enable[MechanismTag.FORMATION]
            and not self.enable[MechanismTag.ROTATION]
            and len(off) == 2
        ):
            return "G-topology"
        if self.homogeneous_archetype is not None and all(self.enable.values()):
            return f"homog:{self.homogeneous_archetype.value.lower()}"
        if all(self.enable.values()) and self.homogeneous_archetype is None:
            return "full"
        return "custom"


def _to_jsonable(obj: Any) -> Any:
    if is_dataclass(obj) and not isinstance(obj, type):
        return {f.name: _to_jsonable(getattr(obj, f.name)) for f in fields(obj)}
    if isinstance(obj, Mapping):
        return {_key_str(k): _to_jsonable(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_to_jsonable(v) for v in obj]
    if isinstance(obj, (MechanismTag, Archetype)):
        return obj.value
    return obj


def _key_str(key: Any) -> str:
    if isinstance(key, (MechanismTag, Archetype)):
        return key.value
    return str(key)


#: `tfo.TFO_STATIC` (optimizer-interface.md §1): the manager disabled, everything else on.
TFO_STATIC = TFOConfig().ablate(MechanismTag.MANAGER)
