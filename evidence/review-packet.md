# Review packet #3427
head: ad9ce7f526b47202bb3ca5e10050b7b48262fc19
base: 63bcdcaad827ad3d98f914bc2e5b6110f9bb9444

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: red
CodeQL id=130322269247 success
arch-score / arch-score id=130322212913 success
arm id=130321975503 skipped
budget-raise-gate / budget-raise-gate id=130322213142 success
cancel-superseded id=130321976842 success
codeql id=130322192042 skipped
codeql / Analyze (actions) id=130322213240 success
codeql / Analyze (javascript-typescript) id=130322213187 success
codeql / Analyze (python) id=130322213531 success
gate id=130322588976 failure
governance id=130322192658 skipped
governance / delivery-status id=130322212969 success
governance / delivery-status-publish id=130322215424 skipped
governance / env-matrix id=130322213108 success
governance / instrument-self-tests id=130322212952 in_progress
governance / policy-docs id=130322213021 success
governance / record id=130322215274 skipped
governance / wave-script id=130322212940 success
hassfest id=130322192885 skipped
hassfest / hassfest id=130322213096 success
kernel-points id=130322215204 skipped
pr-contract id=130322591074 skipped
prelude id=130321976834 success
refresh id=130321976571 success
sweep-self id=130322835929 skipped
tests id=130322192334 skipped
tests / arch-instrument id=130322439547 in_progress
tests / briefs id=130322213170 success
tests / browser id=130322439504 success
tests / closure-scope id=130322213124 success
tests / closures id=130322439572 in_progress
tests / coverage id=130322439552 in_progress
tests / fast (3.14) id=130322439519 in_progress
tests / mutation id=130322213131 success
tests / mutation-autofix id=130322544767 skipped
tests / mutation-pins id=130322544116 skipped
tests / nightly-ha id=130322441562 skipped
tests / nightly-status id=130322213208 success
tests / replay id=130322441046 skipped
tests / typing id=130322439538 success
validate id=130322191899 skipped
validate / validate-hacs id=130322213097 success

## Refusals
red-unanswered: concluded red check `gate` is not named in ## Red checks

## Advisories
required-wait: required context `gate` reads concluded failure at ad9ce7f526b47202bb3ca5e10050b7b48262fc19 in the digest, but merge_train.py classify --pr reads WAIT (pending: gate red: none): classify decides, as bus.sh's dispatch does, and a pending check never refuses

## carry_audit at the head
NOTE body item c6e0f756: dismissed:the group's next part owns them, and the brief scopes this part to Carries 1-4
NOTE body item ca30358e: dismissed:no tracked caller exists to change and the seat's launch environment is not in the tree; the next daemon-PATH audit reads the install, not this guard
NOTE body item 251a1e4a: dismissed:the choice is recorded in the shim comment at the admit block and pinned by the t3 null control, so the owner's reversal is one arm
CARRY-AUDIT: 3 finding item(s): 3 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
ok         bash tools/pr/app_push.sh --self-test
             `tools/pr/app_push.sh` is in the tree at this head
  ok         python3 -I tools/ci/codescan_wait.py --self-test
             `tools/ci/codescan_wait.py` is in the tree at this head
  ok         python3 -I tools/audit/seat/gh_calls.py --self-test
             `tools/audit/seat/gh_calls.py` is in the tree at this head
  ok         bash tools/audit/seat/seat_venv.sh --self-test
             `tools/audit/seat/seat_venv.sh` is in the tree at this head
  ok         PYTHONPATH=tests/hastub python3 -I tests/ci_ratchet.py --self-test
             `tests/ci_ratchet.py` is in the tree at this head
  ok         python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)
             `tests/closure.py` is in the tree at this head

FIGURES: 6 resolved, 0 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
none

## Three-dot diff
diff --git a/dev/programme/delivery/3427.md b/dev/programme/delivery/3427.md
new file mode 100644
index 0000000000..e79b456bec
--- /dev/null
+++ b/dev/programme/delivery/3427.md
@@ -0,0 +1 @@
+- [#3427](https://github.com/tvofi/heatpump_optimizer/pull/3427) — **open**, R10-GH-READ-RESIDUE: r10 gh read residue (R10-GH-READ-RESIDUE)
diff --git a/tests/ci_ratchet.py b/tests/ci_ratchet.py
index 14c90c71a7..3ef2e63032 100644
--- a/tests/ci_ratchet.py
+++ b/tests/ci_ratchet.py
@@ -649,21 +649,29 @@ def run_chain(r: dict) -> "list[str] | None":
     return chain[::-1]
 
 
-def gather_runs(out_file, *, repo=None, runner=None, window: int = PUSH_WINDOW) -> int:
+def gather_runs(out_file, *, repo=None, runner=None, window: int = PUSH_WINDOW, sleep=None) -> int:
     """The ci-ratchet job's runs.json: the newest `window` (PUSH_WINDOW when
     grading) push runs of ci.yml and the pre-umbrella tests.yml together, each
     with its jobs. Any failed read refuses by name: a short window is not a
-    fast one."""
+    fast one. Every read rides tools/audit/seat/gh_read.py's read rule (4 reads,
+    transient statuses only): main went red twice in a day (2026-11-10, -11) on
+    one HTTP 502 here, the grading step never having run."""
+    sys.path.insert(0, str(ROOT / "tools" / "audit" / "seat"))
+    import gh_read  # noqa: E402 -- the one read rule
     repo = repo or os.environ.get("GITHUB_REPOSITORY")
     if not repo:
         raise _refusal("--gather-runs needs GITHUB_REPOSITORY")
     run = runner or subprocess.run
 
     def api(*argv):
-        proc = run(["gh", "api", *argv], capture_output=True, text=True)
-        if proc.returncode != 0 or not (proc.stdout or "").strip():
-            raise _refusal(f"gh api {argv[-1]} failed (rc {proc.returncode}): "
-                           f"{(proc.stderr or '').strip()[:300]}")
+        def attempt():
+            proc = run(["gh", "api", *argv], capture_output=True, text=True)
+            if proc.returncode != 0 or not (proc.stdout or "").strip():
+                return proc, (proc.stderr or "").strip() or "gh printed nothing"
+            return proc, None
+        proc, failure, _n, why = gh_read.retry(attempt, gh_read.gh_wait, sleep or time.sleep)
+        if failure is not None:
+            raise _refusal(f"gh api {argv[-1]} failed (rc {proc.returncode}) {why}: {failure[:300]}")
         return proc.stdout
     runs = []
     for wf in PUSH_RUNS:
@@ -1156,10 +1164,34 @@ def self_test() -> int:
         ck("--gather-runs --window N keeps the newest N (a record's wider window)",
            n == 3 and sum("/jobs?" in a[-1] for a in reads) == 3
            and all("per_page=3" in a[-1] for a in reads if "/jobs?" not in a[-1]), msg or f"n={n}")
-        msg = refused(lambda: gather_runs(f, repo="o/r", runner=lambda argv, **_kw: subprocess.CompletedProcess(
+        naps = []
+        msg = refused(lambda: gather_runs(f, repo="o/r", sleep=naps.append, runner=lambda argv, **_kw: subprocess.CompletedProcess(
             argv, 1, "", "gh: HTTP 502")))
-        ck("a failed runs read refuses by name (a short window is not a fast one)",
-           "failed (rc 1)" in msg and "HTTP 502" in msg, msg or "no refusal")
+        ck("a sustained 502 on the runs read refuses by name after the read rule's 4 reads (a short window is not a fast one)",
+           "failed (rc 1)" in msg and "HTTP 502" in msg and len(naps) == 3, msg or "no refusal")
+        # R10-GH-READ-RESIDUE: one 502 on the jobs listing of one run (main red 2026-11-10, -11) is ridden out.
+        reads.clear()
+        flaky = []
+
+        def gh_502_once(argv, **kw):
+            if "/jobs?" in argv[-1] and not flaky:
+                flaky.append(argv)
+                return subprocess.CompletedProcess(argv, 1, "", "gh: HTTP 502")
+            return gh(argv, **kw)
+        n, msg = safe(lambda: gather_runs(f, repo="o/r", runner=gh_502_once, sleep=lambda _s: None))
+        ck("one injected 502 on a jobs listing still gathers the whole window",
+           n == 16 and len(flaky) == 1 and all("jobs" in r for r in json.loads(f.read_text())["workflow_runs"]
+                                               if run_kind(r) is not None), msg or f"n={n}")
+        reads.clear()
+        gone = []
+        naps.clear()
+
+        def gh_404(argv, **_kw):
+            gone.append(argv)
+            return subprocess.CompletedProcess(argv, 1, "", "gh: Not Found (HTTP 404)")
+        msg = refused(lambda: gather_runs(f, repo="o/r", runner=gh_404, sleep=naps.append))
+        ck("null control: a 404 refuses after one read, no sleep",
+           len(gone) == 1 and not naps and "HTTP 404" in msg, msg or "no refusal")
 
     # --- runner queue is not work (main red, CI job 121295715608) ----------
     # Run 40225415246, its timeline as the jobs API gave it (minutes from the
diff --git a/tools/audit/seat/gh_calls.py b/tools/audit/seat/gh_calls.py
index 0f5ed462d6..64ac22d046 100644
--- a/tools/audit/seat/gh_calls.py
+++ b/tools/audit/seat/gh_calls.py
@@ -171,7 +171,7 @@ def self_test():
         # a real gh (the CI runner does; a Mac does not).
         tools = w / "tools"
         tools.mkdir()
-        for tool in ("ps", "tr", "cut", "wc", "mv", "date", "cat", "sh", "sed", "mkdir", "env", "python3", "chmod"):
+        for tool in ("ps", "tr", "cut", "wc", "mv", "date", "cat", "sh", "sed", "mkdir", "env", "python3", "chmod", "git"):
             found = shutil.which(tool)
             if found:
                 (tools / tool).symlink_to(found)
@@ -575,6 +575,39 @@ def self_test():
             ("gh extension exec", ["extension", "exec", "x"]))
         for label, args in refused:
             check(f"{label} is refused", run(args).returncode == 1)
+        # R10-GH-READ-RESIDUE (P449): one install on the daemons' PATH, run from any checkout. The
+        # baked tree t1, a worktree t2 of it, a clone t3 git does not register beside it, and an
+        # untracked file t4 of the same name.
+        sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "tests"))
+        from throwaway_git import throwaway_git_clone, throwaway_git_init  # noqa: E402 -- the one throwaway-repo builder
+        t1 = w / "t1"
+        (t1 / "tools" / "pr").mkdir(parents=True)
+        (t1 / "tools" / "pr" / "gh_comment.py").write_text(gcs.read_text())
+        genv = throwaway_git_init(t1, "-q")
+        for argv in (["add", "."], ["commit", "-qm", "x"], ["worktree", "add", "-q", str(w / "t2")]):
+            subprocess.run(["git", *argv], cwd=t1, env=genv, check=True)
+        # t5: a registered worktree whose gh_comment.py git does not track (the tracked half of the rule)
+        subprocess.run(["git", "worktree", "add", "-q", str(w / "t5")], cwd=t1, env=genv, check=True)
+        subprocess.run(["git", "rm", "-q", "--cached", "tools/pr/gh_comment.py"], cwd=w / "t5", env=genv, check=True)
+        throwaway_git_clone(t1, w / "t3", "-q")
+        (w / "t4" / "tools" / "pr").mkdir(parents=True)
+        (w / "t4" / "tools" / "pr" / "gh_comment.py").write_text(gcs.read_text())
+        baked = good.replace("gcpy=@HPO_GH_COMMENT@\n", f"gcpy={t1}/tools/pr/gh_comment.py\n")
+        for label, tree, want_rc in (
+                ("the baked tree's own script", "t1", 7),
+                ("a second registered worktree's tracked script", "t2", 7),
+                ("null control: a clone git does not list beside the baked tree", "t3", 1),
+                ("null control: an untracked file of the same path and name", "t4", 1),
+                ("null control: a registered worktree whose script is not tracked", "t5", 1)):
+            check(f"second tree: {label}",
+                  run([], via=f"{py} -I {w / tree}/tools/pr/gh_comment.py {W}", shim_text=baked).returncode == want_rc)
+        guard_mut = baked.replace('[ "$wl" = "worktree $troot" ] && ok=1', 'ok=1')
+        check("mutant: the worktree registration dropped lets an unlisted clone through",
+              guard_mut != baked and run([], via=f"{py} -I {w / 't3'}/tools/pr/gh_comment.py {W}", shim_text=guard_mut).returncode == 7)
+        tr_mut = baked.replace(" && git -C \"$troot\" ls-files --error-unmatch tools/pr/gh_comment.py >/dev/null 2>&1", "")
+        check("mutant: the tracked-file predicate dropped lets an untracked script in a registered worktree through",
+              tr_mut != baked and run([], via=f"{py} -I {w / 't5'}/tools/pr/gh_comment.py {W}", shim_text=tr_mut).returncode == 7)
+        install(good)
         mut = good.replace("trackers='201 ", "trackers='0 ")
         check("mutant: the guard's issue number changed lets the planted post through",
               mut != good and run(planted, shim_text=mut).returncode == 7)
diff --git a/tools/audit/seat/shims/seat-gh b/tools/audit/seat/shims/seat-gh
index 15d7b0c8f4..75060fd9ad 100755
--- a/tools/audit/seat/shims/seat-gh
+++ b/tools/audit/seat/shims/seat-gh
@@ -336,6 +336,20 @@ if [ -n "${hit:-}" ]; then
     done
     if [ -n "$script" ] && [ -n "$gcpy" ]; then
       a=$(rp "$script") && b=$(rp "$gcpy") && [ "$a" = "$b" ] && ok=1
+      # Another tree's gh_comment.py (R10-GH-READ-RESIDUE, P449): the daemons' PATH carries one
+      # install, run from any checkout. Admitted by real path when it is the tracked
+      # tools/pr/gh_comment.py of a worktree git registers beside the baked tree's; a file
+      # merely so named, in a directory git does not list, stays refused.
+      if [ -z "$ok" ] && [ -n "$a" ]; then
+        case $a in */tools/pr/gh_comment.py)
+          troot=${a%/tools/pr/gh_comment.py} broot=${gcpy%/tools/pr/gh_comment.py}
+          if [ "$broot" != "$gcpy" ] && git -C "$troot" ls-files --error-unmatch tools/pr/gh_comment.py >/dev/null 2>&1; then
+            while IFS= read -r wl; do
+              [ "$wl" = "worktree $troot" ] && ok=1
+            done < <(git -C "$broot" worktree list --porcelain 2>/dev/null)
+          fi ;;
+        esac
+      fi
     fi ;;
   esac
   [ -n "$ok" ] || { echo "gh shim: a comment write on a record issue (#${trackers// /, #}) goes through tools/pr/gh_comment.py (its mandate guard refuses a post that voids a mandate); refused" >&2; exit 1; }
diff --git a/tools/ci/codescan_wait.py b/tools/ci/codescan_wait.py
index 41e9f016ab..95d80cf675 100644
--- a/tools/ci/codescan_wait.py
+++ b/tools/ci/codescan_wait.py
@@ -95,6 +95,20 @@ def source(get, repo, run_id, pr, base, stop, sleep=time.sleep, now=time.monoton
         sleep(POLL_S)
 
 
+def carried_over(j):
+    """A job a partial re-run lists from the earlier attempt: completed `success` and no `steps` key at all.
+    Its analysis ran and uploaded then, and the listing no longer carries the step row; an empty or
+    lagging `steps` list is not this (the row is there, or the leg is mid-write)."""
+    return j.get("status") == "completed" and j.get("conclusion") == "success" and "steps" not in j
+
+
+def analysis(j):
+    """The conclusion of a job's analysis step: its row's, `success` for a carried-over job, else None."""
+    if carried_over(j):
+        return "success"
+    return next((s.get("conclusion") for s in j.get("steps") or [] if s["name"] == STEP), None)
+
+
 def settled(jobs):
     """Every codeql job listed completed, and each either skipped outright or with its analysis step concluded:
     a leg whose step row lags reads as stood down in `legs_uploaded`, and goes unread."""
@@ -105,7 +119,7 @@ def settled(jobs):
             return False
         if j.get("conclusion") in ("skipped", "cancelled"):
             continue
-        if not any(s["name"] == STEP and s.get("conclusion") for s in j.get("steps") or []):
+        if not analysis(j):
             return False
     return True
 
@@ -115,7 +129,7 @@ def legs_uploaded(jobs):
     out = []
     for j in jobs:
         name = j["name"]
-        if name in CODEQL and any(s["name"] == STEP and s["conclusion"] == "success" for s in j.get("steps") or []):
+        if name in CODEQL and analysis(j) == "success":
             out.append(name[name.index("(") + 1:-1])
     return sorted(out)
 
@@ -321,6 +335,20 @@ def self_test() -> int:
     reads.clear()
     check("20 null: a settled stand-down (step skipped) is not waited for",
           go(world(A.THREE[1:], A.EMPTY, [], run_jobs={100: jobs(skip=("python",))})) == [])
+    # 21-24: a partial re-run lists the carried-over jobs without `steps` (R10-GH-READ-RESIDUE, d678abfc)
+    bare = [{"name": nm, "status": "completed", "conclusion": "success"} for nm in CODEQL]
+    check("21 carried-over step-less success jobs are settled and all legs uploaded",
+          settled(bare) and legs_uploaded(bare) == legs_uploaded(jobs()) != [])
+    check("22 null: a step-less job that did not succeed is neither settled nor an uploaded leg",
+          not settled([dict(j, conclusion="failure") for j in bare]) and legs_uploaded([dict(j, conclusion="failure") for j in bare]) == [])
+    check("23 null: a lagging step row (steps present, no conclusion) is still unsettled",
+          not settled(lag()) and legs_uploaded(lag()) == [])
+    done_lag = lambda st: [{"name": nm, "status": "completed", "conclusion": "success", "steps": st} for nm in CODEQL]   # noqa: E731
+    check("23b null: a completed success job with a lagging or empty `steps` list is not carried over: unsettled, not uploaded",
+          all(not settled(done_lag(st)) and legs_uploaded(done_lag(st)) == []
+              for st in ([], [{"name": STEP, "conclusion": None}])))
+    check("24 null: a step-less job still in progress is unsettled",
+          not settled([dict(j, status="in_progress") for j in bare]))
     print(f"codescan_wait self-test: {n} checks, {bad} failed")
     return 1 if bad else 0
 
diff --git a/tools/pr/app_push.sh b/tools/pr/app_push.sh
index b499d50aec..58b8b402bf 100644
--- a/tools/pr/app_push.sh
+++ b/tools/pr/app_push.sh
@@ -615,7 +615,10 @@ HELPER
   # (#1267) -- 64 MiB keeps such a push in one Content-Length request.
   # Asynchronous, as prepr above, so a stop signal interrupts the `wait`.
   local push_rc=0
-  GIT_TERMINAL_PROMPT=0 git -C "$wt" -c credential.helper= -c "credential.helper=$PRIV/credhelper.sh" \
+  # Under gh_read's git retry (git_transient only: a 5xx, a reset, a timeout; a
+  # rejection answers at once), as remerge_main.sh's fetches are.
+  GIT_TERMINAL_PROMPT=0 python3 "$(cd "$(dirname -- "$0")/../audit/seat" && pwd)/gh_read.py" --git-retry \
+    git -C "$wt" -c credential.helper= -c "credential.helper=$PRIV/credhelper.sh" \
     -c http.postBuffer=64m push "https://github.com/$repo.git" "$br" &
   wait $! || push_rc=$?
   [ "$push_rc" = 0 ] || die "the App's push of $br to $repo was refused; no pull request was opened or re-bodied"
@@ -676,7 +679,8 @@ cp "$(dirname -- "$SELF")/app_mint.sh" "$W/tool/"
 # The real guard, at the path the copy resolves it by (../audit/seat/), and the
 # signal reap it sources from there.
 mkdir -p "$W/audit/seat" && cp "$(dirname -- "$SELF")/../audit/seat/ref_privacy.py" "$W/audit/seat/" \
-  && cp "$(dirname -- "$SELF")/../audit/seat/pr_args.sh" "$W/audit/seat/"
+  && cp "$(dirname -- "$SELF")/../audit/seat/pr_args.sh" "$W/audit/seat/" \
+  && cp "$(dirname -- "$SELF")/../audit/seat/gh_read.py" "$W/audit/seat/"
 FAILS=0; N=0
 st() { N=$((N + 1)); if [ "$1" = "$2" ]; then echo "ok   $3"; else echo "FAIL $3 (got '$1', want '$2')"; FAILS=$((FAILS + 1)); fi; }
 SHA=1111111111111111111111111111111111111111
@@ -747,6 +751,7 @@ case "$*" in
     else printf 'a\0371+t@users.noreply.github.com\0371+t@users.noreply.github.com\037fix: the stub subject\036'; fi ;;
   *"push https://github.com/"*)
     if [ -f "$STUB/push-fails" ]; then echo "error: stub push refused" >&2; exit 1; fi
+    if [ -f "$STUB/push-flaky" ]; then rm -f "$STUB/push-flaky"; echo "error: RPC failed; HTTP 502 curl 22 The requested URL returned error: 502" >&2; exit 1; fi
     if [ -f "$STUB/push-tree" ]; then  # a push still running when the pusher is stopped
       echo $$ >> "$STUB/pids"
       bash -c 'sleep 30 & echo $! >> "$0"; wait' "$STUB/pids" & echo $! >> "$STUB/pids"
@@ -990,6 +995,13 @@ st "$(grep -c '^curl \(POST\|PATCH\) repos/o/r/pulls' "$W/pushfail/log")" 0 "and
 st "$(calls pushfail 'curl DELETE installation/token')" 1 "the token is revoked after the failed push"
 st "$(leftover pushfail)" 0 "and the private directory is gone, token and all"
 
+# R10-GH-READ-RESIDUE: one transient push failure is ridden out (gh_read's
+# git_transient); a refusal is pushed once and answered at once (the null control).
+mkcase pushflaky; : > "$W/pushflaky/push-flaky"
+run pushflaky o/r "$W/tool-wt" "$BR" "$W/body.md"; st $? 0 "a push that fails once on a 502 still lands and opens the pull request"
+st "$(grep -c '^git .*push https://github.com/' "$W/pushflaky/log")" 2 "the push was tried twice (one transient failure, one success)"
+st "$(grep -c '^git .*push https://github.com/' "$W/pushfail/log")" 1 "a refused push is tried once, never retried"
+
 mkcase mangle; : > "$W/mangle/mangle-body"
 run mangle o/r "$W/tool-wt" "$BR" "$W/body.md"; st $? 1 "a body that reads back different refuses, though the POST returned 0"
 st "$(grep -c 'modulo one trailing newline' "$W/mangle/err")" 1 "naming the byte-identity rule it failed"

## Before you return the verdict (P275)
Run `python3 -I tools/audit/carry_audit.py check --body <PR body file> --comments <file holding [{"id": 0, "body": <verdict.md text>}]>`. Give every reported item its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>`;
an evidence line flagged by its wording takes `Carry: dismissed: evidence, not a finding`. Return the verdict only at rc 0.
