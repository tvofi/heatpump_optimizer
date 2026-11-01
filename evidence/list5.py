EC, CO = "entry_config.py", "coordinator.py"
muts += [
 ("L358-GUARD_OFF", [(EC, "    if isinstance(raw, list) and len(raw) == 2 and all(isinstance(side, dict) for side in raw):", "    if False:")]),
 ("L360-RETURN_DEL", [(EC, "        return raw[0], raw[1]\n    return None\n", "        return raw[0], raw[1]\n    pass\n")]),
 ("L369-GUARD_OFF", [(EC, "    if settings is None or pinned is None:", "    if False:")]),
 ("L373-RETURN_DEL", [(EC, "    return with_settings(wiring, (settings[0], settings[1]))", "    pass")]),
 ("L9955-GUARD_OFF", [(CO, "        if value is not None and self._learning_frozen(CONF_DHW_TEMP_ENTITY, room_air=False) is None:", "        if False:")]),
 ("L9957-RETURN_DEL", [(CO, "            return value\n        return None\n\n    def _file_dhw_lead_predictions", "            return value\n        pass\n\n    def _file_dhw_lead_predictions")]),
]
