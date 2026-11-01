Fix review: merge f4f7daf6ce71185391f69f09d4bd26e4932fe233

bus-nonce: 22c1cb59673fdb795ade94217b227b0e

## Summary

Round 1 review of #3086 (R10-HOTFIX-UUTILS-SLEEP), at head f4f7daf6ce71185391f69f09d4bd26e4932fe233. The diff is three-dot against merge base 6421fe135d9f, which is also origin/main. dev/governance/roles/ is unchanged between the merge base and origin/main, so the contract I applied is current. The fix replaces the bystander's renamed symlink to /bin/sleep with a wrapper, `exec sleep "$1"`. That clears main's red on governance / instrument-self-tests under real uutils, and reverting it brings the red back.

## Findings

- The body's Figures line `MODE: SCOPED -- 0 script(s) run` was measured before the closures.json classification commit. At 473fdfff2 and 18490e997 I get `MODE: SCOPED -- 0 script(s) run, 33 scoped out.`. At 783e189f3, which the body names as the authored code head, and at f4f7daf6ce71185391f69f09d4bd26e4932fe233, I get `MODE: SCOPED -- 1 script(s) run, 32 scoped out.` (RUN tests/entities.py). So the quoted figure does not hold at the head it is attributed to. CI's own selection (tests / closure-scope success, tests / fast success) is the binding one and is green. The fix is not affected; this is a stale figure in the body. Carry: dismissed: a body figure only, superseded by CI's green scoped run at the head, and it changes nothing a later stage must do.

## Evidence

- RESULT finder-harness baseline (main CI, real uutils): job 124813746788 on `Image: ubuntu-26.04` at 6421fe135 printed `Security violation: Requested utility \`unrelated-sleep\` does not match executable name: /usr/lib/cargo/bin/coreutils/sleep` and `pr_args self-test: 158 checks, 2 failed` three times (open_pr, pr_args and update_pr steps). The failing arms were `open_pr: the null control -- an unrelated sleeper survives` and `null control: a normal successful update_pr leaves nothing behind ...`. Log: ev/main_job_124813746788.log.
- RESULT finder-harness head (PR CI, real uutils): job 124832739397 on `Image: ubuntu-26.04` at f4f7daf6ce71185391f69f09d4bd26e4932fe233 printed `pr_args self-test: 158 checks, 0 failed` in all three steps, with no Security violation line and no ##[error]. Log: ev/head_job_124832739397.log.
- RESULT emulation, base: `r10_uutils_sleep.sh 6421fe135 emu` -> `pr_args self-test: 158 checks, 2 failed`, rc=1, the same two arms as CI. origin/main emu (the same commit) gives the same result.
- RESULT emulation, head: `r10_uutils_sleep.sh f4f7daf6ce71185391f69f09d4bd26e4932fe233 emu` -> `158 checks, 0 failed`, rc=0.
- RESULT mutant (the fix reverted to `ln -s /bin/sleep`): `r10_uutils_sleep.sh f4f7daf6ce71185391f69f09d4bd26e4932fe233 emu symlink` -> `158 checks, 2 failed`, rc=1. The mutant is killed by the same two arms.
- RESULT null control: `r10_uutils_sleep.sh f4f7daf6ce71185391f69f09d4bd26e4932fe233 gnu` -> `158 checks, 0 failed`, rc=0, on host GNU coreutils (Ubuntu 24.04).
- All four body figures for r10_uutils_sleep.sh reproduce exactly. That harness is the fixer's own instrument, disclosed as such in the body and landed in the tree (fixer step 18). The finder's harness is the CI job above, and I read it at both ends.
- I tried to run a real uutils binary locally as an independent control. This environment's permission layer refused to execute the downloaded binary, so I did not use it; the real-uutils evidence is CI's ubuntu-26.04 runner at both ends, as cited.
- The fixture is sound: $UNREL stays the sleeper's pid (exec). The bystander checks key only on $UNREL by pid (pr_args.sh lines 664, 946, 1080 and the cleanup at 1496), and nothing matches the name `unrelated-sleep` by pattern.
- Class sweep. I re-ran the body's three greps at the merge base (ev/class_rule.txt). They return the same 19 sites the body dispositions, and I agree with each disposition: only pr_args.sh:625 runs a coreutils binary under another name. A wider rule of my own covers copies and installs of /bin binaries, `$(command -v|which)` copies, `exec -a`, argv0 and `executable=` (ev/class_rule_widened.txt). It returns only s2_release_gate.py (`executable="/bin/bash"`, not coreutils) and two comment/text lines, so no further seam is open. Other sleep uses (`/bin/sleep N` in beatd.py, fractional `sleep 0.1`, the stub `$W/bin/sleep` in app_approve.sh) call sleep under its own name, which uutils accepts.
- CI on f4f7daf6ce71185391f69f09d4bd26e4932fe233: `merge_train.py classify` printed `GREEN f4f7daf6ce71185391f69f09d4bd26e4932fe233 pending: none red: none` (rc=0, 11:59Z). In the full check-run set (38 runs), no run concluded failure; the conclusions are success, skipped or neutral (CodeQL).
- Red checks: no check is red at the head. The body's ## Red checks answers main's red on governance / instrument-self-tests: no cheaper detector exists, because seat hosts run GNU coreutils. I accept that answer, and the landed harness now reproduces the failure on any Linux seat.
- structure.py at f4f7daf6ce71185391f69f09d4bd26e4932fe233: `STRUCTURE RATCHET PASSED` (ev/structure.txt).
- Scoped gate at f4f7daf6ce71185391f69f09d4bd26e4932fe233: `MODE: SCOPED -- 1 script(s) run, 32 scoped out.` (ev/scope.txt).
- Delivery row: dev/programme/delivery/3086.md is in the three-dot diff.
- Claim files: tests/golden/claimed_drift.txt and card_claimed_drift.txt are byte-identical to origin/main. VERSION, RELEASE_NOTES.md and the manifest are untouched.
- Merge: `git merge-tree --write-tree origin/main f4f7daf6ce71185391f69f09d4bd26e4932fe233` -> 1c6bc0be48ba, rc=0, no conflict.
- Head: the branch ref is still f4f7daf6ce71185391f69f09d4bd26e4932fe233 at verdict time, and main is still 6421fe135. The body names 783e189f3 as the code head, and f4f7daf6ce71185391f69f09d4bd26e4932fe233 adds only the delivery row.
- Forward-carry: the body says none, and the fix changes no later stage.
