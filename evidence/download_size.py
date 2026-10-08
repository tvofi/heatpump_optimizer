"""Reviewer's instrument (round 2, not the finder's). Largest week repeat that
capped() keeps inline; then that bundle's download as HA 2025.2.0 writes it:
json.dumps(payload, indent=2, cls=ExtendedJSONEncoder), the entry's diagnostics
under payload["data"] = {config, coordinator, domain, debug}. The coordinator
snapshot is the bundle's own "diagnostics" key (the same snapshot diagnostics.py
passes in), so it is counted a second time, as the real file does."""
import gzip, json, sys
sys.path[:0] = ["tests/hastub", "tests", "custom_components"]
from heatpump_optimizer import debugger as d
week = json.load(gzip.open(sys.argv[1]))
rows = week["cycle_rows"]
def bundle(n):
    b = dict(week); b["cycle_rows"] = rows * n; return b
lo, hi = 1, 200
while lo < hi:
    mid = (lo + hi + 1) // 2
    if "inline" not in d.capped(bundle(mid), "k"): lo = mid
    else: hi = mid - 1
b = bundle(lo)
snap = week.get("diagnostics")
ha = {"home_assistant": {"installation_type": "Home Assistant OS", "version": "2025.2.0"},
      "custom_components": {}, "integration_manifest": {}, "setup_times": {}}
payload = {**ha, "data": {"config": {}, "coordinator": snap, "domain": "heatpump_optimizer", "debug": b},
           "issues": []}
download = len(json.dumps(payload, indent=2, default=str).encode())
snap_bytes = len(json.dumps({"data": {"coordinator": snap}}, indent=2, default=str).encode())
print(f"RESULT repeat_inline_max={lo}")
print(f"RESULT capped_measure={d.download_bytes(b) + d.DOWNLOAD_HEADROOM_BYTES} cap={d.INLINE_CAP_BYTES}")
print(f"RESULT coordinator_snapshot_indent2_bytes={snap_bytes} headroom={d.DOWNLOAD_HEADROOM_BYTES}")
print(f"RESULT download_indent2_bytes={download} within_cap={download <= d.INLINE_CAP_BYTES}")
nb = bundle(lo + 1)
print(f"RESULT next_repeat_capped_inline={'inline' not in d.capped(nb, 'k')}")
