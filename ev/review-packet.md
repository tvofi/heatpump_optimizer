# Review packet #3344
head: 1a1da73c912e471b40b7b06ea94a76b71d62c100
base: 996ded2a6dc52816bd4c7dd873c048d85fc6adad

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: green
CodeQL id=128824506926 success
arch-score / arch-score id=128830476458 success
arm id=128824366852 skipped
budget-raise-gate / budget-raise-gate id=128830476771 success
cancel-superseded id=128830443941 success
codeql id=128830476420 skipped
codeql / Analyze (actions) id=128824465304 success
codeql / Analyze (javascript-typescript) id=128824465408 success
codeql / Analyze (python) id=128824465407 success
gate id=128830443316 success
governance id=128830444371 skipped
governance / delivery-status id=128824465488 success
governance / delivery-status-publish id=128824466580 skipped
governance / env-matrix id=128824465341 success
governance / instrument-self-tests id=128824465334 success
governance / policy-docs id=128824465310 success
governance / record id=128824466376 skipped
governance / wave-script id=128824465355 success
hassfest id=128830444287 skipped
hassfest / hassfest id=128824465265 success
kernel-points id=128830444184 skipped
pr-contract id=128830444158 skipped
pr-contract / pr-contract id=128829924964 success
prelude id=128830443628 success
refresh id=128830443453 success
tests id=128830444432 skipped
tests / arch-instrument id=128824617951 success
tests / briefs id=128824465320 success
tests / browser id=128824618017 success
tests / ci-ratchet id=128829801719 skipped
tests / claims-autofix id=128827410560 skipped
tests / closure-scope id=128824465346 success
tests / closures id=128824617928 success
tests / closures-autofix id=128827890531 skipped
tests / coverage id=128824618053 success
tests / coverage-ratchet id=128829799718 success
tests / fast (3.14) id=128824618037 success
tests / graders-head-copy id=128829799623 success
tests / lane-proofs id=128829799735 success
tests / mutation id=128824465324 success
tests / mutation-autofix id=128824661408 skipped
tests / mutation-pins id=128824661847 skipped
tests / nightly-ha id=128824619836 skipped
tests / nightly-status id=128824465448 success
tests / replay id=128824619368 skipped
tests / typing id=128824618058 success
validate id=128830444203 skipped
validate / validate-hacs id=128824465269 success

## Refusals
none

## Advisories
none

## carry_audit at the head
CARRY-AUDIT: 0 finding item(s): 0 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
ok         python3 tools/audit/seat/roster_edit.py --self-test
             `tools/audit/seat/roster_edit.py` is in the tree at this head
  ok         python3 -I tools/audit/seat/roster_queue.py --self-test
             `tools/audit/seat/roster_queue.py` is in the tree at this head
  ok         python3 -I tools/audit/seat/postmerge.py --self-test
             `tools/audit/seat/postmerge.py` is in the tree at this head
  unverified git diff --stat origin/main...HEAD
             `git diff` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  unverified git merge-base --is-ancestor 28482eceeb6b9809e44b12d80fc994282cc21645 HEAD
             `git merge-base` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals

FIGURES: 3 resolved, 2 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
none

## Three-dot diff
diff --git a/dev/programme/delivery/3344.md b/dev/programme/delivery/3344.md
new file mode 100644
index 000000000..215ef9fd8
--- /dev/null
+++ b/dev/programme/delivery/3344.md
@@ -0,0 +1 @@
+- [#3344](https://github.com/tvofi/heatpump_optimizer/pull/3344) — **open**, R10-ROSTER-WRITE-SWEEP: roster write sweep, part 2 (R10-ROSTER-WRITE-SWEEP)
diff --git a/tools/audit/seat/postmerge.py b/tools/audit/seat/postmerge.py
index f3116863a..afe15fa6d 100644
--- a/tools/audit/seat/postmerge.py
+++ b/tools/audit/seat/postmerge.py
@@ -50,6 +50,16 @@ def steps(pr: int, repo: str, state_dir: Path, sha: str, group: str) -> "list[tu
     ]
 
 
+def refusal_detail(o: str) -> str:
+    """The step's last line, led by the lint ERROR lines a refusal printed: the
+    TOTAL line alone never named what the gate refused (P435)."""
+    lines = [ln.strip() for ln in o.strip().splitlines()]
+    if not lines:
+        return "no output"
+    errs = [ln for ln in lines if ln.startswith("ERROR")][:3]
+    return " | ".join(errs + [lines[-1]])[:300]
+
+
 def postmerge(pr: int, repo: str, state_dir: Path, dry: bool, retry: bool = False,
               run=rb.sh, out=print, roster=None) -> int:
     owed: "list[tuple[str, str]]" = []
@@ -69,7 +79,7 @@ def postmerge(pr: int, repo: str, state_dir: Path, dry: bool, retry: bool = Fals
             out(f"DRY-RUN {name}: " + " ".join(argv))
             continue
         code, o = run(argv)
-        last = o.strip().splitlines()[-1][:160] if o.strip() else "no output"
+        last = refusal_detail(o)
         if name == "main":
             out(f"main {last}")
             if code == 3:  # WAIT: the push's own checks are still running
@@ -120,6 +130,10 @@ def self_test() -> int:
 
     full = "c" * 40
     roster = {"groups": [{"group": "R10-X", "resume": {"branch": "fix/r10-x"}}]}
+    det = refusal_detail("x\n  ERROR   [G-1] cite: a.py:9 moved\nTOTAL: 1 error(s)\n")
+    check("refusal_detail leads with the lint ERROR line", "G-1" in det and det.endswith("TOTAL: 1 error(s)"), det)
+    check("refusal_detail of plain output is its last line (null control)",
+          refusal_detail("a\nb\n") == "b" and refusal_detail("") == "no output")
 
     def fake(rc=None):
         rc = rc or {}
diff --git a/tools/audit/seat/roster_edit.py b/tools/audit/seat/roster_edit.py
index df8cccd8e..6da65c88c 100644
--- a/tools/audit/seat/roster_edit.py
+++ b/tools/audit/seat/roster_edit.py
@@ -887,6 +887,22 @@ def ruling_reader(worktree, checkout):
 
 
 # ----------------------------------------------------------------- flow
+def _on_origin(checkout, wt, sha, branch) -> bool:
+    """Whether some origin ref holds `sha`. The local tracking refs go stale
+    when a rival writer pushes the roster branch, so a miss fetches the
+    branch once and asks again before an unpushed edit is declared."""
+    def held():
+        return bool(run(["git", "-C", str(wt), "for-each-ref", "--contains",
+                         sha, "--format=%(refname)",
+                         "refs/remotes/origin/"]).strip())
+    if held():
+        return True
+    subprocess.run(["git", "-C", str(checkout), "fetch", "-q", "origin",
+                    f"+refs/heads/{branch}:refs/remotes/origin/{branch}"],
+                   capture_output=True)
+    return held()
+
+
 def prepare_worktree(checkout, ref, branch, wt, discard=None) -> str:
     """A throwaway DETACHED worktree at the branch's remote tip when one
     exists (so sequential edits accumulate), else at origin/<ref>; returns
@@ -909,9 +925,7 @@ def prepare_worktree(checkout, ref, branch, wt, discard=None) -> str:
         if run(["git", "-C", str(wt), "status", "--porcelain"]).strip():
             raise Refuse(f"{wt} has uncommitted changes; refusing to reuse it")
         old = run(["git", "-C", str(wt), "rev-parse", "HEAD"]).strip()
-        if old != discard and not run(
-                ["git", "-C", str(wt), "for-each-ref", "--contains", old,
-                 "--format=%(refname)", "refs/remotes/origin/"]).strip():
+        if old != discard and not _on_origin(checkout, wt, old, branch):
             raise Refuse(f"{wt} HEAD {old[:12]} is on no origin ref; an "
                          "unpushed edit would be lost")
         run(["git", "-C", str(wt), "checkout", "-q", "--detach", base_sha])
@@ -997,8 +1011,27 @@ def brief_lint_script(lint_cwd) -> str | None:
     return None
 
 
-def lint_gate(checkout, lint_cwd, roster_path):
-    """brief_lint from a fresh origin/main checkout. Returns (ok, detail)."""
+ERROR_LINE = re.compile(r"^\s*ERROR\b.*$", re.M)
+TOTAL_N = re.compile(r"TOTAL: (\d+) error")
+
+
+def _lint_errors(out):
+    """(the ERROR lines of one lint run, whether they account for its TOTAL).
+    A failure the lines do not account for (a problem printed in another
+    shape) cannot be attributed to a write, so the gate refuses it whole."""
+    errs = [m.group(0).strip() for m in ERROR_LINE.finditer(out)]
+    m = TOTAL_N.search(out)
+    return errs, bool(m) and int(m.group(1)) == len(errs)
+
+
+def lint_gate(checkout, lint_cwd, roster_path, base_text=None):
+    """brief_lint from a fresh origin/main checkout. Returns (ok, detail).
+
+    With `base_text` (the roster as the write found it) the gate refuses only
+    the ERROR lines the same lint over that base does not print: a merge to
+    main that moves a line one brief cites must not stop a write that never
+    touches that brief (P435). Each pre-existing error is returned in `detail`
+    as a WARN naming its group, for the owner to re-pin."""
     run(["git", "-C", str(checkout), "fetch", "-q", "origin", "main"])
     main_sha = run(["git", "-C", str(checkout), "rev-parse", "origin/main"]).strip()
     made = None
@@ -1023,7 +1056,25 @@ def lint_gate(checkout, lint_cwd, roster_path):
         out = r.stdout + r.stderr
         ok = bool(TOTAL_OK.search(out))
         tail = "\n".join(out.strip().splitlines()[-3:])
-        return ok, tail
+        if ok or base_text is None:
+            return ok, tail
+        errs, whole = _lint_errors(out)
+        if not whole:
+            return False, tail
+        bdir = tempfile.mkdtemp(prefix="hpo-lint-base-")
+        try:
+            bpath = Path(bdir) / Path(roster_path).name
+            bpath.write_text(base_text, encoding="utf-8")
+            br = subprocess.run(["node", script, str(bpath)], cwd=lint_cwd,
+                                capture_output=True, text=True)
+            base_errs, _ = _lint_errors(br.stdout + br.stderr)
+        finally:
+            shutil.rmtree(bdir, ignore_errors=True)
+        new = [e for e in errs if e not in base_errs]
+        if new:
+            return False, "\n".join(new + [tail])
+        warn = "\n".join(f"WARN pre-existing, re-pin owed: {e}" for e in errs)
+        return True, warn
     finally:
         if made:
             run(["git", "-C", str(checkout), "worktree", "remove",
@@ -1067,8 +1118,9 @@ def write_roster(checkout, ref, branch, worktree, roster_path, msg, push,
             raise Refuse(str(e))
         path = Path(worktree) / rel
         print(f"roster: {rel} on {branch}")
-        roster = json.loads(path.read_text(encoding="utf-8"))
-        before = json.loads(path.read_text(encoding="utf-8"))
+        base_text = path.read_text(encoding="utf-8")
+        roster = json.loads(base_text)
+        before = json.loads(base_text)
         if not edit(roster, rel):
             return 0
         why = triage_refusal(added_texts(before, roster),
@@ -1086,7 +1138,9 @@ def write_roster(checkout, ref, branch, worktree, roster_path, msg, push,
         run(["git", "-C", str(worktree), "commit", "-q", "-am", msg])
         head = run(["git", "-C", str(worktree), "rev-parse", "HEAD"]).strip()
         refspec = f"{head}:refs/heads/{branch}"
-        ok, detail = lint_gate(checkout, lint_cwd, path)
+        ok, detail = lint_gate(checkout, lint_cwd, path, base_text)
+        if ok and detail:
+            print(detail, file=sys.stderr)
         if not ok:
             print(f"roster_edit: LINT GATE REFUSED the push\n{detail}\n"
                   f"the commit is local at {head[:12]} in {worktree} "
@@ -1101,6 +1155,11 @@ def write_roster(checkout, ref, branch, worktree, roster_path, msg, push,
                             "origin", refspec],
                            capture_output=True, text=True)
         if r.returncode == 0:
+            # our own push: the tracking ref must follow it, or the next op
+            # in this run finds HEAD on no origin ref
+            subprocess.run(["git", "-C", str(checkout), "update-ref",
+                            f"refs/remotes/origin/{branch}", head],
+                           capture_output=True)
             print(f"pushed {branch} at {head}")
             return 0
         why = (r.stderr or r.stdout).strip()[:400]
@@ -1148,7 +1207,9 @@ def build_parser():
                         "containing it")
     p.add_argument("--cite", help="set-size / set-files: <ref>@<sha>, a ref "
                    "that must hold the sha; recorded in resume.note")
-    p.add_argument("--add", nargs="+", help="set-files: paths appended to files")
+    p.add_argument("--add", nargs="+", action="extend",
+                   help="set-files: paths appended to files; repeatable "
+                        "(the default store action kept only the last list)")
     p.add_argument("--set-files", help="set-files: replace files whole "
                    "(comma list, - for none)")
     p.add_argument("--set-hot", help="set-files: replace hot_files whole "
@@ -1424,6 +1485,35 @@ def _self_test() -> int:
     finally:
         os.chdir(here)
 
+    # --- the gate refuses only errors the base roster does not already carry (P435)
+    errlint = (
+        "import {readFileSync} from 'node:fs';\n"
+        "const t=readFileSync(process.argv[2],'utf8');\n"
+        "const e=[...t.matchAll(/__bad_(\\w+)__/g)].map(m=>m[1]);\n"
+        "for (const x of e) console.log(`  ERROR   [G-${x}] cite: a.py:${x} moved`);\n"
+        "console.log(`TOTAL: ${e.length} error(s) across 1 file(s)`);\n")
+    drv_e, lint_e = planted("gate-base", {new_rel: errlint})
+    rpath = lint_e / "roster-under-lint.json"
+    cur = "{}\n__bad_one__\n"
+    def base_gate(text, base):
+        rpath.write_text(text, encoding="utf-8")
+        return lint_gate(drv_e, str(lint_e), rpath, base)
+    ok, why = base_gate(cur + "other edit\n", cur)
+    check("lint gate: an unrelated write passes beside a pre-existing error, warning it",
+          ok and "WARN pre-existing" in why and "G-one" in why, why[:200])
+    ok, why = base_gate(cur + "__bad_two__\n", cur)
+    check("lint gate: the same write adding a bad citation is refused, naming it",
+          not ok and "G-two" in why.splitlines()[0], why[:200])
+    ok, why = base_gate("{}\nclean\n", "{}\nclean\n")
+    check("lint gate: a clean roster writes as before (null control)",
+          ok and why.startswith("TOTAL: 0"), why[:200])
+    ok, why = base_gate(cur, None)
+    check("lint gate: with no base text every error refuses (the old gate)",
+          not ok and "G-one" in why, why[:200])
+    ok, why = base_gate(cur, "{}\n")
+    check("lint gate: an error the base lacks refuses (an empty base set would pass it)",
+          not ok and "G-one" in why, why[:200])
+
     # The fixture's roster: one round, so the newest IS this path.
     FIXTURE_ROSTER = f"{roster_lib.ROSTERS_DIR}/wave-r9-groups.json"
     seed = Path(tmp, "seed")
@@ -2499,7 +2589,7 @@ def _self_test() -> int:
     def racing(times):
         busy = []
 
-        def hooked(checkout, lint_cwd, roster_path):
+        def hooked(checkout, lint_cwd, roster_path, *rest):
             if not busy and len(rivals) < times:
                 rivals.append(f"rival carry {next(serial)}")
                 busy.append(1)
@@ -2512,7 +2602,7 @@ def _self_test() -> int:
                     busy.clear()
                 if rc_r != 0:
                     raise Refuse(f"self-test rival edit failed rc={rc_r}")
-            return real_lint(checkout, lint_cwd, roster_path)
+            return real_lint(checkout, lint_cwd, roster_path, *rest)
         return hooked
 
     def race_tip():
@@ -2704,7 +2794,38 @@ def _self_test() -> int:
     check("fetch_origin: several raced refs in one fetch are one race",
           got[0] == "ok" and got[1] == 2, got)
 
+    # --- a stale tracking ref is not an unpushed edit (P409)
+    wt_ = Path(tmp, "wt")
+    run(["git", "-C", str(drv), "fetch", "-q", "origin"])
+    head_ = tip()
+    run(["git", "-C", str(wt_), "checkout", "-q", "--detach", head_])
+    check("P409: the worktree head is on origin before the tracking ref goes stale",
+          _on_origin(drv, wt_, head_, "edit-1"))
+    for ref_ in run(["git", "-C", str(drv), "for-each-ref", "--format=%(refname)",
+                     "refs/remotes/origin/"]).split():
+        run(["git", "-C", str(drv), "update-ref", "-d", ref_])
+    check("P409: a stale tracking ref (a rival's push) passes after the one fetch",
+          _on_origin(drv, wt_, head_, "edit-1"))
+    run(["git", "-C", str(wt_), "commit", "-q", "--allow-empty", "-m", "unpushed"])
+    check("P409: a real unpushed commit still refuses (null control)",
+          not _on_origin(drv, wt_, run(["git", "-C", str(wt_), "rev-parse",
+                                        "HEAD"]).strip(), "edit-1"))
+    run(["git", "-C", str(wt_), "reset", "-q", "--hard", head_])
+    run(["git", "-C", str(drv), "update-ref", "-d", "refs/remotes/origin/edit-1"])
+    check("P409: two ops in one run both land after our own push",
+          more("set-resume", "R9-A", "first", "--field", "note") == 0
+          and more("set-resume", "R9-A", "second", "--field", "note") == 0
+          and "second" in (grp("R9-A").get("resume") or {}).get("note", "")
+          and subprocess.run(["git", "-C", str(drv), "rev-parse",
+                              "refs/remotes/origin/edit-1"],
+                             capture_output=True, text=True).stdout.strip() == tip())
     shutil.rmtree(tmp, ignore_errors=True)
+    # --- repeated --add (P418): extend, never keep only the last list
+    for argv_, want_ in ((["--add", "a", "--add", "b"], ["a", "b"]),
+                         (["--add", "a", "b", "--add", "c"], ["a", "b", "c"]),
+                         (["--add", "a"], ["a"])):
+        check(f"set-files {' '.join(argv_)} parses to {want_}",
+              parse_op(["set-files", "G", "--worktree", "w"] + argv_)[0].add == want_)
     # --- the roster seat's lane (P215): structural ops need the queue runner's marker
     saved_lane = os.environ.pop(LANE_ENV, None)
     try:
diff --git a/tools/audit/seat/roster_queue.py b/tools/audit/seat/roster_queue.py
index 2dc796f52..5258b84f5 100644
--- a/tools/audit/seat/roster_queue.py
+++ b/tools/audit/seat/roster_queue.py
@@ -280,12 +280,24 @@ def _run_batch(a, sh, rep, py, editor, lines, mark):
         common += ["--branch", a.branch]
     try:
         re_ = load_editor(editor)
-        edits = []
-        for _, (op, g, arg, extra) in items:
-            with contextlib.redirect_stderr(io.StringIO()):  # argparse's usage noise
-                args, value, rest = re_.parse_op(
-                    [op, g] + ([arg] if arg else []) + extra + common)
-            edits.append(re_.make_edit(args, value, rest))
+        edits, good = [], []
+        for ln, (op, g, arg, extra) in items:
+            err = io.StringIO()
+            try:
+                with contextlib.redirect_stderr(err):  # argparse's usage noise
+                    args, value, rest = re_.parse_op(
+                        [op, g] + ([arg] if arg else []) + extra + common)
+                edits.append(re_.make_edit(args, value, rest))
+                good.append((ln, (op, g, arg, extra)))
+            except (SystemExit, re_.Refuse) as e:
+                # one line the parser refuses: name it, batch the rest (P417)
+                why = (err.getvalue().strip().splitlines() or [str(e)])[-1]
+                rep(f"roster: {op} {g} refused rc=2 {why[:300]}")
+                if mark:
+                    mark_line(a.queue, ln, "refused")
+        items = good
+        if not items:
+            return 0
         edit, results = re_.batch_edit(edits)
         _git("fetch", "-q", "origin", cwd=a.lint_clone)
         _git("checkout", "-q", "--detach", "origin/main", cwd=a.lint_clone)
@@ -299,9 +311,8 @@ def _run_batch(a, sh, rep, py, editor, lines, mark):
         m = re.search(r"pushed \S+ at ([0-9a-f]+)", buf.getvalue())
         if rc != 0 or not (m or not any(r is None for r in results)):
             raise RuntimeError(f"batch rc={rc}")
-    except SystemExit as e:  # argparse refused a line: that is a batch-level failure
-        rc, m, results = 1, None, None
-    except Exception as e:  # noqa: BLE001
+    except (SystemExit, Exception) as e:  # noqa: BLE001 - say what, then fall back
+        rep(f"roster: batch failed {type(e).__name__}: {str(e)[:300]}".replace("\n", " "))
         rc, m, results = 1, None, None
     if results is None:
         rep("roster: batch fell back to the single-op path")
@@ -317,6 +328,17 @@ def _run_batch(a, sh, rep, py, editor, lines, mark):
     return 0
 
 
+def refusal_tail(out):
+    """What a refused op reports: the last three lines, or, for a lint-gate
+    refusal, the ERROR lines under its banner -- the TOTAL line alone never
+    named the citation (P435)."""
+    lines = out.strip().split("\n")
+    for i, ln in enumerate(lines):
+        if "LINT GATE REFUSED" in ln:
+            return " | ".join(lines[i + 1:i + 6])[:700]
+    return " | ".join(lines[-3:])[:400]
+
+
 def _run_op(a, sh, rep, py, editor, op, g, arg, extra):
     """One op: exactly one report line, or an exception for the caller to report."""
     cmd = [py, editor, op, g] + ([arg] if arg else []) + extra + [
@@ -348,7 +370,7 @@ def _run_op(a, sh, rep, py, editor, op, g, arg, extra):
         if attempt < 4 and (MOVED in out or ("failed to push" in out and "lint gate: TOTAL: 0" in out)):
             sh("git", "worktree", "remove", "--force", a.worktree)
             continue
-        rep(f"roster: {op} {g} refused rc={r.returncode} " + " | ".join(out.strip().split("\n")[-3:])[:400])
+        rep(f"roster: {op} {g} refused rc={r.returncode} " + refusal_tail(out))
         return False
 
 
@@ -691,6 +713,11 @@ def _self_test():
         run_queue(argparse.Namespace(**{**vars(base), "first": "all", "last": None, "mark": True}),
                   python=sys.executable)
         ck("a marked line is never applied again", (t / "rep").read_text().count("\n") == 3)
+        gate = "x\nroster_edit: LINT GATE REFUSED the push\nERROR [G-1] cite a.py:9\nTOTAL: 1 error(s)\nthe commit is local\n"
+        ck("refusal_tail: a lint-gate refusal reports the ERROR line, not only TOTAL",
+           "ERROR [G-1]" in refusal_tail(gate))
+        ck("refusal_tail: other output is its last three lines (null)",
+           refusal_tail("a\nb\nc\nd") == "b | c | d")
         # inline append-carry readback (LANDED test, first 60 chars)
         ck("readback_text: the carry's first 60 chars are found",
            readback_text(sha, "G", "hello carry", cwd=clone))
@@ -702,8 +729,9 @@ def _self_test():
                   python=sys.executable)
         rr = (t / "rep").read_text().split("\n")
         ck("run --batch: a batch-level failure falls back to the single-op path",
-           rr[0] == "roster: batch fell back to the single-op path"
-           and rr[1] == f"roster: bogus-op G pushed {sha[:9]}", rr)
+           rr[0].startswith("roster: batch failed RuntimeError") and "no batch_edit" in rr[0]
+           and rr[1] == "roster: batch fell back to the single-op path"
+           and rr[2] == f"roster: bogus-op G pushed {sha[:9]}", rr)
         # ONE editor for both paths (resolve_editor), named by what each path ran
         seen = []
         real_load = load_editor
@@ -717,8 +745,8 @@ def _self_test():
                   python=sys.executable)
         globals()["load_editor"] = real_load
         ck("run --batch loads the passed --editor, and its fallback runs that same file",
-           seen == [str(stub)] and (t / "rep").read_text().split("\n")[1]
-           == f"roster: set-stage G pushed {sha[:9]}", seen)
+           seen == [str(stub)] and f"roster: set-stage G pushed {sha[:9]}"
+           in (t / "rep").read_text().split("\n"), seen)
         ck("resolve_editor: no --editor is the roster_edit.py beside this script, never the edit checkout",
            resolve_editor(argparse.Namespace(editor=None, edit_checkout=str(clone)))
            == str(Path(__file__).resolve().parent / "roster_edit.py")
@@ -734,6 +762,15 @@ def _self_test():
                                         "editor": real_ed}), python=sys.executable)
         ck("run --batch: a batch whose every op is refused reports each refused, no fallback",
            (t / "rep").read_text().startswith("roster: set-stage G refused rc=2"))
+        # P417: one malformed line is named and refused; the rest still batch
+        fresh("1 bogus-op G done\n2 set-stage G done\n")
+        run_queue(argparse.Namespace(**{**vars(base), "first": 1, "last": 2, "batch": True,
+                                        "editor": real_ed}), python=sys.executable)
+        rr = (t / "rep").read_text().split("\n")
+        ck("run --batch: a malformed line is named and refused, the rest still batch (no fallback)",
+           rr[0].startswith("roster: bogus-op G refused rc=2")
+           and rr[1].startswith("roster: set-stage G refused rc=2")
+           and "fell back" not in "\n".join(rr), rr)
         # release-held: a held carry waits for its batch file on origin/main
         (t / "q.txt").write_text(
             "#held append-carry G 'x dev/programme/triage/b.md#P1'\n"

## Before you return the verdict (P275)
Run `python3 -I tools/audit/carry_audit.py check --body <PR body file> --comments <file holding [{"id": 0, "body": <verdict.md text>}]>`. Give every reported item its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>`;
an evidence line flagged by its wording takes `Carry: dismissed: evidence, not a finding`. Return the verdict only at rc 0.
