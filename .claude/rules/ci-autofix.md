---
description: CI already autofixes UNDER-SCOPED closures, inherited claims and killed mutants — do not duplicate
paths:
  - "tests/closures.json"
  - "tests/golden/claimed_drift.txt"
  - "tests/golden/card_claimed_drift.txt"
  - "tests/mutation_budgets.json"
  - ".github/workflows/**"
---
# Mechanical CI autofix (do not re-implement)

Same-repo PRs already have three jobs in `.github/workflows/tests.yml`. If `closures` is
`UNDER-SCOPED`, `fast` fails `INHERITED CLAIMS` or `mutation` refuses unpinned sites, **wait**.
Do not open a parallel PR, do not Darwin `--single` an under-scope CI already recorded (Linux
`strace` recordings are the ones to merge), and do not hand-empty claim files that match
`origin/main`. Darwin can `--single` a **new** node script, or grow a node closure; it cannot
replace a Linux node recording.

**That wait is conditional: it holds only while the job reports that it is
repairing.** Each job pushes on `changed` alone, and every other status used
to fall through to job success, so a skipped repair was indistinguishable
from a completed one and the wait never ended (#523). Each job now prints
its status to the job summary, and `closures-autofix` goes red on
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
classify at all). `claims-autofix` reddens on nothing it can return
today — `apply_inherited_claims` has no failure status, and its
`skip-not-inherited` is the ordinary answer for every unrelated `fast`
failure — so its summary line is its only signal.

**Three paths still end green unrepaired; none is closed here.**

- **A committed phantom.** `check` fails the `closures` job when the committed
  table lists a path that is not a file (#1310), but the autofix reports no
  UNDER-SCOPED and stays green — the status a clean run also reports — so no bot
  commit is coming: a recording cannot drop a dead path. Repair the table in
  place: `python3 tests/closure.py prune`.
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

  A failed recording can also read files a clean run never does (a traceback
  pulls source through `linecache`), so an UNDER-SCOPED beside one may be an
  artefact; either way, fix the script and the next push re-records.

| Failure | Job | Commit subject | Code |
|---|---|---|---|
| `UNDER-SCOPED` | `closures-autofix` | `ci: re-record closures` | `closure.apply_under_scoped_recordings` |
| `INHERITED CLAIMS` | `claims-autofix` | `ci: drop inherited claims` | `env_drift.apply_inherited_claims` |
| unpinned sites | `mutation-autofix` | `ci: pin killed mutants` | `mutation_table.apply_pins` |

Those subjects are loop guards. A `GITHUB_TOKEN` push's `pull_request` runs wait `action_required` for a
human; the job dispatches Tests/Hassfest/Validate and CodeQL, which run at once. Governance's contexts come
from the held run once approved (#1514). `recheck-gate` treats `ci:` as PR-like (not `slow`). All
three approve those held runs as a dedicated Actions-only App, fail-soft while its secrets are absent.

When `mutation-autofix` goes red, run `--pin-killed` yourself. Do not automate survivor triage, golden drift, structure budgets,
`no-copies`, orphan → `INERT`, or briefs lint. A new selectable script with **no** recording is
not UNDER-SCOPED — add it to a derive lane or `--single` it; autofix cannot invent a trace.

## The claim-file conflict is prevented, not autofixed

A conflict in the two claim files is **not** an autofix case: CI never runs on a `DIRTY` pull
request, so no job is red and there is no failure to key on, and the repair would push to
branches frozen for review. `claim-files.md` carries the refusal — do not replace it with
`merge=union`, or add a job that pushes resolutions.
