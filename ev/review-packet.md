# Review packet #2962
head: 34ce6c99b6bf5dd7f64f6b1d78a6eb6a53460d7e
base: ce5940c0d1d8f611a818d53e7fffcafb48b356c1

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: red
CodeQL id=123650214711 neutral
arch-score / arch-score id=123649821791 success
arm id=123649553820 skipped
budget-raise-gate / budget-raise-gate id=123649822018 success
cancel-superseded id=123649573234 success
codeql / Analyze (actions) id=123649821902 success
codeql / Analyze (javascript-typescript) id=123649821700 success
codeql / Analyze (python) id=123649821514 in_progress
governance / delivery-status id=123649821815 success
governance / delivery-status-publish id=123649824420 skipped
governance / env-matrix id=123649821676 in_progress
governance / instrument-self-tests id=123649821567 in_progress
governance / policy-docs id=123649821674 success
governance / record id=123649823695 skipped
governance / wave-script id=123649821616 success
hassfest / hassfest id=123649821487 success
kernel-points id=123649822651 skipped
prelude id=123649572544 success
refresh id=123649573496 success
tests / arch-instrument id=123650073224 success
tests / briefs id=123649821706 success
tests / browser id=123650073247 in_progress
tests / closure-scope id=123649821800 success
tests / closures id=123650073342 in_progress
tests / coverage id=123650073286 success
tests / coverage-ratchet id=123650536850 success
tests / fast (3.14) id=123650073446 in_progress
tests / graders-head-copy id=123650536906 in_progress
tests / mutation id=123649821952 success
tests / mutation-autofix id=123650272921 skipped
tests / mutation-pins id=123650272051 skipped
tests / nightly-ha id=123650077069 skipped
tests / nightly-status id=123649821624 failure
tests / replay id=123650075790 skipped
tests / typing id=123650073290 in_progress
validate / validate-hacs id=123649821599 success

## Refusals
none

## Advisories
none

## carry_audit at the head
CARRY-AUDIT: 0 finding item(s): 0 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
ok         python3 -I tools/audit/seat/review_packet.py --self-test
             `tools/audit/seat/review_packet.py` is in the tree at this head
  ok         node tools/policy/policy_lint.mjs --pr-body body.md --head <a*40> --red "tests / nightly-status" --red typing
             `tools/policy/policy_lint.mjs` is in the tree at this head
  unverified git grep -l -E -- '--red\b' -- 'tools/**' '.github/**' '.claude/**'
             `git grep` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  ok         tools/pr/prepr.sh
             `tools/pr/prepr.sh` is in the tree at this head
  ok         tools/audit/seat/body_patch.sh
             `tools/audit/seat/body_patch.sh` is in the tree at this head
  ok         tools/audit/seat/record_row.py
             `tools/audit/seat/record_row.py` is in the tree at this head
  ok         tools/ci/alert_list.py
             `tools/ci/alert_list.py` is in the tree at this head
  ok         tools/audit/seat/review_packet.py
             `tools/audit/seat/review_packet.py` is in the tree at this head
  ok         python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir $D
             `tests/closure.py` is in the tree at this head
  ok         python3 tests/structure.py
             `tests/structure.py` is in the tree at this head
  ok         bash tools/pr/prepr.sh <body>
             `tools/pr/prepr.sh` is in the tree at this head
  ok         tools/audit/seat/seat_venv.sh
             `tools/audit/seat/seat_venv.sh` is in the tree at this head

FIGURES: 11 resolved, 1 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
none

## Three-dot diff
diff --git a/dev/programme/delivery/2962.md b/dev/programme/delivery/2962.md
new file mode 100644
index 000000000..7384d702f
--- /dev/null
+++ b/dev/programme/delivery/2962.md
@@ -0,0 +1 @@
+- [#2962](https://github.com/tvofi/heatpump_optimizer/pull/2962) — **open**, review_packet: leave the seat mutant harness to #2959 (R10-FLY-PACKET-RED-PATHS)
diff --git a/tools/audit/seat/review_packet.py b/tools/audit/seat/review_packet.py
index d04fd0323..dc7b7c291 100644
--- a/tools/audit/seat/review_packet.py
+++ b/tools/audit/seat/review_packet.py
@@ -310,6 +310,27 @@ def tool(argv: list[str], body: str) -> tuple[int, str]:
         os.unlink(f.name)
 
 
+def unanswered_reds(body: str, head: str, base: str, reds: list[str],
+                    touched: set[str], existing: set[str]) -> list[str]:
+    """The concluded reds the body's `## Red checks` leaves unanswered, as
+    `policy_lint.mjs --pr-body` decides over the diff's own paths (P282). A
+    reporter that grades main is owed no answer while the diff leaves its inputs
+    alone, and policy_lint reads that from `--paths-file` and `--existing-file`:
+    without them the obligation is restored on purpose, so every pull request
+    would owe one for main's red. The exemption stays policy_lint's alone, as
+    prepr.sh's body_check keeps it."""
+    if not reds:
+        return []
+    with tempfile.TemporaryDirectory() as td:
+        pf, ef = Path(td, "paths"), Path(td, "existing")
+        pf.write_text("".join(f"{x}\n" for x in sorted(touched)))
+        ef.write_text("".join(f"{x}\n" for x in sorted(existing)))
+        _, out = tool(["node", "tools/policy/policy_lint.mjs", "--pr-body", "{BODY}", "--head", head,
+                       "--base", base, "--paths-file", str(pf), "--existing-file", str(ef),
+                       *[x for n in reds for x in ("--red", n)]], body)
+    return sorted(n for n in reds if f"check `{n}` is red and `## Red checks` does not name it" in out)
+
+
 def writes_packet(refusals: list[str]) -> bool:
     """How a render treats its own refusals: written unless it is unpublishable.
 
@@ -387,11 +408,8 @@ def gather(a) -> dict:
     gate = gate_digest(runs)
     crc, cout = tool([sys.executable, "-I", "tools/audit/carry_audit.py", "check", "--body", "{BODY}"], body)
     _, fout = tool(["node", "tools/policy/figure_lint.mjs", "--pr-body", "{BODY}", "--at", head], body)
-    red_unanswered = []
-    if gate[2]:
-        _, pout = tool(["node", "tools/policy/policy_lint.mjs", "--pr-body", "{BODY}", "--head", head,
-                        *[x for n in gate[2] for x in ("--red", n)]], body)
-        red_unanswered = sorted(n for n in gate[2] if f"check `{n}` is red and `## Red checks` does not name it" in pout)
+    existing = set(git("diff", "--name-only", "--no-renames", "--diff-filter=a", f"{base}...{head}").split())
+    red_unanswered = unanswered_reds(body, head, base, gate[2], touched, existing)
     ident = ref_privacy.Identity.of_host()
     host = [w for w in [ref_privacy.body_refusal(body, ident)] if w]
     host += ref_privacy.content_refusals(ref_privacy.added_lines(base, head, repo()), ident)
@@ -558,6 +576,22 @@ def _self_test() -> int:
     check("hot-file reader null: a verdict-ref commit subject is not a verdict",
           verdict_merge_head("d" * 40, read=lambda s: f"verdict 7 {H}\n") is None)
 
+    # red-unanswered over the diff's paths (P282), through policy_lint itself:
+    # main's `nightly-status` red is owed no answer by a diff that leaves its
+    # inputs alone, `typing` beside it is (the arm); a diff touching the
+    # reporter's own script owes both (the null control), and so does #2954's,
+    # which touched the workflow that schedules it.
+    unanswering = f"## Head\n{H}\n\n## Red checks\nnone\n"
+    both = ["tests / nightly-status", "typing"]
+    check("red-unanswered: main's nightly-status red is not owed by a diff touching only a test file",
+          unanswered_reds(unanswering, H, B, both, {"tests/x.py"}, set()) == ["typing"])
+    check("red-unanswered null: a diff touching tests/nightly_status.py owes both",
+          unanswered_reds(unanswering, H, B, both, {"tests/nightly_status.py"}, {"tests/nightly_status.py"}) == both)
+    wf = {".github/workflows/nightly.yml", ".github/workflows/governance.yml"}
+    check("red-unanswered null: #2954's workflow diff still owes nightly-status",
+          unanswered_reds(unanswering, H, B, both, wf, wf) == both)
+    check("red-unanswered null: no concluded red reads nothing", unanswered_reds(unanswering, H, B, [], {"tests/x.py"}, set()) == [])
+
     # The independence arm reads a base blob, so it is driven over a checkout of
     # its own: a self-test must not need the tree it happens to be run in.
     # Built through `tests/throwaway_git.py`, the one way a tracked script

