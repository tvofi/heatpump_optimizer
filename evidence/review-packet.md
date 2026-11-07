# Review packet #3241
head: 96987ab3d7224b04803106ae4366c5a02bb91b51
base: f2a015142714383722bf49d7ab20d8398ec9674c

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: green
CodeQL id=128284395617 success
arch-score / arch-score id=128294119254 success
arm id=128283492846 skipped
budget-raise-gate / budget-raise-gate id=128294119309 success
cancel-superseded id=128294118706 success
codeql id=128294119207 skipped
codeql / Analyze (actions) id=128286619798 success
codeql / Analyze (javascript-typescript) id=128286619894 success
codeql / Analyze (python) id=128286619845 success
gate id=128294118593 success
governance id=128294152781 skipped
governance / delivery-status id=128286620105 success
governance / delivery-status-publish id=128286621692 skipped
governance / env-matrix id=128286619856 success
governance / instrument-self-tests id=128286619890 success
governance / policy-docs id=128286619926 success
governance / record id=128286621002 skipped
governance / wave-script id=128286619846 success
hassfest id=128294119039 skipped
hassfest / hassfest id=128286619782 success
kernel-points id=128294119157 skipped
pr-contract id=128294119210 skipped
pr-contract / pr-contract id=128293626552 success
prelude id=128294146528 success
refresh id=128294119083 success
tests id=128294119089 skipped
tests / arch-instrument id=128286886340 success
tests / briefs id=128286619834 success
tests / browser id=128286886339 success
tests / ci-ratchet id=128291962357 skipped
tests / claims-autofix id=128290186414 skipped
tests / closure-scope id=128286619892 success
tests / closures id=128286886335 success
tests / closures-autofix id=128291962150 skipped
tests / coverage id=128286886319 success
tests / coverage-ratchet id=128289822223 success
tests / fast (3.14) id=128286886250 success
tests / graders-head-copy id=128289822183 success
tests / lane-proofs id=128290185194 success
tests / mutation id=128286619802 success
tests / mutation-autofix id=128286928797 skipped
tests / mutation-pins id=128286927924 skipped
tests / nightly-ha id=128286887632 skipped
tests / nightly-status id=128286619803 success
tests / replay id=128286886346 success
tests / typing id=128286886279 success
validate id=128294149969 skipped
validate / validate-hacs id=128286619808 success

## Refusals
none

## Advisories
hot-file: HPO_BUS_TRAIN_STATE is unset, so every merge verdict reads unboarded

## carry_audit at the head
NOTE stale tree: 96987ab3d7224b04803106ae4366c5a02bb91b51 lacks origin/main 355d9965a7a14ec45ef8cd25fb9c75c5ced044f1; roster read at origin/main
NOTE body item fac7779b: R10-CARRY-RESIDUE-2
CARRY-AUDIT: 1 finding item(s): 1 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
ok         python3 tools/audit/seat/r10_ledger_mutants.py --self-test
             `tools/audit/seat/r10_ledger_mutants.py` is in the tree at this head
  ok         python3 -I tests/replay.py
             `tests/replay.py` is in the tree at this head
  ok         D=$(mktemp -d); python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"
             `tests/closure.py` is in the tree at this head
  ok         tests/doc_claims.py
             `tests/doc_claims.py` is in the tree at this head
  ok         python3 tests/structure.py
             `tests/structure.py` is in the tree at this head
  unverified git diff --quiet origin/main HEAD -- tests/golden/claimed_drift.txt tests/golden/card_claimed_drift.txt
             `git diff` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  ok         bash tools/audit/seat/cloud-setup.sh --check
             `tools/audit/seat/cloud-setup.sh` is in the tree at this head

FIGURES: 6 resolved, 1 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
none

## Three-dot diff
diff --git a/dev/programme/delivery/3241.md b/dev/programme/delivery/3241.md
new file mode 100644
index 000000000..c68b42472
--- /dev/null
+++ b/dev/programme/delivery/3241.md
@@ -0,0 +1 @@
+- [#3241](https://github.com/tvofi/heatpump_optimizer/pull/3241) — **open**, R10-CARRY-RESIDUE: carry residue (R10-CARRY-RESIDUE)
diff --git a/tests/replay.py b/tests/replay.py
index c04edcf36..b597350e8 100644
--- a/tests/replay.py
+++ b/tests/replay.py
@@ -466,7 +466,12 @@ COST_DETECTION = 2.0
 #: 217.8-290.5, each edge 18-22 % inside; a loaded M1 (177-394, load average
 #: 30-200) spans more than a 2x band holds and is left out. ``peak_kib`` and
 #: ``loop_cpu_ratio`` over all four environments, the M1 included: 2514-2783
-#: and 0.137-0.227, the loop's edges 9-10 % inside.
+#: and 0.137-0.227 at that recording. The CI ``replay`` job reads the loop
+#: wider: 0.128 and 0.1339 (ref30: jobs 125240101580, 125160076828), 0.1418
+#: and 0.1433 (ref46: 125097530406, 125316010511), 0.189 (ref24: 125461180429),
+#: so under that recording's 0.249 budget its residual margin was the ref30
+#: reading, 2.8 % over the floor 0.1245, the ceiling side 24 %; round 3 below
+#: re-derives that budget.
 #: Re-centred (R10-REPLAY-COST-BUDGET) on the readings the CI ``replay`` job
 #: and nightly.yml ``slow`` take, from their own ``cost`` lines, and on
 #: nothing a reviewer's or author's box read. Owner fixture ``cpu_ratio``
diff --git a/tools/audit/seat/beat_jobs.py b/tools/audit/seat/beat_jobs.py
index 5f2f4c39f..3e4be953b 100644
--- a/tools/audit/seat/beat_jobs.py
+++ b/tools/audit/seat/beat_jobs.py
@@ -101,7 +101,7 @@ HOLD_STALE_S = 24 * 3600  # gap 6: a hold line never expired
 #: orchestrator_tick.py and ledger.py print; the self-test pins each literal there.
 FAMILY = re.compile(
     r"^(?:OWED\b|DISPATCH:|OWNER FLAG:|BLOCKED-UNFIXED:|DESIGN-BUILD:|UNREADABLE:|DESIGN OWED:"
-    r"|REVIEW OWED:|REVIEW STALLED:|UNLEVELLED:|APPROVAL-OWED:|MERGE-READY:|main-red "
+    r"|REVIEW OWED:|RECORD-OWED:|REVIEW STALLED:|UNLEVELLED:|APPROVAL-OWED:|MERGE-READY:|main-red "
     r"|main \S+: REQUIRED not green"
     r"|#\d+: (?:RAISE APPROVAL OWED|NOT REVIEWABLE|mergeable state DIRTY|RED unanswered"
     r"|code-owned with no \S+ review))")
diff --git a/tools/audit/seat/beat_jobs_selftest.py b/tools/audit/seat/beat_jobs_selftest.py
index 3fb0df7da..7487a63dc 100644
--- a/tools/audit/seat/beat_jobs_selftest.py
+++ b/tools/audit/seat/beat_jobs_selftest.py
@@ -180,7 +180,7 @@ def cases(bj) -> dict[str, bool]:
         digest(c) == (FIXTURE / "digest.txt").read_text())
     src = "".join((HERE / f).read_text() for f in ("orchestrator_tick.py", "ledger.py"))
     lits = ["OWED", "DISPATCH:", "OWNER FLAG:", "BLOCKED-UNFIXED:", "DESIGN-BUILD:", "UNREADABLE:",
-            "DESIGN OWED:", "REVIEW OWED:", "REVIEW STALLED:", "UNLEVELLED:", "APPROVAL-OWED:",
+            "DESIGN OWED:", "REVIEW OWED:", "RECORD-OWED:", "REVIEW STALLED:", "UNLEVELLED:", "APPROVAL-OWED:",
             "MERGE-READY:", "main-red ", "REQUIRED not green", "RAISE APPROVAL OWED", "NOT REVIEWABLE",
             "mergeable state DIRTY", "RED unanswered", "code-owned with no ",
             "BOARD measured from origin/main at"]
diff --git a/tools/audit/seat/ledger.py b/tools/audit/seat/ledger.py
index 89b882803..4d1d738d9 100644
--- a/tools/audit/seat/ledger.py
+++ b/tools/audit/seat/ledger.py
@@ -105,7 +105,7 @@ ROOT = Path(__file__).resolve().parents[3]
 KINDS = {
     "handoff-no-pr": "derived", "handoff-update": "derived", "probe-ref": "derived",
     "handoff-hold-malformed": "derived", "handoff-held": "derived", "handoff-body-stale": "derived",
-    "design-build": "derived", "review-owed": "derived",
+    "design-build": "derived", "review-owed": "derived", "record-owed": "derived",
     "probe-refused": "derived", "confirm-owed": "derived", "push-stuck": "derived",
     "seat-no-return": "derived",
     "fixer-round": "derived", "recut": "derived", "train-parked": "derived", "dirty": "derived",
@@ -635,12 +635,21 @@ def design_builds(verdicts: dict, designs: dict, stage_of, disp: dict) -> list[s
     return out
 
 
-def review_owed(prs: list, readback: dict, dispatched: set, carries=None, skip_branch=None) -> list[str]:
+def review_owed(prs: list, readback: dict, dispatched: set, carries=None, skip_branch=None,
+                recarry=None) -> list[str]:
     """`REVIEW OWED: #N <head12>` per open non-draft PR whose comments were
     read, no verdict names its head, no dispatch record is at that head, and
     -- with `carries(verdict_head, head)` -- the newest verdict is not a merge
     that carries to the head (the train's predicate, app_approve_carries). A PR whose
-    `headRefName` is `skip_branch` (the record branch, passed in) is never owed one."""
+    `headRefName` is `skip_branch` (the record branch, passed in) is never owed one.
+    With `recarry(prior, head, n)` (git_recarry): a head that differs from a
+    head of a `merge` verdict, or a dispatched head, of the PR only by clean
+    merges of main, or only by the PR's own delivery row, prints
+    `CARRY: #N <head12>` instead (P90; the ancestor-recarry test of
+    standing-tick.md). A head is a prior only while its newest verdict is a
+    merge, or it is dispatched with no verdict yet: a blocked verdict's head is
+    no prior, though bus.sh's dispatch record holds it too (only a merge
+    verdict carries; fix-review.md step 12)."""
     out = []
     for pr in sorted(prs, key=lambda p: p["number"]):
         n, head = pr["number"], pr.get("headRefOid") or ""
@@ -653,10 +662,76 @@ def review_owed(prs: list, readback: dict, dispatched: set, carries=None, skip_b
         last = lines[-1] if lines else ""
         if carries and last.startswith("Fix review: merge ") and carries(verdict_head(last), head):
             continue
+        newest = {h: l for l in lines if (h := verdict_head(l))}  # the newest verdict at each head
+        priors = [h for h, l in newest.items() if l.startswith("Fix review: merge ")] \
+            + sorted(h for k, h in dispatched if k == str(n) and h not in newest)
+        if recarry and any(recarry(h, head, n) for h in dict.fromkeys(priors)):
+            out.append(f"CARRY: #{n} {head[:12]}")
+            continue
         out.append(f"REVIEW OWED: #{n} {head[:12]}")
     return out
 
 
+def git_recarry(cwd: str, main: str, env=None):
+    """recarry(prior, head, n) -> True when every first-parent commit of
+    prior..head is a merge with no conflict-resolution edit whose second parent
+    is in `main`, or a commit touching only `dev/programme/delivery/<n>.md`, and
+    `prior` is an ancestor of `head`. Any git failure is False, so the PR stays owed."""
+    def g(*a):
+        r = subprocess.run(["git", "-C", cwd, *a], env=env, capture_output=True, text=True)
+        return r.stdout if r.returncode == 0 else None
+
+    def recarry(prior: str, head: str, n) -> bool:
+        if not (is_sha(prior) and is_sha(head)) or prior == head:
+            return False
+        if subprocess.run(["git", "-C", cwd, "merge-base", "--is-ancestor", prior, head],
+                          env=env, capture_output=True).returncode != 0:
+            return False
+        revs = g("rev-list", "--first-parent", f"{prior}..{head}")
+        if not revs or not revs.split():
+            return False
+        for c in revs.split():
+            parents = (g("rev-list", "--parents", "-n1", c) or "").split()[1:]
+            if len(parents) > 1:
+                resolved = g("diff-tree", "--cc", "-r", "--no-commit-id", c)
+                if resolved is None or resolved.strip() or any(
+                        subprocess.run(["git", "-C", cwd, "merge-base", "--is-ancestor", p, main],
+                                       env=env, capture_output=True).returncode != 0 for p in parents[1:]):
+                    return False
+            else:
+                files = g("diff-tree", "--no-commit-id", "--name-only", "-r", c)
+                if files is None or set(files.split()) != {f"dev/programme/delivery/{n}.md"}:
+                    return False
+        return True
+    return recarry
+
+
+RECORD_OWED_MINUTES = 30
+
+
+def record_owed(prs: list, now: datetime.datetime, record_prefix: str = "record/",
+                minutes: int = RECORD_OWED_MINUTES) -> list[str]:
+    """`RECORD-OWED: #N <head12> <age>m` per open non-draft PR on a `record/`
+    branch (the record and autofix pull requests) that is APPROVED and has been
+    open `minutes` or more (P33). Keyed PR and head by the line, closed by the PR's
+    merge or close, because the open-PR list the tick already fetched no longer
+    holds it."""
+    out = []
+    for pr in sorted(prs, key=lambda p: p["number"]):
+        head = pr.get("headRefOid") or ""
+        if pr.get("isDraft") or not head or not (pr.get("headRefName") or "").startswith(record_prefix) \
+                or (pr.get("reviewDecision") or "").upper() != "APPROVED":
+            continue
+        try:
+            made = datetime.datetime.fromisoformat((pr.get("createdAt") or "").replace("Z", "+00:00"))
+        except ValueError:
+            continue
+        age = (now - made).total_seconds() / 60
+        if age >= minutes:
+            out.append(f"RECORD-OWED: #{pr['number']} {head[:12]} {int(age)}m")
+    return out
+
+
 def app_approve_carries(cwd: str, main: str, env=None):
     """carries(verdict, head) through `tools/pr/app_approve.sh --carry`, run in `cwd` against
     `main`: True only on its rc 0, so a carry it cannot decide stays owed."""
@@ -962,6 +1037,86 @@ def self_test() -> int:
         rb["5"].append(f"Fix review: blocked {vh} harness: y")
         check("a newest verdict that is blocked carries nothing", [l.split()[2] for l in
               review_owed(crs, rb, set(), carrier)] == ["#5", "#6"])
+        # ---- CARRY (P90): the head moved past its verdict by a main merge, or by its own row only
+        cg("checkout", "-q", "main")
+        mh = cput("main2.txt", "main moves again")
+        cg("checkout", "-q", "fix")
+        cg("reset", "-q", "--hard", vh)
+        cg("merge", "-q", "--no-edit", "main")
+        merged_head = cg("rev-parse", "HEAD")
+        (cw / "dev/programme/delivery").mkdir(parents=True, exist_ok=True)
+        row_head = cput("dev/programme/delivery/7.md", "its own row")
+        both_head = cput("other.txt", "row plus another file")
+        recarry = git_recarry(str(cw), "main", throwaway_git_env())
+        rb2 = {"7": [f"Fix review: merge {vh}"]}
+        pr7 = lambda h: [{"number": 7, "headRefOid": h}]
+        check("a head that is a verdicted head plus one main merge prints CARRY",
+              review_owed(pr7(merged_head), rb2, set(), None, None, recarry) == [f"CARRY: #7 {merged_head[:12]}"])
+        check("null control: the same head without the recarry test is REVIEW OWED",
+              review_owed(pr7(merged_head), rb2, set()) == [f"REVIEW OWED: #7 {merged_head[:12]}"])
+        check("a head plus only its own delivery row prints CARRY",
+              review_owed(pr7(row_head), rb2, set(), None, None, recarry) == [f"CARRY: #7 {row_head[:12]}"])
+        check("a head plus its row and another file prints REVIEW OWED (null)",
+              review_owed(pr7(both_head), rb2, set(), None, None, recarry) == [f"REVIEW OWED: #7 {both_head[:12]}"])
+        check("a code commit on top of a main merge prints REVIEW OWED (null)",
+              review_owed(pr7(own_head), {"7": [f"Fix review: merge {carried_head}"]}, set(), None, None, recarry)
+              == [f"REVIEW OWED: #7 {own_head[:12]}"])
+        cg("checkout", "-q", "-b", "side", vh)
+        sib = cput("sib.txt", "a sibling the head never contained")
+        cg("checkout", "-q", "fix")
+        check("null control: a prior that is no ancestor of the head carries nothing",
+              review_owed(pr7(row_head), {"7": [f"Fix review: merge {sib}"]}, set(), None, None, recarry)
+              == [f"REVIEW OWED: #7 {row_head[:12]}"])
+        check("a dispatched head is a prior too",
+              review_owed(pr7(merged_head), {"7": []}, {("7", vh)}, None, None, recarry) == [f"CARRY: #7 {merged_head[:12]}"])
+        check("null control: a blocked verdict's head is no prior, whatever its class",
+              [review_owed(pr7(merged_head), {"7": [f"Fix review: blocked {vh} {why}"]}, set(), None, None, recarry)
+               for why in ("mutation-vacuous: x", "root-cause-unanswered: y")]
+              == [[f"REVIEW OWED: #7 {merged_head[:12]}"]] * 2)
+        # bus.sh records every dispatch and refuses a verdict with none at its head,
+        # so a blocked verdict's head is always in the dispatch record too
+        check("a blocked verdict's head in the dispatch record is no prior",
+              [review_owed(pr7(merged_head), {"7": rb}, {("7", vh)}, None, None, recarry)
+               for rb in ([f"Fix review: blocked {vh} root-cause-unanswered: y"],
+                          [f"Fix review: merge {vh}", f"Fix review: blocked {vh} mutation-vacuous: x"])]
+              == [[f"REVIEW OWED: #7 {merged_head[:12]}"]] * 2)
+        check("null control: a dispatched head whose newest verdict is a merge still carries",
+              [review_owed(pr7(merged_head), {"7": rb}, {("7", vh)}, None, None, recarry)
+               for rb in ([f"Fix review: merge {vh}"],
+                          [f"Fix review: blocked {vh} mutation-vacuous: x", f"Fix review: merge {vh}"])]
+              == [[f"CARRY: #7 {merged_head[:12]}"]] * 2)
+        # a merge of main whose conflict was resolved by hand carries an edit no review saw
+        cg("checkout", "-q", "-b", "conf", vh)
+        cvh = cput("conflict.txt", "the branch's side")
+        cg("checkout", "-q", "main")
+        cput("conflict.txt", "main's side")
+        cg("checkout", "-q", "conf")
+        cg("merge", "-q", "--no-edit", "main")
+        conf_head = cput("conflict.txt", "a hand resolution neither side wrote")
+        check("a main merge with a hand-resolved conflict prints REVIEW OWED",
+              len(cg("rev-list", "--parents", "-n1", conf_head).split()) == 3
+              and review_owed(pr7(conf_head), {"7": [f"Fix review: merge {cvh}"]}, set(), None, None, recarry)
+              == [f"REVIEW OWED: #7 {conf_head[:12]}"])
+        # a clean merge of a branch that is not main brings code no review saw
+        cg("checkout", "-q", "-b", "topic", vh)
+        cput("topic.txt", "a side branch main never took")
+        cg("checkout", "-q", "-b", "fix3", vh)
+        cg("merge", "-q", "--no-ff", "--no-edit", "topic")
+        side_head = cg("rev-parse", "HEAD")
+        check("a clean merge of a side branch prints REVIEW OWED",
+              len(cg("rev-list", "--parents", "-n1", side_head).split()) == 3
+              and review_owed(pr7(side_head), rb2, set(), None, None, recarry) == [f"REVIEW OWED: #7 {side_head[:12]}"])
+        # ---- RECORD-OWED (P33): an approved record PR open 30 minutes
+        t0 = datetime.datetime(2026, 1, 1, 12, 0, tzinfo=datetime.timezone.utc)
+        mk = lambda n, mins, **kw: {"number": n, "headRefOid": A, "headRefName": "record/autofix",
+                                    "reviewDecision": "APPROVED",
+                                    "createdAt": (t0 - datetime.timedelta(minutes=mins)).isoformat(), **kw}
+        ro_ = record_owed([mk(1, 31), mk(2, 29), mk(3, 31, reviewDecision="REVIEW_REQUIRED"),
+                           mk(4, 31, headRefName="fix/x"), mk(5, 31, isDraft=True), mk(6, 30)], t0)
+        check("an approved record PR open 31 or exactly 30 minutes opens an entry; 29, unapproved, off-branch "
+              "and draft do not", ro_ == [f"RECORD-OWED: #1 {A[:12]} 31m", f"RECORD-OWED: #6 {A[:12]} 30m"])
+        check("a merged or closed record PR is absent from the open list, so it closes the entry",
+              record_owed([mk(2, 29)], t0) == [] and record_owed([], t0) == [])
         # ---- covered, the level, the exit codes, over a throwaway origin
         env = throwaway_git_env()
         o, w = D / "o.git", D / "w"
diff --git a/tools/audit/seat/orchestrator_tick.py b/tools/audit/seat/orchestrator_tick.py
index 2247e7a28..23a44e40f 100644
--- a/tools/audit/seat/orchestrator_tick.py
+++ b/tools/audit/seat/orchestrator_tick.py
@@ -754,7 +754,11 @@ class Tick:
         elif dispatched is not None:
             rr = _module("record_row_tick", "tools/audit/seat/record_row.py")
             for text in lg.review_owed(prs, self._readback, dispatched, self._carries,
-                                       getattr(rr, "RECORD_BRANCH", None)):
+                                       getattr(rr, "RECORD_BRANCH", None),
+                                       lg.git_recarry(self.checkout or ".", "origin/main")):
+                self.line(S, text, flag=not text.startswith("CARRY:"))
+            now = getattr(self, "now", None) or datetime.datetime.now(datetime.timezone.utc)
+            for text in lg.record_owed(prs, now):
                 self.line(S, text, flag=True)
 
     # ------------------------------------------------------- OWED buckets
@@ -4652,6 +4656,56 @@ def self_test() -> int:
         ])
         total, failed = total + a, failed + f
 
+        # ---- CARRY and RECORD-OWED through the tick's own call (R10-CARRY-RESIDUE): a real
+        # checkout whose origin/main the tick's git_recarry reads. #80's head is its merge verdict's
+        # head plus one clean main merge; #81 is an approved record PR open 40 minutes.
+        tgc = _module("throwaway_git_carry", "tests/throwaway_git.py")
+        with tempfile.TemporaryDirectory() as d:
+            env = tgc.throwaway_git_init(d, "-q", "-b", "main")
+
+            def cgit(*argv):
+                return subprocess.run(["git", *argv], cwd=d, env=env, capture_output=True, text=True).stdout.strip()
+
+            def cput(name: str, msg: str) -> str:
+                (Path(d) / name).write_text(msg + "\n")
+                cgit("add", "-A")
+                cgit("commit", "-qm", msg)
+                return cgit("rev-parse", "HEAD")
+
+            cput("base.txt", "base")
+            cgit("checkout", "-qb", "fix")
+            cvh = cput("fix.txt", "the reviewed fix")
+            cgit("checkout", "-q", "main")
+            cput("main.txt", "main moves on")
+            cgit("checkout", "-q", "fix")
+            cgit("merge", "-q", "--no-edit", "main")
+            cmh = cgit("rev-parse", "HEAD")
+            cgit("update-ref", "refs/remotes/origin/main", "main")
+            ca_board = [pr_obj(80, cmh), dict(pr_obj(81, h(81), branch="record/autofix", rd="APPROVED"),
+                                               createdAt=iso(NOW - datetime.timedelta(minutes=40)))]
+
+            def ca_run(verdict: str) -> list:
+                extra = [(("issues/80/comments?per_page=100",), 0, json.dumps([[vc(22, verdict)]])),
+                         (("issues/81/comments?per_page=100",), 0, json.dumps([[]]))]
+                t_ca = tick(prs=ca_board, gh_extra=extra, bus_state=str(tmp / "bus-ro"), checkout=d)
+                t_ca._git.on(("ls-remote",), out="")
+                t_ca._carries = lambda v, hd: False  # the train's predicate stays out: this row is git_recarry's
+                t_ca.verdict_levels("PRS", ca_board)
+                return t_ca.sections.get("PRS", [])
+
+            ca, cb = ca_run(f"Fix review: merge {cvh}"), ca_run(f"Fix review: blocked {cvh} mutation-vacuous: x")
+        a, f = check("CARRY and RECORD-OWED", [
+            ("a verdicted head plus one main merge prints CARRY, unflagged, and no REVIEW OWED",
+             {"flag": False, "text": f"CARRY: #80 {cmh[:12]}"} in ca
+             and not any(x["text"].startswith("REVIEW OWED: #80") for x in ca)),
+            ("null control: the same head after a blocked verdict is REVIEW OWED, flagged, and no CARRY",
+             {"flag": True, "text": f"REVIEW OWED: #80 {cmh[:12]}"} in cb
+             and not any(x["text"].startswith("CARRY") for x in cb)),
+            ("an approved record PR open 40 minutes prints RECORD-OWED, flagged",
+             {"flag": True, "text": f"RECORD-OWED: #81 {h(81)[:12]} 40m"} in ca),
+        ])
+        total, failed = total + a, failed + f
+
         # ---- DESIGN-BUILD (the RCA's section 5.5) ----
         A40, B40 = "a" * 40, "b" * 40
         rlm = _module("roster_lib_db", "tools/audit/seat/roster_lib.py")
diff --git a/tools/audit/seat/owed_unactioned.py b/tools/audit/seat/owed_unactioned.py
index fe62eb6eb..91214d175 100644
--- a/tools/audit/seat/owed_unactioned.py
+++ b/tools/audit/seat/owed_unactioned.py
@@ -16,7 +16,7 @@ two handoffs routed to the opener at 10:55Z stood 8 h.
 
 WHAT IT DOES. It reads the tick board's owed family -- every `-> ` line that
 starts `OWED`, `REVIEW OWED:`, `DISPATCH:`, `OWNER FLAG:`, `DESIGN-BUILD:`,
-`MERGE-READY:`, `BLOCKED-UNFIXED:`, `APPROVAL-OWED:`, `UNLEVELLED:` or `REVIEW STALLED:` -- and keys each on its obligation: the
+`MERGE-READY:`, `BLOCKED-UNFIXED:`, `APPROVAL-OWED:`, `UNLEVELLED:`, `REVIEW STALLED:` or `RECORD-OWED:` -- and keys each on its obligation: the
 handoff topic, or `#<pr>`. A verdict level (`MERGE-READY: #N <head8>`) carries
 its head8 as the id, so an acknowledgement covers one head and a new head
 re-raises. `APPROVAL-OWED:` means queue the PR for the train, which posts the
@@ -53,7 +53,7 @@ import re
 import sys
 import tempfile
 
-FAMILY = re.compile(r"^-> (OWED|REVIEW OWED:|DISPATCH:|OWNER FLAG:|DESIGN-BUILD:|MERGE-READY:|BLOCKED-UNFIXED:|APPROVAL-OWED:|UNLEVELLED:|REVIEW STALLED:)")
+FAMILY = re.compile(r"^-> (OWED|REVIEW OWED:|RECORD-OWED:|DISPATCH:|OWNER FLAG:|DESIGN-BUILD:|MERGE-READY:|BLOCKED-UNFIXED:|APPROVAL-OWED:|UNLEVELLED:|REVIEW STALLED:)")
 BOARD = re.compile(r"^BOARD measured from origin/main at \S+, (\S+)")
 SHA = re.compile(r"\b[0-9a-f]{12,40}\b")
 REF = re.compile(r"\b(?:refs/heads/)?(?:handoff-body|handoff|design)/(\S+)")
@@ -87,6 +87,9 @@ def key_of(line: str) -> "tuple[str, list[str]]":
     if m:
         return m.group(1), [m.group(2)]
     m = re.match(r"REVIEW STALLED: (#\d+) ([0-9a-f]{8}) \d+m$", body)  # the minutes grow each sweep: not in the key
+    if m:
+        return m.group(1), [m.group(2)]
+    m = re.match(r"RECORD-OWED: (#\d+) ([0-9a-f]{12}) \d+m$", body)  # the minutes grow, as above
     if m:
         return m.group(1), [m.group(2)]
     m = re.match(r"UNLEVELLED: (#\d+) ([0-9a-f]{8}) \S+$", body)
@@ -384,6 +387,13 @@ def self_test() -> int:
             rcn, on = go(tick(v0 + dt.timedelta(minutes=30), moved), lack, state=st)
             check(f"{name}: a new head8 re-raises", rcn == 1 and f"{key}  sweeps=4" in on
                   and f" {key} 9e8d7c6b ttl=1" in on)
+        # RECORD-OWED keys #<N> on its head12; its minutes grow each sweep and are not in the key
+        rw = "-> RECORD-OWED: #3235 5d4c3b2a1f0e 41m"
+        w0 = t0 + dt.timedelta(hours=6)
+        go(tick(w0, rw), state="lv-record.json")
+        rcw, ow = go(tick(w0 + dt.timedelta(minutes=10), rw.replace("41m", "51m")), state="lv-record.json")
+        check("RECORD-OWED: keyed #3235 on its head12, unactioned on the second sweep as its minutes grow",
+              rcw == 1 and "#3235  sweeps=2" in ow and " #3235 5d4c3b2a1f0e ttl=1" in ow)
         _, kv = board(tick(t0, review, mr))
         check("REVIEW OWED and MERGE-READY on one pull request are one key",
               set(kv) == {"#2896"} and kv["#2896"]["shas"] == ["5f3a5dd615b5", "5f3a5dd6"])
diff --git a/tools/audit/seat/r10_ledger_mutants.py b/tools/audit/seat/r10_ledger_mutants.py
index c56f1b351..9c6f01a63 100644
--- a/tools/audit/seat/r10_ledger_mutants.py
+++ b/tools/audit/seat/r10_ledger_mutants.py
@@ -5,7 +5,8 @@ Metric, one line per plant: `RESULT mutant=<name> rc=<rc> fails=<n>`, then the
 failing check names. Each plant is one exact one-occurrence replacement in one
 of the files the ledger change touched; the driver applies it, runs that
 file's owner's self-test (ledger.py for the ledger and open_pr.sh's attempt
-lines, cloud_relay.sh, orchestrator_tick.py), and restores the file byte for
+lines, cloud_relay.sh, bus.sh, orchestrator_tick.py, beat_jobs.py,
+owed_unactioned.py), and restores the file byte for
 byte. It refuses to start when a target differs from HEAD, so a restore cannot
 overwrite work. Expected: every plant rc=1 with fails>=1 -- a FAIL line, not a
 crash (a crash is rc=1 with fails=0 and prints its tail). Each plant mutates
@@ -15,7 +16,7 @@ a predicate, never a tail.
     python3 tools/audit/seat/r10_ledger_mutants.py --null
     python3 tools/audit/seat/r10_ledger_mutants.py --self-test
 
-Null control: `--null` runs the three self-tests with no plant, which must
+Null control: `--null` runs every owner's self-test with no plant, which must
 print rc=0 fails=0 each. `--self-test` runs no plant and pins the sweep's
 preconditions: every anchor occurs exactly once, every plant changes its text,
 and every Python mutant parses.
@@ -29,7 +30,8 @@ ROOT = Path(__file__).resolve().parents[3]
 BUS = "tools/audit/seat/bus.sh"
 LEDGER, RELAY, TICK, OPENER = ("tools/audit/seat/ledger.py", "tools/audit/seat/cloud_relay.sh",
                                "tools/audit/seat/orchestrator_tick.py", "tools/audit/seat/open_pr.sh")
-OWNER = {LEDGER: LEDGER, OPENER: LEDGER, RELAY: RELAY, TICK: TICK, BUS: BUS}
+BEAT, OWED_U = "tools/audit/seat/beat_jobs.py", "tools/audit/seat/owed_unactioned.py"
+OWNER = {LEDGER: LEDGER, OPENER: LEDGER, RELAY: RELAY, TICK: TICK, BUS: BUS, BEAT: BEAT, OWED_U: OWED_U}
 PLANTS = {
     # the ledger: event closers, the level's closers, aging, refusals, stores
     "L1_readback_no_close": (LEDGER, '                how = "read-back"', "                how = None"),
@@ -93,8 +95,9 @@ PLANTS = {
     # the tick reads the ledger
     "T1_unkinded_printed": (TICK, "            if len(f) > 2 and f[2] in lg.KINDS:", "            if True:"),
     "T2_no_reads_fold": (TICK, 'lg.fold(rows, getattr(self, "_live", None), getattr(self, "_readback", None))', "lg.fold(rows)"),
-    "T3_review_owed_silent": (TICK, '                                       getattr(rr, "RECORD_BRANCH", None)):\n                self.line(S, text, flag=True)',
-                              '                                       getattr(rr, "RECORD_BRANCH", None)):\n                pass'),
+    "T3_review_owed_silent": (TICK, '''lg.git_recarry(self.checkout or ".", "origin/main")):
+                self.line(S, text, flag=not text.startswith("CARRY:"))''',
+                              'lg.git_recarry(self.checkout or ".", "origin/main")):\n                pass'),
     "T4_no_escalation": (TICK, "                                aging, group_of, last_open):\n            self.line(S, text, flag=True)",
                          "                                aging, group_of, last_open):\n            pass"),
     "T5_no_design_build": (TICK, "        self.design_builds(S, rl, roster)\n", ""),
@@ -102,6 +105,28 @@ PLANTS = {
                              "            return\n        if not rows"),
     "T7_readback_uncollected": (TICK, '            self._readback[str(n)] = [(c.get("body") or "").split("\\n", 1)[0].rstrip("\\r") for c in vs]',
                                 "            pass"),
+    # R10-CARRY-RESIDUE: the CARRY arm, RECORD-OWED, and the family readers of RECORD-OWED
+    "C1_recarry_conflict_unchecked": (LEDGER, "if resolved is None or resolved.strip() or any(",
+                                      "if resolved is None or any("),
+    "C2_recarry_side_merge": (LEDGER, "if resolved is None or resolved.strip() or any(",
+                              "if resolved is None or resolved.strip() or False and any("),
+    "C3_record_owed_strict": (LEDGER, "        if age >= minutes:", "        if age > minutes:"),
+    "C4_tick_no_recarry": (TICK, ',\n                                       lg.git_recarry(self.checkout or ".", "origin/main")', ""),
+    "C5_tick_carry_flagged": (TICK, 'flag=not text.startswith("CARRY:")', "flag=True"),
+    "C6_tick_no_record_owed": (TICK, "for text in lg.record_owed(prs, now):", "for text in []:"),
+    "C7_beat_family_no_record": (BEAT, "|RECORD-OWED:|", "|"),
+    "C8_owed_family_no_record": (OWED_U, "|RECORD-OWED:|", "|"),
+    "C9_blocked_prior_carries": (LEDGER, 'for h, l in newest.items() if l.startswith("Fix review: merge ")]', "for h, l in newest.items()]"),
+    "C10_record_owed_unkeyed": (OWED_U, '    m = re.match(r"RECORD-OWED: (#\\d+) ([0-9a-f]{12}) \\d+m$", body)',
+                                '    m = None'),
+    "C11_recarry_no_ancestor": (LEDGER, '        if subprocess.run(["git", "-C", cwd, "merge-base", "--is-ancestor", prior, head],',
+                                '        if False and subprocess.run(["git", "-C", cwd, "merge-base", "--is-ancestor", prior, head],'),
+    "C12_recarry_any_commit": (LEDGER, 'if files is None or set(files.split()) != {f"dev/programme/delivery/{n}.md"}:',
+                               "if files is None:"),
+    "C13_record_owed_unapproved": (LEDGER, '                or (pr.get("reviewDecision") or "").upper() != "APPROVED":',
+                                   "                or False:"),
+    "C14_dispatched_not_prior": (LEDGER, " \\\n            + sorted(h for k, h in dispatched if k == str(n) and h not in newest)", ""),
+    "C15_blocked_dispatched_prior": (LEDGER, "if k == str(n) and h not in newest)", "if k == str(n))"),
 }
 
 

## Before you return the verdict (P275)
Run `python3 -I tools/audit/carry_audit.py check --body <PR body file> --comments <file holding [{"id": 0, "body": <verdict.md text>}]>`. Give every reported item its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>`;
an evidence line flagged by its wording takes `Carry: dismissed: evidence, not a finding`. Return the verdict only at rc 0.
