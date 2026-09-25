"""The TFO engine: the 9-step iteration order of mechanism-interface.md §3.

Wires every mechanism module behind its `cfg.enable` flag with the documented neutral fallback,
and terminates cleanly on `BudgetExhausted` from any depth.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Optional

import numpy as np

from tfo import neutral
from tfo.account import BudgetExhausted, EvalAccount
from tfo.archetypes import (
    box_to_box,
    deep_lying_playmaker,
    destroyer,
    finisher,
    overlapping_wing_back,
    sweeper_keeper,
    virtuoso,
    zonal_centre_back,
)
from tfo.clock import MatchClock
from tfo.config import StateParameterVector, TFOConfig
from tfo.manager import Manager, TacticalState
from tfo.registry import ARCHETYPE_TAG, Archetype, DEFAULT_ARCHETYPE_COUNTS, MechanismTag
from tfo.rng import StreamBank
from tfo.squad import Ball, KeeperArchive, RoleSheet, Squad, TabuRegister, normalized_distance
from tfo.tactics import (
    counter_attack,
    fatigue,
    formation as formation_mod,
    offside,
    possession,
    pressing,
    rotation,
    set_pieces,
    substitutions,
    var_review,
)
from tfo.trace import RunTrace

_ARCHETYPE_MOVE: dict[Archetype, Callable] = {
    Archetype.SWEEPER_KEEPER: None,  # the Sweeper-Keeper is a hook, not a per-iteration move
    Archetype.ZONAL_CENTRE_BACK: zonal_centre_back.move,
    Archetype.OVERLAPPING_WING_BACK: overlapping_wing_back.move,
    Archetype.DEEP_LYING_PLAYMAKER: deep_lying_playmaker.move,
    Archetype.BOX_TO_BOX: box_to_box.move,
    Archetype.DESTROYER: destroyer.move,
    Archetype.VIRTUOSO: virtuoso.move,
    Archetype.FINISHER: finisher.move,
}


def _effective_role_counts(cfg: TFOConfig) -> dict[Archetype, int]:
    if cfg.homogeneous_archetype is not None:
        n_out = cfg.squad.n - 1
        return {cfg.homogeneous_archetype: n_out}
    return dict(cfg.squad.role_counts)


@dataclass
class MatchContext:
    """Bundles the objects every mechanism reads (mechanism-interface.md §1)."""

    squad: Squad
    formation: object
    role_sheet: RoleSheet
    ball: Ball
    archive: KeeperArchive
    tabu: TabuRegister
    clock: MatchClock
    account: EvalAccount
    cfg: TFOConfig
    trace: RunTrace
    zones: Optional[object] = None
    state_params: StateParameterVector = None  # type: ignore[assignment]


def _slot_order_outfield(squad: Squad) -> list[int]:
    return sorted(range(1, squad.n), key=lambda i: int(squad.slot[i]))


def _diversity(squad: Squad) -> float:
    outfield = squad.X[1:]
    if outfield.shape[0] == 0:
        return 0.0
    centroid = outfield.mean(axis=0)
    dists = normalized_distance(outfield, centroid)
    return float(np.mean(dists))


def run(
    cfg: TFOConfig,
    objective: Callable[[np.ndarray], np.ndarray],
    d: int,
    budget: int,
    seed: int,
    constraints: Optional[Callable[[np.ndarray], np.ndarray]] = None,
    callback: Optional[Callable[..., None]] = None,
) -> tuple[EvalAccount, RunTrace, MatchContext]:
    """Runs TFO to completion (or until the budget is spent) and returns the account, the trace,
    and the final MatchContext (for callers, such as `api.py`, that need final squad/ball state)."""
    n = cfg.squad.n

    # contract C6: TFO's first draw is exactly default_rng(seed).random((n, D)).
    init_rng = np.random.default_rng(seed)
    X_init = init_rng.random((n, d))

    account = EvalAccount(budget=budget, objective=objective, d=d)

    squad = Squad.initialize(n=n, d=d, rng=init_rng, mesh_init=cfg.operators.mesh_h_init)
    squad.X[:] = X_init

    n_init = min(n, budget)
    f_init = np.full(n, np.inf)
    if n_init > 0:
        try:
            f_partial = account.evaluate(X_init[:n_init], MechanismTag.INIT)
            f_init[:n_init] = f_partial
        except BudgetExhausted:
            pass
    squad.set_initial_fitness(f_init)

    # Disabled Sweeper-Keeper (mechanism-interface.md §2.1): archive size K = 1 (incumbent only).
    archive_k = cfg.operators.archive_k if cfg.enable[MechanismTag.SWEEPER_KEEPER] else 1
    archive = KeeperArchive(k=archive_k, min_sep=cfg.operators.archive_min_sep, d=d)
    account.add_hook(lambda x, f, is_new: archive.on_evaluation(x, f, is_new))
    # The hook was registered AFTER the init batch already ran; replay it now so the archive still
    # sees every initial point (Sweeper-Keeper's archive-update hook fires "on every account.evaluate
    # call", including init).
    if account.x_best is not None:
        best_idx = int(np.argmin(f_init[:n_init])) if n_init > 0 else None
        for idx in range(n_init):
            archive.on_evaluation(X_init[idx], float(f_init[idx]), idx == best_idx)

    role_counts = _effective_role_counts(cfg)
    role_sheet = RoleSheet.layout(role_counts, n_slots=30)

    trace = RunTrace()
    bank = StreamBank(seed)

    initial_state_params = cfg.states["CONTROL"]
    formation = formation_mod.Formation.build(
        initial_state_params.formation,
        n_out=n - 1,
        fully_connected=not cfg.enable[MechanismTag.FORMATION],
    )

    n_zonal = role_counts.get(Archetype.ZONAL_CENTRE_BACK, 0)
    zones = (
        zonal_centre_back.Zones.redraw(m=n_zonal, d=d, rng=bank.stream(MechanismTag.ZONAL_CENTRE_BACK))
        if n_zonal > 0
        else None
    )

    if n > 1:
        outfield_slice = squad.f[1:]
        best_outfield = 1 + int(np.argmin(outfield_slice)) if np.any(np.isfinite(outfield_slice)) else 1
    else:
        best_outfield = 0
    ball = Ball(x_b=squad.X[best_outfield].copy(), f_b=float(squad.f[best_outfield]), carrier=best_outfield)

    tabu = TabuRegister(t_max=cfg.operators.tabu_max, r_tabu=cfg.operators.tabu_radius, d=d)

    clock = MatchClock(budget=budget, n_fixtures=cfg.operators.n_fixtures)

    manager: Optional[Manager] = Manager(cfg.manager, cfg.states) if cfg.enable[MechanismTag.MANAGER] else None

    ctx = MatchContext(
        squad=squad,
        formation=formation,
        role_sheet=role_sheet,
        ball=ball,
        archive=archive,
        tabu=tabu,
        clock=clock,
        account=account,
        cfg=cfg,
        trace=trace,
        zones=zones,
        state_params=initial_state_params,
    )

    subs_used_this_fixture = [0]

    def _on_rotation():
        if cfg.enable[MechanismTag.ROTATION]:
            rotation.apply(ctx)

    def _on_zonal_redraw():
        if ctx.zones is not None:
            ctx.zones = zonal_centre_back.Zones.redraw(
                m=n_zonal, d=d, rng=bank.stream(MechanismTag.ZONAL_CENTRE_BACK)
            )

    def _on_stamina_recovery():
        if cfg.enable[MechanismTag.FATIGUE]:
            fatigue.recover_all(squad, cfg.operators.fatigue_r0, clock.t)

    def _on_sub_cap_reset():
        subs_used_this_fixture[0] = 0

    clock.on_boundary(
        rotation=_on_rotation,
        zonal_redraw=_on_zonal_redraw,
        stamina_recovery=_on_stamina_recovery,
        substitution_cap_reset=_on_sub_cap_reset,
    )

    last_f_best_for_manager = account.f_best
    set_piece_call_index = 0
    iteration = 0

    try:
        while account.evals_used < budget:
            evals_before = account.evals_used

            # --- step 1: manager ---
            div = _diversity(squad)
            tried = ball.passes_tried
            retained = ball.passes_retained
            poss_rate = retained / tried if tried > 0 else 0.5
            if manager is not None:
                material_improvement = (
                    last_f_best_for_manager - account.f_best
                    > cfg.manager.delta_mat * max(abs(last_f_best_for_manager), 1e-12)
                )
                last_f_best_for_manager = account.f_best
                state_params = manager.update(
                    div=div, poss=poss_rate, material_improvement=material_improvement, t=clock.t
                )
                if manager.state == TacticalState.CHASING:
                    pass  # only reachable when the manager is enabled (TFO), by construction
                if formation.name != state_params.formation:
                    formation = formation_mod.Formation.build(
                        state_params.formation,
                        n_out=n - 1,
                        fully_connected=not cfg.enable[MechanismTag.FORMATION],
                    )
                    ctx.formation = formation
                ctx.state_params = state_params
            else:
                state_params = cfg.states["CONTROL"]
                ctx.state_params = state_params

            # --- step 2: possession ---
            if cfg.enable[MechanismTag.POSSESSION]:
                possession.apply(ctx, bank.stream(MechanismTag.POSSESSION))
            else:
                possession.apply_disabled(ball, squad)

            # --- step 3: pressing membership ---
            P = pressing.membership(ctx) if cfg.enable[MechanismTag.PRESSING] else []
            P_set = set(P)

            # --- step 4: per-agent moves ---
            for i in _slot_order_outfield(squad):
                x_before = squad.X[i].copy()

                if i in P_set:
                    pressing.step(i, ctx, bank.stream(MechanismTag.PRESSING))
                else:
                    slot_i = int(squad.slot[i])
                    archetype = role_sheet.archetype_at(slot_i)
                    if archetype is not None:
                        tag = ARCHETYPE_TAG[archetype]
                        if cfg.enable[tag] and archetype != Archetype.SWEEPER_KEEPER:
                            move_fn = _ARCHETYPE_MOVE[archetype]
                            move_fn(i, ctx, bank.stream(tag))
                        elif archetype != Archetype.SWEEPER_KEEPER:
                            y = neutral.propose(
                                squad.X[i], cfg.operators.neutral_sigma, squad.stamina[i], bank.stream(tag)
                            )
                            y = offside.repair(y, squad.X[i], bank.stream(tag))
                            f_y = float(account.evaluate(y[None, :], MechanismTag.NEUTRAL)[0])
                            if f_y <= squad.f[i]:
                                squad.update_agent(i, y, f_y)

                if cfg.enable[MechanismTag.FATIGUE]:
                    fatigue.drain_agent(
                        squad, i, x_before, cfg.operators.fatigue_kappa, cfg.operators.stamina_min
                    )

                if cfg.enable[MechanismTag.COUNTER_ATTACK]:
                    if counter_attack.check_and_fire(
                        i, squad.X[i], float(squad.f[i]), ctx, bank.stream(MechanismTag.COUNTER_ATTACK)
                    ):
                        trace.record_counter_attack()

            # --- step 5: substitutions ---
            if cfg.enable[MechanismTag.SUBSTITUTIONS]:
                cap_now = cfg.operators.substitution_cap + (
                    state_params.substitution_cap_increment
                )
                remaining_cap = max(0, cap_now - subs_used_this_fixture[0])
                substituted = substitutions.apply(
                    ctx, bank.stream(MechanismTag.SUBSTITUTIONS), cap_override=remaining_cap, start_index=1
                )
                subs_used_this_fixture[0] += len(substituted)
                for _ in substituted:
                    trace.record_substitution()

            # --- step 6: set pieces (fixed schedule) ---
            if iteration % cfg.operators.set_piece_period == 0 and cfg.enable[MechanismTag.SET_PIECES]:
                set_pieces.apply(set_piece_call_index, ctx, bank.stream(MechanismTag.SET_PIECES))
                set_piece_call_index += 1
                trace.record_set_piece()

            # --- step 7: VAR review (fixed schedule) ---
            if iteration % cfg.operators.var_review_period == 0 and cfg.enable[MechanismTag.VAR_REVIEW]:
                n_rollbacks = var_review.apply(ctx)
                for _ in range(n_rollbacks):
                    trace.record_var_rollback()

            # --- step 8: fixture boundary ---
            evals_this_iter = account.evals_used - evals_before
            clock.advance(evals_this_iter)

            # --- step 9: trace ---
            state_name = manager.state.value if manager is not None else "CONTROL"
            trace.record_iteration(state_name, iteration, account.evals_used)
            if callback is not None:
                callback(
                    iteration=iteration,
                    evals_used=account.evals_used,
                    f_best=account.f_best,
                    state=state_name,
                )

            clock.tick_iteration()
            iteration += 1
    except BudgetExhausted:
        pass

    trace.finalize_mechanism_evals(account.evals_by_tag)
    return account, trace, ctx
