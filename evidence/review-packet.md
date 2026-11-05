# Review packet #3221
head: fd0d130a7e040c64da4fcd93c1ca2aa2a2fc9f56
base: 79f765e6b2e0f97e61b57d7b605fc4e70b4bf21e

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: red
CodeQL id=127154947698 neutral
arch-score / arch-score id=127154477331 success
arm id=127154348501 skipped
budget-raise-gate / budget-raise-gate id=127154477082 success
cancel-superseded id=127155639890 success
codeql / Analyze (actions) id=127154477157 success
codeql / Analyze (javascript-typescript) id=127154477203 success
codeql / Analyze (python) id=127154477352 in_progress
governance / delivery-status id=127154477191 failure
governance / delivery-status-publish id=127154479008 skipped
governance / env-matrix id=127154477193 success
governance / instrument-self-tests id=127154477241 in_progress
governance / policy-docs id=127154477278 success
governance / record id=127154480389 skipped
governance / wave-script id=127154477446 success
hassfest / hassfest id=127154477176 success
kernel-points id=127154478782 skipped
prelude id=127155640297 in_progress
refresh id=127155640373 success
tests / arch-instrument id=127154676494 success
tests / briefs id=127154477097 success
tests / browser id=127154676272 success
tests / claims-autofix id=127157003618 skipped
tests / closure-scope id=127154476868 success
tests / closures id=127154676180 in_progress
tests / coverage id=127154676269 in_progress
tests / fast (3.14) id=127154676296 success
tests / mutation id=127154477214 success
tests / mutation-autofix id=127154942172 skipped
tests / mutation-pins id=127154942554 skipped
tests / nightly-ha id=127154678307 skipped
tests / nightly-status id=127154477012 failure
tests / replay id=127154679555 skipped
tests / typing id=127154676217 success
validate / validate-hacs id=127154476816 success

## Refusals
none

## Advisories
hot-file: HPO_BUS_TRAIN_STATE is unset, so every merge verdict reads unboarded

## carry_audit at the head
CARRY-AUDIT: 0 finding item(s): 0 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
ok         bash tools/audit/seat/pr_args.sh --self-test
             `tools/audit/seat/pr_args.sh` is in the tree at this head
  ok         bash tools/audit/seat/open_pr.sh --self-test
             `tools/audit/seat/open_pr.sh` is in the tree at this head
  ok         bash tools/audit/seat/update_pr.sh --self-test
             `tools/audit/seat/update_pr.sh` is in the tree at this head
  ok         bash tools/audit/seat/pr_args.sh --pushers
             `tools/audit/seat/pr_args.sh` is in the tree at this head
  ok         bash tools/pr/app_push.sh --self-test
             `tools/pr/app_push.sh` is in the tree at this head
  ok         bash tools/pr/prepr.sh --self-test
             `tools/pr/prepr.sh` is in the tree at this head
  ok         python3 tests/structure.py
             `tests/structure.py` is in the tree at this head
  ok         python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)
             `tests/closure.py` is in the tree at this head
  unverified git diff --quiet $(git merge-base origin/main HEAD)...HEAD -- tests/golden/claimed_drift.txt tests/golden/card_claimed_drift.txt VERSION RELEASE_NOTES.md custom_components/*/manifest.json
             `git diff` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals

FIGURES: 8 resolved, 1 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
none

## Three-dot diff
diff --git a/dev/programme/delivery/3221.md b/dev/programme/delivery/3221.md
new file mode 100644
index 000000000..e8466bb84
--- /dev/null
+++ b/dev/programme/delivery/3221.md
@@ -0,0 +1 @@
+- [#3221](https://github.com/tvofi/heatpump_optimizer/pull/3221) — **open**, R10-HANDOFF-PATH part 1: reuse the fixer's prepr receipt at open and update (R10-HANDOFF-PATH)
diff --git a/tools/audit/seat/body_push.sh b/tools/audit/seat/body_push.sh
index 64ecdaf70..3f7484f0f 100644
--- a/tools/audit/seat/body_push.sh
+++ b/tools/audit/seat/body_push.sh
@@ -12,6 +12,19 @@
 set -euo pipefail
 TOPIC=${1:?topic}; BODY=${2:?body file}; NOTE=${3:-}
 REF=handoff-body/$TOPIC
+# The receipt (P386): prepr.sh's last passing full run in this checkout wrote
+# `<sha> <tree>` to hpo-prepr-receipt in its git dir. When that sha is the code
+# head this body describes and that tree is the head's, the body commit carries
+# it as a `Prepr: <sha> <tree>` trailer, which app_push.sh --reuse reads so the
+# run is not repeated at open or update. Anything else carries none.
+prepr_trailer() { # checkout root, code head -> `Prepr: <sha> <tree>`, or nothing
+  local f s t
+  f=$(git -C "$1" rev-parse --absolute-git-dir 2>/dev/null)/hpo-prepr-receipt
+  [ -f "$f" ] && read -r s t _ < "$f" || return 0
+  [[ $s =~ ^[0-9a-f]{40}$ && $t =~ ^[0-9a-f]{40}$ ]] || return 0
+  [ "$s" = "$2" ] && [ "$t" = "$(git -C "$1" rev-parse "$2^{tree}" 2>/dev/null)" ] || return 0
+  printf 'Prepr: %s %s' "$s" "$t"
+}
 [ -f "$BODY" ] || { echo "body_push: no body at $BODY" >&2; exit 2; }
 [ -z "$NOTE" ] || [ -f "$NOTE" ] || { echo "body_push: no note at $NOTE" >&2; exit 2; }
 # The handoff gate (dev/audit/rca/R10-HANDOFF-PREPR-BOUNCE.md, M2): the static
@@ -106,6 +119,12 @@ rm -f "${TMPDIR:-/tmp}/body_push.$$"
 # naming the handoff it applies (V147). A result body names none.
 MSG="body: $TOPIC"
 [ -z "$HREF" ] || MSG=$(printf 'body: %s\n\nCode: %s' "$TOPIC" "$HREF")
+PT=""; [ -z "$HREF" ] || PT=$(prepr_trailer "$ROOT" "$HREF")
+if [ -n "$PT" ]; then
+  MSG=$(printf '%s\n%s' "$MSG" "$PT"); echo "body_push: $PT (prepr's receipt at this code head)"
+elif [ -n "$HREF" ]; then
+  echo "body_push: no Prepr: trailer -- no receipt of a passing full prepr.sh run at ${HREF:0:12} in this checkout, so the open runs the full prepr"
+fi
 # shellcheck disable=SC2086 # $P is empty or exactly "-p <sha>"
 C=$(git commit-tree "$TREE" $P -m "$MSG")
 # The topic names the ref and the message: refuse one that names this host
diff --git a/tools/audit/seat/open_pr.sh b/tools/audit/seat/open_pr.sh
index 8d8a8ddcb..0baf9c450 100755
--- a/tools/audit/seat/open_pr.sh
+++ b/tools/audit/seat/open_pr.sh
@@ -4,7 +4,9 @@
 # The PR worktree and body live under $HPO_STATE_DIR/pr/<topic> (default ~/.local/state/hpo), and the
 # seat venv seat_venv.sh builds there comes first on PATH.
 # Successor of handoff_push.sh's open path: always merges origin/main, names the roster group in the row.
-# The row push (p2) asks app_push.sh for --row-only, so an open runs one full prepr, not two (P53),
+# The body push (p1) asks app_push.sh for --reuse: the fixer's receipted prepr, carried as the
+# handoff body's `Prepr:` trailer, is not repeated over its clean merge with main (P386).
+# The row push (p2) asks app_push.sh for --row-only, so an open runs at most one full prepr (P53),
 # and lands seconds after the PR rather than a prepr later, before CI on p1 can report a red the body
 # was never asked to answer (#2625, #2629). Once the PR exists, any exit before its row is pushed (a
 # refused row push, a step errexit stops, a stop signal) returns the worktree to the pushed head and
@@ -115,8 +117,10 @@ python3 "$PRT/ci_predict.py" --rekey-body $D/body.md --from $C || echo "open_pr:
 if test -f tools/audit/app_push.sh; then _push=tools/audit/app_push.sh; else _push=tools/pr/app_push.sh; fi
 # Asynchronous, so a stop signal interrupts the `wait` and the EXIT trap reaps
 # the tree (pr_args.sh's why).
-{ pr_push_hold; PREPR_SKIP_CLOSURES=1 PYTHONPATH=tests/hastub bash "$_push" $R $WT $BR $D/body.md $ISS > $D/p1.log 2>&1 & } 9>>"${PR_PUSH_LOCK:-/dev/null}"
+RU=--reuse  # mut:opreuse
+{ pr_push_hold; PREPR_SKIP_CLOSURES=1 PYTHONPATH=tests/hastub bash "$_push" ${RU-} $R $WT $BR $D/body.md $ISS > $D/p1.log 2>&1 & } 9>>"${PR_PUSH_LOCK:-/dev/null}"
 pr_wait $! $D/p1.log
+grep -h '^app_push: REUSE:' $D/p1.log || :
 PR_PUSHED=$(git rev-parse HEAD)
 N=$(grep -oE 'pull request #[0-9]+' $D/p1.log | head -1 | grep -oE '[0-9]+')
 pr_exit_trap "op_close_unrowed; $PR_EXIT_FIRST"  # mut:trapclose
diff --git a/tools/audit/seat/pr_args.sh b/tools/audit/seat/pr_args.sh
index c7e40aa88..177a289c2 100644
--- a/tools/audit/seat/pr_args.sh
+++ b/tools/audit/seat/pr_args.sh
@@ -366,6 +366,8 @@ tools/policy/check-wave-script.mjs mention: a test title
 tools/policy/friction_issues.mjs mention: comments
 tools/audit/seat/gh_read.py mention: its docstring cites the read-back rule of app_push.sh; it runs no subprocess
 tools/audit/seat/body_patch.sh mention: comments; it PATCHes a body through app_mint.sh and runs no push
+tools/audit/seat/body_push.sh mention: comments; it writes the Prepr: trailer app_push.sh --reuse reads, and runs no push
+tools/pr/prepr.sh mention: comments; it honours the receipt app_push.sh --reuse passes it, and runs no push
 tools/pr/app_mint.sh mention: comments; sourced by app_push.sh, it launches nothing
 tools/policy/policy_lint.mjs mention: a refusal message'
 pr_pushers() { # [<root>] [<rev>]: the census; one line per seam, exit 1 on any OPEN
@@ -576,7 +578,7 @@ STUB
   for k in dirt orig; do
     [ -e "$t/fix$k" ] && continue
     git -C "$o" checkout -q -b "handoff/$k" "$base" && mkdir -p "$o/tools/pr" && printf 'b\n' > "$o/b" \
-      && if [ "$k" = dirt ]; then printf '#!/bin/bash\n: > "$2/dirt"; exit 1\n'; else printf '#!/bin/bash\ngit -C "$2" push -q origin "$3"; exit 1\n'; fi > "$o/tools/pr/app_push.sh" \
+      && if [ "$k" = dirt ]; then printf '#!/bin/bash\n[ "$1" != --reuse ] || shift\n: > "$2/dirt"; exit 1\n'; else printf '#!/bin/bash\n[ "$1" != --reuse ] || shift\ngit -C "$2" push -q origin "$3"; exit 1\n'; fi > "$o/tools/pr/app_push.sh" \
       && git -C "$o" add b tools/pr/app_push.sh && git -C "$o" commit -q -m "code $k" \
       && git -C "$o" update-ref "refs/heads/handoff-body/$k" "$body" && git -C "$o" checkout -q main && touch "$t/fix$k"
   done
@@ -1096,7 +1098,7 @@ print("free")' "$1"
     git -C "$o" checkout -q -b handoff/r "$base" && mkdir -p "$o/tools/pr" && printf 'b\n' > "$o/b" \
       && cat > "$o/tools/pr/app_push.sh" <<'STUB'
 #!/bin/bash
-D=$STUB_DIR; printf '%s\n' "$*" >> "$D/argv"; [ "$1" != --row-only ] || shift
+D=$STUB_DIR; printf '%s\n' "$*" >> "$D/argv"; case $1 in --row-only|--reuse) shift ;; esac
 wt=$2; br=$3; n=$(( $(cat "$D/n" 2>/dev/null || echo 0) + 1 )); echo $n > "$D/n"
 case $n in
   1) git -C "$wt" push -q origin "$br" || exit 1; echo "app_push: PUSHED to $br; pull request #5 is open"; exit 0 ;;
@@ -1143,9 +1145,12 @@ STUB
   [ "$(cat "$t/opwt")" = detached ]
   ck "open_pr: a successful open leaves its worktree detached at the pushed head" $?
   # The row push asks app_push.sh for --row-only (P53): one full prepr per open, not two; the
-  # code push never asks (null control).
-  [ "$(sed -n 2p "$t/argv" | cut -d' ' -f1)" = --row-only ] && [ "$(sed -n 1p "$t/argv" | cut -d' ' -f1)" = tvofi/heatpump_optimizer ]
-  ck "open_pr: its row push passes --row-only, and its code push does not" $?
+  # code push asks for --reuse (P386), whose verdict reuses a receipted prepr or runs the full
+  # one, and never for --row-only (null control).
+  [ "$(sed -n 2p "$t/argv" | cut -d' ' -f1)" = --row-only ] && [ "$(sed -n 1p "$t/argv" | cut -d' ' -f1)" = --reuse ]
+  ck "open_pr: its row push passes --row-only, and its code push --reuse, never --row-only" $?
+  racerun opreuse; [ "$(sed -n 1p "$t/argv" | cut -d' ' -f1)" = tvofi/heatpump_optimizer ] && [ "$(sed -n 2p "$t/argv" | cut -d' ' -f1)" = --row-only ]
+  ck "  mutant mut:opreuse (its line deleted): the code push asks no reuse verdict, so it runs the full prepr" $?
   racerun release; [ "$(cat "$t/opwt")" = branch ] && [ "$(cat "$t/rowpushed")" = 1 ]
   ck "  mutant mut:release (its line deleted): the opened PR's worktree still holds its branch" $?
   racerun oprowonly; [ "$(sed -n 2p "$t/argv" | cut -d' ' -f1)" = tvofi/heatpump_optimizer ]
@@ -1156,7 +1161,7 @@ STUB
   # records its arguments and pushes; fix/v starts at handoff/v's tip, without its row.
   if [ ! -e "$t/fixv" ]; then
     git -C "$o" checkout -q -b handoff/v "$base" && mkdir -p "$o/tools/pr" && printf 'v\n' > "$o/v" \
-      && printf '#!/bin/bash\nprintf "%%s\\n" "$*" >> "$STUB_DIR/argv"; [ "$1" != --row-only ] || shift\ngit -C "$2" push -q origin "$3" || exit 1; echo "app_push: PUSHED"\n' > "$o/tools/pr/app_push.sh" \
+      && printf '#!/bin/bash\nprintf "%%s\\n" "$*" >> "$STUB_DIR/argv"; case $1 in --row-only|--reuse) shift ;; esac\ngit -C "$2" push -q origin "$3" || exit 1; echo "app_push: PUSHED"\n' > "$o/tools/pr/app_push.sh" \
       && git -C "$o" add v tools/pr/app_push.sh && git -C "$o" commit -q -m "code v" \
       && git -C "$o" branch fix/v HEAD && git -C "$o" checkout -q main && touch "$t/fixv"
   fi
@@ -1212,9 +1217,9 @@ STUB
   [ "$(cat "$t/rc")" = 1 ] && grep -qF "update_pr: REFUSE: handoff/v ($codeV2) is not in the head" "$t/out" && [ "$(bpcalls)" = 4 ]
   ck "update_pr: code - with a handoff tip the head lacks refuses, and patches no body" $?
   upd - "$codeV2"
-  [ "$(cat "$t/rc")" = 0 ] && [ "$(pushes)" = 2 ] && [ "$(sed -n 2p "$wsd/argv" | cut -d' ' -f1)" = tvofi/heatpump_optimizer ] \
+  [ "$(cat "$t/rc")" = 0 ] && [ "$(pushes)" = 2 ] && [ "$(sed -n 2p "$wsd/argv" | cut -d' ' -f1)" = --reuse ] \
     && git -C "$o" merge-base --is-ancestor "$codeV2" fix/v && ! git -C "$o" merge-base --is-ancestor main fix/v
-  ck "null control: a new code sha is merged and pushed through the full prepr, main still unmerged" $?
+  ck "null control: a new code sha is merged and pushed asking for --reuse, never --row-only (app_push.sh's verdict or the full prepr judges it), main still unmerged" $?
   touch "$wsd/dirty"; bonly -
   [ "$(cat "$t/rc")" = 1 ] && grep -qF "update_pr: REFUSE: body-only update would move the head $(cat "$t/vbefore")" "$t/out" \
     && [ "$(pushes)" = 2 ] && [ "$(bpcalls)" = 4 ] && [ "$(cat "$t/vbefore")" = "$(cat "$t/vafter")" ]
@@ -1225,8 +1230,8 @@ STUB
   unmove 2
   upd - -
   [ "$(cat "$t/rc")" = 0 ] && [ "$(pushes)" = 3 ] && git -C "$o" merge-base --is-ancestor main fix/v \
-    && [ "$(sed -n 3p "$wsd/argv" | cut -d' ' -f1)" = tvofi/heatpump_optimizer ] && grep -qF "merges origin/main" "$t/bv.md"
-  ck "null control: without HPO_UPDATE_BODY_ONLY a DIRTY pull request still absorbs main, through the full prepr" $?
+    && [ "$(sed -n 3p "$wsd/argv" | cut -d' ' -f1)" = --reuse ] && grep -qF "merges origin/main" "$t/bv.md"
+  ck "null control: without HPO_UPDATE_BODY_ONLY a DIRTY pull request still absorbs main, asking for --reuse, never --row-only" $?
   # merge-tree is the local proof when GitHub does not say DIRTY (#3089 review, mutant A): main
   # conflicting with fix/v is merged, so the run stops on the conflict, patching and pushing nothing
   rm -f "$wsd/dirty"; printf 'main side\n' > "$o/v" && git -C "$o" add v && git -C "$o" commit -q -m "main: v conflicts"
@@ -1373,7 +1378,7 @@ GH
   ck "null control: a worktree whose HEAD origin has is detached as before, and the run reaches its push" $?
   # The row-only arm (R10-ROW-ONLY-UPDATE): a head that is the live head plus one commit (here code
   # sha `-` adding the row) asks app_push.sh for --row-only, whose own verdict decides whether a
-  # full prepr is owed; a head merging new code never asks.
+  # full prepr is owed; a head merging new code asks for --reuse instead (P386), never --row-only.
   # Branch fix/w carries an app_push.sh stub that records its arguments, then fails the push.
   if [ ! -e "$t/fixw" ]; then
     git -C "$o" checkout -q -b fix/w "$base" && mkdir -p "$o/tools/pr" \
@@ -1384,10 +1389,12 @@ GH
     rm -f "$t/argv"; cp "$t/body.md" "$t/b.md"; HANDOFF_TOPIC=x run "$1" update_pr.sh fix/w "$2" "$t/b.md"; }
   rowrun - -; [[ $(cat "$t/argv" 2>/dev/null) == "--row-only tvofi/heatpump_optimizer "* ]]
   ck "update_pr: code sha '-' asks app_push.sh for --row-only, whose verdict decides the prepr" $?
-  rowrun rowonly -; [[ $(cat "$t/argv" 2>/dev/null) == "tvofi/heatpump_optimizer "* ]]
-  ck "  mutant mut:rowonly (its line deleted): code sha '-' runs the full prepr" $?
-  rowrun - "$code"; [[ $(cat "$t/argv" 2>/dev/null) == "tvofi/heatpump_optimizer "* ]]
-  ck "null control: a code sha the head lacks is merged and never asks for --row-only, so its push runs the full prepr" $?
+  rowrun rowonly -; [[ $(cat "$t/argv" 2>/dev/null) == "--reuse tvofi/heatpump_optimizer "* ]]
+  ck "  mutant mut:rowonly (its line deleted): code sha '-' asks for --reuse, not --row-only" $?
+  rowrun - "$code"; [[ $(cat "$t/argv" 2>/dev/null) == "--reuse tvofi/heatpump_optimizer "* ]]
+  ck "null control: a code sha the head lacks is merged and never asks for --row-only; it asks for --reuse, whose verdict or the full prepr judges its push" $?
+  rowrun updreuse "$code"; [[ $(cat "$t/argv" 2>/dev/null) == "tvofi/heatpump_optimizer "* ]]
+  ck "  mutant mut:updreuse (its line deleted): a code sha the head lacks asks no reuse verdict, so its push runs the full prepr" $?
   for c in "$code" -; do
     cp "$t/body.md" "$t/b.md"; run - update_pr.sh fix/x "$c" "$t/b.md"
     [ "$(cat "$t/rc")" != 0 ] && ! grep -q 'REFUSE: code sha\|REFUSE: origin has\|argument(s)' "$t/out" \
diff --git a/tools/audit/seat/update_pr.sh b/tools/audit/seat/update_pr.sh
index 869ba8ba2..fe9c85f6b 100755
--- a/tools/audit/seat/update_pr.sh
+++ b/tools/audit/seat/update_pr.sh
@@ -20,7 +20,9 @@
 # (R10-ROW-ONLY-UPDATE): app_push.sh's own verdict replaces the full prepr with the body contract
 # when the push is exactly this PR's row added onto its live head under the body plus this run's
 # note, and runs prepr otherwise; its `app_push: ROW-ONLY:` line, naming which and why, is printed
-# here. A head that merges new code, or main, never asks.
+# here. A head that merges new code, or main, asks for --reuse instead (P386): the fixer's receipted
+# prepr, the handoff body's `Prepr:` trailer, is not repeated over its clean merge with the live head
+# and main, and app_push.sh runs the full prepr on any other head; its `app_push: REUSE:` line too.
 # BODY-ONLY (R10-FLOW-BODY-ONLY): when the merges and the row leave the head exactly the live head
 # (the code sha already in it, or `-`; main clean; the row present), nothing is pushed:
 # body_patch.sh runs the body contract at that head from this run's worktree and PATCHes the body,
@@ -126,9 +128,10 @@ s=prefix(s,pre); open(p,'w').write(s)
 E
 if test -f tools/audit/app_push.sh; then _push=tools/audit/app_push.sh; else _push=tools/pr/app_push.sh; fi
 RO=""; [ "$(git rev-parse "$H^@")" != "$LIVE" ] || RO=--row-only  # mut:rowonly
+[ -n "$RO" ] || RO=--reuse  # mut:updreuse
 # Asynchronous, so a stop signal interrupts the `wait` and the EXIT trap reaps
 # the tree (pr_args.sh's why).
 { pr_push_hold; PREPR_SKIP_CLOSURES=1 PYTHONPATH=tests/hastub bash "$_push" $RO $R $WT $BR $B $ISS > $WT.log 2>&1 & } 9>>"$PR_PUSH_LOCK"
 pr_wait $! $WT.log
-grep -h '^app_push: ROW-ONLY:' $WT.log || :
+grep -h '^app_push: \(ROW-ONLY\|REUSE\):' $WT.log || :
 echo "HEAD=$H"
diff --git a/tools/pr/app_push.sh b/tools/pr/app_push.sh
index dd33bad78..df23a7d20 100644
--- a/tools/pr/app_push.sh
+++ b/tools/pr/app_push.sh
@@ -4,7 +4,7 @@
 # -- the author identity decision 0011 built this tool for, with the body's
 # contract check FIRST so nothing reaches the remote until the body passes.
 #
-#   tools/pr/app_push.sh [--dry-run] [--recarry|--row-only] <owner/repo> <worktree> <branch> <body.md> [issue-numbers...]
+#   tools/pr/app_push.sh [--dry-run] [--recarry|--row-only|--reuse] <owner/repo> <worktree> <branch> <body.md> [issue-numbers...]
 #   tools/pr/app_push.sh --branch-only <owner/repo> <worktree> batch/<name>
 #   tools/pr/app_push.sh --self-test
 #
@@ -122,6 +122,29 @@
 # Anything else runs prepr exactly as without the flag. It writes no note of
 # its own; one `app_push: ROW-ONLY:` line names the path taken and why, and
 # the push must still be the HEAD the verdict judged.
+#
+# --reuse is open_pr.sh's first push and update_pr.sh's code push (P386, owner
+# directive 2026-11-04: a fixer's prepr is not repeated at open or update). It
+# runs prepr under PREPR_SKIP_CODE=<C> -- no heavy slot, the steps keyed to the
+# code alone dropped, the steps keyed to main, the body or the merge kept, with
+# tests/structure.py and ci predict on HEAD merged with main -- and then
+# `row_only_checks`, only when every one of these holds, each read here and
+# failing closed:
+#   (a) the branch is fix/<topic>, and the tip of origin's handoff-body/<topic>
+#       carries exactly one `Prepr: <C> <T>` trailer, body_push.sh's copy of
+#       prepr.sh's receipt of a passing full run;
+#   (b) C's tree is T, so the run it records was over this code;
+#   (c) C is in HEAD, and C merges cleanly with the live head (when a pull
+#       request is open) and then with the origin/main commit HEAD holds, which
+#       is on the freshly fetched main's first-parent chain -- no resolution;
+#   (d) HEAD's tree is that clean merge's, or it plus this pull request's own
+#       delivery row and nothing else;
+#   (e) no commit outside C, the live head and main but that one row commit.
+# Not keyed to main standing still under a closure, which fired on 0 of 4 code
+# opens (s6-batch95.md#P346): main's commits passed on main, CI gates the merged
+# head. Anything else runs the full prepr exactly as without the flag. One
+# `app_push: REUSE:` line names the path taken and why, and the push must still
+# be the HEAD the verdict judged.
 set -uo pipefail
 
 # pr_args.sh's reap: a stopped pusher ends the whole tree it started, and prepr
@@ -235,6 +258,64 @@ sys.exit(not (j > i and prefix(live, b[i:j]).rstrip("\n") == b.rstrip("\n")))' "
   _rv_no "HEAD ${RV_HEAD:0:8} is the live head ${live:0:8} plus one commit adding or editing only $row, one open row for #$num, and the body is the live one under one new \`## Head\` note"
 }
 
+# The --reuse verdict: (a) to (e) of the header, in that order, the first
+# failure named; recarry_verdict's shape. It reads HEAD ONCE and leaves RV_HEAD,
+# RV_C (the receipted code sha), RV_TITLE (the live title, else empty) and RV_WHY
+# set, and prints RV_WHY. The merges it computes are unreferenced commits.
+reuse_verdict() { # worktree listing branch -> RV_*; rc 0 = the receipt replaces prepr's code steps
+  local wt=$1 listing=$2 br=$3 topic tip tr c t live="" num="" mb x y mt d xs n row=""
+  RV_C="" RV_TITLE="" RV_HEAD=$(git -C "$wt" rev-parse HEAD 2>/dev/null) || RV_HEAD=""
+  _rv_no() { RV_WHY=$*; echo "$*"; }
+  [[ $RV_HEAD =~ ^[0-9a-f]{40}$ ]] || { _rv_no "HEAD does not read back"; return 1; }
+  topic=${br#fix/}
+  [ "$topic" != "$br" ] && [ -n "$topic" ] || { _rv_no "$br is not fix/<topic>, so no handoff-body ref holds its receipt"; return 1; }
+  # open_pr.sh names the branch fix/<topic>-pr when the seat holds fix/<topic>; the
+  # trailer, not the name, decides, so a wrong ref only fails (b) to (e).
+  tip=$(git -C "$wt" ls-remote origin "refs/heads/handoff-body/$topic" 2>/dev/null | awk 'NF { print $1; exit }')
+  if [ -z "$tip" ] && [ "${topic%-pr}" != "$topic" ]; then
+    topic=${topic%-pr}; tip=$(git -C "$wt" ls-remote origin "refs/heads/handoff-body/$topic" 2>/dev/null | awk 'NF { print $1; exit }')
+  fi
+  [[ $tip =~ ^[0-9a-f]{40}$ ]] || { _rv_no "origin holds no handoff-body/$topic, so no receipt"; return 1; }
+  git -C "$wt" fetch -q origin "refs/heads/handoff-body/$topic" 2>/dev/null || { _rv_no "handoff-body/$topic could not be fetched"; return 1; }
+  tr=$(git -C "$wt" log -1 --format='%(trailers:key=Prepr,valueonly)' "$tip" 2>/dev/null | sed '/^[[:space:]]*$/d')
+  [ "$(printf '%s\n' "$tr" | grep -c .)" = 1 ] && read -r c t <<<"$tr" && [[ $c =~ ^[0-9a-f]{40}$ && $t =~ ^[0-9a-f]{40}$ ]] \
+    || { _rv_no "handoff-body/$topic's tip ${tip:0:8} carries no one \`Prepr: <sha> <tree>\` trailer, so no receipt"; return 1; }
+  [ "$(git -C "$wt" rev-parse "$c^{tree}" 2>/dev/null)" = "$t" ] \
+    || { _rv_no "the receipt's tree ${t:0:8} is not code ${c:0:8}'s tree, so the run it records was not over this code"; return 1; }
+  git -C "$wt" merge-base --is-ancestor "$c" "$RV_HEAD" 2>/dev/null \
+    || { _rv_no "the receipted code ${c:0:8} is not in HEAD ${RV_HEAD:0:8}"; return 1; }
+  read -r live num RV_TITLE < <(printf '%s' "$listing" | python3 -c 'import sys, json
+l = json.load(sys.stdin)
+if not l: print("none")
+else: d = l[0]; print(d["head"]["sha"], int(d["number"]), " ".join(str(d.get("title") or "").split()))' 2>/dev/null)
+  if [ "$live" = none ]; then live=""
+  else
+    [[ $live =~ ^[0-9a-f]{40}$ ]] || { _rv_no "the open-pull-request listing names no live head that reads back"; return 1; }
+    . "$(dirname -- "$0")/../audit/seat/delivery_row.sh" || { _rv_no "delivery_row.sh did not load, so the row's path is unknown"; return 1; }
+    row=$ROW_DIR/$num.md
+  fi
+  git -C "$wt" fetch -q origin main 2>/dev/null || { _rv_no "origin/main could not be fetched"; return 1; }
+  mb=$(git -C "$wt" merge-base "$RV_HEAD" refs/remotes/origin/main 2>/dev/null) || { _rv_no "HEAD has no merge base with origin/main"; return 1; }
+  git -C "$wt" rev-list --first-parent refs/remotes/origin/main 2>/dev/null | grep -x "$mb" >/dev/null \
+    || { _rv_no "the main HEAD holds, ${mb:0:8}, is not on the freshly fetched origin/main's first-parent chain"; return 1; }
+  x=$c
+  for y in $live $mb; do
+    mt=$(git -C "$wt" merge-tree --write-tree "$x" "$y" 2>/dev/null) \
+      || { _rv_no "code ${c:0:8} does not merge cleanly with ${y:0:8}; a resolution goes through the full prepr"; return 1; }
+    x=$(git -C "$wt" -c user.name=app_push -c user.email=app_push@invalid commit-tree "$mt" -p "$x" -p "$y" -m "app_push: reuse verdict merge" 2>/dev/null) \
+      || { _rv_no "the clean merge could not be written"; return 1; }
+  done
+  d=$(git -C "$wt" diff --no-renames --name-status "$x" "$RV_HEAD" 2>/dev/null) || { _rv_no "the diff against the clean merge could not be read"; return 1; }
+  [ -z "$d" ] || { [ -n "$row" ] && { [ "$d" = "$(printf 'A\t%s' "$row")" ] || [ "$d" = "$(printf 'M\t%s' "$row")" ]; }; } \
+    || { _rv_no "HEAD's tree is not the clean merge of code ${c:0:8}${live:+, the live head ${live:0:8}} and main's ${mb:0:8}${row:+ plus $row} (git diff --name-status: $(printf '%s' "$d" | tr '\t' ' ' | paste -sd';' -))"; return 1; }
+  xs=$(git -C "$wt" rev-list --no-merges "$RV_HEAD" --not "$c" $live "$mb" 2>/dev/null) || { _rv_no "HEAD's own commits could not be listed"; return 1; }
+  n=$(printf '%s' "$xs" | grep -c .)
+  [ "$n" = 0 ] || { [ "$n" = 1 ] && [ -n "$row" ] && [ "$(git -C "$wt" diff-tree --no-commit-id --no-renames --name-only -r "$xs" 2>/dev/null)" = "$row" ]; } \
+    || { _rv_no "HEAD carries $n commit(s) beyond code ${c:0:8}, the live head and main, not only this pull request's own row"; return 1; }
+  RV_C=$c
+  _rv_no "HEAD ${RV_HEAD:0:8} is the clean merge of the receipted code ${c:0:8} (tree ${t:0:8})${live:+, the live head ${live:0:8}} and main's ${mb:0:8}${row:+, plus at most its own row}"
+}
+
 # What --row-only runs in prepr's place: two of the body checks pr-contract runs,
 # at the head the verdict judged and with the live title -- step 7's body
 # contract (`policy_lint.mjs --pr-body`) and the carry check
@@ -381,10 +462,11 @@ judge_commits() { # worktree branch head -> rc 0 when ref_privacy's guard passes
 }
 
 push_and_open() {
-  local dry=0 bonly=0 recarry=0 rowonly=0
+  local dry=0 bonly=0 recarry=0 rowonly=0 reuse=0 reused=0
   [ "${1:-}" = "--dry-run" ] && { dry=1; shift; }
   [ "${1:-}" = "--recarry" ] && { recarry=1; shift; }
   [ "${1:-}" = "--row-only" ] && { rowonly=1; shift; }
+  [ "${1:-}" = "--reuse" ] && { reuse=1; shift; }
   if [ "${1:-}" = "--branch-only" ]; then
     bonly=1; shift
     [ $# -eq 3 ] || die "usage: app_push.sh --branch-only <owner/repo> <worktree> batch/<name>"
@@ -394,7 +476,8 @@ push_and_open() {
   [ "$recarry$bonly" != 11 ] || die "--recarry and --branch-only do not combine: a batch/ branch has no pull request to recarry"
   [ "$recarry$rowonly" != 11 ] || die "--recarry and --row-only do not combine: a recarry's head is a merge, a row's is one commit"
   [ "$rowonly$bonly" != 11 ] || die "--row-only and --branch-only do not combine: a batch/ branch has no pull request to row"
-  [ $# -ge 4 ] || die "usage: app_push.sh [--dry-run] [--recarry|--row-only] <owner/repo> <worktree> <branch> <body.md> [issue-numbers...]"
+  [ "$reuse" = 0 ] || [ "$recarry$rowonly$bonly" = 000 ] || die "--reuse combines with none of --recarry, --row-only and --branch-only: each is its own verdict"
+  [ $# -ge 4 ] || die "usage: app_push.sh [--dry-run] [--recarry|--row-only|--reuse] <owner/repo> <worktree> <branch> <body.md> [issue-numbers...]"
   local repo=$1 wt=$2 br=$3 body=$4
   shift 4
   [[ $repo =~ ^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$ ]] || die "repo '$repo' is not owner/repo"
@@ -460,6 +543,13 @@ push_and_open() {
     if [ "$skip" = 1 ]; then echo "app_push: ROW-ONLY: prepr SKIPPED: $RV_WHY"; else echo "app_push: ROW-ONLY: prepr RUNS: $RV_WHY"; fi
     [ -n "$RV_HEAD" ] || die "--row-only: HEAD in $wt does not read back"
   fi
+  local RV_C=""
+  if [ "$reuse" = 1 ]; then
+    flag=reuse
+    reuse_verdict "$wt" "$listing" "$br" >/dev/null && reused=1
+    if [ "$reused" = 1 ]; then echo "app_push: REUSE: prepr's code steps SKIPPED, no heavy slot: $RV_WHY"; else echo "app_push: REUSE: full prepr RUNS: $RV_WHY"; fi
+    [ -n "$RV_HEAD" ] || die "--reuse: HEAD in $wt does not read back"
+  fi
 
   # THE #678 ORDERING: the body passes BEFORE anything is minted. prepr.sh
   # derives its diff from the worktree it runs in, so it runs with the
@@ -470,13 +560,16 @@ push_and_open() {
   prepr="$(cd "$(dirname -- "$0")" && pwd)/prepr.sh"
   [ -f "$prepr" ] || die "no prepr.sh beside this script at $prepr"
   if [ "$bonly" = 0 ] && [ "$skip" = 0 ]; then
-    ( cd "$wt" && bash "$prepr" "$body" "$@" ) & prepr_pid=$!
+    # shellcheck disable=SC2030,SC2031 # the receipt's sha reaches prepr's environment alone
+    ( cd "$wt" && if [ "$reused" = 1 ]; then export PREPR_SKIP_CODE=$RV_C; fi && bash "$prepr" "$body" "$@" ) & prepr_pid=$!
     wait "$prepr_pid" || prepr_rc=$?
     [ "$prepr_rc" = 0 ] \
       || die "the body did not pass tools/pr/prepr.sh, so NOTHING was minted, pushed or posted; repair it and run this again"
   fi
   [ "$rowonly$skip" != 11 ] || row_only_checks "$wt" "$body" "$RV_HEAD" "$RV_TITLE" \
     || die "--row-only: the body contract (policy_lint.mjs --pr-body) or the carry check (carry_audit.py) refused $body, so NOTHING was minted, pushed or posted"
+  [ "$reused" = 0 ] || row_only_checks "$wt" "$body" "$RV_HEAD" "${RV_TITLE:-$(git -C "$wt" log -1 --format=%s)}" \
+    || die "--reuse: the body contract (policy_lint.mjs --pr-body) or the carry check (carry_audit.py) refused $body, so NOTHING was minted, pushed or posted"
 
   # Only a committed tip is pushed: HEAD is the branch's tip, and the tree is
   # clean. A dirty worktree would push a sha whose tree the body never
@@ -488,7 +581,7 @@ push_and_open() {
   [ "$head" = "$tip" ] || die "worktree HEAD ($head) is not the committed tip of '$br' ($tip); commit or check out first"
   [ -z "$(git -C "$wt" status --porcelain 2>/dev/null)" ] \
     || die "worktree $wt is dirty; only a committed tip is pushed -- commit or clean it first"
-  [ "$recarry$rowonly" = 00 ] || [ "$head" = "$RV_HEAD" ] \
+  [ "$recarry$rowonly$reuse" = 000 ] || [ "$head" = "$RV_HEAD" ] \
     || die "--$flag: HEAD moved to $head after the verdict judged $RV_HEAD; nothing was minted or pushed"
   local subject; subject=$(git -C "$wt" log -1 --format=%s) || die "could not read the tip commit's subject"
   judge_commits "$wt" "$br" "$head" \
@@ -603,7 +696,7 @@ printf '## Head\n\n`%s`\n\n## Mutation proof\n\nm\n\n## Null control\n\nn\n\n##
 # so a stopped app_push can be judged by what survives it.
 cat > "$W/tool/prepr.sh" <<'STUB'
 #!/bin/bash
-printf 'prepr %s\n' "$*" >> "$STUB/log"
+printf 'prepr %s%s\n' "${PREPR_SKIP_CODE:+PREPR_SKIP_CODE=$PREPR_SKIP_CODE }" "$*" >> "$STUB/log"
 [ -f "$STUB/prepr-fails" ] && { echo "prepr: REFUSE" >&2; exit 1; }
 if [ -f "$STUB/prepr-tree" ]; then
   echo $$ >> "$STUB/pids"
@@ -1254,5 +1347,85 @@ st "$(grep -c '^app_push: PUSHED ' "$W/rclosed/out")" 0 "and no success line"
 # the budget itself: 4 reads = the first read plus 3 retries, settling 5s/15s/45s.
 st "$(grep -c '^RB_TRIES=${APP_PUSH_READBACK_TRIES:-4}$' "$SELF")$(grep -c '^RB_SLEEP=${APP_PUSH_READBACK_SLEEP:-5}$' "$SELF")" 11 "the default budget is a first read plus 3 retries, settling 5s/15s/45s (~65s of settles)"
 
+# --reuse (P386), through the stubs: the stub origin holds no handoff-body ref,
+# so no receipt, and the full prepr runs (fixture arm (b), end to end); and the
+# flag combines with no other verdict's.
+mkcase unorcpt
+run unorcpt --reuse o/r "$W/tool-wt" "$BR" "$W/body.md"; st $? 0 "--reuse with no receipt on origin pushes after the full prepr"
+st "$(calls unorcpt 'prepr ')$(grep -c '^prepr PREPR_SKIP_CODE=' "$W/unorcpt/log")" 10 "and that prepr ran once, with no PREPR_SKIP_CODE: the fail-closed arm (b)"
+st "$(grep -c '^app_push: REUSE: full prepr RUNS: origin holds no handoff-body/stub-x, so no receipt$' "$W/unorcpt/out")" 1 "one REUSE line names the full path and why"
+mkcase ucombo
+run ucombo --row-only --reuse o/r "$W/tool-wt" "$BR" "$W/body.md"; st $? 1 "REFUSE: --reuse with --row-only"
+st "$(wc -l < "$W/ucombo/log" | tr -d ' ')" 0 "before any prepr, gh, git, openssl or curl call"
+
+# --reuse, real git: the production reuse_verdict, extracted from this file, over
+# a bare origin whose handoff-body/t carries prepr's receipt as body_push.sh
+# writes it. The ruling's fixture arms (a), (b), (c) and (f) are the verdict's;
+# (d) and (e) are prepr.sh's merged_steps, in its own self-test.
+eval "$(sed -n '/^reuse_verdict() {/,/^}/p' "$SELF")"
+. "$(dirname -- "$SELF")/../audit/seat/delivery_row.sh" || { echo "FAIL delivery_row.sh did not load"; exit 1; }
+U="$W/reuse"; mkdir -p "$U"
+throwaway_git_init "$U/origin.git" -q --bare -b main && throwaway_git_clone -q "$U/origin.git" "$U/wt" >/dev/null 2>&1 \
+  && (cd "$U/wt" && printf 'a\n' > a && rgit add a && rgit commit -qm base && rgit tag B && rgit push -q origin HEAD:main \
+      && rgit checkout -q -b fix/t && printf 'code\n' > c && printf 'a2\n' > a && rgit add c a && rgit commit -qm code && rgit tag C \
+      && rgit checkout -q main && printf 'm\n' > m && rgit add m && rgit commit -qm main2 && rgit push -q origin main \
+      && rgit checkout -q fix/t && rgit merge -q --no-edit origin/main)
+uc=$(git -C "$U/wt" rev-parse C); ut=$(git -C "$U/wt" rev-parse 'C^{tree}')
+ubody() { # [trailer line] -> handoff-body/t on origin, one commit carrying it
+  local m; m=$(printf 'body: t\n\nCode: %s%s' "$uc" "${1:+$(printf '\n%s' "$1")}")
+  rgit -C "$U/wt" push -q -f origin "$(git -C "$U/wt" commit-tree "$(git -C "$U/wt" mktree </dev/null)" -m "$m"):refs/heads/handoff-body/t"
+}
+ulist() { python3 -c 'import json, sys; print(json.dumps([{"number": 7, "title": "t", "head": {"sha": sys.argv[1]}, "body": "b"}]))' "$1"; }
+ubody "Prepr: $uc $ut"
+reuse_verdict "$U/wt" "[]" fix/t > "$U/why"; st "$?$RV_C" "0$uc" "real git (a): an open whose head is the receipted code merged cleanly with main reuses the receipt, RV_C the code ($(cat "$U/why"))"
+(cd "$U/wt" && mkdir -p "$ROW_DIR" && printf '| #7 |\n' > "$ROW_DIR/7.md" && rgit add "$ROW_DIR/7.md" && rgit commit -qm row)
+st "$(reuse_verdict "$U/wt" "$(ulist "$uc")" fix/t >/dev/null; echo $?)" 0 "real git (a): an update to that live head, merged with main, plus its own row, reuses it"
+(cd "$U/wt" && printf 'x\n' > x && rgit add x && rgit commit -qm extra)
+st "$(reuse_verdict "$U/wt" "$(ulist "$uc")" fix/t | grep -c 'is not the clean merge of code')" 1 "real git: one more file past the row runs the full prepr"
+(cd "$U/wt" && rgit reset -q --hard HEAD~2)
+# (e) alone: two commits past the clean merge that net to no tree change, so the
+# tree check passes and only the commit count sees subjects nothing checked
+# (fix review of #3221, plant F9); the head reset under them reuses again.
+(cd "$U/wt" && printf 'x\n' > tx && rgit add tx && rgit commit -qm "neutral one" && rgit rm -q tx && rgit commit -qm "neutral two")
+st "$(reuse_verdict "$U/wt" "[]" fix/t | grep -c "^HEAD carries 2 commit(s) beyond code ${uc:0:8}, the live head and main, not only this pull request's own row$")" 1 "real git (e): two tree-neutral commits past the clean merge run the full prepr"
+(cd "$U/wt" && rgit reset -q --hard HEAD~2)
+st "$(reuse_verdict "$U/wt" "[]" fix/t >/dev/null; echo $?)" 0 "real git: the clean merge without them reuses (the (e) arm's null control)"
+ubody ""
+st "$(reuse_verdict "$U/wt" "[]" fix/t | grep -c "carries no one .Prepr: <sha> <tree>. trailer, so no receipt$")" 1 "real git (b): a body with no receipt runs the full prepr (null control)"
+ubody "Prepr: $(git -C "$U/wt" rev-parse B) $(git -C "$U/wt" rev-parse 'B^{tree}')"
+st "$(reuse_verdict "$U/wt" "[]" fix/t | grep -c 'is not the clean merge of code')" 1 "real git (b): a receipt naming another sha, an ancestor whose own tree matches, runs the full prepr"
+rgit -C "$U/wt" push -q origin :refs/heads/handoff-body/t
+st "$(reuse_verdict "$U/wt" "[]" fix/t)" "origin holds no handoff-body/t, so no receipt" "real git (b): no handoff-body ref runs the full prepr"
+ubody "Prepr: $uc $(git -C "$U/wt" rev-parse 'B^{tree}')"
+st "$(reuse_verdict "$U/wt" "[]" fix/t)" "the receipt's tree $(git -C "$U/wt" rev-parse --short=8 'B^{tree}') is not code ${uc:0:8}'s tree, so the run it records was not over this code" "real git (f): a tree differing from the trailer's runs the full prepr"
+ubody "Prepr: $uc $ut"
+st "$(reuse_verdict "$U/wt" "[]" fix/t >/dev/null; echo $?)" 0 "real git: the same receipt restored reuses again (the (f) arm's null control)"
+st "$(reuse_verdict "$U/wt" "[]" fix/t-pr >/dev/null; echo $?)" 0 "real git: open_pr.sh's fix/<topic>-pr branch finds handoff-body/<topic>"
+ubody "$(printf 'Prepr: %s %s\nPrepr: %s %s' "$uc" "$ut" "$uc" "$ut")"
+st "$(reuse_verdict "$U/wt" "[]" fix/t | grep -c "carries no one .Prepr: <sha> <tree>. trailer, so no receipt$")" 1 "real git (a): two Prepr: trailers, though each is the receipt, run the full prepr"
+ubody "Prepr: $uc $ut"
+(cd "$U/wt" && rgit checkout -q main && printf 'a3\n' > a && rgit add a && rgit commit -qm conflicting && rgit push -q origin main \
+  && rgit checkout -q fix/t && rgit reset -q --hard C && rgit merge -q --no-edit origin/main; printf 'resolved\n' > a && rgit add a && rgit commit -qm resolved)
+st "$(reuse_verdict "$U/wt" "[]" fix/t)" "code ${uc:0:8} does not merge cleanly with $(git -C "$U/wt" rev-parse --short=8 origin/main); a resolution goes through the full prepr" "real git (c): a conflict resolved in the merge runs the full prepr"
+# (c)'s first-parent arm: HEAD holds a side commit main merged, not main's own
+# first-parent history; the earlier reusing rows are its null control.
+(cd "$U/wt" && rgit checkout -q -b side origin/main~1 && printf 'sd\n' > sd && rgit add sd && rgit commit -qm side \
+  && rgit checkout -q main && rgit reset -q --hard origin/main && rgit merge -q --no-ff --no-edit side && rgit push -q origin main \
+  && rgit checkout -q fix/t && rgit reset -q --hard C && rgit merge -q --no-edit side)
+st "$(reuse_verdict "$U/wt" "[]" fix/t | grep -c "^the main HEAD holds, $(git -C "$U/wt" rev-parse --short=8 side), is not on the freshly fetched origin/main's first-parent chain$")" 1 "real git (c): HEAD holding a main commit off main's first-parent chain runs the full prepr"
+
+# --reuse wiring past a reusing verdict: a copy whose reuse_verdict is replaced by
+# one that reuses, so prepr runs under PREPR_SKIP_CODE and row_only_checks follow it.
+sed '/^reuse_verdict() {/,/^}/c\
+function reuse_verdict { RV_HEAD=$(git -C "$1" rev-parse HEAD); RV_C=$RV_HEAD; RV_TITLE=""; RV_WHY="stub reuse"; echo "$RV_WHY"; }' "$SELF" > "$W/tool/app_push_reuse.sh"
+rucase() { mkcase "$1"; cp "$W/body.md" "$W/$1/body.md"; ( export STUB="$W/$1" PATH="$W/bin:$PATH" TMPDIR="$W/$1/tmp" HPO_IDENTITY_DIR="$W/id"
+  bash "$W/tool/app_push_reuse.sh" --reuse o/r "$W/tool-wt" "$BR" "$W/$1/body.md" > "$W/$1/out" 2> "$W/$1/err" ); }
+rucase ureused; st $? 0 "--reuse, the verdict reusing: pushed"
+st "$(grep -c "^prepr PREPR_SKIP_CODE=$SHA " "$W/ureused/log")$(grep -c '^node tools/policy/policy_lint.mjs --pr-body ' "$W/ureused/log")$(grep -c '^carry_audit check --body ' "$W/ureused/log")" 111 "and prepr ran under PREPR_SKIP_CODE, then the body contract and the carry check"
+mkcase ufail; : > "$W/ufail/node-fails"; cp "$W/body.md" "$W/ufail/body.md"
+( export STUB="$W/ufail" PATH="$W/bin:$PATH" TMPDIR="$W/ufail/tmp" HPO_IDENTITY_DIR="$W/id"
+  bash "$W/tool/app_push_reuse.sh" --reuse o/r "$W/tool-wt" "$BR" "$W/ufail/body.md" > "$W/ufail/out" 2> "$W/ufail/err" ); st $? 1 "--reuse, the verdict reusing: a body the contract refuses refuses after the reduced prepr"
+st "$(grep -c '^git .*push' "$W/ufail/log")$(calls ufail curl)" 00 "and nothing was minted or pushed"
+
 echo "app_push self-test: $N checks, $FAILS failed"
 [ "$FAILS" -eq 0 ]
diff --git a/tools/pr/prepr.sh b/tools/pr/prepr.sh
index 06c256aa1..5caf2f13e 100755
--- a/tools/pr/prepr.sh
+++ b/tools/pr/prepr.sh
@@ -1615,6 +1615,96 @@ selftest_inputs() { # -> one path per line; a trailing / is a directory prefix
   fi
   printf '%s\n' "$SELFTEST_FIXTURES"
 }
+# --- the receipt and the merged tree (P386, R10-HANDOFF-PATH part 1) --------
+# A full run that passes with a body writes `<HEAD sha> <tree sha>` to
+# hpo-prepr-receipt in this checkout's git dir. body_push.sh carries it onto the
+# handoff-body/<topic> commit as a `Prepr:` trailer when its sha is the handoff's
+# code head, and app_push.sh --reuse reads it there, so a fixer's run is not
+# repeated at open or update. A run that sets any PREPR_SKIP_* but
+# PREPR_SKIP_CLOSURES (closures-autofix repairs that one on the pull request)
+# writes none, PREPR_SKIP_CODE included; so does a run over a dirty tree, whose
+# HEAD is not what ran. `--body-check` and `--fill-red` exit before the main
+# flow, which removes an earlier receipt first, so a failing run leaves none.
+# The receipt names the HEAD the run STARTED on, read where the main flow starts
+# (`receipt_line`); a HEAD that moved while the steps ran is refused, since a
+# commit landing mid-run is code the steps never saw.
+receipt_file() { # -> the receipt's path in this checkout's git dir
+  local g; g=$(git rev-parse --absolute-git-dir 2>/dev/null) || return 1
+  printf '%s/hpo-prepr-receipt\n' "$g"
+}
+receipt_skips() { # -> the PREPR_SKIP_* variables set non-empty, PREPR_SKIP_CLOSURES aside
+  local v out=""
+  for v in $(compgen -v PREPR_SKIP_); do
+    [ "$v" = PREPR_SKIP_CLOSURES ] || [ -z "${!v}" ] || out="$out $v"
+  done
+  printf '%s' "${out# }"
+}
+receipt_line() { # -> `<HEAD sha> <tree sha>`, the receipt's one line, or nothing
+  local h t
+  h=$(git rev-parse --verify -q HEAD 2>/dev/null) && t=$(git rev-parse --verify -q 'HEAD^{tree}' 2>/dev/null) || return 0
+  printf '%s %s\n' "$h" "$t"
+}
+receipt_write() { # rc, body, the run's starting receipt_line -> one line; the receipt only for a passing full run with a body over a clean, unmoved tree
+  local f s
+  f=$(receipt_file) || { say skip "receipt" "no git dir, so none written"; return 0; }
+  [ "$1" = 0 ] || { say skip "receipt" "rc=$1, so none written"; return 0; }
+  [ -n "$2" ] || { say skip "receipt" "no body passed, so none written"; return 0; }
+  s=$(receipt_skips)
+  [ -z "$s" ] || { say skip "receipt" "$s set, so no full run and none written"; return 0; }
+  [ -z "$(git status --porcelain --untracked-files=no 2>/dev/null)" ] \
+    || { say skip "receipt" "the tree is dirty, so HEAD is not what ran and none written"; return 0; }
+  [ -n "${3:-}" ] || { say skip "receipt" "the run's starting HEAD was not read, so none written"; return 0; }
+  [ "$3" = "$(receipt_line)" ] \
+    || { step "receipt" 1 "HEAD is $(receipt_line | cut -c1-12), not ${3:0:12} where this run started: the steps never saw the commit(s) between, so none written -- run prepr again"; return 0; }
+  printf '%s\n' "$3" > "$f" \
+    && say ok "receipt" "$(cut -c1-12 "$f") written for body_push.sh's Prepr: trailer"
+}
+
+# HEAD merged with origin/main: HEAD itself when it holds main's tip, else the
+# clean `git merge-tree` result committed unreferenced (rc 1 on a conflict, the
+# pull request's DIRTY). Carry 4: #3052 went red on tests/structure.py at a merge
+# no step had measured.
+merged_head() { # -> the merged sha on stdout
+  local t
+  if git merge-base --is-ancestor origin/main HEAD 2>/dev/null; then git rev-parse HEAD; return; fi
+  t=$(git merge-tree --write-tree HEAD origin/main 2>/dev/null) || return 1
+  git -c user.name=prepr -c user.email=prepr@invalid commit-tree "$t" -p HEAD -p origin/main -m "prepr: HEAD merged with origin/main"
+}
+merged_run() { # merged sha, command... -> the command's rc, run at that sha's tree in a throwaway worktree
+  local m=$1 d r; shift
+  if [ "$m" = "$(git rev-parse HEAD)" ]; then "$@"; return; fi
+  d=$(mktemp -d) || return 1
+  git worktree add -q --detach "$d/t" "$m" >/dev/null 2>&1 \
+    || { echo "no worktree of ${m:0:12} could be made"; rm -rf "$d"; return 1; }
+  ( cd "$d/t" && "$@" ); r=$?
+  git worktree remove --force "$d/t" >/dev/null 2>&1; rm -rf "$d"; git worktree prune 2>/dev/null
+  return "$r"
+}
+# The steps keyed to the merge: tests/structure.py on the merged tree, always,
+# and under PREPR_SKIP_CODE the ci predict step 6d runs on HEAD otherwise, there,
+# static: without step 6d's `--record-self-tests`, which re-runs each changed
+# file's own self-test (minutes on a tools diff, measured on this group's) to
+# record its reads against the closures -- a closures question, which
+# PREPR_SKIP_CLOSURES already leaves to closures-autofix, and heavy work this
+# mode takes no slot for.
+merged_steps() { # body, unpinned-site key file -> step lines
+  local m out r b=""
+  [ -z "$1" ] || [ ! -f "$1" ] || b=$(cd "$(dirname -- "$1")" && pwd)/$(basename -- "$1")
+  if ! m=$(merged_head); then
+    step "merged tree" 1 "HEAD and origin/main do not merge cleanly, so no merged tree exists to check -- merge origin/main"
+    return
+  fi
+  out=$(merged_run "$m" python3 tests/structure.py 2>&1); r=$?
+  step "merged structure" "$r" "$(printf '%s\n' "$out" | tail -1 | cut -c1-160) (tests/structure.py at ${m:0:12}, HEAD merged with origin/main)"
+  [ -n "${PREPR_SKIP_CODE:-}" ] || return 0
+  out=$(merged_run "$m" predict_line origin/main "$2" "$b"); r=$?
+  case $r in
+    3) say skip "ci predict" "$out" ;;
+    0) step "ci predict" 0 "$out (at ${m:0:12}, HEAD merged with origin/main)" ;;
+    *) step "ci predict" 1 "$out (at ${m:0:12}, HEAD merged with origin/main)" ;;
+  esac
+}
+
 selftest_owed() { # changed-paths file -> 0 when a changed path is a self-test input
   awk 'NR==FNR { if ($0 ~ /\/$/) d[$0]=1; else f[$0]=1; next }
        ($0 in f) { hit=1; exit }
@@ -3809,6 +3899,72 @@ exit $rc'*) r=0 ;; *) r=1 ;; esac
   st "$r" 0 "the main flow starts the summary after step 1 and ends on its result line"
   rm -rf "${SM:?}"
 
+  # --- P386: the receipt, body_push.sh's Prepr: trailer, and the merged-tree steps.
+  # A throwaway origin whose main gains BAD (tests/structure.py fails on it) or
+  # RED (the stub predictor refuses it) after the fix branch was cut, so each
+  # red exists only on HEAD merged with main: fixture arms (d) and (e).
+  RQ=$(mktemp -d)
+  rq() { git -C "$RQ/wt" "$@" >/dev/null 2>&1; }
+  throwaway_git_init "$RQ/o.git" -q --bare -b main && throwaway_git_clone -q "$RQ/o.git" "$RQ/wt" >/dev/null 2>&1 \
+    && mkdir -p "$RQ/wt/tests" && printf 'import os, sys\nprint("structure: BAD" if os.path.exists("BAD") else "structure: ok")\nsys.exit(os.path.exists("BAD"))\n' > "$RQ/wt/tests/structure.py" \
+    && rq add tests && rq commit -qm base && rq push -q origin HEAD:main && rq checkout -q -b fix/t && printf 'f\n' > "$RQ/wt/f" && rq add f && rq commit -qm fix
+  rsay() { printf '%s %s\n' "$1" "$2"; }
+  rstep() { printf '%s %s rc=%s\n' "$([ "$2" -eq 0 ] && echo ok || echo REFUSE)" "$1" "$2"; }
+  # shellcheck disable=SC2329 # called by merged_steps under PREPR_SKIP_CODE
+  rpredict() { if [ -f RED ]; then echo "PREDICT red"; return 1; fi; echo "no red"; }
+  msteps() { (cd "$RQ/wt" && git fetch -q origin && say() { rsay "$@"; } && step() { rstep "$@"; } && predict_line() { rpredict "$@"; } && merged_steps "" /dev/null) 2>/dev/null; }
+  st "$(msteps | grep -c '^ok merged structure rc=0')" 1 "merged_steps: tests/structure.py passes on HEAD merged with a clean main (the (d) arm's null control)"
+  (cd "$RQ/wt" && git checkout -q main && : > BAD && git add BAD && git commit -qm bad && git push -q origin main && git checkout -q fix/t) >/dev/null 2>&1
+  st "$(msteps | grep -c '^REFUSE merged structure rc=1')$([ -f "$RQ/wt/BAD" ] && echo onhead)" 1 "(d) a clean merge whose tests/structure.py fails is refused, though HEAD alone passes"
+  (cd "$RQ/wt" && git checkout -q main && git rm -q BAD && : > RED && git add RED && git commit -qm red && git push -q origin main && git checkout -q fix/t) >/dev/null 2>&1
+  st "$(msteps | grep -c 'ci predict')" 0 "a full run's merged_steps leaves ci predict to step 6d"
+  st "$(PREPR_SKIP_CODE=x msteps | grep -c '^REFUSE ci predict rc=1')" 1 "(e) under PREPR_SKIP_CODE a ci predict red on the merged main is refused"
+  (cd "$RQ/wt" && git checkout -q main && git rm -q RED && git commit -qm green && git push -q origin main && git checkout -q fix/t) >/dev/null 2>&1
+  st "$(PREPR_SKIP_CODE=x msteps | grep -c '^ok ci predict rc=0')" 1 "and passes once main is green again (the (e) arm's null control)"
+  (cd "$RQ/wt" && git checkout -q main && printf 'm\n' > f && git add f && git commit -qm conflicting && git push -q origin main && git checkout -q fix/t) >/dev/null 2>&1
+  st "$(msteps | grep -c '^REFUSE merged tree rc=1')" 1 "a head that does not merge cleanly with main is refused, never measured on HEAD alone"
+  # The receipt: a passing full run with a body over a clean tree, and nothing else.
+  rw() { (cd "$RQ/wt" && rm -f "$(receipt_file)" && say() { rsay "$@"; } && receipt_write "$1" "$2" "${3-$RH}" >/dev/null && cat "$(receipt_file)" 2>/dev/null); }
+  RH="$(git -C "$RQ/wt" rev-parse HEAD) $(git -C "$RQ/wt" rev-parse 'HEAD^{tree}')"
+  st "$(rw 0 body.md)" "$RH" "receipt: a passing run with a body writes <HEAD sha> <tree sha> in the git dir"
+  st "$(PREPR_SKIP_CLOSURES=1 rw 0 body.md)" "$RH" "receipt: PREPR_SKIP_CLOSURES alone still writes one"
+  st "$(rw 1 body.md)" "" "receipt: a refused run writes none"
+  st "$(rw 0 '')" "" "receipt: a run with no body writes none"
+  st "$(PREPR_SKIP_CODE=x rw 0 body.md)" "" "receipt: a PREPR_SKIP_CODE run (app_push --reuse) writes none"
+  st "$(PREPR_SKIP_ANY=1 rw 0 body.md)" "" "receipt: any other PREPR_SKIP_* writes none"
+  (printf 'dirty\n' >> "$RQ/wt/f")
+  st "$(rw 0 body.md)" "" "receipt: a dirty tree writes none"
+  (cd "$RQ/wt" && git checkout -q f)
+  # The HEAD the run started on (the reviewer's ev/midrun.sh, function-level): a
+  # commit landing while the steps ran is refused, never receipted; the first
+  # receipt row, its start unmoved, is the null control.
+  rwm() { (cd "$RQ/wt" && rm -f "$(receipt_file)" && printf 'mid\n' > mid && git add mid && git commit -qm mid \
+    && say() { rsay "$@"; } && step() { rstep "$@"; } \
+    && printf '%s|%s' "$(receipt_write 0 body.md "$RH" | grep -c '^REFUSE receipt rc=1$')" "$(cat "$(receipt_file)" 2>/dev/null)"; git reset -q --hard HEAD~1); }
+  st "$(rwm)" "1|" "receipt: HEAD moved past the run's start (a commit landing mid-run) is refused and writes none"
+  st "$(rw 0 body.md '')" "" "receipt: a run whose start HEAD was not read writes none"
+  (cd "$RQ/wt" && rm -f "$(receipt_file)" && bash "$OLDPWD/tools/pr/prepr.sh" --body-check "$RQ/none.md" >/dev/null 2>&1)
+  st "$([ -f "$(git -C "$RQ/wt" rev-parse --absolute-git-dir)/hpo-prepr-receipt" ] && echo written)" "" "receipt: --body-check writes none"
+  # body_push.sh's trailer, extracted from it: only the receipt at this code head, with its tree.
+  eval "$(sed -n '/^prepr_trailer() {/,/^}/p' tools/audit/seat/body_push.sh)"
+  (cd "$RQ/wt" && say() { :; } && receipt_write 0 body.md "$RH")
+  st "$(prepr_trailer "$RQ/wt" "$(git -C "$RQ/wt" rev-parse HEAD)")" "Prepr: $RH" "body_push: the receipt at the code head becomes the Prepr: trailer"
+  st "$(prepr_trailer "$RQ/wt" "$(git -C "$RQ/wt" rev-parse HEAD~1)")" "" "body_push: a receipt at another sha gives none"
+  printf '%s %s\n' "$(git -C "$RQ/wt" rev-parse HEAD)" "$(git -C "$RQ/wt" rev-parse 'HEAD~1^{tree}')" > "$(git -C "$RQ/wt" rev-parse --absolute-git-dir)/hpo-prepr-receipt"
+  st "$(prepr_trailer "$RQ/wt" "$(git -C "$RQ/wt" rev-parse HEAD)")" "" "body_push: a receipt whose tree is not the head's gives none"
+  printf '%s %s\n' "$(git -C "$RQ/wt" rev-parse HEAD~1)" "$(git -C "$RQ/wt" rev-parse 'HEAD^{tree}')" > "$(git -C "$RQ/wt" rev-parse --absolute-git-dir)/hpo-prepr-receipt"
+  st "$(prepr_trailer "$RQ/wt" "$(git -C "$RQ/wt" rev-parse HEAD)")" "" "body_push: a receipt whose tree is the head's but whose sha is not gives none"
+  # (a): a PREPR_SKIP_CODE run takes no heavy slot and runs no code-keyed step, but
+  # runs the merged-tree steps through the main flow's own call; and, given a body,
+  # it removes an earlier receipt first, so a run that writes none leaves none.
+  RA=$(cd "$RQ/wt" && git reset -q --hard origin/main~1 && printf 'stale\n' > "$(receipt_file)" \
+    && printf '## Head\n\n`%s`\n' "$(git rev-parse HEAD)" > "$RQ/a.md" \
+    && PREPR_SKIP_CODE=0123456789abcdef0123456789abcdef01234567 PREPR_VERBOSE=1 timeout 300 bash "$OLDPWD/tools/pr/prepr.sh" "$RQ/a.md" 2>&1)
+  st "$(printf '%s\n' "$RA" | grep -cE '^  [a-zA-Z]+ +(heavy slot|policy_lint|self-test|agreement lane|gate priority) ')$(printf '%s\n' "$RA" | grep -c '^  ok  *code steps  ')" 01 "(a) a PREPR_SKIP_CODE run takes no heavy slot and drops the code-keyed steps"
+  st "$(printf '%s\n' "$RA" | grep -cE '^  [a-zA-Z]+ +merged structure ')$(printf '%s\n' "$RA" | grep -cE '^  [a-zA-Z]+ +ci predict ')" 11 "(a) and runs tests/structure.py and ci predict on HEAD merged with main, once each"
+  st "$([ -f "$(git -C "$RQ/wt" rev-parse --absolute-git-dir)/hpo-prepr-receipt" ] && echo left)" "" "(a) a run with a body removes an earlier receipt first, so one that writes none leaves none"
+  rm -rf "$RQ"
+
   printf '\n%s passed, %s failed\n' "$st_pass" "$st_fail"
   [ "$st_fail" -eq 0 ] || exit 2
   exit 0
@@ -3860,7 +4016,10 @@ if [ -n "${1:-}" ]; then
   fi
   say ok "body path" "not directly in a shared root"
   [ -z "${PREPR_BODY_PATH_ONLY:-}" ] || exit 0
+  # An earlier run's receipt goes first, so a run that fails leaves none (`receipt_write`).
+  rm -f "$(receipt_file)" 2>/dev/null
 fi
+RUN_START=$(receipt_line)  # the HEAD every step below measures; `receipt_write` refuses any other
 
 # --- 1. the merge base resolves.
 # A shallow clone answers "no common ancestor" and every scoped command below
@@ -3872,6 +4031,12 @@ if [ -z "$BASE" ]; then
 fi
 step "merge-base" 0 "$BASE"
 summary_start
+# PREPR_SKIP_CODE=<sha> is app_push.sh --reuse's (P386): the receipt of a full run
+# at that code sha was found and the head is its clean merge with the live head
+# and main, so the steps keyed to the code alone are dropped and no heavy slot is
+# taken; the steps keyed to main, the body or the merge still run (`merged_steps`).
+REUSE=${PREPR_SKIP_CODE:-}
+[ -z "$REUSE" ] || say ok "code steps" "reused from the receipt at ${REUSE:0:12}: no heavy slot, and the steps keyed to the code alone are dropped"
 
 # --- 1a. no transport file in any commit the branch adds (`transport_in_ancestry`).
 TRANSPORT=$(transport_in_ancestry "$BASE" HEAD)
@@ -3908,6 +4073,12 @@ if [ -n "${1:-}" ] && [ "${1:-}" != "--self-test" ] && [ -f "$1" ]; then
   fi
 fi
 
+# One interpreter resolution per run, shared by steps 6a and 6c (`recorder_python`).
+PREPR_RECORDER_CACHE=/tmp/prepr-recpy.$$; : > "$PREPR_RECORDER_CACHE"  # not exported: the nested --self-test must resolve afresh
+
+if [ -n "$REUSE" ]; then
+  say skip "code-keyed steps" "PREPR_SKIP_CODE: heavy slot, gate mode, policy_lint, mutants, rules_sync, fragments, hooks, codeowners_gap, machinery ratchet, brief_lint, field coverage, agreement lane, register check"
+else
 # --- 1b0. the gate-lease priority of this branch's group (tvofi, 2026-10-20).
 # The lease is generic: it orders waiters by an integer and never decides who
 # deserves one. This step supplies the integer from tools/pr/gate_priority.py,
@@ -3979,9 +4150,6 @@ take_slot() { # idempotent: the first call takes (or joins) the slot, later call
   rm -f "$slot_stderr"
 }
 
-# One interpreter resolution per run, shared by steps 6a and 6c (`recorder_python`).
-PREPR_RECORDER_CACHE=/tmp/prepr-recpy.$$; : > "$PREPR_RECORDER_CACHE"  # not exported: the nested --self-test must resolve afresh
-
 # --- 2. the scoped gate's MODE line, printed rather than inferred.
 # CLAUDE.md rule 1: `MODE: SCOPED -- 0 script(s) run` and `MODE: FULL` both
 # print zero and mean opposite things. Printing it is the whole step; a seat
@@ -4116,6 +4284,7 @@ step "register check" $? "$(tail -1 /tmp/prepr-fl.$$)"
 rm -f /tmp/prepr-fl.$$
 fi
 rm -f "${HEAVY_PLAN:-}"
+fi  # the code-keyed steps, PREPR_SKIP_CODE's first group
 
 # --- 3f6. no tracked script, workflow or decision record tied to a temp or
 # machine path, which `instrument-self-tests` runs on the branch's own copy.
@@ -4129,6 +4298,10 @@ rm -f /tmp/prepr-tp.$$
 PRIVACY_LINE=$(privacy_line)
 step "ref privacy" $? "$PRIVACY_LINE"
 
+if [ -n "$REUSE" ]; then
+  say skip "code-keyed steps" "PREPR_SKIP_CODE: pinned graders, self-test, wave-script"
+else
+
 # --- 3g. every grader a pinned job runs has a local path here, or a reason,
 # and the reader understood every pinned job (`pinned_verdict` above).
 VERDICT=$(pinned_verdict "$PREPR_PATH" .github/workflows/*.yml)
@@ -4176,6 +4349,7 @@ else
   say skip "wave-script" "no change to the script, the checker, the rosters, the briefs or a pinned path"
 fi
 rm -f /tmp/prepr-wv.$$
+fi  # the code-keyed steps, PREPR_SKIP_CODE's second group
 
 # --- 5. VERSION, the manifest and the notes heading are untouched.
 # Versions are assigned after the merge by tools/release/stamp.py. A branch that
@@ -4213,6 +4387,8 @@ step "claims hygiene" $? "$CLAIMS_LINE"
 # push that only re-bodies.
 if [ -n "${PREPR_SKIP_CLOSURES:-}" ]; then
   say skip "closures" "PREPR_SKIP_CLOSURES is set -- closures-autofix is the only check left"
+elif [ -n "${REUSE:-}" ]; then
+  say skip "closures" "PREPR_SKIP_CODE: the receipted run covered the code; closures-autofix covers the merge"
 else
   # The slot is taken only when the recorder will run: a scoped diff on a
   # machine that records here (`closures_owes_slot`); a skip or a full diff is CI's.
@@ -4230,12 +4406,15 @@ fi
 # it, recorded by CI's recorder (SELF-TEST READS, dev/audit/rca/R10-RCA-CLOSURE-ARGV.md):
 # seconds per such file, none on a diff that changes none.
 UNPINNED_SITES=/tmp/prepr-unpinned.$$
+if [ -z "$REUSE" ]; then  # under PREPR_SKIP_CODE, `merged_steps` runs it on the merged tree
 PREDICT_LINE=$(predict_line origin/main "$UNPINNED_SITES" "${1:-}" "" record)
 case $? in
   3) say skip "ci predict" "$PREDICT_LINE" ;;
   0) step "ci predict" 0 "$PREDICT_LINE" ;;
   *) step "ci predict" 1 "$PREDICT_LINE" ;;
 esac
+fi
+merged_steps "${1:-}" "$UNPINNED_SITES"
 if [ -s "$UNPINNED_SITES" ]; then
   say WARN "unpinned sites" "$(grep -c . "$UNPINNED_SITES") site(s) the diff adds with no pin -- the body owes each a line under ## Unpinned sites (step 7d)"
 fi
@@ -4248,6 +4427,9 @@ fi
 # nothing here refuses, and with MUTANT_CMD unset the step skips. The cap keeps
 # the in-tree tier fast; the heavy pass (MUTANT_MAX=0, all mutants) is a cloud
 # seat's.
+if [ -n "$REUSE" ]; then
+  say skip "code-keyed steps" "PREPR_SKIP_CODE: diff mutants, no-copies"
+else
 if [ -z "${MUTANT_CMD:-}" ]; then
   say skip "diff mutants" "MUTANT_CMD unset -- set it to the group's self-test or features_block.py call to mutate the diff's added lines (report only)"
 elif [ ! -f tools/audit/seat/mutant_run.py ]; then
@@ -4281,7 +4463,9 @@ if diff_paths "$BASE" "$COPY_PATHS"; then
 else
   step "no-copies" 1 "the changed-path list did not derive from $BASE...HEAD, so no-copies was not run"
 fi
-rm -f "$COPY_PATHS" "$PREPR_RECORDER_CACHE"
+rm -f "$COPY_PATHS"
+fi  # the code-keyed steps, PREPR_SKIP_CODE's third group
+rm -f "$PREPR_RECORDER_CACHE"
 
 # --- 6e. no moved path re-added: tests.yml's fast job runs the layout guard;
 # `moved_line` above, 0.4 to 2.1 s. It reads the index against $BASE, so it needs
@@ -4295,6 +4479,9 @@ esac
 
 # --- 6f. no raw git init/clone: governance.yml's `throwaway_git.py --check`;
 # `throwaway_line` above. Reads the committed tree at HEAD.
+if [ -n "$REUSE" ]; then
+  say skip "code-keyed steps" "PREPR_SKIP_CODE: throwaway git, claims register"
+else
 THROWAWAY_LINE=$(throwaway_line "$PWD")
 case $? in
   3) say skip "throwaway git" "$THROWAWAY_LINE" ;;
@@ -4320,6 +4507,7 @@ else
   esac
 fi
 rm -rf "$CR" "$CR.paths" "$CR.arch"
+fi  # the code-keyed steps, PREPR_SKIP_CODE's fourth group
 
 # --- 7. the body, when one was passed.
 BODY="${1:-}"
@@ -4436,6 +4624,7 @@ if [ -n "$ORDER" ]; then
 fi
 
 rm -f "${UNPINNED_SITES:-}"
+receipt_write "$rc" "${BODY:-}" "$RUN_START"
 echo
 echo "PRE-PR: $(git rev-parse HEAD) $digest"
 summary_end "$(git rev-parse HEAD)"

## Before you return the verdict (P275)
Run `python3 -I tools/audit/carry_audit.py check --body <PR body file> --comments <file holding [{"id": 0, "body": <verdict.md text>}]>`. Give every reported item its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>`;
an evidence line flagged by its wording takes `Carry: dismissed: evidence, not a finding`. Return the verdict only at rc 0.
