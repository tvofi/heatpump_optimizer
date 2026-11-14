CLOUD REVIEWER seat for PR #3563 of tvofi/heatpump_optimizer, at head 2ef5531223d56cc35d40fbbcb8f8d61ede644c57. Bus nonce: 9d90ce63f65294ddf6e0c0a1cbd8dab1. Never send push notifications. Write no Claude Code footer, no Co-Authored-By or Claude-Session trailer and no claude.ai session link in any commit, pull-request body or comment you produce; check your commits with `git log --format=%B` before pushing.
Setup: `git fetch --unshallow --tags origin`. The session-start `toolchain:` line says whether venv-ci's python3 is on PATH: on REFUSE, start each Bash call with `eval "$(bash .claude/hooks/session-start.sh --env-lines)"`. Then run `bash tools/audit/seat/cloud-setup.sh --check`, and on REFUSE stop: report its line as your result and start no work. Run anything heavy in the background with Monitor and no timeout. Never wait in one tool call longer than 240 s; poll again instead. Read your policy once, verbatim: `python3 -I tools/policy/role_pack.py render fix-review --out $HOME/role-pack.md`, then that file in place of your role contract and INSTRUMENTS.md; on REFUSE read those files as before.
Role: read dev/governance/roles/fix-review.md and its rules from main, and follow them exactly. Fetch the PR head with `git fetch origin 2ef5531223d56cc35d40fbbcb8f8d61ede644c57`; the PR body is in the PR. Start from the review packet, which you render here rather than read from the dispatcher, whose copy is a path on its own machine: `python3 -I tools/audit/seat/review_packet.py render --pr 3563 --head 2ef5531223d56cc35d40fbbcb8f8d61ede644c57 --reviewed-head f11bdd4d483c0509ad108b0e00112aaae8f1368d --out $HOME/review-packet.md`. A refusal names its signal and the packet is still written unless the signal is `host-path`; re-read the live checks either way. This is a later round over the reviewed head f11bdd4d483c0509ad108b0e00112aaae8f1368d: its scope is the packet's `## Review scope` line, the delta and the previous verdict's findings when it reads `delta`, widened only to the exact already-reviewed code a production (custom_components/) delta puts at non-obvious risk that CI would not detect, the verdict naming path and risk; an instrument, test, policy or body delta never widens it (fix-review.md step 12). Verify each claim adversarially: mutate the fix and check the tests fail, and check every figure in the body at this head. Check that it merges with origin/main (`git merge-tree --write-tree origin/main <head>`); block on main only when that reports a conflict, never on a head that is behind main but merges cleanly (the train re-proves it on the current main). Wait for CI on this head only by re-running `python3 tools/audit/seat/merge_train.py classify 2ef5531223d56cc35d40fbbcb8f8d61ede644c57 --pr 3563` in the background, at least 60 s between runs, until it exits 0 (GREEN), 1 (RED), 2 (unreadable: say so in the verdict) or 4 (APPROVAL-OWED: the only red is the budget raise's approval, which follows your verdict; judge the head as GREEN and quote the line); 3 is WAIT, so run it again. Never wait with `pgrep` or `pkill`, whose `-f` pattern matches the waiter's own command line, nor on a context the ruleset does not require, such as `prelude`. A review_packet `required-red` signal does not stop you while classify prints WAIT: classify decides. If your review is otherwise complete and classify still prints WAIT after about 30 minutes of polling, stop waiting: put the line `pending-ci: <the context names it printed>` straight after the `bus-nonce:` line and return the verdict as below; the relay posts it once CI is green at this head, refuses it over a red, and refuses it if the head moves. If the review is not complete then, push `Fix review: blocked 2ef5531223d56cc35d40fbbcb8f8d61ede644c57 ci-wait: <the last classify line>` as below.
Output: in a fresh directory of your own (`W=$(mktemp -d)`), write verdict.md, whose first line is exactly `Fix review: merge 2ef5531223d56cc35d40fbbcb8f8d61ede644c57` or `Fix review: blocked 2ef5531223d56cc35d40fbbcb8f8d61ede644c57 <class>: <reason>` (no brackets; the class is lower-case letters and dashes), in the format the role file gives, then a blank line, then `bus-nonce: 9d90ce63f65294ddf6e0c0a1cbd8dab1`, then the body in sections. A blocked verdict's block goes under `## Block`. Each finding this PR does not settle (a defect, a surviving mutant, a deferral, a follow-up, a task owed after the merge) is its own bullet under `## Findings` ending in its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>` (finding-propagation.md). Everything else (RESULT lines, re-runs, CI state, figures you could not re-derive) goes under `## Evidence`: tools/audit/carry_audit.py reads an item there, and under any heading of a merge verdict but `## Findings`, `## Friction`, a block heading and a note heading (Residuals, Follow-ups, Notes ...), by its shape alone: a finding only when it opens with a lead word (Residual:, Follow-up:, Out of scope: ...) or carries a `Carry:`, so a defect you hand on goes under `## Findings`, and bus.sh refuses a verdict holding a finding with no valid `Carry:`. Put the evidence files in `ev/` beside it, under 25 MB in all (cite a large log by path and keep its tail: a ~30 MB ev/ once failed its push), and make at least one file under `ev/` contain the full 40-hex head `2ef5531223d56cc35d40fbbcb8f8d61ede644c57` (e.g. `ev/HEAD.txt` holding the head you reviewed, beside your command output): bus.sh refuses a verdict whose `ev/` names no head. Do NOT run bus.sh: its dispatch record lives on the orchestrator's machine, which publishes the verdict there (cloud_relay.sh). Return the verdict on a probe ref, and push nothing else; this builds one parentless commit with a private index and touches no branch of your checkout: `R=$(git rev-parse --show-toplevel); G=$(git rev-parse --absolute-git-dir); mkdir -p $W/pr && cp -r $W/verdict.md $W/ev $W/pr/ && cd $W/pr && T=$(GIT_DIR=$G GIT_INDEX_FILE=$W/idx GIT_WORK_TREE=$W/pr sh -c 'git add -A -f . && git write-tree') && C=$(GIT_DIR=$G git -c user.name=hpo-fixer -c user.email=70032254+tvofi@users.noreply.github.com commit-tree $T -m "verdict 3563 2ef5531223d56cc35d40fbbcb8f8d61ede644c57") && git -C $R push -q origin $C:refs/heads/probe/rev-3563-9d90ce63`. That ref is the return signal. Do not post comments, approve or merge.
Every way your turn ends pushes a verdict to that ref: a setup or hook refusal that stops you pushes `Fix review: blocked 2ef5531223d56cc35d40fbbcb8f8d61ede644c57 seat-refused: <the refusing line>`; never end your turn while a background poll runs. After the push, read the ref back with `git ls-remote origin refs/heads/probe/rev-3563-9d90ce63`, and push again if it does not print your commit.
A red is owed a `## Red checks` answer, and may block, only when its name is in the set `python3 tools/audit/seat/merge_train.py owed-reds` prints (defect-root-cause.md); any other red is neither answered nor a block.
Never write to any branch except your return refs. Never work around a hook or a refusal; report it in your result instead.
Discovery reads (search, list, read across files) go through Agent subagents, as the frugal routing guard requires: when it refuses inline work, dispatch a haiku or sonnet Agent subagent to do it rather than bypassing the guard; never set FRUGAL_ALLOW_INLINE and never edit .claude/settings.json.

Brief (snapshotted when this payload was rendered):
# Review packet #3563
head: 2ef5531223d56cc35d40fbbcb8f8d61ede644c57
base: e23124ff6e45bac1d48b4a775dad555a37965355

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: pending
arm id=132261101231 skipped
cancel-superseded id=132261107895 queued
prelude id=132261108391 queued
refresh id=132261108214 queued

## Refusals
none

## Advisories
none

## carry_audit at the head
NOTE body item 753b6610: R11-INTAKE-R10-RESIDUE
NOTE body item f14f17f5: R11-INTAKE-R10-RESIDUE
NOTE body item c7e69450: R11-INTAKE-R10-RESIDUE
NOTE body item a0e752f6: R11-INTAKE-R10-RESIDUE
NOTE body item 3bbcabdc: R11-INTAKE-R10-RESIDUE
CARRY-AUDIT: 5 finding item(s): 5 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
ok         node dev/audit/harnesses/r10_card_user_text.mjs
             `dev/audit/harnesses/r10_card_user_text.mjs` is in the tree at this head
  ok         python3 -I dev/audit/harnesses/r10_card_evidence_kinds.py
             `dev/audit/harnesses/r10_card_evidence_kinds.py` is in the tree at this head
  ok         tests/card.mjs
             `tests/card.mjs` is in the tree at this head
  ok         python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)
             `tests/closure.py` is in the tree at this head
  ok         node tests/card.mjs
             `tests/card.mjs` is in the tree at this head
  ok         GOLDEN_MODE=drift node tests/card_drift.mjs
             `tests/card_drift.mjs` is in the tree at this head
  ok         tests/features.py
             `tests/features.py` is in the tree at this head
  ok         tests/doc_claims.py
             `tests/doc_claims.py` is in the tree at this head
  ok         tests/harness_headers.py
             `tests/harness_headers.py` is in the tree at this head
  ok         tests/arch_score_head.py
             `tests/arch_score_head.py` is in the tree at this head
  ok         tests/deployment_shape.py
             `tests/deployment_shape.py` is in the tree at this head
  ok         tests/plan_view.py
             `tests/plan_view.py` is in the tree at this head
  ok         tests/env_drift.py
             `tests/env_drift.py` is in the tree at this head
  ok         GOLDEN_MODE=drift tests/golden.py
             `tests/golden.py` is in the tree at this head
  ok         tests/layout.py
             `tests/layout.py` is in the tree at this head
  ok         tests/closure.py selftest
             `tests/closure.py` is in the tree at this head
  ok         tests/env_drift.py --claims-only 90c6bc3b0
             `tests/env_drift.py` is in the tree at this head
  ok         python3 tests/structure.py
             `tests/structure.py` is in the tree at this head
  ok         python3 tools/pr/ci_predict.py --apply-inert
             `tools/pr/ci_predict.py` is in the tree at this head
  ok         HPO_PAGES_OUT=<scratch> node tests/card_browser.mjs
             `tests/card_browser.mjs` is in the tree at this head

FIGURES: 20 resolved, 0 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
none

## Review scope: delta (later round over the reviewed head f11bdd4d483c0509ad108b0e00112aaae8f1368d)
Confirm each finding of the previous verdict is resolved, re-read the live required checks, and review the delta below. Widen only to exactly the already-reviewed code a delta touching production code (custom_components/) puts at risk of being affected in a non-obvious way CI would not detect, naming the path and the risk in the verdict; an instrument, test, policy or body delta never justifies a wider review (fix-review.md step 12).

## Previous verdict at f11bdd4d483c0509ad108b0e00112aaae8f1368d
Fix review: blocked f11bdd4d483c0509ad108b0e00112aaae8f1368d comment-evidence: advisor.refit_detail is verdicted true on a code comment; the ±7-10 % lower bound exists only in accuracy.py:646-650's comment

bus-nonce: c1e04704ece088aa66287f43b445823c

## Block

- Reviewer addition (1) of this group's brief: "a row whose evidence is a comment is a block". `dev/audit/rounds/round10/user-text-card.md:176` verdicts `advisor.refit_detail` true. The text says, in en, sv and de, "about ±7-10 % uncertain". The row's evidence for that clause is "accuracy.py:651 REFIT_BAND_PERCENT=10 (comment states 7-10 %)". In code, at base 90c6bc3b0, `REFIT_BAND_PERCENT = 10` (accuracy.py:651) is published as `"band_percent": REFIT_BAND_PERCENT` (accuracy.py:776). The 7 appears only in the `#:` comment at accuracy.py:646-650, a pre-study figure. The card renders this key at card.js:10097 with `{days}` and `{pairs}` only, so it never reads `attrs.refit.band_percent`. The row's other quoted evidence, `_refit_start` "after the last boost-tagged pair plus settle, and after the last restore", is the docstring at accuracy.py:657-658. The code body at :659-663 does implement that behaviour, but the row quotes the docstring, not the code. The coordinator.py:1363 "Recommend-only" citation is also a docstring (restart_advice, :1358-1365). The row must be re-judged against code. Either the band clause is verdicted unverifiable or corrected to the published `band_percent`, or the card renders `band_percent` and a test pins it (brief addition 3). The other docstring-citing rows I sampled also cite a deciding code line: `score.part_overall` (:50, coordinator.py:3381/3392) and `health.cop_reason_unaligned_meters` (:140, heat_energy.py:567, the `unaligned if got.elec_kw is None` expression in close_span). This is the only row I found whose claim rests on a comment alone. The sample covered every row that names a comment or docstring (`grep -niE 'docstring|comment'`, 6 hits, 3 of them rows). Rows that quote a docstring without saying so were not swept.
- Surviving mutant on a pinned claim (brief addition 3). The body says the invalid-window pin checks that "the card's check reads `quietWindows`". The body's own corrected-list item says "the save and simulate checks also read `quietWindows`". The check is `/quietWindows \|\| \[\]\)\.find\(/.test(cardSrc)` (tests/card.mjs, last block), which one match satisfies. Mutant `drop-quiet-find-first` swaps `(draft.quietWindows || []).find(` for `(draft.dhwWindows || []).find(` at card.js:13217 (the first of two sites, :13217 and :13336). The suite stays at rc 0, `ALL CARD CHECKS PASSED`. With that mutant, the channel-neutral error text is false for one of the two handlers, and nothing fails. The fix is to require both sites, or to pin the behaviour by driving each handler with an invalid quiet window.

## Findings

- `tests/card.mjs`: the `check("user text: the invalid-window error ...` call in the new block is indented four spaces where its siblings use two. This is cosmetic only. Carry: dismissed: whitespace, no behaviour; the re-cut touches this block anyway

## Evidence

- Round 1 of review, a handoff review: no pull request exists yet, so there is no review packet and no CI to read. This verdict reads no check runs and answers no red. `merge_train.py owed-reds` prints the required set, but no run exists at this head.
- Head measured: f11bdd4d483c0509ad108b0e00112aaae8f1368d, which is the tip of handoff/r10-user-text-verify-card and the head the body's `## Head` names. Merge base: 90c6bc3b0756475e28d4ace8d8e31c4788474933. origin/main is e23124ff6e45bac1d48b4a775dad555a37965355.
- `git diff $(merge-base)...origin/main -- dev/governance/roles/` is empty, so the contract is current.
- `git merge-tree --write-tree origin/main f11bdd4d4` gives rc 0 and tree cda4d02d02dc4a8257fb41b6913ec3c431f2b13b, so there is no conflict (ev/merge-tree.txt).
- RESULT card.mjs at head: rc 0, `ALL CARD CHECKS PASSED`, after `tests/plan_view.py` wrote its payload (ev/card-head.txt).
- RESULT mutation proof, re-run: the base card with the head's tests gives rc 1, with exactly the 7 FAILs the body lists (ev/mut-basecard.txt). This reproduces the body.
- RESULT targeted mutants, 9 run and 8 killed (ev/targeted-mutants.txt):
  - Killed: `COP_TRACKING_ERROR_GATE` 0.3→0.25, sv gate 30 %→40 %, the modelled floor `<= 0.1`→`<= 0.2`, "Varmvatten" re-added to the sv window error, both `quietWindows` finds removed, the old de "Wärmespeicherung", a truncated sv grid page, and a de.json grid menu label.
  - Survived: `drop-quiet-find-first` (see Block).
- RESULT enumerator, own run: the head prints `table 644 (unreached 0)`, `literal 4`; the base prints `table 648 (unreached 3)`, `literal 4`. These match the body's Figures (ev/enum-head.txt, ev/enum-base.txt). The planted null control was not re-run.
- Not re-derived: the verdict counts true 331 / false 22 / stale 1 / unverifiable 6 / n/a 292. They come from the fixer's nine reader tables, which are not in the tree. Only the summary table and the per-row record are, so I could not re-derive the `cut -f4` count.
- Not re-derived: the browser PNG cmp results and the 11-script gate table. This is a cheap-checks-only review, and card.mjs plus card_drift were the closures I re-ran.
- RESULT VERSION, manifest and RELEASE_NOTES.md: absent from the three-dot diff. `tests/golden/claimed_drift.txt` is untouched.
- Forward-carry destination `R11-INTAKE-R10-RESIDUE` exists in `dev/programme/rosters/wave-r10-groups.json` on origin/main. I did not check whether its brief already holds the five carries. The body states no roster SHA for them, and this block returns the branch anyway.
- RESULT `GOLDEN_MODE=drift node tests/card_drift.mjs` at the head: rc 0, `card_drift: 21 state(s) moved and claimed, 24 identical` (ev/card_drift-head.txt). Every moved state is claimed, which matches the body's 21.

## Delta diff: git diff f11bdd4d483c0509ad108b0e00112aaae8f1368d 2ef5531223d56cc35d40fbbcb8f8d61ede644c57
diff --git a/custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js b/custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js
index da01b5b58a..d7c75fd2a9 100644
--- a/custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js
+++ b/custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js
@@ -296,7 +296,7 @@ const STRINGS = {
     // The drift alarm's restart points (R9-DIAG-2S, #1936).
     "advisor.refit_title": "Restart the heat-loss model at {to} (now {from})",
     "advisor.refit_detail":
-      "Refitted from {days} settled days ({pairs} intervals) since the last boost or restore; about ±7-10 % uncertain. Nothing changes until you accept.",
+      "Refitted from {days} settled days ({pairs} intervals) since the last boost or restore; about ±{band} % uncertain. Nothing changes until you accept.",
     "advisor.refit_wait_title": "Heat-loss refit pending",
     "advisor.refit_wait_detail":
       "Predictions are drifting. A refit needs {need} settled days of evidence; {days} so far.",
@@ -308,6 +308,7 @@ const STRINGS = {
     "advisor.optin_wood": "Wood-stove timing",
     "advisor.optin_fuse": "Fuse size",
     "advisor.optin_frequency": "Compressor frequency",
+    "advisor.optin_sensor_off": "then turn on its sensor in the entity settings: it is off by default",
     // The options-flow step each opt-in is turned on in (ADVISOR_OPT_IN_STEP).
     "advisor.step_tuning": "Configure → Savings vs comfort",
     "advisor.step_building": "Configure → Advanced settings → Heating system and heat storage",
@@ -1176,7 +1177,7 @@ const STRINGS = {
     "advisor.apply_failed": "Kunde inte verkställa: {error}",
     "advisor.refit_title": "Starta om värmeförlustmodellen på {to} (nu {from})",
     "advisor.refit_detail":
-      "Omanpassad från {days} lugna dagar ({pairs} intervall) sedan senaste boost eller återställning; osäkerhet ungefär ±7-10 %. Ingenting ändras förrän du godtar.",
+      "Omanpassad från {days} lugna dagar ({pairs} intervall) sedan senaste boost eller återställning; osäkerhet ungefär ±{band} %. Ingenting ändras förrän du godtar.",
     "advisor.refit_wait_title": "Omanpassning av värmeförlusten väntar",
     "advisor.refit_wait_detail":
       "Prognoserna driver. En omanpassning kräver {need} lugna dagar med underlag; {days} hittills.",
@@ -1188,6 +1189,7 @@ const STRINGS = {
     "advisor.optin_wood": "Vedpannans timing",
     "advisor.optin_fuse": "Huvudsäkring",
     "advisor.optin_frequency": "Kompressorfrekvens",
+    "advisor.optin_sensor_off": "slå sedan på dess sensor i entitetsinställningarna: den är avstängd från början",
     "advisor.step_tuning": "Konfigurera → Besparing kontra komfort",
     "advisor.step_building": "Konfigurera → Avancerade inställningar → Värmesystem och värmelagring",
     "advisor.step_grid": "Konfigurera → Effekttariff, sedan Avancerade inställningar → Säkring och effekttak",
@@ -1997,7 +1999,7 @@ const STRINGS = {
     "advisor.applied_setpoint": "Warmwasser-Sollwert auf {to} °C gesetzt.",
     "advisor.apply_failed": "Anwenden nicht möglich: {error}",
     "advisor.refit_title": "Wärmeverlustmodell bei {to} neu starten (jetzt {from})",
-    "advisor.refit_detail": "Neu angepasst aus {days} abgeschlossenen Tagen ({pairs} Intervalle) seit dem letzten Boost oder der letzten Wiederherstellung; etwa ±7–10 % Unsicherheit. Es ändert sich nichts, bis du zustimmst.",
+    "advisor.refit_detail": "Neu angepasst aus {days} abgeschlossenen Tagen ({pairs} Intervalle) seit dem letzten Boost oder der letzten Wiederherstellung; etwa ±{band} % Unsicherheit. Es ändert sich nichts, bis du zustimmst.",
     "advisor.refit_wait_title": "Neuanpassung des Wärmeverlusts ausstehend",
     "advisor.refit_wait_detail": "Die Vorhersagen driften. Eine Neuanpassung benötigt Belege aus {need} abgeschlossenen Tagen; bisher {days}.",
     "advisor.restore_title": "Modell von {when} wiederherstellen",
@@ -2008,6 +2010,7 @@ const STRINGS = {
     "advisor.optin_wood": "Zeitpunkt für den Kaminofen",
     "advisor.optin_fuse": "Sicherungsgröße",
     "advisor.optin_frequency": "Verdichterfrequenz",
+    "advisor.optin_sensor_off": "dann seinen Sensor in den Entitätseinstellungen aktivieren: er ist standardmäßig deaktiviert",
     "advisor.step_tuning": "Konfigurieren → Einsparung oder Komfort",
     "advisor.step_building": "Konfigurieren → Erweiterte Einstellungen → Heizsystem und Wärmespeicher",
     "advisor.step_grid": "Konfigurieren → Lastspitzentarif des Netzes, dann Erweiterte Einstellungen → Sicherung und Spitzenwächter",
@@ -9996,8 +9999,11 @@ const ADVISOR_SUFFIXES = {
   restart: "_model_restart_advisor",
 };
 const ADVISOR_OPT_IN = ["wood", "fuse", "frequency"];
-// The options-flow step that turns each opt-in on ("degree" is shown only while
-// the score sensor publishes no price_tiles: their switch is off). Home
+// The options-flow step each opt-in needs: it turns "degree" on (shown only
+// while the score sensor publishes no price_tiles: their switch is off), and
+// is the settings page of the three ADVISOR_OPT_IN advisors, whose sensors
+// no step turns on: they stay disabled until the user enables them, and the
+// row says so (`advisor.optin_sensor_off`). Home
 // Assistant has no URL into a step, so the button opens the entry, whose
 // Configure starts the flow, and the row names the step (R10-DEEPLINK).
 const ADVISOR_OPT_IN_STEP = { degree: "tuning", wood: "building", fuse: "grid", frequency: "metering" };
@@ -10094,7 +10100,8 @@ function restartRows(plan) {
     rows.push(row("adopt_refit",
       L("advisor.refit_title", { to: Number(refit.scale).toFixed(2),
         from: readNumber(attrs.current_scale) === null ? "—" : readNumber(attrs.current_scale).toFixed(2) }),
-      L("advisor.refit_detail", { days: Number(refit.settled_days).toFixed(1), pairs: refit.pairs })));
+      L("advisor.refit_detail", { days: Number(refit.settled_days).toFixed(1), pairs: refit.pairs,
+        band: finiteNum(refit.band_percent) ? String(Number(refit.band_percent)) : "—" })));
   } else if (refit) {
     rows.push(row("", L("advisor.refit_wait_title"),
       L("advisor.refit_wait_detail", { need: refit.required_days, days: Number(refit.settled_days).toFixed(1) })));
@@ -10218,7 +10225,7 @@ function advisorInboxHtml(host) {
   const rows = advisorRows(host);
   const feedback = feedbackGaps(host.plan);
   const optIn = (priceTiles(host.plan) ? ADVISOR_OPT_IN : ["degree", ...ADVISOR_OPT_IN]).map((id) => `<div class="fact-inbox-row">
-      <span class="fact-text">${esc(L(`advisor.optin_${id}`))}<span class="fact-sub">${esc(L(`advisor.step_${ADVISOR_OPT_IN_STEP[id]}`))}</span></span>
+      <span class="fact-text">${esc(L(`advisor.optin_${id}`))}<span class="fact-sub">${esc(L(`advisor.step_${ADVISOR_OPT_IN_STEP[id]}`))}${ADVISOR_OPT_IN.includes(id) ? esc(`; ${L("advisor.optin_sensor_off")}`) : ""}</span></span>
       <button type="button" class="fact-act" data-act="open_options">${esc(L("advisor.act_settings"))}</button>
     </div>`).join("");
   return `<div class="fact-head"><span class="fact-title">${esc(L("advisor.inbox_heading"))}</span></div>
diff --git a/dev/audit/harnesses/r10_card_evidence_kinds.py b/dev/audit/harnesses/r10_card_evidence_kinds.py
new file mode 100644
index 0000000000..0e40e1a62b
--- /dev/null
+++ b/dev/audit/harnesses/r10_card_evidence_kinds.py
@@ -0,0 +1,82 @@
+# R10-USER-TEXT-VERIFY-CARD: classifies every file:line a round-10 user-text
+# record cites, at the record's merge base, as code, comment, docstring or
+# blank, and prints each row with a citation that is not code (the owner's
+# ruling of 2026-11-13: text is verified against behaviour, never a comment).
+#
+#    python3 -I dev/audit/harnesses/r10_card_evidence_kinds.py <record.md> [base]
+#
+# Run from a worktree root. A row is a table line opening with a backticked
+# key, read up to the record's own sweep section (whose table quotes the
+# citations it replaced); a citation is `path:line` or `path:line-line` (a `~` before the line is
+# read as the line). A bare path resolves under the package, its `www/`, or its
+# `translations/`. Comment: a stripped line opening `#` (.py) or `//`, `*`,
+# `/*` (.js, .mjs). Docstring: a line inside a bare string expression, by
+# `ast`. Output: `ONLY` (no citation of the row is code) or `SOME`, the key,
+# then each non-code citation with its kind; a summary on stderr.
+# Counts and classifications only; no timing, no network.
+import ast, re, subprocess, sys
+BASE = sys.argv[2] if len(sys.argv) > 2 else "90c6bc3b0756475e28d4ace8d8e31c4788474933"
+rec = sys.argv[1]
+PKG = "custom_components/heatpump_optimizer/"
+cache = {}
+def src(path):
+    if path not in cache:
+        r = subprocess.run(["git", "show", f"{BASE}:{path}"], capture_output=True, text=True)
+        cache[path] = r.stdout.splitlines() if r.returncode == 0 else None
+    return cache[path]
+doc = {}
+def docranges(path):
+    if path in doc: return doc[path]
+    rs = set()
+    try:
+        t = ast.parse("\n".join(src(path)))
+        for n in ast.walk(t):
+            if isinstance(n, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
+                b = n.body
+                if b and isinstance(b[0], ast.Expr) and isinstance(getattr(b[0], "value", None), ast.Constant) and isinstance(b[0].value.value, str):
+                    rs.update(range(b[0].lineno, b[0].end_lineno + 1))
+            # attribute docstrings: a bare string expression anywhere
+            if isinstance(n, ast.Expr) and isinstance(getattr(n, "value", None), ast.Constant) and isinstance(n.value.value, str):
+                rs.update(range(n.lineno, n.end_lineno + 1))
+    except Exception: pass
+    doc[path] = rs; return rs
+def kind(path, ln):
+    lines = src(path)
+    if lines is None or ln < 1 or ln > len(lines): return "missing"
+    s = lines[ln - 1].strip()
+    if path.endswith(".py"):
+        if ln in docranges(path): return "docstring"
+        if s.startswith("#"): return "comment"
+        if s == "": return "blank"
+        return "code"
+    if path.endswith((".js", ".mjs")):
+        if s.startswith(("//", "*", "/*")): return "comment"
+        if s == "": return "blank"
+        return "code"
+    return "code"
+CIT = re.compile(r"((?:<home>/[^/\s]+/)?(?:[\w.-]+/)*[\w.-]+\.(?:py|js|mjs|json)):~?(\d+)(?:-(\d+))?")
+def resolve(p):
+    p = re.sub(r"^<home>/[^/]+/", "", p)
+    for cand in (p, PKG + p, PKG + "www/" + p, PKG + "translations/" + p):
+        if src(cand) is not None: return cand
+    return None
+rows = flagged = 0
+for line in open(rec):
+    if line.startswith("## Comment and docstring evidence"): break  # the sweep's own table quotes the old citations
+    m = re.match(r"\|\s*`([^`]+)`\s*\|", line)
+    if not m: continue
+    rows += 1
+    kinds = []
+    for c in CIT.finditer(line):
+        path = resolve(c.group(1))
+        if path is None: kinds.append((c.group(0), "unresolved")); continue
+        a = int(c.group(2)); b = int(c.group(3) or a)
+        ks = {kind(path, l) for l in range(a, min(b, a + 60) + 1)} - {"blank"}
+        k = "code" if "code" in ks else ("+".join(sorted(ks)) or "blank")
+        kinds.append((c.group(0), k))
+    bad = [(c, k) for c, k in kinds if k not in ("code",)]
+    if bad:
+        flagged += 1
+        allbad = all(k != "code" for _, k in kinds)
+        print(f"{'ONLY' if allbad else 'SOME'}\t{m.group(1)}\t" + "; ".join(f"{c}={k}" for c, k in bad))
+print(f"rows {rows} flagged {flagged}", file=sys.stderr)
diff --git a/dev/audit/rounds/round10/user-text-card.md b/dev/audit/rounds/round10/user-text-card.md
index 0fc1fc4292..4719195bfd 100644
--- a/dev/audit/rounds/round10/user-text-card.md
+++ b/dev/audit/rounds/round10/user-text-card.md
@@ -16,8 +16,8 @@ Each row was judged by reading the code that decides it: where the card renders
 
 | verdict | rows |
 |---|---|
-| true | 331 |
-| false | 22 |
+| true | 330 |
+| false | 23 |
 | stale | 1 |
 | unverifiable | 6 |
 | n/a | 292 |
@@ -26,10 +26,10 @@ Each row was judged by reading the code that decides it: where the card renders
 
 | key | text at the base (en) | what the code does | evidence | correction |
 |---|---|---|---|---|
-| `health.learn_savings_why` | Waiting for the first settled month | Not waiting for a SETTLED (closed) month: the sensor becomes available as soon as any month, including the still-open current month, has booked savings_baseline; its value is the open month estimate (row.estimated). Waiting ends at first booked month, not at month close. | sensor.py:~525 "return None if self._rows() else "settled_savings_month""; ledger.py:~486 "if "savings_baseline" not in lines: continue" ; ledger.py:~497 "estimated = key == open_key"; sensor.py:~532 native_value reads row with "estimated" | en, sv, de: Waiting for the first month with a booked saving |
-| `health.learn_score_why` | Waiting for the first scored day | Key is never rendered: the score branch in healthWaitingWhy uses scoreReasonText of the sensor reasons.overall, so this string is dead. Recommend removing the key from all three languages (no text change needed). | <home>/wt-card/custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js:10512 "if (id === "score") {... return scoreReasonText(...overall)}" returns before L(`health.learn_${id}_why`) at :10516 | key removed (never rendered) |
+| `health.learn_savings_why` | Waiting for the first settled month | Not waiting for a SETTLED (closed) month: the sensor becomes available as soon as any month, including the still-open current month, has booked savings_baseline; its value is the open month estimate (row.estimated). Waiting ends at first booked month, not at month close. | sensor.py:528 "return None if self._rows() else "settled_savings_month""; ledger.py:495 "if "savings_baseline" not in lines: continue" ; ledger.py:506 "estimated = key == open_key"; sensor.py:~532 native_value reads row with "estimated" | en, sv, de: Waiting for the first month with a booked saving |
+| `health.learn_score_why` | Waiting for the first scored day | Key is never rendered: the score branch in healthWaitingWhy uses scoreReasonText of the sensor reasons.overall, so this string is dead. Recommend removing the key from all three languages (no text change needed). | custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js:10512 "if (id === "score") {... return scoreReasonText(...overall)}" returns before L(`health.learn_${id}_why`) at :10516 | key removed (never rendered) |
 | `health.model_default` | Still the default: no samples yet. | Before any sample the tank rate is the value set in the Hot water tank options (default 0.3 C/h), not necessarily the default; the other rows say 'the settings' estimate' | dhw_learning.py:186 self.cooling_rate: float = float(params().dhw_cooling_rate); config_flow.py:1792 _F("hot_water_tank", CONF_DHW_COOLING_RATE, DEFAULT_DHW_COOLING_RATE, ...); coordinator.py:7963 "dhw_cooling_rate_learned": cooling_samples > 0 | en, sv, de: Still the settings' rate: no samples yet. |
-| `health.model_share` | {v} % of the settings' estimate | The ratio is the lower floor's loss relative to the settings value after the whole-house learned scale is applied (the split, not the level). With house scale 1.3 and ratio 100 % the lower floor really loses 130 % of the settings estimate | coordinator.py:5950 base_u = params.lower_floor_heat_loss * self._house_heat_loss_scale; thermal_model.py:604 lower_floor_heat_loss * self.lower_floor_loss_ratio; coordinator.py:5906 docstring-free behaviour: ratio multiplies only the lower zone on top of the house scale | en, sv, de: {v} % of the house-wide estimate |
+| `health.model_share` | {v} % of the settings' estimate | The ratio is the lower floor's loss relative to the settings value after the whole-house learned scale is applied (the split, not the level). With house scale 1.3 and ratio 100 % the lower floor really loses 130 % of the settings estimate | coordinator.py:5950 base_u = params.lower_floor_heat_loss * self._house_heat_loss_scale; thermal_model.py:604 lower_floor_heat_loss * self.lower_floor_loss_ratio | en, sv, de: {v} % of the house-wide estimate |
 | `health.cop_reason_tracking_gate` | The house did not follow the plan closely enough in the interval. | Not about the house: the interval's metered-power / planned-power ratio differs by more than 30 % from its own walking average (a one-off blip in the pump's draw vs the plan) | accuracy.py:906-907 if abs(ratio - ewma) / max(ewma, 1e-6) > COP_TRACKING_ERROR_GATE: return COP_REFUSED_TRACKING; const.py:265 COP_TRACKING_ERROR_GATE = 0.3; coordinator.py:5360-5365 ratio = measured_power / commanded | en, sv, de: The pump's power draw against the plan moved more than 30 % away from its recent average in the interval. |
 | `health.cop_reason_modelled_cop` | Only a modelled efficiency was available, not a measured one. | Refusal is when the model's own reference COP for the interval is <= 0.1 (unusable reference); lack of a measurement is cop_sample/no_heat_reading or the not_measurable state, and a modelled-only install still folds | coordinator.py:5389-5390 if modelled_cop <= 0.1: return COP_REFUSED_MODELLED | en, sv, de: The model's own efficiency for the interval was unusable (0.1 or lower), so there was nothing to compare against. |
 | `health.metric_lower` | The lower floor's heat loss as a share of the settings' estimate. Above 100 % loses more; with no samples it is the settings' estimate. | Ratio is relative to the settings value after the whole-house scale (the split, not the level); 100 % means 'same as the rest of the house learned', not 'as settings'. Starts at 100 % with no samples, so that part holds | coordinator.py:5950 base_u = params.lower_floor_heat_loss * self._house_heat_loss_scale; thermal_model.py:604; const.py:1551 DEFAULT_LOWER_FLOOR_LOSS_RATIO = 1.0 | en, sv, de: The lower floor's heat loss as a share of the house-wide estimate for it: the settings' value with the whole house's learned correction. Above 100 % loses more; with no samples it is 100 %. |
@@ -40,7 +40,7 @@ Each row was judged by reading the code that decides it: where the card renders
 | `advisor.step_tuning` | Configure → Savings vs comfort | de page title in translations/de.json is "Einsparung oder Komfort" but the card says "Einsparungen vs. Komfort": navigation label differs from HA de UI. en and sv match their page titles; only de is off. | custom_components/heatpump_optimizer/config_flow.py:1867 _F("tuning", CONF_PRICE_TILES_ENABLED, ...); custom_components/heatpump_optimizer/config_flow.py:1606 _P("tuning","Savings vs comfort",_TOP) | de only: Konfigurieren → Einsparung oder Komfort |
 | `advisor.step_grid` | Configure → Grid peak tariff | The fuse advisor needs main_fuse_amperes > 0 (default 0), set on Advanced settings -> Fuse and peak guards, and is published on the Monthly Peak sensor which is available only with the capacity tariff on (page "Grid peak tariff"). The grid page alone does not hold the fuse size. Confidence moderate (navigation wording). | custom_components/heatpump_optimizer/config_flow.py:1909 _F("grid_connection", CONF_MAIN_FUSE_A, ...) on page "Fuse and peak guards" (_ADVANCED, 1632); custom_components/heatpump_optimizer/coordinator.py:8970 "fuse = self._fuse_kw(); if fuse is None: return"; custom_components/heatpump_optimizer/entry_config.py:263 fuse_kw None when amps <= 0; custom_components/heatpump_optimizer/sensor.py:2154-2157 MonthlyPeak available only when peak_tariff_enabled | en, sv, de: Configure → Grid peak tariff, then Advanced settings → Fuse and peak guards |
 | `receipt.covers` | Covers {lines}. The savings figure compares spot cost only. | Savings baseline and actual are both priced at spot PLUS the interval's per-kWh grid energy fee (add_savings_settlement spot=spot+fee_per_kwh), so the grid energy fee is compared too; only capacity charge and compressor wear (and uncovered intervals) are left out. The same sentence's {lines} list contains the grid energy fee line, so 'spot cost only' contradicts it. sv and de say the same as en and are equally wrong. | custom_components/heatpump_optimizer/ledger.py:333 "spot=spot + fee_per_kwh"; savings_baseline/actual booked via book() at spot+fee (custom_components/heatpump_optimizer/ledger.py:372-376); custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js:10836 | en, sv, de: Covers {lines}. The savings figure compares only the spot price and the per-kWh grid fee. |
-| `plan.space_blocked` | DHW only — no space heating: the house trace is the plan's promise, not what the pump is executing. | space_blocked is true whenever the mode cannot heat rooms, which includes pure Cooling (dhw also False), where hot water is not running either. Banner then wrongly says 'DHW only'. Condition is 'space heating blocked by pump mode', not 'DHW only'. sv and de repeat the same 'DHW only' error. | custom_components/heatpump_optimizer/pump_signals.py:341 "return self.mode_observed and not self.mode_owned and not self.mode.space_heat"; custom_components/heatpump_optimizer/pump_mode.py MODE_COOL space_heat=False dhw=False; sensor.py:1539 "space_blocked": bool(...) | en, sv, de: No space heating in the pump's current mode: the house trace is the plan's promise, not what the pump is executing. |
+| `plan.space_blocked` | DHW only — no space heating: the house trace is the plan's promise, not what the pump is executing. | space_blocked is true whenever the mode cannot heat rooms, which includes pure Cooling (dhw also False), where hot water is not running either. Banner then wrongly says 'DHW only'. Condition is 'space heating blocked by pump mode', not 'DHW only'. sv and de repeat the same 'DHW only' error. | custom_components/heatpump_optimizer/pump_signals.py:340 "return self.mode_observed and not self.mode_owned and not self.mode.space_heat"; custom_components/heatpump_optimizer/pump_mode.py MODE_COOL space_heat=False dhw=False; sensor.py:1539 "space_blocked": bool(...) | en, sv, de: No space heating in the pump's current mode: the house trace is the plan's promise, not what the pump is executing. |
 | `slots.released_one` | {n} slot was released to protect the house or the tank. | n counts released plan TIME STEPS summed over both channels (one entry per step per channel in released_space/released_dhw), not slots; a single slot spans several steps so a one-slot release can read as many slots. Only forced-off pins are ever released. | custom_components/heatpump_optimizer/coordinator.py:2466-2471 "{\"step\": i, \"reason\": \"safety\"} for i in result.manual_released_space"; www/heatpump-optimizer-card.js:11553 "released = released_space.length + released_dhw.length" | en, sv, de: {n} plan step was released to protect the house or the tank. |
 | `slots.released_other` | {n} slots were released to protect the house or the tank. | n counts released plan TIME STEPS summed over both channels (one entry per step per channel in released_space/released_dhw), not slots; a single slot spans several steps so a one-slot release can read as many slots. Only forced-off pins are ever released. Swedish text uses the same word for one and many. | custom_components/heatpump_optimizer/coordinator.py:2466-2471 "{\"step\": i, \"reason\": \"safety\"} for i in result.manual_released_space"; www/heatpump-optimizer-card.js:11553 "released = released_space.length + released_dhw.length" | en, sv, de: {n} plan steps were released to protect the house or the tank. |
 | `whatif.no_windows_hint` | No windows: hot water is never required, so the tank is only kept above its idle minimum. | Empty window list means windows are not active. If the schedule is enabled (default True, const.py:1574) the planner derives windows from the learned hourly draw pattern (falling back to full day); if schedule is disabled hot water is required around the clock (FULL_DAY). It is never 'never required'; idle minimum applies only outside the (derived) windows. Same wrong claim in sv and de. | custom_components/heatpump_optimizer/dhw_planner.py:436-446 "if params.dhw_windows_active: ... if not params.dhw_schedule_enabled: return [FULL_DAY], False ... pattern = params.effective_dhw_draw_pattern()"; custom_components/heatpump_optimizer/thermal_model.py:860 "return bool(self.dhw_schedule_enabled and self.dhw_windows)"; custom_components/heatpump_optimizer/dhw_planner.py:904 "floor_temps = np.where(in_window, dhw_min_temp, idle_min_temp)" | en, sv, de: No windows: the optimizer plans hot water from your learned usage pattern, or keeps it ready around the clock when the hot water schedule is turned off. |
@@ -49,6 +49,7 @@ Each row was judged by reading the code that decides it: where the card renders
 | `errors.invalid_window_time` | The hot water window “{window}” is not a valid time. | The same check also fires for a silent/off (quiet) window, not only hot-water windows, so naming it a hot water window is wrong for quiet windows. | custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js:13256-13264 "draft.dhwWindows.find(...) \|\| (draft.quietWindows \|\| []).find(...)" -> L("errors.invalid_window_time"); custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js:13375-13384 same | en, sv, de: The window “{window}” is not a valid time. |
 | `score.part_overall` | The average of whichever scores below have evidence. Not a score of its own. | Overall averages only the heat pump (machine) and driving (operation) grades; the house (envelope) grade is shown in the breakdown but excluded (compose_scores docstring: averaging the house in made a DHW-only cheap-hour plan read 5/100). The card also never reads this key (scoreParts/scoreRowTitle only use part_envelope/machine/operation). | custom_components/heatpump_optimizer/coordinator.py:3381 "available = [part[0] for part in (machine, operation) if part[0] is not None]"; coordinator.py:3392 "round(float(np.mean(available))" | en, sv, de: The average of the heat pump and driving scores, whichever have evidence. The house score is shown but not averaged in. Not a score of its own. |
 | `score.reason_cop_unmeasurable` | COP cannot be measured on this install, so the heat pump is not graded: it needs a heat energy meter or a thermal power meter covering the heating circuit, hot water included, and a power meter, neither an estimate. | The machine grade calls cop_measured(dhw=False), so heat_sees_dhw is NOT required: a meter that does not see hot water still yields a grade (hot-water bands just need the extra declaration). Also with a heat counter the power side must be the electric counter, not any power entity. Moderate confidence on wording: 'hot water included' is the only overclaim. | custom_components/heatpump_optimizer/thermal_model.py:1340-1343 "self.measured_heat and self.cop_electric() and not (self.heat_estimated or self.power_estimated) and (self.heat_sees_dhw or not dhw)"; coordinator.py:10618 "probe_install(...).cop_measured(False)" | en, sv, de: COP cannot be measured on this install, so the heat pump is not graded: it needs a heat energy meter or a thermal power meter covering the heating circuit and a power meter, neither an estimate. |
+| `advisor.refit_detail` | Refitted from {days} settled days ({pairs} intervals) since the last boost or restore; about ±7-10 % uncertain. Nothing changes until you accept. | The refit publishes one band, `band_percent` = REFIT_BAND_PERCENT = 10, and `_refit_disagrees` judges the refit against that band alone; the 7 is the pre-study figure in the `#:` comment over the constant, which no code reads. The settled span and the accept gate hold: the span starts after the last boost-tagged pair plus settle, or after the last restore, whichever is later; the advice applies nothing, and only the `restore_learned_snapshot` call with `source: refit` adopts it. | accuracy.py:651 `REFIT_BAND_PERCENT = 10`; accuracy.py:776 `"band_percent": REFIT_BAND_PERCENT`; coordinator.py:3278 `band = float(refit.get("band_percent") or 0.0) / 100.0`; accuracy.py:659-663 `bounds.append(utc_shift(max(tagged), settle))` ... `return max(bounds)`; coordinator.py:1391 `since=tracker.evidence_since`; accuracy.py:192-193 `restart_evidence` sets `evidence_since`, called at coordinator.py:9590 in `_apply_learner_payloads`; services.py:1220-1227 `from_refit = data.get("source") == "refit"` ... `async_adopt_heat_loss_refit(coord)`; www/heatpump-optimizer-card.js:11079 the accept button sends `{ source: "refit" }` | en, sv, de: the band is the published `band_percent`, rendered as `±{band} %` (`restartRows` passes `refit.band_percent`) |
 
 ### Unverifiable
 
@@ -69,27 +70,27 @@ Each row was judged by reading the code that decides it: where the card renders
 
 | key | claim | evidence |
 |---|---|---|
-| `health.fresh` | input has a reading within its age limit / plan within limit | <home>/wt-card/custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js:10468 "rows.push(row(key, entityOf(key), "ok", ... L("health.fresh"))" for inputs not in problems; <home>/wt-card/custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js:10488 "stale ? health.stale : health.fresh" with stale = age.minutes > age.limit |
-| `health.stale` | plan older than limit, or input past its age limit | <home>/wt-card/custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js:10459 "p.problem === "stale" ? L("health.stale")"; <home>/wt-card/custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js:10485 "const stale = age.minutes > age.limit" (limit = max(3*interval, 90 min), :9647) |
-| `health.p_unavailable` | entity state is unavailable/unknown | <home>/wt-card/custom_components/heatpump_optimizer/inputs.py:939 "if not has_value(state): reading.problem = "unavailable"" |
-| `health.p_missing_entity` | configured entity id not in state machine | <home>/wt-card/custom_components/heatpump_optimizer/inputs.py:934 "state = self.hass.states.get(entity_id); if state is None: ... missing_entity" |
-| `health.p_not_numeric` | state not parseable as number | <home>/wt-card/custom_components/heatpump_optimizer/inputs.py:~1000 "except (TypeError, ValueError): reading.problem = "not_numeric"" |
-| `health.p_implausible` | value outside plausible range | <home>/wt-card/custom_components/heatpump_optimizer/inputs.py:1011 "if not plausible_c(key, value): ... _set_problem(reading, "implausible")" |
-| `health.p_unknown_value` | text state not among accepted values | <home>/wt-card/custom_components/heatpump_optimizer/inputs.py:1062 "reading.problem = "unknown_value"" |
-| `health.p_not_boolean` | state not parseable as yes/no flag | <home>/wt-card/custom_components/heatpump_optimizer/inputs.py:1097 "reading.problem = "not_boolean"" |
-| `health.p_unknown_unit` | unit not recognised for power/flow conversion | <home>/wt-card/custom_components/heatpump_optimizer/inputs.py:1115 "reading.problem = "unknown_unit""; 1132 |
-| `health.p_not_configured` | no entity configured for slot | <home>/wt-card/custom_components/heatpump_optimizer/inputs.py:930 "if not entity_id: reading.problem = "not_configured""; (returns before health.record and details() skips entity_id None (:181), so the card never receives it; harmless) |
-| `health.ago` | {age} = minutes since reading, formatted | <home>/wt-card/custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js:10463 "L("health.ago", { age: fmtMinutes(age) })" from p.age_minutes (inputs.py:188 round(reading.age_minutes,1)); fresh rows from input_ages_minutes (inputs.py:169-174) |
-| `health.limit` | {limit} = max age allowed for that input | <home>/wt-card/custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js:10464 "L("health.limit", { limit: fmtMinutes(limit) })" from max_age_minutes; <home>/wt-card/custom_components/heatpump_optimizer/inputs.py:193 "max_age_minutes": reading.max_age_minutes |
-| `health.no_age` | shown when problem has no age (never read) | <home>/wt-card/custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js:10463 "p.age_minutes !== null ? ago : L("health.no_age")"; <home>/wt-card/custom_components/heatpump_optimizer/inputs.py:188 age_minutes None when no timestamp |
-| `health.pill_ok` | zero input problems | <home>/wt-card/custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js:10413 "n === 0 ? L("health.pill_ok")" n = attributes.problems.length |
-| `health.pill_one` | exactly one problem | <home>/wt-card/custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js:10414 "n === 1 ? health.pill_one" |
-| `health.pill_other` | {n} = number of problems | <home>/wt-card/custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js:10414 "L(..., { n })" n = problems.length (binary_sensor.py:111 "problems": data.get("input_problems")) |
-| `health.solved` | {age} since last optimization | <home>/wt-card/custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js:10487 "L("health.solved", { age: fmtMinutes(age.minutes) })" from _last_optimization state (:9638) |
-| `health.next_solve` | {age} until next scheduled optimization | <home>/wt-card/custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js:10481 "due > 0.5 ? L("health.next_solve", { age: fmtMinutes(due) })" due from _next_optimization state; sensor.py:840 |
-| `health.next_due` | next solve time already reached | <home>/wt-card/custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js:10481 "due > 0.5 ? next_solve : L("health.next_due")" (due<=0.5 min incl. overdue) |
-| `health.steps` | {n} = number of forecast steps in plan | <home>/wt-card/custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js:10482 "L("health.steps", { n: steps.length })" steps = plan.forecast(space\|\|dhw) |
-| `health.solve_time` | {s} = solve duration seconds | <home>/wt-card/custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js:10483 "L("health.solve_time", { s: (ms / 1000).toFixed(1) })"; coordinator.py:3150 "solve_time_ms": result.solve_time_ms |
+| `health.fresh` | input has a reading within its age limit / plan within limit | custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js:10468 "rows.push(row(key, entityOf(key), "ok", ... L("health.fresh"))" for inputs not in problems; custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js:10488 "stale ? health.stale : health.fresh" with stale = age.minutes > age.limit |
+| `health.stale` | plan older than limit, or input past its age limit | custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js:10459 "p.problem === "stale" ? L("health.stale")"; custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js:10485 "const stale = age.minutes > age.limit" (limit = max(3*interval, 90 min), :9647) |
+| `health.p_unavailable` | entity state is unavailable/unknown | custom_components/heatpump_optimizer/inputs.py:939 "if not has_value(state): reading.problem = "unavailable"" |
+| `health.p_missing_entity` | configured entity id not in state machine | custom_components/heatpump_optimizer/inputs.py:934 "state = self.hass.states.get(entity_id); if state is None: ... missing_entity" |
+| `health.p_not_numeric` | state not parseable as number | custom_components/heatpump_optimizer/inputs.py:~1000 "except (TypeError, ValueError): reading.problem = "not_numeric"" |
+| `health.p_implausible` | value outside plausible range | custom_components/heatpump_optimizer/inputs.py:1010-1014 "if not plausible_c(key, value): ... _set_problem(reading, "implausible")" |
+| `health.p_unknown_value` | text state not among accepted values | custom_components/heatpump_optimizer/inputs.py:1062 "reading.problem = "unknown_value"" |
+| `health.p_not_boolean` | state not parseable as yes/no flag | custom_components/heatpump_optimizer/inputs.py:1097 "reading.problem = "not_boolean"" |
+| `health.p_unknown_unit` | unit not recognised for power/flow conversion | custom_components/heatpump_optimizer/inputs.py:1115 "reading.problem = "unknown_unit""; 1132 |
+| `health.p_not_configured` | no entity configured for slot | custom_components/heatpump_optimizer/inputs.py:930 "if not entity_id: reading.problem = "not_configured""; (returns before health.record and details() skips entity_id None (:181), so the card never receives it; harmless) |
+| `health.ago` | {age} = minutes since reading, formatted | custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js:10463 "L("health.ago", { age: fmtMinutes(age) })" from p.age_minutes (inputs.py:188 round(reading.age_minutes,1)); fresh rows from input_ages_minutes (inputs.py:169-174) |
+| `health.limit` | {limit} = max age allowed for that input | custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js:10464 "L("health.limit", { limit: fmtMinutes(limit) })" from max_age_minutes; custom_components/heatpump_optimizer/inputs.py:193 "max_age_minutes": reading.max_age_minutes |
+| `health.no_age` | shown when problem has no age (never read) | custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js:10463 "p.age_minutes !== null ? ago : L("health.no_age")"; custom_components/heatpump_optimizer/inputs.py:188 age_minutes None when no timestamp |
+| `health.pill_ok` | zero input problems | custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js:10413 "n === 0 ? L("health.pill_ok")" n = attributes.problems.length |
+| `health.pill_one` | exactly one problem | custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js:10414 "n === 1 ? health.pill_one" |
+| `health.pill_other` | {n} = number of problems | custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js:10414 "L(..., { n })" n = problems.length (binary_sensor.py:111 "problems": data.get("input_problems")) |
+| `health.solved` | {age} since last optimization | custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js:10487 "L("health.solved", { age: fmtMinutes(age.minutes) })" from _last_optimization state (:9638) |
+| `health.next_solve` | {age} until next scheduled optimization | custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js:10481 "due > 0.5 ? L("health.next_solve", { age: fmtMinutes(due) })" due from _next_optimization state; sensor.py:840 |
+| `health.next_due` | next solve time already reached | custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js:10481 "due > 0.5 ? next_solve : L("health.next_due")" (due<=0.5 min incl. overdue) |
+| `health.steps` | {n} = number of forecast steps in plan | custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js:10482 "L("health.steps", { n: steps.length })" steps = plan.forecast(space\|\|dhw) |
+| `health.solve_time` | {s} = solve duration seconds | custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js:10483 "L("health.solve_time", { s: (ms / 1000).toFixed(1) })"; coordinator.py:3150 "solve_time_ms": result.solve_time_ms |
 | `health.learn_accuracy_why` | accuracy row waits for first scored interval | sensor.py:~1937 "if payload_number(accuracy.get("temperature_mae")) is None: return "first_scored_interval"" |
 | `health.model_from` | row shows the learner's sample count once its learned flag is set | coordinator.py:7973 "house_heat_loss_learned": house_loss_converged(self._house_heat_loss_samples); coordinator.py:7981 "lower_floor_loss_learned": self._lower_floor_loss_samples > 0; coordinator.py:7963 cooling_samples > 0; card 10632 |
 | `health.model_estimate` | house row not yet learned and no learner phase published: value is the settings estimate, no samples | coordinator.py:3250 round(params.house_heat_loss_base * scale, 4) with scale default 1.0 (const DEFAULT_HOUSE_HEAT_LOSS_SCALE); card 10633 : house ? house.text : L("health.model_estimate") |
@@ -121,7 +122,7 @@ Each row was judged by reading the code that decides it: where the card renders
 | `health.learner_settling` | past the count gate, value still moving; pct = EWMA walk traversed | learner_progress.py:135-136 phase = "settling"; progress = learner.walked(n); coordinator.py:1712-1715 _solar_aperture_walked = 1 - (1 - ALPHA) ** walk |
 | `health.learner_settling_any` | settling with no progress figure | learner_progress.py:135-136 walked None -> progress None; card 10585 |
 | `health.model_unobservable` | house heat loss is not observable without a power meter | card 10630 observable = inputAssigned(plan, "heat_pump_power_entity"); thermal_model.py:1645 heat_loss_basis: 2 if earned and measured_heat else 1 if measured_power else 0; thermal_model.py:1619-1635 learner_unmetered |
-| `health.cop_measured` | age of the last measured COP | coordinator.py:7989 "measured_cop_at": self._measured_cop.at.isoformat(); accuracy.py:861 at = when that COP folded; card 10664 |
+| `health.cop_measured` | age of the last measured COP | coordinator.py:7989 "measured_cop_at": self._measured_cop.at.isoformat(); accuracy.py:925 "self.at = at", recorded at coordinator.py:5424 with dt_util.now(); card 10664 |
 | `health.cop_reason_heat_metered` | COP measured by a heat meter | accuracy.py:845 return COP_ESTIMATED if estimated else COP_HEAT_METERED; thermal_model.py:1339-1345 cop_measured |
 | `health.cop_reason_not_measurable` | no heat reading, shown efficiency is the model's own; heat or thermal power meter incl. hot water would measure it | accuracy.py:843-844 if not measured_heat: return COP_NOT_MEASURABLE; thermal_model.py:1439-1441 measured_heat = CONF_HEAT_ENERGY_ENTITY or CONF_THERMAL_POWER_ENTITY; thermal_model.py:1343 (heat_sees_dhw or not dhw) |
 | `health.cop_reason_estimated_inputs` | power or heat reading is the pump's own estimate | accuracy.py:845 COP_ESTIMATED if estimated; coordinator.py:7993-7995 estimated=install.heat_estimated or install.power_estimated; thermal_model.py:1479-1485 _estimated(source,...) |
@@ -137,7 +138,7 @@ Each row was judged by reading the code that decides it: where the card renders
 | `health.cop_reason_blended_duty` | space and hot water shared the interval | coordinator.py:5384-5388 if modelled_cop is None: return COP_REFUSED_BLENDED; coordinator.py:5311 return None, False, None (mode neither space nor dhw) |
 | `health.cop_reason_observed_cop` | observed efficiency implausible | coordinator.py:5401-5402 if not np.isfinite(observed_cop) or observed_cop <= 0.1: return COP_REFUSED_OBSERVED |
 | `health.cop_reason_span_open` | waiting for the meter span to close | coordinator.py:5357-5358 if heat_energy.meter_of(self).counter: return COP_REFUSED_SPAN_OPEN |
-| `health.cop_reason_unaligned_meters` | heat and power meters not read at same moments | heat_energy.py:567 unaligned if got.elec_kw is None; heat_energy.py:554-556 docstring: refuses with unaligned without an electric delta at both instants |
+| `health.cop_reason_unaligned_meters` | heat and power meters not read at same moments | heat_energy.py:567 unaligned if got.elec_kw is None |
 | `health.cop_reason_counter_reset` | heat counter reset | heat_energy.py:462-463 elif heat_kwh < 0.0: self.refusal = SPAN_REFUSED_RESET |
 | `health.cop_reason_counter_rollover` | heat counter rolled over | heat_energy.py:464-465 elif heat_kwh > max_heat_kw * hours * HEAT_COUNTER_SLACK: self.refusal = SPAN_REFUSED_ROLLOVER |
 | `health.cop_reason_counter_resolution` | counter too coarse | heat_energy.py:139-141 if q is None or not expected_kwh > 0.0 or q / expected_kwh > HEAT_RESOLUTION_EPS: return SPAN_REFUSED_RESOLUTION |
@@ -145,11 +146,11 @@ Each row was judged by reading the code that decides it: where the card renders
 | `health.metric_heat_loss` | house loss in W per degree; no samples = settings estimate | sensor.py:2051 round(effective * 1000.0, 1); coordinator.py:3250 house_heat_loss_base * scale; const.py:1532 DEFAULT_HOUSE_HEAT_LOSS_SCALE = 1.0 |
 | `health.metric_solar` | window solar gain vs settings; >1 lets in more; no samples = settings value | coordinator.py:3683-3686 _solar_aperture scale 1.0 initial; coordinator.py:4297-4301 plan uses scale only if aperture_on and n >= SOLAR_APERTURE_MIN_SAMPLES else 1.0 |
 | `health.metric_cop` | COP row: still delivers as much heat per kWh; dash = not yet watched | card 10604-10614 value "—" with watched:false unless alarm or watched_buckets > 0; coordinator.py:9496 baseline shortfall |
-| `health.debug_off` | off; Start records a week of cycles into the diagnostics file | debugger.py:71 COLLECT_SPAN = timedelta(days=7); debugger.py:708-716 async_command start with no collector sets CONF_DEBUG_COLLECT True (entry reload starts it); diagnostics.py:408 debugger.capped(await collector.async_bundle(...)) |
+| `health.debug_off` | off; Start records a week of cycles into the diagnostics file | debugger.py:71 COLLECT_SPAN = timedelta(days=7); debugger.py:708-716 async_command start with no collector sets CONF_DEBUG_COLLECT True (entry reload starts it); diagnostics.py:413-414 debugger.capped(await collector.async_bundle(...)) |
 | `health.debug_active` | rows so far and days left | debugger.py:609 status rows: len(self.rows); card 10726 days = ceil((start + DEBUG_DAYS*864e5 - now)/864e5); debugger.py:545 now - started_at >= COLLECT_SPAN |
 | `health.debug_final` | finished; download to keep | debugger.py:545-546 now - self.started_at >= COLLECT_SPAN -> finalize; debugger.py:600-601 restart clears rows |
 | `health.debug_confirm` | starting again discards finished collection | debugger.py:600-601 restart(): self.started_at, self.final, self.rows, self.snapshots = None, False, [], []; debugger.py:714-715 elif action == "start" and collector.final: collector.restart(); card 11057-11060 first press arms |
-| `advisor.empty` | shown when every optional temperature sensor is already configured | custom_components/heatpump_optimizer/topology.py:1146 "candidates = [key for key in _ADVISOR_CANDIDATES if not config.get(key)]"; custom_components/heatpump_optimizer/topology.py:1147 returns None when none left; custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js:10931 "if (!rows.length)" |
+| `advisor.empty` | shown when every optional temperature sensor is already configured | custom_components/heatpump_optimizer/topology.py:1146 "candidates = [key for key in _ADVISOR_CANDIDATES if not config.get(key)]"; custom_components/heatpump_optimizer/topology.py:1147 returns None when none left; custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js:10930 "if (!rows.length)" |
 | `advisor.spread_note` | spread = how far apart model temperature predictions can sit across the sensor-pinned band | custom_components/heatpump_optimizer/topology.py:1116 "abs(float(getattr(ends[0], name)) - float(getattr(ends[1], name)))" max over _ADVISOR_SPREAD_FIELDS; custom_components/heatpump_optimizer/topology.py:1206 "spread_c" |
 | `advisor.unpriced_heading` | rows below are candidates the estimate does not price | custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js:10968 unpriced = rows.filter(!row.priced); custom_components/heatpump_optimizer/topology.py:1189-1196 "priced": False |
 | `advisor.reason_weather_backed` | outdoor temp already comes from weather entity; estimate cannot price a probe | custom_components/heatpump_optimizer/topology.py:1036 CONF_OUTDOOR_TEMP_ENTITY: "weather_backed"; custom_components/heatpump_optimizer/coordinator.py:6668-6674 "elif (forecast_outdoor := forecast_outdoor_now(self._weather_forecast" |
@@ -157,8 +158,8 @@ Each row was judged by reading the code that decides it: where the card renders
 | `advisor.reason_no_clamped_parameter` | DHW learners fit quantities with no clamp band the estimate sweeps | custom_components/heatpump_optimizer/topology.py:1042 CONF_DHW_TEMP_ENTITY: "no_clamped_parameter"; custom_components/heatpump_optimizer/topology.py:1163-1190 lanes only for indoor, lower floor, buffer |
 | `advisor.act_hint` | clicking a row lets you pick a sensor on the Setup page | custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js:10985-10986 "openSetupSlot(host, key, ev)"; custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js:10999 "host.dialog.page = "setup"" |
 | `advisor.inbox_empty` | no rows means plan is already as cheap as settings allow | custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js:10266-10268 "rows.length ? ... : feedback.length ? "" : <div class=empty>inbox_empty"; custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js:10055-10078 advisorRow returns null when not installed or at recommendation |
-| `advisor.optin_heading` | listed advice appears once its option is turned on | custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js:10260-10264 optIn rows each with "advisor.step_*" and open_options; custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js:10028-10032 disabled-by-default advisors never read |
-| `advisor.value_month` | rounded monthly money per row in plan currency | custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js:10210-10212 "Math.round(row.value), currency: host.plan.currency()"; dhw custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js:10174 "perDay * DAYS_PER_MONTH" (30); degree custom_components/heatpump_optimizer/price_tiles.py:97 per_month; gap custom_components/heatpump_optimizer/sensor.py:2990 sek_per_month |
+| `advisor.optin_heading` | listed advice appears once its option is turned on | custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js:10260-10264 optIn rows each with "advisor.step_*" and open_options; custom_components/heatpump_optimizer/coordinator.py:10723 price_tiles_enabled gate; sensor.py:2130, 2809, 3011 _attr_entity_registry_enabled_default = False (wood, fuse, frequency: no options step enables them; see the sweep) |
+| `advisor.value_month` | rounded monthly money per row in plan currency | custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js:10210-10212 "Math.round(row.value), currency: host.plan.currency()"; dhw custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js:10174 "perDay * DAYS_PER_MONTH" (30); degree custom_components/heatpump_optimizer/price_tiles.py:91 "return delta * MONTH_HOURS / horizon_hours"; gap custom_components/heatpump_optimizer/sensor.py:2990 sek_per_month |
 | `advisor.no_value` | row has no money figure | custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js:10210 "row.value === null ? L("advisor.no_value")"; valve value:null at 10186; dhw null when perDay<=0 at 10174 |
 | `advisor.unavailable` | shown when an advisor sensor is unavailable (or unknown without a reason) | custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js:10061 "if (st.state === "unavailable") return { kind, status: "error" }"; custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js:10066 unknown without waiting_for -> error; custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js:10207 L("advisor.unavailable") |
 | `advisor.gap_detail` | the model prices the missing sensor | custom_components/heatpump_optimizer/sensor.py:2988-2990 native_value = gaps[0]["sek_per_month"]; custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js:10157-10163 value=sensor state, title gap_title |
@@ -173,9 +174,8 @@ Each row was judged by reading the code that decides it: where the card renders
 | `advisor.applied` | valve target written as the manual setpoint | custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js:11063-11071 callService assign_entity {key: "mixing_valve_target_entity", entity_id: "", manual_setpoint}; custom_components/heatpump_optimizer/services.py:865-872 options[CONF_MIXING_VALVE_TARGET] = float(setpoint) |
 | `advisor.applied_setpoint` | hot-water setpoint written | custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js:11020-11027 callService apply_schedule {dhw_setpoint: to}; custom_components/heatpump_optimizer/services.py:480 dhw_setpoint accepted |
 | `advisor.refit_title` | restart heat-loss model at refit scale (current scale) | custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js:10135-10137 to=refit.scale.toFixed(2), from=current_scale; custom_components/heatpump_optimizer/coordinator.py:1408-1430 async_adopt_heat_loss_refit sets thermal["house_heat_loss_scale"] = scale |
-| `advisor.refit_detail` | refit from settled days/intervals since last boost or restore, +-7-10 %, nothing changes until accepted | custom_components/heatpump_optimizer/accuracy.py:655-662 _refit_start "after the last boost-tagged pair plus settle, and after the last restore"; custom_components/heatpump_optimizer/accuracy.py:651 REFIT_BAND_PERCENT=10 (comment states 7-10 %); custom_components/heatpump_optimizer/coordinator.py:1363 "Recommend-only" |
 | `advisor.refit_wait_title` | a refit is pending (drift alarm, no refit yet) | custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js:10130,10139-10141 drift_alarm and refit.scale not finite |
-| `advisor.refit_wait_detail` | refit needs {need} settled days; {days} so far | custom_components/heatpump_optimizer/accuracy.py:779 "required_days": REFIT_SETTLED_DAYS (3.0); custom_components/heatpump_optimizer/accuracy.py:704 "days < REFIT_SETTLED_DAYS or pairs < 24.0 / max(dt_hours, 1e-6)" |
+| `advisor.refit_wait_detail` | refit needs {need} settled days; {days} so far | custom_components/heatpump_optimizer/accuracy.py:779 "required_days": REFIT_SETTLED_DAYS (3.0); custom_components/heatpump_optimizer/accuracy.py:707 "days < REFIT_SETTLED_DAYS or pairs < 24.0 / max(dt_hours, 1e-6)" |
 | `advisor.restore_title` | restore the last good snapshot taken on {when} | custom_components/heatpump_optimizer/coordinator.py:1376-1380 restore taken_at = ring.best_restore(); custom_components/heatpump_optimizer/snapshots.py:237-247 undo_target -> best_restore |
 | `advisor.restore_detail` | last known-good learned state captured before drift began | custom_components/heatpump_optimizer/snapshots.py:207-214 skips unhealthy/alarmed snapshots and "taken_day >= self._streak_started" |
 | `advisor.restarted` | learned model restarted after accepting | custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js:11076-11080 callService restore_learned_snapshot then note(L("advisor.restarted")); custom_components/heatpump_optimizer/coordinator.py:1408-1430 applies learner payloads |
@@ -187,10 +187,10 @@ Each row was judged by reading the code that decides it: where the card renders
 | `savings.old_basis` | month booked against another (older) reference | custom_components/heatpump_optimizer/ledger.py:513 "old_basis = self.meta_mean(key, REFERENCE_BASIS_META) != REFERENCE_BASIS" |
 | `savings.below_meter_floor` | no saving is stated for this month (meter floor) | custom_components/heatpump_optimizer/ledger.py:515-516,520 "withheld = old_basis or below_floor"; "savings_sek: None if withheld else saved" |
 | `savings.meter_floor_note` | no saving stated when baseline used under half the energy the meter recorded | custom_components/heatpump_optimizer/ledger.py:199 "booked_kwh < METER_FLOOR * metered_kwh" with METER_FLOOR = 0.5 (ledger.py:115) |
-| `savings.wood_note` | saving includes wood heat; firewood cost not counted; shown when wood configured | custom_components/heatpump_optimizer/wood_fuel.py:105 "return bool((data.get(\"wood_fuel\") or {}).get(\"show_whatif\"))"; custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js:15874; custom_components/heatpump_optimizer/ledger.py:479-481 |
+| `savings.wood_note` | saving includes wood heat; firewood cost not counted; shown when wood configured | custom_components/heatpump_optimizer/wood_fuel.py:105 "return bool((data.get(\"wood_fuel\") or {}).get(\"show_whatif\"))"; custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js:15874; custom_components/heatpump_optimizer/ledger.py:375-381 savings lines booked in kWh, no firewood cost line |
 | `savings.empty` | shown when there are no savings months | custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js:15822 "if (!rows.length)"; custom_components/heatpump_optimizer/ledger.py:499 rows only for months with savings_baseline |
 | `receipt.closed` | the receipt is for a closed (rolled-over) month | custom_components/heatpump_optimizer/ledger.py roll_receipts: "closed = sorted(k for k in ledger.months if k < current and k not in reports)"; custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js:10846 |
-| `receipt.saved` | month's saving vs a modelled plain thermostat reference, amount/pct from the savings row | custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js:10827 "row && finiteNum(row.savings_sek)"; custom_components/heatpump_optimizer/ledger.py:513-526 "savings_sek: None if withheld else saved"; reference = thermostat, ledger.py:62 REFERENCE_BASIS |
+| `receipt.saved` | month's saving vs a modelled plain thermostat reference, amount/pct from the savings row | custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js:10827 "row && finiteNum(row.savings_sek)"; custom_components/heatpump_optimizer/ledger.py:513-526 "savings_sek: None if withheld else saved"; reference = thermostat, optimizer.py:5953-5981 _compute_baseline_power steps self.model.simulate_step, booked as savings_baseline at ledger.py:375 |
 | `receipt.not_priced` | wear line shows 'not priced' when compressor starts exist but no wear was booked | custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js:10822 "!basis.includes(\"wear\") && ... compressor_starts > 0"; custom_components/heatpump_optimizer/coordinator.py:10509 "if wear > 0:" books wear line |
 | `receipt.peak` | capacity line basis is the month's billed peak in kW | custom_components/heatpump_optimizer/ledger.py:306 "data[\"meta\"][CAPACITY_PEAK_META] = {\"sum\": float(peak_kw)"; ledger.py:688-691 capacity_peak_kw; custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js:10813 |
 | `receipt.starts` | compressor start count for the month | custom_components/heatpump_optimizer/coordinator.py:10538 "compressor_starts=self._start_counter.month_count(month)"; custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js:10811 |
@@ -220,9 +220,9 @@ Each row was judged by reading the code that decides it: where the card renders
 | `reasons.dhw_ready` | DHW step that prepares the tank for a demand window | custom_components/heatpump_optimizer/optimizer.py:2086 "ready_temps[i] > 0" -> REASON_DHW_READY |
 | `reasons.legionella` | legionella cycle step | custom_components/heatpump_optimizer/optimizer.py:2083 "i == legionella_step" -> REASON_LEGIONELLA |
 | `reasons.manual_plan` | step forced on by user manual plan | custom_components/heatpump_optimizer/optimizer.py:2220 "out[i] = REASON_MANUAL" for pinned-on steps |
-| `reasons.pump_mode` | step paused because the pump operating mode cannot serve the channel | custom_components/heatpump_optimizer/optimizer.py:2160 "REASON_PUMP_MODE if reason in IDLE_REASONS"; <home>/wt-card/custom_components/heatpump_optimizer/pump_signals.py:341 "not self.mode.space_heat" |
+| `reasons.pump_mode` | step paused because the pump operating mode cannot serve the channel | custom_components/heatpump_optimizer/optimizer.py:2160 "REASON_PUMP_MODE if reason in IDLE_REASONS"; custom_components/heatpump_optimizer/pump_signals.py:340 "not self.mode.space_heat" |
 | `reasons.pump_mode_dhw` | no DHW because mode (heat-only or cooling) cannot make hot water | custom_components/heatpump_optimizer/pump_mode.py MODES: MODE_HEAT dhw=False, MODE_COOL dhw=False; custom_components/heatpump_optimizer/pump_signals.py:345 "not self.mode.dhw"; card www/heatpump-optimizer-card.js:9112 "pumpModeChannel.field === \"dhw_power\"" |
-| `reasons.pump_mode_space` | no heating because mode (hot-water-only or cooling) cannot heat rooms | custom_components/heatpump_optimizer/pump_mode.py MODES: MODE_COOL space_heat=False, MODE_DHW space_heat=False; custom_components/heatpump_optimizer/pump_signals.py:341 "not self.mode.space_heat" |
+| `reasons.pump_mode_space` | no heating because mode (hot-water-only or cooling) cannot heat rooms | custom_components/heatpump_optimizer/pump_mode.py MODES: MODE_COOL space_heat=False, MODE_DHW space_heat=False; custom_components/heatpump_optimizer/pump_signals.py:340 "not self.mode.space_heat" |
 | `reasons.idle` | step with no heating | custom_components/heatpump_optimizer/optimizer.py:1942 "codes = np.full(n, REASON_IDLE"; 2158 power <= threshold |
 | `reasons.boost` | energy from a boost the user turned on | custom_components/heatpump_optimizer/boost.py:400 "action[\"space_reason\"] = REASON_BOOST"; coordinator.py:4108 global boost mode |
 | `reasons.comfort_mode` | energy from user-selected comfort mode | custom_components/heatpump_optimizer/coordinator.py:4105 "space_reason\": REASON_COMFORT_MODE" |
@@ -250,22 +250,22 @@ Each row was judged by reading the code that decides it: where the card renders
 | `menu.add_slot_dhw` | menu button adds a hot water slot at the click time | custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js:12139,12147-12150 "SlotModel.add(runs, at, PLAN_STEP_MS, bounds)" |
 | `menu.add_slot_space` | menu button adds a heating slot at the click time | custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js:12139,12147-12150 |
 | `slots.no_plan_to_pin` | nothing to pin when no plan | custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js:11593-11596 "if (!Object.keys(payload).length) ... slots.no_plan_to_pin"; 11586 "if (!forecastOf(channel).length) continue" |
-| `slots.pinned_result` | pinned; kept unless it would take the house or tank below limits | custom_components/heatpump_optimizer/optimizer.py:4161-4175 safety-release loop frees forced-off pins that breach hard lines; manual_plan.py:20-22 |
+| `slots.pinned_result` | pinned; kept unless it would take the house or tank below limits | custom_components/heatpump_optimizer/optimizer.py:4161-4175 safety-release loop frees forced-off pins that breach hard lines |
 | `slots.back_to_auto_result` | after clearing, planning is automatic again | custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js:11634-11642 callService clear_manual_plan then reset() |
 | `slots.pinned_status` | slots are pinned while a manual override is active | custom_components/heatpump_optimizer/coordinator.py:8554-8556 "if override is None or override.is_expired(...): return None" else active True; www/heatpump-optimizer-card.js:6902-6908 manualOverride() |
 | `whatif.slots_hint` | drag/resize/right-click edit slots in bottom lanes; Apply pins them for {hours} h | custom_components/heatpump_optimizer/services.py:1122 "expires_at = utc_shift(now, timedelta(hours=MANUAL_PLAN_WINDOW_HOURS))"; custom_components/heatpump_optimizer/const.py:1647 "MANUAL_PLAN_WINDOW_HOURS: Final = 20"; custom_components/heatpump_optimizer/sensor.py:1489 "manual_plan_window_hours": MANUAL_PLAN_WINDOW_HOURS (fills {hours} via custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js:12655); card contextmenu handler custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js:12556,12464 (right-click opens add/remove menu) |
 | `whatif.zoom_limit_hint` | when zoomed, editing stops at visible edge; dragging a slot to the edge pans | custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js:11456-11458 viewLimitsEditing "p.visibleEnd < Math.min(p.applyEnd, p.planEnd) - 1000"; custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js:12389 autopan "clientX > rect.left + rect.width - AUTOPAN_MARGIN_PX" |
-| `whatif.schedule_hint` | the heating hours/windows below are recurring daily settings the optimizer plans against, not just today | custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js:13351 saves via apply_schedule {day_start_hour, day_end_hour, dhw_windows}; custom_components/heatpump_optimizer/optimizer.py:2525 "day, night, start, end = self._comfort_pair(when)" |
+| `whatif.schedule_hint` | the heating hours/windows below are recurring daily settings the optimizer plans against, not just today | custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js:13302-13310 onSaveSchedule calls apply_schedule {day_start_hour, day_end_hour, dhw_windows}; custom_components/heatpump_optimizer/optimizer.py:2525 "day, night, start, end = self._comfort_pair(when)" |
 | `whatif.setback_hint` | outside heating hours the night (lower) comfort temperature applies | custom_components/heatpump_optimizer/optimizer.py:2525-2538 "if start <= hour < end: return day; return night" |
 | `whatif.quiet_hint` | Silent caps the compressor in the window; Off means no space heating or hot water scheduled and nothing extra written | custom_components/heatpump_optimizer/quiet_windows.py:416-426 silent_cap_kw returns max(measured\|fraction, CAPACITY_FLOOR_FRACTION)*p_max; custom_components/heatpump_optimizer/optimizer.py:4522 "power_caps = np.where(off_mask, 0.0, power_caps)"; custom_components/heatpump_optimizer/dhw_planner.py:1102 "forced_off = _forced_off_with(forced_off, off_steps, n_steps)" |
 | `whatif.quiet_not_enforced` | silent row shown as not enforced when the optimizer cannot hold the control | custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js:12960-12962 "markSilent = notEnforced && notEnforced !== 'false'"; custom_components/heatpump_optimizer/quiet_windows.py:533-534 "if silent_unenforceable(config, get_state): out['quiet_silent_not_enforced'] = 'true'"; custom_components/heatpump_optimizer/sensor.py:123-124 |
 | `whatif.quiet_frac` | fraction of power kept during silent mode | custom_components/heatpump_optimizer/quiet_windows.py:424-426 "if fraction >= 1.0: return None; return max(fraction, CAPACITY_FLOOR_FRACTION) * float(p_max)"; custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js:13012 slider min 0.6 max 1 |
-| `whatif.idle_status` | simulating changes nothing; saving replaces the configured schedule | custom_components/heatpump_optimizer/services.py:767 "results[entry_id] = await coord.async_simulate(overrides)"; custom_components/heatpump_optimizer/coordinator.py:11257 "scratch_params = copy.deepcopy(params)" -> async_simulate runs on scratch copies; custom_components/heatpump_optimizer/services.py:1001 apply_schedule (handle_apply_schedule :944) writes entry options (async_update_entry) |
+| `whatif.idle_status` | simulating changes nothing; saving replaces the configured schedule | custom_components/heatpump_optimizer/services.py:767 "results[entry_id] = await coord.async_simulate(overrides)"; custom_components/heatpump_optimizer/coordinator.py:11257 "scratch_params = copy.deepcopy(params)" -> async_simulate runs on scratch copies; custom_components/heatpump_optimizer/services.py:944 handle_apply_schedule, :1089 writes entry options (async_update_entry) |
 | `whatif.temperatures_hint` | comfort slider is the heating-day house temperature; DHW minimum is the floor inside a demand window; both simulated like the schedule | custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js:13341-13346 overrides {target_temp, comfort_temp_day: draft.comfort, dhw_min_temperature}; custom_components/heatpump_optimizer/dhw_planner.py:904 "np.where(in_window, dhw_min_temp, idle_min_temp)"; custom_components/heatpump_optimizer/optimizer.py:2527-2531 day temp used only start<=hour<end |
 | `whatif.cap_no_setpoint` | DHW minimum slider is capped at {t} C, far enough below setpoint to leave a band | custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js:12906-12909 dhwMinCeiling = published dhw_min_temperature_max else DHW_MIN_FALLBACK; custom_components/heatpump_optimizer/sensor.py:1407 "round(value - DHW_MIN_TEMP_SETPOINT_MARGIN, 1)" |
 | `whatif.cap_with_setpoint` | cap is {t}; band {band} C below {setpoint} C setpoint | custom_components/heatpump_optimizer/sensor.py:1407 "value - DHW_MIN_TEMP_SETPOINT_MARGIN"; custom_components/heatpump_optimizer/const.py:1384 "DHW_MIN_TEMP_SETPOINT_MARGIN: Final = 5.0"; custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js:12768-12772 band = setpoint - ceiling |
 | `whatif.clamped_warning` | saved minimum above the cap is shown lowered on the slider and saving stores the lower value | custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js:12669-12672 "if (draft.dhwMin > ceiling) { clamped = draft.dhwMin; draft.dhwMin = ceiling; }"; custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js:13309 save sends dhw_min_temperature: draft.dhwMin |
-| `whatif.confirm_hint` | save replaces heating hours, DHW windows, temperatures and reloads the integration; press again to confirm | custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js:13285-13292 pendingSave then 8 s lapse; custom_components/heatpump_optimizer/__init__.py:398 "await hass.config_entries.async_reload(entry.entry_id)"; custom_components/heatpump_optimizer/__init__.py:345 add_update_listener; services.py:1001 apply_schedule fields |
+| `whatif.confirm_hint` | save replaces heating hours, DHW windows, temperatures and reloads the integration; press again to confirm | custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js:13285-13292 pendingSave then 8 s lapse; custom_components/heatpump_optimizer/__init__.py:398 "await hass.config_entries.async_reload(entry.entry_id)"; custom_components/heatpump_optimizer/__init__.py:345 add_update_listener; services.py:944 handle_apply_schedule fields |
 | `whatif.saved_result` | after saving the optimizer reloads and plans with new schedule | custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js:13311-13312 L("whatif.saved_result") after apply_schedule resolves; custom_components/heatpump_optimizer/__init__.py:398 async_reload |
 | `whatif.same_cost` | within 0.5 currency units per month of current plan | custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js:13441 "if (Math.abs(delta) < 0.5)"; custom_components/heatpump_optimizer/price_tiles.py:105 "monthly_cost_delta": round(per_month(spend, horizon_hours), 2) |
 | `whatif.cheaper_per_month` | simulated plan costs {amount} less per month than the current plan | custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js:13443-13447 "cheaper = delta < 0 ... amount: Math.abs(delta).toFixed(0)"; custom_components/heatpump_optimizer/price_tiles.py:103-105 spend = sim.predicted_cost + extra - live.predicted_cost; per_month |
@@ -308,7 +308,7 @@ Each row was judged by reading the code that decides it: where the card renders
 | `setup.no_valve_caption` | No mixing valve: delivery is not throttled | custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js:4388 ": [L(\"setup.no_valve_caption\")]" when !valve; custom_components/heatpump_optimizer/mixing_valve.py:73 "is_throttling: (mode or MODE_NONE) in THROTTLING_MODES" |
 | `setup.dhw_combi_caption` | Hot water made in the buffer tank when combi store is active | custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js:4405 'topo.dhw_source === "combi"'; custom_components/heatpump_optimizer/topology.py:684 '"dhw_source": "combi" if p.combi_tank_active else "tank"' |
 | `setup.dhw_coil_caption` | Hot water tank is refilled through a coil in the wood tank when coil is active (option + hot water + two-tank model) | custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js:4362 "coilState = dhwCoil ? active"; custom_components/heatpump_optimizer/thermal_model.py:366 "dhw_wood_coil_enabled and dhw_enabled and two_tank_modelled" |
-| `setup.dhw_coil_preheats` | Coil preheats the mains (cold inlet) water with wood-tank heat | custom_components/heatpump_optimizer/thermal_model.py:2843 "leaves the coil at mains + eps*(T_wood - mains)"; custom_components/heatpump_optimizer/thermal_model.py:2833 def dhw_coil_draw_reduction |
+| `setup.dhw_coil_preheats` | Coil preheats the mains (cold inlet) water with wood-tank heat | custom_components/heatpump_optimizer/thermal_model.py:2867-2868 "t_in = inlet_temp + DHW_WOOD_COIL_EFFECTIVENESS * max(0.0, wood_temp - inlet_temp)"; custom_components/heatpump_optimizer/thermal_model.py:2833 def dhw_coil_draw_reduction |
 | `setup.dhw_coil_off` | Coil option on but model cannot run it | custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js:4364 'topo.dhw_wood_coil_configured ? "off"'; custom_components/heatpump_optimizer/topology.py:705 "dhw_wood_coil_configured": p.dhw_wood_coil_enabled |
 | `setup.dhw_coil_off_why` | Coil not modelled because it needs the two-tank layout | custom_components/heatpump_optimizer/thermal_model.py:366 "dhw_coil_active = enabled and dhw_enabled and two_tank_modelled"; custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js:4405 box only drawn when topo.dhw, so two-tank is the missing condition |
 | `setup.dhw_coil_none` | No hot-water coil configured on the wood tank | custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js:4364 ': "none' when neither dhw_wood_coil nor configured |
@@ -333,7 +333,7 @@ Each row was judged by reading the code that decides it: where the card renders
 | `setup.manual_setpoint_hint` | Manual setpoint is used when no target sensor is assigned; 0 means the comfort-band top (max_temp) | custom_components/heatpump_optimizer/thermal_model.py:2181 "target = p.mixing_valve_target or p.comfort_ceiling"; custom_components/heatpump_optimizer/coordinator.py:6699 "valve_target = reader.read(CONF_MIXING_VALVE_TARGET_ENTITY)"; custom_components/heatpump_optimizer/thermal_model.py:1067 comfort_ceiling = CONF_MAX_TEMP |
 | `setup.setpoint_reloading` | Setpoint saved to config and integration reloads | custom_components/heatpump_optimizer/services.py:869 "options[CONF_MIXING_VALVE_TARGET] = float(setpoint)"; custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js:14139 setpoint_reloading branch |
 | `errors.not_connected` | shown when hass or hass.callService is missing | custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js:13249 "typeof this.host.hass.callService !== \"function\"" |
-| `errors.day_start_equals_end` | equal day start/end hour leaves no daytime comfort period | custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js:13278 "draft.dayStart === draft.dayEnd"; comfort_band.py:198 "if start >= end" (day value only for start <= hour < end, night temp round the clock) |
+| `errors.day_start_equals_end` | equal day start/end hour leaves no daytime comfort period | custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js:13278 "draft.dayStart === draft.dayEnd"; comfort_band.py:200 "if start >= end" (day value only for start <= hour < end, night temp round the clock) |
 | `errors.no_answer` | simulate returned no result | custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js:13415-13416 "? L(\"errors.could_not_simulate\", { err: first.error }) : L(\"errors.no_answer\")" |
 | `errors.no_plan_data` | no plan data yet (neither plan has data) | custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js:15571 "} else if (!anyData) { body = this.plan.noPlanHtml()" |
 | `errors.diag_not_found` | entity id not in hass.states; configure {kind}_entity in card config | custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js:6989-6991 "const st = this.stateOf(id); if (!st) return L(\"errors.diag_not_found\"..."; custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js:15086,15089 space_entity/dhw_entity validated config keys |
@@ -366,32 +366,32 @@ Each row was judged by reading the code that decides it: where the card renders
 | `score.driver_dear_hours` | driver: energy bought above the day's mean price | custom_components/heatpump_optimizer/driving_grade.py:81 "dear_hours: mean_spot * (kwh - kwh_lo) - (sek - sek_lo)" |
 | `score.driver_earlier_days` | driver: days scored before drivers were kept | custom_components/heatpump_optimizer/driving_grade.py:114 "points[\"earlier_days\"] = grade - REFERENCE - sum(points.values())" |
 | `score.driver_typical_machine` | machine shown when no driver moves it: matches own COP history | custom_components/heatpump_optimizer/coordinator.py:3315 "SCORE_REFERENCE ... machine: 100.0"; www/heatpump-optimizer-card.js:9741 |
-| `score.driver_typical_operation` | operation with no driver: bought at the day's flat mean price | custom_components/heatpump_optimizer/coordinator.py:3315 "operation: driving_grade.REFERENCE"; driving_grade.py:28 "REFERENCE = 0.0" |
+| `score.driver_typical_operation` | operation with no driver: bought at the day's flat mean price | custom_components/heatpump_optimizer/coordinator.py:3315 "operation: driving_grade.REFERENCE"; driving_grade.py:31 "REFERENCE = 0.0" |
 | `score.evidence_bands` | samples per outdoor band, {required} needed | custom_components/heatpump_optimizer/coordinator.py:3352 "\"required\": COP_BASELINE_MIN_SAMPLES"; www/heatpump-optimizer-card.js:9755 "ev.bands.slice(0, 4)" |
 | `score.evidence_band` | {lo} to {hi} degC: {n} samples | custom_components/heatpump_optimizer/coordinator.py:3347 "outdoor_c: 3 * band ... samples: int(entry[1])"; www/heatpump-optimizer-card.js:9757-9758 "hi: Number(b.outdoor_c) + 3" |
 | `score.evidence_band_dhw` | {lo} to {hi} degC hot water: {n} samples | custom_components/heatpump_optimizer/coordinator.py:3347 "hot_water: curve is True"; www/heatpump-optimizer-card.js:9757 "b.hot_water ? score.evidence_band_dhw" |
-| `score.evidence_empty` | no COP samples yet (no baseline bucket) | custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js:9762 "L(\"score.evidence_empty\")" when bands empty; coordinator.py:3345 bands from _cop_baseline |
+| `score.evidence_empty` | no COP samples yet (no baseline bucket) | custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js:9762 "L(\"score.evidence_empty\")" when bands empty; coordinator.py:3346-3350 bands from baseline.items(), called with self._cop_baseline at coordinator.py:10621 |
 | `score.evidence_frozen` | {n} intervals refused while learning was frozen | custom_components/heatpump_optimizer/coordinator.py:5334 "self._measured_cop.frozen_refusals += 1"; accuracy.py:877 |
 | `fold.narrative_total` | summed kWh and cost of the narrative rows | custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js:9889-9904 "items.reduce(... kwh: t.kwh + Number(it.kwh) ... sek ..." and L("fold.narrative_total") |
 | `fold.hint` | click toggles the fold | custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js:9853 button data-fold with title L("fold.hint") |
 | `whynow.metric` | per-reason arrow=run/idle direction, % = share of total push this step, high share=hardest push, plan weighs whole day; no data = no plan for the hour (before first solve or price forecast missing) | custom_components/heatpump_optimizer/slot_drivers.py:121-122 "weights = np.divide(100.0 * push, total..." (magnitudes sum to 100); slot_drivers.py:151-166 why_now_at returns None if no drivers or "not np.isfinite(result.prices[i])" / price_known false; custom_components/heatpump_optimizer/sensor.py:1639 "if why_now else attrs" |
-| `whynow.all_neutral` | shown when no driver has any effect | custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js:9828 "drivers.every((d) => d.direction === \"neutral\")"; custom_components/heatpump_optimizer/slot_drivers.py:131 "abs(weight) < NEUTRAL_BELOW_PCT" (0.5) |
-| `whynow.dir_run` | driver direction is run/idle | custom_components/heatpump_optimizer/slot_drivers.py:131-134 "return \"run\" if weight > 0 else \"idle\"" |
-| `whynow.dir_idle` | driver direction is run/idle | custom_components/heatpump_optimizer/slot_drivers.py:131-134 "return \"run\" if weight > 0 else \"idle\"" |
-| `whynow.dir_neutral` | driver has no effect now (\|weight\|<0.5%) | custom_components/heatpump_optimizer/slot_drivers.py:131-132 "if abs(weight) < NEUTRAL_BELOW_PCT: return \"neutral\"" |
+| `whynow.all_neutral` | shown when no driver has any effect | custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js:9828 "drivers.every((d) => d.direction === \"neutral\")"; custom_components/heatpump_optimizer/slot_drivers.py:134 "abs(weight) < NEUTRAL_BELOW_PCT" (0.5) |
+| `whynow.dir_run` | driver direction is run/idle | custom_components/heatpump_optimizer/slot_drivers.py:134-134 "return \"run\" if weight > 0 else \"idle\"" |
+| `whynow.dir_idle` | driver direction is run/idle | custom_components/heatpump_optimizer/slot_drivers.py:134-134 "return \"run\" if weight > 0 else \"idle\"" |
+| `whynow.dir_neutral` | driver has no effect now (\|weight\|<0.5%) | custom_components/heatpump_optimizer/slot_drivers.py:134 "if abs(weight) < NEUTRAL_BELOW_PCT: return \"neutral\"" |
 | `whynow.explain_price_rank` | price rank across plan: cheapest slot fully run, dearest idle | custom_components/heatpump_optimizer/slot_drivers.py:69-80 "rank = (less + 0.5*(equal-1))/(n-1); return 1.0 - 2.0 * rank" |
 | `whynow.explain_comfort_floor` | room distance from middle of comfort band: below middle=run, above=idle | custom_components/heatpump_optimizer/slot_drivers.py:118 "np.clip((floor + half - room) / half, -1.0, 1.0)" with half=(ceiling-floor)/2 (slot_drivers.py:111) |
 | `whynow.explain_mold_guard` | how far mold guard lifts lowest allowed temp above comfort minimum; only pushes toward running | custom_components/heatpump_optimizer/slot_drivers.py:119 "np.clip((mold - floor) / half, 0.0, 1.0)" |
 | `whynow.explain_away` | how far away mode/holiday schedule lowers lowest allowed temp; only pushes toward idle | custom_components/heatpump_optimizer/slot_drivers.py:120 "-np.clip(drops / half, 0.0, 1.0)"; slot_drivers.py:46-66 away_floor_drops (away setback + holiday profile) |
-| `whynow.explain_forecast` | slot weather vs next 8 h: colder/windier/wetter ahead=run, more sun ahead=idle | custom_components/heatpump_optimizer/slot_drivers.py:91-95 "(out[i]-out[i:end].mean())/10 + (hlf[i:end].mean()-hlf[i]) - (sun...)"; FORECAST_LOOKAHEAD_H = 8.0 (slot_drivers.py:32); hlf = wind/precip loss factor optimizer.py:566-582 |
+| `whynow.explain_forecast` | slot weather vs next 8 h: colder/windier/wetter ahead=run, more sun ahead=idle | custom_components/heatpump_optimizer/slot_drivers.py:91-95 "(out[i]-out[i:end].mean())/10 + (hlf[i:end].mean()-hlf[i]) - (sun...)"; FORECAST_LOOKAHEAD_H = 8.0 (slot_drivers.py:30); hlf = wind/precip loss factor optimizer.py:566-582 |
 | `tiles.planned_title` | electricity the plan uses for heating over its horizon (space+DHW) | custom_components/heatpump_optimizer/coordinator.py:4941 "total_energy_kwh": round(sum(raw_space) * dt_hours, 2); 4960 same for dhw; card 9572 planTotal sums both |
 | `tiles.cost_title` | electricity cost of the plan over its horizon | custom_components/heatpump_optimizer/coordinator.py:4942-4944 "sum(p * pr for p, pr in zip(raw_space, raw_prices)) * dt_hours"; card planTotal(plan, "total_cost") |
 | `status.heating` | a plan step is heating now | custom_components/heatpump_optimizer/coordinator.py:4945 "active_now: bool(raw_space and channel_heating_steps(raw_space[:1], raw_dhw[:1])[0])"; www/heatpump-optimizer-card.js:9680 |
-| `status.stale_title` | no new plan for more than {minutes} min; in auto and economy the pump runs on its own curve until a solve succeeds | custom_components/heatpump_optimizer/coordinator.py:7802 "if self._mode in (MODE_AUTO, MODE_ECONOMY) and self._plan_is_stale(): ... return"; coordinator.py:800 "max(PLAN_STALE_INTERVALS * interval, PLAN_STALE_FLOOR_MINUTES)"; www/heatpump-optimizer-card.js:9647 |
+| `status.stale_title` | no new plan for more than {minutes} min; in auto and economy the pump runs on its own curve until a solve succeeds | custom_components/heatpump_optimizer/coordinator.py:7802 "if self._mode in (MODE_AUTO, MODE_ECONOMY) and self._plan_is_stale(): ... return"; coordinator.py:808 "max(PLAN_STALE_INTERVALS * interval, PLAN_STALE_FLOOR_MINUTES)"; www/heatpump-optimizer-card.js:9647 |
 | `status.fallback_title` | no plan yet so the pump runs on its own curve | custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js:9670 "plans.every(st => st.state === \"no plan\")"; sensor.py:1460 "if not plan: return \"no plan\""; coordinator.py:7800 "if not self._current_action ... return" |
 | `status.manual` | manual plan until {time} | custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js:9660-9664 "manual.expires_at"; coordinator.py:8556 "expires_at": override.expires_at.isoformat() |
 | `slots.slot_aria` | Enter opens actions, Delete removes | custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js:12485-12487 "key === Enter ... wantsRemove = key === Delete \|\| Backspace" |
-| `slots.lane_aria` | Enter adds a slot (opens add menu) | custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js:12485-12471 Enter opens openMenu(channel,...) on a lane |
+| `slots.lane_aria` | Enter adds a slot (opens add menu) | custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js:12481-12485,12548 Enter opens openMenu(channel,...) on a lane |
 | `editor.hours` | hours of plan shown | www/heatpump-optimizer-card.js:16091 "defaultWindow(spFc, rawDhw, cfg.hours, Date.now())"; 15100 validation |
 | `editor.what_if` | toggles showing the schedule editor | www/heatpump-optimizer-card.js:11396 "return !!this.host.config.what_if"; 12638 "if (!this.host.config.what_if) return \"\"" |
 | `editor.show_stats` | toggles the headline stat tiles | www/heatpump-optimizer-card.js:9586 "if (!cfg.show_stats) return \"\"" |
@@ -404,3 +404,38 @@ Each row was judged by reading the code that decides it: where the card renders
 ### No behaviour claimed
 
 `header.default_title`, `header.enlarge`, `header.enlarge_chart`, `header.tab_plan`, `header.tab_setup`, `header.tab_savings`, `header.tab_advisor`, `header.tab_health`, `health.inputs`, `health.plan`, `health.learning`, `health.checklist`, `health.input_away_presence_entity`, `health.input_buffer_tank_temp_entity`, `health.input_compressor_freq_entity`, `health.input_dhw_disinfection_switch_entity`, `health.input_dhw_inlet_entity`, `health.input_dhw_setpoint_entity`, `health.input_dhw_temp_entity`, `health.input_external_heat_entity`, `health.input_floor_return_temp_entity`, `health.input_flow_meter_entity`, `health.input_grid_fee_entity`, `health.input_heat_pump_backup_heater_entity`, `health.input_heat_pump_capacity_limited_entity`, `health.input_heat_pump_defrost_entity`, `health.input_heat_pump_dhw_booster_entity`, `health.input_heat_pump_energy_entity`, `health.input_heat_pump_fault_entity`, `health.input_heat_pump_heat_energy_entity`, `health.input_heat_pump_mode_entity`, `health.input_heat_pump_online_entity`, `health.input_heat_pump_power_entity`, `health.input_heat_pump_return_temp_entity`, `health.input_heat_pump_supply_temp_entity`, `health.input_heat_pump_switch_entity`, `health.input_heat_pump_thermal_power_entity`, `health.input_holiday_calendar_entity`, `health.input_house_power_entity`, `health.input_indoor_humidity_entity`, `health.input_indoor_temp_entity`, `health.input_lower_floor_temp_entity`, `health.input_mixing_valve_target_entity`, `health.input_mixing_valve_write_entity`, `health.input_heat_curve_displace_entity`, `health.input_outdoor_temp_entity`, `health.input_price_entity`, `health.input_pv_export_price_entity`, `health.input_pv_production_entity`, `health.input_solar_radiation_entity`, `health.input_space_circulation_pump_entity`, `health.input_space_setpoint_entity`, `health.input_space_setpoint_high_limit_entity`, `health.input_space_setpoint_low_limit_entity`, `health.input_valve_outlet_temp_entity`, `health.input_vvc_pump_entity`, `health.input_weather_entity`, `health.input_wood_tank_bottom_entity`, `health.input_wood_tank_top_entity`, `health.learn_savings`, `health.learn_cop`, `health.learn_accuracy`, `health.learn_score`, `health.model`, `health.model_heat_loss`, `health.model_solar`, `health.model_lower`, `health.model_tank`, `health.model_cop`, `health.model_gains`, `health.model_house`, `health.model_lower_floor`, `health.support_title`, `health.check_indoor`, `health.act_assign`, `health.act_show`, `health.input_other`, `health.debug_title`, `health.act_debug_start`, `advisor.heading`, `advisor.estimated`, `advisor.inbox_heading`, `advisor.gap_title`, `advisor.act_assign`, `advisor.act_apply`, `advisor.act_settings`, `advisor.optin_degree`, `advisor.apply_failed`, `advisor.act_adopt`, `advisor.act_restore`, `advisor.optin_wood`, `advisor.optin_fuse`, `advisor.optin_frequency`, `advisor.feedback_power`, `advisor.feedback_energy`, `advisor.feedback_frequency`, `advisor.feedback_flow`, `advisor.act_dismiss`, `savings.col_month`, `savings.col_baseline`, `savings.col_actual`, `savings.col_savings`, `savings.col_pct`, `receipt.col_line`, `receipt.col_basis`, `receipt.col_cost`, `receipt.line_spot`, `receipt.line_grid_fee`, `receipt.line_capacity`, `receipt.line_immersion`, `receipt.line_dhw_booster`, `receipt.line_backup_heater`, `receipt.line_wear`, `receipt.total`, `replay.measured`, `replay.indoor`, `replay.cost`, `header.close`, `series.price`, `series.dhw_slots`, `series.space_slots`, `series.actioned`, `series.quiet_silent`, `series.quiet_off`, `tooltip.actioned`, `series.outdoor`, `series.dhw_temp`, `series.house_temp`, `series.solar`, `away.toggle`, `away.return`, `setup.tanks`, `setup.tank_dhw`, `setup.tank_wood`, `series.upper_floor`, `series.lower_floor`, `series.dhw_band`, `plan.now`, `plan.now_temp`, `plan.zoom_out`, `plan.zoom_in`, `plan.show_whole_plan`, `plan.history_loading`, `slots.lane_dhw`, `slots.lane_space`, `slots.lane_wood`, `slots.applying`, `slots.until_suffix`, `slots.clearing`, `whatif.todays_slots`, `whatif.show_whole_plan_button`, `whatif.apply_plan`, `whatif.undo_changes`, `whatif.back_to_auto`, `whatif.usual_schedule`, `whatif.heating_hours`, `whatif.day_from`, `whatif.day_start_aria`, `whatif.day_to`, `whatif.day_end_aria`, `whatif.dhw_windows`, `whatif.window_start_aria`, `whatif.window_end_aria`, `whatif.remove`, `whatif.remove_window_aria`, `whatif.window_days_aria`, `whatif.days_daily`, `whatif.days_weekdays`, `whatif.days_weekend`, `whatif.days_monday`, `whatif.days_tuesday`, `whatif.days_wednesday`, `whatif.days_thursday`, `whatif.days_friday`, `whatif.days_saturday`, `whatif.days_sunday`, `whatif.add_window`, `whatif.quiet_windows`, `whatif.quiet_action_silent`, `whatif.quiet_action_off`, `whatif.quiet_action_aria`, `whatif.add_quiet`, `whatif.no_quiet_hint`, `whatif.wood`, `whatif.wood_liters`, `whatif.add_wood_slot`, `whatif.simulate`, `whatif.save_schedule`, `whatif.reset`, `whatif.temperatures`, `whatif.comfort_temp`, `whatif.dhw_min`, `whatif.dhw_min_aria`, `whatif.confirm_overwrite`, `whatif.saving`, `whatif.simulating`, `setup.done_editing`, `setup.edit_layout`, `setup.save_layout`, `setup.undo_layout`, `setup.tidy_layout`, `setup.svg_aria`, `places.heat_pump`, `places.buffer_tank`, `places.mixing_valve`, `places.upper_zone`, `places.lower_zone`, `places.wood_tank`, `places.wood_valve`, `places.dhw_tank`, `places.slab_shunt`, `setup.box_hp_tank`, `setup.box_buffer_tank`, `setup.box_4way_valve`, `setup.box_mixing_valve`, `setup.box_outside`, `setup.box_heat_pump`, `setup.box_dhw_tank`, `setup.box_upper_floor`, `setup.box_house`, `setup.box_lower_floor`, `setup.not_configured`, `setup.click_to_assign_title`, `setup.fold_show`, `setup.fold_hide`, `setup.configure`, `setup.configure_page`, `setup.type_outside`, `setup.type_heat_source`, `setup.type_valve`, `setup.type_store`, `setup.type_hot_water`, `setup.type_coil`, `setup.type_coil_off`, `setup.type_radiator`, `setup.type_slab`, `setup.picker_aria`, `setup.picker_none`, `setup.assign`, `setup.cancel`, `setup.picker_filter_placeholder`, `setup.picker_filter_aria`, `setup.confirm_clear`, `errors.could_not_apply`, `errors.could_not_clear`, `errors.could_not_save`, `errors.could_not_simulate`, `errors.could_not_save_layout`, `errors.could_not_assign`, `errors.diag_space`, `errors.diag_dhw`, `errors.cfg_not_object`, `errors.cfg_space_entity`, `errors.cfg_dhw_entity`, `errors.cfg_solar_entity`, `errors.cfg_what_if`, `errors.cfg_title`, `errors.cfg_series`, `errors.cfg_series_unknown`, `errors.cfg_series_visibility`, `errors.cfg_show_stats`, `headline.savings`, `headline.score`, `score.label_envelope`, `score.label_machine`, `score.label_operation`, `headline.savings_pct`, `fold.narrative_title`, `whynow.title`, `whynow.no_data`, `whynow.weight`, `whynow.driver_price_rank`, `whynow.driver_comfort_floor`, `whynow.driver_mold_guard`, `whynow.driver_away`, `whynow.driver_forecast`, `tiles.price_now`, `tiles.planned`, `tiles.cost`, `tiles.indoor`, `status.idle`, `status.stale`, `status.fallback`, `status.manual_open`, `editor.title`, `editor.space_entity`, `editor.dhw_entity`, `editor.solar_entity`, `editor.currency`.
+
+## Comment and docstring evidence, swept
+
+The owner's ruling binds the evidence as well as the text: a row whose claim rests on a comment or a docstring is not verified. The sweep is a rule, not a sample: `python3 -I dev/audit/harnesses/r10_card_evidence_kinds.py dev/audit/rounds/round10/user-text-card.md` reads every row of the tables above, resolves each `file:line` it cites at the merge base, and classifies the cited lines as code, comment (`#`, `//`, `*`), docstring (a string expression, by `ast`) or blank; it prints each row with any citation that is not code. Its null control is the record at f11bdd4d4, the head the review blocked: it printed `advisor.refit_detail` (the coordinator.py:1363 docstring) and `slots.lane_aria`'s reversed range. A row naming a comment in prose ("comment states") without citing its line is not printed, so `grep -niE 'comment|docstring'` over the record was read as well: it returns `health.model_share`, `score.part_overall`, `health.cop_reason_unaligned_meters` and `advisor.refit_detail`.
+
+Every row returned, with its disposition. "Line drift" means the quoted text is code at a line a few off the cited one; the row is re-anchored and its verdict stands.
+
+| row | non-code citation at the base | disposition |
+|---|---|---|
+| `advisor.refit_detail` | accuracy.py:651 "(comment states 7-10 %)"; :655-662 docstring; coordinator.py:1363 docstring | the 7 % was comment-only: **false**, corrected (Corrected table) and pinned; the other clauses re-judged on accuracy.py:659-663, services.py:1220-1227 |
+| `advisor.optin_heading` | card.js:10028-10032 comment "never read" | re-judged on code: the degree row leaves the list once `price_tiles_enabled` is on (coordinator.py:10723, card.js `optIn`), but wood, fuse and frequency are sensors created disabled by default (sensor.py:2130, 2809, 3011 `_attr_entity_registry_enabled_default = False`) that no options page turns on and the card never reads. The rows named only the options page, so they now also say to turn the sensor on: `advisor.optin_sensor_off`, en, sv, de, pinned |
+| `savings.wood_note` | ledger.py:479-481 docstring | re-judged on code: the savings lines booked are kWh (ledger.py:375-381), priced at spot plus fee; `git grep -niE 'firewood\|wood_(cost\|sek\|price)' 90c6bc3b0 -- custom_components/heatpump_optimizer/ledger.py` returns the docstring alone, so no firewood cost is booked. True |
+| `setup.dhw_coil_preheats` | thermal_model.py:2843 docstring | re-judged on code: thermal_model.py:2867-2868 `t_in = inlet_temp + DHW_WOOD_COIL_EFFECTIVENESS * max(0.0, wood_temp - inlet_temp)`. True |
+| `receipt.saved` | ledger.py:62 comment | re-judged on code: the reference is the thermostat loop of optimizer.py:5953-5981 (`_compute_baseline_power`, `self.model.simulate_step`), booked as `savings_baseline` at ledger.py:375. True |
+| `score.evidence_empty` | coordinator.py:3345 docstring | re-anchored: coordinator.py:3346-3350 builds `bands` from `baseline.items()`, called with `self._cop_baseline` at coordinator.py:10621. True |
+| `status.stale_title` | coordinator.py:800 docstring | re-anchored: coordinator.py:808 `return max(PLAN_STALE_INTERVALS * interval, PLAN_STALE_FLOOR_MINUTES)`. True |
+| `health.cop_measured` | accuracy.py:861 docstring | re-anchored: accuracy.py:925 `self.at = at`, recorded at coordinator.py:5424 with `dt_util.now()`. True |
+| `advisor.value_month` | price_tiles.py:97 docstring | re-anchored: price_tiles.py:91 `return delta * MONTH_HOURS / horizon_hours`, used at :105. True |
+| `advisor.refit_wait_detail` | accuracy.py:704 docstring | line drift: accuracy.py:707 `days < REFIT_SETTLED_DAYS`. True |
+| `health.model_share` | coordinator.py:5906 docstring | the docstring citation is dropped; coordinator.py:5950 and thermal_model.py:604 carry the row. Corrected as before |
+| `health.learn_savings_why` | ledger.py:~486 docstring; sensor.py:~525 blank | line drift: ledger.py:495, :506; sensor.py:528. Corrected as before |
+| `health.cop_reason_unaligned_meters` | heat_energy.py:554-556 docstring | heat_energy.py:567 is code and decides the row (the review's own reading). True |
+| `slots.pinned_result` | manual_plan.py:20-22 docstring | optimizer.py:4161-4175 is code and decides the row; the docstring citation adds nothing. True |
+| `health.p_implausible` | inputs.py:1011 comment | line drift: inputs.py:1010 `if not plausible_c(key, value):`, :1014 `_set_problem(reading, "implausible")`. True |
+| `health.debug_off` | diagnostics.py:408 comment | line drift: diagnostics.py:413-414 `debugger.capped(await collector.async_bundle(...))`. True |
+| `advisor.empty` | card.js:10931 comment | line drift: card.js:10930 `if (!rows.length) {`. True |
+| `whatif.schedule_hint` | card.js:13351 comment | line drift: the `apply_schedule` call in `onSaveSchedule`, its payload `day_start_hour`, `day_end_hour`, `dhw_windows`. True |
+| `errors.day_start_equals_end` | comfort_band.py:198 comment | line drift: comfort_band.py:200 `if start >= end:`. True |
+| `score.driver_typical_operation` | driving_grade.py:28 comment | line drift: driving_grade.py:31 `REFERENCE = 0.0`; the flat mean is driving_grade.py:91 `1.0 - paid_mean / mean_spot`. True |
+| `whynow.explain_forecast` | slot_drivers.py:32 comment | line drift: slot_drivers.py:30 `FORECAST_LOOKAHEAD_H = 8.0`. True |
+| `plan.space_blocked`, `reasons.pump_mode`, `reasons.pump_mode_space` | pump_signals.py:341 blank | line drift: pump_signals.py:340 `return self.mode_observed and not self.mode_owned and not self.mode.space_heat` |
+| `whynow.all_neutral`, `whynow.dir_neutral` | slot_drivers.py:131-132 blank | line drift: slot_drivers.py:134 `if abs(weight) < NEUTRAL_BELOW_PCT:`. True |
+| `whatif.idle_status`, `whatif.confirm_hint` | services.py:1001 blank | line drift: services.py:944 `handle_apply_schedule`, :1089 `async_update_entry`. True |
+| `slots.lane_aria` | card.js:12485-12471, a reversed range | card.js:12481-12485 `wantsMenu` on Enter, :12548 `this.openMenu(...)`. True |
+| `score.part_overall` | names a docstring in prose | coordinator.py:3381/3392 is code and decides the row (the review's reading). Corrected as before |
diff --git a/dev/programme/delivery/3499.md b/dev/programme/delivery/3499.md
index ab08e8486e..e6f9d2f65f 100644
--- a/dev/programme/delivery/3499.md
+++ b/dev/programme/delivery/3499.md
@@ -1 +1 @@
-- [#3499](https://github.com/tvofi/heatpump_optimizer/pull/3499) — **open**, R10-GATE-DEFER-BARRIER: r10 gate defer barrier (R10-GATE-DEFER-BARRIER)
+- [#3499](https://github.com/tvofi/heatpump_optimizer/pull/3499) — **merged `6142f48`**, R10-GATE-DEFER-BARRIER: r10 gate defer barrier (R10-GATE-DEFER-BARRIER).
diff --git a/dev/programme/delivery/3511.md b/dev/programme/delivery/3511.md
index c847f05d89..071ec1a8dc 100644
--- a/dev/programme/delivery/3511.md
+++ b/dev/programme/delivery/3511.md
@@ -1 +1 @@
-- [#3511](https://github.com/tvofi/heatpump_optimizer/pull/3511) — **open**, R10-SAV-VALUATION-RESIDUE: r10 sav valuation residue
+- [#3511](https://github.com/tvofi/heatpump_optimizer/pull/3511) — **merged `90c6bc3`**, R10-SAV-VALUATION-RESIDUE: r10 sav valuation residue.
diff --git a/dev/programme/delivery/3520.md b/dev/programme/delivery/3520.md
index 99ff6e09e8..622ef34ae4 100644
--- a/dev/programme/delivery/3520.md
+++ b/dev/programme/delivery/3520.md
@@ -1 +1 @@
-- [#3520](https://github.com/tvofi/heatpump_optimizer/pull/3520) — **open**, R10-HOTFIX-TICK-SELFTEST-CHECKOUT: r10 hotfix tick selftest checkout (R10-HOTFIX-TICK-SELFTEST-CHECKOUT)
+- [#3520](https://github.com/tvofi/heatpump_optimizer/pull/3520) — **merged `ad95665`**, R10-HOTFIX-TICK-SELFTEST-CHECKOUT: r10 hotfix tick selftest checkout.
diff --git a/dev/programme/delivery/3526.md b/dev/programme/delivery/3526.md
index 9b2ad1f42f..34a6cfc62c 100644
--- a/dev/programme/delivery/3526.md
+++ b/dev/programme/delivery/3526.md
@@ -1 +1 @@
-- [#3526](https://github.com/tvofi/heatpump_optimizer/pull/3526) — **open**, R10-DUTY-SWITCH-PLANNER-PRICE: r10 duty switch planner price (R10-DUTY-SWITCH-PLANNER-PRICE)
+- [#3526](https://github.com/tvofi/heatpump_optimizer/pull/3526) — **merged `c67c193`**, R10-DUTY-SWITCH-PLANNER-PRICE: r10 duty switch planner price (R10-DUTY-SWITCH-PLANNER-PRICE).
diff --git a/dev/programme/delivery/3539.md b/dev/programme/delivery/3539.md
index 80a5e06e48..310486959d 100644
--- a/dev/programme/delivery/3539.md
+++ b/dev/programme/delivery/3539.md
@@ -1 +1 @@
-- [#3539](https://github.com/tvofi/heatpump_optimizer/pull/3539) — **open**, R10-REVIEW-DISPATCH-RESIDUE (part 6): r10 review dispatch residue p6 (R10-REVIEW-DISPATCH-RESIDUE)
+- [#3539](https://github.com/tvofi/heatpump_optimizer/pull/3539) — **merged `1906e79`**, R10-REVIEW-DISPATCH-RESIDUE (part 6): r10 review dispatch residue p6.
diff --git a/dev/programme/delivery/3546.md b/dev/programme/delivery/3546.md
new file mode 100644
index 0000000000..375ea41b10
--- /dev/null
+++ b/dev/programme/delivery/3546.md
@@ -0,0 +1 @@
+- [#3546](https://github.com/tvofi/heatpump_optimizer/pull/3546) — **open**, R10-HOTFIX-UPDATEPR-FIGURE-REFRESH: r10 hotfix updatepr figure refresh (R10-HOTFIX-UPDATEPR-FIGURE-REFRESH)
diff --git a/dev/programme/delivery/3549.md b/dev/programme/delivery/3549.md
index b2769f696d..7ceb24fe6f 100644
--- a/dev/programme/delivery/3549.md
+++ b/dev/programme/delivery/3549.md
@@ -1 +1 @@
-- [#3549](https://github.com/tvofi/heatpump_optimizer/pull/3549) — **open**, R10-HOTFIX-OPENER-REFUSALS: open_pr.sh shares one body file across two runs, and ci_predict reads a stale roster ref (R10-HOTFIX-OPENER-REFUSALS)
+- [#3549](https://github.com/tvofi/heatpump_optimizer/pull/3549) — **merged `cfa8683`**, R10-HOTFIX-OPENER-REFUSALS: open_pr.sh shares one body file across two runs, and ci_predict reads a stale roster ref (R10-HOTFIX-OPENER-REFUSALS).
diff --git a/dev/programme/delivery/3554.md b/dev/programme/delivery/3554.md
index 8c6d8f8d39..2d2eff2c46 100644
--- a/dev/programme/delivery/3554.md
+++ b/dev/programme/delivery/3554.md
@@ -1 +1 @@
-- [#3554](https://github.com/tvofi/heatpump_optimizer/pull/3554) — **open**, roster: land the round-10 roster from handoff/audit-r10-roster ce60e992 (v7.1.15) (R10-ROSTER-BATCH24)
+- [#3554](https://github.com/tvofi/heatpump_optimizer/pull/3554) — **merged `e28a310`**, roster: land the round-10 roster from handoff/audit-r10-roster ce60e992 (v7.1.15).
diff --git a/dev/programme/delivery/3555.md b/dev/programme/delivery/3555.md
index 04eb95d993..4d785d436a 100644
--- a/dev/programme/delivery/3555.md
+++ b/dev/programme/delivery/3555.md
@@ -1 +1 @@
-- [#3555](https://github.com/tvofi/heatpump_optimizer/pull/3555) — **open**, roster: land the round-10 roster from handoff/audit-r10-roster b1697d36 (carry-201 entry 6 remeasure) (R10-ROSTER-BATCH24)
+- [#3555](https://github.com/tvofi/heatpump_optimizer/pull/3555) — **merged `154dbb4`**, roster: land the round-10 roster from handoff/audit-r10-roster b1697d36 (carry-201 entry 6 remeasure).
diff --git a/dev/programme/delivery/3558.md b/dev/programme/delivery/3558.md
new file mode 100644
index 0000000000..ba59b6fa03
--- /dev/null
+++ b/dev/programme/delivery/3558.md
@@ -0,0 +1 @@
+- [#3558](https://github.com/tvofi/heatpump_optimizer/pull/3558) — **open**, R10-HOTFIX-TICK-BASH32: r10 hotfix tick bash32 (R10-HOTFIX-TICK-BASH32)
diff --git a/dev/programme/delivery/3559.md b/dev/programme/delivery/3559.md
new file mode 100644
index 0000000000..c2150aeb02
--- /dev/null
+++ b/dev/programme/delivery/3559.md
@@ -0,0 +1 @@
+- [#3559](https://github.com/tvofi/heatpump_optimizer/pull/3559) — **open**, record: delivery rows (autofix)
diff --git a/dev/programme/delivery/3563.md b/dev/programme/delivery/3563.md
new file mode 100644
index 0000000000..097d6ed7b5
--- /dev/null
+++ b/dev/programme/delivery/3563.md
@@ -0,0 +1 @@
+- [#3563](https://github.com/tvofi/heatpump_optimizer/pull/3563) — **open**, R10-USER-TEXT-VERIFY-CARD: r10 user text verify card (R10-USER-TEXT-VERIFY-CARD)
diff --git a/tests/card.mjs b/tests/card.mjs
index 0b47f9230b..11848f48b3 100644
--- a/tests/card.mjs
+++ b/tests/card.mjs
@@ -4298,7 +4298,7 @@ const restartStates = (patch = {}) => {
   const rsPage = rs.html().slice(rs.html().indexOf('advisor-page"'));
   check("a drift alarm offers the refit with its band, and the restore point",
     /Restart the heat-loss model at 1\.14 \(now 0\.67\)/.test(rsPage)
-    && /3\.3 settled days \(180 intervals\)/.test(rsPage) && /±7-10 %/.test(rsPage)
+    && /3\.3 settled days \(180 intervals\)/.test(rsPage) && /±10 %/.test(rsPage)
     && /Nothing changes until you accept/.test(rsPage)
     && /Restore the model from 2026-03-01/.test(rsPage)
     && /data-act="adopt_refit"/.test(rsPage) && /data-act="restore_snapshot"/.test(rsPage));
@@ -4342,7 +4342,7 @@ const restartStates = (patch = {}) => {
   const rsv = mkInbox(restartStates(), "sv-SE").html();
   check("the restart rows speak Swedish",
     /Starta om värmeförlustmodellen på 1\.14 \(nu 0\.67\)/.test(rsv)
-    && /Godta omanpassning/.test(rsv) && /±7-10 %/.test(rsv) && /Återställ modellen från/.test(rsv));
+    && /Godta omanpassning/.test(rsv) && /±10 %/.test(rsv) && /Återställ modellen från/.test(rsv));
 }
 
 // --- Scenario: the layout editor (v3.16.0, issue #40) ----------------------
@@ -13804,14 +13804,93 @@ check("without an indoor reading the corner now label is absent",
   check("user text: the COP refusal reasons quote COP_TRACKING_ERROR_GATE and the modelled-COP floor, in every card language",
     Number.isFinite(gate) && modelled !== undefined && copBad.length === 0,
     `gate ${gate}, modelled floor ${modelled}; wrong in: ${copBad.join(",")}`);
-  // 3. The window-time error fires for silent/off windows too (the save and
-  // simulate handlers' `invalid` reads `quietWindows`), so no language may
-  // call the window a hot-water one.
+  // 3. The window-time error fires for silent/off windows too, so no
+  // language may call the window a hot-water one. Both handlers that refuse
+  // an invalid window -- Save (`onSaveSchedule`) and Simulate (`run`) -- are
+  // driven with a valid hot-water window and an invalid quiet one: each must
+  // print the error and call no service. A handler that checked hot-water
+  // windows only would let the quiet one through.
   const hotWord = { en: /hot water/i, sv: /varmvatten/i, de: /warmwasser/i };
-    check("user text: the invalid-window error names no channel, in every card language",
-    langs.every((l) => hotWord[l]) && langs.every((l) => !hotWord[l].test(tbl[l]["errors.invalid_window_time"]))
-    && /quietWindows \|\| \[\]\)\.find\(/.test(cardSrc),
+  check("user text: the invalid-window error names no channel, in every card language",
+    langs.every((l) => hotWord[l]) && langs.every((l) => !hotWord[l].test(tbl[l]["errors.invalid_window_time"])),
     langs.map((l) => `${l}: ${tbl[l]["errors.invalid_window_time"]}`).join(" | "));
+  const quietRefused = [];
+  for (const handler of ["onSaveSchedule", "run"]) {
+    const ed = build(slotStates, { what_if: true });
+    ed.dialog.open();
+    let served = 0;
+    ed._hass = mkHass(ed._hass.states, () => { served++; return {}; });
+    const panel = ed.whatIf;
+    panel.onSlotEdit = () => {}; // keep the draft below, not the DOM's rows
+    const draft = panel.draft();
+    draft.dhwWindows = [{ days: "daily", start: "06:00", end: "08:00" }];
+    draft.quietWindows = [{ days: "daily", start: "notatime", end: "08:00", action: "silent" }];
+    await panel[handler]({ stopPropagation: () => {} });
+    const got = ed.shadowRoot.querySelector(".wi-result").textContent;
+    const want = fn("L")("errors.invalid_window_time", { window: fn("windowRange")(draft.quietWindows[0]) });
+    if (got !== want || served !== 0) quietRefused.push(`${handler}: ${JSON.stringify(got)} vs ${JSON.stringify(want)}, ${served} service call(s)`);
+  }
+  check("user text: Save and Simulate both refuse an invalid quiet window with the channel-neutral error",
+    quietRefused.length === 0, quietRefused.join("; "));
+  // 4. The refit row's uncertainty is the band the refit publishes
+  // (`heat_loss_refit`'s `band_percent`, from accuracy.py's
+  // REFIT_BAND_PERCENT), rendered in every card language. A probe band the
+  // constant does not name proves the row reads the attribute, not a literal.
+  const band = Number((read("accuracy.py").match(/^REFIT_BAND_PERCENT\s*=\s*([0-9.]+)/m) || [])[1]);
+  const bandBad = [];
+  for (const lang of langs) {
+    for (const b of [band, 13]) {
+      const s = restartStates();
+      s[`${ADVISOR_PFX}_model_restart_advisor`].attributes.refit.band_percent = b;
+      const c = new Card();
+      c.setConfig({ type: "custom:heatpump-optimizer-card" });
+      c.hass = { states: s, language: lang, callService: async () => {} };
+      c._onCardClick({});
+      c.dialog.page = "advisor";
+      c._render();
+      const html = collect(c.shadowRoot).join("\n");
+      if (!html.includes(`±${b} %`) || !tbl[lang]["advisor.refit_detail"].includes("±{band} %")) bandBad.push(`${lang} band ${b}`);
+    }
+  }
+  check("user text: the refit row states the band_percent the refit publishes, in every card language",
+    Number.isFinite(band) && bandBad.length === 0, `REFIT_BAND_PERCENT ${band}; wrong: ${bandBad.join(", ")}`);
+  // 5. The opt-in rows: the options page turns the price of a degree on, but
+  // no page turns the wood, fuse or frequency advisor on -- each is a sensor
+  // created disabled (sensor.py's `_attr_entity_registry_enabled_default =
+  // False` in its class) -- so those rows say to enable the sensor, and the
+  // degree row does not. The classes are named here: the card's ids are not
+  // sensor keys.
+  const sensorPy = read("sensor.py");
+  const offByDefault = (cls) => {
+    const at = sensorPy.indexOf(`class ${cls}(`);
+    const next = sensorPy.indexOf("\nclass ", at + 1);
+    return at >= 0 && /_attr_entity_registry_enabled_default = False/.test(sensorPy.slice(at, next < 0 ? undefined : next));
+  };
+  const optClass = { wood: "WoodBurnAdvisorSensor", fuse: "MonthlyPeakSensor", frequency: "FrequencyAdvisorSensor" };
+  const optInIds = fn("ADVISOR_OPT_IN");
+  const optBad = [];
+  for (const id of optInIds) if (!offByDefault(optClass[id])) optBad.push(`${id}: ${optClass[id]} is not disabled by default`);
+  for (const lang of langs) {
+    const c = new Card();
+    c.setConfig({ type: "custom:heatpump-optimizer-card" });
+    // Price tiles off, so the degree row is offered too: the note's control.
+    const st = inboxStates();
+    st[`${ADVISOR_PFX}_optimization_score`].attributes.price_tiles = {};
+    c.hass = { states: st, language: lang, callService: async () => {} };
+    c._onCardClick({});
+    c.dialog.page = "advisor";
+    c._render();
+    const rowsHtml = collect(c.shadowRoot).join("\n").split('class="fact-inbox-row');
+    const note = fn("esc")(tbl[lang]["advisor.optin_sensor_off"]);
+    for (const id of ["degree", ...optInIds]) {
+      const row = rowsHtml.find((r) => r.includes(fn("esc")(tbl[lang][`advisor.optin_${id}`])));
+      if (row === undefined) { optBad.push(`${lang} ${id}: no row`); continue; }
+      if (row.includes(note) !== optInIds.includes(id)) optBad.push(`${lang} ${id}: note ${row.includes(note)}`);
+    }
+  }
+  check("user text: an opt-in advisor whose sensor is off by default says to enable it, in every card language",
+    optInIds.length === 3 && optBad.length === 0, optBad.join("; "));
+  build(mkStates(DEFAULT_SPACE, DEFAULT_DHW, true)); // back to English
 }
 
 console.log(fails ? `\n${fails} CARD CHECK(S) FAILED` : "\nALL CARD CHECKS PASSED");
diff --git a/tests/closures.json b/tests/closures.json
index 88fb6f3ac7..e4ae506c0f 100644
--- a/tests/closures.json
+++ b/tests/closures.json
@@ -4187,6 +4187,7 @@
    "dev/audit/harnesses/r10_briefs_fold_placement.mjs",
    "dev/audit/harnesses/r10_buffer_store.py",
    "dev/audit/harnesses/r10_card_blocker_names.py",
+   "dev/audit/harnesses/r10_card_evidence_kinds.py",
    "dev/audit/harnesses/r10_card_harmony.mjs",
    "dev/audit/harnesses/r10_card_user_text.mjs",
    "dev/audit/harnesses/r10_card_voice_states.mjs",
diff --git a/tools/audit/seat/INSTRUMENTS.md b/tools/audit/seat/INSTRUMENTS.md
index 72b0b6dca2..c89b3c07f0 100644
--- a/tools/audit/seat/INSTRUMENTS.md
+++ b/tools/audit/seat/INSTRUMENTS.md
@@ -126,7 +126,7 @@ standing-seat liveness step keep the seats alive.
 - [`sweep_gantt.py`](instruments/sweep_gantt.py.md) — compares the live state to the plan's Gantt and prints each unacknowledged `GANTT-SLIP`
 - [`verdict_audit.py`](instruments/verdict_audit.py.md) — maps every open PR to its latest verdict and holder; prints `UNHELD` lines
 - [`survivor_list.py`](instruments/survivor_list.py.md) — refuses a `mutation-vacuous` verdict that omits a survivor its evidence's driver output reports; `bus.sh push-verdict` runs it
-- [`bare_array.py`](instruments/bare_array.py.md) — refuses a bare `"${name[@]}"` in any tracked `tools/**/*.sh` script (a sourced library runs under its caller's `set -u`), which macOS bash 3.2 dies on when the array is empty (`--check`, `--self-test`)
+- [`bare_array.py`](instruments/bare_array.py.md) — refuses two macOS bash 3.2 failures in tracked `tools/**/*.sh`: a bare `"${name[@]}"` (empty under a caller's `set -u`) and a `case` pattern lacking its `(` in `$( )` (`--check`, `--self-test`)
 - [`tmp_paths.py`](instruments/tmp_paths.py.md) — refuses a tracked script, workflow or decision record that depends on a temp or machine path (`--check`, `--self-test`)
 - [`update_pr.sh`](instruments/update_pr.sh.md) — brings an open PR branch to its head + a code SHA (merge) + origin/main (merge), adds the PR's own delivery row when the head lacks it (`delivery_row.sh`), prefixes ## Head with what happened, pushes as `hpo-author`
 - [`wt_sync.sh`](instruments/wt_sync.sh.md) — snapshots every worktree whose state is not already on origin (unpushed commits, uncommitted or untracked files) to `origin/wip-sync/<slug>`
diff --git a/tools/audit/seat/bare_array.py b/tools/audit/seat/bare_array.py
index 1d3386a916..676db44d89 100644
--- a/tools/audit/seat/bare_array.py
+++ b/tools/audit/seat/bare_array.py
@@ -1,5 +1,5 @@
 #!/usr/bin/env python3
-"""Refuse a bare `"${name[@]}"` in a tracked tools/ shell script.
+"""Refuse two bash-3.2-only failures in a tracked tools/ shell script.
 
     python3 -I tools/audit/seat/bare_array.py --check [--ref <commit>]
     python3 -I tools/audit/seat/bare_array.py --self-test
@@ -24,6 +24,19 @@ the mutant line by that marker at the line's end (`pr_args.sh`'s header), so a
 reason appended after the marker unanchors the mutant, and any line carrying
 one is refused. `"${name[*]}"`, `${#name[@]}` and `"${name[@]:...}"` are not
 matched.
+
+THE SECOND RULE: a `case` pattern without its leading `(` inside a `$( ... )`
+command substitution, or a `<( ... )`/`>( ... )` process substitution, quoted
+or not. Bash 3.2 finds the end of a substitution by counting parentheses, so
+the pattern's `)` closes it early: unquoted, `bash -n` fails (`tick_loop.sh`,
+PR 3520, the tick loop's own freshness check refusing on every pass); inside
+double quotes `bash -n` passes and the substitution dies at run time. Bash 4+
+parses both. The way out is the pattern's own `(`: `(func) ...;;`. A case in a
+plain `( ... )` subshell, in backquotes, or at top level is not refused, since
+3.2 parses those; there is no opt-out marker, because a refused site never
+parses on 3.2. Comments, quotes and here-document bodies are skipped (an
+unbalanced `)` in a here-document inside a substitution is a 3.2 hazard of its
+own, which this rule does not judge).
 """
 from __future__ import annotations
 
@@ -61,6 +74,88 @@ def sites(text: str) -> list[tuple[int, str]]:
     return [(n, lines[n - 1].strip()) for n in sorted(out)]
 
 
+WORD = re.compile(r"\w+")  # a word; only case, in and esac are read
+HEREDOC = re.compile(r"""<<(-?)[ \t]*(['"]?)\\?([A-Za-z_][A-Za-z0-9_]*)\2""")
+COMMAND = re.compile(r"(?:\A|[\n;&|(){!`]|(?:\A|\W)(?:then|do|else|time))[ \t]*\Z")  # `case` is a keyword here
+BEFORE, AFTER = " \t\n;&|(){`", " \t\n;&|()`"
+EOL = re.compile(r".*")  # to the end of the line, the newline left
+SQUOTE = re.compile(r"'[^']*'?")
+PATTERN = re.compile(r"""(?:\\.|'[^']*'?|"(?:\\.|[^"\\])*"?|[^)'"\\])*\)?""", re.S)  # through its `)`
+
+
+def case_sites(text: str) -> list[tuple[int, str]]:
+    """(line number, line) of each case pattern lacking `(` inside a substitution."""
+    stack: list = []  # "sub", "paren", "dq", "bt", "param", or a case: [case, head|pat|body]
+    hits, docs, i, n = set(), [], 0, len(text)
+    lines = text.splitlines()
+    while i < n:
+        c, t = text[i], stack[-1] if stack else None
+        if isinstance(t, list) and t[1] == "pat":
+            m = WORD.match(text, i)
+            if c in " \t\n":
+                i += 1
+            elif c == "#":
+                i = EOL.match(text, i).end()
+            elif m and m.group() == "esac" and text[m.end():m.end() + 1] in AFTER:
+                stack.pop()  # the keyword is then read again, in the enclosing context
+            else:
+                outer = [e for e in stack if e in ("sub", "bt")]
+                if c != "(" and outer[-1:] == ["sub"]:
+                    hits.add(text.count("\n", 0, i) + 1)
+                t[1], i = "body", PATTERN.match(text, i + (c == "(")).end()
+            continue
+        if t == "dq" and c not in "\\$`":
+            stack.pop() if c == '"' else None
+            i += 1
+            continue
+        word = text[i - 1:i] in BEFORE  # at i == 0 the slice is "", which is in any string
+        m = WORD.match(text, i) if word else None
+        kw = m.group() if m and text[m.end():m.end() + 1] in AFTER else None
+        if c == "\\":
+            i += 1
+        elif c == "}" and t == "param":
+            stack.pop()
+        elif c == "#" and word and t != "param":
+            i = EOL.match(text, i).end() - 1
+        elif c == "'" and t != "dq":
+            i = SQUOTE.match(text, i).end() - 1
+        elif c == '"':
+            stack.append("dq")
+        elif c == "`":
+            stack.pop() if t == "bt" else stack.append("bt")
+        elif text.startswith(("$(", "<(", ">("), i):
+            stack.append("sub")  # `$((` too: its `((` and `))` then pair as a paren
+            i += 1
+        elif text.startswith("${", i):
+            stack.append("param")
+        elif c == "(":
+            stack.append("paren")
+        elif c == ")" and t in ("sub", "paren"):
+            stack.pop()
+        elif HEREDOC.match(text, i) and not text.startswith("<<<", i):
+            h = HEREDOC.match(text, i)
+            docs.append(re.compile("^" + "\t*" * len(h.group(1)) + h.group(3) + "$", re.M))
+        elif c == "\n" and docs:
+            for d in docs:  # each body in turn, to its delimiter line or the end
+                e = d.search(text, i + 1)
+                i = e.end() if e else n
+            docs = []
+            continue
+        elif isinstance(t, list) and t[1] == "body" and text.startswith((";;", ";&"), i):
+            t[1] = "pat"
+            i += 2 if text.startswith(";;&", i) else 1
+        elif m:
+            if kw == "case" and COMMAND.search(text, max(0, i - 9), i):
+                stack.append(["case", "head"])
+            elif kw == "in" and t == ["case", "head"]:
+                t[1] = "pat"
+            elif kw == "esac" and t == ["case", "body"]:
+                stack.pop()
+            i = m.end() - 1
+        i += 1
+    return [(k, lines[k - 1].strip()) for k in sorted(hits)]
+
+
 def scan(ref: str | None = None) -> list[str]:
     """`path:line: text` per refused site across tracked tools/**/*.sh."""
     root = subprocess.check_output(["git", "rev-parse", "--show-toplevel"], text=True).strip()
@@ -76,7 +171,7 @@ def scan(ref: str | None = None) -> list[str]:
             text = subprocess.check_output(["git", "show", f"{ref}:{p}"], text=True, cwd=root)
         else:
             text = (Path(root) / p).read_text()
-        out += [f"{p}:{n}: {t}" for n, t in sites(text)]
+        out += [f"{p}:{n}: {t}" for n, t in sorted(set(sites(text) + case_sites(text)))]
     return out
 
 
@@ -121,6 +216,85 @@ def self_test() -> int:
        "a reason after a mut marker is refused in a judged file on a guarded line")
     st(sites(head + 'f x  # never-empty: argv  # mut:x\n'), [],
        "a judged file's non-bare line with the reason before the marker passes (null)")
+    # The second rule: the line numbers each text refuses. Run against bash 3.2.57, every refused
+    # shape fails, at `bash -n` or (quoted, or in backquotes) at run time.
+    def cs(text, want, name):
+        st([k for k, _ in case_sites(text)], want, name)
+
+    tick = ('out=$(export A=1\n  case $1 in\n    func) . "$t/e"; export -f exec; "$B" --n ;;\n'
+            '    bashenv) BASH_ENV=$t/e "$B" --n ;;\n    none) "$B" --n ;;\n  esac 2>&1); src=$?\n')
+    cs(tick, [3, 4, 5], "planted: tick_loop.sh's shape at PR 3520, three bare patterns in $( )")
+    cs(tick.replace("func)", "(func)").replace("bashenv)", "(bashenv)").replace("none)", "(none)"), [],
+       "the same with each pattern's own ( passes (null)")
+    cs("case a in a) x=$(echo 1);; esac\n", [], "a case at top level passes, its body's $( ) too")
+    cs("( case a in a) :;; esac )\nx=`case a in a) :;; esac`\n", [], "a subshell or backquotes pass")
+    cs("x=$(y=`case a in a) :;; esac`)\n", [], "backquotes inside $( ) reset it")
+    cs("x=$(y=`echo $(case a in a) :;; esac)`)\n", [1], "a $( ) inside those backquotes counts")
+    cs("cat <(case a in a) :;; esac)\ncat >(case a in\n b) :;; esac)\n", [1, 3],
+       "a process substitution counts, either direction")
+    cs('x="$(case a in a) :;; esac)"\n', [1], "a quoted $( ) counts: bash -n passes, the run dies")
+    cs("x=$(case a in (a|b) :;& c) :;; esac)\nx=$(case a in (a) :;;& (b) :;; d) :;; esac)\n", [1, 2],
+       "a bare pattern after ;& or ;;& is refused, a led one after ;; passes")
+    cs("x=$(case a in (a) :;; esac; echo b)\nx=$(echo)\ncase a in a) :;; esac\n", [],
+       "esac and the closing ) end the substitution's reach")
+    cs("x=$(case a in\n  # c) a comment\n  (a) :;;\nesac; echo '# case a in a)' \"case a in a)\")\n", [],
+       "comments and quoted text are not patterns")
+    cs("x=$(echo a#b $# \"\\\"\" \"$(echo \\\")\"; case a in a) :;; esac)\n", [1],
+       "a mid-word # is no comment; escapes in and out of quotes")
+    cs("x=$(echo \\)\ncase a in a) :;; esac)\n", [2], "an escaped ) does not close the substitution")
+    cs("x=$(cat <<E\ncase a in a) x;; esac\nE\ncat <<-'F'\n\tb) )\n\tF\ncase a in a) :;; esac)\n", [7],
+       "here-document bodies are skipped, and scanning resumes after the delimiter")
+    cs("x=$(cat <<<case; case a in a) :;; esac)\n", [1], "a here-string is not a here-document")
+    cs("x=$(echo $(( (1)+2 )) ${y:-z}; case a in a) :;; esac)\nx=$(( (1) ))${y}\ncase a in a) :;; esac\n",
+       [1], "arithmetic and ${ } nest and close")
+    cs("x=$(f() { case a in a) :;; esac; }; ( case b in b) :;; esac ))\n", [1],
+       "a function or subshell inside $( ) is still inside it")
+    cs("x=$(if t; then case a in a) :;; esac; fi; while t; do case b in\n b) :;; esac; done)\n", [1, 2],
+       "case after then and do is a keyword")
+    cs("x=$(t && case a in a) :;; esac)\nx=$(case a in (a) case b in b) :;; esac;; esac)\n", [1, 2],
+       "case after && and a nested case after a pattern are keywords")
+    cs("local rt case\ncase=$(echo case a in b)\nx=$(mycase a in b)\n", [],
+       "case as an argument, a variable or inside a word is not the keyword")
+    cs('x=$(case "$y" in ("a)") :;; \'b)\'|c) :;; esac)\n', [1], "a pattern's quoted ) is not its end")
+    cs("$(case a in a) :;; esac)\n\nx=$(case a in (a\\'\"\") :;;\n c) :;; esac)\n", [1, 4],
+       "a $( ) at the text's start; an escaped quote and an empty quote inside a led pattern")
+    cs("\n# $(\ncase a in a) :;; esac\nx=$(case a in (a);;\n b) :;; esac)\n", [5],
+       "a leading newline counts; a comment opens no $( ); ;; right after a pattern")
+    cs("x=$(echo ')' '' \")\" ${#a} $((1)) $(((1)+(2))); case a in a) :;; esac)\n", [1],
+       "quoted ), an empty quote, ${#...}, arithmetic: none closes the substitution")
+    cs("x=$(echo $((1)))\ncase a in a) :;; esac\nx=${y}$(case a in a) :;; esac)\n", [3],
+       "arithmetic and ${ } close where they end")
+    cs("x=$(echo # )\ncase a in a) :;; esac)\nx=$(case a in (a) :;;&(b) :;;\n c) :;; esac)\n", [2, 4],
+       "a comment's ) closes nothing; ;;& is consumed whole")
+    cs("x=$(cat <<E\nE\ncase a in a) :;; esac)\nx=$(case a in (a) :\nesac)\ncase b in b) :;; esac\n", [3],
+       "a here-document's delimiter can be its first line; esac after a body without ;; ends the case")
+    cs("x=$(cat <<-E\n\t\tE\ncase a in a) :;; esac)\nx=$(cat <<E\n\tE\ncase a in a) :;; esac\nE\n)\n", [3],
+       "<<- strips tabs before its delimiter, << does not")
+    cs("x=`echo $(case a in a) :;; esac)`; y=$(z=`case a in a) :;; esac`)\n", [1],
+       "case right after a backquote is a keyword; a $( ) inside backquotes counts")
+    # The CLI over a scratch repository: both rules, `--check` on the tree and at a ref.
+    import tempfile
+    sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "tests"))
+    from throwaway_git import throwaway_git_init
+    with tempfile.TemporaryDirectory() as d:
+        env = throwaway_git_init(d, "-q")
+        (Path(d) / "tools").mkdir()
+        (Path(d) / "tools/a.sh").write_text('f "${a[@]}"\nx=$(case a in a) :;; esac)\n')
+        (Path(d) / "tools/b.txt").write_text('f "${a[@]}"\n')
+
+        def cli(*args):
+            r = subprocess.run([sys.executable, "-I", __file__, *args], cwd=d, env=env,
+                               capture_output=True, text=True)
+            return r.returncode, r.stdout.split("\n")[:-1]
+
+        subprocess.run(["git", "add", "-A"], cwd=d, env=env, check=True)
+        subprocess.run(["git", "commit", "-qm", "x"], cwd=d, env=env, check=True)
+        want = (1, ['tools/a.sh:1: f "${a[@]}"', "tools/a.sh:2: x=$(case a in a) :;; esac)"])
+        st(cli("--check"), want, "--check prints each site of both rules in .sh files, rc 1")
+        (Path(d) / "tools/a.sh").write_text("x=$(case a in (a) :;; esac)\n")
+        st(cli("--check"), (0, []), "--check on the repaired tree passes (null)")
+        st(cli("--check", "--ref", "HEAD"), want, "--check --ref reads the commit, not the tree")
+        st(cli()[0], 2, "no arm prints the usage, rc 2")
     for f in fails:
         print("FAIL", f)
     print("bare_array self-test:", "FAILED" if fails else "ok")
@@ -133,7 +307,8 @@ if __name__ == "__main__":
     if "--check" in sys.argv:
         ref = sys.argv[sys.argv.index("--ref") + 1] if "--ref" in sys.argv else None
         hits = scan(ref)
-        print("\n".join(hits))
+        if hits:
+            print("\n".join(hits))
         sys.exit(1 if hits else 0)
     print(__doc__)
     sys.exit(2)
diff --git a/tools/audit/seat/instruments/bare_array.py.md b/tools/audit/seat/instruments/bare_array.py.md
index 529187f451..f3c694b6b2 100644
--- a/tools/audit/seat/instruments/bare_array.py.md
+++ b/tools/audit/seat/instruments/bare_array.py.md
@@ -11,3 +11,9 @@
   on the line or on a comment-only line directly above it; a line ending in
   `# mut:<name>` takes the reason above, and a reason placed after that marker
   is refused on any line, because it unanchors the self-test's mutant.
+  Second rule: a `case` pattern without its leading `(` inside a `$( ... )`,
+  `<( ... )` or `>( ... )` substitution, quoted or not, is refused: bash 3.2
+  ends the substitution at the pattern's `)`, so `bash -n` fails (PR 3520 put
+  one in `tick_loop.sh`, whose freshness check then refused every tick pass),
+  or, quoted, the run dies. The way out is the `(`, as in `(func) ...;;`; no
+  marker excuses one, since 3.2 never parses it.
diff --git a/tools/audit/seat/instruments/update_pr.sh.md b/tools/audit/seat/instruments/update_pr.sh.md
index f964bc717c..eac78f7f29 100644
--- a/tools/audit/seat/instruments/update_pr.sh.md
+++ b/tools/audit/seat/instruments/update_pr.sh.md
@@ -17,6 +17,7 @@
   body move of a PR whose head holds its handoff, with `HPO_UPDATE_BODY_ONLY=1`:
   a run that would then move the head (a DIRTY PR's clean main merge, an added
   row) refuses and pushes nothing, since that move skipped the review freeze.
+  A body carrying a generated figure block has it re-rendered (`figure_block.py refresh`, as `open_pr.sh` does) at the head the run pushes or patches, on both paths, before app_push.sh or body_patch.sh; a failed refresh refuses, pushing and patching nothing; a body with no block is untouched.
   When: updating a PR after review prep or a main merge, or re-bodying it.
   Refusal: as `remerge_main.sh` — a conflict stops, it is never resolved
   silently; no open PR at the branch stops before any push. Up front, each an
diff --git a/tools/audit/seat/pr_args.sh b/tools/audit/seat/pr_args.sh
index 63c2e08c89..dbf53479dc 100644
--- a/tools/audit/seat/pr_args.sh
+++ b/tools/audit/seat/pr_args.sh
@@ -485,9 +485,17 @@ pr_pushers() { # [<root>] [<rev>]: the census; one line per seam, exit 1 on any
 # copyin carries ref_privacy.py for the same reason: handoff_push.sh's guard
 # fails closed without it, so its reap arms never reached a push (#2668's CI).
 pr_args_self_test() (
-  local src t f=0 n=0 o m base code side body i reapsha UNREL
+  local src seat t f=0 n=0 o m base code side body i reapsha UNREL
   src=$PR_ARGS_DIR
   t=$(mktemp -d) || { echo "pr_args self-test: no temporary directory"; return 1; }
+  # The programs under test are copied from a snapshot of them taken here, never from the live
+  # checkout: a job step that moves the checkout mid-run (tick_loop.sh's restart onto origin/main)
+  # would otherwise hand the later arms the base's copies (R10-HOTFIX-UPDATEPR-FIGURE-REFRESH).
+  # Only the files the arms copy in, and roster_lib.py, which pr_cap.py loads from beside itself: an arm
+  # naming one not listed fails at its cp, never reads the tree.
+  seat=$t/seat; mkdir "$seat" && (cd "$src" && cp -p delivery_row.sh gh_read.py handoff_push.sh open_pr.sh \
+    pr_args.sh pr_cap.py ref_privacy.py remerge_main.sh roster_lib.py update_pr.sh "$seat/") \
+    || { echo "pr_args self-test: no snapshot of the programs under test"; rm -rf "$t"; return 1; }
   # The pusher stubs the reap arms drive read this directory ($T is open_pr's topic).
   REAP_DIR=$t; export REAP_DIR
   # A stopped pusher's stub app_push: it records itself and a two-level sleep
@@ -542,8 +550,8 @@ STUB
   copyin() { # <mutant|->: copies of the scripts, less the named mutant's line
     local g
     for g in open_pr.sh update_pr.sh handoff_push.sh remerge_main.sh delivery_row.sh pr_args.sh pr_cap.py ref_privacy.py gh_read.py; do
-      if [ "$1" = - ]; then cp "$src/$g" "$m/tools/audit/seat/$g"
-      else grep -v "# mut:$1\$" "$src/$g" > "$m/tools/audit/seat/$g"; fi
+      if [ "$1" = - ]; then cp "$seat/$g" "$m/tools/audit/seat/$g"
+      else grep -v "# mut:$1\$" "$seat/$g" > "$m/tools/audit/seat/$g"; fi
     done
   }
   i=0
@@ -692,8 +700,8 @@ STUB
   git -C "$o" reset -q --hard "$base"
   relsrc() { # <mutant|-> <fresh clone> <sibling>: source by a relative path, cd to the sibling, ask
     mkdir -p "$2/tools/audit/seat"
-    if [ "$1" = - ]; then cp "$src/pr_args.sh" "$2/tools/audit/seat/pr_args.sh"
-    else grep -v "# mut:$1\$" "$src/pr_args.sh" > "$2/tools/audit/seat/pr_args.sh"; fi
+    if [ "$1" = - ]; then cp "$seat/pr_args.sh" "$2/tools/audit/seat/pr_args.sh"
+    else grep -v "# mut:$1\$" "$seat/pr_args.sh" > "$2/tools/audit/seat/pr_args.sh"; fi
     ( unset PR_ARGS_DIR; cd "$2" && . ./tools/audit/seat/pr_args.sh && cd "$3" && PR_NAME=fresh pr_tools_fresh ) > "$t/out" 2>&1
   }
   relsrc - "$t/fr" "$t/st"; ck "pr_args: sourced by a relative path from a fresh clone, then cd'd into a stale sibling, passes" $?
@@ -1259,8 +1267,8 @@ STUB
     git -C "$m" worktree prune; git -C "$m" branch -qD fix/r 2>/dev/null
     git -C "$o" branch -qD fix/r 2>/dev/null
     for g in open_pr.sh update_pr.sh delivery_row.sh pr_args.sh pr_cap.py; do
-      if [ "$1" = - ]; then cp "$src/$g" "$m/tools/audit/seat/$g"
-      else grep -v -e "# mut:${1%%+*}\$" -e "# mut:${1##*+}\$" "$src/$g" > "$m/tools/audit/seat/$g"; fi  # a+b: two mutants at once
+      if [ "$1" = - ]; then cp "$seat/$g" "$m/tools/audit/seat/$g"
+      else grep -v -e "# mut:${1%%+*}\$" -e "# mut:${1##*+}\$" "$seat/$g" > "$m/tools/audit/seat/$g"; fi  # a+b: two mutants at once
     done
     cp "$t/body.md" "$t/bR.md"
     HPO_STATE_DIR=$sd STUB_DIR=$sdir BR=fix/r BR_FIXED=1 bash "$m/tools/audit/seat/open_pr.sh" r "$codeR" T G > "$t/outo" 2>&1 & op=$!
@@ -1412,7 +1420,7 @@ STUB
     sd=$(cd "$sd" && pwd -P); rm -rf "$sdir"; mkdir -p "$sdir"; figbody "$2"
     printf 'z\n' > "$o/zz" && git -C "$o" add zz && git -C "$o" -c user.name=t -c user.email=t@t commit -q -m "main file"
     for g in open_pr.sh delivery_row.sh pr_args.sh pr_cap.py; do
-      if [ "$1" = - ]; then cp "$src/$g" "$m/tools/audit/seat/$g"; else grep -v "# mut:$1\$" "$src/$g" > "$m/tools/audit/seat/$g"; fi
+      if [ "$1" = - ]; then cp "$seat/$g" "$m/tools/audit/seat/$g"; else grep -v "# mut:$1\$" "$seat/$g" > "$m/tools/audit/seat/$g"; fi
     done
     HPO_STATE_DIR=$sd STUB_DIR=$sdir bash "$m/tools/audit/seat/open_pr.sh" f "$codeF" T G > "$t/fo" 2>&1; echo $? > "$t/frc"
     git -C "$o" cat-file -e fix/f-pr:dev/programme/delivery/5.md 2>/dev/null && echo 1 > "$t/frow" || echo 0 > "$t/frow"
@@ -1435,6 +1443,59 @@ STUB
   ck "open_pr: a re-run after an open closed at its row push clears the left-over branch and worktree and opens" $?
   figrun opfig2 block; figrun opclear block keep; [ "$(cat "$t/frc")" != 0 ] && [ "$(cat "$t/frow")" = 0 ]
   ck "  mutant mut:opclear (its line deleted): the re-run fails at git worktree add -b on the left-over branch (the defect)" $?
+  # R10-HOTFIX-UPDATEPR-FIGURE-REFRESH: update_pr.sh re-renders the body's figure blocks at the head it
+  # pushes (moved-head path, before app_push) or patches (body-only path, before body_patch.sh), as
+  # open_pr.sh's op_figures does. fix/g starts at $base; handoff/f's pusher stub is lint's figure-block
+  # head check; the stub figure_block.py rewrites head= to HEAD, notes each call and fails while $t/figfail exists.
+  cat > "$m/tools/pr/figure_block.py" <<STUBF
+import os, re, subprocess, sys
+open("$t/figcalled", "a").close()
+if os.path.exists("$t/figfail"): sys.exit(1)
+f = sys.argv[sys.argv.index("refresh") + 1]
+h = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
+t = re.sub(r"head=[0-9a-f]{40}", "head=" + h, open(f).read())
+open(f, "w").write(t)
+STUBF
+  cp "$t/bin/gh" "$t/gh.orig"
+  printf '#!/bin/sh\ncase "$*" in *--head*) echo 5 ;; *mergeStateStatus*) echo CLEAN ;; "pr view"*) echo "a title" ;; *) exit 99 ;; esac\n' > "$t/bin/gh"
+  printf '#!/bin/bash\necho called >> "%s/ubp.log"\nh=$(grep -o "^<!-- figure-block: [a-z-]* mb=[0-9a-f]* head=[0-9a-f]*" "$5" | grep -o "head=.*" | cut -c6-)\n[ -z "$h" ] || [ "$h" = "$4" ] || { echo "body_patch: REFUSE: figure-block scope-line names another head ($h)"; exit 1; }\necho "body_patch: OK"\n' "$t" > "$t/ubp.sh"
+  ufig() { # <mutant|-> <code sha|-> <block|none>: update_pr.sh fix/g over a body with (or without) a figure block naming the code head
+    rm -f "$t/figcalled"
+    if [ "$3" = block ]; then printf '## Head\n\nthe body\n\n## Figures\n\n<!-- figure-block: scope-line mb=%s head=%s -->\n~~~text\nx\n~~~\n<!-- /figure-block -->\n' "$base" "$codeF" > "$t/bu.md"
+    else printf '## Head\n\nthe body\n' > "$t/bu.md"; fi
+    git -C "$o" rev-parse fix/g > "$t/ubefore" 2>/dev/null || echo none > "$t/ubefore"
+    HANDOFF_TOPIC=f HPO_BODY_PATCH=$t/ubp.sh run "$1" update_pr.sh fix/g "$2" "$t/bu.md"
+    git -C "$o" rev-parse fix/g > "$t/uafter"
+  }
+  ufresh() { git -C "$o" branch -f fix/g "$base"; rm -f "$t/figfail" "$t/ubp.log"; }
+  ubody() { grep -o '^<!-- figure-block: [a-z-]* mb=[0-9a-f]* head=[0-9a-f]*' "$t/bu.md" | grep -o 'head=.*' | cut -c6-; }
+  ufresh; ufig - "$codeF" block
+  [ "$(cat "$t/rc")" = 0 ] && [ "$(ubody)" = "$(cat "$t/uafter")" ] && [ "$(cat "$t/uafter")" != "$(cat "$t/ubefore")" ]
+  ck "update_pr: a moved head with a figure block pushes a body whose block names the new head" $?
+  ufresh; ufig updfig1 "$codeF" block
+  [ "$(cat "$t/rc")" != 0 ] && grep -qF "figure-block scope-line names another head" "$t/out"
+  ck "  mutant mut:updfig1 (its line deleted): the push carries a block naming another head and is refused" $?
+  ufresh; touch "$t/figfail"; ufig - "$codeF" block
+  [ "$(cat "$t/rc")" != 0 ] && grep -qF "update_pr: REFUSE: the figure-block refresh at the head to push failed" "$t/out" && [ "$(cat "$t/uafter")" = "$base" ]
+  ck "update_pr: a failing refresh at the head to push refuses and pushes nothing" $?
+  ufresh; ufig - "$codeF" block; rm -f "$t/ubp.log"
+  ufig - - block
+  [ "$(cat "$t/rc")" = 0 ] && [ "$(cat "$t/ubefore")" = "$(cat "$t/uafter")" ] && grep -qF "update_pr: BODY-ONLY" "$t/out" && [ "$(ubody)" = "$(cat "$t/uafter")" ] && [ "$(wc -l < "$t/ubp.log")" = 1 ]
+  ck "update_pr: a body-only run over a block naming the code head patches a body naming the live head" $?
+  ufig updfig2 - block
+  [ "$(cat "$t/rc")" != 0 ] && grep -qF "body_patch: REFUSE: figure-block scope-line names another head" "$t/out"
+  ck "  mutant mut:updfig2 (its line deleted): body_patch.sh is handed a block naming another head and refuses" $?
+  rm -f "$t/ubp.log"; touch "$t/figfail"; ufig - - block
+  [ "$(cat "$t/rc")" != 0 ] && grep -qF "update_pr: REFUSE: the figure-block refresh at the unmoved head failed" "$t/out" && [ ! -e "$t/ubp.log" ] && [ "$(cat "$t/ubefore")" = "$(cat "$t/uafter")" ]
+  ck "update_pr: a failing refresh on the body-only path refuses and patches nothing" $?
+  ufresh; ufig - "$codeF" none
+  [ "$(cat "$t/rc")" = 0 ] && [ ! -e "$t/figcalled" ] && ! grep -q 'figure-block' "$t/bu.md"
+  ck "null control: a body with no figure block never reaches the refresh and is pushed as before" $?
+  ufresh; ufig - "$codeF" none; ufig - - none
+  [ "$(cat "$t/rc")" = 0 ] && [ ! -e "$t/figcalled" ] && grep -qF "update_pr: BODY-ONLY" "$t/out"
+  ck "null control: a body-only run over a body with no figure block never reaches the refresh" $?
+  git -C "$o" branch -qD fix/g; git -C "$o" reset -q --hard "$base"; cp "$t/gh.orig" "$t/bin/gh"
+  git -C "$m" worktree prune; git -C "$m" branch -qD fix/g 2>/dev/null; git -C "$m" update-ref -d refs/remotes/origin/fix/g; true
   # R10-FLOW-BODY-ONLY parts (a) and (b), ruling R4: update_pr.sh merges origin/main only when the PR
   # is DIRTY or the merge would conflict, and a head the run leaves unmoved is re-bodied by
   # body_patch.sh (here a stub, HPO_BODY_PATCH) with no push. handoff/v carries a push stub that
@@ -1558,7 +1619,7 @@ GH
     rm -rf "$sd" "$sdir"; mkdir -p "$sdir" "$sd"; sd=$(cd "$sd" && pwd -P)
     git -C "$m" worktree prune; git -C "$m" branch -qD fix/r 2>/dev/null; git -C "$o" branch -qD fix/r 2>/dev/null
     for g in open_pr.sh update_pr.sh delivery_row.sh pr_args.sh pr_cap.py; do
-      if [ "$1" = - ]; then cp "$src/$g" "$m/tools/audit/seat/$g"; else grep -v "# mut:$1\$" "$src/$g" > "$m/tools/audit/seat/$g"; fi
+      if [ "$1" = - ]; then cp "$seat/$g" "$m/tools/audit/seat/$g"; else grep -v "# mut:$1\$" "$seat/$g" > "$m/tools/audit/seat/$g"; fi
     done
     case ${2:-} in edit) touch "$sdir/editfail" ;; postpush) touch "$sdir/p2postfail" ;; selftest) touch "$sdir/p2selftest" ;; host) touch "$sdir/p2selftest" "$sdir/hostfail" ;; stmix|body) touch "$sdir/p2$2" "$sdir/hostfail" ;;
       stalefig) touch "$sdir/hostfail" "$sdir/figfail"; mkdir -p "$sd/pr/r" && printf '  REFUSE   self-test             FAIL x\n' > "$sd/pr/r/p2.log" ;; *) touch "$sdir/p2fail" ;; esac
@@ -1650,11 +1711,11 @@ STUB
   }
   hrlib() { # <-|mutant|ret:tag|shared>: the library the next hrrun sources; ret:<tag> turns that line's `|| return 1` into `|| return 0`
     case $1 in
-      -) cp "$src/pr_args.sh" "$t/hr/lib.sh" ;;
-      ret:*) sed "/# $1\$/s/|| return 1/|| return 0/" "$src/pr_args.sh" > "$t/hr/lib.sh" ;;
+      -) cp "$seat/pr_args.sh" "$t/hr/lib.sh" ;;
+      ret:*) sed "/# $1\$/s/|| return 1/|| return 0/" "$seat/pr_args.sh" > "$t/hr/lib.sh" ;;
       # one tree for every measurement, replaced by whichever run starts next: the blocked head's pr_step_sig
-      shared) sed '/# ret:sigpriv$/s|w=.*|w=$3/tree; git -C "$1" worktree remove --force "$w" >/dev/null 2>\&1; rm -rf "$w"; mkdir -p "$w"|' "$src/pr_args.sh" > "$t/hr/lib.sh" ;;
-      *) grep -v "# mut:$1\$" "$src/pr_args.sh" > "$t/hr/lib.sh" ;;
+      shared) sed '/# ret:sigpriv$/s|w=.*|w=$3/tree; git -C "$1" worktree remove --force "$w" >/dev/null 2>\&1; rm -rf "$w"; mkdir -p "$w"|' "$seat/pr_args.sh" > "$t/hr/lib.sh" ;;
+      *) grep -v "# mut:$1\$" "$seat/pr_args.sh" > "$t/hr/lib.sh" ;;
     esac
   }
   hrrun() { # <head sha> [main sha] [log] -> pr_host_refusal's status
@@ -1823,7 +1884,7 @@ STUB
     local sd=$t/mconf-$1 g
     rm -rf "$sd"; mkdir -p "$sd"; sd=$(cd "$sd" && pwd -P); git -C "$m" worktree prune; git -C "$m" branch -qD fix/q 2>/dev/null
     for g in open_pr.sh update_pr.sh delivery_row.sh pr_args.sh pr_cap.py; do
-      if [ "$1" = - ]; then cp "$src/$g" "$m/tools/audit/seat/$g"; else grep -v "# mut:$1\$" "$src/$g" > "$m/tools/audit/seat/$g"; fi
+      if [ "$1" = - ]; then cp "$seat/$g" "$m/tools/audit/seat/$g"; else grep -v "# mut:$1\$" "$seat/$g" > "$m/tools/audit/seat/$g"; fi
     done
     HPO_STATE_DIR=$sd BR=fix/q BR_FIXED=1 bash "$m/tools/audit/seat/open_pr.sh" q "$codeR" T G > "$t/outq" 2>&1; echo $? > "$t/rcq"
     [ -d "$sd/pr/q/wt" ] && echo kept > "$t/wtq" || echo gone > "$t/wtq"
@@ -1846,8 +1907,8 @@ STUB
     local sd=$t/unp-$1-$2-${3:--} g
     rm -rf "$sd" "$sd.link" "$t/s$i"; git -C "$m" worktree prune; git -C "$m" branch -qD fix/u 2>/dev/null; mkdir -p "$sd/pr/u"; sd=$(cd "$sd" && pwd -P)
     for g in open_pr.sh update_pr.sh delivery_row.sh pr_args.sh pr_cap.py; do
-      if [ "$1" = - ]; then cp "$src/$g" "$m/tools/audit/seat/$g"
-      else grep -v "# mut:$1\$" "$src/$g" > "$m/tools/audit/seat/$g"; fi
+      if [ "$1" = - ]; then cp "$seat/$g" "$m/tools/audit/seat/$g"
+      else grep -v "# mut:$1\$" "$seat/$g" > "$m/tools/audit/seat/$g"; fi
     done
     git -C "$m" fetch -q origin fix/u && git -C "$m" worktree add -q -b fix/u "$sd/pr/u/wt" origin/fix/u || return 1
     [ "$2" = 0 ] || { printf 'row\n' > "$sd/pr/u/wt/row" && git -C "$sd/pr/u/wt" add row && git -C "$sd/pr/u/wt" commit -q -m row; }
@@ -1948,7 +2009,7 @@ STUB
   fi
   rmrun() { # <mutant|-> <branch>: remerge_main.sh on <branch> in worktree $t/rmw; the output in $t/out
     local g; git -C "$t/rmm" worktree remove --force "$t/rmw" 2>/dev/null; rm -rf "$t/rmw"; git -C "$t/rmm" worktree prune
-    for g in remerge_main.sh pr_args.sh gh_read.py; do grep -v "# mut:$1\$" "$src/$g" > "$t/rmm/tools/audit/seat/$g"; done
+    for g in remerge_main.sh pr_args.sh gh_read.py; do grep -v "# mut:$1\$" "$seat/$g" > "$t/rmm/tools/audit/seat/$g"; done
     git -C "$t/rmm" fetch -q origin "$2" && git -C "$t/rmm" worktree add -q -B "$2" "$t/rmw" "origin/$2" \
       && PATH="$t/rmgit:$PATH" bash "$t/rmm/tools/audit/seat/remerge_main.sh" 7 "$t/rmw" "$2" "$t/body.md" > "$t/out" 2>&1
     echo $? > "$t/rc"
@@ -2113,7 +2174,7 @@ print(n)' "$1"
   # line above leaves that line running on into the next (round 2's first mut:fggc did, and its arm
   # read the broken copy as a pass). mutshape <files...>: exit 1 naming each such line.
   mutshape() { awk 'prev ~ /\\$/ && /# mut:[A-Za-z0-9]+$/ { print FILENAME ":" FNR; bad = 1 } { prev = $0 } END { exit bad }' "$@"; }
-  (cd "$src" && mutshape open_pr.sh update_pr.sh handoff_push.sh remerge_main.sh delivery_row.sh pr_args.sh)
+  (cd "$seat" && mutshape open_pr.sh update_pr.sh handoff_push.sh remerge_main.sh delivery_row.sh pr_args.sh)
   ck "every # mut: line is a whole statement, never one continued from the line above" $?
   printf 'a \\\n  b  # mut:x\n' > "$t/mutshape.sh"; ! mutshape "$t/mutshape.sh" >/dev/null
   ck "null control: a # mut: line continued from the line above is named" $?
@@ -2125,7 +2186,7 @@ print(n)' "$1"
   rkrun() { # <mutant|-> <stub rc> -> $t/rk.argv: what the stub saw; $t/rk.err: the statement's stderr
     : > "$t/rk.argv"
     printf '#!/bin/bash\necho "$*" >> "%s/rk.argv"\nexit %s\n' "$t" "$2" > "$t/rkseat/bus.sh"
-    if [ "$1" = - ]; then grep -h '# mut:rekey$' "$src/open_pr.sh"; else grep -h '# mut:rekey$' "$src/open_pr.sh" | grep -v "# mut:$1\$"; fi > "$t/rk.line"
+    if [ "$1" = - ]; then grep -h '# mut:rekey$' "$seat/open_pr.sh"; else grep -h '# mut:rekey$' "$seat/open_pr.sh" | grep -v "# mut:$1\$"; fi > "$t/rk.line"
     SEAT=$t/rkseat PR_NAME=open_pr T=ht N=77 bash "$t/rk.line" 2> "$t/rk.err"
     echo $? > "$t/rk.rc"
   }
@@ -2138,7 +2199,7 @@ print(n)' "$1"
   rkrun rekey 0; [ ! -s "$t/rk.argv" ]
   ck "  mutant mut:rekey (its line deleted) re-keys nothing" $?
   # The cap's own counting rule, which orchestrator_tick.py imports too.
-  python3 -I "$src/pr_cap.py" --self-test > "$t/cap.out" 2>&1 && grep -q 'pr_cap self-test: [1-9][0-9]* checks, 0 failed' "$t/cap.out"
+  python3 -I "$seat/pr_cap.py" --self-test > "$t/cap.out" 2>&1 && grep -q 'pr_cap self-test: [1-9][0-9]* checks, 0 failed' "$t/cap.out"
   ck "pr_cap.py --self-test: its tally says 0 failed" $?
   reap
   kill "$UNREL" 2>/dev/null; wait "$UNREL" 2>/dev/null || :
diff --git a/tools/audit/seat/tick_loop.sh b/tools/audit/seat/tick_loop.sh
index d0b7147789..0b35a54fa4 100644
--- a/tools/audit/seat/tick_loop.sh
+++ b/tools/audit/seat/tick_loop.sh
@@ -463,9 +463,9 @@ f = open(sys.argv[1], "a"); fcntl.flock(f, fcntl.LOCK_EX); open(sys.argv[1] + ".
       local v=$t/victim-$1.git; rm -f "$t/shadow"; throwaway_git_init "$v" -q --bare || return 1
       out=$(export HPO_HEARTBEAT_REMOTE=$v TICK_RC=1
         case $1 in
-          func) . "$t/execfn"; export -f exec; "$BASH" "$HERE/tick_loop.sh" --self-test --nested ;;
-          bashenv) BASH_ENV=$t/execfn "$BASH" "$HERE/tick_loop.sh" --self-test --nested ;;
-          none) "$BASH" "$HERE/tick_loop.sh" --self-test --nested ;;
+          (func) . "$t/execfn"; export -f exec; "$BASH" "$HERE/tick_loop.sh" --self-test --nested ;;
+          (bashenv) BASH_ENV=$t/execfn "$BASH" "$HERE/tick_loop.sh" --self-test --nested ;;
+          (none) "$BASH" "$HERE/tick_loop.sh" --self-test --nested ;;
         esac 2>&1); src=$?
       refs=$(git -C "$v" for-each-ref | grep -c .); }
     for c in func bashenv; do
diff --git a/tools/audit/seat/update_pr.sh b/tools/audit/seat/update_pr.sh
index 611d4360f3..bd00868f07 100755
--- a/tools/audit/seat/update_pr.sh
+++ b/tools/audit/seat/update_pr.sh
@@ -97,6 +97,15 @@ TTL=$(gh pr view "$N" -R $R --json title -q .title)
 _added=$(ensure_row . "$N" "$(row_line "$N" $R "$TTL")")
 ROW=""; [ -z "$_added" ] || ROW="adds one commit containing only this PR's own row, \`$_added\`"
 M=$(git rev-parse --short origin/main); H=$(git rev-parse HEAD)
+# A generated figure block names the head it was rendered at (figure_block.py refresh, as open_pr.sh's
+# op_figures), and the merges and the row above moved it: re-render at the head this run pushes or patches,
+# before either. A body with no block is untouched; a failed refresh refuses, pushing and patching nothing.
+upd_figures() { # <where>
+  grep -q '^<!-- figure-block: ' "$B" || return 0
+  python3 -I "$PRT/figure_block.py" refresh "$B" --base origin/main --head HEAD > $WT.fig.log 2>&1 && return 0
+  pr_refuse "the figure-block refresh $1 failed; nothing is pushed or patched:
+$(tail -n 20 $WT.fig.log)"
+}
 # HPO_UPDATE_BODY_ONLY (cloud_relay.sh's handoff_arm, on a body-only move it does not review-freeze):
 # the head must stay the live head, so a DIRTY merge of main or an added row refuses, pushing nothing
 # (#3089 review round 2): only the orchestrator, past the freeze, moves a head under review.
@@ -117,6 +126,7 @@ import sys; from head_note import prefix
 p,H=sys.argv[1:3]; s=open(p).read()
 s=prefix(s,"`%s` is this PR's head, unchanged: its code was already in it and main merged cleanly, so the orchestrator's script set this body without a push.\n\n"%H); open(p,'w').write(s)
 E
+  upd_figures "at the unmoved head"  # mut:updfig2
   rc=0; ( cd "$WT" && bash "${HPO_BODY_PATCH:-$SEAT/body_patch.sh}" --repo $R "$N" "$H" "$B" ) > $WT.log 2>&1 || rc=$?
   cat $WT.log
   [ "$rc" = 0 ] || pr_refuse "body-only: body_patch.sh refused #$N at $H (exit $rc); its log is $WT.log"
@@ -131,6 +141,7 @@ if MM: pre="`%s` "%H + ((N+" and then ") if N else "") + "merges origin/main `%s
 else: pre="`%s` "%H + " and then ".join(x for x in (N, R) if x) + ".\n\n"  # main merged cleanly: not merged (R4)
 s=prefix(s,pre); open(p,'w').write(s)
 E
+upd_figures "at the head to push"  # mut:updfig1
 if test -f tools/audit/app_push.sh; then _push=tools/audit/app_push.sh; else _push=tools/pr/app_push.sh; fi
 RO=""; [ "$(git rev-parse "$H^@")" != "$LIVE" ] || RO=--row-only  # mut:rowonly
 [ -n "$RO" ] || RO=--reuse  # mut:updreuse
diff --git a/tools/ci/selftest_closures.json b/tools/ci/selftest_closures.json
index d56ec9a60d..f5a326bae7 100644
--- a/tools/ci/selftest_closures.json
+++ b/tools/ci/selftest_closures.json
@@ -1387,22 +1387,7 @@
     "dev/audit/rounds/round4/D1/verify2_d102.py",
     "dev/audit/rounds/round4/D1/verify2_d1inst.py",
     "dev/audit/rounds/round4/D10",
-    "dev/audit/rounds/round4/D10/coverage_measure.sh",
-    "dev/audit/rounds/round4/D10/d10_own_D10-01.py",
-    "dev/audit/rounds/round4/D10/d10_own_D10-01.sh",
-    "dev/audit/rounds/round4/D10/d10_own_D10-02.py",
-    "dev/audit/rounds/round4/D10/d10_own_D10-03.py",
-    "dev/audit/rounds/round4/D10/log_when_unavailable.py",
-    "dev/audit/rounds/round4/D10/mypy_arms.sh",
-    "dev/audit/rounds/round4/D10/qs_rules.out.txt",
-    "dev/audit/rounds/round4/D10/qs_rules.py",
-    "dev/audit/rounds/round4/D10/quality_scale.draft.yaml",
-    "dev/audit/rounds/round4/D10/reports",
-    "dev/audit/rounds/round4/D10/reports/FINDER.md",
-    "dev/audit/rounds/round4/D10/verify-0-1.md",
-    "dev/audit/rounds/round4/D10/verify-0-2.md",
-    "dev/audit/rounds/round4/D10/verify-0-3.md",
-    "dev/audit/rounds/round4/D10/verify3",
+    "dev/audit/rounds/round4/D10/**",
     "dev/audit/rounds/round4/D10/verify3/**",
     "dev/audit/rounds/round4/D11",
     "dev/audit/rounds/round4/D11/d11_own_D11-01.py",
@@ -1664,9 +1649,7 @@
     "dev/audit/rounds/round4/resume_row.py",
     "dev/audit/rounds/round5",
     "dev/audit/rounds/round5-fix",
-    "dev/audit/rounds/round5-fix/R5-D7",
-    "dev/audit/rounds/round5-fix/R5-D7/learner_guard_ends.py",
-    "dev/audit/rounds/round5-fix/R5-INST-01",
+    "dev/audit/rounds/round5-fix/**",
     "dev/audit/rounds/round5-fix/R5-INST-01/**",
     "dev/audit/rounds/round5/D0",
     "dev/audit/rounds/round5/D0/seat-a",
@@ -1709,9 +1692,7 @@
     "dev/audit/rounds/round5/D4/seat-a",
     "dev/audit/rounds/round5/D4/seat-a/sweep.mjs",
     "dev/audit/rounds/round5/D7",
-    "dev/audit/rounds/round5/D7/seat-a",
-    "dev/audit/rounds/round5/D7/seat-a/sysid_step_bias.py",
-    "dev/audit/rounds/round5/D7/seat-b",
+    "dev/audit/rounds/round5/D7/**",
     "dev/audit/rounds/round5/D7/seat-b/**",
     "dev/audit/rounds/round5/D8",
     "dev/audit/rounds/round5/D8/seat-b",
@@ -2419,23 +2400,8 @@
     "tools/audit/seat/wt_sync.sh",
     "tools/audit/worktree_gc.sh",
     "tools/ci",
-    "tools/ci/alert_list.py",
-    "tools/ci/alert_list_mutants.sh",
-    "tools/ci/codescan_wait.py",
-    "tools/ci/fixtures",
-    "tools/ci/fixtures/gate_busy_defer_runs.json",
-    "tools/ci/fixtures/ruleset",
+    "tools/ci/**",
     "tools/ci/fixtures/ruleset/**",
-    "tools/ci/gate.py",
-    "tools/ci/ghapi.py",
-    "tools/ci/prelude.py",
-    "tools/ci/ruleset_cutover.py",
-    "tools/ci/selftest_closures.json",
-    "tools/ci/selftest_scope.py",
-    "tools/ci/selftest_scope_mutants.sh",
-    "tools/ci/selftest_step.sh",
-    "tools/ci/sweep.py",
-    "tools/ci/sweep_selftest.py",
     "tools/coverage",
     "tools/coverage/**",
     "tools/devices",
@@ -9159,6 +9125,7 @@
     "-",
     ".",
     "config",
+    "dev/programme/delivery/5.md",
     "objects",
     "packed-refs",
     "refs",

## Before you return the verdict (P275)
Run `python3 -I tools/audit/carry_audit.py check --body <PR body file> --comments <file holding [{"id": 0, "body": <verdict.md text>}]>`. Give every reported item its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>`;
an evidence line flagged by its wording takes `Carry: dismissed: evidence, not a finding`. Return the verdict only at rc 0.
