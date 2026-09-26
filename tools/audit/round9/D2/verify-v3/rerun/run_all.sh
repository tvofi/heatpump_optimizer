#!/bin/sh
# V3 step-1 re-runs of the D2 finders' harnesses, venv substituted (/home/claude/venv).
# Run from the repository root: sh tools/audit/round9/D2/verify-v3/rerun/run_all.sh
P=/home/claude/venv/bin/python
D=tools/audit/round9/D2
O=$D/verify-v3/rerun
export PYTHONPATH=tests/hastub
r(){ n=$1; shift; echo "== $n: $*" ; ( cat /proc/loadavg; timeout 1800 $P "$@" ; echo "exit=$?"; cat /proc/loadavg ) > $O/$n.out 2>&1; }
r stab $D/s1/m1_stability.py
r stab_p $D/s1/m1_stability.py --perturb=ratio1
r coil $D/s1/m1_coil.py
r coil_p $D/s1/m1_coil.py --perturb=mixuse
r slab $D/s2/slab_cap_scale.py
r slab_p $D/s2/slab_cap_scale.py --perturb
r flow $D/s2/flow_bias_clamp.py
r flow_p $D/s2/flow_bias_clamp.py --perturb
r cqp $D/s3/current_quarter_price.py
r cqp_p $D/s3/current_quarter_price.py --perturb
r pv $D/s3/pv_piecewise.py
r pv_p $D/s3/pv_piecewise.py --perturb
r sizer $D/s4/sizer_margin.py --seeds 16
r sizer_p $D/s4/sizer_margin.py --seeds 16 --perturb margin
r objid $D/s2/objective_identities.py
r objid_p $D/s2/objective_identities.py --perturb
r plan2 $D/s2/slab_cap_plan.py 2.0
r cov $D/s4/coverage.py --seeds 40
r cov_s0 $D/s4/coverage.py --seeds 40 --perturb sigma0
