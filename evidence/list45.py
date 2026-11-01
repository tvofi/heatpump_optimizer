EC, CO, CF, SV, SN = "entry_config.py", "coordinator.py", "config_flow.py", "services.py", "snapshots.py"
muts += [
 # typing repair: undone_settings / _side_pair (a6592a23)
 ("T1-undone-guard-off", [(EC, "    if settings is None or pinned is None:\n        return None", "    if False:\n        return None")]),
 ("T2-undone-or-to-and", [(EC, "    if settings is None or pinned is None:", "    if settings is None and pinned is None:")]),
 ("T3-side_pair-narrowing-dropped", [(EC, "    if isinstance(raw, list) and len(raw) == 2 and all(isinstance(side, dict) for side in raw):", "    if True:")]),
 ("T3b-side_pair-guard-off", [(EC, "    if isinstance(raw, list) and len(raw) == 2 and all(isinstance(side, dict) for side in raw):", "    if False:")]),
 ("T4-side_pair-len-off", [(EC, "isinstance(raw, list) and len(raw) == 2 and all(", "isinstance(raw, list) and all(")]),
 ("T5-side_pair-dict-off", [(EC, " and len(raw) == 2 and all(isinstance(side, dict) for side in raw):", " and len(raw) == 2:")]),
 ("T5b-side_pair-list-off", [(EC, "    if isinstance(raw, list) and len(raw) == 2 and", "    if len(raw) == 2 and")]),
 ("T6-side_pair-return-dropped", [(EC, "        return raw[0], raw[1]\n", "        pass\n")]),
 # restore early return, humidity bounds, DHW probe
 ("C1-undo-return-dropped", [(CO, "            return await _async_undo_factory_reset(self, snap)", "            await _async_undo_factory_reset(self, snap)")]),
 ("C2-humidity-low-bound", [(CO, "return value if value is not None and 0.0 <= value <= 100.0 else None", "return value if value is not None and 0.0 < value <= 100.0 else None")]),
 ("C3-humidity-high-bound", [(CO, "return value if value is not None and 0.0 <= value <= 100.0 else None", "return value if value is not None and 0.0 <= value < 100.0 else None")]),
 ("C4-dhw-probe-guard-off", [(CO, "        if value is not None and self._learning_frozen(CONF_DHW_TEMP_ENTITY, room_air=False) is None:", "        if True:")]),
 ("C5-dhw-probe-frozen-dropped", [(CO, "        if value is not None and self._learning_frozen(CONF_DHW_TEMP_ENTITY, room_air=False) is None:", "        if value is not None:")]),
 # undo pins
 ("P1-pins-not-restored", [(EC, "    wiring = ({**unpinned[0], **pinned[0]}, {**unpinned[1], **pinned[1]})", "    wiring = (data, options)")]),
 ("P2-pins-not-recorded", [(EC, "    pinned = [{k: side[k] for k in FACTORY_PINNED if k in side} for side in (data, options)]", "    pinned = [{}, {}]")]),
 ("P3-pins-wrong-side", [(EC, "    wiring = ({**unpinned[0], **pinned[0]}, {**unpinned[1], **pinned[1]})", "    wiring = ({**unpinned[0], **pinned[1]}, {**unpinned[1], **pinned[0]})")]),
 ("P4-unpin-skipped", [(EC, "    unpinned = [{k: v for k, v in side.items() if k not in FACTORY_PINNED} for side in (data, options)]", "    unpinned = [dict(data), dict(options)]")]),
 # refused unload
 ("R1-refusal-ignored", [(CO, "    if not await hass.config_entries.async_unload(entry.entry_id):\n        return False", "    if not await hass.config_entries.async_unload(entry.entry_id):\n        pass")]),
 ("R2-reset-says-done-on-refusal", [(CO, "    done = await _async_rewrite_entry(coord, voided, settings)", "    done = await _async_rewrite_entry(coord, voided, settings) or True")]),
 ("R3-log-says-applied", [(CO, "\"applied; restore_learned_snapshot undoes it\" if done", "\"applied; restore_learned_snapshot undoes it\" if True")]),
 ("R4-options-step-says-done", [(CF, "\"factory_reset_done\" if done else", "\"factory_reset_done\" if True else")]),
 ("R5-service-raises-nothing", [(SV, "        if not await async_factory_reset(coord, data[\"scope\"]):", "        if await async_factory_reset(coord, data[\"scope\"]) and False:")]),
 ("R6-undo-spends-point-before-unload", [(CO, "    return await _async_rewrite_entry(coord, spent, undone_settings(", "    snap.pop(\"before_reset\")\n    undo.setdefault(\"x\", 1)\n    return await _async_rewrite_entry(coord, spent, undone_settings(")]),
 ("R7-heat-loss-void-before-unload", [(CO, "        await coord.async_reset_heat_loss_learners()\n        return voided_documents", "        return voided_documents"), (CO, "    ctx = _ctx_of(coord)\n    settings = None if scope", "    if scope != FACTORY_RESET_SCOPES[0]:\n        await coord.async_reset_heat_loss_learners()\n    ctx = _ctx_of(coord)\n    settings = None if scope")]),
 # carry-over: dispatch, undo order, ring
 ("L0-learners-dispatch-off", [(CO, "        if scope == FACTORY_RESET_SCOPES[0]:\n            return {}", "        if True:\n            return {}")]),
 ("S0-settings-dispatch-off", [(CO, "    settings = None if scope == FACTORY_RESET_SCOPES[1] else", "    settings = None if True else")]),
 ("U1-no-undo-point", [(CO, "                              {**undo_point(scope, entry.data, entry.options), \"stores\": documents})", "                              None)")]),
 ("U2-undo_target-never", [(SN, "        if self.snapshots and \"before_reset\" in self.snapshots[-1]:", "        if False:")]),
 ("U3-best_restore-takes-undo", [(SN, "if not snap.get(\"healthy\") or \"before_reset\" in snap:", "if not snap.get(\"healthy\"):")]),
 ("U4-undo-settings-not-restored", [(CO, "undone_settings(coord.entry.data, coord.entry.options, undo))", "None)")]),
 ("U5-void-before-undo-point", [(CO, "    for store in (*_restored_stores(coord), coord._snapshot_store):\n        await store.async_wait_for_read()\n", "    for store in (*_restored_stores(coord), coord._snapshot_store):\n        await store.async_wait_for_read()\n    if scope != FACTORY_RESET_SCOPES[0]:\n        await coord.async_reset_heat_loss_learners()\n")]),
 ("U6-no-flush-before-documents", [(CO, "    await _async_save_restored(coord)\n    return {name:", "    return {name:")]),
 ("U7-undo-ignores-age", [(SN, "        if self.snapshots and \"before_reset\" in self.snapshots[-1]:", "        if self.snapshots and any(\"before_reset\" in s for s in self.snapshots):")]),
 ("N1-confirm-ignored", [(CF, "        if not user_input.get(\"confirm\"):\n            return await self.async_step_advanced()\n", "")]),
 ("N2-not-loaded-guard-off", [(CF, "        if (coord := getattr(self._entry, \"runtime_data\", None)) is None:", "        if (coord := getattr(self._entry, \"runtime_data\", None)) is None and False:")]),
 ("S1-settings-keeps-price_weight", [(EC, "    kept = [{k: v for k, v in side.items() if k in FACTORY_KEPT} for side in wiring]", "    kept = [{k: v for k, v in side.items() if k in FACTORY_KEPT or k == 'price_weight'} for side in wiring]")]),
 ("S2-two_zone-pin-off", [(EC, "    pinned = dict(zip(FACTORY_PINNED, (const.TWO_ZONE_MODE_ON if two_zone else const.TWO_ZONE_MODE_OFF, dhw, wood)))", "    pinned = dict(zip(FACTORY_PINNED, (const.TWO_ZONE_MODE_OFF, dhw, wood)))")]),
 ("S4-main-fuse-not-kept", [(EC, "    const.CONF_MAIN_FUSE_A: \"the house's main fuse: a default arms the fuse guard \"\n    \"against a fuse the house does not have\",\n", "")]),
 ("SV1-entry_id-optional", [(SV, "        vol.Required(\"entry_id\"): cv.string,\n        vol.Required(\"scope\"): vol.In(FACTORY_RESET_SCOPES),", "        vol.Optional(\"entry_id\"): cv.string,\n        vol.Required(\"scope\"): vol.In(FACTORY_RESET_SCOPES),")]),
 ("SV2-scope-optional", [(SV, "        vol.Required(\"scope\"): vol.In(FACTORY_RESET_SCOPES),\n    }\n)\n\nSERVICE_SCHEMA_DIAGNOSE", "        vol.Optional(\"scope\", default=\"both\"): vol.In(FACTORY_RESET_SCOPES),\n    }\n)\n\nSERVICE_SCHEMA_DIAGNOSE")]),
]
EC, CO = "entry_config.py", "coordinator.py"
muts += [
 ("L358-GUARD_OFF", [(EC, "    if isinstance(raw, list) and len(raw) == 2 and all(isinstance(side, dict) for side in raw):", "    if False:")]),
 ("L360-RETURN_DEL", [(EC, "        return raw[0], raw[1]\n    return None\n", "        return raw[0], raw[1]\n    pass\n")]),
 ("L369-GUARD_OFF", [(EC, "    if settings is None or pinned is None:", "    if False:")]),
 ("L373-RETURN_DEL", [(EC, "    return with_settings(wiring, (settings[0], settings[1]))", "    pass")]),
 ("L9955-GUARD_OFF", [(CO, "        if value is not None and self._learning_frozen(CONF_DHW_TEMP_ENTITY, room_air=False) is None:", "        if False:")]),
 ("L9957-RETURN_DEL", [(CO, "            return value\n        return None\n\n    def _file_dhw_lead_predictions", "            return value\n        pass\n\n    def _file_dhw_lead_predictions")]),
]
