W=$(cat ~/W)
for m in "$@"; do
  (cd $W/$m && PYTHONPATH=tests/hastub timeout 3600 python3 tests/features.py > $W/ev/features-$m.log 2>&1; echo "rc=$?" >> $W/ev/features-$m.log)
done
