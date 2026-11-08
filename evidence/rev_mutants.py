"""Reviewer mutants (PR 3301, round 2 review): added ci_predict.py lines not in
dev/audit/rca/prepr-head-graders/mutants.py. Each runs graders_self_test (or the named
self-test) from a copy of tools/pr/ and prints its FAIL count."""
import subprocess, sys, tempfile, shutil
from pathlib import Path
root = Path(sys.argv[1]).resolve(); src = (root / "tools/pr/ci_predict.py").read_text()
G = "graders_self_test"
M = {
 "V1 BOOTSTRAP on every refusal (membership dropped)": ('(f" -- {BOOTSTRAP}" if prog in hit else "")', '(f" -- {BOOTSTRAP}")', G),
 "V2 BOOTSTRAP never": ('(f" -- {BOOTSTRAP}" if prog in hit else "")', '""', G),
 "V3 partial annotation dropped from the refusal": ('(f" (partial: ran without {part})" if part else "")', '""', G),
 "V4 PARTIAL note never written": ('if part:\n                    said.append(f"GRADER PARTIAL', 'if part:\n                    (lambda *_: 0)(f"GRADER PARTIAL', G),
 "V5 notes never returned": ("        notes += sorted(set(said))", "        pass", G),
 "V6 backslash continuation not joined": ('body = body.replace("\\\\\\n", " ")', 'body = body', G),
 "V7 keyed by bare job": ("            keyed[key] = hit", "            keyed[job] = hit", G),
 "V8 PR_TOKENS not excused from gaps": ("            and a not in PR_TOKENS and a not in PR_DROPPED\n", "", G),
 "V9 runner files not redirected to tmp": ("a = str(tmp / Path(a).name) if a in files else a", "a = a", G),
 "V10 runner files not written": ("                for f, text_ in files.items():\n                    (tmp / Path(f).name).write_text(text_ or \"\")", "                pass", G),
 "V11 .sh run by node": ('("bash" if prog.endswith(".sh") else "node", prog)', '("node", prog)', G),
 "V12 '<' kept as an argument": ('if a in PR_DROPPED and a != "<" or (a == "<" or (i and argv[i - 1] == "<")):', 'if a in PR_DROPPED and a != "<" or (i and argv[i - 1] == "<"):', G),
 "V13 partial key exact, not prefix": ("if key_[:len(k)] == k", "if key_ == k", G),
 "V14 partial never matched": ("if key_[:len(k)] == k", "if False", G),
 "V15 ci_tree_run gets no workflow": ("tuple(step(p, a) for p, a in runs), wf)", "tuple(step(p, a) for p, a in runs))", G),
 "V16 stdin not passed to run": ("out = run(*cmd, *args, input=stdin)", "out = run(*cmd, *args)", G),
 "V17 author stand-in wrong": ('"$(cat /tmp/pr-author.txt)": "hpo-author[bot]"', '"$(cat /tmp/pr-author.txt)": "x"', G),
 "V18 grader_gaps reads only the first text": ("runs = [r for t in texts for r in pinned_runs(t)]", "runs = [r for t in texts[:1] for r in pinned_runs(t)]", G),
 "V19 boot counts every red (main)": ('boot = sum(1 for j, l in preds if is_red(j, l) and "BOOTSTRAP:" in l)', 'boot = sum(1 for j, l in preds if is_red(j, l))', G),
 "V20 summary drops the BOOTSTRAP count": ('+ (f" ({boot} BOOTSTRAP: split or move, not repair)" if boot else "")', '', G),
 "C2-R1 self_test_reads grades under the file's own key": ('json.dumps({**rec, "script": host})', 'json.dumps(rec)', "self_test_reads_self_test"),
}
for name, (a, b, fn) in M.items():
    n = src.count(a)
    if n != 1:
        print(f"{name}: SITE COUNT {n} (not applied)"); continue
    d = Path(tempfile.mkdtemp()); shutil.copytree(root / "tools/pr", d / "pr")
    (d / "pr/ci_predict.py").write_text(src.replace(a, b))
    try:
        out = subprocess.run([sys.executable, "-I", "-c", f"import sys; sys.path.insert(0, {str(d/'pr')!r}); from pathlib import Path; import ci_predict as c; print('bad', c.{fn}(Path({str(root)!r})))"],
                             capture_output=True, text=True, cwd=root, timeout=600).stdout
    except subprocess.TimeoutExpired:
        out = "TIMEOUT"
    fails = [l.strip()[:110] for l in out.splitlines() if "FAIL" in l]
    print(f"{name}: {out.strip().splitlines()[-1] if out.strip() else 'no output'}; {len(fails)} FAIL", flush=True)
    for f in fails: print("   ", f)
    shutil.rmtree(d)
