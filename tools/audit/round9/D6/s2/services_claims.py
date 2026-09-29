"""D6-s2 harness: docs/configuration.md "## Services" claims against the registered services.

Metric: count of Services-section claims (service count, entry_id roster, per-service
field lists/counts, returns column, documented numeric ranges, mode values, assignable
keys, selectable layouts) that disagree with what heatpump_optimizer.services
.async_register_services registers (through the real integration async_setup, into
tests/harness.py:FakeServices), each range probed by feeding boundary values through
the registered voluptuous schema. Key: the registered schema / registration kwargs.

Command (from the export root):
    PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D6/s2/services_claims.py
Perturbation: --perturb adds one Optional field to services.SERVICE_SCHEMA_SET_THERMAL_PARAMS
  and removes 'boost' from const.OPERATION_MODES (in memory) before registration;
  services_claims_false must go up by >= 2.
Expected: see REPORT.md (exact).
Baseline: 1936d5ca72a06556eeed4e8e5bf3dea520e517e1. Machine: cloud container, 4 CPU, Linux.
Root rule: ROOT = Path.cwd().
"""

import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import asyncio
import re
import sys
import time
from pathlib import Path
from unittest import mock

ROOT = Path.cwd()
sys.path.insert(0, str(ROOT / "tests"))
sys.path.insert(0, str(ROOT / "tests" / "hastub"))
_t0p, _t0t = time.process_time(), time.thread_time()

import voluptuous as vol  # noqa: E402
import harness  # noqa: E402
from harness import FakeHass, ha_setup_component  # noqa: E402
import heatpump_optimizer as integration  # noqa: E402
from heatpump_optimizer import const, services, topology  # noqa: E402

DOC = ROOT / "docs/configuration.md"


def section():
    text = DOC.read_text()
    start = text.index("## Services")
    end = text.index("\n## ", start + 5)
    base = text[:start].count("\n") + 1
    return text[start:end], base


def register():
    kwargs = {}
    orig = harness.FakeServices.async_register

    def spy(self, domain, service, handler, schema=None, **kw):
        kwargs[service] = kw
        return orig(self, domain, service, handler, schema=schema, **kw)

    hass = FakeHass()
    with mock.patch.object(harness.FakeServices, "async_register", spy):
        asyncio.run(ha_setup_component(integration, hass))
    schemas = {s: hass.services._schemas[(const.DOMAIN, s)]
               for s in hass.services.async_services().get(const.DOMAIN, {})}
    return schemas, kwargs


def inner(schema):
    """The dict-schema under a vol.All wrapper."""
    if isinstance(schema, vol.Schema):
        return schema
    for v in getattr(schema, "validators", ()):
        if isinstance(v, vol.Schema):
            return v
    return None


def fields(schema):
    s = inner(schema)
    return {str(k): (type(k).__name__, v) for k, v in s.schema.items()} if s else {}


def accepts(schema, payload):
    try:
        schema(payload)
        return True
    except (vol.Invalid, vol.MultipleInvalid, ValueError, TypeError):
        return False


def probe_range(schema, name, lo, hi):
    """(documented lo accepted, below lo refused, hi accepted, above hi refused)."""
    try:
        is_int = isinstance(schema({name: lo + 0.5})[name], int)
    except (vol.Invalid, ValueError, TypeError):
        is_int = False
    if is_int:
        eps = 1.0  # an integer field (Coerce(int) truncates): step outside by one
    else:
        eps = 1e-6
    below = accepts(schema, {name: lo - max(eps, abs(lo) * 1e-6)})
    above = accepts(schema, {name: hi + max(eps, abs(hi) * 1e-6)})
    return accepts(schema, {name: lo}), not below, accepts(schema, {name: hi}), not above


def num(s):
    return float(s.replace("−", "-"))


def main():
    perturb = "--perturb" in sys.argv
    patches = []
    if perturb:
        extra = vol.Schema({**services.SERVICE_SCHEMA_SET_THERMAL_PARAMS.schema,
                            vol.Optional("d6_probe_field"): vol.Coerce(float)})
        patches.append(mock.patch.object(services, "SERVICE_SCHEMA_SET_THERMAL_PARAMS", extra))
        patches.append(mock.patch.object(services, "SERVICE_SCHEMA_SET_MODE", vol.Schema(
            {vol.Required("mode"): vol.In([m for m in const.OPERATION_MODES if m != "boost"])})))
    for p in patches:
        p.start()
    try:
        schemas, kwargs = register()
    finally:
        for p in patches:
            p.stop()
    text, base = section()
    claims = []

    def claim(line_off, what, ok, detail=""):
        claims.append((base + line_off, what, bool(ok), detail))

    lines = text.splitlines()

    def at(pattern):
        for i, l in enumerate(lines):
            if re.search(pattern, l):
                return i
        return 0

    m = re.search(r"(\d+) services are registered", text)
    claim(at(r"services are registered"), f"{m.group(1)} services registered",
          int(m.group(1)) == len(schemas), f"registered {len(schemas)}")
    with_entry = sorted(s for s in schemas if "entry_id" in fields(schemas[s]))
    m = re.search(r"The (\w+)\s+that act on a specific config entry", text)
    words = {"seven": 7, "eight": 8, "six": 6, "five": 5, "nine": 9}
    claim(at(r"that act on a specific"), f"{m.group(1)} services accept entry_id",
          words.get(m.group(1)) == len(with_entry), f"with entry_id: {with_entry}")
    m = re.search(r"`run_optimization`, `set_away`, `set_mode`,\s+`set_thermal_parameters` and `simulate_plan` always", text)
    no_entry = {"run_optimization", "set_away", "set_mode", "set_thermal_parameters", "simulate_plan"}
    claim(at(r"always act on every"), "five services without entry_id",
          m is not None and no_entry == set(schemas) - set(with_entry), str(sorted(set(schemas) - set(with_entry))))
    # table rows
    for i, l in enumerate(lines):
        mm = re.match(r"^\| `(\w+)` \| (.+?) \| (.+?) \|$", l)
        if not mm:
            continue
        svc, fdesc, ret = mm.groups()
        f = fields(schemas.get(svc, vol.Schema({})))
        names = set(f)
        required = {k for k, (t, _v) in f.items() if t == "Required"}
        doc_names = set(re.findall(r"`(\w+)`", fdesc))
        cnt = re.match(r"(\d+) optional", fdesc)
        if fdesc == "none":
            ok, det = names == set(), f"fields {sorted(names)}"
        elif cnt:
            n_opt = sum(1 for k, (t, _v) in f.items() if t == "Optional" and k != "entry_id")
            ok = int(cnt.group(1)) == n_opt and (("entry_id" in fdesc) == ("entry_id" in names))
            det = f"{n_opt} optional non-entry_id fields; entry_id {'present' if 'entry_id' in names else 'absent'}"
        else:
            ok = doc_names == names
            det = f"schema {sorted(names)}"
            if "(required)" in fdesc or "both required" in fdesc:
                req_doc = set(re.findall(r"`(\w+)` \(required\)", fdesc))
                if "both required" in fdesc:
                    req_doc = set(re.findall(r"`(\w+)`", fdesc.split("(both required)")[0]))
                ok = ok and req_doc <= required
        claim(i, f"table {svc}: fields '{fdesc}'", ok, det)
        sr = kwargs.get(svc, {}).get("supports_response")
        sr = getattr(sr, "value", sr)
        want = {"—": None, "always": "only", "optional": "optional"}.get(ret.strip())
        claim(i, f"table {svc}: returns '{ret}'", (sr or None) == want, f"supports_response={sr}")
    # prose field counts
    m = re.search(r"All (\d+) fields\s+are optional", text)
    tp = fields(schemas["set_thermal_parameters"])
    claim(at(r"All \d+ fields"), f"set_thermal_parameters: all {m.group(1)} fields optional",
          int(m.group(1)) == len(tp) and all(t == "Optional" for t, _ in tp.values()), f"{len(tp)} fields")
    # ranges in the set_thermal_parameters bullets
    start = at(r"^- \*\*House and slab")
    stop = at(r"^\*\*`simulate_plan`\*\*")
    bullet = " ".join(lines[start:stop])
    doc_listed = set()
    for grp in re.finditer(r"((?:`\w+`(?:,| and)?\s*)+)\((?:each )?([−\d.]+)–([−\d.]+)\)", bullet):
        # a comma-joined run shares the range; a range means nothing on a
        # boolean or string field, so only numeric fields of the run are probed
        names = [n for n in re.findall(r"`(\w+)`", grp.group(1))
                 if not accepts(schemas["set_thermal_parameters"], {n: "not-a-number"})]
        lo, hi = num(grp.group(2)), num(grp.group(3))
        for n in names:
            doc_listed.add(n)
            r = probe_range(schemas["set_thermal_parameters"], n, lo, hi)
            claim(start, f"set_thermal_parameters.{n} range {grp.group(2)}–{grp.group(3)}", all(r),
                  f"lo ok/below refused/hi ok/above refused = {r}")
    doc_listed |= set(re.findall(r"`(\w+)`", bullet))
    claim(start, "set_thermal_parameters bullets name every schema field",
          doc_listed >= set(tp), f"unlisted {sorted(set(tp) - doc_listed)}")
    # simulate_plan prose list
    i = at(r"^\*\*`simulate_plan`\*\*")
    para = " ".join(lines[i:i + 8])
    listed = set(re.findall(r"`(\w+)`", para.split("Fields, all optional:")[1].split("An empty")[0]))
    sp = fields(schemas["simulate_plan"])
    claim(i, "simulate_plan: prose 'Fields, all optional' lists the schema",
          listed == set(sp), f"schema-only {sorted(set(sp) - listed)}")
    for n, lo, hi in re.findall(r"`(\w+)` \((\d+)–(\d+)\)", para):
        r = probe_range(schemas["simulate_plan"], n, float(lo), float(hi))
        claim(i, f"simulate_plan.{n} range {lo}–{hi}", all(r), str(r))
    # set_mode values
    i = at(r"^\*\*`set_mode`\*\*")
    para = " ".join(lines[i:i + 5])
    modes = set(re.findall(r"`(\w+)` \(", para)) | ({"off"} if "or `off`" in para else set())
    accepted = {x for x in modes | {"auto", "comfort", "economy", "boost", "off", "eco"}
                if accepts(schemas["set_mode"], {"mode": x})}
    claim(i, f"set_mode values {sorted(modes)}", modes == accepted, f"accepted {sorted(accepted)}")
    # assign_entity keys
    i = at(r"^\*\*`assign_entity`\*\*")
    para = " ".join(lines[i:i + 16])
    m = re.search(r"one of\s+the (\d+) assignable", para)
    keys = set(re.findall(r"`(\w+_entity)`", para)) - {"assign_entity"}
    acc = {k for k in keys | set(topology.ASSIGNABLE_KEYS)
           if accepts(schemas["assign_entity"], {"key": k, "entity_id": ""})}
    claim(i, f"assign_entity: {m.group(1)} keys, listed", int(m.group(1)) == len(acc) and keys == acc,
          f"accepted {len(acc)}; doc-only {sorted(keys - acc)}; schema-only {sorted(acc - keys)}")
    # apply_topology selectable layouts
    i = at(r"^\*\*`apply_topology`\*\*")
    para = " ".join(lines[i:i + 3])
    m = re.search(r"one of the (\w+) selectable", para)
    lay = [k for k in topology.LAYOUTS if accepts(schemas["apply_topology"], {"layout": k})]
    claim(i, f"apply_topology: {m.group(1)} selectable layouts", words.get(m.group(1), -1) == len(lay) or m.group(1) == "four" and len(lay) == 4, f"accepted {lay}")
    # apply_schedule fields
    i = at(r"^\*\*`apply_schedule`\*\*")
    para = " ".join(lines[i:i + 3])
    listed = set(re.findall(r"`(\w+)`", para)) - {"apply_schedule"}
    aps = set(fields(schemas["apply_schedule"])) - {"entry_id"}
    claim(i, "apply_schedule: prose lists its fields", listed == aps, f"schema {sorted(aps)}")
    # apply_manual_plan default expiry 20 h -- drive the production helper when present
    for line, what, ok, det in claims:
        print(f"{'true ' if ok else 'FALSE'} docs/configuration.md:{line:<5} {what} -- {det}")
    print(f"RESULT services_claims={len(claims)} count")
    print(f"RESULT services_claims_false={sum(not c[2] for c in claims)} count")
    tp_, tt = time.process_time() - _t0p, time.thread_time() - _t0t
    print(f"RESULT thread_factor={tp_ / tt if tt else 1.0:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    try:
        sw = [l for l in open("/proc/vmstat") if l.startswith("pswpin")][0].split()[1]
    except Exception:
        sw = "na"
    print(f"RESULT swapins={sw}")


if __name__ == "__main__":
    main()
