# Review packet #3260
head: 5b39c4111ca5ae464a607490c42d70c638af24a3
base: 28482eceeb6b9809e44b12d80fc994282cc21645

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: red
CodeQL id=128212114147 success
arch-score / arch-score id=128221319145 success
arm id=128211850677 skipped
budget-raise-gate / budget-raise-gate id=128221374698 success
cancel-superseded id=128221360613 success
codeql id=128221369175 skipped
codeql / Analyze (actions) id=128212038474 success
codeql / Analyze (javascript-typescript) id=128212038535 success
codeql / Analyze (python) id=128212038432 success
gate id=128221318581 failure
governance id=128221356562 skipped
governance / delivery-status id=128212038552 success
governance / delivery-status-publish id=128212039990 skipped
governance / env-matrix id=128212038529 success
governance / instrument-self-tests id=128212038492 success
governance / policy-docs id=128212038427 success
governance / record id=128212041180 skipped
governance / wave-script id=128212038506 success
hassfest id=128221368392 skipped
hassfest / hassfest id=128212038305 success
kernel-points id=128221318552 skipped
pr-contract id=128221320012 skipped
prelude id=128221366967 success
refresh id=128221362364 success
tests id=128221369844 skipped
tests / arch-instrument id=128212268014 in_progress
tests / briefs id=128212038396 success
tests / browser id=128212267929 success
tests / closure-scope id=128212038499 success
tests / closures id=128212267935 success
tests / closures-autofix id=128220511633 skipped
tests / coverage id=128212267900 in_progress
tests / fast (3.14) id=128212267891 in_progress
tests / mutation id=128212038407 success
tests / mutation-autofix id=128212372572 skipped
tests / mutation-pins id=128212371815 skipped
tests / nightly-ha id=128212269559 skipped
tests / nightly-status id=128212038354 success
tests / replay id=128212269419 skipped
tests / typing id=128212268015 success
validate id=128221319575 skipped
validate / validate-hacs id=128212038387 success

## Refusals
red-unanswered: concluded red check `gate` is not named in ## Red checks
required-red: required context `gate` concluded failure at 5b39c4111ca5ae464a607490c42d70c638af24a3

## Advisories
none

## carry_audit at the head
NOTE body item 728df1bf: dismissed:orientation only, each carry is answered below
NOTE body item 62b6e444: R10-BODY-CONTRACT
NOTE body item a223202b: dismissed:answered in this pull request
NOTE body item 939f3156: dismissed:built and pinned in this pull request
NOTE body item b9ffbdde: dismissed:3221 merged, this diff touches neither file
NOTE body item 106e7c34: R10-BODY-CONTRACT
NOTE body item 1d9246db: dismissed:answered in this pull request
NOTE body item 134797fc: dismissed:answered in this pull request
NOTE body item 5b54efca: dismissed:answered in this pull request
NOTE body item d46d43b2: dismissed:answered in this pull request
NOTE body item 7d9e145f: R10-BODY-CONTRACT
CARRY-AUDIT: 11 finding item(s): 11 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
ok         python3 -I tools/audit/carry_audit.py --self-test
             `tools/audit/carry_audit.py` is in the tree at this head
  ok         node tools/policy/brief_lint.mjs
             `tools/policy/brief_lint.mjs` is in the tree at this head
  unverified node -e "import('./tools/policy/brief_lint.mjs').then(m=>console.log(m.rosterIssues().size))"
             node runs an inline script rather than a file
  ok         python3 tests/structure.py
             `tests/structure.py` is in the tree at this head
  ok         python3 tests/entities.py
             `tests/entities.py` is in the tree at this head
  ok         python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)
             `tests/closure.py` is in the tree at this head
  unverified git grep -n FOLD_LINE tools/
             `git grep` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals

FIGURES: 5 resolved, 2 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
none

## Three-dot diff
diff --git a/dev/programme/carries/carry-1795.json b/dev/programme/carries/carry-1795.json
deleted file mode 100644
index ecfecb408..000000000
--- a/dev/programme/carries/carry-1795.json
+++ /dev/null
@@ -1,39 +0,0 @@
-{
-  "_comment": [
-    "Carry destination for R9-UX-5 (#1795, lane UX: advisor actions and exact idle sub-codes), from R9-UX-1 (#1795, why now, why not) and R9-UX-2 (#1795, advisor inbox).",
-    "The round-9 roster's R9-UX-5 group brief on handoff/audit-r9-fixplan should carry the same text; the roster is not on main,",
-    "so this file is the in-tree destination. While the two disagree the newer one is right. Shape: .claude/rules/finding-propagation.md."
-  ],
-  "issue": 1795,
-  "stage": "R9-UX-5, or any later seat that adds lines to the chart's hover tooltip (tooltipHtml, idleWhyHtml) or turns an advisor inbox row into an apply action (advisorRows, attachAdvisorInbox); and R9-UX-7 (model status and diagnostics, which adds to the Health tab), see the third entry",
-  "carries": [
-    {
-      "from": "the pull request for R9-UX-1, which put the idle step's likely-because block in the tooltip",
-      "effect": "narrows",
-      "control": "Established by measurement with its null control in tests/card_browser.mjs's P9 grid, in Chromium. With the tooltip capped at the chart's height by max-height and overflow: hidden, the check 'P9 grid: no text is clipped where its ancestor cannot scroll to it' went red on the explanation's li runs in the tooltip_hover cell; the same grid is green with fitWhy, which omits the explanation's last lines instead (the control). Without either, the box ran below the chart on a 400 px card (a probe measured the box's bottom past the chart wrapper's), which the P9 pop-up check did not see because it bounded a tooltip by its chart horizontally only.",
-      "remeasure": "Do not trust these figures: they were measured at the UX-1 code head, and a later stage is judged against its own merge base. Run tests/card_browser.mjs and read the two P9 checks named here; then hover the dearest idle step on a narrow card and compare the tooltip's box with its .chartwrap's.",
-      "brief": "The hover tooltip cannot scroll, so it may not clip text (P9 refuses overflow: hidden on it), and since R9-UX-1 the P9 pop-up check also holds a tooltip inside its chart's height. Exact idle sub-codes replace the likely-because lines in idleWhyHtml rather than adding a second block, and anything that does not fit is omitted by fitWhy, last line first, never clipped. Put the most telling line first, because on a small card it is the one that survives."
-    },
-    {
-      "from": "the pull request for R9-UX-2, which put the advisor inbox on the Advisor tab",
-      "effect": "removes",
-      "control": "Established by tests/card.mjs's scenario 'the advisor inbox (R9-UX-2, #1795)': the hot-water row has act open_schedule, which only sets dialog.page to plan and calls no service (check 'the hot-water row opens the schedule editor, and calls no service'). Null control: the valve row's apply_valve calls assign_entity with a manual setpoint, so a row that applies something is already pinned there.",
-      "remeasure": "Do not trust this description of the code: read advisorRows and attachAdvisorInbox in the card at your merge base and run node tests/card.mjs; the hot-water check above is the one that must change.",
-      "brief": "R9-UX-5 turns the hot-water row's Open schedule action into an apply action: the row's act becomes a service call that writes the recommended setpoint, the Plan-page fallback goes, and the check that the row calls no service is rewritten to pin the call. Price of a degree is delivered by R9-UX-2 as the degree row, whose action opens the what-if panel seeded with the tile's target; nothing is owed on it. A hot-water price is interpolated linearly between the swept candidates (dhwCostPerDay) because the default setpoint is off the sweep's grid; an apply action must write the recommended setpoint, not an interpolated one."
-    },
-    {
-      "from": "the pull request for R9-UX-3, which put the Health tab on the card",
-      "effect": "removes",
-      "control": "Established by tests/card.mjs's scenario 'the Health tab (R9-UX-3)': the card lists a waiting sensor from its unavailable state and a fixed per-sensor reason (HEALTH_WAITING), because Home Assistant publishes no attributes for an unavailable entity, so waiting_for is unreadable by the card at the moment it matters. Null control: with the sensor available the row does not appear, and the card reads nothing from the unavailable sensor's attributes.",
-      "remeasure": "Do not trust this description of the code: read healthPageHtml and HEALTH_WAITING in the card at your merge base and run node tests/card.mjs. Three facts the Health tab could not read, each re-checked at your merge base: the plan's fallback input ('the plan uses X instead') is not published; a count of insight sensors that are off by default has no card-side source (the card has no entity registry, and tests/entities.py refuses card reads of disabled-by-default sensors); the Input Problem sensor's limit (max_age_minutes) is published only for a failing input.",
-      "brief": "R9-UX-7 adds model status to the Health tab and must not expect waiting_for from an unavailable sensor: if it needs the reason in words it publishes it on an always-available enabled sensor (a per-sensor map, or a field on an existing one), or keeps the card's per-sensor reason map in step with any sensor it adds to HEALTH_WAITING. A row that needs the fallback input, the default-off insight count or the limit of a healthy input needs the backend to publish it first; the Health tab shows those rows as plain text today and says so in docs/dashboard-card.md. Where this entry and the roster's R9-UX-7 brief disagree, the newer is right and the other is the bug."
-    },
-    {
-      "from": "the pull request for R9-UX-4, which added the notifier module and its five events",
-      "effect": "narrows",
-      "control": "Established by tests/features.py's UX-4 block: the comfort-at-risk event carries predicted_min_c, at, floor_c and peak_guard_suppressing, and exactly the keys notifier.EVENT_DATA declares (check 'each event carries exactly the data keys the module declares'). No published field says why a step is cold; peak_guard_suppressing is the only cause the payload carries. Null control: the block's comfort plans carry no peak_guard_suppressing key at all and the event still fires (data value false), so the event is not tied to the guard.",
-      "remeasure": "Do not trust this description of the code: read _comfort and EVENT_DATA in notifier.py at your merge base and run the UX-4 block of tests/features.py. Re-check which cause fields the payload publishes once the idle sub-codes exist.",
-      "brief": "The design asks the comfort event for its why (\"the fuse limit caps heating 02:00-05:00\"). R9-UX-4 ships only peak_guard_suppressing, because the payload carried no per-step cause. When UX-5 publishes the exact idle sub-codes per step it also extends EVENT_DATA and the comfort detector to name the cause of the coldest step, in the event, in docs/automations.md's table and in the blueprint's message, which today says only that the peak guard is holding heating back. Where this entry and the roster's R9-UX-5 brief disagree, the newer is right and the other is the bug."
-    }
-  ]
-}
diff --git a/dev/programme/delivery/3260.md b/dev/programme/delivery/3260.md
new file mode 100644
index 000000000..5913919df
--- /dev/null
+++ b/dev/programme/delivery/3260.md
@@ -0,0 +1 @@
+- [#3260](https://github.com/tvofi/heatpump_optimizer/pull/3260) — **open**, R10-BODY-CONTRACT (part 2): body contract carries from #3227 (R10-BODY-CONTRACT)
diff --git a/dev/programme/rosters/wave-r9-groups.json b/dev/programme/rosters/wave-r9-groups.json
index 3ed5f824c..d81444983 100644
--- a/dev/programme/rosters/wave-r9-groups.json
+++ b/dev/programme/rosters/wave-r9-groups.json
@@ -6098,7 +6098,11 @@
    },
    "brief": "Round-9 feature PR UX-6 (lane UX, money and memory). Models: fixer opus (ledger and accuracy stores, a receipt defect with its failing test, and two card views); reviewer opus in another session; runner haiku; record sonnet. tvofi decided on 2026-09-30: U1 notifications are documented events plus a blueprint, no option fields; U2 the trust replay is the full day-ahead replay; U3 the shared household power budget is deferred beyond round 9 as a feature request; U4 \"the budgets are in place to make sound architectural decisions, they can be raised as a last resort if payment does not yield better code, after codeowner approval\"; U5 \"make sure that the finished card pages gets described with screenshots in the documentation\". First rule: before any work, read CLAUDE.md and every rules file it references (.claude/rules, the role contract tools/audit/briefs/fixer.md), and follow them; pass this rule on in every sub-agent brief. Never call the owner anything but tvofi, in commits, PR bodies, comments and delivery notes; the PR attribution line is _Requested by **tvofi**_. Design of record: handoff/round9/state/alt/design/ux/DESIGN-UX.md and the pre-study handoff/round9/state/alt/design/ux/PRE-STUDY-UX.md (at 1a90e4cb on handoff/audit-r9-alt), with the mockups and CONTRAST.json beside them, built on the lane-UI design of record handoff/round9/state/alt/design/DESIGN.md (at 7bca8ab3); where this brief and those files disagree, the newer is right and the other is the bug. This is a new production feature, not a finding: there is no class, no barrier and no RCA, except where this brief names a defect to fix with its failing test first. Value-bearing goldens stay byte-identical unless this brief says otherwise; moved card states are claimed in tests/golden/card_claimed_drift.txt with claims-for equal to VERSION, never re-recorded (CLAUDE.md rule 3). Scope, per DESIGN-UX.md section UX-6 and PRE-STUDY-UX.md item 3: (1) defect, failing test first: the monthly receipt's total_sek sums every line except the reasons, so it counts spot together with the space and dhw lines that split it and the two savings lines (_freeze_month_report in custom_components/heatpump_optimizer/coordinator.py, lines booked at its space line and in ledger.py's savings lines); (2) the receipt freeze moves out of the coordinator into custom_components/heatpump_optimizer/ledger.py as a pure, tested function, its sound home, which also pays for this PR's call sites; (3) the capacity charge is booked as a ledger line before the peak tracker resets at month change, so a receipt can name it; (4) every receipt kept (24 months) is published unrecorded on the enabled monthly-savings sensor; (5) a daily snapshot of the plan's promise (the room trajectory and the cost, taken at a fixed hour) is kept beside the accuracy history in custom_components/heatpump_optimizer/accuracy.py's store, bounded, and published unrecorded (decision U2); (6) the Savings tab shows the receipt with a sentence saying what it covers, the cost by reason, and \"Yesterday: the plan against reality\" in the concept-A panel style (promise dashed, measurement solid, shared time axis, colours of record). Also correct the stale comment in _learning_view that still describes the fixed heat-loss defect (#110). After R9-EG-B7 (coordinator.py), R9-EG-B11 (sensor.py) and R9-UX-5 (the card). R9-UX-7 is a sibling with no edge: both edit the card and sensor.py in different functions, and whichever merges second merges main. Must keep working: the monthly savings table and its estimate badge. Documentation (U5): regenerate, with the browser test's page-screenshot mode that R9-UI-3 lands, the screenshots of every card page this PR changes, light and dark, into docs/img/card, and describe the page in docs/dashboard-card.md in the same PR; never hand-capture a screenshot, so the docs stay true to the code (D6). Budgets (U4, CLAUDE.md rule 2): design to fit first, putting new logic where it belongs architecturally rather than in the coordinator; pay for lines only where the payment is itself the better design, never by deleting working functionality or shuffling lines to meet a number; a raise is the last resort, and then the body shows why payment would not give better code and tvofi confirms the raise as code owner before the push, and it merges only on tvofi's approving review (budget-raise-gate). The 2026-09-29 mandate does not pre-confirm raises for this lane: ask on #201, and while it waits the orchestrator keeps dispatching everything else. Run python3 tests/structure.py before every hand-off and re-measure at your own merge base; carry no number. Standing: cloud seat: no PRs, no GitHub comments, no issues, no gh; hand the branch and body off on your handoff branch and the Mac orchestrator pushes as the hpo-author App via tools/audit/app_push.sh; hpo-approver approves a non-code-owned PR, tvofi reviews a code-owned one (decision 0011). Mutation: pin the sites this change adds (mutation_table.py --scope changed --base origin/main); --max 0 is never proof. Resumability (tvofi 19:05Z): commit and push to your handoff branch at every step boundary and at least every 30 minutes, update the resume note in this entry's resume field with every push, and append one dated line per milestone to the round-9 resume log. No VERSION, manifest version or notes-heading edits. Part of #201; issues stay empty until the orchestrator files the lane's feature issue. Carry from roster rev 4.2 (tvofi's product page, 2026-09-30; design of record handoff/round9/state/alt/design/site/DESIGN-SITE.md at 2b5031bf): decision U5 extends to the product page: a card page whose screenshot this PR adds or regenerates takes its gallery slot on the page in the same PR (DESIGN-SITE.md, gallery slots), with the caption quoted from its section of docs/dashboard-card.md. A README feature paragraph this PR adds or removes is forced onto or off the page by the doc_claims.py page arm.",
    "carry": [
-    "From R9-EG-A4 (stacked, handoff/r9-eg-a4): once the arch-score required check lands, a typing-only change can show a coordinator footprint rise (annotated aliases and bare returns count as logic until #1867's measuring fault fix is on main). If the gate reports a rise, add an '## Architecture score' line to the body naming the metric and why; the fix review judges the reason."
+    "From R9-EG-A4 (stacked, handoff/r9-eg-a4): once the arch-score required check lands, a typing-only change can show a coordinator footprint rise (annotated aliases and bare returns count as logic until #1867's measuring fault fix is on main). If the gate reports a rise, add an '## Architecture score' line to the body naming the metric and why; the fix review judges the reason.",
+    "From carry-1795 (#1795, moved here from the carry file; the pull request for R9-UX-1, which put the idle step's likely-because block in the tooltip; effect: narrows): The hover tooltip cannot scroll, so it may not clip text (P9 refuses overflow: hidden on it), and since R9-UX-1 the P9 pop-up check also holds a tooltip inside its chart's height. Exact idle sub-codes replace the likely-because lines in idleWhyHtml rather than adding a second block, and anything that does not fit is omitted by fitWhy, last line first, never clipped. Put the most telling line first, because on a small card it is the one that survives. Control: Established by measurement with its null control in tests/card_browser.mjs's P9 grid, in Chromium. With the tooltip capped at the chart's height by max-height and overflow: hidden, the check 'P9 grid: no text is clipped where its ancestor cannot scroll to it' went red on the explanation's li runs in the tooltip_hover cell; the same grid is green with fitWhy, which omits the explanation's last lines instead (the control). Without either, the box ran below the chart on a 400 px card (a probe measured the box's bottom past the chart wrapper's), which the P9 pop-up check did not see because it bounded a tooltip by its chart horizontally only. Remeasure: Do not trust these figures: they were measured at the UX-1 code head, and a later stage is judged against its own merge base. Run tests/card_browser.mjs and read the two P9 checks named here; then hover the dearest idle step on a narrow card and compare the tooltip's box with its .chartwrap's.",
+    "From carry-1795 (#1795, moved here from the carry file; the pull request for R9-UX-2, which put the advisor inbox on the Advisor tab; effect: removes): R9-UX-5 turns the hot-water row's Open schedule action into an apply action: the row's act becomes a service call that writes the recommended setpoint, the Plan-page fallback goes, and the check that the row calls no service is rewritten to pin the call. Price of a degree is delivered by R9-UX-2 as the degree row, whose action opens the what-if panel seeded with the tile's target; nothing is owed on it. A hot-water price is interpolated linearly between the swept candidates (dhwCostPerDay) because the default setpoint is off the sweep's grid; an apply action must write the recommended setpoint, not an interpolated one. Control: Established by tests/card.mjs's scenario 'the advisor inbox (R9-UX-2, #1795)': the hot-water row has act open_schedule, which only sets dialog.page to plan and calls no service (check 'the hot-water row opens the schedule editor, and calls no service'). Null control: the valve row's apply_valve calls assign_entity with a manual setpoint, so a row that applies something is already pinned there. Remeasure: Do not trust this description of the code: read advisorRows and attachAdvisorInbox in the card at your merge base and run node tests/card.mjs; the hot-water check above is the one that must change.",
+    "From carry-1795 (#1795, moved here from the carry file; the pull request for R9-UX-3, which put the Health tab on the card; effect: removes): R9-UX-7 adds model status to the Health tab and must not expect waiting_for from an unavailable sensor: if it needs the reason in words it publishes it on an always-available enabled sensor (a per-sensor map, or a field on an existing one), or keeps the card's per-sensor reason map in step with any sensor it adds to HEALTH_WAITING. A row that needs the fallback input, the default-off insight count or the limit of a healthy input needs the backend to publish it first; the Health tab shows those rows as plain text today and says so in docs/dashboard-card.md. Where this entry and the roster's R9-UX-7 brief disagree, the newer is right and the other is the bug. Control: Established by tests/card.mjs's scenario 'the Health tab (R9-UX-3)': the card lists a waiting sensor from its unavailable state and a fixed per-sensor reason (HEALTH_WAITING), because Home Assistant publishes no attributes for an unavailable entity, so waiting_for is unreadable by the card at the moment it matters. Null control: with the sensor available the row does not appear, and the card reads nothing from the unavailable sensor's attributes. Remeasure: Do not trust this description of the code: read healthPageHtml and HEALTH_WAITING in the card at your merge base and run node tests/card.mjs. Three facts the Health tab could not read, each re-checked at your merge base: the plan's fallback input ('the plan uses X instead') is not published; a count of insight sensors that are off by default has no card-side source (the card has no entity registry, and tests/entities.py refuses card reads of disabled-by-default sensors); the Input Problem sensor's limit (max_age_minutes) is published only for a failing input.",
+    "From carry-1795 (#1795, moved here from the carry file; the pull request for R9-UX-4, which added the notifier module and its five events; effect: narrows): The design asks the comfort event for its why (\"the fuse limit caps heating 02:00-05:00\"). R9-UX-4 ships only peak_guard_suppressing, because the payload carried no per-step cause. When UX-5 publishes the exact idle sub-codes per step it also extends EVENT_DATA and the comfort detector to name the cause of the coldest step, in the event, in docs/automations.md's table and in the blueprint's message, which today says only that the peak guard is holding heating back. Where this entry and the roster's R9-UX-5 brief disagree, the newer is right and the other is the bug. Control: Established by tests/features.py's UX-4 block: the comfort-at-risk event carries predicted_min_c, at, floor_c and peak_guard_suppressing, and exactly the keys notifier.EVENT_DATA declares (check 'each event carries exactly the data keys the module declares'). No published field says why a step is cold; peak_guard_suppressing is the only cause the payload carries. Null control: the block's comfort plans carry no peak_guard_suppressing key at all and the event still fires (data value false), so the event is not tied to the guard. Remeasure: Do not trust this description of the code: read _comfort and EVENT_DATA in notifier.py at your merge base and run the UX-4 block of tests/features.py. Re-check which cause fields the payload publishes once the idle sub-codes exist."
    ]
   },
   {
diff --git a/tests/closures.json b/tests/closures.json
index 79d3291ae..aceb64fc7 100644
--- a/tests/closures.json
+++ b/tests/closures.json
@@ -1573,7 +1573,6 @@
    "dev/programme/HANDOVER.md",
    "dev/programme/carries/carry-1645.json",
    "dev/programme/carries/carry-1774.json",
-   "dev/programme/carries/carry-1795.json",
    "dev/programme/carries/carry-1922.json",
    "dev/programme/carries/carry-201.json",
    "dev/programme/carries/carry-2065.json",
diff --git a/tests/entities.py b/tests/entities.py
index 1a257bf95..d26dc8b0e 100644
--- a/tests/entities.py
+++ b/tests/entities.py
@@ -28325,6 +28325,26 @@ R.check(
 # Read from the comment-stripped job, as the pins above are.
 _PC_STEPS = _PC_BODY_STEP.split("\n      - name: ")
 _PC_WAIT = next((_b for _b in _PC_STEPS if _b.startswith("Wait for code scanning")), "")
+# THE CARRY STEP NAMES THE PULL REQUEST'S BRANCH (R10-BODY-CONTRACT part 2, carry 9): the
+# refusal prints the live groups after-edged on the PR's own group as the valid targets,
+# and it finds the group from `--branch`; without it the refusal reads `valid targets:
+# unknown` and nothing else fails. The step is read off the registered job; the plant is
+# the same step text with the flag dropped, the null control the step as written.
+_PC_CARRY = next((_b for _b in _PC_STEPS if _b.startswith("Every finding the body records")), "")
+
+
+def _pc_carry_names_branch(step: str) -> bool:
+    return ('carry_audit.py check --body' in step and ' --branch "$HEAD_REF"' in step
+            and "HEAD_REF: ${{ github.event.pull_request.head.ref }}" in step)
+
+
+R.check(
+    "pr-contract's carry step passes `--branch \"$HEAD_REF\"`, bound to the PR head ref (plant and null)",
+    bool(_PC_CARRY) and _pc_carry_names_branch(_PC_CARRY)
+    and not _pc_carry_names_branch(_PC_CARRY.replace(' --branch "$HEAD_REF"', ""))  # mut:carry-branch
+    and not _pc_carry_names_branch(_PC_CARRY.replace("github.event.pull_request.head.ref", "github.head_ref")),
+    f"step={'found' if _PC_CARRY else 'missing'}",
+)
 _PC_WAIT_I = next((_i for _i, _b in enumerate(_PC_STEPS) if _b.startswith("Wait for code scanning")), -1)
 _PC_LIST_I = next((_i for _i, _b in enumerate(_PC_STEPS) if _b.startswith("List the red checks")), -1)
 R.check(
diff --git a/tools/audit/carry_audit.py b/tools/audit/carry_audit.py
index 150a1b4be..d465594e7 100644
--- a/tools/audit/carry_audit.py
+++ b/tools/audit/carry_audit.py
@@ -120,7 +120,7 @@ CARRY_SECTIONS = ("forward-carry", "friction")
 NONE_ITEM = re.compile(r"^\W*(?:none|n/a)\W*$|^\W*n/a\s*:", re.I)
 # Not a finding wherever it sits: attribution, the bus trailer and its review
 # trailers (`bus-nonce:`, `Round: <n>`), raw RESULT lines.
-TRAILER = re.compile(r"^\W*(?:\U0001f916|Co-Authored-By|bus:|bus-nonce:|Round:\s*\d|Evidence:|RESULT\b)", re.I)
+TRAILER = re.compile(r"^\W*(?:\U0001f916|Co-Authored-By|bus:|bus-nonce:|Round:\s*\d+\W*$|Evidence:|RESULT\b)", re.I)
 # A verdict's `## Evidence` section, and every section of a merge verdict but a
 # findings section, is read by its structure alone (P308, P314): a check's
 # state or a measurement there says "not blocking" or "deferred" as often as a
@@ -340,7 +340,7 @@ def seg_dests(seg: str) -> list[str]:
     if dm:
         return ["dismissed:" + dm.group(1)]
     # `Carry: <GROUP> | dismissed: <reason>`: the group is a pointer, not a destination
-    pm = re.match(r"([^\s|,;]+)\s*[|;,]\s*[`*_]*dismissed\s*:\s*(.*)", rest, re.I)
+    pm = re.match(r"([^\s|,;]+)\s*\|\s*[`*_]*dismissed\s*:\s*(.*)", rest, re.I)
     if pm and GROUP_TOK.match(pm.group(1).strip("`*_().:")):
         return [f"dismissed({pm.group(1).strip('`*_().:')}):{pm.group(2)}"]
     found = []
@@ -634,7 +634,10 @@ def report(res: dict, label: str = "") -> int:
     return 1 if (u or b) else 0
 
 
-FOLD_LINE = re.compile(r"^\s*(?:[-*+]\s+)?(?:\*\*)?Fold \(([a-z])\):\s*(.*)$", re.M)
+# The owner's live spelling (#1955, comment 5983672253): `**Fold (e), added 2026-10-04 (owner)**: <ask>`. Accepted:
+# a letter of either case, bold before or after the colon, and a `, <note>` clause between the parenthesis and the colon.
+FOLD_LINE = re.compile(r"^\s*(?:[-*+]\s+)?(?:\*\*)?Fold \(([A-Za-z])\)(?:\*\*)?(?:,[^:\n]*?)?(?:\*\*)?:(?:\*\*)?\s*(.*)$",
+                       re.M)
 # prepr.sh's INTENDED_JQ and preflight.sh's CLOSING_REF: the nine GitHub closing keywords, four reference shapes.
 CLOSES = re.compile(r"\b(?:close[sd]?|fix(?:e[sd])?|resolve[sd]?)\s*:?\s+"
                     r"(?:https?://[^ ]*/issues/|[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+#|GH-|#)(\d+)", re.I)
@@ -650,22 +653,31 @@ def fold_answered(ans: str) -> bool:
     return bool(re.match(r"dismissed\s*:\s*\S", ans, re.I))
 
 
-def fold_problems(body: str, issue_text) -> "tuple[list[str], list[str]]":
+def fold_problems(body: str, issue_text, dests=None) -> "tuple[list[str], list[str]]":
     """(unanswered folds, notes) of a body that says `Closes #N`. An issue's owner
     folds are its `Fold (x): <ask>` lines; the body answers each on a line of its own,
     outside fences. `issue_text(n)` is the issue's text or None (unfetchable: the
-    close passes with a note, so a network miss never blocks a merge)."""
+    close passes with a note, so a network miss never blocks a merge). With `dests`, a
+    `Fold (x): Carry: <dest>` answer's destination is checked against the roster as an
+    item's `Carry:` is, not only for being well formed."""
     # fences and HTML comments render as no answer, so neither counts as one
     text = "\n".join(re.sub(r"```.*?```|~~~.*?~~~|<!--.*?-->", "", body, flags=re.S).split("\n"))
-    answered = {m.group(1) for m in FOLD_LINE.finditer(text) if fold_answered(m.group(2))}
+    answered = {m.group(1).lower() for m in FOLD_LINE.finditer(text) if fold_answered(m.group(2))}
     problems, notes = [], []
+    for m in FOLD_LINE.finditer(text) if dests else ():
+        ans = m.group(2).strip().strip("`*_").strip()
+        if re.match(r"carry\s*:", ans, re.I):
+            for tok in seg_dests("Carry:" + ans.split(":", 1)[1]):
+                ok, why = dests.check(tok)
+                if not ok:
+                    problems.append(f"fold ({m.group(1).lower()}) answer `Carry: {tok}` is refused: {why}")
     for n in dict.fromkeys(int(x) for x in CLOSES.findall(text)):
         it = issue_text(n)
         if it is None:
             notes.append(f"#{n} not fetched: its folds are not checked")
             continue
-        problems += [f"#{n} fold ({k}) is unanswered: {ask.strip()[:90]!r}"
-                     for k, ask in FOLD_LINE.findall(it) if k not in answered]
+        problems += [f"#{n} fold ({k.lower()}) is unanswered: {ask.strip()[:90]!r}"
+                     for k, ask in FOLD_LINE.findall(it) if k.lower() not in answered]
     return problems, notes
 
 
@@ -692,16 +704,21 @@ def gh_issue_state(repo: str):
 
 
 def gh_issue_text(repo: str):
-    """n -> the issue's body, or None when `gh` cannot read it."""
+    """n -> the issue's body and its owner's comments, or None when `gh` cannot read it.
+    An owner fold lives in a comment as often as in the body (#1955's fold (e)); a comment
+    by anyone else is no fold, so a stranger cannot add an ask a close must answer."""
     def text(n: int) -> str | None:
         try:
-            return gh_json(f"repos/{repo}/issues/{n}").get("body") or ""
+            parts = [gh_json(f"repos/{repo}/issues/{n}").get("body") or ""]
+            parts += [c.get("body") or "" for c in gh_json(f"repos/{repo}/issues/{n}/comments", paginate=True)
+                      if c.get("author_association") == "OWNER"]
+            return "\n".join(parts)
         except (SystemExit, ValueError):
             return None
     return text
 
 
-def folds_rc(body: str, repo: str, folds_file: str | None) -> int:
+def folds_rc(body: str, repo: str, folds_file: str | None, dests=None) -> int:
     """Print the unanswered folds of <body>'s closes (`--issue-folds-file` JSON
     `{"<n>": "<issue text>"}` offline, else `gh`); 1 when any."""
     if not CLOSES.search(body):
@@ -711,7 +728,7 @@ def folds_rc(body: str, repo: str, folds_file: str | None) -> int:
         reader = lambda n: data.get(str(n))  # noqa: E731
     else:
         reader = gh_issue_text(repo)
-    problems, notes = fold_problems(body, reader)
+    problems, notes = fold_problems(body, reader, dests)
     for x in notes:
         print(f"NOTE fold {x}")
     for x in problems:
@@ -906,10 +923,13 @@ def main(argv: list[str]) -> int:
         if a.cmd == "check":
             body = Path(a.body).read_text()
             comments = json.loads(Path(a.comments).read_text()) if a.comments else []
-            fold_rc = folds_rc(body, a.repo, a.issue_folds_file)
+            dests = None
+            if FOLD_LINE.search(body):  # a fold answer's destination is read against the roster
+                dests = load_dests(Path(a.git_dir), ref, a.briefs_dir, pr_group=a.pr_group)
+            fold_rc = folds_rc(body, a.repo, a.issue_folds_file, dests)
             if not finding_rows(body, comments)[0]:
                 return report({"rows": []}) | fold_rc  # nothing to route: the roster is not read
-            dests = load_dests(Path(a.git_dir), ref, a.briefs_dir, pr_group=a.pr_group)
+            dests = dests or load_dests(Path(a.git_dir), ref, a.briefs_dir, pr_group=a.pr_group)
             if not dests.pr_group and a.branch:
                 dests.pr_group = pr_group_of(dests, a.branch)  # mut:branch
             return report(audit(body, comments, dests)) | fold_rc
@@ -933,7 +953,7 @@ def main(argv: list[str]) -> int:
         if a.cmd == "pr":
             dests = load_dests(ROOT, ref, a.briefs_dir, gh_issue_state(a.repo))
             body, comments = read_pr(a.n, a.repo, None)
-            return report(audit(body, comments, dests), f"#{a.n} ")
+            return report(audit(body, comments, dests), f"#{a.n} ") | folds_rc(body, a.repo, None, dests)
         if a.cmd == "roster":
             repo = str(ROOT)
             rel = roster_lib.roster_path(repo, ref)
@@ -1090,6 +1110,42 @@ def _self_test() -> int:
           [("(e)" in x) for x in fp(full.replace("Fold (e): Carry: R10-LIVE", "```\nFold (e): built\n```"))] == [True])
     check("... an answer inside an HTML comment is no answer",
           [("(e)" in x) for x in fp(full.replace("Fold (e): Carry: R10-LIVE", "<!--\nFold (e): built\n-->"))] == [True])
+    # every accepted issue-side spelling is read as a fold: `Fold (a)` unanswered is refused naming (a)
+    for sp in ("**Fold (a)**: do x", "Fold (A): do x", "**Fold (a):** do x", "- Fold (a): do x",
+               "**Fold (a), added 2026-10-04 (owner)**: do x"):
+        check(f"issue-side spelling {sp!r} is a fold",
+              [("(a)" in x) for x in fp("Closes #7\n", sp + "\n")] == [True])
+        check(f"... and `Fold (a): built` answers it", fp("Closes #7\n\nFold (a): built\n", sp + "\n") == [])
+    check("... an uppercase answer `Fold (A): built` answers the lowercase ask",
+          fp("Closes #7\n\nFold (A): built\n", "Fold (a): x\n") == [])
+    for sp in ("Fold (ab): do x", "Fold (a) do x, no colon", "see Fold (a): in the text above", "Fold: (a) do x"):
+        check(f"{sp!r} is no fold (null control)", fp("Closes #7\n", sp + "\n") == [])
+    # a fold answer's destination is read against the roster, not only for being well formed
+    def fpd(ans):
+        return fold_problems("Closes #7\n\nFold (a): " + ans + "\n", lambda n: "Fold (a): x\n", D)[0]
+    check("`Fold (a): Carry: R10-LIVE` (a live group) is accepted against the roster (null control)",
+          fpd("Carry: R10-LIVE") == [])
+    check("`Fold (a): Carry: R10-INVENTED` is well formed but names no group, refused",
+          len(fpd("Carry: R10-INVENTED")) == 1 and "R10-INVENTED" in fpd("Carry: R10-INVENTED")[0])
+    check("`Fold (a): Carry: R10-OVER` (a done group) is refused as an item's Carry: is",
+          len(fpd("Carry: R10-OVER")) == 1)
+    check("without a roster the destination is not read, as before (null control)",
+          fold_problems("Closes #7\n\nFold (a): Carry: R10-INVENTED\n", lambda n: "Fold (a): x\n")[0] == [])
+    # the issue's text is its body plus its OWNER's comments, nobody else's
+    global gh_json
+    real_gh_json, calls = gh_json, []
+    def fake_gh_json(path, paginate=False):
+        calls.append(path)
+        return ([{"author_association": "OWNER", "body": "**Fold (e), added (owner)**: ask"},
+                 {"author_association": "NONE", "body": "Fold (z): a stranger's ask"}]
+                if path.endswith("/comments") else {"body": "Fold (a): from the body"})
+    gh_json = fake_gh_json
+    try:
+        txt = gh_issue_text("o/r")(9)
+    finally:
+        gh_json = real_gh_json
+    check("issue text carries the body and the owner's comment", "Fold (a)" in txt and "Fold (e)" in txt)
+    check("... and not a non-owner's comment (null control)", "Fold (z)" not in txt)
     check("an issue with no `Fold (x):` line is accepted unchanged (null control)",
           fp("Closes #7\n", "Please fix this; a fold (a): in prose.\n") == [])
     check("a body that does not close the issue owes no fold answer (null control)",
@@ -1152,6 +1208,32 @@ def _self_test() -> int:
           rc == 1 and "FOLD-UNANSWERED" in out and "1 routed" in out)
     rc, out = cli("Closes #7\n\nFold (a): built\n", folds=fold_issue)
     check("check --body accepts the same close once the fold is answered (null control)", rc == 0 and "FOLD-UNANSWERED" not in out)
+    # the fold answer's destination is read against the roster on the CLI line that feeds
+    # fold_problems (the `dests` handed to folds_rc, and the FOLD_LINE test guarding the read)
+    rc, out = cli("Closes #7\n\nFold (a): Carry: R10-INVENTED\n", folds=fold_issue)
+    check("check --body refuses a fold answered `Carry:` a group the roster lacks (rc 1, FOLD-UNANSWERED)",
+          rc == 1 and "FOLD-UNANSWERED" in out and "R10-INVENTED is not a group" in out)
+    rc, out = cli("Closes #7\n\nFold (a): Carry: R10-CONS\n", folds=fold_issue)
+    check("... and accepts one answered with a live group (null control)", rc == 0 and "FOLD-UNANSWERED" not in out)
+    # `pr` reads the same fold answer on the same roster, with gh stubbed
+    def pr_cli(body: str) -> "tuple[int, str]":
+        names = ("read_pr", "load_dests", "gh_issue_state", "gh_issue_text")
+        real = {k: globals()[k] for k in names}
+        globals().update(read_pr=lambda n, repo, d: (body, []), load_dests=lambda *a, **k: Dcl,
+                         gh_issue_state=lambda repo: (lambda n: "open"),
+                         gh_issue_text=lambda repo: (lambda n: "Fold (a): do x\n"))
+        buf = io.StringIO()
+        try:
+            with contextlib.redirect_stdout(buf):
+                rc = main(["pr", "7"])
+        finally:
+            globals().update(real)
+        return rc, buf.getvalue()
+    rc, out = pr_cli("Closes #7\n\nFold (a): Carry: R10-INVENTED\n")
+    check("pr refuses a fold answered `Carry:` a group the roster lacks (rc 1, FOLD-UNANSWERED)",
+          rc == 1 and "R10-INVENTED is not a group" in out)
+    rc, out = pr_cli("Closes #7\n\nFold (a): Carry: R10-CONS\n")
+    check("... and accepts one answered with a live group (null control)", rc == 0 and "FOLD-UNANSWERED" not in out)
     rc, out = cli(plant.rstrip() + " Carry: R10-GONE\n", "--branch", "fix/r10-pr")
     check("check --branch resolves the PR group, so a closed destination lists its valid targets",
           rc == 1 and "valid targets: unknown" not in out and "R10-CONS" in out)
@@ -1445,6 +1527,9 @@ def _self_test() -> int:
         ("... a pointer that is no group of the roster is refused",
          P + " Carry: R10-INVENTED | dismissed: two words\n", "bad"),
         ("... a one-word reason after a pointer is refused", P + " Carry: R10-OVER | dismissed: moot\n", "bad"),
+        ("a `,` after the pointer is not the documented `|`: the group is read as a destination, here a done one",
+         P + " Carry: R10-OVER, dismissed: two words\n", "bad"),
+        ("... nor is a `;`", P + " Carry: R10-OVER; dismissed: two words\n", "bad"),
         ("a bolded `dismissed:` reads", P + " Carry: **dismissed: host load**\n", "routed"),
         ("`Dismissed:` reads in any case", P + " Carry: Dismissed: host load, not a defect\n", "routed"),
         ("`and` separates destinations", P + " Carry: R10-LIVE and #999\n", "bad"),
@@ -1561,6 +1646,8 @@ def _self_test() -> int:
         ("a finding line under the Evidence heading still reads as one after the trailer words (null control)",
          head, verdict_of("merge", "## Evidence\n\n- Round: 3\n- Residual: the census misses one.\n"),
          [("lead", U)]),
+        ("a finding line `Round: 3 of the audit missed a ref` is a finding, so unrouted",
+         head + "## Friction\n\n- Round: 3 of the audit missed a ref.\n", (), [("section", U)]),
         ("`Round:` with no number is not a trailer (null control)",
          head + "## Friction\n\nRound: the guard misses a ref.\n", (), [("section", U)])]
     item_grammar += [
diff --git a/tools/policy/brief_lint.mjs b/tools/policy/brief_lint.mjs
index 51ea0f9d0..df98af716 100644
--- a/tools/policy/brief_lint.mjs
+++ b/tools/policy/brief_lint.mjs
@@ -852,6 +852,7 @@ function checkShape(groups, findings) {
 // and belongs where case 4 already is.
 export const CARRY_FILE_RE = /^carry-(\d+)\.json$/
 export const ROSTER_FILE_RE = /^wave-.*-groups\.json$/
+export const ROSTERS_DIR = path.join(ROOT, 'dev', 'programme', 'rosters')
 const CARRY_EFFECTS = new Set(['narrows', 'invalidates', 'removes'])
 const CARRY_FIELDS = ['from', 'effect', 'control', 'remeasure', 'brief']
 
@@ -870,7 +871,11 @@ export function rosterIssues(dir) {
   const out = new Map()
   let files
   try {
-    files = dir ? fs.readdirSync(dir).filter((f) => ROSTER_FILE_RE.test(f)).sort().map((f) => path.join(dir, f)) : workflowFiles(ROSTER_FILE_RE)
+    // No argument reads the roster directory (roster_lib.ROSTERS_DIR) as well as workflowFiles(): a default
+    // that read only the latter indexed one issue, so the live-group refusal never fired in CI (#2896 A1).
+    const d = dir ?? ROSTERS_DIR
+    files = fs.readdirSync(d).filter((f) => ROSTER_FILE_RE.test(f)).sort().map((f) => path.join(d, f))
+    if (!dir) files = [...new Set([...files, ...workflowFiles(ROSTER_FILE_RE)])]
   } catch {
     return out
   }
@@ -954,13 +959,16 @@ export function checkCarryShape(file, data, findings, roster) {
 // Repairing them would rewrite other groups' controls, so the control lint leaves out these files and
 // only them (both its citation check and its no-path rule): the set is closed -- a new carry file is
 // never added here -- and shrinks as a carry is re-measured or consumed.
+// LEGACY_CONTROL_CAP pins that: the set may only shrink (assertLegacyControl), and a member whose
+// controls now lint clean must leave it.
+const LEGACY_CONTROL_CAP = 14
 const LEGACY_CONTROL_FILES = new Set([
   'carry-1067.json', 'carry-1336.json', 'carry-1395.json', 'carry-1398.json', 'carry-1412.json',
   'carry-1454.json', 'carry-1459.json', 'carry-1463.json', 'carry-1644.json', 'carry-1645.json',
-  'carry-1659.json', 'carry-1660.json', 'carry-1795.json', 'carry-201.json', 'carry-752.json',
+  'carry-1659.json', 'carry-1660.json', 'carry-201.json', 'carry-752.json',
 ])
 
-export function lintCarryFile(file, { roster } = {}) {
+export function lintCarryFile(file, { roster, legacy = LEGACY_CONTROL_FILES } = {}) {
   const findings = []
   const label = path.posix.basename(file)
   let data
@@ -976,7 +984,7 @@ export function lintCarryFile(file, { roster } = {}) {
     if (!c || typeof c !== 'object') return
     // The control is cited prose like the brief: an unresolvable path or symbol, a metric literal or a
     // derived count in it is refused the same way (the next stage re-establishes the finding from it).
-    if (typeof c.control === 'string' && c.control.trim() && !LEGACY_CONTROL_FILES.has(label)) {
+    if (typeof c.control === 'string' && c.control.trim() && !legacy.has(label)) {
       lintBrief(`${label} carry ${i} control`, c.control, findings)
       // A control no seat can re-run is a figure, not a control (writing-for-agents.md: no enumerator,
       // no figure). The requirement binds every carry file but the LEGACY_CONTROL_FILES recorded below.
@@ -1288,7 +1296,7 @@ function assertCarryControl() {
     for (const m of problems) console.log(`  ${m}`)
     return 1
   }
-  console.log('\nCONTROL ok: a carry control with no path, or an unresolvable one, is refused; one naming an existing harness is not; the 15 legacy files are left out')
+  console.log('\nCONTROL ok: a carry control with no path, or an unresolvable one, is refused; one naming an existing harness is not; the legacy files are left out')
   return 0
 }
 
@@ -1322,6 +1330,45 @@ function assertCarryFixtures() {
   return 0
 }
 
+// A1 (#2896) and the carry-control narrowing, pinned:
+//  - the no-argument roster default reads dev/programme/rosters, so a carry file at an issue a live group
+//    covers is refused by lintCarryFile with no roster handed in (a carry at 999999 is not: null control);
+//  - LEGACY_CONTROL_FILES only shrinks: its size is at most LEGACY_CONTROL_CAP, and every member still has a
+//    control error when linted without the exemption (a repaired file must be removed from the set).
+function assertLegacyControl() {
+  const problems = []
+  const live = [...rosterIssues(ROSTERS_DIR).keys()][0]
+  const tmp = fs.mkdtempSync(path.join(os.tmpdir(), 'carrycollide-'))
+  try {
+    const model = JSON.parse(fs.readFileSync(path.join(FIXTURES, 'carry-990001.json'), 'utf8'))
+    const at = (n) => {
+      const f = path.join(tmp, `carry-${n}.json`)
+      fs.writeFileSync(f, JSON.stringify({ ...model, issue: n }))
+      return lintCarryFile(f).filter((x) => x.severity === 'error' && x.message.includes('live roster group'))
+    }
+    if (!Number.isInteger(live)) problems.push('the roster directory indexes no issue: the default reads nothing')
+    else if (!at(live).length) problems.push(`a carry file at #${live}, covered by a live group, is accepted with the default roster`)
+    if (at(999999).length) problems.push('a carry file at an uncovered issue (999999) is refused as a collision (null control)')
+  } finally {
+    fs.rmSync(tmp, { recursive: true, force: true })
+  }
+  if (LEGACY_CONTROL_FILES.size > LEGACY_CONTROL_CAP) problems.push(`LEGACY_CONTROL_FILES holds ${LEGACY_CONTROL_FILES.size} files, over its cap ${LEGACY_CONTROL_CAP}: the set only shrinks`)
+  const files = new Map(carryFiles().map((f) => [path.posix.basename(f), f]))
+  for (const label of LEGACY_CONTROL_FILES) {
+    const f = files.get(label)
+    if (!f) { problems.push(`${label} is in LEGACY_CONTROL_FILES and in no carry directory: remove it`); continue }
+    const errs = lintCarryFile(f, { roster: new Map(), legacy: new Set() }).filter((x) => x.severity === 'error' && / control/.test(x.group))
+    if (!errs.length) problems.push(`${label}: its controls lint clean without the exemption: remove it from LEGACY_CONTROL_FILES`)
+  }
+  if (problems.length) {
+    console.log('\nLEGACY-CONTROL VACUOUS:')
+    for (const m of problems) console.log(`  ${m}`)
+    return 1
+  }
+  console.log('\nLEGACY-CONTROL ok: the default roster refuses a live-group collision and accepts an uncovered carry; the legacy set is within its cap and each member still needs the exemption')
+  return 0
+}
+
 // treeListing acceptance: a throwaway repo whose second commit adds b.txt and
 // deletes a.txt. The head listing must show the add and not the delete, the
 // first commit's the reverse (null control), the checkout form follows the
@@ -1491,6 +1538,7 @@ function main() {
     acceptanceRc += assertRosterIssues()
     acceptanceRc += assertCarryFixtures()
     acceptanceRc += assertCarryControl()
+    acceptanceRc += assertLegacyControl()
     acceptanceRc += assertTreeRev()
   }
   process.exit(totalErrors > 0 || acceptanceRc ? 1 : 0)

## Before you return the verdict (P275)
Run `python3 -I tools/audit/carry_audit.py check --body <PR body file> --comments <file holding [{"id": 0, "body": <verdict.md text>}]>`. Give every reported item its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>`;
an evidence line flagged by its wording takes `Carry: dismissed: evidence, not a finding`. Return the verdict only at rc 0.
