Fix review: merge b72efecda93d11758d4883335c1a2579ad76d353

bus-nonce: 25b487edd799d698950ddeb0e2455168

## Scope

Later round (owner ruling 2026-11-09): the delta `git diff 9c92e927bf4b75d84420ce1d2ad4906be116d06b b72efecda93d11758d4883335c1a2579ad76d353`, a merge resolution only. The previous verdict at 9c92e927 was `merge`. This is the seventh review of #3297; this round re-reviews a merge resolution, not a new cut of the code. `review_carry.py 9c92e927 b72efec` prints `FRESH-REVIEW` because 1002809e is not the automatic merge of its parents, so this verdict reviews that resolution delta alone (fix-review.md step 12).

## Evidence

- Merge shape: b72efec = 18aa1b86 + origin/main 699f4d9; 18aa1b86 = 9c92e927 + 1002809e; 1002809e = 9c92e927 + main b0762725 ("resolve five conflicts"). For b72efec and 18aa1b86, `git merge-tree --write-tree <p1> <p2>` yields exactly the commit's own tree (b8aaddfa, 1aacd0dd), so neither merge changed anything beyond the automatic merge. The only hand resolution is 1002809e.
- 1002809e against the automatic merge tree ef725200 of 9c92e927 and b0762725 (`git diff --stat`): only the five conflicted files differ, matching the body's list. The resolutions are:
  - `tests/golden/config_flow.json`: a union, keeping main's `heat_curve_displace_entity` and the branch's `heat_meter_sees_dhw`. Re-check at the head: `PYTHONPATH=tests/hastub python3 tests/golden.py --only config_flow` prints `ALL 1 GOLDEN SCENARIOS UNCHANGED` (ev/golden_config_flow.txt).
  - `tests/golden/claimed_drift.txt`: the driver printed `MERGE-CLAIM: refused` for scenario `config_flow`. The resolution keeps the branch's six lines and drops main's R10-GENERIC-HEAT-CURVE `config_flow` line, as the driver's instruction and `claim-files.md` direct. Re-check: `env_drift.py --claims-only 699f4d9` prints `claims hygiene: 699f4d9ef40f4eaf62397e81ae000680e417baf3 ok` (ev/claims_hygiene.txt).
  - `option_doc_coverage.py`: the base has 205/238, the branch adds 3, main adds 3, giving 211/244. Re-derived by running the script at the head: `RESULT option_fields_rendered=211`, `RESULT option_schema_keys_rendered=244`, `option_fields_undocumented=0` (ev/odc_run.txt).
  - `claims.json` and `claims.md` C125: the base has 46, the branch adds 2, main adds 1, giving 49. Re-derived: `claims.py` at the head regenerates both files and `git status --short` prints nothing, so 49 is what the instrument writes; `claims_false=0` (ev/claims_run.txt).
- Neither parent lost a change: `diff <(git diff -U0 01782a1e 9c92e927 | grep '^[+-]') <(git diff -U0 b0762725 1002809e | grep '^[+-]')` differs only in the three re-measured counters and main's dropped claim line (ev/branch_content_control.txt). In the per-file numstat for the branch side, only `claimed_drift.txt` differs (6/0 -> 6/1); for the main side, only `claimed_drift.txt` (main's +1 line, dropped) (ev/numstat_*.txt). This matches the body's control exactly.
- Whether production risk widens the review: main's incoming side touches 10 production files this branch also changed (ev/overlap_prod.txt). All of them merged automatically. None of the +/- lines in `git diff 9c92e927 b72efec -- custom_components/heatpump_optimizer/*.py` names a symbol of the reviewed COP seam (`cop_measured`, `cop_sample`, `_fold_cop_evidence`, `_measured_cop`, `_observe_cop_health`, `_COP_BASELINE_KEY`, `machine_score`, `cop_observability`, `InstallCapability`, `probe_install`, `_estimated`, the meter-source and `heat_meter_sees_dhw` options, `_waiting_for`): 0 lines (ev/seam_touch.txt). The review was therefore not widened.
- Merges with main: `git merge-tree --write-tree origin/main b72efec` exits 0 at main 55bccf1c (ev/merge_tree_main.txt).
- `VERSION`, the manifest and the RELEASE_NOTES heading: the three-dot diff against the merge base prints 0 lines (ev/version_check.txt). No `*_budgets.json` is touched.
- The PR body names b72efec as head. The remote branch is still b72efec at post time (ev/head_at_post.txt).
- CI: `merge_train.py classify b72efec --pr 3297` returned `GREEN b72efecda93d11758d4883335c1a2579ad76d353 pending: none red: none` (rc=0, 08:47:24Z; ev/classify.txt, ev/classify.log). No required red at this head. The required set is what `merge_train.py owed-reds` lists (ev/owed_reds.txt), and none of its contexts is red at this head, so no red is owed an answer.
- Previous verdict's first follow-up (the edit-run `gate` deferral that held classify at RED): it no longer applies at this head, where classify reads GREEN.
- Not re-run: the mutation proof and the finder's harness. The production code is unchanged from the verdicted lines (see the seam check above), and CI's `tests / mutation` is cited, not re-run.

## Findings

- Follow-up: the unpinned `and self.cop_electric()` conjunct in `InstallCapability.cop_measured` is still unpinned at this head. It is carried from the previous verdict and was not re-run, because this merge-only delta leaves its code unchanged. Carry: #201
