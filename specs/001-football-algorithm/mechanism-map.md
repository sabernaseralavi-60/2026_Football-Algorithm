# Mechanism Map: Total Football Optimizer (TFO)

**Name.** The algorithm is the **Total Football Optimizer (TFO)**, and its ablation twin, the
identical operator set with the adaptive control layer switched off, is **TFO-static**. "The
Football Algorithm" stays as the informal series title next to the sibling *Chess Algorithm (CA)*,
but it is not used as the formal name, because the acronym "FA" already belongs to the Firefly
Algorithm, one of the most-cited metaheuristics in the field, and would be ambiguous in every
results table. *Total football* is a tactical doctrine, not a person: outfield players swap
positions freely while the team keeps its shape. That is what TFO does. Agents keep a formation (an
interaction graph) while roles, focus and shape all shift underneath it. The long-range
recombination archetype is called the **Deep-Lying Playmaker**, not the *Regista*. The Modernized
Tiki-taka Algorithm (MTTA; Song & Zhao, 2026), a direct baseline, already uses "regista" and "long
cross-field pass" for a different mechanism, a success-based step-size factor. Reusing the word
would put two unrelated operators under one label in the same comparison tables.

**Why this is not a chess reskin.** CA arranges heterogeneous pieces around one incumbent. Every
piece relates to the whole population through the King, so its interaction structure is
effectively a star, and its adaptive layer changes *how often* each move fires. TFO changes three
structural axes that CA held fixed. (1) **Interaction structure.** Agents interact only along the
edges of a *formation graph* (a lines × lanes pitch lattice), and the formation's shape is itself a
control variable. Cellular-EA takeover theory then yields a falsifiable prediction: compact
formations exploit and stretched ones explore. CA has nothing equivalent. (2) **Search focus.** A
*ball* separate from the incumbent is carried across the graph by a threshold-accepting chain of
passes. Transitions such as turnovers and counter-attacks are *events* triggered by where
improvements occur, not phases read off a clock or a divergence threshold. (3) **Temporal
control.** TFO deliberately runs three kinds of clock side by side: *adaptive* (the manager's
state machine), *event-driven* (counter-attack, substitution, pressing) and *fixed-schedule* (set
pieces, VAR). One algorithm can therefore measure whether rehearsed or adaptive intensification
pays. VAR, a deferred audit that can overturn moves that were already accepted, and the moving
offside ε-line have no analogue in CA. By operator family, 11 of TFO's 19 mechanisms fall in
families that do not appear in CA's operator-family table (see the overlap audit below).

## Mapping table

| Football concept | Algorithmic mechanism | Operator family |
|---|---|---|
| **Player archetypes** | | |
| Sweeper-Keeper (1 agent) | Holds a small, distance-diverse archive of best-so-far solutions and is never lost; play restarts from it (ball reset, origin of the Finisher's restarts) | Elitism with a bounded hall-of-fame archive (De Jong 1975; Rosin & Belew 1997) |
| Zonal Centre-Back | Explores only inside its assigned stratum of a partition of the search box; zones are redrawn at every fixture boundary, so no region is left unmarked | Stratified / Latin-hypercube sampling, space partitioning (McKay et al. 1979) |
| Overlapping Wing-Back | "Switches the play": evaluates the quasi-opposite of its position about the squad centroid and keeps the better of the two | Quasi-opposition-based learning, generation jumping (Tizhoosh 2005; Rahnamayan et al. 2007) |
| Destroyer (ball-winning midfielder) | Contests duels: when two agents fall inside a niche radius, the worse one is dispossessed and relocated out of the niche by a differential kick | Clearing / crowding-based niching (Pétrowski 1996; Mahfoud 1995) |
| Deep-Lying Playmaker | Long diagonal pass: recombines with a partner at maximal graph distance in the formation, bypassing local topology. *Prior art (full text):* in the football family a "long pass" always means a long *step*. In FbOA it appears in prose only, with no equation (related-work §2.12). In MTTA it is the step enlarged by the adaptive factor, and MTTA calls that midfielder mechanism the "regista" (related-work §2.10). TFO's "long" is graph distance to a recombination partner. This archetype was therefore renamed from "Regista" (see the naming note above) | BLX-α crossover over small-world long-range links (Eshelman & Schaffer 1993; Watts & Strogatz 1998) |
| Box-to-Box Engine | Links defence and attack: a differential move built from its neighbourhood best plus a defender-minus-forward difference vector | Neighbourhood-based differential mutation, DEGL-style local DE (Das et al. 2009) |
| Virtuoso (close-control dribbler) | Beats defenders one at a time: polls tiny ± steps along a few coordinates, takes the first improvement, and expands the mesh on success or contracts it on failure | Compass / generalized pattern search (Hooke & Jeeves 1961; Torczon 1997) |
| Finisher (explosive centre-forward) | Mostly quiet, occasionally explosive: heavy-tailed jumps around the ball; after repeated misses it restarts from a different Sweeper-Keeper archive elite. *Prior art (full text):* FTTA and IFTTA already mutate the *incumbent* with a Cauchy term whose weight decays as 1/k (related-work §2.11). The Finisher's jumps are centred on the ball, keep their heavy tail, and end in an elite restart | Lévy-flight (heavy-tailed) mutation with elite restart (Lee & Yao 2004; Mantegna 1994) |
| **Team-level tactics** | | |
| Formation (4-4-2, 4-3-3, back five …) | The squad sits on a lines × lanes pitch lattice, and each agent interacts only with its von Neumann teammates; the formation is the lattice's shape (compact ↔ stretched). *Prior art (full text):* the Soccer Match Algorithm's "4-4-2" only counts roles among one solution's decision variables, and its partners are chosen over the whole team, so it has no topology (related-work §2.13). Two methods do restrict or vary interaction, though neither controls a shape: TTA passes along a fixed index ring (related-work §2.9), and FTTA re-clusters its groups by GMM every iteration (related-work §2.11) | Cellular (structured) population with dynamic grid-shape topology (Alba & Dorronsoro 2005; Kennedy & Mendes 2002) |
| Positional rotation ("total football") | At fixture boundaries, a better agent in a deeper line swaps slots, and therefore archetype, with a worse upfield neighbour | Rank-based role reassignment restricted to graph neighbours: fitness-triggered pairwise position swaps between adjacent nodes of a dynamic hierarchy (Janson & Middendorf 2005) |
| The ball and possession | A single focal point is passed between formation neighbours by short drift steps; a pass is *retained* only if fitness does not regress by more than τ. The closest prior art is the Tiki-taka Algorithm (full text, `related-work.md` §2.9). TTA keeps one ball *per player* (B is n × d), passes along a fixed directed index ring (b_i ← b_{i+1}), never evaluates the balls, and loses a pass at random with p = 0.1–0.3. TFO has one ball, passes on the controlled 2-D lattice, and retains a pass by a τ threshold on fitness. TFO's ball is also decoupled from the incumbent, unlike SGO and FOA (2012), where the ball *is* the best solution. The Soccer Match Algorithm's possession is also kept or lost on fitness outcome, but it is a token that decides which decision variable moves next, not a point in the search space (related-work §2.13) | Threshold accepting (Dueck & Scheuer 1990); τ = 0 gives non-regression with neutral drift |
| Pressing (high press ↔ low block) | Agents within radius ρ of the ball drop their role move and close the ball down with a shrinking-encircling step; ρ is the pressing intensity | Distance-gated shrinking-encircling attraction (cf. GWO/WOA encircling; Mirjalili et al. 2014) |
| Counter-attack (transition) | Turnover event: when an off-ball agent finds a materially better point far from the ball, the ball relocates there and the attacking line makes a short large-step burst whose step decays geometrically. *Prior art (full text):* the Soccer Match Algorithm also turns possession over when a move fails, but it relocates nothing and no burst follows (related-work §2.13). The distinct element is the relocation plus the burst | Event-triggered basin hopping / iterated-local-search relocation (Wales & Doye 1997; Lourenço et al. 2003) |
| Set pieces (corners, free kicks) | Every *c* iterations the incumbent runs a rehearsed routine from a fixed script and never adapts it. Corner: an orthogonal-array probe on a random coordinate pair. Free kick: a three-point parabolic line search along a random direction | Fixed-frequency memetic local search: orthogonal-design sampling, successive parabolic interpolation (Leung & Wang 2001; Brent 1973) |
| Offside line | Out-of-box coordinates are pulled back onside, between the old position and the bound. On constrained problems a moving ε-line decides "onside" (violation ≤ ε(t)) and steps up to ε = 0 late in the run | Bound repair (Helwig et al. 2013) + ε-constrained feasibility ranking (Takahama & Sakai 2006; Deb 2000) |
| Substitutions | An agent whose personal best has stalled for *W* iterations and whose stamina is low is replaced by a fresh uniformly random agent, at most five per fixture; the outgoing position is marked tabu. *Prior art (full text):* the closest is IFTTA's per-agent stagnation-counter restart, which has no stamina gate, no cap and no tabu (related-work §2.11). SLOCA's reserve players are still unverified (related-work §2.4) | Stagnation-triggered random immigrants, capped (Grefenstette 1992) |
| Fatigue and fixture congestion | Each agent's step scale drains with the distance it covers and recovers at fixture breaks, and recovery shrinks as the season goes on; substitutes arrive with full stamina | Workload-clocked per-agent step-size annealing (cf. Kirkpatrick et al. 1983) |
| VAR review | Every *v* iterations, moves accepted since the last review are audited against global checks (tabu zones, duplicate positions, true feasibility) and overturned by rollback, unless they produced a new global best ("clear and obvious" rule) | Deferred tabu audit with aspiration criterion: short-term memory plus rollback (Glover 1989) |
| The manager's tactical board | Reads diversity, possession rate, goal drought (a material-improvement stagnation counter) and match clock, then switches among Build-up, Control, High Press and Chasing the Game. Each state sets the formation, ρ, τ, pass-chain length and role rates. *Prior art (full text):* the Soccer Match Algorithm adapts each move type's selection probability from its recent mean improvement, which is adaptive operator selection with no discrete states. MTTA scales one step-size factor by ×0.95 after an improvement and ×1.05 after stagnation. Neither switches topology (related-work §2.13, related-work §2.10) | Feedback-driven adaptive parameter control, state machine (Eiben et al. 1999) |

*Archetype inspiration (homage to styles of play, not to individuals).* The Sweeper-Keeper follows
modern ball-playing goalkeepers who start attacks from the back. The Zonal Centre-Back follows
commanding defenders who organise a zonal line. The Overlapping Wing-Back follows attacking
full-backs who overlap and switch play to the far flank. The Destroyer follows ball-winning
defensive midfielders who break up play in congested areas. The Deep-Lying Playmaker follows
deep-lying playmakers who dictate tempo with long diagonal passes. The Box-to-Box Engine follows tireless
midfielders who cover both penalty areas. The Virtuoso follows low-centre-of-gravity dribblers who
beat opponents with many tiny touches. The Finisher follows powerful centre-forwards whose quiet
spells end in sudden, spectacular strikes.

## Overlap audit against the Chess Algorithm (CA)

| TFO mechanism | Shares an operator family with CA? | Stated difference |
|---|---|---|
| Sweeper-Keeper | Yes (King + overprotection archive) | Archive also seeds Finisher restarts and ball resets |
| Overlapping Wing-Back | Yes (opposition-based initialisation) | Used as in-run generation jumping about the centroid, not at initialisation |
| Box-to-Box Engine | Yes (knight's fork, differential mutation) | Neighbourhood-restricted donor selection on the formation graph |
| Positional rotation | Yes (promotion, rank-based reassignment) | Local pairwise swaps with graph neighbours at fixture boundaries, not global re-ranking every iteration |
| Pressing | Partly (elite-guided perturbation in CA's role moves) | Membership gated by distance to the ball, radius under adaptive control |
| Substitutions | Yes (threefold repetition, re-initialisation) | Triggered by individual stagnation plus fatigue, capped per fixture, feeds the VAR tabu register |
| Fatigue | Yes (development schedule, decaying step) | Per-agent, workload-clocked rather than global and iteration-clocked |
| Manager's tactical board | Yes (phase state machine) | Also switches interaction topology (formation), not only operator rates |
| Zonal Centre-Back, Destroyer, Deep-Lying Playmaker, Virtuoso, Finisher, Formation, Possession, Counter-attack, Set pieces, Offside line, VAR | No | 11 mechanisms in families absent from CA's operator-family table |
