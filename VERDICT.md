Fix review: merge 15a99c4ff739b8b91e89699a165cb72058e2f173

bus-nonce: 25a41551552a7e015f7e0e79bd08cf62

Round 2 (delta review over the reviewed head 8daf6df1576494f49f0ac32d790dbedbb6c92d0e). The delta is the fixer's commit 11e9a4e96 (merged as 6804e9c5a) plus an automatic main merge (5e2ef89b) with no resolution. `review_carry.py` prints FRESH-REVIEW because 11e9a4e96 changes content. The own delta touches only `tools/plan/replan.py`, `tools/audit/seat/plan_page.py` and `tools/audit/seat/plan_phases.py`. Nothing under `custom_components/` changed, so the scope does not widen.

## Evidence

- RESULT previous block 1 (phase_hours unwired) is resolved. `MODEL_FIELDS` now names `phase_hours`, and `build_plan` copies it only when it is present (`replan.py:1537`), so it is not required. The self-test arm now goes from durations to `build_plan` to `render`. M1-unwire (drop `"phase_hours"` from `MODEL_FIELDS`) is KILLED, and so is M17-page-handoff (`phase_hours=None` at `plan_page.py:800`). Both fail on the phase arm with `got: (2, 2)` (ev/selftests-and-mutants.txt).
- RESULT previous block 2 is resolved. Each mutant ran at the head and was restored afterwards, and the worktree was clean after the runs:
  - M6 (`check_plan` next-round recursion changed to `pass`) is KILLED with `got: []`.
  - M16 (`except PlanError` changed to `except ZeroDivisionError`) is KILLED.
  - M15 (`"beyond"` changed to `0`) is KILLED with `got: 0`.
  - Driver: ev/mutation_driver.py.
- RESULT figures at head (ev/selftests-and-mutants.txt):
  - `plan_page self-test: 152 checks, 0 failed` matches the body.
  - `self-test: 0 failed` (replan) matches the body.
  - `beat_jobs self-test: 284 checks, 0 failed`. The body says 274. The difference comes from main: main's base 5e2ef89b gives 281 (ev/beat_jobs-main-base.txt), and the PR's own +3 matches its earlier 271 to 274. See the Note.
- RESULT merge: `git merge-tree --write-tree origin/main 15a99c4ff7` against origin/main 91674d15cd exits 0 with no conflict (ev/merge-tree.txt).
- RESULT VERSION, manifest, RELEASE_NOTES and both claim files are untouched in the three-dot diff (ev/threedot-stat.txt).
- RESULT CI: `merge_train.py classify 15a99c4ff7 --pr 3676` prints `GREEN 15a99c4ff739b8b91e89699a165cb72058e2f173 pending: none red: none` (ev/classify-log.txt). No owed red is open at this head, so no `## Red checks` answer is owed.
- RESULT head re-read: the branch head is still 15a99c4ff7 (ev/head-reread.txt), and the body's `## Head` names it.
- Finder's harness: none named. This is an owner-directed instrument group, so each carry's own control is its harness. The mutation driver and the phase_hours domain probe are the reviewer's, not the finder's.
- Note: figure-stale: the body's `## Figures` beat_jobs line (274) is the pre-merge count; at this head it is 284, and the increase is main's, not this PR's. Carry: dismissed: paperwork at a head whose code is verified; the count is re-derived above.

## Findings

- Residual: the body says `_model_duration`'s guard makes a separate validator unnecessary, but the guard does not cover the whole input domain that the new durations path opens (ev/phase_hours_domain.txt).
  - `phase_hours: {"finders": NaN}` (Python's `json` accepts `NaN`) prints `nan h (plan model)`, and `Infinity` prints `inf h (plan model)`.
  - A non-dict `phase_hours` (a list or a number) raises `AttributeError` in `render`.
  - `check_plan` checks none of these cases.
  - Today the fault cannot be reached: `durations.json` has no `phase_hours`, and every malformed value fails visibly rather than as a plausible figure.
  - Carry: dismissed: unreachable at this tree; any malformed value fails loudly or prints as nan/inf, never as a believable duration
