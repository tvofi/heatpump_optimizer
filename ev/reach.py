# Runs tests/entities.py's R10/R11 N-log-flood block alone, verbatim, from a checkout's cwd.
#   reach.py <entities.py> [<entities.py whose _r11_logger_aliases replaces the first's>]
# Prints each R.check in the block as ok/FAIL with its detail.
import ast, re, subprocess, sys, tempfile
from pathlib import Path

src = open(sys.argv[1]).read()
if len(sys.argv) > 2:
    def seg(s):
        for n in ast.parse(s).body:
            if isinstance(n, ast.FunctionDef) and n.name == "_r11_logger_aliases":
                return ast.get_source_segment(s, n)
    src = src.replace(seg(src), seg(open(sys.argv[2]).read()))
lines = src.splitlines(keepends=True)
start = next(i for i, l in enumerate(lines) if l.startswith("from collections import Counter  # noqa: E402"))
end = next(i for i, l in enumerate(lines) if l.startswith("# THE RECORD JOB'S WINDOW CACHE"))


class R:
    @staticmethod
    def check(name, ok, detail=""):
        print(("ok  " if ok else "FAIL"), name[:70], "" if ok else f"[{detail}]"[:3000])


ns = {"ast": ast, "re": re, "subprocess": subprocess, "tempfile": tempfile, "Path": Path, "R": R, "__name__": "reach"}
exec(compile("".join(lines[start:end]), "entities-block", "exec"), ns)
print("verdict", ns["_r11_alias_verdict"](ns["_r11_aliases_found"]))
