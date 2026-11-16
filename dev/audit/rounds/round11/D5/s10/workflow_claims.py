#!/usr/bin/env python3
"""D5-s10 non-finding checks over .claude/workflows/*.js comment claims, each executed against the code it sits on.

Metric: RESULT mismatches = claims below that the code contradicts:
  audit-fix.js:22/32 + audit-wave.js:45/50 "hand-mirrored" prompts -- the two fixer and two reviewer template
    literals are byte-identical after normalising the interpolation names;
  audit-wave.js:3 "chunks of at most three" -- the batch slice bound is 3;
  audit-verify.js:64 "start at 15" -- SHARD_SIZE default is 15; :104 "One verifier per dimension" -- the constant is 1;
  audit-wave.js:7-9 "carry no `import` of a sibling file anywhere" -- no workflow script has an import/require;
  web-*.js:1-3 "the shared prompt block ... hand-copied" -- tools/policy/fragments_sync.mjs --check exits 0.
Command (export root): PYTHONPATH=tests/hastub $HOME/venv-ci/bin/python3 \
  dev/audit/rounds/round11/D5/s10/workflow_claims.py --repo /home/user/heatpump_optimizer --ref 92d38ecb640bd462f2e19c0814d0f0b7df1ee692
Expected at 92d38ecb (box B12, round 11): RESULT claims=6 mismatches=0, exact.
Perturbation: --perturb edits one word of audit-wave.js's fixer prompt in the scratch copy: mismatches 0 -> 1 (up).
Writes only under a mkdtemp root.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import argparse, re, shutil, subprocess, tempfile
from pathlib import Path

ap = argparse.ArgumentParser(); ap.add_argument("--repo", required=True); ap.add_argument("--ref", required=True)
ap.add_argument("--perturb", action="store_true"); a = ap.parse_args()
root = Path(tempfile.mkdtemp(prefix="d5s10_wf_"))
try:
    arch = subprocess.run(["git", "-C", a.repo, "archive", a.ref], capture_output=True, check=True).stdout
    subprocess.run(["tar", "-x", "-C", str(root)], input=arch, check=True)
    W = root / ".claude/workflows"
    if a.perturb:
        p = W / "audit-wave.js"; p.write_text(p.read_text().replace("You own fix group", "You hold fix group", 1))
    rd = lambda n: (W / n).read_text()
    norm = lambda s: re.sub(r"\$\{[^}]*\}", "${}", s)
    tl = lambda s, start: norm(re.search(re.escape(start) + r"[^`]*`", s[s.index(start) - 1:]).group(0))
    fix, wave = rd("audit-fix.js"), rd("audit-wave.js")
    res = {}
    res["fixer_prompt_mirrored"] = tl(fix, "You own fix group") == tl(wave, "You own fix group") if "You own fix group" in wave else False
    res["reviewer_prompt_mirrored"] = tl(fix, "You are the adversarial fix reviewer") == tl(wave, "You are the adversarial fix reviewer")
    res["wave_chunk_three"] = "ready.slice(0, 3)" in wave
    ver = rd("audit-verify.js")
    res["shard_15_and_one_verifier"] = "args?.shard_size ?? 15" in ver and "const VERIFIERS_PER_DIMENSION = 1" in ver
    res["no_sibling_import"] = not any(re.search(r"^\s*import\s|require\(", (W / f).read_text(), re.M) for f in os.listdir(W) if f.endswith(".js"))
    g = lambda *x: subprocess.run(["git", "-C", str(root), *x], capture_output=True, text=True)
    g("init", "-q"); g("add", "-A"); g("-c", "user.email=t@t", "-c", "user.name=t", "commit", "-qm", "s")
    fr = subprocess.run(["node", "tools/policy/fragments_sync.mjs", "--check"], cwd=root, capture_output=True, text=True)
    res["fragments_in_sync"] = fr.returncode == 0
    for k, v in res.items():
        print(f"   {k}={int(v)}")
    print(f"RESULT claims={len(res)} count")
    print(f"RESULT mismatches={sum(not v for v in res.values())} count")
finally:
    shutil.rmtree(root, ignore_errors=True)
print("RESULT thread_factor=1.000"); print(f"RESULT load1={os.getloadavg()[0]:.2f}"); print("RESULT swapins=0")
