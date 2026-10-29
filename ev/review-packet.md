# Review packet #2961
head: 3d3d7edd16bb4e291e865973be64e378d49c72fa
base: 279578074a17cb2c7f527f5e28da0de4e2006db0

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: red
CodeQL id=123619479935 success
arch-score / arch-score id=123683354934 success
arm id=123618736926 skipped
budget-raise-gate / budget-raise-gate id=123683345280 success
cancel-superseded id=123683347491 success
codeql id=123683354662 skipped
codeql / Analyze (actions) id=123683285259 success
codeql / Analyze (javascript-typescript) id=123683285989 success
codeql / Analyze (python) id=123683285673 success
gate id=123684256014 success
governance id=123683294357 skipped
governance / delivery-status id=123683286337 success
governance / delivery-status-publish id=123683285466 skipped
governance / env-matrix id=123683285575 success
governance / instrument-self-tests id=123683284954 success
governance / policy-docs id=123683285034 success
governance / record id=123683286568 skipped
governance / wave-script id=123683284933 success
hassfest id=123683294791 skipped
hassfest / hassfest id=123683362825 success
kernel-points id=123683341977 skipped
pr-contract / pr-contract id=123683897010 success
prelude id=123683293577 success
refresh id=123683360118 success
tests id=123683295124 skipped
tests / arch-instrument id=123683288553 success
tests / briefs id=123683286300 success
tests / browser id=123683286660 success
tests / ci-ratchet id=123683289965 skipped
tests / claims-autofix id=123683288938 skipped
tests / closure-scope id=123683285524 success
tests / closures id=123683287789 success
tests / closures-autofix id=123683289151 skipped
tests / coverage id=123683287657 success
tests / coverage-ratchet id=123683288993 success
tests / fast (3.14) id=123683288299 success
tests / graders-head-copy id=123683288989 success
tests / lane-proofs id=123683289329 success
tests / mutation id=123683285428 success
tests / mutation-autofix id=123683288746 skipped
tests / mutation-pins id=123683286736 skipped
tests / nightly-ha id=123683288253 skipped
tests / nightly-status id=123683284816 failure
tests / replay id=123683288596 skipped
tests / typing id=123683287591 success
validate id=123683293841 skipped
validate / validate-hacs id=123683285847 success

## Refusals
none

## Advisories
none

## carry_audit at the head
NOTE body item 88e6cff9: R10-FLY-LEDGER-SAMPLE
NOTE body item b53aef9e: dismissed:a record recounts, it is not rewritten; the correction lives where the cause is named
NOTE body item 0968efad: R10-FRICTION-MUTATION-SURVIVOR
NOTE body item 503618af: R10-FLY-LEDGER-SAMPLE
NOTE body item 447588b0: dismissed:paid within the cap, no raise
NOTE body item 9212ff30: dismissed:the untaught-vocabulary fold is `R10-RCA-FRICTION-RESIDUE` section 4's countermeasure
NOTE body item e649a80d: dismissed:environment, the check-run conclusions and times were re-read
CARRY-AUDIT: 7 finding item(s): 7 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
ok         node tools/policy/policy_lint.mjs --stats --since v7.0.4
             `tools/policy/policy_lint.mjs` is in the tree at this head
  ok         python3 dev/audit/rca/mutation-survivor/mutblocks.py <window PR list>
             `dev/audit/rca/mutation-survivor/mutblocks.py` is in the tree at this head
  unverified git log -1 --format=%s
             `git log` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  unverified git rev-list --first-parent --merges v7.0.4..88c6ad5bb
             `git rev-list` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  unverified git diff --quiet $m^1...$m^2 -- 'custom_components/*.py'
             `git diff` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  ok         bash dev/audit/rca/mutation-survivor/pinsbefore.sh 2817 2832 2834
             `dev/audit/rca/mutation-survivor/pinsbefore.sh` is in the tree at this head
  ok         gh api repos/tvofi/heatpump_optimizer/issues/<N>/comments
             gh api: every long flag accepted
  unverified git log -S'"skip-nothing-killed", "skip-head-moved"' -- tests/closure.py
             `git log` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  ok         gh api repos/tvofi/heatpump_optimizer/commits/4fbe4c6a5/check-runs
             gh api: every long flag accepted

FIGURES: 5 resolved, 4 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
none

## Three-dot diff
diff --git a/.claude/rules/ci-autofix.md b/.claude/rules/ci-autofix.md
index 5185aea27..7fa72f3a2 100644
--- a/.claude/rules/ci-autofix.md
+++ b/.claude/rules/ci-autofix.md
@@ -13,58 +13,60 @@ paths:
 Same-repo PRs run three jobs (`.github/workflows/tests.yml`). **Before the PR exists
 nothing waits**: a handoff ref runs no job, so a red `prepr.sh` step 6d predicts is repaired
 before handoff (`--single`; for INERT READS `python3 tools/pr/ci_predict.py --apply-inert`,
-which writes the Linux recording's entry, not a `--single`). Once it exists, if `tests / closures` is
+which writes the Linux recording's entry). Once it exists, if `tests / closures` is
 `UNDER-SCOPED`, `tests / fast` fails `INHERITED CLAIMS` or `tests / mutation` refuses unpinned sites, **wait** --
-a `DIRTY` head queues no run, so no bot commit comes. Do not open a parallel PR, do not
-Darwin `--single` an under-scope CI already recorded, and do not hand-empty claim files
-that match `origin/main`. Darwin can `--single` a **new** node script, or grow a node
-closure; it cannot replace a Linux node recording.
+a `DIRTY` head queues no run, so no bot commit comes. Do not open a parallel PR,
+Darwin `--single` an under-scope CI already recorded, or hand-empty claim files
+that match `origin/main`. Darwin can `--single` a **new** node script or grow a node
+closure, never replace a Linux node recording.
 
 **That wait holds only while the job reports it is
 repairing.** Each job pushes on `changed` alone and prints its status to the
 job summary (#523). `closures-autofix` goes red on `skip-failed-recording`,
 `skip-merge-failed`, `skip-still-fails`, `skip-unchanged`,
 `skip-classifier-disagrees` and `skip-manual-repair-owed` — a repair was owed
-and it did not happen. **A red autofix job means no bot commit comes.** The
-`--single` prohibition above, which assumes the bot will merge, lapses. Read the summary
+and did not happen. **A red autofix job means no bot commit comes**; the
+`--single` prohibition above lapses. Read the summary
 line, re-derive the script it names and commit `tests/closures.json`; Python
 lanes record through `sys.addaudithook`, so Darwin is sound for them — except
-the inert dimension, which is Linux-recorded (`strace`-only): the bot merges
+the Linux-recorded (`strace`-only) inert dimension: the bot merges
 INERT READS from CI recordings too (#1886, R9-CI-1). On `skip-failed-recording` a
-script the check named (or its driven child) stopped while being recorded — fix it first; re-deriving would record the same truncation.
+named script (or its driven child) stopped while recorded: fix it first, as re-deriving records the same truncation.
 
-**What green means, exactly — read the summary line, not the tick.** Green is
+**What green means — read the summary line, not the tick.** Green is
 `changed` (repaired and pushed), `skip-clean` or `skip-not-under-scoped` (no
 repair was owed *to the bot*), or `skip-not-allowed` (it declined to
 classify). It runs the base's `tests/closure.py`: if that stops early
 (a PR moving a file out of INERT) where `closures` printed UNDER-SCOPED, the
 status is `skip-classifier-disagrees`; any other failed check (PHANTOM, NOT A
-FILE, an INERT pair) is `skip-manual-repair-owed`, so `skip-not-under-scoped` means it passed (#1864). `claims-autofix` reddens on nothing it
-can return today — `apply_inherited_claims` has no failure status, and its
-`skip-not-inherited` is the ordinary answer for every unrelated `fast`
-failure — so its summary line is its only signal.
+FILE, an INERT pair) is `skip-manual-repair-owed`, so `skip-not-under-scoped` means it passed (#1864). `claims-autofix` never reddens
+(`apply_inherited_claims` has no failure status; `skip-not-inherited` answers
+every unrelated `fast` failure): its summary line is its only signal.
 
-**Three paths still end green unrepaired.**
+**Four paths still end green unrepaired.**
 
 - **A committed phantom.** `check` fails the `closures` job when the committed
   table lists a path that is not a file (#1310), but the autofix reports no
   UNDER-SCOPED and stays green: a recording cannot drop a dead path. Repair the
   table: `python3 tests/closure.py prune`.
-- **The loop guard.** After the bot pushes, the next run's head subject is
-  `ci: re-record closures`, so `autofix_allowed` returns false *before* any
-  classification runs: if that run is still UNDER-SCOPED the status is
-  `skip-not-allowed` and no second commit comes.
+- **The loop guard.** After the bot pushes, the next head's subject is
+  `ci: re-record closures`, so `autofix_allowed` refuses *before* classifying:
+  a still UNDER-SCOPED run reads `skip-not-allowed`, and no second commit comes.
 - **A truncated recording masking the under-scope.** `check` never inspects a
   recording's `rc`, and a script that exits early records only what it
   reached — so where that truncation hides the *only* under-approximation,
   `check` passes and the job is green on `skip-clean` — or on `changed`, since
   an unnamed script's cut-short recording is left out (R9-CI-1). `skip-failed-recording`
-  fires only *after* UNDER-SCOPED is printed, deliberately: unrelated
+  fires only *after* UNDER-SCOPED prints, deliberately: unrelated
   `no-copies` and NOT-A-FILE failures fail recordings too, and their closures
   were never stale.
 
   A failed recording reads files a clean run never does (`linecache`): an
   UNDER-SCOPED beside one may be an artefact. Fix the script; a push re-records.
+- **A survivor.** `mutation-autofix` pins kills only, so a site no driver kills
+  leaves it green, `tests / mutation` red for good (#2840). `pinned by
+  mutation-autofix` is a prediction until a `mutation-pins` log or `--pin-killed`
+  kills the site; a `-- lives` line is the seat's.
 
 | Failure | Job | Commit subject | Code |
 |---|---|---|---|
@@ -72,18 +74,18 @@ failure — so its summary line is its only signal.
 | `INHERITED CLAIMS` | `claims-autofix` | `ci: drop inherited claims` | `env_drift.apply_inherited_claims` |
 | unpinned sites | `mutation-autofix` | `ci: pin killed mutants` | `mutation_table.apply_pins` |
 
-Those subjects are loop guards. The job dispatches `ci.yml -f pr -f base` once, not four workflows;
-a `GITHUB_TOKEN` push's `pull_request` runs are held `action_required`, so the one required check `gate` and the `tests / *` units are ABSENT at a bot head
-until a run is approved: all three approve them (kept until M-3), fail-soft while their secrets are
-absent, when an App push or body edit cures it. Absent is not green (`orchestrator.md` section 11).
+Those subjects are loop guards. The job dispatches `ci.yml -f pr -f base` once;
+a `GITHUB_TOKEN` push's `pull_request` runs are held `action_required`, so the required `gate` and the `tests / *` units are ABSENT at a bot head
+until approved: all three jobs approve them (kept until M-3), fail-soft without their
+secrets, when an App push or body edit cures it. Absent is not green (`orchestrator.md` section 11).
 
-When `mutation-autofix` goes red, run `--pin-killed` yourself. After `ci: pin killed mutants`
-the reviewer re-checks the body's `## Red checks` `mutation` line, which a pin stales. Do not automate survivor triage,
+When `mutation-autofix` goes red, run `--pin-killed` yourself. A `ci: pin killed mutants`
+stales the body's `## Red checks` `mutation` line; the reviewer re-checks it. Do not automate survivor triage,
 golden drift, structure budgets, `no-copies`, orphan → `INERT`, or briefs lint. A new selectable script with **no** recording is
 not UNDER-SCOPED — add it to a derive lane or `--single` it; autofix cannot invent a trace.
 
 ## A driver-file conflict: one bot merges it, none autofixes it
 
-CI never runs on a `DIRTY` pull request, so no job is red to key on. Do not replace a driver
+CI never runs on a `DIRTY` pull request: no job is red to key on. Do not replace a driver
 with `merge=union`. Only `.github/workflows/merge-main.yml` pushes a resolution (tvofi,
 2026-10-08): `ci: merge main`, where `main`'s drivers resolve every conflicting file.
diff --git a/.cursor/rules/ci-autofix.mdc b/.cursor/rules/ci-autofix.mdc
index c93008363..c60113e01 100644
--- a/.cursor/rules/ci-autofix.mdc
+++ b/.cursor/rules/ci-autofix.mdc
@@ -8,58 +8,60 @@ alwaysApply: true
 Same-repo PRs run three jobs (`.github/workflows/tests.yml`). **Before the PR exists
 nothing waits**: a handoff ref runs no job, so a red `prepr.sh` step 6d predicts is repaired
 before handoff (`--single`; for INERT READS `python3 tools/pr/ci_predict.py --apply-inert`,
-which writes the Linux recording's entry, not a `--single`). Once it exists, if `tests / closures` is
+which writes the Linux recording's entry). Once it exists, if `tests / closures` is
 `UNDER-SCOPED`, `tests / fast` fails `INHERITED CLAIMS` or `tests / mutation` refuses unpinned sites, **wait** --
-a `DIRTY` head queues no run, so no bot commit comes. Do not open a parallel PR, do not
-Darwin `--single` an under-scope CI already recorded, and do not hand-empty claim files
-that match `origin/main`. Darwin can `--single` a **new** node script, or grow a node
-closure; it cannot replace a Linux node recording.
+a `DIRTY` head queues no run, so no bot commit comes. Do not open a parallel PR,
+Darwin `--single` an under-scope CI already recorded, or hand-empty claim files
+that match `origin/main`. Darwin can `--single` a **new** node script or grow a node
+closure, never replace a Linux node recording.
 
 **That wait holds only while the job reports it is
 repairing.** Each job pushes on `changed` alone and prints its status to the
 job summary (#523). `closures-autofix` goes red on `skip-failed-recording`,
 `skip-merge-failed`, `skip-still-fails`, `skip-unchanged`,
 `skip-classifier-disagrees` and `skip-manual-repair-owed` — a repair was owed
-and it did not happen. **A red autofix job means no bot commit comes.** The
-`--single` prohibition above, which assumes the bot will merge, lapses. Read the summary
+and did not happen. **A red autofix job means no bot commit comes**; the
+`--single` prohibition above lapses. Read the summary
 line, re-derive the script it names and commit `tests/closures.json`; Python
 lanes record through `sys.addaudithook`, so Darwin is sound for them — except
-the inert dimension, which is Linux-recorded (`strace`-only): the bot merges
+the Linux-recorded (`strace`-only) inert dimension: the bot merges
 INERT READS from CI recordings too (#1886, R9-CI-1). On `skip-failed-recording` a
-script the check named (or its driven child) stopped while being recorded — fix it first; re-deriving would record the same truncation.
+named script (or its driven child) stopped while recorded: fix it first, as re-deriving records the same truncation.
 
-**What green means, exactly — read the summary line, not the tick.** Green is
+**What green means — read the summary line, not the tick.** Green is
 `changed` (repaired and pushed), `skip-clean` or `skip-not-under-scoped` (no
 repair was owed *to the bot*), or `skip-not-allowed` (it declined to
 classify). It runs the base's `tests/closure.py`: if that stops early
 (a PR moving a file out of INERT) where `closures` printed UNDER-SCOPED, the
 status is `skip-classifier-disagrees`; any other failed check (PHANTOM, NOT A
-FILE, an INERT pair) is `skip-manual-repair-owed`, so `skip-not-under-scoped` means it passed (#1864). `claims-autofix` reddens on nothing it
-can return today — `apply_inherited_claims` has no failure status, and its
-`skip-not-inherited` is the ordinary answer for every unrelated `fast`
-failure — so its summary line is its only signal.
+FILE, an INERT pair) is `skip-manual-repair-owed`, so `skip-not-under-scoped` means it passed (#1864). `claims-autofix` never reddens
+(`apply_inherited_claims` has no failure status; `skip-not-inherited` answers
+every unrelated `fast` failure): its summary line is its only signal.
 
-**Three paths still end green unrepaired.**
+**Four paths still end green unrepaired.**
 
 - **A committed phantom.** `check` fails the `closures` job when the committed
   table lists a path that is not a file (#1310), but the autofix reports no
   UNDER-SCOPED and stays green: a recording cannot drop a dead path. Repair the
   table: `python3 tests/closure.py prune`.
-- **The loop guard.** After the bot pushes, the next run's head subject is
-  `ci: re-record closures`, so `autofix_allowed` returns false *before* any
-  classification runs: if that run is still UNDER-SCOPED the status is
-  `skip-not-allowed` and no second commit comes.
+- **The loop guard.** After the bot pushes, the next head's subject is
+  `ci: re-record closures`, so `autofix_allowed` refuses *before* classifying:
+  a still UNDER-SCOPED run reads `skip-not-allowed`, and no second commit comes.
 - **A truncated recording masking the under-scope.** `check` never inspects a
   recording's `rc`, and a script that exits early records only what it
   reached — so where that truncation hides the *only* under-approximation,
   `check` passes and the job is green on `skip-clean` — or on `changed`, since
   an unnamed script's cut-short recording is left out (R9-CI-1). `skip-failed-recording`
-  fires only *after* UNDER-SCOPED is printed, deliberately: unrelated
+  fires only *after* UNDER-SCOPED prints, deliberately: unrelated
   `no-copies` and NOT-A-FILE failures fail recordings too, and their closures
   were never stale.
 
   A failed recording reads files a clean run never does (`linecache`): an
   UNDER-SCOPED beside one may be an artefact. Fix the script; a push re-records.
+- **A survivor.** `mutation-autofix` pins kills only, so a site no driver kills
+  leaves it green, `tests / mutation` red for good (#2840). `pinned by
+  mutation-autofix` is a prediction until a `mutation-pins` log or `--pin-killed`
+  kills the site; a `-- lives` line is the seat's.
 
 | Failure | Job | Commit subject | Code |
 |---|---|---|---|
@@ -67,18 +69,18 @@ failure — so its summary line is its only signal.
 | `INHERITED CLAIMS` | `claims-autofix` | `ci: drop inherited claims` | `env_drift.apply_inherited_claims` |
 | unpinned sites | `mutation-autofix` | `ci: pin killed mutants` | `mutation_table.apply_pins` |
 
-Those subjects are loop guards. The job dispatches `ci.yml -f pr -f base` once, not four workflows;
-a `GITHUB_TOKEN` push's `pull_request` runs are held `action_required`, so the one required check `gate` and the `tests / *` units are ABSENT at a bot head
-until a run is approved: all three approve them (kept until M-3), fail-soft while their secrets are
-absent, when an App push or body edit cures it. Absent is not green (`orchestrator.md` section 11).
+Those subjects are loop guards. The job dispatches `ci.yml -f pr -f base` once;
+a `GITHUB_TOKEN` push's `pull_request` runs are held `action_required`, so the required `gate` and the `tests / *` units are ABSENT at a bot head
+until approved: all three jobs approve them (kept until M-3), fail-soft without their
+secrets, when an App push or body edit cures it. Absent is not green (`orchestrator.md` section 11).
 
-When `mutation-autofix` goes red, run `--pin-killed` yourself. After `ci: pin killed mutants`
-the reviewer re-checks the body's `## Red checks` `mutation` line, which a pin stales. Do not automate survivor triage,
+When `mutation-autofix` goes red, run `--pin-killed` yourself. A `ci: pin killed mutants`
+stales the body's `## Red checks` `mutation` line; the reviewer re-checks it. Do not automate survivor triage,
 golden drift, structure budgets, `no-copies`, orphan → `INERT`, or briefs lint. A new selectable script with **no** recording is
 not UNDER-SCOPED — add it to a derive lane or `--single` it; autofix cannot invent a trace.
 
 ## A driver-file conflict: one bot merges it, none autofixes it
 
-CI never runs on a `DIRTY` pull request, so no job is red to key on. Do not replace a driver
+CI never runs on a `DIRTY` pull request: no job is red to key on. Do not replace a driver
 with `merge=union`. Only `.github/workflows/merge-main.yml` pushes a resolution (tvofi,
 2026-10-08): `ci: merge main`, where `main`'s drivers resolve every conflicting file.
diff --git a/dev/audit/rca/R10-RCA-MUTATION-SURVIVOR.md b/dev/audit/rca/R10-RCA-MUTATION-SURVIVOR.md
new file mode 100644
index 000000000..0e12861ed
--- /dev/null
+++ b/dev/audit/rca/R10-RCA-MUTATION-SURVIVOR.md
@@ -0,0 +1,228 @@
+# R10-RCA-MUTATION-SURVIVOR: a survivor is green on the one job a seat is told to watch (#2840)
+
+The root-cause record for the recurring-friction key `mutation-survivor`
+(#2840), run apart from any fix (`dev/governance/roles/root-cause.md`). It
+reads `R10-RCA-FRICTION-RESIDUE.md` first and re-derives none of it: #2410's
+family subtraction, #2660's `mutation-vacuous` residue and section 7's
+`ci-autofix` gaps are that record's, and are cited below only where this cause
+reaches them.
+
+**Merge base and window.** Merge base `88c6ad5bbec69bfe157e04597a74d0c9c3e4775c`,
+which was `origin/main` when measured (2026-10-29, UTC). Window `v7.0.4..88c6ad5bb`;
+`v7.0.4` is dated 2026-10-22T13:48:08Z.
+
+## 1. The count, re-derived
+
+`node tools/policy/policy_lint.mjs --stats --since v7.0.4`, rc=0, 10 m 22 s
+(`mutation-survivor/stats_v7.0.4.txt`):
+
+    STATS: 285 merged pull request(s) in v7.0.4..origin/main
+         4 / 6     mutation-survivor   <- at or over threshold
+
+The issue's snapshot was 3 / 5; one PR (#2912, 2026-10-28) has entered the key
+since. The four PRs and their six entries were enumerated by a second reader,
+`mutation-survivor/mutblocks.py` (every `Fix review: blocked <sha> <word>:`
+comment on the window's 285 merged PRs whose word is a mutation-family member,
+with the `mutation_table.py` site keys — `<file>.py:<line> <KIND>` — that its
+Block section cites; output `mutblocks.tsv`, 0 `FETCH-FAILED` rows). Its
+`mutation-survivor` rows reproduce the histogram's 4 PRs / 6 entries — #2579
+(3 rounds, plus a second-bullet block in its round 1), #2817, #2820, #2912 —
+so the two readers agree.
+
+## 2. The brief's premise holds for two of the four
+
+The brief's subject is "survivors that `tests/mutation_table.py --pin-killed`
+would have reported before handoff". `--pin-killed` drives only the candidate
+sites `mutation_table.py` inventories, which are `custom_components/` code
+(`fixer.md` step 2: "its lane mutates `custom_components/` only; a `tools/`
+site needs an in-tree mutant harness"). Split by what the Block cites:
+
+| PR | entries | surviving mutant | in `--pin-killed`'s reach |
+|---|---|---|---|
+| #2579 | 3 | `tools/audit/seat/review_strength.py`: hand mutants against its own self-test (a 600-line cut, a slice, a regex's inner `-`, a nonce slice) | **no** — `tools/` |
+| #2820 | 1 | `tools/policy/friction_issues.mjs`: first-write-wins on a shared census key | **no** — `tools/`, JavaScript |
+| #2817 | 1 | `coordinator.py:6303 GUARD_OFF`, `coordinator.py:6331 GUARD_OFF` | yes |
+| #2912 | 1 | `config_flow.py:3490 RETURN_DEL` (equivalent) | yes |
+
+**#2579 and #2820 are not this subject.** Each is a reviewer's hand mutant on an
+instrument's self-test, outside any generated class: #2579's round 5 records
+that the fixer's own class sweep of 2333 mutants did not contain the surviving
+edit. No mechanical detector in the tree reaches them, and the cheapest one
+that did is the adversarial review that found them — `defect-root-cause.md`'s
+"does not qualify" case. Recorded, nothing built (section 6).
+
+**#2817 and #2912 share one cause, and it is not in `tests/mutation_table.py`.**
+`--pin-killed` reports both correctly; the defect is in what tells a seat it
+has to run it.
+
+## 3. Named cause
+
+Both bodies disposed every added `custom_components/` site as "pinned by
+`mutation-autofix`" — #2817 all 25, #2912 24 — and in both a site no driver
+kills was among them. `mutation-autofix` cannot pin a survivor, and **every path
+a survivor takes through it is green**:
+
+- `measurement()` (`tests/mutation_table.py`) returns `measured` when any site
+  was killed and `skip-nothing-killed` when none was; the survivors' count,
+  which the base program prints in `PIN KILLED: N pinned, M left unpinned`, is
+  parsed for N and discarded for M.
+- `apply_pins()` returns `changed` once any kill is written, whatever is left.
+- `closure.AUTOFIX_QUIET["mutation-autofix"]` holds `changed`,
+  `skip-not-allowed`, `skip-not-unpinned`, `skip-nothing-killed` and
+  `skip-head-moved`: the job is red only when a measurement failed.
+
+So a survivor leaves `tests / mutation` red indefinitely and `mutation-autofix`
+green. `ci-autofix.md`, as it stood at the merge base, told the seat to **wait**
+on `tests / mutation` refusing unpinned sites, that the wait "holds only while
+the job reports it is repairing", and to run `--pin-killed` "when
+`mutation-autofix` goes red". The one trigger the rule names cannot fire for a
+survivor; the wait has no end for one. The fact is printed — the
+`tests / mutation-pins` log marks each one `-- lives` — but nothing a seat is
+told to read says so.
+
+Timelines (check runs, `mutation-survivor/pinsbefore.sh`):
+
+- **#2817.** CI measured head `4fbe4c6a5`: `tests / mutation-pins (1..6)`
+  concluded by 16:39:51Z — the reviewer quotes them listing
+  `6278 GUARD_OFF -- lives` and `6306 GUARD_OFF -- lives`
+  (`ev/ci_mutation_pins_4fbe4c6a5.txt`; the job logs answer 403 to this seat) —
+  and `mutation-autofix` concluded **success** at
+  16:41:11Z. The reviewed head `3b437b851` and its body ("all 25 pinned by
+  mutation-autofix") came at 17:02Z, after the measurement that refuted it.
+- **#2912.** The prior verdict merged `cc0510ee` on the condition that
+  `tests / mutation` turn green; the bot's `ci: pin killed mutants` head
+  `4fc6a4c51` pinned 23 of 24, `tests / mutation` stayed red on the 24th, and the
+  reviewer blocked it at 18:54:48Z.
+- **#2832** (same cause, filed under `mutation-vacuous`): 8 of 25 added
+  `legionella.py` sites `-- lives` in the head's own `mutation-pins` shards,
+  `mutation-autofix` **success**, body "every one of the 25 pinned by
+  `mutation-autofix`"; blocked 6 minutes after the shards concluded.
+
+## 4. Process state: (c)
+
+The process existed and was obeyed. `fixer.md` step 2 lists "pinned by
+`mutation-autofix`" as a disposition; `prepr.sh` step 7d (`unpinned_line`)
+checks only that each listed key has a line; `ci-autofix.md` keyed the seat's
+own action on `mutation-autofix` going red. Each seat did what the text said,
+and the result the text exists for — no survivor reaching review — did not
+follow, because the signal the text keys on is quiet by construction for the
+case it must catch. It is not (b): no seat skipped a step; the "firmer
+instruction" a (b) reading suggests would have told the #2817 fixer to watch a
+job that was green. It is not (d): `AUTOFIX_QUIET`'s mutation tuple has held this form since
+`dc66cc878` (2026-09-24), before the window, and nothing under it changed.
+
+## 5. How far the class reaches
+
+Rule: `mutblocks.py` over the window's 285 merged PRs, every mutation-family
+block whose Block cites a `mutation_table.py` site key. Five PRs:
+
+| PR | word | disposition |
+|---|---|---|
+| #2817 | `mutation-survivor` | this cause (body: all pinned by `mutation-autofix`) |
+| #2912 | `mutation-survivor` | this cause (24 left to `mutation-autofix`, one equivalent survivor) |
+| #2832 | `mutation-vacuous` | this cause (8 of 25 live; body: all pinned) — and it is the one post-`662a380` entry `R10-RCA-FRICTION-RESIDUE` section 6 left as #2660's "residue 1" |
+| #2632 | `mutation-unpinned` | sibling, recorded by `R10-RCA-FRICTION-RESIDUE` section 7: a killable site whose CI pin run timed out, so no bot pin came |
+| — | (not a verdict) | #2834, `R10-RCA-FRICTION-RESIDUE` section 7: ten sites written "pinned by `mutation-autofix`" undriven, two survivors, refused by CI |
+
+Null control on the enumerator: the same regex finds no site key in #2579's or
+#2820's blocks (`sites=0`), whose survivors are `tools/` code — so the rule
+separates the two populations rather than matching every block. Before the
+window, #2379 (2026-10-18, `mutation-untriaged`: "3 added sites survive every
+driver after mutation-autofix") is the same shape under a third word.
+
+**The cause spans four class words** (`mutation-survivor`, `mutation-vacuous`,
+`mutation-unpinned`, `mutation-untriaged`) and one friction rule id
+(`ci-autofix`), which is why no key held it: #2840 filed two of its instances
+beside two that are not.
+
+## 6. Cost test
+
+    cost(countermeasure, recurring) < cost(defect) x P(recurrence)
+
+**P(recurrence).** Of the window's 285 merged PRs, 28 change
+`custom_components/*.py` (`git diff --quiet` over each first-parent merge's
+three-dot diff; the same loop over `nonexistent/*.py` counts 0). Four of the 28 —
+#2817, #2832, #2912, #2834 — carried a survivor left to `mutation-autofix`
+past handoff: **4 / 28 = 14 %** of the PRs that can produce one. #2379 shows it
+in the previous window too.
+
+**cost(defect).** Block to the PR's next verdict: #2817 91 min, #2912 161 min,
+#2832 496 min (overnight); median 161 min, plus one adversarial review round
+each. #2834's owner names its own cost: a CI round and a fixer round.
+
+**Candidates.**
+
+- **A. Run `--pin-killed` before every handoff that adds a site.** Measured at
+  #2817's reviewed head against its base `f54f40cc1`, `--jobs 4` on a
+  4-core container: stopped at the seat's 30-minute limit with **0 of 29**
+  mutants decided — the null control and the baselines alone took 284 s
+  (`env_drift.py`), 463 s (`features.py`) and 505 s (`entities.py`)
+  (`mutation-survivor/pin2817.txt`). CI's measurement of the same diff at
+  `4fbe4c6a5` took six `mutation-pins` shards 30.9 to 77.9 min each,
+  **366 runner-minutes**, 78 min wall clock (check-run start and completion
+  times). Even the local lower bound, 30 min × 28 PRs = 840 min a window,
+  exceeds the whole defect, 4 × 161 min = 644 min, before it is weighted by
+  anything. **Refused**: it costs more than it prevents, and repeats a
+  measurement the CI shards already make on every push.
+- **B. Correct the rule (landed here).** Zero seconds per run. The policy
+  corpus does not grow: `ci-autofix.md` stays at its token cap (1469 / 1469),
+  paid by wording trims that move no claim.
+- **C. Make the survivor loud (carried).** `mutation-autofix` reddens when its
+  measurement leaves an added site alive, naming the site in its summary line.
+  Zero seconds per run: the same job, reading a number it already parses.
+  Owned by `R10-FLY-LEDGER-SAMPLE`, the group holding `tests/mutation_table.py`
+  and #2840's own measure-first carry.
+
+## 7. Countermeasure
+
+**B, landed.** `dev/governance/rules/ci-autofix.md` (generated copies by
+`node tools/policy/rules_sync.mjs`) gains a fourth "path that ends green
+unrepaired":
+
+> **A survivor.** `mutation-autofix` pins kills only, so a site no driver kills
+> leaves it green, `tests / mutation` red for good (#2840). `pinned by
+> mutation-autofix` is a prediction until a `mutation-pins` log or
+> `--pin-killed` kills the site; a `-- lives` line is the seat's.
+
+It addresses state (c) at its unit: the rule's description of what the bot
+signals was false for this case, and is now true. It would have changed #2817,
+whose reviewed head and body came 22 minutes after the shards printed `-- lives`, and
+#2832, whose body's claim was refutable from the head's own shards. Policy
+change under the orchestrator's mandate, scope `all` (the brief).
+
+**C, carried** to `R10-FLY-LEDGER-SAMPLE`, with its acceptance: replayed on
+#2817's `4fbe4c6a5` measurement (`PIN KILLED: 24 pinned, 2 left unpinned`
+shape), the job is red and its summary names `coordinator.py:6278 GUARD_OFF`
+and `6306 GUARD_OFF`; on a measurement with `0 left unpinned` it is green
+(`changed`); a `skip-head-moved` measurement stays quiet. That carry also
+answers the group's #2840 item: the survivors share a cause, and it is the
+autofix's status vocabulary, not `--pin-killed`. Survivor *triage* stays manual
+(`ci-autofix.md`): C reports, it does not dispose.
+
+**Refused, with the reason recorded:**
+
+- A (section 6).
+- A check that a body's "pinned by `mutation-autofix`" row is backed by a
+  measurement, in `prepr.sh` step 7d: at a first handoff no measurement exists
+  (a handoff ref runs no job), so the arm could only refuse the prediction the
+  rule now names as one, or demand A.
+- A mechanical detector for #2579's and #2820's shape: no generated class reached
+  either surviving edit (#2579 round 5's 2333-mutant sweep), so the cheapest
+  detector is the review that ran.
+
+## 8. Carries
+
+- `Carry: R10-FLY-LEDGER-SAMPLE` — countermeasure C and its acceptance, and the
+  answer to that group's #2840 carry (section 7).
+
+## Evidence
+
+`dev/audit/rca/mutation-survivor/`:
+
+- `stats_v7.0.4.txt` — the `policy_lint --stats --since v7.0.4` run at
+  `88c6ad5bb`.
+- `mutblocks.py`, `mutblocks.tsv` — the window's mutation-family blocks with
+  their cited site keys (section 5's enumerator).
+- `pinsbefore.sh` — per-commit `mutation-pins` completion and `mutation-autofix`
+  conclusion for a PR (section 3's timelines).
+- `pin2817.txt` — `--pin-killed` at #2817's reviewed head (section 6, A).
diff --git a/dev/audit/rca/mutation-survivor/mutblocks.py b/dev/audit/rca/mutation-survivor/mutblocks.py
new file mode 100644
index 000000000..91e74bb27
--- /dev/null
+++ b/dev/audit/rca/mutation-survivor/mutblocks.py
@@ -0,0 +1,24 @@
+import json, re, subprocess, sys
+# Rule: every "Fix review: blocked <sha> <word>:" issue comment on a PR merged in the window
+# whose class word is one of the mutation family's members (policy_lint FRICTION_FAMILIES 'mutation'
+# plus the untaught mutation-unpinned / unpinned-site / mutation-untriaged), with the
+# mutation_table site keys its Block section cites (empty = no site key: a tools/ or hand mutant).
+FAM = {"mutation","mutation-vacuous","mutation-survivor","test-vacuous","vacuous-test","vacuous-check",
+       "mutant-survives","mutation-unpinned","unpinned-site","mutation-untriaged"}
+KINDS = "GUARD_OFF|RETURN_DEL|CMP_BOUND|CLAMP_DROP|RAISE_DEL|BOOLOP|CONST"
+SITE = re.compile(r"([\w/.-]+\.py):(\d+)\s+(%s)" % KINDS)
+HEAD = re.compile(r"^Fix review: blocked [0-9a-f]{40} ([a-z][a-z0-9-]*)")
+R = "repos/tvofi/heatpump_optimizer"
+for n in open(sys.argv[1]).read().split():
+    out = subprocess.run(["gh","api","--paginate","--slurp",f"{R}/issues/{n}/comments"],capture_output=True,text=True)
+    if out.returncode: print(f"#{n}\tFETCH-FAILED", flush=True); continue
+    for c in [c for p in json.loads(out.stdout) for c in p]:
+        b = c.get("body") or ""
+        m = HEAD.match(b)
+        if not m: continue
+        words = {m.group(1)} | set(re.findall(r";\s*([a-z][a-z0-9-]*):", b.splitlines()[0]))
+        if not words & FAM: continue
+        blk = b.split("## Findings")[0]
+        sites = sorted({f"{p.split('/')[-1]}:{l} {k}" for p,l,k in SITE.findall(blk)})
+        auto = "pinned by mutation-autofix" in blk or "pinned by `mutation-autofix`" in blk
+        print(f"#{n}\t{c['created_at']}\t{','.join(sorted(words & FAM))}\tsites={len(sites)}\tautofix-claim={auto}\t{' ; '.join(sites)[:200]}", flush=True)
diff --git a/dev/audit/rca/mutation-survivor/mutblocks.tsv b/dev/audit/rca/mutation-survivor/mutblocks.tsv
new file mode 100644
index 000000000..6d8331a9a
--- /dev/null
+++ b/dev/audit/rca/mutation-survivor/mutblocks.tsv
@@ -0,0 +1,24 @@
+#2919	2026-10-28T21:25:49Z	mutation-vacuous	sites=0	autofix-claim=False	
+#2916	2026-10-28T23:21:38Z	mutation-vacuous	sites=0	autofix-claim=False	
+#2937	2026-10-28T22:06:09Z	mutation-vacuous	sites=0	autofix-claim=False	
+#2912	2026-10-28T18:54:48Z	mutation-survivor	sites=1	autofix-claim=False	config_flow.py:3490 RETURN_DEL
+#2920	2026-10-28T18:11:49Z	mutation-vacuous	sites=0	autofix-claim=False	
+#2873	2026-10-28T02:56:03Z	mutation-vacuous	sites=0	autofix-claim=False	
+#2832	2026-10-25T21:55:35Z	mutation-vacuous	sites=2	autofix-claim=True	legionella.py:345 CMP_BOUND ; legionella.py:655 BOOLOP
+#2817	2026-10-25T18:24:13Z	mutation-survivor	sites=4	autofix-claim=True	coordinator.py:6278 GUARD_OFF ; coordinator.py:6303 GUARD_OFF ; coordinator.py:6306 GUARD_OFF ; coordinator.py:6331 GUARD_OFF
+#2697	2026-10-24T11:07:35Z	mutation-vacuous	sites=0	autofix-claim=False	
+#2697	2026-10-24T16:05:10Z	mutation-vacuous	sites=0	autofix-claim=False	
+#2820	2026-10-25T17:18:20Z	mutation-survivor	sites=0	autofix-claim=False	
+#2712	2026-10-24T23:48:23Z	mutation-vacuous	sites=0	autofix-claim=False	
+#2709	2026-10-24T14:01:08Z	mutation-vacuous	sites=0	autofix-claim=False	
+#2632	2026-10-23T06:11:42Z	mutation-unpinned	sites=2	autofix-claim=False	coordinator.py:9553 RETURN_DEL ; coordinator.py:9568 RETURN_DEL
+#2645	2026-10-23T03:55:48Z	mutation-vacuous	sites=0	autofix-claim=False	
+#2647	2026-10-23T05:44:33Z	mutation-vacuous	sites=0	autofix-claim=False	
+#2629	2026-10-22T23:52:27Z	unpinned-site	sites=0	autofix-claim=False	
+#2528	2026-10-21T14:36:00Z	vacuous-test	sites=0	autofix-claim=False	
+#2528	2026-10-21T20:43:20Z	vacuous-test	sites=0	autofix-claim=False	
+#2580	2026-10-21T17:11:40Z	mutation-vacuous	sites=0	autofix-claim=False	
+#2579	2026-10-21T22:23:02Z	mutation-survivor	sites=0	autofix-claim=False	
+#2579	2026-10-22T10:17:03Z	mutation-survivor	sites=0	autofix-claim=False	
+#2579	2026-10-22T13:08:40Z	mutation-survivor	sites=0	autofix-claim=False	
+#2605	2026-10-22T10:30:57Z	mutation-vacuous	sites=0	autofix-claim=False	
diff --git a/dev/audit/rca/mutation-survivor/pin2817.txt b/dev/audit/rca/mutation-survivor/pin2817.txt
new file mode 100644
index 000000000..bd8406308
--- /dev/null
+++ b/dev/audit/rca/mutation-survivor/pin2817.txt
@@ -0,0 +1,36 @@
+  3972 unpinned site(s) of 6360 candidate sites, 3957 at the ratchet base f54f40cc1157529fea147456ad67e26c24d67aca; the ledger agrees with the deterministic inventory
+MUTATION TABLE -- scope changed: 5 production file(s) whose code this diff adds or modifies
+PIN KILLED -- 29 new unpinned site(s) against f54f40cc1157529fea147456ad67e26c24d67aca to drive
+  29 mutant(s) over 5 file(s); drivers in play: tests/arch_score_head.py, tests/backtest.py, tests/block_duty.py, tests/boost_drift_replay.py, tests/config_flow_steps.py, tests/debug_collect.py, tests/deployment_shape.py, tests/doc_claims.py, tests/edge.py, tests/entities.py, tests/env_drift.py, tests/features.py, tests/finite_boundary.py, tests/guard_pins.py, tests/harness_headers.py, tests/manual_plan.py, tests/optimality.py, tests/plan_view.py, tests/solar_alignment.py, tests/stress.py, tests/structure.py, tests/typing_ruler.py, tests/validate.py, tests/wood_advisor.py
+  ref-driven drivers compare against 'f54f40cc1157529fea147456ad67e26c24d67aca' (run.sh's GOLDEN_REF resolution)
+  null control: custom_components/heatpump_optimizer/coordinator.py:517 NULL_COMMENT, a comment-only edit every driver in play must let survive
+  tests/harness_headers.py: baseline and null control deferred until a mutant survives every shared driver
+  tests/stress.py: baseline and null control deferred until a mutant survives every shared driver
+  tests/arch_score_head.py: baseline and null control deferred until a mutant run of it is red
+  tests/backtest.py: baseline and null control deferred until a mutant run of it is red
+  tests/block_duty.py: baseline and null control deferred until a mutant run of it is red
+  tests/boost_drift_replay.py: baseline and null control deferred until a mutant run of it is red
+  tests/config_flow_steps.py: baseline and null control deferred until a mutant run of it is red
+  tests/debug_collect.py: baseline and null control deferred until a mutant run of it is red
+  tests/deployment_shape.py: baseline and null control deferred until a mutant run of it is red
+  tests/doc_claims.py: baseline and null control deferred until a mutant run of it is red
+  tests/edge.py: baseline and null control deferred until a mutant run of it is red
+  tests/entities.py: baseline and null control deferred until a mutant run of it is red
+  tests/features.py: baseline and null control deferred until a mutant run of it is red
+  tests/finite_boundary.py: baseline and null control deferred until a mutant run of it is red
+  tests/guard_pins.py: baseline and null control deferred until a mutant run of it is red
+  tests/manual_plan.py: baseline and null control deferred until a mutant run of it is red
+  tests/optimality.py: baseline and null control deferred until a mutant run of it is red
+  tests/plan_view.py: baseline and null control deferred until a mutant run of it is red
+  tests/solar_alignment.py: baseline and null control deferred until a mutant run of it is red
+  tests/structure.py: baseline and null control deferred until a mutant run of it is red
+  tests/typing_ruler.py: baseline and null control deferred until a mutant run of it is red
+  tests/validate.py: baseline and null control deferred until a mutant run of it is red
+  tests/wood_advisor.py: baseline and null control deferred until a mutant run of it is red
+  baseline tests/env_drift.py: rc=0 failed=0 284s
+  null control custom_components/heatpump_optimizer/coordinator.py:517 NULL_COMMENT survived every driver
+  baseline tests/features.py: rc=0 failed=0 463s
+  baseline tests/entities.py: rc=0 failed=0 505s
+  null control custom_components/heatpump_optimizer/coordinator.py:517 NULL_COMMENT survived tests/features.py
+  null control custom_components/heatpump_optimizer/coordinator.py:517 NULL_COMMENT survived tests/entities.py
+# stopped by the seat's 30-minute background limit at 15:31Z (started 14:59Z); no PIN KILLED summary line was reached
diff --git a/dev/audit/rca/mutation-survivor/pinsbefore.sh b/dev/audit/rca/mutation-survivor/pinsbefore.sh
new file mode 100644
index 000000000..fa3ed76ce
--- /dev/null
+++ b/dev/audit/rca/mutation-survivor/pinsbefore.sh
@@ -0,0 +1,12 @@
+# For each PR: every PR commit with a concluded `tests / mutation-pins*` run, its latest completion,
+# so a measurement that existed before the blocked head was pushed can be read off.
+R=repos/tvofi/heatpump_optimizer
+for n in "$@"; do
+  echo "=== #$n"
+  for sha in $(gh api --paginate "$R/pulls/$n/commits?per_page=100" --jq '.[].sha'); do
+    d=$(gh api "$R/commits/$sha" --jq '.commit.committer.date')
+    p=$(gh api "$R/commits/$sha/check-runs?per_page=100" --jq '[.check_runs[]|select(.name|startswith("tests / mutation-pins"))|select(.completed_at)|.completed_at]|max // "-"')
+    a=$(gh api "$R/commits/$sha/check-runs?per_page=100" --jq '[.check_runs[]|select(.name=="tests / mutation-autofix")|.conclusion]|join(",")')
+    echo "${sha:0:9} pushed $d pins-concluded $p autofix $a"
+  done
+done
diff --git a/dev/audit/rca/mutation-survivor/stats_v7.0.4.txt b/dev/audit/rca/mutation-survivor/stats_v7.0.4.txt
new file mode 100644
index 000000000..46bdd58fc
--- /dev/null
+++ b/dev/audit/rca/mutation-survivor/stats_v7.0.4.txt
@@ -0,0 +1,277 @@
+GAP: 0 merge(s) recovered from the commit's own "Merge pull request #N" subject after /commits/<sha>/pulls answered []
+WINDOW_CACHE: off -- no --window-cache, so this mode fetched the window itself
+STATS: 285 merged pull request(s) in v7.0.4..origin/main; verdict grammar ["blocked","merge"] over block classes ["mutation-vacuous","harness","null-control","claims","version","head-moved","carry-missing","root-cause-unanswered","preflight-mismatch","class-open","conflict","other","product-tradeoff-regression","metric-gamed","architecture-unsound","root-cause-detectable","root-cause-unrecorded"] read from .claude/workflows/web-fix-wave.js
+STATS COVERAGE: 235 of 285 merged pull request(s) in the window carried a parsable verdict; 50 carried none (#2943 #2941 #2940 #2911 #2893 #2868 #2863 #2847 #2845 #2795 +40 more); the histogram's verdict denominator is 235, not the window's merge count
+STATS COVERAGE BY CLASS: merged pull request(s) carrying no parsable verdict, of each class's window, by the title's type -- record 49 of 62 (#2943 #2941 #2940 #2911 #2893 #2868 #2863 #2847 #2845 #2795 +39 more); build 1 of 3 (#2774); (untyped) 0 of 119; ci 0 of 2; coordinator 0 of 1; depgraph 0 of 1; fix 0 of 15; flow 0 of 1; fly 0 of 1; inputs 0 of 1; plan 0 of 1; policy 0 of 2; rca 0 of 6; roles 0 of 1; roster 0 of 29; train 0 of 1; triage 0 of 39
+STATS ENDPOINTS: parsable verdict(s) by the endpoint they arrived on -- /issues/<n>/comments (issue comment): 495; /pulls/<n>/reviews (review): 0. Both endpoints are read, so a verdict posted as a review is counted rather than read as a merge that carried none.
+STATS ROUNDS: over the 235 merged pull request(s) carrying a parsable verdict, first-verdict yield 124/235 = 0.528 (the first verdict was `merge`), one-round yield 98/235 = 0.417 (merged on that one verdict, no later parsable one). Of the 260 parsable verdict(s) after a pull request's first, by the verdict before each: 37 re-verified a head that moved after a `merge` (23 PR(s), the "head-moved (rework)" row), 176 repaired after a `blocked`, 47 repeated the previous verdict's head. A `Fix review:` line outside the grammar is in none of these; each is reported below.
+verdict class (PRs / entries):
+   235 / 319   merge   <- at or over threshold
+    32 / 38    carry-missing   <- at or over threshold
+    13 / 14    mutation-vacuous   <- at or over threshold
+    11 / 18    class-open   <- at or over threshold
+     6 / 6     root-cause-detectable   <- at or over threshold
+     5 / 9     claim-false   <- at or over threshold
+     4 / 6     mutation-survivor   <- at or over threshold
+     4 / 4     harness   <- at or over threshold
+     3 / 4     merge-conflict   <- at or over threshold
+     3 / 3     head-moved   <- at or over threshold
+     3 / 3     regression   <- at or over threshold
+     2 / 4     ruling-unsound
+     2 / 3     other
+     2 / 2     ci-unconcluded
+     2 / 2     figure-wrong
+     2 / 2     body-stale
+     2 / 2     ci-red
+     2 / 2     root-cause-unanswered
+     2 / 2     verdict-word
+     2 / 2     ruling-refuted
+     2 / 2     body-head-stale
+     1 / 2     budget-exceeded
+     1 / 2     claim
+     1 / 2     claim-drift
+     1 / 2     vacuous-test
+     1 / 1     conflict
+     1 / 1     countermeasure-silenced
+     1 / 1     null-control
+     1 / 1     predicate-over-fire
+     1 / 1     delivery-row-stale
+     1 / 1     ruling
+     1 / 1     prior
+     1 / 1     metric-gamed
+     1 / 1     harness-nondeterministic
+     1 / 1     nondeterministic-arm
+     1 / 1     duplicate-ruling
+     1 / 1     root-cause-unrecorded
+     1 / 1     ratchet-unrecorded
+     1 / 1     body-figure
+     1 / 1     ruling-incomplete
+     1 / 1     ruling-change
+     1 / 1     released-early
+     1 / 1     claims
+     1 / 1     pr-contract-refused
+     1 / 1     pin-wrong
+     1 / 1     structure-breach
+     1 / 1     carry-dest-done
+     1 / 1     ruling-misrouted
+     1 / 1     figures-unverified
+     1 / 1     contract-incomplete
+     1 / 1     body-claim-wrong
+     1 / 1     carry-undisposed
+     1 / 1     figure-false
+     1 / 1     brief-lint
+     1 / 1     figure-uncited
+     1 / 1     host-path
+     1 / 1     policy-loosened
+     1 / 1     dangling-owner
+     1 / 1     record-contradicts-diff
+     1 / 1     figure-unverified
+     1 / 1     mutation-unpinned
+     1 / 1     retry-rule-unsound
+     1 / 1     unpinned-site
+     1 / 1     claim-refuted
+     1 / 1     defect
+     1 / 2     mutation (family) (of 18; mutation-vacuous, mutation-survivor file their own)
+CENSUS	verdict class	235	319	merge
+CENSUS	verdict class	32	38	carry-missing
+CENSUS	verdict class	13	14	mutation-vacuous
+CENSUS	verdict class	11	18	class-open
+CENSUS	verdict class	6	6	root-cause-detectable
+CENSUS	verdict class	5	9	claim-false
+CENSUS	verdict class	4	6	mutation-survivor
+CENSUS	verdict class	4	4	harness
+CENSUS	verdict class	3	4	merge-conflict
+CENSUS	verdict class	3	3	head-moved
+CENSUS	verdict class	3	3	regression
+CENSUS	verdict class	2	4	ruling-unsound
+CENSUS	verdict class	2	3	other
+CENSUS	verdict class	2	2	ci-unconcluded
+CENSUS	verdict class	2	2	figure-wrong
+CENSUS	verdict class	2	2	body-stale
+CENSUS	verdict class	2	2	ci-red
+CENSUS	verdict class	2	2	root-cause-unanswered
+CENSUS	verdict class	2	2	verdict-word
+CENSUS	verdict class	2	2	ruling-refuted
+CENSUS	verdict class	2	2	body-head-stale
+CENSUS	verdict class	1	2	budget-exceeded
+CENSUS	verdict class	1	2	claim
+CENSUS	verdict class	1	2	claim-drift
+CENSUS	verdict class	1	2	vacuous-test
+CENSUS	verdict class	1	1	conflict
+CENSUS	verdict class	1	1	countermeasure-silenced
+CENSUS	verdict class	1	1	null-control
+CENSUS	verdict class	1	1	predicate-over-fire
+CENSUS	verdict class	1	1	delivery-row-stale
+CENSUS	verdict class	1	1	ruling
+CENSUS	verdict class	1	1	prior
+CENSUS	verdict class	1	1	metric-gamed
+CENSUS	verdict class	1	1	harness-nondeterministic
+CENSUS	verdict class	1	1	nondeterministic-arm
+CENSUS	verdict class	1	1	duplicate-ruling
+CENSUS	verdict class	1	1	root-cause-unrecorded
+CENSUS	verdict class	1	1	ratchet-unrecorded
+CENSUS	verdict class	1	1	body-figure
+CENSUS	verdict class	1	1	ruling-incomplete
+CENSUS	verdict class	1	1	ruling-change
+CENSUS	verdict class	1	1	released-early
+CENSUS	verdict class	1	1	claims
+CENSUS	verdict class	1	1	pr-contract-refused
+CENSUS	verdict class	1	1	pin-wrong
+CENSUS	verdict class	1	1	structure-breach
+CENSUS	verdict class	1	1	carry-dest-done
+CENSUS	verdict class	1	1	ruling-misrouted
+CENSUS	verdict class	1	1	figures-unverified
+CENSUS	verdict class	1	1	contract-incomplete
+CENSUS	verdict class	1	1	body-claim-wrong
+CENSUS	verdict class	1	1	carry-undisposed
+CENSUS	verdict class	1	1	figure-false
+CENSUS	verdict class	1	1	brief-lint
+CENSUS	verdict class	1	1	figure-uncited
+CENSUS	verdict class	1	1	host-path
+CENSUS	verdict class	1	1	policy-loosened
+CENSUS	verdict class	1	1	dangling-owner
+CENSUS	verdict class	1	1	record-contradicts-diff
+CENSUS	verdict class	1	1	figure-unverified
+CENSUS	verdict class	1	1	mutation-unpinned
+CENSUS	verdict class	1	1	retry-rule-unsound
+CENSUS	verdict class	1	1	unpinned-site
+CENSUS	verdict class	1	1	claim-refuted
+CENSUS	verdict class	1	1	defect
+CENSUS	verdict family	1	2	mutation (family)
+rework (PRs / entries):
+    23 / 37    head-moved (rework)   <- at or over threshold
+CENSUS	rework	23	37	head-moved (rework)
+friction rule id (PRs / entries):
+    10 / 11    .claude/rules/gate-scoping.md   <- at or over threshold
+     8 / 11    tools/audit/briefs/fixer.md   <- at or over threshold
+     7 / 7     .claude/rules/finding-propagation.md   <- at or over threshold
+     4 / 4     .claude/rules/ci-autofix.md   <- at or over threshold
+     3 / 4     .claude/rules/brief-citations.md   <- at or over threshold
+     2 / 3     brief
+     2 / 2     policy_lint.mjs
+     2 / 2     environment
+     2 / 2     fixer-env
+     1 / 2     roster
+     1 / 1     .claude/rules/delivery-status-tracking.md
+     1 / 1     rounds.py
+     1 / 1     brief_lint
+     1 / 1     gitignore-global-config
+     1 / 1     main-red-invisible
+     1 / 1     cloud-fixer-prompt
+     1 / 1     handoff-instrument
+     1 / 1     tools/audit/seat/ref_privacy.py
+     1 / 1     roster-brief
+     1 / 1     features-block-header-only
+     1 / 1     prepr
+     1 / 1     round-3-instrument-rewrite
+     1 / 1     entity-heartbeat-load
+     1 / 1     roster-vocabulary
+     1 / 1     roster-stage-derivation
+     1 / 1     stage-flag-stored
+     1 / 1     seat-brief-hold
+     1 / 1     roster-moves-under-a-count
+     1 / 1     policy-cap
+     1 / 1     duplicate-proposal
+     1 / 1     out-of-tree-wiring
+     1 / 1     tests/run.sh
+     1 / 1     carries-omitted
+     1 / 1     tests/entities.py
+     1 / 1     .claude/workflows/agreement.mjs
+     1 / 1     gate-sweep-step-under-bash-env
+     1 / 1     proxy-write
+     1 / 1     R10-PIN-DRIVE-INCONCLUSIVE
+     1 / 1     harness
+     1 / 1     fixer-instrument
+     1 / 1     cloud_dispatch
+     1 / 1     brief-diagnosis
+     1 / 1     tools/audit/harnesses/r10_relay_owed_class_reach.py
+     1 / 1     tools/audit/briefs/orchestrator.md
+     1 / 1     r10_seat_selftests_mutants
+     1 / 1     .claude/rules/ratchet-budgets.md
+     1 / 1     tools/audit/prepr.sh
+     1 / 1     tools/audit/seat/seat_venv.sh
+     1 / 1     fixer
+     1 / 1     fixer-handoff
+     1 / 1     dispatch
+     1 / 1     .claude/rules/defect-root-cause.md
+     1 / 1     .claude/rules/writing-for-agents.md
+     1 / 1     fixes-vs-disposition
+     1 / 1     cloud-seat-toolchain
+     2 / 2     environment (family)
+CENSUS	friction rule id	10	11	.claude/rules/gate-scoping.md
+CENSUS	friction rule id	8	11	tools/audit/briefs/fixer.md
+CENSUS	friction rule id	7	7	.claude/rules/finding-propagation.md
+CENSUS	friction rule id	4	4	.claude/rules/ci-autofix.md
+CENSUS	friction rule id	3	4	.claude/rules/brief-citations.md
+CENSUS	friction rule id	2	3	brief
+CENSUS	friction rule id	2	2	policy_lint.mjs
+CENSUS	friction rule id	2	2	environment
+CENSUS	friction rule id	2	2	fixer-env
+CENSUS	friction rule id	1	2	roster
+CENSUS	friction rule id	1	1	.claude/rules/delivery-status-tracking.md
+CENSUS	friction rule id	1	1	rounds.py
+CENSUS	friction rule id	1	1	brief_lint
+CENSUS	friction rule id	1	1	gitignore-global-config
+CENSUS	friction rule id	1	1	main-red-invisible
+CENSUS	friction rule id	1	1	cloud-fixer-prompt
+CENSUS	friction rule id	1	1	handoff-instrument
+CENSUS	friction rule id	1	1	tools/audit/seat/ref_privacy.py
+CENSUS	friction rule id	1	1	roster-brief
+CENSUS	friction rule id	1	1	features-block-header-only
+CENSUS	friction rule id	1	1	prepr
+CENSUS	friction rule id	1	1	round-3-instrument-rewrite
+CENSUS	friction rule id	1	1	entity-heartbeat-load
+CENSUS	friction rule id	1	1	roster-vocabulary
+CENSUS	friction rule id	1	1	roster-stage-derivation
+CENSUS	friction rule id	1	1	stage-flag-stored
+CENSUS	friction rule id	1	1	seat-brief-hold
+CENSUS	friction rule id	1	1	roster-moves-under-a-count
+CENSUS	friction rule id	1	1	policy-cap
+CENSUS	friction rule id	1	1	duplicate-proposal
+CENSUS	friction rule id	1	1	out-of-tree-wiring
+CENSUS	friction rule id	1	1	tests/run.sh
+CENSUS	friction rule id	1	1	carries-omitted
+CENSUS	friction rule id	1	1	tests/entities.py
+CENSUS	friction rule id	1	1	.claude/workflows/agreement.mjs
+CENSUS	friction rule id	1	1	gate-sweep-step-under-bash-env
+CENSUS	friction rule id	1	1	proxy-write
+CENSUS	friction rule id	1	1	R10-PIN-DRIVE-INCONCLUSIVE
+CENSUS	friction rule id	1	1	harness
+CENSUS	friction rule id	1	1	fixer-instrument
+CENSUS	friction rule id	1	1	cloud_dispatch
+CENSUS	friction rule id	1	1	brief-diagnosis
+CENSUS	friction rule id	1	1	tools/audit/harnesses/r10_relay_owed_class_reach.py
+CENSUS	friction rule id	1	1	tools/audit/briefs/orchestrator.md
+CENSUS	friction rule id	1	1	r10_seat_selftests_mutants
+CENSUS	friction rule id	1	1	.claude/rules/ratchet-budgets.md
+CENSUS	friction rule id	1	1	tools/audit/prepr.sh
+CENSUS	friction rule id	1	1	tools/audit/seat/seat_venv.sh
+CENSUS	friction rule id	1	1	fixer
+CENSUS	friction rule id	1	1	fixer-handoff
+CENSUS	friction rule id	1	1	dispatch
+CENSUS	friction rule id	1	1	.claude/rules/defect-root-cause.md
+CENSUS	friction rule id	1	1	.claude/rules/writing-for-agents.md
+CENSUS	friction rule id	1	1	fixes-vs-disposition
+CENSUS	friction rule id	1	1	cloud-seat-toolchain
+CENSUS	friction family	2	2	environment (family)
+CENSUS: 123 key(s)
+threshold: 3 or more of one key in the window opens "[policy] recurring friction: <key>". Nothing is opened here.
+(window)
+  INFO    [stats] (window): not opened: verdict class "merge" at 235 pull request(s) is the passing verdict .claude/workflows/web-fix-wave.js requires before a merge, so this row counts rework nowhere -- a merge verdict re-verifying a head that moved after a `merge` is counted on the "head-moved (rework)" row, and a repair after a block is on the STATS ROUNDS line. Friction is rework.
+  INFO    [stats] (window): would open "[policy] recurring friction: carry-missing" -- verdict class at 32 in this window, threshold 3. Counted as DISTINCT pull requests (38 entries in all); recurrence is across occasions, not within one body. Not opened here: a seat measures and files, a report does not.
+  INFO    [stats] (window): would open "[policy] recurring friction: mutation-vacuous" -- verdict class at 13 in this window, threshold 3. Counted as DISTINCT pull requests (14 entries in all); recurrence is across occasions, not within one body. Not opened here: a seat measures and files, a report does not.
+  INFO    [stats] (window): would open "[policy] recurring friction: class-open" -- verdict class at 11 in this window, threshold 3. Counted as DISTINCT pull requests (18 entries in all); recurrence is across occasions, not within one body. Not opened here: a seat measures and files, a report does not.
+  INFO    [stats] (window): would open "[policy] recurring friction: root-cause-detectable" -- verdict class at 6 in this window, threshold 3. Counted as DISTINCT pull requests (6 entries in all); recurrence is across occasions, not within one body. Not opened here: a seat measures and files, a report does not.
+  INFO    [stats] (window): would open "[policy] recurring friction: claim-false" -- verdict class at 5 in this window, threshold 3. Counted as DISTINCT pull requests (9 entries in all); recurrence is across occasions, not within one body. Not opened here: a seat measures and files, a report does not.
+  INFO    [stats] (window): would open "[policy] recurring friction: harness" -- verdict class at 4 in this window, threshold 3. Counted as DISTINCT pull requests (4 entries in all); recurrence is across occasions, not within one body. Not opened here: a seat measures and files, a report does not.
+  INFO    [stats] (window): would open "[policy] recurring friction: mutation-survivor" -- verdict class at 4 in this window, threshold 3. Counted as DISTINCT pull requests (6 entries in all); recurrence is across occasions, not within one body. Not opened here: a seat measures and files, a report does not.
+  INFO    [stats] (window): would open "[policy] recurring friction: merge-conflict" -- verdict class at 3 in this window, threshold 3. Counted as DISTINCT pull requests (4 entries in all); recurrence is across occasions, not within one body. Not opened here: a seat measures and files, a report does not.
+  INFO    [stats] (window): would open "[policy] recurring friction: head-moved" -- verdict class at 3 in this window, threshold 3. Counted as DISTINCT pull requests (3 entries in all); recurrence is across occasions, not within one body. Not opened here: a seat measures and files, a report does not.
+  INFO    [stats] (window): would open "[policy] recurring friction: regression" -- verdict class at 3 in this window, threshold 3. Counted as DISTINCT pull requests (3 entries in all); recurrence is across occasions, not within one body. Not opened here: a seat measures and files, a report does not.
+  INFO    [stats] (window): would open "[policy] recurring friction: head-moved (rework)" -- rework at 23 in this window, threshold 3. Counted as DISTINCT pull requests (37 entries in all); recurrence is across occasions, not within one body. Not opened here: a seat measures and files, a report does not.
+  INFO    [stats] (window): would open "[policy] recurring friction: .claude/rules/gate-scoping.md" -- friction rule id at 10 in this window, threshold 3. Counted as DISTINCT pull requests (11 entries in all); recurrence is across occasions, not within one body. Not opened here: a seat measures and files, a report does not.
+  INFO    [stats] (window): would open "[policy] recurring friction: tools/audit/briefs/fixer.md" -- friction rule id at 8 in this window, threshold 3. Counted as DISTINCT pull requests (11 entries in all); recurrence is across occasions, not within one body. Not opened here: a seat measures and files, a report does not.
+  INFO    [stats] (window): would open "[policy] recurring friction: .claude/rules/finding-propagation.md" -- friction rule id at 7 in this window, threshold 3. Counted as DISTINCT pull requests (7 entries in all); recurrence is across occasions, not within one body. Not opened here: a seat measures and files, a report does not.
+  INFO    [stats] (window): would open "[policy] recurring friction: .claude/rules/ci-autofix.md" -- friction rule id at 4 in this window, threshold 3. Counted as DISTINCT pull requests (4 entries in all); recurrence is across occasions, not within one body. Not opened here: a seat measures and files, a report does not.
+  INFO    [stats] (window): would open "[policy] recurring friction: .claude/rules/brief-citations.md" -- friction rule id at 3 in this window, threshold 3. Counted as DISTINCT pull requests (4 entries in all); recurrence is across occasions, not within one body. Not opened here: a seat measures and files, a report does not.
+WOULD OPEN: 16 issue(s)
diff --git a/dev/governance/rules/ci-autofix.md b/dev/governance/rules/ci-autofix.md
index 5185aea27..7fa72f3a2 100644
--- a/dev/governance/rules/ci-autofix.md
+++ b/dev/governance/rules/ci-autofix.md
@@ -13,58 +13,60 @@ paths:
 Same-repo PRs run three jobs (`.github/workflows/tests.yml`). **Before the PR exists
 nothing waits**: a handoff ref runs no job, so a red `prepr.sh` step 6d predicts is repaired
 before handoff (`--single`; for INERT READS `python3 tools/pr/ci_predict.py --apply-inert`,
-which writes the Linux recording's entry, not a `--single`). Once it exists, if `tests / closures` is
+which writes the Linux recording's entry). Once it exists, if `tests / closures` is
 `UNDER-SCOPED`, `tests / fast` fails `INHERITED CLAIMS` or `tests / mutation` refuses unpinned sites, **wait** --
-a `DIRTY` head queues no run, so no bot commit comes. Do not open a parallel PR, do not
-Darwin `--single` an under-scope CI already recorded, and do not hand-empty claim files
-that match `origin/main`. Darwin can `--single` a **new** node script, or grow a node
-closure; it cannot replace a Linux node recording.
+a `DIRTY` head queues no run, so no bot commit comes. Do not open a parallel PR,
+Darwin `--single` an under-scope CI already recorded, or hand-empty claim files
+that match `origin/main`. Darwin can `--single` a **new** node script or grow a node
+closure, never replace a Linux node recording.
 
 **That wait holds only while the job reports it is
 repairing.** Each job pushes on `changed` alone and prints its status to the
 job summary (#523). `closures-autofix` goes red on `skip-failed-recording`,
 `skip-merge-failed`, `skip-still-fails`, `skip-unchanged`,
 `skip-classifier-disagrees` and `skip-manual-repair-owed` — a repair was owed
-and it did not happen. **A red autofix job means no bot commit comes.** The
-`--single` prohibition above, which assumes the bot will merge, lapses. Read the summary
+and did not happen. **A red autofix job means no bot commit comes**; the
+`--single` prohibition above lapses. Read the summary
 line, re-derive the script it names and commit `tests/closures.json`; Python
 lanes record through `sys.addaudithook`, so Darwin is sound for them — except
-the inert dimension, which is Linux-recorded (`strace`-only): the bot merges
+the Linux-recorded (`strace`-only) inert dimension: the bot merges
 INERT READS from CI recordings too (#1886, R9-CI-1). On `skip-failed-recording` a
-script the check named (or its driven child) stopped while being recorded — fix it first; re-deriving would record the same truncation.
+named script (or its driven child) stopped while recorded: fix it first, as re-deriving records the same truncation.
 
-**What green means, exactly — read the summary line, not the tick.** Green is
+**What green means — read the summary line, not the tick.** Green is
 `changed` (repaired and pushed), `skip-clean` or `skip-not-under-scoped` (no
 repair was owed *to the bot*), or `skip-not-allowed` (it declined to
 classify). It runs the base's `tests/closure.py`: if that stops early
 (a PR moving a file out of INERT) where `closures` printed UNDER-SCOPED, the
 status is `skip-classifier-disagrees`; any other failed check (PHANTOM, NOT A
-FILE, an INERT pair) is `skip-manual-repair-owed`, so `skip-not-under-scoped` means it passed (#1864). `claims-autofix` reddens on nothing it
-can return today — `apply_inherited_claims` has no failure status, and its
-`skip-not-inherited` is the ordinary answer for every unrelated `fast`
-failure — so its summary line is its only signal.
+FILE, an INERT pair) is `skip-manual-repair-owed`, so `skip-not-under-scoped` means it passed (#1864). `claims-autofix` never reddens
+(`apply_inherited_claims` has no failure status; `skip-not-inherited` answers
+every unrelated `fast` failure): its summary line is its only signal.
 
-**Three paths still end green unrepaired.**
+**Four paths still end green unrepaired.**
 
 - **A committed phantom.** `check` fails the `closures` job when the committed
   table lists a path that is not a file (#1310), but the autofix reports no
   UNDER-SCOPED and stays green: a recording cannot drop a dead path. Repair the
   table: `python3 tests/closure.py prune`.
-- **The loop guard.** After the bot pushes, the next run's head subject is
-  `ci: re-record closures`, so `autofix_allowed` returns false *before* any
-  classification runs: if that run is still UNDER-SCOPED the status is
-  `skip-not-allowed` and no second commit comes.
+- **The loop guard.** After the bot pushes, the next head's subject is
+  `ci: re-record closures`, so `autofix_allowed` refuses *before* classifying:
+  a still UNDER-SCOPED run reads `skip-not-allowed`, and no second commit comes.
 - **A truncated recording masking the under-scope.** `check` never inspects a
   recording's `rc`, and a script that exits early records only what it
   reached — so where that truncation hides the *only* under-approximation,
   `check` passes and the job is green on `skip-clean` — or on `changed`, since
   an unnamed script's cut-short recording is left out (R9-CI-1). `skip-failed-recording`
-  fires only *after* UNDER-SCOPED is printed, deliberately: unrelated
+  fires only *after* UNDER-SCOPED prints, deliberately: unrelated
   `no-copies` and NOT-A-FILE failures fail recordings too, and their closures
   were never stale.
 
   A failed recording reads files a clean run never does (`linecache`): an
   UNDER-SCOPED beside one may be an artefact. Fix the script; a push re-records.
+- **A survivor.** `mutation-autofix` pins kills only, so a site no driver kills
+  leaves it green, `tests / mutation` red for good (#2840). `pinned by
+  mutation-autofix` is a prediction until a `mutation-pins` log or `--pin-killed`
+  kills the site; a `-- lives` line is the seat's.
 
 | Failure | Job | Commit subject | Code |
 |---|---|---|---|
@@ -72,18 +74,18 @@ failure — so its summary line is its only signal.
 | `INHERITED CLAIMS` | `claims-autofix` | `ci: drop inherited claims` | `env_drift.apply_inherited_claims` |
 | unpinned sites | `mutation-autofix` | `ci: pin killed mutants` | `mutation_table.apply_pins` |
 
-Those subjects are loop guards. The job dispatches `ci.yml -f pr -f base` once, not four workflows;
-a `GITHUB_TOKEN` push's `pull_request` runs are held `action_required`, so the one required check `gate` and the `tests / *` units are ABSENT at a bot head
-until a run is approved: all three approve them (kept until M-3), fail-soft while their secrets are
-absent, when an App push or body edit cures it. Absent is not green (`orchestrator.md` section 11).
+Those subjects are loop guards. The job dispatches `ci.yml -f pr -f base` once;
+a `GITHUB_TOKEN` push's `pull_request` runs are held `action_required`, so the required `gate` and the `tests / *` units are ABSENT at a bot head
+until approved: all three jobs approve them (kept until M-3), fail-soft without their
+secrets, when an App push or body edit cures it. Absent is not green (`orchestrator.md` section 11).
 
-When `mutation-autofix` goes red, run `--pin-killed` yourself. After `ci: pin killed mutants`
-the reviewer re-checks the body's `## Red checks` `mutation` line, which a pin stales. Do not automate survivor triage,
+When `mutation-autofix` goes red, run `--pin-killed` yourself. A `ci: pin killed mutants`
+stales the body's `## Red checks` `mutation` line; the reviewer re-checks it. Do not automate survivor triage,
 golden drift, structure budgets, `no-copies`, orphan → `INERT`, or briefs lint. A new selectable script with **no** recording is
 not UNDER-SCOPED — add it to a derive lane or `--single` it; autofix cannot invent a trace.
 
 ## A driver-file conflict: one bot merges it, none autofixes it
 
-CI never runs on a `DIRTY` pull request, so no job is red to key on. Do not replace a driver
+CI never runs on a `DIRTY` pull request: no job is red to key on. Do not replace a driver
 with `merge=union`. Only `.github/workflows/merge-main.yml` pushes a resolution (tvofi,
 2026-10-08): `ci: merge main`, where `main`'s drivers resolve every conflicting file.
diff --git a/dev/programme/delivery/2961.md b/dev/programme/delivery/2961.md
new file mode 100644
index 000000000..2f7842cc3
--- /dev/null
+++ b/dev/programme/delivery/2961.md
@@ -0,0 +1 @@
+- [#2961](https://github.com/tvofi/heatpump_optimizer/pull/2961) — **open**, rca(R10-FRICTION-MUTATION-SURVIVOR): a survivor is green on the job a seat watches; ci-autofix.md names it (#2840) (R10-FRICTION-MUTATION-SURVIVOR)

