#!/usr/bin/env python3
"""The repository layout barrier (R9-RO-1): every tracked path in its place.

tests/layout.json is the TARGET tree of the reorganisation (lane RO): ordered
categories of globs, the `retired` paths the lane moves out of the way, and the
`historical` prefixes whose text keeps the paths that were true when it was
written (tvofi's D2). Four arms, each counted separately:

  category    every `git ls-files` path matches exactly one category glob
  retired     no tracked path sits at a retired `old` path
  reference   no live text file cites a retired `old` path as a path token --
              which a basename fallback (brief_lint's lookupPath) never sees
  dead        every category glob and every retired entry still matches a
              tracked file, and every retired target lands in one category:
              a glob that matches nothing is a check that measures nothing

    python3 tests/layout.py               # report on this tree, then --self-test
    python3 tests/layout.py --report      # per-arm counts; exit 0 whatever they are
    python3 tests/layout.py --enforce     # exit 1 on any finding (R9-RO-9 flips to this)
    python3 tests/layout.py --self-test   # the null controls below, in a throwaway repo
    python3 tests/layout.py --verbose     # every finding, not the first few per arm
    python3 tests/layout.py --gen-retired INVENTORY.tsv   # print the `retired` list

REPORT MODE IS THE DEFAULT until R9-RO-9: on today's tree the counts are the
distance to the target, and each RO pull request shows its step on that meter.

It is run_always in tests/run.sh: a pure `git mv` is scoped only by its
destination, so a scoped run would never select this script for the change it
exists to see.

It reads the INDEX, never the worktree: paths come from `git ls-files` and file
text from `git grep --cached`. That keeps its recorded closure to the manifest
and itself (the closure recorder drops `.git/`), so the INERT prose it reads is
not a dependency `closure.py merge` would refuse. A seat checking unstaged edits
stages them first.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MANIFEST = "tests/layout.json"
ARMS = ("category", "retired", "reference", "dead")
SHOWN = 10  # findings printed per arm without --verbose


def glob_re(glob: str) -> re.Pattern[str]:
    """`**` crosses directories, `*` and `?` do not, `{a,b}` alternates."""
    out, i = "", 0
    while i < len(glob):
        c = glob[i]
        if glob.startswith("**", i):
            out += ".*"
            i += 2
        elif c == "*":
            out += "[^/]*"
            i += 1
        elif c == "?":
            out += "[^/]"
            i += 1
        elif c == "{":
            j = glob.index("}", i)
            out += "(?:" + "|".join(re.escape(a) for a in glob[i + 1:j].split(",")) + ")"
            i = j + 1
        else:
            out += re.escape(c)
            i += 1
    return re.compile(out + r"\Z")


def ref_re(old: str) -> re.Pattern[str]:
    """`old` as a path token: not the tail of a longer name, and not the head
    of one (`round5/` is not cited by `round5-fix/`, `docs/setup/` not by
    `docs/setup.md`). A directory entry is cited with or without its slash."""
    head = r"(?<![\w.-])"
    if old.endswith("/"):
        return re.compile(head + re.escape(old[:-1]) + r"(?=/|\.(?!\w)|[^\w./-]|\Z)")
    return re.compile(head + re.escape(old) + r"(?![\w/-]|\.\w)")


def under(path: str, entry: str) -> bool:
    return path.startswith(entry) if entry.endswith("/") else path == entry


def load(root: Path) -> dict:
    return json.loads((root / MANIFEST).read_text())


def git(root: Path, *args: str) -> bytes:
    return subprocess.run(["git", *args], cwd=root, check=True,
                          capture_output=True).stdout


def tracked(root: Path) -> list[str]:
    return [p for p in git(root, "ls-files", "-z").decode().split("\0") if p]


def categories_of(path: str, cats: list[tuple[str, list]]) -> list[str]:
    return [name for name, res in cats if any(r.match(path) for r in res)]


def target(path: str, retired: list[dict]) -> str | None:
    """Where the move map puts `path`: itself, a new path, or None (deleted)."""
    for r in retired:
        if under(path, r["old"]):
            if r["new"] is None:
                return None
            return r["new"] + path[len(r["old"]):] if r["old"].endswith("/") else r["new"]
    return path


def check(root: Path, manifest: dict) -> tuple[dict[str, list[str]], int]:
    """Per-arm findings for the index at `root`, and how many paths it read."""
    cats = compiled(manifest)
    retired, hist = manifest["retired"], manifest["historical"]
    globs = {c["name"]: c["globs"] for c in manifest["categories"]}
    files = tracked(root)
    found: dict[str, list[str]] = {a: [] for a in ARMS}

    hits: dict[tuple[str, str], int] = {}
    for p in files:
        names = categories_of(p, cats)
        if not names:
            found["category"].append(f"outside the allowed categories: {p}")
        elif len(names) > 1:
            found["category"].append(f"in {len(names)} categories ({', '.join(names)}): {p}")
        for name, res in cats:
            for g, r in zip(globs[name], res):
                if r.match(p):
                    hits[(name, g)] = hits.get((name, g), 0) + 1

    for r in retired:
        new = r["new"] or "nothing (deleted)"
        for p in files:
            if not under(p, r["old"]):
                continue
            if r.get("since"):
                found["retired"].append(f"reintroduces moved path {p}; it lives at {new} since {r['since']}")
            else:
                found["retired"].append(f"planned move not yet made: {p} -> {target(p, retired) or new}")

    def historical(p: str) -> bool:
        t = target(p, retired)
        return p == MANIFEST or any(x is not None and x.startswith(h) for x in (p, t) for h in hist)

    if retired:
        pats = "\n".join(r["old"].rstrip("/") for r in retired) + "\n"
        with tempfile.NamedTemporaryFile("w", suffix=".pat", delete=False) as fh:
            fh.write(pats)
        try:
            # Historical text is filtered below anyway; leaving it out of the
            # grep is what keeps the arm to seconds (round evidence is most bytes).
            skip = [MANIFEST, *hist, *(r["old"] for r in retired
                                       if r["new"] and any(r["new"].startswith(h) for h in hist))]
            proc = subprocess.run(["git", "grep", "--cached", "-z", "-n", "-I", "-F", "-f", fh.name,
                                   "--", ".", *(f":(exclude,literal){x}" for x in skip)],
                                  cwd=root, capture_output=True)
        finally:
            Path(fh.name).unlink()
        if proc.returncode not in (0, 1):
            raise SystemExit(f"layout: git grep failed: {proc.stderr.decode()}")
        res = [(r, ref_re(r["old"])) for r in retired]
        for rec in proc.stdout.decode(errors="replace").splitlines():
            path, line, text = rec.split("\0", 2)
            if historical(path):
                continue
            for r, rx in res:
                if rx.search(text):
                    use = f"use {r['new']}" if r["new"] else "it is deleted"
                    found["reference"].append(f"{path}:{line} cites retired path {r['old']}; {use}")

    for name, gs in globs.items():
        for g in gs:
            if not hits.get((name, g)):
                found["dead"].append(f"category {name}: glob matches no tracked file: {g}")
    for r in retired:
        if r["new"] is None:
            continue  # a deletion is live as a refusal; nothing can match it
        olds = [p for p in files if under(p, r["old"])]
        news = [p for p in files if under(p, r["new"])]
        if not olds and not news:
            found["dead"].append(f"retired entry matches nothing at either end: {r['old']} -> {r['new']}")
        for p in olds:
            t = target(p, retired)
            if len(categories_of(t, cats)) != 1:
                found["dead"].append(f"retired target is in {len(categories_of(t, cats))} categories: {p} -> {t}")
    return found, len(files)


def report(found: dict[str, list[str]], n: int, verbose: bool) -> None:
    print(f"layout: {n} tracked path(s) enumerated")
    for arm in ARMS:
        items = found[arm]
        print(f"  {arm:<9} {len(items)} finding(s)")
        for msg in items if verbose else items[:SHOWN]:
            print(f"    {msg}")
        if not verbose and len(items) > SHOWN:
            print(f"    ... {len(items) - SHOWN} more (--verbose)")


# ---------------------------------------------------------------------------
# the null controls


def instance(glob: str) -> str:
    """One concrete path a glob matches."""
    s = re.sub(r"\{([^,}]*)[^}]*\}", r"\1", glob)
    return s.replace("**", "x").replace("*", "x").replace("?", "x")


def self_test(root: Path) -> int:
    """Build a throwaway repo from the real manifest in which every arm is
    empty, then plant one red case per arm and the negative controls, each on
    its own copy. Every case names the vector of arm counts it must produce, so
    a planted case that lights the wrong arm fails as surely as one that lights
    none. The planted paths are drawn from the manifest, never written here,
    or this file would be a live citation of what it retires."""
    manifest = load(root)
    retired = manifest["retired"]
    real = tracked(root)
    files: set[str] = {MANIFEST}
    for c in manifest["categories"]:
        files.update(instance(g) for g in c["globs"])
    for r in retired:
        if r["new"] is None:
            continue
        olds = [p for p in real if under(p, r["old"])] or [p for p in real if under(p, r["new"])]
        if olds and r["old"].endswith("/"):
            files.add(target(olds[0], retired) or "")
        else:
            files.add(r["new"] + ("x" if r["new"].endswith("/") else ""))
    files.discard("")
    moved = next(r for r in retired if r["new"] and not r["old"].endswith("/"))
    moved_dir = next(r for r in retired if r["new"] and r["old"].endswith("/"))
    user_doc = instance(next(c for c in manifest["categories"] if c["name"] == "docs")["globs"][0])
    cite = f"see `{moved['old']}` for the details\n"
    extra_cat = {"name": "nothere", "globs": ["nothere/**"], "why": "planted"}
    twin = {"name": "twin", "globs": [user_doc], "why": "planted"}

    cases = [
        # (name, files to add {path: text}, manifest edit, expected counts)
        ("base tree", {}, None, (0, 0, 0, 0)),
        ("file outside every category", {"docs/notes/x.md": ""}, None, (1, 0, 0, 0)),
        ("path in two categories", {}, lambda m: m["categories"].append(twin), (1, 0, 0, 0)),
        ("retired file re-added", {moved["old"]: ""}, None,
         (0 if _admitted(moved["old"], manifest) else 1, 1, 0, 0)),
        ("live citation of a retired path", {user_doc: cite}, None, (0, 0, 1, 0)),
        ("live citation of a retired directory, no slash", {user_doc: f"under {moved_dir['old'][:-1]} now\n"}, None,
         (0, 0, 1, 0)),
        ("dead category glob", {}, lambda m: m["categories"].append(extra_cat), (0, 0, 0, 1)),
        ("negative: the citation under the archive", {"dev/archive/x.md": cite}, None, (0, 0, 0, 0)),
        ("negative: the citation in a delivery row", {"dev/programme/delivery/9999.md": cite}, None, (0, 0, 0, 0)),
        ("negative: a longer name that contains it", {user_doc: f"see `{moved['old']}x` and `x{moved['old']}`\n"},
         None, (0, 0, 0, 0)),
        ("negative: the new path cited", {user_doc: f"see `{moved['new']}`\n"}, None, (0, 0, 0, 0)),
    ]
    failed = 0
    for name, add, edit, want in cases:
        tmp = Path(tempfile.mkdtemp(prefix="hpo-layout-"))
        try:
            m = json.loads(json.dumps(manifest))
            if edit:
                edit(m)
            for p in sorted(files | set(add)):
                f = tmp / p
                f.parent.mkdir(parents=True, exist_ok=True)
                f.write_text(add.get(p, ""))
            (tmp / MANIFEST).write_text(json.dumps(m, indent=1))
            subprocess.run(["git", "init", "-q"], cwd=tmp, check=True)
            subprocess.run(["git", "add", "-A"], cwd=tmp, check=True)
            found, n = check(tmp, m)
            got = tuple(len(found[a]) for a in ARMS)
            listed = len(tracked(tmp))
            ok = got == want and n == listed and n >= len(files)
            print(f"  {'ok  ' if ok else 'FAIL'} self-test: {name}: counts {got}, want {want}; "
                  f"enumerated {n} of {listed} listed")
            if not ok:
                failed += 1
                for arm in ARMS:
                    for msg in found[arm][:5]:
                        print(f"         {arm}: {msg}")
        finally:
            shutil.rmtree(tmp)
    return failed


def compiled(manifest: dict) -> list[tuple[str, list[re.Pattern[str]]]]:
    return [(c["name"], [glob_re(g) for g in c["globs"]]) for c in manifest["categories"]]


def _admitted(path: str, manifest: dict) -> bool:
    return len(categories_of(path, compiled(manifest))) == 1


# ---------------------------------------------------------------------------
# the retired list, generated from the move map


def gen_retired(inventory: Path, root: Path) -> list[dict]:
    """One entry per maximal directory the move map moves whole (every row
    under it moves by the same prefix rewrite and nothing under it stays),
    otherwise one per file. A path the target categories still admit is not
    retired (.claude/rules/ stays, generated: tvofi's D1). `since` is carried
    over from the current manifest, so regenerating never forgets a landed move."""
    manifest = load(root)
    since = {r["old"]: r.get("since") for r in manifest.get("retired", [])}
    rows = list(csv.DictReader(inventory.open(), delimiter="\t"))
    stays = {r["path"] for r in rows if r["action"] == "keep"}
    stays |= {p for p in tracked(root) if _admitted(p, manifest)}
    moves = {}
    for r in rows:
        if r["action"] == "keep" or _admitted(r["path"], manifest):
            continue
        new = r["new_path"].split(" + ")[0].strip() or None
        moves[r["path"]] = None if r["action"] == "delete" else new

    def whole(d: str) -> str | None | bool:
        """The new prefix if directory `d` moves whole, else False."""
        if any(p.startswith(d) for p in stays):
            return False
        prefixes = set()
        for p, new in moves.items():
            if p.startswith(d):
                if new is None or not new.endswith(p[len(d):]):
                    return False
                prefixes.add(new[: len(new) - len(p) + len(d)])
        return prefixes.pop() if len(prefixes) == 1 else False

    out: list[dict] = []

    def walk(d: str) -> None:
        mine = sorted(p for p in moves if p.startswith(d))
        subdirs = sorted({d + p[len(d):].split("/")[0] + "/" for p in mine if "/" in p[len(d):]})
        for p in mine:
            if "/" not in p[len(d):]:
                out.append({"old": p, "new": moves[p], "since": since.get(p)})
        for s in subdirs:
            new = whole(s)
            if new:
                out.append({"old": s, "new": new, "since": since.get(s)})
            else:
                walk(s)

    walk("")
    return sorted(out, key=lambda r: r["old"])


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--report", action="store_true")
    ap.add_argument("--enforce", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--verbose", action="store_true")
    ap.add_argument("--gen-retired", metavar="INVENTORY")
    a = ap.parse_args()
    if a.gen_retired:
        print(json.dumps(gen_retired(Path(a.gen_retired), ROOT), indent=1))
        return 0
    rc = 0
    run_all = not (a.report or a.enforce or a.self_test)
    if a.report or a.enforce or run_all:
        found, n = check(ROOT, load(ROOT))
        report(found, n, a.verbose)
        listed = len(tracked(ROOT))
        if n != listed:
            print(f"FAIL: enumerated {n} path(s) but git ls-files lists {listed}")
            rc = 1
        if a.enforce and any(found.values()):
            rc = 1
        print(f"layout: MODE: {'ENFORCE' if a.enforce else 'REPORT (exit 0 on findings until R9-RO-9)'}")
    if a.self_test or run_all:
        failed = self_test(ROOT)
        print(f"layout self-test: {'ok' if not failed else f'{failed} case(s) FAILED'}")
        rc = rc or (1 if failed else 0)
    return rc


if __name__ == "__main__":
    sys.exit(main())
