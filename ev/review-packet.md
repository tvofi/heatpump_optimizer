# Review packet #3549
head: 0e200f4995c2b708c75b5c2ba4307ef3e124a9ca
base: 3b9749dac55a85c200005352c661198c982e5799

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: red
CodeQL id=131902096360 success
arch-score / arch-score id=131902023220 success
arm id=131901667706 skipped
budget-raise-gate / budget-raise-gate id=131902023256 success
cancel-superseded id=131901665244 success
codeql id=131902025509 skipped
codeql / Analyze (actions) id=131902006006 success
codeql / Analyze (javascript-typescript) id=131902005944 success
codeql / Analyze (python) id=131902005885 success
gate id=131902876956 failure
governance id=131902025285 skipped
governance / delivery-status id=131902005987 success
governance / delivery-status-publish id=131902009448 skipped
governance / env-matrix id=131902006048 success
governance / instrument-self-tests id=131902005754 in_progress
governance / policy-docs id=131902005747 success
governance / record id=131902009472 skipped
governance / wave-script id=131902005874 success
hassfest id=131902024850 skipped
hassfest / hassfest id=131902005746 success
kernel-points id=131902024814 skipped
pr-contract id=131902878506 skipped
prelude id=131901664796 success
refresh id=131901665020 success
sweep-self id=131904506459 skipped
tests id=131902024583 skipped
tests / arch-instrument id=131902549148 success
tests / briefs id=131902006031 success
tests / browser id=131902549127 success
tests / claims-autofix id=131904131631 skipped
tests / closure-scope id=131902006041 success
tests / closures id=131902549164 in_progress
tests / coverage id=131902549163 in_progress
tests / fast (3.14) id=131902549146 success
tests / mutation id=131902005978 success
tests / mutation-autofix id=131902376693 skipped
tests / mutation-pins id=131902376170 skipped
tests / nightly-ha id=131902552238 skipped
tests / nightly-status id=131902005929 success
tests / replay id=131902552189 skipped
tests / typing id=131902549107 success
validate id=131902025015 skipped
validate / validate-hacs id=131902005900 success

## Refusals
introduced-red: unreadable: head governance / instrument-self-tests job 131902005754: in_progress has not concluded: an introduced red cannot be ruled out (fail closed)

## Advisories
hot-file: HPO_BUS_TRAIN_STATE is unset, so every merge verdict reads unboarded
required-wait: required context `gate` reads concluded failure at 0e200f4995c2b708c75b5c2ba4307ef3e124a9ca in the digest, but merge_train.py classify --pr reads WAIT (pending: gate red: none): classify decides, as bus.sh's dispatch does, and a pending check never refuses

## carry_audit at the head
CARRY-AUDIT: 0 finding item(s): 0 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
ok         bash tools/audit/seat/open_pr.sh --self-test
             `tools/audit/seat/open_pr.sh` is in the tree at this head
  ok         python3 tools/pr/ci_predict.py --self-test
             `tools/pr/ci_predict.py` is in the tree at this head
  unverified bash -n
             bash with no script argument
  ok         node tools/policy/brief_lint.mjs
             `tools/policy/brief_lint.mjs` is in the tree at this head

FIGURES: 3 resolved, 1 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
none

## Review scope: delta (later round over the reviewed head cde73e8b72fc563d515fd5ab66a6a12eec85698e)
Confirm each finding of the previous verdict is resolved, re-read the live required checks, and review the delta below. Widen only to exactly the already-reviewed code a delta touching production code (custom_components/) puts at risk of being affected in a non-obvious way CI would not detect, naming the path and the risk in the verdict; an instrument, test, policy or body delta never justifies a wider review (fix-review.md step 12).

## Previous verdict at cde73e8b72fc563d515fd5ab66a6a12eec85698e
Fix review: blocked cde73e8b72fc563d515fd5ab66a6a12eec85698e class-open: open_pr.sh mut:opreg predicate matches the logical $WT against git's physical worktree path, so a state dir reached through a symlink silently keeps the defect

bus-nonce: c04e83e9f6dd3d06bef25f6fb05f05da

## Block

Round 1. `tools/audit/seat/open_pr.sh` line `# mut:opreg` compares `worktree $WT`, with `WT=${HPO_STATE_DIR:-$HOME/.local/state/hpo}/pr/$T/wt` unresolved, against `git worktree list --porcelain`, which prints the worktree's physical (symlink-resolved) path. Measured: `git worktree add` at `~/symt/link/wt`, where `link -> real`, lists `worktree /root/symt/real/wt`. Whenever any component of the state-dir path is a symlink, OP_REG is empty, the second opener falls through to the `-pr` rename, takes its own lock and rewrites the shared body.md: the defect this PR fixes. The new self-test hides this domain: `dualrun` resolves its state dir with `pwd -P` before calling open_pr.sh. Perturbation: the same `dualrun` with the state dir passed through a symlink to that same resolved directory (ev/perturb_symlink.diff) turns the live case red: `FAIL open_pr: a second opener on a topic whose opener worktree is registered is BUSY (75), body.md byte-identical, the first opens`, `pr_args self-test: 247 checks, 1 failed` (ev/open_pr_selftest_symlink_perturb.txt). The unperturbed head passes 247/0 (ev/open_pr_selftest_head.txt). The body's `Known gap` covers only the detached-worktree case and leaves this domain undispositioned. Owed: resolve the path before the match (for example, compare against the physical path of `$D` once it exists, or canonicalise both sides) with a self-test case that passes the state dir through a symlink, or disposition this domain in the body. The same logical-against-physical comparison already exists at `open_pr.sh` (`grep -qxF "worktree $WT"`, the stray-directory guard) and `update_pr.sh` (`mut:elsewhere`). This PR does not introduce those sites; whoever fixes the predicate should check them too.

## Evidence

- Head reviewed: cde73e8b72fc563d515fd5ab66a6a12eec85698e (ev/HEAD.txt). It is still the live head of fix/r10-hotfix-opener-refusals per `git ls-remote` at verdict time. Base and merge base: 3b9749dac55a85c200005352c661198c982e5799. The roles diff merge-base...origin/main is empty, so the contract is current.
- RESULT figure 1: `bash tools/audit/seat/open_pr.sh --self-test` at the head ends `pr_args self-test: 247 checks, 0 failed`, rc 0. This matches the body.
- RESULT figure 2: `python3 tools/pr/ci_predict.py --self-test` at the head ends `ci_predict self-test: 0 failed`, rc 0. This matches the body.
- Mutation `mut:opreg` and `mut:headnote`: the in-harness mutant arms pass at the head (the mutants are detected). I did not plant a separate opreg mutant: the symlink perturbation empties OP_REG the same way, and the live case goes red.
- Mutation `mut:roundrefs` (my own): deleting the marked call line in ci_tree_run fails only the source-shape pin `ci_tree_run calls fetch_round_rosters on one # mut:roundrefs line` (rc 1, ev/mut_roundrefs.txt). Making `fetch_round_rosters` return early fails `fetch_round_rosters takes root's remote-tracking ref` (rc 1, ev/mut_fetch_noop.txt). The call site is pinned by source inspection, not behaviourally, and the body discloses this.
- Refspec parity: pr-contract.yml fetches `+refs/heads/handoff/audit-r*-roster:refs/remotes/origin/handoff/audit-r*-roster` from GitHub. The helper maps root's `refs/remotes/origin/...` to the same destination, which is the equivalent for a --shared local clone.
- Null controls: the lone-run control passes at the head. Part 2's tracking=False null passes.
- Merge with main: `git merge-tree --write-tree origin/main <head>` rc 0, no conflict (ev/merge_tree.txt).
- VERSION, the manifest, RELEASE_NOTES.md, the golden and claim files, the budgets and closures.json are untouched (ev/untouched.txt, empty diff). The claim files are not touched, so no drift claim is owed.
- tests/entities.py (env -u BASH_ENV) cannot run in this container: `ModuleNotFoundError: paho` under venv-ha (no homeassistant in venv-ci). The same failure occurs at the base, so it is environmental and not verified here; CI's run is the evidence (ev/entities_head.txt).
- Finder's harness: none named. This is a hotfix from root cause R10-RCA-OPENER-REFUSALS, and the fixer's self-test arms are the only harness.
- CI: classify printed `WAIT cde73e8b72fc563d515fd5ab66a6a12eec85698e pending: gate red: none` through 11:07 UTC (ev/classify_poll.txt). The verdict is blocked on the review itself, so I did not wait further. The review packet refused `introduced-red: unreadable` while instrument-self-tests was queued. No red has been read, so no `## Red checks` answer is owed.

## Delta diff: git diff cde73e8b72fc563d515fd5ab66a6a12eec85698e 0e200f4995c2b708c75b5c2ba4307ef3e124a9ca
diff --git a/tools/audit/seat/open_pr.sh b/tools/audit/seat/open_pr.sh
index 0b14ad5890..2070d94970 100755
--- a/tools/audit/seat/open_pr.sh
+++ b/tools/audit/seat/open_pr.sh
@@ -40,7 +40,7 @@ pr_code_sha_shape "$2"
 export PATH=${HPO_STATE_DIR:-$HOME/.local/state/hpo}/venv-ci/bin:$PATH
 M=$(cd "$(git -C "$(dirname -- "$0")" rev-parse --path-format=absolute --git-common-dir)/.." && pwd)
 T=$1; C=$2; TITLE=$3; G=$4; shift 4; ISS="$*"
-D=${HPO_STATE_DIR:-$HOME/.local/state/hpo}/pr/$T; WT=$D/wt; BR=${BR:-fix/$T}; R=tvofi/heatpump_optimizer
+pr_state_root; D=$PR_STATE/pr/$T; WT=$D/wt; BR=${BR:-fix/$T}; R=tvofi/heatpump_optimizer
 # A topic's opener worktree $WT is shared by every opener of the topic (a seat's hand run, open_driver.py's), so the
 # branch it holds names the lock of the run holding it. A second opener adopts that branch and meets the first's lock
 # (BUSY) before it writes the shared body.md, not a -pr lock of its own. A detached worktree holds no branch: a
diff --git a/tools/audit/seat/pr_args.sh b/tools/audit/seat/pr_args.sh
index 33a1683bbd..63c2e08c89 100644
--- a/tools/audit/seat/pr_args.sh
+++ b/tools/audit/seat/pr_args.sh
@@ -59,6 +59,16 @@ pr_code_in_handoff() { # <sha> <topic>: after the fetch of handoff/<topic>; PR_H
   [ "$1" != "$PR_BT" ] || pr_refuse "code sha $1 is not an ancestor of origin/handoff/$2 ($PR_HT); it is the tip of handoff-body/$2: that is the BODY sha; pass the CODE sha"  # mut:body
   pr_refuse "code sha $1 is not an ancestor of origin/handoff/$2 ($PR_HT), and it is not the tip of handoff-body/$2 (${PR_BT:-absent})"  # mut:ancestor
 }
+pr_state_root() { # sets PR_STATE: the state dir ($HPO_STATE_DIR, default ~/.local/state/hpo), its pr/ created, as its physical path
+  # git records and lists a worktree by its physical path (`git worktree list --porcelain`), so every path
+  # open_pr.sh and update_pr.sh derive from the state dir and match against that list (mut:opreg, the
+  # left-over guard, mut:elsewhere, update_pr.sh's own-worktree scan) is built on this one spelling: a
+  # symlinked component, a trailing slash or a `/./` segment in $HPO_STATE_DIR otherwise matches nothing,
+  # silently (#3549's review). `cd -P && pwd -P`, not realpath: macOS's /bin/bash 3.2 and BSD tools run this.
+  PR_STATE=${HPO_STATE_DIR:-$HOME/.local/state/hpo}
+  mkdir -p "$PR_STATE/pr" || pr_refuse "cannot create the state dir $PR_STATE/pr"
+  PR_STATE=$(CDPATH= cd -P -- "$PR_STATE" && pwd -P) || pr_refuse "cannot resolve the state dir $PR_STATE"  # mut:stateroot
+}
 pr_busy() { printf '%s: BUSY: %s; nothing was changed, run again when it ends\n' "${PR_NAME:-pr}" "$*" >&2; exit 75; }  # a stop that is a live run's, not a permanent refusal (carry 8)
 pr_lock_busy() { # <lock-file> <branch> <worktree>: the holder did not take the lock: BUSY (75) when another holder has it
   local rc=0 o
@@ -1315,13 +1325,21 @@ STUB
   dualend() { # <state dir>
     reap; git -C "$m" worktree remove --force "$1/pr/r/wt" 2>/dev/null; git -C "$m" worktree prune; git -C "$o" reset -q --hard "$base"; true
   }
-  dualrun() { # <mutant|->: rc of the second opener in $t/rc2, body.md before and after it in $t/bd1 and $t/bd2
-    local sd=$t/dual-state sdir=$t/dual-stub k=0 op
-    dualreset "$sd" "$sdir"; sd=$(cd "$sd" && pwd -P); dualcopy "$1"
-    env -u BR -u BR_FIXED HPO_STATE_DIR=$sd STUB_DIR=$sdir bash "$m/tools/audit/seat/open_pr.sh" r "$codeR" T G > "$t/dout1" 2>&1 & op=$!
+  spell() { # <physical dir> <-|link|slash|dot>: another spelling of that dir (#3549's review: git lists the physical one)
+    case $2 in
+      link) ln -sfn "$1" "$1.link"; printf '%s\n' "$1.link" ;;
+      slash) printf '%s/\n' "$1" ;;
+      dot) printf '%s/./%s\n' "${1%/*}" "${1##*/}" ;;
+      *) printf '%s\n' "$1" ;;
+    esac
+  }
+  dualrun() { # <mutant|-> [<spelling>]: rc of the second opener in $t/rc2, body.md before and after it in $t/bd1 and $t/bd2
+    local sd=$t/dual-state sdir=$t/dual-stub k=0 op sp
+    dualreset "$sd" "$sdir"; rm -f "$sd.link"; sd=$(cd "$sd" && pwd -P); dualcopy "$1"; sp=$(spell "$sd" "${2:--}")
+    env -u BR -u BR_FIXED HPO_STATE_DIR=$sp STUB_DIR=$sdir bash "$m/tools/audit/seat/open_pr.sh" r "$codeR" T G > "$t/dout1" 2>&1 & op=$!
     while [ ! -e "$sdir/p2started" ] && [ $k -lt 400 ]; do sleep 0.05; k=$((k + 1)); done
     cksum < "$sd/pr/r/body.md" > "$t/bd1"
-    env -u BR -u BR_FIXED HPO_STATE_DIR=$sd STUB_DIR=$sdir bash "$m/tools/audit/seat/open_pr.sh" r "$codeR" T G > "$t/dout2" 2>&1; echo $? > "$t/rc2"
+    env -u BR -u BR_FIXED HPO_STATE_DIR=$sp STUB_DIR=$sdir bash "$m/tools/audit/seat/open_pr.sh" r "$codeR" T G > "$t/dout2" 2>&1; echo $? > "$t/rc2"
     cksum < "$sd/pr/r/body.md" > "$t/bd2"
     touch "$sdir/release"; wait "$op"; echo $? > "$t/rc1"
     dualend "$sd"
@@ -1340,6 +1358,16 @@ STUB
   ck "  mutant mut:opreg (its line deleted): the second opener takes the -pr lock, is not BUSY, and rewrites body.md (the defect)" $?
   lonerun; [ "$(cat "$t/rc3")" = 0 ] && [ "$(cat "$t/lrow")" = 1 ]
   ck "  null control: a lone opener beside a stale local fix/r and no registered worktree still takes fix/r-pr" $?
+  # #3549's review: git lists the opener worktree by its physical path, so a state dir spelled otherwise
+  # (a symlinked component, a trailing slash, a `/./` segment) left OP_REG empty and the defect live.
+  # pr_state_root (pr_args.sh) resolves it once; each spelling is the live case above, and the symlink
+  # spelling with that resolution deleted is the defect again.
+  for sp in link slash dot; do
+    dualrun - $sp; [ "$(cat "$t/rc2")" = 75 ] && grep -qF "BUSY" "$t/dout2" && [ "$(cat "$t/bd1")" = "$(cat "$t/bd2")" ] && [ "$(cat "$t/rc1")" = 0 ] && grep -q '^PR=5 ' "$t/dout1"
+    ck "open_pr: the state dir spelled $sp: a second opener is BUSY (75), body.md byte-identical, the first opens" $?
+  done
+  dualrun stateroot link; [ "$(cat "$t/rc2")" != 75 ] && [ "$(cat "$t/bd1")" != "$(cat "$t/bd2")" ]
+  ck "  mutant mut:stateroot (its line deleted): through a symlinked state dir the second opener is not BUSY and rewrites body.md (the defect)" $?
   # R10-HOTFIX-OPENPR-FIGURE-REFRESH: a figure block names the head it was rendered at, so the body
   # open_pr.sh pushes needs it re-rendered at each head it pushes (p1 when the main merge moved the
   # head, p2 always: the row commit moves it). The stub pusher is lint's figure-block head check; the
@@ -1814,9 +1842,9 @@ STUB
   ck "  mutants mut:oplock and mut:unpushed (both deleted): the row's push is refused, HEAD detached under it, and the PR keeps no row (the defect)" $?
   # Only committed work is detached from a worktree: one holding commits origin lacks is refused
   # (the old reset would have dropped them); one whose HEAD origin has is detached as before.
-  unpushed() { # <mutant> <commit: 1|0>
-    local sd=$t/unp-$1-$2 g
-    rm -rf "$sd" "$t/s$i"; git -C "$m" worktree prune; git -C "$m" branch -qD fix/u 2>/dev/null; mkdir -p "$sd/pr/u"; sd=$(cd "$sd" && pwd -P)
+  unpushed() { # <mutant> <commit: 1|0> [<spelling> of the state dir update_pr.sh is given]
+    local sd=$t/unp-$1-$2-${3:--} g
+    rm -rf "$sd" "$sd.link" "$t/s$i"; git -C "$m" worktree prune; git -C "$m" branch -qD fix/u 2>/dev/null; mkdir -p "$sd/pr/u"; sd=$(cd "$sd" && pwd -P)
     for g in open_pr.sh update_pr.sh delivery_row.sh pr_args.sh pr_cap.py; do
       if [ "$1" = - ]; then cp "$src/$g" "$m/tools/audit/seat/$g"
       else grep -v "# mut:$1\$" "$src/$g" > "$m/tools/audit/seat/$g"; fi
@@ -1824,7 +1852,7 @@ STUB
     git -C "$m" fetch -q origin fix/u && git -C "$m" worktree add -q -b fix/u "$sd/pr/u/wt" origin/fix/u || return 1
     [ "$2" = 0 ] || { printf 'row\n' > "$sd/pr/u/wt/row" && git -C "$sd/pr/u/wt" add row && git -C "$sd/pr/u/wt" commit -q -m row; }
     cp "$t/body.md" "$t/bU.md"
-    HPO_STATE_DIR=$sd bash "$m/tools/audit/seat/update_pr.sh" fix/u - "$t/bU.md" > "$t/outu" 2>&1; echo $? > "$t/rcu"
+    HPO_STATE_DIR=$(spell "$sd" "${3:--}") bash "$m/tools/audit/seat/update_pr.sh" fix/u - "$t/bU.md" > "$t/outu" 2>&1; echo $? > "$t/rcu"
     git -C "$sd/pr/u/wt" symbolic-ref -q HEAD > "$t/attached" 2>&1 || echo detached > "$t/attached"
     reap; git -C "$m" worktree remove --force "$sd/pr/u/wt" 2>/dev/null; git -C "$m" worktree remove --force "$sd/pr/upd-fix-u" 2>/dev/null; git -C "$m" worktree prune; git -C "$m" branch -qD fix/u 2>/dev/null; true
   }
@@ -1839,6 +1867,13 @@ STUB
   unpushed - 0
   [ "$(cat "$t/attached")" = detached ] && grep -qF "update_pr: REFUSE: the push failed" "$t/outu" && ! grep -qF "(unpushed work" "$t/outu"
   ck "null control: a worktree whose HEAD origin has is detached as before, and the run reaches its push" $?
+  # #3549's review, update_pr.sh's side: its own-worktree scan (`grep "^$P/"`) and mut:elsewhere match git's
+  # physical list, so a symlinked state dir left that clean worktree on the branch and the run BUSY.
+  unpushed - 0 link
+  [ "$(cat "$t/attached")" = detached ] && grep -qF "update_pr: REFUSE: the push failed" "$t/outu" && ! grep -qF "checked out elsewhere" "$t/outu"
+  ck "update_pr: through a symlinked state dir, that worktree is detached as before and the run reaches its push" $?
+  unpushed stateroot 0 link; [ "$(cat "$t/attached")" = refs/heads/fix/u ] && grep -qF "checked out elsewhere" "$t/outu"
+  ck "  mutant mut:stateroot (its line deleted): through a symlinked state dir the worktree stays on the branch and the run is BUSY (the defect)" $?
   # The row-only arm (R10-ROW-ONLY-UPDATE): a head that is the live head plus one commit (here code
   # sha `-` adding the row) asks app_push.sh for --row-only, whose own verdict decides whether a
   # full prepr is owed; a head merging new code asks for --reuse instead (P386), never --row-only.
diff --git a/tools/audit/seat/update_pr.sh b/tools/audit/seat/update_pr.sh
index 60a11a9b94..611d4360f3 100755
--- a/tools/audit/seat/update_pr.sh
+++ b/tools/audit/seat/update_pr.sh
@@ -41,7 +41,7 @@ SEAT=$(cd "$(dirname -- "$0")" && pwd); PRT=$(cd "$(dirname -- "$0")/../../pr" &
 pr_need_args 3 $# "update_pr.sh <branch> <code-sha|-> <body-file> [issues...]"
 [ "$2" = - ] || pr_code_sha_shape "$2"
 [ -f "$3" ] || pr_refuse "no body file at $3"
-M=$(cd "$(git -C "$(dirname -- "$0")" rev-parse --path-format=absolute --git-common-dir)/.." && pwd); P=${HPO_STATE_DIR:-$HOME/.local/state/hpo}/pr; mkdir -p "$P"
+M=$(cd "$(git -C "$(dirname -- "$0")" rev-parse --path-format=absolute --git-common-dir)/.." && pwd); pr_state_root; P=$PR_STATE/pr  # physical: matched against git worktree list below
 BR=$1; C=$2; B=$3; shift 3; ISS="$*"; R=tvofi/heatpump_optimizer
 WT=$P/upd-${BR//\//-}
 # The EXIT trap goes first, so the lock (pr_branch_lock) is freed by it after the reap: bash runs it

## Before you return the verdict (P275)
Run `python3 -I tools/audit/carry_audit.py check --body <PR body file> --comments <file holding [{"id": 0, "body": <verdict.md text>}]>`. Give every reported item its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>`;
an evidence line flagged by its wording takes `Carry: dismissed: evidence, not a finding`. Return the verdict only at rc 0.
