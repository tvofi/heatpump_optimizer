"""Reviewer's mutant driver for #3464 (the REVIEWER's instrument, not the finder's or fixer's).
Each mutant: fresh `git archive` copy of the head, one text replacement, one command."""
import subprocess, sys, tempfile, shutil, re, os
from pathlib import Path
REPO, HEAD = sys.argv[1], sys.argv[2]
PY = sys.executable
def copy():
    d = tempfile.mkdtemp(prefix="mut")
    subprocess.run(f"git -C {REPO} archive {HEAD} | tar -x -C {d}", shell=True, check=True)
    return Path(d)
def sub(d, f, old, new, count=1):
    p = d / f; t = p.read_text()
    assert t.count(old) >= 1, (f, old)
    if count == 1: assert t.count(old) == 1, (f, old, t.count(old))
    p.write_text(t.replace(old, new))
ENT = r'''
import sys
from pathlib import Path
src = Path("tests/entities.py").read_text().split("\n")
i = next(n for n, l in enumerate(src) if l.startswith('_SR = Path("dev/governance/roles")'))
k = next(n for n, l in enumerate(src) if n > i and l.startswith('R.check('))
j = next(n for n, l in enumerate(src) if n > k and l == ")")
class R:
    @staticmethod
    def check(name, ok, detail=""):
        print(("ok   " if ok else "FAIL ") + name + ("" if ok else "  [" + detail + "]")); sys.exit(0 if ok else 1)
exec("\n".join(src[i:j+1]))
'''
SELF = lambda f: [PY, "-I", f"tools/audit/seat/{f}.py", "--self-test"]
PC = "| `plan_coordinator_cap` | `replan.py --coordinator-cap`: the plan's coordinator cap (replan's own default when absent) |\n"
def fix_main(d): sub(d, "tools/audit/seat/sweep_template.md", PC, "")
TICKROWS = ("| `tick_alive` | the tick seat's liveness file, touched every pass |\n",
            "| `tick_brief` | the tick seat's brief, the prompt a restarted tick seat receives |\n| `tick_stale_min` | minutes after which a silent tick seat is dead |\n")
def s1(d):
    sub(d, "tools/audit/seat/sweep_template.md", "| `tick_log` |", TICKROWS[0] + TICKROWS[1] + "| `tick_log` |")
    sub(d, "tools/audit/seat/sweep_template.md", "(5) Tick digest. Read", "(5) Tick watcher. If {{tick_alive}} is missing or older than {{tick_stale_min}} minutes, the tick seat has died: start a new one whose prompt is the contents of {{tick_brief}}. Read")
M = [
 ("NULL-pulse", SELF("pulse"), []),
 ("P1", SELF("pulse"), [lambda d: sub(d, "tools/audit/seat/pulse.py", 'STANDING = {"merge": 120, "dispatch": 60}', 'STANDING = {"tick": 70, "merge": 120, "dispatch": 60}')]),
 ("P2", SELF("pulse"), [lambda d: sub(d, "tools/audit/seat/pulse.py", 'STANDING = {"merge": 120, "dispatch": 60}', 'STANDING = {"merge": 120, "dispatch": 60, "roster": 60}')]),
 ("P3-rev", SELF("pulse"), [lambda d: sub(d, "tools/audit/seat/pulse.py", 'RETIRED = ("tick", "roster")', 'RETIRED = ("tick",)')]),
 ("P4-rev", SELF("pulse"), [lambda d: sub(d, "tools/audit/seat/pulse.py", " (tick and roster are retired into beat rows)", "")]),
 ("NULL-sweep-asis", SELF("sweep_render"), []),
 ("NULL-sweep-mainfix", SELF("sweep_render"), [fix_main]),
 ("S1-mainfix", SELF("sweep_render"), [fix_main, s1]),
 ("S1-asis", SELF("sweep_render"), [s1]),
 ("NULL-cloud", SELF("cloud_dispatch"), []),
 ("C1", SELF("cloud_dispatch"), [lambda d: sub(d, "tools/audit/seat/cloud_dispatch.py", "        if vtip:\n            _git(repo_dir, \"fetch\", \"-q\", \"origin\", vtip[0])\n            verdict = (vtip[0], _git(repo_dir, \"show\", f\"{vtip[0]}:verdict.md\").split(\"\\n\", 1)[0])", "        verdict = ('f' * 40, 'Design review: revise x')")]),
 ("C2", SELF("cloud_dispatch"), [lambda d: sub(d, "tools/audit/seat/cloud_dispatch.py", "        if vtip:\n", "        if False:\n")]),
 ("C3", SELF("cloud_dispatch"), [lambda d: sub(d, "tools/audit/seat/cloud_dispatch.py", "            verdict = (vtip[0], _git(", "            verdict = (design_tip(repo_dir, group_id), _git(")]),
 ("C4-rev", SELF("cloud_dispatch"), [lambda d: sub(d, "tools/audit/seat/cloud_dispatch.py", '    if role == "designer":  # a revise', '    if role in ("designer", "design-reviewer"):  # a revise')]),
 ("C5-rev", SELF("cloud_dispatch"), [lambda d: sub(d, "tools/audit/seat/cloud_dispatch.py", 'f"first line `{verdict[1]}`: read it first', 'f"read it first')]),
 ("NULL-entities", [PY, "-c", ENT], []),
 ("E1", [PY, "-c", ENT], [lambda d: sub(d, "dev/governance/roles/standing.md", "## Recycle\n", "")]),
 ("E2", [PY, "-c", ENT], [lambda d: (lambda p: p.write_text(re.sub(r"Dispatch a reviewer at a pull request's head H.*?\(`ci-autofix.md`\)\. ", "", p.read_text(), flags=re.S)))(d / "dev/governance/roles/standing.md")]),
 ("E3", [PY, "-c", ENT], [lambda d: sub(d, "dev/governance/roles/standing.md", " or `claims-autofix`", "")]),
 ("E4", [PY, "-c", ENT], [lambda d: (lambda p: p.write_text(re.sub(r"   \*\*`ci_predict.py` printing `BOOTSTRAP`\*\*.*?\(decision 0013, Consequences\)\.\n\n", "", p.read_text(), flags=re.S)))(d / "dev/governance/roles/fixer.md")]),
 ("E5", [PY, "-c", ENT], [lambda d: sub(d, "dev/governance/roles/proposal-triage.md", ", under `standing.md`", "")]),
 ("E6", [PY, "-c", ENT], [lambda d: sub(d, "dev/governance/roles/standing-merge.md", "(`standing.md`; `orchestrator.md` section 5)", "(`orchestrator.md` section 5)")]),
 ("E7-rev", [PY, "-c", ENT], [lambda d: sub(d, "dev/governance/roles/standing-tick.md", "(`standing.md`)", "")]),
 ("E8-rev", [PY, "-c", ENT], [lambda d: (lambda p: p.write_text(re.sub(r"## Wait\n.*?(?=## Reads)", "## Wait\n\n", p.read_text(), flags=re.S)))(d / "dev/governance/roles/standing.md")]),
 ("E9-rev", [PY, "-c", ENT], [lambda d: (lambda p: p.write_text(re.sub(r"## Recycle\n.*?(?=## Alive files)", "## Recycle\n\n", p.read_text(), flags=re.S)))(d / "dev/governance/roles/standing.md")]),
 ("D1-rev-merge-drops-verdict", SELF("cloud_dispatch"), [lambda d: sub(d, "tools/audit/seat/cloud_dispatch.py", "args = dict(design=design, verdict=verdict, env_id", "args = dict(design=design, env_id")]),
 ("D2-rev-merge-drops-partline", SELF("cloud_dispatch"), [lambda d: sub(d, "tools/audit/seat/cloud_dispatch.py", ' + (f"\\n{pline}\\n" if pline else ""),', ',')]),
]
only = set(sys.argv[3:])
for name, cmd, muts in M:
    if only and name not in only: continue
    d = copy()
    before = subprocess.run(["git", "-C", REPO, "rev-parse", HEAD], capture_output=True, text=True).stdout.strip()
    for m in muts: m(d)
    r = subprocess.run(cmd, cwd=d, capture_output=True, text=True)
    out = (r.stdout + r.stderr).strip().split("\n")
    fails = [l.strip() for l in out if "FAIL" in l]
    line = " || ".join(fails) if fails else out[-1]
    print(f"RESULT MUTANT {name} {'KILLED' if r.returncode else 'SURVIVED'} at {before[:12]} rc={r.returncode}: {line[:330]}", flush=True)
    shutil.rmtree(d)
