set -u
H=/tmp/hpo-rev-3930/wt/dev/audit/rounds/round11
for side in base wt; do
  cd /tmp/hpo-rev-3930/$side
  echo "##### $side $(git rev-parse HEAD)"
  for spec in "D1/s2/weather_stuck.py" "D1/s2/weather_stuck.py --advancing" "D1/s2/pv_stale.py" "D1/s2/pv_stale.py --fresh" "D14/s2/staleness_flags.py" "D1/leads/humidity_reader_settings.py" "D1/s3/parsers_fuzz.py --arm ecl110"; do
    set -- $spec
    f=$1; shift
    echo "== $f $*"
    PYTHONPATH=tests/hastub timeout 600 python3 "$H/$f" "$@" 2>&1 | grep -E '[a-z_]+=|RESULT|Error' | tail -12
  done
done
