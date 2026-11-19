#!/usr/bin/env python3
"""D5.M4 ledger for seat D5-s7 (tests/f*): every D5 comment unit rowed by an executed check.

Metric (one line): per file, the count of D5 units (tools/audit/text_ledger.py:units_of, dim D5)
failing C2 (a named identifier or path absent from the code of the tracked tree at the ref) or
C5 (a sentence over 40 words), after the triage overrides in triage.tsv.
Count key: the unit id text_ledger prints; a name counts as resolved when it occurs as a code
token (Python NAME/STRING tokens outside comments and docstrings, JS/shell/JSON/YAML text outside
`//` and `#` comments) of a live tracked file, never by the comment's own text.

Command:  PYTHONPATH=tests/hastub $HOME/venv-ci/bin/python3 dev/audit/rounds/round11/D5/s7/m4_comments.py \
              [--repo /home/user/heatpump_optimizer] [--ref 92d38ecb640bd462f2e19c0814d0f0b7df1ee692] \
              [--ledger OUT.tsv] [--perturb c2-define|c5-split|plant]
Expected: RESULT lines below, exact (a count over text; no timing).
Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692, box B12 (export /home/user/audit-r11-baseline).

Perturbations (in memory, no file is edited):
  c2-define   adds every unresolved name to the code-token set (as a fix defining or renaming
              would): c2_fail goes to zero.
  c5-split    re-splits every sentence at its 40th word: c5_fail goes to zero.
  fix-path    the one-line comment edit at tests/features.py:57049 (the moved partition.py's new path):
              features.py c2_fail falls by 1.
  plant       appends one comment naming a missing symbol to the first file: c2_fail rises by 1.
The writer-side null control is text_ledger.py check --plant on the ledger this writes.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS",
           "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import argparse, ast, io, re, subprocess, sys, time, tokenize
from pathlib import Path

ROOT = Path.cwd()
sys.path.insert(0, str(ROOT / "tools/audit"))
import text_ledger  # noqa: E402  (the instrument the units come from)

HERE = Path(__file__).resolve().parent
SEAT_FILES = ["tests/features.py", "tests/finite_boundary.py", "tests/frontend.py"]
LIVE = re.compile(r"^(custom_components|tests|tools|blueprints|\.claude|\.github|\.cursor|dev/audit/harnesses|dev/audit/config|dev/governance|hacs\.json|[^/]+$)")
CODE_SUF = (".py", ".js", ".mjs", ".sh", ".json", ".yaml", ".yml", ".toml", ".cfg", ".ini", ".tsv", ".html", ".css")
IDENT = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")
# Bare (un-backticked) names a comment uses as code: snake_case with an underscore, or CamelCase.
BARE = re.compile(r"(?<![\w./#-])(_?[a-z][a-z0-9]*(?:_[a-z0-9]+)+_?|_[a-z][a-z0-9_]*|[A-Z][a-z0-9]+(?:[A-Z][a-z0-9]+)+)(?:\.[A-Za-z_]\w*)*(?![\w/-])")
TICK = re.compile(r"``([^`]+)``|`([^`]+)`")
PATH = re.compile(r"(?<![\w.])((?:[\w.-]+/)+[\w.-]+\.(?:py|js|mjs|sh|json|md|yaml|yml|tsv|txt))\b")
NUM = re.compile(r"(?<![\w.#/-])(\d+\.\d+|\d{2,})(?![\w.]*[-/]\w)\s*(°C|°F|kWh|kW|W|Wh|h|s|min|%|K|L|l|litres?|degC|C|ms|days?|steps?)?(?![\w])")
CONV = (1, 60, 3600, 4, 1000, 100, 24, 0.25, 96)
PRAGMA = re.compile(r"^\s*(noqa|type:|pragma|fmt:|pylint|isort|nosec|pyright|mypy)", re.I)


def tracked(repo, ref):
    return subprocess.check_output(["git", "-C", repo, "ls-tree", "-r", "--name-only", ref], text=True).split("\n")


def py_code_tokens(text):
    out = set()
    try:
        tree = ast.parse(text)
        doc_lines = set()
        for n in ast.walk(tree):
            if isinstance(n, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) and n.body:
                f = n.body[0]
                if isinstance(f, ast.Expr) and isinstance(f.value, ast.Constant) and isinstance(f.value.value, str):
                    doc_lines.add(f.lineno)
        for tok in tokenize.generate_tokens(io.StringIO(text).readline):
            if tok.type == tokenize.NAME:
                out.add(tok.string)
            elif tok.type == tokenize.STRING and tok.start[0] not in doc_lines:
                out.update(IDENT.findall(tok.string))
            elif tok.type == tokenize.FSTRING_MIDDLE if hasattr(tokenize, "FSTRING_MIDDLE") else False:
                out.update(IDENT.findall(tok.string))
    except (SyntaxError, tokenize.TokenError, ValueError):
        out.update(IDENT.findall(text))
    return out


def other_code_tokens(path, text):
    if path.endswith((".js", ".mjs")):
        text = re.sub(r"/\*.*?\*/", " ", text, flags=re.S)
        text = re.sub(r"(?m)(^|[\s;{}(])//[^\n]*", " ", text)
    elif path.endswith((".sh", ".yaml", ".yml", ".toml", ".cfg", ".ini")):
        text = re.sub(r"(?m)(^|\s)#[^\n!{]*$", " ", text)
    return set(IDENT.findall(text))


def code_universe(root, files):
    names, paths = set(), set()
    for f in files:
        if not f:
            continue
        paths.add(f)
        parts = f.split("/")
        for i in range(1, len(parts)):
            paths.add("/".join(parts[:i]))
        if not LIVE.match(f) or not f.endswith(CODE_SUF):
            continue
        try:
            t = (root / f).read_text(encoding="utf-8")
        except (UnicodeDecodeError, FileNotFoundError, IsADirectoryError):
            continue
        names |= py_code_tokens(t) if f.endswith(".py") else other_code_tokens(f, t)
    return names, paths


def body(kind, t):
    if kind == "docstring":
        return t
    return "\n".join(re.sub(r"^\s*#\s?", "", l) for l in t.splitlines())


def refs(text):
    """(names, paths) a unit names as code."""
    names, paths = set(), set(PATH.findall(text))
    plain = TICK.sub(" ", text)
    for a, b in TICK.findall(text):
        span = a or b
        if "/" in span and PATH.search(span):
            paths |= set(PATH.findall(span)); continue
        if " " in span.strip() and not re.match(r"^[\w.]+\(", span.strip()):
            # an expression: its dotted names that look like code
            names |= {m.group(0) for m in BARE.finditer(span)}
            continue
        m = re.match(r"^\s*([A-Za-z_][\w.]*)", span)
        if m and len(m.group(1)) >= 3:
            names.add(m.group(1).rstrip("."))
    names |= {m.group(0) for m in BARE.finditer(plain)}
    return names, paths


def resolve(name, universe):
    parts = [p for p in name.split(".") if p]
    return all(p in universe for p in parts)


SEP = re.compile(r"^\s*(?:[-=#*~_]{3,}.*|.*[-=]{4,}\s*)$")
BULLET = re.compile(r"^\s*(?:[*+]|-(?!-)|\d+[.)])\s+")


def paragraphs(kind, raw, src_lines, line):
    """A unit's prose split where a reader sees a break: a blank or rule line, a list item, a
    heading rule, and (for a comment block) each trailing comment on its own code line."""
    if kind == "docstring":
        lines = raw.splitlines()
        trailing = [False] * len(lines)
    else:
        lines = raw.splitlines()
        trailing = [bool(src_lines[line - 1 + i].split("#")[0].strip()) if line - 1 + i < len(src_lines) else False
                    for i in range(len(lines))]
        lines = [re.sub(r"^\s*#\s?", "", l) for l in lines]
    out, cur = [], []
    for l, tr in zip(lines, trailing):
        if tr or not l.strip() or SEP.match(l) or BULLET.match(l):
            if cur:
                out.append(" ".join(cur)); cur = []
            if tr or SEP.match(l):
                out.append(l); continue
        if l.strip():
            cur.append(l)
    if cur:
        out.append(" ".join(cur))
    return out


def long_sentences(paras, cap=40):
    return [s for p in paras for s in text_ledger.sentences(p) if len(s.split()) > cap]


def code_numbers(text):
    """{line: numeric literals} of a file's code: NUMBER tokens and the digits inside string tokens."""
    nums = {}
    for tok in tokenize.generate_tokens(io.StringIO(text).readline):
        if tok.type == tokenize.NUMBER:
            try:
                nums.setdefault(tok.start[0], set()).add(float(eval(tok.string.replace("_", ""))))
            except Exception:
                pass
        elif tok.type == tokenize.STRING:
            for d in re.findall(r"\d+\.?\d*", tok.string):
                nums.setdefault(tok.start[0], set()).add(float(d))
    return nums


def number_candidates(t, line, nums):
    """C7/C1n: a cited decimal or unit-bearing number with no code literal (or a x60, x3600, x4,
    x1000, x100, x24, x0.25, x96 conversion of one) from 40 lines above to 120 below the unit."""
    n = t.count("\n") + 1
    window = set().union(*[nums.get(i, set()) for i in range(max(1, line - 40), line + n + 120)])
    out = []
    for m in NUM.finditer(t):
        d = m.group(1)
        if not m.group(2) and "." not in d:
            continue
        v = float(d)
        if any(abs(v - w * k) <= 1e-6 * max(1, abs(v)) or abs(v * k - w) <= 1e-6 * max(1, abs(w))
               for w in window for k in CONV):
            continue
        out.append(d + (m.group(2) or ""))
    return out


def load_triage():
    p = HERE / "triage.tsv"
    out = {}
    if p.exists():
        for l in p.read_text().splitlines():
            if l.strip() and not l.startswith("#"):
                uid, crit, name, verdict, why = (l.split("\t") + ["", "", "", ""])[:5]
                out[(uid, crit, name)] = (verdict, why)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default="/home/user/heatpump_optimizer")
    ap.add_argument("--ref", default="92d38ecb640bd462f2e19c0814d0f0b7df1ee692")
    ap.add_argument("--ledger")
    ap.add_argument("--detail")
    ap.add_argument("--perturb", choices=["c2-define", "c5-split", "plant", "fix-path"])
    a = ap.parse_args()
    t0 = time.process_time()
    files = tracked(a.repo, a.ref)
    universe, paths = code_universe(ROOT, files)
    triage = load_triage()
    texts = {f: (ROOT / f).read_text(encoding="utf-8") for f in SEAT_FILES}
    if a.perturb == "fix-path":
        texts[SEAT_FILES[0]] = texts[SEAT_FILES[0]].replace("tools/audit/w5-partition/partition.py",
                                                            "tools/coverage/partition.py")
    if a.perturb == "plant":
        f0 = SEAT_FILES[0]
        texts[f0] += "\n# Planted: `_planted_missing_symbol_r11` never exists.\n"
    src = {f: texts[f].splitlines() for f in SEAT_FILES}
    numbers = {f: code_numbers(texts[f]) for f in SEAT_FILES}
    units = [u for f in SEAT_FILES for u in text_ledger.units_of(f, texts[f], "D5")]
    rows, per_file, detail = [], {}, []
    cap = 10 ** 9 if a.perturb == "c5-split" else 40
    for uid, line, kind, t in units:
        f = uid.split("#")[0]
        pf = per_file.setdefault(f, {"units": 0, "claim": 0, "no_claim": 0, "c2_fail": 0, "c5_fail": 0,
                                     "c2_names": 0, "c2_names_unresolved": 0, "issue_refs": 0,
                                     "c1_fail": 0, "num_cited": 0, "num_candidates": 0,
                                     "num_candidate_units": 0, "false_rows": 0, "unverifiable_rows": 0})
        pf["units"] += 1
        b = body(kind, t)
        prose = text_ledger.WORDS.findall(b)
        if PRAGMA.match(b.strip()) or len(prose) < 2 or not re.search(r"[A-Za-z]{2,}\s+[A-Za-z]{2,}", b):
            pf["no_claim"] += 1
            rows.append([uid, str(line), "no-claim", "", "", "-", ""])
            continue
        pf["claim"] += 1
        names, ps = refs(b)
        bad_n = sorted(n for n in names if not resolve(n, universe))
        bad_p = sorted(p for p in ps if p not in paths and not any(x.endswith("/" + p) for x in paths if p.count("/") >= 1 and x.endswith(p)))
        if a.perturb == "c2-define":
            universe |= {p for n in bad_n for p in n.split(".")}
            paths |= set(bad_p)
            bad_n, bad_p = [], []
        pf["c2_names"] += len(names) + len(ps)
        pf["issue_refs"] += len(re.findall(r"(?<![\w&])#\d{2,5}\b", b))
        fails = []
        for n in bad_n + bad_p:
            v = triage.get((uid, "C2", n))
            if v and v[0] == "resolves":
                continue
            fails.append(("C2", n))
        for (tu, crit, name), (verdict, why) in triage.items():
            if tu == uid and crit == "C1" and verdict == "false":
                fails.append(("C1", f"{name} ({why})"))
        pf["num_cited"] += sum(1 for m in NUM.finditer(t) if m.group(2) or "." in m.group(1))
        cands = [c for c in number_candidates(t, line, numbers[f])
                 if triage.get((uid, "C1n", c), ("",))[0] not in ("true", "resolves")]
        pf["num_candidates"] += len(cands)
        pf["num_candidate_units"] += bool(cands)
        longs = long_sentences(paragraphs(kind, t, src[f], line), cap)
        for s in longs:
            fails.append(("C5", f"{len(s.split())} words: {s[:90]}"))
        c2 = [x for x in fails if x[0] == "C2"]
        c5 = [x for x in fails if x[0] == "C5"]
        pf["c2_names_unresolved"] += len(c2)
        pf["c2_fail"] += bool(c2)
        pf["c5_fail"] += bool(c5)
        pf["c1_fail"] += any(x[0] == "C1" for x in fails)
        cmd = f"m4_comments.py --detail OUT ({uid})"
        res = f"names={len(names)} paths={len(ps)} unresolved={[x[1] for x in c2]} long={len(c5)}"
        res += f" untriaged_numbers={cands}"
        if fails:
            pf["false_rows"] += 1
            truth = "; ".join(f"{c}: {n}" for c, n in fails)[:400]
            rows.append([uid, str(line), "claim", cmd, res.replace("\t", " "), "false", truth.replace("\t", " ")])
            detail.append(f"{uid}\t{line}\t" + truth.replace("\t", " "))
        elif cands:
            pf["unverifiable_rows"] += 1
            rows.append([uid, str(line), "claim", cmd, res.replace("\t", " "), "unverifiable",
                         ("cited numbers with no adjacent code literal, not triaged: " + ", ".join(cands))[:400]])
            detail.append(f"{uid}\t{line}\tC1n: " + ", ".join(cands))
        else:
            rows.append([uid, str(line), "claim", cmd, res.replace("\t", " "), "true", ""])
    if a.ledger:
        Path(a.ledger).write_text("\t".join(text_ledger.HEADER) + "\n" + "\n".join("\t".join(r) for r in rows) + "\n")
    if a.detail:
        Path(a.detail).write_text("\n".join(detail) + "\n")
    tot = {}
    for f, pf in per_file.items():
        for k, v in pf.items():
            print(f"RESULT {f}:{k}={v} count")
            tot[k] = tot.get(k, 0) + v
    for k, v in tot.items():
        print(f"RESULT total:{k}={v} count")
    print(f"RESULT code_names={len(universe)} count")
    cpu = time.process_time() - t0
    try:
        import resource
        sw = resource.getrusage(resource.RUSAGE_SELF).ru_nswap
    except Exception:
        sw = 0
    print(f"RESULT thread_factor={cpu / max(time.thread_time(), 1e-9):.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print(f"RESULT swapins={sw}")


if __name__ == "__main__":
    main()
