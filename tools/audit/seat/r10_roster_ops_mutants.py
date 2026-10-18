#!/usr/bin/env python3
"""R10-ROSTER-OPS: every plant roster_edit.py's self-test must refuse.

Metric, one line per plant: `RESULT mutant=<name> rc=<rc> fails=<n>`, then the
failing check names. Each plant is one exact one-occurrence replacement in
tools/audit/seat/roster_edit.py; the driver applies it, runs
`roster_edit.py --self-test`, and restores the file byte for byte. It refuses
to start when the file differs from HEAD, so a restore cannot overwrite work.
Expected: every plant rc=1 with fails>=1 -- a FAIL line, not a crash (a
crash is rc=1 with fails=0 and prints its tail).

Plants, one per refusal of the two ops and per round-trip property:
  A1-A5  set-after: unknown after-group, self-edge, repeated edge, cycle, and
         the cycle checked on the graph before the edit.
  A6     set-after's unknown target group (a silent write to a detached dict).
  A7     set-after on a no-op moves the key, so its bytes change.
  C1-C5  drop-carry: an absent carry, no match (silently drops entry 0), an
         ambiguous match (silently drops the first), a negative index (drops
         the last), a non-integer index (silently drops entry 0).
  C6     drop-carry of the last entry leaves `"carry": []`.
  C7     drop-carry by index drops the neighbour.
  C8     drop-carry's unknown group.
  P1-P3  the argparse refusals: index and --match together, neither, and
         --match on another op.
  D1     the dump's indent, the byte round-trip itself.

    python3 tools/audit/seat/r10_roster_ops_mutants.py [plant ...]
    python3 tools/audit/seat/r10_roster_ops_mutants.py --null

Null control: `--null` runs the self-test with no plant, which must print
rc=0 fails=0.
"""
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TARGET = "tools/audit/seat/roster_edit.py"
DETACHED = ('g = next((x for x in roster.get("groups", []) '
            'if x.get("group") == group), {})')

PLANTS = {
    "A1": ('    if bad:\n        raise Refuse(f"set-after: {group} after names',
           '    if False:\n        raise Refuse(f"set-after: {group} after names'),
    "A2": ("    if group in after:\n", "    if False:\n"),
    "A3": ("    if dup:\n", "    if False:\n"),
    "A4": ("    if cycle:\n", "    if False:\n"),
    "A5": ("    edges[group] = after\n", ""),
    "A6": ('    g = _need(roster, group)\n    after = [] if spec',
           f'    {DETACHED}\n    after = [] if spec'),
    "A7": ('    g["after"] = after\n',
           '    g.pop("after", None)\n    g["after"] = after\n'),
    "C1": ('    if not carry:\n        raise Refuse(f"drop-carry: {group} carries nothing")',
           '    if False:\n        raise Refuse(f"drop-carry: {group} carries nothing")'),
    "C2": ("if match in c]\n", "if match in c] or [0]\n"),
    "C3": ("        if len(hits) > 1:\n", "        if False:\n"),
    "C4": ("        if not 0 <= i < len(carry):\n",
           "        if not i < len(carry):\n"),
    "C5": ("            i = int(index)\n",
           '            i = int(index) if index.lstrip("-").isdigit() else 0\n'),
    "C6": ('    if not carry:\n        del g["carry"]\n',
           '    if False:\n        del g["carry"]\n'),
    "C7": ("    del carry[i]\n", "    del carry[i - 1]\n"),
    "C8": ('    g = _need(roster, group)\n    carry = g.get("carry")',
           f'    {DETACHED}\n    carry = g.get("carry")'),
    "P1": ('p.error("drop-carry takes an index or --match, not both")', "pass"),
    "P2": ('p.error("drop-carry needs an index or --match")', "pass"),
    "P3": ('p.error("--match is a drop-carry flag")', "pass"),
    "D1": ("return json.dumps(roster, indent=1)",
           "return json.dumps(roster, indent=2)"),
}


def self_test():
    r = subprocess.run([sys.executable, TARGET, "--self-test"], cwd=ROOT,
                       capture_output=True, text=True)
    fails = [ln for ln in r.stdout.splitlines() if ln.startswith("FAIL ")]
    return r.returncode, fails, (r.stdout + r.stderr).strip().splitlines()[-3:]


def report(name, rc, fails, tail):
    print(f"RESULT mutant={name} rc={rc} fails={len(fails)}")
    for f in fails:
        print("   ", re.sub(r" \(got: .*\)$", "", f))
    if rc and not fails:
        print("    crash tail:", *tail, sep="\n      ")


def main(argv):
    path = ROOT / TARGET
    if subprocess.run(["git", "diff", "--quiet", "HEAD", "--", TARGET],
                      cwd=ROOT).returncode != 0:
        print(f"refusing: {TARGET} differs from HEAD", file=sys.stderr)
        return 2
    if argv == ["--null"]:
        report("null", *self_test())
        return 0
    names = argv or list(PLANTS)
    unknown = [n for n in names if n not in PLANTS]
    if unknown:
        print(f"unknown plant(s): {unknown}", file=sys.stderr)
        return 2
    original = path.read_bytes()
    survivors = []
    try:
        for name in names:
            old, new = PLANTS[name]
            text = original.decode("utf-8")
            if text.count(old) != 1:
                print(f"plant {name}: anchor occurs {text.count(old)} times",
                      file=sys.stderr)
                return 2
            path.write_bytes(text.replace(old, new).encode("utf-8"))
            rc, fails, tail = self_test()
            path.write_bytes(original)
            report(name, rc, fails, tail)
            if not fails:
                survivors.append(name)
    finally:
        path.write_bytes(original)
    print(f"plants: {len(names)}, without a FAIL line: {survivors or 'none'}")
    return 1 if survivors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
