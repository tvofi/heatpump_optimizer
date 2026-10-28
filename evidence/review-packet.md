# Review packet #2923
head: b04f9e93bd4ec068436a90f000a98851ed44318c
base: beb570c817c4efcae0d5f6f4bba52f3383baf8db

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: pending
arm id=122993688855 skipped
cancel-superseded id=122993689657 queued
prelude id=122993690148 queued
refresh id=122993690133 queued

## Refusals
none

## Advisories
none

## carry_audit at the head
CARRY-AUDIT: 0 finding item(s): 0 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
ok         bash tools/pr/app_push.sh --self-test
             `tools/pr/app_push.sh` is in the tree at this head
  ok         python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)
             `tests/closure.py` is in the tree at this head
  ok         python3 tests/structure.py
             `tests/structure.py` is in the tree at this head
  ok         tests/run.sh
             `tests/run.sh` is in the tree at this head
  ok         GATE_SCOPE=auto PYTHONPATH=tests/hastub bash tests/run.sh
             `tests/run.sh` is in the tree at this head
  ok         tests/layout.py
             `tests/layout.py` is in the tree at this head
  ok         tests/harness_headers.py
             `tests/harness_headers.py` is in the tree at this head
  ok         bash tools/pr/prepr.sh <body>
             `tools/pr/prepr.sh` is in the tree at this head
  ok         tools/audit/seat/seat_venv.sh
             `tools/audit/seat/seat_venv.sh` is in the tree at this head
  ok         tools/pr/app_push.sh
             `tools/pr/app_push.sh` is in the tree at this head

FIGURES: 10 resolved, 0 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
none

## Three-dot diff
diff --git a/dev/programme/delivery/2923.md b/dev/programme/delivery/2923.md
new file mode 100644
index 000000000..9ced10513
--- /dev/null
+++ b/dev/programme/delivery/2923.md
@@ -0,0 +1 @@
+- [#2923](https://github.com/tvofi/heatpump_optimizer/pull/2923) — **open**, R10-FLY-ROWONLY-BASE: row-only body check passes --base (R10-FLY-ROWONLY-BASE)
diff --git a/tools/pr/app_push.sh b/tools/pr/app_push.sh
index 91333c173..9b336b114 100644
--- a/tools/pr/app_push.sh
+++ b/tools/pr/app_push.sh
@@ -246,7 +246,9 @@ sys.exit(not (j > i and prefix(live, b[i:j]).rstrip("\n") == b.rstrip("\n")))' "
 # pinned to the live head, which passed them: one added row moves no claim
 # file, VERSION, code or closure, and (d) leaves the body the live one plus
 # the caller's note -- so pr-contract's and prepr's figure lint and preflight,
-# which read only that body and that tree, are not re-run either.
+# which read only that body and that tree, are not re-run either. The contract
+# gets prepr's own `--base` (its BASE, the same merge base): without it a diff
+# touching a `*_budgets.json` is refused unread (R10-FLY-ROWONLY-BASE).
 row_only_checks() { # worktree body head title -> rc 0 when both checks pass
   ( cd "$1" || exit 1
     base=$(git merge-base origin/main HEAD 2>/dev/null) || { echo "no merge base with origin/main" >&2; exit 1; }
@@ -255,7 +257,7 @@ row_only_checks() { # worktree body head title -> rc 0 when both checks pass
       || { rm -f "$p" "$e"; echo "the changed-path list did not derive from $base...HEAD" >&2; exit 1; }
     lint=tools/policy/policy_lint.mjs; test -f .claude/workflows/policy_lint.mjs && lint=.claude/workflows/policy_lint.mjs
     tok=${GITHUB_TOKEN:-${GH_TOKEN:-}}; [ -n "$tok" ] || tok=$(gh auth token 2>/dev/null) || tok=""
-    GH_TOKEN=$tok node "$lint" --pr-body "$2" --head "$3" --title "$4" --paths-file "$p" --existing-file "$e"; rc=$?
+    GH_TOKEN=$tok node "$lint" --pr-body "$2" --head "$3" --title "$4" --paths-file "$p" --existing-file "$e" --base "$base"; rc=$?
     rm -f "$p" "$e"; [ "$rc" = 0 ] || exit "$rc"
     python3 -I tools/audit/carry_audit.py check --body "$2" )
 }
@@ -1130,6 +1132,27 @@ reset_q; (cd "$Q/wt" && ensure_row . 7 "$(row_line 7 o/r t)" >/dev/null)
 st "$(cp "$W/qlive.md" "$W/qbody.md"; row_only_verdict "$Q/wt" "$(python3 -c 'import json, sys
 print(json.dumps([{"number": 7, "title": "t", "head": {"sha": sys.argv[1]}, "body": "## Head\n\nx\n"}]))' "$(git -C "$Q/wt" rev-parse live)")" "$W/qbody.md")" \
   "the body file is not the live pull-request body under one new \`## Head\` note" "real git: a body that is not the live one under one new note runs prepr"
+# R10-FLY-ROWONLY-BASE: the production row_only_checks, extracted from this
+# file, with the REAL contract (policy_lint.mjs --pr-body and its
+# budget_raise_gate.py) on a throwaway repo whose branch moves a cap in
+# tests/structure_budgets.json, as every ratchet pull request's does. Without
+# `--base` the contract refuses any budget path as "was not read" (#2912,
+# #2913), so a lowered cap must pass and a raised one stay refused as a raise.
+eval "$(sed -n '/^row_only_checks() {/,/^}/p' "$SELF")"
+Z="$W/rbase"
+throwaway_git_init "$Z/wt" -q -b main && (cd "$Z/wt" && mkdir -p tests tools/audit && cp -R "$(dirname -- "$SELF")/../policy" tools/ \
+  && cp "$W/tool-wt/tests/layout.py" "$W/tool-wt/tests/layout.json" "$(dirname -- "$SELF")/../../tests/structure_budgets.json" tests/ \
+  && cp "$W/tool-wt/tools/audit/carry_audit.py" tools/audit/ && rgit add -A && rgit commit -qm base && rgit update-ref refs/remotes/origin/main HEAD)
+zcap() { # max_cc delta -> rc and the contract's output of row_only_checks on a branch moving that cap
+  (cd "$Z/wt" && rgit checkout -q -B fix origin/main && python3 -c 'import json, sys
+p = "tests/structure_budgets.json"; d = json.load(open(p)); d["max_cc"] += int(sys.argv[1]); open(p, "w").write(json.dumps(d, indent=2) + "\n")' "$1" \
+    && rgit commit -qam cap)
+  sed -e "s/^\`0\{40\}\`$/\`$(git -C "$Z/wt" rev-parse HEAD)\`/" -e '/^## Forward-carry$/,/^## /s#^`.*`$#`tests/layout.py`#' \
+    "$(dirname -- "$SELF")/../policy/fixtures/policy-rot/prepr/good.md" > "$Z/body.md"
+  STUB=$Z GH_TOKEN=stub-no-network row_only_checks "$Z/wt" "$Z/body.md" "$(git -C "$Z/wt" rev-parse HEAD)" t > "$Z/out" 2>&1; echo "rc=$?"
+}
+st "$(zcap -1)$(grep -c 'was not read' "$Z/out")" rc=00 "real contract: a row-only push onto a pull request that lowers a budget cap passes (it was refused as \"was not read\": no --base)"
+st "$(zcap 1)$(grep -c 'budget_raise_gate.py refuses this body' "$Z/out")$(grep -c 'was not read' "$Z/out")" rc=110 "null control: one that raises the cap is still refused, as a raise owing \`## Raise justification\`"
 
 # R10-RECARRY-HEAD: each recarry's note names its head under the `## Head`
 # HEADING, read by the reader pr-contract runs (policy_lint.mjs --pr-body).

