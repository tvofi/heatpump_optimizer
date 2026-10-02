# reviewer mutants over .github/workflows/tests.yml / governance.yml; each restored from HEAD
import subprocess, sys, os, re, pathlib
W = pathlib.Path(sys.argv[1]); EV = pathlib.Path(sys.argv[2])
T = '.github/workflows/tests.yml'; G = '.github/workflows/governance.yml'
def rep(path, old, new, count=1):
    p = W / path; s = p.read_text(); assert s.count(old) >= 1, (path, old); p.write_text(s.replace(old, new, count))
def m1(): subprocess.run(['git','checkout','1abfef56d081146d7a38828047d790a23ffcac27','--',T], cwd=W, check=True)
def m2():
    s=(W/T).read_text(); i=s.index("The pull request's field_coverage.mjs, under the Actions token")
    j=s.index('run: node .claude/workflows/field_coverage.mjs', i); (W/T).write_text(s[:j]+'run: true'+s[j+len('run: node .claude/workflows/field_coverage.mjs'):])
def m3(): rep(T, "              'tools/audit/record-predicate' \\\n", "")
def m4():
    s=(W/T).read_text(); i=s.index("The pull request's policy_lint.mjs, under the Actions token")
    j=s.index("if: ${{ !cancelled() && ", i); (W/T).write_text(s[:j]+"if: ${{ "+s[j+len("if: ${{ !cancelled() && "):])
def r1():  # field_coverage step loses its token
    s=(W/T).read_text(); i=s.index("The pull request's field_coverage.mjs, under the Actions token")
    j=s.index("        env:\n          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}\n", i); (W/T).write_text(s[:j]+s[j+len("        env:\n          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}\n"):])
def r2(): rep(T, 'echo "governance=true" >> "$GITHUB_OUTPUT"', 'echo "governance=false" >> "$GITHUB_OUTPUT"')  # arm never fires
def r3():  # arm keyed on the wrong value
    s=(W/T).read_text(); s=s.replace("steps.changed.outputs.governance == 'true' }}", "steps.changed.outputs.governance == 'false' }}"); (W/T).write_text(s)
def r4(): rep(T, "if: ${{ !cancelled() && github.event_name == 'pull_request' }}\n    runs-on", "if: ${{ github.event_name == 'pull_request' }}\n    runs-on")  # job-level guard
def r5(): rep(G, "      - name: Refuse a Cursor rule that is not the generated form of its source\n", "      - name: Refuse a Cursor rule that is not the generated form of its source\n        env:\n          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}\n")  # a new token-bearing pinned grader
def r6(): rep(T, "if git diff --quiet \"$BASE\"...\"$HEAD\" -- \\\n              '.claude/workflows/*.mjs'", "if true || git diff --quiet \"$BASE\"...\"$HEAD\" -- \\\n              '.claude/workflows/*.mjs'")  # trigger short-circuited
MUT = dict(M1=m1,M2=m2,M3=m3,M4=m4,R1=r1,R2=r2,R3=r3,R4=r4,R5=r5,R6=r6)
env = dict(os.environ, PYTHONPATH='tests/hastub', PATH='/Users/timmalmstrom/hpo-seats/bin:'+os.environ['PATH'])
for name in (sys.argv[3:] or MUT):
    try: MUT[name]()
    except Exception as e: print(f'RESULT {name} APPLY-FAILED {e!r}', flush=True); subprocess.run(['git','checkout','HEAD','--',T,G],cwd=W); continue
    d = subprocess.run(['git','diff','--stat'],cwd=W,capture_output=True,text=True).stdout.strip().splitlines()
    out = subprocess.run([os.path.expanduser('~/hpo-seats/R9-F11.4-venv/bin/python3'),'tests/entities.py'],cwd=W,env=env,capture_output=True,text=True)
    (EV/f'mut_{name}.txt').write_text(out.stdout+out.stderr)
    fails=[l.strip() for l in out.stdout.splitlines() if l.lstrip().startswith('FAIL')]
    tail=[l for l in out.stdout.splitlines() if 'ENTITY CHECKS' in l]
    print(f'RESULT {name} rc={out.returncode} diff={d[-1] if d else "NONE"} {tail[-1] if tail else "no-tail"}', flush=True)
    for f in fails: print('   ', f[:220], flush=True)
    subprocess.run(['git','checkout','HEAD','--',T,G],cwd=W,check=True)
print('RESTORED', subprocess.run(['git','status','--short'],cwd=W,capture_output=True,text=True).stdout.strip())
