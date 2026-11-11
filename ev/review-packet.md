# Review packet #3424
head: f9c7952b3a261ec46c0ecebdde72fa622e2c7d3e
base: d08ed31049cd3636cde4d2fdeb3bd7cd4b3c842a

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: red
CodeQL id=130302386263 success
arch-score / arch-score id=130302112997 success
arm id=130301880643 skipped
budget-raise-gate / budget-raise-gate id=130302112742 success
cancel-superseded id=130301881506 success
codeql id=130302098139 skipped
codeql / Analyze (actions) id=130302112749 success
codeql / Analyze (javascript-typescript) id=130302112761 success
codeql / Analyze (python) id=130302112770 success
gate id=130302765436 failure
governance id=130302098511 skipped
governance / delivery-status id=130302112780 success
governance / delivery-status-publish id=130302114185 skipped
governance / env-matrix id=130302112753 success
governance / instrument-self-tests id=130302112776 in_progress
governance / policy-docs id=130302112710 success
governance / record id=130302114596 skipped
governance / wave-script id=130302112733 success
hassfest id=130302098807 skipped
hassfest / hassfest id=130302112590 success
kernel-points id=130302114391 skipped
pr-contract id=130302767057 skipped
prelude id=130301881250 success
refresh id=130301881011 success
sweep-self id=130303208881 skipped
tests id=130302098923 skipped
tests / arch-instrument id=130302654929 success
tests / briefs id=130302113052 success
tests / browser id=130302654865 success
tests / closure-scope id=130302113094 success
tests / closures id=130302654898 in_progress
tests / coverage id=130302654949 in_progress
tests / fast (3.14) id=130302654866 in_progress
tests / mutation id=130302113047 success
tests / mutation-autofix id=130302784652 skipped
tests / mutation-pins id=130302783169 skipped
tests / nightly-ha id=130302657192 skipped
tests / nightly-status id=130302113120 success
tests / replay id=130302656691 skipped
tests / typing id=130302654927 success
validate id=130302098083 skipped
validate / validate-hacs id=130302112618 success

## Refusals
none

## Advisories
required-wait: required context `gate` reads concluded failure at f9c7952b3a261ec46c0ecebdde72fa622e2c7d3e in the digest, but merge_train.py classify --pr reads WAIT (pending: gate red: none): classify decides, as bus.sh's dispatch does, and a pending check never refuses

## carry_audit at the head
NOTE body item bdd0c3fc: R10-TRAIN-RESIDUE: R10-TRAIN-RESIDUE resolved on origin/handoff/audit-r10-roster
NOTE body item bdd0c3fc: R10-TRAIN-RESIDUE: R10-TRAIN-RESIDUE resolved on origin/handoff/audit-r10-roster
NOTE body item bdd0c3fc: R10-TRAIN-RESIDUE: R10-TRAIN-RESIDUE resolved on origin/handoff/audit-r10-roster
NOTE body item bdd0c3fc: dismissed:built or already on main
NOTE body item bdd0c3fc: dismissed:later part dispatched at this merge, not this repair
CARRY-AUDIT: 1 finding item(s): 1 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
ok         PYTHONPATH=tests/hastub python3 tools/audit/seat/merge_train.py --self-test
             `tools/audit/seat/merge_train.py` is in the tree at this head
  ok         python3 tests/structure.py
             `tests/structure.py` is in the tree at this head

FIGURES: 2 resolved, 0 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
none

## Three-dot diff
diff --git a/dev/programme/delivery/3424.md b/dev/programme/delivery/3424.md
new file mode 100644
index 0000000000..84c76458c6
--- /dev/null
+++ b/dev/programme/delivery/3424.md
@@ -0,0 +1 @@
+- [#3424](https://github.com/tvofi/heatpump_optimizer/pull/3424) — **open**, R10-TRAIN-RESIDUE: r10 train residue (R10-TRAIN-RESIDUE)
diff --git a/tools/audit/seat/merge_train.py b/tools/audit/seat/merge_train.py
index 986b1c7b40..57bd64199c 100644
--- a/tools/audit/seat/merge_train.py
+++ b/tools/audit/seat/merge_train.py
@@ -2399,7 +2399,9 @@ class Train:
         """Whether `policy_approve` posts step 5's approval at <h>: (mandate id,
         policy paths, why). The id is None when nothing is posted, and <why>
         then says why ('' when there is nothing to say: no policy path, no
-        --mandate, or the owner's approval already at <h>). A read only -- the
+        --mandate, or the owner's approval already at <h>; or a refusal: the
+        owner's own latest CHANGES_REQUESTED, or a `gh` account that is not
+        the owner's). A read only -- the
         one decision `policy_approve` posts on and `policy_admits` (the
         pre-flight) judges with, so the two cannot drift."""
         cid = self.mandate_id()
@@ -2414,6 +2416,19 @@ class Train:
         if any(g._is_owner(r.get("user")) and r.get("state") == "APPROVED" and r.get("commit_id") == h
                for r in self._reviews(pr, "the policy approval")):
             return None, pol, ""  # the owner's approval is at the head already: never re-posted
+        own = [r for r in self._reviews(pr, "the policy approval")
+               if g._is_owner(r.get("user")) and not g.AGENT_DECLARED.search(r.get("body") or "")
+               and r.get("state") in ("APPROVED", "CHANGES_REQUESTED", "DISMISSED")]
+        if own and own[-1].get("state") == "CHANGES_REQUESTED":
+            # `budget_raise_gate.approval`'s rule, which refuses a mandated approval over it.
+            return None, pol, (f"{g.OWNER_LOGIN}'s own latest decisive review is CHANGES_REQUESTED, "
+                               "which a mandated approval does not override")
+        code, login = self.run(["gh", "api", "user", "--jq", ".login"])
+        if code or login.strip() != g.OWNER_LOGIN:
+            # The post is the owner's review and the pre-flight judges it as the owner's: a
+            # `gh` account that is not the owner posts one `policy_gate` refuses at the merge.
+            return None, pol, (f"the gh account is {login.strip()[:40] or 'unreadable'}, not {g.OWNER_LOGIN}"
+                               if not code else "the gh account could not be read")
         now = datetime.datetime.now(datetime.timezone.utc)
         try:
             live, why = g.mandate_state(cid, *self._mandate_read(cid), now, now.strftime("%Y-%m-%dT%H:%M:%SZ"),
@@ -4382,6 +4397,8 @@ def _self_test() -> int:
                 return 0, world.get("required", "fast\n")
             if "app_approve.sh" in a:
                 return world.get("approve", (0, "APPROVED"))
+            if argv[:3] == ["gh", "api", "user"]:  # the acting account
+                return 0, world.get("post_user", {"login": "orchestrator"})["login"]
             if argv[:3] == ["gh", "pr", "review"]:
                 # What GitHub would hold after the post: the next reviews read
                 # returns it -- unless the read-back is meant to fail.
@@ -4922,6 +4939,16 @@ def _self_test() -> int:
         check(f"policy post null: {name} posts nothing, and the policy stop is today's",
               rc == 1 and posts(calls) == 0 and "policy:" in lines[-1] and "no decisive review" in lines[-1]
               and not merged(calls))
+    # Carries 7/11 and 8/12 (R10-TRAIN-RESIDUE): the post and the pre-flight's simulation share
+    # `policy_approval_due`, so one refusal each covers both.
+    rc, lines, calls = go({**POL, "reviews": [], "mandate": mandate(NOW),
+                           "post_user": {"login": "someone-else", "id": 9, "type": "User"}}, mandate=str(MID))
+    check("policy post: a gh account that is not the owner posts nothing, and the stop names the account",
+          rc == 1 and posts(calls) == 0 and not merged(calls) and any("gh account is someone-else" in ln for ln in lines))
+    rc, lines, calls = go({**POL, "reviews": [{**owner_review(H0, NOW), "state": "CHANGES_REQUESTED", "body": ""}],
+                           "mandate": mandate(NOW), "post_user": OWNER}, mandate=str(MID))
+    check("policy post: the owner's own latest CHANGES_REQUESTED posts no mandated approval",
+          rc == 1 and posts(calls) == 0 and not merged(calls) and "CHANGES_REQUESTED" in lines[-1])
     rc, lines, calls = go({**POL, "reviews": [owner_review(H0, NOW)], "mandate": mandate(NOW), "post_user": OWNER},
                           mandate=str(MID))
     check("policy post: an owner approval already at the head is not re-posted, and it lands",
@@ -7633,6 +7660,8 @@ def _batch_self_test(check) -> None:
                 rf = w.get("reviews_for")
                 return 0, json.dumps([(rf(w["heads"][int(n)]) if rf else [])
                                       + [r for r in w.get("posted", []) if r["pr"] == int(n)]])
+            if argv[:3] == ["gh", "api", "user"]:  # the acting account: the owner's
+                return 0, _mandate_gate().OWNER_LOGIN
             if argv[:3] == ["gh", "pr", "review"]:  # posted as the owner's account, as `gh` is
                 gm = _mandate_gate()
                 w.setdefault("posted", []).append(
diff --git a/tools/audit/seat/queue_pre_flight.py b/tools/audit/seat/queue_pre_flight.py
index f7f02fa4ed..20a8afbc17 100644
--- a/tools/audit/seat/queue_pre_flight.py
+++ b/tools/audit/seat/queue_pre_flight.py
@@ -371,6 +371,8 @@ def _self_test() -> int:
                 return 0, json.dumps([world.get("comments", [])])
             if argv[:2] == ["gh", "api"] and a.endswith("/pulls/7 --jq .body // \"\""):
                 return 0, world.get("body", "")
+            if argv[:3] == ["gh", "api", "user"]:  # the acting account `policy_approval_due` reads: the owner's
+                return 0, mt._mandate_gate().OWNER_LOGIN
             return 0, ""
         return run
 

## Before you return the verdict (P275)
Run `python3 -I tools/audit/carry_audit.py check --body <PR body file> --comments <file holding [{"id": 0, "body": <verdict.md text>}]>`. Give every reported item its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>`;
an evidence line flagged by its wording takes `Carry: dismissed: evidence, not a finding`. Return the verdict only at rc 0.
