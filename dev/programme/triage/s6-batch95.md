# Proposal triage, session s9, batch 95 (P345-P348)

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

Verdict: OWNER-ORDERED (not ruled). The owner ordered this directly (tvofi, 2026-10-31: "I want
that implemented, both persistently as well as you applying it locally immediately"). The
orchestrator withdrew the queue line before this seat's ruling, and the group is
R10-FLY-OPEN-PREPR-REUSE. `proposal-triage.md` gates proposals, and an owner order is not one, so
this entry records no verdict. An earlier draft of it read REJECT; that verdict does not stand.

What stays here is the evidence. The orchestrator carries it to the group's fixer as constraints:
- On every code open today, main moved under a selected closure (4 of 4, table below), so a skip
  keyed to "main did not move under the closure" runs prepr anyway on that shape.
- The open-time prepr's cross-main prediction caught a real red at 18:34Z. A skip must not
  drop that prediction against the merged main.

The slot half is owner-ordered too (tvofi, 2026-10-31, "do all of them"): a prepr takes its
heavy slot at step 1b, before step 2 knows the scope. The orchestrator routes it as an
owner-ordered carry on R10-PREPR-CAP (`in-progress`, #3051), held until #3051's verdict. It is not
a ruling here, and the evidence it cites is the "slot" item below.

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
- **Where the wall time goes (the slot evidence).**
  - **The mechanism** (at `a7dd7f50d`): `prepr.sh` takes its heavy slot at step 1b (line 3555) for
    its whole life, before step 2 (line 3598) prints the scope. Its self-test pins that order:
    line 3268 requires `slot-take` before `step "policy_lint"`. Whether each heavy step runs is a
    diff predicate the step already prints as a `skip` line (self-test, mutants, closures,
    no-copies, brief_lint, wave-script).
  - **The count:**
    - Source: every `*prepr*.log` under the session directory modified within 3 days (43 files).
      35 of them hold a `heavy slot  taken slot=<n> ... expires_at=<t>` line and ran to a `PRE-PR:`
      or `REFUSE` line.
    - The take time is `expires_at` less `gate_lock.LEASE_SECONDS` (1800, `tests/gate_lock.py`
      line 78).
    - 29 runs are light: none of the six heavy steps printed `ok`. Their in-slot time had a
      median of 0.9 min (max 3.8).
    - The 6 heavy runs had a median of 15.2 min in the slot (max 74.0).
    - The light runs' waits, from the 8 logs whose start the daemonize header records: 39.1,
      20.9, 15.3, 12.5, 10.2, 9.9, 4.1 and 0.1 min (median 11.4).
    - The 21 hand-started light logs give no reliable start, because a file's birth time is not
      the run's start, and are left out.
    - This batch's own light prepr was stopped at 25 min 55 s in `slot-take` (`ps -o etime`, pid
      60376).
  - So a light run queues a median 11 min for a slot it uses for about 1 min, and a light open
    holds an opener slot meanwhile.
  - Today's opens, START to RESULT: 31 min (#3050), 24 min (#3052), 22 min (#3053, 0 scripts),
    76 min (#3055) and 77 min (#3056).
  - The sample is mostly the triage seats' logs. Fixer preprs do not log under that name, so heavy
    runs are under-sampled.

The evidence's limits: the open table is one day's opens (five) from one opener log.

## P347: prepr step 3h runs only when the diff touches prepr.sh or its self-test inputs

Verdict: REJECT, as redundant. The proposed rule is the rule step 3h already runs, and at the open
it already ignores main's merge.

Source: the orchestrator s9's triage-queue line of 2026-10-31T21:33:05Z (`s7/triage-queue-s7.txt`
line 38). Its figures (3h at 23-74 min on 3 opens, slot waits up to 64 min) come from the R10-FLY-
OPEN-PREPR-REUSE seat's `measure.out`. That group was dropped at 21:33Z on the owner's ruling
(roster queue line 900).

Instances:
- **The rule in force** (`tools/pr/prepr.sh` at `a7dd7f50d`):
  - Step 3h (lines 3737-3746) runs `--self-test` only when `selftest_owed` (lines 1508-1538)
    finds a changed path among `selftest_inputs`. Otherwise it prints `skip self-test  no change
    to prepr.sh, a program it names or its fixtures`.
  - `selftest_inputs` is prepr.sh itself, every tracked script path it names, `counts.mjs`,
    `render_md.mjs` and the fixtures directory: 56 paths here, derived by sourcing those lines.
  - Its self-test rows pin the trigger and a null control (lines 3188-3200).
  - That is the proposal's rule: "the diff touches prepr.sh or its self-test inputs".
- **Main's merge is already excluded at the open.**
  - The changed-path list is `git diff "$BASE"...HEAD`, with `BASE=$(git merge-base origin/main
    HEAD)` (line 3525).
  - `open_pr.sh` merges origin/main into the code head first (lines 103-105). So at the open,
    BASE is main's tip, and the list is the authored head's own changes.
  - The proposal's "an open's merge of main that touches neither skips it" is therefore already
    what happens.
- **The rule run on today's ten opens** (C from `s9/seat-opener/driver4.log`; the three-dot diff
  of C against its merge base with origin/main, matched against the 56 inputs):
  - Five owe 3h through C's own files:
    - `632bd15b9`: `tests/entities.py`, `tests/features.py`.
    - `fddb9a1bf`: `tests/features.py`.
    - `6aea809f6`: `tools/audit/carry_audit.py`, `roster_lib.py`, `brief_lint.mjs`.
    - `c18116991`: `tests/closure.py`, `tests/entities.py`, `tools/pr/prepr.sh`.
    - `d1afdcf87`: `tests/closure.py`, `tests/entities.py`.
  - Five owe nothing: `9a1a9835f`, `5f1c1d80b`, `e316cdb95`, `f25b5d6a2` and `df25f62e4`.
  - The proposed rule selects exactly the same set, so it saves 0 h.

Cost: a re-statement of `selftest_owed` in `prepr.sh`, the most-run gate file, plus its self-test
rows.

Binding:
- No benefit: the rule exists, and on today's opens the proposal skips nothing the tree does not
  already skip.
- What would change the answer is a narrower trigger. The self-test is one program of 431
  checks, keyed on 56 inputs, and the five owing heads above owe it through `tests/entities.py`,
  `tests/features.py` and `tests/closure.py`, which prepr.sh names as programs it runs. A
  proposal would need a measured per-row input map showing that a change to those files cannot
  move the rows that take the 23-74 min, with the minutes it would save. The open-time re-run of
  a self-test the fixer already ran at the same head is the dropped reuse question, not this one.

## P348: bus.sh dispatch's review-carry refusal carries a blocked verdict

Verdict: ACCEPT, as a carry on R10-FLY-RAISE-REVIEWABLE (P345, `not-started`; it lands with this
batch). Both are refusals in the same function, `bus.sh dispatch`, that stop a review the head
needs. One fixer and one review take both. The carry is in the group JSON's `carry` list.

Source: the orchestrator s9's triage-queue line of 2026-10-31T21:45:00Z (`s7/triage-queue-s7.txt`
line 39).

Instances:
- **The refusal** (`tools/audit/seat/bus.sh` at `a7dd7f50d`):
  - Lines 484-494: when `--reviewed-head <rh>` is given and no `--nonce`,
    `review_carry.py "$rh" "$h" --verdict-only` answering CARRY (rc 0) dies: "the prior review
    carries, so no second reviewer is dispatched".
  - `review_carry.py` reads only the commit range (its docstring: "THE TEST IS A COMMIT RANGE").
    It never reads what the prior review decided.
  - The ruling it implements is "if there are no code changes, the previous review can be
    carried" (tvofi, 2026-10-27). A blocked review carried leaves nothing to merge, so carrying
    it blocks the answer the review asked for.
- **#3045 round 3 at `9ef51b82`:** a metric-gamed block was answered by a body re-take with the
  head unmoved. The dispatch went out only by omitting `--reviewed-head`, which also drops the
  check for the case it exists for.
- **The shape's frequency**, over all 493 `verdict/<pr>` refs (fetched to `refs/scratch-v/*`,
  then `git log --format='%cI %s'`, matching `verdict: #N Fix review: <v> <head>`):
  - 1184 verdicts, 437 of them blocked.
  - 97 verdicts sit at a head an earlier verdict on the same PR had blocked.
  - 38 of those fall after the refusal landed (`6f905c40f`, 2026-10-27T19:05Z), for example
    #2962 `9ce0179f`, #3010 `d538f2da` and #3014 `42b228ec`, each blocked and then merged at the
    same head.
  - Each one dispatched with `--reviewed-head` would have been refused. The dispatch seat's
    brief names `--reviewed-head <blocked head>` for exactly these round-2 reviews
    (`s9/seat-dispatch/STATE-HANDOFF.md` line 17, #3048).
  - The 97 can include same-verdict replays. The figure counts verdict commits, not distinct
    reviews.
- **Rule run on each kind:**
  - #3045 r3 (blocked at the head, body-only answer): mints. Correct.
  - A merge verdict at `rh` and a clean range: still refused. Correct; this is the null control,
    the ruling's case.

Cost:
- In `bus.sh`, about 10 lines: a `verdict_at <pr> <rh>` reader of `verdict/<pr>`'s history,
  beside `blocked_rounds` (lines 396-403), which already reads that ref.
  - The CARRY refusal fires only when the latest verdict naming `rh` is `merge`.
  - A blocked verdict, or none, mints, and prints `review-carry: <rh> was blocked, so a fresh
    review is owed`.
  - An unreadable ref refuses, as `blocked_rounds`' callers do.
- Three self-test rows beside the carry rows (around line 930): blocked at `rh` mints; merge at
  `rh` refuses (null control); unreadable refuses.
- One clause in `dev/governance/roles/orchestrator.md` line 172: "against a reviewed head whose
  verdict was merge". That is a policy file. It merges on tvofi's approving review or under
  mandate 6329234399, which is in force with scope all.
- `bus.sh` has no `policy_lint.mjs --budgets` row. Whether `orchestrator.md`'s role cap has room
  for the clause is the fixer's to check with `--budgets`; if it has none, the fixer cuts an
  equal amount of text.

Binding:
- The refusal blocks the one review a blocked verdict asks for, and the shape occurred 38 times
  in four days.
- The workaround disables the check entirely.
- The fix is about 10 lines in a function the same group already opens. The benefit clearly
  outweighs the cost.

The carry:
P348: in `tools/audit/seat/bus.sh` `dispatch`, the review-carry refusal (lines 484-494 at
`a7dd7f50d`) fires only when the latest verdict naming the reviewed head in `verdict/<pr>`'s
history is `merge`. Read it with a `verdict_at` beside `blocked_rounds`. A blocked verdict, or
none, mints and prints `review-carry: <rh> was blocked, so a fresh review is owed`. An unreadable
ref refuses. Basis: #3045 round 3 at `9ef51b82`, dispatched only by omitting `--reviewed-head`; 38
verdicts since `6f905c40f` sit at a head an earlier verdict had blocked. Rows: blocked at `rh` with
a clean range mints; null control: merge at `rh` with a clean range refuses (CARRY); unreadable
refuses. One mutant drops the verdict test, and the blocked row fails. Amend
`dev/governance/roles/orchestrator.md` line 172 with "against a reviewed head whose verdict was
merge". triage: dev/programme/triage/s6-batch95.md#P348
