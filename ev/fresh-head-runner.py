# Reviewer-built fresh one-line mutants at 53f24912 (finder-runner.py's shape).
import subprocess, sys, pathlib
W = pathlib.Path(sys.argv[1]); f = W/"mut/tools/pr/app_approve.sh"
orig = f.read_text()
P403 = "    403) printf '%s\\n' \"$status\" | grep -qi 'secondary rate limit'; return ;;"
SED = "\\2 &/p' | tail -1)"
TR = "  printf '%s\\n' \"$1\" | grep -qE '^Get"
M = [
 ("G0 null", None, None),
 ("G1 F13: 403 phrase reads all stderr, then tail -1", P403, P403.replace('"$status" |', '"$1" | tail -1 |')),
 ("G2 403 phrase reads all stderr, then head -1", P403, P403.replace('"$status" |', '"$1" | head -1 |')),
 ("G3 403 phrase reads all stderr (revert to round 3's code)", P403, P403.replace('"$status"', '"$1"')),
 ("G4 status line | tail -1 (claimed equivalent)", P403, P403.replace('"$status" |', '"$status" | tail -1 |')),
 ("G5 status line | head -1 (claimed equivalent)", P403, P403.replace('"$status" |', '"$status" | head -1 |')),
 ("G6 sed keeps code only (\\2 & -> \\2)", SED, "\\2/p' | tail -1)"),
 ("G7 sed keeps message (\\2 & -> \\2 \\1)", SED, "\\2 \\1/p' | tail -1)"),
 ("G8 case on whole status ${status%% *} -> $status", 'case "${status%% *}" in', 'case "$status" in'),
 ("G9 shortest suffix ${status%% *} -> ${status% *}", 'case "${status%% *}" in', 'case "${status% *}" in'),
 ("G10 status tail -1 -> head -1", SED, "\\2 &/p' | head -1)"),
 ("G11 status tail deleted", SED, "\\2 &/p')"),
 ("G12 phrase -qi -> -qiw", "grep -qi 'secondary rate limit'", "grep -qiw 'secondary rate limit'"),
 ("G13 phrase -qi -> -q", "grep -qi 'secondary rate limit'", "grep -q 'secondary rate limit'"),
 ("G14 phrase -> 'secondary rate limit.'", "grep -qi 'secondary rate limit'", "grep -qi 'secondary rate limit\\.'"),
 ("G15 phrase -> 'rate limit'", "grep -qi 'secondary rate limit'", "grep -qi 'rate limit'"),
 ("G16 every 403 transient", "grep -qi 'secondary rate limit'; return ;;", "true; return ;;"),
 ("G17 transport reads status not stderr", TR, TR.replace('"$1"', '"$status"')),
 ("G18 transport reads tail -1 of stderr", TR, TR.replace('"$1" |', '"$1" | tail -1 |')),
 ("G19 transport reads head -1 of stderr", TR, TR.replace('"$1" |', '"$1" | head -1 |')),
 ("G20 status reads tail -1 of stderr first", "  status=$(printf '%s\\n' \"$1\" |", "  status=$(printf '%s\\n' \"$1\" | tail -1 |"),
 ("G21 status reads head -1 of stderr first", "  status=$(printf '%s\\n' \"$1\" |", "  status=$(printf '%s\\n' \"$1\" | head -1 |"),
 ("G22 budget unbounded", '|| [ "$_try" -ge "$READ_TRIES" ]; then', '|| false; then'),
 ("G23 READ_TRIES 4->3", "READ_TRIES=4\n", "READ_TRIES=3\n"),
 ("G24 READ_TRIES 4->5", "READ_TRIES=4\n", "READ_TRIES=5\n"),
 ("G25 READ_SLEEP 5->1", "READ_SLEEP=5\n", "READ_SLEEP=1\n"),
 ("G26 backoff x3 -> x2", "_delay=$((_delay * 3))", "_delay=$((_delay * 2))"),
 ("G27 no backoff", 'sleep "$_delay"', 'sleep 5'),
 ("G28 sleep deleted", '    sleep "$_delay"\n', ''),
 ("G29 retry non-transient (drop !)", 'if ! gh_transient', 'if gh_transient'),
 ("G30 classify folded GH_ERR", 'gh_transient "$(cat "$_ef")"', 'gh_transient "$GH_ERR"'),
 ("G31 5??|429 -> 5??", "    5??|429) return 0 ;;", "    5??) return 0 ;;"),
 ("G32 403 key -> 40?", "    403) printf", "    40?) printf"),
]
sel = sys.argv[2:]
for name, a, b in M:
    if sel and name.split()[0] not in sel: continue
    if a is not None:
        if orig.count(a) < 1:
            print(f"{name}: NOT-APPLICABLE (text absent)"); continue
        f.write_text(orig.replace(a, b, 1))
    p = subprocess.run(["bash", "tools/pr/app_approve.sh", "--self-test"], cwd=W/"mut", capture_output=True, text=True)
    f.write_text(orig)
    out = (p.stdout+p.stderr).splitlines()
    fails = [l for l in out if l.startswith("FAIL")]
    summ = [l for l in out if "checks," in l]
    print(f"{name}: rc={p.returncode} {summ[-1] if summ else ''} {'KILLED' if p.returncode else 'SURVIVED'}")
    for l in fails[:4]: print("    ", l)
    sys.stdout.flush()
