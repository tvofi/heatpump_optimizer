#!/bin/bash
# Replay a merged PR's fast-gate selection under the branch's closure.py, against
# the selection the PR's own tree made. Usage: replay_select.sh <closure.py> <pr> <head> <base>
set -eu
NEW=$1; PR=$2; H=$3; B=$4; W=$(mktemp -d)/pr-$PR
git worktree add -q "$W" "$H"
(cd "$W" && python3 tests/closure.py select --diff "$B" --json > "$W.old.json")
python3 - "$NEW" "$W" "$B" "$PR" <<'PY'
import sys, json, os, importlib.util
from pathlib import Path
new, w, b, pr = sys.argv[1:]
spec = importlib.util.spec_from_file_location("closure_new", new); c = importlib.util.module_from_spec(spec); spec.loader.exec_module(c)
c.ROOT = Path(w); c.CLOSURES = c.ROOT / "tests" / "closures.json"; os.chdir(w)
n = c.select(sorted(set(c.changed_files(b))), c.base_closures(b))
o = json.load(open(w + ".old.json"))
print(f"#{pr} old: {o['mode']} {len(o['run'])} | new: {n['mode']} {len(n['run'])}, entries moved {len(n.get('entry_changed', []))}")
print("   old ran, new skips:", sorted(set(o["run"]) - set(n["run"])))
PY
git worktree remove --force "$W"
