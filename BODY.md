Root-cause record for the third `GREW critical_path_minutes` on `main` (`8f286293b`, run 41397326281), extended to the fourth (`8e90d8144`, run 41818271680). The record is `dev/audit/rca/r10-ci-critpath-3.md`. Its replay is `dev/audit/harnesses/r10_rca_ci_critpath_3/replay.py`, over three Actions-API fixtures beside it. No production code, budget, claim file or ratchet changes. Both countermeasures are drafts for the owner; red 4's hotfix is the orchestrator's and is not touched.

This head repairs review round 2 (verdict/3189, blocked: `tests / fast (3.14)` failed `harness_headers.py` on the replay's depth root `ROOT = HERE.parents[3]`):

1. **The replay finds the repository root by the canonical walk-up**, an inlined copy of `tools/audit/repo_root.py`'s `repo_root` that `harness_headers.inline_scan` accepts byte for byte. No fixed parent depth remains in the harness.
2. **`tests/closures.json` records the harness** under `inert_reads` for `tests/harness_headers.py` (one added line), from `tests/derive_closures.sh --single tests/harness_headers.py` run on Linux. That clears the `INERT READS UNDER-APPROXIMATED` refusal.
3. **The record states the image change in the host step** (the verdict's residual). Replay step 5 compares run 4009 (image 20261025.179.1) with run 4128, the only fast (3.14) job on image 20261101.186.1, so the ×1.72 per-script exhibit is confounded with the image. The record now says so, and cites run 4035, a slow job on the same image as 4009 (27.3 min against 20.4), by job minutes only because no per-script log was kept for it. The replay prints the image pair and run 4035.
4. `origin/main` moved to `3583448e1` since the base; it is merged into this head.

## Head

a7ecefe2d68177574d27befc5100cb6bea293c72

`origin/main` was at `3583448e197ab9625a4e684264290e19c80fdd69` at 2026-11-04 UTC and is merged. `tools/pr/prepr.sh` was run once at this head after that merge and the closures record: rc=0, `git status --porcelain` empty.

## Mutation proof

No production line changes. The repair's own mutant: restoring `ROOT = HERE.parents[3]` in the replay turns `harness_headers.py` red: `FAIL every inlined walk matches the canonical helper and no depth root remains [FAIL depth seams: dev/audit/harnesses/r10_rca_ci_critpath_3/replay.py:64: ROOT = HERE.parents[3]]` and `1 of 112 HARNESS HEADER CHECKS FAILED`. Restored, it prints `ALL 112 HARNESS HEADER CHECKS PASSED`. The replay's own mutant from round 1 stands: grading red 3 with the live ratchet prints `RESULT: does NOT hold`.

## Null control

The finder's detector, `python3 -c "import sys; sys.path.insert(0,'tests'); import harness_headers as h; print(h.depth_root_seams())"`, on the unrepaired head `fd9c5bab5` printed `['dev/audit/harnesses/r10_rca_ci_critpath_3/replay.py:51: ROOT = HERE.parents[3]']`, and at the base `8e90d8144` and at this head it prints `[]`. With the mutant above it prints the seam again. The replay's pinned control from round 1 is unchanged.

## Figures

- `python3 -c "import sys; sys.path.insert(0,'tests'); import harness_headers as h; print(h.depth_root_seams())"` prints `[]` at this head: the rule that enumerates the depth-root seams of the class, over every file in its scope, so no other seam is open.
- `PYTHONPATH=tests/hastub python3 tests/harness_headers.py` prints `ALL 112 HARNESS HEADER CHECKS PASSED`.
- `python3 dev/audit/harnesses/r10_rca_ci_critpath_3/replay.py` prints `RESULT: holds`; its step 5 prints the image pair and run 4035's 27.3 min. Every other figure in the record is unchanged from round 1.
- `bash tests/derive_closures.sh --single tests/harness_headers.py` prints `tests/harness_headers.py    401 files` and adds the one `inert_reads` line.
- `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"` prints `MODE: SCOPED -- 0 script(s) run, 33 scoped out`.
- `python3 tests/structure.py` prints `STRUCTURE RATCHET PASSED`.

## Red checks

Check-run set of `fd9c5bab5` (all 55, one page): the concluded reds are below. All of the first four are this diff's own, from one cause, `ROOT = HERE.parents[3]` in the new harness.

- `tests / fast (3.14)`: `harness_headers.py` refused the depth root. Owner: this PR. Cheaper detector: `harness_headers.depth_root_seams()`, under a second, no Home Assistant stack. Standing cost: one call of it in `prepr.sh`, under a second a run. `prepr.sh` does not run it today: `harness_headers.py` is `run_always` only in CI (`tests/run.sh:720`) and `prepr.sh:433-434` defers it wholesale. Round 1 never measured the line (no check ran at `00f1d0eca`), so the earlier "none" here was true only because nothing ran. Repaired here; the prepr follow-up is under `## Forward-carry`.
- `tests / closures`: `INERT READS UNDER-APPROXIMATED`, the new harness read by `harness_headers.py` with no `inert_reads` entry. Owner: this PR. Same cause; the entry is recorded in this head.
- `tests / closures-autofix`: `skip-failed-recording`, because `harness_headers.py` exited non-zero while it was recorded. Owner: this PR, same cause; it is repaired by the head above, and the entry is already recorded so no bot commit is owed.
- `gate` (two runs) and `pr-contract / pr-contract` (two runs): aggregates of the checks above and of the body's earlier `## Red checks`; they follow this head.
- `tests / nightly-status`: main's, not this PR's. The diff reaches only `dev/audit`, `dev/programme/delivery` and `tests/closures.json`'s `inert_reads`.
- `codeql / Analyze (python)` concluded cancelled, not red.

## Forward-carry

`prepr.sh` should run `harness_headers.inline_scan()`, or at least `depth_root_seams()`, and leave only the timed parts of `harness_headers.py` to CI, so a branch adding a harness under `dev/audit/` cannot reach CI red on a static, sub-second check. Lands in the prepr/gate group R10-PREPR-CAP (`tools/pr/prepr.sh`). Carry: R10-PREPR-CAP

## Friction

none
