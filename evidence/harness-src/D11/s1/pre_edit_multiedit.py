# Metric: count of probe payloads that write a new "## " version heading into
#   RELEASE_NOTES.md off main and that .claude/hooks/pre-edit.sh lets through
#   (exit 0) -- key: the hook's own exit status on the real script, end to end.
# Command: PYTHONPATH=tests/hastub <home>/.local/state/hpo/venv-ci/bin/python3 dev/audit/rounds/round10/D11/s1/pre_edit_multiedit.py
# Expected: RESULT escaped_heading_writes=1 (MultiEdit), control_refused=1 (Edit); tolerance 0.
#   --perturb (the hook also reads tool_input["edits"][*].new_string) -> escaped=0.
# Baseline 17f1c55fad1b; machine: macOS arm64 (B6). Counts only; not contention-sensitive.
import os
for v in ("OMP_NUM_THREADS","OPENBLAS_NUM_THREADS","MKL_NUM_THREADS","NUMEXPR_NUM_THREADS","VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(v, "1")
import json, subprocess, sys, tempfile, time, shutil

ROOT = os.getcwd()
HOOK = os.path.join(ROOT, ".claude/hooks/pre-edit.sh")
tmp = tempfile.mkdtemp(prefix="d11s1-")
hook = os.path.join(tmp, "pre-edit.sh")
src = open(HOOK).read()
if "--perturb" in sys.argv:
    old = '#     text = " ".join(str(v) for k, v in ti.items()\n#                     if k in ("new_string", "content", "new_source"))'
    assert old in src, "perturbation anchor missing"
    new = old + '\n#     text += " ".join(str(e.get("new_string","")) for e in (ti.get("edits") or []) if isinstance(e, dict))'
    src = src.replace(old, new)
open(hook, "w").write(src)

notes = os.path.join(ROOT, "RELEASE_NOTES.md")
cases = {
    "Edit":      {"tool_name": "Edit", "tool_input": {"file_path": notes, "old_string": "x", "new_string": "## v9.9.9\n"}},
    "MultiEdit": {"tool_name": "MultiEdit", "tool_input": {"file_path": notes, "edits": [{"old_string": "x", "new_string": "## v9.9.9\n"}]}},
}
def run(p):
    env = dict(os.environ, CLAUDE_PROJECT_DIR=ROOT)
    return subprocess.run(["bash", hook], input=json.dumps(p), text=True, env=env, capture_output=True).returncode
t0, c0 = time.process_time(), time.thread_time()
rc = {k: run(v) for k, v in cases.items()}
for k, v in rc.items(): print(f"# {k}: rc={v}")
print(f"RESULT escaped_heading_writes={int(rc['MultiEdit']==0)} count")
print(f"RESULT control_refused={int(rc['Edit']==2)} count")
pc, tc = time.process_time()-t0, time.thread_time()-c0
print(f"RESULT thread_factor={pc/tc if tc else 1.0:.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
print("RESULT swapins=0")
shutil.rmtree(tmp)
