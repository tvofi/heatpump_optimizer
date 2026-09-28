import json
p='.claude/workflows/policy_lint.mjs'; s=open(p).read()
i=s.index('function rulePaths(rel) {'); j=s.index('\n}\n',i)+3
s=s[:i]+"function rulePaths(rel) {\n  return frontmatterPaths(read(rel))\n}\n"+s[j:]
a="import { checkCounts, derivations,"
s=s.replace(a,"import { frontmatterPaths } from './rule_frontmatter.mjs'\n"+a,1)
# merge subject: both shapes, as stamp.py reads them
s=s.replace("const MERGE_SUBJECT_RE = /\\(#(\\d+)\\)\\s*$/","const MERGE_SUBJECT_RE = /^Merge pull request #(\\d+)\\b|\\(#(\\d+)\\)\\s*$/")
s=s.replace("""    const m = s.match(MERGE_SUBJECT_RE)
    if (!m || seen.has(m[1])) continue
    seen.add(m[1])
    rows.push({ pr: m[1], subject: s })""","""    const m = s.match(MERGE_SUBJECT_RE)
    const n = m && (m[1] || m[2])
    if (!n || seen.has(n)) continue
    seen.add(n)
    rows.push({ pr: n, subject: s })""")
open(p,'w').write(s)
p='.claude/workflows/rules_sync.mjs'; s=open(p).read()
s=s.replace("import { fileURLToPath } from 'node:url'\n","import { fileURLToPath } from 'node:url'\nimport { frontmatterPaths } from './rule_frontmatter.mjs'\n")
s=s.replace("function parse(text, rel) {","export function parse(text, rel) {")
s=s.replace("""  const paths = [...fm.matchAll(/^\\s*-\\s*"([^"]+)"\\s*$/gm)].map((x) => x[1])""","""  const paths = frontmatterPaths(text) || []""")
i=s.index("const check = process.argv.includes('--check')")
s=s[:i]+"if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {\n"+s[i:]+"}\n"
open(p,'w').write(s)
p='.claude/workflows/audit-find.js'; s=open(p).read()
ids=[k for k in json.load(open('tools/audit/bugclasses.json')) if not k.startswith('_')]
old="const CLASS_GUESS = /^([PI][0-9]+|new)$/"
assert old in s
s=s.replace(old,"const CLASS_GUESS = /^("+"|".join(ids+['new'])+")$/")
open(p,'w').write(s)
# agreement: rules_sync reader imports when parse is exported; registry drops the now-single grammar
p='.claude/workflows/agreement.mjs'; s=open(p).read()
a="      const parse = fnFromSource('.claude/workflows/rules_sync.mjs', 'parse')"
b="""      const rsSrc = rd('.claude/workflows/rules_sync.mjs')
      const parse = /\\nexport function parse\\(/.test(rsSrc) && /import\\.meta\\.url\\)\\) \\{/.test(rsSrc)
        ? (await import(pathToFileURL(path.join(HERE, 'rules_sync.mjs')).href)).parse
        : fnFromSource('.claude/workflows/rules_sync.mjs', 'parse')"""
assert a in s; s=s.replace(a,b)
open(p,'w').write(s)
