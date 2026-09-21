---
description: CI already autofixes UNDER-SCOPED closures and inherited claims — do not duplicate
paths:
  - "tests/closures.json"
  - "tests/golden/claimed_drift.txt"
  - "tests/golden/card_claimed_drift.txt"
  - ".github/workflows/**"
---
# Mechanical CI autofix (do not re-implement)

Same-repo PRs already have two jobs in `.github/workflows/tests.yml`. If
`closures` is `UNDER-SCOPED` or `fast` fails `INHERITED CLAIMS`, **wait**.
Do not open a parallel PR, do not Darwin `--single` an under-scope CI
already recorded (Linux `strace` recordings are the ones to merge), and
do not hand-empty claim files that match `origin/main`. Darwin can
`--single` a **new** node script, or grow a node closure; it cannot
replace a Linux node recording.

**That wait is conditional: it holds only while the job reports that it is
repairing.** Each job pushes on `changed` alone, and every other status used
to fall through to job success, so a skipped repair was indistinguishable
from a completed one and the wait never ended (#523). Both jobs now end by
printing their status to the job summary, and `closures-autofix` goes red on
`skip-failed-recording`, `skip-merge-failed`, `skip-still-fails` and
`skip-unchanged` — UNDER-SCOPED was printed, a repair was owed, and it did
not happen. **A red autofix job means there will be no bot commit.** The
`--single` prohibition above does not survive it: that prohibition assumes
the autofix holds the recordings *and will merge them*. Read the summary
line, re-derive the script it names and commit `tests/closures.json`; Python
lanes record through `sys.addaudithook`, so Darwin is sound for them. On
`skip-failed-recording` the script named in the `closures` log stopped while
being recorded — fix that script first; re-deriving it would only record the
same truncation.

**What green means, exactly — read the summary line, not the tick.** Green is
`changed` (repaired and pushed), `skip-clean` or `skip-not-under-scoped` (no
repair was owed *to the bot*), or `skip-not-allowed` (the job declined to
classify at all). The conclusion cannot tell "repaired" from "nothing was
owed"; the summary line can. `claims-autofix` reddens on nothing it can return today —
`apply_inherited_claims` has no attempted-and-failed status, and its
`skip-not-inherited` is the ordinary answer for every unrelated `fast`
failure, so reddening it would over-fire — so its summary line is its only
signal.

**Three paths still end green unrepaired; none is closed here.**

- **A committed phantom.** `check` fails the `closures` job when the committed
  table lists a path that is not a file (#1310), while the autofix finds no
  UNDER-SCOPED and stays green on `skip-not-under-scoped` — the same status a
  clean run reports, so the summary line cannot separate them. A repair is owed
  and no commit is coming: a recording cannot drop a dead path. Repair the
  table in place and commit `tests/closures.json`: `python3 tests/closure.py
  prune` (measured: `apply_under_scoped_recordings` →
  `skip-not-under-scoped`, `autofix_repair_failed` → false).
- **The loop guard.** After the bot pushes, the next run's head subject is
  `ci: re-record closures`, so `autofix_allowed` returns false *before* any
  classification runs: if that run is still UNDER-SCOPED the status is
  `skip-not-allowed`, the job is green, and no second commit comes. Closing
  it needs a dry-run classification and a decision about the loop guard's
  contract. #527 makes this path routine by making the push routine.
- **A truncated recording masking the under-scope.** `check` never inspects a
  recording's `rc`, and a script that exits early records only what it
  reached — so where that truncation hides the *only* under-approximation,
  `check` passes and the job is green on `skip-clean`. `skip-failed-recording`
  fires only *after* UNDER-SCOPED has been printed, deliberately:
  `closures-autofix` runs on ANY `closures` failure, so reddening every failed
  recording would fire on unrelated `no-copies`, NOT-A-FILE and INERT failures
  and send their reader to re-derive a closure that was never stale. The
  script that failed normally reddens `fast` in the same run; one that fails
  *only* under recording would not.

  A failed recording's file list is **not** simply a subset of what a clean run
  would touch: an error path can read files the clean path never does (a
  traceback pulls source through `linecache`). So an UNDER-SCOPED reached with
  a failed recording present may be genuine or may be an artefact of the
  failure. The remedy does not branch on which — fix the failing script, and
  the closures job re-records on the next push — which is why
  `skip-failed-recording` says exactly that and does **not** tell you to
  re-derive.

| Failure | Job | Commit subject | Code |
|---|---|---|---|
| `UNDER-SCOPED` | `closures-autofix` | `ci: re-record closures` | `closure.apply_under_scoped_recordings` |
| `INHERITED CLAIMS` | `claims-autofix` | `ci: drop inherited claims` | `env_drift.apply_inherited_claims` |

Those subjects are loop guards. A `GITHUB_TOKEN` push's `pull_request` runs wait `action_required` for a
human; the job dispatches Tests/Hassfest/Validate and CodeQL, which run at once. Governance's contexts come
from the unheld `edited` run a body edit fires. `recheck-gate` treats `ci:` as PR-like (not `slow`). Both
jobs also approve those held runs as a dedicated Actions-only App, fail-soft while its secrets are absent.

Do not automate golden drift, structure budgets, `no-copies`, orphan →
`INERT`, or briefs lint. A new selectable script with **no** recording is
not UNDER-SCOPED — add it to a derive lane or `--single` it; autofix cannot
invent a trace.

## The claim-file conflict is prevented, not autofixed

A merge conflict in the two claim files is **not** a third autofix case. CI
never runs on a `DIRTY` pull request, so no job is red and there is no
uniquely-detected failure to key on; the trigger would have to be a push to
`main` fanning out over every open PR, and the repair would push to branches
frozen for review. The `claimnotes` driver and why it refuses are
`claim-files.md`'s: do not replace the refusal with `merge=union`, and do not
add a job that pushes resolutions to open PR branches.
