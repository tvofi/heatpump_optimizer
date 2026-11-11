"""The .gitignore `config/` rule is anchored to the repository root.

An unanchored `config/` ignores a directory of that name at any depth, so
`git add` of a tracked file under dev/audit/config/ or dev/governance/config/
exits 1 (and `git add -A` skips a new file there): a handoff silently omits it.
The local Home Assistant runtime directory is the root-level one only.

Run: python tests/gitignore_config.py
"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def ignored(path: str) -> bool:
    r = subprocess.run(["git", "check-ignore", "-q", "--no-index", path],
                       cwd=ROOT, capture_output=True)
    return r.returncode == 0


fails = []
# Null control: the root-level runtime directory stays ignored.
if not ignored("config/x"):
    fails.append("root-level config/x is no longer ignored")
for nested in ("dev/audit/config/x", "dev/governance/config/x"):
    if ignored(nested):
        fails.append(f"{nested} is ignored by .gitignore")
if fails:
    print("FAIL gitignore_config:", *fails, sep="\n  ")
    sys.exit(1)
print("ok gitignore_config: /config/ ignored, nested config/ dirs visible")
