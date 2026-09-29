#!/usr/bin/env python3
"""D11-s2: does the release path refuse a commit main never reviewed?

Metric (one line): over two arms -- the tagged commit IS on origin/main (null
control), and the tagged commit is an unmerged branch commit (test arm) -- the
number of arms in which `.github/workflows/release.yml`'s `release` job, its own
`run:` steps executed in order in a scratch clone, reaches `gh release create`
and the tree digest (i.e. would publish and attest).

Count key: whether the stubbed `gh` recorded a `release create` call AND the
"Digest the tag's tree" step printed a digest, both driven by the production
step scripts read from release.yml at run time (never re-typed here).

Arms and event paths: both `push: tags v*` (GITHUB_REF_NAME=tag, the path an
identity with contents:write reaches by pushing a tag) and `workflow_dispatch`
(DISPATCH_TAG), each on-main and off-main -> 4 cells.

Perturbation (`--perturb`): inserts ONE line into release.yml's "Resolve the tag"
step in this tree -- `git fetch -q origin main && git merge-base --is-ancestor
"$GITHUB_SHA" FETCH_HEAD || exit 1` -- and reverts it in `finally` (byte-checked).
Expected: off-main cells published 2 -> 0 (to_zero); on-main cells stay 2.

Run (from the tree root):
  PYTHONPATH=tests/hastub OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 \
  NUMEXPR_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 TMPDIR=<private tmp> \
  python3 tools/audit/round8/D11/s2_release_gate.py [--perturb]
Expected at baseline cdf82da: off_main_published=2 of 2, on_main_published=2 of 2 (exact).
Machine: 4-vCPU cloud container (round 8 BASELINE.md); counts are contention-immune.
Limits: GitHub-side tag rulesets are outside this harness; it measures what the
workflow itself refuses.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import argparse, shutil, subprocess, sys, tempfile, time
import yaml

WF = ".github/workflows/release.yml"
GUARD = '          git fetch -q origin main && git merge-base --is-ancestor "$GITHUB_SHA" FETCH_HEAD || exit 1\n'
ANCHOR = '          if [ "$EVENT_NAME" = "workflow_dispatch" ]; then\n'


def sh(cmd, cwd, env=None, check=True):
    r = subprocess.run(cmd, cwd=cwd, env=env, shell=isinstance(cmd, str),
                       capture_output=True, text=True, executable="/bin/bash" if isinstance(cmd, str) else None)
    if check and r.returncode:
        raise RuntimeError(f"{cmd}: {r.stderr}")
    return r


def run_cell(steps, work, origin, sha, event, tag):
    """Execute release.yml's run steps in order; return (published, digest_seen)."""
    for d in ("ghlog", "env"):
        p = os.path.join(work, ".." , d)
        if os.path.exists(p):
            os.remove(p)
    ghlog = os.path.abspath(os.path.join(work, "..", "ghlog"))
    genv = os.path.abspath(os.path.join(work, "..", "env"))
    open(genv, "w").close()
    bindir = os.path.abspath(os.path.join(work, "..", "bin"))
    os.makedirs(bindir, exist_ok=True)
    # gh stub: `gh release create TAG --target SHA ...` creates the tag on origin
    open(os.path.join(bindir, "gh"), "w").write(
        "#!/bin/bash\necho \"$@\" >> %s\n"
        "if [ \"$1 $2\" = 'release create' ]; then\n"
        "  tag=$3; shift 3; tgt=\n  while [ $# -gt 0 ]; do [ \"$1\" = --target ] && tgt=$2; shift; done\n"
        "  git -C %s tag -f \"$tag\" \"$tgt\" >/dev/null\nfi\n" % (ghlog, origin))
    os.chmod(os.path.join(bindir, "gh"), 0o755)
    sh(["git", "checkout", "-q", "--detach", sha], work)
    if event == "push":
        sh(["git", "-C", origin, "tag", "-f", tag, sha], work)
    digest = False
    for st in steps:
        if "run" not in st:
            continue
        env = dict(os.environ)
        for line in open(genv):
            if "=" in line:
                k, v = line.rstrip("\n").split("=", 1)
                env[k] = v
        env.update({"PATH": bindir + ":" + os.environ["PATH"], "GITHUB_ENV": genv,
                    "GITHUB_SHA": sha, "GITHUB_REF_NAME": tag if event == "push" else "main",
                    "EVENT_NAME": "workflow_dispatch" if event == "dispatch" else "push",
                    "DISPATCH_TAG": tag, "GH_TOKEN": "stub"})
        script = st["run"]
        r = subprocess.run(["bash", "-e", "-c", script], cwd=work, env=env, capture_output=True, text=True)
        if "tree digest sha256:" in r.stdout:
            digest = True
        if r.returncode:
            break
    published = os.path.exists(ghlog) and "release create" in open(ghlog).read()
    return published, digest


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--perturb", action="store_true")
    a = ap.parse_args()
    t0p, t0t = time.process_time(), time.thread_time()
    orig = open(WF, "rb").read()
    try:
        if a.perturb:
            txt = orig.decode()
            assert ANCHOR in txt
            open(WF, "w").write(txt.replace(ANCHOR, GUARD + ANCHOR, 1))
        wf = yaml.safe_load(open(WF))
        steps = wf["jobs"]["release"]["steps"]
    finally:
        open(WF, "wb").write(orig)
        assert open(WF, "rb").read() == orig
    tmp = tempfile.mkdtemp(prefix="s2rel-", dir=os.environ.get("TMPDIR"))
    try:
        origin = os.path.join(tmp, "origin.git")
        sh(["git", "clone", "-q", "--bare", "--shared", os.getcwd(), origin], tmp)
        base = sh(["git", "rev-parse", "HEAD"], os.getcwd()).stdout.strip()
        sh(["git", "-C", origin, "update-ref", "refs/heads/main", base], tmp)
        work = os.path.join(tmp, "work")
        sh(["git", "clone", "-q", "--shared", origin, work], tmp)
        sh(["git", "-c", "user.name=s2", "-c", "user.email=s2@x", "commit", "-q", "--allow-empty",
            "-m", "unmerged branch commit"], work)
        off = sh(["git", "rev-parse", "HEAD"], work).stdout.strip()
        sh(["git", "push", "-q", "origin", "HEAD:refs/heads/feature"], work)
        res = {}
        for arm, sha in (("on_main", base), ("off_main", off)):
            for ev in ("push", "dispatch"):
                tag = "v9.9.%d" % len(res)
                res[(arm, ev)] = run_cell(steps, work, origin, sha, ev, tag)
                print(f"CELL arm={arm} event={ev} sha={sha[:8]} published,digest={res[(arm, ev)]}")
        for arm in ("on_main", "off_main"):
            n = sum(1 for (a_, _), (p, d) in res.items() if a_ == arm and p and d)
            print(f"RESULT {arm}_published={n} of 2 cells")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print("RESULT perturbed=%d" % int(a.perturb))
    tp, tt = time.process_time() - t0p, time.thread_time() - t0t
    print("RESULT thread_factor=%.3f" % (tp / tt if tt else 1.0))
    print("RESULT load1=%.2f" % os.getloadavg()[0])
    sw = [l for l in open("/proc/vmstat") if l.startswith("pswpin")][0].split()[1]
    print("RESULT swapins=%s" % sw)


if __name__ == "__main__":
    main()
