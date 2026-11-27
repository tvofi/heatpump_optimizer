Fix review: blocked 1d027949b899f6f1491de54d1908a73d8d28c581 class-open: frost_hold.gate runs on an install with no power switch; it sets frost_holding there, so the arbiter serves a cold idle step as space at the pump's floor and the learners freeze, where the option is hidden and claimed inert
bus-nonce: 37420e0dbf906ad97b83a9179b255305

Round: first full review at this head. The earlier verdicts on review/3882 are blocks (96523195 tests-red, 49658957 merge-conflict), and no merge verdict exists, so the scope is the full three-dot diff against merge base e84856520dc4. Measured in a detached worktree at 1d027949b899f6f1491de54d1908a73d8d28c581.

## Block

- The predicate's unguarded domain is an install with no power switch. The body, the release note, strings.json and the design all scope the hold to "every install with a heat-pump power switch", and config_flow hides both options there (`when=_power_switch`). But `coordinator._write_supply` calls `frost_hold.gate(...)` on every cycle before its `if switch_entity and value is not None` check. `gate` then sets `held.frost_holding = _active(...)`, and `EntryConfig.frost_hold` defaults to True whether or not a switch exists. So on a no-switch install, every idle step below +2 C, or with a stale or missing outdoor reading, has these effects:
  - `pump_arbiter._served` returns "space", so under Pump duty control `desired(..., frost=True)` writes the space set-point at `_hold_floor_c` in place of the baseline row.
  - `_note_pass` records the pass as idle, and `_observe` marks the step "frost-hold" in the duty ledger.
  - `frost_hold.freeze_reason` freezes the learners for two intervals after each pass, every pass when no meter is installed.
  - The user cannot opt out, because the option is not shown.
- Probe (ev/probe_noswitch.py, output ev/probe_noswitch_1d027949.txt): with switch=None at -3 C, `gate(False)` returns None, frost_holding is True, `_served(duty=None)` returns 'space' and `freeze_reason` returns 'frost_hold', the same as with switch.hp. Null control: at +5 C with no switch the result is False/False. The block's `_fh_inp` accepts `switch=None`, but no check drives it.
- Fix shape: `_active` or `gate` must treat a missing `heat_pump_switch_entity` like opted out (latched None, not holding). The same applies to `take_off`, whose cut-off path is already switch-bound. Add one check with no switch and its switch.hp null control.

## Checked, survives the block

- RESULT merge: `git merge-tree --write-tree origin/main 1d027949b899f6f1491de54d1908a73d8d28c581` at main 9ffb388f7ec88aada3354a316553908d34c664e8 exits 0 (LEDGER-MERGE resolved tests/closures.json) (ev/merge-tree.txt).
- RESULT structure: `tests/structure.py` at the head prints STRUCTURE RATCHET PASSED, max_class_loc 7763 <= 7763 and module_excess_loc 21644 <= 21644 (ev/structure-at-head.txt). Against main's table the raise is module_excess_loc 21627 -> 21644 (+17) and max_class_loc 7762 -> 7763 (+1). budget-raise-gate is green.
- RESULT version: VERSION, manifest.json and RELEASE_NOTES.md are untouched in the three-dot diff.
- RESULT checks: live check-runs at the head (ev/checks-1d027949b899f6f1491de54d1908a73d8d28c581.txt) are all success or skipped except tests / nightly-ha (2025.2.0), nightly-ha (stable) and nightly-status. None of the three is required, and the body answers them.
- Not re-run: the mutation proof and the finder's harness (none is named; the design's evidence plan is the judge's). The fix above moves production code, so both are owed again at the repaired head.

Note: body-figure: `## Head` still quotes module_excess_loc 21663 <= 21663 for the 22802e44 head. The head measures 21644 against the re-recorded table. Carry: dismissed: evidence, not a finding
