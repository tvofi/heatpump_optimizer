import sys; sys.path.insert(0, "dev/audit/rounds/round11/D3/s1/wave/D3-g35/probes")
import sysid_probe_common as c
m = c.load()
for kw in [dict(), dict(drift=0.01), dict(noise=0.02), dict(gains=0.0), dict(gains=-0.3), dict(gains=2.0), dict(cadence_min=30)]:
    print(kw, c.fmt(c.run(m, c.plant_samples(m, **kw))))
