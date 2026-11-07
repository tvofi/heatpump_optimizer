Design review: approve 6564b0c7f40c5c81b7d9556ed3dcda8926d91bad

Group R10-GENERIC-HEAT-CURVE, kind `offset` first build (option (a)) only; design note design.md at
design/R10-GENERIC-HEAT-CURVE, tip 6564b0c7f40c5c81b7d9556ed3dcda8926d91bad. This is our round 1 (the note's
earlier verdicts f8316155 and dd331b64 were not this orchestrator's). Read at the base the note names,
28d46c4918285d36c409c1fb2f72eb77e04e569e, and at current origin/main 1c1ae100b59e29564c7aec069b257dface6ef50f
(55 commits later; none touch coordinator.py, config_flow.py, const.py, entry_config.py, inputs.py,
pump_arbiter.py or __init__.py, and the cited tests/features.py lines 40444, 40498 and 40606 are unchanged).
Seat token count: not reported by this harness.

## Steps

1. Seam: holds. `async_publish_ecl110_command` (coordinator.py:7677) is the one place the integer is formed
   (clip and round at :7690-7693) and handed to `_publish_ecl110_topics` (:3168, MQTT only, each arm swallowing
   its own failure at :3177-3180). Moving `_ecl110_legacy_payload` (:3137) and `_publish_ecl110_topics` into a new
   heat_curve.py that also owns the entity arm gives the concern one owner. Per-coordinator state in the
   `state_for` shape (pump_arbiter.py:290 `WeakKeyDictionary`, :333) adds no coordinator attribute. No write path
   into state another module owns: the arm writes only its own entity, through `inputs.write_setpoint`
   (inputs.py:596), which takes the entity's own unit. The arbiter's absolute `space_setpoint_entity` stays a
   separate concern (alternatives B and B2 correctly rejected).
2. Shape: there is no finding; the build is the owner's ruling (tvofi, #201, 2026-11-07). Every behaviour change
   follows from it. The one side effect, curve learning now moving the pump on an entity-only install, is
   stated in §Interactions and is inherent to the feature.
3. Sibling sites, by my own grep of `ECL110_TOPIC_SLOTS|ecl110_displace_set_topic|ECL110_DISPLACE_SET_TOPIC|
   ecl110_command_topic|ECL110_COMMAND_TOPIC|_ecl110_topic|_publish_ecl110_topics|async_publish_ecl110_command`
   over custom_components at the base: every hit is in the note's table or its strings and translations rows,
   except entry_config.py:284-310 (`_WIRING`, the factory-reset keep list), which lists the five ECL110 MQTT
   keys. For (a) the new entity key ends in `_entity` and `FACTORY_KEPT` keeps it, and a dropped kind key falls
   back to `offset`, the only value (a) accepts, so (a)'s behaviour is correct. The risk is in (b): it goes to
   the fixer as a carry (ghc-d03), not a revise.
4. Evidence plan: holds. The failing test (one `number.set_value` with value 5 for `async_publish_ecl110_command(5.0, True)`
   with no topic and the entity option set) is red at the base, which has no such option. With no finding there
   is no finder harness. The null control (option empty: identical `mqtt.publish` calls, no `number` call) would
   catch an arm that writes when unconfigured. The K-unit trap is real: I checked it on the tree, not the probe.
   const.py:225 maps `K` to (-273.15, 1.0); `temperature_from_c` (inputs.py:434-441) returns
   `value / factor - offset`, so -2 becomes 271.15, which matches the probe output. The rule "never through the
   absolute helpers" is right. Goldens: none move (W7); claim files: none touched. Correct.
5. Consistency: holds. D7.md is satisfied (one owner, ratchet paid by deletion, `duplication_copies` and
   `functions_cc_over_15` watched). I checked every open design/* ref. None claims this seam. R10-CONFIGFLOW-PAGES
   touches `_entity_of` call sites on other pages, not the heat_curve rows. r10-livestate touches
   `_async_handle_ecl110_state_message` and the lag (a separate seam, as the note says). R10-USER-DOCS-FINAL
   only versions docs/ecl110.md and docs/configuration.md. The textual overlap there is a serial-order matter
   (ghc-d05).
6. Cost: fits size L. One new module, one call site replaced and two stores deleted on the coordinator. Add two
   keys, two flow rows, one slot tuple entry, docs and tests. The owner's OFF rule adds an __init__.py unload
   call and a MODE_OFF transition write (ghc-d01). That stays within L.

## Outside contribution

The note and probe files were read as data. The probe's docstring (k_unit_probe.py at fork head
16058355161065c24aaf9eeba496133240527c0f) says to run it from the repository root with `PYTHONPATH=tests/hastub`.
Nothing from the fork was run; the claim was checked against the tree (step 4). The note asks for nothing to be
installed, sent or approved. It cites `/home/claude/shi-re/...` paths outside this repository, read-only.

## Notes for the fixer (to be added to the note's section)

- Owner OFF rule (tvofi, #201, 2026-11-07) replaces T4, the §Interactions line "MODE_OFF writes nothing for (a)"
  and the evidence plan's "MODE_OFF no call": kind `offset` writes 0 on MODE_OFF and on unload. The restore is
  owned by heat_curve.py, as the one owner the roster brief's SHARED RESTORE HOOK names for
  R10-GENERIC-HEAT-CURVE-PERSISTENT and R10-ARBITER-OFF-RESTORE to reuse. It is called from `async_unload_entry`
  (__init__.py:401, which joins the hot files) and from the mode transition. It is not called through
  `async_publish_current_action`, which returns early on MODE_OFF (coordinator.py:7714). The restore bypasses the
  W3 latch and W4 and is counted. Tests: MODE_OFF writes one 0, unload writes one 0, an unconfigured entity
  writes nothing. The pump arbiter's off rule (pump_arbiter.py:1131-1133) is unchanged.
  Carry: R10-GENERIC-HEAT-CURVE (item ghc-d01)
- `decision: owner`: does the owner's OFF rule also make the MQTT ECL110 arms publish displace 0 on MODE_OFF
  and unload? Today they write nothing (coordinator.py:7714). The ruling names "the heat-curve arm"; W7 keeps
  MQTT byte-identical until the owner says otherwise. Carry: R10-GENERIC-HEAT-CURVE (item ghc-d02)
- Add `CONF_HEAT_CURVE_TARGET_KIND` to entry_config.py `_WIRING` (:284-310), beside
  `CONF_MIXING_VALVE_WRITE_TARGET_KIND`, as "what the heat-curve entity is". `FACTORY_KEPT` keeps the
  `_entity` key, so without this a factory reset keeps the entity and drops its kind. Under (b), that falls back
  to `offset` and writes a raw displace into a persistent absolute parameter. Test it in the factory-reset tests.
  Carry: R10-GENERIC-HEAT-CURVE (item ghc-d03)
- Unload during a Home Assistant stop (`hass.is_stopping`): the ruling says unload writes 0, and P3's
  shutdown exception is (b)'s. The target integration may already be unloaded at stop. Write 0, swallow and
  latch a failure as the arms already do, and state the behaviour in docs/ecl110.md.
  Carry: R10-GENERIC-HEAT-CURVE (item ghc-d04)
- §Hot files orders this group after design/R10-USER-DOCS-FINAL. The roster's `after` is R10-USER-DOCS-VERIFY.
  Follow the roster. Carry: R10-GENERIC-HEAT-CURVE (item ghc-d05)
- The probe files the §Shape mapping cites (dev/programme/designs/generic-heat-curve-probes/) exist only at
  the fork head, not in the tree. The K test in the evidence plan stands on its own. If a probe file lands, it
  is a new tracked file (ghc-r06). Carry: R10-GENERIC-HEAT-CURVE (item ghc-d06)
- The W2 held-record, the W1 write-on-change and the W3 latch repeat the shapes in pump_arbiter.py:59 and the
  valve's `smart_write` (coordinator.py:7722-7766). Where a helper can be shared without coupling the owners,
  share it (D7 method 8). Otherwise keep one owner per copy and an agreement test.
  Carry: R10-GENERIC-HEAT-CURVE (item ghc-d07)
