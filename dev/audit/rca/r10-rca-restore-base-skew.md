# R10-RCA-RESTORE-BASE-SKEW: a check-source restore pinned to the payload's base mixes two mains

Root-cause seat (`dev/governance/roles/root-cause.md`,
`dev/governance/rules/defect-root-cause.md`) beside R10-HOTFIX-RESTORE-BASE-SKEW,
never inside it: this document edits no workflow and no test. Trigger: the
red-check trigger, `pr-contract` red on PR 3424 at `f9c7952b` (run 42953123178,
job 130312858296). Measured at `origin/main` `dbd1ab5b07` on 2026-11-11 05:05Z;
sections 3 to 5 re-taken at `49462e86f3` (main `a7628041dc`) on 2026-11-11 07:18Z;
the line numbers of section 3 are that commit's.
The ruling is `dev/programme/triage/s6-batch160.md#P572` at roster `b91ac890cf`
on `origin/handoff/audit-r10-roster`, not yet on main.

## 1. The cause, reproduced

Job 130312858296's step "Every finding the body records names its destination"
died with `AttributeError: module 'roster_lib' has no attribute
'carry_receivable'` from `carry_audit.py`'s `Dests.live`.

- The job checked out GitHub's merge commit `427c4ca874`, whose parents are
  `c620ebba96` (main at 03:29:26Z) and the head `f9c7952b`
  (`git log -1 --format='%P' 427c4ca8`).
- `pr-contract.yml`'s step "Restore the check source from the base commit" takes
  `PINNED` from `github.event.pull_request.base.sha`, which in this run's
  payload was `d08ed31049`: 53 commits (19 merges) behind the merge commit's
  first parent (`git rev-list --count d08ed31049..c620ebba96`, `--merges`).
- `roster_lib.py` is in the restore pathspec; `carry_audit.py` is not
  (`tools/audit/*.py` is absent from it). `carry_receivable` was added to
  `roster_lib.py` by `e08425e904` (2026-11-10), with its caller in
  `carry_audit.py`. `git merge-base --is-ancestor e08425e904 d08ed31049` is
  false; against `c620ebba96` it is true.
- So the job ran a caller from one main against a callee from an older main.

Reproduction, independent of the fixer's harness: in a detached worktree at
`427c4ca8`, `git checkout <src> -- tools/audit/seat/roster_lib.py` then
`python3 -I -c "import sys; sys.path.insert(0,'tools/audit/seat'); import roster_lib; print(hasattr(roster_lib,'carry_receivable'))"`
prints `False` for `src=d08ed31049` and `True` for `src=c620ebba96` (the null
control); `git show 427c4ca8:tools/audit/carry_audit.py | grep -c 'roster_lib.carry_receivable'`
prints 2. `427c4ca8` is no longer fetchable (`refs/pull/3424/merge` has moved);
re-run at its first parent `c620ebba96` (the head touches neither file), the same
three commands print `False`, `True` and 2. The full step, replayed with the hotfix's own instrument
(`dev/audit/harnesses/r10_restore_base_skew.py` at
`handoff-wip/r10-hotfix-restore-base-skew` `5ab1c861c8`):
`--source d08ed31049…` prints `RESULT exit=1`, `RESULT attributeerror=True`;
`--source c620ebba96…` prints `RESULT exit=0`, `RESULT attributeerror=False`.

**Which side moved.** Neither file is wrong; the restore source is. Run 42953123178
was attempt 2 of the run: a re-run keeps both `GITHUB_SHA` and the payload, so it
reproduced the red, and only a new event at a moved head refreshes `base.sha`.

**What `base.sha` is.** Not the commit the merge ref is built on. This document
relies only on the measured inequality with the merge commit's first parent
above, not on a model of when GitHub sets the field.

## 2. Process state: (c), the process was followed and did not produce the intended result

The process: a census in `tests/entities.py`, landed by `e55be57447`
(2026-10-23, R10-CI-LAYOUT-P2), enumerates every `PINNED` restore in a
gate-required job and asserts, under the check named
"and on a pull_request and a push every such restore reads the event's own commit",
that on a pull_request each expression evaluates to the payload's `BASESHA`.
An older pin from `46a6ac4d68` (2026-09-22), "`policy-docs` restores its graders
from the base commit before it grades", requires the literal
`github.event.pull_request.base.sha` in the step.

Both pass at `49462e86f3`, a tree whose `pr-contract.yml` still restores from
the payload base (`PYTHONPATH=tests/hastub python3 tests/entities.py`, the two
check names above in its `ok` lines). Their unit is the
expression's value, "the payload's base"; the property the restore exists for is
"the restored files and the unrestored ones come from one tree", which the
census never reads. Its target was the head (a PR grading itself), and it took
the payload base as the base by construction. Its units were also
`governance.yml` and `tests.yml` only (`grep -n '^_BP_UNITS = ' tests/entities.py`
prints `{"governance.yml": "governance", "tests.yml": "tests"}`), so this instance, in
`pr-contract.yml`, was outside it.

Not (b): no rule asked for the first parent and was ignored. Not (d): no
precondition changed underneath it; `base.sha` was never the merge commit's
parent by contract, and the skew existed from the first restore. What grew is
exposure (section 4), not the defect.

## 3. How far the class reaches

Rule: `grep -n 'PINNED:.*base.sha\|PINNED=.*base' .github/workflows/*.yml`
returns 22 sites at `dbd1ab5b07` and at `49462e86f3` (`grep -c`, per file): `budget-raise-gate.yml` 1, `ci.yml` 6,
`codeql.yml` 2, `governance.yml` 6, `pr-contract.yml` 1, `tests.yml` 6. Each
restores a subset of paths into a merge-ref checkout, so each mixes two trees
whenever the payload base lags. Disposition: all 22 are
R10-HOTFIX-RESTORE-BASE-SKEW's seam, whose brief says every restore; its WIP
census (`_rbs_defects`) reads every `.github/workflows/*.yml` and plants a
payload-base read into `pr-contract.yml` as a control, so the unit gap of
section 2 is closed there. `grep -n 'merge-base FETCH_HEAD HEAD' .github/workflows/*.yml`
returns one line, the batch arm `ci.yml:117`
(`PINNED=$(git merge-base FETCH_HEAD HEAD)`), which is not a payload read.

Other `base.sha` reads. Rule, at `49462e86f3`:
`grep -n 'github.event.pull_request.base.sha' .github/workflows/*.yml | grep -v 'PINNED:.*base.sha\|PINNED=.*base'`
returns these 11 lines:

```
$ grep -n 'github.event.pull_request.base.sha' .github/workflows/*.yml | grep -v 'PINNED:.*base.sha\|PINNED=.*base'
.github/workflows/arch-score.yml:63: EVENT_BASE: ${{ github.event.pull_request.base.sha || github.event.merge_group.base_sha }}
.github/workflows/budget-raise-gate.yml:96: PR_BASE: ${{ github.event.pull_request.base.sha || github.event.merge_group.base_sha }}
.github/workflows/ci.yml:130: BASE_SHA: ${{ github.event.pull_request.base.sha }}
.github/workflows/dependabot-automerge.yml:69: ref: ${{ github.event.pull_request.base.sha }}
.github/workflows/governance.yml:213: MACHINERY_BASE: ${{ github.event.pull_request.base.sha || (inputs.base && format('origin/{0}', inputs.base)) || '' }}
.github/workflows/governance.yml:246: SINCE: ${{ github.event.pull_request.base.sha || github.event.merge_group.base_sha || github.event.before }}
.github/workflows/pr-contract.yml:159: PAYLOAD_BASE: ${{ github.event.pull_request.base.sha }}
.github/workflows/tests.yml:1180: PR_BASE: ${{ github.event.pull_request.base.sha }}
.github/workflows/tests.yml:1501: BASE: ${{ github.event.pull_request.base.sha }}
.github/workflows/tests.yml:1896: BASE="${{ github.event.pull_request.base.sha || github.event.merge_group.base_sha }}"
.github/workflows/tests.yml:2104: BASE="${{ github.event.pull_request.base.sha || github.event.merge_group.base_sha }}"
```

The table below dispositions each. Ruling P572 ("Do not change
the diff bases", `dev/programme/triage/s6-batch160.md` at roster `b91ac890cf`)
classes `BASE_SHA`, `SINCE`, `PR_BASE`, `MACHINERY_BASE`, `PAYLOAD_BASE` and
`tests.yml`'s `BASE` as keys of the pull request's own diff, not restore sources;
the consumer named per line is what was read to confirm it.

| read | variable | consumer | disposition |
|---|---|---|---|
| `arch-score.yml:63` | `EVENT_BASE` | step output `base` | not this class: scorer and both trees read whole from git |
| `budget-raise-gate.yml:96` | `PR_BASE` | `budget_raise_gate.py --base`: `git show` of budget JSON, `merge-base`, and the scorer run inside a detached worktree of the base, a whole tree | diff key, P572 |
| `ci.yml:130` | `BASE_SHA` | `codeql_scope.py changed --base` (`git diff`) | diff key, P572 |
| `dependabot-automerge.yml:69` | `ref` | a whole checkout of the base | not this class: no mixed tree |
| `governance.yml:213` | `MACHINERY_BASE` | `machinery_ratchet.py --check-event`: merge-base and first-parent history | diff key, P572 |
| `governance.yml:246` | `SINCE` | `git diff --quiet "$SINCE" HEAD` | diff key, P572 |
| `pr-contract.yml:159` | `PAYLOAD_BASE` | step output `base`, read as `PR_BASE` by "List the paths this pull request changes" (`git diff`) and the raise check (`raises_between`) | diff key, P572 |
| `tests.yml:1180` | `PR_BASE` | `git show "$PR_BASE":tests/mutation_table.py > tests/_mutation_table_base.py`, then run | **in the class**, below |
| `tests.yml:1501` | `BASE` | `closure.py changed --base`, `git diff "$BASE"...` | diff key, P572 |
| `tests.yml:1896` | `BASE` | the same | diff key, P572 |
| `tests.yml:2104` | `BASE` | `closure.py changed --base` | diff key, P572 |

Ten are not this class. The eleventh is, although P572 files `PR_BASE` among the
diff bases: job `mutation-pins` (actions/checkout with no `ref`, so the merge
commit) writes the payload base's `tests/mutation_table.py` into the checkout
and runs it with `--pin-killed`. That program resolves every script it drives
against its own location (`ROOT = Path(__file__).resolve().parent.parent` in
`tests/mutation_table.py`), so a program from the payload's main drives
`tests/closure.py`, `tests/stress.py` and the mutated scripts of the merge
commit's main: the shape of section 1 with caller and callee swapped. The step's
`grep -q -- '--pin-killed'`, `'--budget-minutes'` and `'--shard'` guard the
workflow-to-program interface, not the program-to-script one. The countermeasure
of section 5 owes it a key: `_rbs_defects` matches `git checkout "$PINNED"` and
`"$PINNED:` only, so it does not read this site; the census must also match a
payload-base blob written into the checkout (`git show "<event base>":<path> >`),
and that source resolve to the merge commit's first parent like the 22.
Carried to R10-HOTFIX-RESTORE-BASE-SKEW (the body names the carry).

Whether `arch-score`'s base-to-head comparison credits main's commits when
`base.sha` is not an ancestor of the head was not measured here.

## 4. Cost test

    cost(countermeasure, recurring) < cost(defect) x P(recurrence)

- **cost(defect), per occurrence.** Measured: one PR, 64.6 min. A re-run
  cannot heal a red (section 1), so it costs a head move and one full CI cycle;
  run 42953123178 took 64.6 min from creation (03:29:46Z) to its failed
  re-run's end (04:34:20Z) (`actions_get`, `created_at` to `updated_at`).
  Upper bound, not a measurement: P572 counts 19 of 23 open PRs *exposed*
  (their `base.sha` lacks `8efacee48d`) and records "Not measured: how many of
  them reach `carry_receivable`"; were every exposed PR to redden,
  19 x 64.6 = 1227 PR-minutes.
- **P(recurrence).** One occurrence observed, the one this trigger names; no
  search of other runs' logs was made. Window at `dbd1ab5b07`,
  `W="--first-parent --since=2026-11-04T00:00Z dbd1ab5b07"`: `git rev-list --count $W`
  = 231 first-parent commits, 211 of them merges (`--merges`); 58 touch the
  22 patterns of `pr-contract`'s restore pathspec at `c620ebba96` and 9 touch
  `roster_lib.py` (`git log --format=%H -m $W -- <pathspec> | sort -u | wc -l`;
  null control, the same over `tools/none.py`, prints 0). Any of them that
  changes an interface an unrestored file calls recurs it; the estimate is
  ≥ 1 per week while the train merges at that rate.
- **cost(countermeasure, recurring).** Two parts.
  - The hotfix's resolver: one `git rev-parse HEAD^1` and one
    `git merge-base --is-ancestor` per pull_request run, resolved once in
    `ci.yml`'s prelude (`_rbs_defects` refuses a prelude without it): 100
    pairs took 0.675 s here (7 ms a pair) and 1.609 s on the reviewer's runner
    (16 ms); were each of the 22 sites to resolve its own, under 0.4 s a run.
  - The census arm, `_rbs_defects` with its four plants, added to
    `tests/entities.py` beside the existing `_BP_` arm (it replaces none):
    median 1.98 s, max 2.47 s over 20 runs on a 4-CPU container, run from
    the hotfix WIP `5ab1c861c8`'s source (lines `_bp_value` and the
    `_RBS_` block, extracted verbatim, against `49462e86f3`'s workflows, 29
    defects as at `dbd1ab5b07`); null control, the same timer around an empty
    arm, 0.000 s. Nearly all of it is `yaml.safe_load` of every workflow,
    five times; with the parse cached by text the first run takes 0.222 s,
    same 29 defects. Frequency, not measured: how many times a week
    `tests/entities.py` runs (scoped gate, FULL pushes, mutation lanes that
    re-run scripts per mutant, local runs) was not counted. For scale only:
    `ci.yml` ran 999 times between run 6266 (2026-11-09T00:20:41Z) and run
    7265 (2026-11-11T07:12:02Z), `list_workflow_runs ci.yml` pages 1000 and 1
    at `perPage=1`, about 3060 a week.

Per week, against the one measured occurrence (64.6 min): the resolver, once per
`ci.yml` run, costs 3060 x 0.016 s = 49 s. The census arm is stated by its
break-even, since its run count is unmeasured: as written it pays while
`tests/entities.py` runs fewer than 64.6 min / 1.98 s = 1957 times a week, and
with the parse cached fewer than 64.6 min / 0.222 s = 17459; against the 1227
PR-minute upper bound, 37181 and 331621. At one run per `ci.yml` run (3060) the
arm as written does not pay on the measured occurrence and the cached one does.
The cache is carried to R10-HOTFIX-RESTORE-BASE-SKEW, with the count of
`tests/entities.py` runs a week as the measurement that settles it.

## 5. The cheaper detector, and the countermeasure

**The cheaper detector existed in shape and asserted the defect.** The
`entities.py` census above is static, local, and runs whenever a workflow
changes. Had its pull_request arm required the merge commit's first parent, it
would have refused the first base-pinned restore on 2026-10-23, before any PR
reddened, at the standing cost section 4 measures. The countermeasure is
therefore to change that unit, not to add a rule (state (c)):

1. The census asserts every restore resolves to the merge commit's first parent
   on a pull_request, over every workflow file, with the payload-base read
   planted as its control: built by R10-HOTFIX-RESTORE-BASE-SKEW (WIP
   `4f9fc83dc7`, `5ab1c861c8`), not here, so this seat stays outside the fix.
2. The runtime assertion that the payload `base.sha` is an ancestor of `HEAD^1`
   in the one shared resolver, which turns an unexplained `AttributeError` into
   a named refusal: same group.

Demonstration (`defect-root-cause.md`: the census failing on the defect and
passing once fixed), run with the arm extracted verbatim from `5ab1c861c8`
as in section 4: against `49462e86f3`'s workflows it prints `defects=29`, among
them `pr-contract.yml:pr-contract restores from BASESHA`; against
`5ab1c861c8`'s own workflows, `defects=0`. The fixed state is WIP, not landed,
and the `tests.yml:1180` site of section 3 is in neither count, since the arm
does not read it. The arm inside `tests/entities.py` is the hotfix's mutation
proof and its reviewer's to check (`fix-review.md`).

No policy change is proposed: the rule a seat follows ("restore graders from the
base") was right; its implementation read the wrong commit.
