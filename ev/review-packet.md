# Review packet #3242
head: 40019c52e481653979ba934604c0b220c6d5ea37
base: 9315526f8dca6dcd07f9cf3f2685bd1dd633b4f6

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: red
CodeQL id=127775695519 success
arch-score / arch-score id=127775634294 success
arm id=127775458476 skipped
budget-raise-gate / budget-raise-gate id=127775634553 success
cancel-superseded id=127775433495 success
codeql id=127775611529 skipped
codeql / Analyze (actions) id=127775634307 success
codeql / Analyze (javascript-typescript) id=127775634340 success
codeql / Analyze (python) id=127775634344 success
gate id=127775984978 failure
governance id=127775610543 skipped
governance / delivery-status id=127775634516 success
governance / delivery-status-publish id=127775636726 skipped
governance / env-matrix id=127775634410 in_progress
governance / instrument-self-tests id=127775634457 in_progress
governance / policy-docs id=127775634346 success
governance / record id=127775636976 skipped
governance / wave-script id=127775634442 success
hassfest id=127775610214 skipped
hassfest / hassfest id=127775634429 success
kernel-points id=127775635711 skipped
pr-contract id=127775986036 skipped
prelude id=127775433894 success
refresh id=127775433935 success
tests id=127775611389 skipped
tests / arch-instrument id=127775808361 success
tests / briefs id=127775634430 success
tests / browser id=127775808265 in_progress
tests / closure-scope id=127775634476 success
tests / closures id=127775808279 in_progress
tests / coverage id=127775808350 in_progress
tests / fast (3.14) id=127775808347 in_progress
tests / mutation id=127775634354 success
tests / mutation-autofix id=127775864056 skipped
tests / mutation-pins id=127775863741 skipped
tests / nightly-ha id=127775810796 skipped
tests / nightly-status id=127775634396 success
tests / replay id=127775809807 skipped
tests / typing id=127775808254 success
validate id=127775610819 skipped
validate / validate-hacs id=127775634373 success

## Refusals
red-unanswered: concluded red check `gate` is not named in ## Red checks
required-red: required context `gate` concluded failure at 40019c52e481653979ba934604c0b220c6d5ea37

## Advisories
hot-file: HPO_BUS_TRAIN_STATE is unset, so every merge verdict reads unboarded

## carry_audit at the head
NOTE body item 23f95806: dismissed:done on main or in this PR
NOTE body item e5efc307: dismissed:done on main or in this PR
NOTE body item 1a3939e1: dismissed:already in the group brief, unchanged and still owed
NOTE body item 3d0d76cc: dismissed:done on main or in this PR
NOTE body item 6e663196: dismissed:done on main or in this PR
NOTE body item b88b7313: dismissed:already in the group brief, unchanged and still owed
NOTE body item f99d117c: dismissed:already in the group brief, unchanged and still owed
NOTE body item 8db8cd09: dismissed:already in the group brief, unchanged and still owed
NOTE body item 5778dcec: dismissed:already in the group brief, unchanged and still owed
NOTE body item 2692b6d6: dismissed:done on main or in this PR
NOTE body item b37e5437: dismissed:already in the group brief, unchanged and still owed
NOTE body item 09db6f42: dismissed:already in the group brief, unchanged and still owed
NOTE body item 0412922c: dismissed:already in the group brief, unchanged and still owed
NOTE body item 9b407a1c: dismissed:already in the group brief, unchanged and still owed
NOTE body item 15e5463b: dismissed:already in the group brief, unchanged and still owed
NOTE body item 3bd20e57: dismissed:done on main or in this PR
CARRY-AUDIT: 16 finding item(s): 16 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
ok         python3 tools/audit/seat/merge_train.py --self-test
             `tools/audit/seat/merge_train.py` is in the tree at this head
  ok         python3 tests/structure.py
             `tests/structure.py` is in the tree at this head
  ok         bash tools/pr/prepr.sh
             `tools/pr/prepr.sh` is in the tree at this head

FIGURES: 3 resolved, 0 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
none

## Three-dot diff
diff --git a/dev/audit/harnesses/r10_seat_selftests_mutants.py b/dev/audit/harnesses/r10_seat_selftests_mutants.py
index e63e3c1fd..d8dff0474 100644
--- a/dev/audit/harnesses/r10_seat_selftests_mutants.py
+++ b/dev/audit/harnesses/r10_seat_selftests_mutants.py
@@ -274,6 +274,9 @@ MUTANTS = [
     ("merge_train-42", "merge_train.py",
      "queue = t.drain_order([entry] + spooled if front else spooled + [entry])  # mut:start",
      "queue = [entry] + spooled if front else spooled + [entry]  # mut:start"),
+    ("merge_train-43", "merge_train.py", "return bool(tree) and tree == self.tree(tip)", "return bool(tree)"),
+    ("merge_train-44", "merge_train.py", "                status, step, pf_why = t.preflight_entry(item)\n",
+     '                status, step, pf_why = "PASS", "", ""\n'),
     # r10-ci-layout-p2-u9a: the merge-main bot's pin chain under ci.yml's names.
     ("merge_main_bot-1", "tools/pr/merge_main_bot.py", 'PIN_CHAIN = re.compile(r"^tests / (?:',
      'PIN_CHAIN = re.compile(r"^(?:'),
diff --git a/dev/programme/delivery/3242.md b/dev/programme/delivery/3242.md
new file mode 100644
index 000000000..dfb6b1b6a
--- /dev/null
+++ b/dev/programme/delivery/3242.md
@@ -0,0 +1 @@
+- [#3242](https://github.com/tvofi/heatpump_optimizer/pull/3242) — **open**, R10-TRAIN-MERGE-LOOP: train merge loop (R10-TRAIN-MERGE-LOOP)
diff --git a/tools/audit/seat/merge_train.py b/tools/audit/seat/merge_train.py
index f3044585e..a7a2e11f6 100644
--- a/tools/audit/seat/merge_train.py
+++ b/tools/audit/seat/merge_train.py
@@ -770,7 +770,12 @@ POLICY_RED = ("FAILURE", "CANCELLED", "TIMED_OUT", "ACTION_REQUIRED", "STARTUP_F
 # A skip of these classes is the environment's, not the entry's: the train's own
 # worktree holder (P189) or GitHub's branch policy at the last merge attempt
 # (P291). Re-added at the SAME verdict head, such an entry is admitted again.
-READMIT_SAME_VERDICT = (HOLDER, BRANCH_POLICY)
+#: A pre-flight park (`Train.preflight`) of any step other than the holder's. A body
+#: patch moves no head, so the park's cause can be cured at the same verdict;
+#: `train_add` re-runs the pre-flight at the add (`Train.preflight_entry`) and
+#: refuses while the cause holds, the drain's batch pre-flight does the same.
+PREFLIGHT_PARK = "PRE-FLIGHT"
+READMIT_SAME_VERDICT = (HOLDER, BRANCH_POLICY, PREFLIGHT_PARK)
 
 
 class MainMoved(Stop):
@@ -1118,6 +1123,13 @@ def train_add(t: "Train", item: dict, train_argv: "list[str]", launch=launch_det
             t.log(f"ALREADY #{pr}: {held} ({'live train pid %d' % live if live else 'no live train'}); nothing added")
             return 0
         why = t.admit_add(item)
+        if not why and live and str(pr).isdigit():
+            rec = queue_seen_read(t.state).get(str(pr)) or {}
+            if (rec.get("state") == "skipped" and rec.get("class") == PREFLIGHT_PARK
+                    and str(item.get("verdict") or "") == str(rec.get("verdict") or "")):
+                status, step, pf_why = t.preflight_entry(item)
+                if status != "PASS":
+                    why = f"{step}: {pf_why} (the pre-flight park at this verdict still holds)"
         if why:
             t.log(f"ADD REFUSED #{pr} {why}")
             return 1
@@ -2418,6 +2430,19 @@ class Train:
         self.log("TRAIN DONE")
         return 1 if self.skipped else 0
 
+    def pre_flight_reader(self):
+        """The one PreFlight construction `preflight` and `preflight_entry` share."""
+        sys.modules.setdefault("merge_train", sys.modules[__name__])  # one Stop class, not two
+        if str(Path(__file__).resolve().parent) not in sys.path:
+            sys.path.insert(0, str(Path(__file__).resolve().parent))
+        import queue_pre_flight
+        return queue_pre_flight.PreFlight(self.repo, train=self, checkout=ROOT, bot_cured=True,
+                                          free_holders=self.free_holders)
+
+    def preflight_entry(self, item: dict) -> "tuple[str, str, str]":
+        """(status, step, why) of one entry under the same construction `preflight` uses."""
+        return self.pre_flight_reader().entry(item)
+
     def preflight(self, queue: list[dict]) -> list[dict]:
         """`--pre-flight`: queue_pre_flight.py's admission reads over the whole
         queue before anything waits or merges; a PARK or FAIL entry is logged
@@ -2428,12 +2453,7 @@ class Train:
         --free-holders, a holder `freeable` clears. A rehearsal reads none."""
         if not (self.pre_flight and self.real):
             return list(queue)
-        sys.modules.setdefault("merge_train", sys.modules[__name__])  # one Stop class, not two
-        if str(Path(__file__).resolve().parent) not in sys.path:
-            sys.path.insert(0, str(Path(__file__).resolve().parent))
-        import queue_pre_flight
-        pf = queue_pre_flight.PreFlight(self.repo, train=self, checkout=ROOT, bot_cured=True,
-                                        free_holders=self.free_holders)
+        pf = self.pre_flight_reader()
         keep = []
         for item in queue:
             status, step, why = pf.entry(item)
@@ -2445,9 +2465,8 @@ class Train:
                    "verdict": item.get("verdict")}
             # PreFlight parks at `recarry` for one cause, the worktree holder
             # (`worktree_holder`): the environment's, so P189's exception reaches it.
-            cls = HOLDER if step == "recarry" else None
-            if cls:
-                row["class"] = cls
+            cls = HOLDER if step == "recarry" else PREFLIGHT_PARK
+            row["class"] = cls
             self.skipped.append(row)
             self.seen_mark(item.get("pr"), "skipped", cls)
         (self.state / "skipped.json").write_text(json.dumps(self.skipped, indent=2) + "\n")
@@ -2524,6 +2543,25 @@ class Train:
                     + (o.strip().splitlines() or ["(no output)"])[-1][:160]
         return {"pr": n, "verdict": verdict, "verdict_comment": comment}
 
+    def same_tree_posting(self, n: int, tip: str, body: str) -> bool:
+        """The comment's `bus: verdict/<n> at <sha>,` names a commit that is not the tip
+        but stands for it: bus.sh signs `<pr> <tree>`, so a tree posts once whatever
+        commit carries it. True iff <sha> is an ancestor of <tip> and the two trees are
+        equal (the objects from a fetch of verdict/<n>); a failed fetch or read is False."""
+        m = re.search(rf"^bus: verdict/{n} at ([0-9a-f]{{40}}),", body, re.M)
+        if not m or m.group(1) == tip:
+            return False
+        sha = m.group(1)
+        if self.run(["git", "fetch", "-q", "origin", f"verdict/{n}"])[0]:
+            return False
+        if self.run(["git", "merge-base", "--is-ancestor", sha, tip])[0]:
+            return False
+        try:
+            tree = self.tree(sha)
+            return bool(tree) and tree == self.tree(tip)
+        except Stop:
+            return False
+
     def posted_verdict(self, n: int, tip: "str | None", allow: "tuple[set, int]") -> "tuple[str, str] | str":
         """(the merge verdict's head, its comment id) for pull request <n>, or
         why there is none: a confirmed verdict on the bus (`verdict/<n>`, at
@@ -2550,7 +2588,7 @@ class Train:
             return f"verdict/{n} at {tip} is confirmed and not posted"
         v = max(vs, key=lambda c: (c.get("created_at") or "", c.get("id") or 0))
         body = v.get("body") or ""
-        if f"\nbus: verdict/{n} at {tip}," not in body:
+        if f"\nbus: verdict/{n} at {tip}," not in body and not self.same_tree_posting(n, tip, body):
             return f"the newest posted verdict (comment {v.get('id')}) is not verdict/{n}'s tip {tip}"
         first = body.split("\n", 1)[0].rstrip("\r")
         got = proof_watch.parse_verdict(first)
@@ -4882,6 +4920,10 @@ def _queue_self_test(check) -> None:
             a = " ".join(argv)
             if argv[:3] == ["gh", "pr", "list"]:
                 return w.get("list", (0, json.dumps(w["prs"])))
+            if argv[:3] == ["git", "merge-base", "--is-ancestor"]:  # same_tree_posting's reads
+                return (0, "") if (argv[3], argv[4]) in w.get("anc", ()) else (1, "")
+            if argv[:2] == ["git", "rev-parse"] and argv[2].endswith("^{tree}"):
+                return 0, w.get("trees", {}).get(argv[2][:-7], "tree-of-" + argv[2][:-7])
             if argv[:2] == ["git", "ls-remote"]:  # the whole bus, or admit_add's one verdict/<pr>
                 return w.get("ls", (0, "".join(f"{t}\trefs/heads/verdict/{n}\n" for n, t in w["tips"].items()
                                                if argv[-1] in ("refs/heads/verdict/*", f"refs/heads/verdict/{n}"))))
@@ -4926,6 +4968,21 @@ def _queue_self_test(check) -> None:
     check("queue: no verdict/<pr> on the bus is left (#17)", "no confirmed verdict" in left.get(17, ""))
     check("queue: a newest posted verdict that is not the bus tip waits (#18: confirmed, not posted)",
           "not verdict/18's tip" in left.get(18, ""))
+    # Carry 4: bus.sh posts once per `<pr> <tree>`, so a same-tree commit appended after the
+    # posting stands for the posted one; a different tree, or a non-descendant, still waits.
+    def posted_for(tip, **over):
+        wd = world(comments={18: [posted(18, f"Fix review: merge {hx('e')}", tip=hx("7"))]}, **over)
+        tt = Train("o/r", Path(tempfile.mkdtemp(dir=tmp.name)), None, "", (), 1, run=fake(wd)[0], log=lambda m: None)
+        return tt.posted_verdict(18, tip, ({login}, vid))
+    t_new = hx("9")
+    same = posted_for(t_new, anc={(hx("7"), t_new)}, trees={hx("7"): "T1", t_new: "T1"})
+    diff = posted_for(t_new, anc={(hx("7"), t_new)}, trees={hx("7"): "T1", t_new: "T2"})
+    nonanc = posted_for(t_new, anc=set(), trees={hx("7"): "T1", t_new: "T1"})
+    check("queue: a tip one same-tree descendant commit after the commented sha is queued with the same head and comment id",
+          same == (hx("e"), "1018"))
+    check("queue: null controls -- a tip whose tree differs (#18's case), and a same-tree commit that does not descend "
+          "from the commented sha, still wait",
+          isinstance(diff, str) and "not verdict/18's tip" in diff and isinstance(nonanc, str) and "not verdict/18's tip" in nonanc)
     check("queue: a merge comment under another login is no verdict, though it carries the App's id (#19)",
           "not posted" in left.get(19, ""))
     check("queue: a merge comment under the App's login and another id is no verdict (#20)",
@@ -6756,16 +6813,38 @@ def _batch_self_test(check) -> None:
                 sys.modules["queue_pre_flight"] = real_pf
         rec = queue_seen_read(Path(d))
     check("P189 HOLDER arm, pre-flight: a PARK at `recarry` (the worktree holder) is recorded skipped [HOLDER] "
-          "with its verdict, so a same-verdict re-add is admitted; a `carry` PARK is skipped with no class",
+          "with its verdict, so a same-verdict re-add is admitted; a `carry` PARK is skipped [PRE-FLIGHT]",
           kept == [] and rec["7"] == {"verdict": V7, "state": "skipped", "class": HOLDER}
-          and rec["8"] == {"verdict": V7, "state": "skipped"}
-          and already_held(7, V7, rec, set()) is None and bool(already_held(8, V7, rec, set())))
+          and rec["8"] == {"verdict": V7, "state": "skipped", "class": PREFLIGHT_PARK}
+          and already_held(7, V7, rec, set()) is None and already_held(8, V7, rec, set()) is None)
     check("P189 HOLDER arm: an entry skipped [HOLDER] and re-added at the SAME verdict is ADDED by `add` and "
           "by the drain (batch 2), and a ci-skipped one at the same verdict is ALREADY on both sides",
           add_rc == [0, 0] and add_said[0].startswith("ADDED #7") and add_said[1].startswith("ALREADY #8:")
           and more and [int(e["pr"]) for e in bs[-1]] == [7] and "ADDED #7: batch 2 of this train" in drain_said
           and any(ln.startswith("ALREADY #8:") for ln in drain_said))
 
+    # Carries 3/18: a pre-flight park at the SAME verdict rejoins once its cause is
+    # cured (the add re-runs the pre-flight) and is refused, spooling nothing, while it holds.
+    def pf_add(pr, cls, status):
+        with tempfile.TemporaryDirectory() as d:
+            st, pl2 = Path(d), []
+            tq = Train("o/r", st, None, "", (), 1, run=lambda *a, **k: (0, ""), log=pl2.append)
+            tq.admit_add = lambda item: None
+            tq.preflight_entry = lambda item: (status, "findings", "1 unrouted") if status != "PASS" else ("PASS", "", "")
+            (st / QUEUE_OPEN).write_text(f"{os.getpid()}\n")
+            tq._seen = {str(pr): {"verdict": V7, "state": "skipped", **({"class": cls} if cls else {})}}
+            queue_seen_write(st, tq._seen)
+            rc = train_add(tq, {"pr": pr, "verdict": V7}, ["true"], launch=lambda *a: (0, "no"))
+            return rc, pl2, spool_read(st)[0]
+    rc_ok, say_ok, sp_ok = pf_add(7, PREFLIGHT_PARK, "PASS")
+    rc_bad, say_bad, sp_bad = pf_add(7, PREFLIGHT_PARK, "PARK")
+    rc_ci, say_ci, sp_ci = pf_add(8, None, "PASS")
+    check("carries 3/18: a cured pre-flight park rejoins at the same verdict (ADDED, spooled); the uncured one is "
+          "ADD REFUSED rc 1 with no spool line; a ci skip at the same verdict stays ALREADY (null)",
+          rc_ok == 0 and say_ok[0].startswith("ADDED #7") and [e["pr"] for e in sp_ok] == [7]
+          and rc_bad == 1 and say_bad[0].startswith("ADD REFUSED #7 findings: 1 unrouted") and sp_bad == []
+          and rc_ci == 0 and say_ci[0].startswith("ALREADY #8:") and sp_ci == [])
+
     def live_add(w, n):  # the REAL train_add against the live train's state dir, admit_add passed
         al: list[str] = []
         ta = Train("o/r", w["state"], None, "", (), 1, run=stub(w), log=al.append)

## Before you return the verdict (P275)
Run `python3 -I tools/audit/carry_audit.py check --body <PR body file> --comments <file holding [{"id": 0, "body": <verdict.md text>}]>`. Give every reported item its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>`;
an evidence line flagged by its wording takes `Carry: dismissed: evidence, not a finding`. Return the verdict only at rc 0.
