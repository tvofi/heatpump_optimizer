Fix review: blocked 7572aa0aa878e55d8480264d8f0bcd927c6280aa findings-unresolved: the main conflict is cleared, but the round-3 verdict's two untested reads (pulse.py read_alive gen_t, seat_gen.py ps_start) still survive their mutants and the body does not answer them; Mutation proof still quotes mutants=22

bus-nonce: 4fe03951e4ee4618d4861b447c4d1f19

## Block

This is review round 4: b18d78b5070c, then 1418e0f76c47, then 1e2a04f06c42 (the round-3 verdict, blocked main-conflict, on probe/revt-r10-seat-identity-p5-0b7d3729), and now this head. From the fourth round, `fixer.md` owes a re-cut. The dispatch named 1418e0f76c47 as the reviewed head. Its delta to this head is the fixer commit 1e2a04f06c, which round 3 reviewed, plus one new commit, the merge 7572aa0aa8 of origin/main 4145f2852642. The merge's resolution (`git show --remerge-diff`) touches only the `PLANTS` table in `dev/audit/harnesses/r10_open_driver_mutants.py`, plus the `tests/closures.json` ledger merge. The delta writes no `custom_components/` code, so the scope is not widened.

1. The round-3 block is cleared. `git merge-tree --write-tree origin/main 7572aa0a` returns rc 0 (ev/merge_tree_main.txt), and origin/main is the merge base 4145f2852642. The resolution keeps both sides: main's M-livetip and M-moved-gone, and this branch's `GRAMMAR` targets on M-exact and M-body. The harness prints `RESULT mutants=24` and `RESULT survived=0`, which matches `EXPECTED` (ev/harness_head.txt). The resolution is load-bearing. If M-exact and M-body are reverted to main's untargeted hunk, the harness aborts with `ABORT M-exact: pattern occurs 0 times` (ev/reviewer_mutants.txt).
2. The two tests the round-3 verdict asked for are still missing. That verdict carried both as "owed by this branch's re-cut, a block item" and said this merge should add them. The merge changed none of `pulse.py`, `seat_gen.py` or `seat_gen_selftest.py`, and the body neither adds the tests nor answers the items. Both mutants were re-run at this head and both still survive (ev/reviewer_mutants.txt):
   - In `pulse.py:477`, changing `if sd:` to `if False:` disables the `<seat>.gen` read that feeds SUPERSEDED. The self-test still reports 69 checks, 0 failed.
   - In `seat_gen.py:98`, changing `ps_start` to `return 0` leaves the self-test at 23 checks, 0 failed.

   Remedy: add a `--seat-alive` CLI case with `HPO_STATE_DIR` holding a `merge.gen`, and a `ps_start(os.getpid(), now)` bound check. Show both mutants killed, or answer each item in the body with a measured reason.
3. The body's `## Mutation proof` line still reads `mutants=22`, but the harness prints 24 at this head. The body's own Forward-carry and merge sections say 24. Restate it.

## Findings

- `pulse.py` `read_alive` reads `gen_t` with no test (Block 2). Carry: dismissed: owed by this branch's re-cut, a block item
- `seat_gen.py` `ps_start` has no test (Block 2). Carry: dismissed: owed by this branch's re-cut, a block item
- The body's Mutation proof figure is stale (Block 3). Carry: dismissed: owed by this branch's re-cut, a block item

## Evidence

- Setup: `cloud-setup.sh --check` printed `OK python3 is /opt/hpo/venv-ci/bin/python3`. `role_pack.py render fix-review` rc 0. `git diff <mb>...origin/main -- dev/governance/roles/` was empty, so the contract is current.
- No pull request exists, so there is no review packet and no CI run to read. This is a handoff review. The body was read from `handoff-body/r10-seat-identity-p5` e60ef0c2f316 (ev/BODY_at_e60ef0c2.md). Its `## Head` equals the head measured, and `handoff/r10-seat-identity-p5` points at it (step 7). With no checks, no red is owed an answer. The owed-reds set is in ev/owed_reds.txt.
- `review_carry.py 1418e0f7 7572aa0a` prints `FRESH-REVIEW`, so this is a delta round.
- RESULT harness at head: `mutants=24`, `survived=0` (ev/harness_head.txt).
- RESULT self-tests at head (ev/selftests.txt): seat_gen 23 checks, 0 failed. pulse 69 checks, 0 failed. beat_jobs 203 checks, 0 failed. open_driver 93 checks, 0 failed.
- Three-dot diff against merge base 4145f2852642: `VERSION`, `RELEASE_NOTES.md`, `custom_components/` (the manifest included) and `tests/golden` are untouched (ev/three_dot.txt). No fixture moved, so `env_drift.py --all` is not applicable. `closure.orphan_files()` at head prints `[]` (ev/orphans.txt).
- `tests/entities.py`, run with `env -u BASH_ENV`, did not run here, so it is not verified. Under venv-ci it fails `No module named 'homeassistant'`, and under venv-ha it fails `No module named 'paho'` (ev/entities.txt). The null control at origin/main fails the same way (ev/entities_main.txt), so the failure comes from the container, not the branch.
- I did not re-run `prepr.sh` or the mutation table. The body's `prepr.sh rc=0` at the merged head is quoted and was not re-derived.
