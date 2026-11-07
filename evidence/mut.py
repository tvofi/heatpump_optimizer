import subprocess, sys, os
from pathlib import Path
W = Path("/tmp/tmp.NxRJ50dQWt/wt"); MT = "tools/audit/seat/merge_train.py"; HR = "dev/audit/harnesses/r10_codescan_wait_race.py"
M = [
 ("hotfix-defer-empty", MT, '        if red != [GATE]:\n            return []\n', '        return []\n'),
 ("hotfix-no-cascade-grace", MT, '                    elif graced and red == [GATE]:', '                    elif False:'),
 ("hotfix-count-action_required", MT, 'st.strip() not in ("completed", "action_required", "")', 'st.strip() not in ("completed", "")'),
 ("c3-runs_approved-True", MT, '    return bool(rows) and not any("action_required" in r for r in rows)', '    return True'),
 ("c3-runs_approved-noempty", MT, '    return bool(rows) and not any(', '    return not any('),
 ("c3-unreadable-approves", MT, 'return subject if code or not runs_approved(o) else None', 'return subject if not runs_approved(o) else None'),
 ("c6-drop-started_at", MT, ' and at and (c.get("started_at") or "") >= at]', ']'),
 ("c6-drop-head-pin", MT, '        if code == 0 and ref.strip() != head:', '        if False:'),
 ("c6-red-not-refused", MT, 'c.get("conclusion") in ("failure", "cancelled") for c in mine)', 'c.get("conclusion") in () for c in mine)'),
 ("c6-no-comment-needed", MT, '            if not (at and said):', '            if not at:'),
 ("c7-transient-False", MT, '    return not GIT_REFUSED.search(output) and bool(GIT_TRANSIENT.search(output))', '    return False'),
 ("c7-ignore-refused", MT, '    return not GIT_REFUSED.search(output) and bool(GIT_TRANSIENT.search(output))', '    return bool(GIT_TRANSIENT.search(output))'),
 ("c7-wrapper-unhooked", MT, '                return run_git_retry(run, argv, self.sleep, self.log, **kw)', '                return run(argv, **kw)'),
 ("c9-drop-admission", MT, '    if not item.get("draft") or not is_draft(t, pr):', '    if not is_draft(t, pr):'),
 ("c9-no-reread", MT, '    if is_draft(t, pr):\n        raise Stop("undraft", f"#{pr} is a draft again', '    if False:\n        raise Stop("undraft", f"#{pr} is a draft again'),
 ("c9-ready-fail-continues", MT, '    if code:\n        raise Stop("undraft", f"gh pr ready', '    if False:\n        raise Stop("undraft", f"gh pr ready'),
 ("c9-add-no-record", MT, '            entry["draft"] = True', '            pass'),
 ("c8-no-fallback", HR, 'for size in (100, 30):', 'for size in (100,):'),
]
def run(f):
    if f == HR:
        p = subprocess.run([sys.executable, HR, "--selftest"], cwd=W, capture_output=True, text=True)
    else:
        p = subprocess.run([sys.executable, MT, "--self-test"], cwd=W, capture_output=True, text=True, env=dict(os.environ, PYTHONPATH="tests/hastub"))
    out = p.stdout + p.stderr
    fails = [l.strip() for l in out.splitlines() if l.strip().startswith(("FAIL", "not ok"))]
    summ = [l for l in out.splitlines() if "checks," in l]
    return p.returncode, summ[-1] if summ else out.strip().splitlines()[-1][:160], fails
only = sys.argv[1:]
for name, f, a, b in M:
    if only and name not in only: continue
    p = W / f; src = p.read_text()
    assert src.count(a) == 1, (name, src.count(a))
    p.write_text(src.replace(a, b))
    try:
        rc, s, fails = run(f)
    finally:
        p.write_text(src)
    print(f"MUTANT {name}: rc={rc} {s} {'KILLED' if rc else 'SURVIVED'}")
    for x in fails[:6]: print("   ", x[:150])
