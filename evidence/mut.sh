#!/bin/bash
# mut.sh <wt> <scratch>: ablation arms and mutants M1-M5 on the nine new calibration cases, restoring after each.
set -u
WT=$1; S=$2; cd $WT
export PATH=$S/bin:$PATH PYTHONPATH=tests/hastub
L=tools/audit/archscore/metrics/layering.py
NINE=a3_layer_violations_control,a3_layer_violations_fix,a3_layer_violations_null,a3_private_cross_module_control,a3_private_cross_module_fix,a3_private_cross_module_null,rt_21_lazy_solver_import,rt_22_private_module_attr,rt_23_layer_owner_import
run() { # name
  python3 tools/audit/archscore/calibrate.py --only $NINE --jobs 4 > $S/evidence/arm_$1.txt 2>&1; rc=$?
  echo "== $1 rc=$rc"; grep -E "^(a3_|rt_2[123])" $S/evidence/arm_$1.txt | awk '{print "  ",$1,$4,$6}'; grep "^MOVED" $S/evidence/arm_$1.txt | grep -v "now None" | sed 's/^/   /'
}
mutate() { python3 - $L "$1" "$2" <<'PY'
import sys; p, old, new = sys.argv[1:]; s = open(p).read(); assert s.count(old) == 1, old; open(p, "w").write(s.replace(old, new))
PY
}
run M0_none
for c in C17 C18 C19; do ARCHSCORE_ABLATE=$c run ablate_$c; done
mutate 'live = None if ALL_SCOPES else _module_level(mod.tree)' 'live = _module_level(mod.tree)'; run M1_import_time_only; git checkout -q -- $L
mutate 'elif PRIVATE_ATTRS and isinstance(n, ast.Attribute)' 'elif False and isinstance(n, ast.Attribute)'; mutate 'elif PRIVATE_ATTRS and isinstance(n, ast.Call)' 'elif False and isinstance(n, ast.Call)'; run M2_no_attr_crossings; git checkout -q -- $L
mutate 'unused = unused_boundary_imports(pkg) if UNUSED_IMPORTS else []' 'unused = []'; run M3_tripwire_reads_nothing; git checkout -q -- $L
mutate 'if r > rank[m])' 'if r > 2)'; run M4_no_layer_above; git checkout -q -- $L
mutate '                            if _private(name or target.rsplit(".", 1)[-1]):' '                            if False:'; run M5_no_imported_private; git checkout -q -- $L
mutate 'if id(n) in pkg.type_checking_imports or' 'if'; run M6_type_checking_counted; git checkout -q -- $L
git status --short
