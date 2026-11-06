# Review packet #3250
head: 99cf3c2537c0199d966aff7b1c5fd86bcc8f663c
base: b36679ceaa65a08a67a84f0d934c93aa15f7c7f3

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: red
CodeQL id=127920017157 success
arch-score / arch-score id=127919952161 success
arm id=127919675061 skipped
budget-raise-gate / budget-raise-gate id=127919952162 success
cancel-superseded id=127919675284 success
codeql id=127919954346 skipped
codeql / Analyze (actions) id=127919930474 success
codeql / Analyze (javascript-typescript) id=127919930595 success
codeql / Analyze (python) id=127919930568 success
gate id=127920529181 failure
governance id=127919953965 skipped
governance / delivery-status id=127919930572 success
governance / delivery-status-publish id=127919932148 skipped
governance / env-matrix id=127919930794 success
governance / instrument-self-tests id=127919930623 in_progress
governance / policy-docs id=127919930594 success
governance / record id=127919933329 skipped
governance / wave-script id=127919930657 success
hassfest id=127919954815 skipped
hassfest / hassfest id=127919930488 success
kernel-points id=127919954184 skipped
pr-contract id=127920530622 skipped
prelude id=127919675169 success
refresh id=127919675336 success
tests id=127919955460 skipped
tests / arch-instrument id=127920146271 success
tests / briefs id=127919930490 success
tests / browser id=127920146274 in_progress
tests / closure-scope id=127919930495 success
tests / closures id=127920146496 in_progress
tests / coverage id=127920146320 in_progress
tests / fast (3.14) id=127920146691 in_progress
tests / mutation id=127919930455 success
tests / mutation-autofix id=127920372759 skipped
tests / mutation-pins id=127920373737 skipped
tests / nightly-ha id=127920148634 skipped
tests / nightly-status id=127919930411 success
tests / replay id=127920148751 skipped
tests / typing id=127920146311 success
validate id=127919954493 skipped
validate / validate-hacs id=127919930426 success

## Refusals
red-unanswered: concluded red check `gate` is not named in ## Red checks
required-red: required context `gate` concluded failure at 99cf3c2537c0199d966aff7b1c5fd86bcc8f663c

## Advisories
hot-file: HPO_BUS_TRAIN_STATE is unset, so every merge verdict reads unboarded

## carry_audit at the head
NOTE body item c5fd5054: dismissed:landed in this PR
CARRY-AUDIT: 1 finding item(s): 1 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
ok         python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)
             `tests/closure.py` is in the tree at this head
  ok         tests/entities.py
             `tests/entities.py` is in the tree at this head
  ok         tests/env_drift.py --claims-only
             `tests/env_drift.py` is in the tree at this head
  ok         tests/closure.py selftest
             `tests/closure.py` is in the tree at this head
  ok         tests/layout.py
             `tests/layout.py` is in the tree at this head
  ok         tests/harness_headers.py
             `tests/harness_headers.py` is in the tree at this head
  ok         python3 tests/structure.py
             `tests/structure.py` is in the tree at this head

FIGURES: 7 resolved, 0 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
none

## Three-dot diff
diff --git a/dev/programme/delivery/3250.md b/dev/programme/delivery/3250.md
new file mode 100644
index 000000000..da6f5482b
--- /dev/null
+++ b/dev/programme/delivery/3250.md
@@ -0,0 +1 @@
+- [#3250](https://github.com/tvofi/heatpump_optimizer/pull/3250) — **open**, R10-ROSTER-READ-SWEEP: roster-reader predicates, carries 1-4 (R10-ROSTER-READ-SWEEP)
diff --git a/tools/audit/carry_audit.py b/tools/audit/carry_audit.py
index 150a1b4be..e1bc369e9 100644
--- a/tools/audit/carry_audit.py
+++ b/tools/audit/carry_audit.py
@@ -419,8 +419,10 @@ class Dests:
             return True, ""
         if r is not None and self.live(r):
             return True, f"{tok} resolved on {self.round_ref}"
-        stage = ((g or r).get("resume") or {}).get("stage")
-        return False, (f"{tok} is {'done' if stage in roster_lib.DONE_STAGES else stage} (resume.stage {stage}); "
+        res = (g or r).get("resume") or {}
+        stage = res.get("stage")
+        into = f" into {res['absorbed_into']}" if stage == "absorbed" and res.get("absorbed_into") else ""
+        return False, (f"{tok} is {'done' if stage in roster_lib.DONE_STAGES else stage}{into} (resume.stage {stage}); "
                        f"valid targets: {self.consumers()}")
 
     @staticmethod
@@ -1108,7 +1110,7 @@ def _self_test() -> int:
     # after-edged on the pull request's own group as the valid targets.
     def gr(name, stage, after=()):
         return {"group": name, "after": list(after), "resume": {"stage": stage}}
-    Dcl = Dests({"groups": [gr("R10-PR", "in-progress"), gr("R10-GONE", "done"), gr("R10-ABS", "absorbed"),
+    Dcl = Dests({"groups": [gr("R10-PR", "in-progress"), gr("R10-GONE", "done"), dict(gr("R10-ABS", "absorbed"), resume={"stage": "absorbed", "absorbed_into": "R10-CONS"}),
                             gr("R10-CONS", "not-started", ["R10-PR"]), gr("R10-DEAD", "done", ["R10-PR"]),
                             gr("R10-OTHER", "not-started", ["R10-LIVE"]), gr("R10-NS", "not-started")]},
                 set(), None, pr_group="R10-PR")
@@ -1118,6 +1120,9 @@ def _self_test() -> int:
         check(f"a closed group ({g}) is refused naming it and listing the live after-edged consumers",
               g in msg and "R10-CONS" in msg and "R10-OTHER" not in msg and "R10-DEAD" not in msg
               and "R10-NS" not in msg)
+    r = run(plant.rstrip() + " Carry: R10-ABS\n", d=Dcl)
+    check("an absorbed destination is refused naming absorbed_into",
+          "R10-ABS is absorbed into R10-CONS" in (r["rows"][0]["bad"][0] if r["b"] == 1 else ""))
     for g in ("R10-CONS", "R10-NS"):
         r = run(plant.rstrip() + f" Carry: {g}\n", d=Dcl)
         check(f"a live group ({g}) is accepted with no note (null control)",
diff --git a/tools/audit/seat/handover_prompt.py b/tools/audit/seat/handover_prompt.py
index 013d50133..b123337ab 100644
--- a/tools/audit/seat/handover_prompt.py
+++ b/tools/audit/seat/handover_prompt.py
@@ -53,7 +53,7 @@ def in_flight(roster: dict) -> list:
     out = []
     for g, gr in roster_lib.groups_of(roster).items():
         stage = (gr.get("resume") or {}).get("stage") or NOT_STARTED
-        if stage not in roster_lib.DONE_STAGES and stage != NOT_STARTED:
+        if stage not in roster_lib.CLOSED_STAGES and stage != NOT_STARTED:
             out.append((g, gr))
     return out
 
@@ -269,6 +269,9 @@ def _self_test() -> int:
     check("empty roster renders", "Ready next" in empty
           and "none" in empty and "Worktrees in flight" not in empty)
 
+    rc, refused, tb = roster_lib.missing_ref_probe(__file__)
+    check("a missing roster ref is one REFUSED line, rc 2, no traceback",
+          rc == 2 and refused == 1 and not tb, (rc, refused, tb))
     print(f"handover_prompt self-test: {n_checks[0]} checks, "
           f"{len(failed)} failed")
     for f in failed:
@@ -277,4 +280,4 @@ def _self_test() -> int:
 
 
 if __name__ == "__main__":
-    sys.exit(main())
+    sys.exit(roster_lib.run_refusing("handover_prompt", main))
diff --git a/tools/audit/seat/orchestrator_tick.py b/tools/audit/seat/orchestrator_tick.py
index c605a1601..64051c76a 100644
--- a/tools/audit/seat/orchestrator_tick.py
+++ b/tools/audit/seat/orchestrator_tick.py
@@ -2181,9 +2181,16 @@ class Tick:
                                      f"{sha[:12]} is not in origin/main's "
                                      "history -- re-derive the resume",
                                   flag=True)
-            # owner-gated age
-            gated = [g for gid, g in groups.items()
-                     if gid in open_g and g.get("owner_gate")]
+            # owner-gated age: the gate's class is roster_lib's (`gate_kind`);
+            # a covered gate is informational, only an owner gate flags and
+            # costs the issues read
+            kinds = {gid: rl.gate_kind(g.get("owner_gate")) for gid, g in groups.items()
+                     if gid in open_g}
+            covered = [gid for gid, k in kinds.items() if k == "covered"]
+            gated = [groups[gid] for gid, k in kinds.items() if k == "owner"]
+            if covered:
+                self.line(S, f"{len(covered)} group(s) with an owner gate the "
+                             "mandate in force covers (informational)")
             if gated:
                 issues = sorted(i for g in gated for i in (g.get("issues") or []))
                 age = ""
@@ -2782,6 +2789,29 @@ def self_test() -> int:
              and not any("#2394 not OPEN" in x["text"] for x in t_rp.findings)),
         ])
         total, failed = total + a, failed + f
+        def gated_tick(gate):
+            ro = {"groups": [{"group": "G-OWN", "issues": [7], "owner_gate": gate,
+                              "resume": {"stage": "not-started"}},
+                             {"group": "G-NONE", "resume": {"stage": "not-started"}}]}
+            rf = tmp / f"gate-{abs(hash(gate))}.json"
+            rf.write_text(json.dumps(ro))
+            tg = tick(prs=[], queue=str(q16), roster=str(rf),
+                      states={p: ("closed", H2) for p in (2379, 2394, 2416)})
+            tg.replan()
+            return tg
+        tg_cov = gated_tick("code-owned: .claude/hooks/ (mandate 6329234399)")
+        tg_own = gated_tick("owner decision after the probe")
+        a, f = check("REPLAN owner gates: only a decision not yet taken flags", [
+            ("a mandate-covered gate prints one informational line, no flag",
+             any("1 group(s) with an owner gate" in l["text"] and not l["flag"]
+                 for l in tg_cov.sections["REPLAN"])
+             and not any("blocked on owner" in x["text"] for x in tg_cov.findings)),
+            ("a covered gate costs no issues read",
+             not any("issues/7" in " ".join(c) for c in tg_cov._gh.calls)),
+            ("an owner gate is flagged blocked on owner",
+             any("1 group(s) blocked on owner" in x["text"] for x in tg_own.findings)),
+        ])
+        total, failed = total + a, failed + f
         t = tick(procs=lambda pattern: [(11, "python3 merge_train.py"),
                                         (12, "python3 merge_train.py")])
         t.train()
diff --git a/tools/audit/seat/plan_table.py b/tools/audit/seat/plan_table.py
index ee74990ee..67638a6cf 100644
--- a/tools/audit/seat/plan_table.py
+++ b/tools/audit/seat/plan_table.py
@@ -274,6 +274,9 @@ def _self_test() -> int:
     empty = render({"groups": []}, "fixture", 1, {})
     check("empty roster renders", "0 open group(s) of 0" in empty)
 
+    rc, refused, tb = roster_lib.missing_ref_probe(__file__)
+    check("a missing roster ref is one REFUSED line, rc 2, no traceback",
+          rc == 2 and refused == 1 and not tb, (rc, refused, tb))
     print(f"plan_table self-test: {n_checks[0]} checks, {len(failed)} failed")
     for f in failed:
         print("FAIL", f)
@@ -323,4 +326,4 @@ def main(argv=None) -> int:
 
 
 if __name__ == "__main__":
-    sys.exit(main())
+    sys.exit(roster_lib.run_refusing("plan_table", main))
diff --git a/tools/audit/seat/resume_doc.py b/tools/audit/seat/resume_doc.py
index a5ae76f0b..531c4c2d0 100644
--- a/tools/audit/seat/resume_doc.py
+++ b/tools/audit/seat/resume_doc.py
@@ -237,6 +237,9 @@ def _self_test() -> int:
 
     import shutil
     shutil.rmtree(d, ignore_errors=True)
+    rc, refused, tb = roster_lib.missing_ref_probe(__file__)
+    check("a missing roster ref is one REFUSED line, rc 2, no traceback",
+          rc == 2 and refused == 1 and not tb, (rc, refused, tb))
     print(f"resume_doc self-test: {n_checks[0]} checks, {len(failed)} failed")
     for f in failed:
         print("FAIL", f)
@@ -244,4 +247,4 @@ def _self_test() -> int:
 
 
 if __name__ == "__main__":
-    sys.exit(main())
+    sys.exit(roster_lib.run_refusing("resume_doc", main))
diff --git a/tools/audit/seat/roster_lib.py b/tools/audit/seat/roster_lib.py
index e520976b2..2ae49b208 100644
--- a/tools/audit/seat/roster_lib.py
+++ b/tools/audit/seat/roster_lib.py
@@ -80,6 +80,11 @@ LIVE_CLAIM = tuple(w for w, k in STAGE_KIND if k == "live-claim")
 #: records that is not here keeps the group open (and its after-edges
 #: constraining).
 DONE_STAGES = tuple(w for w, k in STAGE_KIND if k == "done")
+#: The stages that end a group's work: the done ones, and `absorbed`, whose
+#: work lives in its fold destination. `is_open`, the after-edge closure and the
+#: carry destination check read this one set; `absorbed` stays a disposition
+#: (roster_sync never rewrites it), so DONE_STAGES keeps meaning "merged".
+CLOSED_STAGES = DONE_STAGES + ("absorbed",)
 #: Human dispositions: nothing derives, clears or overwrites one.
 DISPOSITION = tuple(w for w, k in STAGE_KIND if k == "disposition")
 #: The stages in which a group's work is under way, for the planner's live
@@ -340,13 +345,52 @@ def groups_of(roster: dict) -> dict:
 
 
 def is_open(group: dict) -> bool:
-    return (group.get("resume") or {}).get("stage") not in DONE_STAGES
+    return (group.get("resume") or {}).get("stage") not in CLOSED_STAGES
 
 
 def open_groups(roster: dict) -> dict:
     return {k: g for k, g in groups_of(roster).items() if is_open(g)}
 
 
+def run_refusing(tool: str, main, argv=None) -> int:
+    """`main(argv)`, a missing roster printed as the one `<tool>: REFUSED ...`
+    line and exit 2, never a traceback: the shared refusal of every reader
+    (carry_audit's own contract)."""
+    try:
+        return main(argv)
+    except RosterNotFound as e:
+        print(f"{tool}: REFUSED {e}")
+        return 2
+
+
+def missing_ref_probe(script: str) -> tuple[int, int, bool]:
+    """(rc, REFUSED lines, traceback seen) of `script` run against a roster ref
+    that does not exist: the self-test row every roster reader owes."""
+    r = subprocess.run([sys.executable, "-I", script, "--roster-ref",
+                        "origin/no-such-ref-xyz"], capture_output=True, text=True)
+    out = r.stdout + r.stderr
+    return r.returncode, out.count("REFUSED"), "Traceback" in out
+
+
+#: Owner-gate classes. A gate is `covered` when it names a mandate id or begins
+#: with a prefix the mandate in force covers (0013); `owner` when it states a
+#: decision still to be taken. The gate's meaning is the roster schema's, so the
+#: tick calls this and holds no pattern of its own.
+_GATE_COVERED = re.compile(r"\bmandate[ds]?\b|\A\s*(?:code-owned|policy|budget):", re.I)
+#: A gate stating a decision still to be taken (today only "owner decision after the probe").
+_GATE_OWNER = re.compile(r"\bowner decision\b", re.I)
+
+
+def gate_kind(text) -> str | None:
+    """None for no gate, `covered` for one the mandate in force covers, `owner`
+    for one stating a decision not yet taken (a mandate or covered prefix wins)."""
+    if not isinstance(text, str) or not text.strip():
+        return None
+    if _GATE_OWNER.search(text) and not _GATE_COVERED.search(text):
+        return "owner"
+    return "covered"
+
+
 # ------------------------------------------------------------ the carry ledger
 #
 # #2733's first invariant: a carry not yet implemented routes to a group that
@@ -361,9 +405,8 @@ def open_groups(roster: dict) -> dict:
 # `implemented` records that the sha is on main; it is not a verification.
 CARRY_MARKS = ("implemented", "moved", "dismissed")
 _CARRY_MARK = re.compile(r" \[(implemented|moved|dismissed): ([^\]\n]+)\]\Z")
-#: The stages in which a group can no longer receive or discharge a carry: the
-#: closed ones, and `absorbed`, whose work lives in its fold destination.
-CARRY_CLOSED = DONE_STAGES + ("absorbed",)
+#: The stages in which a group can no longer receive or discharge a carry.
+CARRY_CLOSED = CLOSED_STAGES
 #: THE CUT-OVER, per roster path: a carry that sat on a closed group at this
 #: roster-branch commit is LEGACY and is never reported, so the invariant
 #: starts at the cut-over with no blanket migration and nothing marked
@@ -718,6 +761,27 @@ def _self_test() -> int:
     got = [(s[0], s[2]) for s in stranded({"groups": [
         cg, cg | {"group": "AB", "resume": {"stage": "absorbed"}},
         cg | {"group": "CO", "resume": {"stage": "carries-open"}}]}, legacy)]
+    check("absorbed is closed: not open, and an after-edge on it clears",
+          not is_open({"resume": {"stage": "absorbed"}})
+          and is_open({"resume": {"stage": "queued"}})
+          and "absorbed" not in DONE_STAGES and CARRY_CLOSED == CLOSED_STAGES,
+          (CLOSED_STAGES, CARRY_CLOSED))
+    ab = {"groups": [{"group": "A", "resume": {"stage": "absorbed"}},
+                     {"group": "B", "after": ["A"], "resume": {"stage": "queued"}}]}
+    check("an absorbed group is not in the open set or the dependency depth",
+          list(open_groups(ab)) == ["B"] and depth_of(ab)["B"] == 1 and depth_of(ab)["A"] == 1, depth_of(ab))
+    covered_gates = [
+        "code-owned CI: mandated approval under 6329234399",
+        "Policy: tvofi approves or mandate 6329234399",
+        "code-owned: .claude/hooks/",
+        "budget: a measurement change may move a ratchet metric",
+        "D10.md is policy; .github/workflows code-owned (approve under mandate 6329234399)"]
+    check("gate_kind: every gate shape on the roster is covered",
+          all(gate_kind(t) == "covered" for t in covered_gates),
+          [gate_kind(t) for t in covered_gates])
+    check("gate_kind: a pending decision is owner; no gate is None",
+          gate_kind("owner decision after the probe") == "owner"
+          and gate_kind("") is None and gate_kind(None) is None)
     check("stranded: a pending carry on a done or absorbed group, never on an "
           "open one", got == [("G", 1), ("AB", 0), ("AB", 1)], got)
 
diff --git a/tools/plan/replan.py b/tools/plan/replan.py
index 7a27ac5d1..0b9698882 100644
--- a/tools/plan/replan.py
+++ b/tools/plan/replan.py
@@ -201,7 +201,7 @@ def groups_of(roster: dict) -> dict:
 
 
 def is_done(group: dict) -> bool:
-    return (group.get("resume") or {}).get("stage") in ("done", "rca-done")
+    return not roster_lib.is_open(group)
 
 
 def roster_lane(group: dict) -> str:
@@ -1298,6 +1298,12 @@ def selftest() -> int:
             failures.append(name)
 
     plan = build_plan(roster, durations, caps, start, "v1.0.0", round_n=FIXTURE_ROUND)
+    absorbed = dict(roster, groups=roster["groups"] + [
+        {"group": "X", "size": "S", "lane": "Core model", "kind": "defect",
+         "after": [], "resume": {"stage": "absorbed", "absorbed_into": "A"}}])
+    pa = build_plan(absorbed, durations, caps, start, "v1.0.0", round_n=FIXTURE_ROUND)
+    expect("an absorbed group is closed work, not scheduled", pa["groups"]["X"].get("done") is True,
+           str(pa["groups"].get("X")))
     again = build_plan(roster, durations, caps, start, "v1.0.0", round_n=FIXTURE_ROUND)
     expect("deterministic: two runs are byte-identical",
            json.dumps(plan, sort_keys=True) == json.dumps(again, sort_keys=True))

## Before you return the verdict (P275)
Run `python3 -I tools/audit/carry_audit.py check --body <PR body file> --comments <file holding [{"id": 0, "body": <verdict.md text>}]>`. Give every reported item its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>`;
an evidence line flagged by its wording takes `Carry: dismissed: evidence, not a finding`. Return the verdict only at rc 0.
