import subprocess, sys, pathlib
root = pathlib.Path(sys.argv[1]); f = root / "tools/audit/seat/plan_audit.py"
orig = f.read_text()
M = [
 ("b01 deferred bug", 'and not row.get("card")', 'and False', 1),
 ("b02 unknown finding", 'if fid not in ids:', 'if False:', 1),
 ("b03 double closure", 'elif fid in owner:', 'elif False:', 1),
 ("b04 NO-READ hold", 'if unread and entry["direction"] != "undecided":', 'if False:', 1),
 ("b05 rank edge", 'edges.get((group, waits)) not in adrs', 'False', 1),
 ("b06 unexamined", 'if want == 2 and not entry.get("examined_by"):', 'if False:', 1),
 ("b07 rank mismatch", 'if entry.get("rank") != want:', 'if False:', 1),
 ("b08 authored time", 'kind = "AUTHORED time" if _TIME_KEY.search(key) else "UNKNOWN key"', 'kind = "UNKNOWN key"', 1),
 ("b09 closed grammar", 'if key not in OBJECTIVE_KEYS[level]:', 'if False:', 1),
 ("b10 unranked open", 'if not g.get("done") and name not in entries:', 'if False:', 1),
 ("b11 undisposed", 'if line.get("status") == "MISSED" and not dispositions.get(line.get("key")):', 'if False:', 1),
 ("b12 stale pin", 'if a["generated"].get("roster_blob") != pin.get("roster_blob"):', 'if False:', 1),
 ("b13 floor filter", 'return {g for g in projected if ranks.get(g) != 2 or g in reached}', 'return set(projected)', 1),
 ("b14 reduced refusal", 'for extra in sorted(set(b["groups"]) - want):', 'for extra in []:', 1),
 ("b15 projection differs", 'if committed != want:', 'if False:', 1),
 ("b16 UNPREDICTED", 'elif move == better and term not in credited:', 'elif False:', 1),
 ("b17 merged", 'status = "HELD" if group in merged else "MISSED"', 'status = "HELD"', 1),
 ("b18 NOT-DUE", '        if not due_next:\n            line(key, "NOT-DUE"', '        if False:\n            line(key, "NOT-DUE"', 1),
 ("b19 version-free", '"wall_hours": a["summary"]["wall_hours"], "closure": a["summary"]["closure"],', '"wall_hours": a["summary"]["wall_hours"], "closure": a["summary"]["closure_stamp"],', 1),
 ("b20 lead clock", 'lead = [_hours(g["finish"], start)', 'lead = [_hours(g["finish"], g.get("start") or start)', 1),
 ("b21 NO-READ guard", 'if was is None or now is None:', 'if False and (was is None or now is None):', 1),
 # reviewer's own
 ("r01 undecided no builder", 'if entry["direction"] == "undecided" and unread and not entry.get("builder"):', 'if False:', 1),
 ("r02 no basis", 'if entry["direction"] != "undecided" and not entry.get("basis"):', 'if False:', 1),
 ("r03 foreign term", 'for term in sorted(set(stated) - set(terms)):', 'for term in []:', 1),
 ("r04 group no entry", 'for group in sorted(named - set(entries)):', 'for group in []:', 1),
 ("r05 entry no group", 'for group in sorted(set(entries) - named):', 'for group in []:', 1),
 ("r06 unknown class", 'if cid not in classes:', 'if False:', 1),
 ("r07 rank bugs", 'if any(f in bugs for f in entry.get("removes") or []):', 'if False:', 1),
 ("r08 weakened", 'VERIFIED = ("verified", "weakened")', 'VERIFIED = ("verified",)', 1),
 ("r09 bug class", 'if f.get("verdict") in VERIFIED and f.get("stop_rule_class") == "bug"}', 'if f.get("verdict") in VERIFIED}', 1),
 ("r10 hold worse", 'line(key, "MISSED" if move == worse else "HELD", f"moved {move}, predicted hold")', 'line(key, "HELD", f"moved {move}, predicted hold")', 1),
 ("r11 tie band", 'if abs(now - was) <= width:', 'if False:', 1),
 ("r12 examined settle", 'seen = any(r.get("group") == group for r in rows)', 'seen = True', 1),
 ("r13 due_next", 'due_next = record.get("round") == (plan.get("round") or 0) + 1', 'due_next = False', 1),
 ("r14 reduced drops", 'for gone in sorted(want - set(b["groups"])):', 'for gone in []:', 1),
 ("r15 start pin", 'if a["generated"].get("start") != pin.get("start") or b["generated"].get("start") != pin.get("start"):', 'if False:', 1),
 ("r16 no block", 'if not isinstance(block, dict):\n        return ["NO objective block', 'if False:\n        return ["NO objective block', 1),
 ("r17 defer verdict", 'row.get("verdict") == "defer" and', 'True and', 1),
 ("r18 rank1 only edges", 'if not isinstance(entry, dict) or entry.get("rank") != 1:', 'if not isinstance(entry, dict):', 1),
 ("r19 waits rank2", '(entries.get(waits) or {}).get("rank") == 2 and', 'True and', 1),
 ("r20 want up/down", 'line(key, "HELD" if move == want else "MISSED", f"moved {move}, predicted {want}")', 'line(key, "HELD", f"moved {move}, predicted {want}")', 1),
 ("r21 missed keyed", 'line(key, "MISSED" if found else "HELD", f"{len(found)} keyed row(s) match", terms)', 'line(key, "HELD", f"{len(found)} keyed row(s) match", terms)', 1),
 ("r22 held credit", 'credited = {t for ln in lines if ln["status"] == "HELD" for t in ln["terms"]}', 'credited = {t for ln in lines for t in ln["terms"]}', 1),
 ("r23 delay rank1", 'if rank == 1 and fa and fb:', 'if fa and fb:', 1),
 ("r24 production lead", 'if name in production and g.get("finish")]', 'if g.get("finish")]', 1),
 ("r25 share band", 'width = 2 * (p1 * (1 - p1) / n1 + p2 * (1 - p2) / n2) ** 0.5', 'width = 0', 1),
 ("r26 count band", 'width = 2 * (was + now) ** 0.5', 'width = 0', 1),
 ("r27 examined rank2 settle", '            if entry.get("rank") == 2:\n                rows = _keyed(record, "examined_by")', '            if True:\n                rows = _keyed(record, "examined_by")', 1),
 ("r28 injected production", '        if group in production:\n            next_round', '        if True:\n            next_round', 1),
 ("r29 reached closure", 'if rank == 1:\n            reached |= after_closure(group, projected)', 'if True:\n            reached |= after_closure(group, projected)', 1),
]
surv = []
for name, old, new, n in M:
    c = orig.count(old)
    if c != n:
        print(f"SKIP {name}: pattern occurs {c}x"); surv.append(name + " (SKIP)"); continue
    f.write_text(orig.replace(old, new))
    r = subprocess.run([sys.executable, str(f), "--self-test"], capture_output=True, text=True, cwd=root)
    fails = [l.strip() for l in r.stdout.splitlines() if l.strip().startswith("FAIL")]
    tb = [l for l in r.stderr.splitlines() if "Error" in l][-1:] 
    if r.returncode == 0:
        print(f"SURVIVED {name}"); surv.append(name)
    else:
        print(f"KILLED {name} rc={r.returncode}: {fails[:3] or tb}")
f.write_text(orig)
print("survivors:", surv)
