import subprocess, sys, os, tempfile
wt, py, drv = sys.argv[1:4]
yml = open(os.path.join(wt, ".github/workflows/tests.yml")).read()
base_run = subprocess.run(["git","-C",wt,"show","e9febe6224eaccedbdcd3ffdf3f92a84cb034e9a:.github/workflows/tests.yml"],capture_output=True,text=True).stdout
MUT = {
 "R0 unmutated": [],
 "R1 delete unique_by(.run) (one artifact per run)": [("| reverse | unique_by(.run)\n", "| reverse\n")],
 "R2 '|| true' after jq -s add": [('> "$RUNNER_TEMP/window.json"\n          python3', '> "$RUNNER_TEMP/window.json" || true\n          python3')],
 "R3 '|| true' on the listing (delete fail-loud)": [('>> "$RUNNER_TEMP/lanes.json"\n', '>> "$RUNNER_TEMP/lanes.json" || true\n')],
 "R4 drop second sort before cap": [("unique_by(.run)\n                    | sort_by(.at) | reverse | .[:15]", "unique_by(.run)\n                    | .[:15]")],
 "R5 delete 'set -euo pipefail'": [("set -euo pipefail\n          M=\"$RUNNER_TEMP/metrics\"", "M=\"$RUNNER_TEMP/metrics\"")],
 "R6 cat instead of jq -s add": [('jq -s add "$RUNNER_TEMP/lanes.json"', 'cat "$RUNNER_TEMP/lanes.json"')],
 "R7 run id from .run_id only": [("{id: .id, run: (.workflow_run.id // .run_id),\n                        name", "{id: .id, run: .run_id,\n                        name")],
 "R8 delete expired filter": [("                     | select(.expired == false)\n", "")],
 "R9 cap 16": [(".[:15]'", ".[:16]'")],
 "R10 drop ': > lanes.json' truncation": [(':  > "$RUNNER_TEMP/lanes.json"\n'.replace(":  ",": "), "")],
}
for name, subs in MUT.items():
    t = yml
    for a, b in subs:
        assert t.count(a) == 1, (name, a, t.count(a))
        t = t.replace(a, b)
    f = tempfile.NamedTemporaryFile("w", suffix=".yml", delete=False); f.write(t); f.close()
    r = subprocess.run([py, drv, wt, f.name, "33427", "33522"], capture_output=True, text=True, cwd=wt)
    fails = [l for l in r.stdout.splitlines() if l.startswith("FAIL ")]
    print(f"RESULT mutant={name!r} {'KILLED' if fails else 'SURVIVED'} by={[l.split('  ::')[0][5:60] for l in fails]}" + ("" if r.returncode==0 else f" rc={r.returncode} err={r.stderr[-300:]!r}"))
# null control: the base's step text substituted in place of the head's step
import re
def step(y):
    i = y.index("      - name: Gather this run's"); j = y.index("\n      - ", i+10); return y[i:j]
t = yml.replace(step(yml), step(base_run))
f = tempfile.NamedTemporaryFile("w", suffix=".yml", delete=False); f.write(t); f.close()
r = subprocess.run([py, drv, wt, f.name, "33427", "33522"], capture_output=True, text=True, cwd=wt)
print("NULL CONTROL (base step under head checks):"); print(r.stdout[-1500:])
