# covtrust.py: tests.yml's coverage staging and covtrust steps run as entities.py's check runs them,
# for the push run's own marker; prints each step's rc, stderr tail, the marker and the output.
import os, subprocess, tempfile, yaml
from pathlib import Path

job = yaml.safe_load(open(".github/workflows/tests.yml"))["jobs"]["coverage"]
by = {str(s.get("id") or s.get("name")): s for s in job["steps"]}
check, stage = by["covtrust"]["run"], by["Stage this commit's per-script coverage"]["run"]
head = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
with tempfile.TemporaryDirectory() as t:
    t = Path(t); (t / "w" / "out" / "per").mkdir(parents=True)
    p = subprocess.run(["bash", "-e", "-c", stage], capture_output=True, text=True,
                       env={**os.environ, "RUNNER_TEMP": str(t), "W5P_WORK": str(t / "w"),
                            "GITHUB_EVENT_NAME": "push", "GITHUB_REF": "refs/heads/main"})
    m = t / "coverage-base" / ".measured-by"
    marker = m.read_text() if m.exists() else None
    print("stage rc", p.returncode, "stderr", p.stderr[-400:], "marker", repr(marker))
with tempfile.TemporaryDirectory() as t:
    t = Path(t); (t / "coverage-base").mkdir()
    (t / "coverage-base" / ".measured-by").write_text(marker or "")
    (t / "out").write_text("")
    p = subprocess.run(["bash", "-e", "-c", check], capture_output=True, text=True,
                       env={**os.environ, "RUNNER_TEMP": str(t), "BASE": head, "GITHUB_OUTPUT": str(t / "out")})
    print("check rc", p.returncode, "stdout", p.stdout[-300:], "stderr", p.stderr[-400:],
          "out", repr((t / "out").read_text()), "kept", (t / "coverage-base").exists())
print("check step:\n" + check)
