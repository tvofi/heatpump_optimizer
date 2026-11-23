W=$HOME/audit-r11-D3-s1/dev/audit/rounds/round11/D3/s1/wave/D3-g01
grep -E 'VERDICT|CMD|GATES-DONE|RUN-EXIT|Error|REFUSE' $HOME/logs/run.log | tail -3
for j in $W/gates/*.json; do k=$(basename $j .json); [ "$k" = null ] && continue
  [ -f $W/results/$k.json ] && continue
  python3 -c "import json;d=json.load(open('$j'));print('$k',d['verdict'],d.get('killed_by'),d.get('fail_lines'),d.get('wall_s'))"
  python3 $HOME/pt/write_result.py $k
done
bash $HOME/gate_wave.sh ckpt; echo ckpt-rc=$?; bash $HOME/gate_wave.sh status
