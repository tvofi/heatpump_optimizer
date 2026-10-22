## Common to every P2a seat (R10-CI-LAYOUT-P2, sub-PR P2a "umbrella engine, inert"; Part of #2495)

You build ONE unit of P2a offline and return it on your handoff refs. You do NOT open a pull request. You do NOT write a delivery row. You do NOT post anything to GitHub. The orchestrator's integration seat assembles the five P2a units and the glue into one pull request on its own machine. Every GitHub write is the orchestrator's (decisions 0011 and 0013).

Plan refs, which you read from the refs and never from memory:
- the approved design: `git show 1371a0a6:DESIGN-P2.md` (also DESIGN-P1.md and RESPONSE.md, and the `measure/` tree at that commit). Read §2, §4 and §10 for your unit. The round-5 review is `afc00bfe`.
- the plan addendum and its design review: `git fetch origin plan/ci-layout` (tip 4a9b0975b). Read `plans/ci-layout/PLAN.md` (A1-A6) and `plans/ci-layout/DESIGN-REVIEW.md` (amendments, B1-B9, and the §6 unit list). tvofi's 2026-10-19 ruling sets a 60 s floor on every GitHub poll, overruling the 30 s and 15 s figures there.
- the execution plan: the P2a section is pasted below. The P2a/P2b split is approved as a Plan amendment, #201 comment 6343078022. Any interface change the later live probes find goes into P2b, never into a P2a-prime.

Rules for this seat:
- Base: fresh origin/main, in a worktree of your own under an ABSOLUTE scratch directory. Follow dev/governance/roles/fixer.md: failing test first, mutation proof, a null control for every quantified claim, then `python3 tests/structure.py` before the push.
- Set `PREPR_SKIP_CLOSURES=1`. Run `GATE_SCOPE=auto tests/run.sh` (the scoped gate); CI owns the closures. Use the gate lease (gate-scoping.md).
- Spare the GitHub API. Prefer git. You have no need of live GitHub calls: your unit is offline, with self-tests over fakes or saved JSON. Make at most a handful of reads if you must. Stop on any 403 or 429 and report it rather than retrying.
- When your diff changes any doc or comment that harness tooling reads, or any `docs/`, `dev/` or `tools/**/README` / `INSTRUMENTS.md` text, run `python3 -I tests/harness_headers.py` before the push and see it green.
- Self-test hygiene:
  - Your instrument has a `--self-test` printing exactly `<name> self-test: N checks, 0 failed`.
  - Any git repository a test needs is built through `tests/throwaway_git.py`; run `python3 tests/throwaway_git.py --check`.
  - A seat-selftest mutant goes in `dev/audit/harnesses/r10_seat_selftests_mutants.py`. It takes a per-file id (for example `ci_probe-1`), sits inside its instrument's own block, and is never appended at the end.
  - Any new `git push` site is registered in `PUSHERS` in `tools/audit/seat/ref_privacy.py`.
- Classify only your OWN new files in `tests/closure.py`, one line each, or tests/entities.py fails with "these force the FULL suite when touched". Do NOT edit `.github/workflows/*` or `tests/entities.py`. Do NOT touch any file another P2a unit owns (see the contract). The integration seat writes the workflow wiring and the entities pins.
- Never touch VERSION, the manifest version or the RELEASE_NOTES heading. Never re-record a value-bearing golden fixture.
- Your PR-body draft, which you push with body_push.sh, carries these headings:
  - "## Unit": which unit, its files, and its line count measured by `git diff --stat`;
  - "## Interface": exactly what you export against the contract;
  - "## Controls": each plant, null and mutant, with the command and its output;
  - "## Red checks": answer every check red on main's ancestry, one line each, today nightly-status. pr-contract refuses a body that leaves one out.
- Before the push: `git log origin/main..HEAD` holds only your commits, with no merge of a roster branch. The code head goes to `refs/heads/handoff/<topic>`, and the body goes through `bash tools/audit/seat/body_push.sh <topic> <body.md>`.
- Bound: about 400 production lines. A unit that cannot be sound within it stops and says so in its body (fixer.md step 17); it does not grow.
## Your unit: U0b, the sweep (sonnet, oracle-driven). Topic r10-ci-layout-p2a-u0b

Files you own (new):
- `tools/ci/sweep.py`
- `tools/audit/seat/sweep_driver.py`, plus its row in `tools/audit/seat/INSTRUMENTS.md`
- their tests
- classification lines for your own files in `tests/closure.py`

Do NOT edit `tools/ci/gate.py`. U0a's argparse calls `sweep.main(argv, get, post)`. Do NOT write `tools/ci/ghapi.py`. Code against contract item 1's signatures with injected fakes, and catch or propagate `RateLimited` from a local shim whose name and fields match the contract. The integration seat swaps the shim for the real `ghapi`.

What to build. Read DESIGN-P2 §2.1 (the gate-sweep row), §4.3 items 1 and 4, §10 ("The sweep on a probe ref: the driver"), and the round-5 must-fix items N5-1 and N5-4.

1. `sweep.main(["--run", id], get, post)`, for a CI completion whose `gate` is green at the PR's LIVE head:
   - Re-run the `gate` job of every older run at that head whose latest `gate` is completed and not `success`.
   - Then poll every older run whose `gate` attempt is requested and not completed (queued, waiting, pending, requested or in_progress; N5-4's wording), and re-run each one that completes red.
   - Bounds and limits:
     - poll interval at least 60 s (tvofi's floor);
     - ONE runs listing per poll for all the runs it polls;
     - 600 s bound;
     - each polled run re-run at most once;
     - never past attempt 45 (N2);
     - never the triggering run, never a green run.
   - Rate limits: on `RateLimited`, print `RATE-LIMITED`, re-run nothing until `reset_epoch`, and exit non-zero.
2. `sweep_driver.py` (seat-side, `gh api` with the seat token):
   - Every poll (at least 60 s here, which overrides the design's 5 s), list the probe PR's `ci.yml` runs at the head and their latest `gate` jobs.
   - N5-1: key on run ATTEMPTS, not status transitions. For each run, read each attempt up to `run_attempt` not yet swept: only attempt 1 under `--nochain`, every attempt under `--chain`. Log any attempt first seen already superseded.
   - Start `python3 -I <probe tree>/tools/ci/gate.py --sweep --run <id>` as a concurrent child.
   - Idle exit after 900 s.
   - One log line per sweep, as §10 specifies.
   - Read `/rate_limit` before each poll, and back off below 20 % remaining or on any 403 (A1 item 5).
   - It must never write except through the child's re-runs.

Controls:
- `measure/rev/driver_arm.py` at 1371a0a6 re-scored with your program's decision function: latency 20, 35, 65 and 125 s, both arms, END-BAD 0. Null: the driver not running moves every-suite to 16 of 34.
- Self-test plants:
  - a triggering run is never re-run;
  - a green run is never re-run;
  - attempt 46 is refused;
  - a superseded attempt is logged;
  - a stubbed 403 rate limit gives zero re-runs (null: an ordinary red IS re-run).
- Mutation proof.
## EXECUTION.md (revision 2), P2a section, pasted

### P2a units (from §1)

| unit | files | prod / test lines (est.) | depends on | runs as | lands in |
|---|---|---|---|---|---|
| **U0a** gate core | `tools/ci/prelude.py` (kind/pr/base/scope/legs derivation, A2 item 2 kinds); `tools/ci/gate.py` predicate + `--refresh` + A1 item 4 `RATE-LIMITED` outcome (fail closed, no re-run before `X-RateLimit-Reset`); B3 `REQUIRED[push]` enumerated by command from `tests.yml`; `tools/policy/fixtures/required-contexts.json` gains `gate_required` (additive, `contexts` unchanged); `tests/closure.py` `GATE_FILES += tools/ci/` | 400 / 250 (`gate_replay2`/`gate_sim` adapted to drive the port, TAIL and EARLY arms, fork plant R3-4) | nothing (offline) | **cloud, opus**, handoff `handoff/r10-ci-layout-p2-u0a` | P2a |
| **U0b** sweep | `gate.py --sweep --run` (N5-1 attempt keying, N5-4 status set, poll ≥ 60 s per tvofi 2026-10-19, one runs listing per poll, 600 s bound, attempt cap 45); `tools/audit/seat/sweep_driver.py` (`--chain`/`--nochain`, idle 900 s, ≥ 60 s poll, 403 back-off, A1 item 5) + `INSTRUMENTS.md` row | 350 / 200 | the P2a interface contract (§3.1); runs in parallel with U0a | cloud, **sonnet** (oracle: the sweep self-test, `driver_arm.py`) | P2a |
| **U9c** ruleset instrument | `tools/ci/ruleset_cutover.py` (`--dry-run`/`--apply`/`--rollback`, `set -e` semantics, absolute rollback path, the review's §4 preconditions 3a-3e, two-half read-back, rollback triggers printed), self-test over saved JSON, wired in `instrument-self-tests` | 250 / 150 | nothing | cloud, **opus** (it drives a security setting) | P2a |
| **UP** probe instrument (new; §2) | `tools/audit/seat/ci_probe.py`, trimmed to `push`/`dispatch`/`rerun-job`/`cancel`/`label`/`retarget`/`close`/`review`/`dismiss-review`; its `PUSHERS` row in `ref_privacy.py`; the `ci-probe/` family in `prune_refs.py`; the relay/bus null control (§0 item 2); `INSTRUMENTS.md` row, self-test with `tests/throwaway_git.py`, mutants under per-file ids (`ci_probe-1`…) inside its own block of `r10_seat_selftests_mutants.py` | 300 / 200 | nothing | cloud, sonnet | P2a |
| **U6-lib** alert lister | `tools/ci/alert_list.py`, ported from `measure/rev/alert_list.py`: N5-2 alert-level dismissed subtraction, N5-3 pinned `sort`/`direction`, 404 fails closed; its self-test and the `alert_list_mutants.sh` cases | 300 / 150 | the P2a interface contract (§3.1) | cloud, **sonnet** (oracle: `measure/rev/alert_list.py` and its mutants) | P2a |
| P2a glue | `governance.yml` `instrument-self-tests`: one step per new self-test; entities pins (`gate.py` `REQUIRED` == fixture `gate_required`; the forgery pins that need no `ci.yml`); `tests/closure.py` classification; `selftest_wiring.py --check` reads N/N/0 | 120 / 80 | U0a, U0b, U9c, UP, U6-lib | **local, integration seat (opus)** | P2a |

### P2a packaging and its interface contract (from §3)

**P2a, "umbrella engine, inert".** U0a + U0b + U9c + UP + U6-lib + glue. About 1720
production lines plus about 1030 test lines (est.); new files are most of it.
- **Mergeable alone, green under the 17:** no workflow trigger and no check name
  changes. The only workflow edit adds `instrument-self-tests` steps to
  `governance.yml`.
- **Sound alone:** each piece is a self-tested, CI-wired instrument.
  - `gate.py`'s `REQUIRED` is pinned equal to the fixture's new `gate_required`.
  - The ruleset instrument's `--dry-run` reads the live ruleset days before it is used.
  - `sweep_driver.py` and `ci_probe.py` are what the fan-out runs.
- **No dead window that matters:** `gate.py` has no caller until P2b, for about a day,
  but its self-test runs in CI.
- **Gates:** FULL (`tests/closure.py` gains `tools/ci/`). Code-owned
  (`/.github/workflows/`), approved under the mandate. Not policy.
- **What it buys:**
  - P2b's review surface drops by about half.
  - The two adversarial pieces get their own opus review: the gate predicate and the
    ruleset instrument tvofi will run.
  - Every unit cuts its probe ref from a base that already has the engine.

#### The P2a interface contract (binding on every P2a seat)

P2a is **not** one seat. It is about 1,720 production lines (est.), more than four
times the about-400-line fixer bound. The parts are independent once the contract
below is fixed, so they are built as **5 parallel cloud seats** (U0a, U0b, U9c, UP,
U6-lib). The integration seat then assembles them locally, with the glue.

1. **The API client.** All GitHub REST I/O inside `tools/ci/` goes through **one
   module, `tools/ci/ghapi.py`, owned by U0a**:
   - `get(path, params=None) -> Resp` and `post(path, body=None) -> Resp`, where
     `Resp = (status:int, headers:dict, json)`;
   - a `RateLimited(Exception)` raised on 403/429 whose body reads `rate limit exceeded`
     (A1 item 4), carrying `reset_epoch`;
   - `paginate(path, params)`;
   - the token from `GITHUB_TOKEN` / `GH_TOKEN`;
   - stdlib only (`urllib`).
2. **Injection.** Every other `tools/ci/` module (U0b's `tools/ci/sweep.py`, U6-lib's
   `tools/ci/alert_list.py`) is pure decision code over JSON. It takes an **injected**
   `get`/`post` with exactly that signature and raises or propagates `RateLimited`
   unchanged. Self-tests inject fakes. Nothing but `ghapi.py` imports `urllib`. The
   integration seat binds the injected functions to `ghapi` in P2a's glue.
3. **Entry points.**
   - `python3 -I tools/ci/gate.py --pr N --base B --kind K` (the predicate);
   - `--refresh`;
   - `--sweep --run <id>`. U0a's argparse dispatches to `sweep.main(argv, get, post)`;
     U0b writes `sweep.py` and must not edit `gate.py`.
   - `prelude.py` prints `key=value` lines for `$GITHUB_OUTPUT`, with the keys `kind`,
     `pr`, `base`, `scope`, `legs`.
   - Outcome words on stdout, first token: `PASS`, `FAIL <reason>`, `RATE-LIMITED`.
     A rate limit is never `PASS` and never re-run before `reset_epoch`.
4. **`REQUIRED`.** `gate.py` exposes `REQUIRED: dict[str, tuple[str, ...]]` keyed by
   event class. It is read by the entities pin against the fixture's new
   `gate_required` list, which is additive; `contexts` stays the 17 in P2a.
5. **Seat-side tools are not `tools/ci/`.** `sweep_driver.py` (U0b) and `ci_probe.py`
   (UP) live in `tools/audit/seat/` and use `gh api` (seat token), with:
   - a poll floor of 60 s;
   - a `/rate_limit` read before each write, refusing below 20 % remaining;
   - one log line per write.

   `ruleset_cutover.py` (U9c) uses `gh api` as the owner and is never run in CI except
   its offline self-test.
6. **Wiring.** Each seat delivers a `--self-test` that prints
   `<name> self-test: N checks, 0 failed`. The integration seat wires each one as a step
   in `governance.yml` `instrument-self-tests` (after #2579 merges) and re-runs
   `selftest_wiring.py --check` (N/N/0, rc 0). **Seats do not edit `governance.yml` or
   `tests/entities.py`**: the glue does.
   - Each seat classifies only its **own** new files in `tests/closure.py`, one line
     each, because `tests/entities.py` refuses an unclassified file.
   - U0a alone adds `tools/ci/` to `GATE_FILES`.
   - The integration seat resolves the adjacent-line conflicts in `closure.py`.
   - Every other file is touched by one seat only.
7. **Mutants.** Any seat-selftest mutants go in
   `dev/audit/harnesses/r10_seat_selftests_mutants.py`. They take per-file ids
   (`ci_probe-1`, `sweep_driver-1`), inside the instrument's own block, never appended
   at the end. Git repositories are built only through `tests/throwaway_git.py`.

