# Review packet #3020
head: d1ee705999d5c3de1ac5d071bb8fd91051dbbd4c
base: 5d4e0bcfb88413ddf9ca7f0884c36bbec9235447

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: pending
CodeQL id=124378115141 success
arch-score / arch-score id=124378028925 success
arm id=124377929381 skipped
budget-raise-gate / budget-raise-gate id=124378029020 success
cancel-superseded id=124377887731 success
codeql / Analyze (actions) id=124378028911 success
codeql / Analyze (javascript-typescript) id=124378028914 success
codeql / Analyze (python) id=124378029053 success
governance / delivery-status id=124378028901 success
governance / delivery-status-publish id=124378030077 skipped
governance / env-matrix id=124378029009 in_progress
governance / instrument-self-tests id=124378029035 in_progress
governance / policy-docs id=124378028995 success
governance / record id=124378030684 skipped
governance / wave-script id=124378029004 success
hassfest / hassfest id=124378028804 success
kernel-points id=124378030308 skipped
prelude id=124377888066 success
refresh id=124377888038 success
tests / arch-instrument id=124378182425 success
tests / briefs id=124378029029 success
tests / browser id=124378182504 in_progress
tests / closure-scope id=124378029049 success
tests / closures id=124378182441 in_progress
tests / coverage id=124378182440 in_progress
tests / fast (3.14) id=124378182426 in_progress
tests / mutation id=124378029027 success
tests / mutation-autofix id=124378393847 skipped
tests / mutation-pins id=124378393788 skipped
tests / nightly-ha id=124378184422 skipped
tests / nightly-status id=124378028947 success
tests / replay id=124378184260 skipped
tests / typing id=124378182434 success
validate / validate-hacs id=124378028958 success

## Refusals
none

## Advisories
none

## carry_audit at the head
CARRY-AUDIT: 0 finding item(s): 0 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
unverified git show origin/main:tools/audit/seat/roster_queue.py
             `git show` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  ok         tests/structure.py
             `tests/structure.py` is in the tree at this head

FIGURES: 1 resolved, 1 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
none

## Three-dot diff
diff --git a/dev/programme/delivery/3020.md b/dev/programme/delivery/3020.md
new file mode 100644
index 000000000..24e7bf8d3
--- /dev/null
+++ b/dev/programme/delivery/3020.md
@@ -0,0 +1 @@
+- [#3020](https://github.com/tvofi/heatpump_optimizer/pull/3020) — **open**, triage: s8 batch 78 (P315 ruling) (R10-TRIAGE-S6)
diff --git a/dev/programme/triage/s6-batch78.md b/dev/programme/triage/s6-batch78.md
new file mode 100644
index 000000000..69b72e0f4
--- /dev/null
+++ b/dev/programme/triage/s6-batch78.md
@@ -0,0 +1,79 @@
+# Proposal triage, session s8, batch 78 (P315)
+
+The rolling batch (V182) after batch 77 (handoff `triage-s8-batch77`). Facts were read at
+origin/main `5d4e0bcfb`, in the orchestrator's `seat-ledger.md` and `s7/roster-queue-s7.txt`, and
+in the R10-FLY-BEAT-FETCH-RACE group file the orchestrator queued
+(`s8/beatrace/R10-FLY-BEAT-FETCH-RACE.json`).
+
+## P315: roster_queue.py `run` dies before writing a report line, so a caller reads the previous op's line
+
+Verdict: ACCEPT narrowed, a carry on **R10-FLY-BEAT-FETCH-RACE**, as the orchestrator directs. That
+group is S and not started, and owns the roster write path's transient failures (`roster_edit.py`
+`fetch_origin`). This carry adds `tools/audit/seat/roster_queue.py` to its files.
+- **The rule.** `run_queue` writes exactly one report line for every op it attempts, whatever
+  happens. An exception in the op, or in the lint clone's `git fetch` and `git checkout`, becomes
+  `roster: <op> <group> FAILED <ExceptionType>: <message>`. The run then stops with a nonzero rc,
+  never silently.
+- **A missing `--lint-clone` is refused by name** before the first op:
+  `roster: lint clone <path> missing; nothing applied`, rc 2.
+- **REJECTED: having the runner re-clone the lint clone itself.** Provisioning the clone is the
+  caller's (`--lint-clone` is "a checkout it owns", the runner's own docstring). A re-clone at an
+  arbitrary path would also hide a misconfigured path behind a network side effect.
+- **Order with P300.** P300 (`s6-batch68.md`, R10-ORCH-ROSTER-SCHEMA) adds `--mark` to the same
+  `run_queue`. A FAILED line marks `#refused` there. The two carries touch distinct seams (the
+  exception path and the marking), and whichever lands second merges main.
+- **Hold.** This carry waits until the group is on the roster branch. Its own append-group was one
+  of the ops the slip falsely marked `#done (already)`, and is re-queued.
+
+Source: the orchestrator s8's message of 2026-10-31 (a slip, under slips-become-proposals).
+
+Instances:
+- **The defect, read at main.** `run_queue` (`roster_queue.py:93`) calls
+  `_git("fetch", "-q", "origin", cwd=a.lint_clone)` at line 123. `_git` (lines 45-46) is a bare
+  `subprocess.run` with `cwd=`, so a missing directory raises `FileNotFoundError` from the
+  subprocess before `rep()` writes anything.
+- **The ledger.** `seat-ledger.md` lines 2765-2769 hold five `roster s8: no report line written
+  (rc=1): ... FileNotFoundError` lines, and the ledger holds 17 `refused exception
+  FileNotFoundError` lines in all.
+- **The consequence**, by the orchestrator's account and its queue. The s8 loop read the report's
+  last line, which belonged to the previous op, as this op's result and marked 12 ops
+  `#done (already)` that never landed. Two of them were carries that #3014's review depended on.
+  One was the append-group of R10-FLY-BEAT-FETCH-RACE itself: queue line 520 reads `#done
+  (already) append-group R10-FLY-BEAT-FETCH-RACE ...`, line 532 re-queues it, and the group is
+  absent from `origin/handoff/audit-r10-roster` at this read.
+- **Already done, out of tree.** The s8 loop now trusts only a freshly appended line. The lint
+  clone was re-cloned, and the 12 ops were re-queued.
+
+Cost:
+- About 10 lines in `run_queue`: a try/except around each op writing the FAILED line and
+  returning nonzero, and a missing-directory check on `--lint-clone`. Add two self-test rows.
+- No new file, writer or API call. `roster_queue.py` is not a capped file.
+
+Binding:
+- One deleted directory turned into 12 ops reported landed that had not, two of them gating a
+  review, found only by reading the roster back.
+- About 10 lines turn that silent false result into a loud failure. That is clearly positive.
+- The caller-side fix (trust only a fresh line) is correct but lives only out of tree. The tree's
+  runner must not depend on every caller knowing its failure leaves no line.
+
+Carry text (for `roster_edit.py append-carry R10-FLY-BEAT-FETCH-RACE`, citing
+`triage: dev/programme/triage/s6-batch78.md#P315`): "P315 (orchestrator 2026-10-31, slip). Adds
+tools/audit/seat/roster_queue.py to this group's files.
+- `run_queue` (`roster_queue.py:93` at 5d4e0bcfb) writes exactly one report line per op attempted.
+  Any exception in the op, or in the lint clone's `git fetch`/`git checkout` (`_git`, line 123),
+  becomes `roster: <op> <group> FAILED <ExceptionType>: <message>`, and the run stops nonzero.
+- A missing `--lint-clone` directory is refused before the first op:
+  `roster: lint clone <path> missing; nothing applied`, rc 2.
+- The runner never re-clones.
+- Observed 2026-10-30/31: a deleted lint clone raised `FileNotFoundError` at line 123 before any
+  report line. The caller read the previous op's line, and 12 ops were marked `#done (already)`
+  that never landed (`seat-ledger.md` 2765-2769: `no report line written (rc=1)`). This group's
+  own append-group was one of them.
+- Self-test rows:
+  - With `--lint-clone` pointing at a missing directory, the report gains the named refusal and
+    rc is 2. Today it raises with no line.
+  - An op whose subprocess raises gains one FAILED line naming the exception, and rc is nonzero.
+  - Null: a run whose ops all push writes one `pushed` line per op, unchanged.
+- One mutant: remove the per-op except, and the raising row writes no line.
+- P300's `--mark` (R10-ORCH-ROSTER-SCHEMA) marks a FAILED op `#refused`. Whichever lands second
+  merges main."

