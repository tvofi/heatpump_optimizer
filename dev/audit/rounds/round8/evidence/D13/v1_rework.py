#!/usr/bin/env python3
"""D13 / round 8 / verifier v1 -- rework rounds, re-measured from git, not from the finder's walk.

METRIC (one line): for every window merge, each `Fix review:` verdict after the
first (issue comments + reviews + inline review comments, by time) is a REWORK
ROUND; a round whose predecessor was `merge` at a different head is a
RE-VERIFICATION, and each re-verification is classified by GIT: the three-dot
authored diff (git diff <main-before-merge>...<head> | git patch-id --stable) at
the old head against the new head -- `identical` (s11's "authored diff proved
byte-identical" carry path would have sufficed) or `changed`.
Also: commits old..new by kind (merge-of-main / bot-authored / content).

Independent of s1_yield.mjs: own verdict regex (not the wave's), own endpoint set
(adds /pulls/<n>/comments), own classification (git patch-id, not SHA inequality).
Inputs: the window's PR list from `git log --first-parent` subjects
("Merge pull request #N"), and the API via v1_gh (own cache under
/home/claude/audit-r8/tmp/D13-v1/v1cache).

COMMAND (tree root): PYTHONPATH=tests/hastub python3 tools/audit/round8/D13/v1_rework.py [--pin-head N]
PERTURBATION: --pin-head N rewrites PR N's verdict heads to its first verdict's head
(in memory): re-verifications fall by that PR's count; the NULL CONTROL is a
PR with one verdict (--pin-head on it moves nothing).
MACHINE: any; counts only, no timing claim.
"""
import argparse
import collections
import json
import re
import subprocess
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import v1_gh as G  # noqa: E402

SINCE, HEAD = "c310541", "cdf82daabcfe3777d98b31489f36df5555ec9d82"
VRE = re.compile(r"^Fix review:\s*(merge|blocked)\b\s*([0-9a-f]{40})?", re.I)


def git(*a, inp=None):
    return subprocess.run(["git", *a], capture_output=True, text=True, input=inp).stdout


def patch_id(base, head):
    d = git("diff", "-U0", f"{base}...{head}")
    out = git("patch-id", "--stable", inp=d).split()
    return out[0] if out else "EMPTY"


def verdicts(n):
    rows = []
    for c in G.pages(f"repos/{G.REPO}/issues/{n}/comments?per_page=100"):
        rows.append((c["created_at"], "issue", c["body"]))
    for c in G.pages(f"repos/{G.REPO}/pulls/{n}/reviews?per_page=100"):
        rows.append((c.get("submitted_at") or "", "review", c["body"]))
    for c in G.pages(f"repos/{G.REPO}/pulls/{n}/comments?per_page=100"):
        rows.append((c["created_at"], "inline", c["body"]))
    rows.sort(key=lambda r: r[0])
    out = []
    for at, ep, body in rows:
        first = (body or "").strip().split("\n")[0]
        m = VRE.match(first)
        if m:
            out.append({"at": at, "ep": ep, "word": m.group(1).lower(), "head": m.group(2)})
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pin-head", type=int)
    ap.add_argument("--verbose", action="store_true")
    a = ap.parse_args()
    log = git("log", "--first-parent", "--format=%H %P%x09%s", f"{SINCE}..{HEAD}").splitlines()
    merges = []
    for l in log:
        shas, subj = l.split("\t", 1)
        m = re.match(r"Merge pull request #(\d+)", subj)
        if m:
            s = shas.split()
            merges.append((int(m.group(1)), s[0], s[1]))
    print(f"window {SINCE}..{HEAD[:10]}: {len(merges)} merge subjects")
    kinds = collections.Counter()
    why = collections.Counter()
    mix = collections.Counter()
    per = {}
    n_withv = one_round = first_merge = 0
    for n, msha, main_before in merges:
        vs = verdicts(n)
        if a.pin_head == n and vs:
            for v in vs:
                v["head"] = vs[0]["head"]
        if not vs:
            continue
        n_withv += 1
        first_merge += vs[0]["word"] == "merge"
        one_round += len(vs) == 1 and vs[0]["word"] == "merge"
        for prev, cur in zip(vs, vs[1:]):
            if prev["word"] == "blocked":
                kinds["repair->" + cur["word"]] += 1
                continue
            if prev["head"] == cur["head"]:
                kinds["same-head->" + cur["word"]] += 1
                continue
            same = patch_id(main_before, prev["head"]) == patch_id(main_before, cur["head"])
            k = "reverify-identical-diff" if same else "reverify-changed-diff"
            kinds[k + "->" + cur["word"]] += 1
            per.setdefault(n, []).append(k)
            # the branch's own commits between the two heads (first-parent: main's
            # commits brought in by a merge are not the branch's work)
            revs = git("rev-list", "--first-parent", "--format=%P%x09%an%x09%s", "--no-commit-header",
                       f"{prev['head']}..{cur['head']}").splitlines()
            kset = set()
            for r in revs:
                par, an, _s = r.split("\t", 2)
                kk = "merge-commit" if len(par.split()) > 1 else "bot" if "[bot]" in an or an.endswith("bot") else "content"
                kset.add(kk)
                why[kk] += 1
            mix["+".join(sorted(kset)) or "(none)"] += 1
            if a.verbose:
                print(f"  #{n} {prev['head'][:8]}->{cur['head'][:8]} {k} commits={[r.split(chr(9))[1:] for r in revs]}")
    G.R("rounds_by_branch_commit_mix", dict(mix))
    total_extra = sum(kinds.values())
    rev = sum(v for k, v in kinds.items() if k.startswith("reverify"))
    G.R("verdict_prs", n_withv)
    G.R("first_pass_yield", f"{first_merge / n_withv:.4f}")
    G.R("one_round_yield", f"{one_round / n_withv:.4f}")
    G.R("extra_rounds", total_extra)
    G.R("extra_rounds_by_kind", dict(sorted(kinds.items())))
    G.R("reverify_rounds", rev)
    G.R("reverify_prs", {k: v for k, v in sorted(per.items())})
    G.R("commits_between_reverified_heads", dict(why))
    G.R("api_failures", len(G.FAILURES))


if __name__ == "__main__":
    main()
