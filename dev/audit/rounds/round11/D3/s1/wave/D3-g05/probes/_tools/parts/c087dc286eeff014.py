from dataclasses import replace
from custom_components.heatpump_optimizer.external_heat import ExternalHeatDetector, ExternalHeatObservation
OLD, NEW = "max_sample_hours=max(1.0, 1.5 * interval_hours),", "max_sample_hours=(1.0),"
MUT = mutant_method("_external_heat_config", OLD, NEW)


def cfg(fn, minutes):
    return fn(coord(optimization_interval=minutes, wood_furnace_enabled=True, external_heat_detection_enabled=True))


def active_after(conf, minutes, n=4):
    """A DHW tank rising 4 C/h with the compressor off, sampled once per update cycle."""
    det = ExternalHeatDetector(conf)
    t0 = datetime(2026, 1, 15, 12, 0, tzinfo=timezone.utc)
    for i in range(n):
        h = i * minutes / 60.0
        det.update(ExternalHeatObservation(now=t0 + timedelta(minutes=i * minutes), dhw_temp=40.0 + 4.0 * h,
                                           buffer_temp=None, commanded_power_kw=0.0, measured_power_kw=0.0))
    return det.suppressing


moved = 0
for minutes in range(10, 125, 5):  # the config flow's own range, _number(10, 120, 5)
    b, m = cfg(CLS._external_heat_config, minutes), cfg(MUT, minutes)
    moved += int(b.max_sample_hours != m.max_sample_hours)
for minutes in (30, 60, 61, 90, 120):
    b, m = cfg(CLS._external_heat_config, minutes), cfg(MUT, minutes)
    print(f"RESULT interval{minutes}_max_sample_hours baseline={b.max_sample_hours} mutant={m.max_sample_hours}")
    print(f"RESULT interval{minutes}_detector_suppressing baseline={active_after(b, minutes)} mutant={active_after(m, minutes)}")
print(f"RESULT intervals_moved={moved} of 23 count")
tail()
