R9-DBG-0, R9-DIAG-1 and R9-FR-1 are recorded `stage: done` with their issues
closed as completed, but their pre-study deliverables exist only on `handoff/*`
refs and are absent from `main` under any name — and a landed file already cites
one of them (`tools/replay/debug_replay.py:49` cites `debugger-prestudy.md
section 5`, a document the tree does not hold). This lands the three documents,
and the small scripts and `runs/` evidence each names, at the round's own
convention path `dev/audit/rounds/round9/prestudy/` — where the round's other
pre-studies (`integration-prestudy.md`, `surfaces-prestudy.md`, the ALT endgame
plans) already live, and where a new tracked file falls in the `dev/audit/`
INERT prefix (`tests/closure.py:297`) and the `dev/audit/rounds/**` layout
category (`tests/layout.json:79`) the siblings use, so no new classification
entry is added.

Refs inventoried (each with `git diff --name-status origin/main...<ref>`; not the
task's list taken on trust):

- `handoff/r9-dbg-0` @ `eae236d6` — R9-DBG-0
- `handoff/r9-diag-1` @ `3c90f86a3` — R9-DIAG-1
- `handoff/r9-friction-study` @ `c8a6be1cf` — R9-FR-1 (the FR-1 ref; resolved by
  `git ls-remote 'refs/heads/handoff/*friction*'`)

Documents are transcribed verbatim; the only added line is one provenance HTML
comment at the head of each, naming its source ref and the baseline SHA at which
its paths were measured (the reorganisation moved `tools/audit/round9/` under
`dev/audit/rounds/round9/`), so a stale path is flagged rather than rewritten.

## What landed, and what was left (with the reason)

| file | ref | decision |
|---|---|---|
| `debugger-prestudy.md` | r9-dbg-0 | **landed** — the R9-DBG-0 deliverable |
| `boost-drift-prestudy.md` | r9-diag-1 | **landed** — the R9-DIAG-1 deliverable |
| `friction-prestudy.md` | r9-friction-study | **landed** — R9-FR-1 round 1 |
| `friction-prestudy-r2.md` | r9-friction-study | **landed** — R9-FR-1 round 2 |
| `friction-prestudy-r2-groups.json` | r9-friction-study | **landed** — the fold set the r2 document §6 says is "in" it (7.7 KB); the FR-1 resume names it |
| `boost_drift_refit.py` | r9-diag-1 | **landed** — the script the §4 refit table is measured with; it reads `runs/boost-model-wrong15.json` and `runs/null-no-boost.json` |
| `runs/` (diag, 12 files) | r9-diag-1 | **landed** — the arm `.json` carry the `daily` rows the §3 F1 table is read from and the two the refit reads for §4; the `.log` carry the §4 F4 variant tables the document cites by name |
| `runs/` (debugger, 5 files) | r9-dbg-0 | **landed** — `gen-week.log` carries the RESULT byte figures the document states; `ingest-smoke.log`/`ingest-smoke-corrupt.log` the 12/12 and 11/12 verdicts; the two bundles are **22,658 B** and **132,629 B** (measured `git ls-tree -l`), not multi-MB, and the document names them as committed, so they make the §5 bundle shape and the ingest smoke directly re-runnable |
| `dbg_bundle_gen.py` | r9-dbg-0 | **left** — already on main as `tools/replay/dbg_bundle_gen.py` |
| `dbg_ingest_smoke.py` | r9-dbg-0 | **left** — generalised into `tools/replay/debug_ingest.py` on main, whose docstring names it (`Generalises the R9-DBG-0 smoke (dbg_ingest_smoke.py at eae236d66)`); landing the prototype beside its generalisation is a parallel copy |
| `boost_drift_replay.py` | r9-diag-1 | **left** — already on main as `tests/boost_drift_replay.py` |
| `handoff/round9/fix/resume/DBG-0.md`, `FR-1.md` | all | **left** — seat baton notes (the `handoff/` class), volatile seat state, not pre-study deliverables; their actionable content (the debugger doc §8 open decisions, the fold set and seven issue dispositions) is in the documents and the groups JSON |

## Head

b24adb76639d2ed7fe2644e8076fe8b3120a4279

## Mutation proof

n/a: no production line changes. The diff adds documents and read-only evidence
under `dev/audit/`, which `tests/structure.py` does not measure and no production
module imports; the classification arm is the `layout --guard` null control below.

## Null control

At `origin/main` the three documents are absent and a landed file already cites
one:

    git ls-tree -r origin/main --name-only | grep -E 'round9/prestudy/.*(debugger|boost-drift|friction)-prestudy'
    -> (none present)
    git grep -n 'debugger-prestudy' origin/main -- tools/replay/debug_replay.py
    -> origin/main:tools/replay/debug_replay.py:49:# synthetic week (debugger-prestudy.md section 5).

The `layout --guard` machinery is shown live by a planted file at an uncovered
path (`dev/round9-orphan-probe.md`, temporarily staged):

    python3 tests/layout.py --guard --base origin/main
    -> placement: dev/round9-orphan-probe.md is in 0 categories of tests/layout.json ... ; GUARD: 1 refusal(s)

removed, the same command reports `GUARD: 0 refusal(s)` — the guard fires, and
the `dev/audit/rounds/**` placement is what satisfies it.

## Figures

    git rev-parse HEAD                                   -> b24adb76639d2ed7fe2644e8076fe8b3120a4279
    git show --stat HEAD                                 -> 23 files changed, 31164 insertions(+); week/bundle.json.gz 132629 bytes, day1-bundle.json.gz 22658 bytes
    git ls-tree -r -l HEAD -- dev/audit/rounds/round9/prestudy/runs  -> 17 runs/ blobs (12 diag, 5 debugger) with sizes
    python3 tests/layout.py --guard --base origin/main   -> GUARD: 0 refusal(s) (rc 0)
    PYTHONPATH=tests/hastub python3 tests/entities.py    -> ALL 2234 ENTITY CHECKS PASSED (rc 0)
    python3 tests/structure.py                           -> STRUCTURE RATCHET PASSED (rc 0, no metric moved)
    diff <(tail -n +2 <landed doc>) <(git show <ref>:<old-path>)  -> empty for all four documents and both scripts (body byte-identical; one provenance line added)
      control: the same diff without `tail -n +2` is non-empty (the added comment line differs), so the comparison can fail
    bash tools/pr/prepr.sh <this body>                   -> PREPR_RC=0 (clean), PR-BODY 0 error(s)

## Red checks

none

## Forward-carry

none — this lands documents; no finding here changes how a later stage works.
The R9-DBG-3 group already cites `debugger-prestudy.md` section 5 from the landed
`tools/replay/debug_replay.py:49`, and this landing is what makes that citation
resolve.

## Friction

fixer: stale: the seat brief's situation table listed `dbg_ingest_smoke.py` as
not-landed; `tools/replay/debug_ingest.py` already generalises it on main.
