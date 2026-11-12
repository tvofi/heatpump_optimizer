import sys,re,subprocess,pathlib
# Head-end adaptation of the prior reviewer's ev/mutant_driver.py (verdict 8ce5db59): same mutants,
# anchors re-spelled where 007d340483/45ae9ae729 rewrote the line, plus mutants on the delta's added lines.
F=pathlib.Path("tools/audit/carry_audit.py"); orig=F.read_text()
PC='if not (nxt.startswith((" ", "\\t")) and CARRY.search(nxt)):'
M={
 "kindsec_noNote": ('kind_sec = block_sec or FINDINGS_HEADING.match(sec) or NOTE_HEADING.search(sec)','kind_sec = block_sec or FINDINGS_HEADING.match(sec)'),
 "kindsec_noFindings": ('kind_sec = block_sec or FINDINGS_HEADING.match(sec) or NOTE_HEADING.search(sec)','kind_sec = block_sec or NOTE_HEADING.search(sec)'),
 "kindsec_noBlock": ('kind_sec = block_sec or FINDINGS_HEADING.match(sec)','kind_sec = FINDINGS_HEADING.match(sec)'),
 "para_cont": (PC,'if True:'),
 "para_noindent": (PC,'if not (CARRY.search(nxt)):'),
 "para_nocarry": (PC,'if not (nxt.startswith((" ", "\\t"))):'),
 "para_bullet_readded(equivalence probe)": (PC,'if not (nxt.startswith((" ", "\\t")) and CARRY.search(nxt) and not BULLET.match(nxt)):'),
 "quoted_spans": ('+ [m.span() for m in QUOTED_PHRASE.finditer(blanked)]',''),
 "quoted_lookbehind": ('(?<![\\w"])"[^"\\n]*"(?!\\w)', '"[^"\\n]*"(?!\\w)'),
 "quoted_lookahead": ('(?<![\\w"])"[^"\\n]*"(?!\\w)', '(?<![\\w"])"[^"\\n]*"'),
 "blank_off": ('QUOTED_PHRASE.finditer(blanked)','QUOTED_PHRASE.finditer(text)'),
 "blank_shrink": ('re.sub(r"[^\\n]", " ", m.group(0))','""'),
 "mdlink_shaped": ('without routing (P589)."""\n    rest = MD_LINK.sub(r"\\1", seg.split(":", 1)[1])','without routing (P589)."""\n    rest = (seg.split(":", 1)[1])'),
 "mdlink_dests": ('marker segment (`Carry: ...`)."""\n    rest = MD_LINK.sub(r"\\1", seg.split(":", 1)[1])','marker segment (`Carry: ...`)."""\n    rest = (seg.split(":", 1)[1])'),
 "mdlink_url_any": ('\\]\\([^)\\s]*\\)")','\\]\\([^)]*\\)")'),
 "marker_dismissed": ('if re.match(r"dismissed\\s*:", rest, re.I):\n        return True','if False:\n        return True'),
 "marker_group": ('return bool(GROUP_TOK.match(tok) or ISSUE_TOK','return bool(ISSUE_TOK'),
 "marker_issue": ('return bool(GROUP_TOK.match(tok) or ISSUE_TOK.match(tok) or','return bool(GROUP_TOK.match(tok) or'),
 "marker_brief": (' or BRIEF_TOK.match(tok))',')'),
 "marker_true": ('without routing (P589)."""\n','without routing (P589)."""\n    return True\n'),
 "shaped": ('carry_segments(t, shaped=True)','carry_segments(t)'),
 "findings_true": ('any(findings_section or m.group','any(True or m.group'),
 "findings_false": ('any(findings_section or m.group','any(False or m.group'),
 "normpr-landed": ('srcs = [("#" + x if x.isdigit() else x) for x in','srcs = [(x if x.isdigit() else x) for x in'),
 "normpr_landops": ('    pr = norm_pr(pr)\n    src = f"From','    src = f"From'),
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
