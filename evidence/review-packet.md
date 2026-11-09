# Review packet #3341
head: 06a3478fdbf386278952d741985e5da5ee28bd5c
base: 6457496aba7b1076b1ed60c374c5badafdf66fc1

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: red
CodeQL id=128955727876 neutral
arch-score / arch-score id=128956059476 success
arm id=128955279855 skipped
budget-raise-gate / budget-raise-gate id=128956059347 success
cancel-superseded id=128955575998 success
codeql id=128956060526 skipped
codeql / Analyze (actions) id=128955414214 success
codeql / Analyze (javascript-typescript) id=128955414106 success
codeql / Analyze (python) id=128955414114 in_progress
gate id=128956599985 failure
governance id=128956060615 skipped
governance / delivery-status id=128955414223 failure
governance / delivery-status-publish id=128955415241 skipped
governance / env-matrix id=128955414137 success
governance / instrument-self-tests id=128955414199 success
governance / policy-docs id=128955414061 success
governance / record id=128955415638 skipped
governance / wave-script id=128955414192 success
hassfest id=128956060999 skipped
hassfest / hassfest id=128955414098 success
kernel-points id=128956060715 skipped
pr-contract id=128956601085 skipped
prelude id=128955575864 success
refresh id=128955575573 success
tests id=128956060651 skipped
tests / arch-instrument id=128955985748 success
tests / briefs id=128955414130 success
tests / browser id=128955985791 success
tests / claims-autofix id=128959361403 skipped
tests / closure-scope id=128955414146 success
tests / closures id=128955985923 in_progress
tests / coverage id=128955985753 success
tests / coverage-ratchet id=128959827058 queued
tests / fast (3.14) id=128955985759 success
tests / graders-head-copy id=128959827047 queued
tests / lane-proofs id=128959827053 queued
tests / mutation id=128955414173 success
tests / mutation-autofix id=128955774145 skipped
tests / mutation-pins id=128955773196 skipped
tests / nightly-ha id=128955987495 skipped
tests / nightly-status id=128955414249 success
tests / replay id=128955987008 skipped
tests / typing id=128955985776 success
validate id=128956061155 skipped
validate / validate-hacs id=128955414019 success

## Refusals
red-unanswered: concluded red check `gate` is not named in ## Red checks
red-unanswered: concluded red check `governance / delivery-status` is not named in ## Red checks
required-red: required context `gate` concluded failure at 06a3478fdbf386278952d741985e5da5ee28bd5c

## Advisories
none

## carry_audit at the head
CARRY-AUDIT: 0 finding item(s): 0 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
ok         python3 -I tools/audit/seat/survivor_list.py --self-test
             `tools/audit/seat/survivor_list.py` is in the tree at this head
  ok         bash tools/audit/seat/bus.sh --self-test
             `tools/audit/seat/bus.sh` is in the tree at this head
  ok         python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"
             `tests/closure.py` is in the tree at this head
  ok         python3 tests/closure.py select --files $(git diff --name-only $(git merge-base origin/main HEAD)...HEAD)
             `tests/closure.py` is in the tree at this head
  ok         tests/run.sh
             `tests/run.sh` is in the tree at this head
  ok         tests/doc_claims.py
             `tests/doc_claims.py` is in the tree at this head
  ok         tests/entities.py
             `tests/entities.py` is in the tree at this head
  ok         tests/harness_headers.py
             `tests/harness_headers.py` is in the tree at this head
  ok         python3 tests/structure.py
             `tests/structure.py` is in the tree at this head
  ok         node tools/policy/policy_lint.mjs --budgets
             `tools/policy/policy_lint.mjs` is in the tree at this head
  ok         python3 -I tools/audit/seat/selftest_wiring.py --check
             `tools/audit/seat/selftest_wiring.py` is in the tree at this head
  ok         node tools/policy/agreement.mjs
             `tools/policy/agreement.mjs` is in the tree at this head
  unverified git merge-tree --write-tree HEAD <sibling handoff head>
             `git merge-tree` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  ok         python3 -I tools/audit/seat/review_strength.py --by class
             `tools/audit/seat/review_strength.py` is in the tree at this head

FIGURES: 13 resolved, 1 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
none

## Three-dot diff
diff --git a/.github/workflows/governance.yml b/.github/workflows/governance.yml
index dbe456598..7041eb669 100644
--- a/.github/workflows/governance.yml
+++ b/.github/workflows/governance.yml
@@ -1153,6 +1153,13 @@ jobs:
           python3 -I tools/audit/seat/verdict_audit.py --self-test | tee "$RUNNER_TEMP/verdict-audit-self-test.txt"
           grep -Eq '^verdict_audit self-test: [1-9][0-9]* checks, 0 failed$' "$RUNNER_TEMP/verdict-audit-self-test.txt"
 
+      - name: Show the survivor-list check (tools/audit/seat/survivor_list.py) refusing its own fixtures
+        if: ${{ !cancelled() }}
+        run: |
+          set -o pipefail
+          python3 -I tools/audit/seat/survivor_list.py --self-test | tee "$RUNNER_TEMP/survivor-list-self-test.txt"
+          grep -Eq '^survivor_list self-test: [1-9][0-9]* checks, 0 failed$' "$RUNNER_TEMP/survivor-list-self-test.txt"
+
       - name: Show the CI probe instrument (tools/audit/seat/ci_probe.py) refusing its own fixtures
         if: ${{ !cancelled() }}
         run: |
diff --git a/dev/governance/roles/fix-review.md b/dev/governance/roles/fix-review.md
index eb1f7c6cd..da313db60 100644
--- a/dev/governance/roles/fix-review.md
+++ b/dev/governance/roles/fix-review.md
@@ -9,32 +9,35 @@ Long jobs and CI waits follow `fixer.md`'s preamble; rotate context between roun
 
 1. Re-run the mutation proof: delete the production line(s) the PR names,
    run the closure, confirm the named checks fail, restore. If nothing fails,
-   the test is vacuous: `blocked <sha> mutation-vacuous: <mutant>`.
+   it is vacuous: `blocked <sha> mutation-vacuous: <mutants>`: every
+   survivor your driver run at that head reports, which `push-verdict` reads in
+   your evidence (`survivor_list.py`, tvofi 2026-11-07).
 2. Measure with the **finder's** harness, not the fixer's: at the baseline
    SHA and at the PR head, printing your own `RESULT` lines. One flat by
-   design (`fixer.md` step 3): confirm it flat, not regressed, at both ends,
-   and run the companion yourself at both ends.
+   design (`fixer.md` step 3): confirm it flat at both ends, and run
+   its companion yourself at both.
 3. Re-run the null control and the both-ends check where the PR claims one.
 4. Compare the claim files with the actual drift: run `env_drift.py --all`
-   (and `card_drift.mjs` for card changes) against the merge base; every
+   (`card_drift.mjs` for a card) against the merge base; every
    moved fixture is claimed and every claim moved.
 5. Check `VERSION`, the manifest version and the notes heading are untouched.
 6. Attack the fix at other configurations the finding's harness accepts:
    the other topologies, the other price profiles, the zero-evidence install.
    **And open the class: a harness's configurations are its parameters, not its
-   population.** Run the enumeration rule the body names and compare its output with
+   population.** Run the enumeration rule the body names and compare its output to
    the diff: a seam it returns that is neither in the diff nor dispositioned in the body
-   is `blocked <sha> class-open: <seam>`, a site or a predicate's unguarded
-   domain. A body whose issue states more than one seam and names no rule is `blocked <sha> harness: class-rule-missing`. A body whose rule
-   returns nothing is a body whose class is one seam — say so rather than treating the absence as compliance.
+   is `blocked <sha> class-open: <seams>`, a site or a predicate's unguarded
+   domain: every one the review found, not one per round, no hunt past it owed.
+   An item whose harness does not move under its own perturbation is void
+   (`judge.md`): padding buys nothing. A body whose issue states more than one seam and names no rule is `blocked <sha> harness: class-rule-missing`. A rule returning
+   nothing means a one-seam class: say so, never read the absence as compliance.
 7. Confirm the head SHA in the PR body is the head you measured, or `--carry`s to it.
-8. **A quoted number you cannot re-derive is not verified — say so.** Re-derive
+8. **A quoted number you cannot re-derive is not verified: say so.** Re-derive
    under the PR's stated rule before trusting its count; if you cannot, or
-   if you had to build your own definition to check it, write that in the verdict.
+   had to build your own definition, write that in the verdict.
 9. **When the finding has no committed harness, that is itself a finding**.
-   A fixer who builds their own instrument must
-   disclose it as their own, not the finder's -- so do you, if you built one;
-   one rebuilt because a copy lived out of tree is named, and lands (`fixer.md` 18).
+   An instrument you or the fixer built is disclosed as the builder's, not the
+   finder's; one rebuilt from an out-of-tree copy is named and lands (`fixer.md` 18).
    A feature's harness is its judge's design: a requirement or on-device measurement it names and neither tests nor tvofi waived is `blocked <sha> harness: design-trace-missing <item>` (#1588).
 
 10. **Check the forward-carry before you return `merge`.** The PR body names
@@ -66,11 +69,9 @@ Long jobs and CI waits follow `fixer.md`'s preamble; rotate context between roun
     `record`/`skip red-history` for the range; `skip` means every earlier head
     UNCHECKED.
 
-    **A GREEN `mutation` does not mean the baseline was green.** Since #1120 the
-    lane prints `MUTATION TABLE INCONCLUSIVE` and exits 0 on `--scope changed`
-    when its baseline is red, so a green conclusion means either no mutant
-    survived or none was evaluated; a diff writing no production code line draws
-    no mutant (`changed_lines`). Where the answer turns on it, read the lane's log.
+    **A GREEN `mutation` may have evaluated nothing**: on `--scope changed` a red
+    baseline prints `MUTATION TABLE INCONCLUSIVE` and exits 0 (#1120), and a diff
+    writing no production code line draws no mutant (`changed_lines`). Where the answer turns on it, read the lane's log.
 
     **Cite CI's heavy runs** (tvofi, 2026-09-30): never re-run the gate or the
     mutation table. Cheap checks (seconds: a lint, one
@@ -92,26 +93,21 @@ Long jobs and CI waits follow `fixer.md`'s preamble; rotate context between roun
 13. **A conflict is a measurement, not a status field.** `mergeStateStatus:
     DIRTY` is GitHub's, computed where the `claimnotes` driver cannot run
     (`claim-files.md`). Confirm before you block:
-
-    ```
-    git merge-tree --write-tree origin/main <head>
-    ```
-
-    A non-zero exit names the conflicting paths. Block on main only on one,
+    `git merge-tree --write-tree origin/main <head>`; a non-zero exit names the conflicting paths. Block on main only on one,
     never on a head behind main that merges cleanly (tvofi 11-07). A
     conflict off the two claim files is yours.
 
     **The driver's verdict is in that command's stderr; read it, never infer it
     from the paths.** `merge-tree` invokes the driver once per conflicting claim
     file if you installed it (`claim-files.md`). Key on the marker,
-    `MERGE-CLAIM: resolved <path>` or `MERGE-CLAIM: refused <path>`, not on the
+    `MERGE-CLAIM: resolved|refused <path>`, not on the
     wording after it, which several checks supply. A `resolved` line settles
-    that file, and a non-zero exit beside it is about another path. A `refused`
-    line is the orchestrator's to resolve by hand, not a defect in the authored
-    work — say which file refused and why.
+    that file; a non-zero exit beside it is another path's. A `refused`
+    line is the orchestrator's to resolve by hand, not the author's defect: say
+    which file refused and why.
 
     Never classify by line shape: to `_comment_lines` a `may-drift` line **is**
-    a `#` comment, and `merge_claim_defect` refuses when one is lost, so "only
+    a `#` comment, and `merge_claim_defect` refuses losing one, so "only
     comment notes conflict" waves a real refusal through.
 
 14. **Every number the diff moves is earned by the change, not the instrument**:
diff --git a/dev/programme/delivery/3341.md b/dev/programme/delivery/3341.md
new file mode 100644
index 000000000..3a4b9f2d7
--- /dev/null
+++ b/dev/programme/delivery/3341.md
@@ -0,0 +1 @@
+- [#3341](https://github.com/tvofi/heatpump_optimizer/pull/3341) — **open**, R10-REVIEW-ENUMERATE: review enumerate (R10-REVIEW-ENUMERATE)
diff --git a/tests/closures.json b/tests/closures.json
index 49fc44084..e85d795d9 100644
--- a/tests/closures.json
+++ b/tests/closures.json
@@ -3936,6 +3936,7 @@
    "tools/audit/seat/roster_lib.py",
    "tools/audit/seat/roster_queue.py",
    "tools/audit/seat/selftest_wiring.py",
+   "tools/audit/seat/survivor_list.py",
    "tools/audit/seat/sweep_driver.py",
    "tools/audit/seat/sweep_driver_selftest.py",
    "tools/audit/seat/sweep_gantt.py",
diff --git a/tools/audit/seat/INSTRUMENTS.md b/tools/audit/seat/INSTRUMENTS.md
index 6e6d022b2..b3fa17163 100644
--- a/tools/audit/seat/INSTRUMENTS.md
+++ b/tools/audit/seat/INSTRUMENTS.md
@@ -121,6 +121,7 @@ sweep's standing-seat liveness step keep them alive.
 - [`sweep_template.md`](instruments/sweep_template.md.md) — the orchestrator's recurring sweep, steps in order
 - [`sweep_gantt.py`](instruments/sweep_gantt.py.md) — compares the live state to the plan's Gantt and prints each unacknowledged `GANTT-SLIP`
 - [`verdict_audit.py`](instruments/verdict_audit.py.md) — maps every open PR to its latest verdict and holder; prints `UNHELD` lines
+- [`survivor_list.py`](instruments/survivor_list.py.md) — refuses a `mutation-vacuous` verdict that omits a survivor its evidence's driver output reports; `bus.sh push-verdict` runs it
 - [`bare_array.py`](instruments/bare_array.py.md) — refuses a bare `"${name[@]}"` in any tracked `tools/**/*.sh` script (a sourced library runs under its caller's `set -u`), which macOS bash 3.2 dies on when the array is empty (`--check`, `--self-test`)
 - [`tmp_paths.py`](instruments/tmp_paths.py.md) — refuses a tracked script, workflow or decision record that depends on a temp or machine path (`--check`, `--self-test`)
 - [`update_pr.sh`](instruments/update_pr.sh.md) — brings an open PR branch to its head + a code SHA (merge) + origin/main (merge), adds the PR's own delivery row when the head lacks it (`delivery_row.sh`), prefixes ## Head with what happened, pushes as `hpo-author`
diff --git a/tools/audit/seat/bus.sh b/tools/audit/seat/bus.sh
index c6189967d..86e75f9c1 100755
--- a/tools/audit/seat/bus.sh
+++ b/tools/audit/seat/bus.sh
@@ -76,7 +76,8 @@
 # would refuse (ref_privacy.py body-lines, naming the line: P76), and one whose
 # finding items name no valid `Carry:` (carry_audit.py, the train pre-flight's
 # parser, over the verdict as its one comment, at origin/main and the round's
-# roster branch as last fetched: P40, P207). The push runs with a 500 MB
+# roster branch as last fetched: P40, P207), and a `mutation-vacuous` verdict omitting a survivor
+# the evidence's driver output reports (survivor_list.py). The push runs with a 500 MB
 # http.postBuffer: a ~30 MB evidence/ once failed HTTP 400 at git's 1 MB (#2563).
 #
 # NONCE VISIBILITY. The record lives in `$S` — `$HPO_BUS_STATE` else
@@ -295,6 +296,10 @@ push_verdict() { # pr verdict-file evidence-dir -> proposes the verdict on revie
   why=$(python3 -I "$ROOT/tools/audit/seat/ref_privacy.py" body-lines "$v") \
     || die "push-verdict: its post would refuse $v at $why; write the path as ~/... or drop it"
   why=$(carry_gate "$v") || die "push-verdict: $why"
+  # A mutation-vacuous block names every survivor its evidence's driver output reports, so the
+  # repair answers them in one round (fix-review.md step 1; tvofi 2026-11-07; #3262's four blocks).
+  why=$(python3 -I "$ROOT/tools/audit/seat/survivor_list.py" check "$v" "$ev") \
+    || die "push-verdict: $(tr '\n' ' ' <<< "$why")"
   t=$(mktemp -d) || die "push-verdict: no temporary directory"
   mkdir -p "$t/w/evidence" && cp "$v" "$t/w/VERDICT.md" && cp -R "$ev"/. "$t/w/evidence/" \
     || { rm -rf "$t"; die "push-verdict: could not stage the verdict and its evidence"; }
@@ -1850,6 +1855,22 @@ B
   out=$(vg "A defect, its log at ~/hpo/x.log. Carry: R10-LIVE"); rc=$?
   [ $rc = 0 ] && [ "$(tip review/7)" != "$r7" ]
   expect "and proposes it with the path written ~/... (the null control)" $?
+  # Owner ruling 2026-11-07 (card 2): a mutation-vacuous block lists every survivor its evidence's
+  # driver output reports; another class over the same evidence is not read (null control).
+  mkdir -p "$W/evmut"; printf '%s\n' "$h1" > "$W/evmut/head.txt"
+  printf 'SURVIVED custom_components/x/a.py:12 GUARD_OFF  if False:\nSURVIVED custom_components/x/a.py:40 RETURN_DEL  pass\n' > "$W/evmut/mutants.log"
+  vm() { printf 'Fix review: blocked %s %s\n\nbus-nonce: %s\n' "$h1" "$1" "$NG" > "$W/vm.md"; seat push-verdict 7 "$W/vm.md" "$W/evmut" 2>&1; }
+  r7=$(tip review/7)
+  out=$(vm "mutation-vacuous: custom_components/x/a.py:12 lives"); rc=$?
+  [ $rc != 0 ] && [ "$(tip review/7)" = "$r7" ] && echo "$out" | grep -q "UNLISTED custom_components/x/a.py:40 .*names 1 of the 2 survivor"
+  expect "push-verdict refuses a mutation-vacuous verdict naming one of two survivors, and review/7 does not move" $?
+  out=$(vm "harness: custom_components/x/a.py:12 lives"); rc=$?
+  [ $rc = 0 ] && [ "$(tip review/7)" != "$r7" ]
+  expect "null control: another blocked class over the same evidence proposes" $?
+  r7=$(tip review/7)
+  out=$(vm "mutation-vacuous: custom_components/x/a.py:12 and custom_components/x/a.py:40 live"); rc=$?
+  [ $rc = 0 ] && [ "$(tip review/7)" != "$r7" ]
+  expect "and proposes the mutation-vacuous verdict once it lists both survivors" $?
   GIT_TRACE2_EVENT=$W/tr2 GIT_TRACE2_CONFIG_PARAMS=http.postBuffer seat push-verdict 7 "$W/merge-clean.md" "$W/ev1" >/dev/null 2>&1
   grep -q '"param":"http.postbuffer","value":"524288000"' "$W/tr2"
   expect "the verdict push runs with a 500 MB http.postBuffer (#2563's HTTP 400)" $?
diff --git a/tools/audit/seat/instruments/survivor_list.py.md b/tools/audit/seat/instruments/survivor_list.py.md
new file mode 100644
index 000000000..d14e86c7c
--- /dev/null
+++ b/tools/audit/seat/instruments/survivor_list.py.md
@@ -0,0 +1,14 @@
+# `survivor_list.py`
+
+- `survivor_list.py` — `check VERDICT.md EVIDENCE_DIR`: for a first line
+  `Fix review: blocked <sha> mutation-vacuous:`, reads every file under the
+  evidence directory for the survivor lines `mutant_run.py` (`--diff`,
+  `--spec`) and `tests/mutation_table.py` (`LIVES`, `--pin-killed`'s
+  `UNPINNED ... -- lives`) print, less a site marked `[triaged equivalent]`,
+  and prints one `UNLISTED <file>:<line>` (or spec name) per survivor the
+  verdict does not name, rc 1. Any other verdict class passes unread. Owner
+  ruling (tvofi 2026-11-07, card 2, NARROW): one block lists every survivor
+  the review found at that head (`fix-review.md` step 1). When: `bus.sh
+  push-verdict` runs it on every verdict, local or relayed by
+  `cloud_relay.sh`. `--self-test` drives each driver format, the
+  other-class null control, and pins the producers' own print statements.
diff --git a/tools/audit/seat/survivor_list.py b/tools/audit/seat/survivor_list.py
new file mode 100644
index 000000000..32b7a7dd6
--- /dev/null
+++ b/tools/audit/seat/survivor_list.py
@@ -0,0 +1,180 @@
+#!/usr/bin/env python3
+"""A `mutation-vacuous` block names every survivor its evidence reports.
+
+    python3 -I tools/audit/seat/survivor_list.py check VERDICT.md EVIDENCE_DIR
+    python3 -I tools/audit/seat/survivor_list.py --self-test
+
+Owner ruling (tvofi, 2026-11-07, waste-study card 2, NARROW): a reviewer that
+blocks `mutation-vacuous` lists every survivor it found at that head in the one
+verdict, so the repair answers them in one round rather than one per round
+(#3262: four blocks, each a new survivor in the same files). `fix-review.md`
+step 1 binds the reviewer; `bus.sh push-verdict` runs `check`, so a local seat
+and a cloud relay (which calls push-verdict) are refused alike.
+
+WHAT IS READ. Every file under EVIDENCE_DIR, for the survivor lines the three
+drivers print:
+  mutant_run.py --diff     `SURVIVED <file>:<line> <OPERATOR>  <mutated line>`
+  mutant_run.py --spec     `SURVIVED <name>` (its automatic NULL is not one)
+  mutation_table.py        `  LIVES <file>:<line> <kind>`, less a site its own
+                           survivor list marks `[triaged equivalent]`
+  mutation_table.py --pin-killed  `  UNPINNED <file>:<line> <kind> -- lives`
+A survivor is LISTED when the verdict holds its key -- `<file>:<line>`, or the
+spec name -- as a whole token. Only the review's own driver output is counted:
+the rule asks for what the review found, never a hunt past it, and a verdict
+whose evidence holds no driver output has nothing to count (rc 0).
+
+WHAT IS CHECKED. Only a first line `Fix review: blocked <40 hex> mutation-vacuous:`.
+Any other class, and `merge`, pass unread. rc 0 listed (or not this class);
+rc 1 one `UNLISTED <key>` line per survivor the verdict omits, then a summary;
+rc 2 unreadable input.
+"""
+from __future__ import annotations
+
+import re
+import sys
+import tempfile
+from pathlib import Path
+
+sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "tests"))
+import mutation_table  # noqa: E402  the --pin-killed survivor grammar's owner
+
+CLASS = re.compile(r"^Fix review: blocked [0-9a-f]{40} mutation-vacuous:")
+SITE = r"(\S+:\d+)"
+DRIVER_LINES = (
+    re.compile(rf"^SURVIVED {SITE} [A-Z_]+\b", re.M),          # mutant_run --diff
+    re.compile(r"^SURVIVED (?!NULL$)([^\s:]+)$", re.M),       # mutant_run --spec
+    re.compile(rf"^  LIVES {SITE} \S+", re.M),                # mutation_table
+)  # --pin-killed's `UNPINNED ... -- lives` is read by its owner, mutation_table.survivor_sites
+TRIAGED = re.compile(rf"^    {SITE} \S+: .*\[triaged equivalent\]$", re.M)
+PRODUCERS = {
+    "tools/audit/seat/mutant_run.py": (
+        'print(f"SURVIVED {rel}:{n} {op}  {new}"',
+        '("SURVIVED " if rc == 0 else "KILLED ") + m["name"]'),
+    "tests/mutation_table.py": (
+        'mark = "LIVES" if verdict == "LIVES"',
+        "print(f\"  {mark} {mut['file']}:{mut['line']} {mut['kind']}{note}\")",
+        '"  [triaged equivalent]"',
+        "def survivor_sites(run: str | None) -> list[str]:"),
+}
+
+
+def survivors(texts: list[str]) -> list[str]:
+    """Every survivor key the driver outputs report, less triaged-equivalent sites."""
+    found, triaged = set(), set()
+    for t in texts:
+        for rx in DRIVER_LINES:
+            found.update(rx.findall(t))
+        found.update(k.split(" ", 1)[0] for k in mutation_table.survivor_sites(t))
+        triaged.update(TRIAGED.findall(t))
+    return sorted(found - triaged)
+
+
+def unlisted(verdict: str, texts: list[str]) -> list[str]:
+    """The survivors a `mutation-vacuous` verdict does not name; [] for any other verdict."""
+    if not CLASS.match(verdict):
+        return []
+    return [k for k in survivors(texts)
+            if not re.search(rf"(?<![\w./-]){re.escape(k)}(?![\w])", verdict)]
+
+
+def evidence_texts(ev: Path) -> list[str]:
+    return [p.read_text(encoding="utf-8", errors="replace")
+            for p in sorted(ev.rglob("*")) if p.is_file()]
+
+
+def check(verdict_path: str, ev_dir: str) -> int:
+    try:
+        verdict = Path(verdict_path).read_text(encoding="utf-8")
+        ev = Path(ev_dir)
+        if not ev.is_dir():
+            raise OSError(f"no evidence directory {ev_dir}")
+        texts = evidence_texts(ev)
+    except (OSError, UnicodeDecodeError) as exc:
+        print(f"survivor_list: unreadable: {exc}")
+        return 2
+    missing = unlisted(verdict, texts)
+    for k in missing:
+        print(f"UNLISTED {k}")
+    if missing:
+        n = len(survivors(texts))
+        print(f"a mutation-vacuous verdict names {n - len(missing)} of the {n} survivor(s) "
+              f"its evidence reports; list every one (fix-review.md step 1)")
+        return 1
+    return 0
+
+
+def _self_test() -> int:
+    fails, ran = [], []
+
+    def t(name, cond):
+        ran.append(name)
+        print(("ok   " if cond else "FAIL ") + name)
+        if not cond:
+            fails.append(name)
+
+    h = "a" * 40
+    mv = f"Fix review: blocked {h} mutation-vacuous: "
+    diff_two = ("SURVIVED custom_components/x/a.py:12 GUARD_OFF  if False:\n"
+                "SURVIVED custom_components/x/a.py:40 RETURN_DEL  pass\n")
+    t("two diff-mode survivors are both read",
+      survivors([diff_two]) == ["custom_components/x/a.py:12", "custom_components/x/a.py:40"])
+    t("a verdict naming one of two is refused, naming the other",
+      unlisted(mv + "custom_components/x/a.py:12 lives", [diff_two]) == ["custom_components/x/a.py:40"])
+    t("a verdict naming both passes",
+      unlisted(mv + "custom_components/x/a.py:12 and custom_components/x/a.py:40", [diff_two]) == [])
+    t("null control: another blocked class with the same evidence passes",
+      unlisted(f"Fix review: blocked {h} class-open: seam", [diff_two]) == [])
+    t("null control: a merge verdict passes",
+      unlisted(f"Fix review: merge {h}", [diff_two]) == [])
+    t("a key is a whole token: :12 does not list :120",
+      unlisted(mv + "custom_components/x/a.py:120", ["SURVIVED custom_components/x/a.py:12 CALL_DEL  pass\n"])
+      == ["custom_components/x/a.py:12"])
+    t("a key is a whole token: tools/setup.py:3 does not list setup.py:3",
+      unlisted(mv + "tools/setup.py:3", ["SURVIVED setup.py:3 CALL_DEL  pass\n"]) == ["setup.py:3"])
+    t("spec mode: a named survivor is read, NULL is not",
+      survivors(["SURVIVED NULL\nSURVIVED guard_off\nKILLED other\n"]) == ["guard_off"])
+    table = ("  LIVES custom_components/x/b.py:7 cmp\n"
+             "  ok    custom_components/x/b.py:9 cmp  -- killed\n"
+             "  LIVES custom_components/x/b.py:11 const\n\n"
+             "  2 survivor(s) of 3 evaluated = 33.3%, cap 50.0%\n"
+             "    custom_components/x/b.py:7 cmp: x < y\n"
+             "    custom_components/x/b.py:11 const: n = 3  [triaged equivalent]\n")
+    t("mutation_table: LIVES read, a triaged-equivalent site and a kill are not",
+      survivors([table]) == ["custom_components/x/b.py:7"])
+    t("--pin-killed: an UNPINNED ... -- lives line is read",
+      survivors(["  UNPINNED custom_components/x/c.py:3 guard -- lives\n"]) == ["custom_components/x/c.py:3"])
+    t("evidence with no driver output counts nothing",
+      unlisted(mv + "x", ["RESULT mutant=a rc=1 fails=2\n"]) == [])
+    with tempfile.TemporaryDirectory() as d:
+        ev = Path(d, "ev")
+        (ev / "sub").mkdir(parents=True)
+        (ev / "head.txt").write_text(h + "\n")
+        (ev / "sub" / "mutants.log").write_text(diff_two)
+        v = Path(d, "V.md")
+        v.write_text(mv + "custom_components/x/a.py:12\n\nbus-nonce: " + "0" * 32 + "\n")
+        t("check reads nested evidence and returns rc 1", check(str(v), str(ev)) == 1)
+        v.write_text(mv + "custom_components/x/a.py:12, custom_components/x/a.py:40\n")
+        t("check returns rc 0 once every survivor is listed", check(str(v), str(ev)) == 0)
+        t("check returns rc 2 for a missing evidence directory", check(str(v), d + "/none") == 2)
+    # The formats above are the producers' own print statements: one that changes shape turns
+    # this red, rather than every survivor silently reading as none (fixer.md step 11).
+    root = Path(__file__).resolve().parents[3]
+    for rel, anchors in PRODUCERS.items():
+        src = (root / rel).read_text(encoding="utf-8")
+        for a in anchors:
+            t(f"{rel} still prints {a!r}", a in src)
+    print(f"survivor_list self-test: {len(ran)} checks, {len(fails)} failed")
+    return 1 if fails else 0
+
+
+def main(argv: list[str]) -> int:
+    if argv == ["--self-test"]:
+        return _self_test()
+    if len(argv) == 3 and argv[0] == "check":
+        return check(argv[1], argv[2])
+    print(__doc__.split("\n\n")[1])
+    return 2
+
+
+if __name__ == "__main__":
+    sys.exit(main(sys.argv[1:]))

## Before you return the verdict (P275)
Run `python3 -I tools/audit/carry_audit.py check --body <PR body file> --comments <file holding [{"id": 0, "body": <verdict.md text>}]>`. Give every reported item its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>`;
an evidence line flagged by its wording takes `Carry: dismissed: evidence, not a finding`. Return the verdict only at rc 0.
