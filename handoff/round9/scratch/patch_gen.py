import sys
P=sys.argv[1]; s=open(P).read()
def rep(old,new,n=1):
    global s
    c=s.count(old); assert c==n,(c,old[:100]); s=s.replace(old,new)
rep("SWEEP_LABEL, SWEEP_DIR, INSTANCES, LEADS, LEDGER_NOTES, N_RCA, CARRIES, ROUTING, ROLE_MODELS)",
    "SWEEP_LABEL, SWEEP_DIR, INSTANCES, LEADS, LEDGER_NOTES, N_RCA, CARRIES, ROUTING, ROLE_MODELS,\n                  REFUSED, CAP_EXCEPTIONS)")
rep("""for p in PRS:
    p.setdefault("instances", [])""", """for p in PRS:
    p.setdefault("instances", [])
    p.setdefault("covers", [])""")
rep("""    if len(whole) + len(p["instances"]) > 5:
        errors.append(f"{p['id']}: {len(whole)} whole findings + {len(p['instances'])} sweep instances, over fixer.md's cap")""",
"""    if len(whole) + len(p["instances"]) > 5 and p["id"] not in CAP_EXCEPTIONS:
        errors.append(f"{p['id']}: {len(whole)} whole findings + {len(p['instances'])} sweep instances, over fixer.md's cap")
    if p["id"] in CAP_EXCEPTIONS and len(whole) + len(p["instances"]) <= 5:
        errors.append(f"{p['id']}: listed in CAP_EXCEPTIONS but within the cap; drop the exception")""")
rep("""missing = sorted(set(FIND) - set(placed))""", """# a finding tvofi refused is placed by its refusal and must not also sit in a PR
for fid, why in REFUSED.items():
    if fid not in FIND:
        errors.append(f"refused {fid} is not a surviving finding")
    elif fid in placed:
        errors.append(f"refused {fid} is also placed in {placed[fid]}")
for pid in CAP_EXCEPTIONS:
    if pid not in {p["id"] for p in PRS}:
        errors.append(f"cap exception {pid} names no PR")
missing = sorted(set(FIND) - set(placed) - set(REFUSED))""")
# covers check after anc computed: insert before '# ---------------------------------------------------------------- derived'
rep("""# ---------------------------------------------------------------- derived""",
"""# a PR that covers findings (a class-level barrier tvofi commissioned beyond the RCA's) must come after
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

# ---------------------------------------------------------------- derived""")
rep("""FIXTURE = {"F1.3", "F2.1", "F2.3", "F2.4", "F10.1", "F1.7", "F1.10", "F2.5"}
BLOCKED = {"F7.3": "tvofi ruling on the A3(e) decision", "F11.2": "tvofi decisions on D11-s1-01 (ruleset setting) and D11-s1-04 (delegated identity)",
           "F11.3": "tvofi approval (policy)", "F11.5": "tvofi approval of each RCA policy draft (TVOFI-ASKS group a)"}""",
"""FIXTURE = {"F1.3", "F2.1", "F2.3", "F2.4", "F10.1", "F1.7", "F1.10", "F2.5"}
# every tvofi ask was answered at 19:16Z; what remains blocked is an action, not a decision
BLOCKED = {"F10.5": "the new ledger-writer App identity and its credential, a Mac/tvofi setup action under decision 0011 (card C5); the fixer's work does not wait on it, the writer's first real push does"}""")
# json brief: covers + cap exception
rep("""    parts.extend(p["notes"])
    for c in p.get("carry", []):""", """    if p["covers"]:
        parts.append("Covers, as a class-level check (closes none of them; each closes in the PR that fixes it): " + ", ".join(p["covers"]) + ".")
    if p["id"] in CAP_EXCEPTIONS:
        parts.append("Over fixer.md's five-item cap by recorded exception: " + CAP_EXCEPTIONS[p["id"]] + ".")
    parts.extend(p["notes"])
    for c in p.get("carry", []):""")
# roster fields
rep("""    g["findings"] = [fid for fid, _ in p["findings"]]""", """    g["findings"] = [fid for fid, _ in p["findings"]]
    g["covers"] = p["covers"]
    g["cap_exception"] = CAP_EXCEPTIONS.get(p["id"])""")
rep("""    cs = classes_of(p) or barriers_of(p["id"])
    g = collections.OrderedDict()""", """    cs = classes_of(p) or barriers_of(p["id"]) or sorted({FIND[f]["cls"] for f in p["covers"]})
    g = collections.OrderedDict()""")
rep("""roster["struck"] = []""", """roster["struck"] = []
roster["refused"] = collections.OrderedDict((fid, why) for fid, why in REFUSED.items())
roster["decisions"] = "tvofi answered all 35 asks at 19:16Z (cmsg_01EL5jLi4rokGBbkaevYXSJV6CQVMDN96YfVMTcN5QGSx2); handoff/round9/TVOFI-ASKS.md, DECISIONS, records each card's answer and where it is applied\"""")
# PR table findings column
rep("""    fl = ", ".join([fid + ("*" if part else "") for fid, part in p["findings"]] + ["+" + i["id"] for i in p["instances"]]) or "(class barrier)\"""",
    """    fl = ", ".join([fid + ("*" if part else "") for fid, part in p["findings"]] + ["+" + i["id"] for i in p["instances"]]) or ("(barrier; covers " + ", ".join(p["covers"]) + ")" if p["covers"] else "(class barrier)")""")
rep("""    T.append(f"| {p['id']} | {p['lane']} | {depth[p['id']]} | {fl} | {', '.join(classes_of(p)) or '-'} |""",
    """    T.append(f"| {p['id']}{' (cap exception)' if p['id'] in CAP_EXCEPTIONS else ''} | {p['lane']} | {depth[p['id']]} | {fl} | {', '.join(classes_of(p)) or ', '.join(sorted({FIND[f]['cls'] for f in p['covers']})) or '-'} |""")
rep("""T.append("\\n`*` = part of a finding;""", """T.append("\\n`*` = part of a finding; `(cap exception)` = over fixer.md's five-item cap by tvofi's recorded choice;""")
# finding table
rep("""    where = ", ".join(w[0] + (f" ({w[1]})" if w[1] else "") for w in placed[fid])""",
    """    where = ", ".join(w[0] + (f" ({w[1]})" if w[1] else "") for w in placed[fid]) if fid in placed else "**refused** (" + REFUSED[fid].split(" (")[1].split(")")[0] + ")\"""")
rep("""## Finding to PR (all 145 survivors)\\n")""", """## Finding to PR (all 145 survivors; refused ones name tvofi's card)\\n")""")
# class table
rep("""    for f in c["findings"]:
        for w in placed[f["id"]]:
            if w[0] not in prs: prs.append(w[0])""", """    for f in c["findings"]:
        if f["id"] in REFUSED:
            prs.append(f"{f['id']} refused"); continue
        for w in placed[f["id"]]:
            if w[0] not in prs: prs.append(w[0])""")
# lane brief lines
rep("""        lines.append(f"- Needs tvofi: {'**yes** - ' + p['tvofi'] if p['tvofi'] else 'no'}.")""",
    """        lines.append(f"- Needs tvofi: {'**yes** - ' + p['tvofi'] if p['tvofi'] else 'no'}.")
        if pid in CAP_EXCEPTIONS:
            lines.append(f"- **Over fixer.md's five-item cap by recorded exception:** {CAP_EXCEPTIONS[pid]}.")
        if p["covers"]:
            lines.append(f"- Covers, as a class-level check (each finding closes in the PR that fixes it): {', '.join(p['covers'])}.")""")
rep("""        elif not p["instances"]:
            lines.append("- Findings: none; this PR is a class barrier.")""", """        elif not p["instances"]:
            lines.append("- Findings: none; this PR is a class barrier." if (barriers_of(pid) or p["covers"]) else "- Findings: none; this PR builds what tvofi commissioned (fix notes).")""")
rep("""        cs = classes_of(p) or barriers_of(pid)
        lines.append("- Class sweeps""", """        cs = classes_of(p) or barriers_of(pid) or sorted({FIND[f]["cls"] for f in p["covers"]})
        lines.append("- Class sweeps""")
rep("""        for c in (classes_of(PR[pid]) or barriers_of(pid)):""", """        for c in (classes_of(PR[pid]) or barriers_of(pid) or sorted({FIND[f]["cls"] for f in PR[pid]["covers"]})):""")
# FIX-PLAN fill
rep("""    wave1=", ".join(p["id"] for p in PRS if depth[p["id"]] == 1),""", """    wave1=", ".join(p["id"] for p in PRS if depth[p["id"]] == 1),
    n_wave1=sum(1 for p in PRS if depth[p["id"]] == 1),
    wave1_rows="\\n".join(f"| {p['id']} | {p['lane']} ({LANES[p['lane']]['name']}) | {model_of(p['id'])} | `{branch_of(p['id'])}` | `handoff/round9/fix/{p['lane']}.md` | {p['tvofi'] and 'yes' or '-'} |" for p in PRS if depth[p["id"]] == 1),
    wave1_absent=", ".join(f"{ln} (first PR {LANE_ORDER[ln][0]}, after {', '.join(PR[LANE_ORDER[ln][0]]['after'])})" for ln in LANES if all(depth[i] > 1 for i in LANE_ORDER[ln])),
    refused_rows="\\n".join(f"| {fid} | {FIND[fid]['cls']} | {why} |" for fid, why in REFUSED.items()),
    cap_rows="\\n".join(f"| {pid} | {why} |" for pid, why in CAP_EXCEPTIONS.items()),
    n_blocked=len(BLOCKED), blocked_rows="\\n".join(f"| {k} | {v} |" for k, v in BLOCKED.items()),""")
# wave-1 json
rep("""print("chain", chain_len, " ".join(chain))""", """W1 = [collections.OrderedDict([("pr", p["id"]), ("lane", p["lane"]), ("model", model_of(p["id"])), ("branch", branch_of(p["id"])),
      ("brief_path", f"handoff/round9/fix/{p['lane']}.md")]) for p in PRS if depth[p["id"]] == 1]
assert len({w["lane"] for w in W1}) == len(W1), "two wave-1 PRs in one lane"
with open(os.path.join(OUT, "handoff/round9/WAVE1.json"), "w") as fh:
    json.dump(W1, fh, indent=1); fh.write("\\n")
print("wave1", " ".join(f"{w['pr']}:{w['model']}" for w in W1))
print("chain", chain_len, " ".join(chain))""")
open(P,'w').write(s); print("gen.py patched")
