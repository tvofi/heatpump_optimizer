cd /home/user/audit-r11-px-D2-2; export PYTHONPATH=tests/hastub; PY=/opt/hpo/venv-ci/bin/python3; D=dev/audit/rounds/round11/D2/s3; O=$HOME/vout/D2-v2/v1
run() { n=$1; shift; s=$(date +%s); echo "### $n load1=$(cut -d' ' -f1 /proc/loadavg)" > $O/$n.out; timeout 5400 "$@" >> $O/$n.out 2>&1; echo "### rc=$? wall=$(( $(date +%s)-s ))s load1_end=$(cut -d' ' -f1 /proc/loadavg)" >> $O/$n.out; }
T="env HASTUB_TZ=Europe/Stockholm $PY $D/m4_tariff.py"
run sysid $PY $D/m5_sysid.py &
run crosscov $PY $D/m5_crosscov.py &
run risk $PY $D/m3_risk.py &
run tariff $T &
wait
run risk_p $PY $D/m3_risk.py --perturb-raw &
run t_minor $T --perturb minor &
run t_tomorrow $T --perturb tomorrow &
run t_weekday $T --perturb weekday &
wait
run t_oneperday $T --perturb oneperday &
run t_topk $T --perturb topk &
run t_realhours $T --perturb realhours &
run tank $PY $D/m5_tankfall.py &
wait
run tank_p $PY $D/m5_tankfall.py --perturb-skip-heated &
run draw $PY $D/m5_drawrange.py &
run draw_p $PY $D/m5_drawrange.py --perturb-floor &
run sysid_p $PY $D/m5_sysid.py --perturb-bar5 &
wait
run crosscov_p $PY $D/m5_crosscov.py --perturb-ridge0
echo done > $O/ALLDONE
