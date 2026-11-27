Fix review: merge 6d2f691972e5ef7ab122c521fa357e73b3040c50

bus-nonce: 32d236412e4c2c646be48ba6e786bf9c
pending-ci: gate

## Summary

This is a later-round delta review. The packet names 1d3b7925 as the reviewed head, but `verdict/3869` and `review/3869` carry two later verdicts: blocked at 392fe0b7 (metric-gamed) and blocked at 4ab51be4 (ci-red, nine surviving added sites). The latest is 18a5d67f7f at 4ab51be4. So I reviewed `git diff 4ab51be4 6d2f6919`, restricted to this branch's own commits, and confirmed the 4ab51be4 block is resolved. 392fe0b7's block was already confirmed resolved in 18a5d67f7f. Every merge in the range is git-clean.

- Production delta: one line, 5b7ae2ff89 (duty_switch.py `_kept_leg`). `need > 0 and _kept_minutes(...) < need` becomes `_kept_minutes(...) < need`. `_kept_minutes` returns `max(at, 0.0)` or `inf`, so it is never negative, and `need` is `leg_minimum`-clamped to 0..15. When need is 0, both forms are false. When need is above 0, they are identical. No behaviour moves, and the change takes out a mutant no check could kill.
- Test delta: 49d3e2692a adds four checks to the R11-OWNER-MODE-LEGS block. 5b7ae2ff89 adds a heating-minimum-0 check. 55f4f5d1c2 only splits a comment.
- Ledger delta: 1190b420e7 triages five survivors as equivalent. The bot commits 39771d9c33 and bdefc611d2 add killed_by pins.
- Other delta: 928dcb1ac3 re-cuts the D5-s7 scope under max_units.

## Findings

none

## Evidence

- Head: 6d2f691972e5ef7ab122c521fa357e73b3040c50 (`HEAD.txt`). It is still the PR head when this verdict is written.
- RESULT 4ab51be4 block resolved. Each of the nine named survivors is now disposed:
  - Killed, by CI's own mutation-autofix pins (bdefc611d2): duty_legs.py:370 CLAMP_DROP (`availability.CLAMP_DROP.b7002cce`), duty_switch.py:616 GUARD_OFF and 621 CMP_BOUND (`_kept_leg.GUARD_OFF.b99e4db9` / `e54ba5a2`, `_kept_leg.CMP_BOUND.e54ba5a2`), and duty_switch.py:631 CLAMP_DROP (`_kept_minutes.CLAMP_DROP.c344d965`).
  - Triaged as equivalent (1190b420e7): duty_legs.py:160, 168, 169, 196 and 201, as `_mode_runs` 5ba171ad, 66bb4d09 and a4744748 and `_with_minimums` a257ad19 and 463d143f.
- RESULT equivalence re-derived independently. `probe_triaged_mutants.txt` holds my own differential probe (`probe.py`, seed 3869, my own generator, not the fixer's). It ran plan_legs and availability, original against each mutant, over 4000 random plans: 1-8 steps, both orders, extra None/0.5/2/5, minimums 0-45, before IDLE/SPACE/DHW, lost 0/0.1/0.5, floor None/0.5. All five triaged mutants show 0 differing. The null control is a killable mutant (`dhw_run < dhw_min + 1.0`), which differs on 42 of 4000, so the probe separates.
- I also read the code against each triage reason:
  - a4744748: `right` is read only at a two-step's SPACE slot, so the mutant's own-code neighbour is never DHW.
  - a257ad19: at equality, `longer` equals `dhw_leg`, which is a no-op. The whole-step test reads a heating leg that `_split` and lengthening keep at 5 min or more.
  - 463d143f: a pass that changes nothing is a fixed point.
  - 5ba171ad and 66bb4d09: the wrapped index is discarded by the `np.where` around it.
- Merges (`merges_structure.txt`): all 11 first-parent merges since 4ab51be4 have trees equal to `git merge-tree --write-tree` of their parents, so none has a hand resolution. `git merge-tree --write-tree origin/main HEAD` exits 0 (`MERGE-CLAIM: resolved`).
- Three-dot against merge base 43ec8e32: VERSION, the manifest and RELEASE_NOTES.md are untouched.
- `tests/structure.py` at the head prints `module_excess_loc 21599 <= 21599`, `STRUCTURE RATCHET PASSED`.
- Step 12 widening: none. The only production line is behaviour-preserving, for the reason given in the Summary.
- Step 11, live checks at the head:
  - `gate` is red only on `FAIL tests / mutation` (`gate.txt`).
  - The mutation table's sole refusal is `flow_lift.py:FlowCurveBias.observe_temps BOOLOP 04143c3f: disposition names no site the inventory generates` (`mutation_refusal.txt`). That pin is on origin/main, and flow_lift.py is byte-identical to main's. It is main's inherited red, with its fix in flight as #3939 (open). It is not this PR's.
  - `nightly-ha` (stable, 2025.2.0) and `nightly-status` are red and are not in the owed-reds set. Every other check is green or skipped.
- Note: ci-red-inherited: required `gate` is red at this head on main's stale flow_lift 04143c3f pin alone (#3939). The `pending-ci: gate` line hands the post to the relay once #3939 lands and the gate re-runs.
