import subprocess, sys, pathlib, concurrent.futures as cf
W = pathlib.Path(open('/root/W').read().strip())
H = "7a85168ef3ce5112c145e3441567d5bf28c632d0"
REPO = "/home/user/heatpump_optimizer"
CO, RL, PR, GC = ("tools/audit/seat/closeout.py", "tools/audit/seat/roster_lib.py",
                  "tools/audit/seat/prune_refs.py", "tools/audit/worktree_gc.sh")
T = {CO: "python3 tools/audit/seat/closeout.py --self-test", RL: "python3 tools/audit/seat/closeout.py --self-test",
     PR: "python3 tools/audit/seat/prune_refs.py --self-test", GC: "bash tools/audit/worktree_gc.sh --self-test"}
M = [  # (id, file, old, new, count-th occurrence (0=first) )
 ("M01-co-blocker-exempt-dropped", CO, "exempt = roster_lib.closeout_exempt(roster)[0]", "exempt = set()", 0),
 ("M02-co-issue-exempt-dropped", CO, "exempt = roster_lib.closeout_exempt(c.roster)[1]", "exempt = set()", 0),
 ("M03-rl-host-condition-dropped", RL, "\n             and (G[n][\"resume\"].get(\"host\") not in open_)}", "}", 0),
 ("M04-rl-ruled-empty", RL, 'RULED_STAGES = ("refused", "refuted")', "RULED_STAGES = ()", 0),
 ("M05-rl-no-transitive-post", RL, "    grew = True\n    while grew:", "    grew = False\n    while grew:", 0),
 ("M06-rl-post-issues-dropped", RL, "return post | ruled, {i for n in post", "return post | ruled, {i for n in ()", 0),
 ("M07-pr-alias-off", PR, "        tags = [(sha_tag(a, s) if held.get(a, s) != s else a, s) for a, s in tags]", "        pass", 0),
 ("M08-pr-delete-check-plain-only", PR, "and s not in (have.get(archive_tag(n)), have.get(sha_tag(archive_tag(n), s)))", "and s != have.get(archive_tag(n))", 0),
 ("M09-pr-alias-always", PR, "if held.get(a, s) != s else a", "if True else a", 0),
 ("M10-gc-classA-cwd-dropped", GC, '    cwd_free "$wt" "$real" || return 0\n    ELIGIBLE=$((ELIGIBLE+1))\n    if [ -n "$st_out" ]', '    ELIGIBLE=$((ELIGIBLE+1))\n    if [ -n "$st_out" ]', 0),
 ("M11-gc-classB-cwd-dropped", GC, '  cwd_free "$wt" "$real" || return 0\n  ELIGIBLE=$((ELIGIBLE+1))\n  if [ "$onremote" -eq 1 ]', '  ELIGIBLE=$((ELIGIBLE+1))\n  if [ "$onremote" -eq 1 ]', 0),
 ("M12-gc-classB-cwd-onremote-only", GC, '  cwd_free "$wt" "$real" || return 0\n  ELIGIBLE=$((ELIGIBLE+1))\n  if [ "$onremote" -eq 1 ]', '  if [ "$onremote" -eq 1 ]; then cwd_free "$wt" "$real" || return 0; fi\n  ELIGIBLE=$((ELIGIBLE+1))\n  if [ "$onremote" -eq 1 ]', 0),
 ("M13-gc-dirty-topic-guard-dropped", GC, 'if [ "$topic" -eq 1 ] && {', 'if false && {', 0),
 ("M14-gc-topic-closed-not-mapped", GC, "          merged|closed) topic=1 ;;", "          merged) topic=1 ;;", 0),
 ("M15-gc-topic-mapping-off", GC, "    work/?*|scratch/?*|seat/?*) pr_state_of", "    NEVERMATCH) pr_state_of", 0),
 ("M16-gc-closed-state-unread", GC, '("closed" if "CLOSED" in s else "none")', '"none"', 0),
 ("M17-gc-E-merged-check-off", GC, 'if [ "$(pr_state_of "fix/$topic")" != merged ]; then', 'if false; then', 0),
 ("M18-gc-E-age-guard-off", GC, '    if recently_modified "$seat_real" "$ORPHAN_AGE"; then\n      printf \'keep  %s  fresh\\n\' "$seat_real"', '    if false; then\n      printf \'keep  %s  fresh\\n\' "$seat_real"', 0),
 ("M19-gc-E-cwd-off", GC, '      cwd_free "$cp" "$cp" || continue', '      :', 0),
 ("M20-gc-E-gitdir-guard-off", GC, '[ -d "$cp" ] && [ ! -e "$cp/.git" ] || continue', '[ -d "$cp" ] || continue', 0),
 ("M21-gc-E-live-under-off", GC, '    nested=$(live_under "$seat_real")\n    if [ -n "$nested" ]; then\n      printf \'keep  %s  live-worktree (%s)\\n\' "$seat_real" "$nested"; KEPT_N=$((KEPT_N+1)); continue\n    fi\n    for cp', '    for cp', 0),
 ("M22-gc-seats-first-root-only", GC, 'IFS=: read -r -a SEATS_LIST <<<"$SEATS_ROOT"', 'IFS=: read -r -a SEATS_LIST <<<"${SEATS_ROOT%%:*}"', 0),
 ("M23-gc-E-name-filter-any", GC, "        *mutant*|*null*|*head*) copies+=", "        *) copies+=", 0),
 ("N00-gc-null-comment-only", GC, "# --- class E: plain repo copies in a seat dir", "# --- class E: plain repo copies in a seat dir (null edit)", 0),
 ("N01-pr-null-comment-only", PR, "    if tags:\n        held = remote_tags", "    if tags:  # null edit\n        held = remote_tags", 0),
 ("M24-gc-E-dry-run-ignored", GC, '      if [ "$DRY" -eq 0 ]; then\n        rm -rf "$cp"', '      if true; then\n        rm -rf "$cp"', 0),
]
def run(m):
    mid, f, old, new, _ = m
    d = W / "mut" / mid
    subprocess.run(["git", "-C", REPO, "worktree", "add", "-q", "--detach", str(d), H], check=True)
    p = d / f; s = p.read_text()
    n = s.count(old)
    if n != 1:
        return f"RESULT {mid} NOT-APPLIED (anchor count {n})"
    p.write_text(s.replace(old, new))
    r = subprocess.run(T[f], shell=True, cwd=d, capture_output=True, text=True, timeout=1800)
    out = r.stdout + r.stderr
    (W / "ev" / f"mutant-{mid}.txt").write_text(out[-6000:] + f"\nrc={r.returncode}\n")
    fails = [l for l in out.splitlines() if "FAIL" in l][:3]
    subprocess.run(["git", "-C", REPO, "worktree", "remove", "--force", str(d)])
    return f"RESULT {mid} {'KILLED' if r.returncode != 0 else 'SURVIVED'} rc={r.returncode} {fails[:2]}"
sel = [m for m in M if len(sys.argv) < 2 or m[0] in sys.argv[1:]]
with cf.ThreadPoolExecutor(4) as ex:
    for line in ex.map(run, sel):
        print(line, flush=True)
