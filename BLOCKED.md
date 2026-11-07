# BLOCKED: r10-generic-heat-curve, the body push

The code is handed off: `refs/heads/handoff/r10-generic-heat-curve` at
`98ce151cff8b29c82836af504aca20804aa038dc`; `tools/pr/prepr.sh` ran rc=0 on it with the body
(`origin/main` at `364353e670f666be6c97a5942ffa0bea9132b5ce`, unmoved since).

`tools/audit/seat/body_push.sh r10-generic-heat-curve <body>` refuses at its carry-landing step:

    CARRY-MISSING R10-ARBITER-OFF-RESTORE body item 73eb63bd: not in its brief or carries
    CARRY-MISSING R10-GENERIC-HEAT-CURVE-PERSISTENT body items 73eb63bd, 67895f89, 711d4be1
    CARRY-LANDED: 4 missing
    body_push: ... land it on the round's roster branch (carry_audit.py land-ops), then push the body

Landing them means writing to the round's roster branch. This seat's brief forbids that
("Never write to any branch except your return refs ..."; "Never work around a hook or a
refusal"). The refused body is kept at `refs/heads/handoff-wip/r10-generic-heat-curve-body`
(body_push.sh keeps it), so nothing is lost.

**The question:** will the orchestrator (or the standing-roster seat) apply these
`roster_edit.py` ops on `handoff/audit-r10-roster`, then push the kept body with
`bash tools/audit/seat/body_push.sh r10-generic-heat-curve <the kept BODY.md>`? Or should this
seat be granted that one roster write?

`python3 -I tools/audit/carry_audit.py --roster-ref origin/main land-ops --body <body> --topic r10-generic-heat-curve` prints:

```
append-carry R10-ARBITER-OFF-RESTORE 'From r10-generic-heat-curve, body item 73eb63bd: The hook'\''s interface (this body'\''s "restore hook" list) changes how R10-ARBITER-OFF-RESTORE and R10-GENERIC-HEAT-CURVE-PERSISTENT must work: register a consumer and arm before the first write, never a second owner of the unload, MODE_OFF or remove path. Lands in those two groups'\'' entries in `dev/programme/rosters/wave-r10-groups.json`. Carry: R10-ARBITER-OFF-RESTORE. Carry: R10-GENERIC-HEAT-CURVE-PERSISTENT. (items 73eb63bd)'
append-carry R10-GENERIC-HEAT-CURVE-PERSISTENT 'From r10-generic-heat-curve, body item 73eb63bd: The hook'\''s interface (this body'\''s "restore hook" list) changes how R10-ARBITER-OFF-RESTORE and R10-GENERIC-HEAT-CURVE-PERSISTENT must work: register a consumer and arm before the first write, never a second owner of the unload, MODE_OFF or remove path. Lands in those two groups'\'' entries in `dev/programme/rosters/wave-r10-groups.json`. Carry: R10-ARBITER-OFF-RESTORE. Carry: R10-GENERIC-HEAT-CURVE-PERSISTENT. (items 73eb63bd)'
append-carry R10-GENERIC-HEAT-CURVE-PERSISTENT 'From r10-generic-heat-curve, body item 67895f89: For the persistent kind: the baseline is persisted per entry by `async_arm`, which answers the note'\''s O3 (a crash'\''s displaced value is never re-captured) and O4 (one owner); O1 does not arise, because the baseline is not in the options. O2 (budget and dwell across reloads) and O5'\''s endurance numbers (12/day, 7000/yr) stay that group'\''s, in `dev/programme/rosters/wave-r10-groups.json`. Carry: R10-GENERIC-HEAT-CURVE-PERSISTENT. (items 67895f89)'
append-carry R10-GENERIC-HEAT-CURVE-PERSISTENT 'From r10-generic-heat-curve, body item 711d4be1: ghc-d02, `decision: owner`: whether the MQTT ECL110 arms also publish displace 0 on MODE_OFF and unload. Not built: W7 keeps MQTT byte-identical. Lands in `dev/programme/rosters/wave-r10-groups.json`. Carry: R10-GENERIC-HEAT-CURVE-PERSISTENT. (items 711d4be1)'
```
