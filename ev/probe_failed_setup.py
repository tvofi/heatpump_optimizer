
# ---- reviewer probe: a setup that fails after fault_log.async_setup (HA runs only the entry's on_unload callbacks) ----
async def _rv_failed_setup(fail_first):
    hass, entry = _FlHass({"sensor.fd": _fl_state("OK", 0)}), _fl_entry(entry_id=f"rv_fail_{fail_first}")
    await _fl.async_setup(hass, entry, _FlConfig.from_mapping(_FL_TEXT))
    if fail_first:
        for cb in list(entry._on_unload):
            cb()
        entry._on_unload.clear()
    else:
        await _fl.async_close(entry)
    await _fl.async_setup(hass, entry, _FlConfig.from_mapping(_FL_TEXT))
    _FL_CLOCK[0] += 1000.0
    before = _fl_storage.SAVE_COUNTS.get(_fl_key(entry), 0)
    await _fl_fire(hass, "sensor.fd", "E5", 10)
    after = _fl_storage.SAVE_COUNTS.get(_fl_key(entry), 0)
    return len(hass.state_listeners), after - before
_rv_leak = _fl_aio.run(_rv_failed_setup(True))
_rv_null = _fl_aio.run(_rv_failed_setup(False))
print("REVIEWER-PROBE failed-setup (listeners, saves on one event):", _rv_leak, "null control (closed by unload):", _rv_null)
