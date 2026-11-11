# Review packet #3462
head: 588d1a4dfe607bc990fb3ced410a1df98005b9cf
base: ee64358be7eeccaec5178a923cb3b83a18a924a0

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: pending
arch-score / arch-score id=130507355238 queued
arm id=130504100916 skipped
budget-raise-gate / budget-raise-gate id=130507355222 queued
cancel-superseded id=130504116717 queued
codeql id=130507357513 skipped
governance id=130507357769 skipped
hassfest id=130507357447 skipped
kernel-points id=130507357325 skipped
prelude id=130504116578 queued
refresh id=130504116246 queued
tests id=130507358144 skipped
validate id=130507357338 skipped

## Refusals
none

## Advisories
hot-file: HPO_BUS_TRAIN_STATE is unset, so every merge verdict reads unboarded

## carry_audit at the head
NOTE body item b86ca073: dismissed:the roster branch's R10-GH-READ-RESIDUE-P3 group owns those reads, a group the base roster CI grades against does not yet hold
NOTE body item 39fc2822: dismissed:host install step, now flagged each tick pass by TICK-GH
CARRY-AUDIT: 2 finding item(s): 2 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
ok         python3 tools/audit/seat/merge_train.py --self-test
             `tools/audit/seat/merge_train.py` is in the tree at this head
  ok         python3 -I tools/audit/seat/gh_calls.py --self-test
             `tools/audit/seat/gh_calls.py` is in the tree at this head
  unverified python3 -c 'import sys; sys.path.insert(0,"tools/audit/seat"); import gh_read; sys.exit(gh_read.self_test())'
             python3 runs an inline script rather than a file
  ok         python3 tools/audit/seat/record_row.py --self-test
             `tools/audit/seat/record_row.py` is in the tree at this head
  ok         bash tools/audit/seat/tick_loop.sh --self-test
             `tools/audit/seat/tick_loop.sh` is in the tree at this head
  ok         python3 -I tools/audit/seat/beatd.py --self-test
             `tools/audit/seat/beatd.py` is in the tree at this head
  ok         python3 tools/audit/seat/queue_pre_flight.py --self-test
             `tools/audit/seat/queue_pre_flight.py` is in the tree at this head
  ok         python3 -I tools/policy/agreement_py.py --out <f>
             `tools/policy/agreement_py.py` is in the tree at this head
  ok         node tools/policy/agreement.mjs --py-json <f>
             `tools/policy/agreement.mjs` is in the tree at this head
  ok         python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)
             `tests/closure.py` is in the tree at this head
  ok         tests/entities.py
             `tests/entities.py` is in the tree at this head
  ok         python3 tests/structure.py
             `tests/structure.py` is in the tree at this head
  unverified git grep -c -e '--paginate' -- tools tests ':!*.md'
             `git grep` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals

FIGURES: 11 resolved, 2 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
none

## Review scope: full (first round: no --reviewed-head)

## Three-dot diff
diff --git a/dev/programme/delivery/3462.md b/dev/programme/delivery/3462.md
new file mode 100644
index 000000000..3fbb79570
--- /dev/null
+++ b/dev/programme/delivery/3462.md
@@ -0,0 +1 @@
+- [#3462](https://github.com/tvofi/heatpump_optimizer/pull/3462) — **open**, R10-GH-READ-RESIDUE (part 2): r10 gh read residue p2 (R10-GH-READ-RESIDUE)
diff --git a/tools/audit/seat/beatd.py b/tools/audit/seat/beatd.py
index 7fab6ee56..92a06343b 100644
--- a/tools/audit/seat/beatd.py
+++ b/tools/audit/seat/beatd.py
@@ -37,7 +37,8 @@ died holding it. A job's environment is HOME, USER, LOGNAME, LANG, LC_ALL,
 TMPDIR, SHELL, its env_pass names, `HPO_BEATD_JOB=<name>`, `HPO_REAL_GIT`,
 `HPO_GIT_SHIM_LOG=S/beatd/git-retry.log`, the ref-lock timeout
 (`core.filesRefLockTimeout=30000` through GIT_CONFIG_COUNT), and PATH with
-`beatd_shims` first. The real git is resolved once, before that prepend: the
+`beatd_shims` first, then the seat bin dir (`$HPO_STATE_DIR/bin`, default
+`~/.local/state/hpo/bin`), then the beat's own. The real git is resolved once, before that prepend: the
 first `git` on the beat's own PATH, canonicalised; it refuses rc 2 when there
 is none, when it is a shim (line 2 `# hpo-git-shim`), or when it does not
 answer `--version` with `git version`. `--once` runs each job once; `--for N`
@@ -285,6 +286,11 @@ def next_start(kind: str, prev: float, start: float, end: float, interval_s: flo
     return (end if kind == "watch" else max(prev, start)) + interval_s
 
 
+def seat_bin() -> Path:
+    # GH-BUCKET-SPENDER-UNLOGGED / P449: no daemon PATH reached the seat gh shim, so the opener's gh calls went unlogged
+    return Path(os.environ.get("HPO_STATE_DIR") or Path.home() / ".local/state/hpo") / "bin"
+
+
 class Beat:
     def __init__(self, state: Path, table: dict, repo: Path, real_git: str):
         self.dir = state / "beatd"
@@ -303,7 +309,7 @@ class Beat:
                  HPO_GIT_SHIM_LOG=str(self.dir / "git-retry.log"),
                  GIT_CONFIG_COUNT="1", GIT_CONFIG_KEY_0="core.filesRefLockTimeout",
                  GIT_CONFIG_VALUE_0="30000",
-                 PATH=os.pathsep.join([str(SHIMS), os.environ.get("PATH", "")]))
+                 PATH=os.pathsep.join([str(SHIMS), str(seat_bin()), os.environ.get("PATH", "")]))
         return e
 
     def argv(self, job: dict) -> list[str]:
@@ -965,7 +971,16 @@ def case6_beat(prog, w):
     p = _passes(s, "fetch")
     log = s / "beatd" / "git-retry.log"
     envs = (rw / "env").read_text() if (rw / "env").exists() else ""
-    return {"beat job B exits ok through the shim": r.returncode == 0 and len(p) == 1
+    sd = w / "seatstate"
+    pf = w / "jobpath"
+    t2 = _table(w, [_job("pathjob", ["/bin/bash", "-c", f'echo "$PATH" > {pf}'], timeout_s=60)])
+    _beat(prog, "run", "--state", w / "s6c", "--jobs", t2, "--once",
+          env=dict(os.environ, HPO_STATE_DIR=str(sd)))
+    ents = pf.read_text().strip().split(os.pathsep) if pf.exists() else []
+    beat_path = os.environ.get("PATH", "").split(os.pathsep)
+    return {"job PATH: beatd_shims, then $HPO_STATE_DIR/bin": ents[:2] == [str(SHIMS), str(sd / "bin")],
+            "job PATH: the beat's own PATH follows unchanged": ents[2:] == beat_path,
+            "beat job B exits ok through the shim": r.returncode == 0 and len(p) == 1
             and p[0].endswith("outcome=ok"),
             "beat job's retry lands in S/beatd/git-retry.log": log.exists()
             and len(log.read_text().splitlines()) >= 1,
@@ -1149,8 +1164,11 @@ MUTANTS = {
         "shim", "max=${HPO_GIT_RETRIES:-2}", "max=0", "6",
         "race: B through the shim exits 0, origin/main current, a retry logged"),
     "m6_no_shim_prepend": (
-        "beatd", "PATH=os.pathsep.join([str(SHIMS), os.environ.get(\"PATH\", \"\")]))",
+        "beatd", "PATH=os.pathsep.join([str(SHIMS), str(seat_bin()), os.environ.get(\"PATH\", \"\")]))",
         "PATH=os.environ.get(\"PATH\", \"\"))", "6b", "beat job B exits ok through the shim"),
+    "m6_no_seat_bin": (
+        "beatd", "[str(SHIMS), str(seat_bin()), os.environ", "[str(SHIMS), os.environ", "6b",
+        "job PATH: beatd_shims, then $HPO_STATE_DIR/bin"),
     "m6_drop_C_skip": (
         "shim", "-C|-c|--git-dir", "-c|--git-dir", "6",
         "race: B through the shim exits 0, origin/main current, a retry logged"),
diff --git a/tools/audit/seat/gh_calls.py b/tools/audit/seat/gh_calls.py
index 64ac22d04..ffed9783b 100644
--- a/tools/audit/seat/gh_calls.py
+++ b/tools/audit/seat/gh_calls.py
@@ -1,7 +1,7 @@
 #!/usr/bin/env python3
 """Reader for the gh call log the seat gh shim writes (P284).
 
-    gh_calls.py --top [--since <utc>] [--limit N] [--log PATH]
+    gh_calls.py --top [--since <utc>] [--limit N] [--log PATH]   # rc 3: no call logged
     gh_calls.py --coverage [PID ...]
     gh_calls.py --self-test
 
@@ -10,7 +10,9 @@ by call count, over $HPO_STATE_DIR/gh-calls.log and its rotated .1 (default
 state root $HOME/.local/state/hpo). `--since` keeps lines whose UTC stamp is
 not before it; a stamp is the shim's `YYYY-MM-DDTHH:MM:SSZ`, and a value that
 is not one is refused, never read as "everything". A line the shim did not
-write is counted and reported, not ranked.
+write is counted and reported, not ranked. With no call logged in the window
+it prints one `gh_calls: UNATTRIBUTED:` line naming the gh PATH finds first,
+and whether it is the shim, and exits 3.
 
 --coverage names, for each given pid (default: every process whose command
 line holds a known daemon name), whether the `gh` its PATH finds first is the
@@ -85,20 +87,40 @@ def render_top(lines, since=None, limit=10):
     return "\n".join(out)
 
 
-def first_gh_is_shim(path: str):
-    """True/False: the first executable `gh` on PATH is/is not the shim; None: no gh."""
+def first_gh(path: str):
+    """The first executable `gh` on PATH, else None."""
     for d in path.split(":"):
         p = Path(d or ".") / "gh"
         if p.is_file() and os.access(p, os.X_OK):
-            try:
-                with open(p, errors="replace") as f:
-                    f.readline()
-                    return f.readline().rstrip("\n") == MARKER
-            except OSError:
-                return False
+            return p
     return None
 
 
+def first_gh_is_shim(path: str):
+    """True/False: the first executable `gh` on PATH is/is not the shim; None: no gh."""
+    p = first_gh(path)
+    if p is None:
+        return None
+    try:
+        with open(p, errors="replace") as f:
+            f.readline()
+            return f.readline().rstrip("\n") == MARKER
+    except OSError:
+        return False
+
+
+def top_report(lines, since, limit, path: str):
+    """(rc, text) for --top: the tables at rc 0, or -- no call logged since
+    <since> -- one UNATTRIBUTED line naming the gh that PATH finds, at rc 3.
+    Two "(none)" tables at rc 0 read as "nothing spent" while the bucket hit 0
+    (GH-BUCKET-SPENDER-UNLOGGED, 2026-11-11: no shim was installed)."""
+    if top(lines, since, limit)[3]:
+        return 0, render_top(lines, since, limit)
+    kind = "shim" if first_gh_is_shim(path) else "not the shim"
+    return 3, (f"gh_calls: UNATTRIBUTED: no call logged since {since or 'the log began'}; "
+               f"gh on PATH is {first_gh(path) or 'none'} ({kind})")
+
+
 def proc_path(pid):
     try:
         env = Path(f"/proc/{pid}/environ").read_bytes().split(b"\0")
@@ -575,38 +597,57 @@ def self_test():
             ("gh extension exec", ["extension", "exec", "x"]))
         for label, args in refused:
             check(f"{label} is refused", run(args).returncode == 1)
-        # R10-GH-READ-RESIDUE (P449): one install on the daemons' PATH, run from any checkout. The
-        # baked tree t1, a worktree t2 of it, a clone t3 git does not register beside it, and an
-        # untracked file t4 of the same name.
+        # R10-GH-READ-RESIDUE (P449, then SHIM-COMMENT-GUARD-ONE-CHECKOUT): one install on the
+        # daemons' PATH, run from any checkout of this repository -- a tree that tracks the shim
+        # -- whose gh_comment.py is tracked and unmodified, so its mandate_guard is the committed one.
         sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "tests"))
         from throwaway_git import throwaway_git_clone, throwaway_git_init  # noqa: E402 -- the one throwaway-repo builder
         t1 = w / "t1"
         (t1 / "tools" / "pr").mkdir(parents=True)
         (t1 / "tools" / "pr" / "gh_comment.py").write_text(gcs.read_text())
+        (t1 / "tools" / "audit" / "seat" / "shims").mkdir(parents=True)
+        (t1 / "tools" / "audit" / "seat" / "shims" / "seat-gh").write_text(good)
         genv = throwaway_git_init(t1, "-q")
         for argv in (["add", "."], ["commit", "-qm", "x"], ["worktree", "add", "-q", str(w / "t2")]):
             subprocess.run(["git", *argv], cwd=t1, env=genv, check=True)
-        # t5: a registered worktree whose gh_comment.py git does not track (the tracked half of the rule)
+        # t5: a registered worktree whose gh_comment.py git does not track, in its HEAD or index
         subprocess.run(["git", "worktree", "add", "-q", str(w / "t5")], cwd=t1, env=genv, check=True)
-        subprocess.run(["git", "rm", "-q", "--cached", "tools/pr/gh_comment.py"], cwd=w / "t5", env=genv, check=True)
+        for argv in (["rm", "-q", "--cached", "tools/pr/gh_comment.py"], ["commit", "-qm", "untrack"]):
+            subprocess.run(["git", *argv], cwd=w / "t5", env=genv, check=True)
         throwaway_git_clone(t1, w / "t3", "-q")
         (w / "t4" / "tools" / "pr").mkdir(parents=True)
         (w / "t4" / "tools" / "pr" / "gh_comment.py").write_text(gcs.read_text())
+        # t6: a clone whose gh_comment.py carries a local edit (a mandate_guard removed, say)
+        throwaway_git_clone(t1, w / "t6", "-q")
+        (w / "t6" / "tools" / "pr" / "gh_comment.py").write_text(gcs.read_text() + "# edited\n")
+        # t7: a clean, tracked tools/pr/gh_comment.py in a repository that is not this one (no shim)
+        (w / "t7" / "tools" / "pr").mkdir(parents=True)
+        (w / "t7" / "tools" / "pr" / "gh_comment.py").write_text(gcs.read_text())
+        g7 = throwaway_git_init(w / "t7", "-q")
+        for argv in (["add", "."], ["commit", "-qm", "x"]):
+            subprocess.run(["git", *argv], cwd=w / "t7", env=g7, check=True)
         baked = good.replace("gcpy=@HPO_GH_COMMENT@\n", f"gcpy={t1}/tools/pr/gh_comment.py\n")
+
+        def via(tree, shim):
+            return run([], via=f"{py} -I {w / tree}/tools/pr/gh_comment.py {W}", shim_text=shim).returncode
         for label, tree, want_rc in (
                 ("the baked tree's own script", "t1", 7),
-                ("a second registered worktree's tracked script", "t2", 7),
-                ("null control: a clone git does not list beside the baked tree", "t3", 1),
-                ("null control: an untracked file of the same path and name", "t4", 1),
-                ("null control: a registered worktree whose script is not tracked", "t5", 1)):
-            check(f"second tree: {label}",
-                  run([], via=f"{py} -I {w / tree}/tools/pr/gh_comment.py {W}", shim_text=baked).returncode == want_rc)
-        guard_mut = baked.replace('[ "$wl" = "worktree $troot" ] && ok=1', 'ok=1')
-        check("mutant: the worktree registration dropped lets an unlisted clone through",
-              guard_mut != baked and run([], via=f"{py} -I {w / 't3'}/tools/pr/gh_comment.py {W}", shim_text=guard_mut).returncode == 7)
-        tr_mut = baked.replace(" && git -C \"$troot\" ls-files --error-unmatch tools/pr/gh_comment.py >/dev/null 2>&1", "")
-        check("mutant: the tracked-file predicate dropped lets an untracked script in a registered worktree through",
-              tr_mut != baked and run([], via=f"{py} -I {w / 't5'}/tools/pr/gh_comment.py {W}", shim_text=tr_mut).returncode == 7)
+                ("a second registered worktree's clean tracked script", "t2", 7),
+                ("a second checkout git does not register beside the baked tree, clean", "t3", 7),
+                ("null control: an untracked file of the same path and name, outside any checkout", "t4", 1),
+                ("null control: a checkout whose script is not tracked", "t5", 1),
+                ("null control: the same file with a local edit", "t6", 1),
+                ("null control: a clean tracked script in a repository holding no seat-gh", "t7", 1)):
+            check(f"second tree: {label}", via(tree, baked) == want_rc)
+        for label, frag, tree in (
+                ("the tracked-file predicate dropped lets an untracked script through",
+                 ' && git -C "$troot" ls-files --error-unmatch tools/pr/gh_comment.py >/dev/null 2>&1', "t5"),
+                ("the unmodified predicate dropped lets a locally edited script through",
+                 ' && git -C "$troot" diff --quiet HEAD -- tools/pr/gh_comment.py >/dev/null 2>&1', "t6"),
+                ("the this-repository predicate dropped lets another repository's script through",
+                 ("ls-files --error-unmatch tools/audit/seat/shims/seat-gh", "ls-files tools/audit/seat/shims/seat-gh"), "t7")):
+            m = baked.replace(*frag) if isinstance(frag, tuple) else baked.replace(frag, "")
+            check(f"mutant: {label}", m != baked and via(tree, m) == 7)
         install(good)
         mut = good.replace("trackers='201 ", "trackers='0 ")
         check("mutant: the guard's issue number changed lets the planted post through",
@@ -718,6 +759,30 @@ def self_test():
         (w / "real" / "gh").chmod(0o700)
         check("a real gh ahead of the shim reads as not logged",
               first_gh_is_shim(f"{w / 'real'}:{w / 'own'}") is False)
+
+        # GH-BUCKET-SPENDER-UNLOGGED: an empty window is named, never two "(none)" tables at rc 0.
+        since = "2026-11-11T06:24:00Z"
+        rc, text = top_report([], since, 10, f"{w / 'real'}:{w / 'own'}")
+        check("an empty log with a non-shim gh first: rc 3 and the UNATTRIBUTED line naming it",
+              rc == 3 and text == f"gh_calls: UNATTRIBUTED: no call logged since {since}; "
+                                  f"gh on PATH is {w / 'real' / 'gh'} (not the shim)")
+        rc, text = top_report(sample[:1], since, 10, f"{w / 'real'}")
+        check("lines all before --since are no call logged: rc 3", rc == 3 and "UNATTRIBUTED" in text)
+        rc, text = top_report([], since, 10, f"{w / 'own'}")
+        check("the shim first and nothing logged still reads rc 3, naming the shim",
+              rc == 3 and text.endswith(f"gh on PATH is {w / 'own' / 'gh'} (shim)"))
+        rc, text = top_report([], None, 10, str(tools))
+        check("no gh on PATH at all is named, and no --since reads from the log's start",
+              rc == 3 and text.endswith("since the log began; gh on PATH is none (not the shim)"))
+        one = ["2026-11-11T06:30:00Z 1 orchestrator_tick.py api repos/o/r/pulls"]
+        rc, text = top_report(one, since, 10, f"{w / 'real'}")
+        check("null control: one logged call gives rc 0 and today's tables",
+              rc == 0 and text == render_top(one, since, 10) and "UNATTRIBUTED" not in text)
+        (w / "empty.log").write_text("")
+        r = subprocess.run([sys.executable, "-I", __file__, "--top", "--since", since, "--log", str(w / "empty.log")],
+                           capture_output=True, text=True, env={"PATH": f"{w / 'real'}:{tools}", "HOME": str(w)}, timeout=60)
+        check("the CLI exits 3 with the line on an empty window",
+              r.returncode == 3 and r.stdout.startswith("gh_calls: UNATTRIBUTED: no call logged since "))
     print(f"gh_calls self-test: {pass_n + fail_n} checks, {fail_n} failed")
     return 1 if fail_n else 0
 
@@ -748,11 +813,12 @@ def main(argv):
         return 0
     if "--top" in a:
         try:
-            print(render_top(read_lines(log), since, limit))
+            rc, text = top_report(read_lines(log), since, limit, os.environ.get("PATH", ""))
         except ValueError as e:
             print(f"gh_calls: {e}", file=sys.stderr)
             return 2
-        return 0
+        print(text)
+        return rc
     print(__doc__, file=sys.stderr)
     return 2
 
diff --git a/tools/audit/seat/gh_read.py b/tools/audit/seat/gh_read.py
index 670529685..3adc4df52 100644
--- a/tools/audit/seat/gh_read.py
+++ b/tools/audit/seat/gh_read.py
@@ -32,6 +32,7 @@ its self-test drives both over its alternatives table and compares them.
 from __future__ import annotations
 
 import email.utils
+import json
 import http.client
 import re
 import sys
@@ -206,6 +207,39 @@ def retry(attempt, wait_for, sleep, note=lambda line: None):
         delay *= 3
 
 
+#: One page of a paged list, GitHub's maximum, and the walk's bound: past
+#: MAX_PAGES full pages the read refuses rather than return a truncated list.
+PER_PAGE = 100
+MAX_PAGES = 100
+
+
+def read_pages(read, path: str, key: str = "", per_page: int = PER_PAGE, max_pages: int = MAX_PAGES):
+    """Every item of the paged list at <path> -> (code, items, why); items is
+    None and why the failure on a failed, unparseable or unbounded walk.
+
+    Page by explicit `page=N`, never `gh api --paginate`: that follows the Link
+    header, which names `repositories/<id>/...`, and a cloud seat's proxy
+    answers that URL 403 (S14-CLOUD-CLASSIFY-PAGINATE: `merge_train.py
+    classify` exited 2 on it). A short page ends the walk. `read` is the
+    caller's runner -- `merge_train`'s carries this file's retry rule -- and
+    <key> names the list in an object page (`check_runs`), "" an array page."""
+    sep = "&" if "?" in path else "?"
+    items: list = []
+    for n in range(1, max_pages + 1):
+        code, out = read(["gh", "api", f"{path}{sep}per_page={per_page}&page={n}",
+                          "--jq", f".{key}[]" if key else ".[]"])
+        if code:
+            return code, None, out
+        try:
+            page = [json.loads(x) for x in out.splitlines() if x.strip()]
+        except ValueError:
+            return 1, None, f"page {n} of {path} is not JSON: {one_line(out)[-120:]}"
+        items += page
+        if len(page) < per_page:  # mut:short-page
+            return 0, items, ""
+    return 1, None, f"{path}: more than {max_pages} pages of {per_page}: refused, not truncated"
+
+
 def one_line(failure) -> str:
     return " ".join(str(failure).split())
 
@@ -547,6 +581,57 @@ def self_test() -> int:
     with contextlib.redirect_stderr(io.StringIO()):
         check("--git-retry refuses an argv that is not git (usage, rc 2)", main(["--git-retry", "ls"]) == 2)
 
+    # S14-CLOUD-CLASSIFY-PAGINATE: a paged list read by explicit page number.
+    def server(sizes, key="check_runs"):
+        """A stub `gh api` serving len(sizes) pages of sizes[n-1] items; any
+        followed Link header (`--paginate`, or a repositories/<id> URL) is the
+        cloud proxy's 403."""
+        calls = []
+
+        def read(argv):
+            calls.append(argv)
+            a = " ".join(argv)
+            if "--paginate" in argv or "repositories/" in a:
+                return 1, "gh: Forbidden (HTTP 403)"
+            n = int(argv[2].rsplit("&page=", 1)[1])
+            base = sum(sizes[:n - 1])
+            page = [{"id": base + i} for i in range(sizes[n - 1] if n <= len(sizes) else 0)]
+            jq = argv[argv.index("--jq") + 1] if "--jq" in argv else ""
+            if jq not in (f".{key}[]", ".[]"):
+                return 1, f"unexpected --jq {jq!r}"
+            return 0, "".join(json.dumps(x) + "\n" for x in page)
+        return read, calls
+
+    read, calls = server([2, 2, 1])
+    code, items, why = read_pages(read, "repos/o/r/commits/h/check-runs", "check_runs", per_page=2)
+    check("a three-page answer reads every item, in order, in 3 reads",
+          code == 0 and [x["id"] for x in items] == [0, 1, 2, 3, 4] and len(calls) == 3 and why == "")
+    check("each read names its page explicitly and follows no Link header (the stub 403s one)",
+          [c[2].rsplit("&page=", 1)[1] for c in calls] == ["1", "2", "3"]
+          and not any("--paginate" in c for c in calls))
+    read, calls = server([1])
+    code, items, _ = read_pages(read, "repos/o/r/commits/h/check-runs", "check_runs", per_page=2)
+    check("null control: a one-page (short) answer makes exactly one read",
+          code == 0 and len(items) == 1 and len(calls) == 1)
+    read, calls = server([1])
+    read_pages(read, "repos/o/r/commits/h/check-runs", "check_runs")
+    check("by default a page is GitHub's maximum, 100 (the page size a short page is judged against)",
+          calls[0][2] == "repos/o/r/commits/h/check-runs?per_page=100&page=1")
+    read, calls = server([2, 2, 0], key="")
+    code, items, _ = read_pages(read, "repos/o/r/pulls/1/reviews?state=x", per_page=2)
+    check("a full last page ends on the empty page after it; a query string is extended with &",
+          code == 0 and len(items) == 4 and len(calls) == 3
+          and calls[0][2].startswith("repos/o/r/pulls/1/reviews?state=x&"))
+    read, calls = server([2] * 9, key="")
+    code, items, why = read_pages(read, "repos/o/r/x", per_page=2, max_pages=3)
+    check("a walk past max_pages refuses, never truncates", code == 1 and items is None and "3 pages" in why)
+    code, items, why = read_pages(lambda argv: (4, "gh: Not Found (HTTP 404)"), "repos/o/r/x")
+    check("a failed read is the caller's failure: its code and its text, verbatim",
+          code == 4 and items is None and why == "gh: Not Found (HTTP 404)")
+    code, items, why = read_pages(lambda argv: (0, "{not json\n"), "repos/o/r/x")
+    check("an unparseable page is a failure (rc 1), never an empty list",
+          code == 1 and items is None and why.startswith("page 1 of repos/o/r/x is not JSON"))
+
     print(f"gh_read self-test: {passed + failed} checks, {failed} failed")
     return 1 if failed else 0
 
diff --git a/tools/audit/seat/merge_train.py b/tools/audit/seat/merge_train.py
index 57bd64199..6c2acb0b7 100644
--- a/tools/audit/seat/merge_train.py
+++ b/tools/audit/seat/merge_train.py
@@ -928,11 +928,10 @@ class Stop(Exception):
 # "Base branch was modified", the GraphQL "is not up to date" family).
 BASE_MOVED = re.compile(r"base branch was modified|not up to date|head branch is behind|is behind the base", re.I)
 HOLDER = "HOLDER"                    # the recarry's branch is checked out in another worktree
-def runs_approved(listing: str) -> bool:
-    """True when a head's pull_request runs listing (status<TAB>conclusion
-    lines) has at least one run and none still held action_required."""
-    rows = [ln.split("\t") for ln in listing.splitlines() if ln.strip()]
-    return bool(rows) and not any("action_required" in r for r in rows)
+def runs_approved(runs: "list[dict]") -> bool:
+    """True when a head's pull_request runs listing has at least one run and
+    none still held action_required (its status or its conclusion)."""
+    return bool(runs) and not any("action_required" in (r.get("status"), r.get("conclusion")) for r in runs)
 
 
 BOT_HEAD = "BOT-HEAD"                # a GITHUB_TOKEN push is the head: its pull_request runs are held
@@ -1389,13 +1388,9 @@ def post_approval_wait(t: "Train", pr: int, head: str, poll: float, budget_s: fl
                 revs, why = [], s.why
             at = max((r.get("submitted_at") or "" for r in revs if (r.get("user") or {}).get("login") == APPROVER_BOT
                       and r.get("state") == "APPROVED" and r.get("commit_id") == head), default="")
-            code, raw = t.run(["gh", "api", "--paginate", "--slurp", f"repos/{t.repo}/issues/{pr}/comments?per_page=100"])
-            try:
-                said = code == 0 and any((c.get("user") or {}).get("login") == APPROVER_BOT
-                                         and (c.get("body") or "").startswith(f"Fix review: merge {head}")
-                                         for page in json.loads(raw) for c in page)
-            except (ValueError, TypeError):
-                said = False
+            code, cs, _ = t.pages(f"repos/{t.repo}/issues/{pr}/comments")
+            said = code == 0 and any((c.get("user") or {}).get("login") == APPROVER_BOT
+                                     and (c.get("body") or "").startswith(f"Fix review: merge {head}") for c in cs)
             runs = t._check_runs(head) or []
             mine = [c for c in runs if c.get("name") in WAIT_GATES and at and (c.get("started_at") or "") >= at]
             if not (at and said):
@@ -1600,6 +1595,12 @@ class Train:
             return code, (f"{o.rstrip()} {why}" if why else o)
         return retried
 
+    def pages(self, path: str, key: str = "") -> "tuple[int, list | None, str]":
+        """Every item of the paged list at <path>, by explicit page number
+        under the read rule (gh_read.read_pages): never `--paginate`, whose
+        followed Link header a cloud seat's proxy refuses."""
+        return gh_read.read_pages(self.run, path, key)
+
     def out(self, *argv: str, cwd: Path = ROOT, stdin: str | None = None) -> str:
         return self.run(list(argv), cwd=cwd, stdin=stdin)[1].strip()
 
@@ -1644,10 +1645,8 @@ class Train:
         who, _, subject = o.strip().partition("\t")
         if who not in ("github-actions", "github-actions[bot]"):
             return None
-        code, o = self.run(["gh", "api", "--paginate", "--jq",
-                            '.workflow_runs[] | [.status, (.conclusion // "")] | @tsv',
-                            f"repos/{self.repo}/actions/runs?head_sha={h}&event=pull_request&per_page=100"])
-        return subject if code or not runs_approved(o) else None
+        code, runs, _ = self.pages(f"repos/{self.repo}/actions/runs?head_sha={h}&event=pull_request", "workflow_runs")
+        return subject if code or not runs_approved(runs) else None
 
     def bot_refusal(self, pr: int, h: str, subject: str) -> Stop:
         return Stop("ci", f"#{pr} head {h[:8]} is a GITHUB_TOKEN push (github-actions[bot]: "
@@ -1841,15 +1840,11 @@ class Train:
                     cls=STALE_VERDICT_CARRY)
 
     def _check_runs(self, h: str) -> "list[dict] | None":
-        """One paginated read of the check runs at <h>, parsed; None on a failed
+        """One paged read of the check runs at <h>, parsed; None on a failed
         or unparseable read (wait_ci's fetch, shared with main_green's
         log-only overlap read)."""
-        code, raw = self.run(["gh", "api", "--paginate", "--jq", ".check_runs[]",
-                              f"repos/{self.repo}/commits/{h}/check-runs?per_page=100"])
-        try:
-            return [json.loads(x) for x in raw.splitlines() if x.strip()] if code == 0 else None
-        except ValueError:
-            return None
+        code, runs, _ = self.pages(f"repos/{self.repo}/commits/{h}/check-runs", "check_runs")
+        return None if code else runs
 
     def gate_deferred(self, h: str, red: "list[str]") -> "list[int]":
         """The ids of the other workflow runs at <h> still unfinished when the
@@ -1863,28 +1858,18 @@ class Train:
         stands, today's skip); `wait_ci`'s polls bound the wait."""
         if red != [GATE]:
             return []
-        code, o = self.run(["gh", "api", "--paginate", "--jq", ".workflow_runs[] | [.id, .status] | @tsv",
-                            f"repos/{self.repo}/actions/runs?head_sha={h}&per_page=100"])
+        code, runs, _ = self.pages(f"repos/{self.repo}/actions/runs?head_sha={h}", "workflow_runs")
         if code:
             return []
-        out = []
-        for ln in o.splitlines():
-            rid, _, st = ln.partition("\t")
-            if rid.strip().isdigit() and st.strip() not in ("completed", "action_required", ""):
-                out.append(int(rid))
-        return sorted(out)
+        return sorted(r["id"] for r in runs if isinstance(r.get("id"), int)
+                      and (r.get("status") or "") not in ("completed", "action_required", ""))
 
     def _gate_busy(self, h: str, check_runs) -> list:
         """gate_busy at <h> from one ci.yml runs listing by head sha. An
         unreadable listing reads no run busy, logged: the red stands as it did
         before this read existed -- a refusal, never a wait on a guess."""
-        code, raw = self.run(["gh", "api", "--paginate", "--jq", ".workflow_runs[]",
-                              f"repos/{self.repo}/actions/workflows/ci.yml/runs?head_sha={h}&per_page=100"])
-        try:
-            ci_runs = [json.loads(x) for x in raw.splitlines() if x.strip()] if code == 0 else None
-        except ValueError:
-            ci_runs = None
-        if ci_runs is None:
+        code, ci_runs, _ = self.pages(f"repos/{self.repo}/actions/workflows/ci.yml/runs?head_sha={h}", "workflow_runs")
+        if code:
             self.log(f"gate red at {h[:8]}: the ci.yml runs listing is unreadable, so no run reads busy")
             return []
         return gate_busy(ci_runs, check_runs) or gate_rerunning(ci_runs, check_runs)
@@ -2041,12 +2026,10 @@ class Train:
             return comment, []
         thread = []
         for n in g.RECORD_ISSUES:
-            code, o = self.run(["gh", "api", "--paginate", "--slurp",
-                                f"repos/{self.repo}/issues/{n}/comments"
-                                f"?per_page=100&since={comment.get('created_at')}"])
+            code, cs, why = self.pages(f"repos/{self.repo}/issues/{n}/comments?since={comment.get('created_at')}")
             if code:
-                raise Stop("policy", f"the mandate thread on #{n} could not be read: " + o.strip()[-160:])
-            thread += [c for page in json.loads(o) for c in page]
+                raise Stop("policy", f"the mandate thread on #{n} could not be read: " + why.strip()[-160:])
+            thread += cs
         return comment, thread
 
     def policy_gate(self, pr: int, h: str, files: list[str], posting: "dict | None" = None) -> "str | None":
@@ -2096,11 +2079,10 @@ class Train:
                 read[cid] = self._mandate_read(cid)
             return read[cid]
         try:
-            code, o = self.run(["gh", "api", "--paginate", "--slurp",
-                                f"repos/{self.repo}/pulls/{pr}/reviews?per_page=100"])
+            code, reviews, why = self.pages(f"repos/{self.repo}/pulls/{pr}/reviews")
             if code:
-                raise Stop("policy", head_pol + ": the reviews could not be read: " + o.strip()[-160:])
-            reviews = [r for page in json.loads(o) for r in page] + ([posting] if posting else [])
+                raise Stop("policy", head_pol + ": the reviews could not be read: " + why.strip()[-160:])
+            reviews += [posting] if posting else []
             ok, why = g.approval(reviews, h, mandate_fn, merge_mandate)
             if not ok:
                 raise Stop("policy", head_pol + ": " + (self._policy_move(h, pol, reviews) or why))
@@ -2145,11 +2127,10 @@ class Train:
                 f"({', '.join(moved)}): a fresh owner review, not a carry") if moved else ""
 
     def _reviews(self, pr: int, what: str) -> list[dict]:
-        code, o = self.run(["gh", "api", "--paginate", "--slurp",
-                            f"repos/{self.repo}/pulls/{pr}/reviews?per_page=100"])
+        code, reviews, why = self.pages(f"repos/{self.repo}/pulls/{pr}/reviews")
         if code:
-            raise Stop("approve", f"the reviews could not be read for {what}: " + o.strip()[-160:])
-        return [r for page in json.loads(o) for r in page]
+            raise Stop("approve", f"the reviews could not be read for {what}: " + why.strip()[-160:])
+        return reviews
 
     def _body(self, pr: int) -> str:
         """The pull request's body; an unreadable one stops (a raise's
@@ -2257,12 +2238,8 @@ class Train:
                             "--body-file", str(bf)])
         if code:
             raise Stop("approve", "the carried review was refused: " + o[-200:])
-        try:
-            code, o = self.run(["gh", "api", "--paginate", "--slurp",
-                                f"repos/{self.repo}/pulls/{pr}/reviews?per_page=100"])
-            back = [r for page in json.loads(o) for r in page] if code == 0 else []
-        except ValueError:
-            back = []
+        code, back, _ = self.pages(f"repos/{self.repo}/pulls/{pr}/reviews")
+        back = [] if code else back
         if not any(r.get("state") == "APPROVED" and r.get("commit_id") == h
                    and (r.get("body") or "") == body for r in back):
             raise Stop("approve", "the carried approval did not read back byte-identical; "
@@ -3173,13 +3150,9 @@ class Train:
         if tip is None:
             return f"no confirmed verdict on the bus (verdict/{n})"
         authors, vid = allow
-        code, o = self.run(["gh", "api", "--paginate", "--slurp", f"repos/{self.repo}/issues/{n}/comments?per_page=100"])
-        try:
-            cs = [c for page in json.loads(o) for c in page] if code == 0 else None
-        except (ValueError, TypeError):
-            cs = None
-        if cs is None:
-            return f"its comments could not be read: {o.strip()[-120:]}"
+        code, cs, why = self.pages(f"repos/{self.repo}/issues/{n}/comments")
+        if code:
+            return f"its comments could not be read: {why.strip()[-120:]}"
         vs = [c for c in cs if (c.get("user") or {}).get("login") in authors
               and (c.get("user") or {}).get("id") == vid and (c.get("body") or "").startswith("Fix review:")]
         if not vs:
@@ -3361,9 +3334,8 @@ class Train:
         """The one entry whose own files lie in the closure of every script the
         proof's failing jobs name, under main's table or the proof's; None when
         no script is named (a job with no script) or more than one entry owns them."""
-        code, raw = self.run(["gh", "api", "--paginate", "--jq", ".check_runs[]",
-                              f"repos/{self.repo}/commits/{sha}/check-runs?per_page=100"])
-        runs = [json.loads(x) for x in raw.splitlines() if x.strip()] if code == 0 else []
+        code, runs, _ = self.pages(f"repos/{self.repo}/commits/{sha}/check-runs", "check_runs")
+        runs = [] if code else runs
         scripts: set[str] = set()
         for c in runs:
             if c.get("name") in red and c.get("conclusion") not in GREEN:
@@ -3623,13 +3595,8 @@ class Train:
             code, att = self.run(["gh", "api", f"repos/{self.repo}/actions/runs/{rid}", "--jq", ".run_attempt"])
             if code or att.strip() != "1":
                 continue
-            code, raw = self.run(["gh", "api", "--paginate", "--jq", ".jobs[]",
-                                  f"repos/{self.repo}/actions/runs/{rid}/jobs?filter=latest&per_page=100"])
-            try:
-                failed = [j for j in (json.loads(x) for x in raw.splitlines() if x.strip())
-                          if j.get("conclusion") == "failure"] if code == 0 else []
-            except ValueError:
-                failed = []
+            code, jobs, _ = self.pages(f"repos/{self.repo}/actions/runs/{rid}/jobs?filter=latest", "jobs")
+            failed = [] if code else [j for j in jobs if j.get("conclusion") == "failure"]
             logs = {j.get("id"): job_log(self.run, self.repo, j.get("id")) for j in failed}
             got = infra_due(1, failed, logs)
             if got is None:
@@ -4384,13 +4351,13 @@ def _self_test() -> int:
                     return 0, ""
                 return 0, "\n".join(f for f in (stdin or "").split() if f in ("CLAUDE.md", "AGENTS.md", "dev/governance/roles/fixer.md"))
             if argv[:2] == ["gh", "api"] and "/pulls/" in a and "/reviews" in a:
-                return 0, json.dumps([world.get("reviews", [])])
+                return 0, _jl(world.get("reviews", []))
             if argv[:2] == ["gh", "api"] and "/issues/comments/" in a:
                 return (0, json.dumps(world["mandate"])) if world.get("mandate") \
                     else (1, "gh: Not Found (HTTP 404)")
             if argv[:2] == ["gh", "api"] and any(f"/issues/{n}/comments" in a for n in _mandate_gate().RECORD_ISSUES):
                 # every record issue is read; the fixture's thread is #201's
-                return 0, json.dumps([world.get("thread", []) if "/issues/201/" in a else []])
+                return 0, _jl(world.get("thread", []) if "/issues/201/" in a else [])
             if argv[:2] == ["gh", "api"] and a.endswith("rulesets --jq " + argv[-1]):
                 return (0, "7") if world.get("required", "fast\n") else (1, "HTTP 404")
             if "rulesets/7" in a:
@@ -4413,7 +4380,7 @@ def _self_test() -> int:
             if "state,mergeCommit" in a:
                 return 0, world["merge"].pop(0) if world.get("merge") else "MERGED " + "d" * 40
             if argv[:2] == ["gh", "api"] and re.search(r"/issues/\d+/comments", a):  # pre-flight's findings read
-                return 0, json.dumps([world.get("verdict_comments", [])])
+                return 0, _jl(world.get("verdict_comments", []))
             return 0, ""
         return run, calls
 
@@ -5321,9 +5288,9 @@ def _self_test() -> int:
           "and the train goes on at the new head (null control for the refusal above)",
           rc == 0 and merged(calls) and any("recarry" in ln for ln in lines)
           and any(c[:3] == ["gh", "pr", "merge"] and c[-1] == H1 for c in calls))
-    for what, runs, merges in (("approved (completed/success)", (0, "completed\tsuccess\n"), True),
-                               ("still held action_required", (0, "completed\taction_required\n"), False),
-                               ("held, status form", (0, "action_required\t\n"), False),
+    for what, runs, merges in (("approved (completed/success)", (0, _jl([{"status": "completed", "conclusion": "success"}])), True),
+                               ("still held action_required", (0, _jl([{"status": "completed", "conclusion": "action_required"}])), False),
+                               ("held, status form", (0, _jl([{"status": "action_required", "conclusion": None}])), False),
                                ("absent (no pull_request run)", (0, ""), False),
                                ("unreadable listing", (1, "gh: HTTP 502"), False)):
         rc, lines, calls = go({"bot_tips": {H0: BOT}, "bot_runs": runs})
@@ -5496,7 +5463,8 @@ def _self_test() -> int:
                                                                         "conclusion": "neutral", "started_at": "1"}]})
     check("skipped and neutral are green (null control)", rc == 0 and merged(calls))
     check("the CI read pages past the first 100 runs",
-          any("--paginate" in c and any("check-runs" in x for x in c) for c in calls))
+          any(any("check-runs" in x for x in c) and any(re.search(r"[?&]page=\d+", x) for x in c) for c in calls)
+          and not any("--paginate" in c for c in calls))
     rc, lines, calls = go({"contains": [True, True, False]})
     check("main moving after approval and before the merge stops it", rc == 1 and "merge:" in lines[-1] and not merged(calls))
     rc, lines, calls = go({"preflight": "  ok       policy corpus -- current"})
@@ -5638,9 +5606,9 @@ def _stale_verdict_self_test(check) -> None:
             if argv[:2] == ["git", "ls-remote"]:
                 return 0, f"{T}\trefs/heads/verdict/7\n"
             if argv[:2] == ["gh", "api"] and "/comments" in a:
-                return 0, json.dumps([[{"id": 42, "created_at": "2026-11-06T23:00:00Z",
+                return 0, _jl([{"id": 42, "created_at": "2026-11-06T23:00:00Z",
                                         "user": {"login": login, "id": vid},
-                                        "body": f"Fix review: merge {H}\n\nbus: verdict/7 at {T}, confirmed\n"}]])
+                                        "body": f"Fix review: merge {H}\n\nbus: verdict/7 at {T}, confirmed\n"}])
             if argv[:2] == ["git", "log"]:  # verdict/7, newest first: the merge tip over a blocked one
                 return (log_code, "fatal: bad object" if log_code else
                         f"{T}\x00verdict: #7 Fix review: merge {H}\n"
@@ -5823,7 +5791,7 @@ def _queue_self_test(check) -> None:
                 return 0, json.dumps({"state": "OPEN", "baseRefName": "main", "headRefOid": h})
             if argv[:2] == ["gh", "api"] and "/comments" in a:
                 n = int(a.split("/issues/")[1].split("/")[0])
-                return 0, json.dumps([w["comments"].get(n, [])])
+                return 0, _jl(w["comments"].get(n, []))
             if "--carry" in argv:
                 i = argv.index("--carry")
                 return 0, w["carry"].get((argv[i + 1], argv[i + 2]), "app_approve: REFUSE: unknown pair")
@@ -6260,8 +6228,8 @@ def _gate_race_self_test(check) -> None:
         with tempfile.TemporaryDirectory() as d:
             t = Train("o/r", Path(d), None, "", (), 1, run=run, sleep=lambda s: None, log=lambda s: None, polls=polls)
             return t.wait_ci(H, only=[GATE]), calls_sb
-    busy = "42237558473\tin_progress\n42237558635\tcompleted\n"
-    done = "42237558473\tcompleted\n42237558635\tcompleted\n"
+    busy = _jl([{"id": 42237558473, "status": "in_progress"}, {"id": 42237558635, "status": "completed"}])
+    done = _jl([{"id": 42237558473, "status": "completed"}, {"id": 42237558635, "status": "completed"}])
     rerun_green = dict(edit_gate, conclusion="success", started_at="2026-11-06T15:26:00Z")
     red, _ = wait([[edit_gate], [edit_gate], [rerun_green, code_gate]], [busy, done, done], polls=5)
     check("a failed gate beside an unfinished sibling run is waited on, then through the cascade re-run's lag, "
@@ -6271,7 +6239,7 @@ def _gate_race_self_test(check) -> None:
     red, sb = wait([[edit_gate]], [done])
     check("null control: a red gate with no unfinished sibling run still returns red on the first poll",
           red == [GATE] and len(sb) == 1)
-    red, sb = wait([[edit_gate]], ["42237558473\taction_required\n42237558635\tcompleted\n"])
+    red, sb = wait([[edit_gate]], [_jl([{"id": 42237558473, "status": "action_required"}, {"id": 42237558635, "status": "completed"}])])
     check("a held sibling run (action_required) is not unfinished: the red gate returns on the first poll",
           red == [GATE] and len(sb) == 1)
     red, sb = wait([[edit_gate]], [(1, "boom")])
@@ -6307,7 +6275,7 @@ def _review_settle_self_test(check) -> None:
                 return 0, json.dumps({"mergeStateStatus": ms, "reviewDecision": rd,
                                       "statusCheckRollup": [{"name": "gate", "conclusion": rollup}]})
             if "/reviews" in a:
-                return 0, json.dumps([list(reviews)])
+                return 0, _jl(list(reviews))
             return 0, ""
         t = Train("o/r", Path("."), None, "", (), 1, run=run, sleep=sleeps.append, log=lines.append,
                   polls=3, wall=lambda: NOW)
@@ -7121,13 +7089,13 @@ def _state_self_test(check, go, merged, throwaway_git_init) -> None:
             if got is not None:
                 return got
             if "/reviews" in a:
-                return 0, json.dumps([reviews if reviews is not None else [owner_rv(OLD, now)]])
+                return 0, _jl(reviews if reviews is not None else [owner_rv(OLD, now)])
             if argv[:3] == ["gh", "pr", "view"]:
                 return 0, body
             if "issues/comments/" in a:
                 return 0, json.dumps(mandate_c(now))
             if "/comments" in a:
-                return 0, json.dumps([[]])
+                return 0, _jl([])
             return 1, "unexpected " + a
         saved, buf = Train._run, io.StringIO()
         Train._run = staticmethod(fake_run)
@@ -7658,8 +7626,8 @@ def _batch_self_test(check) -> None:
                 n = a.split("/pulls/")[1].split("/")[0]
                 w.setdefault("reviews_reads", []).append(n)
                 rf = w.get("reviews_for")
-                return 0, json.dumps([(rf(w["heads"][int(n)]) if rf else [])
-                                      + [r for r in w.get("posted", []) if r["pr"] == int(n)]])
+                return 0, _jl((rf(w["heads"][int(n)]) if rf else [])
+                           + [r for r in w.get("posted", []) if r["pr"] == int(n)])
             if argv[:3] == ["gh", "api", "user"]:  # the acting account: the owner's
                 return 0, _mandate_gate().OWNER_LOGIN
             if argv[:3] == ["gh", "pr", "review"]:  # posted as the owner's account, as `gh` is
@@ -7672,7 +7640,7 @@ def _batch_self_test(check) -> None:
             if argv[:2] == ["gh", "api"] and "/issues/comments/" in a:
                 return (0, json.dumps(w["mandate"])) if w.get("mandate") else (1, "gh: Not Found (HTTP 404)")
             if argv[:2] == ["gh", "api"] and any(f"/issues/{n}/comments" in a for n in _mandate_gate().RECORD_ISSUES):
-                return 0, json.dumps([w.get("thread", []) if "/issues/201/" in a else []])
+                return 0, _jl(w.get("thread", []) if "/issues/201/" in a else [])
             if "preflight.sh" in a:
                 return 0, "  clean    no refusal"
             if "worktree_gc.sh" in a:
@@ -8771,11 +8739,13 @@ def _add_self_test(check) -> None:
                 return 0, "true" if w.get("is_draft") else "false"
             if argv[:2] == ["git", "ls-remote"]:  # verdict/<pr>'s confirmed tip
                 return w.get("ls", (0, f"{T}\t{argv[-1]}\n"))
+            if argv[:2] == ["gh", "api"] and "/comments" in a and "comments" in w:
+                return w["comments"]
             if argv[:2] == ["gh", "api"] and "/comments" in a:  # its posting: merge at the added verdict
                 first = w.get("first", f"Fix review: merge {w.get('verdict', H)}")
-                return 0, json.dumps([[{"id": 42, "created_at": "2026-10-25T00:00:00Z",
+                return 0, _jl([{"id": 42, "created_at": "2026-10-25T00:00:00Z",
                                         "user": {"login": login, "id": vid},
-                                        "body": f"{first}\n\nbus: verdict/{w.get('pr', 7)} at {T}, confirmed\n"}]])
+                                        "body": f"{first}\n\nbus: verdict/{w.get('pr', 7)} at {T}, confirmed\n"}])
             if argv[:3] == ["gh", "pr", "view"]:
                 return w.get("view", (0, json.dumps({"state": "OPEN", "baseRefName": "main", "headRefOid": H})))
             if "--carry" in argv:
@@ -8787,7 +8757,7 @@ def _add_self_test(check) -> None:
             if "--corpus-filter" in a:
                 return 0, "\n".join(f for f in (stdin or "").split() if f == "CLAUDE.md")
             if argv[:2] == ["gh", "api"] and "/reviews" in a:
-                return 0, json.dumps([w.get("reviews", [])])
+                return 0, _jl(w.get("reviews", []))
             if argv[:2] == ["gh", "api"] and "/pulls/" in a:  # the body raise_hold justifies
                 return 0, ""
             if argv[:3] == ["gh", "pr", "view"]:
@@ -8813,6 +8783,8 @@ def _add_self_test(check) -> None:
              "base: #7 targets dev"),
             ("verdict", {"ls": (0, "")}, "verdict: no confirmed verdict on the bus (verdict/7)"),
             ("verdict", {"ls": (128, "fatal: unreachable")}, "verdict: the verdict bus could not be read"),
+            ("verdict", {"comments": (1, "gh: Not Found (HTTP 404)")},
+             "verdict: its comments could not be read: gh: Not Found (HTTP 404)"),
             ("verdict", {"first": f"Fix review: blocked {H} tests: red"}, "verdict: the newest verdict is blocked"),
             ("verdict", {"first": f"Fix review: merge {V}"},
              "verdict: the newest posted merge verdict names 222222222222, not the added 111111111111"),
@@ -9187,12 +9159,12 @@ def _post_approval_self_test(check) -> None:
             if "git/ref/pull" in j:
                 return 0, ref
             if "/reviews" in j:
-                return 0, json.dumps([[{"user": {"login": APPROVER_BOT}, "state": "APPROVED", "commit_id": H,
-                                       "submitted_at": AT}]])
+                return 0, _jl([{"user": {"login": APPROVER_BOT}, "state": "APPROVED", "commit_id": H,
+                                       "submitted_at": AT}])
             if "/comments" in j:
                 if comments is not None:
                     return 0, comments
-                return 0, json.dumps([[{"user": {"login": APPROVER_BOT}, "body": f"Fix review: {verdict} {H}\nn"}]])
+                return 0, _jl([{"user": {"login": APPROVER_BOT}, "body": f"Fix review: {verdict} {H}\nn"}])
             if "check-runs" in j:
                 rs = runs_by_poll[min(len(slept), len(runs_by_poll) - 1)]
                 return 0, "\n".join(json.dumps(r) for r in rs)
@@ -9455,5 +9427,10 @@ def main(argv: list[str]) -> int:
                  **opts).train(queue)
 
 
+def _jl(items) -> str:
+    """A paged read's stub answer: one compact JSON item per line (`--jq .[]`)."""
+    return "".join(json.dumps(x) + "\n" for x in items)
+
+
 if __name__ == "__main__":
     sys.exit(main(sys.argv[1:]))
diff --git a/tools/audit/seat/orchestrator_tick.py b/tools/audit/seat/orchestrator_tick.py
index 894d00ca2..9ce2cd959 100644
--- a/tools/audit/seat/orchestrator_tick.py
+++ b/tools/audit/seat/orchestrator_tick.py
@@ -2811,6 +2811,9 @@ def self_test() -> int:
         gh.on("rate_limit", out=json.dumps({"remaining": rate[0],
                                             "limit": rate[1]}))
         for pr, rv in (reviews or {}).items():
+            flat = [x for p in rv for x in (p if isinstance(p, list) else [p])]
+            gh.on(lambda argv, pr=pr: any(f"pulls/{pr}/reviews" in a and "page=" in a for a in argv),
+                  out="".join(json.dumps(x) + "\n" for x in flat))
             gh.on(f"pulls/{pr}/reviews", out=json.dumps(rv))
         # GitHub search answers GET only: a stub that 404s any search call
         # NOT carrying --method GET, so an arm fails loudly on the POST form
diff --git a/tools/audit/seat/queue_pre_flight.py b/tools/audit/seat/queue_pre_flight.py
index 20a8afbc1..a3a8d24de 100644
--- a/tools/audit/seat/queue_pre_flight.py
+++ b/tools/audit/seat/queue_pre_flight.py
@@ -184,14 +184,9 @@ class PreFlight:
         code, body = self.t.run(["gh", "api", f"repos/{self.repo}/pulls/{pr}", "--jq", '.body // ""'])
         if code:
             return f"the body could not be read: {body.strip()[-160:]}"
-        code, o = self.t.run(["gh", "api", "--paginate", "--slurp",
-                              f"repos/{self.repo}/issues/{pr}/comments?per_page=100"])
-        try:
-            if code:
-                raise ValueError(o.strip()[-160:])
-            comments = [c for page in json.loads(o) for c in page]
-        except (ValueError, TypeError) as e:
-            return f"the comments could not be read: {e}"
+        code, comments, why = self.t.pages(f"repos/{self.repo}/issues/{pr}/comments")
+        if code:
+            return f"the comments could not be read: {why.strip()[-160:]}"
         if not ca.finding_rows(body, comments)[0]:
             return ""  # nothing to route: the roster is not read
         try:
@@ -358,17 +353,17 @@ def _self_test() -> int:
             if argv[:2] == ["gh", "api"] and "/reviews" in a:
                 if world.get("reviews_fail"):
                     return 1, "gh: HTTP 403"
-                return 0, json.dumps([world.get("reviews", [])])
+                return 0, mt._jl(world.get("reviews", []))
             if argv[:2] == ["gh", "api"] and "/issues/comments/" in a:
                 return (0, json.dumps(world["mandate"])) if world.get("mandate") \
                     else (1, "gh: Not Found (HTTP 404)")
             if argv[:2] == ["gh", "api"] and any(f"/issues/{n}/comments" in a for n in mt._mandate_gate().RECORD_ISSUES):
                 # every record issue is read; the fixture's thread is #201's
-                return 0, json.dumps([world.get("thread", []) if "/issues/201/" in a else []])
+                return 0, mt._jl(world.get("thread", []) if "/issues/201/" in a else [])
             if argv[:2] == ["gh", "api"] and "/issues/7/comments" in a:
                 if world.get("comments_fail"):
                     return 1, "gh: HTTP 502"
-                return 0, json.dumps([world.get("comments", [])])
+                return 0, mt._jl(world.get("comments", []))
             if argv[:2] == ["gh", "api"] and a.endswith("/pulls/7 --jq .body // \"\""):
                 return 0, world.get("body", "")
             if argv[:3] == ["gh", "api", "user"]:  # the acting account `policy_approval_due` reads: the owner's
diff --git a/tools/audit/seat/shims/seat-gh b/tools/audit/seat/shims/seat-gh
index 75060fd9a..a0efd0fbb 100755
--- a/tools/audit/seat/shims/seat-gh
+++ b/tools/audit/seat/shims/seat-gh
@@ -123,7 +123,7 @@ esac
 # The record-issue comment guard (R10-RAISE-GATE-SHIM; tools/pr/gh_comment.py's mandate_guard
 # lives in that script alone, so a raw post bypassed it). DENY BY DEFAULT: a call that could
 # write a comment on a record issue (#201, or its continuation) is refused unless the caller is python running the
-# tree's own gh_comment.py (by real path); it is let through only when it is on an explicit
+# baked tree's gh_comment.py, or a checkout's tracked and unmodified one (by real path; below); it is let through only when it is on an explicit
 # list of calls that cannot. The list is gh's own command table, not a list of spellings:
 #   - no subcommand, or --version/--help alone: pass; any other leading flag: refused;
 #   - `issue`: view/list/status/create pass; comment, close, reopen, edit, delete, lock,
@@ -336,18 +336,19 @@ if [ -n "${hit:-}" ]; then
     done
     if [ -n "$script" ] && [ -n "$gcpy" ]; then
       a=$(rp "$script") && b=$(rp "$gcpy") && [ "$a" = "$b" ] && ok=1
-      # Another tree's gh_comment.py (R10-GH-READ-RESIDUE, P449): the daemons' PATH carries one
-      # install, run from any checkout. Admitted by real path when it is the tracked
-      # tools/pr/gh_comment.py of a worktree git registers beside the baked tree's; a file
-      # merely so named, in a directory git does not list, stays refused.
+      # Another checkout's gh_comment.py (R10-GH-READ-RESIDUE, P449; SHIM-COMMENT-GUARD-ONE-CHECKOUT,
+      # P591): the daemons' PATH carries one install, and three live checkouts run seat tools.
+      # Admitted by real path <root>/tools/pr/gh_comment.py when <root> is a checkout of this
+      # repository (it tracks this shim) and the script is tracked and unmodified against HEAD,
+      # so its mandate_guard is the committed one. A file merely so named, an untracked one, or
+      # one with a local edit stays refused.
       if [ -z "$ok" ] && [ -n "$a" ]; then
         case $a in */tools/pr/gh_comment.py)
-          troot=${a%/tools/pr/gh_comment.py} broot=${gcpy%/tools/pr/gh_comment.py}
-          if [ "$broot" != "$gcpy" ] && git -C "$troot" ls-files --error-unmatch tools/pr/gh_comment.py >/dev/null 2>&1; then
-            while IFS= read -r wl; do
-              [ "$wl" = "worktree $troot" ] && ok=1
-            done < <(git -C "$broot" worktree list --porcelain 2>/dev/null)
-          fi ;;
+          troot=${a%/tools/pr/gh_comment.py}
+          git -C "$troot" ls-files --error-unmatch tools/audit/seat/shims/seat-gh >/dev/null 2>&1 \
+            && git -C "$troot" ls-files --error-unmatch tools/pr/gh_comment.py >/dev/null 2>&1 \
+            && git -C "$troot" diff --quiet HEAD -- tools/pr/gh_comment.py >/dev/null 2>&1 \
+            && ok=1 ;;
         esac
       fi
     fi ;;
diff --git a/tools/audit/seat/tick_loop.sh b/tools/audit/seat/tick_loop.sh
index a75d48bad..f3ce6b003 100644
--- a/tools/audit/seat/tick_loop.sh
+++ b/tools/audit/seat/tick_loop.sh
@@ -56,6 +56,13 @@
 # HPO_TICK_CMD replace the relay script and the tick command (the self-test's stubs).
 set -uo pipefail
 HERE=$(cd "$(dirname -- "$0")" && pwd)
+# The seat bin dir (seat_venv.sh --install-shims; $HPO_STATE_DIR/bin) goes first on the
+# PATH every child inherits -- orchestrator_tick.py, cloud_relay.sh, the sweep's train --
+# so their gh is the logging shim (GH-BUCKET-SPENDER-UNLOGGED: the tick was ~21% of a
+# spent bucket, unlogged). Once: a restart's exec inherits it already first.
+SEAT_BIN=${HPO_STATE_DIR:-$HOME/.local/state/hpo}/bin
+case $PATH in "$SEAT_BIN":*) ;; *) PATH=$SEAT_BIN:$PATH ;; esac  # mut:seatbin
+export PATH
 
 # The relay holder: takes <out>.relay.lock (flock, non-blocking; 75 when held), runs
 # the relay with its output in <out>.relay.log, then writes "<rc> <started-utc>" to
@@ -151,8 +158,13 @@ sweep_pass() { # <out>: one merge-train sweep when one is due; prints its TICK-S
 }
 
 tick_pass() { # <out> [tick args...]: one pass; prints the banner
-  local out=$1 relay rrc trc tmp now code behind stale; shift
+  local out=$1 relay rrc trc tmp now code behind stale g; shift
   relay=${HPO_TICK_RELAY:-$HERE/cloud_relay.sh}
+  # GH-BUCKET-SPENDER-UNLOGGED: a pass whose children's gh is not the shim spends unlogged.
+  g=$(command -v gh)
+  [ -n "$g" ] && sed -n '2{p;q;}' "$g" 2>/dev/null | grep -qxF '# hpo-gh-shim' \
+    || printf 'TICK-GH %s gh=%s: not the seat gh shim; this pass'"'"'s gh calls are not logged (seat_venv.sh --install-shims %s)\n' \
+      "$(date -u +%FT%TZ)" "${g:-none}" "$SEAT_BIN"
   mkdir -p "$(dirname -- "$out")"
   fresh_check "$out"
   if [ -n "$stale" ]; then
@@ -185,6 +197,22 @@ tick_loop_self_test() (
   chmod +x "$t/tick.sh"
   printf '#!/bin/bash\necho "hb $*" >> "%s/hb"; exit "${HB_RC:-0}"\n' "$t" > "$t/hb.sh"
   export HPO_TICK_HEARTBEAT=$t/hb.sh
+  # The seat bin dir under a scratch state dir, holding a gh that carries the shim marker,
+  # so a host whose gh is not the shim (CI's) prints no TICK-GH line in the rows below.
+  mkdir -p "$t/state/bin" "$t/bare/bin"; export HPO_STATE_DIR=$t/state
+  printf '#!/bin/sh\n# hpo-gh-shim\nexit 0\n' > "$t/state/bin/gh"; chmod +x "$t/state/bin/gh"
+  # GH-BUCKET-SPENDER-UNLOGGED: the children run with the seat bin dir first on PATH.
+  printf '#!/bin/bash\nprintf "%%s\\n" "$PATH" > "%s/path"; command -v gh > "%s/gh"; echo BOARD\n' "$t" "$t" > "$t/pathtick.sh"
+  out=$(HPO_TICK_RELAY=$t/absent.sh HPO_TICK_CMD="bash $t/pathtick.sh" bash "$0" --once --out "$t/b.txt")
+  case $(cat "$t/path") in "$t/state/bin:"*) [ "$(cat "$t/gh")" = "$t/state/bin/gh" ] && ! printf '%s\n' "$out" | grep -q '^TICK-GH' ;; *) false ;; esac
+  ck "the tick's child PATH starts with the seat bin dir, whose gh shim it finds; no TICK-GH line" $?
+  out=$(PATH="$t/state/bin:$PATH" HPO_TICK_RELAY=$t/absent.sh HPO_TICK_CMD="bash $t/pathtick.sh" bash "$0" --once --out "$t/b.txt")
+  [ "$(tr ':' '\n' < "$t/path" | grep -cx "$t/state/bin")" = 1 ]
+  ck "a PATH already led by the seat bin dir (a restart's exec) is not prepended twice" $?
+  out=$(HPO_STATE_DIR=$t/bare HPO_TICK_RELAY=$t/absent.sh HPO_TICK_CMD="bash $t/pathtick.sh" bash "$0" --once --out "$t/b.txt")
+  g=$(cat "$t/gh"); printf '%s\n' "$out" | grep -Eq "^TICK-GH [0-9T:-]+Z gh=${g:-none}: not the seat gh shim" \
+    && [ "$(printf '%s\n' "$out" | grep -c '^TICK-')" = 2 ]
+  ck "a seat bin dir with no gh shim: one TICK-GH flag line naming the gh found, beside the banner" $?
   # The rows before the freshness rows run from no checkout: never the real one, whose
   # fetch and checkout a restart would move.
   mkdir "$t/nogit"; export HPO_TICK_CODE_DIR=$t/nogit GIT_CEILING_DIRECTORIES=$t
diff --git a/tools/policy/agreement_py.py b/tools/policy/agreement_py.py
index 125b5b0e6..ee976a856 100644
--- a/tools/policy/agreement_py.py
+++ b/tools/policy/agreement_py.py
@@ -378,7 +378,7 @@ def budget_raise():
                 if argv[:3] == ["git", "merge-base", "origin/main"]:
                     return 0, base + "\n"
                 if argv[:2] == ["gh", "api"] and "/reviews" in " ".join(argv):
-                    return 0, "[[]]"
+                    return 0, ""  # no review: an empty page of the train's paged read (gh_read.read_pages)
                 return 1, f"agreement_py: no answer for {argv[:3]}"
             import tempfile
             with tempfile.TemporaryDirectory() as d:

## Before you return the verdict (P275)
Run `python3 -I tools/audit/carry_audit.py check --body <PR body file> --comments <file holding [{"id": 0, "body": <verdict.md text>}]>`. Give every reported item its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>`;
an evidence line flagged by its wording takes `Carry: dismissed: evidence, not a finding`. Return the verdict only at rc 0.
