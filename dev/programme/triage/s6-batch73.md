# Proposal triage, session s8, batch 73 (P307)

The rolling batch (V182) after batch 72 (#2993, merged). Facts were read at origin/main
`cf4f6b7a6`, in the live merge-train log (the orchestrator's `merge_train/train.log`, 3732 lines,
2026-10-16 to 2026-10-30), and in the orchestrator's regain-24h evidence (`s8/regain24/`).

## P307: run the record beat outside the train's critical section (lever L7)

Verdict: DEFER. The benefit is not measured, and the stated mechanism is not reproduced. The
filing's figure, "the record beat held the train 7.06 h on 30 SHAs", has no command behind it in
the evidence it cites. The train log shows the hold running the other way: the train holds the
record beat. The in-train record merges it does show cost no code merge a CI cycle that its own
base move would not already have cost. The host if the answer changes:
**R10-TRAIN-OVERLAP-GRADE**, which owns the in-train record ordering (P289, `s6-batch61.md`, the
critical-path jump over the record sweep). Not R10-FLY-TRAIN-DEFAULTS, whose surface is the train's
defaults, not `sweep_bots` ordering.

Source: the orchestrator s8's message of 2026-10-30, lever L7 of its regain-24h investigation
(card L7, "Cut the post-approval train and CI wait": "the record beat held the train 7.06 h on 30
SHAs ... run the record beat off the train's critical section"). The owner approved the mandate
levers on 2026-10-30 (#201 comment 6527969942); that approves pursuing the lever, not this
ruling's cost test.

Instances, and what each shows:
- **The 7.06 h figure is not in the cited evidence.** The cited files are `phases.txt` and
  `durs.txt`. `phases.txt` gives "last merge verdict->merged (train/CI): median 1.78 mean 2.25 sum
  144.2 p90 3.81" over 64 PRs. `durs.txt` gives per-PR first-commit-to-merge. Neither holds a
  record-hold duration, a hold count or a list of 30 SHAs. `grep -rn '7\.06\|held'` over the
  evidence scripts finds nothing.
- **The hold ref holds the record beat, not the train.**
  - `merge_train.py`'s `hold_refresh` (line 2125 at main) publishes `refs/heads/train-hold` "before
    anything merges", and logs `TRAIN HOLD ... the record beat waits` (line 2169).
  - Its docstring (lines 101-105) gives the reason: nightly.yml's record beat would otherwise
    auto-merge record PRs and move main mid-train.
  - In the train log, `TRAIN HOLD refs` appears 601 times and `TRAIN HOLD released` 62 times,
    over 110 `BATCH` lines. That is the train refreshing its hold on the record beat, not waiting
    on it.
- **The record PR merges at the batch start, not inside a recarry.**
  - `--bot-prs` (`sweep_bots`, lines 1229-1271) merges the open record PR before the batch reads
    its base. A pending one is logged and skipped: "a pending check ... never stops the train".
  - Train log: 8 `BOT #N MERGED` lines, each followed directly by the batch's `OVERLAP` base read.
    There are 15 `BOT #N pending` skips, 0 "record PR #N merged under the batch" (the P191
    mid-batch path) and 0 "critical path: the record sweep waits".
  - So a record merge moves the base the batch is about to read. An entry whose head lacks that
    main recarries once, as it would for any earlier main move.
- **What the 2.25 h mean does show.** The time from the last merge verdict to merged is 2.25 h
  mean against the card's ~55 min CI leg. That gap has candidate causes this evidence does not
  split: the hourly pitch, batch formation, `--overlap` base waits, recarries on code-only main
  moves, and approvals. L7's other two actions (pull FLY-CANCEL-SWEEP and FLY-TRAIN-DEFAULTS
  forward) are queue order. They are the orchestrator's to take and need no ruling.

Cost, if built as filed:
- Moving `sweep_bots` out of the batch start means record PRs merge between batches or after the
  train. That puts back the mid-train main move `hold_refresh` exists to stop (#2291, #2295,
  #2299, issue #2302), unless the record-hold rules are rewritten too.
- It is an S-to-M change in `merge_train.py` (6703 lines at main, a hot file), under a host that
  already holds 20 carries. Its stage was flipped and repaired six times since 2026-10-28
  (P305, `s6-batch71.md`). That is the three-round risk the filing names.

Binding: an unmeasured benefit against a change that touches the guard written for a recorded
incident class, in a hot file, on a host already at three-round risk. That is DEFER under the
contract, never ACCEPT.

What would change the answer: one per-SHA attribution with its command. It should show a code
head whose merge waited on the record beat, by a record PR merging ahead of it, or by a `BOT`
pending that the train waited on. Give the wait for each SHA from a timestamped source (the
train's per-batch log time, or the `train-hold` commit dates the hold encodes), and their sum.
Then it goes to R10-TRAIN-OVERLAP-GRADE as a carry beside P289. The control the filing asks to
name is `merge_train.py`'s own hold self-test (`hold_idx`, line 4393; the `TRAIN HOLD released`
assertion, line 4414). It must still pass: the record beat must not merge a record PR while a
batch's base is read.
