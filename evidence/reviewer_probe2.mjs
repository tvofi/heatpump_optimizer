// Reviewer's own probe, part 2 (round 4 of #2697): option values with spaces and
// multi-line GraphQL merges. node reviewer_probe2.mjs <agreement.mjs>
import fs from 'node:fs'
const src = fs.readFileSync(process.argv[2], 'utf8')
const from = src.indexOf('// WHAT A MERGE CALL IS'); const to = src.indexOf("// WHICH LINE IS MAIN'S")
const block = src.slice(from, to).replace(/^function nonTemplateMerges[\s\S]*?\n}\n/m, '')
const sw = new Function(block + '\nreturn subjectWriters')()
const shapes = [
  ['gh pr --subject "x y" merge (gh 2.89 parses)', 'gh pr --subject "x y" merge 9 --merge'],
  ['gh pr -t "x y" merge (gh 2.89 parses)', 'gh pr -t "x y" merge 9 --merge'],
  ['gh pr --subject x merge (one-word value, control)', 'gh pr --subject x merge 9 --merge'],
  ['argv: "pr", "--subject", "x y", "merge"', 'run(["gh", "pr", "--subject", "x y", "merge", n])'],
  ['argv: "pr", "--subject", s, "merge"', 'run(["gh", "pr", "--subject", s, "merge", n])'],
  ['gh -R "o r" pr merge (spaced value before pr)', 'gh -R "o/r x" pr merge 9 --subject x'],
  ['graphql: shell multi-line query', "gh api graphql -f query='\nmutation {\n  mergePullRequest(input: {\n    pullRequestId: \"$ID\"\n    commitHeadline: \"x\"\n  }) { clientMutationId }\n}'"],
  ['graphql: python triple-quoted multi-line', 'Q = """\nmutation($id: ID!) {\n  mergePullRequest(input: {pullRequestId: $id,\n    commitHeadline: "x"}) { clientMutationId }\n}"""'],
  ['graphql: python triple-quoted, one line opener', 'Q = """mutation { mergePullRequest(input: {\n  pullRequestId: $id,\n  commitHeadline: "x"}) { clientMutationId } }"""'],
  ['graphql: JS template multi-line', 'const q = `\nmutation {\n  mergePullRequest(input: {\n    pullRequestId: id,\n    commitHeadline: "x"\n  }) { clientMutationId }\n}`'],
]
for (const [n, t] of shapes) { const r = sw(['f'], () => t + '\n'); console.log(`${n}: calls=${r.calls.length} bad=${JSON.stringify(r.bad)}`) }
