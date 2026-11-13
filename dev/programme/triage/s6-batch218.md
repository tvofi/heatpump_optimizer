# Proposal triage, session s14, batch 218

Sources: triage queue lines 335 to 345. Lines 335 to 341 are seven PROPOSAL lines (orchestrator s14,
2026-11-11T22:08:52Z, items A1 to A7 of the adversarial review of the machinery convergence
study), ruled as P658 to P664, and the orchestrator's message of 2026-11-11 about 22:15Z on the
roster's one string `model`, ruled as P665. Lines 342 to 344 are three OWNER-RULED lines (tvofi, 2026-11-11, verbatim "I agree with all the recommendations." on the study review's Q1 to Q3), recorded as P666 to P668. Line 345, an OWNER-FACT, went straight to R10-HOTFIX-CARD-HEALTH-TEXT as a carry (roster queue line 4603) and needs no ruling. Line numbers are at origin/main 61afd4f2db. Roster
read at handoff/audit-r10-roster ea774b53f3. Every accepted part is a carry on an existing group,
so the open-PR cap does not bear on them.

## P658: A1, superseded main runs cancelled in a row

Verdict: ACCEPT as a carry on R10-CI-PRIORITY-PAUSE (a guarded main arm in cancel_superseded.py).

Source: triage queue line 335.

Instances, re-measured from the Actions API (ci.yml, branch main), 2026-11-11 about 22:10Z:
- 142 cancelled main runs in total, matching the review's 142 of 669.
- In the newest 100 main push runs, the longest unbroken row of cancelled runs is 7. In the newest
  50 it is 6. The review's row of seven after #3315, whose first concluded run was created
  4 h 55 min later, is that row of seven.
- No tool cancels main runs today. tools/pr/cancel_superseded.py refuses a main branch
  (:90-91 and :153), and carry 4 of R10-CI-PRIORITY-PAUSE exempts main-branch runs. Every main
  cancel in the s14 sweep record is a manual `gh` cancel (sweep.md lines 570, 579 and 619). So
  the rule the review asks for has no code home until one is built. The cancels themselves are
  the owner's decision (ruling 6, 2026-11-11), and this carry keeps them.

Duplicate check: carries 4 to 6 of R10-CI-PRIORITY-PAUSE cover pull-request runs and a zombie
cancel memory, and they exempt main. None bounds a run of main cancels. Not a duplicate.

Accepted change: add a `main` arm to cancel_superseded.py, the one sanctioned path for cancelling
superseded main runs. It never cancels the newest main run of a workflow. It refuses a cancel
that would leave more than three consecutive main runs of that workflow without a concluded one.

Basis: a medium defect. CLAUDE.md rule 1's promise that main goes red within one merge failed for
4 h 55 min.

## P659: A2, the train's wait cap expires during an outage

Verdict: ACCEPT as a carry on R10-TRAIN-RESIDUE-P2.

Source: triage queue line 336.

Instances:
- s14/sweep.md:636 (2026-11-11T20:57Z): GitHub's Webhooks/Actions incident, with 218 jobs
  queued. The train was SIGSTOPped by hand so that its wait caps would not expire (#3455 stood at
  4320 of 7320 s).
- The cap is counted in polls. tools/audit/seat/merge_train.py:2881-2893 adds each poll's sleep to
  `waited`, whatever the poll read. `wait_cap_s` (:3719-3722) is polls x (REVIEW_POLL_SECONDS +
  POLL_SECONDS). An unreadable listing returns at once, because `runs or ()` is empty, so the
  merge proceeds without the wait (docstring: "an unreadable listing is not a wait"). The same
  cap gates the rejoin of a skipped head (:3729-3733).

Duplicate check: no carry on R10-TRAIN-RESIDUE-P2 names an outage, an unreadable poll or the wait
cap. P655 (TRAIN-SKIP-RELEASES-WORKTREE, idx 19) is a different seam. Not a duplicate.

Accepted change: a poll that cannot read the run listing, or that reads while Actions is
measurably stalled, adds nothing to `waited` and does not end the wait.

Basis: a medium defect, worked around by hand during the instance.

## P660: A3, a hotfix handoff behind the board's 20-line cap

Verdict: ACCEPT the tick-board half as a carry on R10-TICK-RESIDUE-P3; REJECT the opener half and the R10-HOTFIX-OPENER-UNBLOCK destination (refuted: the opener has no line cap and already orders hotfix first).

Source: triage queue line 337.

Instances:
- s14/sweep.md:648 and :660: hotfix handoff r10-hotfix-selftest-scope-union-p2 sat behind
  "OWED handoffs capped at 20 of 68". It was opened by hand as #3482.
- The cap is tools/audit/seat/orchestrator_tick.py:2438. `stranded[:CAP_ORPHANS]` (CAP_ORPHANS =
  20, :182) takes bus.sh orphans in the order bus.sh prints them, with no class order.
- The opener half is refuted. open_driver.py reads `OWED ... handoff-no-pr` level lines
  (BOARD_RE :76), not the tick's capped `OWED handoff:` lines. It has no line cap, and it already
  orders hotfix, then outside and critical path (:32-38, :104-108).
- open-driver.log holds no line for this topic. So the opener never received the topic from the
  relay level. Why the level lacked it is not established here. That is the orchestrator's to
  measure, and it is not this carry.

Duplicate check: R10-HOTFIX-OPENER-UNBLOCK's brief (parts A and B: stale checkout, moved tip) and
the R10-TICK-RESIDUE-P3 carries do not order the capped list. Not a duplicate.

Accepted change: before the cap, the tick sorts the orphan lines with hotfix, outside and
critical-path topics first, using the opener's own class function. This needs no second
vocabulary.

Basis: a medium defect on the critical path, with one manual open.

## P661: A4, move P605 to the group that owns bus.sh

Verdict: ACCEPT the move: R10-CARRY-AUDIT-P5 carry 4 moves to R10-REVIEW-DISPATCH-RESIDUE's next part.

Source: triage queue line 338.

Instances:
- P605's carry (CARRY-LANDED-OWN-TOPIC) changes tools/audit/seat/bus.sh carry_landed. But it
  sits on R10-CARRY-AUDIT-P5, whose files are tools/audit/carry_audit.py only. That group is
  not started, and it comes after R10-BODY-CONTRACT, which is still in progress.
- R10-REVIEW-DISPATCH-RESIDUE lists bus.sh. Its part 1 is #3448 (open), and parts 3 and 4
  merged (#3450, #3445).
- The measured cost is from P656 (batch 216): 4 of 19 bus-refused dispatches were false
  (#3481, #3227, #3220, #3448), and they created 11 duplicate carries.

Duplicate check: this is a move, not a new carry. The text goes verbatim with its controls.

Basis: an architecture fix, putting the carry on the seam's owner, and a measured defect that the
carry's current home would delay.

## P662: A5, the Health-tab hotfix's test must fail on the released defect

Verdict: ACCEPT as a carry on R10-HOTFIX-CARD-HEALTH-TEXT, worded to the RCA's cause (contrast, not emptiness); REJECT the RCA half (already answered).

Source: triage queue line 339.

Instances:
- The RCA body (handoff-body/r10-rca-card-health-text f00f4a0233, BODY.md lines 7-33) finds the
  text present but painted at 1.24:1. `.adv-text`, `.adv-sub`, `.model-value` and `.adv-act` draw
  `--hpo-text` (theme-driven) on `--hpo-surface-2` (a darkMode literal) since 906fee95e (#2841).
  The mirror arm reads 1.11:1. The rows of the Advisor inbox are hit too.
- The group's brief, step 1, asks the test to assert that each row's label text is "non-empty".
  The released defect has non-empty text, so that test is green on it, and its mutation proof
  ("reverting the fix") could pass while missing the escape.
- The RCA half is already answered. BODY.md lines 51-59 name which checks ran green and why
  (`themeMismatch` measures `.tile, .hl-stat, .hl-narrative, .status-pill` only, and card.mjs
  PAIRS lacks the rows' `--hpo-text` pair).

Duplicate check: the group has no carries, and its brief's test is the non-empty one. Not a
duplicate.

Basis: severity, a critical-path hotfix whose stated test would pass on the defect.

## P663: A6, re-record the machinery ratchet down at closeout

Verdict: ACCEPT as a carry on R10-CLOSEOUT-PREP.

Source: triage queue line 340.

Instances, measured here:
- `python3 tools/audit/machinery_ratchet.py --measure --head origin/main` at 61afd4f2db reads
  nonproduction_merges 498 against a cap of 521 with a band of 5. That is 23 below, more than the
  band.
- churn_per_kilo_product_lines reads 12299 against 14797 with a band of 3636. That is within the
  band, so it is not re-recorded.
- dev/governance/config/machinery_budgets.json's `_comment`: "re-record a cap down when the
  measurement falls more than its band below it".

Duplicate check: no carry on R10-CLOSEOUT-PREP names the machinery budgets. Not a duplicate.

Basis: the budget file's own rule. Lowering a cap is not a raise.

## P664: A7, the freeze clause in the round playbook

Verdict: ACCEPT the clause as a carry on R10-ROUND-PLAYBOOK-FINAL; REJECT the scorecard citation (the scorecard is not in the tree).

Source: triage queue line 341.

Instances:
- The owner's ruling of 2026-11-01 is quoted in the plan's constraints table: "After v10.0.0 the
  machinery is frozen unless a change unblocks a production pull request, fixes a red, or proves
  20%".
- R10-ROUND-PLAYBOOK-FINAL's brief and 29 carries hold no freeze text: 0 matches for "freez".
  "Fixes a red" names no red. Tonight's 59-hour self-test red on main and a gate red are
  different things, and the review shows the difference matters (REVIEW.md 2.1).
- The scorecard of the study's section 7 lives only in a session directory outside the tree.
  brief_lint.mjs needs a resolvable citation, and ref_privacy refuses host paths. It can be cited
  only once it is tracked.

Duplicate check: no freeze carry on the group. Not a duplicate.

Basis: an owner ruling that no seat has yet written into policy. The definition of "a red" is
policy wording, and it binds only on the owner's approving review at merge.

## P665: the roster's one string `model`

Verdict: ACCEPT as a low-priority carry on R10-CI-PRIORITY-PAUSE (the roster_lib seam), superseding P525's REJECT on new facts.

Source: the orchestrator's message, 2026-11-11 about 22:15Z (no queue line).

Instances:
- At the roster ea774b53f3, R10-REPLAY-OPEN-LOG holds `"model": "sonnet"`. It is the one string
  among 478 groups: 469 objects, 8 null.
- tools/audit/seat/review_strength.py:251 calls `.get("fixer")` on it and crashes.
  tools/audit/seat/cloud_dispatch.py:182 and :202 read a non-dict as `{}` and silently drop it.
- P525 (batch 141) rejected the tool change because the datum was the cheaper cure. That cure is
  not available. roster_edit.py has no op that writes `model` (its ops are append-carry,
  append-group, edit-brief, mark-carry, set-after, set-files, set-resume, set-size, set-source,
  set-stage and wire-issue). The orchestrator rules out a hand commit on the roster.

Duplicate check: no carry names the model shape. R10-CI-PRIORITY-PAUSE is the only open group
whose files include roster_lib.py.

Accepted change: one reader, `roster_lib.group_model(group)`. It returns the object, maps a string
s to `{"fixer": s}`, and maps anything else to `{}`. review_strength.py and cloud_dispatch.py read
the model only through it. roster_edit.py append-group refuses a non-object `model` in the group
it adds. The existing datum is never refused, because the reader tolerates it.

Basis: a low-severity defect whose only cure is now a tool change. It is low priority within the
group, behind carries 4 to 6.

## P666: Q1, ci-ratchet advisory on a push to main (owner-ruled)

Verdict: ACCEPT as a carry on R10-HOTFIX-GATE-REDISPATCH-LOOP, marked build-on-next-red (owner ruling, not a cost/benefit question).

Source: triage queue line 342.

The owner's ruling (tvofi, 2026-11-11, verbatim "I agree with all the recommendations."):
`tests / ci-ratchet` becomes advisory on a push to main. It is built as a hotfix on its next red,
and otherwise in round 11. The push rule is tools/ci/gate.py:68 (`PUSH_ONLY = {"tests":
("coverage", "coverage-ratchet", "ci-ratchet")}`), joined into the push set at :88.
R10-HOTFIX-GATE-REDISPATCH-LOOP is the one open group whose files include tools/ci/gate.py.

## P667: Q2, a soak before v10.0.0 (owner-ruled)

Verdict: ACCEPT as a carry on R10-ROUND-PLAYBOOK-FINAL (owner ruling).

Source: triage queue line 343.

R10-ROUND-PLAYBOOK-FINAL's brief holds the closure criteria (both v10.0.0 and the catalog PR
landed). R10-CLOSEOUT-PREP's brief is the carry-file reconciliation and holds no stamp step. The
playbook therefore owns the closure stamp sequence. No open group owns tools/release/stamp.py, so
in this carry the soak binds as the playbook's closure step, not as a stamp refusal.

## P668: Q3, round-11 intake: the scorecard and the measurement groups (owner-ruled)

Verdict: ACCEPT as two carries: the D11/D13 paragraphs on R10-ROUND-PLAYBOOK-FINAL, and the scorecard's landing on R10-TICK-RESIDUE-P3 (owner ruling).

Source: triage queue line 344.

No open group lists dev/governance/dimensions/. R10-ROUND-PLAYBOOK-FINAL is the open closeout
group that edits policy (dev/audit/README.md, CLAUDE.md), so the paragraphs go there with the two
files added. The owner's ruling is the policy approval. The scorecard is recorded daily and is
report-only, which makes it a beat row. R10-TICK-RESIDUE-P3 owns tools/audit/seat/beat_jobs.py and
beatd.jobs.json. The reference script (62 lines) reads host paths and evals a study file
(`W=` and `FAMILY` from yield.py), so it lands rewritten, not copied.
