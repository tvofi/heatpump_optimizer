# Proposal triage, session s14, batch 165 (P579)

This batch rules `s7/triage-queue-s7.txt` line 261. The bar and the denominators are batch 141's.

Sources:
- origin/main `8f97247fc1`. Every `merge_train.py` line number below is at that commit.
- The live train's log, `~/.local/state/hpo/merge_train/train.log`, snapshot of 19710 lines at
  05:30Z (seat copy `s14-8/train-snap.log`). Line numbers below are in that snapshot.
- Two scripts over that log, `s14-8/waits2.py` (output `s14-8/waits2.out`, `s14-8/waits3.out`).
  A wait is a run of `beat: waiting <what> (poll k, t+Ns ...)` lines with the same `<what>` and a
  rising `t+`; its length is the last `t+`. The spool is tracked from the log: an entry joins it
  on `ADDED #n to the live train` or `spooled for the live train's next batch`, and it empties on
  the drain line `ADDED #...: batch k of this train` (`merge_train.py:3857`) or a `BATCH ` line.
  A wait is spool-blocked from the first poll at which the spool is non-empty. Its outcome is read
  from the 11 lines after it: `SKIP #`, `stays skipped` or `past the N s cap` is skip; `merged` is
  merged; anything else is other (55 of 75 "other" are `#n <head> ci red=[]`, a green head that
  goes on to its merge).
- No GitHub API calls.

## P579: TRAIN-REJOIN-WAIT-BLOCKS-SPOOL

Verdict: REJECT both arms (yield the rejoin wait to a non-empty spool; move a WAIT rejoin
candidate into the spool). DEFER a critical-path-only yield, on the terms below.

The instance is not a rejoin wait. PR 3355 is this batch's serial entry (`serial: #3355`, line
19629). It was parked `[MAIN-MOVED]` on a base-branch policy refusal (line 19646), took the
card-5 no-recarry path (line 19648; `merges_as_is`, `merge_train.py:2553`, called from
`recarry`, `:2494`), and now waits in `wait_ci` (`:1905`) at its own head: the gate red there is
read as a deferral while ci.yml run 42961218591 is unfinished (`:1951`), and the heartbeat is
`wait_ci`'s (`:1988`). `Train.rejoin` (`:3709`) prints no `beat:` line at all, and the log has no
`REJOIN #3355` line in this batch. Both arms as asked therefore move 0 of the 1 instance.

Source: queue line 261, 2026-11-11T05:23:40Z, orchestrator s14.

Instances:
- **This instance.** `beat: waiting CI at dee7a1fa`, 24 polls, t+5596 s at the snapshot, cap
  7320 s (`wait_cap_s`, `:3703`). Spool non-empty for the whole wait (`waits2.out`, top row:
  `line 19651 ... t 5596 blk 5596`).
- **The rejoin wait itself, whole log.** 18 `REJOIN #` outcomes: 15 RED, 1 head moved, 2 GREEN
  (359 s and 7229 s after the skip). The rejoin is a minor share of spool blocking.
- **The general mechanism the instance does show: a single-head `CI at` wait in a batch blocks
  the spool.** Whole log (BATCH 20261016-183919 to 20261111-002834-b4, 26 days; 243 waits,
  523,303 wait-s):
  - wait ending in skip: 78 waits, 25 spool-blocked, **47,740 s** blocked, 147,040 PR-s;
  - wait ending in merge: 50 waits, 11 spool-blocked, 23,471 s;
  - other (mostly green, going on to merge): 75 waits, 38 spool-blocked, 64,387 s.
- **Last 7 days** (from `BATCH 20261104`, line 9748; 256,345 wait-s):
  - ending in skip: 53 waits, 13 spool-blocked, **17,228 s** (4.8 h), 36,635 PR-s;
  - ending in merge: 37 waits, 7 spool-blocked, 18,633 s;
  - other: 14 waits, 3 spool-blocked, 2,425 s.
- **Rule applied per instance, as a yield to a non-empty spool on any single-head wait:**
  - skip-ending waits: a pure gain, the whole blocked span: 17,228 / 256,345 = **6.7%** of the
    train's waiting in 7 days; 47,740 / 523,303 = 9.1% over 26 days.
  - merge-ending waits: a reorder, not a gain. The spool batch merges earlier and the waiting
    head merges later; only the overlap of the two CI waits is saved, at most the blocked span
    (18,633 s), and every yield moves main under the waiting head, which owes a re-grade
    (`:2634` path) and on a strict ruleset a recarry.
  - Upper bound with every blocked second counted as saved: (17,228 + 18,633 + 2,425) /
    256,345 = 14.9%.
- **Null control.** A spool-blocked count needs a spool: the same script reports 147 of 243
  waits with an empty spool for their whole span (0 s blocked), so the measure does not count
  every wait as blocked.

Cost:
- A yield in `merge_train.py` (9,430 lines, the train's hot file, owned by R10-TRAIN-RESIDUE,
  part 2 open and unstarted): a spool check inside `wait_ci`'s serial callers after one poll, a
  Stop that re-spools the waiting entry at its head and verdict, the drain, and a re-grade of
  the yielded head on the moved main. About 40 production lines plus self-test arms for yield,
  no-yield on an empty spool, and the re-spooled entry's re-grade: about 80 lines in all, and at least
  one review round on the train's hot file.
- `merge_train.py` has no row in `tests/structure_budgets.json` at `8f97247fc1`; no capped file.

Binding:
- **Both arms as asked: REJECT.** They act on `Train.rejoin`, and the instance is a `wait_ci`
  in the serial path. Applied to this instance they move nothing.
- **The general yield (any single-head wait, non-empty spool): REJECT.** It is new machinery on
  an instrument, so it must clear 20% (`proposal-triage.md`, Machinery). The measured pure gain
  is 6.7% of the train's waiting over 7 days (9.1% over 26), and even counting every blocked
  second, merges included, it is 14.9%. The binding cost is a re-grade-on-moved-main branch in
  the train's hot file for a gain under the bar.
- **A critical-path-only yield: DEFER.** The instance's real cost is that main's red repair,
  PR 3419, queues behind the wait. That is one critical-path instance in the log. It changes on
  a second instance in which a critical-path PR sits in the spool for more than 30 minutes behind
  a single-head wait; the owning group would be R10-TRAIN-RESIDUE part 2.
- **Owed to the orchestrator, not a build:** this instance's wait ends by cap no later than
  t+7320 s, about 06:00Z, or earlier when run 42961218591 concludes. A critical-path merge that
  cannot wait for that is the orchestrator's operational call, through the merge seat (the live
  train is pid 90895; a stopped train leaves the spool to start a train of its own, `:3838-3842`), under the never-slip ruling for the
  critical path.
