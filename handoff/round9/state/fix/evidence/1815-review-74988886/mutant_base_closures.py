import json
import subprocess
import sys

sys.path.insert(0, "tests")
import closure

files = closure.changed_files("e4eda221")
print("changed", files)
real = closure.select(files, closure.base_closures("e4eda221"))
print("real   ", real["mode"], real["run"])


def mut_head(diff_ref):
    shown = subprocess.run(
        ["git", "show", "HEAD:tests/closures.json"],
        cwd=closure.ROOT,
        capture_output=True,
        text=True,
    )
    return json.loads(shown.stdout)["closures"]


m = closure.select(files, mut_head("e4eda221"))
print("mutantH", m["mode"], m["run"])


def mut_ref(diff_ref):  # diff_ref itself instead of merge base
    shown = subprocess.run(
        ["git", "show", f"{diff_ref}:tests/closures.json"],
        cwd=closure.ROOT,
        capture_output=True,
        text=True,
    )
    return json.loads(shown.stdout)["closures"]


m = closure.select(files, mut_ref("e4eda221"))
print("mutantR", m["mode"], m["run"])
