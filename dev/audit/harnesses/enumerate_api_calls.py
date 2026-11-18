#!/usr/bin/env python3
"""enumerate_api_calls.py [SINCE] -- the REST reads Nightly's record-autofix job
makes in its "Enumerate the window's merges" step on one push to main, counted
offline (dev/audit/rca/ratelimit-recur.md).

    python3 dev/audit/harnesses/enumerate_api_calls.py           # window = last v* tag
    python3 dev/audit/harnesses/enumerate_api_calls.py v7.0.4

record_api_calls.sh's sibling: that harness counts Governance's `record` job,
this one the second reader of the same GITHUB_TOKEN bucket on every push to
main. It runs `record_row.enumerate_merges` over SINCE..HEAD with `_api`
replaced by a stub that logs each path and answers from the merge commits'
own "Merge pull request #N" subjects (both `/commits/<sha>/pulls` and
`/pulls/<n>`, so either shape of the function completes); no request leaves
the host. It REFUSES (rc 1) a window holding merges that it read nothing for,
and a merge whose subject names no pull request, rather than print a count
that measured nothing. A null control is an empty window: SINCE=HEAD reads 0.
`count(since, cwd)` is the same reading at the HEAD of any checkout, so
record_burst_replay.py reads each push's tip through it (a no-checkout
worktree) rather than a formula of its own.
"""
import os
import re
import subprocess
import sys
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
sys.path.insert(0, str(ROOT / "tools/audit/seat"))
import record_row  # noqa: E402


def git(cwd, *args):
    return subprocess.run(["git", "-C", str(cwd), *args], check=True,
                          capture_output=True, text=True).stdout


def count(since, cwd=ROOT):
    """(calls, merges) the enumeration makes over `since..HEAD` of `cwd`;
    raises record_row.Refuse where the count would be partial."""
    subject = dict(ln.split("\t", 1) for ln in git(
        cwd, "log", "--first-parent", "--format=%H\t%s", f"{since}..HEAD").splitlines())
    by_number = {}
    for sha, s in subject.items():
        if m := re.match(r"Merge pull request #(\d+) ", s):
            by_number[int(m.group(1))] = sha
    calls = []

    def pull(n):
        return {"number": n, "title": subject[by_number[n]], "state": "closed",
                "head": {"ref": "stub"}, "merge_commit_sha": by_number[n]}

    def stub(repo, path, token):
        calls.append(path)
        if path.startswith("/pulls/"):
            return pull(int(path.split("/")[2]))
        m = re.match(r"Merge pull request #(\d+) ", subject[path.split("/")[2]])
        return [pull(int(m.group(1)))] if m else []

    # enumerate_merges walks the working directory's HEAD.
    api, here = record_row._api, os.getcwd()
    record_row._api = stub
    os.chdir(cwd)
    try:
        merges = record_row.enumerate_merges("tvofi/heatpump_optimizer", since, "stub")
    finally:
        record_row._api = api
        os.chdir(here)
    if by_number and not calls:
        raise record_row.Refuse(f"{len(by_number)} merge(s) in {since}..HEAD and no "
                                "read logged; refusing a count that measured nothing")
    return len(calls), len(merges)


def main():
    since = sys.argv[1] if len(sys.argv) > 1 else git(
        ROOT, "describe", "--tags", "--abbrev=0", "--match", "v*").strip()
    try:
        calls, merges = count(since)
    except record_row.Refuse as why:
        sys.exit(f"enumerate_api_calls: refused, the count would be partial: {why}")
    print(f"ENUMERATE {calls} call(s) for {merges} merge(s) over "
          f"{since}..HEAD, per push to main")


if __name__ == "__main__":
    main()
