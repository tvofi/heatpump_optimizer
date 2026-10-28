import sys,subprocess,pathlib
p=pathlib.Path('tools/policy/agreement.mjs'); orig=p.read_text()
M={
'M1 title arm end-anchor':(r"/^\S(?:.*\S)? \(#[1-9]\d*\)$/",r"/\(#\d+\)$/"),
'M2 number \\d+':(r"\(#[1-9]\d*\)$/]",r"\(#\d+\)$/]"),
'M3 extent ends every line':("      if (!open.length && !depth && text[i - 1] !== '\\\\') return text.slice(start, i)\n","      return text.slice(start, i)\n"),
'M4 backslash ignored':("&& text[i - 1] !== '\\\\')", ")"),
'M5 depth ignored at line end':("if (!open.length && !depth && text","if (!open.length && text"),
'M6 blank-line end deleted':("      if (!text.slice(i + 1, next < 0 ? text.length : next).trim()) return text.slice(start, i)\n",""),
'M7 enclosing close not end':("&& --depth < 0) return text.slice(start, i + 1)","&& --depth < -99) return text.slice(start, i + 1)"),
'M8 start always line start':("const start = open.length ? open[open.length - 1] : ls","const start = ls"),
'M9 MERGE_CALL literal spaces':(r'"pr",\s*"merge"','"pr", "merge"'),
'M10 quotes not read':("if (c === '\"' || c === \"'\") { st.q = c; return true }",""),
'M11 escapes not read':("if (st.esc) st.esc = false; else if (c === '\\\\') st.esc = true; else ",""),
'M12 blank-line state reset removed':("      st = { q: '', esc: false }\n      const next","      const next"),
'M13 pop on close before at removed':("    else if (')]}'.includes(c)) open.pop()\n",""),
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
