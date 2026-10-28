Triage batch 50 rules V162 (a shared REST poller and cache, filed after the shared token's core bucket hit 0/5000 at about 09:50Z) as P248, DEFER, to R10-ORCH-BEATD.

- **The standing polls are BEATD's.** Its one supervised beat replaces the tick, dispatch and roster seats with jobs, and runs CI and proof waits as watch jobs with 60 s floors.
- **The quota line already ships.** `orchestrator_tick.py` flags `API quota low` below 20 %.
- **The one exhaustion has no attributed consumer.** The cache as filed would span about 150 call sites, and the merge train's check-run read would gain a stale-green risk.
- **What would change the answer:** a second exhaustion, after BEATD arm (c) is live, with the consumer named.

The orchestrator's out-of-tree `orch_sweep.sh` repeats the board's per-PR check-run reads. That half is sent to the orchestrator, not carried.

No product behaviour changes: the diff is one markdown file under `dev/programme/triage/`.

## Head

`fa3eddc472ccb16b2caa3a8d387559109f6fd394`; the file is the whole diff against `0b8f8b585daf6a84ae9470389a709d5fec2a4f47`.

## Mutation proof

This file's only consumer is `tools/audit/seat/roster_edit.py`'s triage gate.
- On the committed file, `ruling_verdict` reads P248 as `DEFER`.
- A carry citing `#P248` is refused: `#P248 is not an ACCEPT ruling (DEFER)`.
- Mutant (the verdict rewritten to `ACCEPT` in a copy): the same carry passes, so the gate reads this line.

No carry is queued.

## Null control

With the file absent, the same call returns `the triage ruling dev/programme/triage/s6-batch50.md is not on the roster branch or origin/main`.

## Figures

- `gh api rate_limit` at 10:40:58Z (this endpoint does not count against core): core 494 used, 4506 remaining of 5000, reset 11:02:51Z; graphql 200 used.
- The seat ledger at 09:57Z (merge s8): the REST bucket was exhausted until 10:02Z, and the merge seat polled one GraphQL list per pass.
- The tick's docstring measures its own cost: 67 calls at 27 open PRs, 84 at 21.
- GitHub call sites by `grep -c`: `orchestrator_tick.py` 24, `merge_train.py` 113, `proof_watch.py` 6, `ci-watch.sh` 5.

## Red checks

`none`. A ref with no pull request has no checks.

## Forward-carry

none

## Friction

none
