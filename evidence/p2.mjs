import fs from 'node:fs'
const src = fs.readFileSync(process.argv[2], 'utf8')
const block = src.slice(src.indexOf('const MERGE_CALL'), src.indexOf("// WHICH LINE IS MAIN'S")).replace(/^function nonTemplateMerges[\s\S]*?\n}\n/m, '')
const sw = new Function(block + '\nreturn subjectWriters')()
const t = 'gh \\\n  pr merge 9 --merge --subject "Merge pull request #9 (x)"'
console.log(JSON.stringify(t), JSON.stringify(sw(['f'], () => t)))
