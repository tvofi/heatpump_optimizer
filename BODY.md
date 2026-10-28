Triage batch 51 rules the four owner-approved cards filed after the 12:42Z power loss, V163-V166, as P249-P252.

- **P249 (V163, parallel opens and updates): REJECT.** At 16:03Z `tests/gate_lock.py slot-status` read 4/4 slots held by two `open_pr.sh` and two `update_pr.sh` runs. The concurrency asked for was already running, and `HEAVY_SLOTS = 4` admits no fifth run. Load was 64-75 on 8 cores.
- **P250 (V164, prepr reuse at the same code SHA): DEFER.** The open-time prepr runs no test gate. Most of its steps are keyed to the base, main or the body, and the open's merge with main changes the head. No per-step clock exists, so the reusable share is unmeasured. What would change the answer: per-step times for 10 or more open-time runs. The owner if it clears the bar is R10-PREPR-CAP.
- **P251 (V165, heavy runs on cloud under load): ACCEPT narrowed, as dispatch practice with no tree change and no roster op.**
  - S/M fixers, and reviewers that run mutation tables or full suites, go to cloud.
  - No local mutation table or full suite starts while load1 is above 50.
  - L/XL, critical-path and repeatedly blocked fixers stay local under the owner's 2026-10-24 ruling. Moving them is the owner's call.
- **P252 (V166, 30-minute wip refs): REJECT.** The fixer worktrees survived the power loss clean on disk, and 17 seat dirs already keep STATE.md or RESUME.md. The roughly 3 h was downtime. wt_sync.sh already snapshots worktrees off host. Its measured gap is cadence: one pass ran over 34 min because its scratch arm hashes 76,178 files one process each, so worktrees are snapshotted about every 50 min. The orchestrator's loop can close that without a tree change.

No product behaviour changes: the diff is one markdown file under `dev/programme/triage/`.

## Head

`6a0f1e936b519e02e1f3b3fb3e751d8231065cd1`; the file is the whole diff against `f844df1fe750d5e420af0d1555f4b9472a740413`.

## Mutation proof

This file's only consumer is `tools/audit/seat/roster_edit.py`'s triage gate.
- On the committed file, `ruling_verdict` reads P249 `REJECT`, P250 `DEFER`, P251 `ACCEPT` and P252 `REJECT`.
- A carry citing `#P249`, `#P250` or `#P252` is refused, for example `#P249 is not an ACCEPT ruling (REJECT)`. A carry citing `#P251` passes.
- Mutant (P249's verdict rewritten to `ACCEPT` in a copy): the same carry passes, so the gate reads this line.

No carry is queued. P251 is dispatch practice, not a roster op.

## Null control

With the file absent, the same call returns `the triage ruling dev/programme/triage/s6-batch51.md is not on the roster branch or origin/main`.

## Figures

- `python3 tests/gate_lock.py slot-status` at 16:03Z: `4/4 slots held ... queue=-`.
- `uptime` at 16:03Z: load averages 64.09, 75.32, 67.71; `sysctl -n hw.ncpu`: 8.
- Open durations, from creation to last write of each open's `p1.log`: 13, 16, 23 and 30 min.
- `ps -axo pcpu` at 16:05Z: 11 `tests/features.py` processes at 20-26 % each, from a local fixer's mutation table and a local reviewer.
- Resume proxies (seat dirs per group): 5, 4, 2 and 1, 12 in all.
- wt_sync pass started 15:33:21Z, still running at 16:07:55Z; scratch arm `find` count 76,178 files; 113 completed passes since 2026-10-24T08:14:41Z; `git ls-remote origin 'refs/heads/wip-sync/*' | wc -l` 524.

## Red checks

`none`. A ref with no pull request has no checks.

## Forward-carry

none

## Friction

none
