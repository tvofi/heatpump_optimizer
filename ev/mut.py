import subprocess, sys, pathlib
WT = sys.argv[1]
E, Q, P = "tools/audit/seat/roster_edit.py", "tools/audit/seat/roster_queue.py", "tools/audit/seat/postmerge.py"
M = [
 ("M1 --add default store", E, 'nargs="+", action="extend",', 'nargs="+",'),
 ("M2 _on_origin no fetch", E, '    subprocess.run(["git", "-C", str(checkout), "fetch", "-q", "origin",\n                    f"+refs/heads/{branch}', '    0 and subprocess.run(["git", "-C", str(checkout), "fetch", "-q", "origin",\n                    f"+refs/heads/{branch}'),
 ("M3 no update-ref after push", E, '"update-ref",\n                            f"refs/remotes/origin/{branch}", head]', '"rev-parse",\n                            f"refs/remotes/origin/{branch}"]'),
 ("M4 empty base set", E, "        new = [e for e in errs if e not in base_errs]", "        new = list(errs)"),
 ("M5 base set = all errs (pass every error)", E, "        new = [e for e in errs if e not in base_errs]", "        new = []"),
 ("M6 drop whole-check", E, "        if not whole:\n            return False, tail", "        if False:\n            return False, tail"),
 ("M7 no WARN detail", E, "        return True, warn", "        return True, ''"),
 ("M8 write_roster no base_text", E, "ok, detail = lint_gate(checkout, lint_cwd, path, base_text)", "ok, detail = lint_gate(checkout, lint_cwd, path)"),
 ("M9 batch: keep refused line", Q, "        items = good\n", "        pass\n"),
 ("M10 batch: no per-line catch", Q, "            except (SystemExit, re_.Refuse) as e:\n                # one line", "            except ZeroDivisionError as e:\n                # one line"),
 ("M11 batch: no failure report", Q, '        rep(f"roster: batch failed', '        0 and rep(f"roster: batch failed'),
 ("M12 batch: no mark refused", Q, '                if mark:\n                    mark_line(a.queue, ln, "refused")\n        items = good', '                if 0:\n                    mark_line(a.queue, ln, "refused")\n        items = good'),
 ("M13 refusal_tail ignores gate", Q, '        if "LINT GATE REFUSED" in ln:', '        if False:'),
 ("M14 _run_op uses old tail", Q, '+ refusal_tail(out))', '+ " | ".join(out.strip().split("\\n")[-3:])[:400])'),
 ("M15 refusal_detail no ERROR lead", P, '    errs = [ln for ln in lines if ln.startswith("ERROR")][:3]', '    errs = []'),
 ("M16 postmerge old last-line", P, "        last = refusal_detail(o)", '        last = o.strip().splitlines()[-1][:160] if o.strip() else "no output"'),
]
T = {E: [sys.executable, E, "--self-test"], Q: [sys.executable, "-I", Q, "--self-test"], P: [sys.executable, "-I", P, "--self-test"]}
sel = sys.argv[2:] or None
for name, f, old, new in M:
    if sel and name.split()[0] not in sel: continue
    fp = pathlib.Path(WT, f); src = fp.read_text()
    if src.count(old) != 1:
        print(f"RESULT {name}: NOT-APPLIED (count={src.count(old)})", flush=True); continue
    fp.write_text(src.replace(old, new))
    try:
        r = subprocess.run(T[f], cwd=WT, capture_output=True, text=True, timeout=600)
        out = r.stdout + r.stderr
        fails = [l for l in out.splitlines() if l.lstrip().startswith("FAIL")]
        tail = out.strip().splitlines()[-1] if out.strip() else ""
        verdict = "KILLED" if r.returncode != 0 else "SURVIVED"
        print(f"RESULT {name}: {verdict} rc={r.returncode} :: {tail[:120]} :: {'; '.join(fails[:2])[:300]}", flush=True)
    finally:
        fp.write_text(src)
