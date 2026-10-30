# Review packet #2977
head: 967abc3e9c7ca6d224ba5d55cee77145d109ea3b
base: 1148ee635e8278ebbb033b524d54001b2a89218c

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: green
CodeQL id=123951892505 success
arch-score / arch-score id=123951662185 success
arm id=123951529675 skipped
budget-raise-gate / budget-raise-gate id=123951662271 success
cancel-superseded id=123951527607 success
codeql / Analyze (actions) id=123951661987 success
codeql / Analyze (javascript-typescript) id=123951661950 success
codeql / Analyze (python) id=123951662001 success
gate id=123965140490 success
governance / delivery-status id=123951662428 success
governance / delivery-status-publish id=123951664362 skipped
governance / env-matrix id=123951662061 success
governance / instrument-self-tests id=123951662042 success
governance / policy-docs id=123951662396 success
governance / record id=123951663473 skipped
governance / wave-script id=123951662106 success
hassfest / hassfest id=123951661961 success
kernel-points id=123951663771 skipped
pr-contract / pr-contract id=123964939570 success
prelude id=123951527379 success
refresh id=123951527708 success
tests / arch-instrument id=123951811222 success
tests / briefs id=123951662045 success
tests / browser id=123951811158 success
tests / ci-ratchet id=123961791376 skipped
tests / claims-autofix id=123955936575 skipped
tests / closure-scope id=123951662003 success
tests / closures id=123951811291 success
tests / closures-autofix id=123957794910 skipped
tests / coverage id=123951811325 success
tests / coverage-ratchet id=123961789473 success
tests / fast (3.14) id=123951811250 success
tests / graders-head-copy id=123961789429 success
tests / lane-proofs id=123961789494 success
tests / mutation id=123951662027 success
tests / mutation-autofix id=123951921573 skipped
tests / mutation-pins id=123951920391 skipped
tests / nightly-ha id=123951812982 skipped
tests / nightly-status id=123951662005 success
tests / replay id=123951813747 skipped
tests / typing id=123951811177 success
validate / validate-hacs id=123951662010 success

## Refusals
none

## Advisories
none

## carry_audit at the head
CARRY-AUDIT: 0 finding item(s): 0 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
ok         bash tools/pr/app_approve.sh --carry <merge>^1 <merge> origin/main
             `tools/pr/app_approve.sh` is in the tree at this head
  unverified python3 -I <git show origin/main:tests/env_drift.py> --merge-claim-file O A B 7 tests/golden/claimed_drift.txt
             the path `<git` is a template or an expansion, not a literal
  ok         bash tools/pr/app_approve.sh --self-test
             `tools/pr/app_approve.sh` is in the tree at this head
  ok         python3 tools/audit/seat/review_carry.py --self-test
             `tools/audit/seat/review_carry.py` is in the tree at this head
  ok         python3 tests/closure.py select --diff da066609fb1f076333d064f5f49612998253f7ce
             `tests/closure.py` is in the tree at this head
  ok         tests/entities.py
             `tests/entities.py` is in the tree at this head
  ok         PYTHONPATH=tests/hastub python3 tests/entities.py
             `tests/entities.py` is in the tree at this head
  ok         python3 tests/structure.py
             `tests/structure.py` is in the tree at this head
  ok         PREPR_SKIP_CLOSURES=1 bash tools/pr/prepr.sh <this body>
             `tools/pr/prepr.sh` is in the tree at this head
  unverified git grep -l -- '--carry' -- tools/ .github/
             `git grep` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  ok         tools/pr/app_approve.sh
             `tools/pr/app_approve.sh` is in the tree at this head
  ok         tools/audit/seat/review_carry.py
             `tools/audit/seat/review_carry.py` is in the tree at this head
  ok         tools/policy/policy_lint.mjs
             `tools/policy/policy_lint.mjs` is in the tree at this head
  ok         tools/pr/merge_main_bot.py
             `tools/pr/merge_main_bot.py` is in the tree at this head
  unverified git grep -n "other than the union"
             `git grep` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals

FIGURES: 12 resolved, 3 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
none

## Three-dot diff
diff --git a/dev/governance/roles/orchestrator.md b/dev/governance/roles/orchestrator.md
index 1f078aee1..00cc225d6 100644
--- a/dev/governance/roles/orchestrator.md
+++ b/dev/governance/roles/orchestrator.md
@@ -228,8 +228,8 @@ Through the roster seat, on `standing-roster.md`'s terms.
 - A `merge` verdict from a reviewer that measured **this** head, or a **carry**,
   with no reviewer turn (tvofi, 2026-10-01): `tools/pr/app_approve.sh --carry
   <verdict> <head>` reports carried, the files `git diff --name-only <verdict>
-  <head>` names miss the branch's own diff, and each claim file a pure union of
-  both sides. Anything else is a resolution delta for the same reviewer.
+  <head>` names miss the branch's own diff. Anything else is a resolution delta
+  for the same reviewer.
 - CI green at the verdicted head, landed onto a green `main` by
   `tools/audit/seat/merge_train.py batch` (tvofi, 2026-10-07), the only bypass:
   a proved batch merges while `main`'s tree equals its proof's; one entry merges
diff --git a/dev/programme/delivery/2977.md b/dev/programme/delivery/2977.md
new file mode 100644
index 000000000..869e82fa5
--- /dev/null
+++ b/dev/programme/delivery/2977.md
@@ -0,0 +1 @@
+- [#2977](https://github.com/tvofi/heatpump_optimizer/pull/2977) — **open**, R10-FLY-CARRY-CLAIM-DRIVER: a claim file the driver resolved carries (R10-FLY-CARRY-CLAIM-DRIVER)
diff --git a/tools/audit/seat/instruments/app_approve.sh.md b/tools/audit/seat/instruments/app_approve.sh.md
index 1b49b0f33..e4aa0de07 100644
--- a/tools/audit/seat/instruments/app_approve.sh.md
+++ b/tools/audit/seat/instruments/app_approve.sh.md
@@ -4,7 +4,8 @@
   exact head SHA, only on a `merge` verdict for that SHA from an allowlisted
   account (`--carry` re-approves a carried verdict: no branch-authored commit
   in `git rev-list <verdict>..<head> --not main`, every merge git's automatic
-  one and each `claimnotes` file a pure union of its parents' lines). When:
+  one and each `claimnotes` file a pure union of its parents' lines or main's
+claim-driver output on them). When:
   landing a
   non-code-owned verdicted PR whose head the reviewer measured. Refusal: a
   head SHA that is not the PR's current head, or a verdict whose SHA or
diff --git a/tools/audit/seat/instruments/review_carry.py.md b/tools/audit/seat/instruments/review_carry.py.md
index 2947d525e..f2ac1bd7d 100644
--- a/tools/audit/seat/instruments/review_carry.py.md
+++ b/tools/audit/seat/instruments/review_carry.py.md
@@ -6,7 +6,7 @@
   exactly one `CARRY`/`FRESH-REVIEW` (`git rev-list --count <reviewed>..<new>
   --not origin/main`; CARRY needs zero, or every commit in it a merge, and
   then `tools/pr/app_approve.sh --carry` carrying the range — each merge
-  git's automatic one, claim files a pure union, the branch's own diff equal
+  git's automatic one, claim files a pure union or main's driver output, the branch's own diff equal
   — asked, never copied, so the two cannot answer one range oppositely; a
   merge of the branch's own previous head, update_pr.sh's re-cut, passes,
   and a hand-resolved conflict does not). When: before
diff --git a/tools/audit/seat/review_carry.py b/tools/audit/seat/review_carry.py
index 8a4289375..a37da51d8 100755
--- a/tools/audit/seat/review_carry.py
+++ b/tools/audit/seat/review_carry.py
@@ -18,7 +18,8 @@ change. Zero, or a count whose commits are all merges, is no branch-authored
 commit; what a merge can still author is its resolution, so the range then
 carries only where `tools/pr/app_approve.sh --carry` carries it -- each merge
 git's own automatic merge of its parents outside main's driver files, each
-claim file the pure union of both sides, and the branch's own diff equal at
+claim file the pure union of both sides or main's claim-driver output on
+them, and the branch's own diff equal at
 both heads -- and this prints CARRY. A merge of the branch's own previous
 head, the shape update_pr.sh re-cuts one into, passes all three. A
 hand-resolved conflict, a line a merge adds of its own, or a main change that
@@ -114,7 +115,8 @@ APP_APPROVE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
 def app_approve_carry(repo, reviewed, new, main):
     """-> None when app_approve.sh --carry carries reviewed -> new, else its
     reason: each merge git's automatic one outside main's driver files, each
-    claim file the pure union of both sides, the branch's own diff equal."""
+    claim file the pure union of both sides or main's claim-driver output on
+    them, the branch's own diff equal."""
     proc = subprocess.run(["bash", APP_APPROVE, "--carry", reviewed, new, main],
                           cwd=repo, capture_output=True, text=True)
     out = proc.stdout.strip()
@@ -411,8 +413,8 @@ def self_test():
     v, _, _, _ = answer(reviewed2, auto, main=main_q)
     check("the same merge, git's automatic result, answers CARRY", v, CARRY)
     # A claim file (main's `merge=claimnotes`) is left out of the tree
-    # comparison and must resolve to the pure union of both sides, as
-    # app_approve.sh --carry requires.
+    # comparison and must resolve to the pure union of both sides (or main's
+    # driver output on them), as app_approve.sh --carry requires.
     _t(seat, "checkout", "-q", "-b", "main-claim", main_c)
     with open(os.path.join(seat, "claims.txt"), "w") as fh:
         fh.write("base-claim\nmain-claim\n")
diff --git a/tools/pr/app_approve.sh b/tools/pr/app_approve.sh
index 4969ed21d..43a4167e3 100755
--- a/tools/pr/app_approve.sh
+++ b/tools/pr/app_approve.sh
@@ -64,8 +64,9 @@
 # is no change (tvofi, 2026-10-27: "if there are no code changes, the
 # previous review can be carried"); (3) each merge's tree is git's automatic
 # merge of its parents outside the driver files below, and it resolves each
-# `merge=claimnotes` file to a pure union of its two parents' lines, because
-# a resolution that drops, adds or rewrites a line is content no review
+# `merge=claimnotes` file to a pure union of its two parents' lines or to
+# exactly what main's claim driver writes on them (P290), because any other
+# resolution that drops, adds or rewrites a line is content no review
 # measured; and (4) the branch's own diff against its merge base with main is
 # byte-identical
 # at V and at H, read with two relaxations measured over round 9's window
@@ -225,6 +226,23 @@ bot_paths() { # subject -> one pathspec per line, nothing for an unknown subject
   esac
 }
 
+# claim_driver_wrote <main ref> <merge> <parent 1> <parent 2> <path>: 0 only when
+# main's claim driver resolves <path> at (merge base, parent 1, parent 2) and its
+# output is byte-equal to <path> at <merge>. Quiet, like merge-tree in `carry`.
+claim_driver_wrote() {
+  local m=$1 c=$2 a=$3 b=$4 p=$5 o d r=1
+  o=$(git merge-base "$a" "$b" 2>/dev/null) || return 1
+  d=$(mktemp -d) || return 1
+  git show "$m:tests/env_drift.py" > "$d/driver.py" 2>/dev/null \
+    && { git show "$o:$p" > "$d/O" 2>/dev/null || :; } \
+    && { git show "$a:$p" > "$d/A" 2>/dev/null || :; } \
+    && { git show "$b:$p" > "$d/B" 2>/dev/null || :; } \
+    && python3 -I "$d/driver.py" --merge-claim-file "$d/O" "$d/A" "$d/B" 7 "$p" >/dev/null 2>&1 \
+    && git show "$c:$p" 2>/dev/null | cmp -s - "$d/A" && r=0
+  rm -rf "$d"
+  return $r
+}
+
 # carry <verdict sha> <head sha> <main ref>: prints the reason; 0 only on a carry.
 carry() {
   local v=$1 h=$2 main=$3 c ps ae subj p mv mh t x y b ba bt e cp got want
@@ -282,12 +300,20 @@ carry() {
       # pure union of both sides is the only resolution that changes nothing:
       # it carries the branch's note and main's. A line dropped, added or
       # rewritten is content no review measured, so it is a change.
+      # Git's own resolution is the other one that changes nothing, and the
+      # driver does not union: it takes the claim list from the side that
+      # changed it, so a claim main cleared stays cleared (P290). So the file
+      # also passes byte-equal to what main's driver writes on the parents'
+      # merge base and the two parents. Main's driver, as main's
+      # `.gitattributes` above: a branch's own driver would grade itself.
+      # A driver refusal (both sides rewrote the claim list) writes nothing
+      # that can match, which leaves the union deciding.
       while IFS= read -r p; do
         [ -z "$p" ] && continue
         got=$(git show "$c:$p" 2>/dev/null | awk 'NF' | sort -u)
         want=$({ git show "$1:$p" 2>/dev/null; git show "$2:$p" 2>/dev/null; } | awk 'NF' | sort -u)
-        [ "$got" = "$want" ] \
-          || { echo "$c resolves $p to something other than the union of its parents"; return 1; }
+        [ "$got" = "$want" ] || claim_driver_wrote "$main" "$c" "$1" "$2" "$p" \
+          || { echo "$c resolves $p to something other than the union of its parents or main's driver output on them"; return 1; }
       done <<<"$cp"
     elif [[ $subj != ci:* ]] && [ -z "$(bot_paths "$subj")" ]; then
       echo "$c is a commit of the branch's own ($subj)"; return 1
@@ -364,7 +390,7 @@ carry() {
   norm() { "${d[@]}" "$1" "$2" -- . ${x[@]+"${x[@]}"} | sed -e '/^index /d' -e 's/^@@ .*/@@/'; }
   cmp -s <(norm "$mv" "$v") <(norm "$mh" "$h") \
     || { echo "the branch's own diff differs: $mv..$v against $mh..$h"; return 1; }
-  echo "no branch-authored commit in the range, every merge the automatic one with its claim files a pure union of both sides, and the branch's own diff compares equal"
+  echo "no branch-authored commit in the range, every merge the automatic one with its claim files a pure union of both sides or main's driver output on them, and the branch's own diff compares equal"
 }
 
 cleanup() {
@@ -1636,6 +1662,49 @@ H_CR=$(claim_merge '# note\nc1 # one\nc2 # two\nc3 # three, reworded\nc4 # four\
 ( cd "$R" && bash "$SELF" --carry "$VC" "$H_CR" main ) > "$W/carry.out" 2>&1
 st $? 1 "NO CARRY: a claim resolution that rewrites a line"
 st "$(grep -c "union of its parents" "$W/carry.out")" 1 "refused as a claim resolution that is not the union"
+# The real driver (P290): it takes the claim list from the one side that
+# changed it, so a claim main cleared stays cleared and the union rule above
+# refuses git's own resolution. A merge whose claim file is exactly what main's
+# driver writes on (merge base, first parent, second parent) carries; one
+# hand-added claim line beside that output does not.
+RD="$W/claimdrv"; throwaway_git_init "$RD" -q -b main
+( cd "$RD" || exit 2
+  git config merge.claimnotes.name claims
+  git config merge.claimnotes.driver 'python3 tests/env_drift.py --merge-claim-file %O %A %B %L %P'
+  mkdir -p tests/golden
+  cp "$(cd "$(dirname "$SELF")/../.." && pwd)/tests/env_drift.py" tests/env_drift.py
+  printf 'tests/golden/claimed_drift.txt merge=claimnotes\n' > .gitattributes
+  printf '# note\n# claims-for: 1.0.0\nc1 # one\n' > tests/golden/claimed_drift.txt
+  git add -A; git commit -qm main0
+  git checkout -qb fix
+  printf '# note\n# the fix keeps c1\n# claims-for: 1.0.0\nc1 # one\n' > tests/golden/claimed_drift.txt
+  git commit -qam "fix: own"; git rev-parse HEAD > ../claimdrv.v
+  git checkout -q main
+  printf '# note\n# main clears c1\n# claims-for: 1.0.0\n' > tests/golden/claimed_drift.txt
+  git commit -qam "main: clears c1" )
+VD=$(cat "$W/claimdrv.v")
+H_DR=$( cd "$RD" && git checkout -q --detach "$VD" && git merge -q --no-ff --no-edit main >/dev/null 2>&1 \
+  && git rev-parse HEAD )
+st "$( cd "$RD" && git show "$H_DR:tests/golden/claimed_drift.txt" | grep -c '^c1')" 0 \
+  "the fixture's driver resolved the merge, keeping main's cleared claim cleared"
+( cd "$RD" && bash "$SELF" --carry "$VD" "$H_DR" main ) > "$W/carry.out" 2>&1
+st $? 0 "CARRY: a claim file resolved by main's driver, which is not the union"
+H_DA=$( cd "$RD" && git checkout -q --detach "$VD" && git merge -q --no-ff --no-edit --no-commit main >/dev/null 2>&1
+  printf 'c9 # by hand\n' >> tests/golden/claimed_drift.txt; git add tests/golden/claimed_drift.txt
+  git commit -q --no-edit && git rev-parse HEAD )
+( cd "$RD" && bash "$SELF" --carry "$VD" "$H_DA" main ) > "$W/carry.out" 2>&1
+st $? 1 "NO CARRY: the driver's resolution with one hand-added claim line"
+st "$(grep -c "union of its parents" "$W/carry.out")" 1 "refused as neither the union nor the driver's output"
+# The driver is main's, never the head's: a branch whose own driver writes
+# nothing (so its output is the first parent's file) cannot carry a merge that
+# dropped main's side of the claim file by hand.
+VF=$( cd "$RD" && git checkout -q --detach "$VD" && printf 'import sys\nsys.exit(0)\n' > tests/env_drift.py \
+  && git commit -qam "fix: a driver that writes nothing" && git rev-parse HEAD )
+H_DF=$( cd "$RD" && git checkout -q --detach "$VF" && git merge -q --no-ff --no-edit --no-commit main >/dev/null 2>&1
+  git checkout "$VF" -- tests/golden/claimed_drift.txt; git commit -q --no-edit && git rev-parse HEAD )
+( cd "$RD" && bash "$SELF" --carry "$VF" "$H_DF" main ) > "$W/carry.out" 2>&1
+st $? 1 "NO CARRY: main's side dropped by hand, which only the head's own driver would write"
+st "$(grep -c "union of its parents" "$W/carry.out")" 1 "refused on main's driver, not the head's"
 EVV="$W/ev-v"; mkdir -p "$EVV"; printf 'fix review at head %s\n' "$V" > "$EVV/verdict.md"
 CARRYV="[$(comment 2 "Fix review: merge $V" "$APPR" NONE "evidence: $EVV")]"
 setpr "$H_MERGE"; mkcase carry open false "$H_MERGE" "$CARRYV"

