#!/bin/bash
# usage: plants.sh <worktree> <outfile>
cd "$1" || exit 2; F=custom_components/heatpump_optimizer/config_flow.py; H=$(git rev-parse HEAD)
run(){ python3 -I tools/audit/check_scopes.py --repo . --ref "$1" --population 2>&1 | grep -E 'tank_volume|house_size|NO-READ|UNREADABLE'; echo "rc=${PIPESTATUS[0]}"; }
plant(){ name=$1; git checkout -q --detach $H; python3 - "$F" "$2" "$3" <<'EOF'
import sys;p=sys.argv[1];s=open(p).read();o,n=sys.argv[2],sys.argv[3];assert o in s,o;open(p,'w').write(s.replace(o,n,1))
EOF
git -c user.name=r -c user.email=r@x commit -qam "plant $name" --no-verify; echo "== $name"; run HEAD; git checkout -q --detach $H; }
{ echo "== clean at $H"; run HEAD
plant P3-Farg 'CONF_DHW_TANK_VOLUME, DEFAULT_DHW_TANK_VOLUME, _number' 'CONF_DHW_TANK_VOLUME, 300.0, _number'
plant P4-qdict 'CONF_HEATED_AREA: DEFAULT_HEATED_AREA,' 'CONF_HEATED_AREA: 180.0,'
plant P6-presence '    CONF_DHW_TANK_VOLUME: DEFAULT_DHW_TANK_VOLUME,
}' '    CONF_DHW_TANK_VOLUME: 250.0,
}'
plant P7-wizard-hl 'CONF_HOUSE_HEAT_LOSS_COEFFICIENT: DEFAULT_HOUSE_HEAT_LOSS_COEFFICIENT,' 'CONF_HOUSE_HEAT_LOSS_COEFFICIENT: 0.2,'
plant P9-wizard-tank '                            CONF_DHW_TANK_VOLUME: DEFAULT_DHW_TANK_VOLUME,' '                            CONF_DHW_TANK_VOLUME: 220.0,'
plant P8-suggested 'CONF_HOUSE_HEAT_LOSS_COEFFICIENT, _SUGGESTED,' 'CONF_HOUSE_HEAT_LOSS_COEFFICIENT, 0.3,'
plant N1-same 'CONF_DHW_TANK_VOLUME, DEFAULT_DHW_TANK_VOLUME, _number' 'CONF_DHW_TANK_VOLUME, 200.0, _number'
plant N2-step 'CONF_HEATED_AREA: _number(20, 1000, 5,' 'CONF_HEATED_AREA: _number(20, 1000, 10,'
plant X1-subscript '_DHW_PRESENCE_PAIR_DEFAULTS: Final = {' '_X: dict = {}
_X[CONF_DHW_TANK_VOLUME] = 300.0
_DHW_PRESENCE_PAIR_DEFAULTS: Final = {'
plant X2-get-or '_DHW_PRESENCE_PAIR_DEFAULTS: Final = {' '_X = lambda d: d.get(CONF_DHW_TANK_VOLUME) or 300.0
_DHW_PRESENCE_PAIR_DEFAULTS: Final = {'
plant X3-kwkey '_DHW_PRESENCE_PAIR_DEFAULTS: Final = {' '_X = _F("t", key=CONF_DHW_TANK_VOLUME, default=300.0)
_DHW_PRESENCE_PAIR_DEFAULTS: Final = {'
plant X4-setdefault '_DHW_PRESENCE_PAIR_DEFAULTS: Final = {' '_X = lambda d: d.setdefault(CONF_DHW_TANK_VOLUME, 300.0)
_DHW_PRESENCE_PAIR_DEFAULTS: Final = {'
} > "$2" 2>&1
git checkout -q --detach $H; git status --short | head
