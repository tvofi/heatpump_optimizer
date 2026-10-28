Fix review: merge b7d2b645faf0a440f269b5734d16025058d53e61

bus-nonce: 8d5be6d3893125ceb8861682c4cb8703

Round 2. I measured head b7d2b645faf0a440f269b5734d16025058d53e61, and it was still `refs/pull/2629/head` when I wrote this verdict. I worked from detached worktrees at that head. `dev/governance/roles/` has no diff between the merge base and origin/main, so the contract I followed is current.

## Round-2 delta

The delta is `e1ff812ce` (two acceptance arms in `tools/policy/policy_lint.mjs`, two checks in `tests/entities.py`) and two merges of main. I recomputed the merge resolution. `git merge-tree` of e364a0d73 and e1ff812ce differs from the head's tree only in `dev/programme/rosters/wave-r10-groups.json`. There the head keeps main's carry line and drops the branch's longer variant, so the three-dot diff no longer touches the roster. The resolution is benign. The 63a4dce67→b7d2b645 merge brings only main's `tests/entities.py` and `tests/nightly_status.py`, so none of this PR's code moved.

## RESULT lines (all at b7d2b645)

- RESULT acceptance: `FIXTURE ok: 92 error(s) hold 253 pins`, rc=0 (ev/accept_head.txt). This matches the body.
- RESULT entities: `ALL 2404 ENTITY CHECKS PASSED`, rc=0, under /opt/hpo/venv-ci (Python 3.14.7) with `PYTHONPATH=tests/hastub` (ev/entities_head.txt). Both new checks print `ok`. The body says 2401 at 63a4dce67. The 3 extra checks come from main's entities.py, merged after that measurement, so the body's number is stale for this head but was not wrong when taken.
- RESULT mutation_table: `python tests/mutation_table.py --pin-killed --base origin/main` printed `scope changed: no production code line added or modified`, `0 new unpinned site(s)`, `PIN KILLED: nothing to pin`, and 4062 unpinned sites at both ends, rc=0 (ev/mutation_table.txt). This matches the body.
- RESULT policy_lint mutants (my script, ev/mut_lint.py; output in ev/mutants_lint.txt). All are scored by the acceptance:
  - R1, a failed enumeration cached as an empty map: rc=1 (failed-enumeration arm and its null control)
  - R1b, the `if (fetched.ok)` guard deleted: rc=1 (TypeError, as the body says)
  - R1c (mine), a failure with a `why` cached: rc=1
  - R2, `cache || {}`: rc=1 (foreign-key arm)
  - R2b (mine), a `startsWith` key check: rc=1
  - R2c (mine), the key compared on its `since` half only: rc=1
  - R2d (mine), the key compared on its head half only: **survives**, rc=0 with 253 pins. See Findings.
- RESULT entities mutants (ev/mut_entities.py; output in ev/mutants_entities*.txt). Each one fails `every record-job invocation ... passes the same --window-cache file` at rc=1, and the shape check stays `ok`:
  - null: rc=0, both checks ok
  - M1-yaml (all five flags dropped)
  - Y1 (`--sunset` `.claude` arm)
  - E1 (mine: `--sunset` `tools` arm)
  - E2 (mine: `--record` only)
  - E3 (mine: one `--stats` arm given `window2.json`)
  - E4 (mine: `--stats` `.claude` arm)
- RESULT carry: `carry_audit.py pr 2629` and `check --body` both print `4 finding item(s): 4 routed, 0 unrouted, 0 bad destination(s)` (ev/carry_audit.txt). The live body's git blob sha1 is 24ff8c3becc6443cb08c28a80e3fee8fa85fe742, which matches the brief (ev/body.md). The toolchain friction names `Carry: R10-FLY-CLOUD-SETUP-TOOLCHAIN`.
- RESULT merge: `git merge-tree --write-tree origin/main(4e38e7d7b) b7d2b645` exits 0 with no MERGE-CLAIM line (ev/merge-tree.txt).
- RESULT CI: all 44 check runs on the head have completed: 35 success, 9 skipped, 0 failure (ev/ci.txt, from the commit's check-runs API). nightly-status and pr-contract (all three runs) are green. The body's `## Red checks` answers reds from earlier heads: nightly-status's false ABSENT, and pr-contract rounds 0 and 1. The round-1 pr-contract refusal (unrouted carries) is cleared by the routed body. No red on this head needs an answer.
- VERSION, the manifest version, RELEASE_NOTES and both claim files are untouched three-dot.

## Round-1 block, re-checked

Every item that cleared the block holds at this head:
- A failing `pulls` stand-in is read twice: R1, R1b and R1c are killed.
- A foreign-key file is not served: R2 is killed.
- The record job's five `--window-cache` invocations are pinned: M1-yaml, Y1 and E1–E4 are killed, and the null control passes.
- The body's carries are routed.

Round 1's other evidence carries over, because the code it covered did not move: the harness figures 834→370, the replay table, the M-A to M-E mutants and the concurrency analysis.

## Findings

- R2d survives: `readWindowCache` comparing only the head half of the key (`..<main>`) serves a file written for another `since` on the same head. The acceptance's foreign seed is `${windowKey}-foreign`, which differs only in the head half, so the body's claim "a file from another window ... is ignored" is pinned only for another head. I traced the path. In the `record` job all three modes pass the same `steps.window.outputs.since`, and `$RUNNER_TEMP` is per job, so no caller in the job reaches a file keyed on another since. Only a manual run reusing one `--window-cache` file across two `--since` values could, and that path is far-fetched. A one-line change, seeding a key with a different since half, would pin it, but it is not worth a block. Carry: dismissed: no caller in the record job writes and reads one cache file under two since values; the miss is in the acceptance fixture, not in the guarded code
- The seat environment needed `PYTHONPATH=tests/hastub` and /opt/hpo/venv-ci to run entities.py. `tools/audit/seat/seat_venv.sh` failed here with `No download found for request: cpython-3.14.7`. That is the same friction the body routes to R10-FLY-CLOUD-SETUP-TOOLCHAIN, and /opt/hpo already held the built venv. Carry: R10-FLY-CLOUD-SETUP-TOOLCHAIN

## Not re-derived

- I did not re-run the harness totals (834/370/464/740) or the replay table. Round 1 measured them, and the code they read has not moved since.
- I did not re-run the gate-scope line, the policy lanes or the agreement-lane lines. CI's heavy runs at this head cover them, and all are green.
