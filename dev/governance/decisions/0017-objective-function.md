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

## 1. The function

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
| `escapes` | 1 | objective bugs in a released product version, reported in the window by anyone but the round's finder seats, each with who found it and the owning dimension (`none` is a value) | bugs per round; beside it the removed count (verified findings whose group merged) and removed / (removed + escapes), whole and per dimension | 0; down | none. R10-DIMENSIONS-FULL-COVERAGE records found-by and owner; R11-PRE-ROUND-METRICS prints the series. `scorecard.py` line `E` is a proxy with no window and no owner |
| `injected` | 1 | objective bugs whose cause is a pull request merged in this window or the previous one, named on the fixing group | bugs per 100 production merges | 0; down | none; same two groups. Proxy: production hotfix merges over production merges (`scorecard.py` line `H`) |
| `product_green` | 1 | share of main's concluded `CI` push runs in the window whose `gate` job succeeded | share; concluded runs, the cancelled count beside it | the owner's floor; up | `scorecard.py report` line `A_gate`, which reads the last 20 and has no input producer: R11-PRE-ROUND-METRICS feeds it and adds the window |
| `coverage` | 1 | per dimension, the least examined / universe over its steps, each universe printed by a named command; a step reporting none, and a dimension not run, count 0 | share; the dimension count | 1 in every dimension; up | none. R10-DIMENSIONS-FULL-COVERAGE (the denominator rule) |
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

## 2. Scoring an object

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

## 3. What the function going the right way implies

Let N be the objective bugs present at a round's start, p the least chance
that one is found in a round, q the bugs a fix injects per bug removed, and g
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
| g bounded | product lines added per round beside `escapes` | escapes owned by `none`, or in files newer than the previous baseline, move up |
| escapes are seen | releases per day; the two-finder overlap estimate | `escapes` falls while the estimate of remaining bugs does not |
| the oracle set is fixed | the dimension list | a dimension is added: its first round's finds are a new baseline, never a regression |
| fixes land before the next round | the closure criteria | a finding is open at the next baseline |

## 4. Honesty

- **Held-out checks are not terms**, so no seat is scored on them. *Planted
  defects*: objective bugs written into the baseline export by a seat that is
  neither finder, orchestrator nor evaluator, their list outside the finder
  wall; recall is found / planted. *Two-finder overlap* (the owner's round-11
  trial): two seats on one universe finding n1 and n2 with m shared estimate
  (n1 + 1)(n2 + 1) / (m + 1) - 1 bugs there. Neither has an instrument or a
  roster group yet; until one does the assumptions they sense are unverified
  and section 3 is claimed for no round.
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
| `injected` | leave the cause unnamed | a hotfix or outside group names its cause or the commit that predates the window, checked in review; the hotfix proxy beside it |
| `product_green` | cancel a red run; move a check out of `gate` | the cancelled count is in the denominator's row; `gate`'s check count may not fall |
| `coverage` | declare a smaller universe; report examined unread | the universe is a command the reviewer re-runs; planted defects are spread over the declared and the natural universe |
| `lead_time` | enter the group late; split a group; skip review | the clock starts at the entry; layer 1 is read first; merged production lines per group beside it |
| `closure_slip` | pad the first forecast; defer scope | round start to closure and the deferred count beside it |
| `tokens_per_change` | split a change; run work in an unledgered seat | a change is a roster group; an unledgered class is NO-READ; the round total beside it |
| a verdict | keep everything | the reviewer re-runs the read behind every `remove` and three `keep`s; the unscored share is reported |

## 5. The step

Before a round's baseline is pinned, `dev/governance/roles/evaluator.md` runs:
one evaluator seat that is not the orchestrator and did not work the round it
grades, reviewed by a second seat as `fix-review.md` reviews a fixer, deciding
nothing — the owner decides each card.

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
