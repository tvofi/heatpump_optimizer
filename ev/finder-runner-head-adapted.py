import subprocess, sys, pathlib
W = pathlib.Path(sys.argv[1]); f = W/"mut/tools/pr/app_approve.sh"
orig = f.read_text()
M = [
 ("X0 null", None, None),
 ("X1 unbounded: budget test -> false", '|| [ "$_try" -ge "$READ_TRIES" ]; then', '|| false; then'),
 ("X2 READ_TRIES=4 -> 5", "READ_TRIES=4\n", "READ_TRIES=5\n"),
 ("X2b READ_TRIES=4 -> 3", "READ_TRIES=4\n", "READ_TRIES=3\n"),
 ("X3 429 not transient", "    5??|429) return 0 ;;", "    5??) return 0 ;;"),
 ("X4 5xx not transient", "    5??|429) return 0 ;;", "    429) return 0 ;;"),
 ("X4b only 50x transient", "    5??|429) return 0 ;;", "    50?|429) return 0 ;;"),
 ("X5 every 403 transient", "grep -qi 'secondary rate limit'; return ;;", "true; return ;;"),
 ("X6 403 branch deleted", "    403) printf '%s\\n' \"$status\" | grep -qi 'secondary rate limit'; return ;;\n", ""),
 ("X7 drop 'error connecting to' alternative", "|^error connecting to '", "'"),
 ("X8 drop Go Get alternative", "'^Get \"https?://[^\"]*\": |^error connecting to '", "'^error connecting to '"),
 ("X9 sed requires a message", "s/^gh: (.*\\()?HTTP", "s/^gh: (.*\\()HTTP"),
 ("X10 no backoff (sleep 5 always)", 'sleep "$_delay"', 'sleep 5'),
 ("X11 backoff x2", "_delay=$((_delay * 3))", "_delay=$((_delay * 2))"),
 ("X12 READ_SLEEP=1", "READ_SLEEP=5\n", "READ_SLEEP=1\n"),
 ("X13 tail -1 -> head -1", "\\2 &/p' | tail -1)", "\\2 &/p' | head -1)"),
 ("X14 secondary grep case-sensitive", "grep -qi 'secondary rate limit'", "grep -q 'secondary rate limit'"),
 ("X15 transport grep matches anything", "grep -qE '^Get \"https?://[^\"]*\": |^error connecting to '", "grep -qE '.*'"),
 ("X16 success path keeps stderr file", "      rm -f \"$_ef\"; printf -v", "      printf -v"),
 ("X17 classify GH_ERR not file", 'gh_transient "$(cat "$_ef")"', 'gh_transient "$GH_ERR"'),
 ("X18 sleep deleted", '    sleep "$_delay"\n', ''),
 ("X19 check_pr bypasses gh_read", 'gh_read js "repos/$1/pulls/$2" ||', 'js=$(gh api "repos/$1/pulls/$2") ||'),
 ("X20 secondary grep any 'rate limit'", "grep -qi 'secondary rate limit'", "grep -qi 'rate limit'"),
 ("X21 loop retries non-transient (drop !)", 'if ! gh_transient', 'if gh_transient'),
 ("X22 transport anchor dropped", "'^Get \"https?://[^\"]*\": |^error connecting to '", "'Get \"https?://[^\"]*\": |error connecting to '"),
]
sel = sys.argv[2:]
for name, a, b in M:
    if sel and name.split()[0] not in sel: continue
    if a is not None:
        assert orig.count(a) >= 1, (name, a)
        f.write_text(orig.replace(a, b, 1))
    p = subprocess.run(["bash", "tools/pr/app_approve.sh", "--self-test"], cwd=W/"mut", capture_output=True, text=True)
    f.write_text(orig)
    fails = [l for l in (p.stdout+p.stderr).splitlines() if l.startswith("FAIL")]
    summ = [l for l in (p.stdout+p.stderr).splitlines() if "checks," in l]
    print(f"{name}: rc={p.returncode} {summ[-1] if summ else ''} {'KILLED' if p.returncode else 'SURVIVED'}")
    for l in fails[:4]: print("    ", l)
    sys.stdout.flush()
