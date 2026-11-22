Fix review: blocked 19eafc0fb12c80b3b2c8a7d6f130c28150690e7a mutation-vacuous: pump_arbiter.py:936 GUARD_OFF (O-M7, the high-limit cap in _boost_ceiling_c) survives and is provably equivalent; the body says that cap was deleted, but it is still at the head

bus-nonce: 9dae893d9725ed0b50d989d7b76b7876

Round 1 (full review, no reviewed head). Local fix-review seat replacing the unstarted cloud reviewer of this dispatch; worktree detached at the head, merge base 8cc3fb3e35.

## Block

- `custom_components/heatpump_optimizer/pump_arbiter.py:936-937`, in `_boost_ceiling_c`: `if (limit := _space_limit_c(inp)) is not None: caps.append(limit)`. The body ("Departures", third bullet, and M7 under "Mutation proof") says this cap was removed in `ea4b6dd401` and that "the mutant site no longer exists". It was never removed: `ea4b6dd401` touches only `tests/features.py` (2+/2-), and every commit from `01a105fa9b` to the head carries the line (`ev/m7_site_at_head.txt`).
- The site is a survivor. With GUARD_OFF applied (`if False:`), the FLOWCAP block passes 12 of 12 (`ev/mut_O_M7_boost_ceiling_cap_GUARD_OFF_.txt`). It is also equivalent by construction, so no test can kill it. `_boost_ceiling_c` has one caller, `_map_inputs` (`pump_arbiter.py:1009`). That caller takes `min(boost_c, _space_limit_c(inp) or inf)` over the same value, so `min(min(caps + [L]), L) == min(min(caps), L)`.
- The body's `## Unpinned sites` lists `pump_arbiter.py:936 GUARD_OFF: pinned by mutation-autofix`. Autofix pins only killed mutants, so this site stays an unpinned survivor in `tests / mutation`.
- Repair, which is what the body already says was done: delete the two lines, and the docstring clause "and by the high limit (:func:`_space_limit_c`: ...)", from `_boost_ceiling_c`. Then re-take M8 at the new head. On this head M8 alone fails 4 of 12 (`ev/mut_O_M8_map_top_ignores_limit_.txt`), not the body's "6 at the head". 6 is what M7 and M8 together fail here (`ev/mut_O_M7_M8_.txt`).

## Findings

- Note: design-departure: design `fa8cd134` rule 5 (a limit under the entity's minimum is raised to the minimum) is not built. The design's own "Tests the build owes" line "option 35 with minimum 40 gives 40" is pinned the other way: the limit is dropped and a boost writes 70. The departure is disclosed and measured in the body. Rule 4 of the same note runs first and drops any limit under the lowest heating write. `_gate_c` is bounded up to the entity's minimum, so a limit under the minimum is always under that write, and raising it to the minimum would put the cap at the gate, which writes every heating step as off. Carry: dismissed: the design's rule order makes rule 5 unreachable, and the body discloses it with the `min 40` / `min 41, step 5` check as its pin
- Note: harness: the owner item names no committed finder's harness (the review packet says "Finder's harness: none named"), and the body's `owner_flowcap_harness.py` is the fixer's, out of tree. This review traced the approved design's "Tests the build owes" list instead and did not run the fixer's harness. Carry: dismissed: a feature's harness is its judge's design (fix-review.md step 9); every owed test item but rule 5 is present (Evidence)

## Evidence

- Head measured: 19eafc0fb12c80b3b2c8a7d6f130c28150690e7a (`ev/HEAD.txt`); it matches the body's `## Head`. The role contract is current: `git diff <merge-base>...origin/main -- dev/governance/roles/` printed nothing.
- Merge: `git merge-tree --write-tree origin/main HEAD` at origin/main 49cb3207a9 exits 0 (`ev/merge_tree.txt`).
- Mutation proof, re-run with the reviewer-built driver `ev/mut.py` (textual mutants, restored after each run; mutant_run.py was not used). Option block, 12 checks (`ev/flowcap_head.txt`: ALL 12 PASSED at the head):
  - M1 (`min` to `max`) killed 3
  - M2 (strict `>`) killed 1
  - M3 (a dropped source voids the other) killed 1
  - M4 (floor off) killed 1
  - M5 (ceiling off) killed 1
  - M6 (indoor unit reads the limit) killed 1
  - M7 SURVIVED (above)
  - M8 killed 4
  - M9 killed 1
  - M10 killed 1
  - M11 (the sensor read bypasses `_setpoint_limits_c`) killed 1
  - M12 (the option never read) killed 10; the body says 9
- Clamp block, 7 checks (`ev/clamp_head.txt`: ALL 7 PASSED). C-M1 killed 4, C-M2 killed 2, C-M3 killed 1, C-M4 killed 1, C-M5 killed 1. These match the body's figures.
- Class enumeration, both rules run at the head (`ev/enum_setpoint_service_calls.txt`, `ev/enum_space_setpoint_consumers.txt`). Every seam returned is in the diff or dispositioned in the body:
  - Service calls: the valve `write_setpoint_c` at `coordinator.py:728`, the frequency `set_value`, `heat_curve`, `repairs.py`, `services.py`, the GCHV night `set_value` at `pump_arbiter.py:1647`, and `_write`.
  - Consumers: room path 672 (indoor, excluded), gate 832, `flow_command` 878 (advertised, tested), heating step 972, hold 990, feedback 1079/1115, heating floor 1123, DHW-duty space write 1319 (entity minimum), adopt 1750.
  - No `class-open`.
- Design trace against `fa8cd134` "Tests the build owes":
  - Present: precedence (lower binds, sensor unavailable, crossed pair, neither, option over the advertised maximum), the gate rule with its equality boundary, boost, band top, hold, feedback ceiling, the draw_range not-top check, the indoor exclusion, the options row's 30-70 range with `stored_value_out_of_range`, and the cleared-row seeding in `tests/config_flow_steps.py`.
  - Departs: rule 5 (Findings).
- Structure: `python3 tests/structure.py` at the head prints STRUCTURE RATCHET PASSED. The `module_excess_loc` drop is earned: `silent_rows`/`inside_silent` moved to `quiet_windows.py`, which has 694 lines, under the 2000 `MODULE_LOC_LIMIT`. archscore was not re-run.
- VERSION, the manifest, RELEASE_NOTES.md, tests/golden/ and both claim files are untouched in the three-dot diff.
- Red checks: `merge_train.py owed-reds` prints `tests / mutation`, `tests / typing`, `validate / validate-hacs`. The body answers `tests / fast (3.14)` and `tests / mutation` at f36611dd23. The head's `tests / mutation` would carry the O-M7 survivor above.
- CI at this head: `merge_train.py classify 19eafc0f... --pr 3866` printed `WAIT ... pending: gate red: none` from 22:13Z to 22:16Z (arch-score and budget-raise-gate queued, the gate contexts skipped). The block is on code, so the waiter was stopped and no CI result is relied on.

## Friction

none
