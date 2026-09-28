import sys
def patch(P, pairs):
    s=open(P).read()
    for old,new in pairs:
        c=s.count(old); assert c==1,(P,c,old[:90]); s=s.replace(old,new)
    open(P,'w').write(s)
G='fixplan/gen.py'
patch(G, [
("""JUDGE_N = {(c["id"] or CLASS_SHORT[c["name"]]): c["n"] for c in CLASSES["classes"]}""",
"""JUDGE_N = {(c["id"] or CLASS_SHORT[c["name"]]): c["n"] for c in CLASSES["classes"]}

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
assert set(ISSUE_OF) | set(ISSUE_DROPPED) == set(JUDGE_N), sorted(set(JUDGE_N) - set(ISSUE_OF) - set(ISSUE_DROPPED))"""),
("""# ---------------------------------------------------------------- derived
def classes_of(p):""",
"""# every class issue closes in one PR, the one after every other PR holding the class (Fixes #N there,
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
def classes_of(p):"""),
("""    if p["tvofi"]:
        parts.append("Needs tvofi: " + p["tvofi"] + ".")
    parts.append(STANDING_SHORT""",
"""    if p["tvofi"]:
        parts.append("Needs tvofi: " + p["tvofi"] + ".")
    if issue_refs(p["id"]):
        parts.append("Class issues, in the body exactly as written here: " + issue_text(p["id"]) + ". Fixes #N only where this entry says so, because this PR follows every other PR holding that class; everything else is Part of #N.")
    parts.append(STANDING_SHORT"""),
("""    g["issues"] = []""", """    g["issues"] = sorted(n for n, _, _ in issue_refs(p["id"]))
    g["fixes"] = sorted(n for n, _, closes in issue_refs(p["id"]) if closes)"""),
("""    "`issues` is empty until Phase E files the class issues. `sweep_instances`""",
 """    "`issues` lists the Phase E class issues (#1644-#1688; #1689 closed as not planned with D8-s2-01) each PR's findings, instances, barrier or covers belong to, and `fixes` the ones it closes, because it follows every other PR holding that class; the body says Fixes #N for those and Part of #N for the rest. `sweep_instances`"""),
("""issues[] is filled when Phase E files the class issues.\"""", """issues[] and fixes[] are from the Phase E issue map (2026-09-26).\""""),
("""        lines.append(f"- Needs tvofi: {'**yes** - ' + p['tvofi'] if p['tvofi'] else 'no'}.")""",
 """        lines.append(f"- Needs tvofi: {'**yes** - ' + p['tvofi'] if p['tvofi'] else 'no'}.")
        if issue_refs(pid):
            lines.append(f"- Class issues (the body's wording): {issue_text(pid)}.")"""),
("""    "Touch the claim files only to claim measured drift.""", """    "Class issues: write Fixes #N only for an issue this entry marks Fixes, Part of #N for every other listed issue. "
    "Touch the claim files only to claim measured drift."""),
])
# class table issue column
patch(G, [
("""T.append("| class | N judge | N sweep | N final | rca | sweep | seams | PRs | barrier PR |")
T.append("|---|---|---|---|---|---|---|---|---|")""",
"""T.append("| class | issue | fixed in | N judge | N sweep | N final | rca | sweep | seams | PRs | barrier PR |")
T.append("|---|---|---|---|---|---|---|---|---|---|---|")"""),
("""    T.append(f"| {cid} | {c['n']} |""", """    iss = f"#{ISSUE_OF[cid]}" if cid in ISSUE_OF else f"#{ISSUE_DROPPED[cid][0]} (closed, not planned)"
    T.append(f"| {cid} | {iss} | {CLOSER.get(cid, '-')} | {c['n']} |"""),
])
patch('fixplan/standing.md', [
("""It closes the class issue(s) Phase E filed for its findings (`Closes #N` only for issues this PR fully closes; a split finding's first PR says "leaves #N open") and says `Part of #201`.""",
 """It names the class issues Phase E filed (#1644-#1688) exactly as its PR entry above lists them: `Fixes #N` only where the entry says Fixes (this PR follows every other PR holding that class, so its merge closes the issue), `Part of #N` for every other listed issue, and `Part of #201`. A split finding's first PR also says which finding it leaves open."""),
])
patch('fixplan/FIX-PLAN-head.md', [
("""when its last PR merges, and the first PR's body says "leaves #N open":""", """when its last PR merges, and the first PR's body says which finding it leaves open (its class issue is `Part of #N` there):"""),
])
print("ok")
