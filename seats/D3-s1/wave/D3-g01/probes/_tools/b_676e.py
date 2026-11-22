

def drive(cap, broken, cycles=10):
    hass = FakeHass({})
    solves = []

    async def unusable(*a, **k):
        raise co.ProcessWorkerUnavailable("probe: worker unusable")

    async def healthy(*a, **k):
        return "worker-plan"

    async def run():
        n = 0
        for _ in range(cycles):
            try:
                await co._await_optimize(hass, object(), object())
            except Exception as err:  # UpdateFailed: the skip
                return n, type(err).__name__
            n += 1
        return n, None

    with mock.patch.object(co, "WORKER_FALLBACK_CAP", cap), \
         mock.patch.object(co, "_await_process", unusable if broken else healthy), \
         mock.patch.object(co, "optimize_in_process", lambda *a: solves.append(1) or "inproc-plan"):
        carried, raised = asyncio.run(run())
    return len(solves), carried, raised


b, m = drive(3, True), drive(6, True)
print(f"RESULT inprocess_solves_before_skip_baseline={b[0]} count (then {b[2]})")
print(f"RESULT inprocess_solves_before_skip_mutant={m[0]} count (then {m[2]})")
nb, nm = drive(3, False), drive(6, False)
print(f"RESULT null_inprocess_baseline={nb[0]} mutant={nm[0]} count")
print(f"RESULT null_delta={abs(nb[0] - nm[0]) + abs(nb[1] - nm[1])} count")
tail()
