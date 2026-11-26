Fix review: blocked 791d83e72781db4af7345de8d2c43bcf66cd3475 instrument-self-tests: governance.yml's new ci-shards step is unrecorded in tools/ci/selftest_closures.json, so selftest_scope.py static is red at the head

bus-nonce: 1b6609f795ad71f7dcc8bcb5e3af394d

## Block

- `merge_train.py classify 791d83e7 --pr 3902` returns RED (rc 1). The red is `INTRODUCED Show the self-test scope (tools/ci/selftest_scope.py) refusing its own fixtures`. I reproduced it at the head: `python3 -I tools/ci/selftest_scope.py --self-test` passes (173 checks, 0 failed), but `python3 -I tools/ci/selftest_scope.py static` exits 1 with `STALE tools/ci/selftest_closures.json: its steps differ from the workflow's: missing ['ci-shards'], extra []` (ev/selftest_scope_static.txt). The PR's three-dot diff adds 8 lines and `id: ci-shards` to `.github/workflows/governance.yml` and does not touch `tools/ci/selftest_closures.json`. The step is present in the workflow at f03b95f3 and 791d83e7 and absent at the merge base and on origin/main, and the table lacks it at every one of those refs. This is an instrument-self-tests step red at the head that the diff's own scope selects, so it is the pull request's finding and a block (defect-root-cause.md; fix-review.md step 11). C8 bars a merge at a red in any case. The repair is the fixer's: `python3 tools/ci/selftest_scope.py record --step ci-shards`, then re-run `static`. The same red was INTRODUCED at f03b95f3 (ev/classify-f03b95f3.txt), so it was not opened by this delta and was never answered. `tools/pr/prepr.sh` runs this step's command locally in seconds; whether the handoff ran it is a root-cause note for the fixer.
- Both prior blocks are resolved (below). Once the table is recorded, the only delta left to review is that one re-record. My findings below stand unless the code moves.

## Round

Round 2 (delta) for #3902. Diff reviewed: `git diff f03b95f3 791d83e7` (code commit 5f068649 plus fc14b732, merged into the PR branch). The packet's `## Review scope` line reads `full` only because the dispatch passed the head as `--reviewed-head`; the brief scopes this round to the delta and to the two blocks from f03b95f3. The delta touches nothing under `custom_components/`, so the scope does not widen (fix-review.md step 12).

## Prior blocks

- Block 1 (readers of the fast lane's job name did not count shard jobs): resolved. `tools/ci/shards.py` now owns `FAST`, `is_fast` and `owed_fast`. prelude `owed_needs`/`judging`/`requeued`, gate `status`, sweep `code_red`, probe_bridge `bridge` and replan `_ingest_check_runs` all read the lane through them. A sharded listing owes every `K/N` of its one count and fails closed on mixed counts. The axis is enumerated by a rule, `census()`: `git grep -l -F "fast (3.14"` over tools/, tests/ and .github/, held against `READERS` in both directions. `git grep` outside those three roots returns only dev/ evidence harnesses and RCA records. None of them is in the gating path, and the one measuring harness, `dev/audit/harnesses/ci_script_seconds.py`, matches by prefix (`startswith("fast")`), so it already accepts shard names.
- Block 2 (run.sh's shard routing had no CI check): resolved. `shards.run_sh_routes` sources the file's own `shard_setup`, `shard_of`, `scope_script`, `run_always` and `skip` and drives them over a 2-shard and a 3-shard plan. Every script runs exactly once across the shards, and a script the plan does not name runs in shard 1. The unsharded null runs all four. An invalid shard `3/2` exits 1 with nothing run.

## Findings

- Follow-up: the self-test does not pin probe_bridge's shard ratio floor `(len(ref) // 2 if name == LANE else 1)` (tools/audit/seat/probe_bridge.py:138). The fixture ref holds 2 scripts, so `len(ref)//2 == 1` and a mutant restoring `len(ref) // 2` for shards passes `--self-test` (10 checks, 0 failed). My 3-shard, 6-script-ref probe shows the head is correct (3.14 = 20.0, runs = 3), while the mutant refuses with "no probed fast (3.14) run with its script lines". A self-test case with a ref of 4 or more scripts and shards holding fewer than half of them would pin it. This is not a block: the code at the head is right, the name-mutant on the same reader is killed, and probe_bridge is a seat instrument outside the gate (ev/probe_bridge_3shard.txt). Carry: #3885

## Evidence

- RESULT: my own mutants (ev/mutants.txt): every run.sh routing mutant is killed. Those are the shard_of default 1->2, the inverted owner test, a refused plan returning 0, the shard skip removed and shard_setup ignoring HPO_FAST_SHARD. Killed on the readers side: prelude owed_needs unsharded, gate status reading only the listed shards, sweep dropping is_fast (via `tools/ci/sweep.py --self-test`; the first run, through `sweep_selftest.py`, ran no entry point and was discarded), probe_bridge reading LANE only, replan with no fold, a replan fold ignoring a missing shard, owed_fast taking the union over mixed counts, is_fast unanchored, and READERS dropping gate.py.
- RESULT: two mutants survive. The probe_bridge floor is in Findings above. The other is owed_fast ignoring the prefix: equivalent under every caller, since prelude and gate pass listings that are uniformly `tests / `-prefixed and replan passes unprefixed names with `prefix=""`, so no listing mixes the two.
- RESULT: the fixer's harness `dev/audit/harnesses/r11_fast_shards_readers.py /tmp/wt` at the head gives BASELINE all green and READERS MUTANTS: 7 of 7 killed, rc=0 (ev/readers-harness.txt). This is the fixer's instrument, disclosed as the fixer's. My mutant set above is independent of it.
- RESULT: self-tests at the head (ev/selftests-head.txt): shards 28/0 failed, prelude 153/0, gate 133/0, probe_bridge 10/0, replan 0 failed, sweep (`sweep.py --self-test`) 124/0.
- RESULT: `git merge-tree --write-tree origin/main 791d83e7` exits 0. LEDGER-MERGE resolved tests/closures.json (ev/merge-tree.txt).
- RESULT: CI: classify RED at 791d83e7: `RED 791d83e72781db4af7345de8d2c43bcf66cd3475 pending: gate red: none introduced: 1` (ev/classify-final.txt, poll log ev/classify.log).
- The delta does not touch VERSION, the manifest version or the notes heading.
