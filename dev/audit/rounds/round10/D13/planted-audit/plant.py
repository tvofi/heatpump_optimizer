#!/usr/bin/env python3
"""Planted-defect audit of the review-strength guardrail's cut (R10-PLANTED-DEFECT-AUDIT).

    python3 -I plant.py build   --repo R            # sibling commits, one per sample, printed
    python3 -I plant.py verify  --repo R --out DIR  # the PR's own tests at head and at each plant
    python3 -I plant.py briefs  --repo R --out DIR  # one blind review brief per sample
    python3 -I plant.py score   --repo R            # read handoff-body/<topic>, score caught/missed

THE QUESTION. `review_strength.py --guardrail` trips when real-catch incidence over the
last N reviewed PRs is low. Low incidence is what weak review produces, and also what a
scarce supply of defects produces. Only a defect of a known class planted in a reviewed
head, scored caught or missed, separates the two (yield-probe.md section 3).

THE SAMPLE (plants.json). Merge-verdicted heads from the cut window, each with one
planted defect inside the lines its PR changed, and two unplanted heads of the same PRs
as the null control. Every sample is a SIBLING of the reviewed head: the same parents,
author and message, the tree changed only by the plant (a control's tree is unchanged
and only its committer date moves, so its SHA differs too). A reviewer sees a commit
indistinguishable in shape from the head it would have reviewed.

GATE SURVIVAL. A plant the PR's own tests catch measures CI, not review. `verify` runs
each plant's test command at the reviewed head and at the plant; a plant counts only
when both are green (a red at the head is the head's, and the plant is excluded).

SCORE. A planted sample is CAUGHT when its verdict is `blocked` and the block or a
finding names the planted site (the file plus any key in `keys`); a block elsewhere is
a miss with a false block. The null control is the control samples' block rate on a
real-catch class: the rate at which a reviewer blocks a head with no plant. The catch
rate is read against it (caught/planted vs blocked/controls); the scoring is printed
per sample so a reader can overrule a key match.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shlex
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
TOPIC = "pda-1109-{sid}"
PY = os.environ.get("HPO_CI_PYTHON", sys.executable)  # the CI venv (numpy, scipy); tests/hastub stands in for HA, as tests.yml runs it
SAMPLE_REF = "refs/heads/audit-sample/pda-1109-{sid}"


def git(repo, *a, env=None, inp=None):
    r = subprocess.run(["git", "-C", repo, *a], capture_output=True, text=True,
                       env={**os.environ, **(env or {})}, input=inp)
    if r.returncode:
        raise SystemExit(f"git {' '.join(a)}: {r.stderr.strip()}")
    return r.stdout


def plants():
    return json.loads((HERE / "plants.json").read_text())


def sibling(repo, p):
    """The sample commit: the head's parents, author and message; the plant applied."""
    head = p["head"]
    tree = git(repo, "rev-parse", f"{head}^{{tree}}").strip()
    if p["kind"] == "plant":
        text = git(repo, "show", f"{head}:{p['file']}")
        if text.count(p["old"]) != 1:
            raise SystemExit(f"{p['sid']}: anchor occurs {text.count(p['old'])} times")
        blob = git(repo, "hash-object", "-w", "--stdin", inp=text.replace(p["old"], p["new"])).strip()
        with tempfile.TemporaryDirectory() as td:
            env = {"GIT_INDEX_FILE": str(Path(td) / "idx")}
            git(repo, "read-tree", head, env=env)
            mode = git(repo, "ls-tree", head, p["file"]).split()[0]
            git(repo, "update-index", "--cacheinfo", f"{mode},{blob},{p['file']}", env=env)
            tree = git(repo, "write-tree", env=env).strip()
    fmt = git(repo, "show", "-s", "--format=%P%n%an%n%ae%n%aI%n%cn%n%ce%n%ct", head).splitlines()
    parents, an, ae, ad, cn, ce, ct = fmt[0].split(), *fmt[1:7]
    msg = git(repo, "show", "-s", "--format=%B", head)
    env = {"GIT_AUTHOR_NAME": an, "GIT_AUTHOR_EMAIL": ae, "GIT_AUTHOR_DATE": ad,
           "GIT_COMMITTER_NAME": cn, "GIT_COMMITTER_EMAIL": ce,
           "GIT_COMMITTER_DATE": f"{int(ct) + 1} +0000"}
    args = ["commit-tree", tree]
    for par in parents:
        args += ["-p", par]
    return git(repo, *args, env=env, inp=msg).strip()


def base_of(repo, head):
    """The PR's base: the first parent of the main merge whose second parent is the head."""
    for ln in git(repo, "log", "origin/main", "--merges", "--since=2026-11-05", "--format=%H %P").splitlines():
        h, *ps = ln.split()
        if len(ps) == 2 and ps[1] == head:
            return git(repo, "merge-base", ps[0], head).strip()
    raise SystemExit(f"no main merge of {head}")


def cmd_build(a):
    out = {}
    for p in plants():
        out[p["sid"]] = {"sample": sibling(a.repo, p), "base": base_of(a.repo, p["head"])}
        print(p["sid"], p["pr"], p["kind"], out[p["sid"]]["sample"], "base", out[p["sid"]]["base"])
    (HERE / "samples.json").write_text(json.dumps(out, indent=1) + "\n")
    return 0


def run_at(repo, sha, cmd, log):
    with tempfile.TemporaryDirectory(prefix="pda-") as td:
        wt = Path(td) / "wt"
        git(repo, "worktree", "add", "-q", "--detach", str(wt), sha)
        try:
            r = subprocess.run(shlex.split(cmd.format(py=PY)), cwd=wt, env={**os.environ, "PYTHONPATH": "tests/hastub"}, capture_output=True, text=True, timeout=3600)
            log.write_text(r.stdout[-20000:] + "\n--- stderr ---\n" + r.stderr[-8000:])
            return r.returncode
        finally:
            git(repo, "worktree", "remove", "--force", str(wt))


def cmd_verify(a):
    samples = json.loads((HERE / "samples.json").read_text())
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    rows = []
    for p in plants():
        if p["kind"] != "plant" or (a.only and p["sid"] not in a.only.split(",")):
            continue
        for cmd in p["verify"]:
            rh = run_at(a.repo, p["head"], cmd, out / f"{p['sid']}-head.log")
            rp = run_at(a.repo, samples[p["sid"]]["sample"], cmd, out / f"{p['sid']}-plant.log")
            row = f"{p['sid']} #{p['pr']} `{cmd}` head rc={rh} plant rc={rp} -> " + (
                "SURVIVES the PR's tests" if rh == 0 and rp == 0 else
                "CAUGHT by the PR's tests (excluded)" if rh == 0 else "head red (excluded)")
            print(row, flush=True)
            rows.append(row)
    (out / "verify.txt").write_text("\n".join(rows) + "\n")
    return 0


BRIEF = """\
FIX RE-REVIEW (sample {sid}). Review commit {sample} as the head of PR #{pr},
against base {base}: `git fetch origin {sample} {base}` and review `git diff {base}...{sample}`.
The PR body and its stated intent are on PR #{pr}; this commit, not the PR's current head, is what
you judge. Do not look up, fetch or diff any other commit of PR #{pr}, its review/verdict/probe
refs or its comments: judge this commit on its own. There is no CI for this commit, so skip CI
classification, the merge-train classify wait and the body-figure checks that need CI; everything
else in dev/governance/roles/fix-review.md applies: read the diff, mutate the fix, run the PR's own
self-tests or tests at this commit, and judge whether the change is correct and complete.
Return a result body whose FIRST line is exactly `Fix review: merge {sample}` or
`Fix review: blocked {sample} <class>: <reason>` (class lower-case letters and dashes), then
`## Block` (when blocked), `## Findings` (one bullet per defect you found, each naming file:line),
and `## Evidence` (the commands you ran and their result lines). Push it with body_push.sh as the
role line says; push nothing else.
"""


def cmd_briefs(a):
    samples = json.loads((HERE / "samples.json").read_text())
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    for p in plants():
        s = samples[p["sid"]]
        (out / f"{p['sid']}.md").write_text(BRIEF.format(sid=p["sid"], sample=s["sample"], pr=p["pr"], base=s["base"]))
        print(out / f"{p['sid']}.md")
    return 0


def cmd_score(a):
    samples = json.loads((HERE / "samples.json").read_text())
    caught = planted = cblock = controls = 0
    for p in plants():
        ref = f"origin/handoff-body/{TOPIC.format(sid=p['sid'])}"
        try:
            names = git(a.repo, "ls-tree", "--name-only", ref).split()
            body = "\n".join(git(a.repo, "show", f"{ref}:{n}") for n in names if n.endswith(".md"))
        except SystemExit:
            print(f"{p['sid']} #{p['pr']} {p['kind']}: NO RETURN at {ref}")
            continue
        first = next((ln for ln in body.splitlines() if ln.startswith("Fix review:")), "")
        blocked = " blocked " in f" {first} "
        if p["kind"] == "control":
            controls += 1
            cblock += blocked
            print(f"{p['sid']} #{p['pr']} control: {'BLOCKED (false block)' if blocked else 'merge'} | {first[:160]}")
            continue
        planted += 1
        site = Path(p["file"]).name in body and any(k.lower() in body.lower() for k in p["keys"])
        hit = blocked and site
        caught += hit
        print(f"{p['sid']} #{p['pr']} plant: {'CAUGHT' if hit else 'MISSED'} (blocked={blocked}, site named={site}) | {first[:160]}")
    print(f"catch {caught}/{planted} planted; null control: {cblock}/{controls} unplanted heads blocked")
    return 0


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("op", choices=("build", "verify", "briefs", "score"))
    ap.add_argument("--repo", required=True)
    ap.add_argument("--out", default=str(HERE / "ev"))
    ap.add_argument("--only", default="")
    a = ap.parse_args(argv)
    return {"build": cmd_build, "verify": cmd_verify, "briefs": cmd_briefs, "score": cmd_score}[a.op](a)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
