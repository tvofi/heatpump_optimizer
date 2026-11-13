Fix review: blocked c79e44e2e6929a393a9542cc74b29b5ee3dcd776 claim-false: sv space_setpoint_unit says the unit is never inferred from "enheten" (the unit or device), not from the entity ("entiteten") the body claims

bus-nonce: c167feb53384249e80c50f78d83446bc

## Block

- Carry 1's body says the `space_setpoint_unit` description "now reads that the optimizer never infers the unit from the entity ... in strings.json, en, de and sv". At the head, sv.json:596 reads "Enheten är en deklaration: optimeraren härleder den aldrig från enheten, och bara förifyllningen från en värmepumpsenhet föreslår en." In Swedish, "enheten" is the unit (the same word opens the sentence) or the device. It is not the entity: sv.json spells entity "entitet…" at 82 sites. As written, the clause says the optimizer never infers the unit from the unit, which is both circular and wrong. de ("aus der Entität") and en are correct. The fix is one word, "från entiteten", so the delta stays text only. Evidence: ev/sv_space_setpoint_unit.txt holds the head line, the base count of "Enheten är en deklaration" (1, pre-existing), and the count of "entitet" spellings (82).
- On the same re-cut, look at docs/how-it-works.md:618. The heading still says "Two opt-in refinements:", but its first bullet now opens with default behaviour ("any heat source already resets the timer"). That reads correctly only because the opt-in part follows in the bullet's second clause. Keep the heading, or reword the lead so the bullet names the option first. This is advisory and is not itself a block.

## Evidence

- Round 1. Head c79e44e2e6929a393a9542cc74b29b5ee3dcd776 is unchanged on origin at review time (`git ls-remote`), and it matches the body's `## Head`. Merge base e23124ff6e45bac1d48b4a775dad555a37965355. origin/main at review was 50373173d4.
- No review packet exists and no pull request is open, so there is no CI to read and no red owes an answer.
- `git diff MB...origin/main -- dev/governance/roles/` is empty, so the role contract is current.
- `git merge-tree --write-tree origin/main <head>`: rc=0, it merges cleanly.
- VERSION, manifest.json, RELEASE_NOTES.md, tests/golden and both claim files are untouched in the three-dot diff.
- RESULT M1 (Carry 3): in `pump_schedule.vvc_should_run`, the empty-window case was mutated from `return True` to `return False`. features block `#6 the pump schedule`: control 4/4 ok; mutant `FAIL with no windows the loop is simply left on`, 1 of 4 failed. Reproduced.
- RESULT M2 (Carry 4): in `legionella.py`, the flag-off guard `elif dhw_temp < target - 1.0:` was mutated to `elif True:`. Block `#24`: control 4/4 ok; mutant `FAIL with the flag off the historical instant credit is untouched`, 1 of 4 failed. Reproduced.
- RESULT M3 (my own mutant, the "hot water off" half of Carry 3's new sentence): in coordinator.py `_async_drive_pumps`, `if params.dhw_enabled and params.dhw_windows_active` was mutated to `if params.dhw_windows_active`. tests/features.py: `FAIL hot water disabled leaves the loop pump ON, never stuck off`, so it is pinned. The run hit my 230 s timeout after printing that FAIL (ev/m3_coordinator_features.txt). The tree was restored and `git diff --quiet` passed.
- Code reads confirm Carry 4's text: legionella.py:217-238 credits with the flag on only at `>= target - 0.5` after `DHW_LEGIONELLA_HOLD_MINUTES`, and with it off at `>= target - 1.0`. coordinator.py:4512-4516 passes `[]` unless `dhw_enabled and dhw_windows_active`.
- Carry 2: `git grep legionella_before_return` at the head finds only dev/archive/backlog.md:382, the archived finding itself, so no reader remains.
- Carry 1: `CONF_SPACE_SETPOINT_UNIT` is written only by config_flow (the user's select) and modbus_prefill.py:243. Readers are entry_config, pump_arbiter.py:449/454 and thermal_model.py:1500. I found no inference from the entity.
- Figures: `closure.py select` over the diff's files prints `MODE: SCOPED -- 23 script(s) run, 10 scoped out.`, which matches the body's figure block. I did not re-derive the prose line `25 TEST SCRIPT(S) PASSED; 9 SCOPED OUT AND NOT RUN`. The gate is CI's heavy run and was not re-run. run.sh:884 counts differently from `select` (run_always scripts), so the two lines need not agree. The STRUCTURE RATCHET PASSED line was not re-run either.
- Class: the enumeration is the body's own carry list (0 to 4 here, 5 to 13 dispatched as parts 2 and 3). I found no seam in the four corrected sentences outside the diff across strings, en, de, sv and docs.
- Harness: no finder harness moves for text. The fixer's pinning checks are features.py blocks in the tree, and I re-ran them myself.
- Forward-carry: none named, none owed by this part.
