# reviewer's mutants on the repair commit's changed lines (e64e24a5 vs 14a73c15), run in /home/user/mut at a7223767
import subprocess, sys, pathlib
B = "tools/audit/seat/beat_jobs.py"; T = "tools/audit/seat/sweep_template.md"
M = [
 ("N1 fetch-rc-guard-off", B, "    if rc != 0:  # refs/gantt/ would still", "    if False:  # refs/gantt/ would still"),
 ("N2 fetch-rc-line-dropped", B, '[f"gantt: UNREADABLE fetch rc={rc}: {(err.strip().splitlines() or [\'\'])[-1]}"]', '[]'),
 ("N3 template-row-gantt_acks-deleted", T, "| `gantt_acks` | the Gantt acks file", "| gantt_acks_x | the Gantt acks file"),
 ("N4 template-row-fire_ledger-deleted", T, "| `fire_ledger` | the session's fire ledger", "| fire_ledger | the session's fire ledger"),
 ("N5 new-undeclared-get", B, '    ledger = ctx.overlay.get("fire_ledger")', '    ledger = ctx.overlay.get("fire_ledger") or ctx.overlay.get("zz_new_key")'),
 ("N6 new-undeclared-need", B, 'ctx.need("gantt", "repo", "plan_json", "gantt_roster", "gantt_acks")', 'ctx.need("gantt", "repo", "plan_json", "gantt_roster", "gantt_acks", "zz_need_key")'),
 ("N7 new-undeclared-loop", B, '("unheld_skip", "--skip")):', '("unheld_skip", "--skip"), ("zz_loop_key", "--zz")):'),
 ("N8 template-citation-train_glob-dropped", T, "the train logs {{train_glob}} and", "the train logs and"),
]
root = pathlib.Path("/home/user/mut")
for name, f, a, b in M:
    p = root / f; src = p.read_text()
    if src.count(a) != 1: print(name, "ANCHOR", src.count(a), flush=True); continue
    p.write_text(src.replace(a, b))
    res = []
    for s in ("beat_jobs", "sweep_render"):
        r = subprocess.run(["python3", "-I", f"tools/audit/seat/{s}.py", "--self-test"], cwd=root, capture_output=True, text=True, timeout=900)
        o = (r.stdout + r.stderr).strip().splitlines()
        res.append((s, r.returncode, o[-1:] , [l.strip() for l in o if "FAIL" in l][:3]))
    p.write_text(src)
    print(name, res, flush=True)
