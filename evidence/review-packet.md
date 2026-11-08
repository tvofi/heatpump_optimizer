# Review packet #3342
head: 88690628b6feb50266cdcdb175b2a9c293db472a
base: cb5512741638029289deb392b30bc246fa667387

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: green
CodeQL id=128822133723 success
arch-score / arch-score id=128831628764 success
arm id=128821925834 skipped
budget-raise-gate / budget-raise-gate id=128831597666 success
cancel-superseded id=128831640289 success
codeql id=128831597454 skipped
codeql / Analyze (actions) id=128822090387 success
codeql / Analyze (javascript-typescript) id=128822090280 success
codeql / Analyze (python) id=128822090311 success
gate id=128831596485 success
governance id=128831622795 skipped
governance / delivery-status id=128822090401 success
governance / delivery-status-publish id=128822091445 skipped
governance / env-matrix id=128822090331 success
governance / instrument-self-tests id=128822090379 success
governance / policy-docs id=128822090369 success
governance / record id=128822091892 skipped
governance / wave-script id=128822090399 success
hassfest id=128831596601 skipped
hassfest / hassfest id=128822090235 success
kernel-points id=128831597275 skipped
pr-contract id=128831622363 skipped
pr-contract / pr-contract id=128826311958 success
prelude id=128831641230 success
refresh id=128831597316 success
tests id=128831597393 skipped
tests / arch-instrument id=128822273191 success
tests / briefs id=128822090303 success
tests / browser id=128822273217 success
tests / ci-ratchet id=128826162697 skipped
tests / claims-autofix id=128824621093 skipped
tests / closure-scope id=128822090394 success
tests / closures id=128822273139 success
tests / closures-autofix id=128826097896 skipped
tests / coverage id=128822273269 success
tests / coverage-ratchet id=128826161541 success
tests / fast (3.14) id=128822273172 success
tests / graders-head-copy id=128826161493 success
tests / lane-proofs id=128826161501 success
tests / mutation id=128822090314 success
tests / mutation-autofix id=128822280982 skipped
tests / mutation-pins id=128822281037 skipped
tests / nightly-ha id=128822274605 skipped
tests / nightly-status id=128822090341 success
tests / replay id=128822274532 skipped
tests / typing id=128822273097 success
validate id=128831631102 skipped
validate / validate-hacs id=128822090285 success

## Refusals
none

## Advisories
hot-file: HPO_BUS_TRAIN_STATE is unset, so every merge verdict reads unboarded

## carry_audit at the head
CARRY-AUDIT: 0 finding item(s): 0 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
ok         python3 tools/audit/carry_audit.py roster
             `tools/audit/carry_audit.py` is in the tree at this head
  ok         PYTHONPATH=tests/hastub python3 tools/audit/seat/orchestrator_tick.py --self-test
             `tools/audit/seat/orchestrator_tick.py` is in the tree at this head
  ok         python3 tools/audit/seat/roster_sync.py --self-test
             `tools/audit/seat/roster_sync.py` is in the tree at this head
  ok         python3 tools/audit/seat/roster_edit.py --self-test
             `tools/audit/seat/roster_edit.py` is in the tree at this head
  ok         python3 tests/structure.py
             `tests/structure.py` is in the tree at this head
  ok         PYTHONPATH=tests/hastub python3 tests/entities.py
             `tests/entities.py` is in the tree at this head

FIGURES: 6 resolved, 0 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
none

## Three-dot diff
diff --git a/dev/programme/delivery/3342.md b/dev/programme/delivery/3342.md
new file mode 100644
index 000000000..8d2f80e6b
--- /dev/null
+++ b/dev/programme/delivery/3342.md
@@ -0,0 +1 @@
+- [#3342](https://github.com/tvofi/heatpump_optimizer/pull/3342) — **open**, R10-ROSTER-READ-SWEEP: roster read sweep, part 2 (R10-ROSTER-READ-SWEEP)
diff --git a/tools/audit/seat/orchestrator_tick.py b/tools/audit/seat/orchestrator_tick.py
index ececf246d..bd08d47ce 100644
--- a/tools/audit/seat/orchestrator_tick.py
+++ b/tools/audit/seat/orchestrator_tick.py
@@ -2237,6 +2237,7 @@ class Tick:
                 self.line(S, f"{len(gated)} group(s) blocked on owner "
                              f"disposition{age} -- surface them to the owner",
                           flag=True)
+            self.roster_invariants(S, rl)
         # throughput stall: verdicted+green entries, no train, no main progress
         if queue and not self._seat_procs(self.proc("merge_train.py"),
                                           "merge_train.py", python_only=True):
@@ -2393,6 +2394,53 @@ class Tick:
                 self.line(S, f"  ... {len(rows) - CAP_CARRY} more; run the command above", flag=True)
         self.line(S, f"carry sweep: {summary[0]} (refs {', '.join(refs)}, last {self.carry_last})")
 
+    def roster_invariants(self, S: str, rl) -> None:
+        """#2733's routing invariants at tick level: `carry_audit.py roster`
+        over the tick's roster ref, with the open issues when `gh issue list`
+        answers. A stranded carry (a pending carry on a closed group) or an
+        unrouted open issue is flagged with the command, so neither
+        accumulates between sweeps. A tool that cannot be read is one
+        UNREADABLE line."""
+        if self._carry is None and not (ROOT / CARRY_AUDIT).is_file():
+            return
+        argv = ["--roster-ref", self._roster_ref(S, rl, announce=False), "roster"]
+        tmp = None
+        code, o = self.gh(["issue", "list", "--repo", self.repo, "--state", "open",
+                           "--limit", "500", "--json", "number"])
+        if code == 0:
+            try:
+                json.loads(o)
+                fd, tmp = tempfile.mkstemp(suffix=".json")
+                with os.fdopen(fd, "w") as fh:
+                    fh.write(o)
+                argv += ["--open-issues", tmp]
+            except ValueError:
+                pass
+        try:
+            rc, out = self.carry_run(argv)
+        except OSError as e:
+            self.unreadable(S, "roster invariants", str(e)[:80])
+            return
+        finally:
+            if tmp:
+                try:
+                    os.unlink(tmp)
+                except OSError:
+                    pass
+        summary = [l for l in out if l.startswith("CARRY-ROSTER:")]
+        if rc not in (0, 1) or not summary:
+            self.unreadable(S, "roster invariants", f"exit {rc}, "
+                            + (out[-1][:100] if out else "no output"))
+            return
+        if rc == 1:
+            rows = [l for l in out if l.startswith(("STRANDED", "ISSUE"))]
+            self.line(S, f"routing invariants broken ({summary[0][:120]}): "
+                         "route each with roster_edit.py "
+                         f"(`python3 -I {CARRY_AUDIT} {' '.join(argv[:3])}`)",
+                      flag=True)
+            for l in rows[:CAP_CARRY]:
+                self.line(S, f"  {l.strip()[:160]}", flag=True)
+
     # ----------------------------------------------------------------- ETA
     def eta(self) -> None:
         """ETA deviation, three sources by precision: the train beat's age
@@ -2722,6 +2770,8 @@ def self_test() -> int:
         git.on(("cat-file", "-e"), rc=1)  # rows missing unless a stub says otherwise
         kw.setdefault("relay_log", os.devnull)  # hermetic: never the host's relay log
         kw.setdefault("bus_state", str(tmp / "no-bus"))  # nor its dispatch record
+        # hermetic: never the real carry_audit; the routing-invariants read is clean
+        kw.setdefault("carry", lambda argv: (0, ["CARRY-ROSTER: stub; 0 stranded carry(ies)"]))
         t = Tick("o/r", str(kw.pop("checkout", ROOT)), queue=queue,
                  train_log=train_log, workers_file=workers, roster_file=roster,
                  gh=gh, git=git, proc=procs or (lambda pattern: []),
@@ -2841,6 +2891,29 @@ def self_test() -> int:
              any("1 group(s) blocked on owner" in x["text"] for x in tg_own.findings)),
         ])
         total, failed = total + a, failed + f
+        ri_calls: list = []
+        ri_out = ["STRANDED R10-X (absorbed) carry[0]: 'c'",
+                  "CARRY-ROSTER: r.json at origin/r10; 1 stranded carry(ies)"]
+        tg_roster_path = str(tmp / "ri-roster.json")
+        Path(tg_roster_path).write_text(json.dumps({"groups": [
+            {"group": "G-RI", "resume": {"stage": "not-started"}}]}))
+        tri = tick(queue=str(q16), roster=tg_roster_path, gh_extra=[(("issue", "list"), 0, '[{"number": 5}]')],
+                   carry=lambda argv: ri_calls.append(argv) or (1, ri_out))
+        tri.replan()
+        tri0 = tick(queue=str(q16), roster=tg_roster_path,
+                    carry=lambda argv: (0, ["CARRY-ROSTER: r.json; 0 stranded carry(ies)"]))
+        tri0.replan()
+        a, f = check("REPLAN routing invariants at tick level", [
+            ("a stranded carry flags one line naming the command",
+             any("routing invariants broken" in x["text"] and "carry_audit.py" in x["text"]
+                 for x in tri.findings)),
+            ("the row is printed", any("STRANDED R10-X" in x["text"] for x in tri.findings)),
+            ("the roster call carries --open-issues when gh answers",
+             bool(ri_calls) and "--open-issues" in ri_calls[0] and "roster" in ri_calls[0]),
+            ("null: a clean roster flags nothing from the invariant",
+             not any("routing invariants" in x["text"] for x in tri0.findings)),
+        ])
+        total, failed = total + a, failed + f
         t = tick(procs=lambda pattern: [(11, "python3 merge_train.py"),
                                         (12, "python3 merge_train.py")])
         t.train()
diff --git a/tools/audit/seat/r10_roster_ops_mutants.py b/tools/audit/seat/r10_roster_ops_mutants.py
index 8d5f41342..ca3f49cd9 100644
--- a/tools/audit/seat/r10_roster_ops_mutants.py
+++ b/tools/audit/seat/r10_roster_ops_mutants.py
@@ -67,6 +67,7 @@ Plants, one per refusal of the two ops and per round-trip property:
            naming no live group (W12, W13) or needing none (W14), and a phase
            branch unresolved in roster_lib.group_for_branch (W15).
 
+    W18 append-carry's refusal of text already ending in a mark.
     W16-W17 the lane marker on structural ops (carry 15): the guard dropped
            (W16) and set-stage wrongly made structural (W17); Q13 is the
            queue runner not setting it.
@@ -307,6 +308,8 @@ PLANTS.update({
     "W16": ("    if op in STRUCTURAL_OPS and os.environ.get(LANE_ENV) != LANE_VALUE:\n",
             "    if False:\n"),
     "W17": ('STRUCTURAL_OPS = ("wire-issue",', 'STRUCTURAL_OPS = ("set-stage", "wire-issue",'),
+    "W18": ("    if mark:\n        raise Refuse(f\"append-carry: the text already ends",
+            "    if False:\n        raise Refuse(f\"append-carry: the text already ends"),
     "Q13": (RQ, '    env["HPO_ROSTER_LANE"] = "queue-runner"', '    env["HPO_ROSTER_LANE"] = "x"'),
     "Q9": (RQ, '    if "def batch_edit" not in Path(path).read_text():\n',
            '    if False:\n'),
diff --git a/tools/audit/seat/roster_edit.py b/tools/audit/seat/roster_edit.py
index df8cccd8e..15dccccbf 100644
--- a/tools/audit/seat/roster_edit.py
+++ b/tools/audit/seat/roster_edit.py
@@ -445,6 +445,11 @@ def op_append_carry(roster, group, text):
     if resume.get("pr"):
         print(f"WARN carry to {group}: PR #{resume['pr']} is open on it")
     entry = _text(text)
+    mark = roster_lib.carry_mark(entry)
+    if mark:
+        raise Refuse(f"append-carry: the text already ends in a [{mark[0]}: "
+                     f"{mark[1]}] mark, which reads as discharged on arrival; "
+                     "strip it and let the discharging op write it")
     carry = g.setdefault("carry", [])
     if entry in carry:
         raise Refuse(f"{group} already carries that entry")
@@ -1684,6 +1689,9 @@ def _self_test() -> int:
           and branch_roster()["groups"][0]["carry"] == ["carry text one"])
     check("dup carry refused",
           edit("append-carry", "R9-A", "carry text one") == 2)
+    check("append-carry refuses text ending in a mark-shaped suffix",
+          edit("append-carry", "R9-A", "fresh text [implemented: abc123]") == 2
+          and branch_roster()["groups"][0]["carry"] == ["carry text one"])
     check("unknown group refused", edit("set-stage", "R9-ZZ", "done") == 2)
 
     # The triage gate (decision 0015). The ruling batch lands on origin/main;
diff --git a/tools/audit/seat/roster_sync.py b/tools/audit/seat/roster_sync.py
index 733901b7b..cfd64b91a 100644
--- a/tools/audit/seat/roster_sync.py
+++ b/tools/audit/seat/roster_sync.py
@@ -1161,6 +1161,9 @@ def self_test() -> int:
               "SKIP R9-DEFER: stage deferred is a human disposition" in out, out)
         check("the dry run plans no append of an item the destination holds",
               "carry R9-HELD +=" not in out, out)
+        check("an item the destination holds verbatim is skipped silently, "
+              "not refused as a near-duplicate (M9)",
+              "REFUSED Carry: R9-HELD" not in out, out)
         check("the dry run refuses an item the destination already carries: "
               "same finding, same triage ruling", "REFUSED Carry: R9-FROM "
               "from #15: already carried" in out, out)

## Before you return the verdict (P275)
Run `python3 -I tools/audit/carry_audit.py check --body <PR body file> --comments <file holding [{"id": 0, "body": <verdict.md text>}]>`. Give every reported item its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>`;
an evidence line flagged by its wording takes `Carry: dismissed: evidence, not a finding`. Return the verdict only at rc 0.
