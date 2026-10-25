#!/usr/bin/env python3
"""R10-MERGE-SUBJECT-HARDEN (#2697): the mutation table for the merge-subject guard.

    python3 dev/audit/harnesses/r10_merge_subject_mutants.py   (from the repository root)

Applies each string-replacement mutant to tools/policy/agreement.mjs, runs
`node tools/policy/agreement.mjs --self-test`, prints the summary and every FAIL,
and restores the file (commit first: the restore writes the text read at start).
M, X and Y rows mutate the call extent and the quote reader, T rows the
triple quote, B the code-file test, R rows each named part and sub-part of
MERGE_CALL and SUBJECT_ARG, L rows the lead (the program position, read only
to anchor the line) and L5 the program read again, RV rows each site a
shared part (GAP, OPTIONS) stands in, one site at a time, P rows the statement
read the open bracket comes from (P1 restores the line-local scan), C rows the
comment reader, G rows GAP's comment and literal-join arms. A survivor prints
`N of N` and no FAIL. Expected survivors: Y9, Y10, each dispositioned in the
PR body. A `NOT APPLIED` line means the mutated text moved.
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
'M6 blank-line end deleted':("      if (kind === 'sh' && !text.slice(i + 1, next < 0 ? text.length : next).trim()) return text.slice(start, i)\n",''),
'M7 enclosing close not end':("&& --depth < 0) return text.slice(start, i + 1)","&& --depth < -99) return text.slice(start, i + 1)"),
'M8 start always line start':("const start = open.length ? open[open.length - 1] : ls","const start = ls"),
'M10 quotes not read':('  if (c === \'"\' || c === "\'") { st.q = text.startsWith(c.repeat(3), i) ? c.repeat(3) : c; return st.q.length }\n',''),
'M11 escapes not read':("    else if (c === '\\\\') st.esc = true\n",''),
'M12 blank-line state reset removed':("      st = { q: '', esc: false }\n      const next","      const next"),
'M13 pop on close before at removed':("    else if (')]}'.includes(c)) open.pop()\n",""),
'X1 backward quote skip':("    if (n) { i += n - 1; continue }\n    if (commentAt(kind, text, i)) { const e = text.indexOf('\\n', i); if (e < 0) break; i = e - 1; continue }\n    if ('([{'.includes(c)) open.push(i)","    if (commentAt(kind, text, i)) { const e = text.indexOf('\\n', i); if (e < 0) break; i = e - 1; continue }\n    if ('([{'.includes(c)) open.push(i)"),
'X2 forward quote skip':("    if (n) { i += n - 1; continue }\n    if (commentAt(kind, text, i)) { const e = text.indexOf('\\n', i); if (e < 0) break; i = e - 1; continue }\n    if ('([{'.includes(c)) depth++","    if (commentAt(kind, text, i)) { const e = text.indexOf('\\n', i); if (e < 0) break; i = e - 1; continue }\n    if ('([{'.includes(c)) depth++"),
'X3 push deleted':("open.push(i)","void 0"),
'X4 depth++ deleted':("if ('([{'.includes(c)) depth++","if ('([{'.includes(c)) {}"),
'X5 forward from open bracket':("start + (open.length ? 1 : 0)","start"),
'X6 first match only':("text.matchAll(new RegExp(MERGE_CALL.source, 'g'))","[text.match(MERGE_CALL)].filter(Boolean)"),
'Y1 close quote not cleared':("    else if (text.startsWith(st.q, i)) { const k = st.q.length; st.q = ''; return k }",'    else if (text.startsWith(st.q, i)) { const k = st.q.length; return k }'),
'Y2 line number off by one':("text.slice(0, m.index).split('\\n').length}","text.slice(0, m.index).split('\\n').length - 1}"),
'Y3 no line-end check for backslash nor open (always continue)':("      if (!open.length && !depth && text[i - 1] !== '\\\\') return text.slice(start, i)\n",""),
'Y4 open.length ignored at line end':("if (!open.length && !depth &&","if (!depth &&"),
'Y5 close ends extent at 0 not -1':("--depth < 0)","--depth < 1)"),
'Y7 ls off':("text.lastIndexOf('\\n', at - 1) + 1","0"),
'Y9 slice end exclusive at close':("return text.slice(start, i + 1)","return text.slice(start, i)"),
'Y10 blank-line return removed only text tail':("next < 0 ? text.length : next","next"),
'Y11 title space one -> any':(r"/^\S(?:.*\S)? \(#",r"/^\S(?:.*\S)?\s+\(#"),
'Y12 title leading \\S -> .':(r"/^\S(?:.*\S)? \(#",r"/^.(?:.*\S)? \(#"),
'R1 QUOTE: double quote only': ('const QUOTE = \'["\\\'`]\'', 'const QUOTE = \'["]\''),
'R2 GAP: the \\-newline continuation dropped':('const GAP = String.raw`(?:\\s|\\\\\\n|,|(?:#|\\/\\/)[^\\n]*\\n|\\/\\*[\\s\\S]*?\\*\\/|["\'${\'`\'}][^\\S\\n]*["\'${\'`\'}])+`','const GAP = String.raw`(?:\\s|,|(?:#|\\/\\/)[^\\n]*\\n|\\/\\*[\\s\\S]*?\\*\\/|["\'${\'`\'}][^\\S\\n]*["\'${\'`\'}])+`'),
'R3 GAP: the argv comma dropped':('const GAP = String.raw`(?:\\s|\\\\\\n|,|(?:#|\\/\\/)[^\\n]*\\n|\\/\\*[\\s\\S]*?\\*\\/|["\'${\'`\'}][^\\S\\n]*["\'${\'`\'}])+`','const GAP = String.raw`(?:\\s|\\\\\\n|(?:#|\\/\\/)[^\\n]*\\n|\\/\\*[\\s\\S]*?\\*\\/|["\'${\'`\'}][^\\S\\n]*["\'${\'`\'}])+`'),
'R18 merge_pull_request dropped': ('  String.raw`|merge_pull_request|mergePullRequest|\\/pulls\\/\\S+\\/merge\\b`)', '  String.raw`|mergePullRequest|\\/pulls\\/\\S+\\/merge\\b`)'),
'R19 mergePullRequest dropped': ('  String.raw`|merge_pull_request|mergePullRequest|\\/pulls\\/\\S+\\/merge\\b`)', '  String.raw`|merge_pull_request|\\/pulls\\/\\S+\\/merge\\b`)'),
'R20 the REST merge path dropped': ('  String.raw`|merge_pull_request|mergePullRequest|\\/pulls\\/\\S+\\/merge\\b`)', '  String.raw`|merge_pull_request|mergePullRequest`)'),
'R21 SUBJECT_ARG: short flags alone, no cluster': ('const SUBJECT_ARG = new RegExp(String.raw`(?:^|[\\s"\'[,])(?:--(?:subject|title|body|body-file)(?=[\\s="\',\\]]|$)|-[mrsd]*[tbF])` +', 'const SUBJECT_ARG = new RegExp(String.raw`(?:^|[\\s"\'[,])(?:--(?:subject|title|body|body-file)(?=[\\s="\',\\]]|$)|-[tbF](?=[\\s="\',\\]]|$))` +'),
'R22 SUBJECT_ARG: -d not a cluster flag': ('const SUBJECT_ARG = new RegExp(String.raw`(?:^|[\\s"\'[,])(?:--(?:subject|title|body|body-file)(?=[\\s="\',\\]]|$)|-[mrsd]*[tbF])` +', 'const SUBJECT_ARG = new RegExp(String.raw`(?:^|[\\s"\'[,])(?:--(?:subject|title|body|body-file)(?=[\\s="\',\\]]|$)|-[mrs]*[tbF])` +'),
'R23 SUBJECT_ARG: -F dropped from the short flags': ('const SUBJECT_ARG = new RegExp(String.raw`(?:^|[\\s"\'[,])(?:--(?:subject|title|body|body-file)(?=[\\s="\',\\]]|$)|-[mrsd]*[tbF])` +', 'const SUBJECT_ARG = new RegExp(String.raw`(?:^|[\\s"\'[,])(?:--(?:subject|title|body|body-file)(?=[\\s="\',\\]]|$)|-[mrsd]*[tb])` +'),
'R24 SUBJECT_ARG: commitHeadline/commitBody dropped': ('  String.raw`|\\bcommit_(?:title|message)\\b|\\bcommit(?:Headline|Body)\\b`)', '  String.raw`|\\bcommit_(?:title|message)\\b`)'),
'R25 GAP: whitespace narrowed to one literal space':('const GAP = String.raw`(?:\\s|\\\\\\n|,|(?:#|\\/\\/)[^\\n]*\\n|\\/\\*[\\s\\S]*?\\*\\/|["\'${\'`\'}][^\\S\\n]*["\'${\'`\'}])+`','const GAP = String.raw`(?: |\\\\\\n|,|(?:#|\\/\\/)[^\\n]*\\n|\\/\\*[\\s\\S]*?\\*\\/|["\'${\'`\'}][^\\S\\n]*["\'${\'`\'}])+`'),
'R26 GAP: one separator only, no run':('const GAP = String.raw`(?:\\s|\\\\\\n|,|(?:#|\\/\\/)[^\\n]*\\n|\\/\\*[\\s\\S]*?\\*\\/|["\'${\'`\'}][^\\S\\n]*["\'${\'`\'}])+`','const GAP = String.raw`(?:\\s|\\\\\\n|,|(?:#|\\/\\/)[^\\n]*\\n|\\/\\*[\\s\\S]*?\\*\\/|["\'${\'`\'}][^\\S\\n]*["\'${\'`\'}])`'),
'T1 triple quote not one mark':('  if (c === \'"\' || c === "\'") { st.q = text.startsWith(c.repeat(3), i) ? c.repeat(3) : c; return st.q.length }','  if (c === \'"\' || c === "\'") { st.q = false ? c.repeat(3) : c; return st.q.length }'),
'T2 a line end inside a triple quote ends the call':('      if (st.q.length === 3) continue\n',''),
'B1 a blank line ends a bracketed call in every file':("    const text = read(f); const kind = /\\.py$/.test(f) ? 'py' : /\\.(mjs|js|cjs)$/.test(f) ? 'js' : 'sh'","    const text = read(f); const kind = 'sh'"),
'Y6 calls.push deleted':('      calls.push(f)\n', ''),
'R4 word: the end-of-word lookahead dropped':('const word = (w) => `${QUOTE}?(?<![\\\\w$./-])${w}${QUOTE}?(?![\\\\w-])`', 'const word = (w) => `${QUOTE}?(?<![\\\\w$./-])${w}${QUOTE}?`'),
'R4a word: the start-of-word lookbehind dropped':('const word = (w) => `${QUOTE}?(?<![\\\\w$./-])${w}${QUOTE}?(?![\\\\w-])`', 'const word = (w) => `${QUOTE}?${w}${QUOTE}?(?![\\\\w-])`'),
'R5 word: the opening quote dropped':('const word = (w) => `${QUOTE}?(?<![\\\\w$./-])${w}${QUOTE}?(?![\\\\w-])`', 'const word = (w) => `(?<![\\\\w$./-])${w}${QUOTE}?(?![\\\\w-])`'),
'R6 word: the closing quote dropped':('const word = (w) => `${QUOTE}?(?<![\\\\w$./-])${w}${QUOTE}?(?![\\\\w-])`', 'const word = (w) => `${QUOTE}?(?<![\\\\w$./-])${w}(?![\\\\w-])`'),
'R7 OPTIONS: no option between words':('const OPTIONS = `(?:${GAP}${option(GAP)})*`', "const OPTIONS = ''"),
'R8 OPTION: the separate value dropped':('const option = (gap) => String.raw`${QUOTE}?--?[A-Za-z][\\w-]*(?:=${VALUE}?)?${QUOTE}?(?:${gap}${VALUE})?`', 'const option = (gap) => String.raw`${QUOTE}?--?[A-Za-z][\\w-]*(?:=${VALUE}?)?${QUOTE}?`'),
'R9 OPTION: the =value dropped':('const option = (gap) => String.raw`${QUOTE}?--?[A-Za-z][\\w-]*(?:=${VALUE}?)?${QUOTE}?(?:${gap}${VALUE})?`', 'const option = (gap) => String.raw`${QUOTE}?--?[A-Za-z][\\w-]*${QUOTE}?(?:${gap}${VALUE})?`'),
'R10 OPTION: long options only':('const option = (gap) => String.raw`${QUOTE}?--?[A-Za-z][\\w-]*(?:=${VALUE}?)?${QUOTE}?(?:${gap}${VALUE})?`', 'const option = (gap) => String.raw`${QUOTE}?--[A-Za-z][\\w-]*(?:=${VALUE}?)?${QUOTE}?(?:${gap}${VALUE})?`'),
'R11 VALUE: the double-quoted run dropped':('const VALUE = String.raw`(?:"[^"\\n]*"|\'[^\'\\n]*\'|${\'`\'}[^${\'`\'}\\n]*${\'`\'}|${SLOT}|\\[[^[\\]\\n]*\\]|\\([^()\\n]*\\)|\\$(?![{(])|[^\\s,\'"${\'`\'}()[\\]{}$])+`','const VALUE = String.raw`(?:\'[^\'\\n]*\'|${\'`\'}[^${\'`\'}\\n]*${\'`\'}|${SLOT}|\\[[^[\\]\\n]*\\]|\\([^()\\n]*\\)|\\$(?![{(])|[^\\s,\'"${\'`\'}()[\\]{}$])+`'),
'R11a VALUE: the single-quoted run dropped':('const VALUE = String.raw`(?:"[^"\\n]*"|\'[^\'\\n]*\'|${\'`\'}[^${\'`\'}\\n]*${\'`\'}|${SLOT}|\\[[^[\\]\\n]*\\]|\\([^()\\n]*\\)|\\$(?![{(])|[^\\s,\'"${\'`\'}()[\\]{}$])+`','const VALUE = String.raw`(?:"[^"\\n]*"|${\'`\'}[^${\'`\'}\\n]*${\'`\'}|${SLOT}|\\[[^[\\]\\n]*\\]|\\([^()\\n]*\\)|\\$(?![{(])|[^\\s,\'"${\'`\'}()[\\]{}$])+`'),
'R11b VALUE: a quoted run may hold no whitespace':('const VALUE = String.raw`(?:"[^"\\n]*"|\'[^\'\\n]*\'|${\'`\'}[^${\'`\'}\\n]*${\'`\'}|${SLOT}|\\[[^[\\]\\n]*\\]|\\([^()\\n]*\\)|\\$(?![{(])|[^\\s,\'"${\'`\'}()[\\]{}$])+`','const VALUE = String.raw`(?:"[^"\\s]*"|\'[^\'\\s]*\'|${\'`\'}[^${\'`\'}\\n]*${\'`\'}|${SLOT}|\\[[^[\\]\\n]*\\]|\\([^()\\n]*\\)|\\$(?![{(])|[^\\s,\'"${\'`\'}()[\\]{}$])+`'),
'R11c VALUE: the bare part dropped':('const VALUE = String.raw`(?:"[^"\\n]*"|\'[^\'\\n]*\'|${\'`\'}[^${\'`\'}\\n]*${\'`\'}|${SLOT}|\\[[^[\\]\\n]*\\]|\\([^()\\n]*\\)|\\$(?![{(])|[^\\s,\'"${\'`\'}()[\\]{}$])+`','const VALUE = String.raw`(?:"[^"\\n]*"|\'[^\'\\n]*\'|${\'`\'}[^${\'`\'}\\n]*${\'`\'}|${SLOT}|\\[[^[\\]\\n]*\\]|\\([^()\\n]*\\)|\\$(?![{(]))+`'),
'R11d VALUE: the slot dropped':('const VALUE = String.raw`(?:"[^"\\n]*"|\'[^\'\\n]*\'|${\'`\'}[^${\'`\'}\\n]*${\'`\'}|${SLOT}|\\[[^[\\]\\n]*\\]|\\([^()\\n]*\\)|\\$(?![{(])|[^\\s,\'"${\'`\'}()[\\]{}$])+`','const VALUE = String.raw`(?:"[^"\\n]*"|\'[^\'\\n]*\'|${\'`\'}[^${\'`\'}\\n]*${\'`\'}|\\[[^[\\]\\n]*\\]|\\([^()\\n]*\\)|\\$(?![{(])|[^\\s,\'"${\'`\'}()[\\]{}$])+`'),
'R11e SLOT: the braced slot dropped':('const SLOT = String.raw`\\$?\\{[^{}\\n]*\\}|\\$\\([^()\\n]*\\)`', 'const SLOT = String.raw`\\$\\([^()\\n]*\\)`'),
'R11f SLOT: the command substitution dropped':('const SLOT = String.raw`\\$?\\{[^{}\\n]*\\}|\\$\\([^()\\n]*\\)`', 'const SLOT = String.raw`\\$?\\{[^{}\\n]*\\}`'),
'L1 LEAD dropped: the line is the line of pr':('const LEAD = String.raw`([^\\s,([{]+(?:${LINE_GAP}${option(LINE_GAP)})*${LINE_GAP})?`', "const LEAD = '()?'"),
'L2 LEAD gap crosses a bare line end':('const LEAD = String.raw`([^\\s,([{]+(?:${LINE_GAP}${option(LINE_GAP)})*${LINE_GAP})?`', 'const LEAD = String.raw`([^\\s,([{]+(?:${GAP}${option(GAP)})*${GAP})?`'),
'L3 LINE_GAP: the continuation dropped':('const LINE_GAP = String.raw`(?:[^\\S\\n]|\\\\\\n|,)+`', 'const LINE_GAP = String.raw`(?:[^\\S\\n]|,)+`'),
'L4 the extent opens at the lead, not at pr':("callExtent(text, m.index + (m[1] || '').length, kind)",'callExtent(text, m.index, kind)'),
'L5 the program read again (gh by name only)':("const MERGE_CALL = new RegExp(`${LEAD}${word('pr')}${OPTIONS}${GAP}${word('merge')}` +", "const MERGE_CALL = new RegExp(`(gh${LINE_GAP})${word('pr')}${OPTIONS}${GAP}${word('merge')}` +"),
'RV2 GAP narrowed at pr->merge':("const MERGE_CALL = new RegExp(`${LEAD}${word('pr')}${OPTIONS}${GAP}${word('merge')}` +", "const MERGE_CALL = new RegExp(`${LEAD}${word('pr')}${OPTIONS}\\\\s+${word('merge')}` +"),
'RV5 no options between pr and merge':("const MERGE_CALL = new RegExp(`${LEAD}${word('pr')}${OPTIONS}${GAP}${word('merge')}` +", "const MERGE_CALL = new RegExp(`${LEAD}${word('pr')}${GAP}${word('merge')}` +"),
'T3 a triple quote closed by one quote mark':("    else if (text.startsWith(st.q, i)) { const k = st.q.length; st.q = ''; return k }","    else if (c === st.q[0]) { const k = st.q.length; st.q = ''; return k }"),
'R11g VALUE: the bracketed subscript dropped':('const VALUE = String.raw`(?:"[^"\\n]*"|\'[^\'\\n]*\'|${\'`\'}[^${\'`\'}\\n]*${\'`\'}|${SLOT}|\\[[^[\\]\\n]*\\]|\\([^()\\n]*\\)|\\$(?![{(])|[^\\s,\'"${\'`\'}()[\\]{}$])+`','const VALUE = String.raw`(?:"[^"\\n]*"|\'[^\'\\n]*\'|${\'`\'}[^${\'`\'}\\n]*${\'`\'}|${SLOT}|\\([^()\\n]*\\)|\\$(?![{(])|[^\\s,\'"${\'`\'}()[\\]{}$])+`'),
'R11h VALUE: the call arguments dropped':('const VALUE = String.raw`(?:"[^"\\n]*"|\'[^\'\\n]*\'|${\'`\'}[^${\'`\'}\\n]*${\'`\'}|${SLOT}|\\[[^[\\]\\n]*\\]|\\([^()\\n]*\\)|\\$(?![{(])|[^\\s,\'"${\'`\'}()[\\]{}$])+`','const VALUE = String.raw`(?:"[^"\\n]*"|\'[^\'\\n]*\'|${\'`\'}[^${\'`\'}\\n]*${\'`\'}|${SLOT}|\\[[^[\\]\\n]*\\]|\\$(?![{(])|[^\\s,\'"${\'`\'}()[\\]{}$])+`'),
'R11i VALUE: a lone $ dropped':('const VALUE = String.raw`(?:"[^"\\n]*"|\'[^\'\\n]*\'|${\'`\'}[^${\'`\'}\\n]*${\'`\'}|${SLOT}|\\[[^[\\]\\n]*\\]|\\([^()\\n]*\\)|\\$(?![{(])|[^\\s,\'"${\'`\'}()[\\]{}$])+`','const VALUE = String.raw`(?:"[^"\\n]*"|\'[^\'\\n]*\'|${\'`\'}[^${\'`\'}\\n]*${\'`\'}|${SLOT}|\\[[^[\\]\\n]*\\]|\\([^()\\n]*\\)|[^\\s,\'"${\'`\'}()[\\]{}$])+`'),
'R11j VALUE: one part only, no run':('const VALUE = String.raw`(?:"[^"\\n]*"|\'[^\'\\n]*\'|${\'`\'}[^${\'`\'}\\n]*${\'`\'}|${SLOT}|\\[[^[\\]\\n]*\\]|\\([^()\\n]*\\)|\\$(?![{(])|[^\\s,\'"${\'`\'}()[\\]{}$])+`','const VALUE = String.raw`(?:"[^"\\n]*"|\'[^\'\\n]*\'|${\'`\'}[^${\'`\'}\\n]*${\'`\'}|${SLOT}|\\[[^[\\]\\n]*\\]|\\([^()\\n]*\\)|\\$(?![{(])|[^\\s,\'"${\'`\'}()[\\]{}$])`'),
'G1 GAP: the line comment dropped':('const GAP = String.raw`(?:\\s|\\\\\\n|,|(?:#|\\/\\/)[^\\n]*\\n|\\/\\*[\\s\\S]*?\\*\\/|["\'${\'`\'}][^\\S\\n]*["\'${\'`\'}])+`','const GAP = String.raw`(?:\\s|\\\\\\n|,|\\/\\*[\\s\\S]*?\\*\\/|["\'${\'`\'}][^\\S\\n]*["\'${\'`\'}])+`'),
'G2 GAP: the JS line comment dropped':('const GAP = String.raw`(?:\\s|\\\\\\n|,|(?:#|\\/\\/)[^\\n]*\\n|\\/\\*[\\s\\S]*?\\*\\/|["\'${\'`\'}][^\\S\\n]*["\'${\'`\'}])+`','const GAP = String.raw`(?:\\s|\\\\\\n|,|#[^\\n]*\\n|\\/\\*[\\s\\S]*?\\*\\/|["\'${\'`\'}][^\\S\\n]*["\'${\'`\'}])+`'),
'G3 GAP: the block comment dropped':('const GAP = String.raw`(?:\\s|\\\\\\n|,|(?:#|\\/\\/)[^\\n]*\\n|\\/\\*[\\s\\S]*?\\*\\/|["\'${\'`\'}][^\\S\\n]*["\'${\'`\'}])+`','const GAP = String.raw`(?:\\s|\\\\\\n|,|(?:#|\\/\\/)[^\\n]*\\n|["\'${\'`\'}][^\\S\\n]*["\'${\'`\'}])+`'),
'G4 GAP: the adjacent-literal join dropped':('const GAP = String.raw`(?:\\s|\\\\\\n|,|(?:#|\\/\\/)[^\\n]*\\n|\\/\\*[\\s\\S]*?\\*\\/|["\'${\'`\'}][^\\S\\n]*["\'${\'`\'}])+`','const GAP = String.raw`(?:\\s|\\\\\\n|,|(?:#|\\/\\/)[^\\n]*\\n|\\/\\*[\\s\\S]*?\\*\\/)+`'),
'P1 the open bracket read on the line of pr only (the line-local scan)':('  for (let i = ps; i < at; i++) {','  for (let i = ls; i < at; i++) {'),
'P2 the statement start never moves back':('  for (let p; ps > 0 && (p','  for (let p; false && (p'),
'P3 the backward read resets no quote at a line end':("    if (c === '\\n' && st.q.length !== 3) { st = { q: '', esc: false }; continue }\n",''),
'P4 the backward read resets a triple quote at a line end':("    if (c === '\\n' && st.q.length !== 3) { st","    if (c === '\\n' && true) { st"),
'C1 the backward read skips no comment':("    if (commentAt(kind, text, i)) { const e = text.indexOf('\\n', i); if (e < 0) break; i = e - 1; continue }\n    if ('([{'.includes(c)) open.push(i)","    if ('([{'.includes(c)) open.push(i)"),
'C2 the forward read skips no comment':("    if (commentAt(kind, text, i)) { const e = text.indexOf('\\n', i); if (e < 0) break; i = e - 1; continue }\n    if ('([{'.includes(c)) depth++","    if ('([{'.includes(c)) depth++"),
"C3 a Python '#' opens a comment only at a word's start":("(kind === 'py' || !i ||",'(false || !i ||'),
'C4 no JS line comment':("kind === 'js' ? text.startsWith('//', i) :","kind === 'js' ? false :"),
'C5 a shell # opens a comment anywhere':("(kind === 'py' || !i || /\\s/.test(text[i - 1]))",'(true)'),
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
