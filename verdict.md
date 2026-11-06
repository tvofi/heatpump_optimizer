Fix review: merge 2a0d228c8f6e3d5af516f48f786fe3cb3acea4e6

bus-nonce: b31a181df54fd3a9da0768ce7a782aa1

## Round

This is round 3 of 3 of the fix review for R10-HOTFIX-GATE-BUSY-DEFER (PR #3246), on the critical path. I measured at head 2a0d228c8f6e3d5af516f48f786fe3cb3acea4e6 from detached worktrees at the head, at 8af5fa58 (the null control) and at the merge base b36679ce. The roles diff since the merge base is empty. Round 2 blocked as `mutation-vacuous`: the M24 mutant (`all` to `any` in judge()'s C3 rule) survived. That block is now settled.

## Findings

- Follow-up: the required `gate` reads RED at this head. `merge_train.py classify 2a0d228c... --pr 3246` gives rc 1, `RED ... pending: none red: gate` (ev/classify_log.txt). All three workflow runs have concluded (ev/runs.tsv).
  - Code run 42229011444's gate (127953498222) printed `PASS` at 14:40:36Z.
  - Attempt 2 of the two edit runs then published red at 14:41:36-37Z: 127953951344 (run 42229013617, `FAIL run(s) [42229718965] ...`) and 127953961800 (run 42229718965, `FAIL run(s) [42229013617] ...`).
  - Both jobs printed `programs restored from b36679ce...` (ev/gates_1441.txt). The gate job judges with main's pinned tools/ci/*.py, so this is main's mutual deferral, the defect this PR fixes, reproducing live. The diff did not cause it.
  - The attempt-1 reds, 127931745088 and 127936670895, are C3 at-once deferrals to that code run.
  - The body's `## Red checks` answers exactly this shape: a `gate` red reading `programs restored from <base>` with a mutual `FAIL run(s)` deferral.
  - Clearing the required context so the PR can merge is the orchestrator's call (re-run or override), because main's gate cannot judge this mutual pair until this fix lands.

  Carry: dismissed: main's pinned defect that this PR fixes; the body answers it and the merge mechanics are the orchestrator's
- Out of scope: in code run 42229011444, `governance / instrument-self-tests` (127930702784) was cancelled at the 30-minute limit (13:56:59Z to 14:27:16Z), so the run concluded `cancelled`. The body names this check as MAIN-WIDE: main's push run 42214947262 timed out on the same job. The body carries it in R10-PROCESS-SLIM. This diff adds about one second of gate.py self-test. Carry: dismissed: main-wide job budget, carried by the body to R10-PROCESS-SLIM, not this PR's to settle

## Evidence

- Round-2 block re-measured with the finder's harness for that block. That harness is the round-2 reviewer's `ev/probe_mixed.py` (from probe/rev-3246-f805b9e8). I inserted it before the `done_edit` line of a scratch copy of gate.py's self-test (ev/insert_probe.py) and ran it on a `git archive` export of tools/ and .github/ at each SHA (ev/probe_mixed_r3.txt):
  - head: verdict `FAIL run(s) [42192000000, 42193153511] ...`, naps=0, held_s=0, `66 checks, 0 failed`.
  - head with M24: the probe gives naps=12 and held_s=720, and the self-test reads `66 checks, 1 failed`. The one red case is `prelude/gate cycle: a deferring gate beside an earlier started gate and a later edit run in its prelude publishes at once`, which got 12 × 60 s naps where it wanted none.
  - 8af5fa58 (null control): naps=0 unmutated. With M24, naps=12 and held_s=720, yet the self-test reads `65 checks, 0 failed`, so the mutant survives without the new case, as round 2 found.
  - base b36679ce: naps=0, `57 checks, 0 failed`.
- The mutant table, taken from scratch in a clean worktree at the head with `python3 -I dev/audit/harnesses/r10_ci_gate_core.py mutants`, prints `RESULT mutants=23 survivors=0`, rc 0 (ev/mutants.head.txt). M24 is listed and KILLED (self-test rc 1, replay rc 0), red on the named case above. M17-M22 are KILLED, each red on the cases the body's table names, and I checked every row against the arm's `red:` lines.
- M20-M23 stay killed:
  - M20 and M22 are the in-table rows above.
  - M21 is KILLED on 4 cases, including the C3 null.
  - M23 is my own plant: `started()` also accepts `waiting`. It is red on 2 named cases, `busy-defer null (R3-2 EARLY) ...` and `prelude/gate cycle: ... gate listed `waiting` (R3-2) ...`, giving `66 checks, 2 failed` (ev/m23.head.txt).
- Null controls:
  - The two earlier `prelude/gate cycle:` cases and the C3 at-once case stay green at the head, and under M24 only the new case goes red.
  - `prelude.py --self-test` reads `62 checks, 0 failed` (ev/checks.head.txt).
- replay: `gate_replay2.py over tools/ci/gate.py: rc 0; output IDENTICAL to 1371a0a6:measure/rev/gate_replay2.txt`. sim: `gate_sim.py ... IDENTICAL to 1371a0a6:measure/rev/gate_sim.txt` (ev/replay.head.txt, ev/sim.head.txt).
- Race harness on a `git archive HEAD tools/ci tools/pr` export: rc 0 (ev/race.head.txt).
  - All seven scenarios read the same at the head and at 8af5fa58 (ev/race.r2.txt).
  - `prelude: verdicts 3 UNDECIDED-RED 1 MASKED 0 DEADLOCK no CYCLE 0 gate-wait 300 s`, then `RESIDUAL-RED 0`. The six other scenarios read UNDECIDED-RED 0, DEADLOCK no and CYCLE 0. This matches the body.
- This round changes no production line. `git diff 8af5fa58 HEAD -- tools/ci/gate.py` has one hunk, at `self_test()` line 571. The body's statement holds.
- Tree identity:
  - The head's tree 45f7fca4 equals ea6d8de7's tree.
  - `git diff --quiet 4710b715 HEAD` exits 0, so the body's figures taken at 4710b715 apply to this head.
  - The head's parents are 8af5fa58 and ea6d8de7.
- The body's `## Head` names 2a0d228c..., the head measured. I re-read the branch at verdict time and it is still 2a0d228c....
- `git merge-tree --write-tree origin/main(33e60b5b) HEAD` exits 0 with tree 9fa3151d, so there is no conflict and no claim files are involved.
- Three-dot diff: tools/ci/gate.py, the r10_ci_gate_core.py and r10_gate_defer_race.py harnesses, and dev/programme/delivery/3246.md (the delivery row is present). custom_components/, VERSION and RELEASE_NOTES.md: 0 paths.
- `tests/structure.py`: `STRUCTURE RATCHET PASSED`. `tests/entities.py`: `ALL 2637 ENTITY CHECKS PASSED`. `closure.py select`: `MODE: FULL`, reason `tools/ci/gate.py changes the gate itself` (ev/checks.head.txt). CI owes the full suite. The full suite's code-run jobs concluded success except the main-wide instrument-self-tests cancel above.
- Step 11:
  - The reds at this head are the two pairs of gate deferrals and the instrument-self-tests cancel (ev/gate_checks.tsv).
  - The body names both checks and answers each as main's: the pinned mutual deferral, and the main-wide 30-minute timeout.
  - `pr-contract / pr-contract` 127953134975 succeeded at 14:40:05Z, after the cancel (14:27:16Z). It checked this body.
  - No `pr-contract` run started after the gate reds at 14:41:37Z. The body's answer to them is the generic `gate` red clause, and I matched each log against it myself (ev/gates_1441.txt).
- Settle items from earlier rounds hold unchanged:
  - The self-correction a83b95f9 and the 3c66c9b3/b0bccab4 revert leave replay and sim IDENTICAL.
  - The merge order against #3243 is moot, because #3243 is already on main.
  - The forward-carry is `none`.
- Carry-audit self-check: `carry_audit.py check` was run on the body and this verdict before return; its output is in ev/carry_audit.txt.
