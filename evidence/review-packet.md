# Review packet #3592
head: 897c777b23ca69cac35183ff1a88f1483a8ccdb1
base: d2e7805b7cf91cc8231729ef29383b3ae67a27ae

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: red
CodeQL id=132563719203 success
arch-score / arch-score id=132563700209 success
arm id=132563457882 skipped
budget-raise-gate / budget-raise-gate id=132563700197 success
cancel-superseded id=132563461007 success
codeql id=132563701162 skipped
codeql / Analyze (actions) id=132563660075 success
codeql / Analyze (javascript-typescript) id=132563660054 success
codeql / Analyze (python) id=132563660063 success
gate id=132564060072 failure
governance id=132563701705 skipped
governance / delivery-status id=132563660060 success
governance / delivery-status-publish id=132563661294 skipped
governance / env-matrix id=132563660097 in_progress
governance / instrument-self-tests id=132563660107 in_progress
governance / policy-docs id=132563660080 success
governance / record id=132563661337 skipped
governance / wave-script id=132563660094 success
hassfest id=132563701192 skipped
hassfest / hassfest id=132563659912 success
kernel-points id=132563701561 skipped
pr-contract id=132564060748 skipped
prelude id=132563461312 success
refresh id=132563461206 success
sweep-self id=132564273106 skipped
tests id=132563701274 skipped
tests / arch-instrument id=132563886349 success
tests / briefs id=132563660103 success
tests / browser id=132563885915 success
tests / closure-scope id=132563660186 success
tests / closures id=132563885941 in_progress
tests / coverage id=132563885890 in_progress
tests / fast (3.14) id=132563885877 in_progress
tests / mutation id=132563660114 success
tests / mutation-autofix id=132563946280 skipped
tests / mutation-pins id=132563945988 skipped
tests / nightly-ha id=132563887345 skipped
tests / nightly-status id=132563660116 failure
tests / replay id=132563887988 skipped
tests / typing id=132563885878 success
validate id=132563701445 skipped
validate / validate-hacs id=132563660139 success

## Refusals
introduced-red: unreadable: head governance / instrument-self-tests job 132563660107: in_progress has not concluded: an introduced red cannot be ruled out (fail closed)

## Advisories
hot-file: HPO_BUS_TRAIN_STATE is unset, so every merge verdict reads unboarded
required-wait: required context `gate` reads concluded failure at 897c777b23ca69cac35183ff1a88f1483a8ccdb1 in the digest, but merge_train.py classify --pr reads WAIT (pending: gate red: none): classify decides, as bus.sh's dispatch does, and a pending check never refuses

## carry_audit at the head
NOTE body item 35737f5a: R11-INTAKE-R10-RESIDUE
CARRY-AUDIT: 1 finding item(s): 1 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
FIGURES: 0 resolved, 0 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
none

## Review scope: full (no verdict on verdict/<pr> names the reviewed head cb803e9eedff0a2ea947110e1321cdd6afe0b1d6, so there is no finding to confirm resolved)

## Three-dot diff
diff --git a/dev/programme/delivery/3592.md b/dev/programme/delivery/3592.md
new file mode 100644
index 0000000000..3850a7de00
--- /dev/null
+++ b/dev/programme/delivery/3592.md
@@ -0,0 +1 @@
+- [#3592](https://github.com/tvofi/heatpump_optimizer/pull/3592) — **open**, R10-HOTFIX-CARRY-TIP-SIGPIPE: the carry check reads an own branch tip among many heads (R10-HOTFIX-CARRY-TIP-SIGPIPE)
diff --git a/tools/audit/seat/bus.sh b/tools/audit/seat/bus.sh
index ac8d73abae..3ac4d9b30d 100755
--- a/tools/audit/seat/bus.sh
+++ b/tools/audit/seat/bus.sh
@@ -653,7 +653,7 @@ three_rounds() { # pr past-three-reason -> 0 to dispatch; else why
   [ "$k" -lt 4 ] || { printf '#%s has %s blocked rounds: its re-cut was blocked again, so split or close it (the orchestrator), or pass --past-three <reason>' "$1" "$k"; return 1; }
   body=$(${HPO_BUS_GH:-gh} api "repos/$REPO/pulls/$1" --jq .body) \
     || { printf 'cannot read #%s'"'"'s body to find its ## Re-cut note' "$1"; return 1; }
-  printf '%s\n' "$body" | grep -q '^## Re-cut[[:space:]]*$' && return 0
+  grep -q '^## Re-cut[[:space:]]*$' <<<"$body" && return 0  # a here-string: a pipe into grep -q SIGPIPEs a long body's writer
   printf '#%s has %s blocked round(s): a fourth needs the body replaced under a ## Re-cut note (fixer.md), or --past-three <reason>' "$1" "$k"
   return 1
 }
diff --git a/tools/audit/seat/handoff_push.sh b/tools/audit/seat/handoff_push.sh
index ff10756588..92bacec511 100644
--- a/tools/audit/seat/handoff_push.sh
+++ b/tools/audit/seat/handoff_push.sh
@@ -141,7 +141,7 @@ CODE=$(git rev-parse "$CODE")
 git fetch -q origin main || { echo "could not fetch origin/main to judge $CODE over it"; exit 1; }
 python3 -I "$SEAT/ref_privacy.py" guard --ref "$BR" --commits "$CODE" --over refs/remotes/origin/main \
   || { echo "REFUSE: a commit handoff/$TOPIC adds over main carries a tool's attribution or names this host; nothing pushed"; exit 1; }
-git diff --no-renames --name-only "$CODE" "$T" | grep -vqE '^handoff/' && echo "note: tip adds non-handoff files over $CODE (a later main merge?) -- pushing the code head only"
+git diff --no-renames --name-only "$CODE" "$T" | grep -vE '^handoff/' >/dev/null && echo "note: tip adds non-handoff files over $CODE (a later main merge?) -- pushing the code head only"
 # The body: BODY.md at the tip of the orphan ref handoff-body/$TOPIC (body_push.sh), else the legacy
 # transport commit above the code head, until no open handoff carries one.
 # The body is read from the sha origin ANSWERED for the ref, never FETCH_HEAD.
diff --git a/tools/audit/seat/open_pr.sh b/tools/audit/seat/open_pr.sh
index 2070d94970..a77c35c260 100755
--- a/tools/audit/seat/open_pr.sh
+++ b/tools/audit/seat/open_pr.sh
@@ -45,7 +45,7 @@ pr_state_root; D=$PR_STATE/pr/$T; WT=$D/wt; BR=${BR:-fix/$T}; R=tvofi/heatpump_o
 # branch it holds names the lock of the run holding it. A second opener adopts that branch and meets the first's lock
 # (BUSY) before it writes the shared body.md, not a -pr lock of its own. A detached worktree holds no branch: a
 # finished run's leftover, which takes the -pr name below as a lone run does.
-OP_REG=$(git -C "$M" worktree list --porcelain | awk -v w="worktree $WT" '$0==w{f=1;next} f&&/^branch /{sub("refs/heads/","",$2);print $2;exit} f&&$0==""{exit}')  # mut:opreg
+OP_REG=$(awk -v w="worktree $WT" '$0==w{f=1;next} f&&/^branch /{sub("refs/heads/","",$2);print $2;exit} f&&$0==""{exit}' <<<"$(git -C "$M" worktree list --porcelain)")  # mut:opreg
 if [ -n "${OP_REG:-}" ] && [ -z "${BR_FIXED:-}" ]; then BR=$OP_REG
 elif git -C "$M" show-ref -q --verify refs/heads/$BR && [ -z "${BR_FIXED:-}" ]; then BR=$BR-pr; fi  # a seat often holds a local branch of the default name
 mkdir -p "$D"; cd "$M"
@@ -122,7 +122,8 @@ $(tail -n 20 $D/fig-$1.log)"; echo "$PR_NAME: $OP_WHY" >&2; return 1
 op_clear_leftover() { # a closed-after-p2 open leaves its branch and detached checkout; both go when origin holds all of them
   git -C "$M" worktree prune
   git -C "$M" fetch -q origin "refs/heads/$BR:refs/remotes/origin/$BR" 2>/dev/null || :
-  if git -C "$M" worktree list --porcelain | grep -qxF "worktree $WT"; then  # a stray unregistered directory still stops at worktree add
+  # A here-string, not a pipe: under pr_trap's pipefail a grep -q leaving at an early match SIGPIPEs a long list (141)
+  if grep -qxF "worktree $WT" <<<"$(git -C "$M" worktree list --porcelain)"; then  # a stray unregistered directory still stops at worktree add
     [ -z "$(git -C "$WT" status --porcelain 2>/dev/null)" ] && git -C "$WT" merge-base --is-ancestor HEAD "origin/$BR" 2>/dev/null \
       || pr_refuse "a left-over checkout $WT holds work origin/$BR lacks; keep or remove it, then re-run"
     git -C "$M" worktree remove --force "$WT"
diff --git a/tools/audit/seat/pr_args.sh b/tools/audit/seat/pr_args.sh
index dbf53479dc..fb50e2431e 100644
--- a/tools/audit/seat/pr_args.sh
+++ b/tools/audit/seat/pr_args.sh
@@ -445,30 +445,32 @@ pr_pushers() { # [<root>] [<rev>]: the census; one line per seam, exit 1 on any
     found=$(git -C "$root" grep -lE "$PR_PUSHER_RULE" -- 'tools/*.sh' 'tools/*.py' 'tools/*.mjs' 'tools/*.js')
   fi
   for f in $found; do
-    kind=$(printf '%s\n' "$PR_PUSHERS" | awk -v f="$f" '$1 == f { print $2; exit }')
+    kind=$(awk -v f="$f" '$1 == f { print $2; exit }' <<<"$PR_PUSHERS")
     if [ -n "$rev" ]; then txt=$(git -C "$root" show "$rev:$f"); else txt=$(cat "$root/$f"); fi
     txt=$(printf '%s\n' "$txt" | grep -vE '^[[:space:]]*#')  # a comment runs nothing
     case $kind in
       '') echo "OPEN $f: undispositioned -- it names a pusher; give it an entry in PR_PUSHERS"; bad=1 ;;
       runner)
-        if ! printf '%s\n' "$txt" | grep -qE '(^|[;{[:space:]])pr_exit_trap([[:space:]]|$)'; then
+        # Here-strings, not `printf | grep -q`: a script's whole text overflows the pipe, and a
+        # grep that leaves at its match SIGPIPEs the writer (141 under pipefail).
+        if ! grep -qE '(^|[;{[:space:]])pr_exit_trap([[:space:]]|$)' <<<"$txt"; then
           echo "OPEN $f runner: no pr_exit_trap, so a stop leaves its tree"; bad=1
-        elif printf '%s\n' "$txt" | grep -E 'bash "\$(_push|prepr)"' \
+        elif grep -E 'bash "\$(_push|prepr)"' <<<"$txt" \
              | sed -E 's/[0-9]*[<>]&[0-9-]*//g; s/&>//g; s/&&//g' | grep -qv '&'; then  # `2>&1` and `&&` background nothing
           echo "OPEN $f runner: a push runs in the foreground, so an INT waits behind it"; bad=1
-        elif printf '%s\n' "$txt" | grep -qE '(^|[;{[:space:]])pr_branch_lock[[:space:]]' \
-             && printf '%s\n' "$txt" | grep -E 'bash "\$(_push|prepr)"' | grep -qv 'pr_push_hold'; then
+        elif grep -qE '(^|[;{[:space:]])pr_branch_lock[[:space:]]' <<<"$txt" \
+             && grep -E 'bash "\$(_push|prepr)"' <<<"$txt" | grep -qv 'pr_push_hold'; then
           echo "OPEN $f runner: a push under the branch lock holds no push lock, so the lock can end before it"; bad=1
         else echo "ok   $f runner"; fi ;;
       runner-py)
-        if printf '%s\n' "$txt" | grep -qF '.terminate()' && printf '%s\n' "$txt" | grep -qE '^[[:space:]]+stop_on_signal\(\)'; then
+        if grep -qF '.terminate()' <<<"$txt" && grep -qE '^[[:space:]]+stop_on_signal\(\)' <<<"$txt"; then
           echo "ok   $f runner-py"
         else echo "OPEN $f runner-py: a stop SIGKILLs or orphans its tool"; bad=1; fi ;;
       *) echo "ok   $f $kind" ;;
     esac
   done
   for f in $(printf '%s\n' "$PR_PUSHERS" | awk '{ print $1 }'); do
-    printf '%s\n' $found | grep -qxF "$f" || { echo "OPEN $f: stale -- the rule no longer returns it"; bad=1; }
+    grep -qxF "$f" <<<"$found" || { echo "OPEN $f: stale -- the rule no longer returns it"; bad=1; }
   done
   [ "$bad" = 0 ]
 }
@@ -1443,6 +1445,13 @@ STUB
   ck "open_pr: a re-run after an open closed at its row push clears the left-over branch and worktree and opens" $?
   figrun opfig2 block; figrun opclear block keep; [ "$(cat "$t/frc")" != 0 ] && [ "$(cat "$t/frow")" = 0 ]
   ck "  mutant mut:opclear (its line deleted): the re-run fails at git worktree add -b on the left-over branch (the defect)" $?
+  # The same re-run on a host with many worktrees: `worktree list --porcelain | grep -q` under pr_trap's
+  # pipefail read the left-over checkout, listed early, as absent once the list outgrew the pipe (SIGPIPE,
+  # 141), so it was never removed. The wrapper appends 300 KB of entries after git's own list.
+  mkdir -p "$t/wtpad"; ( k=0; while [ "$k" -lt 3000 ]; do printf 'worktree /nonexistent/pad-%d\nHEAD %040d\ndetached\n\n' "$k" "$k"; k=$((k + 1)); done ) > "$t/wtpad/list"
+  printf '#!/bin/bash\n"%s" "$@" || exit\ncase " $* " in *" worktree list --porcelain "*) exec cat "%s" ;; esac\n' "$(command -v git)" "$t/wtpad/list" > "$t/wtpad/git"; chmod +x "$t/wtpad/git"
+  figrun opfig2 block; PATH="$t/wtpad:$PATH" figrun - block keep; [ "$(cat "$t/frc")" = 0 ] && [ "$(cat "$t/frow")" = 1 ]
+  ck "open_pr: the same re-run with 3000 more worktrees listed after the left-over one still clears it and opens" $?
   # R10-HOTFIX-UPDATEPR-FIGURE-REFRESH: update_pr.sh re-renders the body's figure blocks at the head it
   # pushes (moved-head path, before app_push) or patches (body-only path, before body_patch.sh), as
   # open_pr.sh's op_figures does. fix/g starts at $base; handoff/f's pusher stub is lint's figure-block
diff --git a/tools/pr/app_approve.sh b/tools/pr/app_approve.sh
index 8277a21d9c..f08a336c4b 100755
--- a/tools/pr/app_approve.sh
+++ b/tools/pr/app_approve.sh
@@ -154,7 +154,10 @@ gh_transient() { # gh's stderr -> 0 when another read may ride the failure out
     403) printf '%s\n' "$status" | grep -qi 'secondary rate limit'; return ;;
     ?*) return 1 ;;
   esac
-  printf '%s\n' "$1" | grep -qE '^Get "https?://[^"]*": |^error connecting to '
+  # A here-string, not `printf | grep -q`: grep leaves at its match, and a
+  # writer still writing takes SIGPIPE -- 141 under pipefail, a refusal of a
+  # transient read; where SIGPIPE is ignored (CI), a "write error" on stderr.
+  grep -qE '^Get "https?://[^"]*": |^error connecting to ' <<<"$1"
 }
 
 # git's stderr -> 0 when another fetch may ride the failure out: gh_read.py's
@@ -300,7 +303,9 @@ carry() {
   if [ -n "$(git rev-list -n 1 "$v..$h" --not "$main" 2>/dev/null)" ]; then
     retry_with git_transient heads git ls-remote --heads origin \
       || { echo "origin's branch heads could not be listed, so whether $h is a head of ours is unknown (fail closed): $GH_ERR"; return 1; }
-    printf '%s\n' "$heads" | grep -q "^$h[[:space:]]refs/heads/" || ours=0
+    # A here-string: origin lists thousands of heads, and `printf | grep -q`
+    # under pipefail read its own early match as no match (SIGPIPE, 141).
+    grep -q "^$h[[:space:]]refs/heads/" <<<"$heads" || ours=0
   fi
   # Read at main, never at a head: a branch that gave a file a driver would
   # otherwise take it out of the comparisons itself.
@@ -437,7 +442,7 @@ carry() {
         bt=$(git diff --no-renames --name-only "$c^" "$c")
         while IFS= read -r e; do
           [ -z "$e" ] && continue
-          if printf '%s\n' "$bt" | grep -qxF "$e"; then
+          if grep -qxF "$e" <<<"$bt"; then
             bots="$bots$e"$'\n'
           else
             while IFS= read -r p; do
@@ -1536,6 +1541,13 @@ while IFS=$'\t' read -r a k l; do
 done < "$W/alts"
 st "$alt_bad" 0 "every alternative's inputs and near-misses classify as the table needs (production gh_transient)"
 st "$alt_out" 0 "and gh_transient prints nothing on either stream"
+# The row above flaked in CI (job 132518925875): there SIGPIPE is ignored, so a
+# `printf | grep -q` whose grep left at an early match printed "write error:
+# Broken pipe" whenever the writer was still writing. A transient line followed
+# by more than a pipe buffer makes that race certain, in both signal regimes.
+x="error connecting to api.github.com"$'\n'"$(head -c 200000 /dev/zero | tr '\0' x)"
+gh_transient "$x"; st $? 0 "gh_transient: an early transient line in a long stderr is still transient"
+st "$( (trap '' PIPE; gh_transient "$x" || echo refuse) 2>&1)" "" "(and with SIGPIPE ignored, as in CI, it prints nothing and still classifies transient)"
 st "$(cut -f1 "$W/alts" | sort -u | tr '\n' '|')" "$(printf '%s\n' "$ALTS" | tr '\n' '|')" \
    "(the table keys exactly the alternatives gh_transient's source holds)"
 st "$(cut -f1,2 "$W/alts" | sort -u | cut -f1 | uniq -c | awk '$1 != 2' | wc -l | tr -d ' ')" 0 \
@@ -2063,6 +2075,25 @@ printf '#!/bin/bash\n[ "$1" = ls-remote ] && { echo "fatal: repository not found
 ( cd "$W/clone" && PATH="$W/lsfail:$PATH" bash "$SELF" --carry "$V_F" "$H_FMERGE" origin/main ) > "$W/carry.out" 2>&1
 st $? 1 "NO CARRY: origin's branch heads unreadable, even for an automatic merge of main (fail closed)"
 st "$(grep -c "could not be listed" "$W/carry.out")" 1 "saying the heads could not be listed"
+# origin lists thousands of branch heads (7933 on 2026-11-14). A match that
+# stops reading early -- `printf | grep -q` under pipefail -- kills its writer
+# with SIGPIPE, and the pipeline's 141 read a head of ours as a fork's. The
+# stub answers with the head FIRST and 20000 heads after it, more than any pipe
+# buffer holds, so an early-exit reader fails here every time.
+mkdir -p "$W/lsbig"
+{ printf '%s\trefs/heads/carried-head\n' "$H_CILED"
+  i=0; while [ "$i" -lt 20000 ]; do printf '%040d\trefs/heads/filler-%d\n' "$i" "$i"; i=$((i + 1)); done; } > "$W/lsbig/ours"
+tail -n +2 "$W/lsbig/ours" > "$W/lsbig/fork"
+for f in ours fork; do
+  mkdir -p "$W/lsbig/$f.bin"
+  printf '#!/bin/bash\n[ "$1" = ls-remote ] && { cat "%s"; exit 0; }\nexec "%s" "$@"\n' "$W/lsbig/$f" "$REAL_GIT" > "$W/lsbig/$f.bin/git"
+  chmod +x "$W/lsbig/$f.bin/git"
+done
+( cd "$W/clone" && PATH="$W/lsbig/ours.bin:$PATH" bash "$SELF" --carry "$V" "$H_CILED" origin/main ) > "$W/carry.out" 2>&1
+st $? 0 "CARRY on a head of ours listed first among 20001 branch heads of origin"
+( cd "$W/clone" && PATH="$W/lsbig/fork.bin:$PATH" bash "$SELF" --carry "$V" "$H_CILED" origin/main ) > "$W/carry.out" 2>&1
+st $? 1 "NO CARRY: the same 20000 heads without it (null control)"
+st "$(grep -c "no branch tip of origin" "$W/carry.out")" 1 "refused as a head that is not ours"
 EVF="$W/ev-f"; mkdir -p "$EVF"; printf 'fix review at head %s\n' "$V" > "$EVF/verdict.md"
 CARRYF="[$(comment 2 "Fix review: merge $V" "$APPR" NONE "evidence: $EVF")]"
 setpr "$H_CILED"; mkcase botours open false "$H_CILED" "$CARRYF"

## Before you return the verdict (P275)
Run `python3 -I tools/audit/carry_audit.py check --body <PR body file> --comments <file holding [{"id": 0, "body": <verdict.md text>}]>`. Give every reported item its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>`;
an evidence line flagged by its wording takes `Carry: dismissed: evidence, not a finding`. Return the verdict only at rc 0.
