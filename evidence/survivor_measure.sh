set -e
O=custom_components/heatpump_optimizer/optimizer.py
cp $O /tmp/claude-0/opt.bak
apply(){ python3 - "$1" "$2" <<'PY'
import sys,pathlib
p=pathlib.Path("custom_components/heatpump_optimizer/optimizer.py");s=p.read_text();old,new=sys.argv[1],sys.argv[2]
assert s.count(old)==1; p.write_text(s.replace(old,new))
PY
}
echo "== P7 humidity ignored"; apply '    humidity = None if weather.humidity is None else float(weather.humidity[0])' '    humidity = None'
python3 $1/wood.py | grep -c '^DRAW' || true; python3 $1/wood.py | grep '^DRAW' | sort -t' ' -k10 | head -4
cp /tmp/claude-0/opt.bak $O
echo "== P8 made->need_kw"; apply '    return bool(power_for_heat_per_cop_kw(p, made / cop) > p.max_electrical_power)' '    return bool(power_for_heat_per_cop_kw(p, need_kw / cop) > p.max_electrical_power)'
python3 $1/wood.py | grep -c '^DRAW' || true; python3 $1/probe2.py | head -4
cp /tmp/claude-0/opt.bak $O
git status --short
