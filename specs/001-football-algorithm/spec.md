# Feature Specification: Total Football Optimizer (TFO), Mechanism Design and Evaluation Programme

**Feature Branch**: `001-football-algorithm`

**Created**: 2026-09-24

**Status**: Draft

**Input**: User description: "Design 'The Football Algorithm (FA)', a new population-based
metaheuristic inspired by association-football tactics, with the same discipline as the sibling
Chess Algorithm (CA): every football-flavoured mechanism explicitly mapped to an established
operator family; anonymized player archetypes inspired by famous playing styles but never named
after real people; team-level tactics (formation as interaction topology, pressing, possession,
counter-attacks, set pieces, offside line, substitutions, fatigue, VAR review); an adaptive control
layer plus a static ablation twin carried through every experiment; and a benchmark programme
mirroring CA's rigor (full CEC-2017, validated CEC-2022, classic constrained engineering design,
classical and competition-grade baselines, granular ablation, parameter sensitivity, benchmark
data-integrity audits, honest reporting of losses). No application case study."

**Reading this spec as a research artifact.** Spec Kit's software vocabulary is reinterpreted as
follows. *Users* are the paper's readers, reviewers, and future adopters of the algorithm. *User
stories* are the ways a researcher evaluates, verifies, or adopts TFO. *Functional requirements*
are what each mechanism, the adaptive layer, and the evaluation programme must do; each is stated
so that it can be checked. *Success criteria* are measurable research outcomes: rigor criteria that
must be met, and pre-registered hypotheses whose outcome must be reported whichever way it falls.
The full mechanism-to-operator-family table is in [mechanism-map.md](./mechanism-map.md).

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A reviewer audits the metaphor (Priority: P1)

A reviewer who knows the "metaphor exposed" critique opens the paper expecting a sports reskin of
known operators. They look for one table that names, for every football term, the underlying
operator and its literature family, and for a metaphor-free description from which the algorithm
could be re-implemented. They then check whether any mechanism is claimed as novel purely because
of its name.

**Why this priority**: if this audit fails, nothing else in the paper is read charitably. It is the
precondition for every other story, and it is the part of the contribution that exists before any
experiment is run.

**Independent Test**: give only the mechanism map and the metaphor-free algorithm description to a
reader unfamiliar with football. They can state each mechanism's operator family and cite its
canonical source, and can re-implement the algorithm without consulting any football term.

**Acceptance Scenarios**:

1. **Given** the mechanism map, **When** the reviewer checks each of the 19 mechanisms, **Then**
   every one has a named operator family and at least one canonical citation, and none is unmapped.
2. **Given** the metaphor-free description, **When** every football word is deleted from it,
   **Then** the algorithm remains fully specified.
3. **Given** the overlap audit against CA, **When** the reviewer asks "is this CA again?", **Then**
   each shared family is declared with its stated difference, and the count of TFO mechanisms in
   families absent from CA is reported.
4. **Given** the archetype roster, **When** the reviewer searches the formal terminology for real
   people's names, **Then** there are none, and each homage appears as at most one explanatory
   sentence.

---

### User Story 2 - A researcher positions TFO against strong baselines (Priority: P2)

A researcher choosing an optimizer wants to know where TFO stands: against classical methods (GWO,
PSO, GA, WOA), against its own static twin, and against competition-grade adaptive optimizers
(L-SHADE, CMA-ES), on complete validated suites, with every loss visible.

**Why this priority**: the standing claim is the paper's headline result, and it is only credible if
losses are reported with the same prominence as wins.

**Independent Test**: from the committed per-run results alone, recompute the Friedman mean ranks
and the per-function win/tie/loss records for every pair of algorithms on each suite, and confirm
that they match the manuscript's tables.

**Acceptance Scenarios**:

1. **Given** the full usable CEC-2017 suite at D = 30, **When** all nine algorithms (TFO, TFO-static,
   GWO, PSO, GA, WOA, L-SHADE, CMA-ES, and CA as sibling reference) are run under identical
   evaluation budgets, **Then** mean Friedman ranks and pairwise corrected Wilcoxon win/tie/loss
   records are reported for all 29 functions.
2. **Given** the CEC-2022 suite at D ∈ {10, 20}, **When** only audit-validated cells are analysed,
   **Then** the same statistics are reported, and the excluded cells are listed with their evidence.
3. **Given** the classic constrained engineering design problems, **When** the same roster is run,
   **Then** best, mean, and standard deviation per problem and the pairwise records are reported.
4. **Given** that TFO loses to L-SHADE or CMA-ES on a function, **When** the results are presented,
   **Then** the loss appears in the main-text table and is discussed rather than relegated to an
   appendix.

---

### User Story 3 - A methods researcher attributes performance to mechanisms (Priority: P3)

A researcher who studies algorithm design wants to know which of TFO's mechanisms actually carry
its performance, whether the adaptive layer earns its complexity, and whether the formation
topology does what cellular-EA theory predicts.

**Why this priority**: the ablation turns a list of named mechanisms into a mechanistic explanation
of the standing result, and it decides which mechanisms survive into the published algorithm.

**Independent Test**: run the single-mechanism-off variants, the group-level ablations, and TFO-static
on the ablation problem set, and check whether the reported error ratios and significance counts
identify which mechanisms are load-bearing.

**Acceptance Scenarios**:

1. **Given** each switchable mechanism, **When** it alone is disabled, **Then** the mean final-error
   ratio against full TFO and the count of problems with a significant difference are reported.
2. **Given** the group-level variants (no adaptive layer = TFO-static; fully connected population
   instead of a formation; one homogeneous archetype instead of eight), **When** they are run,
   **Then** their joint contribution is reported next to the single-mechanism results.
3. **Given** two fixed formations, compact and stretched, **When** the algorithm runs with selection
   only, **Then** the measured takeover time and diversity decay differ in the direction that
   structured-population theory predicts.
4. **Given** a mechanism with negligible measured contribution, **When** the paper is finalised,
   **Then** it is either removed or kept with an explicit written justification.

---

### User Story 4 - An independent group reproduces and trusts the numbers (Priority: P4)

A third party clones the repository and wants to regenerate every table and figure, confirm that
no algorithm had an evaluation-budget advantage, and confirm that no reported result rests on a
defective benchmark function.

**Why this priority**: reproducibility and integrity are what let the other stories be believed
without trusting the authors, but they depend on the experiments existing first.

**Independent Test**: follow the documented reproduction sequence on a clean machine and compare
the regenerated tables with the committed ones; inspect the audit records for each benchmark cell.

**Acceptance Scenarios**:

1. **Given** the committed seeds and code, **When** the documented sequence is run, **Then** every
   reported mean, standard deviation, rank, and test outcome is regenerated identically.
2. **Given** the exact evaluation counts, **When** they are inspected, **Then** no algorithm exceeds
   the shared budget in any run, and TFO's internal allocation of evaluations per mechanism is
   reported.
3. **Given** a benchmark cell that failed the optimum audit, **When** the records are inspected,
   **Then** its cross-validation outcome (restored or excluded) and its pre-audit numbers are on
   record.

---

### User Story 5 - A practitioner adopts TFO with default settings (Priority: P5)

An engineer with a bound- or inequality-constrained continuous design problem wants to use TFO
without tuning, and wants to know which settings actually matter.

**Why this priority**: adoption value is real but secondary to the paper's scientific claims; it is
served by the sensitivity study and the constrained benchmarks rather than by new experiments.

**Independent Test**: read the parameter-sensitivity results and check that they name the settings
that matter, the settings that can be left at their defaults, and the direction of any headroom.

**Acceptance Scenarios**:

1. **Given** the one-at-a-time sensitivity sweep, **When** a practitioner reads it, **Then** every
   parameter group is classified as sensitive or robust, with the ratio and significance evidence.
2. **Given** a constrained problem that exposes its constraint values, **When** TFO runs with the
   offside ε-line enabled, **Then** its effect relative to the shared penalty formulation is
   reported in a separate, clearly labelled experiment.

---

### Edge Cases

- **Premature collapse early in the run**: the population contracts to a tiny radius while much of
  the budget remains. The manager must read this as a need to reopen play (stretched formation,
  pressing off), never as a cue for final exploitation. This is the CA "closed position" lesson.
- **Possession loops on a plateau**: with τ = 0, neutral passes can cycle indefinitely on flat
  regions. The number of consecutive neutral passes must be capped so that a plateau cannot absorb
  the budget.
- **Everyone presses**: if most of the squad falls inside the pressing radius, the formation
  dissolves. The pressing fraction must be capped (default: at most half of the outfield agents).
- **Substitution cap exhausted while stagnating**: substitutions stop at the per-fixture cap, and
  only the Chasing-the-Game state may raise it, within a documented limit.
- **VAR overturns the move that found the global best**: the aspiration rule must keep any move that
  produced a new best-so-far, so the incumbent is never lost.
- **Optimum on or near a bound**: the offside repair must still let an agent reach any feasible
  point arbitrarily close to the bound. Engineering optima often lie on constraint boundaries.
- **Controller oscillation**: statistics hovering at a threshold must not flip the tactical state
  every iteration. A minimum dwell time or hysteresis is required.
- **Budget exhausted mid-routine**: a counter-attack burst, a set piece, or a pass chain that would
  exceed the evaluation budget must be truncated exactly at the budget, never overrun.
- **Population size that does not factor into a lattice shape**: every formation must be defined for
  the chosen population size, with a documented rule for any unused slots.
- **A benchmark whose claimed optimum is wrong** (evaluating at it does not return the claimed
  value, or a run beats it): the cell is dispositioned under the integrity audit before any analysis.
- **A non-discriminative benchmark cell** (all algorithms indistinguishable): identified by a rule
  fixed before the results are seen, not excluded by judgement afterwards.
- **Ties in paired tests** (identical final values, for example at an attained optimum): the tie
  handling of the signed-rank test must be stated and applied uniformly.

## Requirements *(mandatory)*

### Functional Requirements

**A. Core architecture**

- **FR-001**: TFO MUST maintain a population (the squad) of candidate solutions in a bounded
  continuous search space. It consists of one Sweeper-Keeper agent plus outfield agents placed on a
  lines × lanes pitch lattice, and each agent carries exactly one archetype.
- **FR-002**: Each outfield agent MUST interact (select partners, donors, or neighbourhood bests)
  only with its von Neumann neighbours on the current formation lattice. The only exceptions are
  those declared in FR-008 (Regista long-range link), FR-015 (pressing), and FR-017 (set pieces
  acting on the incumbent).
- **FR-003**: TFO MUST maintain a *ball*, a focal point distinct from the best-so-far solution,
  which the possession, pressing, counter-attack, and Finisher mechanisms act on.
- **FR-004**: TFO MUST terminate on an exact maximum number of objective evaluations. Every internal
  probe (passes, set pieces, bursts, pattern polls, opposition points) MUST be charged to that one
  budget.

**B. Player archetypes** (each MUST be individually switchable; a disabled archetype falls back to
a documented neutral move)

- **FR-005 Sweeper-Keeper**: MUST keep a bounded, distance-diverse archive of best-so-far solutions
  and MUST never lose the incumbent best. It MUST supply the ball reset point after possession is
  lost and the restart points for the Finisher.
- **FR-006 Zonal Centre-Back**: MUST explore only inside its assigned stratum of a partition of the
  search box. The partition MUST be redrawn at each fixture boundary so that the zonal agents
  jointly stratify the box.
- **FR-007 Overlapping Wing-Back**: MUST, at a set jumping rate, evaluate the quasi-opposite of its
  position about the squad centroid and keep the better of the two.
- **FR-008 Regista**: MUST recombine with a partner chosen at maximal (or near-maximal) graph
  distance on the formation, using a blend crossover whose extent is set by a single parameter.
- **FR-009 Box-to-Box Engine**: MUST move by a differential step built from its neighbourhood best
  and a difference vector between a defensive-line and an attacking-line member of its
  neighbourhood.
- **FR-010 Destroyer**: MUST detect pairs of agents closer than a niche radius. The worse agent of
  each pair MUST be relocated out of the niche by a differential kick, and the better agent is kept.
- **FR-011 Virtuoso**: MUST perform a coordinate-wise pattern poll with a small mesh: first
  improvement accepted, mesh expanded after success and contracted after failure, with the mesh
  kept per agent.
- **FR-012 Finisher**: MUST make heavy-tailed (Lévy-distributed) jumps around the ball. After a set
  number of consecutive failures it MUST restart from an archive elite different from its last
  restart point.

**C. Team-level tactics** (each MUST be individually switchable to a documented neutral default:
plain clipping for the offside line, fully connected interaction for the formation, no rollback
for VAR, and so on; disabling the Sweeper-Keeper archetype reduces its archive to the single
incumbent)

- **FR-013 Formation**: TFO MUST support at least three lattice shapes for the same population
  (compact, balanced, stretched), which differ in their ratio of neighbourhood radius to grid
  radius. Changing formation MUST re-lay agents without changing their positions or fitness.
- **FR-014 Possession**: each iteration MUST run a chain of short passes that move the ball toward
  formation neighbours of its current carrier. A pass MUST be retained only if the new ball fitness
  is no worse than the old plus a threshold τ ≥ 0, and the fraction of retained passes MUST be
  tracked as the possession rate.
- **FR-015 Pressing**: agents within distance ρ of the ball MUST replace their archetype move with
  a shrinking-encircling step toward the ball. The fraction of pressing agents MUST be capped.
- **FR-016 Counter-attack**: a turnover event MUST be declared when an off-ball agent finds a point
  that is materially better than the ball and farther than a transition distance from it. The ball
  MUST then relocate to that point, and the attacking-line agents MUST perform a bounded-length
  burst of large steps around it whose step size decays geometrically. The trigger MUST be
  event-based in both TFO and TFO-static.
- **FR-017 Set pieces**: every *c* iterations, on a fixed schedule identical in TFO and TFO-static,
  the incumbent MUST run one routine from a fixed rehearsed script: a corner (orthogonal-array
  probe on a random coordinate pair) or a free kick (three-point parabolic line search along a
  random direction). The routine choice MUST follow a fixed rotation and MUST NOT be adapted.
- **FR-018 Offside line**: any coordinate outside the search box MUST be repaired to a point between
  the agent's previous position and the violated bound. When a problem exposes constraint values,
  an ε-level feasibility ranking MUST be available whose ε decreases to zero by a set fraction of
  the budget.
- **FR-019 Substitutions**: an agent whose personal best has not improved for *W* iterations and
  whose stamina is below a threshold MUST be replaced by a fresh uniformly random agent, at most a
  capped number per fixture. The outgoing position MUST be added to the VAR tabu register.
- **FR-020 Fatigue**: each agent MUST carry a stamina value that scales its step sizes, drains in
  proportion to the distance it moves, and partially recovers at fixture boundaries. The recovery
  amount MUST decrease over the run, and substitutes MUST enter with full stamina.
- **FR-021 VAR review**: every *v* iterations, every move accepted since the previous review MUST be
  audited against global checks: the endpoint lies inside a tabu zone; the endpoint duplicates
  another agent's position within a collision radius; or, when constraints are exposed, the
  endpoint is truly infeasible although the start was feasible. Failing moves MUST be rolled back
  to the agent's position and fitness at the previous review, at zero evaluation cost, except that
  any move that produced a new best-so-far MUST stand (aspiration).
- **FR-022 Positional rotation**: at fixture boundaries, an agent in a deeper line that is better
  than its upfield neighbour MUST swap slots, and therefore archetypes, with that neighbour.

**D. Adaptive control layer and ablation twin**

- **FR-023**: TFO MUST include a manager state machine that reads, every iteration, smoothed
  population diversity, the possession rate, a goal-drought counter, and the fraction of budget
  elapsed. The goal-drought counter resets only on a materially significant improvement of the
  best-so-far, never on microscopic refinements.
- **FR-024**: The manager MUST select one of four tactical states: Build-up, Control, High Press, and
  Chasing the Game. Each state MUST set the formation, pressing radius ρ, retention threshold τ,
  pass-chain length, and archetype rate multipliers. Chasing the Game (goal drought over threshold)
  MUST respond with diversification (stretched formation, pressing off, raised switch-of-play and
  long-ball rates, emergency substitutions within a documented limit).
- **FR-025**: State transitions MUST use hysteresis or a minimum dwell time, so that the state cannot
  change on consecutive iterations because of noise alone.
- **FR-026**: TFO-static MUST be the identical operator set with the manager disabled. The balanced
  formation, ρ, τ, pass-chain length, and rates are frozen at their defaults, and the Chasing-the-Game
  response is absent. Event-triggered mechanisms (counter-attack, substitution, pressing membership)
  and fixed-schedule mechanisms (set pieces, VAR) MUST behave identically in both configurations.
- **FR-027**: The per-iteration tactical state and the evaluations spent per mechanism MUST be
  recorded for every run, so that controller behaviour can be reported.

**E. Evaluation programme**

- **FR-028**: The roster MUST be TFO, TFO-static, GWO, PSO, GA, WOA, L-SHADE, and CMA-ES. The sibling CA
  SHOULD be included as a reference comparator so that the "not a reskin" claim is also tested
  empirically.
- **FR-029**: The programme MUST run the full usable CEC-2017 suite (29 functions) at D = 30, the
  CEC-2022 suite at D ∈ {10, 20} restricted to audit-validated cells, and the seven classic
  constrained engineering design problems (welded beam, tension/compression spring, pressure
  vessel, speed reducer, three-bar truss, gear train, cantilever beam).
- **FR-030**: Every algorithm MUST receive the identical maximum number of evaluations per cell,
  fixed before any run, and at least 30 independent seeded runs per algorithm per cell.
- **FR-031**: The engineering problems MUST be presented to every roster algorithm in one shared
  formulation (information parity). The offside ε-line on raw constraint values MUST be evaluated
  only in a separate, labelled experiment.
- **FR-032**: Statistics MUST include mean Friedman ranks per suite and pairwise Wilcoxon signed-rank
  tests at α = 0.05 with a stated multiple-comparison correction, reported as complete win/tie/loss
  records.
- **FR-033**: Expected wins and expected losses MUST be written down and committed before any
  test-suite run (see Assumptions, pre-registered hypotheses H1 to H5).

**F. Ablation, sensitivity, and cost**

- **FR-034**: The ablation MUST disable each switchable mechanism one at a time (all 8 archetypes and
  all 10 switchable team-level tactics, at least 18 variants). It MUST also run the group-level
  variants TFO-static, fully connected population (no formation), and single homogeneous archetype,
  on at least six problems spanning the CEC-2017 function classes and the engineering suite, with
  30 runs each.
- **FR-035**: A mechanism-level validation MUST show that compact and stretched formations produce
  measurably different takeover times and diversity decay under selection-only dynamics.
- **FR-036**: A one-at-a-time sensitivity sweep MUST perturb every parameter group low and high:
  archetype fractions, ρ, τ, pass-chain length, set-piece period, VAR period, substitution window
  and cap, fatigue rates, and the manager's thresholds. The two most sensitive parameters SHOULD
  also receive a two-factor interaction check.
- **FR-037**: Evaluation counts MUST be exact, from a wrapper that intercepts every objective call.
  Wall-clock time MUST be measured over repeated runs on an otherwise idle machine, for every roster
  algorithm on a representative subset of problems.

**G. Integrity and reproducibility**

- **FR-038**: Every benchmark cell MUST pass the optimum audit (evaluation at the claimed optimum
  returns the claimed value; no run beats it) before its results are analysed. Failing cells MUST be
  cross-validated against an independent reference implementation built from official data, then
  restored or excluded with documented evidence, and pre-audit numbers MUST be retained.
- **FR-039**: Non-discriminative cells MUST be identified by a mechanical rule committed before the
  results are seen.
- **FR-040**: Parameters and thresholds MUST be calibrated only on a tuning set disjoint from
  CEC-2017, CEC-2022, and the engineering suite, then frozen and committed before any test run.
- **FR-041**: Every table and in-text number MUST be regenerable from committed seeds, code, and raw
  results, and MUST be re-checked against its source data by an automated presentation validation.

**H. Reporting and terminology**

- **FR-042**: The manuscript MUST contain the operator-family table (all 19 mechanisms, with citations),
  a metaphor-free algorithm description, and the overlap audit against CA.
- **FR-043**: No formal term may contain a real person's name, nickname, or likeness, or a club or
  competition trademark. Each archetype MAY carry at most one sentence acknowledging the style of
  play that inspired it.
- **FR-044**: The manuscript MUST position TFO against existing sport- and league-inspired
  metaheuristics and state what is structurally different.
- **FR-045**: The manuscript MUST NOT contain a real-world application case study.

### Key Entities *(include if feature involves data)*

- **Squad (population)**: the set of candidate solutions: one Sweeper-Keeper plus outfield agents.
- **Agent (player)**: a candidate solution with position, fitness, personal best, archetype, lattice
  slot, stamina, stagnation count, per-agent mesh size, and last-review snapshot.
- **Archetype**: one of eight operator profiles; it determines the agent's default move.
- **Formation**: a lattice shape (lines × lanes) that defines the interaction graph. Its shape is a
  control variable.
- **Ball**: the current focal point of attack, with position, fitness, and current carrier. It is
  distinct from the incumbent best.
- **Keeper archive**: a bounded, distance-diverse set of best-so-far solutions.
- **Tabu register**: short-term memory of zones (the positions of substituted-out agents and of
  abandoned ball locations) that VAR checks against.
- **Match clock**: the evaluation budget divided into fixtures, which set the boundaries for
  rotation, zone redraws, stamina recovery, and substitution caps.
- **Tactical state**: the manager's current state and the parameter vector it sets.
- **Run record**: the seed, final error, convergence trace, per-mechanism evaluation counts, and
  tactical-state trace for one run.
- **Benchmark cell**: a (suite, function, dimension) combination, with its audit status and evidence.
- **Hypothesis register**: the pre-registered expectations H1 to H5 and their final verdicts.

## Success Criteria *(mandatory)*

### Measurable Outcomes

*Rigor criteria. These must be met for the project to be complete.*

- **SC-001**: 100% of TFO's mechanisms (19 of 19 at design time, and every one that survives ablation)
  appear in the operator-family table with a named family and at least one canonical citation;
  zero mechanisms are unmapped.
- **SC-002**: At least half of TFO's mechanisms belong to operator families absent from CA's
  operator-family table (11 of 19 at design time), and the ratio is re-reported after ablation
  pruning.
- **SC-003**: 100% of runs, for every algorithm in every cell, consume no more than the shared
  evaluation budget, as confirmed by exact counting. TFO's evaluation allocation per mechanism is
  reported as percentages of the budget, and no overhead figure in the manuscript is an estimate.
- **SC-004**: 100% of the benchmark cells used in any analysis have a recorded audit outcome. Every
  failing cell is either restored after independent cross-validation or excluded with its evidence
  and pre-audit numbers retained.
- **SC-005**: A third party following the documented reproduction sequence regenerates 100% of the
  reported table values identically from the committed seeds, and the automated presentation
  check reports zero mismatches.
- **SC-006**: The ablation covers 100% of switchable mechanisms (at least 18 single-off variants), the
  three group-level variants, and TFO-static, on at least six problems with 30 runs each. It names
  the smallest set of mechanisms that accounts for at least 80% of the total measured
  contribution, and it gives a remove-or-justify disposition for every mechanism whose mean error
  ratio lies within [0.95, 1.05] with at most one significant problem.
- **SC-007**: The sensitivity sweep classifies 100% of parameter groups (including the manager's
  thresholds, which the sibling project did not sweep) as sensitive or robust, with ratio and
  significance evidence per problem.
- **SC-008**: Every loss of TFO to any roster algorithm on any validated cell appears in a main-text
  table, and 100% of the pre-registered hypotheses H1 to H5 are reported as confirmed or refuted.
- **SC-009**: Zero formal terms (archetype and mechanism names, symbols, table rows, figure labels,
  code identifiers) contain a real person's name or likeness.
- **SC-010**: TFO-static appears in 100% of the experiments that TFO appears in.

*Pre-registered research-outcome targets. These are reported whichever way they fall, and a
refuted target is published as a finding, not hidden.*

- **SC-011** (H1): On the full CEC-2017 suite at D = 30, TFO attains the best mean Friedman rank among
  the classical/moderate group (TFO, TFO-static, GWO, PSO, GA, WOA).
- **SC-012** (H1): On the validated CEC-2022 cells and on the seven engineering problems, TFO again
  attains the best mean Friedman rank of the classical/moderate group, with at most 2 significant
  losses in the 35 engineering comparisons against that group (7 problems × 5 rivals).
- **SC-013** (H2): TFO significantly outperforms TFO-static on more CEC-2017 functions than the
  reverse, and has the better mean rank, which demonstrates that the adaptive layer earns its place.
- **SC-014** (H3): Compact formations shorten the measured takeover time relative to stretched ones
  by a statistically significant margin, in the direction that structured-population theory
  predicts.

## Assumptions

- **Name.** The formal name is *Total Football Optimizer (TFO)*, and the ablation twin is *TFO-static*.
  The working title "The Football Algorithm (FA)" was set aside because "FA" is the established
  acronym of the Firefly Algorithm (Yang, 2009; ~4,100 citations) — confirmed, not assumed — and
  would be ambiguous in results tables. A plain "Football Optimizer (TO)" was considered and
  rejected: "TO" is Topology Optimization's acronym in the same engineering-design-benchmark field
  this paper uses, clashes with Tornado Optimizer (TOC, 2025) and Teamwork Optimization Algorithm
  (TOA), and the full name nearly duplicates the existing Football Optimization Algorithm (FbOA,
  El-kenawy et al., 2024) — see the prior-art bullet below. "TFO" itself is not perfectly clean:
  three low-citation, unrelated methods share the string (Twin Fang Optimization, 2025; Tactical
  Flight Optimizer, 2025; Tapeworm Foraging Optimization, 2026) but none is a plausible baseline or
  comparison method. The manuscript MUST spell out "Total Football Optimizer (TFO)" in full at
  first use and MAY note the minor collisions in a footnote; this is a lower bar than clashing with
  an 86+-citation method in the same field. "The Football Algorithm" can remain the informal series
  name alongside the Chess Algorithm.
- **Budget.** The evaluation budget is matched across algorithms, not iterations (a deliberate
  tightening relative to CA's iteration-matched protocol). The default is the suite's official
  maximum (10,000 × D evaluations for CEC suites). If compute limits force a reduction, one reduced
  budget is applied uniformly to every algorithm, declared in the paper, and budget-aware baselines
  (L-SHADE's population-reduction schedule) are configured to the actual budget.
- **Population.** TFO and the classical baselines use a population of 30 by default (the sibling's
  setting), with TFO's 30 counting the Sweeper-Keeper. L-SHADE and CMA-ES use their own recommended
  population rules. Archetype fractions are a planning-phase decision and are covered by the
  sensitivity sweep.
- **Runs and statistics.** Each cell gets 30 independent runs for parity with the sibling paper,
  although the official CEC-2017 protocol uses 51; 51 is adopted if the compute budget allows.
  Pairwise tests use the Holm correction.
- **Engineering suite.** The seven problems are the sibling project's seven, in one shared
  formulation for every algorithm, which by default is the sibling's static-penalty formulation.
- **Tuning set.** It is a set of classical benchmark functions and function-dimension combinations
  that appear in none of the test suites. This fixes the sibling's weakness of checking thresholds
  on CEC-2017 functions that were also reported.
- **Deterministic objectives only.** No noisy-objective re-evaluation mode is in scope. VAR's checks
  are the geometric, tabu, and feasibility checks of FR-021.
- **CA as comparator.** CA is recommended (SHOULD) rather than required, because the project owner's
  roster did not list it. It is included by default because it tests the "not a reskin" claim
  empirically at low cost, since its implementation already exists.
- **Overlap classification.** The Virtuoso's compass search is counted as a family absent from CA:
  CA uses simplex-type reflection and line extrapolation, which are different direct-search
  families. This is flagged for reviewer scrutiny rather than assumed uncontroversial.
- **Prior art to verify during the literature review.** Sport- and league-inspired metaheuristics to
  cite and distinguish from include, at minimum: League Championship Algorithm, Soccer League
  Competition, Football Game Based Optimization, World Cup Optimization, Football Optimization
  Algorithm (FbOA, El-kenawy et al., 2024), Football Team Training Algorithm (FTTA, *Expert Systems
  with Applications*, 2024), Tiki-taka Algorithm (TTA, 2020), Modernized Tiki-taka Algorithm (MTTA,
  2026), and Soccer Match Algorithm (SMA, 2024). Exact references are to be verified before
  citation. The **between-teams-vs-one-squad distinction no longer holds as the primary claim**:
  several of these (FbOA, FTTA, TTA, MTTA, SMA) already model tactics or role specialization
  *within* one team, so that framing alone would not survive review. TFO's positioning instead
  rests on the specific structural mechanisms named in `mechanism-map.md`'s distinctiveness pitch —
  a formation shape that is itself a dynamic interaction topology (not a fixed neighbourhood or
  role list), agents that swap roles under that shape rather than being permanently typed, a focal
  point (the ball) carried by threshold-accepted passes rather than every agent chasing the
  incumbent directly, and mechanisms with no counterpart in any of the above (the deferred VAR
  audit with rollback; the moving offside ε-line). The manuscript MUST check each of these prior
  methods individually against that mechanism list, not merely assert novelty from the team/squad
  framing.
- **Scope.** No real-world application case study is designed or planned. The engineering design
  problems are benchmarks.
- **Pre-registered hypotheses** (committed now, verdicts reported later): **H1**: TFO is the best of the
  classical/moderate group on all three suites. **H2**: TFO beats TFO-static overall. **H3**: the
  formation topology behaves as structured-population theory predicts. **H4 (expected loss)**:
  L-SHADE and CMA-ES outrank TFO on most functions of every suite. **H5 (expected loss niche)**:
  because a structured population slows takeover, TFO converges more slowly than panmictic
  baselines on unimodal CEC-2017 functions; following CA's finding, measured contribution is
  expected to concentrate in the local-refinement (Virtuoso, set pieces) and differential
  (Box-to-Box) families.
- **No open clarifications.** No clarification markers were raised. Every ambiguity was resolved by
  the defaults above, because the specification was produced non-interactively.
