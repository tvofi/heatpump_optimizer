import sys,re,subprocess,pathlib
F=pathlib.Path("tools/audit/carry_audit.py"); orig=F.read_text()
M={
 "normpr-landed": ('srcs = [("#" + x if x.isdigit() else x) for x in','srcs = [(x if x.isdigit() else x) for x in'),
 "shaped": ('carry_segments(t, shaped=True)','carry_segments(t)'),
 "findings_true": ('any(findings_section or m.group','any(True or m.group'),
 "findings_false": ('any(findings_section or m.group','any(False or m.group'),
 "kindsec_noFindings": ('kind_sec = block_sec or FINDINGS_HEADING.match(sec) or NOTE_HEADING.search(sec)','kind_sec = block_sec or NOTE_HEADING.search(sec)'),
 "kindsec_noNote": ('kind_sec = block_sec or FINDINGS_HEADING.match(sec) or NOTE_HEADING.search(sec)','kind_sec = block_sec or FINDINGS_HEADING.match(sec)'),
 "kindsec_noBlock": ('kind_sec = block_sec or FINDINGS_HEADING.match(sec)','kind_sec = FINDINGS_HEADING.match(sec)'),
 "para_cont": ('if not (nxt.startswith((" ", "\\t")) and CARRY.search(nxt) and not BULLET.match(nxt)):','if True:'),
 "para_noindent": ('if not (nxt.startswith((" ", "\\t")) and CARRY.search(nxt) and not BULLET.match(nxt)):','if not (CARRY.search(nxt) and not BULLET.match(nxt)):'),
 "para_nobullet": ('and CARRY.search(nxt) and not BULLET.match(nxt)):','and CARRY.search(nxt)):'),
 "para_nocarry": ('nxt.startswith((" ", "\\t")) and CARRY.search(nxt) and','nxt.startswith((" ", "\\t")) and'),
 "quoted_spans": ('+ [m.span() for m in QUOTED_PHRASE.finditer(text)]',''),
 "quoted_lookbehind": ("(?<![\\w\"])\"[^\"\\n]*\"(?!\\w)","\"[^\"\\n]*\""),
 "marker_dismissed": ('if re.match(r"dismissed\\s*:", rest, re.I):\n        return True','if False:\n        return True'),
 "marker_group": ('return bool(GROUP_TOK.match(tok) or ISSUE_TOK','return bool(ISSUE_TOK'),
 "marker_issue": ('GROUP_TOK.match(tok) or ISSUE_TOK.match(tok) or','GROUP_TOK.match(tok) or'),
 "marker_brief": (' or BRIEF_TOK.match(tok))',')'),
 "marker_true": ('    rest = seg.split(":", 1)[1].strip().strip("`*_")','    return True\n    rest = seg.split(":", 1)[1].strip().strip("`*_")'),
 "normpr_landops": ('    pr = norm_pr(pr)\n    src = f"From','    src = f"From'),
 "normpr_cli": ('                a.pr = norm_pr(a.pr)\n','                pass\n'),
 "normpr_noraise": ('    if pr and not re.fullmatch(r"#\\d+", pr):\n        raise','    if False:\n        raise'),
 "normpr_nohash": ('        return "#" + pr\n','        return pr\n'),
}
res=[]
for k,(a,b) in M.items():
    n=orig.count(a)
    if n!=1: res.append(f"{k}: NOT-APPLIED (count {n})"); continue
    F.write_text(orig.replace(a,b))
    p=subprocess.run([sys.executable,str(F),"--self-test"],capture_output=True,text=True,timeout=600)
    fails=[l for l in p.stdout.splitlines() if "FAIL" in l]
    last=(p.stdout.strip().splitlines() or [""])[-1]
    res.append(f"{k}: rc={p.returncode} {'KILLED' if p.returncode else 'SURVIVED'} | {last} | "+" || ".join(fails[:4]))
F.write_text(orig)
print("\n".join(res))
