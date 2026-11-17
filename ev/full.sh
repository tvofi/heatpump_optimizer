S=/tmp/claude-0/-home-user-heatpump-optimizer/fed31491-137c-5466-8393-3cd29f796565/scratchpad
apply() { python3 - "$1" <<'PY'
import sys; sys.path.insert(0, "/tmp/claude-0/-home-user-heatpump-optimizer/fed31491-137c-5466-8393-3cd29f796565/scratchpad/rev")
from mutants import M
for name, f, old, new in M:
    if name == sys.argv[1]:
        s = open(f).read(); assert s.count(old) == 1; open(f, "w").write(s.replace(old, new))
PY
}
( cd $HOME/wt-mut && git checkout -q -- . && apply store_base_domain_dropped && PYTHONPATH=tests/hastub timeout 3000 python3 tests/finite_boundary.py > $S/rev/fb_mut.out 2>&1; echo "finite_boundary store_base_domain_dropped rc=$?" ; tail -2 $S/rev/fb_mut.out; grep -m3 "FAIL" $S/rev/fb_mut.out | cut -c1-250 ) &
( cd $HOME/wt-mut2 && git checkout -q -- . && apply contrast_unsigned_heat_gate && PYTHONPATH=tests/hastub timeout 3000 python3 tests/features.py > $S/rev/feat_mut.out 2>&1; echo "features contrast_unsigned_heat_gate rc=$?"; tail -2 $S/rev/feat_mut.out; grep -m3 "FAIL" $S/rev/feat_mut.out | cut -c1-250 ) &
wait
echo FULL-DONE
