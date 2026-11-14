# R10-USER-TEXT-VERIFY-CARD: classifies every file:line a round-10 user-text
# record cites, at the record's merge base, as code, comment, docstring or
# blank, and prints each row with a citation that is not code (the owner's
# ruling of 2026-11-13: text is verified against behaviour, never a comment).
#
#    python3 -I dev/audit/harnesses/r10_card_evidence_kinds.py <record.md> [base]
#
# Run from a worktree root. A row is a table line opening with a backticked
# key, read up to the record's own sweep section (whose table quotes the
# citations it replaced); a citation is `path:line` or `path:line-line` (a `~` before the line is
# read as the line). A bare path resolves under the package, its `www/`, or its
# `translations/`. Comment: a stripped line opening `#` (.py) or `//`, `*`,
# `/*` (.js, .mjs). Docstring: a line inside a bare string expression, by
# `ast`. Output: `ONLY` (no citation of the row is code) or `SOME`, the key,
# then each non-code citation with its kind; a summary on stderr.
# Counts and classifications only; no timing, no network.
import ast, re, subprocess, sys
BASE = sys.argv[2] if len(sys.argv) > 2 else "90c6bc3b0756475e28d4ace8d8e31c4788474933"
rec = sys.argv[1]
PKG = "custom_components/heatpump_optimizer/"
cache = {}
def src(path):
    if path not in cache:
        r = subprocess.run(["git", "show", f"{BASE}:{path}"], capture_output=True, text=True)
        cache[path] = r.stdout.splitlines() if r.returncode == 0 else None
    return cache[path]
doc = {}
def docranges(path):
    if path in doc: return doc[path]
    rs = set()
    try:
        t = ast.parse("\n".join(src(path)))
        for n in ast.walk(t):
            if isinstance(n, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
                b = n.body
                if b and isinstance(b[0], ast.Expr) and isinstance(getattr(b[0], "value", None), ast.Constant) and isinstance(b[0].value.value, str):
                    rs.update(range(b[0].lineno, b[0].end_lineno + 1))
            # attribute docstrings: a bare string expression anywhere
            if isinstance(n, ast.Expr) and isinstance(getattr(n, "value", None), ast.Constant) and isinstance(n.value.value, str):
                rs.update(range(n.lineno, n.end_lineno + 1))
    except Exception: pass
    doc[path] = rs; return rs
def kind(path, ln):
    lines = src(path)
    if lines is None or ln < 1 or ln > len(lines): return "missing"
    s = lines[ln - 1].strip()
    if path.endswith(".py"):
        if ln in docranges(path): return "docstring"
        if s.startswith("#"): return "comment"
        if s == "": return "blank"
        return "code"
    if path.endswith((".js", ".mjs")):
        if s.startswith(("//", "*", "/*")): return "comment"
        if s == "": return "blank"
        return "code"
    return "code"
CIT = re.compile(r"((?:/home/user/[^/\s]+/)?(?:[\w.-]+/)*[\w.-]+\.(?:py|js|mjs|json)):~?(\d+)(?:-(\d+))?")
def resolve(p):
    p = re.sub(r"^/home/user/[^/]+/", "", p)
    for cand in (p, PKG + p, PKG + "www/" + p, PKG + "translations/" + p):
        if src(cand) is not None: return cand
    return None
rows = flagged = 0
for line in open(rec):
    if line.startswith("## Comment and docstring evidence"): break  # the sweep's own table quotes the old citations
    m = re.match(r"\|\s*`([^`]+)`\s*\|", line)
    if not m: continue
    rows += 1
    kinds = []
    for c in CIT.finditer(line):
        path = resolve(c.group(1))
        if path is None: kinds.append((c.group(0), "unresolved")); continue
        a = int(c.group(2)); b = int(c.group(3) or a)
        ks = {kind(path, l) for l in range(a, min(b, a + 60) + 1)} - {"blank"}
        k = "code" if "code" in ks else ("+".join(sorted(ks)) or "blank")
        kinds.append((c.group(0), k))
    bad = [(c, k) for c, k in kinds if k not in ("code",)]
    if bad:
        flagged += 1
        allbad = all(k != "code" for _, k in kinds)
        print(f"{'ONLY' if allbad else 'SOME'}\t{m.group(1)}\t" + "; ".join(f"{c}={k}" for c, k in bad))
print(f"rows {rows} flagged {flagged}", file=sys.stderr)
