# 0017 — The objective function, and the evaluation that opens a round

Status: proposed 2026-11-13 as roster group R11-PRE-OBJECTIVE-FUNCTION; in force
from the owner's approving review of the pull request that lands it. Report-only
for round 11, whose close sets the baseline; it gates process changes from
round 12.

## Context

The owner, verbatim (tvofi, 2026-11-13): *"I want the agentic coding process to
converge against optimal quality, lead time and token effectiveness, both with
the number of audit rounds, and also within the rounds by the self-feeding
mechanisms"*; *"at least for objective bugs, I want the codebase to converge
towards 0 bugs with infinite number of audit rounds"*; *"have a fable seat
define that function and add it in the audit process, so that everything can be
evaluated against that objective when a new round is started, and any changes
needed is made before the finders start"*.

Round 10's two pre-studies (the process convergence audit and the dimension
coverage audit; neither is in the tree, and this record restates what it
takes from them) found no variable with a target, a sensor, a feedback path
shorter than its disturbance and a bounded controller, and no tracked
enumerator for escapes, injection, coverage, lead time per class, closure
history or tokens.

The owner's acceptance test for this record, verbatim (2026-11-13): *"a perfect
model that reads it, should be able to improve the dimensions, process and
machinery so that that round is completed perfectly against all dimensions, in
a perfect way"*; *"Running that perfect audit round should result in perfect
production code"*; *"the integration is perfecty generic and can run every
install in a perfect way, resulting in perfect savings"*. So the record is
anchored on the product, defines the end state and not only a direction, and
is meant to be sufficient with the tree alone.

## 1. The terminal objective: perfect production code

Every process and machinery term below is instrumental to the state of
`custom_components/` and `blueprints/` at a round's close. That code is
**perfect** when all three hold:

1. **Every dimension's perfect result holds** (the table below).
2. **The dimension set is complete**: no defect or shortfall of the product
   exists that no dimension would call a failure. Its measure is the term
   `unowned`.
3. **The three product terms are at their end state**: `generality`,
   `operation` and `regret`.

A dimension's **distance** is the count its enumerator prints against the
end state, over the universe `dev/audit/config/scopes.json` gives it. Where
the column says NO-READ no tracked command prints that count at this record's
landing: the distance is unknown, never zero, and the named roster group
builds the read. A proxy is named as one and is never the distance. The floor
is what no reader of this record can remove.

| dimension | its perfect result | decided by | enumerator of the distance | floor |
|---|---|---|---|---|
| D0 price optimality | zero `regret` on every cell of its grid | measurement | NO-READ: the same-information oracle of this section, raced per cell of `tests/profiles.py`'s price shapes and climates; R10-DIMENSIONS-FULL-COVERAGE. Proxy: `tests/optimality.py` reads the solver against its own model | `regret`'s |
| D1 robustness | no wedge, leak, race, stale read or lost store on any enumerated lifecycle path, store, timer, listener or guard | measurement | NO-READ: a census printing each path, store, timer, listener and guard with the test that drives it; R10-DIMENSIONS-FULL-COVERAGE | none |
| D2 mathematical and physical sanity | every identity holds over its stated operating grid; every constant justified | measurement | NO-READ: the identities and their grid are named in no tracked list; R10-DIMENSIONS-FULL-COVERAGE | none |
| D3 test-suite gaps | every guard site pinned by a test that imports the production symbol and whose oracle is not the code under test | measurement | `python3 tests/mutation_table.py --scope full`: surviving mutants and unpinned sites | equivalent mutants, each triaged by name |
| D4 UI/UX | every page, state and flow step renders and works in every shipped language and stated environment; beyond that, the owner's acceptance criteria | measurement, then the owner | `node tests/card_browser.mjs` for rendering; the rest undecided until `owner_criteria.D4` is set | none |
| D5 docs structure and comments | the owner's acceptance criteria | the owner | undecided until `owner_criteria.D5` is set | none |
| D6 claim verification | every claim in the README, docs, strings and release notes is true of the code, and every required user action is stated | measurement | `python3 tests/doc_claims.py` for the claims it registers; NO-READ for a claim outside its register: R10-D5-D6-FULL-SCOPE | none |
| D7 architecture | the programme target of decision 0015 met with no gate metric risen | the owner's target | `python3 tests/structure.py` and `python3 tools/audit/archscore/score.py --diff` against the target of `owner_criteria.D7` | none |
| D8 sensors | every entity publishes the right value, in the right order, with its true reason, in every language | measurement | NO-READ: `python3 tests/entities.py` pins the entities it collects, and nothing prints entity by state by language with the pinning test; R10-DIMENSIONS-FULL-COVERAGE | none |
| D9 efficiency | every cost centre inside the owner's Pi-class budget | the owner's budget | undecided until `owner_criteria.D9` is set; `tests/stress.py` then reads the cost | the solver's work at the planning horizon |
| D10 quality scale | every rule of the owner's target tier met at every site | the owner's tier | undecided until `owner_criteria.D10` is set; `quality_scale.yaml` in the integration's directory then lists each rule's state | rules Home Assistant adds after the baseline |
| D11 governance mechanisms | every mechanism fires when it should and only then | measurement | `node tools/policy/policy_lint_mutants.mjs` and each instrument's `--self-test`; NO-READ for a mechanism with neither: R10-DIMENSIONS-FULL-COVERAGE | none |
| D12 generalization | `generality` at 1 | measurement over the supported population | the denominator: `python3 tools/audit/check_scopes.py --population`; the examined count NO-READ: the cell ledger, R10-DIMENSIONS-FULL-COVERAGE | `generality`'s |
| D13 process yield and cost | the process terms of section 2 at their end state | measurement | section 2's enumerators | section 2's residuals |
| D14 recurring bug classes | no open class, no instance of a barriered class | measurement | `python3 tools/audit/fold_ledger.py check` over `dev/audit/config/bugclasses.json` | none |
| D15 live diagnostics | every bundle replays with no unexplained divergence | measurement | `python3 tools/replay/debug_replay.py --bundle` per bundle; the bundle set is NO-READ (no tracked list of the installs that sent one): R10-DIMENSIONS-FULL-COVERAGE | installs that send no bundle |

Where the third column names the owner, the criterion is the tracked file
`objective.json` names under `owner_criteria`; a null there makes the result
undecided, not perfect, and the evaluation cards it.

The supported population and the comfort bounds below were set by round 10's
orchestrator under the owner's ruling (tvofi, 2026-11-13, verbatim: *"For 5,
this is yours to set using your best judgement"*), each on the basis that it
is what the code already accepts or enforces, so neither adds a claim the
product does not make. The owner changes either at his review; neither is a
tunable the evaluated round may loosen.

**The three product terms.**

- **`generality`**: the integration is right on every install of the supported
  population, with no behaviour correct only for the owner's hardware, tariff,
  climate or configuration. **The supported population is every install the
  integration's own configuration flow can complete at the head**: each pump
  control kind, each tank and valve layout, each price source, each unit
  system it accepts, enumerated from the code and the fixtures and never from
  documentation. A shape the flow accepts and no fixture covers is a measured
  gap in this term, not out of scope. **Its axes and their levels are what
  `python3 tools/audit/check_scopes.py --population` prints**, read from the
  tracked source `objective.json` names per axis under `population`: the
  flow's own option tuples (layout, duty and control modes, valve, tank,
  price and fee sources, building presets, accepted sensor units), each
  optional entity key of the flow present or absent, the translation files,
  the Home Assistant floor in `hacs.json` and the typed version, and the
  price shapes and climates `tests/profiles.py` defines. An axis the flow
  leaves continuous (tank volume, house size) has no tracked levels: it is
  NO-READ in that file, with what would read it. A level the code gains or
  loses moves the population with no edit here.
  The population is the product of the axes, which no seat can walk; **the
  cells the term counts are every level of every axis and every pair of
  levels from two axes**, the two counts the command prints. An interaction
  of three or more axes is in the population and in no cell: it is this
  term's residual. A cell is **examined** when a run that names it exercised
  it end to end and asserted on the outcome (the plan, the writes, the
  published state), from one of four sources: a simulation through the
  coordinator at that configuration, a recorded bundle from such an install
  replayed by D15, a contributor's install report, or a property test whose
  generator is shown to have drawn the cell. A run that asserts nothing
  examines nothing. Perfect: every cell examined, and no defect found on an
  install that the owner's install could not have shown. D12's brief must
  name the command as its universe, add the card and the blueprints to it,
  declare the levels of each NO-READ axis, and keep a cell ledger printing
  each cell with its source, its asserting test, or `not run`:
  R10-DIMENSIONS-FULL-COVERAGE.
- **`operation`**: on each install the executed plan is the right one and is
  executed as planned: every actuator write happens, holds and releases as
  intended, and no comfort or safety bound is violated. Its universe is every
  write site and every hold site, times the plan states (idle, partial, boost,
  hot-water only, first cycle after an upgrade). A write site is a service
  call in the integration's directory that changes a device (`git grep -n
  "async_call(" custom_components/` lists the candidates). Perfect: at every
  cell the value written equals the target the plan computed for that cell,
  read from the plan and never from a document; every refusal has a release
  that needs no person; and replayed bundles show no bound violated. It
  belongs to the actuator-write dimension (write safety and liveness), which
  has no brief at this record's landing: R10-DIMENSIONS-FULL-COVERAGE drafts
  it with the cell ledger, and D8 owns the published reason.
- **`regret`**: what the install paid above the best plan its information
  allowed. **The comfort bounds are those the product already enforces for
  the person**: the configured comfort range, the hot-water minimum, the mold
  and legionella guards, the entity's own limits. Savings are measured only
  among plans that hold every one; a plan that buys savings by leaving a
  bound is a defect of `operation`, never a saving.
  Four costs are read per grid cell or install-day, each over plans holding
  the bounds and inside the pump's limits:
  - `C_real`: metered energy times the price paid.
  - `C_same`, the **same-information oracle**: the least cost on the
    **measured house** given, at each decision time, only the **exogenous
    inputs** that existed then: the prices published, the weather provider's
    forecast as issued, every sensor reading up to that time, and the
    configuration. The measured house is the thermal response and the draw
    the window's own sensors recorded, identified after the fact; it is never
    the integration's learned model, and nothing the integration forecast or
    learned is an input.
  - `C_fore`, perfect foresight: the same, given the realised prices and
    weather.
  - `C_model`: the cost the integration's own model predicted for the plan it
    executed.

  `regret` is `C_real - C_same`, target 0. It is all removable loss: the
  integration's own house-model error, its own demand-forecast error, the
  solver's gap and the gap between plan and execution. The **floor** is
  `C_same - C_fore`: the provider's forecast error in price and weather,
  which no code removes; it is reported beside `regret` and is never part of
  it. The pump's limits and the bounds bind all three plans alike, so they
  are in neither. The **model gap** `|C_real - C_model|` is part of the term:
  a cell is at zero regret only with its model gap inside the band, since a
  model that agrees with itself and not with the meter has measured nothing.
  The oracle is given the realised draw, so the part of a person's draw that
  no history predicts lands in `regret` and not in the floor: zero is the end
  state the term approaches, and that part is its residual. On a flat price
  every plan costs the same, so a savings claim owes the flat-price null (a
  saving on a flat price is zero). D0 owns the term.

## 2. The function

It is an ordering, never one weighted score: a weight is a price at which an
escape may be bought with tokens, and the owner set none. `objective.json`
under `dev/audit/config/` lists the terms and their layers for
`tools/audit/check_scopes.py`; this section defines them. An **objective bug**
is `COMMON.md`'s finding of stop-rule class `bug` that a judge verified, or an
outside report whose hotfix carries the failing-test-first proof. The
**window** of round N runs from the previous closeout stamp to its own
(decision 0016). A **production merge** is `tools/audit/machinery_ratchet.py`'s
class.

| term | layer | definition | unit; denominator | target; direction | enumerator |
|---|---|---|---|---|---|
| `regret` | 1 | section 1: `C_real - C_same`, mean over the grid cells and install-days read; beside it the floor `C_same - C_fore` and the model gap | currency per day and share of `C_same`; cells and install-days | 0 with the model gap inside the band; down | none. The oracle harness (D0's step), the realised-cost record per install-day from a bundle (D15's step) and the model gap beside both: R10-DIMENSIONS-FULL-COVERAGE writes the two steps and their denominators into the briefs |
| `operation` | 1 | section 1: cells where the write, its hold and its release equal the plan's target | share; write and hold sites times plan states | 1; up | none. The actuator-write dimension's cell ledger: R10-DIMENSIONS-FULL-COVERAGE |
| `generality` | 1 | section 1: share of population cells examined; beside it defects the owner's install could not have shown | share; the levels and pairs `check_scopes.py --population` prints | 1 and 0; up and down | the denominator: that command. The examined count: none; D12's cell ledger, R10-DIMENSIONS-FULL-COVERAGE |
| `unowned` | 1 | escapes and owner reports in the window that belong to no dimension | items per round | 0; down | none; read off `escapes` once it records its owner: R10-DIMENSIONS-FULL-COVERAGE |
| `escapes` | 1 | objective bugs in a released product version, reported in the window by anyone but the round's finder seats, each with who found it and the owning dimension (`none` is a value) | bugs per round; beside it the removed count (verified findings whose group merged) and removed / (removed + escapes), whole and per dimension | 0; down | none. R10-DIMENSIONS-FULL-COVERAGE records found-by and owner; R11-PRE-ROUND-METRICS prints the series. `scorecard.py` line `E` is a proxy with no window and no owner |
| `injected` | 1 | objective bugs whose cause is a pull request merged in this window or the previous one, named on the fixing group | bugs per 100 production merges | 0; down | none; same two groups. Proxy: production hotfix merges over production merges (`scorecard.py` line `H`) |
| `product_green` | 1 | share of main's concluded `CI` push runs in the window whose `gate` job succeeded | share; concluded runs, the cancelled count beside it | `thresholds.product_green_floor`; up | `scorecard.py report` line `A_gate`, which reads the last 20 and has no input producer: R11-PRE-ROUND-METRICS feeds it and adds the window |
| `coverage` | 1 | per dimension, the least examined / universe over its steps, each universe printed by a named command; a step reporting none, and a dimension not run, count 0 | share; the dimension count | 1 in every dimension; up | none. R10-DIMENSIONS-FULL-COVERAGE (the denominator rule) |
| `unexamined` | 1 | production merges after the baseline that no finder pass examined before the round's close (a feature, an outside change, a fix's own diff) | share; production merges in the window | 0; down | none. R11-PRE-ROUND-METRICS, from the roster's group kinds |
| `first_pass` | 2 | share of merged pull requests whose first verdict was `merge` | share; reviewed merges in the window | 1; up | `tools/audit/seat/flow_metrics.py --window`; `review_strength.py --window` |
| `lead_time` | 2 | hours from a production group's roster entry to its merge on main, p50 and p90; the clock starts at the entry because a seat chooses its first commit | hours; production groups merged in the window | no target; down | none (`flow_metrics.py` prints merge hours only). R11-PRE-ROUND-METRICS |
| `closure_slip` | 2 | days the forecast closure moved later per day of plan history after the register | days per day; beside it round start to closure in days, and the groups deferred out | `thresholds.closure_slip_ceiling`; down | none: the history exists only inside rendered plan pages. R11-PRE-ROUND-METRICS |
| `tokens_per_change` | 3 | every usage field of every seat (orchestrator, local, cloud) summed over the window, over production merges; one unledgered seat class makes the term NO-READ, never a partial | tokens per production merge; beside it the round total and the coordination share | no target; down | none. R11-PRE-TOKEN-LEDGER |

**Comparing two rounds, or a change's before and after.** A term **moved**
only beyond its band: for a count, a difference above twice the square root of
the two counts' sum; for a share, two standard errors of its denominator; for
`lead_time`, `closure_slip` and `tokens_per_change`, the relative difference
`thresholds.band_lead_time`, `band_closure_slip` and `band_tokens_per_change`
give. Inside the band it is a tie.

**The owner's values are fields of `objective.json`**: `thresholds` holds the
five above, `owner_criteria` the criterion file of each owner-decided
dimension. A null `value` is unset: every comparison or result that needs it
is **undecided**, neither held nor missed, and the evaluation cards it;
`check_scopes.py --round` refuses a start with an unset one uncarded. The
`proposed` beside a value is the orchestrator's proposal and is read by
nothing.

**A NO-READ is undecided, never a tie.** A term NO-READ on either side of a
comparison has not moved and has not held. A term read for the first time
sets its baseline and is no move. So while any layer-1 term is NO-READ,
layer 1 is not shown held and rules 2 to 4 rank nothing: the only process
changes kept are the ones that build a missing read to this section's
definition, and the ones the owner accepts by card.

1. **Layer 1 is never traded.** A change that moves any layer-1 term the wrong
   way is refused whatever else it gains; only the owner accepts one, by card.
   Targets give the direction: a round holds layer 1 when every layer-1 term
   is read on both sides and none is worse.
2. Among changes holding layer 1, the better one moves a layer-2 term the
   right way and none the wrong way. One up and one down is no improvement:
   terms are not traded inside a layer either.
3. Among those tied on layer 2, the lower `tokens_per_change` is better.
4. Still tied: the one with less machinery (`machinery_ratchet.py --measure`),
   then the status quo, since a change has a cost and a tie has no gain.

A count of findings is in no layer: fewer found cannot be told from less
examined.

**The perfect round, and what no reader can remove.** A round is perfect when
it ends with the code of section 1 and ran with every item right first time,
no waiting, no rework and no token that changed no outcome. Each term's
**distance** is its value in the closing round's objective record against the
end state here; a NO-READ is an unknown distance, never zero.

| term | end state | the residual no reader of this record can remove |
|---|---|---|
| `regret` | 0 against the same-information oracle, the model gap inside the band | the draw no history predicts, and the sensor error in the measured house, which is a band on the read and not a cost. The provider's forecast error is the floor `C_same - C_fore`, outside the term |
| `operation` | every cell at the plan's target | what the pump does behind an acknowledged write |
| `generality` | every level and pair examined | interactions of three or more axes; cells no source reaches: no bundle, no contributor, and a simulation only as faithful as `tests/ha_contract.py` records the stub to be |
| `unowned` | 0 | none in what is reported; a shortfall nobody reports and no dimension names is invisible from inside |
| `escapes` | 0 | as `unowned`, and reports depend on installs existing to report |
| `injected` | 0 | none |
| `product_green` | 1 | runner and GitHub outages |
| `coverage` | 1 | none where the universe is enumerable; `generality`'s residual where it is not |
| `unexamined` | 0 | none: a late merge can always be examined before the close, at a cost in `closure_slip` |
| `first_pass` | 1 | none in principle; a judgement criterion the owner has not written makes a first verdict a guess |
| `lead_time` | touch time | the required `gate` job's wall clock, one review, and the owner's review on a code-owned path |
| `closure_slip` | 0 | owner and outside work folded into the open round, which the owner orders |
| `tokens_per_change` | one read of the contract, the brief and the diff per seat, one write of the change | that read and write |

## 3. Scoring an object

`objective.json` maps each class to the globs whose tracked files are its
objects. `CLAUDE.md` and `AGENTS.md` are scored as rules; a script with no
guide, a hook and a skill as instruments; a `.claude/workflows/` script as a
gate. An object is **better** when its yield per cost rose with layer 1 held.

| class | cost | yield | scorable at round 10's close |
|---|---|---|---|
| dimension brief | its finder and verifier seats' tokens and wall clock | removed bugs it found; its `coverage`; less its `escapes` | found and escapes yes (judge record; escapes by hand); cost NO-READ until the token ledger keys a seat by dimension |
| role contract | its tokens times the seats that load it | the seat's first-pass yield and real-catch incidence (`review_strength.py`) per role | per role in part; per clause never, until a block's class names the clause |
| rule | its tokens times its loads, and the seconds of its refusals | its bug class's instances after the rule merged | no: `bugclasses.json` records no instance date and nothing counts a load |
| instrument | its lines, its run seconds, the hotfix groups naming it | refusals a fix followed, or lead time removed | cost yes (roster, `wc`); yield NO-READ until a refusal is logged with its outcome |
| gate (a workflow) | runner seconds per merge and reds no product fault caused | reds a product fault caused | cost NO-READ (no tracked command prints runner seconds per merge: R11-PRE-ROUND-METRICS); yield NO-READ until a red carries its cause |
| standing seat (a role) | tokens per session | merges or dispatches operated, against the script that would do them | local seats by hand from transcripts; R11-PRE-TOKEN-LEDGER makes it a read |

- **keep**: yield per cost not worse, or the object is unscored. An unscored
  object's evidence is `NO-READ:` and the record that would score it; the
  evaluation reports the unscored share, whose direction is down.
- **change**: a layer-1 term read through the object missed (an escape in a
  dimension's territory, a step with no denominator, a red with no product
  cause), or its cost rose beyond the band at flat yield.
- **remove**: measured yield of zero in two consecutive rounds, with no
  layer-1 term read through it. Never on a NO-READ.

**From a distance to a change**, with this record and the tree alone:

- `coverage` below 1 in a dimension: its brief names a universe with no
  enumerating command, or instructs a sample; write the command into the
  brief, delete the sampling instruction, and have rotation carry what was
  not reached.
- An escape owned by a dimension: name the step that should have found it and
  the input that step did not drive, and add that input to the step.
- An `unowned` item: card the dimension, or the widening of one, whose perfect
  result the item violates; until then section 1's clause 2 fails.
- `injected` above 0: read each cause's review; the fixer's or the reviewer's
  contract gains the check that would have refused it, with its null control.
- `first_pass` below 1: the most frequent first-block class names the
  contract clause or the instrument to change; a class a script can decide
  moves to the script.
- A NO-READ term: build the enumerator to the definition in section 2; nothing
  else about that term can be decided first.
- A cost above the residual in the table above is the removable part; the
  residual itself is changed only by changing the gate, the review rule or
  the population, which are the owner's.

## 4. From a perfect round to perfect code

One round yields the code of section 1 only if every link holds:

| link | measured by | chance it fails |
|---|---|---|
| every item in scope was examined | `coverage`, `generality` | 0 at coverage 1 over an enumerable universe; otherwise the unexamined share |
| every real defect in an examined item was found | the planted-defect recall (section 5) | 1 less the recall; unmeasured today, and never 0 for a finder that is a model |
| every finding was fixed correctly | findings open at the close; fixed findings reported again | NO-READ, and in no term: `injected` counts a new defect, never a fix that did not fix. It is read once a re-report names the fix it follows: R10-DIMENSIONS-FULL-COVERAGE |
| no fix injected a defect | `injected` | its rate per fix |
| nothing unexamined merged before the close | `unexamined` | its share |
| the dimension set is complete | `unowned` | unknowable from inside; `unowned` is its lower bound |

Links 2 and 6 are probabilistic by nature, so **one round guarantees perfect
code under no condition this record can check**. What is supported is
convergence over rounds, under the conditions below, and no stronger claim.


Let N be the objective bugs present at a round's start, p the least chance
that one is found in a round (coverage times recall), q the bugs a fix injects per bug removed, and g
the bugs that new product surface adds per round. Found bugs are fixed before
the next round (decision 0016), so the expected count obeys
N' <= (1 - p(1 - q)) N + g.

- With p > 0, q < 1 and g = 0 the expectation falls geometrically to zero, and
  the chance that any bug remains falls with it.
- With g > 0 it falls to the floor g / (p(1 - q)), not to zero. **Zero needs
  new surface to stop adding bugs**; the function lowers the floor and cannot
  remove it.
- `lead_time` and `tokens_per_change` are bounded below, so a sequence that
  never rises converges to a floor. Nothing here says the floor is low, or
  that it is reached faster each round.

The conditions are assumptions; each has a sensor, and a failing one voids the
claim for that round:

| assumption | sensor | fails when |
|---|---|---|
| p > 0 for every bug | `coverage`; the planted-defect recall | a step reports no universe, or recall falls or is 0 for a planted kind |
| q < 1 and not rising | `injected` beside the removed count | `injected` moves up |
| g bounded | `unexamined`; product lines added per round beside `escapes` | escapes owned by `none`, or in files newer than the previous baseline, move up |
| escapes are seen | releases per day; the two-finder overlap estimate | `escapes` falls while the estimate of remaining bugs does not |
| the oracle set is fixed | the dimension list | a dimension is added: its first round's finds are a new baseline, never a regression |
| fixes land before the next round | the closure criteria | a finding is open at the next baseline |

**What the inequality assumes and no sensor above reads.**

1. **p is the least chance over bugs; recall measures a mean.** Planted
   defects estimate the average over the kinds someone thought to plant.
   Each round's survivors are the bugs with the lowest p, so the tail falls
   slower than the measured recall says, and a kind the finder model cannot
   see has p = 0 while every sensor reads well.
2. **The overlap estimate assumes independent finders of equal catchability.**
   Two seats of one model on one brief are positively correlated, so the
   estimate of remaining bugs is biased low and "escapes are seen" reads
   better than the code is. Seats on different models or briefs narrow the
   bias; nothing here measures it.
3. **Found is counted after the judge.** A real defect the verifier refuted
   or the judge voided is lost with no link and no term. Recall is therefore
   judged-real over planted, and a planted defect lost at either stage counts
   as missed.
4. **q counts injection per bug removed, g per unit of new surface.** A
   refactor, a documentation or process fix and the fix of a false positive
   can each inject with no bug removed and no surface added. `injected`'s
   denominator (production merges) covers them; p, q and g do not, so the
   inequality understates the floor by their rate.
5. **A fix that did not fix has no term** (link 3): such a bug stays in N
   with its finding closed, and is found again only at that bug's own p.
6. **The claim is about objective bugs, and about nothing else in
   section 1.** Nothing here argues that `generality`, `operation`, `regret`
   or an owner-judged dimension converges; `regret` carries a residual and
   cannot reach its end state.
7. **`escapes` depends on a reporting rate nobody measures**: how many
   installs exist and would report. A falling `escapes` cannot be told from
   fewer reporters.

So the function moving the right way does not show that the code holds fewer
objective bugs. It shows that the reads this record defines moved. The step
from one to the other rests on the seven assumptions above, of which none is
measured at this record's landing.

## 5. Honesty

- **Held-out checks are not terms**, so no seat is scored on them. *Planted
  defects*: objective bugs written into the baseline export by a seat that is
  neither finder, orchestrator nor evaluator, their list outside the finder
  wall; recall is found / planted. *Two-finder overlap* (the owner's round-11
  trial): two seats on one universe finding n1 and n2 with m shared estimate
  (n1 + 1)(n2 + 1) / (m + 1) - 1 bugs there. Neither has an instrument at
  this record's landing: R11-PRE-ROUND-METRICS builds both, recall counted
  after the judge and the overlap reported with the two seats' models. Until
  they run the assumptions they sense are unverified and section 4 is claimed
  for no round.
- **A process change is kept only on a measured before and after of the term
  it named, with the null control** that the same read does not move where the
  change is absent. From round 12; in round 11 the evaluation reports only.
- **The yardstick is the owner's.** This record, `objective.json`,
  `check_scopes.py`, each enumerator once built, and a round's evaluation and
  objective record are code-owned. Nobody edits this record, `objective.json`,
  the check or an enumerator but by a pull request reviewed as decision 0013
  requires of a code-owned path; an orchestrator proposes a refinement as a
  card. The orchestrator writes two
  things and no others: a closing round's objective record, once, which the
  evaluator re-reads term by term; and, into a card of the evaluation, the
  owner's ruling in his words with where he gave it (`ruling`). The approving
  review that pull request owes is what makes the transcription his.
  The evaluator writes the rest of the evaluation and never a ruling. After
  this record lands, adding a term or an object class removes one.

A control is **live** when a tracked check or a re-run command refuses the
false move at this record's landing, **beside** when it is a companion figure
a reader must look at, and **NO-READ** when it does not exist yet, with the
group that builds it. A term whose only controls are beside or NO-READ can be
moved falsely today, and section 2's NO-READ rule is what stops such a move
ranking a change.

| term | the cheapest false move | what catches it |
|---|---|---|
| `escapes` | rule a report not objective, or own it by `none`; release less often | beside: the owner's reports count unless the owner rules otherwise; `none` is a `change` verdict on the dimension list; releases per day. NO-READ: the overlap estimate, R11-PRE-ROUND-METRICS |
| `regret` | choose easy grid cells; score against the optimizer's own model of itself | live: the oracle's inputs exclude the integration's model by definition (section 1), and the flat-price null. NO-READ: the grid's denominator and the model gap from a bundle, R10-DIMENSIONS-FULL-COVERAGE |
| `operation` | drive only the idle plan; edit the documented target to match the code | the plan states are part of the cell, and the target is the plan's computed value, which no document edit moves. NO-READ: the cell ledger, R10-DIMENSIONS-FULL-COVERAGE |
| `generality` | narrow the supported population; count a stub run as an install; examine a cell with a run that asserts nothing | live: the population is `check_scopes.py --population` over the code's own tuples, so narrowing it is a product change. NO-READ: the cell ledger naming each cell's source and asserting test, R10-DIMENSIONS-FULL-COVERAGE; planted configuration defects, R11-PRE-ROUND-METRICS |
| `unowned` | assign every report to the nearest dimension | beside: the dimension's `escapes` then rises and its brief owes the step; the reviewer attacks the attribution |
| `unexamined` | relabel a feature as a fix; mark a late merge examined by a pass that only says it read it | beside: a fix names the judged finding it closes. NO-READ: an examining pass reports its universe and denominator over the late diff like any step (`coverage`'s rule), R10-DIMENSIONS-FULL-COVERAGE |
| `first_pass` | approve weakly; settle a block outside the verdict bus | beside: real-catch incidence (`review_strength.py --window`). NO-READ: `injected` and `escapes`, its two catchers; until both are read `first_pass` ranks nothing (section 2) |
| `injected` | leave the cause unnamed; the fixing group names a cause that spares its own predecessor | beside: the cause is checked in review; the hotfix proxy. NO-READ: the cause recorded by the root-cause seat, which is not the fixer, R10-DIMENSIONS-FULL-COVERAGE |
| `product_green` | cancel a red run; move a check out of `gate` | beside: the cancelled count is in the denominator's row. NO-READ: `gate`'s check count per window, R11-PRE-ROUND-METRICS |
| `coverage` | declare a smaller universe; re-run a command that prints a narrow universe; report examined unread | live: `check_scopes.py` refuses a tracked path in no universe. NO-READ: planted defects spread over the natural universe, not the declared one, R11-PRE-ROUND-METRICS |
| `lead_time` | enter the group late, when its fixer is ready; split a group; skip review | beside: merged production lines per group. NO-READ: the clock read from the commit that added the group to the roster, never from a field the orchestrator fills, and the gap from the finding's judged date to that commit beside it, R11-PRE-ROUND-METRICS |
| `closure_slip` | pad the first forecast; defer scope | beside: round start to closure and the deferred count |
| `tokens_per_change` | split a change; run work in an unledgered seat | beside: the round total. NO-READ: the ledger, where an unledgered class makes the term NO-READ, R11-PRE-TOKEN-LEDGER |
| a verdict | keep everything; record every term NO-READ with no card | live: `check_scopes.py --round` refuses a `remove` on a NO-READ, a NO-READ naming no builder, and an unset owner value with no card; the reviewer re-runs the read behind every `remove` and three `keep`s |

## 6. The step

Before a round's baseline is pinned, `dev/governance/roles/evaluator.md` runs:
one evaluator seat that is not the orchestrator and did not work the round it
grades, reviewed by a second seat as `fix-review.md` reviews a fixer, deciding
nothing — the owner decides each card. Every `unowned` item, every unset
value of `thresholds` and `owner_criteria`, and every NO-READ no roster group
builds yields a card.

- **Reads**: the closing round's `OBJECTIVE.json` in its directory under
  `dev/audit/yardstick/`, which the orchestrator writes at closure: per term a
  numeric `value` with the `enumerator`, a command on a tracked file, that
  printed it; or `no_read` with the reason, `would_read` (the record or
  harness that would read it) and `builder` (the roster group that builds
  it, or `card:` and a card's id). Recording a read is not grading it; the
  evaluator re-runs each.
- **Writes**: `EVALUATION.json` in the opening round's there: `round`,
  `reads`, `evaluator`, `reviewer`, `review` (the reviewer's `verdict` and
  the `sha` it was given at), `objects` (file to `verdict`, `evidence`, and
  `card` unless `keep`) and `cards` (id to the proposal; the `object` or
  `paths` it changes; `threshold`, `criterion` or `unowned` where it answers
  one; `decision` `accepted|rejected|deferred` with `ruling`; and `merged`,
  the commit of an accepted one).
- **Refuses**: `check_scopes.py --round N`, which `audit-find.js` runs at the
  baseline, exits 1 on a missing record; a term neither read nor NO-READ; a
  read with no number or with an enumerator that is no tracked file; a
  NO-READ naming no `would_read` or `builder`; an object without a verdict
  of the three and evidence; a `remove` on a NO-READ; an evaluator and
  reviewer that are one name under case and punctuation, or either the
  orchestrator; a review that is not `approve` at a commit holding these
  same verdicts; an unset owner value or an `unowned` item with no card; a
  card with no decision or no `ruling`; or an accepted card whose `merged`
  commit is not on the baseline, predates the review, or does not change the
  card's file.
- **Cannot read**: whether the evaluator worked the round it grades or was
  dispatched by the orchestrator it grades. A name is all the record holds.
  The token ledger keys a seat by group and role; once it exists, a seat in
  the graded round's ledger is refused: R11-PRE-TOKEN-LEDGER.

**Standing cost per round**: two seats and the owner's card rulings. Neither
seat has run, so the cost is a cap, not a measurement: the evaluator one
context of `dev/audit/README.md`'s pre-study size, the reviewer one of its
reviewer size; their tokens are the first row of round 12's ledger. The check
adds under a second to a round start (`## Figures` of the landing pull
request).

## Consequences

- Round 11 cannot start until round 10's objective record and round 11's
  evaluation are on main; with no enumerator built most terms are NO-READ,
  which is the baseline.
- R11-PRE-ROUND-METRICS, R11-PRE-TOKEN-LEDGER and R10-DIMENSIONS-FULL-COVERAGE
  build to the definitions above; a definition an instrument cannot meet
  returns here as a card, never as a quiet redefinition.
- Round 11's first evaluation holds a card per unset value of
  `objective.json`: the owner sets each there, or the round does not start.
