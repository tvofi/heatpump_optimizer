#!/usr/bin/env python3
"""D11.M3's enumerator: the step's universe, one item per line.

Run from the export root:  python3 dev/audit/rounds/round11/D11/s2/m3_universe.py
Items, by sub-measure of D11.md method 3:
  size:<aggregate>           the five aggregate caps `policy_lint.mjs --budgets` prints, plus size:ratio
  recurrence:window          the `--stats --since v10.0.0` histogram (api/stats_v10.0.0.out)
  conformance:#<N>           every merged pull request of the window (api/window.json)
  staleness:<doc>            each decision record, the handover, each plan file
  duplication:<file>         each file of the policy set D11.md names for the duplication units
  rulings:<k>                each live RULINGS.md entry (before `## Superseded`), numbered
Baseline 92d38ecb640bd462f2e19c0814d0f0b7df1ee692, box B7.
"""
import glob, json, os, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from policy_health import corpus, live_rulings  # noqa: E402


def main():
    for a in ("always-loaded", "corpus", "role-fixer", "role-record", "role-policy"):
        print(f"size:{a}")
    print("size:ratio")
    print("recurrence:window")
    w = json.load(open(os.path.join(HERE, "api", "window.json")))
    for n in sorted(w["prs"], key=int):
        print(f"conformance:#{n}")
    for f in sorted(glob.glob("dev/governance/decisions/*.md")):
        print(f"staleness:{f}")
    print("staleness:dev/programme/HANDOVER.md")
    for f in sorted(glob.glob("dev/programme/plan*.md")):
        print(f"staleness:{f}")
    pol, extra = corpus()
    for f in sorted(set(pol + extra)):
        print(f"duplication:{f}")
    for i, _ in enumerate(live_rulings(open("dev/programme/RULINGS.md").read()), 1):
        print(f"rulings:{i}")


if __name__ == "__main__":
    main()
