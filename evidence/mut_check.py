"""Reviewer mutant check (the reviewer's own instrument, not the finder's)."""
from datetime import datetime, timedelta, timezone
from custom_components.heatpump_optimizer import heat_energy as he
NOW = datetime(2026, 1, 10, 22, 0, tzinfo=timezone.utc)
m = he.HeatEnergyMeter(counter=True)
m.cycle = (NOW - timedelta(hours=0.5), NOW)
m.dwell.observe(NOW - timedelta(hours=1), he.DHW, None); m.dwell.observe(NOW, he.DHW, None)
bridge = he.replay_gate(None, None, None, None, 1.0, m, (1.0, 0.0), True, False)[1]
heater = he.replay_gate(None, None, None, None, 1.0, m, (1.0, 0.0), True, True)[1]
import subprocess, sys
out = subprocess.run([sys.executable, "../s/unobs_span.py"], capture_output=True, text=True).stdout.splitlines()[0]
space = float(out.split("space_kw=")[1].split()[0])
ok = bridge is True and heater is False and abs(space - 10.0 / 5.5) < 1e-9
print(f"RESULT bridge={bridge} heater_blocks={not heater} observed_space_kw={space:.4f} -> {'PASS' if ok else 'FAIL'}")
sys.exit(0 if ok else 1)
