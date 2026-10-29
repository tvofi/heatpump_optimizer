import sys
sys.path.insert(0, sys.argv[1] + "/tools/audit/seat")
import ref_privacy as rp
ident = rp.Identity.of_host()
lines = open(sys.argv[2]).read().splitlines()
hits = [(i + 1, rp._leaks(l, ident)) for i, l in enumerate(lines)]
hits = [(n, h) for n, h in hits if h]
print(f"RESULT {sys.argv[3]} refusals={len(hits)} {hits}")
