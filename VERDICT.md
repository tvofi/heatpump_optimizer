Fix review: merge 7e8c2248e6892e3484d5724fdb0a92155aae5b4f

bus-nonce: 63099c44ccc5b090e3b23bd49be8c5af

## Summary

Round 1 of PR #3013 (HOTFIX R10-HOTFIX-AWAY-SETBACK), reviewed at head `7e8c2248e6892e3484d5724fdb0a92155aae5b4f` from a detached worktree, against merge base `a9ba3022e32178c5fb4376b4f333be88544ce94d`. The role contract has no diff between the merge base and origin/main. The fix makes `away.solve_bands` set back the weekend and holiday comfort pairs when they are configured. The finder's harness is red at the base and green at the head. Every mutant I planted is killed, the null controls hold, and the per-step comfort class is closed.

`away.py` is code-owned, so `main-protect-checks` requires tvofi's approving review at merge. This verdict flags that and does not block on it.

## Findings

- The probe's (c) is not settled by this PR: there is no state listener on `away_presence_entity`, so an away flag from a presence entity reaches the plan only at the next scheduled update. The fixer's dispatch brief (`dispatch/fixer-r10-hotfix-away-setback` at 71907df1f) says "Its finding is carried there", meaning R10-LIVESTATE. I found no mention of a presence listener at `design/r10-livestate` f589cc0c3 (`git grep -i presence`). The carry is therefore the orchestrator's to confirm or write into that stage's brief. It is not owed by this PR. The owner's live diagnostics show `away_presence_entity none`, so this path does not explain the live report. Carry: R10-LIVESTATE
- Recovery drops the whole setback (the harness `recovery` row equals `null_away_off`). Also, `coordinator._resolve_away` takes the recovery target from `get_comfort_temp(now.hour)` without `when`, so it ignores the weekend and holiday pair. Both are kept unchanged here on purpose. Carry: dismissed: the dispatch brief rules recovery a design question for tvofi, not a defect, and the PR keeps today's behaviour as the null control
- The owner's live symptom (heating slots while away) is not explained by this fix. In the reproduced house the defect raised the Saturday comfort target, not the slot count (harness: `extra space slots in this house: none` at both ends). The live cause is being pursued separately under `dispatch/fixer-r10-hotfix-away-live` (738969543: the live view shows `away_active false`). Carry: dismissed: owned by the separate R10 hotfix-away-live dispatch already issued, not by this PR

## Evidence

- RESULT harness-base (finder's harness `dev/audit/harnesses/r10_live_away_heating.py`, run at a9ba3022e): `arm=weekend ... comfort_sat=21.0`, `arm=weekend_flat ... comfort_sat=21.0`, `arm=holiday ... comfort_sat=21.0`, `VERDICT weekend/holiday comfort REPLACES the away target (Sat 21.0 / 21.0 vs 16.0)`. Red at the base. File: ev/harness-base.txt.
- RESULT harness-head (7e8c2248e): the same three rows read `comfort_sat=16.0`, and the verdict line reads `keeps the away target (Sat 16.0 / 16.0 vs 16.0)`. Every other row is identical to the base, including away, null_away_off, away_off_setpoint21, null_flat, indoor18, weekend_away_off and recovery, with their slots, kWh and DHW. File: ev/harness-head.txt. This reproduces the body's diff claim.
- The committed harness is byte-identical to the one embedded in the probe report at `handoff-body/r10-live-away-heating` aa6e5db30. Its sha1 is `822ccca27a2189754ee77e334e1e0544f8901191`, as the body states. It is the finder's harness, not the fixer's.
- RESULT features-head: `ALL 4607 FEATURE CHECKS PASSED`, rc=0. Both new checks report `ok`. File: ev/features-head-summary.txt. The count matches the body.
- RESULT mutant m1 (delete `**dict.fromkeys(config, target),`): killed. The existing away block's `_g8_sb_c["comfort_temp_day"]` raises KeyError, rc=1. With this line gone the day/night setback goes too, so an older check kills it before the new one runs. File: ev/mutant-m1-summary.txt.
- RESULT mutant m2 (drop the `is not None` filter): killed by `FAIL and RECOVERY ends it`, `1 of 4607 FEATURE CHECKS FAILED`. This confirms the body's claim, which it reasoned but did not mutant-run, that the None filter is pinned by the exact-dict comparison.
- RESULT mutant m3 (remove `holiday_comfort_night` from `_OPT_FIELDS`): killed by `FAIL away sets back the weekend and holiday comfort pairs too`, with holiday away reading `[16.0, 19.5]`. `1 of 4607 FEATURE CHECKS FAILED`. This matches the body's mutant table row.
- RESULT null controls, from my own script (ev/null-controls.py, run through the production `OptimizationConfig`, `solve_bands` and `replace`; ev/null-controls.txt):
  - With away off, a weekend Saturday reads (21.0, 19.5) at both base and head, identical to main.
  - Recovering reads (21.0, 19.5, target 21.0, min 19.0) at both ends, unchanged.
  - With away at 16, `target_temp` and `min_temp` are 16.0, which is min(configured, target).
  - With away at 22, `target_temp` stays 21.0 and `min_temp` stays 19.0, so the min() is kept. The comfort pairs read 22.0, the same semantics the base already applied to weekday day/night.
  - An unconfigured install returns no weekend or holiday band keys, and the fields stay None through `replace`.
- Class enumeration (fixer.md step 8, re-derived): `OptimizationConfig` holds exactly these temperature and comfort fields: target_temp, min_temp, max_temp, comfort_temp_day/night, comfort_temp_day/night_weekend, holiday_comfort_day/night. The solver reads per-step comfort only through `get_comfort_temp` and `get_temp_bounds` (optimizer.py, `_build_comfort_bounds`), and those reach `_comfort_pair` plus min_temp and max_temp.
  - All 8 non-ceiling fields are set back at the head.
  - max_temp is the ceiling and buys no heat.
  - The hour and date fields only choose between values that now all equal the away target.
  - The body's 15-field table matches. No seam is open.
- Merge: `git merge-tree --write-tree origin/main 7e8c2248e` exits 0 against origin/main 437f1ba9b, so there is no conflict. File: ev/merge-tree.txt. The packet's stale-tree note ("lacks origin/main 437f1ba9b") does not affect this, because the tree merges clean.
- VERSION, manifest.json, RELEASE_NOTES.md, tests/golden and both claim files are untouched in the three-dot diff.
- Head: the body names the authored code head 3ec79824c plus the main merge 8c009d866 and a record-row commit. The head at verdict time is still 7e8c2248e (ev/head-at-post.txt).
- CI at 7e8c2248e, read from the check-runs API:
  - No check concluded red.
  - Green: arch-score, budget-raise-gate, closure-scope, briefs, typing, arch-instrument, browser, mutation, nightly-status, delivery-status, env-matrix, policy-docs, wave-script, hassfest, validate-hacs, codeql actions and JS, and the first prelude.
  - Still in progress at verdict time: tests / fast (3.14), tests / coverage, tests / closures, governance / instrument-self-tests, codeql / Analyze (python), and the second prelude.
  - With no red, no root-cause answer is owed (step 11). The merge train should still see these finish green.
  - The green `tests / mutation` lane ran in 32 s. I did not read its log for a possible INCONCLUSIVE; my own three mutants above stand in for it.
- Figures I did not re-derive, and which are cited from the body only: the scoped-gate counts (`22 script(s) run, 11 scoped out`), `NO UNCLAIMED DRIFT: 56 scenario(s)`, the structure ratchet pass and `Architecture score: dS +0.0000`. CI's arch-score and budget-raise-gate are green at this head. The policy is to cite heavy runs, not re-run them.
- Step 14: `tests/closures.json` gains exactly one INERT-READS line, for the new harness. It is earned by the new file, and no budget moved.
- Step 15: the fix stays inside `away.py`, which owns the setback. The body's rejected alternative (a) would have put away state into the optimizer config, and rejecting it is sound. There is no architecture breach.
