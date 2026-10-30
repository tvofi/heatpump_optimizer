# Review packet #3002
head: dabd6f1e596a26abc5bb85515add6480c708003a
base: ca0a6cfbc2e5538e6e2220793831443719ff6e98

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: pending
CodeQL id=124186285898 neutral
arch-score / arch-score id=124185873367 success
arm id=124185665257 skipped
budget-raise-gate / budget-raise-gate id=124185873112 success
cancel-superseded id=124185670388 success
codeql / Analyze (actions) id=124185873363 success
codeql / Analyze (javascript-typescript) id=124185873569 success
codeql / Analyze (python) id=124185873369 in_progress
governance / delivery-status id=124185873557 success
governance / delivery-status-publish id=124185875436 skipped
governance / env-matrix id=124185873378 in_progress
governance / instrument-self-tests id=124185873719 in_progress
governance / policy-docs id=124185873386 success
governance / record id=124185876007 skipped
governance / wave-script id=124185873420 success
hassfest / hassfest id=124185873525 success
kernel-points id=124185875186 skipped
prelude id=124185670330 success
refresh id=124185670022 success
tests / arch-instrument id=124186132284 success
tests / briefs id=124185873274 success
tests / browser id=124186132204 in_progress
tests / closure-scope id=124185873337 success
tests / closures id=124186132414 in_progress
tests / coverage id=124186132260 in_progress
tests / fast (3.14) id=124186132796 in_progress
tests / mutation id=124185873346 success
tests / mutation-autofix id=124186293457 skipped
tests / mutation-pins id=124186293899 skipped
tests / nightly-ha id=124186134692 skipped
tests / nightly-status id=124185873305 success
tests / replay id=124186135237 skipped
tests / typing id=124186132281 success
validate / validate-hacs id=124185873222 success

## Refusals
none

## Advisories
hot-file: HPO_BUS_TRAIN_STATE is unset, so every merge verdict reads unboarded

## carry_audit at the head
CARRY-AUDIT: 0 finding item(s): 0 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
ok         python3 tools/audit/seat/orchestrator_tick.py --self-test
             `tools/audit/seat/orchestrator_tick.py` is in the tree at this head
  ok         bash tools/pr/prepr.sh
             `tools/pr/prepr.sh` is in the tree at this head

FIGURES: 2 resolved, 0 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
none

## Three-dot diff
diff --git a/dev/programme/delivery/3002.md b/dev/programme/delivery/3002.md
new file mode 100644
index 000000000..0aa6ef2cb
--- /dev/null
+++ b/dev/programme/delivery/3002.md
@@ -0,0 +1 @@
+- [#3002](https://github.com/tvofi/heatpump_optimizer/pull/3002) — **open**, R10-FLOW-DESIGN-STAGES part 3: DESIGN OWED tick line age and critical-path mark (R10-FLOW-DESIGN-STAGES)
diff --git a/tools/audit/seat/orchestrator_tick.py b/tools/audit/seat/orchestrator_tick.py
index 9dbe6fefd..8252c040a 100644
--- a/tools/audit/seat/orchestrator_tick.py
+++ b/tools/audit/seat/orchestrator_tick.py
@@ -1178,7 +1178,9 @@ class Tick:
         """`DESIGN OWED:` an eligible group (size L or XL, decision 0014) whose
         every `after` group is done or dispatched, still undispatched itself,
         with no `design/<group>` ref: the designer starts when the last
-        predecessor dispatches, not when it merges. A failed ref read is
+        predecessor dispatches, not when it merges. The line names the age
+        since that dispatch and a `CP` mark when the group is on the roster
+        critical path (`roster_lib.critical_path`). A failed ref read is
         UNREADABLE, never an empty owed list."""
         code, o = self.git(["ls-remote", "origin", "refs/heads/design/*"])
         if code:
@@ -1187,6 +1189,7 @@ class Tick:
         have = {l.split()[1][len("refs/heads/design/"):].lower() for l in o.splitlines()
                 if len(l.split()) >= 2 and l.split()[1].startswith("refs/heads/design/")}
         groups, open_g = rl.groups_of(roster), rl.open_groups(roster)
+        critical = set(rl.critical_path(roster))
         for gid, g in groups.items():
             stage = (g.get("resume") or {}).get("stage")
             if gid not in open_g or not rl.needs_design(g) or gid.lower() in have:
@@ -1196,8 +1199,32 @@ class Tick:
             if any(a in open_g and ((groups[a].get("resume") or {}).get("stage") in UNBLOCKABLE_STAGES)
                    for a in (g.get("after") or []) if a in groups):
                 continue  # a predecessor is not dispatched yet
-            self.line(S, f"DESIGN OWED: {gid} (size {g.get('size')}) -- last predecessor dispatched, "
-                         f"no design/{gid}; dispatch the designer", flag=True)
+            cp = " CP" if gid in critical else ""
+            self.line(S, f"DESIGN OWED:{cp} {gid} (size {g.get('size')}) -- last predecessor dispatched "
+                         f"{self._dispatch_age(rl, groups, g)}, no design/{gid}; dispatch the designer",
+                      flag=True)
+
+    def _dispatch_age(self, rl, groups: dict, g: dict) -> str:
+        """The age of the newest predecessor dispatch, read from the committer
+        date of `origin/dispatch/fixer-<topic>` (the roster keeps no dispatch
+        instant); `age unknown` when no predecessor's dispatch ref is readable
+        and `n/a` for a group with no predecessor."""
+        preds = [groups[a] for a in (g.get("after") or []) if a in groups]
+        if not preds:
+            return "(no predecessor)"
+        ages = []
+        for p in preds:
+            topic = rl.branch_of(p).split("/", 1)[-1]
+            code, o = self.git(["log", "-1", "--format=%cI", f"origin/dispatch/fixer-{topic}"])
+            try:
+                if code:
+                    raise ValueError(o)
+                ages.append(self.now - datetime.datetime.fromisoformat(o.strip()))
+            except ValueError:
+                continue
+        if not ages:
+            return "(age unknown)"
+        return f"{int(min(ages).total_seconds() // 3600)}h ago"
 
     def design_builds(self, S: str, rl, roster: dict) -> None:
         """`DESIGN-BUILD:` every pass for an approved design whose roster group
@@ -4024,7 +4051,7 @@ def self_test() -> int:
         ow, ow_un = oboard(), oboard(ls_rc=1)
         a, f = check("DESIGN OWED", [
             ("an L group whose last predecessor dispatched and that has no design ref is owed one",
-             [x.split()[2] for x in ow] == ["R10-L1"]),
+             len(ow) == 1 and " R10-L1 " in ow[0]),
             ("null controls: a predecessor not dispatched, a design ref, an S group and a dispatched group owe nothing",
              not any(g in x for x in ow for g in ("R10-L2", "R10-L3", "R10-S1", "R10-L4"))),
             ("an unreadable ref listing is UNREADABLE and owes nothing it cannot know",
@@ -4032,6 +4059,36 @@ def self_test() -> int:
         ])
         total, failed = total + a, failed + f
 
+        # ---- DESIGN OWED carries the dispatch age and a CP mark ----
+        aroster = {"groups": [
+            {"group": "R10-P", "size": "S", "resume": {"stage": "in-progress", "branch": "handoff/r10-p"}},
+            {"group": "R10-L1", "size": "L", "after": ["R10-P"], "resume": {"stage": "not-started"}},
+            {"group": "R10-X", "size": "S", "after": ["R10-L1"], "resume": {"stage": "not-started"}},
+            {"group": "R10-Z", "size": "S", "resume": {"stage": "in-progress", "branch": "handoff/r10-z"}},
+            {"group": "R10-L5", "size": "L", "after": ["R10-Z"], "resume": {"stage": "not-started"}}]}
+
+        def aboard(ls_out="", dispatched=True):
+            t = tick()
+            t._git.h.insert(0, (("ls-remote", "refs/heads/design/*"), 0, ls_out))
+            if dispatched:
+                t._git.h.insert(0, (("log", "origin/dispatch/fixer-r10-p"), 0,
+                                    iso(NOW - datetime.timedelta(hours=7)) + "\n"))
+            t.designs_owed("PLAN", rlm, aroster)
+            return flagged(t.sections.get("PLAN", []))
+        ag, ag_ref, ag_unk = aboard(), aboard(f"{A40}\trefs/heads/design/R10-L1\n{A40}\trefs/heads/design/R10-L5\n"), aboard(dispatched=False)
+        l1 = [x for x in ag if "R10-L1 " in x]
+        l5 = [x for x in ag if "R10-L5 " in x]
+        a, f = check("DESIGN OWED age and CP", [
+            ("a group with no design ref prints the age since its predecessor dispatched",
+             len(l1) == 1 and "dispatched 7h ago" in l1[0]),
+            ("a critical-path group carries the CP mark", len(l1) == 1 and "DESIGN OWED: CP R10-L1" in l1[0]),
+            ("null control: a non-critical group prints no CP mark", len(l5) == 1 and " CP " not in l5[0]),
+            ("null control: with the design ref nothing prints", ag_ref == []),
+            ("an unreadable dispatch ref says the age is unknown, not a number",
+             any("age unknown" in x for x in ag_unk) and not any("h ago" in x for x in ag_unk)),
+        ])
+        total, failed = total + a, failed + f
+
         # ---- the null control: an all-clear board, empty list, exit 0 ----
         rfile.write_text(json.dumps({"groups": [
             {"group": "A", "resume": {"stage": "done"}},

