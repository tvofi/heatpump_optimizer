cd /tmp/claude-0/wtm
eval "$(bash .claude/hooks/session-start.sh --env-lines)" 2>/dev/null
export PYTHONPATH=tests/hastub
M="# -- R11-SEAM-cycle-solve: when a solve runs (solve_gate)"
F=custom_components/heatpump_optimizer/solve_gate.py
python3 tools/audit/seat/features_block.py --emit-prelude /tmp/claude-0/repro/p2.py "$M" > /tmp/claude-0/repro/m_emit.log 2>&1
run(){ python3 tools/audit/seat/features_block.py --prelude 'exec(open("/tmp/claude-0/repro/p2.py").read())' "$M" "# == REVIEWER-REPRO" > /tmp/claude-0/repro/m_$1.log 2>&1; echo "$1 rc=$? $(grep -c '  FAIL' /tmp/claude-0/repro/m_$1.log) FAIL" >> /tmp/claude-0/repro/mut_summary.txt; }
: > /tmp/claude-0/repro/mut_summary.txt
run clean
cp $F /tmp/claude-0/repro/sg.bak
python3 - <<'P'
p="custom_components/heatpump_optimizer/solve_gate.py";s=open(p).read()
s=s.replace("    gate.solving = True\n    gate.background_taken = False\n","    gate.solving = True\n",1);open(p,"w").write(s)
P
run begin_solve_reset_deleted; cp /tmp/claude-0/repro/sg.bak $F
python3 - <<'P'
p="custom_components/heatpump_optimizer/solve_gate.py";s=open(p).read()
s=s.replace("    if refreshing:\n        gate.trailing = True\n        return True\n","",1);open(p,"w").write(s)
P
run refreshing_arm_deleted; cp /tmp/claude-0/repro/sg.bak $F
python3 - <<'P'
p="custom_components/heatpump_optimizer/solve_gate.py";s=open(p).read()
s=s.replace("    if ticket != gate.user_waiting:","    if False:",1);open(p,"w").write(s)
P
run supersede_off; cp /tmp/claude-0/repro/sg.bak $F
git diff --stat -- custom_components >> /tmp/claude-0/repro/mut_summary.txt
echo done >> /tmp/claude-0/repro/mut_summary.txt
