# Review packet #3191
head: 5640ad9d03e8a9bd9b5f8cae7701887170e70713
base: 616868bdc5ca54d9555cfc89715f05a33527661e

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: red
CodeQL id=126543728451 neutral
arch-score / arch-score id=126543355314 success
arm id=126543199441 skipped
budget-raise-gate / budget-raise-gate id=126543355293 success
cancel-superseded id=126543131649 success
codeql / Analyze (actions) id=126543354965 success
codeql / Analyze (javascript-typescript) id=126543355258 success
codeql / Analyze (python) id=126543354992 in_progress
governance / delivery-status id=126543355204 success
governance / delivery-status-publish id=126543357717 skipped
governance / env-matrix id=126543355114 success
governance / instrument-self-tests id=126543355092 in_progress
governance / policy-docs id=126543355011 success
governance / record id=126543357522 skipped
governance / wave-script id=126543355067 success
hassfest / hassfest id=126543354935 success
kernel-points id=126543355901 skipped
prelude id=126543131713 in_progress
refresh id=126543131341 success
tests / arch-instrument id=126543564704 success
tests / briefs id=126543355380 success
tests / browser id=126543564844 success
tests / claims-autofix id=126547788677 skipped
tests / closure-scope id=126543355327 success
tests / closures id=126543564932 success
tests / closures-autofix id=126550646315 skipped
tests / coverage id=126543564870 in_progress
tests / fast (3.14) id=126543564737 success
tests / mutation id=126543355357 success
tests / mutation-autofix id=126543700689 skipped
tests / mutation-pins id=126543699998 skipped
tests / nightly-ha id=126543567062 skipped
tests / nightly-status id=126543355253 failure
tests / replay id=126543567391 skipped
tests / typing id=126543564965 success
validate / validate-hacs id=126543355398 success

## Refusals
none

## Advisories
none

## carry_audit at the head
CARRY-AUDIT: 0 finding item(s): 0 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
ok         HPO_GATE_LOCK_DIR=$(mktemp -d)/lk python3 tests/gate_lock.py slot-take --label sN --owner-pid <pid>
             `tests/gate_lock.py` is in the tree at this head
  ok         PYTHONPATH=tests/hastub bash tools/pr/prepr.sh --self-test
             `tools/pr/prepr.sh` is in the tree at this head
  ok         python3 tests/structure.py
             `tests/structure.py` is in the tree at this head
  ok         node tools/policy/policy_lint.mjs
             `tools/policy/policy_lint.mjs` is in the tree at this head

FIGURES: 4 resolved, 0 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
none

## Three-dot diff
diff --git a/.claude/rules/gate-scoping.md b/.claude/rules/gate-scoping.md
index 9224eae4e..d39c22c8a 100644
--- a/.claude/rules/gate-scoping.md
+++ b/.claude/rules/gate-scoping.md
@@ -20,12 +20,11 @@ clears `tests/entities.py`'s history reds (#1693, #1699, #1704).
 
 `/tmp/hpo-gate.lock` holds two leases; `tests/gate_lock.py needs-lease` names a script's:
 `lease`, exclusive, measuring the machine (`tests/stress.py`, `tests/harness_headers.py`);
-`slot`, one of `$HPO_HEAVY_SLOTS` (four), for one unrecorded or recorded in `closures.json` at or above
-`SLOT_MIN_SECONDS`; else `none`. `$HPO_SLOT_LABEL` names a run's slot. Arrival orders
+`slot`, one of `$HPO_HEAVY_SLOTS` (four): unrecorded, or `closures.json` seconds at or above
+`SLOT_MIN_SECONDS`; else `none`. `prepr.sh` takes one at its first heavy step. Arrival orders
 each priority band; a dead or expired ticket is skipped. An expired or abandoned lease is
 free, a slot once its pid is gone. A `lease` wait ends at the script's recorded seconds, rc 76: `run.sh` names it unrun. `flock-wrap`
-retakes a lapsed lease. That lease, not the tick's count, is nudge.md §8's cap; hold it by hand
-with `tests/gate_lock.py`, never `mkdir`:
+retakes a lapsed lease. That lease, not the tick's count, is nudge.md §8's cap; hold it with `tests/gate_lock.py`, never `mkdir`:
 
 ```
 python3 tests/gate_lock.py take --label <your-label>
diff --git a/.cursor/rules/gate-scoping.mdc b/.cursor/rules/gate-scoping.mdc
index 48dc36db2..52e5208e4 100644
--- a/.cursor/rules/gate-scoping.mdc
+++ b/.cursor/rules/gate-scoping.mdc
@@ -19,12 +19,11 @@ clears `tests/entities.py`'s history reds (#1693, #1699, #1704).
 
 `/tmp/hpo-gate.lock` holds two leases; `tests/gate_lock.py needs-lease` names a script's:
 `lease`, exclusive, measuring the machine (`tests/stress.py`, `tests/harness_headers.py`);
-`slot`, one of `$HPO_HEAVY_SLOTS` (four), for one unrecorded or recorded in `closures.json` at or above
-`SLOT_MIN_SECONDS`; else `none`. `$HPO_SLOT_LABEL` names a run's slot. Arrival orders
+`slot`, one of `$HPO_HEAVY_SLOTS` (four): unrecorded, or `closures.json` seconds at or above
+`SLOT_MIN_SECONDS`; else `none`. `prepr.sh` takes one at its first heavy step. Arrival orders
 each priority band; a dead or expired ticket is skipped. An expired or abandoned lease is
 free, a slot once its pid is gone. A `lease` wait ends at the script's recorded seconds, rc 76: `run.sh` names it unrun. `flock-wrap`
-retakes a lapsed lease. That lease, not the tick's count, is nudge.md §8's cap; hold it by hand
-with `tests/gate_lock.py`, never `mkdir`:
+retakes a lapsed lease. That lease, not the tick's count, is nudge.md §8's cap; hold it with `tests/gate_lock.py`, never `mkdir`:
 
 ```
 python3 tests/gate_lock.py take --label <your-label>
diff --git a/dev/governance/roles/nudge.md b/dev/governance/roles/nudge.md
index 00a6a6e2b..8270360db 100644
--- a/dev/governance/roles/nudge.md
+++ b/dev/governance/roles/nudge.md
@@ -70,7 +70,7 @@ Direct-merge only what step 3 leaves out of the queue, other than a `record:` pu
 
 ## 8. Prepr slots
 
-Up to four `prepr.sh` run at a time: each takes one of `tests/gate_lock.py`'s four heavy slots, and a fifth queues: the lease, not the tick's count, is the cap. A seat's own prepr counts. `tools/audit/seat/open_pr.sh`, `tools/audit/seat/update_pr.sh`, `tools/pr/app_push.sh` and a `tests/derive_closures.sh` run each count as one. Do not recarry a branch a seat is writing. Skip a group whose fixer or reviewer worktree was written in the last 15 minutes, or whose own prepr is running. Recarry may run during a train's CI wait. It may not run while the train itself is in recarry.
+Up to four `prepr.sh` run at a time: each takes one of `tests/gate_lock.py`'s four heavy slots just before its first heavy step (a run whose heavy steps are all skipped takes none), and a fifth queues: the lease, not the tick's count, is the cap. A seat's own prepr counts. `tools/audit/seat/open_pr.sh`, `tools/audit/seat/update_pr.sh`, `tools/pr/app_push.sh` and a `tests/derive_closures.sh` run each count as one. Do not recarry a branch a seat is writing. Skip a group whose fixer or reviewer worktree was written in the last 15 minutes, or whose own prepr is running. Recarry may run during a train's CI wait. It may not run while the train itself is in recarry.
 
 ## 9. Conflicting or DIRTY
 
diff --git a/dev/governance/rules/gate-scoping.md b/dev/governance/rules/gate-scoping.md
index 9224eae4e..d39c22c8a 100644
--- a/dev/governance/rules/gate-scoping.md
+++ b/dev/governance/rules/gate-scoping.md
@@ -20,12 +20,11 @@ clears `tests/entities.py`'s history reds (#1693, #1699, #1704).
 
 `/tmp/hpo-gate.lock` holds two leases; `tests/gate_lock.py needs-lease` names a script's:
 `lease`, exclusive, measuring the machine (`tests/stress.py`, `tests/harness_headers.py`);
-`slot`, one of `$HPO_HEAVY_SLOTS` (four), for one unrecorded or recorded in `closures.json` at or above
-`SLOT_MIN_SECONDS`; else `none`. `$HPO_SLOT_LABEL` names a run's slot. Arrival orders
+`slot`, one of `$HPO_HEAVY_SLOTS` (four): unrecorded, or `closures.json` seconds at or above
+`SLOT_MIN_SECONDS`; else `none`. `prepr.sh` takes one at its first heavy step. Arrival orders
 each priority band; a dead or expired ticket is skipped. An expired or abandoned lease is
 free, a slot once its pid is gone. A `lease` wait ends at the script's recorded seconds, rc 76: `run.sh` names it unrun. `flock-wrap`
-retakes a lapsed lease. That lease, not the tick's count, is nudge.md §8's cap; hold it by hand
-with `tests/gate_lock.py`, never `mkdir`:
+retakes a lapsed lease. That lease, not the tick's count, is nudge.md §8's cap; hold it with `tests/gate_lock.py`, never `mkdir`:
 
 ```
 python3 tests/gate_lock.py take --label <your-label>
diff --git a/dev/programme/delivery/3191.md b/dev/programme/delivery/3191.md
new file mode 100644
index 000000000..a4255d489
--- /dev/null
+++ b/dev/programme/delivery/3191.md
@@ -0,0 +1 @@
+- [#3191](https://github.com/tvofi/heatpump_optimizer/pull/3191) — **open**, R10-PREPR-CAP: lazy heavy-slot take (R10-PREPR-CAP)
diff --git a/tools/pr/prepr.sh b/tools/pr/prepr.sh
index fc76d1e0e..4e9d7f7fe 100755
--- a/tools/pr/prepr.sh
+++ b/tools/pr/prepr.sh
@@ -769,6 +769,19 @@ closures_line() { # merge base; rc 0 covered, 1 refused, 3 skipped
   rm -rf "$cw"; return "$r"
 }
 
+# rc 0 when `closures_line` would run the recorder, i.e. the slot is owed.
+closures_owes_slot() { # merge base
+  local cw k r=1
+  closures_records_here || return 1
+  cw=$(mktemp -d)
+  if git diff --no-renames --name-only "$1"...HEAD > "$cw/changed.txt" \
+     && python3 tests/closure.py affected --files-from "$cw/changed.txt" --workdir "$cw/aff" >/dev/null 2>&1; then
+    k=$(cat "$cw/aff/affected.case" 2>/dev/null)
+    [ "$k" = scoped ] && [ -s "$cw/aff/affected.scripts" ] && r=0
+  fi
+  rm -rf "$cw"; return "$r"
+}
+
 # Step 6b runs `closures_line` as a job the prepr `wait`s on, never inside
 # `$(...)`: a trapped signal ends that `wait` at once, where the prepr would
 # defer its own TERM trap until a command substitution's recorder finished --
@@ -995,6 +1008,24 @@ body_line() { # body file, head sha, title, paths file, merge base, head, [unpin
   rm -f "$out"; return "$r"
 }
 
+# Step 1a3's early `## Head` arm (P208, carry 23): the SAME body check step 7
+# runs, invoked before any heavy step, and reduced to its `## Head` refusal --
+# no second parser. The `## Approval` arm needs the diff's path list and stays
+# late; the other body refusals stay step 7's, so a run with a matching `## Head`
+# does exactly what it did. rc 0 the body names this head (or no body to read),
+# 1 it does not: the refusal line is the one policy_lint prints.
+head_arm() { # body file, merge base -> refusal line on stdout
+  local out paths r
+  out=$(mktemp); paths=$(mktemp)
+  diff_paths "$2" "$paths" || { rm -f "$out" "$paths"; return 0; }
+  body_check "$1" "$(git rev-parse HEAD)" "$(git log -1 --format=%s)" "$paths" >"$out" 2>&1
+  if grep -q '`## Head` does not name' "$out"; then
+    grep -m1 '`## Head` does not name' "$out" | sed 's/^[[:space:]]*//'
+    r=1
+  else r=0; fi
+  rm -f "$out" "$paths"; return "$r"
+}
+
 # Step 7e's whole body, so `--self-test` drives the code the step runs.
 # WHY THIS EXISTS (R10-FLOW-JIDOKA). `pr-contract` decides a body's markers only
 # after the push, with `carry_audit.py check --body`; this is that same checker on
@@ -2051,6 +2082,18 @@ EOS
   case "$got" in *'no budget leaf raised'*) st 1 1 "and the ok line says no raise was found, so the gate ran";; *) st 0 1 "and the ok line says no raise was found, so the gate ran";; esac
   got=$(bl base docs unnamed-red.md)
   st "${got%%:*}" 0 "a diff touching no budget file passes"
+  # Step 1a3's early arm (P208, carry 23), driven through `head_arm` over the same
+  # fixture: a body whose `## Head` names another sha is refused with the
+  # policy_lint line; the body naming this head passes (null control).
+  BRH=$(git --git-dir="$BR/.git" rev-parse HEAD)
+  sed "s/$ZERO/$BRH/g" "$DABS/budget-answered.md" > "$BR/head-ok.md"
+  got=$(GIT_DIR="$BR/.git" head_arm "$DABS/budget-answered.md" base); r=$?
+  st "$r" 1 "head_arm refuses a body whose ## Head names another sha, before any heavy step"
+  case "$got" in *'`## Head` does not name'*) st 1 1 "and prints policy_lint's own line";; *) st 0 1 "and prints policy_lint's own line";; esac
+  got=$(GIT_DIR="$BR/.git" head_arm "$BR/head-ok.md" base); r=$?
+  st "$r" 0 "head_arm passes a body naming this head (null control)"
+  hflow_ok=$(awk '/^# --- 1a3\./{f=1} /^# --- 1b0\./{exit} f' "$PREPR_PATH")
+  st "$(grep -cF 'head_arm "$1" "$BASE"' <<<"$hflow_ok")" 1 "the main flow runs the early ## Head arm between the red-check arm and the priority/slot steps"
   # The same plant through step 7 (R10-FLY-BUDGET-LEAF): no raise, so the
   # line ends `no budget leaf raised`, and what precedes it must be the error.
   # `bl base docs unnamed-red.md` above is its null control.
@@ -3257,6 +3300,24 @@ STUB
   ( cd "$QT" && claims_reg_line "$WF/changed" "$QC" ) >/dev/null 2>&1
   st $? 1 "and a target the repository lacks is not copied, so the register is refused (null control)"
   rm -rf "$QT" "$QC"
+  # THE COST OF 6g'S TARGET COPY IS PINNED (carry 24). The loop is shell-only so
+  # the check stays under the owner's 5 s cap; a per-target interpreter put it
+  # over (2.84-3.12 s across 84 targets, #2853). The pin is the count of
+  # interpreter spawns, which must not grow with the number of targets: 40 and
+  # 4 targets spawn the same number.
+  CQ=$(mktemp -d); mkdir -p "$CQ/$(dirname "$CLAIMS_GEN")"
+  printf '# --print-link-targets\n' >"$CQ/$CLAIMS_GEN"
+  printf '1 0\n' >"$CQ/$(dirname "$CLAIMS_GEN")/claims.json"; printf 'x\n' >"$CQ/$(dirname "$CLAIMS_GEN")/claims.md"
+  printf '%s\n' README.md >"$WF/changed" 2>/dev/null || { WF=$(mktemp -d); printf '%s\n' README.md >"$WF/changed"; }
+  claims_spawns() { # target count -> interpreter spawns
+    : >"$CQ/spawns"
+    ( N=$1; python3() { echo x >>"$CQ/spawns"; case "$*" in *--print-link-targets*) seq 1 "$N" | sed 's|^|docs/t|';; esac; return 0; }
+      claims_reg_line "$WF/changed" "$CQ" ) >/dev/null 2>&1
+    wc -l <"$CQ/spawns" | tr -d ' '
+  }
+  n40=$(claims_spawns 40); n4=$(claims_spawns 4)
+  st "$([ "$n40" = "$n4" ] && [ "$n4" -ge 2 ] && [ "$n4" -le 3 ] && echo flat)" flat "6g spawns the same few interpreters for 40 link targets as for 4 (${n4}/${n40}): no per-target interpreter"
+  rm -rf "$CQ"
   rm -rf "$CG"
   rm -rf "${WF:?}"
 
@@ -3399,8 +3460,29 @@ STUB
   st "$(grep -cF '${HPO_SLOT_LABEL:-}' <<<"$flow")" 1 "and joins a slot it was already inside instead of taking a second"
   st "$(grep -cF 'slot-unleased --label "$SLOT_LABEL"' <<<"$flow")" 1 "a run that cannot take a slot counts itself in slot-status"
   st "$(grep -cF "slot-leased --label '\$SLOT_LABEL'" <<<"$flow")" 1 "and clears the count on the way out"
-  slot_order=$(awk '/step "policy_lint"/{seen=1} /slot-take --label/{ if(!seen){print "ok"} exit }' <<<"$flow")
-  st "$slot_order" ok "and takes it before the heavy steps begin"
+  # LAZY (carries 25 and 26): the take is a function the heavy steps call, never
+  # an unconditional line before the light ones. Every call precedes the heavy
+  # command it guards, and the idempotence and the join are DRIVEN below.
+  st "$(grep -cE '^ *take_slot( |$)|&& take_slot$' <<<"$flow")" 4 "the main flow calls take_slot at the mutants, self-test, closures and diff-mutants steps (and defines it once)"
+  slot_order=$(awk '/^take_slot\(\)/{d=1} /step "policy_lint"/{seen=1} /^ *take_slot$/{ if(d && seen){print "ok"} exit }' <<<"$flow")
+  st "$slot_order" ok "and the first call sits after the light policy_lint step: a run that skips every heavy step never takes one"
+  st "$(awk '/^take_slot$/{c=1} /policy_lint_mutants.mjs; then heavy_run/{ if(c){print "ok"} exit }' <<<"$flow")" ok "the mutants drive runs inside the slot (take_slot precedes its heavy_run)"
+  st "$(awk '/^  take_slot$/{c=1} /prepr.sh --self-test; else heavy_run/{ if(c){print "ok"} exit }' <<<"$flow")" ok "the self-test runs inside the slot"
+  TSL=$(mktemp -d); : > "$TSL/log"
+  ( SLOT_LABEL=prepr-test; SLOT_TAKEN=""; unset HPO_SLOT_LABEL
+    say() { :; }; exit_on_signals() { :; }
+    python3() { echo "$*" >> "$TSL/log"; return 0; }
+    eval "$(sed -n '/^take_slot()/,/^}/p' "$PREPR_PATH")"
+    take_slot; take_slot )
+  st "$(grep -c slot-take "$TSL/log")" 1 "take_slot called twice takes exactly one slot (idempotent)"
+  : > "$TSL/log"
+  ( SLOT_LABEL=prepr-test; SLOT_TAKEN=""; export HPO_SLOT_LABEL=outer
+    say() { :; }; exit_on_signals() { :; }
+    python3() { echo "$*" >> "$TSL/log"; return 0; }
+    eval "$(sed -n '/^take_slot()/,/^}/p' "$PREPR_PATH")"
+    take_slot )
+  st "$(grep -c slot-take "$TSL/log")" 0 "a take_slot inside an inherited slot takes none (null control: a nested heavy step joins)"
+  rm -rf "$TSL"
   # (7) The priority the slot-take reads is derived from the branch's group and
   # exported BEFORE the take, so the lease's ticket carries it (tvofi,
   # 2026-10-20). The derivation's own four arms are gate_priority.py's
@@ -3552,7 +3634,7 @@ EOF
   # survivors: `EARLY_REDS_RC=0` in step 1a2, and `if false` for the --pr-branch
   # guard). The arm is a stub returning a chosen rc; the blocks are the
   # production text, extracted and evaluated.
-  blk1a2=$(sed -n '/^# --- 1a2\./,/^# --- 1b0\./p' "$PREPR_PATH" | sed '$d')
+  blk1a2=$(sed -n '/^# --- 1a2\./,/^# --- 1a3\./p' "$PREPR_PATH" | sed '$d')
   bcg=$(sed -n '/^if \[ "${1:-}" = "--body-check" \]/,/^  P=\$(mktemp)/p' "$PREPR_PATH" | sed '$d'; echo fi)
   # The body FILE lives under $WB (a mktemp dir inside ST_ROOT, which the EXIT trap removes),
   # never in the tracked fixture directory: a stray file there dirties the
@@ -3581,6 +3663,26 @@ EOF
     case "$got" in 0:*FELL-THROUGH*) r=0 ;; *) r=1 ;; esac
     st "$r" 0 "step 1a2 does not refuse when the arm returns rc $sr (null control)"
   done
+  # Step 1a3 (P208) driven the same way: the arm is a stub with a chosen rc.
+  blk1a3=$(sed -n '/^# --- 1a3\./,/^# --- 1b0\./p' "$PREPR_PATH" | sed '$d')
+  early_head() { # stub rc -> "<exit rc>:<output>"
+    local o r
+    o=$( STUBRC=$1; rc=0; BASE=x
+      head_arm() { echo "stub-head-line"; return "$STUBRC"; }
+      step() { echo "STEP $1 $2 $3"; [ "$2" -eq 0 ] || rc=1; }
+      summary_end() { :; }
+      set -- "$WB/wiring-body.md"
+      eval "$blk1a3"; echo FELL-THROUGH ); r=$?
+    echo "$r:$o"
+  }
+  got=$(early_head 1)
+  case "$got" in 1:*'STEP pr-body 1 stub-head-line'*) r=0 ;; *) r=1 ;; esac
+  st "$r" 0 "step 1a3 exits nonzero on a head_arm refusal, naming it, before any heavy step"
+  case "$got" in *FELL-THROUGH*) r=1 ;; *) r=0 ;; esac
+  st "$r" 0 "and does not fall through to the heavy steps"
+  got=$(early_head 0)
+  case "$got" in 0:*FELL-THROUGH*) r=0 ;; *) r=1 ;; esac
+  st "$r" 0 "step 1a3 lets a body naming this head run every step as today (null control)"
   bcchk() { # stub rc -> output ending REDSRC=<BODY_CHECK_REDS_RC>
     ( STUBRC=$1; BASE=x
       reds_arm() { echo "stub-line"; return "$STUBRC"; }
@@ -3748,6 +3850,18 @@ if [ -n "${1:-}" ] && [ "${1:-}" != "--self-test" ] && [ -f "$1" ]; then
   fi
 fi
 
+# --- 1a3. the body's `## Head` names this head, BEFORE the heavy steps (P208).
+# Step 7 stays: the head can move during the run (`update_pr.sh`/`open_pr.sh`
+# merge main before pushing). The arm is `head_arm`, the existing body check.
+if [ -n "${1:-}" ] && [ "${1:-}" != "--self-test" ] && [ -f "$1" ]; then
+  EARLY_HEAD_LINE=$(head_arm "$1" "$BASE"); EARLY_HEAD_RC=$?
+  if [ "$EARLY_HEAD_RC" -ne 0 ]; then
+    step "pr-body" 1 "$EARLY_HEAD_LINE -- refused before any heavy step (P208)"
+    summary_end "$(git rev-parse HEAD)"
+    exit $rc
+  fi
+fi
+
 # --- 1b0. the gate-lease priority of this branch's group (tvofi, 2026-10-20).
 # The lease is generic: it orders waiters by an integer and never decides who
 # deserves one. This step supplies the integer from tools/pr/gate_priority.py,
@@ -3780,9 +3894,23 @@ say ok "gate priority" "$HPO_GATE_PRIORITY (env, .gate-priority, then the critic
 # A FAILED take is a WARN, not a refusal -- a broken lease must not make a branch
 # unrunnable, and the wait a healthy lease imposes is bounded by its own expiry.
 SLOT_LABEL="prepr-$$"
-if [ -n "${HPO_SLOT_LABEL:-}" ]; then
-  say ok "heavy slot" "joined $HPO_SLOT_LABEL: this run is already inside a slot"
-else
+# LAZY (R10-PREPR-CAP carries 25 and 26). The slot is taken by `take_slot`, just
+# before the first heavy step that is not skipped -- the mutants drive, the
+# self-test, the scoped closure recordings, the diff mutants -- and kept to the
+# end. A run whose heavy steps are all skipped never queues: the light checks
+# before it ran unleased, and a 0-script prepr waited 25 min 55 s in the FIFO
+# for seconds of work. A failed plan derivation runs every heavy step, so it
+# takes the slot at the first one. A nested heavy step still joins this slot
+# through HPO_SLOT_LABEL.
+SLOT_TAKEN=""
+take_slot() { # idempotent: the first call takes (or joins) the slot, later calls are no-ops
+  [ -z "$SLOT_TAKEN" ] || return 0
+  SLOT_TAKEN=1
+  local slot_stderr
+  if [ -n "${HPO_SLOT_LABEL:-}" ]; then
+    say ok "heavy slot" "joined $HPO_SLOT_LABEL: this run is already inside a slot"
+    return 0
+  fi
   slot_stderr=$(mktemp)
   if python3 tests/gate_lock.py slot-take --label "$SLOT_LABEL" --owner-pid $$ >"$slot_stderr" 2>&1; then
     export HPO_SLOT_LABEL="$SLOT_LABEL"
@@ -3803,7 +3931,7 @@ else
     exit_on_signals
   fi
   rm -f "$slot_stderr"
-fi
+}
 
 # One interpreter resolution per run, shared by steps 6a and 6c (`recorder_python`).
 PREPR_RECORDER_CACHE=/tmp/prepr-recpy.$$; : > "$PREPR_RECORDER_CACHE"  # not exported: the nested --self-test must resolve afresh
@@ -3838,6 +3966,7 @@ HV=$(heavy_skip "mutants" "${HEAVY_PLAN_FILE:-}")
 if [ $? -eq 0 ]; then
   say skip "mutants" "$HV"
 else
+take_slot
 if test -f .claude/workflows/policy_lint_mutants.mjs; then heavy_run /tmp/prepr-mutants.$$ node .claude/workflows/policy_lint_mutants.mjs; else heavy_run /tmp/prepr-mutants.$$ node tools/policy/policy_lint_mutants.mjs; fi
 step "mutants" $? "$(tail -1 /tmp/prepr-mutants.$$)"
 rm -f /tmp/prepr-mutants.$$
@@ -3952,6 +4081,7 @@ step "pinned graders" $? "$(echo $VERDICT)"
 # detector. A diff that cannot be listed is treated as owing it.
 if ! git diff --no-renames --name-only "$BASE"...HEAD > /tmp/prepr-st.$$ 2>/dev/null \
      || selftest_owed /tmp/prepr-st.$$; then
+  take_slot
   if test -f tools/audit/prepr.sh; then heavy_run /tmp/prepr-stlog.$$ bash tools/audit/prepr.sh --self-test; else heavy_run /tmp/prepr-stlog.$$ bash tools/pr/prepr.sh --self-test; fi
   step "self-test" $? "$(tail -1 /tmp/prepr-stlog.$$; grep -E '^  FAIL' /tmp/prepr-stlog.$$ | head -3 | tr '\n' ' ')"
   rm -f /tmp/prepr-stlog.$$
@@ -4026,6 +4156,9 @@ step "claims hygiene" $? "$CLAIMS_LINE"
 if [ -n "${PREPR_SKIP_CLOSURES:-}" ]; then
   say skip "closures" "PREPR_SKIP_CLOSURES is set -- closures-autofix is the only check left"
 else
+  # The slot is taken only when the recorder will run: a scoped diff on a
+  # machine that records here (`closures_owes_slot`); a skip or a full diff is CI's.
+  closures_owes_slot "$BASE" && take_slot
   closures_step "$BASE"
   case $? in
     3) say skip "closures" "$CLOSURES_LINE" ;;
@@ -4062,6 +4195,7 @@ if [ -z "${MUTANT_CMD:-}" ]; then
 elif [ ! -f tools/audit/seat/mutant_run.py ]; then
   say skip "diff mutants" "tools/audit/seat/mutant_run.py is not in this tree"
 else
+  take_slot
   MUT_OUT=$(python3 -I tools/audit/seat/mutant_run.py --diff "$BASE...HEAD" --cmd "$MUTANT_CMD" \
     --max-mutants "${MUTANT_MAX:-40}" --report-only 2>&1)
   MUT_N=$(printf '%s\n' "$MUT_OUT" | grep -c '^SURVIVED ')

## Before you return the verdict (P275)
Run `python3 -I tools/audit/carry_audit.py check --body <PR body file> --comments <file holding [{"id": 0, "body": <verdict.md text>}]>`. Give every reported item its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>`;
an evidence line flagged by its wording takes `Carry: dismissed: evidence, not a finding`. Return the verdict only at rc 0.
