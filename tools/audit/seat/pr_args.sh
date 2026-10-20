#!/bin/bash
# pr_args.sh -- the argument checks and the stop report open_pr.sh and
# update_pr.sh share, so neither can stop without saying why.
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
pr_trap() { # errexit, and the report of every stop it makes
  set -Eeo pipefail
  trap 'pr_stopped $? $LINENO "$BASH_COMMAND"' ERR  # mut:trap
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
  local src t f=0 n=0 o m base code side body i
  src=$(cd "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
  t=$(mktemp -d) || { echo "pr_args self-test: no temporary directory"; return 1; }
  . "$src/../../../tests/throwaway_git.sh" && throwaway_git_env
  ck() { n=$((n + 1)); if [ "$2" = 0 ]; then echo "  ok   $1"; else f=$((f + 1)); echo "  FAIL $1"; fi; }
  o=$t/o; m=$t/m
  { throwaway_git_init "$o" -q -b main && printf 'a\n' > "$o/a" && git -C "$o" add a \
    && git -C "$o" commit -q -m base && base=$(git -C "$o" rev-parse HEAD) \
    && printf 'b\n' > "$o/b" && git -C "$o" add b && git -C "$o" commit -q -m code \
    && code=$(git -C "$o" rev-parse HEAD) && git -C "$o" branch handoff/x "$code" \
    && git -C "$o" branch handoff/y "$code" \
    && git -C "$o" checkout -q -b side "$base" && printf 'c\n' > "$o/c" && git -C "$o" add c \
    && git -C "$o" commit -q -m side && side=$(git -C "$o" rev-parse HEAD) \
    && git -C "$o" checkout -q main && git -C "$o" reset -q --hard "$base" \
    && git -C "$o" branch fix/x "$base" \
    && printf '## Head\n\nthe body\n' > "$t/body.md" \
    && body=$(git -C "$o" commit-tree "$(printf '100644 blob %s\tBODY.md\n' \
         "$(git -C "$o" hash-object -w "$t/body.md")" | git -C "$o" mktree)" -m "body: x") \
    && git -C "$o" update-ref refs/heads/handoff-body/x "$body" \
    && git -C "$o" update-ref refs/heads/handoff-body/z "$body" \
    && throwaway_git_clone -q "$o" "$m" && mkdir -p "$t/bin" "$m/tools/audit/seat" "$m/tools/pr" \
    && cp "$src/../../pr/head_note.py" "$m/tools/pr/head_note.py" \
    && printf '#!/bin/sh\n[ -e "%s/gh.fail" ] && { echo "HTTP 403" >&2; exit 1; }\ncase "$*" in *--head*) echo 5 ;; "pr list"*) cat "%s/prs.json" ;; "pr view"*) echo "a title" ;; *) exit 99 ;; esac\n' "$t" "$t" > "$t/bin/gh" \
    && echo '[]' > "$t/prs.json" \
    && chmod +x "$t/bin/gh"; } || { echo "  FAIL fixture"; rm -rf "$t"; return 1; }
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
  # The open-PR cap (pr_cap.py; tvofi, 2026-10-18): six counted open is the cap.
  prs() { # <counted> [extra json objects]: the stub's open list
    local k=0 j=""
    while [ $k -lt "$1" ]; do j="$j{\"number\":$k,\"title\":\"t\",\"author\":{\"login\":\"app/hpo-author\",\"is_bot\":true}},"; k=$((k + 1)); done
    printf '[%s%s]\n' "$j" "${2:-}" | sed 's/,]$/]/' > "$t/prs.json"
  }
  prs 6
  arm "open_pr: six counted open pull requests refuse at the cap" cap \
    "open_pr: REFUSE: open-PR cap: 6 open >= 6; drain before opening (HPO_OPEN_PR_CAP, --over-cap <reason>)" \
    open_pr.sh x "$code" T G
  arm "open_pr: the cap is checked by the script itself (the call's lines)" capcall \
    "open_pr: REFUSE: open-PR cap: 6 open >= 6" open_pr.sh x "$code" T G
  touch "$t/gh.fail"
  arm "open_pr: an open list gh cannot read refuses, never passes" capreadrc \
    "open_pr: REFUSE: open-PR cap: the open pull requests could not be read (gh exited 1" open_pr.sh x "$code" T G
  rm -f "$t/gh.fail"
  # passes <name> <mutant> <expected text> <args...>: opens (stops only at the
  # absent push), printing the text; the mutant refuses at the cap instead.
  passes() {
    local nm=$1 mu=$2 want=$3; shift 3
    run - open_pr.sh "$@"; grep -qF -- "$want" "$t/out" && ! grep -q 'REFUSE: open-PR cap' "$t/out" \
      && grep -qF "open_pr: REFUSE: the push failed" "$t/out"
    ck "$nm" $?
    run "$mu" open_pr.sh "$@"; grep -q 'REFUSE: open-PR cap' "$t/out"
    ck "  mutant mut:$mu (its line deleted) refuses at the cap instead" $?
  }
  prs 6
  passes "open_pr: --over-cap opens at the cap and logs its reason" overcap \
    "open_pr: OVER-CAP: 6 open >= 6, overridden: the train is draining" \
    --over-cap "the train is draining" x "$code" T G
  prs 5 '{"number":90,"title":"record: rows","author":{"login":"app/hpo-author","is_bot":true}},{"number":91,"title":"bump","author":{"login":"app/dependabot","is_bot":true}}'
  passes "open_pr: five counted open (a record: and a bot pull request beside them) opens" caprecord \
    "open_pr: open-PR cap: 5 open < 6" x "$code" T G
  passes "open_pr: the same board, the bot pull request uncounted" capbot \
    "open_pr: open-PR cap: 5 open < 6" x "$code" T G
  echo '[]' > "$t/prs.json"
  run - open_pr.sh x "$code" T G
  [ "$(cat "$t/rc")" != 0 ] && ! grep -q 'REFUSE: code sha\|REFUSE: origin has\|argument(s)' "$t/out" \
    && [ "$(git -C "$t/s$i/pr/x/wt" rev-parse HEAD)" = "$code" ] \
    && grep -qF "open_pr: REFUSE: the push failed; its log is $t/s$i/pr/x/p1.log" "$t/out" \
    && ! grep -q STOPPED "$t/out"
  ck "null control: open_pr with the code sha passes every check, and its failed push names its log" $?
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
    rm -f "$hk"; git -C "$m" worktree remove --force "$sd/pr/upd-fix-x" 2>/dev/null
    cp "$t/body.md" "$t/b.md"; HPO_STATE_DIR=$sd bash "$m/tools/audit/seat/update_pr.sh" fix/x - "$t/b.md" > "$t/out" 2>&1
    echo $? > "$t/rc"
    [ -s "$t/sleepers" ] && kill $(cat "$t/sleepers") 2>/dev/null; rm -f "$t/sleepers"
    git -C "$m" worktree remove --force "$sd/pr/upd-fix-x" 2>/dev/null; rm -rf "$sd"
  }
  detrun -
  grep -qF "update_pr: REFUSE: the push failed" "$t/out1" && ! grep -qF "update_pr: BUSY" "$t/out" \
    && grep -qF "update_pr: REFUSE: the push failed" "$t/out" && ! grep -q STOPPED "$t/out"
  ck "update_pr: a child the run left detached does not hold the lock; the next run on the branch reaches its push" $?
  detrun unlock
  grep -qF "update_pr: BUSY" "$t/out"
  ck "  mutant mut:unlock (its line deleted): the holder outlives the run and the next run is BUSY" $?
  for c in "$code" -; do
    cp "$t/body.md" "$t/b.md"; run - update_pr.sh fix/x "$c" "$t/b.md"
    [ "$(cat "$t/rc")" != 0 ] && ! grep -q 'REFUSE: code sha\|REFUSE: origin has\|argument(s)' "$t/out" \
      && grep -qF "update_pr: REFUSE: the push failed" "$t/out" && ! grep -q STOPPED "$t/out"
    ck "null control: update_pr with code sha '${c:0:7}' passes every check, and its failed push names its log" $?
  done
  # The cap's own counting rule, which orchestrator_tick.py imports too.
  python3 -I "$src/pr_cap.py" --self-test > "$t/cap.out" 2>&1 && grep -q 'pr_cap self-test: [1-9][0-9]* checks, 0 failed' "$t/cap.out"
  ck "pr_cap.py --self-test: its tally says 0 failed" $?
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
