import subprocess, sys, pathlib
R = pathlib.Path("/root/rev")
M = [
 ("m1-dr-dispatch-clause", "tools/audit/seat/ledger.py", "        if t in review_at and review_at[t] >= tip_at[t]:\n            continue\n", ""),
 ("m2-dr-stage-gate", "tools/audit/seat/ledger.py", " or stage not in DESIGN_REVIEW_STAGES \\\n", " \\\n"),
 ("m3-dr-disposition", "tools/audit/seat/ledger.py", "or disp.get(f\"refs/heads/design/{t}\", (\"\",))[0] == tip:", "or False:"),
 ("m4-dr-verdict-at-tip", "tools/audit/seat/ledger.py", "if (m and m.group(2) == tip) or stage", "if False or stage"),
 ("m5-dr-call-dropped", "tools/audit/seat/orchestrator_tick.py", "        self.design_reviews_owed(S, rl, roster, lg, (designs, reviewers, firsts, disp), names)\n", ""),
 ("m6-dr-fetch-unreadable", "tools/audit/seat/orchestrator_tick.py", "        if self.git([\"fetch\", \"-q\", \"origin\", *refs])[0]:\n            return self.unreadable(S, \"design reviews owed\", \"could not fetch the design refs\")\n", ""),
 ("m7-ud-seatless", "tools/audit/seat/orchestrator_tick.py", "SEATLESS_STAGES = UNBLOCKABLE_STAGES + (\"carries-open\",)", "SEATLESS_STAGES = UNBLOCKABLE_STAGES"),
 ("m8-ud-after-clear", "tools/audit/seat/orchestrator_tick.py", "            if res.get(\"stage\") == \"carries-open\" and all(", "            if res.get(\"stage\") == \"carries-open\" and any("),
 ("m9-ud-startafter", "tools/audit/seat/orchestrator_tick.py", "                if m and opened is None:", "                if False:"),
 ("m10-ud-ref-age", "tools/audit/seat/orchestrator_tick.py", "(at := self._commit_at(\"origin/\" + r)) is None or at >= opened", "(at := self._commit_at(\"origin/\" + r)) is None or True"),
 ("m11-ud-unreadable", "tools/audit/seat/orchestrator_tick.py", "        if code:\n            return self.unreadable(S, what, o.strip()[-100:])\n        seats: dict = {}", "        seats: dict = {}"),
 ("m12-ud-cp", "tools/audit/seat/orchestrator_tick.py", "UNDISPATCHED:{' CP' if gid in critical else ''}", "UNDISPATCHED:{''}"),
 ("m13-oc-window", "tools/audit/seat/orchestrator_tick.py", "if any(a is None or self.now - a <= window for a in at):", "if any(a is None for a in at):"),
 ("m14-oc-gates", "tools/audit/seat/orchestrator_tick.py", "a in open_g and rl.gates(groups[a])]", "a in groups]"),
 ("m15-oc-outside", "tools/audit/seat/orchestrator_tick.py", "if open_g[g].get(\"source\") == \"outside\"]", "]"),
 ("m16-op-stuck3", "tools/audit/seat/orchestrator_tick.py", "if any(f.get(\"n\", 0) >= 3 for f in fails)", "if any(f.get(\"n\", 0) >= 1 for f in fails)"),
 ("m17-op-lastline", "tools/audit/seat/orchestrator_tick.py", "(f\" -- opener last: {last[-1]}\" if last else \"\")", "(f\" -- opener last: {last[0]}\" if last else \"\")"),
 ("m18-op-absent-stranded", "tools/audit/seat/orchestrator_tick.py", "if stranded and not od.is_dir():", "if not od.is_dir():"),
 ("m19-ou-key-dr", "tools/audit/seat/owed_unactioned.py", "the tip is the id: a new tip re-raises\n    if m:\n        return m.group(1), [m.group(2)]", "the tip is the id: a new tip re-raises\n    if m:\n        return m.group(1), []"),
 ("m26-ou-key-ud", "tools/audit/seat/owed_unactioned.py", "    m = re.match(r\"UNDISPATCHED:(?: CP)? (\\S+) \", body)", "    m = None and re.match(r\"UNDISPATCHED:(?: CP)? (\\S+) \", body)"),
 ("m20-ou-family-dr", "tools/audit/seat/owed_unactioned.py", "|DESIGN-REVIEW OWED:|UNDISPATCHED:", "|UNDISPATCHED:"),
 ("m21-bj-family-oc", "tools/audit/seat/beat_jobs.py", "|OUTSIDE-CHAIN-IDLE ", ""),
 ("m22-ledger-arm", "tools/audit/seat/ledger.py", "        (\"refs/heads/design/\", \"design-review\"),\n", ""),
 ("m23-ud-wipseat", "tools/audit/seat/orchestrator_tick.py", "SEAT_REFS = (\"refs/heads/dispatch/fixer-*\", \"refs/heads/handoff/*\",", "SEAT_REFS = (\"refs/heads/dispatch/fixer-*\","),
 ("m24-dr-cp", "tools/audit/seat/ledger.py", "{' CP' if group in critical else ''}", "{''}"),
 ("m25-dr-timeread-unreadable", "tools/audit/seat/orchestrator_tick.py", "            if code or not o.strip().isdigit():\n                return self.unreadable(S, \"design reviews owed\", f\"no commit time for {sha[:12]}\")\n", "            if code or not o.strip().isdigit():\n                continue\n"),
]
TESTS = {"tools/audit/seat/ledger.py":["tools/audit/seat/orchestrator_tick.py --self-test","tools/audit/seat/ledger.py --self-test"],
 "tools/audit/seat/orchestrator_tick.py":["tools/audit/seat/orchestrator_tick.py --self-test"],
 "tools/audit/seat/owed_unactioned.py":["tools/audit/seat/orchestrator_tick.py --self-test","tools/audit/seat/owed_unactioned.py --self-test"],
 "tools/audit/seat/beat_jobs.py":["tools/audit/seat/beat_jobs.py --self-test --no-mutants"]}
sel = sys.argv[1:]
for name, f, old, new in M:
    if sel and name not in sel: continue
    p = R/f; src = p.read_text()
    n = src.count(old)
    if n != 1: print(f"RESULT {name}: SKIP pattern count {n}"); continue
    p.write_text(src.replace(old, new))
    try:
        outs=[]
        for t in TESTS[f]:
            r = subprocess.run(["timeout","220","python3",*t.split()],cwd=R,capture_output=True,text=True)
            fails=[l for l in (r.stdout+r.stderr).splitlines() if l.lstrip().startswith(("FAIL","fail"," FAIL")) or "FAIL " in l[:8]]
            outs.append((t.split()[0].split('/')[-1], r.returncode, (r.stdout+r.stderr).strip().splitlines()[-1:] , fails[:3]))
        killed = any(rc!=0 for _,rc,_,_ in outs)
        print(f"RESULT {name}: {'KILLED' if killed else 'SURVIVED'} {[(a,b,c) for a,b,c,_ in outs]}")
        for _,_,_,fl in outs:
            for l in fl: print("    ", l[:200])
    finally:
        p.write_text(src)
