import fs from 'fs'
const src = fs.readFileSync(process.argv[2], 'utf8')
const grab = (re) => src.match(re)[0]
const code = [grab(/const MERGE_CALL = .*\n/), grab(/const SUBJECT_ARG = .*\n/),
  grab(/\nfunction quoted[\s\S]*?\n}\n/), grab(/\nfunction callExtent[\s\S]*?\n}\n/), grab(/\nfunction subjectWriters[\s\S]*?\n}\n/),
  'return subjectWriters'].join('\n')
const sw = new Function(code)()
const cases = {
  'closed paren before call on same line, --subject after': '(cd repo) && gh pr merge 9 --merge --subject "Merge pull request #9 (x)"\n',
  'closed bracket before argv': 'x = [1]; run(["gh", "pr", "merge", n, "--subject", s])\n',
  'unclosed apostrophe in shell comment then continuation': 'gh pr merge 9 --merge \\\n  --match-head-commit h  # don\'t\n echo ")"\n  --subject s\n',
  'argv continuation, apostrophe in comment then next statement subject': 'run(["gh", "pr", "merge", n,  # it\'s\n     "--merge"])\nother(["--subject", s])\n',
}
for (const [k, v] of Object.entries(cases)) console.log(JSON.stringify(sw(['f'], () => v).bad), '<-', k)
