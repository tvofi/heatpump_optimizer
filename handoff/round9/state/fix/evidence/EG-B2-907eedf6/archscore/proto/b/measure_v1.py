#!/usr/bin/env python3
"""Add the v1 metrics (metrics_v1.py) to every measured tree: corpus + trajectory (vec1/<sha12>.json)
and planted (planted1/<case>.json). Same trees, same order as measure_corpus.py / measure_planted.py.

    python3 measure_v1.py corpus|planted
"""
import json, subprocess, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = "/home/user/heatpump_optimizer"
BASE = "7952d8f9"


def git(*a, cwd=REPO):
    return subprocess.run(["git", "-C", str(cwd), *a], capture_output=True, text=True, check=True).stdout


def m(wt):
    r = subprocess.run([sys.executable, str(HERE / "metrics_v1.py"), str(wt)], capture_output=True, text=True)
    return json.loads(r.stdout) if r.returncode == 0 else {"_v1_error": r.stderr[-400:]}


def corpus():
    wt = HERE / "wt-v1c"
    out = HERE / "vec1"
    out.mkdir(exist_ok=True)
    shas = sorted(p.stem for p in (HERE / "vec").glob("*.json"))
    if not wt.exists():
        git("worktree", "add", "--detach", str(wt), BASE)
    try:
        for i, s in enumerate(shas):
            if (out / f"{s}.json").exists():
                continue
            git("checkout", "-q", "--detach", "--force", s, cwd=wt)
            git("clean", "-qfdx", cwd=wt)
            (out / f"{s}.json").write_text(json.dumps(m(wt), sort_keys=True))
            print(i, len(shas), s, flush=True)
    finally:
        git("worktree", "remove", "--force", str(wt))


def planted():
    sys.path.insert(0, str(HERE.parent / "a3"))
    import controls
    wt = HERE / "wt-v1p"
    out = HERE / "planted1"
    out.mkdir(exist_ok=True)
    if not wt.exists():
        git("worktree", "add", "--detach", str(wt), BASE)

    def reset():
        git("checkout", "-q", "-f", BASE, cwd=wt)
        git("clean", "-qfdx", "custom_components", "tests", cwd=wt)
    try:
        reset()
        (out / "_base.json").write_text(json.dumps(m(wt), sort_keys=True))
        for p in sorted((HERE.parent / "a1" / "perturb").glob("[GBN]*.py")):
            reset()
            subprocess.run([sys.executable, str(p), str(wt)], check=True, capture_output=True)
            (out / f"a1_{p.stem}.json").write_text(json.dumps(m(wt), sort_keys=True))
            print(p.stem, flush=True)
        for metric, arms in controls.plan().items():
            for arm in ("control", "control_write", "fix", "null"):
                if arm not in arms:
                    continue
                reset()
                if arm == "fix" and arms.get("fix_on") == "control":
                    arms["control"][1](wt)
                arms[arm][1](wt)
                (out / f"a3_{metric}_{arm}.json").write_text(json.dumps(m(wt), sort_keys=True))
                print(metric, arm, flush=True)
    finally:
        git("worktree", "remove", "--force", str(wt))


if __name__ == "__main__":
    {"corpus": corpus, "planted": planted}[sys.argv[1]]()
