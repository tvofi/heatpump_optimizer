# reviewer's mutation driver (built by the reviewer): python-literal replace, run the
# "Config entry migration" section of tests/entities.py (header lines 1-148 + section
# 15627-15951 + R.close, extracted at the head into tests/_rv_mig_block.py), restore.
cd $HOME/wt; P=custom_components/heatpump_optimizer/entry_config.py
T="env PYTHONPATH=tests/hastub python3 tests/_rv_mig_block.py"
m() { name=$1 old=$2 new=$3
  python3 - "$P" "$old" "$new" <<'PY' || { echo "$name NOAPPLY"; return; }
import sys; f,o,n=sys.argv[1:]; s=open(f).read(); assert s.count(o)==1, s.count(o); open(f,'w').write(s.replace(o,n))
PY
  out=$($T 2>&1); rc=$?; git checkout -q -- $P
  echo "$name rc=$rc $(echo "$out" | grep -E '^ *FAIL|Error|PASSED|FAILED' | head -3 | tr '\n' ' ' | cut -c1-400) porcelain=[$(git status --porcelain -uno | tr '\n' ' ')]"
}
echo "CLEAN rc: $($T >/dev/null 2>&1; echo $?) $($T 2>&1 | tail -1)"
m M1-whole-not-defaulted "_lead_minutes, _whole,
)" "_lead_minutes,
)"
m M2-old-finite_float 'f.name: None if value is None else f.metadata["parse"](value, f.default)' 'f.name: finite_float(value)'
m M3-none-stored-as-default 'f.name: None if value is None else f.metadata["parse"](value, f.default)' 'f.name: f.metadata["parse"](value, f.default)'
m M4-float-default-parse 'f.name: None if value is None else f.metadata["parse"](value, f.default)' 'f.name: None if value is None else finite_float(value, f.default)'
m M5-drop-heated_area "    heated_area_m2: float = _key(const.DEFAULT_HEATED_AREA, finite_float)
" ""
m M6-drop-wood_price "    wood_price_sek_m3: float | None = _key(None, finite_float)
" ""
m M7-repaired-keeps-None "        if key not in repairs or repairs[key] is not None
" "        if True
"
m M8-drop-day_start_hour_weekend "    day_start_hour_weekend: int | None = _key(None, _whole)
" "    day_start_hour_weekend: int | None = _key(None, _as_stored)
"
m M9-bool-not-repaired "and (isinstance(value := stored[f.name], bool) or not isinstance(value, (int, float)))" "and not isinstance(value := stored[f.name], (int, float))"
