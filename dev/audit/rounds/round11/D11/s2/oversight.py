#!/usr/bin/env python3
"""D11.M2 (NIST AI 100-1 GOVERN / AI 600-1 human oversight; Scorecard Code-Review):
whether the human oversight point is provable from GitHub's records.

Metric (one line): of the window's merged pull requests, how many carry an
APPROVED review at the merged head under the owner's account (login tvofi) that
the production classifier `tools/policy/budget_raise_gate.py:approval` reads as
the owner's own (no mandate reader given), versus agent-declared.

Population: round 11's window, api/window.json (fetch_window.py). The review
bodies there are the first 400 characters GitHub returned.
Key: `approval()`'s verdict and the AGENT_DECLARED regex it applies to the review
body; the GitHub identity (login, id, type) of every one of these reviews is the
owner's in both arms, so the split is made by body text alone.

Run:   PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D11/s2/oversight.py [--perturb]
       --perturb deletes every AGENT_DECLARED match from each body (an agent that
       does not declare itself): `owner_own_at_head` must go UP from 0 to the count
       of agent-declared approvals, with no change to any GitHub-recorded field.
Expected at baseline 92d38ecb640bd462f2e19c0814d0f0b7df1ee692, box B7: exact counts.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import json, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = ["tools/policy"]
import budget_raise_gate as b  # noqa: E402


def main(argv):
    w = json.load(open(os.path.join(HERE, "api", "window.json")))
    t0, c0 = time.process_time(), time.thread_time()
    owner_user = {"login": b.OWNER_LOGIN, "id": b.OWNER_ID, "type": b.OWNER_TYPE}
    own = declared = owner_account_at_head = merged_by_owner = 0
    for n, p in w["prs"].items():
        head = p["pull"]["head_sha"]
        merged_by_owner += p["pull"]["merged_by"] == b.OWNER_LOGIN
        revs = []
        for i, r in enumerate(p["reviews"]):
            if r["user"] != b.OWNER_LOGIN:
                continue
            body = r["body"] or ""
            if "--perturb" in argv:
                body = b.AGENT_DECLARED.sub("", body)
            revs.append({"id": i, "user": owner_user, "state": r["state"], "commit_id": r["commit_id"], "body": body})
        if any(r["state"] == "APPROVED" and r["commit_id"] == head for r in revs):
            owner_account_at_head += 1
            ok, why = b.approval(revs, head, mandate_fn=None)
            if ok:
                own += 1
            elif any(b.AGENT_DECLARED.search(r["body"]) for r in revs):
                declared += 1
    n = len(w["prs"])
    print(f"RESULT window_prs={n} count")
    print(f"RESULT owner_account_approval_at_head={owner_account_at_head} count")
    print(f"RESULT owner_own_at_head={own} count")
    print(f"RESULT agent_declared_under_owner_account={declared} count")
    print(f"RESULT merged_by_owner_account={merged_by_owner} count")
    pc, tc = time.process_time() - t0, time.thread_time() - c0
    print(f"RESULT thread_factor={pc / tc if tc else 1.0:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT swapins=0")


if __name__ == "__main__":
    main(sys.argv[1:])
