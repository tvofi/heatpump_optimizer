cd /tmp/claude-0/-home-user-heatpump-optimizer/c85cc0b3-a7f8-52e2-80dd-5fe6ac9e6b18/scratchpad/head
for t in base head; do
 for i in $(seq 10); do PYTHON=python3 bash dev/audit/harnesses/r10_roster_push_race.sh /tmp/claude-0/-home-user-heatpump-optimizer/c85cc0b3-a7f8-52e2-80dd-5fe6ac9e6b18/scratchpad/$t shared | grep '^mode='| sed "s/^/$t /"; done
 for i in $(seq 10); do PYTHON=python3 bash dev/audit/harnesses/r10_roster_push_race.sh /tmp/claude-0/-home-user-heatpump-optimizer/c85cc0b3-a7f8-52e2-80dd-5fe6ac9e6b18/scratchpad/$t separate | grep '^mode='| sed "s/^/$t /"; done
 for i in $(seq 3); do PYTHON=python3 bash dev/audit/harnesses/r10_roster_push_race.sh /tmp/claude-0/-home-user-heatpump-optimizer/c85cc0b3-a7f8-52e2-80dd-5fe6ac9e6b18/scratchpad/$t solo | grep '^mode='| sed "s/^/$t /"; done
done
