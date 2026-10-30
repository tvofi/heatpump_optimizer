Fix review: blocked ddf75aaf8651c502794de257bbc76c044282f102 ci-red: tests / mutation is red on two added unpinned sites, pump_arbiter.py:1195 CMP_BOUND and :1222 GUARD_OFF, which both survive tests/features.py at this head, so the body's left-to-mutation-autofix disposition cannot clear them

bus-nonce: eb46adc353be3bb6b9c8bc1ae428724e

## Block

Round: this is the review of the round-4 head (merge delta fd6103038..ddf75aaf8651c502794de257bbc76c044282f102, three-dot against origin/main aced25893). review_carry.py prints FRESH-REVIEW: the delta carries branch-only commits f841c6f7e, 0a3077976, 1a7150482 and 5affc1af8.

`tests / mutation` (check run 123981124883) concluded `failure` at this head. Its log reads `MUTATION TABLE REFUSED -- 3618 unpinned site(s) against 3622 at the ratchet base aced25893..., 2 of them added by this diff`. The two added sites are:
- `ADDED UNPINNED custom_components/heatpump_optimizer/pump_arbiter.py:1195 CMP_BOUND`, the bound `i >= len(inp.plan.power_schedule or ())` in `step_supply`.
- `ADDED UNPINNED custom_components/heatpump_optimizer/pump_arbiter.py:1222 GUARD_OFF`, the no-switch-entity return in `note_supply`.

The body's final `## Unpinned sites` hands both to `mutation-autofix`, saying no pin and no survivor are claimed. That lane can only pin a mutant that some driver kills. I ran both mutants at this head (ev/U1195-cmpbound.txt, ev/U1222-guardoff.txt): `i >=` became `i >`, and the guard became `if False:`. Each time `tests/features.py` printed `ALL 4596 FEATURE CHECKS PASSED` with rc=0. The body's own pin-drive paragraph also says both "live under every driver". So the disposition the body gives cannot turn the check green. The red stays until one of two things happens:
- a check is added that kills each mutant, or
- the fixer proposes a survivor_triage verdict for each in the body, and a reviewer judges it. ci-autofix.md does not let that triage be automated.

The brief's check 3, CI green at the head, therefore fails.

## Findings

- The body records two contradictory `## Unpinned sites` sections.
  - One is spliced into the middle of the Mutation proof paragraph: "The ledger drive (`## Unpinned sites`` `PYTHONPATH=...`". It lists 1195, 1222 and `coordinator.py:7525 GUARD_OFF`, each with a proposed `equivalent` triage.
  - The final section lists only 1195 and 1222, gives them to `mutation-autofix`, and says "no survivor is claimed".
  - The repair is one section that matches the head: either a killing check, or a proposed triage per site for the reviewer to judge.
  - Carry: R10-SAV-ACTUATION
- `## Red checks` and `## Figures` give stale counts for `tests / mutation` at this head.
  - Red checks says it "stays red on the 13 under ## Unpinned sites", and Figures cites "the 24 unpinned sites" (28 before the pin commit).
  - At this head the lane names 2 added sites.
  - The red check at this head needs its own line under `## Red checks`.
  - Carry: R10-SAV-ACTUATION
- `thermal_model.plan_step_runs`: the body says its five mutation sites were "for mutation-autofix's lane or the next round". The ledger diff at this head adds `plan_step_runs.GUARD_OFF.e5c45a76` and `plan_step_runs.RETURN_DEL.f0f14778` killed pins. The body's sentence is not updated to say which of the five are now pinned.
  - Carry: R10-SAV-ACTUATION

## Evidence

- RESULT head-measured ddf75aaf8651c502794de257bbc76c044282f102 (ev/HEAD.txt). `git ls-remote origin refs/heads/fix/r10-sav-actuation` still printed this SHA at 09:41:57 UTC.
- RESULT delta-production: the branch's own diff of `custom_components/` is byte-for-byte the same at fd6103038 (three-dot against its own merge base 2f28a21ca) and at this head (three-dot against aced25893). No production line changed in the delta. The delta is tests/features.py's guard checks (`_sa_guarded`) and ledger pins.
- RESULT X0-null: unmutated head, `ALL 4596 FEATURE CHECKS PASSED` rc=0. The body quotes 4578 for the earlier head `1a7150482`. The 18-check difference is main's merged checks plus this round's 12-check section. I did not re-derive that split.
- RESULT X1-boost: live-boost return deleted. 1 of 4596 failed, only "... under a live boost across a boundary whose plan step is off".
- RESULT X2-sysid: system_identification guard deleted. 1 of 4596 failed, only "... under a system_identification action".
- RESULT X3a-mode: mode term dropped. 1 of 4596 failed, only "... under a fixed (comfort) mode".
- RESULT X3b-stale: plan_stale term dropped. 1 of 4596 failed, only "... under a stale plan".
- RESULT X4-released: `if inp.entry_released: return` deleted. 1 of 4596 failed, only "... under a released entry".
- RESULT X5-release: `release_supply(held)` deleted from `release`. 1 of 4596 failed, only "unload drops the one step tick two cycles armed".
- RESULT X6-armonce: the arm-once guard deleted. 1 of 4596 failed on the same unload check.
- Mutation proof X1 to X6 reproduces exactly as the body states. The null run writes `['turn_off']`, so each empty write list is the guard's doing. I ran the whole tests/features.py per mutant with ev/drive.py, not the body's standalone section.
- RESULT U1195-cmpbound and U1222-guardoff: both survive, rc=0, 4596 passed (see Block).
- Claim files: tests/golden/claimed_drift.txt and card_claimed_drift.txt are byte-identical to origin/main at this head. The branch claims nothing, so they resolve as main's claims (claim-files.md). VERSION, manifest.json and RELEASE_NOTES.md are untouched three-dot (ev/merge-and-claims.txt).
- Merge: `git merge-tree --write-tree origin/main ddf75aaf8651c502794de257bbc76c044282f102` exits 0 with tree 477bcfb32. There is no conflict and no MERGE-CLAIM line.
- CI at this head, read from the check-runs API at about 09:35 to 09:42 UTC:
  - Success: tests/fast (3.14), closures, arch-instrument, typing, replay, browser, briefs, closure-scope, nightly-status, arch-score, budget-raise-gate, hassfest, validate-hacs, env-matrix, policy-docs, wave-script, delivery-status, and codeql actions and javascript-typescript.
  - Failure: tests/mutation.
  - Still in progress: mutation-pins (1), coverage, instrument-self-tests, codeql python.
  - No `pr-contract` run appears among this head's check runs.
- RESULT mutation-pins: `tests / mutation-pins (1)` (check run 123981348573) was `in_progress` at 09:42 UTC. A bot pin commit would move the head, and this verdict names ddf75aaf8651c502794de257bbc76c044282f102 only.
- Unverified: I re-derived none of the body's figures that describe earlier heads (structure deltas, archscore dS, the phase harness AGREE lines, ci_predict counts). They do not bear on the delta, since production code is unchanged, and the scoped CI lanes are green.
- Finder's harness: the packet names none. The body's phase harness dev/audit/harnesses/r10_sav_actuation_phase.py is disclosed as the fixer's own build, and an earlier round reviewed it. I did not re-run it, because no production line changed in this delta.
