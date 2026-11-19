"""D10-s2 gold docs-* rules, one executed check per rule, against the README
and docs/ the integration's manifest "documentation" URL serves.

  docs-supported-functions  every entity the platforms add (census of
      _census.entities) is named, by its English catalogue name, in the
      README's Entities section; the per-platform "(N total)" headings equal
      the census; the README's disabled-by-default list equals the entities
      the census finds disabled.
  docs-data-update          the documented default optimization interval
      equals const.DEFAULT_OPTIMIZATION_INTERVAL, which the coordinator
      passes to DataUpdateCoordinator as update_interval.
  docs-examples             every blueprint under blueprints/automation is
      linked from the README, and every blueprint link resolves to a file.
  docs-known-limitations, docs-supported-devices, docs-troubleshooting,
  docs-use-cases            the README carries the section (heading found)
      with at least one entry under it.
Metric: docs_bad = sum of the failures above.
Key: the README text against the names and counts the production entities
publish (en catalogue name of each entity's translation key).
Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D10/s2/docs_gold.py [--perturb]
Expected at baseline 92d38ecb: RESULT docs_bad=0, exact.
--perturb renames one entity's translation key in memory (the README no
longer names it): docs_bad rises by 1.
Instrumented symbol: heatpump_optimizer.sensor:async_setup_entry (the census)
and heatpump_optimizer.const:DEFAULT_OPTIMIZATION_INTERVAL.
Machine: local macOS box B2, Python 3.14 venv-ci.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import re
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _census as c  # noqa: E402
from heatpump_optimizer import const  # noqa: E402

README = Path("README.md").read_text()
en = c.load_json("translations/en.json")["entity"]
ents, coord, entry = c.entities()
if "--perturb" in sys.argv:
    en["sensor"]["zz_renamed"] = {"name": "Zz Renamed Sensor"}
    ents[0][1]._attr_translation_key = "zz_renamed"

bad = []


def section(title, stop=r"\n## "):
    m = re.search(rf"\n## {re.escape(title)}\n(.*?)(?={stop})", README, re.S)
    return m.group(1) if m else ""


entities_md = section("Entities")
names = {}
for p, e in ents:
    name = en[p][e._attr_translation_key]["name"]
    names[(p, type(e).__name__)] = name
    if name.lower() not in entities_md.lower():
        bad.append(f"supported-functions: {p} {name!r} not named in README Entities")
heads = {"sensor": "Sensors", "binary_sensor": "Binary Sensors", "button": "Buttons"}
census = Counter(p for p, _ in ents)
for p, h in heads.items():
    m = re.search(rf"### {h} \((\d+) total\)", README)
    if not m or int(m.group(1)) != census[p]:
        bad.append(f"supported-functions: heading {h} says {m and m.group(1)} vs census {census[p]}")
print(f"RESULT entities_named={sum(1 for (p, k), n in names.items() if n.lower() in entities_md.lower())} count")

# disabled-by-default list, as the README states it
m = re.search(r"Disabled by default: (.*?)\.\n", entities_md, re.S)
listed = {x.strip() for x in re.split(r",| and ", (m.group(1) if m else "").replace("\n", " ")) if x.strip()}
off = set()
for p, e in ents:
    v = None
    for k in type(e).__mro__:
        if "entity_registry_enabled_default" in vars(k) and isinstance(vars(k)["entity_registry_enabled_default"], property) \
                and k.__module__.startswith("heatpump_optimizer"):
            v = e.entity_registry_enabled_default
            break
    else:
        v = getattr(e, "_attr_entity_registry_enabled_default", True)
    if not v:
        off.add(names[(p, type(e).__name__)])
for x in sorted(off ^ listed):
    bad.append(f"supported-functions: disabled list differs on {x!r}")
print(f"RESULT disabled_listed={len(listed)} count")
print(f"RESULT disabled_census={len(off)} count")

# docs-data-update
how = Path("docs/how-it-works.md").read_text()
m = re.search(r"Every optimization interval \((\d+) minutes by default\)", how)
stated = int(m.group(1)) if m else None
if stated != int(const.DEFAULT_OPTIMIZATION_INTERVAL):
    bad.append(f"data-update: stated {stated} vs code {const.DEFAULT_OPTIMIZATION_INTERVAL}")
print(f"RESULT interval_stated={stated} minutes")

# docs-examples
blue = sorted(p.name for p in Path("blueprints/automation").glob("*.yaml"))
links = re.findall(r"blueprints/automation/([\w.-]+\.yaml)", README)
for b in blue:
    if b not in links:
        bad.append(f"examples: blueprint {b} not linked from README")
for link in set(links):
    if link not in blue:
        bad.append(f"examples: README links missing blueprint {link}")
print(f"RESULT blueprints={len(blue)} count")
print(f"RESULT blueprint_links={len(set(links))} count")

# headings
for rule, title in (("known-limitations", "Known limitations"), ("supported-devices", "Supported heat pumps and controls"),
                    ("troubleshooting", "Troubleshooting"), ("use-cases", "What it does")):
    body = section(title)
    entries = len(re.findall(r"^(?:- |\| |### |\*\*|\d+\. )", body, re.M))
    print(f"RESULT {rule.replace('-', '_')}_entries={entries} count")
    if entries == 0:
        bad.append(f"{rule}: README section {title!r} missing or empty")

for b in bad:
    print("BAD", b)
print(f"RESULT docs_bad={len(bad)} count")
c.stats()
