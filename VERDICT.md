Fix review: merge 43c9255bf7ecdb1e1d3c5807805dae1dd2665f1e

bus-nonce: c9236fe09b1d8338fe14068fe74850fd

Round: this reviews round 5. It is a body-only re-take of r4 (code head ea464fe68, unchanged) after the blocked verdict f3bd78c35 on the r2 head. Measured from detached worktrees at 43c9255bf7ecdb1e1d3c5807805dae1dd2665f1e.

## Findings

- tools/audit/seat/sweep_template.md item (3), a line this diff rewrites, still reads "Verdicted pull requests go to one train on the hourly pitch". The owner's re-scope (tvofi 2026-10-24) drops the hourly pitch: the head's mechanism is the event add plus a 1800 s backstop sweep. This is wording only and no code reads it. It belongs with the nudge.md step-3 alignment that the body's Forward-carry 3 already sends on. Control: sweep_template.md item (3) names the event add and the backstop sweep, not an hourly pitch. Carry: R10-POLICY-ROLE-PACK
- The one-train invariant holds only within a single state dir, and the head's two triggers can be configured with different ones. bus.sh's event add uses $HPO_BUS_TRAIN_STATE. tick_loop.sh's sweep_pass runs `merge_train.py sweep` with no --state-dir, so it falls back to the HPO_STATE_DIR default (merge_train.py:5429). sweep_template.md item (3) names `--state-dir {{orch_scratch}}`. Nothing binds the three, and two state dirs would each start a train beside the other. Both triggers are off by default, so no live path is affected at this head. Control: the beat's sweep job and the bus event add are configured with one named state dir, and a test proves a sweep and an event add under the shipped configuration reach the same queue.open. Carry: R10-ORCH-BEATD

## Evidence

- Head: 43c9255bf7ecdb1e1d3c5807805dae1dd2665f1e (ev/HEAD.txt). The PR head ref still pointed at it when I posted. Roles diff merge-base...origin/main under dev/governance/roles/ is empty, so the contract is current.
- Head composition (ev/resolution.txt): the head's tree equals `git merge-tree --write-tree adcce8fc6 102f74975`, and adcce8fc6's tree equals `git merge-tree --write-tree f3bd78c35 ea464fe68`. Both merges are mechanical, with no hand resolution (the closures.json ledger driver resolved the set merge). The authored code is ea464fe68, as the body states.
- Merge with current origin/main (de794b537): `git merge-tree --write-tree origin/main 43c9255bf7ecdb1e1d3c5807805dae1dd2665f1e` gives rc=0, tree e2ba26088, no conflict (ev/merge-tree.txt). On that merged tree, `python3 tests/structure.py` prints STRUCTURE RATCHET PASSED with rc 0 (ev/structure-merged.txt).
- RESULT at head (ev/head-checks.txt): every figure matches the body:
  - merge_train 318 checks, 0 failed
  - bus 74, 0 failed
  - tick_loop 17, 0 failed
  - train.sh ok
  - orchestrator_tick 214, 0 failed
  - proof_watch 40, 0 failed
  - structure.py STRUCTURE RATCHET PASSED, rc 0 (seam_cut_total 420 <= 420)
  - agreement_py `RESULT divergent=0 unregistered=0 dead=0 refused=0`, 18/18 restore
  - selftest_wiring 96/96/0
- RESULT fixer harness, run by me at head (ev/fixer-mutants.txt): 43 non-M0 mutants (A1-A12, V1-V6, R1-R7, C1, C2, S1-S8, B1-B3, T1-T3, G1, G2). 0 lines read ` 0 failed` or NOT FOUND, so all 43 were killed. M0 baseline is 318/17/74, 0 failed. Under G1 and G2, agreement_py prints unregistered=1, as the body says. The tree was clean after the run.
- RESULT reviewer mutants (my own, ev/reviewer-mutants.txt), 14 planted and 14 killed, each failing a named arm:
  - R1: verdict sha compare
  - R2: live check reads train.pid instead of queue.open (TRAIN-UPGRADE carry)
  - R3: closing-train wait dropped (one-train arm)
  - R4: CARRY: yes ignored (P96(b) null control fails)
  - R5: carry skipped (CARRIED arm fails)
  - R6: sweep seen-at-head dropped (EXACTLY ONCE)
  - R7: ledger train-stop hold dropped
  - R8: sweep start-failure path dropped
  - R9: verdict rule removed from admit_add
  - R10: queue lock removed
  - R11: ALREADY rule removed
  - R12: bus.sh event add removed
  - R13: bus.sh merge-only filter removed
  - R14: tick_loop sweep call removed
- Carry P96(b): discharged by a pin. The arm at merge_train.py:5285-5344 drives the real app_approve.sh --carry over a throwaway repo, with the verdict an ancestor of the head and main's merge as the only gap. It requires the carry to be read under the queue lock (held == [True]) and the entry to be spooled for the NEXT batch. Its null control is a head with an own-branch delta past the verdict, refused as `carry: ... CARRY: no`. R4, R5 and R10 each kill it.
- Carry TRAIN-UPGRADE: discharged. `Train.admit_add` gains the `verdict` rule (add_verdict), on main, after open/base and before carry. `grep "def pitch|launch_train|def live_train" merge_train.py` returns nothing at the head, and launch_detached is the one launcher. train_add reads queue.open first, then waits out a live train.pid (merge_train.py:798-829). R2 and R3 kill it.
- The previous blocked finding (f3bd78c35, design-trace-missing) is closed. The head has the add admission, the event add from bus.sh post_verdict, the backstop sweep, and no timed pitch. Its arms cover refused-add-with-rule, add-during-proof landing in the next batch, and sweep exactly-once with never a second train.
- Body figures re-derived (ev/figures.txt): `git diff 973618e6f HEAD -- tests/closures.json` gives 5 added lines and 0 removed. At 973618e6f, bus.sh has 0 train_add/HPO_BUS_TRAIN and merge_train.py has no `def sweep(`.
- Not re-derived, taken from CI instead: the strace closure recording (about 19 min) and the body's local entities.py 2-of-2440 figure. CI `tests / closures` is green at this head.
- Untouched: VERSION, manifest, RELEASE_NOTES.md and both claim files have an empty three-dot diff.
- CI at head (ev/ci.txt): every run concluded, with success or skipped and no red. This includes tests / closures, fast (3.14), mutation, lane-proofs, instrument-self-tests, pr-contract and budget-raise-gate. The earlier reds (tests / closures and closures-autofix at f3bd78c35) are named and answered in the body's Red checks, with the cheaper detector and its cost. The diff's governance.yml lines add ledger.py, proof_watch.py, record_row.py and roster_lib.py to the wave-script restore list; agreement_py's restore 18/18 confirms them.
