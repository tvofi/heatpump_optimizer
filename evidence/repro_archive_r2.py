"""Reviewer's reproduction, round 2 (the reviewer's instrument, not a finder's): corpus_mirror.safe_extract
over archives whose member cannot be READ, and one the local file system refuses for a reason of its own."""
import io, os, struct, sys, tempfile, zipfile, importlib
from pathlib import Path
sys.path.insert(0, "tools/audit/seat")
cm = importlib.import_module("corpus_mirror")

def z(members, method=zipfile.ZIP_DEFLATED):
    b = io.BytesIO()
    with zipfile.ZipFile(b, "w", method) as f:
        for n, d in members:
            f.writestr(n, d)
    return b.getvalue()

def patch(data, local=None, central=None):
    """Rewrite fixed header fields of the one member: (offset in header, struct fmt, value)."""
    b = bytearray(data)
    lo, ce = b.find(b"PK\x03\x04"), b.find(b"PK\x01\x02")
    for base, edits in ((lo, local or []), (ce, central or [])):
        for off, fmt, val in edits:
            struct.pack_into(fmt, b, base + off, val)
    return bytes(b)

plain = z([("m.txt", b"hello hello hello hello hello hello hello hello")])
shapes = {
    "null control: one deflated member": plain,
    "the member's encrypted flag is set": patch(plain, [(6, "<H", 1)], [(8, "<H", 1)]),
    "the member's compression method is one zipfile does not implement (99)": patch(plain, [(8, "<H", 99)], [(10, "<H", 99)]),
    "the member's deflate stream is corrupt": None,
    "the member's stream ends early": None,
}
# corrupt / truncated stream: overwrite the compressed bytes in place
lo = plain.find(b"PK\x03\x04"); nlen, xlen = struct.unpack_from("<HH", plain, lo + 26); start = lo + 30 + nlen + xlen
csize = struct.unpack_from("<I", plain, lo + 18)[0]
b = bytearray(plain); b[start:start + csize] = b"\xff" * csize; shapes["the member's deflate stream is corrupt"] = bytes(b)
big = z([("m.txt", os.urandom(4000).hex().encode())])
lo = big.find(b"PK\x03\x04"); nlen, xlen = struct.unpack_from("<HH", big, lo + 26); start = lo + 30 + nlen + xlen
csize = struct.unpack_from("<I", big, lo + 18)[0]
b = bytearray(big); b[start + csize // 2:start + csize] = b"\x00" * (csize - csize // 2); shapes["the member's stream ends early"] = bytes(b)

def run(label, data, dest=None):
    d = dest or Path(tempfile.mkdtemp()) / "out"
    try:
        print(f"{label}: returned {cm.safe_extract(data, d)!r}")
    except Exception as e:
        print(f"{label}: RAISED {type(e).__name__} (uncaught by safe_extract)")

for label, data in shapes.items():
    run(label, data)

# through a scan, as the round-1 arm does: the Stub of the instrument's own self-test
for label in ("the member's encrypted flag is set", "the member's compression method is one zipfile does not implement (99)"):
    td = Path(tempfile.mkdtemp())
    s = cm.Stub(hostile={"repos/o/r/actions/runs/901/logs": shapes[label]})
    mi = cm.Mirror(td / "p", run=s.run, run_bytes=s.run_bytes, git=s.git, http=s.http, new_bare=s.new_bare, sleep=s.sleeps.append,
                   now=lambda: s.clock, repo="o/r", say=[].append)
    try:
        rc = mi.scan(["S5"], "https://example.invalid/o/r", {})
        print(f"scan, run 901's logs archive where {label}: rc {rc}, state {mi.cur['state']}, run logs {mi.cur['items'].get('run logs')}")
    except Exception as e:
        cur = td / "p"
        print(f"scan, run 901's logs archive where {label}: RAISED {type(e).__name__} out of scan(); in-memory state {mi.cur['state']!r}")
