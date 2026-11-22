# reviewer's mutation driver: python-literal replace, run, restore
cd $HOME/wt; P=custom_components/heatpump_optimizer
m() { name=$1 file=$2 old=$3 new=$4; shift 4
  python3 - "$file" "$old" "$new" <<'PY' || { echo "$name NOAPPLY"; return; }
import sys; f,o,n=sys.argv[1:]; s=open(f).read(); assert s.count(o)==1, s.count(o); open(f,'w').write(s.replace(o,n))
PY
  out=$("$@" 2>&1); rc=$?; git checkout -q -- $file
  echo "$name rc=$rc $(echo "$out" | grep -E '^ *FAIL|Error|PASSED|FAILED' | head -2 | tr '\n' ' ' | cut -c1-300) porcelain=[$(git status --porcelain | tr '\n' ' ')]"
}
OM="env PYTHONPATH=tests/hastub python3 tests/open_meteo.py"
WA="env PYTHONPATH=tests/hastub python3 tests/wood_advisor.py"
echo "CLEAN open_meteo: $($OM 2>&1 | tail -1)"; echo "CLEAN wood_advisor: $($WA 2>&1 | tail -1)"
m M1-kept-all $P/open_meteo.py "if t >= floor]" "if True]" $OM
m M2-lt1 $P/open_meteo.py "if len(kept) < 2:" "if len(kept) < 1:" $OM
m M3-floor-noresolution $P/open_meteo.py "utc_instant(datetime.min) + resolution" "utc_instant(datetime.min)" $OM
m M4-lead-finite $P/entry_config.py "_key(const.DEFAULT_WOOD_LIGHTING_LEAD_MINUTES, _lead_minutes)" "_key(const.DEFAULT_WOOD_LIGHTING_LEAD_MINUTES, finite_float)" $WA
m M5-lead-noceil $P/entry_config.py "not 0.0 <= minutes <= _MAX_PLAN_MINUTES" "not 0.0 <= minutes" $WA
m M6-lead-strictfloor $P/entry_config.py "not 0.0 <= minutes <= _MAX_PLAN_MINUTES" "not 0.0 < minutes <= _MAX_PLAN_MINUTES" $WA
FB="python3 tools/audit/seat/features_block.py"
FB() { env PYTHONPATH=tests/hastub python3 tools/audit/seat/features_block.py --prelude "exec(open('/root/rv/pre.py').read())" 'R.section("Non-numeric inputs (v5.3.0)")' 'R.section("Heat pump operating mode (v5.3.0)")'; }
echo "CLEAN features-block: $(FB 2>&1 | tail -1)"
m M7-parse_bool-revert $P/inputs.py "    number = finite_float(token)
    return None if number is None else number != 0.0" "    try:
        return float(token) != 0.0
    except (TypeError, ValueError):
        return None" FB
m M8-begin-guard-off $P/inputs.py "        if not isinstance(entity_id, str):
            entity_id = None" "        if False:
            entity_id = None" FB
m M9-plausible-onesided $P/inputs.py "window[0] <= value_c <= window[1]" "window[0] <= value_c" FB
