# Review packet #3168
head: e088994a83cb40aff41ae2cd2ec8b05d955af771
base: 8f286293be2d03817a2de23a3a0c884ec2e94fab

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: pending
CodeQL id=125162764970 neutral
arch-score / arch-score id=125162555083 success
arm id=125162372444 skipped
budget-raise-gate / budget-raise-gate id=125162555142 success
cancel-superseded id=125162379047 success
codeql / Analyze (actions) id=125162555105 success
codeql / Analyze (javascript-typescript) id=125162554977 success
codeql / Analyze (python) id=125162555107 in_progress
governance / delivery-status id=125162555182 success
governance / delivery-status-publish id=125162557431 skipped
governance / env-matrix id=125162555032 in_progress
governance / instrument-self-tests id=125162554957 in_progress
governance / policy-docs id=125162554903 in_progress
governance / record id=125162557717 skipped
governance / wave-script id=125162555026 success
hassfest / hassfest id=125162554861 success
kernel-points id=125162556970 skipped
prelude id=125162379462 success
refresh id=125162379626 success
tests / arch-instrument id=125162722726 success
tests / briefs id=125162555361 success
tests / browser id=125162722836 in_progress
tests / closure-scope id=125162555254 success
tests / closures id=125162722792 in_progress
tests / coverage id=125162722852 in_progress
tests / fast (3.14) id=125162722824 in_progress
tests / mutation id=125162555144 success
tests / mutation-autofix id=125162764853 skipped
tests / mutation-pins id=125162763858 skipped
tests / nightly-ha id=125162725013 skipped
tests / nightly-status id=125162555216 success
tests / replay id=125162724876 skipped
tests / typing id=125162722795 success
validate / validate-hacs id=125162555074 success

## Refusals
none

## Advisories
none

## carry_audit at the head
NOTE body item c74eab4d: dismissed:built in this diff, nothing left.
NOTE body item 8d35a6cf: R10-BASH-KILL-HOOK
NOTE body item 4b604006: R10-BASH-KILL-HOOK
CARRY-AUDIT: 3 finding item(s): 3 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
ok         node tools/policy/policy_lint.mjs --hooks
             `tools/policy/policy_lint.mjs` is in the tree at this head
  ok         python3 tools/audit/carry_audit.py check --body <this body>
             `tools/audit/carry_audit.py` is in the tree at this head
  unverified git show origin/main:tools/policy/policy_lint.mjs
             `git show` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals

FIGURES: 2 resolved, 1 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
none

## Three-dot diff
diff --git a/dev/programme/delivery/3168.md b/dev/programme/delivery/3168.md
new file mode 100644
index 000000000..aa84e3e77
--- /dev/null
+++ b/dev/programme/delivery/3168.md
@@ -0,0 +1 @@
+- [#3168](https://github.com/tvofi/heatpump_optimizer/pull/3168) — **open**, R10-BASH-KILL-HOOK: bash kill hook p1 (graders learn the hook) (R10-BASH-KILL-HOOK)
diff --git a/tools/policy/field_coverage.mjs b/tools/policy/field_coverage.mjs
index 071f4855d..ad71bd25d 100644
--- a/tools/policy/field_coverage.mjs
+++ b/tools/policy/field_coverage.mjs
@@ -113,14 +113,6 @@ const HOOKS = {
     'permissions': 'tool permissions are not a hook; --hooks judges hooks and nothing else reads this key',
     'attribution': "the harness's commit and PR attribution text, not a hook (R10-FLY-NO-FOOTERS); --hooks judges hooks. What it hides is refused downstream whatever this key holds: ref_privacy.py's push guard and policy_lint.mjs's body contract",
   },
-  // PENDING: an IGNORE for a key a later pull request adds. Unmatched it is
-  // printed, not DEAD; matched it clears the field like an IGNORE. Decision 0013's
-  // tolerant form: this lands first so the pinned grader never reads the key BLIND.
-  // The follow-up (R10-FLY-NO-FOOTERS, #2636 or a one-line change after it merges)
-  // moves the entry into `ignore`, where an absent key is DEAD again.
-  pending: {
-    'attribution': "the harness's commit and PR attribution text, not a hook (R10-FLY-NO-FOOTERS); --hooks judges hooks. What it hides is refused downstream whatever this key holds: ref_privacy.py's push guard and policy_lint.mjs's body contract",
-  },
   async verdict(obj) {
     const tmp = fs.mkdtempSync(path.join(os.tmpdir(), 'fc-hooks-'))
     const f = path.join(tmp, 'settings.json')
diff --git a/tools/policy/policy_lint.mjs b/tools/policy/policy_lint.mjs
index f8f98b627..a9f61cffe 100644
--- a/tools/policy/policy_lint.mjs
+++ b/tools/policy/policy_lint.mjs
@@ -7086,24 +7086,17 @@ function cmdHooks(settingsPath) {
   // the three events. Both are checked against the actual tool contract, not
   // against this file's own fixture, so a wrong value in either field is
   // caught the same way a missing script is.
+  // The tools a PreToolUse hook script exists to judge, keyed on the SCRIPT: a
+  // matcher is blind when it cannot fire on any tool its own script reads. One
+  // list for every script made `pre-bash.sh` under a `Bash` matcher read as
+  // blind, and passed it wired to the edit tools -- where it never sees a
+  // command. A PreToolUse script not named here is tested against the edit
+  // tools, the contract this check was written for.
   const EDIT_TOOLS = ['Edit', 'Write', 'MultiEdit', 'NotebookEdit']
+  const HOOK_TOOLS = { '.claude/hooks/pre-bash.sh': ['Bash'] }
   const rows = []
   for (const [event, groups] of Object.entries(parsed.hooks || {})) {
     for (const g of groups || []) {
-      if (event === 'PreToolUse') {
-        // A missing matcher, `""` and `"*"` are Claude Code's own "match every
-        // tool" spellings (docs/settings reference), not a pattern to compile
-        // -- feeding `"*"` to `RegExp` throws (an unquantified `*` at the
-        // start), which this used to read as MATCHER BLIND on a group that in
-        // fact fires on every edit. Claude Code itself tests a matcher
-        // unanchored, so this does too rather than requiring a whole-string
-        // match a real config was never written to satisfy.
-        let fires = g.matcher == null || g.matcher === '' || g.matcher === '*'
-        if (!fires) {
-          try { fires = EDIT_TOOLS.some((t) => new RegExp(g.matcher).test(t)) } catch { fires = false }
-        }
-        if (!fires) rows.push({ event, script: '(matcher)', verdict: 'MATCHER BLIND', why: `matcher ${JSON.stringify(g.matcher)} cannot fire on Edit, Write, MultiEdit or NotebookEdit, so no hook in this group ever sees an edit` })
-      }
       for (const h of g.hooks || []) {
         if (h.type !== 'command') { rows.push({ event, script: h.command || '(none)', verdict: 'BAD TYPE', why: `type ${JSON.stringify(h.type ?? null)} is not "command", so this entry never runs` }); continue }
         // The command is a shell line with $CLAUDE_PROJECT_DIR and quoting in
@@ -7112,6 +7105,21 @@ function cmdHooks(settingsPath) {
         const m = String(h.command || '').match(/[.\w/-]*\.claude\/hooks\/[\w.-]+\.sh/)
         if (!m) { rows.push({ event, script: h.command || '(none)', verdict: 'UNREADABLE', why: 'no .claude/hooks/*.sh path in the command line' }); continue }
         const script = `.claude/hooks/${m[0].split('/').pop()}`
+        if (event === 'PreToolUse') {
+          // A missing matcher, `""` and `"*"` are Claude Code's own "match every
+          // tool" spellings (docs/settings reference), not a pattern to compile
+          // -- feeding `"*"` to `RegExp` throws (an unquantified `*` at the
+          // start), which this used to read as MATCHER BLIND on a group that in
+          // fact fires on every tool. Claude Code itself tests a matcher
+          // unanchored, so this does too rather than requiring a whole-string
+          // match a real config was never written to satisfy.
+          const tools = HOOK_TOOLS[script] || EDIT_TOOLS
+          let fires = g.matcher == null || g.matcher === '' || g.matcher === '*'
+          if (!fires) {
+            try { fires = tools.some((t) => new RegExp(g.matcher).test(t)) } catch { fires = false }
+          }
+          if (!fires) rows.push({ event, script, verdict: 'MATCHER BLIND', why: `matcher ${JSON.stringify(g.matcher)} cannot fire on ${tools.join(', ')}, the tools ${script} judges, so it never sees one` })
+        }
         if (!fs.existsSync(path.join(ROOT, script))) { rows.push({ event, script, verdict: 'MISSING', why: 'the command names a file that is not in the tree' }); continue }
         let out = ''
         let code = 0

## Before you return the verdict (P275)
Run `python3 -I tools/audit/carry_audit.py check --body <PR body file> --comments <file holding [{"id": 0, "body": <verdict.md text>}]>`. Give every reported item its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>`;
an evidence line flagged by its wording takes `Carry: dismissed: evidence, not a finding`. Return the verdict only at rc 0.
