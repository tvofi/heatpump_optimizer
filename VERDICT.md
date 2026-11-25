Fix review: blocked ef591eaa117c9fb901cdb2f37844a94e921a35d3 mutation-vacuous: pump_arbiter.py:1341 _pass_record _settle(held, inp) -> held.served survives tests/features.py

bus-nonce: 070b20820d5fa25a7d75a026935459f9

## Block

- `custom_components/heatpump_optimizer/pump_arbiter.py:1341`. The repair (b5ae3058f5) takes the I4/I6 exclusions out of `_map_inputs` and gives `_pass_record` its own call into the gate: `m = _map_inputs(inp, now, boosted, _settle(held, inp))`. Swapping in `held.served` (bypassing the gate) leaves the full `tests/features.py` unchanged at this head: 1 of 6159 failed, the same environmental row the unmutated baseline fails. The mutant changes behaviour. `_flow_command` gates on `flow_setpoint_driven`, which admits the return unit (`SPACE_SETPOINT_WATER_UNITS`) and does not exclude an experiment step, so `_pass_record` runs on both. A probe run inside the settle span after a swap shows the difference:
  - On a system-identification step and on a return target, the head records `PassRecord.floor_c` 59.0, the unsettled floor. The mutant records 34.0, the settled floor.
  - Null control: on a plain flow target both record 34.0.

  Before this delta the guard sat inside `_map_inputs`, so T6's kill covered both callers. Now the `desired()` call site is pinned (mutant m4 is KILLED) but the `_pass_record` call site is not. The body's mutation proof lists only "`_pass_record` unsettled" (passing `None`), which is a different mutant. T6 tests `_settle` in isolation, not that `_pass_record` routes through it. CI's syntactic mutation table will not draw this mutant. The fix is a pin: a check that `_pass_record`'s `floor_c` on an experiment step and on a return target is the unsettled floor within the settle span, with the plain-flow row as its null control. `ev/probe_pass_record.diff` is a starting shape.

## Findings

- Follow-up: once the `_pass_record` gate pin lands, re-run this mutant (m3) and the probe at the new head; nothing else in the delta needs re-review (see Evidence). Carry: R11-OWNER-STEP-KICK

## Evidence

- Scope: this is a delta review over the reviewed head 4c2f14778b281cfb2b55e73e3b9b484cbd9140de, as dispatched. The packet's `## Review scope` line reads `full`, because no verdict on `verdict/3883` names 4c2f1477. Main's own changes are removed by diffing `git merge-tree --write-tree origin/main 4c2f1477` (tree f53f3a962b, conflicts in claims.py, deployment_shape.py, features.py) against ef591eaa. That leaves 10 files: `pump_arbiter.py` (b5ae3058), D6 claims.{py,json,md}, `docs/architecture.md`, `tests/closures.json`, `tests/deployment_shape.py`, `tests/features.py`, `structure_budgets.json` and the `desired.GUARD_OFF.0082e8a4` pin. `pump_arbiter.py` and `flow_anchor.py` are byte-identical between 5e88c6f01a and ef591eaa.
- Prior finding resolved: rev-3883's `architecture-unsound` finding (coord_footprint 2521 -> 2523, WORSENS). At this head `python3 tools/audit/archscore/score.py --diff bb6377b4da` prints `Architecture score: dS +0.0000 NULL` (`ev/archscore.txt`).
- Delta semantics: `_settle` reproduces the old `_map_inputs` guard for both callers. `state_for` is memoised (`_STATES` dict), so the second `state_for(coord)` call in `desired()` returns the same object as before. The behaviour is unchanged except for the pinning gap under Block.
- Hand-resolved hunks:
  - `tests/features.py`: the STEP-KICK block at the head is byte-identical to 280a51a4's (234 lines), and the CARD-EXTERNAL-HEAT block is byte-identical to main bb6377b4's (46 lines). Both are kept, in that order.
  - The counts, re-derived at the head:
    - 103 top-level `.py` modules (`git ls-tree`).
    - 122 tracked files under `custom_components/heatpump_optimizer/`.
    - 66 HA-free modules: 103 less the 36 module-level importers (claims.py C34) less the one function-level importer.
  - `claims.py` prints `arch_modules_on_disk=103`, `arch_map_listed=103` and `claims_false=0`. Running it leaves the tree clean, so `claims.json`/`.md` match it.
  - Both history clauses are kept in claims.py (two RESULT lines) and in deployment_shape.py.
- Checks at the head:
  - `PYTHONPATH=tests/hastub python3 tests/doc_claims.py`: ALL 443 checks PASSED. The body's 441 was taken at 280a51a4; main has since added rows.
  - `tests/deployment_shape.py`: ALL DEPLOYMENT SHAPE CHECKS PASSED.
  - `tests/structure.py`: rc 0, `ok module_excess_loc 21765 <= 21765`. Main's budget is 21774, so the row falls 9 and nothing is raised. The body's 21766 is the 280a51a4 value.
- Mutants (`ev/mutants.txt`, `ev/mut_*.txt`): m1 (I4 dropped from `_settle`), m2 (I6 dropped) and m4 (`desired()` bypassing `_settle`) are KILLED. m3 SURVIVED (Block). The baseline's single failure is `_bootstrap drops the package directory`, a worktree-path artefact present in every run.
- Merge: `git merge-tree --write-tree origin/main ef591eaa` exits 0 (origin/main bb6377b4).
- CI: `merge_train.py classify` still prints WAIT after about 27 minutes of polling (`WAIT ef591eaa117c9fb901cdb2f37844a94e921a35d3 pending: gate red: none`, `ev/classify-last.txt`). Because the verdict is blocked on code, it does not wait for CI. The owed-reds set is `tests / mutation`, `tests / typing`, `validate / validate-hacs`, and none of them is concluded red at this head.
- Not re-run: the finder's harness `dev/audit/harnesses/r11_owner_step_kick.py`. It reads `flow_anchor.py`, which the delta does not touch. I did not re-derive the body's 19 of 19 and 15 of 15 mutation counts. My own drive is the four mutants above.
