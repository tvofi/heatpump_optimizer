# usage: run_mutants.sh <tree> <evdir>; for each plant: self-test, finder reap_probe, finder launch_probe, my reap_fail_probe
T=$1; E=$2
NAMES="R-reap-nostem old-launch R-open-rc-nostem R-open-log-nostem R-stem-noop R-shift1 R-unquoted-log R-argv-swap R-reap-log-ok R-fail-log-nostem R-reap-alive-dead R-reap-rc-empty"
for n in M0 $NAMES; do
  X=$(mktemp -d); python3 -I $E/mk3.py $T $X/t $n >/dev/null || { echo "ABORT $n"; continue; }
  S=$X/t/tools/audit/seat
  st=$(python3 -I $S/open_driver.py --self-test 2>&1); src=$?
  sf=$(printf '%s\n' "$st" | grep -c '^FAIL ')
  fl=$(printf '%s\n' "$st" | grep '^FAIL ' | tr '\n' ';')
  rp=$(python3 -I $E/finder_reap_probe.py $S 2>&1 | tail -1)
  lp=$(python3 -I $E/finder_launch_probe.py $S 2>&1 | tail -1)
  fp=$(python3 -I $E/reap_fail_probe.py $S 2>&1 | tail -1)
  echo "RESULT mutant=$n selftest_rc=$src selftest_failed=$sf [$rp] [$lp] [$fp] $fl"
  rm -rf $X
done
