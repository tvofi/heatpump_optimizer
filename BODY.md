Closes #2272.

R10-REPLAY-REAL-DAY: the replay lane's first real recorded day. tvofi's 2026-10-30 away episode, cut from his own Home Assistant export, masked and sealed, replayed through the current coordinator as a nightly regression guard on the away path. Getting there took three changes to the export first, because the owner's install defeated it twice.

**1. The recorder a `recorder: db_url` names (`tools/replay/export.py`).** tvofi's recorder is MariaDB. `export.py` read only `<config>/home-assistant_v2.db`, a stale leftover, and wrote a near-empty day (2 states, both from 2025-01-10) that its own `--check` passed. The export now resolves the recorder from `--db-url`, else `--db`, else configuration.yaml's `recorder: db_url` (inline or `!include`, `!secret` through secrets.yaml), else the default SQLite file. MySQL/MariaDB is read through the driver the Home Assistant container ships (`MySQLdb`, else `pymysql`), found at run time, refused by name when absent, in a `SET SESSION TRANSACTION READ ONLY` session, SELECTs only, with the SQL shared with the SQLite path (`?` rewritten to `%s`). The SQLite path stays stdlib-only. The URL's credentials are never printed, logged or written: the recorder is named `scheme://host/database`, and a failed connect reports the exception class only. A window in which a mapped input has no state, updated or reported, is refused, naming the inputs by masked role and the recorder read. An input is an id under an entry key the installed integration reads, so a key a release retired (`heat_pump_entity`, v3.8.0, never read) is named on stderr and left out rather than refused (the owner's first MariaDB run).

**2. Location masking (`custom_components/heatpump_optimizer/replay_doc.py`, the one sealing path both writers use).** tvofi: "It is important that the fixer masks my street address." The Tibber price sensor's id is derived from the home's address. `document()` now renames every entity id through one mapping: an id the entry holds under a key becomes `<domain>.<role>` (`price_entity` -> `sensor.price`; the n-th of an `_entities` list `<role>_n<n>`; the Tibber series `sensor.price`, or `sensor.price_series` when the entry's own `price_entity` holds `sensor.price`), and every other id an HMAC of the id keyed by the entry id, `<domain>.e_<10 hex>`. Free text in entry values (anything holding whitespace) is dropped, never masked; text that looks like a street address (`ADDRESS`: a word of 3+ letters, a space, underscore or hyphen, a house number of up to 4 digits and an optional letter) fails `text_ok`. `refusals()` (what `seal()` refuses and `--check` prints) adds an unmasked id and an address-like token to the shape rules, and scrubs every message of the id and the token it refuses, naming the class only. Download diagnostics gets the masking through the same `seal()`.

**3. The leak guard on a real week (`replay_doc.seal`, `export.check_file`).** The owner's second run was refused ("2 dropped credential value(s) survive elsewhere"). The guard searched every dropped string by plain substring, including text dropped only for its shape; a date fragment such as `2026-10` sits inside every ISO time. The first repair (`1363bcf61`) dropped string copies and nulled all 116532 row times of the owner's next export, which passed `--check` (the third run; caught on read-back, never committed). Now: only values that sat under a credential-named key (`Credential`) are searched, as whole tokens (not inside a longer letter/digit run); an ISO time is never a copy; a credential copy in a kept string is dropped; a copy as a number or a key refuses, naming its place (`states[<masked id>].attributes.<key>`) and never the value; Home Assistant's state words (`unknown`, `unavailable`, ...) are not searched. `export.untimed` refuses, at write and in `--check`, a document whose window or row times are not ISO times.

**4. The fixture and the lane (`tools/replay/cut_day.py`, `tests/replay.py`, `tests/replay/owner-2026-10-30-away.json`).** The sealed week export is 13.35 MB and never committed. `cut_day.py` cuts a fixture from it: of every input only the rows in force at the lane's quarter-hour cycle instants (exactly what `run_fixture` reads), the price series and the weather to the export's end (read ahead), no published entity, and two recorded controls: `controls.away`, the owner's away commands (the one published `datetime` entity is the return time; the away switch is the one published switch that turned on within 10 s of it being set; anything else is refused), and `controls.reloads`, the minutes at which every published entity went `unavailable` while every input stayed readable (an in-process reload, not a Home Assistant restart). The lane replays each away command through `coordinator.async_set_away` (what the switch and the datetime entity call), each reload as a new coordinator handed the last publish (`skip_first_solve`, `reload_handover`) with its first light refresh, and now runs the session restore the coordinator spawns after the constructor returns (`RestoringHass`): the stub used to close it, so a reload lost the stored override and the replay showed a defect that is not in the code (measured, below). An Open-Meteo install replays with no solar forecast (the lane opens no socket).

The fixture is 16:00-20:00 local on Friday 2026-10-30, 16 cycles, 39 610 B: the away switch on at 15:42:54Z (return 2026-10-31T19:00Z), the integration reloaded in process at 15:44Z, away off at 18:39:25Z. The new invariant `away` (`away_offenders`): while the recorded command holds away, the plan's view is active, holds the override, and, not recovering, its published floor is at the away target.

**What this gate is, plainly (orchestrator ruling under mandate 6329234399, (a)).** It is a REGRESSION GUARD on the away view across a recorded switch, reload and restore. It detects neither away hotfix's defect: the current head and the tree before both hotfixes (`8327c6e6ecb3c1d5f54bf3dc0235ddabb029348b`, main before #3013) both pass it with 0 offenders and identical away views. R10-HOTFIX-AWAY-SETBACK is unexercised on this install (no weekend or holiday comfort fields are configured: `comfort_temp_day_weekend`, `comfort_temp_night_weekend`, `holiday_comfort_day`, `holiday_comfort_night` all None); R10-HOTFIX-AWAY-LIVE's defect is a timing race (a resolve before the session restore lands, a handover published before the switch's solve) that a recording cannot reproduce, since the lane's restore lands before any resolve; R10-HOTFIX-AWAY-PRESENCE is excluded (`away_presence_entity` is None on this install, and the group had not merged). The fixer contract's "pre-fix fails" is answered by this disclosure and the invariant's own control pairs (`control:away:view`, `control:away:override`, `control:away:floor`), not by a constructed case: a fixture stays a recorded day.

**What the recording shows, labelled comparison only.** Every recorded day ran a build without either away hotfix: both merged on 2026-10-31 (#3013 01:35+01:00, #3015 06:24+01:00), after the export's window, and neither is in a stamped release. The export carries no build version; by stamp tag dates (`git for-each-ref refs/tags/v*`): 10-24..10-27 23:36 at most v7.0.4, then at most v7.0.5 until 10-30 15:59+01:00, then at most v7.1.0. The recorded published entities are what that build did and are not in the fixture; the recorded pump draw (an input) during the away window was 1.92 kWh against 0.73 kWh in the same hours of 10-29.

**The day choice and its size.** 2026-10-30 is the carry's day (the away findings); the export covers 2026-10-24..30 (`--days 7`). Warm-up: the lane cannot seed learned state from history; a run from local midnight (96 cycles) and the cold 16:00 span agree on the away view at every away cycle but not on the plan's energy (15:45Z: 11.37 kWh against 7.0 kWh over the 24 h plan), so the invariant keys on the view, which a cold start reproduces, and the fixture is the span. No contrasting non-away day was added: one cycle of this install costs 15-40 CPU-s here, and the nightly lane replays each fixture four times.

**Cost budget.** Not recorded locally: `cpu_ratio` read 177, 243, 274 and 394 in four clean local runs of this install at load averages 30-200, a spread no 2x band holds. It is recorded from this pull request's CI `replay` job (the lane prints `record:` lines), the second runner class; until `COST_BUDGETS` carries `owner-2026-10-30-away.json`, `cycle_cost` reports `no recorded budget` for it.

## Carries

The group's eleven roster carries (`origin/handoff/audit-r10-roster`, `dev/programme/rosters/wave-r10-groups.json`, R10-REPLAY-REAL-DAY):

- Carry 1 (#2514: the real recorded day is not in the tree): done. `tests/replay/owner-2026-10-30-away.json`, cut from the owner's export (`--days 7 --end 2026-10-31`, the brief's scope addition) after `export.check_file` and `seal` passed on it.
- Carry 2 (classify the new fixture): done for `tests/closures.json` (the `tests/entities.py` and `tests/features.py` sets, beside `synthetic-dhw-only.json`; `tools/replay/cut_day.py` in the `tests/entities.py` set). `COST_BUDGETS` is recorded from this pull request's CI `replay` job, not here (Cost budget above; Carry 10).
- Carry 3 (#2810: a non-credential string collision refuses the whole replay half, naming nothing): done. Only credential-named values are searched now, never text dropped for its shape and never inside an ISO time, and a refusal names each place, never the value (`leak_copy:*`, `seal`).
- Carry 4 and Carry 6 (read `unhealthy_input` from the weekly learner snapshots of the next live bundle; change outdoor's 180 min limit only on that evidence): not done. They read a live diagnostics bundle's learner snapshots, which the replay export does not carry and this seat may not read; the limit is unchanged. Owed to a seat holding the next live bundle, re-homed by the orchestrator (no live group reads one).
- Carry 5 (R10-DIAG-REDACT's redaction on the owner's own exported day): done. `export.check_file` and `seal` on the owner's export: 0 violations, masking checks under `## Figures`; the pre-mask first export is refused by class, never by token.
- Carry 7 (the day choice): done. 2026-10-30, not the fallback: all 26 mapped inputs have a state updated or reported inside 2026-10-30T00:00+01:00..2026-10-31T00:00+01:00 in the owner's export (0 without one, by `quiet_inputs`' rule applied to that day), so the recorder-gap fallback was not needed.
- Carry 8 (D15 L6: the sensors self-test's age rule for a quiet power meter): not done; it needs a live bundle's self-test record, which the export does not carry. Owed with Carry 4.
- Carry 9 (R10-SCORES' `--bundle PATH` scale-drift harness on the owner's house): not done; it needs the owner's diagnostics bundle, not the replay export. Owed with Carry 4.
- Carry 10 (no `loop_cpu_ratio` budget for the real day from one environment): done by not recording one locally; local `loop_cpu_ratio` read 0.137-0.159 at four loads, and the budget waits for the CI runner class.
- Carry 11 (the MariaDB recorder and location masking): done, items (1) and (2) above.

## Head

73ef649127591972b7744a4c2f253eb9bb2f5d6d

## Mutation proof

Phase 1 (`mutants.py`, sha1 29e550f8f9e381d6a54aa795fd772d99a1123f62, out of tree; each mutant against the then-head's `sanitiser_checks` and `tests/debug_collect.py`, the unmutated tree the null, 84/84 and 162/162):
- no db_url from configuration.yaml: red `recorder:db_url_whole_day_read`, `recorder:db_url_secret_resolved`, `recorder:url_from_configuration:inline_quoted` (+8)
- no read-only session: red `recorder:db_url_read_only_session_selects_only`
- URL not redacted: red `recorder:db_url_credentials_never_printed`, `recorder:db_url_connect_refusal_names_no_credential`
- no quiet-input refusal: red `recorder:stale_sqlite_near_empty_day_refused`, `recorder:db_url_emptied_window_refused_naming_inputs_and_recorder`
- `mask()` identity: red `mask:street_in_entity_ids_and_names_absent_from_export`, `synthetic_reproduces`, debug_collect's replay-half check
- no `mask_violations`: red `mask:check_refuses_unmapped_id_naming_class_not_token`, `mask:seal_refuses_unmapped_id_naming_class_not_token`
- refusal not scrubbed: red `mask:check_refuses_unmapped_id_naming_class_not_token`
- no ADDRESS in `text_ok`: red `leak_probe:state_street_number:export_drops`, `mask:check_refuses_address_text_naming_class_not_token`, debug_collect's address-like home name check
- no entry free-text drop: red `leak_probe:entry_free_text:export_drops`, `leak_probe:entry_free_text:check_refuses`
- no `!secret` resolution: red `recorder:url_from_configuration:secret` (+7)
- retired-key filter removed: red `recorder:retired_key_left_out`

Leak guard (in place, restored each time): no `STATE_WORDS` exclusion: red `leak_copy:state_words_under_a_credential_key_not_searched`; no copy drop: red `leak_copy:string_copy_in_attribute_dropped`; unbounded copy: red `leak_copy:null_number_inside_a_longer_one_sealed`; no place list: red `leak_copy:number_copy_refused_naming_its_place_not_its_value`; no ISO-time exemption: red `leak_copy:credential_text_inside_timestamps_keeps_them`; `untimed` dropped from `check_file`: red `mask:check_refuses_a_document_with_its_times_nulled`.

Phase 2 (`mut2.py`, sha1 c0b26da6d2f8eab42c6f926a73866e9408f052b5, out of tree; `cut_day_checks` and the `control:away*` controls at a98bbd40e (the head less a rename and six stale ledger pins), null 0 red):
- no thinning: red `cut_day:every_cycle_instant_reads_as_the_whole_export`
- no read-ahead: red `cut_day:price_series_kept_to_the_export_end`
- a restart counted as a reload: red `cut_day:null_restart_with_inputs_gone_is_no_reload`
- published entities kept: red `cut_day:no_published_entity_kept`
- switch not paired with the return time: `cut_day.cut` refuses the probe document (two switches turn on), so `cut_day_checks` raises
- away floor unchecked: red `control:away:floor`; override unchecked: red `control:away:override`

The session restore in `RestoringHass`: the lane run before it existed is its mutant. On the fixture at head, with the restore closed as before, every one of the 12 commanded cycles read `active=False override=False` (12 `away` offenders, 9.12-19.18 kWh planned); with it, 0 offenders.

## Null control

- `tests/replay/synthetic-dhw-only.json` regenerates byte-identical through `synthesize.py` + `export.py` (`synthetic_reproduces`), and passes `check_file` (`mask:null_committed_fixture_passes_the_check`).
- `recorder:read_key_unrecorded_refused`: an unrecorded entity under a key the integration reads is still refused.
- `leak_copy:null_number_inside_a_longer_one_sealed`, `cut_day:null_restart_with_inputs_gone_is_no_reload`, `cut_day:null_day_without_a_command_has_none`.
- The baseline (`a7dd7f50d`, origin/main at the branch point) on the owner's MariaDB layout, invented: the SQLite-only export wrote "9 entities, 1 state rows" and passed its own check.
- Mold-guard perturbation (below): the same fixture with `mold_guard_enabled` False.

## Figures

- Replay sanitiser, mask, recorder, leak-copy and cut_day checks: 103/103 at a98bbd40e: `PYTHONPATH=tests/hastub python3 -c "import sys; sys.path.insert(0,'tests'); import replay; r=replay.sanitiser_checks(sorted(replay.FIXTURES.glob('*.json')))+[replay.synthetic_reproduces()]; print(sum(x[1] for x in r), len(r))"`
- `tests/debug_collect.py`: 162/162 (`PYTHONPATH=tests/hastub python3 tests/debug_collect.py`).
- The fixture passes the export's check, 0 violations: `python3 tools/replay/export.py --check tests/replay/owner-2026-10-30-away.json`.
- The fixture reads as the export at every cycle instant: 416/416 (input, instant) reads in the window and 64/64 read-ahead reads of `sensor.price` and `weather.weather` equal, `replay.Recording.at` over `cut_day.grid` on the fixture and on `$EXPORT/hpo-replay-2026-10-24_2026-10-30.json` (sha1 8a08433b06733135e20729547a41058d6100be48); whole days 10-29 and 10-30: 2496/2496 each.
- Masking on `$EXPORT` and on the fixture, by rule (the owner's ids from his first export held in memory only): raw ids from the first export found verbatim 0 of 108; address-like strings 0; ids 107 of which 82 hashed and the rest roles, `refusals` empty; numbers with 3+ decimals within 0.01 of the home coordinate: 48 in `$EXPORT`, every one a temperature or power state (paths `states[sensor.wood_tank_bottom]`, `states[sensor.floor_return_temp]`, ...), 0 in the fixture; `entry.options.solar_location` at 2 decimals (`nightly_ha` A10). `git diff origin/main...HEAD` holds none of the owner's address tokens.
- Away replay, 16 cycles, `python3 tests/replay.py --one tests/replay/owner-2026-10-30-away.json`: head 0 `away` offenders, 12 commanded cycles `active=True override=True floor=15.0`, planned space heating 5.51-13.19 kWh per 24 h plan; `8327c6e6e` the same, 0 offenders, 5.51-13.20 kWh.
- Warm-up: the 96-cycle run from local midnight on `cut_day.py --day 2026-10-30` reads `active=True` at every away cycle, 8.49-18.45 kWh planned; the cold span 7.0-13.09 kWh at the same cycles (both without the reload).
- Recorded pump draw, labelled comparison: 1.92 kWh over 15:42:54-18:39:25Z on 10-30, 0.73 kWh over the same hours of 10-29, the integral of the `sensor.heat_pump_power` rows in `$EXPORT`.
- Local cost, not a budget: `cpu_ratio` 177.1, 243.5, 274.3 and 394.1, `peak_kib` 2514-2694, `loop_cpu_ratio` 0.137-0.159, from the `--one` runs' `cost` objects.

## Red checks

- `tests/entities.py` exits on this macOS box at its py-spy sampler (`PermissionError: Cannot get task port`), before the replay checks it carries; the environment, not this diff. The checks it would run here are the 103 above, run directly. CI's Linux run decides it.
- The nightly `replay` lane reports `cycle_cost: no recorded budget` for the new fixture until its budget is recorded from this pull request's CI `replay` job (see Cost budget).
- `mutation` at 73ef64912759: red by construction on the 41 site(s) under `## Unpinned sites`; mutation-autofix pins killed sites after the push.

## Unpinned sites

- `custom_components/heatpump_optimizer/replay_doc.py:336 BOOLOP`: pinned by mutation-autofix (its lane mutates custom_components/)
- `custom_components/heatpump_optimizer/replay_doc.py:336 GUARD_OFF`: pinned by mutation-autofix (its lane mutates custom_components/)
- `custom_components/heatpump_optimizer/replay_doc.py:401 BOOLOP`: pinned by mutation-autofix (its lane mutates custom_components/)
- `custom_components/heatpump_optimizer/replay_doc.py:401 GUARD_OFF`: pinned by mutation-autofix (its lane mutates custom_components/)
- `custom_components/heatpump_optimizer/replay_doc.py:403 GUARD_OFF`: pinned by mutation-autofix (its lane mutates custom_components/)
- `custom_components/heatpump_optimizer/replay_doc.py:526 GUARD_OFF`: pinned by mutation-autofix (its lane mutates custom_components/)
- `custom_components/heatpump_optimizer/replay_doc.py:528 GUARD_OFF`: pinned by mutation-autofix (its lane mutates custom_components/)
- `custom_components/heatpump_optimizer/replay_doc.py:535 GUARD_OFF`: pinned by mutation-autofix (its lane mutates custom_components/)
- `custom_components/heatpump_optimizer/replay_doc.py:542 RETURN_DEL`: pinned by mutation-autofix (its lane mutates custom_components/)
- `custom_components/heatpump_optimizer/replay_doc.py:550 RETURN_DEL`: pinned by mutation-autofix (its lane mutates custom_components/)
- `custom_components/heatpump_optimizer/replay_doc.py:559 BOOLOP`: pinned by mutation-autofix (its lane mutates custom_components/)
- `custom_components/heatpump_optimizer/replay_doc.py:559 GUARD_OFF`: pinned by mutation-autofix (its lane mutates custom_components/)
- `custom_components/heatpump_optimizer/replay_doc.py:561 GUARD_OFF`: pinned by mutation-autofix (its lane mutates custom_components/)
- `custom_components/heatpump_optimizer/replay_doc.py:564 GUARD_OFF`: pinned by mutation-autofix (its lane mutates custom_components/)
- `custom_components/heatpump_optimizer/replay_doc.py:566 RETURN_DEL`: pinned by mutation-autofix (its lane mutates custom_components/)
- `custom_components/heatpump_optimizer/replay_doc.py:568 RETURN_DEL`: pinned by mutation-autofix (its lane mutates custom_components/)
- `custom_components/heatpump_optimizer/replay_doc.py:573 BOOLOP`: pinned by mutation-autofix (its lane mutates custom_components/)
- `custom_components/heatpump_optimizer/replay_doc.py:573 GUARD_OFF`: pinned by mutation-autofix (its lane mutates custom_components/)
- `custom_components/heatpump_optimizer/replay_doc.py:575 GUARD_OFF`: pinned by mutation-autofix (its lane mutates custom_components/)
- `custom_components/heatpump_optimizer/replay_doc.py:577 BOOLOP`: pinned by mutation-autofix (its lane mutates custom_components/)
- `custom_components/heatpump_optimizer/replay_doc.py:577 GUARD_OFF`: pinned by mutation-autofix (its lane mutates custom_components/)
- `custom_components/heatpump_optimizer/replay_doc.py:579 BOOLOP`: pinned by mutation-autofix (its lane mutates custom_components/)
- `custom_components/heatpump_optimizer/replay_doc.py:580 GUARD_OFF`: pinned by mutation-autofix (its lane mutates custom_components/)
- `custom_components/heatpump_optimizer/replay_doc.py:583 RETURN_DEL`: pinned by mutation-autofix (its lane mutates custom_components/)
- `custom_components/heatpump_optimizer/replay_doc.py:589 GUARD_OFF`: pinned by mutation-autofix (its lane mutates custom_components/)
- `custom_components/heatpump_optimizer/replay_doc.py:593 BOOLOP`: pinned by mutation-autofix (its lane mutates custom_components/)
- `custom_components/heatpump_optimizer/replay_doc.py:599 GUARD_OFF`: pinned by mutation-autofix (its lane mutates custom_components/)
- `custom_components/heatpump_optimizer/replay_doc.py:617 RETURN_DEL`: pinned by mutation-autofix (its lane mutates custom_components/)
- `custom_components/heatpump_optimizer/replay_doc.py:648 RETURN_DEL`: pinned by mutation-autofix (its lane mutates custom_components/)
- `custom_components/heatpump_optimizer/replay_doc.py:662 BOOLOP`: pinned by mutation-autofix (its lane mutates custom_components/)
- `custom_components/heatpump_optimizer/replay_doc.py:662 GUARD_OFF`: pinned by mutation-autofix (its lane mutates custom_components/)
- `custom_components/heatpump_optimizer/replay_doc.py:667 GUARD_OFF`: pinned by mutation-autofix (its lane mutates custom_components/)
- `custom_components/heatpump_optimizer/replay_doc.py:672 GUARD_OFF`: pinned by mutation-autofix (its lane mutates custom_components/)
- `custom_components/heatpump_optimizer/replay_doc.py:674 RETURN_DEL`: pinned by mutation-autofix (its lane mutates custom_components/)
- `custom_components/heatpump_optimizer/replay_doc.py:679 GUARD_OFF`: pinned by mutation-autofix (its lane mutates custom_components/)
- `custom_components/heatpump_optimizer/replay_doc.py:681 BOOLOP`: pinned by mutation-autofix (its lane mutates custom_components/)
- `custom_components/heatpump_optimizer/replay_doc.py:681 GUARD_OFF`: pinned by mutation-autofix (its lane mutates custom_components/)
- `custom_components/heatpump_optimizer/replay_doc.py:683 RETURN_DEL`: pinned by mutation-autofix (its lane mutates custom_components/)
- `custom_components/heatpump_optimizer/replay_doc.py:689 GUARD_OFF`: pinned by mutation-autofix (its lane mutates custom_components/)
- `custom_components/heatpump_optimizer/replay_doc.py:701 CMP_BOUND`: pinned by mutation-autofix (its lane mutates custom_components/)
- `custom_components/heatpump_optimizer/replay_doc.py:704 GUARD_OFF`: pinned by mutation-autofix (its lane mutates custom_components/)

`tools/replay/cut_day.py` and `tools/replay/export.py` are `tools/` sites, which `mutation-autofix` does not mutate: each site's mutant and the check it turns red are listed under `## Mutation proof`, run from the out-of-tree harnesses cited there by sha1. The lane's `RestoringHass` and the controls replay in `run_fixture` are pinned by the fixture's nightly `away` check (12 offenders with the restore closed, above).

## Forward-carry

- The mold guard neutralises away mode on this install (a product finding, not this group's fix). With the measured indoor humidity of 52-53 %, outdoor 1-5 °C and `thermal_bridge_frsi` 0.7, `mold_safe_room_floor` gives 19.2-20.9 °C, which `_mold_floor_series` caps at the configured target 19.5 °C and, by design, keeps above the away setback; so on the 2026-10-30 away span the head plans 5.5-13.2 kWh of space heating over each 24 h plan with the view correctly away (floor 15.0) and the plans' predicted room minimum at 19.5-20.6 °C. Perturbation: the same fixture with `mold_guard_enabled` False plans 0 kWh at 11 of 12 away cycles, the room falling to 14.3 °C. The docs must not claim that away mode saves energy while the mold guard holds the floor; the product question goes to tvofi. Lands in `dev/programme/rosters/wave-r10-groups.json`, as a carry of R10-USER-DOCS-VERIFY. Carry: R10-USER-DOCS-VERIFY

## Friction

none
