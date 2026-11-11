import pathlib, sys
d = pathlib.Path("/root/ev/mut")
def bad(name):
    t = (d / f"{name}.log").read_text().split("STDERR-TAIL")[0].splitlines()
    return t[1], [l.strip() for l in t[2:] if l.strip() and not l.startswith(("ALL ", "==", "--")) ]
rc, base = bad("control"); base_set = set(base)
print("control", rc, len(base)); [print("   ", l[:230]) for l in base[:8]]
for f in sorted(d.glob("*.log")):
    n = f.stem
    if n in ("control", "driver"): continue
    rc, b = bad(n); new = [l for l in b if l not in base_set]
    print(f"{n} {rc} lines-not-in-control {len(new)}" + ("   <-- SURVIVED" if not new else ""))
    for l in new[:int(sys.argv[1]) if len(sys.argv) > 1 else 4]: print("   ", l[:230])
