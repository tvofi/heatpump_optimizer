# BLOCKED: R11-OUTSIDE-ROOMS-P2 (fixer), body push refused CARRY-LANDED

Question: `bash tools/audit/seat/body_push.sh r11-outside-rooms-p2 <body>` exited 4 at code head `884555c9a64729ef096e1ce84fb5bd3c78dfaf81` (pushed to `handoff/r11-outside-rooms-p2`): four forward-carries are not in their groups' briefs on the roster, which this seat may not write. Will the relay fold them (`carry_audit.py land-ops`) and re-run `body_push.sh` on the kept body?

State:
- Code: `handoff/r11-outside-rooms-p2` at `884555c9a64729ef096e1ce84fb5bd3c78dfaf81`, first clean `tools/pr/prepr.sh` head (`PRE-PR: 884555c9a64729ef096e1ce84fb5bd3c78dfaf81 ... rc=0`, `PREPR_SKIP_CLOSURES=1`), on R11-OUTSIDE-ROOMS-P1's handoff head `71609de6570ef91bcd846caee4158e16e7f1e339`.
- Body: kept by `body_push.sh` at `handoff-wip/r11-outside-rooms-p2-body` `d9350bf0a1315f8007aff2eceee4a591df8425b0`; it passes `prepr.sh --body-check` and the review packet (`3 live, 3 dispatched carries, 0 refused`).
- Nothing else is open on this seat's side; no further code is owed.

`body_push.sh` output (push transport lines left out):

~~~text
fill-red: `## Red checks` already names mutation; nothing written
figure_block: refreshed 1 block(s) at 884555c9a647
ref_privacy (body) ok: no host identity in the body
review-packet handoff: R11-OUTSIDE-ROOMS-P2 at 884555c9a647, 3 live, 3 dispatched carries, 0 refused
CARRY-MISSING R11-OUTSIDE-ROOMS-P2 body item 324a1354: not in its brief or carries: '- The cap under the band (1.0 K, `rooms.ROOM_LIFT_CAP_C`) and phase 2 as its own opt-in toggle, defa'
CARRY-MISSING R11-OUTSIDE-ROOMS-P2 body item daa69071: not in its brief or carries: "- A floor lifted to the comfort target raises the plan's peak above the unlifted plan's: `dev/audit/"
CARRY-MISSING R11-OUTSIDE-ROOMS-P3 body item e98789a8: not in its brief or carries: '- The why-now comfort-floor row and the daily narrative do not name the room lift (note item 5a1c0e0'
CARRY-MISSING R11-OUTSIDE-ROOMS-P3 body item fc1592bb: not in its brief or carries: '- A new options field moves `tests/golden/config_flow.json` and the D5 harness header counts (`dev/a'
CARRY-LANDED: 4 missing
body_push: a carry above is not in its group's brief or carries; land it on the round's roster branch (carry_audit.py land-ops), then push the body
body_push: REFUSED CARRY-LANDED
body_push: refused body kept at handoff-wip/r11-outside-rooms-p2-body d9350bf0a1315f8007aff2eceee4a591df8425b0
~~~
