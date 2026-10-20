python3 -I -c 'import os; os.setpgid(0,0); os.execvp("bash",["bash","-c","sleep 2; true & sleep 2; true"])' &
L=$!; sleep 0.5; kill -KILL $L; sleep 4
echo "group $L after its push ended:"; ps -A -o pid,ppid,pgid,stat,comm | awk -v g=$L 'NR==1||$3==g'
