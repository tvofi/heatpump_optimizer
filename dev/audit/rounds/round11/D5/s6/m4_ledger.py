#!/usr/bin/env python3
"""D5-s6 step D5.M4: row every D5 comment unit of the seat's cells by executed checks of the tree.

Metric: per unit, the C2/C5 checks of criteria/D5-criteria.md executed against the tree at the
baseline -- (a) every repository path the unit names resolves to a tracked file or directory,
(b) every `file:symbol` / `module:symbol` citation names a symbol the cited file defines (AST for
Python, a definition regex for shell/JS), (c) every `name()` the unit calls exists as a code token
somewhere in the tree's code (Python NAME tokens; whole text for other suffixes), (d) no sentence
of the unit is over 40 words (C5).  Count key: the unit id text_ledger.py assigns.
A unit with at least one checkable token is a `claim` row (verdict true/false); otherwise
`no-claim`.  Writes LEDGER.tsv and FLAGS.tsv beside this file (or --out DIR) and prints RESULT lines.

Run:  PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D5/s6/m4_ledger.py \
          --repo /home/user/heatpump_optimizer --ref 92d38ecb640bd462f2e19c0814d0f0b7df1ee692
      (--repo is any git checkout holding the baseline commit; files are read from the cwd export)
Further checks: (e) a comment directly above a tuple/list/set/dict display that states a count of
items is compared with the display's length (C1-count, "cited number vs adjacent constant"); (f) every
--flag on a usage line naming the file itself appears in the file's code strings (C1-flag).  Flags of
(a), (e), (f) were read by hand: CONFIRMED lists those confirmed false (truth_checks.py re-executes
each against its production symbol); the rest are rowed true as `adjudicated-ok`.
Expected (baseline 92d38ecb, box B11), exact: units=3781 claim_rows=840 false_rows=263 C1-flag=1
C1-count=1 C2-path=9 C2-cite=0 C2-call=0 C5-len=404 C5_files=99; then
`python3 tools/audit/text_ledger.py check --dim D5 <LEDGER.tsv> --plant --seat D5-s6 --repo R --ref X`
prints unrowed=0 orphan=0 malformed=0 plant_refused=1.
Perturbation: --c5-split FILE rewrites FILE's units in memory with a full stop every 30 words (what a
fix that shortens the sentences does); C5-len must drop (pr_args.sh: 404 -> 372).  --plant-symbol NAME
adds NAME to the code tokens (C2-call stand-in).
Machine: box B11 container.  No timing: counts only.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import argparse, ast, io, re, subprocess, sys, time, tokenize
from pathlib import Path

sys.path.insert(0, "tools/audit")
import text_ledger  # noqa: E402  production instrument: the unit enumerator under test

HERE = Path(__file__).resolve().parent
PATH_RE = re.compile(r"(?<![\w/$<{-])(?<![\w]\.)((?:[\w.-]+/)+[\w.-]*|[\w-]+(?:\.[\w-]+)*\.(?:py|js|mjs|sh|json|md|mdc|yml|yaml|tsv|txt|toml|html))(?![\w/])")
CITE_RE = re.compile(r"(?<![\w/.-])((?:[\w.-]+/)*[\w-]+\.(?:py|sh|mjs|js)):([A-Za-z_][\w.]*)")
CALL_RE = re.compile(r"(?<![\w.$])([A-Za-z_][A-Za-z0-9_]*(?:\.[A-Za-z_][A-Za-z0-9_]*)*)\(\)")
COMMENT_MARK = re.compile(r"^\s*(#+|//+|/\*+|\*+/?|\*)\s?", re.M)
import builtins  # noqa: E402
BUILTIN_OK = set(dir(builtins))


# Flags of kinds C1-count, C1-flag and C2-path the seat confirmed false by hand, each re-executed by
# truth_checks.py against the production symbol.  Every other such flag was read in place and is a
# runtime artefact the script writes (plan.json, VERDICT.md), a placeholder or f-string fragment
# (carry-N.json, dev/programme/rosters/wave-r), a self-test fixture (docs/x.md), a deliberate
# old-layout fallback (roster_edit.py's BRIEF_LINT_OLD), a file cited at another ref, a literal
# whose count the comment does not state, or a flag the parser builds in a loop: rowed `true`.
CONFIRMED = {
    ("tools/release/stamp.py", "C1-count", "RECORD_CLASS_RES"),
    ("tools/release/stamp.py", "C2-path", "tools/audit/README.md"),
    ("tools/release/stamp.py", "C2-path", ".claude/workflows/policy_lint.mjs"),
    ("tools/audit/seat/replay_draws.py", "C2-path", "tests/replay_draws.tsv"),
    ("tools/audit/seat/row_position.py", "C2-path", "dev/audit/harnesses/row_position.py"),
    ("tools/audit/seat/plan_audit.py", "C1-flag", "--target"),
    ("tools/audit/seat/update_pr.sh", "C2-path", "updatepr.sh"),
    ("tools/audit/seat/roster_lib.py", "C2-path", "gen_table_rev3.py"),
    ("tools/audit/seat/plan_table.py", "C2-path", "gen_table_rev3.py"),
}


def confirmed(f, kind, tok):
    return kind == "C5-len" or any(c[0] == f and c[1] == kind and tok.startswith(c[2]) for c in CONFIRMED)


def tracked(repo, ref):
    out = subprocess.check_output(["git", "-C", repo, "ls-tree", "-r", "--name-only", ref], text=True)
    files = set(out.split("\n")) - {""}
    dirs = set()
    for f in files:
        p = f.split("/")
        for i in range(1, len(p)):
            dirs.add("/".join(p[:i]))
    return files, dirs


def code_tokens(files):
    """Every identifier the tree's code (not its comments) holds."""
    toks = set()
    for f in files:
        p = Path(f)
        if p.suffix not in (".py", ".sh", ".js", ".mjs", ".json", ".yml", ".yaml", ".toml", ".md", ".html", ".mdc", ".cfg"):
            continue
        try:
            text = p.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        if p.suffix == ".py":
            try:
                for t in tokenize.generate_tokens(io.StringIO(text).readline):
                    if t.type == tokenize.NAME:
                        toks.add(t.string)
                    elif t.type == tokenize.STRING or t.type == getattr(tokenize, "FSTRING_MIDDLE", -1):
                        toks.update(re.findall(r"[A-Za-z_]\w*", t.string))
                continue
            except (tokenize.TokenError, SyntaxError, IndentationError):
                pass
        if p.suffix in (".sh",):
            text = "\n".join(l for l in text.splitlines() if not l.lstrip().startswith("#"))
        if p.suffix in (".js", ".mjs"):
            text = re.sub(r"(?m)^\s*//.*$", "", text)
        toks.update(re.findall(r"[A-Za-z_]\w*", text))
    return toks


def defined(path, text):
    """Names a file defines: AST bindings at any depth for Python, definition regexes otherwise."""
    names = set()
    if path.endswith(".py"):
        try:
            tree = ast.parse(text)
        except SyntaxError:
            return set(re.findall(r"[A-Za-z_]\w*", text))
        for n in ast.walk(tree):
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                names.add(n.name)
            elif isinstance(n, ast.Name) and isinstance(n.ctx, ast.Store):
                names.add(n.id)
            elif isinstance(n, ast.Attribute) and isinstance(n.ctx, ast.Store):
                names.add(n.attr)
            elif isinstance(n, (ast.Import, ast.ImportFrom)):
                names.update((a.asname or a.name).split(".")[0] for a in n.names)
            elif isinstance(n, ast.arg):
                names.add(n.arg)
        return names
    names.update(re.findall(r"(?m)^\s*(?:function\s+)?([A-Za-z_]\w*)\s*\(\)\s*\{", text))
    names.update(re.findall(r"(?m)^\s*(?:export\s+)?(?:local\s+|readonly\s+|declare\s+[-\w]*\s*)?([A-Za-z_]\w*)=", text))
    names.update(re.findall(r"(?:function|const|let|var|class)\s+([A-Za-z_$][\w$]*)", text))
    return names


CODEISH = re.compile(r"^\s*(python3?|node|bash|\$|--|\.\.\.|[\w./-]+\.(py|sh|mjs|js)\b|[\w./-]+\s*\[)")


def sentences(t):
    """Prose sentences of a unit: comment markers stripped, paragraphs split on blank lines,
    indented or command lines (usage blocks) dropped, text_ledger's own SENT splitter within a
    paragraph, a backtick or double-backtick span counted as one word."""
    out = []
    for para in re.split(r"\n\s*(?:#+|//+|\*)?\s*\n", t):
        keep = []
        for ln in para.splitlines():
            raw = COMMENT_MARK.sub("", ln, count=1) if re.match(r"^\s*(#|//|/\*|\*)", ln) else ln
            if re.match(r"^( {4,}|\t)", raw) or CODEISH.match(raw) or re.match(r"^\s*([-*+]|\d+[.)])\s", raw):
                if keep:
                    out.extend(_split(" ".join(keep))); keep = []
                if re.match(r"^\s*([-*+]|\d+[.)])\s", raw) and not re.match(r"^( {4,}|\t)", raw):
                    keep = [re.sub(r"^\s*([-*+]|\d+[.)])\s", "", raw)]
                continue
            keep.append(raw)
        if keep:
            out.extend(_split(" ".join(keep)))
    return out


def _split(body):
    body = " ".join(body.split())
    body = re.sub(r"``[^`]*``|`[^`]*`", "X", body)
    return [s for s in text_ledger.SENT.split(body) if text_ledger.WORDS.search(s)]


NUMW = {w: i for i, w in enumerate("zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen seventeen eighteen nineteen twenty".split())}
COUNT_RE = re.compile(r"\b(" + "|".join(NUMW) + r"|\d{1,3})\s+(?:[a-z-]+\s+){0,2}?([a-z]+s)\b", re.I)


def literal_sizes(path, text):
    """{first line of the statement after a comment: (name, literal length)} for every assignment
    of a tuple/list/set/dict display: the constant a comment above it may count."""
    out = {}
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return out
    for n in ast.walk(tree):
        if isinstance(n, (ast.Assign, ast.AnnAssign)) and isinstance(n.value, (ast.Tuple, ast.List, ast.Set, ast.Dict)):
            tgt = n.targets[0] if isinstance(n, ast.Assign) else n.target
            name = getattr(tgt, "id", getattr(tgt, "attr", "?"))
            size = len(n.value.keys) if isinstance(n.value, ast.Dict) else len(n.value.elts)
            if any(isinstance(e, ast.Starred) for e in getattr(n.value, "elts", [])):
                continue
            out[n.lineno] = (name, size)
    return out


def code_strings(path, text):
    """The file's code text a usage line's flag must appear in: Python string constants, or
    shell/JS lines that are not comments."""
    if path.endswith(".py"):
        try:
            tree = ast.parse(text)
            doc = ast.get_docstring(tree, clean=False)
            return "\n".join(n.value for n in ast.walk(tree)
                             if isinstance(n, ast.Constant) and isinstance(n.value, str) and n.value != doc)
        except SyntaxError:
            return text
    return "\n".join(l for l in text.splitlines() if not l.lstrip().startswith(("#", "//", "*")))


def usage_flags(path, t):
    """(flag) on a unit's usage lines: a line that names this file's own basename."""
    base = Path(path).name
    out = []
    for ln in t.splitlines():
        if re.search(r"(^|[\s/])" + re.escape(base) + r"\b", ln) and not re.search(r"'s\b", ln.split(base, 1)[1][:3]):
            out += re.findall(r"(?<![\w-])(--[a-z][a-z0-9-]*)", ln.split(base, 1)[1])
    return out


def count_claims(t):
    return [(m.group(0), int(m.group(1)) if m.group(1).isdigit() else NUMW[m.group(1).lower()]) for m in COUNT_RE.finditer(t)]


def resolve_path(tok, unit_file, files, dirs):
    t = tok.rstrip("/.:,")
    if not t or any(c in t for c in "<>{}*$") or t.startswith(("/", "~", "http", "./", "../")):
        return None  # not a repository path claim
    if "/" not in t and not re.search(r"\.(py|js|mjs|sh|json|md|mdc|yml|yaml|tsv|txt|toml|html)$", t):
        return None
    if re.fullmatch(r"[\d./-]+", t) or t.count("/") == 0 and t.split(".")[0] == "":
        return None
    # tokens like "origin/main", "handoff/<topic>", "a/b" units are ref names or ratios, not paths
    first = t.split("/")[0]
    if "/" in t and first not in {d.split("/")[0] for d in dirs} | {f.split("/")[0] for f in files}:
        return None
    base = str(Path(unit_file).parent)
    for cand in (t, f"{base}/{t}"):
        if cand in files or cand in dirs:
            return True
    if any(f.endswith("/" + t) or f == t for f in files) or any(d.endswith("/" + t) for d in dirs):
        return True
    return False


def scan(units, files, dirs, toks, texts):
    rows, flags = [], []
    defs_cache = {}
    for uid, line, kind, t in units:
        f = uid.split("#")[0]
        checks, bad = [], []
        if kind == "file":
            rows.append((uid, line, "no-claim", "", "", "-", "")); continue
        for m in PATH_RE.finditer(t):
            r = resolve_path(m.group(1), f, files, dirs)
            if r is None:
                continue
            checks.append(f"path:{m.group(1)}")
            if not r:
                bad.append(("C2-path", m.group(1)))
        for m in CITE_RE.finditer(t):
            cf, sym = m.group(1), m.group(2)
            hits = [x for x in files if x == cf or x.endswith("/" + cf)]
            if not hits:
                continue
            ok = False
            for h in hits:
                if h not in defs_cache:
                    try:
                        defs_cache[h] = defined(h, Path(h).read_text(encoding="utf-8"))
                    except (OSError, UnicodeDecodeError):
                        defs_cache[h] = None
                d = defs_cache[h]
                if d is None or sym.split(".")[0] in d:
                    ok = True
            checks.append(f"cite:{cf}:{sym}")
            if not ok:
                bad.append(("C2-cite", f"{cf}:{sym}"))
        for m in CALL_RE.finditer(t):
            name = m.group(1)
            parts = name.split(".")
            if len(parts[-1]) < 3:
                continue
            checks.append(f"call:{name}")
            if not all(p in toks or p in BUILTIN_OK for p in parts[-1:]):
                bad.append(("C2-call", name))
        if kind == "comment" and f.endswith(".py"):
            if f not in defs_cache.setdefault("__lit__", {}):
                try:
                    defs_cache["__lit__"][f] = literal_sizes(f, Path(f).read_text(encoding="utf-8"))
                except (OSError, UnicodeDecodeError):
                    defs_cache["__lit__"][f] = {}
            lits = defs_cache["__lit__"][f]
            end = int(line) + t.count("\n")
            hit = lits.get(end + 1) or lits.get(int(line))
            cc = count_claims(t)
            if hit and cc:
                checks.append(f"count:{hit[0]}={hit[1]}")
                if hit[1] not in {n for _, n in cc}:
                    bad.append(("C1-count", f"{hit[0]} has {hit[1]} items; comment says " + ", ".join(w for w, _ in cc)))
        if kind in ("docstring", "comment"):
            uf = usage_flags(f, t)
            if uf:
                cs = defs_cache.setdefault("__cs__", {})
                if f not in cs:
                    try:
                        cs[f] = code_strings(f, Path(f).read_text(encoding="utf-8"))
                    except (OSError, UnicodeDecodeError):
                        cs[f] = ""
                for fl in sorted(set(uf)):
                    checks.append(f"flag:{fl}")
                    if not re.search(re.escape(fl) + r"(?![a-z0-9-])", cs[f]):
                        bad.append(("C1-flag", fl))
        for s in sentences(t):
            n = len(s.split())
            if n > 40:
                checks.append(f"len:{n}")
                bad.append(("C5-len", f"{n} words: {s[:90]}"))
        dismissed = [(a, b) for a, b in bad if not confirmed(f, a, b)]
        bad = [(a, b) for a, b in bad if confirmed(f, a, b)]
        if dismissed:
            checks.append("adjudicated-ok:" + ",".join(f"{a}={b}" for a, b in dismissed))
        if checks:
            res = ";".join(checks)[:300] + " => " + ("FAIL " + ";".join(f"{a}={b}" for a, b in bad) if bad else "ok")
            truth = "; ".join(f"{a} {b}" for a, b in bad)[:300]
            rows.append((uid, line, "claim", f"python3 {Path(__file__).relative_to(Path.cwd()) if Path(__file__).is_relative_to(Path.cwd()) else __file__} --unit {uid}",
                         res.replace("\t", " ").replace("\n", " "), "false" if bad else "true", truth.replace("\t", " ").replace("\n", " ")))
        else:
            rows.append((uid, line, "no-claim", "", "", "-", ""))
        for a, b in bad:
            flags.append((uid, line, a, b))
        for a, b in dismissed:
            flags.append((uid, line, a + "-dismissed", b))
    return rows, flags


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True)
    ap.add_argument("--ref", default="92d38ecb640bd462f2e19c0814d0f0b7df1ee692")
    ap.add_argument("--seat", default="D5-s6")
    ap.add_argument("--out", default=str(HERE))
    ap.add_argument("--unit")
    ap.add_argument("--plant-symbol", action="append", default=[])
    ap.add_argument("--c5-split", action="append", default=[],
                    help="perturbation: every comment unit of FILE rewritten in memory with a full stop every 30 words")
    a = ap.parse_args()
    t0, c0 = time.process_time(), time.thread_time()
    files, dirs = tracked(a.repo, a.ref)
    seat = text_ledger.seat_files(a.seat, a.repo, a.ref)
    units = text_ledger.enumerate_units(".", seat, "D5")
    if a.c5_split:
        def rebreak(t):
            w = t.split()
            return " ".join((x[:1].upper() + x[1:] if i % 30 == 0 and i else x) + ("." if i % 30 == 29 else "")
                            for i, x in enumerate(w))
        units = [(u, l, k, rebreak(t) if u.split("#")[0] in a.c5_split else t) for u, l, k, t in units]
    toks = code_tokens(sorted(files)) | set(a.plant_symbol)
    rows, flags = scan(units, files, dirs, toks, None)
    if a.unit:
        for r in rows:
            if r[0] == a.unit:
                print("\t".join(map(str, r)))
        for fl in flags:
            if fl[0] == a.unit:
                print("FLAG", *fl)
        return
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    with open(out / "LEDGER.tsv", "w", encoding="utf-8") as fh:
        fh.write("\t".join(text_ledger.HEADER) + "\n")
        for r in rows:
            fh.write("\t".join(map(str, r)) + "\n")
    with open(out / "FLAGS.tsv", "w", encoding="utf-8") as fh:
        for fl in flags:
            fh.write("\t".join(map(str, fl)) + "\n")
    print(f"RESULT units={len(units)} count")
    print(f"RESULT claim_rows={sum(r[2] == 'claim' for r in rows)} count")
    print(f"RESULT false_rows={sum(r[5] == 'false' for r in rows)} count")
    for k in ("C1-flag", "C1-count", "C2-path", "C2-cite", "C2-call", "C5-len", "C1-flag-dismissed", "C1-count-dismissed", "C2-path-dismissed"):
        print(f"RESULT {k}={sum(f[2] == k for f in flags)} count")
    c5 = {}
    for fl in flags:
        if fl[2] == "C5-len":
            c5[fl[0].split("#")[0]] = c5.get(fl[0].split("#")[0], 0) + 1
    print(f"RESULT C5_files={len(c5)} count")
    if c5:
        vals = sorted(c5.values())
        print(f"RESULT C5_per_file_min={vals[0]} max={vals[-1]} total_drop_max_file={sum(vals) - vals[-1]} count")
    with open(out / "C5_BY_FILE.tsv", "w", encoding="utf-8") as fh:
        for k in sorted(c5):
            fh.write(f"{k}\t{c5[k]}\n")
    print(f"RESULT files_with_false={len({r[0].split('#')[0] for r in rows if r[5] == 'false'})} count")
    print(f"RESULT thread_factor={(time.process_time() - t0 + 1e-9) / (time.thread_time() - c0 + 1e-9):.2f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT swapins=0")


if __name__ == "__main__":
    main()
