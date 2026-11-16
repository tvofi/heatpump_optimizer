Design review: revise 9cebbb202dc93846f77b12303e5112cdc5727d92 architecture-unsound

Round 3. Reviewed from a detached worktree at 9cebbb202d (one file, design.md), judged against base 030a4d377f, the base the note names. Change since round 2: `git diff dd3283712b..9cebbb202d`, design.md only.

## Round-2 point and notes

- P1 (C, the refusal predicate): answered. The cited sites hold at 030a4d377f: `tools/audit/seat/bus.sh:563` (`BUS refused`, return 1); `tools/audit/seat/roster_edit.py:1345` (`LINT GATE REFUSED`, return 3); `tools/audit/seat/cloud-setup.sh:97` (`cloud-setup check: REFUSE`, return 1); `tools/pr/app_push.sh:159`; `tools/pr/push.sh:636`; `tools/pr/prepr.sh:1824`. A text predicate misses these, so exit status with structural exclusion rows is a sound replacement. The evidence row at :58 plants each refusal format, and each exclusion arm has a mutant.
- d-p2-head, b-hotfile-head: answered (handoff/r11-pre-round-metrics-p2 at 28c3ba15ee and design/R11-PRE-SECURITY-PRIVACY at 8f52783880, both unmoved at review). siblings: nothing was needed.
- d-fetcher: the reader is now named, but the answer opens point 1 below.

## Revise point

1. architecture-unsound, design.md:49 ([d-fetcher], "The reader"), and :13 (the part table's D row, "the run fetcher of [d-fetcher]").
   - The note adds a second fetcher of the CI run listing as a new seat instrument (gate_runs.py, promoted from the eval/r11 prototype). Its output is a jsonl directory that `loop_ledger.py --runs` reads.
   - That concern already has an owner at 030a4d377f. `tools/audit/seat/round_metrics.py:391` `fetch_runs` (the `produce` subcommand) pages `actions/workflows/ci.yml/runs` for every completed CI run since the round's start. It covers push and pull_request events and records `run_attempt`. It writes `ci_runs.json` and `runs.json`, and caches each run's job listing with `filter=all` under `jobs/jobs_<id>.json`. That listing returns the jobs of every attempt with their `run_attempt`, so attempt 1 red then attempt 2 green is already readable with no `/attempts/<n>` call. The cache is append-and-resume (`JOB_FETCH_MAX`, "job listings left for the next pass"), and the self-test runs on a fake paginator (`round_metrics_selftest.py:203`).
   - `round_metrics.py`'s `restore` read already computes red spells on main from the same input.
   - The note never names `round_metrics.py` (`git grep -n round_metrics 9cebbb202d -- design.md` prints nothing).
   - A second fetcher means two caches of one listing that can disagree, two input registrations in `field_coverage.mjs`, a new closure entry and a new file under one-in-one-out, for a record decision 0018's producer already keeps.
   - Fix wanted: D reads `round_metrics.py produce`'s directory.
     - Widen `fetch_runs`'s kept fields by what the clearing-event match needs: `head_sha`, `event`, `head_branch`, and the pull-request number from `pull_requests[]`. Keep the existing keys, so `runner_s`, `product_green` and `restore` are unchanged; their self-test arms prove it.
     - Point `loop_ledger.py --runs` at that directory.
     - Drop the new instrument and its `/attempts/<n>` widening.
   - D's evidence row at :59 keeps its plants, rebuilt as `ci_runs.json` plus `jobs_<id>.json` fixtures. The attempt case is one jobs file whose `gate` job has `run_attempt` 1 failure and 2 success, and it reads `external`. The same run with no jobs file reads `unread`.
   - If `round_metrics.py` is a hot file of a sibling in flight, the note says so and names the order. No open `design/*` ref names it at review time (`git grep round_metrics` over the 15 `refs/remotes/origin/design/*`).

## Routed

- decision: orchestrator. The `after` edges stand as round 2 recorded (D after R11-PRE-ROUND-METRICS part 2 merges, C after R11-PRE-TOKEN-LEDGER). If D extends `round_metrics.py`, check that file against R11-PRE-ROUND-METRICS part 2's diff and add any serial edge it needs.

## Notes for the fixer

- Part C step 2 (design.md:35): some non-zero exits are deferrals by the instrument's own contract, not refusals.
  - `tools/audit/seat/merge_pr.sh:533-538`: exit 3 is "the train's WAIT ... never RED, so a caller retries rather than reads a refusal".
  - `tools/audit/seat/cloud_relay.sh:276-299`: return 75 means "the pending-ci draft is held".
  - Report-by-exit instruments: `postmerge.py` (exit 1 when something is owed) and `mutant_run.py` (rc non-zero on a survivor).
  - Add a structural `deferred` scope row (75 EX_TEMPFAIL, plus each instrument-declared wait code, enumerated at the merge base by `git grep -n -E "WAIT|return 75|exit 75" -- tools .claude/hooks`), planted and mutated like `usage`, so a deferral prints in its own row and never counts as a refusal. List the report-by-exit instruments in the body.
  - Carry: R11-PRE-NO-READ-BUILDERS (item c-deferred)
- Part D (design.md:44): the [R1] sentence still reads "at acf0b72578" while the table row at :15 reads 28c3ba15ee. Cite part 2's merge commit once D builds. Carry: R11-PRE-NO-READ-BUILDERS (item d-p2-head-text)
- design/R11-PRE-TOOLCHAIN-PIN:design.md:30 uses `gate_runs` as stamp.py's existing function (`tools/release/stamp.py:774`). If any new file survives point 1, a module named gate_runs.py would collide with that name. Carry: R11-PRE-NO-READ-BUILDERS (item name-collision)
- design/R11-PRE-SECURITY-PRIVACY:design.md:77 (S5) also lists `actions/runs`, but for text scanning, not for gate status. It is not this concern. Carry: dismissed: different concern, no shared record (item s5-runs)

This is the third note. If it draws `revise` again, the designer re-cuts to the minimal shape (decision 0014; design-review.md "Three notes at most"), and the points above become carries.

Seat token count: not reported by this harness.
