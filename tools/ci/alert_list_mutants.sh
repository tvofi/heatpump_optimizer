#!/bin/sh
# Each rule of alert_list.py is pinned by its self-test: one mutant per rule, written to a
# temporary directory, and the self-test must refuse it (a BAD row or a crash).
# Run from a checkout: sh tools/ci/alert_list_mutants.sh
set -u
src=tools/ci/alert_list.py
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
python3 -I "$src" --self-test >/dev/null || { echo "BASELINE RED: the unmutated self-test fails"; exit 1; }
mutant() {  # $1 label, $2 old text, $3 new text
  python3 -I -c 'import sys; s=open(sys.argv[1]).read(); a, b = sys.argv[2], sys.argv[3]; assert s.count(a) == 1, a; open(sys.argv[4], "w").write(s.replace(a, b))' \
    "$src" "$2" "$3" "$tmp/al.py" || { echo "MUTANT NOT APPLIED: $1"; exit 1; }
  out=$(python3 -I "$tmp/al.py" --self-test 2>&1); rc=$?
  echo "== $1: self-test rc $rc"
  printf '%s\n' "$out" | grep -E '^BAD|self-test:|Error' | sed 's/^/   /'
  [ "$rc" -ne 0 ] || { echo "   NOT REFUSED"; exit 1; }
}
mutant "alert-level dismissed read skipped (N5-2)" 'if alert.get("state") != "dismissed":' 'if True:'
mutant "base-open exclusion never applied" 'if base_repeats:' 'if False:'
mutant "a result without an alert number skipped" 'raise ReadFailed(f"analysis {ids[leg]} ({leg}): a result' 'continue  # (f"'
mutant "an unmatched leg not refused" 'if missing:' 'if False:'
mutant "sort and direction left unpinned (N5-3)" '"tool_name": "CodeQL", **PINS}' '"tool_name": "CodeQL"}'
mutant "SARIF read without its Accept header" 'headers={"Accept": ACCEPT_SARIF})' 'headers=None)'
mutant "RateLimited swallowed as a failed read" 'except ReadFailed as e:
        return False, f"FAIL' 'except Exception as e:
        return False, f"FAIL'
mutant "a failed alert read tolerated" 'f"alert {n}")' 'f"alert {n}") if False else {}'
echo "ALERT-LIST MUTANTS: every mutant refused"
