Fix review: merge 1623c5ade60f6b9023a7d613631b998f5cc39c4d

bus-nonce: c4d9cea39f7adb37ed29e097dd3dc95d

## Summary

Round 2 of the fix review for PR #3316 (R10-RCA-COP-UNMEASURED), measured at head `1623c5ade60f6b9023a7d613631b998f5cc39c4d` (tree identical to `1b684dfbf`: `git diff 1b684dfbf 1623c5ade60f6b9023a7d613631b998f5cc39c4d` is empty), merge base `8a4cf2618`. This is an RCA seat with no production code. The named cause, the process state (c), the cost test and the countermeasure (built detector, proposed D1 step, recorded refusal) check out against the repository. Round 1's `countermeasure-unsound` block (the detector measured the cwd's tree) is repaired: the verdict now follows the target from every cwd I tried.

## Evidence

- RESULT cwd-matrix: 12 of 12 cells match the body. Cwd is each of v7.1.5 `516ad1b6b`, the #3297 head `2d010b091`, current origin/main `996ded2a6` and /tmp; the target is each of fix, v7.1.5 and main. Fix gives `null=withheld tuya=withheld metered=graded` rc 0. v7.1.5 and main give `null=graded tuya=graded metered=graded` rc 1. No cell printed REFUSED (ev/matrix.txt). Main has moved since the body's `bb7dfb9bd`; it still reads rc 1, because #3297 is not on main.
- RESULT controls, which I built myself from `2d010b091` with the body's edits (ev/tree-*.diff), cwd v7.1.5: the skip tree (`if measured:` changed to `if False:`) gives `withheld x3` rc 2. Door N gives `null=graded tuya=withheld` rc 1. Door T gives `null=withheld tuya=graded` rc 1 (ev/controls.txt).
- RESULT detector mutants, scored with the body's command (fix rc 0 from cwd v7.1.5; v7.1.5 rc 1 from cwd fix; skip rc 2; doors rc 1). The unmutated detector passes. M-a to M-h are all killed, 8 of 8, and each fails on the arm the body names (ev/mutants.txt, ev/mutants/). One extra mutant of my own, M-i, survives; see Findings.
- Mutation proof (step 1): the diff adds no production line (`git diff --stat` shows only dev/, delivery and one closures.json entry). The diff-mutant step draws nothing, as the body says, because `mutant_run.py` skips `dev/`. The hand proof above stands in for it.
- Figures re-derived (ev/figures.txt, ev/figures2.txt):
  - 134 tags from `git tag --contains a63b576cd -l 'v*' --no-contains v7.1.6`, running v4.0.0 (2026-08-26) to v7.1.5 (2026-11-07), which is 73 days.
  - v2.8.0, the first tag containing `df7db8215`, is dated 2026-08-22: 78 days to 2026-11-08.
  - The name census at the merge base is 23.
  - `df7db8215` holds `observed_cop = modelled_cop * commanded / self._measured_power` and `ATTR_COP_MEASURED = "measured_cop"`.
  - `a63b576cd` is #50, v4.0.0, with "inherits every filter for free".
  - The citation `sweep-P5.md:37` and the D1 lines 10-11 quotes are verbatim at the merge base.
  - fold_ledger: `50 classes, 755 instances, 121 ..., 138 rca entries`, 0 violations.
  - closure select: `MODE: SCOPED -- 1 script(s) run, 32 scoped out`.
  - structure.py: `STRUCTURE RATCHET PASSED`.
- Not re-derived: that PR #11 merged "four minutes after opening, with no review"; #3297's 12.0 h, 12 commits, 39 files and +700/−146; the 2 to 3 min per name estimate (labelled an estimate in the body). I did not read them through the API.
- Untouched files: no `*_budgets.json`, `VERSION`, manifest, `RELEASE_NOTES.md` or `tests/golden` change in the three-dot diff. No claim files move, so step 4 has nothing to compare. The roles diff from the merge base to origin/main is empty.
- Closure classification: the new harness is in `tests/closures.json`. The code run's `tests / closures` passed and its `tests / fast` passed (entities included).
- Merge with main: `git merge-tree --write-tree origin/main 1623c5ade60f6b9023a7d613631b998f5cc39c4d` exits 0, with `LEDGER-MERGE: resolved` for `tests/closures.json` and `bugclasses.json`.
- Forward-carry (step 10): the roster at `a62e0a80a` holds the cwd-capture carry on R10-RCA-COP-UNMEASURED. The group goes `carries-open` (roster_edit HOLD_STAGE) rather than `done` while the carry is pending, so it stays a live destination. The docs carry goes to #3139. carry_audit at the head: 2 routed, 0 unrouted.
- CI at this head:
  - The code run 42511678981 concluded success. Its `gate` (128833446999, 19:16:48Z) and `pr-contract / pr-contract` (128833300805) both succeeded.
  - The only reds are the two edit-run gates, 128826363189 and 128826551028. Each log reads `FAIL run(s) [42511678981] at this head are still being judged; their gate decides`. That is the deferral, and the run it deferred to is green.
  - `merge_train.py classify` still prints `RED 1623c5ade60f6b9023a7d613631b998f5cc39c4d pending: none red: gate` rc 1 at 19:22Z (ev/classify2.txt). It takes the worst gate suite, and no gate-sweep has run since 12:22Z to re-judge the deferred reds.
  - Under the brief's GATE DEFERRAL rule I judge the head green. The train needs those edit gates re-run before GitHub's rollup reads green.
- Red checks (step 11): the body says no check had concluded when it was written. Every red since then is that deferral, so no gate red owes a root-cause answer.

## Findings

- Minor: the body's `## Head` still carries a stale line, "The head is `1b684dfbf...`", under the line naming `1623c5ade60f6b9023a7d613631b998f5cc39c4d`. The two trees are byte-identical, so every figure holds at this head.
  Carry: dismissed: wording only, tree identical
- Residual: my own mutant M-i survives the scored command: the provenance refusal's `return 3` turned to `pass`, with `os.chdir(root)` left in. The refusal cannot be reached while the change of directory runs before the imports, at every tree I measured. M-g and M-h already show the refusal firing and the capture it guards.
  Carry: dismissed: equivalent mutant behind os.chdir
- Follow-up: the cwd capture is wider than this detector. The body's enumerator returns 24 harnesses under `dev/audit/harnesses/` that import `tests/harness.py` and set sys.path with no os.chdir (ev/cwd_enum.txt). At least 8 of them take a root or tree argument, so they may grade the shell's tree.
  Carry: R10-RCA-COP-UNMEASURED

## Friction

none
