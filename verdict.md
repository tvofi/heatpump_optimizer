Fix review: merge ac6c53581363fc4b6206e369bc13985c892db9cc

bus-nonce: 717189ed0b1c7db5d68f746f41bf58da

## Scope
Round-2 delta of #2813 (triage batch 24, P111-P122), at head ac6c53581363fc4b6206e369bc13985c892db9cc. Round 1 blocked ruling-refuted on P117 at bd88bca13ce433d838432184320a2ce9eea9bc6f. Only the re-ruled P117 is reviewed; the rest is confirmed unchanged.

## Verdict reasoning
(1) The 15 `snapshots` `learners/peak_tracker/*` leaves are now REJECTED, and the reason holds at this head: coordinator.py:9335-9336 ("peak_tracker deliberately absent: realised monthly peaks are billed facts, not learned state") sits inside `_learner_snapshot_payloads`, the snapshot learner payload; every other `peak_tracker` hit under custom_components/ is the live `_peak_tracker` object, persisted under `peaks` (coordinator.py:8130), not under `learners/`. No current writer emits `learners/peak_tracker`. verify.md row s1-05 (verdict weaken) says the same.
(2) The 3 `pump_duty` `written/silent/*` leaves: pump_arbiter.py:272 `_SLOTS = ("mode", "dhw_setpoint", "space_setpoint", "silent")`, and `_command` writes every slot through `_write`, which stores `held.written[slot] = (value, now)` and persists; store.py:464-467 declares `written/{mode,dhw_setpoint,space_setpoint}/{0,1}` only, no `written/silent`. R10-SAV-ACTUATION is on origin/main's roster (and the roster branch), stage not-started, not absorbed, no PR or train entry closes it. The carry names it, cites `triage: dev/programme/triage/s6-batch24.md#P117`, and says the legacy half is not built (Cost and Binding; carry: "Do not touch the 15 ...").
(3) Instances, Cost and Binding each carry their references (REPORT.md, coordinator.py:9335-9336, verify.md s1-05, pump_arbiter `_SLOTS`, store.py DOMAINS); see the findings for two citation imprecisions.
(4) Body figure "12 ACCEPT" reproduces. The PR changes only dev/programme/triage/s6-batch24.md and dev/programme/delivery/2813.md (three-dot). No host or home path in the diff. Merges cleanly with origin/main. CI on the head: no failed run, two still in progress.

## Findings
- The leaf count for the rejected half is not reconciled with the tree: P117 states 15 `learners/peak_tracker/*` leaves (from the out-of-tree live-bundle REPORT.md, which I cannot read), while the source it cites for the re-ruling, dev/audit/rounds/round10/D15/verify.md row s1-05, records 22 (of 25), and dev/audit/rounds/round10/D15/s1/REPORT.md:32 says 25. Likely a different bundle (P117 itself says the legacy leaves age out with the snapshot ring), but the file does not say so. It does not block: the half is REJECTED and routes no work, and the carry's instruction ("do not touch") holds at any count. Carry: dismissed: rejected half routes no work and the carry instruction is count-independent; reconcile the figure only if P117 is ever re-opened.
- The carry cites "`pump_arbiter.py` `_SLOTS`, lines 71-75": `_SLOTS` is at pump_arbiter.py:272; lines 71-75 are the module docstring describing the silent slot. The symbol is named, so a fixer finds it. Carry: dismissed: the symbol name resolves the citation; line numbers drift anyway.
- The carry asks R10-SAV-ACTUATION to edit store.py `DOMAINS`, but that group's roster `files` are coordinator.py and pump_arbiter.py only; P117's Cost line acknowledges no live group owns store.py. When the carry is appended, store.py should be added to the group's files so its scope gate does not refuse the one-line declaration. Carry: R10-SAV-ACTUATION
- The PR's title is "Merge remote-tracking branch 'origin/main' into triage/s6-batch24", and the body's `## Head` section holds three stacked paragraphs describing the head differently; under a squash merge the title becomes main's commit subject. Outside this delta's scope and not a ruling defect. Carry: dismissed: the orchestrator retitles the PR (triage batch 24, P111-P122) before merge; no code or ruling change follows.

## Evidence
- ev/HEAD.txt: the reviewed head.
- ev/diffs.txt: `git diff bd88bca13 ac6c53581363fc4b6206e369bc13985c892db9cc --stat` is 1 file (s6-batch24.md, +7/-7), all in the P117 hunk, so P111-P116 and P118-P122 are byte-identical to round 1; three-dot vs origin/main is the batch file and the delivery row only; `git merge-tree --write-tree` clean (rc 0).
- ev/p117_reads.txt: the coordinator, store, pump_arbiter, verify.md and s1/REPORT.md lines behind the reasoning above.
- ev/ruling_verdict.txt: RESULT P111..P122 ACCEPT, P123 None (null control); mutant P117 Verdict->REJECT makes ruling_verdict return REJECT and triage_refusal refuse a carry citing #P117, while the head lets it through.
- ev/ci.txt: check-runs and roster reads. governance / instrument-self-tests is still in progress on this head and was not observed completing.
- The 3 and 15 figures against the live-bundle REPORT.md could not be re-derived: that file is a seat scratch file, not in the tree. The 3 matches verify.md s1-05.
