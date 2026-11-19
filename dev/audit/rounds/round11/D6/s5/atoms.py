#!/usr/bin/env python3
"""D6-s5 M1/M2: row every text unit of the seat's cells and check each mechanically checkable atom.

Metric: per unit, the backticked atoms it states that the tree can falsify -- a repository path
(exists at the root, relative to the document, as a glob, or by basename/suffix anywhere in the
tree), a `file:symbol` (the symbol is defined or assigned in that file) and a `script --flag`
(the flag literal occurs in that script's source).  A unit holding at least one atom is a
`claim` row: verdict true when every atom resolves, `stale` when a path or symbol atom does not.
Count key: the atom as written in the document, resolved against the files the tree delivers.

Command (from the export root):
  PYTHONPATH=tests/hastub ~/venv-ci/bin/python3 dev/audit/rounds/round11/D6/s5/atoms.py \
      [--root .] [--repo /path/to/clone --ref SHA] [--ledger OUT.tsv] [--units dev/audit/rounds/round11/D6/s5/units.tsv]
Expected at baseline 92d38ecb640bd462f2e19c0814d0f0b7df1ee692 (box B13, container):
  RESULT units=3483, the claim/stale counts this seat's REPORT.md records, exact.
Perturbation: --plant-missing writes every unresolved path atom as an empty file into a temp
copy's file list (in memory) -> RESULT stale_atoms goes to_zero for path atoms.
The units file is `tools/audit/text_ledger.py units --dim D6 --seat D6-s5 ...` output; the
harness re-derives each unit's text through `text_ledger.units_of` (the production instrument).
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import argparse, fnmatch, re, sys, time
from pathlib import Path

sys.path.insert(0, "tools/audit")
import text_ledger  # noqa: E402  the production enumerator

SRC = {"repo": None, "ref": None}


def source(root, path):
    """A file's text as the resolving tree delivers it (the baseline commit when --repo is given)."""
    if SRC["repo"]:
        import subprocess
        r = subprocess.run(["git", "-C", SRC["repo"], "show", f"{SRC['ref']}:{path}"], capture_output=True, text=True, errors="replace")
        return r.stdout
    try:
        return (Path(root) / path).read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


SELF = "dev/audit/rounds/round11/D6/s5"
EXT = (".py", ".md", ".json", ".sh", ".mjs", ".js", ".yml", ".yaml", ".txt", ".tsv", ".mdc", ".toml", ".cfg", ".html", ".svg", ".csv")
TOPS = ("tools/", "tests/", "dev/", "docs/", "custom_components/", ".claude/", ".github/", "blueprints/")
BT = re.compile(r"`([^`\n]+)`")
SKIP_PREFIX = ("$", "~", "/tmp", "/home", "/root", "origin/", "http", "refs/", "handoff/", "<", "heads/", "main:", "plan/", "design/", "audit-")


def git_tree(repo, ref):
    import subprocess
    out = set(subprocess.check_output(["git", "-C", repo, "ls-tree", "-r", "--name-only", ref], text=True).split("\n")) - {""}
    dirs = {"/".join(f.split("/")[:i]) for f in out for i in range(1, f.count("/") + 1)}
    return out, dirs


def tree(root):
    out, dirs = set(), set()
    for dp, dn, fn in os.walk(root):
        rel = os.path.relpath(dp, root)
        if rel == ".git" or rel.startswith(".git/") or rel.startswith(SELF) or "/node_modules" in "/" + rel or "__pycache__" in rel:
            continue
        r = "" if rel == "." else rel + "/"
        if r:
            dirs.add(r.rstrip("/"))
        for f in fn:
            out.add(r + f)
    return out, dirs


def brace(p):
    m = re.search(r"\{([^{}]*)\}", p)
    if not m:
        return [p]
    return [x for alt in m.group(1).split(",") for x in brace(p[:m.start()] + alt + p[m.end():])]


def path_atoms(atom):
    """Tokens of a backticked atom that state a repository path."""
    out = []
    for tok in atom.split():
        tok = tok.strip("'\",;()")
        if not tok or tok.startswith(SKIP_PREFIX) or tok.startswith("-") or "=" in tok or "@" in tok:
            continue
        base = re.split(r"[#]", tok)[0]
        while base.startswith("./"):
            base = base[2:]
        base = re.sub(r":[A-Za-z_][\w.]*$", "", base)
        base = re.sub(r":\d+(-\d+)?$", "", base)
        if not base or base.startswith(".") and base.count("/") == 0 and not base.endswith(EXT):
            continue
        if not re.fullmatch(r"[\w./*{},+\-\[\]]+", base):
            continue
        if base.endswith(EXT) or base.endswith("/") or base.startswith(TOPS):
            out.append(base)
    return out


def resolve(p, doc, files, dirs, by_base):
    if "*" in p or "{" in p or "[" in p:
        pats = brace(p)
        if "/" not in p.rstrip("/"):
            return any(fnmatch.fnmatch(os.path.basename(f), pat) for pat in pats for f in files)
        return any(fnmatch.fnmatch(f, pat) or fnmatch.fnmatch(f, os.path.join(os.path.dirname(doc), pat)) or fnmatch.fnmatch(f, "*/" + pat)
                   for pat in pats for f in files)
    q = p.rstrip("/")
    if q in files or q in dirs:
        return True
    rel = os.path.normpath(os.path.join(os.path.dirname(doc), q))
    if rel in files or rel in dirs:
        return True
    if "/" not in q:
        return q in by_base or any(d.rsplit("/", 1)[-1] == q for d in dirs)
    return any(f.endswith("/" + q) for f in files) or any(d.endswith("/" + q) for d in dirs)


# Triage of an atom the tree does not hold (the rule REPORT.md states):
#  NOT_PATH: an extension or a quoted source fragment or a placeholder, not a path claim (dropped);
#  ABSENT_STATED: the sentence itself says the path is gone, archived at a SHA, out of tree or owed;
#  anything else under a top-level repository directory: stale;
#  anything else: a runtime-state or seat-workdir name outside the repository -> unverifiable here.
NOT_PATH = {".mdc", ".sh", "/roster_sync.py", "foo.py"}
ABSENT_STATED = {"SEAT-BLOCK.md", "dev/programme/carries/carry-201.json", "tools/audit/round1/", "round3/",
                 "wave-1b-groups.json", "wave-2-groups.json", "wave-3-groups.json", "web-phase0.js",
                 "triage-quiet-judges.json", "round2/HARNESSES.md", "nudge.md", "../setup-qa/", "docs/handovers/",
                 "relay_watch.sh", "prune_refs.py --no-age-keeps"}


def triage(atom, kind):
    a = atom.strip()
    if a in NOT_PATH:
        return None
    if a in ABSENT_STATED:
        return "ok"
    if kind != "path" or a.startswith(TOPS):
        return "stale"
    return "unverifiable"


SYM = re.compile(r"^([\w./-]+\.(?:py|mjs|js|sh)):([A-Za-z_][\w]*)(?:\.[\w]+)*")


def symbol_ok(path, name, root, files, by_base):
    cands = [path] if path in files else [f for f in files if f.endswith("/" + path)] or by_base.get(os.path.basename(path), [])
    for c in cands:
        src = source(root, c)
        if re.search(rf"(def|class|function|const|let|var|async def)\s+{re.escape(name)}\b|^\s*{re.escape(name)}\s*[:=]|\b{re.escape(name)}\s*=", src, re.M):
            return True
    return False


def check_unit(text, doc, root, files, dirs, by_base):
    """[(atom, kind, ok)] for one unit."""
    res = []
    for atom in BT.findall(text):
        a = atom.strip()
        for p in path_atoms(a):
            res.append((p, "path", resolve(p, doc, files, dirs, by_base)))
        m = SYM.match(a)
        if m and resolve(m.group(1), doc, files, dirs, by_base):
            res.append((f"{m.group(1)}:{m.group(2)}", "symbol", symbol_ok(m.group(1), m.group(2), root, files, by_base)))
        toks = a.split()
        if toks and toks[0] in ("python3", "node", "bash"):
            toks = toks[1:]
        if toks and toks[0].endswith((".py", ".sh", ".mjs")) and resolve(toks[0], doc, files, dirs, by_base):
            t0 = toks[0][2:] if toks[0].startswith("./") else toks[0]
            cands = [t0] if t0 in files else ([f for f in files if f.endswith("/" + t0)] or by_base.get(os.path.basename(t0), []))
            srcs = [source(root, c) for c in cands]
            if srcs:
                for t in toks[1:]:
                    fl = t.split("=")[0]
                    if re.fullmatch(r"--[a-z][\w-]*", fl):
                        res.append((f"{t0} {fl}", "flag", any(fl in x for x in srcs)))
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    ap.add_argument("--units", default=f"{SELF}/units.tsv")
    ap.add_argument("--ledger")
    ap.add_argument("--repo", help="resolve against this repository's tree at --ref (the baseline) instead of the export")
    ap.add_argument("--ref", default="92d38ecb640bd462f2e19c0814d0f0b7df1ee692")
    ap.add_argument("--plant-missing", action="store_true")
    ap.add_argument("--list-stale", action="store_true")
    a = ap.parse_args()
    t0 = time.process_time()
    SRC.update(repo=a.repo, ref=a.ref)
    files, dirs = git_tree(a.repo, a.ref) if a.repo else tree(a.root)
    unit_ids = [l.split("\t") for l in Path(a.units).read_text().splitlines() if l.strip()]
    docs = sorted({u[0].split("#")[0] for u in unit_ids})
    units = []
    for d in docs:
        units += text_ledger.units_of(d, text_ledger.read(a.root, d), "D6")
    by_base = {}
    for f in files:
        by_base.setdefault(os.path.basename(f), []).append(f)
    if a.plant_missing:  # perturbation: the tree delivers every path the documents name
        for uid, _l, _k, t in units:
            for atom, kind, ok in check_unit(t, uid.split("#")[0], a.root, files, dirs, by_base):
                if kind == "path" and not ok and triage(atom, kind) == "stale" and "*" not in atom and "{" not in atom:
                    files.add(atom.rstrip("/"))
                    by_base.setdefault(os.path.basename(atom.rstrip("/")), []).append(atom)
    rows, stale_units, stale_atoms, claims, per_kind, unverifiable = [], [], 0, 0, {}, 0
    for uid, line, kind, t in units:
        doc = uid.split("#")[0]
        res = check_unit(t, doc, a.root, files, dirs, by_base)
        if not res:
            continue
        res = [(x, k, ok) for x, k, ok in res if ok or triage(x, k) is not None]
        if not res:
            continue
        claims += 1
        for x, k, ok in res:
            per_kind.setdefault(k, [0, 0])[0 if ok else 1] += 1
        bad = [(x, k) for x, k, ok in res if not ok and triage(x, k) == "stale"]
        unv = [(x, k) for x, k, ok in res if not ok and triage(x, k) == "unverifiable"]
        stated = [(x, k) for x, k, ok in res if not ok and triage(x, k) == "ok"]
        stale_atoms += len(bad)
        unverifiable += bool(unv) and not bad
        cmd = "atoms.py check_unit (references only: paths, file:symbol, script --flag): " + "; ".join(f"{k}:{x}" for x, k, _ in res)
        result = f"{sum(ok for _, _, ok in res)}/{len(res)} atoms resolve in the baseline tree"
        if stated:
            result += "; absent as the sentence states: " + ", ".join(x for x, _ in stated)
        if unv:
            result += "; runtime/out-of-tree names: " + ", ".join(x for x, _ in unv)
        if bad:
            result += "; unresolved: " + ", ".join(f"{k}:{x}" for x, k in bad)
        verdict = "stale" if bad else "unverifiable" if unv else "true"
        truth = ("no such " + "; ".join(f"{k} {x}" for x, k in bad) + " in the baseline tree") if bad else \
            ("names a runtime-state or seat-workdir path outside the repository; no state directory on this box to check it" if unv else "")
        rows.append([uid, str(line), "claim", cmd[:900], result[:600], verdict, truth[:600]])
        if bad:
            stale_units.append((uid, line, bad))
    print(f"RESULT units={len(units)}")
    print(f"RESULT atom_claim_units={claims}")
    print(f"RESULT stale_units={len(stale_units)}")
    print(f"RESULT stale_atoms={stale_atoms}")
    print(f"RESULT unverifiable_units={unverifiable}")
    for k, (ok, bad) in sorted(per_kind.items()):
        print(f"RESULT atoms_{k}_ok={ok} atoms_{k}_unresolved={bad}")
    if a.list_stale:
        for uid, line, bad in stale_units:
            print("STALE", uid, line, " | ".join(f"{k}:{x}" for x, k in bad))
    if a.ledger:
        Path(a.ledger).write_text("\n".join("\t".join(r) for r in rows) + "\n")
    cpu = time.process_time() - t0
    try:
        import resource
        sw = resource.getrusage(resource.RUSAGE_SELF).ru_nswap
    except Exception:
        sw = 0
    print(f"RESULT thread_factor={1.0:.2f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print(f"RESULT swapins={sw}")
    print(f"RESULT cpu_s={cpu:.2f} provisional")


if __name__ == "__main__":
    main()
