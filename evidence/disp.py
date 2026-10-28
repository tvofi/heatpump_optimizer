from datetime import datetime, timezone
from math import comb
import re
for s in ["2026-10-15T12:37Z", "2026-10-15T12:37:05Z", "2026-10-15Z", "2026-10-15T12:37+02:00", "2026-10-15T12:37Z+01:00"]:
    r = []
    for rep in ("+00:00", "+00"):
        try: r.append(datetime.fromisoformat(s.replace("Z", rep)).astimezone(timezone.utc).isoformat())
        except Exception as e: r.append("ERR "+str(e)[:50])
    print("fromiso", s, r, "SAME" if r[0]==r[1] else "DIFF")
N32 = re.compile(r"^bus-nonce:\s*([0-9a-f]{32})", re.M); N31 = re.compile(r"^bus-nonce:\s*([0-9a-f]{31})", re.M)
b = "bus-nonce: " + "a"*31 + "\n"
print("nonce31 body: orig", N32.search(b), "| mutant", N31.search(b)[1][:8])
def cdf(k, n, p): return sum(comb(n, i) * p ** i * (1 - p) ** (n - i) for i in range(k + 1))
import struct
def nxt(x, d): 
    i = struct.unpack('<q', struct.pack('<d', x))[0]; return struct.unpack('<d', struct.pack('<q', i + d))[0]
hits = []
for n in range(1, 41):
    for k in range(0, n):
        lo, hi = 0.0, 1.0
        for _ in range(200):
            mid = (lo+hi)/2
            if cdf(k, n, mid) > 0.05: lo = mid
            else: hi = mid
        for d in range(-3000, 3001):
            p = nxt(lo, d)
            if cdf(k, n, p) == 0.05: hits.append((n, k, repr(p))); break
print("exact cdf==0.05 hits (n,k,p0):", len(hits), hits[:8])
