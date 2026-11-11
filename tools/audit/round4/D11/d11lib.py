"""Shared GitHub-API plumbing for the D11 harnesses (round 4).

Not a harness. Every harness in this directory imports it for one thing: a
cached, failure-counting `gh api` wrapper. Both properties matter here.

* CACHED, because a D11 number is a statement about the repository at a pinned
  baseline and the repository keeps moving. The cache directory is printed by
  every harness; delete it to re-measure against a later head.
* FAILURE-COUNTING, because GitHub's SECONDARY rate limit returns HTTP 403
  while `gh api rate_limit` still reports `remaining: 5000`. A sweep that
  swallows the 403 prints a confident, wrong, smaller number. Every harness
  here prints `RESULT api_failures=<n>` beside its figures; a figure with a
  non-zero failure count is not evidence.

Run from the repository root. Requires `gh` authenticated with read access to
tvofi/heatpump_optimizer.
"""

import datetime
import json
import os
import pathlib
import subprocess
import sys
import time

REPO = os.environ.get("D11_REPO", "tvofi/heatpump_optimizer")
CACHE = pathlib.Path(
    os.environ.get("D11_CACHE", os.path.expanduser("~/.cache/hpo-d11-round4"))
)
BASELINE_SHA = "7dd68dd327fe3dbfb09f3bd0fe38910c58877697"
# The baseline commit's committer date, in UTC. Every window closes here so a
# harness re-run next week reproduces the number rather than tracking main.
BASELINE_UTC = "2026-09-12T10:44:09Z"
RULESET_ID = 22628467

FAILURES = []


def _key(path):
    for a, b in (("/", "_"), ("?", "~"), ("&", "~"), ("=", "-")):
        path = path.replace(a, b)
    return path


def api(path, paginate=False, cache=True):
    """GET a REST path. Returns decoded JSON, or None and records a failure."""
    CACHE.mkdir(parents=True, exist_ok=True)
    f = CACHE / (_key(path) + (".page.json" if paginate else ".json"))
    if cache and f.exists() and f.stat().st_size:
        return json.loads(f.read_text())
    cmd = ["gh", "api", path]
    if paginate:
        cmd += ["--paginate", "--slurp"]
    p = None
    for attempt in range(3):
        p = subprocess.run(cmd, capture_output=True, text=True)
        if p.returncode == 0:
            f.write_text(p.stdout)
            return json.loads(p.stdout)
        if "rate limit" in (p.stderr or "").lower():
            time.sleep(20 * (attempt + 1))
            continue
        break
    FAILURES.append((path, ((p.stderr if p else "") or "").strip()[:200]))
    return None


def graphql(query, out_name, cache=True):
    CACHE.mkdir(parents=True, exist_ok=True)
    f = CACHE / (out_name + ".json")
    if cache and f.exists() and f.stat().st_size:
        return json.loads(f.read_text())
    p = subprocess.run(
        ["gh", "api", "graphql", "-f", "query=" + query],
        capture_output=True,
        text=True,
    )
    if p.returncode != 0:
        FAILURES.append((out_name, (p.stderr or "").strip()[:200]))
        return None
    f.write_text(p.stdout)
    return json.loads(p.stdout)


def git(*args, root="."):
    return subprocess.run(
        ["git", "-C", root] + list(args), capture_output=True, text=True
    ).stdout


def result(name, value, unit=""):
    print(f"RESULT {name}={value} {unit}".rstrip())


def footer():
    """Every harness ends with this. `api_failures` is the control on the counts."""
    result("api_failures", len(FAILURES))
    for path, err in FAILURES:
        print(f"  API FAILURE {path}: {err}", file=sys.stderr)
    result("cache_dir", str(CACHE))
    result("baseline_sha", BASELINE_SHA)


def utc(ts):
    """'2026-09-09T11:37:08.935+02:00' -> '2026-09-09T09:37:08Z'."""
    if not ts:
        return ""
    d = datetime.datetime.fromisoformat(ts)
    return (
        d.astimezone(datetime.timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )


def ruleset_versions():
    """[(utc_iso, ruleset_state)] oldest first, from the ruleset history endpoint.

    A merge is judged against the required set in force WHEN IT MERGED, not
    against today's: the set went 18 -> 17 -> 16 inside this audit's window.
    """
    hist = api(f"repos/{REPO}/rulesets/{RULESET_ID}/history") or []
    out = []
    for v in hist:
        vid = v.get("version_id")
        full = api(f"repos/{REPO}/rulesets/{RULESET_ID}/history/{vid}")
        if not full:
            continue
        state = full.get("state", full)
        out.append((utc(full.get("updated_at") or v.get("updated_at")), state))
    out.sort(key=lambda x: x[0])
    return out


def required_contexts(state):
    for r in state.get("rules", []):
        if r["type"] == "required_status_checks":
            return {c["context"] for c in r["parameters"]["required_status_checks"]}
    return set()


def merged_prs(cache=True):
    """Every merged pull request, with author, merge commit, head oid and reviews.

    REST `pulls?state=all` is the set oracle; GraphQL carries the reviews in one
    page each. Both are cached.
    """
    pages = []
    cur = None
    for _ in range(12):
        after = "null" if cur is None else f'"{cur}"'
        q = """
query {
  repository(owner:"%s", name:"%s") {
    pullRequests(states:MERGED, first:100, orderBy:{field:CREATED_AT, direction:DESC}, after:%s) {
      pageInfo{hasNextPage endCursor}
      nodes {
        number createdAt mergedAt headRefOid baseRefName additions deletions changedFiles
        author{login}
        mergeCommit{oid committedDate}
        reviews(first:20){totalCount nodes{state author{login} submittedAt commit{oid}}}
      }
    }
  }
}""" % (REPO.split("/")[0], REPO.split("/")[1], after)
        d = graphql(q, f"merged_prs_{len(pages)}", cache=cache)
        if not d:
            break
        blk = d["data"]["repository"]["pullRequests"]
        pages.extend(blk["nodes"])
        if not blk["pageInfo"]["hasNextPage"]:
            break
        cur = blk["pageInfo"]["endCursor"]
    return {n["number"]: n for n in pages}


def check_runs(sha):
    """The commit's CHECK-RUNS LISTING, not the checks summary.

    The summary keeps one run per context name and so hides a run that went red
    and was then re-run green. Every D11 claim about a red check reads this.
    """
    d = api(f"repos/{REPO}/commits/{sha}/check-runs?per_page=100", paginate=True)
    if d is None:
        return None
    return [c for page in d for c in page.get("check_runs", [])]
