# Review packet #3428
head: 846f2dc07b4503522909bf953b91e502f168f2af
base: ee64358be7eeccaec5178a923cb3b83a18a924a0

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: pending
CodeQL id=130729313553 neutral
arch-score / arch-score id=130729092486 queued
arm id=130724930639 skipped
budget-raise-gate / budget-raise-gate id=130729092251 success
cancel-superseded id=130724843884 queued
codeql id=130728525284 skipped
codeql / Analyze (actions) id=130729092656 queued
codeql / Analyze (javascript-typescript) id=130729092552 success
codeql / Analyze (python) id=130729092998 queued
governance id=130728524992 skipped
governance / delivery-status id=130729091881 queued
governance / delivery-status-publish id=130729095182 skipped
governance / env-matrix id=130729092064 queued
governance / instrument-self-tests id=130729091956 queued
governance / policy-docs id=130729092077 queued
governance / record id=130729093663 skipped
governance / wave-script id=130729091923 queued
hassfest id=130728527973 skipped
hassfest / hassfest id=130729092217 queued
kernel-points id=130729093721 skipped
prelude id=130724843960 success
refresh id=130724843519 queued
tests id=130728524951 skipped
tests / briefs id=130729091694 success
tests / closure-scope id=130729091704 in_progress
tests / mutation id=130729092163 queued
tests / nightly-status id=130729092074 queued
validate id=130728526125 skipped
validate / validate-hacs id=130729092212 queued

## Refusals
none

## Advisories
none

## carry_audit at the head
NOTE stale tree: 846f2dc07b4503522909bf953b91e502f168f2af lacks origin/main c71d3f6e8983948f51ea6ac0b9e0ecfc76069d4d; roster read at origin/main
NOTE body item e79c976e: dismissed:the code went straight to the handoff ref
CARRY-AUDIT: 1 finding item(s): 1 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
ok         PYTHONPATH=tests/hastub python3 tools/plan/size_durations.py --self-test
             `tools/plan/size_durations.py` is in the tree at this head
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

## Review scope: full (first round: no --reviewed-head)

## Three-dot diff
diff --git a/dev/audit/harnesses/r10_plan_page_mutants.py b/dev/audit/harnesses/r10_plan_page_mutants.py
index 7d633449a..52acaf8a6 100644
--- a/dev/audit/harnesses/r10_plan_page_mutants.py
+++ b/dev/audit/harnesses/r10_plan_page_mutants.py
@@ -49,6 +49,19 @@ MUTANTS = [
     ("M0", PAGE, None, None),
     ("live", PAGE, "elif _stage(entry) in replan.LIVE_STAGES:", "elif False:"),
     ("blocked", PAGE, "elif blk and not part:", "elif False:"),
+    ("hotfix-mark", PAGE, "g not in done and roster_lib.is_hotfix(entry),",
+     "g not in done and False,"),
+    ("hotfix-gates-crit", PAGE, "gating_crit = {a for c in crit if c in G",
+     "gating_crit = {a for c in () if c in G"),
+    # Round 2's four survivors (fix review 9774026d05): the mark as rendered,
+    # and each term of the row's `hot` and of `gating_crit`.
+    ("hot-render", PAGE, '           if r["hot"] else "")', '           if False else "")'),
+    ("hot-gates", PAGE, "if a in G and roster_lib.gates(G[a])}", "if a in G}"),
+    ("hot-notdone", PAGE, "g in gating_crit and g not in done and", "g in gating_crit and"),
+    ("hot-crit", PAGE, "gating_crit = {a for c in crit if c in G for a",
+     "gating_crit = {a for c in G for a"),
+    ("closure-conditions-text", PAGE, "{', '.join(summ.get('closure_conditions') or",
+     "{', '.join([] or"),
     ("partial", PAGE, "if m and m.group(1) in G:", "if False:"),
     ("blocked-by-less-done", PAGE,
      "if a in G and a not in discharged and roster_lib.gates(G[a])]",
@@ -68,9 +81,6 @@ MUTANTS = [
      "if i[\"state\"] == \"OPEN\")"),
     ("page-refuses-stale", PAGE, "    if stale:\n        bad.append", "    if False:\n        bad.append"),
     ("freshness-rule", PLAN, "if have != want:", "if False:"),
-    ("stamp-on-axis", PAGE,
-     "end = max([_t(plan[\"summary\"][\"closure\"])] + [_t(s[\"at\"]) for s in plan[\"stamps\"]]\n",
-     "end = max([_t(plan[\"summary\"][\"closure\"])]\n"),
     # Round 2: the fix review's survivors B to E (probe/rev-2558-e98d4b97).
     # B moved with its rule (2026-11-01): `replan.check_plan` refuses a plan
     # recording no model, which the page reads through C, so the page's own
diff --git a/dev/programme/delivery/3428.md b/dev/programme/delivery/3428.md
new file mode 100644
index 000000000..a4cc0908a
--- /dev/null
+++ b/dev/programme/delivery/3428.md
@@ -0,0 +1 @@
+- [#3428](https://github.com/tvofi/heatpump_optimizer/pull/3428) — **open**, R10-PLAN-PAGE-RESIDUE: r10 plan page residue (R10-PLAN-PAGE-RESIDUE)
diff --git a/tools/audit/seat/plan_page.py b/tools/audit/seat/plan_page.py
index 6980acec0..970578df1 100644
--- a/tools/audit/seat/plan_page.py
+++ b/tools/audit/seat/plan_page.py
@@ -184,6 +184,17 @@ def merged_pr(group: str, commit: str | None, by_sha: dict, by_group: dict):
     return by_group.get(group)
 
 
+def _plain_key(key: list) -> str:
+    """A sort key (replan's `sort_key`, always a list) as plain values: a null
+    reads as a dash, never a Python repr."""
+    return ", ".join("—" if v is None else str(v) for v in key)
+
+
+def _wave_text(wave) -> str:
+    """A group's wave for a tooltip or attribute: a dash when it has none."""
+    return "—" if wave is None else str(wave)
+
+
 def build_rows(roster: dict, plan: dict, snap: dict) -> list:
     """One row per roster group: status, PR, issues, blockers, schedule."""
     G = roster_lib.groups_of(roster)
@@ -218,6 +229,11 @@ def build_rows(roster: dict, plan: dict, snap: dict) -> list:
         if g:
             by_group[g] = p["number"]  # the latest merge for the group
     state = {i["number"]: i for i in snap["issues"]}
+    # A hotfix that a critical-path group waits on holds the path, whether or
+    # not the longest chain runs through it: the same gating edges as `blk`.
+    # A discharged predecessor is in `done`, which the row's `hot` excludes.
+    gating_crit = {a for c in crit if c in G for a in G[c].get("after") or []
+                   if a in G and roster_lib.gates(G[a])}
 
     rows = []
     for g, entry in G.items():
@@ -226,6 +242,8 @@ def build_rows(roster: dict, plan: dict, snap: dict) -> list:
         # that a discharged predecessor is closed work, as replan reads it.
         blk = [a for a in entry.get("after") or []
                if a in G and a not in discharged and roster_lib.gates(G[a])]
+        if g in done:
+            blk = []  # a merged group waits on nothing (the legend's not-yet-done rule)
         part = sorted(delivered.get(g) or [])
         sfx = f", part merged #{', #'.join(map(str, part))}" if part else ""
         pr = ", ".join(f"#{n}" for n in open_pr.get(g, [])) or "—"
@@ -270,12 +288,15 @@ def build_rows(roster: dict, plan: dict, snap: dict) -> list:
             "tier": pg.get("tier"),
             "why": "; ".join(x for x in (
                 pg.get("tier_reason"), pg.get("start_reason"), pg.get("duration_basis"),
-                f"sort key {pg['sort_key']}" if pg.get("sort_key") else None) if x),
+                f"sort key {_plain_key(pg['sort_key'])}" if pg.get("sort_key") else None) if x),
             "issues": [(n, n in fixes, (state.get(n) or {}).get("state") != "CLOSED",
                         (state.get(n) or {}).get("title", ""))
                        for n in entry.get("issues") or []],
             "blk": blk, "desc": roster_lib.one_line_brief(entry, 170),
-            "crit": g in crit, "wave": None if g in done else pg["wave"],
+            "crit": g in crit,
+            "hot": g in gating_crit and g not in done and roster_lib.is_hotfix(entry),
+            "part": bool(part) and g not in done,
+            "wave": None if g in done else pg["wave"],
             "start": None if g in done else pg["start"],
             "finish": None if g in done else pg["finish"]})
         if pg.get("done"):  # the plan counts it done (absorbed): nothing to draw
@@ -291,9 +312,9 @@ def swimlanes(plan: dict, rows: list) -> tuple[str, int]:
     it draws (a link crossing more than one lane or two hours is left to the
     ◆ marks and the caption)."""
     now = _t(plan["generated"]["start"])
-    # The axis runs to the last planned stamp: the round-close stamp lands
-    # after closure, and an axis ending at closure would not draw it.
-    end = max([_t(plan["summary"]["closure"])] + [_t(s["at"]) for s in plan["stamps"]]
+    # The axis runs to closure, which is the later of the round-close stamp and
+    # the last post-closure step, so no stamp lies past it.
+    end = max([_t(plan["summary"]["closure"])]
               + [_t(plan["summary"]["post_closure_finish"])
                  for _ in [0] if plan["summary"].get("post_closure_finish")])
     slots = plan["generated"]["caps"]["slots"]
@@ -353,11 +374,11 @@ def swimlanes(plan: dict, rows: list) -> tuple[str, int]:
                 txt = name if room >= len(name) else (name[:room - 1] + "…" if room >= 4 else "")
                 when = r["s"].strftime("%a %d %b %H:%M")
                 parts.append(
-                    f'<g class="grp" data-st="{r["st"]}" data-name="{html.escape(name)}" '
+                    f'<g class="grp" data-st="{r["st"]}" data-part="{int(r["part"])}" data-name="{html.escape(name)}" '
                     f'data-state="{html.escape(r["label"])}" data-start="{when}" '
-                    f'data-eta="{r["finish"]}" data-wave="{r["wave"]}">'
+                    f'data-eta="{r["finish"]}" data-wave="{_wave_text(r["wave"])}">'
                     f'<title>{r["g"]}: {html.escape(r["label"])}, starts {when}, '
-                    f'ETA {r["finish"]}, wave {r["wave"]}</title>')
+                    f'ETA {r["finish"] or "—"}, wave {_wave_text(r["wave"])}</title>')
                 if w < 16:  # widen a narrow bar's hover target, not the bar
                     parts.append(f'<rect x="{x0 - 3:.1f}" y="{yy}" width="{w + 8:.1f}" '
                                  f'height="{RH}" fill="transparent"/>')
@@ -431,6 +452,24 @@ def project_issues(roster: dict, plan: dict, open_now: set) -> dict:
     return out
 
 
+def _plural(n: int, one: str, many: str) -> str:
+    return f"{n} {one if n == 1 else many}"
+
+
+def _other_issues_sentence(proj: dict) -> str:
+    """The open issues on no open group, pluralised from the count; the
+    unplanned clause is dropped when none are listed."""
+    other, orphans = len(proj["other"]), len(proj["orphans"])
+    rec = ", ".join(f"#{n}" for n in RECORD_ISSUES if n in proj["other"])
+    head = _plural(other, "other open issue is", "other open issues are") + " on no open group"
+    if not other:
+        return "no other open issue is on no open group."
+    parts = ([f"{rec} (the record issue{'s' if rec.count('#') > 1 else ''})"] if rec else [])
+    if orphans:
+        parts.append(f"the {orphans} listed below as unplanned")
+    return head + (": " + " and ".join(parts) if parts else "") + "."
+
+
 def issues_section(roster: dict, plan: dict, snap: dict) -> str:
     """The first section of the page: the open-issue count stepping down at each
     projected close. Omitted, with a note, when the snapshot has no GitHub state."""
@@ -486,9 +525,9 @@ def issues_section(roster: dict, plan: dict, snap: dict) -> str:
     note = (f"Open issues carried by not-done roster groups, as GitHub had them at the plan's "
             f"start; each is projected to close at the planned finish of the last group "
             f"carrying it. {len(unplanned)} sit on groups with no planned finish and stay "
-            f"flat; {len(proj['other'])} other open issues are on no open group: "
-            f"{', '.join(f'#{n}' for n in RECORD_ISSUES)} (the record issues) and the "
-            f"{len(proj['orphans'])} listed below as unplanned.")
+            f"flat; {_other_issues_sentence(proj)} The status strip counts "
+            f"{len(open_now - TRACKING_ISSUES)} open issues, the record issues left out: the "
+            f"{total} drawn here plus the {len(proj['orphans'])} unplanned.")
     title = {i["number"]: i.get("title") or "" for i in snap["issues"]}
     orphans = "".join(
         f'<li class="unplanned">#{n} {html.escape(title.get(n, ""))}: unplanned: no open '
@@ -600,11 +639,15 @@ def render(roster: dict, roster_src: str, plan: dict, snap: dict,
     slots, every = caps["slots"], caps["stamp_every"]
     chain = plan["critical_path"]
     waves_of = {g: w["wave"] for w in plan["waves"] for g in w["groups"]}
-    counts = {k: sum(1 for r in rows if r["st"] == k)
-              for k in _STRIP}
+    counts = {k: sum(1 for r in rows if r["st"] == k) for k in _STRIP}
+    # One predicate for the strip and the row label: a not-done group with a
+    # merged part (a carries-open one included) is part merged.
+    counts["partial"] = sum(1 for r in rows if r["part"])
     open_iss = ("—" if snap.get("offline") else str(sum(
         1 for i in snap["issues"]
         if i["state"] == "OPEN" and i["number"] not in TRACKING_ISSUES)))
+    n_open_rows = sum(1 for r in rows if r["st"] != "done")
+    n_sched = sum(1 for r in rows if r["st"] != "done" and r["finish"])
     order = {k: i for i, k in enumerate(("S", "M", "L", "XL"))}
     sizes = ", ".join(f"{k} {v:g} h" for k, v in sorted(
         model["sizes_hours"].items(), key=lambda kv: (order.get(kv[0], 99), kv[0])))
@@ -615,8 +658,10 @@ def render(roster: dict, roster_src: str, plan: dict, snap: dict,
         return f'<span class="{cls}" title="{e(title)}">#{n}</span>'
 
     trs = "".join(
-        f'<tr class="{r["st"]}" data-st="{r["st"]}"><td class="g">'
+        f'<tr class="{r["st"]}" data-st="{r["st"]}" data-part="{int(r["part"])}"><td class="g">'
         + ('<span class="cp" title="critical path">◆</span>' if r["crit"] else "")
+        + ('<span class="cp hotcp" title="hotfix blocking a critical-path group">▲</span>'
+           if r["hot"] else "")
         + f'{e(short(r["g"]))}<div class="lanec">{e(r["lane"])}</div></td>'
         f'<td class="d">{e(r["desc"])}</td>'
         f'<td class="st">{pill(r["st"], r["label"])}</td>'
@@ -654,8 +699,12 @@ def render(roster: dict, roster_src: str, plan: dict, snap: dict,
         "tier_legend": e(", ".join(f"{t} {w}" for t, w in sorted(replan.TIER_LEGEND.items()))),
         "slots": str(slots), "every": str(every),
         "slots_note": e(
-            f"Read from plan.json: {summ['groups_open']} open groups, {summ['batches']} "
-            f"merge batches, closure {summ['closure']}. A wave is the set of groups "
+            f"Read from plan.json: {summ['groups_open']} scheduled open groups (the lanes), "
+            f"of the {n_open_rows} the table lists as not merged; the other {n_open_rows - n_sched} "
+            f"are held without a schedule. {summ['batches']} "
+            f"merge batches, closure {summ['closure']}. The programme is closed only when "
+            f"{', '.join(summ.get('closure_conditions') or ['(conditions not in plan.json)'])}. "
+            f"A wave is the set of groups "
             f"dispatched at one instant; the next opens as soon as one of the {slots} "
             f"pull-request slots frees. Coordinator cap {caps['coordinator_cap']}; "
             f"{inherited} inherited in-progress coordinator groups are recorded in "
@@ -1043,6 +1092,63 @@ def _self_test() -> int:
             check("critical-path groups carry the mark",
                   all(rows[g]["crit"] for g in plan["critical_path"])
                   and page.count('class="critmark"') == len(plan["critical_path"]))
+            # A hotfix that a critical-path group waits on is marked, on or off the chain.
+            import copy
+            cg = next(g for g in plan["critical_path"] if g != "R9-PART")
+            hot_roster = copy.deepcopy(roster)
+            for e_ in hot_roster["groups"]:
+                if e_["group"] == "R9-PART":
+                    e_["kind"] = "bug"
+                if e_["group"] == cg:
+                    e_["after"] = list(e_["after"]) + ["R9-PART"]
+            hot_rows = {r["g"]: r for r in build_rows(hot_roster, plan, snap)}
+            cold_roster = copy.deepcopy(hot_roster)
+            for e_ in cold_roster["groups"]:
+                if e_["group"] == "R9-PART":
+                    e_["kind"] = "defect"
+            cold_rows = {r["g"]: r for r in build_rows(cold_roster, plan, snap)}
+            def marked(roster_, plan_=plan):
+                """The rows whose rendered name cell carries the hotfix mark."""
+                return re.findall(r'class="cp hotcp" title="hotfix blocking a critical-path '
+                                  r'group">▲</span>([^<]*)<div', render(
+                                      roster_, f"main:{roster_lib.ROSTERS_DIR}/wave-r9-groups.json",
+                                      plan_, snap))
+
+            def staged(stage):
+                r_ = copy.deepcopy(hot_roster)
+                for e_ in r_["groups"]:
+                    if e_["group"] == "R9-PART":
+                        e_["resume"] = dict(e_.get("resume") or {}, stage=stage)
+                return r_
+            nc = next(g for g, r in rows.items()
+                      if not r["crit"] and r["st"] != "done" and g != "R9-PART")
+            off_cp = copy.deepcopy(roster)
+            for e_ in off_cp["groups"]:
+                if e_["group"] == "R9-PART":
+                    e_["kind"] = "bug"
+                if e_["group"] == nc:
+                    e_["after"] = list(e_.get("after") or []) + ["R9-PART"]
+            dis_plan = copy.deepcopy(plan)
+            dis_plan["groups"]["R9-PART"]["discharged"] = True
+            check("a hotfix a critical-path group waits on is marked, on its row of the page",
+                  [g for g, r in hot_rows.items() if r["hot"]] == ["R9-PART"]
+                  and marked(hot_roster) == [short("R9-PART")], marked(hot_roster))
+            nulls = {"non-hotfix": marked(cold_roster), "no crit edge": marked(roster),
+                     "off-path edge": marked(off_cp) if roster_lib.is_hotfix(
+                         roster_lib.groups_of(off_cp)["R9-PART"]) and "R9-PART" in
+                     roster_lib.groups_of(off_cp)[nc]["after"] else ["fixture lost its edge"],
+                     "released (refuted)": marked(staged("refuted")),
+                     "closed (deferred)": marked(staged("deferred")),
+                     "discharged": marked(hot_roster, dis_plan)}
+            check("hotfix mark (null): a non-hotfix on the edge, a hotfix only an off-path "
+                  "group waits on, a released, a closed and a discharged predecessor mark no row",
+                  not any(nulls.values())
+                  and not any(r["hot"] for r in cold_rows.values())
+                  and not any(r["hot"] for r in rows.values()), str(nulls))
+            check("the closure conditions are stated on the page",
+                  "The programme is closed only when no open pull requests, no handoffs, "
+                  "no carries, no findings, no leads, only the coordination issue open." in page,
+                  re.findall(r"The programme is closed[^.]*\.", page))
             check("every open group's tier is shown, and a merged group's is not",
                   all(f'<td class="tier">{rows[g]["tier"]}</td>' in page
                       for g in rows if rows[g]["tier"] is not None)
@@ -1072,7 +1178,7 @@ def _self_test() -> int:
             check("every planned stamp is drawn on the axis, the round-close one after "
                   "closure included",
                   page.count('class="stampline"') == len(plan["stamps"])
-                  and _t(plan["stamps"][-1]["at"]) > _t(plan["summary"]["closure"]),
+                  and _t(plan["stamps"][-1]["at"]) >= _t(plan["summary"]["closure"]),
                   (page.count('class="stampline"'), plan["stamps"], plan["summary"]["closure"]))
             check("the closure stamp renders as the round's major, kind round-close",
                   '<td class="mono">v9.0.0</td>' in page
@@ -1100,9 +1206,82 @@ def _self_test() -> int:
             sec = issues_section(roster, plan, snap)
             check("the issues chart is the first section, drawn from the open set",
                   0 <= page.find("Projected open issues") < page.find("<h2>Swimlanes")
-                  and "2 open now" in page and "1 other open issues are on no open group" in page
+                  and "2 open now" in page and "1 other open issue is on no open group: #3394 (the record issue)." in page
                   and "Unplanned: no open group" not in page
                   and sec.count("<polyline") == 1, re.findall(r"\d+ open now", page))
+            # Count sentence: pluralised from the count, the unplanned clause
+            # dropped when none are listed (carry 2).
+            one = _other_issues_sentence({"other": {201}, "orphans": {}})
+            many = _other_issues_sentence({"other": {201, 77, 78}, "orphans": {77: [], 78: []}})
+            check("the other-issues sentence for none says none, not a zero count",
+                  _other_issues_sentence({"other": set(), "orphans": {}})
+                  == "no other open issue is on no open group.")
+            held_n = sum(1 for g in rows if rows[g]["st"] != "done" and not scheduled(g))
+            check("the lede counts the open groups held without a schedule",
+                  held_n >= 1 and f"the other {held_n} are held without a schedule" in page,
+                  re.findall(r"the other \d+ are held", page))
+            check("the other-issues sentence is singular for one and drops the zero clause",
+                  one == "1 other open issue is on no open group: #201 (the record issue)."
+                  and "0 listed" not in one, one)
+            check("null control: several with unplanned orphans pluralise and keep the clause",
+                  many == "3 other open issues are on no open group: #201 (the record issue) "
+                  "and the 2 listed below as unplanned.", many)
+            # Wave None and a null in the sort key never render as Python (carry 3).
+            nowave = json.loads(json.dumps(plan))
+            nowave["groups"]["R9-BLOCK"].update(wave=None, sort_key=[None, 4, "R9-BLOCK"])
+            npage = render(roster, f"main:{roster_lib.ROSTERS_DIR}/wave-r9-groups.json",
+                           nowave, snap)
+            check("a group with no wave and a null in its sort key renders no None",
+                  'data-wave="None"' not in npage and "wave None" not in npage
+                  and "sort key [" not in npage and "None" not in
+                  "".join(re.findall(r"<svg.*?</svg>", npage, re.S))
+                  and "sort key —, 4, R9-BLOCK" in npage, re.findall(r".{30}None.{20}", npage)[:3])
+            check("null control: a group at a wave renders wave N and data-wave=N",
+                  re.search(r'data-wave="\d+"', page) and re.search(r"wave \d+</title>", page),
+                  re.findall(r'data-wave="[^"]*"', page)[:3])
+            # One predicate for the strip's part-merged count and the row label.
+            co_roster = {"groups": roster["groups"] + [grp("R9-CO", "CO", stage="carries-open")]}
+            co_snap = dict(snap, merged_prs=snap["merged_prs"] + [
+                {"number": 24, "title": "R9-CO: part one", "head_ref": "fix/r9-co-1",
+                 "merge_commit_sha": "f" * 40, "merged_at": "2026-01-04T00:00:00Z"}])
+            co_plan = json.loads(json.dumps(plan))
+            co_plan["groups"]["R9-CO"] = dict(co_plan["groups"]["R9-PART"])
+            co_rows = {r["g"]: r for r in build_rows(co_roster, co_plan, co_snap)}
+            co_page = render(co_roster, f"main:{roster_lib.ROSTERS_DIR}/wave-r9-groups.json",
+                             co_plan, co_snap)
+            want_part = sum(1 for r in co_rows.values() if "part merged" in r["label"]
+                            and r["st"] != "done")
+            check("a carries-open group holding a merged part counts in the strip as its row does",
+                  co_rows["R9-CO"]["st"] == "held" and "part merged #24" in co_rows["R9-CO"]["label"]
+                  and want_part >= 2
+                  and f"<b>{want_part}</b><span>part merged, residual open</span>" in co_page,
+                  (want_part, re.findall(r"<b>\d+</b><span>part merged", co_page)))
+            check("null control: no part-merged group reads 0",
+                  "<b>0</b><span>part merged, residual open</span>" in render(
+                      roster, f"main:{roster_lib.ROSTERS_DIR}/wave-r9-groups.json",
+                      plan, dict(snap, merged_prs=snap["merged_prs"][:2])))
+            check("the group note and the issues note state how the two counts relate",
+                  f"of the {sum(1 for r in build_rows(roster, plan, snap) if r['st'] != 'done')} "
+                  "the table lists as not merged" in page
+                  and "The status strip counts 2 open issues, the record issues left out: the 2 "
+                  "drawn here plus the 0 unplanned." in page, re.findall(r"status strip counts[^.]*", page))
+            # A markdown heading in a brief renders as plain text (carry 4).
+            hb = roster_lib.one_line_brief({"brief": "# Fixer brief\n\nDo the thing.\nMore."})
+            dr = {r["g"]: r for r in build_rows(
+                {"groups": [grp("R9-D", "CO", after=("R9-OPEN",), stage="done", commit="aaaaaaa1"),
+                            grp("R9-OPEN", "CO")]}, dict(plan, groups={
+                                "R9-D": plan["groups"]["R9-DONE-SHA"],
+                                "R9-OPEN": plan["groups"]["R9-READY"]}), snap)}
+            check("a done row lists no open group under Blocked by",
+                  dr["R9-D"]["blk"] == [], dr["R9-D"]["blk"])
+            check("the Part merged filter matches the held part-merged row",
+                  'data-part="1"' in co_page and "f==='partial'&&part==='1'" in co_page
+                  and 'data-part="1"' not in render(roster, f"main:{roster_lib.ROSTERS_DIR}/wave-r9-groups.json",
+                                                    plan, dict(snap, merged_prs=snap["merged_prs"][:2])))
+            check("a description beginning '# Fixer brief' renders without the '#', lines joined",
+                  hb.startswith("Fixer brief") and "#" not in hb and "\n" not in hb, hb)
+            check("null control: a description with no heading is unchanged",
+                  roster_lib.one_line_brief({"brief": "Does X. More."}) == "Does X.")
             no_gh = {"issues": [], "open_prs": [], "merged_prs": [], "offline": True}
             check("no GitHub state: the chart is omitted with a note",
                   "Omitted" in issues_section(roster, plan, no_gh)
@@ -1386,10 +1565,10 @@ td.st{min-width:11rem}
   });
   var bs=document.querySelectorAll('.filters button'), rows=document.querySelectorAll('#rows tr'),
       bars=document.querySelectorAll('svg g.grp'), hide=document.getElementById('hide-done'), f='all';
-  function shown(st){ return (f==='all'||st===f) && !(hide.checked && st==='done'); }
+  function shown(st,part){ return (f==='all'||st===f||(f==='partial'&&part==='1')) && !(hide.checked && st==='done'); }
   function apply(){
-    rows.forEach(function(r){ r.hidden=!shown(r.getAttribute('data-st')); });
-    bars.forEach(function(b){ b.style.display=shown(b.getAttribute('data-st'))?'':'none'; });
+    rows.forEach(function(r){ r.hidden=!shown(r.getAttribute('data-st'),r.getAttribute('data-part')); });
+    bars.forEach(function(b){ b.style.display=shown(b.getAttribute('data-st'),b.getAttribute('data-part'))?'':'none'; });
   }
   bs.forEach(function(b){b.addEventListener('click',function(){
     bs.forEach(function(x){x.setAttribute('aria-pressed',x===b?'true':'false')});
diff --git a/tools/audit/seat/roster_lib.py b/tools/audit/seat/roster_lib.py
index 72418af63..cac4c2922 100644
--- a/tools/audit/seat/roster_lib.py
+++ b/tools/audit/seat/roster_lib.py
@@ -661,6 +661,10 @@ def one_line_brief(group: dict, limit: int = 160) -> str:
     longer than `limit` is cut with an ellipsis.
     """
     text = (group.get("brief") or "").strip()
+    # A brief written as a markdown document opens with a heading marker; the
+    # row is plain text, so the marker goes and the lines join.
+    text = re.sub(r"\A\s*#{1,6}[ \t]*", "", text)
+    text = re.sub(r"\s*\n\s*", " ", text)
     text = _ATTRIBUTION.sub("", text)
     cut = re.split(r"(?<=\.)\s", text, maxsplit=1)[0]
     cut = cut.replace("|", "/")
diff --git a/tools/plan/durations.json b/tools/plan/durations.json
index 2ce69631e..d6ece5958 100644
--- a/tools/plan/durations.json
+++ b/tools/plan/durations.json
@@ -3,16 +3,16 @@
  "batch_window_minutes": 0,
  "batch_window_note": "0: merge a batch as soon as it is merge-ready, sharing a gate run only among groups that finish at the same instant. Measured on the round-10 roster at blob 277cdd359193 (branch tip e3010676), fixed start 2026-10-20T17:00Z: window 0 closes 226.28 h with 44 batches and 5737.5 CI minutes; 20 min closes 228.28 h with 44 and the same CI; 60 min 232.28 h; 120 min 238.28 h. Closure is the first objective, and holding a finished group delays its dependents' release even when no group is waiting for the slot, so every window above 0 costs wall time with no CI saving at this roster.",
  "cancelled_rate_note": "The cancelled-rate denominator is the Analyze (python) rows that completed, not the commits whose three legs all completed: a run cancelled at its 30-minute cap is a cancelled run even when another leg of the same tree had not finished at measurement time. Measured 2026-10-20T17:53Z: 2 cancelled of 30 Analyze rows (0.067).",
- "carries_per_part": 11.0,
+ "carries_per_part": 22.0,
  "carry_baseline": {
   "L": 3.0,
-  "M": 1.0,
+  "M": 2.0,
   "S": 0.0,
   "XL": 11.5
  },
- "carry_hours": 0.33,
- "carry_part_hours": 19.8,
- "carry_provenance": "p75 hours over 43 second-or-later part PRs (first commit or creation to merge); carries_per_part is the p90 of roster carries a part body cites as answered over the 20 that cite any (size_durations.cited_carries): a part's capacity, since a part's hours do not grow with its carries. held_open_carries: each carries-open group's carries no merged body of its own cites, at measurement; replan.py counts any carry appended since as open",
+ "carry_hours": 0.28,
+ "carry_part_hours": 26.8,
+ "carry_provenance": "p75 hours over 99 second-or-later part PRs (first commit or creation to merge); carries_per_part is the p90 of roster carries a part body cites as answered over the 58 that cite any (size_durations.cited_carries): a part's capacity, since a part's hours do not grow with its carries. held_open_carries: each carries-open group's carries no merged body of its own cites, at measurement; replan.py counts any carry appended since as open",
  "ci": {
   "Analyze (python)": {
    "cancelled": 2,
@@ -51,131 +51,56 @@
  "closure_lead_minutes": 120,
  "first_round_by_class_hours": {
   "L": {
-   "production": 16.0
+   "instrument": 17.9,
+   "production": 18.6
   },
   "M": {
-   "instrument": 13.6,
-   "production": 17.2
+   "instrument": 18.0,
+   "production": 18.7
   },
   "S": {
-   "instrument": 11.7,
-   "production": 16.1
+   "instrument": 12.4,
+   "production": 17.5
   }
  },
  "first_round_hours": {
-  "L": 16.4,
-  "M": 14.9,
-  "S": 12.1,
-  "XL": 22.6
+  "L": 18.6,
+  "M": 18.4,
+  "S": 13.3,
+  "XL": 23.3
  },
  "held_open_carries": {
-  "R10-996-RUNNER-CLAIMS": {
-   "carries": 3,
-   "open": 3
-  },
-  "R10-COP-GATE": {
-   "carries": 27,
-   "open": 19
-  },
-  "R10-COP-PARTLOAD": {
-   "carries": 8,
-   "open": 7
-  },
-  "R10-FLOW-BOARD": {
-   "carries": 8,
-   "open": 6
-  },
-  "R10-FLOW-BODY-ONLY": {
-   "carries": 18,
-   "open": 4
-  },
-  "R10-FLOW-DESIGN-STAGES": {
-   "carries": 23,
-   "open": 18
-  },
-  "R10-FLY-CANCEL-SWEEP": {
-   "carries": 2,
-   "open": 2
-  },
-  "R10-FLY-LEDGER-SAMPLE": {
-   "carries": 6,
-   "open": 1
-  },
-  "R10-FLY-MANDATE-REVOKE-GUARD": {
-   "carries": 3,
-   "open": 2
+  "R10-CLOSEOUT-CLEANUP": {
+   "carries": 7,
+   "open": 0
   },
-  "R10-FLY-MUTANT-RESTORE": {
+  "R10-DEPENDABOT-3414-COMPAT": {
    "carries": 1,
    "open": 1
   },
-  "R10-FLY-NO-FOOTERS": {
-   "carries": 6,
-   "open": 6
-  },
-  "R10-FLY-OPENPR-ATOMIC": {
-   "carries": 10,
-   "open": 1
-  },
-  "R10-FLY-RELAY-REVIEW-FF": {
-   "carries": 18,
-   "open": 18
-  },
-  "R10-FLY-SEAT-ALIVE-ID": {
-   "carries": 6,
-   "open": 2
-  },
-  "R10-FLY-SUITE-ENV-FLAKES": {
-   "carries": 15,
-   "open": 15
-  },
-  "R10-FLY-TICK-APPROVAL-OWED": {
-   "carries": 3,
-   "open": 3
-  },
-  "R10-FLY-TRAIN-DEFAULTS": {
-   "carries": 5,
-   "open": 5
+  "R10-DISPATCH-AT-HANDOFF": {
+   "carries": 17,
+   "open": 0
   },
-  "R10-FRICTION-REGRESSION": {
-   "carries": 3,
-   "open": 3
+  "R10-FIXER-MD-SPELLING-CORPUS": {
+   "carries": 7,
+   "open": 7
   },
-  "R10-MERGE-SUBJECT-CASEARM": {
+  "R10-GENERIC-HEAT-CURVE-PERSISTENT": {
    "carries": 8,
    "open": 1
   },
-  "R10-ORCH-LEDGER": {
-   "carries": 45,
-   "open": 43
-  },
-  "R10-ORCH-PLANPAGE": {
-   "carries": 11,
-   "open": 3
-  },
-  "R10-ORCH-REVIEW-PACKET": {
-   "carries": 15,
-   "open": 4
-  },
-  "R10-ORCH-ROSTER-SCHEMA": {
-   "carries": 35,
-   "open": 34
-  },
-  "R10-TRAIN-OVERLAP-GRADE": {
-   "carries": 23,
-   "open": 1
-  },
-  "R10-USER-DOCS-FINAL": {
-   "carries": 1,
+  "R10-HOTFIX-MAIN-SELFTESTS": {
+   "carries": 2,
    "open": 0
   },
-  "R10-UX-HEALTH": {
-   "carries": 22,
-   "open": 2
+  "R10-REVIEW-ENUMERATE": {
+   "carries": 0,
+   "open": 0
   },
-  "R10-WOOD-NOTIFY": {
-   "carries": 4,
-   "open": 4
+  "R10-WATER-SETPOINT-FEEDBACK": {
+   "carries": 8,
+   "open": 1
   }
  },
  "inflow_groups_per_hour": 0.4,
@@ -187,26 +112,27 @@
   "merges": 29
  },
  "review_rounds": {
-  "L": 4.18,
-  "M": 2.59,
-  "S": 2.33,
-  "XL": 2.83
+  "L": 4.0,
+  "M": 3.47,
+  "S": 2.47,
+  "XL": 3.17
  },
  "review_rounds_by_class": {
   "L": {
-   "production": 3.44
+   "instrument": 4.12,
+   "production": 3.92
   },
   "M": {
-   "instrument": 2.22,
-   "production": 2.81
+   "instrument": 3.26,
+   "production": 3.7
   },
   "S": {
-   "instrument": 2.19,
-   "production": 2.51
+   "instrument": 2.4,
+   "production": 2.49
   }
  },
  "roster_provenance": "The schedule figures in the pull request body are taken at roster branch tip e3010676747126df614e595ae43477db7d32e7b9, roster blob 277cdd3591938af542a3f72510389f9bc3378429. A later roster edit moves the batches, the CI minutes and the closure; re-run the replanner and re-take the figures rather than quoting these.",
- "round_hours": 4.62,
+ "round_hours": 5.65,
  "samples": [
   {
    "Analyze (python)": {
@@ -426,13 +352,13 @@
   }
  ],
  "sizes_hours": {
-  "L": 31.1,
-  "M": 22.2,
-  "S": 18.2,
-  "XL": 31.1
+  "L": 35.6,
+  "M": 32.4,
+  "S": 21.6,
+  "XL": 35.6
  },
- "sizes_measured_at": "2026-11-01T07:38:26Z",
+ "sizes_measured_at": "2026-11-11T04:56:48Z",
  "sizes_percentile": 75,
- "sizes_provenance": "p75 over 189 done groups with a merged PR (S n=123, M n=49, L n=11, XL n=6): active hours (the union of each part's first commit or creation, or the roster's dispatch stamp, to its merge) with extra review rounds priced out at the pooled Theil-Sen slope (4.62 h/round), then the cell's mean rounds added back; per class where a cell has n>=5. Wall clock: review, queueing and the PR-less handoff wait are inside it. carry_hours (0.33 h) is the Theil-Sen slope of the round-adjusted hours on the group's carry count, priced per carry above the size's median (carry_baseline). Monotone in size: XL 31 h lifted to L's 31.1 h. Measured by tools/plan/size_durations.py; re-derive, never edit.",
+ "sizes_provenance": "p75 over 348 done groups with a merged PR (S n=227, M n=94, L n=21, XL n=6): active hours (the union of each part's first commit or creation, or the roster's dispatch stamp, to its merge) with extra review rounds priced out at the pooled Theil-Sen slope (5.65 h/round), then the cell's mean rounds added back; per class where a cell has n>=5. Wall clock: review, queueing and the PR-less handoff wait are inside it. carry_hours (0.28 h) is the Theil-Sen slope of the round-adjusted hours on the group's carry count, priced per carry above the size's median (carry_baseline). Monotone in size: XL 29.9 h lifted to L's 35.6 h. Measured by tools/plan/size_durations.py; re-derive, never edit. Input: 1021 merged PRs created since 2026-10-12, read by size_durations.fetch_rest (--via rest).",
  "stamp_lead_minutes": 60
 }
diff --git a/tools/plan/replan.py b/tools/plan/replan.py
index 3026fd97f..4b228fa78 100644
--- a/tools/plan/replan.py
+++ b/tools/plan/replan.py
@@ -114,17 +114,27 @@ ROUND_CLOSE = "round-close"
 
 # A fixer already working. `queued` is not working: the plan dispatches it.
 LIVE_STAGES = ("in-progress", "fixing", "review", "in-review")
+#: The live stages whose build is finished: a group here starts from its
+#: review rounds, not from a fresh fixer start.
+REVIEW_STAGES = ("review", "in-review")
 
 DEFAULT_CAPS = {
-    "slots": 16,             # open pull requests: the owner's cap since 2026-10-31
-    "seats": 16,             # fixers working: one per open pull request
+    "slots": 20,             # open pull requests: the owner's cap since 2026-11-07
+    "seats": 20,             # fixers working: one per open pull request
     "coordinator_cap": 2,    # open pull requests touching coordinator.py
     "stamp_every": 3,        # production groups per patch stamp (tvofi 2026-10-26)
 }
 #: Where DEFAULT_CAPS' slots and seats come from, recorded in every plan that
 #: uses them: a plan drawn at a cap nobody chose must say whose cap it is.
-CAPS_PROVENANCE = ("tvofi 2026-10-31 (#201 comment 6544047621): 16 open pull "
-                   "requests; replan.py DEFAULT_CAPS")
+CAPS_PROVENANCE = ("tvofi 2026-11-07 (#201 comment 6707334933, superseding 6544047621): "
+                   "20 open pull requests; replan.py DEFAULT_CAPS")
+
+
+#: What "the programme is closed" means beyond the plan's last finish (tvofi
+#: 2026-11-07, #201): the plan states it beside `summary.closure`, which is only
+#: the schedule's own end.
+CLOSURE_CONDITIONS = ("no open pull requests", "no handoffs", "no carries", "no findings",
+                      "no leads", "only the coordination issue open")
 
 
 class PlanError(Exception):
@@ -551,6 +561,13 @@ def group_hours(group: dict, durations: dict, is_live: bool, where: str,
         why += left_out
     else:
         hours, why = float(sizes[size]), f"{size}: sizes_hours"
+    if is_live and stage in REVIEW_STAGES and size in first:
+        # The build is done: what is left is the review rounds still to run, at
+        # least one, never more than a fresh fixer's remaining share.
+        left_rounds = max(rounds - 1, 1.0)
+        in_review = min(left_rounds * float(durations["round_hours"]),
+                        hours * float(durations.get("live_remaining_fraction", 0.7)))
+        return in_review, why + f", in {stage}: {left_rounds:.2f} review round(s) left"
     if is_live:
         hours *= float(durations.get("live_remaining_fraction", 0.7))
         why += ", working (live_remaining_fraction)"
@@ -877,8 +894,8 @@ def selftest_model() -> int:
 
     # 5. caps: a call naming none draws at the owner's, and says so.
     nocaps = cli_caps(parse_args([]))
-    expect("a replan given no caps does not draw a 6-slot plan: the owner's 16, with provenance",
-           nocaps["slots"] == 16 and nocaps["seats"] == 16
+    expect("a replan given no caps does not draw a 6-slot plan: the owner's 20, with provenance",
+           nocaps["slots"] == 20 and nocaps["seats"] == 20
            and nocaps["provenance"] == CAPS_PROVENANCE, nocaps)
     given = cli_caps(parse_args(["--slots", "4"]))
     expect("null control: a cap given on the command line is used and named as given",
@@ -1290,6 +1307,11 @@ def build_plan(roster: dict, durations: dict, caps: dict, start: dt.datetime,
         post_start[n] = ready_at
         post_end[n] = ready_at + post_dur[n]
 
+    # The programme closes at the LATER of the round-close stamp and the last
+    # post-closure step (the catalog PR): tvofi 2026-11-07, "not considered
+    # closed until both v.10.0.0 and the catalog PR has landed".
+    closure_at = max([stamps[-1]["at"]] + list(post_end.values()))
+
     # a wave is the set of groups the replan dispatches at one instant
     by_open: dict = {}
     for n in open_:
@@ -1412,7 +1434,7 @@ def build_plan(roster: dict, durations: dict, caps: dict, start: dt.datetime,
         # Expected arrivals over the plan's wall time, priced at the median
         # size: reported, not scheduled -- they are not groups yet.
         sz = sorted(float(v) for v in size_hours.values())
-        n_exp = inflow * closure / 60.0
+        n_exp = inflow * closure_at / 60.0
         arrivals = {"groups": round(n_exp, 2),
                     "work_hours": round(n_exp * sz[len(sz) // 2], 2)}
     peak_flight, peak_coord = peak_concurrency(groups_out, start)
@@ -1480,9 +1502,10 @@ def build_plan(roster: dict, durations: dict, caps: dict, start: dt.datetime,
             "inherited_dependency_violations": inherited_deps,
         },
         "summary": {
-            "closure": iso(start, closure),
+            "closure": iso(start, closure_at),
             "closure_stamp": stamps[-1]["version"],
-            "wall_hours": round(closure / 60.0, 2),
+            "closure_conditions": list(CLOSURE_CONDITIONS),
+            "wall_hours": round(closure_at / 60.0, 2),
             "ci_minutes": ci,
             "gate_minutes": gate_report,
             "batches": len(batch_rows),
@@ -1760,9 +1783,16 @@ def check_plan(plan: dict) -> list:
         bad.append("summary: stamp count disagrees with the stamps list")
     if s["groups_open"] != len(groups):
         bad.append("summary: open-group count disagrees with the groups list")
-    closure = max((mins(g["finish"]) for g in in_round.values()), default=0)
+    close_stamps = [x for x in plan.get("stamps", []) if x.get("kind") == ROUND_CLOSE]
+    post_fin = [mins(plan["groups"][n]["finish"]) for n in s.get("post_closure") or []
+                if n in plan["groups"]]
+    closure = max([mins(x["at"]) for x in close_stamps] + post_fin
+                  or [max((mins(g["finish"]) for g in in_round.values()), default=0)])
+    if s.get("closure_conditions") != list(CLOSURE_CONDITIONS):
+        bad.append("summary: closure_conditions is not the owner's closure conditions")
     if mins(s["closure"]) != closure:
-        bad.append("summary: closure is not the last group finish")
+        bad.append("summary: closure is not the later of the round-close stamp and the "
+                   "last post-closure group finish")
     if "model" in plan["generated"]:
         bad += model_refusals(plan["generated"]["model"])
     else:
@@ -2377,10 +2407,56 @@ def selftest() -> int:
            pc["groups"]["R10-CATALOG-PR"].get("post_closure") is True
            and pc["groups"]["R10-CATALOG-PR"]["start"] >= close_at
            and pc["summary"]["post_closure"] == ["R10-CATALOG-PR"], str(pc["groups"]["R10-CATALOG-PR"]))
-    expect("post-closure: in no stamp's carries and outside summary.closure",
+    expect("post-closure: in no stamp's carries, and summary.closure is the later of the "
+           "stamp and the catalog step's finish (tvofi 2026-11-07), which starts no earlier "
+           "than the stamp",
            all("R10-CATALOG-PR" not in s["carries"] for s in pc["stamps"])
-           and pc["summary"]["closure"] == p0["summary"]["closure"]
-           and pc["stamps"] == p0["stamps"], str(pc["stamps"]))
+           and pc["summary"]["closure"] == pc["groups"]["R10-CATALOG-PR"]["finish"]
+           and pc["summary"]["closure"] > close_at
+           and pc["groups"]["R10-CATALOG-PR"]["start"] >= close_at
+           and pc["stamps"] == p0["stamps"], str((pc["summary"]["closure"], pc["stamps"])))
+    # The fixture prices a round at 0 h, which would make every review price 0:
+    # these arms use a round of 1 h and S at the named expected rounds.
+    def rv(st, rounds=3.0, drop=()):
+        d = dict(durations, round_hours=1.0, review_rounds={**durations["review_rounds"], "S": rounds})
+        return group_hours(fx("RV", "S", stage=st), {k: v for k, v in d.items() if k not in drop},
+                           True, "<t>")[0]
+    expect("live stage: a group in review is priced by its review rounds left, below a fresh "
+           "fixer's remaining share; one in progress is not",
+           abs(rv("in-review") - 2.0) < 1e-9 and rv("in-review") == rv("review")
+           and rv("in-review") < rv("in-progress"),
+           str([rv(x) for x in ("in-review", "review", "in-progress")]))
+    expect("live stage (floor): fewer than two expected rounds still price one review round, "
+           "not the rounds themselves (max(rounds - 1, 1))",
+           abs(rv("in-review", 1.4) - 1.0) < 1e-9 and 1.4 < rv("in-progress", 1.4),
+           str((rv("in-review", 1.4), rv("in-progress", 1.4))))
+    unset = ("live_remaining_fraction",)
+    expect("live stage (cap): with no live_remaining_fraction recorded, review and progress "
+           "share the one 0.7 default, so many rounds left price as in progress",
+           rv("in-review", 99.0, unset) == rv("in-progress", 99.0, unset) < 98.0,
+           str((rv("in-review", 99.0, unset), rv("in-progress", 99.0, unset))))
+    gen_start = dt.datetime.strptime(pc["generated"]["start"], "%Y-%m-%dT%H:%M:%SZ")
+    expect("post-closure: wall_hours runs to summary.closure (the catalog finish), not the stamp",
+           abs(pc["summary"]["wall_hours"] * 60 - (
+               dt.datetime.strptime(pc["summary"]["closure"], "%Y-%m-%dT%H:%M:%SZ")
+               - gen_start).total_seconds() / 60) < 1.0
+           and pc["summary"]["wall_hours"] > p0["summary"]["wall_hours"],
+           str((pc["summary"]["wall_hours"], p0["summary"]["wall_hours"])))
+    expect("closure conditions: the plan states the owner's six (tvofi 2026-11-07), and --check "
+           "refuses a plan that drops them",
+           pc["summary"]["closure_conditions"] == [
+               "no open pull requests", "no handoffs", "no carries", "no findings",
+               "no leads", "only the coordination issue open"]
+           and any("closure_conditions" in b for b in check_plan(
+               dict(pc, summary=dict(pc["summary"], closure_conditions=[])))), "")
+    expect("post-closure (null): with no post-stamp group, closure is the stamp's at",
+           p0["summary"]["closure"] == p0["stamps"][-1]["at"], str(p0["summary"]["closure"]))
+    expect("post-closure (a): a plan whose closure drops the catalog step is refused by --check",
+           any("closure" in b for b in check_plan(
+               dict(pc, summary=dict(pc["summary"], closure=p0["summary"]["closure"])))), "")
+    ex = cli_caps(parse_args(["--slots", "7"]))
+    expect("slots 20 (null): an explicit --slots keeps its value, the seats stay the default",
+           ex["slots"] == 7 and ex["seats"] == DEFAULT_CAPS["seats"] == 20, str(ex))
     expect("post-closure (null): a production group with no stamp dependency is in the "
            "closing stamp's carries",
            pc["stamps"][-1]["carries"] == ["R10-A", "R10-B"], str(pc["stamps"][-1]))
@@ -2705,6 +2781,24 @@ def selftest() -> int:
         expect("since-tag: a clean merge's change is read against its first parent",
                got == ["R10-STORE-RACES"], str(got))
 
+    # --measure-sizes hands --sizes-via to size_durations.run: the module is a
+    # stub in sys.modules, so the mutation copies (no size_durations.py beside
+    # them) run this arm too, and no read reaches the network.
+    import types
+    from unittest import mock
+    vias = []
+    stub = types.SimpleNamespace(
+        SINCE="2026-10-12", DEFAULT_PERCENTILE=0.5,
+        run=lambda *a, **k: vias.append((a[7:8] or [k.get("via", "graphql")])[0])
+        or {"sizes_hours": {}})
+    with mock.patch.dict(sys.modules, {"size_durations": stub}), \
+            tempfile.TemporaryDirectory() as td:
+        for via in ("rest", "graphql"):
+            main(["--measure-sizes", "--sizes-via", via,
+                  "--out-durations", os.path.join(td, "d.json")])
+    expect("--measure-sizes --sizes-via rest reaches size_durations.run as via=rest "
+           "(null: graphql)", vias == ["rest", "graphql"], str(vias))
+
     gate = gate_minutes(durations)
     want_gate = 50.0 + 22.0 + 27.0 * (1.0 + 0.04)
     expect("the gate price includes the cancelled-leg rerun",
@@ -2879,7 +2973,7 @@ def selftest() -> int:
              "if inflow > 0:", "if inflow >= 0:"),
             ("inflow-rate",
              _m("def build_plan(roster: dict, ", "durations: dict, caps: dict, start: dt.datetime,"),
-             "n_exp = inflow * closure / 60.0", "n_exp = 1.0"),
+             "n_exp = inflow * closure_at / 60.0", "n_exp = 1.0"),
             ("height-tiebreak",
              _m("def dispatch_key(n: str, ", "tier: dict, savings: dict,"),
              _m("sav, -height[n], ", "-dur_min[n], n)"), "sav, n)"),
@@ -2901,6 +2995,9 @@ def selftest() -> int:
             ("held-carry-model",
              _m("def group_hours(group: dict, ", "durations: dict,"),
              _m('if stage == HELD_STAGE and ', 'durations.get("carries_per_part"):'), "if False:"),
+            ("live-review-stage",
+             _m("def group_hours(group: dict, ", "durations: dict,"),
+             _m("if is_live and stage in REVIEW_STAGES ", "and size in first:"), "if False:"),
             ("rounds-explicit",
              _m("def group_hours(group: dict, ", "durations: dict,"),
              _m("hours = work + (rounds - 1) * ", 'float(durations["round_hours"])'),
@@ -2951,6 +3048,25 @@ def selftest() -> int:
             ("stamp-cadence",
              _m("def build_plan(roster: dict, ", "durations: dict, caps: dict, start: dt.datetime,"),
              _m("while len(carry) >= ", "every:"), "while False:"),
+            ("review-min",
+             _m("def group_hours(group: dict, ", "durations: dict,"),
+             _m("left_rounds = max(rounds - 1, ", "1.0)"), "left_rounds = rounds"),
+            ("wall-hours",
+             _m("def build_plan(roster: dict, ", "durations: dict, caps: dict, start: dt.datetime,"),
+             _m('"wall_hours": round(closure_at ', "/ 60.0, 2),"),
+             '"wall_hours": round(closure / 60.0, 2),'),
+            ("closure-conditions",
+             _m("def build_plan(roster: dict, ", "durations: dict, caps: dict, start: dt.datetime,"),
+             _m('"closure_conditions": list(', 'CLOSURE_CONDITIONS),'),
+             '"closure_conditions": [],'),
+            ("closure-later-of",
+             _m("def build_plan(roster: dict, ", "durations: dict, caps: dict, start: dt.datetime,"),
+             _m("closure_at = max([stamps[-1][\"at\"]] + ", "list(post_end.values()))"),
+             "closure_at = max([stamps[-1][\"at\"]] + [])"),
+            ("closure-check-later-of",
+             _m("def check_plan(plan: dict", ") -> list:"),
+             _m("closure = max([mins(x[\"at\"]) for x in close_stamps] + ", "post_fin"),
+             "closure = max([mins(x[\"at\"]) for x in close_stamps] + []"),
             ("round-close-version",
              _m("def build_plan(roster: dict, ", "durations: dict, caps: dict, start: dt.datetime,"),
              _m("stamps.append({\"version\": closing, ", "\"at\": closure + closure_lead,"),
@@ -3154,6 +3270,8 @@ def parse_args(argv=None):
                         "(tools/plan/size_durations.py) into --out-durations")
     p.add_argument("--sizes-csv", default=None, help="--measure-sizes: write the raw rows here")
     p.add_argument("--prs-cache", default=None, help="--measure-sizes: read or write the fetch")
+    p.add_argument("--sizes-via", choices=("graphql", "rest"), default="graphql",
+                   help="--measure-sizes: the PR read (size_durations.READS)")
     p.add_argument("--out-durations", default=None)
     p.add_argument("--live-refs", default=None,
                    help="a saved `git ls-remote --heads` listing: liveness by evidence")
@@ -3189,7 +3307,7 @@ def main(argv=None) -> int:
         old = json.loads(target.read_text(encoding="utf-8")) if target.is_file() else {}
         got = size_durations.run(args.repo, args.roster_ref, args.repo_owner, size_durations.SINCE,
                                  args.prs_cache, args.sizes_csv,
-                                 size_durations.DEFAULT_PERCENTILE)
+                                 size_durations.DEFAULT_PERCENTILE, args.sizes_via)
         target.write_text(json.dumps({**old, **got}, indent=1, sort_keys=True) + "\n",
                           encoding="utf-8")
         print(f"measured sizes {got['sizes_hours']} -> {target}")
diff --git a/tools/plan/size_durations.py b/tools/plan/size_durations.py
index 9666a986b..ec7e9cbc6 100644
--- a/tools/plan/size_durations.py
+++ b/tools/plan/size_durations.py
@@ -56,8 +56,10 @@ The held (carries-open) model
     `carry_part_hours`; zero open carries plan zero.
 
 Percentiles are linear between order statistics (numpy's default rule).
-The one network read is `fetch()`, GraphQL queries through `gh api graphql`
-under `gh_read.retry`'s transient rule; nothing is written to GitHub.
+The one network read is `fetch()`, GraphQL queries through `gh api graphql`,
+or `fetch_rest()` (`--via rest`) where GraphQL is refused, both under
+`gh_read.retry`'s transient rule; nothing is written to GitHub. Either writes
+the same `--prs-cache` shape, and the model's `sizes_provenance` names the read.
 """
 
 from __future__ import annotations
@@ -71,6 +73,7 @@ import os
 import re
 import subprocess
 import sys
+import tempfile
 from pathlib import Path
 
 HERE = Path(__file__).resolve().parent
@@ -130,6 +133,17 @@ def iso(t: dt.datetime) -> str:
 
 # ------------------------------------------------------------------- reads
 
+def _gh(argv: list) -> str:
+    """One `gh api` read under `gh_read.retry`'s transient rule; raises on failure."""
+    def attempt():
+        r = subprocess.run(argv, capture_output=True, text=True)
+        return (r.stdout, None) if r.returncode == 0 else (None, r.stderr)
+    text, failure, _, why = gh_read.retry(attempt, gh_read.gh_wait, __import__("time").sleep)
+    if failure is not None:
+        raise RuntimeError(f"{' '.join(argv[:3])} failed {why}: {gh_read.one_line(failure)}")
+    return text
+
+
 def fetch(repo_owner: str, since: str) -> list:
     """Merged PRs created since `since`, newest first, flattened. Read only."""
     owner, name = repo_owner.split("/")
@@ -139,20 +153,54 @@ def fetch(repo_owner: str, since: str) -> list:
         argv = ["gh", "api", "graphql", "-f", "query=" + query]
         if cursor:
             argv += ["-f", "cursor=" + cursor]
-
-        def attempt():
-            r = subprocess.run(argv, capture_output=True, text=True)
-            return (r.stdout, None) if r.returncode == 0 else (None, r.stderr)
-        text, failure, _, why = gh_read.retry(attempt, gh_read.gh_wait, __import__("time").sleep)
-        if failure is not None:
-            raise RuntimeError(f"gh api graphql failed {why}: {gh_read.one_line(failure)}")
-        page = json.loads(text)["data"]["repository"]["pullRequests"]
+        page = json.loads(_gh(argv))["data"]["repository"]["pullRequests"]
         out += [flatten(n) for n in page["nodes"]]
         if not page["pageInfo"]["hasNextPage"] or page["nodes"][-1]["createdAt"] < since:
             return out
         cursor = page["pageInfo"]["endCursor"]
 
 
+def rest_node(pr: dict, commits: list, comments: list) -> dict:
+    """A REST pull (`GET pulls`), its commits and its issue comments in the
+    GraphQL node shape `flatten` reads: either read writes the one cache."""
+    first = ((commits or [{}])[0].get("commit") or {}).get("author") or {}
+    return {
+        "number": pr["number"], "title": pr.get("title"),
+        "headRefName": (pr.get("head") or {}).get("ref"), "createdAt": pr["created_at"],
+        "mergedAt": pr["merged_at"], "body": pr.get("body"),
+        "mergeCommit": {"oid": pr.get("merge_commit_sha")},
+        "commits": {"nodes": [{"commit": {"authoredDate": first.get("date")}}]},
+        "comments": {"nodes": [{"createdAt": c["created_at"], "body": c.get("body")}
+                               for c in comments]},
+    }
+
+
+def fetch_rest(repo_owner: str, since: str, get=None) -> list:
+    """`fetch` over the REST API, for a seat whose `gh api graphql` is refused:
+    the same PRs (merged, created since `since`, newest first) and fields, at
+    three reads per PR; `get(path)` is the read, injected by the self-test.
+    Unlike `fetch`, it drops the last page's PRs created before `since`, which
+    no round-10 group owns (`SINCE`). Read only."""
+    get = get or (lambda path: json.loads(_gh(["gh", "api", f"repos/{repo_owner}/{path}"])))
+    out, page = [], 1
+    while True:
+        pulls = get(f"pulls?state=closed&sort=created&direction=desc&per_page=100&page={page}")
+        for p in pulls:
+            if p["created_at"] < since:
+                return out
+            if p.get("merged_at"):
+                n = p["number"]
+                out.append(flatten(rest_node(p, get(f"pulls/{n}/commits?per_page=1"),
+                                             get(f"issues/{n}/comments?per_page=100"))))
+        if len(pulls) < 100:
+            return out
+        page += 1
+
+
+#: `--via`: the read that builds the PR list, recorded in `sizes_provenance`.
+READS = {"graphql": fetch, "rest": fetch_rest}
+
+
 def flatten(n: dict) -> dict:
     """One PR in the shape every function below reads (and the cache holds)."""
     first = ((n.get("commits") or {}).get("nodes") or [{}])[0].get("commit") or {}
@@ -598,6 +646,90 @@ def self_test() -> int:
         if not cond:
             fails.append(name)
 
+    # The REST read writes the GraphQL read's cache, field for field.
+    gq = {"number": 7, "title": "t", "headRefName": "fix/x", "createdAt": "2026-10-13T00:00:00Z",
+          "mergedAt": "2026-10-14T00:00:00Z", "body": "b", "mergeCommit": {"oid": "a" * 40},
+          "commits": {"nodes": [{"commit": {"authoredDate": "2026-10-12T23:00:00Z"}}]},
+          "comments": {"nodes": [{"author": {"login": "x"}, "createdAt": f"2026-10-13T0{i}:00:00Z",
+                                  "body": f"Fix review: merge {i}abcdef0\nmore"} for i in (1, 2)]}}
+    rp = {"number": 7, "title": "t", "head": {"ref": "fix/x"}, "created_at": "2026-10-13T00:00:00Z",
+          "merged_at": "2026-10-14T00:00:00Z", "body": "b", "merge_commit_sha": "a" * 40}
+    rcommits = [{"commit": {"author": {"date": d}}}
+                for d in ("2026-10-12T23:00:00Z", "2026-10-13T05:00:00Z")]
+    rcomments = [{"user": {"login": "x"}, "created_at": c["createdAt"], "body": c["body"]}
+                 for c in gq["comments"]["nodes"]]
+    check("rest_node: a REST pull, its commits and comments flatten as the GraphQL node",
+          flatten(rest_node(rp, rcommits, rcomments)) == flatten(gq))
+    check("rest_node (null): no commit read falls back to creation, as the GraphQL node does",
+          flatten(rest_node(rp, [], []))["first_commit_at"] == rp["created_at"])
+
+    def pull(n, day, merged=True):
+        return dict(rp, number=n, created_at=f"2026-10-{day}T00:00:00Z",
+                    merged_at="2026-10-30T00:00:00Z" if merged else None)
+    pages = {1: [pull(500 - i, 20, merged=i % 2 == 0) for i in range(100)],
+             2: [pull(300, 13), pull(299, 11), pull(298, 13)]}
+    asked = []
+
+    def fake_get(path):
+        asked.append(path)
+        m = re.search(r"pulls\?.*page=(\d+)$", path)
+        if m:
+            return pages.get(int(m.group(1)), [])
+        return rcommits if "/commits" in path else rcomments
+    got = fetch_rest("o/r", "2026-10-12", fake_get)
+    check("fetch_rest: merged PRs only, across a full page, stopping at the first created "
+          "before since", [p["number"] for p in got] == [500 - i for i in range(0, 100, 2)] + [300]
+          and any("page=2" in a for a in asked) and not any("page=3" in a for a in asked))
+    pages[2] = [pull(300, 13), pull(297, 14)]
+    pages[3] = [pull(200, 13)]
+    got = fetch_rest("o/r", "2026-10-12", fake_get)
+    check("fetch_rest: a short page ends the read", [p["number"] for p in got][-2:] == [300, 297])
+    check("fetch_rest: a PR created at the cut-off instant is read",
+          [p["number"] for p in fetch_rest("o/r", "2026-10-13T00:00:00Z", fake_get)][-1] == 297)
+    check("_gh: a read returns its stdout", _gh([sys.executable, "-c", "print(7)"]) == "7\n")
+    try:
+        _gh([sys.executable, "-c", "import sys; sys.exit(3)"])
+        gh_raised = False
+    except RuntimeError:
+        gh_raised = True
+    check("_gh (null): a failed read raises, never returns", gh_raised)
+    with tempfile.TemporaryDirectory() as td:
+        cache, calls = os.path.join(td, "prs.json"), []
+        fresh = read_prs({"rest": lambda o, s_: calls.append((o, s_)) or [{"number": 1}]},
+                         "rest", "o/r", "2026-10-12", cache)
+        again = read_prs({"rest": lambda o, s_: calls.append((o, s_)) or []},
+                         "rest", "o/r", "2026-10-12", cache)
+    check("read_prs: a fresh read writes the cache, a second replays it without a read",
+          fresh == ([{"number": 1}], False) and again == ([{"number": 1}], True)
+          and calls == [("o/r", "2026-10-12")])
+    check("input_note names the read and a replayed cache",
+          input_note("rest", "2026-10-12", 3, True) == " Input: 3 merged PRs created since "
+          "2026-10-12, read by size_durations.fetch_rest (--via rest), replayed from a "
+          "--prs-cache file." and input_note("graphql", "x", 1, False).endswith(
+              "size_durations.fetch (--via graphql)."))
+
+    # `run` reads through `reads[via]` and its provenance names that read.
+    roster, prs = _fixture()
+    with tempfile.TemporaryDirectory() as td:
+        rf, read_by = os.path.join(td, "roster.json"), []
+        Path(rf).write_text(json.dumps(roster), encoding="utf-8")
+        fakes = {v: (lambda o, s_, v=v: read_by.append(v) or prs) for v in READS}
+        ran = {v: run(td, None, "o/r", "2026-10-12", None, None, DEFAULT_PERCENTILE, v,
+                      reads=fakes, roster_file=rf)["sizes_provenance"] for v in ("rest", "graphql")}
+    check("run --via rest: the rest read builds the PR list", read_by == ["rest", "graphql"])
+    check("run --via rest: sizes_provenance ends naming fetch_rest",
+          ran["rest"].endswith(input_note("rest", "2026-10-12", len(prs), False)))
+    check("run --via graphql (null): sizes_provenance ends naming fetch",
+          ran["graphql"].endswith(input_note("graphql", "2026-10-12", len(prs), False)))
+    with tempfile.TemporaryDirectory() as td:
+        rf, pc = os.path.join(td, "roster.json"), os.path.join(td, "prs.json")
+        Path(rf).write_text(json.dumps(roster), encoding="utf-8")
+        Path(pc).write_text(json.dumps(prs), encoding="utf-8")
+        replay = run(td, None, "o/r", "2026-10-12", pc, None, DEFAULT_PERCENTILE, "rest",
+                     reads={"rest": lambda o, s_: 1 / 0}, roster_file=rf)["sizes_provenance"]
+    check("run --prs-cache: sizes_provenance ends naming the replay, no read made",
+          replay.endswith(input_note("rest", "2026-10-12", len(prs), True)))
+
     roster, prs = _fixture()
     mapping = prs_of_groups(roster, prs, {})
     check("branch maps R9-A to #11", mapping.get("R9-A") == [11])
@@ -709,14 +841,12 @@ def self_test() -> int:
 # -------------------------------------------------------------------- main
 
 def run(repo: str, roster_ref: str | None, repo_owner: str, since: str,
-        cache: str | None, csv_path: str | None, percentile: float) -> dict:
-    roster, _, _ = replan.load_roster(repo, roster_ref)
-    if cache and Path(cache).is_file():
-        prs = json.loads(Path(cache).read_text(encoding="utf-8"))
-    else:
-        prs = fetch(repo_owner, since)
-        if cache:
-            Path(cache).write_text(json.dumps(prs), encoding="utf-8")
+        cache: str | None, csv_path: str | None, percentile: float,
+        via: str = "graphql", reads: dict = READS, roster_file: str | None = None) -> dict:
+    """The size model over `reads[via]`'s PR list; `reads` and `roster_file`
+    (`replan.load_roster`'s `file`) are injected by the self-test."""
+    roster, _, _ = replan.load_roster(repo, roster_ref, file=roster_file)
+    prs, replayed = read_prs(reads, via, repo_owner, since, cache)
     rows, parts, held, _mapping = measure(repo, roster, prs)
     if csv_path:
         write_csv(rows, csv_path)
@@ -726,10 +856,30 @@ def run(repo: str, roster_ref: str | None, repo_owner: str, since: str,
         write_csv(held_report(roster, prs, _mapping), stem + "-held-carries.csv")
     out = model(rows, percentile)
     out.update(carry_model(parts, held, percentile))
+    out["sizes_provenance"] += input_note(via, since, len(prs), replayed)
     out["sizes_measured_at"] = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
     return out
 
 
+def read_prs(reads: dict, via: str, repo_owner: str, since: str, cache: str | None):
+    """(PRs, replayed): the `--prs-cache` file when it exists, else `reads[via]`,
+    written to the cache when one is named."""
+    if cache and Path(cache).is_file():
+        return json.loads(Path(cache).read_text(encoding="utf-8")), True
+    prs = reads[via](repo_owner, since)
+    if cache:
+        Path(cache).write_text(json.dumps(prs), encoding="utf-8")
+    return prs, False
+
+
+def input_note(via: str, since: str, n: int, replayed: bool) -> str:
+    """The provenance sentence naming the model's input, so a re-derivation by
+    the other read can tell drift from a different input."""
+    return (f" Input: {n} merged PRs created since {since}, read by "
+            f"size_durations.{READS[via].__name__} (--via {via})"
+            + (", replayed from a --prs-cache file." if replayed else "."))
+
+
 def main(argv=None) -> int:
     p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
     p.add_argument("--self-test", action="store_true")
@@ -738,13 +888,16 @@ def main(argv=None) -> int:
     p.add_argument("--repo-owner", default="tvofi/heatpump_optimizer")
     p.add_argument("--since", default=SINCE, help="earliest PR creation read")
     p.add_argument("--prs-cache", default=None, help="read (or write) the fetched PRs here")
+    p.add_argument("--via", choices=sorted(READS), default="graphql",
+                   help="the read that fetches the PRs (rest where graphql is refused)")
     p.add_argument("--csv", default=None)
     p.add_argument("--percentile", type=float, default=DEFAULT_PERCENTILE)
     p.add_argument("--out-durations", default=None, help="merge the model into this file")
     a = p.parse_args(argv)
     if a.self_test:
         return self_test()
-    out = run(a.repo, a.roster_ref, a.repo_owner, a.since, a.prs_cache, a.csv, a.percentile)
+    out = run(a.repo, a.roster_ref, a.repo_owner, a.since, a.prs_cache, a.csv, a.percentile,
+              a.via)
     if a.out_durations:
         target = Path(a.out_durations)
         old = json.loads(target.read_text(encoding="utf-8")) if target.is_file() else {}

## Before you return the verdict (P275)
Run `python3 -I tools/audit/carry_audit.py check --body <PR body file> --comments <file holding [{"id": 0, "body": <verdict.md text>}]>`. Give every reported item its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>`;
an evidence line flagged by its wording takes `Carry: dismissed: evidence, not a finding`. Return the verdict only at rc 0.
