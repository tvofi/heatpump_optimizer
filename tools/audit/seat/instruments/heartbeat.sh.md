# `heartbeat.sh`

- `heartbeat.sh` — the andon (Lean flow study K8, R10-FLOW-ANDON; cost-tested
  by R10-RCA-ORCH-CONTINUITY): `--once --message TEXT` force-pushes
  `heartbeat/orchestrator` as one parentless empty-tree commit whose message is
  the pass line `TICK-PASS <utc> relay=<..> tick=<rc>`, over the seat's own
  credential (`-f --no-verify`, the message through `ref_privacy.py guard`);
  a refused or failed push prints `HEARTBEAT NOT PUSHED: <reason>`, exits 1
  and never stops the loop. `--watch [--max-age 1200]` is the off-host
  watcher's command: it fetches the ref and exits 1 with `HEARTBEAT STALE: ..`
  when the committer date is older than the limit or the ref is absent. When:
  `tick_loop.sh` calls `--once` every pass; the owner schedules a cloud task
  every 15 min running `--watch` that notifies the owner on exit 1 (the
  schedule is owner-side, not in the tree). A standalone job script, so
  R10-ORCH-MACHINERY registers it as the beat's heartbeat job and retires the
  call from `tick_loop.sh`. Refusal: unknown option, a non-numeric
  `--max-age`. `--self-test` drives both modes over a bare-repo fixture, a
  stale ref and a fresh one.
