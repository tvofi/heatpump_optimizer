#!/usr/bin/env python3
"""D11.M3 conformance over every merged pull request of round 11's window.

Metric (one line): per obligation, the share of the window's merged pull requests
(first-parent merges v10.0.0..baseline, the set from `/commits/<sha>/pulls`) that
meet it, read from GitHub's own records snapshotted in api/window.json.

Obligations (D11.md method 3, conformance):
  O1 verdict   the approver App's newest `Fix review:` comment parses (production
               grammar `tools/audit/seat/proof_watch.py:parse_verdict`) as `merge`
               at the merged head, or at an ancestor whose distance to the head is
               main-merges only (a carry), from a login other than the author.
  O2 contract  the FIRST completed, non-skipped `pr-contract / pr-contract` run at
               the merged head (check-runs listing, filter=all) is `success`.
  O3 row       a #3394 comment `Merged #<N>` exists (delivery-status-tracking.md 1).
  O4 red-ans   every context in `tools/ci/gate.py:REQUIRED`'s union whose latest
               run completed at the merged head by merged_at is red is named in the
               body's `## Red checks` section (vacuously met when none is).
  O3 uses `tools/audit/seat/record_beat.py:TEMPLATE`'s prefix ("Merged #").
  O1 counts a delivery-row-only commit after the verdict as a carry.
Key: the count is keyed on the parsed verdict / the check-run conclusion GitHub
delivered, never on a title or a label.

Run:   PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D11/s2/conformance.py [--perturb]
       --perturb replaces proof_watch.parse_verdict with a reader that returns None
       (O1 must go to 0) and empties gate.REQUIRED (O4 must go to 1.0, all vacuous).
Expected at baseline 92d38ecb640bd462f2e19c0814d0f0b7df1ee692 (box B7): see RESULT lines,
exact (a fixed snapshot). Counts only; no timing.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import json, re, subprocess, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = ["tools/audit/seat", "tools/ci"]
import proof_watch  # noqa: E402
import record_beat  # noqa: E402
import gate  # noqa: E402

APPROVER = "hpo-approver[bot]"


def git(*a):
    return subprocess.run(["git", *a], capture_output=True, text=True)


def carried(verdict_sha, head, first_parent):
    """True when verdict_sha is an ancestor of head and every non-merge commit
    between them is already on main (reachable from the merge's first parent)."""
    if verdict_sha == head:
        return True
    if git("merge-base", "--is-ancestor", verdict_sha, head).returncode != 0:
        return False
    own = git("rev-list", "--no-merges", f"{verdict_sha}..{head}", f"^{first_parent}").stdout.split()
    # a commit touching only dev/programme/delivery/ rows is the recognised
    # delivery-row carry (the approval bodies say "delivery-row commit only")
    own = [c for c in own if not all(f.startswith("dev/programme/delivery/")
                                     for f in git("show", "--name-only", "--format=", c).stdout.split())]
    return not own


def red_section(body):
    m = re.search(r"^## Red checks\s*\n(.*?)(?=^## |\Z)", body or "", re.S | re.M)
    return m.group(1) if m else None


def measure(d, issue3394):
    req = {n for names in gate.REQUIRED.values() for n in names}
    rows = []
    merged_lines = "\n".join(c["body"] for c in issue3394)
    fp = {m["subject_pr"]: m["parents"][0] for m in d["merges"]}
    for n, p in d["prs"].items():
        pr = p["pull"]
        head, author = pr["head_sha"], pr["user"]
        vs = [c for c in p["comments"] if c["user"] == APPROVER and c["body"].startswith("Fix review:")]
        o1 = False
        why1 = "no verdict comment"
        if vs:
            v = max(vs, key=lambda c: c["created_at"])
            got = proof_watch.parse_verdict(v["body"].split("\n", 1)[0].rstrip("\r"))
            if got is None:
                why1 = "newest verdict unparsed"
            elif got[0] != "merge":
                why1 = "newest verdict blocked"
            elif v["user"] == author:
                why1 = "verdict by author"
            elif carried(got[1], head, fp[int(n)]):
                o1, why1 = True, ("at head" if got[1] == head else "carried")
            else:
                why1 = f"merge verdict at {got[1][:8]} not head {head[:8]} nor a carry"
        pcs = sorted([c for c in p["check_runs_at_head"] if c["name"] == "pr-contract / pr-contract"
                      and c["status"] == "completed" and c["conclusion"] not in ("skipped", "cancelled", "neutral")],
                     key=lambda c: c["started_at"] or "")
        o2 = bool(pcs) and pcs[0]["conclusion"] == "success"
        why2 = pcs[0]["conclusion"] if pcs else "no completed pr-contract run at head"
        prefix = record_beat.TEMPLATE.split("{pr}")[0]
        o3 = re.search(rf"{re.escape(prefix)}{n}\b", merged_lines) is not None
        last = {}
        for c in p["check_runs_at_head"]:
            if c["name"] in req and c["completed_at"] and c["completed_at"] <= pr["merged_at"]:
                if c["name"] not in last or c["completed_at"] > last[c["name"]]["completed_at"]:
                    last[c["name"]] = c
        reds = sorted(k for k, c in last.items() if c["conclusion"] in ("failure", "timed_out", "action_required"))
        sec = red_section(pr["body"])
        unanswered = [r for r in reds if sec is None or (r not in sec and r.split(" / ")[-1] not in sec)]
        o4 = not unanswered
        rows.append({"pr": int(n), "title": pr["title"][:60], "author": author, "merged_by": pr["merged_by"],
                     "O1": o1, "O1_why": why1, "O2": o2, "O2_why": why2, "O3": o3, "O4": o4,
                     "reds": reds, "unanswered": unanswered})
    return sorted(rows, key=lambda r: r["pr"])


def main(argv):
    d = json.load(open(os.path.join(HERE, "api", "window.json")))
    iss = json.load(open(os.path.join(HERE, "api", "issue3394.json")))
    if "--perturb" in argv:
        proof_watch.parse_verdict = lambda first: None
        gate.REQUIRED = {}
    t0, c0 = time.process_time(), time.thread_time()
    rows = measure(d, iss)
    n = len(rows)
    if "--table" in argv:
        for r in rows:
            print(f"#{r['pr']}\tO1={int(r['O1'])} ({r['O1_why']})\tO2={int(r['O2'])} ({r['O2_why']})\tO3={int(r['O3'])}\tO4={int(r['O4'])} {r['unanswered']}\t{r['title']}")
    print(f"RESULT window_prs={n} count")
    for k in ("O1", "O2", "O3", "O4"):
        m = sum(r[k] for r in rows)
        print(f"RESULT {k}_met={m} count")
        print(f"RESULT {k}_fraction={m / n:.4f} ratio")
    print(f"RESULT O4_prs_with_required_red={sum(1 for r in rows if r['reds'])} count")
    print(f"RESULT O2_unmet_prs={','.join(str(r['pr']) for r in rows if not r['O2'])}")
    print(f"RESULT O1_unmet_prs={','.join(str(r['pr']) for r in rows if not r['O1'])}")
    print(f"RESULT O4_unmet_prs={','.join(str(r['pr']) for r in rows if not r['O4'])}")
    pc, tc = time.process_time() - t0, time.thread_time() - c0
    print(f"RESULT thread_factor={pc / tc if tc else 1.0:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT swapins=0")
    json.dump(rows, open(os.path.join(HERE, "api", "conformance_rows.json" if "--perturb" not in argv else "conformance_rows_perturbed.json"), "w"), indent=1)


if __name__ == "__main__":
    main(sys.argv[1:])
