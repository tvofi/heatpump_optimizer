# Proposal triage, session s14, batch 202 (P628-P630)

Sources:
- Roster `handoff/audit-r10-roster` at `003806b637`. The groups owning `merge_train.py`,
  `replan.py` and `cloud_relay.sh` were read there.
- origin/main `ceb3070ccb`.
- The live merge-train log, `~/.local/state/hpo/merge_train/train.log`: 20305 lines. Today's runs
  start at line 19380, `start=2026-11-11T00:28:34Z`.
- `gh api repos/tvofi/heatpump_optimizer/actions/runs?event=pull_request_review&created=>=2026-11-11`:
  53 runs. The gate job log of each failed run was read.
- The relay log, `$HPO_STATE_DIR/cloud-relay.log`.
- The s14-20 replan scenarios, `seat/triage/s14-20/rp2/<scenario>/out.json`, snapshot
  2026-11-11T13:58Z.

## P628: the merge train waits on the review run its own approval starts

Verdict: ACCEPT narrowed, as a new group R10-TRAIN-REVIEW-PRESETTLE (S, fixer sonnet, reviewer
opus, severity normal). The train approves every queued entry when the batch starts, so each
entry's `CI review` run finishes while earlier entries merge. Neither branch of the queue line's
`e.g.` is taken.

Source: triage queue line 306, 2026-11-11T14:00:39Z, orchestrator s14, THROUGHPUT.

The mechanism, read in `tools/audit/seat/merge_train.py` at origin/main:
- Step 6, `approve()` (:2325), posts the App's approval at the head right before the merge.
- The approval starts a `CI review` run of ci.yml. That run's new `gate` check is pending at the
  head, so base-branch policy refuses the merge until it concludes.
- `review_settle()` (:2870) therefore polls. It logs `still running; the merge waits (N s of
  7320 s)` once per 300 s.
- The review run is already light. `prelude.py` (:55, :170) runs only `budget-raise-gate` on a
  review. Its time is runner queueing, plus the prelude waiting on earlier runs at the head.

Instances, from train.log since line 19380 (parser: `seat/triage/s14-21/waits.py`). Each figure
is the last logged value, so the true wait is up to 300 s more:
- 22 entries merged today, and 11 of them waited on a review run.
- The logged total is 2800 s, so the true total is 2800-6100 s. Over the train's 13.6 h active day
  that is 6-12%.
- The saturated window is different. Merge times are origin/main's first-parent committer dates
  (`git log --first-parent --format=%cI`, +01:00 converted to Z). From #3425's merge at 11:13Z to
  #3447's at 14:05Z, the train merged 3 entries in 172 min. Their waits:
  - #3459: 0 s
  - #3453: 1020-1320 s
  - #3447: 1320-1620 s
  - In total that is 39-49 min of 172 min, so 23-28% of the train's time in that window.
  - Per entry, for the two that waited: #3453 waited 17-22 min of its 23 min since #3459
    (13:07Z to 13:30Z), which is 74-96%. #3447 waited 22-27 min of its 35 min (13:30Z to
    14:05Z), which is 63-77%.
- `CI review` run duration, from created to updated:
  - Since 10Z (n=15): median 2099 s and max 8998 s. Saturation is rising.
  - Over the day (n=50): median 836 s.
- With 9 entries spooled at today's 1020-1620 s, that is 2.6-4.1 h of serial wait.

Null control (does a review run ever change the gate's answer?):
- Of 50 completed review runs, 41 succeeded and 9 failed.
- 7 failures are the `gate` job. I read the gate log of each of these 7. Every one prints
  `FAIL <context>: failure (run <id>)`, and in each the failing run is an EARLIER code run at
  that head (`pr-contract` x3, `tests / fast (3.14)` x4). So each head was already red.
- 1 failure is `refresh` (#3405, run 42932587919), not `gate`.
- 1 failure is #3451's 43011857024. Its log was not read. Its two sibling review runs cite #3451's
  red `tests / fast` code run.
- No review run turned a green head red. So the run's only job is the policy catch-up, and
  starting it earlier loses nothing.

Cost/benefit:
- The benefit is 23-28% of the train's time over the saturated window, and 63-96% per waiting
  entry, while runners are saturated. That clears the 20% bar
  on the train lane. It clears the machinery rule's 10% to change an existing lane.
- It does not clear the bar on programme completion. The plan's closure is set by fixer chains:
  the binding chain carries 2 merges, about 50 min of a 94.8 h horizon, under 1%.
- The whole-day share (6-12%) is below the bar. The ACCEPT therefore rests on the saturated
  window, which is the present state with about 50 runs queued. It is not a claim about an idle
  runner pool.
- Cost:
  - About 40-80 lines in `merge_train.py` plus a selftest.
  - No new REST reads: `approve()` already reads `_reviews` once per head.
  - The number of review runs is unchanged, since there is one approval per head either way.
    The runs only start earlier.
- No `tests/structure_budgets.json` row names `merge_train.py`
  (`git grep -n merge_train.py -- tests/structure_budgets.json`: no hit).

Rejected alternatives:
- (1) The train does not wait for a review run at a green head. Rejected: the pending review-run
  `gate` blocks the merge under base-branch policy. Skipping the wait only turns it into the
  108-line `base-branch policy refusal` class already in train.log.
- (2) Cancel the review run as superseded. Rejected: a cancelled required check is not a pass.
- (3) ci.yml starts no review run at an unchanged head. Rejected:
  - `tests/entities.py` pins ci.yml's triggers and a `gate` whose `if:` no event can make false.
  - The review run carries `budget-raise-gate`'s re-judgement at the owner's review (0013).
  - That makes it a policy-surface change, for a gain the narrowed design gets without touching
    ci.yml.

Placement:
- R10-TRAIN-RESIDUE-P2 owns `merge_train.py`, but it is in progress with #3470 open and 18
  carries. A carry there would add a round to an open PR.
- R10-GATE-DEFER-BARRIER, R10-SEAT-SCRIPT-OUTPUT, R10-GH-READ-RESIDUE-P3 and
  R10-INTRODUCED-REDS-BARRIER are other seams.
- So it is a new S group, after R10-TRAIN-RESIDUE-P2, with overlap admitted on `merge_train.py`.
  Its seam is the approve step and `review_settle`.

Acceptance, in the train's selftest:
- (i) In a batch of N entries, each entry whose head is verdicted, carry-checked and gate-green
  is approved once when the batch starts. `approve()` at merge time then returns
  `already, at this head` and posts nothing.
- (ii) An entry whose head moves (recarry or main-moved) is approved afresh at the new head, as
  today.
- (iii) An entry that fails a pre-approval check (no verdict, CARRY no, red gate, a policy path
  without the mandate, a budget raise) is not pre-approved. Step 6 judges it at its turn,
  unchanged.
- (iv) Null control: with one entry, the order of calls is unchanged from main.
- (v) Mutation:
  - Dropping the pre-approval makes (i) red, because the selftest's stub review run has not
    concluded at that entry's turn.
  - Pre-approving a CARRY-no entry makes (iii) red.
- (vi) Replay: on today's #3453/#3447 timeline, their review runs would start at the batch's
  start, after #3425 merged at 11:13Z. Today they start at approval, 13:38:09Z for #3447's run
  43030906050, whose wait (1320-1620 s) would then fall to about 0.

Binding: train time under runner saturation, 23-28% over the window and 63-96% per waiting entry, measured. Whole-day 6-12% stated.

## P629: replan exempts the binding chain from the coordinator cap

Verdict: REJECT as an instrument change. The 9.8 h is available now as an orchestrator dispatch
decision, at no code cost (below).

Source: triage queue line 307, 2026-11-11T14:18:51Z, orchestrator s14 via triage s14-21,
PLANNER.

Instances (s14-20 scenarios, coordinator cap 3, snapshot 2026-11-11T13:58Z, roster carrying the
dropped R10-WATER-SETPOINT-FEEDBACK edge that landed at `823f5d12bf`):
- `S-arb-noafter-c3`:
  - closure is 2026-11-15T12:44Z.
  - R10-ECL110-MQTT-OFF-NEUTRAL has `start_reason` `coordinator cap 3: waited for a coordinator
    slot`. It starts 2026-11-14T13:20Z, at tier 4.
  - The binding chain is R10-ARBITER-OFF-RESTORE -> R10-ECL110-MQTT-OFF-NEUTRAL, with 24.92 h
    slack.
- `S-arb-noafter+ecl-nocoord-c3`:
  - closure is 2026-11-15T02:56Z, and ECL110 starts 2026-11-12T11:46Z.
  - The binding chain moves to R10-WATER-SETPOINT-FEEDBACK -> R10-DUTY-SWITCH-RESTART-LEARNING
    -> R10-START-COUNTER-EDGES.
- In both, `critical_path` is R10-FIXER-MD-SPELLING-CORPUS -> R10-STANDING-CONTRACTS-P2 ->
  R10-ROUND-PLAYBOOK-FINAL. That is the longest-work path (69.82 h), and ECL110 is not on it.
- The saving is 9.8 h of the 94.8 h from snapshot to closure, which is 10.3%.

The policy reading:
- `orchestrator.md` section 5 exempts "a group in the current plan's `critical_path`". That is
  exactly what `replan.py` exempts (`pick(..., cap_exempt)`, :1140; `critical_path()`, :395).
- So the plan follows the letter, and ECL110 is not a section-5 group today.
- Exempting the binding chain is therefore a change to which groups the cap rule exempts, not a
  repair. Severity is normal at most, and the 20% bar applies.

Cost/benefit:
- 10.3% on programme completion is under the 20% bar.
- The change is also not free:
  - The binding chain is the schedule's own output. Exempting it moves it, here to three other
    groups, so a sound implementation needs a monotone fixed point over re-schedules.
  - Every exempted coordinator group is one more concurrent `coordinator.py` PR past a cap that
    exists to bound merge conflicts.
- The same 9.8 h needs no code. When R10-ARBITER-OFF-RESTORE merges (#3404), the orchestrator
  can dispatch R10-ECL110-MQTT-OFF-NEUTRAL over the coordinator cap, `pr_cap.py dispatch-gate
  --over-cap "binding chain: R10-ECL110-MQTT-OFF-NEUTRAL"`.
- The next replan then reads it as started (inherited) and models the earlier closure.
- Whether a binding-chain group earns the section-5 exemption is a dispatch judgement under the
  mandate. It is not this seat's to rule.

What would change it: a binding-chain group held past the coordinator cap at two or more
successive replans, where the summed modelled delay reaches 20% of the remaining horizon.

Binding: 10.3% on programme completion, under the bar. A free operational lever exists.

## P630: the relay's handoff arm runs before its probe and confirm arms

Verdict: ACCEPT, as a carry check on R10-RELAY-ARM-ORDER (#3465). No new group.
- (i) The `topic` single-post form: REJECT.
- (ii) A tracked form for the hold-as-priority-lever: REJECT, as already tracked.

Source: triage queue line 308, 2026-11-11T14:18:51Z, orchestrator s14, RELAY, with the dispatch
seat's additions of 14:13Z.

Coverage:
- R10-RELAY-ARM-ORDER's brief (`s6-batch182.md#P601`, item 1 RELAY-ARMS-FIRST) is this
  proposal.
- #3465's diff from its merge base reorders `pass()` (cloud_relay.sh): `probe_arm; confirm_arm;
  handoff_arm; carry_fold_arm`.
- Its selftest checks "a verdict returned before the pass is POSTED before handoff_arm starts".

The residual #3465 does not cover:
- A verdict that returns while a pass's `handoff_arm` is inside a 30-45 min update_pr still waits
  for the rest of that update.
- The measured hold fits that shape. The last POSTED line in cloud-relay.log is 13:21:59Z
  (#3470), and none follows through 14:18Z.
- The carry asks the reviewer to confirm that the reorder covers verdicts present at pass start.
- The residual is DEFERRED until #3465 merges. What would change it: probe-to-POSTED p90 over
  20 min across 24 h after the merge (P601's figure before it was 51.6 min). That would justify
  running the update detached so the loop keeps probing.

(i) `cloud_relay.sh topic <topic> <pr>`, posting one probe/revt-* verdict without a pass:
- After #3465 every pass posts first, so the hand path only covers the in-update residual above.
- A second posting path is a second place for the posted/confirm bookkeeping
  (`cloud-relayed`, `.confirm-*`) to diverge.
- The cost is more than the residual it would serve.

(ii) The hold as a priority lever is already tracked:
- `cloud_relay.sh` (:6 `held <pr>`; :114-135 the hold and release grammar, and the malformed
  file as OWED, never hold-all).
- `bus.sh` (:470-480, R10-FLY-RELAY-HOLD) reads the same file.
- Using it to skip updates is an operational use of a tracked control, so no new form is owed.
- Note: the hold currently lists 3465, the fix itself. Release 3465 first so its own update is
  not the one held.

Cost/benefit:
- The carry costs one reviewer check on an open S PR.
- The benefit is P601's: a median of 6.8 min and a p90 of 51.6 min of probe-to-POSTED latency
  on every returned verdict.

Binding: covered by #3465. (i) costs more than the residual it serves. (ii) exists.
