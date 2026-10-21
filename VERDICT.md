Fix review: blocked 5332c59f9b5e883d1b1638a6f310fbc7237bdaa9 vacuous-test: the reap arms check only the recorder's leader pid, so a watchdog that TERMs the pid instead of the group orphans derive_closures.sh's lanes and the self-test stays 323/0; step 6b's own closures_step call is also unpinned

This is round 2, the second review of this group. I measured head `5332c59f9b5e883d1b1638a6f310fbc7237bdaa9`, and it was still the PR head when I wrote this. Its tree `02b062d86` is the automatic merge of `2545f3659` with main `49c222280`. Code head `47e0cdd97` is byte-identical to the head on all four authored files, so the body's figures, taken at `47e0cdd97`, apply here (ev/head-lineage.txt). I worked from a detached worktree of the head, under /etc/profile.d/hpo-toolchain.sh with bash 5.2.21. `dev/governance/roles/` on main is unchanged since the merge base. `git merge-tree --write-tree origin/main <head>` exited 0 with tree `a5ac35924`, against main `57f0c9c77` (81 commits past the base), so the merge is clean.

## Blocking

- **The arms pin the recorder's leader pid, not its process group, and the group is the load.** The watchdog's `kill -TERM -- -"$rpid"` and the `set -m` that gives the recorder its own group exist because `tests/derive_closures.sh` forks its recording lanes as `( ... ) &` (derive_closures.sh:235). Those lanes are the python recordings that fed the box's load. The self-test's sleeper has no child, and `reap_arm` checks only `$spid`. M7 changes one token, `kill -TERM -- -"$rpid"` to `kill -TERM "$rpid"`, and the self-test gives 323 passed, 0 failed (ev/mut-M7.txt).
  - I wrote my own probe (ev/lane-*.diff). It gives the sleeper one `( sleep 300 ) &` lane, as derive_closures.sh does, and adds the lane's state to `REAP`. A process counts as alive only when `ps -o stat=` shows something other than `Z`, because PID 1 in this container leaves zombies unreaped and `kill -0` counts them as alive. My first pass used `kill -0` and misread a zombie this way.
  - At the head, the probe passes all three reap arms with `gone:gone:lane-gone`. Under M7, all three fail with `gone:gone:lane-alive` (ev/lane-M7.txt). In both runs, the one other failure is my probe's own `| grep -qv`, caught by the pipefail lint.
  - So the head's code is right, but the test does not hold it. Its arms pass while the production orphan of the recorder's work comes back.
  - To unblock: make the sleeper fork a child, as the recorder does. Then require that child gone in every reap arm, and read it as gone by its state, not by `kill -0`. That last point is the zombie trap R10-UPDATE-PR-SIGNALS's brief records for this container. Carry: R10-PREPR-CAP (item 61eab2a5)
- **Step 6b's call site, the route this round changes, is not driven.** `drv.sh` evals prepr up to `rc=0` and then calls `closures_step` itself, so prepr.sh:2945 never runs under the arms. M9 puts that line back to the round-1 route, `CLOSURES_LINE=$(closures_line "$BASE")`, and the self-test still gives 323 passed, 0 failed (ev/mut-M9.txt).
  - That is the shape round 1 measured as deferring a TERM to the prepr until the recorder finishes. M4sub puts the same shape inside `closures_step`, and it fails the TERM-alone and group arms (321/2). So a one-line revert at the production site restores the round-1 defect with the suite green.
  - To unblock, either one fixes it: have the driver reach the recorder through step 6b's own statement, or add a static pin that 6b calls `closures_step` and runs no `$(closures_line`. M9 must then fail. Carry: R10-PREPR-CAP (item 3fc47a16)

## Round-1 items, re-checked

- **Round 1's block (vacuous-test) is repaired for the mechanisms it named.** The arms now run the job-and-`wait` route, with prepr's traps installed through `exit_on_signals` and the driver's own `$$`, and the head gives `323 passed, 0 failed` (ev/selftest-head.txt).
  - RESULT M0 (null, unmodified): 323/0.
  - RESULT M3wd (watchdog body replaced by `( : ) & wpid=$!`): 320/3, all three reap arms.
  - RESULT M3setm (delete `set -m`): 321/2, the KILL and TERM-alone arms.
  - RESULT M4sub (`closures_step` back to `$(closures_line ...)`): 321/2, the TERM-alone and group arms.
  - All of these match the body. Carry: dismissed: repaired at this head (item f77a7120)
- **The off-Linux default and the opt-in hold.** RESULT M1 gives 319/4, M2 gives 321/2 and M6 gives 322/1, each failing exactly the arms the body names. The minor finding from round 1 is fixed: `PREPR_RECORD_CLOSURES=0` no longer opts in, and M6 pins that. Carry: dismissed: confirmed as claimed (item 9c353878)
- **The roster's recommendation is dispositioned.** Round 1 noted it as undispositioned: force the opt-in on diffs touching `tests/closures.json` or `tests/closure.py`. The body now dispositions it: those diffs are case `full`, which 6b skips before the platform predicate is read. A `full`-case arm pins that skip. Carry: dismissed: a full-case diff never reaches the opt-in (item 542f776b)

## Not blocking

- **M5 survives as the body says.** RESULT M5 (`exit_on_signals` emptied) gives 323/0, and I accept the body's equivalent-mutant disposition. bash's default TERM disposition also runs the EXIT trap and exits 143, so on this interpreter nothing observable separates the two. Carry: dismissed: equivalent mutant on bash 5.2 (item 7362c299)
- **M4 survives, and I read it as equivalent.** RESULT M4 (`closures_line` run in the foreground with no `&`) gives 323/0. A foreground function call has no `$(...)`, so the `wait "$rpid"` inside it runs in the top shell and the trap still ends it at once. The job layer is load-bearing only against a command substitution, which M4sub covers. Carry: dismissed: equivalent to the job route (item 25985327)
- **M8 is caught, by a hang rather than a failure.** RESULT M8 (delete the `kill "$wpid"` cleanup) hung the self-test after its line 184, and I killed it at 733 s. A lingering watchdog holds the `$(...)` pipe of the self-test's own `closures_line` captures open while `$$` lives. A hang in step 3h would show it. Carry: dismissed: caught by a hang (item a1166f6d)
- **One body claim is stale.** The body says `carry_audit.py check` refuses its sibling-seam carry as BAD-DEST because `R10-PREPR-CAP is done`. At roster `23ef06dc6` the group's stage is `in-progress`, and the same check over the body prints `2 routed, 0 unrouted, 0 bad destination(s)` (ev/carry-body.txt). The sibling seams are prepr's foreground heavy steps, the 18 lines the body's rule returns, which I re-counted at 18. Their carry now names the group that this PR closes on merge, so it reaches no later stage. When the body is re-cut, route that carry to a group that outlives this PR, or to the orchestrator's issue the body names. Carry: dismissed: stale wording, re-route on re-cut (item 11113f3e)

## Figures re-derived at the head (ev/cheap-checks.txt)

- **Figures match the body.** `RULES-SYNC ok`. `MODE: SCOPED -- 1 script(s) run, 32 scoped out.`, and scope.run is `tests/entities.py`. `ALL 2375 ENTITY CHECKS PASSED`. `claims hygiene: 49c222280... ok`, which is the head's own base: the body quotes `e7c664856` at the code head. `ALL 124 closure shrink pins PASSED`, `layout self-test: ok`, `ALL 109 HARNESS HEADER CHECKS PASSED`, `STRUCTURE RATCHET PASSED` and `Architecture score: dS +0.0000 NULL`. The `PREPR_RECORD:-` grep gives one production line, prepr.sh:564. Carry: dismissed: re-measured and confirmed (item 7a034a7c)
- **No release files or claim files move.** VERSION, the manifest, RELEASE_NOTES.md and tests/golden are untouched, and no claim file moved. The nightly-status path filter over the diff prints nothing (rc 1). Carry: dismissed: re-measured and confirmed (item 2d56cd8b)
- **Finder's harness (step 9).** The reopened group still has no committed harness. Its evidence is the owner ruling and the roster note's out-of-tree 6b count. The lane probe is my own instrument, not the finder's, and it is disclosed above. The pack at `30c57744a` (dev/programme/flow-study/) states nothing about this group that the diff contradicts. Carry: dismissed: no committed harness exists (item f1328887)

## CI at this head (check-runs API, ev/check-runs.tsv)

- **CI has concluded, and the one red is answered.** All 49 runs have concluded. The one red is `nightly-status` (job 119339580088). It grades main's scheduled run 39563978649 at `c77f89d`, where `mutation-nightly` and `slow` failed, and the diff reaches nothing those lanes read. The body's `## Red checks` names and answers it. `closures` and `mutation` are green. `pr-contract` was green at 17:05:18Z, after the last run concluded (closures-autofix and ci-ratchet at 17:03:26Z). Carry: dismissed: main's red, answered in body (item 2c5f406c)
- **Policy approval is still owed.** gate-scoping.md and its two generated copies still owe tvofi's approving review. That review is not mine to give. Carry: dismissed: owner approval still owed (item 110972e5)

bus-nonce: b5c87533bd83cca7b8de279dd5a2019d
