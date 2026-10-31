---
description: CI autofixes UNDER-SCOPED and INERT READS closures, inherited claims and killed mutants — do not duplicate
paths:
  - "tests/closures.json"
  - "tests/golden/claimed_drift.txt"
  - "tests/golden/card_claimed_drift.txt"
  - "tests/mutation_budgets.json"
  - "tests/mutation_ledger/**"
  - ".github/workflows/**"
---
# Mechanical CI autofix (do not re-implement)

Same-repo PRs run three jobs (`.github/workflows/tests.yml`). **Before the PR exists
nothing waits**: a handoff ref runs no job, so a red `prepr.sh` step 6d predicts is repaired
before handoff (`--single`; for INERT READS `python3 tools/pr/ci_predict.py --apply-inert`,
which writes the Linux recording's entry). Once it exists, if `tests / closures` is
`UNDER-SCOPED`, `tests / fast` fails `INHERITED CLAIMS` or `tests / mutation` refuses unpinned sites, **wait** --
a `DIRTY` head queues no run, so no bot commit comes. Do not open a parallel PR,
Darwin `--single` an under-scope CI already recorded, or hand-empty claim files
that match `origin/main`. Darwin can `--single` a **new** node script or grow a node
closure, never replace a Linux node recording.

**That wait holds only while the job reports it is
repairing.** Each job pushes on `changed` alone and prints its status to the
job summary. `closures-autofix` goes red on `skip-failed-recording`,
`skip-merge-failed`, `skip-still-fails`, `skip-unchanged`,
`skip-classifier-disagrees` and `skip-manual-repair-owed` —
and did not happen. **A red autofix job means no bot commit comes**; the
`--single` prohibition above lapses. Read the summary
line, re-derive the script it names and commit `tests/closures.json`; Python
lanes record through `sys.addaudithook`, so Darwin is sound for them — except
the Linux-recorded (`strace`-only) inert dimension: the bot merges
INERT READS from CI recordings too. On `skip-failed-recording` a
named script (or its driven child) stopped while recorded: fix it first, as re-deriving records the same truncation.

**What green means — read the summary line, not the tick.** Green is
`changed` (repaired and pushed), `skip-clean` or `skip-not-under-scoped` (no
repair was owed *to the bot*), or `skip-not-allowed` (it declined to
classify). It runs the base's `tests/closure.py`: if that stops early
(a PR moving a file out of INERT) where `closures` printed UNDER-SCOPED, the
status is `skip-classifier-disagrees`; any other failed check (PHANTOM, NOT A
FILE, an INERT pair) is `skip-manual-repair-owed`, so `skip-not-under-scoped` means it passed. `claims-autofix` never reddens
(`apply_inherited_claims` has no failure status; `skip-not-inherited` answers
every unrelated `fast` failure): its summary line is its only signal.

**Four paths still end green unrepaired.**

- **A committed phantom.** `check` fails the `closures` job when the committed
  table lists a path that is not a file, but the autofix reports no
  UNDER-SCOPED and stays green: a recording cannot drop a dead path. Repair the
  table: `python3 tests/closure.py prune`.
- **The loop guard.** After the bot pushes, the next head's subject is
  `ci: re-record closures`, so `autofix_allowed` refuses *before* classifying:
  a still UNDER-SCOPED run reads `skip-not-allowed`, and no second commit comes.
- **A truncated recording masking the under-scope.** `check` never inspects a
  recording's `rc`, and a script that exits early records only what it
  reached — so where that truncation hides the *only* under-approximation,
  `check` passes and the job is green on `skip-clean` — or on `changed`, since
  an unnamed script's cut-short recording is left out. `skip-failed-recording`
  fires only *after* UNDER-SCOPED prints, deliberately: unrelated
  `no-copies` and NOT-A-FILE failures fail recordings too, and their closures
  were never stale.

  A failed recording reads files a clean run never does (`linecache`): an
  UNDER-SCOPED beside one may be an artefact. Fix the script; a push re-records.
- **A survivor.** `mutation-autofix` pins kills only, so a site no driver kills
  leaves it green, `tests / mutation` red. `pinned by
  mutation-autofix` is a prediction until a `mutation-pins` log or `--pin-killed`
  kills the site; a `-- lives` line is the seat's.

| Failure | Job | Commit subject | Code |
|---|---|---|---|
| `UNDER-SCOPED`, INERT READS | `closures-autofix` | `ci: re-record closures` | `closure.apply_under_scoped_recordings` |
| `INHERITED CLAIMS` | `claims-autofix` | `ci: drop inherited claims` | `env_drift.apply_inherited_claims` |
| unpinned sites | `mutation-autofix` | `ci: pin killed mutants` | `mutation_table.apply_pins` |
| no null control | none | none | `ci_predict.null_control_preds` predicts it; add a whole-line comment |

Those subjects are loop guards. The job dispatches `ci.yml -f pr -f base` once;
a `GITHUB_TOKEN` push's `pull_request` runs are held `action_required`, so the required `gate` and the `tests / *` units are ABSENT at a bot head
until approved: all three jobs approve them, fail-soft without their
secrets, when an App push or body edit cures it. Absent is not green.

When `mutation-autofix` goes red, run `--pin-killed` yourself. A `ci: pin killed mutants`
stales the body's `## Red checks` `mutation` line; the reviewer re-checks it. Do not automate survivor triage,
golden drift, structure budgets, `no-copies`, orphan → `INERT`, or briefs lint. A new selectable script with **no** recording is
not UNDER-SCOPED — add it to a derive lane or `--single` it; autofix cannot invent a trace.

## A driver-file conflict: one bot merges it, none autofixes it

CI never runs on a `DIRTY` pull request: no job is red to key on. Do not replace a driver
with `merge=union`. Only `.github/workflows/merge-main.yml` pushes a resolution (tvofi,
2026-10-08): `ci: merge main`, where `main`'s drivers resolve every conflicting file.
