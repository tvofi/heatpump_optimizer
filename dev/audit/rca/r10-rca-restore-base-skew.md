# R10-RCA-RESTORE-BASE-SKEW: a check-source restore pinned to the payload's base mixes two mains

Root-cause seat (`dev/governance/roles/root-cause.md`,
`dev/governance/rules/defect-root-cause.md`) beside R10-HOTFIX-RESTORE-BASE-SKEW,
never inside it: this document edits no workflow and no test. Trigger: the
red-check trigger, `pr-contract` red on PR 3424 at `f9c7952b` (run 42953123178,
job 130312858296). Measured at `origin/main` `dbd1ab5b07` on 2026-11-11 05:05Z.
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
prints 2. The full step, replayed with the hotfix's own instrument
(`dev/audit/harnesses/r10_restore_base_skew.py` at
`handoff-wip/r10-hotfix-restore-base-skew` `5ab1c861c8`):
`--source d08ed31049…` prints `RESULT exit=1`, `RESULT attributeerror=True`;
`--source c620ebba96…` prints `RESULT exit=0`, `RESULT attributeerror=False`.

**Which side moved.** Neither file is wrong; the restore source is. Run 42953123178
was attempt 2 of the run: a re-run keeps both `GITHUB_SHA` and the payload, so it
reproduced the red, and only a new event at a moved head refreshes `base.sha`.

**What `base.sha` is.** Not the commit the merge ref is built on. On three of
four open PRs sampled it equalled `git merge-base <head> <main>` (3423, 3388,
3355); on 3431 it was newer (`444cf62fab` against merge base `40fe1cae2e`). This
document relies only on the measured inequality with the merge commit's first
parent, not on a model of when GitHub sets the field.

## 2. Process state: (c), the process was followed and did not produce the intended result

The process: a census in `tests/entities.py`, landed by `e55be57447`
(2026-10-23, R10-CI-LAYOUT-P2), enumerates every `PINNED` restore in a
gate-required job and asserts, under the check named
"and on a pull_request and a push every such restore reads the event's own commit",
that on a pull_request each expression evaluates to the payload's `BASESHA`.
An older pin from `46a6ac4d68` (2026-09-22), "`policy-docs` restores its graders
from the base commit before it grades", requires the literal
`github.event.pull_request.base.sha` in the step.

Both ran and passed on main and on every reddened PR. Their unit is the
expression's value, "the payload's base"; the property the restore exists for is
"the restored files and the unrestored ones come from one tree", which the
census never reads. Its target was the head (a PR grading itself), and it took
the payload base as the base by construction. Its units were also
`governance.yml` and `tests.yml` only (`_BP_UNITS`), so this instance, in
`pr-contract.yml`, was outside it.

Not (b): no rule asked for the first parent and was ignored. Not (d): no
precondition changed underneath it; `base.sha` was never the merge commit's
parent by contract, and the skew existed from the first restore. What grew is
exposure (section 4), not the defect.

## 3. How far the class reaches

Rule: `grep -n 'PINNED:.*base.sha\|PINNED=.*base' .github/workflows/*.yml`
returns 22 sites at `dbd1ab5b07`: `budget-raise-gate.yml` 1, `ci.yml` 6,
`codeql.yml` 2, `governance.yml` 6, `pr-contract.yml` 1, `tests.yml` 6. Each
restores a subset of paths into a merge-ref checkout, so each mixes two trees
whenever the payload base lags. Disposition: all 22 are
R10-HOTFIX-RESTORE-BASE-SKEW's seam, whose brief says every restore; its WIP
census (`_rbs_defects`) reads every `.github/workflows/*.yml` and plants a
payload-base read into `pr-contract.yml` as a control, so the unit gap of
section 2 is closed there. The one batch arm, `ci.yml:117`
(`git merge-base FETCH_HEAD HEAD`), is not a payload read.

Other `base.sha` reads, `grep -n 'github.event.pull_request.base.sha' .github/workflows/*.yml`
less the 22: `arch-score.yml:63` (scorer and both trees read whole from git, no
mixed tree) and `dependabot-automerge.yml:69` (a whole checkout of the base, no
mixed tree). Neither is this class. Whether `arch-score`'s base-to-head
comparison credits main's commits when `base.sha` is not an ancestor of the head
(3431's shape) was not measured here.

## 4. Cost test

    cost(countermeasure, recurring) < cost(defect) x P(recurrence)

- **cost(defect), per occurrence.** 19 of 23 open PRs red at the order (the
  ruling's count). Re-measured: 17 of 23 open PRs at 05:05Z have a payload
  `base.sha` lacking `e08425e904` (rule: `git merge-base --is-ancestor e08425e904 <base.sha>`
  over `list_pull_requests state=open`'s `base.sha`), and the same 17 restore
  files differing from main (`git diff --name-only <base.sha> dbd1ab5b07 -- <pr-contract pathspec> | wc -l` non-zero).
  Null control: the three PRs whose `base.sha` is `dbd1ab5b07` (3419, 3424,
  3432) read 0 differing and `has`. A re-run cannot heal a red (section 1), so
  each costs a head move and one full CI cycle; run 42953123178 took 64.6 min
  from creation (03:29:46Z) to its failed re-run's end (04:34:20Z). 19 x 64.6 =
  1227 PR-minutes of gated latency, once.
- **P(recurrence).** One occurrence observed in the 7 days to 2026-11-11, in
  which 57 of main's 231 first-parent merges touched the `pr-contract` restore
  set and 9 touched `roster_lib.py` (`git log --first-parent --since=2026-11-04T00:00Z -m origin/main -- <pathspec>`).
  Any of them that changes an interface an unrestored file calls recurs it; the
  estimate is ≥ 1 per week while the train merges at that rate.
- **cost(countermeasure, recurring).** The hotfix's resolver: one
  `git rev-parse HEAD^1` and one `git merge-base --is-ancestor` per restoring
  job, 13 ms a pair (100 pairs in 1.32 s, `time` locally); 22 sites, under
  0.3 s of runner time per PR. Its census arm replaces an existing one in
  `tests/entities.py`, no new script.

0.3 s per PR against ~1227 PR-minutes per weekly occurrence: the countermeasure
pays.

## 5. The cheaper detector, and the countermeasure

**The cheaper detector existed in shape and asserted the defect.** The
`entities.py` census above is static, local, and runs whenever a workflow
changes. Had its pull_request arm required the merge commit's first parent, it
would have refused the first base-pinned restore on 2026-10-23, before any PR
reddened, at no added standing cost. The countermeasure is therefore to change
that unit, not to add a rule (state (c)):

1. The census asserts every restore resolves to the merge commit's first parent
   on a pull_request, over every workflow file, with the payload-base read
   planted as its control: built by R10-HOTFIX-RESTORE-BASE-SKEW (WIP
   `4f9fc83dc7`, `5ab1c861c8`), not here, so this seat stays outside the fix.
2. The runtime assertion that the payload `base.sha` is an ancestor of `HEAD^1`
   in the one shared resolver, which turns an unexplained `AttributeError` into
   a named refusal: same group.

Demonstration owed: `defect-root-cause.md` requires the census shown failing on
the defect and passing once fixed. This seat's run of the hotfix's
`tests/entities.py` against `origin/main`'s workflows was stopped waiting on the
gate lease, so that pair is the hotfix's mutation proof and its reviewer's to
check (`fix-review.md`); the replay pair in section 1 is the one this seat ran.

No policy change is proposed: the rule a seat follows ("restore graders from the
base") was right; its implementation read the wrong commit.
