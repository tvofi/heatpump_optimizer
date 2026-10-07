import subprocess,sys,pathlib
p=pathlib.Path("tests/layout.py"); orig=p.read_text()
M={
 "M6 marker unkeyed": ('or re.search(r"layout:old=" + o + r"(?![\\w./-])", line))', 'or "layout:old" in line)'),
 "M7 locate unkeyed": ('or re.search(r"\\b(?:locate|canon)\\(\\s*[\'\\"`]" + o + r"/?[\'\\"`]", line)', 'or re.search(r"\\b(?:locate|canon)\\(", line)'),
 "M8 marker lookahead dropped": ('r"(?![\\w./-])"', 'r""'),
 "M9 new-path arm dropped": ('(new and new.rstrip("/") in line)', '(False)'),
 "M10 generated rule copies not exempt": ('"dev/audit/rca/", ".claude/rules/", ".cursor/rules/")', '"dev/audit/rca/")'),
}
for k,(a,b) in M.items():
    if orig.count(a)!=1: print("RESULT",k,"PATTERN-MISS",orig.count(a)); continue
    p.write_text(orig.replace(a,b))
    r=subprocess.run([sys.executable,"tests/layout.py","--self-test"],capture_output=True,text=True)
    reds=[l.strip() for l in (r.stdout+r.stderr).splitlines() if "FAIL" in l]
    print(f"RESULT {k}: rc={r.returncode} red={len(reds)}"); [print("   ",x[:160]) for x in reds[:4]]
p.write_text(orig)
