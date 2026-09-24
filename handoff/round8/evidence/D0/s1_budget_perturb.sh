#!/bin/bash
# D0 round 8 seat s1: the perturbation for D0-s1-01. Applies the one-line production edit
# (both L-BFGS-B "ftol": 1e-6 literals in optimizer.py -> 1e-12), runs s1_budget.py on five
# two-zone cells, and restores optimizer.py in a trap (git checkout) whatever happens.
# Expected: prod J drops to the ftol arm's J; RESULT ftol_gap_* -> ~0 (|gap| < 1e-6);
# runs_stopped_by_ftol falls from its baseline count.
# Command (tree root): bash tools/audit/round8/D0/s1_budget_perturb.sh
set -u
F=custom_components/heatpump_optimizer/optimizer.py
trap 'git checkout -- "$F"; git diff --quiet -- "$F" && echo "RESTORED $F"' EXIT
n=$(grep -c '"ftol": 1e-6' "$F"); echo "ftol literals edited: $n"
sed -i 's/"ftol": 1e-6/"ftol": 1e-12/g' "$F"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 PYTHONPATH=tests/hastub
for c in "winter_typical winter_cold" "flat winter_cold" "shoulder winter_cold" "winter_narrow winter_cold" "winter_extreme winter_mild"; do
  set -- $c
  python3 -u tools/audit/round8/D0/s1_budget.py --tz 1 --dhw 0 --arms prod,ftol --prices $1 --weather $2 | grep -E "^CELL|runs_stopped_by_ftol|ftol_gap_max|prod_lbfgsb_runs"
done
