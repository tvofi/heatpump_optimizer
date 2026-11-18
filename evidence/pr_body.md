R11-PRE-NO-READ-BUILDERS, part D of the approved design (design/R11-PRE-NO-READ-BUILDERS de4e49ddc1558abbc64d26049015d16592a42ef2, `Design review: approve` at design-verdict 02b7a5e8c41cd47e5764fa9332b36287b2f6ae1c): a cause per red gate run, in the vocabulary the convergence record already holds (decision 0018 section 3; card E11-N-GATE-CAUSE, and for main card E11-GATE-REDS). Both cards re-read in `dev/audit/yardstick/round11/EVALUATION.json` at the merge base, landed from eval/r11 c04cef7fca50e00fa23466dab28f941a4d5034af (`review.verdict` approve, of 83dc9488180379b859042b5f24b87d94a5a02c95): `decision: accepted`, neither rewritten nor dropped.

**Part C is not in this pull request, and cannot be built at this base.** The design orders C after R11-PRE-TOKEN-LEDGER's merge, and the per-session iterator C imports does not exist (`## Figures`). The load count of E11-N-RULE-YIELD, E11-N-INSTRUMENT-YIELD and the workflow run line of E11-N-GATE-CAUSE stay open on the group.

**D. A cause per red run.** `loop_ledger.py --runs DIR` reads `ci_runs.json` and `jobs/jobs_<id>.json` from the directory `round_metrics.py produce` writes and makes no API call. A red is a run attempt whose `gate` job concluded `failure`: a main row on main's push (`event` push and `head_branch` main, `found_by ci-main`), a head row on any other run (no `found_by`). One row per red; its cause is the first of these that holds:

1. a later attempt of the same run went green: `external`;
2. main was red (the row's own run on main; for a head row, main's last push run at or before it, each main run read at its latest attempt): `#<n>`, the pull request merged at main's first red push run after its last green one, parsed by `round_metrics.SUBJECT` from that commit's subject in `--repo`; a spell already open at the first main run in the directory has no opener read and reads `unread` on every row it reaches, until a green main run is read;
3. a later run at the same `head_sha` went green: `external`;
4. on a head row, a later run of the same pull request went green: `#<pr>`. The pull request is the run's `pr`, else the `pr` of a run at its `head_sha`; `head_branch` is never a key.

`roster_lib.is_cause` is the cause test taken out of `convergence_why`, which calls it; a derived cause is held to the same function, and one it refuses reads `unread`. A derived row carries no `rca`, is written to no roster and feeds no other read. `fetch_runs` keeps `head_sha`, `event`, `head_branch` and `pr` on each `ci_runs.json` row; `runs.json` is built from the narrow rows before the four fields are added, so `scorecard.py`'s input is unchanged.

`unread` is a read state, never passed through the cause test (verdict note d-unread-not-a-cause): a merge subject naming no pull request, a head no run names a pull request for, a derived word the test refuses. A run with no job listing at its latest attempt can hold a red no one read (a first-attempt success aside): it prints its own `unread` row and the count becomes `gate_reds unread (k of n runs ...)` with the reds read beside it, by the file's no-partial-value rule.

**The product/machinery column is `gate.status` on a push run and `unread` on any other.** `tools/ci/gate.py`'s `status(jobs, cls)` and `MACHINERY_JOBS` are at the merge base (`## Figures`). A row whose run's `event` is push prints `product <v>, machinery <v>`, `status`'s pair under class `push` over the red attempt's own jobs in `run_jobs`' shape; a job with no conclusion is passed as unfinished, so it reads `unread` in its verdict, as a member not listed at the attempt does. Any other row prints `product/machinery unread (gate.status takes an event class, and pr or pr-cc is not derivable from a cached run row)`. The summary line counts both: `product red p, machinery red m of k push reds (gate.status); product/machinery unread on u (...)`. Each row still lists the attempt's failed jobs as `gate.machinery_line` splits them, over `gate.gate_required()` plus `prelude` and `gate`. `gate.py` is unchanged.

## Departures from the design note, raised

Ruled: the orchestrator accepted all six departures below (the four the design-note list raises and the two the repair of 3fe03e1480 raises) under the owner's mandate 6893738184, recorded at `refs/heads/inbox/r11-pre-no-read-builders` 6aeb520723, INBOX line 1. None awaits a ruling.

- **A red nothing cleared reads `uncleared`, a second read state.** The note derives the cause from the clearing event and names no word for a red with none (an abandoned head, a main red with no red spell read). `unread` would say an input is missing when every input was read. It is counted beside the causes and is held to no vocabulary. Changing it to `unread` is one constant.
- **The note lists three clearing events and no order among them.** The order built is the list above: a green later attempt of the same run first, since it is the same tree; main's red spell before a green at the same `head_sha`, since a pull-request run tests the head merged into main at that time and a later run at the same head can go green because main was fixed. The self-test pins that order with a plant.
- **Step 4 has no `head_sha` test.** A later green run at the red's own `head_sha` already read `external` at step 3, so the note's "at a later sha" is implied, and the clause was an unkillable mutant. With a null `head_sha` on both runs, a later green of the same pull request reads `#<pr>`.
- **`runs.json` projection, as the note asks, by building the narrow rows first** and widening a copy, in place of projecting keys out of the wide row.

Raised by the repair of 3fe03e1480:

- **The column is `unread` on every run that is no push.** The note applies the function to the run's job listing whatever the run. `status` takes the event class, and `gate.event_class` derives `pr` against `pr-cc` from `reaches_custom_components`, a three-dot diff of the pull request's head that no `ci_runs.json` row holds; `no-pr` against `pr` is not derivable either, since a null `pr` on a row is also what a fork's run reads. Printing a verdict under a guessed class would grade a run against members it never required.
- **The pair is over the red attempt's own jobs**, where `status`'s docstring names a run's latest jobs: a row is one attempt, and the latest attempt of a run that went green would read green on its red row.

## Head

`2a374610679c6e56bf3f75a158e60741827451ec` merges the authored code head `44a130aa4eb62e859d149548feb10c58451e00c0`.

`44a130aa4eb62e859d149548feb10c58451e00c0` is the code head, the repair of af0616cbe8dbd95e9a0ccb1e8822949f579a7cba after round 2's `Fix review: blocked` at review/3696 (dd1cc7e774f75950ca71c56f00ef73eb13df51f7). Merge base 8e76c192d269e0837a80d0606f3ac12ebecb223d; `git merge-tree --write-tree origin/main HEAD` exits 0 with origin/main at 99a4010e479f04af984c30a4b5cfc2f98d3736ad, so main is not merged in. The repair is one commit and touches only `tools/audit/seat/loop_ledger.py`'s self-test and its `MUTANTS` table. No line of the read changes.

prepr: passed rc=0 at 44a130aa4eb62e859d149548feb10c58451e00c0

Round 2's block, one item with five swaps, each now with a fixture that tells it apart and a `MUTANTS` row:

1. `summary product reads product` (the product count reads the machinery verdict): run 63, a push red whose product is red and machinery green, joins runs 61/62. The summary must read `product red 1, machinery red 0 of 3 push reds`, and the swap prints `product red 0`.
2. `summary product unread no red` (`a == RED` to `a != GREEN`): the same directory's summary. Runs 61 and 62 read `product unread`, so the swap prints `product red 3`.
3. `summary machinery unread no red` (`b == RED` to `b != GREEN`): the same summary. Run 62 reads `machinery unread`, so the swap prints `machinery red 1`.
4. `summary unread over reds` (`len(reds)` to `len(rows)`): run 70 has no listing and run 71 is a pull-request red. The summary must end `product/machinery unread on 1 (...))`, and the swap prints `on 2`.
5. `column event a push alone` (`== "push"` to `!= "pull_request"`): the `both` listing on a `merge_group` run, and again on a `workflow_dispatch` run on the branch main. Both rows and the summary must read the column unread (`of 0 push reds`, `unread on 2`).

Round 1's three items stay resolved and are not reopened.

## Mutation proof

Round 2 (this repair). The five rows above are in the table and each prints `ok    mutant killed: <row> (by '<check>')` under `python3 -I tools/audit/seat/loop_ledger.py --self-test`. The full self-test at the head ends `loop_ledger self-test: 0 failed`, with no `FAIL` line, 99 `ok` lines (`grep -c '^ok'`) and 35 `ok    mutant killed` lines (`grep -c '^ok    mutant killed'`).

The reviewer's own swaps (`evidence/mut.py` of review/3696 at dd1cc7e774). Unedited, the driver now prints `SKIP <name>: matches N` for six of them, because the `MUTANTS` table quotes each needle. So the same twelve swaps were run with two changes: each swap is applied to the code above `\nMUTANTS = {` only, and the unswapped copy runs first as a control (the driver labels a passing run `SURVIVED`). Run at `44a130aa4eb62e859d149548feb10c58451e00c0`; `git status --short` showed only the uncommitted repair, and the tree was restored after each swap:

~~~text
SURVIVED NULL control: no swap | loop_ledger self-test: 0 failed | []
KILLED edge return deleted | loop_ledger self-test: 2 failed
KILLED EDGE falsy | loop_ledger self-test: 2 failed
KILLED status all in_progress | loop_ledger self-test: 2 failed
KILLED event != pull_request | loop_ledger self-test: 2 failed | ['FAIL  NULL reds: a merge_group run reads the column unread, never a verdict of the push class', 'FAIL  NULL reds: a workflow_dispatch run ...']
KILLED headline product counts machinery | loop_ledger self-test: 1 failed | ['FAIL  reds: the summary counts a verdict red only where it reads red: an unread verdict is no red, and the product count ...']
KILLED headline product != GREEN | loop_ledger self-test: 1 failed | ['FAIL  reds: the summary counts a verdict red only where it reads red: ...']
KILLED headline machinery != GREEN | loop_ledger self-test: 1 failed | ['FAIL  reds: the summary counts a verdict red only where it reads red: ...']
KILLED unread count over rows | loop_ledger self-test: 1 failed | ["FAIL  reds: the summary's unread column counts the reds read, never a run with no job listing"]
KILLED row pair swapped | loop_ledger self-test: 3 failed
KILLED status class pr | loop_ledger self-test: 1 failed
KILLED status over all jobs | loop_ledger self-test: 1 failed
KILLED edge on head rows only | loop_ledger self-test: 2 failed
~~~

Each of the five fails under its swap and passes at the head. The swap was written and run first, then the check, so the check's failure under it is the failing case. The control's `0 failed` is the null.

Round 1 (the repair of 3fe03e1480), as recorded at ad36eefec0:

`python3 -I tools/audit/seat/loop_ledger.py --self-test` carries the proof in the tree: each `MUTANTS` row is one exact one-occurrence swap run on a copy of the file, and the self-test fails on a survivor or a needle that no longer occurs once above the table. Rows added by the repair, each with the check that fails under it and passes at the head:

- `gate job by name` (`_gates` reads every job): `reds: a failed job that is not `gate`, at an attempt whose gate did not fail, is no red`;
- `failed jobs failed` (the conclusion test dropped from the row's failed jobs): `reds: a job that did not fail at the red attempt is on neither list of its row`;
- `prelude and gate owed` (the two names dropped from `owed`): `reds: a failed prelude is a required failure, never a machinery job`;
- `main row's own spell` (a main row takes the head row's path): `reds: a main run red at an earlier attempt and unconcluded at its latest joins no red spell: uncleared, never the spell's pull request`;
- `edge spell` (the spell starts closed): `reds: a main red spell already open at the first main run read has no opener: ...`;
- `column class from the event` (every row graded as a push): `NULL reds: the same listing on a pull-request run reads the column unread, never a verdict of the push class`;
- `column member unconcluded` (a job with no conclusion passed as completed): `reds: a member with no conclusion, or not listed at the attempt, reads unread in its verdict, never red or green`.

Failing case first, items 2 and 3: with the checks written and the code at caa40bb294, `--self-test --no-mutants` printed `FAIL  reds: a main red spell already open at the first main run read has no opener: ...`, `FAIL  reds: the edge spell ends at the first green main run read, and the next red after it opens a spell`, then ended on `NameError: name 'NO_CLASS' is not defined` at the column's null check. Item 1's four checks pass at 3fe03e1480's code and fail under their swaps: the four `mutant killed` lines.

The reviewer's 28 swaps (`evidence/mut.py` of review/3696, unedited, run in place at `ad36eefec030b7e38c99c583a0da145795562d93`, the tree restored after):

~~~text
KILLED  is_cause: #n pattern dropped :: loop_ledger.py rc=1: FAIL  reds: a derived word the cause test refuses reads unread, never the word (+1 more)
KILLED  is_cause: CAUSES arm dropped :: loop_ledger.py rc=1: FAIL  a fully recorded roster reads every line (+11 more)
KILLED  is_cause: roster-group arm dropped :: loop_ledger.py rc=1: FAIL  is_cause: a pull request, external, original or another roster group; never the group itself or a bare word | roster_edit.py rc=1: FAIL set-fi ...
KILLED  is_cause: own-group refusal dropped :: loop_ledger.py rc=1: FAIL  is_cause: a pull request, external, original or another roster group; never the group itself or a bare word
SURVIVED convergence_why: is_cause call dropped
KILLED  fetch_runs: head_sha dropped :: round_metrics.py rc=1: FAIL producer: ci_runs.json keeps head_sha, event, head_branch and the first pull request's number
KILLED  fetch_runs: event dropped :: round_metrics.py rc=1: FAIL producer: ci_runs.json keeps head_sha, event, head_branch and the first pull request's number (+1 more)
KILLED  fetch_runs: head_branch dropped :: round_metrics.py rc=1: FAIL producer: ci_runs.json keeps head_sha, event, head_branch and the first pull request's number
KILLED  fetch_runs: pr always null :: round_metrics.py rc=1: FAIL producer: ci_runs.json keeps head_sha, event, head_branch and the first pull request's number
KILLED  fetch_runs: ci_runs.json written narrow :: round_metrics.py rc=1: FAIL producer: ci_runs.json keeps head_sha, event, head_branch and the first pull request's number (+1 more)
KILLED  green: latest attempt -> first :: loop_ledger.py rc=1: FAIL  reds: a main red with no later green and no red spell read reads uncleared, never unread (+1 more)
KILLED  green: non-failure latest reads red :: loop_ledger.py rc=1: FAIL  reds: a main red with no later green and no red spell read reads uncleared, never unread (+1 more)
KILLED  green: no-listing first-attempt success not green :: loop_ledger.py rc=1: FAIL  reds: a red inherited from main reads the pull request merged at main's first red push run after its last green, on the head ro ...
KILLED  mains: unread main runs kept out :: loop_ledger.py rc=1: FAIL  reds: a main red with no later green and no red spell read reads uncleared, never unread (+7 more)
KILLED  cause: main spell step removed :: loop_ledger.py rc=1: FAIL  reds: a red inherited from main reads the pull request merged at main's first red push run after its last green, on the head row and on both mai ( ...
KILLED  cause: subject unread -> uncleared :: loop_ledger.py rc=1: FAIL  reds: a merge subject naming no pull request reads unread: the row stays and the count is whole
STALE   cause: head row uses own opener, not main's last: needle occurs 2 time(s)
STALE   cause: main row takes head-row path: needle occurs 2 time(s)
KILLED  cause: no-pr head reads uncleared :: loop_ledger.py rc=1: FAIL  reds: a run on the branch main that is no push is a head row and opens no red spell (+2 more)
KILLED  rows: blind run dropped :: loop_ledger.py rc=1: FAIL  reds: the same run with no job listing reads unread, the count unread with it, and is never dropped (+2 more)
STALE   rows: gate job counted as failed job: needle occurs 2 time(s)
STALE   rows: failed = any conclusion: needle occurs 0 time(s)
STALE   owed: prelude and gate not owed: needle occurs 2 time(s)
KILLED  summary: main/heads counts swapped :: loop_ledger.py rc=1: FAIL  reds: a red and a later green run at one head_sha reads external (+4 more)
KILLED  summary: unread causes counted as caused :: loop_ledger.py rc=1: FAIL  reds: a main red spell already open at the first main run read has no opener: unread on the main row and on a head row after it, never t ...
KILLED  main(): --runs ignored :: loop_ledger.py rc=1: FAIL  reds: --runs prints the read after the roster reads; without it the read is unread
KILLED  _when: order by id alone :: loop_ledger.py rc=1: FAIL  reds: a green run before the red at its head_sha clears nothing: uncleared, never external (+1 more)
STALE   gate job name: needle occurs 2 time(s)
RESULT reviewer mutants: 28 drawn, 1 survived
~~~

`convergence_why: is_cause call dropped` is the row the verdict rules no survivor (the driver does not run `roster_lib.py --self-test`). Six needles are stale: five occur a second time in the `MUTANTS` table that now quotes them, and one line moved. The same seven swaps, applied once to the code above the table, with the unswapped control:

~~~text
PASSES  NULL control: no swap (loop_ledger.py) :: rc=0: loop_ledger self-test: 0 failed
PASSES  NULL control: no swap (roster_lib.py) :: rc=0: roster_lib self-test: 98 checks, 0 failed
KILLED  cause: head row uses own opener, not main's last :: rc=1: FAIL  reds: a red inherited from main reads the pull request merged at main's first red push run after its last green, on the head row and on both ma ...
KILLED  cause: main row takes head-row path :: rc=1: FAIL  reds: a main run red at an earlier attempt and unconcluded at its latest joins no red spell: uncleared, never the spell's pull request
KILLED  rows: gate job counted as failed job :: rc=1: FAIL  reds: a failed prelude is a required failure, never a machinery job (+1 more)
KILLED  rows: failed = any conclusion (needle moved: the line now reads `if j.get("conclusion") == "failure" and`) :: rc=1: FAIL  reds: a failed prelude is a required failure, never a machinery job (+1 more)
KILLED  owed: prelude and gate not owed :: rc=1: FAIL  reds: a failed prelude is a required failure, never a machinery job
KILLED  gate job name :: rc=1: FAIL  reds: a failed job that is not `gate`, at an attempt whose gate did not fail, is no red (+5 more)
KILLED  convergence_why: is_cause call dropped (under roster_lib.py --self-test) :: rc=1: TypeError: argument of type 'NoneType' is not a container or iterable
RESULT 7 swaps, 0 survived
~~~

The surviving predicates of the earlier rounds stay killed: the table's rows from 3fe03e1480 all print `mutant killed` (two needles were re-anchored to the lines they moved to: `failed jobs per attempt`, and the new `failed jobs failed`).

The reviewer's plants (`evidence/plants.py`, unedited) at `ad36eefec030b7e38c99c583a0da145795562d93`:

~~~text
## P1 window left edge: the first main run in the window is already red, no green before it (spell opener unobserved)
    gate_reds 2 (main 1, heads 1) caused {}; cause unread 2; uncleared 0; product red 0, machinery red 0 of 1 push reds (gate.status); product/machinery unread on 1 (gate.status takes an event class,
      red run 11 attempt 1 main dddddddddd cause unread (main red at the first main run read, no green main run read before it) found_by ci-main; required failed: none; machinery (report-only, never g
      red run 12 attempt 1 head aaaaaaaaaa cause unread (main red at the first main run read, no green main run read before it); required failed: none; machinery (report-only, never gating): no other
## P2 main red at attempts 1,2 then green at 3; a head red between
    gate_reds 3 (main 2, heads 1) caused {external: 2}; cause unread 0; uncleared 1; product red 0, machinery red 0 of 2 push reds (gate.status); product/machinery unread on 1 (gate.status takes an ev
      red run 11 attempt 1 main dddddddddd cause external (a later attempt of the run went green) found_by ci-main; required failed: none; machinery (report-only, never gating): no other job listed; p
      red run 11 attempt 2 main dddddddddd cause external (a later attempt of the run went green) found_by ci-main; required failed: none; machinery (report-only, never gating): no other job listed; p
      red run 12 attempt 1 head aaaaaaaaaa cause uncleared (no later green); required failed: none; machinery (report-only, never gating): no other job listed; product/machinery unread (gate.status ta
## P3 narrow rows (a ci_runs.json written before this PR: no head_sha/event/pr keys)
    gate_reds 1 (main 0, heads 1) caused {}; cause unread 1; uncleared 0; product red 0, machinery red 0 of 0 push reds (gate.status); product/machinery unread on 1 (gate.status takes an event class,
      red run 1 attempt 1 head - cause unread (no run at the head names a pull request); required failed: none; machinery (report-only, never gating): no other job listed; product/machinery unread (ga
## P4 listing at the latest attempt with no gate job, run concluded failure (e.g. prelude failed, gate never listed)
    gate_reds 0 (main 0, heads 0) caused {}; cause unread 0; uncleared 0; product red 0, machinery red 0 of 0 push reds (gate.status); product/machinery unread on 0 (gate.status takes an event class,
## P5 gate skipped/cancelled at the latest attempt on a head, run concluded cancelled
    gate_reds 0 (main 0, heads 0) caused {}; cause unread 0; uncleared 0; product red 0, machinery red 0 of 0 push reds (gate.status); product/machinery unread on 0 (gate.status takes an event class,
## P6 head red while main red; the PR's later commit green after main fixed (design: main's PR, not own)
    gate_reds 2 (main 1, heads 1) caused {#41: 2}; cause unread 0; uncleared 0; product red 0, machinery red 0 of 1 push reds (gate.status); product/machinery unread on 1 (gate.status takes an event c
      red run 11 attempt 1 main dddddddddd cause #41 (main red since run 11) found_by ci-main; required failed: none; machinery (report-only, never gating): no other job listed; product unread, machin
      red run 12 attempt 1 head aaaaaaaaaa cause #41 (main red since run 11); required failed: none; machinery (report-only, never gating): no other job listed; product/machinery unread (gate.status t
## P7 squash-merge subject on main's first red run
    gate_reds 1 (main 1, heads 0) caused {}; cause unread 1; uncleared 0; product red 0, machinery red 0 of 1 push reds (gate.status); product/machinery unread on 0 (gate.status takes an event class,
      red run 11 attempt 1 main dddddddddd cause unread (main red since run 11, whose subject names no pull request) found_by ci-main; required failed: none; machinery (report-only, never gating): no
## P8 a listing with jobs: null / malformed row
    RAISED TypeError 'NoneType' object is not iterable
## P9 a run row with pr as string
    gate_reds 1 (main 0, heads 1) caused {#5: 1}; cause unread 0; uncleared 0; product red 0, machinery red 0 of 0 push reds (gate.status); product/machinery unread on 1 (gate.status takes an event cl
      red run 1 attempt 1 head aaaaaaaaaa cause #5 (its later commit went green); required failed: none; machinery (report-only, never gating): no other job listed; product/machinery unread (gate.stat
~~~

P1 reads `unread` on both rows. P8 raises as it did at 3fe03e1480: `fetch_runs` writes `jobs` as a list on every listing it caches, and the verdict lists no block on it.

## Unpinned sites

The class the block's four instances belong to is a swap on an added line of the read that its self-test lets through. Its enumerator is `python3 -I tools/audit/seat/mutant_run.py --diff 38bf516bdd...HEAD --path tools/audit/seat/loop_ledger.py --cmd "sh -c 'python3 -I tools/audit/seat/loop_ledger.py --self-test --no-mutants >/dev/null'" --max-mutants 105 --report-only`: file order, so the draw covers every added line from `_when` through `main` and runs on into the self-test's own fixtures. It prints five survivors on the read's lines, each named by its text:

- `CONST_SWAP` `sys.path.insert(0, ci)` to `insert(1, ci)` in `_gate`: equivalent, `tools/ci` is the only path entry holding `gate`.
- `CMP_BOUND` `k > attempt and c == "success"` to `k >= attempt`: equivalent, the attempt's own conclusion is `failure`.
- `CMP_BOUND` `_when(m) <= _when(r)` to `<` in `before`: equivalent, `_when` ends in the run id and this arm is a head row's, never a main run's.
- `CMP_BOUND` `_when(x) > _when(r)` to `>=` in `later`: equivalent, the equal case is the red's own run, green only when a later attempt went green, and step 1 has returned by then.
- `RETURN_DEL` on `return self_test(not a.no_mutants)` in `main`: the swapped line is the measuring command's own exit status, so no check that command runs can read it; `main` then prints the roster report and returns 0. A value check outside the file would re-implement the exit.

Its other survivors are on fixture and `check(...)` lines of `_self_test_reds` (a deleted check, a fixture's run id), which are not the read.

`prepr.sh`'s own draw is the first 40 of the same list.

## Null control

- A green-only directory prints `gate_reds 0 (main 0, heads 0) caused {}; cause unread 0; uncleared 0; product red 0, machinery red 0 of 0 push reds (gate.status); product/machinery unread on 0 (...)` and no row. No `--runs` prints `gate_reds unread (no --runs directory)`; a directory with no `ci_runs.json` prints `gate_reds unread`. Each is a self-test check (`NULL reds: ...`).
- The column's null: the listing that reads `product red, machinery green` and `product green, machinery red` on a push run reads `unread` on a pull-request run (`NULL reds: the same listing on a pull-request run ...`).
- The edge spell's null: with a green main run read first, the same red main run reads `#41` on all three rows (`reds: a red inherited from main ...`), and after the edge spell's first green the next red opens a spell of its own.
- The mutant runners' null: the unswapped copy ends `0 failed` under the same command (`PASSES  NULL control` above; `mutant_run.py` refuses a run whose unedited command fails).
- The repair changes the text two existing checks pin, both the column's (`reds: a red attempt's failed jobs split ...` and `NULL reds: a green-only directory ...`), as block item 2 asks; no other check that was at 3fe03e1480 changed its expectation.

## Figures

<!-- figure-block: scope-line mb=8e76c192d269e0837a80d0606f3ac12ebecb223d head=2a374610679c6e56bf3f75a158e60741827451ec -->
~~~text
MODE: FULL -- every test script runs, nothing is scoped out.
~~~
<!-- /figure-block -->
- Self-tests at the head: `python3 -I tools/audit/seat/loop_ledger.py --self-test` ends `loop_ledger self-test: 0 failed`; its `ok` lines counted by `grep -c '^ok'`, the mutants among them by `grep -c '^ok    mutant killed'`. At ad36eefec0 (round 1's head; this repair changes none of these files, `git diff --name-only af0616cbe8 HEAD` prints `tools/audit/seat/loop_ledger.py` alone): `python3 -I tools/audit/seat/round_metrics.py --self-test` ends `round_metrics self-test: ok (with mutants)`; `python3 -I tools/audit/seat/scorecard.py --self-test` ends `ok (with mutants)`; `python3 -I tools/audit/seat/roster_edit.py --self-test`, `python3 -I tools/audit/seat/roster_lib.py --self-test` and `python3 -I tools/ci/gate.py --self-test` each end `0 failed`.
- `PYTHONPATH=tests/hastub python3 tests/entities.py` ended `ALL 2725 ENTITY CHECKS PASSED` at ad36eefec0; not re-run at this head, whose diff from af0616cbe8 adds no file.
- The column's function at the merge base: `git grep -n -E '^def status|^MACHINERY_JOBS' 38bf516bdd -- tools/ci/gate.py` prints both names.
- No live read was taken. The read's input is `round_metrics.py produce`'s directory, which this seat cannot fill: the session has no Actions API access. `python3 -I tools/audit/seat/loop_ledger.py --repo .` at the head ends `gate_reds unread (no --runs directory)`. The first live figure is the beat's, from `<state>/scorecard`.
- Part C's edge is open: `git ls-remote origin 'refs/heads/*token-ledger*'` prints nothing, and `git grep -c nested_memory origin/main -- tools` prints nothing.
- [d-hotfile-enumerator] at this merge base, origin's handoff refs fetched 2026-11-17: for each `refs/remotes/origin/handoff/*` ref with a merge base, `git diff --name-only <merge base> <ref>` filtered on `round_metrics|loop_ledger|roster_lib|tools/ci/gate.py` prints this topic's own ref and three more, `r11-pre-plan-render` 11e9a4e964, `r11-pre-round-check-gate-p2` 2cb653f2dd and `r11-pre-round-metrics-p2` e3f232aa84 (`roster_lib.py`; the last also `instruments/loop_ledger.py.md`); `git merge-tree --write-tree HEAD <ref>` exits 0 for each.
- `python3 tools/audit/archscore/score.py --diff 38bf516bdd HEAD` prints `Architecture score: dS +0.0000 NULL`. `python3 tests/structure.py` prints `STRUCTURE RATCHET PASSED` (re-run at 44a130aa4e).
- `python3 -I tools/ci/selftest_scope.py select --change M:tools/ci/gate.py` names `loop-ledger` at the head. The repair changes no closure file: `git diff 3fe03e1480 HEAD --name-only` prints `tools/audit/seat/loop_ledger.py` and `tools/audit/seat/instruments/loop_ledger.py.md`.
- No file is added, so nothing new is classified; no golden moves and neither claim file is touched.

## Red checks

- None owed. `merge_train.py classify af0616cbe8dbd95e9a0ccb1e8822949f579a7cba --pr 3696` printed `GREEN ... pending: none red: none` at the reviewed head (review/3696 `evidence/classify_last.txt`). This repair changes only the self-test half of `loop_ledger.py`.

## Forward-carry

- Carry 0 (part D built in this handoff, with the verdict's notes runs-json-width, d-hotfile-enumerator and branch-reuse and the design note's [d-p2-head]; part C not built): part C of the approved design is unbuilt (the load count per rule, an instrument's refusal with its outcome, a run line per workflow script), with the design note's fixer notes [paths], [P1] and [c-deferred]: the orchestrator dispatches it once R11-PRE-TOKEN-LEDGER is on main with an importable per-session iterator that also yields each session's subagent transcript files. [paths] is owed with it: E11-N-GATE-CAUSE's `paths` in `dev/audit/yardstick/round11/EVALUATION.json` become `tools/audit/seat/roster_lib.py`, `tools/audit/seat/loop_ledger.py` and `tools/audit/seat/round_metrics.py` in place of `tools/ci/gate.py`, plus C's file, written before the card is recorded merged; this pull request does not write them, because the card is whole only with C's run line. Lands in R11-PRE-TOKEN-LEDGER's row of the round-11 roster on handoff/audit-r10-roster, the group whose merge opens part C; this group's own row is at stage carries-open and takes no carry. Carry: R11-PRE-TOKEN-LEDGER
- Item d-toolchain-p2-column, re-written (it replaces the text of item 6889317b on R11-PRE-PARALLEL-PIPELINE's row, whose precondition, `gate.status` on main, is met): `loop_ledger.gate_reds` applies `gate.status` under class `push` to a push run's red attempt and prints `product/machinery unread` on every other row, because `status` takes an event class (`push`, `no-pr`, `pr`, `pr-cc`) and neither `pr` against `pr-cc` (`gate.reaches_custom_components`, a three-dot diff of the pull request's head) nor `no-pr` against `pr` is derivable from a cached run row. Whoever grades the other rows first caches the class per run in `round_metrics.fetch_runs`, then widens the one expression that reads `r.get("event") == "push"`; the departure raised for it awaits the orchestrator's ruling. Control: the self-test check `NULL reds: the same listing on a pull-request run reads the column unread, never a verdict of the push class` pins today's text and fails when a non-push row takes a verdict, and the `MUTANTS` row `column class from the event` is its mutant. Lands in R11-INTAKE-R10-RESIDUE's row of the round-11 roster on handoff/audit-r10-roster: R11-PRE-PARALLEL-PIPELINE, the group that holds `tools/ci/gate.py`, reads `done` there and takes no carry. Carry: R11-INTAKE-R10-RESIDUE
- The six departures above were accepted by the orchestrator under mandate 6893738184 (refs/heads/inbox/r11-pre-no-read-builders 6aeb520723, INBOX line 1); lands in R11-INTAKE-R10-RESIDUE's row of the round-11 roster on handoff/audit-r10-roster, R11-PRE-PARALLEL-PIPELINE reading `done` there, the surface being `tools/audit/seat/loop_ledger.py`. Carry: R11-INTAKE-R10-RESIDUE
- A limit of the design's rule, measured by reading `.github/workflows/ci.yml`'s triggers: a `pull_request` `edited` or `labeled` event and a `pull_request_review` event each start a run at the unchanged `head_sha`, so a red cleared by a body edit or a review at the same head reads `external`, as a re-run does. The instrument page says so. Splitting the two needs the run's kind, which the run listing the producer caches does not keep (it is in the run's `display_title`). Lands in R11-INTAKE-R10-RESIDUE's row of the round-11 roster on handoff/audit-r10-roster: R11-PRE-PARALLEL-PIPELINE, the group that holds `tools/ci/gate.py`, reads `done` there and takes no carry. Carry: R11-INTAKE-R10-RESIDUE

## Friction

- gate-scoping.md: cost: `python3 -I tools/ci/selftest_scope.py record --step loop-ledger` rewrote six steps it was not asked to record (`open-pr`, `policy-lint-mutants`, `pr-args`, `push-names-the-host`, `temp-or-machine-path`, `update-pr`), deleting ignore entries; the wanted step was copied out by hand. The second sighting in this group: #3683's body records the same for `--step review-strength-enumerator`. Carry: dismissed: no live roster group owns `tools/ci/selftest_scope.py`; left for the round-end proposal triage


