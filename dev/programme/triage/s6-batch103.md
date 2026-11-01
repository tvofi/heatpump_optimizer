# Proposal triage, session s10, batch 103 (P360)

The rolling batch after batch 102. Facts were read at origin/main `d052f80f7`, on pull requests
#3055, #3065 and #3090, in the live merge train's state directory (train pid 58734) and in the
session's seat ledger.

## P360: the hot-file rule reads the train state the cloud cannot see

Verdict: REJECT as proposed. Neither change (a train-written boarded ref, or a warning when the
train state is absent) would have saved the measured instance, because that refusal was correct.
The residual case, a cloud handoff refused over a pull request that is boarded, is DEFERRED to
R10-DISPATCH-AT-HANDOFF.

Source: the orchestrator s10's queue line of 2026-11-01T16:53:15Z, from #3055's round-3 body-only
cloud fixer (cse_0189ZDZ9RYB7oU3V2T2incu4). Its `body_push.sh` refused `hot-file: #3065 holds an
unboarded merge verdict and shares tools/audit/seat/cloud_relay.sh`, and the body was lost with the
container.

Instances:
- **The rule.** `hot_file_refusals` (`tools/audit/seat/review_packet.py` line 188) refuses when an
  open pull request shares a `HOT_FILES` path with the diff, holds a merge verdict at its own head,
  and is not in `train_boarded()` (line 574). `train_boarded()` is the train's spool plus
  `queue.pending.json`, read from `HPO_BUS_TRAIN_STATE`. With that variable unset it returns the
  empty set, and `render` already prints the advisory `hot-file: HPO_BUS_TRAIN_STATE is unset, so
  every merge verdict reads unboarded` (line 521).
- **The shared file is real.** The three-dot diff of #3065 at `1ac45d875` touches
  `tools/audit/seat/cloud_relay.sh` and `dev/audit/harnesses/r10_seat_selftests_mutants.py`. That
  of #3055 at `757c71eb9` touches `tools/audit/seat/cloud_relay.sh` and
  `tools/audit/seat/pr_args.sh`. All three are `HOT_FILES` paths.
- **#3065 was not boarded.** The proposal says #3065 "was in train 58734's queue". The train's own
  record says otherwise:
  - its `train.log` line 7507 reads `PARK #3065 policy: policy paths changed
    (dev/governance/roles/standing-dispatch.md): no decisive review by tvofi`, at batch 2's start;
  - lines 7538-7539 read `ALREADY #3065: skipped by this train at this same verdict 1ac45d875522`;
  - its `skipped.json` holds #3065 at verdict `1ac45d875522`, phase `pre-flight`;
  - its `queue.pending.json` reads `[3054, 3066]`, and its spool `queue-add.jsonl` ends with
    #3049, #3073, #3077 and #3084;
  - the seat ledger's orchestrator line of 2026-11-01T16:56:51Z says the same: "#3051/#3065 were
    PARKED at b2 start ... not in 58734".
- **So the local read refuses too.** `train_boarded()` run locally with `HPO_BUS_TRAIN_STATE` set
  to that state directory (2026-11-01T16:59Z) returns `[3049, 3054, 3066, 3073, 3077, 3084]`,
  which has no 3065. With the variable unset it returns `[]`. The local refusal names the same pull request and
  the same file as the cloud's did. The cloud's blindness did not cause this instance.
- **The second pull request cited.** #3090 at `3e6bf4230` shares
  `dev/audit/harnesses/r10_seat_selftests_mutants.py` with #3065. The same ledger line records
  "#3090 reviewer stays held on #3065 merging". That is the rule's intended sequencing, not a
  false refusal.
- **Boarded instances measured: 0.** No measured cloud handoff has been refused over a pull
  request that `train_boarded()` would have returned.

Cost:
- **(b), a warning when the state is absent.** About 5 lines in `handoff`, plus a self-test arm and
  its null. `review_packet.py` is not under any `tests/*_budgets.json` key
  (`grep -n review_packet tests/*_budgets.json` prints nothing).
  - It saves nothing on this instance. The body would have pushed, and the next local dispatch's
    `render` would have refused the same #3065, so #3055 still waits on #3065 merging.
  - It also weakens the P256 handoff gate in every seat that runs without the variable. That
    includes local seats: s9's record-pending line shows a local #3055 `body_push` refused, and
    re-run "with HPO_BUS_TRAIN_STATE=...".
- **(a), a train-written boarded ref.** A new ref writer in the merge train, one push per board and
  unboard, and a new reader. That is a standing GitHub write per train event and new maintenance
  surface, to fix a false refusal with no measured instance.

Binding:
- **Why REJECT.** The one measured instance is a correct refusal. #3065 held an unboarded merge
  verdict at its head, parked on policy approval, and shared a hot file. Each change has a real
  cost, and neither would have recovered the 5617 s of fixer time this instance lost.
- **The loss had another cause.** The body was lost because a cloud body-only fixer was fired while
  its hot-file peer was parked and unboarded, and the container kept nothing it could not push.
  That is a dispatch-sequencing fact, already in the orchestrator's hands: the event-gated re-fire
  when #3065 merges, which the ledger line of 16:53:15Z records.
- **The DEFER.** One instance would change the answer: a cloud handoff refused by `hot-file` over a
  pull request that `train_boarded()` returned at that time, run locally with the variable set.
  R10-DISPATCH-AT-HANDOFF owns the item. It is the not-started group that lists
  `tools/audit/seat/review_packet.py` in its `files`. R10-ORCH-REVIEW-PACKET is not chosen: it has
  a packet in flight, and a carry would refuse that packet.

No roster op: a REJECT and a DEFER route nothing.
