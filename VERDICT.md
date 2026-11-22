Fix review: blocked db727d36e02f837e587bc049069d586a587fb913 ci-red: classify reads RED red: gate, three gate suites still hold a pre-decision read of a run that has since completed

bus-nonce: 38e370c11341660ef3382dc85f218dd7

## Summary

This is round 4 at the same head, `db727d36e0`. Round 3 (`probe/rev-3825-23455ea9`, `bef3842c44`) blocked only on stale `gate` suites. Since then the stale suites were re-run, but two of the re-runs ran while run 44942948357 was itself re-running. So they again read "still being judged". The head and its diff are unchanged, and the role files on main changed only in wording, so this round re-ran the cheap checks at the head and read the new CI.

No code, test or harness finding blocks. The head merges cleanly with origin/main. Mutant A1 still fails its check at this head.

## Block

- `merge_train.py classify db727d36e0 --pr 3825` exits 1 at 04:55 UTC: `RED db727d36e02f837e587bc049069d586a587fb913 pending: none red: gate` (`ev/classify.log`). The review packet refused on `required-red` for the same reason.
- Cause, read through `merge_train`'s own `gate_suites`, `job_log` and `gate_outcome` (`ev/gate_suites.txt`). There are six `gate` suites at this head, and every workflow run at the head has now completed (`ev/runs_at_head.txt`).
  - Three suites fail on the owed raise approval alone, `budget-raise-gate / budget-raise-gate: failure`: jobs 137044070127, 137047381856 and 137086254280.
  - Three suites are stale. Each printed `run(s) [...] at this head are still being judged; their gate decides`:
    - job 136969344649, run 44942948064 attempt 1, which was never re-run;
    - job 137062556803, run 44952774191, re-run at 02:34, while 44942948357 was still re-running (it completed at 04:07);
    - job 137065210288, run 44943642493, re-run at 02:36, same cause.
  - So `gate_raise_only` is False, `approval_owed` returns None, and classify fails closed to RED.
- Remedy, for the orchestrator: re-run the `gate` job only, in runs 44942948064, 44952774191 and 44943642493. Do it now that no run at this head is in progress, and one run at a time, or at least after every other run has completed. Classify should then read APPROVAL-OWED. This review's checks carry, because the head is unchanged.

## Findings

- Follow-up: the `yields` floor in `tests/cycle_budgets.json` is recorded on one platform and read on another, so how sensitive it is depends on the kernel. Round 1 showed that a planted halving of `_gil_yield` failed only one of five scenarios (`probe/rev-3825-d64c72ea`, `ev/mut_yield_half.txt`). The production code is unchanged at this head. Carry: dismissed: design-approved operator (§5) that still detects a halving; the C part's CI-platform re-record (design §7) is where re-recording the lane's budgets on CI's platform runs

## Notes

- Note: round: this is the fourth review round at this head. All three earlier rounds turned on CI state alone: round 1 `merge`, round 2 `merge` with `pending-ci`, round 3 `ci-red` on stale suites. None turned on code, so this seat reads no re-cut as owed on the fix. If the orchestrator reads `fix-review.md`'s "from the fourth, a re-cut is owed" otherwise, the call is its own.
- Note: figure: the body's A figures are 2 short. The head reads `flow_error_triples=56` (body: 54), and mutant A1 reads 56 unrecovered (body: 54). The extra 2 are main's silent-mode `device_prefill` triples, as round 3 recorded.

## Evidence

- Round 4 of #3825. Head `db727d36e02f837e587bc049069d586a587fb913` (`ev/HEAD.txt`). The PR head re-read at the end of the review is unchanged and `open` (`ev/head_reread.txt`).
- Role contracts: `git diff $(git merge-base origin/main HEAD)...origin/main -- dev/governance/roles/` touches `fix-review.md` and `fixer.md`. The changes are rewordings, plus the open-axis `class-open: axis` rule that the comms addendum already binds. No step this review relies on changed.
- Merge with main: `git merge-tree --write-tree origin/main db727d36e0` exits 0, with `LEDGER-MERGE: resolved tests/closures.json` (`ev/merge-tree.txt`).
- Step 1, re-run at this head, under venv-ci with `PYTHONPATH=tests/hastub`:
  - Clean: `RESULT unrecovered_flow_error_triples=0`, `ALL 684 checks PASSED`, rc 0 (`ev/cfs_head.txt`).
  - A1: tracker `done = True` set to False at `tests/config_flow_steps.py:553` and `:560`. Result: `RESULT unrecovered_flow_error_triples=56`, rc 1 (`ev/mut_A1.txt`). Restored afterwards.
  - Not re-run, because the head is unchanged: A2, beatd `--self-test 2`, M9/M10, the gate-schema mutant, the cycle_lane arms and the finder's harness at both ends (56/54 at the base, 56/0 at the head). Their evidence is at `bef3842c44` and `ce756cbe00` `ev/`.
- Step 14: unchanged since round 3. `budget_raise_gate.py` reads `script_runs_per_push: 54 -> 56`, and `score.py` reads `dS +0.0000 NULL` (`bef3842c44` `ev/gate_raise.txt`, `ev/archscore.txt`).
- Step 11: `gate` is in the owed-reds set (`ev/owed_reds.txt`). The body's `## Raise justification` and `## Red checks` answer the budget-raise red. The stale suites are pre-decision reads, not defects.
- Seat environment: `config_flow_steps.py` needs `PYTHONPATH=tests/hastub` under venv-ci, as `cloud-setup.sh` documents. The first run here, without it, failed on import, and that run is not evidence.
