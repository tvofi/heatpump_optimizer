"""D11-s2 harness: the owner-approval predicate cannot tell the owner from a seat.

Metric: of the sampled merged PRs on which budget_raise_gate.approval() -- the
  in-tree predicate for CLAUDE.md's "approval is the owner's approving GitHub
  review" -- returns True at the merged head, how many had that counted review
  given by an LLM seat by the review's own body (count and fraction).
Count key: approval()'s return value on the recorded reviews; "seat-given" is the
  counted review's body declaring "the orchestrator gives it"/"given by the
  orchestrator" -- a declaration the seat wrote, so this undercounts, never over.
Sample: tools/audit/round9/D11/s2/reviews_snapshot.json (12 first-parent merges
  before the baseline; how drawn is in its _source).
Perturbation (the fix CLAUDE.md's identity section describes): a seat's approval
  posted under its own App identity (hpo-approver[bot]) instead of the owner's
  account -> owner approvals counted drop to the human ones (seat_counted -> 0).
Command: PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D11/s2/owner_review.py
Expected: RESULT owner_approved_at_head=6, seat_counted_as_owner=6, perturbed_seat_counted=0 (exact on the snapshot).
Baseline: 1936d5ca72a06556eeed4e8e5bf3dea520e517e1. Machine: B3.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _common import tail  # noqa: E402
import copy, json, re
sys.path.insert(0, ".claude/workflows")
import budget_raise_gate as brg  # noqa: E402

SEAT = re.compile(r"orchestrator gives it|given by the orchestrator", re.I)
HERE = os.path.dirname(os.path.abspath(__file__))


def counted(prs):
    ok, seat = 0, 0
    for pr in prs:
        good, _why = brg.approval(pr["reviews"], pr["head"])
        if not good:
            continue
        ok += 1
        mine = [r for r in pr["reviews"] if r["user"]["login"] == brg.OWNER_LOGIN
                and r["state"] in ("APPROVED", "CHANGES_REQUESTED", "DISMISSED")]
        seat += bool(SEAT.search(mine[-1].get("body") or ""))
        print(f"#   PR {pr['n']}: owner approval counted at head; seat-given={bool(SEAT.search(mine[-1].get('body') or ''))}")
    return ok, seat


def main():
    snap = json.load(open(os.path.join(HERE, "reviews_snapshot.json")))["prs"]
    print(f"# sample={len(snap)} merged PRs; authors={sorted({p['author'] for p in snap})}")
    ok, seat = counted(snap)
    pert = copy.deepcopy(snap)
    for pr in pert:
        for r in pr["reviews"]:
            if SEAT.search(r.get("body") or ""):
                r["user"] = {"login": "hpo-approver[bot]", "id": 330097732, "type": "Bot"}
    print("# perturbed: seat approvals under the seat's own App identity")
    pok, pseat = counted(pert)
    human_head = ok - seat
    print(f"RESULT sample={len(snap)} count")
    print(f"RESULT owner_approved_at_head={ok} count")
    print(f"RESULT seat_counted_as_owner={seat} count")
    print(f"RESULT human_owner_approvals_at_head={human_head} count")
    print(f"RESULT perturbed_owner_approved_at_head={pok} count")
    print(f"RESULT perturbed_seat_counted={pseat} count")
    tail()


if __name__ == "__main__":
    main()
