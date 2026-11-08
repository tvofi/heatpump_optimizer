"""List every `Fix review: blocked <sha> <KEY>: ...` entry of one verdict key.

    node tools/policy/policy_lint.mjs --stats --since v7.1.2 --window-cache W.json
    python3 -I dev/audit/rca/ci-red/entries.py W.json ci-red

`--stats` prints only the histogram, so this reads the window cache's raw
per-PR comments with the histogram's own rule: the first line of a comment
matching the wave script's VERDICT_RE, key = the class word after the head sha.
Prints `#PR<TAB>created_at<TAB>head<TAB>minutes to the PR's next verdict<TAB>why`
and a final `ENTRIES n PRS m` line. Review-endpoint verdicts are not read; the
window this was run on carried none (`STATS ENDPOINTS` prints 0).
"""
import datetime as D
import json
import re
import sys

VERDICT = re.compile(r"^Fix review:\s+(merge|blocked)\s+([0-9a-f]{40})(?:\s+([a-z][a-z0-9-]*)\s*:\s*(.+))?$")


def ts(s):
    return D.datetime.fromisoformat(s.replace("Z", "+00:00"))


def main(path, key):
    cache = json.load(open(path))
    n, prs = 0, set()
    for pr, v in sorted(cache["prReads"].items(), key=lambda x: int(x[0])):
        rows = sorted((c.get("created_at", ""), (c["body"] or "").strip().split("\n")[0]) for c in v["comments"])
        found = [(t, VERDICT.match(line)) for t, line in rows if VERDICT.match(line)]
        for i, (t, m) in enumerate(found):
            if m.group(1) == "blocked" and m.group(3) == key:
                gap = round((ts(found[i + 1][0]) - ts(t)).total_seconds() / 60) if i + 1 < len(found) else ""
                print(f"#{pr}\t{t}\t{m.group(2)[:9]}\t{gap}\t{m.group(4)}")
                n += 1
                prs.add(pr)
    print(f"ENTRIES {n} PRS {len(prs)}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
