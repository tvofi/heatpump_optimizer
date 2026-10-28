Fix review: blocked e380bebfa2b4a529b857da251d3e26619a1fe846 harness: finder-harness-misreported: the body says the R10-ARCH-SHAPES band census exists on no origin ref and cannot be cited, but dev/audit/harnesses/r10_band_census.py (blob 893c39573714a99fb151ec76cbdf0ec40b878675, commit 648f88d9e) is on fix/r10-arch-shapes-pr and handoff/r10-arch-shapes. The brief's sha1 citation is missing, and the forward-carry hands that false finding to R10-ARCH-SHAPES

bus-nonce: c3a9ad2b44080d28c40a806b66d57f38

Round 1. Reviewed head `e380bebfa2b4a529b857da251d3e26619a1fe846`, detached worktree. `fix/r10-996-runner-claims` on origin was still that SHA at 02:20Z. Role contract: `dev/governance/roles/` has no diff between the merge base and origin/main `7d2056970`, so it is current.

## Block

- **The finder's harness is misreported.** The body's third `## Forward-carry` bullet says "No ref on origin carries it: `git grep -l band_census` over `fix/r10-arch-shapes-pr`, `handoff/r10-arch-shapes` … returns nothing. So no sha1 can be cited." That is false at this head's time:
  - `git grep -l band_census origin/fix/r10-arch-shapes-pr` returns `dev/audit/harnesses/r10_band_census.py` and `tests/closures.json`. The same holds on `origin/handoff/r10-arch-shapes`.
  - The file was added by `648f88d9e` (2026-10-25T22:21Z, "harness: the D8-s1-01 band census … (evidence for R10-996-RUNNER-CLAIMS)"). Blob `893c39573714a99fb151ec76cbdf0ec40b878675`.
  - #996 comment 6404201979 (22:22Z, the comment the body itself cites in `## Problem`) names it: "Band census: `dev/audit/harnesses/r10_band_census.py` in #2819".
  - The group brief says to cite its sha1. The body cites none, measures only with the fixer's own `r10_shape_claim_controls.sh` and the replayed readings, and carries "no sha1 can be cited" to R10-ARCH-SHAPES as a finding. Under `finding-propagation.md`, a false precondition would land in that stage's brief.
- **What clears it is body-only; no code needs to change.**
  - Replace the third forward-carry bullet with the harness path, blob `893c3957…` and commit `648f88d9e`, and drop the R10-ARCH-SHAPES carry.
  - Cite the census in `## Figures` as the finder's harness. This review's run of it, below, may be quoted with its RESULT lines.
- The substance holds under the finder's harness (see Evidence). A re-review after a body-only fix carries every number below unchanged.

## Findings

- **Surviving mutants on the path-wildcard grammar.** Each mutant was one line of `tests/env_drift.py` at the head, run against the PR's 13 shape-claim pins (harness `ev/sc_pins.py` and `ev/mutate.py`, my own instrument and disclosed as such). Three survive:
  - R13: `[*]` compiled to `.*` instead of `\[\d+\]`.
  - R14: a path `*` compiled to `.*`, so it crosses `.` and `[`, instead of `[^.\[\]]*`.
  - R17: `_SHAPE_LINE.fullmatch` changed to `.match`, so trailing tokens after the to-set are silently ignored.

  No pin uses a `*` inside a path. Nothing pins `[*]` against a non-index suffix. Nothing pins a line with trailing garbage. R13 and R14 widen what a shape excuses (fail-open), and the grammar is documented in `claim-files.md` as "`*` matches within one key". Owed: three pins. (1) A `*`-in-key path that must not cross a dot. (2) `space_reasons[*]` that must not match `space_reasons_x[0]` or `space_reasons[0].k`. (3) A trailing-token line refused by `shape_claim_error`. Carry: R10-996-RUNNER-CLAIMS
- **Equivalent mutant, recorded:** R10 drops the `path.startswith(prefix)` guard in `shaped_leaves`. `_diff_leaves` always prefixes the path with `<fixture>.`, so the guard is unreachable. Carry: dismissed: an equivalent mutant; the guard is unreachable from `judge_drift`
- **`## Red checks` is stale.** It says "none on CI yet". The head's runs have since concluded, with `governance / delivery-status` red. That check is not this PR's: its log lists 18 OVERDUE rows, all of them merged PRs on main (#2821 … #2795), and says "This check is NOT a required context and a red here blocks no merge". This diff's only delivery input is its own new row, `dev/programme/delivery/2843.md`, which reads `open` and is not among the overdue rows. No answer is owed under `defect-root-cause.md`. Refresh the section when the body is edited. Carry: R10-996-RUNNER-CLAIMS
- **The class-rule listing is incomplete.** `## Class seams` lists four `tools/` callers. `git grep` also finds `tools/audit/seat/merge_train.py:4326` and `tools/pr/app_approve.sh:216`, and the `claims-autofix` job in `.github/workflows/tests.yml` calls `env_drift.apply_inherited_claims`. I read all three: they are path-level or line-generic, never parse a claim key, and so are sound with a `shape:` line. No seam is open, but the listing should name them. Carry: R10-996-RUNNER-CLAIMS

## Evidence

- **Finder's harness, run by me.** `r10_band_census.py` (blob `893c3957…`), run in a worktree at the parked arm `996b54cf1`, this container (numeric_probe `37fadb5234b8`, numpy_build `1d6b22fc9d3d`):
  - `RESULT scenarios=50 susceptible=15 failures=0`
  - `SUSCEPTIBLE away_setback direct_flow_carnot everything_on fuse_guard shoulder_two_zone tariff_plus_two_zone valve_storage valve_storage_low_target valve_storage_small_tank valve_storage_smart_write valve_upper_direct_slab winter_two_zone_dhw wood_coil wood_two_tank wood_two_tank_smart_write`
  - File: `ev/finder_band_census_at_996b54cf1.txt`.
- **The census's own population, judged by the head's matcher.** `ev/nudge_capture.py` uses the census's `_nudged_make`. I captured 19 scenarios (the 15 susceptible plus `dhw_cold_tank`, `horizon_48h`, `valve_storage_flat_prices`, `cool_rainy_summer` from the other hosts' readings) at the four census nudges {0, 1e-15, 1e-12, 1e-9}, at both the arm `996b54cf1` and its base `a1d56b66f`. Each cell went through the head's `shaped_leaves` with the PR's shape line (`ev/judge_nudge.py`):
  - `RESULT cells=76 moved_cells=38 shape_hit_cells=38 loose_leaves=0`.
  - Every leaf the arm moves under any nudge on this host is in the shape. That includes non-may-drift `valve_storage_low_target` at 1e-12 and 1e-9, which moves here only under a nudge.
  - It is a second host-like reading beyond the PR's four replayed readings. File: `ev/nudge_judge.txt`.
- **Real-capture controls, re-run at the head** (`r10_shape_claim_controls.sh`, sha1 `0a7f16ae4109e472446962233e6086e8470e2c5d`, matching the body). Results: `RESULT after_rc=0`, `RESULT narrow_rc=1`, `RESULT null_rc=1`.
  - after: `SHAPED away_setback: 4 leaves`, `SHAPED valve_storage_small_tank: 1 leaves`.
  - null: `STALE claim for shape: …` and `SHAPE CLAIM MATCHED NOTHING`.
  - These match the body. Files: `ev/controls_*`.
- **Mutation proof on the real driver.** I deleted `claimed_hits.extend(sorted(shape_hits))` in a worktree copy of the head and re-ran the controls harness, which runs real `env_drift.py --all`. Result: `RESULT after_rc=1` (from 0), with `1 STALE CLAIM(S)` and `SHAPE CLAIM MATCHED NOTHING`. The check goes red. Files: `ev/realdriver_mutant_*`.
- **Mutation proof on the pins.** These are my 17 mutants, not the body's M1–M9. 13 are killed: path fullmatch, `old not in tos`, `new in tos`, from-set test, isinstance, `matched |= hits`, `shape_hits |= matched`, `claimed_hits.extend`, SHAPED-arm-excuses-loose, both-ways raise, literal regex, the `shape_claim_error` wiring in `main()`, and the shape branch in `runner_conditional_error`. Survivors are under Findings. I did not re-run the body's M1–M9 through the full `tests/entities.py`. File: `ev/mutants_pins.txt`.
- **Fail closed, read in the code.**
  - A value leaf, the reverse pair, another reason pair, another path, a move inside the to-set and a non-string from are each refused (the pins pass at the head).
  - Malformed, both-ways, keyless-path, float and wildcard-target lines are refused before capture in both `main()` paths.
  - A may-drift fixture's judged leaves are judged on `diffs`, not on `loose`, so a shape excuses nothing in a may-drift fixture.
- **Claimed and may-drift at once.** A shape key never equals a fixture name, and `may_drift_error` is unchanged. `env_drift.py --claims-only` at the head: `claims hygiene: origin/main ok`.
- **Claim files.** `tests/golden/claimed_drift.txt` and `card_claimed_drift.txt` are byte-identical to the merge base in the three-dot diff. The PR claims nothing.
- **Policy.** The body declares the policy change under mandate 6329234399 and owes the owner's approving review. `node tools/policy/rules_sync.mjs --check`: `RULES-SYNC ok`. `policy_lint.mjs`: `TOTAL: 0 error(s) across 50 policy file(s)`. `claim-files.md` is 53 lines and 2385 bytes, matching the body.
- **Cheap figures re-derived at the head; each matches the body.**
  - `ALL 117 closure shrink pins PASSED`
  - `ALL 112 HARNESS HEADER CHECKS PASSED`
  - `STRUCTURE RATCHET PASSED`
  - `Architecture score: dS +0.0000 NULL` (vs `7d2056970`)
  - File: `ev/cheap_checks.txt`.
- **Not re-derived by me:** the full `tests/entities.py` count (`2 of 2454`) and the scoped-gate mode line. CI's heavy runs are cited instead: `tests / fast (3.14)` success, `tests / closures` success, `tests / coverage` success.
- **Merge.** `git merge-tree --write-tree origin/main e380bebfa…` exits 0 with tree `42ed81f3d57e…` against origin/main `7d2056970`. No `MERGE-CLAIM` line was printed (no claim-file conflict). `VERSION`, the manifest and `RELEASE_NOTES.md` are untouched. The delivery row `dev/programme/delivery/2843.md` is in the three-dot diff. File: `ev/merge_tree_and_diff.txt`.
- **#996.** The decision is recorded as comment 6406191050 ("Decision on the claim grammar … closes the grammar question"). The body's "Issue #996's claim-grammar decision closes here" contains no GitHub closing keyword before `#996`, so it auto-closes nothing. #996 itself has been closed since 2026-09-20.
- **CI on the head** (check-runs API, 02:20Z):
  - Concluded success: fast (3.14), closures, coverage, browser, typing, mutation, arch-instrument, closure-scope, briefs, nightly-status, graders-head-copy, coverage-ratchet, lane-proofs, env-matrix, instrument-self-tests, policy-docs, wave-script, budget-raise-gate, arch-score, hassfest, validate-hacs, and codeql actions and javascript.
  - Red: `governance / delivery-status`, main's overdue rows; it is not a required check and does not block.
  - Still in progress: `codeql / Analyze (python)` and one `prelude` job (run 40256340326).
  - No `pr-contract` run is listed on this head.
