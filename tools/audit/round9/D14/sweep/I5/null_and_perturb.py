"""I5 sweep null control + perturbation, run against entity_counts.py as the
representative shape-checker (chosen because its three claims already mix a
hold and a defect at baseline, so both directions are visible in one file).

Null control: patch the one disagreeing claim (docs/configuration.md:196,
"All 74 entities") to the value the code constructs, and show
disagreeing_claims drops 1 -> 0 with no other claim moving.

Perturbation: with the doc fixed, re-introduce a one-line stale count
elsewhere (README.md:417, a claim that already holds) and show
disagreeing_claims moves 0 -> 1 again.

Command: python3 tools/audit/round9/D14/sweep/I5/null_and_perturb.py
Baseline 1936d5ca72a06556eeed4e8e5bf3dea520e517e1. Edits are made and reverted
in place inside this process; the working tree is unchanged on exit.
"""
import subprocess
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[6]
HARNESS = ["python3", "tools/audit/round9/D5/s1/entity_counts.py"]


def run():
    import os
    env = dict(os.environ)
    env["PYTHONPATH"] = "tests/hastub"
    p = subprocess.run(HARNESS, cwd=str(ROOT), env=env, capture_output=True, text=True, timeout=60)
    m = re.search(r"RESULT disagreeing_claims=(\d+)", p.stdout)
    return int(m.group(1)) if m else None


def main():
    cfg = ROOT / "docs/configuration.md"
    readme = ROOT / "README.md"
    cfg_orig = cfg.read_text()
    readme_orig = readme.read_text()
    try:
        baseline = run()
        print(f"RESULT baseline_disagreeing_claims={baseline} count")

        cfg.write_text(cfg_orig.replace("All 74 entities", "All 75 entities"))
        null_count = run()
        print(f"RESULT null_control_disagreeing_claims={null_count} count  (doc fixed to match code)")

        lines = readme_orig.splitlines(keepends=True)
        lines[416] = lines[416].replace("75", "80")  # README.md:417, 0-indexed
        readme.write_text("".join(lines))
        perturbed = run()
        print(f"RESULT perturbed_disagreeing_claims={perturbed} count  (one-line re-introduction elsewhere)")

        ok = baseline == 1 and null_count == 0 and perturbed == 1
        print(f"RESULT null_and_perturbation_ok={int(ok)} bool")
        if not ok:
            sys.exit(1)
    finally:
        cfg.write_text(cfg_orig)
        readme.write_text(readme_orig)


if __name__ == "__main__":
    main()
