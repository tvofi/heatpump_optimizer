# R10-RCA-INERT-PREDICT: step 6d refuses an INERT READS that no route it names can repair

The root-cause seat for two instruments that contradict each other. It follows
`dev/governance/roles/root-cause.md` and `dev/governance/rules/defect-root-cause.md`,
and ran at `origin/main` `52f698905`. The seat posted nothing and filed no issue.

The contradiction, on the tree at that SHA:

- `tools/pr/prepr.sh` step 6d runs `tools/pr/ci_predict.py`. It refuses a
  predicted `closures` INERT READS before the push. Its comment cites R9-RO-11:
  "the autofix jobs repaired none of them". Its last line sends the seat to
  `ci-autofix.md` for who repairs what.
- `ci-autofix.md` says `closures-autofix` merges INERT READS from CI's Linux
  recordings. It tells the seat to wait, and not to Darwin `--single` a
  recording CI already made.
- `tests/harness_headers.py` reads every file under `dev/audit/harnesses/`
  from a child process. Only Linux `strace -f` sees that read. A Darwin seat
  cannot record the entry, and it cannot push past 6d without it.

The trigger is the second one in `defect-root-cause.md`. On #2371
(R10-LEAF-IMPORTS) step 6d refused twice. The fixer then moved the harness to
`tools/audit/seat/` to get out of the glob. Review called that move
metric-gamed. The fixer then hand-wrote one `inert_reads` line through
`closure.write_closures`, which is the route of main's precedents `2f7aafdc8`
and `d5b85a501`. No instrument and no rule names that route.

## 1. Both sides, reproduced at `52f698905`

Evidence is under the seat's scratch `ev/`. The plant is a five-line harness
with a RESULT header, `dev/audit/harnesses/rca_planted_probe.py`, committed on
a branch cut from `origin/main`.

**prepr's side.** `ci_predict.py --base origin/main` on the plant prints:

    PREDICT closures INERT READS tests/harness_headers.py: dev/audit/harnesses/rca_planted_probe.py (a new file beside 40 it lists)
    CI PREDICT: 1 predicted red(s) on closures against 52f698905868 -- repair before the handoff; who repairs which is ci-autofix.md's

It exits with rc=1, so step 6d refuses.

**The Darwin recorder's side.** The child-process claim was tested, not
assumed. Under an in-process `sys.addaudithook`,
`harness_headers.check_repo_roots()` runs its child scan. The hook saw no open
of the planted file, and `_scope_paths()`, which the child walks, does list it
(`ev/darwin_parent_read.txt`). The parent reads only
`dev/audit/rounds/round*/D*/*.py` itself, through `_discover`. The child's
`inline_scan` reads `dev/audit/harnesses/`.

**CI's side.** `closure.affected(['dev/audit/harnesses/rca_planted_probe.py'])`
returns `scoped`, with `tests/harness_headers.py` selected `via inert_reads
(dir: dev/audit/harnesses)` (`ev/plant_affected.txt`). So a scoped CI run
re-records the reading script. The real runs show that the bot then repairs
the entry:

| run | scope | `closures` job | `closures-autofix` | bot commit | what it added |
|---|---|---|---|---|---|
| 38296697023 (#2157, 2026-10-12) | `SCOPE_CASE: scoped`, `SCOPE_SCRIPTS: tests/harness_headers.py` | failure, 19:18:08 to 19:22:23 | `AUTOFIX: changed`, 19:22:26 to 19:22:56 | `36ca97b6b` | 1 harness_headers entry under `round9/prestudy/` |
| 38738096725 (#2251, 2026-10-15) | scoped | failure, 12:54:59 to 12:58:19 | `AUTOFIX: changed` | `e1ac127d3` | 28 entries |
| 38716543452 (#2244, 2026-10-15) | full | failure, 10:04:51 to 10:23:38 | `AUTOFIX: changed` | `c013415cf` | 177 entries |

Each of those `closures` logs prints `INERT READS UNDER-APPROXIMATED` with the
`tests/harness_headers.py:` lines. The logs were read through the jobs API and
are kept under `ev/run<id>/`. All three are new directories, so the sibling
arm did not fire there: `inert_siblings` needs three listed siblings in the
same directory. 6d stayed quiet, the seat pushed, and the bot repaired.

**Is R9-RO-11's premise still true after #1886? No, not for INERT READS.**
The premise was measured before 6d landed (`00007b44c`, 2026-10-07). Since
#2049 (R9-CI-1, on main 2026-10-08 08:40) the bot merges INERT READS. Since
#2129 (on main 2026-10-12 13:17) a scoped run re-records the reading script.
Run 38296697023 is the scoped repair, 6 h after #2129 landed.

## 2. Cause and process state

**Cause.** The refusal still has a reason, but its stated reason and its
named route both went stale. The refusal is still worth having. The bot's
repair costs a red `closures` run, about 4 min 15 s scoped in run 38296697023.
It also costs a commit on the head after the push. That commit moves the head
under a review that `fix-review.md` freezes, and a head that moved under
review is a blocked verdict. The bot's head also lacks the `pull_request`
contexts until an App push (`ci-autofix.md`). So a pre-push repair is still
cheaper. But 6d names no pre-push repair. It points at `ci-autofix.md`, and
that file names only the bot route, which 6d has just forbidden.

**Process state: (d), its preconditions changed underneath it.**

- When 6d was written (`00007b44c`, 2026-10-07), `ci-autofix.md` at that SHA
  read: "repair a missing `inert_reads` entry by merging the CI
  closure-recordings artifact". That was a seat's repair. The pointer
  "who repairs which is ci-autofix.md's" led to a route.
- Precondition 1 moved with R9-CI-1 (`f5a547322`, on main through #2049).
  The bot took the repair, and `ci-autofix.md` was rewritten to say so
  (`37e560679`). 6d's pointer now leads to "wait".
- Precondition 2 moved with #2129 (`1ec5ce967`). The revert `0f64774f6`
  (2026-10-08) had kept the refusal because a harness-only diff took the skip
  arm: "a scoped CI run does not re-record the reading script". After #2129
  it does.
- Neither change touched 6d. `ci_predict.py`'s docstring and `prepr.sh`'s
  comment still assert "repaired none".

This is not (b). Seats obeyed 6d and did not wait when they could not push.
It is not (c) either: each instrument does what it was built to do, and the
rule it points to was rewritten after the pointer was made. The (d)
countermeasure makes 6d state the route it requires, from its own output,
instead of borrowing a pointer from a file that can move.

## 3. Class search: every `inert_reads` entry, hand-written against bot-merged

`ev/class_search.py` walks every non-merge commit on `origin/main` that adds
an `(script, file)` pair to `inert_reads` (`ev/class_search.txt`):

- **60 commits: 11 bot (`ci: re-record closures`), 49 hand-written.**
- Since #2129 landed (2026-10-12 13:17): 3 bot commits (`36ca97b6b`,
  `c013415cf`, `e1ac127d3`), each on a new directory 6d could not predict.
  There were 15 hand-written commits (`ev/post_precondition_hand.txt`).
  Fourteen of them add `tests/harness_headers.py <- dev/audit/harnesses/<new
  file>`, from `d7bfeb0dd` (2026-10-14 23:14) to `2f7aafdc8` (2026-10-17
  01:59). That is every new-harness pull request in the window. The fifteenth
  (`0461329ce`) is `entities.py`'s and outside the class.
- All 14 hand-written entries still stand in `origin/main`'s table. Main's
  push runs after `2f7aafdc8` are green (39089195755, 39085984214,
  39084306630, 39082469553), and a push to main forces the full arm, so
  Linux's recording agreed with each hand-written line. The hand route is
  sound. It is unnamed, and #2371 shows a seat that does not find the
  precedent tries something worse.
- The wider shape is an instrument whose refusal points at a rule that moved.
  The search also found the same shape in the other 6d arms. ADDED UNPINNED
  already warns and names `## Unpinned sites`, and STALE PIN names its repair
  in its own `CI PREDICT` line. Both say the repair in their own output.
  INERT READS was the one arm that delegated its route.

## 4. Cost test

    cost(countermeasure, recurring) < cost(defect) x P(recurrence)

- **P(recurrence), measured.** 14 occurrences in 2.1 days, 2026-10-14 23:14
  to 2026-10-17 01:59, one for every new `dev/audit/harnesses/` file. R10 is
  the round that lands harnesses in that directory (fixer.md step 18).
- **cost(defect), per occurrence.** A seat that finds the precedent pays one
  JSON edit by hand and a second prepr run. This seat did not measure that.
  For a seat that does not find it, #2371 is measured. The harness commit
  `63ec8f870` is 00:23:25 and the move commit `9d68037b6` is 03:32:00, an
  interval of 3 h 09 min that holds two refusals. The move then cost a review
  round, called metric-gamed. The 3 h 09 min is an upper bound on what the
  defect cost, not the defect's cost alone. A seat that obeys
  `ci-autofix.md` literally and pushes past 6d pays at least one red
  `closures` run (4 min 15 s scoped, run 38296697023) and 30 s of autofix. It
  also pays a bot head that needs an App push before its required contexts
  exist.
- **cost(countermeasure, recurring).** Zero seconds on every run that
  predicts nothing: the flag is opt-in, and collecting the pairs is a set
  insert inside loops that already run. `ci_predict.py` measured 3.14 s,
  3.61 s and 4.29 s over three runs (`ev/t*.txt`). The new self-test arms add
  one `--apply-inert` with two predicts, one null-control predict and one
  layout parse to `prepr.sh --self-test`, which `tests/entities.py` drives.
  The wall time of `--apply-inert` was 16.42 s, 10.62 s and 7.27 s, measured
  while a self-test ran beside it, so those figures are upper bounds
  (`ev/apply_timing.txt`). Call it under 15 s per `entities.py` run.
- **Verdict.** 14 occurrences in 2.1 days at even one prepr re-run each
  (minutes) is more than 15 s per entities run, unless entities runs about
  50 times a day for every occurrence. A single #2371-shaped occurrence pays
  the standing cost for months. **Build it.**

## 5. Countermeasure, on this branch

It addresses state (d): 6d now states in its own output the route it
requires, so a later change to `ci-autofix.md` cannot strand it.

1. `tools/pr/ci_predict.py --apply-inert` collects the `(script, file)` pairs
   from both INERT READS arms, the sibling glob and the import edge. It adds
   them to `tests/closures.json` through `closure.write_closures`, the
   table's one writer, then predicts again. The entry it writes is what CI's
   Linux recording would merge. At worst it is an over-approximation, the
   direction `_fold_inert_reads` keeps.
2. When any INERT READS is predicted, the predictor prints the route:
   ``CI PREDICT: an INERT READS entry is written with `python3
   tools/pr/ci_predict.py --apply-inert` and committed; ...``.
3. The stale premise is corrected in `ci_predict.py`'s docstring and in
   `prepr.sh`'s 6d comment. Both now cite #2049, #2129 and run 38296697023,
   and say why the refusal stays.
4. There are three `prepr.sh --self-test` arms beside the existing `pinert`
   arm: the apply clears the prediction (rc=0), the table passes
   `closure.layout_errors`, and `--apply-inert` on the null branch leaves
   `tests/closures.json` byte-identical.

**Shown to detect** (`ev/demo_plant.txt`, `ev/demo_null.txt`):

- On the defect, the plant: `PREDICT closures INERT READS ...`, then the route
  line, rc=1.
- After `--apply-inert`: `APPLIED inert_reads tests/harness_headers.py:
  dev/audit/harnesses/rca_planted_probe.py`, then `no closures or fast red
  predicted`, rc=0. The diff is one inserted line in sorted position, and
  `layout_errors` returns `[]`.
- Null control: a diff that changes only the predictor gets rc=0 and an
  empty `git status --porcelain -- tests/closures.json`.
- It does not go green by skipping. The arm still refuses before the apply,
  and the self-test's `pinert` arm still requires the PREDICT line.
- Mutation proof. With `apply_inert`'s write disabled (`if added and False:`),
  `prepr.sh --self-test` prints `FAIL --apply-inert writes the predicted
  entry, and the prediction then clears (got 1, wanted 0)` and ends at 276
  passed and 1 failed, rc=2. The unmutated head ends at 277 passed and 0
  failed, rc=0.

**Not landed, because it is policy and needs tvofi's approval.** This is a
draft for `dev/governance/rules/ci-autofix.md`, to follow the sentence that
ends "the bot merges INERT READS from CI recordings too (#1886, R9-CI-1)":

> One 6d predicts is not the wait: `prepr.sh` refuses it before the push, and
> `python3 tools/pr/ci_predict.py --apply-inert` writes the entry the Linux
> recording would — that commit is not a `--single`.

It addresses (d) in the rule as the code change does in the instrument: the
rule's "wait" then covers only the INERT READS CI finds and 6d did not
predict. It adds one sentence against `ci-autofix.md`'s cap in
`policy_budgets.json`; this seat did not measure the headroom. Without the draft,
the instrument's own line already names the route. The draft removes the
contradiction for a reader who starts at the rule.

## 6. Found on the way, outside this scope

`tools/pr/prepr.sh` line 1741 on `origin/main` puts `` `slot` `` inside a
double-quoted label. The shell runs it as a command (`slot: command not
found` in the self-test output). The fourth argument then shifts, so the arm
prints `ok   0` instead of its label. The comparison itself still runs. This
is reported to the orchestrator, not fixed here.
