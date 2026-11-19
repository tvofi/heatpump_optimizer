"""D6-s6 ledger: one row per text_ledger unit of translations/de.json, each claim checked by running code.

Metric: false+stale = the number of de.json units whose executed check against production
contradicts the sentence (text_ledger check's RESULT false= and stale= lines, summed).
Count key: the verdict of the executed check on the value the production seam delivers
(rendered schema, registered service, collected entity, the card's STRINGS.de, a driven
function's output), never the de.json text alone.
Command (from the export root):
  PYTHONPATH=tests/hastub $HOME/venv-ci/bin/python3 dev/audit/rounds/round11/D6/s6/ledger.py
  ... ledger.py --perturb combi_station       (const.COMBI_TANK_PRESETS['external_station'] potable volume set to
      0.0, the value its own comment names: false+stale down by 1)
  ... ledger.py --perturb card_de             (the card's STRINGS.de "series.lower_floor_modelled"
      set to the English label the de text quotes: false+stale down by 1)
  ... ledger.py --perturb wood_birch          (wood_fuel.WOOD_KWH_M3['birch'] packed/loose swapped back to the
      0.60 ratio the other two types carry: false+stale down by 1)
Expected at the baseline: RESULT false_plus_stale=18 (exact; counts, contention-immune);
combi_station -> 17, card_de -> 17, wood_birch -> 17.
Baseline 92d38ecb640bd462f2e19c0814d0f0b7df1ee692; box B13, 4 vCPU container, Python 3.14.
Writes ledger.tsv beside itself (the perturbed arms write into a mkdtemp root instead).
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import argparse, asyncio, hashlib, json, pathlib, re, subprocess, sys, tempfile, time

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(pathlib.Path.cwd() / "tools" / "audit"))
import text_ledger as T  # noqa: E402

DE = "custom_components/heatpump_optimizer/translations/de.json"
ap = argparse.ArgumentParser()
ap.add_argument("--perturb", choices=["combi_station", "card_de", "wood_birch"], default=None)
ap.add_argument("--dump", action="store_true", help="print each claim row")
A = ap.parse_args()

t0 = time.process_time()
import facts  # noqa: E402
from custom_components.heatpump_optimizer import config_flow as cf, const  # noqa: E402

if A.perturb == "combi_station":
    cf.COMBI_TANK_PRESETS["external_station"] = const.CombiTankPreset(0.75, 0.0)
if A.perturb == "wood_birch":
    from custom_components.heatpump_optimizer import wood_fuel
    wood_fuel.WOOD_KWH_M3["birch"] = {"packed": 1900.0, "loose": 1140.0}
F = facts.collect()
if A.perturb == "card_de":
    F["card"]["de"]["series.lower_floor_modelled"] = "Lower floor (modelled)"

import checks  # noqa: E402  (the per-claim table; needs F)
checks.F = F

# ---------------------------------------------------------------- units with their key paths
doc = json.loads(pathlib.Path(DE).read_text(encoding="utf-8"))
units = []  # (uid, path tuple, idx, text)
seen = {}


def walk(v, p):
    if isinstance(v, dict):
        for k, x in v.items():
            walk(x, p + (k,))
    elif isinstance(v, list):
        for x in v:
            walk(x, p)
    elif isinstance(v, str):
        for i, s in enumerate(T.sentences(v)):
            h = hashlib.sha1(" ".join(s.split()).encode()).hexdigest()[:10]
            k = seen.get(h, 0)
            seen[h] = k + 1
            units.append((f"{DE}#{h}" + (f".{k}" if k else ""), p, i, s))


walk(doc, ())
official = [u[0] for u in T.units_of(DE, pathlib.Path(DE).read_text(encoding="utf-8"), "D6")]
assert [u[0] for u in units] == official, "unit ids diverge from text_ledger.units_of"

# every de label, for the quoted-reference check
LABELS = set()


def lwalk(v):
    if isinstance(v, dict):
        for x in v.values():
            lwalk(x)
    elif isinstance(v, str):
        LABELS.add(v.strip())


lwalk(doc)
CARD_DE = set(F["card"]["de"].values()) if isinstance(F["card"]["de"], dict) else set()

# ---------------------------------------------------------------- existence checks


def step_fields(flow, step):
    page = F[flow].get(step)
    if page is None:
        return None
    fl = dict(page["fields"])
    if flow == "config" and step == "device_prefill":
        for k in F["prefill"]:
            fl.setdefault(k, {"required": False})
    return fl


def step_exists(flow, step):
    if flow == "config":
        return hasattr(cf.HeatPumpOptimizerConfigFlow, "async_step_" + step)
    return hasattr(cf.HeatPumpOptimizerOptionsFlow, "async_step_" + step) or step in {p.step for p in cf._OPTION_PAGES}


def existence(p):
    """(claim text, ok, observed) for what a unit's key names, or None when the key names nothing checkable."""
    if p[0] in ("config", "options"):
        flow = p[0]
        if p[1] == "step":
            step = p[2]
            if not step_exists(flow, step):
                return (f"{flow} step {step} exists", False, "no async_step_" + step)
            rest = p[3:]
            fields = step_fields(flow, step) or {}
            secs = fields.get("__sections__", {})
            if rest[0] == "sections":
                g = rest[1]
                ok = g in secs
                if rest[2] in ("data", "data_description"):
                    k = rest[3]
                    ok = ok and k in secs.get(g, set())
                    return (f"{flow}/{step} section {g} holds field {k}", ok, f"section {g}: {sorted(secs.get(g, []))[:6]}...")
                return (f"{flow}/{step} renders section {g}", ok, f"sections={sorted(secs)}")
            if rest[0] in ("data", "data_description"):
                k = rest[1]
                if k == "after_save" and flow == "options":
                    return (f"options pages carry after_save", True, "_options_schema appends after_save")
                ok = k in fields
                return (f"{flow}/{step} renders field {k}", ok, f"{len([x for x in fields if x != '__sections__'])} fields; {k} {'present' if ok else 'absent'}")
            if rest[0] == "menu_options":
                menu = (F[flow].get(step) or {}).get("menu", [])
                return (f"{flow}/{step} menu offers {rest[1]}", rest[1] in menu, f"menu={menu}")
            return (f"{flow} step {step} exists", True, "async_step_" + step)
        if p[1] in ("error", "abort"):
            return (f"{flow} {p[1]} key {p[2]} is raised by production", p[2] in F["strings"], f"string constant {p[2]!r} {'found' if p[2] in F['strings'] else 'absent'}")
    if p[0] == "selector":
        opts = F["selectors"].get(p[1], set())
        if len(p) >= 4 and p[2] == "options":
            return (f"selector {p[1]} offers {p[3]}", p[3] in opts, f"options={sorted(opts)}")
    if p[0] == "entity":
        plat, key = p[1], p[2]
        ents = F["entities"].get(plat, {})
        e = ents.get(key)
        if e is None:
            return (f"{plat} entity {key} is created", False, f"collected {plat}: {len(ents)}")
        if len(p) == 4 and p[3] == "name":
            return (f"{plat} entity {key} is created", True, f"collected by {plat}.async_setup_entry")
        if p[3] == "state":
            opts = getattr(e, "_attr_options", None) or getattr(e, "options", None)
            if opts:
                return (f"{key} can publish state {p[4]}", p[4] in opts, f"options={len(opts)}")
            return (f"{key} can publish state {p[4]}", p[4] in F["strings"], "string constant")
        if p[3] == "state_attributes":
            attr = p[4]
            if attr == "preset_mode":
                modes = getattr(e, "_attr_preset_modes", None) or getattr(e, "preset_modes", None) or []
                return (f"climate offers preset {p[6]}", p[6] in modes, f"preset_modes={modes}")
            if len(p) == 6:
                return (f"{key} publishes attribute {attr}", attr in F["strings"], "string constant")
            return (f"{key}.{attr} can hold {p[6]}", p[6] in F["strings"], "string constant")
    if p[0] == "services":
        svc = p[1]
        reg = F["services"]
        if svc not in reg:
            return (f"service {svc} is registered", False, "not registered")
        if p[2] == "fields":
            f = p[3]
            ok = f in reg[svc] and f in ((F["services_yaml"].get(svc) or {}).get("fields") or {})
            return (f"service {svc} takes field {f}", ok, f"schema has {f}: {f in reg[svc]}; services.yaml: {f in ((F['services_yaml'].get(svc) or {}).get('fields') or {})}")
        if p[2] == "sections":
            return (f"service {svc} groups section {p[3]}", True, "services.yaml section")
        return (f"service {svc} is registered", True, "async_register_services")
    if p[0] in ("issues", "exceptions"):
        return (f"{p[0][:-1]} key {p[1]} is raised by production", p[1] in F["strings"], f"string constant {p[1]!r} {'found' if p[1] in F['strings'] else 'absent'}")
    return None


LABEL_TAILS = {"name", "title", "menu_options", "data"}


def is_label(p):
    if p[0] == "selector":
        return True
    if p[0] == "entity" and (p[-1] == "name" or "state" in p):
        return True
    if p[0] in ("config", "options") and p[1] == "step" and (p[3] in ("title", "menu_options", "data") or (p[3] == "sections" and p[-1] == "name") or (p[3] == "sections" and len(p) > 5 and p[5] == "data")):
        return True
    if p[0] == "services" and p[-1] == "name":
        return True
    if p[0] == "issues" and p[-1] == "title":
        return True
    return False


# ---------------------------------------------------------------- quoted references
QUOTE = re.compile(r"„([^“]+)“|\"([^\"]+)\"")


def quoted_refs(s):
    out = []
    for m in QUOTE.finditer(s):
        q = (m.group(1) or m.group(2)).strip()
        verdict = checks.quote_kind(q, LABELS, CARD_DE)
        out.append((q, verdict))
    return out


# ---------------------------------------------------------------- build rows
rows, stats = [], {"label": 0, "content": 0, "behaviour": 0}
false_rows = []
for uid, p, idx, s in units:
    path = "/".join(p)
    ex = existence(p)
    parts, verdict, truth = [], "true", ""
    if ex is not None:
        parts.append(f"{ex[0]}: {'yes' if ex[1] else 'NO'} ({ex[2]})")
        if not ex[1]:
            verdict, truth = "false", f"production has no such object: {ex[0]}"
    label = is_label(p)
    content = []
    for name, ok, obs, kind in checks.content_checks(path, idx, s):
        content.append(name)
        parts.append(f"{name}: {'ok' if ok else 'CONTRADICTED'} ({obs})")
        if not ok and verdict == "true":
            verdict, truth = kind, obs
        elif not ok:
            truth += "; " + obs
    for q, (qok, qobs) in quoted_refs(s):
        if qok is None:
            continue
        content.append("quote")
        parts.append(f"quoted „{q}“: {qobs}")
        if not qok:
            if verdict == "true":
                verdict, truth = "stale", f"„{q}“ is not what the German UI shows: {qobs}"
            else:
                truth += f"; „{q}“: {qobs}"
    if label:
        stats["label"] += 1
        tier = "label"
    elif content:
        stats["content"] += 1
        tier = "content"
    else:
        stats["behaviour"] += 1
        tier = "behaviour"
        if verdict == "true":
            verdict = "unverifiable"
            truth = "behavioural sentence; its anchor object was checked, the behaviour it states was not driven this round"
    cmd = f"ledger.py[{tier}] {path}#{idx}"
    res = " | ".join(parts) or "no anchor"
    rows.append([uid, "0", "claim", cmd, res.replace("\t", " ").replace("\n", " ")[:900], verdict, truth.replace("\t", " ").replace("\n", " ")[:600]])
    if verdict in ("false", "stale"):
        false_rows.append((path, idx, s, verdict, truth))

out_dir = HERE if A.perturb is None else pathlib.Path(tempfile.mkdtemp(prefix="d6s6-"))
ledger_path = out_dir / "ledger.tsv"
ledger_path.write_text("\n".join(["\t".join(T.HEADER)] + ["\t".join(r) for r in rows]) + "\n", encoding="utf-8")

for path, idx, s, v, t in false_rows:
    print(f"   {v.upper()} {path}#{idx}: {s[:140]}")
    print(f"        truth: {t[:300]}")
unm = checks.unmapped_numeric([(u[1], u[2], u[3]) for u in units])
for u in unm:
    print("   UNMAPPED", u)
r = subprocess.run([sys.executable, "tools/audit/text_ledger.py", "check", "--dim", "D6", str(ledger_path), DE] + (["--plant"] if A.perturb is None else []),
                   capture_output=True, text=True)
print(r.stdout.strip())
counts = dict(re.findall(r"RESULT (\w+)=(\d+)", r.stdout))
print(f"RESULT tier_label={stats['label']} tier_content={stats['content']} tier_behaviour={stats['behaviour']}")
print(f"RESULT unmapped_numeric={len(unm)}")
print(f"RESULT false_plus_stale={int(counts.get('false', 0)) + int(counts.get('stale', 0))} rows")
print(f"RESULT ledger_check_rc={r.returncode}")
print(f"RESULT perturb={A.perturb}")
_tc = time.thread_time()
print("RESULT thread_factor=%.3f" % (time.process_time() / _tc if _tc else 1.0))
print("RESULT load1=%s" % open("/proc/loadavg").read().split()[0])
try:
    sw = [l for l in open("/proc/vmstat") if l.startswith("pswpin")][0].split()[1]
except Exception:  # noqa: BLE001
    sw = "n/a"
print(f"RESULT swapins={sw}")
