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
