# R10-ECL110-MQTT-OFF-NEUTRAL: re-dispatch at e23124ff6e finds the group already merged

Question: the resume head handoff/r10-ecl110-mqtt-off-neutral@e43f976d22 is already on origin/main (PR #3534, merge 727e37e7b1; `git merge-base --is-ancestor e43f976d22 e23124ff6e` exits 0), so a fresh handoff would describe an empty diff. Should this group be closed as delivered rather than re-handed off?

Evidence, measured 2026-11-13 at origin/main e23124ff6e:
- `python3 -I tools/audit/carry_audit.py --roster-ref origin/main landed --body <BODY.md of handoff-body/r10-ecl110-mqtt-off-neutral@6fca353df2> --topic r10-ecl110-mqtt-off-neutral` prints `CARRY-LANDED: 0 missing`, rc 0.
- Carry 0 (item 30ec8edf) is answered in that merged body: site (1) dismissed (the displace stays a curve offset owned by the solve); site (2) closed in the diff (`_apply_action` -> `async_publish_current_action(heat_pump_on=on)`). Carry 1 is already marked dismissed on the roster as a duplicate of carry 0.
- No code, handoff or body ref was pushed by this run.
