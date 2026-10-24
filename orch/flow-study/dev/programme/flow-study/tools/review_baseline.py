"""Review-strength baseline: real-catch and bookkeeping blocks per reviewed pull request.

The exact enumerator behind the 0.52 and 0.15 figures in the Lean flow study (STUDY, guardrail
baselines). Read-only; run in a clone of tvofi/heatpump_optimizer:

    git fetch origin '+refs/heads/review/*:refs/remotes/origin/review/*'
    python3 review_baseline.py 2026-10-15T12:37Z 2026-10-21T11:00Z     # 0.52 (study window)
    python3 review_baseline.py 2026-10-19T14:50Z 2026-10-21T14:50Z     # 0.15 (48 h before adoption)
    python3 review_baseline.py --hours 48                              # rolling, now

Source: every ref refs/remotes/origin/review/<N> with a numeric N (the reviewer's proposed
verdicts that bus.sh push-verdict appends, one commit per verdict; not the confirmed verdict/<N>
refs). A verdict is one commit whose subject matches VERDICT below; its time is the commit's
committer date in UTC; a window is [start, end). Numerator: blocked verdicts whose class token
(the first word after the 40-hex head, a bracket allowed) is in REAL_CATCH; every other blocked
verdict, including an absent or unparsed class, is bookkeeping. Denominator: the number of
distinct pull requests with at least one verdict in the window (reviewed pull requests, not
merged ones). Re-reviews count: a pull request blocked twice in the window adds two blocks.
"""
import datetime as dt
import re
import subprocess
import sys

VERDICT = re.compile(r"Fix review: (merge|blocked) [0-9a-f]{40}\s*\[?([a-z-]+)?")
REAL_CATCH = {
    "harness", "class-open", "test-vacuous", "vacuous-test", "vacuous-check", "mutation-vacuous",
    "mutant-survives", "mutation-survivor", "mutation-untriaged", "mutation",
    "architecture-unsound", "metric-gamed", "defect", "product-tradeoff-regression",
    "policy-regression", "figures-false",
}


def when(text):
    return dt.datetime.fromisoformat(text.replace("Z", "+00:00")).astimezone(dt.timezone.utc)


def verdicts(repo="."):
    refs = subprocess.run(["git", "-C", repo, "for-each-ref", "refs/remotes/origin/review",
                           "--format=%(refname:short)"], capture_output=True, text=True,
                          check=True).stdout.split()
    for ref in refs:
        pr = ref.rsplit("/", 1)[1]
        if not pr.isdigit():
            continue
        log = subprocess.run(["git", "-C", repo, "log", "--format=%cI|%s", ref],
                             capture_output=True, text=True, check=True).stdout
        for line in log.splitlines():
            stamp, subject = line.split("|", 1)
            m = VERDICT.search(subject)
            if m:
                yield when(stamp), int(pr), m.group(1), m.group(2) or ""


def measure(start, end, rows):
    window = [r for r in rows if start <= r[0] < end]
    prs = {r[1] for r in window}
    real = sum(1 for r in window if r[2] == "blocked" and r[3] in REAL_CATCH)
    book = sum(1 for r in window if r[2] == "blocked" and r[3] not in REAL_CATCH)
    merges = sum(1 for r in window if r[2] == "merge")
    n = len(prs)
    return {"start": start.isoformat(), "end": end.isoformat(), "verdicts": len(window),
            "reviewed_prs": n, "merge_verdicts": merges, "real_catch_blocks": real,
            "bookkeeping_blocks": book,
            "real_catch_per_pr": round(real / n, 2) if n else None,
            "bookkeeping_per_pr": round(book / n, 2) if n else None}


def main(argv):
    rows = list(verdicts())
    if argv[:1] == ["--hours"]:
        end = dt.datetime.now(dt.timezone.utc)
        start = end - dt.timedelta(hours=float(argv[1]))
    elif len(argv) == 2:
        start, end = when(argv[0]), when(argv[1])
    else:
        print(__doc__)
        return 2
    for k, v in measure(start, end, rows).items():
        print(f"{k}: {v}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
