"""D0.M8's install-day universe does not survive the finder export (round 11 D0-s3,
baseline 92d38ecb, box B3).

Metric: lines `tools/audit/enumerate.py d15-installs` prints in a tree after
`tools/audit/prepare_baseline.sh --strip <tree> 11` (the finder wall + the
earlier-round strip every finder export goes through), against the lines it
prints in the same tree before the strip (the control). Key: the enumerator's
own stdout line count and exit status.

Command (from the export root):
  PYTHONPATH=tests/hastub $HOME/venv-ci/bin/python3 dev/audit/rounds/round11/D0/s3/wall_d15.py [--perturb keep_bundles]
Expected: before_strip_lines=1 rc=0; after_strip_lines=0 rc!=0 (REFUSE: evidence
... is not in the tree). Under --perturb keep_bundles (one line added to the
strip's keep set: every `evidence` path dev/audit/config/bundles.json names)
after_strip_lines=1 (moves up, to the control).
The evidence file is planted as a placeholder at the path bundles.json names,
since the export this seat works in no longer has it (that absence is the
finding): the strip decides by path, never by content.
Instrumented symbols: tools/audit/prepare_baseline.sh:strip_earlier_rounds,
tools/audit/enumerate.py:d15.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import sys
import json
import shutil
import tempfile
import subprocess
import time

KEEP_LINE = 'keep = {f for fs in json.loads((root / "tests/closures.json").read_text())["closures"].values()\n'
KEEP_ADD = ('keep |= {b["evidence"] for b in json.loads((root / "dev/audit/config/bundles.json").read_text())'
            '.get("bundles", []) if b.get("evidence")}\n')


def count(tree):
    p = subprocess.run([sys.executable, os.path.join(tree, "tools/audit/enumerate.py"), "--repo", tree, "d15-installs"],
                       capture_output=True, text=True)
    lines = [l for l in p.stdout.splitlines() if l.strip()]
    return len(lines), p.returncode, (p.stderr.strip().splitlines() or [""])[-1][:200]


def main():
    perturb = "--perturb" in sys.argv and sys.argv[sys.argv.index("--perturb") + 1] == "keep_bundles"
    t0 = time.process_time(); tt0 = time.thread_time()
    tmp = tempfile.mkdtemp(prefix="d0s3-wall-")
    try:
        tree = os.path.join(tmp, "tree")
        for p in ("tests", "tools/audit", "dev/audit/config"):
            shutil.copytree(p, os.path.join(tree, p), ignore=shutil.ignore_patterns("__pycache__", "replay", "golden"))
        bundles = json.load(open("dev/audit/config/bundles.json"))["bundles"]
        for b in bundles:
            ev = os.path.join(tree, b["evidence"])
            os.makedirs(os.path.dirname(ev), exist_ok=True)
            open(ev, "w").write("# placeholder planted by wall_d15.py\n")
        before = count(tree)
        script = os.path.join(tree, "tools/audit/prepare_baseline.sh")
        if perturb:
            s = open(script).read()
            assert KEEP_LINE in s, "keep line moved; re-derive the perturbation"
            i = s.index(KEEP_LINE)
            j = s.index("\n", s.index("\n", i) + 1) + 1  # after the two-line set comprehension
            s = s[:j] + KEEP_ADD + s[j:]
            open(script, "w").write(s)
        env = dict(os.environ, PYTHON=sys.executable)
        st = subprocess.run(["bash", script, "--strip", tree, "11"], capture_output=True, text=True, env=env)
        after = count(tree)
        print(f"strip rc={st.returncode} {st.stdout.strip()[-200:]} {st.stderr.strip()[-200:]}")
        print(f"RESULT bundles_in_config={len(bundles)}")
        print(f"RESULT before_strip_lines={before[0]} rc={before[1]}")
        print(f"RESULT after_strip_lines={after[0]} rc={after[1]} ({after[2]})")
        print(f"RESULT perturbed={int(perturb)}")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    pc, tc = time.process_time() - t0, time.thread_time() - tt0
    print(f"RESULT thread_factor={pc / tc if tc else 1.0:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    sw = -1
    for line in open("/proc/vmstat"):
        if line.startswith("pswpin"):
            sw = int(line.split()[1])
    print(f"RESULT swapins={sw}")


if __name__ == "__main__":
    main()
