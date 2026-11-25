# step2.sh: for each gate record lacking a result: run its probe on this container, write the record, checkpoint
W=$HOME/audit-r11-D3-s1/dev/audit/rounds/round11/D3/s1/wave/D3-g01
cd $HOME/audit-r11-D3-s1
for j in $W/gates/*.json; do k=$(basename $j .json); [ "$k" = null ] && continue
  [ -f $W/results/$k.json ] && continue
  python3 -c "import json;d=json.load(open('$j'));print('$k',d['verdict'],d.get('killed_by'),d.get('fail_lines'),d.get('wall_s'))"
  PYTHONPATH=tests/hastub $HOME/venv-ci/bin/python3 $W/probes/probe_$k.py 2>&1 | grep RESULT | head -12
  GATE_CPU=2.30GHz PYTHONPATH=tests/hastub $HOME/venv-ci/bin/python3 $HOME/pt/write_result.py $k
done
bash $HOME/gate_wave.sh ckpt; echo ckpt-rc=$?; bash $HOME/gate_wave.sh status
