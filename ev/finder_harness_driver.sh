E=$HOME/rv/export/dev/audit/rounds/round11
for side in wtb wt; do
  cd $HOME/rv/$side; o=$HOME/rv/ev/harness_$side.txt; : > $o
  echo "== tree $(git rev-parse HEAD)" >> $o
  (HASTUB_TZ=Europe/Stockholm PYTHONPATH=tests/hastub timeout 900 python3 $E/D2/s3/m4_tariff.py 2>&1 | grep RESULT) >> $o
  (PYTHONPATH=tests/hastub timeout 900 python3 $E/D7/s3/m8_agree.py --only temperature_roundtrip 2>&1 | grep RESULT) >> $o
  for arm in pump openmeteo; do (PYTHONPATH=tests/hastub timeout 900 python3 $E/D1/s3/parsers_fuzz.py --arm $arm 2>&1 | grep RESULT) >> $o; done
  (PYTHONPATH=tests/hastub timeout 900 python3 $E/D1/leads/plausible_upper.py 2>&1 | grep RESULT) >> $o
  for n in 1 2 3 4 5 6; do (PYTHONPATH=tests/hastub:tests timeout 1500 python3 $E/D1/s2/config_fuzz.py --versions $n 2>&1 | grep -E "RESULT|Traceback|Error") >> $o; done
  echo "== done" >> $o
done
