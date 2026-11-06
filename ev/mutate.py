import sys, pathlib
p = pathlib.Path(sys.argv[1]) / "custom_components/heatpump_optimizer/coordinator.py"
s = p.read_text()
M = {
 "m1": [("        return bool(selector.select(timeout_s))",
         "        import select as _s\n        return bool(_s.select([stream], [], [], timeout_s)[0])")],
 "m2": [("    except ProcessWorkerTimeout as err:\n        log_held(hass, key, True, \"%s; %s skipped this cycle\", err, name)\n        raise\n", "")],
 "m3": [("        log_held(hass, f\"process_worker_timeout:{entry_id}\", True,\n                 \"%s; keeping the last plan, a fresh worker starts next cycle\", err)",
         "        _LOGGER.warning(\"%s; keeping the last plan, a fresh worker starts next cycle\", err)")],
 "m4": [("        log_held(hass, key, True, \"%s; %s skipped this cycle\", err, name)\n", "")],
 "m5": [("            if has_fd and not _reply_ready(stdout, timeout):", "            if has_fd and not _reply_ready(stdout, None):"),
        ("        result = await _await_process(hass, fn, *args)\n    except ProcessWorkerTimeout",
         "        try:\n            result = await asyncio.wait_for(_await_process(hass, fn, *args), PROCESS_REPLY_TIMEOUT_S)\n        except TimeoutError as _e:\n            raise ProcessWorkerTimeout('loop deadline') from _e\n    except ProcessWorkerTimeout")],
 "m6": [("    log_held(hass, key, False)\n    return result", "    return result")],
 "m7": [("    log_held(hass, f\"process_worker_timeout:{entry_id}\", False)\n    return result", "    return result")],
}
for old, new in M[sys.argv[2]]:
    assert s.count(old) == 1, (sys.argv[2], old)
    s = s.replace(old, new)
if "asyncio.wait_for" in s and "\nimport asyncio" not in s:
    raise SystemExit("asyncio not imported")
p.write_text(s)
print("mutated", sys.argv[2])
