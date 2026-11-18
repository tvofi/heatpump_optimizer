# R10-RCA-PUSHER-CENSUS-ESCAPE: pull requests merged `instrument-self-tests` reds their own diffs introduced

The root-cause seat's analysis for the class R10-INTRODUCED-REDS-BARRIER
barriers, landed by that group's fixer in the root-cause seat's terms (triage
`dev/programme/triage/s6-batch200.md#P626`). Every figure below was re-measured
at the fixer's merge base `60413046e3` on 2026-11-11 (`date -u` 14:17Z), by the
command beside it. Carried figures are marked as carried. Run and job reads
use `A=repos/tvofi/heatpump_optimizer`.

## 1. The defect

#3425 (`ee64358be`) merged with `governance / instrument-self-tests` red on
four steps that its own diff turned red. The four are the sweep template
render and the three `pr_args.sh` census steps (the PR opener, the PR argument
builder and the PR updater). From that merge on, every push to `main` reads
red on the same four steps. Enumerator, the built check at each merge's
second parent against the merge base of its parents:

    m=ee64358be; python3 tools/audit/seat/merge_train.py introduced \
      $(git rev-parse $m^2) --base $(git merge-base $m^1 $m^2)

It prints 4 `INTRODUCED` lines and exits 1 at `c93903f075` against
`a7628041dc` (head job 130479299736, base job 130352715261). The same
command for #3361 (`8652aa65ce`) prints 2 lines (the two `selftest_scope.py`
steps) and exits 1 at `825f549270` against `b8f67a7751` (head job
129632490622, base job 129479891231). Main was still red when this was
measured, 3.06 h after #3425's merge
(`git log -1 --format=%cI ee64358be` = 11:13:48Z): the push job of
`0a2139b1d` (130543139624) is red on the same four steps plus the push-only
drift step.

Instances: 2 merges measured (#3361 and #3425). The root-cause seat counted
3, #3425 twice because two independent causes (`c966df873`, the remerge
exit-code change, and `c6c04f21b`, the plan-beat cap hand-off) reached it.
That attribution is carried, not re-measured. A scan of every merge since
the ruling was not run: 137 first-parent commits
(`git rev-list --first-parent --count 234ff52c75..origin/main`), each one
filtered check-run read, would answer it. Until then, 2 is a lower bound.

## 2. The cause

`instrument-self-tests` is in no required set: decision 0013's
`HPO_JOB_GRADES: nothing` boundary keeps the self-tests out of any grading
job. The 2026-11-07 ruling (`234ff52c75`, committed 2026-11-07T19:15:02Z)
narrowed the reds a body owes an answer to the set
`merge_train.py owed-reds` prints. The job is outside that set. So #3425's
body owed no `## Red checks` line, `classify` printed GREEN over the required
contexts, and no reviewer rule read the job. The merges fell 2.39 d (#3361)
and 3.67 d (#3425) after the ruling, by the commit dates of `8652aa65ce`,
`ee64358be` and `234ff52c75`.

## 3. The process state

**(d), the preconditions changed.** Before the ruling, `pr-contract` made a
body answer every red at the head, so an introduced self-test red needed an
answer and drew a reviewer's block. The ruling removed that obligation for
non-required checks, correctly for reds inherited from `main`. It removed the
backstop for reds a pull request introduces too, and no process noticed that.
The comment above the job in `.github/workflows/governance.yml` still said
`pr-contract` made the body answer such a red.

## 4. The cost test

- The defect costs main red from the merge until a hotfix lands. #3425's
  red was 3.06 h and still standing when measured, so that is a lower bound.
  The root-cause seat's figure of about 6 h per occurrence (main red plus
  seat-hours), at about 0.6 occurrences per 17 h release cycle, is carried.
- The countermeasure (C1) costs nothing on a head whose `instrument-self-tests`
  job did not conclude failure, beyond the check-run read the caller already
  makes. On a red head it adds one filtered check-run read at the base and one
  job-step read per side. `review_packet.introduced_reading` at `c93903f075`
  measured 2.53 s for its four reads, the head's filtered listing included.
- The class reddens `main`, which meets the owner's bar without a percentage.

## 5. The countermeasures

- **C1, built (R10-INTRODUCED-REDS-BARRIER).** `merge_train.introduced_at` is
  the one rule. A step concluded `failure` at the head and not at the latest
  concluded run at the merge base is INTRODUCED. The push-only drift step
  (`Refuse a self-test read set the committed table misses`) is excluded. No
  base run counts every head red. A step skipped by scoping concludes
  `skipped`, so it is never red. An unreadable input fails closed.
  `classify --pr` reads an introduced red as RED, so `bus.sh dispatch` and a
  cloud reviewer's wait both stop on it. `review_packet.py` refuses it as
  `introduced-red`. `fix-review.md` step 11 makes it a block. A red inherited
  from `main` stays unowed, as the 2026-11-07 ruling holds.
- **C2, refused as a barrier.** A census arm in `prepr.sh` covers one step,
  not the class. It is the recorded fallback.
- **C3 and C5, refused.** C5 costs 431 s or more per `prepr.sh` run (carried).
- **C4, refused.** Making `instrument-self-tests` required conflicts with
  decision 0013's `HPO_JOB_GRADES: nothing` boundary.

## 6. The detector shown to detect

The acceptance pairs, all through
`python3 tools/audit/seat/merge_train.py introduced <head> --base <base>`:

| pair | INTRODUCED | rc |
|---|---|---|
| `c93903f075` (#3425 head) against `cbd23f1c8b` | 4 | 1 |
| `cbd23f1c8b` against `f24d107bd7` (both red on the drift step alone) | 0 | 0 |
| `0a2139b1d` against `ee64358be` (both red on the same 4 steps) | 0 | 0 |

The third row is the inherited-red control: removing the base subtraction
turns it to 4 with rc 1. The second row is flat under that mutation, because
its only red is the excluded drift step. The root-cause seat's scratch probe
(a head-versus-base comparison of job step conclusions over saved job JSON)
reproduced the first two rows; it stays out of the tree, and the built check
replaces it.
