# Reviewer's own probe (F10.9c review): a PR touching only DISCLAIMER.md (INERT)
# and a main change deleting a file it links; merge_fastpath.decide says ELIGIBLE,
# claims.py (run by run_always tests/harness_headers.py) passes on each side and
# fails on the merged tree. Run from a worktree at the PR head.
set -u
F=tools/audit/README.md
LINK="See also [the audit README]($F)."
claims() { PYTHONPATH=tests/hastub python3 tools/audit/round4/D6/claims.py 2>&1 | grep -E '^RESULT claims_(true|false)='; }
python3 - "$F" <<'PY'
import sys, json, pathlib
sys.path.insert(0, "tools/audit"); sys.path.insert(0, "tests")
import merge_fastpath as m
t = json.loads(pathlib.Path("tests/closures.json").read_text())
wf = [p.read_text() for p in sorted(pathlib.Path(".github/workflows").glob("*.yml"))]
r = m.decide(["DISCLAIMER.md"], [sys.argv[1]], {"main": t, "head": t}, m.grader_specs(wf), None)
print("decide(pr=[DISCLAIMER.md], main=[%s]) ->" % sys.argv[1], r or "ELIGIBLE")
PY
echo "== PR side (link added, file present)"; echo "$LINK" >> DISCLAIMER.md; claims
echo "== merged (link added, file deleted)"; mv $F /tmp/_f.md; claims
echo "== main side (file deleted, no link)"; git checkout -q -- DISCLAIMER.md; claims
mv /tmp/_f.md $F; git status --short
