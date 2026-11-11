import subprocess, sys, pathlib, re
wt = pathlib.Path(sys.argv[1]); f = wt/"tools/audit/seat/merge_train.py"
orig = f.read_text()
M = [
 ("M1 last-listed wins", "        if name not in best or (stamp, i) >= best[name][0]:", "        if True:"),
 ("M2 never-admitted arm off", "                if not item.get(\"draft\") or undrafted:", "                if False:"),
 ("M3 STILL_DRAFT arm deleted", "            if STILL_DRAFT.search(said):", "            if False and STILL_DRAFT.search(said):"),
 ("M4 record_drafts call site deleted", "            self.record_drafts(queue)\n", "            pass\n"),
 ("M5 record_drafts body read -> pass", "                item[\"draft\"] = is_draft(self, int(item[\"pr\"]))", "                pass"),
 ("M6 record_drafts overwrites recorded", "            if \"draft\" not in item:\n                item[\"draft\"]", "            if True:\n                item[\"draft\"]"),
 ("M7 pending set ignored", "            pending.add(name)", "            pass"),
 ("M8 zero-time not cleared", "            stamp = \"\"\n", "            pass\n"),
 ("M9 startedAt fallback dropped", "c.get(\"completedAt\") or c.get(\"startedAt\") or \"\"", "c.get(\"completedAt\") or \"\""),
 ("M10 tie keeps earlier listed", "(stamp, i) >= best[name][0]", "(stamp, i) > best[name][0] if False else stamp > best[name][0][0]"),
 ("M11 undrafted flag never set", "                undrafted = True\n", "                pass\n"),
 ("M12 record_drafts real guard inverted", "        if not self.real:\n            return\n        for item in queue:", "        if self.real:\n            return\n        for item in queue:"),
 ("M13 policy_refusal back to last-listed", "        last = rollup_states(d.get(\"statusCheckRollup\") or ())", "        last = {(c.get('name') or c.get('context') or '?'): (c.get('conclusion') or c.get('state') or c.get('status') or '').upper() for c in (d.get('statusCheckRollup') or ())}"),
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
