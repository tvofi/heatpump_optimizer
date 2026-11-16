Fix review: merge c0847381f73ec0cdfed571b5df6bc244955bf459

bus-nonce: 5d23a25cf454b880304e9aa84675b2ae
pending-ci: tests / closures, tests / coverage, governance / instrument-self-tests

Round: first review of #3669 (no prior reviewed head). Scope per owner ruling 2026-11-16, workaround 5: the landing only; the evaluation's judgements (approved by evaluation review round 4, 83dc948818) were not re-reviewed.

Note: body-claim: the body and 8d2bc61ac1's message say `here.parents[5]` "resolved one directory above the root"; at the head path `dev/audit/rounds/round11/evaluation/tally.py` `parents[5]` is the repository root (ev/parents5.txt: has manifest True), and tally.py at c04cef7fca runs rc 0. The fix is still required: `tests/harness_headers.py` refuses the depth seam whatever it resolves to.

## Findings

- Note: body-claim: the PR body and 8d2bc61ac1 describe `parents[5]` in tally.py as resolving above the repository root; it resolves to the root, so the change answers harness_headers' depth-seam refusal, not a wrong path. No later stage depends on the sentence. Carry: dismissed: description only, the code change stands on the harness_headers refusal

## Evidence

- Head reviewed: c0847381f73ec0cdfed571b5df6bc244955bf459 (ev/HEAD.txt); base 6f422812d5d8b918beace0283419c153f6df66ce; `git diff <base>...origin/main -- dev/governance/roles/` empty.
- History: `git merge-base --is-ancestor` holds for 83dc948818 (the approved revision) and c04cef7fca (eval/r11 tip, = origin/eval/r11) against the head.
- Files: `git diff c04cef7fca <head>` over `dev/audit/yardstick/round11` and `dev/audit/rounds/round11/evaluation` touches only tally.py (+15/-2); the file sets under both paths are identical. The three-dot diff adds those nine paths plus `dev/programme/delivery/3669.md`, nothing else. The older c6ce415b77 copy landed at caf50a30cf is fully superseded at the head.
- tally.py: the inlined `repo_root` matches `tools/audit/repo_root.py` (`harness_headers.inline_scan()` rc 0 at head; `tests/harness_headers.py` ALL 115 PASSED with tests/hastub). Mutant A, tally.py reverted to c04cef7fca: inline_scan rc 1, `FAIL depth seams: ...tally.py:13: repo = here.parents[5]`. Mutant B, walk body altered (`for cand in here.parents:`): inline_scan rc 1, `FAIL python copies=187 differ=[...tally.py]`. Both restored. `tally.py` at head rc 0, prints `CARDS 48 ... decided=48`.
- Classification: at head `closure.orphan_files()` is `[]`, and `closure.is_inert` is true for all ten changed paths (ev/classification.txt). `tests/closures.json`, `tests/closure.py`, VERSION, manifest, RELEASE_NOTES.md and tests/golden untouched (ev/untouched.txt).
- check_scopes: `tools/audit/check_scopes.py --repo . --round 11` at base: `FAIL start evaluation round=11: 1 gap(s)` (`EVALUATION.json is not in the tree`); at head: `14 gap(s), 12 card(s) beside the finders`, every gap `card ... is accepted and not merged at this ref`, no review-sha gap. Control (my own, in place of the body's unpushed 55148fa033): the head tree committed on main with no merge (5739e98e27, local only) gives `15 gap(s)` incl. `review sha '83dc9488...' is not a commit in the ref's history`; the merge removes exactly that gap. Body figures 14 and the base refusal re-derived.
- Merge: `git merge-tree --write-tree origin/main <head>` rc 0 (ev/merge-tree.txt).
- Red checks: `merge_train.py owed-reds` prints tests / coverage-ratchet, tests / fast (3.14), tests / mutation, tests / typing, validate / validate-hacs. The body answers `tests / fast (3.14)` at c5ac4df684 (harness_headers depth seam; cheaper detector none ran, cost stated) and names `INERT READS UNDER-APPROXIMATED` on `tests / closures` for the autofix job (ci-autofix.md). `tests / nightly-status` red at this head is outside the owed set: neither answered nor a block.
- CI: `merge_train.py classify <head> --pr 3669` printed `WAIT c0847381f73ec0cdfed571b5df6bc244955bf459 pending: gate red: none` on every run 16:37-17:10 UTC (ev/classify-log.txt). Live check runs at 17:03 UTC: owed set tests / fast (3.14), tests / mutation, tests / typing, validate / validate-hacs success; tests / coverage, tests / closures, governance / instrument-self-tests in progress; tests / coverage-ratchet not yet reported. Hence the pending-ci line; the relay posts only over green at this head.
- Head re-read before return: origin `fix/r11-start-evaluation-land` still at c0847381f73ec0cdfed571b5df6bc244955bf459.
