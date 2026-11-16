import subprocess, shutil, sys, pathlib
WT = pathlib.Path("/root/wt")
M = [
 ("owed_watch.py", 'ok = any(low.startswith(f"rev-{n}-") for n in g["prs"])', 'ok = False'),
 ("owed_watch.py", 'if "CP" in tags or "OUTSIDE" in tags:', 'if "CP" in tags:'),
 ("owed_watch.py", 'if r.get("state") == "APPROVED" and (r.get("commit") or {}).get("oid") == p["headRefOid"]]', 'if r.get("state") == "APPROVED"]'),
 ("owed_watch.py", 'last = max((when for when', 'last = min((when for when'),
 ("owed_watch.py", 'if not (dsha and f"at head {head}" in first.get(dsha, "")):', 'if not dsha:'),
 ("owed_watch.py", 'return any(when is not None and when >= t and _names_group(g, l) for when, l in rows)', 'return any(_names_group(g, l) for when, l in rows)'),
 ("owed_watch.py", '"dispatch": "PROMPT.md"}', '"dispatch": "PROMPT.txt"}'),
 ("owed_watch.py", 'if p["head_t"] is None:', 'if False:'),
 ("owed_watch.py", 'raise Unreadable(f"critical path: {why}")', 'cp = set()'),
 ("owed_watch.py", "if not r.startswith((\"dispatch/design\", \"dispatch/reviewer-rev-\"))):", "):"),
 ("owed_watch.py", 'elif family in ("design", "design-verdict"):\n            ok = low == gid', 'elif family in ("design", "design-verdict"):\n            ok = low.startswith(gid)'),
 ("owed_watch.py", "if age > FIRE_GRACE_MIN and not any(f.name in l for _, l in rows):", "if age > FIRE_GRACE_MIN:"),
 ("orchestrator_tick.py", "return owatch.seat_on(n, topics, heads, self._fired(), self.now, self._age_min, self._blocked_md, kinds)", "return owatch.seat_on(n, topics, heads, self._fired(), self.now, self._age_min, self._blocked_md)"),
 ("orchestrator_tick.py", "m = owatch.FIX_VERDICT.match(line)", "m = owatch.DESIGN_VERDICT.match(line)"),
 ("beat_jobs.py", 'got = ctx.need("cp-owed", "repo", "fire_ledger")', 'got = ctx.need("cp-owed", "repo", "repo")'),
]
CMDS = [["python3","-I","tools/audit/seat/owed_watch.py","--self-test"],
        ["python3","tools/audit/seat/orchestrator_tick.py","--self-test"],
        ["python3","-I","tools/audit/seat/beat_jobs.py","--self-test","--no-mutants"]]
for f, old, new in M:
    p = WT/"tools/audit/seat"/f; src = p.read_text()
    if src.count(old) != 1: print("SKIP-nomatch", f, old[:60]); continue
    p.write_text(src.replace(old, new))
    try:
        res = []
        for c in CMDS:
            r = subprocess.run(c, cwd=WT, capture_output=True, text=True, timeout=300)
            tail = [l for l in (r.stdout+r.stderr).splitlines() if "FAIL" in l or "self-test:" in l][:2]
            res.append(f"{c[2].split('/')[-1]} rc={r.returncode} {tail[-1] if tail else ''}")
        killed = any("rc=0" not in x for x in res)
        print(("KILLED  " if killed else "SURVIVED"), f, repr(old[:70]), "|", " ; ".join(res))
    finally:
        p.write_text(src)
