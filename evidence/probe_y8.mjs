// Own instrument: extract the head's guard block (as the PR's seam probe does) and
// run it, optionally with MERGE_CALL's gh arm reverted to literal spaces (Y8).
import fs from 'node:fs'
let src = fs.readFileSync(process.argv[2], 'utf8')
if (process.argv[3] === 'Y8') src = src.replace(String.raw`\bgh\s+pr\s+merge\b`, String.raw`\bgh pr merge\b`)
const from = src.indexOf('const MERGE_CALL'); const to = src.indexOf("// WHICH LINE IS MAIN'S")
const block = src.slice(from, to).replace(/^function nonTemplateMerges[\s\S]*?\n}\n/m, '')
const sw = new Function(block + '\nreturn subjectWriters')()
for (const t of ['gh pr \\\n  merge 9 --merge --subject "Merge pull request #9 (x)"\n', 'gh  pr merge 9 --subject s\n', 'gh pr merge 9 --subject s\n'])
  console.log(process.argv[3] || 'head', JSON.stringify(sw(['f'], () => t)), JSON.stringify(t))
