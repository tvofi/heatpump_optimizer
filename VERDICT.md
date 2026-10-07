Fix review: blocked 223f88c24cb52a33ff7a04799d60e5e3ee8e004f root-cause-unanswered: closures and closures-autofix went red at this head, body silent (main's own closures at 38c03d94 is red identically)

bus-nonce: 52b17f201355b63a7a5ea736e74ac9a7

Reviewer seat r9c-rev-2018, round 2. I judged only the delta since 7e197a6f. The measured head is 223f88c24cb52a33ff7a04799d60e5e3ee8e004f, and it was still live when I posted. Its tree is identical to that of e62b8b63, the merge of origin/main 38c03d94 into 00834c66.

## The four delta items: all pass

1. **Mutants killed, measured with my own harness.** `timing_check_mutants_r2.py` runs the head's own pin block from tests/stress.py verbatim, without re-implementing it, against each mutant of `timing_check`.
   - Baseline: 2 checks, 0 failures.
   - Killed: T2 (`!= "1"`), T3 (`recording = True`), T1 and T4.
   - The result is the same with `HPO_CLOSURE_RECORDING=1` preset, which is how the recorder runs it, and the pin restores the variable afterwards (`'1'` stays `'1'`, unset stays unset).
   - My round-1 harness still reports T2 and T3 as surviving, but that is expected: its `stress_pin` column re-implements only the old `(1, 0, 1)` pin.
2. **`## Approval` is now correct.** It names CODEOWNERS lines 138, 140 and 150 and says @tvofi's approving review is owed.
3. **The bugclasses.json merge is correct.**
   - The top-level keys equal main's (e62b8b63^2).
   - `_rca` adds only `R9-RCA-stress-recording` and removes nothing; R9-RCA-1985 is present.
   - `I2.rca` gains only that citation.
   - Outside stress.py, the three-dot patches for closure.py, derive_closures.sh, the RCA doc and the delivery row are byte-identical to round 1's.
   - stress.py's patch grew by exactly 00834c66's 19 lines.
   - `merge-tree` against origin/main exits 0, `closure.py selftest` passes 36 of 36, and VERSION, the manifest, the notes heading and both claim files are untouched.
4. **CI at the head, read from the API.** `fast (3.14)` (job 112810164577) is green.
   - The new pin passed: `with HPO_CLOSURE_RECORDING unset a timing miss fails, and only "1" exempts it ... (#2018)`.
   - All six timing verdicts appear as counted `ok` lines, with 0 "not graded" notes.
   - The run ended `ALL 106 STRESS CHECKS PASSED`.

## Blocking: an unanswered red

`closures` (112810272267) and `closures-autofix` (112820973686) are red at this head.
- `closures` failed with `INERT READS UNDER-APPROXIMATED`: `tests/harness_headers.py` reads `tools/audit/harnesses/eg_b7_seam_hubs.py`.
- `closures-autofix` reported `skip-manual-repair-owed`.

The red belongs to main, not to this PR. Main's own `closures` at 38c03d94 (job 112789710707) fails with the identical line. Neither file is in this diff, and stress.py's recording logs `done tests/stress.py (exit 0)`.

The block exists only because `fix-review.md` step 11 makes silence blocking, and the body names neither check. The fix is body-only and does not move the head: add both checks to `## Red checks` as inherited from main, citing main's run 112789710707 at 38c03d94. The code is otherwise merge-ready.

Not checked: `coverage`, which was still in progress.
