Fix review: blocked 3134798017b1d26994c410206349b06d187559a0 red-checks: the required gate concluded failure at this head and the body's Red checks reads b9cc5e32's runs, naming none of this head's concluded reds

bus-nonce: cadcb4da69387217a9d4d50501093e2e

## Block

- The required context `gate` is red at 3134798017b1d26994c410206349b06d187559a0: `merge_train.py classify` prints `RED 3134798017b1d26994c410206349b06d187559a0 pending: none red: gate` (exit 1), re-read at verdict time. The latest gate run 128471344242 (run 42385416529, 17:14:38Z-17:15:10Z) logs `FAIL pr-contract / pr-contract: failure (run 42387066581)`: it read the failed pr-contract 128449815767 of the superseded run 42387066581, although pr-contract 128471138373 in its own run is green (17:13:48Z-17:14:35Z). So the red looks like a stale cross-run read rather than a code defect, but a red required context is not a merge verdict; it needs a gate re-run after a green pr-contract.
- The body's `## Red checks` says it reads "the PR 3252 head b9cc5e32... (total_count 42)". This head has total_count 68 (one page of 100, read via get_check_runs), with these concluded reds, none named in the body: `gate` 128471344242, 128452383371 and 128448828285 (failure); `pr-contract / pr-contract` 128449815767 and 128446411039 (failure); `tests / nightly-status` 128455324026 (failure). The body's runs (128377933403, 128377933374) are of another head. This is the same class as round 3's block (verdict/3252 22658bca); the repair did not rewrite the section for this head.
- The code itself passes: see Evidence. Repair needed is body-only (Red checks rewritten against 3134798 runs) plus a green gate run.

## Findings

- Finding (a), carried: the relay and bus self-tests were not run under macOS bash 3.2 in this round either; this container has only bash 5.2. Claim: the self-test passes under bash 3.2 / APFS. Evidence: none at this head; the body states it was not demonstrated. Harness: `bash tools/audit/seat/cloud_relay.sh --self-test` under /bin/bash 3.2 on APFS. Metric: failed-check count. Perturbation: the round-4 mutant R4b (collision check moved after extraction), which reproduced the orchestrator's APFS failure mode in principle. Carry: R10-RELAY-SWEEP

## Evidence

- Head reviewed: 3134798017b1d26994c410206349b06d187559a0 (ev/HEAD.txt), parents 45c0f78a0 and de5a645a4; merge base 28d46c4918285d36c409c1fb2f72eb77e04e569e. Detached worktree at the head.
- `bash tools/audit/seat/cloud_relay.sh --self-test`: `cloud_relay self-test: 372 checks, 0 failed`, rc 0 (ev/cloud_relay.sh.log). Matches the body's 372.
- `bash tools/audit/seat/bus.sh --self-test`: `bus self-test: 159 checks, 0 failed`, rc 0 (ev/bus.sh.log). Matches 159.
- `python3 -I tools/audit/seat/orchestrator_tick.py --self-test` rc 0; `python3 -I tools/audit/seat/ledger.py --self-test` rc 0; `node tools/policy/policy_lint.mjs` rc 0 (ev/selftests.txt; the two python logs were written to one file name by my loop and are not kept, only their rc).
- Round-4 mutant R4a (delete the `ev_case_collision` call in relay(), cloud_relay.sh lines 235-236; ev/mutant_r4a.diff): 372 checks, 5 failed, including `refused before any write: nothing was extracted (tar never ran)` and `ev/HEAD.txt and ev/head.txt are refused rc 2` (ev/mut_r4a.log). Killed.
- Round-4 mutant R4b (move the collision check to after `git archive | tar -x`, the pre-repair order behind the APFS failure; ev/mutant_r4b.diff): 372 checks, 2 failed: `refused before any write: nothing was extracted (tar never ran)` and `and no scratch directory was created (TMPDIR still empty)` (ev/mut_r4b.log). Killed: the ordering is pinned on a case-sensitive filesystem, by the tar-call and TMPDIR rows; the null control `null control: distinct names do run the extract` stays ok.
- Earlier mutation-vacuous lines stay killed: X2 (bus.sh line 390 `if cc=$(git ls-tree ...)` to `if false; then :`): 159 checks, 2 failed, the two read-side case rows (ev/mut_x2.log). Y1 (`if n > 0:` to `if False:` at orchestrator_tick.py:1057): 283 checks, 1 failed, `relay GAP: a relay log holding a handoff-no-pr OWED line and no .level file prints GAP, flagged, with the count` (ev/mut_y1.log).
- `git merge-tree --write-tree origin/main HEAD` against origin/main 4b5d771bd: rc 0, clean (ev/merge-tree.txt).
- review_packet.py render: `REFUSE required-red: required context gate concluded failure` (ev/review-packet.md); figure_lint 10 resolved, carry_audit 0 items.
- bash 3.2 compatibility of the new self-test helpers was only read: `$'\n'`, `${n:0:8}`, `local` and here-strings are bash 3.2 features; no run.
