Fix review: merge a39a08f1db5453f79458dadcfe2d975deee664a8

bus-nonce: 99174f7b58e73752c14fa4de6150b6ea

## Scope

Round: re-review of the resolution delta 89b04b74f..a39a08f1d (fix-review.md step 12); a merge verdict stood at 89b04b74f. Head measured: a39a08f1db5453f79458dadcfe2d975deee664a8, still the PR head when this verdict was written. origin/main 486e65cbd9c8451c01624f13b773feb6d722ad9b. No finder's harness is named (packet: "none named"); the harness used is the PR's own `sweep_render.py --self-test` plus targeted mutants of my own, disclosed as mine.

## Findings

- Main's `owed_unactioned.py` sentences in sweep step (5) (from 8f97f7471, R10-RCA-OWED-UNACTIONED) are pinned by no check: my mutant M5 deleted them at the head and `sweep_render.py --self-test` stayed at `24 checks, 0 failed`. A conflict resolution that dropped main's side would therefore have passed every gate. The resolution here kept them verbatim (read, not inferred), the gap is on main before this delta, and the body discloses the sibling gap (the citation check misses a path not at a span's start). Carry: dismissed: pre-existing on main, resolution kept the sentence verbatim, outside this delta

## Evidence

- RESULT resolution: `git merge-tree --write-tree 89b04b74f 7685a4d98` conflicts only in `tools/audit/seat/sweep_template.md`. The hand-resolved tree (b37742fe) differs from the automatic merge in that one file only; `tests/closures.json` merged as a set by the driver (ev/resolution-merge-tree.txt). 74c2a66a7 and a39a08f1d have the same trees as their automatic merges.
- RESULT both sides survive (orchestrator.md section 6, read on the merged artifact): at the head, step (5) equals the PR-side line at 89b04b74f + " " + main's appended owed_unactioned sentences. The PR clause `Read {{tick_log}}'s newest pass unfiltered ...` is present verbatim, main's sentences are present verbatim, and main's superseded `Act on the newest actionable lines` is gone, as the PR intended. No conflict markers. No stale placeholder (`local_seat_cap`, `cloud_above_cap`, `plan_generator`, `plan_artifact`) remains. The three-dot diff differs from the 89b04b74f three-dot only in the (5) context line and index/hunk offsets.
- RESULT self-test at head: `sweep_render self-test: 24 checks, 0 failed`, rc 0 (ev/selftest-head.txt).
- RESULT mutants at head (ev/mutants.txt): M1 drop `--skip-bad` -> 1 failed; M2 drop `DESIGN-BUILD:` -> 1 failed; M3 break the plan_page beat -> 1 failed; M4 `defaults_missing` returns [] -> 1 failed; M6 drop the PR's unfiltered-read clause in (5) -> 1 failed; M5 drop main's owed_unactioned sentences -> 0 failed (finding above). The tree was restored after each mutant.
- RESULT figures re-derived at head: `tests/structure.py` STRUCTURE RATCHET PASSED; `tests/closure.py select` `MODE: SCOPED -- 1 script(s) run, 32 scoped out.` (RUN tests/entities.py); `tests/entities.py` (venv-ci python 3.14) `ALL 2470 ENTITY CHECKS PASSED` rc 0, matching the body's merged-head figure. I did not re-run the base-template figures (`22 checks, 2 failed`) or prepr; they come from the previous verdicted round and are not verified here.
- RESULT merge: `git merge-tree --write-tree origin/main a39a08f1d` rc 0; origin/main 486e65cbd is an ancestor of the head (ev/merge-tree.txt).
- VERSION, the manifest, RELEASE_NOTES.md and tests/golden are untouched in the three-dot diff (0 lines).
- Head (step 7): the body's `## Head` names a39a08f1db5453f79458dadcfe2d975deee664a8 and describes b37742fe as the measured code head, with a39a08f1 as an automatic main merge. I confirmed that merge is tree-identical to the automatic one.
- CI at head (check-runs API, all runs concluded, ev/check-runs.txt): every run is success, skipped or neutral except `tests / nightly-status` failure (job 123316328010). Its log reads `NIGHTLY FAILED: nightly-ha (stable) failed last night` (scheduled run 40806276912 on main head ee48937) and states it is not a required context on `main-protect` and does not block a merge. The diff (delivery row, closures.json, sweep_render.py, sweep_template.md) reaches none of its inputs, so by fix-review.md step 11 it is not this PR's red. The body's `## Red checks` answers it that way, which matches (ev/nightly-status.txt). No check run named `pr-contract` appears at this head; the CI-edit `prelude` (123319878893), which started 07:29 after the red concluded, is success.
- Forward-carry (step 10): the body says n/a and leaves the dispatch-gate arms to the orchestrator; this was judged at the previous head's merge verdict and is unchanged by the delta.
