# Review packet #3898
head: dbaca057a07250e002538b3176477c5046732746
base: d9100de781ec174960655fdab1a5af48c303d7bd

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: red
CodeQL id=139593978513 success
arch-score / arch-score id=139593644989 success
arm id=139593220582 skipped
budget-raise-gate / budget-raise-gate id=139593645027 success
cancel-superseded id=139593234816 success
codeql id=139593646429 skipped
codeql / Analyze (actions) id=139593622616 success
codeql / Analyze (javascript-typescript) id=139593622661 success
codeql / Analyze (python) id=139593622690 success
gate id=139594518229 failure
governance id=139593646439 skipped
governance / env-matrix id=139593622848 in_progress
governance / instrument-self-tests id=139593622682 in_progress
governance / policy-docs id=139593622681 in_progress
governance / record id=139593624655 skipped
governance / wave-script id=139593622894 success
hassfest id=139593646541 skipped
hassfest / hassfest id=139593622575 success
kernel-points id=139593646471 skipped
pr-contract id=139594520837 skipped
prelude id=139593234486 success
refresh id=139593234688 success
sweep-self id=139595449977 skipped
tests id=139593647043 skipped
tests / arch-instrument id=139594051699 in_progress
tests / briefs id=139593622950 success
tests / browser id=139594052104 in_progress
tests / closure-scope id=139593622956 success
tests / closures id=139594051774 in_progress
tests / coverage id=139594051904 in_progress
tests / fast (3.14) id=139594051758 in_progress
tests / mutation id=139593622838 success
tests / mutation-autofix id=139594122911 skipped
tests / mutation-pins id=139594122178 skipped
tests / nightly-ha id=139594053226 skipped
tests / nightly-status id=139593622896 failure
tests / replay id=139594055168 skipped
tests / typing id=139594051709 success
validate id=139593646112 skipped
validate / validate-hacs id=139593622637 success

## Refusals
introduced-red: unreadable: head governance / instrument-self-tests job 139593622682: in_progress has not concluded: an introduced red cannot be ruled out (fail closed)

## Advisories
required-wait: required context `gate` reads concluded failure at dbaca057a07250e002538b3176477c5046732746 in the digest, but merge_train.py classify --pr reads WAIT (pending: gate red: none): classify decides, as bus.sh's dispatch does, and a pending check never refuses

## carry_audit at the head
NOTE body item d6a310a0: dismissed:a one-round bootstrap of the scorecard's own window convention, printed unread rather than a guessed window.
NOTE body item da94e3c3: dismissed:no reader of that log in this group.
CARRY-AUDIT: 2 finding item(s): 2 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
ok         python3 -I tools/audit/seat/token_ledger.py --self-test
             `tools/audit/seat/token_ledger.py` is in the tree at this head
  ok         python3 -I tools/audit/seat/cloud_dispatch.py --self-test
             `tools/audit/seat/cloud_dispatch.py` is in the tree at this head
  ok         python3 -I tools/audit/seat/beat_jobs.py --self-test
             `tools/audit/seat/beat_jobs.py` is in the tree at this head
  ok         python3 -I tools/audit/check_scopes.py --repo . --self-test
             `tools/audit/check_scopes.py` is in the tree at this head
  ok         python3 -I tools/audit/seat/token_ledger.py collect --projects ~/.claude/projects/-home-user-heatpump-optimizer --out <scratch>/tokens.tsv --seat-class cloud
             `tools/audit/seat/token_ledger.py` is in the tree at this head
  ok         python3 tests/structure.py
             `tests/structure.py` is in the tree at this head

FIGURES: 6 resolved, 0 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
none

## Review scope: full (no verdict on verdict/<pr> names the reviewed head dbaca057a07250e002538b3176477c5046732746, so there is no finding to confirm resolved)

## Three-dot diff
diff --git a/.github/workflows/governance.yml b/.github/workflows/governance.yml
index eb2fbfe6f6..d34105c374 100644
--- a/.github/workflows/governance.yml
+++ b/.github/workflows/governance.yml
@@ -540,6 +540,17 @@ jobs:
         if: steps.scope.outputs.round-metrics == 'true'
         run: python3 -I tools/audit/seat/round_metrics.py --self-test
 
+      # Decision 0018's token ledger (R11-PRE-TOKEN-LEDGER): usage counted once per
+      # response, every field apart, keyed by the seat key, and the round_metrics
+      # tokens line unread while a seat class has no row, offline.
+      - name: Show the token ledger keying usage per seat and leaving an unledgered class unread
+        id: token-ledger
+        if: steps.scope.outputs.token-ledger == 'true'
+        run: |
+          set -euo pipefail
+          python3 -I tools/audit/seat/token_ledger.py --self-test | tee "$RUNNER_TEMP/token-ledger-self-test.txt"
+          grep -Eq '^token_ledger self-test: [1-9][0-9]* passed, 0 failed$' "$RUNNER_TEMP/token-ledger-self-test.txt"
+
       # Decision 0018 section 5's two held-out checks (R11-PRE-ROUND-METRICS):
       # planted-defect recall's refusals and its count after the judge, and the
       # two-finder overlap estimate; each holds an empty input to unread, never
diff --git a/dev/programme/delivery/3898.md b/dev/programme/delivery/3898.md
new file mode 100644
index 0000000000..3a3a058b19
--- /dev/null
+++ b/dev/programme/delivery/3898.md
@@ -0,0 +1 @@
+- [#3898](https://github.com/tvofi/heatpump_optimizer/pull/3898) — **open**, R11-PRE-TOKEN-LEDGER: per-seat token ledger summed from transcripts, read by the scorecard (R11-PRE-TOKEN-LEDGER)
diff --git a/tests/closures.json b/tests/closures.json
index 244e2086d3..68b29d6c61 100644
--- a/tests/closures.json
+++ b/tests/closures.json
@@ -4614,6 +4614,7 @@
    "tools/audit/seat/sweep_gantt.py",
    "tools/audit/seat/sweep_render.py",
    "tools/audit/seat/tmp_paths.py",
+   "tools/audit/seat/token_ledger.py",
    "tools/audit/seat/toolchain.py",
    "tools/audit/seat/toolchain_selftest.py",
    "tools/audit/seat/topic_grammar.py",
diff --git a/tools/audit/check_scopes.py b/tools/audit/check_scopes.py
index 612e044bdb..f05ac810da 100644
--- a/tools/audit/check_scopes.py
+++ b/tools/audit/check_scopes.py
@@ -41,6 +41,9 @@ unmarked_groups} and exits: the accepted cards that gate no finder and are unmer
 the open groups of the roster (roster_lib's reader, or --roster-ref) whose `gates_finders` is not
 true; rc 1, with an `UNMARKED <card|group>` line, while an accepted card or open group carries no
 boolean. Run when the finders finish, it is the architect's input. --self-test drives a complete record (passes) and one perturbation per rule.
+--tokens FILE (with --round; default $HPO_STATE_DIR/scorecard/tokens.tsv, token_ledger.py's) refuses
+an evaluator or reviewer named as a `seat` of a row in round N-1's window; no ledger, a seat class
+with no row in the window or a seat row with no key prints unread.
 The record also needs: an approving review at a commit in --ref's history whose EVALUATION.json
 graded the same objects, a ruling on every decided card, an accepted card's commit after that review
 and changing the card's file, reads that are numbers with a tracked enumerator, NO-READs that name
@@ -55,7 +58,7 @@ and `UNREADABLE <axis>: <why>` when a source is missing or an axis yields no lev
 the identifiers a module uses outside its imports, less each one its calls mark required and never
 optional: a key no install can leave out, or one no step presents, is no two-level axis.
 """
-import argparse, ast, contextlib, copy, importlib.util, io, itertools, json, math, re, subprocess, sys, tempfile
+import argparse, ast, contextlib, copy, csv, datetime, importlib.util, io, itertools, json, math, os, re, subprocess, sys, tempfile, time
 from pathlib import Path
 
 sys.path.insert(0, str(Path(__file__).resolve().parent / "seat"))
@@ -298,6 +301,16 @@ def norm(s):
     return re.sub(r"[\W_]+", "", str(s).casefold())
 
 
+def ledger_gaps(path, ev, rows, a, b):
+    """Decision 0018 section 6: an evaluator or reviewer seat that is a seat of the graded round's
+    token ledger (token_ledger.py's `seat` column, rows with a <= t < b) worked the round it
+    grades. Names compare as `norm` spells them; a `-` seat is no seat."""
+    at = lambda t: datetime.datetime.fromisoformat(t.replace("Z", "+00:00")).timestamp()
+    seats = {norm(r.get("seat", "")) for r in rows if r.get("t") and a <= at(r["t"]) < b} - {""}
+    return [f"{path} {k} {ev[k]!r} is a seat in the graded round's token ledger: it worked the round it grades"
+            for k in ("evaluator", "reviewer") if full(ev.get(k)) and norm(ev[k]) in seats]
+
+
 def enumerates(cmd, tree):
     """The first path-like token of an enumerator command is a tracked script.
     A design choice: a tracked document is no enumerator, whatever follows it."""
@@ -838,6 +851,14 @@ def evaluation_self_test(tree, show):
         "B1 a disguised orchestrator or the same seat respelled is refused":
             all(only(run(edit(lambda c: c.update(**{k: v}))), "two seats") for k, v in (
                 ("evaluator", "orchestrator-r10"), ("evaluator", "the orchestrator"), ("reviewer", "Orchestrator"), ("reviewer", "Evaluator R8"))),
+        "B1 an evaluator or reviewer that is a seat of the graded round's token ledger is refused, either spelling, at the window's first second":
+            ledger_gaps("E", good, [{"t": "2026-01-02T00:00:00Z", "seat": "Evaluator_R8"}], 1767312000, 2e9)
+            == ["E evaluator 'evaluator-r8' is a seat in the graded round's token ledger: it worked the round it grades"]
+            and len(ledger_gaps("E", good, [{"t": "2026-01-02T00:00:00Z", "seat": "plan-review-r8"}], 1767312000, 2e9)) == 1,
+        "B1 null: the same seat outside the window, another seat, or a `-` seat is no gap":
+            ledger_gaps("E", good, [{"t": "2026-01-02T00:00:00Z", "seat": "evaluator-r8"}], b=1767312000, a=0) == []
+            and ledger_gaps("E", good, [{"t": "2026-01-02T00:00:00Z", "seat": "fixer-r8-x"}, {"t": "2026-01-02T00:00:00Z", "seat": "-"},
+                                        {"t": "2026-01-02T00:00:01Z", "seat": "evaluator-r8"}], b=1767312001, a=0) == [],
         "B2 a review that is no approve verdict is refused":
             only(run(edit(lambda c: c.pop("review"))), "review is not an approve") and only(run(edit(lambda c: c["review"].update(verdict="revise"))), "review is not an approve"),
         "B2 a review sha outside the ref's history is refused": only(run(edit(lambda c: c["review"].update(sha="zzz"))), "is not a commit in the ref"),
@@ -1030,6 +1051,8 @@ def main():
     ap.add_argument("--self-test", action="store_true")
     ap.add_argument("--seat", help="print the cells this seat (D<k>-s<n>) owns and exit")
     ap.add_argument("--round", type=int, help="also refuse this round's start without its start evaluation")
+    ap.add_argument("--tokens", help="with --round: the token ledger (default $HPO_STATE_DIR/scorecard/tokens.tsv) whose "
+                    "graded-round rows refuse an evaluator or reviewer seat")
     ap.add_argument("--population", action="store_true", help="print the install population's levels read at --ref and exit")
     ap.add_argument("--open-cards", action="store_true",
                     help="with --round: print, as JSON, P3's input (open non-gating cards at --ref, open non-gating roster groups) and exit; rc 1 naming any unmarked card or group")
@@ -1282,6 +1305,12 @@ def main():
         run_r1 = default_run(scopes, "--round", "1")
         cov["--round exits 1 with no evaluation in the tree"] = (run_r1.returncode == 1 and cited in run_r1.stdout
             and "FAIL start evaluation" in run_r1.stdout and "round1/EVALUATION.json is not in the tree" in run_r1.stdout)
+        # main()'s --round reads the token ledger (0018 section 6): run whole, an absent ledger
+        # prints unread whatever the tree's tags; round_ledger_gaps' window and rows below.
+        with tempfile.TemporaryDirectory() as nod:
+            cov["--round reads its token ledger: an absent one prints unread"] = "LEDGER unread: no token ledger (--tokens)" in (
+                default_run(scopes, "--round", "11", "--tokens", str(Path(nod) / "tokens.tsv")).stdout)
+        cov.update(ledger_round_self_test())
         run_oc = default_run(scopes, "--round", "1", "--open-cards")
         cov["--open-cards refuses a round with no evaluation, never an empty list"] = (run_oc.returncode == 2
             and "round1/EVALUATION.json tracked" in run_oc.stderr and "open_cards" not in run_oc.stdout)
@@ -1310,6 +1339,7 @@ def main():
     if a.round is not None:
         beside = []
         gaps = evaluation_gaps(a.round, tree, show, merged, anc, changed, beside)
+        gaps += round_ledger_gaps(a, show, tree)
         print(f"{'ok' if not gaps else 'FAIL'} start evaluation round={a.round}: {len(gaps)} gap(s), {len(beside)} card(s) beside the finders")
         for g in gaps:
             print(f"   {g}")
@@ -1318,5 +1348,93 @@ def main():
         ok = ok and not gaps
     sys.exit(0 if ok else 1)
 
+def ledger_round_self_test():
+    """round_ledger_gaps over a scratch repo tagged v9.0.0 (2026-01-01) and v10.0.0 (2026-01-03):
+    round 11's record grades round 10, the window [v9.0.0, v10.0.0)."""
+    from throwaway_git import throwaway_git_init  # main() put tests/ on the path
+    rec, arms = records(11)[1], {}
+    ev = {"evaluator": "r11-evaluator", "reviewer": "r11-evaluation-reviewer"}
+    with tempfile.TemporaryDirectory() as d:
+        env = throwaway_git_init(d, "-q")
+        for n, stamp in ((9, 1767225600), (10, 1767398400)):
+            subprocess.run(["git", "-C", d, "commit", "-q", "--allow-empty", "-m", f"v{n}"],
+                           env=dict(env, GIT_COMMITTER_DATE=f"{stamp} +0000", GIT_AUTHOR_DATE=f"{stamp} +0000"))
+            subprocess.run(["git", "-C", d, "tag", f"v{n}.0.0"], env=env)  # a failure leaves no window: the arms below fail
+        led = Path(d) / "tokens.tsv"
+
+        whole = [("2026-01-01T12:00:00Z", "-", "orchestrator"), ("2026-01-01T12:00:00Z", "cloud-x", "cloud")]
+
+        def run(rows, tree=frozenset({rec}), tokens=str(led), classes=whole):
+            led.write_text("t\tseat_class\tseat\n" + "".join(f"{t}\t{c}\t{s}\n" for t, s, c in
+                                                                [(*r, "local") for r in rows] + list(classes)))
+            with contextlib.redirect_stdout(io.StringIO()) as out:
+                got = round_ledger_gaps(argparse.Namespace(round=11, tokens=tokens, repo=d), lambda p: json.dumps(ev), tree)
+            return got, out.getvalue()
+        first, last = run([("2026-01-01T00:00:00Z", "r11-evaluator")]), run([("2026-01-02T23:59:59Z", "R11 evaluation reviewer")])
+        arms["--round: the evaluator a seat at the graded window's first second is refused"] = (
+            [g.split(" is a seat")[0] for g in first[0]] == [f"{rec} evaluator 'r11-evaluator'"])
+        arms["--round: the reviewer, respelled, a seat at its last second is refused"] = (
+            [g.split(" is a seat")[0] for g in last[0]] == [f"{rec} reviewer 'r11-evaluation-reviewer'"])
+        arms["--round null: a seat before or at the window's end, or another seat, is no gap"] = run(
+            [("2025-12-31T23:59:59Z", "r11-evaluator"), ("2026-01-03T00:00:00Z", "r11-evaluator"),
+             ("2026-01-02T00:00:00Z", "fixer-r11-x")]) == ([], "")
+        arms["--round null: a round with no record in the tree reads no ledger"] = run(
+            [("2026-01-01T00:00:00Z", "r11-evaluator")], tree=frozenset()) == ([], "")
+        no_cloud = run([("2026-01-02T00:00:00Z", "fixer-r11-x")], classes=whole[:1])
+        arms["--round: a seat class with no row in the window prints unread (review/3898: a silent pass)"] = (
+            no_cloud[0] == [] and "LEDGER unread: seat classes with no row in the window: cloud" in no_cloud[1])
+        # tokens.tsv is cumulative: a class's row from before the window is no row in it (review/3898 round 2).
+        old_cloud = run([("2026-01-02T00:00:00Z", "fixer-r11-x")],
+                        classes=whole[:1] + [("2025-12-31T12:00:00Z", "cloud-x", "cloud")])
+        arms["--round: a seat class whose only row predates the window prints unread"] = (
+            old_cloud[0] == [] and "LEDGER unread: seat classes with no row in the window: cloud" in old_cloud[1])
+        unkeyed = run([("2026-01-02T00:00:00Z", "-"), ("2026-01-02T00:00:00Z", "r11-evaluator")])
+        arms["--round: an unkeyed seat row prints unread, and a keyed seat found is still refused"] = (
+            "LEDGER unread: 1 seat row(s) with no seat key" in unkeyed[1] and len(unkeyed[0]) == 1)
+        arms["--round null: every class keyed in the window, an orchestrator's `-` included, prints no unread"] = (
+            run([("2026-01-02T00:00:00Z", "fixer-r11-x")]) == ([], ""))
+        gone = run([("2026-01-01T00:00:00Z", "r11-evaluator")], tokens=str(Path(d) / "none.tsv"))
+        arms["--round: an absent ledger prints unread, no gap"] = gone[0] == [] and "LEDGER unread: no token ledger" in gone[1]
+    return arms
+
+
+def round_ledger_gaps(a, show, tree):
+    """`ledger_gaps` over --tokens (default $HPO_STATE_DIR/scorecard/tokens.tsv) in round
+    --round minus one's window (round_metrics.round_window); an absent ledger or window is
+    printed unread, no gap: the refusal exists once the ledger does (0018 section 6)."""
+    path = records(a.round)[1]
+    if path not in tree:
+        return []
+    src = a.tokens or (os.environ.get("HPO_STATE_DIR") and str(Path(os.environ["HPO_STATE_DIR"]) / "scorecard" / "tokens.tsv"))
+    spec = importlib.util.spec_from_file_location("round_metrics", Path(__file__).resolve().parent / "seat" / "round_metrics.py")
+    rm = importlib.util.module_from_spec(spec)
+    spec.loader.exec_module(rm)
+    win = rm.round_window(Path(a.repo), a.round - 1, time.time())
+    try:
+        rows = list(csv.DictReader(io.StringIO(Path(src).read_text()), delimiter="\t")) if src else None
+    except OSError:
+        rows = None
+    if rows is None or win is None:
+        print(f"   LEDGER unread: {'no token ledger (--tokens)' if rows is None else f'no tag v{a.round - 2}.0.0 opens round {a.round - 1}'}; "
+              "an evaluator or reviewer seat of the graded round is not checked")
+        return []
+    why = ledger_unread(rows, win[0], win[1], rm.SEAT_CLASSES)
+    if why:  # a seat found is still refused; its absence is not read
+        print(f"   LEDGER unread: {why}; an evaluator or reviewer seat of the graded round is not checked whole")
+    return ledger_gaps(path, json.loads(show(path)), rows, win[0], win[1])
+
+
+def ledger_unread(rows, a, b, classes):
+    """Why the window's rows cannot show a seat absent, or "": a seat class (round_metrics.SEAT_CLASSES)
+    with no row, or a non-orchestrator row whose `seat` is `-` (an unkeyed local spawn, whose brief
+    no rule keys). Absence read off such a ledger would be a partial, which 0018 forbids."""
+    at = lambda t: datetime.datetime.fromisoformat(t.replace("Z", "+00:00")).timestamp()
+    win = [r for r in rows if r.get("t") and a <= at(r["t"]) < b]
+    missing = [c for c in classes if c not in {r.get("seat_class") for r in win}]
+    unkeyed = sum(r.get("seat_class") != "orchestrator" and r.get("seat", "-") in ("-", "") for r in win)
+    return "; ".join(([f"seat classes with no row in the window: {', '.join(missing)}"] if missing else [])
+                     + ([f"{unkeyed} seat row(s) with no seat key"] if unkeyed else []))
+
+
 if __name__ == "__main__":
     main()
diff --git a/tools/audit/seat/INSTRUMENTS.md b/tools/audit/seat/INSTRUMENTS.md
index c9771d97bb..a4e26f2104 100644
--- a/tools/audit/seat/INSTRUMENTS.md
+++ b/tools/audit/seat/INSTRUMENTS.md
@@ -128,6 +128,7 @@ standing-seat liveness step keep the seats alive.
 - [`selftest_absorb.py`](instruments/selftest_absorb.py.md) — the actor half of main's self-test table repair: absorbs the `selftest-closures` artifacts of main's red or owed push runs at main's tip and force-pushes the one standing ref `handoff/selftest-absorb` (beatd row `selftest-absorb`); `verify` is that pull request's mechanical review
 - [`scorecard.py`](instruments/scorecard.py.md) — report-only convergence lines (gate and run health, first-verdict yield, machinery blocks, train skips, hotfix share, size, escapes, detection delay, seat cost, and round_metrics.py's reads over the open round), each but the hotfix naming measure held to a null control, written daily to `S/beatd/scorecard.txt`
 - [`round_metrics.py`](instruments/round_metrics.py.md) — decision 0018's flow reads per round and per week (merges by class, lead_time from the roster-entry commit per class, product_green with the gate's check count, restore, runner seconds and tokens per merge), unread on no input, and the producer of the scorecard's inputs
+- [`token_ledger.py`](instruments/token_ledger.py.md) — decision 0018's token ledger: usage per seat from the Claude transcripts, every field apart, keyed by the seat key each dispatch writes, into the `tokens.tsv` round_metrics.py reads; the cloud class unread until its usage leaves the container
 - [`toolchain.py`](instruments/toolchain.py.md) — the stable tools ref `toolchain/stable`: `behind` counts what the ref holds over a checkout on the seat paths, `promote` moves it along main to the newest commit whose push run reads MACHINERY green, and prints `PROMOTE-HELD` when the newest three past it do not
 - [`plant_recall.py`](instruments/plant_recall.py.md) — plants a held-out seat's objective bugs into the baseline export before the finders, refusing an unsound plant list, and counts recall after the judge (found / planted, whole, per space and per kind), unread on no input
 - [`finder_overlap.py`](instruments/finder_overlap.py.md) — seats a twin finder on one scopes.json seat's universe and estimates the bugs there from the two seats' judged-real overlap, with both models, unread on no input
diff --git a/tools/audit/seat/beat_jobs.py b/tools/audit/seat/beat_jobs.py
index 7f793e1cf0..8f0b15a332 100644
--- a/tools/audit/seat/beat_jobs.py
+++ b/tools/audit/seat/beat_jobs.py
@@ -147,7 +147,11 @@ ROWS (the job table's `interval_s` in brackets):
                      owner's thresholds, 2026-11-07); a held breach re-prints its
                      first line, so it is new once per trip. A line suggests; the
                      orchestrator decides. `bottleneck: UNREADABLE` on a non-zero rc.
-  scorecard [86400]  round_metrics.py `produce --dir S/scorecard --repo <checkout>
+  scorecard [86400]  token_ledger.py `collect --out S/scorecard/tokens.tsv --projects <dir>...`
+                     (the overlay's `claude_projects`, else the checkout's project dir
+                     under ~/.claude/projects; a failure is `scorecard: UNREADABLE
+                     token_ledger rc=<n>` and the rest still runs), then
+                     round_metrics.py `produce --dir S/scorecard --repo <checkout>
                      --gh-repo <repo>` refreshes the inputs (one REST batch), then
                      scorecard.py `report --dir S/scorecard --train-log <train_log>
                      [--sweep-record <sweep_record>]` into `S/beatd/scorecard.txt`
@@ -772,18 +776,31 @@ def scorecard(ctx: Ctx) -> None:
     got = ctx.need("scorecard", "train_log", "repo")
     if got is None:
         return
+    rc, _, err = ctx.py("tools/audit/seat/token_ledger.py", "collect", "--out", str(ctx.state / "scorecard" / "tokens.tsv"),
+                        *[a for p in claude_projects(ctx) for a in ("--projects", p)])
+    lines = [] if rc == 0 else [f"scorecard: UNREADABLE token_ledger rc={rc}: {(err.strip().splitlines() or [''])[-1]}"]
     rc, _, err = ctx.py("tools/audit/seat/round_metrics.py", "produce", "--dir", str(ctx.state / "scorecard"),
                         "--repo", str(ctx.repo), "--gh-repo", got[1])
     if rc != 0:
-        return write_job(ctx, "scorecard", [f"scorecard: UNREADABLE produce rc={rc}: {(err.strip().splitlines() or [''])[-1]}"])
+        return write_job(ctx, "scorecard", lines + [f"scorecard: UNREADABLE produce rc={rc}: {(err.strip().splitlines() or [''])[-1]}"])
     args = ["report", "--dir", str(ctx.state / "scorecard"), "--train-log", got[0], "--repo", str(ctx.repo)]
     if ctx.overlay.get("sweep_record"):
         args += ["--sweep-record", str(ctx.overlay["sweep_record"])]
     rc, out, err = ctx.py("tools/audit/seat/scorecard.py", *args)
     if rc != 0 or not out.strip():
-        return write_job(ctx, "scorecard", [f"scorecard: UNREADABLE rc={rc}: {(err.strip().splitlines() or [''])[-1]}"])
+        return write_job(ctx, "scorecard", lines + [f"scorecard: UNREADABLE rc={rc}: {(err.strip().splitlines() or [''])[-1]}"])
     atomic(ctx.state / "beatd" / "scorecard.txt", out)
-    write_job(ctx, "scorecard", [])
+    write_job(ctx, "scorecard", lines)
+
+
+def claude_projects(ctx: Ctx) -> list[str]:
+    """The Claude project directories whose transcripts the token ledger reads: the overlay's
+    `claude_projects` (one path or a list), else the one the client names after the checkout
+    (every character outside [A-Za-z0-9] a `-`) under ~/.claude/projects."""
+    got = ctx.overlay.get("claude_projects")
+    if got:
+        return [str(p) for p in ([got] if isinstance(got, str) else got)]
+    return [str(Path.home() / ".claude" / "projects" / re.sub(r"[^A-Za-z0-9]", "-", str(ctx.repo.resolve())))]
 
 
 def toolchain_promote(ctx: Ctx) -> None:
diff --git a/tools/audit/seat/beat_jobs_selftest.py b/tools/audit/seat/beat_jobs_selftest.py
index 9e87e5f11c..c49816bbdb 100644
--- a/tools/audit/seat/beat_jobs_selftest.py
+++ b/tools/audit/seat/beat_jobs_selftest.py
@@ -606,9 +606,26 @@ def cases(bj) -> dict[str, bool]:
     c, f = fresh(answers={"scorecard.py": (0, sc_out, "")})
     bj.scorecard(c)
     pr = next((x for x in f.calls if any(a.endswith("round_metrics.py") for a in x)), [])
-    res["scorecard: the producer runs first, handed produce, the dir, the checkout and the overlay's repo"] = (
-        f.calls and f.calls[0] == pr and "produce" in pr and arg(pr, "--dir") == str(c.state / "scorecard")
+    tl = next((x for x in f.calls if any(a.endswith("token_ledger.py") for a in x)), [])
+    res["scorecard: the token ledger runs first, into the producer's dir, reading the checkout's project dir"] = (
+        f.calls and f.calls[0] == tl and "collect" in tl and arg(tl, "--out") == str(c.state / "scorecard" / "tokens.tsv")
+        and arg(tl, "--projects") == bj.claude_projects(c)[0])
+    res["scorecard: the default project dir is the client's name for the checkout, every non-alphanumeric a `-`"] = (
+        bj.claude_projects(type("C", (), {"overlay": {}, "repo": Path("/srv/ck/heat_pump.x")})())
+        == [str(Path.home() / ".claude" / "projects" / "-srv-ck-heat-pump-x")])
+    res["scorecard: the producer runs next, handed produce, the dir, the checkout and the overlay's repo"] = (
+        f.calls[1:2] == [pr] and "produce" in pr and arg(pr, "--dir") == str(c.state / "scorecard")
         and arg(pr, "--repo") == str(c.repo) and arg(pr, "--gh-repo") == "o/r")
+    c, f = fresh(overlay={"repo": "o/r", "train_log": "/x/t.log", "claude_projects": ["/p/a", "/p/b"]},
+                 answers={"token_ledger.py": (2, "", "token_ledger: refused: no project directory: /p/a\n"),
+                          "scorecard.py": (0, sc_out, "")})
+    bj.scorecard(c)
+    tl = next((x for x in f.calls if any(a.endswith("token_ledger.py") for a in x)), [])
+    res["scorecard: the overlay's claude_projects are each handed on; a failed ledger is UNREADABLE and the report "
+        "still runs (its tokens line prints unread)"] = (
+        [tl[i + 1] for i, a in enumerate(tl) if a == "--projects"] == ["/p/a", "/p/b"]
+        and digest(c) == "scorecard: UNREADABLE token_ledger rc=2: token_ledger: refused: no project directory: /p/a\n"
+        and (c.state / "beatd" / "scorecard.txt").exists())
     c, f = fresh(answers={"round_metrics.py": (1, "", "Traceback\nApiError: 502\n"), "scorecard.py": (0, sc_out, "")})
     bj.scorecard(c)
     res["scorecard: a failed producer is UNREADABLE and the report does not run on stale inputs"] = (
@@ -1423,9 +1440,13 @@ MUTANTS = {
                        "ci-attempt: the #3287 window fires once per looping run, naming it and its pull request"),
     "ci_attempt_pr": ('or "no pull request"', 'and "no pull request"',
                       "ci-attempt: the #3287 window fires once per looping run, naming it and its pull request"),
-    "scorecard_produce_rc": ('        return write_job(ctx, "scorecard", [f"scorecard: UNREADABLE produce rc=',
-                             '        pass  # write_job(ctx, "scorecard", [f"scorecard: UNREADABLE produce rc=',
+    "scorecard_produce_rc": ('        return write_job(ctx, "scorecard", lines + [f"scorecard: UNREADABLE produce rc=',
+                             '        pass  # write_job(ctx, "scorecard", lines + [f"scorecard: UNREADABLE produce rc=',
                              "scorecard: a failed producer is UNREADABLE and the report does not run on stale inputs"),
+    "scorecard_tokens_rc_dropped": ('    lines = [] if rc == 0 else [f"scorecard: UNREADABLE token_ledger rc=',
+                                    '    lines = [] if True else [f"scorecard: UNREADABLE token_ledger rc=',
+                                    "scorecard: the overlay's claude_projects are each handed on; a failed ledger is UNREADABLE and the report "
+                                    "still runs (its tokens line prints unread)"),
     "scorecard_rc_clean": ('    if rc != 0 or not out.strip():\n        return write_job(ctx, "scorecard"',
                            '    if not out.strip():\n        return write_job(ctx, "scorecard"',
                            "scorecard: a failed instrument is UNREADABLE, never written"),
diff --git a/tools/audit/seat/cloud_dispatch.py b/tools/audit/seat/cloud_dispatch.py
index 790c06afe8..cfe8b75bbc 100644
--- a/tools/audit/seat/cloud_dispatch.py
+++ b/tools/audit/seat/cloud_dispatch.py
@@ -87,6 +87,7 @@ def _sibling(name: str):
 ref_privacy = _sibling("ref_privacy")
 roster_lib = _sibling("roster_lib")
 proof_watch = _sibling("proof_watch")  # the bus-nonce line's one Python reader
+token_ledger = _sibling("token_ledger")  # the seat-key line every payload carries
 HOME = re.compile(ref_privacy.HOME_DIR)
 LOWER_HEX = frozenset("0123456789abcdef")
 
@@ -384,9 +385,13 @@ def _prompt(role: str, repo: str, pr: str, head: str, topic: str, nonce: str, br
 
 def render(role: str, head: str, *, env_id: str, model: str, repo: str, pr: str = "",
            topic: str = "", nonce: str = "", brief: str = "", publish_ref: str = "",
-           design: str = "", pin: str = "", reviewed_head: str = "", verdict: tuple = ()) -> dict:
+           design: str = "", pin: str = "", reviewed_head: str = "", verdict: tuple = (),
+           group: str = "") -> dict:
     """The payload; with `publish_ref`, its event is the stub naming PROMPT.md at commit
-    `pin` of that ref (`publish_seat`)."""
+    `pin` of that ref (`publish_seat`). The event's first line, the stub's or the whole
+    prompt's, ends with the seat key (`token_ledger.header`: `group`, the role, the model,
+    the seat's dispatch name), which the token ledger keys the seat's usage by: every cloud
+    seat is fired with a `render` event, so no cloud dispatch path writes an unkeyed one."""
     if role not in ROLES:
         raise Refusal(f"role must be one of {', '.join(ROLES)}")
     if not is_head(head or ""):
@@ -413,6 +418,14 @@ def render(role: str, head: str, *, env_id: str, model: str, repo: str, pr: str
         raise Refusal("a published seat's stub needs the 40-hex commit holding its PROMPT.md")
     text = (_pointer(role, repo, pr, head, topic, nonce, publish_ref, pin) if publish_ref
             else _prompt(role, repo, pr, head, topic, nonce, brief, design, reviewed_head, verdict))
+    # The key ends the first line of the event, stub or whole prompt alike: the event is the
+    # seat's first user message, the one line token_ledger.read_transcript reads it from.
+    try:
+        key = token_ledger.header(group=group, role=role, model=model, seat=f"{role}-{topic or 'rev-' + pr}")
+    except token_ledger.Refusal as e:
+        raise Refusal(str(e))
+    first, _, rest = text.partition("\n")  # the first line's end: line 2 stays the setup line
+    text = f"{first} {key}\n{rest}"
     payload = {"job_config": {"ccr": {
         "environment_id": env_id,
         "session_context": {
@@ -558,6 +571,29 @@ def part_line(group_id: str, pending: list[int], part: int) -> str:
             "dispatched at this part's handoff; answer none of them")
 
 
+PART_LINE = re.compile(r"^Part \d+ of \d+: build carries [0-9+-]+;.*$", re.M)
+
+
+def inherit_part(prev_prompt: str, brief: str) -> str:
+    """`brief`, plus the generated part line of the prompt it re-dispatches when it holds
+    none. A repair of a split part is dispatched on the flag path with a hand brief: without
+    the line, review_packet's `part_carries` read no part and its handoff demanded every
+    roster carry (R11-PRE-TOOLCHAIN-PIN's repair, a546de28d0, against f0c093cebc's part 1)."""
+    m = PART_LINE.search(prev_prompt or "")
+    if not m or PART_LINE.search(brief):
+        return brief
+    return brief.rstrip("\n") + "\n\n" + m.group(0) + "\n"
+
+
+def _prev_prompt(repo_dir: str, ref: str) -> str:
+    """PROMPT.md at the tip of `ref` on origin, or "" when the ref holds none."""
+    tip = _tip(repo_dir, ref)
+    if not tip:
+        return ""
+    r = subprocess.run(["git", "-C", repo_dir, "show", f"{tip}:PROMPT.md"], capture_output=True, text=True)
+    return r.stdout if r.returncode == 0 else ""
+
+
 def dispatch_ref(role: str, topic: str, pr: str) -> str:
     """`dispatch/<role>-<topic>`, or `dispatch/<role>-rev-<PR>` for a seat with no topic."""
     key = topic or (f"rev-{pr}" if pr.isdigit() else "")
@@ -696,7 +732,7 @@ def dispatch_group(role: str, group_id: str, model: str, *, repo_dir: str = ".",
             verdict = (vtip[0], _git(repo_dir, "show", f"{vtip[0]}:verdict.md").split("\n", 1)[0],
                        int(_git(repo_dir, "rev-list", "--count", vtip[0]).strip()))
     args = dict(design=design, verdict=verdict, env_id=known["env_id"], model=model, repo=roster.get("repo") or known["repo"],
-                pr=pr, topic=topic,
+                pr=pr, topic=topic, group=group_id,
                 brief=group_brief(group, roster, fixer=role == "fixer")
                 + "".join(f"\n{ln}\n" for ln in (dline, pline) if ln),
                 reviewed_head=reviewed_head)
@@ -933,8 +969,10 @@ def _group_checks(check) -> None:
         check("the stub keeps the seat line and the footer ban inline; PROMPT.md is the whole prompt",
               ptr.startswith("CLOUD FIXER seat for owner/name, topic r10-x, at head " + tip + ".")
               and FOOTER_BAN in ptr and msg.startswith("CLOUD FIXER") and msg not in ptr)
-        check("the stub payload is far smaller than the prompt: under 1 KB whole, the brief absent, the SHA present",
-              len(fetched(line, "PAYLOAD.json")) < 1024 < len(msg) and "Fix the thing" not in ptr and pin in ptr)
+        check("the stub payload is far smaller than the prompt: under 1 KB whole less its seat key, the brief absent, "
+              "the SHA present",
+              len(fetched(line, "PAYLOAD.json")) - len(" " + (token_ledger.HEADER.search(ptr) or re.search("$", ptr)).group(0))
+              < 1024 < len(msg) and "Fix the thing" not in ptr and pin in ptr)
         check("without --publish the flag path is unchanged: the whole prompt in its event, nothing published",
               rc0 == 0 and content(plain.getvalue()) == msg)
         check("the roster brief is inlined and the roster tip is the head",
@@ -944,6 +982,13 @@ def _group_checks(check) -> None:
                                                               "Legacy.\n\nAfter: none\n"))
         # CARRY 4 (tvofi 2026-11-01 card 2): the live consumers and the class enumeration, generated.
         ptext = fetched(dispatch("R10-PROD"), "PROMPT.md")
+        pkey = token_ledger.parse_header(ptext.splitlines()[0])
+        pstub = content(fetched("dispatch/fixer-r10-prod", "PAYLOAD.json"))
+        check("a group seat's prompt keys it, on its first line, by group, role, model and dispatch name, and its "
+              "stub, the seat's first user message, ends its first line with the same key (R11-PRE-TOKEN-LEDGER; "
+              "review/3898: the stub carried none)",
+              pkey is not None and (pkey["group"], pkey["role"], pkey["seat"]) == ("R10-PROD", "fixer", "fixer-r10-prod")
+              and token_ledger.parse_header(pstub.splitlines()[0]) == pkey)
         check("a fixer's brief lists the live consumers (after-edged and file-sharing) as the only valid Carry targets, not the done one",
               "Valid `Carry:` targets (live consumers of R10-PROD: groups after it or sharing its files): R10-CONS, R10-SHARE\n" in ptext
               and "R10-DONEC" not in ptext.split("Valid `Carry:` targets")[1])
@@ -976,6 +1021,14 @@ def _group_checks(check) -> None:
             check("--part 2 renders the topic <topic>-p2 and one generated line naming carries 5-9",
                   p2 == "dispatch/fixer-r10-split-p2" and "topic r10-split-p2, at head" in p2text
                   and sum(ln == pline for ln in p2text.splitlines()) == 1 and p2text.endswith(pline + "\n"))
+            (work / "repair.txt").write_text("Repair of the part's red head.\n")
+            with contextlib.chdir(work), contextlib.redirect_stdout(io.StringIO()):
+                rrc = main(["--role", "fixer", "--head", tip, "--topic", "r10-split-p2", "--brief", str(work / "repair.txt"),
+                            "--env-id", "env_x", "--model", "m-1", "--repo", "owner/name", "--publish"])
+            rtext = fetched(p2, "PROMPT.md")
+            check("a flag-path repair of part 2 on its own ref keeps the part's line, after its hand brief (carry: "
+                  "R11-PRE-TOOLCHAIN-PIN's repair held none)",
+                  rrc == 0 and "Repair of the part's red head." in rtext and rtext.endswith("\n\n" + pline + "\n"))
             cwhy = why_any("R10-CLASH", part=2)
             awhy = why_any("R10-CLASH", part=3)
             check("a part whose topic is another group's id (R10-CLASH-P2) or branch (R10-ALIAS) refuses naming it; "
@@ -1426,6 +1479,16 @@ def self_test() -> int:
           and "role_pack.py" not in prompts["probe"])
     check("the fixer reads its role file, not CLAUDE.md, which the harness already loaded",
           "dev/governance/roles/fixer.md" in prompts["fixer"] and "CLAUDE.md" not in prompts["fixer"])
+    check("every role's prompt ends its first line with its seat key: the role, the model, the dispatch name",
+          all(token_ledger.parse_header(t.splitlines()[0]) == {"group": "-", "role": r, "dimension": "-", "model": "m-1",
+                                                                 "seat": f"{r}-t-1"} for r, t in prompts.items()))
+    gen = "Part 1 of 2: build carries 0-4; the others are later parts dispatched at this part's handoff; answer none of them"
+    check("a hand brief re-dispatching a split part inherits the part line its ref's prompt held (R11-PRE-TOOLCHAIN-PIN "
+          "repair a546de28d0), once",
+          inherit_part(f"x\n\n{gen}\n", "Repair.\n") == f"Repair.\n\n{gen}\n"
+          and inherit_part(f"x\n{gen}\n", f"Repair.\n\n{gen}\n") == f"Repair.\n\n{gen}\n")
+    check("and nothing is added when the previous prompt held no part line, or there was none (null control)",
+          inherit_part("Carry 0: a\n", "Repair.\n") == "Repair.\n" == inherit_part("", "Repair.\n"))
     check("every role's setup line runs the toolchain check and stops on its REFUSE (#2709)",
           all(f"`{SETUP_CHECK}`, and on REFUSE stop" in t.splitlines()[1] for t in prompts.values()))
     rv = prompts["reviewer"]
@@ -1500,6 +1563,10 @@ def self_test() -> int:
               ptr.startswith(_seat_line(role, "owner/name", a["pr"], head, a["topic"], a["nonce"]))
               and f"git fetch origin {pin} && git show {pin}:PROMPT.md" in ptr and f"of {ref} " in ptr
               and sum(FOOTER_BAN in x for x in ptr.splitlines()) == 1 and len(ptr) < len(prompts[role]))
+        whole = render(role, head, **base, **a)["job_config"]["ccr"]["events"][0]["data"]["message"]["content"]
+        check(f"a published {role}'s stub ends its first line with the seat key its whole prompt carries",
+              token_ledger.parse_header(ptr.splitlines()[0]) == token_ledger.parse_header(whole.splitlines()[0])
+              is not None)
         check(f"a published {role} with no 40-hex pin is refused", refused(role, publish_ref=ref, pin="")
               and refused(role, publish_ref=ref, pin=ref) and not refused(role, publish_ref=ref, pin=pin))
     check("a reviewer's stub carries its nonce", "abc123" in render(
@@ -1628,8 +1695,10 @@ def main(argv: list[str]) -> int:
         known = dict(pr=args.pr, topic=args.topic, nonce=args.nonce, brief=brief, design=args.design,
                      reviewed_head=args.reviewed_head, **_config(args))
         if args.publish:
-            payload = publish_seat(".", dispatch_ref(args.role, args.topic, args.pr), args.role, args.head,
-                                   **known)
+            ref = dispatch_ref(args.role, args.topic, args.pr)
+            if args.role == "fixer":  # a hand brief re-dispatching a split part keeps the part's line
+                known["brief"] = inherit_part(_prev_prompt(".", ref), brief)
+            payload = publish_seat(".", ref, args.role, args.head, **known)
         else:
             payload = render(args.role, args.head, **known)
     except Refusal as e:
diff --git a/tools/audit/seat/instruments/token_ledger.py.md b/tools/audit/seat/instruments/token_ledger.py.md
new file mode 100644
index 0000000000..1dfa3b1b37
--- /dev/null
+++ b/tools/audit/seat/instruments/token_ledger.py.md
@@ -0,0 +1,31 @@
+# `token_ledger.py`
+
+- `token_ledger.py` — decision 0018 section 2's token ledger: every usage field
+  of every seat, apart, keyed by group, role, dimension, model and seat
+  (R11-PRE-TOKEN-LEDGER; the process convergence audit d5d7ff81, section 6 row
+  a4). Its rules and null controls are the script's docstring; the commands are:
+  - **The key a dispatch writes** (`cloud_dispatch.render` ends the first line of
+    every cloud event with it, the published stub included; a local spawn writes
+    it as its brief's first line, which no rule checks, so an unkeyed spawn's row
+    is `seat=-` and `check_scopes.py --round` prints its refusal unread):
+
+        python3 -I tools/audit/seat/token_ledger.py header --role <role> --group <G> --model <m> \
+          [--dimension <D>] [--seat <name>]
+
+  - **The ledger** (the beat's `scorecard` row runs it daily before
+    `round_metrics.py produce`, into the file `round_metrics.py`'s `tokens`
+    line reads):
+
+        python3 -I tools/audit/seat/token_ledger.py collect --projects <claude project dir> \
+          --out <state>/scorecard/tokens.tsv
+
+    `--seat-class cloud`, run inside a cloud seat on its own project dir, reads
+    that session: the cloud class has no row on the host, so the `tokens` line
+    prints unread, never a partial.
+  - **Each field apart, per seat class and role:**
+
+        python3 -I tools/audit/seat/token_ledger.py summary --ledger <state>/scorecard/tokens.tsv \
+          [--since ISO] [--until ISO]
+
+  - **Importable:** `sessions(project_dir)` yields each session's id, its own
+    transcript and its subagent transcripts.
diff --git a/tools/audit/seat/sweep_template.md b/tools/audit/seat/sweep_template.md
index a84b69a073..679cade87c 100644
--- a/tools/audit/seat/sweep_template.md
+++ b/tools/audit/seat/sweep_template.md
@@ -53,6 +53,7 @@ rendered text that no overlay value supplied.
 | `train_state` | optional: the merge train's state dir; the `cancel-sweep` row passes it as `--train-state`, so a pull request in the train's queue or spool is never cancelled for a priority run; empty leaves the flag out |
 | `gantt_roster` | the roster the beat's `gantt` row reads, as `<branch>:<path>` (fetched to `refs/gantt/roster`, never a local branch) |
 | `gantt_acks` | the Gantt acks file `sweep_gantt.py --acks` reads, one `<ISO> <KEY> act\|defer\|accept [until=<ISO>] <reason>` line per answered slip |
+| `claude_projects` | optional: the Claude project directories (one path or a list) whose session transcripts the beat's `scorecard` row sums into the token ledger `token_ledger.py collect`; absent: the checkout's own under `~/.claude/projects` |
 | `fire_ledger` | the session's fire ledger, one line per seat fired with its leading UTC stamp, which the `gantt`, `verdict-audit` and `cp-owed` rows hand on as `--fired` (a line within 12 h holds the pull request or topic it names) |
 | `sweep_record` | optional: the day's sweep record file, rendered `scorecard.py --sweep-record FILE`; whose `recycle` lines of the standing dispatch and triage seats the `scorecard` row counts as K (absent: K prints unread) |
 | `train_glob` | the glob of live train logs `verdict_audit.py --train-glob` reads (a log modified within 3 h holds its queued pull requests) |
@@ -74,7 +75,7 @@ ORCHESTRATOR SWEEP, round {{round}}, repository {{repo}}. Read {{seat_ledger}} f
 
 (4) After each merge (`dev/governance/roles/standing-merge.md`: `tools/audit/seat/postmerge.py` runs after each merge and prints what is still `OWED`): read the merge seat's `merged` report and its read-back of the issues the merge closed (`dev/governance/roles/orchestrator.md` section 4), queue `set-stage` for a roster group to the `roster-drain` row, make one #3394 comment through `tools/pr/gh_comment.py` with its read-back, and remove the finished seat's worktrees under {{seat_root}} and its scratch; the `disk` row (step 8) runs `worktree_gc.sh`.
 
-(4b) Record beat. The beat's `plan-beat` row runs `python3 tools/plan/replan.py --out {{plan_json}} --slots {{plan_slots}} --seats {{plan_seats}} {{plan_coordinator_cap}}` (plus `--live-refs {{plan_live_refs}} --in-flight {{plan_in_flight}}` when the overlay names those files, so a group with a fixer ref or an open pull request is priced as working, not by its stage word), then `tools/audit/seat/state_docs.py --push --mirror {{state_mirror}} --plan {{plan_json}}`, every 30 minutes, merge or none; it publishes the plan page as `PLAN.html` in the plan table's commit at the state ref and mirrors it as {{plan_page}}, republished at the same path. A `plan-beat: PLAN UNAVAILABLE` line in {{digest}}/digest.txt is the page UNAVAILABLE (the other docs are still pushed; the ref keeps the last good page): answer its reason and re-run that replan, never hand-run `plan_page.py` around the refusal; a `plan-beat: REFUSED` line is the docs push's own refusal. A `plan-beat: PLAN MOVED` line is a page that changed since the last beat: republish it at {{plan_page}} this sweep (owner ruling, 2026-11-06: every sweep updates the plan artifact). The beat's `gantt` row compares that plan with the Gantt baseline through `tools/audit/seat/sweep_gantt.py`: it reads the roster at {{gantt_roster}}, the fire ledger {{fire_ledger}} and the acks file {{gantt_acks}}; each `GANTT-SLIP` line of {{digest}}/digest.txt is owed `act`, `defer` or `accept`, appended to {{gantt_acks}} (owner ruling, 2026-11-01). The beat's `scorecard` row runs `python3 tools/audit/seat/scorecard.py report {{sweep_record}}` (its other arguments are the beat's own), report-only; K prints unread when no sweep record is given.
+(4b) Record beat. The beat's `plan-beat` row runs `python3 tools/plan/replan.py --out {{plan_json}} --slots {{plan_slots}} --seats {{plan_seats}} {{plan_coordinator_cap}}` (plus `--live-refs {{plan_live_refs}} --in-flight {{plan_in_flight}}` when the overlay names those files, so a group with a fixer ref or an open pull request is priced as working, not by its stage word), then `tools/audit/seat/state_docs.py --push --mirror {{state_mirror}} --plan {{plan_json}}`, every 30 minutes, merge or none; it publishes the plan page as `PLAN.html` in the plan table's commit at the state ref and mirrors it as {{plan_page}}, republished at the same path. A `plan-beat: PLAN UNAVAILABLE` line in {{digest}}/digest.txt is the page UNAVAILABLE (the other docs are still pushed; the ref keeps the last good page): answer its reason and re-run that replan, never hand-run `plan_page.py` around the refusal; a `plan-beat: REFUSED` line is the docs push's own refusal. A `plan-beat: PLAN MOVED` line is a page that changed since the last beat: republish it at {{plan_page}} this sweep (owner ruling, 2026-11-06: every sweep updates the plan artifact). The beat's `gantt` row compares that plan with the Gantt baseline through `tools/audit/seat/sweep_gantt.py`: it reads the roster at {{gantt_roster}}, the fire ledger {{fire_ledger}} and the acks file {{gantt_acks}}; each `GANTT-SLIP` line of {{digest}}/digest.txt is owed `act`, `defer` or `accept`, appended to {{gantt_acks}} (owner ruling, 2026-11-01). The beat's `scorecard` row runs `python3 tools/audit/seat/scorecard.py report {{sweep_record}}` (its other arguments are the beat's own), report-only; K prints unread when no sweep record is given. Before it, the row sums the session transcripts under {{claude_projects}} into the token ledger (`tools/audit/seat/token_ledger.py collect`), whose `tokens` line in the scorecard prints unread while the cloud class has no row.
 
 (4c) Open pull requests. Reconcile every open pull request to one bucket, with its reason: in train, review out, fixer out, CI wait, or owner-held; none waits without one; critical path first. The beat's `verdict-audit` row (`tools/audit/seat/verdict_audit.py`, reading {{fire_ledger}}, the train logs {{train_glob}} and the skip file {{unheld_skip}}) prints an `UNHELD` line in {{digest}}/digest.txt for each pull request whose next step nobody holds: give each a holder this sweep, or put a pull request held by an owner ruling on {{unheld_skip}} (owner ruling, 2026-11-06: no pull request waits unheld). The beat's `cp-owed` row (`tools/audit/seat/owed_watch.py`, reading {{fire_ledger}}) prints a `CP-OWED <arm> <subject>` line for each step of a critical-path or outside group, or of its pull request, past its grace: act on each this sweep, critical path and outside first (owner directive, tvofi 2026-11-09: never let the critical path or outside pull requests slip). The beat's `bottleneck` row (`tools/audit/seat/bottleneck_check.py`, reading the train log {{train_log}} and the cap {{plan_slots}}) prints a `BOTTLENECK:` line in {{digest}}/digest.txt once per trip of a flow metric past the owner's threshold, with a suggested action: decide whether to act on it this sweep; the line takes no action itself (owner request, tvofi 2026-11-07). A `BOTTLENECK-UNREADABLE:` line is a metric the alert cannot see.
 
diff --git a/tools/audit/seat/token_ledger.py b/tools/audit/seat/token_ledger.py
new file mode 100644
index 0000000000..c836eab0e9
--- /dev/null
+++ b/tools/audit/seat/token_ledger.py
@@ -0,0 +1,339 @@
+#!/usr/bin/env python3
+"""token_ledger.py -- decision 0018's token ledger: usage per seat, every field apart.
+
+    python3 -I tools/audit/seat/token_ledger.py header --role R [--group G] [--model M] [--dimension D] [--seat S]
+    python3 -I tools/audit/seat/token_ledger.py collect --projects DIR [--projects DIR ...] --out FILE
+                                                        [--seat-class cloud]
+    python3 -I tools/audit/seat/token_ledger.py summary --ledger FILE [--since ISO] [--until ISO]
+    python3 -I tools/audit/seat/token_ledger.py --self-test
+
+WHY (owner ruling 2026-11-13, card P4; the round-10 process convergence audit
+d5d7ff81, section 1 T and section 6 row a4; decision 0018 section 2,
+`tokens_per_change`): no record of token use existed, so T could not be a
+controlled variable.
+
+THE KEY. Every dispatch writes one line `Seat key: group=G role=R dimension=D
+model=M seat=S` (`header`; `-` for a field that does not apply) into the seat's
+first message, at a line's start or after a space. `collect` reads it from the
+first user message of each transcript, and from no later one. The paths that
+write it: every cloud seat is fired with a `cloud_dispatch.render` event, and
+`render` ends that event's first line with the key, the stub `publish_seat`
+fires included. Residue, by category: a local seat spawned by a host session's
+Agent tool, whose first message the spawning session writes and no rule keys;
+its row is `seat=-`, and check_scopes --round prints its refusal unread while
+the graded window holds one (`ledger_unread`).
+
+THE SOURCE. A Claude project directory holds `<session>.jsonl` (the session's
+own transcript) and `<session>/subagents/agent-<id>.jsonl` (each spawned seat's);
+`sessions()` yields both per session, importable by any reader. Every assistant
+line carries `message.usage`; one API response is written once per content
+block, so usage is counted once per (message id, request id) over the whole
+session. The four fields are kept apart (FIELDS); `tokens` is their sum.
+
+THE CLASS (round_metrics.SEAT_CLASSES): a session's own transcript with no seat
+key is the orchestrator's; with one, a local seat run as its own session; every
+subagent transcript is a local seat. `--seat-class cloud` labels every row cloud:
+a cloud seat's transcript lives only in its own container (measured: the seat
+reads it at `~/.claude/projects/<cwd slug>/$CLAUDE_CODE_SESSION_ID.jsonl`), and
+no tracked path brings it to the host this job runs on, so the cloud class has
+no row and round_metrics' `tokens` line prints unread, never a partial.
+
+THE LEDGER `--out` (the beat's `<state>/scorecard/tokens.tsv`, round_metrics'
+input): one row per (session, agent, UTC day), columns COLUMNS, `t` the day's
+last usage stamp. A pass replaces the rows of every transcript it read and keeps
+the rest, so a transcript the client has since pruned keeps its rows.
+"""
+from __future__ import annotations
+
+import argparse
+import collections
+import csv
+import importlib.util
+import io
+import json
+import os
+import re
+import sys
+import tempfile
+from pathlib import Path
+
+HERE = Path(__file__).resolve().parent
+FIELDS = ("input_tokens", "output_tokens", "cache_creation_input_tokens", "cache_read_input_tokens")
+KEYS = ("group", "role", "dimension", "model", "seat")
+COLUMNS = ("t", "seat_class", "tokens", *FIELDS, "session", "agent", *KEYS)
+HEADER = re.compile(r"(?:^|(?<= ))Seat key: (.*)$", re.M)
+VALUE = re.compile(r"[A-Za-z0-9._/@+-]+")
+
+
+class Refusal(Exception):
+    pass
+
+
+def header(**kw: str) -> str:
+    """The seat-key line; a value outside VALUE (a space, an `=`) would split the key, so it refuses."""
+    if set(kw) - set(KEYS):
+        raise Refusal(f"unknown key {sorted(set(kw) - set(KEYS))}")
+    vals = {k: (kw.get(k) or "-") for k in KEYS}
+    bad = [k for k, v in vals.items() if not VALUE.fullmatch(v)]
+    if bad or vals["role"] == "-":
+        raise Refusal(f"seat key {', '.join(bad) or 'role'} is empty or not one token: {vals}")
+    return "Seat key: " + " ".join(f"{k}={vals[k]}" for k in KEYS)
+
+
+def parse_header(text: str) -> dict | None:
+    m = HEADER.search(text or "")
+    if not m:
+        return None
+    got = dict(p.split("=", 1) for p in m.group(1).split() if "=" in p)
+    return {k: got.get(k, "-") for k in KEYS}
+
+
+def sessions(project: Path):
+    """(session id, its own transcript, [its subagent transcripts]) per session of one project dir."""
+    for main in sorted(Path(project).glob("*.jsonl")):
+        yield main.stem, main, sorted((main.parent / main.stem / "subagents").glob("*.jsonl"))
+
+
+def _text(content) -> str:
+    if isinstance(content, str):
+        return content
+    return "\n".join(b.get("text", "") for b in content or [] if isinstance(b, dict))
+
+
+def read_transcript(path: Path, seen: set) -> tuple[dict | None, dict]:
+    """(the seat key of its first user message, {day: {field: n, "t": last stamp, "model": m}})."""
+    key, first, days = None, True, {}
+    with open(path, encoding="utf-8", errors="replace") as f:
+        for ln in f:
+            try:
+                o = json.loads(ln)
+            except ValueError:
+                continue
+            m = o.get("message") if isinstance(o, dict) else None
+            if not isinstance(m, dict):
+                continue
+            if first and o.get("type") == "user":
+                first, key = False, parse_header(_text(m.get("content")))
+            u = m.get("usage")
+            stamp = str(o.get("timestamp") or "")
+            if not isinstance(u, dict) or len(stamp) < 10:
+                continue
+            ident = (m.get("id"), o.get("requestId"))
+            if ident in seen and ident != (None, None):
+                continue
+            seen.add(ident)
+            d = days.setdefault(stamp[:10], dict.fromkeys(FIELDS, 0) | {"t": "", "model": "-"})
+            for k in FIELDS:
+                d[k] += int(u.get(k) or 0)
+            d["t"] = max(d["t"], stamp)
+            d["model"] = m.get("model") or d["model"]
+    return key, days
+
+
+def rows_of(project: Path, seat_class: str | None = None) -> list[dict]:
+    rows = []
+    for sid, main, subs in sessions(project):
+        seen: set = set()
+        for path in [main, *subs]:
+            key, days = read_transcript(path, seen)
+            own = path == main
+            cls = seat_class or ("local" if not own or key else "orchestrator")
+            if key is None:
+                key = dict.fromkeys(KEYS, "-") | ({"role": "orchestrator"} if cls == "orchestrator" else {})
+            for day in sorted(days):
+                d = days[day]
+                rows.append({"t": d["t"], "seat_class": cls, "tokens": sum(d[k] for k in FIELDS),
+                             **{k: d[k] for k in FIELDS}, "session": sid,
+                             "agent": "-" if own else path.stem.removeprefix("agent-"),
+                             **key, "model": key["model"] if key["model"] != "-" else d["model"]})
+    return rows
+
+
+def read_ledger(path: Path) -> list[dict]:
+    try:
+        return list(csv.DictReader(io.StringIO(Path(path).read_text()), delimiter="\t"))
+    except OSError:
+        return []
+
+
+def collect(projects: list[Path], out: Path, seat_class: str | None = None) -> tuple[int, int]:
+    """Rewrite `out`: the rows of every transcript read now, plus kept rows of transcripts not read.
+    Returns (rows written, transcripts read)."""
+    fresh = [r for p in projects for r in rows_of(p, seat_class)]
+    read = {(sid, "-" if path == main else path.stem.removeprefix("agent-"))
+            for p in projects for sid, main, subs in sessions(p) for path in [main, *subs]}
+    kept = [r for r in read_ledger(out) if (r.get("session"), r.get("agent")) not in read]
+    rows = sorted(kept + fresh, key=lambda r: (r["t"], r["session"], r["agent"]))
+    buf = io.StringIO()
+    w = csv.DictWriter(buf, COLUMNS, delimiter="\t", extrasaction="ignore", lineterminator="\n")
+    w.writeheader()
+    w.writerows(rows)
+    out.parent.mkdir(parents=True, exist_ok=True)
+    fd, tmp = tempfile.mkstemp(dir=out.parent, prefix=".tokens.")
+    with os.fdopen(fd, "w") as f:
+        f.write(buf.getvalue())
+    os.replace(tmp, out)
+    return len(rows), len(read)
+
+
+def summary(rows: list[dict], since: str = "", until: str = "") -> list[str]:
+    """Per seat class and role, each field apart and the total, over rows with since <= t < until."""
+    acc: dict = collections.defaultdict(lambda: collections.Counter())
+    for r in rows:
+        if since <= r["t"] and (not until or r["t"] < until):
+            acc[(r["seat_class"], r["role"])].update({k: int(r[k]) for k in (*FIELDS, "tokens")})
+    return [f"{c}\t{role}\t" + "\t".join(f"{k}={n[k]}" for k in (*FIELDS, "tokens"))
+            for (c, role), n in sorted(acc.items())]
+
+
+# ---------------------------------------------------------------- self-test
+
+def _line(kind: str, mid: str, req: str, t: str, usage: dict | None = None, text: str = "") -> str:
+    msg = {"role": kind, "content": text} if kind == "user" else {"id": mid, "model": "m-x", "usage": usage}
+    return json.dumps({"type": kind, "requestId": req, "timestamp": t, "message": msg}) + "\n"
+
+
+def self_test() -> int:
+    passed = failed = 0
+
+    def check(name: str, cond: bool) -> None:
+        nonlocal passed, failed
+        passed, failed = passed + bool(cond), failed + (not cond)
+        print(f"  {'ok  ' if cond else 'FAIL'} {name}")
+
+    u = {"input_tokens": 1, "output_tokens": 10, "cache_creation_input_tokens": 100, "cache_read_input_tokens": 1000}
+    key = header(group="G-1", role="fixer", model="opus", seat="fixer-g-1")
+    check("header renders every key, `-` where unset",
+          key == "Seat key: group=G-1 role=fixer dimension=- model=opus seat=fixer-g-1")
+    check("parse_header reads it back from inside a longer message",
+          parse_header("CLOUD FIXER seat.\n" + key + "\nmore") == parse_header("CLOUD FIXER seat. " + key) ==
+          {"group": "G-1", "role": "fixer", "dimension": "-", "model": "opus", "seat": "fixer-g-1"})
+    check("no seat key, or one glued to a word, parses as None (null control)",
+          parse_header("CLOUD FIXER seat.") is None and parse_header("xSeat key: role=r") is None)
+
+    def refuses(**kw) -> bool:
+        try:
+            header(**kw)
+        except Refusal:
+            return True
+        return False
+    check("a value with a space, an `=`, an empty role or an unknown key refuses; a plain one does not",
+          refuses(role="fix er") and refuses(role="fixer", group="a=b") and refuses(group="G")
+          and refuses(role="x", colour="red") and not refuses(role="x"))
+
+    with tempfile.TemporaryDirectory() as tmp:
+        proj = Path(tmp) / "proj"
+        (proj / "s1" / "subagents").mkdir(parents=True)
+        (proj / "s1.jsonl").write_text(
+            _line("user", "", "", "2026-11-01T00:00:00Z", text="hello")
+            + _line("assistant", "m1", "r1", "2026-11-01T01:00:00Z", u)
+            + _line("assistant", "m1", "r1", "2026-11-01T01:00:01Z", u)  # a second content block of m1
+            + _line("assistant", "m2", "r2", "2026-11-02T01:00:00Z", u) + "not json\n")
+        (proj / "s1" / "subagents" / "agent-a1.jsonl").write_text(
+            _line("user", "", "", "2026-11-01T02:00:00Z", text=key + "\nbrief")
+            + _line("assistant", "m3", "r3", "2026-11-01T02:00:00Z", u))
+        (proj / "s1" / "subagents" / "agent-a2.jsonl").write_text(
+            _line("user", "", "", "2026-11-01T03:00:00Z", text="no key")
+            + _line("assistant", "m4", "r4", "2026-11-01T03:00:00Z", u))
+        got = list(sessions(proj))
+        check("sessions() yields the session's own transcript and each subagent transcript",
+              [(s, m.name, [p.name for p in subs]) for s, m, subs in got]
+              == [("s1", "s1.jsonl", ["agent-a1.jsonl", "agent-a2.jsonl"])])
+        out = Path(tmp) / "state" / "scorecard" / "tokens.tsv"
+        n, read = collect([proj], out)
+        rows = read_ledger(out)
+        by = {(r["agent"], r["t"][:10]): r for r in rows}
+        check("one row per transcript and day: 2 orchestrator days, 2 subagents", n == 4 and read == 3)
+        o1 = by[("-", "2026-11-01")]
+        check("a response written once per content block counts once (m1 twice is 1111, not 2222)",
+              o1["tokens"] == "1111")
+        check("every usage field is kept apart and `tokens` is their sum",
+              [o1[k] for k in FIELDS] == ["1", "10", "100", "1000"])
+        check("a session's own transcript with no key is the orchestrator's",
+              o1["seat_class"] == "orchestrator" and o1["role"] == "orchestrator")
+        a1, a2 = by[("a1", "2026-11-01")], by[("a2", "2026-11-01")]
+        check("a keyed subagent is a local seat keyed by group, role, dimension, model and seat",
+              (a1["seat_class"], a1["group"], a1["role"], a1["dimension"], a1["model"], a1["seat"])
+              == ("local", "G-1", "fixer", "-", "opus", "fixer-g-1"))
+        check("an unkeyed subagent is still a local seat, its model read from the response",
+              (a2["seat_class"], a2["group"], a2["role"], a2["model"]) == ("local", "-", "-", "m-x"))
+        (proj / "s1" / "subagents" / "agent-a2.jsonl").unlink()
+        collect([proj], out)
+        check("a transcript pruned since keeps its rows; the rest are replaced, not appended",
+              len(read_ledger(out)) == 4)
+        n2, _ = collect([proj], Path(tmp) / "cloud.tsv", seat_class="cloud")
+        check("--seat-class cloud labels every row cloud",
+              {r["seat_class"] for r in read_ledger(Path(tmp) / "cloud.tsv")} == {"cloud"} and n2 == 3)
+        check("summary keeps each field apart per seat class and role",
+              "local\tfixer\tinput_tokens=1\toutput_tokens=10\tcache_creation_input_tokens=100"
+              "\tcache_read_input_tokens=1000\ttokens=1111" in summary(rows))
+        # review/3898 M4, M5: a real transcript's later user lines (each tool_result) never rekey
+        # it, and a day's `t` is its last stamp whatever order the lines were written in
+        proj2 = Path(tmp) / "proj2"
+        proj2.mkdir()
+        tool_result = json.dumps({"type": "user", "timestamp": "2026-11-01T02:00:01Z", "message": {
+            "role": "user", "content": [{"type": "tool_result", "tool_use_id": "x", "content": "done"}]}}) + "\n"
+        (proj2 / "s2.jsonl").write_text(
+            _line("user", "", "", "2026-11-01T01:00:00Z", text=key)
+            + _line("assistant", "m5", "r5", "2026-11-01T02:00:00Z", u) + tool_result
+            + _line("user", "", "", "2026-11-01T02:00:02Z", text="Seat key: role=reviewer seat=other")
+            + _line("assistant", "m6", "r6", "2026-11-01T01:30:00Z", u))
+        collect([proj2], Path(tmp) / "two.tsv")
+        two = read_ledger(Path(tmp) / "two.tsv")
+        check("a keyed transcript stays keyed by its first user message through later user lines (a tool_result, "
+              "another key): one local fixer row",
+              [(r["seat_class"], r["role"], r["seat"]) for r in two] == [("local", "fixer", "fixer-g-1")])
+        check("a day's `t` is its latest stamp, not its last-written one", two[0]["t"] == "2026-11-01T02:00:00Z")
+        # the reader this ledger feeds: round_metrics.token_line, unchanged
+        spec = importlib.util.spec_from_file_location("round_metrics", HERE / "round_metrics.py")
+        rm = importlib.util.module_from_spec(spec)
+        spec.loader.exec_module(rm)
+        merges = [{"class": "production", "ct": rm.epoch("2026-11-01T12:00:00Z")}]
+        a, b = rm.epoch("2026-11-01T00:00:00Z"), rm.epoch("2026-11-03T00:00:00Z")
+        line = rm.token_line(out.parent, merges, a, b)
+        check("round_metrics reads the ledger and prints unread while the cloud class has no row",
+              "seat classes with no ledger row: cloud;" in line)
+        with open(out, "a") as f:
+            f.write("2026-11-01T05:00:00Z\tcloud\t5\n")
+        check("one cloud row makes it read, summing `tokens` (null control for the unread arm)",
+              rm.token_line(out.parent, merges, a, b).startswith("tokens 4449 per production merge"))
+    print(f"token_ledger self-test: {passed} passed, {failed} failed")
+    return 1 if failed else 0
+
+
+def main(argv: list[str]) -> int:
+    if argv == ["--self-test"]:
+        return self_test()
+    ap = argparse.ArgumentParser(prog="token_ledger.py")
+    sub = ap.add_subparsers(dest="cmd", required=True)
+    h = sub.add_parser("header")
+    for k in KEYS:
+        h.add_argument(f"--{k}", default="")
+    c = sub.add_parser("collect")
+    c.add_argument("--projects", action="append", required=True, type=Path)
+    c.add_argument("--out", required=True, type=Path)
+    c.add_argument("--seat-class", choices=("cloud",))
+    s = sub.add_parser("summary")
+    s.add_argument("--ledger", required=True, type=Path)
+    s.add_argument("--since", default="")
+    s.add_argument("--until", default="")
+    a = ap.parse_args(argv)
+    try:
+        if a.cmd == "header":
+            print(header(**{k: getattr(a, k) for k in KEYS}))
+        elif a.cmd == "collect":
+            missing = [str(p) for p in a.projects if not p.is_dir()]
+            if missing:
+                raise Refusal(f"no project directory: {', '.join(missing)}")
+            n, read = collect(a.projects, a.out, a.seat_class)
+            print(f"token_ledger: {n} rows from {read} transcripts into {a.out}")
+        else:
+            print("\n".join(summary(read_ledger(a.ledger), a.since, a.until)))
+    except Refusal as e:
+        print(f"token_ledger: refused: {e}", file=sys.stderr)
+        return 2
+    return 0
+
+
+if __name__ == "__main__":
+    sys.exit(main(sys.argv[1:]))
diff --git a/tools/ci/selftest_closures.json b/tools/ci/selftest_closures.json
index 69901c1fd7..14d357721e 100644
--- a/tools/ci/selftest_closures.json
+++ b/tools/ci/selftest_closures.json
@@ -235,6 +235,8 @@
     "tools/audit/seat/ci_predict_replay.sh",
     "tools/audit/seat/ci_priority.py",
     "tools/audit/seat/ci_probe.py",
+    "tools/audit/seat/ci_rerun.py",
+    "tools/audit/seat/ci_supersede.sh",
     "tools/audit/seat/closeout.py",
     "tools/audit/seat/cloud-setup.sh",
     "tools/audit/seat/cloud_dispatch.py",
@@ -320,6 +322,7 @@
     "tools/audit/seat/seat_gen.py",
     "tools/audit/seat/seat_gen_selftest.py",
     "tools/audit/seat/seat_venv.sh",
+    "tools/audit/seat/selftest_absorb.py",
     "tools/audit/seat/selftest_wiring.py",
     "tools/audit/seat/shell_hazard.py",
     "tools/audit/seat/shims/**",
@@ -332,6 +335,7 @@
     "tools/audit/seat/sweep_template.md",
     "tools/audit/seat/tick_loop.sh",
     "tools/audit/seat/tmp_paths.py",
+    "tools/audit/seat/token_ledger.py",
     "tools/audit/seat/toolchain.py",
     "tools/audit/seat/toolchain_selftest.py",
     "tools/audit/seat/topic_grammar.py",
@@ -432,6 +436,8 @@
     "tools/audit/seat/fixtures",
     "tools/audit/seat/fixtures/beat_jobs",
     "tools/audit/seat/fixtures/ci_critpath",
+    "tools/audit/seat/fixtures/ci_rerun",
+    "tools/audit/seat/fixtures/ci_rerun/pr3836",
     "tools/audit/seat/hooks",
     "tools/audit/seat/instruments",
     "tools/audit/seat/shims",
@@ -3120,6 +3126,7 @@
     "tools/audit/seat/ref_privacy.py",
     "tools/audit/seat/review_packet.py",
     "tools/audit/seat/roster_lib.py",
+    "tools/audit/seat/token_ledger.py",
     "tools/audit/seat/topic_grammar.py"
    ],
    "probes": [
@@ -7595,9 +7602,7 @@
     "dev/governance/dimensions",
     "dev/governance/rules/a-rule.md",
     "dev/programme/.gitattributes",
-    "dev/programme/carries/.gitattributes",
-    "dev/programme/carries/carry-1645.json",
-    "dev/programme/carries/carry-201.json",
+    "dev/programme/carries/**",
     "dev/programme/delivery",
     "dev/programme/register/.gitattributes",
     "dev/programme/rosters/.gitattributes",
@@ -11197,6 +11202,23 @@
     "rev-list"
    ]
   },
+  "token-ledger": {
+   "run_sha": "2187606ddb988417845b538a2a014db8fc1fd2616f7bf42e304f706467d5d4a6",
+   "files": [
+    "tools/audit/seat/round_metrics.py",
+    "tools/audit/seat/token_ledger.py"
+   ],
+   "probes": [
+    ".",
+    "tools",
+    "tools/audit",
+    "tools/audit/seat"
+   ],
+   "dirs": [],
+   "index": false,
+   "objects": false,
+   "git": []
+  },
   "toolchain": {
    "run_sha": "58a9dcb43610f2fb8ff4466f1623dd23eff5bec9e8fdfd1cf4ca65cfa4bc6b54",
    "files": [

## Before you return the verdict (P275)
Run `python3 -I tools/audit/carry_audit.py check --body <PR body file> --comments <file holding [{"id": 0, "body": <verdict.md text>}]>`. Give every reported item its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>`;
an evidence line flagged by its wording takes `Carry: dismissed: evidence, not a finding`. Return the verdict only at rc 0.
