# Review packet #2978
head: 6e89bf7f902f701170b3393e8eaa6d27f23d73e6
base: 043b111d01c90ecb1220980df1d363c0b50bb37f

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: red
CodeQL id=123831380600 neutral
arch-score / arch-score id=123831132358 success
arm id=123830965773 skipped
budget-raise-gate / budget-raise-gate id=123831132593 success
cancel-superseded id=123830972245 success
codeql / Analyze (actions) id=123831132332 success
codeql / Analyze (javascript-typescript) id=123831132417 success
codeql / Analyze (python) id=123831132422 in_progress
governance / delivery-status id=123831132360 success
governance / delivery-status-publish id=123831134170 skipped
governance / env-matrix id=123831132294 in_progress
governance / instrument-self-tests id=123831132411 in_progress
governance / policy-docs id=123831132572 in_progress
governance / record id=123831133937 skipped
governance / wave-script id=123831132390 success
hassfest / hassfest id=123831132449 success
kernel-points id=123831133428 skipped
prelude id=123830972113 success
refresh id=123830971862 success
tests / arch-instrument id=123831277619 in_progress
tests / briefs id=123831132286 success
tests / browser id=123831277524 in_progress
tests / closure-scope id=123831132213 success
tests / closures id=123831277545 in_progress
tests / coverage id=123831277528 in_progress
tests / fast (3.14) id=123831277515 in_progress
tests / mutation id=123831132236 success
tests / mutation-autofix id=123831393670 skipped
tests / mutation-pins id=123831392351 skipped
tests / nightly-ha id=123831278855 skipped
tests / nightly-status id=123831132239 failure
tests / replay id=123831278567 skipped
tests / typing id=123831277540 in_progress
validate / validate-hacs id=123831132140 success

## Refusals
red-unanswered: concluded red check `tests / nightly-status` is not named in ## Red checks

## Advisories
none

## carry_audit at the head
CARRY-AUDIT: 0 finding item(s): 0 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
ok         python3 tools/audit/seat/merge_train.py --self-test
             `tools/audit/seat/merge_train.py` is in the tree at this head
  ok         python3 dev/audit/harnesses/r10_train_overlap_grade_p2_mutants.py
             `dev/audit/harnesses/r10_train_overlap_grade_p2_mutants.py` is in the tree at this head
  ok         python3 tests/structure.py
             `tests/structure.py` is in the tree at this head
  ok         tests/entities.py
             `tests/entities.py` is in the tree at this head
  ok         PYTHONPATH=tests/hastub python3 tests/entities.py
             `tests/entities.py` is in the tree at this head
  ok         python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir <dir>
             `tests/closure.py` is in the tree at this head
  unverified git grep -n "QUEUE_PENDING\|QUEUE_SEEN\|already_held(\|queue_seen_read(" -- tools/ .github/ tests/
             `git grep` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals

FIGURES: 6 resolved, 1 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
none

## Three-dot diff
diff --git a/dev/audit/harnesses/r10_train_overlap_grade_p2_mutants.py b/dev/audit/harnesses/r10_train_overlap_grade_p2_mutants.py
new file mode 100644
index 000000000..064e37e3a
--- /dev/null
+++ b/dev/audit/harnesses/r10_train_overlap_grade_p2_mutants.py
@@ -0,0 +1,114 @@
+#!/usr/bin/env python3
+"""R10-TRAIN-OVERLAP-GRADE part 2: one mutant per arm of merge_train.py's one
+admission rule (`already_held`, P129 as amended by P189 and P291), against its
+own self-test.
+
+    python3 dev/audit/harnesses/r10_train_overlap_grade_p2_mutants.py            # all, 4 at a time
+    python3 dev/audit/harnesses/r10_train_overlap_grade_p2_mutants.py --list     # enumerate only
+    python3 dev/audit/harnesses/r10_train_overlap_grade_p2_mutants.py M0 M5      # named
+
+Run from the branch's worktree. Each mutant replaces exactly one source span of
+tools/audit/seat/merge_train.py (the span must occur exactly once, or the
+mutant is reported STALE, never silently skipped), writes the result beside the
+original as `_mutant_<id>.py` (so ROOT, gh_read and the tool table resolve as
+for the real file), runs its `--self-test`, and prints the FAIL lines. M0 is
+the unmutated file and must pass; every other mutant must fail at least one
+check, else it SURVIVED. The copies are removed whatever happens.
+"""
+from __future__ import annotations
+
+import concurrent.futures
+import subprocess
+import sys
+from pathlib import Path
+
+def repo_root(start):
+    """The directory holding custom_components/heatpump_optimizer/manifest.json."""
+    from pathlib import Path
+    here = Path(start).resolve()
+    if here.is_file():
+        here = here.parent
+    marker = Path("custom_components") / "heatpump_optimizer" / "manifest.json"
+    for cand in (here, *here.parents):
+        if (cand / marker).is_file():
+            return cand
+    raise RuntimeError(f"no repository root above {start}")
+
+
+ROOT = repo_root(__file__)
+SRC = ROOT / "tools/audit/seat/merge_train.py"
+
+# (id, arm, the span, its replacement)
+MUTANTS = [
+    ("M0", "the unmutated head", "", ""),
+    ("M1", "the drain applies the shared rule, not the any-seen rule",
+     '                held = already_held(int(e["pr"]), e.get("verdict"), self._seen, set())',
+     '                held = "in this train already" if str(int(e["pr"])) in self._seen else None'),
+    ("M2", "a skip takes the entry out of the pending layer",
+     '        self.seen_mark(pr, "skipped", cls)  # out of the pending layer',
+     '        pass  # out of the pending layer'),
+    ("M3", "a BRANCH-POLICY skip is re-admitted at the same verdict",
+     'READMIT_SAME_VERDICT = (HOLDER, BRANCH_POLICY)', 'READMIT_SAME_VERDICT = (HOLDER,)'),
+    ("M4", "a HOLDER skip is re-admitted at the same verdict",
+     'READMIT_SAME_VERDICT = (HOLDER, BRANCH_POLICY)', 'READMIT_SAME_VERDICT = (BRANCH_POLICY,)'),
+    ("M5", "the same-verdict exception holds in the drain too, not in add only",
+     '                held = already_held(int(e["pr"]), e.get("verdict"), self._seen, set())',
+     '                held = already_held(int(e["pr"]), e.get("verdict"), {n: {k: v for k, v in r.items() '
+     'if k != "class"} for n, r in self._seen.items()}, set())'),
+    ("M6", "every merge attempt refused by the branch policy is classed BRANCH-POLICY",
+     'cls=BRANCH_POLICY if BRANCH_POLICY_SAID.search(said) else None)', 'cls=None)'),
+    ("M7", "a skipped entry at a new verdict is admitted",
+     '        if str(verdict or "") != str(rec.get("verdict") or ""):\n            return None',
+     '        if False:\n            return None'),
+    ("M8", "an earlier batch's skip never drops a re-added serial entry",
+     '            bad = {s["pr"] for s in self.skipped[mine:]}', '            bad = {s["pr"] for s in self.skipped}'),
+    ("M9", "a merge is recorded merged", '                self.seen_mark(pr, "merged")\n', ''),
+    ("M10", "null control: an entry still to run is ALREADY",
+     '    if state == "pending":\n        return "still to run in this train"',
+     '    if state == "pending":\n        return None'),
+    ("M11", "add reads the live train's record",
+     'queue_seen_read(t.state) if live else {}', '{}'),
+    ("M12", "a spooled entry is ALREADY", '    if pr in spooled:\n        return', '    if False:\n        return'),
+    ("M13", "a pre-flight PARK at recarry is a HOLDER skip",
+     '            cls = HOLDER if step == "recarry" else None', '            cls = None'),
+]
+
+
+def one(m: tuple[str, str, str, str]) -> tuple[str, str, list[str]]:
+    mid, _arm, old, new = m
+    text = SRC.read_text()
+    if old and text.count(old) != 1:
+        return mid, "STALE", [f"span occurs {text.count(old)} times"]
+    dst = SRC.parent / f"_mutant_{mid}.py"
+    try:
+        dst.write_text(text.replace(old, new) if old else text)
+        r = subprocess.run([sys.executable, str(dst), "--self-test"], cwd=ROOT, capture_output=True, text=True,
+                           timeout=1800)
+        fails = [ln.strip() for ln in r.stdout.splitlines() if ln.startswith("  FAIL")]
+        if mid == "M0":
+            return mid, "PASS" if r.returncode == 0 and not fails else "BROKEN", fails
+        return mid, "KILLED" if fails or r.returncode else "SURVIVED", fails or [f"rc {r.returncode}"]
+    finally:
+        dst.unlink(missing_ok=True)
+
+
+def main(argv: list[str]) -> int:
+    if argv[:1] == ["--list"]:
+        for mid, arm, _o, _n in MUTANTS:
+            print(f"{mid}\t{arm}")
+        return 0
+    todo = [m for m in MUTANTS if not argv or m[0] in argv]
+    bad = 0
+    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:
+        for mid, state, fails in ex.map(one, todo):
+            arm = next(a for i, a, _o, _n in MUTANTS if i == mid)
+            print(f"{mid} {state}: {arm}")
+            for f in fails[:4]:
+                print(f"    {f[:200]}")
+            bad += state not in ("PASS", "KILLED")
+    print(f"MUTANTS: {len(todo)} run, {bad} not as required")
+    return 1 if bad else 0
+
+
+if __name__ == "__main__":
+    sys.exit(main(sys.argv[1:]))
diff --git a/dev/programme/delivery/2978.md b/dev/programme/delivery/2978.md
new file mode 100644
index 000000000..5693ea7ff
--- /dev/null
+++ b/dev/programme/delivery/2978.md
@@ -0,0 +1 @@
+- [#2978](https://github.com/tvofi/heatpump_optimizer/pull/2978) — **open**, R10-TRAIN-OVERLAP-GRADE part 2: one admission rule for add and the batch drain (R10-TRAIN-OVERLAP-GRADE)
diff --git a/tests/closures.json b/tests/closures.json
index 2671377dd..7194cff3a 100644
--- a/tests/closures.json
+++ b/tests/closures.json
@@ -3815,6 +3815,7 @@
    "dev/audit/harnesses/r10_tick_train_mutants.sh",
    "dev/audit/harnesses/r10_tick_which_roster.py",
    "dev/audit/harnesses/r10_title_seam.sh",
+   "dev/audit/harnesses/r10_train_overlap_grade_p2_mutants.py",
    "dev/audit/harnesses/r10_train_raise_hold_mutants.sh",
    "dev/audit/harnesses/r10_train_raise_hold_replay.py",
    "dev/audit/harnesses/r10_train_upgrade_mutants.py",
diff --git a/tools/audit/seat/instruments/merge_train.py.md b/tools/audit/seat/instruments/merge_train.py.md
index 4ce430257..d5afb80c8 100644
--- a/tools/audit/seat/instruments/merge_train.py.md
+++ b/tools/audit/seat/instruments/merge_train.py.md
@@ -61,7 +61,15 @@
   `batch` also takes several batches in one queue (a list of lists), run in
   order on one train, each with its own admission, proof and merges; between
   two it drains what `train.sh add` spooled into one more batch, never into a
-  batch in proof, and a batch that stops ends the train (`NOT RUN` lines). A
+  batch in proof, and a batch that stops ends the train (`NOT RUN` lines).
+  `add` and that drain apply one admission rule (`already_held`, over the
+  live train's `queue.seen.json`): a pull request still to run, spooled,
+  merged or run by this train is `ALREADY` on both sides; one it skipped is
+  admitted again at a new verdict head, and at the same one when the skip was
+  the environment's (`[HOLDER]`, or `[BRANCH-POLICY]`: every merge attempt
+  refused by GitHub's base-branch policy). `skipped.json`'s rows name the
+  verdict. `dev/audit/harnesses/r10_train_overlap_grade_p2_mutants.py` holds
+  one mutant per arm of that rule. A
   policy head batches like any other: under a `--mandate` naming the mandate's
   comment id, in force for policy merging, the train posts the citing approval
   step 5 requires (`policy_approve`); a budget raise still goes serial.
diff --git a/tools/audit/seat/merge_train.py b/tools/audit/seat/merge_train.py
index 02ffc447d..57ab85a87 100644
--- a/tools/audit/seat/merge_train.py
+++ b/tools/audit/seat/merge_train.py
@@ -217,7 +217,8 @@ THE LIVE QUEUE (R10-TRAIN-UPGRADE; tvofi, 2026-10-24). `batch` runs its batches
 in order and, between two, drains `<state-dir>/queue-add.jsonl` -- what `add`
 appended while a batch ran -- into one more batch; a batch in proof is never
 changed. `add` (train.sh add) takes the state dir's flock, is a no-op for a pull
-request the live train or the spool already holds (ALREADY), runs
+request the live train or the spool already holds (ALREADY: `already_held`,
+the one rule the drain applies too, over `queue.seen.json`), runs
 `Train.admit_add` (ADD REFUSED #<pr> <rule>: <why>), then spools the entry for
 the live train or, with none, starts one over it. A batch that stops ends the
 train (NOT RUN lines); spooled entries stay for the next. One train per state
@@ -674,6 +675,12 @@ STALE_VERDICT_CARRY = "STALE-VERDICT-CARRY"  # the verdict sha no longer carries
 ROW_MISSING = "ROW-MISSING"          # no delivery row in the three-dot diff
 BOT_ROUTE = "bot-head"               # batch: a GITHUB_TOKEN tip goes serial, where its recarry cures it
 MAIN_MOVED = "MAIN-MOVED"            # origin/main moved under a settled head or a proof
+BRANCH_POLICY = "BRANCH-POLICY"      # every merge attempt refused by GitHub's base-branch policy
+BRANCH_POLICY_SAID = re.compile(r"base branch policy prohibits the merge", re.I)
+# A skip of these classes is the environment's, not the entry's: the train's own
+# worktree holder (P189) or GitHub's branch policy at the last merge attempt
+# (P291). Re-added at the SAME verdict head, such an entry is admitted again.
+READMIT_SAME_VERDICT = (HOLDER, BRANCH_POLICY)
 
 
 class MainMoved(Stop):
@@ -791,7 +798,8 @@ def budget_fixture(budgets: "dict | None", argv: list[str], base: str) -> "tuple
 QUEUE_LOCK = "queue.lock"            # the flock every reader and writer below takes
 QUEUE_OPEN = "queue.open"            # the live train's pid: the queue accepts adds
 QUEUE_SPOOL = "queue-add.jsonl"      # one entry per line, appended by `add`
-QUEUE_PENDING = "queue.pending.json"  # the PRs in the running and later batches: `add`'s idempotence
+QUEUE_PENDING = "queue.pending.json"  # the PRs still to run (running and later batches), read by review_packet
+QUEUE_SEEN = "queue.seen.json"        # every PR the live train held: {pr: {verdict, state[, class]}}
 ADD_SETTLE_SECONDS = 10              # how long `add` waits on a train.sh starting, or one closing
 
 
@@ -872,6 +880,55 @@ def spool_append(state: Path, entry: dict) -> None:
         fh.write(json.dumps(entry, sort_keys=True) + "\n")
 
 
+def already_held(pr: int, verdict: "str | None", seen: dict, spooled: "set[int]") -> "str | None":
+    """THE admission rule `add` (`train_add`) and the drain (`Train.queue_take`)
+    both apply (P129, P189, P291): None admits <pr> at <verdict>, else why it
+    is ALREADY held. `seen` is the live train's record (QUEUE_SEEN): per pull
+    request the verdict it entered at and its state -- `pending` (still to run:
+    the running or a later batch), `merged`, `ran` (a batch completed it
+    without a merge, a rehearsal) or `skipped` (with the skip class). Held: a
+    spooled entry, a pending one, one this train merged or ran, and one it
+    skipped at this same verdict -- unless that skip's class is the
+    environment's (READMIT_SAME_VERDICT). A skipped entry at a new verdict is
+    admitted: a skip is not pending."""
+    if pr in spooled:
+        return "spooled for the live train's next batch"
+    rec = seen.get(str(pr))
+    if rec is None:
+        return None
+    state = rec.get("state")
+    if state == "pending":
+        return "still to run in this train"
+    if state == "skipped":
+        if str(verdict or "") != str(rec.get("verdict") or ""):
+            return None
+        if rec.get("class") in READMIT_SAME_VERDICT:
+            return None
+        return (f"skipped by this train at this same verdict {str(verdict)[:12]}"
+                + (f" [{rec['class']}]" if rec.get("class") else "") + "; a new verdict head re-admits it")
+    return "merged by this train" if state == "merged" else "run by this train"
+
+
+def queue_seen_read(state: Path) -> dict:
+    """The live train's QUEUE_SEEN; call it under the lock. A train started
+    before the file existed wrote QUEUE_PENDING only: read those as pending."""
+    try:
+        return json.loads((state / QUEUE_SEEN).read_text())
+    except (OSError, ValueError):
+        pass
+    try:
+        return {str(int(n)): {"state": "pending"} for n in json.loads((state / QUEUE_PENDING).read_text())}
+    except (OSError, ValueError, TypeError):
+        return {}
+
+
+def queue_seen_write(state: Path, seen: dict) -> None:
+    """QUEUE_SEEN and the QUEUE_PENDING view derived from it; call it under the lock."""
+    (state / QUEUE_SEEN).write_text(json.dumps(seen, indent=2, sort_keys=True) + "\n")
+    (state / QUEUE_PENDING).write_text(
+        json.dumps(sorted(int(n) for n, r in seen.items() if r.get("state") == "pending")) + "\n")
+
+
 def launch_detached(argv: "list[str]", state: Path) -> "tuple[int, str]":
     """Start train.sh detached (its own session: `add` returns, the train goes
     on) and wait up to ADD_SETTLE_SECONDS for it to take train.pid. (pid, "")
@@ -895,7 +952,8 @@ def train_add(t: "Train", item: dict, train_argv: "list[str]", launch=launch_det
     """`add`: load one verdicted pull request into the state dir's live train,
     or start that train. Under QUEUE_LOCK, in order: a pull request already in
     the live train's running or later batches, or already spooled, is a no-op
-    (`ALREADY`, rc 0 -- a backstop sweep calls this safely); `Train.admit_add`
+    (`ALREADY`, rc 0 -- a backstop sweep calls this safely; `already_held`, the
+    drain's rule too, so the two never disagree); `Train.admit_add`
     must pass (`ADD REFUSED #<pr> <rule>: <why>`, rc 1); a live train gets the
     entry in its spool, which it drains as its NEXT batch (`ADDED`); with none,
     `<train_argv> --queue <file>` starts one over the entry (and anything a
@@ -907,12 +965,10 @@ def train_add(t: "Train", item: dict, train_argv: "list[str]", launch=launch_det
         live = read_pid(t.state / QUEUE_OPEN)
         live = live if pid_alive(live) else None
         spooled, _bad = spool_read(t.state)
-        try:
-            pending = set(json.loads((t.state / QUEUE_PENDING).read_text())) if live else set()
-        except (OSError, ValueError):
-            pending = set()
-        if str(pr).isdigit() and int(pr) in pending | {int(e["pr"]) for e in spooled}:
-            t.log(f"ALREADY #{pr}: queued in the {'live train (pid %d)' % live if live else 'spool'}; nothing added")
+        held = (already_held(int(pr), item.get("verdict"), queue_seen_read(t.state) if live else {},
+                             {int(e["pr"]) for e in spooled}) if str(pr).isdigit() else None)
+        if held:
+            t.log(f"ALREADY #{pr}: {held} ({'live train pid %d' % live if live else 'no live train'}); nothing added")
             return 0
         why = t.admit_add(item)
         if why:
@@ -943,7 +999,8 @@ def train_add(t: "Train", item: dict, train_argv: "list[str]", launch=launch_det
             t.log(f"ADD REFUSED #{pr} start: train.sh did not start ({why})")
             return 2
         (t.state / QUEUE_OPEN).write_text(f"{pid}\n")
-        (t.state / QUEUE_PENDING).write_text(json.dumps(sorted(int(e["pr"]) for e in queue)) + "\n")
+        queue_seen_write(t.state, {str(int(e["pr"])): {"verdict": e.get("verdict"), "state": "pending"}
+                                   for e in queue})
         t.log(f"STARTED train.sh pid {pid} over {' '.join('#%d' % int(e['pr']) for e in queue)}; queue {qf.name}")
         return 0
 
@@ -1889,6 +1946,7 @@ class Train:
                           "--jq", '"\\(.state) \\(.mergeCommit.oid)"')
             if st.startswith("MERGED"):
                 self.log(f"#{pr} {st}")
+                self.seen_mark(pr, "merged")
                 break
             # Every refusal is logged with GitHub's own words (train-b5, #2290:
             # eight silent attempts, "not merged" and no reason). One that says
@@ -1897,7 +1955,8 @@ class Train:
             if BASE_MOVED.search(said):
                 raise MainMoved("merge", f"GitHub refused the merge because the base moved: {said}")
         else:
-            raise Stop("merge", f"not merged after {self.merge_tries} attempts; the last refusal: {said}")
+            raise Stop("merge", f"not merged after {self.merge_tries} attempts; the last refusal: {said}",
+                       cls=BRANCH_POLICY if BRANCH_POLICY_SAID.search(said) else None)
         owner, name = self.repo.split("/")
         q = ('query={repository(owner:"%s",name:"%s"){pullRequest(number:%d){closingIssuesReferences(first:10)'
              "{nodes{number state}}}}}" % (owner, name, pr))
@@ -2046,7 +2105,15 @@ class Train:
                 keep.append(item)
                 continue
             self.log(f"PARK #{item.get('pr')} {step}: {why}")
-            self.skipped.append({"pr": item.get("pr"), "phase": "pre-flight", "reason": f"{step}: {why}"})
+            row = {"pr": item.get("pr"), "phase": "pre-flight", "reason": f"{step}: {why}",
+                   "verdict": item.get("verdict")}
+            # PreFlight parks at `recarry` for one cause, the worktree holder
+            # (`worktree_holder`): the environment's, so P189's exception reaches it.
+            cls = HOLDER if step == "recarry" else None
+            if cls:
+                row["class"] = cls
+            self.skipped.append(row)
+            self.seen_mark(item.get("pr"), "skipped", cls)
         (self.state / "skipped.json").write_text(json.dumps(self.skipped, indent=2) + "\n")
         self.log(f"PRE-FLIGHT: {len(keep)} of {len(queue)} admitted")
         return keep
@@ -2606,10 +2673,27 @@ class Train:
         brackets when the shape is a known one) and collected for skipped.json.
         A red main is never skippable: the caller re-raises it."""
         self.log(f"SKIP #{pr} {phase}: " + (f"[{cls}] {why}" if cls else why))
-        row = {"pr": pr, "phase": phase, "reason": why}
+        row = {"pr": pr, "phase": phase, "reason": why,
+               "verdict": (getattr(self, "_seen", {}).get(str(pr)) or {}).get("verdict")}
         if cls:
             row["class"] = cls
         self.skipped.append(row)
+        self.seen_mark(pr, "skipped", cls)  # out of the pending layer: a skip is not still to run (P189)
+
+    def seen_mark(self, pr, state: str, cls: "str | None" = None) -> None:
+        """Record <pr>'s new state in the live train's QUEUE_SEEN (and its
+        QUEUE_PENDING view) under the lock; a no-op outside `batch`'s queue."""
+        rec = getattr(self, "_seen", {}).get(str(pr))
+        q = getattr(self, "_queue", None)
+        if rec is None or not q or q["closed"]:
+            return
+        rec["state"] = state
+        rec.pop("class", None)
+        if cls:
+            rec["class"] = cls
+        with queue_lock(self.state):
+            if read_pid(self.state / QUEUE_OPEN) == os.getpid():
+                queue_seen_write(self.state, self._seen)
 
     def skip_report(self, total: int) -> None:
         """`--skip-bad`'s closing report: the skipped list under the state dir
@@ -2630,7 +2714,6 @@ class Train:
             self.log(f"TRAIN STOPPED {e}")
             return 1
         self.skipped = []
-        seen = {int(e["pr"]) for b in batches for e in b}
         total = 0
         self._queue = {"batches": batches, "next": 0, "closed": False}
         try:
@@ -2646,7 +2729,10 @@ class Train:
                     self.hold_release()
                 if stopped:
                     return 1
-                if not self.queue_take(batches, k + 1, seen):
+                for e in batches[k]:  # neither merged nor skipped: ran (a rehearsal), no longer pending
+                    if self._seen.get(str(int(e["pr"])), {}).get("state") == "pending":
+                        self.seen_mark(int(e["pr"]), "ran")
+                if not self.queue_take(batches, k + 1):
                     self.log("TRAIN DONE")
                     return 1 if self.skipped else 0
                 self.log(f"BATCH DONE {name}: {len(batches) - k - 1} more batch(es) on this train, next "
@@ -2663,17 +2749,16 @@ class Train:
             if held not in (None, os.getpid(), os.getppid()) and pid_alive(held):
                 raise Stop("queue", f"a live train (pid {held}) holds {self.state / QUEUE_OPEN}; one train per state dir")
             (self.state / QUEUE_OPEN).write_text(f"{os.getpid()}\n")
-            self._queue_pending(batches)
-
-    def _queue_pending(self, batches: "list[list[dict]]") -> None:
-        (self.state / QUEUE_PENDING).write_text(
-            json.dumps(sorted(int(e["pr"]) for b in batches for e in b)) + "\n")
+            self._seen = {str(int(e["pr"])): {"verdict": e.get("verdict"), "state": "pending"}
+                          for b in batches for e in b}
+            queue_seen_write(self.state, self._seen)
 
-    def queue_take(self, batches: "list[list[dict]]", k: int, seen: "set[int]") -> bool:
+    def queue_take(self, batches: "list[list[dict]]", k: int) -> bool:
         """Between batches: drain the spool into ONE new batch after those still
-        to run (an entry this train already holds is logged ALREADY, never run
-        twice). True when batch <k> is there to run; False closes the queue in
-        the same locked step, so an add after it starts a train of its own."""
+        to run (an entry `already_held` -- the rule `add` applied -- is logged
+        ALREADY, never run twice). True when batch <k> is there to run; False
+        closes the queue in the same locked step, so an add after it starts a
+        train of its own."""
         with queue_lock(self.state):
             added, bad = spool_read(self.state)
             (self.state / QUEUE_SPOOL).unlink(missing_ok=True)
@@ -2681,19 +2766,20 @@ class Train:
                 self.log(f"ADD UNREADABLE (dropped): {ln[:160]}")
             fresh = []
             for e in added:
-                if int(e["pr"]) in seen:
-                    self.log(f"ALREADY #{e['pr']}: in this train already; not queued twice")
+                held = already_held(int(e["pr"]), e.get("verdict"), self._seen, set())
+                if held:
+                    self.log(f"ALREADY #{e['pr']}: {held}; not queued twice")
                     continue
-                seen.add(int(e["pr"]))
+                self._seen[str(int(e["pr"]))] = {"verdict": e.get("verdict"), "state": "pending"}
                 fresh.append(e)
             if fresh:
                 batches.append(fresh)
                 self.log(f"ADDED {' '.join('#%d' % int(e['pr']) for e in fresh)}: batch {len(batches)} of this train")
             if k >= len(batches):
-                (self.state / QUEUE_OPEN).unlink(missing_ok=True)
-                (self.state / QUEUE_PENDING).unlink(missing_ok=True)
+                for f in (QUEUE_OPEN, QUEUE_PENDING, QUEUE_SEEN):
+                    (self.state / f).unlink(missing_ok=True)
                 return False
-            self._queue_pending(batches[k:])
+            queue_seen_write(self.state, self._seen)
             return True
 
     def queue_close(self) -> None:
@@ -2707,8 +2793,8 @@ class Train:
         batches, k = q["batches"], q["next"]
         with queue_lock(self.state):
             if read_pid(self.state / QUEUE_OPEN) == os.getpid():
-                (self.state / QUEUE_OPEN).unlink(missing_ok=True)
-                (self.state / QUEUE_PENDING).unlink(missing_ok=True)
+                for f in (QUEUE_OPEN, QUEUE_PENDING, QUEUE_SEEN):
+                    (self.state / f).unlink(missing_ok=True)
             left, _bad = spool_read(self.state)
         for b in batches[k:]:
             self.log("NOT RUN " + " ".join("#%d" % int(e["pr"]) for e in b) + ": the train stopped before this batch")
@@ -2817,6 +2903,7 @@ class Train:
         self.hold_armed = True
         self.hold_refresh()  # before the sweep: the record beat waits for the batch
         self.branches: list[str] = []
+        mine = len(self.skipped)  # this batch's skips start here: an earlier batch's never filter a re-added entry
         try:
             mf = _fastpath()
             self.sweep_bots()  # before the base is read: a record PR merged now is under every proof
@@ -2852,7 +2939,7 @@ class Train:
                 self.run(["git", "fetch", "-q", "origin", self.base])
                 rb = self.git("rev-parse", f"origin/{self.base}")
                 # A bot-routed head still contains main now; it recarries at its turn.
-                todo = [a for a in serial if a["pr"] not in {s["pr"] for s in self.skipped}
+                todo = [a for a in serial if a["pr"] not in {s["pr"] for s in self.skipped[mine:]}
                         and BOT_ROUTE not in a["route"]]
                 self.log(f"OVERLAP: recarrying {', '.join('#%d' % a['pr'] for a in todo)} up front, "
                          "their pull_request runs fire together")
@@ -2927,7 +3014,7 @@ class Train:
                     recover = recover and phase != "post-merge"
                     self.skip(a["pr"], phase, s.why, s.cls)
             order = {int(item["pr"]): i for i, item in enumerate(queue)}
-            bad = {s["pr"] for s in self.skipped}
+            bad = {s["pr"] for s in self.skipped[mine:]}
             later = sorted([a for a in serial + dropped if a["pr"] not in bad], key=lambda a: order[a["pr"]])
             if lone and later and self.real:
                 # A red push run must point at one merge: the unproved one is graded alone.
@@ -4971,6 +5058,8 @@ def _batch_self_test(check) -> None:
                 return 0, "77 completed" if w["review_reads"] > w.get("review_pending", 0) else "77 in_progress"
             if argv[:3] == ["gh", "pr", "merge"]:
                 n, h = int(argv[3]), argv[-1]
+                if n in w.get("policy_refuse", ()):  # P291: GitHub's base-branch policy refuses this PR
+                    return 1, "the base branch policy prohibits the merge"
                 if w.get("review_reads", 0) <= w.get("review_pending", 0):  # base-branch policy: the run is not over
                     w["refused"] = w.get("refused", 0) + 1
                     return 1, "the base branch policy prohibits the merge"
@@ -5066,8 +5155,8 @@ def _batch_self_test(check) -> None:
             lines: list[str] = []
             t = Train("o/r", Path(d) / "state", mandate, "the orchestrator", ignore, 1, run=stub(w),
                       sleep=lambda s: (w.setdefault("slept", []).append(s), w.get("on_sleep", lambda: None)()),
-                      log=lines.append, polls=2, merge_tries=2,
-                      base=base, skip_bad=skip_bad, overlap=overlap, main_moved_tries=main_moved_tries, **opts)
+                      log=lambda ln: (lines.append(ln), w.get("on_log", lambda _ln: None)(ln)),
+                      polls=2, merge_tries=2, base=base, skip_bad=skip_bad, overlap=overlap, main_moved_tries=main_moved_tries, **opts)
             q = ([{"pr": n, "verdict": w["heads"][n]} for n in prs] if batches is None
                  else [[{"pr": n, "verdict": w["heads"][n]} for n in b] for b in batches])
             rc = t.batch(q, "t")
@@ -5624,10 +5713,142 @@ def _batch_self_test(check) -> None:
           w["rc"] == 0 and list(w["merged"]) == [1, 2, 3, 4]
           and "c.txt" not in w["proof_names"][0] and "d.txt" not in w["proof_names"][0]
           and [b for b, _ in w["pushed"]] == ["batch/t-1", "batch/t-b2-1"]
-          and any(ln == "ALREADY #1: in this train already; not queued twice" for ln in w["lines"])
+          and any(ln == "ALREADY #1: merged by this train; not queued twice" for ln in w["lines"])
           and any(ln == "ADDED #3 #4: batch 2 of this train" for ln in w["lines"])
           and not (w["state"] / QUEUE_OPEN).exists() and not (w["state"] / QUEUE_SPOOL).exists()
           and w["lines"][-1] == "TRAIN DONE")
+    # ONE ADMISSION RULE for `add` and the drain (P129 as amended by P189, P291):
+    # the field instance, batch 20261029-193537-b4 of train pid 34197. After
+    # `SKIP REPORT: 5 skipped of 10` the drain logged ALREADY for #2917, #2872
+    # and #2961, skipped earlier and re-added at new verdict heads, and #2970,
+    # skipped at its merge by GitHub's base-branch policy, was refused twice
+    # by `add` from the pending layer at its reviewed head. Replayed: batch 1
+    # skips #2 and #3 (red CI at their verdicts), batch 2 merges #4, skips #5
+    # at the merge (the branch policy) and #6 (red CI). Each re-add goes
+    # through the REAL train_add against the live train's state dir; its
+    # admit_add (the verdict/carry/row reads, tested in _add_self_test) is
+    # passed, so only the ALREADY layer is under test.
+    def readd(w, state):
+        def rehead(n):  # a new verdict head: one commit on the branch, its tree unchanged
+            h = w["heads"][n]
+            new = g(w["R"], "commit-tree", f"{h}^{{tree}}", "-p", h, "-m", f"fix {n}")[1]
+            g(w["R"], "update-ref", f"refs/heads/pr{n}", new)
+            w["heads"][n] = new
+
+        def add(n):
+            al: list[str] = []
+            ta = Train("o/r", state, None, "", (), 1, run=stub(w), log=al.append)
+            ta.admit_add = lambda item: None
+            rc = train_add(ta, {"pr": n, "verdict": w["heads"][n]}, ["true"], launch=lambda *a: (0, "no"))
+            w.setdefault("add_lines", []).extend(al)
+            return rc
+
+        def on_log(ln):
+            if ln.startswith("BATCH t-b2 "):  # #5 and #6 are in the live batch: refused, null control
+                w["live_rc"] = [add(5), add(6)]
+                w["live_lines"] = list(w.get("add_lines", []))
+            if ln.startswith("SKIP REPORT") and not w.get("readded"):
+                w["reports"] = w.get("reports", 0) + 1
+                if w["reports"] < 2:
+                    return
+                w["readded"] = True
+                rehead(2)
+                rehead(3)  # ... a GITHUB_TOKEN tip: batch 3 routes it serial, past the skipped filter
+                w["bot_heads"] = {w["heads"][3]: "ci: pin killed mutants"}
+                w["policy_refuse"].discard(5)  # the owner's approval landed; the head is unchanged
+                w["add_lines"] = []
+                w["re_rc"] = [add(n) for n in (2, 3, 5, 6, 4)]
+                with queue_lock(state):  # the drain's own null controls: past add, straight to the spool
+                    for n in (6, 4):
+                        spool_append(state, {"pr": n, "verdict": w["heads"][n]})
+        return on_log
+
+    six = {n: {f"f{n}.txt": f"{n}\n"} for n in range(1, 7)}
+
+    def b4_shape(w):
+        w["red"].update({w["heads"][2], w["heads"][3], w["heads"][6]})
+        w["policy_refuse"] = {5}
+        w["remerge"] = True
+        w["on_log"] = readd(w, w["state"])
+    w = go(six, base="main", batches=[[1, 2, 3], [4, 5, 6]], skip_bad=True, setup=b4_shape)
+    adds = w.get("add_lines", [])
+    said = lambda pfx: any(ln.startswith(pfx) for ln in w["lines"])  # noqa: E731
+    check("P291 batch-4 replay: entries this train skipped and re-added at new verdict heads (#2, #3), and a "
+          "merge skip by GitHub's branch policy re-added at its reviewed head (#5), are ADDED by `add` and "
+          "by the drain alike, and land in the next batch",
+          w.get("re_rc", [])[:3] == [0, 0, 0]
+          and [any(ln.startswith(f"ADDED #{n} to the live train") for ln in adds) for n in (2, 3, 5)] == [True] * 3
+          and said("ADDED #2 #3 #5: batch 3 of this train")
+          and not any(said(f"ALREADY #{n}:") for n in (2, 3, 5))
+          and sorted(w["merged"]) == [1, 2, 3, 4, 5] and said("BATCH t-b3 ")
+          and said("#3 serial: bot-head") and w.get("recarries") == [3])
+    check("P291 the merge skip carries its environment class: SKIP #5 merge: [BRANCH-POLICY], and "
+          "skipped.json's row names the class and the verdict it was skipped at",
+          said("SKIP #5 merge: [BRANCH-POLICY] not merged after")
+          and any(r["pr"] == 5 and r.get("class") == "BRANCH-POLICY" and r.get("verdict") for r in w["skip_json"] or []))
+    check("P189 null control: a ci-skipped entry re-added at the SAME verdict (#6), and an entry this train "
+          "merged (#4), are ALREADY on both sides -- `add` spools nothing, the drain runs neither",
+          [any(ln.startswith(f"ALREADY #{n}:") for ln in adds) for n in (6, 4)] == [True, True]
+          and said("ALREADY #6:") and said("ALREADY #4:") and 6 not in w["merged"])
+    check("null control: an entry still in the live batch (#5, #6 re-added as batch 2 starts) is ALREADY "
+          "from the pending layer, rc 0, nothing spooled",
+          w.get("live_rc") == [0, 0]
+          and [any(ln.startswith(f"ALREADY #{n}:") for ln in w.get("live_lines", [])) for n in (5, 6)] == [True, True]
+          and not any(ln.startswith("ADDED") for ln in w.get("live_lines", [])))
+    # P189's HOLDER arm, through BOTH callers of the one rule: the live train's
+    # record says #7 was skipped [HOLDER] (the train's own worktree holder) and
+    # #8 skipped by its CI, each at verdict V7. `add` at V7: #7 ADDED, #8
+    # ALREADY; the drain over both spooled: #7 joins batch 2, #8 ALREADY.
+    with tempfile.TemporaryDirectory() as d:
+        st, V7, hl = Path(d), "7" * 40, []
+        tt = Train("o/r", st, None, "", (), 1, run=lambda *a, **k: (0, ""), log=hl.append)
+        tt.admit_add = lambda item: None
+        (st / QUEUE_OPEN).write_text(f"{os.getpid()}\n")
+        tt._seen = {"7": {"verdict": V7, "state": "skipped", "class": HOLDER},
+                    "8": {"verdict": V7, "state": "skipped"}}
+        queue_seen_write(st, tt._seen)
+        add_rc = [train_add(tt, {"pr": n, "verdict": V7}, ["true"], launch=lambda *a: (0, "no")) for n in (7, 8)]
+        add_said = list(hl)
+        with queue_lock(st):
+            spool_append(st, {"pr": 8, "verdict": V7})
+        bs = [[{"pr": 1, "verdict": V7}]]
+        tt._queue = {"batches": bs, "next": 1, "closed": False}
+        more = tt.queue_take(bs, 1)
+        drain_said = hl[len(add_said):]
+    # ... and a pre-flight PARK at `recarry` (PreFlight's worktree holder) is
+    # that HOLDER skip, recorded with its class; a `carry` PARK has none.
+    class _PF:
+        def __init__(self, *a, **k):
+            pass
+
+        def entry(self, item):
+            return ("PARK", "recarry", "held by /other/wt") if item["pr"] == 7 else ("PARK", "carry", "CARRY: no")
+    with tempfile.TemporaryDirectory() as d:
+        pl: list[str] = []
+        tp = Train("o/r", Path(d), None, "", (), 1, run=lambda *a, **k: (0, ""), log=pl.append, pre_flight=True)
+        (Path(d) / QUEUE_OPEN).write_text(f"{os.getpid()}\n")
+        tp._queue = {"batches": [], "next": 0, "closed": False}
+        tp._seen = {"7": {"verdict": V7, "state": "pending"}, "8": {"verdict": V7, "state": "pending"}}
+        real_pf, sys.modules["queue_pre_flight"] = sys.modules.get("queue_pre_flight"), type(sys)("queue_pre_flight")
+        sys.modules["queue_pre_flight"].PreFlight = _PF
+        try:
+            kept = tp.preflight([{"pr": 7, "verdict": V7}, {"pr": 8, "verdict": V7}])
+        finally:
+            if real_pf is None:
+                sys.modules.pop("queue_pre_flight", None)
+            else:
+                sys.modules["queue_pre_flight"] = real_pf
+        rec = queue_seen_read(Path(d))
+    check("P189 HOLDER arm, pre-flight: a PARK at `recarry` (the worktree holder) is recorded skipped [HOLDER] "
+          "with its verdict, so a same-verdict re-add is admitted; a `carry` PARK is skipped with no class",
+          kept == [] and rec["7"] == {"verdict": V7, "state": "skipped", "class": HOLDER}
+          and rec["8"] == {"verdict": V7, "state": "skipped"}
+          and already_held(7, V7, rec, set()) is None and bool(already_held(8, V7, rec, set())))
+    check("P189 HOLDER arm: an entry skipped [HOLDER] and re-added at the SAME verdict is ADDED by `add` and "
+          "by the drain (batch 2), and a ci-skipped one at the same verdict is ALREADY on both sides",
+          add_rc == [0, 0] and add_said[0].startswith("ADDED #7") and add_said[1].startswith("ALREADY #8:")
+          and more and [int(e["pr"]) for e in bs[-1]] == [7] and "ADDED #7: batch 2 of this train" in drain_said
+          and any(ln.startswith("ALREADY #8:") for ln in drain_said))
     flat = go({1: {"a.txt": "A\n"}, 2: {"b.txt": "B\n"}})
     nested = go({1: {"a.txt": "A\n"}, 2: {"b.txt": "B\n"}}, batches=[[1, 2]])
     shas = lambda xs: [re.sub(r"\b[0-9a-f]{8,40}\b", "<sha>", x) for x in xs]  # noqa: E731

