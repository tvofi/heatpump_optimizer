#!/usr/bin/env python3
"""D11-s2: sampled per-merge conformance, one fraction per obligation.

Metric (one line): for each obligation, (#sampled merged PRs meeting it) / (#sampled
merged PRs it applies to), over the sample drawn by the rule in the snapshot.

Obligations:
  O1 approval  -- an APPROVED review whose commit_id == the merged head (the merge
                  commit's second parent, read from git here) by a login other than
                  the author identity (hpo-author[bot])
  O2 contract  -- the earliest pr-contract run listed at the head concluded success
                  (listing is filter=latest: see the snapshot's _source)
  O3 row       -- docs/delivery/<N>.md exists in the tree (the disposition row)
  O4 reds      -- every check that concluded failure at the head is named under
                  `## Red checks` (applies only to PRs with a failure listed)
Inputs: tools/audit/round8/D11/s2_conformance_snapshot.json (API reads, recorded with
their source) and the tree itself (merge parents, docs/delivery/).
Perturbation: `--head-from first-parent` keys O1 on the merge's FIRST parent (main's
side) instead of the PR head -> O1 must fall to 0 of 6, showing the fraction is keyed
on the head git delivers, not on the snapshot's own `head` field.

Run (from the tree root):
  PYTHONPATH=tests/hastub OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 \
  NUMEXPR_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 python3 tools/audit/round8/D11/s2_conformance.py
Expected at baseline cdf82da: O1 6/6, O2 6/6, O3 5/6 (1489 is the baseline merge itself;
its row is owed after it), O4 0/0.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import argparse, json, subprocess, time

SNAP = "tools/audit/round8/D11/s2_conformance_snapshot.json"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--head-from", default="second-parent", choices=["second-parent", "first-parent"])
    a = ap.parse_args()
    t0p, t0t = time.process_time(), time.thread_time()
    s = json.load(open(SNAP))
    drawn = subprocess.run(["bash", "-c", s["sample_rule"]], capture_output=True, text=True).stdout.split()
    author = s["author_identity"]
    rows, o = [], {"O1": [0, 0], "O2": [0, 0], "O3": [0, 0], "O4": [0, 0]}
    for p in s["prs"]:
        parent = "^2" if a.head_from == "second-parent" else "^1"
        head = subprocess.run(["git", "rev-parse", p["merge"] + parent], capture_output=True, text=True).stdout.strip()
        o1 = any(st == "APPROVED" and cid == head and who != author for who, st, cid in p["reviews"])
        runs = sorted(p["pr_contract"])
        o2 = bool(runs) and runs[0][1] == "success"
        o3 = os.path.exists(f"docs/delivery/{p['n']}.md")
        for k, v in (("O1", o1), ("O2", o2), ("O3", o3)):
            o[k][0] += int(v); o[k][1] += 1
        if p["failed_at_head"]:
            o["O4"][1] += 1  # body check would go here; none in this sample
        rows.append((p["n"], p["merge"], head[:8], o1, o2, o3, len(p["failed_at_head"])))
    print("sample drawn by rule:", drawn, "| snapshot merges:", [p["merge"] for p in s["prs"]])
    print("RESULT sample_matches_rule=%d" % int(drawn == [p["merge"] for p in s["prs"]]))
    print("| PR | merge | head | O1 approval@head by non-author | O2 first pr-contract green | O3 row | reds@head |")
    for r in rows:
        print("| #%d | %s | %s | %s | %s | %s | %d |" % r)
    for k, (num, den) in o.items():
        print(f"RESULT {k}={num} of {den}")
    tp, tt = time.process_time() - t0p, time.thread_time() - t0t
    print("RESULT thread_factor=%.3f" % (tp / tt if tt else 1.0))
    print("RESULT load1=%.2f" % os.getloadavg()[0])
    sw = [l for l in open("/proc/vmstat") if l.startswith("pswpin")][0].split()[1]
    print("RESULT swapins=%s" % sw)


if __name__ == "__main__":
    main()
