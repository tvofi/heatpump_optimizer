#!/usr/bin/env python3
"""Second path: does a single-parent PR-branch head shaped like a stamp pass `fast`'s claims hygiene?

Usage (from a checkout of this repository):
  python3 tools/audit/ci-version-edit/recheck_stamp_forgery.py <commit-ish>

Builds a scratch clone whose base carries one claim (`config_flow`), then a
branch commit forging a stamp: VERSION and manifest bumped, a notes heading,
both claim files re-stamped for the new VERSION with EMPTY lists -- which
deletes the base's claim. Runs the measured tree's own
`tests/env_drift.py --claims-only <ref>` (what tests/run.sh runs always) at
three CI shapes, with the environment each run carries:

  recheck   workflow_dispatch on the branch ref (the closures-autofix
            dispatch, or a manual one): HEAD = branch tip, ONE parent,
            ref = merge-base origin/main HEAD (tests.yml's recheck arm).
  pr-merge  the pull_request run: HEAD = refs/pull/N/merge, TWO parents.
  main-push the real stamp pushed to main: HEAD = the stamp, ref = HEAD^1.
"""
import os, re, subprocess, sys, tempfile

SRC = os.getcwd()
REV = sys.argv[1]


def git(*a, cwd):
    p = subprocess.run(["git", *a], cwd=cwd, capture_output=True, text=True)
    if p.returncode:
        raise SystemExit(f"git {' '.join(a)}: {p.stderr}")
    return p.stdout.strip()


root = tempfile.mkdtemp(prefix="hvh2-")
w = os.path.join(root, "w")
git("clone", "-q", "--no-local", SRC, w, cwd=root)
git("checkout", "-q", "--detach", git("rev-parse", REV, cwd=SRC), cwd=w)
git("config", "user.name", "h", cwd=w); git("config", "user.email", "h@h", cwd=w)
ver = open(os.path.join(w, "VERSION")).read().strip()
major, minor, patch = map(int, ver.split("."))
new = f"{major}.{minor}.{patch + 1}"
CL, CCL = "tests/golden/claimed_drift.txt", "tests/golden/card_claimed_drift.txt"
MAN = "custom_components/heatpump_optimizer/manifest.json"


def edit(path, fn):
    full = os.path.join(w, path)
    t = open(full).read()
    open(full, "w").write(fn(t))
    git("add", path, cwd=w)


edit(CL, lambda t: t.rstrip("\n") + "\nconfig_flow  # probe claim on the base\n")
git("commit", "-q", "-m", "base carries a claim", cwd=w)
base = git("rev-parse", "HEAD", cwd=w)

edit("VERSION", lambda t: new + "\n")
edit(MAN, lambda t: re.sub(r'"version": "[^"]*"', f'"version": "{new}"', t))
edit("RELEASE_NOTES.md", lambda t: t.replace("\n## ", f"\n## v{new}\n\nx\n\n## ", 1))
for f in (CL, CCL):
    edit(f, lambda t: "\n".join(
        l for l in t.replace(f"# claims-for: {ver}", f"# claims-for: {new}").split("\n")
        if not l.startswith("config_flow")) )
git("commit", "-q", "-m", "forged stamp on a branch", cwd=w)
forged = git("rev-parse", "HEAD", cwd=w)
git("checkout", "-q", "--detach", base, cwd=w)
git("merge", "-q", "--no-ff", "-m", "refs/pull/N/merge", forged, cwd=w)
prmerge = git("rev-parse", "HEAD", cwd=w)

rows = [
    ("recheck (dispatch on branch)", forged, base,
     {"GITHUB_ACTIONS": "true", "GITHUB_EVENT_NAME": "workflow_dispatch",
      "GITHUB_REF": "refs/heads/ci/forged"}, True),
    ("pr-merge (pull_request run)", prmerge, base,
     {"GITHUB_ACTIONS": "true", "GITHUB_EVENT_NAME": "pull_request",
      "GITHUB_REF": "refs/pull/1/merge"}, True),
    ("main-push (a real stamp, null)", forged, base,
     {"GITHUB_ACTIONS": "true", "GITHUB_EVENT_NAME": "push",
      "GITHUB_REF": "refs/heads/main"}, False),
    ("schedule on main at the stamp (null)", forged, base,
     {"GITHUB_ACTIONS": "true", "GITHUB_EVENT_NAME": "schedule",
      "GITHUB_REF": "refs/heads/main"}, False),
]
bad = 0
for name, head, ref, env, want_refused in rows:
    git("checkout", "-q", "--detach", head, cwd=w)
    parents = len(git("rev-list", "--parents", "-n", "1", "HEAD", cwd=w).split()) - 1
    e = {k: v for k, v in os.environ.items() if not k.startswith("GITHUB_")}
    e.update(env, PYTHONPATH="tests/hastub")
    p = subprocess.run([sys.executable, "tests/env_drift.py", "--claims-only", ref],
                       cwd=w, env=e, capture_output=True, text=True)
    refused = p.returncode != 0
    ok = refused == want_refused
    bad += not ok
    first = (p.stdout.strip().splitlines() or ["(no output)"])[0][:70]
    print(f"{'ok ' if ok else 'BAD'} rc={p.returncode} parents={parents} "
          f"want={'refused' if want_refused else 'passed'}  {name}: {first}")
print(f"measured {git('rev-parse', '--short=12', REV, cwd=SRC)}; {bad} row(s) not as the rule requires")
sys.exit(1 if bad else 0)
