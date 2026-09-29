#!/usr/bin/env python3
"""Measure the full vector on every planted case: A1's 30 perturbations and A3's 22 control/fix/null arms.

    python3 measure_planted.py [--repo /home/user/heatpump_optimizer]

One detached worktree (wt-planted/) at 7952d8f9, reset between cases. Labels:
A1 G* GOOD, B* BAD, N* NULL; A3 control BAD (adds one instance of a defect shape), fix GOOD
(removes one), null NULL. An A3 fix with fix_on == "control" is measured against the
control's vector, not the baseline. Output: planted/<case>.json {label, base, vec, src}.
"""
import json, subprocess, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
A1 = HERE.parent / "a1"
A3 = HERE.parent / "a3"
REPO = "/home/user/heatpump_optimizer"
BASE = "7952d8f9"
WT = HERE / "wt-planted"
OUT = HERE / "planted"
OUT.mkdir(exist_ok=True)


def git(*a, cwd=REPO):
    return subprocess.run(["git", "-C", str(cwd), *a], capture_output=True, text=True, check=True).stdout


def reset():
    git("checkout", "-q", "-f", BASE, cwd=WT)
    git("clean", "-qfdx", "custom_components", "tests", cwd=WT)


def vec():
    r = subprocess.run([sys.executable, str(HERE / "measure_vec.py"), str(WT)], capture_output=True, text=True, check=True)
    return json.loads(r.stdout)


def main():
    if not WT.exists():
        git("worktree", "add", "--detach", str(WT), BASE)
    try:
        reset()
        base = vec()
        (OUT / "_base.json").write_text(json.dumps(base, sort_keys=True))
        for p in sorted((A1 / "perturb").glob("[GBN]*.py")):
            name = p.stem
            reset()
            subprocess.run([sys.executable, str(p), str(WT)], check=True, capture_output=True)
            lab = {"G": "GOOD", "B": "BAD", "N": "NULL"}[name[0]]
            (OUT / f"a1_{name}.json").write_text(json.dumps(
                {"label": lab, "base": "_base", "vec": vec(), "src": f"a1/perturb/{name}.py"}, sort_keys=True))
            print(name, lab, flush=True)
        sys.path.insert(0, str(A3))
        import controls
        for metric, arms in controls.plan().items():
            ctrl_vec = None
            for arm, lab in (("control", "BAD"), ("control_write", "BAD"), ("fix", "GOOD"), ("null", "NULL")):
                if arm not in arms:
                    continue
                reset()
                base_name = "_base"
                if arm == "fix" and arms.get("fix_on") == "control":
                    arms["control"][1](WT)
                    base_name = f"a3_{metric}_control"
                arms[arm][1](WT)
                v = vec()
                (OUT / f"a3_{metric}_{arm}.json").write_text(json.dumps(
                    {"label": lab, "base": base_name, "vec": v, "src": f"a3/controls.py {metric}.{arm}: {arms[arm][0]}"},
                    sort_keys=True))
                print(metric, arm, lab, flush=True)
    finally:
        git("worktree", "remove", "--force", str(WT))
    return 0


if __name__ == "__main__":
    sys.exit(main())
