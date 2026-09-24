# Related Work: Football- and Sports-Inspired Metaheuristics vs. the Total Football Optimizer (TFO)

**Status.** This is the authoritative prior-art review for TFO. It replaces the "prior art to verify" note that
was in `spec.md`. Search date: 2026-09-24. Sources: the Consensus academic search index (Semantic Scholar,
Scopus, PubMed and arXiv), Crossref bibliographic verification through the FastTrack `verify_reference`
tool, and general web search, which returns abstracts and publisher or aggregator snippets. The full texts of
the primary papers could not be fetched in this session because every publisher host was blocked by the
network egress proxy. Where a mechanism is described below, the source is named: the *abstract*, a *secondary
description* in a later paper, review or code page, or a *snippet*. Anything that still needs the full text is
flagged in §6. Citation counts are a snapshot taken on 2026-09-24. **Crossref** means Crossref's
`is-referenced-by` count and **Consensus** means the count shown by the Consensus index. The two differ, and
both are reported where both were seen.

**Mechanism labels used below.** They refer to `mechanism-map.md`. Archetypes: SK Sweeper-Keeper, ZCB Zonal
Centre-Back, OWB Overlapping Wing-Back, DES Destroyer, REG Regista, B2B Box-to-Box Engine, VIR Virtuoso, FIN
Finisher. Team-level tactics: FORM formation-as-topology, ROT positional rotation, BALL ball and possession,
PRESS pressing, CTR counter-attack, SET set pieces, OFF offside line, SUB substitutions, FAT fatigue, VAR VAR
review, MGR the manager's state machine.

---

## 1. Introduction: why football needs careful positioning

Sports metaphors have been used in metaheuristic design since at least the League Championship Algorithm
(Kashan, 2009). Two surveys already catalogue the family. Alatas (2019, *Artificial Intelligence Review*)
covers LCA, Soccer League Optimization, Soccer Game Optimization, Soccer League Competition, Golden Ball,
World Cup Optimization, the Football Game Inspired Algorithm and the Most Valuable Player Algorithm. Osaba &
Yang (2021, Springer book chapter) cover the soccer-specific subset. Since 2020 the pace has increased. This
pass identified **twelve distinct football/soccer-specific optimizers (2013–2026)**. On top of these come the
generic sports-league LCA (2009), the match-adjacent Stadium Spectators Optimizer (2024), and at least seven
published variants. That makes football the most crowded single-sport metaphor in the field. Between them,
these methods have already used almost every obvious football idea:

- league and tournament competition among sub-populations (LCA, SLC, SLO, SLOCA, Golden Ball, WCO);
- a ball or ball-carrier as an attractor (SGO, FGA, TTA);
- short and long passes (TTA, FbOA);
- role heterogeneity and fitness-based role assignment (FTTA, MTTA, SMA);
- substitutes and reserve players (SGO, SLC, SLOCA);
- player fatigue (SLOCA);
- coach supervision and in-game tactical shifts (FGA, Golden Ball, SMA).

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
- **Mechanism** (abstract and secondary descriptions). A round-robin schedule pairs individuals. The match
  result is decided stochastically, and a fitter individual is more likely to win. A new solution is built by
  an "artificial match analysis", a SWOT-style update that combines differences from the winner/loser
  relations of the current and next-week pairings. An optional end-of-season "transfer" module exchanges
  parts of solutions. PLCA runs several local leagues as a multi-population.
- **Overlap with TFO.** Weak. The time-varying pairing schedule is a restricted interaction pattern, but it is
  a round-robin over the whole population, not a spatial lattice (FORM). Both algorithms use a fixture/season
  clock, but in TFO the fixture boundary is only a timing device (ROT, ZCB, FAT recovery).
- **Terminology collision (must be addressed in the manuscript).** In LCA, "team formation" means *the
  solution vector itself*. In TFO, "formation" means *the interaction topology*. The paper should state this
  explicitly so that a reviewer does not read TFO's formation as LCA's.
- **No counterpart in LCA.** All 8 archetypes, BALL, PRESS, CTR, SET, OFF, VAR, FAT, SUB, and the adaptive MGR.
- **Verdict:** distinct.

### 2.2 Soccer League Competition (SLC)

- **References.** Moosavian, N., & Kasaee Roodsari, B. (2014). Soccer league competition algorithm: A novel
  meta-heuristic algorithm for optimal design of water distribution networks. *Swarm and Evolutionary
  Computation* 17, 14–24. doi:10.1016/j.swevo.2014.02.002 (Crossref 220; Consensus 220). · Also *International
  Journal of Intelligence Science* 4(1), 7–16 (2014). doi:10.4236/ijis.2014.41002.
- **Metaphor.** A professional soccer league, with competition between teams and within each team.
- **Mechanism** (abstract and secondary descriptions). The population is partitioned into teams of *fixed
  players* and *substitutes*. Team power is the mean power of the fixed players. Teams play, and four
  operators follow. *Imitation* moves the winners' fixed players toward the best players. *Provocation* lets
  the winners' substitutes challenge fixed players. *Mutation* is applied to some of the losers' fixed
  players. *Substitution* is applied to the losers' reserves. Players are then re-sorted, with the best
  players going to the best teams.
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
- **Mechanism** (abstract). The population is split into three strata of teams. Strong teams buy the best
  players of regular teams, regular teams buy from the weakest, and the weakest "discover young players"
  (fresh random solutions). This amounts to hierarchical migration with random immigrants at the bottom tier.
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
  snippets of the ResearchGate and MathWorks pages.
- **Metaphor.** A soccer championship with qualifying and main competitions.
- **Mechanism** (snippet only). The algorithm runs in two stages, qualifying competitions and main
  competitions. It "applies a fatigue factor to players and randomly uses reserve players to avoid premature
  convergence."
- **Overlap with TFO. Needs scrutiny.** At the metaphor level SLOCA already has **both fatigue (FAT) and
  reserve players (SUB)**, which were not on the project's earlier list. The mechanism behind them is
  unverified. TFO's FAT is a *per-agent, workload-clocked* step-scale drain (proportional to distance covered),
  with recovery at fixture breaks that weakens over the season. TFO's SUB is stagnation-plus-stamina gated,
  capped at five per fixture, and feeds the VAR tabu register. If SLOCA's fatigue is a global,
  iteration-clocked decay, TFO differs in the same way `mechanism-map.md` already records against CA. That
  has to be confirmed from the full text.
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
- **Mechanism** (abstracts and secondary descriptions). GB is a multi-population method for **combinatorial**
  problems (TSP, CVRP, VRPB, bin packing). A team is a set of solutions, and its best member is the captain.
  *Conventional training* applies neighbourhood moves. *Custom training* works with the captain to escape
  local optima. League matches between teams, twice per season, set team scores, and those scores drive
  player and captain transfers at the end of the season.
- **Overlap with TFO.** Weak. There is a season/fixture clock, and there is a weak analogue of MGR if GB's
  coaches change their training operator when the team performs badly. That detail was **not confirmed** in
  what could be read.
- **No counterpart in GB.** GB is a discrete, permutation-based method, so none of TFO's continuous operators
  (OWB, B2B, VIR, FIN, SET, OFF) has a counterpart. Nor do FORM, BALL, PRESS, CTR, VAR or FAT.
- **Verdict:** distinct. It also belongs to a different problem class.

### 2.6 World Cup Optimization (WCO)

- **Reference.** Razmjooy, N., Khalilpour, M., & Ramezani, M. (2016). A new meta-heuristic optimization
  algorithm inspired by FIFA World Cup competitions: Theory and its application in PID designing for AVR
  system. *Journal of Control, Automation and Electrical Systems* 27(4), 419–440.
  doi:10.1007/s40313-016-0242-6 (Crossref 245; Consensus 258).
- **Metaphor.** The FIFA World Cup: continents, qualification, the tournament stages and a play-off.
- **Mechanism** (abstract and secondary descriptions). Solutions are grouped into "continents" and compete
  within them. The best advance to the next stage, and a *play-off* parameter gives third-placed teams a
  second chance. In effect this is hierarchical tournament selection with a controlled leak of non-winners.
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
- **Mechanism** (abstracts and secondary descriptions). The **ball dribbler is the best solution found so
  far**. *Move forward* is a local search between a player and the dribbler. *Move off* explores using the
  player's current position, its personal best and the dribbler. *Substitute players* form a pool that
  tracks a set of best-so-far solutions and is swapped in with probability η. In SGOLS, move forward also
  uses information from **nearby players**.
- **Overlap with TFO.**
  - BALL: partial. SGO has a ball-carrier attractor, but **SGO's ball is the incumbent**. TFO's central
    design claim is a ball that is *separate from the incumbent* and is carried by passes. SGO is therefore
    the clearest foil for that claim, not a counter-example to it.
  - SK: partial. SGO's substitute pool of best-so-far solutions is an elite archive, which is closer to
    TFO's Sweeper-Keeper archive than to TFO's substitutions.
  - B2B/FORM: partial. SGOLS's "nearby players" is a local neighbourhood, but it appears to be defined by
    distance, not by an explicit graph whose shape is controlled. Whether "nearby" is index-based or
    Euclidean needs the full text.
- **No counterpart in SGO.** FORM as a controllable topology, ROT, PRESS, CTR, SET, OFF, VAR, FAT, MGR, and
  ZCB/OWB/DES/REG/VIR/FIN.
- **Verdict:** partial overlap (BALL at the metaphor level, SK), distinct on structure.

### 2.8 Football Game Algorithm / Football Game Inspired Algorithm (FGA / FGO)

- **References.** Fadakar, E., & Ebrahimi, M. (2016). A new metaheuristic football game inspired algorithm.
  *2016 1st Conference on Swarm Intelligence and Evolutionary Computation (CSIEC)*, 6–11.
  doi:10.1109/CSIEC.2016.7482120 (Crossref 81; Consensus 71). · Variant: Subramaniyan, S., & Ramiah, J.
  (2020). Improved football game optimization for state estimation and power quality enhancement.
  *Computers & Electrical Engineering* 81, 106547. doi:10.1016/j.compeleceng.2019.106547.
- **Metaphor.** Players searching for good scoring positions under a coach's supervision.
- **Mechanism** (abstract and secondary descriptions). Each player combines a *random walk* with a *move
  toward the player who has the ball*. A *coach* acts as a higher-level supervisor. The authors claim the
  method can locate multiple global optima. The improved variant (IFGO) adds "offensive players who may
  cause injuries."
- **Overlap with TFO.**
  - BALL: partial. There is a ball-holder attractor. Whether the ball-holder is simply the current best
    (as in SGO) or a separately moving focal point is **not confirmed**.
  - MGR: partial. A coach acts as supervisor, but whether it is a feedback-driven state machine or a fixed
    relocation or elitism rule is **not confirmed**.
- **No counterpart in FGA.** FORM, ROT, PRESS, CTR, SET, OFF, VAR, FAT, SUB, and the archetypes.
- **Verdict:** partial overlap (BALL, MGR). Needs scrutiny: confirm the coach and ball-holder rules from the
  full text.

### 2.9 Tiki-taka Algorithm (TTA)

- **Reference.** Ab. Rashid, M.F.F. (2021). Tiki-taka algorithm: a novel metaheuristic inspired by football
  playing style. *Engineering Computations* 38(1), 313–343. doi:10.1108/EC-03-2020-0137. Published online
  in 2020 and in print in 2021 (Crossref 47; Consensus 39). · Multi-objective variant: Ab. Rashid & Ramli
  (2023), *Engineering Computations* 40(3), 564–593. doi:10.1108/EC-03-2022-0185.
- **Metaphor.** The tiki-taka style of play: short passing, positioning and possession.
- **Mechanism** (abstract and secondary snippets). The algorithm keeps a **ball-position matrix B that is
  separate from player positions**. The ball is passed by *short passing to a nearby player*, and there is a
  **probability of losing the ball** (reported as "between 10%–…"; the upper bound was cut off). Players
  update their positions relative to the ball and to **several randomly selected key players (leaders)**.
  The abstract names "the short passing strategy that exploits a nearby player to move to a better
  position" as the main contribution.
- **Overlap with TFO. This is the closest prior art to TFO's BALL mechanism.** TTA already has a ball state
  distinct from the incumbent, moved by short passes between nearby players, with a turnover possibility.
  `mechanism-map.md` even labels TFO's possession row "(tiki-taka)". The differences that **can be defended**
  are all at the mechanism level:
  1. **Acceptance rule.** TFO keeps a pass only if fitness does not regress by more than τ (threshold
     accepting, Dueck & Scheuer 1990). τ is under the manager's control, and τ = 0 gives non-regression with
     neutral drift. TTA's loss is a fixed random probability that does not depend on fitness.
  2. **Pass geometry.** TFO passes run along the edges of an explicit formation lattice whose shape is
     itself a control variable (FORM). In TTA "nearby" means index adjacency or distance, and that has to be
     confirmed from the full text.
  3. **Number of balls.** TFO has *one* focal point for the whole squad. TTA's B appears to be a matrix, which
     suggests one ball coordinate per player. That also needs the full text.
  4. **Turnover semantics.** In TFO a change of possession is an *event triggered by where improvement
     occurs*: an off-ball agent finds a materially better point far from the ball, and a counter-attack burst
     follows (CTR). In TTA the loss is random.
- **Other overlaps.** TTA's multiple random key players are only weakly related to FIN's restarts from the
  Sweeper-Keeper archive.
- **No counterpart in TTA.** FORM, ROT, PRESS, CTR as an event, SET, OFF, VAR, FAT, SUB, MGR, and all
  archetype operators except weak relations noted above.
- **Verdict:** needs scrutiny on BALL; distinct elsewhere. The manuscript **must** cite TTA in the
  possession row and give the four differences above. It is also worth considering dropping the
  "(tiki-taka)" gloss from the row label, or keeping it deliberately and addressing TTA head-on.

### 2.10 Modernized Tiki-taka Algorithm (MTTA)

- **Reference.** Song, X., & Zhao, J. (2026). MTTA: Modernized Tiki-Taka Algorithm with role specialization
  for solving engineering application problems and feature selection. *Mathematics* 14(11), 1900.
  doi:10.3390/math14111900 (Crossref 0). The author list comes from Crossref. Consensus shows "Xiang-Kun Song
  et al."
- **Metaphor.** Tiki-taka with modern positional roles.
- **Mechanism** (abstract). TTA plus Logistic–Tent chaotic initialisation plus a **fitness-based three-role
  mechanism** (forwards, midfielders, defenders), each role with its own update rule, which gives an
  "adaptive balance" between exploration and exploitation over the run.
- **Overlap with TFO. Needs scrutiny.**
  - Archetypes: partial. MTTA also has heterogeneous role-specific update rules. TFO has eight archetypes
    rather than three, and each maps to a *different named operator family* (elitist archive, stratified
    sampling, quasi-opposition, niching, BLX-α, local DE, pattern search, Lévy flight). MTTA's three rules are
    presumably variants of one family, but that needs the full text.
  - ROT: partial. MTTA assigns roles *by fitness*. TFO also reassigns roles by rank. The defensible difference
    is the same one `mechanism-map.md` records against CA: TFO uses **local pairwise swaps between formation
    neighbours at fixture boundaries, so the archetype follows the lattice slot**, not a global re-ranking.
    It has not been confirmed whether MTTA re-ranks every iteration.
  - BALL: inherited from TTA (see §2.9).
- **No counterpart in MTTA.** FORM, PRESS, CTR, SET, OFF, VAR, FAT, SUB, MGR.
- **Verdict:** partial overlap (archetypes, ROT). Needs scrutiny.

### 2.11 Football Team Training Algorithm (FTTA) and variants

- **References.** Tian, Z., & Gai, M. (2024). Football team training algorithm: A novel sport-inspired
  meta-heuristic optimization algorithm for global optimization. *Expert Systems with Applications* 245,
  123088. doi:10.1016/j.eswa.2023.123088 (Crossref 161; Consensus 145). The author names come from Crossref.
  Consensus shows "Zhi-Gang Tian et al.", which is a metadata conflict. · Variants: Hou, Cui, Rong & Jin
  (2024), IFTTA, *Biomimetics* 9(7), 419, doi:10.3390/biomimetics9070419. · Sun et al. (2025), MIFTTA,
  *Concurrency and Computation: Practice and Experience* 37(23–24), e70282, doi:10.1002/cpe.70282. · Peng et
  al. (2024), chaotic-map FTTA, RICAI 2024 (seen in Consensus, not Crossref-verified).
- **Metaphor.** A training session rather than a match: collective training, then group training, then
  individual extra training.
- **Mechanism** (abstract and secondary descriptions in IFTTA and MIFTTA).
  - *Collective training.* In each iteration every agent **randomly chooses one of four behaviour types**.
    Followers move toward the best agent. Thinkers learn from the best-minus-worst gap. Volatiles fluctuate
    independently. The fourth type is discoverers.
  - *Group training.* An "adaptive cluster grouping mechanism" (MIFTTA's words) partitions agents into groups
    that learn within the group.
  - *Individual extra training.* Intensification around the best agent.
  - IFTTA's authors criticise FTTA for "referring too much to the optimal individual." FTTA is
    incumbent-centric.
- **Overlap with TFO.**
  - Archetypes: partial. FTTA has heterogeneous behaviours, but the type is **drawn at random each
    iteration**. In TFO an archetype is *bound to a lattice slot* and changes only through ROT.
  - FORM, B2B: partial. FTTA's clustered group training is a population partition used for local learning.
    Unlike TFO's formation, the clusters are recomputed from the data and are not a controlled lattice whose
    shape carries a takeover-time prediction.
  - SET: partial. Both have a stage of intensification around the incumbent. TFO's set pieces are
    *fixed-schedule, scripted, never-adapted* designs (an orthogonal-array corner and a parabolic-interpolation
    free kick). FTTA's extra-training update form was not confirmed.
- **No counterpart in FTTA.** BALL, PRESS, CTR, OFF, VAR, FAT, SUB, MGR as a state machine, and ZCB, OWB, DES,
  VIR, FIN as distinct operator families.
- **Verdict:** partial overlap (role heterogeneity, incumbent intensification); distinct on structure. FTTA
  is the most-cited football method (161 Crossref citations) and is the natural **empirical** football-family
  baseline. Adding it to the comparator roster is worth considering, since it tests the claim directly.

### 2.12 Football Optimization Algorithm (FbOA)

- **Reference.** El-Kenawy, E.-S.M., Ibrahim, A., et al. (2024). Football Optimization Algorithm (FbOA): A
  novel metaheuristic inspired by team strategy dynamics. *Journal of Artificial Intelligence and
  Metaheuristics* 8(1), 21–38. doi:10.54216/JAIM.080103 (Crossref 87; Consensus 86). Crossref's author list for
  this DOI is malformed: affiliations are deposited as authors, and only El-Sayed M. El-Kenawy and Abdelhameed
  Ibrahim can be identified. The complete author list has to be taken from the PDF.
- **Metaphor.** Team strategy in match play.
- **Mechanism** (abstract only; nothing beyond it could be retrieved). "Tactical positioning and movement,
  incorporating **short passes, long passes, and positional adjustments**." Evaluated on CEC 2005 at 30 and
  100 dimensions.
- **Overlap with TFO. Needs scrutiny.**
  - REG: partial at the metaphor level. FbOA's *long pass* may resemble TFO's Regista long diagonal (BLX-α
    with the partner at maximum graph distance). The distinction TFO can defend is that the "long" in REG is
    *graph* distance on the formation lattice, a small-world long-range link, not a large step length.
  - BALL: partial at the metaphor level. FbOA's *short pass* may resemble TFO's possession drift. The update
    equations are unknown.
- **No counterpart in FbOA** (from the abstract). FORM, ROT, PRESS, CTR, SET, OFF, VAR, FAT, SUB, MGR.
- **Verdict:** needs scrutiny, because the mechanism is unknown. FbOA also nearly shares TFO's name (see
  `spec.md` Assumptions → Name).

### 2.13 Soccer Match Algorithm (SMA)

- **Reference.** Ben Ammar, R., Gharbi, A., & Babai, M.Z. (2024). Soccer Match Algorithm for global
  optimization: A contender metaheuristic. *IEEE Access* 12, 93924–93945. doi:10.1109/ACCESS.2024.3424791
  (Crossref 7; Consensus 5).
- **Metaphor.** A full soccer match: "tactical roles, compositions, playing styles, and player interactions."
- **Mechanism** (abstract only). The algorithm integrates "an unprecedented array of soccer concepts" together
  with an **adaptive learning framework for dynamic parameter adjustment based on ongoing performance
  feedback**, and includes "**tactical shifts during a game**." It is benchmarked against HHO and TTA.
- **Overlap with TFO. The highest-priority full-text check in this review.**
  - MGR: potentially close. SMA's performance-feedback parameter adaptation plus in-game tactical shifts is,
    on its face, the same *idea* as TFO's manager state machine: feedback-driven adaptive parameter control
    (Eiben et al. 1999) that switches between tactical states.
  - FORM: unknown. If SMA's "compositions" change who interacts with whom, TFO's formation-as-topology claim
    is weakened. If "composition" only means role counts, the claim holds.
  - Archetypes and ROT: probably partial ("tactical roles").
  - TFO's defensible difference, pending the full text: TFO's manager also **switches the interaction
    topology** (the formation's shape) and the pressing radius ρ, the acceptance threshold τ and the
    pass-chain length. It is driven by diversity, possession rate, goal drought and the match clock. Its
    contribution is isolated by the pre-registered TFO vs TFO-static ablation (H2).
- **No counterpart in SMA** (from the abstract). OFF (the moving ε-line), VAR (deferred audit with rollback),
  SET as a fixed-schedule scripted design, FAT. These are unconfirmed but unlikely, since none is mentioned in
  an abstract that stresses breadth of concepts.
- **Verdict:** needs scrutiny (MGR, possibly FORM). SMA should be read before the manuscript's novelty
  paragraph is written.

### 2.14 Adjacent: Stadium Spectators Optimizer (SSO)

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
| Most Valuable Player Algorithm (MVPA) | Bouchekara (2020), *Operational Research* 20(1), 139–195, doi:10.1007/s12351-017-0320-y (online 2017) | Players form teams and compete both as teams and individually for MVP | League-type. No overlap |
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
not a sports metaphor and does not roll back accepted moves.

---

## 4. Synthesis table

| Algorithm | Year | What it models | Closest TFO mechanism(s) | Verdict |
|---|---|---|---|---|
| LCA / PLCA | 2009/2014 (PLCA 2019) | League fixtures between individual "teams". "Formation" means the solution vector | none. League clock ≈ fixture clock only | **Distinct** (terminology note on "formation") |
| SLC | 2014 | Multi-team league. Fixed players vs substitutes. Imitation, provocation, mutation | SUB (vocabulary), ROT (global rank reallocation) | **Distinct** |
| SLO | 2014 (arXiv) | Rich/regular/poor tiers, transfers, youth discovery | SUB (random immigrants) | **Distinct** |
| SLOCA | 2022 | Qualifying and main competitions, **fatigue factor**, **reserve players** | **FAT, SUB** | **Partial overlap: needs scrutiny** |
| Golden Ball | 2013/2014 | Multi-population league for combinatorial problems. Captains, training, transfers | MGR (weak, unconfirmed) | **Distinct** (different problem class) |
| WCO | 2016 | Continental tournament with play-off | none | **Distinct** |
| SGO (+SGOLS) | 2013/2015 (2020) | Ball dribbler = best-so-far. Move forward/move off. Substitute elite pool. Nearby-player info | BALL (but ball = incumbent), SK, B2B (local info) | **Partial overlap** |
| FGA / IFGO | 2016 (2020) | Random walk + move toward ball-holder, coach supervisor | BALL, MGR (both unconfirmed) | **Partial overlap: needs scrutiny** |
| **TTA** | 2020/2021 | Separate ball matrix, short passes to nearby player, random ball loss, multiple key players | **BALL** (closest prior art) | **Needs scrutiny** (defensible on acceptance rule, graph passing, single ball, event turnovers) |
| MTTA | 2026 | TTA + fitness-based forward/midfielder/defender roles | Archetypes, ROT, BALL | **Partial overlap: needs scrutiny** |
| FTTA (+IFTTA, MIFTTA) | 2024 (2024, 2025) | Training session. Random per-iteration behaviour types, cluster groups, extra training of best | Archetypes, FORM/B2B (clusters), SET | **Partial overlap**. Distinct on structure |
| FbOA | 2024 | Short passes, long passes, positional adjustment | REG (long pass), BALL (short pass) | **Needs scrutiny** (mechanism unknown) |
| **SMA** | 2024 | Roles, compositions, playing styles, **performance-feedback adaptive parameters, in-game tactical shifts** | **MGR**, possibly FORM, archetypes | **Needs scrutiny** (highest priority) |
| SSO | 2024 | Spectator influence on players | none | **Distinct** |

**Coverage across TFO's 19 mechanisms.** No football-inspired method found in this pass has a counterpart for
**OFF** (bound repair plus the moving ε-constrained line), **VAR** (deferred tabu audit with rollback and an
aspiration clause), **PRESS** (distance-gated encircling around the ball), **SET** as fixed-schedule scripted
orthogonal-array or parabolic designs, **FORM** as a controlled lattice topology (subject to the SMA check),
or the archetype operator families **ZCB** (stratified sampling), **OWB** (quasi-opposition), **DES**
(clearing niching), **VIR** (pattern search) and **FIN** (Lévy flight with elite restart).

Partial overlaps exist for the following, and each needs a stated, mechanism-level difference in the paper:

- **BALL:** TTA, SGO, FGA, FbOA
- **ROT and archetype heterogeneity:** MTTA, FTTA, SMA, SLC
- **SUB:** SLOCA, SLC, SLO, SGO
- **FAT:** SLOCA
- **MGR:** SMA, FGA
- **REG:** FbOA
- **SK:** SGO
- **CTR:** only BTOA's basketball "fast break", which is outside the football family

---

## 5. Positioning statement (the panel's judgement)

> Football is the most heavily mined sports metaphor in metaheuristics. At least twelve football- or
> soccer-specific optimizers have appeared between 2013 and 2026, following the generic League
> Championship Algorithm of 2009. Together they have already used league
> competition, a ball or ball-carrier attractor, short and long passes, role specialisation, substitutes,
> fatigue and coach-driven tactical shifts. TFO therefore claims none of these football *concepts* as new.
> Every TFO operator is presented as an instance of a named, metaphor-free operator family. What TFO
> contributes is a *structural* composition that none of these methods has. First, the population interacts
> only along the edges of an explicit lattice whose shape is a controlled variable, and that gives a
> falsifiable takeover-time prediction (H3). Second, a single focal point, distinct from the incumbent, is
> moved along those edges and retained by threshold acceptance, rather than lost at random as in the
> Tiki-taka Algorithm or equated with the incumbent as in Soccer Game Optimization. Third, turnovers and
> counter-attacks are events triggered by where improvement occurs, not phases read off a clock. Fourth, two
> mechanisms have no counterpart anywhere in this family: a deferred VAR audit that can roll back moves
> already accepted, and a moving offside ε-feasibility line. The value of the adaptive manager is not
> asserted from the metaphor (the Soccer Match Algorithm already adapts parameters from performance
> feedback). It is measured by a pre-registered ablation against TFO-static (H2).

The panel judges this claim defensible **provided that** the full texts of SMA, TTA, FbOA and SLOCA are read
before submission and confirm the mechanism descriptions in §2. If SMA's "compositions" turn out to reshape
the interaction structure, the formation claim must be narrowed to "a lattice topology whose *shape* is
controlled and tied to a takeover-time prediction" and must drop any implication that no football method
varies who interacts with whom.

---

## 6. Verification notes (manual checks required before citing)

1. **Full texts were not read for any football-inspired method.** Every publisher host (IEEE Xplore,
   ScienceDirect, Nature, MDPI, PMC, Semantic Scholar and OpenAlex APIs, ResearchGate mirrors) was blocked by
   the session's egress proxy. The mechanism descriptions above come from abstracts, from secondary
   descriptions in variant papers (IFTTA and MIFTTA for FTTA; SGOLS for SGO) and from search snippets.
   **Priority order for manual reading: SMA → TTA → FbOA → SLOCA → FGA → MTTA → FTTA.**
2. **SMA:** whether "compositions" change the interaction structure, and what the adaptive framework adapts
   and on what signal.
3. **TTA:** whether B holds one ball per player or a single ball; whether "nearby player" means index-adjacent
   (a ring) or distance-based; the exact loss probability range; how key players are selected.
4. **FbOA:** the update equations for the short pass, long pass and positional adjustment. Also the full
   author list, because Crossref's deposit lists affiliations as authors.
5. **SLOCA:** what the fatigue factor scales and what clock drives it; how reserve players are triggered. **No
   Crossref DOI.** The venue (*Advances in Computational Design* 7(4):297, Techno-Press) comes from web
   snippets only, and the end page is unknown.
6. **FGA:** whether the ball-holder is the current best, and what the coach operator does.
7. **Golden Ball:** whether coaches change the training operator when performance is poor (the "coach" rule
   was not seen in any retrieved text).
8. **Author metadata conflicts.** For FTTA, Crossref gives *Zhirui Tian & Mei Gai* and Consensus gives
   "Zhi-Gang Tian et al." Use Crossref, but confirm on the PDF. For MTTA, Crossref gives *Xiangkun Song & Jian
   Zhao*.
9. **Citation counts differ by source and change over time.** Values here are from 2026-09-24. `spec.md`
   previously gave FTTA "~145" (the Consensus figure); Crossref shows 161. FbOA is 86 (Consensus) or 87
   (Crossref). Cite counts sparingly, if at all, and re-pull them at submission.
10. **Online versus print years.** TTA: online 2020, print 2021 (vol. 38(1)). Alatas: online 2017, print 2019
    (*AIR* 52(3):1579–1627, doi:10.1007/s10462-017-9587-x). MVPA: online 2017, print 2020. RCGO: online
    2022, print 2023. Follow the target journal's style.
11. **Not Crossref-verified:** TWO's venue and pages; the Squid Game Optimizer DOI; the SGOLS DOI (taken from a
    URL); the chaotic-map FTTA conference paper; SLO (arXiv:1406.4462, no DOI).
12. **Acronym collisions to footnote in the manuscript:** "SGO" is both Soccer Game Optimization and Squid
    Game Optimizer. "SSO" is the Stadium Spectators Optimizer here, and other methods also use SSO. "SMA" is
    widely used for another metaheuristic as well, but that was not checked in this pass.
13. **Search budget.** The Consensus monthly quota was exhausted during this pass (it resets 2026-10-01). A
    follow-up sweep for 2026 football variants published after mid-2026 is advisable closer to submission.
14. **Reviews to cite for the landscape:** Alatas (2019), doi:10.1007/s10462-017-9587-x (Crossref 39;
    Consensus 47). Osaba & Yang (2021), *Springer Tracts in Nature-Inspired Computing*, 81–102,
    doi:10.1007/978-981-16-0662-5_5.
