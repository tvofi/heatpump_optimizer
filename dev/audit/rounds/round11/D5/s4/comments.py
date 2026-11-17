#!/usr/bin/env python3
"""D5-s4 M4 instrument: executed mechanical checks of every D5 comment unit in the seat's cells.

Measures, per comment unit text_ledger.py lists for D5-s4 (custom_components/heatpump_optimizer/
{j..z}*.py and www/*.js), four checks against the CODE of the tree, never against another comment:
  C2  unresolved = a name the unit cites (``x``, `x`, snake_case, name(), a.b) that occurs in no
      code token of any tracked file (Python NAME/STRING tokens, JS/JSON/YAML/shell text with
      comments stripped) and is no tracked path, builtin or stdlib/numpy/scipy attribute.
      Count key: the cited token against the production code token set.
  C5  long = a sentence of the unit over 40 words (text_ledger.sentences on the comment text).
  C7  num = a comment block sitting directly on `NAME = <numeric literal>` that cites numbers,
      none of which equals the literal's value under a unit factor (1, 60, 3600, 86400, 24, 1440,
      100, 1000 and their inverses). Count key: the value ast evaluates from the production line.
  C4  hist = a unit with >=2 sentences where more than half match the history pattern (round
      ids, finding ids, issue numbers, "used to", "previously", "was measured" ...).
Run:   PYTHONPATH=tests/hastub /root/venv-ci/bin/python3 dev/audit/rounds/round11/D5/s4/comments.py
           [--repo /home/user/heatpump_optimizer --ref 92d38ecb...] [--file PATH] [--tsv OUT]
           [--edit 'PATH|OLD|NEW']   (in-memory one-line production edit; the perturbation)
Expected at the baseline (exact, counts): units=3367 unresolved_units=18 (raw; 2 survive hand triage, both
  sysid.py) long_units=558 hist_units=43 num_units=42 (raw; 0 survive py_numbers.py/card_numbers.mjs).
  Perturbation: --file custom_components/heatpump_optimizer/sysid.py --edit
  'custom_components/heatpump_optimizer/sysid.py|through prior_rel = prior_w / data_w.|through prior_rel = s_noise / prior_sd.'
  moves unresolved_units 2 -> 1; --file .../pump_mode.py --edit '...pump_mode.py|the mode — reads its answer from
  here, so there is|the mode. All read their answer from here, so there is' moves long_units 3 -> 2.
  The wall/cpu line is provisional.
Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box B11 (4 vCPU container).
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS",
           "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import argparse, ast, builtins, io, json, keyword, re, subprocess, sys, time, tokenize
from pathlib import Path

sys.path.insert(0, "tools/audit")
import text_ledger as TL  # noqa: E402

BASE = "92d38ecb640bd462f2e19c0814d0f0b7df1ee692"
SEAT = "D5-s4"
IDENT = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")
BACKTICK = re.compile(r"``([^`]+)``|`([^`\n]+)`")
SNAKE = re.compile(r"(?<![\w./-])_*[a-z][a-z0-9]*(?:_[a-z0-9]+)+\b(?:\(\))?")
CALL = re.compile(r"(?<![\w.])([A-Za-z_]\w*)\(\)")
DOTTED = re.compile(r"(?<![\w./])([A-Za-z_]\w*(?:\.[A-Za-z_]\w*)+)(?:\(\))?")
NUM = re.compile(r"(?<![\w.#-])(-?\d+(?:\.\d+)?)(?![\w.]*\d)")
HIST = re.compile(r"\bround[- ]?\d+|\bR\d+[-.]\w|\bD\d{1,2}-(?:s\d+-)?\d{2}\b|#\d{3,}|\bused to\b|\bpreviously\b|"
                  r"\bformerly\b|\bwas measured\b|\bmeasured (?:on|at|in) (?:round|the)|\bno longer\b|\buntil v?\d|"
                  r"\bsince v?\d|\bv\d+\.\d+\.\d+|\bthe old\b|\bused instead\b|\bthe fix\b|\bregress", re.I)
FACTORS = (1, 60, 3600, 86400, 24, 1440, 100, 1000, 7, 168, 10080)
STDMODS = ("math", "numpy", "scipy.optimize", "datetime", "asyncio", "time", "json", "re", "os", "logging",
           "statistics", "itertools", "functools", "collections", "dataclasses", "typing", "concurrent.futures",
           "multiprocessing", "pathlib", "zoneinfo", "enum", "random", "bisect", "heapq", "hashlib", "copy")
ENTITY_DOMAINS = ("sensor", "switch", "number", "select", "binary_sensor", "button", "climate", "water_heater",
                  "input_number", "input_boolean", "homeassistant", "persistent_notification", "hass", "self",
                  "heatpump_optimizer", "this", "state", "attrs", "attributes", "config", "entry", "data",
                  "options", "plan", "cfg", "card", "window", "document", "Math", "Number", "Array", "Object",
                  "JSON", "Date", "String", "console", "customElements", "np")


def tracked(repo, ref):
    return subprocess.check_output(["git", "-C", repo, "ls-tree", "-r", "--name-only", ref], text=True).split()


def strip_js_comments(text):
    return re.sub(r"/\*.*?\*/|(?<![:\\\"'])//[^\n]*", " ", text, flags=re.S)


def code_tokens(root, files):
    """Every identifier-like token of the code (comments removed), and every tracked path."""
    toks = set()
    for f in files:
        p = Path(root) / f
        try:
            text = p.read_text(encoding="utf-8")
        except (UnicodeDecodeError, FileNotFoundError, IsADirectoryError):
            continue
        suf = p.suffix.lower()
        if suf == ".py":
            try:
                for t in tokenize.generate_tokens(io.StringIO(text).readline):
                    if t.type == tokenize.NAME:
                        toks.add(t.string)
                    elif t.type in (tokenize.STRING, getattr(tokenize, "FSTRING_MIDDLE", -1)):
                        toks.update(IDENT.findall(t.string)); toks.update(re.findall(r"[\w.-]+", t.string))
            except (tokenize.TokenError, SyntaxError, IndentationError):
                toks.update(IDENT.findall(text))
        elif suf in (".js", ".mjs", ".ts"):
            body = strip_js_comments(text)
            toks.update(IDENT.findall(body)); toks.update(re.findall(r"[\w.-]+", body))
        elif suf in (".json", ".yaml", ".yml", ".sh", ".toml", ".cfg", ".ini", ".txt", ".html", ".css", ".tsv"):
            body = re.sub(r"(?m)^\s*#.*$", " ", text) if suf in (".sh", ".yaml", ".yml") else text
            toks.update(IDENT.findall(body)); toks.update(re.findall(r"[\w.-]+", body))
        toks.add(f); toks.add(Path(f).name); toks.add(Path(f).stem)
        for parent in Path(f).parents:
            toks.add(str(parent)); toks.add(str(parent) + "/")
    return toks


def _external(name):
    if hasattr(builtins, name) or keyword.iskeyword(name):
        return True
    for m in STDMODS:
        try:
            mod = __import__(m, fromlist=["_"])
        except Exception:  # noqa: BLE001 -- an absent module resolves nothing
            continue
        if hasattr(mod, name):
            return True
    return False


def resolves(tok, corpus):
    t = tok.strip().rstrip("()").rstrip(":,;.")
    if not t or t in corpus:
        return True
    if not IDENT.fullmatch(t.replace(".", "").replace("/", "").replace("-", "")[:1] + "x") and not IDENT.match(t):
        return True
    if "/" in t or t.endswith((".py", ".js", ".json", ".md", ".mjs", ".sh")):
        return t in corpus or t.rstrip("/") in corpus or Path(t).name in corpus
    if "." in t:
        parts = t.split(".")
        if parts[0] in ENTITY_DOMAINS or parts[0] in STDMODS:
            return all(p in corpus or _external(p) or p in ENTITY_DOMAINS for p in parts[1:]) or parts[-1] in corpus
        return all(p in corpus or _external(p) for p in parts)
    return _external(t)


def cited(text):
    """Names a unit cites: backticked single names, snake_case words, name(), dotted names."""
    out = []
    for m in BACKTICK.finditer(text):
        s = (m.group(1) or m.group(2)).strip()
        if re.fullmatch(r"[A-Za-z_][\w.]*(\(\))?", s) and ("_" in s or "." in s or s.endswith("()")
                                                          or re.search(r"[a-z][A-Z]", s)):
            out.append(s)
    plain = BACKTICK.sub(" ", text)
    plain = re.sub(r"https?://\S+", " ", plain)
    out += [m.group(0) for m in SNAKE.finditer(plain)]
    out += [m.group(1) + "()" for m in CALL.finditer(plain)]
    out += [m.group(1) for m in DOTTED.finditer(plain)
            if not re.fullmatch(r"(e\.g|i\.e|etc|vs|cf)\b.*", m.group(1)) and not m.group(1)[0].isdigit()]
    seen, res = set(), []
    for s in out:
        if s not in seen:
            seen.add(s); res.append(s)
    return res


def clean(text, kind):
    if kind == "docstring":
        return text
    lines = []
    for ln in text.splitlines():
        ln = re.sub(r"^\s*(#:?|//+|/\*+|\*+/?)\s?", "", ln)
        lines.append(re.sub(r"\*/\s*$", "", ln))
    return "\n".join(lines)


def const_value(line_text):
    m = re.match(r"\s*(?:export\s+)?(?:const\s+|let\s+|var\s+)?([A-Za-z_]\w*)\s*(?::\s*[\w\[\], .]+)?\s*=\s*([^#\n]+?)\s*(?:#.*|//.*)?;?\s*$", line_text)
    if not m:
        return None, None
    expr = m.group(2).rstrip(";").replace("_", "")
    try:
        node = ast.parse(expr, mode="eval")
        ok = (ast.Expression, ast.Constant, ast.BinOp, ast.UnaryOp, ast.operator, ast.unaryop)
        if not all(isinstance(n, ok) for n in ast.walk(node)):
            return None, None
        v = eval(compile(node, "<c>", "eval"), {"__builtins__": {}}, {})  # nodes checked: literal arithmetic only
    except Exception:  # noqa: BLE001
        return None, None
    if isinstance(v, bool) or not isinstance(v, (int, float)):
        return None, None
    return m.group(1), float(v)


def numeric_mismatch(unit_line, kind, text, lines):
    """C7: the value of the NAME = number line the comment block sits on, and the numbers it cites."""
    if kind != "comment":
        return None
    n_lines = text.count("\n") + 1
    cands = []
    first = lines[unit_line - 1] if 0 < unit_line <= len(lines) else ""
    if not first.lstrip().startswith(("#", "//")):     # trailing comment on the line itself
        cands.append(first)
    else:
        nxt = unit_line - 1 + n_lines
        if nxt < len(lines):
            cands.append(lines[nxt])
    for c in cands:
        name, val = const_value(re.sub(r"(#|//).*$", "", c))
        if name is None:
            continue
        body = clean(text, kind)
        nums = [float(x) for x in NUM.findall(body.replace(",", ""))]
        nums = [x for x in nums if x not in (0.0,)]
        if not nums:
            return None
        for x in nums:
            for f in FACTORS:
                for y in (x * f, x / f):
                    if abs(y - val) <= 1e-9 * max(1.0, abs(val)) or abs(-y - val) <= 1e-9 * max(1.0, abs(val)):
                        return None
        return {"name": name, "value": val, "cited": nums}
    return None


def check_units(root, files, edits):
    corpus_files = tracked(ARGS.repo, ARGS.ref)
    corpus = code_tokens(root, corpus_files)
    rows = []
    for f in files:
        text = TL.read(root, f)
        for path, old, new in edits:
            if path == f:
                assert old in text, f"edit target not found in {f}: {old!r}"
                text = text.replace(old, new, 1)
        lines = text.splitlines()
        cursor = 0
        for uid, line, kind, utext in TL.units_of(f, text, "D5"):
            # text_ledger's JS line drifts past unterminated quotes (ledger_lines.py): relocate it.
            first = utext.splitlines()[0].strip() if utext.strip() else ""
            real = next((i + 1 for i in range(cursor, len(lines)) if first and first in lines[i]), None)
            if real is not None and f.endswith(".js"):
                line = real
            cursor = max(cursor, (real or line) - 1)
            body = clean(utext, kind)
            unresolved = [c for c in cited(body) if not resolves(c, corpus)]
            sents = TL.sentences(body)
            long_ = [s for s in sents if len(s.split()) > 40]
            hist = [s for s in sents if HIST.search(s)]
            histflag = len(sents) >= 2 and len(hist) * 2 > len(sents)
            num = numeric_mismatch(line, kind, utext, lines)
            rows.append({"unit": uid, "file": f, "line": line, "kind": kind, "unresolved": unresolved,
                         "long": [len(s.split()) for s in long_], "hist": histflag,
                         "hist_n": f"{len(hist)}/{len(sents)}", "num": num})
    return rows


def main():
    global ARGS
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default="/home/user/heatpump_optimizer")
    ap.add_argument("--ref", default=BASE)
    ap.add_argument("--root", default=".")
    ap.add_argument("--file", action="append")
    ap.add_argument("--tsv")
    ap.add_argument("--json")
    ap.add_argument("--edit", action="append", default=[], help="PATH|OLD|NEW, in memory")
    ARGS = ap.parse_args()
    t0, c0 = time.perf_counter(), time.process_time()
    files = ARGS.file or TL.seat_files(SEAT, ARGS.repo, ARGS.ref)
    edits = [tuple(e.split("|", 2)) for e in ARGS.edit]
    rows = check_units(ARGS.root, files, edits)
    if ARGS.tsv:
        with open(ARGS.tsv, "w") as fh:
            fh.write("unit\tline\tkind\tunresolved\tlong\thist\tnum\n")
            for r in rows:
                fh.write(f"{r['unit']}\t{r['line']}\t{r['kind']}\t{','.join(r['unresolved'])}\t"
                         f"{','.join(map(str, r['long']))}\t{r['hist_n'] if r['hist'] else ''}\t"
                         f"{json.dumps(r['num']) if r['num'] else ''}\n")
    if ARGS.json:
        Path(ARGS.json).write_text(json.dumps(rows))
    per = {}
    for r in rows:
        d = per.setdefault(r["file"], {"units": 0, "unresolved": 0, "long": 0, "hist": 0, "num": 0})
        d["units"] += 1
        d["unresolved"] += bool(r["unresolved"]); d["long"] += bool(r["long"])
        d["hist"] += r["hist"]; d["num"] += bool(r["num"])
    for f, d in sorted(per.items()):
        print(f"FILE {f} " + " ".join(f"{k}={v}" for k, v in d.items()))
    print(f"RESULT units={len(rows)} count")
    for k in ("unresolved", "long", "hist", "num"):
        print(f"RESULT {k}_units={sum(d[k] for d in per.values())} count")
    print(f"RESULT unresolved_tokens={sum(len(r['unresolved']) for r in rows)} count")
    cpu = time.process_time() - c0
    thread_cpu = time.thread_time()
    print(f"RESULT thread_factor={(time.process_time() / thread_cpu) if thread_cpu else 1.0:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    try:
        swp = [l for l in open("/proc/vmstat") if l.startswith("pswpin")][0].split()[1]
    except (OSError, IndexError):
        swp = "na"
    print(f"RESULT swapins={swp}")
    print(f"RESULT wall={time.perf_counter() - t0:.1f} s provisional cpu={cpu:.1f}")


if __name__ == "__main__":
    main()
