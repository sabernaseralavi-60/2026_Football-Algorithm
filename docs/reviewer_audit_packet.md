# Reviewer Audit Packet: Total Football Optimizer (TFO)

This packet is the single artefact for User Story 1's Independent Test (spec.md): "give only the
mechanism map and the metaphor-free description to a reader unfamiliar with football; they can
state each mechanism's operator family and canonical source, and re-implement the algorithm without
any football term." It bundles three pieces, each generated directly from the code
(`src/tfo/registry.py`) so none of them can drift from the implementation (Principle I):

1. The operator-family table (all 19 mechanisms, family, canonical citation) -- `scripts/make_mechanism_table.py`.
2. The CA overlap audit (SC-002) -- `scripts/audit_overlap.py`.
3. The complete metaphor-free specification -- `docs/metaphor_free_description.md`.

## 1. Operator-family table

Every one of TFO's 19 mechanisms, mapped to a named operator family from the established
metaheuristics literature with at least one canonical citation (FR-042, SC-001).

| # | Mechanism | Module | Operator family | Canonical citation(s) | FR |
|---|---|---|---|---|---|
| 1 | Sweeper-Keeper | `tfo.archetypes.sweeper_keeper` | Elitism with a bounded hall-of-fame archive | De Jong (1975); Rosin & Belew (1997) | FR-005 |
| 2 | Zonal Centre-Back | `tfo.archetypes.zonal_centre_back` | Stratified / Latin-hypercube sampling, space partitioning | McKay et al. (1979) | FR-006 |
| 3 | Overlapping Wing-Back | `tfo.archetypes.overlapping_wing_back` | Quasi-opposition-based learning, generation jumping | Tizhoosh (2005); Rahnamayan et al. (2007) | FR-007 |
| 4 | Deep-Lying Playmaker | `tfo.archetypes.deep_lying_playmaker` | BLX-alpha crossover over small-world long-range links | Eshelman & Schaffer (1993); Watts & Strogatz (1998) | FR-008 |
| 5 | Box-to-Box Engine | `tfo.archetypes.box_to_box` | Neighbourhood-based differential mutation, DEGL-style local DE | Das et al. (2009) | FR-009 |
| 6 | Destroyer | `tfo.archetypes.destroyer` | Clearing / crowding-based niching | Petrowski (1996); Mahfoud (1995) | FR-010 |
| 7 | Virtuoso | `tfo.archetypes.virtuoso` | Compass / generalized pattern search | Hooke & Jeeves (1961); Torczon (1997) | FR-011 |
| 8 | Finisher | `tfo.archetypes.finisher` | Levy-flight (heavy-tailed) mutation with elite restart | Lee & Yao (2004); Mantegna (1994) | FR-012 |
| 9 | Formation | `tfo.tactics.formation` | Cellular (structured) population with dynamic grid-shape topology | Alba & Dorronsoro (2005); Kennedy & Mendes (2002) | FR-013 |
| 10 | Positional rotation | `tfo.tactics.rotation` | Rank-based role reassignment restricted to graph neighbours | Janson & Middendorf (2005) | FR-022 |
| 11 | Possession | `tfo.tactics.possession` | Threshold accepting | Dueck & Scheuer (1990) | FR-014 |
| 12 | Pressing | `tfo.tactics.pressing` | Distance-gated shrinking-encircling attraction | Mirjalili et al. (2014) | FR-015 |
| 13 | Counter-attack | `tfo.tactics.counter_attack` | Event-triggered basin hopping / iterated-local-search relocation | Wales & Doye (1997); Lourenco et al. (2003) | FR-016 |
| 14 | Set pieces | `tfo.tactics.set_pieces` | Fixed-frequency memetic local search: orthogonal-design sampling, successive parabolic interpolation | Leung & Wang (2001); Brent (1973) | FR-017 |
| 15 | Offside line | `tfo.tactics.offside` | Bound repair + epsilon-constrained feasibility ranking | Helwig et al. (2013); Takahama & Sakai (2006); Deb (2000) | FR-018 |
| 16 | Substitutions | `tfo.tactics.substitutions` | Stagnation-triggered random immigrants, capped | Grefenstette (1992) | FR-019 |
| 17 | Fatigue and fixture congestion | `tfo.tactics.fatigue` | Workload-clocked per-agent step-size annealing | Kirkpatrick et al. (1983) | FR-020 |
| 18 | VAR review | `tfo.tactics.var_review` | Deferred tabu audit with aspiration criterion: short-term memory plus rollback | Glover (1989) | FR-021 |
| 19 | The manager's tactical board | `tfo.manager` | Feedback-driven adaptive parameter control, state machine | Eiben et al. (1999) | FR-023,FR-024,FR-025,FR-026 |


## 2. CA overlap audit

Design-time: 11 of 19 mechanisms (57.9%) belong to operator families absent from CA's operator-family table. At-least-half claim holds: True.

Per-mechanism detail is in `mechanism-map.md`'s "Overlap audit against the Chess Algorithm (CA)"
table, which is committed prior art positioning, not code-generated (Principle I, FR-042).

## 3. Metaphor-free specification

The full text of `docs/metaphor_free_description.md` follows verbatim. It contains zero football
vocabulary (enforced by `scripts/check_metaphor_free.py`, tasks.md T114) and is sufficient on its
own to re-implement the algorithm.

---

# Metaphor-Free Algorithm Description

**Purpose.** This document specifies the algorithm (tasks.md T113; Principle I) in operator terms
only, so it can be re-implemented by a reader who has never seen the accompanying descriptive
vocabulary. Every equation and rule below (sections 1-16) is identical to the one the
implementation runs. A separate appendix at the end maps each numbered section to its
implementation module, for maintainers only; that appendix is not part of the specification and is
excluded from the metaphor-free check.

Nothing below depends on any topic outside this document. All notation is self-contained.

## 1. Search space, population, and notation

- Search space: the unit box `[0, 1]^D`. A wrapping layer maps to and from the caller's real box
  `[lb, ub]`; every operator below runs in the unit box.
- Population size `n = 30`, indexed `0, 1, ..., n-1`. Index `0` is the **archive-linked agent**;
  indices `1, ..., n-1` (`n_out = n - 1 = 29`) are **search agents**.
- Each agent `i` holds a position `X[i] in [0,1]^D`, a fitness value `f[i] = objective(X[i])`, a
  personal-best pair `(P[i], f_P[i])` with `f_P[i] <= f[i]` always, a step-scale multiplier
  `s[i] in [s_min, 1]`, a stagnation counter, and (for one operator role) a mesh size `h[i]`.
- Distances are Euclidean, normalised by the box diagonal `sqrt(D)`, unless stated otherwise.
- `t in [0, 1]` is the fraction of the evaluation budget `B` spent so far.
- Every operator below is **independently switchable**. When switched off, it is replaced by the
  **neutral operator** `N`: `y = x_i + sigma * s_i * z`, `z ~ Normal(0, I)`, accepted if
  `objective(y) <= f[i]` (with `y` clipped into range first, see §3).

## 2. Interaction graph

The `n_out = 29` search agents sit on the nodes of a 2-D toroidal grid with `lines * lanes` nodes,
where `lines * lanes >= n_out`; the surplus `lines*lanes - n_out` nodes are marked **vacant** and
hold no agent. Node `(0, c)` for all lanes `c` is called the **base row**; increasing row index
moves toward the **lead row** (`row = lines - 1`).

Three grid shapes are defined for `n_out = 29`:

| Shape | lines x lanes | neighbourhood-to-grid ratio |
|---|---|---|
| compact | 5 x 6 | ~0.40 |
| balanced | 3 x 10 | ~0.30 |
| spread | 2 x 15 | ~0.21 |

Each shape has exactly one vacant node, placed at the end of the lead row. Adjacency is the
4-neighbour (up/down/left/right) rule on the **torus** (row and column indices wrap modulo `lines`
and `lanes`), excluding vacant nodes from every neighbour list. Graph distance between two nodes is
the shortest-path hop count over this adjacency, restricted to non-vacant nodes.

A **disabled** interaction graph is the fully connected graph on the 29 non-vacant nodes (every
node adjacent to every other), with graph distance 1 between every pair; the base/lead row
assignment is kept unchanged.

Each search agent occupies exactly one grid node at a time (its "node index"); a fixed
**role-assignment table**, described next, maps node index to operator role and is never changed
by a change of grid shape.

## 3. Bound handling
Every candidate point `y` produced by any operator below is repaired against the position `x_old`
it was generated from, before being evaluated:

```
for each coordinate j where y_j < 0 or y_j > 1:
    bound_j = 0 if y_j < 0 else 1
    u ~ Uniform(0, 1)
    y_j <- x_old_j + u * (bound_j - x_old_j)
```

This keeps `y` in `[0, 1]^D`, on the segment between `x_old` and the violated bound, so points
arbitrarily close to a bound remain reachable. The **disabled** default is plain coordinate-wise
clipping to `[0, 1]`.

(A moving feasibility threshold `epsilon(t) = epsilon_0 * (1 - t/T_c)^cp` for `t < T_c`, else 0,
together with a two-key comparison "compare on the objective value when both points' constraint
violation is at most `epsilon(t)`, otherwise compare on violation first" exists for problems with
explicit constraints; it is out of scope for problems without them.)

## 4. Archive-linked agent
A bounded archive `A` of up to `K` points, with fitness values `f_A`, is updated on **every**
objective evaluation performed anywhere in the algorithm, as follows:

- If the evaluated point is a new global-best point, it always becomes `A[0]` (overwriting whatever
  was there).
- Otherwise, let `d_min` be its normalised distance to the nearest current archive member. It is
  admitted only if:
  - it is at least `min_sep` from every current member, **and**
  - either the archive has fewer than `K` members, or its value is better than the current worst
    member's value (in which case the worst member is replaced);
  - if it is better than some member but within `min_sep` of that member, it replaces that nearest
    member instead of being added.

The **disabled** default sets `K = 1` (the archive holds only the global-best point).

## 5. Operator roles

Twenty-nine search agents are partitioned, by a fixed table assigning node indices to roles (lowest
indices to roles 1-2 below, then roles 3-5, then roles 6-7), into 7 roles with default counts
`4, 4, 3, 6, 3, 5, 4` respectively (in the order listed). Each role below acts on one search agent
`i` at its own turn, producing one candidate `y` (repaired per §3, then evaluated), accepted or
rejected per its own rule.

### 5.1 Zone-sampling operator
The role's `m` agents each own one cell of a Latin-hypercube partition of `[0,1]^D` into `m^D`
equal cells, refreshed every epoch (§9): for each dimension `j`, an independent random permutation
`pi_j` of `{0, ..., m-1}` assigns agent `k`'s sub-interval `[pi_j(k)/m, (pi_j(k)+1)/m)` in
dimension `j`. Agent `k` proposes `y ~ Uniform(cell_k)` and accepts if `objective(y) <= f[i]`.

### 5.2 Reflection-jump operator
Let `c` be the centroid of all search agents' current positions. With probability `Jr` (scaled by
the controller in its diversification state, §10), propose the reflected-interpolated point
`o = 2c - x_i`, `y = c + u .* (o - c)` with `u ~ Uniform(0,1)^D` elementwise, and keep whichever of
`x_i, y` has the better objective value. With probability `1 - Jr`, apply the neutral operator `N`.

### 5.3 Long-range recombination operator
A partner node `p` is drawn uniformly among the nodes at graph distance at least `d_max - 1` from
`i`'s node (`d_max` = the current graph's diameter among non-vacant nodes) -- the graph's declared
long-range exception. `y` is the BLX-alpha blend of `x_i` and the partner's position `x_p`: each
coordinate is drawn uniformly from the interval spanned by the two parents' values on that
coordinate, widened by `alpha` times that interval's length at both ends. Accepted if
`objective(y) <= f[i]`.

### 5.4 Local differential operator
Let `N(i)` be `i`'s graph neighbours. Let `x_d` be the position of the neighbourhood member
(including `i`) whose node lies in the lowest-index row present in the neighbourhood, and `x_a` the
member whose node lies in the highest-index row present (ties broken uniformly at random). Let
`x_nbest` be the neighbourhood member (including `i`) with the best objective value. Propose
`v = x_nbest + F * (x_d - x_a)`, then `y` by binomial crossover of `x_i` and `v` with rate `CR`
(one coordinate always taken from `v`). Accept if `objective(y) <= f[i]`.

### 5.5 Clearing operator
For each neighbour `j in N(i)` whose normalised distance to `i` is below a niche radius `r`: the
member of `{i, j}` with the worse objective value, `w`, is displaced:
`y = x_w + F * (x_r1 - x_r2)`, with `r1, r2` drawn independently (with replacement if needed) from
`N(i)`. This displacement is applied **unconditionally** (whatever `objective(y)` turns out to be);
the better member of the pair is never moved. If no neighbour is within `r`, `i` applies the
neutral operator `N` instead.

### 5.6 Pattern-search operator
Agent `i` holds a mesh size `h[i]`. A poll chooses `k` coordinates in random order; for each, it
tries `x_i +/- h[i] * e_j` in turn (unit vector `e_j`) and stops at the first improving point,
accepting it. On success, `h[i] <- min(2 h[i], h_max)`. If every trial in the poll fails,
`h[i] <- max(h[i]/2, h_min)` and `i` does not move.

### 5.7 Heavy-tailed operator
Propose `y = F_point + sigma_L * s_i * L`, where `F_point` is the position of the algorithm's
**shared focal point** (§7, distinct from the global-best point) and `L` is a symmetric
Mantegna-algorithm Levy-stable step of tail index `beta`. Accept if `objective(y) <= f[i]`, and
reset a per-agent failure counter to 0; otherwise increment it. After `F_fail` consecutive
failures, `i` **restarts unconditionally** from an archive member (§4) other than the one it last
restarted from, plus a small Gaussian offset, and its failure counter resets to 0.

## 6. Positional-swap operator
At every epoch boundary (§9): for every lane (grid column) and every adjacent row pair `(r, r+1)`
with `r` from the base row upward (no wraparound across the torus for this rule), if the agent at
row `r` has a strictly better objective value than the agent at row `r+1`, the two agents' node
indices are swapped (and therefore their operator roles, since roles are read through the
role-assignment table indexed by node). The role-assignment table itself never changes; only the
node <-> agent correspondence does.

## 7. Shared focal point and drift chain
A point `F` distinct from the global-best point, held by a "holder" agent, is advanced by a chain of
up to `L` drift steps per iteration: at each step, a receiver `q` is drawn from the holder's graph
neighbours, and `F' = F + u .* (x_q - F)`, `u ~ Uniform(0,1)^D`, is proposed. The step is **kept**
if `objective(F') <= f_F + tau` (`tau` a retention threshold that may be 0, giving strict
non-regression, or slightly positive, allowing neutral drift); the chain then continues from the
new `F'` with `q` as the new holder. The chain stops on a rejected step, or after
`N_neutral_max` consecutive **retained-but-unchanged-value** steps. After `R_loss` consecutive
chains that ended in a rejected step, `F` is reset to a different archive member (§4), and the
position it leaves is recorded in the forbidden-zone list (§11).

The **disabled** default: `F` is not advanced by drift steps; every iteration it is simply set to
the best-valued search agent's current position, at no evaluation cost.

## 8. Encircling operator
The encircling set is every search agent within a controller-set radius `rho` of `F`, truncated to
the nearest `floor(0.5 * n_out)` such agents. Every agent `i` in this set replaces its role's
operator for this iteration with:

```
a = 2 * (1 - t)                      # shrinks linearly with budget fraction t
A = 2 a r1 - a,  C = 2 r2,  r1, r2 ~ Uniform(0,1)^D
y = F_point - A .* |C .* F_point - x_i|
```

accepted if `objective(y) <= f[i]`. `rho = 0` empties the set.

## 9. Epochs and step-scale annealing

The run is divided into `n_epochs` **epochs**, measured in evaluations, not iterations: epoch `k`
ends at the first iteration boundary where the cumulative evaluation count reaches
`k * B / n_epochs`. At every epoch boundary, in order: the positional-swap operator (§6) runs,
the zone-sampling partition (§5.1) is redrawn, step-scales recover, and the reinitialisation counter
(§12) resets.

After every accepted move, an agent's step-scale drains:
`s_i <- max(s_min, s_i - kappa * ||delta_x|| / sqrt(D))`. At every epoch boundary it recovers:
`s_i <- min(1, s_i + r0 * (1 - t))` (recovery shrinks as the run proceeds). A reinitialised agent
(§12) enters with `s_i = 1`. The **disabled** default holds `s_i = 1` for every agent always.

## 10. Adaptive controller
A 4-state controller reads, once per iteration: the EMA of the mean normalised distance of every
search agent to the population centroid (`div`), the EMA of the drift-chain retention rate
(`poss`), the number of iterations since the last **material** improvement of the global best
(`drought`; a material improvement is `(f_old - f_new) > delta_mat * max(|f_old|, 1e-12)`), and `t`.
Each threshold used below has separate "enter" and "exit" values (a hysteresis band), and a state
change is only allowed after at least `dwell_min` iterations in the current state. In priority
order:

1. If `drought >= G_max`, or (`div` is low **and** `t < t_late`): enter the **diversify** state.
2. Else if `div` is low **and** `t >= t_intensify` **and** `poss` is high: enter the **intensify-local**
   state.
3. Else if `div` is high: enter the **explore-build** state.
4. Else: the **balanced-control** state.

Each state sets its own interaction-graph shape, encircling radius `rho`, retention threshold
`tau`, drift-chain length `L`, a set of per-role rate multipliers, and a bounded increment to the
reinitialisation cap (§12; only the diversify state raises it). The **disabled** variant (the
ablation twin) fixes the balanced-control state's parameters for the whole run and never evaluates
the guards above, so its diversify state is never reached.

## 11. Event-triggered relocation
Whenever any accepted off-focal-point move `y` (evaluated value `f_y`) satisfies both
`f_y < f_F - Delta_mat * max(|f_F|, 1e-12)` and `||y - F_point|| > d_trans` (normalised distance),
the shared focal point relocates to `y` immediately (its old position is recorded in the forbidden-
zone list, §12), and every agent on the lead row then takes a burst of up to `burst_len` steps of
geometrically shrinking scale:
`y_k = F_point + s0 * gamma^k * z_k`, `z_k ~ Normal(0, I)`, `k = 0, ..., burst_len - 1`, each
accepted if it improves that agent's own value; the focal point itself is further updated whenever
one of these steps improves upon it. This rule is identical whether or not the controller (§10) is
enabled.

## 12. Forbidden-zone list and reinitialisation
A FIFO list of up to `T_max` zone centres, each with radius `r_tabu`, records positions vacated by a
reinitialisation (below) or by a focal-point reset (§7). Any search agent whose personal-best value
has not improved for `W` iterations **and** whose step-scale is below a threshold is
**reinitialised**: replaced by a uniformly random point in `[0,1]^D`, with step-scale reset to 1 and
its role-specific counters and mesh reset, up to a per-epoch cap (raised by a bounded amount in the
diversify state). The vacated position is added to the forbidden-zone list.

## 13. Fixed-schedule local probes
Every `c` iterations, on the current global-best point `x*`, alternating on a **fixed, never
adapted** schedule:

- **Orthogonal probe:** pick a random coordinate pair `(j, k)`; evaluate the `3x3` orthogonal design
  over `{x*-h, x*, x*+h}` on those two coordinates (8 new points, the centre already known).
- **Line probe:** pick a random unit direction `d`; evaluate `x* +/- h*d`; fit the unique quadratic
  through the three points `(x*-h*d, x*, x*+h*d)` and, if it is convex, evaluate its vertex (up to 3
  new points total).

Any improving point found here also updates the archive (§4) through the same evaluation channel as
every other operator.

## 14. Periodic audit
Every `v` iterations, every agent that moved since the previous audit is checked against three
conditions: its current position lies within `r_tabu` of a forbidden-zone centre; its current
position lies within `r_coll` of another agent's (in which case the worse of the two fails); or (on
problems with explicit constraints only) it lost feasibility although its pre-move position was
feasible. A failing agent is rolled back to its position and value as of the previous audit, **at
no evaluation cost**, unless its move set a new global-best value in the meantime (in which case it
is kept regardless). The snapshot is refreshed for every agent after the audit runs.

## 15. Accounting

Every evaluation performed by any operator above is charged to that operator's own counter; the
neutral operator (used only when an operator is switched off) has its own counter. The controller,
positional-swap operator, step-scale annealing, and periodic audit never themselves call the
objective function; their counters are always exactly 0. The sum of every counter always equals the
total number of evaluations performed, which never exceeds the budget `B`: a batch that would
exceed the remaining budget is truncated to exactly the remaining count before the run stops.

## 16. One iteration, in order

```
1. controller reads its inputs and sets this iteration's parameters (§10)         [0 evaluations]
2. drift-chain step on the shared focal point (§7)
3. encircling-set membership recomputed (§8)
4. for every search agent, in ascending node-index order:
       if in the encircling set: encircling step (§8)
       else: this agent's role operator (§5), or the neutral operator if its role is disabled
       step-scale drain for this agent (§9)
       event-triggered relocation check (§11)
5. reinitialisation sweep (§12)
6. every c iterations: fixed-schedule local probe (§13)
7. every v iterations: periodic audit (§14)
8. if an epoch boundary was crossed this iteration: positional swap, zone redraw,
   step-scale recovery, reinitialisation-cap reset, in that order (§9, §6)
9. record this iteration's controller state and cumulative evaluation count
```

The run stops the instant the evaluation budget is exhausted, at any point in this sequence,
without evaluating a single additional point.

---

## Appendix: implementation cross-reference (not part of the metaphor-free specification)

This appendix exists only to help maintainers locate each operator in the codebase. It is not
part of the specification above -- everything needed to re-implement the algorithm is in
sections 1-16 -- and it is deliberately excluded from the metaphor-free scan
(`scripts/check_metaphor_free.py` stops reading at this heading).

- 3. Bound handling: `tfo/tactics/offside.py`
- 4. Archive-linked agent: `tfo/archetypes/sweeper_keeper.py`
- 5.1 Zone-sampling operator: `zonal_centre_back.py`
- 5.2 Reflection-jump operator: `overlapping_wing_back.py`
- 5.3 Long-range recombination operator: `deep_lying_playmaker.py`
- 5.4 Local differential operator: `box_to_box.py`
- 5.5 Clearing operator: `destroyer.py`
- 5.6 Pattern-search operator: `virtuoso.py`
- 5.7 Heavy-tailed operator: `finisher.py`
- 6. Positional-swap operator: `tactics/rotation.py`
- 7. Shared focal point and drift chain: `tactics/possession.py`
- 8. Encircling operator: `tactics/pressing.py`
- 9. Epochs and step-scale annealing: `tactics/fatigue.py`, `clock.py`
- 10. Adaptive controller: `manager.py`
- 11. Event-triggered relocation: `tactics/counter_attack.py`
- 12. Forbidden-zone list and reinitialisation: `tactics/substitutions.py`, `squad.py`
- 13. Fixed-schedule local probes: `tactics/set_pieces.py`
- 14. Periodic audit: `tactics/var_review.py`

