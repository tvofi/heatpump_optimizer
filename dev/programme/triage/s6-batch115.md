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

## P374: a verdict ref takes a second commit with the same tree, and the pull request deadlocks

Verdict: ACCEPT, as a defect in an instrument: option (a), narrowed to `append_commit` in
`tools/audit/seat/bus.sh`. Option (b) is refused. The carry, b115-P374, goes to
R10-FLY-RAISE-REVIEWABLE, whose files already hold `bus.sh` and `merge_train.py` and whose next
step is a fixer.

Source: the orchestrator s10's message of 2026-11-02, about 13:50Z, after a hand fix (seat
ledger, 13:49:10Z `DEADLOCK-BY-HAND #3173`).

Instances:
- **#3173** (`fix/r10-agreement-bootstrap-p1`, R10-AGREEMENT-BOOTSTRAP p1). Read from
  `git cat-file -p` on each commit:
  - `verdict/3173` got `f9aafd42` at 14:44:06+01, confirmed from `review/3173` at `2eab795f`.
  - It then got `dba76851` at 14:44:12+01, parented on `f9aafd42` and confirmed from
    `review/3173` at `e6899918`.
  - Both have tree `50c657668ec5`. The messages differ only in that `bus-confirmed` line and a
    `bus-model: opus` line, so the two are not byte-identical.
- **The double writer is the reviewer's push, not the relay.** `git log origin/review/3173`:
  - `2eab795f` at 14:43:56+01, on `6bc25136`;
  - `e6899918` at 14:44:03+01, on `2eab795f`, with an empty diff and the same message.
  - `push-verdict` therefore ran twice on one verdict, and each review head was confirmed once.
- **Why the second confirm passed its replay guard.** The guard in `confirm()` (`bus.sh` lines
  567-571 at origin/main `3905069f3`) reads `posted-signed` before it pushes. The second confirm
  started before the first had posted, passed, and appended `dba76851`. Only then did
  `post_verdict` (lines 353-355) refuse it as a replay. That left the posted commit one behind
  the tip.
- **Why the train refused.** `merge_train.py` line 2472 refuses when "the newest posted verdict
  (comment ...) is not verdict/<n>'s tip". That is a deliberate guard, pinned by its self-test
  arm "a newest posted verdict that is not the bus tip waits (#18: confirmed, not posted)"
  (line 4773).
- **One instance** in the seat ledger. The defect has the same shape as P368: a verified
  deadlock in an instrument, worked around by hand.

Rule run on the instance:
- With the carry's rule, the reviewer's second `push-verdict` reads `review/3173`'s tip
  `2eab795f`. Its tree equals the tree being pushed, so it pushes nothing. `e6899918` never
  exists and there is no second confirm.
- If two confirms still race, the second reads `verdict/3173`'s tip `f9aafd42`, whose tree is
  the same, and appends nothing. The posted commit stays the tip, which is the state the hand fix
  restored.

Cost:
- One guard in one shell function, `append_commit`, which both `push-verdict` and `confirm`
  call: about 6 lines.
- Three self-test arms in `bus.sh`'s existing self-test and one mutant in
  `dev/audit/harnesses/r10_seat_selftests_mutants.py`.
- An S group that already holds `bus.sh`, so no new group and no new file.
- Option (b) would loosen `merge_train.py`'s verdict-identity check, a merge gate, for every pull
  request in order to cover a state that (a) stops from being written. That is the binding
  cost of refusing (b).
- No capped file is touched by this ruling.

Binding:
- **Why ACCEPT.** A verified defect in an instrument, not a proposal. It deadlocks any pull
  request whose reviewer re-runs `push-verdict`, production pull requests included.
- **The tree is the right key.** `post_verdict` already treats "<pr> <tree>" as what was signed,
  and "each round's nonce makes its tree distinct" (lines 346-351). A same-tree append can only
  repeat a verdict, never carry a new one.
- **Delivery.** The carry lands when this batch is on main. If R10-FLY-RAISE-REVIEWABLE's fixer
  is dispatched before then, the orchestrator hands the fixer this entry directly.

## P375: RED-UNOWNED reads a fired seat as no seat, missing payload-named fires and handoff-wip

Verdict: ACCEPT, narrowed to propagating the finding into the brief that builds the tracked
level: carry b115-P375 on R10-TICK-PR-BUCKETS. That group's carry 6 specifies RED-UNOWNED as
"no seat dispatched" and leaves the meaning of "dispatched" open. No new group and no new check.
The session-local stand-in is the orchestrator's own script and outside the roster.

Source: the orchestrator s10's message of 2026-11-02, about 16:30Z, a slip from that day's
sweeps.

Instances:
- **#3085, four lines from 15:37Z to 16:09Z** (orchestrator's report).
  - The dispatch seat's `ledger-standin.txt` line 212 reads
    `2026-11-02T15:03:29Z FIRED payload-fix-3085-r5.json`.
  - The stand-in `blind_spots.py` (sweep runner, line 61) calls
    `fired_after(["#3085 ", "#3085)", topic], now - 3 h)`. Line 212 names neither `#3085` nor
    `r10-closeout-cleanup`, only the payload file, so the fire is invisible.
  - Earlier FIRED lines for #3085 (ledger-standin lines 94, 112 and 147) wrote `#3085 r<k>`; the
    line format changed and the predicate did not.
  - The script never reads `handoff-wip/<topic>`, which moved at 15:08Z (orchestrator's report).
- **#3174, the same class, by hand.** Seat ledger at 16:16:43Z: "ordered #3174 retake on
  BLOCKED-SILENT without checking handoff-wip (moved 16:13Z); dispatch caught it".
- **The tracked form is not built yet.**
  - On roster `2c50a2cfc`, R10-TICK-PR-BUCKETS is at stage `not-started` with 7 carries.
  - Carry 6 asks for "three tick levels with these predicates", each with a null control and a
    planted positive.
  - `blind_spots.py`'s docstring names it as that carry's stand-in.

Rule run on the instances:
- With the carry's definition, line 212 is a fire for #3085, because it names a payload file for
  pull request 3085. So is `handoff-wip/r10-closeout-cleanup` moving at 15:08Z. RED-UNOWNED
  prints nothing for #3085 until 18:03Z.
- #3174's handoff-wip motion at 16:13Z likewise holds it.

Cost:
- Carry text only. It fixes the meaning of one word in a predicate the group already owes:
  about 5 lines in the level it writes, and one planted arm.
- Without it, the tracked level copies the stand-in's blind spot. It would fire on every pull
  request whose fix is in progress, and a false RED-UNOWNED invites a duplicate fixer, which is
  how #3174's retake was ordered.
- No capped file is touched by this ruling.

Binding:
- **Why ACCEPT.** A finding that changes how a later stage must work goes into that stage's own
  brief before it is built (`finding-propagation.md`). This is not a proposal for new
  machinery, so the LOG class does not apply.
- **What stays with the orchestrator.** The two-line patch to its own stand-in: add payload-file
  keys to `fired_after`, and treat a handoff-wip move in the window as a fire.

## P376: seat-no-return fires for a dispatch that returned on a split-part topic

Verdict: DEFER (LOG, by the owner's 2026-11-01 ~19:50Z rule), with the class sent to a root-cause
seat. On its own, the false line costs one OWED-ACK, or deleting the dispatch ref, which is the
level's documented disposal. It holds no merge. What changes the answer is the root-cause
seat's countermeasure for split-part topics, below, which may route this site with the others.

Source: the orchestrator s10's message of 2026-11-02, about 16:30Z.

Instances:
- **r10-agreement-bootstrap.** `git log -1 --format=%cI` on each ref:
  - `dispatch/fixer-r10-agreement-bootstrap` (`b3f577cb`) is at 08:08:44Z.
  - The exact-topic return refs all predate it: `handoff/` and `handoff-wip/` at 05:41Z,
    `handoff-body/` at 06:37Z, `fix/r10-agreement-bootstrap` at 07:14Z.
  - The seat returned on the split-part topic: `handoff/r10-agreement-bootstrap-p1` at 11:36Z
    and `handoff-body/r10-agreement-bootstrap-p1` at 12:34Z. #3173 then merged.
  - The orchestrator acknowledged it in the seat ledger at 16:26:08Z (OWED-ACK, "false
    positive").
- **The mechanism is the topic name, not the session.** `noreturn_arm` in
  `tools/audit/seat/cloud_relay.sh` (lines 595-626 at origin/main `ea59e9a09`) asks only for
  `handoff/`, `handoff-wip/`, `handoff-body/<topic>`, `fix/<topic>-pr` and `fix/<topic>` with
  the dispatch's exact topic. A return on `<topic>-p<N>` is never asked for.
  - The report's reading, "keys on the session ending", does not match the code. The predicate
    reads no session state: the dispatch tip's age and those five refs are its only inputs.
- **The same blindness, elsewhere.**
  - The opener: P363 (`s6-batch106.md`) and P370 (`s6-batch112.md`), with 4 part topics missed
    by 03:24Z.
  - The stand-in `blind_spots.py` line 46, whose candidates strip only `-pr` and `-2`, not
    `-p<N>`.
  - That makes three instruments with one cause: each keys on an exact topic, and none knows a
    topic's part family.

Cost:
- A fix inside `noreturn_arm` alone means another per-instrument rule. It needs about 10 lines
  and a self-test arm in `cloud_relay.sh`, which is hot in round 10, to suppress one false
  OWED line per split.
- The class already has a third site, so per-site fixes keep re-paying the same cost.
- No capped file is touched by this ruling.

Binding:
- **Why LOG.** The friction holds no pull request that touches `custom_components/`, and no
  measured gain is offered.
- **The class is the root-cause seat's.** At the third instrument, a recurring defect is owed a
  root-cause seat (`CLAUDE.md`, "A recurring error is not a third issue";
  `dev/governance/roles/root-cause.md`), not a third per-site carry. Dispatching it is the
  orchestrator's call. Its countermeasure decides whether one topic-family reader replaces the
  per-site rules, including R10-OPENER-REUSE carry 10.

## P377: one topic grammar for the split-part class (the root-cause seat's barrier)

Verdict: ACCEPT, as a root-cause countermeasure. It keeps that route and is not ruled as a
proposal under the LOG class. The carry, b115-P377, goes to R10-TICK-PR-BUCKETS, with
R10-OPENER-REUSE as the fallback. A set-files op adds the consumers it edits to the group's
files. The root-cause document rides in this batch as `s6-batch115-rca-topic-family.md`, so
that the fixer, which cannot read the host, lands it from the tree.

Source:
- The orchestrator s10's message of 2026-11-02, about 16:55Z. It relayed the root-cause seat's
  verdict "build" for the class P376 sent to it.
- The document is `s6-batch115-rca-topic-family.md` in this directory: the seat's text with its
  host paths scrubbed (`ref_privacy.py scrub`: 0 of 2 files would change).

Instances, checked against origin/main `ea59e9a09`:
- **The class's three instances.** The opener (P363 and P370), `noreturn_arm` (P376), and the
  stand-in `blind_spots.py`.
  - The document re-attributes the stand-in's measured misses to P375's class.
  - It keeps the stand-in as a site of this class, with no measured miss.
- **Its six-site table checks out.**
  - `open_driver.py` line 88 is `def resolve(topic, groups, body_head, titles)`.
  - `roster_sync.py` line 259 is `def matches(roster, prs)`.
  - `cloud_relay.sh` lines 533 and 540 strip `fix/` and `-pr` with sed and awk.
  - `noreturn_arm` is lines 595-626.
- **The recording targets exist.** `dev/audit/config/bugclasses.json` is a dict of 53 classes,
  whose entries carry an `rca` key. `tools/audit/fold_ledger.py` is the checker that reads it.
- **Its measured cost.** 6 false or missed lines, 46 min of measured holds, and one duplicate
  opus seat avoided by a hand check. Splitting is a standing move: 13 of 235 dispatched topics
  split in 3 days.

Cost:
- The document's figure for the standing cost is about 0.5 s per 120 s relay pass. Only an aged
  dispatch whose exact refs did not move pays one extra `ls-remote`.
- New code: one new module in `tools/audit/seat`. Two consumers move their existing rules into
  it unchanged, and two call sites change.
- Tests: three rows, two null controls and two mutants.
- Hot files: `cloud_relay.sh` is hot in round 10, and it enters R10-TICK-PR-BUCKETS's files.
  That widens an M group that is `not-started`. It does not widen a group in flight.
- No capped file is touched by this ruling.

Binding:
- **Why ACCEPT.** The class has three instances, so it owes a barrier (`defect-root-cause.md`).
  The cost test, roughly 0.5 s a pass against 16 min times 0.3 a day plus a duplicate-seat risk,
  picks a shared reader over a fourth per-site rule.
- **Why this group.** R10-TICK-PR-BUCKETS would otherwise build a seventh site: its carry 6, and
  b115-P375's definition of "a seat is on it", which reads handoff-wip by family.
- **The fallback.** If the orchestrator routes the carry to R10-OPENER-REUSE, the same text
  applies, and the set-files op names that group instead.
