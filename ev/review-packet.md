# Review packet #3614
head: d24189bd656ff982867bff3c7f55df985e573214
base: b3831ff64eca1936f0b618193ee86c3e337b51a9

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: red
CodeQL id=132853805866 success
arch-score / arch-score id=132851979715 success
arm id=132850776835 skipped
budget-raise-gate / budget-raise-gate id=132851979602 success
cancel-superseded id=132850728883 success
codeql id=132851762490 skipped
codeql / Analyze (actions) id=132851979557 success
codeql / Analyze (javascript-typescript) id=132851979564 success
codeql / Analyze (python) id=132851979511 success
gate id=132853734896 failure
governance id=132851762316 skipped
governance / env-matrix id=132851979542 in_progress
governance / instrument-self-tests id=132851979573 in_progress
governance / policy-docs id=132851979630 success
governance / record id=132851980950 skipped
governance / wave-script id=132851979576 success
hassfest id=132851762385 skipped
hassfest / hassfest id=132851979496 success
kernel-points id=132851980174 skipped
pr-contract id=132853736684 skipped
prelude id=132850728865 success
refresh id=132850728616 success
sweep-self id=132854424658 skipped
tests id=132851763100 skipped
tests / arch-instrument id=132853909065 success
tests / briefs id=132851979517 success
tests / browser id=132853909078 in_progress
tests / closure-scope id=132851979624 success
tests / closures id=132853909119 in_progress
tests / coverage id=132853909239 in_progress
tests / fast (3.14) id=132853909068 in_progress
tests / mutation id=132851979504 success
tests / mutation-autofix id=132853543463 skipped
tests / mutation-pins id=132853543559 skipped
tests / nightly-ha id=132853910462 skipped
tests / nightly-status id=132851979558 success
tests / replay id=132853910609 skipped
tests / typing id=132853909261 success
validate id=132851763023 skipped
validate / validate-hacs id=132851979468 success

## Refusals
introduced-red: unreadable: head governance / instrument-self-tests job 132851979573: in_progress has not concluded: an introduced red cannot be ruled out (fail closed)

## Advisories
hot-file: HPO_BUS_TRAIN_STATE is unset, so every merge verdict reads unboarded
required-wait: required context `gate` reads concluded failure at d24189bd656ff982867bff3c7f55df985e573214 in the digest, but merge_train.py classify --pr reads WAIT (pending: gate red: none): classify decides, as bus.sh's dispatch does, and a pending check never refuses

## carry_audit at the head
CARRY-AUDIT: 0 finding item(s): 0 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
ok         bash tools/audit/seat/pr_args.sh --self-test
             `tools/audit/seat/pr_args.sh` is in the tree at this head
  ok         gh pr list
             gh pr list: every long flag accepted
  ok         bash tools/audit/seat/body_push.sh --self-test
             `tools/audit/seat/body_push.sh` is in the tree at this head
  unverified git archive origin/main tools tests
             `git archive` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals

FIGURES: 3 resolved, 1 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
none

## Review scope: delta (later round over the reviewed head 6dc42ccc267162b473d552d5f39f389d9c9a224e)
Confirm each finding of the previous verdict is resolved, re-read the live required checks, and review the delta below. Widen only to exactly the already-reviewed code a delta touching production code (custom_components/) puts at risk of being affected in a non-obvious way CI would not detect, naming the path and the risk in the verdict; an instrument, test, policy or body delta never justifies a wider review (fix-review.md step 12).

## Previous verdict at 6dc42ccc267162b473d552d5f39f389d9c9a224e
Fix review: blocked 6dc42ccc267162b473d552d5f39f389d9c9a224e class-open: tools/audit/seat/body_push.sh:175

bus-nonce: 1ba2f55ff2cd00bf075a06e2e2106054

## Block
The body's class rule (`grep -n "figure_block.py\" refresh" tools/audit/seat/*.sh`) returns three call sites at this head (ev/enumeration.txt): update_pr.sh:107 and open_pr.sh:122, both closed here, and `tools/audit/seat/body_push.sh:175`, which runs `figure_block.py refresh "$ABS"` with no `--base`, so it renders against figure_block.py's default `origin/main` (tools/pr/figure_block.py:280). It is neither in the diff nor dispositioned in the body's "Class seams" line, which lists two sites. body_push.sh is the handoff body push; the body must either close it (take the recorded base where a PR exists) or state why `origin/main` is correct there, as it does for op_figures p1.

## Evidence
- Head measured: 6dc42ccc267162b473d552d5f39f389d9c9a224e (ev/HEAD.txt). Round 1.
- classify at head: GREEN (ev/classify.txt). merge-tree against origin/main: clean (ev/merge-tree.txt).
- `pr_args.sh --self-test` at head: 269 checks, 0 failed (ev/pr_args-selftest.log), including mut:opbase and mut:updbase killed, the equal-base null control and the unreadable-base refusal. The two closed sites are sound.
- VERSION, manifest, notes, claim files, budgets and closures untouched.
- carry_audit: 0 findings.

## Delta diff: git diff 6dc42ccc267162b473d552d5f39f389d9c9a224e d24189bd656ff982867bff3c7f55df985e573214
diff --git a/tools/audit/seat/body_push.sh b/tools/audit/seat/body_push.sh
index d7603e2417..2e0b29497d 100644
--- a/tools/audit/seat/body_push.sh
+++ b/tools/audit/seat/body_push.sh
@@ -19,11 +19,13 @@ if [ "${1:-}" = "--self-test" ]; then
   FAILS=0; N=0; st() { N=$((N + 1)); if [ "$1" = "$2" ]; then echo "ok   $3"; else echo "FAIL $3 (got '$1', want '$2')"; FAILS=$((FAILS + 1)); fi; }
   # shellcheck source=../../../tests/throwaway_git.sh
   . "$SH/../../../tests/throwaway_git.sh"
-  mkcopy() { mkdir -p "$W/$1/audit/seat" "$W/$1/pr"; cp "$SH/ref_privacy.py" "$W/$1/audit/seat/"
-    if [ "$2" = real ]; then cp "$SELF" "$W/$1/audit/seat/body_push.sh"; else sed '/# mut:keep$/s/.*/    :/' "$SELF" > "$W/$1/audit/seat/body_push.sh"; fi
+  mkcopy() { mkdir -p "$W/$1/audit/seat" "$W/$1/pr"; cp "$SH/ref_privacy.py" "$SH/pr_args.sh" "$W/$1/audit/seat/"
+    case $2 in real) cp "$SELF" "$W/$1/audit/seat/body_push.sh";; bpbase) sed '/# mut:bpbase$/s/.*/    :/' "$SELF" > "$W/$1/audit/seat/body_push.sh";;
+      *) sed '/# mut:keep$/s/.*/    :/' "$SELF" > "$W/$1/audit/seat/body_push.sh";; esac
     printf '#!/bin/bash\n[ "$1" = --body-check ] && [ -f "$FLAGS/lint" ] && { echo lint-stub-refuses; exit 1; }\nexit 0\n' > "$W/$1/pr/prepr.sh"
-    printf 'import os\nopen(os.environ["FLAGS"] + "/refreshed", "w").close()\n' > "$W/$1/pr/figure_block.py"; }
-  mkcopy t real; mkcopy m mutant
+    printf 'import os, sys\nopen(os.environ["FLAGS"] + "/refreshed", "w").close()\nopen(os.environ["FLAGS"] + "/figbase", "a").write(sys.argv[sys.argv.index("--base") + 1] + "\\n")\n' > "$W/$1/pr/figure_block.py"; }
+  mkcopy t real; mkcopy m mutant; mkcopy b bpbase
+  mkdir -p "$W/bin"; printf '#!/bin/sh\ncase "$*" in api*pulls?state*) cat "$W/prn" ;; api*pulls/*) cat "$W/pullbase" ;; *) exit 99 ;; esac\n' > "$W/bin/gh"; chmod +x "$W/bin/gh"; : > "$W/prn"
   printf '#!/bin/bash\nexit 0\n' > "$W/packer"; printf '#!/bin/bash\n[ -f "$FLAGS/packet" ] && exit 1\nexit 0\n' > "$W/packer"
   printf '#!/bin/bash\n[ -f "$FLAGS/landed" ] && exit 1\nexit 0\n' > "$W/landed"; chmod +x "$W/packer" "$W/landed"
   throwaway_git_init "$W/o.git" -q --bare; throwaway_git_init "$W/repo" -q
@@ -34,7 +36,7 @@ if [ "${1:-}" = "--self-test" ]; then
   # A hook that refuses any push to handoff-wip/, installed for the failed-keep arm only.
   printf '#!/bin/sh\nwhile read o n r; do case $r in refs/heads/handoff-wip/*) exit 1;; esac; done\n' > "$W/hook"; chmod +x "$W/hook"
   run() { # copy -> rc ; FLAGS names the refusal switches, out in $W/out
-    ( cd "$W/repo" && throwaway_git_env && FLAGS="$W/flags" HPO_HANDOFF_PACKER="$W/packer" HPO_HANDOFF_LANDED="$W/landed" \
+    ( cd "$W/repo" && throwaway_git_env && PATH="$W/bin:$PATH" W="$W" FLAGS="$W/flags" HPO_HANDOFF_PACKER="$W/packer" HPO_HANDOFF_LANDED="$W/landed" \
         bash "$W/$1/audit/seat/body_push.sh" t "$W/body.md" > "$W/out" 2>&1 ); }
   keepsha() { git -C "$W/o.git" rev-parse -q --verify refs/heads/handoff-wip/t-body 2>/dev/null || echo none; }
   drop() { git -C "$W/o.git" update-ref -d refs/heads/handoff-wip/t-body 2>/dev/null; rm -rf "$W/flags"; mkdir -p "$W/flags"; }
@@ -69,6 +71,25 @@ if [ "${1:-}" = "--self-test" ]; then
   st "$([ -f "$W/flags/refreshed" ] && echo ran || echo no)" ran "the seat-side figure-block refresh ran"
   drop; run m; st "$([ -f "$W/flags/refreshed" ] && echo ran || echo no)" no "MUTANT refresh deleted: the arm above would fail"
   st "$(git -C "$W/repo" merge-base --is-ancestor "$(git -C "$W/o.git" rev-parse handoff-body/t)" "$CODE" 2>/dev/null; echo $?)" 1 "(null) the published body is not in the code head's ancestry"
+  # R11-HOTFIX-FIGURE-BLOCK-BASE: the refresh takes the open pull request's recorded base.sha. A commit no branch
+  # holds stands for a base other than origin/main's tip (precondition asserted); the null control records equal bases.
+  MAINTIP=$(git -C "$W/repo" rev-parse origin/main); OLDBASE=$(git -C "$W/repo" commit-tree "$MAINTIP^{tree}" -m oldbase)
+  st "$([ "$OLDBASE" != "$MAINTIP" ] && echo differ || echo same)" differ "precondition: the stub's recorded base is not origin/main's tip"
+  figbase() { drop; run "${1:-t}"; rc=$?; tail -n 1 "$W/flags/figbase" 2>/dev/null || echo none; }
+  printf '%s\n' "$OLDBASE" > "$W/pullbase"; echo 5 > "$W/prn"
+  st "$(figbase)" origin/main "no fix/t on origin (no pull request yet): the refresh renders against origin/main"
+  git -C "$W/repo" push -q origin HEAD:refs/heads/fix/t
+  st "$(figbase)" "$OLDBASE" "a pull request exists: the refresh renders against its recorded base.sha, not origin/main"
+  printf '%s\n' "$MAINTIP" > "$W/pullbase"
+  st "$(figbase)" "$MAINTIP" "  null control: equal bases render the one sha, as before"
+  printf '%s\n' "$OLDBASE" > "$W/pullbase"
+  st "$(figbase b)" origin/main "  MUTANT mut:bpbase (its line deleted): the refresh falls back to origin/main, so the arm above would fail"
+  : > "$W/pullbase"; drop; git -C "$W/o.git" update-ref -d refs/heads/handoff-body/t; run t; rc=$?
+  st "$rc$([ -f "$W/flags/refreshed" ] && echo ran || echo no)" 1no "an unreadable recorded base refuses before the refresh"
+  st "$(git -C "$W/o.git" rev-parse -q --verify refs/heads/handoff-body/t 2>/dev/null || echo none)" none "... and pushes nothing"
+  : > "$W/prn"; printf '%s\n' "$OLDBASE" > "$W/pullbase"
+  st "$(figbase)" origin/main "fix/t on origin but no open pull request: origin/main"
+  git -C "$W/repo" push -q origin :refs/heads/fix/t; git -C "$W/o.git" update-ref -d refs/heads/handoff-body/t
   # head-stale: a body whose ## Head names another sha is refused and nothing is pushed; the fresh one (null) passes.
   OTHER=$(printf '%040d' 7); drop; git -C "$W/o.git" update-ref -d refs/heads/handoff-body/t
   printf '## Head\n\n%s\n\n## Other\n\n%s\n' "$OTHER" "$CODE" > "$W/body.md"; run t; rc=$?
@@ -146,6 +167,8 @@ fi
 # means a result (probe, design, verdict), which is no PR body. A handoff/<topic>
 # that is not this checkout's HEAD names a head the open will not run on.
 HERE=$(cd "$(dirname "$0")" && pwd)
+# shellcheck source=pr_args.sh
+. "$HERE/pr_args.sh"  # pr_recorded_base
 HREF=$(git ls-remote origin "refs/heads/handoff/$TOPIC") || { echo "body_push: could not read handoff/$TOPIC from origin" >&2; exit 1; }
 HREF=$(printf '%s\n' "$HREF" | awk 'NF { print $1; exit }')
 if [ -n "$HREF" ]; then
@@ -172,11 +195,22 @@ if [ -n "$HREF" ]; then
   (cd "$ROOT" && bash "$HERE/../../pr/prepr.sh" --fill-red "$ABS")
   # The seat-side writer re-renders every registered figure block at the code head with no
   # agent turn (card 7 option C); pr-contract only verifies. A refusal aborts the push (set -e).
-  (cd "$ROOT" && python3 -I "$HERE/../../pr/figure_block.py" refresh "$ABS") # mut:keep
+  # Its base is the one pr-contract verifies with: the open pull request's recorded base.sha (update_pr.sh,
+  # open_pr.sh's p2 take it), origin/main only where no pull request exists yet, which will record origin/main
+  # as it stands (open_pr.sh's p1). Origin holding fix/<topic> is how a pull request is known to exist; one
+  # whose recorded base cannot be read refuses, with nothing pushed.
   # The red-check arm reads the pull request's head ref over the network, so it
   # is asked for only when origin holds fix/<topic> (a first handoff has none).
-  PRB=""
-  [ -z "$(git ls-remote origin "refs/heads/fix/$TOPIC" 2>/dev/null)" ] || PRB="--pr-branch fix/$TOPIC"
+  PRB=""; FB=origin/main
+  if [ -n "$(git ls-remote origin "refs/heads/fix/$TOPIC" 2>/dev/null)" ]; then
+    PRB="--pr-branch fix/$TOPIC"
+    PRN=$(gh api "repos/tvofi/heatpump_optimizer/pulls?state=open&head=tvofi:fix/$TOPIC" --jq '.[0].number // empty') \
+      || { echo "body_push: REFUSE: the pull requests of fix/$TOPIC could not be listed, so the base its figure block is verified against is unknown" >&2; keep_refused; exit 1; }
+    if [ -n "$PRN" ]; then
+      FB=$(pr_recorded_base tvofi/heatpump_optimizer "$PRN") || { echo "body_push: REFUSE: the recorded base.sha of #$PRN could not be read, the base pr-contract verifies the figure block against" >&2; keep_refused; exit 1; }  # mut:bpbase
+    fi
+  fi
+  (cd "$ROOT" && python3 -I "$HERE/../../pr/figure_block.py" refresh "$ABS" --base "$FB") # mut:keep
   # shellcheck disable=SC2086 # PRB is empty or exactly two words
   if ! LINT=$(cd "$ROOT" && bash "$HERE/../../pr/prepr.sh" --body-check "$ABS" $PRB 2>&1); then
     printf '%s\n' "$LINT" >&2
diff --git a/tools/audit/seat/instruments/body_push.sh.md b/tools/audit/seat/instruments/body_push.sh.md
index 3e4434cdac..467e650cda 100644
--- a/tools/audit/seat/instruments/body_push.sh.md
+++ b/tools/audit/seat/instruments/body_push.sh.md
@@ -19,3 +19,4 @@
   `handoff-body-stale`, and a body naming a tip the PR head already holds is
   applied body-only (`update_pr.sh` with code `-`).
 - Refuses `head-stale` (exit 1, body kept at `handoff-wip/<topic>-body`) when the body's `## Head` does not name `handoff/<topic>`'s code sha: a repair body kept the previous handoff's head (#3212, #3230, #3231; R10-PROCESS-SLIM carry 1).
+- Renders the body's figure block (`figure_block.py refresh`) against the base `pr-contract` verifies with: the open pull request's recorded `base.sha` when origin holds `fix/<topic>` with an open pull request (read by `pr_args.sh`'s `pr_recorded_base`, as `update_pr.sh` and `open_pr.sh`'s p2 do), `origin/main` where none exists yet (R11-HOTFIX-FIGURE-BLOCK-BASE). An unreadable recorded base refuses, nothing pushed.

## Before you return the verdict (P275)
Run `python3 -I tools/audit/carry_audit.py check --body <PR body file> --comments <file holding [{"id": 0, "body": <verdict.md text>}]>`. Give every reported item its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>`;
an evidence line flagged by its wording takes `Carry: dismissed: evidence, not a finding`. Return the verdict only at rc 0.
