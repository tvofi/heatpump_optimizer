# Review packet #3379
head: 762fd619773d8e6291ab0d339454bc1a8d74ed55
base: 63bcdcaad827ad3d98f914bc2e5b6110f9bb9444

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: red
CodeQL id=130275338649 success
arch-score / arch-score id=130275272798 success
arm id=130274071353 skipped
budget-raise-gate / budget-raise-gate id=130275272562 failure
cancel-superseded id=130274076678 success
codeql id=130274760697 skipped
codeql / Analyze (actions) id=130275272508 success
codeql / Analyze (javascript-typescript) id=130275272534 success
codeql / Analyze (python) id=130275272540 success
gate id=130275128370 failure
governance id=130274760073 skipped
governance / delivery-status id=130275272860 success
governance / delivery-status-publish id=130275275132 skipped
governance / env-matrix id=130275272977 in_progress
governance / instrument-self-tests id=130275272885 in_progress
governance / policy-docs id=130275272772 success
governance / record id=130275275088 skipped
governance / wave-script id=130275272855 success
hassfest id=130274760404 skipped
hassfest / hassfest id=130275272742 success
kernel-points id=130275275036 skipped
pr-contract id=130275130183 skipped
prelude id=130274076677 success
refresh id=130274076370 success
sweep-self id=130275361463 skipped
tests id=130274760491 skipped
tests / arch-instrument id=130275626703 success
tests / briefs id=130275272654 success
tests / browser id=130275626681 in_progress
tests / closure-scope id=130275272667 success
tests / closures id=130275626679 in_progress
tests / coverage id=130275627122 in_progress
tests / fast (3.14) id=130275626767 in_progress
tests / mutation id=130275272786 success
tests / mutation-autofix id=130275819392 skipped
tests / mutation-pins id=130275819254 skipped
tests / nightly-ha id=130275628737 skipped
tests / nightly-status id=130275272610 success
tests / replay id=130275628010 skipped
tests / typing id=130275626705 success
validate id=130274759671 skipped
validate / validate-hacs id=130275272603 success

## Refusals
none

## Advisories
required-wait: required context `gate` reads concluded failure at 762fd619773d8e6291ab0d339454bc1a8d74ed55 in the digest, but merge_train.py classify --pr reads WAIT (pending: gate red: none): classify decides, as bus.sh's dispatch does, and a pending check never refuses

## carry_audit at the head
CARRY-AUDIT: 0 finding item(s): 0 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
ok         python3 tools/audit/seat/cloud_dispatch.py --self-test
             `tools/audit/seat/cloud_dispatch.py` is in the tree at this head
  ok         python3 -I tools/audit/seat/review_packet.py --self-test
             `tools/audit/seat/review_packet.py` is in the tree at this head
  ok         python3 dev/audit/harnesses/r10_hotfix_delta_review_mutants.py
             `dev/audit/harnesses/r10_hotfix_delta_review_mutants.py` is in the tree at this head
  ok         python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)
             `tests/closure.py` is in the tree at this head
  ok         tests/doc_claims.py
             `tests/doc_claims.py` is in the tree at this head
  ok         tests/entities.py
             `tests/entities.py` is in the tree at this head
  ok         node tools/policy/policy_lint.mjs
             `tools/policy/policy_lint.mjs` is in the tree at this head
  ok         python3 tools/audit/archscore/score.py --diff origin/main
             `tools/audit/archscore/score.py` is in the tree at this head

FIGURES: 8 resolved, 0 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
none

## Three-dot diff
diff --git a/dev/audit/harnesses/r10_hotfix_delta_review_mutants.py b/dev/audit/harnesses/r10_hotfix_delta_review_mutants.py
new file mode 100644
index 0000000000..8e541f426b
--- /dev/null
+++ b/dev/audit/harnesses/r10_hotfix_delta_review_mutants.py
@@ -0,0 +1,111 @@
+#!/usr/bin/env python3
+"""R10-HOTFIX-DELTA-REVIEW: one mutant per new arm of the later-round delta scope
+(review_packet.py's review_scope, previous_verdict, scope_facts and scope_parts;
+bus.sh dispatch's hand-on to the renderer; cloud_dispatch.py's reviewer render),
+each run against the mutated file's own self-test.
+
+    python3 dev/audit/harnesses/r10_hotfix_delta_review_mutants.py            # all, one at a time
+    python3 dev/audit/harnesses/r10_hotfix_delta_review_mutants.py --list     # enumerate only
+    python3 dev/audit/harnesses/r10_hotfix_delta_review_mutants.py M0 M2      # named
+
+Run from the branch's worktree on a clean tree. Each mutant replaces exactly
+one span of one file in place (a span that does not occur exactly once is
+STALE, never silently skipped), runs that file's `--self-test`, prints the FAIL
+lines and restores the file; mutant_guard restores every file on a kill. M0 is
+the unmutated tree and must pass; every other mutant must fail at least one
+check, else it SURVIVED. Serial, because the mutants share files.
+"""
+
+from __future__ import annotations
+
+import subprocess
+import sys
+from pathlib import Path
+
+def repo_root(start):
+    """The directory holding custom_components/heatpump_optimizer/manifest.json."""
+    from pathlib import Path
+    here = Path(start).resolve()
+    if here.is_file():
+        here = here.parent
+    marker = Path("custom_components") / "heatpump_optimizer" / "manifest.json"
+    for cand in (here, *here.parents):
+        if (cand / marker).is_file():
+            return cand
+    raise RuntimeError(f"no repository root above {start}")
+
+
+ROOT = repo_root(__file__)
+sys.path.insert(0, str(Path(__file__).resolve().parent))
+import mutant_guard  # noqa: E402 -- restores the mutated file on a kill (SIGTERM/SIGINT) and refuses a leftover mutant
+
+PACKET = "tools/audit/seat/review_packet.py"
+BUS = "tools/audit/seat/bus.sh"
+CLOUD = "tools/audit/seat/cloud_dispatch.py"
+RUN = {PACKET: [sys.executable, "-I", PACKET, "--self-test"], BUS: ["bash", BUS, "--self-test"],
+       CLOUD: [sys.executable, "-I", CLOUD, "--self-test"]}
+
+# (id, arm, file, the span, its replacement)
+MUTANTS = [
+    ("M0", "the unmutated head", PACKET, "", ""),
+    ("M1", "a later round's diff is `git diff <rh> <head>`", PACKET,
+     '"diff": git("diff", rh, head) if delta else git("diff", f"{base}...{head}")}',
+     '"diff": git("diff", f"{base}...{head}")}'),
+    ("M2", "the packet renders the delta and the previous verdict", PACKET,
+     '    if kind == "delta":\n        rh = facts["reviewed_head"]', '    if False:\n        rh = facts["reviewed_head"]'),
+    ("M3", "a reviewed head that is not the head's ancestor keeps the full diff", PACKET,
+     "    if not is_anc(rh, head):\n", "    if False:\n"),
+    ("M4", "the previous verdict is the one naming the reviewed head", PACKET,
+     "        if v and v[1] == rh:", "        if v:"),
+    ("M5", "bus.sh dispatch hands the renderer --reviewed-head", BUS,
+     ' ${rh:+--reviewed-head "$rh"} ', " "),
+    ("M7", "the packet's scope line carries the exception's production-code qualifier", PACKET,
+     '(custom_components/) puts at risk', 'puts at risk'),
+    ("M8", "the packet's scope line states a wider trigger", PACKET,
+     'never "\n                "justifies a wider review', 'never "\n                "justifies a wider review, or in full on code that review relied on'),
+    ("M6", "the cloud reviewer renders its packet with --reviewed-head", CLOUD,
+     '+ (f"--reviewed-head {reviewed_head} " if reviewed_head else "") +', "+"),
+]
+
+
+def one(m: tuple[str, str, str, str, str]) -> tuple[str, str, list[str]]:
+    mid, _arm, rel, old, new = m
+    src = ROOT / rel
+    text = src.read_text()
+    if old and text.count(old) != 1:
+        return mid, "STALE", [f"span occurs {text.count(old)} times in {rel}"]
+    try:
+        src.write_text(text.replace(old, new) if old else text)
+        cmds = list(RUN.values()) if mid == "M0" else [RUN[rel]]
+        rcs, fails = [], []
+        for cmd in cmds:
+            r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, timeout=1800)
+            rcs.append(r.returncode)
+            fails += [ln.strip() for ln in r.stdout.splitlines() if ln.startswith("  FAIL")]
+    finally:
+        src.write_text(text)
+    if mid == "M0":
+        return mid, "PASS" if not any(rcs) and not fails else "BROKEN", fails
+    return mid, "KILLED" if fails or any(rcs) else "SURVIVED", fails or [f"rc {rcs}"]
+
+
+def main(argv: list[str]) -> int:
+    mutant_guard.arm([PACKET, BUS, CLOUD])
+    if argv[:1] == ["--list"]:
+        for mid, arm, rel, _o, _n in MUTANTS:
+            print(f"{mid}\t{rel}\t{arm}")
+        return 0
+    todo = [m for m in MUTANTS if not argv or m[0] in argv]
+    bad = 0
+    for m in todo:
+        mid, state, fails = one(m)
+        print(f"{mid} {state}: {m[1]}")
+        for f in fails[:4]:
+            print(f"    {f[:200]}")
+        bad += state not in ("PASS", "KILLED")
+    print(f"MUTANTS: {len(todo)} run, {bad} not as required")
+    return 1 if bad else 0
+
+
+if __name__ == "__main__":
+    sys.exit(main(sys.argv[1:]))
diff --git a/dev/governance/config/policy_budgets.json b/dev/governance/config/policy_budgets.json
index a11c8218e0..a7153fb266 100644
--- a/dev/governance/config/policy_budgets.json
+++ b/dev/governance/config/policy_budgets.json
@@ -124,7 +124,7 @@
     "tools/audit/briefs/D7.md": 575,
     "tools/audit/briefs/D8.md": 808,
     "tools/audit/briefs/D9.md": 857,
-    "tools/audit/briefs/fix-review.md": 2451,
+    "tools/audit/briefs/fix-review.md": 2546,
     "tools/audit/briefs/fixer.md": 5216,
     "tools/audit/briefs/judge.md": 469,
     "tools/audit/briefs/nudge.md": 3814,
diff --git a/dev/governance/roles/fix-review.md b/dev/governance/roles/fix-review.md
index 892e45a4c8..7011f226cb 100644
--- a/dev/governance/roles/fix-review.md
+++ b/dev/governance/roles/fix-review.md
@@ -90,7 +90,12 @@ Long jobs and CI waits follow `fixer.md`'s preamble; rotate context between roun
     (#1667; tvofi 2026-10-27) while `tools/audit/seat/review_carry.py
     <verdicted> <new>` prints `CARRY`: the PR's patch is the one reviewed
     (L6), not `head-moved`; a red CI never carries.
-    Else a main merge is its **resolution delta**, alone yours; any other move is re-reviewed.
+    Else a later round is **its delta** (tvofi 2026-11-09): `git diff <reviewed-head>
+    <head>` (a main merge: its resolution), each prior finding resolved, the live
+    required checks. Only a delta touching production code (`custom_components/`)
+    that puts already-reviewed code's functionality at non-obvious risk, in a way
+    CI would not detect, widens it, to exactly that code; the verdict names the
+    path and the risk. Instrument, test, policy and body deltas never widen it.
 
 13. **A conflict is a measurement, not a status field.** `mergeStateStatus:
     DIRTY` is GitHub's, computed where the `claimnotes` driver cannot run
diff --git a/dev/programme/delivery/3379.md b/dev/programme/delivery/3379.md
new file mode 100644
index 0000000000..90adf5a5b4
--- /dev/null
+++ b/dev/programme/delivery/3379.md
@@ -0,0 +1 @@
+- [#3379](https://github.com/tvofi/heatpump_optimizer/pull/3379) — **open**, hotfix(review): later review rounds review only the delta (owner ruling 2026-11-09) (R10-HOTFIX-DELTA-REVIEW)
diff --git a/tests/closures.json b/tests/closures.json
index 388f371942..d75a7085c9 100644
--- a/tests/closures.json
+++ b/tests/closures.json
@@ -4148,6 +4148,7 @@
    "dev/audit/harnesses/r10_heat_meter_mutants.py",
    "dev/audit/harnesses/r10_hotfix_ci_critpath_3/replay.py",
    "dev/audit/harnesses/r10_hotfix_ci_critpath_4/replay.py",
+   "dev/audit/harnesses/r10_hotfix_delta_review_mutants.py",
    "dev/audit/harnesses/r10_hotfix_train_policy_mandate_mutants.py",
    "dev/audit/harnesses/r10_house_grade.py",
    "dev/audit/harnesses/r10_i1_action_guards.py",
diff --git a/tools/audit/seat/bus.sh b/tools/audit/seat/bus.sh
index 9acfcafd3f..04aee5bbf5 100755
--- a/tools/audit/seat/bus.sh
+++ b/tools/audit/seat/bus.sh
@@ -552,7 +552,8 @@ autofix_inflight() { # head -> prints the autofix bot jobs of the head that are
 # (ledger.py, beside $HPO_BUS_LEDGER else its default log): a seat started at that head.
 # THE REVIEW PACKET (R10-ORCH-REVIEW-PACKET; tvofi card 8): before recording, `review_packet.py
 # render` writes $S/packets/<pr>-<head>.md, refusing on its mechanical signals, and dispatch
-# names it only once `check` reads that head in it. --harness/--harness-file is the finder's.
+# names it only once `check` reads that head in it. --harness/--harness-file is the finder's;
+# --reviewed-head makes a later round's packet its delta and the verdict there (fix-review.md 12).
 # HPO_BUS_PACKER replaces the renderer (the self-test's stub).
 dispatch() { # pr head reviewer [--reviewed-head <sha>] [--nonce N] [--model M] [--past-three <reason>] [--harness P|--harness-file F] -> records, closes, prints the packet and nonce lines
   local force="" fixing=""
@@ -677,7 +678,7 @@ dispatch() { # pr head reviewer [--reviewed-head <sha>] [--nonce N] [--model M]
   # told nothing about a packet and one told "no packet, because X" are in different
   # worlds, and only the second is honest (R10-ORCH-REVIEW-PACKET, #2870).
   pmsg=$(${HPO_BUS_PACKER:-python3 -I "$ROOT/tools/audit/seat/review_packet.py"} render \
-           --pr "$pr" --head "$h" --out "$pk" ${hk:+"$hk" "$hv"} 2>&1 >/dev/null) || prc=$?
+           --pr "$pr" --head "$h" --out "$pk" ${rh:+--reviewed-head "$rh"} ${hk:+"$hk" "$hv"} 2>&1 >/dev/null) || prc=$?
   if [ "$prc" = 0 ] && ! python3 -I "$ROOT/tools/audit/seat/review_packet.py" check "$pk" --head "$h" >/dev/null 2>&1; then
     prc=3
     pmsg="review_packet: UNAVAILABLE: the packet written does not name the head $h"
@@ -1256,6 +1257,8 @@ bus-nonce: $N1b" ] && [ "$(grep -c " $N1b " "$W/state/dispatched")" = 2 ] \
     && echo "$out" | grep -qF "review-carry: $h1 was blocked, so a fresh review is owed" \
     && [ "$(grep -c "^31 $hm cmsg_C3 " "$W/state/dispatched")" = 1 ]
   expect "P348: a blocked verdict at the reviewed head over a clean range mints, says why, and records (#3045 r3)" $?
+  tail -n 1 "$W/packs" | grep -q "^render|--pr|31|--head|$hm|--out|[^|]*|--reviewed-head|$h1|\$"
+  expect "a later round's dispatch hands the renderer its --reviewed-head, so the packet is the delta (fix-review.md 12; null: the harness dispatch below passes none)" $?
   vc merge "$h1"; vc blocked "$h2" "harness: another head"; n=$(grep -c . "$W/state/dispatched")
   out=$(seat dispatch 31 "$hm" cmsg_C4 --reviewed-head "$h1"); rc=$?
   [ $rc != 0 ] && echo "$out" | grep -q "review_carry: CARRY" && [ "$(grep -c . "$W/state/dispatched")" = "$n" ]
diff --git a/tools/audit/seat/cloud_dispatch.py b/tools/audit/seat/cloud_dispatch.py
index d06a658d5f..341fef13b4 100644
--- a/tools/audit/seat/cloud_dispatch.py
+++ b/tools/audit/seat/cloud_dispatch.py
@@ -218,7 +218,7 @@ def _pointer(role: str, repo: str, pr: str, head: str, topic: str, nonce: str, r
 
 
 def _prompt(role: str, repo: str, pr: str, head: str, topic: str, nonce: str, brief: str,
-            design: str = "") -> str:
+            design: str = "", reviewed_head: str = "") -> str:
     first = _seat_line(role, repo, pr, head, topic, nonce) + " " + FOOTER_BAN
     pin = (f"Before any commit, pin the seat identity: `git config user.name {SEAT_NAME} && git config "
            f"user.email {SEAT_EMAIL}`. ") if role in COMMITTING_ROLES else ""
@@ -246,6 +246,7 @@ def _prompt(role: str, repo: str, pr: str, head: str, topic: str, nonce: str, br
                  "the PR body is in the PR. Start from the review packet, which you render here rather than read from the "
                  "dispatcher, whose copy is a path on its own machine: "
                  f"`python3 -I tools/audit/seat/review_packet.py render --pr {pr} --head {head} "
+                 + (f"--reviewed-head {reviewed_head} " if reviewed_head else "") +
                  "--out $HOME/review-packet.md`. A refusal names its signal and the packet is still "
                  "written unless the signal is `host-path`; re-read the live checks either way. ")
         wait_ci = ("\n" if at_handoff else
@@ -262,6 +263,11 @@ def _prompt(role: str, repo: str, pr: str, head: str, topic: str, nonce: str, br
         body = (
             "Role: read dev/governance/roles/fix-review.md and its rules from main, and follow them "
             f"exactly. Fetch the {'handoff' if at_handoff else 'PR'} head with `git fetch origin {head}`; " + where +
+            (f"This is a later round over the reviewed head {reviewed_head}: its scope is the packet's "
+             "`## Review scope` line, the delta and the previous verdict's findings when it reads `delta`, "
+             "widened only to the exact already-reviewed code a production (custom_components/) delta puts "
+             "at non-obvious risk that CI would not detect, the verdict naming path and risk; an "
+             "instrument, test, policy or body delta never widens it (fix-review.md step 12). " if reviewed_head else "") +
             "Verify each claim adversarially: mutate the fix and check the tests fail, and check "
             "every figure in the body at this head. Check that it merges with origin/main "
             "(`git merge-tree --write-tree origin/main <head>`); block on main only when that reports a "
@@ -353,7 +359,7 @@ def _prompt(role: str, repo: str, pr: str, head: str, topic: str, nonce: str, br
 
 def render(role: str, head: str, *, env_id: str, model: str, repo: str, pr: str = "",
            topic: str = "", nonce: str = "", brief: str = "", publish_ref: str = "",
-           design: str = "", pin: str = "") -> dict:
+           design: str = "", pin: str = "", reviewed_head: str = "") -> dict:
     """The payload; with `publish_ref`, its event is the stub naming PROMPT.md at commit
     `pin` of that ref (`publish_seat`)."""
     if role not in ROLES:
@@ -369,6 +375,8 @@ def render(role: str, head: str, *, env_id: str, model: str, repo: str, pr: str
             raise Refusal("a reviewer needs --pr <number> (or --topic <t>, a reviewer at the handoff before the PR opens)")
     elif not topic.strip() or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", topic):
         raise Refusal("a fixer, probe or design seat needs --topic (letters, digits, . _ -)")
+    if reviewed_head and (role != "reviewer" or not is_head(reviewed_head)):
+        raise Refusal("--reviewed-head is a reviewer's: the 40-hex head a previous verdict names")
     if role == "design-reviewer" and not is_head(design or ""):
         raise Refusal("a design reviewer needs --design <the 40-hex design/<topic> tip it reviews>")
     for name, val in (("environment id", env_id), ("model", model), ("repo", repo)):
@@ -379,7 +387,7 @@ def render(role: str, head: str, *, env_id: str, model: str, repo: str, pr: str
     if publish_ref and not is_head(pin):
         raise Refusal("a published seat's stub needs the 40-hex commit holding its PROMPT.md")
     text = (_pointer(role, repo, pr, head, topic, nonce, publish_ref, pin) if publish_ref
-            else _prompt(role, repo, pr, head, topic, nonce, brief, design))
+            else _prompt(role, repo, pr, head, topic, nonce, brief, design, reviewed_head))
     payload = {"job_config": {"ccr": {
         "environment_id": env_id,
         "session_context": {
@@ -526,7 +534,7 @@ def design_approved(repo_dir: str, group_id: str) -> bool:
 def dispatch_group(role: str, group_id: str, model: str, *, repo_dir: str = ".",
                    roster_ref: str | None = None, head: str = "", pr: str = "", nonce: str = "",
                    overlay: str | None = None, environ=None, design_exempt: str = "",
-                   carry_only: bool = False, record_pr: bool = False) -> str:
+                   carry_only: bool = False, record_pr: bool = False, reviewed_head: str = "") -> str:
     """Render the seat for `group_id` from the roster, publish it, return its ref name.
 
     The roster at `roster_ref` of `repo_dir` (default: the round's roster
@@ -572,11 +580,12 @@ def dispatch_group(role: str, group_id: str, model: str, *, repo_dir: str = ".",
         if not design:
             raise Refusal(f"no design/{group_id} on origin to review")
     args = dict(design=design, env_id=known["env_id"], model=model, repo=roster.get("repo") or known["repo"],
-                pr=pr, topic=topic, brief=group_brief(group, roster, fixer=role == "fixer"))
+                pr=pr, topic=topic, brief=group_brief(group, roster, fixer=role == "fixer"),
+                reviewed_head=reviewed_head)
     head = head or _git(repo_dir, "rev-parse", f"{HEAD_REF}^{{commit}}").strip()
     if role == "reviewer":
         render(role, head, **args, nonce=BUS_PROBE_NONCE)  # every other refusal, before the bus records
-        nonce = _bus_dispatch(repo_dir, pr, head, model, nonce, environ)
+        nonce = _bus_dispatch(repo_dir, pr, head, model, nonce, environ, reviewed_head)
     ref = dispatch_ref(role, topic, "")
     try:
         publish_seat(repo_dir, ref, role, head, **args, nonce=nonce)
@@ -597,12 +606,14 @@ def _ledger_log(environ) -> list[str]:
     return ["--log", environ["HPO_BUS_LEDGER"]] if environ.get("HPO_BUS_LEDGER") else []
 
 
-def _bus_dispatch(repo_dir: str, pr: str, head: str, model: str, nonce: str, environ) -> str:
+def _bus_dispatch(repo_dir: str, pr: str, head: str, model: str, nonce: str, environ,
+                  reviewed_head: str = "") -> str:
     """The reviewer's nonce through `bus.sh dispatch`, the worker registry: minted, or a nonce
     minted earlier at this pr and head (the relay's) re-recorded with this seat and model. Either
     closes `reviewer-fire <pr> <head>` in the ledger."""
     r = subprocess.run(["bash", str(HERE / "bus.sh"), "dispatch", pr, head, "cloud", "--model", model,
-                        *(["--nonce", nonce] if nonce else [])],
+                        *(["--nonce", nonce] if nonce else []),
+                        *(["--reviewed-head", reviewed_head] if reviewed_head else [])],
                        cwd=repo_dir, env={**os.environ, **environ}, capture_output=True, text=True)
     n = proof_watch.verdict_nonce(r.stdout)
     if r.returncode or not n:
@@ -888,6 +899,23 @@ def _group_checks(check) -> None:
               and git(work, "rev-parse", "origin/main").strip() not in fetched("dispatch/reviewer-r10-x", "PROMPT.md"))
         check("the reviewer's brief carries the packet render at the dispatched head for the seat's own machine",
               f"review_packet.py render --pr 7 --head {rhead} " in fetched("dispatch/reviewer-r10-x", "PROMPT.md"))
+        rh2 = "c" * 40
+        p_later = _prompt("reviewer", "o/r", "7", rhead, "", "1" * 32, "", "", rh2)
+        p_first = _prompt("reviewer", "o/r", "7", rhead, "", "1" * 32, "")
+        check("a later round's reviewer renders its packet with --reviewed-head and is told its scope is the delta "
+              "(fix-review.md 12); null: a first round's render names no reviewed head",
+              f"render --pr 7 --head {rhead} --reviewed-head {rh2} --out " in p_later
+              and f"later round over the reviewed head {rh2}" in p_later
+              and f"render --pr 7 --head {rhead} --out " in p_first and "--reviewed-head" not in p_first)
+        check("the later-round reviewer prompt carries the exception's three qualifiers and no wider trigger",
+              "custom_components/" in p_later and "non-obvious" in p_later and "CI would not" in p_later
+              and "reaches code that review relied on" not in p_later and "in full" not in p_later)
+        try:
+            render("fixer", rhead, env_id="e", model="m", repo="o/r", topic="t", reviewed_head=rh2)
+            ok = False
+        except Refusal:
+            ok = True
+        check("--reviewed-head is a reviewer's: a fixer given one is refused", ok)
         check("a nonce no dispatch minted is refused by the bus, and records nothing",
               refused(role="reviewer", head=rhead, pr="7", nonce="0" * 32) and len(registry()) == 1)
         check("a packet the renderer refuses holds the reviewer dispatch, and records nothing",
@@ -1253,7 +1281,7 @@ def self_test() -> int:
 #: self-test drives each entry through main() and refuses a flag missing here.
 GROUP_FLAGS = {
     "role": None, "group": None, "model": None, "head": None, "roster_ref": None,
-    "pr": None, "nonce": None, "overlay": None, "design_exempt": None,
+    "pr": None, "nonce": None, "overlay": None, "design_exempt": None, "reviewed_head": None,
     "carry_only": None, "record_pr": None,
     "design": "dispatch_group reads the tip of design/<group> on origin",
     "topic": "the roster gives the topic (the group's branch)",
@@ -1276,6 +1304,8 @@ def _parser() -> argparse.ArgumentParser:
     ap.add_argument("--topic", default="")
     ap.add_argument("--nonce", default="")
     ap.add_argument("--design", default="", help="a design reviewer's reviewed design/<topic> tip (flag path)")
+    ap.add_argument("--reviewed-head", default="", help="a later round's reviewer: the head the previous verdict "
+                    "names, so the packet renders its delta (fix-review.md step 12)")
     ap.add_argument("--design-exempt", default="", help="a fixer dispatch for an L/XL group whose approved "
                     "design, pre-study or prototype is already on record: the reason")
     ap.add_argument("--brief")
@@ -1304,7 +1334,7 @@ def main(argv: list[str]) -> int:
                     raise Refusal(f"--{dest.replace('_', '-')} does not apply with --group: {why}")
             print(dispatch_group(args.role, args.group, args.model or "", roster_ref=args.roster_ref,
                                  head=args.head or "", pr=args.pr, design_exempt=args.design_exempt,
-                                 nonce=args.nonce, overlay=args.overlay,
+                                 nonce=args.nonce, overlay=args.overlay, reviewed_head=args.reviewed_head,
                                  carry_only=args.carry_only, record_pr=args.record_pr))
             return 0
         if not args.head:
@@ -1315,7 +1345,8 @@ def main(argv: list[str]) -> int:
                 brief = Path(args.brief).read_text()
             except OSError as e:
                 raise Refusal(f"unreadable brief: {e.__class__.__name__}")
-        known = dict(pr=args.pr, topic=args.topic, nonce=args.nonce, brief=brief, design=args.design, **_config(args))
+        known = dict(pr=args.pr, topic=args.topic, nonce=args.nonce, brief=brief, design=args.design,
+                     reviewed_head=args.reviewed_head, **_config(args))
         if args.publish:
             payload = publish_seat(".", dispatch_ref(args.role, args.topic, args.pr), args.role, args.head,
                                    **known)
diff --git a/tools/audit/seat/instruments/bus.sh.md b/tools/audit/seat/instruments/bus.sh.md
index d896c69f9c..2f46432448 100644
--- a/tools/audit/seat/instruments/bus.sh.md
+++ b/tools/audit/seat/instruments/bus.sh.md
@@ -33,7 +33,8 @@
   `review_carry.py` answers CARRY refuses only when the latest verdict naming
   `rh` on `verdict/<pr>` is merge; a blocked one, or none, dispatches and prints
   `review-carry: <rh> was blocked|has no verdict, so a fresh review is owed`,
-  and an unreadable `verdict/<pr>` refuses (P348).
+  and an unreadable `verdict/<pr>` refuses (P348). The renderer is handed `--reviewed-head`
+  too, so the packet is that round's delta.
 
 The design steps (decision 0014) write the same append-only way:
 `bus.sh push-design <topic> <design.md>` adds `design.md` to `design/<topic>`;
diff --git a/tools/audit/seat/instruments/review_packet.py.md b/tools/audit/seat/instruments/review_packet.py.md
index 35379117f8..675819084c 100644
--- a/tools/audit/seat/instruments/review_packet.py.md
+++ b/tools/audit/seat/instruments/review_packet.py.md
@@ -1,7 +1,10 @@
 # `review_packet.py`
 
 - `review_packet.py` — the fix reviewer's packet at the frozen head: three-dot
-  diff, the head's check runs as read (red, pending, `none` or green, with run
+  diff (with `--reviewed-head <rh>`, which `bus.sh dispatch` and
+  `cloud_dispatch.py --role reviewer` pass on, a later round's `git diff <rh> <head>`
+  and the verdict naming `rh` instead; a first round, an `rh` not the head's
+  ancestor or one no verdict names keeps the three-dot diff and says which), the head's check runs as read (red, pending, `none` or green, with run
   ids), `carry_audit.py` and `figure_lint.mjs` at the head, the finder's
   harness at both ends when one is named (`--harness`, at the base and
   untouched by the diff, or `--harness-file` outside the tree; `none named`
diff --git a/tools/audit/seat/review_packet.py b/tools/audit/seat/review_packet.py
index 17d94866b9..fbc86a2cbd 100644
--- a/tools/audit/seat/review_packet.py
+++ b/tools/audit/seat/review_packet.py
@@ -1,7 +1,7 @@
 #!/usr/bin/env python3
 """The fix reviewer's packet: the facts a review gathers, rendered once at the frozen head.
 
-    review_packet.py render --pr N --head SHA --out FILE [--main REF]
+    review_packet.py render --pr N --head SHA --out FILE [--main REF] [--reviewed-head SHA]
                             [--harness PATH | --harness-file FILE] [--harness-arg A]...
     review_packet.py check FILE --head SHA     (rc 1: the packet names another head)
     review_packet.py handoff --topic T --body FILE [--main REF] [--roster-ref REF]
@@ -17,6 +17,13 @@ the head when one is named (`none named` and `not run` otherwise), and the
 mutation-ledger diff. Nothing in it reads a clock, so a second render over the
 same facts is byte-identical.
 
+A LATER ROUND IS ITS DELTA (tvofi, 2026-11-09; fix-review.md step 12). With
+`--reviewed-head <rh>` (`bus.sh dispatch` passes its own), the packet holds
+`git diff <rh> <head>` and the VERDICT.md of the latest verdict/<pr> commit
+whose first line names <rh>, in place of the three-dot diff. A first round, an
+<rh> that is not an ancestor of the head, or one no verdict names keeps the
+three-dot diff and says which (`review_scope`).
+
 WHICH CHECKOUT. Every git read runs in the checkout the WORKING DIRECTORY is in,
 never in the directory this module is installed under: `bus.sh dispatch` runs
 the renderer where it dispatches (a cloud dispatch does so in a throwaway
@@ -381,6 +388,42 @@ def verdict_merge_head(sha: str, read=None) -> str | None:
     return v[1] if v and v[0] == "merge" else None
 
 
+def previous_verdict(pr: int, rh: str, shas=None, read=None) -> str | None:
+    """VERDICT.md of the newest verdict/<pr> commit whose first line names <rh>,
+    parsed by `proof_watch.parse_verdict`; None when no verdict names it or the
+    ref is absent. An unreadable ref is UNAVAILABLE, never read as no verdict."""
+    if shas is None:
+        r = subprocess.run(["git", "ls-remote", "origin", f"refs/heads/verdict/{pr}"],
+                           cwd=repo(), capture_output=True, text=True)
+        if r.returncode:
+            raise Unavailable(f"git ls-remote verdict/{pr}: {r.stderr.strip()[:200]}")
+        tip = r.stdout.split()[:1]
+        if not tip:
+            return None
+        git("fetch", "-q", "origin", f"refs/heads/verdict/{pr}")
+        shas = git("log", "--format=%H", tip[0]).split()
+    read = read or (lambda s: git("show", f"{s}:VERDICT.md", check=False))
+    for sha in shas:
+        text = read(sha)
+        v = proof_watch.parse_verdict(text.splitlines()[0]) if text.strip() else None
+        if v and v[1] == rh:
+            return text
+    return None
+
+
+def review_scope(rh: str | None, head: str, verdict: str | None, is_anc) -> tuple[str, str]:
+    """("delta" | "full", why): a later round reviews `git diff <rh> <head>`
+    beside the verdict at <rh> (fix-review.md step 12); every other round the
+    three-dot diff."""
+    if not rh:
+        return "full", "first round: no --reviewed-head"
+    if not is_anc(rh, head):
+        return "full", f"the reviewed head {rh} is not an ancestor of {head}, so its delta is no later round's"
+    if verdict is None:
+        return "full", f"no verdict on verdict/<pr> names the reviewed head {rh}, so there is no finding to confirm resolved"
+    return "delta", f"later round over the reviewed head {rh}"
+
+
 def harness_source(harness: str | None, harness_file: str | None, base: str,
                    touched: set[str], cwd: Path | None = None) -> tuple[str, bytes]:
     """(label, bytes) of the finder's harness; SystemExit on the fixer's."""
@@ -573,7 +616,7 @@ def build(facts: dict) -> tuple[list[str], list[str], str]:
         f"## Finder's harness: {facts['harness_label']}",
         "### at the base", facts["harness_base"], "### at the head", facts["harness_head"], "",
         "## Mutation-ledger diff", facts["ledger_diff"] or "none", "",
-        "## Three-dot diff", facts["diff"],
+        *scope_parts(facts),
         "## Before you return the verdict (P275)",
         f"Run `{SELF_AUDIT}`. Give every reported item its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>`;",
         "an evidence line flagged by its wording takes `Carry: dismissed: evidence, not a finding`. Return the verdict only at rc 0.",
@@ -581,6 +624,23 @@ def build(facts: dict) -> tuple[list[str], list[str], str]:
     return refusals, advisories, "\n".join(parts) + "\n"
 
 
+def scope_parts(facts: dict) -> list[str]:
+    """The packet's diff sections: the delta and the previous verdict on a later
+    round, else the three-dot diff (a facts dict without a scope is a first round)."""
+    kind, why = facts.get("scope") or ("full", "first round: no --reviewed-head")
+    if kind == "delta":
+        rh = facts["reviewed_head"]
+        return [f"## Review scope: delta ({why})",
+                "Confirm each finding of the previous verdict is resolved, re-read the live required checks, and review "
+                "the delta below. Widen only to exactly the already-reviewed code a delta touching production code "
+                "(custom_components/) puts at risk of being affected in a non-obvious way CI would not detect, "
+                "naming the path and the risk in the verdict; an instrument, test, policy or body delta never "
+                "justifies a wider review (fix-review.md step 12).", "",
+                f"## Previous verdict at {rh}", facts["previous_verdict"].rstrip("\n"), "",
+                f"## Delta diff: git diff {rh} {facts['head']}", facts["diff"]]
+    return [f"## Review scope: full ({why})", "", "## Three-dot diff", facts["diff"]]
+
+
 def gather(a) -> dict:
     head, main = a.head, a.main
     base = git("merge-base", main, head).strip()
@@ -622,10 +682,19 @@ def gather(a) -> dict:
         "harness_base": run_harness(data, base, a.harness_arg) if data else "not run",
         "harness_head": run_harness(data, head, a.harness_arg) if data else "not run",
         "ledger_diff": git("diff", f"{base}...{head}", "--", LEDGER),
-        "diff": git("diff", f"{base}...{head}"),
+        **scope_facts(a.pr, getattr(a, "reviewed_head", None), base, head),
     }
 
 
+def scope_facts(pr: int, rh: str | None, base: str, head: str, read_verdict=None) -> dict:
+    """gather's scope keys: the round's scope, the verdict at <rh> and the diff it reviews."""
+    verdict = (read_verdict or previous_verdict)(pr, rh) if rh else None
+    scope = review_scope(rh, head, verdict, is_ancestor)
+    delta = scope[0] == "delta"
+    return {"scope": scope, "reviewed_head": rh, "previous_verdict": verdict,
+            "diff": git("diff", rh, head) if delta else git("diff", f"{base}...{head}")}
+
+
 def hot_prs(touched: set[str]) -> tuple[list[dict], set[int]]:
     """(open pull requests, boarded numbers) the hot-file rule reads; no read
     at all when the diff touches no hot file."""
@@ -836,6 +905,41 @@ def _self_test() -> int:
     check("a head with no run read is `none`, never `green`",
           est == "none" and elines == [] and build({**clean, "gate": (est, elines, [])})[0] == [])
 
+    # A LATER ROUND IS ITS DELTA (tvofi, 2026-11-09). Null control first: a
+    # first round, with no reviewed head, keeps the three-dot diff.
+    check("scope null: a first round renders the three-dot diff and no delta or previous verdict",
+          "## Review scope: full (first round" in t0 and "## Three-dot diff\nd\n" in t0
+          and "## Delta diff" not in t0 and "## Previous verdict" not in t0)
+    RH = "c" * 40
+    pv = f"Fix review: blocked {RH} class-open: seam X\n\n## Findings\n\n- seam X is open. Carry: #1\n"
+    _, _, td_ = build({**clean, "scope": ("delta", "later round"), "reviewed_head": RH, "previous_verdict": pv,
+                       "diff": "delta-only\n"})
+    check("scope: a later round renders `git diff <rh> <head>` and the previous verdict's findings, not the three-dot diff",
+          f"## Delta diff: git diff {RH} {H}\ndelta-only\n" in td_ and f"## Previous verdict at {RH}" in td_
+          and "- seam X is open." in td_ and "## Three-dot diff" not in td_ and "## Review scope: delta" in td_)
+    # The exception's wording (tvofi, 2026-11-09): three qualifiers, no wider trigger.
+    step12 = (ROOT / "dev/governance/roles/fix-review.md").read_text()
+    step12 = step12[step12.index("Else a later round is"):]
+    step12 = step12[:step12.index("\n13. ")]
+    for label, text in (("the packet's scope line", td_), ("fix-review.md step 12", " ".join(step12.split()))):
+        check(f"{label}: the exception names production code, non-obvious risk and CI's blindness, and the wider "
+              "trigger wording is absent",
+              "custom_components/" in text and "non-obvious" in text and "CI would not" in text
+              and "reaches code that review relied on" not in text and "in full" not in text
+              and ("never justifies a wider review" in text or "never widen it" in text))
+    anc_yes, anc_no = (lambda a, b: True), (lambda a, b: False)
+    check("review_scope: delta only with a reviewed head that is an ancestor and a verdict naming it; else full, saying why",
+          review_scope(RH, H, pv, anc_yes)[0] == "delta"
+          and review_scope(None, H, pv, anc_yes) == ("full", "first round: no --reviewed-head")
+          and review_scope(RH, H, pv, anc_no)[0] == "full" and "not an ancestor" in review_scope(RH, H, pv, anc_no)[1]
+          and review_scope(RH, H, None, anc_yes)[0] == "full" and "no verdict" in review_scope(RH, H, None, anc_yes)[1])
+    vs = {"s3": f"Fix review: merge {H}\n", "s2": pv, "s1": f"Fix review: blocked {RH} old: first\n", "s0": "not a verdict\n"}
+    check("previous_verdict: the newest verdict whose first line names <rh>; another head's, an older one and a "
+          "malformed line are skipped; none naming it is None",
+          previous_verdict(7, RH, ["s3", "s0", "s2", "s1"], vs.get) == pv
+          and previous_verdict(7, B, ["s3", "s0", "s2", "s1"], vs.get) is None
+          and previous_verdict(7, RH, [], vs.get) is None)
+
     # EVIDENCE IS NEVER WITHHELD: a refusal still writes the packet, except the
     # one signal a written packet would defeat.
     check("write-on-refusal null: a clean render writes", writes_packet([]))
@@ -1079,6 +1183,27 @@ def _self_test() -> int:
         check("diff_paths -> red-unanswered: the row the diff adds owes main's delivery-status nothing",
               unanswered_reds(unanswering, H, B, ds, *paths, []) == [])
 
+        # The scope over real commits: <rh> on top of pbase, the head on top of <rh>.
+        (t / "kept.txt").write_text("round two\n")
+        tgit("add", "-A")
+        tgit("commit", "-q", "-m", "round two")
+        rhead = tgit("rev-parse", "HEAD").strip()
+        here, _REPO_ROOT = os.getcwd(), None
+        try:
+            os.chdir(t)
+            later = scope_facts(7, phead, pbase, rhead, lambda pr, rh: f"Fix review: blocked {rh} x: y\n")
+            first = scope_facts(7, None, pbase, rhead, lambda pr, rh: f"Fix review: blocked {rh} x: y\n")
+            stray = scope_facts(7, rhead, pbase, phead, lambda pr, rh: f"Fix review: blocked {rh} x: y\n")
+        finally:
+            os.chdir(here)
+            _REPO_ROOT = None
+        check("scope_facts: a later round's diff is `git diff <rh> <head>` alone -- the round-one row is not in it",
+              later["scope"][0] == "delta" and "+round two" in later["diff"] and row not in later["diff"])
+        check("scope_facts null: a first round over the same head reads the three-dot diff, round one's row included",
+              first["scope"][0] == "full" and "+round two" in first["diff"] and row in first["diff"])
+        check("scope_facts null: a reviewed head that is not the head's ancestor reads the three-dot diff",
+              stray["scope"][0] == "full" and row in stray["diff"])
+
         # UNAVAILABLE is a different outcome from a refusal: a seat that cannot
         # read the inputs reports rc 3 and writes nothing, and `bus.sh dispatch`
         # degrades on it. Driven through main(), the path bus.sh calls.
@@ -1132,6 +1257,7 @@ def main(argv: list[str]) -> int:
     r.add_argument("--head", required=True)
     r.add_argument("--out", required=True)
     r.add_argument("--main", default="origin/main")
+    r.add_argument("--reviewed-head", help="the head a previous verdict names: a later round's packet is its delta")
     g = r.add_mutually_exclusive_group()
     g.add_argument("--harness")
     g.add_argument("--harness-file")
@@ -1158,8 +1284,8 @@ def main(argv: list[str]) -> int:
         except Unavailable as e:
             print(f"review_packet: UNAVAILABLE: {e}", file=sys.stderr)
             return 3
-    if not re.fullmatch(r"[0-9a-f]{40}", a.head):
-        print("review_packet: --head takes a 40-hex sha", file=sys.stderr)
+    if not re.fullmatch(r"[0-9a-f]{40}", a.head) or (a.reviewed_head and not re.fullmatch(r"[0-9a-f]{40}", a.reviewed_head)):
+        print("review_packet: --head and --reviewed-head take a 40-hex sha", file=sys.stderr)
         return 2
     try:
         refusals, _, text = build(gather(a))

## Before you return the verdict (P275)
Run `python3 -I tools/audit/carry_audit.py check --body <PR body file> --comments <file holding [{"id": 0, "body": <verdict.md text>}]>`. Give every reported item its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>`;
an evidence line flagged by its wording takes `Carry: dismissed: evidence, not a finding`. Return the verdict only at rc 0.
