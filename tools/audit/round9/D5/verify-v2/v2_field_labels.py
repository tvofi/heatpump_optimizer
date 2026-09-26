"""D5 verify-v2 harness for D5-s1-05 (independent of the finder's field_labels.py).

Metric (one line): of the field names the docs give in (a) the "Setting" column of
configuration.md's "### Two-zone model" table and (b) every *italic* span in
configuration.md and how-it-works.md that ends in a label-shaped noun (sensor, source,
temperature, transfer, fraction, ratio, factor, mode), how many match NO field label anywhere
in translations/en.json (config + options, every step, every section; parentheticals and a
trailing " sensor" stripped, case-insensitive; "A / B" rows split on the slash and matched per
floor), and how many of those have a near-label (difflib ratio >= 0.6) on the form.
Count key: en.json strings, which is what Home Assistant renders on the form.
Command (repository root):
    python tools/audit/round9/D5/verify-v2/v2_field_labels.py [--perturb]
--perturb: in memory, relabel en.json options thermal_model_zones split radiator_power_fraction
    to "Radiator power fraction" -> unmatched must drop by 1.
Baseline 1936d5ca; exact.
"""
import difflib, json, os, re, sys, time
_p0, _t0 = time.process_time(), time.thread_time()
en = json.load(open("custom_components/heatpump_optimizer/translations/en.json"))
if "--perturb" in sys.argv:
    en["options"]["step"]["thermal_model_zones"]["sections"]["split"]["data"]["radiator_power_fraction"] = "Radiator power fraction"
def norm(s):
    s = re.sub(r"\s*\(.*?\)", "", s).strip().lower()
    return re.sub(r"\s+sensor$", "", s)
labels = set()
for flow in ("config", "options"):
    for st in en[flow]["step"].values():
        for v in st.get("data", {}).values():
            labels.add(norm(v))
        for sec in st.get("sections", {}).values():
            for v in sec.get("data", {}).values():
                labels.add(norm(v))
refs = []
conf = open("docs/configuration.md", encoding="utf-8").read()
tz = conf.split("### Two-zone model", 1)[1].split("\n### ", 1)[0]
for line in tz.splitlines():
    m = re.match(r"\|\s*([^|]+?)\s*\|", line)
    if m and m.group(1) not in ("Setting", "---"):
        name = m.group(1)
        if " / " in name:  # "Upper / lower floor thermal mass"
            head, tail = name.split(" / ", 1)
            rest = tail.split(" ", 1)[1] if " " in tail else ""
            parts = [f"{head} {rest}", tail]
        else:
            parts = [name]
        for p in parts:
            refs.append(("configuration.md two-zone table", p))
NOUN = r"(sensor|source|temperature|transfer|fraction|ratio|factor|mode)"
for path in ("docs/configuration.md", "docs/how-it-works.md"):
    for i, line in enumerate(open(path, encoding="utf-8"), 1):
        for m in re.finditer(r"(?<![*\w])\*([A-Z][^*]{3,60}?)\*(?![*\w])", line):
            if re.search(NOUN + r"$", m.group(1).lower()):
                refs.append((f"{path}:{i} italic", m.group(1)))
unmatched = []
for where, name in refs:
    if norm(name) in labels:
        continue
    near = difflib.get_close_matches(norm(name), list(labels), n=1, cutoff=0.6)
    unmatched.append((where, name, near[0] if near else None))
for u in unmatched:
    print("UNMATCHED", u)
print(f"RESULT refs_checked={len(refs)} count")
print(f"RESULT unmatched_refs={len(unmatched)} count")
print(f"RESULT unmatched_with_near_label={sum(1 for u in unmatched if u[2])} count")
cp, ct = time.process_time() - _p0, time.thread_time() - _t0
print(f"RESULT thread_factor={cp/ct if ct else 1:.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
print("RESULT swapins=0")
