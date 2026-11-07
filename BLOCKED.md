# BLOCKED: r10-rca-livehead-cancel, return push refused at CARRY-LANDED

The code is at `refs/heads/handoff/r10-rca-livehead-cancel`
(9bc716deb677f2a4933835782292677caa5245e6). `tools/pr/prepr.sh` passed clean on it
with the body: `PRE-PR: 9bc716deb677... rc=0`, origin/main 294a880dae60,
unmoved since.

`tools/audit/seat/body_push.sh r10-rca-livehead-cancel <body>` refused:

    CARRY-MISSING R10-CI-PRIORITY-PAUSE body item 7bd3e57f: not in its brief or carries
    body_push: a carry above is not in its group's brief or carries; land it on the round's roster branch (carry_audit.py land-ops), then push the body

The refused body is kept at `refs/heads/handoff-wip/r10-rca-livehead-cancel-body`
(55a19a839e80).

**The question.** Landing the carry writes `handoff/audit-r10-roster`, and this
seat's brief allows writes only to its return refs. Will a standing-roster seat
(`roster_edit.py`, `standing-roster.md`) apply the op below? Then this seat, or
the orchestrator, reruns `body_push.sh` with the body from the ref above.

    python3 -I tools/audit/carry_audit.py --roster-ref origin/handoff/audit-r10-roster \
        land-ops --topic r10-rca-livehead-cancel --body <body>

prints the one op owed:

    append-carry R10-CI-PRIORITY-PAUSE 'From r10-rca-livehead-cancel, body item 7bd3e57f: The finding changes the orchestrator's next pass: name the process sending `@tvofi` cancels at live heads (RCA section 6), then either land P267's bounded pause or refuse at that seat's cancel path. ... (items 7bd3e57f)'

The alternative is to route the item elsewhere. `Carry: dismissed:` would hide a
finding a later stage must act on, so this seat did not take it.
