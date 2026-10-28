Triage batch 51 rules V163-V167 as P249-P253. V163-V166 are the four owner-approved cards filed after the 12:42Z power loss, and V167 comes from the #2910 round-2 reviewer.

- **P249 (V163, parallel opens and updates): REJECT.** At 16:03Z `tests/gate_lock.py slot-status` read 4/4 slots held by two `open_pr.sh` and two `update_pr.sh` runs. The concurrency asked for was already running, and `HEAVY_SLOTS = 4` admits no fifth run. Load was 64-75 on 8 cores.
- **P250 (V164, prepr reuse at the same code SHA): DEFER.** The open-time prepr runs no test gate. Most of its steps are keyed to the base, main or the body, and the open's merge with main changes the head. No per-step clock exists, so the reusable share is unmeasured. What would change the answer: per-step times for 10 or more open-time runs. The owner if it clears the bar is R10-PREPR-CAP.
- **P251 (V165, heavy runs on cloud under load): ACCEPT narrowed, as dispatch practice with no tree change and no roster op.**
  - S/M fixers, and reviewers that run mutation tables or full suites, go to cloud.
  - No local mutation table or full suite starts while load1 is above 50.
  - L/XL, critical-path and repeatedly blocked fixers stay local under the owner's 2026-10-24 ruling. Moving them is the owner's call.
- **P252 (V166, 30-minute wip refs): REJECT.** The fixer worktrees survived the power loss clean on disk, and 17 seat dirs already keep STATE.md or RESUME.md. The roughly 3 h was downtime. wt_sync.sh already snapshots worktrees off host. Its measured gap is cadence: one pass ran over 34 min because its scratch arm hashes 76,178 files one process each, so worktrees are snapshotted about every 50 min. The orchestrator's loop can close that without a tree change.
- **P253 (V167, Anthropic author identity): ACCEPT, narrowed to a guard arm in R10-FLY-NO-FOOTERS.**
  - The filing's rough count was right: 500 of 3906 commits on main in 7 days have an `@anthropic.com` author.
  - Since 10-26, 1 of 1002 does: `b9a66d28d`, from a cloud fixer that never set its identity.
  - `ref_privacy.py`'s guard already reads both emails on both push paths, and pins `noreply@anthropic.com` as passing. The carry adds the `anthropic-identity` class and flips that control.

No product behaviour changes: the diff is one markdown file under `dev/programme/triage/`.

## Head

`b64672f6a86097936f1963e87464c22bb08a3b4b`; the file is the whole diff against `f844df1fe750d5e420af0d1555f4b9472a740413`.

## Mutation proof

This file's only consumer is `tools/audit/seat/roster_edit.py`'s triage gate.
- On the committed file, `ruling_verdict` reads P249 `REJECT`, P250 `DEFER`, P251 `ACCEPT`, P252 `REJECT` and P253 `ACCEPT`.
- A carry citing `#P249`, `#P250` or `#P252` is refused, for example `#P249 is not an ACCEPT ruling (REJECT)`. A carry citing `#P251` passes, and so does the P253 carry text that is queued.
- Mutant (P249's verdict rewritten to `ACCEPT` in a copy): the same carry passes, so the gate reads this line.
- Mutant (P253's verdict rewritten to `REJECT` in a copy): the queued carry is refused, `#P253 is not an ACCEPT ruling (REJECT)`.

One carry is queued, held until this file is on main: `append-carry R10-FLY-NO-FOOTERS`, citing `#P253`. P251 is dispatch practice, not a roster op.

## Null control

With the file absent, the same call returns `the triage ruling dev/programme/triage/s6-batch51.md is not on the roster branch or origin/main`.

## Figures

- `python3 tests/gate_lock.py slot-status` at 16:03Z: `4/4 slots held ... queue=-`.
- `uptime` at 16:03Z: load averages 64.09, 75.32, 67.71; `sysctl -n hw.ncpu`: 8.
- Open durations, from creation to last write of each open's `p1.log`: 13, 16, 23 and 30 min.
- `ps -axo pcpu` at 16:05Z: 11 `tests/features.py` processes at 20-26 % each, from a local fixer's mutation table and a local reviewer.
- Resume proxies (seat dirs per group): 5, 4, 2 and 1, 12 in all.
- wt_sync pass started 15:33:21Z, still running at 16:07:55Z; scratch arm `find` count 76,178 files; 113 completed passes since 2026-10-24T08:14:41Z; `git ls-remote origin 'refs/heads/wip-sync/*' | wc -l` 524.
- `git log --since=7.days --format='%ae' origin/main | grep -ic anthropic`: 500 of 3906; over all history, 919 of 12434.
- `git log --since=2026-10-26T00:00Z --format='%ae' origin/main | grep -c anthropic`: 1 of 1002.

## Red checks

`none`. A ref with no pull request has no checks.

## Forward-carry

- P253 ACCEPT narrowed (V167): `ref_privacy.py`'s `email_leaks` refuses an `@anthropic.com` author or committer email as class `anthropic-identity`, with the `noreply@anthropic.com` null control flipped to a refusal arm and a guard-CLI arm. Carry: R10-FLY-NO-FOOTERS

## Friction

none
