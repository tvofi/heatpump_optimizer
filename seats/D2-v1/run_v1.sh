cd /home/user/audit-r11-px-D2-1; export PYTHONPATH=tests/hastub; PY=/opt/hpo/venv-ci/bin/python3; D=dev/audit/rounds/round11/D2; O=$HOME/vout/D2-v1/v1
run() { n=$1; shift; s=$(date +%s); echo "### $n load1=$(cut -d' ' -f1 /proc/loadavg)" > $O/$n.out; timeout 3000 $PY "$@" >> $O/$n.out 2>&1; echo "### rc=$? wall=$(( $(date +%s)-s ))s" >> $O/$n.out; }
run bp $D/s1/batch_parity.py &
run bp_fixlift $D/s1/batch_parity.py --fix-lift &
run bp_fixboth $D/s1/batch_parity.py --fix-lift --fix-emitter &
run era $D/leads/era_loss_order.py &
wait
run era_p $D/leads/era_loss_order.py --perturb &
run cop $D/s2/m2_cop_laws.py &
run cop_lift $D/s2/m2_cop_laws.py --perturb=lift &
run cop_def $D/s2/m2_cop_laws.py --perturb=defrost &
wait
run ps $D/s2/m2_priced_surface.py &
run ps_p $D/s2/m2_priced_surface.py --perturb &
wait
echo done > $O/ALLDONE
