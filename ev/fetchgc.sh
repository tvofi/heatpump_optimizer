S=$1; cd $S; rm -rf r2; git clone -q r r2 && cd r2 && git config gc.auto 1 && for i in $(seq 1 1500); do echo "l$i"; done | git hash-object -w --stdin-paths >/dev/null 2>&1; for i in $(seq 1 1500); do echo "l$i" > ../o$i; done; ls ../o* | git hash-object -w --stdin-paths >/dev/null; rm -f ../o* && (cd ../r && echo y>>f && git -c user.name=a -c user.email=a@b commit -qam y)
L=$S/lock2; : > $L
{ python3 -I -c 'import fcntl; fcntl.flock(9, fcntl.LOCK_EX)'; bash -c 'git fetch -q origin' & } 9>>$L; wait $!; echo "the push (git fetch) exited"
python3 -I -c 'import fcntl,sys; f=open(sys.argv[1],"a")
try: fcntl.flock(f, fcntl.LOCK_EX|fcntl.LOCK_NB); print("free")
except BlockingIOError: print("HELD after the push exited")' $L
ps -eo pid,ppid,args | grep -E '[g]it (gc|maint|repack)'; git --version
