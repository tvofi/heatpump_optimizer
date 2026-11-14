Fix review: merge 3fa750ea3861bf623ea3ff58e8e514321c511b52

bus-nonce: 85b5d71c88c04113f0ddeabdc8d1a33a
pending-ci: gate

## Summary

Round 2, delta review over reviewed head 6295f868a4314316f5e12c72fa2d16ead4895d35. Measured at head 3fa750ea3861bf623ea3ff58e8e514321c511b52 (a merge of the authored head b4617aa636 with the delivery-row commit 7312f605ee; `git diff b4617aa636 3fa750ea38` touches only dev/programme/delivery/3568.md). The delta is docs plus a test (tests/doc_claims.py `check_duty_switch_claims`) plus a delivery record. It changes no production code, so the review does not widen (fix-review.md step 12). All three block items from round 1 are resolved.

## Findings

none

## Evidence

- Block 1 (lost heat in one direction only): resolved. docs/configuration.md now says "For a switch from hot water to heating it also expects the median measured off time as heat not delivered ...; a switch the other way is priced but costs no heat". docs/how-it-works.md now says "for a switch from hot water to heating it also counts the off time as heat not delivered". Both match `duty_legs.lost_share` (custom_components/heatpump_optimizer/duty_legs.py:161), which reads index 0 = `dhw_space`.
- Block 2 (the cold-tank exemption needs a step that heats the tank): resolved. The on/off row reads "unless the step heats the tank and the tank needs heat now". This matches supply_hold.py:156 `not (step_duty(inp.plan, now) in ("dhw", "both") and tank_reason(inp))`.
- Block 3 (null control): resolved. The `git grep -c -E` command with `min\(a, b\) / p_max` added prints nothing at e23124ff6e. At 3fa750ea38 it prints README.md:1, docs/configuration.md:3 and docs/how-it-works.md:1, as the body says. The pattern occurs 0 times in main's how-it-works.md, so the how-it-works count comes from the added paragraph. ev/checks.txt.
- New sentences in the delta, checked against executable code:
  - "counts only some of the switches ... the compressor running, the new duty asking for heat and the plan keeping that duty": duty_switch.py:299-300 (`running`, `ctx.target_demand`, `ctx.plan_stays`, plus `_heated` and `void_cause`; "among" marks the list as a subset). target_demand and plan_stays are set at pump_arbiter.py:1549-1550.
  - "a switch a person's own mode change explains is not counted": `explained = ... ctx.mode_written_at != ep.at` voids the episode (duty_switch.py:341-344).
  - "(not on a combi store)": optimizer.py:354 returns the incumbent on `opt.model.params.dhw_store.combi`.
- Mutation proof (each change restored afterwards; ev/checks.txt):
  - M1, both pages reverted to 6295f868a4: 3 of 356 checks FAILED (both lost-heat checks and the on/off row).
  - M2, `lost_share` reading index 1: 2 of 356 FAILED, naming "heating to hot water", so the direction is read from the code.
  - M3, `_ends_soon` returning `not tank_reason(inp)`: 1 of 356 FAILED, [space=False dhw=False].
  - Restored: ALL 356 checks PASSED, rc 0 (ev/doc_claims_head.txt). The in-check null controls (the pre-fix sentences verbatim) pass.
- Re-derived figures:
  - doc_claims: 356 checks (round 1 had 348; 8 added).
  - `--markers --user`: 0 user-doc marker(s), 0 due.
  - STRUCTURE RATCHET PASSED.
  - `closure.py select`: MODE: SCOPED -- 6 script(s) run, 27 scoped out.
- Not re-derived: the local per-script results for entities, harness_headers, plan_view, md_tables and card_drift. I cite CI for these, not my own runs.
- Merge with main: `git merge-tree --write-tree origin/main 3fa750ea38` gives rc=0, tree a9a4c44e2e. origin/main is 50373173d4, so the head is behind main but merges cleanly.
- Role contract is current: `git diff mb...origin/main -- dev/governance/roles/` is empty.
- VERSION, manifest.json and RELEASE_NOTES.md are untouched. The claim files are untouched. No golden fixture is in the diff.
- Body `## Head` is 3fa750ea38 (it merges b4617aa636), the same head I measured.
- Body `## Red checks` still reads "no pull request exists". That is stale wording from before the PR was opened. CI state at this head is below.
- CI: `merge_train.py classify 3fa750ea38 --pr 3568` printed `WAIT 3fa750ea3861bf623ea3ff58e8e514321c511b52 pending: gate red: none` on every run from 00:05 to 00:30 UTC (ev/classify_poll.txt), so I am returning with `pending-ci: gate`. The digest's `gate` failure (job 132240621821, 23:40) was superseded by gate job 132254567225, success at 00:15. pr-contract / pr-contract succeeded at 00:15. A newer workflow run (43532992520, started 00:16) was still in progress when I stopped. No required check reads red now, so no `## Red checks` answer is owed.
- Round: 2 of the fix-review sequence for this group.
