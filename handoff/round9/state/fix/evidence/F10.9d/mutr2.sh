set -u
cd /home/user/heatpump_optimizer
rm -rf /tmp/claude-0/wtm; 
for m in C1 C3 C4; do
  git worktree add -q --detach /tmp/claude-0/wtm HEAD
  cd /tmp/claude-0/wtm
  case $m in
   C1) sed -i 's|"inert_reads": sorted(f for f in opened if _is_real_file(f) and is_inert(f)),|"inert_reads": [],|' tests/closure.py;;
   C3) python3 - <<'P'
p='tests/closure.py'; s=open(p).read()
s=s.replace("    for k, r in records.items():\n        reads = sorted(f for f in r.get(\"inert_reads\", ())","    for k, r in []:\n        reads = sorted(f for f in r.get(\"inert_reads\", ())",1)
open(p,'w').write(s)
P
   ;;
   C4) sed -i 's/^    if missed:$/    if False:/' tests/closure.py;;
  esac
  git diff --stat | tail -1
  PYTHONPATH=tests/hastub /tmp/claude-0/v312/bin/python tests/entities.py 2>&1 | grep -E "^  FAIL|CHECKS? (FAILED|PASSED)" | cut -c1-140
  cd /home/user/heatpump_optimizer; git worktree remove --force /tmp/claude-0/wtm
done
echo ALLDONE
