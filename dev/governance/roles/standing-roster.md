# The roster seat's contract (retired)

Retired (tvofi, 2026-10-24 card 1) into the `roster-drain` row of
`tools/audit/seat/beatd.jobs.json` (`standing.md`): queue
`tools/audit/seat/roster_edit.py` ops for it; a refusal is never retried past
the lint gate. The owner's constraint binds: the retirement
must not "cause you to run things inline" (`dev/audit/README.md`).
