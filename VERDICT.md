Fix review: merge db727d36e02f837e587bc049069d586a587fb913

bus-nonce: 3a5161b918163fd9a7e34fedb9a67693
pending-ci: gate, governance / instrument-self-tests

## Summary

Round 2. The previous round returned `merge` at 816c2a3e11 (probe ref `probe/rev-3825-d64c72ea`), but it was never posted to `verdict/3825`, so the packet reads `Review scope: full`. This round re-runs every check of the first round at this head. It also tests the two branch commits since then: `ea5ad2a5fd` (beatd's SIGTERM handler now installs before the job threads start) and `144a391879` (adds two main modules to `cycle_lane.py`'s closure). No production file changes. `review_carry.py` prints FRESH-REVIEW. The head merges cleanly with origin/main. Every mutant this seat planted fails its named check.

## Findings

- Follow-up: the `yields` floor is recorded on one platform and read on another, so how sensitive it is depends on the kernel. On this seat's kernel (OPENBLAS_CORETYPE Haswell), clean yields read 528-590 against records 360-495 (`ev/cycle_head.txt`). The first round showed that a planted halving of `_gil_yield` failed only one scenario of five. That run is the first round's evidence (`probe/rev-3825-d64c72ea`, `ev/mut_yield_half.txt`), and the production code it ran on is the same at this head. Carry: dismissed: design-approved operator (§5) that still detects a halving; re-recording the lane's budgets on CI's platform is the remedy, and the C part's CI-platform re-record (design §7) is where that runs

## Notes

- Note: figure: the body's A figures are 2 short. At merge base a8efe1d1c2, the finder's harness reads `error_triples=56`, `unrecovered_triples=54` (body: 54/52); at the head it reads 56/0 (body: 54/0). The A1 mutant reads `unrecovered_flow_error_triples=56` (body: 54). The extra 2 are main's silent-mode `device_prefill` triples, which `8b42bf71c5` recovers. Carry: dismissed: paperwork, the figures moved with main's merge and the head's own check reads 56

## Evidence

- Round 2 of #3825; the packet reads `Review scope: full`. Head `db727d36e02f837e587bc049069d586a587fb913` (`ev/HEAD.txt`); merge base `a8efe1d1c2a8f1e0b44cdf1046a0ea4ca2155a3b`. Role contracts are current: `git diff $(git merge-base origin/main HEAD)...origin/main -- dev/governance/roles/` is empty.
- `review_carry.py 816c2a3e11 db727d36e0` prints `FRESH-REVIEW`: the branch-own commits `144a391879` and `ea5ad2a5fd` change content.
- Merge with main: `git merge-tree --write-tree origin/main db727d36e0` exits 0 (`ev/merge-tree.txt`).
- Step 5: three-dot, `VERSION`, `custom_components/`, `RELEASE_NOTES.md` and `tests/golden/` are untouched (`ev/untouched.txt`, empty). The claim files are not in the diff. No production file changed, so step 4's drift is null by construction.
- Step 1, mutation proof, re-run at this head:
  - A1: both tracker `done = True` set to False (lines 553 and 560). Result: `RESULT unrecovered_flow_error_triples=56`, `1 of 684 checks FAILED` (`ev/mut_A1.txt`).
  - A2: `recover(flow4, "rooms", ...)` removed. Result: `UNRECOVERED options/rooms/too_many_rooms`, `unrecovered_flow_error_triples=1`, `1 of 683 checks FAILED` (`ev/mut_A2.txt`).
  - Carry 0, M9 (`scale *` dropped at `ledger.py:534`) and M10 (`* scale` dropped at `ledger.py:536`), production mutants. Each was run through `features_block.py` over the R10-SAV-COMFORT block up to `_st_z = _SavLedger()`. Clean: `ALL 6 FEATURES BLOCK PASSED`. M9 fails only `(carry 0, M9)`, with stored -2.0 against -2.0. M10 fails only `(carry 0, M10)`, with comfort 1.0 against 1.0 (`ev/feat_*.txt`).
  - Gate schema: `yields` MIN changed to MAX gives `300 checks, 2 failed`, exactly the two `cycle: ...yields...` checks (`ev/mut_gate.txt`). Clean gives `300 checks, 0 failed` (`ev/gate_selftest.txt`).
  - D: `cycle_lane.py --self-check` fails each of four arms only on its own channel, and the clean arm on none: `SELF-CHECK PASSED` (`ev/cycle_selfcheck.txt`).
  - beatd (`ea5ad2a5fd`): this seat restored the old order (thread start, `time.sleep(2)`, then `signal.signal`) in a scratch copy and ran `--self-test 2 --no-mutants`. It prints `FAIL (2) SIGTERM stops the beat and TERMs its job: rc 0, PASS rc=-15, STOP`, while `(2) null: the job was running` holds (`ev/mut_beatd_order.txt`). At the head, `--self-test 2` reads `14 checks, 0 failed`, including `mutant m2_sigterm_handler_after_jobs turns (2) ... red` (`ev/beatd_st2.txt`).
- Step 2, the finder's harness: `cfg_recovery.py` from `50a932de3b`, sha1 `677301f5b8d3e957c24e9f36d23b8a98cf80a68c`, matching the body (`ev/cfg_recovery.py`).
  - Base: 56/54 (`ev/finder_base.txt`). `--perturb` at the base moves unrecovered 54 to 50, so the harness is live (`ev/finder_base_perturb.txt`).
  - Head: 56/0 (`ev/finder_head.txt`).
- Step 3, null controls at the head:
  - `config_flow_steps.py`: `RESULT unrecovered_flow_error_triples=0`, `ALL 684 checks PASSED` (`ev/cfs_head.txt`).
  - `--self-check`: `all six mutations caught by their named checks` (`ev/cfs_selfcheck.txt`).
  - `cycle_lane.py`: `ALL 25 checks PASSED` (`ev/cycle_head.txt`).
  - `comment_ratchet.py`: `OK` (`ev/comment_ratchet.txt`).
  - Not re-derived by this seat: B (needs `coverage`, which venv-ci lacks). `tests/entities.py` hit this seat's 220 s timeout before finishing (`ev/entities.txt`), so it is left to CI.
- Step 6, class: A's closing check enumerates every rendered `(kind, step, code)` triple, so the enumeration is the check itself; the finder's harness reads 0 over the same 56. D's channels are the five in the design's table. No other seam found.
- Step 14:
  - `budget_raise_gate.py --base a8efe1d1c2 --head HEAD --pr 3825` prints `RAISE tests/ci_budgets.json: script_runs_per_push: 54 -> 56` and `RESULT budget_raises=1 count` (`ev/gate_raise.txt`; rc 1 because the approval is owed).
  - `score.py --diff a8efe1d1c2` prints `Architecture score: dS +0.0000 NULL` (`ev/archscore.txt`).
  - The +2 is one new script measured by two instruments. Payments judged as in round 1; this seat found no payment that improves the code.
  - The `144a391879` closures addition (`room_history.py`, `room_record.py`) matches the modules #3711 added on main, which `cycle_lane.py` imports through the coordinator.
- Step 15: the added test code follows the approved design. Step 16: no actuator path touched.
- Step 10: carries C and `script_runs_full_case_pr` are dismissed-routed. The packet's `carry_audit` reads `2 routed, 0 unrouted`.
- Step 11: the body's `## Red checks` answers the earlier heads' reds, including `instrument-self-tests` at `e1dd8b8462`, repaired by `ea5ad2a5fd` and verified above. The owed-reds set is in `ev/owed_reds.txt`.
- CI: unreadable. Classify was polled every ~90 s from 19:59 to 20:30 UTC. Every line read `rc=3 WAIT ... pending: gate red: none` until the last, at 20:30:31, which exited 2: `REFUSE selftests: the head's governance / instrument-self-tests job 136969734850 concluded cancelled, which reads no step: re-run it: an introduced red cannot be ruled out (fail closed)` (`ev/classify.log`). At 20:30 the head's runs 44942948357 and 44943642493 were cancelled en masse (tests, governance, codeql, validate, gate), with the head unchanged. No owed red was classified at this head. `budget-raise-gate` read failure at 20:20 on run 44942948357; that is the raise's owed approval, which follows this verdict (mandate 6893738184, scope all). This verdict therefore carries `pending-ci` for `gate` and `governance / instrument-self-tests`: the relay should post it only once both read green at this head. This seat verified the beatd repair that `instrument-self-tests` exercises locally (step 1).
- Step 12: the head was re-read before return (see `ev/head_reread.txt`).
