Root-cause record for the `pr-contract / pr-contract` reds that `tools/ci/codescan_wait.py` exit 1 writes on a `CI edit` run while the code run's codeql is still analysing. The change is docs and one instrument: `dev/audit/rca/R10-RCA-CODESCAN-WAIT.md` and the read-only harness `dev/audit/harnesses/r10_codescan_wait_race.py`, plus the harness's `inert_reads` line in `tests/closures.json`.

**Cause.** The ordering keys on run ids, and GitHub does not hand out run ids in event order. The push and the body edit land in the same second. In 27 of 94 measured code-and-edit pairs the edit run got the lower id. `prelude.wait_earlier` waits only for lower ids, so that edit run waits for nothing, and `codescan_wait.py` step 1 (`source()`) then FAILs at once: "no run at this head owns a finished codeql unit". **Process state (c):** DESIGN-P2 states the id order as an ordering guarantee and measured its premise by `created_at`; the code and its self-test case 6 follow the design exactly. **Countermeasure:** carried to R10-CI-LAYOUT-P2 and not built here. The carry has three parts: M1, the verdict prelude waits for every code run at the head; M3, the FAIL line reaches the log; M4, self-test cases for the inverted pair.

Of the brief's three instances, two are this mechanism (#2698, #2706). The third, #2704 at `04860ee0`, has both `pr-contract` runs green. Its red is the code run's `gate` under the designed defer rule ("still being judged"); the record says so.

## Head

9a8183f4dcdbf4ba72d38cfe51e2dd813fe099e8

It is on the base `origin/main` `e97f5749b441b282e43bd99dbcbb762e9d10a369`, and the brief's base `bf9f8aa16709ff5c6ab054057480c6d896f46b6c` is an ancestor of it. All API figures were read between 13:59Z and 14:20Z on 2026-10-24.

## Mutation proof

The harness self-test checks the cause's prediction, and a mutant of its one decision fails it:

- `python3 -I dev/audit/harnesses/r10_codescan_wait_race.py --selftest` printed `selftest: 9 checks, 0 failed`.
- Flipping `inv = e["id"] < low` to `>` in a copy printed `selftest: 9 checks, 5 failed ['inverted', 'ordered', 'red_inverted', 'red_ordered']`.

The cause itself was reproduced live. `env -u GH_TOKEN GITHUB_REPOSITORY=tvofi/heatpump_optimizer GITHUB_RUN_ID=40099071633 python3 -I tools/ci/codescan_wait.py --pr 2706 --base main` printed `FAIL closed: no run at this head owns a finished codeql unit for base 'main'`, rc 1, in 3 s, while #2706's code-run python leg (job 120887354588) was `in_progress`.

## Null control

- The same `codescan_wait.py` command for #2704's edit run 40096299978, whose code run's codeql had completed, gave rc 0 and an empty list.
- In the harness run, 0 of 67 ORDERED edit runs are red.
- `python3 -I tools/ci/codescan_wait.py --self-test` printed `codescan_wait self-test: 13 checks, 0 failed`.
- The scoped gate (`python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)`) printed `MODE: SCOPED -- 1 script(s) run, 32 scoped out` and named `tests/entities.py`. It printed `2 of 2425 ENTITY CHECKS FAILED` at this head and the same 2 on an `origin/main` worktree. The two failures are the `gate-sweep.yml` U0c pin and graders-head-copy's `delivery_status` case, and neither reads a file this diff touches. `tests/harness_headers.py` printed `ALL 112 HARNESS HEADER CHECKS PASSED`, and `tests/structure.py` printed `STRUCTURE RATCHET PASSED`.

## Figures

- 202 runs, INVERTED 27 / ORDERED 67, RED 13 INVERTED / 0 ORDERED (23 job attempts, 13 heads, 12 PRs), RERUN 10 (FRESH 2, CARRIED 8). Command: `env -u GH_TOKEN python3 -I dev/audit/harnesses/r10_codescan_wait_race.py --since 2026-10-22T00:00:00Z --until 2026-10-24T14:15:00Z --rows`.
- The 28.1 min median, from the edit run's `pr-contract` start to the code run's last codeql leg, over 12 red heads: the same command's `--rows` columns.
- 3 green and 2 red of 5 hand re-executions: `actions/runs/<id>/jobs?filter=all` for the red runs, as the record names.
- 87 `gate` attempts with `still being judged`, at 57 of 100 PR heads: the job logs of every red `gate` job in that listing, `FAIL ` lines only.
- About 95 min a day of expected loss: 13 instances in 32.7 h at an estimated 10 min each. The record marks the 10 min as an estimate.

## Red checks

none

## Forward-carry

- The verdict prelude must wait for every code run at the head, whatever its id (M1). The wait step must echo `codescan_wait.py`'s `FAIL closed:` line to the log (M3). Self-test cases must cover an edit run whose id is below a busy code run's (M4). All three are in `dev/audit/rca/R10-RCA-CODESCAN-WAIT.md` section 5. Carry: R10-CI-LAYOUT-P2

## Friction

- brief: stale: the brief cites `dev/programme/triage/s6-batch4.md#P62`, which is not on origin/main, and the one fetched ref that carries the file (`wip-sync/ext-wt-8aef46d4` `3545ece63`) lists P54 to P59 only. Carry: R10-CI-LAYOUT-P2
- brief: stale: the brief counts #2704 at `04860ee0` as a `codescan_wait.py` exit 1, but its check runs show both `pr-contract` runs green and a code-run `gate` red under the defer rule. Carry: R10-CI-LAYOUT-P2
