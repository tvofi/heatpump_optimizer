#!/usr/bin/env bash
# The composed-closure byte-identity proof, self-sufficient arm (round-9 C1).
#
# Run by the `composed-proof` job when a pull request changes the composition
# machinery (tools/coverage/coverage_tree.sh, this file, tests/closure.py,
# tests/composed_closures.json, .github/workflows/tests.yml) -- the one head
# where the instrument itself is in doubt. The nightly arm compares the
# artifacts the nightly's own coverage and closures jobs produce on one tree;
# this arm owes its own recordings, because a pull request's closures job
# CONSUMES the composed record, so nothing else on a PR records bare.
#
# For every script on tests/composed_closures.json's allow-list, at this
# checkout, it measures three executions and refuses on any inequality:
#
#   bare      tests/closure.py record            (the closures lane: audit
#             hook + strace union)               hook + strace union)
#   composed  COVERAGE_PROCESS_START=... record  (the coverage lane's composed
#             run: tracer beside the hook)       run, exactly as
#                                             coverage_tree.sh invokes it)
#   traced    COVERAGE_PROCESS_START=... script  (yesterday's coverage lane:
#             only                              line set, no hook)
#
# Equality owed, per the pre-study's acceptance: the composed run's READ SET
# is byte-identical to the bare recording's (files and inert_reads,
# `closure.py composed-compare`), and its LINE SET is byte-identical to the
# traced-only run's (executed lines per file under custom_components/). rc 0
# under all three. Nothing is written inside the worktree.
set -uo pipefail
cd "$(dirname "$0")/../.."
PY="${PYTHON:-python3}"
export PYTHONPATH="$PWD/tests/hastub"
W=$(mktemp -d "${TMPDIR:-/tmp}/hpo-composed-proof-XXXXXX")
trap 'rm -rf "$W"' EXIT
mkdir -p "$W/site"
cat > "$W/site/sitecustomize.py" <<'EOF'
try:
    import coverage
except ImportError:
    pass
else:
    coverage.process_startup()
EOF
mk_rc() {  # $1 = rcfile path, $2 = data dir
  mkdir -p "$2"
  cat > "$1" <<RCEOF
[run]
parallel = True
relative_files = True
data_file = $2/.coverage
source = $PWD/custom_components/heatpump_optimizer
RCEOF
}
export PYTHONPATH="$W/site:$PYTHONPATH"
export COVERAGE_PROCESS_START=
failed=0
for s in $("$PY" tests/closure.py composed-list); do
  base=$(basename "$s")
  echo "=== proving $s ==="
  mk_rc "$W/rc-compose" "$W/data/composed"
  mk_rc "$W/rc-trace" "$W/data/traced"
  # 1. bare: exactly what the closures job's lane records.
  "$PY" tests/closure.py record "$s" --out-dir "$W/bare" \
    > "$W/$base.bare.log" 2>&1
  bare_rc=$?
  # 2. composed: the coverage lane's invocation, tracer beside the hook.
  COVERAGE_PROCESS_START="$W/rc-compose" "$PY" tests/closure.py record "$s" \
    --out-dir "$W/composed" > "$W/$base.composed.log" 2>&1
  composed_rc=$?
  # 3. traced-only: the coverage lane as it was before composition.
  COVERAGE_PROCESS_START="$W/rc-trace" "$PY" "$s" > "$W/$base.traced.log" 2>&1
  traced_rc=$?
  echo "rc: bare=$bare_rc composed=$composed_rc traced=$traced_rc"
  if [ "$bare_rc" -ne 0 ] || [ "$composed_rc" -ne 0 ] || [ "$traced_rc" -ne 0 ]; then
    echo "composed-proof: $s: equality is proven only for runs that ended (rc 0 under all three)"
    failed=1
  fi
  "$PY" tests/closure.py composed-compare \
    --composed-dir "$W/composed" --bare-dir "$W/bare" || failed=1
  COVERAGE_PROCESS_START= "$PY" -m coverage combine --rcfile="$W/rc-compose" \
    --keep >> "$W/combine.log" 2>&1
  COVERAGE_PROCESS_START= "$PY" -m coverage combine --rcfile="$W/rc-trace" \
    --keep >> "$W/combine.log" 2>&1
  COVERAGE_PROCESS_START= "$PY" -m coverage json --rcfile="$W/rc-compose" \
    -o "$W/composed.json" >> "$W/combine.log" 2>&1
  COVERAGE_PROCESS_START= "$PY" -m coverage json --rcfile="$W/rc-trace" \
    -o "$W/traced.json" >> "$W/combine.log" 2>&1
  if ! "$PY" - "$W" "$s" <<'EOF'
import json, sys
from pathlib import Path
w, script = Path(sys.argv[1]), sys.argv[2]
def lines(p):
    d = json.loads(p.read_text())
    return {f: frozenset(v["executed_lines"]) for f, v in d["files"].items()}
a, b = lines(w / "composed.json"), lines(w / "traced.json")
diff = sorted(f for f in set(a) | set(b) if a.get(f) != b.get(f))
if diff:
    print(f"composed-proof: {script}: the composed line set differs from "
          f"the traced-only line set in {len(diff)} file(s):")
    for f in diff[:6]:
        only_c = sorted(a.get(f, frozenset()) - b.get(f, frozenset()))
        only_t = sorted(b.get(f, frozenset()) - a.get(f, frozenset()))
        print(f"  {f}: composed-only {only_c[:8]} traced-only {only_t[:8]}")
    sys.exit(1)
print(f"composed-proof: {script}: line sets byte-identical over "
      f"{len(a)} file(s)")
EOF
  then
    failed=1
  fi
done
if [ "$failed" -ne 0 ]; then
  echo "composed-proof: an equality broke; remove the script from tests/composed_closures.json until it is proven"
  exit 1
fi
echo "composed-proof: every allow-listed script proven at this head"
