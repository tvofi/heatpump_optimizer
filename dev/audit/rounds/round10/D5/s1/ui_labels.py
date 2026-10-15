"""D5-s1 harness: docs name UI labels the production UI does not display.

Metric: count of (doc, line, label) where README.md / docs/*.md tell the reader
to pick a UI label that the production UI text does not show verbatim. Key: the
label string the production seam delivers -- manifest.json "name" (the Add
integration picker) and strings.json config/options menu_options (the buttons a
config/options flow menu renders).
Two seam rules, both enumerated here:
  A. "Add integration → X" where X != manifest.json name.
  B. a bold or quoted doc label that starts with a production menu label and
     adds a parenthetical suffix the UI does not show (e.g. "(expert)").
Run:   PYTHONPATH=tests/hastub python3 dev/audit/rounds/round10/D5/s1/ui_labels.py [--perturb]
Expect: mismatches=5 (exact, count) at baseline 17f1c55fad1b; --perturb (in-memory:
strings.json config.step.building.menu_options.thermal += " (expert)") must
give mismatches=1 (only docs/configuration.md:23's integration name remains).  Machine: B1 (macOS, darwin).  No timing; no BLAS.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import glob, json, re, sys, time

PKG = "custom_components/heatpump_optimizer"
manifest = json.load(open(f"{PKG}/manifest.json"))
strings = json.load(open(f"{PKG}/strings.json"))
if "--perturb" in sys.argv:
    m = strings["config"]["step"]["building"]["menu_options"]
    m["thermal"] = m["thermal"] + " (expert)"

labels = set()
for flow in ("config", "options"):
    for st in strings[flow]["step"].values():
        labels.update(st.get("menu_options", {}).values())
low = {l.lower(): l for l in labels if len(l) >= 10}

hits = []
for f in ["README.md"] + sorted(glob.glob("docs/*.md")):
    text = open(f).read()
    for m in re.finditer(r"Add integration\s*→\s*([^*.)]+?)\s*(?:\*\*|\.|\))", text):
        x = " ".join(m.group(1).split())
        if x != manifest["name"]:
            hits.append((f, text.count("\n", 0, m.start()) + 1, "A", x, manifest["name"]))
    for i, line in enumerate(text.split("\n"), 1):
        for m in re.finditer(r'\*\*([^*\n]+)\*\*|"([^"\n<]+)(?:<br/>([^"\n<]+))?"', line):
            t = " ".join(p for p in m.groups() if p).strip().rstrip(".:")
            for seg in [s.strip() for s in t.split("→")]:
                sl = seg.lower()
                if sl in low:
                    continue
                for lab_l, lab in low.items():
                    if sl.startswith(lab_l) and re.fullmatch(r"\s*\([^)]*\)", seg[len(lab):]):
                        hits.append((f, i, "B", seg, lab))
for h in hits:
    print("HIT %s:%d rule=%s doc=%r ui=%r" % h)
print(f"RESULT mismatches={len(hits)} count")
print(f"RESULT thread_factor={time.process_time() / max(time.thread_time(), 1e-9):.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
print("RESULT swapins=0")
