import subprocess, sys, pathlib, shutil
root = pathlib.Path(sys.argv[1]); which = sys.argv[2:]
M = {
 "M9": ("tools/pr/cancel_superseded.py", "if has_merge_verdict(api, a.repo, pr) is not False:", "if False:"),
 "M9b": ("tools/pr/cancel_superseded.py", "if has_merge_verdict(api, a.repo, pr) is not False:", "if has_merge_verdict(api, a.repo, pr) is True:"),
 "M9c": ("tools/pr/cancel_superseded.py", "                protected.add(pr)  # a verdict", "                pass  # a verdict"),
 "M10": ("tools/audit/seat/ci_pause.py", "        if ci_priority.is_priority(self._tier(mine[0], roster, crit, setting)[0] if mine else \"main-push\", setting):\n            return None\n", ""),
 "M11": ("tools/audit/seat/ci_pause.py", "if p is not None and ci_priority.is_priority(self._tier(p, roster, crit, setting)[0], setting):", "if p is not None:"),
 "M12": ("tools/audit/seat/ci_pause.py", "if mine else \"main-push\"", "if mine else \"tier1\""),
 "M13": ("tools/audit/seat/ci_pause.py", "        if code:\n            return None\n        by_ref", "        by_ref"),
 "M14": ("tools/audit/seat/ci_pause.py", "by_ref = {p[\"ref\"]: p for p in prs if not p[\"fork\"]}", "by_ref = {}"),
 "M15": ("tools/audit/seat/merge_train.py", "                if not reran:\n                    self.hold_reruns(h, \"stale re-run\")\n", ""),
 "M16": ("tools/audit/seat/merge_train.py", "        for k in range(HOLD_POLLS if cp is not None else 0):", "        for k in range(0):"),
 "M17": ("tools/audit/seat/merge_train.py", "            self.sleep(POLL_SECONDS)\n        if cp is not None:", "            break\n        if cp is not None:"),
 "M18": ("tools/audit/seat/beat_jobs.py", "        extra += [\"--train-state\", str(ctx.overlay[\"train_state\"])]", "        pass"),
 "M19": ("tools/audit/seat/sweep_render.py", ",\n                  \"train_state\": \"--train-state\"}", "}"),
 "M20": ("tools/audit/seat/ci_priority.py", "max(0.0, (min(starts) - t0) / 60)", "max(0.0, (max(starts) - t0) / 60)"),
 "M21": ("tools/audit/seat/ci_priority.py", "        if w is None:\n            out[\"unstarted\"] += 1\n            continue\n", "        w = w or 0.0\n"),
}
test = {"tools/pr/cancel_superseded.py": "tools/pr/cancel_superseded.py", "tools/audit/seat/ci_pause.py": "tools/audit/seat/ci_pause.py",
        "tools/audit/seat/merge_train.py": "tools/audit/seat/merge_train.py", "tools/audit/seat/beat_jobs.py": "tools/audit/seat/beat_jobs.py",
        "tools/audit/seat/sweep_render.py": "tools/audit/seat/sweep_render.py", "tools/audit/seat/ci_priority.py": "tools/audit/seat/ci_priority.py"}
for k in which or M:
    f, old, new = M[k]; p = root / f; src = p.read_text()
    n = src.count(old)
    if n != 1:
        print(f"{k} NOT-APPLIED count={n}", flush=True); continue
    p.write_text(src.replace(old, new))
    try:
        r = subprocess.run([sys.executable, "-I", test[f], "--self-test"], cwd=root, capture_output=True, text=True, timeout=1500)
        out = r.stdout + r.stderr
        fails = [l.strip()[:150] for l in out.splitlines() if l.strip().startswith("FAIL")][:3]
        summ = [l for l in out.splitlines() if "self-test:" in l and "checks" in l][-1:] or [out.strip().splitlines()[-1][:150] if out.strip() else ""]
        print(f"{k} {f} rc={r.returncode} {'KILLED' if r.returncode else 'SURVIVED'} {summ} {fails}", flush=True)
    finally:
        p.write_text(src)
