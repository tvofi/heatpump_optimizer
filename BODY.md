R10-GENERIC-HEAT-CURVE, kind `offset` (design option (a)): the heat-curve displace reaches a Home Assistant `number` entity, and the shared off/unload restore hook the two later groups reuse. Built under the owner's ruling (tvofi, #201, 2026-11-07: "Yes, it should be built. Offset kind and a later persistent kind, both in this round. Turning the optimizer off should restore the baseline, retract my 26 september ruling") and the approved design (`Design review: approve 6564b0c7f40c5c81b7d9556ed3dcda8926d91bad`, note `design.md` on `design/R10-GENERIC-HEAT-CURVE`). Outside contribution: PR 3284 by Bankaifan; the design note and probe were read as data, nothing from the fork was run. There is no finding and no issue to close: the build is the owner's ruling.

**What changed.**
- `heat_curve.py` (new) owns the displace's fan-out: the ECL110 `/set` and legacy JSON MQTT arms, moved verbatim from `coordinator.py` (`ecl110_legacy_payload`, `publish_ecl110_topics`), then an entity arm. `async_publish_ecl110_command` still forms the one integer (plan, fixed modes, boost, peak guard, curve bias) and hands it to `heat_curve.publish`; two coordinator stores (`_ecl110_displace_set_topic`, `_ecl110_retain`) are deleted for the entry config.
- Entity arm, kind `offset`: the integer as a temperature difference in the entity's own unit (K, °C or no unit as is, °F ×9/5, any other unit refused), never through the absolute set-point helpers; bounded to ±`heat_curve_offset_band_k` (default 3 K, 0.5–5 K) and the entity's range. W1 write-on-change, W2 held record with its own `HELD_GRACE_S` (90 s, reasoned in code: not the arbiter's Tuya-calibrated `ECHO_GRACE_S`, ghc-r05), W3 give-up latch, W4 `2 × 1440 / interval` guard, W6 saturation latch, T2 range-excludes-0 refusal at save and at every write by one rule (`heat_curve.range_excludes_zero`). The raw reading comes from `inputs.number_reading`, the module that owns entity reads.
- `off_restore.py` (new): the one owner of the off/unload restore. MODE_OFF (through `off_restore.async_mode_change`, called from `async_set_mode`) and `async_unload_entry` write 0 to an offset entity the optimizer wrote; `async_remove_entry` only drops the persisted record (`async_forget`), so the restore has one owner (the note's O4). While off the arm writes nothing. MQTT arms unchanged (W7; ghc-d02 is the owner's).
- Options: `heat_curve_displace_entity` (`number`, `input_number`), `heat_curve_target_kind` (`offset` only), `heat_curve_offset_band_k`; the page is "Heat curve control". `ECL110_TOPIC_SLOTS` gains the entity key. The entity is refused when it equals an entity the optimizer already writes, on every page's save and on the pre-fill save (ghc-r03). Factory reset keeps the kind beside its entity (ghc-d03).
- Docs: `docs/ecl110.md` "Without MQTT: a number entity" (T1–T3 contract, W1–W6, the off rule with the stop case, the Luxtronik SHI example with U1, U2 and ghc-r04, python-luxtronik cited at `02afea84bd5bf3ee87445de6f2a42b8029983169`), `docs/configuration.md`, `README.md`, `docs/architecture.md`.

**The restore hook's interface, which R10-ARBITER-OFF-RESTORE and R10-GENERIC-HEAT-CURVE-PERSISTENT call unchanged.**
- `off_restore.register_consumer(key, factory)` at import; `factory(config)` returns `off_restore.Restorer(entity_id, write, neutral=None, baseline_of=<(hass, entity_id) -> float | None>)`, or `None` when unconfigured.
- `await off_restore.async_arm(hass, entry, config, key)` before each write: the first arm captures `baseline_of(...)` for a consumer with no `neutral` and persists it per entry (store `heatpump_optimizer_<entry_id>_off_restore`), so a restart never re-captures a value the optimizer wrote (the note's O3); `False` refuses the write (no readable baseline).
- The coordinator and `__init__` call `async_mode_change`, `async_restore` and `async_forget`; a consumer never does. A restore write bypasses the consumer's own policy, is counted (`off_restore.diagnostics`), and a failure is latched and keeps the consumer armed for the next off or unload.
- Shown by the check "a stand-in second consumer registers without editing the hook: its baseline, captured before its first write, survives a restart and is what the restore writes" (tests/features.py, section R10-GENERIC-HEAT-CURVE). The arbiter's own MODE_OFF branch (`pump_arbiter._arbitrate`) is untouched here.

**Alternatives, and why each lost.** (1) Pass the coordinator to `heat_curve`/`off_restore` (the note's shape): `tools/audit/archscore` charged every function handed it (coord_footprint 2491 → 2563); keying on the config entry costs one `views` seam cross (`self.entry`) and keeps the score NULL. (2) The restore in `async_publish_current_action`: returns early on MODE_OFF and is not called on unload (verdict note). (3) A Store-free baseline in the options (the note's P1): every write of it reloads the entry (O1); the per-entry store does not. (4) Hand-rolled reads of `state.state`/`min`/`max` in `heat_curve`: a float of entity state outside `inputs.py` (entities.py P8); `inputs.number_reading` owns it. (5) Repeating entity, kind and band in the diagnostics section: they are the config section's; the heat-curve section carries numbers only.

**Write-endurance carry** (12 writes/day, Daikin 7000/yr) binds the persistent kind only and is not built here.

**Toolchain.** `bash tools/audit/seat/cloud-setup.sh` then `--check`: OK, python3 is venv-ci's; numpy 2.5.4 and scipy 1.18.1, matching `tests/requirements-ci.txt`.

**Repair round (this head).** The reds at `e330a7681c5b5e4ac416e0b8ed4270a857e89ab2` were this branch's own; five commits answer them and touch no production line: `tests/features.py`, `tests/golden/config_flow.json`, `tests/golden/claimed_drift.txt` and two `tests/mutation_ledger/survivor_triage/` records.
- `tests / fast (3.14)`: `tests/env_drift.py --all` found the float-free `config_flow` fixture STALE and its drift UNCLAIMED (the heat_curve page's three new options and the menu label). Re-recorded with `golden.py --record --only config_flow`, which a float-free fixture allows on any machine, and claimed in `claimed_drift.txt` under `claims-for: 7.1.5`; no other fixture or claim line moves.
- `tests / coverage-ratchet`: `off_restore.py` at 90.10 % (ten missed lines: the save and remove failures, a refused arm, the unconfigured disarm, a raising restore write). New checks drive each through the production functions; the module measures 100 % under `tests/features.py` alone.
- `tests / mutation` and `tests / mutation-autofix`: the 71 sites CI listed as ADDED UNPINNED. Each one is now killed by a driver CI runs, or triaged equivalent with its measurement (two sites). The new checks in the section are the kills.

## Head

`fb9b2313ec06b69c6810df8a49457daf509b3b17`. It merges the PR head `30e7024e81f409e60803ab25928ed6f7d717d527` into this round's code head `90d3265e87bfad1901dc3f580f5b03f3d483d006`; the merge resolved cleanly. `30e7024e8` is the merge-main bot's `ci: merge main` on `e330a7681c5b5e4ac416e0b8ed4270a857e89ab2`, bringing origin/main to `15e34edb8b1c`, now the merge base. `90d3265e8` is five commits on `e330a768`, and they touch no production line. The merge was needed so the handoff fast-forwards from the PR head (prepr's push-order step refused the unmerged `90d3265e8`); it is not a merge of a moved main.

Where each figure was measured. The mutation proof, the diff-mutant and spec passes, the coverage run and the first suite pass ran at `90d3265e8` over merge base `53273de4d`. After the merge these re-ran at `fb9b2313e` over `15e34edb8`: `tests/features.py`, the section block, the scoped five (`tests/closure.py select` over this round's commits still names config_flow_steps, entities, env_drift, features and golden), `structure.py`, `closure.py selftest`, `tools/pr/prepr.sh`, and its body check. The merged delta touches `coordinator.py` and `tests/features.py`, never `heat_curve.py`, `off_restore.py` or `config_flow.py`, so the mutant sites keep their lines and text. `origin/main` was at `e36e5327d` at 2026-11-08 UTC. `git merge-tree --write-tree origin/main HEAD` reports no conflict (`tests/closures.json` resolved by the ledger driver), so main was not merged, per the owner's 2026-11-07 ruling.

## Mutation proof

Each mutant is one named production edit, applied in a `git archive` copy of the head, run, and restored. The driver is the `R10-GENERIC-HEAT-CURVE` block of `tests/features.py` through `tools/audit/seat/features_block.py` (the `MUTANT_CMD` under Figures). The failing check names, as printed:

```
BASELINE (unmutated head): rc=0, 0 failing

M1 entity arm call deleted (heat_curve.publish): rc=1, 26 failing
    FAIL no topic and an offset entity: one publish of 5 sends one set_value of 5 (R10-GENERIC-HEAT-CURVE)  [writes=[] mqtt=[]]
    FAIL both configured: MQTT first with the full integer, the entity bounded by the 3 K default band  [[('mqtt', 'publish', {'topic': 'ecl/set', 'payload': '5', '
    FAIL a kelvin entity is sent -2 for -2, never 271.15 through the absolute helpers (T1)  [[]]
    FAIL a Fahrenheit entity is sent the difference x9/5: 2 K is 3.6 °F (T1)  [[]]
    FAIL an entity range narrower than the displace saturates and is latched once, naming it (W6)  [writes=[] warn=[]]
    FAIL inside the grace a differing reading proves nothing: no second write (W2)  [[]]
    FAIL after the grace the first miss is written once more (W2)  [[]]
    FAIL a second miss for the same target latches a warning and sends nothing (W3)  [writes=[] warn=[]]
    FAIL and a new target is written again (W3)  [[]]
    FAIL at the guard nothing is written and it is latched; one below it the write goes (W4)  [at=[] below=[] warn=[]]
    FAIL absent, unavailable, a non-temperature unit, a sensor, a range without 0 or a raising service: no value lands, the failure is latched, the MQTT arm still p
    FAIL MODE_OFF after a write writes one 0 (the off rule)  [[]]
    FAIL and while off the arm writes nothing, nor does a second off  [[]]
    FAIL unload after a write writes one 0, through async_unload_entry (the off rule)  [ok=True writes=[]]
    FAIL a write left armed by a crash is restored by the next run's first off  [[]]
    FAIL a range narrower than the displace saturates on the low side too: -3 K sends -2 (W6)  [[]]
    FAIL a target within half a step of the last write is that write, still in its grace: 3 after 2 at step 2 sends nothing (W2)  [[]]
    FAIL a reading that held clears the misses, and the grace is 90 s: a miss 91 s after the write is written once more, not given up (W1, W2)  [writes=[] misses=0]
    FAIL writes older than 24 h leave the guard: a full day of them 24 h and 1 s old blocks nothing (W4)  [writes=[] kept=96]
    FAIL at exactly 90 s the grace is over: a miss then is written once more (W2's bound)  [[]]
    FAIL a write that succeeds clears the failure latch, and so does a readable entity: the next failure is warned again, not swallowed  [write=[0, 1] entity=[0, 0,
    FAIL the heat-curve diagnostics: zeros before any write, the write and its 24 h count after one  [fresh={'written': None, 'misses': 0, 'writes_24h': 0, 'write_c
    FAIL publish called without mode_off writes the entity: only the off mode suppresses the arm  [[]]
    FAIL a heat-curve write armed before its entity option was cleared is disarmed unwritten at the next off  [writes=[] diag={'armed': [], 'restores': 0, 'last_res
    FAIL a mode change that is not into off, or off to off, restores nothing and answers 0  [ret=(0, 0) writes=[]]
    FAIL a restore is persisted, so the next run does not restore it again; a forgotten entry's armed set is gone from the store  [saved=[] forgotten=[]]

M2 off-rule mode hook call deleted (coordinator.async_set_mode): rc=1, 4 failing
    FAIL MODE_OFF after a write writes one 0 (the off rule)  [[2]]
    FAIL and while off the arm writes nothing, nor does a second off  [[2]]
    FAIL a write left armed by a crash is restored by the next run's first off  [[2]]
    FAIL a restore is persisted, so the next run does not restore it again; a forgotten entry's armed set is gone from the store  [saved=[2] forgotten=[2]]

M3 unload restore deleted (__init__.async_unload_entry): rc=1, 1 failing
    FAIL unload after a write writes one 0, through async_unload_entry (the off rule)  [ok=True writes=[-3]]

M4 W1 hold predicate off (heat_curve._decide): rc=1, 2 failing
    FAIL a reading already at the target is not written (W1)  [[3]]
    FAIL a reading exactly half a step from the target holds: 2.25 against 2 at step 0.5 is not written (W1)  [[2]]

M5 persisted armed set never loaded (off_restore._armed_record): rc=1, 3 failing
    FAIL a write left armed by a crash is restored by the next run's first off  [[2]]
    FAIL a stand-in second consumer registers without editing the hook: its baseline, captured before its first write, survives a restart and is what the restore wr
    FAIL the persisted armed set is read once per entry, not at every arm  [[]]

M6 a failed restore write disarms anyway (off_restore.async_restore): rc=1, 2 failing
    FAIL a restore whose write raises sends nothing, stays armed and latches a warning naming the entity  [armed=True after=([1], {'armed': [], 'restores': 1, 'last
    FAIL and the next off retries it: one write of the neutral 0, disarmed and counted  [sent=0 writes=[] diag={'armed': [], 'restores': 1, 'last_restore': 'unload'

M7 store save swallow removed (off_restore._save): rc=1, 0 failing

M8 W2 grace bound moved (heat_curve._decide): rc=1, 1 failing
    FAIL at exactly 90 s the grace is over: a miss then is written once more (W2's bound)  [[2]]

M9 the arm's sent answer dropped (heat_curve.write_displace): rc=1, 1 failing
    FAIL the entity arm answers True only for a write sent: held, capped and unreadable are False  [(False, False, False, False)]

restored clean: rc=0, 0 failing
```

M7 prints no FAIL line: the block stops at the dead-store check on the uncaught `RuntimeError: store gone`, which is rc=1 too. M1–M5 re-take the previous round's proof at this head; M6–M9 pin lines this round's checks added.

## Null control

The unmutated head runs the block at rc=0 with 0 failing (BASELINE above), and so does the restored copy. The entity option empty, the same publish sends no `set_value`, and the `/set` topic carries `5` as before (check "the entity option empty: no set_value, and the /set topic still carries the integer (W7)"). Each mutant pass under Figures starts with mutant_run's NULL mutant (no edit) and reports it SURVIVED; a command that failed unedited would have reported `KILLED NULL` and stopped at rc 3.

## Figures

- `PYTHONPATH=tests/hastub python3 tests/features.py`: ALL 4970 FEATURE CHECKS PASSED at `fb9b2313e` (392 s); ALL 4961 at `90d3265e8`. The section block: ALL 48 FEATURES BLOCK PASSED at both.
- `PYTHONPATH=tests/hastub python3 tests/config_flow_steps.py`: ALL 548 checks PASSED. `tests/golden.py`: NO STALE FIXTURE, 56 committed fixtures. `python3 tests/env_drift.py --all 53273de4d449a990bc29734565f63babada9ff7f`: NO UNCLAIMED DRIFT, NO STALE FIXTURE, CLAIMED config_flow (8 leaves); at `e330a768` the same command printed `1 UNCLAIMED DRIFT(S)` and `1 COMMITTED FIXTURE(S) ARE STALE` (the null control). `--claims-only`: claims hygiene ok. `tests/closure.py selftest`: ALL 118 PASSED. `tests/structure.py`: STRUCTURE RATCHET PASSED.
- `PYTHONPATH=tests/hastub python3 tests/entities.py`: 3 of 2655 failed on this host: "the coverage job reuses only an entry main's push run saved", "the release ZIP holds the integration folder at its root" and "the Pages workflow deploys on a release tag". The same command at the merge base `53273de4d` on this host fails the same 3 of 2655 (the null control), and CI's `tests / fast (3.14)` ran `tests/entities.py` green at `e330a768`. So the three are this host's workflow-step probes, not the diff's.
- Scope: `python3 tests/closure.py select --diff 53273de4d449a990bc29734565f63babada9ff7f --workdir <dir>` prints `MODE: SCOPED -- 30 script(s) run, 3 scoped out`; over this round's own commits (`--diff e330a7681c5b5e4ac416e0b8ed4270a857e89ab2`) `MODE: SCOPED -- 5 script(s) run`, namely config_flow_steps, entities, env_drift, features and golden, each run above, plus run.sh's `run_always` lines (`env_drift.py --claims-only`, `closure.py selftest`). `tests/stress.py` is CI's.
- Coverage: `python3 -m coverage run --include='*/off_restore.py' tests/features.py` then `python3 -m coverage report -m` (coverage 7.17.2): off_restore.py 101 statements, 0 missed, 100 %. CI's coverage-ratchet read 90.10 % at `e330a768`, with lines 115, 116, 129, 160, 161, 164, 165, 167, 199 and 200 missed (the null control).
- Diff mutants, the owner's 2026-11-07 ruling: `MUTANT_CMD='env PYTHONPATH=tests/hastub python3 tools/audit/seat/features_block.py --prelude "import asyncio as _asyncio" --prelude "import logging as _logging" --prelude "src = open(__file__).read(); i = src.index(\"class _LogCapture(\"); exec(src[i:src.index(\"async def _drive_outage_polls\", i)])" "R.section(\"R10-GENERIC-HEAT-CURVE" "R.section(\"R5-D12-01"'`. The preludes are the three names earlier blocks define; `_LogCapture` is executed from features.py's own text, never copied. `python3 -I tools/audit/seat/mutant_run.py --diff 53273de4d449a990bc29734565f63babada9ff7f...HEAD --cmd "$MUTANT_CMD" --report-only` over 146 mutants: 67 SURVIVED at `e330a768`, 24 at this head; wall 2 m 51 s at `e330a768`. The 24 at this head: 11 on lines another driver owns, killed by it (#193 S3 block: heat_curve.py 163, 169, 180; `tests/config_flow_steps.py`: config_flow.py 2191, 2214, 2253, 3699; `tests/typing_ruler.py`: 2193, 2216; `tests/golden.py --only config_flow`: const.py 1497, 1498; `tests/finite_boundary.py`: store.py 479). The other 13 are equivalent under mutant_run's operators, which CI's table does not ratchet (heat_curve.py 76, 78, 148, 149, 273, 276; config_flow.py 1773 CONST_SWAP on a box field's unread step, #1679; off_restore.py 43; plus the mutant_run CONST_SWAP/CALL_DEL forms of lines whose ratcheted sites are killed). The four targeted passes ran in 1197 s wall.
- `MUTANT_CMD=<the command above> bash tools/pr/prepr.sh <body>` at `fb9b2313e`, step 6d' (`mutant_run.py --diff` capped at its default 40 mutants): 18 SURVIVED, each one among the 24 the previous line answers (config_flow.py 1773, 2191, 2192, 2193, 2214, 2215, 2216, 2253, 3699 twice; const.py 1498; heat_curve.py 76, 78, 148, 149, 163, 169, 180). prepr ran in 971 s with rc=0.
- CI's ratcheted sites: the 71 mutants (69 keys) `tests / mutation` listed as ADDED UNPINNED at `e330a768`, regenerated by `mutation_table._generate` at this head (production lines unchanged) and driven by `mutant_run.py --spec`: 61 KILLED by the two features.py blocks (94 s wall), 6 by `tests/config_flow_steps.py` (122 s), 2 by `tests/typing_ruler.py` (56 s), 2 SURVIVED and triaged equivalent. Survivor count: 0 untriaged. Each site's disposition is under `## Unpinned sites`.
- `python3 tests/mutation_table.py --pin-killed --base 53273de4d449a990bc29734565f63babada9ff7f` locally: unmeasured. Run 1 was INCONCLUSIVE on env_drift's red baseline (since repaired). Run 2 was INCONCLUSIVE on entities.py's three host probes. Run 3, without entities.py and stress.py, was stopped at this environment's 2 h background limit before writing a pin. The pins are `mutation-autofix`'s after the push (`ci-autofix.md`).
- Toolchain: `python3 -c "import numpy,scipy;print(numpy.__version__,scipy.__version__)"` prints 2.5.4 1.18.1, equal to `tests/requirements-ci.txt`.

## Architecture score

`python3 tools/audit/archscore/score.py --diff origin/main` at this head: `Architecture score: dS +0.0000 NULL`. No metric rises, so no per-metric line is owed; this round changes no production line. `off_restore` imports `homeassistant.core.HomeAssistant` for the `hass` it writes through and the store it persists to: it is a glue module.

## Red checks

Every concluded red at `e330a7681c5b5e4ac416e0b8ed4270a857e89ab2` and at the PR head `30e7024e81f409e60803ab25928ed6f7d717d527` (check-runs, filter=all, every page; the runs cancelled there are not concluded reds), and the branch's red history `pr-contract` records, by literal name:
- `tests / fast (3.14)`: class own, `tests/env_drift.py --all` STALE and UNCLAIMED `config_flow`. Answer: re-recorded and claimed (above). The cheaper detector exists and is the same script: `env_drift.py --all` in the scoped gate before handoff. It was not run on the last merge of main into the branch, which brought the fixture's drift into view; no cheaper detector is missing.
- `tests / coverage-ratchet`: class own, off_restore.py 90.10 % < 95 %. Answer: covered to 100 %. A cheaper detector exists at a cost: `coverage run` over the module's driver (one features.py run, ~7 min). prepr.sh does not run it; I'm recording that rather than building it here.
- `tests / mutation`: class own, 71 ADDED UNPINNED. Answer: every site killed by a CI driver or triaged (`## Unpinned sites`). The cheaper detector is prepr step 6d plus `mutant_run.py --diff` with `MUTANT_CMD` (seconds per mutant over the block). It was not run last round; it ran this round. Red by construction until `mutation-autofix` pins the killed sites after the push.
- `tests / mutation-autofix`: class own, `skip-measure-failed`: the pin shards measured nothing because `tests / fast` was red on env_drift's baseline. Answer: that red is repaired above; with every site killable, the job's pins follow. No cheaper detector: it is the repair job.
- `gate`: class follows from the four above. Answer: those four.
- `governance / delivery-status`: red at the PR head `30e7024e8` only, a check outside the required set (the owner's 2026-11-07 ruling: delivery-status never counts). Named here, not answered.
- `pr-contract / pr-contract`: class own, `## Red checks` did not name the four `tests / *` reds. Answer: this section names each. Its cheaper detector, `prepr.sh --body-check`, ran clean at this head.
`UNDER-SCOPED` and `INHERITED CLAIMS`: none predicted.

## Forward-carry

- The hook's interface (this body's "restore hook" list) changes how R10-ARBITER-OFF-RESTORE and R10-GENERIC-HEAT-CURVE-PERSISTENT must work: register a consumer and arm before the first write, never a second owner of the unload, MODE_OFF or remove path. Lands in those two groups' entries in `dev/programme/rosters/wave-r10-groups.json`. Carry: R10-ARBITER-OFF-RESTORE. Carry: R10-GENERIC-HEAT-CURVE-PERSISTENT.
- For the persistent kind: the baseline is persisted per entry by `async_arm`, which answers the note's O3 (a crash's displaced value is never re-captured) and O4 (one owner); O1 does not arise, because the baseline is not in the options. O2 (budget and dwell across reloads) and O5's endurance numbers (12/day, 7000/yr) stay that group's, in `dev/programme/rosters/wave-r10-groups.json`. Carry: R10-GENERIC-HEAT-CURVE-PERSISTENT.
- ghc-d02, `decision: owner`: whether the MQTT ECL110 arms also publish displace 0 on MODE_OFF and unload. Not built: W7 keeps MQTT byte-identical. Lands in `dev/programme/rosters/wave-r10-groups.json`. Carry: R10-GENERIC-HEAT-CURVE-PERSISTENT.

## Roster carries

- Carry 1 (the contributor trailer): the body ends with `Co-authored-by: Bankaifan <476059+Bankaifan@users.noreply.github.com>`, and so does the first commit of the branch (`ad975093f`).
- Carry 2 (the band default from the web-research probe): `const.py` `DEFAULT_HEAT_CURVE_OFFSET_BAND_K = 3.0` and `HEAT_CURVE_OFFSET_BAND_RANGE_K = (0.5, 5.0)`, the comment citing handoff-body/r10-ghc-research 52f5a442, BODY.md, its "Recommended defaults" row O5a; the options field is 0.5–5 K, a box field whose step is `"any"` (#1679), so no increment is enforced; `docs/ecl110.md` states the 5 K ceiling as *[documented, a third-party app's docs]* and the 3 K default as an *[estimate]*. The write-endurance limits bind the persistent kind only and are not built here (Forward-carry).
- Carry 3 (the owner's "Arbiter too"): the MODE_OFF and unload restore is one hook, `off_restore`, with the interface named above; the arbiter group registers a consumer and arms it, and the two restores share `async_mode_change`, `async_restore` and `async_forget`. A stand-in second consumer registers with no edit to the hook (the check named above). The arbiter's behaviour is untouched here, as the brief's SCOPE requires.

## Design carries

ghc-03 and ghc-04 stay as the note disposed of them (a D6 and a D5 round's); untouched here. The design carries, each disposed of here: ghc-d01 (off rule: MODE_OFF and unload write 0, counted, bypassing W3/W4; tests named above), ghc-d03 (kind kept in `_WIRING`; factory-reset check), ghc-d04 (stopping: written anyway, failure latched and kept armed; docs/ecl110.md), ghc-d05 (roster `after` followed), ghc-d06 (no probe file landed), ghc-d07 (W1/W2/W3 kept in one owner, `heat_curve._decide`; the valve's epsilon block and the arbiter's record are not cloned), ghc-01 (integer sent: checks read `5` and `-2` back), ghc-02 (re-pointed at `EntryConfig`), ghc-r01 (docs say the peak guard and a mode change publish without the staleness check), ghc-r02 (`log_held`), ghc-r03 (refused on every page and the pre-fill save; checks on the heat_curve and building pages), ghc-r04 (docs/ecl110.md), ghc-r05 (`HELD_GRACE_S`, reasoned in code), ghc-r06 (both modules in 22 recorded closures), ghc-r07 (commit named), ghc-r08 (an entity with no state at save is not judged; the arm re-checks the range at every write). Band default cited to its source: const.py `DEFAULT_HEAT_CURVE_OFFSET_BAND_K` names handoff-body/r10-ghc-research 52f5a442, BODY.md, "Recommended defaults" row O5a; docs/ecl110.md flags the [documented]/[estimate] tags.

## Friction

- frugal-routing: cost: the inline-search budget counted plain sed/cat/tail reads of a file already located, and a Monitor's tail, so file reads went through extra subagents. Carry: dismissed: a session plugin's guard, not this repository's policy
- handoff-wip: stale: `refs/heads/handoff-wip/r10-generic-heat-curve` held a previous seat's `BLOCKED` commit (`d70150252`, 2026-11-07 19:02Z) on head `98ce151cf`, so this seat's fast-forward step push was refused. Nothing was forced; the ref is deleted after the body push, as the brief directs. Carry: dismissed: one seat's leftover, already resolved by the PR existing

## Unpinned sites

The 69 keys (71 mutants) `tests / mutation` listed as ADDED UNPINNED at `e330a768`, each with its disposition. Every site is under `custom_components/`, which the `mutation-autofix` lane mutates.
- custom_components/heatpump_optimizer/config_flow.py:2191 BOOLOP: pinned by mutation-autofix; killed here by tests/config_flow_steps.py
- custom_components/heatpump_optimizer/config_flow.py:2191 GUARD_OFF: pinned by mutation-autofix; killed here by tests/config_flow_steps.py
- custom_components/heatpump_optimizer/config_flow.py:2193 RETURN_DEL: pinned by mutation-autofix; killed here by tests/typing_ruler.py
- custom_components/heatpump_optimizer/config_flow.py:2214 BOOLOP: pinned by mutation-autofix; killed here by tests/config_flow_steps.py
- custom_components/heatpump_optimizer/config_flow.py:2214 GUARD_OFF: pinned by mutation-autofix; killed here by tests/config_flow_steps.py
- custom_components/heatpump_optimizer/config_flow.py:2216 RETURN_DEL: pinned by mutation-autofix; killed here by tests/typing_ruler.py
- custom_components/heatpump_optimizer/config_flow.py:2253 RETURN_DEL: pinned by mutation-autofix; killed here by tests/config_flow_steps.py
- custom_components/heatpump_optimizer/config_flow.py:3699 RETURN_DEL: pinned by mutation-autofix; killed here by tests/config_flow_steps.py
- custom_components/heatpump_optimizer/heat_curve.py:66 CONST: pinned by mutation-autofix; killed here by the R10-GENERIC-HEAT-CURVE and #193 S3 blocks of tests/features.py
- custom_components/heatpump_optimizer/heat_curve.py:67 CONST: pinned by mutation-autofix; killed here by the R10-GENERIC-HEAT-CURVE and #193 S3 blocks of tests/features.py
- custom_components/heatpump_optimizer/heat_curve.py:88 GUARD_OFF: pinned by mutation-autofix; killed here by the R10-GENERIC-HEAT-CURVE and #193 S3 blocks of tests/features.py
- custom_components/heatpump_optimizer/heat_curve.py:90 RETURN_DEL: pinned by mutation-autofix; killed here by the R10-GENERIC-HEAT-CURVE and #193 S3 blocks of tests/features.py
- custom_components/heatpump_optimizer/heat_curve.py:95 GUARD_OFF: pinned by mutation-autofix; killed here by the R10-GENERIC-HEAT-CURVE and #193 S3 blocks of tests/features.py
- custom_components/heatpump_optimizer/heat_curve.py:97 RETURN_DEL: pinned by mutation-autofix; killed here by the R10-GENERIC-HEAT-CURVE and #193 S3 blocks of tests/features.py
- custom_components/heatpump_optimizer/heat_curve.py:148 BOOLOP: pinned by mutation-autofix; killed here by the R10-GENERIC-HEAT-CURVE and #193 S3 blocks of tests/features.py
- custom_components/heatpump_optimizer/heat_curve.py:148 GUARD_OFF: triaged equivalent, tests/mutation_ledger/survivor_triage/heat_curve.py/publish_ecl110_topics.GUARD_OFF.8b6644d6.json
- custom_components/heatpump_optimizer/heat_curve.py:152 GUARD_OFF: pinned by mutation-autofix; killed here by the R10-GENERIC-HEAT-CURVE and #193 S3 blocks of tests/features.py
- custom_components/heatpump_optimizer/heat_curve.py:169 GUARD_OFF: pinned by mutation-autofix; killed here by the R10-GENERIC-HEAT-CURVE and #193 S3 blocks of tests/features.py
- custom_components/heatpump_optimizer/heat_curve.py:209 BOOLOP: pinned by mutation-autofix; killed here by the R10-GENERIC-HEAT-CURVE and #193 S3 blocks of tests/features.py
- custom_components/heatpump_optimizer/heat_curve.py:209 GUARD_OFF: pinned by mutation-autofix; killed here by the R10-GENERIC-HEAT-CURVE and #193 S3 blocks of tests/features.py
- custom_components/heatpump_optimizer/heat_curve.py:219 CMP_BOUND*2: pinned by mutation-autofix; killed here by the R10-GENERIC-HEAT-CURVE and #193 S3 blocks of tests/features.py
- custom_components/heatpump_optimizer/heat_curve.py:219 RETURN_DEL: pinned by mutation-autofix; killed here by the R10-GENERIC-HEAT-CURVE and #193 S3 blocks of tests/features.py
- custom_components/heatpump_optimizer/heat_curve.py:229 GUARD_OFF: pinned by mutation-autofix; killed here by the R10-GENERIC-HEAT-CURVE and #193 S3 blocks of tests/features.py
- custom_components/heatpump_optimizer/heat_curve.py:232 GUARD_OFF: pinned by mutation-autofix; killed here by the R10-GENERIC-HEAT-CURVE and #193 S3 blocks of tests/features.py
- custom_components/heatpump_optimizer/heat_curve.py:235 GUARD_OFF: pinned by mutation-autofix; killed here by the R10-GENERIC-HEAT-CURVE and #193 S3 blocks of tests/features.py
- custom_components/heatpump_optimizer/heat_curve.py:237 CLAMP_DROP*2: pinned by mutation-autofix; killed here by the R10-GENERIC-HEAT-CURVE and #193 S3 blocks of tests/features.py
- custom_components/heatpump_optimizer/heat_curve.py:239 GUARD_OFF: pinned by mutation-autofix; killed here by the R10-GENERIC-HEAT-CURVE and #193 S3 blocks of tests/features.py
- custom_components/heatpump_optimizer/heat_curve.py:240 CLAMP_DROP: pinned by mutation-autofix; killed here by the R10-GENERIC-HEAT-CURVE and #193 S3 blocks of tests/features.py
- custom_components/heatpump_optimizer/heat_curve.py:241 GUARD_OFF: pinned by mutation-autofix; killed here by the R10-GENERIC-HEAT-CURVE and #193 S3 blocks of tests/features.py
- custom_components/heatpump_optimizer/heat_curve.py:242 CLAMP_DROP: pinned by mutation-autofix; killed here by the R10-GENERIC-HEAT-CURVE and #193 S3 blocks of tests/features.py
- custom_components/heatpump_optimizer/heat_curve.py:243 RETURN_DEL: pinned by mutation-autofix; killed here by the R10-GENERIC-HEAT-CURVE and #193 S3 blocks of tests/features.py
- custom_components/heatpump_optimizer/heat_curve.py:248 BOOLOP: pinned by mutation-autofix; killed here by the R10-GENERIC-HEAT-CURVE and #193 S3 blocks of tests/features.py
- custom_components/heatpump_optimizer/heat_curve.py:248 CMP_BOUND: pinned by mutation-autofix; killed here by the R10-GENERIC-HEAT-CURVE and #193 S3 blocks of tests/features.py
- custom_components/heatpump_optimizer/heat_curve.py:248 GUARD_OFF: pinned by mutation-autofix; killed here by the R10-GENERIC-HEAT-CURVE and #193 S3 blocks of tests/features.py
- custom_components/heatpump_optimizer/heat_curve.py:250 RETURN_DEL: pinned by mutation-autofix; killed here by the R10-GENERIC-HEAT-CURVE and #193 S3 blocks of tests/features.py
- custom_components/heatpump_optimizer/heat_curve.py:251 CMP_BOUND: pinned by mutation-autofix; killed here by the R10-GENERIC-HEAT-CURVE and #193 S3 blocks of tests/features.py
- custom_components/heatpump_optimizer/heat_curve.py:251 GUARD_OFF: pinned by mutation-autofix; killed here by the R10-GENERIC-HEAT-CURVE and #193 S3 blocks of tests/features.py
- custom_components/heatpump_optimizer/heat_curve.py:253 RETURN_DEL: pinned by mutation-autofix; killed here by the R10-GENERIC-HEAT-CURVE and #193 S3 blocks of tests/features.py
- custom_components/heatpump_optimizer/heat_curve.py:254 CMP_BOUND: pinned by mutation-autofix; killed here by the R10-GENERIC-HEAT-CURVE and #193 S3 blocks of tests/features.py
- custom_components/heatpump_optimizer/heat_curve.py:254 GUARD_OFF: pinned by mutation-autofix; killed here by the R10-GENERIC-HEAT-CURVE and #193 S3 blocks of tests/features.py
- custom_components/heatpump_optimizer/heat_curve.py:257 CMP_BOUND: pinned by mutation-autofix; killed here by the R10-GENERIC-HEAT-CURVE and #193 S3 blocks of tests/features.py
- custom_components/heatpump_optimizer/heat_curve.py:257 RETURN_DEL: pinned by mutation-autofix; killed here by the R10-GENERIC-HEAT-CURVE and #193 S3 blocks of tests/features.py
- custom_components/heatpump_optimizer/heat_curve.py:262 CLAMP_DROP: pinned by mutation-autofix; killed here by the R10-GENERIC-HEAT-CURVE and #193 S3 blocks of tests/features.py
- custom_components/heatpump_optimizer/heat_curve.py:262 RETURN_DEL: pinned by mutation-autofix; killed here by the R10-GENERIC-HEAT-CURVE and #193 S3 blocks of tests/features.py
- custom_components/heatpump_optimizer/heat_curve.py:277 GUARD_OFF: pinned by mutation-autofix; killed here by the R10-GENERIC-HEAT-CURVE and #193 S3 blocks of tests/features.py
- custom_components/heatpump_optimizer/heat_curve.py:279 GUARD_OFF: pinned by mutation-autofix; killed here by the R10-GENERIC-HEAT-CURVE and #193 S3 blocks of tests/features.py
- custom_components/heatpump_optimizer/heat_curve.py:281 RETURN_DEL: pinned by mutation-autofix; killed here by the R10-GENERIC-HEAT-CURVE and #193 S3 blocks of tests/features.py
- custom_components/heatpump_optimizer/heat_curve.py:294 BOOLOP: pinned by mutation-autofix; killed here by the R10-GENERIC-HEAT-CURVE and #193 S3 blocks of tests/features.py
- custom_components/heatpump_optimizer/heat_curve.py:294 CMP_BOUND: pinned by mutation-autofix; killed here by the R10-GENERIC-HEAT-CURVE and #193 S3 blocks of tests/features.py
- custom_components/heatpump_optimizer/heat_curve.py:297 CMP_BOUND: pinned by mutation-autofix; killed here by the R10-GENERIC-HEAT-CURVE and #193 S3 blocks of tests/features.py
- custom_components/heatpump_optimizer/heat_curve.py:300 GUARD_OFF: pinned by mutation-autofix; killed here by the R10-GENERIC-HEAT-CURVE and #193 S3 blocks of tests/features.py
- custom_components/heatpump_optimizer/heat_curve.py:306 RETURN_DEL: pinned by mutation-autofix; killed here by the R10-GENERIC-HEAT-CURVE and #193 S3 blocks of tests/features.py
- custom_components/heatpump_optimizer/heat_curve.py:310 RETURN_DEL: pinned by mutation-autofix; killed here by the R10-GENERIC-HEAT-CURVE and #193 S3 blocks of tests/features.py
- custom_components/heatpump_optimizer/inputs.py:635 GUARD_OFF: pinned by mutation-autofix; killed here by the R10-GENERIC-HEAT-CURVE and #193 S3 blocks of tests/features.py
- custom_components/heatpump_optimizer/off_restore.py:43 GUARD_OFF: triaged equivalent, tests/mutation_ledger/survivor_triage/off_restore.py/@module.GUARD_OFF.e1433e05.json
- custom_components/heatpump_optimizer/off_restore.py:48 CONST: pinned by mutation-autofix; killed here by the R10-GENERIC-HEAT-CURVE and #193 S3 blocks of tests/features.py
- custom_components/heatpump_optimizer/off_restore.py:98 GUARD_OFF: pinned by mutation-autofix; killed here by the R10-GENERIC-HEAT-CURVE and #193 S3 blocks of tests/features.py
- custom_components/heatpump_optimizer/off_restore.py:100 GUARD_OFF: pinned by mutation-autofix; killed here by the R10-GENERIC-HEAT-CURVE and #193 S3 blocks of tests/features.py
- custom_components/heatpump_optimizer/off_restore.py:104 GUARD_OFF: pinned by mutation-autofix; killed here by the R10-GENERIC-HEAT-CURVE and #193 S3 blocks of tests/features.py
- custom_components/heatpump_optimizer/off_restore.py:109 RETURN_DEL: pinned by mutation-autofix; killed here by the R10-GENERIC-HEAT-CURVE and #193 S3 blocks of tests/features.py
- custom_components/heatpump_optimizer/off_restore.py:128 GUARD_OFF: pinned by mutation-autofix; killed here by the R10-GENERIC-HEAT-CURVE and #193 S3 blocks of tests/features.py
- custom_components/heatpump_optimizer/off_restore.py:131 GUARD_OFF: pinned by mutation-autofix; killed here by the R10-GENERIC-HEAT-CURVE and #193 S3 blocks of tests/features.py
- custom_components/heatpump_optimizer/off_restore.py:134 GUARD_OFF: pinned by mutation-autofix; killed here by the R10-GENERIC-HEAT-CURVE and #193 S3 blocks of tests/features.py
- custom_components/heatpump_optimizer/off_restore.py:142 RETURN_DEL: pinned by mutation-autofix; killed here by the R10-GENERIC-HEAT-CURVE and #193 S3 blocks of tests/features.py
- custom_components/heatpump_optimizer/off_restore.py:159 GUARD_OFF: pinned by mutation-autofix; killed here by the R10-GENERIC-HEAT-CURVE and #193 S3 blocks of tests/features.py
- custom_components/heatpump_optimizer/off_restore.py:175 RETURN_DEL: pinned by mutation-autofix; killed here by the R10-GENERIC-HEAT-CURVE and #193 S3 blocks of tests/features.py
- custom_components/heatpump_optimizer/off_restore.py:186 GUARD_OFF: pinned by mutation-autofix; killed here by the R10-GENERIC-HEAT-CURVE and #193 S3 blocks of tests/features.py
- custom_components/heatpump_optimizer/off_restore.py:188 RETURN_DEL: pinned by mutation-autofix; killed here by the R10-GENERIC-HEAT-CURVE and #193 S3 blocks of tests/features.py
- custom_components/heatpump_optimizer/off_restore.py:206 GUARD_OFF: pinned by mutation-autofix; killed here by the R10-GENERIC-HEAT-CURVE and #193 S3 blocks of tests/features.py

Co-authored-by: Bankaifan <476059+Bankaifan@users.noreply.github.com>
