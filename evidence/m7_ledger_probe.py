import os, subprocess, sys, tempfile
from pathlib import Path
tree = sys.argv[1]
STUB = ("#!/bin/sh\n" 'case "$1" in\n' "  -c) exit 0 ;;\n"
 "  -m) for a; do [ \"$prev\" = -o ] && echo '{}' > \"$a\"; " 'prev="$a"; done; exit 0 ;;\n'
 "  tests/closure.py)\n" '    [ "$2" = coverage-split ] || exit 0\n'
 "    n=0; while read -r s; do [ -n \"$s\" ] || continue\n"
 "      if [ $n = 0 ]; then printf 'reuse\\t%s\\n' \"$s\"; " "else printf 'measure\\t%s\\n' \"$s\"; fi; n=1; done; exit 0 ;;\n"
 "  tests/coverage_ratchet.py)\n" '    [ -n "$CTR_FLOOR_FAIL" ] && echo "  FAIL every module >= 95.0 %"' "\n    exit 0 ;;\n"
 '  *) echo "$1" >> "$CTR_RAN"; exit 0 ;;\n' "esac\n")
with tempfile.TemporaryDirectory() as td:
    d = Path(td); st = d/"py"; st.write_text(STUB); st.chmod(0o755)
    (d/"reuse").mkdir(); (d/"work").mkdir()
    env = {**os.environ, "PYTHON": str(st), "W5P_WORK": str(d/"work"), "W5P_SCOPE": str(d/"scope.json"),
           "W5P_REUSE": str(d/"reuse"), "W5P_LANES": "1", "HPO_CI_METRICS": str(d/"m.tsv"),
           "CTR_RAN": str(d/"ran"), "CTR_FLOOR_FAIL": "1"}
    r = subprocess.run(["bash","tools/coverage/coverage_tree.sh","fast"], cwd=tree, env=env, capture_output=True, text=True)
    print("rc", r.returncode)
    for f in sorted(d.rglob("scripts.tsv"))+sorted(d.rglob("provenance.tsv")):
        rows=f.read_text().splitlines()
        print(f.name, "rows", len(rows), "reused rows", sum("\treused" in x for x in rows))
    sm = sorted(d.rglob("scripts.tsv"))
    if sm:
        sys.path.insert(0, str(Path(tree)/"tests"))
        print(subprocess.run([sys.executable, "tests/closure.py", "coverage-summary", str(sm[0])], cwd=tree, capture_output=True, text=True, env={**os.environ,"PYTHONPATH":"tests/hastub"}).stdout.strip()[:80])
