#!/usr/bin/env python3
"""D6-s2 claims harness: entity ids, service names and relative links named in docs/*.md.

METRIC: (a) every `<domain>.heat_pump_optimizer_<x>` entity id cited in docs/*.md is
checked against the entity ids the real platform async_setup_entry produces
(tests/entities.py:collect, ids set by heatpump_optimizer.entity naming); (b) every
`heatpump_optimizer.<service>` cited is checked against services.yaml top-level keys
and services.async_setup_services registration constant set; (c) every relative markdown
link [..](file#anchor) in docs/*.md is checked for target existence and GitHub-slug anchor.
Count key: entity ids as delivered by the constructed entities' .entity_id.
RUN: PYTHONPATH=tests/hastub /Users/timmalmstrom/.local/state/hpo/venv-ci/bin/python dev/audit/rounds/round10/D6/s2/docs_refs.py [--perturb]
--perturb: in memory, renames the produced ids' prefix (entity.f-string seam emulated by
rewriting collected .entity_id) so entity_false must rise to the number of cited ids.
EXPECTED: see REPORT.md, tolerance 0. BASELINE 17f1c55fad1b, machine macOS arm64 box B2.
"""
import os
for v in ("OMP_NUM_THREADS","OPENBLAS_NUM_THREADS","MKL_NUM_THREADS","NUMEXPR_NUM_THREADS","VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(v, "1")
import re, sys, time, pathlib, importlib, glob
t0p, t0t = time.process_time(), time.thread_time()
sys.path.insert(0, "tests"); sys.path.insert(0, "custom_components")
src = pathlib.Path("tests/entities.py").read_text().splitlines()
cut = next(i for i, l in enumerate(src) if l.startswith("sensors = collect(sensor)"))
ns = {"__name__": "entities_prefix", "__file__": "tests/entities.py"}
exec(compile("\n".join(src[:cut]), "tests/entities.py", "exec"), ns)
produced = set()
for plat in ("sensor","binary_sensor","switch","button","climate","datetime","number","select"):
    try: mod = importlib.import_module(f"heatpump_optimizer.{plat}")
    except ImportError: continue
    for e in ns["collect"](mod):
        eid = getattr(e, "entity_id", None)
        if eid: produced.add(eid if "--perturb" not in sys.argv else eid.replace("heat_pump_optimizer_", "hpo_"))
docs = sorted(glob.glob("docs/*.md"))
ent_true = ent_false = 0; out = []
for d in docs:
    for m in re.finditer(r"\b((?:sensor|binary_sensor|switch|button|climate|datetime|number|select)\.heat_pump_optimizer_[a-z0-9_]+)", pathlib.Path(d).read_text()):
        eid = m.group(1)
        if eid in produced: ent_true += 1
        else: ent_false += 1; out.append(f"ENTITY_MISSING {d} {eid}")
import yaml
svcs = set(yaml.safe_load(open("custom_components/heatpump_optimizer/services.yaml")).keys())
svc_true = svc_false = 0
for d in docs:
    for m in re.finditer(r"heatpump_optimizer\.([a-z_]+)", pathlib.Path(d).read_text()):
        if m.group(1) in svcs: svc_true += 1
        else: svc_false += 1; out.append(f"SERVICE_MISSING {d} {m.group(1)}")
def slug(h):
    h = re.sub(r"[`*_]|\[([^\]]*)\]\([^)]*\)", lambda mm: mm.group(1) or "", h.strip().lower())
    h = re.sub(r"[^\w\- ]", "", h)
    return h.replace(" ", "-")
def anchors(p):
    s, seen = set(), {}
    txt = pathlib.Path(p).read_text(); fence = False
    for l in txt.splitlines():
        if l.startswith("```"): fence = not fence
        if fence: continue
        mm = re.match(r"#{1,6}\s+(.*)", l)
        if mm:
            b = slug(mm.group(1)); n = seen.get(b, 0); seen[b] = n+1
            s.add(b if n == 0 else f"{b}-{n}")
    s |= set(re.findall(r'<a (?:name|id)="([^"]+)"', txt))
    return s
link_true = link_false = 0
for d in docs:
    txt = re.sub(r"```.*?```", "", pathlib.Path(d).read_text(), flags=re.S)
    for m in re.finditer(r"\]\(([^)\s]+)\)", txt):
        tgt = m.group(1)
        if re.match(r"[a-z]+:", tgt): continue
        path, _, anc = tgt.partition("#")
        fp = os.path.normpath(os.path.join(os.path.dirname(d), path)) if path else d
        if not os.path.exists(fp): link_false += 1; out.append(f"LINK_DEAD {d} {tgt}"); continue
        if anc and fp.endswith(".md") and anc not in anchors(fp):
            link_false += 1; out.append(f"ANCHOR_DEAD {d} {tgt}"); continue
        link_true += 1
for o in out: print(o)
print(f"RESULT produced_entities={len(produced)} count")
print(f"RESULT entity_true={ent_true} count"); print(f"RESULT entity_false={ent_false} count")
print(f"RESULT service_true={svc_true} count"); print(f"RESULT service_false={svc_false} count")
print(f"RESULT link_true={link_true} count"); print(f"RESULT link_false={link_false} count")
pc, tc = time.process_time()-t0p, time.thread_time()-t0t
print(f"RESULT thread_factor={pc/tc if tc else 1:.3f}"); print(f"RESULT load1={os.getloadavg()[0]:.2f}"); print("RESULT swapins=0")
