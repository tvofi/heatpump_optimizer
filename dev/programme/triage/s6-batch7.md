# Proposal triage, session s6, batch 7 (P65)

One ruling, S6-V11 of the s6 orchestrator's out-of-tree `proposals.md`, filed
2026-10-24T15:04Z. Numbering continues after `s6-batch6.md` (P64). GitHub calls: 0.

## P65: DECISION-OWED lines in to-main.txt read by no sweep step (S6-V11)
Verdict: DEFER; owner of the interim fix: the s6 sweep's step (10). Would change the answer: a DECISION-OWED or SEAT-OWED line left unread for a full sweep after step 10 was in force (the interim fix failed), or the tick gaining a cheap offset read (below) as a by-product of other tick work.
Source: s6 proposals.md S6-V11 (`grep -n 'V11' proposals.md` prints line 92). Candidate: the tick reads `to-main.txt` as a level and reports unacted lines as OWED.
Instances: 1 slip, many lines. The files named are the orchestrator's out-of-tree scratch files. `grep -c -E '^(DECISION-OWED|SEAT-OWED)' to-main.txt` prints 19 of the file's 32 lines (`wc -l to-main.txt` prints 32), the filing's lines 24-32 among them. Cost of the slip: a late find "by chance" (per the filing); no lost PR is cited, so the cost is unmeasured. The interim fix is already in force: `grep -n '^(10) Seat decision file' sweep.md` prints line 35, which reads every line newer than the last sweep via the `to-main.read` offset.
Cost: S -- a tick-side reader, an acknowledgement convention (the file has no acted marker: lines are appended and never struck, so "unacted" needs a new format or a second file), plus a self-test; recurring read in the tick loop on every pass.
Binding: the benefit is unmeasured now that step 10 exists, and an unmeasured benefit is DEFER, never ACCEPT. The "unacted" half of the candidate needs an acknowledgement format the file does not have, which is the complexity; reporting everything past the offset is just step 10 moved into the tick, with a second reader of the same offset that can race the sweep's advance. Null control for the re-rule: the number of DECISION-OWED lines the sweep read late after step 10 was added (`seat-ledger.md` entries naming a to-main line found late) must be nonzero for a re-rule to ACCEPT.
