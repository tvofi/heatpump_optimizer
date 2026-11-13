R10-OUTSIDE-VALVE-TARGET-LABEL: the mixing-valve target option reads as a water temperature but is the room temperature the circuit holds; this names it as a room temperature and raises a notice when it sits above the comfort ceiling. Reported by Bankaifan on pull request 3529 (follow-up comment 6840023148); the mechanism was verified by reading the code, and the contributor's energy figure was not reproduced, so no figure is claimed.

The label becomes "Room temperature the mixing circuit holds" and its description opens by saying it is not a water temperature (en, de, sv in strings.json and the three translations, plus docs/configuration.md and README). A repair `valve_target_above_comfort` (mixing_valve.audit_target, called from the existing comfort-band audit so it reaches existing entries) names the target and the ceiling; it is a notice, not a refusal, because a target above comfort can be deliberate (slab charging). The solve is unchanged. Carry 0 (P-OUTSIDE-3529-C): the contributor's three commits from docs/combi-effectiveness-measurement (81b21d7733, the effectiveness measuring recipe) are cherry-picked with Bankaifan kept as author under his numbered noreply address; the effectiveness bound 0.1 to 1.0 and the clamp in thermal_model.py are untouched. For the reviewer: the recipe's sentence that the ratio belongs to the sensor the model reads is the one to check against that clamp. Issue 3529 is wired to R11-OUTSIDE-HONEST-STARTS-RUNS, so this closes nothing by keyword.

## Head

`d710600251b5e4be6d8a754c6ef4d97f61329877`

## Mutation proof

Removing the `mixing_valve.audit_target(...)` call in `coordinator._audit_comfort_band` turns exactly one check red when `PYTHONPATH=tests/hastub python3 tests/features.py` runs: "valve target: a configured target above the comfort ceiling raises one repair, once across two cycles, naming the target and the ceiling" (1 of 5365 FEATURE CHECKS FAILED). The trap check (a configured 30 against 0 moves the planned hot-water energy on a combi entry) passes on the unmodified solve, pinning why the notice is needed.

## Null control

On the unmodified tree a target of 0, unset, 21, 23 (at the ceiling) and 23.5 under a 24 ceiling raise no notice ("valve target null control" passes), and the same target replans byte-identically (the notice reads the plan, never changes it). Golden fixtures are unchanged and neither claim file is touched. Authorship control: `git rev-parse HEAD^{tree}` equals the tree of 918f38cc7fbfc3f777e256efa6f05f7d5a33fb63, and `git log --format='%an %ae' origin/main..HEAD` shows only numbered users.noreply.github.com addresses.

## Figures

- Architecture score, `python3 tools/audit/archscore/score.py --diff e4ca2d940efd1e87912d80cb3ebddf8240ba0729 HEAD~1` (the previous head, 3d1e538d): `dS -0.0006 WORSENS (inadmissible: coord_footprint 2506->2507)`, the red check reproduced.
- Same command with the final head, `... --diff e4ca2d940efd1e87912d80cb3ebddf8240ba0729` (tree): `Architecture score: dS +0.0000 NULL`, so coord_footprint is not above its merge-base value of 2506.
- `tools/pr/prepr.sh` on the committed head d710600251b5e4be6d8a754c6ef4d97f61329877: rc=0, no refusal.

## Red checks

- `tests / mutation`: red by construction on the 2 predicted sites under `- `arch-score / arch-score`: the previous head's `_audit_comfort_band` called `mixing_valve.audit_target` with `getattr(self, "_ctx", self)._thermal_params` inline, a call as an argument, which footprint.py does not read as delegation, so it counted one coordinator statement. The head now binds `ctx = getattr(self, "_ctx", self)` once (the form `_audit_lower_floor` already uses, which the scorer reads as an alias) and passes `ctx._thermal_params`, so the call is plain delegation. The same binding also serves the existing `comfort_band.violations` read. Payment taken (option 1): no statement moved or deleted and no behaviour changed; the label text and the notice are untouched. The cheaper detector is the arch-score step at the handoff (`score.py --diff`, seconds, no standing cost); it was not run before the first handoff, and the fixer contract's step 17 names it, so this was state (b), not followed. Run at this handoff.

## Unpinned sites` (CI's mutation predictor, not a mutant run by this seat). The cheaper detector is the one that predicted it, prepr.sh step 7d, at no standing cost; I did not run the mutants. By reading, the features check at target 30 over ceiling 23 kills the return deletion and the null control at a target equal to the ceiling (23) kills the bound change, and `mutation-autofix` pins killed sites after the push.

## Unpinned sites

- `custom_components/heatpump_optimizer/mixing_valve.py:122 CMP_BOUND`: pinned by mutation-autofix; expected to die on the null control at a target equal to the ceiling (23 against 23 raises no notice). Not measured here.
- `custom_components/heatpump_optimizer/mixing_valve.py:122 RETURN_DEL`: pinned by mutation-autofix; expected to die on the check that a target of 30 over a 23 ceiling raises the repair. Not measured here.

## Forward-carry

none

## Friction

none
