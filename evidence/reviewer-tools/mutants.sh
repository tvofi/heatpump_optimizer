#!/bin/bash
S=$1; export PATH=$S/bin:$PATH; cd $S/mut || exit 1
CM=tools/audit/archscore/metrics/common.py; HW=tools/audit/archscore/metrics/hub_solve_writes.py
run() { echo "== $1"; PYTHONPATH=tests/hastub python3 $S/tools/spell.py 2>&1 | tail -12; PYTHONPATH=tests/hastub python3 tests/arch_score_head.py 2>&1 | grep -E 'FAIL|passed|failed' | head -4; }
mut() { python3 $S/tools/sub.py "$2" "$3" "$4" || return; run "$1"; git checkout -q -- tools; git status --short tools; }
run M0
mut M1-call-roles $CM "return self._call_roles(e, env, mod, cls, bare) if FOLLOW_RETURNS else EMPTY" "return EMPTY"
mut M2-readers $CM "self.readers.setdefault((t.attr, stores[p]), role[1])" "pass"
mut M3-rebinds $CM "for k, v in self._derive_rebinds().items():" "for k, v in {}.items():"
mut M4-event-roots $HW "if not EVENT_ROOTS or pkg.coord_key not in pkg.classes:" "if True:"
