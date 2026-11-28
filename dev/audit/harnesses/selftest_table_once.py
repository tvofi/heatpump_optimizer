#!/usr/bin/env python3
"""R11-SELFTEST-SCOPE-P3: does the self-test table's generator write each read once?

    python3 dev/audit/harnesses/selftest_table_once.py TABLE_COMMIT [MODULE_COMMIT]

Drives the record path of `tools/ci/selftest_scope.py` as MODULE_COMMIT has it
(default HEAD): over the table committed at TABLE_COMMIT, every step's `D/**`
probe is re-measured as D's tracked files one by one (a trace probes files,
never a directory whole), unioned over the committed entry by `union_entry`,
and written by `write_table` against TABLE_COMMIT's tracked tree, in a detached
worktree. Prints the number of items the written table lists more than once.
Main's table at 33b1e089 held 13 such items (#3551 removed them by its union).
"""
import importlib.util
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
MODULE = "tools/ci/selftest_scope.py"


def git(*args: str, cwd: Path = ROOT) -> str:
    return subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True, text=True).stdout


def doubled(table_rev: str, module_rev: str) -> int:
    with tempfile.TemporaryDirectory() as d:
        wt = Path(d) / "wt"
        git("worktree", "add", "-q", "--detach", str(wt), table_rev)
        try:
            (Path(d) / "m.py").write_text(git("show", f"{module_rev}:{MODULE}"))
            spec = importlib.util.spec_from_file_location("selftest_scope_at_rev", Path(d) / "m.py")
            m = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(m)
            table = m.parse_table(git("show", f"{table_rev}:{m.TABLE}"))
            tracked, _ = m._tracked(wt)
            entries = {}
            for sid, e in table["steps"].items():
                e = {k: (sorted(set(v)) if isinstance(v, list) else v) for k, v in e.items()}
                whole = [p[:-3] for p in e.get("probes", ()) if p.endswith("/**")]
                measured = {**e, "probes": sorted(f for f in tracked for w in whole if f.startswith(w + "/"))}
                entries[sid] = m.union_entry(e, measured)
            out = Path(d) / "table.json"
            m.write_table(out, entries, wt)
            steps = json.loads(out.read_text())["steps"]
            return sum(len(v) - len(set(v)) for e in steps.values() for v in e.values() if isinstance(v, list))
        finally:
            git("worktree", "remove", "--force", str(wt))


def main(argv: list[str]) -> int:
    if not 1 <= len(argv) <= 2:
        print(__doc__, file=sys.stderr)
        return 2
    table_rev, module_rev = argv[0], argv[1] if len(argv) > 1 else "HEAD"
    print(f"table {table_rev}, module {module_rev}: RESULT doubled={doubled(table_rev, module_rev)}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
