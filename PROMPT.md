CLOUD REVIEWER seat for PR #3570 of tvofi/heatpump_optimizer, at head b56f703837126d8e20d1af7f75339ed58189ce3a. Bus nonce: aeba9c83f42ab7f673cc5ba648b71533. Never send push notifications. Write no Claude Code footer, no Co-Authored-By or Claude-Session trailer and no claude.ai session link in any commit, pull-request body or comment you produce; check your commits with `git log --format=%B` before pushing.
Setup: `git fetch --unshallow --tags origin`. The session-start `toolchain:` line says whether venv-ci's python3 is on PATH: on REFUSE, start each Bash call with `eval "$(bash .claude/hooks/session-start.sh --env-lines)"`. Then run `bash tools/audit/seat/cloud-setup.sh --check`, and on REFUSE stop: report its line as your result and start no work. Run anything heavy in the background with Monitor and no timeout. Never wait in one tool call longer than 240 s; poll again instead. Read your policy once, verbatim: `python3 -I tools/policy/role_pack.py render fix-review --out $HOME/role-pack.md`, then that file in place of your role contract and INSTRUMENTS.md; on REFUSE read those files as before.
Role: read dev/governance/roles/fix-review.md and its rules from main, and follow them exactly. Fetch the PR head with `git fetch origin b56f703837126d8e20d1af7f75339ed58189ce3a`; the PR body is in the PR. Start from the review packet, which you render here rather than read from the dispatcher, whose copy is a path on its own machine: `python3 -I tools/audit/seat/review_packet.py render --pr 3570 --head b56f703837126d8e20d1af7f75339ed58189ce3a --out $HOME/review-packet.md`. A refusal names its signal and the packet is still written unless the signal is `host-path`; re-read the live checks either way. Verify each claim adversarially: mutate the fix and check the tests fail, and check every figure in the body at this head. Check that it merges with origin/main (`git merge-tree --write-tree origin/main <head>`); block on main only when that reports a conflict, never on a head that is behind main but merges cleanly (the train re-proves it on the current main). Wait for CI on this head only by re-running `python3 tools/audit/seat/merge_train.py classify b56f703837126d8e20d1af7f75339ed58189ce3a --pr 3570` in the background, at least 60 s between runs, until it exits 0 (GREEN), 1 (RED), 2 (unreadable: say so in the verdict) or 4 (APPROVAL-OWED: the only red is the budget raise's approval, which follows your verdict; judge the head as GREEN and quote the line); 3 is WAIT, so run it again. Never wait with `pgrep` or `pkill`, whose `-f` pattern matches the waiter's own command line, nor on a context the ruleset does not require, such as `prelude`. A review_packet `required-red` signal does not stop you while classify prints WAIT: classify decides. If your review is otherwise complete and classify still prints WAIT after about 30 minutes of polling, stop waiting: put the line `pending-ci: <the context names it printed>` straight after the `bus-nonce:` line and return the verdict as below; the relay posts it once CI is green at this head, refuses it over a red, and refuses it if the head moves. If the review is not complete then, push `Fix review: blocked b56f703837126d8e20d1af7f75339ed58189ce3a ci-wait: <the last classify line>` as below.
Output: in a fresh directory of your own (`W=$(mktemp -d)`), write verdict.md, whose first line is exactly `Fix review: merge b56f703837126d8e20d1af7f75339ed58189ce3a` or `Fix review: blocked b56f703837126d8e20d1af7f75339ed58189ce3a <class>: <reason>` (no brackets; the class is lower-case letters and dashes), in the format the role file gives, then a blank line, then `bus-nonce: aeba9c83f42ab7f673cc5ba648b71533`, then the body in sections. A blocked verdict's block goes under `## Block`. Each finding this PR does not settle (a defect, a surviving mutant, a deferral, a follow-up, a task owed after the merge) is its own bullet under `## Findings` ending in its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>` (finding-propagation.md). Everything else (RESULT lines, re-runs, CI state, figures you could not re-derive) goes under `## Evidence`: tools/audit/carry_audit.py reads an item there, and under any heading of a merge verdict but `## Findings`, `## Friction`, a block heading and a note heading (Residuals, Follow-ups, Notes ...), by its shape alone: a finding only when it opens with a lead word (Residual:, Follow-up:, Out of scope: ...) or carries a `Carry:`, so a defect you hand on goes under `## Findings`, and bus.sh refuses a verdict holding a finding with no valid `Carry:`. Put the evidence files in `ev/` beside it, under 25 MB in all (cite a large log by path and keep its tail: a ~30 MB ev/ once failed its push), and make at least one file under `ev/` contain the full 40-hex head `b56f703837126d8e20d1af7f75339ed58189ce3a` (e.g. `ev/HEAD.txt` holding the head you reviewed, beside your command output): bus.sh refuses a verdict whose `ev/` names no head. Do NOT run bus.sh: its dispatch record lives on the orchestrator's machine, which publishes the verdict there (cloud_relay.sh). Return the verdict on a probe ref, and push nothing else; this builds one parentless commit with a private index and touches no branch of your checkout: `R=$(git rev-parse --show-toplevel); G=$(git rev-parse --absolute-git-dir); mkdir -p $W/pr && cp -r $W/verdict.md $W/ev $W/pr/ && cd $W/pr && T=$(GIT_DIR=$G GIT_INDEX_FILE=$W/idx GIT_WORK_TREE=$W/pr sh -c 'git add -A -f . && git write-tree') && C=$(GIT_DIR=$G git -c user.name=hpo-fixer -c user.email=70032254+tvofi@users.noreply.github.com commit-tree $T -m "verdict 3570 b56f703837126d8e20d1af7f75339ed58189ce3a") && git -C $R push -q origin $C:refs/heads/probe/rev-3570-aeba9c83`. That ref is the return signal. Do not post comments, approve or merge.
Every way your turn ends pushes a verdict to that ref: a setup or hook refusal that stops you pushes `Fix review: blocked b56f703837126d8e20d1af7f75339ed58189ce3a seat-refused: <the refusing line>`; never end your turn while a background poll runs. After the push, read the ref back with `git ls-remote origin refs/heads/probe/rev-3570-aeba9c83`, and push again if it does not print your commit.
A red is owed a `## Red checks` answer, and may block, only when its name is in the set `python3 tools/audit/seat/merge_train.py owed-reds` prints (defect-root-cause.md); any other red is neither answered nor a block.
Never write to any branch except your return refs. Never work around a hook or a refusal; report it in your result instead.
Discovery reads (search, list, read across files) go through Agent subagents, as the frugal routing guard requires: when it refuses inline work, dispatch a haiku or sonnet Agent subagent to do it rather than bypassing the guard; never set FRUGAL_ALLOW_INLINE and never edit .claude/settings.json.

Brief (snapshotted when this payload was rendered):
# Review packet #3570
head: b56f703837126d8e20d1af7f75339ed58189ce3a
base: e23124ff6e45bac1d48b4a775dad555a37965355

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: pending
arm id=132208917690 skipped
cancel-superseded id=132208934082 queued
prelude id=132208934127 queued
refresh id=132208933740 queued

## Refusals
none

## Advisories
none

## carry_audit at the head
CARRY-AUDIT: 0 finding item(s): 0 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
ok         node tools/policy/brief_lint.mjs
             `tools/policy/brief_lint.mjs` is in the tree at this head

FIGURES: 1 resolved, 0 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
none

## Review scope: full (first round: no --reviewed-head)

## Three-dot diff
diff --git a/dev/programme/delivery/3570.md b/dev/programme/delivery/3570.md
new file mode 100644
index 0000000000..7513b65c09
--- /dev/null
+++ b/dev/programme/delivery/3570.md
@@ -0,0 +1 @@
+- [#3570](https://github.com/tvofi/heatpump_optimizer/pull/3570) — **open**, R10-CLOSEOUT-PREP (part 3): r10 closeout prep p3 (R10-CLOSEOUT-PREP)
diff --git a/tools/policy/brief_lint.mjs b/tools/policy/brief_lint.mjs
index 05198529c5..2a8c5e6754 100644
--- a/tools/policy/brief_lint.mjs
+++ b/tools/policy/brief_lint.mjs
@@ -1415,8 +1415,12 @@ function assertCarryControl() {
   }
   const good = carryControlFindings('dev/audit/harnesses/agreement_two_pr.mjs prints the count')
   if (good.length) problems.push(`a control naming an existing harness is refused (null control): ${good[0].message}`)
-  const legacy = carryControlFindings('the FUTURE-STATE section 2 figures', 'carry-201.json')
-  if (legacy.length) problems.push(`a legacy carry file is refused (the narrowing): ${legacy[0].message}`)
+  // The legacy example is read from the set, not named: the set only shrinks, and a
+  // named member that leaves it would turn this narrowing check into a refusal.
+  const member = [...LEGACY_CONTROL_FILES].sort()[0]
+  if (!member) problems.push('the legacy set is empty, so the narrowing is unexercised')
+  const legacy = member ? carryControlFindings('the FUTURE-STATE section 2 figures', member) : []
+  if (legacy.length) problems.push(`a legacy carry file (${member}) is refused (the narrowing): ${legacy[0].message}`)
   if (problems.length) {
     console.log('\nCONTROL VACUOUS: carry control:')
     for (const m of problems) console.log(`  ${m}`)

## Before you return the verdict (P275)
Run `python3 -I tools/audit/carry_audit.py check --body <PR body file> --comments <file holding [{"id": 0, "body": <verdict.md text>}]>`. Give every reported item its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>`;
an evidence line flagged by its wording takes `Carry: dismissed: evidence, not a finding`. Return the verdict only at rc 0.
