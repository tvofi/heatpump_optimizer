import importlib.util,subprocess,sys
spec=importlib.util.spec_from_file_location("mt",sys.argv[1]);mt=importlib.util.module_from_spec(spec);spec.loader.exec_module(mt)
run=lambda a:(lambda r:(r.returncode,r.stdout+r.stderr))(subprocess.run(a,capture_output=True,text=True))
CF=("tests/golden/claimed_drift.txt","tests/golden/card_claimed_drift.txt")
for lab,h in zip(("claim-only","content+claim","clean","unknown"),sys.argv[3:]):
    f=mt.conflicts(run,sys.argv[2],h); print("RESULT",lab,f, "->", mt.dirty_repair(f,CF) if f else f)
