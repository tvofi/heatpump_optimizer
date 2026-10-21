#!/bin/bash
# pr_args.sh -- the argument checks, the stop report and the signal reap
# open_pr.sh and update_pr.sh share, so neither can stop without saying why,
# and a stopped one ends the work it started.
#
#   . tools/audit/seat/pr_args.sh       (open_pr.sh, update_pr.sh; PR_NAME first)
#   tools/audit/seat/pr_args.sh --self-test
#
# WHY IT EXISTS (R10-OPENPR-SILENT, 2026-10-18). open_pr.sh runs under
# `set -eo pipefail`. Twice the orchestrator passed the handoff-BODY sha where
# the CODE sha belongs; `git merge-base --is-ancestor` returned non-zero, prints
# nothing when it does, and the script exited -- the daemonize log held only
# its banner and read as a hang for 40 minutes. Two layers close it:
#   - the checks below refuse a wrong argument up front, naming it, and name a
#     body sha as one ("that is the BODY sha; pass the CODE sha");
#   - pr_trap's ERR trap reports every other stop errexit makes -- the failing
#     command, its line and its status -- so no stop is silent. `-E` carries the
#     trap into functions and substitutions; it reports from the top-level shell
#     only, where the failure reaches the assignment or command that stops it.
# Every line is "<PR_NAME>: REFUSE: ..." or "<PR_NAME>: STOPPED: ...", on stderr.
#
# THE MUTANTS. A line ending in `# mut:<name>` is the predicate one self-test
# arm pins. The self-test runs each arm on copies of the scripts and again on
# copies without that line, and the arm must fail there: a check that passed
# both ways would pin nothing. Sourcing defines functions only; it runs nothing.

pr_refuse() { printf '%s: REFUSE: %s\n' "${PR_NAME:-pr}" "$*" >&2; exit 1; }
pr_stopped() { # <status> <line> <command>: the ERR trap's report
  [ "${BASH_SUBSHELL:-0}" = 0 ] || return 0
  printf '%s: STOPPED: line %s exited %s: %s\n' "${PR_NAME:-pr}" "$2" "$1" "$3" >&2
}
pr_trap() { # errexit, the report of every stop it makes, and the signal reap
  set -Eeo pipefail
  trap 'pr_stopped $? $LINENO "$BASH_COMMAND"' ERR  # mut:trap
  pr_signal_traps
}
pr_need_args() { # <min> <got> <usage>
  [ "$2" -ge "$1" ] || pr_refuse "$2 argument(s), at least $1 needed: $3"  # mut:arity
}
pr_code_sha_shape() { # <sha>: a full sha, not an abbreviation or a ref name
  local re='^[0-9a-f]{40}$'
  [[ $1 =~ $re ]] || pr_refuse "code sha '$1' is not 40 lowercase hex characters"  # mut:hex
}
pr_handoff_tips() { # <topic> <need-body: 1|0>: sets PR_HT and PR_BT from what origin answers
  local out
  out=$(git ls-remote origin "refs/heads/handoff/$1" "refs/heads/handoff-body/$1") \
    || pr_refuse "could not list handoff/$1 and handoff-body/$1 on origin"
  PR_HT=$(printf '%s\n' "$out" | awk -v r="refs/heads/handoff/$1" '$2 == r { print $1 }')
  PR_BT=$(printf '%s\n' "$out" | awk -v r="refs/heads/handoff-body/$1" '$2 == r { print $1 }')
  [ -n "$PR_HT" ] || pr_refuse "origin has no handoff/$1 (the code ref)"  # mut:noref
  [ "$2" = 0 ] || [ -n "$PR_BT" ] || pr_refuse "origin has no handoff-body/$1 (the body ref)"  # mut:nobody
}
pr_code_in_handoff() { # <sha> <topic>: after the fetch of handoff/<topic>; PR_HT and PR_BT set
  git cat-file -e "$1^{commit}" 2>/dev/null || pr_refuse "code sha $1 does not resolve to a commit here, after fetching handoff/$2"  # mut:resolve
  git merge-base --is-ancestor "$1" "$PR_HT" && return 0
  [ "$1" != "$PR_BT" ] || pr_refuse "code sha $1 is not an ancestor of origin/handoff/$2 ($PR_HT); it is the tip of handoff-body/$2: that is the BODY sha; pass the CODE sha"  # mut:body
  pr_refuse "code sha $1 is not an ancestor of origin/handoff/$2 ($PR_HT), and it is not the tip of handoff-body/$2 (${PR_BT:-absent})"  # mut:ancestor
}
pr_push_failed() { # <log>: a refused push names its refusal, or its log's tail
  grep -E 'REFUSE' "$1" >&2 || tail -n 20 "$1" >&2 || true
  pr_refuse "the push failed; its log is $1"
}

# ---- the stop: reap the whole descendant tree -------------------------------
# WHY IT EXISTS (R10-PUSHER-REAP, 2026-10-20). A pusher stopped with TERM left
# its whole subtree running: a shell does not forward a signal to a foreground
# child, so the child reparented to launchd and kept burning CPU -- six
# survivors aged 26 to 62 minutes on a box already at load 77 on eight cores,
# each needing a kill two levels further down. Bash also DEFERS a trap until the
# foreground command finishes, so a trap alone stops nothing while a push runs:
# the callers run the pusher asynchronously and `wait` on it (pr_wait), which a
# trapped signal interrupts.
#
# The reap walks children by parent pid and signals each by pid -- never
# `pkill -f`, which on a shared box reaches other seats' processes. The walk
# appends to PR_REAP_PIDS in a function called from this shell, so the pgrep in
# its `for` list is the only child each step forks -- a wrapping subshell would
# itself be listed as a descendant of this shell.
pr_descendants() { # <pid>: append every live descendant to PR_REAP_PIDS, a parent before its children
  local k
  for k in $(pgrep -P "$1" 2>/dev/null); do
    PR_REAP_PIDS[${#PR_REAP_PIDS[@]}]=$k
    pr_descendants "$k"
  done
}
pr_kill() { # <signal> <pid>: one numeric pid above 1 -- never a pattern, never a group
  case $2 in ''|0|1|*[!0-9]*) return 0 ;; esac
  kill -"$1" "$2" 2>/dev/null || :  # mut:stop
}
pr_reap() { # TERM every descendant of this shell, then KILL whatever outlives a bounded grace
  local p alive n=0
  PR_REAP_PIDS=()
  pr_descendants $$
  [ "${#PR_REAP_PIDS[@]}" -gt 0 ] || return 0
  for p in "${PR_REAP_PIDS[@]}"; do pr_kill TERM "$p"; done
  while [ "$n" -lt "${PR_REAP_TENTHS:-20}" ]; do
    alive=()
    for p in "${PR_REAP_PIDS[@]}"; do kill -0 "$p" 2>/dev/null && alive[${#alive[@]}]=$p; done
    [ "${#alive[@]}" -gt 0 ] || return 0
    PR_REAP_PIDS=("${alive[@]}")
    sleep 0.1
    n=$((n + 1))
  done
  for p in "${PR_REAP_PIDS[@]}"; do pr_kill KILL "$p"; done
  return 0
}
pr_signal_exit() { # <status>: a stop signal -- reap the tree, then end the shell
  trap '' TERM INT HUP  # a second signal must not interrupt the reap
  pr_reap
  exit "$1"
}
pr_signal_traps() { # TERM/INT/HUP end the whole descendant tree, then the shell
  trap 'pr_signal_exit 143' TERM
  trap 'pr_signal_exit 130' INT
  trap 'pr_signal_exit 129' HUP
}
pr_wait() { # <pid> <log>: wait for the asynchronous pusher -- a trapped signal interrupts it
  local rc=0
  wait "$1" || rc=$?
  [ "$rc" = 0 ] || pr_push_failed "$2"
}

# ---- self-test -------------------------------------------------------------
# One scratch origin (a plain repository: no push anywhere) and a clone of it
# holding copies of the scripts, so the scripts' own `origin` is the scratch
# one. Offline: `gh` is a stub (its open list is $t/prs.json; $t/gh.fail makes
# it fail), and app_push.sh is absent from the clone, so a
# run that passes every check stops at its push, which pr_push_failed reports.
# The clone also carries tools/pr/head_note.py, which open_pr.sh and
# update_pr.sh resolve (`PRT`) before their first check: without it every run
# stopped in the ERR trap there, and 25 arms failed (#2444's CI, after #2442).
pr_args_self_test() (
  local src t f=0 n=0 o m base code side body i reapsha UNREL
  src=$(cd "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
  t=$(mktemp -d) || { echo "pr_args self-test: no temporary directory"; return 1; }
  # The pusher stubs the reap arms drive read this directory ($T is open_pr's topic).
  REAP_DIR=$t; export REAP_DIR
  # A stopped pusher's stub app_push: it records itself and a two-level sleep
  # tree by pid, then blocks, so the survivors of a signal can be counted. A
  # successful run (`ok`) leaves nothing behind; a later run (`fast`) exits at once.
  cat > "$t/reap-stub.sh" <<'STUB'
#!/bin/bash
echo $$ > "$REAP_DIR/started"
echo $$ >> "$REAP_DIR/pids"
[ -e "$REAP_DIR/fast" ] && exit 1
if [ -e "$REAP_DIR/ok" ]; then
  bash -c 'sleep 1' reap-child "$REAP_DIR/mark" & echo $! >> "$REAP_DIR/pids"
  wait; exit 0
fi
bash -c 'sleep 30; :' reap-parent "$REAP_DIR/mark" & echo $! >> "$REAP_DIR/pids"
bash -c 'sleep 30 & echo $! >> "$0"; wait' "$REAP_DIR/pids" & echo $! >> "$REAP_DIR/pids"
wait
exit 1
STUB
  . "$src/../../../tests/throwaway_git.sh" && throwaway_git_env
  ck() { n=$((n + 1)); if [ "$2" = 0 ]; then echo "  ok   $1"; else f=$((f + 1)); echo "  FAIL $1"; fi; }
  o=$t/o; m=$t/m
  { throwaway_git_init "$o" -q -b main && printf 'a\n' > "$o/a" && git -C "$o" add a \
    && git -C "$o" commit -q -m base && base=$(git -C "$o" rev-parse HEAD) \
    && printf 'b\n' > "$o/b" && git -C "$o" add b && git -C "$o" commit -q -m code \
    && code=$(git -C "$o" rev-parse HEAD) && git -C "$o" branch handoff/x "$code" \
    && git -C "$o" branch handoff/y "$code" \
    && git -C "$o" checkout -q -b reapup "$code" && mkdir -p "$o/tools/pr" \
    && cp "$REAP_DIR/reap-stub.sh" "$o/tools/pr/app_push.sh" \
    && git -C "$o" add tools/pr/app_push.sh && git -C "$o" commit -q -m "reap stub" \
    && git -C "$o" checkout -q main && git -C "$o" branch handoff/reap reapup \
    && git -C "$o" checkout -q -b side "$base" && printf 'c\n' > "$o/c" && git -C "$o" add c \
    && git -C "$o" commit -q -m side && side=$(git -C "$o" rev-parse HEAD) \
    && git -C "$o" checkout -q main && git -C "$o" reset -q --hard "$base" \
    && git -C "$o" branch fix/x "$base" \
    && printf '## Head\n\nthe body\n' > "$t/body.md" \
    && body=$(git -C "$o" commit-tree "$(printf '100644 blob %s\tBODY.md\n' \
         "$(git -C "$o" hash-object -w "$t/body.md")" | git -C "$o" mktree)" -m "body: x") \
    && git -C "$o" update-ref refs/heads/handoff-body/x "$body" \
    && git -C "$o" update-ref refs/heads/handoff-body/z "$body" \
    && git -C "$o" update-ref refs/heads/handoff-body/reap "$body" \
    && throwaway_git_clone -q "$o" "$m" && mkdir -p "$t/bin" "$m/tools/audit/seat" "$m/tools/pr" \
    && cp "$src/../../pr/head_note.py" "$m/tools/pr/head_note.py" \
    && printf '#!/bin/sh\n[ -e "%s/gh.fail" ] && { echo "HTTP 403" >&2; exit 1; }\ncase "$*" in *--head*) echo 5 ;; "pr list"*) cat "%s/prs.json" ;; "pr view"*) echo "a title" ;; *) exit 99 ;; esac\n' "$t" "$t" > "$t/bin/gh" \
    && echo '[]' > "$t/prs.json" \
    && chmod +x "$t/bin/gh"; } || { echo "  FAIL fixture"; rm -rf "$t"; return 1; }
  reapsha=$(git -C "$o" rev-parse reapup)
  export PATH="$t/bin:$PATH"; unset HANDOFF_TOPIC PR_N
  # run <mutant|-> <script> <args...>: copies of the scripts (less the mutant's
  # line), a fresh state root, the output in $t/out and the status in $t/rc.
  i=0
  run() {
    local mu=$1 sc=$2 g; shift 2; i=$((i + 1))
    # The last run's worktrees go, so a branch it checked out is free again.
    rm -rf "$t/s$((i - 1))"; git -C "$m" worktree prune
    for g in open_pr.sh update_pr.sh delivery_row.sh pr_args.sh pr_cap.py; do
      if [ "$mu" = - ]; then cp "$src/$g" "$m/tools/audit/seat/$g"
      else grep -v "# mut:$mu\$" "$src/$g" > "$m/tools/audit/seat/$g"; fi
    done
    HPO_STATE_DIR=$t/s$i BR=fix/x-$i BR_FIXED=1 bash "$m/tools/audit/seat/$sc" "$@" > "$t/out" 2>&1
    echo $? > "$t/rc"
  }
  # arm <name> <mutant> <expected text> <script> <args...>: refuses, naming it;
  # and the mutant without that line no longer prints the text.
  arm() {
    local nm=$1 mu=$2 want=$3; shift 3
    run - "$@"; [ "$(cat "$t/rc")" != 0 ] && grep -qF -- "$want" "$t/out"
    ck "$nm" $?
    run "$mu" "$@"; ! grep -qF -- "$want" "$t/out"
    ck "  mutant mut:$mu (its line deleted) fails that arm" $?
  }
  arm "open_pr: three arguments refuse, naming the count" arity \
    "open_pr: REFUSE: 3 argument(s), at least 4 needed" open_pr.sh x "$code" T
  arm "open_pr: an abbreviated code sha refuses as not 40-hex" hex \
    "open_pr: REFUSE: code sha '${code:0:12}' is not 40" open_pr.sh x "${code:0:12}" T G
  arm "open_pr: a 40-hex sha that names no commit refuses as unresolved" resolve \
    "open_pr: REFUSE: code sha 0123456789012345678901234567890123456789 does not resolve" \
    open_pr.sh x 0123456789012345678901234567890123456789 T G
  arm "open_pr: the body sha in the code slot refuses, naming it the BODY sha" body \
    "that is the BODY sha; pass the CODE sha" open_pr.sh x "$body" T G
  arm "open_pr: a non-ancestor refuses, saying it is not the body tip" ancestor \
    "open_pr: REFUSE: code sha $side is not an ancestor of origin/handoff/x ($code), and it is not the tip of handoff-body/x" \
    open_pr.sh x "$side" T G
  arm "open_pr: a topic with no handoff/<topic> refuses, naming the ref" noref \
    "open_pr: REFUSE: origin has no handoff/z" open_pr.sh z "$code" T G
  arm "open_pr: a topic with no handoff-body/<topic> refuses, naming the ref" nobody \
    "open_pr: REFUSE: origin has no handoff-body/y" open_pr.sh y "$code" T G
  mkdir -p "$t/s$((i + 1))/pr/x/wt" "$t/s$((i + 2))/pr/x/wt"
  touch "$t/s$((i + 1))/pr/x/wt/f" "$t/s$((i + 2))/pr/x/wt/f"
  arm "open_pr: a failing step past the checks (worktree add) reports itself through the ERR trap" trap \
    "open_pr: STOPPED: line" open_pr.sh x "$code" T G
  # The soft cap gates dispatch, not opening (pr_cap.py; tvofi, 2026-10-20):
  # a twenty-strong open board is information, and --over-cap is advisory.
  prs() { # <counted> [extra json objects]: the stub's open list
    local k=0 j=""
    while [ $k -lt "$1" ]; do j="$j{\"number\":$k,\"title\":\"t\",\"author\":{\"login\":\"app/hpo-author\",\"is_bot\":true}},"; k=$((k + 1)); done
    printf '[%s%s]\n' "$j" "${2:-}" | sed 's/,]$/]/' > "$t/prs.json"
  }
  # passes <name> <mutant> <expected text> <args...>: the run opens (stops only
  # at the absent push), printing the text and no cap refusal; on a copy
  # without the mutant's line the text is gone and the run did not crash (a
  # deleted line that only tracebacks pins no behaviour).
  passes() {
    local nm=$1 mu=$2 want=$3; shift 3
    run - open_pr.sh "$@"; grep -qF -- "$want" "$t/out" \
      && ! grep -q 'REFUSE: open-PR cap\|REFUSE: WIP cap' "$t/out" \
      && grep -qF "open_pr: REFUSE: the push failed" "$t/out"
    ck "$nm" $?
    run "$mu" open_pr.sh "$@"; ! grep -qF -- "$want" "$t/out" && ! grep -q Traceback "$t/out"
    ck "  mutant mut:$mu (its line deleted) no longer prints it" $?
  }
  prs 20
  passes "open_pr: twenty open pull requests do not stop an open; the count is information" openinfo \
    "open_pr: 20 open PRs; the cap gates dispatch, not opening" x "$code" T G
  passes "open_pr: --over-cap is still accepted, and says it is advisory" overadvisory \
    "open_pr: --over-cap is advisory: the train is draining (the cap gates dispatch, not opening)" \
    --over-cap "the train is draining" x "$code" T G
  touch "$t/gh.fail"
  run - open_pr.sh x "$code" T G
  grep -qF "open_pr: open pull requests could not be read (gh exited 1" "$t/out" \
    && ! grep -q 'REFUSE: open-PR cap\|REFUSE: WIP cap' "$t/out" \
    && grep -qF "open_pr: REFUSE: the push failed" "$t/out"
  ck "open_pr: an open count gh cannot read says so and still opens" $?
  run inforead open_pr.sh x "$code" T G
  ! grep -qF "could not be read" "$t/out" && ! grep -q Traceback "$t/out"
  ck "  mutant mut:inforead (its line deleted) reports the unreadable board as a count" $?
  rm -f "$t/gh.fail"
  prs 5 '{"number":90,"title":"record: rows","author":{"login":"app/hpo-author","is_bot":true}},{"number":91,"title":"bump","author":{"login":"app/dependabot","is_bot":true}}'
  passes "open_pr: a record: title and another bot's pull request are not in the open count" caprecord \
    "open_pr: 5 open PRs; the cap gates dispatch, not opening" x "$code" T G
  passes "open_pr: the same board, the bot pull request uncounted" capbot \
    "open_pr: 5 open PRs; the cap gates dispatch, not opening" x "$code" T G
  echo '[]' > "$t/prs.json"
  run - open_pr.sh x "$code" T G
  [ "$(cat "$t/rc")" != 0 ] && ! grep -q 'REFUSE: code sha\|REFUSE: origin has\|argument(s)' "$t/out" \
    && [ "$(git -C "$t/s$i/pr/x/wt" rev-parse HEAD)" = "$code" ] \
    && grep -qF "open_pr: REFUSE: the push failed; its log is $t/s$i/pr/x/p1.log" "$t/out" \
    && ! grep -q STOPPED "$t/out"
  ck "null control: open_pr with the code sha passes every check, and its failed push names its log" $?
  # ---- a stopped pusher reaps its whole descendant tree (R10-PUSHER-REAP) ----
  # The stub app_push above leaves a two-level sleep tree recorded by pid, so
  # each arm counts what is still alive after the signal. The bystander sleeper
  # started here descends from no pusher: it is the null control for "kills only
  # what it started", and the arm the by-pid rule is mutated against.
  ln -s /bin/sleep "$REAP_DIR/unrelated-sleep"
  "$REAP_DIR/unrelated-sleep" 300 & UNREL=$!
  ralive() { # <pids file> -> how many of its pids are alive; polled, since a killed child can be a zombie for a moment
    local p n k=0
    while :; do
      n=0
      for p in $(cat "$1" 2>/dev/null); do kill -0 "$p" 2>/dev/null && n=$((n + 1)); done
      if [ "$n" = 0 ] || [ "$k" -ge 30 ]; then echo "$n"; return; fi
      sleep 0.1; k=$((k + 1))
    done
  }
  rclean() { # end this fixture's recorded pids, by pid (never a pattern)
    local p
    for p in $(cat "$REAP_DIR/pids" 2>/dev/null); do
      case $p in ''|0|1|*[!0-9]*) ;; *) kill -TERM "$p" 2>/dev/null ;; esac
    done
    : > "$REAP_DIR/pids"
  }
  copyin() { # <mutant|->: copies of the scripts, less the named mutant's line
    local g
    for g in open_pr.sh update_pr.sh delivery_row.sh pr_args.sh pr_cap.py; do
      if [ "$1" = - ]; then cp "$src/$g" "$m/tools/audit/seat/$g"
      else grep -v "# mut:$1\$" "$src/$g" > "$m/tools/audit/seat/$g"; fi
    done
  }
  reapopen() { # <mutant>: TERM open_pr.sh mid-push and record what survives it
    local sd=$t/ropen up k=0
    git -C "$m" worktree prune; rm -rf "$sd"
    rm -f "$REAP_DIR/started" "$REAP_DIR/fast" "$REAP_DIR/ok"; : > "$REAP_DIR/pids"
    copyin "$1"
    HPO_STATE_DIR=$sd bash "$m/tools/audit/seat/open_pr.sh" reap "$reapsha" T G > "$t/out" 2>&1 & up=$!
    while [ "$(wc -l < "$REAP_DIR/pids")" -lt 4 ] && [ $k -lt 600 ]; do sleep 0.05; k=$((k + 1)); done
    kill -TERM "$up"; k=0
    while kill -0 "$up" 2>/dev/null && [ $k -lt 40 ]; do sleep 0.1; k=$((k + 1)); done
    kill -0 "$up" 2>/dev/null && echo alive > "$t/pusher" || echo gone > "$t/pusher"
    ralive "$REAP_DIR/pids" > "$t/survivors"
    kill -0 "$UNREL" 2>/dev/null && echo alive > "$t/unrel" || echo gone > "$t/unrel"
    rclean; wait "$up" 2>/dev/null
    git -C "$m" worktree remove --force "$sd/pr/reap" 2>/dev/null
    git -C "$m" branch -D fix/reap fix/reap-pr 2>/dev/null; rm -rf "$sd"
  }
  reapopen -
  ck "open_pr: TERM reaps the whole descendant tree, and the pusher is gone" \
     "$( [ "$(cat "$t/pusher")" = gone ] && [ "$(cat "$t/survivors")" = 0 ] && echo 0 || echo 1 )"
  ck "open_pr: the null control -- an unrelated sleeper survives" \
     "$( [ "$(cat "$t/unrel")" = alive ] && echo 0 || echo 1 )"
  reapopen stop
  ck "  mutant mut:stop (the reap's kill line deleted): the pusher dies and its tree survives" \
     "$( [ "$(cat "$t/survivors")" -gt 0 ] && echo 0 || echo 1 )"
  arm "update_pr: two arguments refuse, naming the count" arity \
    "update_pr: REFUSE: 2 argument(s), at least 3 needed" update_pr.sh fix/x "$code"
  arm "update_pr: an abbreviated code sha refuses as not 40-hex" hex \
    "update_pr: REFUSE: code sha '${code:0:12}' is not 40" update_pr.sh fix/x "${code:0:12}" "$t/body.md"
  arm "update_pr: the body sha in the code slot refuses, naming it the BODY sha" body \
    "that is the BODY sha; pass the CODE sha" update_pr.sh fix/x "$body" "$t/body.md"
  arm "update_pr: a non-ancestor refuses, saying it is not the body tip" ancestor \
    "update_pr: REFUSE: code sha $side is not an ancestor of origin/handoff/x ($code), and it is not the tip of handoff-body/x" \
    update_pr.sh fix/x "$side" "$t/body.md"
  arm "update_pr: a branch whose topic has no handoff/<topic> refuses, naming the ref" noref \
    "update_pr: REFUSE: origin has no handoff/q" update_pr.sh fix/q "$code" "$t/body.md"
  arm "update_pr: branch fix/x-pr, with no handoff/x-pr on origin, is checked against handoff/x" prtopic \
    "update_pr: REFUSE: code sha $side is not an ancestor of origin/handoff/x ($code)" \
    update_pr.sh fix/x-pr "$side" "$t/body.md"
  arm "update_pr: a failing step past the checks (fetching an absent branch) reports itself through the ERR trap" trap \
    "update_pr: STOPPED: line" update_pr.sh fix/x-absent - "$t/body.md"
  # reap: end every lock holder a fixture run recorded under $t (a mutant's may never exit), by
  # the holder pid its lock file names -- never pid 0 or 1, which kill reads as a group.
  reap() {
    local l h
    for l in $(find "$t" -name 'upd-*.lock' 2>/dev/null); do
      h=$(cut -d' ' -f2 "$l" 2>/dev/null); case $h in ''|0|1|*[!0-9]*) ;; *) kill "$h" 2>/dev/null ;; esac
    done
  }
  # One run per branch (the 2026-10-19/20 worktree vanish): update_pr.sh's fixed per-branch
  # worktree was force-removed under a concurrent run's prepr. lockrun <mutant> <hold: 1|0>
  # registers that worktree with a file in it (the in-flight run's), holds -- or, at 0, leaves
  # behind a dead pid in -- the branch's lock, and runs update_pr.sh on the branch.
  lockrun() {
    local s=$t/s$((i + 1)) hp="" k=0
    rm -f "$t/held"; mkdir -p "$s/pr"
    git -C "$m" worktree add -q --detach "$s/pr/upd-fix-x" && touch "$s/pr/upd-fix-x/live"
    if [ "$2" = 1 ]; then
      python3 -I -c 'import fcntl, os, sys, time; f = open(sys.argv[1], "a"); fcntl.flock(f, fcntl.LOCK_EX); f.write("%d 0\n" % os.getpid()); f.flush(); open(sys.argv[2], "w").close(); time.sleep(120)' \
        "$s/pr/upd-fix-x.lock" "$t/held" & hp=$!
      while [ ! -e "$t/held" ] && [ $k -lt 200 ]; do sleep 0.1; k=$((k + 1)); done
    else echo 99999 > "$s/pr/upd-fix-x.lock"; fi
    cp "$t/body.md" "$t/b.md"; run "$1" update_pr.sh fix/x - "$t/b.md"
    [ -z "$hp" ] || { kill "$hp" 2>/dev/null; wait "$hp" 2>/dev/null; }
    reap
    [ -e "$s/pr/upd-fix-x/live" ] && echo 1 > "$t/live" || echo 0 > "$t/live"
  }
  lockrun - 1
  [ "$(cat "$t/rc")" = 75 ] && grep -qF "update_pr: BUSY: another update_pr.sh run" "$t/out" \
    && [ "$(cat "$t/live")" = 1 ] && ! grep -q STOPPED "$t/out"
  ck "update_pr: a branch whose update is in flight refuses BUSY (75) and leaves that run's worktree in place" $?
  lockrun lock 1
  ! grep -qF "update_pr: BUSY" "$t/out" && [ "$(cat "$t/live")" = 0 ]
  ck "  mutant mut:lock (its line deleted) removes the in-flight run's worktree" $?
  lockrun - 0
  [ "$(cat "$t/rc")" != 0 ] && ! grep -qF "update_pr: BUSY" "$t/out" \
    && grep -qF "update_pr: REFUSE: the push failed" "$t/out" && ! grep -q STOPPED "$t/out"
  ck "null control: a lock left by a dead run (the kernel freed it) does not block; the run reaches its push" $?
  # The lock dies with the run, whatever the run started (#2469's round-1 review: an fd of the
  # run's shell was inherited by a `git gc --auto` git detached, which held the lock afterwards).
  # detrun <mutant>: two runs on fix/x in ONE state directory, one after the other; during the
  # first, a post-checkout hook (git runs it at `worktree add`) leaves a detached child behind.
  detrun() {
    local sd=$t/sd-$1 g hk=$m/.git/hooks/post-checkout
    rm -rf "$t/s$i"; git -C "$m" worktree prune  # the last run's worktree holds fix/x
    for g in open_pr.sh update_pr.sh delivery_row.sh pr_args.sh pr_cap.py; do
      if [ "$1" = - ]; then cp "$src/$g" "$m/tools/audit/seat/$g"
      else grep -v "# mut:$1\$" "$src/$g" > "$m/tools/audit/seat/$g"; fi
    done
    printf '#!/bin/sh\nsleep 30 </dev/null >/dev/null 2>&1 &\necho $! >> "%s/sleepers"\n' "$t" > "$hk"; chmod +x "$hk"
    cp "$t/body.md" "$t/b.md"; HPO_STATE_DIR=$sd bash "$m/tools/audit/seat/update_pr.sh" fix/x - "$t/b.md" > "$t/out1" 2>&1
    if kill -0 "$(cut -d' ' -f2 "$sd/pr/upd-fix-x.lock")" 2>/dev/null; then echo 1 > "$t/hold1"; else echo 0 > "$t/hold1"; fi
    rm -f "$hk"; git -C "$m" worktree remove --force "$sd/pr/upd-fix-x" 2>/dev/null
    cp "$t/body.md" "$t/b.md"; HPO_STATE_DIR=$sd bash "$m/tools/audit/seat/update_pr.sh" fix/x - "$t/b.md" > "$t/out" 2>&1
    echo $? > "$t/rc"
    [ -s "$t/sleepers" ] && kill $(cat "$t/sleepers") 2>/dev/null; rm -f "$t/sleepers"
    reap
    git -C "$m" worktree remove --force "$sd/pr/upd-fix-x" 2>/dev/null; rm -rf "$sd"
  }
  detrun -
  grep -qF "update_pr: REFUSE: the push failed" "$t/out1" && ! grep -qF "update_pr: BUSY" "$t/out" \
    && grep -qF "update_pr: REFUSE: the push failed" "$t/out" && ! grep -q STOPPED "$t/out"
  ck "update_pr: a child the run left detached does not hold the lock; the next run on the branch reaches its push" $?
  [ "$(cat "$t/hold1")" = 0 ]
  ck "update_pr: the lock holder has exited by the time a run returns" $?
  detrun unlock; [ "$(cat "$t/hold1")" = 1 ]
  ck "  mutant mut:unlock (its line deleted): the holder is still alive when the run returns" $?
  # A stopped run reaps its whole descendant tree (R10-PUSHER-REAP): branch fix/t
  # carries the same stub app_push, so a TERM is judged by what survives it.
  # SIGKILL runs no trap, so that arm checks only the lock, which the holder
  # frees when its parent dies. Every wait is on a condition with a bound.
  # stoprun <mutant> <signal>: run 1 gets the signal mid-push.
  if [ ! -e "$t/fixt" ]; then
    git -C "$o" checkout -q -b fix/t "$base" && mkdir -p "$o/tools/pr" \
      && cp "$REAP_DIR/reap-stub.sh" "$o/tools/pr/app_push.sh" \
      && git -C "$o" add tools/pr/app_push.sh && git -C "$o" commit -q -m stub && git -C "$o" checkout -q main && touch "$t/fixt"
  fi
  updt() { cp "$t/body.md" "$t/b$1.md"; HPO_STATE_DIR=$2 bash "$m/tools/audit/seat/update_pr.sh" fix/t - "$t/b$1.md" > "$t/out$1" 2>&1; }
  stoprun() { # <mutant> <signal>
    local sd=$t/st-$1-$2 up k=0 hp
    rm -rf "$t/s$i"; git -C "$m" worktree prune
    rm -f "$REAP_DIR/started" "$REAP_DIR/fast" "$REAP_DIR/ok" "$t/out2" "$t/out3"; : > "$REAP_DIR/pids"
    copyin "$1"
    cp "$t/body.md" "$t/b1.md"  # run 1 is update_pr.sh itself, so the signal reaches it, not a subshell
    HPO_STATE_DIR=$sd bash "$m/tools/audit/seat/update_pr.sh" fix/t - "$t/b1.md" > "$t/out1" 2>&1 & up=$!
    while [ "$(wc -l < "$REAP_DIR/pids")" -lt 4 ] && [ $k -lt 600 ]; do sleep 0.05; k=$((k + 1)); done
    hp=$(cut -d' ' -f2 "$sd/pr/upd-fix-t.lock" 2>/dev/null || :)
    case $hp in ''|0|1|*[!0-9]*) echo 0 > "$t/held" ;; *) kill -0 "$hp" 2>/dev/null && echo 1 > "$t/held" || echo 0 > "$t/held" ;; esac
    kill -"$2" "$up"
    k=0; while kill -0 "$up" 2>/dev/null && [ $k -lt 40 ]; do sleep 0.1; k=$((k + 1)); done
    kill -0 "$up" 2>/dev/null && echo alive > "$t/pusher" || echo gone > "$t/pusher"
    ralive "$REAP_DIR/pids" > "$t/survivors"
    kill -0 "$UNREL" 2>/dev/null && echo alive > "$t/unrel" || echo gone > "$t/unrel"
    touch "$REAP_DIR/fast"  # every later run's stub exits at once
    updt 2 "$sd"; wait "$up" 2>/dev/null; updt 3 "$sd"
    rclean
    git -C "$m" worktree remove --force "$sd/pr/upd-fix-t" 2>/dev/null; rm -rf "$sd"
  }
  took_lock() { ! grep -qF "update_pr: BUSY" "$t/out3" && grep -qF "update_pr: REFUSE: the push failed" "$t/out3"; }
  stoprun - TERM
  ck "update_pr: TERM reaps the whole descendant tree, and the pusher is gone" \
     "$( [ "$(cat "$t/pusher")" = gone ] && [ "$(cat "$t/survivors")" = 0 ] && echo 0 || echo 1 )"
  ck "update_pr: the lock is held while the push runs" \
     "$( [ "$(cat "$t/held")" = 1 ] && echo 0 || echo 1 )"
  ck "update_pr: after the stop the lock is free, so the next run takes it" \
     "$( ! grep -qF "update_pr: BUSY" "$t/out2" && took_lock && echo 0 || echo 1 )"
  stoprun stop TERM
  ck "  mutant mut:stop (the reap's kill line deleted): the pusher dies and its tree survives" \
     "$( [ "$(cat "$t/survivors")" -gt 0 ] && echo 0 || echo 1 )"
  stoprun - KILL
  ck "update_pr: a SIGKILLed run leaves no stale lock; a later run takes it" "$( took_lock && echo 0 || echo 1 )"
  stoprun watch TERM
  ck "  mutant mut:watch (the holder's wait line deleted): the holder exits at once, so it is not held during the push" \
     "$( [ "$(cat "$t/held")" = 0 ] && echo 0 || echo 1 )"
  stopok() { # the null control: a run that succeeds leaves nothing behind
    local sd=$t/okrun
    rm -rf "$sd"; git -C "$m" worktree prune; rm -f "$REAP_DIR/started" "$REAP_DIR/fast"
    : > "$REAP_DIR/pids"; : > "$REAP_DIR/ok"; cp "$t/body.md" "$t/b.md"
    copyin -
    HPO_STATE_DIR=$sd bash "$m/tools/audit/seat/update_pr.sh" fix/t - "$t/b.md" > "$t/out" 2>&1
    echo $? > "$t/rc"
    rm -f "$REAP_DIR/ok"
    ralive "$REAP_DIR/pids" > "$t/survivors"
    kill -0 "$UNREL" 2>/dev/null && echo alive > "$t/unrel" || echo gone > "$t/unrel"
    git -C "$m" worktree remove --force "$sd/pr/upd-fix-t" 2>/dev/null; rm -rf "$sd"
  }
  stopok
  ck "null control: a normal successful update_pr leaves nothing behind and stops nothing it did not start" \
     "$( [ "$(cat "$t/rc")" = 0 ] && [ "$(cat "$t/survivors")" = 0 ] && [ "$(cat "$t/unrel")" = alive ] && echo 0 || echo 1 )"
  for c in "$code" -; do
    cp "$t/body.md" "$t/b.md"; run - update_pr.sh fix/x "$c" "$t/b.md"
    [ "$(cat "$t/rc")" != 0 ] && ! grep -q 'REFUSE: code sha\|REFUSE: origin has\|argument(s)' "$t/out" \
      && grep -qF "update_pr: REFUSE: the push failed" "$t/out" && ! grep -q STOPPED "$t/out"
    ck "null control: update_pr with code sha '${c:0:7}' passes every check, and its failed push names its log" $?
  done
  # The cap's own counting rule, which orchestrator_tick.py imports too.
  python3 -I "$src/pr_cap.py" --self-test > "$t/cap.out" 2>&1 && grep -q 'pr_cap self-test: [1-9][0-9]* checks, 0 failed' "$t/cap.out"
  ck "pr_cap.py --self-test: its tally says 0 failed" $?
  reap
  kill "$UNREL" 2>/dev/null; wait "$UNREL" 2>/dev/null || :
  rm -rf "$t"
  echo "pr_args self-test: $n checks, $f failed"
  [ "$f" = 0 ]
)

if [ "${BASH_SOURCE[0]}" = "$0" ]; then
  case ${1:-} in
    --self-test) pr_args_self_test; exit ;;
    *) sed -n '2,6p' "$0" >&2; exit 2 ;;
  esac
fi
