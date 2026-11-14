CLOUD REVIEWER seat for PR #3544 of tvofi/heatpump_optimizer, at head a60a65d87376397adc098cbf2b7b2377ccaeca02. Bus nonce: 91e4ef1c8e645e1e33000f667e60fa85. Never send push notifications. Write no Claude Code footer, no Co-Authored-By or Claude-Session trailer and no claude.ai session link in any commit, pull-request body or comment you produce; check your commits with `git log --format=%B` before pushing.
Setup: `git fetch --unshallow --tags origin`. The session-start `toolchain:` line says whether venv-ci's python3 is on PATH: on REFUSE, start each Bash call with `eval "$(bash .claude/hooks/session-start.sh --env-lines)"`. Then run `bash tools/audit/seat/cloud-setup.sh --check`, and on REFUSE stop: report its line as your result and start no work. Run anything heavy in the background with Monitor and no timeout. Never wait in one tool call longer than 240 s; poll again instead. Read your policy once, verbatim: `python3 -I tools/policy/role_pack.py render fix-review --out $HOME/role-pack.md`, then that file in place of your role contract and INSTRUMENTS.md; on REFUSE read those files as before.
Role: read dev/governance/roles/fix-review.md and its rules from main, and follow them exactly. Fetch the PR head with `git fetch origin a60a65d87376397adc098cbf2b7b2377ccaeca02`; the PR body is in the PR. Start from the review packet, which you render here rather than read from the dispatcher, whose copy is a path on its own machine: `python3 -I tools/audit/seat/review_packet.py render --pr 3544 --head a60a65d87376397adc098cbf2b7b2377ccaeca02 --reviewed-head a60a65d87376397adc098cbf2b7b2377ccaeca02 --out $HOME/review-packet.md`. A refusal names its signal and the packet is still written unless the signal is `host-path`; re-read the live checks either way. This is a later round over the reviewed head a60a65d87376397adc098cbf2b7b2377ccaeca02: its scope is the packet's `## Review scope` line, the delta and the previous verdict's findings when it reads `delta`, widened only to the exact already-reviewed code a production (custom_components/) delta puts at non-obvious risk that CI would not detect, the verdict naming path and risk; an instrument, test, policy or body delta never widens it (fix-review.md step 12). Verify each claim adversarially: mutate the fix and check the tests fail, and check every figure in the body at this head. Check that it merges with origin/main (`git merge-tree --write-tree origin/main <head>`); block on main only when that reports a conflict, never on a head that is behind main but merges cleanly (the train re-proves it on the current main). Wait for CI on this head only by re-running `python3 tools/audit/seat/merge_train.py classify a60a65d87376397adc098cbf2b7b2377ccaeca02 --pr 3544` in the background, at least 60 s between runs, until it exits 0 (GREEN), 1 (RED), 2 (unreadable: say so in the verdict) or 4 (APPROVAL-OWED: the only red is the budget raise's approval, which follows your verdict; judge the head as GREEN and quote the line); 3 is WAIT, so run it again. Never wait with `pgrep` or `pkill`, whose `-f` pattern matches the waiter's own command line, nor on a context the ruleset does not require, such as `prelude`. A review_packet `required-red` signal does not stop you while classify prints WAIT: classify decides. If your review is otherwise complete and classify still prints WAIT after about 30 minutes of polling, stop waiting: put the line `pending-ci: <the context names it printed>` straight after the `bus-nonce:` line and return the verdict as below; the relay posts it once CI is green at this head, refuses it over a red, and refuses it if the head moves. If the review is not complete then, push `Fix review: blocked a60a65d87376397adc098cbf2b7b2377ccaeca02 ci-wait: <the last classify line>` as below.
Output: in a fresh directory of your own (`W=$(mktemp -d)`), write verdict.md, whose first line is exactly `Fix review: merge a60a65d87376397adc098cbf2b7b2377ccaeca02` or `Fix review: blocked a60a65d87376397adc098cbf2b7b2377ccaeca02 <class>: <reason>` (no brackets; the class is lower-case letters and dashes), in the format the role file gives, then a blank line, then `bus-nonce: 91e4ef1c8e645e1e33000f667e60fa85`, then the body in sections. A blocked verdict's block goes under `## Block`. Each finding this PR does not settle (a defect, a surviving mutant, a deferral, a follow-up, a task owed after the merge) is its own bullet under `## Findings` ending in its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>` (finding-propagation.md). Everything else (RESULT lines, re-runs, CI state, figures you could not re-derive) goes under `## Evidence`: tools/audit/carry_audit.py reads an item there, and under any heading of a merge verdict but `## Findings`, `## Friction`, a block heading and a note heading (Residuals, Follow-ups, Notes ...), by its shape alone: a finding only when it opens with a lead word (Residual:, Follow-up:, Out of scope: ...) or carries a `Carry:`, so a defect you hand on goes under `## Findings`, and bus.sh refuses a verdict holding a finding with no valid `Carry:`. Put the evidence files in `ev/` beside it, under 25 MB in all (cite a large log by path and keep its tail: a ~30 MB ev/ once failed its push), and make at least one file under `ev/` contain the full 40-hex head `a60a65d87376397adc098cbf2b7b2377ccaeca02` (e.g. `ev/HEAD.txt` holding the head you reviewed, beside your command output): bus.sh refuses a verdict whose `ev/` names no head. Do NOT run bus.sh: its dispatch record lives on the orchestrator's machine, which publishes the verdict there (cloud_relay.sh). Return the verdict on a probe ref, and push nothing else; this builds one parentless commit with a private index and touches no branch of your checkout: `R=$(git rev-parse --show-toplevel); G=$(git rev-parse --absolute-git-dir); mkdir -p $W/pr && cp -r $W/verdict.md $W/ev $W/pr/ && cd $W/pr && T=$(GIT_DIR=$G GIT_INDEX_FILE=$W/idx GIT_WORK_TREE=$W/pr sh -c 'git add -A -f . && git write-tree') && C=$(GIT_DIR=$G git -c user.name=hpo-fixer -c user.email=70032254+tvofi@users.noreply.github.com commit-tree $T -m "verdict 3544 a60a65d87376397adc098cbf2b7b2377ccaeca02") && git -C $R push -q origin $C:refs/heads/probe/rev-3544-91e4ef1c`. That ref is the return signal. Do not post comments, approve or merge.
Every way your turn ends pushes a verdict to that ref: a setup or hook refusal that stops you pushes `Fix review: blocked a60a65d87376397adc098cbf2b7b2377ccaeca02 seat-refused: <the refusing line>`; never end your turn while a background poll runs. After the push, read the ref back with `git ls-remote origin refs/heads/probe/rev-3544-91e4ef1c`, and push again if it does not print your commit.
A red is owed a `## Red checks` answer, and may block, only when its name is in the set `python3 tools/audit/seat/merge_train.py owed-reds` prints (defect-root-cause.md); any other red is neither answered nor a block.
Never write to any branch except your return refs. Never work around a hook or a refusal; report it in your result instead.
Discovery reads (search, list, read across files) go through Agent subagents, as the frugal routing guard requires: when it refuses inline work, dispatch a haiku or sonnet Agent subagent to do it rather than bypassing the guard; never set FRUGAL_ALLOW_INLINE and never edit .claude/settings.json.

Brief (snapshotted when this payload was rendered):
# Review packet #3544
head: a60a65d87376397adc098cbf2b7b2377ccaeca02
base: e23124ff6e45bac1d48b4a775dad555a37965355

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: pending
.github/dependabot.yml id=132185490093 success
CodeQL id=132185953595 success
arch-score / arch-score id=132250408677 success
arm id=132185509157 skipped
budget-raise-gate / budget-raise-gate id=132250359978 success
cancel-superseded id=132250401019 success
codeql id=132250359629 skipped
codeql / Analyze (actions) id=132250336302 success
codeql / Analyze (javascript-typescript) id=132250337104 success
codeql / Analyze (python) id=132250336102 success
gate id=132250358751 in_progress
governance id=132250423624 skipped
governance / delivery-status id=132250336038 success
governance / delivery-status-publish id=132250341221 skipped
governance / env-matrix id=132250395021 success
governance / instrument-self-tests id=132250370014 success
governance / policy-docs id=132250336076 success
governance / record id=132250337270 skipped
governance / wave-script id=132250336048 success
hassfest id=132250418423 skipped
hassfest / hassfest id=132250380887 success
kernel-points id=132250410431 skipped
pr-contract id=132250360765 skipped
pr-contract / pr-contract id=132250339846 success
prelude id=132250359164 success
refresh id=132250392506 success
tests id=132250411388 skipped
tests / arch-instrument id=132250337127 success
tests / briefs id=132250387122 success
tests / browser id=132250337810 success
tests / ci-ratchet id=132250339011 skipped
tests / claims-autofix id=132250338182 skipped
tests / closure-scope id=132250336497 success
tests / closures id=132250336889 success
tests / closures-autofix id=132250338069 skipped
tests / coverage id=132250336568 success
tests / coverage-ratchet id=132250337894 success
tests / fast (3.14) id=132250336688 success
tests / graders-head-copy id=132250338100 success
tests / lane-proofs id=132250338950 success
tests / mutation id=132250375125 success
tests / mutation-autofix id=132250338142 skipped
tests / mutation-pins id=132250337105 skipped
tests / nightly-ha id=132250337763 skipped
tests / nightly-status id=132250396760 success
tests / replay id=132250337268 skipped
tests / typing id=132250336740 success
validate id=132250423159 skipped
validate / validate-hacs id=132250336809 success

## Refusals
none

## Advisories
hot-file: HPO_BUS_TRAIN_STATE is unset, so every merge verdict reads unboarded

## carry_audit at the head
CARRY-AUDIT: 0 finding item(s): 0 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
ok         node tools/policy/policy_lint.mjs
             `tools/policy/policy_lint.mjs` is in the tree at this head
  unverified git merge-tree --write-tree origin/main 8382e2aa25
             `git merge-tree` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  unverified git merge origin/main
             `git merge` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  ok         node tools/policy/brief_lint.mjs
             `tools/policy/brief_lint.mjs` is in the tree at this head
  ok         bash tools/pr/prepr.sh
             `tools/pr/prepr.sh` is in the tree at this head

FIGURES: 3 resolved, 2 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
none

## Review scope: delta (later round over the reviewed head a60a65d87376397adc098cbf2b7b2377ccaeca02)
Confirm each finding of the previous verdict is resolved, re-read the live required checks, and review the delta below. Widen only to exactly the already-reviewed code a delta touching production code (custom_components/) puts at risk of being affected in a non-obvious way CI would not detect, naming the path and the risk in the verdict; an instrument, test, policy or body delta never justifies a wider review (fix-review.md step 12).

## Previous verdict at a60a65d87376397adc098cbf2b7b2377ccaeca02
Fix review: blocked a60a65d87376397adc098cbf2b7b2377ccaeca02 body: the Null control quotes the cloud_relay self-test as 465 checks at this head, which prints 501

bus-nonce: 41c4643bafddfb0eb74e5513f05f272b

Round: third review (round 3) of #3544. This is a delta review over the blocked head 8382e2aa25cab7c82b6e6ce8e5059412d5e970c3, at head a60a65d87376397adc098cbf2b7b2377ccaeca02.

## Block

1. body: the PR body says "All measurements below are at the head given below". Its `## Null control` then states that at this head `bash tools/audit/seat/cloud_relay.sh --self-test` printed `cloud_relay self-test: 465 checks, 0 failed`. At a60a65d873 that command prints `cloud_relay self-test: 501 checks, 0 failed`, rc 0 (ev/selftest-relay.txt). Control: at the previously reviewed head 8382e2aa25 the same command prints `465 checks, 0 failed` (ev/selftest-relay-at-8382e2aa25.txt). So the figure was carried from that head and not re-taken after the main merge. Main's bdf1dc827e and 7d09eae1ba, which the merge brings in, add the 36 checks (ev/delta.txt). The fix is a body edit and no code change: re-take the figure at this head, or scope it to the head where it was taken. This is a mechanical class (`body`) and owes no re-cut. The bus (202) and ledger (103) counts re-derive exactly at this head (ev/selftest-bus.txt, ev/selftest-ledger.txt).

The previous block is resolved (see Evidence). Nothing else blocks.

## Findings

none

## Evidence

- Head: ev/HEAD.txt holds a60a65d87376397adc098cbf2b7b2377ccaeca02, the head the dispatch names. The body's `## Head` names it, merging the authored head 440ae4033125.
- Scope is delta, per the packet's `## Review scope` line. The delta 8382e2aa25..a60a65d873 is a merge of origin/main e23124ff6e and nothing else. The PR's three-dot diff against the new base is identical to its three-dot diff at 8382e2aa25 against the old base 0723540391, once index and hunk-header lines are stripped: 5 files, +202/-36. Neither merge has a resolution of its own: `git show --remerge-diff` prints nothing for 440ae40331 or a60a65d873, and their trees are equal (ev/delta.txt). The delta adds no PR-authored `custom_components/` change, so the scope is not widened.
- The previous block (red-unanswered: `tests / briefs`) is resolved. The body's `## Red checks` now names `tests / briefs` and answers it. Its claim checks out: d65839f2e2 and b4a663ebe5 are not ancestors of 8382e2aa25 and are ancestors of this head (`git merge-base --is-ancestor`). `node tools/policy/brief_lint.mjs` at this head exits 0 with no VACUOUS line (ev/brief-lint-head.txt).
- `node tools/policy/policy_lint.mjs` at this head prints `TOTAL: 0 error(s) across 51 policy file(s)`, rc 0 (ev/policy-lint-head.txt).
- Self-tests at this head, in a detached worktree: bus 202 checks / 0 failed, ledger 103 / 0, cloud_relay 501 / 0. All three are rc 0.
- Merge with main: `git merge-tree --write-tree origin/main a60a65d873` prints one tree, rc 0 (ev/merge-tree.txt). origin/main is e23124ff6e, the merge base. `git diff $(merge-base)...origin/main -- dev/governance/roles/` is empty, so the contract is current.
- VERSION, the manifest version, RELEASE_NOTES.md and tests/golden are untouched on the three-dot range against e23124ff6e (ev/delta.txt).
- Mutation: the PR's patch is unchanged from 8382e2aa25, where round 2 re-ran every production mutant KILLED with NULL SURVIVED. The merge adds no PR-authored line, so no mutant was re-run.
- CI: `merge_train.py classify a60a65d873 --pr 3544` read WAIT on all 7 polls, from 21:43:38Z to 21:51:22Z (`pending: gate red: none`; ev/classify.txt). This block is a body edit, which does not move the head, so CI was not waited out. The next round re-reads the live checks, including the packet's `introduced-red` refusal on the still-running `governance / instrument-self-tests` (ev/review-packet.md). The owed-reds set is in ev/owed-reds.txt.

## Delta diff: git diff a60a65d87376397adc098cbf2b7b2377ccaeca02 a60a65d87376397adc098cbf2b7b2377ccaeca02

## Before you return the verdict (P275)
Run `python3 -I tools/audit/carry_audit.py check --body <PR body file> --comments <file holding [{"id": 0, "body": <verdict.md text>}]>`. Give every reported item its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>`;
an evidence line flagged by its wording takes `Carry: dismissed: evidence, not a finding`. Return the verdict only at rc 0.
