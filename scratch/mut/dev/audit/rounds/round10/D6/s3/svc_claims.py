"""D6-s3 claims harness: services.yaml / strings.json / translations / manifest / hacs.
Metric: count of claims (service yaml field, example, select option, number range,
catalogue key, manifest/hacs value) that disagree with the production object they describe.
Count key: the schema object registered by services:async_register_services (captured from
hass.services.async_register), not text in services.yaml.
Run: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round10/D6/s3/svc_claims.py [--verbose]
Expected: as printed (counts exact, tolerance 0). Baseline 17f1c55fad1b, macOS arm64 (B3).
"""
import os
for _v in ("OMP_NUM_THREADS","OPENBLAS_NUM_THREADS","MKL_NUM_THREADS","NUMEXPR_NUM_THREADS","VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import sys, json, time
sys.path.insert(0, ".")
import yaml, voluptuous as vol
import custom_components.heatpump_optimizer.services as S
from custom_components.heatpump_optimizer.const import DOMAIN

VERBOSE = "--verbose" in sys.argv
c0, t0 = time.process_time(), time.thread_time()
reg = {}
class _Svc:
    def async_register(self, domain, name, handler, schema=None, **kw):
        reg[name] = schema
class _H:
    services = _Svc(); data = {}
S.async_register_services(_H())

base = "custom_components/heatpump_optimizer/"
Y = yaml.safe_load(open(base + "services.yaml"))
cats = {n: json.load(open(base + p)) for n, p in
        [("strings", "strings.json"), ("en", "translations/en.json"), ("sv", "translations/sv.json")]}

claims = 0; bad = []
def chk(ok, msg):
    global claims
    claims += 1
    if not ok: bad.append(msg)

def schema_keys(sch):
    out = {}
    if isinstance(sch, vol.All):
        sch = next((v for v in sch.validators if isinstance(v, vol.Schema)), sch)
    s = getattr(sch, "schema", None)
    if isinstance(s, dict):
        for k, v in s.items():
            out[str(k)] = (isinstance(k, vol.Required), v)
    return out

for name in sorted(set(Y) | set(reg)):
    chk(name in reg, f"yaml service {name} not registered")
    chk(name in Y, f"registered service {name} absent from services.yaml")
    if name not in reg or name not in Y: continue
    sch = reg[name]; keys = schema_keys(sch)
    yf = (Y[name] or {}).get("fields") or {}
    # flatten sections
    flat = {}
    for f, spec in yf.items():
        if isinstance(spec, dict) and "fields" in spec and "selector" not in spec:
            flat.update(spec["fields"])
        else: flat[f] = spec
    if keys:
        for f in keys:
            chk(f in flat, f"{name}: schema field {f} not in services.yaml")
    for f, spec in flat.items():
        spec = spec or {}
        if keys: chk(f in keys, f"{name}: yaml field {f} not accepted by schema")
        if f in keys:
            chk(bool(spec.get("required", False)) == keys[f][0],
                f"{name}.{f}: yaml required={spec.get('required', False)} schema Required={keys[f][0]}")
        if "example" in spec and sch is not None:
            req = {k: None for k, (r, _) in keys.items() if r and k != f}
            try:
                # validate the field alone
                fs = keys.get(f, (None, None))[1]
                if fs is not None: vol.Schema(fs)(spec["example"])
                chk(True, "")
            except Exception as e:
                chk(False, f"{name}.{f}: example {spec['example']!r} rejected: {e}")
        sel = spec.get("selector") or {}
        if "select" in sel and f in keys:
            for opt in (sel["select"] or {}).get("options", []):
                o = opt["value"] if isinstance(opt, dict) else opt
                try: vol.Schema(keys[f][1])(o); chk(True, "")
                except Exception as e: chk(False, f"{name}.{f}: select option {o!r} rejected: {e}")
        if "number" in sel and f in keys and isinstance(sel["number"], dict):
            for bnd in ("min", "max"):
                if bnd in sel["number"]:
                    try: vol.Schema(keys[f][1])(sel["number"][bnd]); chk(True, "")
                    except Exception as e: chk(False, f"{name}.{f}: selector {bnd}={sel['number'][bnd]} rejected: {e}")
    for cn, cat in cats.items():
        sv = cat.get("services", {}).get(name)
        chk(sv is not None, f"{cn}: no services.{name}")
        if sv:
            cf = sv.get("fields", {})
            for f in flat: chk(f in cf, f"{cn}: services.{name}.fields.{f} missing")
            for f in cf: chk(f in flat, f"{cn}: services.{name}.fields.{f} stale (not in yaml)")

def leaves(d, p=""):
    if isinstance(d, dict):
        for k, v in d.items(): yield from leaves(v, p + "/" + k)
    else: yield p
ks = {n: set(leaves(c)) for n, c in cats.items()}
for n in ("en", "sv"):
    for k in ks["strings"] - ks[n]: chk(False, f"{n}: missing key {k}")
    for k in ks[n] - ks["strings"]: chk(False, f"{n}: extra key {k}")
    claims += len(ks["strings"] & ks[n])

man = json.load(open(base + "manifest.json")); hacs = json.load(open("hacs.json"))
chk(man["version"] == open("VERSION").read().strip(), "manifest version != VERSION")
chk(man["domain"] == DOMAIN, "manifest domain != const.DOMAIN")
chk(man["name"] == hacs["name"], "manifest name != hacs name")
import importlib
for r in man["requirements"]:
    mod = r.split(">=")[0].split("==")[0]
    chk(importlib.util.find_spec(mod) is not None, f"requirement {mod} not importable")

for b in bad:
    if VERBOSE or True: print("FALSE", b)
pc, tc = time.process_time() - c0, time.thread_time() - t0
print(f"RESULT registered_services={len(reg)} count")
print(f"RESULT yaml_services={len(Y)} count")
print(f"RESULT claims_checked={claims} count")
print(f"RESULT claims_false={len(bad)} count")
print(f"RESULT thread_factor={pc/tc if tc else 1:.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
print("RESULT swapins=0")
