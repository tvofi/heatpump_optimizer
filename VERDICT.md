Fix review: merge 8c9dc2697a74ebb036f4dddb8557edd57664d8bd

bus-nonce: f3dea7a3ccd3b8c7452547c4e275712f

Round 1, handoff review: the head is the handoff tip, and the body's `## Head` names the same SHA. There is no pull request, no review packet and no CI run yet, so no live checks were read. The `## Red checks` section says none, and there is no run to contradict it. Role contracts: `git diff 154dbb4c...origin/main -- dev/governance/roles/` is empty, so the contract is current.

## Findings

- Main-merge break: the head merges into current origin/main (e23124ff6e) without a textual conflict, but `tests/doc_claims.py` then exits 1 at `tests/doc_claims.py:4739` with `AttributeError: module 'heatpump_optimizer.pump_arbiter' has no attribute 'SPLIT_MIN_MINUTES'` (ev/doc_claims_on_main_merge.txt). Main's 4a8115bc10 (R10-DUTY-SWITCH-PLANNER-PRICE) moved the constant to `duty_legs.SPLIT_MIN_MINUTES` with the same value, 5.0, and kept the 5-minute rule. I monkeypatched the pin to point at `duty_legs`; all 19 pins and the written-slot arm then come back empty on the main merge, so the text stays true and only the import is stale. The brief forbids blocking on a head that merges cleanly, so this is a merge verdict. The train's re-proof on current main will go red here until the pin reads `duty_legs.SPLIT_MIN_MINUTES`. That one-line test delta needs no wider review, but a red CI never carries. Carry: dismissed: the train re-proves at current main and this red returns the branch to its fixer; the repair is the one-line pin repoint named here
- Conflict with #3561 (a02783d4). The two wordings agree: both say that under Control the optimizer writes the space set-point entity (3561: "writes it on every plan step"; this branch: writes the plan's room or water temperature), and that under Off or Observe it is only read. This branch will conflict with #3561 once #3561 merges. `git merge-tree --write-tree a02783d4 <head>` exits 1 with CONFLICT (content) in strings.json, en.json, sv.json and de.json (ev/merge_tree.txt). The cause is adjacent-line edits: #3561 changes `space_setpoint_entity` and this branch changes `space_setpoint_unit` on the next line. The resolution is to keep both lines. I resolved it that way and checked the result: `flow_write_findings` returns [] with and without `_OWNED_ELSEWHERE`, so the exemption expires as the body says and #3561's text passes the written-slot arm. Carry: dismissed: a hand resolution the orchestrator makes at the second merge, both sides kept; measured here
- Translations are not pinned (brief item 3). The written-slot arm reads only strings.json. Mutant M7 plants "never writes" in sv.json's `space_setpoint_unit` and stays green (`ALL 354 checks PASSED`, ev/mutants.txt). sv and de are covered only for keys, by entities.py. Carry: R11-INTAKE-R10-RESIDUE
- The written-slot set is narrower than the set of written entities (brief item 3). It is derived from `pump_arbiter._entities`, which returns mode, dhw_setpoint, space_setpoint and silent. The heat pump on/off switch (`heat_pump_switch_entity`) is also written: the body's own `pump_duty_mode` correction says the plan switches it under all three modes. Mutant M9 appends "The optimizer never writes it." to that key's help and stays green. The `dhw_disinfection_switch_entity` written under Control is outside the set too. No shipped sentence is false today, so this is a gap in pin coverage, not an open seam. Carry: R11-INTAKE-R10-RESIDUE
- Two rows in the record cite strings.json (`options.step.advanced.menu_options`) rather than the code that builds the menu: `options.step.init.description` and `options.step.advanced.description`, both judged true. Neither rests on a comment or docstring, so brief item 1 does not block. Carry: R11-INTAKE-R10-RESIDUE
- `pump_duty_mode` says "toward 5 °C (or the Minimum lift above the inlet water)". This is a temperature difference (FLOW_MIN_LIFT_K), so the unit should be K. The wording predates this branch ("toward 5 °C (or flow_min_lift_k)" at the merge base), and the pin keys on "°C", so the unit fix also needs the regex changed. Carry: R11-INTAKE-R10-RESIDUE

## Evidence

- RESULT mutation: 9 mutants at the head, using ev/mutants.sh with doc_claims.py as the closure check (ev/mutants.txt).
  - Killed:
    - M1: `space_setpoint_unit` restored to its merge-base text gives the written-slot FAIL.
    - M2: `LEASE_MINUTES` set to 60 in pump_arbiter.py gives the figure-pin FAIL plus the null control.
    - M3: `SPLIT_MIN_MINUTES` set to 6 gives the figure-pin FAIL.
    - M4: `_OWNED_ELSEWHERE` emptied gives the `space_setpoint_entity` FAIL. This is the body's null control.
    - M5: `ECONOMY_MIN_TEMP_WIDENING` set to 2.0 gives the figure-pin FAIL.
    - M6: `curve_learning.STEP_K` set to 0.3 gives the figure-pin FAIL ("quotes six tenths, the code holds 0.9").
    - M8: "never writes" planted on `heat_pump_capacity_limited_entity` (the silent slot) gives the written-slot FAIL.
  - Survived: M7 (sv.json) and M9 (`heat_pump_switch_entity`). Both are gaps in coverage, not in the claims the diff pins; they are listed under Findings.
  - Baseline: `ALL 354 checks PASSED` in 11.9 s.
- RESULT figures at the head (ev/head_figures.txt):
  - Flow strings: 1074 per catalogue for strings, en, sv and de.
  - Claim set: 370 distinct texts at the head. The record has 369 rows, matching the stated 369 at the merge base.
  - Verdict counts: {'true': 286, 'false': 27, 'stale': 12, 'unverifiable': 4, 'no-claim': 40}.
  - `git diff --stat` prints 112/112/112/110 for strings, de, en and sv.
  - tests/doc_claims.py: ALL 354 checks PASSED.
  - tests/entities.py: completed with exit 0.
  - tests/structure.py: STRUCTURE RATCHET PASSED.
  - All figures match the body.
- Not re-derived: the scoped-gate figures (`MODE: SCOPED -- 11 script(s) run, 22 scoped out` and run.sh's 13/21). The gate is a heavy run, CI has not run, and the contract has CI's figures cited rather than re-run. Also not re-derived: the move of `tests/closures.json` `tests/harness_headers.py` from rc 1 to rc 0 and its added `flow_claims.py` entry, which is a recorded measurement I did not re-run.
- RESULT brief item 1: ev/evidence_kind.py classified every evidence `path:line` at the merge base by AST and tokenize as code versus comment or docstring. Every row judged true, false, stale or unverifiable cites at least one code line, apart from the two strings.json-cited rows under Findings. I spot-checked rows against the code: `flow_curve_cop_enabled`, `dhw_setpoint`, `away_dhw_min_temperature`, `min_temperature`, `max_temperature`, `space_setpoint_unit` and `pump_duty_mode`. In each, the why and the correction are grounded in code lines such as constants, `_entities` and `_share`, not in comments.
- RESULT brief item 3, pinned claims: the 19 figure pins and the written-slot arm are pinned and every pin was killed by a mutant. Unpinned: translations, the switch slots outside `_entities`, and the prose-only rows the body names (the 0.5 K night floor literal and the pre-fill registers).
- Merge with origin/main: `git merge-tree --write-tree origin/main <head>` exits 0. The claimnotes driver line is `LEDGER-MERGE: resolved tests/closures.json` and no claim file conflicts (ev/merge_tree.txt).
- VERSION, the manifest version and RELEASE_NOTES.md are untouched: `git diff 154dbb4c <head>` is empty for all three. The claim files are untouched, and no golden fixtures were moved.
- owed-reds set read with `merge_train.py owed-reds`. There are no runs, so no red is owed an answer.
- Forward-carry: every body line carries `R11-INTAKE-R10-RESIDUE`. With no pull request, carry_audit's `pr` check cannot run against a body yet.
