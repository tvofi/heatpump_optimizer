Fix review: blocked 45d083123c6f45482dae00bbef4b82bf6e50bc04 body-figure: the ## Head line says the head merges origin/main 50af6174f, but its main parent is 0825aee641c8 (886 commits later); the claim-file resolution itself is correct

bus-nonce: 8d6f69e91b30d93aa360e010c67894f8

## Round

Delta review of #2753 at the new head, after a prior merge verdict at bd1a5f31c7a25282420285197412882f4a40a162. Scope as briefed: only the merge of origin/main and its hand-resolved tests/golden/claimed_drift.txt. The fix itself was not re-reviewed.

## Block

The one line this pass added to the body, the first paragraph of `## Head`, says "`45d083123c6f...` merges origin/main `50af6174f` into this PR's previous head `bd1a5f31c7a2...`". That is false. `git log -1 --format='%H %P' 45d083123c6f45482dae00bbef4b82bf6e50bc04` gives parents bd1a5f31c7a25282420285197412882f4a40a162 and 0825aee641c8afb1e67be2a6af9d07e9c9dec9fa (main at #2780). 50af6174f is #2686 from 2026-10-24, 886 commits behind the merged parent. It is the merge base a shallow clone reports, not the commit that was merged. The head SHA the body names is right (step 7). The merged-main SHA is a figure in the body that does not re-derive (step 8). Later seats read it as the merge that brought in R10-LEARNER-ETA's claims, and 50af6174f does not hold them. Repair, body only: replace `50af6174f` with `0825aee64` in that sentence. Nothing else needs to change. Everything below holds at this head, so a re-review after the repair only has to check that sentence.

## Findings

- Body `## Head` names the wrong origin/main commit for the merge at 45d083123c6f (50af6174f; the actual parent is 0825aee641c8). This is the block above, and the PR settles it with a body edit before the merge. Carry: dismissed: blocking defect of this PR's own body, repaired on this PR before merge, nothing for a later stage

## Evidence

- (1) Three-way check on tests/golden/claimed_drift.txt (ev/claimed_drift_threeway.txt). The merge commit is 45d083123c6f, with parents PR bd1a5f31c7a2 and main 0825aee641c8, and merge base b89fea13e99f.
  - Main's side (base -> 0825aee6): dropped the five R10-SCORES lines (`coord_all_features|coord_dhw|coord_grid_fee|coord_minimal|coord_two_zone  # R10-SCORES: envelope 58.3 -> null (learner unconverged), reasons and model_restart added`). Added the five R10-LEARNER-ETA lines for the same fixtures (`# R10-LEARNER-ETA: data.learner_progress and the model status sensor's learner_progress added (24 leaves each)`). Added the 9-line `# R10-LEARNER-ETA (#2260): ...` comment block.
  - The PR's side (base -> bd1a5f31) added one line: `config_flow # R10 thermal power option (#1955 fold e): the heat_pump_thermal_power_entity field is published on the meters group; keys added, no value moved`.
  - At the head: main -> head adds exactly that one config_flow line, and PR -> head is exactly main's change, byte for byte.
  - So the result has every line main added, the PR's one line, and none of the five R10-SCORES claim lines, which only main removed. Nothing was invented, and every direction word is as each side wrote it. The `# R10-SCORES (#2258): ...` explanatory comment that both sides kept is still present.
- The driver's refusal reproduces: `git merge-tree --write-tree bd1a5f31 0825aee6` prints `MERGE-CLAIM: refused tests/golden/claimed_drift.txt` ("both sides rewrote the claim list") and `LEDGER-MERGE: resolved tests/closures.json` (ev/merge_tree.txt). The refusal comes from the claim-list rewrite on both sides. It is not a defect in the authored work.
- (2) VERSION at the head is 7.0.4. `# claims-for: 7.0.4` is in tests/golden/claimed_drift.txt (line 57) and tests/golden/card_claimed_drift.txt (line 22) (ev/claims_for.txt).
- (3) `python3 tests/env_drift.py` in a detached worktree at the head gives rc=0, `NO UNCLAIMED DRIFT: 5 scenario(s) checked against origin/main` and `NO STALE FIXTURE`. There is no claimed-and-may-drift refusal. config_flow is reported "unjudged ... not captured in this mode", as expected without --all (ev/env_drift.txt). I did not re-run `--all` here; CI's env-matrix lane does that, and it passed.
- (4) `git diff --stat bd1a5f31 45d08312` covers the same 67 paths as `git diff --stat b89fea13 0825aee6` (main's own commits). The added and removed line content matches file by file, with no DIFFERS line. Going the other way, `0825aee6 -> 45d08312` matches `b89fea13 -> bd1a5f31` file by file. That is the PR's original 36 files, 840 insertions and 106 deletions, the same set as the PR API's changed_files 36 (ev/diff_stat.txt). The three-dot diff against current origin/main shows the same 36 paths. Nothing outside the PR's original change set changed.
- tests/golden/card_claimed_drift.txt was not touched by the PR, by the merge, or between bd1a5f31 and the head (all three diffs empty).
- `git merge-tree --write-tree origin/main 45d08312` at origin/main bc52ad2af1d0 gives rc=0 and tree e1e8dedce95e: it merges clean against current main.
- CI on 45d083123c6f45482dae00bbef4b82bf6e50bc04 (check-runs API, ev/ci_checkruns.txt): 36 runs and no failure. Seven were still in progress when I read them: tests / fast (3.14), tests / closures, tests / mutation, tests / coverage, governance / instrument-self-tests, codeql python and one prelude. Those seven have no conclusion yet and are not verified here.
- The body's head SHA `45d083123c6f45482dae00bbef4b82bf6e50bc04` equals the head I measured. The body's "no code changed" is true: the merge's only change beyond main's own commits is the claim-file line.
