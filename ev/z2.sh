python3 -I -c 'import os; os.setpgid(0,0); os.execvp("bash",["bash","-c","bash -c \"sleep 1.5; exit 0\"; true"])' &
L=$!; sleep 0.3; kill -KILL $L; sleep 1.4
for i in $(seq 1 30); do echo "t+$((i*100))ms: $(ps -A -o pgid=,stat= | awk -v g=$L '$1==g{print $2}' | tr '\n' ' ')"; sleep 0.1; done | awk '{print} /: *$/ {n++} n>2{exit}'
