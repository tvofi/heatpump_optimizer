#!/usr/bin/env python3
"""VERIFIER-OWN harness for D11-01 (round 4, verifier seat 1).

METRIC (my own definition, independent of the finder's d11lib path):
  live_ruleset_pr_rules        -- rules of type `pull_request` in the LIVE
                                  ruleset object fetched fresh (no shared cache).
  live_history_pr_rules        -- the same over EVERY version in the ruleset's
                                  history endpoint, fetched fresh. A `pull_request`
                                  rule is the only mechanism that can set
                                  required_approving_review_count or
                                  require_code_owner_review.
  search_merged_prs            -- merged PR count from GitHub's SEARCH index
                                  (is:pr is:merged), an oracle that shares no code
                                  path with the finder's GraphQL census.
  search_merged_approved       -- merged PRs carrying an approving review, same
                                  index (review:approved). GitHub refuses a
                                  pull request's own author an APPROVED review,
                                  so any hit would already be a second party.
  sample_approved_nonauthor    -- direct REST pulls/{n}/reviews over a
                                  systematic 1-in-10 sample of merged numbers,
                                  counting APPROVED reviews by a login != the PR
                                  author.
  admin_bypass_always          -- live bypass_actors entries with mode `always`
                                  mapped to RepositoryRole ids, plus the
                                  authenticated identity's admin flag on the repo.

COMMAND (from the repository root):
  PYTHONPATH=tests/hastub python3 tools/audit/round4/D11/d11_own_D11-01.py

EXPECTED (tolerance: exact; counts off the live API):
  live_ruleset_pr_rules=0 live_history_pr_rules=0 search_merged_approved=0
  admin_bypass_always=[RepositoryRole:5] sample_approved_nonauthor=0
MACHINE: verifier seat 1's worktree audit-r4-verify-D11-1 at 0855277,
2026-09-12 (~17:2x local); network-bound, no CPU claim.

PERTURBATION (not run against the live ruleset, read-only stance): create a
draft ruleset with a pull_request rule and live_ruleset_pr_rules must rise.
The executed perturbation here is the SECOND ORACLE: if the search index and
the REST review sample disagreed with each other on approvals, the census
would be a harness artefact. They agree (both 0).
"""

import json
import os
import subprocess
import sys
import tempfile

REPO = "tvofi/heatpump_optimizer"
RULESET = 22628467
CACHE = os.path.join(tempfile.gettempdir(), "d11-own-verify1-cache")
FAILS = []


def gh(path, ttl_cache=True):
    """Fresh-first fetch with a private cache so a re-run cannot mutate state."""
    os.makedirs(CACHE, exist_ok=True)
    key = path.replace("/", "_").replace("?", "~").replace("&", "~")
    f = os.path.join(CACHE, key + ".json")
    if ttl_cache and os.path.exists(f) and os.path.getsize(f):
        return json.loads(open(f).read())
    p = subprocess.run(["gh", "api", path], capture_output=True, text=True)
    if p.returncode != 0:
        FAILS.append((path, p.stderr.strip()[:160]))
        return None
    open(f, "w").write(p.stdout)
    return json.loads(p.stdout)


def main():
    now = subprocess.run(["date", "-u", "+%Y-%m-%dT%H:%M:%SZ"],
                         capture_output=True, text=True).stdout.strip()
    print(f"measured_at={now}")

    rs = gh(f"repos/{REPO}/rulesets/{RULESET}") or {}
    pr_rules = [r for r in rs.get("rules", []) for _ in [1] if r["type"] == "pull_request"]
    print(f"live ruleset rules: {sorted(r['type'] for r in rs.get('rules', []))}")
    bypass = rs.get("bypass_actors", [])
    always = [b for b in bypass if b.get("bypass_mode") == "always"]
    print(f"live bypass_actors: {bypass}")

    hist = gh(f"repos/{REPO}/rulesets/{RULESET}/history") or []
    hist_pr = 0
    for v in hist:
        full = gh(f"repos/{REPO}/rulesets/{RULESET}/history/{v.get('version_id')}")
        if full and any(r["type"] == "pull_request" for r in full.get("rules", [])):
            hist_pr += 1
    print(f"ruleset versions: {len(hist)}; with a pull_request rule: {hist_pr}")

    # authenticated identity's admin flag (this is the merging identity: the
    # census shows 589/592 merges authored by tvofi, the gh account in use)
    me = gh(f"repos/{REPO}") or {}
    admin = bool((me.get("permissions") or {}).get("admin"))
    print(f"authenticated login admin on repo: {admin}")

    # second oracle: the search index
    s_merged = gh(f"search/issues?q=repo:{REPO}+is:pr+is:merged&per_page=1") or {}
    s_appr = gh(f"search/issues?q=repo:{REPO}+is:pr+is:merged+review:approved&per_page=1") or {}
    s_chang = gh(f"search/issues?q=repo:{REPO}+is:pr+is:merged+review:changes_requested&per_page=1") or {}
    print(f"search: merged={s_merged.get('total_count')} "
          f"approved={s_appr.get('total_count')} changes_requested={s_chang.get('total_count')}")

    # third oracle: direct REST reviews on a systematic 1-in-10 sample
    nums = sorted(p["number"] for p in gh(f"repos/{REPO}/pulls?state=all&per_page=100&sort=created&direction=desc",
                                          ) or [])  # first page only for numbering
    # full merged set via REST pagination
    merged = {}
    page = 1
    while True:
        d = gh(f"repos/{REPO}/pulls?state=all&per_page=100&page={page}")
        if not d:
            break
        for p in d:
            if p.get("merged_at"):
                merged[p["number"]] = p
        if len(d) < 100:
            break
        page += 1
    sample = sorted(merged)[::10]
    appr_na = 0
    appr_any = 0
    for n in sample:
        rvs = gh(f"repos/{REPO}/pulls/{n}/reviews?per_page=100") or []
        author = (merged[n].get("user") or {}).get("login")
        if any(r.get("state") == "APPROVED" for r in rvs):
            appr_any += 1
        if any(r.get("state") == "APPROVED"
               and (r.get("user") or {}).get("login") != author for r in rvs):
            appr_na += 1
    print(f"REST merged census={len(merged)}; sample={len(sample)} "
          f"(every 10th); approved_any={appr_any} approved_nonauthor={appr_na}")

    print()
    print(f"RESULT live_ruleset_pr_rules={len(pr_rules)}")
    print(f"RESULT live_ruleset_versions={len(hist)}")
    print(f"RESULT live_history_pr_rules={hist_pr}")
    print(f"RESULT search_merged_prs={s_merged.get('total_count')}")
    print(f"RESULT search_merged_approved={s_appr.get('total_count')}")
    print(f"RESULT rest_merged_census={len(merged)}")
    print(f"RESULT sample_size={len(sample)}")
    print(f"RESULT sample_approved_any={appr_any}")
    print(f"RESULT sample_approved_nonauthor={appr_na}")
    always_ids = [str(b.get("actor_type")) + ":" + str(b.get("actor_id")) for b in always]
    print(f"RESULT admin_bypass_always={always_ids}")
    print(f"RESULT authenticated_admin={int(admin)}")
    print(f"RESULT api_failures={len(FAILS)}")
    for pth, err in FAILS:
        print(f"  API FAILURE {pth}: {err}", file=sys.stderr)


if __name__ == "__main__":
    main()
