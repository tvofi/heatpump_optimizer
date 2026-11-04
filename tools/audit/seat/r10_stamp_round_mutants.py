#!/usr/bin/env python3
"""R10-STAMP-ROUND-MAJOR: every plant stamp.py's self-test must refuse.

Metric, one line per plant: `RESULT mutant=<name> rc=<rc> fails=<n>`, then the
failing check names. Each plant is one exact one-occurrence replacement in
tools/release/stamp.py; the driver applies it, runs `stamp.py --self-test`, and
restores the file byte for byte. It refuses to start when the file differs from
HEAD, so a restore cannot overwrite work. Expected: every plant rc=1 with
fails>=1 -- a FAIL line, not a crash (a crash is rc=1 with fails=0 and prints
its tail).

Plants, one per predicate of decision 0016's `next_version` and its wiring:
  R1  a round close stamps N.1.0 instead of N.0.0.
  R2  a round equal to the current major is let through (`<=` to `<`).
  R3  the roster's round is never compared (also passes an unreadable roster).
  R4  --round-close beside --bump is let through.
  R5  --bump major is let through to bump(), which has no major arm.
  R6  main() drops --round-close before next_version.

    python3 tools/audit/seat/r10_stamp_round_mutants.py [plant ...]
    python3 tools/audit/seat/r10_stamp_round_mutants.py --null [<base rev>]
    python3 tools/audit/seat/r10_stamp_round_mutants.py --self-test

Null control: `--null` runs the self-test with no plant, which must print
rc=0 fails=0; given a base revision it also prints every patch and minor bump
over a version grid from that revision's stamp.py and from the tree's, through
`next_version` where it exists, and reports `RESULT null grid=<n> differ=<d>`:
d=0 is patch and minor behaving exactly as before. `--self-test` does not run
the plants and pins the preconditions instead: every anchor occurs exactly
once in the target, and the grid comparison counts a planted difference.
"""
import importlib.util
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TARGET = "tools/release/stamp.py"

PLANTS = {
    "R1": ('return f"{round_close}.0.0", None', 'return f"{round_close}.1.0", None'),
    "R2": ("if round_close <= major:", "if round_close < major:"),
    "R3": ("if round_close != roster_round:", "if False:"),
    "R4": ('        if part is not None:\n            return None, "--round-close',
           '        if False:\n            return None, "--round-close'),
    "R5": ('if part == "major":\n        return None', 'if False:\n        return None'),
    "R6": ("nxt, why = next_version(current, args.bump, args.round_close,",
           "nxt, why = next_version(current, args.bump, None,"),
}

GRID = [f"{a}.{b}.{c}" for a in range(12) for b in (0, 1, 9, 10, 99)
        for c in (0, 1, 5, 9, 10, 99)]


def target_self_test():
    r = subprocess.run([sys.executable, TARGET, "--self-test"], cwd=ROOT,
                       capture_output=True, text=True)
    fails = [ln.strip() for ln in r.stdout.splitlines() if ln.startswith("  FAIL")]
    return r.returncode, fails, (r.stdout + r.stderr).strip().splitlines()[-3:]


def report(name, rc, fails, tail):
    print(f"RESULT mutant={name} rc={rc} fails={len(fails)}")
    for f in fails:
        print(f"    {f}")
    if rc and not fails:
        print("    crash tail:")
        for ln in tail:
            print(f"      {ln}")


def grid_rows(path):
    """`version part next` for every patch and minor bump over GRID, read from
    the stamp.py at `path`: through next_version when it has one, else bump."""
    spec = importlib.util.spec_from_file_location("stamp_under_test", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    nv = getattr(mod, "next_version", None)
    return [f"{v} {p} {nv(v, p, None, None)[0] if nv else mod.bump(v, p)}"
            for v in GRID for p in ("patch", "minor")]


def differ(a, b):
    return sum(x != y for x, y in zip(a, b)) + abs(len(a) - len(b))


def null(base):
    rc, fails, tail = target_self_test()
    report("null", rc, fails, tail)
    if base is None:
        return 1 if rc or fails else 0
    src = subprocess.run(["git", "show", f"{base}:{TARGET}"], cwd=ROOT,
                         capture_output=True, text=True, check=True).stdout
    with tempfile.TemporaryDirectory() as d:
        old = Path(d) / "stamp_base.py"
        old.write_text(src)
        before, after = grid_rows(old), grid_rows(ROOT / TARGET)
    d = differ(before, after)
    print(f"RESULT null grid={len(after)} differ={d}")
    return 1 if rc or fails or d else 0


def self_test():
    passed = failed = 0

    def ck(name, ok):
        nonlocal passed, failed
        passed, failed = passed + bool(ok), failed + (not ok)
        print(f"  {'ok  ' if ok else 'FAIL'} {name}")

    text = (ROOT / TARGET).read_text()
    for name, (old, new) in PLANTS.items():
        ck(f"{name}: its anchor occurs exactly once", text.count(old) == 1)
        compile(text.replace(old, new), TARGET, "exec")
    rows = grid_rows(ROOT / TARGET)
    ck("the grid covers patch and minor for every version", len(rows) == 2 * len(GRID))
    planted = rows[:]
    planted[0] = planted[0] + "x"
    ck("the grid comparison counts a planted difference, and none without one",
       differ(rows, planted) == 1 and differ(rows, rows) == 0)
    print(f"r10_stamp_round_mutants self-test: {passed + failed} checks, {failed} failed")
    return 1 if failed else 0


def main(argv):
    path = ROOT / TARGET
    if argv == ["--self-test"]:
        return self_test()
    if subprocess.run(["git", "diff", "--quiet", "HEAD", "--", TARGET], cwd=ROOT).returncode:
        print(f"refused: {TARGET} differs from HEAD; a restore would overwrite it")
        return 2
    if argv[:1] == ["--null"]:
        return null(argv[1] if len(argv) > 1 else None)
    names = argv or list(PLANTS)
    unknown = [n for n in names if n not in PLANTS]
    if unknown:
        print(f"refused: unknown plant(s) {unknown}; known: {list(PLANTS)}")
        return 2
    original = path.read_bytes()
    survivors = []
    try:
        for name in names:
            old, new = PLANTS[name]
            path.write_text(original.decode().replace(old, new))
            rc, fails, tail = target_self_test()
            report(name, rc, fails, tail)
            if not fails:
                survivors.append(name)
    finally:
        path.write_bytes(original)
    print(f"plants: {len(names)}, without a FAIL line: {survivors or 'none'}")
    return 1 if survivors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
