// reviewer's own extent-class generator: node probe.mjs <agreement.mjs> ; prints refused(1)/not(0) per probe
import fs from 'node:fs'
const src = fs.readFileSync(process.argv[2], 'utf8')
const block = src.slice(src.indexOf('// WHAT A MERGE CALL IS'), src.indexOf("// WHICH LINE IS MAIN'S")).replace(/^function nonTemplateMerges[\s\S]*?\n}\n/m, '')
const sw = new Function(block + '\nreturn subjectWriters')()
const B = '`'
// [name, expect(1 refuse / 0 null), ext, text]
const P = []
const add = (n, e, x, t) => P.push([n, e, x, t])
// wrap after program/pr/merge, py & js & sh
for (const x of ['py', 'mjs']) {
  const q = x === 'py' ? '"' : "'"
  const run = x === 'py' ? 'subprocess.run(' : "execFileSync("
  add('wrap-after-gh', 1, x, `${run}[${q}gh${q},\n    ${q}pr${q}, ${q}merge${q}, n,\n    ${q}--subject${q}, s])`)
  add('wrap-after-pr', 1, x, `${run}[${q}gh${q}, ${q}pr${q},\n    ${q}merge${q}, n,\n    ${q}--subject${q}, s])`)
  add('wrap-after-merge', 1, x, `${run}[${q}gh${q}, ${q}pr${q}, ${q}merge${q},\n    n,\n    ${q}--subject${q}, s])`)
  add('nested-outer-call', 1, x, `check(${run}\n    [${q}gh${q},\n     ${q}pr${q}, ${q}merge${q}, n,\n     ${q}-t${q}, s]))`)
  add('nested-dict-args', 1, x, `${run}{${q}args${q}: [\n  ${q}gh${q},\n  ${q}pr${q}, ${q}merge${q},\n  ${q}--body${q}, b]})`)
  add('prior-closed-group', 1, x, `x = f(a,\n  b)\n${run}[${q}gh${q},\n  ${q}pr${q}, ${q}merge${q}, n,\n  ${q}--subject${q}, s])`)
  add('prior-unclosed-sibling-null', 0, x, `T = [\n  [${q}gh${q},\n   ${q}pr${q}, ${q}merge${q}, n],\n  [${q}x${q}, ${q}--subject${q}, s],\n]`)
  add('later-stmt-flag-null', 0, x, `${run}[${q}gh${q},\n    ${q}pr${q}, ${q}merge${q}, n])\nother(${q}--subject${q}, s)`)
  add('quote-across-line', 1, x, `${run}[${q}gh${q}, ${q}a(b${q},\n    ${q}pr${q}, ${q}merge${q}, n,\n    ${q}--subject${q}, s])`)
  add('closer-in-string-before-pr', 1, x, `${run}[${q}gh${q}, ${q})${q},\n    ${q}pr${q}, ${q}merge${q}, n,\n    ${q}--subject${q}, s])`)
}
// python comments
add('py-comment-paren-before-pr', 1, 'py', 'subprocess.run(["gh",  # see (x\n    "pr", "merge", n,\n    "--subject", s])')
add('py-comment-closer-before-pr', 1, 'py', 'subprocess.run(["gh",  # :)\n    "pr", "merge", n,\n    "--subject", s])')
add('py-comment-closer-after-merge', 1, 'py', 'subprocess.run(["gh", "pr", "merge", n,  # :)\n    "--subject", s])')
add('py-triple-before', 1, 'py', 'doc = """a (\nb"""\nsubprocess.run(["gh",\n    "pr", "merge", n,\n    "--subject", s])')
add('py-exploded-trailing-comma', 1, 'py', 'run(\n    [\n        "gh",\n        "pr",\n        "merge",\n        str(n),\n        "--subject",\n        s,\n    ],\n    check=True,\n)')
add('py-blank-in-bracket', 1, 'py', 'run([\n    "gh",\n\n    "pr", "merge", n,\n    "--subject", s])')
add('py-blank-after-pr', 1, 'py', 'run(["gh", "pr", "merge", n,\n\n    "--subject", s])')
// js comments
add('js-line-comment-closer', 1, 'mjs', "execFileSync('gh', [ // :)\n  'pr', 'merge', n,\n  '--subject', s])")
add('js-block-comment-closer-before', 1, 'mjs', "execFileSync('gh', [ /* :) */\n  'pr', 'merge', n,\n  '--subject', s])")
add('js-block-comment-closer-after', 1, 'mjs', "execFileSync('gh', ['pr', 'merge', n, /* :) */ '--subject', s])")
add('js-backtick-closer-after', 1, 'mjs', "execFileSync('gh', ['pr', 'merge', n, '--body', `ok :)`, '--subject', s])")
add('js-backtick-closer-before', 1, 'mjs', "execFileSync('gh', [`:)`,\n  'pr', 'merge', n,\n  '--subject', s])")
add('js-backtick-multiline-before', 1, 'mjs', "const m = `a\n(b`\nexecFileSync('gh', [\n  'pr', 'merge', n,\n  '--subject', s])")
add('js-template-program', 1, 'mjs', "execSync(`gh pr merge ${n}\n  --subject ${s}`)")
add('js-regex-closer', 1, 'mjs', "execFileSync('gh', ['pr', 'merge', String(n).replace(/\\)/g, ''), '--subject', s])")
// shell
add('sh-continuation', 1, 'sh', 'gh pr merge "$n" \\\n  --squash \\\n  --subject "$s"')
add('sh-array', 1, 'sh', 'args=(\n  pr merge "$n"\n  --subject "$s"\n)\ngh "${args[@]}"')
add('sh-comment-paren', 1, 'sh', '# (note\ngh pr merge "$n" --subject "$s"')
add('sh-case-paren', 1, 'sh', 'case $x in\n  a) gh pr merge "$n" \\\n     --subject "$s" ;;\nesac')
add('sh-closer-in-dq-after', 1, 'sh', 'gh pr merge "$n" --body ":)" --subject "$s"')
// over-fire nulls
add('null-view-wrapped', 0, 'py', 'subprocess.run(["gh",\n    "pr", "view", n,\n    "--json", "title"])\n')
add('null-sibling-table-later', 0, 'py', 'CMDS = {\n  "m": ["gh",\n        "pr", "merge", n],\n  "e": ["gh", "pr", "edit", n, "--title", t],\n}')
add('null-prose-md', 0, 'md', 'We run `gh pr merge` with no flags.\n\nUse --subject only for edits.')
add('null-earlier-stmt-flag', 0, 'py', 'other("--subject", s)\nsubprocess.run(["gh",\n    "pr", "merge", n])')
add('null-earlier-open-bracket-flag', 0, 'py', 'opts = ["--subject", s,\n  "x"]\nsubprocess.run(["gh",\n    "pr", "merge", n])')
add('null-enclosing-call-earlier-flag', 0, 'py', 'wrap("--subject", s,\n  subprocess.run(["gh",\n    "pr", "merge", n]))')
for (const [n, e, x, t] of P) {
  const r = sw(['f.' + x], () => t).bad.length ? 1 : 0
  console.log(`${r === e ? 'ok  ' : 'MISS'} got=${r} want=${e} ${x} ${n}`)
}
