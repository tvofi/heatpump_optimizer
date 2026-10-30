# Review packet #2992
head: e456ff01323580d4390f964483a17dbdb6cff5bf
base: 507a9ec264eb373b132248d752259254d8a9fa4d

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: pending
CodeQL id=124070639887 neutral
arch-score / arch-score id=124070275337 success
arm id=124070140142 skipped
budget-raise-gate / budget-raise-gate id=124070275365 success
cancel-superseded id=124070138053 success
codeql / Analyze (actions) id=124070275362 success
codeql / Analyze (javascript-typescript) id=124070275450 success
codeql / Analyze (python) id=124070275212 in_progress
governance / delivery-status id=124070275446 success
governance / delivery-status-publish id=124070277743 skipped
governance / env-matrix id=124070275232 in_progress
governance / instrument-self-tests id=124070275423 in_progress
governance / policy-docs id=124070275387 success
governance / record id=124070277192 skipped
governance / wave-script id=124070275283 success
hassfest / hassfest id=124070275113 success
kernel-points id=124070277767 skipped
prelude id=124070138170 success
refresh id=124070137941 success
tests / arch-instrument id=124070644062 success
tests / briefs id=124070275374 success
tests / browser id=124070644105 in_progress
tests / closure-scope id=124070275420 success
tests / closures id=124070644085 in_progress
tests / coverage id=124070643944 in_progress
tests / fast (3.14) id=124070643947 in_progress
tests / mutation id=124070275451 success
tests / mutation-autofix id=124070826968 skipped
tests / mutation-pins id=124070824654 skipped
tests / nightly-ha id=124070646723 skipped
tests / nightly-status id=124070275348 success
tests / replay id=124070647718 skipped
tests / typing id=124070643946 in_progress
validate / validate-hacs id=124070275266 success

## Refusals
none

## Advisories
none

## carry_audit at the head
NOTE body item d3e283f4: R10-TRAIN-OVERLAP-GRADE
NOTE body item 0d432c40: R10-TRAIN-OVERLAP-GRADE
NOTE body item 57d5cfbe: R10-TRAIN-OVERLAP-GRADE
NOTE body item c61ba6ff: dismissed:no finder harness exists for instrument carries; the fixtures are the measurement
CARRY-AUDIT: 4 finding item(s): 4 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
ok         python3 tools/audit/seat/merge_train.py --self-test
             `tools/audit/seat/merge_train.py` is in the tree at this head
  unverified git show 89ccf732...:tools/audit/seat/merge_train.py > tools/audit/seat/_base_merge_train.py
             `git show` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  unverified git diff 89ccf732... HEAD -- tools/audit/seat/merge_train.py | grep -c '^+.*check('
             `git diff` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  ok         python3 tests/closure.py select --diff 89ccf73266a8dcfc0e8d4f45ad6583b0cb622db6 --workdir "$D"
             `tests/closure.py` is in the tree at this head
  ok         tests/entities.py
             `tests/entities.py` is in the tree at this head
  ok         PYTHONPATH=tests/hastub python3 tests/entities.py
             `tests/entities.py` is in the tree at this head
  ok         python3 tests/env_drift.py --claims-only 89ccf732...
             `tests/env_drift.py` is in the tree at this head
  ok         python3 tests/closure.py selftest
             `tests/closure.py` is in the tree at this head
  ok         python3 tests/layout.py
             `tests/layout.py` is in the tree at this head
  ok         python3 tests/harness_headers.py
             `tests/harness_headers.py` is in the tree at this head
  ok         python3 tests/structure.py
             `tests/structure.py` is in the tree at this head
  ok         python3 tools/audit/archscore/score.py --diff 89ccf73266a8dcfc0e8d4f45ad6583b0cb622db6
             `tools/audit/archscore/score.py` is in the tree at this head

FIGURES: 10 resolved, 2 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
none

## Three-dot diff
diff --git a/dev/programme/delivery/2992.md b/dev/programme/delivery/2992.md
new file mode 100644
index 000000000..6480f475a
--- /dev/null
+++ b/dev/programme/delivery/2992.md
@@ -0,0 +1 @@
+- [#2992](https://github.com/tvofi/heatpump_optimizer/pull/2992) — **open**, R10-TRAIN-OVERLAP-GRADE part 3: park a base-policy refusal with its read reason; record-PR sweep on refusal and after a critical-path entry (R10-TRAIN-OVERLAP-GRADE)
diff --git a/tools/audit/seat/instruments/merge_train.py.md b/tools/audit/seat/instruments/merge_train.py.md
index fe97947bf..4eaeaddca 100644
--- a/tools/audit/seat/instruments/merge_train.py.md
+++ b/tools/audit/seat/instruments/merge_train.py.md
@@ -15,10 +15,13 @@
   on the new main. An owner approval GitHub already holds at the live head is
   the owner's, with nothing re-posted (GitHub re-anchors one across a clean
   base merge: #2209). `--bot-prs` merges the open record/autofix pull request
-  in the train's own sequence behind record_row.py's identical guard;
-  `--pre-flight` runs `queue_pre_flight.py` first and PARKs a failing entry;
-  `--free-holders` detaches a clean, pushed holder worktree. Every refused
-  merge attempt is logged in GitHub's words; the recarry worktrees a run made
+  in the train's own sequence behind record_row.py's identical guard, after a
+  critical-path entry rather than before it, and once more after a refused
+  merge attempt; `--pre-flight` runs `queue_pre_flight.py` first and PARKs a
+  failing entry; `--free-holders` detaches a clean holder worktree with no
+  commit origin lacks. Every refused merge attempt is logged in GitHub's
+  words, and a base-branch policy refusal parks the entry with the reason
+  read from the merge state; the recarry worktrees a run made
   are removed before its closing line. Every `gh api` GET and `gh pr view`
   it or `queue_pre_flight.py` makes is under `gh_read.py`'s read rule, each
   settle logged.
diff --git a/tools/audit/seat/merge_train.py b/tools/audit/seat/merge_train.py
index c1998b076..eb24a8c17 100644
--- a/tools/audit/seat/merge_train.py
+++ b/tools/audit/seat/merge_train.py
@@ -90,7 +90,11 @@ later pull request would be graded against a `main` the refused one never joined
      `--match-head-commit` (retried; `main` re-checked before each attempt;
      every refusal logged in GitHub's words, a base-moved one -- or, serially,
      every attempt refused with main moved past the head -- recovered as a
-     moved main), the closing-issue read-back, and `worktree_gc.sh`. The
+     moved main; a base-branch policy refusal is diagnosed from the merge
+     state, review decision and check rollup and PARKS the entry
+     [BRANCH-POLICY] with that reason unless a required context is still
+     pending, a missing approval first offered to --approval-carry), the
+     closing-issue read-back, and `worktree_gc.sh`. The
      recarry worktrees a run made are removed before its closing line.
 
 It prints one line per step and ends `TRAIN DONE` or `TRAIN STOPPED #<pr> <step>:
@@ -245,13 +249,19 @@ merge bot PRs automatically"; run and batch):
       sequence (before the batch's base is read, before each recarry), behind
       record_row.py's identical `--automerge-check --require-green` guard at
       its head and --match-head-commit; a refusal or a pending check never
-      merges it and never stops the train. Its CI beat still merges one the
-      train has not taken; the recovery above answers that move.
+      merges it and never stops the train; GitHub's refusal is named in the
+      BOT line. A refused merge attempt (not base-moved) sweeps once more, and
+      a record PR merged there recarries the entry by the recovery above. A
+      critical-path entry (roster_lib; unread = none) skips the sweep before
+      its recarry, or before a batch holding it reads its base, and the sweep
+      runs after its merge(s). Its CI beat still merges one the train has not
+      taken; the recovery above answers that move.
   --pre-flight -- queue_pre_flight.py's reads first; a PARK or FAIL entry is
       left out (`PARK #<pr>` line, skipped.json, rc 1) instead of stopping the
       train at its turn.
   --free-holders -- a recarry branch checked out in another worktree that is
-      clean (no untracked file) with HEAD at origin/<branch> is detached
+      clean (no untracked file) with HEAD at origin/<branch> or an ancestor of
+      it (no commit origin lacks) is detached
       (`git -C <holder> switch <branch>` restores it); anything else is the
       HOLDER stop, its reason appended.
 """
@@ -679,6 +689,9 @@ BOT_ROUTE = "bot-head"               # batch: a GITHUB_TOKEN tip goes serial, wh
 MAIN_MOVED = "MAIN-MOVED"            # origin/main moved under a settled head or a proof
 BRANCH_POLICY = "BRANCH-POLICY"      # every merge attempt refused by GitHub's base-branch policy
 BRANCH_POLICY_SAID = re.compile(r"base branch policy prohibits the merge", re.I)
+# A required context's statusCheckRollup reading (a CheckRun's conclusion or a
+# StatusContext's state) that holds a policy refusal for good: the car parks.
+POLICY_RED = ("FAILURE", "CANCELLED", "TIMED_OUT", "ACTION_REQUIRED", "STARTUP_FAILURE", "STALE", "ERROR")
 # A skip of these classes is the environment's, not the entry's: the train's own
 # worktree holder (P189) or GitHub's branch policy at the last merge attempt
 # (P291). Re-added at the SAME verdict head, such an entry is admitted again.
@@ -1014,7 +1027,7 @@ class Train:
                  skip_bad: bool = False, overlap: bool = False,
                  approval_carry: bool = False, main_moved_tries: int = 0,
                  bot_prs: bool = False, pre_flight: bool = False,
-                 free_holders: bool = False,
+                 free_holders: bool = False, critical=None,
                  clock: "callable" = time.monotonic, wall: "callable" = time.time) -> None:
         self.repo, self.state, self.mandate, self.role = repo, state, mandate, role
         if base != "main" and not base.startswith("batch/"):
@@ -1042,6 +1055,10 @@ class Train:
         # today's train; the CLI's --main-moved-tries defaults to MAIN_MOVED_TRIES.
         self.main_moved_tries, self.bot_prs = main_moved_tries, bot_prs
         self.pre_flight, self.free_holders = pre_flight, free_holders
+        # P289: is an entry on the critical path (item -> bool); the roster's
+        # reading by default, a fixture's in the self-test.
+        self.critical = critical or self._critical
+        self.cp_read: "tuple[dict, set] | None" = None  # (roster, critical ids), read once per run
         self.skipped: list[dict] = []
         self.approved: dict[int, str] = {}  # {pr: head} this run approved (P86: never twice at one head)
         self.made_wts: list[Path] = []  # recarry worktrees THIS run created (release_worktrees)
@@ -1165,17 +1182,21 @@ class Train:
     def freeable(self, path: str, br: str) -> "str | None":
         """None when the worktree at <path> holding <br> can be detached with
         nothing lost -- no change and no untracked file (`status --porcelain`
-        empty: an untracked file is somebody's claim), and HEAD exactly
-        origin/<br>'s tip, so the branch's whole state is on the remote --
-        else the reason it cannot. Reads only."""
+        empty: an untracked file is somebody's claim), and HEAD origin/<br>'s
+        tip or an ancestor of it, so every commit it holds is on the remote
+        (P184: s41 refused 45d08312, an ancestor of origin's 8a133f39) --
+        else the reason it cannot. Keyed on commits, never a path pattern.
+        Reads only."""
         code, st = self.run(["git", "-C", path, "status", "--porcelain"])
         if code or st.strip():
             return "it has uncommitted or untracked files" if not code else "its status cannot be read"
         self.run(["git", "fetch", "-q", "origin", br])
         here = self.run(["git", "-C", path, "rev-parse", "HEAD"])[1].strip()
         there = self.run(["git", "rev-parse", f"origin/{br}"])[1].strip()
-        if not is_sha(here) or here != there:
-            return f"its HEAD {here[:8]} is not origin/{br} {there[:8]} (unpushed work)"
+        if not (is_sha(here) and is_sha(there)):
+            return f"its HEAD {here[:8]} or origin/{br} {there[:8]} cannot be read (unpushed work unknown)"
+        if here != there and not self.ok("git", "-C", path, "merge-base", "--is-ancestor", here, there):
+            return f"its HEAD {here[:8]} has commits origin does not have (origin/{br} is {there[:8]})"
         return None
 
     def free_holder(self, pr: int, wt: Path, br: str) -> None:
@@ -1189,7 +1210,7 @@ class Train:
             "no worktree holds it" if holder is None else self.freeable(holder, br))
         if why is None and self.ok("git", "-C", holder, "checkout", "-q", "--detach") \
                 and self.ok("git", "worktree", "add", "-q", "-B", br, str(wt), f"origin/{br}"):
-            self.log(f"#{pr} recarry [HOLDER] freed: {holder} held {br}, clean at origin/{br}; "
+            self.log(f"#{pr} recarry [HOLDER] freed: {holder} held {br}, clean, nothing origin/{br} lacks; "
                      f"detached it (restore: git -C {holder} switch {br})")
             return
         s = self.holder_refusal(wt, br)
@@ -1205,7 +1226,7 @@ class Train:
         item.setdefault("carried_from", h)
         item.setdefault("carried_chain", []).append(h)
 
-    def sweep_bots(self) -> None:
+    def sweep_bots(self) -> "int | None":
         """`--bot-prs`: merge the open record/autofix pull request NOW, in the
         train's own sequence, rather than let its CI beat merge it under a head
         the train has settled. The guard is record_row.py's own, the identical
@@ -1214,33 +1235,58 @@ class Train:
         ruleset still gates it (the approver App's review is the beat's to
         post). Nothing here stops the train: an unreadable lookup, a guard
         refusal (never merged), a pending check (left for the next sweep or
-        the beat) and a merge GitHub refuses are logged as BOT lines."""
+        the beat) and a merge GitHub refuses are logged as BOT lines, a
+        refusal with `gh pr merge`'s last output line (P231). The record PR's
+        number when it merged, else None."""
         if not (self.bot_prs and self.real):
-            return
-        rr = [sys.executable, "-I", str(ROOT / "tools/audit/seat/record_row.py"), "--repo", self.repo]
+            return None
+        rr =[sys.executable, "-I", str(ROOT / "tools/audit/seat/record_row.py"), "--repo", self.repo]
         if not os.environ.get("GH_TOKEN"):  # record_row reads its token from the env, never argv
             code, tok = self.run(["gh", "auth", "token"])
             if code or not tok.strip():
                 self.log("BOT: no gh token to read the record pull request with; not swept")
-                return
+                return None
             os.environ["GH_TOKEN"] = tok.strip()
         code, o = self.run([*rr, "--find-open", "--owner", self.repo.split("/")[0]])
         n = (o.strip().splitlines() or [""])[-1].strip()
         if code or not n.isdigit():
             self.log(f"BOT: the open record pull request could not be looked up: {o.strip()[-160:]}")
-            return
+            return None
         if n == "0":
-            return
+            return None
         h = self.head(int(n))
         code, o = self.run([*rr, "--automerge-check", "--require-green", "--pr", n, "--head", h])
         last = (o.strip().splitlines() or ["(no output)"])[-1][:200]
         if code:
             self.log(f"BOT #{n} {'pending' if code == 3 else 'refused by the guard'} at {h[:8]}: {last}; not merged")
-            return
-        self.run(["gh", "pr", "merge", n, "--repo", self.repo, "--merge", "--match-head-commit", h])
+            return None
+        _, said = self.run(["gh", "pr", "merge", n, "--repo", self.repo, "--merge", "--match-head-commit", h])
         st = self.out("gh", "pr", "view", n, "--repo", self.repo, "--json", "state,mergeCommit",
                       "--jq", '"\\(.state) \\(.mergeCommit.oid)"')
-        self.log(f"BOT #{n} {st}" if st.startswith("MERGED") else f"BOT #{n} not merged at {h[:8]} ({st[:80]})")
+        if st.startswith("MERGED"):
+            self.log(f"BOT #{n} {st}")
+            return int(n)
+        said = next((ln.strip() for ln in reversed(said.splitlines()) if ln.strip()), "(no output)")
+        self.log(f"BOT #{n} not merged at {h[:8]} ({st[:80]}) refused: {said[:200]}")
+        return None
+
+    def _critical(self, item: dict) -> bool:
+        """P289: is <item>'s group on the critical path -- its branch mapped
+        by roster_lib.group_for_branch, the path read by critical_path_groups,
+        both at the roster's reader ref, once per run. Anything unread is
+        nothing critical: today's order, the record PR first."""
+        try:
+            import roster_lib
+            if self.cp_read is None:
+                self.cp_read = ({}, set())  # first: a read that raises is not retried per entry
+                ref = roster_lib.reader_ref(str(ROOT), None)
+                self.cp_read = (roster_lib.show_roster(str(ROOT), ref),
+                                roster_lib.critical_path_groups(str(ROOT), ref) or set())
+            roster, crit = self.cp_read
+            gid = roster_lib.group_for_branch(roster, item.get("branch") or "")
+            return bool(gid) and roster_lib.norm_group(gid) in crit
+        except Exception:
+            return False
 
     def carry_refusal(self, pr: int, verdict: str, h: str, o: str) -> Stop:
         """The `--carry` refusal, classified when its shape is the known one:
@@ -1598,30 +1644,36 @@ class Train:
         an admission's cached answer, `mandate_state`'s own rules. h0 is any
         head this invocation's recarries moved through (`carried_chain`: a
         main-moved recovery recarries more than once), the one the approval
-        names; the delta is read from it."""
+        names; the delta is read from it. Each None leaves its reason in
+        item["carry_refused"], which a policy park names."""
+        def no(why: str) -> None:
+            item["carry_refused"] = why
         if not self.approval_carry or not self.mandate:
-            return None
+            return no("--approval-carry or --mandate is not given")
         chain = [c for c in item.get("carried_chain") or [item.get("carried_from")] if is_sha(c or "") and c != h]
         if not chain:
-            return None
+            return no("this run's recarry did not move the head")
         try:
             prior, cid = self._owner_approval_at(pr, chain)
             if prior is None:
-                return None
+                return no("no owner APPROVED review citing one mandate sits at a head this run's recarry "
+                          "moved off (an App or agent review carries nothing)")
             h0 = prior["commit_id"]
             code, out = self.run(["git", "diff", "--no-renames", "--name-only", h0, h])
             if code:
                 raise Stop("approve", f"the recarry delta {h0[:12]}..{h[:12]} could not be "
                            "read: " + out.strip()[-160:])
-            if [f for f in out.split() if f in files]:
-                return None  # a branch-own file moved: a resolution, and a resolution re-reviews
+            own = [f for f in out.split() if f in files]
+            if own:  # a branch-own file moved: a resolution, and a resolution re-reviews
+                return no(f"the recarry delta {h0[:8]}..{h[:8]} names branch-own {', '.join(own[:4])} "
+                          "(a conflict resolution re-reviews)")
             g = _mandate_gate()
             now = datetime.datetime.now(datetime.timezone.utc)
             comment, thread = self._mandate_read(cid)  # fresh, at the merge: never admission's read
-            live, _why = g.mandate_state(cid, comment, thread, now,
-                                         now.strftime("%Y-%m-%dT%H:%M:%SZ"), "merge")
+            live, why = g.mandate_state(cid, comment, thread, now,
+                                        now.strftime("%Y-%m-%dT%H:%M:%SZ"), "merge")
             if not live:
-                return None
+                return no(f"mandate {cid} is not in force at the merge: {why}")
         except Stop:
             raise
         except Exception as e:  # fail closed: an unread carry grants nothing
@@ -1750,7 +1802,13 @@ class Train:
         pr, v = int(item["pr"]), item["verdict"]
         if not is_sha(v):
             raise Stop("queue", f"verdict '{v}' is not a 40-hex sha")
-        self.sweep_bots()  # a record PR merged now is inside this recarry, not under it
+        if self.bot_prs and self.critical(item):
+            # P289 (tvofi, 2026-10-29): critical-path entries jump the record
+            # step; `serial` sweeps after this entry's merge instead.
+            item["sweep_after"] = True
+            self.log(f"#{pr} critical path: the record sweep waits for its merge")
+        else:
+            self.sweep_bots()  # a record PR merged now is inside this recarry, not under it
         h = self.head(pr)
         if not is_sha(h):
             raise Stop("head", f"could not read the head: {h[:120]}")
@@ -1810,21 +1868,25 @@ class Train:
             raise self.bot_refusal(pr, h, bot)
         return h
 
-    def one(self, item: dict, req: "list[str] | None" = None) -> None:
+    def one(self, item: dict) -> None:
         self.hold_refresh()  # per item: a long item must not age the hold stale
-        req = req if req is not None else self.required()
-        self.serial(item, self.recarry(item), None, req)
+        self.serial(item, self.recarry(item), None)
 
-    def serial(self, item: dict, h: str, rb: "str | None", req: "list[str] | None") -> None:
+    def serial(self, item: dict, h: str, rb: "str | None") -> None:
         """`at_head`, recovering a MainMoved up to --main-moved-tries times: a
         foreign merge moved main under the settled head (step 4, or the guard
         before a merge), so the entry is re-carried onto the new main and every
         step from the CI wait on runs again at the new head -- the carry, the
         approval and --match-head-commit all re-read there. Past the bound, the
-        stop is today's."""
+        stop is today's. The head wait judges the contexts a pull request's
+        head carries (P34), read here, so no caller can hand it main's set."""
+        req = self.required(pr_head=True)
         for n in range(self.main_moved_tries + 1):
             try:
-                return self.at_head(item, h, rb, req)
+                self.at_head(item, h, rb, req)
+                if item.pop("sweep_after", False):
+                    self.sweep_bots()  # P289: the record PR merges after the critical-path entry
+                return
             except MainMoved as s:
                 if n == self.main_moved_tries:
                     if n:
@@ -1833,8 +1895,12 @@ class Train:
                 self.log(f"#{item['pr']} [MAIN-MOVED] {s.step}: {s.why}; recarry "
                          f"{n + 1}/{self.main_moved_tries} onto the new main, then CI again")
                 h, rb = self.recarry(item), None
+            except Stop:
+                if item.pop("sweep_after", False):
+                    self.sweep_bots()  # the entry stopped: the record PR waits no longer
+                raise
 
-    def one_overlap(self, item: dict, req: "list[str] | None") -> None:
+    def one_overlap(self, item: dict) -> None:
         """`--overlap`'s serial step for one entry: its head was re-carried UP
         FRONT (a dropped entry, routed only by the proof, re-carries here at
         its turn), so its pull_request runs fired with the others' and this
@@ -1842,7 +1908,7 @@ class Train:
         caller lands entries one at a time, an earlier still-pending entry
         never jumped by a later eligible one."""
         h = item.get("rc_head") or self.recarry(item)
-        self.serial(item, h, item.get("rc_base"), req)
+        self.serial(item, h, item.get("rc_base"))
 
     def at_head(self, item: dict, h: str, rb: "str | None", req: "list[str] | None") -> None:
         """Steps 2-7 at a settled head: wait its CI, carry the verdict, land
@@ -1934,16 +2000,16 @@ class Train:
         if re.search(r"(?m)^\s*REFUSE\b", pf) or not re.search(r"(?m)^\s*clean\b", pf):
             raise Stop("preflight", "the title did not pass preflight.sh: " + pf.strip()[-200:])
         self.unstale(h)
-        said = "(no output)"
+        said, swept, carried = "(no output)", False, False
         for k in range(1, self.merge_tries + 1):
             if k == 1:
                 self.review_settle(pr, h)
             else:
                 self.sleep(30)
             guard()
-            code, said = self.run(["gh", "pr", "merge", str(pr), "--repo", self.repo, "--merge",
-                                   "--match-head-commit", h])
-            said = " ".join(said.split())[-240:] or "(no output)"
+            code, whole = self.run(["gh", "pr", "merge", str(pr), "--repo", self.repo, "--merge",
+                                    "--match-head-commit", h])
+            said = " ".join(whole.split())[-240:] or "(no output)"
             st = self.out("gh", "pr", "view", str(pr), "--repo", self.repo, "--json", "state,mergeCommit",
                           "--jq", '"\\(.state) \\(.mergeCommit.oid)"')
             if st.startswith("MERGED"):
@@ -1956,6 +2022,28 @@ class Train:
             self.log(f"#{pr} merge attempt {k}/{self.merge_tries} refused (rc={code}): {said}")
             if BASE_MOVED.search(said):
                 raise MainMoved("merge", f"GitHub refused the merge because the base moved: {said}")
+            if not swept and self.bot_prs:
+                # P191: a record PR that turned green mid-batch merges now, once
+                # per landing, and the existing recovery recarries this entry.
+                swept = True
+                bot = self.sweep_bots()
+                if bot:
+                    raise MainMoved("merge", f"the record PR #{bot} merged under the batch")
+            if BRANCH_POLICY_SAID.search(said):
+                why, wait, approval = self.policy_refusal(pr, h)
+                self.log(f"#{pr} base-branch policy refusal, whole: {' '.join(whole.split()) or '(no output)'}; "
+                         f"read: {why}")
+                if wait:
+                    continue
+                if approval and not carried:
+                    carried = True
+                    how = self._carry_owner_approval(pr, h, item, files)
+                    if how:
+                        self.log(f"#{pr} approved ({how}) at {h[:8]} after the policy refusal")
+                        continue
+                    why += f"; no approval carried: {item.get('carry_refused', 'unread')}"
+                raise Stop("merge", f"not merged after {k} attempt(s): parked, {why}; the last refusal: {said}",
+                           cls=BRANCH_POLICY)
         else:
             raise Stop("merge", f"not merged after {self.merge_tries} attempts; the last refusal: {said}",
                        cls=BRANCH_POLICY if BRANCH_POLICY_SAID.search(said) else None)
@@ -1967,6 +2055,43 @@ class Train:
             self.run(["bash", tool("worktree_gc"), self.repo])
         return st.split()[-1]
 
+    def policy_refusal(self, pr: int, h: str) -> "tuple[str, bool, bool]":
+        """Why GitHub's base-branch policy refused <pr> at <h> (carries 1-3,
+        P34), read from `gh pr view --json mergeStateStatus,reviewDecision,
+        statusCheckRollup` against the head's required contexts: (reason,
+        wait, approval). `wait` -- a required context still pending or not
+        yet reported, or the state unreadable -- retries as before; anything
+        else parks the entry with the reason, never 8 blind attempts. A
+        required context red names it; `approval` marks the refusal an
+        approval can answer (REVIEW_REQUIRED, or BLOCKED with every required
+        context green: the ruleset's extra approval at the moved head)."""
+        code, o = self.run(["gh", "pr", "view", str(pr), "--repo", self.repo, "--json",
+                            "mergeStateStatus,reviewDecision,statusCheckRollup"])
+        try:
+            d = json.loads(o) if code == 0 else None
+            req = self.required(pr_head=True)
+        except (ValueError, Stop):
+            d = None
+        if not isinstance(d, dict):
+            return f"the merge state could not be read ({o.strip()[-120:] or 'no output'})", True, False
+        last: dict = {}
+        for c in d.get("statusCheckRollup") or ():
+            last[c.get("name") or c.get("context") or "?"] = (
+                c.get("conclusion") or c.get("state") or c.get("status") or "").upper()
+        red = [n for n in req if n not in self.ignore and last.get(n) in POLICY_RED]
+        pending = [n for n in req if n not in self.ignore and n not in red
+                   and last.get(n) not in ("SUCCESS", "SKIPPED", "NEUTRAL")]
+        ms, rd = d.get("mergeStateStatus") or "?", d.get("reviewDecision") or "none"
+        state = f"mergeStateStatus {ms}, reviewDecision {rd}"
+        if red:
+            return f"required context(s) red at {h[:8]}: {', '.join(red)} ({state})", False, False
+        if pending:
+            return f"required context(s) not yet green at {h[:8]}: {', '.join(pending)} ({state})", True, False
+        if rd in ("REVIEW_REQUIRED", "CHANGES_REQUESTED") or ms == "BLOCKED":
+            return (f"{state}: every required context is green, so the missing requirement is a review "
+                    f"at {h[:8]}"), False, rd != "CHANGES_REQUESTED"
+        return f"{state}, every required context green: no cause read", False, False
+
     def review_settle(self, pr: int, h: str) -> None:
         """Before the FIRST merge attempt (P86): the approval's `CI review` run
         (ci.yml on `pull_request_review`) at <h> must conclude, or base-branch
@@ -2917,7 +3042,13 @@ class Train:
         mine = len(self.skipped)  # this batch's skips start here: an earlier batch's never filter a re-added entry
         try:
             mf = _fastpath()
-            self.sweep_bots()  # before the base is read: a record PR merged now is under every proof
+            # P289: a batch holding a critical-path entry reads its base without
+            # the record sweep and sweeps after its merges.
+            cp = self.bot_prs and any(self.critical(i) for i in queue)
+            if cp:
+                self.log("critical path in the batch: the record sweep waits for its merges")
+            else:
+                self.sweep_bots()  # before the base is read: a record PR merged now is under every proof
             self.run(["git", "fetch", "-q", "origin", self.base])
             base = self.git("rev-parse", f"origin/{self.base}")
             req = self.required()
@@ -3024,6 +3155,8 @@ class Train:
                     phase = "post-merge" if self.is_merged(a["pr"]) else s.step
                     recover = recover and phase != "post-merge"
                     self.skip(a["pr"], phase, s.why, s.cls)
+            if cp:
+                self.sweep_bots()  # P289: after the batch's merges, before its serial entries recarry
             order = {int(item["pr"]): i for i, item in enumerate(queue)}
             bad = {s["pr"] for s in self.skipped[mine:]}
             later = sorted([a for a in serial + dropped if a["pr"] not in bad], key=lambda a: order[a["pr"]])
@@ -3036,7 +3169,7 @@ class Train:
                 self.log(f"serial: {', '.join('#%d' % a['pr'] for a in later)}")
                 for a in later:
                     try:
-                        self.one_overlap(a, req) if self.overlap else self.one(a, req)
+                        self.one_overlap(a) if self.overlap else self.one(a)
                     except Stop as s:
                         if s.step == "main" or not self.skip_bad:
                             raise Stop(s.step, f"#{a['pr']} {s.why}", cls=s.cls) from None
@@ -3162,10 +3295,11 @@ def _self_test() -> int:
             if got is not None:
                 return got
             if "record_row.py" in a:  # --bot-prs: the record PR lookup and its guard
-                if "--find-open" in argv:
-                    return world.get("bot_find", (0, "0"))
+                if "--find-open" in argv:  # a merged record PR is no longer open
+                    return (0, "0") if 9 in world.get("bot_merged", ()) else world.get("bot_find", (0, "0"))
                 world.setdefault("bot_guarded", []).append(argv[argv.index("--head") + 1])
-                return world.get("bot_guard", (0, "AUTOMERGE OK #9"))
+                g = world.get("bot_guard", (0, "AUTOMERGE OK #9"))
+                return (g.pop(0) if len(g) > 1 else g[0]) if isinstance(g, list) else g  # a list: one per sweep
             # THE RECORD-BEAT HOLD (issue #2302): the commit the hold ref points
             # at, and the ref create/update. `hold_sha` empty (the default) is
             # the API refusing, which the train must survive.
@@ -3183,8 +3317,13 @@ def _self_test() -> int:
                 return 0, ("e" * 40 if "headRefOid" in a else
                            "MERGED " + "9" * 40 if 9 in world.get("bot_merged", ()) else "OPEN None")
             if argv[:3] == ["gh", "pr", "merge"] and argv[3] == "9":
+                if "bot_merge_out" in world:  # GitHub refuses the record PR (P231)
+                    world.setdefault("bot_refused", []).append(9)
+                    return world["bot_merge_out"]
                 world.setdefault("bot_merged", []).append(9)
                 return 0, ""
+            if "mergeStateStatus" in a:  # the policy refusal's diagnosis read
+                return world.get("policy_state", (1, "HTTP 502"))
             if argv[:3] == ["gh", "pr", "view"] and "--json" in argv and argv[argv.index("--json") + 1] == "body":
                 return 0, world.get("pr_body", "")
             if argv[:3] == ["gh", "pr", "merge"] and world.get("merge_outs"):
@@ -3293,6 +3432,7 @@ def _self_test() -> int:
         world.setdefault("heads", [H0])
         world.setdefault("contains", [])
         world.setdefault("runs", green)
+        opts.setdefault("critical", lambda it: False)  # never the live roster in a fixture
         lines: list[str] = []
         timeline: list[tuple[str, str]] = []  # calls and log lines, in order
         run, calls = fake(world)
@@ -3521,6 +3661,54 @@ def _self_test() -> int:
     rc, lines, calls = go({"bot_find": (0, "9")})
     check("without --bot-prs no record PR is looked up (the default is today's train)",
           rc == 0 and not any("record_row.py" in " ".join(c) for c in calls))
+    # P231 (#2893): GitHub's refusal of the record PR's merge is named in the
+    # BOT line, gh's last non-empty output line; the MERGED arm above is the null.
+    WHY = "At least 1 approving review is required by reviewers with write access."
+    rc, lines, calls = go({"bot_find": (0, "9"), "bot_merge_out": (
+        1, "X Pull request o/r#9 is not mergeable\nGraphQL: Repository rule violations found\n\n" + WHY + "\n\n")},
+        bot_prs=True)
+    check("P231: a record PR GitHub refuses logs `BOT #9 not merged ... refused: <gh's last line>`, "
+          "verbatim, and the queue still lands",
+          rc == 0 and any(ln.startswith("BOT #9 not merged at ") and ln.endswith("refused: " + WHY) for ln in lines)
+          and [c[3] for c in calls if c[:3] == ["gh", "pr", "merge"]] == ["9", "7"])
+    # P191: a refused attempt (not BASE_MOVED) sweeps the record PR once; one
+    # that turned green merges and the main-moved recovery recarries the entry.
+    REF7 = (1, "X Pull request tvofi/r#7 is not mergeable: the merge commit cannot be cleanly created.")
+    PEND, OK9 = (3, "AUTOMERGE PENDING #9"), (0, "AUTOMERGE OK #9")
+    rc, lines, calls = go({"bot_find": (0, "9"), "bot_guard": [PEND, OK9], "merge_outs": [REF7],
+                           "merge": ["OPEN None", "MERGED " + "e" * 40],
+                           "contains": [True, True, True, False, True], "heads": [H0, H0, H0, H1]},
+                          bot_prs=True, main_moved_tries=1)
+    check("P191: a refused attempt with a record PR now green merges it (BOT MERGED) and recovers "
+          "through MAIN-MOVED: recarried, merged at the new head",
+          rc == 0 and [(c[3], c[-1]) for c in calls if c[:3] == ["gh", "pr", "merge"]]
+          == [("7", H0), ("9", "e" * 40), ("7", H1)]
+          and any(ln.startswith("BOT #9 MERGED") for ln in lines) and remerges(calls) == 1
+          and any("[MAIN-MOVED] merge: the record PR #9 merged under the batch" in ln for ln in lines))
+    for find, guard, word in (((0, "0"), OK9, "no open record PR"), ((0, "9"), PEND, "a record PR still pending")):
+        rc, lines, calls = go({"bot_find": find, "bot_guard": guard, "merge_outs": [REF7] * 3,
+                               "merge": ["OPEN None"] * 3}, bot_prs=True, main_moved_tries=1)
+        check(f"P191 null ({word}): the refused attempts go on as today -- three attempts, one sweep "
+              "past the recarry's, no MAIN-MOVED",
+              rc == 1 and sum(c[:4] == ["gh", "pr", "merge", "7"] for c in calls) == 3
+              and sum("--find-open" in c for c in calls) == 2 and remerges(calls) == 0
+              and "not merged after 3 attempts" in lines[-1] and not any("MAIN-MOVED" in ln for ln in lines)
+              and (find[1] == "0" or sum(ln.startswith("BOT #9 pending") for ln in lines) == 2))
+    rc, lines, calls = go({"bot_find": (0, "9"), "merge_outs": [REF7] * 3, "merge": ["OPEN None"] * 3})
+    check("P191 null: without --bot-prs a refused attempt sweeps nothing",
+          rc == 1 and not any("record_row.py" in " ".join(c) for c in calls))
+    # P289 (tvofi, 2026-10-29): a critical-path entry jumps the record step;
+    # the record PR merges after it, before the next entry.
+    q78 = [dict(item), dict(item, pr=8, branch="fix/y")]
+    for cp, want in ((lambda it: it["pr"] == 7, ["7", "9", "8"]), (lambda it: False, ["9", "7", "8"])):
+        rc, lines, calls = go({"bot_find": (0, "9")}, q=[dict(i) for i in q78], bot_prs=True, critical=cp)
+        check(f"P289 serial: {'a critical-path #7 merges, then the record PR, then #8' if want[0] == '7' else 'null, nothing critical: the record PR merges FIRST, as today'}",
+              rc == 0 and [c[3] for c in calls if c[:3] == ["gh", "pr", "merge"]] == want
+              and (want[0] != "7" or any(ln == "#7 critical path: the record sweep waits for its merge"
+                                         for ln in lines)))
+    rc, lines, calls = go({"bot_find": (0, "9")}, bot_prs=True, critical=lambda it: True)
+    check("P289 serial, a critical-path entry alone: the record PR still merges, after it (the run's end)",
+          rc == 0 and [c[3] for c in calls if c[:3] == ["gh", "pr", "merge"]] == ["7", "9"])
     if had_token is None:
         os.environ.pop("GH_TOKEN", None)
     # --pre-flight: queue_pre_flight's reads first; a failing entry PARKs.
@@ -3546,7 +3734,7 @@ def _self_test() -> int:
     # --free-holders: a clean holder at origin/<branch> is detached, nothing else.
     seen: list[list[str]] = []
 
-    def holding(state: str, at: str, here: str = "1" * 40):
+    def holding(state: str, at: str, here: str = "1" * 40, behind: bool = False):
         seen.clear()
 
         def wrap(base_run):
@@ -3567,6 +3755,8 @@ def _self_test() -> int:
                 if argv[:4] == ["git", "-C", "/other/wt", "checkout"]:
                     freed.append(1)
                     return 0, ""
+                if argv[:6] == ["git", "-C", "/other/wt", "merge-base", "--is-ancestor", here]:
+                    return (0 if behind else 1), ""  # P184: is the holder's HEAD inside origin/<br>
                 return base_run(argv, cwd=cwd, stdin=stdin)
             return run
         return wrap
@@ -3578,7 +3768,7 @@ def _self_test() -> int:
           and any("[HOLDER] freed: /other/wt" in ln and "switch fix/x" in ln for ln in lines))
     for st, at, why in ((" M x.py\n", "1" * 40, "uncommitted or untracked"),
                         ("?? note.md\n", "1" * 40, "uncommitted or untracked"),
-                        ("", "2" * 40, "unpushed work")):
+                        ("", "2" * 40, "commits origin does not have")):
         rc, lines, calls = go({"contains": [False], "heads": [H0, H1]}, wrap=holding(st, at), free_holders=True)
         check(f"--free-holders refuses a holder with {why} ({st.strip() or 'HEAD off origin'}): "
               "today's HOLDER stop, the reason appended, nothing detached",
@@ -3591,6 +3781,20 @@ def _self_test() -> int:
           "equal failures are no sha, and nothing is detached",
           rc == 1 and "[HOLDER]" in lines[-1] and "unpushed work" in lines[-1]
           and not detached(calls) and not merged(calls))
+    # P184 (s41 refused 45d08312, an ancestor of origin's 8a133f39): a clean
+    # holder BEHIND origin/<branch> loses nothing, so it is freed; the arm
+    # above (HEAD 1.., origin 2.., not an ancestor) is its refusing twin.
+    rc, lines, calls = go({"contains": [False], "heads": [H0, H1]}, wrap=holding("", "2" * 40, behind=True),
+                          free_holders=True)
+    check("P184 --free-holders: a clean holder whose HEAD is an ancestor of origin/<branch> is freed, "
+          "logged, and the recarry goes on to the merge",
+          rc == 0 and merged(calls) and detached(calls)
+          and any("[HOLDER] freed: /other/wt" in ln and "nothing origin/fix/x lacks" in ln for ln in lines))
+    rc, lines, calls = go({"contains": [False], "heads": [H0, H1]}, wrap=holding("", "2" * 40),
+                          free_holders=True)
+    check("P184 null: a clean holder AHEAD of origin/<branch> refuses naming the commits origin does not have",
+          rc == 1 and "[HOLDER]" in lines[-1] and "has commits origin does not have" in lines[-1]
+          and not detached(calls) and not merged(calls))
     rc, lines, calls = go({"contains": [False], "heads": [H0, H1]}, wrap=holding("", "1" * 40))
     check("without --free-holders even a freeable holder stops exactly as today (null control)",
           rc == 1 and "[HOLDER]" in lines[-1] and "not freed" not in lines[-1] and not detached(calls))
@@ -3788,6 +3992,71 @@ def _self_test() -> int:
     rc, lines, calls = go(carry_world(reviews=[], mandate=mandate(NOW)), mandate=CB, approval_carry=True)
     check("approval-carry with no owner APPROVED review at h0 behaves as today", rc == 1
           and "a raise is the owner's" in lines[-1] and not approved(calls) and not merged(calls))
+    # Carries 1-3 (#2577, P4 s4, P34): "base branch policy prohibits the
+    # merge" is diagnosed from the merge state, the review decision and the
+    # check rollup, and the car PARKS with that reason instead of 8 retries.
+    POL_REF = (1, "X Pull request tvofi/r#7 is not mergeable: the base branch policy prohibits the merge.\n"
+                  "To have the pull request merged after all the requirements have been met, add --auto.")
+
+    def pstate(ms="BLOCKED", rd="APPROVED", fast=("COMPLETED", "SUCCESS")):
+        return 0, json.dumps({"mergeStateStatus": ms, "reviewDecision": rd, "statusCheckRollup": [
+            {"__typename": "CheckRun", "name": "fast", "status": fast[0], "conclusion": fast[1]},
+            {"__typename": "StatusContext", "context": "nightly-status", "state": "FAILURE"}]})
+    n7 = lambda calls: sum(c[:4] == ["gh", "pr", "merge", "7"] for c in calls)
+    rc, lines, calls = go({"merge_outs": [POL_REF] * 3, "merge": ["OPEN None"] * 3,
+                           "policy_state": pstate(fast=("COMPLETED", "FAILURE"))})
+    check("policy refusal with a required context red at the head: ONE attempt, parked [BRANCH-POLICY] "
+          "naming it, and the whole refusal logged",
+          rc == 1 and n7(calls) == 1 and "[BRANCH-POLICY] not merged after 1 attempt(s): parked, "
+          "required context(s) red at aaaaaaaa: fast" in lines[-1]
+          and any("policy refusal, whole: X Pull request" in ln and "add --auto." in ln for ln in lines))
+    rc, lines, calls = go({"merge_outs": [POL_REF] * 3, "merge": ["OPEN None"] * 3})
+    check("policy refusal null: an unreadable merge state retries as today, three attempts",
+          rc == 1 and n7(calls) == 3 and "[BRANCH-POLICY] not merged after 3 attempts" in lines[-1])
+    rc, lines, calls = go({"merge_outs": [POL_REF], "merge": ["OPEN None", "MERGED " + "e" * 40],
+                           "policy_state": pstate(fast=("IN_PROGRESS", None))})
+    check("policy refusal with a required context still running waits: the next attempt merges",
+          rc == 0 and n7(calls) == 2 and any("not yet green at aaaaaaaa: fast" in ln for ln in lines))
+    rc, lines, calls = go({"merge_outs": [POL_REF] * 3, "merge": ["OPEN None"] * 3,
+                           "policy_state": pstate(rd="REVIEW_REQUIRED")})
+    check("policy refusal for a missing review, no --approval-carry: parked at once with the reason",
+          rc == 1 and n7(calls) == 1 and "reviewDecision REVIEW_REQUIRED" in lines[-1]
+          and "no approval carried: --approval-carry or --mandate is not given" in lines[-1])
+
+    def pol_world(**over):  # fresh per arm: a clean recarry H0 -> H1 of a non-code-owned entry
+        return dict({"contains": [False], "heads": [H0, H1], "merge_outs": [POL_REF] * 3,
+                     "merge": ["OPEN None", "MERGED " + "e" * 40],
+                     "carry_delta": (H0, H1, "docs/a-main-only-file.md\n"),
+                     "policy_state": pstate(rd="REVIEW_REQUIRED"),
+                     "reviews": [dict(owner_review(H0, NOW), id=RID)], "mandate": mandate(NOW)}, **over)
+    w = pol_world()
+    rc, lines, calls = go(w, mandate=CB, approval_carry=True)
+    check("carry 2: a policy refusal for the owner approval a clean recarry left behind is answered by "
+          "the approval carry, and the next attempt merges",
+          rc == 0 and n7(calls) == 2 and any("approved (carry) at " + H1[:8] in ln for ln in lines)
+          and "Carried by the train's clean recarry from " + H0 in w["carry_body"])
+    APPR = {"login": APPROVER_LOGIN, "id": 2, "type": "Bot"}
+    for over, why in (({"carry_delta": (H0, H1, f"{ROW_DIR}/7.md\n")}, "names branch-own"),
+                      ({"reviews": [dict(owner_review(H0, NOW), id=RID, user=APPR)]}, "no owner APPROVED review"),
+                      ({"mandate": mandate(NOW, until_min=-1)}, "is not in force at the merge")):
+        rc, lines, calls = go(pol_world(**over), mandate=CB, approval_carry=True)
+        check(f"carry 2 null ({why}): no carry, parked [BRANCH-POLICY] after one attempt with that reason",
+              rc == 1 and n7(calls) == 1 and "[BRANCH-POLICY]" in lines[-1] and "parked" in lines[-1]
+              and why in lines[-1] and not any("approved (carry)" in ln for ln in lines))
+    # P34: the head wait reads the required set a pull request's head carries
+    # (pr_head=True). PR_ONLY is empty under the umbrella `gate`; a non-empty
+    # one is the seam this arm drives.
+    keep = PR_ONLY
+    globals()["PR_ONLY"] = ("pr-contract",)
+    try:
+        for pc, red in (("failure", True), ("success", False)):
+            rc, lines, calls = go({"required": "fast\npr-contract\n", "runs": green + [
+                {"name": "pr-contract", "status": "completed", "conclusion": pc, "started_at": "1"}]})
+            check(f"P34: pr-contract {pc} at the head ({'stops at ci naming it, no merge attempt' if red else 'null: merges'})",
+                  (rc == 1 and "ci:" in lines[-1] and "pr-contract" in lines[-1] and not merged(calls)) if red
+                  else (rc == 0 and merged(calls)))
+    finally:
+        globals()["PR_ONLY"] = keep
     rc, lines, calls = go(carry_world(reviews=[dict(owner_review("f" * 40, NOW), id=RID)],
                                       mandate=mandate(NOW)), mandate=CB, approval_carry=True)
     check("approval-carry with the owner's approval on another commit does not carry", rc == 1
@@ -5164,6 +5433,7 @@ def _batch_self_test(check) -> None:
             (setup or (lambda w: None))(w)
             w["base_sha"] = g(w["R"], "rev-parse", base)[1]
             lines: list[str] = []
+            opts.setdefault("critical", lambda it: False)  # never the live roster in a fixture
             t = Train("o/r", Path(d) / "state", mandate, "the orchestrator", ignore, 1, run=stub(w),
                       sleep=lambda s: (w.setdefault("slept", []).append(s), w.get("on_sleep", lambda: None)()),
                       log=lambda ln: (lines.append(ln), w.get("on_log", lambda _ln: None)(ln)),
@@ -5307,6 +5577,17 @@ def _batch_self_test(check) -> None:
           "which carries its commit -- and both entries land on that proof",
           w["rc"] == 0 and sorted(w["merged"]) == [1, 2] and bot is not None and proof is not None
           and bot < proof and "rec.txt" in (w["proof_names"] or [[]])[0])
+    # P289: a batch holding a critical-path entry reads its base WITHOUT the
+    # sweep and sweeps after its merges; the arm above is the null.
+    w = go({1: {"a.txt": "A\n"}, 2: {"b.txt": "B\n"}}, base="main", bot_prs=True,
+           critical=lambda it: int(it["pr"]) == 1)
+    bot = next((i for i, ln in enumerate(w["lines"]) if ln.startswith("BOT #9 MERGED")), None)
+    last = max((i for i, ln in enumerate(w["lines"]) if re.match(r"#[12] MERGED", ln)), default=None)
+    check("P289 batch: with a critical-path entry the proof is built without the record PR, both "
+          "entries land, then the record PR merges",
+          w["rc"] == 0 and sorted(w["merged"]) == [1, 2] and bot is not None and last is not None
+          and last < bot and "rec.txt" not in (w["proof_names"] or [[]])[0]
+          and any(ln.startswith("critical path in the batch") for ln in w["lines"]))
     w = go({1: {"a.txt": "A\n"}, 2: {"b.txt": "B\n"}}, bot_prs=True)
     check("batch --bot-prs on a batch/ rehearsal looks nothing up and merges no record PR -- a "
           "rehearsal writes nothing to main -- while the rehearsal itself still lands",

