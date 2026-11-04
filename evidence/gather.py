import json, subprocess, sys
sys.path.insert(0, "/home/user/heatpump_optimizer/tests")
import ci_ratchet as c
def runner(argv, **kw):
    args = argv[2:]
    jq = None
    if "--jq" in args:
        jq = args[args.index("--jq")+1]
    url = args[-1]
    p = subprocess.run(["curl","-sS","-f","https://api.github.com/"+url], capture_output=True, text=True)
    out = p.stdout
    if p.returncode==0 and jq:
        out = "\n".join(json.dumps(x) for x in json.loads(out)["jobs"])
    return subprocess.CompletedProcess(argv, p.returncode, out, p.stderr)
n = c.gather_runs(sys.argv[1], repo="tvofi/heatpump_optimizer", runner=runner, window=int(sys.argv[2]))
