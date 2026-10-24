#!/usr/bin/env python3
"""D11 / round 4 -- the review verdict, sampled, and who wrote it.

METRIC. Over a SYSTEMATIC SAMPLE of the merge window -- every 4th merged pull
request, ordered by pull-request number ascending, over
2026-09-09T09:37:08Z..2026-09-12T10:44:09Z (n=41 of 164) -- four counts:
  any_verdict      merges carrying an issue comment whose first line starts
                   `Fix review:` (the verdict grammar `web-fix-wave.js` defines
                   and `policy_lint --stats` parses).
  merge_verdict    merges carrying `Fix review: merge` specifically.
  head_named       of those, verdicts quoting the merged head's 7-char prefix,
                   which `fix-review.md` requires so a verdict cannot be read
                   against a head that moved under it.
  distinct_authors GitHub accounts that wrote any verdict comment in the sample.
                   This is the accountability number: a verdict written by the
                   pull request's own author is a self-review whatever its text
                   says, and GitHub's records are the only place that can be
                   checked.

WHY A SAMPLE AND WHY THIS ONE. One API call per pull request, and the point is a
proportion rather than a set, so a systematic 1-in-4 is enough and states its own
draw. The `Fix review:` protocol binds fix-wave pull requests, not every merge,
so `any_verdict` is the protocol's COVERAGE of the window and not a failure rate;
`distinct_authors` is the one that is a conformance claim.

COMMAND (from the repository root):
  PYTHONPATH=tests/hastub python3 tools/audit/round4/D11/verdict_sample.py

EXPECTED at baseline 7dd68dd (tolerance: exact unless a comment is edited after
the fact -- comment bodies stay editable and a deletion leaves no trace, so this
figure is weaker than the check-run ones):
  sample=41 any_verdict=16 merge_verdict=16 head_named=15
  distinct_verdict_authors=1 self_reviewed=16 api_failures=0
MACHINE: any; network-bound.

PERTURBATION. Set D11_STRIDE=1 (the whole window rather than every 4th) and
`sample` must rise to 164 while `merge_verdict/sample` stays inside a few points
-- a proportion that moves with the stride is a sampling artefact rather than a
measurement.
"""

import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import d11lib as L  # noqa: E402

W0 = os.environ.get("D11_WINDOW_START", "2026-09-09T09:37:08Z")
W1 = os.environ.get("D11_WINDOW_END", L.BASELINE_UTC)
STRIDE = int(os.environ.get("D11_STRIDE", "4"))


def main():
    prs = L.merged_prs()
    win = sorted(n for n, p in prs.items() if W0 <= p["mergedAt"] <= W1)
    sample = win[::STRIDE]
    any_v = merge_v = head_named = self_rev = 0
    authors = set()
    for n in sample:
        pages = L.api(f"repos/{L.REPO}/issues/{n}/comments?per_page=100", paginate=True)
        if pages is None:
            continue
        cs = [c for page in pages for c in page]
        fr = [c for c in cs if (c.get("body") or "").lstrip().startswith("Fix review:")]
        if fr:
            any_v += 1
        for c in fr:
            authors.add((c.get("user") or {}).get("login"))
        mv = [c for c in fr if re.match(r"Fix review:\s*merge", (c["body"] or "").lstrip())]
        if mv:
            merge_v += 1
            head = prs[n]["headRefOid"]
            if any(head[:7] in (c["body"] or "") for c in mv):
                head_named += 1
            pr_author = (prs[n]["author"] or {}).get("login")
            if all((c.get("user") or {}).get("login") == pr_author for c in mv):
                self_rev += 1
    print(f"window {W0} .. {W1}; population {len(win)}; stride {STRIDE}")
    print(f"sample (pull-request numbers): {sample}")
    print(f"verdict comment authors: {sorted(a for a in authors if a)}")
    L.result("population", len(win))
    L.result("sample", len(sample))
    L.result("any_verdict", any_v)
    L.result("merge_verdict", merge_v)
    L.result("head_named", head_named)
    L.result("distinct_verdict_authors", len([a for a in authors if a]))
    L.result("self_reviewed", self_rev)
    L.footer()


if __name__ == "__main__":
    main()
