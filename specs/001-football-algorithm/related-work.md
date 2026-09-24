# Related Work: Football- and Sports-Inspired Metaheuristics vs. the Total Football Optimizer (TFO)

**Status.** This is the authoritative prior-art review for TFO. It replaces the "prior art to verify" note that
was in `spec.md`. It was built in two passes on 2026-09-24.

- **Pass 1 (search).** Sources were the Consensus academic search index (Semantic Scholar, Scopus, PubMed and
  arXiv), Crossref bibliographic verification through the FastTrack `verify_reference` tool, and general web
  search. Every publisher host was blocked by the network egress proxy, so this pass saw only abstracts,
  secondary descriptions and snippets.
- **Pass 2 (full text).** The project owner supplied PDFs of eight primary sources. They sit in the repository
  root: SMA (`Soccer_Match_Algorithm_for_Global_Optimization_A_Contender_Metaheuristic.pdf`), TTA
  (`10.1108@EC-03-2020-0137.pdf`), FbOA (`11729543348.pdf`), FTTA
  (`Football-team-training-algorithm-A-novel-sport-inspired-meta-heuristic-optimization-algorithm.pdf`), MTTA
  (`mathematics-14-01900-v2.pdf`), FGA (`fadakar2016.pdf`), IFTTA (`biomimetics-09-00419-v2.pdf`) and the
  Alatas survey (`alatas2017.pdf`). Each was read in full, including equations, pseudocode, parameter tables
  and experimental sections.

§2.8–§2.14 now rest on the full text. Their citations give the section, equation and **printed page number**:
IEEE Access and Emerald page numbers for SMA and TTA, "p. N" of the article for MDPI and JAIM, and sections only
for the online-first Alatas PDF, which has no page numbers. Mechanisms that are still described from an
abstract, a secondary description or a snippet are labelled as such. SLOCA is still snippet-only.
Citation counts are a snapshot taken on 2026-09-24. **Crossref** means Crossref's `is-referenced-by` count and
**Consensus** means the count shown by the Consensus index. The two differ, and both are reported where both
were seen.

**Mechanism labels used below.** They refer to `mechanism-map.md`. Archetypes: SK Sweeper-Keeper, ZCB Zonal
Centre-Back, OWB Overlapping Wing-Back, DES Destroyer, REG Regista, B2B Box-to-Box Engine, VIR Virtuoso, FIN
Finisher. Team-level tactics: FORM formation-as-topology, ROT positional rotation, BALL ball and possession,
PRESS pressing, CTR counter-attack, SET set pieces, OFF offside line, SUB substitutions, FAT fatigue, VAR VAR
review, MGR the manager's state machine.

---

## 1. Introduction: why football needs careful positioning

Sports metaphors have been used in metaheuristic design since at least the League Championship Algorithm
(Kashan, 2009). Two surveys already catalogue the family.

- **Alatas.** *Artificial Intelligence Review*, online 2017, print 2019, 52(3):1579–1627. The full text was read.
  §3.1–§3.9 review **nine** sports-inspired algorithms: LCA, Soccer League Optimization, Soccer Game
  Optimization, the Soccer League Competition Algorithm, Golden Ball, World Cup Optimization, the **Football
  Optimization Algorithm (FOA; Hatamzadeh & Khayyambashi, 2012)**, the Football Game Algorithm and the Most
  Valuable Player Algorithm. §5 benchmarks all of them except SLO and Golden Ball.
  - *Correction.* Pass 1 omitted FOA from this list and from the roster. It is now §2.14.
  - *Alatas's own warning.* §6 already notes that "some algorithms are just similar version of existing
    approaches, with a different name and different metaphor", and it singles out FOA as resembling FGA. That
    is the criticism TFO's constitution pre-empts.
- **Osaba & Yang** (2021, Springer book chapter) cover the soccer-specific subset.

Since 2020 the pace has increased. The two passes identified **thirteen distinct football/soccer-specific
optimizers (2012–2026)**. On top of these come the generic sports-league LCA (2009), the match-adjacent
Stadium Spectators Optimizer (2024), and at least eight published variants. That makes football the most
crowded single-sport metaphor in the field. Between them, these methods have already used almost every
obvious football idea:

- league and tournament competition among sub-populations (LCA, SLC, SLO, SLOCA, Golden Ball, WCO);
- a ball or ball-carrier as an attractor (SGO, FOA, FGA, TTA), and possession as a fitness-contingent
  scheduling token (SMA);
- short and long passes (TTA, FbOA and MTTA; SMA's "pass" is a coordinate-level move);
- role heterogeneity and fitness-based role assignment (FTTA, MTTA, SMA);
- substitutes and reserve players (SGO, SLC, SLOCA, FOA, FGA, SMA), and stagnation-triggered restarts
  (IFTTA);
- player fatigue (SLOCA);
- coach supervision and in-game tactical shifts (FGA, Golden Ball, SMA), and feedback-driven parameter
  adaptation (SMA, MTTA);
- even the names: MTTA already calls its adaptive step-size midfielder a *regista* (MTTA §3.1), and TTA's
  introduction names *total football* as a playing style that no algorithm had yet modelled (TTA §1, p. 316).

A new football-inspired method therefore cannot claim novelty from its metaphor or from any single football
concept. TFO's constitution (Principle: mechanism before metaphor) already forbids that. Distinctiveness has
to be shown **mechanism by mechanism, at the level of the operator family**. The rest of this document does
that.

---

## 2. Football/soccer-inspired algorithms: mechanism-level comparison

Each entry gives the reference, the core metaphor, the computational mechanism (with its evidence level), and
an explicit overlap breakdown against TFO's 19 mechanisms.

### 2.1 League Championship Algorithm (LCA) and Premier League Championship Algorithm (PLCA)

- **References.** Kashan, A.H. (2009). League Championship Algorithm: A new algorithm for numerical function
  optimization. *SoCPaR 2009*, 43–48. doi:10.1109/SoCPaR.2009.21. · Kashan, A.H. (2014). League Championship
  Algorithm (LCA): An algorithm for global optimization inspired by sport championships. *Applied Soft
  Computing* 16, 171–200. doi:10.1016/j.asoc.2013.12.005 (Crossref 277; Consensus 281). · Variant: Kashan,
  Jalili & Karimiyan (2019). Premier League Championship Algorithm. *Studies in Computational Intelligence*,
  215–240. doi:10.1007/978-981-13-6569-0_11.
- **Metaphor.** A generic sports league, not football specifically. Each individual is a team, and teams play
  weekly fixtures over seasons.
- **Mechanism** (abstract; secondary description in Alatas §3.1, Eqs. 2–4). A single round-robin schedule
  pairs individuals. The match result is decided stochastically, and a fitter individual is more likely to
  win. A new solution is built by an "artificial match analysis", a SWOT-style update that combines
  differences from the winner/loser relations of the current and next-week pairings. Selection is greedy. An
  optional end-of-season "transfer" module exchanges parts of solutions. PLCA runs several local leagues as a
  multi-population.
- **Overlap with TFO.** Weak. The time-varying pairing schedule is a restricted interaction pattern, but it is
  a round-robin over the whole population, not a spatial lattice (FORM). Both algorithms use a fixture/season
  clock, but in TFO the fixture boundary is only a timing device (ROT, ZCB, FAT recovery).
- **Terminology collision (must be addressed in the manuscript).** In LCA, "team formation" means *the
  solution vector itself*. Alatas §3.1, Table 1 maps "Formation" to "Solution" explicitly. In TFO,
  "formation" means *the interaction topology*. The paper should state this so that a reviewer does not read
  TFO's formation as LCA's.
- **No counterpart in LCA.** All 8 archetypes, BALL, PRESS, CTR, SET, OFF, VAR, FAT, SUB, and the adaptive MGR.
- **Verdict:** distinct.

### 2.2 Soccer League Competition (SLC)

- **References.** Moosavian, N., & Kasaee Roodsari, B. (2014). Soccer league competition algorithm: A novel
  meta-heuristic algorithm for optimal design of water distribution networks. *Swarm and Evolutionary
  Computation* 17, 14–24. doi:10.1016/j.swevo.2014.02.002 (Crossref 220; Consensus 220). · Also *International
  Journal of Intelligence Science* 4(1), 7–16 (2014). doi:10.4236/ijis.2014.41002.
- **Metaphor.** A professional soccer league, with competition between teams and within each team.
- **Mechanism** (abstract; secondary description in Alatas §3.4.1, Eqs. 10–16). The population is partitioned
  into teams of *fixed players* and *substitutes*. Team power is the mean power of the fixed players. Teams
  play, and four operators follow.
  - *Imitation* moves the winners' fixed players toward the team's Star Player and the league's Super Star
    Player.
  - *Provocation* moves the winners' substitutes relative to the centroid of the fixed players.
  - *Mutation* is applied to some of the losers' fixed players.
  - *Substitution* recombines pairs of the losers' substitutes.

  Players are then re-sorted, with the best players going to the best teams.
- **Overlap with TFO.**
  - SUB: shared vocabulary only. SLC's substitutes are a reserve sub-population that competes for fixed
    slots. TFO's substitutions are stagnation-triggered random immigrants, capped per fixture and marked tabu.
    The operator families differ.
  - ROT: partial. SLC reallocates players to teams by rank, which is a global rank-based reassignment. TFO's
    rotation is a *local pairwise swap between graph neighbours* at fixture boundaries.
- **No counterpart in SLC.** FORM, BALL, PRESS, CTR, SET, OFF, VAR, FAT, MGR, and all archetype operators.
- **Verdict:** distinct, with a terminological overlap on SUB.

### 2.3 Soccer League Optimization (SLO)

- **Reference.** Khaji, E. (2014). Soccer League Optimization: A heuristic algorithm inspired by the football
  system in European countries. arXiv:1406.4462 (Consensus 5). Preprint only. No journal version was found.
- **Metaphor.** The transfer economy of European leagues, with rich, regular and poor clubs.
- **Mechanism** (abstract; Alatas §3.2). The population is split into three strata of teams. Strong teams buy
  the best players of regular teams, regular teams buy from the weakest, and the weakest "discover young
  players" (fresh random solutions). This amounts to hierarchical migration with random immigrants at the
  bottom tier. Alatas (§3.2.1, §5) notes that no formal mathematical formulation was published, and excludes
  SLO from his benchmark for that reason.
- **Overlap with TFO.** SUB is partial: both inject random immigrants. SLO injects them into the weakest tier
  continuously. TFO triggers them per agent on stagnation and low stamina, caps them per fixture and marks
  them tabu.
- **No counterpart in SLO.** Everything else.
- **Verdict:** distinct. SLO is low-impact and should be cited briefly for completeness.

### 2.4 Soccer League Optimization-based Championship Algorithm (SLOCA)

- **Reference.** Ghasemi, M.R., Ghasri, M., & Salarnia, A. (2022). Soccer league optimization-based
  championship algorithm (SLOCA): A fast novel meta-heuristic technique for optimization problems. *Advances
  in Computational Design* 7(4), 297–… (Techno-Press). **No DOI is registered with Crossref.** The candidate
  `10.12989/acd.2022.7.4.297` returned "not registered". The venue, volume and start page come from web
  snippets of the ResearchGate and MathWorks pages. **No PDF was available for pass 2.**
- **Metaphor.** A soccer championship with qualifying and main competitions.
- **Mechanism** (snippet only). The algorithm runs in two stages, qualifying competitions and main
  competitions. It "applies a fatigue factor to players and randomly uses reserve players to avoid premature
  convergence."
- **Overlap with TFO. Needs scrutiny.** At the metaphor level SLOCA already has **both fatigue (FAT) and
  reserve players (SUB)**. The mechanism behind them is unverified.
  - TFO's FAT is a *per-agent, workload-clocked* step-scale drain, proportional to distance covered. Stamina
    recovers at fixture breaks, and recovery weakens over the season.
  - TFO's SUB is gated by stagnation plus low stamina, capped at five per fixture, and feeds the VAR tabu
    register.
  - If SLOCA's fatigue is a global, iteration-clocked decay, TFO differs in the same way `mechanism-map.md`
    already records against CA. That has to be confirmed from the full text.
- **No counterpart in SLOCA** (as far as can be seen). FORM, BALL, PRESS, CTR, SET, OFF, VAR, MGR, and the
  archetypes.
- **Verdict:** partial overlap (FAT, SUB). Needs scrutiny: read the full text before submission.

### 2.5 Golden Ball (GB)

- **References.** Osaba, E., Diaz, F., & Onieva, E. (2014). Golden ball: a novel meta-heuristic to solve
  combinatorial optimization problems based on soccer concepts. *Applied Intelligence* 41(1), 145–166.
  doi:10.1007/s10489-013-0512-y (Crossref 88; Consensus 95). · Osaba et al. (2013), *GECCO '13 Companion*,
  1743–1744. doi:10.1145/2464576.2480776. · Osaba et al. (2014), *The Scientific World Journal*, article
  563259. doi:10.1155/2014/563259.
- **Note.** GB is **football-inspired**, not a non-football sports method. It belongs in this section.
- **Metaphor.** A soccer league season with teams, captains, training sessions, matches and transfers.
- **Mechanism** (abstracts; secondary description in Alatas §3.5.1). GB is a multi-population method for
  **combinatorial** problems (TSP, CVRP, VRPB, bin packing).
  - A team is a set of solutions, and its best member is the captain.
  - *Conventional training* applies neighbourhood moves, and a move is accepted only if it improves.
    *Custom training* works with the captain to escape local optima.
  - League matches between teams, twice per season, set team scores. Those scores drive player transfers at
    the end of the season: the best team gets the best player of the worst team, and so on.
  - A *special exchange* moves a player that has not improved after repeated trainings to a random other
    team, which is a stagnation-triggered migration.
  - Alatas also reports a "cessation of coaches" rule: a coach is replaced when their team keeps getting bad
    results. He does not say what the replacement changes algorithmically.
- **Overlap with TFO.** Weak. There is a season/fixture clock, and the coach-replacement rule is a weak,
  unspecified analogue of MGR (secondary evidence only). The special exchange is stagnation-triggered, like
  SUB, but it migrates the stagnant player instead of replacing it with a fresh random agent.
- **No counterpart in GB.** GB is a discrete, permutation-based method, so none of TFO's continuous operators
  (OWB, B2B, VIR, FIN, SET, OFF) has a counterpart. Nor do FORM, BALL, PRESS, CTR, VAR or FAT.
- **Verdict:** distinct. It also belongs to a different problem class.

### 2.6 World Cup Optimization (WCO)

- **Reference.** Razmjooy, N., Khalilpour, M., & Ramezani, M. (2016). A new meta-heuristic optimization
  algorithm inspired by FIFA World Cup competitions: Theory and its application in PID designing for AVR
  system. *Journal of Control, Automation and Electrical Systems* 27(4), 419–440.
  doi:10.1007/s40313-016-0242-6 (Crossref 245; Consensus 258).
- **Metaphor.** The FIFA World Cup: continents, qualification, the tournament stages and a play-off.
- **Mechanism** (abstract; secondary description in Alatas §3.6.1, Eqs. 21–27). Solutions are grouped into
  "continents", which are scored by a mean-plus-spread rank. The best advance to the next stage, and a
  *play-off* parameter gives third-placed teams a second chance. The new population mixes the best solutions
  with fresh random ones. In effect this is hierarchical tournament selection with a controlled leak of
  non-winners.
- **Overlap with TFO.** None at the operator level. TFO has no tournament or elimination scheme.
- **Verdict:** distinct.

### 2.7 Soccer Game Optimization (SGO) and variants

- **References.** Purnomo, H.D., & Wee, H.-M. (2013). Soccer Game Optimization. In *Meta-Heuristics
  Optimization Algorithms in Engineering, Business, Economics, and Finance* (IGI Global), 386–420.
  doi:10.4018/978-1-4666-2086-5.ch013. · Purnomo & Wee (2015). Soccer game optimization with substitute
  players. *Journal of Computational and Applied Mathematics* 283, 79–90. doi:10.1016/j.cam.2015.01.008. ·
  Variant: Purnomo et al. (2020), "The use of local information sharing on soccer game optimization"
  (SGOLS), *Soft Computing*. The DOI was taken from the result URL and is not Crossref-verified.
- **Metaphor.** Soccer players moving across the pitch toward a ball dribbler.
- **Mechanism** (abstracts; secondary descriptions in Alatas §3.3.1, Eqs. 5–9, and in SMA §II.C, p. 93925).
  - The **ball dribbler is the best solution found so far**. Alatas's Eq. 6 updates it only when a player
    improves on it, and SMA describes it as "the best current solution".
  - *Move forward* is a centre-of-mass combination of the player's position, its personal best and the
    dribbler.
  - *Move off* is a random move.
  - *Substitute players* form a pool that stores a set of best-so-far positions and is swapped in with a set
    probability.
  - In SGOLS, move forward also uses information from **nearby players**.
- **Overlap with TFO.**
  - BALL: partial. SGO has a ball-carrier attractor, but **SGO's ball is the incumbent**. TFO's central
    design claim is a ball that is *separate from the incumbent* and is carried by passes. SGO is therefore
    the clearest foil for that claim, not a counter-example to it.
  - SK: partial. SGO's substitute pool of best-so-far solutions is an elite archive, which is closer to
    TFO's Sweeper-Keeper archive than to TFO's substitutions.
  - B2B/FORM: partial. SGOLS's "nearby players" is a local neighbourhood. No SGOLS full text was available,
    so whether "nearby" is index-based or Euclidean is still unverified.
- **No counterpart in SGO.** FORM as a controllable topology, ROT, PRESS, CTR, SET, OFF, VAR, FAT, MGR, and
  ZCB/OWB/DES/REG/VIR/FIN.
- **Verdict:** partial overlap (BALL at the metaphor level, SK), distinct on structure.

### 2.8 Football Game Algorithm / Football Game Inspired Algorithm (FGA / FGO) — full text read

- **References.** Fadakar, E., & Ebrahimi, M. (2016). A new metaheuristic football game inspired algorithm.
  *2016 1st Conference on Swarm Intelligence and Evolutionary Computation (CSIEC)*, 6–11.
  doi:10.1109/CSIEC.2016.7482120 (Crossref 81; Consensus 71). · Variant: Subramaniyan, S., & Ramiah, J.
  (2020). Improved football game optimization for state estimation and power quality enhancement.
  *Computers & Electrical Engineering* 81, 106547. doi:10.1016/j.compeleceng.2019.106547. The variant was not
  read.
- **Metaphor.** A single team, always attacking, whose players look for scoring positions under a coach's
  supervision.
- **Mechanism** (full text).
  - *General movement* (§III.A, Eqs. 1–2, p. 8).
    - Update: X_i^t = X_i^{t−1} + α_i ε + β (X_ball^t − X_i^{t−1}), with ε ~ U[−1, 1], β ~ U[0, 1] and a
      decaying step α_i = α_0 θ^t.
    - X_ball^t is "the position of the player who has the ball at time step t". "The ball will be passed
      randomly between the players and the players in the better positions have more chance to receive the
      ball" (p. 8). The selection distribution is not specified.
  - *Coaching* (§III.B, Eqs. 3–4, pp. 8–9).
    - A coach memory CM stores the best positions found. Its size is CMS = n/2 (Table I, p. 10).
    - Two strategies act on it. The *attacking* ("Hyper Radius Penalty") strategy relocates every member whose
      distance from the best exceeds HRLV^t. The *substitution* ("Fitness Penalty") strategy replaces every
      member whose fitness is worse than FLV^t.
    - Both thresholds decay geometrically: HRLV^t = HRLV_min + (HRLV^{t−1} − HRLV_min)·γ (Eq. 3), with γ =
      0.95. FLV decays in the same way with λ = 0.85 (Eq. 4).
    - Relocated players are placed at X_new = X_nearest-best + α_i ε. The equation is printed as a second
      "(4)" and the pseudocode (Fig. 5, p. 9) calls it Eq. (5).
    - The authors state that "exploitation is coach's duty in the algorithm" (§V, p. 11).
- **Resolved questions.**
  - *Is the ball-holder the current best?* **No, and it is not a separately tracked focal point either.** The
    ball-holder is a current population member drawn stochastically with a fitness bias at each iteration.
    The ball has no state of its own, and there is no pass-acceptance rule.
  - *What does the coach do?* **It is not a feedback-driven state machine.** It is an elite archive combined
    with two open-loop, geometrically decaying thresholds, on distance and on fitness. Every agent that breaks
    a threshold is relocated near its nearest archived elite. In operator-family terms this is archive-based
    elitist relocation (restart) with annealed thresholds.
- **Overlap with TFO.**
  - BALL: metaphor-level only. The attractor is a fitness-biased random current member.
  - MGR: **none at the operator-family level.** FGA's thresholds follow a fixed schedule and read no search
    state. Pass 1's "partial (MGR)" verdict is withdrawn.
  - SK / FIN / SUB: partial (new in pass 2). The coach memory is an elite archive (SK), and relocation around
    the nearest archived elite resembles FIN's elite restart and SUB's replacement. The differences:
    - TFO's archive is small and distance-diverse.
    - FIN restarts after an individual agent's repeated misses and then uses Lévy jumps.
    - SUB is triggered by an agent's own stagnation plus low stamina, is capped per fixture, and marks the
      outgoing position tabu.
    - FGA applies global threshold schedules to every member at every iteration.
  - PRESS: weak. FGA's hyper-radius penalty is the only distance-gated rule found in the family. It points
    the opposite way from TFO's pressing: agents *outside* a radius around the best are sent to an archived
    elite, whereas TFO's pressing makes agents *inside* ρ of the ball close it down.
- **No counterpart in FGA.** FORM (attraction to the ball-holder is global), ROT, CTR, SET, OFF, VAR, FAT, and
  the ZCB, OWB, DES, REG, B2B and VIR archetype families.
- **Verdict:** partial overlap (SK, FIN and SUB through the coach memory; BALL at the metaphor level only).
  **Distinct on MGR**, which reverses pass 1.

### 2.9 Tiki-taka Algorithm (TTA) — full text read

- **Reference.** Ab. Rashid, M.F.F. (2021). Tiki-taka algorithm: a novel metaheuristic inspired by football
  playing style. *Engineering Computations* 38(1), 313–343. doi:10.1108/EC-03-2020-0137. The paper was received
  6 March 2020 and accepted 27 May 2020. It was published online in 2020 and in print in 2021 (Crossref 47;
  Consensus 39). · Multi-objective variant: Ab. Rashid & Ramli (2023), *Engineering Computations* 40(3),
  564–593. doi:10.1108/EC-03-2022-0185. The variant was not read.
- **Metaphor.** The tiki-taka style of play: short passing, positioning and possession. Its introduction
  (§1, p. 316) notes that earlier football algorithms model no specific tactic, and names "samba" and "total
  football by the Dutch team" as examples. TFO's name answers that remark directly, and the manuscript can
  say so.
- **Mechanism** (full text).
  - *State* (§2.2.1, Eqs. 1–2, p. 318).
    - Players P and balls B are both n × d matrices, with "B = P" at initialisation. **There is one ball per
      player.**
    - The key-player archive h holds the top n_k players by fitness. n_k is "approximately 10% of the total
      players or a minimum of three". The archive is updated every iteration and "only contains the current
      values".
  - *Ball update* (§2.2.2, Eq. 3, p. 318). The printed rule is:

    b_i′ = rand·(b_i − b_{i+1}) + b_i  if r_p > prob_lose;
    b_i′ = b_i − (c1 + rand)·(b_i − b_{i+1})  otherwise.

    - "For the last ball position, b_n, the term b_{i+1} is replaced with b_1". **The pass partner is
      therefore the next index on a fixed, directed ring**, even though the prose says "the nearest player".
    - prob_lose lies in [0.1, 0.3] (p. 318; pseudocode p. 319).
    - The Taguchi-tuned defaults are prob_lose = 0.2, c1 = 1.2, c2 = 2.5 and c3 = 1.0 (§3.1, Table 4, p. 323).
    - As printed, the success branch moves b_i *away from* b_{i+1} and the loss branch moves it toward and past
      b_{i+1}. That is the reverse of the prose, which says a successful pass goes "to the nearest player" and
      a lost ball is "delivered behind the player". MTTA reprints the same form (MTTA Eq. 3, p. 8).
  - *Player update* (§2.2.3, Eq. 4, pp. 318–319).
    - Rule: p_i′ = p_i + rand·c2·(b_i′ − p_i) + rand·c3·(h − p_i).
    - h is one key player chosen at random from the archive. The paper says the selection "is random because
      the number of key players is more than one".
    - The pseudocode (p. 319) replaces P by P′ unconditionally, with no greedy selection. **The balls are never
      evaluated**, and after initialisation B is never re-synchronised with P.
  - *Stated uniqueness and limitation* (§5, pp. 338–339). "The TTA exploits the nearby solution in addition to
    a set of leading solutions". The unsuccessful-pass reflection "makes the exploration activity to
    concentrate on a particular region".
- **Resolved questions.**
  1. *One ball per player or a single ball?* **One per player** (B is n × d).
  2. *Is "nearby" index-adjacent or Euclidean?* **Index-adjacent on a directed ring** (i → i+1, with n → 1).
  3. *What is the loss probability?* **10–30 %**, with a tuned default of **0.2**.
  4. *How are key players chosen?* The **top ~10 % (at least 3) of the current population by fitness**, and
     one of them is drawn uniformly at random for each player update.
- **Overlap with TFO. TTA is still the closest prior art to BALL, and full-text reading adds one real point of
  contact with FORM.** The defensible differences are all at the mechanism level:
  1. **Acceptance rule (confirmed).** TTA never evaluates its balls, and loss is a fitness-independent event
     with probability 0.1–0.3. TFO keeps a pass only if fitness does not regress by more than τ (threshold
     accepting, Dueck & Scheuer 1990). τ is under the manager's control, and τ = 0 gives non-regression with
     neutral drift.
  2. **Pass geometry (closer than assumed).** TTA's passes *do* run along a graph: a fixed, directed,
     one-dimensional ring over population indices. TFO therefore cannot claim to be the first football method
     with graph-restricted passing. What it can claim:
     - Its graph is a two-dimensional lines × lanes lattice with von Neumann neighbourhoods, and the lattice's
       shape is a control variable with a takeover-time prediction (H3).
     - The lattice restricts *all* agent interaction. TTA's ring constrains only the ball update, while the
       player update also pulls every agent toward a random global elite.
  3. **Number of balls (confirmed).** TTA has n balls, one per player. TFO has one focal point for the whole
     squad.
  4. **Turnover semantics (confirmed).** In TTA the loss is random. In TFO a change of possession is an event
     triggered by where improvement occurs, followed by a counter-attack burst (CTR).
- **Other overlaps.** TTA's key-player archive (the current top 10 %, sampled uniformly) is an elite-guidance
  set that could be compared with SK. TFO's Sweeper-Keeper archive differs: it is best-so-far and
  distance-diverse, and it seeds restarts and ball resets rather than guiding every move.
- **No counterpart in TTA.** ROT, PRESS, CTR as an event, SET, OFF (TTA uses a death penalty, §4), VAR, FAT,
  SUB, MGR, and the archetype operators.
- **Verdict:** closest prior art on BALL; partial overlap on FORM (a fixed index ring); distinct elsewhere. The
  manuscript **must** cite TTA in both the possession row and the formation row and give the four differences
  above.

### 2.10 Modernized Tiki-taka Algorithm (MTTA) — full text read

- **Reference.** Song, X., & Zhao, J. (2026). MTTA: Modernized Tiki-Taka Algorithm with role specialization
  for solving engineering application problems and feature selection. *Mathematics* 14(11), 1900. Published
  29 May 2026. doi:10.3390/math14111900 (Crossref 0). The authors, **Xiangkun Song and Jian Zhao**, are
  confirmed on p. 1.
- **Metaphor.** Tiki-taka with modern positional roles.
- **Mechanism** (full text).
  - *Role division* (§3, p. 9; Algorithm 1, line 10, p. 16). The population is divided "according to
    individual fitness ranking **at each iteration**". Forwards are the top 10 %, defenders the bottom 20 %,
    and midfielders the remaining 70 %.
  - *Ball update.* TTA's Eq. 3, unchanged (p. 8).
  - *Midfielders* (§3.1, Eqs. 5–6, pp. 10–11).
    - Step factor: CF ← max(0.95·CF, 0.1) if the global best improved from t−1 to t, and CF ← min(1.05·CF, 2.0)
      otherwise.
    - Rule: p′ = p + CF·rand·(b′ − p) + CF·rand·(h − p).
    - The paper calls this mechanism the **regista**. Its "long cross-field pass" is the large step that CF
      produces after stagnation (§3.1, Fig. 1, p. 11).
  - *Forwards* (§3.2.1, Eq. 7, p. 12). TTA's player update with a sine modulation of the elite term,
    × (1 + α sin(2π t/T_max)), where α = 0.1.
  - *Defenders* (§3.2.2, Eq. 8, pp. 13–14). Rule: p′ = b ⊙ p̄_d + d ⊙ (h − p), where b and d are uniform random
    vectors and p̄_d is the mean position of all defenders.
  - *Initialisation* (§3.3). Logistic–Tent chaotic initialisation.
  - *Evaluation.* Sensitivity analysis (§4.4, Table 13, p. 26) and a single-factor ablation (§4.5,
    pp. 27–29).
- **Resolved questions.**
  - *Are the three role rules different operator families?* **No.** Forwards and midfielders both use TTA's
    ball-plus-elite attraction. They differ only in a deterministic sine schedule versus a success-based step
    factor. The defender rule is a randomly weighted defender-centroid term plus elite attraction, which is
    still attraction toward population statistics. So the three roles are variants of one attraction family.
    TFO's eight archetypes map to eight *named, different* families.
  - *When are roles reassigned?* **Every iteration**, by global re-ranking.
- **Overlap with TFO.**
  - Archetypes: weak. MTTA's role-specific rules exist, but they are not role-specific operator families.
  - ROT: partial, as pass 1 recorded, now confirmed. MTTA re-ranks globally every iteration. TFO makes local
    pairwise swaps between formation neighbours at fixture boundaries, so the archetype follows the lattice
    slot.
  - MGR: partial (new). MTTA's CF is feedback-driven step-size control on a single scalar. It is
    success-based, in the spirit of Rechenberg's 1/5 rule. TFO's manager is a multi-signal state machine that
    also switches the topology.
  - REG: **naming collision (new).** MTTA already uses "regista" and "long cross-field pass" for large-step
    exploration. TFO's Regista is a recombination with a partner at maximum *graph* distance (BLX-α), which is
    a different operator. The manuscript must either cite MTTA's use of the term or rename the archetype.
  - PRESS: metaphor only. MTTA's defender prose invokes "high-pressing" (p. 13), but the mechanism is
    centroid-plus-elite attraction, not distance-gated membership.
  - BALL: inherited from TTA (n balls, index ring, random loss; §2.9).
- **No counterpart in MTTA.** FORM, PRESS as a mechanism, CTR, SET, OFF, VAR, FAT, SUB.
- **Verdict:** partial overlap (ROT; MGR as scalar step-size control; the REG name; weak on archetypes);
  distinct on structure.

### 2.11 Football Team Training Algorithm (FTTA) and variants — full text read (FTTA, IFTTA)

- **References.** Tian, Z., & Gai, M. (2024). Football team training algorithm: A novel sport-inspired
  meta-heuristic optimization algorithm for global optimization. *Expert Systems with Applications* 245,
  123088. doi:10.1016/j.eswa.2023.123088 (Crossref 161; Consensus 145). The authors, **Zhirui Tian and Mei
  Gai**, are confirmed on p. 1. Consensus's "Zhi-Gang Tian" is wrong.
  - Variants: Hou, J., Cui, Y., Rong, M., & Jin, B. (2024), IFTTA, *Biomimetics* 9(7), 419, published 8 July
    2024, doi:10.3390/biomimetics9070419 (full text read). · Sun et al. (2025), MIFTTA, *Concurrency and
    Computation: Practice and Experience* 37(23–24), e70282, doi:10.1002/cpe.70282 (not read). · Peng et al.
    (2024), chaotic-map FTTA, RICAI 2024 (seen in Consensus, not Crossref-verified, not read).
- **Metaphor.** A training session rather than a match: collective training, then group training, then
  individual extra training.
- **Mechanism** (FTTA full text).
  - *Collective training* (§2.1.1, Eqs. 1–4, pp. 5–6). Players "randomly change their own types" at every
    iteration among four behaviours:
    - Followers: F + rand·(F_best − F) (Eq. 1).
    - Discoverers: F + rand·(F_best − F) − rand·(F_worst − F) (Eq. 2).
    - Thinkers: F + rand·(F_best − F_worst) (Eq. 3).
    - Volatilities: F·(1 + t(k)), a t-distributed draw whose degrees of freedom equal the iteration count
      (Eq. 4).
  - *Group training* (§2.1.2, Eqs. 5–10, pp. 6–8).
    - The coaches cluster all players into four groups with **MGEM, a mixture-of-Gaussians EM clusterer in
      decision space**. The groups are labelled Strikers, Midfielders, Defenders and Goalkeepers.
    - If any group falls below a minimum size ("Team number", at least 2), the grouping falls back to
      uniform random groups (Eq. 5).
    - Within a group, each player works one dimension at a time. It copies the group best's coordinate with
      probability p_study (Eq. 6), or copies a random group member's coordinate (Eq. 7). Two players may
      exchange a coordinate, each scaled by (1 + randn), with probability p_comm (Eqs. 8–9). With probability
      p_error = 0.001 a player copies another dimension of another player (Eq. 10).
    - Defaults are p_study = p_comm = 0.2 (pseudocode, p. 9).
  - *Selection.* Offspring replace parents greedily (Eq. 12, p. 9).
  - *Individual extra training* (§2.1.3, Eq. 11, p. 8). Only the best player is trained:
    F_best × (1 + (1 − 1/k)·Gauss + (1/k)·Cauchy), accepted only if it improves (pseudocode, p. 9).
- **IFTTA's critique and changes** (Hou et al. 2024, full text).
  - *The critique, specifically.* "Agents that choose the follower, discoverer, and thinker identities all
    learn from the best individual" (§3.1, p. 5). FTTA's extra training does perturb the optimal agent, "but
    it is less effective" (§3.2, p. 6). So **three of FTTA's four collective behaviours, plus the whole
    extra-training stage, reference the incumbent.** Volatilities are the only exception, and group training
    references the group best instead.
  - *Fitness-distance-balanced collective training (FTS, §3.1, Eqs. 11–13, pp. 5–6).* X_best is replaced by an
    agent chosen on a score, ω·norm(fitness) + (1 − ω)·norm(distance to best). The roulette variant was best
    (Table 4, p. 9).
  - *Non-monopoly extra training (NTS, §3.2, Eqs. 14–17, p. 6).* A coordinate-level perturbation of the best
    agent with Gaussian or Cauchy factors.
  - *Population restart (PRS, §3.3, Eq. 18, p. 7).* Each agent carries a counter, Trial_i, of updates without
    improvement. When the counter passes a threshold, the agent is restarted by either a masked partial random
    re-initialisation or a DE-like difference move, (X_r1 − X_r2). The threshold's value is not given in the
    method text.
  - *Ablation.* Every strategy improves FTTA, and FTS helps most (Table 8, p. 12).
- **Resolved questions.**
  - *Update rules.* The four behaviour rules are confirmed above. The type is drawn at random at every
    iteration.
  - *"Adaptive cluster grouping".* It is GMM-EM clustering in decision space at every iteration, with a random
    fallback. The four group labels are cluster names. Every group uses the same learning rules, and these
    rules are per-coordinate discrete recombination (copy or exchange), not movement.
  - *Individual extra training.* It is a multiplicative Gauss–Cauchy mutation of the incumbent at every
    iteration, with greedy acceptance.
  - *How incumbent-centric is FTTA?* Highly: 3 of 4 collective behaviours use the global best, and 2 of those
    also use the global worst.
- **Overlap with TFO.**
  - Archetypes: partial, as pass 1 recorded, now confirmed. FTTA's behaviour types are drawn at random each
    iteration. In TFO an archetype is bound to a lattice slot and changes only through ROT.
  - FORM / B2B: **partial, and sharper than pass 1 recorded.** FTTA *does* change who interacts with whom at
    every iteration, through its GMM clusters. TFO therefore cannot claim to be the only football method with a
    time-varying interaction structure. The defensible difference is that FTTA's partition is recomputed from
    positions by an unsupervised clusterer, a speciation-style partition. It is not a lattice whose shape a
    controller sets, and it carries no takeover-time prediction.
  - SET: partial, as pass 1 recorded, now confirmed as a different family. FTTA intensifies around the
    incumbent every iteration with a stochastic multiplicative mutation. TFO's set pieces are fixed-period,
    scripted designs: an orthogonal-array corner and a parabolic-interpolation free kick.
  - FIN: **partial (new).** FTTA's extra training mixes a heavy-tailed Cauchy term into its mutation, with
    weight 1/k, and IFTTA's NTS does the same. So the heavy-tailed-mutation family does appear in the football
    family. TFO's Finisher differs on three counts:
    - its Lévy jumps are centred on the ball, not the incumbent;
    - its heavy tail does not decay as 1/k;
    - it restarts from an archive elite after repeated misses.
  - SUB: **partial (new, via IFTTA).** PRS is a per-agent, stagnation-triggered restart, the closest
    football-family counterpart to TFO's substitutions. TFO's differences:
    - the trigger also requires low stamina;
    - substitutions are capped at five per fixture;
    - the replacement is a fresh uniform agent;
    - the outgoing position is marked tabu for VAR.

    IFTTA's PRS is uncapped, has no tabu memory, and part of it is a DE-like move.
  - B2B: weak. Differential vectors appear (the thinkers' best − worst, and IFTTA's X_r1 − X_r2), but no donor
    is restricted to a neighbourhood.
- **No counterpart in FTTA/IFTTA.** BALL, PRESS, CTR, OFF, VAR and FAT. MGR is also absent: FTTA has no
    adaptive control, and IFTTA's adaptive ω is an iteration-based schedule. Nor do ZCB, OWB, DES or VIR
    appear.
- **Verdict:** partial overlap (role heterogeneity, a time-varying partition, heavy-tailed incumbent mutation,
  and stagnation restarts through IFTTA); distinct on structure. FTTA is the most-cited football method (161
  Crossref citations), and MTTA's Friedman summaries rank it third of eleven on both of MTTA's suites (§4.1–4.2,
  pp. 22–24). It is still the natural **empirical** football-family baseline and is worth adding to the
  comparator roster.

### 2.12 Football Optimization Algorithm (FbOA) — full text read

- **Reference.** El-Kenawy, E.-S.M., Rizk, F.H., Zaki, A.M., Mohamed, M.E., Ibrahim, A., Abdelhamid, A.A.,
  Khodadadi, N., Almetwally, E.M., & Eid, M.M. (2024). Football Optimization Algorithm (FbOA): A novel
  metaheuristic inspired by team strategy dynamics. *Journal of Artificial Intelligence and Metaheuristics*
  8(1), 21–38. doi:10.54216/JAIM.080103 (Crossref 87; Consensus 86). Received 12 March 2024 and accepted 11
  August 2024.
  - The full nine-author list is taken from the PDF's first page (p. 21): El-Sayed M. El-Kenawy, Faris H.
    Rizk, Ahmed Mohamed Zaki, Mahmoud Elshabrawy Mohamed, Abdelhameed Ibrahim, Abdelaziz A. Abdelhamid, Nima
    Khodadadi, Ehab M. Almetwally, Marwa M. Eid. Crossref's deposit is malformed: it lists affiliations as
    authors and identifies only two people.
- **Metaphor.** Team strategy in match play.
- **Mechanism** (full text).
  - *Passes appear in prose only* (§3.1, p. 26). "Short passing, lob passing, and … through ball passing, each
    corresponding to different search techniques". Short passing is local search in close neighbourhoods, lob
    passing is intermediate search, and the through ball ("long-range") pushes agents into new areas.
  - *Exploration* (§3.2.1, pp. 26–27).
    - "Fb(S(t+1)) = i".
    - A velocity V_n = F_max(b_x·a_i[F_ext − F_min] + r·b_y·a_j[F_best − F_min] × cos(π/Iteration)).
    - A "best force" F_best = (1/K) Σ_{n=0}^{K} F_max^{n²}/(2n+1)².
  - *Exploitation* (§3.2.2, p. 28): Fb(S(t+1)) = F_i + z_3·Fb(S(t)) + K·sin(π/Iteration).
  - *Mutation* (§3.2.2, p. 28): S(t) = K·a_q((2n+1)/x) + K·cos(π/Iteration).
  - *What is missing.* There is no pseudocode. F_ext, F_min, a_i, a_j, a_q and x are not operationally
    defined, and the paper does not say how V_n enters the position update.
  - *Parameters.* The listed parameters (a1, a2, b1, b2, r1, z, Θ ∈ [0, 12π], a ∈ [−8, 8]; §5.1, Table 2,
    p. 30) do not match the symbols in the equations. §5.1 also calls the method a "Feedback-based
    Optimization Algorithm".
  - *Evaluation.* Mean and standard deviation are reported for 7 unimodal functions only (Table 3, p. 31). The
    100-D table reports time and FEs, not accuracy (Table 5, p. 34).
- **Resolved questions.**
  - *What are the short-pass and long-pass equations?* **The paper contains none.** The long pass is
    described only in prose, as a long-range search step. It is neither a graph-distance link nor a partner
    choice.
  - *Is there a positional-adjustment rule?* **No dedicated rule exists.** The published mechanism is too
    under-specified to reimplement from the paper.
- **Overlap with TFO.**
  - REG: metaphor only. TFO's "long" is graph distance on the formation lattice (BLX-α with the partner at
    maximum graph distance), not step length.
  - BALL: none. FbOA has no ball state and no pass partner.
- **No counterpart in FbOA.** Everything at the mechanism level.
- **Verdict:** distinct at the mechanism level. Cite FbOA for its name proximity (see `spec.md` Assumptions →
  Name) and as an example of a metaphor-only "long pass". It cannot be used as a baseline without the authors'
  code.

### 2.13 Soccer Match Algorithm (SMA) — full text read

- **Reference.** Ben Ammar, R., Gharbi, A., & Babai, M.Z. (2024). Soccer Match Algorithm for global
  optimization: A contender metaheuristic. *IEEE Access* 12, 93924–93945. doi:10.1109/ACCESS.2024.3424791
  (Crossref 7; Consensus 5). Published 8 July 2024. The authors (Roua Ben Ammar, Anis Gharbi, Mohamed Zied
  Babai) are confirmed on p. 93924.
- **Metaphor.** A full soccer match between two teams.
- **Mechanism** (full text).
  - *Representation* (§III.A–B, pp. 93926–93927). **SMA evolves exactly two candidate solutions.** "Each of
    the two teams represents an individual solution, while decision variables are represented by the
    artificial soccer players". An n-variable problem therefore gives each team n players, one of them a
    goalkeeper.
  - *Tactical composition* (§III.B.1, Eq. 1, p. 93927).
    - T : n_D ∼ n_M ∼ n_F sets how many players (decision variables) are defenders, midfielders and forwards.
      The counts are scaled from a ten-outfield-player team, for example n_D = ⌈4(n−1)/10⌉.
    - "In our experiments, we implemented the mostly used tactical composition T = 4∼4∼2."
    - A role fixes a player's seven skill scores: pass, dribble, pace, shoot, goalkeeping, ball control and
      defence (§III.B.2, Tables 3–4).
  - *Playing style* (§III.B.3, Eq. 2). S = [s_pass, s_dribble, s_run, s_shoot].
  - *Moves* (§III.C.3–6, pp. 93928–93929).
    - A two-player move (pass, dribble or shot) builds a score-weighted focal point, F_AB = (RS_A·X_A +
      RS_B·X_B)/(RS_A + RS_B) (Eq. 3). Each of the two variables is resampled uniformly between its old value
      and F_AB.
    - A run resamples the variable uniformly within ±Rd_A, where Rd_A = |X_A|·Pace_A/100 (Eq. 4).
    - The move type is drawn by roulette on style plus the player's relevant score (§III.C.4, Table 5).
    - The receiver or defender is drawn by roulette on relevant scores over **all** teammates or opponents
      (§III.C.5, Table 6).
    - After a pass or dribble, every other outfield player of both teams also runs (§III.C.6; pseudocode step
      5.b.iii, p. 93931).
  - *Learning* (§III.C.7, pp. 93929–93930). There are two mechanisms, both driven by the team's fitness change
    per move (the "percentage of fitness evolution").
    - Each directly involved player's relevant skill score changes by +1 if that change is positive and by −1
      otherwise (Table 8).
    - After the last k uses of a move type, that type's style parameter is set to the mean fitness-improvement
      percentage over those uses, with negative values set to zero. The style vector is then rescaled to sum
      to 100 (Table 10).
    - Tuning chose S = [0.1, 0.1, 0.1, 0.7] and K = 100 (§IV.A, p. 93932).
  - *Possession* (Table 9, p. 93930).
    - A pass leaves the ball with the receiver on success, and gives it to a random opponent on failure.
    - A dribble leaves it with the dribbler on success, and gives it to the defender on failure.
    - A shot hands kick-off to the opponents on success, and gives the ball to their goalkeeper on failure.
    - A move counts as a "success" if it "has the best positive fitness evolution" (p. 93930).
  - *Acceptance* (p. 93930; pseudocode step 5.d.iii, p. 93931). Every move builds on the latest solution even
    if it is worse. After a shot, which ends an action, play resumes from the fitter of the team best and the
    current solution ("Revert Decision Variables to Best Values").
  - *Substitution* (§III.C.8, p. 93930). After each iteration, any player whose score is null or negative is
    replaced by a new player with the same variable value. The pseudocode says the replacement has a
    "Different Tactical Role".
- **Resolved questions.**
  - *Do "compositions" change who interacts with whom?* **No. This resolves the panel's highest-priority
    question in TFO's favour.**
    - Compositions are **role counts over the decision variables** of each of the two solutions, fixed at
      4-4-2 in every experiment.
    - Interaction partners are drawn by score-weighted roulette over all teammates or all opponents, so no
      interaction topology exists anywhere in SMA.
    - Because SMA's "players" are coordinates rather than candidate solutions, its "player interactions" are
      coordinate-level moves inside, or between, two solution vectors.
    - Substitution can change one player's role, and so let the role counts drift, but it never restricts
      partners.
    - **TFO's formation-as-controlled-topology claim is unaffected by SMA.**
  - *What does the adaptive framework adapt, and on what signal?* It adapts two things. The first is
    **per-operator selection weights (the style vector)**, set from each move type's recent mean improvement.
    This is continuous credit-assignment adaptive operator selection in the probability-matching sense
    (Goldberg 1990; Thierens 2005). The second is **per-variable skill scores**, reinforced by ±1 per move.
    - The signal is the team's fitness change per move.
    - It is **not a state machine**: there are no discrete tactical states, and nothing structural
      (composition, partner rules or acceptance) is switched.
    - The abstract's "tactical shifts during a game" are these style-vector updates.
- **Overlap with TFO.**
  - MGR: partial at the level of "adaptive parameter control" (Eiben et al. 1999), but a **different family**.
    SMA assigns credit per operator. TFO's manager is a finite-state controller that reads diversity,
    possession rate, goal drought and the match clock. Each of its states sets the formation's shape, ρ, τ,
    the pass-chain length and the role rates. If reviewers press on the manager, the natural extra control is
    an adaptive-operator-selection variant of TFO, in addition to TFO-static.
  - BALL / CTR: **closer than the abstract suggested (new).** SMA's possession is kept or lost according to
    whether the move improved fitness (Table 9). That is fitness-contingent retention with outcome-triggered
    turnovers. However:
    - SMA's ball is a *scheduling token* that decides which variable of which solution moves next. It is not
      a point in the search space.
    - A turnover relocates nothing, and no burst follows.

    TFO's defensible differences:
    - its ball is a focal point in the search space, moved by drift steps;
    - retention is threshold acceptance with a controlled τ;
    - a counter-attack relocates the focal point to a materially better off-ball point and triggers a
      decaying large-step burst.
  - VAR: weak analogue (new). SMA reverts to the team best after every shot. That is a periodic, fitness-based
    restart-from-best at action boundaries. It is not an audit: there are no non-fitness criteria, no
    aspiration clause, and accepted moves are never rolled back by a rule set.
  - SUB: vocabulary only. SMA's substitution resets one coordinate's role and skills and keeps its value.
  - Archetypes / ROT: weak. SMA's roles set *skill scores*, and every player uses the same move operators.
    There is no rotation.
  - *Methodological note.* Eq. 4 makes the run radius proportional to |X_A|, so steps vanish near the
    coordinate origin. That is an origin-centred bias to remember if SMA is ever run on unshifted functions.
    The benchmark is 13 classic functions at n = 10, 25 and 50 with a 5,000-FE cap (§IV.B).
- **No counterpart in SMA.** FORM, PRESS, SET, OFF, FAT, and the ZCB, OWB, DES, REG, B2B, VIR and FIN families.
- **Verdict:** **distinct on FORM (resolved).** Partial on MGR (a different family: adaptive operator
  selection versus a state machine). Partial on BALL/CTR (a fitness-contingent possession token). Weak on VAR.
  The novelty paragraph must cite SMA for adaptive control, for fitness-contingent possession and for
  reversion to the best.

### 2.14 Football Optimization Algorithm (FOA, 2012) — added in pass 2 from Alatas §3.7

- **References.** Hatamzadeh, P., & Khayyambashi, M.R. (2012a). Football optimization: an algorithm for
  optimization inspired by football game. *11th Intelligent Systems Conference (ICS11)*, Kharazmi University,
  Tehran. The TTA paper cites it at p. 261. · Hatamzadeh & Khayyambashi (2012b). Neural network learning based
  on football optimization algorithm. *CICIS 2012*, 8–14 (as cited in SMA, ref. [20]). No DOI was found, and
  the primary text was not obtained.
- **Metaphor.** A team of main and substitute players passing to the best-placed player while spectators
  disturb play.
- **Mechanism** (secondary: Alatas §3.7.1, Eqs. 28–32, Table 7; SMA §II.G, p. 93926).
  - The team is split into m = round(n·α) main players plus substitutes.
  - Ball owner = the best index of Rank_i = Fitness(player_i) + U(−d, d) over the main players, **which is a
    noisy incumbent**.
  - A pass is a parameter exchange between the passer and the owner.
  - The other players move toward the best player.
  - "Spectators" make random parameter changes.
  - The best substitute replaces the weakest main player whenever it is stronger.
  - FGA's introduction (p. 6) and Alatas §6 both describe FOA's formulation as vague.
- **Overlap with TFO.** BALL at the metaphor level only (the ball is the incumbent, as in SGO); SUB is
  vocabulary only. Its long name is **identical** to FbOA's (§2.12).
- **Verdict:** distinct. Cite it for completeness and in the naming footnote.

### 2.15 Adjacent: Stadium Spectators Optimizer (SSO)

- **Reference.** Nemati, M., Zandi, Y., & Sadighi Agdas, A. (2024). Application of a novel metaheuristic
  algorithm inspired by stadium spectators in global optimization problems. *Scientific Reports* 14, 3078.
  doi:10.1038/s41598-024-53602-2 (Crossref 16).
- **Metaphor.** Spectators influencing players during a match. The sport is not specified in the abstract.
- **Mechanism** (abstract). A parameter-free update driven by the influence of spectators. It is benchmarked
  against TTA.
- **Verdict:** distinct. It is listed because it is match-inspired and compares itself against TTA.

---

## 3. Non-football sports-inspired methods (landscape check)

This pass also covered the wider sports family. The treatment here is deliberately short. None of these
methods models football, and none has an operator that comes close to TFO's structural claims. The few
analogues worth noting are called out.

| Method | Reference (verified via Crossref unless noted) | Mechanism in one line | Note vs TFO |
|---|---|---|---|
| Volleyball Premier League (VPL) | Moghdani & Salimifard (2018), *Applied Soft Computing* 64, 161–185, doi:10.1016/j.asoc.2017.11.043 (Crossref 287) | League of teams, with "substitution, coaching, and learning" terms | Uses "substitution" as vocabulary. League competition, like LCA |
| Tug of War Optimization (TWO) | Kaveh & Zolghadr (2016), IUST journal (Consensus 84). **Venue not Crossref-verified** | Solutions are teams that pull on one another by fitness-weighted forces under Newtonian dynamics | Physics-style pairwise attraction. No overlap |
| Most Valuable Player Algorithm (MVPA) | Bouchekara (2020), *Operational Research* 20(1), 139–195, doi:10.1007/s12351-017-0320-y (online 2017) | Players form teams and compete both as teams and individually for MVP (Alatas §3.9) | League-type. No overlap |
| Basketball Team Optimization Algorithm (BTOA) | Chen et al. (2025), *Scientific Reports* 15, 21629, doi:10.1038/s41598-025-05477-0 | "High-intensity training, fast breaks, dynamic positioning, coordinated passing" | **Fast break ≈ counter-attack (CTR) and passing ≈ BALL at the metaphor level.** Worth one sentence in the paper. Its trigger rules were not verified |
| Kho-Kho Optimization (KKO) | Srivastava & Das (2020), *Engineering Applications of Artificial Intelligence* 94, 103763, doi:10.1016/j.engappai.2020.103763 | Chasing strategies of a tag-team game | No overlap |
| Kabaddi Game Optimizer (KGO) | Ayyarao et al. (2026), *Array* 31, 101138, doi:10.1016/j.array.2026.101138 | Two teams, raid/defend moves, leader exchange, replacement of weak individuals | Replacement of weak individuals is weakly like SUB |
| Running City Game Optimizer (RCGO) | Ma, Hu, Lu & Liu (2023; online 2022), *Journal of Computational Design and Engineering* 10(1), 65–107, doi:10.1093/jcde/qwac131 | Siege, defensive and eliminated-selection strategies | No overlap |
| Squid Game Optimizer | Azizi et al. (2023), *Scientific Reports* (Consensus 77). **DOI not verified** | Offensive and defensive groups with random attack moves | Game-inspired rather than sport. No overlap. Its acronym "SGO" collides with Soccer Game Optimization |

Other game- or human-activity-inspired methods seen in search but out of scope: Hiking Optimization Algorithm
(*Knowledge-Based Systems*, 2024), Battle Royale Optimization (2020), Team Competition and Cooperation
Optimization (2022), and Offensive Defensive Optimization (*Scientific Reports*, 2025, inspired by board
games). None is football-inspired.

Searches for corner-kick, free-kick, penalty, offside, referee or VAR-specific metaheuristics found **no such
algorithm**. The results were sports-analytics papers (optimising real penalty kicks and corners, for
example TacticAI), not optimizers. A search for a referee-, VAR- or rollback-audit-inspired optimizer found
only an unrelated "referee" verification procedure in bilevel derivative-free optimization benchmarking. It is
not a sports metaphor and does not roll back accepted moves. None of the eight full texts read in pass 2
contains a set-piece, offside or referee operator either.

---

## 4. Synthesis table

**Evidence** records the best source read for each method: **FT** is the full text, **Sec** is a secondary
description (Alatas or a variant paper), **Abs** is the abstract only, and **Snip** is a web snippet only.

| Algorithm | Year | Evidence | What it models | Closest TFO mechanism(s) | Verdict |
|---|---|---|---|---|---|
| LCA / PLCA | 2009/2014 (PLCA 2019) | Abs + Sec | League fixtures between individual "teams". "Formation" means the solution vector | none. League clock ≈ fixture clock only | **Distinct** (terminology note on "formation") |
| FOA | 2012 | Sec | Ball owner = noisy best. Parameter-exchange passes. Substitutes | BALL (ball = incumbent), SUB (vocabulary) | **Distinct** (name identical to FbOA) |
| SLC | 2014 | Abs + Sec | Multi-team league. Fixed players vs substitutes. Imitation, provocation, mutation | SUB (vocabulary), ROT (global rank reallocation) | **Distinct** |
| SLO | 2014 (arXiv) | Abs + Sec | Rich/regular/poor tiers, transfers, youth discovery | SUB (random immigrants) | **Distinct** |
| SLOCA | 2022 | Snip | Qualifying and main competitions, **fatigue factor**, **reserve players** | **FAT, SUB** | **Partial overlap: needs scrutiny** (no full text) |
| Golden Ball | 2013/2014 | Abs + Sec | Multi-population league for combinatorial problems. Captains, training, transfers, coach replacement | MGR (weak, unspecified), SUB (stagnation exchange) | **Distinct** (different problem class) |
| WCO | 2016 | Abs + Sec | Continental tournament with play-off | none | **Distinct** |
| SGO (+SGOLS) | 2013/2015 (2020) | Abs + Sec | Ball dribbler = best-so-far. Move forward/move off. Substitute elite pool. Nearby-player info | BALL (but ball = incumbent), SK, B2B (local info, definition unverified) | **Partial overlap** |
| FGA | 2016 | **FT** | Random walk + pull toward a fitness-biased ball-holder. Coach memory with decaying distance/fitness thresholds that relocate agents near elites | SK, FIN, SUB (coach memory); BALL (metaphor); PRESS (weak) | **Partial overlap**. MGR overlap withdrawn |
| **TTA** | 2020/2021 | **FT** | n balls (one per player) passed along a fixed index ring, random loss (p = 0.1–0.3), pull toward own ball + random top-10 % elite | **BALL** (closest prior art), FORM (fixed ring) | **Closest prior art on BALL; partial on FORM.** Defensible on acceptance rule, controlled 2-D lattice, single ball, event turnovers |
| MTTA | 2026 | **FT** | TTA + per-iteration fitness-ranked forward/midfielder/defender variants of one attraction family; success-based step factor ("regista") | ROT, MGR (scalar), REG (name), archetypes (weak), BALL (via TTA) | **Partial overlap**. Distinct on structure |
| FTTA (+IFTTA, MIFTTA) | 2024 (2024, 2025) | **FT** (FTTA, IFTTA); Abs (MIFTTA) | Random per-iteration behaviour types (3 of 4 best-guided), GMM clusters recomputed every iteration, Gauss–Cauchy mutation of the best; IFTTA adds stagnation restarts | Archetypes, FORM/B2B (clusters), FIN (Cauchy), SET (different family), SUB (IFTTA PRS) | **Partial overlap**. Distinct on structure |
| FbOA | 2024 | **FT** | Short/lob/through-ball passes in prose only; under-specified velocity, exploitation and mutation formulas | REG (metaphor only) | **Distinct at mechanism level** (not reimplementable) |
| **SMA** | 2024 | **FT** | Two solutions; players = decision variables; role counts (4-4-2); per-operator credit-assignment adaptation; fitness-contingent possession; revert to best after shots | **MGR** (different family), BALL/CTR (possession token), VAR (weak) | **FORM resolved: distinct.** Partial on MGR, BALL/CTR |
| SSO | 2024 | Abs | Spectator influence on players | none | **Distinct** |

**Coverage across TFO's 19 mechanisms (after pass 2).** No football-inspired method found has a counterpart
for any of the following:

- **OFF**: bound repair plus the moving ε-constrained line.
- **VAR**: a deferred audit on non-fitness grounds, with rollback and an aspiration clause. SMA's end-of-action
  reversion to the best is the nearest thing, and it is a plain fitness restart.
- **SET**: fixed-schedule, scripted orthogonal-array or parabolic designs.
- **FORM as a *controlled* lattice topology.** SMA has no topology at all. TTA's fixed index ring and FTTA's
  per-iteration GMM partition are the nearest, and neither is shape-controlled.
- **PRESS as distance-gated encircling of the ball.** FGA's hyper-radius penalty is the only distance-gated
  rule, and it sends *far* agents to an archived elite.
- The archetype operator families **ZCB** (stratified sampling), **OWB** (quasi-opposition), **DES** (clearing
  niching) and **VIR** (pattern search).

**FIN** has moved from "no counterpart" to "partial": heavy-tailed Cauchy mutation of the incumbent appears in
FTTA and IFTTA.

Partial overlaps exist for the following. Each needs a stated, mechanism-level difference in the paper:

- **BALL:** TTA (closest: a separate ball matrix and ring passes), SMA (fitness-contingent possession token),
  SGO and FOA (ball = incumbent), FGA (fitness-biased ball-holder); FbOA at the metaphor level only.
- **FORM:** TTA (fixed directed index ring on the balls), FTTA (GMM clusters recomputed every iteration).
- **ROT and archetype heterogeneity:** MTTA, FTTA, SMA, SLC.
- **SUB:** IFTTA's stagnation-triggered restart (closest), SLOCA, SLC, SLO, SGO, FOA, FGA (fitness-threshold
  relocation), Golden Ball (stagnation exchange); SMA in vocabulary only.
- **FAT:** SLOCA (unverified).
- **MGR:** SMA (per-operator credit assignment), MTTA (success-based step-size factor).
- **REG:** MTTA (uses the name "regista"; long pass = large step), FbOA (prose only).
- **SK:** SGO (substitute elite pool), FGA (coach memory), TTA (key-player archive).
- **FIN:** FTTA and IFTTA (Cauchy mutation of the incumbent), FGA (relocation around the nearest elite).
- **CTR:** SMA (outcome-triggered turnover without relocation), BTOA (basketball "fast break", outside the
  football family).
- **VAR:** SMA (reversion to the best, weak).
- **PRESS:** FGA (distance-gated but opposite in direction), MTTA (metaphor only).
- **SET:** FTTA (intensification around the incumbent every iteration; a different family).
- **B2B:** FTTA thinkers and IFTTA PRS (differential vectors, not restricted to a neighbourhood).

---

## 5. Positioning statement (the panel's judgement)

> Football is the most heavily mined sports metaphor in metaheuristics. At least thirteen football- or
> soccer-specific optimizers appeared between 2012 and 2026, following the generic League Championship
> Algorithm of 2009. Together they have already used league competition, a ball or ball-carrier attractor,
> short and long passes, fitness-contingent possession, role specialisation (even under the name *regista*),
> substitutes and stagnation-triggered restarts, fatigue, coach-driven tactical shifts and feedback-driven
> parameter adaptation. TFO therefore claims none of these football *concepts* as new. Every TFO operator is
> presented as an instance of a named, metaphor-free operator family. What TFO contributes is a *structural*
> composition that none of these methods has.
>
> First, all agent interaction runs along the edges of an explicit lines × lanes lattice whose *shape* is a
> controlled variable, and that yields a falsifiable takeover-time prediction (H3). Other football methods
> restrict or vary interaction: the Tiki-taka Algorithm passes along a fixed index ring, and the Football Team
> Training Algorithm re-clusters its groups every iteration. None makes the topology's shape a control
> variable or ties it to structured-population theory.
>
> Second, a single focal point in the search space, distinct from the incumbent, is moved along those edges
> and retained by threshold acceptance. The Tiki-taka Algorithm keeps one unevaluated ball per player and
> loses it at random. Soccer Game Optimization and the Football Optimization Algorithm equate the ball with the
> incumbent. The Soccer Match Algorithm's fitness-contingent possession decides which decision variable moves
> next, not where the search is focused.
>
> Third, a counter-attack is an event triggered by where improvement occurs. It relocates the focal point to a
> materially better off-ball point and launches a decaying burst. The Soccer Match Algorithm's turnovers are
> also outcome-triggered, but they relocate nothing.
>
> Fourth, two mechanisms have no counterpart anywhere in this family. One is a deferred VAR audit that rolls
> back accepted moves on non-fitness grounds, with an aspiration clause; the Soccer Match Algorithm's
> end-of-action reversion to the best is a plain fitness restart. The other is a moving offside ε-feasibility
> line.
>
> The value of the adaptive manager is not asserted from the metaphor. The Soccer Match Algorithm already
> adapts operator probabilities from per-move improvement, and the Modernized Tiki-taka Algorithm adapts its
> step size on improvement or stagnation. The manager's value is measured by a pre-registered ablation against
> TFO-static (H2).

**What the full-text pass changed.** The panel had flagged one possible blocker: SMA's "compositions" might
reshape who interacts with whom, which would force a narrower formation claim. **The full text rules that
out.** SMA evolves two solutions whose "players" are decision variables. Its compositions are role counts,
fixed at 4-4-2, and its interaction partners are drawn by score-weighted roulette over the whole team. So the
formation claim did **not** need narrowing on SMA's account. It is still stated above in its narrow form
("*shape* … controlled … takeover-time prediction"), for a separate reason: pass 2 showed that TTA
(a fixed ring) and FTTA (per-iteration clusters) do restrict or vary interaction. The manuscript must therefore
not imply that no football method restricts or varies who interacts with whom.

The other changes relative to the pass-1 statement:

1. The ball clause now contrasts TFO with SMA's possession token and FOA's noisy incumbent, as well as with TTA
   and SGO.
2. The counter-attack clause now rests on *relocation plus burst*, not on "turnovers are events", because SMA
   already has outcome-triggered turnovers.
3. The VAR clause now specifies non-fitness audit criteria and names SMA's reversion as the nearest analogue.
4. The concept list now includes fitness-contingent possession, stagnation restarts, the *regista* name and
   feedback-driven adaptation.
5. The count of football-specific methods rises from twelve to thirteen with the addition of FOA (2012).

**Manuscript obligations that follow from pass 2.**

- Cite TTA in both the possession row and the formation row.
- Cite SMA in the manager, possession/counter-attack and VAR discussions.
- Cite FTTA in the formation row (clusters) and the Finisher row (Cauchy mutation), and IFTTA in the
  substitution row.
- Cite MTTA in the rotation and manager rows, and either acknowledge MTTA's prior use of *regista* or rename
  TFO's archetype.
- Cite FGA in the Sweeper-Keeper and substitution rows.
- Footnote FOA vs FbOA.

**Remaining condition.** The claim stays conditional on reading SLOCA's full text (FAT, SUB) before
submission. SGOLS's "nearby" definition and FOA's primary text are lower-risk checks (§6).

---

## 6. Verification notes (manual checks required before citing)

1. **Full-text status.**
   - *Read in full on 2026-09-24 from the owner-supplied PDFs:* SMA, TTA, FbOA, FGA, MTTA, FTTA, IFTTA, and the
     Alatas survey.
   - *Not read, so abstract, secondary or snippet evidence only:* SLOCA, SGO and SGOLS, LCA, SLC, SLO, Golden
     Ball, WCO, FOA (2012), MIFTTA, the TTA multi-objective variant, IFGO, BTOA, and SSO.
   - **Priority order for what remains: SLOCA → SGOLS → FOA (2012) → Golden Ball.**
2. **SLOCA** (unchanged; still the one open item that could touch a claim). What the fatigue factor scales and
   what clock drives it; how reserve players are triggered. **There is no Crossref DOI.** The venue (*Advances
   in Computational Design* 7(4):297, Techno-Press) comes from web snippets only, and the end page is unknown.
3. **SGOLS.** Whether "nearby players" is index-based or Euclidean. No full text has been seen.
4. **FOA (2012).** The primary text and full bibliographic details: the ICS11 proceedings at Kharazmi University
   (TTA cites p. 261) and CICIS 2012, pp. 8–14. There is no DOI. The mechanism above comes from Alatas §3.7 and
   SMA §II.G.
5. **Golden Ball.** What "cessation of coaches" changes algorithmically. Alatas §3.5.1 reports only that
   coaches are replaced after bad results. This is low priority because GB is combinatorial and distinct
   either way.
6. **Residual ambiguities *inside* papers that were read.** The text itself is unclear on these points, so do
   not over-state them in the manuscript.
   - TTA's printed Eq. 3 has signs that are the reverse of its prose. Describe TTA's ball rule by its
     structure (ring partner, fitness-independent random loss, n balls), not by the direction of the step.
   - FGA does not specify the distribution used to choose the ball-holder.
   - SMA's definition of a "success" ("the best positive fitness evolution") is ambiguous.
   - IFTTA's PRS threshold is not stated in the method section.
   - MTTA's recap of TTA misprints the ring wrap-around ("b_{i+1} is replaced with b_i").
   - FbOA's equations are under-specified and cannot be reimplemented.
7. **Author metadata — resolved on the PDFs.** FTTA is *Zhirui Tian & Mei Gai* (Crossref was right and
   Consensus was wrong). MTTA is *Xiangkun Song & Jian Zhao*. FbOA has the nine authors listed in §2.12.
8. **Citation counts differ by source and change over time.** Values here are from 2026-09-24. `spec.md`
   previously gave FTTA "~145" (the Consensus figure); Crossref shows 161. FbOA is 86 (Consensus) or 87
   (Crossref). Cite counts sparingly, if at all, and re-pull them at submission.
9. **Online versus print years.**
   - TTA: accepted May 2020, online 2020, print 2021 (vol. 38(1)).
   - Alatas: online 2017, print 2019 (*AIR* 52(3):1579–1627, doi:10.1007/s10462-017-9587-x). The supplied PDF
     is the online-first version without page numbers; SMA's reference [11] confirms the print details.
   - SMA: online 8 July 2024. MVPA: online 2017, print 2020. RCGO: online 2022, print 2023.
   - Follow the target journal's style.
10. **Not Crossref-verified:** TWO's venue and pages; the Squid Game Optimizer DOI; the SGOLS DOI (taken from a
    URL); the chaotic-map FTTA conference paper; SLO (arXiv:1406.4462, no DOI); FOA (2012, no DOI).
11. **Name and acronym collisions to footnote in the manuscript.**
    - "SGO" is both Soccer Game Optimization and Squid Game Optimizer.
    - "SSO" is the Stadium Spectators Optimizer here, and other methods also use SSO.
    - "SMA" is also the Slime Mould Algorithm (Li et al., 2020), a far more widely used metaheuristic.
    - "FOA" (Hatamzadeh & Khayyambashi, 2012) and "FbOA" (El-Kenawy et al., 2024) have the **same** long name,
      "Football Optimization Algorithm", and "FOA" is also the Fruit Fly Optimization Algorithm.
    - MTTA already uses **"regista"** for a different mechanism (§2.10).
12. **Search budget.** The Consensus monthly quota was exhausted during pass 1 (it resets 2026-10-01). A
    follow-up sweep for 2026 football variants published after mid-2026 is advisable closer to submission.
13. **Reviews to cite for the landscape:** Alatas (2019), doi:10.1007/s10462-017-9587-x (Crossref 39;
    Consensus 47). The full text was read, and it covers nine sports algorithms including FOA. Osaba & Yang
    (2021), *Springer Tracts in Nature-Inspired Computing*, 81–102, doi:10.1007/978-981-16-0662-5_5.
