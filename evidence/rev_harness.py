"""Reviewer-built harness (NOT the finder's: no committed finder harness exists).
Runs the ci-ratchet 'Gather' step's run: text from a given tests.yml under an independent
stub gh, in failure modes modelled on production job 119281753833 ("unexpected end of JSON
input", then JSONDecodeError), and prints RESULT lines."""
import os, subprocess, sys, tempfile, json, yaml
yml = yaml.safe_load(open(sys.argv[1]))
run = next(s["run"] for s in yml["jobs"]["ci-ratchet"]["steps"] if s.get("name","").startswith("Gather this run's"))
run = run.replace("${{ github.repository }}", "o/r")
GH = r'''#!/bin/bash
# independent stub: listing calls go through real jq over a synthetic body, or fail per MODE
if [ "$1 $2" = "run download" ]; then exit 0; fi
url="$2"
case "$url" in
  */zip) python3 -c "import io,zipfile,sys;b=io.BytesIO();z=zipfile.ZipFile(b,'w');z.writestr('m.tsv','x\n');z.close();sys.stdout.buffer.write(b.getvalue())"; exit 0;;
esac
echo "$url" >> "$LOG"
jqf=""; while [ $# -gt 0 ]; do [ "$1" = "--jq" ] && jqf="$2"; shift; done
name=$(printf %s "$url" | sed -n 's/.*name=\([^&]*\).*/\1/p')
case "$MODE" in
  empty) echo "unexpected end of JSON input" >&2; exit 1;;            # production signature
  fail_unfiltered) if [ -z "$name" ]; then echo "unexpected end of JSON input" >&2; exit 1; fi;;
  fail_one) if [ "$name" = "ci-metrics-coverage" ]; then echo "gh: Server Error (HTTP 502)" >&2; exit 1; fi;;
esac
python3 - "$name" <<'PY' | jq "$jqf"
import json, sys
name = sys.argv[1]
names = [name] if name else ["ci-metrics-fast","ci-metrics-coverage","ci-metrics-closures","other"]
arts = []
i = 0
for run in range(100, 140):
    for n in names:
        i += 1
        arts.append({"id": i, "name": n, "expired": False, "workflow_run": {"id": run}, "run_id": None,
                     "created_at": f"2026-10-21T{run-100:02d}:00:00Z"})
arts.sort(key=lambda a: a["created_at"], reverse=True)
print(json.dumps({"artifacts": arts[:100]}))
PY
'''
for mode in ["ok", "empty", "fail_unfiltered", "fail_one"]:
    with tempfile.TemporaryDirectory() as td:
        os.makedirs(f"{td}/bin"); open(f"{td}/bin/gh","w").write(GH); os.chmod(f"{td}/bin/gh", 0o755)
        r = subprocess.run(["bash","-c",run], capture_output=True, text=True,
            env={**os.environ, "PATH": f"{td}/bin:"+os.environ["PATH"], "RUNNER_TEMP": td,
                 "GITHUB_RUN_ID": "139", "GITHUB_REPOSITORY": "o/r", "LOG": f"{td}/log", "MODE": mode})
        files = sorted(os.listdir(f"{td}/metrics")) if os.path.isdir(f"{td}/metrics") else []
        w = [l for l in r.stdout.splitlines() if l.startswith("window:")]
        print(f"RESULT mode={mode} rc={r.returncode} window={w[0] if w else None} files={len(files)} "
              f"traceback={'Traceback' in r.stderr} gh_msg_surfaced={('unexpected end' in r.stderr) or ('HTTP 50' in r.stderr)} "
              f"listings={len(open(td+'/log').read().splitlines()) if os.path.exists(td+'/log') else 0}")
