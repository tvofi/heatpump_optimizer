import json
import sys
import hashlib
import os

sys.path.insert(0, "tests")
import closure

E = "/mnt/project-files/audit-r9/fix/evidence/F10.9/"
print(sorted(os.listdir(E)))


def load(n):
    p = E + n
    b = open(p, "rb").read()
    print(n, hashlib.sha1(b).hexdigest()[:8])
    return json.loads(b)


A = load("strace_features_dc6c97e4.json")
B = load("lane_dst_checks_dc6c97e4.json")
H = load("hookonly_features_dc6c97e4.json")
print("how", A.get("how"), B.get("how"), H.get("how"))
real = lambda r: {
    f for f in r["files"] if closure._is_real_file(f) and not closure.is_inert(f)
}
rb = real(B)
print(
    "A",
    len(A["files"]),
    "B real",
    len(rb),
    "missing from A",
    sorted(rb - set(A["files"])),
)
print("missing from hook-only H", sorted(rb - set(H["files"])))
main = json.loads(os.popen("git show dc6c97e4:tests/closures.json").read())["closures"][
    "tests/features.py"
]
print("missing from main committed features", sorted(rb - set(main)))
