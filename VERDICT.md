Fix review: merge cfef1ef4afadbe8ee8501ad9fe827e7108b61da6

bus-nonce: 4cdf10f32f5ee80914f7f004a218ebda

Round 1 (no earlier reviewed head). Measured at head cfef1ef4af, the head of `fix/r11-service-schema-p2` when this was written.

## Evidence

- RESULT mutation: 13 mutants on the four production lines the body names, each run through `tools/audit/seat/features_block.py` over the block from `_et_quiet_hass = FakeHass()` to `_et_quiet_set = _et_call(` (prelude from `--emit-prelude` at the head), with `__pycache__` cleared before each run. All 13 killed, none survived (`ev/mutants.txt`). This covers the body's M1-M4, the 56/70 CONST_SWAP, GUARD_OFF (`if False:`) on each of the three fold predicates, `max=69`, and `if True:` on each fold predicate (that one is killed by a KeyError on the absent-field arm). The unmutated block prints `ALL 7 FEATURES BLOCK PASSED` (`ev/head-block-unmutated.log`). A comment-only null control in `services.py` also passed with rc 0.
- RESULT failing-test-first: the head's `tests/features.py` block, run against base 38bf516bdd production code, fails exactly the three new behaviour checks: explicit 1.0 reset (`stored 0.6`), sibling folds (all four arms 0.6), and 71 °C (`71 raised None`). The absent-field null control and the 55/54 check pass there (`ev/base-block.log`). This re-derives the body's before/after probe figures with an in-tree instrument; the body's scratch `probe.py` itself was not available to re-run.
- RESULT null controls: `apply_schedule without the fraction keeps a stored 0.6` passes at base and head. The `absent` arms read 0.6 at both ends, and 70 °C is accepted at both ends.
- RESULT class (step 6): I re-ran the body's enumeration rule (`git grep -nE 'CONF_SILENT_MODE_FRACTION|"silent_mode_power_fraction"'` over `custom_components/heatpump_optimizer/*.py`, without `const.py`) at 38bf516bdd. It returns the same three fold sites the body lists: `quiet_windows.py:556`, `quiet_windows.py:575` and `services.py:388`, all changed. The other rows are the ones the body dispositions: `config_flow.py:1923`, `quiet_windows.py:420`, `sensor.py:127` and the three schema rows (`ev/checks.txt`).
  - For the legionella range there is no rule in the body, and it is a one-seam change. I checked the other writers of `dhw_legionella_temperature` at the head. The options flow field is `_number(55, 70, ...)` (`config_flow.py:1795`). The Modbus prefill suggestion is filtered by `_prefill_fits` against that same 55-70 widget (`config_flow.py:2182`). No other writer is unbounded.
- RESULT merge: `git merge-tree --write-tree origin/main cfef1ef4af` against origin/main d218fa6ce0 exits 0 with no conflict.
- RESULT versions: `VERSION`, `manifest.json`, the `RELEASE_NOTES.md` heading and `tests/golden` are untouched three-dot from 4ecca4cc58. No claim file is touched and no fixture is value-bearing for this diff.
- RESULT CI: `merge_train.py classify cfef1ef4af --pr 3700` printed `GREEN cfef1ef4afadbe8ee8501ad9fe827e7108b61da6 pending: none red: none` (exit 0, `ev/classify.log`).
  - The only red in the packet digest is `tests / nightly-status`. It is not in the `merge_train.py owed-reds` set, so no answer is owed and it does not block.
- RESULT ledger (step 14): the three re-keyed `killed_by` pins (`1f9e8473`, `b6bb9a79`, `df339fe0`) follow predicates that this diff really changed. My GUARD_OFF runs G1, G3 and G4 show each new line is killed by the check its pin names. CI `tests / mutation` is green at the head.
- RESULT actuator (step 16): the diff adds no path that skips a write. The 71-75 refusal is at service-input validation. A 71-75 stored by an earlier release still reaches the existing guard, which caps it and raises the notice; the body discloses this and `tests/guard_pins.py`'s census still drives 55-75.
- Not re-derived: the body's `25 TEST SCRIPT(S) PASSED` gate figure, taken at c22c267e2f, and the archscore `dS +0.0000`. CI's `gate` and `arch-score` are green at the head and are cited in place of re-running them, as the role contract requires.

## Findings

- Note: owner-review: the fix applies ruling (a) to `quiet_windows.overridden_config` and `quiet_windows.apply_config_keys` as well as the ruled `apply_schedule` site. The body discloses this as beyond the ruling's literal scope. It also discloses the card consequence: an install with a stored fraction below 1.0 and no quiet rows stores 1.0 on its next quiet-window save. Both are tested and consistent with the ruling, and the owner's review of the rulings covers them. Carry: dismissed: disclosed in the PR body for the owner's review of rulings (a) and (b); no later stage changes
- Note: figure: the body's before/after probe is a scratch `probe.py` (sha1 only) that is not in the tree. Its readings are re-derived above with the committed block. Carry: dismissed: re-derived in this verdict's Evidence with an in-tree instrument
