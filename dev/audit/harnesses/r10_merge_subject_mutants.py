#!/usr/bin/env python3
"""R10-MERGE-SUBJECT-HARDEN (#2697): the mutation table for the merge-subject guard.

    python3 dev/audit/harnesses/r10_merge_subject_mutants.py   (from the repository root)

Applies each string-replacement mutant to tools/policy/agreement.mjs, runs
`node tools/policy/agreement.mjs --self-test`, prints the summary and every FAIL,
and restores the file (commit first: the restore writes the text read at start).
M, X and Y rows mutate the call extent and the quote reader, T rows the
triple quote, B the code-file test, R rows each named part and sub-part of
MERGE_CALL and SUBJECT_ARG, and RV rows each site a shared part (GAP, OPTIONS)
stands in, one site at a time. A survivor prints `N of N` and no FAIL.
Expected survivors: X5, Y9, Y10, each dispositioned in the PR body. A `NOT
APPLIED` line means the mutated text moved.
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
'M6 blank-line end deleted':('      if (!code && !text.slice(i + 1, next < 0 ? text.length : next).trim()) return text.slice(start, i)\n',''),
'M7 enclosing close not end':("&& --depth < 0) return text.slice(start, i + 1)","&& --depth < -99) return text.slice(start, i + 1)"),
'M8 start always line start':("const start = open.length ? open[open.length - 1] : ls","const start = ls"),
'M10 quotes not read':('  if (c === \'"\' || c === "\'") { st.q = text.startsWith(c.repeat(3), i) ? c.repeat(3) : c; return st.q.length }\n',''),
'M11 escapes not read':("    else if (c === '\\\\') st.esc = true\n",''),
'M12 blank-line state reset removed':("      st = { q: '', esc: false }\n      const next","      const next"),
'M13 pop on close before at removed':("    else if (')]}'.includes(c)) open.pop()\n",""),
'X1 backward quote skip':("    if (n) { i += n - 1; continue }\n    if ('([{'.includes(c)) open.push(i)","    if ('([{'.includes(c)) open.push(i)"),
'X2 forward quote skip':("    if (n) { i += n - 1; continue }\n    if ('([{'.includes(c)) depth++","    if ('([{'.includes(c)) depth++"),
'X3 push deleted':("open.push(i)","void 0"),
'X4 depth++ deleted':("if ('([{'.includes(c)) depth++","if ('([{'.includes(c)) {}"),
'X5 forward from open bracket':("start + (open.length ? 1 : 0)","start"),
'X6 first match only':("text.matchAll(new RegExp(MERGE_CALL.source, 'g'))","[text.match(MERGE_CALL)].filter(Boolean)"),
'Y1 close quote not cleared':("    else if (text.startsWith(st.q, i)) { const k = st.q.length; st.q = ''; return k }",'    else if (text.startsWith(st.q, i)) { const k = st.q.length; return k }'),
'Y2 line number off by one':("text.slice(0, m.index).split('\\n').length}","text.slice(0, m.index).split('\\n').length - 1}"),
'Y3 no line-end check for backslash nor open (always continue)':("      if (!open.length && !depth && text[i - 1] !== '\\\\') return text.slice(start, i)\n",""),
'Y4 open.length ignored at line end':("if (!open.length && !depth &&","if (!depth &&"),
'Y5 close ends extent at 0 not -1':("--depth < 0)","--depth < 1)"),
'Y6 calls.push deleted':("      calls.push(f)\n      if (SUBJECT_ARG","      if (SUBJECT_ARG"),
'Y7 ls off':("text.lastIndexOf('\\n', at - 1) + 1","0"),
'Y9 slice end exclusive at close':("return text.slice(start, i + 1)","return text.slice(start, i)"),
'Y10 blank-line return removed only text tail':("next < 0 ? text.length : next","next"),
'Y11 title space one -> any':(r"/^\S(?:.*\S)? \(#",r"/^\S(?:.*\S)?\s+\(#"),
'Y12 title leading \\S -> .':(r"/^\S(?:.*\S)? \(#",r"/^.(?:.*\S)? \(#"),
'R1 QUOTE: double quote only': ('const QUOTE = \'["\\\'`]\'', 'const QUOTE = \'["]\''),
'R2 GAP: the \\-newline continuation dropped': ('const GAP = String.raw`(?:\\s|\\\\\\n|,)+`', 'const GAP = String.raw`(?:\\s|,)+`'),
'R3 GAP: the argv comma dropped': ('const GAP = String.raw`(?:\\s|\\\\\\n|,)+`', 'const GAP = String.raw`(?:\\s|\\\\\\n)+`'),
'R4 word: the end-of-word lookahead dropped': ('const word = (w) => `${QUOTE}?${w}${QUOTE}?(?![\\\\w-])`', 'const word = (w) => `${QUOTE}?${w}${QUOTE}?`'),
'R5 word: the opening quote dropped': ('const word = (w) => `${QUOTE}?${w}${QUOTE}?(?![\\\\w-])`', 'const word = (w) => `${w}${QUOTE}?(?![\\\\w-])`'),
'R6 word: the closing quote dropped': ('const word = (w) => `${QUOTE}?${w}${QUOTE}?(?![\\\\w-])`', 'const word = (w) => `${QUOTE}?${w}(?![\\\\w-])`'),
'R7 OPTIONS: no option between words': ('const OPTIONS = `(?:${GAP}${OPTION})*`', "const OPTIONS = ''"),
'R8 OPTION: the separate value dropped': ('const OPTION = String.raw`${QUOTE}?--?[A-Za-z][\\w-]*(?:=[^\\s,\'"${\'`\'}\\]]*)?${QUOTE}?` +\n  `(?:${GAP}${QUOTE}?[^\\\\s,\'"${\'`\'}\\\\]]+${QUOTE}?)?`', 'const OPTION = String.raw`${QUOTE}?--?[A-Za-z][\\w-]*(?:=[^\\s,\'"${\'`\'}\\]]*)?${QUOTE}?`'),
'R9 OPTION: the =value dropped': ('const OPTION = String.raw`${QUOTE}?--?[A-Za-z][\\w-]*(?:=[^\\s,\'"${\'`\'}\\]]*)?${QUOTE}?` +', 'const OPTION = String.raw`${QUOTE}?--?[A-Za-z][\\w-]*${QUOTE}?` +'),
'R10 OPTION: long options only': ('const OPTION = String.raw`${QUOTE}?--?[A-Za-z][\\w-]*(?:=[^\\s,\'"${\'`\'}\\]]*)?${QUOTE}?` +', 'const OPTION = String.raw`${QUOTE}?--[A-Za-z][\\w-]*(?:=[^\\s,\'"${\'`\'}\\]]*)?${QUOTE}?` +'),
'R12 PROGRAM: the variable program dropped': ('const PROGRAM = String.raw`(?:(?<![\\w$./-])(?:[\\w./-]*\\/)?gh|\\$\\{?[A-Za-z_]\\w*\\}?)${QUOTE}?`', 'const PROGRAM = String.raw`(?:(?<![\\w$./-])(?:[\\w./-]*\\/)?gh)${QUOTE}?`'),
'R13 PROGRAM: an unbraced variable only': ('const PROGRAM = String.raw`(?:(?<![\\w$./-])(?:[\\w./-]*\\/)?gh|\\$\\{?[A-Za-z_]\\w*\\}?)${QUOTE}?`', 'const PROGRAM = String.raw`(?:(?<![\\w$./-])(?:[\\w./-]*\\/)?gh|\\$[A-Za-z_]\\w*)${QUOTE}?`'),
'R14 PROGRAM: the path dropped': ('const PROGRAM = String.raw`(?:(?<![\\w$./-])(?:[\\w./-]*\\/)?gh|\\$\\{?[A-Za-z_]\\w*\\}?)${QUOTE}?`', 'const PROGRAM = String.raw`(?:(?<![\\w$./-])gh|\\$\\{?[A-Za-z_]\\w*\\}?)${QUOTE}?`'),
'R15 PROGRAM: the lookbehind dropped': ('const PROGRAM = String.raw`(?:(?<![\\w$./-])(?:[\\w./-]*\\/)?gh|\\$\\{?[A-Za-z_]\\w*\\}?)${QUOTE}?`', 'const PROGRAM = String.raw`(?:(?:[\\w./-]*\\/)?gh|\\$\\{?[A-Za-z_]\\w*\\}?)${QUOTE}?`'),
'R16 PROGRAM: the closing quote dropped': ('const PROGRAM = String.raw`(?:(?<![\\w$./-])(?:[\\w./-]*\\/)?gh|\\$\\{?[A-Za-z_]\\w*\\}?)${QUOTE}?`', 'const PROGRAM = String.raw`(?:(?<![\\w$./-])(?:[\\w./-]*\\/)?gh|\\$\\{?[A-Za-z_]\\w*\\}?)`'),
'R17 the quoted pr/merge arm dropped': ('  `|${QUOTE}pr${QUOTE}${OPTIONS}${GAP}${QUOTE}merge${QUOTE}` +\n', ''),
'R18 merge_pull_request dropped': ('  String.raw`|merge_pull_request|mergePullRequest|\\/pulls\\/\\S+\\/merge\\b`)', '  String.raw`|mergePullRequest|\\/pulls\\/\\S+\\/merge\\b`)'),
'R19 mergePullRequest dropped': ('  String.raw`|merge_pull_request|mergePullRequest|\\/pulls\\/\\S+\\/merge\\b`)', '  String.raw`|merge_pull_request|\\/pulls\\/\\S+\\/merge\\b`)'),
'R20 the REST merge path dropped': ('  String.raw`|merge_pull_request|mergePullRequest|\\/pulls\\/\\S+\\/merge\\b`)', '  String.raw`|merge_pull_request|mergePullRequest`)'),
'R21 SUBJECT_ARG: short flags alone, no cluster': ('const SUBJECT_ARG = new RegExp(String.raw`(?:^|[\\s"\'[,])(?:--(?:subject|title|body|body-file)(?=[\\s="\',\\]]|$)|-[mrsd]*[tbF])` +', 'const SUBJECT_ARG = new RegExp(String.raw`(?:^|[\\s"\'[,])(?:--(?:subject|title|body|body-file)(?=[\\s="\',\\]]|$)|-[tbF](?=[\\s="\',\\]]|$))` +'),
'R22 SUBJECT_ARG: -d not a cluster flag': ('const SUBJECT_ARG = new RegExp(String.raw`(?:^|[\\s"\'[,])(?:--(?:subject|title|body|body-file)(?=[\\s="\',\\]]|$)|-[mrsd]*[tbF])` +', 'const SUBJECT_ARG = new RegExp(String.raw`(?:^|[\\s"\'[,])(?:--(?:subject|title|body|body-file)(?=[\\s="\',\\]]|$)|-[mrs]*[tbF])` +'),
'R23 SUBJECT_ARG: -F dropped from the short flags': ('const SUBJECT_ARG = new RegExp(String.raw`(?:^|[\\s"\'[,])(?:--(?:subject|title|body|body-file)(?=[\\s="\',\\]]|$)|-[mrsd]*[tbF])` +', 'const SUBJECT_ARG = new RegExp(String.raw`(?:^|[\\s"\'[,])(?:--(?:subject|title|body|body-file)(?=[\\s="\',\\]]|$)|-[mrsd]*[tb])` +'),
'R24 SUBJECT_ARG: commitHeadline/commitBody dropped': ('  String.raw`|\\bcommit_(?:title|message)\\b|\\bcommit(?:Headline|Body)\\b`)', '  String.raw`|\\bcommit_(?:title|message)\\b`)'),
'R25 GAP: whitespace narrowed to one literal space': ('const GAP = String.raw`(?:\\s|\\\\\\n|,)+`', 'const GAP = String.raw`(?: |\\\\\\n|,)+`'),
'R26 GAP: one separator only, no run': ('const GAP = String.raw`(?:\\s|\\\\\\n|,)+`', 'const GAP = String.raw`(?:\\s|\\\\\\n|,)`'),
'T1 triple quote not one mark':('  if (c === \'"\' || c === "\'") { st.q = text.startsWith(c.repeat(3), i) ? c.repeat(3) : c; return st.q.length }','  if (c === \'"\' || c === "\'") { st.q = false ? c.repeat(3) : c; return st.q.length }'),
'T2 a line end inside a triple quote ends the call':('      if (st.q.length === 3) continue\n',''),
'B1 a blank line ends a bracketed call in every file':('    const text = read(f); const code = /\\.(py|mjs|js|cjs)$/.test(f)','    const text = read(f); const code = false'),
'R8 OPTION: the separate value dropped':('const OPTION = String.raw`${QUOTE}?--?[A-Za-z][\\w-]*(?:=${VALUE}?)?${QUOTE}?(?:${GAP}${VALUE})?`','const OPTION = String.raw`${QUOTE}?--?[A-Za-z][\\w-]*(?:=${VALUE}?)?${QUOTE}?`'),
'R9 OPTION: the =value dropped':('const OPTION = String.raw`${QUOTE}?--?[A-Za-z][\\w-]*(?:=${VALUE}?)?${QUOTE}?(?:${GAP}${VALUE})?`','const OPTION = String.raw`${QUOTE}?--?[A-Za-z][\\w-]*${QUOTE}?(?:${GAP}${VALUE})?`'),
'R10 OPTION: long options only':('const OPTION = String.raw`${QUOTE}?--?[A-Za-z][\\w-]*(?:=${VALUE}?)?${QUOTE}?(?:${GAP}${VALUE})?`','const OPTION = String.raw`${QUOTE}?--[A-Za-z][\\w-]*(?:=${VALUE}?)?${QUOTE}?(?:${GAP}${VALUE})?`'),
'R11 VALUE: the double-quoted run dropped':('const VALUE = String.raw`(?:"[^"\\n]*"|\'[^\'\\n]*\'|${\'`\'}[^${\'`\'}\\n]*${\'`\'}|[^\\s,\'"${\'`\'}\\]]+)`','const VALUE = String.raw`(?:\'[^\'\\n]*\'|${\'`\'}[^${\'`\'}\\n]*${\'`\'}|[^\\s,\'"${\'`\'}\\]]+)`'),
'R11a VALUE: the single-quoted run dropped':('const VALUE = String.raw`(?:"[^"\\n]*"|\'[^\'\\n]*\'|${\'`\'}[^${\'`\'}\\n]*${\'`\'}|[^\\s,\'"${\'`\'}\\]]+)`','const VALUE = String.raw`(?:"[^"\\n]*"|${\'`\'}[^${\'`\'}\\n]*${\'`\'}|[^\\s,\'"${\'`\'}\\]]+)`'),
'R11b VALUE: a quoted run may hold no whitespace':('const VALUE = String.raw`(?:"[^"\\n]*"|\'[^\'\\n]*\'|${\'`\'}[^${\'`\'}\\n]*${\'`\'}|[^\\s,\'"${\'`\'}\\]]+)`','const VALUE = String.raw`(?:"[^"\\s]*"|\'[^\'\\s]*\'|${\'`\'}[^${\'`\'}\\n]*${\'`\'}|[^\\s,\'"${\'`\'}\\]]+)`'),
'R11c VALUE: the bare run dropped':('const VALUE = String.raw`(?:"[^"\\n]*"|\'[^\'\\n]*\'|${\'`\'}[^${\'`\'}\\n]*${\'`\'}|[^\\s,\'"${\'`\'}\\]]+)`','const VALUE = String.raw`(?:"[^"\\n]*"|\'[^\'\\n]*\'|${\'`\'}[^${\'`\'}\\n]*${\'`\'})`'),
'R12 PROGRAM: the variable program dropped':('  String.raw`|\\$(?:[A-Za-z_]\\w*|\\{[A-Za-z_]\\w*(?::?[-=?+][^}\\n]*)?\\}|\\([^()\\n]*\\)))${QUOTE}?`','  String.raw`|\\$(?!))${QUOTE}?`'),
'R13 PROGRAM: an unbraced variable only':('  String.raw`|\\$(?:[A-Za-z_]\\w*|\\{[A-Za-z_]\\w*(?::?[-=?+][^}\\n]*)?\\}|\\([^()\\n]*\\)))${QUOTE}?`','  String.raw`|\\$(?:[A-Za-z_]\\w*|\\([^()\\n]*\\)))${QUOTE}?`'),
'R13a PROGRAM: a braced variable takes no default':('  String.raw`|\\$(?:[A-Za-z_]\\w*|\\{[A-Za-z_]\\w*(?::?[-=?+][^}\\n]*)?\\}|\\([^()\\n]*\\)))${QUOTE}?`','  String.raw`|\\$(?:[A-Za-z_]\\w*|\\{[A-Za-z_]\\w*\\}|\\([^()\\n]*\\)))${QUOTE}?`'),
'R13b PROGRAM: the command substitution dropped':('  String.raw`|\\$(?:[A-Za-z_]\\w*|\\{[A-Za-z_]\\w*(?::?[-=?+][^}\\n]*)?\\}|\\([^()\\n]*\\)))${QUOTE}?`','  String.raw`|\\$(?:[A-Za-z_]\\w*|\\{[A-Za-z_]\\w*(?::?[-=?+][^}\\n]*)?\\}))${QUOTE}?`'),
'R14 PROGRAM: the path dropped':('const PROGRAM = String.raw`(?:(?<![\\w$./-])(?:[\\w./-]*\\/)?gh(?:\\.exe)?` +','const PROGRAM = String.raw`(?:(?<![\\w$./-])gh(?:\\.exe)?` +'),
'R15 PROGRAM: the lookbehind dropped':('const PROGRAM = String.raw`(?:(?<![\\w$./-])(?:[\\w./-]*\\/)?gh(?:\\.exe)?` +','const PROGRAM = String.raw`(?:(?:[\\w./-]*\\/)?gh(?:\\.exe)?` +'),
'R16 PROGRAM: the closing quote dropped':('  String.raw`|\\$(?:[A-Za-z_]\\w*|\\{[A-Za-z_]\\w*(?::?[-=?+][^}\\n]*)?\\}|\\([^()\\n]*\\)))${QUOTE}?`','  String.raw`|\\$(?:[A-Za-z_]\\w*|\\{[A-Za-z_]\\w*(?::?[-=?+][^}\\n]*)?\\}|\\([^()\\n]*\\)))`'),
'R16a PROGRAM: gh.exe dropped':('const PROGRAM = String.raw`(?:(?<![\\w$./-])(?:[\\w./-]*\\/)?gh(?:\\.exe)?` +','const PROGRAM = String.raw`(?:(?<![\\w$./-])(?:[\\w./-]*\\/)?gh` +'),
'RV1 GAP narrowed at program->pr':("const MERGE_CALL = new RegExp(`${PROGRAM}${OPTIONS}${GAP}${word('pr')}${OPTIONS}${GAP}${word('merge')}` +","const MERGE_CALL = new RegExp(`${PROGRAM}${OPTIONS}\\\\s+${word('pr')}${OPTIONS}${GAP}${word('merge')}` +"),
'RV2 GAP narrowed at pr->merge':("const MERGE_CALL = new RegExp(`${PROGRAM}${OPTIONS}${GAP}${word('pr')}${OPTIONS}${GAP}${word('merge')}` +","const MERGE_CALL = new RegExp(`${PROGRAM}${OPTIONS}${GAP}${word('pr')}${OPTIONS}\\\\s+${word('merge')}` +"),
'RV3 GAP narrowed in the quoted arm':('  `|${QUOTE}pr${QUOTE}${OPTIONS}${GAP}${QUOTE}merge${QUOTE}` +','  `|${QUOTE}pr${QUOTE}${OPTIONS}, ${QUOTE}merge${QUOTE}` +'),
'RV4 no options before pr':("const MERGE_CALL = new RegExp(`${PROGRAM}${OPTIONS}${GAP}${word('pr')}${OPTIONS}${GAP}${word('merge')}` +","const MERGE_CALL = new RegExp(`${PROGRAM}${GAP}${word('pr')}${OPTIONS}${GAP}${word('merge')}` +"),
'RV5 no options between pr and merge':("const MERGE_CALL = new RegExp(`${PROGRAM}${OPTIONS}${GAP}${word('pr')}${OPTIONS}${GAP}${word('merge')}` +","const MERGE_CALL = new RegExp(`${PROGRAM}${OPTIONS}${GAP}${word('pr')}${GAP}${word('merge')}` +"),
'RV6 no options in the quoted arm':('  `|${QUOTE}pr${QUOTE}${OPTIONS}${GAP}${QUOTE}merge${QUOTE}` +','  `|${QUOTE}pr${QUOTE}${GAP}${QUOTE}merge${QUOTE}` +'),
'T3 a triple quote closed by one quote mark':("    else if (text.startsWith(st.q, i)) { const k = st.q.length; st.q = ''; return k }","    else if (c === st.q[0]) { const k = st.q.length; st.q = ''; return k }"),
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
