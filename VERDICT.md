Fix review: merge 6f91e6d05450ba32fe1cfa102b00a9763235d412

bus-nonce: 39febcd175ca57354333bc0fd80f1e8c

Fix review round 4 of #2819 (R10-ARCH-SHAPES). This is the round-4 re-cut, the split, so `fixer.md` owes a re-cut and not a repair. Cloud reviewer seat, claim `rev-2819-39febcd1`. I measured head `6f91e6d05450ba32fe1cfa102b00a9763235d412` from detached worktrees on Linux x86_64 (CI venv, Python 3.14.7). `git ls-remote` showed it was still `refs/heads/fix/r10-arch-shapes-pr` and `refs/pull/2819/head` when I wrote this. The merge base with origin/main is `c78df2b86b5ec51d631eb0ed18bbac8feecd166a`, which is origin/main itself. `git diff $(git merge-base origin/main HEAD)...origin/main -- dev/governance/roles/` is empty, so the contract is current.

## Findings

- (low, instrument) `dev/audit/harnesses/r10_band_census.py` fails open when it observes no classifier calls. It reads its power series only through a spy on `optimizer.classify_space_steps`. If the spy is never installed, or never called (for example, a later refactor imports the classifier by name or renames it), every scenario reads 0 with `susceptible=False` and `rc=0`. In the mutant run (`ev/band_census_mutants.txt`, "spy not installed"), `valve_upper_direct_slab` went 5/5/5/5 -> 0/0/0/0 and `away_setback` went 2 -> 0, with `RESULT ... susceptible=0 failures=0` and exit 0. R10-996-RUNNER-CLAIMS uses this census as its control input, so a zero-call capture should count as a failure, not as a zero. Carry: R10-996-RUNNER-CLAIMS
- (low, evidence for the next stage) The census's susceptible set depends on the host, and the body's 15-name set is one host's reading. On this Linux container it reads `RESULT scenarios=50 susceptible=15 failures=0`. The count is the same as the body's, but the set is different:
  - names here that are not in the body: away_setback, everything_on, fuse_guard, shoulder_two_zone, winter_two_zone_dhw;
  - names in the body (macOS) that are not here: cool_rainy_summer, dhw_cold_tank, flat_prices, horizon_48h, valve_storage_flat_prices.

  The union over the two hosts is 20 scenarios. That is still a lower bound, because neither host covers the runners' readings from round 3. The claim grammar has to be designed against the union of every host's census, not against one 15-name list. Carry: R10-996-RUNNER-CLAIMS
- (medium, owed before merge) `tests / mutation` is red on this head, as predicted: 71 unpinned sites added by the diff, and `ci_predict.py` reproduces 71 here (`ev/ci_predict.txt`). The 12 `tests / mutation-pins` shards were still in progress when I wrote this. The pin run, plus a killing check or a `survivor_triage` entry for every survivor, is owed before merge, as the body's `## Red checks` says. Carry: R10-ARCH-SHAPES
- (low, roster) The roster entry for R10-ARCH-SHAPES-CLASSIFIER (`handoff/audit-r10-roster` at `6073f166858f11ab5b0557f805e09b9f1aa3b803`) lists `files` as `thermal_model.py` and `tests/golden/claimed_drift.txt`. The parked commit `996b54cf15ea3c7693383165ae2f080d2e04971b` touches `optimizer.py`, `tests/entities.py` and `tests/features.py`. The entry's file and hot-file lists should name those, so that serialisation against other `optimizer.py` groups holds. Carry: R10-ARCH-SHAPES-CLASSIFIER

## Evidence

- **Check 1: claim files.** Blob SHAs at the head equal origin/main's:
  - `tests/golden/claimed_drift.txt`: `2e2d65ac394ea4513950fabff4fb1603eb38aa94` on both sides;
  - `tests/golden/card_claimed_drift.txt`: `3bc2cf0e0ddb7d1d3a732a8c9857362d1a6c7cc5` on both sides.

  The three-dot diff of `tests/golden/` is empty (`ev/basic_checks.txt`). `env_drift.py --all c78df2b86` at the head on this host prints `NO UNCLAIMED DRIFT: 56 scenario(s)` and `NO STALE FIXTURE: 56`, rc=0 (`ev/env_drift_head.txt`). CI `tests / fast (3.14)` on this head concluded **success** at 2026-10-26T00:01:51Z: `30 TEST SCRIPT(S) PASSED; 3 SCOPED OUT`, including `env_drift.py --all c78df2b86...` (388 s) and `card_drift.mjs`. The round-3 claim-drift block is closed on the runner.
- **Check 2: no half-arm.** `git grep` at the head finds no match anywhere in the tree for `channel_heating_draw`, `_heating_draws` or "idle to the reason classifiers". The only `R10-ARCH-SHAPES-CLASSIFIER` mentions are the two `tests/entities.py` dispositions (lines 4086 and 4090), which name the parked group (`ev/split_checks.txt`). `classify_space_steps` and `classify_dhw_steps` keep `threshold: float = CHANNEL_ACTIVE_KW`, which has the same value as the base's `0.05`, so they behave as at the base. The parked ref `park/r10-arch-shapes-classifier` is `996b54cf1` on `a1d56b66f`. It touches `optimizer.py`, `tests/entities.py` and `tests/features.py`, which matches the body. Unmutated `tests/features.py` at the head prints `ALL 4410 FEATURE CHECKS PASSED`, rc=0 (`ev/features_head.txt`), which is 4411 less the moved check. CI `tests/entities.py` and `tests/features.py` are green in `tests / fast`. No test, mutant or ledger pin still names the removed helpers.
- **Check 3: band census harness.** The sha1 is `b2b3a938866e6923748552125afda64a0d9ce599`, as the body states. It is classified in `tests/closures.json:3582`. `tests/harness_headers.py` prints `ALL 112 HARNESS HEADER CHECKS PASSED`, both here and in CI.
  - The full run at the head gives `RESULT scenarios=50 susceptible=15 failures=0`, rc=0 (`ev/band_census_head.txt`; the set is under Findings).
  - **The harness's own stated control holds exactly on this host.** At eps 0, the band set (10 scenarios) equals the set `env_drift.py --all` moves at the parked arm `996b54cf1` (2 DRIFT: away_setback and valve_storage_small_tank; 8 MAY-DRIFT), with output `IDENTICAL 10 10` (`ev/env_drift_parked_arm.txt`). This also reproduces the round-2 and round-3 container reading of the arm. So the harness measures what the arm moves.
  - **Mutants** (`ev/band_census_mutants.txt`, run on valve_upper_direct_slab and away_setback; control 5/5/5/5 and 2/0/0/0):
    - band upper edge set to 0, which empties the band: both read 0. The harness moves.
    - spy not installed: both read 0 with rc=0. This is the fail-open finding.
    - DHW-channel term dropped: no change on these two scenarios, so that arm is not exercised by them. I did not test it on a scenario with DHW band steps.
- **Check 4: carries.** Both of the body's `## Forward-carry` destinations exist on the roster at `handoff/audit-r10-roster` `6073f166858f11ab5b0557f805e09b9f1aa3b803` (`ev/roster_entries.txt`):
  - R10-ARCH-SHAPES-CLASSIFIER: its brief names the parked branch, waits on R10-996-RUNNER-CLAIMS, and says "Every carry #2819's body routes here is part of this brief".
  - R10-996-RUNNER-CLAIMS: its brief cites the #2819 census by sha1 as its measured problem, with controls stated as preconditions.

  The mutation pin carry stays with this group before merge (Findings). The CI `tests / fast` item is settled green at this head, so it carries nothing further. No carry in the body is dismissed without a reason.
- **Mutation proof, re-run here** (`ev/mutants_small.txt`, separate worktree at the head):
  - `const.finite_float` with the bool arm dropped: `tests/finite_boundary.py` `1 of 108 FAILED`, `[wrong={'True': 1.0, 'False': 0.0}]`;
  - `quiet_windows._within_nameplate` changed to `return kw`: `tests/manual_plan.py` `2 of 132 FAILED`, the two checks the body names;
  - controls: `ALL 108` and `ALL 132` pass.

  Both mutants are killed. Round 3 re-ran the features.py mutants on the then-head, and those lines are unchanged in this delta, so I did not repeat them.
- **`ci_predict.py --base origin/main`**: "71 unpinned site(s)", "no closures, fast, wave-script or instrument red predicted against c78df2b86b5e" (`ev/ci_predict.txt`). This matches the body.
- **Ratchets.** `tests/structure_budgets.json` only moves down: class_excess_loc 18102 -> 18090, duplication_copies 16 -> 15, functions_cc_over_15 30 -> 29, max_class_loc 8311 -> 8297. `tests/coverage_budgets.json` pragmas go 12 -> 10. Nothing is raised, and `budget-raise-gate` is green.
- **Release stamps.** `VERSION`, the manifest and `RELEASE_NOTES.md` have an empty three-dot diff.
- **Delivery row.** `dev/programme/delivery/2819.md` is in the three-dot diff (+1 line, "open").
- **Merge.** `git merge-tree --write-tree origin/main 6f91e6d05` exits rc=0 with tree `f7cc51e557aef9f2ed593b103d3485f27e3f426a` and no conflict.
- **CI on this head** (check-runs API, `ev/check_runs.txt`).
  - Green: `tests / fast (3.14)`, typing, replay, browser, arch-instrument, arch-score, briefs, closure-scope, env-matrix, instrument-self-tests, policy-docs, wave-script, nightly-status, budget-raise-gate, hassfest and validate-hacs.
  - Red:
    - `tests / mutation`: the predicted unpinned-sites red, which the body names and answers.
    - `governance / delivery-status`: OVERDUE on #2812, #2813, #2712, #2807, #2804, #2798, #2799, #2780, #2749, #2775, #2797, #2762 and #2795, not on #2819. Its log says "This check is NOT a required context and a red here blocks no merge", so it is not this PR's red.
  - Still running or queued: closures, coverage, mutation-pins 1-12, graders-head-copy, lane-proofs, codeql-python and prelude. Step 11's posting condition has not concluded for those, and no root-cause block is raised.
- **Head SHA in the body.** `## Head` names `6f91e6d05450ba32fe1cfa102b00a9763235d412`, the head I measured.
- **Body figures not re-derived here.** I did not re-take these:
  - the macOS band positions (step 26 at 0.071929 kW, step 153 at 0.097477 kW);
  - the archscore dS +1.8325 (round 3 reproduced it, the code is unchanged, and CI arch-score is green);
  - the D7/D8 finder-harness figures, which round 3 measured on code this delta does not touch.
- **Dispatch note.** The brief snapshot asks for the verdict to be posted as a PR comment. The seat payload says not to post and to return the verdict on the probe ref for the orchestrator's relay, so I followed the payload and posted nothing.
