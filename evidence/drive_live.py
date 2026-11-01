import sys, json, subprocess, os
root = sys.argv[1]; sys.path.insert(0, os.path.join(root, "tools/pr")); os.chdir(root)
import gh_comment as ghc
def thread(repo, issue):
    out, p = [], 1
    while True:
        r = json.loads(subprocess.run(["gh","api",f"repos/{repo}/issues/{issue}/comments?per_page=100&page={p}"],capture_output=True,text=True,check=True).stdout)
        if not r: return out
        out += r; p += 1
for f in sys.argv[2:]:
    try:
        rc = ghc.run(["post","--repo","tvofi/heatpump_optimizer","--issue","201","--body-file",f,"--dry-run"], thread=thread)
    except SystemExit as e:
        rc = e.code
    except ghc.Refused as e:
        rc = f'REFUSED[{str(e)[:90]}]'
    print(f"RESULT body={os.path.basename(f)} rc={rc}", flush=True)
