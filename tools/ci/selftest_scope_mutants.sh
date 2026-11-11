#!/bin/sh
# Each trace-completeness rule of selftest_scope.py and each tracing rule of
# selftest_step.sh is pinned by selftest_scope.py's self-test: one mutant per
# rule, written to a temporary directory, and the self-test must refuse it
# (R10-HOTFIX-SELFTEST-SCOPE-HANG). A selftest_scope.py mutant runs as the real
# path's source, so its ROOT is the checkout; a wrapper mutant is handed to the
# unmutated self-test through --wrapper.
# Run from a checkout: sh tools/ci/selftest_scope_mutants.sh [--self-test]. The
# flag only names the run for selftest_wiring.py's rule; there is no other mode.
set -u
src=tools/ci/selftest_scope.py
wrapper=tools/ci/selftest_step.sh
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
python3 -I "$src" --self-test > /dev/null || { echo "BASELINE RED: the unmutated self-test fails"; exit 1; }
apply() { # <file> <old> <new> <out>: the file with old, present once, replaced by new
  python3 -I -c 'import sys; s=open(sys.argv[1]).read(); a, b = sys.argv[2], sys.argv[3]; assert s.count(a) == 1, a; open(sys.argv[4], "w").write(s.replace(a, b))' \
    "$1" "$2" "$3" "$4"
}
report() { # <label> <rc> <output>
  echo "== $1: self-test rc $2"
  printf '%s\n' "$3" | grep -E '^  FAIL|self-test:|Error' | sed 's/^/   /'
  [ "$2" -ne 0 ] || { echo "   NOT REFUSED"; exit 1; }
}
scope_mutant() { # <label> <old> <new>
  apply "$src" "$2" "$3" "$tmp/s.py" || { echo "MUTANT NOT APPLIED: $1"; exit 1; }
  out=$(python3 -I -c 'import sys; f, real = sys.argv[1], sys.argv[2]; sys.argv = [real, "--self-test"]; exec(compile(open(f).read(), real, "exec"), {"__name__": "__main__", "__file__": real})' \
    "$tmp/s.py" "$PWD/$src" 2>&1); rc=$?
  report "$1" "$rc" "$out"
}
wrapper_mutant() { # <label> <old> <new>
  apply "$wrapper" "$2" "$3" "$tmp/step.sh" || { echo "MUTANT NOT APPLIED: $1"; exit 1; }
  out=$(python3 -I "$src" --self-test --wrapper "$tmp/step.sh" 2>&1); rc=$?
  report "$1" "$rc" "$out"
}
scope_mutant "a missing bg trace skipped" 'broken.append(f"MISSING trace' 'None and broken.append(f"MISSING trace'
scope_mutant "an empty trace read whole" 'return "EMPTY"' 'return ""'
scope_mutant "a partial trace read whole" 'return "" if seen["root"] in seen["ended"] else "PARTIAL"' 'return ""'
scope_mutant "a signal death read as partial" '(?:exited with|killed by) ' '(?:exited with) '
scope_mutant "check drops the trace refusals" 'refuse = broken + refuse' 'refuse = refuse'
scope_mutant "record passes over a broken trace" 'return 1 if failed or broken else 0' 'return 1 if failed else 0'
wrapper_mutant "only launch untraced (the incident's wrapper)" 'case "$UNTRACED" in *" ${GITHUB_ACTION:-} "*)' 'case " launch " in *" ${GITHUB_ACTION:-} "*)'
wrapper_mutant "no strace exec'd anyway" 'if ! command -v strace > /dev/null 2>&1; then' 'if false; then'
wrapper_mutant "exit lines suppressed (-qq)" 'exec strace -f -q -y' 'exec strace -f -qq -y'
wrapper_mutant "drift traced again" 'UNTRACED=" scope strace launch drift unread "' 'UNTRACED=" scope strace launch unread "'
echo "SELFTEST-SCOPE MUTANTS: every mutant refused"
