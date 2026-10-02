import json, subprocess, sys
sys.path.insert(0, "tests")
import mutation_table as m
OUT = "/tmp/claude-0/drain-out"
head = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
pins = json.load(open(f"{OUT}/pins.json"))
sites0 = m.inventory(); b0 = m.load_budgets(); un0 = m.unpinned_sites(b0, sites0)
print("head", head)
print("unpinned before", len(un0))
st = m.apply_drained(OUT, head, [])
print("apply 1:", st)
por = subprocess.run(["git", "status", "--porcelain", "--untracked-files=all"], capture_output=True, text=True).stdout
print("write-set problems:", m.drain_write_set_problems(por))
new = [l for l in por.splitlines() if l.startswith("?? ")]
print("new row files:", len(new))
b1 = m.load_budgets(); un1 = m.unpinned_sites(b1, sites0)
print("unpinned after", len(un1), "delta", len(un0) - len(un1))
by = {}
for s in sites0: by.setdefault(s["anchor"], []).append(s)
disp = m.dispositions(b1)
print("pinned anchors now covered:", sum(all(m.disposition_matches(disp.get(a), s) for s in by[a]) for a in pins), "of", len(pins))
surv = open(f"{OUT}/survivors.txt").read().split("\n")
surv_anchors = {s["anchor"] for s in un0 if m.triage_key(s) in surv}
print("survivor sites still unpinned:", sum(1 for s in un1 if m.triage_key(s) in surv), "of", len([x for x in surv if x]))
print("rows written for survivors:", len([a for a in b1.get("killed_by", {}) if a in surv_anchors]))
print("form/layout/completeness problems:", m.ledger_form_problems(b1) + m.layout_problems() + m.completeness_problems(b1, sites0))
print("ratchet refusal vs HEAD^1 base:", m.ratchet_refusal(len(un0), un1))
st2 = m.apply_drained(OUT, head, [])
print("apply 2 (same slice):", st2)
cl = m.load_closures(); allow = [x for x in m.DEFAULT_SCRIPTS.split(",") if x]
p2 = m.drain_pool(un1, cl, allow, 20261002, 40)
print("same-seed slice after recording: anchors", len({s['anchor'] for s in p2}), "overlapping recorded", len({s['anchor'] for s in p2} & set(pins)))
