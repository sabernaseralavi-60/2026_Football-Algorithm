"""Mechanism registry: tag <-> module <-> operator family <-> citation (mechanism-map.md).

This module is the single source of truth for:

- the closed, 21-member :class:`MechanismTag` enumeration
  (contracts/evaluation-ledger.md §2);
- the 8-member :class:`Archetype` enumeration (data-model.md A2);
- the operator-family table that ``scripts/make_mechanism_table.py`` (T109) renders for the
  manuscript, so the table cannot drift from the code (Principle I);
- the CA overlap audit that ``scripts/audit_overlap.py`` (T111) computes;
- the Principle VI identifier allowlist checked by
  ``tests/contract/test_identifier_allowlist.py`` (T112).

Every identifier here is a tactical-function name or a plain algorithmic term. None names a real
person, club, or competition (constitution Principle VI).
"""

from __future__ import annotations

import enum
from dataclasses import dataclass


class MechanismTag(str, enum.Enum):
    """The closed 21-tag vocabulary of evaluation-ledger.md §2."""

    INIT = "init"

    # 8 archetype tags (mechanism-interface.md §2, mechanisms 1-8)
    SWEEPER_KEEPER = "sweeper_keeper"
    ZONAL_CENTRE_BACK = "zonal_centre_back"
    OVERLAPPING_WING_BACK = "overlapping_wing_back"
    DEEP_LYING_PLAYMAKER = "deep_lying_playmaker"
    BOX_TO_BOX = "box_to_box"
    DESTROYER = "destroyer"
    VIRTUOSO = "virtuoso"
    FINISHER = "finisher"

    # 11 tactic tags (mechanism-interface.md §2, mechanisms 9-19)
    FORMATION = "formation"
    ROTATION = "rotation"
    POSSESSION = "possession"
    PRESSING = "pressing"
    COUNTER_ATTACK = "counter_attack"
    SET_PIECES = "set_pieces"
    OFFSIDE = "offside"
    SUBSTITUTIONS = "substitutions"
    FATIGUE = "fatigue"
    VAR_REVIEW = "var_review"
    MANAGER = "manager"

    NEUTRAL = "neutral"


class Archetype(str, enum.Enum):
    """The 8 player archetypes (data-model.md A2). Tactical-function names only."""

    SWEEPER_KEEPER = "SWEEPER_KEEPER"
    ZONAL_CENTRE_BACK = "ZONAL_CENTRE_BACK"
    OVERLAPPING_WING_BACK = "OVERLAPPING_WING_BACK"
    DEEP_LYING_PLAYMAKER = "DEEP_LYING_PLAYMAKER"
    BOX_TO_BOX = "BOX_TO_BOX"
    DESTROYER = "DESTROYER"
    VIRTUOSO = "VIRTUOSO"
    FINISHER = "FINISHER"


#: Archetype -> the MechanismTag its move is charged under.
ARCHETYPE_TAG: dict[Archetype, MechanismTag] = {
    Archetype.SWEEPER_KEEPER: MechanismTag.SWEEPER_KEEPER,
    Archetype.ZONAL_CENTRE_BACK: MechanismTag.ZONAL_CENTRE_BACK,
    Archetype.OVERLAPPING_WING_BACK: MechanismTag.OVERLAPPING_WING_BACK,
    Archetype.DEEP_LYING_PLAYMAKER: MechanismTag.DEEP_LYING_PLAYMAKER,
    Archetype.BOX_TO_BOX: MechanismTag.BOX_TO_BOX,
    Archetype.DESTROYER: MechanismTag.DESTROYER,
    Archetype.VIRTUOSO: MechanismTag.VIRTUOSO,
    Archetype.FINISHER: MechanismTag.FINISHER,
}

#: Default outfield role-sheet composition (data-model.md A2, n_out = 29, provisional).
DEFAULT_ARCHETYPE_COUNTS: dict[Archetype, int] = {
    Archetype.ZONAL_CENTRE_BACK: 4,
    Archetype.OVERLAPPING_WING_BACK: 4,
    Archetype.DEEP_LYING_PLAYMAKER: 3,
    Archetype.BOX_TO_BOX: 6,
    Archetype.DESTROYER: 3,
    Archetype.VIRTUOSO: 5,
    Archetype.FINISHER: 4,
}
assert sum(DEFAULT_ARCHETYPE_COUNTS.values()) == 29, "n_out must be 29 (data-model.md A1)"

ARCHETYPE_TAGS: tuple[MechanismTag, ...] = tuple(ARCHETYPE_TAG.values())
TACTIC_TAGS: tuple[MechanismTag, ...] = (
    MechanismTag.FORMATION,
    MechanismTag.ROTATION,
    MechanismTag.POSSESSION,
    MechanismTag.PRESSING,
    MechanismTag.COUNTER_ATTACK,
    MechanismTag.SET_PIECES,
    MechanismTag.OFFSIDE,
    MechanismTag.SUBSTITUTIONS,
    MechanismTag.FATIGUE,
    MechanismTag.VAR_REVIEW,
    MechanismTag.MANAGER,
)

#: The 18 mechanisms switched off one at a time (FR-034); manager is the 19th `enable` flag but
#: switching it off is the group-level TFO-static variant, not a single-off variant.
SWITCHABLE_TAGS: tuple[MechanismTag, ...] = ARCHETYPE_TAGS + tuple(
    t for t in TACTIC_TAGS if t != MechanismTag.MANAGER
)
assert len(SWITCHABLE_TAGS) == 18

#: The 19 `enable` flags of data-model.md A15 (18 switchable mechanisms plus the manager).
ENABLE_TAGS: tuple[MechanismTag, ...] = SWITCHABLE_TAGS + (MechanismTag.MANAGER,)
assert len(ENABLE_TAGS) == 19

#: Mechanisms whose tag must end any run with a count of exactly 0 (evaluation-ledger.md §2).
ZERO_EVAL_TAGS: frozenset[MechanismTag] = frozenset(
    {
        MechanismTag.SWEEPER_KEEPER,
        MechanismTag.FORMATION,
        MechanismTag.ROTATION,
        MechanismTag.OFFSIDE,
        MechanismTag.FATIGUE,
        MechanismTag.VAR_REVIEW,
        MechanismTag.MANAGER,
    }
)

ALL_TAGS: tuple[MechanismTag, ...] = tuple(MechanismTag)
assert len(ALL_TAGS) == 21


@dataclass(frozen=True)
class MechanismEntry:
    """One row of the operator-family table (mechanism-map.md's mapping table)."""

    tag: MechanismTag
    display_name: str
    module: str
    kind: str  # "archetype" | "tactic" | "manager"
    family: str
    citations: tuple[str, ...]
    fr: str
    overlaps_ca: str  # "yes" | "partly" | "no" (mechanism-map.md's overlap audit)
    ca_overlap_note: str


REGISTRY: dict[MechanismTag, MechanismEntry] = {
    MechanismTag.SWEEPER_KEEPER: MechanismEntry(
        tag=MechanismTag.SWEEPER_KEEPER,
        display_name="Sweeper-Keeper",
        module="tfo.archetypes.sweeper_keeper",
        kind="archetype",
        family="Elitism with a bounded hall-of-fame archive",
        citations=("De Jong (1975)", "Rosin & Belew (1997)"),
        fr="FR-005",
        overlaps_ca="yes",
        ca_overlap_note="Shares the King + overprotection archive family; this archive also "
        "seeds Finisher restarts and ball resets.",
    ),
    MechanismTag.ZONAL_CENTRE_BACK: MechanismEntry(
        tag=MechanismTag.ZONAL_CENTRE_BACK,
        display_name="Zonal Centre-Back",
        module="tfo.archetypes.zonal_centre_back",
        kind="archetype",
        family="Stratified / Latin-hypercube sampling, space partitioning",
        citations=("McKay et al. (1979)",),
        fr="FR-006",
        overlaps_ca="no",
        ca_overlap_note="Family absent from CA's operator-family table.",
    ),
    MechanismTag.OVERLAPPING_WING_BACK: MechanismEntry(
        tag=MechanismTag.OVERLAPPING_WING_BACK,
        display_name="Overlapping Wing-Back",
        module="tfo.archetypes.overlapping_wing_back",
        kind="archetype",
        family="Quasi-opposition-based learning, generation jumping",
        citations=("Tizhoosh (2005)", "Rahnamayan et al. (2007)"),
        fr="FR-007",
        overlaps_ca="yes",
        ca_overlap_note="Shares opposition-based initialisation; used here as in-run generation "
        "jumping about the centroid, not only at initialisation.",
    ),
    MechanismTag.DEEP_LYING_PLAYMAKER: MechanismEntry(
        tag=MechanismTag.DEEP_LYING_PLAYMAKER,
        display_name="Deep-Lying Playmaker",
        module="tfo.archetypes.deep_lying_playmaker",
        kind="archetype",
        family="BLX-alpha crossover over small-world long-range links",
        citations=("Eshelman & Schaffer (1993)", "Watts & Strogatz (1998)"),
        fr="FR-008",
        overlaps_ca="no",
        ca_overlap_note="Family absent from CA's operator-family table.",
    ),
    MechanismTag.BOX_TO_BOX: MechanismEntry(
        tag=MechanismTag.BOX_TO_BOX,
        display_name="Box-to-Box Engine",
        module="tfo.archetypes.box_to_box",
        kind="archetype",
        family="Neighbourhood-based differential mutation, DEGL-style local DE",
        citations=("Das et al. (2009)",),
        fr="FR-009",
        overlaps_ca="yes",
        ca_overlap_note="Shares the knight's-fork differential-mutation family; donor selection "
        "here is restricted to the formation-graph neighbourhood.",
    ),
    MechanismTag.DESTROYER: MechanismEntry(
        tag=MechanismTag.DESTROYER,
        display_name="Destroyer",
        module="tfo.archetypes.destroyer",
        kind="archetype",
        family="Clearing / crowding-based niching",
        citations=("Petrowski (1996)", "Mahfoud (1995)"),
        fr="FR-010",
        overlaps_ca="no",
        ca_overlap_note="Family absent from CA's operator-family table.",
    ),
    MechanismTag.VIRTUOSO: MechanismEntry(
        tag=MechanismTag.VIRTUOSO,
        display_name="Virtuoso",
        module="tfo.archetypes.virtuoso",
        kind="archetype",
        family="Compass / generalized pattern search",
        citations=("Hooke & Jeeves (1961)", "Torczon (1997)"),
        fr="FR-011",
        overlaps_ca="no",
        ca_overlap_note="Family absent from CA's operator-family table.",
    ),
    MechanismTag.FINISHER: MechanismEntry(
        tag=MechanismTag.FINISHER,
        display_name="Finisher",
        module="tfo.archetypes.finisher",
        kind="archetype",
        family="Levy-flight (heavy-tailed) mutation with elite restart",
        citations=("Lee & Yao (2004)", "Mantegna (1994)"),
        fr="FR-012",
        overlaps_ca="no",
        ca_overlap_note="Family absent from CA's operator-family table.",
    ),
    MechanismTag.FORMATION: MechanismEntry(
        tag=MechanismTag.FORMATION,
        display_name="Formation",
        module="tfo.tactics.formation",
        kind="tactic",
        family="Cellular (structured) population with dynamic grid-shape topology",
        citations=("Alba & Dorronsoro (2005)", "Kennedy & Mendes (2002)"),
        fr="FR-013",
        overlaps_ca="no",
        ca_overlap_note="Family absent from CA's operator-family table.",
    ),
    MechanismTag.ROTATION: MechanismEntry(
        tag=MechanismTag.ROTATION,
        display_name="Positional rotation",
        module="tfo.tactics.rotation",
        kind="tactic",
        family="Rank-based role reassignment restricted to graph neighbours",
        citations=("Janson & Middendorf (2005)",),
        fr="FR-022",
        overlaps_ca="yes",
        ca_overlap_note="Shares promotion / rank-based reassignment; here it is a local pairwise "
        "swap with graph neighbours at fixture boundaries, not a global re-ranking every "
        "iteration.",
    ),
    MechanismTag.POSSESSION: MechanismEntry(
        tag=MechanismTag.POSSESSION,
        display_name="Possession",
        module="tfo.tactics.possession",
        kind="tactic",
        family="Threshold accepting",
        citations=("Dueck & Scheuer (1990)",),
        fr="FR-014",
        overlaps_ca="no",
        ca_overlap_note="Family absent from CA's operator-family table.",
    ),
    MechanismTag.PRESSING: MechanismEntry(
        tag=MechanismTag.PRESSING,
        display_name="Pressing",
        module="tfo.tactics.pressing",
        kind="tactic",
        family="Distance-gated shrinking-encircling attraction",
        citations=("Mirjalili et al. (2014)",),
        fr="FR-015",
        overlaps_ca="partly",
        ca_overlap_note="Partial overlap with CA's elite-guided perturbation in its role moves; "
        "membership here is gated by distance to the ball, with the radius under adaptive "
        "control.",
    ),
    MechanismTag.COUNTER_ATTACK: MechanismEntry(
        tag=MechanismTag.COUNTER_ATTACK,
        display_name="Counter-attack",
        module="tfo.tactics.counter_attack",
        kind="tactic",
        family="Event-triggered basin hopping / iterated-local-search relocation",
        citations=("Wales & Doye (1997)", "Lourenco et al. (2003)"),
        fr="FR-016",
        overlaps_ca="no",
        ca_overlap_note="Family absent from CA's operator-family table.",
    ),
    MechanismTag.SET_PIECES: MechanismEntry(
        tag=MechanismTag.SET_PIECES,
        display_name="Set pieces",
        module="tfo.tactics.set_pieces",
        kind="tactic",
        family="Fixed-frequency memetic local search: orthogonal-design sampling, successive "
        "parabolic interpolation",
        citations=("Leung & Wang (2001)", "Brent (1973)"),
        fr="FR-017",
        overlaps_ca="no",
        ca_overlap_note="Family absent from CA's operator-family table.",
    ),
    MechanismTag.OFFSIDE: MechanismEntry(
        tag=MechanismTag.OFFSIDE,
        display_name="Offside line",
        module="tfo.tactics.offside",
        kind="tactic",
        family="Bound repair + epsilon-constrained feasibility ranking",
        citations=("Helwig et al. (2013)", "Takahama & Sakai (2006)", "Deb (2000)"),
        fr="FR-018",
        overlaps_ca="no",
        ca_overlap_note="Family absent from CA's operator-family table.",
    ),
    MechanismTag.SUBSTITUTIONS: MechanismEntry(
        tag=MechanismTag.SUBSTITUTIONS,
        display_name="Substitutions",
        module="tfo.tactics.substitutions",
        kind="tactic",
        family="Stagnation-triggered random immigrants, capped",
        citations=("Grefenstette (1992)",),
        fr="FR-019",
        overlaps_ca="yes",
        ca_overlap_note="Shares threefold-repetition re-initialisation; here it is triggered by "
        "individual stagnation plus fatigue, capped per fixture, and feeds the VAR tabu "
        "register.",
    ),
    MechanismTag.FATIGUE: MechanismEntry(
        tag=MechanismTag.FATIGUE,
        display_name="Fatigue and fixture congestion",
        module="tfo.tactics.fatigue",
        kind="tactic",
        family="Workload-clocked per-agent step-size annealing",
        citations=("Kirkpatrick et al. (1983)",),
        fr="FR-020",
        overlaps_ca="yes",
        ca_overlap_note="Shares the development-schedule / decaying-step family; here it is "
        "per-agent and workload-clocked rather than global and iteration-clocked.",
    ),
    MechanismTag.VAR_REVIEW: MechanismEntry(
        tag=MechanismTag.VAR_REVIEW,
        display_name="VAR review",
        module="tfo.tactics.var_review",
        kind="tactic",
        family="Deferred tabu audit with aspiration criterion: short-term memory plus rollback",
        citations=("Glover (1989)",),
        fr="FR-021",
        overlaps_ca="no",
        ca_overlap_note="Family absent from CA's operator-family table.",
    ),
    MechanismTag.MANAGER: MechanismEntry(
        tag=MechanismTag.MANAGER,
        display_name="The manager's tactical board",
        module="tfo.manager",
        kind="manager",
        family="Feedback-driven adaptive parameter control, state machine",
        citations=("Eiben et al. (1999)",),
        fr="FR-023,FR-024,FR-025,FR-026",
        overlaps_ca="yes",
        ca_overlap_note="Shares the phase state-machine family; here it also switches "
        "interaction topology (formation), not only operator rates.",
    ),
}
assert set(REGISTRY.keys()) == set(ENABLE_TAGS), "registry must cover exactly the 19 mechanisms"


def all_mechanisms() -> tuple[MechanismEntry, ...]:
    """All 19 registry entries, in the ``mechanism-interface.md`` §2 order (archetypes then tactics)."""
    return tuple(REGISTRY[tag] for tag in ENABLE_TAGS)


def ca_absent_count() -> int:
    """Number of TFO mechanisms whose operator family is absent from CA's table (SC-002)."""
    return sum(1 for entry in REGISTRY.values() if entry.overlaps_ca == "no")


#: Identifier allowlist (Principle VI, FR-043, SC-009): every value used as a mechanism tag,
#: archetype name, or displayed identifier anywhere in code or results. Built mechanically from
#: this registry, never hand-maintained, so it cannot silently drift.
IDENTIFIER_ALLOWLIST: frozenset[str] = frozenset(
    {tag.value for tag in MechanismTag}
    | {a.value for a in Archetype}
    | {entry.display_name for entry in REGISTRY.values()}
)
