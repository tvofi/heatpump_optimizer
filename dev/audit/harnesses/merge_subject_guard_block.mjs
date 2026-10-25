// The merge-subject guard's block cut out of a tools/policy/agreement.mjs source,
// for the instruments that evaluate one guard against another (the R10-MERGE-SUBJECT-HARDEN
// harnesses and R10-RCA-MERGE-SUBJECT-CLASS-OPEN's differential). One cut, one owner.
// The block opens at `// WHAT A MERGE CALL IS`, or, in a guard from before the extent
// reader, at its subject-flag comment, and ends at `// WHICH LINE IS MAIN'S`.
// nonTemplateMerges reads constants defined later in the file, so it is cut out.
// Returns null when either end is missing.
export const guardBlock = (src) => {
  const h = src.indexOf('// WHAT A MERGE CALL IS'); const from = h < 0 ? src.indexOf('// What a merge call may not carry') : h
  const to = src.indexOf("// WHICH LINE IS MAIN'S")
  if (from < 0 || to < 0) return null
  return src.slice(from, to).replace(/^function nonTemplateMerges[\s\S]*?\n}\n/m, '')
}
// The block evaluated, returning what `names` lists (a JS expression over the block's bindings).
export const guardEval = (src, names, who) => {
  const block = guardBlock(src)
  if (block === null) { console.error(`${who}: guard block not found`); process.exit(2) }
  return new Function(block + `\nreturn ${names}`)()
}
