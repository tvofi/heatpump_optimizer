Fix review: blocked 46e7faa93fdf786a39090aed84a4f91ec11599b6 mutation-vacuous: tools/ci/prelude.py machinery_rowblind reading ev instead of scoped survives the closure

bus-nonce: 96993dd62117e15f50d39617f0842ad9

Round 1 (first review of #3847; no --reviewed-head).

## Block

- Survivor M7 (`ev/M7.diff`): in `tools/ci/prelude.py` `outputs`, the changed line `out["machinery_rowblind"] = "true" if scoped != "pull_request" ...` reverted to read `ev` (the pre-change line). `python3 tools/ci/prelude.py --self-test` prints `89 checks, 0 failed` and `PYTHONPATH=tests/hastub python3 tests/entities.py`, the only other script in `tests/closures.json` that reaches `tools/ci/prelude.py`, prints `ALL 2740 ENTITY CHECKS PASSED` (`ev/entities_M7_summary.txt`, `ev/entities_M7.log`). The body says a verified PR dispatch scopes "`machinery`, `machinery_rowblind` and `selftests` exactly as for that PR's `pull_request` run". The CI-2 positive arm and its five null arms read `legs`, `machinery` and `selftests`, but none reads `machinery_rowblind`, so that part of the claim is not pinned. The mutant fails safe: arch-instrument still runs on dispatches. The test is still missing. Remedy: add `machinery_rowblind` to the CI-2 positive tuple (expect `false` for the doc-only diff) and to each null arm (expect `true`), then re-show that M7 is killed.

## Evidence

- Head reviewed: `46e7faa93fdf786a39090aed84a4f91ec11599b6` (`ev/HEAD.txt`), which is the PR's live head and the head the body names. Merge base: `40e513eea4ca3dacad882b7a1a1366b6b188f777`. Under `git diff $(git merge-base origin/main HEAD)...origin/main -- dev/governance/roles/`, nothing is printed, so the role contract is current.
- CI: `merge_train.py classify 46e7faa93fdf786a39090aed84a4f91ec11599b6 --pr 3847` exits 0 and prints `GREEN 46e7faa93fdf786a39090aed84a4f91ec11599b6 pending: none red: none` (`ev/classify.txt`).
- Merges with main: `git merge-tree --write-tree origin/main HEAD` prints `b839c74641c7381270be292887eb8e39e079ea0d` and exits 0 (`ev/head_checks.txt`).
- VERSION, the manifest version, RELEASE_NOTES.md and both claim files are untouched: a three-dot diff over them prints 0 lines.
- The body's four prelude mutants (M1 to M4) are all killed by the named CI-2 arms (`ev/prelude_mutants.txt`). The reviewer's own mutants M5 (`base_sha` not replaced), M6 (`machinery` reads `ev`), M8 (`legs` read `ev`), M9 (`dispatch_diff` always None) and M10 (the base ref ignored) are also killed. M7 survives (see Block).
- Workflow pins: the same entities.py run passes every CI-1, CI-5, CI-7 and CI-17 check at this head, null controls included, with only the prelude mutated. The reviewer did not hand-plant workflow mutants beyond the body's own plants.
- Figures, re-derived at the current merge base:
  - `prelude self-test: 89 checks, 0 failed` matches the body.
  - `python3 tests/structure.py` prints `STRUCTURE RATCHET PASSED`.
  - `python3 tests/comment_ratchet.py --base origin/main` prints `comment_ratchet: OK` with long_units 2301 -> 2301. The body's 2303 -> 2303 was taken against the older base `6fdc15354f`.
  - entities prints 2740 checks. The body's 2735 was taken at the older base. Both differences come from the move in main's base, not from this diff.
  - The body's "15 steps" is confirmed: 14 `setup-python` steps carry `cache: pip` across `tests.yml`, `governance.yml`, `kernel-points.yml` and `nightly.yml`, plus the composite `nightly-ha` action.
- CI-17 cache glob: every cached `setup-python` step follows an `actions/checkout` at the workspace root, with no `path:` and no sparse checkout. The composite action is used only after a checkout. So `tests/requirements-*.txt` matches in every job, including the jobs CI skipped at this head: mutation-pins, replay, kernel-points, the nightly jobs and governance's regret-oracle.
- CI-5: `ci.yml` triggers `push` only on `branches: [main]`, so the `CI-main` group never mixes another branch's push. The workflow-level `cancel_superseded.py main` arm is wired into no workflow, so no automated canceller fights the group. A coalesced main parent makes the push arm's coverage key (`HEAD^1`) miss, which means a full measurement: a cost, not a correctness change.
- CI-1, autofix: `approved_head` is set only when the approved CI run's id appears in `hits`, the earlier poll at the pushed SHA. A CI run that is created between that poll and the `held` listing is approved but not counted, so the head is also dispatched. This fails toward running (two runs, the pre-change behaviour) and is not a defect.
- Owed red: `tests / fast (3.14)`, at the earlier head `547a71778069`, is in the `owed-reds` set. The body's `## Red checks` answers it and names the cheaper detector (`tests/comment_ratchet.py`).
- Prepr was not re-run, as the dispatch's owner rule says: the fixer's receipt covers the code.
- Closing self-audit: `carry_audit.py check` over this verdict prints `CARRY-AUDIT: 0 finding item(s): 0 routed, 0 unrouted, 0 bad destination(s)`, rc 0. The body was audited separately by the packet render at this head, with the same 0 items; this run used only the body's `## Forward-carry` and `## Friction` sections, both `none`.
