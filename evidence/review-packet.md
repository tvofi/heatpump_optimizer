# Review packet #3055
head: 6a988a237f91a853d006f7908e41cfbd30bc9bc9
base: a7dd7f50d67e0c3819956b15ef95d77f4f6ebfc0

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: pending
CodeQL id=124648662537 neutral
arch-score / arch-score id=124648399978 success
arm id=124648278965 skipped
budget-raise-gate / budget-raise-gate id=124648399981 success
cancel-superseded id=124648287987 success
codeql / Analyze (actions) id=124648400176 success
codeql / Analyze (javascript-typescript) id=124648400025 success
codeql / Analyze (python) id=124648400064 in_progress
governance / delivery-status id=124648400160 success
governance / delivery-status-publish id=124648401104 skipped
governance / env-matrix id=124648400011 success
governance / instrument-self-tests id=124648400141 in_progress
governance / policy-docs id=124648400082 success
governance / record id=124648400962 skipped
governance / wave-script id=124648400088 success
hassfest / hassfest id=124648399979 success
kernel-points id=124648400960 skipped
prelude id=124648287702 success
refresh id=124648288005 success
tests / arch-instrument id=124648528983 in_progress
tests / briefs id=124648400050 success
tests / browser id=124648529114 success
tests / closure-scope id=124648400269 success
tests / closures id=124648528994 in_progress
tests / coverage id=124648529043 in_progress
tests / fast (3.14) id=124648528925 in_progress
tests / mutation id=124648400188 success
tests / mutation-autofix id=124648556322 skipped
tests / mutation-pins id=124648555589 skipped
tests / nightly-ha id=124648530336 skipped
tests / nightly-status id=124648400058 success
tests / replay id=124648529834 skipped
tests / typing id=124648528990 success
validate / validate-hacs id=124648400075 success

## Refusals
none

## Advisories
hot-file: HPO_BUS_TRAIN_STATE is unset, so every merge verdict reads unboarded

## carry_audit at the head
NOTE body item f2315161: R10-FLY-SUITE-ENV-FLAKES
CARRY-AUDIT: 1 finding item(s): 1 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
unverified git grep -nE '"\$\{[A-Za-z_]+\[@\]\}"' -- 'tools/**/*.sh'
             `git grep` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  ok         python3 -I tools/audit/seat/bare_array.py --check --ref 3759d49a5
             `tools/audit/seat/bare_array.py` is in the tree at this head
  ok         tests/entities.py
             `tests/entities.py` is in the tree at this head
  ok         python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)
             `tests/closure.py` is in the tree at this head
  ok         tests/structure.py
             `tests/structure.py` is in the tree at this head
  ok         tools/pr/prepr.sh
             `tools/pr/prepr.sh` is in the tree at this head
  ok         tools/pr/ci_predict.py
             `tools/pr/ci_predict.py` is in the tree at this head

FIGURES: 6 resolved, 1 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
none

## Three-dot diff
diff --git a/.github/workflows/governance.yml b/.github/workflows/governance.yml
index 54a9de2e1..d795c9acf 100644
--- a/.github/workflows/governance.yml
+++ b/.github/workflows/governance.yml
@@ -441,6 +441,14 @@ jobs:
           python3 -I tools/audit/seat/tmp_paths.py --self-test
           python3 -I tools/audit/seat/tmp_paths.py --check
 
+      # macOS bash 3.2 dies on an empty array's bare "${a[@]}" under `set -u`,
+      # which CI's bash 5 expands cleanly (triage P303): the static rule.
+      - name: Refuse a bare array expansion in a set -u script
+        run: |
+          set -euo pipefail
+          python3 -I tools/audit/seat/bare_array.py --self-test
+          python3 -I tools/audit/seat/bare_array.py --check
+
       # A push whose ref name or commit message names the host (#2310: 70
       # wip-sync refs carried the account name). The self-test drives the
       # slug, the guard and wt_sync.sh end to end on a planted identity; the
diff --git a/dev/programme/delivery/3055.md b/dev/programme/delivery/3055.md
new file mode 100644
index 000000000..e093fd3b5
--- /dev/null
+++ b/dev/programme/delivery/3055.md
@@ -0,0 +1 @@
+- [#3055](https://github.com/tvofi/heatpump_optimizer/pull/3055) — **open**, R10-FLY-BUS-BASH32: fly bus bash32 (R10-FLY-BUS-BASH32)
diff --git a/tests/closure.py b/tests/closure.py
index 081f0fb4a..3c477285b 100644
--- a/tests/closure.py
+++ b/tests/closure.py
@@ -753,6 +753,8 @@ INERT_EXCEPT = (
     "tools/audit/seat/merge_train.py",
     "tools/audit/seat/queue_pre_flight.py",
     "tools/audit/seat/tmp_paths.py",
+    # R10-FLY-BUS-BASH32: tests/entities.py loads it for the bare-array rule.
+    "tools/audit/seat/bare_array.py",
     # R10-FLOW-AUTOTRAIN: merge_train.py imports these two when tests/entities.py
     # loads it (proof_watch for the verdict grammar, ledger for the sweep's
     # train-stop hold). CI's recording at f3bd78c35 (closures job 121037861937)
diff --git a/tests/closures.json b/tests/closures.json
index e122fb4be..6abb315d0 100644
--- a/tests/closures.json
+++ b/tests/closures.json
@@ -1817,6 +1817,7 @@
    "tools/audit/repo_root.py",
    "tools/audit/round4/D11/d11lib.py",
    "tools/audit/round4/D11/governance_cost.py",
+   "tools/audit/seat/bare_array.py",
    "tools/audit/seat/gh_read.py",
    "tools/audit/seat/handover_prompt.py",
    "tools/audit/seat/ledger.py",
diff --git a/tests/entities.py b/tests/entities.py
index 01660f41e..0cd0fd307 100644
--- a/tests/entities.py
+++ b/tests/entities.py
@@ -28069,6 +28069,45 @@ R.check(
         "app_comment.sh"),
     "the predicate must read the step's run line, not the file name anywhere",
 )
+# --- bare array expansion under set -u (R10-FLY-BUS-BASH32, triage P303) -------
+#
+# macOS /bin/bash 3.2 rejects an EMPTY array's `"${a[@]}"` under `set -u`; CI's
+# bash 5 expands it cleanly, so no run-time row here can see the defect -- this
+# is the static rule `tools/audit/seat/bare_array.py` owns, over every tracked
+# tools/**/*.sh. It encodes a design choice: the guard `${a[@]+"${a[@]}"}` or a
+# `# never-empty: <reason>` marker is the only way out, and a file with no
+# `set -u` is not judged.
+import importlib.util as _ba_util  # noqa: E402
+
+try:
+    _ba_spec = _ba_util.spec_from_file_location(
+        "hpo_bare_array", _closure.ROOT / "tools" / "audit" / "seat" / "bare_array.py")
+    _ba = _ba_util.module_from_spec(_ba_spec)
+    _ba_spec.loader.exec_module(_ba)
+    _ba_hits = _ba.scan("HEAD")  # git show reads blobs: no file under tools/ is opened, so none joins this script's closure
+    _ba_head = "#!/bin/bash\nset -uo pipefail\n"
+    # bus.sh orphans at the base (3759d49a5): the unguarded call that died.
+    _ba_base = _ba_head + 'x | python3 -I ledger.py landed "${arms[@]}" "$main" $fix_heads\n'
+    _ba_fixed = _ba_head + 'x | python3 -I ledger.py landed ${arms[@]+"${arms[@]}"} "$main" $fix_heads\n'
+    _ba_rows = (
+        (len(_ba.sites(_ba_base)) == 1, "the base bus.sh call is refused"),
+        (_ba.sites(_ba_fixed) == [], "the guarded form passes (control)"),
+        (_ba.sites(_ba_head + 'f "${a[@]}"  # never-empty: literal list\n') == [],
+         "an allow-marked never-empty site passes (null)"),
+        (_ba.sites('set -e\nf "${a[@]}"\n') == [], "a file without set -u is not judged (null)"),
+        (_ba.self_test.__call__() == 0, "its own self-test passes"),
+    )
+except Exception as _ba_exc:  # noqa: BLE001 -- a crash is one red check, not a partial run
+    _ba_hits, _ba_rows = [f"{type(_ba_exc).__name__}: {_ba_exc}"], ()
+R.check(
+    "no tracked tools/**/*.sh script under set -u expands a bare \"${array[@]}\"",
+    not _ba_hits,
+    "bash 3.2 (macOS) dies on an empty array under -u; guard with ${a[@]+\"${a[@]}\"} or "
+    "mark the line `# never-empty: <reason>`:\n" + "\n".join(_ba_hits),
+)
+for _ba_ok, _ba_name in _ba_rows:
+    R.check("bare_array: " + _ba_name, _ba_ok, "tools/audit/seat/bare_array.py")
+
 # --- record-autofix: the record beat for rowless merges (R9-FR-10, #1952) ----
 #
 # `record` reddens on main after every rowless merge, and the beat that clears
diff --git a/tools/audit/seat/bare_array.py b/tools/audit/seat/bare_array.py
new file mode 100644
index 000000000..e838b1dcf
--- /dev/null
+++ b/tools/audit/seat/bare_array.py
@@ -0,0 +1,105 @@
+#!/usr/bin/env python3
+"""Refuse a bare `"${name[@]}"` in a tracked tools/ shell script that runs under `set -u`.
+
+    python3 -I tools/audit/seat/bare_array.py --check [--ref <commit>]
+    python3 -I tools/audit/seat/bare_array.py --self-test
+
+WHY. macOS /bin/bash 3.2 rejects the expansion of an EMPTY array under `set -u`
+(`name[@]: unbound variable`); bash 4.4+ and so CI's bash 5 expand it cleanly.
+A run-time test on CI therefore passes on the defect, and the rule that
+`bus.sh`, `body_push.sh` and `seat_venv.sh` each state in prose did not stop
+`bus.sh orphans` (`"${arms[@]}"`, R10-FLY-ORPHANS-REWRITTEN) from dying on the
+operator's machine (triage P303). This is the static half.
+
+THE RULE, per file: a file with a `set` command carrying the `u` option is
+judged; a file without one is not. In a judged file, each non-comment line is
+refused for every `"${name[@]}"` that is not the guarded form
+`${name[@]+"${name[@]}"}`, unless the line carries
+`# never-empty: <reason>` with a reason, stating why the array cannot be empty
+there. `"${name[*]}"`, `${#name[@]}` and `"${name[@]:...}"` are not matched.
+The `set -u` test is textual and file-wide: a `set +u` window is not modelled,
+so a site inside one takes the marker too.
+"""
+from __future__ import annotations
+
+import re
+import subprocess
+import sys
+from pathlib import Path
+
+SET_U = re.compile(r"^\s*set\s+(?:-[A-Za-z]*u[A-Za-z]*|-o\s+nounset)\b", re.M)
+BARE = re.compile(r'"\$\{([A-Za-z_]\w*)\[@\]\}"')
+MARK = re.compile(r"#\s*never-empty:\s*\S")
+
+
+def sites(text: str) -> list[tuple[int, str]]:
+    """(line number, line) of each refused expansion in one script's text."""
+    if not SET_U.search(text):
+        return []
+    out = []
+    for n, line in enumerate(text.splitlines(), 1):
+        if line.lstrip().startswith("#") or MARK.search(line):
+            continue
+        for m in BARE.finditer(line):
+            if not line[: m.start()].endswith("${%s[@]+" % m.group(1)):
+                out.append((n, line.strip()))
+                break
+    return out
+
+
+def scan(ref: str | None = None) -> list[str]:
+    """`path:line: text` per refused site across tracked tools/**/*.sh."""
+    root = subprocess.check_output(["git", "rev-parse", "--show-toplevel"], text=True).strip()
+    if ref:
+        names = subprocess.check_output(
+            ["git", "ls-tree", "-r", "--name-only", ref, "--", "tools"], text=True, cwd=root).split()
+    else:
+        names = subprocess.check_output(
+            ["git", "ls-files", "--", "tools"], text=True, cwd=root).split()
+    out = []
+    for p in sorted(n for n in names if n.endswith(".sh")):
+        if ref:
+            text = subprocess.check_output(["git", "show", f"{ref}:{p}"], text=True, cwd=root)
+        else:
+            text = (Path(root) / p).read_text()
+        out += [f"{p}:{n}: {t}" for n, t in sites(text)]
+    return out
+
+
+def self_test() -> int:
+    fails = []
+
+    def st(got, want, name):
+        if got != want:
+            fails.append(f"{name}: got {got!r}, want {want!r}")
+
+    head = "#!/bin/bash\nset -uo pipefail\n"
+    bare = head + 'f "${arms[@]}" x\n'
+    st(len(sites(bare)), 1, "a bare expansion under set -u is refused")
+    st(sites(head + 'f ${arms[@]+"${arms[@]}"} x\n'), [], "the guarded form passes")
+    st(sites(head + 'f "${a[@]}" # never-empty: argv of this script, checked above\n'), [],
+       "an allow-marked never-empty site passes (null)")
+    st(len(sites(head + 'f "${a[@]}" # never-empty:\n')), 1, "a marker with no reason does not excuse")
+    st(sites('#!/bin/bash\nset -e\nf "${a[@]}"\n'), [], "a file without set -u is not judged (null)")
+    st(len(sites('set -euo pipefail\nf "${a[@]}"\n')), 1, "set -euo counts as set -u")
+    st(sites(head + '# f "${a[@]}"\n'), [], "a comment line is skipped")
+    st(len(sites(head + 'f ${b[@]+"${b[@]}"} "${a[@]}"\n')), 1,
+       "a guard on one array does not excuse another on the line")
+    st(len(sites(head + 'f ${b[@]+"${a[@]}"}\n')), 1, "a guard names its own array")
+    st(sites(head + 'n=${#a[@]}; f "${a[*]}"\n'), [], "length and star forms are not matched")
+    for f in fails:
+        print("FAIL", f)
+    print("bare_array self-test:", "FAILED" if fails else "ok")
+    return 1 if fails else 0
+
+
+if __name__ == "__main__":
+    if "--self-test" in sys.argv:
+        sys.exit(self_test())
+    if "--check" in sys.argv:
+        ref = sys.argv[sys.argv.index("--ref") + 1] if "--ref" in sys.argv else None
+        hits = scan(ref)
+        print("\n".join(hits))
+        sys.exit(1 if hits else 0)
+    print(__doc__)
+    sys.exit(2)
diff --git a/tools/audit/seat/body_patch.sh b/tools/audit/seat/body_patch.sh
index 33617a480..25ffc5b19 100644
--- a/tools/audit/seat/body_patch.sh
+++ b/tools/audit/seat/body_patch.sh
@@ -95,7 +95,7 @@ contract() { # pr-json base head body -> rc
   local args=(--pr-body "$body" --head "$head" --base "$base" --title "$title" --author "$author"
               --paths-file "$d/files" --existing-file "$d/existing") name rc=0
   while IFS= read -r name; do args+=(--red "$name"); done < "$d/reds"
-  node tools/policy/policy_lint.mjs "${args[@]}" || rc=1 # mut:contract
+  node tools/policy/policy_lint.mjs "${args[@]}" || rc=1 # mut:contract  # never-empty: args starts with the literal --pr-body list
   python3 -I tools/audit/carry_audit.py check --body "$body" || rc=1 # mut:carry
   rm -rf "$d"
   return "$rc"
diff --git a/tools/audit/seat/bus.sh b/tools/audit/seat/bus.sh
index 3338eaffb..df29abe03 100755
--- a/tools/audit/seat/bus.sh
+++ b/tools/audit/seat/bus.sh
@@ -651,7 +651,7 @@ orphans() { # [--min-age-h N] [--no-body] [--no-ancestry] [--no-content] [--excl
   [ "$no_ancestry" = 1 ] && arms+=(--no-ancestry)
   [ "$no_content" = 1 ] && arms+=(--no-content)
   landed_nl=$LF"$(git for-each-ref --format='%(objectname)' "$ns/handoff/" \
-    | python3 -I "$ROOT/tools/audit/seat/ledger.py" landed "${arms[@]}" "$main" $fix_heads)"$LF \
+    | python3 -I "$ROOT/tools/audit/seat/ledger.py" landed ${arms[@]+"${arms[@]}"} "$main" $fix_heads)"$LF \
     || die "orphans: ledger.py landed could not classify the handoff tips"
   now=$(date +%s)
   # A while-read over a heredoc, not a pipe: the counters survive the loop.
diff --git a/tools/audit/seat/cloud-setup.sh b/tools/audit/seat/cloud-setup.sh
index bdc0a4378..1484c2152 100644
--- a/tools/audit/seat/cloud-setup.sh
+++ b/tools/audit/seat/cloud-setup.sh
@@ -61,7 +61,7 @@ EOF
 variables() { # prefix: the environment variables a seat's shell needs
   local d rest="" parts
   IFS=: read -ra parts <<< "$PATH"
-  for d in "${parts[@]}"; do [ "$d" = "$1/venv-ci/bin" ] || rest="${rest:+$rest:}$d"; done
+  for d in ${parts[@]+"${parts[@]}"}; do [ "$d" = "$1/venv-ci/bin" ] || rest="${rest:+$rest:}$d"; done
   printf '%s\n' "PATH=$1/venv-ci/bin:$rest" \
     "HPO_TYPING_PYTHON=$1/venv-ha/bin/python" "OPENBLAS_CORETYPE=$CORETYPE"
 }
@@ -100,9 +100,9 @@ self_test() (
   mapfile -t vars < <(PATH="$base" variables "$P")
   out=$(PATH="$P/venv-ci/bin:$base:$P/venv-ci/bin" variables "$P" | head -n 1)
   [ "$out" = "${vars[0]}" ]; expect "the printed PATH holds venv-ci/bin once, first, from a PATH holding it twice" $?
-  out=$(run "${vars[@]}" bash -c python3)
+  out=$(run "${vars[@]}" bash -c python3)  # never-empty: vars is the three-line output of variables, asserted above
   [ "$out" = venv ]; expect "a non-login bash under the printed variables gets venv-ci's python3" $?
-  run "${vars[@]}" bash -c "$fns; check \"\$1\"" _ "$P" >/dev/null
+  run "${vars[@]}" bash -c "$fns; check \"\$1\"" _ "$P" >/dev/null  # never-empty: vars is the three-line output of variables, asserted above
   expect "check is OK under the printed variables" $?
   out=$(run bash -c "$fns; check \"\$1\"" _ "$P"); rc=$?
   [ "$rc" = 1 ] && case $out in *"REFUSE"*"PATH=$P/venv-ci/bin:$base HPO_TYPING_PYTHON=$P/venv-ha/bin/python OPENBLAS_CORETYPE=$CORETYPE"*) true ;; *) false ;; esac
@@ -116,7 +116,7 @@ self_test() (
   [ $? = 1 ]; expect "check refuses without OPENBLAS_CORETYPE" $?
   run bash -c ". \"\$2\"; $fns; check \"\$1\"" _ "$P" "$W/profile.sh" >/dev/null
   expect "check is OK in a shell that sourced the profile" $?
-  out=$(run "${vars[@]}" HPO_PREFIX="$P" bash "$SELF" --check); rc=$?
+  out=$(run "${vars[@]}" HPO_PREFIX="$P" bash "$SELF" --check); rc=$?  # never-empty: vars is the three-line output of variables, asserted above
   [ "$rc" = 0 ] && case $out in *" OK "*) true ;; *) false ;; esac
   expect "cloud-setup.sh --check exits 0 under the printed variables" $?
   out=$(run HPO_PREFIX="$P" bash "$SELF" --check); rc=$?
diff --git a/tools/audit/seat/cloud_relay.sh b/tools/audit/seat/cloud_relay.sh
index 12dd735b8..7fbf30416 100644
--- a/tools/audit/seat/cloud_relay.sh
+++ b/tools/audit/seat/cloud_relay.sh
@@ -448,7 +448,7 @@ handoff_arm() { # one pass over open PRs; updates one whose handoff is ahead of
     # One launch for both routes, so the self-test's stub runs the production launch line.
     urc=0; upd=(bash "$HERE/update_pr.sh"); [ -z "${HPO_RELAY_UPDATE:-}" ] || upd=("$HPO_RELAY_UPDATE")
     # Its output is kept until it ends, so a failure records its reason: the last REFUSE line, else the last line.
-    pr_own_group "${upd[@]}" "$br" "$hs" "$body" $iss > "$bd/update.out" 2>&1 &
+    pr_own_group "${upd[@]}" "$br" "$hs" "$body" $iss > "$bd/update.out" 2>&1 &  # never-empty: upd is assigned the bash update_pr.sh command on the line above
     PR_REAP_LEAD=$!; wait "$PR_REAP_LEAD" || urc=$?
     cat "$bd/update.out" >&2
     # 75 is update_pr.sh's BUSY: another run (the orchestrator's) holds this branch's worktree. Not
diff --git a/tools/audit/seat/pr_args.sh b/tools/audit/seat/pr_args.sh
index 5a3050123..eabff259f 100644
--- a/tools/audit/seat/pr_args.sh
+++ b/tools/audit/seat/pr_args.sh
@@ -170,7 +170,7 @@ pr_tools_fresh() { # after `git fetch origin main`: refuse when this file's chec
   local d n h o why
   d=$(cd "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
   h=$(git -C "$d" rev-parse --short=12 HEAD 2>/dev/null) && o=$(git -C "$d" rev-parse --short=12 origin/main 2>/dev/null) \
-    && n=$(git -C "$d" rev-list --count HEAD..origin/main -- "${PR_FRESH_PATHS[@]}" 2>/dev/null) \
+    && n=$(git -C "$d" rev-list --count HEAD..origin/main -- ${PR_FRESH_PATHS[@]+"${PR_FRESH_PATHS[@]}"} 2>/dev/null) \
     || pr_refuse "could not count what origin/main adds over the checkout holding $d"
   [ "$n" != 0 ] || return 0
   why="STALE CHECKOUT $h behind origin/main $o by $n commit(s) touching tools/audit/seat tools/pr"
@@ -237,16 +237,16 @@ pr_reap() { # TERM every descendant of this shell, then KILL whatever outlives a
   pr_descendants $$
   [ "${#PR_REAP_PIDS[@]}" -gt 0 ] || return 0
   pr_lead_stop  # mut:lead
-  for p in "${PR_REAP_PIDS[@]}"; do pr_kill TERM "$p"; done
+  for p in "${PR_REAP_PIDS[@]}"; do pr_kill TERM "$p"; done  # never-empty: the line above returns when PR_REAP_PIDS is empty
   while [ "$n" -lt "${PR_REAP_TENTHS:-20}" ]; do
     alive=()
-    for p in "${PR_REAP_PIDS[@]}"; do kill -0 "$p" 2>/dev/null && alive[${#alive[@]}]=$p; done
+    for p in "${PR_REAP_PIDS[@]}"; do kill -0 "$p" 2>/dev/null && alive[${#alive[@]}]=$p; done  # never-empty: the loop head returns unless PR_REAP_PIDS holds a pid
     [ "${#alive[@]}" -gt 0 ] || return 0
-    PR_REAP_PIDS=("${alive[@]}")
+    PR_REAP_PIDS=("${alive[@]}")  # never-empty: the line above returns when alive is empty
     sleep 0.1
     n=$((n + 1))
   done
-  for p in "${PR_REAP_PIDS[@]}"; do pr_kill KILL "$p"; done  # mut:grace
+  for p in "${PR_REAP_PIDS[@]}"; do pr_kill KILL "$p"; done  # mut:grace  # never-empty: PR_REAP_PIDS held a pid at the early return and only shrinks to a non-empty alive
   return 0
 }
 pr_exit_trap() { # [<command>]: on every exit, a stop signal's included, run <command>, reap the tree, run PR_TIDY, then PR_AFTER_REAP
diff --git a/tools/pr/app_approve.sh b/tools/pr/app_approve.sh
index 43a4167e3..d04b17c7b 100755
--- a/tools/pr/app_approve.sh
+++ b/tools/pr/app_approve.sh
@@ -387,7 +387,7 @@ carry() {
   mv=$(git merge-base "$main" "$v") && mh=$(git merge-base "$main" "$h") || { echo "no merge base with $main"; return 1; }
   local d=(git -c core.quotepath=off diff --binary --no-renames --no-color --no-ext-diff --no-textconv
     --diff-algorithm=myers -U3)
-  norm() { "${d[@]}" "$1" "$2" -- . ${x[@]+"${x[@]}"} | sed -e '/^index /d' -e 's/^@@ .*/@@/'; }
+  norm() { "${d[@]}" "$1" "$2" -- . ${x[@]+"${x[@]}"} | sed -e '/^index /d' -e 's/^@@ .*/@@/'; }  # never-empty: d is the literal git diff command
   cmp -s <(norm "$mv" "$v") <(norm "$mh" "$h") \
     || { echo "the branch's own diff differs: $mv..$v against $mh..$h"; return 1; }
   echo "no branch-authored commit in the range, every merge the automatic one with its claim files a pure union of both sides or main's driver output on them, and the branch's own diff compares equal"
diff --git a/tools/pr/prepr.sh b/tools/pr/prepr.sh
index acca5adc0..bef833991 100755
--- a/tools/pr/prepr.sh
+++ b/tools/pr/prepr.sh
@@ -866,7 +866,7 @@ body_check() { # body file, head sha, title, paths file, red names...
   # refused here (policy_lint's raise arm reads the diff with the gate's own
   # raises_between), and at body_push.sh's --body-check, not first at the train.
   [ -n "${BASE:-}" ] && args+=(--base "$BASE")
-  if test -f .claude/workflows/policy_lint.mjs; then node .claude/workflows/policy_lint.mjs "${args[@]}"; else node tools/policy/policy_lint.mjs "${args[@]}"; fi
+  if test -f .claude/workflows/policy_lint.mjs; then node .claude/workflows/policy_lint.mjs "${args[@]}"; else node tools/policy/policy_lint.mjs "${args[@]}"; fi  # never-empty: args starts with the literal --pr-body list
   rc=$?
   rm -f "$ex"
   return "$rc"
@@ -1343,7 +1343,7 @@ reds_line() { # body file, head sha, title, paths file, remote head ref
   fi
   while IFS= read -r n; do [ -n "$n" ] && reds+=("$n"); done <<<"$names"
   out=$(mktemp)
-  body_check "$1" "$2" "$3" "$4" "${reds[@]}" >"$out" 2>&1; r=$?
+  body_check "$1" "$2" "$3" "$4" ${reds[@]+"${reds[@]}"} >"$out" 2>&1; r=$?
   if [ "$r" -eq 0 ]; then
     printf '%sthe body answers every red this branch pushed (%s)' "$unread" "$(echo $names)"
   else
@@ -1498,7 +1498,7 @@ TRANSPORT_ROOTS=(tools/audit/handoff/ handoff/)
 transport_in_ancestry() { # merge base, head -> 0 clean, 1 found (prints `<sha> <path>`), 2 unreadable
   local out
   out=$(git log --full-history -c --diff-filter=ACMRT --name-only \
-        --format='@%h' "$1..$2" -- "${TRANSPORT_ROOTS[@]}" 2>/dev/null) || return 2
+        --format='@%h' "$1..$2" -- "${TRANSPORT_ROOTS[@]}" 2>/dev/null) || return 2  # never-empty: TRANSPORT_ROOTS is a literal two-path list
   out=$(printf '%s\n' "$out" | awk '/^@/{c=substr($0,2);next} NF{print c" "$0}')
   [ -z "$out" ] && return 0
   printf '%s\n' "$out"
@@ -3241,7 +3241,7 @@ STUB
   tmp_floor_check /no/such/dir 1 >/dev/null; st $? 0 "an unmeasurable temp dir runs anyway, never refuses"
   # (4) The class, over every script whose sites were drained (above
   # `pipe_grep_q_sites`), and a planted site the search must find.
-  out=$(pipe_grep_q_sites "${PIPE_GREP_Q_FILES[@]}"); r=$?
+  out=$(pipe_grep_q_sites "${PIPE_GREP_Q_FILES[@]}"); r=$?  # never-empty: PIPE_GREP_Q_FILES is a literal list
   st "$r" 0 "no early-exit grep reads a pipe under pipefail in the drained scripts"
   [ "$r" -eq 0 ] || printf '%s\n' "$out" | sed 's/^/       | /' | head -8
   printf '#!/bin/bash\nset -uo pipefail\nprintf x | grep %s y\n' "-q" > "$ST_ROOT/planted.sh"

