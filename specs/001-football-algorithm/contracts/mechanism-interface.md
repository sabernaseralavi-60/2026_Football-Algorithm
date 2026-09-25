# Contract: Mechanism interface (all 19 mechanisms)

**Purpose.** This contract gives each mechanism in [mechanism-map.md](../mechanism-map.md) exactly
one named, independently switchable, independently testable unit. It fixes three things for each
one:

- its operator, stated without metaphor, which is the planning-level form of gate G1;
- its evaluation charge;
- its neutral default when disabled (gate G2).

It also fixes the order in which one engine iteration applies the mechanisms.

The *(prov.)* parameter defaults are listed in [data-model.md](../data-model.md) §A15 and are frozen
at gate G3.

## 1. Common signatures

```python
# Archetype moves (tfo/archetypes/<name>.py): one agent, one proposal, greedy unless stated
def move(i: int, ctx: MatchContext, rng: np.random.Generator) -> None

# Team-level tactics (tfo/tactics/<name>.py): whole-squad operations at their own clock
def apply(ctx: MatchContext, rng: np.random.Generator) -> None
```

- **`MatchContext`** bundles the objects of data-model.md Part A:
  - `squad`, `formation`, `role_sheet`, `ball`, `archive`, `tabu`, `clock`, `state_params`;
  - `account` (the only path to the objective);
  - `cfg`, `trace`.
- **Candidate proposals.** Every proposal passes through `offside.repair(x_new, x_old)` before it is
  evaluated. Every evaluation goes through `account.evaluate(X, tag)`.
- **Random numbers.** `rng` is the mechanism's own stream, spawned at a fixed registry index
  (research.md R11).
- **Disabled mechanisms.** When `cfg.enable[<mechanism>]` is false, the engine does not call the
  mechanism and uses its neutral default instead. The mechanism module itself contains no
  enable/disable logic.
- **Neutral move `N`** (tag `neutral`), used by disabled archetypes: y = x_i + σ·s_i·N(0, I),
  accepted greedily. σ is the global step scale and s_i the agent's stamina (research.md R14).

## 2. Mechanism table

"Evals" is the number of evaluations charged per invocation, under the mechanism's own tag. Each
"Unit test (key invariant)" entry lives in `tests/unit/test_<module>.py`.

### Player archetypes (8)

**1. Sweeper-Keeper** (FR-005)

- **Module:** `archetypes/sweeper_keeper.py`
- **Operator:** a bounded archive of the best points found, kept diverse by distance (data-model.md
  A5). It is updated on every evaluation through an account hook, and it supplies the points used
  for ball resets and Finisher restarts.
- **Evals:** 0
- **Clock:** every evaluation
- **Disabled:** archive size K = 1 (incumbent only)
- **Unit test:** `A[0]` always equals the incumbent; the separation between members is at least
  `min_sep`; the archive never exceeds K members.

**2. Zonal Centre-Back** (FR-006)

- **Module:** `archetypes/zonal_centre_back.py`
- **Operator:** y ~ U(stratum_k), where stratum_k is agent k's cell of the current Latin-hypercube
  stratification (A9); greedy against the agent's own fitness.
- **Evals:** 1
- **Clock:** per iteration; the partition is redrawn at each fixture
- **Disabled:** N
- **Unit test:** every proposal lies inside the agent's stratum; after a redraw, the strata are
  disjoint and their projections tile [0, 1].

**3. Overlapping Wing-Back** (FR-007)

- **Module:** `archetypes/overlapping_wing_back.py`
- **Operator:** with probability Jr (the manager scales this rate in CHASING), take the
  quasi-opposite point about the squad centroid c: o = 2c − x, then y = c + U(0, 1)⊙(o − c). Keep
  the better of x and y. With probability 1 − Jr, apply N.
- **Evals:** 1
- **Clock:** per iteration
- **Disabled:** N
- **Unit test:** y lies coordinate-wise between c and o; the keep-better rule holds.

**4. Deep-Lying Playmaker** (FR-008)

- **Module:** `archetypes/deep_lying_playmaker.py`
- **Operator:** the partner p is drawn uniformly from the slots at graph distance ≥ d_max − 1 from
  agent i on the formation lattice. y is the BLX-α blend of x_i and x_p (each coordinate uniform on
  the interval spanned by the two parents, widened by α times its length at both ends), accepted
  greedily. This is the declared long-range exception to FR-002.
- **Evals:** 1
- **Clock:** per iteration
- **Disabled:** N
- **Unit test:** the partner's graph distance is at least d_max − 1; y lies in the α-widened box.

**5. Box-to-Box Engine** (FR-009)

- **Module:** `archetypes/box_to_box.py`
- **Operator:** v = x_nbest(i) + F·(x_d − x_a). Here x_d is the neighbourhood member in the deepest
  line and x_a the one in the most advanced line (neighbourhood includes i; ties are broken at
  random). Then y = binomial crossover(x_i, v, CR), accepted greedily.
- **Evals:** 1
- **Clock:** per iteration
- **Disabled:** N
- **Unit test:** donors come only from N(i) ∪ {i}; x_d's line is at most x_a's line.

**6. Destroyer** (FR-010)

- **Module:** `archetypes/destroyer.py`
- **Operator:** among the pairs in N(i) ∪ {i} that are closer than r_niche, the worse member w of
  each pair is kicked: y = x_w + F·(x_r1 − x_r2), with r1 and r2 drawn from N(i). The kick is
  accepted **unconditionally**, because clearing displaces the loser whatever its fitness, and the
  better member is kept. If no pair is closer than r_niche, apply N.
- **Evals:** 1 per kick
- **Clock:** per iteration
- **Disabled:** N
- **Unit test:** the better member of each pair is never moved; the kicked agent lands outside the
  niche, or its kick is recorded as failing to leave it.

**7. Virtuoso** (FR-011)

- **Module:** `archetypes/virtuoso.py`
- **Operator:** a compass poll. Choose k coordinates in random order. For each, poll x ± h_i·e_j in
  turn and accept the first improvement. On success, h_i ← min(2h_i, h_max). If the whole poll
  fails, h_i ← max(h_i/2, h_min).
- **Evals:** ≤ 2k
- **Clock:** per iteration
- **Disabled:** N
- **Unit test:** the poll stops at the first improvement; the expand and contract rules hold; the
  mesh stays within [h_min, h_max].

**8. Finisher** (FR-012)

- **Module:** `archetypes/finisher.py`
- **Operator:** y = x_b + σ_L·s_i·Lévy(β), a step with Mantegna's heavy-tailed distribution centred
  on the ball, accepted greedily. After F_fail consecutive failures, restart from archive elite
  e ≠ the previous restart point, with a small Gaussian offset.
- **Evals:** 1 per jump (plus 1 per restart)
- **Clock:** per iteration; restarts are event-driven
- **Disabled:** N
- **Unit test:** jumps are centred on the ball, not on the incumbent; a restart never reuses the last
  restart index when K > 1.

### Team-level tactics (11)

**9. Formation** (FR-013, FR-002)

- **Module:** `tactics/formation.py`
- **Operator:** lattice shapes, toroidal von Neumann neighbour tables, graph distances, and re-lay on
  a change of shape (A3).
- **Evals:** 0
- **Clock:** when the manager changes shape
- **Disabled:** fully connected interaction; slot rows are kept
- **Unit test:** the three shapes exist for n; the ratio is monotone across them; a re-lay leaves X
  and f unchanged; the vacancy rule holds.

**10. Positional rotation** (FR-022)

- **Module:** `tactics/rotation.py`
- **Operator:** one deep-to-upfield pass per lane: if f(row r) < f(row r+1), with no wrap across the
  torus, swap the two agents' slots, and so their archetypes.
- **Evals:** 0
- **Clock:** fixture boundary
- **Disabled:** no swaps
- **Unit test:** only better-deeper/worse-upfield pairs swap; the role-sheet composition is
  preserved.

**11. Possession** (FR-014)

- **Module:** `tactics/possession.py`
- **Operator:** a chain of up to L passes. Each pass picks a receiver q from N(carrier) and proposes
  x_b' = x_b + U(0, 1)·(x_q − x_b). The pass is retained if f(x_b') ≤ f_b + τ.
  - The retained fraction is fed into the possession rate.
  - The chain ends on a lost pass, or once N_neutral_max consecutive neutral passes are reached.
  - After R_loss consecutive lost chains, the ball resets to an archive elite, and the location it
    leaves goes on the tabu list.
- **Evals:** ≤ L
- **Clock:** per iteration
- **Disabled:** the ball is not passed. It remains a focal point: at each iteration it is set to the
  best outfield agent, at 0 evals.
- **Unit test:** the τ acceptance rule holds; the neutral-pass cap stops plateau loops; receivers are
  always neighbours of the carrier.

**12. Pressing** (FR-015)

- **Module:** `tactics/pressing.py`
- **Operator:** the pressing set P = {i : ‖x_i − x_b‖ < ρ}, truncated to the ⌊0.5·n_out⌋ nearest
  agents. Each i ∈ P replaces its archetype move with y = x_b − A⊙|C⊙x_b − x_i|, where
  A = 2a·r₁ − a, C = 2r₂, and a shrinks linearly with t. Accepted greedily.
- **Evals:** 1 per presser
- **Clock:** per iteration; membership is event-driven
- **Disabled:** P = ∅
- **Unit test:** the cap on |P| holds; with ρ = 0 no agent presses.

**13. Counter-attack** (FR-016)

- **Module:** `tactics/counter_attack.py`
- **Operator:** triggered by an **event**, the same in TFO and TFO-static. The event is an accepted
  off-ball move with f(y) < f_b − Δ_mat·max(|f_b|, 1e-12) and ‖y − x_b‖ > d_trans.
  - The ball moves to y; the old ball location becomes tabu.
  - Each agent in the attacking line (the last row) then makes a burst of `burst_len` steps:
    y_k = x_b + s₀γ^k·N(0, I), accepted greedily, and the ball is updated whenever a step improves on
    it.
- **Evals:** ≤ `burst_len` × (number of attackers), truncated at the budget
- **Clock:** event-driven
- **Disabled:** no relocation and no burst
- **Unit test:** the burst's step sizes decay geometrically; the burst is truncated exactly at the
  budget; the trigger requires both the improvement and the distance conditions.

**14. Set pieces** (FR-017)

- **Module:** `tactics/set_pieces.py`
- **Operator:** every c iterations, run on the incumbent, following a fixed script that alternates
  corner, free kick, corner, free kick, and so on.
  - **Corner:** pick a random coordinate pair (j, k) and evaluate the 3 × 3 orthogonal design over
    {x − h, x, x + h} on those two coordinates: 8 new points.
  - **Free kick:** pick a random unit direction d, evaluate x ± h·d, and evaluate the vertex of the
    parabola through the three points when it is convex: up to 3 points.
  - Improvements go to the archive through the account.
- **Evals:** 8 (corner) or ≤ 3 (free kick)
- **Clock:** fixed schedule, the same in TFO and TFO-static; never adapted
- **Disabled:** no set pieces
- **Unit test:** the schedule and the rotation order are fixed; on a 1-D quadratic, the free kick
  hits the vertex exactly.

**15. Offside line** (FR-018)

- **Module:** `tactics/offside.py`
- **Operator:**
  - `repair(y, x_old)`: for each coordinate j outside [0, 1], y_j ← x_old,j + U(0, 1)·(bound_j −
    x_old,j).
  - ε-line: ε(t) = ε₀(1 − t/T_c)^cp, with ε-lexicographic comparison. It runs only in the ε
    experiment.
- **Evals:** 0
- **Clock:** every proposal
- **Disabled:** clipping; no ε-line
- **Unit test:** property-based checks that the repaired point is in the box, between x_old and the
  bound, and that points near the bound stay reachable; ε(T_c) = 0.

**16. Substitutions** (FR-019)

- **Module:** `tactics/substitutions.py`
- **Operator:** an agent with `stagnation ≥ W` and `stamina < s_sub` is replaced by u ~ U[0, 1]^D,
  with stamina 1 and fresh counters and mesh, up to the cap for the current fixture. CHASING raises
  the cap by a bounded increment. The outgoing position goes on the tabu list.
- **Evals:** 1 per substitute
- **Clock:** event-driven; capped per fixture
- **Disabled:** no substitutions
- **Unit test:** the cap is honoured; both trigger conditions are required; the tabu entry is
  written.

**17. Fatigue** (FR-020)

- **Module:** `tactics/fatigue.py`
- **Operator:** drain s_i ← max(s_min, s_i − κ‖Δx‖/√D) after each move; recover
  s_i ← min(1, s_i + r₀(1 − t)) at each fixture. Stamina scales every archetype step.
- **Evals:** 0
- **Clock:** per move and at each fixture
- **Disabled:** s ≡ 1
- **Unit test:** drain is monotone in distance; recovery shrinks with t; substitutes enter with
  s = 1.

**18. VAR review** (FR-021)

- **Module:** `tactics/var_review.py`
- **Operator:** every v iterations, audit each agent that moved since the last review against three
  checks: tabu zone; collision with another agent; loss of feasibility (only when constraints are
  exposed). A failing move is rolled back to (X_rev, f_rev) at zero cost, unless it produced a new
  best-so-far (aspiration).
- **Evals:** 0
- **Clock:** fixed schedule, the same in TFO and TFO-static
- **Disabled:** no rollback
- **Unit test:** the rollback costs 0 evals; aspiration keeps a move that set a new best; the
  incumbent survives any rollback.

**19. Manager** (FR-023 to FR-026)

- **Module:** `manager.py`
- **Operator:** the four-state machine of A8, with EMA inputs, priority guards, hysteresis and
  dwell. It sets the formation, ρ, τ, L, the rate multipliers and the substitution cap.
- **Evals:** 0
- **Clock:** adaptive, every iteration
- **Disabled:** **TFO-static**: the CONTROL vector is frozen and there is no CHASING
- **Unit test:** an oscillating input cannot cause state changes on consecutive iterations; HIGH_PRESS
  is never entered before t_press; CHASING is present only in TFO.

**Switchable count (FR-034).** Mechanisms 1 to 18 are each switched off one at a time, giving 18
single-off variants. Mechanism 19 switched off *is* TFO-static, which is a group-level variant.
The other group-level variants are G-topology (mechanisms 9 and 10 off) and the homogeneous squads
(research.md R14).

## 3. Engine iteration order (`tfo/engine.py`)

The order below is deterministic. Unit and integration tests pin it, because the order affects
reproducibility.

```text
init:   X ← default_rng(seed).random((30, D)); evaluate (tag init); archive, ball, formation, zones set
loop until BudgetExhausted:
  1  manager.update()                    # reads div, poss, drought, t → state_params (0 evals)
  2  possession.apply()                  # pass chain on the ball
  3  pressing.membership()               # P from ρ
  4  for i in outfield agents in slot order:
         pressing step if i∈P else archetype(role_sheet[slot[i]]).move(i)   # offside repair inside
         fatigue.drain(i)
         counter_attack.check_and_fire(i)   # event → relocation + burst
  5  substitutions.apply()
  6  if iteration % c == 0: set_pieces.apply()
  7  if iteration % v == 0: var_review.apply()
  8  if fixture boundary crossed: rotation → zones.redraw → fatigue.recover → substitution cap reset
  9  trace.record(iteration)
```

The keeper-archive update is a hook on every `account.evaluate` call, so it runs continuously, not
at a numbered step.
