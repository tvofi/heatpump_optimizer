#!/usr/bin/env python3
"""R10-ROSTER-OPS: every plant roster_edit.py's self-test must refuse.

Metric, one line per plant: `RESULT mutant=<name> rc=<rc> fails=<n>`, then the
failing check names. Each plant is one exact one-occurrence replacement in
tools/audit/seat/roster_edit.py, or in the file a three-part plant names
(`parts`); the driver applies it, runs that file's `--self-test`, and
restores it byte for byte. It refuses to start when any target differs from
HEAD, so a restore cannot overwrite work.
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
  C6     the last drop deletes the `carry` key (the byte round-trip
         regression; the live roster's empty shape is `"carry": []`).
  C7     drop-carry by index drops the neighbour.
  C8     drop-carry's unknown group.
  P1-P3  the argparse refusals: index and --match together, neither, and
         --match on another op.
  D1     the dump's indent, the byte round-trip itself.
  T1-T5  the triage gate (decision 0015): the uncited proposal arm, a
         non-ACCEPT verdict passing, a missing batch read as an empty one, the gate's call
         in write_roster, and added_texts blind to appended carries.
  K1-K9  the carry ledger (#2733): mark-carry's refusals (K1 a carry already
         marked, K2 an unknown mark, K3 implemented without a sha, K4 the
         whole moved arm, K5 a move to itself, K6 dismissed with no reason),
         set-stage bypassing the shared closing rule (K7), the cut-over not
         read (K8), and set-resume --field stage bypassing it (K9).
  L1-L6  roster_lib's predicate, under roster_lib.py --self-test: marks
         ignored (L1), legacy ignored (L2), every group's carries legacy at
         the cut-over (L3), absorbed not closed (L4), closing never
         downgrades (L5), a mark read anywhere in the text (L6).
  Y1     roster_sync's merge bypassing the shared rule.
  R1-R5  carry_audit's roster arm: closed-only issues unreported (R1),
         unlisted issues unreported (R2), #201 reported (R3), absorbed_into
         unnamed (R4), pull requests read as issues (R5).
  S1-S7  the vocabulary barrier (R10-ORCH-ROSTER-SCHEMA): each of the three
         stage-writing ops losing its classification check (S1 set-stage, S2
         set-resume --field stage, S3 append-group), append-group losing the
         size check (S4), the registry itself letting any word through (S5
         stage, S6 size), and apply_op dropping the threaded vocabulary, so a
         legal size is refused (S7 -- the barrier becoming a blanket one).

    python3 tools/audit/seat/r10_roster_ops_mutants.py [plant ...]
    python3 tools/audit/seat/r10_roster_ops_mutants.py --null
    python3 tools/audit/seat/r10_roster_ops_mutants.py --self-test

Null control: `--null` runs the self-test with no plant, which must print
rc=0 fails=0. `--self-test` does not run the plants -- one costs the target's
own minute -- and pins instead the preconditions the sweep rests on: every
anchor occurs exactly once in the target as it stands, every mutant parses,
and report()/select() keep their shapes.
"""
import contextlib
import io
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TARGET = "tools/audit/seat/roster_edit.py"
DROP = '    del g["carry"][_carry_index(g, index, match, "drop-carry")]\n'
LIB, SYNC, AUDIT = ("tools/audit/seat/roster_lib.py",
                    "tools/audit/seat/roster_sync.py", "tools/audit/carry_audit.py")
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
    "C1": ('    if not carry:\n        raise Refuse(f"{op}: {group} carries nothing")',
           '    if False:\n        raise Refuse(f"{op}: {group} carries nothing")'),
    "C2": ("if match in c]\n", "if match in c] or [0]\n"),
    "C3": ("        if len(hits) > 1:\n", "        if False:\n"),
    "C4": ("    if not 0 <= i < len(carry):\n",
           "    if not i < len(carry):\n"),
    "C5": ("        i = int(index)\n",
           '        i = int(index) if index.lstrip("-").isdigit() else 0\n'),
    "C6": (DROP, DROP + '    if not g["carry"]:\n        del g["carry"]\n'),
    "C7": (DROP, DROP.replace(')]', ') - 1]')),
    "C8": ('    g = _need(roster, group)\n    del g["carry"]',
           f'    {DETACHED}\n    g.setdefault("carry", [])\n    del g["carry"]'),
    "P1": ('p.error("drop-carry takes an index or --match, not both")', "pass"),
    "P2": ('p.error(f"{a.op} needs an index or --match")', "pass"),
    "P3": ('p.error("--match is a drop-carry flag")', "pass"),
    "D1": ("return json.dumps(roster, indent=1)",
           "return json.dumps(roster, indent=2)"),
    "T1": ("        if PROPOSAL_RE.search(text) and not cites:\n",
           "        if False:\n"),
    "T2": ('            if verdict != "ACCEPT":\n',
           "            if verdict is None:\n"),
    "T3": ("        return r.stdout if r.returncode == 0 else None\n",
           '        return r.stdout if r.returncode == 0 else ""\n'),
    "T4": ("        if why:\n            raise Refuse(f\"triage gate: {why}; nothing written\")\n", ""),
    "T5": ("        out += [c for c in carry if c not in held]\n", ""),
    "S1": ('    why = _stage_why(stage, rel, group)\n    if why:\n        raise Refuse(why)\n',
           '    why = None  # S1\n    if why:\n        raise Refuse(why)\n'),
    "S2": ('        why = _stage_why(value, rel, group)\n        if why:\n            raise Refuse(why)\n',
           '        why = None  # S2\n        if why:\n            raise Refuse(why)\n'),
    "S3": ('    if stage is not None:\n        why = _stage_why(stage, rel, gid)\n',
           '    if False:  # S3\n        why = _stage_why(stage, rel, gid)\n'),
    "S4": ('    why = _size_why(new.get("size"), sizes, rel, gid)\n    if why:\n'
           '        raise Refuse(f"append-group: {why}")\n',
           '    why = None  # S4\n    if why:\n'
           '        raise Refuse(f"append-group: {why}")\n'),
    "S5": ("    if stage in roster_lib.STAGES:\n        return None\n",
           "    if True:  # S5\n        return None\n"),
    "S6": ("    if size is None or size in sizes:\n        return None\n",
           "    if True:  # S6\n        return None\n"),
    "S7": ("        op_append_group(roster, value, rel, sizes)\n",
           "        op_append_group(roster, value)  # S7\n"),
    "K1": ('    if roster_lib.carry_mark(g["carry"][i]):\n', "    if False:  # K1\n"),
    "K2": ("    if kind not in roster_lib.CARRY_MARKS:\n", "    if False:  # K2\n"),
    "K3": ('    if kind == "implemented" and not SHA_RE.match(arg):\n',
           "    if False:  # K3\n"),
    "K4": ('    if kind == "moved":\n', "    if False:  # K4\n"),
    "K5": ("        if arg == group:\n", "        if False:  # K5\n"),
    "K6": ('    if kind == "dismissed" and not arg:\n', "    if False:  # K6\n"),
    "K7": ('["stage"] = _closing(g, stage, legacy, "set-stage")\n',
           '["stage"] = stage  # K7\n'),
    "K8": ("                    legacy = roster_lib.read_legacy(a.worktree, rel)\n",
           "                    legacy = {}  # K8\n"),
    "K9": ('        value = _closing(g, value, legacy, "set-resume")\n',
           "        pass  # K9\n"),
    "L1": (LIB, "            if carry_mark(c) is None and c not in held]\n",
           "            if c not in held]  # L1\n"),
    "L2": (LIB, "            if carry_mark(c) is None and c not in held]\n",
           "            if carry_mark(c) is None]  # L2\n"),
    "L3": (LIB, '            if (g.get("resume") or {}).get("stage") in CARRY_CLOSED}\n',
           "            }  # L3\n"),
    "L4": (LIB, 'CARRY_CLOSED = DONE_STAGES + ("absorbed",)\n',
           "CARRY_CLOSED = DONE_STAGES  # L4\n"),
    "L5": (LIB, '    return ("carries-open" if pending else "done"), pending\n',
           '    return "done", pending  # L5\n'),
    "L6": (LIB, r'_CARRY_MARK = re.compile(r" \[(implemented|moved|dismissed): ([^\]\n]+)\]\Z")',
           r'_CARRY_MARK = re.compile(r" \[(implemented|moved|dismissed): ([^\]\n]+)\]")'),
    "Y1": (SYNC, '        closed, _ = roster_lib.closing_stage(g, "done", legacy or {})\n',
           '        closed = "done"  # Y1\n'),
    "R1": (AUDIT, "        elif not any(live for _, live in by):\n",
           "        elif False:  # R1\n"),
    "R2": (AUDIT, "        if not by:\n", "        if False:  # R2\n"),
    "R3": (AUDIT, "    for n in sorted(open_issues - {LOG_ISSUE}):\n",
           "    for n in sorted(open_issues):  # R3\n"),
    "R4": (AUDIT, '        where = f"absorbed into {into}" if stage == "absorbed" and into else stage\n',
           "        where = stage  # R4\n"),
    "R5": (AUDIT, '        elif isinstance(x, dict) and "pull_request" not in x and isinstance(x.get("number"), int):\n',
           '        elif isinstance(x, dict) and isinstance(x.get("number"), int):  # R5\n'),
}


def parts(name):
    """(target, old, new) of a plant: roster_edit.py unless the plant names
    its file. Every target is a Python tool whose `--self-test` prints FAIL
    lines, so one driver reads them all."""
    plant = PLANTS[name]
    return plant if len(plant) == 3 else (TARGET,) + plant


def target_self_test(target=TARGET):
    r = subprocess.run([sys.executable, target, "--self-test"], cwd=ROOT,
                       capture_output=True, text=True)
    fails = [ln for ln in r.stdout.splitlines() if ln.startswith("FAIL ")]
    return r.returncode, fails, (r.stdout + r.stderr).strip().splitlines()[-3:]


def report(name, rc, fails, tail):
    print(f"RESULT mutant={name} rc={rc} fails={len(fails)}")
    for f in fails:
        print("   ", re.sub(r" \(got: .*\)$", "", f))
    if rc and not fails:
        print("    crash tail:", *tail, sep="\n      ")


def select(names):
    """The plants a run names, and any name the table does not hold."""
    chosen = names or list(PLANTS)
    return chosen, [n for n in chosen if n not in PLANTS]


def self_test():
    passed = failed = 0

    def ck(name, ok):
        nonlocal passed, failed
        passed, failed = passed + ok, failed + (not ok)
        print(f"  {'ok  ' if ok else 'FAIL'} {name}")

    for name in PLANTS:
        target, old, new = parts(name)
        text = (ROOT / target).read_text()
        ck(f"{name}: anchor occurs once in {target}", text.count(old) == 1)
        ck(f"{name}: the plant changes the text", new != old)
        try:
            compile(text.replace(old, new), target, "exec")
            ok = True
        except SyntaxError:
            ok = False
        ck(f"{name}: the mutant parses", ok)

    def rendered(rc, fails, tail):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            report("X", rc, fails, tail)
        return out.getvalue().splitlines()

    ck("a killed plant prints its tally and drops the (got:) suffix",
       rendered(1, ["FAIL a (got: 2)"], [])
       == ["RESULT mutant=X rc=1 fails=1", "    FAIL a"])
    ck("a crash with no FAIL line prints its tail",
       rendered(1, [], ["Traceback", "boom"])
       == ["RESULT mutant=X rc=1 fails=0", "    crash tail:",
           "      Traceback", "      boom"])
    ck("a survivor prints fails=0 and no tail",
       rendered(0, [], ["x"]) == ["RESULT mutant=X rc=0 fails=0"])
    ck("no names selects every plant", select([]) == (list(PLANTS), []))
    ck("a named plant is kept", select(["A1"]) == (["A1"], []))
    ck("an unknown plant is returned for refusal",
       select(["ZZ"]) == (["ZZ"], ["ZZ"]))

    print(f"r10_roster_ops_mutants self-test: {passed + failed} checks, "
          f"{failed} failed")
    return 1 if failed else 0


def main(argv):
    if argv == ["--self-test"]:
        return self_test()
    targets = sorted({parts(n)[0] for n in PLANTS})
    if subprocess.run(["git", "diff", "--quiet", "HEAD", "--", *targets],
                      cwd=ROOT).returncode != 0:
        print(f"refusing: one of {targets} differs from HEAD", file=sys.stderr)
        return 2
    if argv == ["--null"]:
        for target in targets:
            report(f"null {target}", *target_self_test(target))
        return 0
    names, unknown = select(argv)
    if unknown:
        print(f"unknown plant(s): {unknown}", file=sys.stderr)
        return 2
    originals = {t: (ROOT / t).read_bytes() for t in targets}
    survivors = []
    try:
        for name in names:
            target, old, new = parts(name)
            path, original = ROOT / target, originals[target]
            text = original.decode("utf-8")
            if text.count(old) != 1:
                print(f"plant {name}: anchor occurs {text.count(old)} times",
                      file=sys.stderr)
                return 2
            path.write_bytes(text.replace(old, new).encode("utf-8"))
            rc, fails, tail = target_self_test(target)
            path.write_bytes(original)
            report(name, rc, fails, tail)
            if not fails:
                survivors.append(name)
    finally:
        for target, original in originals.items():
            (ROOT / target).write_bytes(original)
    print(f"plants: {len(names)}, without a FAIL line: {survivors or 'none'}")
    return 1 if survivors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
