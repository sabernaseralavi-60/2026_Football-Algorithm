"""RunTrace: TacticalSegment run-length encoding, MechanismEvalCount, per-run summaries
(data-model.md A14)."""

from __future__ import annotations

from dataclasses import dataclass, field, replace

from tfo.registry import MechanismTag


@dataclass(frozen=True)
class TacticalSegment:
    state: str
    iter_start: int
    iter_end: int  # exclusive
    eval_start: int
    eval_end: int


@dataclass
class RunTrace:
    segments: list[TacticalSegment] = field(default_factory=list)
    mechanism_evals: dict[str, int] = field(default_factory=dict)
    transitions: int = 0
    counter_attacks: int = 0
    substitutions: int = 0
    var_rollbacks: int = 0
    set_pieces: int = 0

    def record_iteration(self, state: str, iteration: int, evals_used: int) -> None:
        if self.segments and self.segments[-1].state == state:
            last = self.segments[-1]
            self.segments[-1] = replace(last, iter_end=iteration + 1, eval_end=evals_used)
            return
        if self.segments:
            self.transitions += 1
            eval_start = self.segments[-1].eval_end
        else:
            eval_start = 0
        self.segments.append(
            TacticalSegment(
                state=state,
                iter_start=iteration,
                iter_end=iteration + 1,
                eval_start=eval_start,
                eval_end=evals_used,
            )
        )

    def finalize_mechanism_evals(self, evals_by_tag: dict[MechanismTag, int]) -> None:
        self.mechanism_evals = {tag.value: count for tag, count in evals_by_tag.items()}

    def record_counter_attack(self) -> None:
        self.counter_attacks += 1

    def record_substitution(self) -> None:
        self.substitutions += 1

    def record_var_rollback(self) -> None:
        self.var_rollbacks += 1

    def record_set_piece(self) -> None:
        self.set_pieces += 1

    def summary(self, total_iterations: int, final_possession_rate: float) -> dict:
        occupancy: dict[str, int] = {}
        for seg in self.segments:
            occupancy[seg.state] = occupancy.get(seg.state, 0) + (seg.iter_end - seg.iter_start)
        occ_frac = (
            {s: c / total_iterations for s, c in occupancy.items()} if total_iterations > 0 else {}
        )
        return {
            "occupancy": occ_frac,
            "n_transitions": self.transitions,
            "counter_attacks": self.counter_attacks,
            "substitutions": self.substitutions,
            "var_rollbacks": self.var_rollbacks,
            "set_pieces": self.set_pieces,
            "final_possession_rate": final_possession_rate,
        }
