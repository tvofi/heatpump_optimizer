Fix review: blocked f03b95f36ebcb0cc4481ca138c953a96f951f269 class-open: axis readers of the fast job name unenumerated (e.g. tools/ci/prelude.py judging)

bus-nonce: 69a5c376785f7ea4542bda588c117c9b

Round 1 of this PR (review scope `full`, no earlier verdict). Reviewed the net diff against main 658fcae30b, which already holds #3896. That diff is 13 files, from `git diff origin/main $(git merge-tree --write-tree origin/main <head>)`. The three-dot diff from merge base d9100de still carries #3896's own commits, because the PR has two merge bases (d9100de and 58c73880).

## Block

- **class-open: axis readers of the fast job name unenumerated (e.g. tools/ci/prelude.py judging).** The body expands the job name `tests / fast (3.14)` into `fast (3.14, K/N)` for exactly two readers, `gate.gate` (through `fast_names`) and `gate.status`. No rule names the set of readers of that job name, and no residue category covers it. One member outside both breaks at the first sharded run. `prelude.UNITS["tests"]` still lists `fast (3.14)`, so `owed_needs()` still owes `tests / fast (3.14)`. `judging()` then reads a sharded run with every unit completed as not judging, because the owed name is never listed.
  - Probe: `ev/judging_probe.py`, output in `ev/judging-probe.txt`. The unsharded control returns `True`; the same run with shards `1/3..3/3` returns `False`.
  - Effect: `gate.busy` (gate.py:133), `prelude` `wait_sources` (prelude.py:385) and `sweep.py:321` all call `judging`. Each would read every unfinished sharded run at the head as busy until that run ends: the #3263 shape. `requeued()` is affected the same way, so a re-run failed shard is never overlaid.
  - CI cannot see this here: by the body's own bootstrap, this PR's runs use the base's `tools/ci`. Other members found without a hunt: `tools/audit/seat/probe_bridge.py:58` (`LANE = "tests / fast (3.14)"`) and the `tests / fast (3.14)` names in `tests/ci_ratchet.py`. Name the rule that enumerates the readers (for example, every non-fixture reader of the job name in `tools/` and `tests/`) and route each reader it returns.
- **mutation-vacuous: tests/run.sh run_always shard skip (`${FAST_SHARD%/*}` -> `${FAST_SHARD#*/}`).** No CI-run check drives `run.sh`'s shard routing. `git grep HPO_FAST_SHARD|shard_of` finds only the out-of-CI harness `r11_fast_shards_random.sh`, and the 8-mutant driver plants nothing in `run.sh`.
  - Planted mutant: `ev/mutant-runsh.diff`, under the 2-shard plan in `ev/mutant-plan.json` (`tests/md_tables.mjs` in shard 2, everything else in shard 1).
  - Result: `HPO_FAST_SHARD=1/2` and `2/2` both exited 0, each printing `SHARD k/2: 1 TEST SCRIPT(S) PASSED HERE` (`ev/mutant-shard1.log`, `ev/mutant-shard2.log`). The union of the two shards ran one script twice and dropped the rest of the suite silently, with the gate green. This is the silent drop the body says cannot happen ("a wrong estimate can only unbalance the shards").
  - Owed: a committed check, in a closure CI runs, that drives `run.sh` routing with a fixture plan and asserts every script runs exactly once across the shards. It must fail on this mutant.

## Findings

- Note: stale-body: `## Head` has two paragraphs, one naming `da7c201c496c98cbb142ccd40071033f28f6a2b7`, which is not this head. Carry: #3885
- Note: figure-unverified: the Independence figure reads "unmeasured, running" (`r11_fast_shards_random.sh 1 OUT 3`). That randomized run is the body's only full-gate and independence evidence for the routing. It has no result in the body, and I did not re-run it (heavy gate run, per fix-review.md step 11). Carry: #3885

## Evidence

- RESULT: `git merge-tree --write-tree origin/main f03b95f3` exit 0, tree 83a1e813. `LEDGER-MERGE: resolved tests/closures.json`, no conflict (`ev/merge-tree.txt`).
- RESULT: self-tests at the head: `shards self-test: 21 checks, 0 failed`, `gate self-test: 132 checks, 0 failed`, `prelude self-test: 147 checks, 0 failed` (`ev/selftest-*.txt`).
- RESULT: `r11_fast_shards_mutants.py` at the head: all 8 KILLED, baselines green (`ev/mutants.txt`). This matches the body.
- RESULT: `shards.py plan --ref origin/main` gives `["1/4","2/4","3/4","4/4"]`, and with `--changed tests/doc_claims.py` gives `["1/3","2/3","3/3"]` (`ev/plan-figures.txt`). Both match the body.
- RESULT: the payload class (PRODUCERS) is closed by `git grep -E 'HPO_PLANDATA|plandata-'`. The readers on run.sh `run` lines are `card.mjs`, `card_drift.mjs` and `setup_qa_render.mjs`, all in PRODUCERS. `doc_claims.py` sets its own path, and `card_browser.mjs` is not in the fast lane.
- The balance figures (CALIBRATION, PLAN walls, NULL median 1409 s / best 1020 s, FLOOR) and the SPLIT table are not re-derived. They need the 14 CI job logs, which are not in the tree. The NULL (random assignment, 200 draws) is a fair null for LPT packing, but its numbers are unverified here.
- `VERSION`, the manifest, `RELEASE_NOTES.md` and both claim files are untouched in the net diff.
- CI at the head: `merge_train.py classify` still reads `WAIT ... pending: gate red: none` (`ev/classify.log`). This block is on code, so it does not depend on CI. `owed-reds` is in `ev/owed-reds.txt`.
- Builder disclosure: `ev/judging_probe.py`, the run.sh mutant and the fixture plan are the reviewer's own instruments. No finder's harness is named (packet).
