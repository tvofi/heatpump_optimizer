# Review packet #2898
head: 44281492277f962676e72abb09b2202f872d9273
base: 07295d4ea1471048ee2a76a6776b5cd364dcf141

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: pending
CodeQL id=122572298949 success
arch-score / arch-score id=122571641149 success
arm id=122566185201 skipped
budget-raise-gate / budget-raise-gate id=122571641426 success
cancel-superseded id=122566191476 success
codeql / Analyze (actions) id=122571641473 success
codeql / Analyze (javascript-typescript) id=122571641469 success
codeql / Analyze (python) id=122571641448 success
governance / delivery-status id=122571641472 success
governance / delivery-status-publish id=122571642597 skipped
governance / env-matrix id=122571641526 success
governance / instrument-self-tests id=122571641511 success
governance / policy-docs id=122571641528 success
governance / record id=122571642612 skipped
governance / wave-script id=122571641500 success
hassfest / hassfest id=122571641273 success
kernel-points id=122571642522 skipped
prelude id=122566191703 success
refresh id=122566191321 success
tests / arch-instrument id=122572290578 success
tests / briefs id=122571641392 success
tests / browser id=122572290734 success
tests / claims-autofix id=122574524950 skipped
tests / closure-scope id=122571641494 success
tests / closures id=122572290528 success
tests / closures-autofix id=122574307847 skipped
tests / coverage id=122572290637 in_progress
tests / fast (3.14) id=122572290640 success
tests / mutation id=122571641446 success
tests / mutation-autofix id=122572305915 skipped
tests / mutation-pins id=122572304629 skipped
tests / nightly-ha id=122572292603 skipped
tests / nightly-status id=122571641410 success
tests / replay id=122572292607 skipped
tests / typing id=122572290724 success
validate / validate-hacs id=122571641276 success

## Refusals
none

## Advisories
none

## carry_audit at the head
CARRY-AUDIT: 0 finding item(s): 0 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
unverified git log --format=%cI --diff-filter=A -- dev/programme/triage/s6-batch3<n>.md
             `git log` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  ok         tools/audit/seat/merge_train.py
             `tools/audit/seat/merge_train.py` is in the tree at this head
  unverified git diff 4db1d3e28^1 4db1d3e28 -- tools/audit/seat/merge_train.py | grep -c seen
             `git diff` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  ok         tools/audit/worktree_gc.sh
             `tools/audit/worktree_gc.sh` is in the tree at this head
  unverified git worktree list | wc -l
             `git worktree` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  ok         tools/audit/seat/cloud_dispatch.py
             `tools/audit/seat/cloud_dispatch.py` is in the tree at this head
  unverified git ls-files | grep -c orch_sweep
             `git ls-files` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  unverified git grep -n "isolated git worktree\|base repo checkout"
             `git grep` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals

FIGURES: 3 resolved, 5 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
none

## Three-dot diff
diff --git a/dev/programme/delivery/2898.md b/dev/programme/delivery/2898.md
new file mode 100644
index 000000000..5122dfe6d
--- /dev/null
+++ b/dev/programme/delivery/2898.md
@@ -0,0 +1 @@
+- [#2898](https://github.com/tvofi/heatpump_optimizer/pull/2898) — **open**, triage: batch 44 -- rule V132-V135 and V137-V140 as P219-P226 (R10-FLY-WORKTREE-GC)
diff --git a/dev/programme/triage/s6-batch36.md b/dev/programme/triage/s6-batch36.md
index 3613a2edb..1bb7b6877 100644
--- a/dev/programme/triage/s6-batch36.md
+++ b/dev/programme/triage/s6-batch36.md
@@ -5,7 +5,7 @@ writer on the triage role is a live hazard on the stamp path: the orchestrator h
 barrier that admits exactly one batch file newer than the `v7.0.5` tag. Numbering continues
 after `s6-batch35.md` (P199-P203). Facts read at origin/main `524c1896b` on 2026-10-27.
 
-## P204: two seats on one role are invisible and unstoppable (V124)
+## P204: two seats on one role are invisible and unstoppable (orchestrator relay; no `proposals.md` id)
 Verdict: DEFER. Route the item as prose into the carry text of **R10-ORCH-BEATD**
 (`not-started`, L; the sweep/beat is its surface). P197 is deferred to that group and sits
 in its carry 13 (index 12), the context-rotation paragraph, per `s6-batch34.md`; the roster
diff --git a/dev/programme/triage/s6-batch37.md b/dev/programme/triage/s6-batch37.md
index 9a9089178..b253aa00c 100644
--- a/dev/programme/triage/s6-batch37.md
+++ b/dev/programme/triage/s6-batch37.md
@@ -3,7 +3,7 @@
 One entry. Numbering continues after `s6-batch36.md` (P204). Facts re-measured on
 2026-10-27 at origin/main `2b45d098c` and against the live refs and logs named below.
 
-## P205: a STOP result body reads as an orphan handoff on every pass (V125)
+## P205: a STOP result body reads as an orphan handoff on every pass (orchestrator relay; no `proposals.md` id)
 Verdict: DEFER. The item's group is `R10-ORCH-LEDGER` (`carries-open`, L). What would
 change the answer: two or more live STOP result bodies that `dispose` does not heal, or
 a body whose owed text is machine-checkable.
diff --git a/dev/programme/triage/s6-batch38.md b/dev/programme/triage/s6-batch38.md
index c75de0a85..57ce7784a 100644
--- a/dev/programme/triage/s6-batch38.md
+++ b/dev/programme/triage/s6-batch38.md
@@ -2,7 +2,7 @@
 
 One entry. Facts read at origin/main `524c1896b` on 2026-10-27.
 
-## P206: one seat's measurements hold the whole push lane for half an hour (V126)
+## P206: one seat's measurements hold the whole push lane for half an hour (orchestrator relay; no `proposals.md` id)
 Verdict: ACCEPT narrowed -> a carry of **R10-PREPR-CAP** (it owns `tools/pr/prepr.sh` and
 `tests/gate_lock.py`, `stage` `done` -- the roster command under "Roster" below). The proposal asked for a cost/benefit
 ruling on three arms; measured against the tree, the holder-side bound it names in arm 1 is
diff --git a/dev/programme/triage/s6-batch39.md b/dev/programme/triage/s6-batch39.md
index 2ddf87911..a1ed12728 100644
--- a/dev/programme/triage/s6-batch39.md
+++ b/dev/programme/triage/s6-batch39.md
@@ -4,7 +4,7 @@ Four proposals, relayed by the orchestrator on 2026-10-27 in its funding order (
 P209, P210). None is yet in `proposals.md`, whose newest entry is V123. Facts read at
 origin/main `67178dc6a`; this seat's own samples at 17:10Z and 53 s later.
 
-## P207: a verdict publishes before anything checks its findings name a destination (V127)
+## P207: a verdict publishes before anything checks its findings name a destination (orchestrator relay; no `proposals.md` id)
 
 Verdict: ACCEPT -> a carry of **R10-FLY-CARRY-DISPOSITION** (`resume.stage` `not-started`;
 the only group whose `files` name both files the change touches,
@@ -47,7 +47,7 @@ roster (queue_pre_flight:192's own short-circuit, `finding_rows(...)[0]` empty);
 must name the count and the first item, so the reviewer reads in the refusal what the train
 would otherwise have said.
 
-## P208: the body's `## Head` is checked last, after the expensive steps (V128)
+## P208: the body's `## Head` is checked last, after the expensive steps (orchestrator relay; no `proposals.md` id)
 
 Verdict: ACCEPT -> a carry of **R10-RCA-BODY-LINT** (the group that owns `tools/pr/prepr.sh`,
 `tools/audit/seat/body_push.sh` and `tools/policy/policy_lint.mjs`; `resume.stage` `done`, so the
@@ -85,7 +85,7 @@ the early refusal must print the same line the late one does; the check must run
 1b's slot is taken, or the expensive part it exists to avoid is still spent; and the null
 control is a matching body running every step exactly as today.
 
-## P209: the claim driver refuses a merge it can safely union (V129)
+## P209: the claim driver refuses a merge it can safely union (orchestrator relay; no `proposals.md` id)
 
 Verdict: ACCEPT -> a carry of **R10-996-RUNNER-CLAIMS** (`resume.stage` `carries-open`;
 `files` `tests/env_drift.py` and `tests/golden/claimed_drift.txt`).
@@ -126,7 +126,7 @@ deterministic and preserve the stamp, header and `may-drift` lines the existing
 (`tests/entities.py:22423-22445`); the retained refusal keeps the reason that still applies;
 and the policy sentence moves in the same pull request, never after it.
 
-## P210: the field-coverage step has no bound, so a blocked run reads as a long one (V130)
+## P210: the field-coverage step has no bound, so a blocked run reads as a long one (orchestrator relay; no `proposals.md` id)
 
 Verdict: DEFER -> what would change the answer is one healthy run to completion (wall and CPU)
 plus what the zero-CPU instances wait on. The item is `tools/pr/prepr.sh`, `R10-PREPR-CAP`'s
diff --git a/dev/programme/triage/s6-batch40.md b/dev/programme/triage/s6-batch40.md
index 3a303899a..51fa3ce09 100644
--- a/dev/programme/triage/s6-batch40.md
+++ b/dev/programme/triage/s6-batch40.md
@@ -12,10 +12,10 @@ this box, and it is not re-derived here; the claim that #2854's body lacks the f
 
 Correction (this seat, after the first cut merged): the first cut rejected the proposal's second
 arm whole. That was wrong about its lease half, and the entry below is corrected. The first cut
-reached `main` as PR #2886 at `ee5816b1`; this follow-up replaces it, and the ledger keeps the
+reached `main` as PR #2886 (merge `a0e7664ea`); this follow-up replaces it, and the ledger keeps the
 order in which the seat changed its mind.
 
-## P211: the push-stuck guard's threshold sits below the work it is guarding (V131)
+## P211: the push-stuck guard's threshold sits below the work it is guarding (V124)
 
 Verdict: ACCEPT narrowed, in two carries. The proposal's first arm (sample the push's
 process-tree CPU advance instead of elapsed time alone) is the one carried into
diff --git a/dev/programme/triage/s6-batch44.md b/dev/programme/triage/s6-batch44.md
new file mode 100644
index 000000000..ce341e985
--- /dev/null
+++ b/dev/programme/triage/s6-batch44.md
@@ -0,0 +1,249 @@
+# Proposal triage, session s7, batch 44 (P219-P226)
+
+Eight entries: V132-V135, written by the orchestrator s7 on 2026-10-27, and V137-V140, written by
+the orchestrator s8 on 2026-10-28, quoted from `proposals.md` as they stand. `proposals.md` leaves
+V136 unassigned ("#2891 cites it; the triage seat resolves that reference"): no proposal is V136,
+and #2891's P216 heading is corrected to V129, its `Source:` id, on its own branch. Facts read at origin/main `e8cb7e683` (v7.0.5); roster at
+`origin/handoff/audit-r10-roster` `de410e4c9` (212 groups). From this batch on, a heading carries no
+proposal id: the contract's form is `## P<n>: <title>`, and the `Source:` line is the one place an
+id is written (P219).
+
+The same pull request corrects the headings P219 measures in the merged batches 36-40: P204-P210
+read `(orchestrator relay; no proposals.md id)` instead of `(V124)`-`(V130)`, and P211 reads
+`(V124)`, its `Source:` id, instead of `(V131)`. Each entry's `Verdict:` reads the same through
+`roster_edit.ruling_verdict` before and after (P204 DEFER, P205 DEFER, P206 ACCEPT, P207-P209
+ACCEPT, P210 DEFER, P211 ACCEPT), so no roster carry citing them moves. The residual the batch-40
+review left is applied: `s6-batch40.md` now says the first cut "reached `main` as PR #2886 (merge
+`a0e7664ea`)"; `ee5816b1` was the file's blob.
+
+## P219: triage headings cite a V-number seven above their source
+
+Verdict: REJECT -- the instrument (a pre-commit step that resolves a heading's V-number against
+`proposals.md`). The defect it targets is real and is removed here at no tooling cost: headings
+carry no id (above), and batches 41-43 are corrected on their own branches.
+
+Source: `proposals.md` V132 (orchestrator s7, 2026-10-27T21:00Z).
+
+Instances: five batch files, one cause.
+- `grep -n '^## P\|^Source:' dev/programme/triage/s6-batch3[6-9].md dev/programme/triage/s6-batch40.md`
+  at `e8cb7e683`: P204-P210 headings read `(V124)`-`(V130)`, and their `Source:` lines name the
+  orchestrator's relays, not `proposals.md` ("V124 assigned to this seat in the orchestrator's
+  09:37Z relay", `s6-batch36.md:18`; "not yet in `proposals.md`", `s6-batch39.md:13`, `:56`, `:93`,
+  `:135`). P211's heading reads `(V131)` beside `Source: proposals.md V124` (`s6-batch40.md`).
+- Batches 41-43 (PRs #2890, #2891, #2892): headings `(V132)`-`(V138)` beside `Source:` V125-V131.
+- `proposals.md`'s own `## V124` to `## V131` are stamped 18:53Z to 21:00Z, after the relays
+  batches 36-39 ruled: `git log --format=%cI --diff-filter=A -- dev/programme/triage/s6-batch3<n>.md`
+  gives 09:47:20Z (36), 11:33:59Z (37), 12:41:42Z (38) and 17:18:24Z (39).
+- Cost already paid: #2891's round-1 review blocked on V136 and #2890's round-2 review blocked on
+  V132-V135 (hpo-approver, 2026-10-27T20:56:12Z and 21:05:00Z), plus one repair seat for the three
+  branches.
+
+Cause: not a counter that started seven ahead. Two writers allocated one id space. The relays
+behind P204-P210 were seven proposals given ids V124-V130 outside `proposals.md`; the orchestrator
+later wrote different proposals into `proposals.md` as V124 onward. The seat kept the relay
+numbering, so every later heading ran exactly seven ahead -- the offset equals the number of
+relayed rulings.
+
+Cost: the candidate's check has one input, `proposals.md`, which lives in the orchestrator's state
+directory and not in the tree. A pre-commit hook or CI step cannot read it on a runner, and naming
+its path in the tree is a host path `ref_privacy.py` refuses. Moving the file into the tree is a
+larger change than the defect (a new tracked, classified file rewritten on every relay).
+
+Binding: the check's only input is out of the tree, and the defect needs no check once the
+heading carries no id. The rule the owner already wrote holds it: `proposal-triage.md`'s entry is
+`## P<n>: <title>`. The second writer is dispatch practice, not tooling: a relayed proposal is
+ruled with `Source: orchestrator relay` and no V-number until `proposals.md` holds it (sent to the
+orchestrator, not carried).
+
+## P220: a fresh verdict is discarded for the life of a train, because a skipped entry counts as queued
+
+Verdict: DEFER -- owned by **R10-TRAIN-OVERLAP-GRADE**: its carries 9 (P129,
+`s6-batch26.md#P129`), 13 (P189, `s6-batch32.md#P189`) and 15 (the #2846 review applying P189)
+already rule exactly this: one admission predicate for `add` and the drain, a PR this train skipped
+and re-added at a new verdict head admitted into the next batch, and the same log word on both
+sides. The group's `resume.stage` reads `done` with those carries unimplemented, so the route is a
+reopen (the P196 route), queued for the roster seat. The filing's `REPLACED` line and its
+replacement of a still-queued entry at a new head are not carried: P129's controls already fix the
+words, and no instance of a queued (not skipped) entry at a moved head is recorded.
+
+Source: `proposals.md` V133 (orchestrator s7, 2026-10-27T22:45Z).
+
+Instances: three over two trains, two already counted.
+- s7 merge train: `grep -n "in this train already" train.log` in the train's state directory
+  (857 lines) returns one line, `ALREADY #2876: in this train already; not queued twice`; the merge seat's
+  ledger entry at 21:40Z records the re-add at verdict head `9513b571` (comment `6452648096`).
+- s40, 2026-10-25: #2745 and #2753, both counted by P129.
+- At `e8cb7e683`, `batch` still seeds `seen` with every PR the train held
+  (`tools/audit/seat/merge_train.py:2516`) and `queue_take` drops any PR in it (`:2567-2569`); the
+  group's PR #2882 merged at `4db1d3e28` and
+  `git diff 4db1d3e28^1 4db1d3e28 -- tools/audit/seat/merge_train.py | grep -c seen` is 0.
+
+Cost: nothing new. P129's estimate (S, one predicate and self-test arms) and P189's (XS) stand.
+
+Binding: the item is already ruled and carried twice; ruling it a third time adds a carry the
+group would have to reconcile against two others. What is missing is not a ruling but a stage:
+a `done` group with three unimplemented carries is invisible to dispatch.
+
+## P221: `sweep` cannot merge a record PR, so the stamp's flush has no backstop as documented
+
+Verdict: REJECT.
+
+Source: `proposals.md` V134 (orchestrator s7, 2026-10-27T23:25Z, heading clock corrected in V135
+to about 22:0xZ).
+
+Instances: one, #2893 (`record/autofix`), the v7.0.5 stamp's flush.
+- `sweep` left it with `LEFT #2893: the record pull request (record/autofix): --bot-prs merges it`
+  (`merge_train.py:2038`). The line already names the flag.
+- The merge seat's ledger, 22:19Z: "sweep_bots' --automerge-check guard exited 0, gh pr merge was
+  refused by main-protect-checks (requires 1 approving review), #2893 had zero reviews"; "The beat
+  approved 22:18:24Z and merged 22:18:33Z, 49 s after the train released the hold."
+- The same ledger, 22:44Z: "a --bot-prs batch refreshes TRAIN HOLD, which suppresses the approver
+  beat, and sweep_bots does not approve."
+- `tools/audit/seat/INSTRUMENTS.md:516-519` names `sweep` the slow backstop for "each head `queue`
+  admits", which excludes the record branch by `merge_train.py:2037-2038`; it does not name `sweep`
+  for a record PR.
+
+Cost: two strings (the `LEFT` line and `sweep`'s help) in `merge_train.py`, 5,831 lines and the
+train's hot file.
+
+Binding: the repair text the candidate would print -- "run a batch with --bot-prs" -- is the move
+that failed in its own instance: a `--bot-prs` batch held the approver beat off the record PR and
+`sweep_bots` cannot approve, so the PR merged only once the train let go. A message that sends the
+next seat to that move is worse than the current one. The mechanism the ledger measured (a
+`--bot-prs` batch suppresses the approval it waits on, and the train drops `gh pr merge`'s refusal
+text, logging `(OPEN null)`) is a defect with its own route, not a proposal; it is sent to the
+orchestrator for that route.
+
+## P222: the worktree edit guard refuses edits on a worktree that does not exist
+
+Verdict: REJECT.
+
+Source: `proposals.md` V135 (orchestrator s7, 2026-10-27T22:18:45Z).
+
+Instances: one, the `RELEASE_NOTES.md` edit during the v7.0.5 stamp, refused by a `PreToolUse` hook
+naming a worktree `git worktree list` did not hold.
+- `git grep -n "isolated git worktree\|base repo checkout"` at `e8cb7e683` matches only
+  `dev/audit/rounds/round7/D3/REPORT.md:4`, which is prose.
+- `.claude/settings.json`'s only `PreToolUse` hook is `.claude/hooks/pre-edit.sh`
+  (Edit/Write/MultiEdit/NotebookEdit), and `grep -c worktree .claude/hooks/pre-edit.sh` is 0.
+
+Cost: no repository cost can be stated, because no repository file produces the refusal.
+
+Binding: no owner in the tree. The guard is the session host's own worktree-isolation check, and
+no roster group can change it; a carry would sit on a group that cannot deliver it. The workaround
+the filing used (a script, verified) is what the tree supports. The report belongs with the
+owner, against the host.
+
+## P223: `worktree_gc.sh` keeps every clean detached worktree whose head is not on main
+
+Verdict: ACCEPT narrowed -> a carry of **R10-FLY-WORKTREE-GC** (`resume.stage` `not-started`, so
+the op is a plain append; its one file is `tools/audit/worktree_gc.sh`, and its brief is the same
+seam from the other side: never collect unpushed work). The new class is `on-remote`, inside class
+B (detached) only; a worktree on a branch keeps today's rules.
+
+Source: `proposals.md` V137 (orchestrator s8, 2026-10-28).
+
+Instances: one rotation, measured by the filer: 130 worktrees, 5.4 GiB free, 72 of them clean,
+process-free and with heads on remote refs (about 10 GiB). Re-read at this seat's start:
+`git worktree list | wc -l` = 65 and `df -h` reports 10 GiB free at 95 % used, after the manual
+pass the filing describes.
+- `tools/audit/worktree_gc.sh` at `e8cb7e683`: class B keeps a clean detached worktree as
+  `unmerged-head` whenever `head_is_merged_ancestor` (388-392, `git merge-base --is-ancestor
+  <head> origin/main`) fails (562-563); `locked` is decided first (529); the script has no
+  process check (`grep -c lsof tools/audit/worktree_gc.sh` = 0).
+
+Cost: one predicate and one class line in a 701-line script, one self-test arm per control, one
+mutant, plus one fetch per run. Per candidate: one `git for-each-ref --contains <head> refs/remotes refs/tags --count=1`
+and one `lsof -a -d cwd` read, only on worktrees already past the clean and age guards.
+
+Binding: the benefit is measured (a disk-exhaustion stall averted and 72 worktrees removed by
+hand), and the narrowing keeps the group's own promise. A head reachable from a remote-tracking
+ref or a tag can be re-created with `git worktree add <head>`, so nothing unpushed is lost. The
+script fetches nothing today (`grep -c fetch tools/audit/worktree_gc.sh` = 0), so the class adds one
+`git fetch --prune origin` per run: a remote-tracking ref whose branch origin deleted then no longer
+vouches, and a run that cannot fetch keeps every such worktree as today. Kept as today: `locked` (a seat's claim), dirty, young, and any worktree some process has
+as its working directory.
+
+Carry text (for `roster_edit.py append-carry R10-FLY-WORKTREE-GC`, citing
+`triage: dev/programme/triage/s6-batch44.md#P223`): "Add an `on-remote` removal class to class B
+(detached) of `tools/audit/worktree_gc.sh` (V137). Today a clean detached worktree is kept as
+`unmerged-head` whenever its head is not an ancestor of origin/main (`head_is_merged_ancestor`,
+388-392; 562-563); one rotation measured 130 worktrees and 5.4 GiB free, 72 of them clean with
+heads on remote refs (about 10 GiB). After the clean check and before `unmerged-head`, remove the
+worktree as `remove  <wt>  on-remote` when its head is reachable from refs/remotes/* or refs/tags/*
+(read after one `git fetch --prune origin` at the start of the run; a failed fetch keeps them all as `unmerged-head`) and no process has a working directory inside it
+(`lsof -a -d cwd`; an unreadable lsof keeps the worktree, naming `cwd-unread`). `locked` (529),
+dirty and young keep first, as today; a worktree on a branch is out of scope. Controls: a clean
+detached worktree at a head only a remote branch holds is removed; null controls: the same at a
+head no remote ref or tag holds is kept `unmerged-head`; the same with a process cwd inside is
+kept; a locked one is kept `locked`; one mutant drops the cwd test and fails its arm."
+
+## P224: the sweep does not check that the cloud environment and pool triggers still resolve
+
+Verdict: REJECT.
+
+Source: `proposals.md` V138 (orchestrator s8, 2026-10-28).
+
+Instances: one. `cloud-overlay.json` named a deleted environment and both pool triggers were gone;
+the first dispatch failed with HTTP 404, then 400 `environment_not_found` (the filing).
+- `orch_sweep.sh` is not in the tree (`git ls-files | grep -c orch_sweep` = 0); the in-tree sweep
+  is `tools/audit/seat/sweep_template.md`, a prompt the orchestrator follows.
+- `tools/audit/seat/cloud_dispatch.py` reads the environment id from the overlay
+  (`:32-36`, `:334-341`); trigger and environment reads are host tools, not shell-callable.
+
+Cost: the check is a host-tool read by the orchestrator on every sweep. V139 measures that a
+trigger read echoes the whole trigger, about 10 KB; two triggers per sweep at the 1800 s default
+(`INSTRUMENTS.md:516`) is about 20 KB of main-loop context per sweep, about 960 KB a day.
+
+Binding: the failure is already loud and exact at the first dispatch (404, then
+`environment_not_found`), which is the one moment the environment matters; a sweep check buys
+only the time between the loss and that dispatch, at a standing token cost on every sweep. A
+rotation that inherits the loss meets it at its own first dispatch with the same message.
+
+## P225: pool routines that read their payload from a dispatch ref, so a dispatch costs fewer tokens
+
+Verdict: DEFER -- the mechanism already exists in the tree; the decision is a measurement. Owner
+of the in-tree half: **R10-FLOW-DISPATCH** (`done`; `tools/audit/seat/cloud_dispatch.py`). Nothing
+is carried.
+
+Source: `proposals.md` V139 (orchestrator s8, 2026-10-28).
+
+Instances: the filer's estimate, ~10 KB per trigger echo and ~30 KB of main-loop tokens per three
+seats; no transcript count is cited.
+- `cloud_dispatch.py:19-23` already publishes every payload with its prompt on
+  `dispatch/<role>-<topic>` (PAYLOAD.json, PROMPT.md) and states that "a standing trigger whose
+  prompt fetches the ref it is fired with needs nothing else"; `:25-29` records the update+run
+  path the filing wants to leave.
+
+Cost: recreating two routines and one prompt is outside the tree. A `run` with no body cannot name
+which ref to read, so the routine has to pick its dispatch by claim, which is the pool path whose
+failures V107 and V114 recorded (a re-pooled topic reading POOL EMPTY; a hand-edited POOL.txt
+emptying the pool).
+
+Binding: the benefit is an estimate, and the cost includes a claim race the tree has already paid
+for twice. Flips to ACCEPT on one measured pair: the orchestrator's context growth for one
+update+run dispatch against one bodiless pool run, both read from the session transcript, and the
+pool claim's refusal on two concurrent runs shown with a null control.
+
+## P226: the resume header does not show the replan's closure date and open counts
+
+Verdict: DEFER -- owned by **R10-ORCH-BEATD** (`not-started`, 35 carries), which P197
+(`s6-batch34.md#P197`) already names as the owner of the orchestrator's generated handover
+(`state_docs.py` plus the resume, with `handover_prompt.py` and `resume_doc.py`, its carry 13).
+
+Source: `proposals.md` V140 (orchestrator s8, 2026-10-28).
+
+Instances: one: a rotation's `RESUME-PROMPT` read as near-complete ("v7.0.5 stamped, window
+closed") while the replanned page shows 66 open roster issues and closure 2026-11-02 (the filing).
+- `tools/audit/seat/handover_prompt.py` (280 lines) already computes the open groups
+  (`roster_lib.open_groups`, `:46`) for its seats' prompt; the orchestrator's `RESUME-PROMPT.md` is
+  hand-kept and, per P197, deliberately static.
+
+Cost: small in the generator, but the instance's prompt is the hand-kept one, which the generator
+does not write; a header in `handover_prompt.py` reaches it only through R10-ORCH-BEATD's
+generated orchestrator handover.
+
+Binding: no cost of the misread is recorded (no wrong dispatch or lost hour), so the benefit is
+unmeasured, and the owning group already carries the generated handover the header would live in.
+Flips on a recorded decision the misread caused, or on R10-ORCH-BEATD's dispatch, where it is one
+line of its brief.

