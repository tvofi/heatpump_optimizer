# Review packet #3840
head: 1788c2e540f65ace3b94e18a1f9fcadd718015e8
base: 4ebd430fbff9a7b19582ca530a817f34abbafa16

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: green
CodeQL id=137024528834 success
arch-score / arch-score id=137027693554 success
arm id=137023157645 skipped
budget-raise-gate / budget-raise-gate id=137027693550 success
cancel-superseded id=137027534603 success
codeql id=137027694459 skipped
codeql / Analyze (actions) id=137024302442 success
codeql / Analyze (javascript-typescript) id=137024302409 success
codeql / Analyze (python) id=137024302425 success
gate id=137046263228 success
governance id=137027695004 skipped
governance / env-matrix id=137024302386 success
governance / instrument-self-tests id=137024302398 success
governance / policy-docs id=137024302416 success
governance / record id=137024304190 skipped
governance / wave-script id=137024302371 success
hassfest id=137027694977 skipped
hassfest / hassfest id=137024302273 success
kernel-points id=137027694894 skipped
pr-contract id=137028037788 skipped
pr-contract / pr-contract id=137040095474 success
prelude id=137027534412 success
refresh id=137027534676 success
sweep-self id=137046507370 skipped
tests id=137027694330 skipped
tests / arch-instrument id=137025335068 success
tests / briefs id=137024302495 success
tests / browser id=137025335051 success
tests / ci-ratchet id=137037379960 skipped
tests / claims-autofix id=137028657199 skipped
tests / closure-scope id=137024302452 success
tests / closures id=137025335094 success
tests / closures-autofix id=137029028307 skipped
tests / coverage id=137025335029 success
tests / coverage-ratchet id=137037379028 success
tests / fast (3.14) id=137025335098 success
tests / graders-head-copy id=137037379058 success
tests / lane-proofs id=137037378996 success
tests / mutation id=137024302399 success
tests / mutation-autofix id=137024644767 skipped
tests / mutation-pins id=137024644322 skipped
tests / nightly-ha id=137025336231 skipped
tests / nightly-status id=137024302449 success
tests / replay id=137025336100 skipped
tests / typing id=137025335003 success
validate id=137027694926 skipped
validate / validate-hacs id=137024302287 success

## Refusals
none

## Advisories
none

## carry_audit at the head
NOTE body item 8e158ef6: dismissed:owned by the orchestrator's parallel root-cause seat for this hotfix, not this fix's seam.
CARRY-AUDIT: 1 finding item(s): 1 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
unverified - `brief_lint.mjs` `treeListing` (ls-tree / ls-files)
             no segment of this names a program this check knows
  unverified - `refFiles` (ls-tree at a cited tag, `allowFail`)
             no segment of this names a program this check knows
  unverified - `assertGrepExcludeBounded` (ls-files)
             no segment of this names a program this check knows
  unverified - `agreement.mjs` `governanceCode` and `mergeSubjectGuard`'s `tools .claude/workflows` listing
             no segment of this names a program this check knows
  unverified - `counts.mjs` `lsFiles` and its three `derivations` reads, now `gitRead`
             no segment of this names a program this check knows
  unverified - `policy_lint.mjs`'s `git` helper: `refFiles`, the tracked-files loop and `_printerSource`
             no segment of this names a program this check knows
  unverified - `tests/card.mjs`, a stubbed `runGit` that spawns nothing
             no segment of this names a program this check knows
  unverified - `tests/card_rig.mjs` `threeDotFiles`, untracked files and a diff, through an injected `runGit`
             no segment of this names a program this check knows
  ok         python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"
             `tests/closure.py` is in the tree at this head
  ok         tests/entities.py
             `tests/entities.py` is in the tree at this head
  unverified git ls-tree -r --name-only <rev> | wc -c
             `git ls-tree` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  unverified git grep -nE "['\"](ls-files|ls-tree)['\"]" -- 'tools/*.mjs' 'tools/*.js' 'tools/*.cjs' 'tests/*.mjs' 'tests/*.js' 'tests/*.cjs' '.claude/*.mjs' '.claude/*.js'
             `git grep` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  unverified git
             `git` with no subcommand word to resolve
  ok         tests/card.mjs
             `tests/card.mjs` is in the tree at this head
  ok         tests/card_rig.mjs
             `tests/card_rig.mjs` is in the tree at this head
  unverified git grep -I -l
             `git grep` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  unverified gh
             `gh` with no subcommand word to resolve
  unverified git show
             `git show` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  ok         python3 tests/structure.py
             `tests/structure.py` is in the tree at this head
  ok         python3 -I tools/policy/agreement_py.py --out $J && node tools/policy/agreement.mjs --py-json $J
             `tools/policy/agreement_py.py` is in the tree at this head
  ok         python3 -I tools/policy/agreement_py.py --out $J && node tools/policy/agreement.mjs --py-json $J
             `tools/policy/agreement.mjs` is in the tree at this head
  ok         node tools/policy/agreement.mjs --self-test
             `tools/policy/agreement.mjs` is in the tree at this head
  ok         PREPR_SKIP_CODE=1 PREPR_SKIP_CLOSURES=1 bash tools/pr/prepr.sh <body>
             `tools/pr/prepr.sh` is in the tree at this head

FIGURES: 9 resolved, 14 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
none

## Review scope: full (first round: no --reviewed-head)

## Three-dot diff
diff --git a/dev/programme/delivery/3840.md b/dev/programme/delivery/3840.md
new file mode 100644
index 0000000000..8b3d0b1ee4
--- /dev/null
+++ b/dev/programme/delivery/3840.md
@@ -0,0 +1 @@
+- [#3840](https://github.com/tvofi/heatpump_optimizer/pull/3840) — **open**, fix(policy): one gitRead with a 64 MiB maxBuffer for tree-sized git reads (HOTFIX-BRIEF-LINT-MAXBUFFER)
diff --git a/tools/policy/agreement.mjs b/tools/policy/agreement.mjs
index ce9c6225f5..7d3b6a0de0 100644
--- a/tools/policy/agreement.mjs
+++ b/tools/policy/agreement.mjs
@@ -35,12 +35,12 @@ import os from 'node:os'
 import path from 'node:path'
 import { fileURLToPath, pathToFileURL } from 'node:url'
 import { execFileSync } from 'node:child_process'
-import { at, canon, canonList, lsFiles } from './counts.mjs'
+import { at, canon, canonList, gitRead, lsFiles } from './counts.mjs'
 
 const HERE = path.dirname(fileURLToPath(import.meta.url))
 const ROOT = path.resolve(HERE, '..', '..')
 const rd = (rel) => fs.readFileSync(at(rel), 'utf8')
-const git = (args) => execFileSync('git', args, { cwd: ROOT, encoding: 'utf8' })
+const git = (args) => gitRead(args)
 
 // A definition that lives in a script with no exports is read from its source
 // text, as policy_lint.mjs reads web-fix-wave.js's VERDICT_RE: the reader
diff --git a/tools/policy/brief_lint.mjs b/tools/policy/brief_lint.mjs
index dc76b83ea0..dc9b234e8e 100644
--- a/tools/policy/brief_lint.mjs
+++ b/tools/policy/brief_lint.mjs
@@ -59,7 +59,7 @@ import os from 'node:os'
 import path from 'node:path'
 import { fileURLToPath } from 'node:url'
 import { execFileSync } from 'node:child_process'
-import { COUNT_RULES, checkCounts, derivations, canonList, excludeMoved, listDir, at, locate } from './counts.mjs'
+import { COUNT_RULES, checkCounts, derivations, canonList, excludeMoved, listDir, at, locate, gitRead } from './counts.mjs'
 
 const HERE = path.dirname(fileURLToPath(import.meta.url))
 export const ROOT = path.resolve(HERE, '..', '..')
@@ -73,7 +73,7 @@ const EXT_SET = new Set(CODE_EXTS)
 
 export function git(args, opts = {}) {
   try {
-    return execFileSync('git', args, { cwd: ROOT, encoding: 'utf8', stdio: ['ignore', 'pipe', 'pipe'], ...opts })
+    return gitRead(args, { stdio: ['ignore', 'pipe', 'pipe'], ...opts })
   } catch (e) {
     if (opts.allowFail) return null
     throw e
@@ -113,7 +113,7 @@ let _trackedFiles = null
 // paths against the wrong tree.
 export function treeListing(rev, cwd = ROOT) {
   const args = rev ? ['ls-tree', '-r', '--name-only', rev] : ['ls-files']
-  return execFileSync('git', args, { cwd, encoding: 'utf8', stdio: ['ignore', 'pipe', 'pipe'] })
+  return gitRead(args, { cwd, stdio: ['ignore', 'pipe', 'pipe'] })
 }
 
 // `cwd` is the acceptance probe's repo; it is never memoized, so the checkout's cache is untouched.
@@ -1539,6 +1539,33 @@ function assertLegacyListedClean() {
   return 0
 }
 
+// Node's default execFileSync maxBuffer (1 MiB) killed treeListing with ENOBUFS
+// once the repository's own listing crossed it. The index of the probe repo is
+// filled by plumbing with paths whose listing exceeds that default, in both the
+// checkout (ls-files) and the rev (ls-tree) form; the precondition is asserted,
+// so a probe that shrank under the default would refuse rather than pass.
+const NODE_DEFAULT_MAX_BUFFER = 1024 * 1024
+function treeListingOverDefaultBuffer(g, dir) {
+  const problems = []
+  const blob = execFileSync('git', ['hash-object', '-w', '--stdin'], { cwd: dir, input: 'x', encoding: 'utf8' }).trim()
+  const names = []
+  for (let bytes = 0; bytes <= NODE_DEFAULT_MAX_BUFFER + 4096;) {
+    names.push(`big/${String(names.length).padStart(6, '0')}-${'p'.repeat(200)}.txt`)
+    bytes += names.at(-1).length + 1
+  }
+  execFileSync('git', ['update-index', '--add', '--index-info'], { cwd: dir, input: names.map((n) => `100644 ${blob}\t${n}\n`).join('') })
+  const tree = g('write-tree').trim()
+  const rev = g('commit-tree', tree, '-m', 'big').trim()
+  for (const [form, arg] of [['rev', rev], ['checkout', undefined]]) {
+    let out
+    try { out = treeListing(arg, dir) } catch (e) { problems.push(`the ${form} listing over the default maxBuffer threw (${e.code || e.message})`); continue }
+    if (out.length <= NODE_DEFAULT_MAX_BUFFER) problems.push(`the ${form} probe listing is ${out.length} bytes, not over the ${NODE_DEFAULT_MAX_BUFFER}-byte default: vacuous`)
+    const big = out.split('\n').filter((n) => n.startsWith('big/')).length
+    if (big !== names.length) problems.push(`the ${form} listing carried ${big} of ${names.length} probe paths`)
+  }
+  return problems
+}
+
 // treeListing acceptance: a throwaway repo whose second commit adds b.txt and
 // deletes a.txt. The head listing must show the add and not the delete, the
 // first commit's the reverse (null control), the checkout form follows the
@@ -1578,6 +1605,7 @@ function assertTreeRev() {
     let threw = false
     try { treeListing('no-such-rev-probe', dir) } catch { threw = true }
     if (!threw) problems.push('an unresolvable rev did not throw; it fell back silently')
+    problems.push(...treeListingOverDefaultBuffer(g, dir))
   } catch (e) {
     problems.push(`probe repo failed: ${e.message}`)
   } finally {
diff --git a/tools/policy/counts.mjs b/tools/policy/counts.mjs
index dc93b04eee..7fe6b6558b 100644
--- a/tools/policy/counts.mjs
+++ b/tools/policy/counts.mjs
@@ -93,9 +93,14 @@ function read(rel) {
   }
 }
 
-function git(args) {
-  return execFileSync('git', args, { cwd: ROOT, encoding: 'utf8', maxBuffer: 64 * 1024 * 1024 })
+// Every git read that can return a tree-sized listing goes through here: Node's
+// default execFileSync maxBuffer (1 MiB) is below the repository's own
+// `git ls-files` output, and over it the call dies with ENOBUFS.
+export const GIT_MAX_BUFFER = 64 * 1024 * 1024
+export function gitRead(args, opts = {}) {
+  return execFileSync('git', args, { cwd: ROOT, encoding: 'utf8', maxBuffer: GIT_MAX_BUFFER, ...opts })
 }
+const git = (args) => gitRead(args)
 
 // ---------------------------------------------------------------------------
 // Derivations. Every count a policy file is allowed to state is computed here

## Before you return the verdict (P275)
Run `python3 -I tools/audit/carry_audit.py check --body <PR body file> --comments <file holding [{"id": 0, "body": <verdict.md text>}]>`. Give every reported item its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>`;
an evidence line flagged by its wording takes `Carry: dismissed: evidence, not a finding`. Return the verdict only at rc 0.
