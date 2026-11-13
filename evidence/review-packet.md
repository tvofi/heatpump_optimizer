# Review packet #3547
head: a81d7f15293fc2101f42e48ade37ef7022c35517
base: 7eadd75f3c420404aabc83d4b05f9691f3e49136

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: green
CodeQL id=131821437805 success
arch-score / arch-score id=131876068378 success
arm id=131814160470 skipped
budget-raise-gate / budget-raise-gate id=131876068392 success
cancel-superseded id=131876067115 success
codeql id=131876112058 skipped
codeql / Analyze (actions) id=131876109239 success
codeql / Analyze (javascript-typescript) id=131876069206 success
codeql / Analyze (python) id=131876068837 success
gate id=131876071466 success
governance id=131876043342 skipped
governance / delivery-status id=131876069704 success
governance / delivery-status-publish id=131876068775 skipped
governance / env-matrix id=131876069131 success
governance / instrument-self-tests id=131876069298 success
governance / policy-docs id=131876068655 success
governance / record id=131876069251 skipped
governance / wave-script id=131876069444 success
hassfest id=131876043141 skipped
hassfest / hassfest id=131876069327 success
kernel-points id=131876068033 skipped
pr-contract id=131876043726 skipped
pr-contract / pr-contract id=131876073410 success
prelude id=131876117063 success
refresh id=131876130956 success
sweep-self id=131878100765 skipped
tests id=131876043753 skipped
tests / arch-instrument id=131876070260 success
tests / briefs id=131876069516 success
tests / browser id=131876070559 success
tests / ci-ratchet id=131876072028 skipped
tests / claims-autofix id=131876071665 skipped
tests / closure-scope id=131876068795 success
tests / closures id=131876071536 success
tests / closures-autofix id=131876071727 skipped
tests / coverage id=131876071611 success
tests / coverage-ratchet id=131876071887 success
tests / fast (3.14) id=131876070833 success
tests / graders-head-copy id=131876071522 success
tests / lane-proofs id=131876071726 success
tests / mutation id=131876069271 success
tests / mutation-autofix id=131876071127 skipped
tests / mutation-pins id=131876071110 skipped
tests / nightly-ha id=131876071304 skipped
tests / nightly-status id=131876069306 success
tests / replay id=131876071018 skipped
tests / typing id=131876070669 success
validate id=131876043409 skipped
validate / validate-hacs id=131876068917 success

## Refusals
none

## Advisories
none

## carry_audit at the head
CARRY-AUDIT: 0 finding item(s): 0 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
ok         bash tools/pr/prepr.sh --self-test
             `tools/pr/prepr.sh` is in the tree at this head
  ok         python3 tools/pr/gate_priority.py --self-test
             `tools/pr/gate_priority.py` is in the tree at this head
  ok         python3 tests/structure.py
             `tests/structure.py` is in the tree at this head
  ok         PREPR_SKIP_CODE=1 PREPR_SKIP_CLOSURES=1 bash tools/pr/prepr.sh <body>
             `tools/pr/prepr.sh` is in the tree at this head

FIGURES: 4 resolved, 0 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
none

## Review scope: full (first round: no --reviewed-head)

## Three-dot diff
diff --git a/dev/programme/delivery/3547.md b/dev/programme/delivery/3547.md
new file mode 100644
index 00000000..b5e65567
--- /dev/null
+++ b/dev/programme/delivery/3547.md
@@ -0,0 +1 @@
+- [#3547](https://github.com/tvofi/heatpump_optimizer/pull/3547) — **open**, R10-PREPR-RESIDUE (part 2): r10 prepr residue p2 (R10-PREPR-RESIDUE)
diff --git a/tools/pr/gate_priority.py b/tools/pr/gate_priority.py
index 093cb52b..22160c83 100644
--- a/tools/pr/gate_priority.py
+++ b/tools/pr/gate_priority.py
@@ -3,6 +3,7 @@
 
     python3 tools/pr/gate_priority.py              # HEAD's branch, live roster
     python3 tools/pr/gate_priority.py --branch B    # an explicit branch
+    python3 tools/pr/gate_priority.py --hotfix      # prints 1 when the group is a hotfix, else 0
     python3 tools/pr/gate_priority.py --self-test   # hermetic fixtures
 
 The lease (``tests/gate_lock.py``) is generic: it orders waiters by an integer
@@ -99,35 +100,50 @@ def _roster_ref(repo: str) -> str | None:
     return ref
 
 
-def derived_priority(branch: str, *, repo: str = ".", ref: str | None = None,
-                     fetch: bool = True) -> int:
-    """2 for a hotfix group, 1 for an outside group or one in the
-    critical-path set at the roster ref (a missing or malformed set drops only
-    the critical path's 1; an outside group still answers 1).
-
-    0 for every other answer, including every failure. ``ref`` overrides the
-    live roster ref (the self-test's fixture); ``fetch=False`` reads the local
-    ref without refreshing it.
-    """
+def _rank(branch: str, *, repo: str, ref: str | None, fetch: bool) -> int | None:
+    """The roster dispatch rank of the branch's group, None on any failure."""
     try:
         roster_ref = ref
         if roster_ref is None:
             roster_ref = _roster_ref(repo) if fetch else roster_lib.reader_ref(repo, None)
         if roster_ref is None:
-            return PRIORITY_NORMAL
-        group = roster_lib.group_for_branch(
-            roster_lib.show_roster(repo, roster_ref), branch)
-        if group is None:
-            return PRIORITY_NORMAL
+            return None
         roster = roster_lib.show_roster(repo, roster_ref)
+        group = roster_lib.group_for_branch(roster, branch)
+        if group is None:
+            return None
         critical = roster_lib.critical_path_groups(repo, roster_ref)
         if critical is None:
             critical = set()
-        rank = roster_lib.dispatch_rank(roster, group, critical)
-        return {roster_lib.RANK_HOTFIX: HOTFIX_PRIORITY,
-                roster_lib.RANK_TOP: TOP_PRIORITY}.get(rank, PRIORITY_NORMAL)
+        return roster_lib.dispatch_rank(roster, group, critical)
     except Exception:  # noqa: BLE001 -- a pre-pr helper must never crash a run
-        return PRIORITY_NORMAL
+        return None
+
+
+def derived_priority(branch: str, *, repo: str = ".", ref: str | None = None,
+                     fetch: bool = True) -> int:
+    """2 for a hotfix group, 1 for an outside group or one in the
+    critical-path set at the roster ref (a missing or malformed set drops only
+    the critical path's 1; an outside group still answers 1).
+
+    0 for every other answer, including every failure. ``ref`` overrides the
+    live roster ref (the self-test's fixture); ``fetch=False`` reads the local
+    ref without refreshing it.
+    """
+    rank = _rank(branch, repo=repo, ref=ref, fetch=fetch)
+    return {roster_lib.RANK_HOTFIX: HOTFIX_PRIORITY,
+            roster_lib.RANK_TOP: TOP_PRIORITY}.get(rank, PRIORITY_NORMAL)
+
+
+def is_hotfix(branch: str, *, repo: str = ".", ref: str | None = None,
+              fetch: bool = True) -> bool:
+    """True only when the roster classes the branch's group a hotfix.
+
+    The derived class alone: ``$HPO_GATE_PRIORITY`` and ``.gate-priority`` order
+    the lease and say nothing about the group. Every failure is False, so an
+    unreadable roster yields the full pre-PR run, never a skipped one.
+    """
+    return _rank(branch, repo=repo, ref=ref, fetch=fetch) == roster_lib.RANK_HOTFIX
 
 
 def _declared(raw: str | None) -> int | None:
@@ -243,6 +259,13 @@ def _self_test() -> int:
               [derived(b, at=plain_sha) for b in ("handoff/r10-crit", "handoff/r10-other", "fix/none")] == [1, 0, 0],
               [derived(b, at=plain_sha) for b in ("handoff/r10-crit", "handoff/r10-other", "fix/none")])
         (rosters / "wave-r10-groups.json").write_text(json.dumps(roster))
+        check("is_hotfix: true for the hotfix group only; an outside, a critical and an unmapped branch are not",
+              [is_hotfix(b, repo=str(repo), ref=live, fetch=False) for b in
+               ("handoff/r10-hot", "handoff/r10-out", "handoff/r10-crit", "handoff/r10-other", "fix/none")]
+              == [True, False, False, False, False])
+        check("is_hotfix ignores the lease override and fails closed (False) on a failed fetch",
+              not is_hotfix("handoff/r10-other", repo=str(repo), ref=live, fetch=False)
+              and not is_hotfix("handoff/r10-hot", repo=str(repo), fetch=True))
         check("a group that resolves but is not listed stays normal (null control)",
               derived("handoff/r10-other") == 0, derived("handoff/r10-other"))
         check("a branch that maps to no group stays normal",
@@ -292,11 +315,16 @@ def main(argv: list[str] | None = None) -> int:
                         help="roster ref override, for fixtures (default: the live one)")
     parser.add_argument("--no-fetch", action="store_true",
                         help="read the local roster ref without refreshing it")
+    parser.add_argument("--hotfix", action="store_true",
+                        help="print 1 when the roster classes the branch's group a hotfix, else 0")
     parser.add_argument("--self-test", action="store_true")
     args = parser.parse_args(argv)
     if args.self_test:
         return _self_test()
     branch = args.branch if args.branch is not None else _current_branch(args.repo)
+    if args.hotfix:
+        print(int(is_hotfix(branch, repo=args.repo, ref=args.ref, fetch=not args.no_fetch)))
+        return 0
     print(priority_for_branch(branch, repo=args.repo, ref=args.ref,
                               fetch=not args.no_fetch))
     return 0
diff --git a/tools/pr/prepr.sh b/tools/pr/prepr.sh
index e0ffdff4..0425c710 100755
--- a/tools/pr/prepr.sh
+++ b/tools/pr/prepr.sh
@@ -1759,6 +1759,27 @@ merged_steps() { # body, unpinned-site key file -> step lines
   esac
 }
 
+# A hotfix group's branch runs the scoped prepr by default (tvofi, 2026-11-09: "hotfixes should
+# have aggressively scoped or no prepr"; the main de.json hotfix spent about 40 min in a full
+# one while 7 PRs waited). The class is the roster's, through gate_priority.py's own
+# derivation of the group's dispatch rank -- the one the gate lease already trusts -- so a
+# branch name alone never decides it, and an unreadable roster answers 0, a full run. Only an
+# UNSET variable takes the default: a caller's value, set empty included, wins per variable.
+# The scope is code and closures; the merged-tree structure ratchet, ci predict and the body
+# and contract checks (`merged_steps`, steps 1a-1a3, 6, 7) stay, as under any PREPR_SKIP_CODE.
+hotfix_class() { # branch -> 1 when the roster classes its group a hotfix, else 0
+  python3 tools/pr/gate_priority.py --hotfix --branch "$1" 2>/dev/null
+}
+hotfix_scope() { # branch -> exports the unset skips; prints one line when it scoped
+  if [ -n "${PREPR_SKIP_CODE+x}" ] && [ -n "${PREPR_SKIP_CLOSURES+x}" ]; then return 0; fi
+  [ "$(hotfix_class "$1")" = 1 ] || return 0
+  HOTFIX_SCOPED=1
+  [ -n "${PREPR_SKIP_CODE+x}" ] || PREPR_SKIP_CODE=hotfix
+  [ -n "${PREPR_SKIP_CLOSURES+x}" ] || PREPR_SKIP_CLOSURES=1
+  export PREPR_SKIP_CODE PREPR_SKIP_CLOSURES
+  say ok "hotfix scope" "$1 is a hotfix group's branch: code and closure steps skipped; merged structure, ci predict, body and contract checks run (a caller's PREPR_SKIP_CODE / PREPR_SKIP_CLOSURES, set empty included, wins)"
+}
+
 selftest_owed() { # changed-paths file -> 0 when a changed path is a self-test input
   awk 'NR==FNR { if ($0 ~ /\/$/) d[$0]=1; else f[$0]=1; next }
        ($0 in f) { hit=1; exit }
@@ -4120,6 +4141,21 @@ exit $rc'*) r=0 ;; *) r=1 ;; esac
   st "$(printf '%s\n' "$RA" | grep -cE '^  [a-zA-Z]+ +(heavy slot|policy_lint|self-test|agreement lane|gate priority) ')$(printf '%s\n' "$RA" | grep -c '^  ok  *code steps  ')" 01 "(a) a PREPR_SKIP_CODE run takes no heavy slot and drops the code-keyed steps"
   st "$(printf '%s\n' "$RA" | grep -cE '^  [a-zA-Z]+ +merged structure ')$(printf '%s\n' "$RA" | grep -cE '^  [a-zA-Z]+ +ci predict ')" 11 "(a) and runs tests/structure.py and ci predict on HEAD merged with main, once each"
   st "$([ -f "$(git -C "$RQ/wt" rev-parse --absolute-git-dir)/hpo-prepr-receipt" ] && echo left)" "" "(a) a run with a body removes an earlier receipt first, so one that writes none leaves none"
+  # Carry 21: a hotfix group's branch defaults to the scoped run, decided once from the
+  # roster's class (`hotfix_class`, gate_priority.py --hotfix), never from the branch name.
+  hs() { # classifier answer -> "<scope line>|<PREPR_SKIP_CODE>|<PREPR_SKIP_CLOSURES>", the caller's env as set
+    local cls=$1
+    ( hotfix_class() { printf '%s' "$cls"; }
+      say() { printf '%s' "$2"; }
+      hotfix_scope fix/any
+      printf '|%s|%s' "${PREPR_SKIP_CODE-unset}" "${PREPR_SKIP_CLOSURES-unset}" )
+  }
+  st "$( (unset PREPR_SKIP_CODE PREPR_SKIP_CLOSURES; hs 1) )" "hotfix scope|hotfix|1" "(hotfix) a roster-classed hotfix branch prints the scope line and defaults both skips on"
+  st "$( (unset PREPR_SKIP_CODE PREPR_SKIP_CLOSURES; hs 0) )" "|unset|unset" "(hotfix) null control: a non-hotfix branch prints nothing and sets neither skip"
+  st "$( (unset PREPR_SKIP_CLOSURES; PREPR_SKIP_CODE=; hs 1) )" "hotfix scope||1" "(hotfix) an explicit empty PREPR_SKIP_CODE (a full code run) wins; the closures default stays"
+  st "$( (unset PREPR_SKIP_CODE; PREPR_SKIP_CLOSURES=; hs 1) )" "hotfix scope|hotfix|" "(hotfix) an explicit empty PREPR_SKIP_CLOSURES wins; the code default stays"
+  st "$( (PREPR_SKIP_CODE=abc; PREPR_SKIP_CLOSURES=x; hs 1) )" "|abc|x" "(hotfix) explicit values pass through unchanged and, both set, nothing is printed"
+  st "$(awk '/^hotfix_scope "\$\(git rev-parse --abbrev-ref HEAD/{a=NR} /^REUSE=/{b=NR} END{print (a>0 && b>a) ? "ok" : "late"}' "$PREPR_PATH")" ok "(hotfix) the main flow decides the scope once, before REUSE is read from PREPR_SKIP_CODE"
   rm -rf "$RQ"
 
   printf '\n%s passed, %s failed\n' "$st_pass" "$st_fail"
@@ -4192,8 +4228,11 @@ summary_start
 # at that code sha was found and the head is its clean merge with the live head
 # and main, so the steps keyed to the code alone are dropped and no heavy slot is
 # taken; the steps keyed to main, the body or the merge still run (`merged_steps`).
+HOTFIX_SCOPED=""
+hotfix_scope "$(git rev-parse --abbrev-ref HEAD 2>/dev/null)"
 REUSE=${PREPR_SKIP_CODE:-}
-[ -z "$REUSE" ] || say ok "code steps" "reused from the receipt at ${REUSE:0:12}: no heavy slot, and the steps keyed to the code alone are dropped"
+if [ -n "$HOTFIX_SCOPED" ] && [ "$REUSE" = hotfix ]; then say ok "code steps" "hotfix scope: no heavy slot, and the steps keyed to the code alone are dropped"
+elif [ -n "$REUSE" ]; then say ok "code steps" "reused from the receipt at ${REUSE:0:12}: no heavy slot, and the steps keyed to the code alone are dropped"; fi
 
 # --- 1a. no transport file in any commit the branch adds (`transport_in_ancestry`).
 TRANSPORT=$(transport_in_ancestry "$BASE" HEAD)

## Before you return the verdict (P275)
Run `python3 -I tools/audit/carry_audit.py check --body <PR body file> --comments <file holding [{"id": 0, "body": <verdict.md text>}]>`. Give every reported item its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>`;
an evidence line flagged by its wording takes `Carry: dismissed: evidence, not a finding`. Return the verdict only at rc 0.
