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
                  SWEEP_LABEL, SWEEP_DIR, INSTANCES, LEADS, LEDGER_NOTES, N_RCA, CARRIES, ROUTING, ROLE_MODELS,
                  REFUSED, CAP_EXCEPTIONS)

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

# ---------------------------------------------------------------- Phase E class issues (#1644-#1689)
ISSUE_DIR = "/mnt/project-files/audit-r9/issues"
_IMAP = json.load(open(f"{ISSUE_DIR}/ISSUE-MAP.json"))
ISSUE_OF, ISSUE_DROPPED = {}, {}
for x in json.load(open(f"{ISSUE_DIR}/INDEX.json")):
    cid = x["class"] if x["class"] in JUDGE_N else CLASS_SHORT[x["class"]]
    want = {f["id"] for f in FIND.values() if f["cls"] == cid}
    assert set(x["finding_ids"]) == want, (cid, sorted(set(x["finding_ids"]) ^ want))
    if x["slug"] in _IMAP["closed_not_planned"]:
        ISSUE_DROPPED[cid] = (_IMAP["map"][x["slug"]], _IMAP["closed_not_planned"][x["slug"]])
    else:
        ISSUE_OF[cid] = _IMAP["map"][x["slug"]]
assert set(ISSUE_OF) | set(ISSUE_DROPPED) == set(JUDGE_N), sorted(set(JUDGE_N) - set(ISSUE_OF) - set(ISSUE_DROPPED))

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
    i.setdefault("kind", "instance")
    assert i["kind"] in ("instance", "latent"), i["id"]
    INST_BY_CLASS[i["cls"]].append(i)
def counted(cid):
    return [i for i in INST_BY_CLASS[cid] if i["kind"] == "instance"]
for cid in N_RCA:
    assert cid in SW and cid in RCA, cid
for cid, w in SW.items():
    # N final = judged findings + counted instances beyond them (PLAN section 7). The sweep's N
    # stands unless an RCA seat changed it (N_RCA, with its reason); either way it must equal the
    # judged count plus the instances this plan places.
    w["N_sweep"] = w["N"]
    if cid in N_RCA:
        w["N"] = N_RCA[cid][1]
    assert w["N"] == JUDGE_N[cid] + len(counted(cid)), (cid, w["N"], JUDGE_N[cid], len(counted(cid)))
    want_rca = w["N_sweep"] >= 3 or cid == "N-restart"
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
    p.setdefault("covers", [])
for i in INSTANCES:
    PR[i["pr"]]["instances"].append(i)
    f = i["file"]
    # the seam's file is edited by the PR that closes it: `pr`, or `closed_by` where the barrier
    # closes the seam by construction and `pr` carries only its regression test
    fixer_pr = PR[i.get("closed_by") or i["pr"]]
    assert f in fixer_pr["edit"] or f in fixer_pr["borrows"], (i["id"], fixer_pr["id"], f)
    if i.get("closed_by"):
        assert i["closed_by"] in PR, i["id"]
for p in PRS:
    p.setdefault("carry", [])
for dest, cid, text in CARRIES:
    assert dest in PR, dest
    assert cid in RCA, cid
    PR[dest]["carry"].append(f"RCA carry-in ({cid}, 2026-09-26): {text}")
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
    if len(whole) + len(p["instances"]) > 5 and p["id"] not in CAP_EXCEPTIONS:
        errors.append(f"{p['id']}: {len(whole)} whole findings + {len(p['instances'])} sweep instances, over fixer.md's cap")
    if p["id"] in CAP_EXCEPTIONS and len(whole) + len(p["instances"]) <= 5:
        errors.append(f"{p['id']}: listed in CAP_EXCEPTIONS but within the cap; drop the exception")
    for fid, part in p["findings"]:
        if fid not in FIND:
            errors.append(f"{p['id']}: {fid} is not a surviving finding")
        placed[fid].append((p["id"], part))
# a finding tvofi refused is placed by its refusal and must not also sit in a PR
for fid, why in REFUSED.items():
    if fid not in FIND:
        errors.append(f"refused {fid} is not a surviving finding")
    elif fid in placed:
        errors.append(f"refused {fid} is also placed in {placed[fid]}")
for pid in CAP_EXCEPTIONS:
    if pid not in {p["id"] for p in PRS}:
        errors.append(f"cap exception {pid} names no PR")
missing = sorted(set(FIND) - set(placed) - set(REFUSED))
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

# every rca class's barrier PR must come after every PR holding one of its instances, except the
# residual ones its RCA seat measured the barrier's check not to read (printed below), and with an
# instance another PR closes counted at the PR that closes it
known_ids = set(FIND) | {i["id"] for i in INSTANCES}
residual_report = []
for cid, r in RCA.items():
    for x in r.get("residual", []):
        if x not in known_ids:
            errors.append(f"{cid}: residual {x} names no finding or instance")
    holders = set()
    for fid, f in FIND.items():
        if f["cls"] == cid and fid not in r.get("residual", []):
            holders |= {w[0] for w in placed[fid]}
    holders |= {i.get("closed_by") or i["pr"] for i in INST_BY_CLASS[cid] if i["id"] not in r.get("residual", [])}
    for h in holders - {r["barrier"]}:
        if h not in anc[r["barrier"]]:
            errors.append(f"{cid}: barrier PR {r['barrier']} is not after instance PR {h}")
    for x in r.get("residual", []):
        where = [w[0] for w in placed.get(x, [])] or [i["pr"] for i in INSTANCES if i["id"] == x]
        before = all(w == r["barrier"] or w in anc[r["barrier"]] for w in where)
        residual_report.append(f"{cid}: {x} in {', '.join(where)} ({'before' if before else 'after or beside'} barrier {r['barrier']})")
    # a closed_by instance's test PR must follow the PR that closes it
    for i in INST_BY_CLASS[cid]:
        if i.get("closed_by") and i["closed_by"] not in anc[i["pr"]]:
            errors.append(f"{i['id']}: test PR {i['pr']} is not after closing PR {i['closed_by']}")

# a PR that covers findings (a class-level barrier tvofi commissioned beyond the RCA's) must come after
# every PR that fixes one of them, and must run on the strongest model
for p in PRS:
    for fid in p["covers"]:
        if fid not in FIND:
            errors.append(f"{p['id']}: covers {fid}, not a surviving finding"); continue
        for w in placed.get(fid, []):
            if w[0] != p["id"] and w[0] not in anc[p["id"]]:
                errors.append(f"{p['id']}: covers {fid} but is not after {w[0]}, which fixes it")
    if p["covers"] and ROUTING[p["id"]][0] != "opus":
        errors.append(f"{p['id']}: a covering barrier not routed to the strongest model")

# every class issue closes in one PR, the one after every other PR holding the class (Fixes #N there,
# Part of #N everywhere else); a dropped issue must be held by no PR
def issue_classes(p):
    cs = []
    for fid, _ in p["findings"]:
        cs.append(FIND[fid]["cls"])
    cs += [i["cls"] for i in p["instances"]] + [c for c, r in RCA.items() if r["barrier"] == p["id"]] + [FIND[f]["cls"] for f in p["covers"]]
    out = []
    for c in cs:
        if c not in out: out.append(c)
    return out
HOLDERS = collections.defaultdict(set)
for p in PRS:
    for c in issue_classes(p):
        HOLDERS[c].add(p["id"])
for i in INSTANCES:
    if i.get("closed_by"): HOLDERS[i["cls"]].add(i["closed_by"])
CLOSER = {}
for c, hs in HOLDERS.items():
    if c in ISSUE_DROPPED:
        errors.append(f"{c}: its issue #{ISSUE_DROPPED[c][0]} is closed as not planned, but {sorted(hs)} hold it")
        continue
    last = [h for h in hs if all(o == h or o in anc[h] for o in hs)]
    if len(last) != 1:
        errors.append(f"{c} (#{ISSUE_OF[c]}): no single PR follows every holder {sorted(hs)}")
    else:
        CLOSER[c] = last[0]
for c in ISSUE_OF:
    if c not in HOLDERS:
        errors.append(f"{c} (#{ISSUE_OF[c]}) is held by no PR")
def issue_refs(pid):
    return [(ISSUE_OF[c], c, CLOSER.get(c) == pid) for c in issue_classes(PR[pid]) if c in ISSUE_OF]
def issue_text(pid):
    return "; ".join(f"{'Fixes' if closes else 'Part of'} #{n} ({c})" for n, c, closes in issue_refs(pid))

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

FIXTURE = {"F1.3", "F2.1", "F2.3", "F2.4", "F10.1", "F1.7", "F1.10", "F2.5"}
# every tvofi ask was answered at 19:16Z; what remains blocked is an action, not a decision
BLOCKED = {"F10.5": "the new ledger-writer App identity and its credential, a Mac/tvofi setup action under decision 0011 (card C5); the fixer's work does not wait on it, the writer's first real push does"}
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
    "Resumability (tvofi 19:05Z): commit and push to your handoff branch at every step boundary (failing test written, fix green, body drafted) and at least every 30 minutes of work, never holding unpushed work across a long run; with every push update the resume note named in this entry's resume field (last completed step, next step, branch at commit, open questions); at each milestone append one dated line to the round-9 resume log and its git mirror, as the resume field says. A crashed seat is restarted from its branch and note, not from scratch. "
    "Class issues: write Fixes #N only for an issue this entry marks Fixes, Part of #N for every other listed issue. "
    "Touch the claim files only to claim measured drift. No VERSION, manifest version or notes-heading edits. Part of #201."
)

def json_brief(p):
    L = LANES[p["lane"]]
    parts = []
    parts.append(f"Round-9 fix PR {p['id']} ({L['name']} lane). Models: fixer {model_of(p['id'])} ({why_of(p['id'])}); reviewer opus in another session; "
                 + ("RCA and judge opus; " if barriers_of(p['id']) or rca_beside(p['id']) else "")
                 + "runner work (scoped-gate and stress re-runs, closure and budget re-records, report rendering) goes to a haiku subagent that reports numbers and decides nothing; record upkeep (resume note, RESUME.md line, delivery row) may go to sonnet.")
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
    for c in bs:
        r = RCA[c]
        parts.append(f"Class barrier landing here: {c} (RCA seat reported, process state {r['state']}). Form: {r['form']}. "
                     f"Prototype {r['proto']}; cherry-pick {r['pick']}. Lines: {r['lines']}. Ownership: {r['owned']}. "
                     + (f"Residual, which this barrier's check does not read (its RCA's measurement): {', '.join(r['residual'])}. " if r.get('residual') else "")
                     + "Demonstrate it failing on each round-9 instance re-introduced, passing on the fixed tree, and silent on a healthy tree, as the RCA's own runs did; set the class's entry in tools/audit/bugclasses.json (detector, barrier, status) in this PR.")
    if p["covers"]:
        parts.append("Covers, as a class-level check (closes none of them; each closes in the PR that fixes it): " + ", ".join(p["covers"]) + ".")
    if p["id"] in CAP_EXCEPTIONS:
        parts.append("Over fixer.md's five-item cap by recorded exception: " + CAP_EXCEPTIONS[p["id"]] + ".")
    parts.extend(p["notes"])
    for c in p.get("carry", []):
        parts.append(c)
    if p["borrows"]:
        parts.append("Borrowed files (owned by another lane; the after edges order this PR against that lane's PRs on them, so no two open branches edit one file): " + ", ".join(f"{f} from {ln}" for f, ln in p["borrows"].items()) + ".")
    hs = sorted({h for fid, _ in p["findings"] for h in harnesses(fid)})
    if hs:
        parts.append(f"Finder harnesses (evidence commit {EV}): " + ", ".join(hs) + ".")
    if p["instances"]:
        def _probe(i):
            return f"probe {i['probe']} at {SW[i['cls']]['commit']}" if i["src"] != "RCA" else f"failing test: {i['probe']}"
        def _tag(i):
            t = [i["cls"], i["file"].replace(CC, ""), "found by " + i["src"]]
            if i["kind"] == "latent": t.append("latent seam, fills a slot, not counted in N")
            if i.get("closed_by"): t.append("closed by " + i["closed_by"] + "; this PR adds its regression test")
            return ", ".join(t)
        parts.append("Instances in this PR beyond its findings: " + "; ".join(
            f"{i['id']} ({_tag(i)}): {i['seam']}, {i['what']}; {_probe(i)}" for i in p["instances"]) + ".")
    sw = []
    for c in classes_of(p):
        w = SW[c]
        en = "no enumerator script (dispositioned by hand in the class's SWEEP.md)" if w["enum"].endswith("SWEEP.md") else f"enumerator {w['enum']}"
        nn = f"N {w['N']} (judge {JUDGE_N[c]}" + (f", sweep {w['N_sweep']}, RCA fold {w['N']}" if c in N_RCA else "") + ")"
        sw.append(f"{c}: {nn}, rca {'yes' if w['rca'] else 'no'}, sweep {w['thread']} at {w['commit']}, {en}, seams {seam_counts(c)}, all listed in {w['json']}")
    parts.append("Class sweeps (Phase D, final): " + "; ".join(sw) + ". The enumerator is the fixer.md step-8 rule: run it at the merge base and the head and put every seam it returns in Figures against its disposition (closed here, already guarded, or a distinct finding or instance by id). An instance seam of these classes that this PR's findings do not own belongs to the PR the plan names for it.")
    if p["tvofi"]:
        parts.append("Needs tvofi: " + p["tvofi"] + ".")
    if issue_refs(p["id"]):
        parts.append("Class issues, in the body exactly as written here: " + issue_text(p["id"]) + ". Fixes #N only where this entry says so, because this PR follows every other PR holding that class; everything else is Part of #N.")
    parts.append(STANDING_SHORT.format(topic=LANES[p["lane"]]["topic"] + "-" + p["id"].split(".")[1], ev=EV))
    return " ".join(parts)

def model_of(pid):
    return ROUTING[pid][0]
def why_of(pid):
    m, w = ROUTING[pid]
    if w: return w
    return {"F5": "translated text and config UX, small and mechanical", "F6": "card layout, text and keyboard fixes, small and mechanical",
            "F7": "small entity-attribute fixes", "F8": "documentation lane", "F9": "test-pin lane",
            "F11": "non-code-owned parsers with the finder's harness as oracle"}[PR[pid]["lane"]]
for _p in PRS:
    if ROUTING[_p["id"]][0] == "opus" and not ROUTING[_p["id"]][1]:
        errors.append(f"{_p['id']}: routed to the strongest model without a reason")
    if barriers_of(_p["id"]) and ROUTING[_p["id"]][0] != "opus":
        errors.append(f"{_p['id']}: carries a class barrier but is not routed to the strongest model")
def branch_of(pid):
    return f"handoff/{LANES[PR[pid]['lane']]['topic']}-{pid.split('.')[1]}"
def resume_of(pid):
    b = branch_of(pid); ln = PR[pid]["lane"]
    return collections.OrderedDict([
        ("stage", "not-started"),
        ("branch", b), ("commit", None), ("last_step", None),
        ("next_step", "fixer.md step 1 at a fresh merge base: re-measure each finding, then write the failing test"),
        ("note_file", f"handoff/round9/fix/resume/{pid}.md on {b}"),
        ("review_branch", b + "-review"), ("review_note_file", f"handoff/round9/fix/resume/{pid}-review.md on {b}-review"),
        ("plan", f"handoff/audit-r9-fixplan: handoff/round9/fix/{ln}.md section {pid}, handoff/round9/FIX-PLAN.md sections 11 and 12, this roster"),
        ("log", "/mnt/project-files/audit-r9/RESUME.md (cloud), mirrored append-only at handoff/audit-r9-plan:handoff/round9/RESUME.md (Mac and any seat without /mnt)"),
        ("pickup_cloud", f"git fetch origin {b}; if it exists, git worktree add --detach $S/{LANES[ln]['topic']}/wt FETCH_HEAD, read the note file, check its commit equals the fetched head (if the branch is ahead, trust the branch and its log), git merge origin/main if main moved and re-run fixer.md steps 2-8, then continue at next_step; if it does not exist, cut a worktree from origin/main and start at fixer.md step 1"),
        ("pickup_local", f"the same commands from the Mac checkout, reading the plan and the log from git alone (handoff/audit-r9-fixplan and handoff/audit-r9-plan); a Mac seat appends its milestone lines to the mirror only, and the orchestrator copies them into the /mnt log at its next pass"),
        ("note", "Final at E2 with the Phase D sweeps, the round-9 RCA results and tvofi's resumability and model-routing rules folded in (2026-09-26). The seat's resume note on its branch outranks this entry for in-flight state; the orchestrator (or a sonnet record seat) updates stage, commit, last_step and next_step here at each hand-off and merge. issues[] and fixes[] are from the Phase E issue map (2026-09-26)."),
    ])

# ---------------------------------------------------------------- roster
groups = []
for p in PRS:
    cs = classes_of(p) or barriers_of(p["id"]) or sorted({FIND[f]["cls"] for f in p["covers"]})
    g = collections.OrderedDict()
    g["group"] = "R9-" + p["id"]
    g["lane"] = p["lane"]
    g["issues"] = sorted(n for n, _, _ in issue_refs(p["id"]))
    g["fixes"] = sorted(n for n, _, closes in issue_refs(p["id"]) if closes)
    g["findings"] = [fid for fid, _ in p["findings"]]
    g["covers"] = p["covers"]
    g["cap_exception"] = CAP_EXCEPTIONS.get(p["id"])
    g["sweep_instances"] = [i["id"] for i in p["instances"]]
    g["class"] = ",".join(cs)
    g["wave"] = depth[p["id"]]
    g["fixerModel"] = model_of(p["id"])
    g["reviewerModel"] = "opus"
    g["model"] = collections.OrderedDict([("fixer", model_of(p["id"])), ("fixer_why", why_of(p["id"])), ("reviewer", "opus"),
                  ("rca", "opus" if (barriers_of(p["id"]) or rca_beside(p["id"])) else None), ("runner", "haiku"), ("record", "sonnet")])
    g["effort"] = "medium" if p["id"] in EFFORT_LOW else "high"
    g["fixture"] = p["id"] in FIXTURE
    g["owner_gate"] = p["tvofi"]
    g["rca"] = rca_beside(p["id"])
    g["barrier"] = barriers_of(p["id"])
    g["barrier_prototype"] = [RCA[c]["proto"] for c in barriers_of(p["id"])]
    g["blocked_on"] = BLOCKED.get(p["id"])
    g["after"] = ["R9-" + d for d in p["after"]]
    g["resume"] = resume_of(p["id"])
    g["brief"] = json_brief(p)
    groups.append(g)

roster = collections.OrderedDict()
roster["_comment"] = [
    f"Round-9 fix wave: 145 surviving findings in 46 classes (judge 2f97b0a, CLASSES-DRAFT.json at bad458a3) plus {sum(1 for i in INSTANCES if i['kind'] == 'instance')} counted instances beyond them (Phase D sweeps S1-S7 and the RCA fold) and {sum(1 for i in INSTANCES if i['kind'] == 'latent')} latent seams, clustered into {len(PRS)} PRs in 11 lanes.",
    "One entry per PR. `lane` is the cloud fixer thread that owns the PR's files; lanes own disjoint file sets, and a PR that must edit another lane's file lists it under Borrowed in its brief and carries an `after` edge on that lane's last PR on it.",
    "`wave` is the dependency depth (1 = startable now). `owner_gate` names why tvofi must approve; those PRs are kept apart so nothing else waits on them.",
    "`model` routes each role (tvofi 19:05Z): the fixer to the cheapest feasible model with the reason when it is the strongest, reviews and RCA to opus, runners to haiku, record upkeep to sonnet. `resume` names the branch, the resume note on it, and how a cloud or a Mac seat picks the PR up (FIX-PLAN.md sections 11 and 12).",
    "`issues` lists the Phase E class issues (#1644-#1688; #1689 closed as not planned with D8-s2-01) each PR's findings, instances, barrier or covers belong to, and `fixes` the ones it closes, because it follows every other PR holding that class; the body says Fixes #N for those and Part of #N for the rest. `sweep_instances` names the Phase D instances each PR carries beyond its findings (FIX-PLAN.md's instance table). Plan: handoff/round9/FIX-PLAN.md.",
]
roster["fork"] = "db878b29"
roster["fork_note"] = "origin/main after #1643 (db878b29) at plan time. Findings were measured at baseline 1936d5ca (v6.7.1); re-derive every number at your own merge base. Empty claims unless the group is marked fixture and drift is measured. Do not stamp from a wave seat."
roster["session"] = "cloud-r9"
roster["repo"] = "tvofi/heatpump_optimizer"
roster["serial"] = False
roster["struck"] = []
roster["refused"] = collections.OrderedDict((fid, why) for fid, why in REFUSED.items())
roster["decisions"] = "tvofi answered all 35 asks at 19:16Z (cmsg_01EL5jLi4rokGBbkaevYXSJV6CQVMDN96YfVMTcN5QGSx2); handoff/round9/TVOFI-ASKS.md, DECISIONS, records each card's answer and where it is applied"
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
    fl = ", ".join([fid + ("*" if part else "") for fid, part in p["findings"]] + ["+" + i["id"] for i in p["instances"]]) or ("(barrier; covers " + ", ".join(p["covers"]) + ")" if p["covers"] else "(class barrier)")
    T.append(f"| {p['id']}{' (cap exception)' if p['id'] in CAP_EXCEPTIONS else ''} | {p['lane']} | {depth[p['id']]} | {fl} | {', '.join(classes_of(p)) or ', '.join(sorted({FIND[f]['cls'] for f in p['covers']})) or '-'} | {sev_max(p)} | {model_of(p['id'])} | {'**yes**' if p['tvofi'] else '-'} | {', '.join(rca_beside(p['id'])) or '-'} | {', '.join(barriers_of(p['id'])) or '-'} | {', '.join(p['after']) or '-'} |")
T.append("\n`*` = part of a finding; `(cap exception)` = over fixer.md's five-item cap by tvofi's recorded choice; the finding closes when every PR listing it has merged (see the split list). `+` = a Phase D sweep instance (table below).\n")
T.append("## Files per PR (package paths relative to custom_components/heatpump_optimizer/)\n")
T.append("| PR | edits (owned by its lane) | borrows (file from lane) | tvofi because |")
T.append("|---|---|---|---|")
for p in PRS:
    T.append(f"| {p['id']} | {', '.join(x.replace(CC, '') for x in p['edit'])} | {', '.join(f.replace(CC, '') + ' from ' + ln for f, ln in p['borrows'].items()) or '-'} | {p['tvofi'] or '-'} |")
T.append("")

T.append("## Finding to PR (all 145 survivors; refused ones name tvofi's card)\n")
T.append("| finding | sev | class | PR | title |")
T.append("|---|---|---|---|---|")
for fid in sorted(FIND, key=lambda x: (x.split("-")[0][0], int(re.sub(r'\D', '', x.split("-")[0])), x)):
    f = FIND[fid]
    where = ", ".join(w[0] + (f" ({w[1]})" if w[1] else "") for w in placed[fid]) if fid in placed else "**refused** (" + REFUSED[fid].split(" (")[1].split(")")[0] + ")"
    m = f" (merged: {', '.join(f['merged'])})" if f["merged"] else ""
    T.append(f"| {fid}{m} | {f['severity']} | {f['cls']} | {where} | {ftitle(fid)} |")

T.append("\n## Instances beyond the judged findings (Phase D sweeps and the RCA fold)\n")
T.append("Line numbers are at baseline `1936d5ca`. A sweep instance's probe is under its sweep's commit; an RCA instance's failing test is its RCA prototype or evidence. N final = judged findings + the rows of kind `instance`; a `latent` seam fills a PR slot and is not counted. `closed by` names the PR whose change closes the seam when the row's PR carries only its regression test.\n")
T.append("| instance | class | found by | kind | PR | closed by | seam | what fails | failing test |")
T.append("|---|---|---|---|---|---|---|---|---|")
for i in INSTANCES:
    w = SW[i["cls"]]
    src = f"{w['thread']} @ `{w['commit']}`" if i["src"] != "RCA" else f"RCA ({RCA[i['cls']]['slug']})"
    T.append(f"| {i['id']} | {i['cls']} | {src} | {i['kind']} | {i['pr']} | {i.get('closed_by') or '-'} | {i['file'].replace(CC, '')}: {i['seam']} | {i['what']} | {i['probe']} |")
T.append("\nRe-dispositioned at the RCA fold, no longer instances: **P1-sw1** and **P1-sw2** (not store-reachable; defence-in-depth, P1 RCA) and **P9-sw1** (a box-metric artefact, 0 px shared ink, P9 RCA).")

T.append("\n## Class to PR\n")
T.append("Seams are the sweep's own dispositions (`instance`, `guarded`, `not applicable`), every one listed in the lane brief of each lane that holds the class.\n")
T.append("| class | issue | fixed in | N judge | N sweep | N final | rca | sweep | seams | PRs | barrier PR |")
T.append("|---|---|---|---|---|---|---|---|---|---|---|")
bycls = collections.OrderedDict()
for c in CLASSES["classes"]:
    cid = c["id"] or CLASS_SHORT[c["name"]]
    prs = []
    for f in c["findings"]:
        if f["id"] in REFUSED:
            prs.append(f"{f['id']} refused"); continue
        for w in placed[f["id"]]:
            if w[0] not in prs: prs.append(w[0])
    for i in INST_BY_CLASS[cid]:
        if i["pr"] not in prs: prs.append(i["pr"])
    bycls[cid] = (c, prs)
    w = SW[cid]
    iss = f"#{ISSUE_OF[cid]}" if cid in ISSUE_OF else f"#{ISSUE_DROPPED[cid][0]} (closed, not planned)"
    T.append(f"| {cid} | {iss} | {CLOSER.get(cid, '-')} | {c['n']} | {w['N_sweep']} | {w['N']} | {'yes' if w['rca'] else 'no'}{' (barriered)' if c['barriered'] else ''} | {w['thread']} @ `{w['commit']}` | {seam_counts(cid)} | {', '.join(prs)} | {RCA[cid]['barrier'] if cid in RCA else '- (N below 3, not barriered)'} |")

T.append("\n## Owned files and borrow edges\n")
T.append("| lane | name | fixer models (per PR) | owns |")
T.append("|---|---|---|---|")
for ln, L in LANES.items():
    T.append(f"| {ln} | {L['name']} | {', '.join(i + ' ' + model_of(i) for i in LANE_ORDER[ln])} | {', '.join(x.replace(CC, '') for x in L['owns'])} |")

TABLES = "\n".join(T) + "\n"

# ---------------------------------------------------------------- lane briefs
STANDING_MD = open(os.path.join(os.path.dirname(__file__), "standing.md")).read()
for ln, L in LANES.items():
    lines = []
    ids_ = LANE_ORDER[ln]
    lines.append(f"# Round 9 fixer brief {ln}: {L['name']}\n")
    lines.append("Models, per role (FIX-PLAN.md section 12): the fixer per PR as listed below, the cheapest feasible (" + ", ".join(f"{i} {model_of(i)}" for i in ids_)
                 + "); reviews, judging and RCA on the strongest model (opus) in a different session, never this one; runner work (scoped-gate and stress re-runs, closure and budget re-records, rebuilds, report rendering, digests) on a haiku subagent that reports numbers and decides nothing; record upkeep (resume note, RESUME.md lines, delivery rows) may go to sonnet.\n")
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
        lines.append(f"- Fixer model: **{model_of(pid)}** ({why_of(pid)}). Reviewer opus; runner haiku; record sonnet" + ("; RCA opus" if (rca_beside(pid) or barriers_of(pid)) else "") + ".")
        lines.append(f"- Resume: branch `{branch_of(pid)}`, note `handoff/round9/fix/resume/{pid}.md` on it (review: `{branch_of(pid)}-review`, note `{pid}-review.md`); the roster's `resume` field for R9-{pid} gives the cloud and Mac pickup commands.")
        lines.append(f"- Effort: {'medium' if pid in EFFORT_LOW else 'high'}. Golden drift plausible: {'yes, claim what you measure' if pid in FIXTURE else 'not expected'}.")
        lines.append(f"- Needs tvofi: {'**yes** - ' + p['tvofi'] if p['tvofi'] else 'no'}.")
        if issue_refs(pid):
            lines.append(f"- Class issues (the body's wording): {issue_text(pid)}.")
        if pid in CAP_EXCEPTIONS:
            lines.append(f"- **Over fixer.md's five-item cap by recorded exception:** {CAP_EXCEPTIONS[pid]}.")
        if p["covers"]:
            lines.append(f"- Covers, as a class-level check (each finding closes in the PR that fixes it): {', '.join(p['covers'])}.")
        if BLOCKED.get(pid):
            lines.append(f"- Blocked on: {BLOCKED[pid]}.")
        rb = rca_beside(pid); br = barriers_of(pid)
        if rb: lines.append(f"- RCA seat(s) starting beside this PR (strongest model, separate thread): {', '.join(rb)}.")
        for c in br:
            r = RCA[c]
            lines.append(f"- **Class barrier landing in this PR: {c}** (RCA write-up `/mnt/project-files/audit-r9/rca/{r['slug']}/RCA.md`; process state {r['state']}).")
            lines.append(f"  - Form: {r['form']}.")
            lines.append(f"  - Prototype: `{r['proto']}`; cherry-pick {r['pick']}.")
            lines.append(f"  - Lines: {r['lines']}.")
            lines.append(f"  - Code-owned or policy: {r['owned']}.")
            if r.get("residual"):
                lines.append(f"  - Residual (the barrier's check does not read these; measured by the RCA): {', '.join(r['residual'])}.")
            lines.append("  - Demonstrate it failing on each round-9 instance re-introduced, passing on the fixed tree, silent on a healthy tree; set the class's entry in `tools/audit/bugclasses.json` (detector, barrier, status) here.")
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
            lines.append("- Findings: none; this PR is a class barrier." if (barriers_of(pid) or p["covers"]) else "- Findings: none; this PR builds what tvofi commissioned (fix notes).")
        if p["instances"]:
            lines.append("- Instances beyond the findings (a sweep probe, or the RCA's prototype or evidence, is your failing test):")
            for i in p["instances"]:
                extra = []
                if i["kind"] == "latent": extra.append("latent seam: fills a slot, not counted in N")
                if i.get("closed_by"): extra.append(f"closed by {i['closed_by']}; this PR adds its regression test")
                ft = f"Probe: `{i['probe']}` at `{SW[i['cls']]['commit']}`." if i["src"] != "RCA" else f"Failing test: {i['probe']}."
                lines.append(f"  - **{i['id']}** (found by {i['src']}{'; ' + '; '.join(extra) if extra else ''}), class {i['cls']}, `{i['file']}`: {i['seam']}. {i['what'][0].upper() + i['what'][1:]}. {ft}")
        if p.get("carry"):
            lines.append("- Carry-ins:")
            for c in p["carry"]:
                lines.append(f"  - {c}")
        lines.append("- Fix notes:")
        for n in p["notes"]:
            lines.append(f"  - {n}")
        cs = classes_of(p) or barriers_of(pid) or sorted({FIND[f]["cls"] for f in p["covers"]})
        lines.append("- Class sweeps (final; the seam lists are at the end of this brief): " + "; ".join(
            f"{c} N {SW[c]['N']} (judge {JUDGE_N[c]}, sweep {SW[c]['N_sweep']}), rca {'yes' if SW[c]['rca'] else 'no'}, {SW[c]['thread']} @ `{SW[c]['commit']}`, enumerator `{SW[c]['enum']}`" for c in cs) + ".")
        lines.append("")
    lane_classes = []
    for pid in ids_:
        for c in (classes_of(PR[pid]) or barriers_of(pid) or sorted({FIND[f]["cls"] for f in PR[pid]["covers"]})):
            if c not in lane_classes: lane_classes.append(c)
    lines.append("## Class sweeps for this lane's classes (Phase D, final)\n")
    lines.append("Each class's enumerator is your `fixer.md` step-8 rule. Run it from an export of the sweep commit at your merge base and your head; every seam it returns goes in `## Figures` against its disposition. The lists below are the sweep's own, at baseline `1936d5ca` (line numbers are baseline lines). A seam marked `instance` belongs to the finding or instance its note names, and that one's PR closes it, which may be in another lane.\n")
    for c in lane_classes:
        w = SW[c]
        lines.append(f"### {c}: N {w['N']} (judge {JUDGE_N[c]}, sweep {w['N_sweep']}), rca {'yes' if w['rca'] else 'no'}\n")
        if c in N_RCA:
            lines.append(f"- N changed at the RCA fold, {w['N_sweep']} to {w['N']}: {N_RCA[c][0]}.")
        lines.append(f"- Sweep {w['thread']}, commit `{w['commit']}` (branch `handoff/audit-r9-sweep-{w['thread'].lower()}`): `{w['dir']}/`, its `SWEEP.md`, and `{w['json']}`. Enumerator: `{w['enum']}`. Gate seconds the sweep measured: {w['gate'] if w['gate'] is not None else 'not measured'}.")
        if c in RCA:
            lines.append(f"- RCA seat beside {RCA[c]['beside']} (reported; `/mnt/project-files/audit-r9/rca/{RCA[c]['slug']}/RCA.md`); barrier lands in {RCA[c]['barrier']}, prototype `{RCA[c]['proto']}`.")
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
print(f"PRs {len(PRS)}; lanes {len(LANES)}; placed {len(placed)}/145 + refused {len(REFUSED)}; cap exceptions {len(CAP_EXCEPTIONS)}; tvofi PRs {sum(1 for p in PRS if p['tvofi'])}; max depth {max(depth.values())}")
print("wave counts", collections.Counter(depth.values()))
print("topo order", " ".join(order))
print("residual (barrier's check does not read these):")
for x in residual_report: print("  ", x)
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
    f"| {k} | {JUDGE_N[k]} | {SW[k]['N_sweep']} | {SW[k]['N']} | {r['state']} | {r['barrier']} | `{r['proto']}` | {r['owned']} | {r['lines']} |" for k, r in RCA.items())
rca_forms = "\n".join(
    f"- **{k}** -> {r['barrier']}: {r['form']}." + (f" Residual: {', '.join(r['residual'])}." if r.get('residual') else "") for k, r in RCA.items())
carry_rows = "\n".join(f"| {d} | {c} | {t} |" for d, c, t in CARRIES)
fill = dict(
    n_prs=len(PRS), n_inst=sum(1 for i in INSTANCES if i["kind"] == "instance"), n_latent=sum(1 for i in INSTANCES if i["kind"] == "latent"),
    n_rca=len(RCA), n_tvofi=sum(1 for p in PRS if p["tvofi"]), rca_forms=rca_forms, carry_rows=carry_rows, n_carries=len(CARRIES),
    tvofi_rows="\n".join(f"| {p['id']} | {p['tvofi']}{' **Blocked on:** ' + BLOCKED[p['id']] + '.' if p['id'] in BLOCKED else ''} |" for p in PRS if p["tvofi"]),
    n_borrow=sum(1 for p in PRS if p["borrows"]), rca_rows=rca_rows,
    tvofi_list=", ".join(p["id"] for p in PRS if p["tvofi"]),
    chain=" -> ".join(chain), chain_len=chain_len, max_depth=max(depth.values()),
    ledger_notes="\n".join("- " + x for x in LEDGER_NOTES),
    leads="\n".join(f"- **{t}** -> {pid}: {x}" for t, pid, x in LEADS),
    wave1=", ".join(p["id"] for p in PRS if depth[p["id"]] == 1),
    n_wave1=sum(1 for p in PRS if depth[p["id"]] == 1),
    wave1_rows="\n".join(f"| {p['id']} | {p['lane']} ({LANES[p['lane']]['name']}) | {model_of(p['id'])} | `{branch_of(p['id'])}` | `handoff/round9/fix/{p['lane']}.md` | {p['tvofi'] and 'yes' or '-'} |" for p in PRS if depth[p["id"]] == 1),
    wave1_absent=", ".join(f"{ln} (first PR {LANE_ORDER[ln][0]}, after {', '.join(PR[LANE_ORDER[ln][0]]['after'])})" for ln in LANES if all(depth[i] > 1 for i in LANE_ORDER[ln])),
    refused_rows="\n".join(f"| {fid} | {FIND[fid]['cls']} | {why} |" for fid, why in REFUSED.items()),
    cap_rows="\n".join(f"| {pid} | {why} |" for pid, why in CAP_EXCEPTIONS.items()),
    n_blocked=len(BLOCKED), blocked_rows="\n".join(f"| {k} | {v} |" for k, v in BLOCKED.items()),
    last_pr=mo[-1]["id"],
    role_rows="\n".join(f"| {r} | {m} |" for r, m in ROLE_MODELS),
    model_rows="\n".join(f"| {p['id']} | {model_of(p['id'])} | {why_of(p['id'])} |" for p in mo),
    n_sonnet=sum(1 for p in PRS if model_of(p['id']) == "sonnet"), n_opus=sum(1 for p in PRS if model_of(p['id']) == "opus"),
)
head = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "FIX-PLAN-head.md")).read()
for k, v in fill.items():
    head = head.replace("{" + k + "}", str(v))
left = re.findall(r"\{[a-z_0-9]+\}", head)
assert not left, left
with open(os.path.join(OUT, "handoff/round9/FIX-PLAN.md"), "w") as fh:
    fh.write(head + "\n" + TABLES)
W1 = [collections.OrderedDict([("pr", p["id"]), ("lane", p["lane"]), ("model", model_of(p["id"])), ("branch", branch_of(p["id"])),
      ("brief_path", f"handoff/round9/fix/{p['lane']}.md")]) for p in PRS if depth[p["id"]] == 1]
assert len({w["lane"] for w in W1}) == len(W1), "two wave-1 PRs in one lane"
with open(os.path.join(OUT, "handoff/round9/WAVE1.json"), "w") as fh:
    json.dump(W1, fh, indent=1); fh.write("\n")
print("wave1", " ".join(f"{w['pr']}:{w['model']}" for w in W1))
print("chain", chain_len, " ".join(chain))
print("merge order", " ".join(p["id"] for p in mo))
