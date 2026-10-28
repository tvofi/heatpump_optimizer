Fix review: blocked 718ed364dfac4d2d1193502058c4adcf01c386cf class-open: tools/policy/rules_sync.mjs, fragments_sync.mjs, codeowners_gap.py and policy_lint.mjs --hooks are pinned graders the arm does not run and the body does not disposition

bus-nonce: 70859e600ae8db942bcad5e2c3a4435b

## Block

The class the record names (`dev/audit/rca/R10-RCA-PREPR-HEAD-GRADERS.md` sections 2 and 6): a pinned grader that the branch edits is graded by CI with the base's copy. The record says the old arm "reached one grader of four", so it treats the population as four graders. It derives that population from the measured instances. It never enumerates it from the pinned jobs.

I enumerated it myself. The rule: each program a pinned job (`policy-docs`, `env-matrix`, `wave-script`) runs whose file that job restores from the base (`agreement_py.restore_specs` plus `covers` at this head). The output is in `ev/class-enumeration.txt`. It returns these seams, which are not in `GRADERS` and are not dispositioned in the body or the record:

- `tools/policy/rules_sync.mjs --check` (policy-docs, governance.yml:158)
- `tools/policy/fragments_sync.mjs` (policy-docs, :188)
- `dev/audit/rounds/round6/D11/fix/codeowners_gap.py --check` (policy-docs, :169)
- `policy_lint.mjs --hooks` (policy-docs, :197). The CORPUS arm is keyed on this file but runs only the default mode, so a refusal that only `--hooks` makes under the base's copy is predicted green.
- `agreement.mjs --self-test` (wave-script, :1213). The agreement arm runs only the `--py-json` lane.

Under fix-review.md step 6, each seam is class-open. Two repairs are open to the fixer: add the seam to `GRADERS` (or to the mode list of an existing grader), or disposition it in the body and the record. A measured zero instances in round 10, together with a cost test, would be a disposition. Silence is not.

This is round 1.

## Findings

- Surviving mutant M7: I removed `"env-matrix"` from CORPUS's reds tuple in `GRADERS`, and `ci_predict.py --self-test` still reports 0 failed (`ev/mutant-M7.txt`, `ev/mutant-M7.diff`). The body's claim that CORPUS is reported on policy-docs and env-matrix is tested only on the policy-docs half. The plant row checks only `policy-docs`. Carry: R10-RCA-PREPR-HEAD-GRADERS
- Body figure is off by one. The body says "126 rca entries before this one". `fold_ledger.py check` reports 125 rca entries at origin/main `beb570c81` and at the branch point `eab04d0eb`, and 126 at this head, which includes this record (`ev/fold_ledger-eab04d0eb.txt`). Carry: R10-RCA-PREPR-HEAD-GRADERS
- Instrument defect, not this PR's. `review_packet.py render` refused `host-path` on `dev/audit/rca/R10-RCA-PREPR-HEAD-GRADERS.md:4` and wrote no packet. The cause is `ref_privacy._leaks`'s `home-directory` test, a bare substring match of the host's home. On this cloud seat `HOME=/root`, which matches inside `dev/governance/roles/root-cause.md`. The same line under a `/Users/someone` identity returns `[]`. Any cloud seat whose home is `/root` gets this refusal on every diff that cites `roles/root-cause.md`. The fix is a path-segment boundary after the home. Carry: O1

## Evidence

- Head reviewed: `718ed364dfac4d2d1193502058c4adcf01c386cf` (`ev/HEAD.txt`). `git ls-remote` shows the branch still at this head when the verdict was written. Merge base is `beb570c81`, which equals origin/main. `git diff merge-base...origin/main -- dev/governance/roles/` is empty, so the contract is current.
- Review packet: not rendered. The refusal was `host-path` (see Findings), and `host-path` writes no packet. I did not work around it. Checks were read live instead.
- `git merge-tree --write-tree origin/main 718ed364dfac4d2d1193502058c4adcf01c386cf`: rc 0, tree `9a9e0b52` (`ev/merge-tree.txt`). It merges cleanly.
- Self-test at head: `ci_predict self-test: 0 failed` in 8 m 26 s (`ev/selftest.txt`).
- RESULT mutation proof. Each mutant ran `--self-test` from its own worktree at the head:
  - M1 (graders arm dropped from `predict`): 1 failed, the #2916 row.
  - M2 (pathspec restore in `ci_tree_run` deleted): 3 failed, the same three rows the body names.
  - M3 (REFUSED prediction dropped): 1 failed, the #2916 row.
  - M4 (FIELD COVERAGE keyed on its whole closure): 1 failed, "and not by policy_lint.mjs".
  - M1–M4 match the body's table exactly. I did not re-run M5; the body states it as equivalent and kept.
  - My own M6 (CORPUS keyed on its own file, not its closure): 1 failed, the counts.mjs row.
  - M7 survived (see Findings).
- RESULT both ends, using the record's `demo.sh` against `f008c2b75` (#2916 pre-fix) on base `eab04d0eb`:
  - This head's predictor: rc 1, CORPUS REFUSED on policy-docs and env-matrix with the `[named-docs] tools/audit/seat/beatd_shims/git` line (`ev/demo-f008.txt`).
  - Main's predictor, all arms: rc 0, "no closures, fast, wave-script or instrument red predicted" (`ev/demo-f008-mainpredictor.txt`). This is the blind spot reproduced.
  - Null control `c991d64cd` plus a comment keying the arm: rc 0 (`ev/demo-c991-comment.txt`).
  - The predictor prints its base as `71fe1f7fcaea`, which is `merge-base(f008c2b75, eab04d0eb)`. The arm grades against the tip `eab04d0eb`.
  - Times on this seat: 68 s and 72 s, against the body's 26 s and 34 s. Seven self-tests were running in parallel at the time, so the body's timings are not re-derived here.
- Figures:
  - 543 first-parent merges since 2026-10-14 on origin/main: re-derived.
  - Not re-derived: the 70 restored-path PRs, the 15/10/7 key hits, the cost-test seconds, and the six fixer-round durations.
- Untouched: `VERSION`, the manifest, `RELEASE_NOTES.md`, `tests/golden/`, `*budgets*.json`, `tests/closures.json` and `tests/closure.py` have no diff against the merge base. No claim file moved, so step 4 is not applicable.
- CI on this head, check-runs API, read at about 19:16Z:
  - Success: policy-docs, env-matrix, wave-script, briefs, delivery-status, nightly-status, mutation, closure-scope, arch-score, budget-raise-gate, hassfest, validate-hacs, typing, browser, arch-instrument, codeql js and actions.
  - `governance / instrument-self-tests` concluded **cancelled**, not failure.
  - Still in progress: `tests / closures`, `tests / coverage`, `tests / fast (3.14)`, `codeql / Analyze (python)`.
  - No `pr-contract` run was listed yet.
  - No check is red, so step 11 has nothing to answer at this read. The block above does not depend on CI.
- Forward-carry: the body says none, and the record's proposed `gate-scoping.md` line is stated as needing the owner's approval. Nothing to open.
