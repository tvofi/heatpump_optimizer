#!/usr/bin/env python3
"""D11: per-merge conformance with the obligations the record calls enforced.

METRIC (one fraction per obligation, over a stated sample):
  A. review_verdict_present   -- a `Fix review: merge` verdict exists on the pull
                                 request, anywhere in its comments.
  B. verdict_by_other_account -- that verdict was written by a GitHub account
                                 OTHER than the pull request's author. This is the
                                 accountability question NIST AI 100-1 GOVERN 2.1
                                 asks: provable from the platform's records, not
                                 from a comment's word.
  C. github_review_object     -- the pull request carries at least one GitHub
                                 REVIEW (the object a ruleset can require), as
                                 opposed to a comment that says "review".
  D. verdict_at_merged_head   -- the verdict names the head that was merged.
  E. pr_contract_first_green  -- the FIRST `pr-contract` check run at that head
                                 concluded success (the commit's check-runs
                                 listing, which keeps a run that went red and
                                 then green; a summary drops it).
  F. disposition_row          -- `policy_lint.mjs --record` does not name the
                                 pull request as undispositioned.

SAMPLE, stated: the 40 most recent first-parent commits on `main` at or before
the baseline -- a contiguous census of the newest 40 merges, not a random draw.
The set of pull-request numbers is taken from GitHub's commit->PR association
(GraphQL `associatedPullRequests`) and compared with the set the commit SUBJECT
suffix implies; both sets are printed, because the subject suffix is free text
(#677) and the totals can agree while the sets do not.

INSTRUMENTED SYMBOLS: `.claude/workflows/policy_lint.mjs:checkRecord` (driven via
`--record`), and the `pr-contract` job of `.github/workflows/governance.yml`
through its check runs.

RUN (read-only, GraphQL only, ~3 queries; makes no write of any kind):
    cd <repo root> && PYTHONPATH=tests/hastub python3 tools/audit/round3/D11/conformance.py
Results are cached in tools/audit/round3/D11/conformance_raw.json; delete it to
re-fetch. Every figure is printed beside `api_failures`, because a refused call
a loop swallows prints as a real zero.

PERTURBATION: pass HPO_D11_N=5 to shrink the sample -- every fraction must be
recomputed over 5 and the printed sample list must shrink to 5. For obligation B,
the direction is fixed by construction: while the repository has one
collaborator, no sample can raise it above 0.

EXPECTED at baseline ae36eff19d8e542bc351b1ab31ad4167ec8e4ea1, N=40:
    RESULT sample_commits=40 +/-0
    RESULT commits_with_no_merged_pr=1 +/-0      (18d67a2, the v6.3.20 stamp)
    RESULT subject_only=[] and api_only=[]       (#677's trap does not bite here)
    RESULT A_review_verdict_present=0.5385 +/-0.03   (21/39)
    RESULT B_verdict_by_other_account=0.0000 +/-0.00 (0/39)
    RESULT C_github_review_object=0.0000 +/-0.00     (0/39)
    RESULT D_verdict_at_merged_head=0.5128 +/-0.03   (20/39)
    RESULT E_pr_contract_first_green=0.8718 +/-0.03  (34/39)
    RESULT F_disposition_row=0.9487 +/-0.03          (37/39)
    RESULT G_record_required_context_skipped=1.0000 +/-0.00 (39/39)
    RESULT api_failures=0 +/-0
MACHINE: 8-core Apple M1, 8 GB, gh 2.98.0, python3 3.11.5.
"""
import json
import os
import re
import subprocess
import sys
from pathlib import Path

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
RAW = HERE / "conformance_raw.json"
BASELINE = "ae36eff19d8e542bc351b1ab31ad4167ec8e4ea1"
N = int(os.environ.get("HPO_D11_N", "40"))
FAILURES = []
VERDICT_RE = re.compile(r"Fix review:\s*(merge|blocked|reject|revise|approve)", re.I)


def git(*a):
    return subprocess.run(["git", "-C", str(ROOT), *a],
                          capture_output=True, text=True, check=True).stdout


def gql(query):
    p = subprocess.run(["gh", "api", "graphql", "-f", f"query={query}"],
                       capture_output=True, text=True)
    if p.returncode != 0:
        FAILURES.append(p.stderr.strip()[:200])
        return None
    d = json.loads(p.stdout)
    if "errors" in d:
        FAILURES.append(json.dumps(d["errors"])[:300])
    return d.get("data")


def fetch(shas):
    frag = """
      %s: object(oid: "%s") { ... on Commit { oid
        associatedPullRequests(first: 3) { nodes {
          number title body mergedAt headRefOid
          author { login }
          mergeCommit { oid }
          reviews(first: 10) { totalCount nodes { author { login } state commit { oid } } }
          comments(first: 60) { totalCount nodes { author { login } createdAt body } }
        } } } }"""
    out = {}
    for i in range(0, len(shas), 20):
        chunk = shas[i:i + 20]
        body = "".join(frag % (f"c{i + j}", s) for j, s in enumerate(chunk))
        d = gql("query { repository(owner:\"tvofi\", name:\"heatpump_optimizer\") {" + body + "} }")
        if d:
            out.update({k: v for k, v in (d.get("repository") or {}).items() if v})
    return out


def fetch_checks(heads):
    frag = """
      %s: object(oid: "%s") { ... on Commit { oid
        checkSuites(first: 20) { nodes { checkRuns(first: 60) {
          nodes { name conclusion startedAt } } } } } }"""
    out = {}
    for i in range(0, len(heads), 12):
        chunk = heads[i:i + 12]
        body = "".join(frag % (f"h{i + j}", s) for j, s in enumerate(chunk))
        d = gql("query { repository(owner:\"tvofi\", name:\"heatpump_optimizer\") {" + body + "} }")
        if d:
            out.update({k: v for k, v in (d.get("repository") or {}).items() if v})
    return out


def main():
    lines = git("log", "--first-parent", f"--max-count={N}", "--format=%H\t%s", BASELINE).splitlines()
    shas = [ln.split("\t")[0] for ln in lines]
    subj = {}
    for ln in lines:
        sha, s = ln.split("\t", 1)
        m = re.search(r"\(#(\d+)\)$", s)
        subj[sha] = int(m.group(1)) if m else None

    if RAW.exists():
        raw = json.loads(RAW.read_text())
    else:
        raw = {"commits": fetch(shas)}
        heads = sorted({pr["headRefOid"]
                        for v in raw["commits"].values()
                        for pr in (v or {}).get("associatedPullRequests", {}).get("nodes", [])
                        if pr.get("mergedAt")})
        raw["checks"] = fetch_checks(heads)
        raw["api_failures"] = FAILURES
        RAW.write_text(json.dumps(raw, indent=1))
    FAILURES.extend(raw.get("api_failures", []))
    print(f"RESULT api_failures={len(FAILURES)} calls")
    for f in FAILURES[:5]:
        print(f"  FAILED {f[:160]}")
    if FAILURES:
        print("REFUSED: a swallowed refusal prints as a real zero; every fraction below is void")
        return 2

    checks_by_head = {}
    for v in raw["checks"].values():
        if not v:
            continue
        runs = [r for s in v["checkSuites"]["nodes"] for r in s["checkRuns"]["nodes"]]
        checks_by_head[v["oid"]] = runs

    # --- set comparison, never totals (#677) ------------------------------
    api_nums, subj_nums, rows = set(), set(), []
    for i, sha in enumerate(shas):
        node = raw["commits"].get(f"c{i}") or {}
        prs = [p for p in node.get("associatedPullRequests", {}).get("nodes", []) if p.get("mergedAt")]
        for p in prs:
            api_nums.add(p["number"])
        if subj[sha]:
            subj_nums.add(subj[sha])
        rows.append((sha, prs))
    print(f"RESULT sample_commits={len(shas)} commits")
    print(f"RESULT pr_numbers_from_api={len(api_nums)} numbers")
    print(f"RESULT pr_numbers_from_subject={len(subj_nums)} numbers")
    print(f"RESULT subject_only={sorted(subj_nums - api_nums)}")
    print(f"RESULT api_only={sorted(api_nums - subj_nums)}")
    print(f"RESULT commits_with_no_merged_pr={len([r for r in rows if not r[1]])} commits")
    for sha, prs in rows:
        if not prs:
            print(f"    NO PULL REQUEST  {sha[:7]}  {git('log','-1','--format=%s',sha).strip()[:70]}")

    seen, A, B, C, D, E, F = set(), 0, 0, 0, 0, 0, 0
    ANY = [0]
    G = [0, 0]
    total = 0
    undisp = record_undispositioned()
    for sha, prs in rows:
        for pr in prs:
            if pr["number"] in seen:
                continue
            seen.add(pr["number"])
            total += 1
            author = (pr.get("author") or {}).get("login")
            verdicts = [c for c in pr["comments"]["nodes"] if VERDICT_RE.search(c["body"] or "")]
            merges = [c for c in verdicts if re.search(r"Fix review:\s*merge", c["body"] or "", re.I)]
            A += 1 if merges else 0
            ANY[0] += 1 if verdicts else 0
            B += 1 if any((c.get("author") or {}).get("login") != author for c in merges) else 0
            C += 1 if pr["reviews"]["totalCount"] > 0 else 0
            head = pr["headRefOid"]
            D += 1 if any(head[:7] in (c["body"] or "") for c in merges) else 0
            runs = sorted([r for r in checks_by_head.get(head, []) if r["name"] == "pr-contract"],
                          key=lambda r: r["startedAt"] or "")
            E += 1 if (runs and runs[0]["conclusion"] == "SUCCESS") else 0
            F += 0 if pr["number"] in undisp else 1
            rec = [r for r in checks_by_head.get(head, []) if r["name"] == "record"]
            G[0] += 1 if (rec and all(r["conclusion"] == "SKIPPED" for r in rec)) else 0
            G[1] += 1 if rec else 0
    def frac(x):
        return x / total if total else float("nan")
    print(f"RESULT sample_pull_requests={total} pull_requests")
    print(f"RESULT A_review_verdict_present={frac(A):.4f} fraction  ({A}/{total})")
    print(f"RESULT A2_any_fix_review_verdict={frac(ANY[0]):.4f} fraction  ({ANY[0]}/{total})")
    print(f"RESULT B_verdict_by_other_account={frac(B):.4f} fraction  ({B}/{total})")
    print(f"RESULT C_github_review_object={frac(C):.4f} fraction  ({C}/{total})")
    print(f"RESULT D_verdict_at_merged_head={frac(D):.4f} fraction  ({D}/{total})")
    print(f"RESULT E_pr_contract_first_green={frac(E):.4f} fraction  ({E}/{total})")
    print(f"RESULT F_disposition_row={frac(F):.4f} fraction  ({F}/{total})")
    print(f"RESULT G_record_required_context_skipped={ (G[0]/G[1] if G[1] else float('nan')):.4f}"
          f" fraction  ({G[0]}/{G[1]} heads whose `record` check run(s) all concluded SKIPPED,"
          " while `record` is one of the ruleset's 18 required contexts)")
    print(f"RESULT record_undispositioned={sorted(undisp)}")
    return 0


def record_undispositioned():
    """Run the production instrument and read the numbers it refuses."""
    since = subprocess.run(["git", "-C", str(ROOT), "describe", "--tags", "--abbrev=0",
                            "--match", "v*", BASELINE],
                           capture_output=True, text=True).stdout.strip()
    p = subprocess.run(["node", ".claude/workflows/policy_lint.mjs", "--record", "--since", since],
                       cwd=str(ROOT), capture_output=True, text=True,
                       env={**os.environ, "GITHUB_TOKEN": os.environ.get("GITHUB_TOKEN", "")})
    nums = set(int(n) for n in re.findall(r"merged pull request #(\d+)", p.stdout))
    print(f"  policy_lint --record --since {since}: exit={p.returncode}, "
          f"{len(nums)} pull request(s) named")
    return nums


if __name__ == "__main__":
    sys.exit(main())
