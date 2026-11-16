# Review packet #3664
head: 4f3aa7edb38f9818e7ddb5ce2d411c67a35fe8db
base: 367c3b9cac0f4d11cdbeee9c05ffc893f7e1390c

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: red
CodeQL id=133337497975 success
arch-score / arch-score id=133360248619 success
arm id=133335860868 skipped
budget-raise-gate / budget-raise-gate id=133360248064 success
cancel-superseded id=133360308313 success
codeql id=133360313651 skipped
codeql / Analyze (actions) id=133336926715 success
codeql / Analyze (javascript-typescript) id=133336926667 success
codeql / Analyze (python) id=133336926582 success
gate id=133360246749 success
governance id=133360340920 skipped
governance / env-matrix id=133336926594 success
governance / instrument-self-tests id=133336926569 success
governance / policy-docs id=133336926780 success
governance / record id=133336928892 skipped
governance / wave-script id=133336926494 success
hassfest id=133360323923 skipped
hassfest / hassfest id=133336926814 success
kernel-points id=133360334726 skipped
pr-contract id=133360248729 skipped
pr-contract / pr-contract id=133359068167 success
prelude id=133360247070 success
refresh id=133360325405 success
sweep-self id=133360888315 skipped
tests id=133360340388 skipped
tests / arch-instrument id=133338145184 success
tests / briefs id=133336926546 success
tests / browser id=133338145042 success
tests / ci-ratchet id=133356342845 skipped
tests / claims-autofix id=133346782495 skipped
tests / closure-scope id=133336926644 success
tests / closures id=133338145116 success
tests / closures-autofix id=133355538308 skipped
tests / coverage id=133338145287 success
tests / coverage-ratchet id=133356339166 success
tests / fast (3.14) id=133338144791 success
tests / graders-head-copy id=133356339312 success
tests / lane-proofs id=133356340402 success
tests / mutation id=133336926551 success
tests / mutation-autofix id=133338499005 skipped
tests / mutation-pins id=133338498080 skipped
tests / nightly-ha id=133338148172 skipped
tests / nightly-status id=133336926573 failure
tests / replay id=133338148593 skipped
tests / typing id=133338145034 success
validate id=133360248930 skipped
validate / validate-hacs id=133336926342 success

## Refusals
none

## Advisories
none

## carry_audit at the head
NOTE body item 3fef2a34: R11-PRE-HANDOFF-BOOKKEEPING
NOTE body item 86292713: R11-PRE-HANDOFF-BOOKKEEPING
NOTE body item 8b7c0571: R11-PRE-HANDOFF-BOOKKEEPING
NOTE body item 82662d9b: R11-PRE-HANDOFF-BOOKKEEPING
NOTE body item e388a081: R11-PRE-HANDOFF-BOOKKEEPING
NOTE body item 2c33b089: R11-PRE-HANDOFF-BOOKKEEPING
NOTE body item 6fdb7c0e: R11-PRE-HANDOFF-BOOKKEEPING
NOTE body item 1f2f4342: R11-PRE-HANDOFF-BOOKKEEPING
NOTE body item 0992b3f2: R11-PRE-HANDOFF-BOOKKEEPING
NOTE body item 5ba7a300: R11-PRE-HANDOFF-BOOKKEEPING
NOTE body item 821864ce: R11-PRE-HANDOFF-BOOKKEEPING
NOTE body item 9588abd6: R11-PRE-HANDOFF-BOOKKEEPING
NOTE body item f9083836: R11-PRE-HANDOFF-BOOKKEEPING
NOTE body item e66c5f00: R11-PRE-HANDOFF-BOOKKEEPING
NOTE body item a7ed6e4c: R11-PRE-HANDOFF-BOOKKEEPING
NOTE body item 7f96a248: R11-PRE-HANDOFF-BOOKKEEPING
NOTE body item 79b11b82: R11-PRE-PARALLEL-PIPELINE: R11-PRE-PARALLEL-PIPELINE resolved on origin/handoff/audit-r10-roster
CARRY-AUDIT: 17 finding item(s): 17 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
unverified git update-ref refs/remotes/origin/handoff/audit-r10-roster f20f8b13a797c309719ddb00a853748697f1814f
             `git update-ref` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  unverified PYTHONPATH=tests/hastub python3 tools/pr/<copy>.py --base origin/main --body <body: one item, Carry: R11-OUTSIDE-SELF-SETTING-PUMP> --only orphans
             the path `tools/pr/<copy>.py` is a template or an expansion, not a literal
  unverified python3 -I -c "import sys; sys.path[:0]=['tools/pr']; import ci_predict as c; ..."
             python3 runs an inline script rather than a file
  ok         python3 -I tools/pr/ci_predict.py --self-test
             `tools/pr/ci_predict.py` is in the tree at this head
  unverified python3 -I -c "import json,subprocess,sys;sys.path[:0]=['tools/audit/seat','tools/audit'];import roster_sync as rs;d=json.loads(subprocess.run(['git','show','origin/handoff/audit-r10-roster:dev/programme/rosters/wave-r11-groups.json'],capture_output=True,text=True).stdout);cs=[[c for c in g.get('carry') or [] if isinstance(c,str)] for g in d['groups']];print(sum(map(len,cs)),sum(rs.finding_words(c) in map(rs.finding_words,l[:i]) for l in cs for i,c in enumerate(l)),sum(rs.already_carried(l[:i],c) is not None for l in cs for i,c in enumerate(l)))"
             python3 runs an inline script rather than a file
  ok         python3 -I tools/audit/seat/beat_jobs.py --self-test
             `tools/audit/seat/beat_jobs.py` is in the tree at this head
  ok         tests/gate_lock.py slot-take
             `tests/gate_lock.py` is in the tree at this head
  ok         python3 -I tools/audit/seat/roster_sync.py --self-test
             `tools/audit/seat/roster_sync.py` is in the tree at this head
  ok         python3 -I tools/audit/seat/roster_edit.py --self-test
             `tools/audit/seat/roster_edit.py` is in the tree at this head
  ok         python3 -I tools/audit/seat/ref_privacy.py --check
             `tools/audit/seat/ref_privacy.py` is in the tree at this head
  ok         python3 tests/closure.py select --diff 6d55bf6fd1
             `tests/closure.py` is in the tree at this head
  ok         tests/entities.py
             `tests/entities.py` is in the tree at this head
  ok         tests/doc_claims.py
             `tests/doc_claims.py` is in the tree at this head
  ok         python3 tests/structure.py
             `tests/structure.py` is in the tree at this head
  ok         python3 tools/audit/archscore/score.py --diff 6d55bf6fd1
             `tools/audit/archscore/score.py` is in the tree at this head

FIGURES: 11 resolved, 4 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
none

## Review scope: full (first round: no --reviewed-head)

## Three-dot diff
diff --git a/dev/programme/delivery/3664.md b/dev/programme/delivery/3664.md
new file mode 100644
index 0000000000..8906998fa9
--- /dev/null
+++ b/dev/programme/delivery/3664.md
@@ -0,0 +1 @@
+- [#3664](https://github.com/tvofi/heatpump_optimizer/pull/3664) — **open**, R11-PRE-HANDOFF-BOOKKEEPING: r11 pre handoff bookkeeping (R11-PRE-HANDOFF-BOOKKEEPING)
diff --git a/tools/audit/seat/roster_edit.py b/tools/audit/seat/roster_edit.py
index a27b9517e0..430c9ed85f 100644
--- a/tools/audit/seat/roster_edit.py
+++ b/tools/audit/seat/roster_edit.py
@@ -1355,11 +1355,9 @@ def write_roster(checkout, ref, branch, worktree, roster_path, msg, push,
                             "origin", refspec],
                            capture_output=True, text=True)
         if r.returncode == 0:
-            # our own push: the tracking ref must follow it, or the next op
-            # in this run finds HEAD on no origin ref
-            subprocess.run(["git", "-C", str(checkout), "update-ref",
-                            f"refs/remotes/origin/{branch}", head],
-                           capture_output=True)
+            # No tracking-ref write here: every caller (main, roster_queue's
+            # batch, roster_sync) runs fetch_origin before write_roster, which
+            # moves origin/<branch> to this push for the next op.
             print(f"pushed {branch} at {head}")
             return 0
         why = (r.stderr or r.stdout).strip()[:400]
diff --git a/tools/audit/seat/roster_sync.py b/tools/audit/seat/roster_sync.py
index fd58d0787e..16b4e8459a 100644
--- a/tools/audit/seat/roster_sync.py
+++ b/tools/audit/seat/roster_sync.py
@@ -461,6 +461,28 @@ def finding_words(text: str) -> str:
     return " ".join(MARKUP.sub("", str(text)).lower().split())
 
 
+#: The two wrappers a carry's finding is stored in: the queue's landing
+#: (`carry_audit.land_ops`: `From <pr> (<topic>), body item <id>: <text> (items <id>)`)
+#: and the body's own `Carry: <GROUP>` clause, which the sync's derived text ends with.
+QUEUED_PREFIX = re.compile(r"\AFrom [^:]*?, body item [0-9a-f]{8}: ")
+ITEMS_TAG = re.compile(r"\s*\(items? [0-9a-f]{8}(?:[ ,]+[0-9a-f]{8})*\)\s*\Z")
+CARRY_CLAUSE = re.compile(r"\s*Carry:\s*[^\s()]+\s*\Z")
+ITEM_ID = re.compile(r"\bbody item ([0-9a-f]{8})\b|\(items? ([0-9a-f]{8}(?:[ ,]+[0-9a-f]{8})*)\)")
+
+
+def finding_core(text: str) -> str:
+    """`finding_words` of <text> with the queue's `From ..., body item <id>: `
+    prefix, its `(items <id>)` tag and the trailing `Carry: <GROUP>` clause
+    stripped: the finding one body item records, however it was landed."""
+    t = QUEUED_PREFIX.sub("", " ".join(str(text).split()))
+    return finding_words(CARRY_CLAUSE.sub("", ITEMS_TAG.sub("", t)))
+
+
+def item_ids(text: str) -> set[str]:
+    """The carry_audit body-item ids <text> names as a landing's own tag."""
+    return {i for a, b in ITEM_ID.findall(str(text)) for i in (a, *b.replace(",", " ").split()) if i}
+
+
 def rulings(text: str) -> set[tuple[str, str]]:
     """(round, item) for every triage ruling <text> cites, in the resolvable
     form (`triage: <file>#P<n>`) or the routing seat's prose form
@@ -480,7 +502,7 @@ def rulings(text: str) -> set[tuple[str, str]]:
     return out
 
 
-def already_carried(carries: list, text: str) -> str | None:
+def already_carried(carries: list, text: str, item: str | None = None) -> str | None:
     """The destination carry that records this same finding, or None.
 
     The key is the finding, never the pull request (#2889's B1): one pull
@@ -489,16 +511,18 @@ def already_carried(carries: list, text: str) -> str | None:
     a number in prose (`a second instance beside #2447's`) matches it too. Two
     records are the same finding when they cite the same triage ruling, or
     when their substantive text is equal once markup and whitespace are
-    normalised. A derived copy
+    normalised (`finding_core`: the queue's landing and the body's own
+    `Carry:` clause are wrappers, not the finding), or when the carry is tagged
+    with the body item's own carry_audit id `item`. A derived copy
     the destination already holds is refused before the write path's triage
     gate sees it: that gate refuses an unresolvable `triage P<n>` citation,
     and `write_roster` is atomic, so the duplicate would abort the stage
     changes that stop it being re-derived.
     """
-    want = finding_words(text)
+    want = finding_core(text)
     want_rulings = rulings(text)
     for c in carries:
-        if finding_words(c) == want:
+        if (want and finding_core(c) == want) or (item and item in item_ids(c)):  # mut:dupkey
             return str(c)
         if want_rulings & rulings(c):
             return str(c)
@@ -542,7 +566,7 @@ def carry_plan(roster: dict, transitions: list[PR], repo: str,
                     text = " ".join(BULLET.sub("", row["text"], count=1).split())
                     if text in (g.get("carry") or []) or (dest, text) in appends:
                         continue
-                    held = already_carried(g.get("carry") or [], text)
+                    held = already_carried(g.get("carry") or [], text, row["id"])
                     if held is not None:
                         refusals.append((pr.number, dest,
                                          "already carried (the same finding, "
@@ -1080,6 +1104,18 @@ def self_test() -> int:
          "after": [], "brief": "echo",
          "carry": ["the widget parser drops a unit. `Carry: R9-ECHO`"],
          "resume": {"stage": "not-started"}},
+        # The queue landed #15's item first, wrapped as carry_audit.land_ops
+        # writes it: the sync's own derived text is that finding again.
+        {"group": "R9-QUEUED", "lane": "L1", "issues": [], "fixes": [],
+         "after": [], "brief": "queued",
+         "carry": ["From #15 (r9-carry), body item 0badc0de: the queue landed "
+                   "this first. Carry: R9-QUEUED (items 0badc0de)"],
+         "resume": {"stage": "not-started"}},
+        # The queue's landing reworded, so only its `(items <id>)` tag, the
+        # body item's carry_audit id (set below, from BODY), names the item.
+        {"group": "R9-QID", "lane": "L1", "issues": [], "fixes": [],
+         "after": [], "brief": "qid", "carry": [],
+         "resume": {"stage": "not-started"}},
         # The done hold: #88 is open and only R9-HOLD lists it; #89 is closed.
         {"group": "R9-HOLD", "lane": "L1", "issues": [88], "fixes": [],
          "after": [], "brief": "hold",
@@ -1104,7 +1140,15 @@ def self_test() -> int:
             "- the prose control: a distinct finding for a destination that "
             "only mentions the number. Carry: R9-PROSE\n\n"
             "- the widget parser drops a unit. Carry: R9-ECHO\n\n"
+            "- the queue landed this first. Carry: R9-QUEUED\n\n"
+            "- a distinct finding for the queued group. Carry: R9-QUEUED\n\n"
+            "- the sync's words for the queued item. Carry: R9-QID\n\n"
             "- an issue keeps its own record. Carry: #77\n")
+    qid = next(r["id"] for r in carry_audit.audit(BODY, [], carry_audit.Dests(ROSTER_FIXTURE, set()))["rows"]
+               if "R9-QID" in r["dests"])
+    qid_landing = (f"From #15 (r9-carry), body item {qid}: reworded when the queue "
+                   f"landed it. Carry: R9-QID (items {qid})")
+    next(g for g in groups if g["group"] == "R9-QID")["carry"] = [qid_landing]
     PRS = [
         {"number": 11, "state": "MERGED", "headRefName": "fix/r9-live-pr",
          "mergeCommit": {"oid": "a" * 40}, "body": "## Friction\n\n- none\n"},
@@ -1244,6 +1288,16 @@ def self_test() -> int:
                   "the prose control: a distinct finding for a destination "
                   "that only mentions the number. Carry: R9-PROSE"],
               by["R9-PROSE"].get("carry"))
+        check("the queue's landing of the same item is not appended again: "
+              "its prefix, tag and Carry clause stripped, the text is equal",
+              by["R9-QUEUED"].get("carry")
+              == ["From #15 (r9-carry), body item 0badc0de: the queue landed "
+                  "this first. Carry: R9-QUEUED (items 0badc0de)",
+                  "a distinct finding for the queued group. Carry: R9-QUEUED"],
+              by["R9-QUEUED"].get("carry"))
+        check("a reworded queue landing tagged with the item's own id is not "
+              "appended again", by["R9-QID"].get("carry") == [qid_landing],
+              by["R9-QID"].get("carry"))
         check("a duplicate differing only in markup is not appended",
               by["R9-ECHO"].get("carry")
               == ["the widget parser drops a unit. `Carry: R9-ECHO`"],
diff --git a/tools/pr/ci_predict.py b/tools/pr/ci_predict.py
index f260b5317b..b1dfde50b6 100644
--- a/tools/pr/ci_predict.py
+++ b/tools/pr/ci_predict.py
@@ -549,6 +549,26 @@ def names_changed(root: Path, run: str, changed: set[str]) -> bool:
     return False
 
 
+def recorded_readers(root: Path, changed: set[str]) -> set[str]:
+    """The instrument-self-tests steps whose recorded closure in `root`'s
+    tools/ci/selftest_closures.json holds a changed path in `files` -- the
+    readers a step's run text does not name: queue_pre_flight.py's step reads
+    merge_train.py, which 23b943c987 reddened unnamed. Parsed by
+    selftest_scope's own `job_steps` and `covers`; an unreadable table is none."""
+    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "ci"))
+    try:
+        import selftest_scope as ss
+    finally:
+        sys.path.pop(0)
+    table = ss.load_table(root / ss.TABLE)
+    wf = root / INSTRUMENT_WF
+    if table is None or not wf.is_file():
+        return set()
+    return {st.name for st in ss.job_steps(wf.read_text(), INSTRUMENT_JOB)
+            if st.id in table["steps"]
+            and any(ss.covers(table["steps"][st.id].get("files", ()), c) for c in changed)}
+
+
 # A replay that ran out of time measured nothing about the tree: a loaded host
 # (load average 100+) timed out clean branches at 180 s while CI was green.
 STEP_REPLAY_TIMEOUT_ENV = "HPO_STEP_REPLAY_TIMEOUT_S"
@@ -582,14 +602,16 @@ def replay_step(tree: Path, run: str) -> int:
 
 def step_replay_preds(root: Path, base: str, changed: set[str],
                       notes: list | None = None) -> list[tuple[str, str]]:
-    """Each instrument-self-tests step whose run text names a changed file,
-    replayed at the head; one red there is replayed again, as the base's step of
+    """Each instrument-self-tests step whose run text names a changed file, or
+    whose recorded closure reads one (`recorded_readers`), replayed at the
+    head; one red there is replayed again, as the base's step of
     that name, in a detached worktree of the base, and predicted only where the
     base's is green -- so a step this container cannot run (a missing binary,
     an unset variable: red at both ends) is a note left to CI, never the branch's."""
     import tempfile
     head = instrument_steps(root)
-    hit = {n: r for n, r in head.items() if names_changed(root, r, changed)}
+    readers = recorded_readers(root, changed)  # mut:readers
+    hit = {n: r for n, r in head.items() if n in readers or names_changed(root, r, changed)}
     ran = {n: replay_step(root, r) for n, r in hit.items()}
     for n, rc in ran.items():
         if rc == TIMED_OUT:
@@ -637,7 +659,15 @@ def step_replay_self_test(root: Path) -> int:
                 "          grep -Eq '^{n} self-test: [1-9][0-9]* checks, 0 failed$' \"$RUNNER_TEMP/{n}.txt\"\n")
         (t / INSTRUMENT_WF).write_text(f"jobs:\n  {INSTRUMENT_JOB}:\n    steps:\n"
                                        + step.format(n="a") + step.format(n="b")
-                                       + "      - name: c\n        run: bash tools/c.sh\n")
+                                       + "      - name: c\n        run: bash tools/c.sh\n"
+                                       + "      - name: d\n        id: d\n        run: bash tools/d.sh\n")
+        # d's run text and d.sh name no file of tools/lib/: only its recorded closure reads x.sh.
+        (t / "tools" / "lib").mkdir()
+        (t / "tools" / "lib" / "x.sh").write_text("true\n")
+        (t / "tools" / "d.sh").write_text("set -e; for f in tools/lib/*.sh; do . \"$f\"; done\n")
+        (t / "tools" / "ci").mkdir()
+        table = t / "tools" / "ci" / "selftest_closures.json"
+        table.write_text(json.dumps({"steps": {"d": {"files": ["tools/d.sh", "tools/lib/x.sh"]}}}))
         # c's step names only c.sh, whose text drives a.sh (ref_privacy.py over body_push.sh).
         (t / "tools" / "c.sh").write_text("bash tools/a.sh --self-test | grep -q '^a self-test:'\n")
         ok = "echo '{n} self-test: 3 checks, 0 failed'\n"
@@ -683,6 +713,24 @@ def step_replay_self_test(root: Path) -> int:
                 os.environ.pop(STEP_REPLAY_TIMEOUT_ENV, None)
             else:
                 os.environ[STEP_REPLAY_TIMEOUT_ENV] = was
+        (t / "tools" / "lib" / "x.sh").write_text("exit 1\n")
+        got = [l for _, l in step_replay_preds(t, base, {"tools/lib/x.sh"})]
+        good = len(got) == 1 and got[0].startswith("STEP REPLAY d:")
+        print(f"  {'ok  ' if good else 'FAIL'} a step whose recorded closure reads the changed file, "
+              f"its run text naming none, is replayed and predicted red")
+        bad += not good
+        table.write_text(json.dumps({"steps": {"d": {"files": ["tools/d.sh"]}}}))
+        got = len(step_replay_preds(t, base, {"tools/lib/x.sh"}))
+        print(f"  {'ok  ' if got == 0 else 'FAIL'} null control: a closure not holding the changed file is not replayed")
+        bad += got != 0
+        table.write_text(json.dumps({"steps": {"d": {"files": ["tools/lib/**"]}}}))
+        got = len(step_replay_preds(t, base, {"tools/lib/x.sh"}))
+        print(f"  {'ok  ' if got == 1 else 'FAIL'} a closure's `tools/lib/**` entry covers the changed file")
+        bad += got != 1
+        table.unlink()
+        got = len(step_replay_preds(t, base, {"tools/lib/x.sh"}))
+        print(f"  {'ok  ' if got == 0 else 'FAIL'} no table: no recorded reader, nothing replayed, nothing raised")
+        bad += got != 0
     g = globals()
     real = g["step_replay_preds"]
     g["step_replay_preds"] = lambda *_a: [("instrument", "STEP REPLAY sentinel")]
@@ -858,6 +906,24 @@ def run_key(job: str, prog: str, argv) -> tuple[str, ...]:
     return (job, Path(prog).name, *(a for a in argv if a.startswith("--")))
 
 
+ROUND_ROSTERS = "+refs/heads/handoff/audit-r*-roster:refs/remotes/origin/handoff/audit-r*-roster"
+
+
+def refresh_round_rosters(root: Path) -> str | None:
+    """pr-contract fetches the round rosters before its carry check; a seat's
+    remote-tracking ref is as old as its last fetch, so a group the roster
+    gained since reads as a bad destination. Fetch them into `root` as CI does
+    (the grader arm's clone then takes them, `fetch_round_rosters`). None when
+    fetched, else the note that the roster read may be stale."""
+    try:
+        out = subprocess.run(["git", "fetch", "-q", "--no-tags", "origin", ROUND_ROSTERS],
+                             cwd=root, capture_output=True, text=True, timeout=60)
+        why = f"failed: {' '.join(out.stderr.split())[:240] or 'no output'}" if out.returncode else None
+    except subprocess.TimeoutExpired:
+        why = "timed out"
+    return None if why is None else f"ROSTER UNFETCHED: git fetch of the round rosters {why}; the carry check read this clone's refs"
+
+
 def fetch_round_rosters(run) -> None:
     """CI's pr-contract fetches the round rosters' remote-tracking refs; a
     --shared clone's own origin/handoff/* are root's local branches, so take
@@ -1174,6 +1240,10 @@ def predict(root: Path, base_ref: str, pairs: set | None = None,
     base = (git(root, "merge-base", base_ref, "HEAD") or "").strip()
     if not base:
         return 2, [], f"no merge base between {base_ref} and HEAD"
+    if body:  # the carry arm, and the graders arm's pr-contract run, read the round roster
+        stale = refresh_round_rosters(root)  # mut:roundfetch
+        if stale and notes is not None:
+            notes.append(stale)
     sys.path[:0] = [str(root / "tests"), str(root / "tests" / "hastub")]
     import closure
     names = git(root, "diff", "--name-only", "--no-renames", f"{base}...HEAD") or ""
@@ -1679,6 +1749,75 @@ def roundref_self_test(root: Path) -> int:
         shutil.rmtree(tmp, ignore_errors=True)
     line = [l for l in inspect.getsource(ci_tree_run).splitlines() if "fetch_round_rosters" in l]
     check("ci_tree_run calls fetch_round_rosters on one `# mut:roundrefs` line", len(line) == 1 and "# mut:roundrefs" in line[0])
+    return bad + roundfetch_self_test(root)
+
+
+def roundfetch_self_test(root: Path) -> int:
+    """refresh_round_rosters moves a seat's stale remote-tracking round ref to
+    origin's branch, as pr-contract's fetch does; null: an unreachable origin
+    leaves the ref, raises nothing and returns the note; predict refreshes
+    when given a body and only then."""
+    import shutil
+    import tempfile
+    sys.path.insert(0, str(root / "tests"))
+    from throwaway_git import throwaway_git_clone, throwaway_git_init
+    ref = "refs/remotes/origin/handoff/audit-r10-roster"
+    tmp = Path(tempfile.mkdtemp(prefix="hpo-ci-predict-roundfetch-"))
+    bad = 0
+
+    def check(label, ok):
+        nonlocal bad
+        print(f"  {'ok  ' if ok else 'FAIL'} {label}")
+        bad += not ok
+    try:
+        o = tmp / "o"  # origin: its branches are what pr-contract fetches
+        oenv = throwaway_git_init(o, "-q", "-b", "main")
+
+        def sgit(*a):
+            return subprocess.run(a, cwd=o, env=oenv, capture_output=True, text=True, check=True).stdout.strip()
+        sgit("git", "commit", "-q", "--allow-empty", "-m", "main")
+        sgit("git", "branch", "handoff/audit-r10-roster")
+        stale = sgit("git", "rev-parse", "HEAD")
+        r = tmp / "seat"
+        env = throwaway_git_clone(o, r, "-q")
+        sgit("git", "checkout", "-q", "handoff/audit-r10-roster")
+        sgit("git", "commit", "-q", "--allow-empty", "-m", "the roster gains a group")
+        newer = sgit("git", "rev-parse", "HEAD")
+
+        def got():
+            return subprocess.run(["git", "rev-parse", "-q", "--verify", ref], cwd=r, env=env,
+                                  capture_output=True, text=True).stdout.strip()
+        check("the seat's round ref is stale before the refresh", got() == stale)
+        note = refresh_round_rosters(r)
+        check("refresh_round_rosters moves it to origin's branch and returns no note",
+              note is None and got() == newer)
+        subprocess.run(["git", "update-ref", ref, stale], cwd=r, env=env, check=True)
+        subprocess.run(["git", "remote", "set-url", "origin", str(tmp / "absent.git")], cwd=r, env=env, check=True)
+        try:
+            note, raised = refresh_round_rosters(r), False
+        except Exception:
+            note, raised = None, True
+        check("an unreachable origin leaves the ref, raises nothing and notes ROSTER UNFETCHED with git's "
+              "reason (null control)", not raised and got() == stale
+              and (note or "").startswith("ROSTER UNFETCHED") and "absent.git" in (note or ""))
+    finally:
+        shutil.rmtree(tmp, ignore_errors=True)
+    g = globals()
+    real, calls = g["refresh_round_rosters"], []
+    g["refresh_round_rosters"] = lambda r: calls.append(r) or "ROSTER UNFETCHED sentinel"
+    try:
+        with tempfile.NamedTemporaryFile("w", suffix=".md") as f:
+            f.write("## Forward-carry\n\nnone\n")
+            f.flush()
+            notes: list[str] = []
+            predict(root, "HEAD", body=f.name, only="orphans", notes=notes)
+            check("predict with a body refreshes the round rosters and notes a failed refresh",
+                  len(calls) == 1 and "ROSTER UNFETCHED sentinel" in notes)
+            calls.clear()
+            predict(root, "HEAD", only="orphans", notes=[])
+            check("predict without a body fetches nothing (null control)", not calls)
+    finally:
+        g["refresh_round_rosters"] = real
     return bad
 
 
diff --git a/tools/pr/prepr.sh b/tools/pr/prepr.sh
index d588ad272f..1626906bea 100755
--- a/tools/pr/prepr.sh
+++ b/tools/pr/prepr.sh
@@ -2430,14 +2430,15 @@ EOS
   printf 'def f(x):\n    if x > 0:\n        return 1\n    return 0\n' > "$MR/lib.py"
   printf 'import sys\nsys.path.insert(0, ".")\nfrom lib import f\nsys.exit(0 if [f(v) for v in (-2, 0, 1, 2)] == [0, 0, 1, 1] else 1)\n' > "$MR/tests/check.py"
   (mg add -A && mg commit -qm branch) >/dev/null 2>&1
-  got=$(mutants_line "$MR" "$MB" "false"); r=$?
+  got=$(MUTANT_IN_PLACE= mutants_line "$MR" "$MB" "false"); r=$?
   st "$r" 1 "a MUTANT_CMD failing on the unedited tree is refused, never read as no survivor"
   case "$got" in *'BASELINE FAILS'*) st 1 1 "and the refusal quotes mutant_run's own reason";; *) st 0 1 "and the refusal quotes mutant_run's own reason";; esac
-  got=$(mutants_line "$MR" "$MB" "python3 tests/check.py"); r=$?
+  got=$(MUTANT_IN_PLACE= mutants_line "$MR" "$MB" "python3 tests/check.py"); r=$?
   st "$r" 0 "a check killing every mutant of the added lines passes (null control)"
   # A check that needs the checkout (git) fails the archive copy's baseline and
-  # passes in place: the case MUTANT_IN_PLACE exists for, measured on 3379.
-  got=$(mutants_line "$MR" "$MB" "sh -c 'git rev-parse HEAD >/dev/null && python3 tests/check.py'"); r=$?
+  # passes in place: the case MUTANT_IN_PLACE exists for, measured on 3379. The
+  # archive-copy rows clear MUTANT_IN_PLACE: a fixer runs prepr with it set (fixer.md step 2).
+  got=$(MUTANT_IN_PLACE= mutants_line "$MR" "$MB" "sh -c 'git rev-parse HEAD >/dev/null && python3 tests/check.py'"); r=$?
   st "$r" 1 "a check needing a git checkout measures nothing in the archive copy, and is refused"
   got=$(MUTANT_IN_PLACE=1 mutants_line "$MR" "$MB" "sh -c 'git rev-parse HEAD >/dev/null && python3 tests/check.py'"); r=$?
   st "$r" 0 "the same check under MUTANT_IN_PLACE=1 runs in the checkout and passes"

## Before you return the verdict (P275)
Run `python3 -I tools/audit/carry_audit.py check --body <PR body file> --comments <file holding [{"id": 0, "body": <verdict.md text>}]>`. Give every reported item its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>`;
an evidence line flagged by its wording takes `Carry: dismissed: evidence, not a finding`. Return the verdict only at rc 0.
