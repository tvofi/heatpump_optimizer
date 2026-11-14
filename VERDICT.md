Fix review: merge 5a11c05d816dd1dfca988dcba1ca625f74137107

bus-nonce: aa3689bb81c1890c0d69818756a112f9

## Scope

Round 2 of this review, a delta round over the reviewed head 868f8a726bf29471b5f0b42b2e514b83e03cd865. The delta is 9690e76db8 (gate.py, prelude.py, fixture), 727324d879 (delivery row) and two merges: caf8e515ba merges origin/main 50373173d4, and 5a11c05d81 merges the code commit. `git show --remerge-diff` of both merges is empty: no hand resolution (ev/merge-remerge-diff.txt). The delta is instrument code under tools/ci/ and touches no custom_components/ file, so step 12 does not widen the review.

## Prior findings

- Point 1 (failed-unit re-run read as not busy): resolved. `prelude.standing()` overlays a re-queued need only when its previous attempt concluded in STANDS = (success, skipped). The attack shape (`tests / mutation` failed in attempt 1 and queued in attempt 2, `gate` queued) is now busy in `busy()` and in `wait_sources`. The self-test checks pin it, and my mutants below kill it.
- Point 2 (one-sided overlay): resolved. `gate()` now reads sources through `standing(r)` for every other run, including the previous attempt's `started_at`, so a released gate judges the unit where `busy()` read it. With that line mutated away, "one source read: the released gate takes the re-running run's standing pr-contract" fails.
- Point 3 (no domain rule): resolved. The body states R1–R4 as `requeued()`/`standing()` and names null controls for re-run-failed (failed, cancelled, beside the need), re-run-all (prelude re-ran, prelude queued) and no `run_started_at`. I checked R2's empirical premise against the live API: in run 43022147048's latest listing all 41 jobs report run_attempt 2, the carried prelude started 2026-11-11T12:39:05Z, before run_started_at 14:08:41Z, and every re-run job started at 14:08:44Z or later (ev/run-43022147048-latest-jobs.txt). started_at does separate carried jobs from re-run ones, as the body says.

## Findings

- Survivor: dropping R2's clause `jobs.get("prelude") != ("completed", "success")` (ev/mutants.txt, "R2 prelude-green dropped") fails no check in gate or prelude. It is equivalent under GitHub's re-run semantics: a prelude that did not conclude success is re-run by either re-run mode, so its started_at is already at or after run_started_at, or null while it is queued, and the timestamp clause refuses it. Carry: dismissed: equivalent mutant, a non-green prelude is always re-run, so the timestamp clause already covers it

## Evidence

- Head measured: 5a11c05d816dd1dfca988dcba1ca625f74137107 (ev/HEAD.txt), equal to the body's `## Head`. It is still the PR head per classify at the verdict. Merge base = origin/main 50373173d4. `git merge-tree --write-tree origin/main <head>` rc=0 (ev/merge-tree.txt). The role contracts have no diff from the merge base to origin/main.
- RESULT self-tests at the head (ev/selftests-head.txt): gate 106 checks, 0 failed; prelude 82, 0 failed; codescan_wait 25, 0 failed; ruleset_cutover 101, 0 failed. Each matches the body's `## Figures`.
- RESULT mutants (ev/mutants.sh, ev/mutants.txt; FAIL-line counts gate/prelude): STANDS with failure and cancelled added: 3/1. R4 test dropped: 3/1. R2 `pre >= began` dropped: 1/0. R2 prelude-green clause dropped: 0/0 (the survivor above). R1 dropped: 1/0. gate() source read off standing: 1/0. Overlay keeping the latest start: 1/0. judging() on the raw listing: 4/1. Killed counts are this driver's FAIL lines and may differ from the body's per-check counts, but the direction matches (killed versus survived).
- Not re-derived: the body's "7 of the 9 new gate checks failed at 868f8a72" (I did not run the new checks against the old production code). Carry 5, 8 and 9 figures (merge_train 753, merge_pr 28) are outside this delta and were verified in round 1. The 11 prepr.sh diff-mutant survivors are not re-run.
- CI: `merge_train.py classify 5a11c05d816dd1dfca988dcba1ca625f74137107 --pr 3573` printed `GREEN 5a11c05d816dd1dfca988dcba1ca625f74137107 pending: none red: none` (ev/classify.txt). No red, so step 11 owes no answer.
- VERSION, the manifest version, the RELEASE_NOTES heading and the claim files are untouched by the delta. Gate scope is MODE: FULL by the body's account (tools/ci/ touched); CI's heavy run is cited and was not re-run.
