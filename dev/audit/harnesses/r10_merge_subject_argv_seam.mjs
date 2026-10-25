// R10-MERGE-SUBJECT-HARDEN (#2697): the dismissed open seam of the merge-subject
// writer scan. `subjectWriters` reads a merge call's own bracket group
// (`callExtent`), so a subject flag outside that group -- an argv list built
// across expressions -- is not read. A lexical scan cannot follow that; merges
// go only through tools/audit/seat/merge_pr.sh and merge_train.py, which pass
// no --subject. This prints what the guard refuses for each probe shape.
//   node dev/audit/harnesses/r10_merge_subject_argv_seam.mjs [tools/policy/agreement.mjs]
// Expected at the fix head: [] [] ["f:1"] -- the first two are the seam, the
// third is the control (a flag inside the argv list is refused).
// Then the program class: every interpolation shape over every program name,
// generated here independently of the guard's own probes, once running
// `pr merge` (each must be refused, ["f:1"]) and once `pr view` (the null
// control, each must be []). It prints one PROGRAM-CLASS line per shape and
// a total: `PROGRAM-CLASS merge refused=<k> of <n>; view refused=<j> of <n>`.
// Then the extent class: each argv shape whose open bracket stands lines before
// `pr` (wrapped after the program, exploded one element per line), under a .py,
// .mjs and .sh name, with the subject on a later line (refused) and with none
// and a later statement's flag (the null control): `WRAPPED merge refused=<k>
// of <n>; null refused=<j> of <n>`.
// Then THE CLASS #2697 CLOSES, as a table: one row per spelling, each run with
// a subject (refused) and as its null twin (`pr view`, or the call without the
// subject field: passed). A row is the rule's, not an instance's: the table is
// the stated class, and a spelling it does not list is not claimed. It prints
// `CLASS <row>: merge refused|PASSED; null passed|REFUSED` and
// `CLASS merge refused=<k> of <n>; null refused=<j> of <n>`; the PROGRAM-CLASS
// and WRAPPED lines above are its program and extent rows.
// Last, the spellings OPEN at #2697's head, each named by the group that owns
// it: `OPEN <group> <spelling>: XFAIL` while the guard does not read its
// subject, `held` once it does, and `OPEN <group> expected-fail: held=<k> of
// <n>`. R10-MERGE-SUBJECT-CASEARM is a strict expected-fail: it closes only at
// held=n of n; its routed list is #2697's two spellings outside that class.
import fs from 'node:fs'
const src = fs.readFileSync(process.argv[2] || 'tools/policy/agreement.mjs', 'utf8')
// The guard block; a guard from before the extent reader (the merge base's) opens
// at its subject-flag comment.
const head = src.indexOf('// WHAT A MERGE CALL IS')
const from = head < 0 ? src.indexOf('// What a merge call may not carry') : head; const to = src.indexOf("// WHICH LINE IS MAIN'S")
if (from < 0 || to < 0) { console.error('seam probe: guard block not found'); process.exit(2) }
const block = src.slice(from, to).replace(/^function nonTemplateMerges[\s\S]*?\n}\n/m, '')
const subjectWriters = new Function(block + '\nreturn subjectWriters')()
const shapes = [
  'run(["gh", "pr", "merge", n] + ["--subject", s])',
  'args = ["gh", "pr", "merge", n]\nargs += ["--subject", s]\nrun(args)',
  'run(["gh", "pr", "merge", n, "--subject", s])',
]
for (const t of shapes) console.log(JSON.stringify(subjectWriters(['f'], () => t).bad), JSON.stringify(t))
const programs = ['gh', '/usr/bin/gh', 'GH', 'gh_bin', 'self.gh', 'cfg.gh', 'cfg["gh"]', 'os.environ["GH"]', 'shutil.which("gh")', 'which_gh()', 'hub', 'hgh']
const B = '`'
const forms = {
  'f-string': (p, v) => `os.system(f"{${p}} pr ${v} {n} --subject x")`,
  'f-string, single quotes': (p, v) => `os.system(f'{${p}} pr ${v} {n} -t x')`,
  '%-format': (p, v) => `os.system("%s pr ${v} %s --subject x" % (${p}, n))`,
  '%r-format': (p, v) => `os.system("%r pr ${v} %d -t x" % (${p}, n))`,
  '.format': (p, v) => `os.system("{} pr ${v} {} -t x".format(${p}, n))`,
  '.format, indexed': (p, v) => `os.system("{0} pr ${v} {1} --subject x".format(${p}, n))`,
  'template literal': (p, v) => `execSync(${B}\${${p}} pr ${v} \${n} --subject x${B})`,
  'concatenation': (p, v) => `os.system(${p} + " pr ${v} " + str(n) + " --subject x")`,
  'list join': (p, v) => `os.system(" ".join([${p}, "pr", "${v}", n, "-t", x]))`,
  'JS array join': (p, v) => `execSync([${p}, 'pr', '${v}', n, '--subject', x].join(' '))`,
  'shell $(...)': (p, v) => `$(${p}) pr ${v} 9 --subject x`,
  'shell "${...}"': (p, v) => `"\${${p}}" pr ${v} 9 -t x`,
}
let km = 0, kv = 0, tot = 0
for (const [name, form] of Object.entries(forms)) {
  let m = 0, w = 0
  for (const p of programs) {
    if (JSON.stringify(subjectWriters(['f'], () => form(p, 'merge') + '\n').bad) === '["f:1"]') m++
    if (subjectWriters(['f'], () => form(p, 'view') + '\n').bad.length) w++
  }
  console.log(`PROGRAM-CLASS ${name}: merge refused=${m} of ${programs.length}; view refused=${w} of ${programs.length}`)
  km += m; kv += w; tot += programs.length
}
console.log(`PROGRAM-CLASS merge refused=${km} of ${tot}; view refused=${kv} of ${tot}`)
const wrapped = {
  'argv wrapped after gh': [(e) => `subprocess.run(["gh",\n               "pr", "merge", str(n), "--squash",${e}], check=True)\n`, '\n               "--subject", s'],
  'argv wrapped after GH': [(e) => `run([GH,\n     "pr", "merge", str(n),${e}])\n`, '\n     "--subject", s'],
  'exploded argv': [(e) => `run([\n    "gh",\n    "pr",\n    "merge",\n    str(n),${e}\n])\n`, '\n    "--subject",\n    s,'],
  'exploded JS argv': [(e) => `execFileSync('gh', [\n  'pr',\n  'merge',\n  String(n),${e}\n])\n`, "\n  '--subject',\n  s,"],
}
let wm = 0, wn = 0, wt = 0
for (const [name, [form, subj]] of Object.entries(wrapped)) {
  for (const f of ['f.py', 'f.mjs', 'f.sh']) {
    const m = subjectWriters([f], () => form(subj)).bad.length === 1; const z = subjectWriters([f], () => form('') + 'other("--subject", s)\n').bad.length > 0
    console.log(`WRAPPED ${name} ${f}: merge ${m ? 'refused' : 'PASSED'}; null ${z ? 'REFUSED' : 'passed'}`)
    wm += m; wn += z; wt++
  }
}
console.log(`WRAPPED merge refused=${wm} of ${wt}; null refused=${wn} of ${wt}`)
const fl = (v, f) => `gh pr ${v} 9 ${f}`
const rows = [
  ['gh pr merge', 'f.sh', (v) => `gh pr ${v} 9 --squash --subject "x y"`],
  ['a double-quoted word', 'f.sh', (v) => `gh pr "${v}" 9 --subject x`],
  ['a single-quoted word', 'f.sh', (v) => `gh pr '${v}' 9 -t x`],
  ['a \\-newline before pr', 'f.sh', (v) => `gh \\\n  pr ${v} 9 --subject x`],
  ['a \\-newline before merge', 'f.sh', (v) => `gh pr \\\n  ${v} 9 --subject x`],
  ['the subject on a continued line', 'f.sh', (v) => `gh pr ${v} 9 --squash \\\n  --subject x`],
  ['a Python argv', 'f.py', (v) => `run(["gh", "pr", "${v}", n, "--subject", s])`],
  ['a single-quoted argv', 'f.py', (v) => `run(['gh', 'pr', '${v}', n, '--subject', s])`],
  ['a space before an argv comma', 'f.py', (v) => `run(["gh", "pr" , "${v}", n, "-t", s])`],
  ['a # comment between the words', 'f.py', (v) => `run(["gh", "pr",  # c\n     "${v}", n, "--subject", s])`],
  ['a // comment between the words', 'f.mjs', (v) => `execFileSync('gh', ['pr', // c\n  '${v}', n, '--subject', s])`],
  ['a /* */ comment between the words', 'f.mjs', (v) => `execFileSync('gh', ['pr', /* c */ '${v}', n, '--subject', s])`],
  ['two adjacent literals', 'f.py', (v) => `os.system("gh pr " "${v} 9 --subject x")`],
  ['-R o/r between', 'f.sh', (v) => `gh pr -R o/r ${v} 9 --subject x`],
  ['--subject "x y" between', 'f.sh', (v) => `gh pr --subject "x y" ${v} 9`],
  ['-t "x y" between', 'f.sh', (v) => `gh pr -t "x y" ${v} 9`],
  ['-R $(cat r) between', 'f.sh', (v) => `gh pr -R $(cat r) ${v} 9 -t x`],
  ['-R "$O"/"$R" between', 'f.sh', (v) => `gh pr -R "$O"/"$R" ${v} 9 -t x`],
  ['-R {repo} between', 'f.py', (v) => `os.system(f"gh pr -R {repo} ${v} {n} --subject x")`],
  ['a subscript value between', 'f.py', (v) => `run(["gh", "pr", "-R", cfg["repo"], "${v}", n, "--subject", s])`],
  ['an environ value between', 'f.py', (v) => `run(["gh", "pr", "-R", os.environ["REPO"], "${v}", n, "-t", s])`],
  ['an indexed value between', 'f.py', (v) => `run(["gh", "pr", "-R", REPOS[0], "${v}", n, "-t", s])`],
  ['a call value between', 'f.py', (v) => `run(["gh", "pr", "-R", join(o, r), "${v}", n, "--subject", s])`],
  ['an f-string value between', 'f.py', (v) => `run(["gh", "pr", "-R", f"{o}/{r}", "${v}", n, "--subject", s])`],
  ['a JS subscript value between', 'f.mjs', (v) => `execFileSync('gh', ['pr', '-R', cfg['repo'], '${v}', n, '--subject', s])`],
  ...['--subject x', '--subject=x', '--title x', '--body x', '--body-file f', '-t x', '-tx', '-b x', '-F f', '-mt x', '-dmb x', '-mF f']
    .map((f) => [`the flag ${f}`, 'f.sh', (v) => fl(v, f)]),
  ['an exploded call of separate arguments', 'f.py', (v) => `run(\n    "gh",\n    "pr",\n    "${v}",\n    n,\n    "--subject",\n    s,\n)`],
  ['a call split over lines', 'f.py', (v) => `self.run(["gh", "pr", "${v}", n, "--repo", R,\n         "--subject", s])`],
  ['a paren in a shell comment above', 'f.sh', (v) => `# merge (via gh\ngh pr ${v} 9 --subject x`],
  ['merge_pull_request(commit_title=)', 'f.py', (v) => v === 'merge' ? 'merge_pull_request(o, r, n, commit_title=s)' : 'merge_pull_request(o, r, n)'],
  ['/pulls/N/merge -f commit_message=', 'f.sh', (v) => v === 'merge' ? 'gh api -X PUT repos/o/r/pulls/9/merge -f commit_message=x' : 'gh api -X PUT repos/o/r/pulls/9/merge'],
  ['mergePullRequest(commitHeadline:)', 'f.mjs', (v) => v === 'merge' ? 'q(`mutation { mergePullRequest(input: {pullRequestId: $id, commitHeadline: "x"}) { clientMutationId } }`)' : 'q(`mutation { mergePullRequest(input: {pullRequestId: $id}) { clientMutationId } }`)'],
]
let cm = 0, cn = 0
for (const [name, f, t] of rows) {
  const m = subjectWriters([f], () => t('merge') + '\n').bad.length === 1; const z = subjectWriters([f], () => t('view') + '\n').bad.length > 0
  console.log(`CLASS ${name} ${f}: merge ${m ? 'refused' : 'PASSED'}; null ${z ? 'REFUSED' : 'passed'}`)
  cm += m; cn += z
}
console.log(`CLASS merge refused=${cm} of ${rows.length}; null refused=${cn} of ${rows.length}`)
// R10-MERGE-SUBJECT-CASEARM owns every shell case-arm spelling of a merge
// writer: with and without the leading paren, at any indentation, and
// multi-pattern arms. #2697's extent starts the forward read at the line's
// start, so an unmatched `)` there ends the call before `pr`.
const open = {
  'R10-MERGE-SUBJECT-CASEARM': [
    ...['', '  ', '        ', '\t'].flatMap((ind) => ['never)', '(never)', 'a|b)', '(a|b)'].flatMap((pat) => ['f.sh', 'f.md'].map((f) =>
      [`${JSON.stringify(ind + pat)} ${f}`, f, (v) => `case "$m" in\n${ind}${pat} gh pr ${v} "$n" --squash --subject "x" ;;\nesac`]))),
    ['one-line x) gh pr merge 9 -t s f.sh', 'f.sh', (v) => `x) gh pr ${v} 9 -t s`],
  ],
  // Two spellings outside that class text, routed to the same group by #2697's
  // body (the guard's next owner): a blank line between the argv's bracket and
  // `pr` in a Python or JS file, and a closer in a JS block comment after merge.
  'R10-MERGE-SUBJECT-CASEARM routed': [
    ['a blank line in a Python argv f.py', 'f.py', (v) => `run([
    "gh",

    "pr", "${v}", n,
    "--subject", s])`],
    ['a blank line in a JS argv f.mjs', 'f.mjs', (v) => `execFileSync('gh', [

  'pr', '${v}', n,
  '--subject', s])`],
    ['a closer in a JS block comment f.mjs', 'f.mjs', (v) => `execFileSync('gh', ['pr', '${v}', n, /* ) */ '--subject', s])`],
  ],
}
for (const [group, spellings] of Object.entries(open)) {
  let k = 0, z = 0
  for (const [name, f, t] of spellings) {
    const m = subjectWriters([f], () => t('merge') + '\n').bad.length === 1
    if (subjectWriters([f], () => t('view') + '\n').bad.length) z++
    console.log(`OPEN ${group} ${name}: ${m ? 'held' : 'XFAIL'}`)
    k += m
  }
  console.log(`OPEN ${group} expected-fail: held=${k} of ${spellings.length}; null refused=${z} of ${spellings.length}`)
}
