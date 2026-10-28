import fs from 'node:fs'
const src = fs.readFileSync(process.argv[2], 'utf8')
const from = src.indexOf('const MERGE_CALL'); const to = src.indexOf("// WHICH LINE IS MAIN'S")
const block = src.slice(from, to).replace(/^function nonTemplateMerges[\s\S]*?\n}\n/m, '')
const sw = new Function(block + '\nreturn subjectWriters')()
const S = 'Merge pull request #9 (x)'
const shapes = {
  base: `gh pr merge 9 --merge --subject "${S}"`,
  cont_nospace: `gh pr\\\nmerge 9 --merge --subject "${S}"`,
  cont_three: `gh \\\n  pr \\\n  merge 9 \\\n  --merge \\\n  --subject "${S}"`,
  dq_merge: `gh pr "merge" 9 --merge --subject "${S}"`,
  sq_merge: `gh pr 'merge' 9 --merge --subject "${S}"`,
  dq_pr: `gh "pr" merge 9 --merge --subject "${S}"`,
  repo_flag_between: `gh pr -R o/r merge 9 --merge --subject "${S}"`,
  repo_flag_root: `gh --repo o/r pr merge 9 --merge --subject "${S}"`,
  var_gh: `GH=gh; $GH pr merge 9 --merge --subject "${S}"`,
  abs_gh: `/usr/bin/gh pr merge 9 --merge --subject "${S}"`,
  subshell: `out=$(gh pr merge 9 --merge --subject "${S}")`,
  subj_eq: `gh pr merge 9 --merge --subject="${S}"`,
  subj_t: `gh pr merge 9 --merge -t "${S}"`,
  py_sq_argv: `run(['gh', 'pr', 'merge', n, '--subject', s])`,
  py_sq_split: `run(['gh', 'pr',\n     'merge', n, '--subject', s])`,
  py_ws_comma: `run(["gh", "pr" , "merge", n, "--subject", s])`,
  py_split_list: `run(["gh", "pr", "merge", n,\n     "--subject", s])`,
  py_shlex: `run(shlex.split("gh pr merge %s --subject x" % n))`,
  cont_after_flag_value: `gh pr merge 9 --merge \\\n  --body-file f \\\n  --subject "${S}"`,
  cont_comment_line: `gh pr merge 9 --merge \\\n  # note\n  --subject x`,
  heredoc_null: `gh pr merge 9 --merge\necho --subject`,
  crlf_cont: `gh pr merge 9 --merge \\\r\n  --subject "${S}"`,
}
for (const [k, t] of Object.entries(shapes)) { const r = sw(['f'], () => t); console.log(k.padEnd(22), 'calls', r.calls.length, 'bad', JSON.stringify(r.bad)) }
