# Proposal triage, session s9, batch 95 (P345, P346)

The rolling batch after batch 94. Batch 94's refs were pushed without a PR and its opener was in
flight, so this ruling did not move that head. Facts were read at origin/main `a7dd7f50d` and at
the round's roster branch, `origin/handoff/audit-r10-roster` (`dc16091d6`).

## P345: K15 (d) reads a budget-raise PR as not reviewable before its approval exists

Verdict: ACCEPT, as one new S fly-in, **R10-FLY-RAISE-REVIEWABLE**. Its brief is the group JSON
the roster op appends. The proposal's first form is taken, an exclusion in the reviewability
reading. Its second form is not: "the gate rolls that one up as approval owed, not red".
- `gate` must stay non-green, because the ruleset's one required check is what holds an
  unapproved raise off `main`.
- It would also put a CI program on the code-owned surface to fix a seat-tool reading.

Source: the orchestrator s9's triage-queue line of 2026-10-31T20:40:47Z (`s7/triage-queue-s7.txt`
line 35).

Instances:
- **The mechanism.** Every raise PR's head enters this state, at origin/main `a7dd7f50d`:
  - In `tools/policy/budget_raise_gate.py`, lines 503-505, `approval` returns False with
    "<owner>'s approval is on <sha>, not this head" whenever the latest decisive review names
    another commit. Lines 490-492 return False with "no decisive review" when no review exists
    yet. Because the approval follows the verdict, a new head always fails this before its
    review.
  - `tools/ci/gate.py` line 76 puts `budget-raise-gate` among the `pr` event's required units, so
    a red there reddens `gate` (`.github/workflows/ci.yml` line 309: `gate` needs `pr-contract`,
    which line 261 orders after `budget-raise-gate`).
    `tools/policy/fixtures/required-contexts.json` `gate_required` lists
    `budget-raise-gate / budget-raise-gate`, and `merge_train.gating_names` (merge_train.py
    lines 386-394) folds that list into the required names.
  - `merge_train.classify` (lines 434-445) reports the red. `orchestrator_tick.one_pr`
    (orchestrator_tick.py lines 876-882) prints "NOT REVIEWABLE ... back to its fixer, never a
    reviewer (K15 (d))".
  - bus.sh dispatch (bus.sh lines 462-473) refuses the reviewer on `merge_train.py classify`
    rc 1. That refusal landed in `9c53c107b` (2026-10-29, `git log -S"is not reviewable: a
    required context" -- tools/audit/seat/bus.sh`). Since then, a raise head whose gate has
    concluded cannot be dispatched a reviewer at all. Only a dispatch that races the run, while
    it is still WAIT (rc 3), gets through.
- **#3045 at `9ef51b8215dd7216950f177386fb2f5a8f010a47`** (`git ls-remote origin
  refs/pull/3045/head`).
  - The seat ledger's line 3171 reads: `OWED-ACK 2026-10-31T20:40:47Z #3045 ttl=3 "NOT REVIEWABLE
    at 9ef51b82" over-fires: the only red is budget-raise-gate (REFUSED: approval on b02ffd170,
    not this head)`. That is three ticks of a false fixer-route flag, acknowledged by hand.
  - Its review went out only because the dispatch had already been made (ledger line 3150:
    three dispatch records at that head).
  - The queue line cites job 124647394312, which printed "REFUSED: tvofi's approval is on
    b02ffd170d50, not this head".
- **#3006 (critical path) at `979797ad`.** Ledger line 3115 records "Earlier reds at 17:01, 18:32,
  18:34 also budget-raise-gate", before the owner's review 5724343039 at 18:40:43Z. That is the
  same pre-approval state on a critical-path PR. Its later red at 18:43Z is a different cause, the
  P336 revocation.
- **Recurrence.** `grep -i budget-raise-gate seat-ledger.md` names 13 PRs (#2711 #2877 #2879 #2881
  #2962 #2989 #2995 #3000 #3003 #3006 #3014 #3045 #3055). Each new head of a raise PR goes through
  the state once per review round.
- **Rule run on each instance:**
  - #3045: red = {gate, budget-raise-gate}, with a raise and an approval on an older head. The
    reading becomes approval owed and the PR is reviewable. Correct: the verdict is what the
    approval waits for.
  - #3006, pre-approval reds: the same shape. Correct.
  - #3006 at 18:43Z, a revoked mandate after an owner review at the head: `raise_hold` returns
    the gate's mandate reason. That is an approval-arm refusal, so the PR reads approval owed.
    Correct as well: a reviewer is not the fault there, and the verdict already existed.
  - Null control, a raise PR with `tests / fast` also red: not reviewable. That is unchanged, and
    correct.

Cost: S.
- `merge_train.py`: about 25 lines for `approval_owed` and the `classify --pr` arm. It reuses
  `Train.raise_hold` (lines 1531-1588), which already reads the gate's own `raises_between` and
  `approval`, so nothing is restated. Add about 30 lines of self-test rows.
- `bus.sh`: about 3 lines (`--pr`, the rc 4 arm) and one self-test row beside the K15 (d) rows at
  lines 1439-1453.
- `orchestrator_tick.py`: about 6 lines in `one_pr` and two fixture rows.
- Two instrument pages, a few lines each.
- API: two reads (reviews and body, through `raise_hold`), only at a raise head whose sole unit
  red is budget-raise-gate. Every other head costs nothing new; the file list is read from git.
- No capped file. `node tools/policy/policy_lint.mjs --budgets` at `a7dd7f50d` has no row for any
  of the five. `tests/structure_budgets.json` measures `custom_components/` only
  (`tests/structure.py` line 12).
- Overlap is by seam:
  - `bus.sh` is in R10-ORCH-REVIEW-PACKET's files (#2870, the packet arm). This group touches
    only the classify case arm.
  - `orchestrator_tick.py` is in R10-FLY-TICK-APPROVAL-OWED's files (#3041, `verdict_levels`).
    This group touches only `one_pr`'s K15 (d) line.
  - The group stays separate from #3041 because its owner seam is the classifier, not the
    level lines. Adding this to an open PR would also grow #3041's review.
- One sonnet fixer and one opus review.

Binding:
- The deadlock is structural. The approval follows the verdict, and the verdict needs a
  dispatch that the pre-approval red refuses. So every budget-raise PR is either routed back to
  a fixer who has nothing to fix, or is reviewed only through a race or a hand override.
- Two instances on 2026-10-31 alone, one of them critical path, against about 60 lines in one
  owner seam with null controls. The benefit clearly outweighs the cost.
- Dispatch ahead of other instrument fly-ins. Until it lands, the orchestrator's hand
  acknowledgement (the OWED-ACK) is the workaround.

## P346: open_pr skips its prepr on a fixer-recorded prepr receipt

Verdict: REJECT, as proposed. The narrowed form, a prepr that holds no heavy slot when its
scope runs nothing, is DEFERRED to R10-PREPR-CAP (`in-progress`, #3051; files `tools/pr/prepr.sh`
and `tests/gate_lock.py`). That group owns the slot. This seat did not measure the 0-script slot
wait across seats; the orchestrator owns routing it as a proposal with that count.

Source: the orchestrator s9's triage-queue line of 2026-10-31T21:10:17Z (`s7/triage-queue-s7.txt`
line 36).

Instances:
- **What the open runs.** `open_pr.sh` merges origin/main into the authored code head before any
  check (`tools/audit/seat/open_pr.sh` lines 103-105). It then pushes through `app_push.sh` with
  `PREPR_SKIP_CLOSURES=1` (line 118), which runs the full `prepr.sh` (`tools/pr/app_push.sh`
  lines 469-475). So the open always gates a merge commit the fixer never ran, never "an unchanged
  head".
- **The skip condition, run on every open in the opener's log today** (`s9/seat-opener/driver4.log`).
  For each, the authored code head C is taken from the START line. The open's main is the second
  parent of the PR head's parent (the open's merge commit). The test is whether any
  `tests/closures.json` closure of a script that C's three-dot diff selects contains a file main
  changed between `merge-base(C, main)` and that main:

  | PR | C | main moved | scripts selected | closures main touched | skip valid |
  |---|---|---|---|---|---|
  | #3050 | `632bd15b9` | 9 merges, 30 files | 27 | 2 | no |
  | #3052 | `fddb9a1bf` | 9 merges, 30 files | 22 | 2 | no |
  | #3055 | `c18116991` | 3 merges, 53 files | 3 | 3 | no |
  | #3056 | `e316cdb95` | 3 merges, 53 files | 1 | 1 | no |
  | #3053 | `5f1c1d80b` | 3 merges, 53 files | 0 | 0 | yes |

  The rule fires on 0 of 4 code opens. The one head it would pass, triage batch 93, selects 0
  scripts, so its gate runs nothing and a skip saves nothing on the gate.
- **What the open-time prepr still catches.** At 18:34Z it refused `r10-fly-mutant-restore`
  (`9a1a9835f`): `CI PREDICT: 1 predicted red(s) on pr-contract / pr-contract against
  c3a47e5656ef`. That is a prediction against the main the open merged, not the main the fixer
  ran on. A receipt keyed to the fixer's base would have skipped it and opened a PR that went red.
- **Where the wall time goes.** `prepr.sh` takes its heavy slot at step 1b (line 3555) for its
  whole life, before step 2 (line 3598) knows the scope. Run here, this batch's own prepr (0
  scripts, one markdown file) sat in `gate_lock.py slot-take` for 25 min 55 s
  (`ps -o etime`, pid 60376) behind heavy runs, and was stopped by this seat to add this ruling.
  Today's opens took from START to RESULT: 31 min (#3050), 24 min (#3052), 22 min (#3053, 0
  scripts), 76 min (#3055) and 77 min (#3056). The 0-script open's 22 min is a slot wait plus the
  cheap steps, not a gate.

Cost (as proposed):
- A receipt format on the `handoff-body/<topic>` transport, written by `body_push.sh`.
- A reader and a closure-intersection test in `open_pr.sh` or `app_push.sh`.
- The self-test rows for both.
- Three seat files, one of them `app_push.sh`, the authoring instrument (decision 0011).
- The receipt is self-reported by the fixer seat, on a ref the fixer writes.

Binding:
- The measured benefit is about zero: the skip is valid on 0 of 4 code opens.
- Where it would fire, the gate it skips costs nothing, and it would skip the cross-main
  prediction that caught a real red at 18:34Z.
- The trade is not even, it is negative, so this is REJECT.
- The cost the proposal names (opens waiting behind slots) is real. The measured lever is that a
  0-script prepr holds a heavy slot it does not need. That is R10-PREPR-CAP's seam (the slot
  lease, #2267), and it needs a count before it can be ACCEPTed: how many preprs select 0
  scripts, and their slot-take waits.
