# R11-RCA-BOTMERGE-ROW: a budget row only the branch measures breaks on every merge of main

Root-cause seat (`dev/governance/roles/root-cause.md`, `dev/governance/rules/defect-root-cause.md`)
beside #3735 (R11-SEAM-ratchet-raise), never inside it. This document edits no workflow, no
test and no instrument: the tooling freeze is in force, so the countermeasure is a proposal
(`P-R11-BOTMERGE-ROW`) and an untracked overlay prototype. Trigger: the red-check trigger,
`tests / fast (3.14)` red at six heads of #3735, named in its body's `## Red checks` as the third
instance of a class handed to a root-cause seat. Measured on 2026-11-22 against `origin/main`
`726e5bbc32`, branch `fix/r11-seam-ratchet-raise` at `08c19e58ae`.

## 1. The cause, reproduced

`045f358a4f` (2026-11-18) adds the metric `module_excess_loc` to `tests/structure.py` (each
module's span past `MODULE_LOC_LIMIT`, 2000, summed) and its key to `tests/structure_budgets.json`.
Main's `tests/structure.py` does not measure it and main's budget file has no such key
(`git show origin/main:tests/structure_budgets.json`).

`.gitattributes` merges the budget file with the `ledgermerge` driver. Its rule for a key, from
`tools/merge/ledger_merge.py`'s docstring: "a key one side changed takes that side"; for a count
both sides changed, "base plus both deltas". An existing row therefore follows main: main's own
pull requests re-record it, and the driver adds main's delta to the branch's. A branch-only key
has no main side: every merge of main keeps the branch's recorded value, while main's code moves
the quantity the branch's counting rule measures. `tests/structure.py` at the merged head then
fails, in either direction (an unrecorded gain is exit 2 too).

The six breaches, each read from the failing job's log (`gh api .../actions/jobs/<id>/logs`, the
`RESULT module_excess_loc=` and `FAIL module_excess_loc` lines); each head is a `ci: merge main`
commit by `merge-main.yml`:

| head | job | line |
|---|---|---|
| `382df86816` | 135436031929 | `gain module_excess_loc 21536 (budget 21549, -13; not yet recorded)` |
| `011a463926` | 135520088877 | `FAIL module_excess_loc 21571 > 21549 (+22)` |
| `f50a75b4f7` | 135603189444 | `FAIL module_excess_loc 21633 > 21571 (+62)` |
| `430bc6bfad` | 136821033342 | `FAIL module_excess_loc 21694 > 21633 (+61)` |
| `5e4a4a6a24` | 136990440813 | `FAIL module_excess_loc 21816 > 21718 (+98)` |
| `d4bd8ed29e` | 137012722292 | `FAIL module_excess_loc 21779 > 21718 (+61)` |

Which side moved: the main side, every time. The repair seat's attribution, the same span sum
over main's own tree (`max(0, tree.body[-1].end_lineno - 2000)` for each `.py` under
`custom_components/heatpump_optimizer/` at `git show <rev>:<path>`), reads main itself as 21718 at
`e698fc8ac3` and `80331098f4`, 21816 at `35402f7817` (#3737) and 21779 at `4ebd430fbf` (#3728),
equal to each breached head's measurement; every re-record commit on the branch
(`ef7d2e4038`, `0800f342ef`, `b278df39d6`, `bd58b7341e`/`21428d8202`, `611f843468`) names main's
modules and "no line of this PR moved the figure". The branch's code did not cause one of them.

The reported shape ("a bot main merge breaks the same budget row", three instances) is a symptom
of a wider one in two directions: it is six breaches, not three, on one row; and it is not the
bot's: the bot is only the commonest path that merges main. `8f34cd23e0`, a seat's own merge of
main, re-recorded the same row (`ef7d2e4038`). Any merge of main into a branch that carries a
branch-only key does it.

## 2. Why the base keeps going stale

The seats did not start from a stale base. Each re-record was taken at its own merge base (the
`recorded_at` of `611f843468` is `4ebd430fbf`, main's tip when it was written). The base went
stale underneath a correct record because the pull request stayed open while main moved:
87.7 hours from `createdAt` 2026-11-18T15:01:46Z to this measurement, 59 first-parent commits on
main in that window (`git rev-list --first-parent --count --since=2026-11-18T15:01:46Z origin/main`),
25 `ci: merge main` commits on the branch. A value measured at one base is carried to the next
base by a path that re-measures nothing: the merge driver by design, and `merge-main.yml`, whose
only steps are the driver install, `merge_main_bot.py run`, and dispatching and approving the held
checks. `ci-autofix.md` keeps it so: "Do not automate ... structure budgets".

That is the process-wide class, and it is already on record twice: figure blocks
(`R10-RCA-FAMILY-FIGURE-BLOCK-STALE.md`: "no process re-renders a body when a bot moves the
head") and the self-test table (`R10-RCA-FAMILY-SELFTEST-SCOPE-DRIFT.md`). Loop card L9 (owner:
yes) and triage P748 route all of it to R11-PRE-SHARED-FILES: the structure budgets become
"generated after merge instead of edited inside pull requests" (the group's brief). Part 1
(#3708, merged 2026-11-20) built the self-test table only; parts 2 and 3, which carry the
structure budgets, are unbuilt. So the class barrier is ruled and unbuilt for this artifact, and
the instance in front of it is a pull request that must, by its nature, edit the file: it adds a
counting rule.

## 3. Process state: (d)

The ratchet process was sound under a precondition it does not check: every key in the budget
file is measured on both sides of a merge, so main keeps its own rows current and the driver's
"base plus both deltas" carries main's motion into a branch. A pull request that adds a key
removes the main side, and nothing notices: the driver takes "that side", the bot pushes, and
`tests/structure.py` is the first reader, about 30 minutes into `tests / fast (3.14)` (job
135436031929 started 06:11:37Z, the structure step failed at 06:41:49Z).

Not (b): each seat followed the procedure (record at the merge base, the reason in the commit
message, per the owner's 2026-11-18 ruling for this row: "the module-span limit to 2000",
`dev/programme/RULINGS.md`). Not (a): the barrier exists as a ruled design, and its unit does not
reach this instance. `design/R11-PRE-SHARED-FILES` at `20cafac7df`, line 69, prices a pull
request's key against "the smaller of the base's budget and the value measured on the merge-base
tree"; a key absent at the merge base has no base budget, and invariant G1 (line 98) admits "a
budget key added ... in a diff that also changes `tests/structure.py`, whose value must equal the
head's measurement" - the same condition every main merge breaks. Built as approved, the design
leaves this shape red.

## 4. Class reach

- **Branch-only keys, other pull requests.** First-parent commits of main since 2026-09-01 whose
  `tests/structure_budgets.json` key set gains a key against the first parent (each commit of
  `git log --first-parent --since=2026-09-01 origin/main -- tests/structure_budgets.json`, keys
  compared by `json.loads` of `<sha>^1` and `<sha>`): `b38e079f8c`, `841fe0f800`, `d737ab05b3`,
  `6a70396dfd`, `2b6c5b876e`, `8186403516`, `f0a4acac79`, `f269ecccb5`; the same comparison over
  every `*_budgets.json` finds 33 such commits.
  Of the structure ones merged after the bot (2026-10-08): #2340 (`class_excess_loc`) re-stamped
  once after a main merge (`40683e8d7d`, 18498 -> 18468); #2415 and #3729 none.
- **Existing rows a branch also edited.** `1339cf925b`, `b6dad803a2`, `b8353012f5` and
  `9a4e7bf85d` re-record rows after a main merge where both sides wrote the same value or
  a counting rule changed on main; the approved design's merge-base ceiling (line 69) covers these.
- **The inverse.** A key main has and the branch lacks: the driver takes main's key and the
  merge is clean; the failure seen was a predictor reading a base-overlaid render
  (`P-R11-CIPREDICT-ECHO-EXEMPT`, #3837), a different mechanism.
- **Other budget files.** `tests/mutation_budgets.json` shares the driver (`LEDGERS`, "sum") and
  so the shape; the others carry no driver and conflict instead (`DIRTY`, no CI run).

## 5. Cost test

    cost(countermeasure, recurring) < cost(defect) x P(recurrence)

- **cost(defect)**, wall-clock per breach. From the breached head's commit to the re-record commit:
  279, 40, 77, 40, 119 and 30 minutes (`git log --format=%cI`), mean 97.5. The repaired head then
  waits on `tests / fast (3.14)` again, 28 to 46 minutes per run in the table's jobs. The pull
  request's `tests / fast` was red from a bot head to the next green pushed head for 8 h 57 m
  (2026-11-19), 22 h 21 m (2026-11-20/21) and 2 h 50 m (2026-11-21/22), which bounds it above;
  other review work shares those spans. Each repair is one seat turn (attribution, a payment tried
  and refused, `--record --allow-regression`, a body `## Red checks` line) and re-arms the
  budget-raise approval at the new head. Taken: about 120 minutes per breach.
- **P(recurrence)**: measured, 6 breaches on one pull request open 3.65 days in round 11 (1.6 a
  day while open); 1 in round 10 (#2340). The row sits at zero headroom now (head budget 21779,
  main 21779), so the next main merge that grows a module past 2000 lines breaks it again.
  Over a round, 3.5 breaches (the mean of the two rounds).
- **Right side**: 3.5 x 120 = about 420 minutes a round.
- **cost(countermeasure, recurring)**, the narrow arm in section 6: a key-set comparison of the
  head's and the merge base's budget file on every structure run (under a second); only where the
  head carries a branch-only key, one more measurement of the `recorded_at` tree (the
  `tests/structure.py` step took 16 to 28 s in the six jobs above). #3735 had 12 pushed heads,
  about 2 runs each: 24 x 28 s = 11 minutes for the pull request's life. Induced work: one design
  amendment and one delta design review of R11-PRE-SHARED-FILES parts 2 and 3, once.
- **Verdict**: about 11 minutes against about 420 minutes a round. It pays. The class is also an
  audit class (six instances in one round), which owes a class-eliminating barrier regardless.

## 6. Countermeasure

Rungs in order.

1. **Delete.** Not possible alone: a pull request that adds a counting rule must carry the key
   while it is open, and main moved 16 first-parent commits a day in this window. Shortening the
   window is the partial delete: a pull request whose diff adds a `*_budgets.json` key is put on
   the critical path once approved. It costs no tooling and is the orchestrator's dispatch call.
2. **Self-repair.** The merge path re-records the branch-only row by main's own delta. Refused as
   a first choice: `ci-autofix.md` forbids automating structure budgets, a re-record upward is a
   raise (`CLAUDE.md` rule 2), and the delta is only main's if measured with the branch's rule on
   two trees, which is the narrow arm's measurement anyway.
3. **Narrow (proposed).** Amend R11-PRE-SHARED-FILES parts 2 and 3 before they are built: in
   `ratchet`, a key absent from the merge base's budget file is priced at
   `head budget + (measure(merge base) - measure(recorded_at))`, both measured with the running
   copy's counting rule, so a breach is the branch's own movement only; G1's exception records the
   key's value at its `recorded_at`, not "equal to the head's measurement". No new refusal: the
   existing `ratchet` refusal moves from main's motion to the branch's. A self-test owed: failing
   first, a branch-only key and a main commit growing a module past the limit, red today; then
   green; null controls: the branch's own growth of the same row still refuses, and a key present
   at the merge base keeps the line-69 ceiling.
4. **Interim, untracked (freeze).** An overlay the orchestrator runs after a merge of main into a
   pull request whose head carries a branch-only key: the prototype `botrow.py <repo> <head>
   origin/main`, out of tree and named in proposal P-R11-BOTMERGE-ROW. It names the
   branch-only keys, measures them with the head's `tests/structure.py` at `recorded_at`, the merge
   base and the head, prints `BOTROW-BREACH` with main's and the branch's deltas and the repair
   command, and writes nothing. Demonstration in section 7. It finds the breach before
   `tests / fast` reaches the structure step, about 30 minutes in; the repair stays a seat's.

## 7. Demonstration of the overlay prototype

The prototype at sha1 `a0ff4e25ac6f2fc85b66d5394e91e3fb6c3059fc`, run on 2026-11-22 against
`origin/main` (then `40e513eea4`) on a host at load average about 65, so local walls are not CI's:

- **On the defect, `d4bd8ed29e`**: `BOTROW-BREACH module_excess_loc budget=21718 head=21779
  main_delta=+61 branch_delta=+0 recorded_at=e698fc8ac3 merge_base=4ebd430fbf`, "the move is
  main's", rc 1, 535 s. CI's job 137012722292 read `21779 > 21718 (+61)`.
- **On the defect, `430bc6bfad`**: `budget=21633 head=21694 main_delta=+61 branch_delta=+0`, rc 1,
  416 s. CI's job 136821033342 read `21694 > 21633 (+61)`.
- **Once fixed, `f0f7ff15c2`** (`611f843468` merged into the head): `BOTROW-OK
  module_excess_loc budget=21779 head=21779 main_delta=+0 branch_delta=+0`, rc 0, 227 s. It measured
  both trees (`recorded_at` is the merge base, so two measurements, not three): green by
  measurement, not by skipping.
- **Null control, `origin/main`**: `BOTROW: no branch-only key`, rc 0, 1 s; no tree is measured
  where no key is branch-only, which is the standing cost on every other pull request.

Not demonstrated: a breach of the branch's own making (`branch_delta` nonzero) printed as "not
main's alone". The narrow arm's tracked self-test owes it (section 6, rung 3).

## 8. Record

`dev/audit/config/bugclasses.json`: the instances join `N-postreview-merge-red` ("a ratchet move"
is in its mechanism) as non-round instances, and this file is added to its `rca`. The class stays
`open` until the narrow arm lands; it flips to `barriered` then.
