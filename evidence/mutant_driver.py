import subprocess, sys, shutil, pathlib
R = pathlib.Path("/home/user/rev")
M = [
 ("NULL comment-only", "tools/ci/sweep.py", "    def jobs_of(self, run_id):\n", "    def jobs_of(self, run_id):   # null\n"),
 ("G1 deferral waits again", "tools/ci/gate.py", "        if ok or now() - t0 + POLL_S > lag_bound(why):",
  "        if ok or now() - t0 + POLL_S > (GATE_WAIT_MAX_S if why == [deferral(busy(ctx, api['runs_at_head']))] else lag_bound(why)):"),
 ("G2 lagged not recorded", "tools/ci/gate.py", "        lagged = lagged or why\n        sleep(POLL_S)", "        sleep(POLL_S)"),
 ("S1 settle -> old SKIP", "tools/ci/sweep.py", "            return self.settle(run_id, pr, head)", "            return 0"),
 ("S2 arm1 late source removed", "tools/ci/sweep.py", "        if (any(j.get(\"name\") != \"gate\" and (j.get(\"completed_at\") or \"~\") > t0 for j in jobs)", "        if (False"),
 ("S3 arm2 removed", "tools/ci/sweep.py", "                or (i > run_id and t0 <= gs <= t1)\n", ""),
 ("S4 arm3 removed", "tools/ci/sweep.py", "                or (i < run_id and g.get(\"conclusion\") == \"success\" and gs <= t1 and ge >= t0)):", "                ):"),
 ("S5 arm1 excludes no gate", "tools/ci/sweep.py", "j.get(\"name\") != \"gate\" and (j.get(\"completed_at\")", "(j.get(\"completed_at\")"),
 ("S6 no finishing poll", "tools/ci/sweep.py", "            if not finishing or self.clock() + POLL_FLOOR > deadline:", "            if True:"),
 ("S7 no unconcluded skip", "tools/ci/sweep.py", "        if unconcluded:\n", "        if False:\n"),
 ("S8 success gate re-run too", "tools/ci/sweep.py", "            if g.get(\"conclusion\") != \"success\" and late:", "            if late:"),
 ("S9 completed-but-run-open not polled", "tools/ci/sweep.py", "                         or (gates[r[\"id\"]].get(\"status\") == \"completed\" and r[\"status\"] != \"completed\")]", "                         ]"),
 ("S10 live check dropped", "tools/ci/sweep.py", "            if not self.live(pr, head):\n", "            if False:\n"),
]
for name, f, a, b in M:
    p = R / f; orig = p.read_text()
    assert orig.count(a) == 1, (name, orig.count(a))
    p.write_text(orig.replace(a, b))
    try:
        res = []
        for cmd in (["python3","-B","tools/ci/sweep.py","--self-test"], ["python3","-B","tools/ci/gate.py","--self-test"],
                    ["python3","-I","-B","dev/audit/harnesses/r10_gate_busy_defer_3.py","replay"]):
            o = subprocess.run(cmd, cwd=R, capture_output=True, text=True, timeout=600)
            lines = (o.stdout + o.stderr).strip().splitlines()
            tail = [l for l in lines if "checks," in l or l.startswith("RESULT")] or lines[-1:]
            fails = [l for l in lines if l.startswith("FAIL")][:2]
            res.append(f"{cmd[2].split('/')[-1]}: {tail[-1] if tail else '?'} rc={o.returncode}" + ("".join(f"\n      {x[:200]}" for x in fails)))
        print(f"MUTANT {name}:\n  " + "\n  ".join(res), flush=True)
    finally:
        p.write_text(orig)
