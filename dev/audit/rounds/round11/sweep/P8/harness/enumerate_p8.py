"""Class P8 seam enumerator, round 11 (D14 method step 3).

A seam of P8 is a site that RESOLVES a currency or a temperature unit -- picks
which source (feed, entity, instance, fallback) names the unit a number is in --
or converts by such a resolution. Generalises the findings' seams:
D14-s1-03 (config_flow._money/_fee_placeholders/_grid_fee_errors call the
instance-first resolve_currency) and D7-s3-01 (inputs.temperature_from_c, the
write-side inverse of normalize_temperature_c).

Families (AST scan of custom_components/heatpump_optimizer/*.py, plus a line
scan of www/heatpump-optimizer-card.js):
  CUR    a call to resolve_currency / _feed_currency / declared_currency /
         money_scale, or a read of `<x>.config.currency`
  TEMP   a call to normalize_temperature_c / temperature_from_c /
         temperature_c / _instance_unit / setpoint_unit / state_unit, or a
         use of TEMPERATURE_UNIT_TO_C outside const.py
  PRICE  a call to normalize_price_per_kwh
  CARD   a card JS line that resolves a currency (`currency(` definition or
         a `hass.config.currency` / `config.currency` read)
Definitions are not seams; calls are. One seam per (file, line, family).

Run: python3 enumerate_p8.py [--root DIR] [--fixture clean|perturbed]
--fixture clean      a module that reads one canonical resolver only -> seams=0
                     (the resolvers themselves are not listed when called
                     only from their own definition module's helper `canon`)
--fixture perturbed  the same plus one line `c = resolve_currency(hass)` -> seams=1
"""
import argparse, ast, os, re, tempfile

CUR = {"resolve_currency", "_feed_currency", "declared_currency", "money_scale"}
TEMP = {"normalize_temperature_c", "temperature_from_c", "temperature_c",
        "_instance_unit", "setpoint_unit", "state_unit"}
PRICE = {"normalize_price_per_kwh"}
CLEAN = "def canon(x):\n    return float(x)\n"
PERTURB = "def bad(hass):\n    c = resolve_currency(hass)\n    return c\n"
CARD_RE = re.compile(r"(\bcurrency\s*\([^)]*\)\s*\{|hass\.config\.currency|this\.config\.currency|config\.currency)")


def scan_py(path, rel):
    src = open(path, encoding="utf-8").read()
    tree = ast.parse(src)
    defs = [(n.lineno, n.end_lineno, n.name) for n in ast.walk(tree)
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))]
    hits = []
    for n in ast.walk(tree):
        fam = None
        if isinstance(n, ast.Call):
            f = n.func
            name = f.attr if isinstance(f, ast.Attribute) else getattr(f, "id", "")
            if name in CUR: fam = "CUR"
            elif name in TEMP: fam = "TEMP"
            elif name in PRICE: fam = "PRICE"
        elif isinstance(n, ast.Attribute) and n.attr == "currency" and isinstance(n.value, ast.Attribute) and n.value.attr == "config":
            fam = "CUR"
        elif isinstance(n, ast.Name) and n.id == "TEMPERATURE_UNIT_TO_C" and not rel.endswith("const.py") and isinstance(getattr(n, "ctx", None), ast.Load):
            fam = "TEMP"
        if fam:
            hits.append((fam, n.lineno))
    # getattr(..., "currency") reads
    for i, line in enumerate(src.splitlines(), 1):
        if re.search(r'getattr\(getattr\(hass, "config", None\), "currency"', line):
            hits.append(("CUR", i))
    out = []
    lines = src.splitlines()
    for fam, ln in sorted(set(hits), key=lambda x: (x[1], x[0])):
        if lines[ln - 1].lstrip().startswith(("from ", "import ")):
            continue
        c = sorted([d for d in defs if d[0] <= ln <= d[1]])
        out.append((fam, rel, ln, ".".join(d[2] for d in c) or "<module>", lines[ln - 1].strip()[:110]))
    return out


def scan_js(path, rel):
    out = []
    for i, line in enumerate(open(path, encoding="utf-8"), 1):
        s = line.strip()
        if s.startswith(("//", "*", "/*")):
            continue
        if CARD_RE.search(line):
            out.append(("CARD", rel, i, "card", s[:110]))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default="custom_components/heatpump_optimizer")
    ap.add_argument("--fixture", choices=["clean", "perturbed"])
    a = ap.parse_args()
    root = a.root
    if a.fixture:
        root = tempfile.mkdtemp()
        open(os.path.join(root, "fixture.py"), "w").write(CLEAN + ("\n" + PERTURB if a.fixture == "perturbed" else ""))
    seams = []
    for dp, _, fs in sorted(os.walk(root)):
        for f in sorted(fs):
            p = os.path.join(dp, f)
            rel = os.path.relpath(p, os.path.dirname(root.rstrip("/")))
            if f.endswith(".py"):
                seams += scan_py(p, rel)
            elif f == "heatpump-optimizer-card.js":
                seams += scan_js(p, rel)
    seen = set(); uniq = []
    for s in seams:
        if (s[1], s[2], s[0]) not in seen:
            seen.add((s[1], s[2], s[0])); uniq.append(s)
    for fam, rel, ln, sym, code in uniq:
        print(f"SEAM {fam} {rel}:{ln} {sym} | {code}")
    cnt = {k: sum(1 for s in uniq if s[0] == k) for k in ("CUR", "TEMP", "PRICE", "CARD")}
    print("RESULT seams=%d " % len(uniq) + " ".join(f"{k}={v}" for k, v in cnt.items()))


if __name__ == "__main__":
    main()
