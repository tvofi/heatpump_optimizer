#!/usr/bin/env python3
"""Git merge driver for the three measured JSON ledgers, merged key by key.

    python3 tools/merge/ledger_merge.py --install     once per clone
    python3 tools/merge/ledger_merge.py --self-test
    python3 tools/merge/ledger_merge.py --replay 2026-09-10   the evidence below

Every fix pull request re-records ``tests/mutation_budgets.json``,
``tests/structure_budgets.json`` and ``tests/closures.json``, so any two
branches in flight collide there in a line merge even when they recorded
different keys. ``--replay`` re-runs every branch-side merge since a date
twice, without and with this driver, and counts the ledger conflicts; from
2026-09-10 to 2026-09-24 that is 48 without it and 3 with it, and on every
merge there that the plain text merge resolved cleanly the driver writes the
same bytes. Until #1577 keys the mutation ledger by content, a merge that
shifts code still leaves line-keyed dispositions to re-key by hand; the driver
removes the conflict, not that work.

The driver parses base, ours and theirs and merges three ways per key:

  * a key one side changed takes that side; a key both sides changed to the
    same value takes it;
  * a dict both sides changed recurses while it is a table (the top level and
    the maps under it: ``survivor_triage``, ``killed_by``, ``closures``,
    ``recorded``). One level down it is a record -- a disposition, one
    script's timing -- and a record both sides rewrote differently refuses,
    because a field-wise mix of two verdicts is neither. Two exceptions: a
    record carrying an ``at`` timestamp (``last_measured.*``) is one
    measurement, so the later ``at`` wins whole; and a record of numbers only
    (``recorded.*``: seconds, rc) merges field by field under the number rule;
  * a list of strings both sides changed is merged as a set (the closures and
    ``survivor_lines``): base, plus what either side added, less what either
    removed;
  * a number both sides changed: in ``structure_budgets.json`` and
    ``mutation_budgets.json`` it is a count, so it takes base plus both deltas;
    in ``closures.json`` it sits under ``recorded`` (seconds, rc), which no
    check reads for a decision, so it takes the larger;
  * ``recorded_at`` both sides changed takes whichever SHA descends from the
    other.

Anything else both sides changed differently REFUSES, and so does a file
whose bytes do not round-trip through the formatter its writer uses (a hand
edit, a new format). A refusal hands the file to git's own text merge: a clean
one stands, and otherwise the file keeps git's ordinary conflict markers and
the driver exits 1 -- exactly what a clone without the driver gets.

A resolved ledger is a merge of two measurements, not a measurement. Every
number it writes is re-checked by the gate that owns the file -- a sum of
deltas that is wrong for a non-additive metric fails ``tests/structure.py``
one way or the other, and a stale closure is ``UNDER-SCOPED`` -- so the driver
can be wrong only loudly. It prints each key it merged numerically so the seat
knows what to re-run.

GitHub never runs a merge driver, so a pull request still shows ``DIRTY``
until main is merged locally (``claim-files.md``, #570). What this removes is
the hand resolution once it is.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile

DRIVER_NAME = "ledgermerge"
#: Path -> how a number both sides changed is merged.
LEDGERS = {
    "tests/mutation_budgets.json": "sum",
    "tests/structure_budgets.json": "sum",
    "tests/closures.json": "max",
}
#: The ``json.dumps`` shapes the three writers use (mutation_table.py indent 2;
#: structure.py indent 1 sorted; closure.py indent 1). A file that is not
#: byte-identical under one of them (raw or escaped non-ASCII aside) is
#: refused, never reformatted.
FORMATS = (
    {"indent": 1, "sort_keys": True},
    {"indent": 1},
    {"indent": 2},
)
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class Refuse(Exception):
    """Both sides changed ``path`` in a way this driver will not choose."""


_ABSENT = object()


def _is_str_list(v) -> bool:
    return isinstance(v, list) and all(isinstance(x, str) for x in v) and len(set(v)) == len(v)


def _is_num(v) -> bool:
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def _descends(a: str, b: str, repo: str) -> bool:
    """Whether commit ``b`` is an ancestor of ``a`` (``a`` is the newer)."""
    return subprocess.run(
        ["git", "merge-base", "--is-ancestor", b, a], cwd=repo,
        capture_output=True,
    ).returncode == 0


def _key_order(ours: dict, theirs: dict) -> list:
    """Ours' keys, with each key only theirs has placed after its predecessor
    in theirs -- where a text merge would have put it. Sorted when both sides
    are (the #1577 ledger keeps its maps in key order)."""
    keys = list(ours)
    if keys == sorted(keys) and list(theirs) == sorted(theirs):
        return sorted(set(keys) | set(theirs))
    prev = None
    for k in theirs:
        if k not in keys:
            keys.insert(keys.index(prev) + 1 if prev in keys else 0, k)
        prev = k
    return keys


def merge3(base, ours, theirs, *, numbers: str, path: str = "",
           repo: str = ROOT, notes: list | None = None, depth: int = 0):
    """Three-way merge of parsed JSON values; raises ``Refuse``."""
    notes = notes if notes is not None else []
    if ours == theirs:
        return ours
    if ours == base:
        return theirs
    if theirs == base:
        return ours
    where = path or "<root>"
    if isinstance(ours, dict) and isinstance(theirs, dict):
        if "at" in ours and "at" in theirs:
            if not (isinstance(ours["at"], str) and isinstance(theirs["at"], str)):
                raise Refuse(f"{where}: 'at' is not a timestamp on both sides")
            notes.append(f"{where}: kept the later measurement")
            return ours if ours["at"] >= theirs["at"] else theirs
        numeric = all(_is_num(v) for v in list(ours.values()) + list(theirs.values()))
        if depth >= 2 and not numeric:
            raise Refuse(f"{where}: both sides rewrote this record differently")
        b = base if isinstance(base, dict) else {}
        out = {}
        for k in _key_order(ours, theirs):
            v = merge3(b.get(k, _ABSENT), ours.get(k, _ABSENT), theirs.get(k, _ABSENT),
                       numbers=numbers, path=f"{path}.{k}" if path else k,
                       repo=repo, notes=notes, depth=depth + 1)
            if v is not _ABSENT:
                out[k] = v
        return out
    if _is_str_list(ours) and _is_str_list(theirs):
        b = base if _is_str_list(base) else []
        gone = (set(b) - set(ours)) | (set(b) - set(theirs))
        out = [x for x in ours if x not in gone]
        out += [x for x in theirs if x not in gone and x not in set(ours)]
        if ours == sorted(ours) and theirs == sorted(theirs):
            out.sort()
        notes.append(f"{where}: merged as a set ({len(out)} entries)")
        return out
    if _is_num(ours) and _is_num(theirs):
        if numbers == "max":
            notes.append(f"{where}: took the larger of {ours} and {theirs}")
            return max(ours, theirs)
        if _is_num(base):
            got = base + (ours - base) + (theirs - base)
            notes.append(f"{where}: {base} + both deltas = {got}")
            return got
        raise Refuse(f"{where}: both sides added a different number")
    if path.rsplit(".", 1)[-1] == "recorded_at" and isinstance(ours, str) and isinstance(theirs, str):
        if _descends(ours, theirs, repo):
            return ours
        if _descends(theirs, ours, repo):
            return theirs
        raise Refuse(f"{where}: neither SHA descends from the other")
    raise Refuse(f"{where}: both sides changed it differently")


def _format(text: str):
    """The FORMATS entry ``text`` round-trips under, or None."""
    try:
        value = json.loads(text)
    except ValueError:
        return None
    for fmt in FORMATS:
        # A hand edit that pasted a raw non-ASCII character is the same JSON
        # in the same shape; the merge writes it back escaped, as the writer
        # would (14 of the 16 historical ledger refusals were only this).
        for ascii_only in (True, False):
            if json.dumps(value, ensure_ascii=ascii_only, **fmt) + "\n" == text:
                return fmt
    return None


def merge_text(base: str, ours: str, theirs: str, numbers: str,
               repo: str = ROOT, notes: list | None = None) -> str:
    """Merged file text, or raise ``Refuse``."""
    fmt = _format(ours)
    if fmt is None or _format(theirs) != fmt:
        raise Refuse("a side is not in its writer's own JSON format")
    try:
        b = json.loads(base) if base.strip() else {}
    except ValueError:
        raise Refuse("the merge base is not JSON")
    merged = merge3(b, json.loads(ours), json.loads(theirs),
                    numbers=numbers, repo=repo, notes=notes)
    return json.dumps(merged, **fmt) + "\n"


def run_driver(base_path: str, ours_path: str, theirs_path: str,
               marker_size: str = "7", pathname: str = "") -> int:
    """git merge driver: resolve into ``ours_path``, or leave a conflict there."""
    label = pathname or ours_path
    with open(base_path) as f:
        base = f.read()
    with open(ours_path) as f:
        ours = f.read()
    with open(theirs_path) as f:
        theirs = f.read()
    notes: list = []
    try:
        merged = merge_text(base, ours, theirs, LEDGERS.get(pathname, "sum"), notes=notes)
    except Refuse as why:
        # Fall back to git's own text merge, so the driver is never worse than
        # no driver: a merge the text merge resolves stays resolved.
        text = subprocess.run(
            ["git", "merge-file", f"--marker-size={marker_size}",
             "-L", f"{label} (this branch)", "-L", f"{label} (merge base)",
             "-L", f"{label} (incoming)", ours_path, base_path, theirs_path],
            capture_output=True,
        )
        if text.returncode == 0:
            print(f"LEDGER-MERGE: {label}: text merge ({why})", file=sys.stderr)
            return 0
        print(f"LEDGER-MERGE: refused {label}: {why}", file=sys.stderr)
        return 1
    with open(ours_path, "w") as f:
        f.write(merged)
    with open(ours_path) as f:
        if f.read() != merged:
            print(f"LEDGER-MERGE: refused {label}: WRITE NOT VERIFIED", file=sys.stderr)
            return 1
    print(f"LEDGER-MERGE: resolved {label}", file=sys.stderr)
    for n in notes:
        print(f"  {n}", file=sys.stderr)
    if notes:
        print("  re-run the gate that owns this file before pushing", file=sys.stderr)
    return 0


def gitattributes_error(repo: str = ROOT, text: str | None = None) -> str | None:
    """Why ``.gitattributes`` does not route every ledger here, or None."""
    if text is None:
        path = os.path.join(repo, ".gitattributes")
        text = open(path).read() if os.path.exists(path) else ""
    routed = {line.split()[0] for line in text.splitlines()
              if line.strip() and not line.lstrip().startswith("#")
              and f"merge={DRIVER_NAME}" in line.split()[1:]}
    missing = sorted(set(LEDGERS) - routed)
    if not missing:
        return None
    return ("UNROUTED LEDGER: .gitattributes does not send "
            + ", ".join(missing) + f" to merge={DRIVER_NAME}")


def install(repo: str = ROOT) -> str:
    """Configure the driver in ``repo``'s git config and read it back."""
    want = {
        f"merge.{DRIVER_NAME}.name": "merge measured JSON ledgers key by key",
        f"merge.{DRIVER_NAME}.driver":
            "python3 tools/merge/ledger_merge.py --merge %O %A %B %L %P",
    }
    already = True
    for key, value in want.items():
        got = subprocess.run(["git", "config", "--get", key], cwd=repo,
                             capture_output=True, text=True).stdout.strip()
        if got != value:
            already = False
            subprocess.run(["git", "config", key, value], cwd=repo, check=True)
    for key, value in want.items():
        got = subprocess.run(["git", "config", "--get", key], cwd=repo,
                             capture_output=True, text=True).stdout.strip()
        if got != value:
            raise RuntimeError(f"{key} reads {got!r} after install; NOT installed")
    return "already-installed" if already else "installed"


def _dump(value, fmt=FORMATS[1]) -> str:
    return json.dumps(value, **fmt) + "\n"


def self_test() -> int:
    ok = True

    def check(name: str, cond: bool) -> None:
        nonlocal ok
        ok &= bool(cond)
        print(f"  {'ok  ' if cond else 'FAIL'} {name}")

    def refused(fn) -> bool:
        try:
            fn()
        except Refuse:
            return True
        return False

    # closures.json, in the shape the replay found: two branches re-recorded
    # different scripts, and both re-timed one they share.
    base = {"_comment": "c", "recorded": {"a": {"seconds": 1.0, "rc": 0},
                                          "b": {"seconds": 2.0, "rc": 0}},
            "closures": {"a": ["x", "y"], "b": ["y"]}}
    ours = json.loads(json.dumps(base))
    theirs = json.loads(json.dumps(base))
    ours["recorded"]["a"]["seconds"] = 21.1
    theirs["recorded"]["a"]["seconds"] = 27.2
    ours["closures"]["a"] = ["w", "x", "y"]
    theirs["closures"]["a"] = ["x"]
    theirs["closures"]["b"] = ["y", "z"]
    got = json.loads(merge_text(_dump(base), _dump(ours), _dump(theirs), "max"))
    check("closures: a timing both sides re-took no longer conflicts",
          got["recorded"]["a"]["seconds"] == 27.2)
    check("closures: an addition on one side and a removal on the other both land",
          got["closures"]["a"] == ["w", "x"])
    check("closures: a key only one side changed takes that side",
          got["closures"]["b"] == ["y", "z"])

    # structure_budgets.json: both sides re-recorded, so every count and
    # recorded_at differ. Counts take base plus both deltas.
    sb = {"coordinator_loc": 9150, "dead_methods": 0, "recorded_at": "A"}
    so = dict(sb, coordinator_loc=9170, recorded_at="B")
    st = dict(sb, coordinator_loc=9050, dead_methods=0, recorded_at="C")
    fmt = FORMATS[0]
    try:
        merge_text(_dump(sb, fmt), _dump(so, fmt), _dump(st, fmt), "sum", repo=ROOT)
        unrelated_refused = False
    except Refuse as why:
        unrelated_refused = "recorded_at" in str(why)
    check("structure: a recorded_at pair with no ancestry is refused",
          unrelated_refused)
    with tempfile.TemporaryDirectory() as tmp:
        def git(*a):
            return subprocess.run(["git", *a], cwd=tmp, check=True, capture_output=True,
                                  text=True, env=dict(os.environ, GIT_AUTHOR_NAME="t",
                                                      GIT_AUTHOR_EMAIL="t@t", GIT_COMMITTER_NAME="t",
                                                      GIT_COMMITTER_EMAIL="t@t")).stdout.strip()
        git("init", "-q")
        git("commit", "-q", "--allow-empty", "-m", "old")
        old = git("rev-parse", "HEAD")
        git("commit", "-q", "--allow-empty", "-m", "new")
        new = git("rev-parse", "HEAD")
        so["recorded_at"], st["recorded_at"] = old, new
        got = json.loads(merge_text(_dump(sb, fmt), _dump(so, fmt), _dump(st, fmt),
                                    "sum", repo=tmp))
        check("structure: recorded_at takes the descendant SHA", got["recorded_at"] == new)
        check("structure: a count both sides moved takes base plus both deltas",
              got["coordinator_loc"] == 9070)

    # mutation_budgets.json: disjoint dispositions, one shared measurement.
    mb = {"survivor_triage": {"k1": {"verdict": "equivalent"}},
          "last_measured": {"full": {"at": "2026-09-18", "survivors": 12,
                                     "survivor_lines": ["p"]}}}
    mo = json.loads(json.dumps(mb))
    mt = json.loads(json.dumps(mb))
    mo["survivor_triage"]["k0"] = {"verdict": "equivalent"}
    mt["survivor_triage"]["k2"] = {"verdict": "killed"}
    mo["last_measured"]["full"] = {"at": "2026-09-20", "survivors": 10, "survivor_lines": ["q"]}
    mt["last_measured"]["full"] = {"at": "2026-09-19", "survivors": 11, "survivor_lines": ["r"]}
    got = json.loads(merge_text(_dump(mb, FORMATS[2]), _dump(mo, FORMATS[2]),
                                _dump(mt, FORMATS[2]), "sum"))
    check("mutation: dispositions both sides added all land",
          set(got["survivor_triage"]) == {"k0", "k1", "k2"})
    check("mutation: a measurement both sides re-took keeps the later one whole",
          got["last_measured"]["full"]["survivors"] == 10
          and got["last_measured"]["full"]["survivor_lines"] == ["q"])

    # An unsorted map (the pre-#1577 ledger): a key only theirs added lands
    # after its predecessor in theirs, where a text merge would put it
    # (merge 75231a63 was the one clean merge the first version reordered).
    ub = {"z": 1, "a": 1}
    got = merge_text(_dump(ub), _dump({"z": 1, "a": 1, "m": 1}),
                     _dump({"z": 1, "n": 1, "a": 1}), "sum")
    check("an unsorted map places a new key where the text merge would",
          list(json.loads(got)) == ["z", "n", "a", "m"])

    # Refusals: the ones that make the driver safe to route real files to.
    mo2 = json.loads(json.dumps(mb))
    mt2 = json.loads(json.dumps(mb))
    mo2["survivor_triage"]["k1"] = {"verdict": "equivalent", "reason": "one"}
    mt2["survivor_triage"]["k1"] = {"verdict": "killed"}
    check("refuses: one disposition both sides rewrote differently",
          refused(lambda: merge_text(_dump(mb, FORMATS[2]), _dump(mo2, FORMATS[2]),
                                     _dump(mt2, FORMATS[2]), "sum")))
    check("refuses: a side not in its writer's own format",
          refused(lambda: merge_text(_dump(mb), json.dumps(mo, indent=4) + "\n",
                                     _dump(mt), "sum")))
    raw = json.dumps(mo, indent=2, ensure_ascii=False).replace("equivalent", "équivalent", 1) + "\n"
    check("a side with a raw non-ASCII character is merged, not refused",
          not refused(lambda: merge_text(_dump(mb, FORMATS[2]), raw,
                                         _dump(mt, FORMATS[2]), "sum")))
    check("refuses: a side that is not JSON (conflict markers)",
          refused(lambda: merge_text(_dump(mb), "<<<<<<< ours\n", _dump(mt), "sum")))

    # The driver end to end, through the files git hands it.
    with tempfile.TemporaryDirectory() as tmp:
        paths = []
        for name, value in (("O", base), ("A", ours), ("B", theirs)):
            p = os.path.join(tmp, name)
            with open(p, "w") as f:
                f.write(_dump(value))
            paths.append(p)
        rc = run_driver(*paths, "7", "tests/closures.json")
        with open(paths[1]) as f:
            written = json.loads(f.read())
        check("driver: resolves into %A and exits 0",
              rc == 0 and written["closures"]["a"] == ["w", "x"])
        with open(paths[1], "w") as f:
            f.write(_dump(mo2, FORMATS[2]))
        with open(paths[2], "w") as f:
            f.write(_dump(mt2, FORMATS[2]))
        with open(paths[0], "w") as f:
            f.write(_dump(mb, FORMATS[2]))
        rc = run_driver(*paths, "7", "tests/mutation_budgets.json")
        with open(paths[1]) as f:
            left = f.read()
        check("driver: a refusal exits 1 and leaves conflict markers in %A",
              rc == 1 and "<<<<<<<" in left)

        # A refusal the plain text merge resolves stays resolved (a side in a
        # hand-edited format, changes far apart): never worse than no driver.
        wide = {f"k{i}": i for i in range(12)}
        for name, value in (("O", wide), ("A", dict(wide, k0=100)), ("B", dict(wide, k11=100))):
            with open(os.path.join(tmp, name), "w") as f:
                f.write(json.dumps(value, indent=4) + "\n")
        rc = run_driver(*paths, "7", "tests/closures.json")
        with open(paths[1]) as f:
            text_merged = json.loads(f.read())
        check("driver: a format refusal falls back to a clean text merge",
              rc == 0 and text_merged["k0"] == 100 and text_merged["k11"] == 100)

    check(".gitattributes routes all three ledgers to the driver",
          gitattributes_error() is None)
    check("a .gitattributes routing only one ledger is refused",
          (gitattributes_error(text=f"tests/closures.json merge={DRIVER_NAME}\n") or "")
          .startswith("UNROUTED LEDGER"))
    print(f"\n{'all passed' if ok else 'FAILED'}")
    return 0 if ok else 1


def replay(since: str, repo: str = ROOT) -> int:
    """Re-merge every non-PR merge commit since ``since``; count ledger conflicts.

    Each merge runs under its first parent's ``.gitattributes`` and then under
    this tree's. The driver must be installed; without it the two columns are
    equal.
    """
    def git(*a):
        return subprocess.run(["git", *a], cwd=repo, capture_output=True, text=True)
    log = git("log", "--all", "--merges", f"--since={since}", "--format=%H %P %s").stdout
    merges = [l.split(" ", 3) for l in log.splitlines()
              if l.split(" ", 3)[3:] and not l.split(" ", 3)[3].startswith("Merge pull request")]
    before = {f: 0 for f in LEDGERS}
    after = {f: 0 for f in LEDGERS}
    for h, p1, p2, _ in merges:
        # Without: the attributes the merge had (its first parent's, which
        # route no ledger here). With: this tree's.
        for counts, pre in ((before, [f"--attr-source={p1}"]), (after, ["--attr-source=HEAD"])):
            out = git(*pre, "merge-tree", "--write-tree", "--name-only",
                      "--no-messages", p1, p2).stdout.splitlines()[1:]
            for f in LEDGERS:
                counts[f] += f in out
    print(f"{len(merges)} branch-side merges since {since}")
    for f in LEDGERS:
        print(f"  {f}: {before[f]} conflicts without the driver, {after[f]} with it")
    return 0


def main(argv: list) -> int:
    if argv[:1] == ["--merge"] and len(argv) >= 4:
        rest = argv[1:]
        return run_driver(rest[0], rest[1], rest[2],
                          rest[3] if len(rest) > 3 else "7",
                          rest[4] if len(rest) > 4 else "")
    if argv[:1] == ["--install"]:
        print(f"LEDGER-MERGE: {install()}")
        problem = gitattributes_error()
        if problem:
            print(problem, file=sys.stderr)
            return 1
        return 0
    if argv[:1] == ["--replay"] and len(argv) == 2:
        return replay(argv[1])
    if argv[:1] == ["--self-test"]:
        return self_test()
    print(__doc__.split("\n\n")[1], file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
