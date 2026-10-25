Root-cause record for the `pr-contract / pr-contract` reds that `tools/ci/codescan_wait.py` exit 1 writes on a `CI edit` run while the code run's codeql is still analysing. The change is docs and one instrument: `dev/audit/rca/R10-RCA-CODESCAN-WAIT.md` and the read-only harness `dev/audit/harnesses/r10_codescan_wait_race.py`, plus the harness's `inert_reads` line in `tests/closures.json`.

**Cause.** The ordering keys on run ids, and GitHub does not hand out run ids in event order. The push and the body edit land in the same second. In 27 of 94 measured code-and-edit pairs the edit run got the lower id. `prelude.wait_earlier` waits only for lower ids, so that edit run waits for nothing, and `codescan_wait.py` step 1 (`source()`) then FAILs. **Process state (c):** DESIGN-P2 states the id order as an ordering guarantee and measured its premise by `created_at`; the code and its self-test case 6 follow the design exactly.

**Countermeasure, round 2.** Section 5 is re-taken against the tree. M2 (step 1 polls under the 600 s bound) and M3 (the FAIL line on stderr) are on `main` from R10-CI-LAYOUT-P2 carry 25 (`00a9ab4f2`, `cd376eb70`). M1 (a non-code prelude waits for a code run of any id) and M4's `prelude.py` case are built on R10-GATE-DEFER's branch `handoff/r10-gate-defer` `5150d1723`. M4's `codescan_wait.py` half is dropped, and the record says why. What is still owed is the precondition (M2 is legitimate only beside M1) and the before-and-after demonstrations. The record quotes that carry text for R10-GATE-DEFER, a live group, because R10-CI-LAYOUT-P2 is `done`.

## Head

9dead62bcb5039f862026587e7c0f8125e65566c

It is `a569538efd3d555efca3f1a888fc331bc8cabaa6` (the blocked round-2 head) plus one record commit and a merge of `origin/main` `5c0ee109305fc4f377c9326c712156b9ceb0e638`. All API figures below were read between 00:37Z and 01:15Z on 2026-10-25.

## Mutation proof

Each mechanism the record now cites as built is shown failing under a mutant of its own predicate:

- Harness: `python3 -I dev/audit/harnesses/r10_codescan_wait_race.py --selftest` printed `selftest: 9 checks, 0 failed`. In round 1, flipping `inv = e["id"] < low` to `>` printed `9 checks, 5 failed`. The harness is unchanged since then (`git diff a569538ef HEAD -- dev/audit/harnesses/` is empty).
- M3 on main: `python3 -I tools/ci/codescan_wait.py --self-test` printed `17 checks, 0 failed`. With `, file=sys.stderr` removed from `main()`'s `Fail` print, it printed `17 checks, 1 failed` (case 16, "a refusal of the wait itself is on stderr too").
- M1 at R10-GATE-DEFER `5150d1723`: `python3 -I tools/ci/prelude.py --self-test` printed `29 checks, 0 failed`. With `waits_on` reduced to `run["id"] != run_id and run["id"] < run_id` (main's id rule), it printed `29 checks, 1 failed`: "M1: waits for a LATER code run".

## Null control

- In the M1 mutant, the ordered-pair case ("waits for an earlier run, not a later non-code or held one") still passes, so the mutant removes only the inverted-pair wait.
- Harness, same window as the record: 0 of 67 ORDERED edit runs are red. Every red head is INVERTED with `leg_unfinished True` (`--rows`).
- The scoped gate (`python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)`) printed `MODE: SCOPED -- 1 script(s) run, 32 scoped out` and named `tests/entities.py`. With `PYTHONPATH=tests/hastub` it printed `2 of 2429 ENTITY CHECKS FAILED` at this head, and the same `2 of 2429`, the `gate-sweep.yml` U0c pin and graders-head-copy's `delivery_status` case, neither reading a file this diff touches, on an `origin/main` `5c0ee1093` worktree. The run-always lines printed `claims hygiene: ... ok`, `ALL 117 closure shrink pins PASSED`, `layout self-test: ok` and `ALL 112 HARNESS HEADER CHECKS PASSED`. `tests/structure.py` printed `STRUCTURE RATCHET PASSED`.

## Figures

- Window `2026-10-22T00:00:00Z..2026-10-24T14:15:00Z`, re-read at 00:37Z: 202 runs, `INVERTED 27, ORDERED 67`, `RED edit runs: 16 INVERTED, 0 ORDERED; 28 job attempts, 16 heads, 14 PRs`, `RERUN ... 12 (FRESH 2, CARRIED 10)`. Command: `env -u GH_TOKEN python3 -I dev/audit/harnesses/r10_codescan_wait_race.py --since 2026-10-22T00:00:00Z --until 2026-10-24T14:15:00Z --rows`. The first read (13 / 23 / 13 / 12, RERUN 10) predates four heads finishing red.
- Bound against gap: the rule is the `--rows` lines with `red_attempts` above 0 and a `last_codeql_leg_done`, in minutes from `edit_pr_contract_start`. At the first read that was 12 heads (the 13 red heads less `cd7dc09a`, then unfinished), median 28.1 min. Re-read, it is 16 heads, 0.4 to 43.8 min, median 26.2. 14 of the 16 are above 600 s: only `16d3ee72` (0.4) and `3580acc0` (6.1) are not.
- #2756's `718fcadb`: edit run 40123245316 is below code run 40123245376, both created 18:59:50Z. `pr-contract` job 120959896354 started 19:03:25Z and logged `FAIL closed: ... after 600 s` at 19:12:59Z. The python leg completed 19:26:29Z, 23.1 min after the start. Sources: `commits/<sha>/check-runs?filter=all`, `actions/runs/40123245376/jobs?filter=all`, `actions/jobs/120959896354/logs`.
- These figures are carried unchanged from round 1 and were not re-taken: 87 defer-rule `gate` attempts at 57 of 100 heads; 3 green and 2 red of 5 hand re-executions; the 10 min estimate (which the record marks as an estimate).

## Red checks

Read from `commits/<sha>/check-runs?filter=all` for every commit in `$(git merge-base origin/main a569538ef)..a569538ef`. The `cancelled` runs at `fb98e610a` were superseded by the next push, and none is red.

- `pr-contract / pr-contract` 120959896354 at `718fcadb2`, run 40123245316 (the edit run of an inverted pair): `FAIL closed: no run at this head owns a finished codeql unit for base 'main' after 600 s`. This is the record's own defect, with M2 already on main, failing at its bound as the M2 row predicts. **The cheaper detector** is M4's `prelude.py` self-test case, an edit run below a busy code run must wait. It costs under 1 s in `governance`'s self-test step and is built at R10-GATE-DEFER `5150d1723` (Mutation proof above). Carry: R10-GATE-DEFER
- `gate` 120962237384 at `718fcadb2`, same run: the gate reading the red `pr-contract` above. It needs no separate detector, since the same case covers it. Carry: R10-GATE-DEFER
- `gate` 120973683700 at `a569538ef`, code run 40124637935: `FAIL run(s) [40124909955] at this head are still being judged; their gate decides`. That is the designed defer red (the #2704 shape, M5), and `gate` 120973809899 on run 40124909955 went green at 20:04:26Z. **The cheaper detector** is a `gate.py` self-test row in which a deferring gate publishes no red. It costs under 1 s, and it is R10-GATE-DEFER's brief ("a self-test row for the deadlock shape"). Carry: R10-GATE-DEFER

## Forward-carry

- The precondition and the demonstrations of record section 5 must enter R10-GATE-DEFER's brief. The precondition: M2 is legitimate only beside M1, because the 600 s bound is below the edit-to-last-leg gap on 14 of 16 red heads. The demonstrations are the M1 mutant with its ordered-pair null, and the harness over 24 h after the merge printing `RED edit runs: 0 INVERTED` with INVERTED above 0, against the 24 h before as the null. The text is quoted verbatim in the record. This is a roster write (`python3 tools/audit/seat/roster_edit.py append-carry R10-GATE-DEFER @<file>`), which is the orchestrator's: this seat writes no branch but its return refs. R10-GATE-DEFER is `in-progress` on main's roster at `5c0ee1093`, and its `carry` list is empty there. Carry: R10-GATE-DEFER
- Main's roster, R10-RCA-CODESCAN-WAIT `carry[0]`, says M3 "stays owed here". M3 has been on main since `00a9ab4f2` (Mutation proof). That carry is satisfied, so the orchestrator may drop it (`roster_edit.py drop-carry R10-RCA-CODESCAN-WAIT 0`). Carry: dismissed: satisfied on main by carry 25

## Friction

- brief: stale: the brief cites `dev/programme/triage/s6-batch4.md#P62`, which is not on `origin/main`. Main's roster carries P62's text as R10-CI-LAYOUT-P2 `carry[27]`, a group that is now `done`. Carry: dismissed: superseded by main's roster routing
- brief: stale: the brief counts #2704 at `04860ee0` as a `codescan_wait.py` exit 1. Its check runs show both `pr-contract` runs green and a code-run `gate` red under the defer rule, which is R10-GATE-DEFER's subject. Carry: R10-GATE-DEFER
- harness: cost: the window after #2756's first read, `--since 2026-10-24T14:15:00Z --until 2026-10-25T00:30:00Z`, was not taken. Its three reads each failed with `ghapi.ApiError: ... HTTP 502`, once on run 40108409300's jobs and twice on run 40126133450's. Run 40126133450 is a 7-attempt `CI code` run of #2704. For it, `jobs?filter=all&per_page=100&page=1` answers 200, `page=2` answers 502, and `per_page=30` answers 200. The harness's `pages()` asks for 100 per page and does not retry. The window is not evidence for this repair either way, because M1 is not on main. But the after-merge demonstration the carry asks of R10-GATE-DEFER runs this harness over such runs, and it needs a smaller page or a retry on 5xx first. Carry: R10-GATE-DEFER
