#!/bin/bash
# review-2067's own harness (reviewer-built; the finder committed none for the
# floor/trap arms). Cheap: stubs df, never fills the disk.
set -u
WT=/Users/timmalmstrom/hpo-seats/review-2067/wt
EV=/Users/timmalmstrom/hpo-seats/review-2067/evidence
P=$WT/tools/pr/prepr.sh
cd "$WT" || exit 9
fns="$(sed -n '/^SELFTEST_PEAK_KB=/p;/^tmp_floor_check() {/,/^}/p;/^selftest_tmp_root() {/,/^}/p' "$P")"
mkstub() { # dir avail-field
  mkdir -p "$1"; cat > "$1/df" <<S
#!/bin/sh
printf 'Filesystem 1024-blocks Used Available Capacity Mounted on\n/dev/stub 999 999 $2 100%% /\n'
S
  chmod +x "$1/df"; }

echo "== A. floor, planted low space, the REAL entry (df stubbed)"
for av in 1000 446247; do
  T=$EV/tmpA.$av; rm -rf "$T"; mkdir -p "$T"; mkstub "$EV/stubA.$av" "$av"
  s=$(date +%s); out=$(PATH="$EV/stubA.$av:$PATH" TMPDIR="$T" bash "$P" --self-test 2>&1); rc=$?; e=$(( $(date +%s)-s ))
  echo "RESULT floor-low avail=${av}KB rc=$rc secs=$e lines=$(printf '%s\n' "$out"|wc -l|tr -d ' ') FAIL_rows=$(printf '%s\n' "$out"|grep -c '^  FAIL') tmp_entries=$(ls -A "$T"|wc -l|tr -d ' ')"
  printf '%s\n' "$out" | sed 's/^/   | /' | tail -3
done
echo "== A2. boundary + unmeasurable, function alone (stubbed df)"
for av in 446247 446248 garbage ''; do
  mkstub "$EV/stubB" "$av"
  out=$(PATH="$EV/stubB:$PATH" bash -c "$fns"'; tmp_floor_check /x $((2*SELFTEST_PEAK_KB))'); rc=$?
  echo "RESULT floor-fn avail='${av}' rc=$rc out=$(printf '%s' "$out"|cut -c1-60)"
done
echo "== A3. null control: real df, real TMPDIR, default floor"
out=$(bash -c "$fns"'; tmp_floor_check "${TMPDIR:-/tmp}" $((2*SELFTEST_PEAK_KB))'); echo "RESULT floor-real rc=$? df_avail=$(df -Pk "${TMPDIR:-/tmp}"|awk 'NR==2{print $4}')"

echo "== B. trap: every exit path (set -m: an async job in a non-job-control shell starts with INT/QUIT ignored, which a trap cannot undo -- a harness artefact, not the PR's)"
set -m
run_path() { # name body
  T=$EV/tmpB.$1; rm -rf "$T"; mkdir -p "$T"
  TMPDIR="$T" bash -c "$fns"'
selftest_tmp_root || exit 9
d=$(mktemp -d); mkdir "$d/clone"; head -c 100000 /dev/zero > "$d/clone/blob"; echo "$ST_ROOT" > '"$EV"'/root.'"$1"'
'"$2" >/dev/null 2>&1 &
  pid=$!; sleep 1
  case $1 in
    sigterm) kill -TERM $pid ;; sighup) kill -HUP $pid ;; sigint) kill -INT $pid ;;
    sigkill) kill -KILL $pid ;; sigquit) kill -QUIT $pid ;; sigusr1) kill -USR1 $pid ;;
    sigterm-child) kill -TERM $pid ;; pgrp-int) kill -INT -- -$pid 2>/dev/null || kill -INT $pid ;;
  esac
  for i in $(seq 1 60); do kill -0 $pid 2>/dev/null || break; sleep 0.1; done
  kill -0 $pid 2>/dev/null && { kill -KILL $pid; echo "RESULT trap path=$1 HUNG (killed)"; }
  wait $pid; rc=$?; sleep 0.3
  echo "RESULT trap path=$1 rc=$rc leftover=$(ls -A "$T"|wc -l|tr -d ' ')"
}
run_path normal 'sleep 2; exit 0'
run_path error  'sleep 2; exit 2'
run_path seterr 'set -e; sleep 2; false; echo unreachable'
run_path sigterm 'while :; do sleep 0.1; done'
run_path sighup  'while :; do sleep 0.1; done'
run_path sigint  'while :; do sleep 0.1; done'
run_path sigterm-child 'sleep 3; while :; do sleep 0.1; done'
run_path sigquit 'while :; do sleep 0.1; done'
run_path sigusr1 'while :; do sleep 0.1; done'
run_path sigkill 'while :; do sleep 0.1; done'
echo "== B2. subshell exit inside the run does not fire the trap early"
T=$EV/tmpB2; rm -rf "$T"; mkdir -p "$T"
TMPDIR="$T" bash -c "$fns"'
selftest_tmp_root; ( exit 3 ); x=$(exit 4); [ -d "$ST_ROOT" ] && echo alive || echo GONE' | sed 's/^/RESULT subshell root=/'
echo "== B3. SIGPIPE on the self-test writer (prepr --self-test | head -1 shape)"
T=$EV/tmpB3; rm -rf "$T"; mkdir -p "$T"
TMPDIR="$T" bash -c "$fns"'
selftest_tmp_root; while :; do echo line; done' | head -1 >/dev/null; sleep 0.3
echo "RESULT trap path=sigpipe leftover=$(ls -A "$T"|wc -l|tr -d ' ')"
