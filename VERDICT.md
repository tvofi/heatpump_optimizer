Fix review: blocked e9a7b9b49bc695cb0472e1a574051e20f8e12828 harness: class-open tests/structure.py runs unowned and unpinned inside the arch-score gate's process

bus-nonce: c17e10b9cd6611ea59d186d0a5bf1399

Round 1. Reviewer: review-2068 (opus), from a detached worktree at the head; contract current (`git diff merge-base...origin/main -- dev/governance/roles/` empty).
Head measured: e9a7b9b49bc695cb0472e1a574051e20f8e12828. It differs from code head 397895df only by `dev/programme/delivery/2068.md` (+1 line), so it is record-only and every figure below applies to it. I re-read the live head just before posting and it was still e9a7b9b4.

## Blocking 1: the gate's protection is ownership, but an unowned file runs inside the gate

arch-score.yml runs the pull request's own copy of the score, and its header says this is safe because "CODEOWNERS names tools/audit/archscore/". `vector.load_structure` (vector.py:84) executes `REPO/tests/structure.py` inside gate.py's process. That file is the PR's copy:
- CODEOWNERS has no `/tests/structure.py` line (grep count 0).
- It is pinned only in tests.yml. arch-score.yml restores nothing from the base.
- `codeowners_gap.py --check` lists it as `PINNED` and reports `uncovered_files=0`. It cannot see an importlib-by-path load, so the gap is invisible to that instrument as well.

Plant (patches under evidence/):
- P0, the control: two modules that import each other, plus one import of them in coordinator.py. Result: `FAIL: dS -2.7550 WORSENS; unexplained: dead_members 1->2; import_cycle_modules 0->2; public_unused 1->2`, rc=1.
- P1: P0 plus 7 lines appended to tests/structure.py that replace `__main__.decide` when the file is loaded as `archscore_structure`. Result: the same `dS -2.7550` with all three rises, then `PASS: planted: every rise waved through`, rc=0.

The structure.py edit is invisible to tests.yml, which restores base's copy. It is also invisible to code-owner review, because the file is unowned. A narrower edit, such as zeroing one structure-derived metric, flattens that metric's rise in the same way.

Fix, either way: add `/tests/structure.py @tvofi` to CODEOWNERS, or restore it from the base in arch-score.yml as tests.yml does. Also widen codeowners_gap.py's surface so that it follows `spec_from_file_location` loads, or say in the body that it does not.

## Blocking 2: stale body claims (re-take the whole body)

- What-changed item 5 says the workflow "restores tools/audit/archscore/ and tests/structure.py from the base, so a pull request cannot edit the check that grades it". That is false at this head: 545d5bda switched to the PR's own copy, and the Null-control section says so.
- Figures and Scope cite run 37689221025 at 6ec6553e as "the head's parent; the head adds only the carry record". The head is now three commits plus a merge past that, including a workflow and CODEOWNERS change. Cite this head's own runs. `fast (3.14)`, `closures` and `coverage` were still in_progress at e9a7b9b4 when I checked.

## The questions asked

- **Decision rule.** Code reading and `--self-test` agree. Self-test: all 8 cases pass, both locally and in CI job 113579733352.
  - It passes exactly when the change is admissible (no SCORE or GATE_ONLY metric rose) and dS >= 0.
  - Otherwise it passes only if every rise has a line under `## Architecture score` that names the metric (word-bounded) and carries at least 30 more characters.
  - dS < 0 with no rise cannot occur, because every term of an admissible change is >= 0. If it did, it would pass vacuously with an empty "every rise explained" list. That is harmless today, but `decide` does not assert it.
  - The P0 plant above is an end-to-end refusal with the expected rc.
  - The two red-team plants (`rt_14_hub_write_presolve`, `rt_15_payload_cast`) I did NOT re-run locally (heavy, CI's). Their verdict of record must come from this head's `fast (3.14)` arch_score run, which had not finished.
- **Concurrency.** `group: ${{ github.workflow }}-${{ github.run_id }}` with `cancel-in-progress: false`. Each run gets its own group, so nothing is ever cancelled. `_CC_TWIN_ROUTE` in tests/entities.py names `arch-score.yml: per-run`. Both arch-score runs at e9a7b9b4 completed success. OK.
- **Required-check safety.** The workflow has no `paths:` filter and no job `if:`, so it runs on every PR (opened, edited, synchronize, reopened) and on merge_group. It measures only `custom_components/` at the merge base and at the head, so a PR that touches no code reads flat. CI at e9a7b9b4 printed `merge base 4dbe5aace744 ... dS +0.0000 NULL / PASS`.
  - I found no wedge for a non-code PR.
  - The one caveat applies to every required check here, not only this one: a head pushed with GITHUB_TOKEN starts no pull_request run.
  - Do not add `arch-score` to ruleset 23698884 until Blocking 1 is closed. As it stands the required check is bypassable by an unowned file.
- **CODEOWNERS `/tools/audit/archscore/`.** Consistent, not a block.
  - CODEOWNERS' own derived rule (workflow-executed scripts and their imports are owned or pinned, #1515) puts gate.py and its imports on the surface.
  - `fold_ledger.py` and `merge_fastpath.py` are precedent: tools/audit instruments that are owned for exactly this reason.
  - tvofi's 2026-10-05 ruling is "only policy and ratchets", and a required one-sided score gate is enforcement surface.
  - Mandate decision 3 in the body records acceptance.
  - The entry is incomplete rather than wrong: see Blocking 1.

## Checks
- **Red at e9a7b9b4:** `nightly-status` only. It is not this PR's, because the diff does not reach what it reads.
- **In progress:** `fast (3.14)`, `closures`, `coverage`, `browser`, `env-matrix`, `Analyze (python)`.
- **Cancelled at 397895df** (superseded by e9a7b9b4): fast, closures, coverage, Analyze (python).

## Not verified
- C12/C13 mutation proofs and the wave table: not re-run (heavy; CI's).
- Red-team sweep completeness (11 plants): not independently re-derived.
