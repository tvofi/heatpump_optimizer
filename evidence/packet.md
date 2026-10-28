# Review packet #2883
head: 71987ff1ee4f3f411c772681d3bcb32490832c53
base: 6e5995e51bec7c9f6d3f4dc37ed5297fefe1c3d6

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: red
CodeQL id=122599523754 neutral
arch-score / arch-score id=122599133591 success
arm id=122598884958 skipped
budget-raise-gate / budget-raise-gate id=122599133577 success
cancel-superseded id=122598884285 success
codeql / Analyze (actions) id=122599133523 success
codeql / Analyze (javascript-typescript) id=122599133525 success
codeql / Analyze (python) id=122599133507 in_progress
governance / delivery-status id=122599133603 success
governance / delivery-status-publish id=122599134664 skipped
governance / env-matrix id=122599133674 success
governance / instrument-self-tests id=122599133651 in_progress
governance / policy-docs id=122599133742 success
governance / record id=122599134761 skipped
governance / wave-script id=122599133804 success
hassfest / hassfest id=122599133504 success
kernel-points id=122599134144 skipped
prelude id=122598884532 in_progress
refresh id=122598884498 success
tests / arch-instrument id=122599859431 in_progress
tests / briefs id=122599133606 success
tests / browser id=122599859584 in_progress
tests / closure-scope id=122599133602 success
tests / closures id=122599859589 in_progress
tests / coverage id=122599859504 in_progress
tests / fast (3.14) id=122599859469 in_progress
tests / mutation id=122599133524 success
tests / mutation-autofix id=122599430089 skipped
tests / mutation-pins id=122599429974 skipped
tests / nightly-ha id=122599861098 skipped
tests / nightly-status id=122599133664 failure
tests / replay id=122599860680 skipped
tests / typing id=122599859525 success
validate / validate-hacs id=122599133488 success

## Refusals
red-unanswered: concluded red check `tests / nightly-status` is not named in ## Red checks

## Advisories
none

## carry_audit at the head
NOTE body item da04760d: R10-ORCH-PLANPAGE
NOTE body item bf8cecc6: R10-FLOW-TOOLKIT-MODEL
NOTE body item 88ff951e: R10-ORCH-LEDGER
NOTE body item d77d745d: R10-ORCH-PLANPAGE
CARRY-AUDIT: 4 finding item(s): 4 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
unverified python3
             python3 with no script argument
  unverified python3 --version
             python3 with no script argument
  ok         tests/closure.py no-copies
             `tests/closure.py` is in the tree at this head
  ok         tests/entities.py
             `tests/entities.py` is in the tree at this head
  ok         PREPR_SKIP_CLOSURES=1 bash tools/pr/prepr.sh <this body>
             `tools/pr/prepr.sh` is in the tree at this head
  unverified git diff --stat e8cb7e68302b1d350bb8219fea99e911170af030...29f51ba8cb1715f67e3f8b0f9168c3a400d8e253
             `git diff` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  ok         tools/audit/merge_throughput.py
             `tools/audit/merge_throughput.py` is in the tree at this head
  ok         tools/audit/seat/roster_lib.py
             `tools/audit/seat/roster_lib.py` is in the tree at this head
  unverified git diff --numstat e8cb7e68302b1d350bb8219fea99e911170af030...29f51ba8cb1715f67e3f8b0f9168c3a400d8e253
             `git diff` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  unverified git diff --numstat 3bd284f744e372f2440b1f6faa31e3b1708f085f 70928ca4e32c7708c20329eb979b50b935dde972
             `git diff` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  unverified git diff -U0 e8cb7e68302b1d350bb8219fea99e911170af030...29f51ba8cb1715f67e3f8b0f9168c3a400d8e253 -- <file> | awk '/^\+/ && !/^\+\+\+/ && $0 !~ /^\+[[:space:]]*$/ && $0 !~ /^\+[[:space:]]*#/' | wc -l
             `git diff` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  ok         tests/closure.py changes the gate itself, so every closure is suspect
             `tests/closure.py` is in the tree at this head
  ok         python3 tests/closure.py select --diff e8cb7e68302b1d350bb8219fea99e911170af030 --workdir <dir>
             `tests/closure.py` is in the tree at this head
  unverified git diff --name-only e8cb7e683...29f51ba8c -- <those five> | wc -l
             `git diff` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  ok         python3 tests/structure.py
             `tests/structure.py` is in the tree at this head
  ok         python3 tools/audit/archscore/score.py --diff 3bd284f744e372f2440b1f6faa31e3b1708f085f
             `tools/audit/archscore/score.py` is in the tree at this head
  ok         python3 -I tools/audit/merge_throughput.py --self-test
             `tools/audit/merge_throughput.py` is in the tree at this head
  ok         python3 -I tools/audit/seat/roster_lib.py --self-test
             `tools/audit/seat/roster_lib.py` is in the tree at this head
  unverified python3 -I <script> --self-test
             the path `<script>` is a template or an expansion, not a literal
  ok         tools/audit/seat/state_docs.py
             `tools/audit/seat/state_docs.py` is in the tree at this head
  ok         tools/pr/gate_priority.py
             `tools/pr/gate_priority.py` is in the tree at this head
  ok         python3 -I tests/throwaway_git.py --check
             `tests/throwaway_git.py` is in the tree at this head
  unverified git rev-parse --verify --quiet C:<path>
             `git rev-parse` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  unverified git cat-file -e C:<path>
             `git cat-file` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  unverified git ls-tree C -- <path>
             `git ls-tree` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  unverified git archive 2678416c53a2ec863f8c96ff755e84b261142328
             `git archive` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  unverified python3 <copy>
             the path `<copy>` is a template or an expansion, not a literal
  unverified git archive
             `git archive` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  ok         tests/throwaway_git.py
             `tests/throwaway_git.py` is in the tree at this head
  unverified git grep -nE 'cat-file["'"'"', ]+-e\b|"rev-parse", "--verify", "--quiet"|"show", f"\{[^}]+\}:|"ls-tree"' <rev> -- tools/audit/merge_throughput.py tools/audit/seat/{roster_lib,review_strength,state_docs}.py
             `git grep` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  unverified git show
             `git show` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  unverified "$PINNED^{commit}" || git fetch
             `git fetch` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  ok         python3 tests/entities.py
             `tests/entities.py` is in the tree at this head
  ok         ./tests/derive_closures.sh --single tests/entities.py --out-dir <dir>
             `tests/derive_closures.sh` is in the tree at this head
  ok         python3 tests/closure.py check --in-dir <dir> --partial
             `tests/closure.py` is in the tree at this head
  ok         python3 -I tools/audit/merge_throughput.py flow --repo . --tree e40806a7d8b024e7090182ea6d1906f45ddf89e2 --roster-ref cfacd3800bb5fa7deb043e6afd7533fa73f3a5d8
             `tools/audit/merge_throughput.py` is in the tree at this head

FIGURES: 19 resolved, 17 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
none

## Three-dot diff
diff --git a/.github/workflows/governance.yml b/.github/workflows/governance.yml
index 92a18e1df..59f45b2d4 100644
--- a/.github/workflows/governance.yml
+++ b/.github/workflows/governance.yml
@@ -537,6 +537,10 @@ jobs:
           set -euo pipefail
           python3 -I tools/audit/archscore/gate.py --self-test
           python3 -I tools/audit/check_scopes.py --self-test --repo .
+          # merge_throughput.py's `flow` subcommand (R10-FLOW-BOARD) rides
+          # this same self-test: the fixture's exact counts, the unchanged
+          # fixture's null control, and a named arm per classification
+          # predicate. A flow board that stopped counting a kind reddens here.
           python3 -I tools/audit/merge_throughput.py --self-test
           bash tools/audit/worktree_gc.sh --self-test
           python3 -I tools/coverage/partition.py --self-test
diff --git a/dev/programme/delivery/2883.md b/dev/programme/delivery/2883.md
new file mode 100644
index 000000000..adb469479
--- /dev/null
+++ b/dev/programme/delivery/2883.md
@@ -0,0 +1 @@
+- [#2883](https://github.com/tvofi/heatpump_optimizer/pull/2883) — **open**, flow board: measure programme throughput against takt, publish FLOW-BOARD.md (R10-FLOW-BOARD)
diff --git a/tests/closure.py b/tests/closure.py
index c6aaa9326..a579e1713 100644
--- a/tests/closure.py
+++ b/tests/closure.py
@@ -827,18 +827,28 @@ INERT_EXCEPT = (
     # of the generator reads it the same way -- the ref_privacy.py route below.
     "tools/audit/seat/gh_read.py",
     # R9-RO-14: tests/entities.py loads state_docs.py by importlib and runs
-    # its self-test, and that self-test SPAWNS the three state-doc generators
-    # on subprocess command lines -- a repo path on a command line is a real
-    # dependency of the spawning script, so all four land in entities.py's
-    # recorded closure. Left inside the `tools/audit/` prefix they would be
-    # declared unread while being read -- the #357 contradiction, measured
-    # three times on this list already. They leave the prefix the way
-    # record_row.py and roster_lib.py did, so an edit to the beat, or to a
-    # generator it runs, selects tests/entities.py instead of skipping it.
+    # its self-test, and that self-test SPAWNS the state-doc generators on
+    # subprocess command lines -- a repo path on a command line is a real
+    # dependency of the spawning script, so the beat and every generator it
+    # runs land in entities.py's recorded closure. Left inside the
+    # `tools/audit/` prefix they would be declared unread while being read --
+    # the #357 contradiction, measured three times on this list already. They
+    # leave the prefix the way record_row.py and roster_lib.py did, so an edit
+    # to the beat, or to a generator it runs, selects tests/entities.py
+    # instead of skipping it.
     "tools/audit/seat/state_docs.py",
     "tools/audit/seat/plan_table.py",
     "tools/audit/seat/resume_doc.py",
     "tools/audit/seat/handover_prompt.py",
+    # #2883: `merge_throughput.py flow` is the FLOW-BOARD.md generator, the
+    # fourth state doc's, and it lives beside the seat directory rather than
+    # in it. Same route as the four above: state_docs spawns it with its path
+    # on the command line, and `_exec_record` records any repo path on a
+    # subprocess command line as a read, so it is a read tests/entities.py
+    # performs. The pull request that added the call did not re-derive after
+    # it, so the committed closure never listed the file and CI's closures job
+    # named it -- INERT READS UNDER-APPROXIMATED, run 40548660478.
+    "tools/audit/merge_throughput.py",
     # #2310: state_docs.py imports ref_privacy.py, the push guard its push
     # path calls, so entities.py's load of the beat reads it the same way.
     "tools/audit/seat/ref_privacy.py",
diff --git a/tests/closures.json b/tests/closures.json
index fdec417fc..16e51abda 100644
--- a/tests/closures.json
+++ b/tests/closures.json
@@ -1621,6 +1621,7 @@
    "tools/audit/archscore/vector.py",
    "tools/audit/carry_audit.py",
    "tools/audit/judge_batch.py",
+   "tools/audit/merge_throughput.py",
    "tools/audit/round4/D11/d11lib.py",
    "tools/audit/round4/D11/governance_cost.py",
    "tools/audit/seat/gh_read.py",
diff --git a/tools/audit/merge_throughput.py b/tools/audit/merge_throughput.py
index d213535cd..bfafe4ae5 100644
--- a/tools/audit/merge_throughput.py
+++ b/tools/audit/merge_throughput.py
@@ -23,20 +23,44 @@ cut-over: `--from-runs` repeats and the files are one series). The window is sti
 prints is restated only in ## Figures, next to the command that produced
 it.
 
+The `flow` subcommand is the flow board (Lean study K1): throughput against
+the owner's demand of one roster group merged per hour, read from git alone --
+the first-parent log of the tree, the review/verdict bus refs (through
+`review_strength`'s grammar) and the roster (through `roster_lib`). It
+publishes per rolling hour and per 24 h: groups closed against takt 1.0,
+fly-ins closed, main moves split by kind, WIP by flow lane, first-pass review
+yield with its blocked-class mix, and lead time per size. `state_docs.py`'s
+generator list runs it as the FLOW-BOARD.md state doc, so it publishes beside
+the plan table. A source it cannot read prints UNAVAILABLE with its reason,
+never a zero.
+
 Usage:
 
     python3 tools/audit/merge_throughput.py --self-test
     python3 tools/audit/merge_throughput.py --from-runs FILE [--since ISO]
     python3 tools/audit/merge_throughput.py --wait --from-runs FILE
+    python3 tools/audit/merge_throughput.py flow [--repo DIR] [--tree REF] \\
+        [--roster-ref REF | --roster-file PATH] [--until ISO] [--out PATH]
 """
 
 from __future__ import annotations
 
 import argparse
 import json
+import subprocess
 import sys
-from dataclasses import dataclass
-from datetime import datetime, timezone
+from collections import Counter
+from dataclasses import dataclass, replace
+from datetime import datetime, timedelta, timezone
+from pathlib import Path
+
+#: The bus and roster readers are the instruments that already own those
+#: reads: `review_strength.py` parses the verdict grammar the bus publishes,
+#: and `roster_lib.py` is the one owner of the roster schema. Imported, never
+#: copied -- a second parser of either would drift from the first.
+sys.path.insert(0, str(Path(__file__).resolve().parent / "seat"))
+import review_strength as rs  # noqa: E402
+import roster_lib  # noqa: E402
 
 
 def load_rows(paths: list[str]) -> list[dict]:
@@ -308,11 +332,1040 @@ def self_test() -> int:
               analyze(runs_from_gh(load_rows(paths)))["merges"], 2)
         check("one listing is one merge (null)", analyze(runs_from_gh(load_rows(paths[:1])))["merges"], 1)
 
+    failures += flow_self_test()
+
     print(f"{'FAILED' if failures else 'ok'}: merge_throughput.py self-test")
     return 1 if failures else 0
 
 
+def flow_self_test() -> int:
+    """The flow board's arms, offline over a throwaway repository.
+
+    THE FIXTURE (one of each thing the board must tell apart): a roster edit
+    merged on main that closes R1-A, one group-carrying merge (#1 from
+    fix/r1-a), one record merge (#9 from record/autofix), one fly-in (#5 from
+    hotfix/urgent), and #1's two bus verdicts -- blocked on harness, then
+    merge. Every exact count below is a function of that fixture.
+
+    THE CONTROLS. A null control reads the unchanged fixture twice and
+    demands byte-identical boards; its companion moves `--until` past the
+    events and demands they leave the board. The perturbations are keyed to
+    the line each pins: `--record-prefix fix/` reclassifies the group and
+    roster merges (the record predicate), a window starting after the events
+    zeroes every count (the window predicate), a missing roster and a
+    repository with no review refs each read UNAVAILABLE rather than 0
+    (the source predicate).
+    """
+    import tempfile
+    sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tests"))
+    from throwaway_git import throwaway_git_env, throwaway_git_init
+
+    failures = 0
+
+    def check(name: str, got, want) -> None:
+        nonlocal failures
+        if got == want:
+            print(f"  ok   {name}")
+        else:
+            failures += 1
+            print(f"  FAIL {name}: got {got!r}, want {want!r}")
+
+    def check_true(name: str, cond: bool, got="") -> None:
+        nonlocal failures
+        if cond:
+            print(f"  ok   {name}")
+        else:
+            failures += 1
+            print(f"  FAIL {name}: {got!r}")
+
+    env = throwaway_git_env()
+    with tempfile.TemporaryDirectory() as d:
+        R = Path(d)
+        throwaway_git_init(R, "-q", "-b", "main")
+
+        def g(*args, e=None) -> str:
+            return subprocess.run(
+                ["git", "-C", d, *args], capture_output=True, text=True,
+                check=True, env={**env, **(e or {})}).stdout.strip()
+
+        ix = {"GIT_INDEX_FILE": str(R / ".git" / "fixture-index")}
+
+        def mk(parents: str, files: dict, msg: str, t: str) -> str:
+            g("read-tree", *([parents.split()[0]] if parents else ["--empty"]),
+              e=ix)
+            for path, text in files.items():
+                (R / "blob").write_text(text)
+                blob = g("hash-object", "-w", str(R / "blob"), e=ix)
+                g("update-index", "--add", "--cacheinfo",
+                  f"100644,{blob},{path}", e=ix)
+            return g("commit-tree", g("write-tree", e=ix),
+                     *[x for p in parents.split() for x in ("-p", p)],
+                     "-m", msg, e={**ix, "GIT_COMMITTER_DATE": t,
+                                   "GIT_AUTHOR_DATE": t})
+
+        ROSTER = roster_lib.ROSTERS_DIR + "/wave-r1-groups.json"
+        CRIT = roster_lib.CRITICAL_PATH_NAME
+
+        def ros(a="fixing") -> str:
+            return json.dumps({"groups": [
+                {"group": "R1-A", "lane": "IN", "size": "M",
+                 "resume": {"stage": a}},
+                {"group": "R1-B", "lane": "F", "size": "S",
+                 "resume": {"stage": "not-started"}},
+                {"group": "R1-C", "lane": "IN", "size": "L",
+                 "resume": {"stage": "fixing"}}]})
+
+        T = lambda h, m=0: f"2026-10-01T{h:02d}:{m:02d}:00Z"
+        crit = json.dumps({"critical": ["R1-C"]})
+        m0 = mk("", {ROSTER: ros(), CRIT: crit}, "root", T(0))
+        rb = mk(m0, {ROSTER: ros("done")}, "roster: R1-A done", T(1))
+        m1 = mk(f"{m0} {rb}", {ROSTER: ros("done")},
+                "Merge pull request #7 from o/fix/audit-r1-roster", T(1, 15))
+        b1 = mk(m0, {"f1": "1\n"}, "pr1 work", T(0, 30))
+        m2 = mk(f"{m1} {b1}", {"f1": "1\n"},
+                "Merge pull request #1 from o/fix/r1-a", T(2))
+        rc = mk(m2, {"dev/programme/delivery/9.md": "row\n"}, "record row",
+                T(2, 20))
+        m3 = mk(f"{m2} {rc}", {"dev/programme/delivery/9.md": "row\n"},
+                "Merge pull request #9 from o/record/autofix", T(2, 30))
+        fb = mk(m3, {"hot": "x\n"}, "flyin", T(3))
+        m4 = mk(f"{m3} {fb}", {"hot": "x\n"},
+                "Merge pull request #5 from o/hotfix/urgent", T(3, 10))
+        g("update-ref", "refs/remotes/origin/main", m4)
+        g("update-ref", "refs/remotes/origin/roster", m1)
+
+        roster = json.loads(ros("done"))
+        ctx = FlowCtx(repo=R, tree="refs/remotes/origin/main", remote="origin",
+                      roster=roster, roster_unavailable="",
+                      roster_ref="refs/remotes/origin/roster",
+                      roster_path=ROSTER, prefix="", record_prefix="record/",
+                      critical=roster_lib.critical_path_groups(
+                          R, "refs/remotes/origin/roster"))
+        a, b = rs.when(T(0)), rs.when(T(5))
+
+        # The bus refs do not exist yet: the yield rows are UNAVAILABLE, never
+        # 0 -- the source predicate's first arm.
+        r = period(ctx, a, b)
+        check("flow: no review refs reads UNAVAILABLE, not zero",
+              (r["yield"][0], bool(r["yield"][1])), (None, True))
+        check_true("flow: ...and the reason names the bus",
+                   "bus" in r["yield"][1] or "review" in r["yield"][1],
+                   r["yield"][1])
+
+        empty = g("hash-object", "-t", "tree", "-w", "/dev/null")
+
+        def verdict(pr: int, kind: str, head: str, t: str, cls: str = "") -> None:
+            ref = f"refs/remotes/origin/review/{pr}"
+            par = subprocess.run(["git", "-C", d, "rev-parse", "-q",
+                                  "--verify", ref], capture_output=True,
+                                 text=True)
+            subj = (f"verdict: #{pr} Fix review: {kind} {head}"
+                    + (f" {cls}:" if cls else ""))
+            sha = g("commit-tree", empty,
+                    *(["-p", par.stdout.strip()] if par.returncode == 0 else []),
+                    "-m", subj, e={"GIT_COMMITTER_DATE": t,
+                                   "GIT_AUTHOR_DATE": t})
+            g("update-ref", ref, sha)
+
+        verdict(1, "blocked", b1, T(1, 10), "harness")
+        verdict(1, "merge", b1, T(1, 50))
+
+        r = period(ctx, a, b)
+        # 1 -- the two predicates each main move is classified by.
+        check("flow: main moves split group/record/roster/fly-in",
+              (r["moves"][0]["counts"]["group"], r["moves"][0]["counts"]["record"],
+               r["moves"][0]["counts"]["roster"], r["moves"][0]["counts"]["flyin"]),
+              (1, 1, 1, 1))
+        check("flow: fly-ins closed is the fly-in merge count", r["flyins"][0], 1)
+        # 2 -- the roster predicate: a stage entering DONE_STAGES closes once.
+        check("flow: roster groups closed", r["closed"][0], 1)
+        # 3 -- the verdict predicate: #1's first verdict is blocked.
+        check("flow: first-pass yield is the first verdict's kind",
+              r["yield"][0], (0, 1))
+        check("flow: the blocked-class mix counts the class",
+              dict(r["classes"][0]), {"harness": 1})
+        # 4 -- the lead-time rule: merge time minus the branch's first commit.
+        check("flow: lead time per size (h)", r["lead"][0], ({"M": [1.5]}, 0))
+        # 5 -- the lane rule: A from the published critical set, F/FLY and
+        # C/tooling from the roster's own lane, everything else B.
+        check("flow: WIP by flow lane", flow_wip(roster, ctx.critical),
+              {"A": 1, "B": 0, "C": 0, "F": 1})
+
+        # PERTURBATION 1 -- the record key is `record_prefix`, not a name.
+        ctx_fix = replace(ctx, record_prefix="fix/")
+        r = period(ctx_fix, a, b)
+        check("flow: --record-prefix fix/ reclassifies the group and roster merges",
+              (r["moves"][0]["counts"]["group"], r["moves"][0]["counts"]["record"],
+               r["moves"][0]["counts"]["flyin"]), (0, 2, 2))
+        # PERTURBATION 2 -- the window predicate: an empty hour moves nothing.
+        r = period(ctx, rs.when(T(3, 30)), rs.when(T(5)))
+        check("flow: a window after the events counts nothing",
+              (r["moves"][0]["counts"]["group"], r["closed"][0], r["yield"][0]), (0, 0, (0, 0)))
+
+        # THE NULL CONTROL and its companion: identical input, identical
+        # board; a moved `--until` changes it (the board is a function of the
+        # refs, not of when it ran).
+        until = rs.when(T(5))
+        first, second = board(ctx, until), board(ctx, until)
+        check_true("flow null control: an unchanged fixture reads identical",
+                   render_board(first) == render_board(second))
+        check_true("flow null control is not vacuous: a moved until changes it",
+                   render_board(first) != render_board(board(ctx, rs.when(T(4)))))
+        text = render_board(first)
+        for frag in ("# Flow board", "last 1 h", "last 24 h", "Takt 1.0",
+                     "0 / 1.0", "1 / 24.0", "harness:1"):
+            check_true(f"flow board renders {frag!r}", frag in text,
+                       text[:400])
+
+        # UNAVAILABLE, never zeros, for each unreadable source.
+        r = period(replace(ctx, roster=None,
+                           roster_unavailable="no roster at refs/remotes/origin/roster"),
+                   a, b)
+        text = render_board(board(replace(
+            ctx, roster=None,
+            roster_unavailable="no roster at refs/remotes/origin/roster"), until))
+        check_true("flow: an unreadable roster is UNAVAILABLE, never zero",
+                   r["closed"][0] is None and "UNAVAILABLE" in text
+                   and "0 / 24.0" not in text, text[:400])
+        text = render_board(board(replace(ctx, tree="refs/heads/absent"), until))
+        check_true("flow: an unreadable tree is UNAVAILABLE, never zero",
+                   "UNAVAILABLE" in text, text[:400])
+
+        # --- #2883: every way a source can fail to be read -------------------
+        # The rule is the module's last line. Each arm below failed at the
+        # reviewed head: a crash, or a numeric zero where a reader had nothing.
+        import contextlib
+        import io
+
+        def run_flow(argv: list) -> tuple:
+            out, err = io.StringIO(), io.StringIO()
+            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
+                rc = flow_main(argv)
+            return rc, out.getvalue(), err.getvalue()
+
+        # B1: the CLI shape `state_docs` runs. A ref whose roster is malformed
+        # JSON raised json.JSONDecodeError out of flow_main: rc 1, no
+        # UNAVAILABLE, and state_docs' Refuse then dropped the plan table.
+        bad = mk(m0, {ROSTER: "{not json"}, "roster: broken", T(3, 40))
+        g("update-ref", "refs/remotes/origin/roster-bad", bad)
+        rc, out, err = run_flow(["--repo", d,
+                                 "--tree", "refs/remotes/origin/main",
+                                 "--roster-ref", "refs/remotes/origin/roster-bad",
+                                 "--until", T(5)])
+        check("flow: an unparseable roster at --roster-ref exits 0 with "
+              "UNAVAILABLE, never a traceback",
+              (rc, "UNAVAILABLE" in out), (0, True))
+        check_true("flow: ...and the reason names the JSON",
+                   "JSON" in out, out[:300])
+
+        # B1b: a roster that parses but is not a roster. `groups_of` indexed
+        # it and raised AttributeError out of the same CLI.
+        shaped = mk(m0, {ROSTER: json.dumps([])}, "roster: a list", T(3, 45))
+        g("update-ref", "refs/remotes/origin/roster-shaped", shaped)
+        rc, out, err = run_flow(["--repo", d,
+                                 "--tree", "refs/remotes/origin/main",
+                                 "--roster-ref", "refs/remotes/origin/roster-shaped",
+                                 "--until", T(5)])
+        check("flow: a roster that parses but is not one reads UNAVAILABLE",
+              (rc, "UNAVAILABLE" in out), (0, True))
+
+        # B1c: no window end at all -- the second way the board refused before
+        # reading anything, and took the plan table down with it.
+        roster_file = R / "roster-on-disk.json"
+        roster_file.write_text(ros("done"), encoding="utf-8")
+        rc, out, err = run_flow(["--repo", d,
+                                 "--tree", "refs/heads/absent",
+                                 "--roster-file", str(roster_file)])
+        check("flow: no readable window end renders UNAVAILABLE, never a "
+              "refusal", (rc, "UNAVAILABLE" in out), (0, True))
+
+        # B2: a roster commit that will not parse is UNAVAILABLE, not a zero
+        # with an empty reason on the takt headline.
+        bad_ctx = replace(ctx, roster_ref="refs/remotes/origin/roster-bad",
+                          roster_path=ROSTER)
+        r = period(bad_ctx, rs.when(T(3, 30)), rs.when(T(4)))
+        check_true("flow: a malformed roster commit is UNAVAILABLE, never a "
+                   "zero with an empty reason",
+                   r["closed"][0] is None and bool(r["closed"][1]),
+                   r["closed"])
+
+        # B3: the critical-path source. A ref that publishes no file puts no
+        # group on the critical path (a measurement); a file that is there and
+        # cannot be read is UNAVAILABLE, or lane A reads 0 and lane B absorbs
+        # its groups.
+        nc = mk("", {ROSTER: ros("done")}, "roster only", T(0))
+        bc = mk("", {ROSTER: ros("done"), CRIT: "{not json"}, "broken", T(0))
+        g("update-ref", "refs/remotes/origin/roster-nocrit", nc)
+        g("update-ref", "refs/remotes/origin/roster-badcrit", bc)
+        crit_nc, why_nc = critical_read(R, "refs/remotes/origin/roster-nocrit",
+                                        roster)
+        check("flow: a ref publishing no critical path reads (set, '')",
+              (crit_nc, why_nc), (set(), ""))
+        crit_bc, why_bc = critical_read(R, "refs/remotes/origin/roster-badcrit",
+                                        roster)
+        check_true("flow: an unreadable critical path is UNAVAILABLE with its "
+                   "reason", crit_bc is None and "not JSON" in why_bc, why_bc)
+        # `critical_of` is the lossy accessor (the reviewer's harness and any
+        # caller that only needs the membership test): a file source has no
+        # reason to carry, so it reads the computed chain as a plain set. The
+        # fixture's open groups have no after-edges, so the chain is its first
+        # open group.
+        check("flow: critical_of reads a file source's computed chain",
+              critical_of(R, None, json.loads(ros())), {"r1-a"})
+        b_nc = board(replace(ctx, roster_ref="refs/remotes/origin/roster-nocrit",
+                             critical=crit_nc, critical_unavailable=why_nc), until)
+        b_bc = board(replace(ctx, roster_ref="refs/remotes/origin/roster-badcrit",
+                             critical=crit_bc, critical_unavailable=why_bc), until)
+        check("flow: no published critical path puts every open group in B",
+              b_nc["wip"], ({"A": 0, "B": 1, "C": 0, "F": 1}, ""),
+              )
+        check("flow: WIP refuses to answer without a readable critical set, "
+              "never guesses lane A 0", flow_wip(roster, None), None)
+        check_true("flow: an unreadable critical path makes the WIP row "
+                   "UNAVAILABLE, never A 0",
+                   b_bc["wip"][0] is None
+                   and "UNAVAILABLE" in render_board(b_bc).split("### WIP")[1],
+                   b_bc["wip"])
+
+        # B4: the window is closed at both ends, so the default window -- whose
+        # end is a ref tip's own committer time -- counts the tip's merge.
+        r = period(ctx, a, rs.when(T(2, 30)))
+        check("flow: a record merge exactly at the window's end is counted",
+              r["moves"][0]["counts"]["record"], 1)
+        u = flow_default_until(R, "refs/remotes/origin/main",
+                               "refs/remotes/origin/roster")
+        r = period(ctx, u - timedelta(hours=24), u)
+        check("flow: the default window counts the tip merge at exactly its "
+              "end", (r["moves"][0]["counts"]["flyin"],
+                      r["moves"][0]["counts"]["record"]), (1, 1))
+        # B4b: the third measure's window. #1's first verdict -- the blocked
+        # one -- is committed at 01:10; a window ending exactly there must
+        # count it, or the 1 h row's yield is a zero for the verdict that
+        # opened the window's last event.
+        r = period(ctx, a, rs.when(T(1, 10)))
+        check("flow: a verdict at exactly the window's end is counted",
+              (r["yield"][0], dict(r["classes"][0])), ((0, 1), {"harness": 1}))
+        # ...and the roster measure's: the roster ref's tip is the merge that
+        # carries the closing stage at 01:15 (the first-parent walk sees the
+        # closing when it lands on the roster branch, not on the work commit
+        # it came from). A window ending exactly at that tip is the shape the
+        # default window takes when the roster is the later ref -- the closing
+        # commit must be in it.
+        r = period(ctx, a, rs.when(T(1, 15)))
+        check("flow: a roster commit at exactly the window's end closes in it",
+              r["closed"][0], 1)
+
+        # B5: an object git cannot read. A path probe that fails alike for an
+        # absent path and an unreadable object (`cat-file -e` reads the blob;
+        # `rev-parse --verify --quiet` answers rc 1 for an absent path and for
+        # an unreadable tree on the way to it) turned each into "nothing here"
+        # -- a zero on the takt headline, lane A 0 (#2883 review 2). Each
+        # fixture's content is unique, so dropping its object breaks no other
+        # arm; the drop asserts the object was a loose file first.
+        def drop(sha: str) -> bool:
+            p = R / ".git" / "objects" / sha[:2] / sha[2:]
+            had = p.is_file()
+            p.unlink(missing_ok=True)
+            return had
+        gone = mk(m0, {ROSTER: ros("done") + " " * 7}, "roster: blob gone",
+                  T(3, 40))
+        g("update-ref", "refs/remotes/origin/roster-gone", gone)
+        check_true("flow: fixture -- the in-window roster blob was loose and "
+                   "is dropped", drop(g("rev-parse", f"{gone}:{ROSTER}")))
+        r = period(replace(ctx, roster_ref="refs/remotes/origin/roster-gone",
+                           roster_path=ROSTER), rs.when(T(3, 30)), rs.when(T(4)))
+        check_true("flow: a roster commit whose blob git cannot read is "
+                   "UNAVAILABLE, never a zero with an empty reason",
+                   r["closed"][0] is None and "cannot read" in r["closed"][1],
+                   r["closed"])
+        cg = mk("", {ROSTER: ros("done"), CRIT: crit + " " * 7}, "crit gone",
+                T(0))
+        g("update-ref", "refs/remotes/origin/roster-critgone", cg)
+        check_true("flow: fixture -- the critical-path blob was loose and is "
+                   "dropped", drop(g("rev-parse", f"{cg}:{CRIT}")))
+        crit_cg, why_cg = critical_read(R, "refs/remotes/origin/roster-critgone",
+                                        roster)
+        check_true("flow: a critical-path blob git cannot read is UNAVAILABLE "
+                   "with git's reason", crit_cg is None and "cannot read" in why_cg,
+                   (crit_cg, why_cg))
+        b_cg = board(replace(ctx, roster_ref="refs/remotes/origin/roster-critgone",
+                             critical=crit_cg, critical_unavailable=why_cg), until)
+        check_true("flow: ...and the WIP row is UNAVAILABLE, never A 0",
+                   b_cg["wip"][0] is None
+                   and "UNAVAILABLE" in render_board(b_cg).split("### WIP")[1],
+                   b_cg["wip"])
+        # The probe's third answer, consumed. A tree git cannot read fails the
+        # first-parent `log -- path` before `state()` is reached, so no fixture
+        # drives `blob_at`'s None into it; the stub does, and pins that the
+        # walk never reads it as "no roster yet".
+        real_blob_at = roster_lib.blob_at
+        roster_lib.blob_at = lambda *_: (None, "cannot read (stubbed probe)")
+        try:
+            r = period(bad_ctx, rs.when(T(3, 30)), rs.when(T(4)))
+        finally:
+            roster_lib.blob_at = real_blob_at
+        check("flow: a path probe that cannot answer is UNAVAILABLE in the "
+              "roster walk, never {}", r["closed"],
+              (None, "roster unreadable before the window: cannot read "
+                     "(stubbed probe)"))
+        # Null control: the same shape with every object intact reads its
+        # measurement, so the arms above are the drop, not the fixture.
+        intact = mk(m0, {ROSTER: ros("done")}, "roster: intact", T(3, 40))
+        g("update-ref", "refs/remotes/origin/roster-intact", intact)
+        r = period(replace(ctx, roster_ref="refs/remotes/origin/roster-intact",
+                           roster_path=ROSTER), rs.when(T(3, 30)), rs.when(T(4)))
+        check("flow: null control -- the intact roster commit closes its group",
+              r["closed"], (1, ""))
+    return failures
+
+
+# ---------------------------------------------------------------- the flow board
+#
+# Flow board (Lean study K1). The owner's demand is one roster group merged per
+# hour; this board is how a flow change can show it worked. Every measure below
+# has one rule, stated in `render_board`'s Rules section, and every source is
+# read through the instrument that owns it: the first-parent log of the tree,
+# the review bus through `review_strength`, the roster through `roster_lib`.
+# An unreadable source prints UNAVAILABLE with its reason -- never a zero,
+# which would read as a measured "nothing happened".
+TAKT_PER_HOUR = 1.0
+FLOW_PERIODS = (("last 1 h", 1.0), ("last 24 h", 24.0))
+FLY_LANES = frozenset({"F", "FLY"})
+PROCESS_LANES = frozenset({"C", "tooling"})
+
+
+@dataclass(frozen=True)
+class FlowCtx:
+    """One run's inputs. `roster` is None exactly when `roster_unavailable`
+    says why -- the two are set together, so a caller cannot forget one. The
+    same holds for `critical` and `critical_unavailable`: None is UNAVAILABLE,
+    never "nothing is critical" (which is the empty set)."""
+    repo: Path
+    tree: str
+    remote: str
+    roster: dict | None
+    roster_unavailable: str
+    roster_ref: str | None
+    roster_path: str | None
+    prefix: str
+    record_prefix: str
+    critical: set | None
+    critical_unavailable: str = ""
+
+
+def _ok(value):
+    return (value, "")
+
+
+def _na(why: str):
+    return (None, why)
+
+
+def _git_ro(repo: Path, *args: str):
+    return subprocess.run(["git", "-C", str(repo), *args],
+                          capture_output=True, text=True)
+
+
+def flow_tip_time(repo: Path, ref: str) -> datetime | None:
+    """The ref tip's committer time, or None when the ref is unreadable."""
+    r = _git_ro(repo, "log", "-1", "--format=%cI", ref)
+    return parse_iso(r.stdout.strip()) if r.returncode == 0 and r.stdout.strip() else None
+
+
+def flow_default_until(repo: Path, tree: str, roster_ref: str | None) -> datetime | None:
+    """The window's end when `--until` is not given: the later of the tree
+    tip and the roster ref tip. Both are refs the state beat watches, so a
+    rerun over unchanged refs renders the same bytes -- the property the
+    beat's already-current check depends on."""
+    times = [t for t in (flow_tip_time(repo, tree),
+                         flow_tip_time(repo, roster_ref) if roster_ref else None)
+             if t is not None]
+    return max(times) if times else None
+
+
+def _merge_files(repo: Path, first_parent: str, sha: str) -> list[str] | None:
+    """The paths a merge changed against its first parent; None when git
+    cannot answer (the classifier then falls back to the branch name)."""
+    r = _git_ro(repo, "diff-tree", "-r", "--name-only", "--no-commit-id",
+                first_parent, sha)
+    return r.stdout.split() if r.returncode == 0 else None
+
+
+def move_kind(branch: str, files: list[str] | None, roster: dict | None,
+              record_prefix: str) -> str:
+    """One main move's kind, by this order: record, roster-edit, group, fly-in.
+
+    `record` is the branch prefix the record tooling publishes; `roster-edit`
+    is a merge whose diff touches the roster directory (or, when the diff is
+    unreadable, a branch naming a roster), because the path is the property
+    and the branch name is its fallback; `group` is `roster_lib`'s own
+    branch-to-group answer; everything else is a fly-in.
+    """
+    if branch.startswith(record_prefix):
+        return "record"
+    if files is not None:
+        if any(f.startswith(roster_lib.ROSTERS_DIR + "/") for f in files):
+            return "roster"
+    elif "roster" in branch:
+        return "roster"
+    if roster is not None and roster_lib.group_for_branch(roster, branch):
+        return "group"
+    return "flyin"
+
+
+def flow_moves(ctx: FlowCtx, a: datetime, b: datetime):
+    """The first-parent PR merges of the tree in [a, b], classified.
+
+    The window is CLOSED at both ends. Its end is a ref tip's own committer
+    time (`flow_default_until`), so a half-open window would drop the newest
+    merge -- the tip of whichever ref is later -- from every column, including
+    the 1 h column whose whole job is the last hour (#2883).
+    """
+    r = _git_ro(ctx.repo, "log", "--first-parent",
+                "--format=%H%x09%P%x09%cI%x09%s", ctx.tree)
+    if r.returncode:
+        return _na(f"cannot read {ctx.tree}: {(r.stderr or r.stdout).strip()[:120]}")
+    counts = {"group": 0, "record": 0, "roster": 0, "flyin": 0}
+    moves = []
+    for line in r.stdout.splitlines():
+        parts = line.split("\t", 3)
+        if len(parts) != 4:
+            continue
+        sha, parents, stamp, subject = parts
+        ps = parents.split()
+        m = rs.MERGE_RE.match(subject)
+        if not m or len(ps) != 2:
+            continue
+        when = rs.when(stamp)
+        if not a <= when <= b:
+            continue
+        kind = move_kind(m.group(2), _merge_files(ctx.repo, ps[0], sha),
+                         ctx.roster, ctx.record_prefix)
+        counts[kind] += 1
+        moves.append({"sha": sha, "head": ps[1], "t": when,
+                      "branch": m.group(2), "pr": int(m.group(1)),
+                      "kind": kind})
+    return _ok({"counts": counts, "moves": moves})
+
+
+def flow_closed(ctx: FlowCtx, a: datetime, b: datetime):
+    """Prefix roster groups whose stage enters DONE_STAGES in [a, b].
+
+    Every first-parent commit of the roster ref touching the roster path is
+    compared with the one before it, so a group re-opened and re-closed counts
+    twice. A file source has no history to walk and is UNAVAILABLE. A commit
+    whose roster cannot be read -- git's own failure, invalid JSON, or JSON
+    that is not a roster -- is UNAVAILABLE too: `{}` would read as a commit
+    that closed nothing (#2883). A commit that carries no roster yet closes
+    nothing, and is that measurement.
+    """
+    if ctx.roster is None:
+        return _na(ctx.roster_unavailable or "roster unreadable")
+    if not ctx.roster_ref:
+        return _na("a --roster-file carries no first-parent history")
+    path = ctx.roster_path
+    if not path:
+        try:
+            path = roster_lib.roster_path(str(ctx.repo), ctx.roster_ref)
+        except roster_lib.RosterNotFound as e:
+            return _na(f"roster path unreadable: {e}")
+
+    def state(sha: str) -> tuple[dict | None, str]:
+        """The done-flag map at one commit, or None and why it is unreadable."""
+        there, why = roster_lib.blob_at(str(ctx.repo), sha, path)
+        if there is None:
+            return None, why
+        if not there:
+            return {}, ""                      # no roster at this commit yet
+        rr = _git_ro(ctx.repo, "show", f"{sha}:{path}")
+        if rr.returncode:
+            return None, (f"cannot read {path} at {sha[:12]}: "
+                          f"{(rr.stderr or rr.stdout).strip()[:120]}")
+        try:
+            roster = json.loads(rr.stdout)
+        except ValueError as e:
+            return None, f"{path} at {sha[:12]} is not JSON: {e}"
+        why = roster_lib.roster_shape(roster)
+        if why:
+            return None, f"{path} at {sha[:12]} is not a roster: {why}"
+        groups = roster_lib.groups_of(roster)
+        return {k: (v.get("resume") or {}).get("stage") in roster_lib.DONE_STAGES
+                for k, v in groups.items() if k.startswith(ctx.prefix)}, ""
+
+    log = _git_ro(ctx.repo, "log", "--first-parent", "--format=%H%x09%cI",
+                  ctx.roster_ref, "--", path)
+    if log.returncode:
+        return _na(f"cannot read {ctx.roster_ref}: "
+                   f"{(log.stderr or log.stdout).strip()[:120]}")
+    before = _git_ro(ctx.repo, "rev-list", "-1", "--first-parent",
+                     f"--before={a.isoformat()}", ctx.roster_ref).stdout.strip()
+    prev, why = state(before) if before else ({}, "")
+    if prev is None:
+        return _na(f"roster unreadable before the window: {why}")
+    closed = 0
+    for line in reversed(log.stdout.splitlines()):
+        sha, stamp = line.split("\t")
+        if not a <= rs.when(stamp) <= b:
+            continue
+        cur, why = state(sha)
+        if cur is None:
+            return _na(why)
+        closed += sum(done and not prev.get(k, False)
+                      for k, done in cur.items())
+        prev = cur
+    return _ok(closed)
+
+
+def _bus_verdicts(ctx: FlowCtx):
+    """(pr, time, kind, class) for every verdict on the bus, oldest first.
+
+    The grammar is `review_strength`'s -- its ref patterns and its
+    PREFIX_RE/VERDICT_RE, imported, never copied. Its `load()` is not used
+    because it reads `VERDICT.md` per verdict (the nonce, cloud family and
+    model this board does not measure); that is ~900 `git show` calls and
+    takes minutes on this repository, which a beat cannot pay per pass. None
+    of the review refs at all is None (UNAVAILABLE); refs with no subject in
+    the window is a real empty list.
+    """
+    refs_ = []
+    for pattern in (f"refs/remotes/{ctx.remote}/review/",
+                    "refs/tags/archive/review/"):
+        r = _git_ro(ctx.repo, "for-each-ref", "--format=%(refname)", pattern)
+        if r.returncode:
+            raise OSError(f"cannot list {pattern}: "
+                          f"{(r.stderr or r.stdout).strip()[:120]}")
+        refs_ += r.stdout.split()
+    if not refs_:
+        return None
+    # ONE `git log` over every review ref: they share history (each verdict
+    # commit's parent is the previous verdict on the ref), so git dedups the
+    # walk and a process per ref would be ~400 spawns for the same commits.
+    r = _git_ro(ctx.repo, "log", "--format=%H%x09%cI%x09%s", *refs_)
+    if r.returncode:
+        raise OSError(f"cannot read the review refs: "
+                      f"{(r.stderr or r.stdout).strip()[:120]}")
+    seen, out = set(), []
+    for line in r.stdout.splitlines():
+        parts = line.split("\t", 2)
+        if len(parts) != 3:
+            continue
+        sha, stamp, subject = parts
+        if sha in seen or not rs.PREFIX_RE.match(subject):
+            continue
+        seen.add(sha)
+        m = rs.VERDICT_RE.match(subject)
+        if not m:
+            continue
+        out.append((int(m.group(1)), rs.when(stamp), m.group(2),
+                    m.group(4) or ""))
+    out.sort(key=lambda v: v[1])
+    return out
+
+
+def flow_verdicts(ctx: FlowCtx, a: datetime, b: datetime):
+    """(first-pass yield, blocked-class mix) over the period's bus verdicts.
+
+    Yield counts only PRs whose FIRST verdict falls in the period, so a PR
+    reviewed earlier and re-reviewed now is not counted as a first pass. No
+    review ref at all is UNAVAILABLE; refs present with no verdict in the
+    window is a real 0/0. The window is CLOSED at both ends, like the other
+    two measures: a verdict committed at exactly the window's end is in it,
+    which matters because the default end is a ref tip's own committer time
+    (#2883).
+    """
+    try:
+        verdicts = _bus_verdicts(ctx)
+    except OSError as e:  # a broken bus, not a zero
+        why = f"bus unreadable: {e}"
+        return _na(why), _na(why)
+    if verdicts is None:
+        return _na("no review/verdict bus refs"), _na("no review/verdict bus refs")
+    window = [v for v in verdicts if a <= v[1] <= b]
+    first = {}
+    for v in verdicts:
+        first.setdefault(v[0], v)
+    judged = [v for v in window if first[v[0]] is v]
+    yield_ = (sum(v[2] == "merge" for v in judged), len(judged))
+    classes = Counter(v[3] for v in window if v[2] == "blocked")
+    return _ok(yield_), _ok(classes)
+
+
+def _lead_hours(repo: Path, move: dict) -> float | None:
+    """Merge time minus the earliest commit the branch carries.
+
+    The branch's own commits are `<merge>^1..<head>`; a head git does not hold
+    falls back to the head commit itself, and an unreadable one is unresolved.
+    """
+    r = _git_ro(repo, "log", "--format=%cI",
+                f"{move['sha']}^1..{move['head']}")
+    stamps = [rs.when(x) for x in r.stdout.split()] if r.returncode == 0 else []
+    if not stamps:
+        r = _git_ro(repo, "log", "-1", "--format=%cI", move["head"])
+        if r.returncode or not r.stdout.strip():
+            return None
+        stamps = [rs.when(r.stdout.strip())]
+    return round((move["t"] - min(stamps)).total_seconds() / 3600, 2)
+
+
+def flow_lead(ctx: FlowCtx, moves: list[dict]):
+    """Lead time (hours) per roster size, over the period's group merges."""
+    if ctx.roster is None:
+        return _na(ctx.roster_unavailable or "roster unreadable")
+    groups = roster_lib.groups_of(ctx.roster)
+    by_size: dict = {}
+    unresolved = 0
+    for move in moves:
+        if move["kind"] != "group":
+            continue
+        gid = roster_lib.group_for_branch(ctx.roster, move["branch"])
+        size = (groups.get(gid) or {}).get("size")
+        hours = _lead_hours(ctx.repo, move)
+        if hours is None or not size:
+            unresolved += 1
+            continue
+        by_size.setdefault(size, []).append(hours)
+    return _ok((by_size, unresolved))
+
+
+def _lane_of(gid: str, group: dict, critical: set | None) -> str:
+    """The flow lane of one open group. The published critical-path set is A;
+    the roster's own `lane` names F (F, FLY) and C (C, tooling); the rest is
+    B product. A group in the critical set is A whatever its lane says."""
+    if critical and roster_lib.norm_group(gid) in critical:
+        return "A"
+    lane = str(group.get("lane") or "")
+    if lane in FLY_LANES:
+        return "F"
+    if lane in PROCESS_LANES:
+        return "C"
+    return "B"
+
+
+def flow_wip(roster: dict | None, critical: set | None) -> dict | None:
+    """Open groups by flow lane, a snapshot at the window's end.
+
+    None when the roster cannot be read, and None when the critical-path set
+    could not be either: a None `critical` is UNAVAILABLE, not an empty set,
+    and answering it as one would print lane A 0 while lane B swallowed A's
+    groups (#2883). "No group is critical" is `set()`.
+    """
+    if roster is None or critical is None:
+        return None
+    out = {"A": 0, "B": 0, "C": 0, "F": 0}
+    for gid, group in roster_lib.groups_of(roster).items():
+        if roster_lib.is_open(group):
+            out[_lane_of(gid, group, critical)] += 1
+    return out
+
+
+def critical_read(repo: Path, roster_ref: str | None,
+                  roster: dict | None) -> tuple[set | None, str]:
+    """The critical-path set and, when it cannot be read, the reason.
+
+    `(set, "")` when the source answered -- `set()` is the measurement "the
+    ref publishes no critical path, so no group is on it". `(None, why)` when
+    a file is there and cannot be read: a board must print that, because lane
+    A would otherwise read 0 and lane B absorb the groups that belong to it
+    (#2883). A roster that is already UNAVAILABLE is None with no reason of
+    its own; the roster carries the reason.
+    """
+    if roster is None:
+        return None, ""
+    if roster_ref:
+        return roster_lib.critical_path_read(str(repo), roster_ref)
+    return {roster_lib.norm_group(g) for g in roster_lib.critical_path(roster)}, ""
+
+
+def critical_of(repo: Path, roster_ref: str | None, roster: dict | None) -> set | None:
+    """The critical-path set alone, or None.
+
+    The lossy accessor of `critical_read`, for callers that only need the
+    membership test. It keeps the reviewed head's contract exactly -- None is
+    both "unreadable" and "no file", and an empty set reads as None too --
+    so the control that distinguishes them is the board's, which reads
+    `critical_read`.
+    """
+    return critical_read(repo, roster_ref, roster)[0] or None
+
+
+def period(ctx: FlowCtx, a: datetime, b: datetime) -> dict:
+    """Every per-period measure over [a, b]; each value is `(value, reason)`."""
+    if ctx.roster is None:
+        # group vs fly-in is not answerable without the roster, so the split
+        # is unavailable rather than a wrong fly-in count.
+        why = ctx.roster_unavailable or "roster unreadable"
+        moves, flyins, lead = _na(why), _na(why), _na(why)
+    else:
+        moves = flow_moves(ctx, a, b)
+        if moves[0] is None:
+            flyins, lead = _na(moves[1]), _na(moves[1])
+        else:
+            counts = moves[0]["counts"]
+            flyins = _ok(counts["flyin"])
+            lead = flow_lead(ctx, moves[0]["moves"])
+    yield_, classes = flow_verdicts(ctx, a, b)
+    return {"moves": moves, "flyins": flyins, "lead": lead,
+            "closed": flow_closed(ctx, a, b),
+            "yield": yield_, "classes": classes}
+
+
+def board(ctx: FlowCtx, until: datetime | None) -> dict:
+    """The whole board: both rolling periods plus the WIP snapshot.
+
+    `until` is None when neither watched ref yields a commit time. There is
+    then no window, so every per-period measure is UNAVAILABLE with that
+    reason rather than a zero -- the board's own last rule -- and the board is
+    still rendered, so a state beat that cannot read a ref publishes the
+    reason instead of refusing and dropping the documents generated before it
+    (#2883).
+    """
+    if until is None:
+        why = (f"no window end: neither {ctx.tree} nor "
+               f"{ctx.roster_ref or 'the roster file'} has a readable "
+               "commit time")
+        blank = {key: (None, why) for key in
+                 ("moves", "flyins", "lead", "closed", "yield", "classes")}
+        periods = [(label, hours, dict(blank)) for label, hours in FLOW_PERIODS]
+    else:
+        periods = [(label, hours, period(
+            ctx, until - timedelta(hours=hours), until))
+            for label, hours in FLOW_PERIODS]
+    if ctx.roster is None:
+        wip = _na(ctx.roster_unavailable or "roster unreadable")
+    elif ctx.critical is None:
+        wip = _na(ctx.critical_unavailable or "critical path unreadable")
+    else:
+        wip = _ok(flow_wip(ctx.roster, ctx.critical))
+    return {"until": until, "periods": periods, "wip": wip, "ctx": ctx}
+
+
+def _cell(measure) -> str:
+    value, why = measure
+    return f"UNAVAILABLE ({why})" if value is None else ""
+
+
+def _closed_cell(measure, hours: float) -> str:
+    value, why = measure
+    if value is None:
+        return _cell(measure)
+    return f"{value} / {hours * TAKT_PER_HOUR:.1f}"
+
+
+def _count_cell(measure) -> str:
+    value, why = measure
+    return str(value) if value is not None else _cell(measure)
+
+
+def _moves_cell(measure) -> str:
+    value, why = measure
+    if value is None:
+        return _cell(measure)
+    counts = value["counts"]
+    return (f"{counts['group']} / {counts['record']} / "
+            f"{counts['roster']} / {counts['flyin']}")
+
+
+def _yield_cell(measure) -> str:
+    value, why = measure
+    if value is None:
+        return _cell(measure)
+    first_pass, judged = value
+    return f"{first_pass}/{judged} ({first_pass / judged:.2f})" if judged else "0/0 (-)"
+
+
+def _classes_cell(measure) -> str:
+    value, why = measure
+    if value is None:
+        return _cell(measure)
+    return ", ".join(f"{k}:{v}" for k, v in sorted(value.items())) or "none"
+
+
+def _lead_cell(measure) -> str:
+    value, why = measure
+    if value is None:
+        return _cell(measure)
+    by_size, unresolved = value
+    parts = []
+    for size in sorted(by_size):
+        values = sorted(by_size[size])
+        parts.append(f"{size} n={len(values)} p50={percentile(values, 0.5):.2f} "
+                     f"max={max(values):.2f}")
+    if unresolved:
+        parts.append(f"unresolved {unresolved}")
+    return "; ".join(parts) or "none"
+
+
+FLOW_RULES = (
+    "every period is CLOSED at both ends: an event at exactly the window's "
+    "start or end is counted, so the default window -- which ends at a ref "
+    "tip's own committer time -- includes the tip's merge.",
+    "roster groups closed: a group whose resume.stage enters roster_lib's "
+    "DONE_STAGES in the period, counted per first-parent commit of the roster "
+    "ref; takt is 1.0 group per hour, so the period's demand is its hours.",
+    "fly-ins closed: a first-parent PR merge of the tree in the period whose "
+    "branch maps to no roster group and is neither a record nor a roster edit.",
+    "main moves: each first-parent PR merge of the tree in the period, by "
+    "kind -- group-carrying (roster_lib's branch-to-group answer), record "
+    "(--record-prefix), roster-edit (the merge's diff touches the roster "
+    "directory), fly-in (the rest).",
+    "first-pass yield: of the PRs whose FIRST bus verdict falls in the "
+    "period, the share whose first verdict is `merge`; a PR whose first "
+    "verdict predates the period is not judged in it.",
+    "blocked-class mix: every blocked verdict in the period, by the class "
+    "word its subject carries.",
+    "lead time per size: merge time minus the earliest commit the group's "
+    "branch carries, over group-carrying merges whose roster group names a "
+    "size; n, p50 and max hours.",
+    "WIP by lane: open roster groups at the window's end -- A when in the "
+    "published critical-path set, F for roster lanes F/FLY, C for C/tooling, "
+    "B otherwise. A ref that publishes no critical-path file puts no group on "
+    "it; a file that is there and cannot be read is UNAVAILABLE.",
+    "A source that cannot be read prints UNAVAILABLE with its reason; it is "
+    "never a zero.",
+)
+
+
+def render_board(b: dict) -> str:
+    """The markdown document the state beat publishes beside the plan table."""
+    ctx: FlowCtx = b["ctx"]
+    labels = [label for label, _, _ in b["periods"]]
+    if b["until"] is None:
+        ends = ("Window ends UNAVAILABLE (no readable ref time; each measure "
+                "below carries its reason)")
+    else:
+        ends = (f"Window ends {b['until'].isoformat()} (a function of the "
+                "refs, not of when this ran)")
+    lines = ["# Flow board", "", f"{ends}. Takt 1.0 roster group per hour.",
+             "", "Sources: tree `" + ctx.tree + "`, roster "
+             + (f"`{ctx.roster_ref}`" if ctx.roster_ref else "`--roster-file`")
+             + f", bus `{ctx.remote}/review/*`"
+             + (f", group prefix `{ctx.prefix}`" if ctx.prefix else ""),
+             "",
+             "| measure | " + " | ".join(labels) + " |",
+             "|---" * (len(labels) + 1) + "|"]
+
+    def row(name: str, cells: list[str]) -> None:
+        lines.append(f"| {name} | " + " | ".join(cells) + " |")
+
+    row("roster groups closed vs takt",
+        [_closed_cell(m["closed"], h) for _, h, m in b["periods"]])
+    row("fly-ins closed", [_count_cell(m["flyins"])
+                           for _, _, m in b["periods"]])
+    row("main moves: group-carrying / record / roster-edit / fly-in",
+        [_moves_cell(m["moves"]) for _, _, m in b["periods"]])
+    row("first-pass fix-review yield",
+        [_yield_cell(m["yield"]) for _, _, m in b["periods"]])
+    row("blocked-class mix",
+        [_classes_cell(m["classes"]) for _, _, m in b["periods"]])
+    row("lead time per size (h, n/p50/max)",
+        [_lead_cell(m["lead"]) for _, _, m in b["periods"]])
+
+    lines += ["", "### WIP by flow lane (snapshot at the window's end)", ""]
+    value, why = b["wip"]
+    if value is None:
+        lines.append(f"UNAVAILABLE ({why})")
+    else:
+        lines += ["| A critical path | B product | C process | F fly-in |",
+                  "|---|---|---|---|",
+                  f"| {value['A']} | {value['B']} | {value['C']} | {value['F']} |"]
+
+    lines += ["", "## Rules", ""]
+    lines += [f"- {rule}" for rule in FLOW_RULES]
+    return "\n".join(lines) + "\n"
+
+
+def flow_main(argv: list[str]) -> int:
+    ap = argparse.ArgumentParser(
+        prog="merge_throughput.py flow",
+        description="the flow board: throughput against takt 1.0")
+    ap.add_argument("--repo", default=".",
+                    help="the git checkout to read (default .)")
+    ap.add_argument("--tree", default="origin/main")
+    ap.add_argument("--remote", default="origin")
+    src = ap.add_mutually_exclusive_group()
+    src.add_argument("--roster-ref", default=None,
+                     help="default: roster_lib.default_roster_ref's answer")
+    src.add_argument("--roster-file")
+    ap.add_argument("--roster-path")
+    ap.add_argument("--prefix", default="",
+                    help="count only group ids with this prefix")
+    ap.add_argument("--record-prefix", default="record/")
+    ap.add_argument("--until", metavar="ISO",
+                    help="window end (default: the later of the tree tip and "
+                         "the roster ref tip)")
+    ap.add_argument("--fetch", action="store_true",
+                    help="fetch the review/verdict/probe refs and tags first")
+    ap.add_argument("--out")
+    ap.add_argument("--self-test", action="store_true")
+    a = ap.parse_args(argv)
+    if a.self_test:
+        return self_test()
+
+    repo = Path(a.repo)
+    if a.fetch:
+        for heads in ("review", "verdict", "probe"):
+            r = _git_ro(repo, "fetch", "-q", "--tags", a.remote,
+                        f"+refs/heads/{heads}/*:refs/remotes/{a.remote}/{heads}/*")
+            if r.returncode:
+                print(f"flow: fetch of {heads}/ failed, reading what is local: "
+                      f"{(r.stderr or r.stdout).strip()[:160]}", file=sys.stderr)
+
+    if a.roster_file:
+        roster_ref = None
+        try:
+            roster = roster_lib.load_roster_file(a.roster_file)
+        except (OSError, ValueError) as e:
+            roster, why = None, f"cannot read {a.roster_file}: {type(e).__name__}"
+        else:
+            why = roster_lib.roster_shape(roster)
+            if why:                     # parses, but not a roster (#2883)
+                roster, why = None, f"cannot read {a.roster_file}: {why}"
+        roster_path = None
+    else:
+        roster_ref = roster_lib.reader_ref(str(repo), a.roster_ref)
+        try:
+            roster = roster_lib.show_roster(str(repo), roster_ref, a.roster_path)
+        except roster_lib.RosterNotFound as e:
+            roster, why = None, f"roster unreadable: {e}"
+        except ValueError as e:         # json.loads: malformed JSON, not a crash
+            roster, why = None, (f"roster unreadable: {roster_ref} is not "
+                                 f"JSON: {e}")
+        else:
+            why = roster_lib.roster_shape(roster)
+            if why:                     # parses, but not a roster (#2883)
+                roster, why = None, (f"roster unreadable: {roster_ref} is not "
+                                     f"a roster: {why}")
+        roster_path = a.roster_path
+        if roster is not None and not roster_path:
+            try:
+                roster_path = roster_lib.roster_path(str(repo), roster_ref)
+            except roster_lib.RosterNotFound:
+                roster_path = None
+
+    critical, critical_why = critical_read(repo, roster_ref, roster)
+    ctx = FlowCtx(repo=repo, tree=a.tree, remote=a.remote, roster=roster,
+                  roster_unavailable=why, roster_ref=roster_ref,
+                  roster_path=roster_path, prefix=a.prefix,
+                  record_prefix=a.record_prefix, critical=critical,
+                  critical_unavailable=critical_why)
+    until = parse_iso(a.until) if a.until else flow_default_until(
+        repo, a.tree, roster_ref)
+    if until is not None and until.tzinfo is None:
+        until = until.replace(tzinfo=timezone.utc)
+
+    text = render_board(board(ctx, until))
+    if a.out:
+        Path(a.out).write_text(text, encoding="utf-8")
+        print(f"wrote {a.out} ({len(text.encode('utf-8'))} bytes)")
+    else:
+        sys.stdout.write(text)
+    return 0
+
+
 def main(argv: list[str]) -> int:
+    if argv[:1] == ["flow"]:
+        return flow_main(argv[1:])
+
     ap = argparse.ArgumentParser()
     ap.add_argument("--self-test", action="store_true")
     ap.add_argument("--from-runs", metavar="FILE", action="append", default=[])
diff --git a/tools/audit/seat/INSTRUMENTS.md b/tools/audit/seat/INSTRUMENTS.md
index 2521cbbbb..1827637a6 100644
--- a/tools/audit/seat/INSTRUMENTS.md
+++ b/tools/audit/seat/INSTRUMENTS.md
@@ -86,7 +86,19 @@ re-runnable measurement harnesses a fixer or judge lands with a PR — its
   `checks, 0 failed` line.
 - `merge_throughput.py` — measures whether merges land inside the previous
   merge's gate window often enough to justify a merge queue. When: someone
-  proposes a queue; the numbers decide before the mechanism is built.
+  proposes a queue; the numbers decide before the mechanism is built. Its
+  `flow` subcommand is the flow board (Lean study K1): throughput against
+  the owner's demand of one roster group merged per hour, read from git
+  alone — the first-parent log, the review/verdict bus refs through
+  `review_strength`'s grammar and the roster through `roster_lib`. It prints
+  per rolling hour and per 24 h: groups closed against takt 1.0, fly-ins
+  closed, main moves split into group-carrying/record/roster-edit/fly-in,
+  WIP by flow lane (A/B/C/F), first-pass review yield with its blocked-class
+  mix, and lead time per size, and prints UNAVAILABLE rather than a zero
+  when a source cannot be read. When: any flow change that claims to move
+  throughput. Refusal: `--self-test` — its fixture's exact counts, the
+  unchanged-fixture null control, and a named arm per classification
+  predicate; `governance.yml`'s self-test step runs it.
 - `preflight.sh` — mechanical checks on anything the orchestrator publishes
   (merge body, issue body, comment, brief): closing keywords and the claim
   shapes. When: before posting any prose that GitHub or a later seat reads.
@@ -1027,17 +1039,19 @@ sweep's standing-seat liveness step keep them alive.
   and `one-train` beside a train.sh still closing; a pull request already
   queued is `ALREADY`, rc 0. One fcntl lock (`queue.lock`) orders every add
   against the train's drains and its close; never a second train.
-- `state_docs.py` — one call regenerates the three state docs
-  (`plan_table.py`, `resume_doc.py`, `handover_prompt.py`), commits exactly
+- `state_docs.py` — one call regenerates the four state docs
+  (`plan_table.py`, `merge_throughput.py flow`, `resume_doc.py`,
+  `handover_prompt.py`), commits exactly
   their outputs to the orphan ref `handoff/audit-r<N>-plan` at
   `handoff/round<N>/state/`, N the roster's round, and mirrors them to
-  `--mirror`. When: every state
+  `--mirror`. The flow board publishes beside the plan table, so a beat
+  pass carries the throughput figures with the plan they explain. When: every state
   beat — it replaces the five hand commands (worktree, copy, commit, push,
   mirror) and runs the generators instead of copying their logic. Dry run by
   default: without `--push` nothing remote is written. Refusals: any path
-  outside the three state docs (the write set is checked before a commit
+  outside the four state docs (the write set is checked before a commit
   exists to push; every other path at the ref — a round's evidence — is
-  carried untouched), a first commit that would not be exactly the three
+  carried untouched), a first commit that would not be exactly the four
   files, and an already-current tip, which is reported and left alone. The
   commit is plumbing over a temp index, so the calling checkout's index is
   never touched.
diff --git a/tools/audit/seat/roster_lib.py b/tools/audit/seat/roster_lib.py
index 212c793e5..4b3f4ef3e 100644
--- a/tools/audit/seat/roster_lib.py
+++ b/tools/audit/seat/roster_lib.py
@@ -163,6 +163,30 @@ def _git(repo: str, *args: str) -> subprocess.CompletedProcess:
                           text=True)
 
 
+def blob_at(repo: str, ref: str, path: str) -> tuple[bool | None, str]:
+    """Whether `path` is a file in `ref`'s tree: `(True, "")`, `(False, "")`
+    when nothing is at that path, `(None, why)` when git cannot say.
+
+    Read with `git ls-tree`, which reads the trees on the way to `path` and
+    never the blob, so absent (an empty listing) and unreadable (git's own
+    failure) are different answers. `cat-file -e` fails alike for an absent
+    path and an unreadable blob, and `rev-parse --verify --quiet` exits 1
+    alike for an absent path and an unreadable tree on the way to it (#2883).
+    A present blob git cannot read is True here; its reader reports that.
+    """
+    r = _git(repo, "ls-tree", "-z", "--full-tree", ref, "--", path)
+    if r.returncode:
+        return None, (f"cannot read {path} at {ref}: "
+                      f"{(r.stderr or r.stdout).strip()[:140]}")
+    for entry in filter(None, r.stdout.split("\0")):
+        meta, _, name = entry.partition("\t")
+        if name == path:
+            kind = meta.split()[1]
+            return (True, "") if kind == "blob" else (
+                None, f"{path} at {ref} is a {kind}, not a file")
+    return False, ""
+
+
 def roster_path(repo: str = ".", ref: str | None = None,
                 override: str | None = None) -> str:
     """THE answer to "which roster", relative to the repository root.
@@ -174,11 +198,11 @@ def roster_path(repo: str = ".", ref: str | None = None,
     and an absent roster both raise RosterNotFound.
     """
     if override:
-        there = (_git(repo, "cat-file", "-e", f"{ref}:{override}").returncode == 0
-                 if ref else (Path(repo) / override).is_file())
+        there, why = (blob_at(repo, ref, override) if ref
+                      else ((Path(repo) / override).is_file(), ""))
         if not there:
-            raise RosterNotFound(f"--roster-path {override} is not a file at "
-                                 f"{ref or Path(repo).resolve()}")
+            raise RosterNotFound(why or f"--roster-path {override} is not a "
+                                 f"file at {ref or Path(repo).resolve()}")
         return override
     if ref:
         r = _git(repo, "ls-tree", "--name-only", ref, ROSTERS_DIR + "/")
@@ -280,6 +304,30 @@ def reader_ref(repo: str, ref: str | None) -> str:
     return ref
 
 
+def roster_shape(roster) -> str:
+    """Why `roster` is not a roster ("" when it is one).
+
+    JSON that parses is not yet a source this module can read: every reader
+    below indexes `groups` and each entry's `group`, so a list, a `groups`
+    that is not one, or an entry without a string `group` is an unreadable
+    source -- UNAVAILABLE to a caller that must tell it from a measurement
+    (#2883) -- and not an empty roster. A missing `groups` key is still an
+    empty roster: `groups_of` has always read that as no groups, and a
+    roster of none is a measurement.
+    """
+    if not isinstance(roster, dict):
+        return f"not a JSON object ({type(roster).__name__})"
+    groups = roster.get("groups", [])
+    if not isinstance(groups, list):
+        return f"`groups` is a {type(groups).__name__}, not a list"
+    for i, g in enumerate(groups):
+        if not isinstance(g, dict):
+            return f"groups[{i}] is a {type(g).__name__}, not an object"
+        if not isinstance(g.get("group"), str):
+            return f"groups[{i}] carries no string `group`"
+    return ""
+
+
 def groups_of(roster: dict) -> dict:
     """group id -> entry, preserving roster order."""
     return {g["group"]: g for g in roster.get("groups", [])}
@@ -416,32 +464,62 @@ def group_for_branch(roster: dict, branch: str) -> str | None:
 #     {"at": "<iso8601>", "critical": ["R10-GROUP", ...]}
 #
 # `at` records when the set was published and is not read; `critical` is the
-# list of roster group ids. A missing, unreadable or differently-shaped file is
-# None -- "no group is critical" to a caller, never a crash and never "all are".
+# list of roster group ids. A ref that publishes no file means no group is
+# critical -- a measurement, `set()`; a file that is there and cannot be read
+# (git's own failure, invalid JSON, a non-object, a `critical` that is not a
+# list of strings) is UNAVAILABLE with its reason, never a zero and never "all
+# are" (#2883). `critical_path_groups` keeps the lossy None for callers whose
+# contract is to fail toward "nothing critical"; `critical_path_read` is the
+# reason-bearing form a board that must print the difference reads.
 CRITICAL_PATH_NAME = f"{ROSTERS_DIR}/critical-path.json"
 
 
-def critical_path_groups(repo: str, ref: str) -> set[str] | None:
-    """The normalized group ids `CRITICAL_PATH_NAME` lists at `ref`, or None.
+def critical_path_read(repo: str, ref: str) -> tuple[set[str] | None, str]:
+    """`(set, "")` when `ref` answered; `(None, why)` when it could not be read.
 
     Read at `ref` (`git show`), so a caller needs no checkout of the roster
-    branch. None covers every failure the caller must treat as "nothing is
-    critical": the file absent at this ref, git unreadable, invalid JSON, a
-    non-object, or a `critical` that is not a list of strings.
+    branch. An unresolvable REF and a file that will not parse are both
+    unreadable; only a ref that resolves and carries no
+    `CRITICAL_PATH_NAME` at all is the measurement "none published".
     """
+    if _git(repo, "rev-parse", "--verify", "--quiet",
+            f"{ref}^{{commit}}").returncode:
+        return None, f"cannot read {ref}: not a resolvable commit"
+    there, why = blob_at(repo, ref, CRITICAL_PATH_NAME)
+    if there is None:
+        return None, why
+    if not there:
+        return set(), ""
     r = _git(repo, "show", f"{ref}:{CRITICAL_PATH_NAME}")
     if r.returncode:
-        return None
+        return None, (f"cannot read {CRITICAL_PATH_NAME} at {ref}: "
+                      f"{(r.stderr or r.stdout).strip()[:140]}")
     try:
         data = json.loads(r.stdout)
-    except ValueError:
-        return None
+    except ValueError as e:
+        return None, f"{CRITICAL_PATH_NAME} at {ref} is not JSON: {e}"
     if not isinstance(data, dict):
-        return None
+        return None, (f"{CRITICAL_PATH_NAME} at {ref} is not a JSON object "
+                      f"({type(data).__name__})")
     ids = data.get("critical")
     if not isinstance(ids, list) or not all(isinstance(i, str) for i in ids):
-        return None
-    return {norm_group(i) for i in ids}
+        return None, (f"{CRITICAL_PATH_NAME} at {ref} carries no `critical` "
+                      "list of ids")
+    return {norm_group(i) for i in ids}, ""
+
+
+def critical_path_groups(repo: str, ref: str) -> set[str] | None:
+    """The normalized group ids `CRITICAL_PATH_NAME` lists at `ref`, or None.
+
+    The lossy convenience form of `critical_path_read`: None covers every
+    outcome a caller must treat as "nothing is critical" -- the file absent at
+    this ref, git unreadable, invalid JSON, a non-object, or a `critical` that
+    is not a list of strings. `gate_priority.py`'s pre-pr helper is that
+    caller: it must never crash a run. A reader that has to *print* the
+    difference reads `critical_path_read`.
+    """
+    groups, _ = critical_path_read(repo, ref)
+    return groups or None
 
 
 # ------------------------------------------------------------------ self-test
@@ -540,6 +618,20 @@ def _self_test() -> int:
         check("a group id normalizes case and underscore", norm_group("R10_A") == "r10-a")
         check("no critical-path file at a ref is None",
               critical_path_groups(str(repo), "HEAD") is None)
+        check("critical_path_read: a ref publishing no file is (set(), ''), a "
+              "measurement not a failure",
+              critical_path_read(str(repo), "HEAD") == (set(), ""),
+              critical_path_read(str(repo), "HEAD"))
+        check("critical_path_read: an unresolvable ref is UNAVAILABLE",
+              critical_path_read(str(repo), "refs/heads/nope")[0] is None
+              and bool(critical_path_read(str(repo), "refs/heads/nope")[1]))
+        check("roster_shape: an absent groups key is an empty roster",
+              roster_shape({}) == "", roster_shape({}))
+        check("roster_shape: a list is not a roster",
+              "not a JSON object" in roster_shape([]), roster_shape([]))
+        check("roster_shape: an entry without a string group is not a roster",
+              "groups[0]" in roster_shape({"groups": [{"lane": "IN"}]}),
+              roster_shape({"groups": [{"lane": "IN"}]}))
         (repo / CRITICAL_PATH_NAME).write_text(
             json.dumps({"at": "2026-10-20T00:00:00Z", "critical": ["R10_A", "R10-B"]}),
             encoding="utf-8")
@@ -557,6 +649,11 @@ def _self_test() -> int:
             check(f"a malformed critical-path file is None: {bad}",
                   critical_path_groups(str(repo), "HEAD") is None,
                   critical_path_groups(str(repo), "HEAD"))
+            check(f"critical_path_read: a malformed file is UNAVAILABLE, not "
+                  f"empty: {bad}",
+                  critical_path_read(str(repo), "HEAD")[0] is None
+                  and bool(critical_path_read(str(repo), "HEAD")[1]),
+                  critical_path_read(str(repo), "HEAD"))
         check("two rosters at a ref: the newest",
               roster_path(str(repo), "HEAD")
               == f"{ROSTERS_DIR}/wave-r10-groups.json")
@@ -610,6 +707,71 @@ def _self_test() -> int:
         got = default_roster_ref(g)
         check("no roster readable at main: main, with a note (null control)",
               got[0] == MAIN_REF and got[1], got)
+
+        # AN OBJECT GIT CANNOT READ (#2883 review 2). Absent and unreadable
+        # are different answers: `cat-file -e` fails alike for an absent path
+        # and an unreadable blob, and `rev-parse --verify --quiet` exits 1
+        # alike for an absent path and an unreadable tree on the way to it.
+        # Last in the test: the drops below leave HEAD unreadable. Each
+        # dropped object is unique to its commit and asserted loose first.
+        def drop(sha: str) -> bool:
+            p = repo / ".git" / "objects" / sha[:2] / sha[2:]
+            had = p.is_file()
+            p.unlink(missing_ok=True)
+            return had
+
+        def commit_crit(at: str) -> str:
+            (repo / CRITICAL_PATH_NAME).write_text(
+                json.dumps({"at": at, "critical": ["R10-A"]}), encoding="utf-8")
+            subprocess.run(["git", "-C", str(repo), "add", "-A"], check=True)
+            subprocess.run(["git", "-C", str(repo), "commit", "-q", "-m", at],
+                           check=True)
+            return subprocess.run(["git", "-C", str(repo), "rev-parse", "HEAD"],
+                                  capture_output=True, text=True).stdout.strip()
+        intact = commit_crit("2026-10-28T00:00:00Z")
+        check("blob_at: a file present is (True, '')",
+              blob_at(str(repo), intact, CRITICAL_PATH_NAME) == (True, ""),
+              blob_at(str(repo), intact, CRITICAL_PATH_NAME))
+        check("blob_at: an absent path is (False, ''), a measurement",
+              blob_at(str(repo), intact, f"{ROSTERS_DIR}/nope.json") == (False, ""),
+              blob_at(str(repo), intact, f"{ROSTERS_DIR}/nope.json"))
+        check("blob_at: an absent directory is (False, '')",
+              blob_at(str(repo), intact, "zz/nope.json") == (False, ""),
+              blob_at(str(repo), intact, "zz/nope.json"))
+        got = blob_at(str(repo), intact, ROSTERS_DIR)
+        check("blob_at: a directory is not a file, and says so",
+              got[0] is None and "tree" in got[1], got)
+        blob_gone = commit_crit("2026-10-28T01:00:00Z")
+        check("fixture: the critical-path blob was loose and is dropped",
+              drop(subprocess.run(["git", "-C", str(repo), "rev-parse",
+                                   f"{blob_gone}:{CRITICAL_PATH_NAME}"],
+                                  capture_output=True, text=True).stdout.strip()))
+        check("blob_at: an unreadable blob is still present -- its entry is "
+              "read, not its bytes",
+              blob_at(str(repo), blob_gone, CRITICAL_PATH_NAME) == (True, ""),
+              blob_at(str(repo), blob_gone, CRITICAL_PATH_NAME))
+        got = critical_path_read(str(repo), blob_gone)
+        check("critical_path_read: an unreadable blob is UNAVAILABLE with "
+              "git's reason, never set()",
+              got[0] is None and "cannot read" in got[1], got)
+        tree_gone = commit_crit("2026-10-28T02:00:00Z")
+        check("fixture: the rosters tree was loose and is dropped",
+              drop(subprocess.run(["git", "-C", str(repo), "rev-parse",
+                                   f"{tree_gone}:{ROSTERS_DIR}"],
+                                  capture_output=True, text=True).stdout.strip()))
+        got = blob_at(str(repo), tree_gone, CRITICAL_PATH_NAME)
+        check("blob_at: an unreadable tree on the way is (None, why), never "
+              "absent", got[0] is None and "cannot read" in got[1], got)
+        got = blob_at(str(repo), tree_gone, "zz/nope.json")
+        check("blob_at: a path outside the unreadable tree is still absent "
+              "(null control)", got == (False, ""), got)
+        got = critical_path_read(str(repo), tree_gone)
+        check("critical_path_read: an unreadable tree is UNAVAILABLE, never "
+              "set()", got[0] is None and "cannot read" in got[1], got)
+        why = refuses(lambda: roster_path(str(repo), tree_gone, CRITICAL_PATH_NAME))
+        check("an override behind an unreadable tree refuses with git's read, "
+              "not 'is not a file'",
+              "cannot read" in why and "is not a file" not in why, why)
     print(f"roster_lib self-test: {n[0]} checks, {len(fails)} failed")
     for f in fails:
         print("FAIL", f)
diff --git a/tools/audit/seat/state_docs.py b/tools/audit/seat/state_docs.py
index 6d4033a64..430c45716 100644
--- a/tools/audit/seat/state_docs.py
+++ b/tools/audit/seat/state_docs.py
@@ -1,5 +1,5 @@
 #!/usr/bin/env python3
-"""The state-doc pusher: regenerate the three handoff state docs in one call.
+"""The state-doc pusher: regenerate the four handoff state docs in one call.
 
     python3 tools/audit/seat/state_docs.py [--repo OWNER/REPO] \
         [--roster-ref GITREF [--roster-path PATH] | --roster-file PATH] \
@@ -9,9 +9,10 @@
         [--watch-ref REF] [--interval SECONDS] [--tip-file PATH] [--once]
     python3 tools/audit/seat/state_docs.py --self-test
 
-The loop the #1946 generators left open: run plan_table.py, resume_doc.py
-and handover_prompt.py in order, commit exactly their outputs to the orphan
-ref `handoff/audit-r<N>-plan` at handoff/round<N>/state/, and mirror the three
+The loop the #1946 generators left open: run plan_table.py, merge_throughput.py
+(its `flow` subcommand), resume_doc.py and handover_prompt.py in order, commit
+exactly their outputs to the orphan
+ref `handoff/audit-r<N>-plan` at handoff/round<N>/state/, and mirror the four
 files to a local directory. Without --push it is a dry run: nothing remote
 is written and it prints what it would push. N is the ROSTER's round, never a
 constant here: the round `roster_lib.roster_path` picks (the newest
@@ -20,7 +21,7 @@ constant here: the round `roster_lib.roster_path` picks (the newest
 cannot be read is refused, so a round-10 beat cannot write round 9's state.
 
 The write set is guarded the way record_row.py guards its rows: every path
-the commit touches must be one of the three state docs, checked BEFORE any
+the commit touches must be one of the four state docs, checked BEFORE any
 commit exists to push. Every other path at the state ref's tip is carried
 untouched -- the ref holds a round's evidence beside the state docs -- and
 a tip whose content is already current is reported and left alone. The
@@ -30,7 +31,7 @@ body_push.sh's: commit-tree onto the ref's tip, parentless when the ref
 does not exist yet, a fast-forward afterwards -- never a force.
 
 Stateless like the other seat tools: every input is a flag, nothing about a
-session or a machine is hardcoded, stdlib only, and the three generators
+session or a machine is hardcoded, stdlib only, and the four generators
 are RUN, never re-implemented -- their logic lives in exactly one place.
 
 `beat` is the recurring half of tvofi's 2026-10-09 instruction that the state
@@ -80,10 +81,13 @@ import roster_sync  # noqa: E402  the roster-sync step `beat --apply` runs
 #: ref name, so a short name that happens to be a prefix matches nothing.
 WATCH_REF = "refs/heads/main"
 BEAT_INTERVAL = 300.0
-#: The three docs, one per generator. Under a round's state dir they are the
+#: The four docs, one per generator (the flow board is merge_throughput.py's
+#: `flow` subcommand, which lives beside this directory rather than in it).
+#: Under a round's state dir they are the
 #: WHOLE write surface: every other path at the state ref's tip -- a round's
 #: evidence, the older state docs -- is carried, never touched.
-DOC_NAMES = ("PLAN-TABLE.md", "RESUME-CURRENT.md", "NEXT-SESSION-PROMPT.md")
+DOC_NAMES = ("PLAN-TABLE.md", "FLOW-BOARD.md", "RESUME-CURRENT.md",
+             "NEXT-SESSION-PROMPT.md")
 
 
 class State(NamedTuple):
@@ -128,7 +132,7 @@ def run(cmd, cwd=None, env=None, input_text=None) -> str:
 # ----------------------------------------------------------------- generate
 def generate(repo: str, roster_args: list, checkout: str, pr_state: str,
              staging: Path, state_dir: str) -> dict:
-    """Run the three #1946 generators, in order, into staging.
+    """Run the four generators, in order, into staging.
 
     Returns {repo path: text} keyed by the write-set paths. The generators
     are subprocesses with their own flags -- never copied logic. The
@@ -139,22 +143,31 @@ def generate(repo: str, roster_args: list, checkout: str, pr_state: str,
     """
     resume_flags = (["--offline", "--pr-state", pr_state]
                     if pr_state else [])
+    # (script, doc name, subcommand, extra args, takes --repo). The flow board
+    # is merge_throughput.py's `flow` subcommand, so its script sits one
+    # directory up and its `--repo` is the checkout it reads -- never the
+    # OWNER/REPO the other generators carry in their header.
     plan = [
-        ("plan_table.py", "PLAN-TABLE.md", []),
-        ("resume_doc.py", "RESUME-CURRENT.md", resume_flags),
-        ("handover_prompt.py", "NEXT-SESSION-PROMPT.md", []),
+        (SEAT / "plan_table.py", "PLAN-TABLE.md", None, [], True),
+        (SEAT.parent / "merge_throughput.py", "FLOW-BOARD.md", "flow", [], False),
+        (SEAT / "resume_doc.py", "RESUME-CURRENT.md", None, resume_flags, True),
+        (SEAT / "handover_prompt.py", "NEXT-SESSION-PROMPT.md", None, [], True),
     ]
     out: dict = {}
-    for script, name, extra in plan:
+    for script, name, sub, extra, takes_repo in plan:
         target = staging / name
-        cmd = [sys.executable, str(SEAT / script), "--repo", repo, *roster_args,
-               "--out", str(target), *extra]
+        cmd = [sys.executable, str(script)]
+        if sub:
+            cmd.append(sub)
+        if takes_repo:
+            cmd += ["--repo", repo]
+        cmd += [*roster_args, "--out", str(target), *extra]
         r = subprocess.run(cmd, cwd=checkout, capture_output=True, text=True)
         if r.returncode != 0:
-            raise Refuse(f"{script} failed rc {r.returncode}: "
+            raise Refuse(f"{script.name} failed rc {r.returncode}: "
                          f"{(r.stderr or r.stdout).strip()[:400]}")
         if not target.exists() or not target.read_text(encoding="utf-8").strip():
-            raise Refuse(f"{script} produced no {name}")
+            raise Refuse(f"{script.name} produced no {name}")
         text = target.read_text(encoding="utf-8")
         out[f"{state_dir}/{name}"] = text
     return out
@@ -162,7 +175,7 @@ def generate(repo: str, roster_args: list, checkout: str, pr_state: str,
 
 # ------------------------------------------------------------------ the tree
 def check_write_set(staged: dict, write_set: tuple) -> None:
-    """The guarded write set, record_row's shape: anything outside the three
+    """The guarded write set, record_row's shape: anything outside the four
     state docs is refused, never skipped."""
     bad = sorted(p for p in staged if p not in write_set)
     if bad:
@@ -435,7 +448,7 @@ def parser(beat_mode: bool = False) -> argparse.ArgumentParser:
     p.add_argument("--pr-state",
                    help="JSON list of open pull requests; passed to "
                         "resume_doc with --offline (no network, no gh)")
-    p.add_argument("--mirror", help="directory the three files are copied to")
+    p.add_argument("--mirror", help="directory the four files are copied to")
     p.add_argument("--push", action="store_true",
                    help="push the state ref; without it this is a dry run")
     p.add_argument("--message")
@@ -612,15 +625,17 @@ def self_test() -> int:
            sorted(names) == sorted([*WRITE_SET, "docs/keep.md"]), names)
         show = lambda path: git("-C", str(bare), "show", f"{tip}:{path}")
         ok("plan table generated", "Swimlanes" in show(WRITE_SET[0]))
-        ok("resume generated", "## Roster" in show(WRITE_SET[1]))
-        ok("prompt generated", "Next-session prompt" in show(WRITE_SET[2])
-           and "R9-A" in show(WRITE_SET[2]))
-        ok("mirror carries exactly the three files",
+        ok("flow board generated", "# Flow board" in show(WRITE_SET[1])
+           and "Takt 1.0" in show(WRITE_SET[1]))
+        ok("resume generated", "## Roster" in show(WRITE_SET[2]))
+        ok("prompt generated", "Next-session prompt" in show(WRITE_SET[3])
+           and "R9-A" in show(WRITE_SET[3]))
+        ok("mirror carries exactly the four files",
            sorted(p.name for p in mirror.iterdir())
            == sorted(Path(p).name for p in WRITE_SET))
         ok("parent is the previous tip",
            state0 in git("-C", str(bare), "log", "--format=%P", "-1", tip))
-        # THE GUARD: a write outside the three files refuses, in both the
+        # THE GUARD: a write outside the four files refuses, in both the
         # direct check and a real write_tree call over the live tip.
         try:
             check_write_set({"dev/programme/HANDOVER.md": "x", WRITE_SET[0]: "ok"},
@@ -851,7 +866,7 @@ def self_test() -> int:
         # the orchestrator runs it. Two changes, each landed by the pass that
         # saw it, is what "continuously" means; a beat that exited after one
         # pass, or that never re-read the ref, fails the second wait. The
-        # deadline is generous (a pass runs three generators) and the process
+        # deadline is generous (a pass runs four generators) and the process
         # is terminated by the test, which is how this instrument is stopped.
         def wait_tip(want: str, seconds: float = 120.0) -> bool:
             end = time.time() + seconds

