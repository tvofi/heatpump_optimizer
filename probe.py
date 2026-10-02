"""Reviewer's own probe for PR #1843 (not the fixer's harness).
Imports budget_raise_gate from the worktree given as argv[1] and drives
approval()/mandate_check() directly. Prints RESULT lines."""
import importlib.util, sys
spec = importlib.util.spec_from_file_location("brg", sys.argv[1] + "/.claude/workflows/budget_raise_gate.py")
g = importlib.util.module_from_spec(spec); spec.loader.exec_module(g)
H = "a" * 40
OWN = {"login": g.OWNER_LOGIN, "id": g.OWNER_ID, "type": g.OWNER_TYPE}
CID = 5000000001
G = f"MANDATE: agents may approve as {g.OWNER_LOGIN}, scope budget-raise, from 2026-10-02T06:00Z until 2026-10-03T06:00Z"
def cm(body=G, user=OWN, created="2026-10-02T05:00:00Z", updated=None, url="https://api.github.com/repos/tvofi/heatpump_optimizer/issues/201"):
    return {"id": CID, "user": user, "body": body, "created_at": created, "updated_at": updated or created, "issue_url": url}
def rv(body=f"Agent approval, mandate {CID}", state="APPROVED", sha=H, at="2026-10-02T07:00:00Z", user=OWN):
    return {"id": 1, "user": user, "state": state, "commit_id": sha, "submitted_at": at, "body": body}
def run(name, reviews, comment=None, thread=(), expect=None):
    comment = cm() if comment is None else comment
    ok, why = g.approval(reviews, H, lambda c: ((None if comment == "missing" else comment), list(thread)))
    flag = "" if expect is None or ok == expect else "  <-- UNEXPECTED"
    print(f"RESULT {name}: approved={ok} expect={expect}{flag}  | {why[:150]}")
run("baseline mandated approval", [rv()], expect=True)
run("null: no mandate cited", [rv(body="Agent approval, orchestrator seat")], expect=False)
run("null: undeclared owner approval still counts (pre-existing path)", [rv(body="LGTM")], expect=True)
run("expired", [rv(at="2026-10-03T06:00:00Z")], expect=False)
run("before from", [rv(at="2026-10-02T05:59:00Z")], expect=False)
run("revoked by tvofi", [rv()], thread=[{"id": 9, "user": OWN, "body": f"MANDATE REVOKED {CID}"}], expect=False)
run("revocation trailing period", [rv()], thread=[{"id": 9, "user": OWN, "body": f"MANDATE REVOKED {CID}."}], expect=False)
run("revocation with #", [rv()], thread=[{"id": 9, "user": OWN, "body": f"MANDATE REVOKED #{CID}"}], expect=False)
run("revocation lower case", [rv()], thread=[{"id": 9, "user": OWN, "body": f"Mandate revoked {CID}"}], expect=False)
run("revocation with colon", [rv()], thread=[{"id": 9, "user": OWN, "body": f"MANDATE REVOKED: {CID}"}], expect=False)
run("revocation not first line", [rv()], thread=[{"id": 9, "user": OWN, "body": f"Ending it now.\nMANDATE REVOKED {CID}"}], expect=False)
run("revocation by other account (null)", [rv()], thread=[{"id": 9, "user": {"login": "x", "id": 2, "type": "User"}, "body": f"MANDATE REVOKED {CID}"}], expect=True)
run("wrong author login", [rv()], cm(user={"login": "x", "id": g.OWNER_ID, "type": "User"}), expect=False)
run("wrong author id", [rv()], cm(user={**OWN, "id": 1}), expect=False)
run("wrong author type Bot", [rv()], cm(user={**OWN, "type": "Bot"}), expect=False)
run("wrong issue", [rv()], cm(url="https://api.github.com/repos/tvofi/heatpump_optimizer/issues/1838"), expect=False)
run("issue 201 of ANOTHER repo", [rv()], cm(url="https://api.github.com/repos/evil/other/issues/201"), expect=False)
run("scope code-owned", [rv()], cm(body=G.replace("budget-raise", "code-owned")), expect=False)
run("non-head approval", [rv(sha="b" * 40)], expect=False)
run("grammar: quoted mandate first line", [rv()], cm(body="> " + G), expect=False)
run("grammar: mandate on second line", [rv()], cm(body="Note\n" + G), expect=False)
run("grammar: trailing text", [rv()], cm(body=G + " (or longer)"), expect=False)
run("edited after review", [rv()], cm(updated="2026-10-02T07:30:00Z"), expect=False)
run("EDITED BEFORE review: an old tvofi comment rewritten into the grammar", [rv()],
    cm(created="2026-09-01T00:00:00Z", updated="2026-10-02T06:30:00Z"), expect=None)
run("agent approval after owner's own CHANGES_REQUESTED", [rv(body="no", state="CHANGES_REQUESTED", at="2026-10-02T06:30:00Z"), rv()], expect=None)
run("agent mandated approval by App account", [rv(user={"login": "hpo-approver[bot]", "id": 3, "type": "Bot"})], expect=False)
