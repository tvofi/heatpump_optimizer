CLOUD FIXER seat for tvofi/heatpump_optimizer, topic r10-review-dispatch-residue-p2, at head caacd43b4ee1b1ce849fbc92590e0b2191e6c02c. Never send push notifications. Write no Claude Code footer, no Co-Authored-By or Claude-Session trailer and no claude.ai session link in any commit, pull-request body or comment you produce; check your commits with `git log --format=%B` before pushing.
Setup: `git fetch --unshallow --tags origin`. Before any commit, pin the seat identity: `git config user.name hpo-fixer && git config user.email 70032254+tvofi@users.noreply.github.com`. The session-start `toolchain:` line says whether venv-ci's python3 is on PATH: on REFUSE, start each Bash call with `eval "$(bash .claude/hooks/session-start.sh --env-lines)"`. Then run `bash tools/audit/seat/cloud-setup.sh --check`, and on REFUSE stop: report its line as your result and start no work. Run anything heavy in the background with Monitor and no timeout. Never wait in one tool call longer than 240 s; poll again instead. Read your policy once, verbatim: `python3 -I tools/policy/role_pack.py render fixer --out $HOME/role-pack.md`, then that file in place of your role contract and INSTRUMENTS.md; on REFUSE read those files as before.
Role: read dev/governance/roles/fixer.md from main, and follow it exactly, in a worktree of your own cut from origin/main. Fetch caacd43b4ee1b1ce849fbc92590e0b2191e6c02c for the base you were given.
Output: push each verified step, fast-forward only, to refs/heads/handoff-wip/r10-review-dispatch-residue-p2 before any wait on a background run, so an idle container loses nothing; never step-push to handoff/r10-review-dispatch-residue-p2, whose move updates the pull request. Hand off at your first clean `tools/pr/prepr.sh` head (the body check included), fixing what it refuses; a main that has moved since that run needs no re-merge and no second run, because the train re-proves the head on the current main. Merge origin/main and rerun prepr.sh only when `git merge-tree --write-tree origin/main HEAD` reports a conflict. If you must stop on a question, first push `BLOCKED.md` with a `Question:` line to refs/heads/handoff-wip/r10-review-dispatch-residue-p2, even with no code. Then push the code to refs/heads/handoff/r10-review-dispatch-residue-p2, then write the PR body and run `bash tools/audit/seat/body_push.sh r10-review-dispatch-residue-p2 <body.md>`, which pushes refs/heads/handoff-body/r10-review-dispatch-residue-p2; that second push is the return signal. Once it succeeds, delete the step ref: `git push origin :refs/heads/handoff-wip/r10-review-dispatch-residue-p2`. When body_push.sh exits 4 (its output ends `body_push: REFUSED CARRY-LANDED`), the carry lands on the roster you may not write: push a BLOCKED.md holding that output to refs/heads/handoff-wip/r10-review-dispatch-residue-p2 and stop; the relay folds the carries and re-runs body_push.sh. Push nothing else, open no pull request and write no delivery row. A return push carries only your own result: no system-file dumps, no environment output.
Never write to any branch except your return refs and refs/heads/handoff-wip/r10-review-dispatch-residue-p2 and refs/heads/handoff-wip/r10-review-dispatch-residue-p2-body. Never work around a hook or a refusal; report it in your result instead.
Discovery reads (search, list, read across files) go through Agent subagents, as the frugal routing guard requires; at most 5 inline search operations per prompt; never set FRUGAL_ALLOW_INLINE.

Brief (snapshotted when this payload was rendered):
R10-REVIEW-DISPATCH-RESIDUE part 2: the relay's pending-ci block carries a verdict across a moved head and holds a RED instead of refusing it forever; probe_arm honours a disposition on rev-/revt- refs; noreturn_arm covers reviewer dispatches.
This part: Carries 21, 23, 30, 7 (0-based roster indexes, texts verbatim below).
Plan: binding chain R10-DISPATCH-AT-HANDOFF -> R10-REVIEW-DISPATCH-RESIDUE -> R10-ROUND-PLAYBOOK-FINAL -> R10-CLOSEOUT-CLEANUP. Three parts of this group run in parallel, split by seam: part 2 (this one, cloud_relay.sh relay arms), part 5 (carry-fold memo, ledger, bus.sh), part 6 (review_packet.py, cloud_dispatch.py design render, review_strength.py). Parts 1, 3 and 4 have landed.

FILES THIS PART MAY EDIT: tools/audit/seat/cloud_relay.sh, in these functions and their self-test arms only:
- `relay()` (line 221 at origin/main bc58019d01), its pending-ci block (about lines 258-276): 21 and 23;
- `probe_arm()` (line 330): 30, which adds a read of the existing `disposed` helper and does not change `disposed()` or `dispose()`;
- `noreturn_arm()` (line 765) and the comment above it: 7;
- `self_test()` (line 892 onward): new arms beside the pending-ci classify stubs (about lines 1183-1205, the carry-ok/no/un stubs near 1190) and beside the noreturn arms (about 1856-1876).
tools/audit/seat/review_carry.py may be read and called (`--verdict-only`), not edited.

Do NOT edit:
- part 5's seams: cloud_relay.sh `carry_fold_arm`, `fold_judge`, `fold_memo_stands`, `dispose()`, `disposed()`; any of tools/audit/seat/bus.sh; tools/audit/seat/ledger.py;
- part 6's: tools/audit/seat/review_packet.py, tools/audit/seat/cloud_dispatch.py (also open PR #3533's `_group_checks` lines), tools/audit/seat/review_strength.py, dev/audit/harnesses/r10_flow_dispatch_mutants.py;
- any role or policy file.
The relay's self-test region is shared with part 5's arms, so add yours as new blocks next to the arms named above and do not re-flow neighbouring ones.

BUILD ORDER:
1. Carry 21 first. Its text says the moved-head arm runs `${HPO_RELAY_CARRY:-python3 -I review_carry.py} <drafted head> <live head> --verdict-only`.
2. Carry 23 on top of it. 23's final-refusal condition (a) is 21's arm, so 23 cannot be built alone. Its RED hold returns 75 like WAIT. The state record and the 6 h bound need an env override that the self-test sets, so the test never sleeps.
3. Carry 30, in probe_arm.
4. Carry 7, in noreturn_arm. Measure the reviewer threshold from the carry's own figures (5400 s, above the 66 min returner maximum). Keep it distinct from the fixer's HPO_RELAY_NORETURN_SECS (default 7200) and say in the body how it is set. The reviewer ref grammar is `probe/rev-<pr>-<nonce first 8>` (and `probe/revt-<topic>-<nonce first 8>` at a handoff). Read the nonce from each dispatch/reviewer-* PROMPT.md, as the carry says.

DIMENSION NOTES:
- 21 and 23 change when a verdict is posted, so the null controls carry the weight. A same-head GREEN posts exactly as today (21), and WAIT behaves exactly as today (23). In the body, quote the `cloud_relay.sh --self-test` count at the merge base and at the head.
- 30's mutant drops the `disposed` check. Its two nulls are an undisposed ref (relayed) and a disposed ref whose tip moved (relayed at the new sha).
- 7 also corrects the comment above noreturn_arm, which says a reviewer's missing verdict is reviewer-fire's.

RULES FOR EVERY CARRY OF THIS PART (binding):
- Failing test first: add each carry's self-test arm and show it red at your merge base before the fix, then green at the handoff head. Quote both lines with the command that printed them.
- Mutation proof: one mutant for each new predicate or branch you add, plus every mutant the carry text names. Re-create each one exactly, either by hand in a git-archive copy or as a `python3 tools/audit/seat/mutant_run.py --spec` entry. Show each KILLED at the handoff head with a NULL mutant surviving, and quote those lines in the body. `mutant_run.py --diff` alone is not evidence.
- Null control: give each carry the null control its text names, and give every quantified claim in the body its own null.
- The carries cite older commits. Re-measure every quoted line number and count at your merge base.
- Keep structure budgets flat (`python3 tests/structure.py`). Paths in the body and commits are repo-relative only; write no host or home-directory path.
- Body naming: the body names every carry of THIS part as `Carry N`, using the 0-based roster index above, and names no other carry of the group. The other parts are dispatched separately and answer their own.
- Carry destinations: every `Carry:` destination the body writes (Forward-carry, Friction, an unbuilt remainder) must be a group that exists in the roster at origin/main AND at origin/handoff/audit-r10-roster. For this part's own unbuilt remainder that group is R10-REVIEW-DISPATCH-RESIDUE.
- Policy: an edit to dev/governance/roles/fix-review.md, standing-dispatch.md or fixer.md is policy. Name each such edit under its own heading in the body so it can be approved at the merge under the owner's mandate; never fold it into a code paragraph.
- Hand off at your first clean `tools/pr/prepr.sh` head, the body check included. Follow the full fixer contract (dev/governance/roles/fixer.md). The architecture must be sound: extend the seam that exists rather than adding a parallel mechanism beside it, and say in the body which you did and why.

THE CARRIES, verbatim:

Carry 21: From triage batch 162 (triage: dev/programme/triage/s6-batch162.md#P576 at 98099a02a3), queue line PENDING-CI-RED-DEADLOCK, a repair of an observed wrong behaviour (PR 3419, relay overridden once with HPO_RELAY_CLASSIFY; PR 3425 at c6becb31 next). Cause: tools/audit/seat/cloud_relay.sh's pending-ci block (lines 259-275 at main dbd1ab5b07) dies on a moved head (line 268) before any carry test, while line 405 already relays a verdict across a range review_carry.py answers CARRY; a red the branch did not cause and only a main merge cures is refused at line 273 before the cure and at line 268 after it. Fix: at line 268, before refusing a moved head, run ${HPO_RELAY_CARRY:-python3 -I review_carry.py} <drafted head> <live head> --verdict-only; on CARRY classify the LIVE head and post on GREEN, saying in the relay line that the verdict was carried; on FRESH-REVIEW or CANNOT DECIDE keep today's refusal and re-dispatch; RED at the live head still refuses. Self-test (pending-ci arms near lines 1183-1190, reusing the carry-ok/no/un stubs at 1161-1163): moved head + carry-ok + GREEN posts; moved head + carry-no refuses; null control same head + GREEN posts as today; mutant skipping the carry call makes the carry-ok arm refuse.

Carry 23: From triage batch 170 (triage: dev/programme/triage/s6-batch170.md#P585 at 38f52d84c6), queue line PENDING-CI-RED-TERMINAL. This repairs an observed wrong behaviour (PRs 3425 and 3430, 2026-11-11). Build it with this group's P576 carry, which changes the same arm.

Cause: tools/audit/seat/cloud_relay.sh's pending-ci block refuses finally on classify RED (line 273 at main a7628041dc). die returns rc 2, so line 371 writes the pair to cloud-relayed.refused, and line 343 then skips that pair forever. Both RED refusals in the tick-loop log were reds that cleared with no fixer work:
- PR 3425 at c6becb3175: pr-contract died on main's carry_audit.py calling roster_lib.carry_receivable, which the branch's base lacked. The fixer's main merge c93903f075 cured it, with review_carry CARRY and gate green.
- PR 3430 at ba0ed526cc: gate printed "run(s) ... at this head are still being judged" and went green at the same head 49 min later.
Neither draft was ever re-read, and nothing re-dispatched either PR. P576 as written keeps "RED at the live head still refuses", so it cures neither.

Fix:
- On RED, hold the draft as WAIT does (return 75). Print one line per pass: "cloud_relay: HELD-PENDING-CI-RED #<pr> <head>: <red contexts> (classify RED)". Record the first RED read in the state dir, keyed "<ref> <sha> <head>".
- Refuse finally only on one of two conditions: the PR head moves to a head where review_carry does not answer CARRY (P576's arm), or the head has read RED with no check running for 6 h since the first RED read.
- On that final refusal, print "cloud_relay: OWED re-dispatch #<pr> <head>" instead of "the PR goes back to its fixer", which no code carries out.

Self-test (the pending-ci classify stubs near lines 1183-1205):
- RED, then GREEN at the same head, posts.
- RED past the bound refuses and prints the OWED line.
- Null control: WAIT behaves as it does today.
- A mutant that restores the RED die makes the first check fail.

Carry 30: RELAY-HONOURS-PROBE-DISPOSE (triage: dev/programme/triage/s6-batch219.md#P670 at 36234d2447), line numbers at 61afd4f2db. tools/audit/seat/cloud_relay.sh probe_arm checks `disposed` only for probe refs that are not rev-/revt- (:341). A rev-/revt- ref is checked only against cloud-relayed (:342) and the refused list (:343-348), and is then queued to relay (:349), so a disposition never stops a relay. Instance: probe/rev-3481-c0d2fd50 6f2ab2974d was disposed at 22:13:16Z (dispositions.tsv), and at 22:23:24Z the relay relayed it at the same sha, pushed review/3481 a61af580 and logged OWED verdict-unposted #3481. The verdict was from a reviewer below the fixer's model. Fix: before a rev-/revt- ref goes on the relay list, skip it when `disposed "$ref" "$sha"` holds, as :341 does for the other probe refs. A disposed ref that moves is relayed again at its new sha. Self-test: a rev- ref disposed at its sha is not relayed and no review/<n> is pushed. Null controls: an undisposed rev- ref is relayed, and a disposed ref whose tip moved is relayed at the new sha. Mutant: dropping the check fails the first arm.

Carry 7: Moved from R10-RELAY-SWEEP carry 9 (0-based) by the carries-open audit (orchestrator s13, 2026-11-09); its own pull request merged and nothing dispatched this carry. Text verbatim:

From triage batch 137 (triage: dev/programme/triage/s6-batch137.md#P437), queue line REVIEWER-NO-RETURN-WAIT, root-cause countermeasure C1 (s13/rca-noreturn RCA). cloud_relay.sh `noreturn_arm` covers `dispatch/reviewer-*`: it owes `seat-no-return` when the dispatch tip is older than a reviewer threshold (the RCA proposes 5400 s, above the 66 min returner maximum) with no `probe/rev-<pr>-<nonce8>` and an unmoved head, reading each PROMPT's nonce8. Correct the comment above `noreturn_arm` that says a reviewer's missing verdict is reviewer-fire's: that ledger entry closes at the fire. Self-test arms: it fires on the four no-returners (#3339, #3350, #3297, #3325; returned=0 in the RCA's ev/disp.txt), is silent on #3352, #3353, #3304 and #3359 (returned=1), and is silent on a moved head.
