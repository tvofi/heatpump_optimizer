# Review packet #3026
head: 234e6df8739b8403a5bc295cd9c8006f7af8dc7b
base: 2376d3f9e487223bcb6c73b1f618f0db396d2660

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: pending
CodeQL id=124403729700 success
arch-score / arch-score id=124403691403 success
arm id=124403582052 skipped
budget-raise-gate / budget-raise-gate id=124403691438 success
cancel-superseded id=124403586913 success
codeql / Analyze (actions) id=124403691440 success
codeql / Analyze (javascript-typescript) id=124403691385 success
codeql / Analyze (python) id=124403691381 success
gate id=124408803942 in_progress
governance / delivery-status id=124403691471 success
governance / delivery-status-publish id=124403692332 skipped
governance / env-matrix id=124403691496 success
governance / instrument-self-tests id=124403691567 success
governance / policy-docs id=124403691448 success
governance / record id=124403692367 skipped
governance / wave-script id=124403691533 success
hassfest / hassfest id=124403691421 success
kernel-points id=124403692419 skipped
pr-contract / pr-contract id=124408674656 success
prelude id=124403586825 success
refresh id=124403586683 success
tests / arch-instrument id=124403817106 success
tests / briefs id=124403691504 success
tests / browser id=124403817064 success
tests / ci-ratchet id=124404994432 skipped
tests / claims-autofix id=124404947177 skipped
tests / closure-scope id=124403691667 success
tests / closures id=124403817175 success
tests / closures-autofix id=124404994617 skipped
tests / coverage id=124403817140 success
tests / coverage-ratchet id=124404072372 success
tests / fast (3.14) id=124403817081 success
tests / graders-head-copy id=124404072314 success
tests / lane-proofs id=124404946305 success
tests / mutation id=124403691538 success
tests / mutation-autofix id=124403890705 skipped
tests / mutation-pins id=124403890473 skipped
tests / nightly-ha id=124403818204 skipped
tests / nightly-status id=124403691576 success
tests / replay id=124403818187 skipped
tests / typing id=124403817104 success
validate / validate-hacs id=124403691453 success

## Refusals
none

## Advisories
none

## carry_audit at the head
CARRY-AUDIT: 0 finding item(s): 0 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
unverified git show origin/main:tests/entities.py
             `git show` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  unverified git log -S'_hb_stdlib_reads' origin/main -- tests/entities.py
             `git log` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  unverified git show <ref>:BODY.md | grep -iE 'task port|task-port'
             `git show` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  ok         tests/structure.py
             `tests/structure.py` is in the tree at this head

FIGURES: 1 resolved, 3 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
none

## Three-dot diff
diff --git a/dev/programme/delivery/3026.md b/dev/programme/delivery/3026.md
new file mode 100644
index 000000000..130ba00bc
--- /dev/null
+++ b/dev/programme/delivery/3026.md
@@ -0,0 +1 @@
+- [#3026](https://github.com/tvofi/heatpump_optimizer/pull/3026) — **open**, triage: s8 batch 81 (P318 ruling) (R10-TRIAGE-S6)
diff --git a/dev/programme/triage/s6-batch81.md b/dev/programme/triage/s6-batch81.md
new file mode 100644
index 000000000..fa9cd95e1
--- /dev/null
+++ b/dev/programme/triage/s6-batch81.md
@@ -0,0 +1,77 @@
+# Proposal triage, session s8, batch 81 (P318)
+
+The rolling batch (V182) after batch 80 (handoff `triage-s8-batch80`). Facts were read at
+origin/main `2376d3f9e`, on the roster branch, and in the `handoff-body/*` refs on origin.
+
+## P318: tests/entities.py dies on macOS at the heartbeat sampler, hiding every later check
+
+Verdict: ACCEPT narrowed, option (a), a carry on **R10-NIGHTLY-HB-RESPAWN** (`queued`, S). That
+group owns the heartbeat lane's sampler seam (`tests/nightly_ha.py`), its after-edge
+R10-NIGHTLY-PYSPY-RETRY is `done`, and it is dispatchable now. The carry adds `tests/entities.py`
+to its files and may be dispatched alone, ahead of the group's other carries.
+- **The rule.** The module-level arm at `tests/entities.py:18392`
+  (`if _nightly.importlib.util.find_spec("_remote_debugging") is not None:`) runs
+  `_hb_stdlib_reads` (line 18368), which samples a live child process. When that raises
+  `PermissionError` on Darwin, the arm prints one named line,
+  `SKIP stdlib sampler control: macOS denies the task port (<message>)`, and the module goes on.
+  Every later check still runs.
+- **The skip is that narrow on purpose.** It applies on `sys.platform == "darwin"` with
+  `PermissionError` only. On Linux, where CI runs the arm, the error still fails, so the arm keeps
+  its power where it is graded.
+- **REJECTED (b), routing `entities.py` to a cloud or Linux run whenever the local host is
+  Darwin.** It moves a 40,000-line script's whole run off-host to save one arm. Every local
+  fixer's scoped gate would pay a cloud round trip, and local runs are the cheap path the gate is
+  built on.
+- **REJECTED (c), a seat-preamble note.** The run still dies at the same line, and every check
+  after it is still unread. That is the exact cost below, which a note does not remove.
+
+Source: the orchestrator s8's message of 2026-10-31 (a recurring slip, 3 instances on
+2026-10-30/31).
+
+Instances:
+- **The defect, read at main.** `_hb_stdlib_reads` (`tests/entities.py:18368`) spawns a child and
+  runs `_nightly._STDLIB_SAMPLE` against its pid. Its own docstring says a sampler of another
+  process needs a privilege "which the heartbeat container is given and this host is not". The arm
+  at line 18392 runs it at module top level with no handler, so the exception ends the script.
+- **In fixer bodies.** Of the `handoff-body/*` tips on origin, four record the local death:
+  - `r10-cop-partload-p2`: "the nightly lane's stdlib sample dies with `PermissionError: Cannot get
+    task port` (macOS task-port entitlement). The same 44 FAIL li[nes at the merge base]".
+  - `r10-fly-beat-fetch-race`: "Local run caveat ...".
+  - `r10-hotfix-learner-inputs`: "Both runs then stop on the same ...".
+  - `r10-ux-health-p2`: "`entities.py`'s heartbeat arm a task port for its own child".
+- **The cost, by the orchestrator's account.** #3022 went red in CI on `entities.py`'s R10
+  N-log-flood barrier, a one-line classification a full local run catches in about 6 min. The
+  local run had died first, so the fixer read the base's identical death as "fails the same way
+  on the base". That cost one review round and a hotfix delay.
+- **Origin.** The arm arrived in `120cd1bb6` (2026-10-29, "nightly-ha: sample heartbeat stalls with
+  CPython's own remote unwinder where it ships one", R10-FLY-NIGHTLY-HB, done). That is why the
+  three instances cluster on 2026-10-30/31.
+
+Cost:
+- About 6 lines: a `try`/`except PermissionError` around the arm, gated on Darwin, printing the
+  named SKIP. Add one self-test row.
+- No new file, check or CI change. `tests/entities.py` is not a capped file.
+- The scoped gate keeps running `entities.py` locally.
+
+Binding: four fixer runs in two days lost every check after line 18392, and one of those misses
+cost a review round on a hotfix, against a 6-line guard. Clearly positive. The guard is that narrow
+so CI's Linux run still grades the sampler.
+
+Carry text (for `roster_edit.py append-carry R10-NIGHTLY-HB-RESPAWN`, citing
+`triage: dev/programme/triage/s6-batch81.md#P318`): "P318 (orchestrator 2026-10-31, recurring
+slip). Adds tests/entities.py to this group's files. May be dispatched alone, ahead of this group's
+other carries.
+- The module-level arm at `tests/entities.py:18392` (at 2376d3f9e), which runs `_hb_stdlib_reads`
+  (line 18368) against a live child, catches `PermissionError` only when
+  `sys.platform == "darwin"`. It prints `SKIP stdlib sampler control: macOS denies the task port
+  (<message>)` and lets the module continue.
+- On any other platform, or any other exception, behaviour is unchanged: the arm still fails.
+- Observed 2026-10-30/31: four fixer bodies record the local run dying there
+  (`handoff-body/r10-cop-partload-p2`, `r10-fly-beat-fetch-race`, `r10-hotfix-learner-inputs`,
+  `r10-ux-health-p2`). #3022 then went red in CI on a later `entities.py` check a full local run
+  would have caught.
+- Self-test rows:
+  - With the sampler patched to raise `PermissionError` and the platform forced to `darwin`, the
+    module reaches its final summary and prints the SKIP line once.
+  - Null: forced to `linux`, the same raise still fails the run.
+- One mutant: drop the platform condition, and the linux row passes when it must fail."

