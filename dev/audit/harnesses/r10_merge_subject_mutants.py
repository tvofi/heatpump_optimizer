#!/usr/bin/env python3
"""R10-MERGE-SUBJECT-HARDEN (#2697): the mutation table for the merge-subject guard.

    python3 dev/audit/harnesses/r10_merge_subject_mutants.py   (from the repository root)

Applies each string-replacement mutant to tools/policy/agreement.mjs, runs
`node tools/policy/agreement.mjs --self-test`, prints the summary and every FAIL,
and restores the file (commit first: the restore writes the text read at start).
M1-M13 are review/2697 round 1's evidence/mut.py; X1-X6 and Y1-Y12 are round 2's
evidence/mut2.py, Y8 retargeted to the repaired shell arm and Y8a/Y8b added.
A survivor prints `N of N` and no FAIL. Expected survivors: X5, Y9, Y10, each
dispositioned in the PR body. A `NOT APPLIED` line means the mutated text moved.
"""
import pathlib
import subprocess

p = pathlib.Path('tools/policy/agreement.mjs')
orig = p.read_text()
M = {
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
'Y8 MERGE_CALL shell arm to literal spaces':(r"\bgh(?:\s|\\\r?\n)+pr(?:\s|\\\r?\n)+merge\b",r"\bgh pr merge\b"),
'Y8a continuation dropped (back to \\s+)':(r"\bgh(?:\s|\\\r?\n)+pr(?:\s|\\\r?\n)+merge\b",r"\bgh\s+pr\s+merge\b"),
'Y8b \\s to a literal space':(r"\bgh(?:\s|\\\r?\n)+pr(?:\s|\\\r?\n)+merge\b",r"\bgh(?: |\\\r?\n)+pr(?: |\\\r?\n)+merge\b"),
'Y9 slice end exclusive at close':("return text.slice(start, i + 1)","return text.slice(start, i)"),
'Y10 blank-line return removed only text tail':("next < 0 ? text.length : next","next"),
'Y11 title space one -> any':(r"/^\S(?:.*\S)? \(#",r"/^\S(?:.*\S)?\s+\(#"),
'Y12 title leading \\S -> .':(r"/^\S(?:.*\S)? \(#",r"/^.(?:.*\S)? \(#"),
}
try:
    for k, (a, b) in M.items():
        if orig.count(a) != 1:
            print(k, 'NOT APPLIED', orig.count(a))
            continue
        p.write_text(orig.replace(a, b))
        r = subprocess.run(['node', 'tools/policy/agreement.mjs', '--self-test'], capture_output=True, text=True)
        out = r.stdout + r.stderr
        fails = [l.strip() for l in out.splitlines() if l.strip().startswith('FAIL')]
        last = [l for l in out.splitlines() if 'SELF-TEST' in l]
        print(k, '|', last[-1] if last else 'no summary rc=%d' % r.returncode, '|', '; '.join(fails))
finally:
    p.write_text(orig)
