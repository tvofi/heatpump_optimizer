#!/bin/bash
# Reviewer mutants against the head's declared-cost check; tree restored after each.
T=$1; P=$2
cd $T
st=custom_components/heatpump_optimizer/store.py; dr=custom_components/heatpump_optimizer/draw_range.py
run() { name=$1; shift; "$@"; git -C $T diff --stat | tail -1;
  out=$(timeout 200 python3 $P $T 2>&1 | grep -E "declared cost|FAILED-ATTR|Error" | cut -c1-260)
  if echo "$out" | grep -q "FAILED-ATTR failures 0"; then v=SURVIVED; else v=KILLED; fi
  echo "$name: $v"; echo "$out" | sed 's/^/    /'; git -C $T checkout -q -- .; }
run M1_floor_kw_whole_readded sed -i 's|"draw/floor_kw": Domain("real", _POS),|"draw/floor_kw": Domain("real", _POS, whole=_DRAW_KEY),|' $st
run M2_floor_since_whole_readded sed -i 's|"draw/floor_since": _COUNT,|"draw/floor_since": Domain("int", 0, whole=_DRAW_KEY),|' $st
run M3_bad_floor_kw_drops_record sed -i 's|^        out.floor_kw, out.floor_since = _stored_floor(data, lo, len(out.samples))|        if not isinstance(data.get("floor_kw", 0.0), (int, float)): return cls()\n&|' $dr
run M4_bad_floor_since_drops_record sed -i 's|^        out.floor_kw, out.floor_since = _stored_floor(data, lo, len(out.samples))|        if type(data.get("floor_since", 0)) is not int or data.get("floor_since", 0) < 0: return cls()\n&|' $dr
run M5_since_never_restored sed -i 's|(min(max(since, 0), rows) if type(since) is int else 0)|0|' $dr
run M6_bool_floor_accepted sed -i 's|isinstance(raw, (int, float)) and not isinstance(raw, bool)|isinstance(raw, (int, float))|' $dr
git -C $T status --short | head
