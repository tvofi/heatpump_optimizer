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
workflow=.github/workflows/governance.yml
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
python3 -I "$src" --self-test > /dev/null || { echo "BASELINE RED: the unmutated self-test fails"; exit 1; }
apply() { # <file> <old> <new> <out>: the file with old, present once, replaced by new
  python3 -I -c 'import sys; s=open(sys.argv[1]).read(); a, b = sys.argv[2], sys.argv[3]; assert s.count(a) == 1, a; open(sys.argv[4], "w").write(s.replace(a, b))' \
    "$1" "$2" "$3" "$4"
}
# The mutants run JOBS at a time (55 runs of a self-test that waits more than
# it computes: in line they outlast the step replay of tools/pr/ci_predict.py
# and a third of the job's own timeout); each writes its report to a file of
# its own and the reports are printed in order once all have ended. Four to a
# processor: a run computes for about a quarter of the time it takes, and one
# to a processor still outlasted that replay on a seat slower than the one it
# was timed on.
JOBS=${SELFTEST_MUTANT_JOBS:-$(($(getconf _NPROCESSORS_ONLN 2>/dev/null || echo 2) * 4))}
n=0
report() { # <label> <rc> <output>
  echo "== $1: self-test rc $2"
  printf '%s\n' "$3" | grep -E '^  FAIL|self-test:|Error' | sed 's/^/   /'
  [ "$2" -ne 0 ] || echo "   NOT REFUSED"
}
spawn() { # <kind> <label> <old> <new>: one mutant, in the background
  n=$((n + 1))
  ( k=$(printf '%03d' "$n")
    case "$1" in
      scope)
        if apply "$src" "$3" "$4" "$tmp/s.$k.py" 2> /dev/null; then
          out=$(python3 -I -c 'import sys; f, real = sys.argv[1], sys.argv[2]; sys.argv = [real, "--self-test"]; exec(compile(open(f).read(), real, "exec"), {"__name__": "__main__", "__file__": real})' \
            "$tmp/s.$k.py" "$PWD/$src" 2>&1); rc=$?
          report "$2" "$rc" "$out"
        else echo "MUTANT NOT APPLIED: $2"; fi ;;
      wrapper)
        if apply "$wrapper" "$3" "$4" "$tmp/step.$k.sh" 2> /dev/null; then
          out=$(python3 -I "$src" --self-test --wrapper "$tmp/step.$k.sh" 2>&1); rc=$?
          report "$2" "$rc" "$out"
        else echo "MUTANT NOT APPLIED: $2"; fi ;;
      workflow)
        if apply "$workflow" "$3" "$4" "$tmp/wf.$k.yml" 2> /dev/null; then
          out=$(python3 -I "$src" --self-test --workflow "$tmp/wf.$k.yml" 2>&1); rc=$?
          report "$2" "$rc" "$out"
        else echo "MUTANT NOT APPLIED: $2"; fi ;;
    esac > "$tmp/r.$k" 2>&1 ) &
  [ $((n % JOBS)) -ne 0 ] || wait
}
scope_mutant() { spawn scope "$@"; }       # <label> <old> <new>
wrapper_mutant() { spawn wrapper "$@"; }
workflow_mutant() { spawn workflow "$@"; }
scope_mutant "a missing bg trace skipped" 'broken.append(f"MISSING trace' 'None and broken.append(f"MISSING trace'
scope_mutant "an empty trace read whole" 'return "EMPTY"' 'return ""'
scope_mutant "a partial trace read whole" 'return "" if seen["root"] in seen["ended"] else "PARTIAL"' 'return ""'
scope_mutant "a signal death read as partial" '(?:exited with|killed by) ' '(?:exited with) '
scope_mutant "check drops the trace refusals" 'refuse = broken + refuse' 'refuse = refuse'
scope_mutant "record passes over a broken trace" 'return 1 if failed or broken else 0' 'return 1 if failed else 0'
scope_mutant "settle never rewrites the index" '["git", "update-index", "-q", "--really-refresh", "--force-write-index"]' '["true"]'
scope_mutant "the settle command a no-op" 'return settle_index(root)' 'return 0'
scope_mutant "settle_gaps reads no job" 'if any(s.id in UNGATED and SETTLE_CALL.search' 'if True or any(s.id in UNGATED and SETTLE_CALL.search'
scope_mutant "static skips the settle check" 'problems = wiring_gaps(steps) + settle_gaps(steps)' 'problems = wiring_gaps(steps)'
scope_mutant "record replaces the committed entry again" 'entries[sid] = union_entry(entries.get(sid), m)' 'entries[sid] = m'
scope_mutant "record keeps a step the workflow no longer gates" 'return {k: v for k, v in entries.items() if k in gated}' 'return entries'
scope_mutant "prune clears a flag the entry does not set" 'if kind in FLAG_KINDS and not item and entries[step].get(kind):' 'if kind in FLAG_KINDS and not item:'
scope_mutant "prune drops a list item the entry does not hold" 'elif kind in LIST_KINDS and item in entries[step].get(kind, ()):' 'elif kind in LIST_KINDS:'
scope_mutant "prune writes nothing" 'write_table(root / TABLE, entries, root)
        return 0' 'return 0'
scope_mutant "prune accepts an unknown drop" '        if unknown:
            print(f"selftest_scope: not in the table' '        if False:
            print(f"selftest_scope: not in the table'
scope_mutant "check --write writes the bare measurement" 'write_table(write, union_entries(table, measured), root)' 'write_table(write, measured, root)'
scope_mutant "the union drops a committed list entry" 'sorted(set(old.get(k, ())) | set(new.get(k, ())))' 'sorted(set(new.get(k, ())))'
scope_mutant "the union drops a committed flag" 'bool(old.get(k)) or bool(new.get(k))' 'bool(new.get(k))'
scope_mutant "drift refuses a probe the run's own listed dir answers" 'a in dirs or a in set(m["dirs"])' 'a in dirs'
workflow_mutant "CI never settles the index" 'python3 -I tools/ci/selftest_scope.py settle' 'true'
workflow_mutant "CI swallows a failed settle" 'python3 -I tools/ci/selftest_scope.py settle' 'python3 -I tools/ci/selftest_scope.py settle || true'
wrapper_mutant "only launch untraced (the incident's wrapper)" 'case "$UNTRACED" in *" ${GITHUB_ACTION:-} "*)' 'case " launch " in *" ${GITHUB_ACTION:-} "*)'
wrapper_mutant "no strace exec'd anyway" 'if ! command -v strace > /dev/null 2>&1; then' 'if false; then'
wrapper_mutant "exit lines suppressed (-qq)" 'exec strace -f -q -y' 'exec strace -f -qq -y'
wrapper_mutant "drift traced again" 'UNTRACED=" scope strace launch drift absorb unread "' 'UNTRACED=" scope strace launch absorb unread "'
scope_mutant "prune goes on over an unreadable table" '        if table is None:
            print(f"selftest_scope: UNREADABLE {TABLE}", file=sys.stderr)
            return 1
        entries, unknown' '        if False:
            print(f"selftest_scope: UNREADABLE {TABLE}", file=sys.stderr)
            return 1
        entries, unknown'
scope_mutant "record traces in the seat's own checkout" 'tree = scratch_clone(root, tmp / "tree", rev)' 'tree = root'
scope_mutant "the scratch clone keeps no working-tree change" '    for rel in sorted({r for r in listed.split("\0") if r}):' '    for rel in ():'
scope_mutant "the scratch clone skips a staged file" 'listed += "" if rev else git("diff", "--cached"' 'listed += "" if True else git("diff", "--cached"'
scope_mutant "trace_steps traces over an unsettled index" 'if settle_index(tree):' 'if False:'
scope_mutant "an undecorated path resolved against the instrument's own checkout" 'path = os.path.join(base or str(root), raw)' 'path = os.path.join(base or str(ROOT), raw)'
scope_mutant "absorb carries a step recorded under another run text" 'if live.get(sid) != got.get("run_sha"):' 'if sid not in live:'
scope_mutant "absorb carries a read that names nothing at this head" 'if here(k, x)] for k in LIST_KINDS' 'if True] for k in LIST_KINDS'
scope_mutant "absorb carries a probe that is ignored or retired" 'probe_path(item, tracked_dirs) and item not in gone' 'probe_path(item, tracked_dirs)'
scope_mutant "absorb rewrites a table it added nothing to" '    if added:
        write_table(out, entries, root)' '    if True:
        write_table(out, entries, root)'
scope_mutant "absorb goes on over an unreadable source" 'if table is None or None in loaded:' 'if table is None:'
scope_mutant "absorb writes the live table over --out" 'return absorb_cli([Path(argv[k + 1]) for k, a in enumerate(argv) if a == "--from"], out.resolve(), root)' 'return absorb_cli([Path(argv[k + 1]) for k, a in enumerate(argv) if a == "--from"], root / TABLE, root)'
scope_mutant "touched_steps passes over a changed script" 'or any(named(p, text[s.id]) for _, p in changes))]' 'or False)]'
scope_mutant "touched_steps takes any path a script name contains or ends" 'rf"(?<![\w./-]){re.escape(path)}(?![\w./-])"' 're.escape(path)'
scope_mutant "touched_steps forgets what a waiter launcher starts" 'for line in launch.splitlines() for n in s.waits_on()' 'for line in () for n in s.waits_on()'
scope_mutant "touched_steps passes over a step recorded under another run text" '(held.get(s.id) or {}).get("run_sha") != s.run_sha' 's.id not in held'
scope_mutant "precheck grades no drift" '    refuse = drift(table, measured, steps, set(want))[0]
    shared = ' '    refuse = []
    shared = '
scope_mutant "precheck charges the branch main's own drift" 'refuse = broken + [r for r in refuse if r not in shared]' 'refuse = broken + refuse'
scope_mutant "precheck traces the merge base once for each refusal" 'refuse = broken + [r for r in refuse if r not in shared]' 'refuse = broken + [r for r in refuse if r not in base_drift(root, base, refuse, want)]'
scope_mutant "base_drift excuses a refusal the base does not draw" 'measured, was, hit)[0]) & set(refuse)' 'measured, was, hit)[0]) | set(refuse)'
scope_mutant "base_drift traces the head again" 'measured, _, _ = trace_steps(root, was, hit, mb)' 'measured, _, _ = trace_steps(root, was, hit)'
scope_mutant "base_drift grades the base against the head's table" 'drift(parse_table(git("show", f"{mb}:{TABLE}")), measured, was, hit)' 'drift(load_table(root / TABLE), measured, was, hit)'
scope_mutant "the scratch clone lays the working tree over a named commit" 'listed = "" if rev else git("ls-files"' 'listed = git("ls-files"'
scope_mutant "precheck passes a step that failed under the tracer" 'return 1 if refuse else SKIP_RC if failed else 0' 'return 1 if refuse else 0'
scope_mutant "precheck skips over a refusal when a step failed" 'return 1 if refuse else SKIP_RC if failed else 0' 'return SKIP_RC if failed else 1 if refuse else 0'
scope_mutant "precheck drops a broken trace" 'refuse = broken + [r for r in refuse if' 'refuse = [r for r in refuse if'
scope_mutant "precheck runs on with no strace" '    if shutil.which("strace") is None or _traced():
        print(f"selftest_scope precheck: skip' '    if False:
        print(f"selftest_scope precheck: skip'
scope_mutant "precheck traces when nothing is touched" '    if not want:
        print("selftest_scope precheck: the diff changes' '    if False:
        print("selftest_scope precheck: the diff changes'
scope_mutant "a partial drift names the untraced steps" '        if only is not None and sid not in only:
            continue' '        if False:
            continue'
scope_mutant "a partial drift names an extra entry" 'for sid in sorted(set(table["steps"]) - set(gated_ids(steps))) if only is None else ():' 'for sid in sorted(set(table["steps"]) - set(gated_ids(steps))):'
wait
cat "$tmp"/r.*
[ "$(ls "$tmp"/r.* | wc -l)" -eq "$n" ] || { echo "MUTANT LOST: $n started, $(ls "$tmp"/r.* | wc -l) reported"; exit 1; }
! grep -q -e '^   NOT REFUSED$' -e '^MUTANT NOT APPLIED: ' "$tmp"/r.* || exit 1
echo "SELFTEST-SCOPE MUTANTS: every mutant refused"
