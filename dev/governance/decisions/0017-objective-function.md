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

Round 10's two pre-studies (`dev/audit/rounds/round10/`, the process
convergence audit and the dimension coverage audit) found no variable with a
target, a sensor, a feedback path shorter than its disturbance and a bounded
controller, and no tracked enumerator for escapes, injection, coverage, lead
time per class, closure history or tokens.

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

| dimension | its perfect result | decided by |
|---|---|---|
| D0 price optimality | zero `regret` on every cell of its grid | measurement |
| D1 robustness | no wedge, leak, race, stale read or lost store on any enumerated lifecycle path, store, timer, listener or guard | measurement |
| D2 mathematical and physical sanity | every identity holds over its stated operating grid; every constant justified | measurement |
| D3 test-suite gaps | every guard site pinned by a test that imports the production symbol and whose oracle is not the code under test | measurement |
| D4 UI/UX | every page, state and flow step renders and works in every shipped language and stated environment; beyond that, the owner's acceptance criteria | measurement, then the owner |
| D5 docs structure and comments | the owner's acceptance criteria | the owner |
| D6 claim verification | every claim in the README, docs, strings and release notes is true of the code, and every required user action is stated | measurement |
| D7 architecture | the programme target of decision 0015 met with no gate metric risen | the owner's target |
| D8 sensors | every entity publishes the right value, in the right order, with its true reason, in every language | measurement |
| D9 efficiency | every cost centre inside the owner's Pi-class budget | the owner's budget |
| D10 quality scale | every rule of the owner's target tier met at every site | the owner's tier |
| D11 governance mechanisms | every mechanism fires when it should and only then | measurement |
| D12 generalization | `generality` at 1 | measurement over the owner's supported population |
| D13 process yield and cost | the process terms of section 2 at their end state | measurement |
| D14 recurring bug classes | no open class, no instance of a barriered class | measurement |
| D15 live diagnostics | every bundle replays with no unexplained divergence | measurement |

Where the right column names the owner and no criterion is written down, the
result is undecidable, not perfect: the evaluation cards the missing criterion.

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
  gap in this term, not out of scope. Within it the cells are the product of
  these axes, each enumerated in D12's scope: pump make and control interface;
  each optional sensor and actuator present or absent; tariff and price shape;
  climate; house and tank size; duty mode; language; Home Assistant version.
  A cell is
  **examined** when one of four sources exercised it end to end: a simulation
  through the coordinator at that configuration, a recorded bundle from such
  an install replayed by D15, a contributor's install report, or a property
  test over the configuration space; the cell's row names which. Perfect:
  every cell examined, and no defect found on an install that the owner's
  install could not have shown. D12's brief must gain these axes, the card and
  the blueprints in its universe, and a cell ledger printing cells, examined
  and not run.
- **`operation`**: on each install the executed plan is the right one and is
  executed as planned: every actuator write happens, holds and releases as
  intended, and no comfort or safety bound is violated. Its universe is every
  write site and every hold site, times the plan states (idle, partial, boost,
  hot-water only, first cycle after an upgrade). Perfect: at every cell the
  value written equals the documented target, every refusal has a release that
  needs no person, and replayed bundles show no bound violated. It belongs to
  the actuator-write dimension the coverage audit proposes, which has no brief
  yet, and to D8 for the published reason.
- **`regret`**: realised cost less the cost of the oracle plan for the same
  prices, weather, house and comfort bounds. **The comfort bounds are those
  the product already enforces for the person**: the configured comfort range,
  the hot-water minimum, the mold and legionella guards, the entity's own
  limits. Savings are measured only among plans that hold every one; a plan
  that buys savings by leaving a bound is a defect of `operation`, never a
  saving. Perfect savings is zero regret
  against that same-information oracle. Regret against a perfect-foresight
  oracle is the stated upper bound on what any code could save, and is not a
  target. D0 owns it: its race against the oracle per grid cell, the
  flat-price null control every savings claim owes (savings on a flat price
  are zero), and the gap between measured and modelled cost in a live bundle.

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
| `regret` | 1 | section 1; mean over the grid cells and install-days read | currency per day and share of the oracle's cost; cells and install-days | 0 against the same-information oracle; down | none whole. D0's harnesses read part of the grid; no record holds realised cost per install |
| `operation` | 1 | section 1: cells where the write, its hold and its release are as documented | share; write and hold sites times plan states | 1; up | none. The actuator-write dimension, once briefed |
| `generality` | 1 | section 1: share of population cells examined; beside it defects the owner's install could not have shown | share; the enumerated cells | 1 and 0; up and down | none. D12's cell ledger; R10-DIMENSIONS-FULL-COVERAGE's denominator rule |
| `unowned` | 1 | escapes and owner reports in the window that belong to no dimension | items per round | 0; down | none; read off `escapes` once it records its owner |
| `escapes` | 1 | objective bugs in a released product version, reported in the window by anyone but the round's finder seats, each with who found it and the owning dimension (`none` is a value) | bugs per round; beside it the removed count (verified findings whose group merged) and removed / (removed + escapes), whole and per dimension | 0; down | none. R10-DIMENSIONS-FULL-COVERAGE records found-by and owner; R11-PRE-ROUND-METRICS prints the series. `scorecard.py` line `E` is a proxy with no window and no owner |
| `injected` | 1 | objective bugs whose cause is a pull request merged in this window or the previous one, named on the fixing group | bugs per 100 production merges | 0; down | none; same two groups. Proxy: production hotfix merges over production merges (`scorecard.py` line `H`) |
| `product_green` | 1 | share of main's concluded `CI` push runs in the window whose `gate` job succeeded | share; concluded runs, the cancelled count beside it | the owner's floor; up | `scorecard.py report` line `A_gate`, which reads the last 20 and has no input producer: R11-PRE-ROUND-METRICS feeds it and adds the window |
| `coverage` | 1 | per dimension, the least examined / universe over its steps, each universe printed by a named command; a step reporting none, and a dimension not run, count 0 | share; the dimension count | 1 in every dimension; up | none. R10-DIMENSIONS-FULL-COVERAGE (the denominator rule) |
| `unexamined` | 1 | production merges after the baseline that no finder pass examined before the round's close (a feature, an outside change, a fix's own diff) | share; production merges in the window | 0; down | none. R11-PRE-ROUND-METRICS, from the roster's group kinds |
| `first_pass` | 2 | share of merged pull requests whose first verdict was `merge` | share; reviewed merges in the window | 1; up | `tools/audit/seat/flow_metrics.py --window`; `review_strength.py --window` |
| `lead_time` | 2 | hours from a production group's roster entry to its merge on main, p50 and p90; the clock starts at the entry because a seat chooses its first commit | hours; production groups merged in the window | no target; down | none (`flow_metrics.py` prints merge hours only). R11-PRE-ROUND-METRICS |
| `closure_slip` | 2 | days the forecast closure moved later per day of plan history after the register | days per day; beside it round start to closure in days, and the groups deferred out | the owner's ceiling; down | none: the history exists only inside rendered plan pages. R11-PRE-ROUND-METRICS |
| `tokens_per_change` | 3 | every usage field of every seat (orchestrator, local, cloud) summed over the window, over production merges; one unledgered seat class makes the term NO-READ, never a partial | tokens per production merge; beside it the round total and the coordination share | no target; down | none. R11-PRE-TOKEN-LEDGER |

**Comparing two rounds, or a change's before and after.** A term **moved**
only beyond its band: for a count, a difference above twice the square root of
the two counts' sum; for a share, two standard errors of its denominator; for
`lead_time`, `closure_slip` and `tokens_per_change`, the owner's percentage.
Inside the band it is a tie.

1. **Layer 1 is never traded.** A change that moves any layer-1 term the wrong
   way is refused whatever else it gains; only the owner accepts one, by card.
   Targets give the direction: a round holds layer 1 when no term is worse.
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
| `regret` | 0 against the same-information oracle | forecast error in price and weather, sensor error and the pump's limits, all inside the foresight bound |
| `operation` | every cell as documented | what the pump does behind an acknowledged write |
| `generality` | every cell examined | cells no source reaches: no bundle, no contributor, and a simulation only as faithful as `tests/ha_contract.py` records the stub to be |
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

`objective.json` maps each class to the files that are its objects. An object
is **better** when its yield per cost rose with layer 1 held.

| class | cost | yield | scorable at round 10's close |
|---|---|---|---|
| dimension brief | its finder and verifier seats' tokens and wall clock | removed bugs it found; its `coverage`; less its `escapes` | found and escapes yes (judge record; escapes by hand); cost NO-READ until the token ledger keys a seat by dimension |
| role contract | its tokens times the seats that load it | the seat's first-pass yield and real-catch incidence (`review_strength.py`) per role | per role in part; per clause never, until a block's class names the clause |
| rule | its tokens times its loads, and the seconds of its refusals | its bug class's instances after the rule merged | no: `bugclasses.json` records no instance date and nothing counts a load |
| instrument | its lines, its run seconds, the hotfix groups naming it | refusals a fix followed, or lead time removed | cost yes (roster, `wc`); yield NO-READ until a refusal is logged with its outcome |
| gate (a workflow) | runner seconds per merge (`governance_cost.py`) and reds no product fault caused | reds a product fault caused | cost yes; yield NO-READ until a red carries its cause |
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
| every finding was fixed correctly | findings open at the close; fixed findings reported again | measured only once a re-report names the fix it follows |
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

## 5. Honesty

- **Held-out checks are not terms**, so no seat is scored on them. *Planted
  defects*: objective bugs written into the baseline export by a seat that is
  neither finder, orchestrator nor evaluator, their list outside the finder
  wall; recall is found / planted. *Two-finder overlap* (the owner's round-11
  trial): two seats on one universe finding n1 and n2 with m shared estimate
  (n1 + 1)(n2 + 1) / (m + 1) - 1 bugs there. Neither has an instrument or a
  roster group yet; until one does the assumptions they sense are unverified
  and section 4 is claimed for no round.
- **A process change is kept only on a measured before and after of the term
  it named, with the null control** that the same read does not move where the
  change is absent. From round 12; in round 11 the evaluation reports only.
- **The yardstick is the owner's.** This record, `objective.json`,
  `check_scopes.py`, each enumerator once built, and a round's evaluation and
  objective record are code-owned; no mandate scope covers them. An
  orchestrator proposes a refinement as a card and never edits them. Adding a
  term or an object class removes one.

| term | the cheapest false move | what catches it |
|---|---|---|
| `escapes` | rule a report not objective, or own it by `none`; release less often | the owner's reports count unless the owner rules otherwise; `none` is a `change` verdict on the dimension list; releases per day beside it; the overlap estimate |
| `regret` | choose easy grid cells; score against the optimizer's own model of itself | the grid is D0's declared scope with its denominator; the flat-price null; the measured-against-modelled gap from a live bundle |
| `operation` | drive only the idle plan | the plan states are part of the cell |
| `generality` | narrow the supported population; count a stub run as an install | the population is the owner's; each cell names its evidence kind |
| `unowned` | assign every report to the nearest dimension | the dimension's `escapes` then rises and its brief owes the step; the reviewer attacks the attribution |
| `unexamined` | relabel a feature as a fix | a fix names the judged finding it closes |
| `first_pass` | approve weakly; settle a block outside the verdict bus | `injected` and `escapes` are read first; real-catch incidence beside it |
| `injected` | leave the cause unnamed | a hotfix or outside group names its cause or the commit that predates the window, checked in review; the hotfix proxy beside it |
| `product_green` | cancel a red run; move a check out of `gate` | the cancelled count is in the denominator's row; `gate`'s check count may not fall |
| `coverage` | declare a smaller universe; report examined unread | the universe is a command the reviewer re-runs; planted defects are spread over the declared and the natural universe |
| `lead_time` | enter the group late; split a group; skip review | the clock starts at the entry; layer 1 is read first; merged production lines per group beside it |
| `closure_slip` | pad the first forecast; defer scope | round start to closure and the deferred count beside it |
| `tokens_per_change` | split a change; run work in an unledgered seat | a change is a roster group; an unledgered class is NO-READ; the round total beside it |
| a verdict | keep everything | the reviewer re-runs the read behind every `remove` and three `keep`s; the unscored share is reported |

## 6. The step

Before a round's baseline is pinned, `dev/governance/roles/evaluator.md` runs:
one evaluator seat that is not the orchestrator and did not work the round it
grades, reviewed by a second seat as `fix-review.md` reviews a fixer, deciding
nothing — the owner decides each card. Every `unowned` item, and every
owner-decided result of section 1 with no written criterion, yields a card.

- **Reads**: the closing round's `OBJECTIVE.json` in its directory under
  `dev/audit/rounds/`, which the orchestrator writes at closure: per term a
  `value` with the `enumerator` that printed it, or `no_read` with the reason.
  Recording a read is not grading it; the evaluator re-runs each.
- **Writes**: `EVALUATION.json` in the opening round's directory: `round`,
  `reads`, `evaluator`, `reviewer`, `objects` (file to `verdict`, `evidence`,
  and `card` unless `keep`) and `cards` (id to the proposal, `decision`
  `accepted|rejected|deferred` in the owner's words, and `merged`, the commit
  of an accepted one).
- **Refuses**: `check_scopes.py --round N`, which `audit-find.js` runs at the
  baseline, exits 1 on a missing record, a term neither read nor NO-READ, an
  object without a verdict and evidence, one seat in both roles, a card with
  no decision, or an accepted card not merged at the baseline.

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
- The planted-defect and overlap instruments are unowned: round 11's first
  evaluation cards them.
