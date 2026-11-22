Fix review: blocked db727d36e02f837e587bc049069d586a587fb913 ci-red: classify reads RED red: gate, four stale gate suites at this head still red beside the two whose only reason is the owed budget raise

bus-nonce: 23455ea93ac77f0c5aa226646f0f11e3

## Summary

This is round 3 at the same head, `db727d36e0`. Round 2 returned `merge` on `probe/rev-3825-3a5161b9` (`ce756cbe00`) with `pending-ci` set, because the head's CI runs were cancelled. This seat re-dispatched on new runs (run 44947168836). The head is unchanged since round 2, so this round re-ran the cheap checks at the head and read the new CI.

No production file changes. The head merges cleanly with origin/main. Every mutant this seat planted fails its named check. The finder's harness reads 56/54 at the merge base and 56/0 at the head.

## Block

- `merge_train.py classify db727d36e0 --pr 3825` exited 1 at 01:36:54 UTC, and again on a manual re-run: `RED db727d36e02f837e587bc049069d586a587fb913 pending: none red: gate` (`ev/classify.log`). The verdict is blocked on that red alone (card C8). Code, tests and harness hold: no code, test or harness finding blocks.
- Cause, read through `merge_train`'s own `gate_suites`, `job_log` and `gate_outcome` (`ev/gate_suites.txt`). Six `gate` suites sit at this head:
  - The two newest (jobs 137044070127 and 137047381856) fail on one reason only, `budget-raise-gate / budget-raise-gate: failure`. That is the raise's owed approval (mandate 6893738184, scope all), which would read APPROVAL-OWED.
  - Four older suites are still red for other reasons: 136975236298 and 136975307180 were cancelled at 20:30 UTC, and 136969344649 and 136999930894 printed `run(s) [...] at this head are still being judged; their gate decides`.
  - So `gate_raise_only` is False and `approval_owed` returns None, and classify fails closed to RED.
- Remedy, for the orchestrator: re-run the stale gate suites at this head (runs 44942948357, 44943642493 and 44952774191's `gate`) so that each reads its decided outcome. Classify should then read APPROVAL-OWED, and this review's checks carry: the head is unchanged and the review is otherwise complete.

## Findings

- Follow-up: the `yields` floor in `tests/cycle_budgets.json` is recorded on one platform and read on another, so how sensitive it is depends on the kernel. Round 1 showed that a planted halving of `_gil_yield` failed only one of five scenarios (`probe/rev-3825-d64c72ea`, `ev/mut_yield_half.txt`). The production code is unchanged at this head. Carry: dismissed: design-approved operator (§5) that still detects a halving; the C part's CI-platform re-record (design §7) is where re-recording the lane's budgets on CI's platform runs

## Notes

- Note: figure: the body's A figures are 2 short. The finder's harness reads `error_triples=56`, `unrecovered_triples=54` at merge base `a8efe1d1c2` (body: 54/52) and 56/0 at the head (body: 54/0). The A1 mutant reads `unrecovered_flow_error_triples=56` (body: 54). The extra 2 are main's silent-mode `device_prefill` triples, which `8b42bf71c5` recovers. Carry: dismissed: paperwork, the figures moved with main's merge and the head's own check reads 56

## Evidence

- Round 3 of #3825. Head `db727d36e02f837e587bc049069d586a587fb913` (`ev/HEAD.txt`), merge base `a8efe1d1c2a8f1e0b44cdf1046a0ea4ca2155a3b`. The PR body's `## Head` names this head.
- Role contracts are current: `git diff $(git merge-base origin/main HEAD)...origin/main -- dev/governance/roles/` is empty.
- Packet: `Review scope: full`, refusals none. `review_carry.py 816c2a3e11 db727d36e0` prints `FRESH-REVIEW`.
- Merge with main: `git merge-tree --write-tree origin/main db727d36e0` exits 0, with `LEDGER-MERGE: resolved tests/closures.json` (`ev/merge-tree.txt`).
- Step 1, mutation proof, re-run at this head:
  - Clean: `RESULT unrecovered_flow_error_triples=0`, `ALL 684 checks PASSED` (`ev/cfs_head.txt`).
  - A1: tracker `done = True` set to False at `tests/config_flow_steps.py:553` and `:560`. Result: `RESULT unrecovered_flow_error_triples=56` (`ev/mut_A1.txt`).
  - A2: `recover(flow4, "rooms", ...)` at `:1728` replaced by `pass`. Result: `unrecovered_flow_error_triples=1`, `UNRECOVERED options/rooms/too_many_rooms` (`ev/mut_A2.txt`).
  - beatd: `--self-test 2` reads `14 checks, 0 failed`, including `mutant m2_sigterm_handler_after_jobs turns (2) ... red` (`ev/beatd_st2.txt`).
  - Not re-run here, because the head is unchanged since round 2: M9/M10, the gate-schema MIN->MAX mutant and the cycle_lane `--self-check` arms. Their round-2 evidence is at `ce756cbe00` `ev/`.
- Step 2, the finder's harness: `cfg_recovery.py`, sha1 `677301f5b8d3e957c24e9f36d23b8a98cf80a68c`, matching the body. It reads 56/54 at the base (`ev/finder_base.txt`) and 56/0 at the head (`ev/finder_head.txt`). The round-2 `--perturb` at the base moved 54 to 50, so the harness is live.
- Step 14:
  - `budget_raise_gate.py --base a8efe1d1c2 --head HEAD --pr 3825` prints `RAISE tests/ci_budgets.json: script_runs_per_push: 54 -> 56` and `RESULT budget_raises=1 count` (`ev/gate_raise.txt`).
  - `score.py --diff a8efe1d1c2` prints `Architecture score: dS +0.0000 NULL` (`ev/archscore.txt`).
  - The +2 is one new script measured by two instruments. Payments judged as in rounds 1 and 2: this seat found no payment that improves the code.
- Step 5: three-dot, `VERSION`, `custom_components/`, `RELEASE_NOTES.md`, `tests/golden/` and the claim files are untouched (round-2 `ev/untouched.txt`, head unchanged).
- Steps 10-11: the packet's `carry_audit` reads `2 routed, 0 unrouted`. The body's `## Red checks` answers the earlier heads' reds. The owed-reds set is in `ev/owed_reds.txt`.
- CI: classify was polled about every 90 s from 01:19 UTC. It read WAIT (`pending: gate`) until `sweep-self` finished at 01:36 UTC, then RED (see `## Block`).
  - Every required unit context but `budget-raise-gate` reads success at run 44947168836, including `governance / instrument-self-tests`, `tests / fast (3.14)`, `tests / coverage-ratchet` and `tests / mutation`.
  - `gate`'s red is owed an answer, as the owed-reds set names it. The body's `## Raise justification` and `## Red checks` answer the budget-raise red. The stale suites are cancellations and pre-decision reads, not defects.
