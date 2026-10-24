// R10-MERGE-SUBJECT-HARDEN (#2697): the dismissed open seam of the merge-subject
// writer scan. `subjectWriters` reads a merge call's own bracket group
// (`callExtent`), so a subject flag outside that group -- an argv list built
// across expressions -- is not read. A lexical scan cannot follow that; merges
// go only through tools/audit/seat/merge_pr.sh and merge_train.py, which pass
// no --subject. This prints what the guard refuses for each probe shape.
//   node dev/audit/harnesses/r10_merge_subject_argv_seam.mjs [tools/policy/agreement.mjs]
// Expected at the fix head: [] [] ["f:1"] -- the first two are the seam, the
// third is the control (a flag inside the argv list is refused).
import fs from 'node:fs'
const src = fs.readFileSync(process.argv[2] || 'tools/policy/agreement.mjs', 'utf8')
const from = src.indexOf('// WHAT A MERGE CALL IS'); const to = src.indexOf("// WHICH LINE IS MAIN'S")
if (from < 0 || to < 0) { console.error('seam probe: guard block not found'); process.exit(2) }
const block = src.slice(from, to).replace(/^function nonTemplateMerges[\s\S]*?\n}\n/m, '')
const subjectWriters = new Function(block + '\nreturn subjectWriters')()
const shapes = [
  'run(["gh", "pr", "merge", n] + ["--subject", s])',
  'args = ["gh", "pr", "merge", n]\nargs += ["--subject", s]\nrun(args)',
  'run(["gh", "pr", "merge", n, "--subject", s])',
]
for (const t of shapes) console.log(JSON.stringify(subjectWriters(['f'], () => t).bad), JSON.stringify(t))
