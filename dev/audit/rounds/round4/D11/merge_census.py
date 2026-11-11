#!/usr/bin/env python3
"""D11 / round 4 -- what GitHub's own records say happened at every merge.

METRIC, one fraction per obligation, over a stated window:
  reviewed        -- merged PRs carrying an APPROVED review by an account other
                     than the author, from `pullRequests.reviews`. This is the
                     accountability evidence NIST AI 100-1 GOVERN 2.1 asks for
                     and the only form of it that is not a seat's own word.
  first_contract  -- merged PRs whose FIRST `pr-contract` run at the merged head
                     concluded success. Read from the commit's CHECK-RUNS
                     LISTING: the checks summary keeps the newest run per name
                     and hides a context that went red and was re-run green.
  no_red_required -- merged PRs with no run of a required context concluding
                     failure at the merged head, judged against the required set
                     IN FORCE AT THAT MERGE (18 -> 17 -> 16 inside the window).
  red_answered    -- of the merges that did have such a red run, those whose
                     `## Red checks` body section names it.
  disposition     -- merged PRs with a row in docs/plan-2026-09-open-issues.md
                     or docs/HANDOVER.md (the `record` job's own predicate,
                     approximated by a literal `#<n>` mention in either file).

SAMPLE AND HOW IT WAS DRAWN. Not a sample: a census. Two populations, both
closed at the baseline commit's committer date 2026-09-12T10:44:09Z --
  ALL      every merged pull request in the repository (n=592), for `reviewed`,
           because a review obligation does not begin with the ruleset;
  RULESET  every merged pull request with merged_at >= 2026-09-09T09:37:08Z,
           the instant `main-protect` first became active, for the four
           check-keyed fractions, because before that instant no check was
           enforced at the boundary and the fraction would measure nothing.
The set is drawn from GraphQL `pullRequests(states:MERGED)` and cross-checked
against REST `pulls?state=all`; the two must agree on the SET of numbers, never
merely on the total (#677's enumerator reads a free-text subject suffix and
misses a merge whose subject carries none -- this harness never uses that path).

COMMAND (from the repository root):
  PYTHONPATH=tests/hastub python3 tools/audit/round4/D11/merge_census.py

EXPECTED at baseline 7dd68dd (tolerance: exact counts; the window is closed, so
a re-run reproduces them unless a body or a comment is edited afterwards):
  merged_all=592 reviewed=0 window_merges=164 first_contract_green=139
  merges_with_red_required=28 red_answered=10 disposition_rows=164 api_failures=0
MACHINE: any; network-bound.

PERTURBATION. Move the window start one version-tag earlier
(D11_WINDOW_START=2026-09-01T00:00:00Z) and `window_merges` must rise while
`first_contract_green/window_merges` falls -- `pr-contract` did not exist on
every earlier head. Change `## Red checks` to `## Red Checks` in the section
matcher and `red_answered` must fall to 0, which is the control that the
matcher is reading the section rather than the whole body.
"""

import collections
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import d11lib as L  # noqa: E402

WINDOW_START = os.environ.get("D11_WINDOW_START", "2026-09-09T09:37:08Z")
WINDOW_END = os.environ.get("D11_WINDOW_END", L.BASELINE_UTC)
RED_HEADING = os.environ.get("D11_RED_HEADING", "Red checks")
DISPOSITION_DOCS = ["docs/plan-2026-09-open-issues.md", "docs/HANDOVER.md"]


def section(body, head):
    m = re.search(
        r"^##\s*" + re.escape(head) + r"\s*$(.*?)(?=^##\s|\Z)", body or "", re.M | re.S
    )
    return m.group(1).strip() if m else None


def main():
    prs = L.merged_prs()
    rest = L.api(
        f"repos/{L.REPO}/pulls?state=all&per_page=100&sort=created&direction=asc",
        paginate=True,
    )
    rest_flat = {p["number"]: p for page in (rest or []) for p in page}
    rest_merged = {n for n, p in rest_flat.items() if p.get("merged_at")}

    # SET comparison, never totals. #677's trap in one line.
    only_gql = sorted(set(prs) - rest_merged)
    only_rest = sorted(rest_merged - set(prs))
    print(f"SET CHECK  graphql={len(prs)} rest={len(rest_merged)} "
          f"only_graphql={only_gql} only_rest={only_rest}")

    # ---- reviewed, over every merged pull request --------------------------
    approved_nonauthor = 0
    any_approved = 0
    authors = collections.Counter()
    review_states = collections.Counter()
    for n, p in prs.items():
        a = (p["author"] or {}).get("login")
        authors[a] += 1
        rv = p["reviews"]["nodes"]
        for r in rv:
            review_states[r["state"]] += 1
        if any(r["state"] == "APPROVED" for r in rv):
            any_approved += 1
        if any(
            r["state"] == "APPROVED" and (r["author"] or {}).get("login") != a
            for r in rv
        ):
            approved_nonauthor += 1
    print(f"AUTHORS    {dict(authors)}")
    print(f"REVIEWS    states across all merged PRs: {dict(review_states)}")

    # ---- the ruleset window ------------------------------------------------
    vers = L.ruleset_versions()

    def required_at(ts):
        cur = set()
        for t, st in vers:
            if ts >= t:
                cur = L.required_contexts(st)
        return cur

    win = sorted(n for n, p in prs.items() if WINDOW_START <= p["mergedAt"] <= WINDOW_END)
    first_green = 0
    no_contract = []
    red_merges = {}
    missing_required = {}
    for n in win:
        runs = L.check_runs(prs[n]["headRefOid"])
        if runs is None:
            continue
        R = required_at(prs[n]["mergedAt"])
        byname = collections.defaultdict(list)
        for c in runs:
            byname[c["name"]].append(c)
        miss = sorted(c for c in R if c not in byname)
        if miss:
            missing_required[n] = miss
        red = sorted(
            {
                c["name"]
                for c in runs
                if c["name"] in R
                and c["conclusion"]
                in ("failure", "timed_out", "cancelled", "action_required")
            }
        )
        if red:
            red_merges[n] = red
        if "pr-contract" in byname:
            f = sorted(byname["pr-contract"], key=lambda x: x["started_at"] or "")[0]
            if f["conclusion"] == "success":
                first_green += 1
        else:
            no_contract.append(n)

    # ---- `## Red checks` answered ------------------------------------------
    answered = []
    unanswered = []
    for n, red in sorted(red_merges.items()):
        body = (rest_flat.get(n) or {}).get("body") or ""
        s = section(body, RED_HEADING) or ""
        if all(re.search(re.escape(c.split(" ")[0]), s) for c in red):
            answered.append(n)
        else:
            unanswered.append((n, red, s[:80].replace("\n", " / ")))

    # ---- disposition rows ---------------------------------------------------
    root = L.git("rev-parse", "--show-toplevel").strip()
    text = ""
    for rel in DISPOSITION_DOCS:
        p = os.path.join(root, rel)
        if os.path.exists(p):
            text += open(p, encoding="utf-8", errors="replace").read()
    disp = sum(1 for n in win if re.search(r"#%d\b" % n, text))

    print()
    print(f"WINDOW     {WINDOW_START} .. {WINDOW_END}  merges={len(win)}")
    print(f"RED AT HEAD ({len(red_merges)} merges), required-context names:")
    for n, red in sorted(red_merges.items()):
        print(f"  #{n} {red}")
    print(f"RED NOT NAMED IN `## {RED_HEADING}` ({len(unanswered)}):")
    for n, red, s in unanswered:
        print(f"  #{n} red={red} section={s!r}")
    if missing_required:
        print(f"REQUIRED CONTEXT ABSENT AT MERGED HEAD: {missing_required}")

    print()
    L.result("merged_all", len(prs))
    L.result("reviewed_by_non_author", approved_nonauthor)
    L.result("approved_any", any_approved)
    L.result("distinct_pr_authors", len(authors))
    L.result("window_merges", len(win))
    L.result("first_contract_green", first_green)
    L.result("window_merges_without_pr_contract", len(no_contract))
    L.result("merges_with_red_required", len(red_merges))
    L.result("red_answered", len(answered))
    L.result("merges_missing_a_required_context", len(missing_required))
    L.result("disposition_rows", disp)
    L.footer()


if __name__ == "__main__":
    main()
