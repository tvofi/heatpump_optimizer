#!/bin/bash
# usage: mut.sh  (run in worktree)
export PYTHONPATH=tests/hastub:. PYTHONDONTWRITEBYTECODE=1
RD=custom_components/heatpump_optimizer/replay_doc.py
run(){ echo "## $1"; python3 -I -c "import sys; sys.path[:0]=['tests','tests/hastub','tools/replay','.']; exec(open('$MC').read())" 2>&1 | grep 'RESULT mask_checks'; git checkout -q -- .; }
MC=$1
run "M0 null"
sed -i '533s/if conf is not None and (key not in conf or SECRET_KEY.search(str(key))):/if False:/' $RD; git diff --stat|tail -1; run "M1 :533 key guard GUARD_OFF"
sed -i '533s/if conf is not None and (/if conf is not None or (/' $RD; git diff --stat|tail -1; run "M1b :533 BOOLOP"
sed -i '535s/if conf is not None:/if False:/' $RD; git diff --stat|tail -1; run "M2 :535 _entry_shape guard GUARD_OFF"
sed -i '538s/value = _entry_shape(str(key), value)/pass/' $RD; git diff --stat|tail -1; run "M3 :538 _entry_shape call -> pass"
sed -i '540s/if not isinstance(value, list):/if False:/' $RD; git diff --stat|tail -1; run "M4 :540 list test GUARD_OFF"
sed -i '538s/$/\n            if value is _DROP:\n                continue/' $RD; git diff --stat|tail -1; sed -n 535,542p $RD; run "M5 re-add r2 :537 _DROP skip (equivalence check)"
sed -i '538s/$/\n            if False:\n                continue/' $RD; git diff --stat|tail -1; run "M5b re-added skip as if False (r2 GUARD_OFF form, i.e. head)"
sed -i 's/roles = entity_roles(doc.get("entry") or {}, doc.get("price_series_entity"), conf)/roles = entity_roles(doc.get("entry") or {}, doc.get("price_series_entity"), None)/' $RD; git diff --stat|tail -1; run "M6 mask_ids passes None"
sed -i 's/}, str(entry.get("entry_id") or ""), conf)/}, str(entry.get("entry_id") or ""))/' $RD; git diff --stat|tail -1; run "M7 document drops conf"
sed -i '/^        conf=conf,$/d' custom_components/heatpump_optimizer/debugger.py; git diff --stat|tail -1; run "M8 debugger.py conf=conf deleted"
sed -i 's/price_series_entity=price_entity, states=states, conf=conf,/price_series_entity=price_entity, states=states,/' tools/replay/export.py; git diff --stat|tail -1; run "M9 export.py conf=conf deleted"
