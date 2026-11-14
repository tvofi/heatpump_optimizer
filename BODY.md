R10-ARCH-DOCS-DELTA (#2395, part of #201), second pass: re-read `docs/architecture.md` against the six product pull requests the first pass had not read: 3532, 3556, 3569, 3561, 3562, 3581. Continues pull request 3582 from `origin/handoff/r10-arch-docs-delta` (30314c72c5). Product groups r10-sav-valuation-residue-p3 and r10-sav-valuation-residue-p4 (optimizer.py, ledger.py, payload.py, thermal_model.py) are outside this pass; a short later pass covers them.

Result: one correction, caused by 3532. For 3556, 3569, 3561, 3562 and 3581 the diffs change nothing the page states (null results below).

## Head

Head 5eda176a1dcad58b7a58d5839a33ecb93cdd811c (branch r10-arch-docs-delta), measured 2026-11-14T10:28Z against origin/main a77d71fb755f231934e5e59ce1c38c51f86b6439; `git merge-tree --write-tree origin/main HEAD` reports no conflict, so main is not merged in.

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

none owed by this pass beyond those 3582 already carries: the unpinned sites and arch-score reds belong to the stacked heads' own pull requests (3532 now included), whose owners pin them; none is a line this diff writes.
- `mutation` at 5eda176a1dca: red by construction on the 6 site(s) under `## Unpinned sites`; mutation-autofix pins killed sites after the push.

## Unpinned sites

`prepr.sh` step 7d prints 6 sites, all in the stacked heads' production lines (3481, 3574, 3532), none authored here; the owners pin them on their own heads and the train re-derives them at main.

## Carries

- Carry 5 (dev/README.md "requires only gate"): live read on 2026-11-14 of ruleset 23698884 (`main-protect-checks`, enforcement active): rules are `pull_request` and `required_status_checks` with the single context `gate`. The sentence is true; carry 5 and its duplicates 7 and 10 are dismissed on that read. dev/README.md is otherwise not this part's.
- Carry 0, 1, 4: this pass; `doc_claims.py` and `--markers --roster` controls above. Carry 2, 3: untouched, as 3582's body records; user-doc markers left to R10-USER-DOCS-VERIFY.
- The "One owner per concern" bullets: re-read against the six diffs only; none is contradicted (heat_energy's no-HA-import claim re-checked at 3556's head).

## Forward-carry

The two product parts r10-sav-valuation-residue-p3 and r10-sav-valuation-residue-p4 land after this pass; a short later pass re-reads `docs/architecture.md` against them. Carry: R10-ARCH-DOCS-DELTA

## Friction

none
