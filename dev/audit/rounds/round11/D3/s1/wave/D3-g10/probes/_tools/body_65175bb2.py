NAME, OLD, NEW = "async_diagnose_interval", "if report is None:", "if False:"


def drive(mutated, report):
    c = make_coord()
    refreshes = []

    async def fake_await(hass, fn, *args):
        return report

    async def refresh():
        refreshes.append(1)

    patches = [mock.patch.object(co, "_await_process", fake_await), mock.patch.object(c, "async_request_refresh", refresh)]
    if report is not None:
        patches.append(mock.patch.object(co, "_store_diagnosis", lambda coord, rep: None))
    with arm(NAME, OLD, NEW, mutated), counting("No settled interval") as lg:
        for p in patches:
            p.start()
        try:
            out = asyncio.run(c.async_diagnose_interval())
        finally:
            for p in patches:
                p.stop()
    return sum(1 for lv, _ in lg.hits if lv == "INFO"), out, len(refreshes)


b, m = drive(False, None), drive(True, None)
print(f"RESULT none_baseline=(infos,report,refreshes){b}")
print(f"RESULT none_mutant=(infos,report,refreshes){m}")
rep = SimpleNamespace(verdict="ok")
print(f"RESULT null_moved={int(drive(False, rep) != drive(True, rep))} count (worker returns a report)")
tail()
