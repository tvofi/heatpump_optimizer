# Review packet #3445
head: 7fb8680c857220f629c328b842f152d2c236542a
base: a7628041dc02e298c5399003d4c0576391dd5c4e

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: red
CodeQL id=130390431208 success
arch-score / arch-score id=130398094279 success
arm id=130389467539 skipped
budget-raise-gate / budget-raise-gate id=130398073557 success
cancel-superseded id=130398072498 success
codeql id=130398111345 skipped
codeql / Analyze (actions) id=130390360364 success
codeql / Analyze (javascript-typescript) id=130390360281 success
codeql / Analyze (python) id=130390360277 success
gate id=130398074842 success
governance id=130398108365 skipped
governance / delivery-status id=130390360006 success
governance / delivery-status-publish id=130390362037 skipped
governance / env-matrix id=130390360142 success
governance / instrument-self-tests id=130390360056 success
governance / policy-docs id=130390360217 success
governance / record id=130390362731 skipped
governance / wave-script id=130390360027 success
hassfest id=130398073667 skipped
hassfest / hassfest id=130390360039 success
kernel-points id=130398073572 skipped
pr-contract id=130398076419 skipped
pr-contract / pr-contract id=130397349729 success
prelude id=130398122644 success
refresh id=130398118895 success
sweep-self id=130398344757 skipped
tests id=130398105373 skipped
tests / arch-instrument id=130390606904 success
tests / briefs id=130390360062 success
tests / browser id=130390606955 success
tests / ci-ratchet id=130397350839 skipped
tests / claims-autofix id=130392615781 skipped
tests / closure-scope id=130390360072 success
tests / closures id=130390607005 success
tests / closures-autofix id=130397351660 skipped
tests / coverage id=130390606872 success
tests / coverage-ratchet id=130391035758 success
tests / fast (3.14) id=130390606868 success
tests / graders-head-copy id=130391035745 success
tests / lane-proofs id=130392613159 success
tests / mutation id=130390359958 success
tests / mutation-autofix id=130390688645 skipped
tests / mutation-pins id=130390688321 skipped
tests / nightly-ha id=130390610058 skipped
tests / nightly-status id=130390360120 failure
tests / replay id=130390609895 skipped
tests / typing id=130390606926 success
validate id=130398100962 skipped
validate / validate-hacs id=130390360071 success

## Refusals
none

## Advisories
none

## carry_audit at the head
CARRY-AUDIT: 0 finding item(s): 0 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
ok         python3 tools/audit/seat/review_packet.py --self-test | tail -1
             `tools/audit/seat/review_packet.py` is in the tree at this head
  ok         bash tools/audit/seat/body_patch.sh --self-test | tail -1
             `tools/audit/seat/body_patch.sh` is in the tree at this head
  ok         tools/pr/prepr.sh
             `tools/pr/prepr.sh` is in the tree at this head
  unverified git log --format=%B a7628041dc..HEAD | grep -ci 'claude\|co-authored\|session'
             `git log` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals

FIGURES: 3 resolved, 1 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
none

## Review scope: full (first round: no --reviewed-head)

## Three-dot diff
diff --git a/dev/programme/delivery/3445.md b/dev/programme/delivery/3445.md
new file mode 100644
index 0000000000..739ba14464
--- /dev/null
+++ b/dev/programme/delivery/3445.md
@@ -0,0 +1 @@
+- [#3445](https://github.com/tvofi/heatpump_optimizer/pull/3445) — **open**, R10-REVIEW-DISPATCH-RESIDUE (part 4): r10 review dispatch residue p4 (R10-REVIEW-DISPATCH-RESIDUE)
diff --git a/tools/audit/seat/review_packet.py b/tools/audit/seat/review_packet.py
index fbc86a2cbd..94501329a4 100644
--- a/tools/audit/seat/review_packet.py
+++ b/tools/audit/seat/review_packet.py
@@ -352,15 +352,27 @@ def fetch_roster_ref(roster_ref: str | None) -> str:
     return ref
 
 
-def handoff_not_applied(branch: str, head: str, tip_of, is_ancestor) -> str | None:
-    """Why `head` lacks its own handoff (P229), or None. `tip_of(topic)` is
-    `handoff/<topic>`'s tip on origin or None; the first topic with a ref
-    decides. A branch of another shape, or no handoff ref, is never refused."""
+def handoff_not_applied(branch: str, head: str, tip_of, is_ancestor, body: str = "",
+                        round_topic: str | None = None, behind=None) -> tuple[str | None, str | None]:
+    """(refusal, advisory) for `head` lacking its own handoff (P229). `tip_of(topic)`
+    is `handoff/<topic>`'s tip on origin or None; the first topic with a ref
+    decides. A branch of another shape, or no handoff ref, is never refused.
+    For `round_topic` alone (the round roster branch, which takes a commit a
+    minute while a landing takes ten) a head holding the snapshot sha its `## Head`
+    names is accepted when that sha is an ancestor of the tip; `behind(sha, tip)`
+    counts the commits it trails (S14)."""
     for t in handoff_topics(branch):
         tip = tip_of(t)
-        if tip:
-            return None if is_ancestor(tip, head) else f"handoff/{t} {tip} is not an ancestor of {head}"
-    return None
+        if not tip:
+            continue
+        if is_ancestor(tip, head):
+            return None, None
+        if t == round_topic:
+            for sha in re.findall(r"(?<![0-9a-f])[0-9a-f]{7,40}(?![0-9a-f])", section(body, "Head")):
+                if is_ancestor(sha, head) and is_ancestor(sha, tip):
+                    return None, f"roster snapshot {sha}, {behind(sha, tip)} commits behind handoff/{t}; a later landing takes the rest"
+        return f"handoff/{t} {tip} is not an ancestor of {head}", None
+    return None, None
 
 
 def origin_handoff_tip(topic: str) -> str | None:
@@ -544,12 +556,38 @@ def writes_packet(refusals: list[str]) -> bool:
     return not any(r.startswith("host-path:") for r in refusals)
 
 
-def unnamed_carries(body: str, n: int) -> list[int]:
-    """The 1-based indexes of a group's `n` roster carries the body never names
-    as `Carry N` (any case, `[N]` too). A count, not a judgement: whether the
-    named carry is answered well is the reviewer's."""
-    return [i for i in range(1, n + 1)
-            if not re.search(rf"\bcarry\s*\[?{i}\]?(?![0-9])", body, re.I)]
+def unnamed_carries(body: str, carries) -> list[int]:
+    """The 0-based indexes (`cloud_dispatch.py` renders `Carry {i}` from 0) among
+    `carries` -- a count `n` meaning `range(n)`, or the indexes themselves --
+    that the body never names as `Carry N` (any case, `[N]` too). A count, not a
+    judgement: whether the named carry is answered well is the reviewer's."""
+    idx = range(carries) if isinstance(carries, int) else carries
+    return [i for i in idx if not re.search(rf"\bcarry\s*\[?{i}\]?(?![0-9])", body, re.I)]
+
+
+def prompt_carries(prompt: str | None) -> list[int] | None:
+    """The `Carry N:` indexes a dispatch PROMPT.md holds, sorted, or None when
+    there is no prompt or it holds none: the carries the fixer was dispatched
+    with, which a roster appended to afterwards does not change (S14)."""
+    found = sorted({int(m) for m in re.findall(r"^Carry (\d+):", prompt or "", re.M)})
+    return found or None
+
+
+def handoff_carries(prompt: str | None, live: int):
+    """What `unnamed_carries` checks: the dispatched PROMPT's indexes, else the live roster count."""
+    return prompt_carries(prompt) or live
+
+
+def dispatch_prompt(topic: str) -> str | None:
+    """PROMPT.md of `origin`'s `dispatch/fixer-<topic>`, or None when the ref is
+    absent here or unreadable (the caller falls back to the live roster)."""
+    ref = f"refs/heads/dispatch/fixer-{topic}"
+    if not git("ls-remote", "origin", ref, check=False).split():
+        return None
+    if subprocess.run(["git", "fetch", "-q", "origin", ref], cwd=repo(), capture_output=True).returncode:
+        return None
+    r = subprocess.run(["git", "show", "FETCH_HEAD:PROMPT.md"], cwd=repo(), capture_output=True, text=True)
+    return r.stdout if r.returncode == 0 else None
 
 
 def handoff_refusals(structure: str | None, hot: list[str], unnamed: list[int],
@@ -582,9 +620,11 @@ def build(facts: dict) -> tuple[list[str], list[str], str]:
         refusals.append(f"head-note: ## Head does not name the dispatched head {head}"
                         + head_note_repair(head, facts.get("branch")))
     refusals += handoff_refusals(facts["structure"], facts["hot"], [])
+    (word, why), owed_adv = facts.get("required_read") or ("RED", ""), []
     for n in facts["red_unanswered"]:
+        if n in REQUIRED and word in ("WAIT", "GREEN"):
+            continue  # classify --pr reads it not red: its required-wait/green advisory names it (S14)
         refusals.append(f"red-unanswered: concluded red check `{n}` is not named in ## Red checks")
-    (word, why), owed_adv = facts.get("required_read") or ("RED", ""), []
     for n in sorted(set(reds) & set(REQUIRED)):
         if word == "APPROVAL-OWED":
             owed_adv.append(
@@ -642,6 +682,7 @@ def scope_parts(facts: dict) -> list[str]:
 
 
 def gather(a) -> dict:
+    import roster_lib
     head, main = a.head, a.main
     base = git("merge-base", main, head).strip()
     touched, existing = diff_paths(base, head)
@@ -650,7 +691,10 @@ def gather(a) -> dict:
     pr = gh(f"repos/{REPO}/pulls/{a.pr}") or {}
     body = pr.get("body") or ""
     branch = (pr.get("head") or {}).get("ref") or ""
-    handoff = handoff_not_applied(branch, head, origin_handoff_tip, is_ancestor)
+    rr = roster_lib.round_ref(roster_lib.git_in(str(repo())))
+    handoff, snap_adv = handoff_not_applied(
+        branch, head, origin_handoff_tip, is_ancestor, body, rr.removeprefix("origin/handoff/") if rr else None,
+        lambda sha, tip: git("rev-list", "--count", f"{sha}..{tip}").strip())
     unlanded: list[str] = []
     cites = landed_cites(body)
     if cites:  # no roster read at all for a body that cites no landed carry
@@ -676,8 +720,9 @@ def gather(a) -> dict:
         "structure": None if a.no_structure else structure_at_merge(main, head),
         "red_unanswered": red_unanswered, "host": host, "handoff": handoff,
         "hot": hot_file_refusals(touched, open_prs, boarded, a.pr),
-        "advisories": [] if os.environ.get("HPO_BUS_TRAIN_STATE") or not open_prs
-        else ["hot-file: HPO_BUS_TRAIN_STATE is unset, so every merge verdict reads unboarded"],
+        "advisories": ([] if os.environ.get("HPO_BUS_TRAIN_STATE") or not open_prs
+                       else ["hot-file: HPO_BUS_TRAIN_STATE is unset, so every merge verdict reads unboarded"])
+        + ([snap_adv] if snap_adv else []),
         "harness_label": label,
         "harness_base": run_harness(data, base, a.harness_arg) if data else "not run",
         "harness_head": run_harness(data, head, a.harness_arg) if data else "not run",
@@ -727,7 +772,8 @@ def handoff(a) -> int:
     except Exception as e:  # noqa: BLE001 -- an unread roster is not an empty one
         raise Unavailable(f"cannot read the roster at {ref}: {e}")
     gid = roster_lib.group_for_branch(roster, f"handoff/{a.topic}")
-    carries = len(roster_lib.groups_of(roster)[gid].get("carry") or []) if gid else 0
+    live = len(roster_lib.groups_of(roster)[gid].get("carry") or []) if gid else 0
+    carries = handoff_carries(dispatch_prompt(a.topic), live)
     open_prs, boarded = hot_prs(touched)
     anc = lambda sha: subprocess.run(  # noqa: E731
         ["git", "merge-base", "--is-ancestor", sha, head], cwd=repo(), capture_output=True).returncode == 0
@@ -736,7 +782,7 @@ def handoff(a) -> int:
                                 unlanded_carries(landed_cites(body), *reversed(roster_carry_reader([a.topic], ref))))
     for x in refusals:
         print(f"review_packet: REFUSE {x}", file=sys.stderr)
-    print(f"review-packet handoff: {gid or 'no group'} at {head[:12]}, {carries} carries, {len(refusals)} refused")
+    print(f"review-packet handoff: {gid or 'no group'} at {head[:12]}, {live} live, {carries if isinstance(carries, int) else len(carries)} dispatched carries, {len(refusals)} refused")
     return 1 if refusals else 0
 
 
@@ -861,6 +907,22 @@ def _self_test() -> int:
     check("null control: a required red that classify --pr reads RED still refuses, naming classify's line",
           len(r_r) == 1 and r_r[0].startswith("required-red: required context `gate`")
           and "RED pending: none red: gate" in r_r[0] and adv_r == [])
+    wait_rd = ("WAIT", "pending: gate red: none")
+    r_d, adv_d, _ = build({**clean, "gate": gate_digest(redgate), "red_unanswered": ["gate"], "required_read": wait_rd})
+    check("S14 red-unanswered: a required `gate` red that classify --pr reads WAIT renders one required-wait "
+          "advisory and no refusal", r_d == [] and len(adv_d) == 1 and adv_d[0].startswith("required-wait:"))
+    r_dg, _, _ = build({**clean, "gate": gate_digest(redgate), "red_unanswered": ["gate"], "required_read": ("GREEN", "")})
+    check("S14 red-unanswered: the same read GREEN renders", r_dg == [])
+    r_dr, _, _ = build({**clean, "gate": gate_digest(redgate), "red_unanswered": ["gate"], "required_read": ("RED", "pending: none red: gate")})
+    check("S14 red-unanswered null: the same with a RED read refuses red-unanswered and required-red",
+          [x.split(":")[0] for x in r_dr] == ["red-unanswered", "required-red"])
+    r_da, _, _ = build({**clean, "gate": gate_digest(redgate), "red_unanswered": ["gate"],
+                        "required_read": ("APPROVAL-OWED", "1 raise")})
+    check("S14 red-unanswered null: an APPROVAL-OWED read and an absent read keep the refusal",
+          [x.split(":")[0] for x in r_da] == ["red-unanswered"]
+          and "red-unanswered" in [x.split(":")[0] for x in build({**clean, "gate": gate_digest(redgate), "red_unanswered": ["gate"]})[0]])
+    check("S14 red-unanswered null: a non-required red (`tests / fast`) beside a WAIT read still refuses",
+          refused("red-unanswered", red_unanswered=["tests / fast"], required_read=wait_rd))
     with tempfile.TemporaryDirectory() as d:
         stub = Path(d) / "classify.sh"
         stub.write_text('echo "$*" > "$(dirname "$0")/argv"; echo "${PK_OUT:-}"; exit "${PK_RC:-1}"\n')
@@ -970,15 +1032,27 @@ def _self_test() -> int:
             os.unlink(f)
 
     # brief-carries (P256): every index on the group's roster entry is named.
-    six = "".join(f"Carry {i}: answered.\n" for i in range(1, 6))
-    check("brief-carries: a body answering carries 1-5 of 6 is refused naming carry 6",
-          unnamed_carries(six, 6) == [6]
-          and handoff_refusals(None, [], unnamed_carries(six, 6)) == ["brief-carries: carry 6 is not named in the body (`Carry N`)"])
-    check("brief-carries null: the same body with carry 6 dispositioned passes",
-          unnamed_carries(six + "Carry 6: carried to R10-X.\n", 6) == [])
+    six = "".join(f"Carry {i}: answered.\n" for i in range(5))
+    check("brief-carries: a body answering carries 0-4 of 6 (0-based, as the dispatch renders) is refused naming carry 5",
+          unnamed_carries(six, 6) == [5]
+          and handoff_refusals(None, [], unnamed_carries(six, 6)) == ["brief-carries: carry 5 is not named in the body (`Carry N`)"])
+    check("brief-carries null: the same body with carry 5 dispositioned passes",
+          unnamed_carries(six + "Carry 5: carried to R10-X.\n", 6) == [])
+    check("S14 brief-carries: carry 0 is checked, and a one-carry group is not asked for carry 1",
+          unnamed_carries("Carry 1: x\n", 1) == [0] and unnamed_carries("Carry 0: x\n", 1) == [])
+    prompt21 = "preamble\n" + "".join(f"Carry {i}: text\n" for i in range(21)) + "Carry 21 is mentioned mid-line, not a carry line\n"
+    check("S14 brief-carries: the dispatch PROMPT's Carry N: lines decide the set (21), not a live roster of 27",
+          prompt_carries(prompt21) == list(range(21))
+          and unnamed_carries("".join(f"Carry {i}: a\n" for i in range(21)), prompt_carries(prompt21)) == []
+          and unnamed_carries("".join(f"Carry {i}: a\n" for i in range(1, 21)), prompt_carries(prompt21)) == [0])
+    check("S14 brief-carries null: no PROMPT (None) falls to the live count, and a body missing a live carry is refused",
+          prompt_carries(None) is None and prompt_carries("no carries here") is None
+          and handoff_carries(None, 3) == 3 and unnamed_carries("Carry 0: a\nCarry 1: b\n", handoff_carries(None, 3)) == [2])
+    check("S14 brief-carries: with a 21-carry PROMPT and 27 live carries the check runs over the PROMPT's 21",
+          handoff_carries(prompt21, 27) == list(range(21)))
     check("brief-carries null: a group with no carries passes", unnamed_carries("", 0) == [])
     check("brief-carries: `carry 1` does not name carry 10, and `Carry [10]` does",
-          unnamed_carries("Carry 1: x\n", 10)[-1] == 10 and 10 not in unnamed_carries("Carry [10]: x\n", 10))
+          unnamed_carries("Carry 1: x\n", 11)[-1] == 10 and 10 not in unnamed_carries("Carry [10]: x\n", 11))
     check("handoff: structure and hot-file refuse beside the count, each named",
           [r.split(":")[0] for r in handoff_refusals("max_class_loc", ["#9 x"], [2])]
           == ["structure", "hot-file", "brief-carries"])
@@ -1130,16 +1204,41 @@ def _self_test() -> int:
             return subprocess.run(["git", "merge-base", "--is-ancestor", a, b], cwd=t, env=denv).returncode == 0
         tips = {"g": tip}.get
         check("handoff-not-applied: #2887's shape (old head merged with main, tip outside) refuses",
-              (handoff_not_applied("fix/g", stale, tips, anc) or "").startswith(f"handoff/g {tip} is not an ancestor of {stale}")
-              and refused("handoff-not-applied", handoff=handoff_not_applied("fix/g", stale, tips, anc)))
+              (handoff_not_applied("fix/g", stale, tips, anc)[0] or "").startswith(f"handoff/g {tip} is not an ancestor of {stale}")
+              and refused("handoff-not-applied", handoff=handoff_not_applied("fix/g", stale, tips, anc)[0]))
         check("handoff-not-applied: the `fix/<t>-pr` spelling reads handoff/<t>",
-              handoff_not_applied("fix/g-pr", stale, tips, anc) is not None)
+              handoff_not_applied("fix/g-pr", stale, tips, anc)[0] is not None)
         check("handoff-not-applied null: a head containing the handoff tip renders",
-              handoff_not_applied("fix/g", fresh, tips, anc) is None)
+              handoff_not_applied("fix/g", fresh, tips, anc)[0] is None)
         check("handoff-not-applied null: a pull request with no handoff ref renders",
-              handoff_not_applied("fix/nohandoff", stale, tips, anc) is None)
+              handoff_not_applied("fix/nohandoff", stale, tips, anc)[0] is None)
         check("handoff-not-applied null: a branch not spelled fix/<t> renders",
-              handoff_not_applied("g", stale, tips, anc) is None and handoff_not_applied("feat/g", stale, tips, anc) is None)
+              handoff_not_applied("g", stale, tips, anc)[0] is None and handoff_not_applied("feat/g", stale, tips, anc)[0] is None)
+
+        # S14 roster landing: the round roster branch outruns a landing, so a head
+        # holding the snapshot its ## Head names renders (round topic only).
+        snap = commit("roster snapshot", base)
+        rtip = commit("roster moved on", snap)
+        rtip2 = commit("roster moved on again", rtip)
+        landing = commit("landing head", snap, mainc)
+        side = commit("snapshot off the tip", base)
+        side_head = commit("head holding the off-tip snapshot", side)
+        rtips = {"g": rtip2}.get
+        nbehind = lambda sha, tp: tgit("rev-list", "--count", f"{sha}..{tp}").strip()  # noqa: E731
+        hb = lambda sha: f"## Head\n{sha}\n"  # noqa: E731
+        ref, adv = handoff_not_applied("fix/g", landing, rtips, anc, hb(snap), "g", nbehind)
+        check("S14 roster landing: the 3377 shape (head holds the named snapshot, an ancestor of the tip) renders "
+              "with the advisory", ref is None and adv == f"roster snapshot {snap}, 2 commits behind handoff/g; a later landing takes the rest")
+        check("S14 roster landing: a named snapshot not in the head is refused",
+              handoff_not_applied("fix/g", landing, rtips, anc, hb(side), "g", nbehind)[0] is not None
+              and handoff_not_applied("fix/g", landing, rtips, anc, hb(mainc), "g", nbehind)[0] is not None)
+        check("S14 roster landing: a named snapshot that is an ancestor of the tip but not of the head is refused",
+              handoff_not_applied("fix/g", landing, rtips, anc, hb(rtip), "g", nbehind)[0] is not None)
+        check("S14 roster landing: a snapshot in the head but not an ancestor of the tip is refused",
+              handoff_not_applied("fix/g", side_head, rtips, anc, hb(side), "g", nbehind)[0] is not None)
+        check("S14 roster landing null: a fixer topic (not the round's) with the same shape is refused as today (#2887)",
+              handoff_not_applied("fix/g", landing, rtips, anc, hb(snap), "other", nbehind)[0] is not None
+              and handoff_not_applied("fix/g", landing, rtips, anc, hb(snap), None, nbehind)[0] is not None)
 
         # WHICH CHECKOUT, pinned by a read, not by a comment: every git read
         # goes through `repo()`, and `repo()` is the working directory's

## Before you return the verdict (P275)
Run `python3 -I tools/audit/carry_audit.py check --body <PR body file> --comments <file holding [{"id": 0, "body": <verdict.md text>}]>`. Give every reported item its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>`;
an evidence line flagged by its wording takes `Carry: dismissed: evidence, not a finding`. Return the verdict only at rc 0.
