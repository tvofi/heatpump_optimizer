# Review packet #3740
head: 42115f2c1421ece1aae4dc69b2ba4f0f0f261928
base: 8751943e17ef4d3ec699e7859ae829b4528d8ce7

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: red
CodeQL id=135073874199 success
arch-score / arch-score id=135063588457 success
arm id=135050454478 skipped
budget-raise-gate / budget-raise-gate id=135063588779 success
cancel-superseded id=135050447919 success
codeql / Analyze (actions) id=135063588501 success
codeql / Analyze (javascript-typescript) id=135063588475 success
codeql / Analyze (python) id=135063588565 success
governance / env-matrix id=135063588693 success
governance / instrument-self-tests id=135063588662 success
governance / policy-docs id=135063588653 success
governance / record id=135063591953 skipped
governance / wave-script id=135063588521 success
hassfest / hassfest id=135063588393 success
kernel-points id=135063591384 skipped
prelude id=135050448111 success
refresh id=135050447704 success
tests / arch-instrument id=135076487468 success
tests / briefs id=135063588589 success
tests / browser id=135076487392 success
tests / claims-autofix id=135084745744 skipped
tests / closure-scope id=135063588649 success
tests / closures id=135076487440 in_progress
tests / coverage id=135076487326 success
tests / coverage-ratchet id=135083177392 success
tests / fast (3.14) id=135076487342 success
tests / graders-head-copy id=135083177468 queued
tests / lane-proofs id=135086500583 queued
tests / mutation id=135063588550 success
tests / mutation-autofix id=135076174185 skipped
tests / mutation-pins id=135076174144 skipped
tests / nightly-ha id=135076489947 skipped
tests / nightly-status id=135063588426 failure
tests / replay id=135076489530 skipped
tests / typing id=135076487393 success
validate / validate-hacs id=135063588786 success

## Refusals
none

## Advisories
none

## carry_audit at the head
CARRY-AUDIT: 0 finding item(s): 0 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
FIGURES: 0 resolved, 0 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
none

## Review scope: full (first round: no --reviewed-head)

## Three-dot diff
diff --git a/dev/audit/config/objective.json b/dev/audit/config/objective.json
index 1e83a403bd..2ff0ee6ae6 100644
--- a/dev/audit/config/objective.json
+++ b/dev/audit/config/objective.json
@@ -260,7 +260,7 @@
    "unit": "L",
    "basis": "the hot-water tank row of the options flow: config_flow.py's CONF_DHW_TANK_VOLUME field, _number(50, 1500, 10, 'L'), its default const.py's DEFAULT_DHW_TANK_VOLUME (200.0). The buffer and wood tank rows are other options, not this axis.",
    "no_read": "the levels are declared here and nothing reads them: no reader compares them with the flow row they were taken from, so a moved row leaves them stale",
-   "builder": "R11-INTAKE-R10-RESIDUE"
+   "builder": "R11-READS-RESIDUE"
   },
   {
    "axis": "house_size",
@@ -281,7 +281,7 @@
    },
    "basis": "the heated-area row of the building questionnaire (config_flow.py's CONF_HEATED_AREA field, _number(20, 1000, 5, 'm²'), default const.py's DEFAULT_HEATED_AREA 140.0) and the heat-loss row (CONF_HOUSE_HEAT_LOSS_COEFFICIENT over RANGE_HOUSE_HEAT_LOSS (0.01, 1.0) kW/°C, default DEFAULT_HOUSE_HEAT_LOSS_COEFFICIENT 0.15; a two-zone install splits it over the upper and lower rows, defaults 0.08 + 0.07). Each level pairs the two rows' minimum, default or maximum: a declaration, since the flow lets them vary apart.",
    "no_read": "the levels are declared here and nothing reads them: no reader compares them with the flow rows they were taken from, so a moved row leaves them stale",
-   "builder": "R11-INTAKE-R10-RESIDUE"
+   "builder": "R11-READS-RESIDUE"
   }
  ],
  "objects": {
diff --git a/dev/audit/yardstick/round10/OBJECTIVE.json b/dev/audit/yardstick/round10/OBJECTIVE.json
index 745c2a99e7..292499a926 100644
--- a/dev/audit/yardstick/round10/OBJECTIVE.json
+++ b/dev/audit/yardstick/round10/OBJECTIVE.json
@@ -20,17 +20,17 @@
   "regret": {
    "no_read": "no same-information oracle and no realised-cost record per install-day exist; 0018 section 2 names no enumerator",
    "would_read": "the oracle harness raced per grid cell (D0's step) and the realised-cost record per install-day from a bundle (D15's step), with the model gap beside both",
-   "builder": "R11-INTAKE-R10-RESIDUE"
+   "builder": "R11-READS-RESIDUE"
   },
   "operation": {
    "no_read": "no cell ledger over write and hold sites times plan states",
    "would_read": "the actuator-write dimension's cell ledger: each write and hold site (`git grep -n \"async_call(\" custom_components/` lists the candidates) times idle, partial, boost, hot-water only and first cycle after an upgrade, with the plan's target and the value written",
-   "builder": "R11-INTAKE-R10-RESIDUE"
+   "builder": "R11-READS-RESIDUE"
   },
   "generality": {
    "no_read": "the examined count has no enumerator: no cell ledger names a cell with its source and asserting test",
    "would_read": "D12's cell ledger over the levels and pairs the denominator command prints",
-   "builder": "R11-INTAKE-R10-RESIDUE",
+   "builder": "R11-READS-RESIDUE",
    "beside": {
     "denominator": {
      "levels": 195,
@@ -44,7 +44,7 @@
   "unowned": {
    "no_read": "0018 section 2 names no enumerator: read off `escapes` once it records its owner, and `escapes` is itself read by hand",
    "would_read": "the escapes record with found-by and owning dimension; until then the `none` rows of dev/audit/rounds/round10/objective/escapes_hand.tsv",
-   "builder": "R11-INTAKE-R10-RESIDUE",
+   "builder": "R11-READS-RESIDUE",
    "by_hand": {
     "count": 7,
     "ledger": "dev/audit/rounds/round10/objective/escapes_hand.tsv",
@@ -63,7 +63,7 @@
   "escapes": {
    "no_read": "0018 section 2 names no enumerator; the roster records no found-by and no owning dimension",
    "would_read": "the escapes record with found-by and owner per group, and the window series R11-PRE-ROUND-METRICS prints",
-   "builder": "R11-INTAKE-R10-RESIDUE",
+   "builder": "R11-READS-RESIDUE",
    "by_hand": {
     "in_window": 26,
     "by_owner_report": 15,
@@ -94,7 +94,7 @@
   "injected": {
    "no_read": "0018 section 2 names no enumerator: no cause recorded per fixing group by the root-cause seat",
    "would_read": "the cause named on each fixing group, recorded by the root-cause seat, over production merges in this window and the previous",
-   "builder": "R11-INTAKE-R10-RESIDUE",
+   "builder": "R11-READS-RESIDUE",
    "by_hand": {
     "bugs_with_a_named_cause": 4,
     "bugs": {
@@ -118,7 +118,7 @@
   "coverage": {
    "no_read": "no finder report row carries examined over universe, so no step's share can be read",
    "would_read": "the per-step universe and examined count in each dimension's reports, each universe printed by a named command",
-   "builder": "R11-INTAKE-R10-RESIDUE"
+   "builder": "R11-READS-RESIDUE"
   },
   "unexamined": {
    "no_read": "no examining pass reports its universe over a late merge, and the roster's group kinds are not read by any tracked command",
diff --git a/dev/governance/decisions/0018-objective-function.md b/dev/governance/decisions/0018-objective-function.md
index 8fa9a66791..828524e444 100644
--- a/dev/governance/decisions/0018-objective-function.md
+++ b/dev/governance/decisions/0018-objective-function.md
@@ -55,21 +55,21 @@ is what no reader of this record can remove.
 | dimension | its perfect result | decided by | enumerator of the distance | floor |
 |---|---|---|---|---|
 | D0 price optimality | zero `regret` on every cell of its grid | measurement | the same-information oracle of this section, raced per cell of `tests/profiles.py`'s price shapes and climates: `python3 -I tools/audit/regret_oracle.py grid`; R11-PRE-PRODUCT-READS. Proxy: `tests/optimality.py` reads the solver against its own model | `regret`'s |
-| D1 robustness | no wedge, leak, race, stale read or lost store on any enumerated lifecycle path, store, timer, listener or guard | measurement | NO-READ: a census printing each path, store, timer, listener and guard with the test that drives it; R11-INTAKE-R10-RESIDUE | none |
-| D2 mathematical and physical sanity | every identity holds over its stated operating grid; every constant justified | measurement | NO-READ: the identities and their grid are named in no tracked list; R11-INTAKE-R10-RESIDUE | none |
+| D1 robustness | no wedge, leak, race, stale read or lost store on any enumerated lifecycle path, store, timer, listener or guard | measurement | NO-READ: a census printing each path, store, timer, listener and guard with the test that drives it; R11-READS-RESIDUE | none |
+| D2 mathematical and physical sanity | every identity holds over its stated operating grid; every constant justified | measurement | NO-READ: the identities and their grid are named in no tracked list; R11-READS-RESIDUE | none |
 | D3 test-suite gaps | every guard site pinned by a test that imports the production symbol and whose oracle is not the code under test | measurement | `python3 tests/mutation_table.py --scope full`: surviving mutants and unpinned sites | equivalent mutants, each triaged by name |
 | D4 UI/UX | every page, state and flow step renders and works in every shipped language and stated environment; beyond that, the owner's acceptance criteria | measurement, then the owner | `node tests/card_browser.mjs` for rendering; the rest undecided until `owner_criteria.D4` is set | none |
 | D5 docs structure and comments | the owner's acceptance criteria | the owner | undecided until `owner_criteria.D5` is set | none |
 | D6 claim verification | every claim in the README, docs, strings and release notes is true of the code, and every required user action is stated | measurement | `python3 tests/doc_claims.py` for the claims it registers; NO-READ for a claim outside its register: R10-D5-D6-FULL-SCOPE | none |
 | D7 architecture | the programme target of decision 0015 met with no gate metric risen | the owner's target | `python3 tests/structure.py` and `python3 tools/audit/archscore/score.py --diff` against the target of `owner_criteria.D7` | none |
-| D8 sensors | every entity publishes the right value, in the right order, with its true reason, in every language | measurement | NO-READ: `python3 tests/entities.py` pins the entities it collects, and nothing prints entity by state by language with the pinning test; R11-INTAKE-R10-RESIDUE | none |
+| D8 sensors | every entity publishes the right value, in the right order, with its true reason, in every language | measurement | NO-READ: `python3 tests/entities.py` pins the entities it collects, and nothing prints entity by state by language with the pinning test; R11-READS-RESIDUE | none |
 | D9 efficiency | every cost centre inside the owner's Pi-class budget | the owner's budget | undecided until `owner_criteria.D9` is set; `tests/stress.py` then reads the cost | the solver's work at the planning horizon |
 | D10 quality scale | every rule of the owner's target tier met at every site | the owner's tier | undecided until `owner_criteria.D10` is set; `quality_scale.yaml` in the integration's directory then lists each rule's state | rules Home Assistant adds after the baseline |
-| D11 governance mechanisms | every mechanism fires when it should and only then | measurement | `node tools/policy/policy_lint_mutants.mjs` and each instrument's `--self-test`; NO-READ for a mechanism with neither: R11-INTAKE-R10-RESIDUE | none |
+| D11 governance mechanisms | every mechanism fires when it should and only then | measurement | `node tools/policy/policy_lint_mutants.mjs` and each instrument's `--self-test`; NO-READ for a mechanism with neither: R11-READS-RESIDUE | none |
 | D12 generalization | `generality` at 1 | measurement over the supported population | the denominator: `python3 tools/audit/check_scopes.py --population`; the examined count: the cell ledger, each row counted only on the read's own witness, `python3 -I tools/audit/product_reads.py generality --ledger <ledger>`; R11-PRE-PRODUCT-READS | `generality`'s |
 | D13 process yield and cost | the process terms of section 2 at their end state | measurement | section 2's enumerators | section 2's residuals |
 | D14 recurring bug classes | no open class, no instance of a barriered class | measurement | `python3 tools/audit/fold_ledger.py check` over `dev/audit/config/bugclasses.json` | none |
-| D15 live diagnostics | every bundle replays with no unexplained divergence | measurement | `python3 tools/replay/debug_replay.py --bundle` per bundle; the bundle set is NO-READ (no tracked list of the installs that sent one): R11-INTAKE-R10-RESIDUE | installs that send no bundle |
+| D15 live diagnostics | every bundle replays with no unexplained divergence | measurement | `python3 tools/replay/debug_replay.py --bundle` per bundle; the bundle set is NO-READ (no tracked list of the installs that sent one): R11-READS-RESIDUE | installs that send no bundle |
 
 Where the third column names the owner, the criterion is the tracked file
 `objective.json` names under `owner_criteria`; a null there makes the result
@@ -192,7 +192,7 @@ class.
 | `escapes` | 1 | objective bugs in a released product version, reported in the window by anyone but the round's finder seats, each with who found it and the owning dimension (`none` is a value) | bugs per round; beside it the removed count (verified findings whose group merged) and removed / (removed + escapes), whole and per dimension | 0; down | none. R11-PRE-ROUND-METRICS records found-by and owner and prints the series. `scorecard.py` line `E` is a proxy with no window and no owner |
 | `injected` | 1 | objective bugs whose cause is a pull request merged in this window or the previous one, named on the fixing group | bugs per 100 production merges | 0; down | none; same two groups. Proxy: production hotfix merges over production merges (`scorecard.py` line `H`) |
 | `product_green` | 1 | share of main's concluded `CI` push runs in the window whose `gate` job succeeded | share; concluded runs, the cancelled count beside it | `thresholds.product_green_floor`; up | `scorecard.py report` line `A_gate`, which reads the last 20 and has no input producer: R11-PRE-ROUND-METRICS feeds it and adds the window |
-| `coverage` | 1 | per dimension, the least examined / universe over its steps, each universe printed by a named command; a step reporting none, and a dimension not run, count 0 | share; the dimension count | 1 in every dimension; up | none. R11-INTAKE-R10-RESIDUE (the denominator rule) |
+| `coverage` | 1 | per dimension, the least examined / universe over its steps, each universe printed by a named command; a step reporting none, and a dimension not run, count 0 | share; the dimension count | 1 in every dimension; up | none. R11-READS-RESIDUE (the denominator rule) |
 | `unexamined` | 1 | production merges after the baseline that no finder pass examined before the round's close (a feature, an outside change, a fix's own diff) | share; production merges in the window | 0; down | none. R11-PRE-ROUND-METRICS, from the roster's group kinds |
 | `first_pass` | 2 | share of merged pull requests whose first verdict was `merge` | share; reviewed merges in the window | 1; up | `tools/audit/seat/flow_metrics.py --window`; `review_strength.py --window` |
 | `lead_time` | 2 | hours from a production group's roster entry to its merge on main, p50 and p90; the clock starts at the entry because a seat chooses its first commit | hours; production groups merged in the window | no target; down | none (`flow_metrics.py` prints merge hours only). R11-PRE-ROUND-METRICS |
@@ -316,7 +316,7 @@ One round yields the code of section 1 only if every link holds:
 |---|---|---|
 | every item in scope was examined | `coverage`, `generality` | 0 at coverage 1 over an enumerable universe; otherwise the unexamined share |
 | every real defect in an examined item was found | the planted-defect recall (section 5) | 1 less the recall; unmeasured today, and never 0 for a finder that is a model |
-| every finding was fixed correctly | findings open at the close; fixed findings reported again | NO-READ, and in no term: `injected` counts a new defect, never a fix that did not fix. It is read once a re-report names the fix it follows: R11-INTAKE-R10-RESIDUE |
+| every finding was fixed correctly | findings open at the close; fixed findings reported again | NO-READ, and in no term: `injected` counts a new defect, never a fix that did not fix. It is read once a re-report names the fix it follows: R11-READS-RESIDUE |
 | no fix injected a defect | `injected` | its rate per fix |
 | nothing unexamined merged before the close | `unexamined` | its share |
 | the dimension set is complete | `unowned` | unknowable from inside; `unowned` is its lower bound |
@@ -433,9 +433,9 @@ ranking a change.
 | `operation` | drive only the idle plan; edit the documented target to match the code | the plan states are part of the cell, and the target is the plan's computed value, which no document edit moves; a row counts only when the read moved its site in a pass of the cell's plan state, `python3 -I tools/audit/product_reads.py operation --ledger <ledger>`, R11-PRE-PRODUCT-READS |
 | `generality` | narrow the supported population; count a stub run as an install; examine a cell with a run that asserts nothing | live: the population is `check_scopes.py --population` over the code's own tuples, so narrowing it is a product change. a level row counts only when the read's own run with that level switched moves its asserting test, `python3 -I tools/audit/product_reads.py generality --ledger <ledger>`, R11-PRE-PRODUCT-READS; planted configuration defects, R11-PRE-ROUND-METRICS |
 | `unowned` | assign every report to the nearest dimension | beside: the dimension's `escapes` then rises and its brief owes the step; the reviewer attacks the attribution |
-| `unexamined` | relabel a feature as a fix; mark a late merge examined by a pass that only says it read it | beside: a fix names the judged finding it closes. NO-READ: an examining pass reports its universe and denominator over the late diff like any step (`coverage`'s rule), R11-INTAKE-R10-RESIDUE |
+| `unexamined` | relabel a feature as a fix; mark a late merge examined by a pass that only says it read it | beside: a fix names the judged finding it closes. NO-READ: an examining pass reports its universe and denominator over the late diff like any step (`coverage`'s rule), R11-READS-RESIDUE |
 | `first_pass` | approve weakly; settle a block outside the verdict bus | beside: real-catch incidence (`review_strength.py --window`). NO-READ: `injected` and `escapes`, its two catchers; until both are read `first_pass` ranks nothing (section 2) |
-| `injected` | leave the cause unnamed; the fixing group names a cause that spares its own predecessor | beside: the cause is checked in review; the hotfix proxy. NO-READ: the cause recorded by the root-cause seat, which is not the fixer, R11-INTAKE-R10-RESIDUE |
+| `injected` | leave the cause unnamed; the fixing group names a cause that spares its own predecessor | beside: the cause is checked in review; the hotfix proxy. NO-READ: the cause recorded by the root-cause seat, which is not the fixer, R11-READS-RESIDUE |
 | `product_green` | cancel a red run; move a check out of `gate` | beside: the cancelled count is in the denominator's row. NO-READ: `gate`'s check count per window, R11-PRE-ROUND-METRICS |
 | `coverage` | declare a smaller universe; re-run a command that prints a narrow universe; report examined unread | live: `check_scopes.py` refuses a tracked path in no universe. NO-READ: planted defects spread over the natural universe, not the declared one, R11-PRE-ROUND-METRICS |
 | `lead_time` | enter the group late, when its fixer is ready; split a group; skip review | beside: merged production lines per group. NO-READ: the clock read from the commit that added the group to the roster, never from a field the orchestrator fills, and the gap from the finding's judged date to that commit beside it, R11-PRE-ROUND-METRICS |
@@ -507,7 +507,7 @@ request).
 - Round 11 cannot start until round 10's objective record and round 11's
   evaluation are on main; with no enumerator built most terms are NO-READ,
   which is the baseline.
-- R11-PRE-ROUND-METRICS, R11-PRE-TOKEN-LEDGER, R11-PRE-PRODUCT-READS and R11-INTAKE-R10-RESIDUE
+- R11-PRE-ROUND-METRICS, R11-PRE-TOKEN-LEDGER, R11-PRE-PRODUCT-READS and R11-READS-RESIDUE
   build to the definitions above; a definition an instrument cannot meet
   returns here as a card, never as a quiet redefinition.
 - Round 11's first evaluation holds a card per unset value of
diff --git a/dev/programme/RULINGS.md b/dev/programme/RULINGS.md
index 3d0a3a7d31..635a2e86f3 100644
--- a/dev/programme/RULINGS.md
+++ b/dev/programme/RULINGS.md
@@ -102,6 +102,16 @@ divergence"). Re-read on change after every compaction
   carries from the previous round."
 - 2026-11-13: "outside and owner filed findings and requests should always fold
   into the ongoing round if not explicitly deferred by the owner or outsider".
+- 2026-11-18, on round-11 plan revision 4 (`plan/r11` at 50a932de3b, approved
+  by plan review at `plan-verdict/r11` 4494289c0e): "go with all three points".
+  The three points, as recorded: (1) revision 4 is applied to the round-11
+  roster, every row of `CHANGES-R3.md` and `CHANGES-R4.md`; (2) carry 182 of
+  R11-INTAKE-R10-RESIDUE (the heat-ask dither and closed-loop planner harness,
+  from R11-OUTSIDE-SELF-SETTING-PUMP) stays in round 11, re-homed to
+  R11-SEAM-learners, the live group owning `accuracy.py`; (3) R11-READS-RESIDUE
+  is an owner exception to the instrument freeze (card P11), and decision 0018,
+  `dev/audit/config/objective.json` and the round-10 baseline name it as the
+  builder in place of R11-INTAKE-R10-RESIDUE.
 
 ## The instrument freeze, proposals and root cause
 

## Before you return the verdict (P275)
Run `python3 -I tools/audit/carry_audit.py check --body <PR body file> --comments <file holding [{"id": 0, "body": <verdict.md text>}]>`. Give every reported item its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>`;
an evidence line flagged by its wording takes `Carry: dismissed: evidence, not a finding`. Return the verdict only at rc 0.
