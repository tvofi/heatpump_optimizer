import subprocess,pathlib
p=pathlib.Path('tools/policy/agreement.mjs'); orig=p.read_text()
M={
'X1 backward quote skip':("  for (let i = ls; i < at; i++) {\n    const c = text[i]\n    if (quoted(st, c)) continue\n","  for (let i = ls; i < at; i++) {\n    const c = text[i]\n"),
'X2 forward quote skip':("    if (quoted(st, c)) continue\n    if ('([{'.includes(c)) depth++","    if ('([{'.includes(c)) depth++"),
'X3 push deleted':("open.push(i)","void 0"),
'X4 depth++ deleted':("if ('([{'.includes(c)) depth++","if ('([{'.includes(c)) {}"),
'X5 forward from open bracket':("start + (open.length ? 1 : 0)","start"),
'X6 first match only':("text.matchAll(new RegExp(MERGE_CALL.source, 'g'))","[text.match(MERGE_CALL)].filter(Boolean)"),
'Y1 close quote not cleared':("else if (c === st.q) st.q = ''; return true","return true"),
'Y2 line number off by one':("text.slice(0, m.index).split('\\n').length}","text.slice(0, m.index).split('\\n').length - 1}"),
'Y3 no line-end check for backslash nor open (always continue)':("      if (!open.length && !depth && text[i - 1] !== '\\\\') return text.slice(start, i)\n",""),
'Y4 open.length ignored at line end':("if (!open.length && !depth &&","if (!depth &&"),
'Y5 close ends extent at 0 not -1':("--depth < 0)","--depth < 1)"),
'Y6 calls.push deleted':("      calls.push(f)\n      if (SUBJECT_ARG","      if (SUBJECT_ARG"),
'Y7 ls off':("text.lastIndexOf('\\n', at - 1) + 1","0"),
'Y8 MERGE_CALL gh\\s+pr':(r"\bgh\s+pr\s+merge\b",r"\bgh pr merge\b"),
'Y9 slice end exclusive at close':("return text.slice(start, i + 1)","return text.slice(start, i)"),
'Y10 blank-line return removed only text tail':("next < 0 ? text.length : next","next"),
'Y11 title space one -> any':(r"/^\S(?:.*\S)? \(#",r"/^\S(?:.*\S)?\s+\(#"),
'Y12 title leading \\S -> .':(r"/^\S(?:.*\S)? \(#",r"/^.(?:.*\S)? \(#"),
}
for k,(a,b) in M.items():
    if orig.count(a)!=1: print(k,'NOT APPLIED',orig.count(a)); continue
    p.write_text(orig.replace(a,b))
    r=subprocess.run(['node','tools/policy/agreement.mjs','--self-test'],capture_output=True,text=True)
    out=r.stdout+r.stderr
    fails=[l.strip() for l in out.splitlines() if l.strip().startswith('FAIL')]
    last=[l for l in out.splitlines() if 'SELF-TEST' in l]
    print(k,'|',last[-1] if last else 'no summary rc=%d'%r.returncode,'|','; '.join(fails)[:300])
p.write_text(orig)
