Closes #2272.

R10-REPLAY-REAL-DAY: the replay lane's first real recorded day. tvofi's 2026-10-30 away episode is cut from his own Home Assistant export, masked, sealed, and replayed through the current coordinator as a nightly regression guard on the away path. This round answers the round-1 verdict and the two CodeQL alerts:

1. **CodeQL alerts 47 and 48 are fixed in code, not argued.** Privacy binds: no address, host, entity id or credential reaches a log or a file.
   - Alert 47 (`tools/replay/export.py`, stderr line naming the recorder): a MySQL/MariaDB recorder is now named by its kind, `MYSQL_LABEL = "MySQL/MariaDB database"`. No text of the `db_url` (scheme, host, port, database) reaches a message. `redacted()` is deleted. A failed connect reports the exception class only, as before.
   - Alert 48 (`tests/replay.py`, the test writing `secrets.yaml`): the invented user and key are named for what they are, canaries the test searches the output for (`_CANARY_USER`, `_CANARY_KEY`). The value is unchanged. I cannot run CodeQL here. If it still reports the site, the alert is a false positive on an invented value in a temporary directory, and dismissing it is the owner's.
2. **`tests / replay`.** The 14 `no_default` offenders were an invariant false positive (the configured `max_temperature`, 21.0, published as the valve target); `SETPOINT_KEYS` exempts a setpoint at the value of its own config option and nowhere else. `COST_ARMS_SKIPPED` runs this fixture once, without the three doubled-cost arms, and the instrument's proof stays on `synthetic-dhw-only.json`. `COST_BUDGETS` carries the fixture. This round re-took no replay figure (see `## Figures`): the diff since the replayed tree touches no file `run_fixture` reads. The job at this head was still running when this body was written.
3. **The `commanded = None` survivor** is killed: `away_offenders(observations, events)` compares every cycle's replayed command with the fixture's own `controls.away`, read apart from the replay. The harness's REPLAY tier shows 12 offenders for the mutant.
4. **Mutation harness in the tree:** `dev/audit/harnesses/r10_replay_real_day_mutants.py` covers every `tools/` and phase-2 site named below.
5. **Carries 4, 6, 8, 9 and the COST_BUDGETS record** have live destinations on the roster ref (`## Carries`).

## Head

d9ca33852a46237af35f6fd65dee3b9d900c8123

- It merges `origin/main` at c3b7c964f6de44eac8d7d6d2bf5afabdb56566ba (without conflict) into the PR head 18bdd5c88acc1581fec86c99b3ccf967ad085ff6, plus one code commit (2042aefb7ad0): `tools/replay/export.py`, `tests/replay.py`, the mutation harness.
- `tools/pr/prepr.sh` ran on this head after the merge (`PRE-PR: ... rc=0`); `structure.py` passed; `ci_predict.py --only mutation` listed no unpinned site before the merge. The scoped gate ran at 2042aefb7 (merge base fb0a6d5a3): `MODE: SCOPED -- 14 script(s) run, 19 scoped out`, `16 TEST SCRIPT(S) PASSED`. Main's delta since then was not read by the replay lane.
- The check-run set at 18bdd5c88 (all 35 runs, one page): no concluded non-green run. `tests / replay`, `tests / mutation`, `tests / fast (3.14)`, `tests / coverage`, `tests / closures`, `codeql / Analyze (python)` were still in progress; `CodeQL` was `neutral`.

## Mutation proof

The in-tree harness, `PYTHONPATH=tests/hastub python3 dev/audit/harnesses/r10_replay_real_day_mutants.py --replay` (FAST tier: each mutant against a fresh interpreter's `controls()`, `sanitiser_checks()` over the committed fixtures and `synthetic_reproduces()`; REPLAY tier: `tests/replay.py --one` on the owner fixture). The FAST tier was run at a6aa0294e5c91fedeeb019c391f7377419b34e7a, and again at 2042aefb7 (the redaction mutant replaced by the label mutant): `RESULT killed=29 mutants=29 null_red=0` both times. Carry 12's mutant is the 29th. The REPLAY tier ran at 37bafc867607baa747e4e65771573b3146bbd6a2 (`--replay`): `RESULT killed=30 mutants=30 null_red=0` over the 28 FAST mutants then present and its two REPLAY rows below. Each row names the check that went red:

- `export.py` no db_url from configuration.yaml: KILLED, red `recorder:db_url_whole_day_read` (+6 more)
- `export.py` no read-only session: KILLED, red `recorder:db_url_read_only_session_selects_only`
- `export.py` URL carried into the recorder label: KILLED, red `recorder:db_url_credentials_never_printed` (+2 more)
- `export.py` connect refusal carries the driver's text: KILLED, red `recorder:db_url_connect_refusal_names_no_credential`
- `export.py` no quiet-input refusal: KILLED, red `recorder:stale_sqlite_near_empty_day_refused` (+2 more)
- `export.py` no !secret resolution: KILLED, red `recorder:url_from_configuration:secret` (+7 more)
- `export.py` no !include followed: KILLED, red `recorder:url_from_configuration:include`
- `export.py` retired-key filter removed: KILLED, red `recorder:retired_key_left_out`
- `export.py` untimed dropped from check_file: KILLED, red `mask:check_refuses_a_document_with_its_times_nulled`
- `cut_day.py` no thinning: KILLED, red `cut_day:every_cycle_instant_reads_as_the_whole_export`
- `cut_day.py` no read-ahead: KILLED, red `cut_day:price_series_kept_to_the_export_end`
- `cut_day.py` a restart counted as a reload: KILLED, red `cut_day:null_restart_with_inputs_gone_is_no_reload`
- `cut_day.py` published entities kept: KILLED, red `cut_day:no_published_entity_kept`
- `cut_day.py` two paired switches not refused: KILLED, red `cut_day:two_paired_switches_refused`
- `replay_doc.py` an _entities list not claimed (GUARD_OFF): KILLED, red `mask:entities_list_ids_take_their_numbered_role`
- `replay_doc.py` ids in a list not collected (GUARD_OFF): KILLED, red `mask:id_only_as_a_list_item_refused`
- `replay_doc.py` a payload that is no document read as one (GUARD_OFF): KILLED, red `mask:a_payload_that_is_no_document_has_no_violation`
- `replay_doc.py` a list not scanned for credential copies (GUARD_OFF): KILLED, red `leak_copy:copy_inside_a_list_dropped`
- `replay_doc.py` dict keys outside states not renamed: KILLED, red `mask:id_as_any_dict_key_renamed_and_refused_unrenamed` (+22 more)
- `replay_doc.py` dict keys not collected: KILLED, red `mask:id_only_as_a_states_key_refused` (+1 more)
- `replay_doc.py` a bool under a credential key read as a credential (carry 12): KILLED, red `leak_copy:bool_under_a_credential_key_is_no_credential`
- `replay.py` away floor unchecked: KILLED, red `control:away:floor`
- `replay.py` away override unchecked: KILLED, red `control:away:override`
- `replay.py` away command not compared with the recording: KILLED, red `control:away:replayed`
- `replay.py` no_default setpoint exemption removed: KILLED, red `control:no_default:setpoint_value_on_a_reading` (+1 more)
- `replay.py` no_default setpoint exemption on every entity: KILLED, red `control:no_default:setpoint_value_on_a_reading`
- `replay.py` no_default setpoint at any value: KILLED, red `control:no_default:setpoint_at_an_unconfigured_default`
- `replay.py` not_frozen counts a zero as a mirrored value: KILLED, red `control:not_frozen:one_value_beside_zeros`
- `replay.py` arms skipped everywhere allowed: KILLED, red `control:cycle_cost:arms_skipped_never_everywhere`
- `replay.py` the recorded away command not replayed (round 1's survivor) (REPLAY tier): KILLED, the fixture's `away` 12 offender(s), every other count 0
- `replay.py` no_default setpoint exemption not handed the config (REPLAY tier): KILLED, the fixture's `no_default` 14 offender(s), every other count 0

**The reviewer's surviving mutant** (`commanded = returns if active else None` -> `commanded = None` in `run_fixture`) is killed by the REPLAY tier. The fixture's `away` result shows 12 offenders ("the recorded command holds away=True, the replay carried away=False"). In round 1 it showed 0.

The `replay_doc.py` sites are mutated by CI's lane too. Their ledger pins are under `## Unpinned sites`.

## Null control

- The harness's unmutated copy: red [] (FAST tier). The REPLAY tier's null replay of the owner fixture reads `away` 0 and `no_default` 0.
- `no_default`: `control:no_default:setpoint_value_on_a_reading` and `control:no_default:setpoint_at_an_unconfigured_default`. The same 21.0 on a reading entity, or the setpoint at a default the config does not hold, still fires. `control:no_default:setpoint_keys_are_published_config` checks that each key is a sensor in strings.json, that each option is a `CONF_*` value, and that `recommend_target(comfort_max=21.5)` returns 21.5.
- `not_frozen`: `control:not_frozen` (a mirror that tracked 1.0 and 3.0, then stuck) still fires. `control:not_frozen:one_value_beside_zeros` is the owner day's exact shape and does not fire.
- `away`: `control:away:replayed`. An observation the events hold away but the replay did not carry is red, and one after the command ended is not.
- Masking: `mask:id_as_any_dict_key_renamed_and_refused_unrenamed` reads red at 4c994241d's `replay_doc.py`: a key built on the invented test street `_STREET` survives `mask_ids`, and `mask_violations` finds 0. At this head it reads green. The other five `mask_seam_checks` are green at both, because they pin the existing behaviour at the unpinned sites.
- Reviewer's duty-F null (`dbg_null.py`, the reviewer's file at `probe/rev-3078-9c03b1c0:ev/dbg_null.py`): a fixture whose price entity keeps a raw-shaped id gives 5/5 at both ends.

## Figures

All figures were measured on one 4-core Linux container, Python 3.14.7, `OPENBLAS_NUM_THREADS=1`, unless stated otherwise.

- **The finder's harness at both ends.** The reviewer's driver is `tests/replay.py --one tests/replay/owner-2026-10-30-away.json` with `HASTUB_TZ=Europe/Stockholm PYTHONPATH=tests/hastub`, summarised by the reviewer's summariser (`git show origin/probe/rev-3078-9c03b1c0:ev/summ.py`).
  - At 4c994241d: `no_default` 14 (each `sensor.heat_pump_optimizer_valve_target_recommendation=21.0`), `not_frozen` 1 (this box only; the reviewer's and CI's runs read 0), `away` 0, 12 commanded cycles, views `[(True, True, False, 15.0, 15.0)]`, `cycle_cost` 3 (no recorded budget). 694.8 s.
  - At 37bafc867607baa747e4e65771573b3146bbd6a2: `finite`, `unit`, `no_default`, `agreement`, `cycle`, `not_frozen`, `away` and `cycle_cost` all 0. 12 commanded cycles, the same views, planned space heating 5.51-13.2 kWh per 24 h plan at both ends. Cost `cpu_ratio` 268.8, `peak_kib` 2541.3, `loop_cpu_ratio` 0.1847, inside the recorded band. 689.9 s.
  - Later commits change no file the replay reads (see `## Head`).
- **The reviewer's `dbg_null.py`** (`python3 dbg_null.py <tree> <mode>`):
  - 4c994241d: plain 5/5, unrenamed 5/5, none 4/5, absent `KeyError: 'price_entity'`.
  - This head: plain 5/5, unrenamed 5/5, none 4/5, absent `KeyError`.
  - The 4/5 the verdict recorded was at df35202ab; d6a8661e8's fix is in both trees.
- **Carry 12**, by `export.violations` (`PYTHONPATH=tests/hastub:tools/replay:custom_components python3 -c "import export; print(export.violations({'tibber_reauth_started': True}))"`):
  - At 4c994241d, `{"tibber_reauth_started": True}` gives 1 finding ("a credential-named key carries a value"). At this head it gives 0.
  - Null: `{"tibber_token": "abc123xyz"}` gives 1 finding at both.
  - debug_ingest's stage-2b plant (`debug_ingest.PLANTED_SECRET` in a state row) gives `planted_leak_caused_violations=2` at both, and `debug_ingest.gate_checks()` gives 3/3 at both.
- **The `no_default` disposition, by perturbation.** `tests/replay.py --one <fixture> --step-minutes 60` at 4c994241d gives 3 offenders over 4 cycles. The same fixture with `entry.data/options.max_temperature` 21.5 gives 0.
- **The `not_frozen` mechanism**, by a spy on `frozen_offenders` and `power_ratio` in an unchanged `run_fixture`, on the tree before the `not_frozen` change:
  - `power_ratio` read `[None, None, 0.0, None x8, 0.0, 1.55, 1.55, 1.55, 1.55]`.
  - `heat_pump_power` read `[0.0 x12, 1.55, 2.89, 3.02, 0.0]`.
  - The last samples (predicted, actual) were `(0.5, 0.0), (0.5, 1.55)`, then predicted 0.0, which is unusable.
- **Lane wall time.** `PYTHONPATH=tests/hastub python3 tests/replay.py` at 37bafc867 prints `replay lane wall time 765.8 s` (`time`: 12m46s real), under load average 3.6-4.9 (the mutation drives were running beside it). It also prints `1 of 167 replay checks FAILED`: `synthetic-dhw-only.json: cycle_cost [cpu_ratio 2.292 over its budget 2.173 | loop_cpu_ratio 0.1723 over its budget 0.143]`. That red belongs to this box, not to this diff. Interleaved `--one` runs of the synthetic fixture under the same load read `loop_cpu_ratio` 0.150-0.159 at 4c994241d and 0.153-0.162 at this head, both over 0.143. `cpu_ratio` read 2.09-2.12 against 2.04-2.18. No timed line changed: the invariants this round touched run outside the timed span. The 0.143 budget's own comment records an idle 4-core box reading 0.109-0.124. This box is Python 3.14 under load. The owner fixture's single replay is 682-695 s of it. Before this round, the fixture alone was four of those replays, about 46 CPU-minutes, against the job's `timeout-minutes: 30`.
- **The recorded `COST_BUDGETS` entry** is `cpu_ratio` 355.7, `peak_kib` 3740.0, `loop_cpu_ratio` 0.249. Each is sqrt(2) x the geometric midpoint of the extremes of the clean `--one` readings, from the cost objects of those runs:
  - `cpu_ratio`: Linux only, 217.8-290.5. The readings are CI 249.0 (the `record:` line 352.1 / sqrt(2)), the reviewer's box 217.8 and 278.7, and this box 231.8 and 290.5. The band floor is 177.9.
  - `peak_kib`: 2514-2783, adding the first fixer's M1.
  - `loop_cpu_ratio`: 0.137-0.227, the M1 included. The edges are 9-10 % inside.
- **Mutation-autofix at 4c994241d:**
  - `ci_predict.py --only mutation` lists 7 `ADDED UNPINNED` sites at 4c994241d: replay_doc.py 535 GUARD_OFF, 577 BOOLOP, 577 GUARD_OFF, 579 BOOLOP, 580 GUARD_OFF, 589 GUARD_OFF and 672 GUARD_OFF. The 34 pinned plus these 7 make the 41.
  - At this head it lists none. The four sites left after this round's simplification are pinned by `python3 tests/mutation_table.py --pin-killed --base 61b0076f4854`, which printed `PIN KILLED: 4 pinned, 0 left unpinned`, each `killed by tests/entities.py`.
  - Command: `PYTHONPATH=tests/hastub python3 tools/pr/ci_predict.py --base $(git merge-base origin/main HEAD) --only mutation`.
- **The scoped gate:** `GATE_SCOPE=auto GOLDEN_MODE=drift GOLDEN_REF=<merge base> PYTHONPATH=tests/hastub bash tests/run.sh`.
  - At this head, merge base 1a8051350, it printed `MODE: SCOPED -- 14 script(s) run, 19 scoped out` and `16 TEST SCRIPT(S) PASSED; 18 SCOPED OUT AND NOT RUN`, `tests/entities.py` included (468 s).
  - At a6aa0294e, merge base 61b0076f4, it printed `MODE: SCOPED -- 14 script(s) run, 19 scoped out` and `16 TEST SCRIPT(S) PASSED; 18 SCOPED OUT AND NOT RUN`, `tests/entities.py` included (521 s).
  - The earlier run at de065d394 failed only `tests/harness_headers.py`'s `every inlined walk matches the canonical helper`: the new harness's `repo_root` had dropped the helper's inner `from pathlib import Path`. a039a0409 restored it.
- `python3 tests/structure.py`: STRUCTURE RATCHET PASSED. `python3 -I tools/audit/archscore/gate.py --base 1a8051350406 --head <head> --body <body>` at this head: dS +0.0000, no gate metric rose.
- **Not re-derivable in CI, and unverified by review:** these need the owner's untracked export, which no seat holds. The warm-up claim has no null control.
  - The round-1 warm-up claim: 96 cycles from local midnight against the cold span; the away views agree; plan energy 11.37 against 7.0 kWh, and 8.49-18.45 against 7.0-13.09 kWh.
  - The export-side masking figures: 0 of 108 raw ids, 48 near-coordinate numbers in `$EXPORT`, 416/416 and 2496/2496 reads.
  - The recorded pump draw comparison: 1.92 against 0.73 kWh.

## Red checks

- `CodeQL`, red at 4cccd845f: code-scanning alert 47 (py/clear-text-logging-sensitive-data) at `tools/replay/export.py`'s recorder stderr line and alert 48 (py/clear-text-storage-sensitive-data) at `tests/replay.py`'s `secrets.yaml` write.
  - **Fixed in code** (the opening's item 1). Alert 47: the label carries no text of the URL, so nothing derived from the credential-bearing string is logged; `recorder:db_url_credentials_never_printed` still requires the kind label as its positive control, and the mutant that carries the URL into the label is killed by it. Alert 48: the invented user and key are renamed as canaries; the file write is the input the never-printed checks need.
  - Not verified locally: CodeQL does not run in this seat. At 18bdd5c88 the `CodeQL` run is `neutral` and `codeql / Analyze (python)` was still in progress.
  - Cause: new code that handled a database URL. Cheaper detector: none before the push; CodeQL is the cheapest detector of its own alerts. No countermeasure is owed beyond this answer.
- `tests / replay`, cancelled at 4cccd845f. It hit `timeout-minutes: 30` in the fixture's memory-doubled arm, after `no_default` (14) and `cycle_cost` (no recorded budget, so "sees a doubled cycle" could not fire) had failed.
  - Cause: the fixture's four replays, about 12 CPU-minutes each, and two invariant false positives on a real day (Figures).
  - Cheaper detector: one local `tests/replay.py --one` on the fixture. Round 1 ran it and read only the `away` result, while its `counts` already printed `no_default` 14. The four-replay arithmetic was also in round 1's own body ("replays each fixture four times", "15-40 CPU-s" a cycle). Standing cost: zero for the counts; one ~12-minute run for the timing.
  - Fixed here: `SETPOINT_KEYS`, the non-zero mirror rule, `COST_ARMS_SKIPPED` and the recorded budget.
- `tests / mutation`, red at 4cccd845f on the 41 unpinned `replay_doc.py` sites. It is red by construction: `mutation-autofix` pinned the 34 its drivers killed (4c994241d). The other 7 survived because no check drove them. They are dispositioned under `## Unpinned sites`. Cheaper detector: `prepr.sh` step 6d lists every unpinned site in seconds. A site no check drives stays unpinned until a check is written, which is what this round did.
- `tests / fast (3.14)`, red at df35202ab and answered in round 1. `tests/entities.py` failed `debug replay: trim_replay carries sparse export attributes forward [nordpool_rows_with_raw_today=0]`.
  - Cause: `tools/replay/debug_replay.py` named the synthetic fixture's price entity by its raw id, which the masking renames to `sensor.price`. d6a8661e8 fixed it by reading the id the fixture's entry holds. The reviewer's `dbg_null.py` gives 5/5 at 4c994241d and at this head (`## Figures`).
  - Cheaper detector: the local scoped gate. It runs `tests/entities.py`, which carries the check, in minutes instead of a CI round. On the round-1 macOS seat it was blind: `tests/entities.py` exits at its py-spy sampler (`PermissionError: Cannot get task port`) before it reaches the check. On this Linux seat it runs to the end (`## Figures`, the scoped gate). The countermeasure, a sampler that skips rather than exits where the task port is denied, belongs to a root-cause seat, not this fix.
- `pr-contract / pr-contract` and `gate`, failure at 4cccd845f. `pr-contract` refused the body with 3 errors, all of them the unanswered reds above (CodeQL, alerts 47 and 48). `gate` failed on the same refusal in run 41273345201, reported as "unreadable title". This body answers them. Cheaper detector: `tools/pr/prepr.sh`'s body check, which reads the PR's check runs only once a PR exists. Before then it cannot see a CodeQL alert, so none further exists for a seat.

## Unpinned sites

None at this head. `ci_predict.py --only mutation` lists no `ADDED UNPINNED` site. The seven sites 4c994241d left unpinned (all `custom_components/heatpump_optimizer/replay_doc.py`, at 4c994241d's line numbers), each with its disposition:

- `:535 GUARD_OFF` (`entity_roles`, an `_entities` list): pinned at this head, `entity_roles.GUARD_OFF.97aacf73`, killed by `tests/entities.py` through `mask:entities_list_ids_take_their_numbered_role`.
- `:577 BOOLOP`, `:577 GUARD_OFF`, `:579 BOOLOP` (`_entity_ids`'s `keyed` logic): removed with that logic. Every dict key is now collected, and the site no longer exists. Driving them is what exposed the masking hole (the opening's item 6).
- `:580 GUARD_OFF` (ids in a list): pinned, `_entity_ids.GUARD_OFF.50e92e5d`.
- `:589 GUARD_OFF` (a non-document payload): pinned, `_unmasked.GUARD_OFF.14f861a9`.
- `:672 GUARD_OFF` (a list scanned for credential copies): pinned, `_scan.GUARD_OFF.08da69e4`.

- Carry 12 adds three sites, each pinned by `mutation_table.py --pin-killed` (`PIN KILLED: 3 pinned, 0 left unpinned`): `:416 RETURN_DEL` (`_no_credential`, killed by `tests/entities.py`), `:423 BOOLOP` (killed by `tests/debug_collect.py`) and `:423 GUARD_OFF` (killed by `tests/structure.py`). Its edit staled the two `_walk` pins on the old one-line guard, `_walk.BOOLOP.5476d757` and `_walk.GUARD_OFF.5476d757`. Both were deleted by hand, as `ci_predict.py` names that repair, and the new line is pinned afresh above.

The seven were unpinned because no check drove those branches, so no driver could kill them: they were survivors, not unevaluated sites. None was dropped silently.

## Carries

Roster `origin/handoff/audit-r10-roster` at 806d2db83aa080b0cfb3ad9926c48e648e109a7b (`git show 806d2db83aa080b0cfb3ad9926c48e648e109a7b:dev/programme/rosters/wave-r10-groups.json`), group R10-REPLAY-REAL-DAY, `carry` list.

At 806d2db83, no group other than R10-REPLAY-REAL-DAY carried carries 4, 6, 8, 9 or 10's open half. The only matches were in done groups (R10-PARAMS-OWNER, R10-HEAT-METER, R10-REPLAY-LANE), which is the verdict's Block 3.

At the roster's tip when this body was written, 3f6dc470fa20b89cca1473f67c12715a50b7d3e0 (`git show 3f6dc470fa20b89cca1473f67c12715a50b7d3e0:dev/programme/rosters/wave-r10-groups.json`, read by this seat; the group objects' `after`, `carry` and `size` fields), the orchestrator has added two live groups, both `not-started`, both `after: R10-REPLAY-REAL-DAY`:

- **R10-LIVE-BUNDLE-READS** holds carries 4, 6, 8 and 9, verbatim, as its carries 1-4 (it holds 5 carries; the fifth is D15-s1-01).
- **R10-REPLAY-COST-BUDGET** holds the COST_BUDGETS record, owed from the second runner class. This pull request now records a budget, so that group's remaining work is carry 10's open half: re-centring on the other CI class's reading. Its carry text quotes round 1's body ("Not recorded locally"), which this round supersedes. The orchestrator should restate it before dispatch.

This seat cannot edit the roster. Before merge, the orchestrator confirms that both groups are still live at the roster SHA it merges against.

- Carry 12, from the round-10 register: D15-s1-04, "export credential-named-key rule flags a boolean value". Done in this round (the opening's item 7, `## Figures`).
- Carry 1 (the real day), carry 2 (classify the fixture; COST_BUDGETS is now recorded), carry 3 (#2810), carry 5 (R10-DIAG-REDACT on the owner's day), carry 7 (the day choice) and carry 11 (MariaDB and masking): done, as round 1 recorded.
- Carry 4, verbatim, not done (it needs a live diagnostics bundle, which the replay export does not carry and this seat may not hold):
  > From R10-HEAT-METER (#2261; D15 lead L9, finding-propagation.md). Each weekly learner snapshot now records `unhealthy_input`. It holds the first reason `_inputs_unhealthy` gave on that day: the rule over the indoor, outdoor and power inputs that marks a snapshot unhealthy. The house meter is not one of its inputs. On a healthy day it holds None. Read it in the next live bundle. Name which input marked each unhealthy weekly snapshot, and say whether that input was genuinely silent or whether outdoor's 180 min on-change limit flagged a quiet, healthy sensor. Change that limit only on that evidence. Controls: a week with every input reporting marks the snapshot healthy and names none (null); a week with one input silent all day names that input.
- Carry 6, verbatim, not done (the same live bundle):
  > **R10-REPLAY-REAL-DAY** carry 4 (D15 lead L9), in its brief on `origin/main`: read `unhealthy_input` from each weekly learner snapshot in the next live bundle, name the input that marked each unhealthy snapshot, and change outdoor's 180 min on-change limit only on that evidence. Controls: a week with every input reporting names none (null); a week with one input silent all day names that input. Carry: R10-REPLAY-REAL-DAY
- Carry 8, verbatim original text (STRANDED CARRY 34, from R10-HEAT-METER), not done (it needs a live bundle's sensors self-test record):
  > D15 live-bundle lead L6 (owner install; unverified): at finalisation the sensors self-test flagged the house-power meter as a problem input, 238 min old, while the current `data.inputs` reports health `ok`; historical only. VERIFY with the input-freshness work of this group: read the sensors self-test's age rule for a power entity and decide whether a change-reporting meter on a quiet circuit can age past it without an outage. If it can, key the age on the entity's last report time and the integration's own sample, not on the last change. Controls: a power entity that reports a constant value for 4 h is not flagged when its last_updated advances (null: a real silence over the threshold is flagged); one mutant that reads last_changed. (triage: dev/programme/triage/s6-batch24.md#P118)
- Carry 9, verbatim original text (STRANDED CARRY 54, from R10-PARAMS-OWNER), not done (it needs the owner's diagnostics bundle):
  > From R10-SCORES (handoff-body/r10-scores at 8f564875), Forward-carry: **Blocked, not designed around:** the owner's bundle is not in this container, so the suspected 2.6x scale drift and the band on the owner's own house are unmeasured. The harness takes `--bundle PATH` and prints the stored scale, split and samples and the grade on both bases. A local seat with the bundle runs the harness with `--bundle PATH` as part of that group.
- Carry 10, verbatim original text (STRANDED CARRY 57, from R10-REPLAY-LANE), **half done**. The budget is recorded at the centre of a spread over four environments (`## Figures`). Those environments hold one CI class, not the two the carry asks for. The open half is to re-centre on the second CI class's reading, from the next nightly `slow` lane or a CI `replay` job on the other runner class. That is R10-REPLAY-COST-BUDGET's work (see above):
  > R10-REPLAY-LANE must not record a loop_cpu_ratio budget for the real-day fixture from one environment. The same code reads 0.0823-0.1236 (1.50x) across four environments, and ruler speed does not predict it: an idle 4-core box with a 172-190 ms ruler reads 0.109-0.124. Either record at the centre of a spread measured in at least the two CI classes plus one box outside them, or replace the absolute band with a reference measured in the same job (the loop against a fixed tree, on the same runner) so the box cancels. Until then, 0.143 holds only the 1.50x measured here. (source #2548 round 2; replaces the round-1 text)

## Forward-carry

- **The mold guard neutralises away mode on this install.** This is a product finding, not this group's fix, and is unchanged from round 1. It lands as a carry of R10-USER-DOCS-VERIFY in `dev/programme/rosters/wave-r10-groups.json`: the "From R10-REPLAY-REAL-DAY (orchestrator s9, 2026-11-01)" entry, present at 806d2db83. Carry: R10-USER-DOCS-VERIFY

## Friction

none

## Self-correction

The commit `replay: record the owner fixture's cost budget` names this seat's container as a "Python 3.13 venv". It is Python 3.14.7. The CI replay job is 3.13.
