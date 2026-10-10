# R9-ROW-STALE: a row's status is part of what it records, so a merged pull request stops rowing `open`

`tools/audit/seat/record_row.py --plan` asked one question of a row that
already exists -- "is there a row at all" (`has_row`, answered on the row's
**anchor** plus prose mentions) -- and never asked what the row **says**. A
pre-merge row therefore satisfied the plan forever: `-- **open**, <title>`,
the shape `tools/audit/seat/open_pr.sh`, `tools/audit/seat/handoff_push.sh` and
this module's own `self_row` all write, anchors its number, so the merged form
`row_line()` produces (`-- **merged `<sha>`**, ...`) was never recorded.

**The count, its rule, and the tip it was taken at.** Rule: every
`dev/programme/delivery/<N>.md` whose single line is anchored on `<N>` and
carries `**open**`; each then confirmed against the REST API
(`gh api repos/tvofi/heatpump_optimizer/pulls/<N>`, `.merged`). At this head's
merge base (`7cd5a588c`, `origin/main`'s tip): **103 rows read `open` for
pulled requests GitHub reports MERGED -- 103 queried, 0 errors, 0 genuinely
open, 0 closed-unmerged, all into `main`**; 26 of them at `N >= 2040`, 77
below; merge times `2026-10-02T14:49:58Z` to `2026-10-10T06:38:11Z`. The figure
is a function of `main`'s tip, so the earlier reading is recorded rather than
overwritten: at `23d354970` (the base I first measured at) the same rule gave
**100** rows, 24 of them at `N >= 2040`. A row that reads `open` for a `main`
merge is the defect; a row that reads `open` for a genuinely open pull request
is correct, and there were none of those in the set.

Why it matters beyond tidiness: `tools/release/stamp.py --require-rows` stands
on `tests/delivery_status.py`, whose ledger asks `mentions()` -- existence, not
status (`tests/delivery_status.py:379`) -- so a row reading `open` for a merged
pull request **clears the bar that exists to guarantee the record is written**,
and the record is what seats and the owner read.

**One correction to the roster brief, measured.** The brief attributes the
false status to `plan_table.py` and `state_docs.py` generating PLAN-TABLE and
RESUME-CURRENT "from those rows". They do not read the rows' status: both key
on the roster's own `resume.stage` through `roster_lib.open_groups` /
`roster_lib.is_open` (`grep -n 'def is_open' -A 2 tools/audit/seat/roster_lib.py`
reads `resume.stage`, not a row), so a group at `stage: done` cannot be made
open by a row at all. The consumer that reads the status is the record itself:
a seat, the owner, and the orchestrator's status answers. The defect is real
and the blast radius is the record, not the generated tables.

The fix, in one sentence: a second predicate, `row_matches_merge`, is asked
**beside** `has_row` -- never inside it, because `has_row` is the question the
beat's own `self_row` and every pre-merge row need -- and it says whether the
row that exists already tells the merge the plan attests. `--plan` drops a merge
only when the row exists and matches; otherwise it plans a rewrite. Three
things decide whether a row may be rewritten, and each has an arm:

- **The status, not the title.** `_rewrite_granted` rewrites exactly when the
  file's recorded status differs from the status the plan attests, and the plan
  records a merge. A row that already says the same thing is left byte-identical
  even when a sibling instrument titled it differently, and a merged row is never
  reverted to `open` by the beat writing its own self-row.
- **The grant's boundary.** Only a single line in one of the two status shapes a
  row writer emits is the generator's to touch. A seat's multi-line disposition,
  and the pre-2026-10 style that carries facts *inside* the bold
  (`**merged `e602e65`, 2026-09-16 13:09Z, by `tvofi`; roster owed**`), read
  `None` and are left alone -- the plan was stale, the tree won, exactly as
  before this change. Census over the 502 numeric row files at this head: 248
  in-grant `**merged `sha`**`, 103 in-grant `**open**`, 151 outside the grant
  (15 multi-line, 136 prose-status).
- **The merge, not merely the pull request.** A pull request the API still
  reports OPEN attests no merge **whatever sha its entry carries** -- GitHub
  fills `merge_commit_sha` for an open request too, as the test-merge commit --
  so `plan_merges` asks the state first. This is the difference between a stale
  row and a row that is simply early, and it is the first planted control.

`row_line()`'s grammar is untouched, so the readers are unchanged: the
rewritten rows still parse under `policy_lint --record`, still answer
`delivery_status.mentions()`, and stay one line each. The write set is
untouched too: `dev/programme/delivery/<N>.md` only, never the plan of record's
Delivery-status table and never `dev/programme/HANDOVER.md` (issue #1952,
owner-approved 2026-10-04). The anchor key inside `write_rows` moves from the
entry's `number` field to the **file's** number -- the same key
`automerge_refusals` reads a diff by -- because a rewrite is aimed at a file,
and an entry naming one pull request while pathing another must not point a
status rewrite at a row it does not describe.

## Head

`ce70213ae` -- `origin/main` (`7cd5a588c`) merged into the lane, and every
figure below re-taken at that merge. History: failing arms first at `a3b7cee9f`
(7 checks red, production unchanged), the fix at `916fa99df`, the grant's
direction arm at `76b867b94`, the carry note at `ec03a7c26`.

## Mutation proof

Eleven mutants, one at a time, each restored (`git checkout --` after each; the
driver is `/Users/timmalmstrom/hpo-seats/row-stale/mutants.py`, its output
`/Users/timmalmstrom/hpo-seats/row-stale/mutations.txt`, which ends `restored
self-test: rc=0`). Every mutant is a **clause of the fix**, not a tail: the
anchors are the condition in `plan_merges`, the return of `_rewrite_granted`,
the comparison in `row_matches_merge`, the grant checks in `recorded_row_status`,
the status regex, and the number key in `write_rows`. None survived (`rc=0`
would print `!! SURVIVED`).

- **M0, the null control, unmutated**: `record_row self-test: all checks
  passed` (`rc=0`).
- **M1 `plan_merges` back to `has_row` alone (the defect itself)**: `rc=1`, 9
  failed -- the stale row is planned, its line is `row_line`'s byte for byte,
  apply rewrites it, the row reads merged at the API's sha, the wrong-sha row is
  corrected, the group suffix survives, and both predicate arms.
- **M2 the `state == "open"` clause dropped**: `rc=1`, 1 failed -- exactly
  `control A: an open pull request with an open row is untouched`. This is
  control A's perturbation.
- **M3 `_rewrite_granted` → `return False`**: `rc=1`, 6 failed -- apply never
  rewrites.
- **M4 the grant's `now`/`want` boundary dropped**: `rc=1`, 3 failed -- the
  multi-line seat disposition and the prose-status row come into the grant.
- **M4a the grant's direction dropped (`want[0] == "merged"` gone)**: `rc=1`, 1
  failed -- `a merged row is never rewritten back to open`. Before this arm
  existed the mutant **survived**; it is why the arm is in the tree.
- **M5 `row_matches_merge` ignores the sha**: `rc=1`, 2 failed -- no correction.
- **M6 the one-line grant boundary dropped**: `rc=1`, 1 failed -- a seat's
  multi-line disposition becomes rewritable.
- **M7 the status regex loosened to accept facts inside the bold**: `rc=1`, 1
  failed -- the pre-2026-10 hand style becomes rewritable.
- **M8 the anchor key back to the entry's `number` field**: `rc=1`, 1 failed --
  `a rewrite aimed at another row's file is refused`.
- **M9 `has_row` dropped from the guard**: `rc=1`, 9 failed, including
  `control B: a merge with no row still plans and writes a row`. This is control
  B's perturbation.
- **M10 the grant keyed on text, not status**: `rc=1`, 4 failed, including
  `an open row is never rewritten toward another open row's title`.

## Null control

Unmodified tree at the merge base: `record_row self-test: all checks passed`,
and the live corpus -- 103 rows read `**open**` for pull requests the API
reports MERGED (rule and command above; every row confirmed, 0 errors). The
defect is the tree's own state at this base, not a synthetic fixture.

The failing-first commit `a3b7cee9f` carries the arms and none of the fix:
`7 self-test check(s) failed` -- exactly the seven stale/rewrite arms, with both
planted controls and both grant-boundary arms **green** at that tree. A control
that was red before the fix would be measuring the wrong thing.

The two planted controls, and what makes each one able to fail:

- **A genuinely open pull request with an `open` row stays untouched.** The arm
  is not vacuous because it is paired with the predicate: `row_matches_merge`
  **does** read that row stale (`rc: False`), so what holds the plan is
  `plan_merges`'s `state == "open"` clause alone -- and M2, which deletes that
  clause, reddens the arm (1 failed, named above).
- **A pull request with no row at all still gets its row**, both paths: a merged
  entry with no row still plans and writes `row_line`'s merged row, and the
  pre-merge beat still gets `**open**` from `self_row` (what `--write-self-row`
  calls). Its perturbation is M9: with `has_row` dropped from the guard a
  rowless merge is skipped, and the arm that names it goes red. The wide corpus
  below carries two such rowless merges of its own (1885, 1890), so the path is
  exercised on real data too.

The live corpus, at a clean worktree of `origin/main` (`7cd5a588c`), with
`--enumerate` from main's own instrument (the enumerator is unchanged by this
fix) and `--plan`/`--apply` from this head:

- `--since v6.7.13` (the window that covers all 103 stale rows; the last tag is
  `v6.7.17`, and the oldest merge in the set predates it): **161 merges
  enumerated**, `--plan` → **105 rows: 103 rewrites + 2 new** (1885, 1890 --
  merges with no row at all, the path this change leaves alone), `--apply` →
  `git diff --stat` → `103 files changed, 103 insertions(+), 103 deletions(-)`
  (one line each, none truncated) plus those 2 files created. Re-plan → **0
  rows**: idempotent on the real corpus. The 103 rewrites are exactly the 103
  rows the API confirmation above found stale -- no more, no fewer, which is the
  cross-check that the predicate fires on the defect and nothing else.
- After that apply, `grep -l '**open**' dev/programme/delivery/*.md` prints
  nothing at all: **0** rows read `**open**` (and 0 of them at `N >= 2040`), so
  every row that remains is correct rather than merely unchecked.
- The live beat's own window, `v6.7.17..HEAD`: **18 merges, all 18 planned as
  rewrites** -- so the next beat after this merges carries 18 status
  corrections.

The rewritten rows still read as records, driven through the readers the brief
names over that corpus: `policy_lint --record --since v6.7.13` → `TOTAL: 0
error(s) over 161 merged pull request(s)`; `tests/delivery_status.py` →
`DELIVERY STATUS OK — 18 rowed, 0 pending, 0 overdue`; `--require-rows --since
v6.7.13` exits 0 (152 rowed, 0 pending, the record-class merges named exempt);
`delivery_status.mentions()` and `anchored()` read the rewritten rows. A sample
diff, from the corpus run, is the whole change:

    -[#2078](.../pull/2078) — **open**, fix(R9-RO-13): the train may land policy ...
    +[#2078](.../pull/2078) — **merged `23d3549`**, fix(R9-RO-13): the train may land policy ...

The corpus worktree was removed with `git worktree remove`; **no row is written
by this branch**. This pull request is the tool and its arms, which is also why
its own diff is one file.

## Figures

- `head self-test: record_row self-test: all checks passed`, `97` checks
  executed -- `python3 -I tools/audit/seat/record_row.py --self-test`, with the
  executed count taken by instrumenting the closure in a scratch copy at the
  same path (97 `ok()` calls ran; the `--self-test` line alone carries no
  count).
- `failing-first a3b7cee9f: 7 self-test check(s) failed`, the seven new arms --
  same command at that commit (`git show a3b7cee9f:tools/audit/seat/record_row.py`).
- mutation tallies `M0 rc=0` and `M1..M10 rc=1`, no survivor -- `python3 -I
  /Users/timmalmstrom/hpo-seats/row-stale/mutants.py`.
- `103` rows read `open` for merged pull requests at `7cd5a588c`, `100` at
  `23d354970` -- single-line anchored row files carrying `**open**` under
  `dev/programme/delivery/`, then `gh api
  repos/tvofi/heatpump_optimizer/pulls/<N> --jq .merged` per row.
- corpus at `7cd5a588c`: `161` merges, `105` planned (`103` rewrites + `2` new),
  `103 files changed, 103 insertions(+), 103 deletions(-)`, re-plan `0`, `0`
  rows reading `open` after apply -- `python3 -I tools/audit/seat/record_row.py
  --enumerate --since v6.7.13`, then `--plan` and `--apply` with `--root` at
  that worktree.
- live beat window: `18` merges, `18` rewrites -- the same enumeration filtered
  to the `v6.7.17..HEAD` first-parent log.
- readers over the corrected corpus: `TOTAL: 0 error(s) over 161 merged pull
  request(s)` -- `node tools/policy/policy_lint.mjs --record --since v6.7.13`;
  `DELIVERY STATUS OK — 18 rowed, 0 pending, 0 overdue` -- `python3 -I
  tests/delivery_status.py`.
- grant-boundary census at this head: `502` numeric row files -- `248` in-grant
  `**merged `sha`**`, `103` in-grant `**open**`, `151` outside the grant (`15`
  multi-line, `136` prose-status) -- the production `record_row.line_status`
  read over `dev/programme/delivery/*.md`.
- scoped gate: `MODE: SCOPED -- 1 script(s) run, 32 scoped out; changed files
  (1): tools/audit/seat/record_row.py; RUN tests/entities.py` -- `D=$(mktemp -d);
  python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)
  --workdir $D; cat $D/scope.txt`.
- `PYTHONPATH=tests/hastub GOLDEN_MODE=drift GOLDEN_REF=$(git merge-base
  origin/main HEAD) python3 tests/entities.py` -- the scoped gate's one script,
  `ALL 2250 ENTITY CHECKS PASSED` at the merged head `ce70213ae`, its check
  `tools/audit/seat/record_row.py --self-test passes` among them.
- run_always lines: `claims hygiene: 7cd5a588cbbbef354c00148040da2d720b8a888c
  ok` -- `PYTHONPATH=tests/hastub python3 tests/env_drift.py --claims-only
  $(git merge-base origin/main HEAD)`; `ALL 57 closure shrink pins PASSED` --
  `python3 tests/closure.py selftest`; `layout self-test: ok` -- `python3
  tests/layout.py`; `tests/harness_headers.py` reports `12 of 109 HARNESS
  HEADER CHECKS FAILED` at the merged head `ce70213ae`, and its scope is
  `dev/audit/rounds/round*/D*/*.py` and `dev/audit/harnesses/**`, none of which
  this one-file diff touches, so no head of this branch can move it.
- `STRUCTURE RATCHET PASSED`, no metric moved -- `python3 tests/structure.py`.
- `Architecture score: +0.0000` -- `python3 tools/audit/archscore/score.py
  --diff $(git merge-base origin/main HEAD)`.
- both claim files byte-identical to the merge base (this branch claims no
  drift) -- `git diff --name-only $(git merge-base origin/main HEAD)...HEAD`
  lists exactly `tools/audit/seat/record_row.py`, and the same three-dot diff
  carries no `VERSION`, manifest, `RELEASE_NOTES.md` or budget file.
- `tools/audit/seat/record_row.py` is not in the policy corpus -- `printf
  'tools/audit/seat/record_row.py\n' | node tools/policy/policy_lint.mjs
  --corpus-filter` prints nothing; and `.github/CODEOWNERS` names
  `/tools/audit/briefs/`, `/tools/release/` and `/tools/policy/budget_raise_gate.py`,
  not `/tools/audit/seat/`, so this path is not code-owned.
- the automerge guard on a rewrite -- `python3 -I` driving
  `record_row.automerge_refusals` at this head: the same generated line answers
  `[]` as `status: added` and `['dev/programme/delivery/2078.md: not a new file
  adding exactly one line (status modified, -1)']` as `status: modified`.
- `PREPR2 rc=0` at this head -- `closures: scoped recordings are covered`,
  `PR-BODY: 0 error(s)`, `FIGURES: 17 resolved, 5 not verified, 0 refused`,
  `unpinned sites: the diff adds no unpinned mutation site` -- `bash
  tools/pr/prepr.sh BODY.md`.

## Red checks

none. No check went red on this branch: the self-test is green at every commit
except the deliberate failing-first `a3b7cee9f` (arms only), the mutants are
named as restored probes rather than branch state, and the scoped gate's one
script, the structure ratchet and the `run_always` lines are green at the head,
except `harness_headers`, which reports 12 of 109 red at the merged head and
whose scope (`dev/audit/rounds/round*/D*/*.py`, `dev/audit/harnesses/**`) this
one-file diff does not reach -- so it is `main`'s red, not this branch's, and
no commit here can move it.

`prepr.sh` returned **rc=0** at this head. Its closures step refused on the
first attempt -- it re-records `tests/entities.py` by executing it, and that
recording run exited 1 (`REFUSE closures -- failed while being recorded:
tests/entities.py (exit 1)`); the recorded script is green at the same head
(`ALL 2250 ENTITY CHECKS PASSED`, rc=0, run plainly with
`PYTHONPATH=tests/hastub`), the same recording step passed at this lane's
pre-merge head `ec03a7c26` with the identical `record_row.py`, and machine load
was 182 with ~15 sibling seats on the box -- so that exit was the recording
execution under load, not a red check, and the second run cleared it
(`closures: scoped recordings are covered`). **Cheaper detector: none** -- the
recording is the gate itself, and CI runs it on the PR head. No check was
weakened: nothing in this diff touches `tests/entities.py`, the closures or the
recordings.

The root-cause trigger the brief asks me to name, though the rule attaches it to
a released defect or a red check and neither holds here: the **process state is
(c)** -- the process existed, was followed, and did not produce the intended
result. `record-autofix` ran on every push to `main` for the whole window, with
the API facts in hand, and could not converge, because the predicate it asks
(`has_row`) answers a different question ("is there a row at all") than the
record's truth ("does the row match the merge"). It is not (b): nobody skipped a
step -- the beat behaved exactly as written, and `--apply`'s "an existing file is
left alone" clause refused the correction even when a row was planned.

**The cheaper detector, and its standing cost.** There is no existing detector
that could have caught this, and the fix is where the cheap one belongs. The
`record` and `delivery-status` checks stand on `delivery_status.classify`, which
asks `mentions()` -- existence -- and `stamp.py`'s `--require-rows` gate reads
that ledger deliberately token-free, from git alone (`stamp.py:1560-1574`), so a
status-aware check there would have to acquire the API and a token it
deliberately does not have. The place that already holds the merge facts, at
zero extra API calls, is `--plan`, and the countermeasure is the fix itself: the
status is read from the row file (a local read) and compared against the
`merge_sha` `--enumerate` already fetched. Cost: one row-file read per
enumerated merge, no network. The **root-cause seat rides beside this lane**
(per the brief), so this is the named cause, state and countermeasure-in-place,
not an RCA.

## Forward-carry

Two findings change what a later stage must do, both measured.

1. **A status rewrite is a modified file, so the automerge guard refuses the
   beat that carries one.** The guard requires `status: added` (measured above:
   the identical line passes as `added`, is refused as `modified`), so the next
   record beat -- 18 rewrites by the live window -- does **not** auto-merge and
   is reviewed and merged by hand. That is the fallback the guard's own
   paragraph already describes for a refusal, so no assumption is invalidated;
   what is new is that the *ordinary* beat now takes it. **Destination**:
   `tools/audit/seat/record_row.py`'s module docstring, beside `THE REVIEW IS A
   PREDICATE` -- the file the next reader of this lane opens -- with the
   measured pair of guard answers. Widening the guard to auto-merge a content
   change to the record is the owner's decision and is **not** taken here.
2. **The beat's reach is its window.** `--enumerate` reads
   `<last tag>..HEAD`, so a beat corrects only the merges its tag window covers:
   measured, the live `v6.7.17` window plans 18 rewrites while a run from
   `v6.7.13` plans all 103. The other 85 are corrected by no automatic run --
   the tag has already moved past them, and the beat always starts at the tag --
   so they need a seat to run `--since` back to `v6.7.13` (or a future window
   that reaches them). No live roster group receives this -- every `R9-FR*`
   group on `handoff/audit-r9-fixplan` is `resume.stage: done`, and a carry file
   needs a destination issue a fixer does not file -- so it is recorded for
   whichever seat next does record upkeep (`delivery-status-tracking.md` item 1):
   the fix converges the record inside the window it is run over, and nothing
   widens that window on its own.

## Friction

- `finding-propagation: stale: the roster brief attributes the false rows to plan_table.py and state_docs.py "generating PLAN-TABLE and RESUME-CURRENT from those rows"; both key on the roster's resume.stage (roster_lib.is_open), so the correction is recorded in this body rather than repeated in a later seat's brief.`

## Approval

Opened by the hpo-author App. `tools/audit/seat/record_row.py` is not a
code-owned path (`.github/CODEOWNERS` names `/tools/audit/briefs/`,
`/tools/release/`, `/tools/policy/budget_raise_gate.py`, `/tools/pr/contract_rerun.py`,
`/tools/audit/merge_fastpath.py`, `/tools/audit/fold_ledger.py` -- not
`/tools/audit/seat/`) and not in the policy corpus (`policy_lint --corpus-filter`
prints nothing for it), so no `## Approval` is owed by either rule; the
approver App reviews it as the record lane's own instrument. The write set,
`row_line`'s grammar and the automerge guard are all left as they were.
