#!/bin/sh
# Revision 4 (R4-1): each rule of alert_list.py's step 5 is pinned by its self-test.
# Writes one mutant per rule into a temporary directory and shows the self-test
# refusing it (a BAD row or a crash). Run from a checkout: sh measure/rev/alert_list_mutants.sh
set -u
src=measure/rev/alert_list.py
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
mutant() {  # $1 label, $2 old text, $3 new text
  python3 -I -c 'import sys; s=open(sys.argv[1]).read(); a, b = sys.argv[2], sys.argv[3]; assert s.count(a) == 1, a; open(sys.argv[4], "w").write(s.replace(a, b))' \
    "$src" "$2" "$3" "$tmp/al.py" || { echo "MUTANT NOT APPLIED: $1"; exit 1; }
  out=$(python3 -I "$tmp/al.py" self-test 2>&1); rc=$?
  echo "== $1: self-test rc $rc"
  printf '%s\n' "$out" | grep -E '^BAD|SELF-TEST|Error' | sed 's/^/   /'
  [ "$rc" -ne 0 ] || { echo "   NOT REFUSED"; exit 1; }
}
mutant "dismissed alerts not subtracted" 'if n not in dismissed | on_base]' 'if n not in on_base]'
mutant "base-open exclusion never applied" 'if base_repeats:' 'if False:'
mutant "a result without an alert number skipped" 'raise ReadFailed(f"analysis {ids[leg]} ({leg}): a result' 'continue  # (f"'
mutant "an unmatched leg not refused" 'if missing:' 'if False:'
mutant "the listing read by ref (the rejected reading)" 'if "by_ref" in ablate:' 'if True:'
echo "ALERT-LIST MUTANTS: every mutant refused"
