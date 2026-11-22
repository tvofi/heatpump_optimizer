Fix review: merge 738806f84d44ec087837093d272e9e79015b7644

bus-nonce: 6af87c1b9ee498975d83ee6d33ade68e

This is round 5 of this PR and the second after the round-4 re-cut. It is a delta review over the reviewed head 89f4b0324b442b4875d7c8790fc90baf62d5a2e2 (packet `## Review scope: delta`). The previous block (`class-open: axis numeric options that an earlier release stored as non-numbers unenumerated (e.g. day_start_hour)`) is resolved: `_whole` is now in `_DEFAULTED_NUMBERS`, and the set is enumerated by a rule in `tests/entities.py` from four sources that are independent of the repair's key set.

## Findings

- Survivor outside the delta: deleting the `isinstance(value, bool)` arm of `number_repairs`' filter (`entry_config.py`, a line unchanged since 89f4b032) leaves the "Config entry migration" block green (M9, ev/mutants-head.txt). A stored `True` then stays stored. The parse reads it as the default (`finite_float`) or 1 (`_whole`), and a raw reader reads 1.0. That is a silent disagreement, not a raise: the finder's `config_fuzz` `bool` op reads `permanent_cycle_fail` 0 at the reviewed head. This round's scope does not reach it (fix-review.md step 12). Carry: dismissed: the line is outside this round's delta and its effect is a non-raising read the finder's harness already measures at 0.

## Evidence

- Head measured: 738806f84d44ec087837093d272e9e79015b7644 (ev/HEAD.txt), the PR's live head and the head the body's `## Head` names. The delta from 89f4b032 is `90c577f1` (code), `4273112656` (comment split in `tests/entities.py`, no code), and two merges. `review_carry.py 90c577f1 738806f8` prints `FRESH-REVIEW`, so this delta was reviewed in full.
- Merge: `git merge-tree --write-tree origin/main 738806f8` rc=0 (ev/merge-tree.txt).
- `dev/governance/roles/`: main's `fix-review.md` and `fixer.md` are newer than the merge base. I followed main's copy through the role pack.
- `VERSION`, `manifest.json`, `RELEASE_NOTES.md`, `tests/golden/` and `*budgets.json`: the three-dot diff is empty.
- CI: `merge_train.py classify 738806f8 --pr 3734` exits 0 with `GREEN 738806f84d44ec087837093d272e9e79015b7644 pending: none red: none` (ev/ci-classify-poll.log). The body's `## Red checks` answers the range's reds on the owed set (`tests / fast (3.14)` and `gate` at 17b4ff35 and c4766c32, ev/owed-reds.txt), each with its cheaper detector.
- Class rule re-derived at the head by running the test's own `_mig_class` (ev/class-rule-head.txt): `flow 98, questionnaire 1, thermal 47, band 7, parsed 106`, giving `MEMBERS 106`. By parse: `finite_float` 95 (the body's 44 + 51), `_whole` 7, and one each of `_nonzero_number`, `_interval_minutes`, `_lead_minutes` and `_refused_number`. This matches the body's 47 + 7 + 51 + 1.
- Body census re-derived with the finder's `config_fuzz.run` (plan export 819aa2e3, `config_fuzz.py` sha1 c0ecf63a) at version 5. All 106 keys were added to `HEALTHY` (ev/extra106.txt, the field defaults; the nine None-default keys were given plausible values) and each set to `"abc"`, `None`, `[v]` and `{"v": v}` (driver ev/census_driver.py, the previous round's reviewer driver):
  - reviewed head 89f4b032: `RESULT census_fail=103 of 424`, 26 distinct keys (the six hour keys and 20 of the undeclared), `CTRL` ok (ev/census106-wtp.txt).
  - head 738806f8: `RESULT census_fail=0 of 424`, `CTRL` ok (ev/census106-wt.txt). Both match the body. My value choice for the None-default keys is my own definition, and the counts still agree.
  - The previous block's seven `_whole` keys alone go from `census_fail=24 of 28` to `0 of 28` (ev/census-whole-*.txt). A sample of six newly declared keys goes from `8 of 24` to `0 of 24` (ev/census-declared-*.txt).
- Reviewer's mutants at the head (driver ev/mutation_driver.sh, runner ev/mig_block_extract.py: entities.py header lines 1-148, section lines 15627-15951 and `R.close`; clean `ALL 19 ENTITY CHECKS PASSED`; porcelain empty after each; output ev/mutants-head.txt). Every one of these was killed:
  - M1 `_whole` out of `_DEFAULTED_NUMBERS`;
  - M2 the 89f4b032 repair (`finite_float(value)`);
  - M3 a stored None defaulted rather than dropped;
  - M4 a float-default parse in place of the field's parse, which stores the hour as `9.0`;
  - M5/M6/M8 the `heated_area_m2` and `wood_price_sek_m3` declarations deleted, and `day_start_hour_weekend` re-parsed `_as_stored`;
  - M7 `repaired_numbers` keeping None.
  - M9 survives; it is under `## Findings`.
- Widened check, `custom_components/heatpump_optimizer/entry_config.py`. The risk: 51 new `EntryConfig` fields could change what other consumers of the dataclass read. Read at the head: `EntryConfig.__iter__`, `__len__` and `__getitem__` read `raw`, so the mapping's key set and every `config.get` are unchanged. No other module calls `fields(EntryConfig)`, and `__reduce__`/`_restore` carry the new fields by value. The risk does not materialise.
- Widened check, `__init__.async_migrate_entry` repair semantics. The risk: a key now stored at its default rather than dropped could change a presence reader. The presence readers are `thermal_model.py:1050` (`CONF_BUFFER_COOLING_RATE not in config`), `two_zone_from_config` and `dhw_enabled_from_config`, which the new presence check pins. `topology.py:391` reads `float(config.get(CONF_MIXING_VALVE_TARGET) or 0.0)`, which is the same for an absent key and for a stored default of 0.0.
- Open-axis probe (reviewer's heuristic, ev/raw-reader-scan.txt): every `float(`/`int(`/`finite_float(` over `config|merged|options|data|current….get(...)` in the package was checked against the 106-key class. The 19 keys outside it are learner, store and attribute fields (`bias_k`, `window_sum`, `lifetime` ...), not options. No set member the rule misses was found.
- Step 16: the delta adds no path that skips an actuator write. Step 14: the delta moves no budget, ledger or closure.
- A local full `tests/entities.py` run was abandoned: my untracked scratch files under `tests/` were picked up by the closure self-tests (ev/entities-clean-head.txt). CI's green at this head is cited instead, and the scratch files were removed (ev/porcelain-after.txt is empty).
- Instruments built by this reviewer, not the finder: ev/census_driver.py, ev/mutation_driver.sh, ev/mig_block_extract.py and the scan behind ev/raw-reader-scan.txt.
- seat_comms.sh ran (init, ckpt, inbox, loop) with no command received.
