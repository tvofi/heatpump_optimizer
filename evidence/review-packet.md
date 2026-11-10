# Review packet #3355
head: 46f0637251e85de671f9870b60fbb852515c0989
base: 01782a1e3c327cbfb69784b8e676359e5bcfa079

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: red
CodeQL id=129557070912 success
arch-score / arch-score id=129684185419 success
arm id=129555378546 skipped
budget-raise-gate / budget-raise-gate id=129684186156 success
cancel-superseded id=129684212397 success
codeql id=129555864717 skipped
codeql / Analyze (actions) id=129684185561 success
codeql / Analyze (javascript-typescript) id=129684223092 success
codeql / Analyze (python) id=129684185501 success
gate id=129556518452 failure
governance id=129555865613 skipped
governance / delivery-status id=129684185599 skipped
governance / delivery-status-publish id=129684185301 skipped
governance / env-matrix id=129684185114 success
governance / instrument-self-tests id=129684183674 in_progress
governance / policy-docs id=129684229290 success
governance / record id=129684229354 skipped
governance / wave-script id=129684183721 failure
hassfest id=129555864993 skipped
hassfest / hassfest id=129684185788 success
kernel-points id=129684220830 skipped
pr-contract id=129556519887 skipped
prelude id=129684183977 success
refresh id=129684184532 skipped
tests id=129555864695 skipped
tests / arch-instrument id=129684186648 success
tests / briefs id=129684224549 success
tests / browser id=129684187245 success
tests / ci-ratchet id=129684187770 skipped
tests / claims-autofix id=129684187984 skipped
tests / closure-scope id=129684185911 success
tests / closures id=129684186919 success
tests / closures-autofix id=129684187590 skipped
tests / coverage id=129684186978 success
tests / coverage-ratchet id=129684187860 success
tests / fast (3.14) id=129684187013 success
tests / graders-head-copy id=129684187719 skipped
tests / lane-proofs id=129684188359 skipped
tests / mutation id=129684185987 success
tests / mutation-autofix id=129684186743 skipped
tests / mutation-pins id=129684185738 skipped
tests / nightly-ha id=129684186552 skipped
tests / nightly-status id=129684185569 skipped
tests / replay id=129684186657 skipped
tests / typing id=129684186801 success
validate id=129555865832 skipped
validate / validate-hacs id=129684220953 success

## Refusals
red-unanswered: concluded red check `governance / wave-script` is not named in ## Red checks

## Advisories
required-wait: required context `gate` reads concluded failure at 46f0637251e85de671f9870b60fbb852515c0989 in the digest, but merge_train.py classify --pr reads WAIT (pending: gate red: none): classify decides, as bus.sh's dispatch does, and a pending check never refuses

## carry_audit at the head
CARRY-AUDIT: 0 finding item(s): 0 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
ok         node tools/policy/field_coverage.mjs
             `tools/policy/field_coverage.mjs` is in the tree at this head
  ok         node tools/policy/field_coverage.mjs --self-test
             `tools/policy/field_coverage.mjs` is in the tree at this head
  ok         python3 -I tools/pr/figure_block.py --self-test
             `tools/pr/figure_block.py` is in the tree at this head
  ok         python3 tests/structure.py
             `tests/structure.py` is in the tree at this head
  ok         PYTHONPATH=tests/hastub python3 tests/entities.py
             `tests/entities.py` is in the tree at this head
  ok         python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)
             `tests/closure.py` is in the tree at this head
  ok         tests/closure.py changes the gate itself
             `tests/closure.py` is in the tree at this head
  ok         tools/pr/prepr.sh
             `tools/pr/prepr.sh` is in the tree at this head

FIGURES: 8 resolved, 0 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
none

## Three-dot diff
diff --git a/.github/PULL_REQUEST_TEMPLATE.md b/.github/PULL_REQUEST_TEMPLATE.md
index a99bf6be3..39ca29a43 100644
--- a/.github/PULL_REQUEST_TEMPLATE.md
+++ b/.github/PULL_REQUEST_TEMPLATE.md
@@ -18,10 +18,10 @@ What the unmodified tree does.
 
 ## Figures
 
-`none`, or one line per figure the body states, with the command that printed it;
-name the instrument rather than restate what it prints. `pr-contract` refuses a
-command that does not resolve, and never re-runs one. Required check `arch-score`:
-a gate rise passes only explained under `## Architecture score`, one line per metric.
+`none`, or one line per figure with the command that printed it; name the
+instrument, not what it prints. `pr-contract` refuses a command that does not
+resolve, never re-runs one. Gate rise: explain under `## Architecture score`.
+Registered: empty `<!-- figure-block: scope-line -->`..`<!-- /figure-block -->`, `body_push.sh` fills it.
 
 ## Red checks
 
diff --git a/.github/workflows/governance.yml b/.github/workflows/governance.yml
index 712c475ed..5bba00339 100644
--- a/.github/workflows/governance.yml
+++ b/.github/workflows/governance.yml
@@ -547,6 +547,14 @@ jobs:
         if: steps.scope.outputs.superseded-run-canceller == 'true'
         run: python3 tools/pr/cancel_superseded.py --self-test
 
+      - name: Show the figure-block renderer refusing its own fixtures
+        id: figure-block
+        if: steps.scope.outputs.figure-block == 'true'
+        run: |
+          set -o pipefail
+          python3 -I tools/pr/figure_block.py --self-test | tee "$RUNNER_TEMP/figure-block-self-test.txt"
+          grep -Eq '^figure_block self-test: [1-9][0-9]* checks, 0 failed$' "$RUNNER_TEMP/figure-block-self-test.txt"
+
       # The Dependabot auto-merge decision (dependabot-automerge.yml): patch and
       # minor merge, a major is left, and a code-owned path withholds the App's
       # approval, over fixtures and the tree's own CODEOWNERS.
diff --git a/.github/workflows/pr-contract.yml b/.github/workflows/pr-contract.yml
index 30c7a6b59..88f89bf2b 100644
--- a/.github/workflows/pr-contract.yml
+++ b/.github/workflows/pr-contract.yml
@@ -371,6 +371,17 @@ jobs:
         if: always()
         run: if test -f .claude/workflows/figure_lint.mjs; then node .claude/workflows/figure_lint.mjs --pr-body /tmp/pr-body.md; else node tools/policy/figure_lint.mjs --pr-body /tmp/pr-body.md; fi
 
+      # Generated figure blocks are re-rendered from an instrument the BASE's
+      # tools/pr/figure_registry.json names, run by the base's restored copy of
+      # the program (tools/pr/*.py) over the head's tree, read-only. A body with
+      # no block passes.
+      - name: Every figure block is what its registered instrument renders
+        if: always()
+        env:
+          PR_HEAD: ${{ steps.pr.outputs.head }}
+          PR_BASE: ${{ steps.pr.outputs.base }}
+        run: python3 -I tools/pr/figure_block.py verify /tmp/pr-body.md --base "$PR_BASE" --head "$PR_HEAD"
+
       # preflight.sh refuses a closing keyword whose number is not in the
       # intended list it is given. prepr.sh's step 7 derives it with this
       # program byte for byte (`preflight_body`; its self-test pins that). The
diff --git a/dev/programme/delivery/3355.md b/dev/programme/delivery/3355.md
new file mode 100644
index 000000000..603758353
--- /dev/null
+++ b/dev/programme/delivery/3355.md
@@ -0,0 +1 @@
+- [#3355](https://github.com/tvofi/heatpump_optimizer/pull/3355) — **open**, R10-BODY-CONTRACT: body contract, part 3 (R10-BODY-CONTRACT)
diff --git a/tests/closure.py b/tests/closure.py
index 97e609de1..b7d4ce8bd 100644
--- a/tests/closure.py
+++ b/tests/closure.py
@@ -609,6 +609,10 @@ INERT_EXCEPT = (
     # merge: skip-merge-failed on this pair). Same route as the README above:
     # the tools/pr/ prefix stays INERT, the file moves to the recorded closure.
     "tools/pr/cancel_superseded.py",
+    # R10-BODY-CONTRACT-P3: the figure-block renderer and its registry; same route
+    # as cancel_superseded.py above (prefix INERT, file moves to the recorded closure).
+    "tools/pr/figure_block.py",
+    "tools/pr/figure_registry.json",
     # R10-CI-LAYOUT P2b: tests/entities.py imports U5's harness modules (`_u5_load`:
     # run_part.py, unitcheck.py) and opens codeql.yml's program tools/pr/codeql_scope.py
     # (U3's pins). CI's recording on probe #2656 (closures-autofix job 120356230438)
diff --git a/tests/closures.json b/tests/closures.json
index f0029814f..62fe1b8b5 100644
--- a/tests/closures.json
+++ b/tests/closures.json
@@ -1926,6 +1926,8 @@
    "tools/pr/app_approve.sh",
    "tools/pr/cancel_superseded.py",
    "tools/pr/codeql_scope.py",
+   "tools/pr/figure_block.py",
+   "tools/pr/figure_registry.json",
    "tools/pr/preflight.sh",
    "tools/release/stamp.py",
    "tools/replay/cut_day.py",
diff --git a/tools/audit/seat/INSTRUMENTS.md b/tools/audit/seat/INSTRUMENTS.md
index 6e6d022b2..11ca43cd0 100644
--- a/tools/audit/seat/INSTRUMENTS.md
+++ b/tools/audit/seat/INSTRUMENTS.md
@@ -23,6 +23,7 @@ re-runnable measurement harnesses a fixer or judge lands with a PR — its
 - [`app_comment.sh`](instruments/app_comment.sh.md) — posts one fix-review verdict on a PR as `hpo-approver` and reads the posted comment back byte-identical
 - [`app_push.sh`](instruments/app_push.sh.md) — pushes a branch and opens or re-bodies its pull request as the `hpo-author` App
 - [`depgraph.py` (tools/pr/)](instruments/depgraph.py.md) — compares GitHub's dependency graph with the tree's pins
+- [`figure_block.py` (tools/pr/)](instruments/figure_block.py.md) — renders/refreshes/verifies registered figure blocks in a PR body
 - [`head_note.py` (tools/pr/)](instruments/head_note.py.md) — prefixes a note under a body's `## Head` heading, found as `checkPrBody`'s `sections()` reads it (outside a fence, `##`, whitespace, `Head`)
 - [`role_pack.py` (tools/policy/)](instruments/role_pack.py.md) — renders one seat's policy pack: its role contract, the rules its reads load and the INSTRUMENTS.md entries it names, verbatim, in one file
 - [`approve_held_runs.sh`](instruments/approve_held_runs.sh.md) — approves the workflow runs GitHub holds `action_required` on a branch
diff --git a/tools/audit/seat/body_push.sh b/tools/audit/seat/body_push.sh
index 1a2e54df9..c56e418fa 100644
--- a/tools/audit/seat/body_push.sh
+++ b/tools/audit/seat/body_push.sh
@@ -21,7 +21,8 @@ if [ "${1:-}" = "--self-test" ]; then
   . "$SH/../../../tests/throwaway_git.sh"
   mkcopy() { mkdir -p "$W/$1/audit/seat" "$W/$1/pr"; cp "$SH/ref_privacy.py" "$W/$1/audit/seat/"
     if [ "$2" = real ]; then cp "$SELF" "$W/$1/audit/seat/body_push.sh"; else sed '/# mut:keep$/s/.*/    :/' "$SELF" > "$W/$1/audit/seat/body_push.sh"; fi
-    printf '#!/bin/bash\n[ "$1" = --body-check ] && [ -f "$FLAGS/lint" ] && { echo lint-stub-refuses; exit 1; }\nexit 0\n' > "$W/$1/pr/prepr.sh"; }
+    printf '#!/bin/bash\n[ "$1" = --body-check ] && [ -f "$FLAGS/lint" ] && { echo lint-stub-refuses; exit 1; }\nexit 0\n' > "$W/$1/pr/prepr.sh"
+    printf 'import os\nopen(os.environ["FLAGS"] + "/refreshed", "w").close()\n' > "$W/$1/pr/figure_block.py"; }
   mkcopy t real; mkcopy m mutant
   printf '#!/bin/bash\nexit 0\n' > "$W/packer"; printf '#!/bin/bash\n[ -f "$FLAGS/packet" ] && exit 1\nexit 0\n' > "$W/packer"
   printf '#!/bin/bash\n[ -f "$FLAGS/landed" ] && exit 1\nexit 0\n' > "$W/landed"; chmod +x "$W/packer" "$W/landed"
@@ -65,6 +66,8 @@ if [ "${1:-}" = "--self-test" ]; then
   st "$rc" 0 "the healthy run pushes"
   st "$(git -C "$W/o.git" show handoff-body/t:BODY.md 2>/dev/null)" "the body" "... to handoff-body/t"
   st "$(keepsha)" none "... and the keep ref is gone"
+  st "$([ -f "$W/flags/refreshed" ] && echo ran || echo no)" ran "the seat-side figure-block refresh ran"
+  drop; run m; st "$([ -f "$W/flags/refreshed" ] && echo ran || echo no)" no "MUTANT refresh deleted: the arm above would fail"
   st "$(git -C "$W/repo" merge-base --is-ancestor "$(git -C "$W/o.git" rev-parse handoff-body/t)" "$CODE" 2>/dev/null; echo $?)" 1 "(null) the published body is not in the code head's ancestry"
   echo "body_push self-test: $N checks, $FAILS failed"; [ "$FAILS" = 0 ]; exit $?
 fi
@@ -151,6 +154,9 @@ if [ -n "$HREF" ]; then
   # The `mutation` red an unpinned site makes is derived, so it is written into
   # `## Red checks` before the lint, not refused at the open (P67).
   (cd "$ROOT" && bash "$HERE/../../pr/prepr.sh" --fill-red "$ABS")
+  # The seat-side writer re-renders every registered figure block at the code head with no
+  # agent turn (card 7 option C); pr-contract only verifies. A refusal aborts the push (set -e).
+  (cd "$ROOT" && python3 -I "$HERE/../../pr/figure_block.py" refresh "$ABS") # mut:keep
   # The red-check arm reads the pull request's head ref over the network, so it
   # is asked for only when origin holds fix/<topic> (a first handoff has none).
   PRB=""
diff --git a/tools/audit/seat/instruments/figure_block.py.md b/tools/audit/seat/instruments/figure_block.py.md
new file mode 100644
index 000000000..a7d7d28af
--- /dev/null
+++ b/tools/audit/seat/instruments/figure_block.py.md
@@ -0,0 +1,14 @@
+# `figure_block.py`
+
+- `figure_block.py` (tools/pr/) — fills and checks the generated figure blocks
+  in a PR body (`<!-- figure-block: NAME -->` ... `<!-- /figure-block -->`).
+  When: a figure a registered instrument prints (scope-line, structure-ratchet,
+  merge-base), which must not be typed. Refusal: the registry is read from the
+  BASE's `tools/pr/figure_registry.json`, so the author chooses no command, only
+  a registered name; an unregistered name, or a block that differs from what
+  the instrument renders at the head, is refused. A body with no block passes.
+  `render NAME` prints one block; `refresh BODY` fills the blocks in a body
+  file at the head (what `seat/body_push.sh` and `prepr.sh --body-check` run);
+  `verify BODY --base SHA --head SHA` re-renders read-only and refuses a
+  difference (what `pr-contract` runs). `--self-test` runs offline over
+  fixtures and prints `figure_block self-test: N checks, 0 failed`.
diff --git a/tools/ci/selftest_closures.json b/tools/ci/selftest_closures.json
index e6250cad1..64c0c6c4b 100644
--- a/tools/ci/selftest_closures.json
+++ b/tools/ci/selftest_closures.json
@@ -2307,6 +2307,25 @@
    "objects": false,
    "git": []
   },
+  "figure-block": {
+   "run_sha": "7295269b8e4ede5ee5449b86ec2276c56cbd36e12d6e4d0de3373e49703b1cc9",
+   "files": [
+    "tests/throwaway_git.py",
+    "tools/pr/figure_block.py"
+   ],
+   "probes": [
+    ".",
+    "tests",
+    "tools",
+    "tools/pr"
+   ],
+   "dirs": [
+    "tests"
+   ],
+   "index": false,
+   "objects": false,
+   "git": []
+  },
   "figure-census": {
    "run_sha": "740c9b07ed8530eb237326010160ac6b0a36a741f8dd09a41ce91c3a78aaacb7",
    "files": [
diff --git a/tools/policy/field_coverage.mjs b/tools/policy/field_coverage.mjs
index 853318694..eca2116c2 100644
--- a/tools/policy/field_coverage.mjs
+++ b/tools/policy/field_coverage.mjs
@@ -347,7 +347,7 @@ const DECLARED = {
   'pinned tools/audit/preflight.sh': { none: 'runs other checks; no input of its own' },
   'pinned tools/audit/prepr.sh': { none: 'runs other checks over a body; no input of its own' },
   'pinned tools/audit/prepare_baseline.sh': { none: 'check-wave-script reads its ISOLATED_DIMS line as text; it grades no input here' },
-  'pinned tools/pr/figure_block.py': { none: 'reads the figures a pull-request body states against the commands that produced them; graded by its own self-test, no arm here', pending: 'R10-BODY-CONTRACT part 3 pins it in governance.yml' },
+  'pinned tools/pr/figure_block.py': { none: 'reads the figures a pull-request body states against the commands that produced them; graded by its own self-test, no arm here' },
   'pinned tools/audit/machinery_ratchet.py': { none: 'reads machinery_budgets.json through load_budgets(), which refuses a key it does not read and requires each it does (its --self-test pins both), and merge history; no arm here' },
   'pinned tools/audit/round6/D11/fix/codeowners_gap.py': { none: 'reads CODEOWNERS and workflows; residual (D11-s1-03), no arm here' },
   'stamp rule 4': { none: 'reads commit parents and subjects; residual (D11-s1-02), no arm here' },
diff --git a/tools/policy/figure_lint.mjs b/tools/policy/figure_lint.mjs
index 34e40eb20..ab5ce3593 100755
--- a/tools/policy/figure_lint.mjs
+++ b/tools/policy/figure_lint.mjs
@@ -16,7 +16,11 @@
 // the tree would have.
 //
 // WHAT THIS DELIBERATELY DOES NOT DO: it does not execute one character of the
-// body. #679 proposed re-executing allowlisted commands and comparing the
+// body. (Narrowed by card 7, 2026-11-07: the refusal stands, and what changed
+// is who chooses. tools/pr/figure_block.py renders a figure-block only from an
+// instrument the BASE's tools/pr/figure_registry.json names, so the author
+// chooses no command, only a registered name; a free-form figure is still
+// never executed.) #679 proposed re-executing allowlisted commands and comparing the
 // printed value to the stated one. That is refused, and the reasons are
 // recorded here so the next seat has to answer them rather than rediscover
 // them. TWO OF THEM ARE LOAD-BEARING, one is load-bearing for one arm, and the
diff --git a/tools/policy/policy_lint.mjs b/tools/policy/policy_lint.mjs
index ab4ade7c6..47182b013 100644
--- a/tools/policy/policy_lint.mjs
+++ b/tools/policy/policy_lint.mjs
@@ -410,6 +410,7 @@ const LOOP_CHECK_NAMES = [
   // `## Friction` section and the histogram keying nothing, which is the
   // silent shape the shared parser replaced.
   { name: 'checkPrBody', file: 'policy_lint.mjs', kind: 'return' },
+  { name: 'figureBlockProblems', file: 'policy_lint.mjs', kind: 'return' },
   { name: 'frictionEntries', file: 'policy_lint.mjs', kind: 'return' },
   // The histogram's KEYING, which is a second silent shape beside the grammar's:
   // `frictionEntries` decides what an entry IS, `frictionKey` decides which key
@@ -4035,6 +4036,33 @@ function assertAcceptance(derived) {
     }
   }
 
+  // The figure-block arm: a rendered block in `## Figures` passes; each rule
+  // draws exactly its own error; free-form figures with no block are the null
+  // control. Bodies are the healthy good.md with its Figures section swapped.
+  {
+    const own = fs.readFileSync(path.join(prepr, 'good.md'), 'utf8')
+    const figs = own.slice(own.indexOf('## Figures'), own.indexOf('## Red checks'))
+    const H = 'a'.repeat(40)
+    const blk = (attrs) => `<!-- figure-block: scope-line${attrs} -->\n~~~text\nx\n~~~\n<!-- /figure-block -->`
+    const good = blk(` mb=${H} head=${H}`)
+    const cases = [
+      ['a rendered block', `## Figures\n\n${good}\n\n`, null],
+      ['free-form figures, no block (null control)', figs, null],
+      ['a malformed marker', `## Figures\n\n<!-- figure-block: Scope -->\n`, 'does not parse'],
+      ['an unclosed block', `## Figures\n\n${good.replace('<!-- /figure-block -->', '')}\n`, 'never closed'],
+      ['a block outside Figures', `${figs}## Notes\n\n${good}\n\n`, 'outside'],
+      ['another head', `## Figures\n\n${blk(` mb=${H} head=${'b'.repeat(40)}`)}\n\n`, 'another head'],
+      ['an unrendered marker', `## Figures\n\n${blk('')}\n\n`, 'unrendered'],
+    ]
+    for (const [label, text, needle] of cases) {
+      const errs = figureBlockProblems(own.replace(figs, text), { head: H })
+      if (needle ? errs.length !== 1 || !errs[0].includes(needle) : errs.length) {
+        console.log(`\nFIXTURE VACUOUS: the figure-block arm on ${label} drew ${errs.length} error(s) (${errs.map((e) => e.slice(0, 80)).join(' | ')}); it must draw ${needle ? `exactly one, naming \`${needle}\`` : 'none'}`)
+        return 1
+      }
+    }
+  }
+
   // The attribution arm (R10-FLY-NO-FOOTERS): attribution.md is a healthy body
   // plus the footer and a session link, so the arm and only the arm fires on
   // it; good-claude-ai.md names claude.ai in another sense and quotes the
@@ -7050,6 +7078,45 @@ function dependabotYmlAt(base) {
   try { return fs.readFileSync(path.join(ROOT, '.github', 'dependabot.yml'), 'utf8') } catch { return '' }
 }
 
+// The offline half of the figure-block contract (tools/pr/figure_block.py is the
+// grammar's owner and `verify` the rendering half; this runs no instrument).
+// Same line scan as figure_block.parse: an open marker that does not parse, a
+// block never closed or opened inside another, a block outside `## Figures`, a
+// block rendered at another head or never rendered, a name the base's registry
+// does not hold.
+const FIGURE_OPEN = /^<!-- figure-block: ([a-z][a-z0-9-]*)((?: [a-z]+=[0-9a-f]{40})*) -->$/
+const FIGURE_CLOSE = '<!-- /figure-block -->'
+function figureBlockProblems(body, { base = '', head = '' } = {}) {
+  const msgs = []
+  const lines = body.split('\n')
+  const inFigures = new Set((sections(body).get('Figures') ?? '').split('\n'))
+  const headOk = /^[0-9a-f]{40}$/.test(head) && !/^0{40}$/.test(head)
+  let registry
+  if (base) {
+    try {
+      registry = Object.keys(JSON.parse(execFileSync('git', ['show', `${base}:tools/pr/figure_registry.json`], { cwd: ROOT, encoding: 'utf8', stdio: ['ignore', 'pipe', 'ignore'] })).instruments ?? {})
+    } catch { registry = undefined }
+  }
+  for (let i = 0; i < lines.length; i++) {
+    const m = FIGURE_OPEN.exec(lines[i])
+    if (!m) {
+      if (lines[i].startsWith('<!-- figure-block')) msgs.push(`line ${i + 1}: a figure-block marker that does not parse: ${JSON.stringify(lines[i].slice(0, 80))}`)
+      continue
+    }
+    let j = i + 1
+    while (j < lines.length && lines[j] !== FIGURE_CLOSE && !lines[j].startsWith('<!-- figure-block')) j++
+    if (j >= lines.length) { msgs.push(`line ${i + 1}: figure-block ${m[1]} is never closed`); break }
+    if (lines[j] !== FIGURE_CLOSE) { msgs.push(`line ${j + 1}: a figure-block opens inside another`); i = j - 1; continue }
+    if (!inFigures.has(lines[i]) || !inFigures.has(lines[j])) msgs.push(`line ${i + 1}: figure-block ${m[1]} lies outside \`## Figures\``)
+    const headAttr = /(?:^| )head=([0-9a-f]{40})/.exec(m[2])?.[1]
+    if (headOk && headAttr === undefined) msgs.push(`line ${i + 1}: figure-block ${m[1]} is unrendered: run figure_block.py refresh`)
+    else if (headOk && headAttr !== head) msgs.push(`line ${i + 1}: figure-block ${m[1]} names another head (${headAttr.slice(0, 12)}, this is ${head.slice(0, 12)}): run figure_block.py refresh`)
+    if (registry && !registry.includes(m[1])) msgs.push(`line ${i + 1}: figure-block ${m[1]} is not registered at base`)
+    i = j
+  }
+  return msgs
+}
+
 function checkPrBody(bodyPath, { base = '', head = '', title = '', red = [], paths = [], existing = null, notes = [], author = null, commits = null, required = null } = {}) {
   // A Dependabot pull request answers the dependency-bump contract instead
   // (tools/policy/dependabot_contract.mjs); every other author, the full one.
@@ -7175,6 +7242,8 @@ function checkPrBody(bodyPath, { base = '', head = '', title = '', red = [], pat
       message: `check \`${name}\` is red and \`## Red checks\` does not name it.${why} Name the failure and answer it: the cheaper detector and its standing cost, or the finding that none exists.` })
   }
 
+  for (const message of figureBlockProblems(body, { base, head })) out.push({ severity: 'error', check: 'pr-body', where: bodyPath, message })
+
   return out
 }
 
diff --git a/tools/pr/figure_block.py b/tools/pr/figure_block.py
new file mode 100644
index 000000000..4b0c392c5
--- /dev/null
+++ b/tools/pr/figure_block.py
@@ -0,0 +1,304 @@
+#!/usr/bin/env python3
+"""Generated figure blocks for a pull-request body (owner's card 7, option B).
+
+A body's `## Figures` may carry a block whose text is *rendered*, not typed:
+
+    <!-- figure-block: scope-line mb=<40 hex> head=<40 hex> -->
+    ~~~text
+    <what the registered instrument printed>
+    ~~~
+    <!-- /figure-block -->
+
+``figure_registry.json`` names the instruments a block may come from. It is read
+from the BASE tree (``--base``), as ``.claude/workflows/*`` already is, so a pull
+request can neither add an instrument nor choose a command and use it in the
+same pull request: **the author chooses no command**, only a registered name.
+Each registered instrument runs in a throwaway worktree of the head, with the
+registry's ``files`` overlaid from the base, so the program is the base's and the
+tree it measures is the head's.
+
+    figure_block.py render NAME   [--base REF] [--head REF]   print one block
+    figure_block.py refresh BODY  [--base REF] [--head REF]   re-render every block in place
+    figure_block.py verify  BODY  [--base REF] [--head REF]   refuse a block that is not what the
+                                                               registry renders (read-only)
+    figure_block.py --self-test
+
+``refresh`` is the seat-side writer (``body_push.sh``, ``prepr.sh``): a body
+carries an empty marker and the writer fills it at the head with no agent turn.
+``verify`` (``pr-contract``) renders and compares; it writes nothing. Only a
+*registered* figure is structurally non-stale: a free-form figure under
+``## Figures`` stays as it was, well-formed and resolvable, never executed.
+"""
+from __future__ import annotations
+
+import json
+import os
+import re
+import shutil
+import subprocess
+import sys
+import tempfile
+
+REGISTRY = "tools/pr/figure_registry.json"
+OPEN_RE = re.compile(r"^<!-- figure-block: (?P<name>[a-z][a-z0-9-]*)(?P<attrs>(?: [a-z]+=[0-9a-f]{40})*) -->$")
+CLOSE = "<!-- /figure-block -->"
+FENCE = "~~~text"
+FENCE_END = "~~~"
+PLACEHOLDERS = ("mb", "head", "base", "workdir")
+
+
+class Refused(Exception):
+    pass
+
+
+def _git(root: str, *args: str) -> str:
+    p = subprocess.run(["git", "-C", root, *args], capture_output=True, text=True, check=False)
+    if p.returncode:
+        raise Refused(f"git {' '.join(args)}: {p.stderr.strip() or 'failed'}")
+    return p.stdout.strip()
+
+
+def load_registry(root: str, base: str) -> dict:
+    """The registry as the BASE tree holds it; a base without one registers nothing."""
+    p = subprocess.run(["git", "-C", root, "show", f"{base}:{REGISTRY}"], capture_output=True, text=True, check=False)
+    if p.returncode:
+        return {}
+    data = json.loads(p.stdout)
+    return data.get("instruments", {})
+
+
+def parse(text: str):
+    """Yield (start, end, name, attrs, body) per block; line indexes are [start, end]."""
+    lines = text.split("\n")
+    out, i = [], 0
+    while i < len(lines):
+        m = OPEN_RE.match(lines[i])
+        if not m:
+            if lines[i].startswith("<!-- figure-block"):
+                raise Refused(f"line {i + 1}: a figure-block marker that does not parse: {lines[i][:80]!r}")
+            i += 1
+            continue
+        j = i + 1
+        while j < len(lines) and lines[j] != CLOSE:
+            if lines[j].startswith("<!-- figure-block"):
+                raise Refused(f"line {j + 1}: a figure-block opens inside another")
+            j += 1
+        if j >= len(lines):
+            raise Refused(f"line {i + 1}: figure-block {m['name']} is never closed")
+        attrs = dict(a.split("=") for a in m["attrs"].split())
+        out.append((i, j, m["name"], attrs, lines[i + 1:j]))
+        i = j + 1
+    return lines, out
+
+
+def render_text(name: str, attrs: dict, output: str) -> list[str]:
+    a = "".join(f" {k}={attrs[k]}" for k in ("mb", "head") if k in attrs)
+    return [f"<!-- figure-block: {name}{a} -->", FENCE, *output.rstrip("\n").split("\n"), FENCE_END, CLOSE]
+
+
+def run_instrument(root: str, base: str, head: str, mb: str, name: str, reg: dict) -> str:
+    """Run one registered instrument over the head's tree with the base's program."""
+    if name not in reg:
+        raise Refused(f"`{name}` is not in the registry at {base[:12]}:{REGISTRY} "
+                      f"({', '.join(sorted(reg)) or 'it registers nothing'}); a pull request cannot add an instrument and use it")
+    ent = reg[name]
+    tmp = tempfile.mkdtemp(prefix="figblock-")
+    wt = os.path.join(tmp, "wt")
+    workdir = os.path.join(tmp, "work")
+    os.mkdir(workdir)
+    try:
+        _git(root, "worktree", "add", "--detach", "-q", wt, head)
+        for f in ent.get("files", []):
+            _git(wt, "checkout", base, "--", f)  # the base's program, not the head's
+        sub = dict(mb=mb, head=head, base=base, workdir=workdir)
+        argv = [a.format(**sub) for a in ent["argv"]]
+        env = {k: v for k, v in os.environ.items() if k in ("PATH", "HOME", "LANG", "TMPDIR", "VIRTUAL_ENV")}
+        env["PYTHONPATH"] = "tests/hastub"
+        p = subprocess.run(argv, cwd=wt, env=env, capture_output=True, text=True, timeout=ent.get("timeout_s", 300), check=False)
+        if p.returncode not in ent.get("ok_rc", [0]):
+            raise Refused(f"`{name}` exited {p.returncode}: {(p.stderr or p.stdout).strip()[-300:]}")
+        lines = p.stdout.rstrip("\n").split("\n")
+        if "grep" in ent:
+            lines = [ln for ln in lines if re.search(ent["grep"], ln)]
+        if "tail" in ent:
+            lines = lines[-int(ent["tail"]):]
+        if not lines or lines == [""]:
+            raise Refused(f"`{name}` printed nothing after its filter")
+        return "\n".join(lines)
+    finally:
+        subprocess.run(["git", "-C", root, "worktree", "remove", "--force", wt], capture_output=True, check=False)
+        shutil.rmtree(tmp, ignore_errors=True)
+
+
+def context(root: str, base: str, head: str) -> tuple[str, str]:
+    head_sha = _git(root, "rev-parse", "--verify", head + "^{commit}")
+    return head_sha, _git(root, "merge-base", base, head_sha)
+
+
+def cmd_render(root, base, head, name):
+    head_sha, mb = context(root, base, head)
+    out = run_instrument(root, base, head_sha, mb, name, load_registry(root, base))
+    print("\n".join(render_text(name, {"mb": mb, "head": head_sha}, out)))
+
+
+def cmd_refresh(root, base, head, body_path):
+    text = open(body_path, encoding="utf-8").read()
+    lines, blocks = parse(text)
+    if not blocks:
+        return 0
+    head_sha, mb = context(root, base, head)
+    reg = load_registry(root, base)
+    for i, j, name, _attrs, _b in reversed(blocks):
+        out = run_instrument(root, base, head_sha, mb, name, reg)
+        lines[i:j + 1] = render_text(name, {"mb": mb, "head": head_sha}, out)
+    open(body_path, "w", encoding="utf-8").write("\n".join(lines))
+    print(f"figure_block: refreshed {len(blocks)} block(s) at {head_sha[:12]}")
+    return 0
+
+
+def verify_text(text: str, root: str, base: str, head: str) -> list[str]:
+    """Problems with the blocks in ``text``; none when every block is what the registry renders."""
+    _lines, blocks = parse(text)
+    if not blocks:
+        return []
+    head_sha, mb = context(root, base, head)
+    reg = load_registry(root, base)
+    problems = []
+    for i, _j, name, attrs, body in blocks:
+        if attrs.get("head") != head_sha or attrs.get("mb") != mb:
+            problems.append(f"line {i + 1}: block `{name}` names head={attrs.get('head', '-')[:12]} mb={attrs.get('mb', '-')[:12]}, "
+                            f"this run is head={head_sha[:12]} mb={mb[:12]}; re-render with `figure_block.py refresh <body>`")
+            continue
+        try:
+            want = render_text(name, attrs, run_instrument(root, base, head_sha, mb, name, reg))[1:-1]
+        except Refused as e:
+            problems.append(f"line {i + 1}: block `{name}`: {e}")
+            continue
+        if body != want:
+            problems.append(f"line {i + 1}: block `{name}` is not what the registered instrument printed at {head_sha[:12]}; "
+                            "a figure block is rendered, never typed -- run `figure_block.py refresh <body>`")
+    return problems
+
+
+def cmd_verify(root, base, head, body_path):
+    problems = verify_text(open(body_path, encoding="utf-8").read(), root, base, head)
+    for p in problems:
+        print(f"  ERROR   [figure-block] {p}")
+    n = len(parse(open(body_path, encoding="utf-8").read())[1])
+    print(f"figure_block verify: {n} block(s), {len(problems)} refused")
+    return 1 if problems else 0
+
+
+def _scope(root: str, mb: str, workdir: str) -> int:
+    """The registered `scope-line` instrument: the gate's MODE line for the diff since ``mb``."""
+    p = subprocess.run([sys.executable, "tests/closure.py", "select", "--diff", mb, "--workdir", workdir],
+                       cwd=root, capture_output=True, text=True, check=False)
+    scope = os.path.join(workdir, "scope.txt")
+    if p.returncode or not os.path.exists(scope):
+        print(p.stderr[-300:], file=sys.stderr)
+        return 1
+    mode = [ln for ln in open(scope, encoding="utf-8").read().split("\n") if ln.strip().startswith("MODE:")]
+    print(mode[0].strip() if mode else "no MODE line")
+    return 0 if mode else 1
+
+
+def _self_test() -> int:
+    results = []
+
+    def check(name, ok):
+        results.append(bool(ok))
+        print(("  ok  " if ok else "  FAIL") + " " + name)
+
+    def refused(fn):
+        try:
+            fn()
+        except Refused:
+            return True
+        return False
+
+    tmp = tempfile.mkdtemp(prefix="figblock-st-")
+    try:
+        sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "tests"))
+        from throwaway_git import throwaway_git_init
+        env = throwaway_git_init(tmp, "-q", "-b", "main")
+
+        def g(*a, cwd=tmp):
+            subprocess.run(["git", *a], cwd=cwd, env=env, check=True, capture_output=True)
+        os.makedirs(os.path.join(tmp, "tools/pr"))
+        reg = {"instruments": {"mb": {"argv": ["git", "merge-base", "{base}", "{head}"], "files": []},
+                               "bad": {"argv": ["false"], "files": []}}}
+        open(os.path.join(tmp, REGISTRY), "w").write(json.dumps(reg))
+        open(os.path.join(tmp, "f"), "w").write("1")
+        g("add", "-A"); g("commit", "-qm", "base")
+        g("checkout", "-qb", "topic")
+        open(os.path.join(tmp, "f"), "w").write("2")
+        # a head that adds an instrument the base lacks
+        reg["instruments"]["evil"] = {"argv": ["echo", "pwned"], "files": []}
+        open(os.path.join(tmp, REGISTRY), "w").write(json.dumps(reg))
+        g("commit", "-qam", "head")
+        head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=tmp, capture_output=True, text=True).stdout.strip()
+        mbsha = subprocess.run(["git", "rev-parse", "main"], cwd=tmp, capture_output=True, text=True).stdout.strip()
+        body = os.path.join(tmp, "body.md")
+        empty = f"## Figures\n<!-- figure-block: mb -->\n<!-- /figure-block -->\nfree-form: `git log`\n"
+        open(body, "w").write(empty)
+        check("refresh fills an empty marker at the head with no agent turn", cmd_refresh(tmp, "main", "HEAD", body) == 0
+              and mbsha in open(body).read() and head in open(body).read())
+        check("verify accepts the refreshed body and the free-form line beside it", verify_text(open(body).read(), tmp, "main", "HEAD") == []
+              and "free-form: `git log`" in open(body).read())
+        typed = open(body).read().replace(mbsha + "\n~~~", "0" * 40 + "\n~~~", 1)
+        check("a hand-typed value in a block is refused", len(verify_text(typed, tmp, "main", "HEAD")) == 1)
+        moved = open(body).read().replace(head, "1" * 40)
+        check("a block naming another head is refused as stale", len(verify_text(moved, tmp, "main", "HEAD")) == 1)
+        g("commit", "-q", "--allow-empty", "-m", "head2")
+        check("a moved head is stale until the writer re-renders it", len(verify_text(open(body).read(), tmp, "main", "HEAD")) == 1
+              and cmd_refresh(tmp, "main", "HEAD", body) == 0 and verify_text(open(body).read(), tmp, "main", "HEAD") == [])
+        evil = "<!-- figure-block: evil -->\n<!-- /figure-block -->\n"
+        check("an instrument registered only by the head is refused (null: the base's own mb passes above)",
+              refused(lambda: cmd_refresh(tmp, "main", "HEAD", _w(body, evil))))
+        check("an unknown name is refused", refused(lambda: cmd_refresh(tmp, "main", "HEAD", _w(body, "<!-- figure-block: nope -->\n<!-- /figure-block -->\n"))))
+        check("an instrument that exits non-zero is refused", refused(lambda: cmd_refresh(tmp, "main", "HEAD", _w(body, "<!-- figure-block: bad -->\n<!-- /figure-block -->\n"))))
+        check("an unclosed block is refused", refused(lambda: parse("<!-- figure-block: mb -->\nx\n")))
+        check("a malformed marker is refused", refused(lambda: parse("<!-- figure-block: Mb -->\n")))
+        check("a body with no block is untouched (null control)", verify_text("## Figures\nnone\n", tmp, "main", "HEAD") == [])
+    finally:
+        shutil.rmtree(tmp, ignore_errors=True)
+    failed = results.count(False)
+    print(f"figure_block self-test: {len(results)} checks, {failed} failed")
+    return 1 if failed else 0
+
+
+def _w(path: str, text: str) -> str:
+    open(path, "w").write(text)
+    return path
+
+
+def main(argv: list[str]) -> int:
+    if argv[:1] == ["--self-test"]:
+        return _self_test()
+    if argv[:1] == ["_scope"]:
+        return _scope(os.getcwd(), argv[1], argv[2])
+    opts = {"--base": "origin/main", "--head": "HEAD"}
+    pos = []
+    it = iter(argv)
+    for a in it:
+        if a in opts:
+            opts[a] = next(it, "")
+        else:
+            pos.append(a)
+    if len(pos) != 2 or pos[0] not in ("render", "refresh", "verify"):
+        print(__doc__)
+        return 2
+    root = _git(os.getcwd(), "rev-parse", "--show-toplevel")
+    try:
+        if pos[0] == "render":
+            cmd_render(root, opts["--base"], opts["--head"], pos[1])
+            return 0
+        fn = cmd_refresh if pos[0] == "refresh" else cmd_verify
+        return fn(root, opts["--base"], opts["--head"], pos[1])
+    except Refused as e:
+        print(f"  ERROR   [figure-block] {e}")
+        return 1
+
+
+if __name__ == "__main__":
+    sys.exit(main(sys.argv[1:]))
diff --git a/tools/pr/figure_registry.json b/tools/pr/figure_registry.json
new file mode 100644
index 000000000..c3b1a4a96
--- /dev/null
+++ b/tools/pr/figure_registry.json
@@ -0,0 +1,21 @@
+{
+  "_doc": "Instruments a `## Figures` block may be rendered from (tools/pr/figure_block.py). Read from the BASE tree: a pull request cannot add an instrument and use it in the same pull request, and its author chooses no command. `files` are overlaid from the base before the run. Grow by separate pull requests.",
+  "instruments": {
+    "merge-base": {
+      "argv": ["git", "merge-base", "{base}", "{head}"],
+      "files": []
+    },
+    "scope-line": {
+      "argv": ["python3", "tools/pr/figure_block.py", "_scope", "{mb}", "{workdir}"],
+      "files": ["tools/pr/figure_block.py", "tests/closure.py"],
+      "timeout_s": 600
+    },
+    "structure-ratchet": {
+      "argv": ["python3", "tests/structure.py"],
+      "files": ["tests/structure.py"],
+      "ok_rc": [0, 1],
+      "grep": "^STRUCTURE RATCHET",
+      "timeout_s": 600
+    }
+  }
+}
diff --git a/tools/pr/prepr.sh b/tools/pr/prepr.sh
index e084c64a2..68b1b302b 100755
--- a/tools/pr/prepr.sh
+++ b/tools/pr/prepr.sh
@@ -254,6 +254,13 @@ pinned_touched() { # file of changed paths, pins (one per line)
   return 1
 }
 
+# Step 7a2's whole body, and --body-check's: a rendered figure block is re-rendered
+# from the base's registry at HEAD and compared (read-only, offline; pr-contract
+# runs the same verify). A body with no block passes untouched.
+figure_block_check() { # body file
+  python3 -I tools/pr/figure_block.py verify "$1" --base origin/main --head HEAD
+}
+
 # Step 7a's whole body, so `--self-test` drives the code the step runs rather
 # than a second copy of the command. A step wired into the run and demonstrated
 # by a sibling command is a step nothing pins: the assertion passes while the
@@ -1785,6 +1792,9 @@ if [ "${1:-}" = "--body-check" ]; then
   fout=$(figures_check "$2" 2>&1); fr=$?
   if [ "$fr" -eq 0 ]; then echo "figures ok: $(tail -1 <<<"$fout")"; else echo "REFUSE figures: $(tail -1 <<<"$fout")"; fi
   [ "$r" -ne 0 ] || r=$fr
+  gout=$(figure_block_check "$2" 2>&1); gr=$?
+  if [ "$gr" -eq 0 ]; then echo "figure blocks ok: $(tail -1 <<<"$gout")"; else printf '%s\n' "$gout"; echo "REFUSE figure blocks: $(tail -1 <<<"$gout")"; fi
+  [ "$r" -ne 0 ] || r=$gr
   vline=$(privacy_line); vr=$?
   if [ "$vr" -eq 0 ]; then echo "ref_privacy ok: $vline"; else echo "REFUSE ref_privacy: $vline"; fi
   [ "$r" -ne 0 ] || r=$vr
@@ -3880,6 +3890,9 @@ EOF
   st "$r" 0 "and a row that writes into the tracked fixture dir changes it (null control)"
   case "$bc" in *'fout=$(figures_check "$2" 2>&1); fr=$?'*'[ "$r" -ne 0 ] || r=$fr'*) r=0 ;; *) r=1 ;; esac
   st "$r" 0 "--body-check runs step 7a's figure lint and refuses on its rc (carry 8)"
+  case "$bc" in *'gout=$(figure_block_check "$2" 2>&1); gr=$?'*'[ "$r" -ne 0 ] || r=$gr'*) r=0 ;; *) r=1 ;; esac
+  st "$r" 0 "--body-check runs figure_block_check and refuses on its rc (card 7)"
+  st "$(declare -f figure_block_check | grep -c 'figure_block.py verify')" 1 "figure_block_check calls figure_block.py verify"
   case "$bc" in *'vline=$(privacy_line); vr=$?'*'[ "$r" -ne 0 ] || r=$vr'*) r=0 ;; *) r=1 ;; esac
   st "$r" 0 "--body-check runs privacy_line and refuses on its rc (P78)"
   case "$bc" in *'bline=$(body_privacy_line "$2"); br=$?'*'[ "$r" -ne 0 ] || r=$br'*) r=0 ;; *) r=1 ;; esac
@@ -4603,6 +4616,11 @@ if [ -n "$BODY" ] && [ "$BODY" != "--self-test" ]; then
   step "figures" $? "$(tail -1 /tmp/prepr-fig.$$)"
   rm -f /tmp/prepr-fig.$$
 
+  # --- 7a2. every registered figure block is what the registry renders at HEAD.
+  figure_block_check "$BODY" >/tmp/prepr-fb.$$ 2>&1
+  step "figure blocks" $? "$(tail -1 /tmp/prepr-fb.$$)"
+  rm -f /tmp/prepr-fb.$$
+
   # --- 7e. every finding the body records names a destination on the round's
   # roster branch, freshly fetched (`carry_line` above): pr-contract's carry check.
   CARRY_LINE=$(carry_line "$BODY"); CARRY_RC=$?

## Before you return the verdict (P275)
Run `python3 -I tools/audit/carry_audit.py check --body <PR body file> --comments <file holding [{"id": 0, "body": <verdict.md text>}]>`. Give every reported item its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>`;
an evidence line flagged by its wording takes `Carry: dismissed: evidence, not a finding`. Return the verdict only at rc 0.
