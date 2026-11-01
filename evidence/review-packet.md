# Review packet #3075
head: fe4af42579764bb8010e875ac5adb56ac542b3a0
base: b5df066e7a23e914ee81de83ef243097b3b397a3

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: pending
CodeQL id=124779186961 neutral
arch-score / arch-score id=124779043301 success
arm id=124778944623 skipped
budget-raise-gate / budget-raise-gate id=124779043307 success
cancel-superseded id=124778946266 success
codeql / Analyze (actions) id=124779043268 success
codeql / Analyze (javascript-typescript) id=124779043316 success
codeql / Analyze (python) id=124779043367 in_progress
governance / delivery-status id=124779043440 success
governance / delivery-status-publish id=124779044152 skipped
governance / env-matrix id=124779043401 in_progress
governance / instrument-self-tests id=124779043354 in_progress
governance / policy-docs id=124779043425 in_progress
governance / record id=124779044343 skipped
governance / wave-script id=124779043365 success
hassfest / hassfest id=124779043412 success
kernel-points id=124779043821 skipped
prelude id=124778946331 success
refresh id=124778946374 success
tests / arch-instrument id=124779130905 success
tests / briefs id=124779043339 success
tests / browser id=124779130853 in_progress
tests / closure-scope id=124779043369 success
tests / closures id=124779130881 in_progress
tests / coverage id=124779130872 in_progress
tests / fast (3.14) id=124779130840 in_progress
tests / mutation id=124779043372 success
tests / mutation-autofix id=124779147488 skipped
tests / mutation-pins id=124779147543 skipped
tests / nightly-ha id=124779131877 skipped
tests / nightly-status id=124779043309 success
tests / replay id=124779131914 skipped
tests / typing id=124779130883 success
validate / validate-hacs id=124779043298 success

## Refusals
none

## Advisories
none

## carry_audit at the head
CARRY-AUDIT: 0 finding item(s): 0 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
ok         python3 -I tools/plan/replan.py --self-test
             `tools/plan/replan.py` is in the tree at this head
  ok         python3 -I tools/audit/seat/plan_page.py --self-test
             `tools/audit/seat/plan_page.py` is in the tree at this head
  ok         PYTHONPATH=tests/hastub python3 -I tools/audit/seat/state_docs.py --self-test
             `tools/audit/seat/state_docs.py` is in the tree at this head
  ok         python3 -I tools/plan/replan.py --roster-ref e71a089ea915a04960643dac50519aefdf3befa3 --start 2026-10-31T12:00:00Z --out plan.json
             `tools/plan/replan.py` is in the tree at this head
  unverified git grep -n -i -e 'minor=True' -e '"minor"' -e 'minor stamp' -e 'the minor at' -e 'closure_stamp' -- tools tests
             `git grep` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  ok         tools/release/stamp.py
             `tools/release/stamp.py` is in the tree at this head
  ok         tests/finite_boundary.py
             `tests/finite_boundary.py` is in the tree at this head
  ok         tools/audit/carry_audit.py
             `tools/audit/carry_audit.py` is in the tree at this head
  ok         tools/audit/seat/r10_stamp_round_mutants.py
             `tools/audit/seat/r10_stamp_round_mutants.py` is in the tree at this head
  ok         python3 tests/structure.py
             `tests/structure.py` is in the tree at this head
  ok         python3 tests/closure.py select --diff 8fec54ee2afb5e37687f34bc5fd3aa7280f64e1f
             `tests/closure.py` is in the tree at this head
  ok         tests/entities.py
             `tests/entities.py` is in the tree at this head
  ok         python3 tools/pr/ci_predict.py
             `tools/pr/ci_predict.py` is in the tree at this head
  ok         PYTHONPATH=tests/hastub python3 tests/entities.py
             `tests/entities.py` is in the tree at this head
  ok         tools/audit/seat/state_docs.py --self-test passes
             `tools/audit/seat/state_docs.py` is in the tree at this head
  ok         bash tools/pr/prepr.sh body.md
             `tools/pr/prepr.sh` is in the tree at this head

FIGURES: 15 resolved, 1 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
none

## Three-dot diff
diff --git a/dev/programme/delivery/3075.md b/dev/programme/delivery/3075.md
new file mode 100644
index 000000000..ef7fe8b9f
--- /dev/null
+++ b/dev/programme/delivery/3075.md
@@ -0,0 +1 @@
+- [#3075](https://github.com/tvofi/heatpump_optimizer/pull/3075) — **open**, R10-FLY-CLOSURE-MAJOR: the round-closing stamp plans as vN.0.0 (R10-FLY-CLOSURE-MAJOR)
diff --git a/tools/audit/seat/plan_page.py b/tools/audit/seat/plan_page.py
index 4c5c8b060..80b31c016 100644
--- a/tools/audit/seat/plan_page.py
+++ b/tools/audit/seat/plan_page.py
@@ -260,8 +260,8 @@ def swimlanes(plan: dict, rows: list) -> tuple[str, int]:
     it draws (a link crossing more than one lane or two hours is left to the
     ◆ marks and the caption)."""
     now = _t(plan["generated"]["start"])
-    # The axis runs to the last planned stamp: the minor stamp lands after
-    # closure, and an axis ending at closure would not draw it.
+    # The axis runs to the last planned stamp: the round-close stamp lands
+    # after closure, and an axis ending at closure would not draw it.
     end = max([_t(plan["summary"]["closure"])] + [_t(s["at"]) for s in plan["stamps"]])
     slots = plan["generated"]["caps"]["slots"]
     span_h = max(1.0, (end - now).total_seconds() / 3600)
@@ -523,7 +523,7 @@ def render(roster: dict, roster_src: str, plan: dict, snap: dict) -> str:
             f"{inherited} inherited in-progress coordinator groups are recorded in "
             f"plan.json. The line above the lanes is how many groups are in flight at "
             f"each hour, riding the cap. Stamps: one patch per {every} production groups, "
-            f"the minor at closure. Hover any bar, however narrow, for its name, state, "
+            f"the round's major at closure. Hover any bar, however narrow, for its name, state, "
             f"start, ETA and wave. {drawn} of {max(0, len(chain) - 1)} critical-path links "
             f"are drawn; the ◆ and the caption carry the rest."),
         "sizes": e(sizes),
@@ -709,7 +709,8 @@ def _self_test() -> int:
             commit(roster)
             r_, ref_, blob_ = replan.load_roster(str(repo), "main")
             plan = replan.build_plan(r_, durations, dict(replan.DEFAULT_CAPS), start,
-                                     "v1.0.0", ref_, blob_)
+                                     "v1.0.0", ref_, blob_,
+                                     round_n=roster_lib.roster_round(str(rpath)))
             planf, snapf = Path(td) / "plan.json", Path(td) / "snap.json"
             planf.write_text(json.dumps(plan), encoding="utf-8")
             snapf.write_text(json.dumps(snap), encoding="utf-8")
@@ -820,6 +821,10 @@ def _self_test() -> int:
                   and any(rows[g]["tier"] == 1 for g in rows if rows[g]["st"] != "done"),
                   {g: rows[g]["tier"] for g in rows})
             check("a planned stamp is drawn", 'class="stampline"' in page)
+            check("the closure stamp renders as the round's major, kind round-close",
+                  '<td class="mono">v9.0.0</td>' in page
+                  and f'<td class="mono">{replan.ROUND_CLOSE}</td></tr>' in page
+                  and "v1.1.0" not in page, plan["stamps"][-1])
             check("the filter and hide-merged controls ship",
                   'id="hide-done"' in page and 'data-f="blocked"' in page)
             check("no machine path in the page", not re.search(r"/(home|Users|tmp)/", page))
@@ -1087,7 +1092,7 @@ td.d{min-width:260px;max-width:440px}
     <thead><tr><th>Version</th><th>Projected (UTC)</th><th>Carries</th><th>Kind</th></tr></thead>
     <tbody>{{stamps}}</tbody>
   </table></div>
-  <p class="note">Cadence: one patch stamp per {{every}} production groups merged, once main's Tests are green and the release notes name every merged PR. The minor stamp closes the programme.</p>
+  <p class="note">Cadence: one patch stamp per {{every}} production groups merged, once main's Tests are green and the release notes name every merged PR. The round-close stamp closes the programme: round N's major, vN.0.0, the version <code>stamp.py --round-close N</code> assigns.</p>
 </section>
 
 <section>
diff --git a/tools/audit/seat/state_docs.py b/tools/audit/seat/state_docs.py
index ab7e6e167..1b9ffbd5f 100644
--- a/tools/audit/seat/state_docs.py
+++ b/tools/audit/seat/state_docs.py
@@ -623,7 +623,8 @@ def plan_page_arms(root: Path, ok, git) -> None:
                            .read_text(encoding="utf-8"))
     r_, ref_, blob_ = replan.load_roster(str(drv), "main")
     plan = replan.build_plan(r_, durations, dict(replan.DEFAULT_CAPS),
-                             dt.datetime(2026, 1, 5), "v1.0.0", ref_, blob_)
+                             dt.datetime(2026, 1, 5), "v1.0.0", ref_, blob_,
+                             round_n=roster_lib.roster_round(rel))
     planf, snapf = root / "plan.json", root / "psnap.json"
     planf.write_text(json.dumps(plan), encoding="utf-8")
     snapf.write_text(json.dumps({"issues": [], "open_prs": [], "merged_prs": []}),
diff --git a/tools/plan/replan.py b/tools/plan/replan.py
index b26f9a3cf..c0f303379 100644
--- a/tools/plan/replan.py
+++ b/tools/plan/replan.py
@@ -48,7 +48,11 @@ The schedule
 
     A patch stamp is cut once `stamp_every` production groups have merged
     since the last one. A stamp never blocks a dispatch; it pays its own gate
-    run, because `stamp.py` pushes to main.
+    run, because `stamp.py` pushes to main. The programme closes with one
+    `round-close` stamp: round N's major, vN.0.0 (decision 0016), assigned by
+    `stamp.next_version` -- the rule `stamp.py --round-close N` runs -- from
+    the round the roster's path names, so the plan and the stamp cannot
+    disagree on it; a roster naming no round refuses, never defaults.
 
 Why it checks what it checks
     A schedule that violates a cap is not a plan. `--check` refuses (exit 1)
@@ -68,7 +72,7 @@ Why it checks what it checks
     `--self-test` plants each violation and proves the refusal fires.
 
 plan.json shape
-    schema; generated {roster_ref, roster_blob, start, version, durations,
+    schema; generated {roster_ref, roster_blob, start, version, round, durations,
     model {sizes_hours, live_remaining_fraction, sizes_provenance}, caps,
     inherited_coordinator, inherited_dependency_violations}; summary {closure,
     wall_hours, ci_minutes, batches, stamps, ...}; critical_path [group...];
@@ -92,6 +96,9 @@ sys.path.insert(0, os.environ.get("REPLAN_SEAT_DIR")
                or str(Path(__file__).resolve().parent.parent / "audit" / "seat"))
 import roster_lib  # noqa: E402 -- the one owner of which roster a tool reads
 
+sys.path.insert(0, str(Path(roster_lib.__file__).resolve().parents[2] / "release"))
+import stamp  # noqa: E402 -- the one owner of the version a stamp assigns
+
 SELF = "tools/plan/replan.py"
 
 # Production lanes cut a stamp. Instrument, Replay and Docs work does not, on
@@ -104,6 +111,9 @@ PRODUCTION = ("Learners", "Core model", "Product UX")
 # are derived from the roster graph at every replan; none is stored.
 TIER_CRITICAL, TIER_PRODUCTION, TIER_OTHER = 0, 1, 2
 
+# The kind of the one stamp that closes the programme: the round's major.
+ROUND_CLOSE = "round-close"
+
 # A fixer already working. `queued` is not working: the plan dispatches it.
 LIVE_STAGES = ("in-progress", "fixing", "review", "in-review")
 
@@ -345,7 +355,10 @@ def dispatch_key(n: str, tier: dict, savings: dict, height: dict,
 
 def build_plan(roster: dict, durations: dict, caps: dict, start: dt.datetime,
                version: str, roster_ref: str = "", roster_blob: str = "",
-               roster_path: str = "") -> dict:
+               roster_path: str = "", *, round_n: int) -> dict:
+    closing, why = closure_version(version, round_n)
+    if why:
+        raise PlanError(f"the round-close stamp: {why}")
     G = groups_of(roster)
     deps, open_, done = dependency_graph(G)
     order = topo_order(deps)
@@ -540,14 +553,13 @@ def build_plan(roster: dict, durations: dict, caps: dict, start: dt.datetime,
 
     closure = max(merged_t.values(), default=0)
     # The last fewer-than-`every` production groups are not a patch stamp of
-    # their own: the minor stamp closes the programme and carries them. A
-    # second push there would pay a gate run to bump a version the minor bump
-    # replaces hours later.
-    minor = bump(version, patch, minor=True)
+    # their own: the round-close stamp closes the programme and carries them.
+    # A second push there would pay a gate run to bump a version the round's
+    # major replaces hours later.
     for c in carry:
-        stamp_by_group[c] = minor
-    stamps.append({"version": minor, "at": closure + closure_lead,
-                   "carries": list(carry), "kind": "minor", "batch": None})
+        stamp_by_group[c] = closing
+    stamps.append({"version": closing, "at": closure + closure_lead,
+                   "carries": list(carry), "kind": ROUND_CLOSE, "batch": None})
 
     # a wave is the set of groups the replan dispatches at one instant
     by_open: dict = {}
@@ -623,6 +635,7 @@ def build_plan(roster: dict, durations: dict, caps: dict, start: dt.datetime,
             "roster_blob": roster_blob,
             "start": iso(start, 0),
             "version": version,
+            "round": round_n,
             "durations": durations.get("provenance") or {},
             # The duration model this plan was computed with, so a reader of
             # the plan states the figures it used rather than today's file's.
@@ -674,9 +687,23 @@ def build_plan(roster: dict, durations: dict, caps: dict, start: dt.datetime,
     return plan
 
 
-def bump(version: str, n: int, minor: bool = False) -> str:
+def bump(version: str, n: int) -> str:
+    """The `n`th interim patch stamp after `version`."""
     maj, mi, pa = (int(x) for x in version.lstrip("v").split(".")[:3])
-    return f"v{maj}.{mi + 1}.0" if minor else f"v{maj}.{mi}.{pa + n}"
+    return f"v{maj}.{mi}.{pa + n}"
+
+
+def closure_version(version: str, round_n) -> tuple[str | None, str | None]:
+    """`(vN.0.0, None)` for the stamp closing round `round_n`, or `(None, why)`.
+
+    The rule is `stamp.next_version`'s, the one `stamp.py --round-close N`
+    runs, given the round as both the asked and the roster's round: the plan
+    states the version that command will assign, and refuses where it would.
+    """
+    if isinstance(round_n, bool) or not isinstance(round_n, int):
+        return None, f"no round to close (round {round_n!r})"
+    nxt, why = stamp.next_version(version.lstrip("v"), None, round_n, round_n)
+    return (f"v{nxt}", None) if nxt else (None, why)
 
 
 def gate_minutes(durations: dict) -> float:
@@ -841,15 +868,27 @@ def check_plan(plan: dict) -> list:
                        f"flight (cap {slots})")
 
     # 5. stamp cadence: every `every` production merges cuts one patch stamp;
-    #    the last fewer-than-`every` ride the one minor stamp that closes the
-    #    programme
+    #    the last fewer-than-`every` ride the one round-close stamp that closes
+    #    the programme, last, at the version `closure_version` assigns
     produced = [n for n, g in sorted(
         ((n, g) for n, g in groups.items() if g.get("lane") in PRODUCTION),
         key=lambda x: (mins(x[1]["finish"]), x[0]))]
     patch_stamps = [s for s in plan.get("stamps", []) if s["kind"] == "patch"]
-    minor = [s for s in plan.get("stamps", []) if s["kind"] == "minor"]
-    if len(minor) != 1:
-        bad.append(f"stamp cadence: {len(minor)} minor stamps, expected one")
+    closes = [s for s in plan.get("stamps", []) if s["kind"] == ROUND_CLOSE]
+    gen = plan.get("generated") or {}
+    want, why = closure_version(str(gen.get("version") or ""), gen.get("round"))
+    if len(closes) != 1 or plan["stamps"][-1] is not closes[0]:
+        bad.append(f"round close: {len(closes)} {ROUND_CLOSE} stamps, expected "
+                   "one, and last")
+    elif why:
+        bad.append(f"round close: {why}")
+    elif closes[0]["version"] != want:
+        bad.append(f"round close: the closure stamp is {closes[0]['version']}, "
+                   f"round {gen.get('round')} closes as {want}")
+    stray = [s["kind"] for s in plan.get("stamps", [])
+             if s["kind"] not in ("patch", ROUND_CLOSE)]
+    if stray:
+        bad.append(f"stamp cadence: unknown stamp kind(s) {stray}")
     if len(patch_stamps) != len(produced) // every:
         bad.append(f"stamp cadence: {len(patch_stamps)} patch stamps for "
                    f"{len(produced)} production merges at a cadence of {every}")
@@ -859,11 +898,11 @@ def check_plan(plan: dict) -> list:
         if len(s["carries"]) != every:
             bad.append(f"stamp cadence: {s['version']} carries "
                        f"{len(s['carries'])} production groups, not {every}")
-    if minor:
-        covered.extend(minor[0]["carries"])
-        if len(minor[0]["carries"]) > every:
-            bad.append(f"stamp cadence: the minor stamp carries "
-                       f"{len(minor[0]['carries'])} production groups")
+    if closes:
+        covered.extend(closes[0]["carries"])
+        if len(closes[0]["carries"]) > every:
+            bad.append(f"stamp cadence: the round-close stamp carries "
+                       f"{len(closes[0]['carries'])} production groups")
     if covered != produced:
         bad.append("stamp cadence: stamped production groups do not equal the "
                    "merged production groups, in merge order")
@@ -886,6 +925,7 @@ def check_plan(plan: dict) -> list:
 
 def selftest() -> int:
     caps = dict(DEFAULT_CAPS)
+    FIXTURE_ROUND = 2  # the fixture plans close round 2 from v1.0.0
     durations = {
         "sizes_hours": {"S": 2.0, "M": 4.0, "L": 6.0, "XL": 8.0},
         "live_remaining_fraction": 0.7,
@@ -919,8 +959,8 @@ def selftest() -> int:
         if not cond:
             failures.append(name)
 
-    plan = build_plan(roster, durations, caps, start, "v1.0.0")
-    again = build_plan(roster, durations, caps, start, "v1.0.0")
+    plan = build_plan(roster, durations, caps, start, "v1.0.0", round_n=FIXTURE_ROUND)
+    again = build_plan(roster, durations, caps, start, "v1.0.0", round_n=FIXTURE_ROUND)
     expect("deterministic: two runs are byte-identical",
            json.dumps(plan, sort_keys=True) == json.dumps(again, sort_keys=True))
     bad = check_plan(plan)
@@ -934,7 +974,7 @@ def selftest() -> int:
         if g["group"] == "A":
             g["after"] = ["D"]
     try:
-        build_plan(cyc, durations, caps, start, "v1.0.0")
+        build_plan(cyc, durations, caps, start, "v1.0.0", round_n=FIXTURE_ROUND)
         expect("cycle: build refuses", False, "it scheduled a cycle")
     except PlanError as exc:
         expect("cycle: build refuses", "cycle" in str(exc), str(exc))
@@ -990,20 +1030,35 @@ def selftest() -> int:
         rc = subprocess.run([sys.executable, "-I", __file__, "--check",
                              "--plan", str(badp)], capture_output=True).returncode
         expect("--check exits 1 on a planted over-cap wave", rc == 1, f"rc={rc}")
-        cycf = Path(td) / "cyc.json"
+        # The fixture is named as a roster, so the command reads its round and
+        # the exit is the cycle's; the unnamed copy has no round to close.
+        # `--repo td` holds no VERSION, so the fixture closes round 1 from 0.0.0
+        # whatever the checkout's own version is.
+        cycf = Path(td) / "wave-r1-groups.json"
         cycf.write_text(json.dumps(cyc), encoding="utf-8")
-        rc = subprocess.run([sys.executable, "-I", __file__, "--roster-file", str(cycf),
-                             "--out", str(Path(td) / "p.json"),
-                             "--start", "2026-01-05T00:00:00Z"],
-                            capture_output=True).returncode
-        expect("the command exits 2 on a dependency cycle", rc == 2, f"rc={rc}")
+        out = subprocess.run([sys.executable, "-I", __file__, "--roster-file", str(cycf),
+                              "--out", str(Path(td) / "p.json"), "--repo", td,
+                              "--start", "2026-01-05T00:00:00Z"],
+                             capture_output=True, text=True)
+        expect("the command exits 2 on a dependency cycle",
+               out.returncode == 2 and "cycle" in out.stderr,
+               f"rc={out.returncode} {out.stderr[-200:]}")
+        unnamed = Path(td) / "groups.json"
+        unnamed.write_text(json.dumps(roster), encoding="utf-8")
+        out = subprocess.run([sys.executable, "-I", __file__, "--roster-file", str(unnamed),
+                              "--out", str(Path(td) / "p.json"), "--repo", td,
+                              "--start", "2026-01-05T00:00:00Z"],
+                             capture_output=True, text=True)
+        expect("a roster naming no round refuses, never defaults (exit 2)",
+               out.returncode == 2 and "round" in out.stderr,
+               f"rc={out.returncode} {out.stderr[-200:]}")
 
     # planted: an over-cap model input (7 slots' worth of live groups at t=0)
     many = {"groups": [
         {"group": f"L{i}", "size": "S", "lane": "Core model", "kind": "defect",
          "after": [], "resume": {"stage": "in-progress"}} for i in range(7)
     ]}
-    p2 = build_plan(many, durations, caps, start, "v1.0.0")
+    p2 = build_plan(many, durations, caps, start, "v1.0.0", round_n=FIXTURE_ROUND)
     expect("live admission never exceeds the slot cap",
            p2["summary"]["peak_in_flight"] <= caps["slots"],
            str(p2["summary"]["peak_in_flight"]))
@@ -1020,7 +1075,7 @@ def selftest() -> int:
          "after": ["B"], "hot_files": ["coordinator.py"],
          "resume": {"stage": "in-progress"}},
     ]}
-    p3 = build_plan(ahead, durations, caps, start, "v1.0.0")
+    p3 = build_plan(ahead, durations, caps, start, "v1.0.0", round_n=FIXTURE_ROUND)
     inv = p3["generated"]["inherited_dependency_violations"]
     expect("an inherited group ahead of its dependency is recorded",
            [(d["group"], d["after"]) for d in inv] == [("A", "B")], str(inv))
@@ -1064,7 +1119,8 @@ def selftest() -> int:
             subprocess.run(["git", "-C", str(repo), "commit", "-q", "-m", "r"], check=True)
         commit(roster)
         r_, ref_, blob_ = load_roster(str(repo), "main")
-        fresh = build_plan(r_, durations, caps, start, "v1.0.0", ref_, blob_)
+        fresh = build_plan(r_, durations, caps, start, "v1.0.0", ref_, blob_,
+                           round_n=roster_lib.roster_round(str(rpath)))
         expect("a plan pins the roster blob it was built from", len(blob_) == 40, blob_)
         expect("a fresh plan is not stale",
                stale_reason(fresh, str(repo)) is None, str(stale_reason(fresh, str(repo))))
@@ -1112,7 +1168,7 @@ def selftest() -> int:
         {"group": f"K{i}", "size": "S", "lane": "Core model", "kind": "defect",
          "after": [], "hot_files": ["coordinator.py"],
          "resume": {"stage": "not-started"}} for i in range(3)]}
-    p4 = build_plan(coord3, durations, caps, start, "v1.0.0")
+    p4 = build_plan(coord3, durations, caps, start, "v1.0.0", round_n=FIXTURE_ROUND)
     expect("the coordinator cap limits planned groups in flight",
            p4["summary"]["peak_coordinator_in_flight"] <= caps["coordinator_cap"],
            str(p4["summary"]["peak_coordinator_in_flight"]))
@@ -1126,7 +1182,7 @@ def selftest() -> int:
          "after": [], "resume": {"stage": "not-started"}},
         {"group": "C", "size": "XL", "lane": "Core model", "kind": "defect",
          "after": ["B"], "resume": {"stage": "not-started"}}]}
-    p5 = build_plan(order, durations, one, start, "v1.0.0")
+    p5 = build_plan(order, durations, one, start, "v1.0.0", round_n=FIXTURE_ROUND)
     expect("dispatch takes the longest remaining path first, not the shortest job",
            p5["groups"]["A"]["start"] > p5["groups"]["B"]["start"],
            f"A starts {p5['groups']['A']['start']}, B {p5['groups']['B']['start']}")
@@ -1149,7 +1205,7 @@ def selftest() -> int:
         {"group": "TALL", "size": "XL", "lane": "IN", "kind": "instrument",
          "after": [], "resume": {"stage": "not-started"}},
     ]}
-    p7 = build_plan(prio, durations, one, start, "v1.0.0")
+    p7 = build_plan(prio, durations, one, start, "v1.0.0", round_n=FIXTURE_ROUND)
     starts7 = {g: p7["groups"][g]["start"] for g in ("CP", "CP2", "PROD", "TALL")}
     expect("the computed critical path is CP -> CP2",
            p7["critical_path"] == ["CP", "CP2"], str(p7["critical_path"]))
@@ -1172,7 +1228,7 @@ def selftest() -> int:
         {"group": "TALL", "size": "XL", "lane": "IN", "kind": "instrument",
          "after": [], "resume": {"stage": "in-progress"}},
     ]}
-    p8 = build_plan(liveprio, durations, one, start, "v1.0.0")
+    p8 = build_plan(liveprio, durations, one, start, "v1.0.0", round_n=FIXTURE_ROUND)
     expect("the t==0 live admission uses the same priority key",
            p8["groups"]["PROD"]["inherited"] is True
            and p8["groups"]["TALL"]["inherited"] is False,
@@ -1191,7 +1247,7 @@ def selftest() -> int:
         {"group": "NONE", "size": "M", "lane": "IN", "kind": "instrument",
          "after": [], "resume": {"stage": "not-started"}},
     ]}
-    p9 = build_plan(save, durations, one, start, "v1.0.0")
+    p9 = build_plan(save, durations, one, start, "v1.0.0", round_n=FIXTURE_ROUND)
     expect("tier 2 ranks by savings, and absent savings sorts last",
            p9["groups"]["HI"]["start"] < p9["groups"]["LO"]["start"]
            < p9["groups"]["NONE"]["start"],
@@ -1207,7 +1263,7 @@ def selftest() -> int:
         {"group": "ZZZ", "size": "L", "lane": "IN", "kind": "instrument",
          "after": [], "resume": {"stage": "not-started"}},
     ]}
-    p10 = build_plan(tie, durations, one, start, "v1.0.0")
+    p10 = build_plan(tie, durations, one, start, "v1.0.0", round_n=FIXTURE_ROUND)
     expect("height breaks ties within a tier, ahead of the name",
            p10["groups"]["ZZZ"]["start"] < p10["groups"]["AAA"]["start"],
            str({g: p10["groups"][g]["start"] for g in ("AAA", "ZZZ")}))
@@ -1222,7 +1278,7 @@ def selftest() -> int:
     ]}
     try:
         build_plan(unmeasured, durations, caps, start, "v1.0.0",
-                   roster_path="dev/programme/rosters/wave-r10-groups.json")
+                   roster_path="dev/programme/rosters/wave-r10-groups.json", round_n=10)
         expect("an unmeasured size is refused, naming roster, group and size",
                False, "it scheduled an XS group")
     except Exception as exc:  # noqa: BLE001 -- any other failure is a crash, not this refusal
@@ -1235,7 +1291,7 @@ def selftest() -> int:
          "after": [], "resume": {"stage": "not-started"}}
         for k, s in enumerate(("S", "M", "L", "XL"))]}
     try:
-        build_plan(measured, durations, caps, start, "v1.0.0")
+        build_plan(measured, durations, caps, start, "v1.0.0", round_n=FIXTURE_ROUND)
         expect("a roster of only measured sizes plans", True)
     except PlanError as exc:
         expect("a roster of only measured sizes plans", False, str(exc))
@@ -1247,7 +1303,7 @@ def selftest() -> int:
          "savings": "lots", "after": [], "resume": {"stage": "not-started"}},
     ]}
     try:
-        build_plan(badsav, durations, caps, start, "v1.0.0")
+        build_plan(badsav, durations, caps, start, "v1.0.0", round_n=FIXTURE_ROUND)
         expect("a non-numeric savings is refused", False, "it scheduled")
     except Exception as exc:  # noqa: BLE001 -- any other failure is a crash, not this refusal
         expect("a non-numeric savings is refused", "savings" in str(exc), str(exc))
@@ -1255,7 +1311,7 @@ def selftest() -> int:
     prod = {"groups": [
         {"group": f"P{i}", "size": "S", "lane": "Core model", "kind": "defect",
          "after": [], "resume": {"stage": "not-started"}} for i in range(6)]}
-    p6 = build_plan(prod, durations, caps, start, "v1.0.0")
+    p6 = build_plan(prod, durations, caps, start, "v1.0.0", round_n=FIXTURE_ROUND)
     pat = [s for s in p6["stamps"] if s["kind"] == "patch"]
     expect("five production merges cut one patch stamp",
            len(pat) == 1 and len(pat[0]["carries"]) == caps["stamp_every"],
@@ -1266,6 +1322,61 @@ def selftest() -> int:
            and s6["ci_minutes"] == round((s6["batches"] + s6["stamps"])
                                          * s6["gate_minutes"], 1),
            str({k: s6[k] for k in ("ci_minutes", "batches", "stamps", "gate_minutes")}))
+    # The closure stamp is the round's major (decision 0016, tvofi
+    # 2026-10-29): round N closes as vN.0.0, the version `stamp.py
+    # --round-close N` assigns, and the interim stamps stay patch bumps.
+    close = p6["stamps"][-1]
+    expect("the closure stamp is the round-close major of the plan's round",
+           close["kind"] == "round-close" and close["version"] == "v2.0.0"
+           and p6["summary"]["closure_stamp"] == "v2.0.0"
+           and p6["generated"]["round"] == 2, str(close))
+    expect("an interim stamp stays a patch bump of the current version",
+           [s["version"] for s in pat] == ["v1.0.1"], str(pat))
+    p6r3 = build_plan(prod, durations, caps, start, "v1.0.0", round_n=3)
+    expect("the closure major follows the round, not a constant",
+           p6r3["stamps"][-1]["version"] == "v3.0.0", str(p6r3["stamps"][-1]))
+    try:
+        build_plan(prod, durations, caps, start, "v2.4.0", round_n=2)
+        expect("a round not above the current major refuses", False, "it planned one")
+    except PlanError as exc:
+        expect("a round not above the current major refuses",
+               "not above the current major" in str(exc), str(exc))
+    for kind, version in (("minor", "v1.1.0"), ("round-close", "v1.1.0"),
+                          ("round-close", "v3.0.0")):
+        wrong = json.loads(json.dumps(p6))
+        wrong["stamps"][-1].update(kind=kind, version=version)
+        bad = check_plan(wrong)
+        expect(f"--check refuses a {kind} closure stamp {version} in round 2",
+               any("round close" in b for b in bad), str(bad))
+    # The closure arms the wrong-closure rows above never reach: a correct
+    # round-close stamp that is not last, and a stray kind beside a correct one.
+    notlast = json.loads(json.dumps(p6))
+    notlast["stamps"].append(dict(notlast["stamps"][0], carries=[]))
+    notlast["summary"]["stamps"] = len(notlast["stamps"])
+    bad = check_plan(notlast)
+    expect("--check refuses a round-close stamp that is not the last stamp",
+           any("expected one, and last" in b for b in bad), str(bad))
+    stray = json.loads(json.dumps(p6))
+    stray["stamps"].insert(0, dict(stray["stamps"][0], kind="minor", carries=[],
+                                   version="v1.1.0"))
+    stray["summary"]["stamps"] = len(stray["stamps"])
+    bad = check_plan(stray)
+    expect("--check refuses a minor stamp beside a correct round close",
+           any("unknown stamp kind(s) ['minor']" in b for b in bad)
+           and not any("round close" in b for b in bad), str(bad))
+    # `round_n` has no default: a caller that omits it is a TypeError, never a
+    # round silently assumed (the stance next_version takes on no roster).
+    try:
+        build_plan(prod, durations, caps, start, "v1.0.0")
+        expect("build_plan without round_n refuses", False, "it planned a closure")
+    except TypeError as exc:
+        expect("build_plan without round_n refuses", "round_n" in str(exc), str(exc))
+    unround = json.loads(json.dumps(p6))
+    del unround["generated"]["round"]
+    bad = check_plan(unround)
+    expect("--check refuses a plan recording no round",
+           any("round close" in b for b in bad), str(bad))
+
     gate = gate_minutes(durations)
     want_gate = 50.0 + 22.0 + 27.0 * (1.0 + 0.04)
     expect("the gate price includes the cancelled-leg rerun",
@@ -1342,6 +1453,27 @@ def selftest() -> int:
             ("stamp-cadence",
              _m("def build_plan(roster: dict, ", "durations: dict, caps: dict, start: dt.datetime,"),
              _m("if len(carry) >= ", "every:"), "if False:"),
+            ("round-close-version",
+             _m("def build_plan(roster: dict, ", "durations: dict, caps: dict, start: dt.datetime,"),
+             _m("stamps.append({\"version\": closing, ", "\"at\": closure + closure_lead,"),
+             _m("stamps.append({\"version\": bump(version, ", "patch), \"at\": closure + closure_lead,")),
+            ("round-close-check",
+             _m("def check_plan(plan: dict", ") -> list:"),
+             _m("elif closes[0][\"version\"] != ", "want:"), "elif False:"),
+            ("round-close-last",
+             _m("def check_plan(plan: dict", ") -> list:"),
+             _m(" or plan[\"stamps\"][-1] is not ", "closes[0]:"), ":"),
+            ("round-close-stray-kind",
+             _m("def check_plan(plan: dict", ") -> list:"),
+             _m("if s[\"kind\"] not in (\"patch\", ", "ROUND_CLOSE)]"),
+             _m("if s[\"kind\"] not in (\"patch\", ", "\"minor\", ROUND_CLOSE)]")),
+            ("round-n-required",
+             _m("def build_plan(roster: dict, ", "durations: dict, caps: dict, start: dt.datetime,"),
+             _m("roster_path: str = \"\", *, ", "round_n: int) -> dict:"),
+             _m("roster_path: str = \"\", *, ", "round_n: int = 10) -> dict:")),
+            ("round-from-roster",
+             _m("def main(argv=", "None) -> int:"),
+             _m("round_n = roster_lib.roster_round(", "src)"), "round_n = 99"),
             ("ci-formula",
              _m("def build_plan(roster: dict, ", "durations: dict, caps: dict, start: dt.datetime,"),
              _m("ci = round((len(batch_rows) + len(stamps)) ", "* gate_report, 1)"),
@@ -1577,8 +1709,14 @@ def main(argv=None) -> int:
             src = roster_lib.roster_path(args.repo, ref, args.roster_path)
         except roster_lib.RosterNotFound:
             src = args.roster_path or ""
+    # The round the closure stamp closes is the one the roster's path names,
+    # read as `stamp.py --round-close` reads it (`roster_lib.roster_round`).
+    try:
+        round_n = roster_lib.roster_round(src)
+    except roster_lib.RosterNotFound as exc:
+        raise PlanError(f"no round for the round-close stamp: {exc}") from exc
     plan = build_plan(roster, durations, caps, start, version, ref, blob,
-                      roster_path=src)
+                      roster_path=src, round_n=round_n)
     bad = check_plan(plan)
     if bad:
         print("the model produced a violating plan; refusing to write it", file=sys.stderr)

