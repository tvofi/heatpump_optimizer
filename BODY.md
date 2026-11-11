Triage batch 168 rules two orchestrator requests made under mandate 6715477401. It holds two rulings.

- **P582, ACCEPT: GHCP-CARRY6-MQTT-OFF-HOME.**
  - R10-GENERIC-HEAT-CURVE-PERSISTENT's open carry 6 (ghc-d02, MQTT ECL110 arms on MODE_OFF and unload) goes to a new S group, R10-ECL110-MQTT-OFF-NEUTRAL, ordered `after` R10-ARBITER-OFF-RESTORE because the two share three files.
  - Statically, at main, the coordinator publishes nothing on MODE_OFF, so the last displace stands as the topic's last command. The brief measures that first, with the entity arm as the null control, then fixes it or dismisses it with evidence.
- **P583, REJECT (mapping repair) and DEFER (part granularity): PLAN-HELD-SIZE-NONE-MEASURED.**
  - "none measured as answered" means `durations.json` has no held record. It was recorded 2026-11-01, and 0 of today's 8 carries-open groups are in it. `prs_of_groups` maps PR 3402 correctly.
  - A re-measure moves this group by 0 min: a held group is `ceil(open / 11)` x 19.8 h, so 8 open and 1 open both give 1188 min.

The diff is one file against the merge base: `dev/programme/triage/s6-batch168.md`, the ruling. No product behaviour changes.

## Head

`175dda1f2085e9bfdad3b8a8cf0cfc239bbcc137`

## Mutation proof

This file's only consumer is the triage gate in `tools/audit/seat/roster_edit.py`.
- `ruling_verdict` reads P582 as ACCEPT and P583 as REJECT. A citation of P582 passes (`None`), and a citation of P583 is refused as "not an ACCEPT ruling (REJECT)".
- With P582's verdict flipped to REJECT, its citation is refused.

## Null control

- P584 is refused as "no such entry".
- With the file absent, a citation is refused as "not on the roster branch or origin/main".
- In P583's measurement, 1 open carry gives the same 1188 min as 8, which shows the stale record is not what set the figure.

## Figures

- `git diff --stat a7628041dc...175dda1f2085e9bfdad3b8a8cf0cfc239bbcc137`: 1 file, 1 commit.
- The figures are static reads at main `a7628041dc` and roster `de1cf3d732`. PR 3402's body was read once.
- 2 API calls (`gh pr view 3402`).

## Red checks

`none`. The merge base is main `a7628041dc`; its checks are not a red in this head's ancestry. This head's checks run after its push.

## Forward-carry

none

## Friction

none
