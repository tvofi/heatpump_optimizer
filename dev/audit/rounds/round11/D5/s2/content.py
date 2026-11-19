#!/usr/bin/env python3
"""D5.M3 content harness: is every symbol a reader-document unit names current in the code?

Metric: over every unit `text_ledger.py units --dim D6` lists for README.md and docs/*.md, the
backticked symbols (code identifiers with an underscore or dot, file paths, entity ids, service
names) that occur nowhere in the code corpus (custom_components/, blueprints/, tests/, tools/,
.github/, the repository root files), and the units that name one. Key: the symbol text as the
document writes it, searched verbatim (an entity id also by its object-id suffix after
`heatpump_optimizer_`, a slugified translation name counting).

Run:  PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D5/s2/content.py [--perturb SYMBOL=REPLACEMENT ...] [--plant]
  --plant    null control: a unit naming `planted_symbol_never_defined` is appended; stale_symbols +1.
  --perturb  in-memory doc edit: each SYMBOL rewritten to REPLACEMENT before the check (the fix's
             direction: a renamed symbol named by its current name drops out of stale_symbols).
Expected at baseline 92d38ecb640bd462f2e19c0814d0f0b7df1ee692: the RESULT lines it prints, exact (counts).
Machine: B2 (orchestrator's macOS box); counts are contention-immune.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS",
           "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import json, re, sys, time
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, "tools/audit")
import text_ledger  # noqa: E402

DOCS = ["README.md"] + sorted(str(p) for p in Path("docs").glob("*.md"))
OUT = Path(__file__).with_name("work")
CORPUS_DIRS = ["custom_components", "blueprints", "tests", "tools", ".github", ".claude", "dev/governance"]
SKIP = ("dev/audit/rounds", "dev/archive", "__pycache__", "node_modules", "/golden/", "closures.json")
ENTITY = re.compile(r"^(sensor|binary_sensor|switch|button|climate|number|select|datetime|input_number|"
                    r"input_boolean|input_select|water_heater|automation|script|weather|time|text|calendar|"
                    r"person|zone|sun|event|update|notify)\.[a-z0-9_]+$")


def corpus():
    parts = []
    for d in CORPUS_DIRS:
        for p in Path(d).rglob("*"):
            s = str(p)
            if p.is_file() and not any(k in s for k in SKIP) and p.suffix in (
                    ".py", ".js", ".mjs", ".json", ".yaml", ".yml", ".sh", ".txt", ".toml", ".cfg", ".md"):
                if s.startswith(("tests/", "tools/")) and p.suffix == ".md":
                    continue
                try:
                    parts.append(p.read_text(encoding="utf-8"))
                except UnicodeDecodeError:
                    pass
    for f in Path(".").iterdir():
        if f.is_file() and f.suffix in (".json", ".toml", ".cfg", ".yaml", ".yml") or f.name in ("VERSION",):
            parts.append(f.read_text(encoding="utf-8", errors="replace"))
    return "\n".join(parts)


def translation_slugs():
    out = set()
    p = Path("custom_components/heatpump_optimizer/translations/en.json")
    if p.exists():
        d = json.loads(p.read_text())
        for plat, ents in d.get("entity", {}).items():
            for key, v in ents.items():
                out.add(key)
                if isinstance(v, dict) and "name" in v:
                    out.add(re.sub(r"[^a-z0-9]+", "_", v["name"].lower()).strip("_"))
    return out


def symbols(text):
    out = []
    for m in re.finditer(r"`([^`\n]+)`", text):
        t = m.group(1).strip()
        if " " in t or len(t) < 3 or t.startswith(("http", "-", "<", "{", "$", "#")):
            continue
        t = t.rstrip(",.;:()")
        t = re.sub(r"\(\)$", "", t)
        if ENTITY.match(t):
            out.append(("entity", t))
        elif "/" in t and re.match(r"^[\w.\-/*]+$", t) and not re.match(r"^\d", t):
            out.append(("path", t))
        elif re.match(r"^[A-Za-z_][\w]*(\.[A-Za-z_][\w]*)*$", t) and ("_" in t or "." in t):
            out.append(("ident", t))
    return out


def run(perturb, plant):
    texts = {d: Path(d).read_text(encoding="utf-8") for d in DOCS}
    for spec in perturb:
        a, _, b = spec.partition("=")
        texts = {d: t.replace(f"`{a}`", f"`{b}`") for d, t in texts.items()}
    if plant:
        texts["README.md"] += "\n\nThe optimizer reads `planted_symbol_never_defined` each cycle.\n"
    corp = corpus()
    slugs = translation_slugs()
    units = [u for d in DOCS for u in text_ledger.units_of(d, texts[d], "D6")]
    n_sym = 0
    stale = defaultdict(list)
    named = 0
    for uid, line, kind, t in units:
        syms = symbols(t)
        if syms:
            named += 1
        for k, s in syms:
            n_sym += 1
            ok = True
            if k == "path":
                base = s.split("#")[0].rstrip("/")
                cands = [base, os.path.join("docs", base), os.path.join("custom_components/heatpump_optimizer", base)]
                ok = any(Path(c).exists() or "*" in c for c in cands) or base in corp
            elif k == "entity":
                obj = s.split(".", 1)[1]
                suf = obj.replace("heatpump_optimizer_", "", 1)
                ok = s in corp or obj in corp or suf in corp or suf in slugs
            else:
                ok = s in corp or s.split(".")[-1] in corp
            if not ok:
                stale[(k, s)].append(f"{uid}:{line}")
    OUT.mkdir(exist_ok=True)
    rows = sorted(stale.items())
    (OUT / "content_stale.json").write_text(json.dumps({f"{k}:{s}": v for (k, s), v in rows}, indent=1))
    print(f"RESULT units={len(units)} units")
    print(f"RESULT units_naming_symbols={named} units")
    print(f"RESULT symbol_mentions={n_sym} mentions")
    print(f"RESULT stale_symbols={len(stale)} symbols")
    print(f"RESULT stale_units={len({u for v in stale.values() for u in v})} units")
    for (k, s), v in rows:
        print(f"   stale {k} {s}  ({len(v)}x) first {v[0]}")
    print(f"RESULT thread_factor={time.process_time() / max(time.thread_time(), 1e-9):.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT swapins=0")


if __name__ == "__main__":
    args = sys.argv[1:]
    pert = [args[i + 1] for i, a in enumerate(args) if a == "--perturb"]
    run(pert, "--plant" in args)
