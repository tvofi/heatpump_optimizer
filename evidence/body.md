R10-FLOW-JIDOKA: error-proofing in `tools/pr/prepr.sh` before handoff. Refs #2428, the shared `carry-missing` friction issue. This pull request does not close it: R10-FLY-CARRY-DISPOSITION and R10-RCA-FRICTION-RESIDUE still hold it, and no roster group lists it under `fixes`.

- **Step 7e, the carry check.** The new function `carry_line` runs pr-contract's own checker, `python3 -I tools/audit/carry_audit.py --roster-ref <round ref> check --body <body>`. It runs on the body in full prepr (step 7) and in `--body-check`, which is the call `body_push.sh` makes at every handoff. No rule is added (decision 0012). Revision 8 sets the ref: `roster_lib.round_ref` names it (`origin/handoff/audit-r<N>-roster`), and the step fetches it before reading. With `--roster-ref`, carry_audit reads groups and carry files at that ref only. That is where fix-review step 10 looks, so a group that exists only in the worktree's roster, or only in a stale mirror, is refused. If the ref cannot be named or fetched, the step refuses rather than read the mirror. A design choice the reviewer should see: a group that is on main but not yet on the round branch is refused here, while pr-contract would pass it, because pr-contract also reads the tree's roster. Step 7e captures `carry_line`'s rc on the same line as the call (`CARRY_RC=$?`), and the self-test pins the call and the `step "carry"` line as adjacent.
- **Step 7's preflight derives the intended list as pr-contract does (round 2).** `preflight_body` runs `preflight.sh` with the list pr-contract.yml derives: closes minus never, where never is a roster `issues` number that no group names in `fixes`. `INTENDED_JQ` is pr-contract.yml's jq program, byte for byte, and a self-test row refuses when the two differ. Issue numbers passed after the body are now ignored, and the step names them in a `note` line. `--body-check` runs the same preflight, so `body_push.sh` refuses such a body at the handoff. Before this change, step 7 forwarded the caller's numbers, so round 1's `prepr.sh <body> 2428` passed a keyword on #2428 that pr-contract then refused.
- **Step 7c, the red-check arm: why it did not fire, and the gate fix.** The gate defect: 7c skipped whenever 7b's local mirror of the pull request's head ref was absent ("no $UPREF yet"). 7b never fetches, by design. A fixer pushes `handoff/<topic>` and never fetches the `fix/<topic>` head that `handoff_push.sh` opens. So the arm read nothing on revision rounds, even when earlier pushed heads already carried reds. 7c reads check runs over the network anyway, so it now gates on `reds_head_sha`, which fetches the ref first. An unfetchable ref is a skip, like every other unread 7c input. Two kinds of red are not this gate's to fix. A red that first appeared at the blocked head itself is one no pre-push read can see. pr-contract's own reds are excluded from 7c by design. Step 7e now catches the carry refusals among them, and step 7's derived preflight catches the closing-keyword refusals.
- **Heavy steps die with the prepr** (carried from #2528, R10-PREPR-CAP). Steps 3 to 3h used to run their programs in the foreground. A TERM to the prepr waited until the program exited, and a KILL left it running. A new helper, `heavy_run`, wraps 6b's existing recorder pattern: the program runs in its own process group (`set -m`), the prepr `wait`s on it, and a watchdog reaps the group once `$$` is gone. Every program in steps 3 to 3h now runs through it, and so does 6b's recorder.
- The ledger cites the class's second RCA. `dev/audit/config/bugclasses.json` gains the `_rca` entry `R10-RCA-BODY-CHECK-PARITY`, and `N-body-lint-bounce` lists it. `dev/governance/roles/fixer.md` step 5 and an `app_push.sh` comment no longer say that prepr omits the carry check. Two comments that said a seat states the intended list on prepr's command line now say step 7 derives it: one in `app_push.sh`'s header and one in `pr-contract.yml` above the derivation.

Alternatives considered:
- (a) Without `--roster-ref`, carry_audit unions the tree's roster with the round mirror. That is the offline read revision 8 names as the defect.
- (b) Make 7b fetch too. 7b's header argues "NO NETWORK, EVER". Only 7c reads the network, so only 7c fetches.
- (c) Background each heavy step by hand. That would be twelve copies of one pattern. `heavy_run` is the one owner.
- (d) For the intended list: refuse only a forwarded number the roster lists as never. That keeps a second, hand-typed input, which can still differ from CI's in the other direction, for example by omitting an unrostered issue. Deriving the list leaves one input, the one CI reads. A separate jq file shared by both was rejected too: pr-contract's step must keep an admitted command on `codeowners_gap.py`'s pin allowlist, and the workflow restores its programs from the base. The byte-for-byte pin gets the same parity without touching that step's code.
- (e) For X2: an adjacency pin alone, keeping `$?` on the `step` line. Capturing the rc on the call's own line also makes the reviewer's shape harmless: a no-op line between the two no longer changes the rc. Both are done.

## Head

`e9ac63c18510614713f6fc0329c5c24593d2179d` merges the authored code head `4cf87d2e97bb6abd2d223878d06dc63e9e4af4e2` and then merges origin/main `7d2056970` (an automatic merge by the orchestrator's script; any resolution inside the code head is described below) into this PR's previous head.

`4cf87d2e97bb6abd2d223878d06dc63e9e4af4e2`. Its merge base is `5261ba84139d9459465ccd842b61b04c2b1329d8`, origin/main's tip when read at 2026-10-26T01:24Z. This round's commits over the round-1 handoff `2b0eb9d85`:
- a merge of the PR head `042c60c8a`, which adds the delivery row;
- `35c4fb0e9`, a merge of origin/main `5261ba841`, with no conflict;
- `72fab10e4`, the round-2 change;
- `4cf87d2e9`, which re-points the rewritten usage line at `tools/pr/prepr.sh`. The full prepr at `72fab10e4` refused the layout guard and predicted a `tests / fast (3.14)` red, because the line re-added the retired `tools/audit/prepr.sh` path. The change is one comment line, so the mutants and the self-test count taken at `72fab10e4` are unchanged by it.

`git diff --quiet 042c60c8a 35c4fb0e9 -- tools/pr/prepr.sh tools/audit/carry_audit.py tools/audit/seat/roster_lib.py tools/pr/preflight.sh` exits 0, so the main merge changed none of the inputs the round-1 mutants read.

## Approval

`dev/governance/roles/fixer.md` is policy. This pull request changes one sentence of its step 5: it used to say the body must also pass `carry_audit.py check --body`, "which prepr omits", and it now says prepr's step 7e is the carry check. The change corrects the text to match the new step and adds no obligation to a seat. The owner's approving review is still owed before the merge. `tools/pr/prepr.sh`, `tools/pr/app_push.sh`, `tools/audit/seat/tmp_paths.py` and `.github/workflows/pr-contract.yml` (a comment only) are code-owned paths too.

## Mutation proof

Round 2's mutants. Each was applied by a scratch script, out of tree, in a detached worktree at `72fab10e4`. The full `bash tools/pr/prepr.sh --self-test` ran once per mutant, and the worktree was then removed. Unmutated: 384 passed, 0 failed.

- M10, `preflight_body` given the forwarded numbers (`"$@"`) instead of the derived list. This restores the hand-passed list. 3 failed: the row where step 7 refuses a keyword on a roster never-issue though the caller forwards it, plus both null-control rows (fixed issue, unrostered issue).
- M12, the main flow's step 7 back to the old `preflight.sh "$@"` call. 1 failed: "step 7's preflight derives the intended list and refuses on its rc".
- M11, `--body-check` not propagating the preflight rc (`[ "$r" -ne 0 ] || r=$pr` deleted). 1 failed: "and --body-check runs the same preflight and refuses on its rc". This kill comes from a text pin, not a body_push fixture. A fixture would need a never-issue in the real roster that the body_push clone carries.
- X2, the reviewer's surviving mutant in its no-op form (a `:` line between the 7e call and `step "carry"`). 1 failed: "the body step runs carry_line on the body and refuses on its rc".
- X2', the same position holding `CARRY_RC=0`. 1 failed, the same row.

Result: 5 planted, 5 killed. Round 1's M1 to M9 (9 planted, 9 killed, at `1b9a86266` and `2b0eb9d85`) are not re-run. Their inputs did not change (see `## Head`), and their rows all still print `ok` in the 384.

## Null control

- **Self-test count.** `bash tools/pr/prepr.sh --self-test`: `352 passed, 0 failed` at the merge base `5261ba841`. `377 passed, 0 failed` at `35c4fb0e9`, round 1's change merged with main. `384 passed, 0 failed` at `72fab10e4`. Round 2 adds exactly 7 `st` rows: 4 `preflight_body` fixture rows, 1 `INTENDED_JQ` parity row, and 2 call-site rows (step 7, `--body-check`). It rewrites 1 row, the 7e call-site row, into the adjacency form under the same name. 377 + 7 = 384.
- **The finder's instance.** Round 1's body (`handoff-body/r10-flow-jidoka` at `3a106cff3`) was run through the old form `bash tools/pr/preflight.sh 2428`, which passes it: an `ok` line calling 2428 intended, rc 0. It was then run through `preflight_body <that body> dev/programme/rosters 2428` on this head's roster: a `REFUSE` line saying the keyword's issue, 2428, is not in the intended list, rc 1, after `note forwarded issue number(s) 2428 ignored; intended list derived as pr-contract does: none`.
- **Fixture roster** (#100 in two groups' `issues` and no `fixes`, #101 fixed, #555 unrostered). A closing keyword on #100, with 100 forwarded, is refused. One on #101 passes, and one on #555 passes. Under M10 the refusal turns into a pass and both passes turn into refusals.
- **Parity.** `grep -cF -- "'$INTENDED_JQ'" .github/workflows/pr-contract.yml` prints 1 at the head. Any byte changed on either side makes it 0.
- **Worktree-only carry, stale mirror, unrouted then routed, 7c, foreground.** These are round 1's fixtures, and their rows print `ok` in the 384 unchanged. Without `--roster-ref`, carry_audit passes a carry to a group only the worktree holds, and `carry_line` refuses it with `BAD-DEST ... R10-LOCAL`. A stale mirror refuses a group the origin's round branch holds, and the fetch then passes it. An unrouted item is refused with `UNROUTED`, and once routed it passes. `reds_head_sha` finds the origin's `fix` that the clone lacks. A foreground sleeper outlives a KILL (`gone:alive:alive`), and through `heavy_run` all three arms read `gone:gone:gone`.

## Figures

All taken at `72fab10e4` (the full prepr at `4cf87d2e9`) against origin/main `5261ba841`, 2026-10-26 between 00:30Z and 02:10Z, on this box.

- `bash tools/pr/prepr.sh --self-test`: `384 passed, 0 failed`, wall 4 min 47 s by `time`. Merge base: `352 passed, 0 failed`. `35c4fb0e9`: `377 passed, 0 failed`.
- Mutants: 5 planted, 5 killed, by the kill rule "the self-test's summary reports one or more failures". The driver printed no `PATTERN COUNT` refusal: each pattern matched exactly once.
- Scoped gate: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"` prints `MODE: SCOPED -- 2 script(s) run, 31 scoped out`. `scope.run` names `tests/entities.py` and `tests/harness_headers.py`.
- `PYTHONPATH=tests/hastub python3 tests/entities.py`: `2 of 2445 ENTITY CHECKS FAILED` at the head and at the merge base. The sorted FAIL-line names are identical: `diff base head && echo IDENTICAL-FAIL-NAMES` printed it. It is this box's result, not this diff's. CI's `tests / closures` was green at `042c60c8a`.
- `PYTHONPATH=tests/hastub python3 tests/harness_headers.py`: `ALL 112 HARNESS HEADER CHECKS PASSED` at the head and at the merge base.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`.
- `python3 tools/audit/archscore/score.py --diff 5261ba84139d9459465ccd842b61b04c2b1329d8 HEAD`: `Architecture score: dS +0.0000 NULL`.
- `node tools/policy/policy_lint.mjs`: `TOTAL: 0 error(s) across 50 policy file(s)`.
- `node tools/policy/rules_sync.mjs --check`: `RULES-SYNC ok`.
- `python3 -I tools/audit/fold_ledger.py check`: `0 violation(s)`, `122 rca entries`.
- `python3 -I tests/throwaway_git.py --check`: `0 raw git init or clone site(s) refused`.
- `python3 -I tools/audit/seat/ref_privacy.py --check`: `0 refused`.
- `python3 -I tools/audit/seat/tmp_paths.py --check`: `0 refused`.
- `bash tools/pr/prepr.sh <this body>` at `4cf87d2e9`, with no issue number after it, 29 min 24 s wall. Every step is `ok` or `skip` except `closures`. The new lines: `ok preflight`, and `ok carry CARRY-AUDIT: 2 finding item(s): 2 routed, 0 unrouted, 0 bad destination(s), at origin/handoff/audit-r10-roster d373c351f`. `closures` refuses with `failed while being recorded: tests/entities.py (exit 1)`, which is the box result above, identical at the base. Step 7c skips: `work/jidoka` is a local branch name and has no remote head.
- The same run at `72fab10e4` refused `layout guard` and `ci predict` on the retired-path line that `4cf87d2e9` repairs. Before either run, `--body-check` on this body's first draft refused `preflight`, because the draft quoted preflight's own output line about #2428 with its keyword. The new step had refused its own author's body. The quote is reworded.
- The round-1 census of why 7c did not fire (17 verdicts, 24 cited reds) is not restated or re-taken here. Its script was scratch in the round-1 seat and is not in the tree. The record is round 1's body at `handoff-body/r10-flow-jidoka` `3a106cff3`, `## Figures`.

## Red checks

- `pr-contract / pr-contract` and `gate`, red at `042c60c8a` (jobs 121309523358 and 121310055657, and the two `gate` jobs). pr-contract refused round 1's closing keyword on #2428, because #2428 is a roster never-issue, and `gate` was red only because of that refusal. This body names #2428 with `Refs`. The cheaper detector is step 7's preflight fed the roster-derived list. This diff builds it (`preflight_body`, also in `--body-check`), and on round 1's body it refuses the same line locally (see `## Null control`).
- `governance / delivery-status`, red at `042c60c8a` (job 121302697237) on main's overdue delivery rows. It is not a required context and not this PR's. This diff writes no delivery row.
- `tests / nightly-status`, if red on main's ancestry. It grades main's nightly lane, not this head.
- `tests / ci-ratchet`, which may be red on main's push runs: GitHub's repo-wide artifacts listing returns 0 bytes, and a hotfix is in flight. It is not this branch's red, and this diff does not touch `tests/ci_ratchet.py`.

## Forward-carry

- The rest of this group's roster carries are not built in this pull request: the parity test (G1, G2), one grammar owner for `## Forward-carry` (G3), the P-N body-check extensions, the base-pinned replay (P3), ref_privacy and figure_lint at body push, quiet output, `--fill-red`, the wave-script trigger glob (P75), the claims.py byte-identity check, and predicting fast (3.14) and instrument-self-tests. They remain on `R10-FLOW-JIDOKA` on the roster branch. The S size cap (about 400 lines) cannot hold them. Carry: R10-FLOW-JIDOKA
- The round-1 census's HEAD-ONLY class needs a predicting detector, not a reading one. Step 7c can only read reds on commits already pushed. Carry: R10-FLOW-JIDOKA

## Friction

none

