

T0 = co.dt_util.now().replace(microsecond=0)


def drive(dt_h, start, end, **patch):
    """One quiet buffer interval of dt_h hours from start to end degC; returns the samples the learner folded."""
    c = coord()
    c._current_action = {"power": 0.0}
    c._last_buffer_temp_sample, c._last_buffer_sample_time = None, None
    c._buffer_heating_since_sample = False
    rate0, n0 = c._buffer_cooling_rate, c._buffer_cooling_samples
    clock = [T0]

    async def nosave():
        return None

    with mock.patch.object(co.dt_util, "now", lambda: clock[0]), \
         mock.patch.object(c, "_async_save_thermal_learning", nosave), \
         mock.patch.multiple(co, **patch) if patch else mock.patch.object(co, "BUFFER_AMBIENT_TEMP", co.BUFFER_AMBIENT_TEMP):
        asyncio.run(c._async_learn_buffer_cooling(start))
        clock[0] = T0 + co.timedelta(hours=dt_h)
        asyncio.run(c._async_learn_buffer_cooling(end))
    return c._buffer_cooling_samples - n0, round(c._buffer_cooling_rate - rate0, 6)


b, m = drive(1.0, 27.0, 26.8), drive(1.0, 27.0, 26.8, BUFFER_COOLING_MIN_DELTA=8.0)
print(f"RESULT samples_baseline={b[0]} count (rate {b[1]:+.6f})")
print(f"RESULT samples_mutant={m[0]} count (rate {m[1]:+.6f})")
for s, e in ((24.0, 23.9), (28.0, 27.9), (28.1, 28.0)):
    print(f"RESULT inputs {s}->{e}: baseline={drive(1.0, s, e)} mutant={drive(1.0, s, e, BUFFER_COOLING_MIN_DELTA=8.0)}")
nb, nm = drive(0.2, 40.0, 39.8), drive(0.2, 40.0, 39.8, BUFFER_COOLING_MIN_DELTA=8.0)
print(f"RESULT null_delta={int(nb != nm)} count")
tail()
