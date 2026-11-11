Fix review: merge 0437a8168e997e9ebc5b55897a0a96f7538969cc

bus-nonce: b6bb8714fd903aeed4d4870ce199b5e9

## Round

First review of the handoff r10-outside-diag-redact-location (group R10-OUTSIDE-DIAG-REDACT-LOCATION), head `0437a8168e997e9ebc5b55897a0a96f7538969cc`, against merge base `86953c6d99ecf7aa86c7bc9d57fec9a991daad07` (three-dot). `git diff $(merge-base)...origin/main -- dev/governance/roles/` is empty, so the role contract is current.

## Evidence

- No pull request exists yet, so there is no review packet, no check run to read and no CI to wait on. There is no red, so `## Red checks` owes nothing (`merge_train.py owed-reds`: tests / mutation, tests / typing, validate / validate-hacs; none ran).
- Head: `git ls-remote origin refs/heads/handoff/r10-outside-diag-redact-location` = `0437a8168e997e9ebc5b55897a0a96f7538969cc`, re-read before return (step 12); the body's `## Head` names the same SHA (step 7). ev/HEAD.txt.
- Merge with main: `git merge-tree --write-tree origin/main 0437a8168e997e9ebc5b55897a0a96f7538969cc` (origin/main `a7628041dc`) exit 0, tree `af573e4ecc`. No conflict, and no claim file is touched. ev/merge_tree.txt.
- Provenance: `54f7b20d6c` (Bankaifan) has the same patch-id as outside PR #3436's live head `1433484270` diffed against its own main base (`26b0f74b0d` both), so the author's change is kept whole and authorship is kept. `git log --format=%B` over both branch commits shows no Co-Authored-By or Claude-Session trailer. ev/provenance.txt.
- Mutation proof (step 1), rerun with my own driver script (ev/named.sh) and spec (ev/mutants.json, ev/mutants_feat_rest.json), `tools/audit/seat/mutant_run.py`. The body's four mutants reproduce exactly:
  - debug_collect: SURVIVED NULL, KILLED M1, KILLED M2, SURVIVED M3, KILLED M4 (in place, ev/mut_debug_collect.log)
  - features: SURVIVED NULL, SURVIVED M1, KILLED M2, SURVIVED M3, KILLED M4 (ev/mut_features_part1.log in place: NULL/M1/M2; ev/mut_features_part2.log copy-tree: NULL/M3/M4. The first in-place run hit the seat's 30-minute background limit after M2 and left the tree clean.)
  - entities: SURVIVED NULL, SURVIVED M1, KILLED M2, KILLED M3, KILLED M4 (in place, ev/mut_entities.log)
  - Every body mutant is killed by at least one named check, and NULL survives in every run.
- My own extra mutants: R5-value-pass-off (`removed = False`) KILLED by debug_collect, SURVIVED features and entities. R6-redact-only-solar-location KILLED by all three. R7-replay-public-top-only (`_public` drops only `solar_location`) SURVIVED all three, dispositioned under Findings.
- Failing test first (body arms), rerun on debug_collect with the head's tests: main's diagnostics.py+debugger.py gives `2 of 163 DEBUG COLLECT CHECKS FAILED` (the replay-half location check and the value-pass check); the author's gives `1 of 163` (the replay-half check, `"solar_location": {"latitude": 59.33 ...`). This is the hold-out leak the body describes. ev/arm_main_debug_collect.log, ev/arm_author_debug_collect.log. I did not rerun the entities and features arms; they are cited from the body.
- Null control: at the head `ALL 163 DEBUG COLLECT CHECKS PASSED`, `ALL 2704 ENTITY CHECKS PASSED`, `ALL 5222 FEATURE CHECKS PASSED` (ev/head_*.log). These include the token and entry-name checks.
- Structure (step 14): `tests/structure.py` gives `STRUCTURE RATCHET PASSED` at both the merge base and the head, and the `RESULT` lines are identical (diff rc 0). No metric moved and no budget changed. ev/struct_base.log, ev/struct_head.log.
- Architecture score: `score.py --diff <merge base>` gives `Architecture score: dS +0.0000 NULL`. ev/archscore.log.
- Claims and versions (steps 4 and 5): `env_drift.py --claims-only <merge base>` gives `claims hygiene ... ok`. VERSION, the manifest, RELEASE_NOTES.md, tests/golden, closures.json and closure.py are untouched (empty diff stat).
- Mutation-ledger removals: five pins are deleted. Each one's `old` line or function (`COORDINATE_PLACES`, `_coarsen`, the `removed = ... or (under in COORDINATE_KEYS ...)` line) is absent at the head: 0 grep hits at the head, 8 at the merge base and at origin/main. `_private_values`' surviving pins (`*.6a2e5977`, GUARD_OFF) remain. `guard_pins.py`: `ALL 61 GUARD PIN CHECKS PASSED`. Nothing was hand-removed to pass.
- Class (step 6): I reran the body's enumerator. Every location key reaching the download is either a keyed redaction (`TO_REDACT` covers `LOCATION_KEYS` at any depth) or in the replay half. In the replay half, `_public` drops it from entry data and options, the only callers being `replay_entities` and then `async_bundle`. State attributes are cut to `replay_doc.ATTRIBUTE_KEYS`, which holds no coordinate key, so the published `solar_irradiance` sensor's latitude/longitude attributes (sensor.py `attrs.update(diagnostics)`) cannot reach the replay. `tools/replay` does not call `replay_entities`, which confirms the body's claim that the on-instance export is unchanged.
- Scope: `closure.py select --diff <merge base>` at the head gives `MODE: SCOPED -- 29 script(s) run, 4 scoped out` (ev/closure_select.log). Besides the three above I ran 12 more at the head, all passing: block_duty, boost_drift_replay, config_flow_steps, edge, frontend, guard_pins, manual_plan, open_meteo, plan_view, solar_alignment, validate, wood_advisor (ev/extra_*.log). backtest, stress, optimality, card.mjs and card_drift.mjs, and the body's arch_score_head, deployment_shape, doc_claims, finite_boundary, golden, harness_headers and typing_ruler, were not rerun by me. They are left to the PR's gate.

## Findings

- Figure that does not re-derive: the body's `## Figures` names 12 scripts for `scope.run`. The same select at the same head and base prints 29 run (ev/closure_select.log), so the body under-reports the scope. Fifteen of the 17 unlisted are rerun green above. Carry: dismissed: the PR's own scoped gate re-derives and runs all 29 before merge; body wording only
- Figure that does not re-derive: the body's ledger control says the pattern matches 7 lines at origin/main; it matches 8 at both origin/main `a7628041dc` and the merge base (ev/provenance.txt). The conclusion (non-zero at main, zero at the head) holds. Carry: dismissed: off-by-one in a control count whose sign is the claim
- Surviving reviewer mutant R7-replay-public-top-only: narrowing `_public`'s drop to the `solar_location` key survives all three scripts. On today's configuration it is equivalent, because the entry's data/options carry `latitude`/`longitude` only nested under `solar_location`. Carry: dismissed: equivalent mutant on every entry shape config_flow writes today
- Surviving reviewer mutant R5-value-pass-off survives features and entities but is killed by debug_collect's R10-DIAG-REDACT checks, the value pass's own pin. Carry: dismissed: killed by the named check that owns the value pass
- Body friction confirmed: `refs/heads/handoff-wip/r10-outside-diag-redact-location` still points at `defaf622d6`, the commit with the trailers, and must be deleted by the orchestrator. Carry: dismissed: the body's own Friction line already routes it to the orchestrator at handoff
