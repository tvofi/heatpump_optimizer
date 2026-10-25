// R10-MERGE-SUBJECT-HARDEN (#2697): the differential against main's line guard.
// #2697 replaces a guard that reads each line whole with one that reads a call's
// extent, so it may not pass a writer main refuses. This runs both guards'
// `subjectWriters` over one corpus and prints, per corpus part and in total,
//   `<part> lines=N refused_main=A refused_head=B main_not_head=K`
// where N is the lines read, A and B the refused `file:line` keys, and K the keys
// main refuses and the head does not: refused-at-main is a subset of
// refused-at-head exactly when K is 0. The null twin of every generated writer
// (its subject flag deleted) prints `null refused_main=.. refused_head=..`.
//   node dev/audit/harnesses/r10_merge_subject_differential.mjs <main-ref> [<head-ref>]
// (from the repository root; a ref's tools/policy/agreement.mjs is read with
// `git show`, the head's from the working tree when no head ref is given).
// The corpus: the tree's scanned files (the finder's harness surface), the
// reviewer's plants of round 8 (verdict/2697 evidence: md_plant.sh, probe.mjs,
// probe2.mjs, probe3.mjs, copied verbatim), and a generated class: every lead
// that holds a closer with no opener on the line, before every writer, tail,
// indentation and file kind below.
import { execFileSync } from 'node:child_process'
import fs from 'node:fs'
const git = (a) => execFileSync('git', a, { encoding: 'utf8', maxBuffer: 1 << 28 })
const [mainRef, headRef] = process.argv.slice(2)
if (!mainRef) { console.error('usage: r10_merge_subject_differential.mjs <main-ref> [<head-ref>]'); process.exit(2) }
const AG = 'tools/policy/agreement.mjs'
// The guard block of either shape: main's opens at its subject-flag comment.
// nonTemplateMerges reads constants defined later in the file; cut it out, by
// position, as the census does.
const load = (src) => {
  const h = src.indexOf('// WHAT A MERGE CALL IS'); const from = h < 0 ? src.indexOf('// What a merge call may not carry') : h
  const to = src.indexOf("// WHICH LINE IS MAIN'S")
  if (from < 0 || to < 0) { console.error('differential: guard block not found'); process.exit(2) }
  let block = src.slice(from, to)
  const nt = block.indexOf('function nonTemplateMerges'); if (nt >= 0) block = block.slice(0, nt) + block.slice(block.indexOf('\n}\n', nt) + 3)
  return new Function(block + '\nreturn subjectWriters')()
}
const main = load(git(['show', `${mainRef}:${AG}`]))
const head = load(headRef ? git(['show', `${headRef}:${AG}`]) : fs.readFileSync(AG, 'utf8'))
const parts = {}
const run = (part, f, text) => {
  const p = (parts[part] ??= { lines: 0, main: 0, head: 0, miss: [] })
  const m = new Set(main([f], () => text).bad); const h = new Set(head([f], () => text).bad)
  p.lines += text.split('\n').length
  p.main += m.size; p.head += h.size
  for (const k of m) if (!h.has(k)) p.miss.push(`${k} ${JSON.stringify(text.length > 120 ? text.slice(0, 120) + '...' : text)}`)
}
// 1. The tree: the guard's own file list, read from the working tree, spelled
// with string tests as the census spells it, so no second copy of its grammar.
for (const f of git(['ls-files', 'tools', '.claude/workflows']).split('\n')
  .filter((f) => ['.py', '.mjs', '.js', '.cjs', '.sh', '.md'].some((x) => f.endsWith(x))
    && !(f.startsWith('tools/audit/round') && '0123456789'.includes(f['tools/audit/round'.length] ?? '')) && !f.includes('/fixtures/') && f !== AG)) {
  run('tree', f, fs.readFileSync(f, 'utf8'))
}
// 2. The reviewer's plants, verbatim.
const plants = [
  ['f.md', 'Merge it by hand (the train is\ndown) with `gh pr merge 9 --subject x`.'],
  ['f.md', 'Merge it by hand (the train is\n\ndown) with `gh pr merge 9 --subject x`.'],
  ['f.md', 'Merge it by hand (the train is down)\nwith `gh pr merge 9 --subject x`.'],
  ['f.md', 'Merge it by hand, the train is\ndown, with `gh pr merge 9 --subject x`.'],
  ['f.md', '1) gh pr merge 9 --subject x'], ['f.md', 'a) run `gh pr merge 9 --subject x`'], ['f.md', '- step 2) `gh pr merge 9 -t x`'],
  ['f.md', ':) gh pr merge 9 --subject x'], ['f.md', '(see above) gh pr merge 9 --subject x'],
  ['f.mjs', 'foo(() => {\n  a()\n}); execSync("gh pr merge 9 --subject x")'], ['f.mjs', '}) ; execSync("gh pr merge 9 --subject x")'],
  ['f.py', 'x = [\n 1,\n]; os.system("gh pr merge 9 --subject x")'], ['f.py', 'x = (1\n); os.system("gh pr merge 9 -t x")'],
  ['f.sh', 'x=(\n a\n); gh pr merge 9 --subject x'], ['f.sh', 'echo "a)" ; gh pr merge 9 --subject x'], ['f.sh', "echo 'b)' ; gh pr merge 9 -t x"],
  ['f.sh', '# step 1) then\ngh pr merge 9 --subject x'],
]
const rleads = ['never) ', '(never) ', 'a|b) ', '*) ', '[0-9]*) ', '( cd x ) && ', 'r=$(cat f) && ', '[[ -n "$x" ]] && ', '{ true; } && ',
  'a=(1 2); ', 'done; ', 'if (( n > 0 )); then ', 'echo ")"; ', 'i=$((i+1)); ', 'esac; ', 'm() { ', 'f() { :; }; ', '', '    ']
for (const l of rleads) for (const s of ['gh pr merge "$n" --squash --subject "x"', 'gh pr merge 9 -t s', 'gh pr merge 9 --body b'])
  for (const f of ['f.sh', 'f.md']) for (const tail of [' ;;', '']) plants.push([f, 'case $m in\n' + l + s + tail + '\nesac'])
for (const [f, t] of plants) run('plants', f, t)
// 3. The generated class: a closer in the lead that no opener on the line
// matches, with the text before the line that opened it, if any.
const leads = [
  ['', '1) '], ['', 'a) '], ['', '- step 2) '], ['', ':) '], ['', 'x) '], ['', 'never) '], ['', 'a|b) '], ['', '*) '], ['', '[0-9]*) '],
  ['', ') '], ['', '] '], ['', '} '], ['', '}) ; '], ['', '); '], ['', ']; '], ['', 'see 2), then '], ['', 'a) b) '],
  ['Merge it by hand (the train is\n', 'down) with '], ['See [the note\n', 'below] and run '], ['x=(\n a\n', '); '],
  ['foo(() => {\n  a()\n', '}); '], ['x = [\n 1,\n', ']; '], ['case $m in\n', 'never) '], ['case $m in\n', '*) '], ['case $m in\n', '[0-9]*) '],
]
const writers = [
  ['gh pr merge 9 --subject x', 'gh pr merge 9'], ['gh pr merge "$n" --squash --subject "x"', 'gh pr merge "$n" --squash'],
  ['gh pr merge 9 -t s', 'gh pr merge 9 -m'], ['gh pr merge 9 --body b', 'gh pr merge 9 --auto'],
  ['`gh pr merge 9 --subject x`', '`gh pr merge 9`'], ['execSync("gh pr merge 9 --subject x")', 'execSync("gh pr merge 9")'],
  ['os.system("gh pr merge 9 -t x")', 'os.system("gh pr merge 9")'],
  ['gh api -X PUT repos/o/r/pulls/9/merge -f commit_title=x', 'gh api -X PUT repos/o/r/pulls/9/merge'],
]
const nul = { main: 0, head: 0, n: 0 }
for (const [pre, lead] of leads) for (const [w, z] of writers) for (const tail of ['', ' ;;', '.']) for (const ind of ['', '  ', '\t'])
  for (const f of ['f.sh', 'f.md', 'f.py', 'f.mjs']) {
    run('generated', f, `${pre}${ind}${lead}${w}${tail}\n`)
    const t = `${pre}${ind}${lead}${z}${tail}\n`; nul.n++
    nul.main += main([f], () => t).bad.length > 0; nul.head += head([f], () => t).bad.length > 0
  }
let tot = { lines: 0, main: 0, head: 0, miss: 0 }
for (const [part, p] of Object.entries(parts)) {
  for (const m of p.miss) console.log(`MAIN-NOT-HEAD ${part} ${m}`)
  console.log(`${part} lines=${p.lines} refused_main=${p.main} refused_head=${p.head} main_not_head=${p.miss.length}`)
  tot = { lines: tot.lines + p.lines, main: tot.main + p.main, head: tot.head + p.head, miss: tot.miss + p.miss.length }
}
console.log(`null lines=${nul.n} refused_main=${nul.main} refused_head=${nul.head}`)
console.log(`TOTAL lines=${tot.lines} refused_main=${tot.main} refused_head=${tot.head} main_not_head=${tot.miss}`)
process.exitCode = tot.miss ? 1 : 0
