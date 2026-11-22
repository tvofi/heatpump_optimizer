import logging
mut = mutate(SID, "_size_step_power", "        if best is not None:\n            one_peak", "        if False:\n            one_peak")
moved, n = scan(mut)
print(f"RESULT inputs_moved={moved}/{n} count  (returned step power)")


class Count(logging.Handler):
    n = 0

    def emit(self, record):
        Count.n += 1


h = Count(logging.DEBUG)
sysid._LOGGER.addHandler(h)
old = sysid._LOGGER.level
sysid._LOGGER.setLevel(logging.DEBUG)
call(SID._size_step_power, 6.0, 3.0, 21.0, 2.0, HOUSES["features_heavy"])
bl = Count.n
Count.n = 0
call(mut, 6.0, 3.0, 21.0, 2.0, HOUSES["features_heavy"])
print(f"RESULT debug_records_baseline={bl} mutant={Count.n}  (the branch's only effect)")
sysid._LOGGER.removeHandler(h)
sysid._LOGGER.setLevel(old)
tail()
