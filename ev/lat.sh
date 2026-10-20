L=/home/user/rev2469/lat.lock; rm -f $L
python3 -I -c 'import os,sys; os.setpgid(0,0); os.execvp("bash",["bash","-c","python3 -I -c \"import fcntl, os, subprocess, sys, time\nf = open(sys.argv[1], \\\"a\\\")\nfcntl.flock(f, fcntl.LOCK_EX)\np = os.getppid()\nos.setpgid(0, 0)\ndef group(): return subprocess.run([\\\"ps\\\", \\\"-A\\\", \\\"-o\\\", \\\"pgid=\\\"], capture_output=True, text=True).stdout.split().count(str(p))\nwhile group(): time.sleep(1)\n\" '$L' & bash -c \"sleep 3; date +%s.%N > /home/user/rev2469/lat.end\"; wait"])' &
G=$!; sleep 1; kill -KILL $G
python3 -c 'import fcntl,time; f=open("'$L'","a"); fcntl.flock(f,fcntl.LOCK_EX); print("%.3f"%time.time())' > /home/user/rev2469/lat.free
echo "free-after-end: $(python3 -c "print(round($(cat /home/user/rev2469/lat.free)-$(cat /home/user/rev2469/lat.end),3))")"
