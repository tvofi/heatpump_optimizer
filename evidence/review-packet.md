# Review packet #3400
head: 7326025c8472fbe155a46f9edd57530fd9b4be7d
base: 3aac11dfba2a252f329159af0f1c15b48d79818b

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: pending
arm id=129560710147 skipped
cancel-superseded id=129560720801 queued
prelude id=129560721108 queued
refresh id=129560721100 queued

## Refusals
none

## Advisories
none

## carry_audit at the head
CARRY-AUDIT: 0 finding item(s): 0 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
ok         python3 -I tools/audit/seat/review_packet.py --self-test
             `tools/audit/seat/review_packet.py` is in the tree at this head
  ok         python3 tools/audit/seat/merge_train.py classify 71b95e42daf4d32031ce116b01c469b81f2a23a0 --repo tvofi/heatpump_optimizer --pr 3379
             `tools/audit/seat/merge_train.py` is in the tree at this head
  ok         python3 tests/closure.py select --diff b8f67a775137a8032d5c71b34ea64165c1d4613a
             `tests/closure.py` is in the tree at this head
  ok         python3 tests/structure.py
             `tests/structure.py` is in the tree at this head

FIGURES: 4 resolved, 0 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
none

## Three-dot diff
diff --git a/dev/programme/delivery/3400.md b/dev/programme/delivery/3400.md
new file mode 100644
index 000000000..94ca9758a
--- /dev/null
+++ b/dev/programme/delivery/3400.md
@@ -0,0 +1 @@
+- [#3400](https://github.com/tvofi/heatpump_optimizer/pull/3400) — **open**, review_packet: required-red asks classify's whole verdict (r10-hotfix-packet-approval-owed)
diff --git a/tools/audit/seat/instruments/review_packet.py.md b/tools/audit/seat/instruments/review_packet.py.md
index f49cdd216..35379117f 100644
--- a/tools/audit/seat/instruments/review_packet.py.md
+++ b/tools/audit/seat/instruments/review_packet.py.md
@@ -11,8 +11,9 @@
   renders its own from its dispatch prompt. Refusal: carry-audit, a `## Head`
   not naming the head, a `tests/structure.py` refusal at the head merged with
   main, an unanswered concluded red, a required context concluded failure
-  (unless `merge_train.py classify --pr` answers APPROVAL-OWED, printed as the
-  `approval-owed` advisory instead; P345), a host path, a hot file shared with an open pull request holding an
+  that `merge_train.py classify --pr` reads RED or cannot read (APPROVAL-OWED
+  prints the `approval-owed` advisory instead, P345; WAIT or GREEN prints
+  `required-wait`/`required-green`, #3379: classify decides, as in `bus.sh`), a host path, a hot file shared with an open pull request holding an
   unboarded merge verdict, or a `fix/<t>` head lacking its `handoff/<t>` tip
   (`handoff-not-applied`), or a body line citing a carry as landed that the roster ref lacks at the cited sha (`carry-landed`); a pending check never refuses. A `head-note` refusal names the repair (`update_pr.sh`). The packet closes on the `carry_audit.py check` self-audit a reviewer runs before its verdict. `handoff`, run by
   `body_push.sh` before a PR body is pushed, refuses the structure and
diff --git a/tools/audit/seat/review_packet.py b/tools/audit/seat/review_packet.py
index 51b7504fd..f7b8fbe1b 100644
--- a/tools/audit/seat/review_packet.py
+++ b/tools/audit/seat/review_packet.py
@@ -34,10 +34,12 @@ REFUSALS (rc 1, each named by its signal), all mechanical:
   structure        `tests/structure.py` refuses the head merged with main;
   red-unanswered   a CONCLUDED red check the body's `## Red checks` does not name
                    (`policy_lint.mjs --pr-body --red`);
-  required-red     a required context's latest run concluded failure -- unless
-                   `merge_train.py classify --pr` answers APPROVAL-OWED (P345: the
-                   red is only a budget raise's approval, which follows the
-                   review), printed as the `approval-owed` advisory instead;
+  required-red     a required context's latest run concluded failure and
+                   `merge_train.py classify --pr`, which decides, reads it RED or
+                   cannot be read; APPROVAL-OWED (P345: only a budget raise's
+                   approval, which follows the review) prints `approval-owed`,
+                   WAIT or GREEN (a provisional red, P436; #3379) prints
+                   `required-wait`/`required-green`, each an advisory instead;
   host-path        the body or an added line names this host (`ref_privacy.py`);
   hot-file         the diff shares a HOT_FILES path with an open pull request
                    whose merge verdict is at its head and not on the train;
@@ -184,21 +186,32 @@ def gate_digest(runs: list[dict]) -> tuple[str, list[str], list[str]]:
     return state, lines, reds
 
 
-def approval_owed_line(pr: int, head: str) -> str | None:
-    """The reason `merge_train.py classify --pr` prints after `APPROVAL-OWED <head>`
-    (rc 4), else None: the one owner of K15 (d)'s raise exception asked, never
-    restated (P345). Any other answer, or a classifier that cannot run, is None,
-    and the required red refuses as before. HPO_PACKET_CLASSIFY replaces the
-    command (the self-test's stub)."""
+#: `merge_train.py classify`'s exit code -> the verdict word its one line starts with.
+CLASSIFY_WORD = {0: "GREEN", 1: "RED", 3: "WAIT", 4: "APPROVAL-OWED"}
+
+
+def required_reading(pr: int, head: str) -> tuple[str, str]:
+    """(verdict, rest of the line) of `merge_train.py classify <head> --pr <pr>`,
+    the one owner of whether a required red is red (P436: a provisional gate
+    red, or one beside a re-running unit, it reads WAIT) and of K15 (d)'s raise
+    exception (P345). The packet's own latest-run-per-name digest never decides
+    alone: bus.sh dispatches on this same answer, and the two disagreeing is
+    #3379's deadlock. A verdict whose word does not match its rc, a line naming
+    another head, or a classifier that cannot run is ("RED", why): fail closed.
+    HPO_PACKET_CLASSIFY replaces the command (the self-test's stub)."""
     cmd = shlex.split(os.environ.get("HPO_PACKET_CLASSIFY", "")) or [
         sys.executable, str(ROOT / "tools/audit/seat/merge_train.py")]
     try:
         r = subprocess.run([*cmd, "classify", head, "--repo", REPO, "--pr", str(pr)],
                            capture_output=True, text=True)
-    except OSError:
-        return None
-    m = re.search(rf"^APPROVAL-OWED {re.escape(head)} (.+)$", r.stdout, re.M)
-    return m.group(1) if r.returncode == 4 and m else None
+    except OSError as e:
+        return "RED", f"classify could not run: {e}"
+    word = CLASSIFY_WORD.get(r.returncode)
+    m = word and re.search(rf"^{re.escape(word)} {re.escape(head)}(?: (.*))?$", r.stdout, re.M)
+    if m:
+        return word, m.group(1) or ""
+    last = ([ln for ln in (r.stdout + r.stderr).splitlines() if ln.strip()] or [""])[-1]
+    return "RED", f"classify unreadable (rc {r.returncode}): {last[:200]}"
 
 
 def head_note_ok(body: str, head: str) -> bool:
@@ -504,14 +517,20 @@ def build(facts: dict) -> tuple[list[str], list[str], str]:
     refusals += handoff_refusals(facts["structure"], facts["hot"], [])
     for n in facts["red_unanswered"]:
         refusals.append(f"red-unanswered: concluded red check `{n}` is not named in ## Red checks")
-    owed, owed_adv = facts.get("approval_owed"), []
+    (word, why), owed_adv = facts.get("required_read") or ("RED", ""), []
     for n in sorted(set(reds) & set(REQUIRED)):
-        if owed:
+        if word == "APPROVAL-OWED":
             owed_adv.append(
                 f"approval-owed: required context `{n}` concluded failure at {head} only on a budget "
-                f"raise's owed approval (merge_train.approval_owed): {owed}")
+                f"raise's owed approval (merge_train.approval_owed): {why}")
+        elif word in ("WAIT", "GREEN"):
+            owed_adv.append(
+                f"required-{word.lower()}: required context `{n}` reads concluded failure at {head} in the "
+                f"digest, but merge_train.py classify --pr reads {word} ({why}): classify decides, as "
+                "bus.sh's dispatch does, and a pending check never refuses")
         else:
-            refusals.append(f"required-red: required context `{n}` concluded failure at {head}")
+            refusals.append(f"required-red: required context `{n}` concluded failure at {head}"
+                            + (f" (merge_train.py classify --pr reads {word} {why})" if why else ""))
     for w in facts["host"]:
         refusals.append(f"host-path: {w}")
     refusals += facts.get("unlanded", [])
@@ -556,7 +575,7 @@ def gather(a) -> dict:
         unlanded = unlanded_carries(cites, carries_at, on_roster)
     runs = gh(f"repos/{REPO}/commits/{head}/check-runs?per_page=100").get("check_runs", [])
     gate = gate_digest(runs)
-    owed = approval_owed_line(a.pr, head) if set(gate[2]) & set(REQUIRED) else None
+    read = required_reading(a.pr, head) if set(gate[2]) & set(REQUIRED) else None
     crc, cout = tool([sys.executable, "-I", "tools/audit/carry_audit.py", "check", "--body", "{BODY}"], body)
     _, fout = tool(["node", "tools/policy/figure_lint.mjs", "--pr-body", "{BODY}", "--at", head], body)
     red_unanswered = unanswered_reds(body, head, base, gate[2], touched, existing)
@@ -565,7 +584,7 @@ def gather(a) -> dict:
     host += ref_privacy.content_refusals(ref_privacy.added_lines(base, head, repo()), ident)
     open_prs, boarded = hot_prs(touched)
     return {
-        "pr": a.pr, "head": head, "base": base, "body": body, "gate": gate, "approval_owed": owed,
+        "pr": a.pr, "head": head, "base": base, "body": body, "gate": gate, "required_read": read,
         "branch": branch, "unlanded": unlanded,
         "carry_rc": crc, "carry_out": cout, "figure_out": fout,
         "structure": None if a.no_structure else structure_at_merge(main, head),
@@ -690,11 +709,30 @@ def _self_test() -> int:
                {"id": 2, "name": "gate", "status": "completed", "conclusion": "failure"}]
     check("required-red: the required context's latest run concluded failure refuses",
           refused("required-red", gate=gate_digest(redgate)))
-    r_o, adv_o, t_o = build({**clean, "gate": gate_digest(redgate), "approval_owed": "1 budget raise(s), planted"})
+    r_o, adv_o, t_o = build({**clean, "gate": gate_digest(redgate),
+                         "required_read": ("APPROVAL-OWED", "1 budget raise(s), planted")})
     check("P345: a required red that is only a raise's owed approval renders: no refusal, an "
           "`approval-owed` advisory naming the reason, in the packet",
           r_o == [] and len(adv_o) == 1 and adv_o[0].startswith("approval-owed: required context `gate`")
           and "1 budget raise(s), planted" in t_o)
+    # #3379 at 71b95e42, 00:03Z on 11-10: the gate's latest run concluded failure while the
+    # budget-raise-gate re-run was in progress, so classify --pr read WAIT (rc 3) and bus.sh
+    # dispatched it, but the packet asked only "is it APPROVAL-OWED?" and refused required-red.
+    raise_rerun = [*redgate, {"id": 3, "name": "budget-raise-gate / budget-raise-gate",
+                              "status": "in_progress", "conclusion": None}]
+    r_w, adv_w, t_w = build({**clean, "gate": gate_digest(raise_rerun),
+                             "required_read": ("WAIT", "pending: budget-raise-gate red: none")})
+    check("#3379: a required red that classify --pr reads WAIT renders: no refusal, a `required-wait` "
+          "advisory naming classify's line (classify decides; a pending check never refuses)",
+          r_w == [] and len(adv_w) == 1 and adv_w[0].startswith("required-wait: required context `gate`")
+          and "pending: budget-raise-gate" in t_w)
+    r_g, adv_g, _ = build({**clean, "gate": gate_digest(redgate), "required_read": ("GREEN", "pending: none red: none")})
+    check("a required red that classify --pr reads GREEN renders, with a `required-green` advisory",
+          r_g == [] and len(adv_g) == 1 and adv_g[0].startswith("required-green: required context `gate`"))
+    r_r, adv_r, _ = build({**clean, "gate": gate_digest(redgate), "required_read": ("RED", "pending: none red: gate")})
+    check("null control: a required red that classify --pr reads RED still refuses, naming classify's line",
+          len(r_r) == 1 and r_r[0].startswith("required-red: required context `gate`")
+          and "RED pending: none red: gate" in r_r[0] and adv_r == [])
     with tempfile.TemporaryDirectory() as d:
         stub = Path(d) / "classify.sh"
         stub.write_text('echo "$*" > "$(dirname "$0")/argv"; echo "${PK_OUT:-}"; exit "${PK_RC:-1}"\n')
@@ -702,14 +740,18 @@ def _self_test() -> int:
         os.environ["HPO_PACKET_CLASSIFY"] = f"bash {stub}"
         try:
             os.environ.update(PK_OUT=f"APPROVAL-OWED {H} 1 budget raise(s): why", PK_RC="4")
-            got = approval_owed_line(7, H)
+            got = required_reading(7, H)
             argv = (Path(d) / "argv").read_text().split()
             os.environ.update(PK_OUT=f"RED {H} pending: none red: gate", PK_RC="1")
-            red_line = approval_owed_line(7, H)
+            red_line = required_reading(7, H)
+            os.environ.update(PK_OUT=f"WAIT {H} pending: budget-raise-gate red: none", PK_RC="3")
+            wait_line = required_reading(7, H)
             os.environ.update(PK_OUT=f"APPROVAL-OWED {B} 1 budget raise(s): why", PK_RC="4")
-            other = approval_owed_line(7, H)
+            other = required_reading(7, H)
             os.environ.update(PK_OUT=f"APPROVAL-OWED {H} 1 budget raise(s): why", PK_RC="1")
-            wrong_rc = approval_owed_line(7, H)
+            wrong_rc = required_reading(7, H)
+            os.environ.update(PK_OUT=f"REFUSE ci: the check runs at {H[:12]} could not be read", PK_RC="2")
+            unread = required_reading(7, H)
         finally:
             os.environ.pop("PK_OUT", None), os.environ.pop("PK_RC", None)
             if saved is None:
@@ -717,9 +759,13 @@ def _self_test() -> int:
             else:
                 os.environ["HPO_PACKET_CLASSIFY"] = saved
     check("P345: the reason is classify --pr's own APPROVAL-OWED line at rc 4, asked with the pull "
-          "request; RED (rc 1), a line naming another head, and the line at any rc but 4 are None (null controls)",
-          got == "1 budget raise(s): why" and argv[:2] == ["classify", H] and argv[-2:] == ["--pr", "7"]
-          and red_line is None and other is None and wrong_rc is None)
+          "request; RED (rc 1), a line naming another head, and the line at any rc but 4 are RED (null controls)",
+          got == ("APPROVAL-OWED", "1 budget raise(s): why") and argv[:2] == ["classify", H]
+          and argv[-2:] == ["--pr", "7"] and red_line == ("RED", "pending: none red: gate")
+          and other[0] == "RED" and wrong_rc[0] == "RED")
+    check("#3379: classify's WAIT line at rc 3 is WAIT; a REFUSE at rc 2 (unread) fails closed as RED, naming it",
+          wait_line == ("WAIT", "pending: budget-raise-gate red: none")
+          and unread[0] == "RED" and "rc 2" in unread[1] and "could not be read" in unread[1])
     check("required-red null: the same head with that run green renders",
           build({**clean, "gate": gate_digest(list(reversed([dict(r, id=3 - r["id"]) for r in redgate])))})[0] == [])
     running = [{"id": 1, "name": "gate", "status": "in_progress", "conclusion": None},

## Before you return the verdict (P275)
Run `python3 -I tools/audit/carry_audit.py check --body <PR body file> --comments <file holding [{"id": 0, "body": <verdict.md text>}]>`. Give every reported item its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>`;
an evidence line flagged by its wording takes `Carry: dismissed: evidence, not a finding`. Return the verdict only at rc 0.
