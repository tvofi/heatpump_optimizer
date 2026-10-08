"""Reviewer's instrument (not the finder's): is a bundle that capped() carries
inline also under INLINE_CAP_BYTES in the file HA's diagnostics download writes?
HA 2025.2.0 diagnostics/_async_get_json_file_response:
    json.dumps(payload, indent=2, cls=ExtendedJSONEncoder)
"""
import gzip, json, sys
sys.path[:0] = ["tests/hastub", "tests", "custom_components"]
from heatpump_optimizer import debugger as d
week = json.load(gzip.open(sys.argv[1]))
rows = week["cycle_rows"]
lo, hi = 1, 200
def bundle(n):
    b = dict(week); b["cycle_rows"] = rows * n; return b
# largest repeat whose bundle capped() still carries inline
while lo < hi:
    mid = (lo + hi + 1) // 2
    if "inline" not in d.capped(bundle(mid), "k"): lo = mid
    else: hi = mid - 1
b = bundle(lo)
measured = len(d._dumps(b).encode())
download = len(json.dumps({"data": {"debug": b}}, indent=2, default=str).encode())
print(f"RESULT repeat={lo}")
print(f"RESULT capped_inline={'inline' not in d.capped(b, 'k')}")
print(f"RESULT measured_bytes={measured} cap={d.INLINE_CAP_BYTES}")
print(f"RESULT download_indent2_bytes={download} over_cap={download > d.INLINE_CAP_BYTES} ratio={download/measured:.3f}")
# null control: the same bundle serialized the way capped() measures it is under the cap
print(f"RESULT null_compact_under_cap={measured <= d.INLINE_CAP_BYTES}")
