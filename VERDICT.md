Fix review: blocked bd88bca13ce433d838432184320a2ce9eea9bc6f ruling-refuted: P117 says the code writes the 15 snapshots learners/peak_tracker leaves and routes them to a coordinator writer, but coordinator.py:9335 omits peak_tracker deliberately and dev/audit/rounds/round10/D15/verify.md (D15-s1-05, weaken) already established they are legacy leaves no current code writes

bus-nonce: 83cca341bfcb9cf4f214f53e190a2e1b

## Round

Round 1 for this reviewer seat on #2813. Reviewed at head bd88bca13ce433d838432184320a2ce9eea9bc6f (merge base bc52ad2af1d0cfe95896119b649fa56e14c74b5b, which equals origin/main at read time). The roles directory diff from the merge base to origin/main is empty, so the contracts I read are current.

## Block

P117 (L5 -> R10-SAV-ACTUATION) is built on a premise the tree already refutes.

- The ruling's Instances line says the 3 `pump_duty` `written/silent/*` leaves and the 15 `snapshots` `learners/peak_tracker/*` leaves are ones "the code writes". Its Cost and Binding lines then route the snapshots half to "the coordinator tick that writes the `snapshots` leaves", and the carry text tells the fixer to list "the coordinator's snapshot save for `snapshots`" as the writer and to "declare it ... or stop writing it".
- At origin/main, `custom_components/heatpump_optimizer/coordinator.py:9335` sits inside the learner payload the snapshot save builds, and reads "peak_tracker deliberately absent: realised monthly peaks are billed facts, not learned state". No current code writes `learners/peak_tracker` (ev/p117_refute.txt).
- The same lead is already a verified finding in the tree. It is D15-s1-05 in `dev/audit/rounds/round10/D15/s1/REPORT.md`, and its row and attack in `dev/audit/rounds/round10/D15/verify.md` carry the verdict **weaken**: "silent: current writer (pump_arbiter _SLOTS). peak_tracker: NOT written by current code ... legacy snapshots only; sanitize dirty 0, consequence a debug log + sweep gap", and "22 of 25 are peak_tracker in snapshots persisted before peak_tracker was removed from learner payloads". P117 does not cite D15-s1-05 or its verify verdict. It treats as unverified a lead that the tree has already verified and narrowed.
- What follows from the false premise: (a) the routing reason for the snapshots half, that this group has the writer open, does not hold, because there is no writer to have open; (b) the carry's remedy "stop writing it" has no write to remove; (c) the control "after the change the stores self-test reports 0 off-domain leaves on a fixture that exercises both writers" passes trivially for the snapshots half on any synthetic fixture (D15-s1-05 measured 0 on synthetic), while the owner's persisted legacy leaves stay. That is a vacuous control.

The fix is a revision of P117 in this file:
1. Cite D15-s1-05 and its verify.md weaken verdict.
2. Split the two halves. The `pump_duty` `written/silent/*` half has a current writer (pump_arbiter `_SLOTS`). Declare it in `store.DOMAINS` (`store.py:464-467`) in R10-SAV-ACTUATION, which edits `pump_arbiter.py`. The legacy `learners/peak_tracker` half has no writer. It needs a load-time sweep or migration of persisted snapshots, or a recorded decision to accept the leaves as legacy.
3. Give the legacy half a destination that owns the store load path, or justify keeping it in R10-SAV-ACTUATION.
4. Give it a control that seeds a legacy snapshot carrying `learners/peak_tracker` and shows the self-test fall to 0 (null: a fresh snapshot shows 0 before and after).

No other ruling blocks.

## Findings

- P113's carry control "a series with a real window trips and freezes only the house learner" assumes the answer to the design call that the same ruling says is open ("whether COP, DHW, buffer and sysid should freeze on a suspected open window is a design call, not a fix"). At main, `_learning_frozen` returns `ventilation` for every caller (`coordinator.py:6677-6678`), and the house learner, after feeding the detector, freezes too (`coordinator.py:5427-5431`, `if vent_only: ... return`). The control should come from the design note, not before it. Amend it in the same revision as P117, or treat it as open in the design note. Carry: R10-COP-GATE
- P120's verdict line says "S to M", but its group op says "size S", and the op JSON (`triage-b24-group-legionella.json`) is in the orchestrator's directory, not in the tree. The brief text in the ruling is complete enough to create the group. The size should be set once, when the group is created. Carry: R10-LEGIONELLA-COMPLETION
- P115 calls the accuracy reading "the opposite direction" to the over-booking, but the two compare different things: plan against the relaxed DP optimum, and realised against predicted. A positive over-booking and a power_ratio above 1 do not contradict each other. I re-derived the signs at main (`accuracy.py:373-391`): power_ratio = actual / predicted, so 1.31 means realised above predicted; cost_error_percent = (predicted - actual) / actual x 100, so -29 % also means realised above predicted. The two fields agree with each other. The carry's instruction to reconcile still holds. Carry: R10-BUFFER-STORE
- P113-P122 count their instances from a REPORT.md that the ruling says is "a seat scratch file, not in the tree". They also cite the owner's rule ("no lead is deferred past the programme") and, for P122, `tools/era_perturb.py` and `tools/house_spec.py`, none of which is in the tree (ev/rederive.txt). The ruling says so plainly, and every carry is verify-first, so the cited figures route a verification and do not decide a change. Carry: dismissed: disclosed in the file; the carries re-measure at main before any fix
- The PR title is a merge-commit subject ("Merge remote-tracking branch 'origin/main' into triage/s6-batch24"), not a description of the batch. Carry: dismissed: a title is the orchestrator's to set at merge and is not part of the ruling record

## Evidence

- Merge: `git merge-tree --write-tree origin/main bd88bca13ce433d838432184320a2ce9eea9bc6f` gives tree 291a87732c8d6904067535137e869ddd2ee65f40, exit 0, no conflict (ev/head_and_merge.txt).
- Scope: the three-dot diff touches only `dev/programme/triage/s6-batch24.md` (+109) and `dev/programme/delivery/2813.md` (+1). VERSION, the manifest and the notes are untouched.
- Verdict figure: `grep -oE '^Verdict: (ACCEPT|DEFER|REJECT)'` gives 12 ACCEPT, 0 DEFER, 0 REJECT, which matches the body. `roster_edit.ruling_verdict` at the head returns ACCEPT for P111-P122 and None for P123, the body's null control, which I re-ran. Every ruling has Verdict, Source, Instances, Cost, Binding and one carry, brief or design-point text.
- Paths: 0 host or home paths in the batch file and in the delivery row.
- CI on the head: no check concluded failure. governance / instrument-self-tests was still in progress at read time, and so was a prelude in a superseded run (ev/ci.txt). There is no red check to answer.
- Destinations (ev/roster_destinations.txt, roster at origin/main and at origin/handoff/audit-r10-roster 159d163e5):
  - R10-FLOW-DESIGN-STAGES is not-started and holds `cloud_dispatch.py`; R10-FLY-POOL-INSTRUMENT is absorbed into it.
  - R10-TRAIN-OVERLAP-GRADE is queued and holds `merge_train.py`.
  - R10-COP-GATE, R10-SAV-ACTUATION, R10-HEAT-METER and R10-DIAG-REDACT are not-started.
  - R10-BUFFER-STORE is queued. Its first carry is the over-booking measurement from R10-DEMAND-OVERBOOK, as P115 states.
  - R10-HOUSE-GRADE is not-started, after R10-PARAMS-OWNER, and exists on the roster branch only.
  - No destination has a PR, a handoff commit or an open pull request. The open-PR search lists none for these groups; #2712 (R10-DEMAND-OVERBOOK) is open as a draft.
  - P115 and P117 correctly avoid R10-DEMAND-OVERBOOK (#2712 in the train) and R10-PARAMS-OWNER (PR about to open), as merge-STATE.md lists them.
  - I could not read the train spool or merge-STATE.md (orchestrator machine) beyond the brief's account.
- P120 new group: no group on either roster is named R10-LEGIONELLA-COMPLETION. The only groups naming legionella are R10-FAHRENHEIT (done), R10-LEAF-IMPORTS (done) and R10-PARAMS-OWNER (closing). R10-IMMERSION-LATCH's carry is the #2805 floor write in `setpoint_check.py`, and nothing on the roster duplicates the completion path. The ruling states how the group is created (`roster_edit.py append-group`). The functions and constants it names exist at main: `async_track_cycle`, `check_ceiling`, `raise_unreachable_issue`, `raise_unverified_issue` and `check_mode_block` in `legionella.py`, and `DHW_LEGIONELLA_HOLD_MINUTES` and `DHW_LEGIONELLA_BOOST_MAX_HOURS` in `const.py`.
- P122: 9d984a63bf956fa784e0287ecaeb8382c3d3dfd8 exists on origin (origin/handoff/audit-r10-roster). Its subject is "roster_edit append-group R10-HOUSE-GRADE", and it adds 49 lines to the roster creating that group. P122's verdict line cites it. The roster entry already carries the owner's spec carries (W/K, era normalisation, reason codes). P122's confirmed scope agrees with them and adds the measured figures. `envelope_score` is at `coordinator.py:2746`.
- Re-derived, one or more per ruling (ev/rederive.txt):
  - P111: 0 pool hits in `cloud_dispatch.py`, and `pool.py` is absent at main.
  - P112: `queue_lock`, `spool_read`, `spool_append` and `QUEUE_LOCK` exist; the front/remove hits are recarry and worktree-remove prose with no `add` arm.
  - P113: `_learning_frozen` is at 6610 and returns `ventilation` at 6678 for any keys; the caller lines 4937, 9992, 5249 and 10930 call it with the COP, DHW, buffer and sysid keys.
  - P114: the six writer lines 5251, 5368, 5430, 5521, 6509 and 6526 all assign `_learner_freeze_reason`.
  - P115: sign conventions as stated under Findings.
  - P116: `week_solve_ms` is in `debugger.py:308`.
  - P117: `store.py:464-467` declares no `written/silent`; the peak_tracker refutation is above.
  - P118 and P121: no code reference to re-derive; the figures are the report's own and the ruling says it did not re-run them.
  - P119: `_plan_age_minutes` is at `coordinator.py:7516`, with a handover overwrite at 758-763.
  - P120 and P122: as above.
  - I could not re-derive any owner-bundle figure, including the 66 days, 1.31, -29 %, 12.4 s and 272 s, 238 min, 5 of 8, and the house-grade numbers 16.7 to 60.4: the bundle and REPORT.md are not in the tree.
- Not re-derivable in P111: the seat-ledger line numbers and the count of 8 rpool fires. `seat-ledger.md` is not in the tree. The pool I claimed from (dispatch/rpool-s6 POOL.txt) does list dispatch/reviewer-2807-211c7eb4, the ref P111 names.
