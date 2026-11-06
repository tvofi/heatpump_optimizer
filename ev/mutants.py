import subprocess, sys, pathlib
W = pathlib.Path(open(pathlib.Path.home() / "W").read().strip())
wt = W / "mut"
if not wt.exists():
    subprocess.run(["git", "-C", "/home/user/heatpump_optimizer", "worktree", "add", "-q", "--detach", str(wt),
                    "e81028ccef62bed5e4c6b6042f28193bc1d7ce8b"], check=True)
L = "tools/audit/seat/ledger.py"
T = "tools/audit/seat/orchestrator_tick.py"
B = "tools/audit/seat/beat_jobs.py"
O = "tools/audit/seat/owed_unactioned.py"
LT = ["python3", L, "--self-test"]
MUTANTS = [
    ("M1 drop ancestor test", L,
     '        if subprocess.run(["git", "-C", cwd, "merge-base", "--is-ancestor", prior, head],\n                          env=env, capture_output=True).returncode != 0:\n            return False\n',
     "", LT),
    ("M2 any single-parent commit carries (drop row-only arm)", L,
     'if files is None or set(files.split()) != {f"dev/programme/delivery/{n}.md"}:', "if files is None:", LT),
    ("M3 drop conflict-resolution check", L,
     "if resolved is None or resolved.strip() or any(", "if resolved is None or any(", LT),
    ("M4 drop second-parent-in-main check", L,
     "if resolved is None or resolved.strip() or any(", "if resolved is None or resolved.strip() or False and any(", LT),
    ("M5 record_owed boundary >= to >", L, "if age >= minutes:", "if age > minutes:", LT),
    ("M6 record_owed ignores approval", L, '                or (pr.get("reviewDecision") or "").upper() != "APPROVED":', "                or False:", LT),
    ("M7 call site drops recarry", T, ',\n                                       lg.git_recarry(self.checkout or ".", "origin/main")', "", ["python3", T, "--self-test"]),
    ("M8 call site flags CARRY lines", T, 'flag=not text.startswith("CARRY:")', "flag=True", ["python3", T, "--self-test"]),
    ("M9 call site drops record_owed", T, "for text in lg.record_owed(prs, now):", "for text in []:", ["python3", T, "--self-test"]),
    ("M10 beat_jobs FAMILY drops RECORD-OWED", B, "|RECORD-OWED:", "", ["python3", B, "--self-test"]),
    ("M11 owed_unactioned FAMILY drops RECORD-OWED", O, "|RECORD-OWED:", "", ["python3", O, "--self-test"]),
    ("M12 recarry for dispatched only by verdict (drop dispatched priors)", L,
     ' + sorted(h for k, h in dispatched if k == str(n))', "", LT),
]
for name, f, old, new, cmd in MUTANTS:
    p = wt / f
    src = p.read_text()
    if src.count(old) != 1:
        print(f"RESULT {name}: NOT-APPLIED (pattern count {src.count(old)})"); continue
    p.write_text(src.replace(old, new))
    r = subprocess.run(cmd, cwd=wt, capture_output=True, text=True, timeout=900)
    p.write_text(src)
    fails = [l for l in (r.stdout + r.stderr).splitlines() if "FAIL" in l][:3]
    print(f"RESULT {name}: {'KILLED' if r.returncode else 'SURVIVED'} rc={r.returncode} {fails}")
st = subprocess.run(["git", "-C", str(wt), "status", "--porcelain"], capture_output=True, text=True).stdout
print("worktree clean after restore:", st == "")
