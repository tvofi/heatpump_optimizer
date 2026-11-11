#!/usr/bin/env python3
"""D13 / round 8 / verifier v1 -- verdict coverage split by CODE-OWNED FILES, not by who approved.

METRIC (one line): a window merge (first-parent "Merge pull request #N" subject,
c310541..cdf82da) has NO VERDICT when none of its issue comments, reviews or inline
review comments has a trimmed first line matching ^Fix review:\\s*(merge|blocked);
merges are split by whether /pulls/<n>/files touches a path CODEOWNERS (at the
baseline) assigns an owner, using tools/audit/app_approve.sh's own matcher (copied
below, last-match-wins). Also reported: a LOOSE count (any line anywhere in any body
containing "fix review", case-insensitive) to catch verdicts written outside the
first line, and the approver split the finder used, for comparison.

Why this split: app_approve.sh refuses a PR with no verdict (its self-test line
"REFUSE: no Fix review verdict at all") and refuses a code-owned PR outright; the
owner's GitHub review has no such refusal. So the claim predicts: no-verdict merges
concentrate in the code-owned arm, and the non-owned arm's zero is the refusal
working (a mechanism, not an independent null).

COMMAND (tree root): PYTHONPATH=tests/hastub python3 tools/audit/round8/D13/v1_coverage.py [--drop N]
PERTURBATION: --drop N removes PR N's verdicts in memory: no_verdict rises by exactly 1
in N's arm. NULL CONTROL: --drop on a PR already without a verdict moves nothing.
MACHINE: any; counts only.
"""
import argparse
import collections
import fnmatch
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import v1_gh as G  # noqa: E402

SINCE, HEAD = "c310541", "cdf82daabcfe3777d98b31489f36df5555ec9d82"
POP = re.compile(r"^Fix review:\s*(merge|blocked)")


def git(*a):
    return subprocess.run(["git", *a], capture_output=True, text=True).stdout


def rules():
    out = []
    for line in git("show", f"{HEAD}:.github/CODEOWNERS").splitlines():
        line = line.split("#", 1)[0].split()
        if line:
            out.append((line[0], line[1:]))
    return out


def hit(pat, path):  # app_approve.sh's matcher, verbatim logic
    anchored = pat.startswith("/"); p = pat.strip("/")
    if p in ("", "*", "**"): return True
    if pat.endswith("/") or not any(ch in p for ch in "*?["):
        if anchored or "/" in p: return path == p or path.startswith(p + "/")
        return p in path.split("/")
    if anchored or "/" in p: return fnmatch.fnmatch(path, p) or fnmatch.fnmatch(path, p + "/*")
    return any(fnmatch.fnmatch(seg, p) for seg in path.split("/")) or fnmatch.fnmatch(path, p)


def owned(files, R):
    res = []
    for f in files:
        for path in {f["filename"], f.get("previous_filename")} - {None}:
            last = None
            for pat, who in R:
                if hit(pat, path): last = who
            if last: res.append(path)
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--drop", type=int)
    ap.add_argument("--verbose", action="store_true")
    a = ap.parse_args()
    R = rules()
    prs = []
    for l in git("log", "--first-parent", "--format=%s", f"{SINCE}..{HEAD}").splitlines():
        m = re.match(r"Merge pull request #(\d+)", l)
        if m:
            prs.append(int(m.group(1)))
    arm = collections.defaultdict(lambda: {"merges": 0, "no_verdict": 0, "prs": []})
    by_appr = collections.defaultdict(lambda: {"merges": 0, "no_verdict": 0})
    cross = collections.Counter()
    loose_only = []
    for n in prs:
        ic = G.pages(f"repos/{G.REPO}/issues/{n}/comments?per_page=100")
        rv = G.pages(f"repos/{G.REPO}/pulls/{n}/reviews?per_page=100")
        il = G.pages(f"repos/{G.REPO}/pulls/{n}/comments?per_page=100")
        pr = G.one(f"repos/{G.REPO}/pulls/{n}") or {}
        files = G.pages(f"repos/{G.REPO}/pulls/{n}/files?per_page=100")
        bodies = [c.get("body") or "" for c in ic + rv + il]
        has = any(POP.match(b.strip().split("\n")[0]) for b in bodies)
        if a.drop == n:
            has = False
        loose = any(re.search(r"fix review", b, re.I) for b in bodies + [pr.get("body") or ""])
        k = "code-owned" if owned(files, R) else "not-owned"
        appr = ("owner-approved" if any(r["user"]["login"] == "tvofi" and r["state"] == "APPROVED" for r in rv)
                else "app-approved" if any(r["user"]["login"] == "hpo-approver[bot]" and r["state"] == "APPROVED" for r in rv)
                else "none")
        arm[k]["merges"] += 1
        by_appr[appr]["merges"] += 1
        cross[(k, appr)] += 1
        if not has:
            arm[k]["no_verdict"] += 1
            arm[k]["prs"].append(n)
            by_appr[appr]["no_verdict"] += 1
            if loose:
                loose_only.append(n)
            if a.verbose:
                print(f"  #{n} {k} {appr} inline={len(il)} owned={owned(files, R)[:3]} :: {pr.get('title','')[:70]}")
    G.R("window_merges", len(prs))
    G.R("no_verdict", sum(v["no_verdict"] for v in arm.values()))
    G.R("no_verdict_by_code_owned_files", dict(arm))
    G.R("no_verdict_by_approver", dict(by_appr))
    G.R("files_x_approver", {f"{k[0]}|{k[1]}": v for k, v in sorted(cross.items())})
    G.R("no_verdict_but_loose_fix_review_text", loose_only)
    G.R("api_failures", len(G.FAILURES))


if __name__ == "__main__":
    main()
