import subprocess, sys, pathlib
F = pathlib.Path("/home/user/heatpump_optimizer/tools/audit/carry_audit.py")
orig = F.read_bytes()
M = [
 ("D1-dismiss-1word", "if len(re.findall(r\"[A-Za-z0-9]{2,}\", reason)) < 2:", "if len(re.findall(r\"[A-Za-z0-9]{2,}\", reason)) < 1:"),
 ("D2-closed-issue", "not in (None, \"open\"):", "in ():"),
 ("D3-done-group", "        if not roster_lib.is_open(g):\n            return False", "        if False:\n            return False"),
 ("D4-missing-brief", "            if not any(h.is_file() for h in hits):", "            if False:"),
 ("D5-owned-done-group", "            if roster_lib.is_open(g):\n                for n in", "            if True:\n                for n in"),
 ("D6-bad-as-routed", "(\"bad\" if bad else \"routed\")", "\"routed\""),
 ("D7-break-continue", "        break  # prose after the destinations", "        continue  # prose after the destinations"),
 ("D8-item-word", "if not tok or tok.lower() == \"item\" or", "if not tok or"),
 ("D9-unowned-issue", "            if n not in self.owned:", "            if False:"),
 ("D10-unknown-group", "        if g is None:\n            return False", "        if g is None:\n            return True"),
 ("D11-refs-not-merged", "r[\"dests\"] = r[\"dests\"] + refs.get(r[\"id\"], [])", "r[\"dests\"] = r[\"dests\"] or refs.get(r[\"id\"], [])"),
 ("D12-brief-owns-issue", "                self.owned.setdefault(int(n), f.name)", "                pass"),
 ("D13-carry-file-issue", "            carry.add(n)", "            pass"),
]
try:
  for name, a, b in M:
    s = orig.decode()
    if s.count(a) != 1: print(f"RESULT mutant={name} verdict=pattern-count-{s.count(a)}"); continue
    F.write_text(s.replace(a, b))
    r = subprocess.run([sys.executable, "-I", str(F), "--self-test"], capture_output=True, text=True, cwd=F.parents[2])
    tail = (r.stdout.strip().splitlines() or [""])[-1]
    fails = [l for l in r.stdout.splitlines() if "FAIL" in l][:2]
    print(f"RESULT mutant={name} rc={r.returncode} {tail!r} {'killed' if r.returncode else 'SURVIVED'}")
    for l in fails: print("   ", l)
    if r.returncode and "checks" not in tail: print("   stderr:", r.stderr.strip().splitlines()[-1:])
finally:
  F.write_bytes(orig)
