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
    python3 tests/layout.py --guard [--base REF]  # the diff from the merge base only
    python3 tests/layout.py --stale       # every live line citing a landed move
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
import functools
import json
import os
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
    of one (`round5/` is not cited by `round5-fix/`, `a/b/` not by
    `a/b.md`). A directory entry is cited with or without its slash."""
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


def listed(root: Path) -> int:
    """`git ls-files | wc -l`, counted apart from `tracked` so the vacuity guard
    does not compare a reader with itself."""
    return len(git(root, "ls-files").splitlines())


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


# The reorganisation's dual-path lookup (R9-RO-2), the Python twin of
# counts.mjs's: a grader CI restores from the base reads the pull request's
# data where a move pull request put it. A file is read at its old path while
# it is there, else at its new one, so an unowned copy at a new path cannot
# shadow the file in use; a directory, moved whole, resolves new-first
# (`locate`). A path a listing returns is spelt old (`canon`).
# `lifted` is tvofi's D1: the rule sources move and the generated copy stays.
# R9-RO-9 removes both, once nothing reads an old path.
@functools.lru_cache(maxsize=None)
def moves(root: Path = ROOT) -> tuple[tuple[str, str], ...]:
    try:
        m = load(root)
    except (OSError, ValueError):
        return ()
    return tuple((e["old"], e["new"]) for e in m.get("retired", []) + m.get("lifted", []) if e.get("new"))


def _swap(p: str, a: str, b: str) -> str | None:
    if not a.endswith("/"):
        return b if p == a else None
    if p.startswith(a):
        return b + p[len(a):]
    return b[:-1] if p == a[:-1] else None


def canon(p: str, root: Path = ROOT) -> str:
    return next((q for o, n in moves(root) if (q := _swap(p, n, o)) is not None), p)


def locate(p: str, exists=None, root: Path = ROOT, is_file=None) -> str:
    """`p` while it is a file there, else its new path when `exists` (the
    worktree, by default) holds that, else `p`. `exists` alone is a listing,
    whose entries are files."""
    if (is_file or exists or (lambda x: (root / x).is_file()))(p):
        return p
    q = next((q for o, n in moves(root) if (q := _swap(p, o, n)) is not None), None)
    return q if q is not None and (exists or (lambda x: (root / x).exists()))(q) else p


def locate_self_test(root: Path) -> int:
    """`locate` on stub listings: a file is read at its old path beside a copy
    at its new one (#1886 review, round 1: a copy there shadowed a grown file),
    a moved file at its new path, and with neither the old path stays named."""
    m = load(root)
    old = next(r["old"] for r in m["retired"] if r["new"] and not r["old"].endswith("/"))
    new = target(old, m["retired"])
    cases = [({old, new}, old), ({new}, new), (set(), old)]
    failed = 0
    for have, want in cases:
        got = locate(old, have.__contains__, root)
        failed += got != want
        print(f"  {'ok  ' if got == want else 'FAIL'} locate {old} with {sorted(have) or 'neither'}: {got}")
    return failed


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

    if retired:
        pats = "\n".join(r["old"].rstrip("/") for r in retired) + "\n"
        with tempfile.NamedTemporaryFile("w", suffix=".pat", delete=False) as fh:
            fh.write(pats)
        try:
            # Historical text: a `historical` prefix, or a retired path the move
            # map puts under one (a delivery row before it moves), and the
            # manifest, which has to name what it retires.
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


def verdict(found: dict[str, list[str]], enforce: bool) -> int:
    """The exit status a run owes: report mode never fails on findings."""
    return 1 if enforce and any(found.values()) else 0


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
# the guard (R9-RO-10): what a diff ADDS, refused whatever mode the arms are in
#
# The four arms above measure the whole tree's distance to the target, so they
# stay in report mode until the moves finish. The guard reads only the diff
# from the merge base, and refuses three things that move the tree AWAY from
# the target, so it enforces from the day it lands:
#
#   new-reference  a changed file gains a line citing a LANDED retired path
#   unswept        this diff lands a move, and a live line still cites it
#   placement      an added file sits outside every category (unless it is
#                  under a planned move not yet made), or at a path whose move
#                  had landed at the base
#
# A retired entry has LANDED when no tracked file sits under its old path.
# Each exemption is keyed on the ENTRY, never on the line: a line is not a
# citation of `old` when it also names that entry's new path (a dual-path
# fallback, or a narrative that tells its reader where the file went), when
# `old` is the literal argument of `locate(` or `canon(` (the move map
# resolves it), or when it carries `layout:old=<old>` (a fixture building the
# old tree on purpose). Any of the three for one path exempts no other path
# on the same line.


def exempt(old: str, new: str | None, line: str) -> bool:
    o = re.escape(old.rstrip("/"))
    return bool((new and new.rstrip("/") in line)
                or re.search(r"\b(?:locate|canon)\(\s*['\"`]" + o + r"/?['\"`]", line)
                or re.search(r"layout:old=" + o + r"(?![\w./-])", line))

# Text the guard does not read, though the reference arm still counts it:
# the policy-lint config, whose keys are spelt old ON PURPOSE (`canon`'s
# spelling until R9-RO-9 retires `canon`, so a key spelt new matches nothing);
# root-cause records, whose subject is often the old path that broke; and the
# generated rule copies, whose text is their source's (guarded at the source,
# and `rules_sync.mjs --check` refuses a copy that drifts from it).
GUARD_EXEMPT = ("dev/governance/config/", "dev/audit/rca/", ".claude/rules/", ".cursor/rules/")


def landed(files: list[str], retired: list[dict]) -> list[dict]:
    """The landed entries, and every directory their moves emptied: the map
    retires a directory's files one by one, and a citation of the directory
    (a `git diff -- <dir>`, a glob) then reads nothing, silently."""
    have = {p[:i + 1] for p in files for i, c in enumerate(p) if c == "/"} | set(files)
    out = [r for r in retired if r["old"] not in have]
    known = {r["old"] for r in retired}
    while True:
        dirs = {o.rstrip("/").rpartition("/")[0] + "/" for o in (r["old"] for r in out)}
        dirs = sorted(d for d in dirs - have - known if d != "/")
        if not dirs:
            return out
        for d in dirs:
            news = [r["new"] for r in out if r["old"].startswith(d)]
            # Where its files went, as far as they went together: a pointer for
            # the reader, never a fallback (`stale_lines`).
            new = None if None in news else os.path.commonpath([n.rstrip("/").rpartition("/")[0]
                                                                if not n.endswith("/") else n.rstrip("/")
                                                                for n in news]) + "/"
            out.append({"old": d, "new": None if new == "/" else new, "since": "emptied"})
        known.update(dirs)


def guard_re(old: str) -> re.Pattern[str]:
    """`ref_re`, but a top-level `old` is not cited by a nested path's tail:
    `pkg/<name>` is not the retired top-level `<name>`. A nested `old` keeps
    matching after a `/`, as `$ROOT/<old>` spells it."""
    rx = ref_re(old)
    return re.compile(r"(?<!/)" + rx.pattern) if "/" not in old.rstrip("/") else rx


def stale_lines(text: str, entries: list[dict]) -> list[tuple[str, str]]:
    """(old, line) for each line of `text` citing a landed entry, fallbacks
    excepted."""
    out = []
    if not entries:
        return out
    any_old = re.compile("|".join(re.escape(r["old"].rstrip("/")) for r in entries))
    for line in text.splitlines():
        if not any_old.search(line):
            continue
        hits = [r for r in entries if r["old"].rstrip("/") in line and guard_re(r["old"]).search(line)]
        for r in hits:
            emptied = r.get("since") == "emptied"
            if exempt(r["old"], None if emptied else r["new"], line):
                continue
            if emptied and any(h is not r and h["old"].startswith(r["old"]) for h in hits):
                continue  # the file it holds is the citation, counted once
            out.append((r["old"], line))
    return out


def blobs(root: Path, specs: list[str]) -> dict[str, str | None]:
    """Each `<rev>:<path>` as text through one `git cat-file --batch`, None for
    a missing or binary blob."""
    proc = subprocess.run(["git", "cat-file", "--batch"], cwd=root, check=True, capture_output=True,
                          input="".join(f"{s}\n" for s in specs).encode())
    out, buf = {}, proc.stdout
    for s in specs:
        head, _, buf = buf.partition(b"\n")
        if head.endswith(b" missing"):
            out[s] = None
            continue
        size = int(head.rsplit(b" ", 1)[1])
        data, buf = buf[:size], buf[size + 1:]
        out[s] = None if b"\0" in data[:8000] else data.decode(errors="replace")
    return out


def guard_base(root: Path, ref: str) -> str | None:
    """The merge base of `ref` and HEAD; on HEAD itself with nothing staged
    (a push to main) the first parent, so the merge just made is what is read."""
    def rev(*a: str) -> str | None:
        p = subprocess.run(["git", *a], cwd=root, capture_output=True, text=True)
        return p.stdout.strip() if p.returncode == 0 and p.stdout.strip() else None
    base = rev("merge-base", ref, "HEAD")
    staged = subprocess.run(["git", "diff", "--cached", "--quiet", "HEAD"], cwd=root).returncode
    if base and base == rev("rev-parse", "HEAD") and not staged:
        base = rev("rev-parse", "--verify", "--quiet", "HEAD^1")
    return base


def listing(root: Path, rev: str) -> list[str]:
    return [p for p in git(root, "ls-tree", "-r", "-z", "--name-only", rev).decode().split("\0") if p]


def guard(root: Path, manifest: dict, base: str, rev: str | None = None) -> list[str]:
    """The guard's findings for the index at `root` (or commit `rev`) against
    commit `base`."""
    retired, cats = manifest["retired"], compiled(manifest)
    skip = (MANIFEST, *manifest["historical"], *GUARD_EXEMPT)
    files = tracked(root) if rev is None else listing(root, rev)
    then = listing(root, base)
    now, before = landed(files, retired), landed(then, retired)
    fresh = [r for r in now if r not in before]
    planned = [r for r in retired if r not in now]
    diff = git(root, "diff", *(["--cached", base] if rev is None else [base, rev]),
               "-M", "--name-status", "-z").decode().split("\0")
    at = "" if rev is None else rev
    found: list[str] = []
    read: list[tuple[str, str, str]] = []
    i = 0
    while i < len(diff) - 1:
        status = diff[i]
        if status[:1] in "RC":
            src, path, i = diff[i + 1], diff[i + 2], i + 3
        else:
            src, path, i = diff[i + 1], diff[i + 1], i + 2
        if status[:1] == "D":
            continue
        if status[:1] in "ARC":
            hit = next((r for r in before if under(path, r["old"])), None)
            if hit:
                found.append(f"placement: {path} re-adds a moved path; it lives at {hit['new'] or 'nothing (deleted)'}")
            elif len(categories_of(path, cats)) != 1 and not any(under(path, r["old"]) for r in planned):
                found.append(f"placement: {path} is in {len(categories_of(path, cats))} categories of {MANIFEST}; "
                             "add it where its kind belongs, or a category for the kind")
        if not path.startswith(skip):
            read.append((status[:1], src, path))
    text = blobs(root, [f"{at}:{p}" for _, _, p in read] + [f"{base}:{s}" for st, s, _ in read if st != "A"])
    for st, src, path in read:
        head = text[f"{at}:{path}"]
        if head is None:
            continue
        was = text[f"{base}:{src}"] if st != "A" else ""
        old = {}
        for k in stale_lines(was or "", now):
            old[k] = old.get(k, 0) + 1
        for o, line in stale_lines(head, now):
            if old.get((o, line)):
                old[(o, line)] -= 1
            else:
                found.append(f"new-reference: {path} cites retired path {o}: {line.strip()[:120]}")
    if fresh:
        pats = "\n".join(r["old"].rstrip("/") for r in fresh) + "\n"
        proc = subprocess.run(["git", "grep", *(["--cached"] if rev is None else []), "-z", "-n", "-I", "-F",
                               "-f", "-", *([] if rev is None else [rev]), "--", ".",
                               *(f":(exclude,literal){x}" for x in skip)],
                              cwd=root, input=pats.encode(), capture_output=True)
        for rec in proc.stdout.decode(errors="replace").splitlines():
            path, line, body = rec.split("\0", 2)
            if rev is not None:
                path = path.split(":", 1)[1]
            for o, _ in stale_lines(body, fresh):
                found.append(f"unswept: {path}:{line} cites {o}, which this diff moves")
    return found


def stale(root: Path, manifest: dict) -> list[str]:
    """Every live line in the index citing a landed path: what the guard
    keeps from growing, listed whole (historical and exempt text skipped)."""
    files = tracked(root)
    now = landed(files, manifest["retired"])
    skip = (MANIFEST, *manifest["historical"], *GUARD_EXEMPT)
    text = blobs(root, [f":{p}" for p in files if not p.startswith(skip)])
    return [f"{k[1:]}: {o} | {line.strip()[:120]}" for k, t in text.items() if t for o, line in stale_lines(t, now)]


def guard_self_test() -> int:
    """A two-commit repo per case on a stub manifest: the base, then the
    change staged, each case naming how many findings of which kind it owes."""
    m = {"categories": [{"name": "docs", "globs": ["docs/*.md"], "why": "t"},
                        {"name": "tools", "globs": ["tools/**"], "why": "t"},
                        {"name": "arch", "globs": ["arch/**"], "why": "t"},
                        {"name": "twin", "globs": ["docs/twin.md"], "why": "t"}],
         "historical": ["arch/"],
         "retired": [{"old": "old/gone.sh", "new": "tools/gone.sh", "since": "1"},
                     {"old": "old/briefs/a.md", "new": "docs/a.md", "since": "1"},
                     {"old": "gone.txt", "new": None, "since": "1"},
                     {"old": "old/dir/", "new": "tools/dir/", "since": None},
                     {"old": "old/wip.sh", "new": "tools/wip.sh", "since": None}]}
    base = {"docs/a.md": "intro\n", "docs/b.md": "run old/gone.sh here\n", "tools/gone.sh": "",
            "old/dir/x.sh": "", "old/wip.sh": "", "docs/c.md": "see old/wip.sh\n"}
    cites = "run old/gone.sh now\n"
    cases = [
        ("null: the base tree unchanged", {}, (), {}),
        ("a doc gains a citation of a landed path", {"docs/a.md": cites}, (), {"new-reference": 1}),
        ("the same line naming the new path too", {"docs/a.md": "old/gone.sh is tools/gone.sh now\n"}, (), {}),
        ("the same line through the move map", {"docs/a.md": "locate('old/gone.sh')\n"}, (), {}),
        ("the same line marked as building the old tree", {"tools/t.sh": "touch old/gone.sh  # layout:old=old/gone.sh\n"}, (), {}),
        ("a stale command whose marker names another path", {"tools/t.sh": "bash old/gone.sh  # layout:old=old/wip.sh\n"}, (),
         {"new-reference": 1}),
        ("a stale command with an unkeyed marker", {"tools/t.sh": "bash old/gone.sh  # layout:old\n"}, (), {"new-reference": 1}),
        ("a stale command beside a locate of another path", {"tools/t.sh": "locate('x'); bash old/gone.sh\n"}, (),
         {"new-reference": 1}),
        ("prose naming the marker", {"docs/a.md": "run old/gone.sh, or mark it layout:old\n"}, (), {"new-reference": 1}),
        ("the old path as the move map's own argument", {"tools/t.py": "p = locate('old/gone.sh')\n"}, (), {}),
        ("the citation under a historical prefix", {"arch/r.md": cites}, (), {}),
        ("an old citation kept while the file changes", {"docs/b.md": "run old/gone.sh here\nmore\n"}, (), {}),
        ("a second copy of an old citation", {"docs/b.md": "run old/gone.sh here\n" * 2}, (), {"new-reference": 1}),
        ("a file renamed with its old citation", {"docs/d.md": "run old/gone.sh here\n"}, ("docs/b.md",), {}),
        ("a citation of a planned path", {"docs/a.md": "see old/wip.sh\n"}, (), {}),
        ("a nested file sharing a retired top-level name", {"docs/a.md": "pkg/gone.txt is fine\n"}, (), {}),
        ("the retired top-level name itself", {"docs/a.md": "see gone.txt\n"}, (), {"new-reference": 1}),
        ("a citation of a directory the moves emptied", {"docs/a.md": "git diff -- old/briefs/\n"}, (), {"new-reference": 1}),
        ("a file re-added in a directory the moves emptied", {"old/briefs/b.md": ""}, (), {"placement": 1}),
        ("a file outside every category", {"misc/x.txt": ""}, (), {"placement": 1}),
        ("a file in its category", {"tools/y.sh": ""}, (), {}),
        ("a file in two categories", {"docs/twin.md": ""}, (), {"placement": 1}),
        ("a file citation inside an emptied directory, counted once", {"docs/a.md": "see old/briefs/a.md\n"}, (),
         {"new-reference": 1}),
        ("a file under a planned move", {"old/dir/y.sh": ""}, (), {}),
        ("a file re-added at a landed path", {"old/gone.sh": ""}, (), {"placement": 1, "new-reference": 0}),
        ("a move landed, a citation left", {"tools/wip.sh": ""}, ("old/wip.sh",), {"unswept": 1}),
        ("a move landed and swept", {"tools/wip.sh": "", "docs/c.md": "see tools/wip.sh\n"}, ("old/wip.sh",), {}),
    ]
    failed = 0
    from throwaway_git import throwaway_git_init
    tmp = Path(tempfile.mkdtemp(prefix="hpo-layout-guard-"))
    g = ["git", "-c", "user.name=t", "-c", "user.email=t@t", "-c", "commit.gpgsign=false"]
    try:
        env = throwaway_git_init(tmp, "-q")
        for p, t in {**base, MANIFEST: json.dumps(m)}.items():
            (tmp / p).parent.mkdir(parents=True, exist_ok=True)
            (tmp / p).write_text(t)
        subprocess.run([*g, "add", "-A"], cwd=tmp, check=True, env=env)
        subprocess.run([*g, "commit", "-qm", "base"], cwd=tmp, check=True, env=env)
        sha = git(tmp, "rev-parse", "HEAD").decode().strip()
        for name, add, rm, want in cases:
            # Each case starts from the base commit, index and tree both.
            subprocess.run(["git", "reset", "-q", "--hard", sha], cwd=tmp, check=True, env=env)
            subprocess.run(["git", "clean", "-qfdx"], cwd=tmp, check=True, env=env)
            if rm:
                subprocess.run(["git", "rm", "-q", *rm], cwd=tmp, check=True, env=env)
            for p, t in add.items():
                (tmp / p).parent.mkdir(parents=True, exist_ok=True)
                (tmp / p).write_text(t)
            if add:
                subprocess.run(["git", "add", *add], cwd=tmp, check=True, env=env)
            found = guard(tmp, m, sha)
            got = {k: sum(f.startswith(k + ":") for f in found) for k in ("new-reference", "unswept", "placement")}
            ok = all(got[k] == want.get(k, 0) for k in got)
            print(f"  {'ok  ' if ok else 'FAIL'} guard self-test: {name}: {got}")
            if not ok:
                failed += 1
                for f in found:
                    print(f"         {f}")
    finally:
        shutil.rmtree(tmp)
    return failed


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
    to_hist = next(r for r in retired if r["new"] and r["old"].endswith("/")
                   and any(r["new"].startswith(h) for h in manifest["historical"]))
    moved_dir = next(r for r in retired if r["new"] and r["old"].endswith("/"))
    single = next(g for c in manifest["categories"] if c["name"] == "docs"
                  for g in c["globs"] if "*" in g and "**" not in g and "{" not in g)
    below_star = single.rsplit("/", 1)[0] + "/sub/" + instance(single.rsplit("/", 1)[1])
    landed = dict(moved, since="#9999")
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
        ("retired target outside every category", {"docs/notes/x.md": ""},
         lambda m: m["retired"].append({"old": "docs/notes/", "new": "nowhere/", "since": None}), (1, 1, 0, 1)),
        ("moved path re-added after its move landed", {moved["old"]: ""},
         lambda m: m["retired"].__setitem__(m["retired"].index(moved), landed),
         (0 if _admitted(moved["old"], manifest) else 1, 1, 0, 0)),
        ("file one directory below a single-star glob", {below_star: ""}, None, (1, 0, 0, 0)),
        ("live citation of a retired directory ending a sentence",
         {user_doc: f"moved from {moved_dir['old'][:-1]}.\n"}, None, (0, 0, 1, 0)),
        ("dead retired entry", {}, lambda m: m["retired"].append(
            {"old": "nothere-a/", "new": "dev/archive/nothere-b/", "since": None}), (0, 0, 0, 1)),
        ("dead category glob", {}, lambda m: m["categories"].append(extra_cat), (0, 0, 0, 1)),
        ("negative: the citation under the archive", {"dev/archive/x.md": cite}, None, (0, 0, 0, 0)),
        ("negative: the citation in a delivery row", {"dev/programme/delivery/9999.md": cite}, None, (0, 0, 0, 0)),
        ("negative: the citation in a row not yet moved", {to_hist["old"] + "9999.md": cite}, None, (1, 1, 0, 0)),
        ("negative: a longer name that contains it", {user_doc: f"see `{moved['old']}x` and `x{moved['old']}`\n"},
         None, (0, 0, 0, 0)),
        ("negative: the new path cited", {user_doc: f"see `{moved['new']}`\n"}, None, (0, 0, 0, 0)),
    ]
    from throwaway_git import throwaway_git_init
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
            env = throwaway_git_init(tmp, "-q")
            subprocess.run(["git", "add", "-A"], cwd=tmp, check=True, env=env)
            found, n = check(tmp, m)
            got = tuple(len(found[a]) for a in ARMS)
            count = listed(tmp)
            # --enforce fails exactly when some arm has a finding; report never does.
            ok = (got == want and n == count and n >= len(files)
                  and verdict(found, True) == (1 if any(want) else 0)
                  and verdict(found, False) == 0)
            if name.startswith("moved path re-added"):
                ok = ok and any(m.startswith("reintroduces moved path") for m in found["retired"])
            print(f"  {'ok  ' if ok else 'FAIL'} self-test: {name}: counts {got}, want {want}; "
                  f"enumerated {n} of {count} listed")
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
    ap.add_argument("--guard", action="store_true")
    ap.add_argument("--stale", action="store_true")
    ap.add_argument("--replay", type=int, metavar="N",
                    help="the guard over the last N first-parent commits of --base, each against its parent")
    ap.add_argument("--base", default=os.environ.get("GOLDEN_REF") or "origin/main")
    ap.add_argument("--verbose", action="store_true")
    ap.add_argument("--gen-retired", metavar="INVENTORY")
    a = ap.parse_args()
    if a.replay:
        for c in git(ROOT, "rev-list", "--first-parent", "-n", str(a.replay), a.base).decode().split():
            try:
                m = json.loads(git(ROOT, "show", f"{c}:{MANIFEST}"))
            except subprocess.CalledProcessError:
                print(f"{c[:10]} no {MANIFEST}")
                continue
            got = guard(ROOT, m, f"{c}^1", c)
            kinds = {k: sum(f.startswith(k + ":") for f in got) for k in ("new-reference", "unswept", "placement")}
            print(f"{c[:10]} {kinds} {git(ROOT, 'log', '-1', '--format=%s', c).decode().strip()[:60]}")
            for f in got if a.verbose else []:
                print(f"    {f}")
        return 0
    if a.stale:
        lines = stale(ROOT, load(ROOT))
        print("\n".join(lines))
        print(f"layout: {len(lines)} live line(s) cite a landed retired path")
        return 0
    if a.gen_retired:
        print(json.dumps(gen_retired(Path(a.gen_retired), ROOT), indent=1))
        return 0
    rc = 0
    run_all = not (a.report or a.enforce or a.self_test or a.guard)
    if a.report or a.enforce or run_all:
        found, n = check(ROOT, load(ROOT))
        report(found, n, a.verbose)
        count = listed(ROOT)
        if n != count:
            print(f"FAIL: enumerated {n} path(s) but git ls-files lists {count}")
            rc = 1
        rc = rc or verdict(found, a.enforce)
        print(f"layout: MODE: {'ENFORCE' if a.enforce else 'REPORT (exit 0 on findings until R9-RO-9)'}")
    if a.guard or run_all:
        base = guard_base(ROOT, a.base)
        if base is None:
            print(f"layout: GUARD: SKIP -- no merge base with {a.base} here")
        else:
            refused = guard(ROOT, load(ROOT), base)
            for msg in refused:
                print(f"    {msg}")
            print(f"layout: GUARD: {len(refused)} refusal(s) against {base[:12]}")
            rc = rc or (1 if refused else 0)
    if a.self_test or run_all:
        failed = self_test(ROOT) + locate_self_test(ROOT) + guard_self_test()
        print(f"layout self-test: {'ok' if not failed else f'{failed} case(s) FAILED'}")
        rc = rc or (1 if failed else 0)
    return rc


if __name__ == "__main__":
    sys.exit(main())
