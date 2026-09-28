#!/usr/bin/env python3
"""Finder's harness: does pr-contract refuse a PR diff that edits a stamp-owned item?

Usage (from a checkout of this repository):
  python3 tools/audit/ci-version-edit/pr_contract_shapes.py <commit-ish>

Builds a standalone scratch repository whose main is the measured commit, then
constructs one pull-request head per shape and runs, in a checkout of that
head, every `pr-contract` step of .github/workflows/governance.yml (as the
measured commit has it) whose `run:` invokes tools/audit/prepr.sh -- the
workflow's own commands, not a copy. Prints one row per shape with the
combined exit status; a row is REFUSED when any such step exits non-zero.
It also prints how many such steps it ran per shape, so an empty set is
visible rather than read as "passes".
"""
import json, os, re, subprocess, sys, tempfile

import yaml

SRC = os.getcwd()
REV = sys.argv[1]


def git(*a, cwd, check=True):
    p = subprocess.run(["git", *a], cwd=cwd, capture_output=True, text=True)
    if check and p.returncode:
        raise SystemExit(f"git {' '.join(a)}: {p.stderr}")
    return p.stdout.strip()


root = tempfile.mkdtemp(prefix="hvh-")
bare = os.path.join(root, "origin.git")
work = os.path.join(root, "work")
git("clone", "-q", "--no-local", SRC, work, cwd=root)
git("checkout", "-q", "--detach", git("rev-parse", REV, cwd=SRC), cwd=work)
for k, v in (("user.name", "h"), ("user.email", "h@h")):
    git("config", k, v, cwd=work)
B = git("rev-parse", "HEAD", cwd=work)
MAN = "custom_components/heatpump_optimizer/manifest.json"


def commit(parent, edits, msg):
    git("checkout", "-q", "--detach", parent, cwd=work)
    for path, fn in edits:
        full = os.path.join(work, path)
        with open(full) as f:
            text = f.read()
        with open(full, "w") as f:
            f.write(fn(text))
        git("add", path, cwd=work)
    git("commit", "-q", "-m", msg, cwd=work)
    return git("rev-parse", "HEAD", cwd=work)


bump_version = ("VERSION", lambda t: "9.9.9\n")
bump_manifest = (MAN, lambda t: re.sub(r'"version": "[^"]*"', '"version": "9.9.9"', t))
other_manifest = (MAN, lambda t: t.replace('"domain": "heatpump_optimizer",',
                                           '"domain": "heatpump_optimizer",\n  "zz_probe": 1,', 1))
notes_heading = ("RELEASE_NOTES.md", lambda t: t.replace("\n## ", "\n## v9.9.9\n\nx\n\n## ", 1))
docs = ("docs/HANDOVER.md", lambda t: t + "\nprobe line\n")

main2 = commit(B, [bump_version, bump_manifest, notes_heading], "v9.9.9 stamp")
stale = commit(B, [docs], "docs only, forked before the stamp")
git("checkout", "-q", "--detach", stale, cwd=work)
git("merge", "-q", "--no-ff", "-m", "merge main", main2, cwd=work)
merged = git("rev-parse", "HEAD", cwd=work)

shapes = [
    ("VERSION edit", B, commit(B, [bump_version], "bump VERSION"), True),
    ("manifest version edit", B, commit(B, [bump_manifest], "bump manifest"), True),
    ("notes heading edit", B, commit(B, [notes_heading], "notes heading"), True),
    ("all three (stamp-shaped branch)", B,
     commit(B, [bump_version, bump_manifest, notes_heading], "forged stamp"), True),
    ("docs only (null)", B, commit(B, [docs], "docs"), False),
    ("manifest non-version key (null)", B, commit(B, [other_manifest], "key"), False),
    ("main moved past a stamp, branch unmerged (null)", main2, stale, False),
    ("branch merged a stamped main (null)", main2, merged, False),
]

wf = yaml.safe_load(git("show", f"{B}:.github/workflows/governance.yml", cwd=work))
steps = [s for s in wf["jobs"]["pr-contract"]["steps"]
         if "tools/audit/prepr.sh" in (s.get("run") or "")]

git("init", "-q", "--bare", bare, cwd=root)
git("remote", "remove", "origin", cwd=work, check=False)
git("remote", "add", "origin", bare, cwd=work)
wrong = 0
for name, main, head, want_refused in shapes:
    git("push", "-q", "-f", "origin", f"{main}:refs/heads/main", cwd=work)
    git("update-ref", "-d", "refs/remotes/origin/main", cwd=work, check=False)
    git("checkout", "-q", "--detach", head, cwd=work)
    env = dict(os.environ, PR_HEAD=head, PR_BASE=main,
               GITHUB_EVENT_NAME="pull_request")
    rcs = []
    for s in steps:
        p = subprocess.run(["bash", "-eo", "pipefail", "-c", s["run"]], cwd=work,
                           env=env, capture_output=True, text=True)
        rcs.append(p.returncode)
    refused = any(rcs)
    ok = refused == want_refused
    wrong += not ok
    print(f"{'ok ' if ok else 'BAD'} {'REFUSED' if refused else 'passed '} "
          f"steps={len(rcs)} rcs={rcs} want={'refused' if want_refused else 'passed'}  {name}")
print(f"measured commit {B[:12]}; {wrong} shape(s) not as the rule requires")
sys.exit(1 if wrong else 0)
