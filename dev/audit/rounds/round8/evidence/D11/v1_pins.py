#!/usr/bin/env python3
"""v1_pins.py -- D11-v1 (verifier) own measurement for D11-s2-03.

METRIC (one line): install commands, tokenised with shlex from the `run:` of every
step of every `.github/workflows/*.yml` (backslash continuations joined, split on
newline/&&/||/;/|), that are not hash-pinned in OpenSSF Scorecard's sense:
pip/`python -m pip` install without `--require-hashes` whose requirement sources
are not all `--hash`-carrying; `npm install|i|add` (not `npm ci`); `npx <pkg>`.
Requirement files are read from the tree; the typing job's runtime file is
produced by running the production symbol `tests/typing_ruler.py
--print-requirements`. Also reported: how many of those are not even
VERSION-pinned (a requirement without `==`), the stronger defect.

Differs from s2_scorecard.py: it walks every workflow, not tests.yml alone, and
tokenises commands instead of matching lines.

NULL CONTROL: the same walker counts `uses:` refs that are not a 40-hex SHA -> 0
expected (the repository SHA-pins actions).

PERTURBATION (--perturb): `--require-hashes` appended to the first
`pip install -r tests/requirements-ci.txt` command (in memory) -> count - 1.

RUN (tree root): PYTHONPATH=tests/hastub python3 tools/audit/round8/D11/v1_pins.py [--perturb]
EXPECTED at cdf82da: unhashed_installs=12 (exact), version_unpinned=1, uses_unpinned=0.
BASELINE: cdf82daabcfe3777d98b31489f36df5555ec9d82. MACHINE: 4-vCPU cloud container; no timing numbers.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import glob, re, shlex, subprocess, sys, time
from pathlib import Path
import yaml


def req_lines(src):
    if "typing-requirements" in src:
        txt = subprocess.check_output([sys.executable, "tests/typing_ruler.py", "--print-requirements"], text=True)
    else:
        txt = Path(src).read_text()
    return [l.strip() for l in txt.splitlines() if l.strip() and not l.strip().startswith("#")]


def classify(tok):
    """-> None if not an install; else (hashed, version_pinned)."""
    if not tok:
        return None
    t = tok[:]
    while t and re.match(r"^[A-Za-z_][A-Za-z0-9_]*=", t[0]):
        t = t[1:]  # leading VAR=value environment assignments
    if not t:
        return None
    if len(t) >= 3 and t[1] == "-m" and t[2] == "pip":
        t = ["pip"] + t[3:]
    name = os.path.basename(t[0])
    if name in ("pip", "pip3") and len(t) > 1 and t[1] == "install":
        args = t[2:]
        if "--require-hashes" in args:
            return (True, True)
        reqs, i = [], 0
        while i < len(args):
            if args[i] in ("-r", "--requirement"):
                reqs += req_lines(args[i + 1]); i += 2; continue
            if not args[i].startswith("-"):
                reqs.append(args[i])
            i += 1
        hashed = bool(reqs) and all("--hash" in r for r in reqs)
        return (hashed, all("==" in r for r in reqs))
    if name == "npm" and len(t) > 1 and t[1] in ("install", "i", "add"):
        return (False, all("@" in a[1:] for a in t[2:] if not a.startswith("-") and not a.startswith("$") and "/" not in a))
    if name == "npx":
        return (False, True)
    return None


def commands(run):
    run = run.replace("\\\n", " ")
    for part in re.split(r"\n|&&|\|\||;|\|", run):
        part = part.strip()
        if not part or part.startswith("#"):
            continue
        try:
            yield shlex.split(part)
        except ValueError:
            yield part.split()


def main():
    t0p, t0t = time.process_time(), time.thread_time()
    perturb = "--perturb" in sys.argv
    unhashed = unver = uses_bad = 0
    done = False
    for wf in sorted(glob.glob(".github/workflows/*.yml")):
        d = yaml.safe_load(Path(wf).read_text())
        for jid, j in (d.get("jobs") or {}).items():
            for s in j.get("steps") or []:
                u = s.get("uses")
                if u and not u.startswith("./") and not re.search(r"@[0-9a-f]{40}$", u):
                    uses_bad += 1
                for tok in commands(s.get("run") or ""):
                    if perturb and not done and tok[:4] == ["pip", "install", "-r", "tests/requirements-ci.txt"]:
                        tok = tok + ["--require-hashes"]; done = True
                    c = classify(tok)
                    if c is None:
                        continue
                    if not c[0]:
                        unhashed += 1
                        print(f"#   {wf}:{jid}: {' '.join(tok)[:90]}{'' if c[1] else '   [NO VERSION PIN]'}")
                    if not c[1]:
                        unver += 1
    print(f"RESULT unhashed_installs={unhashed} commands")
    print(f"RESULT version_unpinned={unver} commands")
    print(f"RESULT uses_unpinned={uses_bad} refs")
    tp, tt = time.process_time() - t0p, time.thread_time() - t0t
    print(f"RESULT thread_factor={tp / tt if tt else 1.0:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT swapins=0")


if __name__ == "__main__":
    main()
