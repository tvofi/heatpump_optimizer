"""D4 verify-v1 cross-check: the text-side facts of D4-s2-01/02/03/08/09 measured over the shipped
files by a whole-file enumeration (not the finders' rendered-page walk).

Metrics (one line each; counts):
  escaped_leaves            translation/strings leaves whose json.loads text contains a literal \\uXXXX (all 3 files)
  prefill_keys_missing_cfg  keys of options.step.modbus_prefill.data absent from config.step.device_prefill.data (strings.json)
  prefill_err_missing_cfg   'prefill_device_unreadable' absent from config.error (0/1, strings.json)
  services_without_icon     services.yaml top-level services with no icons.json services.<name>
  bare_unit_leaves_<lang>   data_description leaves (any page, rendered or not) matching (\\d) C\\b or \\bm2\\b
  literal_currency_units    config_flow.py _number(...) unit literals naming SEK/EUR/NOK/DKK
Command (repo root): OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 \
  PYTHONPATH=tests/hastub /home/claude/venv/bin/python tools/audit/round9/D4/verify-v1/static_xcheck.py [--perturb]
--perturb: in memory, decode escapes, copy options prefill keys/error into config, add icons, fix units, template currency -> all 0.
Expected at baseline 1936d5ca (evidence tree 6f51db2c): escaped_leaves=6, prefill_keys_missing_cfg=11,
  prefill_err_missing_cfg=1, services_without_icon=12, bare_unit_leaves_en=9, _sv=9, literal_currency_units=1; exact. Machine: G2-V1 cloud box, 4 cores.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import json, re, sys, time, resource

t0p, t0t = time.process_time(), time.thread_time()
PERT = "--perturb" in sys.argv
C = "custom_components/heatpump_optimizer/"
files = {n: json.load(open(C + n, encoding="utf-8")) for n in ("strings.json", "translations/en.json", "translations/sv.json")}
icons = json.load(open(C + "icons.json", encoding="utf-8"))
flow = open(C + "config_flow.py", encoding="utf-8").read()
svc_yaml = open(C + "services.yaml", encoding="utf-8").read()
ESC = re.compile(r"\\u[0-9a-fA-F]{4}")
BARE = re.compile(r"(\d) C\b|\bm2\b")

def leaves(d, path=()):
    if isinstance(d, dict):
        for k, v in d.items():
            yield from leaves(v, path + (k,))
    elif isinstance(d, str):
        yield path, d

if PERT:
    def fix(d):
        if isinstance(d, dict):
            return {k: fix(v) for k, v in d.items()}
        if isinstance(d, str):
            s = ESC.sub(lambda m: chr(int(m.group(0)[2:], 16)), d)
            return re.sub(r"\bm2\b", "m²", re.sub(r"(\d) C\b", r"\1 °C", s))
        return d
    files = {n: fix(d) for n, d in files.items()}
    for d in files.values():
        d["config"]["step"]["device_prefill"].setdefault("data", {}).update(d["options"]["step"]["modbus_prefill"]["data"])
        d["config"].setdefault("error", {})["prefill_device_unreadable"] = d["options"]["error"]["prefill_device_unreadable"]
    services = re.findall(r"^([a-z_]+):\s*$", svc_yaml, re.M)
    icons["services"] = {s: "mdi:cog" for s in services}
    flow = flow.replace("_number(0, 10000, 10, 'SEK/m³')", "_ByHass(lambda hass: _number(0, 10000, 10, f'{resolve_currency(hass)}/m³'))")

escaped = sum(1 for d in files.values() for _, s in leaves(d) if ESC.search(s))
S = files["strings.json"]
missing_keys = sorted(set(S["options"]["step"]["modbus_prefill"]["data"]) - set(S["config"]["step"]["device_prefill"].get("data", {})))
err_missing = int("prefill_device_unreadable" not in S["config"].get("error", {}))
services = re.findall(r"^([a-z_]+):\s*$", svc_yaml, re.M)
no_icon = [s for s in services if s not in icons.get("services", {})]
cur = len(re.findall(r"_number\([^()]*'(?:SEK|EUR|NOK|DKK)[^']*'\)", flow))
print("# prefill keys missing from config.step.device_prefill.data:", missing_keys)
print(f"RESULT escaped_leaves={escaped} count")
print(f"RESULT prefill_keys_missing_cfg={len(missing_keys)} count")
print(f"RESULT prefill_err_missing_cfg={err_missing} count")
print(f"RESULT services_total={len(services)} count")
print(f"RESULT services_without_icon={len(no_icon)} count")
for n, d in files.items():
    if n == "strings.json":
        continue
    lang = n.split("/")[-1][:2]
    bare = [p for p, s in leaves(d) if "data_description" in p and BARE.search(s)]
    print(f"# bare {lang}:", [".".join(p[-3:]) for p in bare])
    print(f"RESULT bare_unit_leaves_{lang}={len(bare)} count")
print(f"RESULT literal_currency_units={cur} count")
tp, tt = time.process_time() - t0p, time.thread_time() - t0t
print(f"RESULT thread_factor={(tp / tt) if tt else 1.0:.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
print(f"RESULT swapins={resource.getrusage(resource.RUSAGE_SELF).ru_nswap}")
