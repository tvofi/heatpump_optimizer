#!/bin/sh
# Round-9: apply prepare_baseline.sh strip_earlier_rounds (verbatim logic @1936d5ca) to one tree. Usage: sh r9-strip-rounds.sh <tree> [python]
T="${1:?tree}"; PY="${2:-python3}"; ROUND=9
"$PY" - "$T" "$ROUND" <<'PY'
import json, re, sys
from pathlib import Path
root, cur = Path(sys.argv[1]), f"round{sys.argv[2]}"
rounds = sorted(d for d in (root / "tools/audit").glob("round*") if d.is_dir() and d.name != cur)
keep = {f for fs in json.loads((root / "tests/closures.json").read_text())["closures"].values()
        for f in fs if f.startswith("tools/audit/round")}
lit = re.compile(r"tools/audit/round[A-Za-z0-9_.-]*(?:/[A-Za-z0-9_.-]+)*")
for t in sorted(p for g in ("*.py", "*.mjs", "*.sh") for p in (root / "tests").glob(g)):
    for m in lit.findall(t.read_text(errors="replace")):
        p = root / m.rstrip("/.")
        if p.is_file():
            keep.add(p.relative_to(root).as_posix())
        elif p.is_dir() and len(p.relative_to(root).parts) > 3:
            keep.update(f.relative_to(root).as_posix() for f in p.rglob("*") if f.is_file())
removed = kept = 0
for d in rounds:
    for f in sorted(d.rglob("*")):
        if f.is_file() or f.is_symlink():
            if f.relative_to(root).as_posix() in keep:
                kept += 1
            else:
                f.unlink()
                removed += 1
    for sub in sorted((d, *(p for p in d.rglob("*") if p.is_dir())), key=lambda p: -len(p.parts)):
        if not any(sub.iterdir()):
            sub.rmdir()
print(f"RESULT stripped_earlier_rounds={len(rounds)} files_removed={removed} files_kept={kept} dir={root}")
PY
