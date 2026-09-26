#!/usr/bin/env python3
"""Generate the round-9 fix plan artefacts from data.py and CLASSES-DRAFT.json.

Writes, under OUT (argv[1]):
  .claude/workflows/wave-r9-groups.json   roster draft, one entry per PR
  handoff/round9/fix/F<n>.md                 one fixer brief per lane
  handoff/round9/FIX-PLAN-tables.md          generated tables for FIX-PLAN.md
and checks: every surviving finding placed; no finding over-placed; the
per-PR finding cap; every `after` names a PR; the dependency graph is acyclic;
and that no two PRs that could be open at once edit the same file.
"""
import json, os, re, sys, collections
sys.path.insert(0, os.path.dirname(__file__))
from data import (LANES, PRS, CLASS_SHORT, SWEEP_OF, S7, RCA, EXEMPT, EV, CC, SWEEP_COMMIT,
                  SWEEP_LABEL, SWEEP_DIR, INSTANCES, LEADS, LEDGER_NOTES)

OUT = sys.argv[1]
CLASSES = json.load(open("/mnt/project-files/audit-r9/judge/CLASSES-DRAFT.json"))

# ---------------------------------------------------------------- findings index
FIND = {}
for c in CLASSES["classes"]:
    cid = c["id"] or CLASS_SHORT[c["name"]]
    for f in c["findings"]:
        FIND[f["id"]] = dict(f, cls=cid, class_name=c["name"], rca=c["rca"], barriered=c["barriered"], n=c["n"])
assert len(FIND) == 145, len(FIND)
JUDGE_N = {(c["id"] or CLASS_SHORT[c["name"]]): c["n"] for c in CLASSES["classes"]}

# ---------------------------------------------------------------- Phase D sweeps
SWEEP_DIRPATH = "/mnt/project-files/audit-r9/sweep"
def _sweep_entries():
    d = json.load(open(f"{SWEEP_DIRPATH}/S1.json")); yield "S1", d
    for n in (2, 3, 4, 6, 7):
        for c in json.load(open(f"{SWEEP_DIRPATH}/S{n}.json"))["classes"]:
            yield f"S{n}", c
    for c in json.load(open(f"{SWEEP_DIRPATH}/S5.json")):
        yield "S5", c
SW = {}
for thread, c in _sweep_entries():
    label = c["class"][5:] if c["class"].startswith("new: ") else c["class"]
    cid = SWEEP_LABEL.get(label) or CLASS_SHORT.get(label) or label
    assert cid in JUDGE_N, f"sweep class {c['class']!r} maps to no plan class"
    assert cid not in SW, f"class {cid} swept twice"
    d, enum = SWEEP_DIR[cid]
    SW[cid] = dict(thread=thread, commit=SWEEP_COMMIT[thread], N=c["N"], rca=bool(c["rca"]),
                   seams=c["seams"], barrier=c.get("barrier_proposal") or "none", gate=c.get("gate_seconds"),
                   dir=f"tools/audit/round9/D14/sweep/{d}", enum=f"tools/audit/round9/D14/sweep/{d}/{enum}",
                   swmd=f"tools/audit/round9/D14/sweep/{d}/SWEEP.md", json=f"tools/audit/round9/D14/sweep/{thread}.json")
missing_sw = sorted(set(JUDGE_N) - set(SW))
assert not missing_sw, f"classes no sweep covered: {missing_sw}"
INST_BY_CLASS = collections.defaultdict(list)
for i in INSTANCES:
    INST_BY_CLASS[i["cls"]].append(i)
for cid, w in SW.items():
    # N final = judged findings + sweep-confirmed instances beyond them (PLAN section 7)
    assert w["N"] == JUDGE_N[cid] + len(INST_BY_CLASS[cid]), (cid, w["N"], JUDGE_N[cid], len(INST_BY_CLASS[cid]))
    want_rca = w["N"] >= 3 or cid == "N-restart"
    assert w["rca"] == want_rca, (cid, w["rca"], w["N"])
    assert (cid in RCA) == w["rca"], f"{cid}: rca {w['rca']} but RCA seat {'present' if cid in RCA else 'absent'}"
for fid, f in FIND.items():
    f["rca"] = SW[f["cls"]]["rca"]

def sweep_of(cls):
    if cls in SWEEP_OF:
        return SWEEP_OF[cls]
    return "S7" if cls in S7 else "S6"

PR = {p["id"]: p for p in PRS}
for p in PRS:
    p.setdefault("instances", [])
for i in INSTANCES:
    PR[i["pr"]]["instances"].append(i)
    f = i["file"]
    assert f in PR[i["pr"]]["edit"] or f in PR[i["pr"]]["borrows"], (i["id"], i["pr"], f)
for title, pid, text in LEADS:
    assert pid in PR, pid
    PR[pid]["notes"].append(f"{title}: {text}")
LANE_ORDER = collections.defaultdict(list)
for p in PRS:
    LANE_ORDER[p["lane"]].append(p["id"])

# lane predecessor is an implicit after edge
for lane, ids in LANE_ORDER.items():
    for a, b in zip(ids, ids[1:]):
        if a not in PR[b]["after"]:
            PR[b]["after"] = [a] + PR[b]["after"]

errors = []
# ---------------------------------------------------------------- placement
placed = collections.defaultdict(list)
for p in PRS:
    whole = [fid for fid, part in p["findings"] if part is None]
    if len(whole) + len(p["instances"]) > 5:
        errors.append(f"{p['id']}: {len(whole)} whole findings + {len(p['instances'])} sweep instances, over fixer.md's cap")
    for fid, part in p["findings"]:
        if fid not in FIND:
            errors.append(f"{p['id']}: {fid} is not a surviving finding")
        placed[fid].append((p["id"], part))
missing = sorted(set(FIND) - set(placed))
if missing:
    errors.append(f"unplaced findings: {missing}")
for fid, where in placed.items():
    wholes = [w for w in where if w[1] is None]
    if len(where) > 1 and len(wholes) != 1 and not all(w[1] for w in where[:-1]):
        errors.append(f"{fid} placed ambiguously: {where}")
    if len(wholes) > 1:
        errors.append(f"{fid} placed whole twice: {where}")

# must-one-PR siblings
SIB = [("D8-s1-03", "D12-s2-01"), ("D12-s1-01", "D12-s3-01"), ("D1-s5-01", "D1-s5-51"), ("D8-s2-02", "D8-s2-03")]
for a, b in SIB:
    pa = {w[0] for w in placed[a]}; pb = {w[0] for w in placed[b]}
    if not pa & pb:
        errors.append(f"siblings {a}/{b} not in one PR: {pa} {pb}")

# ---------------------------------------------------------------- graph
for p in PRS:
    for d in p["after"]:
        if d not in PR:
            errors.append(f"{p['id']}: after {d} names no PR")
order, seen, temp = [], set(), set()
def visit(n):
    if n in seen: return
    if n in temp: errors.append(f"cycle at {n}"); return
    temp.add(n)
    for d in PR[n]["after"]: visit(d)
    temp.discard(n); seen.add(n); order.append(n)
for p in PRS: visit(p["id"])
depth = {}
for n in order:
    depth[n] = 1 + max([depth[d] for d in PR[n]["after"]] or [0])
anc = {}
for n in order:
    s = set()
    for d in PR[n]["after"]:
        s |= {d} | anc[d]
    anc[n] = s

def touched(p):
    return set(p["edit"]) | set(p["borrows"])

# ownership: edits must be owned by the lane; borrows owned by the named lane
def owner(path):
    for ln, L in LANES.items():
        for g in L["owns"]:
            if g.endswith("/**") and path.startswith(g[:-2]): return ln
            if g == path: return ln
    return None
for p in PRS:
    for f in p["edit"]:
        o = owner(f)
        if o != p["lane"]:
            errors.append(f"{p['id']}: edits {f} owned by {o}")
    for f, ln in p["borrows"].items():
        o = owner(f)
        if o != ln:
            errors.append(f"{p['id']}: borrows {f} from {ln} but owner is {o}")
# concurrency: two PRs neither ordered before the other must not share a file
ids = [p["id"] for p in PRS]
for i, a in enumerate(ids):
    for b in ids[i + 1:]:
        if a in anc[b] or b in anc[a]:
            continue
        common = touched(PR[a]) & touched(PR[b])
        if common:
            errors.append(f"{a} and {b} can be open together and share {sorted(common)}")

# every rca class's barrier PR must come after every PR holding one of its instances
for cid, r in RCA.items():
    holders = set()
    for fid, f in FIND.items():
        if f["cls"] == cid:
            holders |= {w[0] for w in placed[fid]}
    holders |= {i["pr"] for i in INST_BY_CLASS[cid]}
    for h in holders - {r["barrier"]}:
        if h not in anc[r["barrier"]]:
            errors.append(f"{cid}: barrier PR {r['barrier']} is not after instance PR {h}")

# ---------------------------------------------------------------- derived
def classes_of(p):
    cs = []
    for fid, _ in p["findings"]:
        c = FIND[fid]["cls"]
        if c not in cs: cs.append(c)
    for i in p["instances"]:
        if i["cls"] not in cs: cs.append(i["cls"])
    return cs

def seam_counts(cid):
    c = collections.Counter(s.get("disposition", "?").replace("_", " ") for s in SW[cid]["seams"])
    return ", ".join(f"{v} {k}" for k, v in sorted(c.items()))

def barriers_of(pid):
    return [c for c, r in RCA.items() if r["barrier"] == pid]

def rca_beside(pid):
    out = []
    for c, r in RCA.items():
        if r["beside"] == pid: out.append(c)
    return out

def sev_max(p):
    rank = {"high": 3, "medium": 2, "low": 1}
    s = [FIND[f]["severity"] for f, _ in p["findings"]]
    return max(s, key=lambda x: rank[x]) if s else "barrier"

HARNESS_RE = re.compile(r"tools/audit/round9/[A-Za-z0-9_./-]+\.(?:py|mjs)")
def harnesses(fid):
    return sorted(set(HARNESS_RE.findall(FIND[fid]["seam_rule"])))

FIXTURE = {"F1.3", "F2.1", "F2.3", "F2.4", "F10.1", "F1.7"}
BLOCKED = {"F7.3": "tvofi ruling on the A3(e) decision", "F11.2": "tvofi decisions on D11-s1-01 (ruleset setting) and D11-s1-04 (delegated identity)",
           "F11.3": "tvofi approval (policy)"}
EFFORT_LOW = {"F8.1", "F8.2", "F8.3", "F5.1", "F9.1", "F9.2", "F6.3"}

STANDING_SHORT = (
    "Standing: read CLAUDE.md, every .claude/rules file and tools/audit/briefs/fixer.md first; call the owner tvofi. "
    "Cloud seat: no PRs, no GitHub comments, no issues, no gh; hand the branch and body off on handoff/{topic} and the Mac orchestrator pushes as the hpo-author App via tools/audit/app_push.sh; "
    "hpo-approver approves a non-code-owned PR, tvofi reviews a code-owned one (decision 0011). "
    "No heavy D3 (tvofi): no mutation pools, pre-screens or quiet windows; a D3-class mutation proof is one mutant applied in memory against the production symbol. "
    "Findings were measured at baseline 1936d5ca; main has since merged #1641, #1642 and #1643, so re-measure each finding at your merge base before fixing. "
    "Harnesses are at evidence commit {ev}: run them from that export, before and after, and cite the path with its sha1 (fixer.md step 3). "
    "Every figure is re-derived at your own merge base. Run python3 tests/structure.py before every hand-off; a budget raise is tvofi's, asked before the push (CLAUDE.md rule 2). "
    "Tests go in a class-named block in sorted position in tests/features.py or tests/entities.py, never at end of file; install both merge drivers before the first commit; re-record closures and budgets once, at the hand-off. "
    "Touch the claim files only to claim measured drift. No VERSION, manifest version or notes-heading edits. Part of #201."
)

def json_brief(p):
    L = LANES[p["lane"]]
    parts = []
    parts.append(f"Round-9 fix PR {p['id']} ({L['name']} lane), model {L['model'] if p['id'] not in MODEL_OVERRIDE else MODEL_OVERRIDE[p['id']]}.")
    if p["findings"]:
        fs = []
        for fid, part in p["findings"]:
            f = FIND[fid]
            s = f"{fid} ({f['severity']}, class {f['cls']}"
            if f["merged"]: s += ", merged " + " and ".join(f["merged"])
            s += ")"
            if part: s += f" [part: {part}]"
            fs.append(s)
        parts.append("Findings: " + "; ".join(fs) + ".")
    bs = barriers_of(p["id"])
    if bs:
        parts.append("Class barrier landing here: " + ", ".join(bs) + " (the RCA seat names its form; it is demonstrated failing on each round-9 instance re-introduced and passing on the fixed tree, and it does not fire on a healthy tree).")
    parts.extend(p["notes"])
    for c in p.get("carry", []):
        parts.append(c)
    if p["borrows"]:
        parts.append("Borrowed files (owned by another lane; the after edges order this PR against that lane's PRs on them, so no two open branches edit one file): " + ", ".join(f"{f} from {ln}" for f, ln in p["borrows"].items()) + ".")
    hs = sorted({h for fid, _ in p["findings"] for h in harnesses(fid)})
    if hs:
        parts.append(f"Finder harnesses (evidence commit {EV}): " + ", ".join(hs) + ".")
    if p["instances"]:
        parts.append("Sweep-confirmed instances in this PR (each sweep probe is the failing test): " + "; ".join(
            f"{i['id']} ({i['cls']}, {i['file'].replace(CC, '')}): {i['seam']}, {i['what']}; probe {i['probe']} at {SW[i['cls']]['commit']}" for i in p["instances"]) + ".")
    sw = []
    for c in classes_of(p):
        w = SW[c]
        en = "no enumerator script (dispositioned by hand in the class's SWEEP.md)" if w["enum"].endswith("SWEEP.md") else f"enumerator {w['enum']}"
        sw.append(f"{c}: N {w['N']} (judge {JUDGE_N[c]}), rca {'yes' if w['rca'] else 'no'}, sweep {w['thread']} at {w['commit']}, {en}, seams {seam_counts(c)}, all listed in {w['json']}")
    parts.append("Class sweeps (Phase D, final): " + "; ".join(sw) + ". The enumerator is the fixer.md step-8 rule: run it at the merge base and the head and put every seam it returns in Figures against its disposition (closed here, already guarded, or a distinct finding or instance by id). An instance seam of these classes that this PR's findings do not own belongs to the PR the plan names for it.")
    if p["tvofi"]:
        parts.append("Needs tvofi: " + p["tvofi"] + ".")
    parts.append(STANDING_SHORT.format(topic=LANES[p["lane"]]["topic"] + "-" + p["id"].split(".")[1], ev=EV))
    return " ".join(parts)

MODEL_OVERRIDE = {"F5.2": "sonnet", "F6.4": "sonnet", "F9.1": "sonnet", "F9.2": "sonnet", "F8.1": "sonnet", "F8.2": "sonnet", "F8.3": "sonnet", "F5.1": "sonnet"}
def model_of(pid):
    return MODEL_OVERRIDE.get(pid, LANES[PR[pid]["lane"]]["model"])

# ---------------------------------------------------------------- roster
groups = []
for p in PRS:
    cs = classes_of(p) or barriers_of(p["id"])
    g = collections.OrderedDict()
    g["group"] = "R9-" + p["id"]
    g["lane"] = p["lane"]
    g["issues"] = []
    g["findings"] = [fid for fid, _ in p["findings"]]
    g["sweep_instances"] = [i["id"] for i in p["instances"]]
    g["class"] = ",".join(cs)
    g["wave"] = depth[p["id"]]
    g["fixerModel"] = model_of(p["id"])
    g["reviewerModel"] = "opus"
    g["effort"] = "medium" if p["id"] in EFFORT_LOW else "high"
    g["fixture"] = p["id"] in FIXTURE
    g["owner_gate"] = p["tvofi"]
    g["rca"] = rca_beside(p["id"])
    g["barrier"] = barriers_of(p["id"])
    g["blocked_on"] = BLOCKED.get(p["id"])
    g["after"] = ["R9-" + d for d in p["after"]]
    g["resume"] = {"stage": "not-started", "branch": f"handoff/{LANES[p['lane']]['topic']}-{p['id'].split('.')[1]}",
                   "note": "Final at E2 with the Phase D sweeps folded in. issues[] is filled when Phase E files the class issues."}
    g["brief"] = json_brief(p)
    groups.append(g)

roster = collections.OrderedDict()
roster["_comment"] = [
    f"Round-9 fix wave: 145 surviving findings in 46 classes (judge 2f97b0a, CLASSES-DRAFT.json at bad458a3) plus {len(INSTANCES)} sweep-confirmed instances (Phase D, S1-S7), clustered into {len(PRS)} PRs in 11 lanes.",
    "One entry per PR. `lane` is the cloud fixer thread that owns the PR's files; lanes own disjoint file sets, and a PR that must edit another lane's file lists it under Borrowed in its brief and carries an `after` edge on that lane's last PR on it.",
    "`wave` is the dependency depth (1 = startable now). `owner_gate` names why tvofi must approve; those PRs are kept apart so nothing else waits on them.",
    "`issues` is empty until Phase E files the class issues. `sweep_instances` names the Phase D instances each PR carries beyond its findings (FIX-PLAN.md's instance table). Plan: handoff/round9/FIX-PLAN.md.",
]
roster["fork"] = "db878b29"
roster["fork_note"] = "origin/main after #1643 (db878b29) at plan time. Findings were measured at baseline 1936d5ca (v6.7.1); re-derive every number at your own merge base. Empty claims unless the group is marked fixture and drift is measured. Do not stamp from a wave seat."
roster["session"] = "cloud-r9"
roster["repo"] = "tvofi/heatpump_optimizer"
roster["serial"] = False
roster["struck"] = []
roster["groups"] = groups

os.makedirs(os.path.join(OUT, ".claude/workflows"), exist_ok=True)
with open(os.path.join(OUT, ".claude/workflows/wave-r9-groups.json"), "w") as fh:
    json.dump(roster, fh, indent=1, ensure_ascii=False); fh.write("\n")

# ---------------------------------------------------------------- tables for FIX-PLAN.md
def ftitle(fid):
    return FIND[fid]["title"].replace("|", "/")

T = []
T.append("## PR table (merge order within each lane; `after` gives the cross-lane edges)\n")
T.append("| PR | lane | wave | findings | classes | sev | model | tvofi | RCA seat beside | barrier here | after |")
T.append("|---|---|---|---|---|---|---|---|---|---|---|")
for p in PRS:
    fl = ", ".join([fid + ("*" if part else "") for fid, part in p["findings"]] + ["+" + i["id"] for i in p["instances"]]) or "(class barrier)"
    T.append(f"| {p['id']} | {p['lane']} | {depth[p['id']]} | {fl} | {', '.join(classes_of(p)) or '-'} | {sev_max(p)} | {model_of(p['id'])} | {'**yes**' if p['tvofi'] else '-'} | {', '.join(rca_beside(p['id'])) or '-'} | {', '.join(barriers_of(p['id'])) or '-'} | {', '.join(p['after']) or '-'} |")
T.append("\n`*` = part of a finding; the finding closes when every PR listing it has merged (see the split list). `+` = a Phase D sweep instance (table below).\n")
T.append("## Files per PR (package paths relative to custom_components/heatpump_optimizer/)\n")
T.append("| PR | edits (owned by its lane) | borrows (file from lane) | tvofi because |")
T.append("|---|---|---|---|")
for p in PRS:
    T.append(f"| {p['id']} | {', '.join(x.replace(CC, '') for x in p['edit'])} | {', '.join(f.replace(CC, '') + ' from ' + ln for f, ln in p['borrows'].items()) or '-'} | {p['tvofi'] or '-'} |")
T.append("")

T.append("## Finding to PR (all 145 survivors)\n")
T.append("| finding | sev | class | PR | title |")
T.append("|---|---|---|---|---|")
for fid in sorted(FIND, key=lambda x: (x.split("-")[0][0], int(re.sub(r'\D', '', x.split("-")[0])), x)):
    f = FIND[fid]
    where = ", ".join(w[0] + (f" ({w[1]})" if w[1] else "") for w in placed[fid])
    m = f" (merged: {', '.join(f['merged'])})" if f["merged"] else ""
    T.append(f"| {fid}{m} | {f['severity']} | {f['cls']} | {where} | {ftitle(fid)} |")

T.append("\n## Sweep-confirmed instances beyond the judged findings (Phase D)\n")
T.append("Line numbers are at baseline `1936d5ca`; each probe is under its sweep's commit. N final = judged findings + these.\n")
T.append("| instance | class | sweep | PR | seam | what fails | probe |")
T.append("|---|---|---|---|---|---|---|")
for i in INSTANCES:
    w = SW[i["cls"]]
    T.append(f"| {i['id']} | {i['cls']} | {w['thread']} @ `{w['commit']}` | {i['pr']} | {i['file'].replace(CC, '')}: {i['seam']} | {i['what']} | `{i['probe']}` |")

T.append("\n## Class to PR\n")
T.append("Seams are the sweep's own dispositions (`instance`, `guarded`, `not applicable`), every one listed in the lane brief of each lane that holds the class.\n")
T.append("| class | N judge | N final | rca | sweep | seams | PRs | barrier PR |")
T.append("|---|---|---|---|---|---|---|---|")
bycls = collections.OrderedDict()
for c in CLASSES["classes"]:
    cid = c["id"] or CLASS_SHORT[c["name"]]
    prs = []
    for f in c["findings"]:
        for w in placed[f["id"]]:
            if w[0] not in prs: prs.append(w[0])
    for i in INST_BY_CLASS[cid]:
        if i["pr"] not in prs: prs.append(i["pr"])
    bycls[cid] = (c, prs)
    w = SW[cid]
    T.append(f"| {cid} | {c['n']} | {w['N']} | {'yes' if w['rca'] else 'no'}{' (barriered)' if c['barriered'] else ''} | {w['thread']} @ `{w['commit']}` | {seam_counts(cid)} | {', '.join(prs)} | {RCA[cid]['barrier'] if cid in RCA else '- (N below 3, not barriered)'} |")

T.append("\n## Owned files and borrow edges\n")
T.append("| lane | name | thread model | owns |")
T.append("|---|---|---|---|")
for ln, L in LANES.items():
    T.append(f"| {ln} | {L['name']} | {L['model']} | {', '.join(x.replace(CC, '') for x in L['owns'])} |")

TABLES = "\n".join(T) + "\n"

# ---------------------------------------------------------------- lane briefs
STANDING_MD = open(os.path.join(os.path.dirname(__file__), "standing.md")).read()
for ln, L in LANES.items():
    lines = []
    ids_ = LANE_ORDER[ln]
    lines.append(f"# Round 9 fixer brief {ln}: {L['name']}\n")
    lines.append(f"Model for this thread: **{L['model']}** ({'the strongest available model' if L['model']=='opus' else 'sonnet'}). "
                 + ("Per-PR overrides: " + ", ".join(f"{i} {model_of(i)}" for i in ids_ if model_of(i) != L['model']) + ". " if any(model_of(i) != L['model'] for i in ids_) else "")
                 + "Reviews run on the strongest model in a different cloud session (never this one).\n")
    lines.append(f"Handoff branches: `handoff/{L['topic']}-<k>` for PR {ln}.<k>, cut from origin/main. Scratch: `$S/{L['topic']}/` with your worktree under it (absolute paths).\n")
    lines.append("## Files this lane owns\n")
    lines.append("Only this lane's PRs edit these, except where another lane's PR lists one under Borrows; the `after` edges in the roster order that PR against yours so the two are never open together. Before opening a PR, check that no borrower of its files is open.\n")
    for f in L["owns"]:
        lines.append(f"- `{f}`")
    lines.append("\nShared ledgers, owned by no lane (class-named block in sorted position; re-record once at the hand-off): " + ", ".join(f"`{x}`" for x in EXEMPT) + ".\n")
    lines.append("## PRs, in merge order\n")
    for pid in ids_:
        p = PR[pid]
        lines.append(f"### {pid}: {p['title']}\n")
        lines.append(f"- Wave (dependency depth): {depth[pid]}. After: {', '.join(p['after']) or 'nothing; start now'}.")
        lines.append(f"- Model: {model_of(pid)}. Effort: {'medium' if pid in EFFORT_LOW else 'high'}. Golden drift plausible: {'yes, claim what you measure' if pid in FIXTURE else 'not expected'}.")
        lines.append(f"- Needs tvofi: {'**yes** - ' + p['tvofi'] if p['tvofi'] else 'no'}.")
        if BLOCKED.get(pid):
            lines.append(f"- Blocked on: {BLOCKED[pid]}.")
        rb = rca_beside(pid); br = barriers_of(pid)
        if rb: lines.append(f"- RCA seat(s) starting beside this PR (strongest model, separate thread): {', '.join(rb)}.")
        if br: lines.append(f"- Class barrier landing in this PR: {', '.join(br)}. Its form comes from that class's RCA seat; demonstrate it failing on each round-9 instance re-introduced, passing on the fixed tree, silent on a healthy tree.")
        lines.append(f"- Edits: {', '.join('`'+x+'`' for x in p['edit'])}.")
        if p["borrows"]:
            lines.append(f"- Borrows: {', '.join('`'+f+'` from '+l for f, l in p['borrows'].items())}.")
        if p["findings"]:
            lines.append("- Findings:")
            for fid, part in p["findings"]:
                f = FIND[fid]
                m = f" (merged: {', '.join(f['merged'])})" if f["merged"] else ""
                pt = f" **Part only:** {part}." if part else ""
                lines.append(f"  - **{fid}**{m}, {f['severity']}, class {f['cls']} ({f['verdict']}): {f['title']}.{pt}")
                lines.append(f"    - Seam rule: `{f['seam_rule']}`")
        elif not p["instances"]:
            lines.append("- Findings: none; this PR is a class barrier.")
        if p["instances"]:
            lines.append("- Sweep-confirmed instances (Phase D; the probe is your failing test):")
            for i in p["instances"]:
                lines.append(f"  - **{i['id']}**, class {i['cls']}, `{i['file']}`: {i['seam']}. {i['what'][0].upper() + i['what'][1:]}. Probe: `{i['probe']}` at `{SW[i['cls']]['commit']}`.")
        if p.get("carry"):
            lines.append("- Carry-ins:")
            for c in p["carry"]:
                lines.append(f"  - {c}")
        lines.append("- Fix notes:")
        for n in p["notes"]:
            lines.append(f"  - {n}")
        cs = classes_of(p) or barriers_of(pid)
        lines.append("- Class sweeps (final; the seam lists are at the end of this brief): " + "; ".join(
            f"{c} N {SW[c]['N']} (judge {JUDGE_N[c]}), rca {'yes' if SW[c]['rca'] else 'no'}, {SW[c]['thread']} @ `{SW[c]['commit']}`, enumerator `{SW[c]['enum']}`" for c in cs) + ".")
        lines.append("")
    lane_classes = []
    for pid in ids_:
        for c in (classes_of(PR[pid]) or barriers_of(pid)):
            if c not in lane_classes: lane_classes.append(c)
    lines.append("## Class sweeps for this lane's classes (Phase D, final)\n")
    lines.append("Each class's enumerator is your `fixer.md` step-8 rule. Run it from an export of the sweep commit at your merge base and your head; every seam it returns goes in `## Figures` against its disposition. The lists below are the sweep's own, at baseline `1936d5ca` (line numbers are baseline lines). A seam marked `instance` belongs to the finding or instance its note names, and that one's PR closes it, which may be in another lane.\n")
    for c in lane_classes:
        w = SW[c]
        lines.append(f"### {c}: N {w['N']} (judge {JUDGE_N[c]}), rca {'yes' if w['rca'] else 'no'}\n")
        lines.append(f"- Sweep {w['thread']}, commit `{w['commit']}` (branch `handoff/audit-r9-sweep-{w['thread'].lower()}`): `{w['dir']}/`, its `SWEEP.md`, and `{w['json']}`. Enumerator: `{w['enum']}`. Gate seconds the sweep measured: {w['gate'] if w['gate'] is not None else 'not measured'}.")
        if c in RCA:
            lines.append(f"- RCA seat beside {RCA[c]['beside']}; barrier lands in {RCA[c]['barrier']}.")
        lines.append(f"- Barrier proposal (the sweep's; the RCA seat decides the form): {w['barrier']}")
        lines.append(f"- Seams ({seam_counts(c)}):")
        for sm in w["seams"]:
            where = sm.get("path") or sm.get("seam") or "?"
            note = (sm.get("note") or "").replace("\n", " ")
            lines.append(f"  - {sm.get('disposition', '?').replace('_', ' ')}: `{where}`" + (f" - {note}" if note else ""))
        lines.append("")
    lines.append(STANDING_MD.format(topic=L["topic"], lane=ln))
    os.makedirs(os.path.join(OUT, "handoff/round9/fix"), exist_ok=True)
    with open(os.path.join(OUT, f"handoff/round9/fix/{ln}.md"), "w") as fh:
        fh.write("\n".join(lines) + "\n")

# ---------------------------------------------------------------- report
print(f"PRs {len(PRS)}; lanes {len(LANES)}; placed {len(placed)}/145; tvofi PRs {sum(1 for p in PRS if p['tvofi'])}; max depth {max(depth.values())}")
print("wave counts", collections.Counter(depth.values()))
print("topo order", " ".join(order))
if errors:
    print("ERRORS:")
    for e in errors: print(" ", e)
    sys.exit(1)
print("OK")

# ---------------------------------------------------------------- merge order
rank = {"high": 0, "medium": 1, "low": 2, "barrier": 3}
mo = sorted(PRS, key=lambda p: (depth[p["id"]], rank[sev_max(p)], p["tvofi"] is not None, int(p["lane"][1:]), p["id"]))
# ensure topological validity of the sorted order
pos = {p["id"]: i for i, p in enumerate(mo)}
for p in PRS:
    for d in p["after"]:
        assert pos[d] < pos[p["id"]], (d, p["id"])
TABLES += "\n## Proposed merge queue (priority among PRs that are ready: review `merge`, CI green, `after` edges merged; one merge at a time)\n\n"
TABLES += "Ordered by dependency depth, then severity, then non-owner-gated first. The orchestrator may swap two adjacent PRs that share no file and no edge; it may not move a PR ahead of its `after`.\n\n"
for i, p in enumerate(mo, 1):
    TABLES += f"{i}. {p['id']} ({sev_max(p)}{', tvofi' if p['tvofi'] else ''}{', fixture' if p['id'] in FIXTURE else ''}) - {p['title']}\n"

# ---------------------------------------------------------------- FIX-PLAN.md
def longest_chain():
    best = {}
    for n in order:
        prev = max(PR[n]["after"], key=lambda d: best[d][0], default=None)
        best[n] = (1 + (best[prev][0] if prev else 0), (best[prev][1] if prev else []) + [n])
    return max(best.values(), key=lambda x: x[0])
chain_len, chain = longest_chain()
rca_rows = "\n".join(
    f"| {k} | {JUDGE_N[k]} | {SW[k]['N']} | {r['beside']} | {r['barrier']} | {r['note']} |" for k, r in RCA.items())
fill = dict(
    n_prs=len(PRS), n_inst=len(INSTANCES), n_rca=len(RCA), n_tvofi=sum(1 for p in PRS if p["tvofi"]),
    n_borrow=sum(1 for p in PRS if p["borrows"]), rca_rows=rca_rows,
    tvofi_list=", ".join(p["id"] for p in PRS if p["tvofi"]),
    chain=" -> ".join(chain), chain_len=chain_len, max_depth=max(depth.values()),
    ledger_notes="\n".join("- " + x for x in LEDGER_NOTES),
    leads="\n".join(f"- **{t}** -> {pid}: {x}" for t, pid, x in LEADS),
    wave1=", ".join(p["id"] for p in PRS if depth[p["id"]] == 1),
    last_pr=mo[-1]["id"],
)
head = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "FIX-PLAN-head.md")).read()
for k, v in fill.items():
    head = head.replace("{" + k + "}", str(v))
left = re.findall(r"\{[a-z_0-9]+\}", head)
assert not left, left
with open(os.path.join(OUT, "handoff/round9/FIX-PLAN.md"), "w") as fh:
    fh.write(head + "\n" + TABLES)
print("chain", chain_len, " ".join(chain))
print("merge order", " ".join(p["id"] for p in mo))
