"""Classify a roster edit pushed after a roster PR's merge verdict: does the verdict still cover it?

A verdict is for one head. A later push moves the head, but a bookkeeping-only delta (new groups
appended; stage, resume, carry or edge changes on groups the verdicted diff never touched; and on a
group it did touch, bookkeeping in fields other than the ones it changed) leaves everything the
reviewer read byte-identical. This prints that judgement mechanically, so the
verdict can be carried (app_approve.sh --carry) with this output as its note instead of buying a
fresh review. Read-only; run in a clone that has fetched main and the roster branch:

    python3 roster_delta.py <verdicted-sha> <new-head> [--base origin/main] [--file PATH]

Exit 0: CARRIES (every covered group identical; the delta is bookkeeping only).
Exit 1: REVIEW (a covered group changed, or a field outside the bookkeeping set changed).
"""
import json
import subprocess
import sys

ROSTER = "dev/programme/rosters/wave-r10-groups.json"
BOOKKEEPING = {"resume", "stage", "carry", "after"}  # fields a bookkeeping delta may touch


def load(ref, path):
    out = subprocess.run(["git", "show", f"{ref}:{path}"], capture_output=True, text=True)
    if out.returncode:
        return {}
    return {g["group"]: g for g in json.loads(out.stdout).get("groups", [])}


def changed(a, b):
    return {k for k in set(a) | set(b) if a.get(k) != b.get(k)}


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 2
    verdicted, head = argv[0], argv[1]
    base = argv[argv.index("--base") + 1] if "--base" in argv else "origin/main"
    path = argv[argv.index("--file") + 1] if "--file" in argv else ROSTER
    mb = subprocess.run(["git", "merge-base", base, verdicted], capture_output=True, text=True,
                        check=True).stdout.strip()
    g_base, g_ver, g_head = load(mb, path), load(verdicted, path), load(head, path)
    covered = {n for n in set(g_base) | set(g_ver) if g_base.get(n) != g_ver.get(n)}
    problems, notes = [], []
    for n in sorted(set(g_ver) | set(g_head)):
        a, b = g_ver.get(n), g_head.get(n)
        if a == b:
            continue
        if n in covered:
            reviewed = changed(g_base.get(n) or {}, a or {})  # the fields the reviewer read here
            fields = changed(a or {}, b or {})
            if a is not None and b is not None and not (fields & reviewed) and fields <= BOOKKEEPING \
                    and len(b.get("carry") or []) >= len(a.get("carry") or []):
                notes.append(f"{n}: covered, but only bookkeeping outside the reviewed fields "
                             f"({', '.join(sorted(fields))}; reviewed: {', '.join(sorted(reviewed))})")
            else:
                problems.append(f"{n}: covered by the verdicted diff and changed ({', '.join(sorted(fields))})")
        elif a is None:
            notes.append(f"{n}: appended (check it equals its source brief)")
        elif b is None:
            problems.append(f"{n}: removed")
        else:
            fields = changed(a, b)
            if "after" in fields:
                notes.append(f"{n}: after-edge changed (the carry note must give the edge's reason)")
            if fields <= BOOKKEEPING:
                if "carry" in fields and len(b.get("carry") or []) < len(a.get("carry") or []):
                    problems.append(f"{n}: a carry was removed")
                else:
                    notes.append(f"{n}: bookkeeping ({', '.join(sorted(fields))})")
            else:
                problems.append(f"{n}: non-bookkeeping fields changed ({', '.join(sorted(fields - BOOKKEEPING))})")
    print(f"merge base {mb[:9]}; verdicted {verdicted[:9]} covers {len(covered)} group(s): {', '.join(sorted(covered))}")
    for line in notes:
        print("  ok     " + line)
    for line in problems:
        print("  REVIEW " + line)
    print("CARRIES: the verdict covers this head (run brief_lint and carry_audit owners too)"
          if not problems else "REVIEW: the delta touches what the reviewer read")
    return 0 if not problems else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
