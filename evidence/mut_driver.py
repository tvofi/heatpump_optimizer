import subprocess, sys, pathlib, re
wt = pathlib.Path(sys.argv[1]); f = wt/"tools/audit/seat/merge_train.py"
orig = f.read_text()
M = [
 ("M4 record_drafts call site deleted", "            self.record_drafts(queue)\n", "            pass\n"),
 ("M7 pending set ignored", "            pending.add(name)", "            pass"),
 ("M8 zero-time not cleared", "if x and not x.startswith(\"0001\")]", "if x]"),
 ("M9 startedAt fallback dropped", "(c.get(\"completedAt\"), c.get(\"startedAt\"))", "(c.get(\"completedAt\"),)"),
 ("M5 read->pass", "                item[\"draft\"] = is_draft(self, int(item[\"pr\"]))", "                pass"),
 ("M1 last-listed wins", "        if name not in best or (stamp, i) >= best[name][0]:", "        if True:"),
]
try:
    for name, a, b in M:
        n = orig.count(a)
        if n != 1:
            print(f"{name}: SKIP anchor count {n}"); continue
        f.write_text(orig.replace(a, b))
        p = subprocess.run([sys.executable, "tools/audit/seat/merge_train.py", "--self-test"], cwd=wt, capture_output=True, text=True)
        out = p.stdout + p.stderr
        fails = [l.strip() for l in out.splitlines() if l.strip().startswith("FAIL")]
        tail = out.strip().splitlines()[-1] if out.strip() else ""
        verdict = "KILLED" if p.returncode else "SURVIVED"
        print(f"{name}: {verdict} rc={p.returncode} fails={len(fails)}")
        for l in fails[:4]: print("    ", l[:200])
        if p.returncode and not fails: print("     tail:", tail[:200])
        sys.stdout.flush()
finally:
    f.write_text(orig)
