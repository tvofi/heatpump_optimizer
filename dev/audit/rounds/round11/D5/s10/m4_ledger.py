#!/usr/bin/env python3
"""D5-s10 step D5.M4: the mechanical rows of the comment ledger over every D5 unit of the seat's cells.

Metric: per D5 unit (tools/audit/text_ledger.py:units_of), the count of repository paths and
`file:symbol` references it names that do not resolve in the baseline tree (criterion C2), the
count of sentences over 40 words (C5), and, where the unit sits directly on a numeric constant
assignment, whether the number it cites matches that constant (the C7 redispatch item).
Count key: the unit's own text, as text_ledger.py:units_of delivers it from the file on disk.

Command (from the export root):
  PYTHONPATH=tests/hastub $HOME/venv-ci/bin/python3 dev/audit/rounds/round11/D5/s10/m4_ledger.py \
      --repo /home/user/heatpump_optimizer --ref 92d38ecb640bd462f2e19c0814d0f0b7df1ee692 \
      [--ledger OUT.tsv] [--file PATH ...]
--repo is any git checkout holding the baseline commit (the export has no .git); the units are
read from the export root (text_ledger's --root, default "."), path existence from `git ls-tree`
at --ref.
Expected at baseline 92d38ecb (box B12, D5-s10, round 11): RESULT units=1794, exact.
Perturbation (judge): --rewrite tools/audit/README.md=dev/audit/README.md (the one-line comment fix, applied
in memory) takes unresolved_paths from 26 to 24 and verdict_false from 3 to 1; --rewrite
dev/audit/README.md=tools/audit/no_such.md raises unresolved_paths (up).
Writes only the --ledger path (default: none) and nothing else.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import argparse, re, subprocess, sys, time
from pathlib import Path

sys.path.insert(0, "tools/audit")
import text_ledger  # noqa: E402  the production enumerator this harness drives

SEAT = "D5-s10"
EXT = r"(?:py|mjs|js|sh|json|md|mdc|yml|yaml|txt|tsv|toml|cfg|ini)"
PATH_RE = re.compile(r"(?<![\w$/.~<{-])((?:\.?[A-Za-z0-9_.-]+/)+[A-Za-z0-9_.-]+\." + EXT + r"|(?:\.?[A-Za-z0-9_-]+/){2,})(?![\w/*<{])")
SYM_RE = re.compile(r"`([A-Za-z0-9_./-]+\.(?:py|mjs|js|sh)):([A-Za-z_][A-Za-z0-9_.]*)")
NUM_RE = re.compile(r"(?<![\w.])(\d+(?:\.\d+)?)(?![\w.]*[/\w])")
ASSIGN_RE = re.compile(r"^\s*(?:const\s+|let\s+|var\s+|export\s+const\s+)?([A-Z][A-Z0-9_]{2,})\s*(?::\s*\w+\s*)?=\s*([-+]?\d+(?:\.\d+)?)\s*[;,]?\s*(?:#.*|//.*)?$")
ROOTS = ("custom_components/", "tests/", "tools/", "dev/", "docs/", ".claude/", ".github/", "blueprints/", ".cursor/")


def tree(repo, ref):
    out = subprocess.check_output(["git", "-C", repo, "ls-tree", "-r", "--name-only", ref], text=True).split("\n")
    files = {f for f in out if f}
    dirs = set()
    for f in files:
        p = f.split("/")
        for i in range(1, len(p)):
            dirs.add("/".join(p[:i]) + "/")
    return files, dirs


def strip_comment(t):
    return re.sub(r"(?m)^\s*(#+|//+|/\*+|\*+/?|\"\"\"|''')", " ", t)


def resolve(path, src, files, dirs, base_names):
    p = path.lstrip("./") if path.startswith("./") else path
    if p in files or p in dirs or (p.rstrip("/") + "/") in dirs:
        return True
    rel = str(Path(src).parent / p)
    if rel in files or rel + "/" in dirs:
        return True
    if not p.startswith(ROOTS) and "/" in p:
        # a relative tail (seat/foo.py, round10/D5/x.py): resolves if any tree path ends with it
        return any(f.endswith("/" + p) for f in files) or any(d.endswith("/" + p.rstrip("/") + "/") for d in dirs)
    return False


def candidates(text):
    body = strip_comment(text)
    out = []
    for m in PATH_RE.finditer(body):
        s = m.group(1)
        if any(x in s for x in ("http", "$", "<", "*", "{", "~")) or s.startswith(("/", "tmp/", "proc/")):
            continue
        if s.count("/") == 1 and not re.search(r"\." + EXT + "$", s):
            continue
        if not s.startswith(ROOTS) and not re.search(r"\." + EXT + "$", s):
            continue  # a bare a/b/ phrase ("and/or/", "owner/repo/") is prose, not a path
        out.append(s)
    return out


def symbol_ok(repo, ref, path, sym, files):
    cands = [path] if path in files else [f for f in files if f.endswith("/" + path)]
    if not cands:
        return None
    name = sym.split(".")[-1]
    for c in cands[:3]:
        try:
            txt = subprocess.check_output(["git", "-C", repo, "show", f"{ref}:{c}"], text=True, errors="replace")
        except subprocess.CalledProcessError:
            continue
        if re.search(r"\b" + re.escape(name) + r"\b", txt):
            return True
    return False


LIST_START = re.compile(r"^\s*(?:[-*+]\s|\d+[.)]\s|RESULT\b|EXPECTED\b|CONTROL\b|BAD\b|PRS\b|\||`|python3|node|bash|PYTHONPATH)")


def paragraphs(text):
    """Prose paragraphs of a unit: split at blank lines, list/RESULT lines and indentation steps."""
    out, cur, ind0 = [], [], None
    for raw in strip_comment(text).splitlines():
        line = raw.rstrip()
        ind = len(line) - len(line.lstrip())
        if not line.strip() or LIST_START.match(line) or (cur and ind0 is not None and ind != ind0):
            if cur:
                out.append(" ".join(cur))
            cur, ind0 = ([line.strip()], ind) if line.strip() else ([], None)
            continue
        if not cur:
            ind0 = ind
        cur.append(line.strip())
    if cur:
        out.append(" ".join(cur))
    return out


def long_sentences(text):
    """C5: sentences over 40 words, counted within prose paragraphs only (not across list items)."""
    return [s for p in paragraphs(text) for s in text_ledger.sentences(p) if len(s.split()) > 40]


def adjacent_constant(src_lines, unit_line, text):
    """The NAME = number line directly below a comment block, or None."""
    n = unit_line - 1 + text.count("\n") + 1
    if n < len(src_lines):
        m = ASSIGN_RE.match(src_lines[n])
        if m:
            return m.group(1), m.group(2)
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True)
    ap.add_argument("--ref", required=True)
    ap.add_argument("--root", default=".")
    ap.add_argument("--ledger")
    ap.add_argument("--file", action="append")
    ap.add_argument("--show", action="store_true")
    ap.add_argument("--rewrite", action="append", default=[], help="OLD=NEW applied to every unit's text in memory (the perturbation: the one-line comment fix)")
    ap.add_argument("--adjudicate", help="TSV unit<TAB>verdict<TAB>command<TAB>note: the seat's executed ruling on a row the mechanical check could not settle")
    a = ap.parse_args()
    t0, c0, h0 = time.time(), time.process_time(), time.thread_time()
    files_in = a.file or text_ledger.seat_files(SEAT, a.repo, a.ref)
    files, dirs = tree(a.repo, a.ref)
    base_names = {f.rsplit("/", 1)[-1] for f in files}
    units = text_ledger.enumerate_units(a.root, files_in, "D5")
    rows, n_unres, n_long, n_numcand, n_sym_bad, unit_bad = [], 0, 0, 0, 0, set()
    per_file, long_files = {}, set()
    for uid, line, kind, text in units:
        for rw in a.rewrite:
            old, new = rw.split("=", 1)
            text = text.replace(old, new)
        src = uid.split("#")[0]
        lines = text_ledger.read(a.root, src).splitlines()
        unres = sorted({p for p in candidates(text) if not resolve(p, src, files, dirs, base_names)})
        nres = len(set(candidates(text))) - len(unres)
        syms_bad = []
        for m in SYM_RE.finditer(text):
            ok = symbol_ok(a.repo, a.ref, m.group(1), m.group(2), files)
            if ok is False:
                syms_bad.append(f"{m.group(1)}:{m.group(2)}")
        longs = long_sentences(text)
        num = None
        if kind == "comment":
            adj = adjacent_constant(lines, line, text)
            if adj:
                nums = NUM_RE.findall(strip_comment(text))
                if nums and float(adj[1]) not in {float(x) for x in nums}:
                    num = f"{adj[0]}={adj[1]} cites {','.join(nums[:6])}"
                    n_numcand += 1
        n_unres += len(unres); n_long += len(longs); n_sym_bad += len(syms_bad)
        if longs:
            long_files.add(src)
        bad = bool(unres or syms_bad)
        if bad:
            unit_bad.add(uid)
            per_file.setdefault(src, []).append(uid)
        res = f"paths_ok={nres} unresolved={len(unres)}{(' ' + ';'.join(unres)) if unres else ''} badsym={len(syms_bad)}{(' ' + ';'.join(syms_bad)) if syms_bad else ''} long={len(longs)}" + (f" num_check={num}" if num else "")
        verdict = "false" if (unres or syms_bad) else "true"
        truth = ("names unresolved in the tree at ref: " + ";".join(unres + syms_bad)) if verdict == "false" else ""
        cmd = f"m4_ledger.py --file {src} --show"
        rows.append([uid, str(line), "claim", cmd, res, verdict, truth])
        if a.show and (bad or num or longs):
            print(f"   {uid} L{line} {res}")
            for s in longs:
                print(f"      long({len(s.split())}): {s[:160]}")
    n_adj = 0
    if a.adjudicate:
        by = {r[0]: r for r in rows}
        for l in Path(a.adjudicate).read_text().splitlines():
            if not l.strip() or l.startswith("#"):
                continue
            uid, verdict, cmd, note = l.split("\t")
            if uid not in by:
                if not a.file:
                    print(f"   adjudicate: no such unit {uid}")
                continue
            if by[uid][5] != "false" and verdict != "false":
                continue  # the mechanical check already passes (e.g. under --rewrite): nothing to rule on
            cmd = cmd.replace("REF", a.ref).replace("REPO", a.repo)
            # "ROOT:" runs a harness from the export root (a semantic C1 check); otherwise a git check in --repo
            here = a.root if cmd.startswith("ROOT:") else a.repo
            cmd = cmd[5:] if cmd.startswith("ROOT:") else cmd
            rc = subprocess.run(["bash", "-c", cmd], cwd=here, capture_output=True).returncode
            held = rc == 0
            r = by[uid]
            r[3] = f"cd $REPO && {cmd}"
            r[4] = r[4] + f" adjudicated_rc={rc}"
            # a ruling whose command does not hold is unverifiable, never silently true
            r[5] = verdict if held else "unverifiable"
            r[6] = "" if r[5] == "true" else note
            n_adj += 1
        print(f"RESULT adjudicated={n_adj} count")
    ver = {}
    for r in rows:
        ver[r[5]] = ver.get(r[5], 0) + 1
    for k in sorted(ver):
        print(f"RESULT verdict_{k}={ver[k]} count")
    if a.ledger:
        Path(a.ledger).write_text("\n".join(["\t".join(text_ledger.HEADER)] + ["\t".join(r) for r in rows]) + "\n")
    print(f"RESULT units={len(units)} count")
    print(f"RESULT files={len(files_in)} count")
    print(f"RESULT unresolved_paths={n_unres} count")
    print(f"RESULT unresolved_symbols={n_sym_bad} count")
    print(f"RESULT long_sentences={n_long} count")
    print(f"RESULT files_with_long_sentence={len(long_files)} count")
    print(f"RESULT number_vs_constant_candidates={n_numcand} count")
    print(f"RESULT units_failing_mechanical={len(unit_bad)} count")
    print(f"RESULT files_with_failing_unit={len(per_file)} count")
    for f in sorted(per_file):
        print(f"   file {f} failing_units={len(per_file[f])}")
    try:
        import resource
        pc = time.process_time() - c0
        print(f"RESULT thread_factor={pc / max(time.thread_time() - h0, 1e-9):.3f}")
    except Exception:
        print("RESULT thread_factor=1.000")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT swapins=0")


if __name__ == "__main__":
    main()
