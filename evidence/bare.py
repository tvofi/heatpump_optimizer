import os,subprocess,sys,tempfile
R="/home/user/heatpump_optimizer"
lock=tempfile.mkdtemp(prefix="rv-")
hs=[subprocess.Popen(["sleep","600"]) for _ in range(4)]
env={k:v for k,v in os.environ.items() if k!="HPO_SLOT_LABEL"}; env["HPO_GATE_LOCK_DIR"]=lock
for i,h in enumerate(hs):
    subprocess.run([sys.executable,"tests/gate_lock.py","slot-take","--label",f"h{i}","--owner-pid",str(h.pid),"--no-wait"],cwd=R,env=env,check=True,capture_output=True)
p=subprocess.Popen(["bash","tools/pr/prepr.sh","--self-test"],cwd=R,env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,start_new_session=True)
try: out,_=p.communicate(timeout=40); print("finished",p.returncode)
except subprocess.TimeoutExpired:
    os.killpg(p.pid,9); out,_=p.communicate(); print("timeout")
print("slot lines:"); [print(l) for l in out.splitlines() if "slot" in l.lower()][:0]
print("LINES",len(out.splitlines())); print("\n".join(out.splitlines()[:12]))
for h in hs: h.kill()
