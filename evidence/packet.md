# Review packet #3412
head: 823d472de04391e40f80468e0b17073d94ccbe25
base: 04dfcafccdde1ee5df21a02fe4f06a5bc1083ea0

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: green
.github/dependabot.yml id=129783411785 success
CodeQL id=129789315612 success
arch-score / arch-score id=129808980218 success
arm id=129783505322 skipped
budget-raise-gate / budget-raise-gate id=129808979966 success
cancel-superseded id=129809031188 success
codeql id=129808980589 skipped
codeql / Analyze (actions) id=129787631574 success
codeql / Analyze (javascript-typescript) id=129787631754 success
codeql / Analyze (python) id=129787631632 success
gate id=129808979911 success
governance id=129808980347 skipped
governance / delivery-status id=129787631738 success
governance / delivery-status-publish id=129787634603 skipped
governance / env-matrix id=129787631835 success
governance / instrument-self-tests id=129787631768 success
governance / policy-docs id=129787631826 success
governance / record id=129787633445 skipped
governance / wave-script id=129787631675 success
hassfest id=129808980202 skipped
hassfest / hassfest id=129787631831 success
kernel-points id=129808980261 skipped
pr-contract id=129808981202 skipped
pr-contract / pr-contract id=129808102015 success
prelude id=129808979673 success
refresh id=129808978449 success
sweep-self id=129809293746 skipped
tests id=129808980235 skipped
tests / arch-instrument id=129789046737 success
tests / briefs id=129787631860 success
tests / browser id=129789046745 success
tests / ci-ratchet id=129806217885 skipped
tests / claims-autofix id=129800052325 skipped
tests / closure-scope id=129787631837 success
tests / closures id=129789046771 success
tests / closures-autofix id=129803078211 skipped
tests / coverage id=129789046696 success
tests / coverage-ratchet id=129806215372 success
tests / fast (3.14) id=129789046766 success
tests / graders-head-copy id=129806215401 success
tests / lane-proofs id=129806215376 success
tests / mutation id=129787631856 success
tests / mutation-autofix id=129789185150 skipped
tests / mutation-pins id=129789185186 skipped
tests / nightly-ha id=129789049524 skipped
tests / nightly-status id=129787631867 success
tests / replay id=129789049942 skipped
tests / typing id=129789046845 success
validate id=129808980414 skipped
validate / validate-hacs id=129787631774 success

## Refusals
none

## Advisories
hot-file: HPO_BUS_TRAIN_STATE is unset, so every merge verdict reads unboarded

## carry_audit at the head
CARRY-AUDIT: 0 finding item(s): 0 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
ok         python3 tools/policy/budget_raise_gate.py --self-test
             `tools/policy/budget_raise_gate.py` is in the tree at this head
  ok         python3 tools/pr/gh_comment.py self-test
             `tools/pr/gh_comment.py` is in the tree at this head
  ok         python3 tools/audit/seat/record_beat.py --self-test
             `tools/audit/seat/record_beat.py` is in the tree at this head
  ok         python3 tools/audit/seat/postmerge.py --self-test
             `tools/audit/seat/postmerge.py` is in the tree at this head
  ok         python3 tools/audit/seat/record_beat.py --dry-run 3350
             `tools/audit/seat/record_beat.py` is in the tree at this head
  ok         python3 tools/audit/seat/merge_train.py --self-test
             `tools/audit/seat/merge_train.py` is in the tree at this head
  ok         python3 tools/audit/seat/orchestrator_tick.py --self-test
             `tools/audit/seat/orchestrator_tick.py` is in the tree at this head
  ok         python3 tools/audit/seat/queue_pre_flight.py --self-test
             `tools/audit/seat/queue_pre_flight.py` is in the tree at this head
  ok         bash tools/audit/seat/merge_pr.sh --self-test
             `tools/audit/seat/merge_pr.sh` is in the tree at this head
  ok         python3 tools/audit/seat/gh_calls.py --self-test
             `tools/audit/seat/gh_calls.py` is in the tree at this head
  ok         gh api dot segments resolving to #201 is refused
             gh api dot segments: every long flag accepted
  unverified git archive
             `git archive` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  ok         python3 tools/audit/seat/plan_page.py --self-test
             `tools/audit/seat/plan_page.py` is in the tree at this head
  ok         python3 tools/audit/carry_audit.py --self-test
             `tools/audit/carry_audit.py` is in the tree at this head
  ok         python3 tools/audit/seat/handover_prompt.py --self-test
             `tools/audit/seat/handover_prompt.py` is in the tree at this head
  ok         python3 tools/audit/seat/record_row.py --self-test
             `tools/audit/seat/record_row.py` is in the tree at this head
  ok         python3 tools/audit/seat/proof_watch.py --self-test
             `tools/audit/seat/proof_watch.py` is in the tree at this head
  ok         python3 tools/audit/seat/pulse.py --self-test
             `tools/audit/seat/pulse.py` is in the tree at this head
  ok         python3 -I tools/audit/carry_audit.py --self-test
             `tools/audit/carry_audit.py` is in the tree at this head
  ok         python3 tools/audit/seat/r10_roster_ops_mutants.py --self-test
             `tools/audit/seat/r10_roster_ops_mutants.py` is in the tree at this head
  ok         bash tools/pr/prepr.sh --self-test
             `tools/pr/prepr.sh` is in the tree at this head
  ok         python3 tools/audit/seat/r10_mandate_guard_mutants.py --self-test
             `tools/audit/seat/r10_mandate_guard_mutants.py` is in the tree at this head
  ok         python3 dev/audit/harnesses/r10_plan_issues_chart_mutants.py M0 orphans-dropped tracking-orphan
             `dev/audit/harnesses/r10_plan_issues_chart_mutants.py` is in the tree at this head
  ok         python3 dev/audit/harnesses/r10_plan_page_mutants.py tracking-excluded
             `dev/audit/harnesses/r10_plan_page_mutants.py` is in the tree at this head
  ok         node tools/policy/policy_lint.mjs --budgets
             `tools/policy/policy_lint.mjs` is in the tree at this head
  ok         node tools/policy/rules_sync.mjs --check
             `tools/policy/rules_sync.mjs` is in the tree at this head
  ok         python3 tools/audit/seat/selftest_wiring.py --check
             `tools/audit/seat/selftest_wiring.py` is in the tree at this head
  ok         node tools/policy/brief_lint.mjs
             `tools/policy/brief_lint.mjs` is in the tree at this head
  ok         python3 tools/audit/archscore/score.py --diff b8f67a7751 HEAD
             `tools/audit/archscore/score.py` is in the tree at this head
  ok         python3 tests/structure.py
             `tests/structure.py` is in the tree at this head
  ok         python3 tests/closure.py select
             `tests/closure.py` is in the tree at this head
  ok         PYTHONPATH=tests/hastub python3 tests/entities.py
             `tests/entities.py` is in the tree at this head
  unverified git grep -n -E '#?\b201\b' -- tools dev/governance .claude tests CLAUDE.md AGENTS.md .github
             `git grep` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals

FIGURES: 31 resolved, 2 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
none

## Three-dot diff
diff --git a/.claude/rules/delivery-status-tracking.md b/.claude/rules/delivery-status-tracking.md
index 1ee41b30d..89a15fd2a 100644
--- a/.claude/rules/delivery-status-tracking.md
+++ b/.claude/rules/delivery-status-tracking.md
@@ -1,5 +1,5 @@
 ---
-description: Keep programme Delivery-status and #201 current after each merge
+description: Keep programme Delivery-status and #3394 current after each merge
 paths:
   - "dev/programme/plan*.md"
   - ".claude/workflows/*-groups.json"
@@ -12,7 +12,7 @@ After each programme merge — wave group, tooling the plan tracks, or a closed
 
 1. **The Delivery-status record** — the plan's frozen table plus one `dev/programme/delivery/<N>.md` per PR; authoritative vs wave body; if they disagree, fix it first.
 2. **`.claude/workflows/wave-*-groups.json` `resume` fields** — match measured `origin/main` (merged PR SHAs, open PR heads).
-3. **GitHub issue #201** — before each PR, merge or release, coordinate here; not a heartbeat.
+3. **Issue #3394** — before each PR, merge or release, coordinate here; not a heartbeat.
 4. **Every PR the programme has opened**, not only the ones a roster predicted. Hotfixes, instrument repairs, harness lanes, policy, and anything found *in passing* have no wave: give each **its own row and section**, never a wave it does not belong to.
 5. **Every open issue**, with a disposition: **scheduled** into a wave or group, **deferred** with a reason, or **refused** with a reason. **"Not mentioned" is not a disposition**: an issue absent from the plan is unscheduled work. At each record, grep the plan for every open issue's number.
 
diff --git a/.claude/rules/writing-for-agents.md b/.claude/rules/writing-for-agents.md
index cac684651..5bdaba192 100644
--- a/.claude/rules/writing-for-agents.md
+++ b/.claude/rules/writing-for-agents.md
@@ -50,7 +50,7 @@ it records**, riding the per-merge record obligation in
 `updated-for:` line names that merge. It links to the Delivery-status table
 rather than restating it.
 
-**Volatile state goes on #201** — which seats are running, which branches are
+**Volatile state goes on #3394** — which seats are running, which branches are
 unpushed, what a resumer does next. Free to post at any moment, and it survives
 an abort, which an unpushed in-tree edit does not.
 
diff --git a/.claude/workflows/web-fix-wave.js b/.claude/workflows/web-fix-wave.js
index d5300a99c..b98aef5d0 100644
--- a/.claude/workflows/web-fix-wave.js
+++ b/.claude/workflows/web-fix-wave.js
@@ -308,7 +308,7 @@ Read dev/governance/roles/fixer.md and dev/audit/README.md, then every issue's b
 ${g.brief}
 Follow every step of the fixer contract: a failing test first that imports the production symbol; the mutation proof with the failing check names pasted; the finding's own harness re-run before and after at your head SHA (copy a harness into the tree under test before running it -- the harnesses disagree about how they find the repository root); a null control on any cost, gain or time claim; both ends of the range for a learner or guard change. ${GATE}
 ${g.fixture ? 'This group moves fixtures. Claim each one with its expected direction in the right claim file, and never claim a fixture that is already may-drift -- env_drift refuses a name that is both. Run env_drift.py --fixtures before and after.' : 'This group must move no fixture: env_drift.py --all against the merge base reports no unclaimed drift, and both claim files stay byte-identical to origin/main.'}
-Never touch VERSION, the manifest version or the RELEASE_NOTES.md heading. Open the pull request with a body that carries Closes #N for each issue, Part of #201, the head SHA you measured, and every executed number; then wait for CI (fast, closures, browser) with actions_list and fix red until it is green.
+Never touch VERSION, the manifest version or the RELEASE_NOTES.md heading. Open the pull request with a body that carries Closes #N for each issue, Part of #3394, the head SHA you measured, and every executed number; then wait for CI (fast, closures, browser) with actions_list and fix red until it is green.
 ${repair ? `A reviewer BLOCKED your previous head. Their comment: ${repair}\nRepair in the same worktree, re-execute fixer steps 2-8 (the evidence described the old tree, and the body is evidence too), push, and return the new head SHA.` : ''}
 Return {pr, head_sha, summary} where pr is the PR NUMBER as an integer. If you could not open a PR -- you ran out of budget, the gate never went green, anything -- return pr: null with the reason in summary, and post the contractual "state at stop:" comment on every issue first. NEVER put prose in the pr field: a sentence there satisfies the schema, is read as a PR number, and sends a reviewer to a PR that does not exist.`
 
diff --git a/.claude/workflows/web-stamp.js b/.claude/workflows/web-stamp.js
index f17641723..7d022da81 100644
--- a/.claude/workflows/web-stamp.js
+++ b/.claude/workflows/web-stamp.js
@@ -1,9 +1,9 @@
-// One stamp per wave, then the wave's record on #201 and in the two
+// One stamp per wave, then the wave's record on #3394 and in the two
 // planning documents. See .claude/workflows/web-fragments.md for the shared
 // prompt block below, which is hand-copied into every web-*.js.
 export const meta = {
   name: 'web-stamp',
-  description: 'Stamp main once for everything merged since the last tag, then record the wave on #201 and in the plan of record',
+  description: 'Stamp main once for everything merged since the last tag, then record the wave on #3394 and in the plan of record',
   phases: [{ title: 'Stamp' }, { title: 'Record' }],
 }
 const GH_READ = `No gh CLI exists in this environment. For every GitHub read run
@@ -168,7 +168,7 @@ phase('Record')
 const record = await agent(`Record wave ${wave} of the open-issues program. ${GH_READ} ${GH_WRITE} ${WT('claude-web/record-wave-' + wave, 'origin/main')}
 These groups merged: ${JSON.stringify(merged)}. The release is ${stamp?.version ? 'v' + stamp.version : 'not stamped yet'}.
 Update the Delivery-status record: each wave row in dev/programme/plan-2026-09-open-issues.md's frozen table gets its release and a status; a merged pull request no row records gets its own file dev/programme/delivery/<N>.md, a line anchored \`- [#N](…/pull/N)\` and its state, never a new table row, which policy_lint refuses past the freeze. Update dev/programme/register/audit-2026-09.md: set each finding's status cell to "fixed (PR #N)" or "released (vX.Y.Z)" -- where a status cell and a body paragraph disagree, the cell is the truth, so change the cell. Open the pull request (docs are INERT, so the gate scopes to almost nothing; still run PYTHONPATH=tests/hastub python3 tests/entities.py, which checks that no tracked file is unclassified) and merge it once its checks are green.
-Then post one comment on issue #201: a table of group, issues, PR, verdict and release for this wave, and one paragraph on anything that surprised you -- a correction to a brief, a number that did not reproduce, a rule that bit. Return {pr, comment_url}.`,
+Then post one comment on issue #3394: a table of group, issues, PR, verdict and release for this wave, and one paragraph on anything that surprised you -- a correction to a brief, a number that did not reproduce, a rule that bit. Return {pr, comment_url}.`,
   { model: 'sonnet', effort: 'medium', label: 'record', phase: 'Record', schema: { type: 'object', required: ['pr'] } })
 
 return { stamp, record }
diff --git a/.cursor/rules/delivery-status-tracking.mdc b/.cursor/rules/delivery-status-tracking.mdc
index e31cb4c5e..206dc1c0a 100644
--- a/.cursor/rules/delivery-status-tracking.mdc
+++ b/.cursor/rules/delivery-status-tracking.mdc
@@ -1,5 +1,5 @@
 ---
-description: Keep programme Delivery-status and #201 current after each merge
+description: Keep programme Delivery-status and #3394 current after each merge
 globs: dev/programme/plan*.md,.claude/workflows/*-groups.json,dev/programme/HANDOVER.md,dev/programme/delivery/**
 alwaysApply: true
 ---
@@ -9,7 +9,7 @@ After each programme merge — wave group, tooling the plan tracks, or a closed
 
 1. **The Delivery-status record** — the plan's frozen table plus one `dev/programme/delivery/<N>.md` per PR; authoritative vs wave body; if they disagree, fix it first.
 2. **`.claude/workflows/wave-*-groups.json` `resume` fields** — match measured `origin/main` (merged PR SHAs, open PR heads).
-3. **GitHub issue #201** — before each PR, merge or release, coordinate here; not a heartbeat.
+3. **Issue #3394** — before each PR, merge or release, coordinate here; not a heartbeat.
 4. **Every PR the programme has opened**, not only the ones a roster predicted. Hotfixes, instrument repairs, harness lanes, policy, and anything found *in passing* have no wave: give each **its own row and section**, never a wave it does not belong to.
 5. **Every open issue**, with a disposition: **scheduled** into a wave or group, **deferred** with a reason, or **refused** with a reason. **"Not mentioned" is not a disposition**: an issue absent from the plan is unscheduled work. At each record, grep the plan for every open issue's number.
 
diff --git a/.cursor/rules/writing-for-agents.mdc b/.cursor/rules/writing-for-agents.mdc
index c79b31846..7b71f17db 100644
--- a/.cursor/rules/writing-for-agents.mdc
+++ b/.cursor/rules/writing-for-agents.mdc
@@ -46,7 +46,7 @@ it records**, riding the per-merge record obligation in
 `updated-for:` line names that merge. It links to the Delivery-status table
 rather than restating it.
 
-**Volatile state goes on #201** — which seats are running, which branches are
+**Volatile state goes on #3394** — which seats are running, which branches are
 unpushed, what a resumer does next. Free to post at any moment, and it survives
 an abort, which an unpushed in-tree edit does not.
 
diff --git a/.github/workflows/budget-raise-gate.yml b/.github/workflows/budget-raise-gate.yml
index 76366b48a..a4d0544ec 100644
--- a/.github/workflows/budget-raise-gate.yml
+++ b/.github/workflows/budget-raise-gate.yml
@@ -43,7 +43,7 @@ on:
 
 # Workflow-level and read-only, and the caller grants no more: the reviews list
 # needs `pull-requests: read`, the checkout `contents: read`, and the owner's
-# recorded mandate, a comment on #201, `issues: read`. No job widens it.
+# recorded mandate, a comment on a record issue, `issues: read`. No job widens it.
 permissions:
   contents: read
   pull-requests: read
diff --git a/.github/workflows/governance.yml b/.github/workflows/governance.yml
index cb6507cad..6b706ea4c 100644
--- a/.github/workflows/governance.yml
+++ b/.github/workflows/governance.yml
@@ -854,7 +854,7 @@ jobs:
           python3 -I tools/audit/seat/ledger.py --self-test | tee "$RUNNER_TEMP/ledger-self-test.txt"
           grep -Eq '^ledger self-test: [1-9][0-9]* checks, 0 failed$' "$RUNNER_TEMP/ledger-self-test.txt"
 
-      # The after-merge bookkeeping (R10-FLY-TRAIN-DEFAULTS part 2): the #201 line from
+      # The after-merge bookkeeping (R10-FLY-TRAIN-DEFAULTS part 2): the record-issue line from
       # its template and the four steps merge_pr.sh and the train run after a merge.
       - name: Show the post-merge record line refusing its own fixtures
         id: post-merge-record-line
diff --git a/.github/workflows/nightly.yml b/.github/workflows/nightly.yml
index bdb6c83c3..2f6393adf 100644
--- a/.github/workflows/nightly.yml
+++ b/.github/workflows/nightly.yml
@@ -576,7 +576,7 @@ jobs:
   # Delivery-status table and the handover are a seat's dispositions, never
   # this job's), commits under the `ci:` subject the loop guard keys on, pushes
   # the record branch, and opens or updates the record pull request as the
-  # hpo-author App with a generated body, then posts its #201 coordination
+  # hpo-author App with a generated body, then posts its record-issue coordination
   # comment. The pull request number exists only after that open or lookup.
   # The same write set then gains dev/programme/delivery/<that number>.md. The line
   # anchors the number and carries no merge SHA: the SHA does not exist until
@@ -623,7 +623,7 @@ jobs:
     timeout-minutes: 10
     # No permissions block, deliberately, so the workflow's read-only floor is
     # what GITHUB_TOKEN holds: the enumeration reads public-repo pull-request
-    # data, and every write -- branch push, pull request, #201 comment --
+    # data, and every write -- branch push, pull request, record-issue comment --
     # rides the App installation token minted below, never GITHUB_TOKEN. The
     # four-jobs floor pin in tests/entities.py stays at four, where a fifth
     # override has to be argued for rather than land.
@@ -684,7 +684,7 @@ jobs:
           gh api rate_limit --jq '"RATE_LIMIT enumerate after: \(.resources.core)"' || true
 
       # Two installation tokens from one minting routine. The author App's
-      # writes the rows, the pull request and the #201 comment, and merges
+      # writes the rows, the pull request and the record-issue comment, and merges
       # its own pull request, so the merge is the App's and its push to main
       # fires main's workflows (a GITHUB_TOKEN merge would not).
       # The approver App's, minted only when HPO_APPROVER_PEM/APPID are set in
@@ -982,15 +982,18 @@ jobs:
           write_payload "$(git rev-parse HEAD)"
           curl_json "record-pr update" PATCH \
             "$RUNNER_TEMP/payload.json" "$API/repos/$REPO/pulls/$NUM"
-          # The beat's #201 coordination comment, naming the pull request it
-          # opened (delivery-status-tracking item 3); one per beat.
+          # The beat's coordination comment on the record issue (#201 until
+          # its 2,500-comment cap; budget_raise_gate.RECORD_ISSUE, the one
+          # definition, since), naming the pull request it opened
+          # (delivery-status-tracking item 3); one per beat.
+          RECORD_ISSUE=$(python3 -I -c 'import sys; sys.path.insert(0, "tools/policy"); from budget_raise_gate import RECORD_ISSUE; print(RECORD_ISSUE)')
           python3 -I tools/audit/seat/record_row.py \
             --print-comment --plan-file "$RUNNER_TEMP/plan.json" --pr "$NUM" \
             > "$RUNNER_TEMP/comment.md"
           python3 -I -c 'import json,os; print(json.dumps({"body": open(os.environ["RUNNER_TEMP"]+"/comment.md").read()}))' \
             > "$RUNNER_TEMP/comment.json"
           curl_json "record-pr comment" POST \
-            "$RUNNER_TEMP/comment.json" "$API/repos/$REPO/issues/201/comments"
+            "$RUNNER_TEMP/comment.json" "$API/repos/$REPO/issues/$RECORD_ISSUE/comments"
           echo "pr=$NUM" >> "$GITHUB_OUTPUT"
 
       # THE MERGE IS A PREDICATE (tvofi, 2026-10-07). A record pull request
diff --git a/CLAUDE.md b/CLAUDE.md
index 060c9542b..adcae52b2 100644
--- a/CLAUDE.md
+++ b/CLAUDE.md
@@ -88,11 +88,11 @@ binds the seat to this file.
 | `claim-files.md` | the `claimnotes` merge driver and its refusal; a branch that claims nothing leaves both claim files byte-identical; a `DIRTY` pull request does not go red, it cannot run |
 | `comment-readback.md` | post an issue or pull-request comment by running `gh_comment.py`, and read back what landed — a read-back leaves an artifact another seat reads, which a warning about the flag does not |
 | `defect-root-cause.md` | a defect that reached a release, or turned a PR red on a check a cheaper detector could have run, owes a cause, a process state and a countermeasure or a recorded refusal |
-| `delivery-status-tracking.md` | a PR's row as `dev/programme/delivery/<N>.md`, roster `resume`, and one #201 comment per state change — at each merge, not at session end; the record outranks any wave body |
+| `delivery-status-tracking.md` | a PR's row as `dev/programme/delivery/<N>.md`, roster `resume`, and one #3394 comment per state change — at each merge, not at session end; the record outranks any wave body |
 | `finding-propagation.md` | a finding that changes how a later stage must work goes into that stage's own brief before the producing pull request merges — a PR comment records it, it does not propagate it |
 | `gate-scoping.md` | how to run the scoped gate, the `gate_lock.py` lease, and never a full `derive_closures.sh` off Linux — that path replaced the Linux recordings and cost one lane most of its closure |
 | `ratchet-budgets.md` | three one-sided caps, because the floor prices a session that opens nothing and a split lowers it without deleting a line; re-record it only alongside a flat corpus and flat role caps |
-| `writing-for-agents.md` | what a sentence in the development record must carry to stay; `README.md` and the rest of `docs/` are outside it; and the one living handover, durable in the tree against volatile on #201 |
+| `writing-for-agents.md` | what a sentence in the development record must carry to stay; `README.md` and the rest of `docs/` are outside it; and the one living handover, durable in the tree against volatile on #3394 |
 
 ### Loaded when a pull-request event arrives
 
diff --git a/dev/audit/harnesses/r10_mandate_guard_instances.py b/dev/audit/harnesses/r10_mandate_guard_instances.py
index 503da9e68..0646ca221 100644
--- a/dev/audit/harnesses/r10_mandate_guard_instances.py
+++ b/dev/audit/harnesses/r10_mandate_guard_instances.py
@@ -65,7 +65,7 @@ def main(argv):
         with open(f, "w", encoding="utf-8") as fh:
             fh.write(t)
         r = subprocess.run([sys.executable, "tools/pr/gh_comment.py", "post", "--repo", g.DEFAULT_REPO,
-                            "--issue", str(g.MANDATE_ISSUE), "--body-file", f, "--dry-run"],
+                            "--issue", str(g.RECORD_ISSUE), "--body-file", f, "--dry-run"],
                            capture_output=True, text=True)
         last = (r.stdout + r.stderr).strip().splitlines()[-1]
         print(f"RESULT body={label} rc={r.returncode} last={last[:40]!r}")
diff --git a/dev/audit/harnesses/r10_plan_issues_chart_mutants.py b/dev/audit/harnesses/r10_plan_issues_chart_mutants.py
index 4615460bb..58c72716a 100644
--- a/dev/audit/harnesses/r10_plan_issues_chart_mutants.py
+++ b/dev/audit/harnesses/r10_plan_issues_chart_mutants.py
@@ -35,10 +35,10 @@ MUTANTS = [
     ("unplanned-dropped", "                unplanned.add(n)", "                pass"),
     ("unplanned-also-closes", "        close_at.pop(n, None)", "        pass"),
     ("other-uncounted", "\"other\": open_now - set(close_at) - unplanned}", "\"other\": set()}"),
-    ("orphans-dropped", "                      if n != TRACKING_ISSUE}", "                      if False}"),
+    ("orphans-dropped", "                      if n not in TRACKING_ISSUES}", "                      if False}"),
     ("orphans-wired-groups", "    out[\"orphans\"] = {n: sorted(wired.get(n, [])) for n in sorted(out[\"other\"])",
      "    out[\"orphans\"] = {n: [] for n in sorted(out[\"other\"])"),
-    ("tracking-orphan", "                      if n != TRACKING_ISSUE}", "                      }"),
+    ("tracking-orphan", "                      if n not in TRACKING_ISSUES}", "                      }"),
     ("orphans-not-listed", "            f'  <ul class=\"orphans\">{orphans}</ul>\\n' if orphans else \"\")",
      "            f'' if orphans else \"\")"),
     ("offline-not-omitted", "    if snap.get(\"offline\"):", "    if False:"),
diff --git a/dev/audit/harnesses/r10_plan_page_mutants.py b/dev/audit/harnesses/r10_plan_page_mutants.py
index eb15cf345..7d633449a 100644
--- a/dev/audit/harnesses/r10_plan_page_mutants.py
+++ b/dev/audit/harnesses/r10_plan_page_mutants.py
@@ -64,7 +64,7 @@ MUTANTS = [
      "return named.pop() if len(named) == 1 else None", "return None"),
     ("closed-strike", PAGE, "(\"\" if is_open else \" closed\")", "\"\""),
     ("tracking-excluded", PAGE,
-     "if i[\"state\"] == \"OPEN\" and i[\"number\"] != TRACKING_ISSUE)",
+     "if i[\"state\"] == \"OPEN\" and i[\"number\"] not in TRACKING_ISSUES)",
      "if i[\"state\"] == \"OPEN\")"),
     ("page-refuses-stale", PAGE, "    if stale:\n        bad.append", "    if False:\n        bad.append"),
     ("freshness-rule", PLAN, "if have != want:", "if False:"),
diff --git a/dev/governance/roles/nudge.md b/dev/governance/roles/nudge.md
index 73198fb27..b7c6b8c30 100644
--- a/dev/governance/roles/nudge.md
+++ b/dev/governance/roles/nudge.md
@@ -10,13 +10,13 @@ This programme keeps seat worktrees under `~/hpo-seats`. A reader on another mac
 
 ## Who writes, and what stays shut
 
-You dispatch fixers, reviewers, and root-cause seats. You post verdicts, approve, merge, stamp, and update the roster, the state docs, and issue #201. Do not hand the orchestrator role to a seat.
+You dispatch fixers, reviewers, and root-cause seats. You post verdicts, approve, merge, stamp, and update the roster, the state docs, and issue #3394 (#201's continuation). Do not hand the orchestrator role to a seat.
 
 Opus seats that die are replaced by a new Task on grok-4.7-high. Do not resume a dead Opus agent. Sonnet seats use cursor-grok-4.6-high. Haiku seats use composer-2.5.
 
 Pull requests are authored by the hpo-author App through `tools/pr/app_push.sh`. The login that reads GitHub is tvofi. The hpo-approver App posts verdicts. A code-owned path needs a tvofi review citing the session mandate. `tools/pr/app_approve.sh` refuses those paths. A merge verdict on a path that is not code-owned is approved with that script. A record pull request that only touches `dev/programme/delivery` is not code-owned. The ruleset still requires one approving review, so that record pull request is approved as tvofi and then merged.
 
-Do not push `main` with the deploy key. Do not merge with the admin flag. Do not edit `VERSION`, the manifest version, or the `RELEASE_NOTES.md` heading except through `tools/release/stamp.py`. A merge message must not close #201. Write `Leaves #201 open`. Never the negated form. Do not run a full `tests/derive_closures.sh` off Darwin. Use that script's single-script mode. Touch a claim file only when the branch is claiming drift. Compare a branch with three dots, never two. Run the train under `python3 -u` so its log is not block-buffered.
+Do not push `main` with the deploy key. Do not merge with the admin flag. Do not edit `VERSION`, the manifest version, or the `RELEASE_NOTES.md` heading except through `tools/release/stamp.py`. A merge message must not close #3394. Write `Leaves #3394 open`. Never the negated form. Do not run a full `tests/derive_closures.sh` off Darwin. Use that script's single-script mode. Touch a claim file only when the branch is claiming drift. Compare a branch with three dots, never two. Run the train under `python3 -u` so its log is not block-buffered.
 
 A timer subscription dedupes by name and answers created false without replacing the prompt. Unsubscribe first, then subscribe. Do not call the two together.
 
diff --git a/dev/governance/roles/orchestrator.md b/dev/governance/roles/orchestrator.md
index 4d0d219e2..4a2fed942 100644
--- a/dev/governance/roles/orchestrator.md
+++ b/dev/governance/roles/orchestrator.md
@@ -212,7 +212,7 @@ Failure shapes already produced, all yours:
 `finding-propagation.mdc` binds the producing pull request. It binds you
 additionally, because you write the rosters and you decide the merge order.
 
-- **A comment is not propagation** — including yours on #201.
+- **A comment is not propagation** — including yours on #3394.
 - **The destination must exist**, and creating it is part of the carry.
 - **Land the roster on main only when the tree needs it** (tvofi, 2026-10-18):
   a carry a PR names, a `Closes` needing a `fixes` edit (`pr-contract` reads
diff --git a/dev/governance/rules/delivery-status-tracking.md b/dev/governance/rules/delivery-status-tracking.md
index 1ee41b30d..89a15fd2a 100644
--- a/dev/governance/rules/delivery-status-tracking.md
+++ b/dev/governance/rules/delivery-status-tracking.md
@@ -1,5 +1,5 @@
 ---
-description: Keep programme Delivery-status and #201 current after each merge
+description: Keep programme Delivery-status and #3394 current after each merge
 paths:
   - "dev/programme/plan*.md"
   - ".claude/workflows/*-groups.json"
@@ -12,7 +12,7 @@ After each programme merge — wave group, tooling the plan tracks, or a closed
 
 1. **The Delivery-status record** — the plan's frozen table plus one `dev/programme/delivery/<N>.md` per PR; authoritative vs wave body; if they disagree, fix it first.
 2. **`.claude/workflows/wave-*-groups.json` `resume` fields** — match measured `origin/main` (merged PR SHAs, open PR heads).
-3. **GitHub issue #201** — before each PR, merge or release, coordinate here; not a heartbeat.
+3. **Issue #3394** — before each PR, merge or release, coordinate here; not a heartbeat.
 4. **Every PR the programme has opened**, not only the ones a roster predicted. Hotfixes, instrument repairs, harness lanes, policy, and anything found *in passing* have no wave: give each **its own row and section**, never a wave it does not belong to.
 5. **Every open issue**, with a disposition: **scheduled** into a wave or group, **deferred** with a reason, or **refused** with a reason. **"Not mentioned" is not a disposition**: an issue absent from the plan is unscheduled work. At each record, grep the plan for every open issue's number.
 
diff --git a/dev/governance/rules/writing-for-agents.md b/dev/governance/rules/writing-for-agents.md
index cac684651..5bdaba192 100644
--- a/dev/governance/rules/writing-for-agents.md
+++ b/dev/governance/rules/writing-for-agents.md
@@ -50,7 +50,7 @@ it records**, riding the per-merge record obligation in
 `updated-for:` line names that merge. It links to the Delivery-status table
 rather than restating it.
 
-**Volatile state goes on #201** — which seats are running, which branches are
+**Volatile state goes on #3394** — which seats are running, which branches are
 unpushed, what a resumer does next. Free to post at any moment, and it survives
 an abort, which an unpushed in-tree edit does not.
 
diff --git a/dev/programme/HANDOVER.md b/dev/programme/HANDOVER.md
index 2838ab276..f4c16d1f9 100644
--- a/dev/programme/HANDOVER.md
+++ b/dev/programme/HANDOVER.md
@@ -7,7 +7,8 @@ into `.claude/rules/`, which the harness loads on this path). It holds what a
 session starting now must know and cannot derive from the tree in one command.
 Delivery status is the frozen table in `dev/programme/plan-2026-09-open-issues.md`
 plus one `dev/programme/delivery/<N>.md` per pull request, linked from here and
-never restated. **Volatile state is on #201 and nowhere here**: running seats,
+never restated. **Volatile state is on #3394 (#201's continuation past its
+2,500-comment cap) and nowhere here**: running seats,
 open pull requests and heads, the train queue, today's next action, the open-PR
 cap currently in force, and the mandate's id and dates. Chronology this file no
 longer carries is read at its last pre-round-10 form,
@@ -99,7 +100,7 @@ line (`git log --first-parent --format='%h %s' v7.0.0..origin/main | grep ' v7\.
   fixers go to the cloud too.** A cloud seat silent past about 2.5 hours with
   no ref pushed is re-run locally after an `ls-remote` guard against a late
   push. Fixers run at medium effort; a mechanical turn takes sonnet or haiku.
-- **The open-PR cap** is the owner's, restated on #201 each time it moves, and
+- **The open-PR cap** is the owner's, restated on #3394 each time it moves, and
   it is a count of open pull requests that gates only starting a new roster
   group. `pr_cap.py dispatch-gate` counts in-progress roster groups against
   `HPO_WIP_CAP` instead, which is not the owner's rule: never quote its `WIP
@@ -119,7 +120,7 @@ tick driver (`tick_loop.sh`, `orchestrator_tick.py`), the verdict path
 `body_push.sh`, `body_patch.sh`), the merge path (`train.sh`, `merge_train.py`,
 `tools/pr/app_approve.sh`), the roster (`roster_edit.py`, `roster_sync.py`,
 `state_docs.py`), the sweep (`sweep_render.py`, `sweep_template.md`), and
-`tools/audit/worktree_gc.sh` after each merge. Comments on #201 and on pull
+`tools/audit/worktree_gc.sh` after each merge. Comments on #3394 and on pull
 requests are posted with `tools/pr/gh_comment.py` and read back
 (`comment-readback.md`).
 
@@ -148,7 +149,7 @@ requests are posted with `tools/pr/gh_comment.py` and read back
 
 The authority to approve as the owner is a record, read from the API at the
 moment of use and trusted nowhere in the tree: the newest comment by `tvofi`
-on #201 whose first line is `MANDATE: agents may approve as tvofi, scope
+on #201 or #3394 whose first line is `MANDATE: agents may approve as tvofi, scope
 <code-owned|budget-raise|all>, from <ISO> until <ISO>`. Its id, scope and
 dates are on #201 and in the sweep prompt; decision 0013 and its 2026-10-02
 and 2026-10-14 amendments are the rule. After `until`, decision 0007's
@@ -168,7 +169,7 @@ per-pull-request owner review is the rule again.
   seat's classifier denial of it is not laundered through the mandate, the seat
   is re-briefed or the work runs where the action is allowed.
 - **The kill switch is deliberately loose.** `budget_raise_gate.py` voids a
-  mandate on any later comment by the owner's account on #201 that contains the
+  mandate on any later comment by the owner's account on #201 or #3394 that contains the
   stem of the verb "to revoke", in any case, on any line, beside that
   mandate's id. **An identifier counts**: a roster group whose name contains
   that stem voided it a second time (2026-10-31) and refused a pull request's
@@ -215,7 +216,7 @@ per-pull-request owner review is the rule again.
    no negated closing keyword, never a custom `--subject`, `preflight.sh` as a
    filter with the intended issues as arguments, then read which issues the
    merge actually closed.
-5. **After each merge**: `state_docs.py --push`, the merge's #201 comment, the
+5. **After each merge**: `state_docs.py --push`, the merge's #3394 comment, the
    delivery row (the beat writes it; a frozen PR's own row costs a record pull
    request), the roster `set-stage` through the roster seat, and
    `tools/audit/worktree_gc.sh`. This file is updated in the same record pull
@@ -228,7 +229,7 @@ per-pull-request owner review is the rule again.
 7. **Stamp.** The orchestrator stamps, `stamp.py --push --push-key
    ~/.zcode/stamp-deploy.key --known-hosts <file>`, never by hand and never in
    a branch. It refuses a `main` whose `ci.yml` push run's `gate` is not green
-   (`--allow-red` takes the cause in the release notes and on #201), a window
+   (`--allow-red` takes the cause in the release notes and on #3394), a window
    with a merged PR lacking its row (`--allow-rowless` likewise), and notes
    omitting a merged PR. The deploy key's SSH on port 22 can time out from the
    stamping host: route `github.com` to `ssh.github.com:443` and verify the host
@@ -432,7 +433,7 @@ graduation owes a mutation proof in its own pull request.
   handoff and only the orchestrator moves the head; a head moved under a live
   review costs it (`orchestrator.md` section 7). A record pull request cannot
   converge while the merge queue runs (#531 stayed open 20 hours over 31
-  merges), so one record per merge, and live state on #201.
+  merges), so one record per merge, and live state on #3394.
 - **`prepr.sh` gates `## Head` against the LOCAL head and `pr-contract` gates
   the REMOTE tip**, so a pull request that writes its own record file pushes
   twice and one `pr-contract` run necessarily fails on the commit being
diff --git a/dev/programme/delivery/3412.md b/dev/programme/delivery/3412.md
new file mode 100644
index 000000000..13b7c398e
--- /dev/null
+++ b/dev/programme/delivery/3412.md
@@ -0,0 +1 @@
+- [#3412](https://github.com/tvofi/heatpump_optimizer/pull/3412) — **open**, R10-HOTFIX-RECORD-ISSUE-CONTINUATION: post #201 records to a continuation issue (R10-HOTFIX-RECORD-ISSUE-CONTINUATION)
diff --git a/tests/entities.py b/tests/entities.py
index 7e52c5066..fdddf6254 100644
--- a/tests/entities.py
+++ b/tests/entities.py
@@ -16966,7 +16966,7 @@ R.check(
     "exactly one handover, with no date in its name",
     _handovers == ["dev/programme/HANDOVER.md"],
     f"found {_handovers or 'none'}; durable state belongs in the single "
-    "dev/programme/HANDOVER.md and volatile state on #201, never in both",
+    "dev/programme/HANDOVER.md and volatile state on #3394, never in both",
 )
 # `updated-for:` is the staleness half: a handover nobody has re-pointed since
 # the merge it describes is the failure mode, not one that has been deleted.
@@ -29812,7 +29812,9 @@ def _raf_job_ok(job: str) -> bool:
         and job.find("--write-self-row") > job.find("NUM=$(")
         and "docs/HANDOVER.md" not in job
         and "for try in 1 2 3" in job
-        and "issues/201/comments" in job
+        and "from budget_raise_gate import RECORD_ISSUE" in job
+        and "issues/$RECORD_ISSUE/comments" in job
+        and "issues/201/comments" not in job
         and "if: always()" in job
         and pushes
         and all(_RAF_LEASE in p for p in pushes)
@@ -32037,7 +32039,7 @@ def _brg_defects(text: str) -> "list[str]":
     if not all(re.search(r"python3 -I \.claude/workflows/budget_raise_gate\.py", runs[i])
                for i in gate):
         out.append("gate not under python3 -I")
-    # `issues: read`: the owner's recorded mandate is a comment on #201.
+    # `issues: read`: the owner's recorded mandate is a comment on a record issue.
     if doc.get("permissions") != {"contents": "read", "pull-requests": "read", "issues": "read"} or any(
             "permissions" in (j or {}) for j in jobs.values()):
         out.append(f"permissions {doc.get('permissions')}")
diff --git a/tools/audit/carry_audit.py b/tools/audit/carry_audit.py
index 1327c3219..97566825e 100644
--- a/tools/audit/carry_audit.py
+++ b/tools/audit/carry_audit.py
@@ -79,7 +79,7 @@ with no `Carry:` (the ledger's work-queue OWED lines are tasks, not read).
 routing check over the roster alone: every pending carry on a done or
 absorbed group (STRANDED, by `roster_lib.pending_carries`; a carry a closed
 group held at `roster_lib.CARRY_CUTOVER` is legacy and exempt) and, given
-`--open-issues FILE`, every open issue but #201 that no live group lists
+`--open-issues FILE`, every open issue but the record issues that no live group lists
 (ISSUE-STRANDED when only closed groups do, ISSUE-UNLISTED when none does);
 `CARRY-ROSTER:` is its summary line. EXIT 0 when every finding item
 is routed to a valid destination; `CARRY-AUDIT:` is the summary line;
@@ -845,8 +845,18 @@ def ledger_unrouted(text: str) -> list[str]:
 
 
 # --------------------------------------------------------------- the roster
-#: The one issue every seat writes to and no group owns (the round's log).
-LOG_ISSUE = 201
+def log_issues() -> frozenset[int]:
+    """The issues every seat writes to and no group owns (the round's log):
+    #201, and its continuation past GitHub's 2,500-comment cap --
+    `budget_raise_gate.RECORD_ISSUES`, the one record-issue definition.
+    Imported on call, because only the roster arm reads it: `check --body`
+    runs where the gate is not this tree's -- pr-contract restores the base's
+    copy of budget_raise_gate.py, and prepr's carry_line fixture copies this
+    file with roster_lib.py alone -- so a module-level import refused every
+    body there with an ImportError, whatever it carried."""
+    sys.path.insert(0, str(ROOT / "tools/policy"))
+    from budget_raise_gate import RECORD_ISSUES
+    return frozenset(RECORD_ISSUES)
 
 
 def open_issue_numbers(text: str) -> set[int]:
@@ -867,7 +877,7 @@ def roster_report(roster: dict, legacy: dict, open_issues: set[int] | None) -> l
     (`roster_lib.pending_carries`, the predicate set-stage and roster_sync
     close a group by) on a group in `roster_lib.CARRY_CLOSED`. With an issue
     list: ISSUE-STRANDED, an open issue only closed groups list; ISSUE-UNLISTED,
-    one no group lists. #201 is the log and is never reported. Without a list
+    one no group lists. A record issue (`log_issues`) is the log and is never reported. Without a list
     the issue arm says nothing: absence is not a measurement."""
     out = []
     for gid, stage, i, text in roster_lib.stranded(roster, legacy):
@@ -881,7 +891,7 @@ def roster_report(roster: dict, legacy: dict, open_issues: set[int] | None) -> l
         live = (g.get("resume") or {}).get("stage") not in roster_lib.CARRY_CLOSED
         for n in set(g.get("issues") or []) | set(g.get("fixes") or []):
             listing.setdefault(n, []).append((gid, live))
-    for n in sorted(open_issues - {LOG_ISSUE}):
+    for n in sorted(open_issues - log_issues()):
         by = listing.get(n, [])
         if not by:
             out.append(f"ISSUE-UNLISTED #{n}")
@@ -1989,7 +1999,7 @@ def _self_test() -> int:
         {"group": "S-LIVE", "issues": [2429], "fixes": [2500], "resume": {"stage": "carries-open"},
          "carry": ["live owed"]},
     ]}
-    lines = roster_report(rr, {"S-DONE": frozenset({"legacy owed"})}, {201, 2429, 2500, 2733, 2855, 2875})
+    lines = roster_report(rr, {"S-DONE": frozenset({"legacy owed"})}, {201, 2429, 2500, 2733, 2855, 2875, *log_issues()})
     stranded_l = [ln for ln in lines if ln.startswith("STRANDED")]
     check("roster: a pending post-cut-over carry on a done group is STRANDED, with its index",
           any(ln.startswith("STRANDED S-DONE (done) carry[1]") for ln in stranded_l))
@@ -2001,8 +2011,9 @@ def _self_test() -> int:
           "ISSUE-STRANDED #2733 listed only by closed group(s): S-DONE" in lines
           and "ISSUE-STRANDED #2855 listed only by closed group(s): S-PAID" in lines)
     check("roster: an open issue no group lists is reported", "ISSUE-UNLISTED #2875" in lines)
-    check("roster (null): an issue a live group lists, in issues or fixes, and #201 are not reported",
-          not [ln for ln in lines if re.search(r"#(2429|2500|201)\b", ln)])
+    check("roster (null): an issue a live group lists, in issues or fixes, and the record issues are not reported",
+          not [ln for ln in lines if re.search(rf"#({'|'.join(map(str, (2429, 2500, *log_issues())))})\b", ln)]
+          and 201 in log_issues() and len(log_issues()) > 1)
     check("roster: with no issue list the issue arm reports nothing, never a guess",
           not [ln for ln in roster_report(rr, {}, None) if ln.startswith("ISSUE")])
     check("roster: open_issues reads gh's JSON, numbers or objects, and drops pull requests",
diff --git a/tools/audit/seat/INSTRUMENTS.md b/tools/audit/seat/INSTRUMENTS.md
index 27a9a7e79..7dfd2705c 100644
--- a/tools/audit/seat/INSTRUMENTS.md
+++ b/tools/audit/seat/INSTRUMENTS.md
@@ -116,8 +116,8 @@ sweep's standing-seat liveness step keep them alive.
 - [`plan_public.py`](instruments/plan_public.py.md) — stages the ongoing round's plan page from the newest state ref for the public site, refusing a page that would publish a host path or a tool's attribution
 - [`bottleneck_check.py`](instruments/bottleneck_check.py.md) — prints one `BOTTLENECK:` line per flow metric past the owner's threshold, with a suggested action the orchestrator decides on, and nothing when none is
 - [`outside_intake.py`](instruments/outside_intake.py.md) — lists submissions by outside users since a cursor with what each is owed (triage, answer, reply), and answers or refuses one, marked so none is answered twice
-- [`postmerge.py`](instruments/postmerge.py.md) — after a merge: the #201 line, the roster stage, the state docs and main's suite state; a failed step is printed OWED and opens the ledger's `postmerge-owed`
-- [`record_beat.py`](instruments/record_beat.py.md) — one merged pull request's #201 record line from a fixed template, the full merge sha, read back byte-identical
+- [`postmerge.py`](instruments/postmerge.py.md) — after a merge: the record-issue line, the roster stage, the state docs and main's suite state; a failed step is printed OWED and opens the ledger's `postmerge-owed`
+- [`record_beat.py`](instruments/record_beat.py.md) — one merged pull request's record-issue line from a fixed template, the full merge sha, read back byte-identical
 - [`sweep_driver.py`](instruments/sweep_driver.py.md) — the probe PR's sweep, where `workflow_run` never fires (`gate-sweep.yml` runs only from the default branch)
 - [`sweep_render.py`](instruments/sweep_render.py.md) — renders the orchestrator sweep from `sweep_template.md` and a session's JSON overlay (stdout or `--out`)
 - [`sweep_template.md`](instruments/sweep_template.md.md) — the orchestrator's recurring sweep, steps in order
diff --git a/tools/audit/seat/gh_calls.py b/tools/audit/seat/gh_calls.py
index 13a9b2bbb..0f5ed462d 100644
--- a/tools/audit/seat/gh_calls.py
+++ b/tools/audit/seat/gh_calls.py
@@ -575,9 +575,21 @@ def self_test():
             ("gh extension exec", ["extension", "exec", "x"]))
         for label, args in refused:
             check(f"{label} is refused", run(args).returncode == 1)
-        mut = good.replace("tracker=201", "tracker=0")
+        mut = good.replace("trackers='201 ", "trackers='0 ")
         check("mutant: the guard's issue number changed lets the planted post through",
               mut != good and run(planted, shim_text=mut).returncode == 7)
+        # The record continues past #201's comment cap: the continuation is guarded alike.
+        rec = good.split("trackers='", 1)[1].split("'", 1)[0].split()[-1]
+        on_rec = ["api", "-X", "POST", f"repos/o/r/issues/{rec}/comments", "-f", f"body={kill_body}"]
+        check("planted: a raw `gh api` post to the continuation record issue is refused",
+              rec != "201" and run(on_rec).returncode == 1)
+        check("planted: a `gh issue comment` on the continuation record issue is refused",
+              run(["issue", "comment", rec, "-b", "x"]).returncode == 1)
+        check("null control: a `gh issue comment` on the issue after it reaches the real gh",
+              run(["issue", "comment", str(int(rec) + 1), "-b", "x"]).returncode == 7)
+        mut = good.replace(f" {rec}'\n", "'\n")
+        check("mutant: the continuation dropped from the trackers lets its planted post through",
+              mut != good and run(on_rec, shim_text=mut).returncode == 7)
         install(good)
 
         # mutants of each rule of the guard: each lets one refused spelling (or spoof) through
@@ -594,7 +606,7 @@ def self_test():
                      "*%*) ;; esac\n  while", ["issue", "comment", "%32%30%32", "-b", "x"], rc=1)
         guard_mutant("trailing slash kept on the target", 'while [ "${w%/}" != "$w" ]; do w=${w%/}; done', ":",
                      ["issue", "comment", "https://github.com/o/r/issues/202/", "-b", "x"], rc=1)
-        guard_mutant("an unreadable target passes", "t=$(num \"${pos[1]}\"); [ \"$t\" != '?' ] && [ \"$t\" != \"$tracker\" ]", 't=$(num "${pos[1]}"); [ "$t" != "$tracker" ]',
+        guard_mutant("an unreadable target passes", "t=$(num \"${pos[1]}\"); [ \"$t\" != '?' ] && ! has \"$trackers\" \"$t\"", 't=$(num "${pos[1]}"); ! has "$trackers" "$t"',
                      ["issue", "comment", "main", "-b", "x"])
         guard_mutant("dot segments kept", "      ''|.) ;;\n      ..) [", "      ''|.) ;;\n      zz) [", ["api", "repos/o/r/issues/202/../201/comments", "-f", "body=x"])
         guard_mutant("empty path segments kept", "      ''|.) ;;\n", "      .) ;;\n",
@@ -621,9 +633,10 @@ def self_test():
             spec = importlib.util.spec_from_file_location("budget_raise_gate", SHIM.parents[3] / "policy" / "budget_raise_gate.py")
             g = importlib.util.module_from_spec(spec)
             spec.loader.exec_module(g)
-            check("the shim's tracker number is budget_raise_gate.MANDATE_ISSUE", f"tracker={g.MANDATE_ISSUE}\n" in good)
+            check("the shim's trackers are budget_raise_gate.RECORD_ISSUES",
+                  f"trackers='{' '.join(map(str, g.RECORD_ISSUES))}'\n" in good)
         except (OSError, ImportError, AttributeError):
-            check("the shim's tracker number is budget_raise_gate.MANDATE_ISSUE (gate readable)", False)
+            check("the shim's trackers are budget_raise_gate.RECORD_ISSUES (gate readable)", False)
 
         # a shim is never its own real gh. The PATH is hermetic: no real gh on any host.
         (w / "real" / "gh").unlink()
diff --git a/tools/audit/seat/handover_prompt.py b/tools/audit/seat/handover_prompt.py
index 984caec3f..c2fe40f9c 100644
--- a/tools/audit/seat/handover_prompt.py
+++ b/tools/audit/seat/handover_prompt.py
@@ -37,6 +37,8 @@ from pathlib import Path
 
 sys.path.insert(0, str(Path(__file__).resolve().parent))
 import roster_lib  # noqa: E402
+sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "policy"))
+from budget_raise_gate import RECORD_ISSUE  # noqa: E402  the one record-issue definition
 
 SELF = "tools/audit/seat/handover_prompt.py"
 NOT_STARTED = "not-started"
@@ -114,8 +116,8 @@ def render(roster: dict, source: str, resume_path: str, resume_text: str,
               "them): " + (", ".join(ready) or "none.")]
     L += ["", "## Resume steps", "",
           "1. Read the resume doc's Roster and Ready next sections.",
-          "2. Claim one ready group and announce it on the tracking issue "
-          "#201 before opening work -- before each PR, merge and release, "
+          "2. Claim one ready group and announce it on the record issue "
+          f"#{RECORD_ISSUE} before opening work -- before each PR, merge and release, "
           "not only after a state change.",
           "3. Work at your own merge base; re-derive every figure you quote "
           "there. A figure from another seat's run is a claim, not a "
@@ -268,7 +270,7 @@ def _self_test() -> int:
           and "tvofi reviews" in text and "decision 0011" in text)
     check("done criteria", "resume.stage" in text and "dev/programme/delivery/" in text)
     check("resume steps", "Claim one ready group" in text
-          and "#201" in text)
+          and f"#{RECORD_ISSUE}" in text and "#201 " not in text)
     # Every repository path the prompt names is in the tree (#1990's RCA: a
     # move left the retired briefs directory here after its contracts went to
     # dev/governance/roles/). A templated `<N>` file is checked by its directory.
diff --git a/tools/audit/seat/instruments/merge_pr.sh.md b/tools/audit/seat/instruments/merge_pr.sh.md
index 50b06bd26..632fd21a2 100644
--- a/tools/audit/seat/instruments/merge_pr.sh.md
+++ b/tools/audit/seat/instruments/merge_pr.sh.md
@@ -2,7 +2,7 @@
 
 - `merge_pr.sh` — merges one PR after its evidence checks. When: a single
   verdicted PR; for more than one, `merge_train.py` below. Owner mode takes
-  `--mandate <comment-id>` and reads that #201 mandate live; `--ready` marks a
+  `--mandate <comment-id>` and reads that record-issue mandate live; `--ready` marks a
   draft ready. Refusal: a verdict or head mismatch stops the merge before the
   merge API call; a draft without `--ready`, or owner mode with no mandate in
   force, refuses before anything posts. Before its CI wait it runs
diff --git a/tools/audit/seat/instruments/orchestrator_tick.py.md b/tools/audit/seat/instruments/orchestrator_tick.py.md
index d87ab1cf0..72dcdd06b 100644
--- a/tools/audit/seat/instruments/orchestrator_tick.py.md
+++ b/tools/audit/seat/instruments/orchestrator_tick.py.md
@@ -72,7 +72,7 @@
   prints every pass for each complete handoff no PR head carries, read by
   `bus.sh orphans --min-age-h 0` (a pull request behind its own newer handoff
   included, #2411); a run with no summary line is UNCHECKED, never a clean
-  zero. STATE's missing-row check, the closes check and the #201
+  zero. STATE's missing-row check, the closes check and the record-issue
   unrecorded-merge check enumerate merges through
   `tests/delivery_status.py`'s `parse_log` and `collect`, so a `<title> (#N)`
   merge counts as a merge (#2413, #2412, #2407). `--only CARRY`
diff --git a/tools/audit/seat/instruments/postmerge.py.md b/tools/audit/seat/instruments/postmerge.py.md
index eee7a838c..8508a0eee 100644
--- a/tools/audit/seat/instruments/postmerge.py.md
+++ b/tools/audit/seat/instruments/postmerge.py.md
@@ -1,7 +1,7 @@
 # `postmerge.py`
 
 - `postmerge.py` — the bookkeeping after a merge, run by `merge_pr.sh` and
-  by the train's landing: the #201 line (`record_beat.py`), the roster stage
+  by the train's landing: the record-issue line (`record_beat.py`), the roster stage
   (`roster_sync.py --apply`; a refusal prints `set-stage owed <group> <merge sha>`),
   `state_docs.py --push`, and main's suite state (`merge_train.py classify --main`).
   When: automatically after each merge; by hand with `--retry` once an OWED
diff --git a/tools/audit/seat/instruments/record_beat.py.md b/tools/audit/seat/instruments/record_beat.py.md
index 40d072f0f..00886114a 100644
--- a/tools/audit/seat/instruments/record_beat.py.md
+++ b/tools/audit/seat/instruments/record_beat.py.md
@@ -1,8 +1,9 @@
 # `record_beat.py`
 
-- `record_beat.py` — posts one #201 line per merged pull request from a
+- `record_beat.py` — posts one record-issue line (`budget_raise_gate.RECORD_ISSUE`, #3394 since
+  #201's comment cap) per merged pull request from a
   fixed template (pull request, the full merge sha resolved from git, roster
-  group, issues the merge closed, "Leaves #201 open"), the body file under the
+  group, issues the merge closed, "Leaves #3394 open"), the body file under the
   state directory, through `tools/pr/gh_comment.py` with its byte-identical
   read-back. When: `postmerge.py` calls it; by hand for a merge the tick reads
   as unrecorded. Refusals: an unmerged pull request, a merge commit git cannot
diff --git a/tools/audit/seat/instruments/shims_seat-gh.md b/tools/audit/seat/instruments/shims_seat-gh.md
index c9e3bc44e..691b6a3bb 100644
--- a/tools/audit/seat/instruments/shims_seat-gh.md
+++ b/tools/audit/seat/instruments/shims_seat-gh.md
@@ -11,15 +11,16 @@
   Refusal: no real gh, `gh shim: no real gh on PATH`, rc 127. When: the shared
   token's core bucket is spent and no host log names the caller (P284). Tested by
   `gh_calls.py --self-test`.
-  Comment guard (R10-RAISE-GATE-SHIM), deny by default: any call that could write a comment on #201
+  Comment guard (R10-RAISE-GATE-SHIM), deny by default: any call that could write a comment on a record
+  issue (#201 or #3394: `budget_raise_gate.RECORD_ISSUES`, the shim's `trackers`, pinned by the self-test)
   is refused unless the caller is python running the tree's own `tools/pr/gh_comment.py`, resolved by
   real path (the installer bakes the path into the copy). Let through without it: a call on an explicit
   list of calls that cannot. `issue` view/list/status/create; `issue` comment/close/reopen/edit/delete/
-  lock/unlock/pin/unpin/transfer/develop only with one target read as a plain number other than 201,
+  lock/unlock/pin/unpin/transfer/develop only with one target read as a plain number other than a tracker,
   under gh's own flag table (an unknown flag, a short-flag cluster or a second target is refused, so
   `close`/`reopen` `--comment`/`-c` are covered by the rule, not by name); `pr` unless a word reads as
-  201; `api` as a read (no field, no `--input`, GET, only an Accept header) or as a write that is not at
-  `issues/201/comments`, not at an unreadable path, not at `issues/comments/<id>` and not graphql unless
+  a tracker; `api` as a read (no field, no `--input`, GET, only an Accept header) or as a write that is not at
+  `issues/<tracker>/comments`, not at an unreadable path, not at `issues/comments/<id>` and not graphql unless
   the document holds no `mutation`/`subscription` and is not read from a file; gh command groups with no
   issue-comment surface; everything else (an unknown subcommand, an alias, an extension, a leading flag
   but `--version`/`--help`) is refused. The number is read after dropping leading zeros, trailing
diff --git a/tools/audit/seat/merge_pr.sh b/tools/audit/seat/merge_pr.sh
index 04d6db58a..c0ec5291a 100755
--- a/tools/audit/seat/merge_pr.sh
+++ b/tools/audit/seat/merge_pr.sh
@@ -3,7 +3,7 @@
 # merge_pr.sh --self-test
 #
 # owner mode approves code-owned paths as tvofi's account under the mandate
-# comment <comment-id> on #201, read live at this run by budget_raise_gate.py's
+# comment <comment-id> on a record issue (#201 or its continuation), read live at this run by budget_raise_gate.py's
 # own reading (`_mandate`, `mandate_state` judged now, its scope the gate's
 # MANDATE_COVERS_CODE_OWNED). No --mandate, or one not in force now, refuses before anything is
 # posted: the script never defaults to a mandate, because a stale one is a
@@ -56,7 +56,7 @@ gates() { # <pr> <mode> <mandate-id> <ready 0|1>
     READY_OWED=1
   fi
   [ "$2" = owner ] || return 0
-  [[ "$3" =~ ^[0-9]{6,}$ ]] || { echo "MANDATE REQUIRED: owner mode needs --mandate <comment-id> naming the mandate in force on #201 (got '$3')"; return 1; }
+  [[ "$3" =~ ^[0-9]{6,}$ ]] || { echo "MANDATE REQUIRED: owner mode needs --mandate <comment-id> naming the mandate in force on a record issue (got '$3')"; return 1; }
   MANDATE_WHY=$(mandate_in_force $R "$3") || { echo "MANDATE $MANDATE_WHY"; return 1; }
   MANDATE_WHY=${MANDATE_WHY#IN FORCE: }
 }
@@ -91,7 +91,7 @@ echo "$*" >> "$FAKE_LOG"
 case "$*" in
   *isDraft*) echo "${FAKE_DRAFT:-false}" ;;
   *issues/comments/*) [ -n "${FAKE_MANDATE:-}" ] && cat "$FAKE_MANDATE" || { echo "gh: Not Found (HTTP 404)" >&2; exit 1; } ;;
-  *issues/201/comments*) echo "[[]]" ;;
+  *issues/[0-9]*/comments*) echo "[[]]" ;;
   *check-runs*) cat "$FAKE_RUNS" ;;
   */rerun*) cp "$FAKE_RUNS_AFTER" "$FAKE_RUNS" ;;
   *actions/runs/*) echo "$FAKE_RUN_STATUS" ;;
@@ -299,6 +299,6 @@ gh pr merge $PR --merge --match-head-commit $S || exit 1  # mut:merge
 sleep 8; echo "merged $(gh pr view $PR --json mergeCommit --jq .mergeCommit.oid)"
 for n in "$@"; do echo "issue $n $(gh issue view $n --json state --jq .state)"; done
 bash tools/audit/worktree_gc.sh $R 2>&1 | tail -1; git pull -q --ff-only origin main
-# The rest of nudge.md step 12 (the #201 line, the roster stage, the state docs, main's
+# The rest of nudge.md step 12 (the record-issue line, the roster stage, the state docs, main's
 # suite state): a failure is printed OWED and never undoes the merge, but fails the script.
 python3 -I tools/audit/seat/postmerge.py "$PR" --repo $R --state-dir "${HPO_STATE_DIR:-$HOME/.local/state/hpo}"  # mut:postmerge
diff --git a/tools/audit/seat/merge_train.py b/tools/audit/seat/merge_train.py
index 75fcad291..986b1c7b4 100644
--- a/tools/audit/seat/merge_train.py
+++ b/tools/audit/seat/merge_train.py
@@ -1047,7 +1047,7 @@ def policy_fixture_builders():
         created = iso(at + datetime.timedelta(minutes=from_min))
         until = "programme-end" if until_min is None else iso(at + datetime.timedelta(minutes=until_min))
         return {"id": MID, "user": own, "created_at": created, "updated_at": created,
-                "issue_url": f"https://api.github.com/repos/{g.DEFAULT_REPO}/issues/{g.MANDATE_ISSUE}",
+                "issue_url": f"https://api.github.com/repos/{g.DEFAULT_REPO}/issues/201",
                 "body": f"MANDATE: agents may approve as {g.OWNER_LOGIN}, scope {scope}, "
                         f"from {created} until {until}"}
 
@@ -2026,7 +2026,7 @@ class Train:
         return self.run(filt, stdin="".join(f + "\n" for f in files))[1].split()
 
     def _mandate_read(self, cid: int) -> "tuple[dict | None, list[dict]]":
-        """The cited comment (None on GitHub's 404) and the tracking issue's
+        """The cited comment (None on GitHub's 404) and every record issue's
         comments since it was written, where a revocation would be --
         budget_raise_gate._mandate's routes, run through `self.run` so the
         self-test answers them and nothing here touches the remote elsewhere."""
@@ -2037,14 +2037,17 @@ class Train:
                 return None, []
             raise Stop("policy", f"mandate {cid} could not be read: " + o.strip()[-160:])
         comment = json.loads(o)
-        if not str(comment.get("issue_url") or "").endswith(g.MANDATE_ISSUE_URL):
+        if not g.on_record_issue(comment):
             return comment, []
-        code, o = self.run(["gh", "api", "--paginate", "--slurp",
-                            f"repos/{self.repo}/issues/{g.MANDATE_ISSUE}/comments"
-                            f"?per_page=100&since={comment.get('created_at')}"])
-        if code:
-            raise Stop("policy", "the mandate thread could not be read: " + o.strip()[-160:])
-        return comment, [c for page in json.loads(o) for c in page]
+        thread = []
+        for n in g.RECORD_ISSUES:
+            code, o = self.run(["gh", "api", "--paginate", "--slurp",
+                                f"repos/{self.repo}/issues/{n}/comments"
+                                f"?per_page=100&since={comment.get('created_at')}"])
+            if code:
+                raise Stop("policy", f"the mandate thread on #{n} could not be read: " + o.strip()[-160:])
+            thread += [c for page in json.loads(o) for c in page]
+        return comment, thread
 
     def policy_gate(self, pr: int, h: str, files: list[str], posting: "dict | None" = None) -> "str | None":
         """THE policy decision, ONE function so the run pass and the batch
@@ -2759,7 +2762,7 @@ class Train:
         return st.split()[-1]
 
     def post_merge(self, pr: int) -> None:
-        """The rest of nudge.md step 12, by `postmerge.py` (the #201 line, the
+        """The rest of nudge.md step 12, by `postmerge.py` (the record-issue line, the
         roster stage, the state docs, main's suite state). Its OWED lines are
         logged and never undo or stop the merge; the tool itself opens the
         ledger's `postmerge-owed` event for a step that failed."""
@@ -4370,8 +4373,9 @@ def _self_test() -> int:
             if argv[:2] == ["gh", "api"] and "/issues/comments/" in a:
                 return (0, json.dumps(world["mandate"])) if world.get("mandate") \
                     else (1, "gh: Not Found (HTTP 404)")
-            if argv[:2] == ["gh", "api"] and "/issues/201/comments" in a:
-                return 0, json.dumps([world.get("thread", [])])
+            if argv[:2] == ["gh", "api"] and any(f"/issues/{n}/comments" in a for n in _mandate_gate().RECORD_ISSUES):
+                # every record issue is read; the fixture's thread is #201's
+                return 0, json.dumps([world.get("thread", []) if "/issues/201/" in a else []])
             if argv[:2] == ["gh", "api"] and a.endswith("rulesets --jq " + argv[-1]):
                 return (0, "7") if world.get("required", "fast\n") else (1, "HTTP 404")
             if "rulesets/7" in a:
@@ -7638,8 +7642,8 @@ def _batch_self_test(check) -> None:
                 return 0, "reviewed"
             if argv[:2] == ["gh", "api"] and "/issues/comments/" in a:
                 return (0, json.dumps(w["mandate"])) if w.get("mandate") else (1, "gh: Not Found (HTTP 404)")
-            if argv[:2] == ["gh", "api"] and "/issues/201/comments" in a:
-                return 0, json.dumps([w.get("thread", [])])
+            if argv[:2] == ["gh", "api"] and any(f"/issues/{n}/comments" in a for n in _mandate_gate().RECORD_ISSUES):
+                return 0, json.dumps([w.get("thread", []) if "/issues/201/" in a else []])
             if "preflight.sh" in a:
                 return 0, "  clean    no refusal"
             if "worktree_gc.sh" in a:
diff --git a/tools/audit/seat/orchestrator_tick.py b/tools/audit/seat/orchestrator_tick.py
index cba1fde24..256a41186 100644
--- a/tools/audit/seat/orchestrator_tick.py
+++ b/tools/audit/seat/orchestrator_tick.py
@@ -77,7 +77,7 @@ Sections, each measured:
           is fixer work, and the orchestrator's duty is routing, not
           diagnosing; the
           mandate read (budget_raise_gate's own mandate_state, the one reader
-          -- the newest grammar-matching owner comment on #201 within
+          -- the newest grammar-matching owner comment on a record issue within
           --mandate-since-days, or exactly --mandate-id); action-pin drift
           (one action pinned at two refs across the workflow set); how far
           the checkout sits behind origin/main.
@@ -1954,7 +1954,7 @@ class Tick:
         else:
             start = (self.now - datetime.timedelta(
                 days=self.mandate_since_days)).strftime("%Y-%m-%dT%H:%M:%SZ")
-            cands = self._thread(start)
+            cands = self._thread(g, start)
             if cands is None:
                 self._mandate_cached = None
                 return None
@@ -1964,14 +1964,15 @@ class Tick:
                      ((c.get("body") or "").strip().splitlines()
                       or [""])[0].strip())]
         if not cands:
-            self.line(S, f"no mandate-grammar comment by the owner on #201 in "
+            self.line(S, "no mandate-grammar comment by the owner on "
+                         f"{', '.join(f'#{n}' for n in g.RECORD_ISSUES)} in "
                          f"the last {self.mandate_since_days}d (searched live "
                          "this tick) -- policy and raise merges refuse",
                       flag=self.mandate_id is None)
             self._mandate_cached = None
             return None
         m = cands[-1]
-        thread = self._thread(m.get("created_at") or "", exclude=m.get("id"))
+        thread = self._thread(g, m.get("created_at") or "", exclude=m.get("id"))
         self._mandate_live = m.get("id")
         ok, why = g.mandate_state(m.get("id"), m, thread or [], self.now,
                                   self.now.isoformat(), when="tick",
@@ -1981,22 +1982,25 @@ class Tick:
         self._mandate_cached = out
         return out
 
-    def _thread(self, since: str, exclude=None) -> "list | None":
-        """The comments a revocation would live in: the tracking issue's
-        comments `since` an instant (merge_train._mandate_read's second
-        route). None: the read failed and is already reported."""
-        code, o = self.gh(["api", "--paginate", "--slurp",
-                           f"repos/{self.repo}/issues/201/comments"
-                           f"?per_page=100&since={since}"])
-        if code:
-            self.unreadable("MAIN", f"#201's comments since {since}",
-                            o.strip()[-100:])
-            return None
-        try:
-            out = [c for page in json.loads(o) for c in page]
-        except ValueError as e:
-            self.unreadable("MAIN", f"#201's comments since {since}", str(e)[:100])
-            return None
+    def _thread(self, g, since: str, exclude=None) -> "list | None":
+        """The comments a grant or a revocation would live in: every record
+        issue's (budget_raise_gate.RECORD_ISSUES, oldest first) comments
+        `since` an instant (merge_train._mandate_read's second route). None:
+        a read failed and is already reported."""
+        out = []
+        for n in g.RECORD_ISSUES:
+            code, o = self.gh(["api", "--paginate", "--slurp",
+                               f"repos/{self.repo}/issues/{n}/comments"
+                               f"?per_page=100&since={since}"])
+            if code:
+                self.unreadable("MAIN", f"#{n}'s comments since {since}",
+                                o.strip()[-100:])
+                return None
+            try:
+                out += [c for page in json.loads(o) for c in page]
+            except ValueError as e:
+                self.unreadable("MAIN", f"#{n}'s comments since {since}", str(e)[:100])
+                return None
         return [c for c in out if c.get("id") != exclude]
 
     def pins(self, S: str) -> None:
@@ -2101,7 +2105,7 @@ class Tick:
         return merges
 
     def unrecorded(self, S: str, since: str) -> None:
-        """Merges on main with no #201 comment carrying the merge sha: the
+        """Merges on main with no record-issue comment carrying the merge sha: the
         record beat's other half. Every merge owes one, a record merge too
         (the orchestrator writes one after each). The newest CAP_MERGES merges
         among main's last UNRECORDED_SCAN first-parent commits, read through
@@ -2122,13 +2126,13 @@ class Tick:
                                  "--jq", ".total_count",
                                  "-f", f"q={sha} repo:{self.repo} type:comment"])
             if code2:
-                self.unreadable(S, f"#201 search for {sha[:12]}",
+                self.unreadable(S, f"record search for {sha[:12]}",
                                 o2.strip()[-80:])
                 break
             if o2.strip() == "0":
                 unrec.append(sha[:12])
         if unrec:
-            self.line(S, "record beat owed: state_docs.py --push + #201 "
+            self.line(S, "record beat owed: state_docs.py --push + record-issue "
                          "comment for " + ", ".join(unrec), flag=True)
         if capped:
             self.line(S, f"unrecorded-merge check capped at {CAP_MERGES}; "
@@ -2781,7 +2785,7 @@ def self_test() -> int:
         for n, body in bodies.items():
             gh.on((f"view {n} ", "--jq", ".body"), out=body)
         if with_mandate and gate_ok:
-            gh.on("issues/201/comments", out=json.dumps([[MAN]]))
+            gh.on("issues/201/comments", out=json.dumps([[MAN]])).on("/comments?per_page", out="[[]]")
         gh.on("rate_limit", out=json.dumps({"remaining": rate[0],
                                             "limit": rate[1]}))
         for pr, rv in (reviews or {}).items():
@@ -3351,7 +3355,7 @@ def self_test() -> int:
         gh.on(f"commits/{H1}/check-runs",
               out=json.dumps(run_obj("tests", conclusion="failure")) + "\n"
               + json.dumps(run_obj("record-autofix", conclusion="failure")))
-        gh.on("issues/201/comments", out=json.dumps([[MAN]]))
+        gh.on("issues/201/comments", out=json.dumps([[MAN]])).on("/comments?per_page", out="[[]]")
         t = Tick("o/r", str(version), gh=gh, git=Stub(), proc=Stub(), now=NOW)
         t.main()
         a, f = check("MAIN", [
@@ -3387,7 +3391,7 @@ def self_test() -> int:
         gh.on(f"commits/{H1}/check-runs",
               out="\n".join(json.dumps(run_obj(n)) for n in ("tests", "closures"))
               + "".join("\n" + json.dumps(run_obj(j, conclusion="failure")) for j in on_push))
-        gh.on("issues/201/comments", out=json.dumps([[MAN]]))
+        gh.on("issues/201/comments", out=json.dumps([[MAN]])).on("/comments?per_page", out="[[]]")
         t = Tick("o/r", str(version), gh=gh, git=Stub(), proc=Stub(), now=NOW)
         t.main()
         a, f = check("MAIN D-1", [
@@ -3414,7 +3418,7 @@ def self_test() -> int:
             gh.on(f"commits/{H1}/check-runs", out="\n".join(
                 json.dumps(run_obj(n, conclusion="failure" if n in names_red else "success"))
                 for n in ("gate", "tests / closures", "tests / fast (3.14)", "record-autofix")))
-            gh.on("issues/201/comments", out=json.dumps([[MAN]]))
+            gh.on("issues/201/comments", out=json.dumps([[MAN]])).on("/comments?per_page", out="[[]]")
             t = Tick("o/r", str(version), gh=gh, git=Stub(), proc=Stub(), now=NOW)
             t.main()
             return [x["text"] for x in t.findings]
@@ -3456,7 +3460,7 @@ def self_test() -> int:
             gh.on("check-runs/119215715286/annotations",
                   rc=0 if ann is not None else 1,
                   out=json.dumps(ann) if ann is not None else "HTTP 502")
-            gh.on("issues/201/comments", out=json.dumps([[MAN]]))
+            gh.on("issues/201/comments", out=json.dumps([[MAN]])).on("/comments?per_page", out="[[]]")
             t = Tick("o/r", str(version), gh=gh, git=Stub(), proc=Stub(), now=NOW)
             t.main()
             txt = [l["text"] for l in t.sections["MAIN"]]
@@ -3480,7 +3484,7 @@ def self_test() -> int:
         gh.on(f"commits/{H1}/check-runs", out=json.dumps(
             run_obj("tests", conclusion="cancelled", cid=119215715286)))
         gh.on("check-runs/119215715286/annotations", out=json.dumps([{"message": sup}]))
-        gh.on("issues/201/comments", out=json.dumps([[MAN]]))
+        gh.on("issues/201/comments", out=json.dumps([[MAN]])).on("/comments?per_page", out="[[]]")
         t = Tick("o/r", str(version), gh=gh, git=Stub(), proc=Stub(), now=NOW)
         t.main()
         txt = [l["text"] for l in t.sections["MAIN"]]
@@ -3526,7 +3530,7 @@ def self_test() -> int:
                 gh = Stub()
                 gh.on("issues/comments/", out=json.dumps(dict(
                     MAN, body=body, updated_at=MAN["created_at"])))
-                gh.on("issues/201/comments", out=json.dumps([[MAN]]))
+                gh.on("issues/201/comments", out=json.dumps([[MAN]])).on("/comments?per_page", out="[[]]")
                 t = Tick("o/r", str(version), gh=gh, git=Stub(), proc=Stub(),
                          now=NOW, mandate_id=mid)
                 t.mandate("MAIN")
@@ -3656,7 +3660,7 @@ def self_test() -> int:
         a, f = check("unrecorded single-parent", [
             ("a single-parent `(#N)` merge with no #201 comment is named; a "
              "recorded merge and a direct push are not",
-             owed == ["record beat owed: state_docs.py --push + #201 comment for "
+             owed == ["record beat owed: state_docs.py --push + record-issue comment for "
                       + sq[:12]]),
             ("null control: every merge recorded names none",
              not any("record beat owed" in x["text"] for x in t2.findings)),
@@ -3731,7 +3735,7 @@ def self_test() -> int:
                 iso(NOW - datetime.timedelta(days=1)),
                 iso(NOW + datetime.timedelta(hours=1))))
             gh = Stub()
-            gh.on("issues/201/comments", out=json.dumps([[man_soon]]))
+            gh.on("issues/201/comments", out=json.dumps([[man_soon]])).on("/comments?per_page", out="[[]]")
             gh.on("rate_limit", out=json.dumps({"remaining": 4000, "limit": 5000}))
             t = Tick("o/r", str(version), gh=gh, git=Stub(), proc=lambda p: [],
                      now=NOW)
@@ -3742,6 +3746,35 @@ def self_test() -> int:
             ])
             total, failed = total + a, failed + f
 
+        # ---- the record past #201's comment cap: every record issue is read ----
+        if gate_ok:
+            rec = g.RECORD_ISSUES[-1]
+            on_rec = dict(MAN, id=mid + 5, issue_url=MAN["issue_url"][:-3] + str(rec))
+            kill = {"id": mid + 9, "user": owner, "body": f"MANDATE REVOKED {mid}",
+                    "created_at": iso(NOW), "updated_at": iso(NOW),
+                    "issue_url": on_rec["issue_url"]}
+
+            def read(old, new):
+                gh = Stub()
+                gh.on("issues/201/comments", out=json.dumps([old]))
+                gh.on(f"issues/{rec}/comments", out=json.dumps([new]))
+                t = Tick("o/r", str(version), gh=gh, git=Stub(), proc=lambda p: [], now=NOW)
+                return t.mandate_read(), gh
+            got, gh = read([], [on_rec])
+            got201, _ = read([MAN], [kill])
+            got_ok, _ = read([MAN], [])
+            a, f = check("record issues", [
+                ("a grant on the continuation issue is found", bool(got) and got[1]["id"] == mid + 5 and got[3]),
+                ("both record issues are read", sorted(
+                    n for n in g.RECORD_ISSUES if any(f"issues/{n}/comments" in " ".join(c) for c in gh.calls))
+                 == sorted(g.RECORD_ISSUES)),
+                ("a #201 grant revoked on the continuation issue is not in force",
+                 bool(got201) and got201[1]["id"] == mid and not got201[3]),
+                ("null control: the same #201 grant with no revocation is in force",
+                 bool(got_ok) and got_ok[3]),
+            ])
+            total, failed = total + a, failed + f
+
         # ---- rate headroom ----
         for remaining, want in ((500, True), (4000, False)):
             t = tick(rate=(remaining, 5000), with_mandate=False)
@@ -4381,7 +4414,7 @@ def self_test() -> int:
         gh.on("check-runs/424243", out=json.dumps(
             {"summary": "skip-failed-recording: no bot commit is coming",
              "text": ""}))
-        gh.on("issues/201/comments", out=json.dumps([[MAN]]))
+        gh.on("issues/201/comments", out=json.dumps([[MAN]])).on("/comments?per_page", out="[[]]")
         gh.on("rate_limit", out=json.dumps({"remaining": 4000, "limit": 5000}))
         t = Tick("o/r", str(version), gh=gh, git=Stub(),
                  proc=lambda p: [], now=NOW)
@@ -4528,7 +4561,7 @@ def self_test() -> int:
         a, f = check("search GET", [
             ("record beat found via GET (no 404 unreadable)",
              any("record beat owed" in x["text"] for x in t.findings)
-             and not any("UNREADABLE" in x["text"] and "#201 search"
+             and not any("UNREADABLE" in x["text"] and "record search"
                          in x["text"] for x in t.findings)),
         ])
         total, failed = total + a, failed + f
diff --git a/tools/audit/seat/plan_page.py b/tools/audit/seat/plan_page.py
index 79056927b..6980acec0 100644
--- a/tools/audit/seat/plan_page.py
+++ b/tools/audit/seat/plan_page.py
@@ -79,9 +79,13 @@ import merge_throughput as mt  # noqa: E402 -- the flow board's computations
 import bottleneck_check  # noqa: E402 -- the one owner of the alert thresholds
 
 SELF = "tools/audit/seat/plan_page.py"
-# The round's tracking issue (CLAUDE.md's #201): the open-issue count leaves it
-# out, because it stays open for the whole programme by design.
-TRACKING_ISSUE = 201
+sys.path.insert(0, str(_SEAT.parents[1] / "policy"))
+from budget_raise_gate import RECORD_ISSUES  # noqa: E402 -- the one record-issue definition
+# The programme's record issues (#201, and its continuation past GitHub's
+# 2,500-comment cap): the open-issue count leaves them out, because they stay
+# open for the whole programme by design. The page names the live one.
+TRACKING_ISSUES = frozenset(RECORD_ISSUES)
+TRACKING_ISSUE = RECORD_ISSUES[-1]
 _ROUND_PREFIX = re.compile(r"\AR\d+-")
 _GROUP_ID = re.compile(r"\bR\d+(?:-[A-Z0-9]+)+\b")
 _DELIVERY_TITLE = re.compile(r"\A(R\d+-[A-Z0-9-]+):")
@@ -423,7 +427,7 @@ def project_issues(roster: dict, plan: dict, open_now: set) -> dict:
     out = {"close_at": close_at, "unplanned": unplanned,
             "other": open_now - set(close_at) - unplanned}
     out["orphans"] = {n: sorted(wired.get(n, [])) for n in sorted(out["other"])
-                      if n != TRACKING_ISSUE}
+                      if n not in TRACKING_ISSUES}
     return out
 
 
@@ -483,7 +487,7 @@ def issues_section(roster: dict, plan: dict, snap: dict) -> str:
             f"start; each is projected to close at the planned finish of the last group "
             f"carrying it. {len(unplanned)} sit on groups with no planned finish and stay "
             f"flat; {len(proj['other'])} other open issues are on no open group: "
-            f"#{TRACKING_ISSUE} (the tracking issue) and the "
+            f"{', '.join(f'#{n}' for n in RECORD_ISSUES)} (the record issues) and the "
             f"{len(proj['orphans'])} listed below as unplanned.")
     title = {i["number"]: i.get("title") or "" for i in snap["issues"]}
     orphans = "".join(
@@ -600,7 +604,7 @@ def render(roster: dict, roster_src: str, plan: dict, snap: dict,
               for k in _STRIP}
     open_iss = ("—" if snap.get("offline") else str(sum(
         1 for i in snap["issues"]
-        if i["state"] == "OPEN" and i["number"] != TRACKING_ISSUE)))
+        if i["state"] == "OPEN" and i["number"] not in TRACKING_ISSUES)))
     order = {k: i for i, k in enumerate(("S", "M", "L", "XL"))}
     sizes = ", ".join(f"{k} {v:g} h" for k, v in sorted(
         model["sizes_hours"].items(), key=lambda kv: (order.get(kv[0], 99), kv[0])))
@@ -854,8 +858,8 @@ def _self_test() -> int:
     check("an open issue wired only via `fixes` to an open group closes at its finish, "
           "not an unplanned orphan",
           fp["close_at"].get(8) == _t("2026-01-05T10:00:00Z") and not fp["orphans"], fp)
-    check("the tracking issue is never an orphan",
-          TRACKING_ISSUE not in project_issues(ir, ip, {1, TRACKING_ISSUE})["orphans"])
+    check("no record issue, #201 or its continuation, is ever an orphan",
+          not TRACKING_ISSUES & set(project_issues(ir, ip, {1, *TRACKING_ISSUES})["orphans"]))
     osec = issues_section(ir, dict(ip, generated={"start": "2026-01-05T00:00:00Z"},
                                    summary={"closure": "2026-01-07T00:00:00Z"}),
                           {"issues": [{"number": n, "title": f"t{n}", "state": "OPEN"}
@@ -1295,7 +1299,7 @@ td.st{min-width:11rem}
   <div class="stat"><b>{{n_blocked}}</b><span>waiting on a group</span></div>
   <div class="stat"><b>{{n_partial}}</b><span>part merged, residual open</span></div>
   <div class="stat"><b>{{n_held}}</b><span>held by a disposition</span></div>
-  <div class="stat"><b>{{open_iss}}</b><span>open issues (excl. #{{tracking}})</span></div>
+  <div class="stat"><b>{{open_iss}}</b><span>open issues (excl. the record issues)</span></div>
   <div class="stat end"><b>{{end}}</b><span>projected programme close</span></div>
 </div>
 
diff --git a/tools/audit/seat/postmerge.py b/tools/audit/seat/postmerge.py
index 084020a24..f00235630 100644
--- a/tools/audit/seat/postmerge.py
+++ b/tools/audit/seat/postmerge.py
@@ -8,7 +8,7 @@ Both merge paths (`merge_pr.sh`, and `merge_train.py`'s landing) call it once
 the merge is confirmed. It runs, in order, and a failure in any is printed as
 `OWED <step>: <why>` and never undoes the merge or stops the next step:
 
-  record   `record_beat.py`: one #201 line from the fixed template, posted by
+  record   `record_beat.py`: one record-issue line from the fixed template, posted by
            `tools/pr/gh_comment.py` with a byte-identical read-back.
   stage    `roster_sync.py --apply` derives the group's `done` stage from the
            merged pull request. A refused sync prints `set-stage owed <GROUP>
@@ -168,7 +168,7 @@ def self_test() -> int:
                                               "merge_train.py classify")] == [1, 1, 1, 1], log)
     code, lines, log = go(dry=True)
     check("the dry run prints the exact comment and every command, runs none, exits 0",
-          code == 0 and lines[0] == f"DRY-RUN comment: Merged #7 {full} (R10-X). Closed issues: #5. Leaves #201 open."
+          code == 0 and lines[0] == f"DRY-RUN comment: Merged #7 {full} (R10-X). Closed issues: #5. Leaves #{rb.RECORD_ISSUE} open."
           and [l.split(":")[0] for l in lines[1:5]] == ["DRY-RUN command", "DRY-RUN stage", "DRY-RUN docs",
                                                          "DRY-RUN main"]
           and not any(k in c for c in log for k in ("gh_comment", "roster_sync", "state_docs", "classify", "ledger")),
diff --git a/tools/audit/seat/proof_watch.py b/tools/audit/seat/proof_watch.py
index 6baf73fa4..f587e4bb8 100644
--- a/tools/audit/seat/proof_watch.py
+++ b/tools/audit/seat/proof_watch.py
@@ -411,7 +411,7 @@ def main(argv: list[str] | None = None) -> int:
     ap.add_argument("--mode", choices=("app", "owner"), default="app",
                     help="the merge identity merge_pr.sh is handed (default %(default)s)")
     ap.add_argument("--mandate", default="",
-                    help="owner mode: the #201 mandate comment id merge_pr.sh reads live")
+                    help="owner mode: the record-issue mandate comment id merge_pr.sh reads live")
     ap.add_argument("--dry-run", action="store_true", help="run every guard, touch nothing")
     a = ap.parse_args(argv)
     if a.self_test:
diff --git a/tools/audit/seat/pulse.py b/tools/audit/seat/pulse.py
index 0d5a565a7..f33c27699 100644
--- a/tools/audit/seat/pulse.py
+++ b/tools/audit/seat/pulse.py
@@ -86,7 +86,7 @@ beat). One stale id beside one fresh is ok: only fresh ids are counted.
 What it does not see, stated: a programme with nothing owed reads ok however
 long it has been stopped -- no cost accrues there but time; a consumer whose
 input no off-host producer writes (a local seat's work before its push); and
-the record duty of a #201 comment per merge.
+the record duty of a record-issue comment per merge.
 
 Run it where the host is not (a scheduled cloud probe seat), and at a
 takeover before the hand survey. --dump writes the snapshot it judged, so a
diff --git a/tools/audit/seat/queue_pre_flight.py b/tools/audit/seat/queue_pre_flight.py
index b0a759f54..f7f02fa4e 100644
--- a/tools/audit/seat/queue_pre_flight.py
+++ b/tools/audit/seat/queue_pre_flight.py
@@ -362,8 +362,9 @@ def _self_test() -> int:
             if argv[:2] == ["gh", "api"] and "/issues/comments/" in a:
                 return (0, json.dumps(world["mandate"])) if world.get("mandate") \
                     else (1, "gh: Not Found (HTTP 404)")
-            if argv[:2] == ["gh", "api"] and "/issues/201/comments" in a:
-                return 0, json.dumps([world.get("thread", [])])
+            if argv[:2] == ["gh", "api"] and any(f"/issues/{n}/comments" in a for n in mt._mandate_gate().RECORD_ISSUES):
+                # every record issue is read; the fixture's thread is #201's
+                return 0, json.dumps([world.get("thread", []) if "/issues/201/" in a else []])
             if argv[:2] == ["gh", "api"] and "/issues/7/comments" in a:
                 if world.get("comments_fail"):
                     return 1, "gh: HTTP 502"
diff --git a/tools/audit/seat/r10_mandate_guard_mutants.py b/tools/audit/seat/r10_mandate_guard_mutants.py
index a971159fc..9099d7950 100644
--- a/tools/audit/seat/r10_mandate_guard_mutants.py
+++ b/tools/audit/seat/r10_mandate_guard_mutants.py
@@ -43,7 +43,7 @@ PLANTS = {
     "G1": (GHC, 'if g.revocable(c, now) and g.revokes(body, c.get("id"))}',
            'if g.revocable(c, now) and g.MANDATE_REVOKED.search(body)'
            ' and re.search(rf"{c.get(\'id\')}(?!\\d)", body)}'),
-    "G2": (GHC, 'on = str(fetch(repo, comment).get("issue_url") or "").endswith(g.MANDATE_ISSUE_URL)',
+    "G2": (GHC, 'on = g.on_record_issue(fetch(repo, comment))',
            "on = False"),
     "G3": (GHC, "} - {withdraw})", "}) if withdraw is None else []"),
     "G4": (GHC, "        mandate_guard(a.repo, body,", "        (lambda *_a, **_k: None)(a.repo, body,"),
diff --git a/tools/audit/seat/r10_roster_ops_mutants.py b/tools/audit/seat/r10_roster_ops_mutants.py
index 768440bb7..996d47d0c 100644
--- a/tools/audit/seat/r10_roster_ops_mutants.py
+++ b/tools/audit/seat/r10_roster_ops_mutants.py
@@ -45,7 +45,7 @@ Plants, one per refusal of the two ops and per round-trip property:
          stage without it (Y4), and the dry run's (Y5) and the write path's
          (Y6) projection without it, which decides a same-pass Carry:.
   R1-R5  carry_audit's roster arm: closed-only issues unreported (R1),
-         unlisted issues unreported (R2), #201 reported (R3), absorbed_into
+         unlisted issues unreported (R2), a record issue reported (R3), absorbed_into
          unnamed (R4), pull requests read as issues (R5).
   S1-S7  the vocabulary barrier (R10-ORCH-ROSTER-SCHEMA): each of the three
          stage-writing ops losing its classification check (S1 set-stage, S2
@@ -219,7 +219,7 @@ PLANTS = {
     "R1": (AUDIT, "        elif not any(live for _, live in by):\n",
            "        elif False:  # R1\n"),
     "R2": (AUDIT, "        if not by:\n", "        if False:  # R2\n"),
-    "R3": (AUDIT, "    for n in sorted(open_issues - {LOG_ISSUE}):\n",
+    "R3": (AUDIT, "    for n in sorted(open_issues - log_issues()):\n",
            "    for n in sorted(open_issues):  # R3\n"),
     "R4": (AUDIT, '        where = f"absorbed into {into}" if stage == "absorbed" and into else stage\n',
            "        where = stage  # R4\n"),
diff --git a/tools/audit/seat/record_beat.py b/tools/audit/seat/record_beat.py
index eb39895bf..e05a84815 100644
--- a/tools/audit/seat/record_beat.py
+++ b/tools/audit/seat/record_beat.py
@@ -1,5 +1,5 @@
 #!/usr/bin/env python3
-"""The #201 record comment of a merge: from a fixed template, read back.
+"""The record-issue comment of a merge: from a fixed template, read back.
 
     python3 tools/audit/seat/record_beat.py [--repo O/R] [--state-dir D] [--dry-run] <PR>...
     python3 tools/audit/seat/record_beat.py --self-test
@@ -9,8 +9,10 @@ GitHub names, then `git rev-parse --verify <oid>^{commit}`; a sha is never
 typed), renders one line from `TEMPLATE`, writes it to a body file under the
 state directory (`gh_comment.py` refuses a shared root) and posts it with
 `tools/pr/gh_comment.py post`, which exits non-zero unless the comment read
-back off the API is byte-identical. The orchestrator tick finds a merge's
-record by searching #201's comments for the 40-character sha
+back off the API is byte-identical. It posts to
+`budget_raise_gate.RECORD_ISSUE`, the one definition of the record issue
+(#201 until its 2,500-comment cap; its continuation since). The orchestrator tick finds a merge's
+record by searching its comments for the 40-character sha
 (`orchestrator_tick.py`'s `unrecorded`), so the template carries it whole: ten
 merges once read unrecorded because their comments cited a short sha.
 
@@ -37,12 +39,13 @@ SEAT = Path(__file__).resolve().parent
 ROOT = SEAT.parents[2]
 sys.path.insert(0, str(SEAT))
 import roster_lib  # noqa: E402
+sys.path.insert(0, str(ROOT / "tools/policy"))
+from budget_raise_gate import RECORD_ISSUE  # noqa: E402  the one record-issue definition
 
 DEFAULT_REPO = "tvofi/heatpump_optimizer"
-RECORD_ISSUE = 201
 NO_GROUP = "no-group"
 SHA = re.compile(r"^[0-9a-f]{40}$")
-TEMPLATE = "Merged #{pr} {sha} ({group}). Closed issues: {issues}. Leaves #201 open."
+TEMPLATE = "Merged #{pr} {sha} ({group}). Closed issues: {issues}. Leaves #{record} open."
 
 
 class Owed(Exception):
@@ -107,7 +110,7 @@ def facts(pr: int, repo: str, run=sh) -> dict:
 
 
 def render(pr: int, sha: str, group: str, issues: list) -> str:
-    return TEMPLATE.format(pr=pr, sha=sha, group=group,
+    return TEMPLATE.format(pr=pr, sha=sha, group=group, record=RECORD_ISSUE,
                            issues=" ".join(f"#{n}" for n in issues) or "none") + "\n"
 
 
@@ -131,7 +134,7 @@ def record(pr: int, repo: str, state_dir: Path, f: dict, group: str, dry: bool,
         return text
     code, o = run(cmd)
     if code != 0:
-        raise Owed(f"the #201 comment was refused ({o.strip()[-160:] or 'no output'})")
+        raise Owed(f"the #{RECORD_ISSUE} comment was refused ({o.strip()[-160:] or 'no output'})")
     return text
 
 
@@ -212,16 +215,18 @@ def self_test() -> int:
         lines = []
         text = record(7, DEFAULT_REPO, Path(td), f, "R9-FR-1", True, run, lines.append)
         check("the dry run prints the exact comment", lines[0] == "DRY-RUN comment: " + text.rstrip("\n")
-              and text == f"Merged #7 {full} (R9-FR-1). Closed issues: #3 #9. Leaves #201 open.\n", lines)
+              and text == f"Merged #7 {full} (R9-FR-1). Closed issues: #3 #9. Leaves #{RECORD_ISSUE} open.\n", lines)
+        check("the comment goes to the record issue, never #201 (closed to comments at its cap)",
+              RECORD_ISSUE != 201 and f"--issue {RECORD_ISSUE} " in lines[1], lines)
         check("the dry run prints the exact command and posts nothing",
-              "gh_comment.py post --repo " + DEFAULT_REPO + " --issue 201 --body-file " in lines[1]
+              "gh_comment.py post --repo " + DEFAULT_REPO + f" --issue {RECORD_ISSUE} --body-file " in lines[1]
               and not any("gh_comment.py" in " ".join(a) for a in log), lines)
         check("the body file lives under the state directory",
               (Path(td) / "postmerge/record-7.md").read_text() == text)
         record(7, DEFAULT_REPO, Path(td), f, "R9-FR-1", False, run)
         check("a real run posts through gh_comment.py", any("gh_comment.py" in " ".join(a) for a in log))
         # the tick's finder searches the comment text for the full sha
-        short = f"Merged #7 {full[:7]} (R9-FR-1). Leaves #201 open."
+        short = f"Merged #7 {full[:7]} (R9-FR-1). Leaves #{RECORD_ISSUE} open."
         check("the tick's finder (full sha in the comment) matches the new comment, not a short-sha one",
               full in text and full not in short)
         bad, _ = fake(rc_comment=1)
diff --git a/tools/audit/seat/record_row.py b/tools/audit/seat/record_row.py
index 61ef053e3..1eae007c4 100644
--- a/tools/audit/seat/record_row.py
+++ b/tools/audit/seat/record_row.py
@@ -125,10 +125,6 @@ RED_CHECKS = {
     "delivery-status": "governance / delivery-status",
 }
 
-#: The programme's tracking issue; the beat posts its coordination comment
-#: there (delivery-status-tracking.md item 3).
-TRACKING_ISSUE = 201
-
 #: GitHub's own closing-keyword families. The generated prose must carry none
 #: of them before an issue number, because GitHub closes an issue from a pull
 #: request's body prose -- a generated `Closes #N` would close an issue the
@@ -603,7 +599,8 @@ def pr_title(rows: list[dict]) -> str:
 
 
 def coord_comment(pr_number: int, rows: list[dict]) -> str:
-    """The beat's #201 coordination comment (delivery-status-tracking item 3).
+    """The beat's coordination comment on the record issue
+    (budget_raise_gate.RECORD_ISSUE; delivery-status-tracking item 3).
 
     States what landed and what stayed manual; carries no closing keyword.
     """
@@ -616,7 +613,7 @@ def coord_comment(pr_number: int, rows: list[dict]) -> str:
         "where `--automerge-check` passes; the HANDOVER updated-for line "
         "stays manual by design. A seat's edit to a neutral row takes it "
         "off the automerge path and back to a manual review.")
-    _no_closing_where("#201 comment", text)
+    _no_closing_where("record-issue comment", text)
     return text
 
 
@@ -1934,7 +1931,7 @@ def main() -> int:
     ap.add_argument("--print-title", action="store_true",
                     help="print the record pull request title for --plan-file")
     ap.add_argument("--print-comment", action="store_true",
-                    help="print the #201 comment for --plan-file and --pr")
+                    help="print the record-issue comment for --plan-file and --pr")
     ap.add_argument("--write-self-row", action="store_true",
                     help="write dev/programme/delivery/<--pr>.md for the open record "
                          "pull request, anchoring its number and carrying no "
diff --git a/tools/audit/seat/shims/seat-gh b/tools/audit/seat/shims/seat-gh
index 94781a751..15d7b0c8f 100755
--- a/tools/audit/seat/shims/seat-gh
+++ b/tools/audit/seat/shims/seat-gh
@@ -120,18 +120,18 @@ esac
   chmod 600 "$log"
 ) 2>/dev/null || true
 
-# The #201 comment guard (R10-RAISE-GATE-SHIM; tools/pr/gh_comment.py's mandate_guard
+# The record-issue comment guard (R10-RAISE-GATE-SHIM; tools/pr/gh_comment.py's mandate_guard
 # lives in that script alone, so a raw post bypassed it). DENY BY DEFAULT: a call that could
-# write a comment on the tracking issue is refused unless the caller is python running the
+# write a comment on a record issue (#201, or its continuation) is refused unless the caller is python running the
 # tree's own gh_comment.py (by real path); it is let through only when it is on an explicit
 # list of calls that cannot. The list is gh's own command table, not a list of spellings:
 #   - no subcommand, or --version/--help alone: pass; any other leading flag: refused;
 #   - `issue`: view/list/status/create pass; comment, close, reopen, edit, delete, lock,
 #     unlock, pin, unpin, transfer and develop pass only with exactly one target that reads as
-#     a plain number other than the tracker, under gh's own flag table (an unknown flag, or a
+#     a plain number other than a tracker, under gh's own flag table (an unknown flag, or a
 #     short-flag cluster, is refused: it could be a value that moves the target); any other
 #     verb is refused;
-#   - `pr`: refused when any word reads as the tracker's number (a PR cannot be the issue,
+#   - `pr`: refused when any word reads as a tracker's number (a PR cannot be the issue,
 #     so this is belt and braces); otherwise passes;
 #   - `api`: a call with no body field, no --input, no method but GET and no header but
 #     Accept is a read and passes (flags read by gh api's own table, an unknown one refused);
@@ -146,7 +146,9 @@ esac
 # %-decoding and `.`/`..`/empty path segments, matched in lower case. Residual, by design: the caller test reads
 # `ps` args, which a caller writes (`exec -a`), so a deliberate spoof of the parent passes
 # (Carry: R10-RAISE-GATE-SHIM); the shim is a guard against a seat's habit, not an adversary.
-tracker=201
+# The trackers: budget_raise_gate.RECORD_ISSUES, the one definition (gh_calls.py's self-test
+# pins this line to it). #201 hit GitHub's 2,500-comment cap; the record continues in the last.
+trackers='201 3394'
 # gh_comment.py's own path: seat_venv.sh --install-shims bakes the tree's into the next
 # line; a shim run from its place in the tree derives it; anywhere else it stays empty,
 # and then no caller passes.
@@ -171,7 +173,7 @@ num() {
 }
 # norm <path>: the path's segments after %-decoding, dropping a URL's scheme and host, a query
 # or anchor, and `.`/`..`/empty segments, and lower-casing every letter (a path segment is
-# matched in lower case: `ISSUES/201/COMMENTS` is the tracker's), into NSEG; 1 when it cannot be read
+# matched in lower case: `ISSUES/201/COMMENTS` is a tracker's), into NSEG; 1 when it cannot be read
 norm() {
   local w=$1 IFS=/ seg
   local -a segs
@@ -223,7 +225,7 @@ issue_gate() {
     ''|view|list|status|create) return 0 ;;
     comment|close|reopen|edit|delete|lock|unlock|pin|unpin|transfer|develop)
       [ -z "$bad" ] && [ "${#pos[@]}" -eq 2 ] || return 1
-      t=$(num "${pos[1]}"); [ "$t" != '?' ] && [ "$t" != "$tracker" ] ;;
+      t=$(num "${pos[1]}"); [ "$t" != '?' ] && ! has "$trackers" "$t" ;;
     *) return 1 ;;
   esac
 }
@@ -231,7 +233,7 @@ pr_gate() {
   local a
   shift
   for a in "$@"; do
-    case $a in -*) ;; *) [ "$(num "$a")" = "$tracker" ] && return 1 ;; esac
+    case $a in -*) ;; *) has "$trackers" "$(num "$a")" && return 1 ;; esac
   done
   return 0
 }
@@ -286,7 +288,7 @@ api_gate() {
         nxt=${NSEG[$((k + 1))]:-}
         [ "$nxt" = comments ] && return 1
         if [ "${NSEG[$((k + 2))]:-}" = comments ]; then
-          t=$(num "$nxt"); { [ "$t" != '?' ] && [ "$t" != "$tracker" ]; } || return 1
+          t=$(num "$nxt"); { [ "$t" != '?' ] && ! has "$trackers" "$t"; } || return 1
         fi ;;
     esac
     k=$((k + 1))
@@ -336,7 +338,7 @@ if [ -n "${hit:-}" ]; then
       a=$(rp "$script") && b=$(rp "$gcpy") && [ "$a" = "$b" ] && ok=1
     fi ;;
   esac
-  [ -n "$ok" ] || { echo "gh shim: a comment write on #$tracker goes through tools/pr/gh_comment.py (its mandate guard refuses a post that voids a mandate); refused" >&2; exit 1; }
+  [ -n "$ok" ] || { echo "gh shim: a comment write on a record issue (#${trackers// /, #}) goes through tools/pr/gh_comment.py (its mandate guard refuses a post that voids a mandate); refused" >&2; exit 1; }
 fi
 
 exec "$real" "$@"
diff --git a/tools/audit/seat/sweep_template.md b/tools/audit/seat/sweep_template.md
index 3e27bc028..a897da69e 100644
--- a/tools/audit/seat/sweep_template.md
+++ b/tools/audit/seat/sweep_template.md
@@ -28,7 +28,7 @@ rendered text that no overlay value supplied.
 |---|---|
 | `round` | the round number, as the `handoff/r<N>-*` refs spell it |
 | `repo` | the repository as `<owner>/<name>` |
-| `mandate` | the comment id of the owner's mandate in force on #201 |
+| `mandate` | the comment id of the owner's mandate in force on #201 or #3394 |
 | `seat_root` | the directory the session's seat worktrees live under |
 | `orch_scratch` | the orchestration scratch directory (not a worktree) |
 | `orch_checkout` | the orchestrator's own checkout, fetched before every re-read |
@@ -70,7 +70,7 @@ ORCHESTRATOR SWEEP, round {{round}}, repository {{repo}}. Read {{seat_ledger}} f
 
 (3) Merges. Verdicted pull requests go to one train on the hourly pitch: `tools/audit/seat/merge_train.py sweep --state-dir {{orch_scratch}} --mandate {{mandate}}` (detached under `tools/audit/seat/daemonize.py`; `tools/audit/seat/tick_loop.sh --sweep` runs it from the tick loop) builds the queue from the verdict bus and `add`s each verdicted head, starting `tools/audit/seat/train.sh` with `--overlap --approval-carry --skip-bad --free-holders --bot-prs --pre-flight --mandate {{mandate}}`, the recommended default (`dev/governance/roles/standing-merge.md`), when no train is running and otherwise loading that train's next batch, never a second live train (`dev/governance/roles/nudge.md` step 3; `dev/governance/roles/orchestrator.md` section 11). The open record or autofix pull request merges inside that train through `--bot-prs`, not between pitches. A budget-file or policy head goes the batch's serial route, where `--pre-flight` parks a budget raise or a policy head the owner has not approved at that head under an open mandate (`Train.raise_hold`, `Train.policy_gate`); a parked one merges directly under mandate {{mandate}} (`dev/governance/roles/nudge.md` steps 5 and 7; `CLAUDE.md` rule 2). Between pitches, a record or autofix pull request merges by hand only behind `tools/audit/seat/record_row.py --automerge-check` (`dev/governance/roles/nudge.md` step 6).
 
-(4) After each merge (`dev/governance/roles/nudge.md` steps 12 and 18): `tools/audit/seat/roster_edit.py set-stage` for a roster group, one #201 comment through `tools/pr/gh_comment.py` with its read-back, `tools/audit/worktree_gc.sh {{repo}}`, the issues the merge commit closed read back (`dev/governance/roles/orchestrator.md` section 4), and the finished seat's worktrees under {{seat_root}} and its scratch removed.
+(4) After each merge (`dev/governance/roles/nudge.md` steps 12 and 18): `tools/audit/seat/roster_edit.py set-stage` for a roster group, one #3394 comment through `tools/pr/gh_comment.py` with its read-back, `tools/audit/worktree_gc.sh {{repo}}`, the issues the merge commit closed read back (`dev/governance/roles/orchestrator.md` section 4), and the finished seat's worktrees under {{seat_root}} and its scratch removed.
 
 (4b) Record beat. The beat's `plan-beat` row runs `python3 tools/plan/replan.py --out {{plan_json}} --slots {{plan_slots}} --seats {{plan_seats}}`, then `tools/audit/seat/state_docs.py --push --mirror {{state_mirror}} --plan {{plan_json}}`, every 30 minutes, merge or none; it publishes the plan page as `PLAN.html` in the plan table's commit at the state ref and mirrors it as {{plan_page}}, republished at the same path. A `plan-beat: PLAN UNAVAILABLE` line in {{digest}}/digest.txt is the page UNAVAILABLE (the other docs are still pushed; the ref keeps the last good page): answer its reason and re-run that replan, never hand-run `plan_page.py` around the refusal; a `plan-beat: REFUSED` line is the docs push's own refusal. A `plan-beat: PLAN MOVED` line is a page that changed since the last beat: republish it at {{plan_page}} this sweep (owner ruling, 2026-11-06: every sweep updates the plan artifact). The beat's `gantt` row compares that plan with the Gantt baseline through `tools/audit/seat/sweep_gantt.py`: it reads the roster at {{gantt_roster}}, the fire ledger {{fire_ledger}} and the acks file {{gantt_acks}}; each `GANTT-SLIP` line of {{digest}}/digest.txt is owed `act`, `defer` or `accept`, appended to {{gantt_acks}} (owner ruling, 2026-11-01).
 
diff --git a/tools/policy/budget_raise_gate.py b/tools/policy/budget_raise_gate.py
index 11751f4bd..c871a9993 100644
--- a/tools/policy/budget_raise_gate.py
+++ b/tools/policy/budget_raise_gate.py
@@ -39,10 +39,10 @@ CHANGES_REQUESTED or DISMISSED; a COMMENTED review decides nothing) is APPROVED
 and was submitted on this exact head SHA, by the login AND numeric id AND
 account type pinned below, and does not say in its own body that an agent gave
 it (AGENT_DECLARED below) -- or, if it does, cites one mandate the owner
-recorded on #201 that covers budget raises and was in force when the review
-was submitted (MANDATE_GRAMMAR, mandate_check), and the body carries the raise
-justification (JUSTIFICATION_HEADING, justification). Anything else, a failed
-API read included, is exit 1.
+recorded on a record issue (RECORD_ISSUES) that covers budget raises and was
+in force when the review was submitted (MANDATE_GRAMMAR, mandate_check), and
+the body carries the raise justification (JUSTIFICATION_HEADING,
+justification). Anything else, a failed API read included, is exit 1.
 
 WHAT IT DOES NOT SEE. A ledger disposition (`survivor_triage`, `killed_by`)
 is a per-site record, not a cap, and is `free` here: an `equivalent` verdict
@@ -102,7 +102,7 @@ AGENT_DECLARED = re.compile(
     r"|claude\.ai/code|generated (?:by|with) \[?claude", re.I)
 # The owner's recorded mandate (tvofi, 2026-10-02, amending the refusal above):
 # an agent may approve as tvofi, openly, while a mandate tvofi wrote is in
-# force. The record is a comment on the tracking issue by the pinned owner
+# force. The record is a comment on a record issue (RECORD_ISSUES) by the pinned owner
 # account, read from the API at run time; no copy in the tree is trusted. Its
 # first line is MANDATE_GRAMMAR, and a comment edited at any time grants
 # nothing (anyone with write access can edit it and its author stays tvofi).
@@ -112,8 +112,22 @@ AGENT_DECLARED = re.compile(
 # "mandate <id>" or as the comment's `issuecomment-<id>` URL, and that word
 # keeps it declared an agent's: authorship is never hidden to pass.
 DEFAULT_REPO = "tvofi/heatpump_optimizer"
-MANDATE_ISSUE = 201
-MANDATE_ISSUE_URL = f"/repos/{DEFAULT_REPO}/issues/{MANDATE_ISSUE}"
+# The programme's coordination and record issue, THE one definition every
+# writer and reader imports (a shell or workflow that cannot import it is
+# pinned to it by a self-test). #201 was the record until GitHub's
+# 2,500-comment cap closed it to comments; tvofi, 2026-11-09, ruled "Yes" to a
+# continuation issue. #201's comments stay the record and are still read: a
+# reader of the record (a mandate, its revocation, a merge's line) reads every
+# issue in RECORD_ISSUES, oldest first; a writer posts to RECORD_ISSUE only.
+RECORD_ISSUES = (201, 3394)
+RECORD_ISSUE = RECORD_ISSUES[-1]
+
+
+def on_record_issue(comment) -> bool:
+    """Whether the API issue comment `comment` is on one of DEFAULT_REPO's
+    RECORD_ISSUES (a comment id is global, so its issue_url is what says)."""
+    url = str(comment.get("issue_url") or "")
+    return any(url.endswith(f"/repos/{DEFAULT_REPO}/issues/{n}") for n in RECORD_ISSUES)
 MANDATE_GRAMMAR = re.compile(
     rf"MANDATE: agents may approve as {OWNER_LOGIN}, scope (code-owned|budget-raise|all), "
     r"from (\S+) until (\S+)")
@@ -383,7 +397,7 @@ def revokes(body, cid) -> bool:
     alone to skip its thread read) and the id as a whole number, so a longer
     number that contains it names another comment. THE one revocation test:
     mandate_state judges the thread with it, and gh_comment.py refuses a post
-    or patch to #201 it holds for (triage P336), by importing it."""
+    or patch to a record issue it holds for (triage P336), by importing it."""
     body = body or ""
     return bool(MANDATE_REVOKED.search(body)) and re.search(rf"(?<!\d){cid}(?!\d)", body) is not None
 
@@ -395,12 +409,12 @@ def mandate_grant(comment):
 
 def revocable(comment, now) -> bool:
     """Whether a revocation naming `comment`'s id would void a grant that can
-    still bind at `now`: the owner's comment on the tracking issue, its first
+    still bind at `now`: the owner's comment on a record issue, its first
     line the grammar, its window not closed (an end that does not parse counts
     as open: guarding too much fails safe). gh_comment.py's guard reads it."""
     m = mandate_grant(comment)
     if not (m and _is_owner(comment.get("user"))
-            and str(comment.get("issue_url") or "").endswith(MANDATE_ISSUE_URL)):
+            and on_record_issue(comment)):
         return False
     end = _when(m.group(3))
     return end is None or end > now
@@ -427,8 +441,9 @@ def mandate_state(cid, comment, thread, at, at_repr, when="review",
     name = f"mandate {cid}"
     if comment is None:
         return False, f"{name} is not a comment that exists"
-    if not str(comment.get("issue_url") or "").endswith(MANDATE_ISSUE_URL):
-        return False, f"{name} is not a comment on {DEFAULT_REPO}#{MANDATE_ISSUE}"
+    if not on_record_issue(comment):
+        return False, (f"{name} is not a comment on {DEFAULT_REPO}'s record issues "
+                       f"({', '.join(f'#{n}' for n in RECORD_ISSUES)})")
     if not _is_owner(comment.get("user")):
         return False, (f"{name} was not written by {OWNER_LOGIN} (id {OWNER_ID}), "
                        "and only the owner grants a mandate")
@@ -658,7 +673,7 @@ def _reviews(repo: str, pr: str) -> list[dict]:
 
 
 def _mandate(repo: str, cid: int) -> tuple[dict | None, list[dict]]:
-    """The cited comment (None when the API answers 404) and the tracking
+    """The cited comment (None when the API answers 404) and every record
     issue's comments since it was written, where a revocation would be."""
     out = subprocess.run(["gh", "api", f"repos/{repo}/issues/comments/{cid}"],
                          capture_output=True, text=True)
@@ -667,15 +682,18 @@ def _mandate(repo: str, cid: int) -> tuple[dict | None, list[dict]]:
             return None, []
         raise RuntimeError(f"gh api exited {out.returncode}: {out.stderr.strip()}")
     comment = json.loads(out.stdout)
-    if not str(comment.get("issue_url") or "").endswith(MANDATE_ISSUE_URL):
+    if not on_record_issue(comment):
         return comment, []
-    out = subprocess.run(
-        ["gh", "api", "--paginate", "--slurp",
-         f"repos/{repo}/issues/{MANDATE_ISSUE}/comments?per_page=100&since={comment.get('created_at')}"],
-        capture_output=True, text=True)
-    if out.returncode != 0:
-        raise RuntimeError(f"gh api exited {out.returncode}: {out.stderr.strip()}")
-    return comment, [c for page in json.loads(out.stdout) for c in page]
+    thread = []
+    for n in RECORD_ISSUES:
+        out = subprocess.run(
+            ["gh", "api", "--paginate", "--slurp",
+             f"repos/{repo}/issues/{n}/comments?per_page=100&since={comment.get('created_at')}"],
+            capture_output=True, text=True)
+        if out.returncode != 0:
+            raise RuntimeError(f"gh api exited {out.returncode}: {out.stderr.strip()}")
+        thread += [c for page in json.loads(out.stdout) for c in page]
+    return comment, thread
 
 
 def _body(repo: str, pr: str) -> str:
@@ -1001,7 +1019,7 @@ def self_test() -> int:
 
     # The owner's recorded mandate (tvofi, 2026-10-02): an agent's review under
     # the owner's account, declared as such, is decisive when it cites a
-    # MANDATE comment tvofi wrote on #201 that covers budget raises and was in
+    # MANDATE comment tvofi wrote on a record issue that covers budget raises and was in
     # force when the review was submitted. Each refusal arm below has a passing
     # neighbour that differs from it in the one field the arm reads.
     MID, RID = 4100000001, 4100000002
@@ -1009,7 +1027,7 @@ def self_test() -> int:
             "from 2026-10-02T06:00Z until 2026-10-03T06:00Z")
 
     def mandate(body=MAND, user=own, created="2026-10-02T05:30:00Z", updated=None,
-                issue=MANDATE_ISSUE, cid=MID) -> dict:
+                issue=RECORD_ISSUE, cid=MID) -> dict:
         return {"id": cid, "user": user, "body": body, "created_at": created,
                 "updated_at": updated or created,
                 "issue_url": f"https://api.github.com/repos/{DEFAULT_REPO}/issues/{issue}"}
@@ -1017,7 +1035,7 @@ def self_test() -> int:
     def revoke(cid=MID, user=own, rid=RID) -> dict:
         return {"id": rid, "user": user, "body": f"MANDATE REVOKED {cid}",
                 "created_at": "2026-10-02T08:00:00Z", "updated_at": "2026-10-02T08:00:00Z",
-                "issue_url": f"https://api.github.com/repos/{DEFAULT_REPO}/issues/{MANDATE_ISSUE}"}
+                "issue_url": f"https://api.github.com/repos/{DEFAULT_REPO}/issues/{RECORD_ISSUE}"}
 
     def agent(sha=H, at="2026-10-02T07:00:00Z", cite=f"mandate {MID}", state="APPROVED") -> dict:
         return {**rv(own, state, sha), "submitted_at": at,
@@ -1101,6 +1119,12 @@ def self_test() -> int:
           rcm([agent()], mandate(user={**own, "id": OWNER_ID + 1}))[0], 1)
     check("mandate: a mandate comment by the approver App fails", rcm([agent()], mandate(user=app))[0], 1)
     check("mandate: a mandate comment on another issue fails", rcm([agent()], mandate(issue=1838))[0], 1)
+    check("mandate: a mandate on #201, the record before the comment cap, still passes",
+          rcm([agent()], mandate(issue=201))[0], 0)
+    check("mandate: ... and a revocation on the continuation issue still voids it",
+          rcm([agent()], mandate(issue=201), thread=[revoke()])[0], 1)
+    check("mandate: the record issue is the last of RECORD_ISSUES, and #201 one of them",
+          (RECORD_ISSUE == RECORD_ISSUES[-1], 201 in RECORD_ISSUES, RECORD_ISSUE != 201), (True, True, True))
     check("mandate: a cited comment that does not exist fails", rcm([agent()], "missing")[0], 1)
     check("mandate: a mandate comment on #201 of another repository fails",
           rcm([agent()], {**mandate(), "issue_url": "https://api.github.com/repos/evil/other/issues/201"})[0], 1)
@@ -1450,17 +1474,17 @@ def _end_to_end() -> list[tuple[str, object, object]]:
         out.append(("e2e: a raise approved on the head, on the second page, exits 0", rc_, 0))
         rc_, _, _ = run(raise_, pages=[[approved(raise_)], [approved(fork)]])
         out.append(("e2e: a raise whose latest approval is stale exits 1", rc_, 1))
-        # The mandate, read live: the cited comment by id, then #201's comments
-        # since it was written, where a revocation would be.
+        # The mandate, read live: the cited comment by id, then every record
+        # issue's comments since it was written, where a revocation would be.
         cid = 4100000001
         mand = {"id": cid, "user": own, "created_at": "2026-10-02T05:30:00Z",
                 "updated_at": "2026-10-02T05:30:00Z",
-                "issue_url": f"https://api.github.com/repos/{DEFAULT_REPO}/issues/{MANDATE_ISSUE}",
+                "issue_url": f"https://api.github.com/repos/{DEFAULT_REPO}/issues/201",
                 "body": (f"MANDATE: agents may approve as {OWNER_LOGIN}, scope budget-raise, "
                          "from 2026-10-02T06:00Z until 2026-10-03T06:00Z")}
         agent_rv = {**approved(raise_), "id": 9, "submitted_at": "2026-10-02T07:00:00Z",
                     "body": f"Agent review under mandate {cid}.\n\n---\n_Generated by [Claude Code](https://claude.ai/code)_"}
-        thread_key = f"issues/{MANDATE_ISSUE}/comments"
+        thread_key = "/comments?per_page=100&since="   # every record issue's thread
         pr_key = f"=repos/{DEFAULT_REPO}/pulls/7"
         just = {"body": (f"## Summary\n\nx\n\n{JUSTIFICATION_HEADING}\n\nPayments tried: none improved it.\n"
                          "Architecture score: dS +0.0000 NULL\n")}
@@ -1469,10 +1493,11 @@ def _end_to_end() -> list[tuple[str, object, object]]:
                                        thread_key: {"out": [[]]}, pr_key: {"out": just}})
         out.append(("e2e: a raise approved at the head under a mandate in force exits 0",
                     (rc_, f"under mandate {cid}" in text), (0, True)))
-        out.append(("e2e: ... after reading the comment, #201 since it was written, then the body",
+        out.append(("e2e: ... after reading the comment, every record issue since it was written, then the body",
                     [c[-1] for c in calls][1:],
                     [f"repos/tvofi/heatpump_optimizer/issues/comments/{cid}",
-                     f"repos/tvofi/heatpump_optimizer/{thread_key}?per_page=100&since=2026-10-02T05:30:00Z",
+                     *(f"repos/tvofi/heatpump_optimizer/issues/{n}/comments?per_page=100&since=2026-10-02T05:30:00Z"
+                       for n in RECORD_ISSUES),
                      pr_key[1:]]))
         out.append(("e2e: ... after running the base's scorer three-dot, fork to head",
                     (open(argv_f).read() if os.path.exists(argv_f := os.path.join(stub, "score_argv")) else None),
diff --git a/tools/policy/policy_lint.mjs b/tools/policy/policy_lint.mjs
index ab4ade7c6..369c4903f 100644
--- a/tools/policy/policy_lint.mjs
+++ b/tools/policy/policy_lint.mjs
@@ -1971,7 +1971,7 @@ function resolvePrFromCommit(subject, rows) {
 
 // Where a disposition may live. CLAUDE.md's programme-tracking section names
 // exactly these two: the Delivery-status table in the plan of record, and the
-// living handover. #201 is deliberately NOT one of them -- it is the volatile
+// living handover. #3394 (#201 before it) is deliberately NOT one of them -- it is the volatile
 // half of the split, free to post at any moment and not in the tree, so a check
 // that accepted it would be satisfiable by something no later seat can read
 // from a checkout.
diff --git a/tools/pr/gh_comment.py b/tools/pr/gh_comment.py
index ef09c964b..c65c530f2 100755
--- a/tools/pr/gh_comment.py
+++ b/tools/pr/gh_comment.py
@@ -35,12 +35,16 @@ Usage:
   --withdraw-mandate CID on post/patch lets the body revoke mandate CID.
 
 THE MANDATE GUARD (triage P336, two instances). budget_raise_gate.py voids a
-mandate on any owner-account comment on #201 whose CURRENT body pairs a form
-of "revoke" with the mandate comment's id, so a seat's state comment naming a
-group whose name holds the word froze every mandated raise. A post or a patch
-to #201 is refused when budget_raise_gate.revokes() holds for the body and the
-id of a #201 comment budget_raise_gate.revocable() reads as a grant, unless
+mandate on any owner-account comment on a record issue (its RECORD_ISSUES:
+#201 and its continuation) whose CURRENT body pairs a form of "revoke" with
+the mandate comment's id, so a seat's state comment naming a group whose name
+holds the word froze every mandated raise. A post or a patch to a record issue
+is refused when budget_raise_gate.revokes() holds for the body and the id of a
+record-issue comment budget_raise_gate.revocable() reads as a grant, unless
 --withdraw-mandate names that id. Both predicates are imported, never copied.
+A post to a record issue other than RECORD_ISSUE is refused before any write:
+GitHub closed #201 to comments at its 2,500-comment cap, and the refusal names
+the issue to post to instead of a bare HTTP 403.
 THIS ENCODES A DESIGN CHOICE: it refuses whatever account posts, since the
 guard does not know which one gh holds and an agent's text is reworded at no
 cost. Stated gap: a raw `gh api` or `gh issue comment` bypasses it;
@@ -216,21 +220,30 @@ def mandate_guard(repo: str, body: str, withdraw, issue=None, comment=None,
     if repo.lower() != g.DEFAULT_REPO.lower() or not g.MANDATE_REVOKED.search(body):
         return
     if issue is not None:
-        on = issue == g.MANDATE_ISSUE
+        on = issue in g.RECORD_ISSUES
     else:
-        on = str(fetch(repo, comment).get("issue_url") or "").endswith(g.MANDATE_ISSUE_URL)
+        on = g.on_record_issue(fetch(repo, comment))
     if not on:
         return
     now = now or datetime.datetime.now(datetime.timezone.utc)
-    hit = sorted({c.get("id") for c in thread(repo, g.MANDATE_ISSUE)
+    hit = sorted({c.get("id") for n in g.RECORD_ISSUES for c in thread(repo, n)
                   if g.revocable(c, now) and g.revokes(body, c.get("id"))} - {withdraw})
     if hit:
-        die(f"on #{g.MANDATE_ISSUE} this body would void mandate comment(s) {', '.join(map(str, hit))}: "
+        die(f"on a record issue this body would void mandate comment(s) {', '.join(map(str, hit))}: "
             "budget_raise_gate.py reads an owner-account comment pairing the revocation word with a "
             "mandate's id as revoking it (triage P336). Reword it, or pass --withdraw-mandate <id> "
             "to withdraw that mandate on purpose")
 
 
+def closed_record_guard(repo: str, issue: int) -> None:
+    """Refuse a post to a record issue that is no longer RECORD_ISSUE (#201, at
+    GitHub's 2,500-comment cap), naming the issue the record continues in."""
+    g = _gate()
+    if repo.lower() == g.DEFAULT_REPO.lower() and issue in g.RECORD_ISSUES and issue != g.RECORD_ISSUE:
+        die(f"#{issue} is closed to comments (GitHub's 2,500-comment cap); the record continues "
+            f"in #{g.RECORD_ISSUE} (budget_raise_gate.RECORD_ISSUE): post there")
+
+
 def write(repo: str, endpoint: str, method: str, body: str) -> dict:
     """POST or PATCH a JSON payload. No field flag is composed anywhere here."""
     fd, payload = tempfile.mkstemp(suffix=".json", prefix="gh_comment_")
@@ -478,18 +491,20 @@ def self_test() -> int:
     # #3006's budget-raise-gate read as voiding the session mandate.
     g = _gate()
     owner = {"login": g.OWNER_LOGIN, "id": g.OWNER_ID, "type": g.OWNER_TYPE}
-    on201 = f"https://api.github.com/repos/{g.DEFAULT_REPO}/issues/{g.MANDATE_ISSUE}"
+    on201 = f"https://api.github.com/repos/{g.DEFAULT_REPO}/issues/201"
+    onrec = f"https://api.github.com/repos/{g.DEFAULT_REPO}/issues/{g.RECORD_ISSUE}"
 
-    def grant(cid, until="programme-end", user=owner):
-        return {"id": cid, "user": user, "issue_url": on201, "created_at": "2026-10-01T00:00:00Z",
+    def grant(cid, until="programme-end", user=owner, url=on201):
+        return {"id": cid, "user": user, "issue_url": url, "created_at": "2026-10-01T00:00:00Z",
                 "updated_at": "2026-10-01T00:00:00Z",
                 "body": f"MANDATE: agents may approve as {g.OWNER_LOGIN}, scope all, "
                         f"from 2026-10-01T00:00Z until {until}\nreason"}
-    BRIEF_ID, LIVE_ID, OLD_ID, ALIEN_ID = 6175172275, 6329234399, 6000000001, 6000000002
+    BRIEF_ID, LIVE_ID, OLD_ID, ALIEN_ID, NEW_ID = 6175172275, 6329234399, 6000000001, 6000000002, 6800000001
     THREAD = [grant(BRIEF_ID), grant(LIVE_ID), grant(OLD_ID, until="2026-10-02T00:00Z"),
               grant(ALIEN_ID, user={"login": "someone", "id": 1, "type": "User"}),
               {"id": 6545892934, "user": owner, "issue_url": on201, "body": "state comment"}]
-    targets = {111: {"id": 111, "issue_url": on201}, 222: {"id": 222, "issue_url": on201[:-3] + "7"}}
+    targets = {111: {"id": 111, "issue_url": on201}, 222: {"id": 222, "issue_url": on201[:-3] + "7"},
+               333: {"id": 333, "issue_url": onrec}}
     reads: list = []
 
     def fake_fetch(_repo, cid):
@@ -499,7 +514,7 @@ def self_test() -> int:
         reads.append(issue)
         if isinstance(THREAD_OVERRIDE[0], Exception):
             raise THREAD_OVERRIDE[0]
-        return THREAD
+        return THREAD if issue == 201 else [grant(NEW_ID, url=onrec)] if issue == g.RECORD_ISSUE else []
     THREAD_OVERRIDE: list = [None]
     FIELD = ("**Orchestrator s9: state since 6545892934 (2026-10-31, ~17:40Z)**\n\n"
              "- #3016 (R10-WOOD-NOTIFY): verdict merge at `9d304c2d`, with code-owner approval under mandate "
@@ -509,7 +524,7 @@ def self_test() -> int:
              "head, on the true figure. Round 2 also kills surviving mutant M6. The gate's value-blind dS check "
              "is carried to R10-FLY-MANDATE-REVOKE-GUARD.\n")
 
-    def guarded(name, text, *extra, target=("post", "--issue", "201"), repo=None):
+    def guarded(name, text, *extra, target=("post", "--issue", str(g.RECORD_ISSUE)), repo=None):
         """(refused, thread reads) for a dry-run post or patch of `text`."""
         reads.clear()
         f = wrote(f"seat/guard-{name}.md", text)
@@ -517,7 +532,7 @@ def self_test() -> int:
                                         "--body-file", f, "--dry-run", *extra],
                                        fetch=fake_fetch, thread=fake_thread))
         return hit, len(reads), msg
-    patch201, patch7 = ("patch", "--comment", "111"), ("patch", "--comment", "222")
+    patch201, patch7, patchrec = ("patch", "--comment", "111"), ("patch", "--comment", "222"), ("patch", "--comment", "333")
     BRIEF = f"decision 0012 is revoked; mandate {BRIEF_ID} still binds"
     hit, _, msg = guarded("brief", BRIEF)
     check("arm6_brief_row_refused_on_post", hit and str(BRIEF_ID) in msg and "--withdraw-mandate" in msg)
@@ -542,6 +557,19 @@ def self_test() -> int:
     check("arm6_an_expired_grant_is_not_guarded", not guarded("old", f"revoked {OLD_ID}")[0])
     check("arm6_a_grant_by_another_account_is_not_guarded", not guarded("alien", f"revoked {ALIEN_ID}")[0])
     check("arm6_a_comment_that_is_no_grant_is_not_guarded", not guarded("state", "revoked 6545892934")[0])
+    # The record moved to RECORD_ISSUE at #201's comment cap: a grant on either
+    # issue is guarded, read from every record issue's thread.
+    check("arm6_a_grant_on_the_continuation_issue_is_guarded",
+          (lambda h: h[0] and str(NEW_ID) in h[2] and h[1] == len(g.RECORD_ISSUES))(guarded("new", f"revoked {NEW_ID}")))
+    check("arm6_a_patch_on_the_continuation_issue_is_guarded", guarded("new-p", BRIEF, target=patchrec)[0])
+    check("arm6_record_issues_are_201_then_its_continuation",
+          g.RECORD_ISSUES[0] == 201 and g.RECORD_ISSUE == g.RECORD_ISSUES[-1] != 201)
+    hit, _, msg = guarded("old-issue", "plain text", target=("post", "--issue", "201"))
+    check("arm7_a_post_to_201_is_refused_naming_the_record_issue", hit and f"#{g.RECORD_ISSUE}" in msg)
+    check("arm7_a_post_to_201_of_another_repository_passes (null control)",
+          not guarded("old-repo", "plain text", target=("post", "--issue", "201"), repo="o/r")[0])
+    check("arm7_a_patch_of_a_201_comment_is_not_refused_by_it (edits still land)",
+          not guarded("old-p", "plain text", target=patch201)[0])
     THREAD_OVERRIDE[0] = Refused("gh exited 1: HTTP 502")
     check("arm6_a_thread_read_that_fails_refuses", guarded("fail", BRIEF)[0])
     THREAD_OVERRIDE[0] = None
@@ -570,7 +598,7 @@ def run(argv: list[str] | None = None, fetch=fetch_comment, thread=fetch_thread)
     p.add_argument("--dry-run", action="store_true",
                    help="post/patch: stop after the refusals, write nothing")
     p.add_argument("--withdraw-mandate", metavar="CID",
-                   help="post/patch to #201: the body may revoke the mandate comment CID")
+                   help="post/patch to a record issue: the body may revoke the mandate comment CID")
     a = p.parse_args(argv)
 
     if a.action == "self-test":
@@ -586,6 +614,8 @@ def run(argv: list[str] | None = None, fetch=fetch_comment, thread=fetch_thread)
         privacy_check(body)
         if a.action == "post" and not a.issue:
             die("post needs --issue")
+        if a.action == "post":
+            closed_record_guard(a.repo, positive_int(a.issue, "--issue"))
         if a.action == "patch" and not a.comment:
             die("patch needs --comment")
         mandate_guard(a.repo, body,

## Before you return the verdict (P275)
Run `python3 -I tools/audit/carry_audit.py check --body <PR body file> --comments <file holding [{"id": 0, "body": <verdict.md text>}]>`. Give every reported item its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>`;
an evidence line flagged by its wording takes `Carry: dismissed: evidence, not a finding`. Return the verdict only at rc 0.
