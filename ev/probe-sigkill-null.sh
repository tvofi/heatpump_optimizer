set -u
W=$(mktemp -d); P=/opt/hpo/venv-ci/bin/python
cat > $W/jobs.json <<J
{"version":1,"jobs":[{"name":"stubborn","argv":["/bin/bash","-c","trap '' TERM; bash -c 'trap \"\" TERM; echo \$\$ > $W/gc.pid; exec sleep 300' & wait"],"cwd":"orch","interval_s":3600,"timeout_s":2,"heartbeat_s":null,"env_pass":[],"class":null,"kind":"periodic"}]}
J
start=$(date +%s)
$P -I wt/tools/audit/seat/beatd.py run --state $W/s --jobs $W/jobs.json --repo wt --once; echo "beatd rc=$? after $(( $(date +%s)-start ))s"
cat $W/s/beatd/journal.log
gc=$(cat $W/gc.pid); sleep 13
echo "15s after timeout: grandchild $gc state: $(awk '{print $3}' /proc/$gc/stat 2>/dev/null || echo gone)"
ls -l $W/s/beatd/stubborn.lock; kill -9 $gc 2>/dev/null; true
