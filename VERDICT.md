Fix review: blocked 8db2e56828e89b75b1294023e6f9ccb7de0be67b root-cause-detectable: tests / fast (3.14)

bus-nonce: c8d82f5fe3b4c23c09f8b3791b23ba36

Round 1, sonnet, finder's harness dev/audit/harnesses/r10_rca_sweep_settle_loop.py. Head measured: 8db2e56828e89b75b1294023e6f9ccb7de0be67b (still the PR head at post).

## Block

The PR's own harness fails a required check. `tests / fast (3.14)` concluded failure at this head (12:52:10Z to 13:03:33Z), and `gate` concluded failure (12:53:19Z). The failing script is `tests/harness_headers.py` (log `ev/fast-log.txt` line 8132), check "every inlined walk matches the canonical helper and no depth root remains": `FAIL depth seams: dev/audit/harnesses/r10_rca_sweep_settle_loop.py:37: ROOT = HERE.parents[2]`. I confirmed the matcher: `depth_root_seams` flags a `ROOT =` line holding `.parents[`, which line 37 is. The change is to resolve the repository root through the canonical helper that check names, not a parent count.

The body says "## Red checks: None. No PR exists and no CI has run on this head". That was true at push and is stale now, so the red is unanswered. A cheaper detector existed: the body itself says `tests/harness_headers.py` was not run to completion on the fixer's host (no `homeassistant`). The depth-seam scan (`depth_root_seams`) is a pure text scan of the harness files and needs no Home Assistant. It would have shown this red before the push. Name it as the detector and run it (or the scan alone) before handoff.

Carry: built-here

## Findings

- Residual: gate-sweep convergence countermeasure A is carried only through PR-body prose ("Carry: #201"); the RCA names the fixer's brief but I did not open a roster carry for it at this head. Whoever lands the sweep fix must confirm the closed-loop check reaches R10-SWEEP-SETTLE-LOOP's brief before that PR merges. Carry: #201

## Evidence

- Replay at my own run (`ev/replay.txt`): origin/main `RESULT replay reruns=86 max_attempt=44 sim_minutes=72 alarm=yes`; 52f9fc5b34 identical; 52f9fc5b34^ `reruns=0 max_attempt=1 alarm=no`; head `--no-restamp` null `reruns=1 max_attempt=2 alarm=no`; head tree `reruns=86 max_attempt=44`; candidate copy (arm 1 skips conclusion == skipped) `reruns=1 max_attempt=2 alarm=no`. These match the record's counts and the harness moves under its perturbations.
- Not re-derived: the census figures (465/324 runs, 428/1618 re-attempts, 17 at cap) need the saved API TSV, which is not in the tree. The 810 runner-minutes figure is the orchestrator's, not taken here.
- RCA content: names a cause, state (c) with evidence, a cost test with numbers, countermeasure A adopted and carried, B proposed. The sweep fixer's side is a separate PR (#3327); this one touches no production line.
- VERSION, manifest and RELEASE_NOTES.md untouched (three-dot diff lists 6 files, none of them). Delivery row dev/programme/delivery/3329.md present. New files: harness .py classified in tests/closures.json INERT READS; the .json fixture is its read input.
- `git merge-tree --write-tree origin/main 8db2e56828e89b75b1294023e6f9ccb7de0be67b` exited with a tree and no conflict.
- CI at this head (classify): WAIT, closures job still in progress when I wrote this; the fast and gate reds above are concluded, so I did not wait further. Non-required reds are not counted.
