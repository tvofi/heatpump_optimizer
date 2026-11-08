"""Reviewer's targeted mutants for #3288 at f326fd6d (reviewer-built, not the finder's)."""
import subprocess, sys, pathlib
root = pathlib.Path(sys.argv[1]); only = sys.argv[2:]
MT="tools/audit/seat/merge_train.py"; AA="tools/pr/app_approve.sh"; GR="tools/audit/seat/gh_read.py"
RM="tools/audit/seat/remerge_main.sh"; HR="dev/audit/harnesses/r10_codescan_wait_race.py"
T_MT="python3 tools/audit/seat/merge_train.py --self-test 2>&1 | tail -1"
T_AA="bash tools/pr/app_approve.sh --self-test 2>&1 | tail -1"
T_PA="bash tools/audit/seat/pr_args.sh --self-test 2>&1 | tail -1"
T_GR="python3 -c \"import sys; sys.path.insert(0,'tools/audit/seat'); import gh_read; sys.exit(gh_read.self_test())\" 2>&1 | tail -1"
T_HR="python3 dev/audit/harnesses/r10_codescan_wait_race.py --selftest 2>&1 | tail -1"
M = {
 "deferred-no-held": (MT, '"completed", "action_required", ""', '"completed", ""', T_MT),
 "deferred-empty": (MT, '        if red != [GATE]:\n            return []', '        return []', T_MT),
 "no-grace-poll": (MT, 'elif graced and red == [GATE]:', 'elif False:', T_MT),
 "drop-main-busy": (MT, '                    busy = self._gate_busy(h, runs)\n', '                    busy = []\n', T_MT),
 "mt-no-git-retry": (MT, 'return gh_read.run_git_retry(run, argv, self.sleep, lambda line: self.log(f"merge_train: {line}"), **kw)', 'return run(argv, **kw)', T_MT),
 "aa-plain-fetch": (AA, 'retry_with git_transient _fetched git fetch', 'git fetch', T_AA),
 "aa-gh-classifier": (AA, 'retry_with git_transient _fetched', 'retry_with gh_transient _fetched', T_AA),
 "aa-always-transient": (AA, 'git_transient() { printf', 'git_transient() { return 0; printf', T_AA),
 "rm-plain-fetch": (RM, 'python3 "$SEAT/gh_read.py" --git-retry git fetch', 'git fetch', T_PA),
 "gr-one-try": (GR, 'if not code or n == GIT_TRIES or not git_transient(o):', 'if True:', T_GR),
 "gr-refused-ignored": (GR, 'return not GIT_REFUSED.search(output) and bool', 'return bool', T_MT),
 "hr-no-fallback": (HR, 'for size in (100, 30):', 'for size in (100,):', T_HR),
}
def sh(c): return subprocess.run(c, shell=True, cwd=root, capture_output=True, text=True).stdout.strip()
print("NULL (unmutated):")
for t in sorted({v[3] for v in M.values()}): print("  ", t.split()[1] if 'import gh_read' not in t else 'gh_read', "->", sh(t))
for name, (f, a, b, t) in M.items():
    if only and name not in only: continue
    p = root / f; src = p.read_text()
    assert src.count(a) == 1, (name, src.count(a))
    p.write_text(src.replace(a, b))
    try: print(f"RESULT mutant={name} file={f} -> {sh(t)}")
    finally: p.write_text(src)
print("restored:", sh("git status --porcelain") or "clean")
