// Reviewer's own probe (round 4 of #2697): runs the head's subjectWriters, extracted
// as dev/audit/harnesses/r10_merge_subject_argv_seam.mjs does, over spellings.
//   node reviewer_probe.mjs <agreement.mjs>
import fs from 'node:fs'
const src = fs.readFileSync(process.argv[2], 'utf8')
const from = src.indexOf('// WHAT A MERGE CALL IS'); const to = src.indexOf("// WHICH LINE IS MAIN'S")
const block = src.slice(from, to).replace(/^function nonTemplateMerges[\s\S]*?\n}\n/m, '')
const sw = new Function(block + '\nreturn subjectWriters')()
const S = '"Merge pull request #9 (x)"'
const shapes = [
  ['brief: gh "pr" merge', `gh "pr" merge 9 --subject ${S}`],
  ['brief: gh pr "merge"', `gh pr "merge" 9 --subject ${S}`],
  ['brief: gh pr -R o/r merge', `gh pr -R o/r merge 9 --subject ${S}`],
  ['brief: gh --repo o/r pr merge', `gh --repo o/r pr merge 9 --subject ${S}`],
  ['brief: single-quoted argv', `run(['gh', 'pr', 'merge', n, '--subject', s])`],
  ['brief: ws before comma', `run(["gh" , "pr" , "merge" , n, "--subject", s])`],
  ['brief: continuation gh->pr', `gh \\\n  pr merge 9 --subject ${S}`],
  ['new: ${GH:-gh} default expansion', `\${GH:-gh} pr merge 9 --subject ${S}`],
  ['new: $(command -v gh)', `$(command -v gh) pr merge 9 --subject ${S}`],
  ['new: gh.exe', `gh.exe pr merge 9 --subject ${S}`],
  ['new: blank line inside argv list', `run(["gh", "pr", "merge", n,\n\n    "--subject", s])`],
  ['new: subject before the merge word', `gh pr --subject ${S} merge 9`],
  ['new: -R value then cluster -Rmt? (control)', `gh pr merge 9 -R o/r -mt x`],
  ['new: argv "-mt" cluster', `run(["gh", "pr", "merge", n, "-mt", s])`],
  ['new: argv "--subject=" attached', `run(["gh", "pr", "merge", n, f"--subject={s}"])`],
  ['new: python implicit concat', `run(["gh", "pr", "merge", n, "--sub" "ject", s])`],
  ['new: gh api -F commit_title', `gh api -X PUT repos/o/r/pulls/9/merge -F commit_title=x`],
  ['new: GraphQL commitHeadline on next line', `q = """mutation { mergePullRequest(input: {\n  pullRequestId: $id,\n  commitHeadline: "x"}) { clientMutationId } }"""`],
  ['new: tab-indented continuation', `gh pr merge 9 \\\n\t--subject ${S}`],
  ['new: trailing-space continuation (bash: not a continuation)', `gh pr merge 9 \\ \n --subject ${S}`],
]
for (const [n, t] of shapes) { const r = sw(['f'], () => t + '\n'); console.log(`${n}: calls=${r.calls.length} bad=${JSON.stringify(r.bad)}`) }
