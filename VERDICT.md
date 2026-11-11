Fix review: blocked bdf48d98a9dd04a437c67fa4aabadc93d1723335 mutation-vacuous: M4 Train.wait_ci pulse log dropped survives; M5 BASELINE_JOBS window removed survives; M8 the body's own mutant (first held-last sort line to pass) survives behind a duplicated copy

bus-nonce: 6da8bf70fe7b71770264867259d468fc

Round: first (handoff tip cfc7185fc716f68829f6941e5b700ffebcb9cacc; measured head bdf48d98a9dd04a437c67fa4aabadc93d1723335, the body's named head).

## Block

1. mutation-vacuous. Survivors at the head, each run with the owning `--self-test` (ev/mutants.txt):
   - M4: delete `if pulse: self.log(pulse)` in `Train.wait_ci` (tools/audit/seat/merge_train.py). Result: `613 checks, 0 failed`. No check proves the train ever logs the pulse; only the pure `one_job_pulse` is tested.
   - M5: replace `done[-BASELINE_JOBS:]` with `done`. Result: `613 checks, 0 failed`. The check that claims "last 6 of 7: the 100 s run falls out of the window" passes without the window. Over all 7 durations the p50 index is still 2800 s (47m) and the max is still 3600 s (60m), so the fixture cannot tell the two apart.
   - M8: the body's stated mutation proof. Replacing the `stranded.sort(...)` line in `Tick.orphans` with `pass` gives `315 checks, 0 failed`. The second, duplicate sort line keeps the behaviour, so the body's claim that this mutant "turned red" does not reproduce at this head. Deleting both copies (M1) does fail, at `315 checks, 1 failed`.
   Mutants that did fail (killed): M1 both sorts removed; M2 held count removed from the cap line; M3 `CAP_NOTICE` reverted (the board reads Unreadable); M6 `!= 1` changed to `< 1`; M7 over-max never printed.
2. architecture-unsound (fixer.md step 17, on added lines). tools/audit/seat/orchestrator_tick.py defines `HELD_TOPIC` twice, with its comment, at lines 183-188. It also runs the `stranded.sort(...)` and `held = sum(...)` pair twice, at lines 2444-2447 (ev/duplication.txt). The duplication is already in the fixer's commit cfc7185fc, not introduced by the main merge b907da84e. Deleting the second copies changes no check (M1b: `315 checks, 0 failed`), so the copies are dead duplicates and they hide M8.
3. A body figure does not re-derive. "merge_train.py --self-test: 613 checks before my additions": at merge base 0a2139b1d it prints `610 checks, 0 failed`, and at the head `613 checks, 0 failed`. So 613 is the count after the additions. The other figures re-derive: orchestrator_tick goes from 312 at base to 315 at head; owed_unactioned from 59 to 60, and the body's 60 is at the head.

To clear the block: remove the duplicate lines; add a check that pins the `wait_ci` pulse log line; add a fixture where the 7th, oldest run changes the p50 or the max; re-take the mutation proof and correct the 613 figure.

## Evidence

- Head self-tests at bdf48d98a: orchestrator_tick 315/0, merge_train 613/0, owed_unactioned 60/0 (ev/selftest_head_*.txt).
- Null controls named in the body are present and pass at the head.
- `git merge-tree --write-tree origin/main <head>` exits 0, so there is no conflict (ev/merge-tree.txt).
- VERSION, the manifest and the RELEASE_NOTES heading are untouched in the three-dot diff.
- There are no golden or claim-file changes, so step 4 has no drift to compare.
- Finder's harness: none is named. The brief items are instrument residue, and each item's harness is a self-test check this PR adds, so the fixer built it.
- Forward-carry: the body says none, and carry_audit at the head reports 0 items.
- CI: `merge_train.py classify` printed `WAIT ... pending: gate red: none` on each poll (ev/classify.log). There was no concluded red on a required check while reviewing. The block does not turn on CI, so I did not wait the full 30 minutes. `owed-reds` printed its set; it ends `tests / mutation`, `tests / typing`, `validate / validate-hacs`.
- Head re-read via the PR API: still bdf48d98a9dd04a437c67fa4aabadc93d1723335.

## Findings

none
