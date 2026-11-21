Fix review: merge 5c8ad0805b99d3be04b221e92cd40ad2c6506d66

bus-nonce: 7ff06ef09f57bb12f614e6fe09fa1e37
pending-ci: gate

## Summary

Round 1 (first review, full scope). The diff at head 5c8ad0805b, three-dot against merge base e698fc8ac3 (origin/main at the time of review), is `.github/workflows/governance.yml` (env-matrix `timeout-minutes` 10 -> 26, plus a five-line comment stating the rule) and the delivery row `dev/programme/delivery/3830.md`. No `custom_components/` line, no test line, no budget, closure, claim or golden file changes.

## Evidence

- Merge: `git merge-tree --write-tree origin/main 5c8ad0805b` exits 0 (tree 9527b4d089), with no conflict. The head's merge base is the current origin/main e698fc8ac3, so the head is not behind main. (ev/local-checks.txt)
- Role contract: `git diff $(merge-base)...origin/main -- dev/governance/roles/` is empty, so the role contract is current.
- VERSION, the manifest and RELEASE_NOTES.md are untouched by the three-dot diff (step 5).
- Mutation proof (step 1): the fix is one value, and its mutant is the base value 10. GitHub's job record shows the mutant failing. I read job 135314988141 (main, 2026-11-19T03:23Z): conclusion `cancelled`, 03:23:42 to 03:33:52 = 610 s, cancelled in step 6, "Require each declared environment shape to produce its declared outcome". That matches the body. I did not re-run the gate or the mutation table, which CI's heavy runs cover (step 11).
- Null control (step 3): job 130932618696 (main, 2026-11-12T02:38Z) has conclusion `success` and took 285 s (02:38:32 to 02:43:17), matching the body.
- Tree bytes, re-derived with `git ls-tree -r -l <c> | awk '{s+=$4} END{print s}'`: 133197618 at 6e100ef698, 140675332 at 8f39313a44, 140333720 at 54cb721164, 265550206 at 8fa10e00ce and 279136158 at 42809bec34. All match the body. Bytes under `dev/audit/rounds/round11` grow by 136795536 - 40639 = 136754897 between 8f39313a44 and 42809bec34, which matches exactly. `states.json` is 35419796 bytes. At the current base e698fc8ac3 the tree is 297568050 bytes, so it has grown further since the body was written, which strengthens the case for the cap rather than weakening it.
- The first-parent log of the matrix programs since 2026-11-12 lists #3688, #3668, #3631 and #3514, matching the body. 8fa10e00ce is the #3723 merge at 2026-11-19T03:20:07Z.
- Arithmetic: 2 x 513 x 1.48 / 60 = 25.31, which rounds up to 26. 513 x 1.48 = 759.2, about 760. 27.8 / 18.8 = 1.479. 600 / 513 = 1.17. All consistent.
- Figures I could not re-derive (step 8): the run counts (11 of 29 after the landing, 262 successes and 0 timeouts of 270 before), p50/p95/max, the lint-step means, the pull-request tallies and the local profile timings. They come from the fixer's out-of-tree harnesses, cited by sha1, which I did not have. I spot-checked two of the named jobs, and both matched. These figures are the fixer's, not verified by this seat.
- Other consumers of the cap: no step in env-matrix sets its own `timeout-minutes`. The new 26 min stays under merge_train's `CODE_RUN_DEADLINE_SECONDS` (150 min, from ci.yml's longest job), and that self-test reads ci.yml, not governance.yml. `tools/ci/gate.py`'s `GATE_WAIT_MAX_S = 720` is as the body states. No test pins the env-matrix value: `tests/entities.py`'s `timeout-minutes: 10` literal is the `graders-head-copy` job in tests.yml.
- Class (step 6): the body names one seam, this job's cap. Its sibling causes, the per-symbol whole-tree grep and the train's timeout re-run arm, are dispositioned in the body to proposal P-R11-94 under the tooling freeze. No enumeration rule is owed for a one-seam class.
- Head (steps 7 and 12): the body names 5c8ad0805b99d3be04b221e92cd40ad2c6506d66, which is the head I measured.
- Red checks: there are no reds at this head. Every required run was still queued at review time. owed-reds are in ev/owed-reds.txt.
- CI: `merge_train.py classify` kept printing WAIT with a `gate` pending (ev/classify.txt). The PR's own env-matrix duration, which the body calls the first uncensored measurement at the new cap, was not yet available at review.

## Findings

- Note: harness: no committed harness (step 9). The body's collectors (`collect.sh`, `collect_lint.sh`, `derive_cap.py`, `windows.py`, `collect_pr.sh`, `analyse.py`, `prof/spy.cjs`) are the fixer's own instruments. They sit out of the tree in the seat's directory, cited by sha1, so no seat can re-run them, and the run-count figures stay unverified by this seat. The underlying data is GitHub's own job record, which any seat can re-read by the job ids the body cites, and two of those ids matched. The change is one CI constant whose correctness the next main runs will show, so I judge the missing harness a paperwork note here, not a block. Carry: dismissed: read-only API collectors over GitHub's job record for a CI-constant hotfix; the body routes the cap's re-derivation from uncensored durations to proposal P-R11-94 at round-end triage
