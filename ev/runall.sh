cd /tmp/tmp.KkoLuKzYqh
for t in r1 ctl head head-remark head-nomap; do
  echo "=== edge $t"; timeout 200 bash fh/runsh_edge.sh /tmp/tmp.KkoLuKzYqh/tree-$t 2>&1 | grep -v '^$'
done > ev/runsh-edge-all.txt 2>&1
for t in r1 head head-nomap; do
  for j in 1 2; do echo "=== harness $t JOBS=$j"; JOBS=$j timeout 200 bash fh/runsh_harness.sh /tmp/tmp.KkoLuKzYqh/tree-$t 2>&1 | grep -v '^$'; done
done > ev/runsh-harness-all.txt 2>&1
echo done > ev/.runall-done
