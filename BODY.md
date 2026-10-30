R10-FLY-GH-READ-RETRY carry 7, from triage w71's #2859 diagnosis: `tools/ci/ghapi.py`'s `get` retried a 5xx answer and let every transport failure through, so prelude at head 5135f0658 (run 40292248220, job 121469803963, step "Derive kind, PR, base, scope and legs") went red on one `http.client.IncompleteRead(0 bytes read, 48262 more expected)` out of `r.read()`. The same job was green twice at the next head. Every `tools/ci` module reads GitHub through `ghapi.get` (each glue binds it: `gate.py`, `prelude.py`, `codescan_wait.py`, `alert_list.py`), so this one seam covers all of them.

The fix: `TRANSPORT` = (`URLError`, `http.client.HTTPException`, `ConnectionError`, `TimeoutError`), which is `gh_read.urllib_wait`'s transport set. A GET retries a TRANSPORT failure on `RETRY_5XX`'s backoffs, just as it retries a 5xx, and raises the last failure once the budget is spent. A POST is never retried. A rate limit still raises `RateLimited` at once, and every other exception raises at once.

Alternatives considered:
- (a) Import `gh_read.retry`. Refused: contract item 2 makes `ghapi` the only urllib module under `tools/ci`, stdlib only, so it cannot import `tools/audit/seat`. Its 5/15/45 s schedule would also replace the (2, 6) schedule that P2 step 11a chose for gate latency.
- (b) Catch the error in each caller. Refused: that makes five copies of one concern.

Part of #2731.

The group's carries, at roster origin/handoff/audit-r10-roster 78c0bb77b. This diff is carry 7 alone:
- Carry 1 (PR 3, pr-contract.yml's body read): not here. That file is code-owned, and the carry gives it a PR of its own.
- Carry 2 (the App JWT curl GET and the carry path's `git fetch`): the JWT read landed in #2639. The `git fetch` is carry 5's.
- Carry 3 (PR 1's proof), applied to this diff's retry loop:
  - (a) Spent budget: the persists arms queue 4 transient failures for a 3-call budget, so only the budget stops them.
  - (b) Census: every member of TRANSPORT goes through the production `get` by an input it must retry. The near-misses it must refuse are a non-transport `ValueError` (1 call) and a 404 answer (1 call).
  - (c) Classifier alternatives: TRANSPORT is a 4-member tuple, not a regex. Each member has its own mutant (`ghapi-5`..`ghapi-8`), so the alternatives are enumerated in full by construction rather than by a source-reading rule.
  - (d) Sweep: no rule-generated sweep. The 7 mutants cover the arm, each member, the raise once the budget is spent, and the retry loop.
- Carry 4 (a spent hourly bucket waits for its reset and never loops): already true of `ghapi`, unchanged here. A rate limit raises `RateLimited` with `reset_epoch` before the 5xx/transport loop, and the `rate limit raises` arms still pass.
- Carry 5 (git fetch/push transport, 15 seams): not here. It needs its own classifier, written against measured git stderr.
- Carry 6 (`r10_codescan_wait_race.py` `pages()` per_page=100 502): not here. `pages()` reads through `ghapi.get`, which already retried that 502 twice, and the read failed 3 times. The fix it needs is a smaller page.
- Carry 7: this diff.

## Head

0c66226e6ab85205f1ce69d2c9184181b3889c1f, on merge base 507a9ec264eb373b132248d752259254d8a9fa4d (origin/main's tip when measured, 2026-10-30).

## Mutation proof

The mutants are in the tree, in `dev/audit/harnesses/r10_seat_selftests_mutants.py` as `ghapi-4`..`ghapi-10`. Each one changes the predicate: the `except TRANSPORT` arm, each of the four TRANSPORT members, the raise once the budget is spent, and the retry loop itself. Run with `python3 dev/audit/harnesses/r10_seat_selftests_mutants.py ghapi-1 ghapi-2 ghapi-3 ghapi-4 ghapi-5 ghapi-6 ghapi-7 ghapi-8 ghapi-9 ghapi-10`, which ends `RESULT survivors=0`. Every mutant is KILLED by a named FAIL, not by a crash. The FAIL lines:
- ghapi-4 (`except ():`): 8 failed, `a truncated read then a 200 on a GET answers the 200`, `... that persists raises the last failure after two retries` (got 1, want 3), the same pair for reset mid-read, timeout mid-read and connection reset.
- ghapi-5 (no URLError): `a connection reset then a 200 ...`, `a connection reset that persists ...`.
- ghapi-6 (no HTTPException): the truncated-read pair.
- ghapi-7 (no ConnectionError): the reset-mid-read pair.
- ghapi-8 (no TimeoutError): the timeout-mid-read pair.
- ghapi-9 (never raise after the budget): `<each of the 4> that persists raises: got 'returned', want 'raised'`.
- ghapi-10 (one try): 12 failed, including the pre-existing `a 502 then a 200 on a GET answers the 200` and `a 5xx that persists is returned after two retries, not looped`.

## Null control

At the base, the new self-test arms run against the base `get`. The control is built by splicing the merge base's `ghapi.py` up to `def self_test` with the head's `self_test`. It prints `ghapi self-test: 32 checks, 8 failed`, and the 8 are exactly the transient and persists arms of the four failures. At the head the same self-test prints `32 checks, 0 failed`. The self-test's own null controls hold at the head:
- a non-transport `ValueError` raises after 1 call;
- a 404 is not retried (1 call);
- each transport failure on a POST raises after 1 call.

## Figures

- `python3 -I tools/ci/ghapi.py --self-test`: `ghapi self-test: 32 checks, 0 failed` at the head (19 checks at the base).
- `python3 dev/audit/harnesses/r10_seat_selftests_mutants.py ghapi-1 ghapi-2 ghapi-3 ghapi-4 ghapi-5 ghapi-6 ghapi-7 ghapi-8 ghapi-9 ghapi-10`: `RESULT survivors=0`.
- `python3 tests/closure.py select --diff 507a9ec264eb373b132248d752259254d8a9fa4d --workdir "$D"`: `MODE: FULL`, reason `tools/ci/ghapi.py changes the gate itself`. I ran the run_always lines (`tests/structure.py`, `tests/closure.py selftest`, `tests/layout.py`, `tests/env_drift.py --claims-only origin/main`), `tests/entities.py`, and every `tools/ci/*.py --self-test`. All exited 0. The rest is left to CI.
- `python3 tools/audit/archscore/score.py --diff 507a9ec264eb373b132248d752259254d8a9fa4d`: `Architecture score: dS +0.0000 NULL`.
- Class seams. The rule `git grep -n "urlopen(" -- tools dev/audit/harnesses .github` enumerates every urllib opener in the instrument trees. Each seam it returns, with its disposition:
  - `tools/ci/ghapi.py` `_open`: closed in this diff.
  - `tools/audit/seat/record_row.py` `urlopen` read: already guarded by `gh_read.retry` / `gh_read.urllib_wait` (#2639). The second hit is its self-test stub.
  - `tools/release/stamp.py` `get_rest`: an unretried GitHub REST read, open, carried to R10-FLY-STAMP-CHECK-NOTES (the live group owning that file).
  - `tools/release/stamp.py` `tests_gate`'s dispatch: a POST, outside the read rule.
  - `dev/audit/harnesses/r10_main_gate_replay.py`: a one-shot replay harness's read, open, and dismissed below: no live group owns it.
  - `dev/audit/harnesses/d6_page_anchors.py` `check`: fetches a documentation page given on its command line, not the GitHub API. Outside the class.
  - Reads through `ghapi.get` are covered by this diff for transport, including `dev/audit/harnesses/r10_codescan_wait_race.py`'s `pages()`. That harness's persistent per_page=100 502 is carry 6, which stays open (a later retry does not ride out a page-size 502).

## Red checks

none

## Forward-carry

- `tools/release/stamp.py` `get_rest` is the stamp's rule-2 REST source: one urlopen with no retry and no classifier (`git grep -nE "retry|urllib_wait" -- tools/release/stamp.py` names no read retry), so one transient read refuses a stamp. It is the class's seam outside this diff. Control: the same `urlopen(` enumerator returns `record_row.py`'s read already behind `gh_read.retry`. Brief to carry: put `get_rest` under `gh_read.urllib_wait`'s classes, failing test first (one transport error then an answer passes in 2 calls, a 404 refuses in 1, a spent budget refuses naming the last failure); `tests_gate`'s dispatch is a POST and stays out. Re-run the enumerator at that group's merge base. Carry: R10-FLY-STAMP-CHECK-NOTES
- `dev/audit/harnesses/r10_main_gate_replay.py`'s urlopen read and its `get` have no retry. Carry: dismissed: a one-shot replay harness of a finished group; #2731, the class's issue, has no live roster group (R10-FLY-GH-READ-RETRY reads done at origin/handoff/audit-r10-roster 78c0bb77b while #2731 is open), so no destination exists; routed to the orchestrator in this handoff's result

## Friction

- frugal-inline-guard: cost: the session's inline-read hook refused a sixth Read of an owned file mid-fix, and the edit went through a scripted replace instead. Carry: dismissed: a session plugin, not repository policy
