#!/usr/bin/env python3
"""R11-PRE-RELAY-REBUILD carry 0: #3358's silent skip, replayed on its real commits.

#3358 (branch fix/r10-combi-tank-pr) sat behind handoff/r10-combi-tank-pr 62542627 for
hours with no trace on the relay's level. This drives one `cloud_relay.sh pass` from a
given seat directory against a scratch origin holding those commits (objects borrowed
from this checkout through alternates, refs written directly, nothing pushed):

  case     PR head    handoff/r10-combi-tank-pr   handoff/r10-combi-tank   bodied
  defect   88f4d521   62542627 (+ body)            577c6974 (+ body)        r10-combi-tank's
  null     d07f8e9e   62542627 (+ body)            577c6974 (+ body)        both

577c6974 is the head's first parent and stands for the older handoff the relay had applied
(its last update of #3358 ended OK on 2026-11-09 at an older tip); d07f8e9e is the head the
handoff was applied at by hand, which contains 62542627. update_pr.sh, approve and dispatch
are stubs; the stub update records its arguments. Prints, per case:

  RESULT <case>_updated=<0|1> <case>_owed=<level lines naming the PR or the -pr handoff>

Defect at the base seat: updated=0 owed=0 (the silent skip). At the fixed seat: updated=1.
Null at either seat: updated=0 owed=0 (a head holding its handoff is owed nothing).

    python3 dev/audit/harnesses/r11_relay_3358_skip.py --seat tools/audit/seat
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
import tempfile
from pathlib import Path


def repo_root(start):
    """The directory holding custom_components/heatpump_optimizer/manifest.json."""
    from pathlib import Path
    here = Path(start).resolve()
    if here.is_file():
        here = here.parent
    marker = Path("custom_components") / "heatpump_optimizer" / "manifest.json"
    for cand in (here, *here.parents):
        if (cand / marker).is_file():
            return cand
    raise RuntimeError(f"no repository root above {start}")


ROOT = repo_root(__file__)
sys.path.insert(0, str(ROOT / "tests"))
from throwaway_git import throwaway_git_init  # noqa: E402  the scratch repositories' one builder
PR = "3358"
BRANCH = "fix/r10-combi-tank-pr"
HEAD_DEFECT = "88f4d521eb55e62a5b11246396c3f298e932d5b9"
HEAD_NULL = "d07f8e9ea5a78bf44ea405ef233ae11ad7e1c211"
HANDOFF_PR = "6254262796cdec57bec1dec5c0d038ba933a215a"
HANDOFF_OLD = "577c6974205926e7dbaa178b91af96a229ea02f3"
MAIN = "b8f67a775137a8032d5c71b34ea64165c1d4613a"


def git(*argv: str, cwd: Path, env=None, stdin: str | None = None) -> str:
    return subprocess.run(["git", *argv], cwd=cwd, env=env, input=stdin, text=True,
                          capture_output=True, check=True).stdout.strip()


def body_commit(origin: Path, names: str) -> str:
    """An orphan commit holding BODY.md that names the handoff tip (HELD-BODY reads its first 8)."""
    blob = git("hash-object", "-w", "--stdin", cwd=origin, stdin=f"Closes #9999\n\nCode head: {names}\n")
    tree = git("mktree", cwd=origin, stdin=f"100644 blob {blob}\tBODY.md\n")
    env = dict(os.environ, GIT_AUTHOR_NAME="h", GIT_AUTHOR_EMAIL="h@h", GIT_COMMITTER_NAME="h",
               GIT_COMMITTER_EMAIL="h@h")
    return git("commit-tree", tree, "-m", "body", cwd=origin, env=env)


def run_case(seat: Path, case: str, head: str, scratch: Path) -> "tuple[int, int]":
    d = scratch / case
    origin, work, state = d / "o.git", d / "w", d / "state"
    for p in (origin, work, state, d / "bus"):
        p.mkdir(parents=True)
    objects = git("rev-parse", "--path-format=absolute", "--git-common-dir", cwd=ROOT) + "/objects"
    throwaway_git_init(origin, "-q", "--bare")
    (origin / "objects" / "info" / "alternates").write_text(objects + "\n")
    bodies = {t: body_commit(origin, tip) for t, tip in (("r10-combi-tank-pr", HANDOFF_PR), ("r10-combi-tank", HANDOFF_OLD))}
    for ref, sha in (("main", MAIN), (BRANCH, head), ("handoff/r10-combi-tank-pr", HANDOFF_PR),
                     ("handoff/r10-combi-tank", HANDOFF_OLD), ("handoff-body/r10-combi-tank-pr", bodies["r10-combi-tank-pr"]),
                     ("handoff-body/r10-combi-tank", bodies["r10-combi-tank"])):
        git("update-ref", f"refs/heads/{ref}", sha, cwd=origin)
    throwaway_git_init(work, "-q")
    (work / ".git" / "objects" / "info" / "alternates").write_text(objects + "\n")
    git("remote", "add", "origin", str(origin), cwd=work)
    applied = ["r10-combi-tank " + bodies["r10-combi-tank"]]
    if case == "null":
        applied.append("r10-combi-tank-pr " + bodies["r10-combi-tank-pr"])
    (state / "cloud-handoff-bodied").write_text("\n".join(applied) + "\n")
    stubs = d / "stubs"
    stubs.mkdir()
    for name, text in (("prs", f"printf '{PR}\\t{BRANCH}\\t{head}\\n'"), ("merged", ":"),
                       ("update", f"echo \"$@\" >> {d}/updated"), ("approve", ":"),
                       ("dispatch", "echo 'bus-nonce: 0123456789abcdef0123456789abcdef'")):
        (stubs / name).write_text(f"#!/bin/sh\n{text}\n")
        (stubs / name).chmod(0o755)
    env = {k: v for k, v in os.environ.items() if not k.startswith(("GIT_", "HPO_"))}
    env.update(HPO_STATE_DIR=str(state), HPO_BUS_STATE=str(d / "bus"), HPO_RELAY_PRS=str(stubs / "prs"),
               HPO_RELAY_MERGED=str(stubs / "merged"), HPO_RELAY_UPDATE=str(stubs / "update"),
               HPO_RELAY_APPROVE=str(stubs / "approve"), HPO_RELAY_DISPATCH=str(stubs / "dispatch"))
    log = state / "cloud-relay.log"
    subprocess.run(["bash", str(seat / "cloud_relay.sh"), "pass", "--log", str(log)], cwd=work, env=env,
                   capture_output=True, text=True, timeout=600)
    updated = (d / "updated").read_text() if (d / "updated").exists() else ""
    level = Path(str(log) + ".level")
    owed = [l for l in (level.read_text().splitlines() if level.exists() else [])
            if f"#{PR}" in l or "handoff/r10-combi-tank-pr" in l]
    return int(f"{BRANCH} {HANDOFF_PR}" in updated), len(owed)


def main(argv) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--seat", default=str(ROOT / "tools" / "audit" / "seat"), help="the seat directory whose cloud_relay.sh runs")
    a = ap.parse_args(argv)
    seat = Path(a.seat).resolve()
    for sha in (HEAD_DEFECT, HEAD_NULL, HANDOFF_PR, HANDOFF_OLD, MAIN):
        if subprocess.run(["git", "cat-file", "-e", f"{sha}^{{commit}}"], cwd=ROOT).returncode:
            print(f"UNAVAILABLE: {sha} is not in this checkout (git fetch --unshallow origin)")
            return 3
    with tempfile.TemporaryDirectory(prefix="hpo-r11-3358-") as tmp:
        for case, head in (("defect", HEAD_DEFECT), ("null", HEAD_NULL)):
            u, o = run_case(seat, case, head, Path(tmp))
            print(f"RESULT {case}_updated={u} {case}_owed={o}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
