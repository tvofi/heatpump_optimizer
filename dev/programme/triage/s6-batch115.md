# Proposal triage, session s10, batch 115 (P373)

The rolling batch after batch 114. Facts were read at origin/main `3905069f3`, at the round's
roster branch `origin/handoff/audit-r10-roster` (`f6df1ab5d`), from the GitHub Actions runs list
for the repository, and in the session's seat ledger.

## P373: rolling record and roster branches, one pull request each per stamp window

Verdict: DEFER (LOG, by the owner's 2026-11-01 ~19:50Z rule). No carry and no group. Parts (1)
and (3) are LOG. Part (2) describes a lane that already works this way. Part (4) is refused on
its cost. The measured saving is reached with no instrument change, by applying the record
batching size the owner already set. The answer changes on a measured CI-time saving above 10%
that only the rolling design reaches, with its baseline and a null control.

Source: the orchestrator s10's message of 2026-11-02, about 12:15Z, filed at the owner's
request. It proposes:
- (1) one rolling record pull request per stamp window, appended by the triage seat through
  `update_pr`, reviewed as a delta;
- (2) the same for roster landings;
- (3) closing the window at stamp planning;
- (4) folding the 8 open record pull requests into the first rolling branch.

Instances:
- **The 8 open record pull requests.** From `gh pr view <n> --json headRefName,files`:
  - #3154, #3157, #3158, #3159, #3161, #3171 and #3172 are triage batches 108 to 114.
  - **Each carries exactly one ruling**: one `s6-batch<N>.md` file and its own delivery row.
  - #3091 is `fix/r10-record-s9-owed`. It changes a carry file, two delivery rows and
    `tests/closures.json`.
  - None of the 8 touches `custom_components/`.
- **The CI share, measured.** The source is `gh api repos/tvofi/heatpump_optimizer/actions/runs`
  for runs created since 2026-11-01T10:00Z. That is 1000 runs, the API's cap, which reach back
  to 2026-11-01T17:17:41Z, a window of about 19 hours.
  - Each run's wall time is `updated_at` less `run_started_at`, and it includes queueing.
  - Branches `fix/triage-s9-batch*`: 80 runs, 559 run-minutes. That is **7.6%** of all run
    time and 12.6% of non-main run time.
  - Branches `fix/r10-record*` and `record/*`: 25 runs, 185 run-minutes, **2.5%** of all run
    time.
  - Fix branches: 306 runs, 3572 run-minutes, 48.8%.
  - Main: 580 runs, 2890 run-minutes, 39.5%.
  - The triage runs are 24 `CI code`, 24 `CI edit`, 24 Dependabot auto-merge and 8 `CI review`,
    over 7 pull requests: about 11 runs and 80 run-minutes per one-ruling pull request.
- **The roster lane already rolls.** Roster landings do not open pull requests:
  - `roster_drain.py` pushes each op to `handoff/audit-r10-roster`, which is 1055 commits ahead
    of origin/main (`git rev-list --count`).
  - The roster reaches main in bulk landings. The last is `75278a0e0` "Land the round-10 roster
    on main".
  - `gh pr list --head handoff/audit-r10-roster` lists only #2277, #2343, #2348 and #2352, all
    from 2026-10-15 to 10-17.
- **The batching size is already set and this seat has not applied it.** The owner's direction of
  2026-10-25 is that triage, roster and record pull requests carry 8 to 10 entries. A
  critical-path-unblocking entry may open early. Batches 108 to 114 were one ruling each. That
  is this seat's slip, not a gap in the instruments.
- **Stamp merges are not serial.** Record pull requests merge only in a stamp's batch, and
  batch-by-default trains (`merge_train.py` queue) merge a stamp's record pull requests on one
  proof. The "8 serial merges" in the proposal is therefore one batch, not eight CI cycles.

Cost:
- Parts (1) to (3) change four instruments:
  - the triage seat's push path, from a new handoff to `update_pr` on a standing branch;
  - the opener's topic-to-PR mapping, which must not open an appended topic;
  - `review_carry`'s fresh-review scope, which must cover a delta;
  - the merge train's stamp queue.
- Each change brings its own self-test arms, mutants and review rounds. The opener and
  review_carry are both hot in round 10 (R10-OPENER-REUSE, R10-ORCH-REVIEW-PACKET).
- A rolling pull request still runs full CI on every `update_pr`. The per-ruling CI cost of an
  append is therefore one run-set, the same as a batch pull request, unless an append skips CI,
  which the proposal does not claim.
- Part (4) costs 8 closures and 8 pointer comments, plus one new pull request with its own full
  CI. It saves no CI already spent, and no stamp merge, because those already go on one batch.
- No capped file is touched by this ruling.

Binding:
- **Why LOG.** The friction does not hold a pull request that touches `custom_components/`.
- **The exemption is not met.**
  - The whole triage lane is 7.6% of CI run time, and triage plus record is 10.1%, both measured
    with queue time included.
  - That is the ceiling of any saving, and neither design reaches it: a rolling branch keeps one
    CI run-set per append.
  - No measured figure above 10% with a baseline and a null control was given, so the proposal is
    ruled under the LOG class, not on its merits.
- **The same saving at no build cost.** From batch 115 on, this seat applies the owner's 8-to-10
  size. It holds rulings in one batch and pushes the batch when it holds 8 rulings, when the
  orchestrator plans a stamp, or early for a ruling whose carry unblocks a critical-path merge.
  - Waiting costs nothing for a DEFER or a REJECT.
  - An ACCEPT carry is held until its ruling is on main, and record pull requests merge only at a
    stamp, so the carry lands no later.
  - At about 11 runs and 80 run-minutes per pull request, one pull request per 8 rulings in
    place of 8 saves about 7 x 80 = 560 run-minutes per 8 rulings. That equals the lane's whole
    measured window, which held 7 rulings.
- **Part (2) needs nothing built.** The roster branch already rolls.
- **Part (4) is refused on its binding cost.** One more full CI run and 8 closures buy no saving,
  because the 8 open pull requests have already run their CI and merge on one stamp batch.
