def drive(mutated, seq):
    """Feed fail/recover events; (WARNING, INFO, DEBUG records about the weather fetch, outage cycles, stale)."""
    c = make_coord()
    with arm(NAME, OLD, NEW, mutated), counting("eather forecast") as lg, counting("Plans continue") as lg2:
        for ev in seq:
            if ev == "fail":
                c._weather_fetch_failed("Weather forecast fetch failed")
            else:
                c._weather_fetch_recovered()
    hits = lg.hits + [h for h in lg2.hits if h not in lg.hits]
    by = {lv: sum(1 for l, _ in hits if l == lv) for lv in ("WARNING", "INFO", "DEBUG")}
    return by["WARNING"], by["INFO"], by["DEBUG"], c._weather_outage_cycles, c._weather_stale_since is not None


SEQ = ("fail", "fail", "recover")
b, m = drive(False, SEQ), drive(True, SEQ)
print(f"RESULT weather_baseline=(warnings,infos,debugs,outage_cycles,stale){b}")
print(f"RESULT weather_mutant=(warnings,infos,debugs,outage_cycles,stale){m}")
print(f"RESULT state_moved={int(b[3:] != m[3:])} count (outage counter and staleness)")
print(f"RESULT null_moved={int(drive(False, NULL) != drive(True, NULL))} count (null sequence {NULL})")
tail()
