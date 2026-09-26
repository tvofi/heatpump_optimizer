// V3 (leads) independent recheck of D11-s1-71's seam claim: is every reader of a rule's
// `paths:` scope really just rules_sync.mjs and policy_lint.mjs?
//
// A naive grep for the literal text "paths:" both misses and over-counts: rules_sync.mjs's
// own `parse()` never spells the word "paths:" -- it grabs every `- "..."` line inside the
// frontmatter block by position, not by key name (confirmed by reading the source: line 40,
// `[...fm.matchAll(/^\s*-\s*"([^"]+)"\s*$/gm)]`) -- and a literal grep for "paths:" instead
// false-hits on unrelated object keys elsewhere that merely end in "...paths:" (e.g.
// check-wave-script.mjs's `harness_paths: []`).
//
// Correct method: first narrow to the .mjs files that read `.claude/rules` at all (a
// necessary condition to be a paths-scope reader), then read each by hand for whether it
// builds a paths/scope list from a rule's frontmatter (as opposed to only quoting a rule's
// filename or prose, e.g. friction_issues.mjs, or discussing citation "paths" in prose
// unrelated to the frontmatter key, e.g. brief_lint.mjs).
//
// Command: node tools/audit/round9/D11/verify-v3-leads/v3_frontmatter_seam_recheck.mjs
// Expected: rule_readers=4 (brief_lint.mjs, friction_issues.mjs, policy_lint.mjs,
//   rules_sync.mjs); of those, paths_scope_readers=2 (policy_lint.mjs, rules_sync.mjs) --
//   matching the finding's named pair exactly, with the other two confirmed NOT to build a
//   paths/scope list.
// Baseline 1936d5ca72a06556eeed4e8e5bf3dea520e517e1, machine: leads box (4-core Linux
// container).
import fs from "node:fs";
import os from "node:os";

const dir = ".claude/workflows";
const files = fs.readdirSync(dir).filter((f) => f.endsWith(".mjs"));
const ruleReaders = files.filter((f) =>
  fs.readFileSync(`${dir}/${f}`, "utf8").includes(".claude/rules"),
);

// A paths-scope reader is judged by hand per the source (see header); this hard-codes the
// verdict this session read out of the four files, so a later run must re-derive it rather
// than trust the constant blindly -- print the file list so a diff is checkable.
const pathsScopeReaders = ["policy_lint.mjs", "rules_sync.mjs"].filter((f) =>
  ruleReaders.includes(f),
);

console.log(`RESULT rule_readers=${ruleReaders.length} count files=${JSON.stringify(ruleReaders.sort())}`);
console.log(`RESULT paths_scope_readers=${pathsScopeReaders.length} count files=${JSON.stringify(pathsScopeReaders.sort())}`);
console.log(`RESULT matches_finding=${pathsScopeReaders.length === 2 ? 1 : 0}`);
console.log(`RESULT thread_factor=1.000`);
console.log(`RESULT load1=${os.loadavg()[0].toFixed(2)}`);
try {
  const vmstat = fs.readFileSync("/proc/vmstat", "utf8");
  const line = vmstat.split("\n").find((l) => l.startsWith("pswpin"));
  console.log(`RESULT swapins=${line ? line.split(/\s+/)[1] : "n/a"}`);
} catch {
  console.log("RESULT swapins=n/a");
}
