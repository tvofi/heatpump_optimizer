Fix review: merge 57eecef02966aeb17efaff0c2d72486cf47cb3e7

Round 2. PR #1806 head 57eecef02966aeb17efaff0c2d72486cf47cb3e7 (live at posting), code head ed1c0af5494145912480b713643b6e234a9c353f, which descends from round-1 head f95051f4 with no force-push.

Head shape: 191f17d5 merges ed1c0af5 into the round-1 PR head 0077ab5a; its tree 1d8e0c3e equals git merge-tree 787fe137 ed1c0af5. 57eecef0 then adds only the bot's 4 mutation-ledger killed_by files from 44a0ba7e (+24 lines, no code). No transport BODY.md or resume file is in the PR tree.

Round-1 items, all closed:
1. typing: pinned mypy 2.3.1 --strict + homeassistant-stubs 2026.9.3 on Python 3.14, run locally at ed1c0af5: no errors (sensor.py:2852 gone). CI typing at 57eecef0: success. _gap_probe_terms now returns a _GapTerms TypedDict with the five keys it always had.
2. Gap-advisor seam: SensorGapAdvisorSensor._gaps passes language=self.coordinator.hass.config.language.
3. Wiring pins: targeted mutants re-run at ed1c0af5 (CPython 3.13 venv, pinned requirements-ci, OPENBLAS_CORETYPE=Haswell). All killed:
   M1 coordinator describe_setup without language: entities rc 1 ("describe_setup on a Swedish hass labels the slots in Swedish")
   M2 config_flow describe_setup without language: config_flow_steps rc 1 ("the setup overview is written in the install's language (Swedish hass)")
   M3 _with_sensor_advisor without language: entities rc 1 ("_with_sensor_advisor ranks with Swedish labels on a Swedish hass")
   M5a / M5b catalog description / requirement untranslated: entities rc 1 ("describe_setup's layout catalog label, description and requirement are Swedish on a Swedish hass")
   M6 rank_sensor_advisor labels untranslated: entities rc 1 (the _with_sensor_advisor check)
   M8 (new) gap advisor without language: entities rc 1 ("the gap advisor sensor ranks with Swedish labels on a Swedish hass")
   M4 and M7 were killed in round 1, and those checks are unchanged.
4. Body: names the round-1 typing red with its cause, the cheaper detector (typing_ruler --mypy) and its cost; cites l4_setup_labels. Head line = ed1c0af5.
5. Nits: "stryps" fixed; CONF_INDOOR_TEMP_ENTITY import now sorted.

At ed1c0af5: features 3631, entities 2003, config_flow_steps 496 checks and structure.py all pass. The finder harness result (l4_setup_labels 41 -> 0, round 1) stands: round 2 touches no translated string except the one nit word.

CI at 57eecef0, all success: typing, fast (3.14), mutation (log: "MUTATION TABLE PASSED", not inconclusive; mutation-autofix skipped, so the pins recorded at 0077ab5a are not stale), coverage, coverage-ratchet, browser (overlap grid with the shortened now-temp label), closures (closures-autofix skipped), env-matrix, briefs, pr-contract, policy-docs, delivery-status, nightly-status, budget-raise-gate, hassfest, validate-hacs, CodeQL. claims-autofix skipped.
Real-HA ha_contract on the merged code (Mac, HA 2026.9.3): 61 contracts and 22 probes passed. The 2025.2.0 floor arm was not run.

Unchanged from round 1 and still clean: coordinator.py has only the two intended call changes; the golden fixtures move only on deterministic leaves and are claimed in both files (claims-for 6.7.12 = VERSION); version files untouched; no budget raise; card docs not owed before UI-3.

One note, not blocking: in config_flow_steps the Swedish probe ends with `del hass.config.language`. That works only while the stub's default language lives on the class. The check passes today.
