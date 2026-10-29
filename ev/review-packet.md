# Review packet #2962
head: 9ce0179f77aa68eab6440c3d85aa92e788936b22
base: ce5940c0d1d8f611a818d53e7fffcafb48b356c1

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: red
arch-score / arch-score id=123687978702 success
budget-raise-gate / budget-raise-gate id=123687995594 success
cancel-superseded id=123688001428 success
codeql id=123687923737 skipped
codeql / Analyze (actions) id=123687963558 success
codeql / Analyze (javascript-typescript) id=123687982835 success
codeql / Analyze (python) id=123687956125 success
gate id=123688862176 queued
governance id=123687920535 skipped
governance / delivery-status id=123687981580 success
governance / delivery-status-publish id=123687960526 skipped
governance / env-matrix id=123687908938 success
governance / instrument-self-tests id=123687953838 success
governance / policy-docs id=123687987765 success
governance / record id=123687909054 skipped
governance / wave-script id=123687976731 success
hassfest id=123687989467 skipped
hassfest / hassfest id=123687987675 success
kernel-points id=123687977428 skipped
pr-contract / pr-contract id=123688500186 success
prelude id=123687979498 success
refresh id=123687952508 success
tests id=123687920966 skipped
tests / arch-instrument id=123687910067 success
tests / briefs id=123687908633 success
tests / browser id=123687910712 success
tests / ci-ratchet id=123687911707 skipped
tests / claims-autofix id=123687910689 skipped
tests / closure-scope id=123687964576 success
tests / closures id=123687910721 success
tests / closures-autofix id=123687911912 skipped
tests / coverage id=123687910046 success
tests / coverage-ratchet id=123687911893 success
tests / fast (3.14) id=123687910019 success
tests / graders-head-copy id=123687911237 success
tests / lane-proofs id=123687911992 success
tests / mutation id=123687985891 success
tests / mutation-autofix id=123687910344 skipped
tests / mutation-pins id=123687909917 skipped
tests / nightly-ha id=123687910485 skipped
tests / nightly-status id=123687907789 failure
tests / replay id=123687910771 skipped
tests / typing id=123687910397 success
validate id=123688001399 skipped
validate / validate-hacs id=123687955140 success

## Refusals
none

## Advisories
none

## carry_audit at the head
NOTE stale tree: 9ce0179f77aa68eab6440c3d85aa92e788936b22 lacks origin/main e5ddba1fad5e6eccfeceaeaaa249bc459963405b; roster read at origin/main
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
index d04fd0323..cabeea067 100644
--- a/tools/audit/seat/review_packet.py
+++ b/tools/audit/seat/review_packet.py
@@ -310,6 +310,41 @@ def tool(argv: list[str], body: str) -> tuple[int, str]:
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
+        rc, out = tool(["node", "tools/policy/policy_lint.mjs", "--pr-body", "{BODY}", "--head", head,
+                        "--base", base, "--paths-file", str(pf), "--existing-file", str(ef),
+                        *[x for n in reds for x in ("--red", n)]], body)
+    # A path list policy_lint refuses is not "no unanswered red": the run
+    # stopped before any rule read the body, so the outcome is unknown.
+    if rc and re.search(r"ERROR +\[pr-body\] --(?:paths|existing)-file ", out):
+        raise Unavailable(f"policy_lint refused the diff's path lists: {out[:200]}")
+    return sorted(n for n in reds if f"check `{n}` is red and `## Red checks` does not name it" in out)
+
+
+def diff_paths(base: str, head: str) -> tuple[set[str], set[str]]:
+    """(touched, existing): the three-dot diff's paths, and those of them the
+    base already had (`--diff-filter=a`), which `unanswered_reds` hands
+    policy_lint as `--existing-file`, so a delivery row the diff adds is read as
+    the pull request's own and not as an input of main's reporter."""
+    span = f"{base}...{head}"
+    return (set(git("diff", "--name-only", "--no-renames", span).split()),
+            set(git("diff", "--name-only", "--no-renames", "--diff-filter=a", span).split()))
+
+
 def writes_packet(refusals: list[str]) -> bool:
     """How a render treats its own refusals: written unless it is unpublishable.
 
@@ -377,7 +412,7 @@ def build(facts: dict) -> tuple[list[str], list[str], str]:
 def gather(a) -> dict:
     head, main = a.head, a.main
     base = git("merge-base", main, head).strip()
-    touched = set(git("diff", "--name-only", "--no-renames", f"{base}...{head}").split())
+    touched, existing = diff_paths(base, head)
     label, data = (harness_source(a.harness, a.harness_file, base, touched)
                    if (a.harness or a.harness_file) else ("none named", b""))
     pr = gh(f"repos/{REPO}/pulls/{a.pr}") or {}
@@ -387,11 +422,7 @@ def gather(a) -> dict:
     gate = gate_digest(runs)
     crc, cout = tool([sys.executable, "-I", "tools/audit/carry_audit.py", "check", "--body", "{BODY}"], body)
     _, fout = tool(["node", "tools/policy/figure_lint.mjs", "--pr-body", "{BODY}", "--at", head], body)
-    red_unanswered = []
-    if gate[2]:
-        _, pout = tool(["node", "tools/policy/policy_lint.mjs", "--pr-body", "{BODY}", "--head", head,
-                        *[x for n in gate[2] for x in ("--red", n)]], body)
-        red_unanswered = sorted(n for n in gate[2] if f"check `{n}` is red and `## Red checks` does not name it" in pout)
+    red_unanswered = unanswered_reds(body, head, base, gate[2], touched, existing)
     ident = ref_privacy.Identity.of_host()
     host = [w for w in [ref_privacy.body_refusal(body, ident)] if w]
     host += ref_privacy.content_refusals(ref_privacy.added_lines(base, head, repo()), ident)
@@ -558,6 +589,35 @@ def _self_test() -> int:
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
+    # main's other reporter: every pull request adds its own delivery row, which
+    # `--existing-file` keeps from reading as an input of `delivery-status`.
+    ds, row = ["governance / delivery-status"], "dev/programme/delivery/9999.md"
+    check("red-unanswered: main's delivery-status red is not owed by a diff adding only its own delivery row",
+          unanswered_reds(unanswering, H, B, ds, {row}, set()) == [])
+    check("red-unanswered null: a delivery row the base already had owes delivery-status",
+          unanswered_reds(unanswering, H, B, ds, {row}, {row}) == ds)
+    try:
+        unanswered_reds(unanswering, H, B, both, set(), set())
+        ok = False
+    except Unavailable:
+        ok = True
+    check("red-unanswered: a path list policy_lint refuses is UNAVAILABLE, not no unanswered red", ok)
+
     # The independence arm reads a base blob, so it is driven over a checkout of
     # its own: a self-test must not need the tree it happens to be run in.
     # Built through `tests/throwaway_git.py`, the one way a tracked script
@@ -640,6 +700,31 @@ def _self_test() -> int:
         check("repo(): a git read runs in the checkout the working directory is in, not the tool's install",
               Path(got) == t)
 
+        # gather's path lists, over a real three-dot diff: the delivery row the
+        # head adds is touched and not existing, so main's delivery-status red
+        # is owed no answer through the same call gather makes.
+        (t / "kept.txt").write_text("base\n")
+        tgit("add", "-A")
+        tgit("commit", "-q", "-m", "kept")
+        pbase = tgit("rev-parse", "HEAD").strip()
+        (t / "kept.txt").write_text("head\n")
+        (t / "dev/programme/delivery").mkdir(parents=True)
+        (t / row).write_text("row\n")
+        tgit("add", "-A")
+        tgit("commit", "-q", "-m", "head")
+        phead = tgit("rev-parse", "HEAD").strip()
+        here, _REPO_ROOT = os.getcwd(), None
+        try:
+            os.chdir(t)
+            paths = diff_paths(pbase, phead)
+        finally:
+            os.chdir(here)
+            _REPO_ROOT = None
+        check("diff_paths: an added delivery row is touched, and only a file the base had is existing",
+              paths == ({"kept.txt", row}, {"kept.txt"}))
+        check("diff_paths -> red-unanswered: the row the diff adds owes main's delivery-status nothing",
+              unanswered_reds(unanswering, H, B, ds, *paths) == [])
+
         # UNAVAILABLE is a different outcome from a refusal: a seat that cannot
         # read the inputs reports rc 3 and writes nothing, and `bus.sh dispatch`
         # degrades on it. Driven through main(), the path bus.sh calls.

