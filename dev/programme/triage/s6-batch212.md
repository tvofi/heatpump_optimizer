# Proposal triage, session s14, batch 212

Sources: triage queue lines 323 and 324, two PROPOSAL lines (orchestrator s14,
2026-11-11T18:38:22Z), ruled as P645 and P646, and the record owed from batch 211. Line numbers
are at origin/main c71d3f6e89.

## Record: P643 restated, and the orchestrator's decision on R10-SEAT-IDENTITY-P5

Verdict: REJECT parts (a) and (b); DEFER part (c) (restating s6-batch211.md#P643, whose multi-line Verdict reads as unreadable).

Orchestrator s14 decision (2026-11-11, on batch 211):
- R10-SEAT-IDENTITY-P5's opener seam is NOT started now, despite 49 moved skips on 2026-11-11
  (open-driver.log).
- Reason: it is an instrument group, not critical path, hotfix or outside, and open PRs are far
  over 20. Owner, 2026-11-11: "Until you are below the soft PR cap of 20, only such new groups may
  be started".
- Local workaround in force: a one-shot opener seat, from a fresh branch-backed worktree, opens
  any priority handoff that the standing opener skips `moved` twice.
- Re-raise trigger, to the orchestrator: the same day's moved-skip count passes 80, or a hotfix
  or outside handoff waits over 60 min on a moved skip.

## P645: three acknowledgement surfaces for one held owed line

Verdict: REJECT the tracked candidate (one acks file and one grammar for all three checks); DEFER retiring the session-local owed check until the beat's owed-check reads.

Source: triage queue line 323. The three readers:
- (a) beat_jobs.py owed_check (:318-323) runs owed_unactioned.py with `--acks` set to the
  seat_ledger path the beat config names ($HPO_STATE_DIR/seat-ledger.md).
- (b) the session's s14/beat_extras.sh (:29-32) runs the same owed_unactioned.py, same grammar,
  with `--acks s14/seat-ledger.md` and `--max-board-min 45`.
- (c) s9/sweep-runner/reconcile.py (:72-99) reads reconcile-holds.txt, `<key-prefix>
  <until-ISO|-> <ruling>` lines, for its RECONCILE lines, which no beat row prints.

Instances (2026-11-11, local state only):
- The orchestrator's figure, cited: 9-13 handled lines re-raised on every sweep from 16:53Z to
  17:48Z (55 min), with acks written to a file no check read.
- `git ls-files` at c71d3f6e89: of the three readers only (a) is tracked. (b) and (c) are
  session-local scripts under the state dir, kept by the owner's 2026-11-09 ruling quoted in
  beat_extras.sh's header ("Fix the gaps locally").
- (a) is not the live reader today: digest/jobs/owed-check (written 19:03Z) holds `UNREADABLE:
  the board is <age> old (over 20)`. (b) is: s14/extras/unact.txt reads "154 key(s) on board
  2026-11-11T18:11:44Z; 76 acknowledged, 78 unactioned".

The rule, run per part:
- Measure: the window in which handled lines re-raised, 55 min of the 18.6 h of 2026-11-11 to
  19:35Z (5%). Or the lines themselves, 9-13 of the 154 keys (6-8%). Both are under 20%, on one
  occurrence, and caused by acks written to the wrong file, not by a reader misreading.
- Severity: unset (no roster group owns (b) or (c)), so it is classified here as normal. The cost
  was re-raised OWED lines for 55 min, with no wrong merge, dispatch or product effect.
- Tracked candidate: two of the three readers it would unify are not in the tree. A tracked
  change can only touch (a), which already has the grammar (b) uses. Rejected: no tracked cost
  buys the gain.
- Local, the orchestrator's own tooling and not a triage ACCEPT: (a) and (b) already share one
  grammar, so pointing beat_extras.sh's `--acks` at $HPO_STATE_DIR/seat-ledger.md makes them one
  file for one argument. (c) keeps its own grammar for its own line family; a hold there does not
  need to stand in the ledger.
- Retiring (b) needs (a) to read. Two causes keep it UNREADABLE:
  - the owed line it cannot key, which is already carried as R10-TICK-RESIDUE-P3 carry idx 22
    (not started);
  - the board-age refusal at the default `--max-board-min 20`, where (b) passes 45.

  No carry names the second. Its rate is unmeasured, because the job file keeps only its last
  state. DEFER until that is measured: what share of a day's owed-check passes are UNREADABLE on
  board age. A share over 20% makes it a carry on R10-TICK-RESIDUE-P3 (medium), which owns
  beat_jobs.py and owed_unactioned.py.

Cost: tracked, none. Local, one argument in beat_extras.sh.

Binding: two of the three surfaces are outside the tree. The one-file local remedy is a single
argument, and the measured cost is 5% of one day on one occurrence.

## P646: `train.sh add` with no live train batches every ready pull request

Verdict: ACCEPT, as a carry on R10-TRAIN-RESIDUE-P2: correct train.sh's add text. REJECT the `--only` flag and the pre-start print.

Source: triage queue line 324. When no train is live, `add` starts one through
merge_train.py ready_batch (:3058-3068). That is carry 14 (tvofi 2026-11-01: batch by default),
pinned by the self-test at :5942: every ready verdicted pull request from build_queue joins the
first batch. The behaviour is the owner's ruling. What is false is train.sh's own text:
- the header (:12-14) says `add` "with no train live, starts one over it";
- the --queue refusal (:75) says "the started train's queue is the added entry".

The instrument guide train.sh.md (:28) states it correctly ("over every ready").

Instances ($HOME/.local/state/hpo/merge_train/train.log):
- `grep -oE 'STARTED train.sh pid [0-9]+ over [^;]+; queue add-queue-202611(0[89]|1[01])' | wc -l`
  gives 16 add-started trains from 2026-11-08 to 2026-11-11.
- A 17th, the orchestrator's instance, has no STARTED line. That add's build_queue logged `QUEUE
  #3355` (line 20642), `QUEUE #3431` (20655) and `QUEUE #3442` (20662), and the merge seat TERMed
  it.
- The seat relaunched at 18:36:24Z with the explicit queue (`train.sh: queue=.../Q.json`, then
  `BATCH 20261111-183624 ... queue=7`), so no excluded pull request merged. The delay was about
  4 min.

The rule, run per part:
- Measure: add-started trains that took in a pull request the orchestrator had excluded. That is
  1 of 17 (6%) over 2026-11-08 to 2026-11-11, under 20%. (Today alone it is 1 of 3, too few to
  bear a percentage.)
- Severity: medium, R10-TRAIN-RESIDUE-P2's roster severity (in progress). That group's carries
  already route merge_train.py and train.sh work. A false statement of what a merge command will
  merge, in the file a seat reads before running it, is a defect repair.
- `--only` duplicates `train.sh --queue Q.json` (header :4), the documented exact-queue start
  the seat used at 18:36. A second spelling of the same start is rejected.
- A print of the batch before it starts gives an unattended seat nothing to act on between the
  print and the start. The STARTED line already names the set (`over #...`), and `merge_train.py
  queue` prints the QUEUE/LEFT lines without starting anything. Rejected.

Cost: train.sh header (:12-14) and one die string (:75), about 4 lines. There is no new flag,
file or check, and train.sh has no structure_budgets.json row.

Binding: a 4-line correction of false text in a merge command's header, against a new flag that
duplicates `--queue`.

Bar: severity medium (R10-TRAIN-RESIDUE-P2). Figure: 1 of 17 add-started trains (6%), under 20%.
Basis: severity-exempt defect repair (medium) only. On the 20% bar alone it would be REJECTed. It
is a carry on a group already in progress, so no new group starts.

Destination: append-carry on R10-TRAIN-RESIDUE-P2, with this text:

> TRAIN-ADD-START-TEXT (triage P646). tools/audit/seat/train.sh says `add` with no train live
> "starts one over it" (header :12-14) and that "the started train's queue is the added entry"
> (the --queue refusal, :75). Since carry 14 (tvofi 2026-11-01, merge_train.py ready_batch
> :3058-3068), the started train's first batch is every ready verdicted pull request from
> build_queue. On 2026-11-11 at 18:3xZ an add with no live train queued #3355, #3431 and #3442,
> which had been excluded, and the merge seat TERMed it.
> Repair: both strings say what instruments/train.sh.md :28 already says. With no live train, add
> starts a train whose first batch is the added entry plus every ready verdicted pull request.
> To start over exactly a chosen set, use `train.sh --queue Q.json`. To see the set first, use
> `merge_train.py queue`. Change no behaviour.
> Demonstration: none is owed for comment text. The review checks that the two strings match
> ready_batch's docstring.
