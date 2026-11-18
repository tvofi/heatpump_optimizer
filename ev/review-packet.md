# Review packet #3732
head: 8e0363b8902905a78733e8f0fe7a2b27fd8c3211
base: ae0ed64af898d8923ac35afe6e9c031ac1e6b111

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: red
CodeQL id=135153728778 success
arch-score / arch-score id=135179491566 success
arm id=135145856342 skipped
budget-raise-gate / budget-raise-gate id=135179491541 success
cancel-superseded id=135179490608 success
codeql id=135179491652 skipped
codeql / Analyze (actions) id=135152542099 success
codeql / Analyze (javascript-typescript) id=135152542084 success
codeql / Analyze (python) id=135152542022 success
gate id=135179491192 success
governance id=135179491563 skipped
governance / env-matrix id=135152542594 success
governance / instrument-self-tests id=135152542494 success
governance / policy-docs id=135152542275 success
governance / record id=135152545353 skipped
governance / wave-script id=135152542283 success
hassfest id=135179491278 skipped
hassfest / hassfest id=135152542150 success
kernel-points id=135179491589 skipped
pr-contract id=135179492543 skipped
pr-contract / pr-contract id=135177333121 success
prelude id=135179579135 success
refresh id=135179490091 success
sweep-self id=135179967127 skipped
tests id=135179491879 skipped
tests / arch-instrument id=135155268546 success
tests / briefs id=135152542313 success
tests / browser id=135155268443 success
tests / ci-ratchet id=135176439066 skipped
tests / claims-autofix id=135170542483 skipped
tests / closure-scope id=135152542314 success
tests / closures id=135155268597 success
tests / closures-autofix id=135176438801 skipped
tests / coverage id=135155268528 success
tests / coverage-ratchet id=135176170335 success
tests / fast (3.14) id=135155268207 success
tests / graders-head-copy id=135176170264 success
tests / lane-proofs id=135176170324 success
tests / mutation id=135152542376 success
tests / mutation-autofix id=135155938764 skipped
tests / mutation-pins id=135155936916 skipped
tests / nightly-ha id=135155271887 skipped
tests / nightly-status id=135152542585 failure
tests / replay id=135155272015 skipped
tests / typing id=135155268465 success
validate id=135179569446 skipped
validate / validate-hacs id=135152542133 success

## Refusals
none

## Advisories
none

## carry_audit at the head
CARRY-AUDIT: 0 finding item(s): 0 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
FIGURES: 0 resolved, 0 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
none

## Review scope: full (first round: no --reviewed-head)

## Three-dot diff
diff --git a/dev/audit/README.md b/dev/audit/README.md
index 0017e0d438..20c26f0f46 100644
--- a/dev/audit/README.md
+++ b/dev/audit/README.md
@@ -38,8 +38,14 @@ or removed one goes red. Decision 0016 ties a round to its major version.
 | 10 post-merge beat and state docs | a merge | row, handover and state docs current | `tools/audit/seat/postmerge.py`, `tools/audit/seat/beatd.py`, `tools/audit/seat/state_docs.py` | `dev/governance/rules/delivery-status-tracking.md` | `dev/programme/delivery/`, `dev/programme/HANDOVER.md`, a #201 comment |
 | 11 stamps | merges since the last tag | the tag pushed | `tools/release/stamp.py`, `.claude/workflows/web-stamp.js` | `orchestrator.md` section 13 | the tag and release notes |
 | 12 projections and extension | a wave edge | the plan re-projected; a new group appended | `tools/plan/replan.py`, `tools/audit/seat/plan_page.py`, `tools/audit/seat/flow_metrics.py` | `orchestrator.md` section 2b | the projection, a roster group |
+| 12b instrument prototype and proposal triage | about 24 h before closeout | the plan's groups in the next round's roster | `tools/audit/seat/roster_edit.py` | `proposal-triage.md` | the batch's `## Plan` |
 | 13 closure | every phase drained | the criteria below hold | `tools/audit/seat/state_docs.py`, `tools/audit/seat/handover_prompt.py`, `tools/audit/seat/resume_doc.py` | `orchestrator.md` section 9 | the final state comment on #201; the round's objective record |
 
+**Phase 12b**: one Fable seat (else opus) consolidates instrument proposals and
+the prototype overlays in the state directory's per-round prototype folder and plans each ACCEPT as the batch's `## Plan`, shaped as
+`architect-planner.md`'s; on another seat's `Plan review: approve <sha>`
+(`plan-review.md`) the orchestrator creates its groups.
+
 Lessons (triage batch 141, P545): stack a later part only under the stack
 study's conditions, at the parent's merge verdict, never its handoff; log a cloud fire by the
 session id `list_runs` shows about 2 min later, never by the trigger id, which
diff --git a/dev/governance/roles/proposal-triage.md b/dev/governance/roles/proposal-triage.md
index 0ae1a56a71..7d2099c144 100644
--- a/dev/governance/roles/proposal-triage.md
+++ b/dev/governance/roles/proposal-triage.md
@@ -1,11 +1,11 @@
 # The proposal-triage seat's contract
 
-A process, tooling or instrument proposal (sweep, seat results, verdict notes)
-passes this gate before building (decision 0015); a required countermeasure
-(root cause, red-check carry, finding fix) keeps its route. **Once per round**
-(tvofi, 2026-11-14): the round's proposals are consolidated and triaged
-together at round end by one opus seat, medium effort; an ACCEPT is built at
-the start of the next round. Check rulings against code.
+A process, tooling or instrument proposal passes this gate before building
+(decision 0015); a required countermeasure (root cause, red-check carry, finding
+fix) keeps its route. **Once per round** (tvofi, 2026-11-14): one opus seat,
+medium effort, triages the round's proposals at round end; ACCEPTs are built at
+the next round's start. Instrument ones go to phase 12b (`dev/audit/README.md`;
+tvofi, 2026-11-18). Check rulings against code.
 
 **By instrument** (card L5): one ruling per instrument named; its third change
 in a round is ruled retire, simplify, redesign (`designer.md`) or leave, never a
@@ -15,10 +15,10 @@ patch.
 time; tokens (model x effort x runs); API calls; standing CPU (Pi-class, CI
 runners); complexity (lines, new files, checks, hot files, review rounds);
 maintenance; induced work (`defect-root-cause.md`). A countermeasure takes
-`root-cause.md` section 5's rungs in order (D11's mechanise-first: repair before
-refuse). Even or marginal: REJECT; unmeasured: DEFER, never ACCEPT. Blocking no
-production merge: LOG, bar the exemption in `dev/audit/README.md`. An exemption
-ACCEPT (over 20% on a `ratchet-budgets.md` measure) says so; its PR records it.
+`root-cause.md` section 5's rungs in order (repair before refuse). Even or
+marginal: REJECT; unmeasured: DEFER, never ACCEPT. Blocking no production merge:
+LOG, bar the exemption in `dev/audit/README.md`. An exemption ACCEPT (over 20%
+on a `ratchet-budgets.md` measure) says so; its PR records it.
 
 **Machinery.** A planned machinery group, or a non-production CI lane or seat,
 stays only on a measured gain of at least 10% on them. Repair of such code
diff --git a/dev/programme/delivery/3732.md b/dev/programme/delivery/3732.md
new file mode 100644
index 0000000000..44c501a5a1
--- /dev/null
+++ b/dev/programme/delivery/3732.md
@@ -0,0 +1 @@
+- [#3732](https://github.com/tvofi/heatpump_optimizer/pull/3732) — **open**, policy: round-end instrument prototype and proposal triage phase
diff --git a/tools/audit/seat/plan_phases.py b/tools/audit/seat/plan_phases.py
index aeac81b480..09927a06f6 100644
--- a/tools/audit/seat/plan_phases.py
+++ b/tools/audit/seat/plan_phases.py
@@ -49,7 +49,8 @@ from pathlib import Path
 
 # The playbook's order (dev/audit/README.md): round start holds the pickup,
 # the start evaluation and the finder-critical groups; fix waves are the
-# roster's group lanes (playbook phases 5 to 10).
+# roster's group lanes (playbook phases 5 to 10); instrument triage is phase
+# 12b, opening about 24 h before closeout, ahead of closure.
 PHASES = (
     ("round-start", "Round start"),
     ("finders", "Finders"),
@@ -57,6 +58,7 @@ PHASES = (
     ("plan", "Architect plan"),
     ("fix-waves", "Fix waves"),
     ("stamps", "Stamps"),
+    ("instrument-triage", "Instrument prototype and proposal triage"),
     ("closure", "Closure"),
 )
 STATUSES = {"not-started": "not started", "running": "running",
@@ -363,7 +365,8 @@ def shown(path: str | Path, repo: str | Path) -> str:
 
 def fixture() -> dict:
     """A round with each status on a phase and on an item, a forecast with
-    its basis, and two phases (fix waves, closure) the file does not list."""
+    its basis, and three phases (fix waves, instrument triage, closure) the file
+    does not list."""
     return {"round": 9, "as_of": "2026-01-05T12:00:00Z", "phases": [
         {"phase": "round-start", "status": "done", "started": "2026-01-01T00:00:00Z",
          "finished": "2026-01-02T00:00:00Z", "entry": "ENTRY-RS", "exit": "EXIT-RS",
@@ -399,6 +402,11 @@ def fixture_checks(check) -> None:
     refuses(lambda d: d["phases"].reverse(), "out of the playbook's order")
     refuses(lambda d: d["phases"].insert(1, dict(ph(d, 0))), "out of the playbook's order")
     refuses(lambda d: ph(d, 0).update(phase="intake"), "unknown phase")
+    check("phases: instrument triage sits after stamps and before closure, in the playbook's order",
+          [p for p, _ in PHASES][-3:] == ["stamps", "instrument-triage", "closure"], PHASES)
+    refuses(lambda d: d["phases"].extend([{"phase": "closure", "status": "not-started"},
+                                          {"phase": "instrument-triage", "status": "not-started"}]),
+            "out of the playbook's order")
     refuses(lambda d: ph(d, 2).pop("waiting_on"), "waiting on nothing named")
     refuses(lambda d: ph(d, 1)["items"][2].pop("waiting_on"), "waiting on nothing named")
     refuses(lambda d: ph(d, 4).update(started="2026-01-07T00:00:00Z"), "a date on a not-started phase")
@@ -409,8 +417,8 @@ def fixture_checks(check) -> None:
     rows = rows_of(doc)
     check("phases: every playbook phase is a row, in order; an unlisted one is not started",
           [r["phase"] for r in rows] == [p for p, _ in PHASES]
-          and [r["status"] for r in rows if r["phase"] in ("fix-waves", "closure")]
-          == ["not-started"] * 2, [(r["phase"], r["status"]) for r in rows])
+          and [r["status"] for r in rows if r["phase"] in ("fix-waves", "instrument-triage", "closure")]
+          == ["not-started"] * 3, [(r["phase"], r["status"]) for r in rows])
     s = section(doc, [], "dev/programme/round9/phases.json")
     tr = {m.group(1): m.group(0) for m in re.finditer(r'<tr data-phase="([a-z-]+)".*?</tr>', s, re.S)}
     check("phases: the section draws a row per phase in the playbook's order",

## Before you return the verdict (P275)
Run `python3 -I tools/audit/carry_audit.py check --body <PR body file> --comments <file holding [{"id": 0, "body": <verdict.md text>}]>`. Give every reported item its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>`;
an evidence line flagged by its wording takes `Carry: dismissed: evidence, not a finding`. Return the verdict only at rc 0.
