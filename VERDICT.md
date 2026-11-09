Fix review: blocked 00d12cad0f12bb8eb7da1010a720f7576fd4a552 carry-missing: not carried to the stress memory pass's readers, whose traced-arm flake stays open on Linux at both ends

bus-nonce: 47eb1e26563a45aa4503d18481cd6425

## Block

The body's first `## Forward-carry` bullet says the traced arm of `tests/stress.py`'s memory pass still bumps by about +1.8 MiB on Linux 3.14 at this head. It also says *"This changes how #3297 and any later stress red on 3.14 must be read: a traced bump of about 1.8 MiB is not evidence against the diff."* That is a finding that changes how a later stage must work: every fixer and reviewer who reads a stress red on 3.14. Yet the bullet routes itself `dismissed: ... no later stage's procedure changes`, which contradicts its own text. `finding-propagation.md` requires that such a finding reach the reader's own brief or role contract before the producing PR merges. It is in this PR's body only (step 10: `carry-missing`).

My measurement shows the residual is real, and that on Linux the finder's harness does not move under the fix. This box is a 4-core Linux x86_64 container running venv-ci CPython 3.14.7. I ran `PYTHONPATH=tests/hastub python3 tests/stress.py` three times per tree, head and base running in parallel pairs. Traced MiB per probe, in the order heavy_old/shoulder, winter/cycle, winter/pv+cycle, typical_slab/winter, winter_extreme/1z/dhw, typical_slab/shoulder (records 3.5 / 3.5 / 3.5 / 3.4 / 3.4 / 1.8):
- head run 1: 5.2 3.3 3.3 3.3 3.3 2.1 — PASSED (5.2 is x1.49, just inside x1.5)
- head run 2: 3.3 3.3 3.3 5.1 5.1 3.9 — `1 of 114 STRESS CHECKS FAILED` (typical_slab/shoulder 3.9 vs 1.8)
- head run 3: 5.2 5.2 3.3 5.1 3.3 2.1 — PASSED
- base run 1: 3.5 3.5 3.5 3.4 3.4 2.2 — PASSED
- base run 2: 3.5 3.5 3.5 3.4 3.4 2.2 — PASSED
- base run 3: 5.3 3.5 5.3 3.4 3.4 2.2 — `1 of 113 STRESS CHECKS FAILED`

Red runs: head 1 of 3, base 1 of 3. Bumped probes: head 7 of 18, base 2 of 18. On Linux the defect the PR is named for, a stress memory red that does not belong to the diff, is not shown closed. The body's Linux mechanism is stated as read from threadpoolctl's source ("no Linux box was available to run it"). I confirmed that on Linux neither the unfixed nor the fixed `_scoped_minimize` imports anything inside the window (ev/linux-inwindow-imports.txt). So the new in-window import check cannot fire on Linux, and only the features pin guards the fix there.

To unblock, carry the precondition: a traced bump of about 1.8 MiB on 3.14 Linux is not, alone, evidence against a diff, and this table shows it is open at both ends. Put it where the stress reader looks (the stress/D9 stage's roster brief or a carry file, or the role contract), with this table's control (base beside head, same box, interleaved) and a re-measure instruction. Or state the Linux residual's own destination. The code change itself is not blocked on merit; see Evidence.

## Findings

- The traced-arm flake of `tests/stress.py`'s memory pass is open on Linux 3.14 at origin/main and at this head: 1 of 3 runs red each, 2 of 18 and 7 of 18 probes bumped. It is unidentified and owes a destination where a stress-red reader looks. Carry: R10-HOTFIX-STRESS-MEM-PEAK
- The new `solve_window_imports` precondition check reads `[]` on Linux with the unfixed optimizer too (ev/linux-inwindow-imports.txt). It is an off-Linux detector only, and the body's Root-cause countermeasure should say so where it claims the probe "notices its own precondition". Carry: R10-HOTFIX-STRESS-MEM-PEAK

## Evidence

- Head reviewed: 00d12cad0f12bb8eb7da1010a720f7576fd4a552 (ev/HEAD.txt). It has the same tree as 6286dfef5e (`git diff --stat` empty); base fdc8d21ada.
- Merge: `git merge-tree --write-tree origin/main 00d12cad` exit 0, tree ae9bdb5262, origin/main 19865e5a86. No conflict.
- Role contract: `git diff <merge-base>...origin/main -- dev/governance/roles/` touches only proposal-triage.md, so fix-review.md is current.
- Mutation proof (step 1), `PYTHONPATH=tests/hastub python3 tests/features.py` in three worktrees at the head:
  - mutA (base optimizer.py): `FAIL the BLAS thread pin reuses ... constructions=4 ..., _blas_threads=NoneType`, then AttributeError, exit 1.
  - mutB (`_blas_threads.limit` replaced by a per-call `threadpool_limits`): `FAIL ... constructions=4 ..., _blas_threads=ThreadpoolController`, `1 of 4979 FEATURE CHECKS FAILED`.
  - mutC (GUARD_OFF, `if False:`): `FAIL without threadpoolctl ... AttributeError("'NoneType' object has no attribute 'limit'")`, `1 of 4979 FEATURE CHECKS FAILED`.
  - All three killed (ev/features-mut*.log).
- The pin is effective and scoped: inside `_scoped_minimize` threadpool_info reads num_threads {(1, 1)}, and after the call [4, 4] (ev/pin-effective.txt). The import-time controller sees the same two openblas libraries a fresh scan sees. `ThreadpoolController.limit` exists in the pinned threadpoolctl 3.7.0 (manifest `>=3.5.0`).
- The replay re-record (step 14) was re-derived. `derive_cost_classes(cost_draws(), "synthetic-dhw-only.json")` gives ref47 2.7713. Without job 128866186676's rows it gives 3.3424, so the movement is earned by the new draw alone. With ref47 at 3.3424, `draw_offenders` names job 128866186676 (`budget 3.342 cannot see a 2x cycle; re-record 2.193`). At the head it names none. Old null (125051003592 to the ref53 border less 1, i.e. ref47): names nothing. New null (into ref40): named (`clean cpu_ratio 1.444: budget 3.987`). `controls()` `control:cycle_cost:draws` True. See ev/replay-derive.txt.
- Class rule `git grep -n "tracemalloc.start"`: 9 windows, matching the body (ev/class-rule.txt). Production `threadpool_limits`/`ThreadpoolController` sites in custom_components: 1, the changed one (ev/threadpool-sites.txt).
- Untouched: VERSION, the manifest, RELEASE_NOTES.md, tests/golden/claimed_drift.txt and card_claimed_drift.txt (empty three-dot diff). I did not run env_drift.py --all; golden is cited to CI.
- Whole-solve CPU in my runs: head median 0.972x of the baseline beside it, base 1.019x (stress-wt.log, stress-wtbase.log).
- Body figures I could not re-derive here: the macOS figures (3.47 / 5.31 / 1.87 / 3.29, 199 / 2076 KiB, churn 1.83 MiB steps). Their scratch instruments live out of tree and are cited by sha1 only.
- CI: `merge_train.py classify 00d12cad... --pr 3349` exited 1: `RED 00d12cad0f12bb8eb7da1010a720f7576fd4a552 pending: none red: gate` (ev/ci-classify.txt).
  - The latest `gate`, job 128928635369, concluded at 01:25:11Z. Its log reads `FAIL codeql / Analyze (python): cancelled (this run)` (ev/job-128928635369.log): a cancelled analysis, not a test.
  - Every test lane passed: `tests / fast (3.14)` (128914863009, including `ok python3 tests/stress.py (252s)`, ev/job-128914863009.log), `tests / replay`, `tests / mutation`, `tests / coverage` and `coverage-ratchet`.
  - `pr-contract / pr-contract` passed at 01:22:20Z, before that gate turned red. So under step 11 no contract run has checked the body against this red yet, and I issue no root-cause verdict on it. The body's `## Red checks` answers the reds at 0f84b0fe8b, not this one. CI's green stress run is one more sample of the same flake: green on CI, 1 of 3 red here.
