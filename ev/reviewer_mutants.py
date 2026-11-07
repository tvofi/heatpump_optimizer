import subprocess, sys, tempfile, shutil
from pathlib import Path
root = Path(sys.argv[1]).resolve(); src = (root / "tools/pr/ci_predict.py").read_text()
M = {
 "A partial note dropped": ('                if part:\n                    said.append(', '                if False:\n                    said.append('),
 "B partial suffix dropped": ('+ (f" (partial: ran without {part})" if part else "")', '+ ""'),
 "C bootstrap always": ('+ (f" -- {BOOTSTRAP}" if prog in hit else "")', '+ f" -- {BOOTSTRAP}"'),
 "D bootstrap never": ('+ (f" -- {BOOTSTRAP}" if prog in hit else "")', '+ ""'),
 "E reviews-unread swallow dropped": ('if "reviews could not be read" in out.stdout:', 'if False:'),
 "F collision key always bare": ('j if names.count(j) == 1 else f"{Path(w).stem}/{j}"', 'j'),
 "G continuation not joined": ('body = body.replace("\\\\\\n", " ")', 'body = body'),
 "H redirect kept": ('rest = rest.split(">")[0]', 'rest = rest'),
 "I bash runs not parsed": ('(?:node|python3(?: -I)?|bash)\\s+([\\w./-]+\\.(?:mjs|py|sh))', '(?:node|python3(?: -I)?)\\s+([\\w./-]+\\.(?:mjs|py))'),
 "J PR_TOKENS gap exclusion dropped": ('            and a not in PR_TOKENS and a not in PR_DROPPED\n', '            and a not in PR_DROPPED\n'),
 "K body-skip dropped": ('if PR_BODY in argv and body is None:', 'if False:'),
 "L ctx substitution dropped": ('a = ctx.get(a, a)', 'a = a'),
 "M notes not returned": ('        notes += sorted(set(said))', '        pass'),
 "N codescan exemption dropped": ('GRADER_EXEMPT[("pr-contract", "codescan_wait.py", "--pr", "--base")] = "it queries the code-scanning API and grades no file"', 'pass'),
 "O INTENDED empty": ('args += sorted(set(re.findall(', 'args += [] and sorted(set(re.findall('),
 "P stdin redirect dropped": ('stdin = (tmp / Path(a).name).read_text()', 'stdin = None'),
 "Q partial key never matches": ('if key_[:len(k)] == k), None)', 'if False), None)'),
 "R1 self-test-reads file key": ('json.dumps({**rec, "script": host})', 'json.dumps(rec)'),
 "S main tail always repair": ('tail = ("repair before the handoff; " if boot < reds else "") + who', 'tail = "repair before the handoff; " + who'),
 "T grader_preds passes workflow None": ('tuple(step(p, a) for p, a in runs), wf)', 'tuple(step(p, a) for p, a in runs), None)'),
}
fn = sys.argv[2] if len(sys.argv) > 2 else None
only = sys.argv[3:] 
for name, (a, b) in M.items():
    if only and name.split()[0] not in only: continue
    n = src.count(a)
    if n != 1: print(f"{name}: SITE COUNT {n}"); continue
    d = Path(tempfile.mkdtemp()); shutil.copytree(root / "tools/pr", d / "pr")
    (d / "pr/ci_predict.py").write_text(src.replace(a, b))
    if fn == "full":
        p = subprocess.run([sys.executable, "-I", str(d / "pr/ci_predict.py"), "--self-test"], capture_output=True, text=True, cwd=root)
        out = p.stdout + p.stderr
        last = [l for l in out.splitlines() if "self-test:" in l][-1:] 
    else:
        out = subprocess.run([sys.executable, "-I", "-c", f"import sys; sys.path.insert(0, {str(d/'pr')!r}); from pathlib import Path; import ci_predict as c; print('bad', c.{fn}(Path({str(root)!r})))"], capture_output=True, text=True, cwd=root)
        out = out.stdout + out.stderr; last = out.strip().splitlines()[-1:]
    fails = [l.strip()[:150] for l in out.splitlines() if "FAIL" in l]
    print(f"{name}: {last}; {len(fails)} FAIL", flush=True)
    for f in fails[:4]: print("   ", f)
    shutil.rmtree(d)
