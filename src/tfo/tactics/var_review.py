"""VAR review (mechanism-interface.md §2.18, FR-021; data-model.md A12).

Operator: every v iterations, audit each agent that moved since the last review against three
checks: tabu zone; collision with another agent; loss of feasibility (only when constraints are
exposed, out of scope for this pass). A failing move is rolled back to (X_rev, f_rev) at zero cost,
unless it produced a new best-so-far (aspiration). After the review, the snapshots are refreshed
(Deferred tabu audit with aspiration criterion: short-term memory plus rollback; Glover 1989).
"""

from __future__ import annotations

from tfo.squad import normalized_distance


def _fails_review(i: int, squad, tabu, collision_radius: float) -> bool:
    if tabu.is_tabu(squad.X[i]):
        return True
    n = squad.X.shape[0]
    for j in range(n):
        if j == i:
            continue
        if float(normalized_distance(squad.X[i], squad.X[j])) < collision_radius:
            # "the worse agent's move fails" -- if i is not strictly better than j, i fails.
            if squad.f[i] >= squad.f[j]:
                return True
    return False


def apply(ctx) -> int:
    """Runs the review; returns the number of agents rolled back."""
    squad = ctx.squad
    tabu = ctx.tabu
    collision_radius = ctx.cfg.operators.collision_radius

    n_rollbacks = 0
    n = squad.X.shape[0]
    for i in range(n):
        if not squad.moved_since_rev[i]:
            continue
        if squad.produced_best_since_rev[i]:
            continue  # aspiration: a move that set a new best is always kept
        if _fails_review(i, squad, tabu, collision_radius):
            squad.rollback(i)
            n_rollbacks += 1

    squad.refresh_review_snapshot()
    return n_rollbacks
