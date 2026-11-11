"""D5-s3 M4: backticked identifiers named in comments/docstrings of
custom_components/heatpump_optimizer/*.py that exist nowhere in the code.

Metric: count of (module, identifier) pairs where a `snake_or_Camel` identifier
written in backticks (optionally `mod.py:sym`, `obj.attr`, `f()`) inside a comment
or docstring of a production module matches no identifier token in the non-comment
code of custom_components/ or tests/. Count key: the identifier string as written in the
production comment (a fix renames the comment or the code; either moves it).
Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round10/D5/s3/comment_symbols.py [--perturb]
--perturb: drops the identifier `async_setup_entry` from the code-token set (simulating a
rename of that production symbol); count must rise.
Expected: see RESULT (exact, deterministic). Baseline 17f1c55fad1b, machine: macOS arm64 (B3).
"""
import os
for _v in ("OMP_NUM_THREADS","OPENBLAS_NUM_THREADS","MKL_NUM_THREADS","NUMEXPR_NUM_THREADS","VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import glob, io, re, sys, time, tokenize, ast
t0p, t0t = time.process_time(), time.thread_time()
PKG = "custom_components/heatpump_optimizer"
ID = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")
TICK = re.compile(r"``?([A-Za-z_][A-Za-z0-9_.:/]*)(?:\(\))?``?")

def split(path):
    src = open(path, encoding="utf-8").read()
    comments, code = [], set()
    doc_nodes = set()
    tree = ast.parse(src)
    for n in ast.walk(tree):
        if isinstance(n, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            if n.body and isinstance(n.body[0], ast.Expr) and isinstance(getattr(n.body[0], "value", None), ast.Constant) and isinstance(n.body[0].value.value, str):
                doc_nodes.add(n.body[0].lineno)
                comments.append((n.body[0].lineno, n.body[0].value.value))
    for tok in tokenize.generate_tokens(io.StringIO(src).readline):
        if tok.type == tokenize.COMMENT:
            comments.append((tok.start[0], tok.string))
        elif tok.type == tokenize.NAME:
            code.add(tok.string)
        elif tok.type == tokenize.STRING and tok.start[0] not in doc_nodes:
            code.update(ID.findall(tok.string))  # string literals (keys, entity ids)
    return comments, code

code_ids = set()
prod = sorted(glob.glob(PKG + "/*.py"))
per = {}
for p in prod + sorted(glob.glob("tests/*.py")) + sorted(glob.glob("tools/**/*.py", recursive=True)):
    try:
        c, k = split(p)
    except Exception:
        continue
    code_ids |= k
    if p in prod:
        per[p] = c
for p in glob.glob(PKG + "/www/*.js") + glob.glob("tests/*.mjs"):
    code_ids |= set(ID.findall(open(p, encoding="utf-8").read()))
for p in glob.glob(PKG + "/*.json") + glob.glob(PKG + "/*.yaml"):
    code_ids |= set(ID.findall(open(p, encoding="utf-8").read()))
if "--perturb" in sys.argv:
    code_ids.discard("async_setup_entry")

# Triaged by reading each hit: names that live outside this repository
# (Home Assistant, numpy, Nord Pool, device payloads, example entity ids), math
# notation, or a sentence saying the name does NOT exist. Not counted.
EXTERNAL = {"input_boolean.holiday_mode", "PW_BLOCKSIZE", "__float__", "_async_configure",
    "homeassistant.util.loop.protect_loop", "sensor.hp_t4", "fault_description", "HH",
    "price_in_cents", "compressorFrequency", "current_option", "has_value", "UPPER_FLOOR_TEMP",
    "sensor.heat_pump_optimizer_upper_floor_temperature", "T_prev", "a_ii", "savings_",
    "coordinator_methods", "_ecl110_topic", "MixedHotWater",
    "dev/audit/harnesses/draw_range_evidence.py", "dev/audit/harnesses/early_cutoff_closed_loop.py",
    "tools/gen_gchv_package.py"}
missing = []
for p, cs in per.items():
    for line, text in cs:
        for m in TICK.finditer(text):
            ref = m.group(1).rstrip(".")
            parts = [x for x in re.split(r"[.:/]", ref) if x and x not in ("py", "js", "json", "mjs", "md")]
            if not parts:
                continue
            sym = parts[-1]
            if not ID.fullmatch(sym) or ("_" not in sym and not any(ch.isupper() for ch in sym[1:])):
                continue  # plain English word, not an identifier
            if sym not in code_ids:
                missing.append((p, line, ref))
for p, line, ref in missing:
    print(f"{'external' if ref in EXTERNAL else 'MISSING '} {p}:{line} `{ref}`")
untriaged = [m for m in missing if m[2] not in EXTERNAL]
print(f"RESULT comment_symbols_untriaged_missing={len(untriaged)} count")
print(f"RESULT comment_symbols_missing={len(missing)} count")
print(f"RESULT modules_scanned={len(per)} count")
pc, tc = time.process_time() - t0p, time.thread_time() - t0t
print(f"RESULT thread_factor={pc/tc if tc else 1.0:.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
print("RESULT swapins=0")
