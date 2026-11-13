CLOUD REVIEWER seat for PR #3544 of tvofi/heatpump_optimizer, at head a60a65d87376397adc098cbf2b7b2377ccaeca02. Bus nonce: 41c4643bafddfb0eb74e5513f05f272b. Never send push notifications. Write no Claude Code footer, no Co-Authored-By or Claude-Session trailer and no claude.ai session link in any commit, pull-request body or comment you produce; check your commits with `git log --format=%B` before pushing.
Setup: `git fetch --unshallow --tags origin`. The session-start `toolchain:` line says whether venv-ci's python3 is on PATH: on REFUSE, start each Bash call with `eval "$(bash .claude/hooks/session-start.sh --env-lines)"`. Then run `bash tools/audit/seat/cloud-setup.sh --check`, and on REFUSE stop: report its line as your result and start no work. Run anything heavy in the background with Monitor and no timeout. Never wait in one tool call longer than 240 s; poll again instead. Read your policy once, verbatim: `python3 -I tools/policy/role_pack.py render fix-review --out $HOME/role-pack.md`, then that file in place of your role contract and INSTRUMENTS.md; on REFUSE read those files as before.
Role: read dev/governance/roles/fix-review.md and its rules from main, and follow them exactly. Fetch the PR head with `git fetch origin a60a65d87376397adc098cbf2b7b2377ccaeca02`; the PR body is in the PR. Start from the review packet, which you render here rather than read from the dispatcher, whose copy is a path on its own machine: `python3 -I tools/audit/seat/review_packet.py render --pr 3544 --head a60a65d87376397adc098cbf2b7b2377ccaeca02 --reviewed-head 8382e2aa25cab7c82b6e6ce8e5059412d5e970c3 --out $HOME/review-packet.md`. A refusal names its signal and the packet is still written unless the signal is `host-path`; re-read the live checks either way. This is a later round over the reviewed head 8382e2aa25cab7c82b6e6ce8e5059412d5e970c3: its scope is the packet's `## Review scope` line, the delta and the previous verdict's findings when it reads `delta`, widened only to the exact already-reviewed code a production (custom_components/) delta puts at non-obvious risk that CI would not detect, the verdict naming path and risk; an instrument, test, policy or body delta never widens it (fix-review.md step 12). Verify each claim adversarially: mutate the fix and check the tests fail, and check every figure in the body at this head. Check that it merges with origin/main (`git merge-tree --write-tree origin/main <head>`); block on main only when that reports a conflict, never on a head that is behind main but merges cleanly (the train re-proves it on the current main). Wait for CI on this head only by re-running `python3 tools/audit/seat/merge_train.py classify a60a65d87376397adc098cbf2b7b2377ccaeca02 --pr 3544` in the background, at least 60 s between runs, until it exits 0 (GREEN), 1 (RED), 2 (unreadable: say so in the verdict) or 4 (APPROVAL-OWED: the only red is the budget raise's approval, which follows your verdict; judge the head as GREEN and quote the line); 3 is WAIT, so run it again. Never wait with `pgrep` or `pkill`, whose `-f` pattern matches the waiter's own command line, nor on a context the ruleset does not require, such as `prelude`. A review_packet `required-red` signal does not stop you while classify prints WAIT: classify decides. If your review is otherwise complete and classify still prints WAIT after about 30 minutes of polling, stop waiting: put the line `pending-ci: <the context names it printed>` straight after the `bus-nonce:` line and return the verdict as below; the relay posts it once CI is green at this head, refuses it over a red, and refuses it if the head moves. If the review is not complete then, push `Fix review: blocked a60a65d87376397adc098cbf2b7b2377ccaeca02 ci-wait: <the last classify line>` as below.
Output: in a fresh directory of your own (`W=$(mktemp -d)`), write verdict.md, whose first line is exactly `Fix review: merge a60a65d87376397adc098cbf2b7b2377ccaeca02` or `Fix review: blocked a60a65d87376397adc098cbf2b7b2377ccaeca02 <class>: <reason>` (no brackets; the class is lower-case letters and dashes), in the format the role file gives, then a blank line, then `bus-nonce: 41c4643bafddfb0eb74e5513f05f272b`, then the body in sections. A blocked verdict's block goes under `## Block`. Each finding this PR does not settle (a defect, a surviving mutant, a deferral, a follow-up, a task owed after the merge) is its own bullet under `## Findings` ending in its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>` (finding-propagation.md). Everything else (RESULT lines, re-runs, CI state, figures you could not re-derive) goes under `## Evidence`: tools/audit/carry_audit.py reads an item there, and under any heading of a merge verdict but `## Findings`, `## Friction`, a block heading and a note heading (Residuals, Follow-ups, Notes ...), by its shape alone: a finding only when it opens with a lead word (Residual:, Follow-up:, Out of scope: ...) or carries a `Carry:`, so a defect you hand on goes under `## Findings`, and bus.sh refuses a verdict holding a finding with no valid `Carry:`. Put the evidence files in `ev/` beside it, under 25 MB in all (cite a large log by path and keep its tail: a ~30 MB ev/ once failed its push), and make at least one file under `ev/` contain the full 40-hex head `a60a65d87376397adc098cbf2b7b2377ccaeca02` (e.g. `ev/HEAD.txt` holding the head you reviewed, beside your command output): bus.sh refuses a verdict whose `ev/` names no head. Do NOT run bus.sh: its dispatch record lives on the orchestrator's machine, which publishes the verdict there (cloud_relay.sh). Return the verdict on a probe ref, and push nothing else; this builds one parentless commit with a private index and touches no branch of your checkout: `R=$(git rev-parse --show-toplevel); G=$(git rev-parse --absolute-git-dir); mkdir -p $W/pr && cp -r $W/verdict.md $W/ev $W/pr/ && cd $W/pr && T=$(GIT_DIR=$G GIT_INDEX_FILE=$W/idx GIT_WORK_TREE=$W/pr sh -c 'git add -A -f . && git write-tree') && C=$(GIT_DIR=$G git -c user.name=hpo-fixer -c user.email=70032254+tvofi@users.noreply.github.com commit-tree $T -m "verdict 3544 a60a65d87376397adc098cbf2b7b2377ccaeca02") && git -C $R push -q origin $C:refs/heads/probe/rev-3544-41c4643b`. That ref is the return signal. Do not post comments, approve or merge.
Every way your turn ends pushes a verdict to that ref: a setup or hook refusal that stops you pushes `Fix review: blocked a60a65d87376397adc098cbf2b7b2377ccaeca02 seat-refused: <the refusing line>`; never end your turn while a background poll runs. After the push, read the ref back with `git ls-remote origin refs/heads/probe/rev-3544-41c4643b`, and push again if it does not print your commit.
A red is owed a `## Red checks` answer, and may block, only when its name is in the set `python3 tools/audit/seat/merge_train.py owed-reds` prints (defect-root-cause.md); any other red is neither answered nor a block.
Never write to any branch except your return refs. Never work around a hook or a refusal; report it in your result instead.
Discovery reads (search, list, read across files) go through Agent subagents, as the frugal routing guard requires: when it refuses inline work, dispatch a haiku or sonnet Agent subagent to do it rather than bypassing the guard; never set FRUGAL_ALLOW_INLINE and never edit .claude/settings.json.

Brief (snapshotted when this payload was rendered):
# Review packet #3544
head: a60a65d87376397adc098cbf2b7b2377ccaeca02
base: e23124ff6e45bac1d48b4a775dad555a37965355

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: pending
.github/dependabot.yml id=132185490093 success
arm id=132185509157 skipped
cancel-superseded id=132185520999 in_progress
prelude id=132185521059 in_progress
refresh id=132185520411 in_progress

## Refusals
none

## Advisories
hot-file: HPO_BUS_TRAIN_STATE is unset, so every merge verdict reads unboarded

## carry_audit at the head
CARRY-AUDIT: 0 finding item(s): 0 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
ok         node tools/policy/policy_lint.mjs
             `tools/policy/policy_lint.mjs` is in the tree at this head
  unverified git merge-tree --write-tree origin/main 8382e2aa25
             `git merge-tree` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  unverified git merge origin/main
             `git merge` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  ok         node tools/policy/brief_lint.mjs
             `tools/policy/brief_lint.mjs` is in the tree at this head
  ok         bash tools/pr/prepr.sh
             `tools/pr/prepr.sh` is in the tree at this head

FIGURES: 3 resolved, 2 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
none

## Review scope: full (first round: no --reviewed-head)

## Three-dot diff
diff --git a/dev/governance/roles/fixer.md b/dev/governance/roles/fixer.md
index 64f01557a8..89cb6796ab 100644
--- a/dev/governance/roles/fixer.md
+++ b/dev/governance/roles/fixer.md
@@ -23,7 +23,7 @@ fix, handoff) through refs, never mid-task, by ~150 k tokens (S, M), ~300 k (L,
    corpus (case, quoting, glued options, delimiters, wrapping) with the corpus
    size named in the body; a spelling the reviewer finds is added to it.
    A `git archive` copy fails the #363 `recorded_at` check, and a self-test
-   needing a checkout, on every mutant, baseline included (#1713, #1723).
+   needing a checkout, on every mutant, baseline included.
    **The diff's survivors are yours before the handoff; `--pin-killed` is
    `ci-autofix.md`'s.** Set `prepr.sh`'s `MUTANT_CMD` to the group's self-test
    or a `features_block.py` call (`MUTANT_IN_PLACE=1` for a checkout); it draws only
@@ -41,8 +41,8 @@ fix, handoff) through refs, never mid-task, by ~150 k tokens (S, M), ~300 k (L,
    reports unverified, not refused. A harness measuring what the fix rightly
    leaves alone reads flat at both ends: say so, and add a sha1-cited companion
    applying the tree's own rule to the same inputs, reading the defect at the
-   baseline and not at the head (#1506, #1561, #1571). A fold deleting a name
-   the harness drives leaves only its count arm readable at the head;
+   baseline and not at the head. A fold deleting a name the harness drives
+   leaves only its count arm readable at the head;
    the fixer ports the rest, as its own (`fix-review.md` step 9; #2365).
    **Every quantified claim carries a null control, not only cost, gain and
    time**: a count, a percentage, an "every" or a "none" is a measurement, owed
@@ -84,8 +84,8 @@ fix, handoff) through refs, never mid-task, by ~150 k tokens (S, M), ~300 k (L,
    p1 the grader hunks alone, p2 the rest, a WIP handoff until p1 is on main
    (decision 0013, Consequences).
 
-   **`run.sh` takes the gate lease itself, around `tests/stress.py` alone**;
-   the queue, the wait bound and holding it by hand are `gate-scoping.md`'s.
+   **`run.sh` takes the gate lease itself, around `tests/stress.py` alone**
+   (`gate-scoping.md`).
    A mutation proof leaves `stress.py` to CI's required mutation check: never
    run it locally per mutant.
 
@@ -116,8 +116,7 @@ fix, handoff) through refs, never mid-task, by ~150 k tokens (S, M), ~300 k (L,
    (a `--carry` head: no re-take; name bot reds), and carries every executed
    number in `## Figures` with its command.
 8. **A quoted number states the rule that produced it, not just its value.**
-   Only a count whose rule is written down is re-derivable (#373: one census,
-   three counts). **Name the instrument you re-ran, and its scope.** If the
+   Only a count whose rule is written down is re-derivable. **Name the instrument you re-ran, and its scope.** If the
    block you are clearing was demonstrated with an *instance*, your verification
    may not be a search for that instance — it must check the property the
    phenomenon states, not the property the block's text states: name a rule that enumerates the class's seams (a command,
@@ -139,12 +138,11 @@ fix, handoff) through refs, never mid-task, by ~150 k tokens (S, M), ~300 k (L,
 9. **A claim should be true; if wrong, correct it — anchored to a lane,
    function, marker or SHA, never a bare line number — and delete only when
    no such correction exists.** Delete on sight, not as a last resort, when
-   the claim is only motivation or scaffolding the finished text doesn't
-   need (#386).
+   the claim is only motivation or scaffolding the finished text doesn't need.
 10. **If the wrong text is generated, fix the generator first, and run it.**
     Correcting prose a script emits leaves the script emitting the old text on
-    its next run, so the correction is undone rather than kept (#539). Grep for
-    the wrong form across the whole tree before deciding what to edit.
+    its next run, so the correction is undone rather than kept. Grep for the
+    wrong form across the whole tree before deciding what to edit.
     **A generator fixed without being run is a claim, not a fix**: run it,
     paste what it now emits, and run it at the merge base as the control.
     Text that *instructs* differs from a record that *recounts*: a measurement
@@ -196,8 +194,7 @@ fix, handoff) through refs, never mid-task, by ~150 k tokens (S, M), ~300 k (L,
     `np.sum(matrix, axis=1)` is not `np.sum(matrix[b])`, and neither is a
     reduction over a row VIEW of a batched array one over the fresh array the
     scalar expression builds: numpy's pairwise loop takes alignment and stride
-    as inputs, per backend (#948: arm64 parity, x86_64 drift, at the 96-step
-    production width only). Where the contract is bitwise, run the SCALAR
+    as inputs, per backend. Where the contract is bitwise, run the SCALAR
     EXPRESSION per row, on the fresh per-row arrays that expression's own
     elementwise ops allocate — batch only what is elementwise end to end — and
     drive the parity grid at the production width.
@@ -205,11 +202,9 @@ fix, handoff) through refs, never mid-task, by ~150 k tokens (S, M), ~300 k (L,
     The same rule holds one level up and across interpreter versions: a
     reduction whose scalar form is a PYTHON BUILTIN is compensated arithmetic
     on CPython 3.12+ — builtin `sum` is Neumaier — and no vectorized
-    accumulation reproduces it (#948: 1-2 ulp, red on CI's 3.14 runner, green
-    on 3.11, whose `sum` is plain). Make the twin call the scalar closure's own
+    accumulation reproduces it. Make the twin call the scalar closure's own
     function per row, and put detector rows on the parity grid that separate
-    the two summations (measured: ~12% of random three-term sums), so the
-    interpreter class that diverges — CI's — runs the detector.
+    the two summations, so the interpreter class that diverges — CI's — runs the detector.
 
     A per-row twin removes re-entry, not work; when it is the fix for a
     recomputation finding, re-measure the finding's cost on the fixed tree and
@@ -250,9 +245,7 @@ fix, handoff) through refs, never mid-task, by ~150 k tokens (S, M), ~300 k (L,
     improvement claim names its mechanism, which the reviewer removes as the
     null control (`fix-review.md` step 14). Never move a metric by a change
     that does not improve the code: a mechanical split, code moved to an
-    unmeasured path, a triage on a killable mutant, or cases enumerated where a
-    structural fix exists (#1874, #2345: a spelling list, three review rounds,
-    class still open).
+    unmeasured path, a triage on a killable mutant, or cases enumerated where a structural fix exists.
 18. **What a later round or seat reruns, or a body figure needs reproduced,
     lands in the same pull request** (tvofi, 2026-10-03): a harness in
     `dev/audit/harnesses/`, a driver or env recipe in `tools/audit/seat/`,
@@ -313,3 +306,10 @@ requires, the arms that fire, and only figures re-taken in that pass. Round
 history is deleted, not restated — except a **disclosed self-correction** (`dev/programme/HANDOVER.md`'s #1058
 tie-break). **A re-cut body blocked on `claims` again is a signal about the fix**:
 the orchestrator splits or closes it.
+
+**Never for a mechanical-only gap** (tvofi, 2026-11-09): `bus.sh dispatch` reads the
+latest block's class and dispatches with no `## Re-cut` when it is `red-unanswered`,
+`body`, `contract`, `conflict`, `head-moved`, `carry`, `carry-missing`, `ungated` or
+CI-only (`ci-red`, `ci-wait`, `ci-pending`, `ci-cancelled`): mechanical, it does not
+count toward the three-round rule. A judgement class, an unknown one or an unreadable
+log refuses.
diff --git a/dev/programme/delivery/3544.md b/dev/programme/delivery/3544.md
new file mode 100644
index 0000000000..e8df5be62b
--- /dev/null
+++ b/dev/programme/delivery/3544.md
@@ -0,0 +1 @@
+- [#3544](https://github.com/tvofi/heatpump_optimizer/pull/3544) — **open**, R10-REVIEW-DISPATCH-RESIDUE (part 5): r10 review dispatch residue p5 (R10-REVIEW-DISPATCH-RESIDUE)
diff --git a/tools/audit/seat/bus.sh b/tools/audit/seat/bus.sh
index e3d72d8039..25c07e7ce3 100755
--- a/tools/audit/seat/bus.sh
+++ b/tools/audit/seat/bus.sh
@@ -521,10 +521,25 @@ verdict_at() { # pr sha -> the latest verdict word naming <sha> on verdict/<pr>
 # a dispatch needs the body's `## Re-cut` note (read only then, through $HPO_BUS_GH) or
 # `--past-three <reason>`, logged in $S/past-three; after a fourth -- a re-cut blocked again --
 # only `--past-three`: the split-or-close is the orchestrator's, never a silent re-dispatch.
+# The classes whose block names a gap a script or a rebase closes, exactly the set carry 11 and its CI-only ruling name
+# and fixer.md's "Never for a mechanical-only gap" paragraph lists (the self-test reads both): a red, waiting, pending or
+# cancelled CI, an unanswered red, the body or contract, a conflict or moved head, a carry, an ungated step.
+# root-cause-unanswered (it dispatches the root-cause seat), preflight-mismatch and every judgement class are absent.
+MECHANICAL_CLASSES=" ci-red ci-wait ci-pending ci-cancelled red-unanswered body contract conflict head-moved carry-missing carry ungated "
+mechanical_block() { # pr -> rc 0 when the latest blocked verdict on verdict/<pr> names a mechanical class; rc 1 otherwise or unreadable
+  local subj cls
+  subj=$(verdict_log "$1") || return 1
+  cls=$(printf '%s\n' "$subj" | sed -n "s/^verdict: #$1 Fix review: blocked [0-9a-f]\{7,40\} \([^ :]*\):.*\$/\1/p" | head -n 1)
+  [ -n "$cls" ] && case $MECHANICAL_CLASSES in *" $cls "*) return 0;; esac
+  return 1
+}
 three_rounds() { # pr past-three-reason -> 0 to dispatch; else why
   local k body
   k=$(blocked_rounds "$1") || { printf 'cannot read verdict/%s to count its review rounds' "$1"; return 1; }
   [ "$k" -ge 3 ] && [ -z "$2" ] || return 0
+  # A latest block of a mechanical class (tvofi, 2026-11-09: "the split should never apply when the gap is
+  # mechanical only") is no round to re-cut over; a judgement class, an unknown one or an unreadable log refuses as before.
+  mechanical_block "$1" && return 0  # mut:mechclass
   [ "$k" -lt 4 ] || { printf '#%s has %s blocked rounds: its re-cut was blocked again, so split or close it (the orchestrator), or pass --past-three <reason>' "$1" "$k"; return 1; }
   body=$(${HPO_BUS_GH:-gh} api "repos/$REPO/pulls/$1" --jq .body) \
     || { printf 'cannot read #%s'"'"'s body to find its ## Re-cut note' "$1"; return 1; }
@@ -733,11 +748,12 @@ dispatch() { # pr head reviewer [--reviewed-head <sha>] [--nonce N] [--model M]
 # for handoff-head..PR-head (the merge of main and the row commit), else it reports
 # HELD-STALE and the PR is re-dispatched at its head. Nothing here reads CI, a row or a packet:
 # none exists before the PR does.
-dispatch_handoff() { # topic sha reviewer [--model M] -> records `topic:<topic> <sha> ...`, prints the nonce
-  local t=${1:-} h=${2:-} r=${3:-} m=- n tip
+dispatch_handoff() { # topic sha reviewer [--model M] [--pr N] -> records `topic:<topic> <sha> ...`, prints the nonce
+  local t=${1:-} h=${2:-} r=${3:-} m=- n tip pr=
   shift 3 2>/dev/null || shift $#
   while [ $# -gt 0 ]; do
     case $1 in
+      --pr) numeric "${2:-}" || die "dispatch-handoff: --pr takes a pull-request number"; pr=$2; shift 2 ;;
       --model) [[ ${2:-} =~ ^[A-Za-z0-9._-]+$ ]] || die "dispatch-handoff: --model takes one token"; m=$2; shift 2 ;;
       *) die "dispatch-handoff: unknown argument '$1'" ;;
     esac
@@ -756,6 +772,11 @@ dispatch_handoff() { # topic sha reviewer [--model M] -> records `topic:<topic>
   [[ $n =~ ^[0-9a-f]{32}$ ]] || die "dispatch-handoff: could not mint a nonce"
   mkdir -p "$S" && printf 'topic:%s %s %s %s %s %s\n' "$t" "$h" "$r" "$n" "$(date -u +%FT%TZ)" "$m" >> "$S/dispatched" \
     || die "dispatch-handoff: cannot record in $S"
+  # The PR is known from --pr or a `<topic> <sha> <pr>` line in rekeyed (a local read, no API call): key the
+  # new record at once, else a reviewer dispatched after the PR opened stays HELD-NOPR (open_pr.sh ran rekey before it existed).
+  [ -n "$pr" ] || pr=$(awk -v t="$t" '$1 == t && $3 ~ /^[0-9]+$/ { p = $3 } END { print p }' "$S/rekeyed" 2>/dev/null)  # mut:rekeyknown
+  # rekey dies on each failure it can meet; its rc 3 (no topic: record) cannot follow the append above.
+  [ -z "$pr" ] || rekey "$t" "$pr" >&2
   printf 'bus-nonce: %s\n' "$n"
 }
 
@@ -1046,7 +1067,7 @@ self_test() {
   # 7, 9, 12, 21, 22 and 24 (21-24 are the FETCHHEAD/poster arms' pull
   # requests); h2 (a child) inherits them; norow is the base, with none.
   mkdir -p "$W/seat/$ROW_DIR"
-  for n in 7 9 12 21 22 24 30 31 32 33 34 35; do
+  for n in 7 9 12 21 22 24 30 31 32 33 34 35 36 37 38 39 40 $(seq 41 54); do
     printf -- '- [#%s](https://github.com/o/r/pull/%s) — **open**\n' "$n" "$n" > "$W/seat/$ROW_DIR/$n.md"
   done
   git -C "$W/seat" -c user.name=t -c user.email=t@t add -A
@@ -1328,6 +1349,33 @@ bus-nonce: $N1b" ] && [ "$(grep -c " $N1b " "$W/state/dispatched")" = 2 ] \
   out=$(seat push-verdict 55 "$W/hmerge.md" "$W/ev1"); rc=$?
   [ $rc = 0 ]; expect "after the re-key the handoff-dispatched verdict proposes on #55 at the handoff head" $?
   git -C "$W/seat" push -q origin :refs/heads/review/55
+  # Carry 28: dispatch-handoff re-keys the new record itself whenever the PR is known (a rekeyed line, or --pr N).
+  git -C "$W/seat" push -q origin "$h2:refs/heads/handoff/ht1"
+  out=$(seat dispatch-handoff ht1 "$h2" cmsg_H5); rc=$?
+  hn2=$(echo "$out" | sed -n 's/^bus-nonce: //p')
+  [ $rc = 0 ] && grep -q "^55 $h2 cmsg_H5 $hn2 " "$W/state/dispatched" && grep -qx "ht1 $h2 55" "$W/state/rekeyed"
+  expect "a second dispatch-handoff for a topic already re-keyed to #55 adds a 55 record and a rekeyed line (carry 28)" $?
+  git -C "$W/seat" push -q origin "$h1:refs/heads/handoff/ht3" "$h1:refs/heads/handoff-body/ht3"
+  out=$(seat dispatch-handoff ht3 "$h1" cmsg_H6 --pr 57); rc=$?
+  hn3=$(echo "$out" | sed -n 's/^bus-nonce: //p')
+  [ $rc = 0 ] && grep -q "^57 $h1 cmsg_H6 $hn3 " "$W/state/dispatched" && grep -qx "ht3 $h1 57" "$W/state/rekeyed"
+  expect "--pr 57 keys a fresh topic at dispatch (carry 28)" $?
+  git -C "$W/seat" push -q origin "$h1:refs/heads/handoff/ht4" "$h1:refs/heads/handoff-body/ht4"
+  out=$(seat dispatch-handoff ht4 "$h1" cmsg_H7); rc=$?
+  [ $rc = 0 ] && grep -q "^topic:ht4 $h1 " "$W/state/dispatched" && ! grep -q "^[0-9]* $h1 cmsg_H7 " "$W/state/dispatched" && ! grep -q "^ht4 " "$W/state/rekeyed"
+  expect "null control: a topic with no PR and no --pr stays topic:-only, so HELD-NOPR is unchanged (carry 28)" $?
+  out=$(seat dispatch-handoff ht4 "$h2" cmsg_H8 --pr x); rc=$?
+  [ $rc != 0 ] && echo "$out" | grep -q "dispatch-handoff: --pr takes a pull-request number" && ! grep -q " cmsg_H8 " "$W/state/dispatched"
+  expect "--pr takes a number, refused before anything is recorded (carry 28)" $?
+  # The rekeyed lookup takes the LAST numeric line for the topic: a later re-key wins, a non-numeric third field is skipped.
+  git -C "$W/seat" push -q origin "$h1:refs/heads/handoff/ht5" "$h1:refs/heads/handoff-body/ht5"
+  printf 'ht5 %s 58\nht5 %s 59\nht5 %s -\n' "$h1" "$h1" "$h1" >> "$W/state/rekeyed"
+  out=$(seat dispatch-handoff ht5 "$h1" cmsg_H9); rc=$?
+  hn5=$(echo "$out" | sed -n 's/^bus-nonce: //p')
+  [ $rc = 0 ] && grep -q "^59 $h1 cmsg_H9 $hn5 " "$W/state/dispatched" && ! grep -q "^58 $h1 cmsg_H9 " "$W/state/dispatched"
+  expect "a topic re-keyed to #58 then #59 (then a non-numeric line) keys the new record to #59 alone (carry 28)" $?
+  git -C "$W/seat" push -q origin :refs/heads/handoff/ht3 :refs/heads/handoff-body/ht3 :refs/heads/handoff/ht4 :refs/heads/handoff-body/ht4 \
+    :refs/heads/handoff/ht5 :refs/heads/handoff-body/ht5
   out=$(seat rekey never 56); rc=$?
   [ $rc = 3 ] && echo "$out" | grep -q "never has no handoff dispatch" && ! grep -q "^56 " "$W/state/dispatched"
   expect "null control: a topic with no handoff dispatch re-keys nothing (rc 3), so open_pr.sh stays quiet" $?
@@ -2024,6 +2072,36 @@ B
   printf "## Summary\nno note\n" > "$W/body31"
   out=$(run dispatch 35 "$h1" cmsg_T); rc=$?
   [ $rc != 0 ] && echo "$out" | grep -q "3 blocked round(s).*## Re-cut"; expect "null control: three distinct blocked heads are three rounds and refuse without a note" $?
+  # Carry 11 (owner directive, tvofi 2026-11-09): a latest block of a mechanical class never counts toward the rule.
+  blkc() { git -C "$W/seat" commit-tree "$(git -C "$W/seat" rev-parse "$h1^{tree}")" ${2:+-p "$2"} \
+             -m "verdict: #$3 Fix review: blocked $(printf '%040d' "$1") $4: round $1"; }
+  blk4() { local rp; rp=$(blkc 1 "" "$1" harness); rp=$(blkc 2 "$rp" "$1" harness); rp=$(blkc 3 "$rp" "$1" "$2")
+           rp=$(blkc 4 "$rp" "$1" "$2"); git -C "$W/seat" push -q origin "$rp:refs/heads/verdict/$1"; }
+  blk4 37 proof; blk4 38 nosuchclass
+  printf "## Summary\nno note\n" > "$W/body31"
+  # The exempt set is fixer.md's: the backticked class words of its "Never for a mechanical-only gap" paragraph
+  # must be MECHANICAL_CLASSES exactly, and each is driven below by its own fourth round beside two it must refuse.
+  pol=$(awk '/^\*\*Never for a mechanical-only gap\*\*/ { on = 1 } on && /^$/ { exit } on' "$ROOT/dev/governance/roles/fixer.md" \
+        | grep -o '`[a-z][a-z-]*`' | tr -d '`' | sort -u | tr '\n' ' ')
+  [ -n "$pol" ] && [ "$pol" = "$(printf '%s\n' $MECHANICAL_CLASSES | sort -u | tr '\n' ' ')" ]
+  expect "fixer.md's mechanical-only paragraph names exactly MECHANICAL_CLASSES (carry 11)" $?
+  n=41
+  for c in $pol root-cause-unanswered preflight-mismatch; do
+    blk4 $n "$c"; out=$(run dispatch $n "$h1" cmsg_T); rc=$?
+    case " $pol " in
+      *" $c "*) [ $rc = 0 ] && echo "$out" | grep -q '^bus-nonce: '; expect "a fourth round after a $c block dispatches with no note (carry 11)" $? ;;
+      *) [ $rc != 0 ] && echo "$out" | grep -q "blocked round"; expect "null control: a fourth round after a $c block refuses (carry 11)" $? ;;
+    esac
+    n=$((n + 1))
+  done
+  out=$(run dispatch 37 "$h1" cmsg_T); rc=$?
+  [ $rc != 0 ] && echo "$out" | grep -q "blocked round"; expect "null control: a fourth round after a proof-class block still refuses (carry 11)" $?
+  out=$(run dispatch 38 "$h1" cmsg_T); rc=$?
+  [ $rc != 0 ] && echo "$out" | grep -q "blocked round"; expect "null control: an unknown class refuses as before (carry 11)" $?
+  rp=$(blkc 1 "" 40 ci-red); rp=$(blkc 2 "$rp" 40 ci-red); rp=$(blkc 3 "$rp" 40 ci-red); rp=$(blkc 4 "$rp" 40 harness)
+  git -C "$W/seat" push -q origin "$rp:refs/heads/verdict/40"
+  out=$(run dispatch 40 "$h1" cmsg_T); rc=$?
+  [ $rc != 0 ]; expect "only the LATEST block's class is read: mechanical rounds then a harness block refuses (carry 11)" $?
 
   # THE REVIEW PACKET: dispatch names the packet rendered at its head and passes the
   # finder's harness through; a REFUSED head records nothing; a seat that cannot render
diff --git a/tools/audit/seat/cloud_relay.sh b/tools/audit/seat/cloud_relay.sh
index 5348a55568..381e763672 100644
--- a/tools/audit/seat/cloud_relay.sh
+++ b/tools/audit/seat/cloud_relay.sh
@@ -857,8 +857,8 @@ noreturn_arm() {
   rm -f "$state/cloud-nr.$$" "$state/cloud-nrr.$$"
 }
 
-fold_judge() { # <memo> <level> <topic> <wip sha> <body sha> <outcome> <epoch> [<OWED level line>]: one judged topic, its level line set
-  printf '%s %s %s %s %s%s\n' "$3" "$4" "${5:--}" "$6" "$7" "${8:+ $8}" >> "$1"; [ -z "${8:-}" ] || printf '%s\n' "$8" >> "$2"; }
+fold_judge() { # <memo> <level> <topic> <wip sha> <body sha> <outcome> <epoch> <BODY.md blob|-> <handoff tip|-> [<OWED level line>]: one judged topic, its level line set
+  printf '%s %s %s %s %s %s %s%s\n' "$3" "$4" "${5:--}" "$6" "$7" "$8" "$9" "${10:+ ${10}}" >> "$1"; [ -z "${10:-}" ] || printf '%s\n' "${10}" >> "$2"; }
 fold_memo_stands() { # <outcome> <epoch> <now>: rc 0 while a judged outcome stands; a failure after the fold expires after 3600 s
   case $1:$2 in blocked:*|folded:*) return 0;; fold-failed:[0-9]*|push-failed:[0-9]*) [ $(($3 - $2)) -lt 3600 ];; *) return 1;; esac; }  # mut:foldttl
 carry_fold_arm() { # one pass over handoff-wip/<topic> refs whose BLOCKED.md names CARRY-LANDED alone: fold the kept body's carries, re-run body_push.sh
@@ -867,13 +867,15 @@ carry_fold_arm() { # one pass over handoff-wip/<topic> refs whose BLOCKED.md nam
   # by hand (4 times on 2026-11-06, twice more on 11-07). The refusal is folded only when it is the ONLY kind the
   # BLOCKED.md names and the refused body is kept on handoff-wip/<topic>-body; any other BLOCKED.md prints a tick
   # line and folds nothing. carry_fold.py is the designated roster writer; HPO_RELAY_FOLD / HPO_RELAY_BODYPUSH replace the two steps.
-  # Every judged (wip sha, body sha) is memoed in cloud-fold-judged, `<topic> <wip> <body|-> <outcome> <epoch> [<OWED line>]`
-  # (P580); a (topic, body) cloud-folded holds is skipped unmemoed. A memoed pair is neither fetched nor shown, and its
+  # Every judged (wip sha, body sha) is memoed in cloud-fold-judged, `<topic> <wip> <body|-> <outcome> <epoch> <blob|-> <handoff tip|-> [<OWED line>]`
+  # (P580); a (topic, body) cloud-folded holds is skipped unmemoed. body_push.sh keeps every refused body as a NEW parentless
+  # commit, so a failure memoed under the kept commit never hits again (r10-train-residue: four kept commits in an hour,
+  # one BODY.md blob): a failed fold or push also stands for a later kept body with the same stop, BODY.md blob and handoff tip. A memoed pair is neither fetched nor shown, and its
   # stored line is set again, because level_set replaces the whole carry-fold level. A failure after the fold is judged
   # again once fold_memo_stands expires it: an ancestry red can clear with no ref moving. The body is pushed from a
   # worktree at a private ref fetched from handoff/<topic>, deleted after the push, never FETCH_HEAD, which a concurrent
   # fetch in this checkout overwrites, and only at that ref's ls-remote tip (P556).
-  local state=${HPO_STATE_DIR:-$HOME/.local/state/hpo} sha ref topic bw bsha kinds wt body why rc memo now mo me ml htip head
+  local state=${HPO_STATE_DIR:-$HOME/.local/state/hpo} sha ref topic bw bsha kinds wt body why rc memo now mo me ml htip head mb mh blob fo fe fb fh fl
   git ls-remote origin 'refs/heads/handoff-wip/*' 'refs/heads/handoff/*' > "$state/cloud-wip.$$" \
     || { echo "cloud_relay: could not list handoff-wip refs; the carry-fold level stays as it was" >&2; rm -f "$state/cloud-wip.$$"; return 0; }
   memo=$state/cloud-fold-judged; now=$(date +%s)
@@ -882,28 +884,40 @@ carry_fold_arm() { # one pass over handoff-wip/<topic> refs whose BLOCKED.md nam
     case $ref in refs/heads/handoff-wip/*) topic=${ref#refs/heads/handoff-wip/};; *) continue;; esac
     case $topic in ''|*/*|*-body|*-carries|*-body-*) continue;; esac
     bsha=$(awk -v r="refs/heads/handoff-wip/$topic-body" '$2 == r { print $1; exit }' "$state/cloud-wip.$$")
-    mo= me= ml=; [ -f "$memo" ] && read -r _ _ _ mo me ml < <(awk -v t="$topic" -v w="$sha" -v b="${bsha:--}" '$1 == t && $2 == w && $3 == b { print; exit }' "$memo")
+    htip=$(awk -v r="refs/heads/handoff/$topic" '$2 == r { print $1; exit }' "$state/cloud-wip.$$"); blob=-
+    mo= me= ml= mb= mh=; [ -f "$memo" ] && read -r _ _ _ mo me mb mh ml < <(awk -v t="$topic" -v w="$sha" -v b="${bsha:--}" '$1 == t && $2 == w && $3 == b { print; exit }' "$memo")
+    [ "${#mb}" = 40 ] || [ "$mb" = - ] || mo=  # a record from before the blob and tip fields is judged again
     if [ -n "$mo" ] && fold_memo_stands "$mo" "$me" "$now"; then
-      fold_judge "$memo.$$" "$state/cloud-level-fold.$$" "$topic" "$sha" "$bsha" "$mo" "$me" "$ml"; continue  # mut:foldmemo
+      fold_judge "$memo.$$" "$state/cloud-level-fold.$$" "$topic" "$sha" "$bsha" "$mo" "$me" "$mb" "$mh" "$ml"; continue  # mut:foldmemo
     fi
+    # A failed fold or push stands over a moved kept body when its BODY.md blob, the stop and handoff/<topic>'s tip all
+    # equal the record's; the record keeps its first epoch, so the retry bound runs from the first failure.
+    fo= fe= fb= fh= fl=; [ -n "$bsha" ] && [ -n "$htip" ] && [ -f "$memo" ] \
+      && read -r _ _ _ fo fe fb fh fl < <(awk -v t="$topic" -v w="$sha" -v h="$htip" '$1 == t && $2 == w && ($4 == "fold-failed" || $4 == "push-failed") && $7 == h { print; exit }' "$memo")
+    if [ -n "$fo" ] && fold_memo_stands "$fo" "$fe" "$now" \
+      && git fetch -q origin "refs/heads/handoff-wip/$topic-body" 2>/dev/null && blob=$(git rev-parse "$bsha:BODY.md" 2>/dev/null) && [ "$blob" = "$fb" ]; then  # mut:foldblob
+      echo "cloud_relay: OWED carry-fold $topic unchanged since $(date -u -d "@$fe" +%FT%TZ): ${fl#*"$sha "}"
+      fold_judge "$memo.$$" "$state/cloud-level-fold.$$" "$topic" "$sha" "$bsha" "$fo" "$fe" "$fb" "$fh" "$fl"; continue
+    fi
+    blob=-
     [ -f "$state/cloud-folded" ] && grep -qxF "$topic $bsha" "$state/cloud-folded" && continue
     git fetch -q origin "$ref" 2>/dev/null && bw=$(git show "$sha:BLOCKED.md" 2>/dev/null) || continue
     kinds=$(printf '%s\n' "$bw" | sed -n 's/^body_push: REFUSED \([A-Z-]*\)[[:space:]]*$/\1/p' | sort -u | tr '\n' ' ')
     if [ "$kinds" != "CARRY-LANDED " ] || [ -z "$bsha" ]; then  # mut:foldonly
       why="BLOCKED.md names ${kinds:-no refusal line}${bsha:+; }${bsha:-and no kept body}: not CARRY-LANDED alone, nothing folded"
       echo "cloud_relay: OWED carry-fold $topic ${sha:0:12} $why"
-      fold_judge "$memo.$$" "$state/cloud-level-fold.$$" "$topic" "$sha" "$bsha" blocked "$now" "$(level_line carry-fold "$ref" "$sha" "$why")"; continue
+      fold_judge "$memo.$$" "$state/cloud-level-fold.$$" "$topic" "$sha" "$bsha" blocked "$now" - "${htip:--}" "$(level_line carry-fold "$ref" "$sha" "$why")"; continue
     fi
     body=$state/cloud-fold-$topic.md
     git fetch -q origin "refs/heads/handoff-wip/$topic-body" 2>/dev/null && git show "$bsha:BODY.md" > "$body" 2>/dev/null \
       || { echo "cloud_relay: no BODY.md at handoff-wip/$topic-body; nothing folded" >&2; continue; }
+    blob=$(git rev-parse "$bsha:BODY.md" 2>/dev/null || echo -)
     rc=0; why=$(${HPO_RELAY_FOLD:-python3 -I "$HERE/carry_fold.py"} --body "$body" --topic "$topic" --worktree "$state/cloud-fold-wt" 2>&1) || rc=$?
     if [ $rc != 0 ]; then
       why=$(last_line "$why"); echo "cloud_relay: OWED carry-fold $topic ${sha:0:12} carry_fold rc=$rc: $why"
-      fold_judge "$memo.$$" "$state/cloud-level-fold.$$" "$topic" "$sha" "$bsha" fold-failed "$now" "$(level_line carry-fold "$ref" "$sha" "carry_fold rc=$rc: $why")"; continue
+      fold_judge "$memo.$$" "$state/cloud-level-fold.$$" "$topic" "$sha" "$bsha" fold-failed "$now" "$blob" "${htip:--}" "$(level_line carry-fold "$ref" "$sha" "carry_fold rc=$rc: $why")"; continue
     fi
     wt=$state/cloud-fold-code; rm -rf "$wt"; git worktree prune; rc=1
-    htip=$(awk -v r="refs/heads/handoff/$topic" '$2 == r { print $1; exit }' "$state/cloud-wip.$$")
     if [ -z "$htip" ] || ! git fetch -q origin "+refs/heads/handoff/$topic:refs/hpo-relay/fold/$topic" 2>/dev/null \
       || ! git worktree add -q --detach "$wt" "refs/hpo-relay/fold/$topic" 2>/dev/null; then  # mut:foldref
       why="no handoff/$topic to push the body from"; echo "cloud_relay: OWED carry-fold $topic ${sha:0:12} $why"
@@ -917,8 +931,8 @@ carry_fold_arm() { # one pass over handoff-wip/<topic> refs whose BLOCKED.md nam
     fi
     git worktree remove --force "$wt" 2>/dev/null; git update-ref -d "refs/hpo-relay/fold/$topic" 2>/dev/null
     if [ $rc = 0 ]; then echo "$topic $bsha" >> "$state/cloud-folded"; echo "cloud_relay: FOLDED $topic: carries landed, body_push.sh pushed handoff-body/$topic"
-      fold_judge "$memo.$$" /dev/null "$topic" "$sha" "$bsha" folded "$now"
-    else fold_judge "$memo.$$" "$state/cloud-level-fold.$$" "$topic" "$sha" "$bsha" push-failed "$now" "$(level_line carry-fold "$ref" "$sha" "$why")"
+      fold_judge "$memo.$$" /dev/null "$topic" "$sha" "$bsha" folded "$now" "$blob" "${htip:--}"
+    else fold_judge "$memo.$$" "$state/cloud-level-fold.$$" "$topic" "$sha" "$bsha" push-failed "$now" "$blob" "${htip:--}" "$(level_line carry-fold "$ref" "$sha" "$why")"
     fi
   done < "$state/cloud-wip.$$"
   mv -f "$memo.$$" "$memo"; level_set carry-fold "$state/cloud-level-fold.$$"; rm -f "$state/cloud-wip.$$"
@@ -2087,6 +2101,48 @@ open(sys.argv[1], "w").close(); time.sleep(60)' "$t/stuck.held" "$t/state/pr/upd
   chk "... with no cloud-folded entry" 1 grep -q "^cf-h " "$t/state/cloud-folded"
   chk "... no FOLDED announcement" 1 grep -q "FOLDED cf-h" <<< "$cfo"
   chk "... and no body_push.sh run" 1 grep -q "^cf-h " "$t/bps"
+  # Carry 17 (P566): body_push.sh keeps each refused body as a NEW parentless commit; a failed fold stands for a later kept
+  # body with the same stop, BODY.md blob and handoff tip, and runs again when any of the three moves.
+  printf '#!/bin/bash\necho "$@" >> %s/bpk\nexit 1\n' "$t" > "$t/bpfail"; chmod +x "$t/bpfail"; export HPO_RELAY_BODYPUSH=$t/bpfail
+  : > "$t/bpk"; cfref handoff/cf-k code.txt "code K"; cfref handoff-wip/cf-k BLOCKED.md "body_push: REFUSED CARRY-LANDED"
+  cfref handoff-wip/cf-k-body BODY.md "the body K"
+  cfo=$(carry_fold_arm 2>&1); kb1=$(cftip handoff-wip/cf-k-body)
+  chk "null control (carry 17): a stop with no record runs body_push.sh as today" 1 test "$(grep -c '^cf-k ' "$t/bpk")" != 1
+  GIT_AUTHOR_DATE="2001-01-01T00:00:00Z" GIT_COMMITTER_DATE="2001-01-01T00:00:00Z" cfref handoff-wip/cf-k-body BODY.md "the body K"
+  chk "the train-residue shape: the refused body is kept again as a new commit with the same BODY.md blob" 1 test "$(cftip handoff-wip/cf-k-body)" = "$kb1"
+  cfo=$(carry_fold_arm 2>&1)
+  chk "... and is not pushed again (same stop, blob and handoff tip)" 0 test "$(grep -c '^cf-k ' "$t/bpk")" = 1
+  chk "... the tick line says OWED, unchanged since the first failure" 0 grep -q "OWED carry-fold cf-k unchanged since 20[0-9-]*T[0-9:]*Z: body_push rc=1" <<< "$cfo"
+  chk "... and its OWED level line still stands" 0 grep -q "carry-fold refs/heads/handoff-wip/cf-k .*body_push rc=1" "$LOG.level"
+  cfref handoff-wip/cf-k-body BODY.md "the body K, edited"; carry_fold_arm >/dev/null 2>&1
+  chk "a changed BODY.md blob runs body_push.sh again" 0 test "$(grep -c '^cf-k ' "$t/bpk")" = 2
+  GIT_AUTHOR_DATE="2002-01-01T00:00:00Z" GIT_COMMITTER_DATE="2002-01-01T00:00:00Z" cfref handoff-wip/cf-k-body BODY.md "the body K, edited"; carry_fold_arm >/dev/null 2>&1
+  chk "null control: the edited body kept again as a new commit is skipped" 0 test "$(grep -c '^cf-k ' "$t/bpk")" = 2
+  GIT_AUTHOR_DATE="2003-01-01T00:00:00Z" GIT_COMMITTER_DATE="2003-01-01T00:00:00Z" cfref handoff-wip/cf-k-body BODY.md "the body K, edited"
+  cfref handoff/cf-k code.txt "code K, moved"; carry_fold_arm >/dev/null 2>&1
+  chk "a moved handoff/<topic> tip with the same blob runs body_push.sh again" 0 test "$(grep -c '^cf-k ' "$t/bpk")" = 3
+  GIT_AUTHOR_DATE="2004-01-01T00:00:00Z" GIT_COMMITTER_DATE="2004-01-01T00:00:00Z" cfref handoff-wip/cf-k-body BODY.md "the body K, edited"
+  awk -v e=$(( $(date +%s) - 3601 )) '$1 == "cf-k" { $5 = e } 1' "$t/state/cloud-fold-judged" > "$t/memo" && mv "$t/memo" "$t/state/cloud-fold-judged"
+  carry_fold_arm >/dev/null 2>&1
+  chk "a record an hour old no longer stands over a new kept commit" 0 test "$(grep -c '^cf-k ' "$t/bpk")" = 4
+  # A failed carry_fold.py (fold-failed) stands over a re-kept body alike, and the standing record keeps its first epoch.
+  printf '#!/bin/bash\necho "$@" >> %s/fk\necho "fold refused"; exit 1\n' "$t" > "$t/foldfail"; chmod +x "$t/foldfail"
+  fsave=${HPO_RELAY_FOLD:-}; export HPO_RELAY_FOLD=$t/foldfail; : > "$t/fk"
+  cfref handoff/cf-f code.txt "code F"; cfref handoff-wip/cf-f BLOCKED.md "body_push: REFUSED CARRY-LANDED"
+  cfref handoff-wip/cf-f-body BODY.md "the body F"; carry_fold_arm >/dev/null 2>&1
+  e0=$(( $(date +%s) - 1800 ))
+  awk -v e=$e0 '$1 == "cf-f" { $5 = e } 1' "$t/state/cloud-fold-judged" > "$t/memo" && mv "$t/memo" "$t/state/cloud-fold-judged"
+  GIT_AUTHOR_DATE="2005-01-01T00:00:00Z" GIT_COMMITTER_DATE="2005-01-01T00:00:00Z" cfref handoff-wip/cf-f-body BODY.md "the body F"
+  cfo=$(carry_fold_arm 2>&1)
+  chk "a failed carry_fold.py (fold-failed) stands over a re-kept body with the same blob and handoff tip" 0 test "$(grep -c 'topic cf-f ' "$t/fk")" = 1
+  chk "... its tick line says OWED, unchanged" 0 grep -q "OWED carry-fold cf-f unchanged since" <<< "$cfo"
+  chk "... and the standing record keeps its first epoch, so the retry bound runs from the first failure" 0 \
+    awk -v e=$e0 '$1 == "cf-f" && $5 == e { f = 1 } END { exit !f }' "$t/state/cloud-fold-judged"
+  if [ -n "$fsave" ]; then export HPO_RELAY_FOLD=$fsave; else unset HPO_RELAY_FOLD; fi
+  cfref handoff-wip/cf-l BLOCKED.md "the fixer is stuck, again"; carry_fold_arm >/dev/null 2>&1
+  awk '$1 == "cf-l" { $6 = ""; $7 = ""; gsub(/  +/, " ") } 1' "$t/state/cloud-fold-judged" > "$t/memo" && mv "$t/memo" "$t/state/cloud-fold-judged"
+  : > "$t/fetches"; cfo=$(git() { [ "$1" != fetch ] || echo "$*" >> "$t/fetches"; command git "$@"; }; carry_fold_arm 2>&1)
+  chk "a memo record from before the blob and tip fields is judged again, not read with shifted fields" 0 grep -q "handoff-wip/cf-l\$" "$t/fetches"
   unset HPO_RELAY_FOLD HPO_RELAY_BODYPUSH; cd "$t/w" || exit 1
   cd / && rm -rf "$t"
   echo "cloud_relay self-test: $((ok+bad)) checks, $bad failed"; [ "$bad" = 0 ]
diff --git a/tools/audit/seat/ledger.py b/tools/audit/seat/ledger.py
index fbf4c39884..01a3ae0d98 100644
--- a/tools/audit/seat/ledger.py
+++ b/tools/audit/seat/ledger.py
@@ -380,6 +380,16 @@ def attempts(rows: list) -> dict:
 
 
 # ------------------------------------------------------------------- level
+def empty_net(git, main: str, tip: str) -> bool:
+    """tip's change against its merge-base with main is nothing, read cleanly: an add-then-remove pair
+    leaves no diff to carry. An unreadable merge-base or diff is not empty."""
+    rc, mb = git(["merge-base", main, tip])
+    if rc:
+        return False
+    rc, names = git(["diff", "--name-status", "--no-renames", mb.strip(), tip])
+    return rc == 0 and not names.strip()
+
+
 def covered(git, main: str, tip: str) -> bool:
     """Main carries every file tip's uncovered commits touch: the same bytes at
     the path; an added file's bytes elsewhere (a recovery moved it); a deletion
@@ -458,7 +468,7 @@ def reverse_applies(git, main: str, tip: str) -> bool:
                 and git(["apply", "--cached", "--check", patch], env)[0] != 0)
 
 
-ANCESTRY_WHY, CONTENT_WHY = ("ancestor", "merges-only"), ("reverse-apply", "content")
+ANCESTRY_WHY, CONTENT_WHY = ("ancestor", "merges-only"), ("reverse-apply", "empty", "content")
 
 
 def landed(git, main: str, tip: str, heads=(), ancestry: bool = True, content: bool = True) -> "str | None":
@@ -469,6 +479,7 @@ def landed(git, main: str, tip: str, heads=(), ancestry: bool = True, content: b
       merges-only    the only commits outside them are merges whose combined
                      diff is empty (no resolution of their own)
       reverse-apply  reverse_applies: the patch is on main, context and all
+      empty          the net change against the merge-base is nothing (an add-then-remove pair)
       content        covered: the change is on main under another commit"""
     if ancestry:
         rc, out = git(["rev-list", "--count", tip, "--not", main, *heads])
@@ -483,6 +494,8 @@ def landed(git, main: str, tip: str, heads=(), ancestry: bool = True, content: b
     if content:
         if reverse_applies(git, main, tip):
             return "reverse-apply"
+        if empty_net(git, main, tip):  # mut:emptynet
+            return "empty"
         if covered(git, main, tip):
             return "content"
     return None
@@ -1181,6 +1194,12 @@ def self_test() -> int:
         check("landed: a tip inside main reads ancestor, not merges-only", landed(gw, mn, anc) == "ancestor")
         check("landed: the re-applied hunk is content (reverse-apply cannot: forward applies too)",
               landed(gw, mn, cov) == "content" and not reverse_applies(gw, mn, cov))
+        g("checkout", "-qb", "work18", mn)
+        put("tmp_add.txt", "added then removed\n", "add a file")
+        g("rm", "-q", "tmp_add.txt")
+        g("commit", "-qm", "remove it again")
+        emt = g("rev-parse", "HEAD")
+        rl = put("real_new.txt", "one real uncovered line\n", "one real uncovered add on the empty pair")
         g("checkout", "-qb", "work7", gb)
         mv = put("moved.txt", "same bytes\n", "add a file")
         g("checkout", "-qb", "work8", gb)
@@ -1222,6 +1241,18 @@ def self_test() -> int:
         put("evil.txt", "E\n", "a merge with a resolution of its own")
         check("null control: a merge carrying its own resolution is not merges-only",
               landed(gw, m_a, g("rev-parse", "HEAD"), [fixh], content=False) is None)
+        # Carry 20, one oracle so that no setup line above can be dropped unread: an add-then-remove tip lands as
+        # empty; the same pair plus one real line stays None; a failing merge-base read (whose output, here, would
+        # diff empty) or a failing diff read is not empty; and landed's reasons are exactly the two declared tuples.
+        bad_rc, _ = gw(["merge-base", "--no-such-option"])
+        check("carry 20: an empty net diff lands as empty; one real line, an unreadable merge-base or diff does not;"
+              " the reasons driven here are ANCESTRY_WHY + CONTENT_WHY",
+              landed(gw, mn, emt) == "empty" and not covered(gw, mn, emt) and landed(gw, mn, rl) is None
+              and empty_net(gw, mn, emt) and bad_rc
+              and not empty_net(lambda a: (bad_rc, mn) if a[0] == "merge-base" else gw(a), mn, emt)
+              and not empty_net(lambda a: gw(a + ["--no-such-option"]) if a[0] == "diff" else gw(a), mn, emt)
+              and {landed(gw, mn, anc), landed(gw, m_a, tipm, [fixh]), landed(gw, rvm, rv), landed(gw, mn, emt),
+                   landed(gw, mn, cov)} == {*ANCESTRY_WHY, *CONTENT_WHY})
         g("checkout", "-q", "main")
         hr = [tuple(l.split()) for l in g("ls-remote", "origin", "refs/heads/handoff/*",
                                            "refs/heads/handoff-body/*").splitlines()]

## Before you return the verdict (P275)
Run `python3 -I tools/audit/carry_audit.py check --body <PR body file> --comments <file holding [{"id": 0, "body": <verdict.md text>}]>`. Give every reported item its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>`;
an evidence line flagged by its wording takes `Carry: dismissed: evidence, not a finding`. Return the verdict only at rc 0.
