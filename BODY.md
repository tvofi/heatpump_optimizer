R10-ARCH-DOCS-DELTA (#2395, part of #201), second pass: re-read `docs/architecture.md` against the six product pull requests the first pass had not read: 3532, 3556, 3569, 3561, 3562, 3581. Continues pull request 3582 from `origin/handoff/r10-arch-docs-delta` (30314c72c5). Product groups r10-sav-valuation-residue-p3 and r10-sav-valuation-residue-p4 (optimizer.py, ledger.py, payload.py, thermal_model.py) are outside this pass; a short later pass covers them.

Result: one correction, caused by 3532. For 3556, 3569, 3561, 3562 and 3581 the diffs change nothing the page states (null results below).

## Head

`f6f271cebd603c22cd5f103dda9850599cf19300` is this PR's head. It is two merges of origin/main onto the previous head 957818d6ea3d2dee9a71e2c01f450b673dfc327b, and they are the only delta since it (`git diff 957818d6ea f6f271cebd`):

Merge 2: `f6f271cebd` merges origin/main 5cd7b874134350b87a72062f4d5df73404a58aff (3587, 3588 savings valuation, 3577, 3514) into merge 1, because main moved during merge 1's checks and then conflicted:
- `custom_components/heatpump_optimizer/optimizer.py`, one hunk. Both sides added different functions after `_thermostat_held_state`. The branch's side is stacked production code, not docs: `_held_reference` from the advisor-steady-start head (#2257). Main's side is `_held_bisected`, `_held_at_valve_top` and `_pump_unreachable` (3587/3588). Kept both, each byte for byte. Main changed the inside of `_thermostat_held_state` and left its signature as it was, and `_held_reference` still calls it with that signature. Read back: the +/- lines of `git diff 51f4cf4d1f f6f271cebd -- optimizer.py` equal main's own delta since 9fdba3b854 exactly, and the +/- lines of `git diff origin/main f6f271cebd -- optimizer.py` equal the branch's own delta exactly (compared as sorted line sets). Main's behaviour is kept byte for byte and nothing is added.
- Re-run for this merge, macOS seat venv-ci: `GOLDEN_MODE=drift GOLDEN_REF=5cd7b87413 tests/golden.py` reads `NO UNCLAIMED DRIFT: 56 scenario(s) checked against 5cd7b874...` and `NO STALE FIXTURE: 56 committed fixture(s) still match what this tree computes` (rc=0). `python3 tests/env_drift.py` reads no unclaimed drift and no stale fixture against origin/main. `tests/features.py`: not re-run to completion locally after the second merge of main. It was stopped at the orchestrator's instruction with 5540 checks ok and 0 FAIL printed so far; CI on Linux is the authority. The optimizer.py resolution is not comment-level. It keeps code from both sides, and no line in it was written or edited by the resolution: each side's functions sit next to each other exactly as that side wrote them. So the features blocks that pin `_held_reference` (branch) and `_held_at_valve_top` / `_held_bisected` / `_pump_unreachable` (main) stand as both sides committed them. `PREPR_SKIP_CODE=1 PREPR_SKIP_CLOSURES=1 tools/pr/prepr.sh` at f6f271cebd: rc=0, claim files `byte-identical to origin/main`, claims hygiene ok against 5cd7b87413. Nothing else was re-run for merge 2: no other file conflicted, and merge 1's scoped gate (below) covered the rest of the tree.

Merge 1: `51f4cf4d1f21199dd26959c0111f64b00cda265b` merges origin/main 9fdba3b8547f9762438dc19b98b310a63d34dcb1 (v7.1.17) into the previous head 957818d6ea3d2dee9a71e2c01f450b673dfc327b, because `git merge-tree --write-tree origin/main 957818d6ea` reported two conflicts:

- `custom_components/heatpump_optimizer/duty_switch.py`, one hunk, module docstring only. Both parents already carry the same code: `Direction.decay` caps the decayed weight at `N_CAP` (main via 3569, this branch via its stacked heads), so no executable line is in conflict. The docstring takes main's wording ("at a booking and on each decay, so a record stored over it is held to it by the first pass"), which states what that code does more precisely than the branch's. Read back: `git diff 957818d6ea <merge> -- duty_switch.py` is that one docstring hunk, which is exactly main's own delta since the merge base 0f37833e21; nothing of main's is lost and nothing is added.
- `tests/golden/claimed_drift.txt`: the claimnotes driver refused (both sides changed claims under different stamps), by design. Resolved as main's file, byte-identical (`git diff origin/main <merge> -- tests/golden/` is empty). Every claim the branch held was inherited, not its own: the eight `baseline_cost` fixture claims (valve_storage, valve_storage_low_target, valve_storage_small_tank, valve_storage_smart_write, valve_upper_direct_slab, wood_coil, wood_two_tank, wood_two_tank_smart_write) and the six suspended may-drift entries came from R10-SAV-VALUATION-RESIDUE part 2, which is on main and which the v7.1.17 stamp emptied and restored. This diff (one docs row) moves no fixture, so it re-adds nothing; measurement below.

Measured on the merge commit, macOS seat venv-ci (python 3.14.7), 2026-11-14:
- `GATE_SCOPE=auto GOLDEN_MODE=drift GOLDEN_REF=9fdba3b854 ./tests/run.sh`: `MODE: SCOPED -- 31 script(s) run, 2 scoped out.` golden.py and env_drift.py (`--claims-only 9fdba3b854`) passed. Three scripts red on this Mac, none reachable from the resolution (one docstring hunk, a claim file identical to main's): `tests/entities.py` (1 of 2724, the timing check "a measured script's late-writing descendant is waited for", inside a sandboxed coverage run), `tests/optimality.py` (1 of 84) and `node tests/card.mjs` (node OOM). The coordinator reports all three red at origin/main on this Mac too; CI on Linux is the authority, so they are not re-proven here. `tests/stress.py` was stopped unfinished for the same reason.
- `python3 tests/env_drift.py`: `NO UNCLAIMED DRIFT: 5 scenario(s) checked against origin/main`, `NO STALE FIXTURE: 5 committed fixture(s) still match what this tree computes`.
- `python3 tests/structure.py`: STRUCTURE RATCHET PASSED. `node tools/policy/policy_lint.mjs`: `TOTAL: 0 error(s) across 51 policy file(s)`. `node tools/policy/brief_lint.mjs`: clean (`FIXTURE ok`).
- `PREPR_SKIP_CODE=1 PREPR_SKIP_CLOSURES=1 tools/pr/prepr.sh` at 51f4cf4d1f: rc=1. Claim files read `byte-identical to origin/main` and claims hygiene reads ok. Its one refusal was that the head no longer merged with origin/main, which had moved to 5cd7b87413 during the run (an optimizer.py conflict). Merge 2 above resolves it, and prepr at f6f271cebd reads rc=0.

The second pass itself was measured at head 5eda176a1dcad58b7a58d5839a33ecb93cdd811c (branch r10-arch-docs-delta), measured 2026-11-14T10:28Z against origin/main a77d71fb755f231934e5e59ce1c38c51f86b6439; `git merge-tree --write-tree origin/main HEAD` reported no conflict then, so main was not merged in at that point.

Stacked product head merged (automatic merge, no conflict): pull request 3532 at fd5fe52fa788805433e1f1fe36b1824e0943838e (duty-switch restart learning part B). The correction below is true only with its code. The earlier stack (3481, 3574) stays as 3582 had it. 3556, 3569, 3561, 3562 and 3581 are read but not merged: nothing they change is stated.

## Mutation proof

n/a: documentation-only diff (one module-map row in docs/architecture.md); no production line to delete.

## Null control

Each head was read with `git diff $(git merge-base origin/main <head>)...<head> -- custom_components/`, then checked against the module map, the diagram, the boundary prose and each "One owner per concern" bullet.

- 3532 (fd5fe52fa7; duty_switch, duty_legs, pump_arbiter, off_restore, optimizer, coordinator): DEPARTURE. `duty_switch.both_step_duty` and `DutySwitchLearner.split` make the latched estimates order the legs of a both step the arbiter serves, so the row "a latched direction's estimate is what the solve prices that switch by" no longer names every reader; the row now also says it orders the arbiter's both-step legs. The `duty_legs` row ("the legs a step is served in, the switches between them, and what a stop at one costs the plan") and the `pump_arbiter` row still hold; `duty_switch` was already in the importer list; no module is added or removed.
- 3556 (fe11888ad6; boost, learner_progress, heat_energy, payload, const, coordinator, card): null. The `learner_progress` row and its bullet say phase, progress and what a learner waits for, which a "frozen" phase with a "boost" wait still satisfies; the `heat_energy` bullet says it imports nothing from Home Assistant, and the diff adds only `logging` there; the `boost` row says two-hour overlays, unchanged.
- 3569 (57ee4591d0; duty_switch, one decay clamp and its docstring): null; no row states the cap.
- 3561 (ebc8483673; pump_arbiter, off_restore): null; the `pump_arbiter` and `off_restore` rows are unchanged in meaning.
- 3562 (ced9b23358; pump_arbiter, off_restore, config_flow, const): null; same rows, plus no option page is added (the page states 24).
- 3581 (2c121b9e14; legionella, pump_arbiter): null; `legionella` and `pump_arbiter` were already importers, no row is contradicted by the notice or `cycle_write`.

Importer set at each head against this branch: `git grep -lE '^(from|import) homeassistant' <head> -- 'custom_components/heatpump_optimizer/*.py'` compared by `diff`: no difference for any of the six, so the 32 and 92 counts hold. No new or removed module in any head (`git ls-tree` diff).

Controls at HEAD: `python3 tests/doc_claims.py` reads ALL 348 checks PASSED; `python3 tests/doc_claims.py --markers --roster dev/programme/rosters/wave-r10-groups.json` reads "0 of 0 marker(s) due"; `tools/pr/prepr.sh` exits rc=0. No marker is added for a landed group.

## Figures

- `python3 tests/doc_claims.py` and `python3 tests/doc_claims.py --markers --roster dev/programme/rosters/wave-r10-groups.json`: results above.
- `tools/pr/prepr.sh`: scoped checks MODE: SCOPED (the diff vs the merge base touches governed files, so its closures step skipped as FULL by design); structure ratchet passed, self-test 553 passed.
- `git diff origin/main...HEAD --stat -- docs/architecture.md`: the one file this pass edits.

## Red checks

This pull request is a docs delta stacked on other heads; the reds below were concluded failures on commits in its range (stacked heads and merge-of-main commits), each cleared at a later commit, and none is a line this diff writes. At the live head the only API red is `tests / nightly-status`; `pr-contract` and `gate` are this check's own refusal. each is named with its job, commit and cause as the job log states it.

- `tests / mutation`: job 132327582237 at commit 49afbe9d01 (04:25Z 2026-11-14), log: `MUTATION TABLE REFUSED -- 2327 unpinned site(s) against 2309 at the ratchet base 0f37833e..., 18 of them added by this diff`; red by construction on the stacked heads' new sites (see `## Unpinned sites`). Cheaper detector: `prepr.sh` step 7d prints the sites before the push and mutation-autofix pins killed sites after it; both already stand, neither is new cost here.
- `tests / fast (3.14)`: job 132302973404 at commit d712c2ba4a (01:02Z 2026-11-14), log: `FAILED python3 tests/features.py` on the check "a charge-start dip that recovers is learned as neither a draw nor usage..." under a Saturday clock; fixed on main by PR 3578 (R10-HOTFIX-FEATURES-WEEKEND-CLOCK, merged 02:43Z), whose merge commit is an ancestor of this head. Cheaper detector: the hotfix's own finding, a faked-weekend clock in the features block; recorded in 3578's `## Red checks`, not repeated here.
- `arch-score / arch-score`: job 131942718609 at commit e9b1651aae (12:53Z 2026-11-13), log: `Architecture score: dS +0.0221 WORSENS (inadmissible: coord_footprint 2505->2513)` and `FAIL ... Add a '## Architecture score' section with one line per metric`, on the stacked advisor-steady-start head's body. Cheaper detector: `tools/audit/archscore/gate.py` (the step the log names) run locally before the push, about 30 s in CI; it belongs to that head's own pull request.
- `tests / briefs`: job 131889367213 at commit 0cb807346c (10:41Z 2026-11-13, a merge-of-main commit), log: `LEGACY-CONTROL VACUOUS: carry-1412.json: its controls lint clean without the exemption: remove it from LEGACY_CONTROL_FILES`. Finding: the briefs lint is itself the cheapest detector for that state of main; no cheaper one exists, and it cleared at a later commit.

## Unpinned sites

`prepr.sh` step 7d prints 6 sites, all in the stacked heads' production lines (3481, 3574, 3532), none authored here; the owners pin them on their own heads and the train re-derives them at main.

## Carries

- Carry 0, Carry 1, Carry 4: this pass; the `doc_claims.py` and `--markers --roster` controls above. No unresolved target marker; no marker is added for a landed group.
- Carry 2, Carry 3: untouched, as 3582's body records; user-doc markers stay with R10-USER-DOCS-VERIFY; the ledger kinds `dev/README.md` names were checked by 3582 against `tools/audit/seat/ledger.py` KINDS.
- Carry 5: live read on 2026-11-14 of ruleset 23698884 (`main-protect-checks`, enforcement active): rules are `pull_request` and `required_status_checks` with the single context `gate`. The sentence "requires only gate" is true; dismissed on that read. dev/README.md is otherwise not this part's.
- Carry 6, Carry 9: duplicates of carry 4, dismissed as the brief records. Carry 7, Carry 10: duplicates of carry 5, dismissed on the read above.
- Carry 8, Carry 14: dev/README.md and the process-slim re-read are not this part's (3582 carried them; dev/README.md waits on pull request 3451).
- Carry 11, Carry 12, Carry 13: duplicates of carries 1, 3 and 0, dismissed as the brief records.
- The "One owner per concern" bullets: re-read against the six diffs only; none is contradicted (heat_energy's no-HA-import claim re-checked at 3556's head).

## Forward-carry

none

## Friction

none


