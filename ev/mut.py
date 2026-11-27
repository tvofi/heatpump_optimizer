import subprocess, shutil, re, sys
from pathlib import Path
SRC = Path("/root/wt/.github/workflows")
T = (SRC/"ci.yml").read_text()
JOBIF = "    if: github.event_name == 'pull_request' || github.event_name == 'pull_request_review'\n    runs-on: ubuntu-latest\n    timeout-minutes: 5\n    permissions:\n      contents: read\n      pull-requests: read\n      actions: write\n"
STEPIF = """        if: >-
          github.event_name == 'pull_request'
          && github.event.sender.login != 'github-actions[bot]'
          && github.event.pull_request.head.repo.full_name == github.repository
"""
a = T.index("      # Independent of the cancel step's outcome")
b = T.index("        run: python3 -I tools/ci/gate.py --refresh\n") + len("        run: python3 -I tools/ci/gate.py --refresh\n")
REF = T[a:b]
RIF = "        if: ${{ !cancelled() && steps.restore.outcome == 'success' }}\n"
RENV = "        env:\n          GH_TOKEN: ${{ github.token }}\n        run: python3"
def rep(t, o, n):
    assert t.count(o) == 1, o
    return t.replace(o, n)
def m7(t):
    t = rep(t, REF, "")
    k = t.index("      - name: Restore the programs from the base")
    return t[:k] + REF + t[k:]
def m8(t):
    s = t.index("  cancel-superseded:\n"); e = t.index("  # >>> units:")
    job = t[s:e]
    return t[:e] + job.replace("cancel-superseded:", "refresh:", 1) + t[e:]
M = {
 "M1": lambda t: rep(t, STEPIF, ""),
 "M2": lambda t: rep(t, RIF, "        if: ${{ !cancelled() }}\n"),
 "M3": lambda t: rep(t, RIF, "        if: ${{ steps.restore.outcome == 'success' }}\n"),
 "M4": lambda t: rep(t, "tools/pr/cancel_superseded.py 'tools/ci/*.py'", "tools/pr/cancel_superseded.py"),
 "M5": lambda t: rep(t, REF, ""),
 "M6": lambda t: rep(t, JOBIF, JOBIF.replace(" || github.event_name == 'pull_request_review'", "")),
 "M7": m7, "M8": m8,
 "M9": lambda t: rep(t, RENV, "        run: python3"),
 "M10": lambda t: rep(t, JOBIF, JOBIF.replace("    if: github.event_name == 'pull_request' || github.event_name == 'pull_request_review'", "    if: (github.event_name == 'pull_request' || github.event_name == 'pull_request_review') && github.event.pull_request.head.repo.full_name == github.repository")),
}
def run(d):
    o = subprocess.run(["/opt/hpo/venv-ci/bin/python3", "/root/drv/drv.py", str(d)], capture_output=True, text=True)
    lines = [l for l in o.stdout.splitlines() if l[:4] in ("PASS", "FAIL")]
    if len(lines) != 5: return "ERROR " + (o.stderr or o.stdout)[-300:]
    return ",".join("abcde"[i] for i, l in enumerate(lines) if l.startswith("FAIL")) or "none"
out = ["baseline (unmodified): failing = " + run(SRC), "", "mutant -> failing checks (a..e)"]
for k, f in M.items():
    d = Path(f"/root/drv/m_{k}"); shutil.rmtree(d, ignore_errors=True); shutil.copytree(SRC, d)
    (d/"ci.yml").write_text(f(T))
    out.append(f"{k}: {run(d)}")
Path("/root/drv/results.txt").write_text("\n".join(out)+"\n"); print("\n".join(out))
