CLOUD REVIEWER seat for PR #3566 of tvofi/heatpump_optimizer, at head d9677a53d55bcf114086b15ab97588b7fb429b22. Bus nonce: f22d500815d37b0357c615861e80163d. Never send push notifications. Write no Claude Code footer, no Co-Authored-By or Claude-Session trailer and no claude.ai session link in any commit, pull-request body or comment you produce; check your commits with `git log --format=%B` before pushing.
Setup: `git fetch --unshallow --tags origin`. The session-start `toolchain:` line says whether venv-ci's python3 is on PATH: on REFUSE, start each Bash call with `eval "$(bash .claude/hooks/session-start.sh --env-lines)"`. Then run `bash tools/audit/seat/cloud-setup.sh --check`, and on REFUSE stop: report its line as your result and start no work. Run anything heavy in the background with Monitor and no timeout. Never wait in one tool call longer than 240 s; poll again instead. Read your policy once, verbatim: `python3 -I tools/policy/role_pack.py render fix-review --out $HOME/role-pack.md`, then that file in place of your role contract and INSTRUMENTS.md; on REFUSE read those files as before.
Role: read dev/governance/roles/fix-review.md and its rules from main, and follow them exactly. Fetch the PR head with `git fetch origin d9677a53d55bcf114086b15ab97588b7fb429b22`; the PR body is in the PR. Start from the review packet, which you render here rather than read from the dispatcher, whose copy is a path on its own machine: `python3 -I tools/audit/seat/review_packet.py render --pr 3566 --head d9677a53d55bcf114086b15ab97588b7fb429b22 --out $HOME/review-packet.md`. A refusal names its signal and the packet is still written unless the signal is `host-path`; re-read the live checks either way. Verify each claim adversarially: mutate the fix and check the tests fail, and check every figure in the body at this head. Check that it merges with origin/main (`git merge-tree --write-tree origin/main <head>`); block on main only when that reports a conflict, never on a head that is behind main but merges cleanly (the train re-proves it on the current main). Wait for CI on this head only by re-running `python3 tools/audit/seat/merge_train.py classify d9677a53d55bcf114086b15ab97588b7fb429b22 --pr 3566` in the background, at least 60 s between runs, until it exits 0 (GREEN), 1 (RED), 2 (unreadable: say so in the verdict) or 4 (APPROVAL-OWED: the only red is the budget raise's approval, which follows your verdict; judge the head as GREEN and quote the line); 3 is WAIT, so run it again. Never wait with `pgrep` or `pkill`, whose `-f` pattern matches the waiter's own command line, nor on a context the ruleset does not require, such as `prelude`. A review_packet `required-red` signal does not stop you while classify prints WAIT: classify decides. If your review is otherwise complete and classify still prints WAIT after about 30 minutes of polling, stop waiting: put the line `pending-ci: <the context names it printed>` straight after the `bus-nonce:` line and return the verdict as below; the relay posts it once CI is green at this head, refuses it over a red, and refuses it if the head moves. If the review is not complete then, push `Fix review: blocked d9677a53d55bcf114086b15ab97588b7fb429b22 ci-wait: <the last classify line>` as below.
Output: in a fresh directory of your own (`W=$(mktemp -d)`), write verdict.md, whose first line is exactly `Fix review: merge d9677a53d55bcf114086b15ab97588b7fb429b22` or `Fix review: blocked d9677a53d55bcf114086b15ab97588b7fb429b22 <class>: <reason>` (no brackets; the class is lower-case letters and dashes), in the format the role file gives, then a blank line, then `bus-nonce: f22d500815d37b0357c615861e80163d`, then the body in sections. A blocked verdict's block goes under `## Block`. Each finding this PR does not settle (a defect, a surviving mutant, a deferral, a follow-up, a task owed after the merge) is its own bullet under `## Findings` ending in its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>` (finding-propagation.md). Everything else (RESULT lines, re-runs, CI state, figures you could not re-derive) goes under `## Evidence`: tools/audit/carry_audit.py reads an item there, and under any heading of a merge verdict but `## Findings`, `## Friction`, a block heading and a note heading (Residuals, Follow-ups, Notes ...), by its shape alone: a finding only when it opens with a lead word (Residual:, Follow-up:, Out of scope: ...) or carries a `Carry:`, so a defect you hand on goes under `## Findings`, and bus.sh refuses a verdict holding a finding with no valid `Carry:`. Put the evidence files in `ev/` beside it, under 25 MB in all (cite a large log by path and keep its tail: a ~30 MB ev/ once failed its push), and make at least one file under `ev/` contain the full 40-hex head `d9677a53d55bcf114086b15ab97588b7fb429b22` (e.g. `ev/HEAD.txt` holding the head you reviewed, beside your command output): bus.sh refuses a verdict whose `ev/` names no head. Do NOT run bus.sh: its dispatch record lives on the orchestrator's machine, which publishes the verdict there (cloud_relay.sh). Return the verdict on a probe ref, and push nothing else; this builds one parentless commit with a private index and touches no branch of your checkout: `R=$(git rev-parse --show-toplevel); G=$(git rev-parse --absolute-git-dir); mkdir -p $W/pr && cp -r $W/verdict.md $W/ev $W/pr/ && cd $W/pr && T=$(GIT_DIR=$G GIT_INDEX_FILE=$W/idx GIT_WORK_TREE=$W/pr sh -c 'git add -A -f . && git write-tree') && C=$(GIT_DIR=$G git -c user.name=hpo-fixer -c user.email=70032254+tvofi@users.noreply.github.com commit-tree $T -m "verdict 3566 d9677a53d55bcf114086b15ab97588b7fb429b22") && git -C $R push -q origin $C:refs/heads/probe/rev-3566-f22d5008`. That ref is the return signal. Do not post comments, approve or merge.
Every way your turn ends pushes a verdict to that ref: a setup or hook refusal that stops you pushes `Fix review: blocked d9677a53d55bcf114086b15ab97588b7fb429b22 seat-refused: <the refusing line>`; never end your turn while a background poll runs. After the push, read the ref back with `git ls-remote origin refs/heads/probe/rev-3566-f22d5008`, and push again if it does not print your commit.
A red is owed a `## Red checks` answer, and may block, only when its name is in the set `python3 tools/audit/seat/merge_train.py owed-reds` prints (defect-root-cause.md); any other red is neither answered nor a block.
Never write to any branch except your return refs. Never work around a hook or a refusal; report it in your result instead.
Discovery reads (search, list, read across files) go through Agent subagents, as the frugal routing guard requires: when it refuses inline work, dispatch a haiku or sonnet Agent subagent to do it rather than bypassing the guard; never set FRUGAL_ALLOW_INLINE and never edit .claude/settings.json.

Brief (snapshotted when this payload was rendered):
# Review packet #3566
head: d9677a53d55bcf114086b15ab97588b7fb429b22
base: e23124ff6e45bac1d48b4a775dad555a37965355

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: red
CodeQL id=132264807571 success
arch-score / arch-score id=132264734171 success
arm id=132264505237 skipped
budget-raise-gate / budget-raise-gate id=132264734386 success
cancel-superseded id=132264465697 success
codeql id=132264729850 skipped
codeql / Analyze (actions) id=132264734248 success
codeql / Analyze (javascript-typescript) id=132264734145 success
codeql / Analyze (python) id=132264734114 success
gate id=132265771536 failure
governance id=132264729822 skipped
governance / delivery-status id=132264734152 success
governance / delivery-status-publish id=132264736910 skipped
governance / env-matrix id=132264734311 success
governance / instrument-self-tests id=132264734198 success
governance / policy-docs id=132264734297 success
governance / record id=132264736787 skipped
governance / wave-script id=132264734088 success
hassfest id=132264730248 skipped
hassfest / hassfest id=132264734092 success
kernel-points id=132264735991 skipped
pr-contract id=132265772499 skipped
prelude id=132264465756 success
refresh id=132264465514 success
sweep-self id=132266635032 skipped
tests id=132264729798 skipped
tests / arch-instrument id=132265908964 in_progress
tests / briefs id=132264734158 success
tests / browser id=132265908663 success
tests / closure-scope id=132264734156 success
tests / closures id=132265908769 in_progress
tests / coverage id=132265908717 in_progress
tests / fast (3.14) id=132265908720 in_progress
tests / mutation id=132264734299 success
tests / mutation-autofix id=132266097948 skipped
tests / mutation-pins id=132266097295 skipped
tests / nightly-ha id=132265911113 skipped
tests / nightly-status id=132264734165 success
tests / replay id=132265914325 skipped
tests / typing id=132265908662 success
validate id=132264729670 skipped
validate / validate-hacs id=132264734123 success

## Refusals
none

## Advisories
hot-file: HPO_BUS_TRAIN_STATE is unset, so every merge verdict reads unboarded
required-wait: required context `gate` reads concluded failure at d9677a53d55bcf114086b15ab97588b7fb429b22 in the digest, but merge_train.py classify --pr reads WAIT (pending: gate red: none): classify decides, as bus.sh's dispatch does, and a pending check never refuses

## carry_audit at the head
NOTE stale tree: 50373173d486faf394b24637c177ab38b691b394 lacks origin/main fdb526895c31c430b31325718f8af768807ffbfb; roster read at origin/main
NOTE body item e6db542a: R11-INTAKE-R10-RESIDUE
CARRY-AUDIT: 1 finding item(s): 1 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
unverified git grep -n 'nudge\.md' <rev> -- . ':!dev/programme/triage' ':!dev/programme/delivery' ':!dev/audit' ':!dev/programme/rosters/*.json' | wc -l
             `git grep` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  ok         node tools/policy/policy_lint.mjs
             `tools/policy/policy_lint.mjs` is in the tree at this head
  ok         node tools/policy/policy_lint.mjs --budgets
             `tools/policy/policy_lint.mjs` is in the tree at this head
  ok         node tools/policy/rules_sync.mjs --check
             `tools/policy/rules_sync.mjs` is in the tree at this head
  ok         python3 -I tools/audit/seat/sweep_render.py --self-test
             `tools/audit/seat/sweep_render.py` is in the tree at this head
  ok         python3 -I tools/policy/budget_raise_gate.py --self-test
             `tools/policy/budget_raise_gate.py` is in the tree at this head
  ok         python3 -I tools/audit/seat/postmerge.py --self-test
             `tools/audit/seat/postmerge.py` is in the tree at this head
  ok         python3 tests/structure.py
             `tests/structure.py` is in the tree at this head
  ok         python3 tests/layout.py
             `tests/layout.py` is in the tree at this head

FIGURES: 8 resolved, 1 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
none

## Review scope: full (first round: no --reviewed-head)

## Three-dot diff
diff --git a/.claude/rules/gate-scoping.md b/.claude/rules/gate-scoping.md
index 869feb82f5..93ec7b4e75 100644
--- a/.claude/rules/gate-scoping.md
+++ b/.claude/rules/gate-scoping.md
@@ -24,7 +24,7 @@ clears `tests/entities.py`'s history reds (#1693, #1699, #1704).
 `SLOT_MIN_SECONDS`; else `none`. `prepr.sh` takes one at its first heavy step. Arrival orders
 each priority band; a dead or expired ticket is skipped. An expired or abandoned lease is
 free, a slot once its pid is gone. A `lease` wait ends at the script's recorded seconds, rc 76: `run.sh` names it unrun. `flock-wrap`
-retakes a lapsed lease. That lease, not the tick's count, is nudge.md §8's cap; hold it with
+retakes a lapsed lease. That lease, not the tick's count, is the `prepr.sh` cap; hold it with
 `python3 tests/gate_lock.py take|renew|release --label <your-label>` (renew between commands), never `mkdir`.
 
 The owner file carries your label and a 30-minute `expires_at`. `renew` exits 75 while another label
diff --git a/.cursor/rules/gate-scoping.mdc b/.cursor/rules/gate-scoping.mdc
index 62eb13e6f5..89fb307981 100644
--- a/.cursor/rules/gate-scoping.mdc
+++ b/.cursor/rules/gate-scoping.mdc
@@ -23,7 +23,7 @@ clears `tests/entities.py`'s history reds (#1693, #1699, #1704).
 `SLOT_MIN_SECONDS`; else `none`. `prepr.sh` takes one at its first heavy step. Arrival orders
 each priority band; a dead or expired ticket is skipped. An expired or abandoned lease is
 free, a slot once its pid is gone. A `lease` wait ends at the script's recorded seconds, rc 76: `run.sh` names it unrun. `flock-wrap`
-retakes a lapsed lease. That lease, not the tick's count, is nudge.md §8's cap; hold it with
+retakes a lapsed lease. That lease, not the tick's count, is the `prepr.sh` cap; hold it with
 `python3 tests/gate_lock.py take|renew|release --label <your-label>` (renew between commands), never `mkdir`.
 
 The owner file carries your label and a 30-minute `expires_at`. `renew` exits 75 while another label
diff --git a/CLAUDE.md b/CLAUDE.md
index d7773599b0..f15d493f4e 100644
--- a/CLAUDE.md
+++ b/CLAUDE.md
@@ -110,7 +110,7 @@ Under `dev/governance/roles/`.
 
 | contract | the role |
 |---|---|
-| `orchestrator.md` | dispatches, merges, holds the freeze, records, stamps; Cursor turn `nudge.md` |
+| `orchestrator.md` | dispatches, merges, holds the freeze, records, stamps |
 | `fixer.md` | owns one architecturally sound fix: failing test first, mutation proof, the finder's harness at both ends, a null control for every quantified claim; steps 2–8 re-execute after any rebase or merge, and the handoff to review freezes the branch |
 | `fix-review.md` | reviews one fix adversarially, from a detached worktree at the head SHA, with the **finder's** harness and never the fixer's; a head that moved under the review is a blocked verdict |
 | `designer.md` | designs an L or XL group with no approved design before its fixer, pipelined behind its last predecessor: the architect note at `design/<group>`, never production code |
diff --git a/dev/README.md b/dev/README.md
index c2c6d20fb0..7b906fa4f2 100644
--- a/dev/README.md
+++ b/dev/README.md
@@ -74,7 +74,7 @@ round adds its own directory rather than rewriting an earlier one.
 | `CLAUDE.md` | repository root | the index: names every policy file, the obligation each carries, and the role or dimension it binds |
 | `AGENTS.md` | repository root | the harness-neutral entry point; it defers to `CLAUDE.md` and states no policy of its own |
 | `tools/audit/seat/INSTRUMENTS.md` | `tools/audit/seat/` | the operator's guide to the seat instruments: what each does and which refusal saves you (usage, not policy) |
-| role contracts | `dev/governance/roles/` | one contract per role: `COMMON.md` (the finder's contract), `fixer.md`, `fix-review.md`, `designer.md`, `design-review.md`, `verifier.md`, `judge.md`, `root-cause.md`, `orchestrator.md`, `nudge.md` |
+| role contracts | `dev/governance/roles/` | one contract per role: `COMMON.md` (the finder's contract), `fixer.md`, `fix-review.md`, `designer.md`, `design-review.md`, `verifier.md`, `judge.md`, `root-cause.md`, `orchestrator.md` |
 | rules | `dev/governance/rules/` | the canonical rule files; `.claude/rules/` is generated from them by `node tools/policy/rules_sync.mjs`, never edited by hand |
 | dimension briefs | `dev/governance/dimensions/` | each in the owner's words: what the dimension measures and how |
 | decisions | `dev/governance/decisions/` | the ADRs: the identity split, the merge boundary, verdict authorship, the design seats |
@@ -191,8 +191,7 @@ The ruleset is the owner's. `tools/ci/ruleset_cutover.py` is the instrument
 that cut its required contexts over to `gate`: it saves a rollback copy, PUTs
 the ruleset's six writable keys, refuses with the difference where either half
 of the read-back fails, and `--rollback` PUTs the saved copy back.
-`dev/governance/roles/nudge.md` section 4 is the rule for reading it: the live
-ruleset every turn, never a remembered list.
+Read it live each time, never from a remembered list.
 
 ### The workflow files
 
@@ -360,7 +359,7 @@ cites any file but that script.
 | orchestrator | runs | fixer, reviewer and design seats | `tools/audit/seat/instruments/cloud_dispatch.py.md`: `or fire the standing trigger` |
 | orchestrator | runs | tick_loop.sh | `tools/audit/seat/instruments/tick_loop.sh.md`: `in place of a seat looping the tick` |
 | orchestrator | runs | beat_jobs.py | `tools/audit/seat/instruments/beatd.py.md`: `until a supervisor unit is applied it runs under` |
-| orchestrator | runs | merge_train.py | `dev/governance/roles/nudge.md`: `tools/audit/seat/merge_train.py run` |
+| orchestrator | runs | merge_train.py | `tools/audit/seat/instruments/merge_train.py.md`: `queued PRs merge through` |
 | orchestrator | runs | heartbeat.sh --watch | `tools/audit/seat/instruments/heartbeat.sh.md`: `the owner schedules a cloud task` |
 | orchestrator | writes | relay hold list | `tools/audit/seat/cloud_relay.sh`: `only the orchestrator writes or edits it` |
 | cloud_dispatch.py | writes | dispatch ref | `tools/audit/seat/cloud_dispatch.py`: `"push", "-q", "origin", f"{commit}:refs/heads/{ref}"` |
diff --git a/dev/governance/config/policy_budgets.json b/dev/governance/config/policy_budgets.json
index d5bf6c0aac..920a3914b6 100644
--- a/dev/governance/config/policy_budgets.json
+++ b/dev/governance/config/policy_budgets.json
@@ -6,7 +6,7 @@
   "_floor_is_not_the_cost": "always_loaded_tokens measures a session that opens nothing. Moving prose out of CLAUDE.md into a paths:-scoped rule lowers it without deleting a line: across the index split the floor fell by more than half while corpus_tokens moved a fraction of a percent. The two caps below are what stop that drop being recorded as headroom -- corpus_tokens does not move when prose moves, and roles charge a seat for what it loads once it opens a file. Policy: .claude/rules/ratchet-budgets.md.",
   "_band": 500,
   "_band_note": "Applies to the five aggregate caps only -- always_loaded_tokens, corpus_tokens and the three roles caps -- which are compared against cap+_band. Per-file caps below are compared exactly and keep zero headroom deliberately. A cap re-recorded to the measured value every time leaves the NEXT pull request refused by the previous seat's arithmetic rather than by its own prose: measured over 2026-09-08..17, twenty consecutive commits sat at exactly zero corpus headroom, 24 of 39 capped files sit there now, and the corpus still rose across a window where the cap was pinned at measured every commit. The recorded cap is the last measurement; the band is the room a seat works in without touching it. Re-record down when the measurement falls more than _band below the cap, and on any reclassification -- .claude/rules/ratchet-budgets.md.",
-  "corpus_tokens": 68618,
+  "corpus_tokens": 64899,
   "roles": {
     "fixer": {
       "opens": [
@@ -74,7 +74,6 @@
     "tools/audit/briefs/fix-review.md": 140,
     "tools/audit/briefs/fixer.md": 315,
     "tools/audit/briefs/judge.md": 30,
-    "tools/audit/briefs/nudge.md": 115,
     "tools/audit/briefs/orchestrator.md": 295,
     "tools/audit/briefs/root-cause.md": 84,
     "tools/audit/briefs/verifier.md": 39,
diff --git a/dev/governance/roles/nudge.md b/dev/governance/roles/nudge.md
deleted file mode 100644
index e0b5636ac5..0000000000
--- a/dev/governance/roles/nudge.md
+++ /dev/null
@@ -1,115 +0,0 @@
-# The orchestrator nudge
-
-This file binds the Cursor orchestrators on grok and qwen. Any other agent uses it as the reference for a timer, a heartbeat, and one turn's scan. The role contract is `dev/governance/roles/orchestrator.md`. This file is the turn that contract names.
-
-Run the numbered steps every turn, in order. Do not stop the turn on a log line, a pending check, or a sentence that names work nobody is doing.
-
-A live timer may add three things, and only for that session: a dated owner mandate, seat identifiers that must not be resumed, and one pull request held open. Re-measure those. They are not copied here: a date or seat id would outlive its session.
-
-This programme keeps seat worktrees under `~/hpo-seats`. A reader on another machine substitutes the root its own dispatch names. The same holds for the state mirror and sync scratch below.
-
-## Who writes, and what stays shut
-
-You dispatch fixers, reviewers, and root-cause seats. You post verdicts, approve, merge, stamp, and update the roster, the state docs, and issue #3394 (#201's continuation). Do not hand the orchestrator role to a seat.
-
-Opus seats that die are replaced by a new Task on grok-4.7-high. Do not resume a dead Opus agent. Sonnet seats use cursor-grok-4.6-high. Haiku seats use composer-2.5.
-
-Pull requests are authored by the hpo-author App through `tools/pr/app_push.sh`. The login that reads GitHub is tvofi. The hpo-approver App posts verdicts. A code-owned path needs a tvofi review citing the session mandate. `tools/pr/app_approve.sh` refuses those paths. A merge verdict on a path that is not code-owned is approved with that script. A record pull request that only touches `dev/programme/delivery` is not code-owned. The ruleset still requires one approving review, so that record pull request is approved as tvofi and then merged.
-
-Do not push `main` with the deploy key. Do not merge with the admin flag. Do not edit `VERSION`, the manifest version, or the `RELEASE_NOTES.md` heading except through `tools/release/stamp.py`. A merge message must not close #3394. Write `Leaves #3394 open`. Never the negated form. Do not run a full `tests/derive_closures.sh` off Darwin. Use that script's single-script mode. Touch a claim file only when the branch is claiming drift. Compare a branch with three dots, never two. Run the train under `python3 -u` so its log is not block-buffered.
-
-A timer subscription dedupes by name and answers created false without replacing the prompt. Unsubscribe first, then subscribe. Do not call the two together.
-
-`--ignore-red` replaces the train's default ignore list, so name both `tests / nightly-status` and `governance / delivery-status`.
-
-## 1. Verdict and handoff
-
-Each turn, run `tools/audit/seat/bus.sh` watch once, and also fetch every open pull request head and every live `handoff/<topic>` ref. Watch-once prints only a ref that moved. A handoff already printed is still owed.
-
-For each open pull request, test whether the head contains the handoff tip. If it does not, run `tools/audit/seat/update_pr.sh` this turn when a prepr slot is free and that group's fixer worktree was not written in the last 15 minutes. Run `tools/audit/seat/open_pr.sh` when no pull request exists. If the push or the open refuses and no fixer is working, dispatch the fixer in this same turn. A fixer worktree with unpushed commits and no process is that handoff, not a new fixer.
-
-When the update exits 0, the printed HEAD contains the handoff. Dispatch the reviewer for that HEAD in the same turn. Do not end on a reviewer who waits.
-
-When a review ref moves, confirm that verdict when it names the contained head and carries its nonce, and post it once required checks have concluded at that head. A verdict on an ancestor is not a verdict on this head. A blocked fix review returns to the original fixer in that same turn. Do not repair the body yourself. Do not spawn a new seat for that repair. The same reviewer takes the next round. Do not update a head whose reviewer worktree under the seat root was written in the last 15 minutes.
-
-## 2. Reviewer owed
-
-This check uses the live head, not the bus line. For each open pull request whose head contains the fixer handoff, if the newest posted fix review does not name that 40-hex head, dispatch a reviewer this turn, without waiting for required checks. A head that moved since a merge verdict goes to `tools/pr/app_approve.sh --carry` first, and gets a reviewer only when the carry refuses. Do not dispatch a reviewer for a pull request whose title starts with `record:`, or for a head a fixer is still changing, or when a reviewer worktree for that pull request was written in the last 15 minutes. Do not start a second reviewer for a group that already has one. Before calling a seat stalled, read `tests/gate_lock.py`. A seat that holds the lease is not stalled.
-
-## 3. Train status, before any merge
-
-Find a live `tools/audit/seat/merge_train.py` and read its log. A live process holds every other merge. Do not merge by hand, do not arm auto-merge, and do not load a second train. An empty log, or a last line still on the ci step, is that one pull request's CI wait. Write the line and continue the scan. Do not end the turn on the train log.
-
-`TRAIN DONE` means that queue finished. Do not reload it. `TRAIN STOPPED` names the pull request, the step, and the reason. Later entries were not graded. Do not reload that queue. A head that does not contain `origin/main` after the ci step is the one restart the script names: run the train again on the pulls it had not merged. Do not restart a queue whose entries are already merged.
-
-Load a train on the hourly pitch, with `--bot-prs`, when no train is running and fewer than four preprs are running. One verdicted pull request is still a train. The record pull request merges inside the pitch, not between pitches. Verdicted means the newest posted fix review is merge for this 40-hex head, or `tools/pr/app_approve.sh` carry says the verdict carries. The train waits for CI in its own ci step, so do not wait for it. Order the queue by creation time, oldest first. Each entry carries the pull request number, the 40-hex the merge verdict names, the comment id (the comment must cite an absolute evidence path), and the issues the body intends to close.
-
-Leave out a `record:` pull request, which `--bot-prs` merges. A `*_budgets.json` or policy-path head stays in: the train routes it serial, and `--pre-flight` parks one the owner has not approved at that head (`Train.raise_hold`, `Train.policy_gate`) for step 7. Never pass `--allow-red`.
-
-The command is detached, because a background waiter dies at two hours:
-
-```
-python3 -u tools/audit/seat/merge_train.py run <queue.json> --bot-prs --pre-flight --mandate "<the session mandate cite>" --ignore-red 'tests / nightly-status' --ignore-red 'governance / delivery-status'
-```
-
-## 4. Required checks
-
-Required checks are the contexts in ruleset `main-protect-checks`. Read that ruleset every turn. The id last used to open it was 23698884. Do not trust a remembered list. `gate` is the one required check; `tests / nightly-status` and `governance / delivery-status` are not units. Pending is not a pass. DIRTY is the claim-file merge GitHub cannot run. Absorb `main` locally with the claimnotes driver.
-
-## 5. Budget files
-
-A `*_budgets.json` change never goes on the train. Merge a budget-file pull request by a mandate approval already on that head, oldest first, only when no train is running. A new head that raises a budget needs a new tvofi review citing the session mandate. A decrease is still a budgets file. Merge it directly, not on the train.
-
-## 6. Record pull requests
-
-A `record:` pull request needs no fix review and no reviewer. The nightly record beat merges it when its approver token is present, and the pitch takes it. By hand only when the beat's outcome is a `skip-` other than `skip-train-hold`: once required checks are success or skipped and no train is running, approve it as tvofi and merge it. An overlay may hold one open.
-
-## 7. Direct merge, when no train is running
-
-Direct-merge only what `--pre-flight` parked: a budgets-file or policy-path pull request whose mandate review is already on that head. Ready means required checks are success or skipped, GitHub reports it mergeable, and the newest posted fix review is merge for this head or carries. Oldest first. Anything the queue takes waits for the pitch.
-
-## 8. Prepr slots
-
-Up to four `prepr.sh` run at a time: each takes one of `tests/gate_lock.py`'s four heavy slots just before its first heavy step (a run whose heavy steps are all skipped takes none), and a fifth queues: the lease, not the tick's count, is the cap. A seat's own prepr counts. `tools/audit/seat/open_pr.sh`, `tools/audit/seat/update_pr.sh`, `tools/pr/app_push.sh` and a `tests/derive_closures.sh` run each count as one. Do not recarry a branch a seat is writing. Skip a group whose fixer or reviewer worktree was written in the last 15 minutes, or whose own prepr is running. Recarry may run during a train's CI wait. It may not run while the train itself is in recarry.
-
-## 9. Conflicting or DIRTY
-
-Absorb `origin/main` into an open head only when it is DIRTY or `git merge-tree --write-tree origin/main <head>` reports a conflict. A head merely behind `main` stays put. Merge-tree exit 0 and no train running: merge `origin/main` and push with `tools/pr/app_push.sh`, then `tools/pr/approve_held_runs.sh`. A content conflict stops. Name the path and return it to the fixer who owns the branch. Do not resolve it yourself.
-
-## 10. A refusal with nobody on it
-
-If a push or an open is refused and no fixer is working on that group, dispatch a fixer this turn. Do not leave the refusal for a later nudge. Do not start a second fixer for a group that already has one working. When you see yourself stating that work needs to be done and no seat is doing it, dispatch or perform that work in this turn.
-
-## 11. Stalled runs, autofix, and a red main
-
-Zero check runs is stalled zero-runs. Run `tools/pr/approve_held_runs.sh` after every App push. CodeQL on a tools-evidence diff is `tools/audit/seat/codeql-triage-poll.sh`, not a new fixer. Read the autofix summary before dispatching a fixer. `changed` means wait for the bot commit. `skip-failed-recording` means fix the script and do not re-derive. `skip-manual-repair-owed` means closures failed and the job was not under-scoped, so no bot commit is coming and the check itself is the repair. `skip-clean` means the check passed and no bot commit is coming. A selectable script with no recording is not under-scoped: add it to a derive lane or record it alone. A red `gate` on `main` outranks the queue. Revert a merge that reddened `main` only when that diff can reach the failure. Never pass `--allow-red`.
-
-## 12. After each merge
-
-`tools/audit/seat/postmerge.py` runs after every merge, from `merge_pr.sh` and from the train, and an `OWED` line it prints is the work left: rerun it with `--retry` once the cause is gone. This step keeps only what that tool cannot do. Only a decision-changing merge owes `dev/programme/HANDOVER.md` an updated-for line, in its own pull request. After a roster update, an open issue the plan does not name is scheduled, deferred, or refused. Do not file a new issue. Issues a session has already deferred stay deferred. The overlay names them.
-
-## 13. Stamps
-
-Run `tools/release/stamp.py` only when no train is waiting, the roster's stamp-unblock group is done, and the latest `ci.yml` push run's `gate` on the current `origin/main` is green. Not during a CI wait. A push-triggered green `gate` is not a nightly. `nightly-status` reads the last concluded schedule or workflow_dispatch on `main`. Do not rerun a push-triggered run as the nightly. A dependabot alert the overlay names stays open. Do not force an override the overlay forbids.
-
-## 14. Handed-off seats
-
-Do not resume a seat the session overlay names as handed off. A later refusal on another group still gets a new seat. Do not start a second fixer or reviewer while that group's worktree was written in the last 15 minutes.
-
-## 15. CI watch
-
-Each turn, read the required contexts from ruleset `main-protect-checks`, as step 4 says. For every open pull request, take the latest check run of each required context on the head oid. A conclusion of failure returns that pull request to its original fixer this turn, with the job URL and failure line, unless `merge_train.py classify <head> --pr <N>` reads it WAIT (a gate deferral). `ci-watch.sh` alerts only on a new signature, so a red it printed is still owed: the signature file is not this check. Pending, `nightly-status` and `delivery-status` are not a return. Zero check runs is stalled zero-runs: `tools/pr/approve_held_runs.sh`, not a fixer. Read the autofix summary before returning a closures or mutation failure, under the same words as step 11. Do not start a second fixer when that group's fixer worktree was written in the last 15 minutes. A pull request the overlay holds is not returned by this step.
-
-## 16. Unblocked groups
-
-Load the roster through `tools/audit/seat/roster_lib.py` at the ref `tools/audit/seat/state_docs.py` defaults. Dispatch by pull: a flow lane under its cap (A critical path 4, B product 4, C process 3, F fly-in 2) takes its eligible group of greatest critical-path depth, behind `tools/audit/seat/pr_cap.py` dispatch-gate, which enforces the total. Eligible: resume stage not-started, after-edges all done or absent, not deferred or refused, no fixer working. Brief it that group's own roster brief. Done stages are the pair `roster_lib.py` names. Register a fly-in at dispatch with `tools/audit/seat/roster_edit.py` append-group, named `R10-FLY-`. An expedite item (red main, quota exhaustion, outage, security) bypasses the caps, one at a time.
-
-## 17. State
-
-When the roster or the open pull-request set changed, run `tools/audit/seat/state_docs.py` with its push flag and the mirror at `~/hpo-orch/state`. That regenerates the plan table, the resume, and the next-session prompt on the plan ref that script writes. Fetch `origin/main` at the start of the turn and measure how many commits `HEAD` lacks. An ancestor checkout is not current.
-
-## 18. After the merge, and the instruments
-
-After each merge, read which issues the merge commit closed. Reopen one the message did not name as intended. A carry is `tools/pr/app_approve.sh` when its carry predicate holds. Only `tools/audit/seat/merge_train.py batch` skips the CI wait after `main` moves. Never clear a live gate lease. `tools/pr/preflight.sh` reads the body on stdin. A filename argument reads nothing and prints clean. Run each instrument from its path in the tree, never from a scratch copy. Look it up in the instruments guide first (`orchestrator.md` 13). If no sync loop is running, start one detached with `tools/audit/seat/wt_sync.sh` and the scratch at `~/hpo-orch`. Do not start a second.
-
-A background update that has exited 0 since the last turn is that notification: dispatch the reviewer for its printed HEAD before ending. A required check that failed since the last turn is the same kind of notification: return that pull request to its fixer before ending.
diff --git a/dev/governance/rules/gate-scoping.md b/dev/governance/rules/gate-scoping.md
index 869feb82f5..93ec7b4e75 100644
--- a/dev/governance/rules/gate-scoping.md
+++ b/dev/governance/rules/gate-scoping.md
@@ -24,7 +24,7 @@ clears `tests/entities.py`'s history reds (#1693, #1699, #1704).
 `SLOT_MIN_SECONDS`; else `none`. `prepr.sh` takes one at its first heavy step. Arrival orders
 each priority band; a dead or expired ticket is skipped. An expired or abandoned lease is
 free, a slot once its pid is gone. A `lease` wait ends at the script's recorded seconds, rc 76: `run.sh` names it unrun. `flock-wrap`
-retakes a lapsed lease. That lease, not the tick's count, is nudge.md §8's cap; hold it with
+retakes a lapsed lease. That lease, not the tick's count, is the `prepr.sh` cap; hold it with
 `python3 tests/gate_lock.py take|renew|release --label <your-label>` (renew between commands), never `mkdir`.
 
 The owner file carries your label and a 30-minute `expires_at`. `renew` exits 75 while another label
diff --git a/dev/programme/delivery/3566.md b/dev/programme/delivery/3566.md
new file mode 100644
index 0000000000..8e55d6120d
--- /dev/null
+++ b/dev/programme/delivery/3566.md
@@ -0,0 +1 @@
+- [#3566](https://github.com/tvofi/heatpump_optimizer/pull/3566) — **open**, R10-NUDGE-RETIRE: r10 nudge retire (R10-NUDGE-RETIRE)
diff --git a/tests/closures.json b/tests/closures.json
index 1d12ff8abb..d4f5148364 100644
--- a/tests/closures.json
+++ b/tests/closures.json
@@ -1281,7 +1281,6 @@
    "custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js",
    "dev/README.md",
    "dev/governance/roles/fix-review.md",
-   "dev/governance/roles/nudge.md",
    "dev/programme/rosters/wave-r10-groups.json",
    "docs/architecture.md",
    "docs/automations.md",
@@ -1652,7 +1651,6 @@
    "dev/governance/roles/fix-review.md",
    "dev/governance/roles/fixer.md",
    "dev/governance/roles/judge.md",
-   "dev/governance/roles/nudge.md",
    "dev/governance/roles/orchestrator.md",
    "dev/governance/roles/plan-review.md",
    "dev/governance/roles/proposal-triage.md",
@@ -4042,7 +4040,8 @@
  },
  "inert_reads": {
   "tests/doc_claims.py": [
-   "docs/site/docs.css"
+   "docs/site/docs.css",
+   "tools/audit/seat/instruments/merge_train.py.md"
   ],
   "tests/entities.py": [
    "LICENSE",
diff --git a/tests/gate_lock.py b/tests/gate_lock.py
index 8bfec99b5a..d70963c8bb 100644
--- a/tests/gate_lock.py
+++ b/tests/gate_lock.py
@@ -46,8 +46,8 @@ measure the machine, so their numbers are comparable only with nothing else
 running: ``stress.py`` and ``harness_headers.py``. Commands that are
 multi-minute CPU-bound but do not measure take instead from the heavy-slot
 POOL (``take_slot``/``release_slot``, ``heavy_slots()`` slots under the `slots`
-subdirectory; #2267), which is what makes nudge.md's four-prepr cap mechanical
-instead of advisory. ``needs_lease`` classifies a scope into the three answers
+subdirectory; #2267), which makes the four-prepr cap mechanical instead of
+advisory (``dev/governance/rules/gate-scoping.md``). ``needs_lease`` classifies a scope into the three answers
 ``run.sh`` dispatches on: ``lease``, ``slot`` or ``none``.
 
 A pool slot is held for the LIFE of its run, not for its lease: the taker's pid
@@ -88,7 +88,7 @@ TICKET_PREFIX = "ticket-"
 # The single lease above serialises one exclusive holder (stress.py). Proving a
 # branch is *runnable* is throughput-bound instead: several commands that each
 # load the box may share it up to a cap, and until now the cap was the
-# orchestrator's, held by hand (nudge.md step 8) and enforced by nothing. A pool
+# orchestrator's, held by hand and enforced by nothing. A pool
 # of HEAVY_SLOTS slots, taken by `take_slot`, is that cap made mechanical.
 #
 # THE POOL IS ITS OWN LOCK DIR, `lock_dir/<POOL_DIRNAME>`, for two reasons. Its
diff --git a/tests/layout.json b/tests/layout.json
index 76646b90a0..037683592f 100644
--- a/tests/layout.json
+++ b/tests/layout.json
@@ -762,11 +762,6 @@
    "new": "dev/governance/roles/judge.md",
    "since": null
   },
-  {
-   "old": "tools/audit/briefs/nudge.md",
-   "new": "dev/governance/roles/nudge.md",
-   "since": null
-  },
   {
    "old": "tools/audit/briefs/orchestrator.md",
    "new": "dev/governance/roles/orchestrator.md",
diff --git a/tools/audit/seat/instruments/sweep_template.md.md b/tools/audit/seat/instruments/sweep_template.md.md
index 9eb4be044e..d57fdbc75a 100644
--- a/tools/audit/seat/instruments/sweep_template.md.md
+++ b/tools/audit/seat/instruments/sweep_template.md.md
@@ -2,6 +2,6 @@
 
 - `sweep_template.md` — the orchestrator's recurring sweep, steps in order,
   each naming the instrument it runs by tree path and the rule file
-  (`orchestrator.md`, `nudge.md`, `CLAUDE.md`) it carries out; a usage guide
-  that restates no policy. When: read through `sweep_render.py`. Refusal: none
+  (`orchestrator.md`, `standing-merge.md`, `standing-dispatch.md`,
+  `CLAUDE.md`) it carries out; a usage guide that restates no policy. When: read through `sweep_render.py`. Refusal: none
   of its own -- the renderer's.
diff --git a/tools/audit/seat/merge_pr.sh b/tools/audit/seat/merge_pr.sh
index 751fe80fd9..d8b1e87080 100755
--- a/tools/audit/seat/merge_pr.sh
+++ b/tools/audit/seat/merge_pr.sh
@@ -337,6 +337,6 @@ gh pr merge $PR --merge --match-head-commit $S || exit 1  # mut:merge
 sleep 8; echo "merged $(gh pr view $PR --json mergeCommit --jq .mergeCommit.oid)"
 for n in "$@"; do echo "issue $n $(gh issue view $n --json state --jq .state)"; done
 bash tools/audit/worktree_gc.sh $R 2>&1 | tail -1; git pull -q --ff-only origin main
-# The rest of nudge.md step 12 (the record-issue line, the roster stage, the state docs, main's
+# The post-merge bookkeeping (standing-merge.md; the record-issue line, the roster stage, the state docs, main's
 # suite state): a failure is printed OWED and never undoes the merge, but fails the script.
 python3 -I tools/audit/seat/postmerge.py "$PR" --repo $R --state-dir "${HPO_STATE_DIR:-$HOME/.local/state/hpo}"  # mut:postmerge
diff --git a/tools/audit/seat/merge_train.py b/tools/audit/seat/merge_train.py
index 41db06854a..f692a2ae16 100644
--- a/tools/audit/seat/merge_train.py
+++ b/tools/audit/seat/merge_train.py
@@ -3195,7 +3195,7 @@ class Train:
         return st.split()[-1]
 
     def post_merge(self, pr: int) -> None:
-        """The rest of nudge.md step 12, by `postmerge.py` (the record-issue line, the
+        """The post-merge bookkeeping, by `postmerge.py` (the record-issue line, the
         roster stage, the state docs, main's suite state). Its OWED lines are
         logged and never undo or stop the merge; the tool itself opens the
         ledger's `postmerge-owed` event for a step that failed."""
@@ -4669,7 +4669,7 @@ def auto_train_argv(repo: str, state: "str | Path", mandate: "str | None") -> "l
 def sweep(t: Train, train_argv: "list[str]", add=train_add, ledger_log: "str | None" = None) -> int:
     """One backstop sweep; its last line is `SWEEP HELD|REFUSED|DONE ...`. HELD:
     the obligations ledger holds an open `train-stop` (a stopped train is read
-    before anything reloads it: nudge.md step 3). Otherwise each entry
+    before anything reloads it: standing-merge.md). Otherwise each entry
     `build_queue` admits is handed to `add`, unless an earlier sweep handed it
     over at the same head. rc 2 on REFUSED: an unreadable ledger or pull request
     list, or an `add` that could not start a train."""
diff --git a/tools/audit/seat/orchestrator_tick.py b/tools/audit/seat/orchestrator_tick.py
index 560b73541e..fcedfdaecf 100644
--- a/tools/audit/seat/orchestrator_tick.py
+++ b/tools/audit/seat/orchestrator_tick.py
@@ -24,14 +24,14 @@ Sections, each measured:
   TRAIN   is `merge_train.py` alive (pgrep, self excluded); the active queue's
           entries vs merged-into-main (an entry whose PR is already MERGED is
           stale, to drop); the log tail (--train-log, last 5 lines) and its
-          sibling .rc; prepr.sh slots (nudge.md step 8's cap, mechanically).
+          sibling .rc; prepr.sh slots (gate-scoping.md's heavy-slot cap).
   PRS     every open PR: the latest check-run per name at its head (transport
           truth: lowercase conclusions, latest-run-wins) as GREEN / RUN / RED;
           a RED in `merge_train.py owed-reds`' set not answered in the body's
           ## Red checks (every RED when that set is unreadable); missing
           delivery row in the three-dot diff; a queue verdict with the head moved past it
           and no carry; DIRTY/BLOCKED mergeable state; ZERO check runs at a
-          head (the bot-push shape -- approve_held_runs.sh, nudge.md step 11);
+          head (the bot-push shape -- approve_held_runs.sh);
           required contexts absent at the head; twin open PRs at one head
           (the shared-head class); a claim-file touch whose `claims-for:` is
           not VERSION; a head left behind main by more than --behind-max
@@ -50,7 +50,7 @@ Sections, each measured:
           40-55 m). No PR yet is OK inside --stall-hours and STALLED?
           beyond it.
   PLAN    roster groups not done whose predecessors are all done (newly
-          unblocked -- start a fixer; nudge.md step 16) and groups blocked,
+          unblocked -- start a fixer; orchestrator.md section 5) and groups blocked,
           naming the blocker. Read through roster_lib, the one schema reader.
   STATE   state-doc staleness, read-only: the handover's updated-for sha vs
           origin/main's tip, and merged PRs since it with no delivery row
@@ -70,7 +70,7 @@ Sections, each measured:
           the tick's roster ref; exit 1 is one dispatch line and the sweep's
           unowned lines, anything else without its summary is UNREADABLE.
   MAIN    main's tip sha; any non-green required context (the ruleset re-read
-          every tick -- nudge.md step 4: never a remembered list); EVERY
+          every tick: never a remembered list); EVERY
           completed-with-failure lane at the tip, required or not, becomes a
           fixer DISPATCH BRIEF (context, job id + error line, suspected class,
           dispatch instruction; bot lanes lead with the ci-autofix rule) --
@@ -83,10 +83,9 @@ Sections, each measured:
           (one action pinned at two refs across the workflow set); how far
           the checkout sits behind origin/main.
 
-Ported from dev/governance/roles/nudge.md (superseded here where mechanical):
-steps 3 (train status, stale queues), 4 (ruleset re-read), 8 (prepr slots),
-11/15 (zero-runs stall, latest-per-name, pending is not a pass), 16 (unblocked
-groups, deferred stays deferred), 17 (an ancestor checkout is not current).
+Mechanical here: train status and stale queues, the ruleset re-read, prepr
+slots, the zero-runs stall, latest-per-name with pending not a pass, unblocked
+groups (deferred stays deferred), and an ancestor checkout not being current.
 Left behind as the orchestrator's judgement, not reportable from tree/API
 reads: verdict-bus watching, reviewer-owed dispatch, the 15-minute
 worktree-recency rules, post-merge duties, stamps, hold overlays.
@@ -428,7 +427,7 @@ class Tick:
     @staticmethod
     def judge(runs_by_name: dict) -> tuple[list[str], list[str], list[str]]:
         """(green, running, red) over every lane, each by the train's
-        run_state: latest-run-wins, pending is not a pass (nudge.md step 15)."""
+        run_state: latest-run-wins, pending is not a pass."""
         by = {"green": [], "pending": [], "red": []}
         for n, c in runs_by_name.items():
             by[mt.run_state(c)].append(n)
@@ -1859,8 +1858,8 @@ class Tick:
                 self.unreadable(S, "policy state file", str(e)[:80])
 
     def required(self, S: str) -> "list[str] | None":
-        """The ruleset's required contexts, re-read every tick (nudge.md step
-        4: never a remembered list); merge_train.required's own route. One
+        """The ruleset's required contexts, re-read every tick (never a
+        remembered list); merge_train.required's own route. One
         read per tick: MAIN and PRS share it."""
         if getattr(self, "_req", None) is not None:
             return self._req
diff --git a/tools/audit/seat/postmerge.py b/tools/audit/seat/postmerge.py
index f00235630c..7eeadeef39 100644
--- a/tools/audit/seat/postmerge.py
+++ b/tools/audit/seat/postmerge.py
@@ -1,5 +1,5 @@
 #!/usr/bin/env python3
-"""After a merge: the bookkeeping nudge.md step 12 used to hand an agent.
+"""After a merge: the bookkeeping no contract hands an agent (`standing-merge.md`).
 
     python3 tools/audit/seat/postmerge.py [--repo O/R] [--state-dir D] [--dry-run] [--retry] <PR>
     python3 tools/audit/seat/postmerge.py --self-test
@@ -199,9 +199,26 @@ def self_test() -> int:
     code, lines, log = go()
     check("without --retry a clean run closes nothing (null control)",
           not any("ledger.py" in c for c in log), log)
-    step12 = (ROOT / "dev/governance/roles/nudge.md").read_text().split("## 12.")[1].split("\n## ")[0]
-    check("nudge.md step 12 names no beat this tool runs (CARRY 3)",
-          not any(b in step12 for b in ("worktree_gc", "gh_comment", "roster_edit", "state_docs")), step12[:80])
+    # CARRY 3: a beat this tool runs is never also handed to an agent by the
+    # contract owning the post-merge bookkeeping, or it runs twice. The beats are
+    # read from `steps()` itself, so a step added there is checked here unedited.
+    beats = {f"{rb.__name__}.py", "gh_comment.py"} | {
+        Path(argv[2]).name + ("" if argv[3].startswith("-") else " " + argv[3])
+        for _, argv, _ in steps(1, "o/r", Path("."), full, "R10-X")}
+    check("the beats are read from steps(): a subcommand is kept, an option is not",
+          {"state_docs.py", "merge_train.py classify"} <= beats, sorted(beats))
+
+    def handed(text: str) -> "list[str]":
+        return sorted(b for b in beats if b in text)
+    orch = (ROOT / "dev/governance/roles/orchestrator.md").read_text()
+    sec = orch.split("\n## 11.")[1].split("\n## ")[0] if "\n## 11." in orch else ""
+    owner = sec + (ROOT / "dev/governance/roles/standing-merge.md").read_text()
+    check("orchestrator.md section 11 still holds the after-each-merge duty this pin reads",
+          "After each merge" in sec, sec[:80])
+    check("orchestrator.md section 11 and standing-merge.md hand an agent no beat this tool runs (CARRY 3)",
+          handed(owner) == [], handed(owner))
+    check("a contract handing an agent `state_docs.py --push` is caught (null control)",
+          handed(owner + "\n- After each merge: run `state_docs.py --push`.") == ["state_docs.py"])
     print(f"postmerge self-test: {n[0]} checks, {len(fails)} failed")
     return 1 if fails else 0
 
diff --git a/tools/audit/seat/roster_edit.py b/tools/audit/seat/roster_edit.py
index d23919deb5..5d3c8a00a7 100644
--- a/tools/audit/seat/roster_edit.py
+++ b/tools/audit/seat/roster_edit.py
@@ -1457,7 +1457,7 @@ STRUCTURAL_OPS = ("wire-issue", "unwire-issue", "edit-brief", "append-carry",
 def lane_refusal(op, group):
     """The refusal text for a structural op called outside the roster queue
     runner, else None. set-stage, append-group and set-resume stay directly
-    callable (nudge.md and sweep_template.md run them by hand). A caller that
+    callable (sweep_template.md runs them by hand). A caller that
     sets the variable by hand is out of scope: the guard stops a caller that
     does not know the lane, not one that forges it."""
     if op in STRUCTURAL_OPS and os.environ.get(LANE_ENV) != LANE_VALUE:
diff --git a/tools/audit/seat/sweep_template.md b/tools/audit/seat/sweep_template.md
index 35688386a9..4a06f1878c 100644
--- a/tools/audit/seat/sweep_template.md
+++ b/tools/audit/seat/sweep_template.md
@@ -4,9 +4,9 @@ This is a usage guide, not policy, in the sense `tools/audit/seat/INSTRUMENTS.md
 states for itself: it adds no obligation. It orders the recurring sweep a
 Claude Code orchestrator session runs on a timer, names the instrument each step
 runs by its tree path, and cites the rule file each step carries out. The role
-is `dev/governance/roles/orchestrator.md`; the turn it names is
-`dev/governance/roles/nudge.md`, which binds a Cursor orchestrator and is the
-reference for any other agent's timer. Where this file and either of those
+is `dev/governance/roles/orchestrator.md`, and the standing seats' terms are
+`dev/governance/roles/standing.md`, `dev/governance/roles/standing-merge.md` and
+`dev/governance/roles/standing-dispatch.md`. Where this file and any of those
 disagree, they are the rule and this file is the bug.
 
 Render it, never hand-copy it:
@@ -15,9 +15,9 @@ Render it, never hand-copy it:
 
 The overlay is one JSON object holding every placeholder below, and nothing
 else. It is the session's, so it stays out of the tree: it carries the dated
-mandate and the host's own paths, which `nudge.md` keeps out of tracked text
-for the same reason ("a date and a seat id in this file outlive the session
-that measured them"). The renderer refuses a placeholder the overlay leaves
+mandate and the host's own paths, which stay out of tracked text because a
+date, a seat id or a host path written there outlives the session that
+measured it. The renderer refuses a placeholder the overlay leaves
 unfilled, an overlay key or a placeholder this table does not declare, a
 declared placeholder the sweep never uses, and a home-directory path in the
 rendered text that no overlay value supplied.
@@ -60,15 +60,15 @@ ORCHESTRATOR SWEEP, round {{round}}, repository {{repo}}. Read {{seat_ledger}} f
 
 (0) Policy re-read. Run `python3 -I tools/audit/seat/policy_reread_check.py --transcript {{transcript}} --stamp {{policy_stamp}}`. On OWED: `git -C {{orch_checkout}} fetch origin`, then read `CLAUDE.md`, every policy file its index names, and `tools/audit/seat/INSTRUMENTS.md` with `git -C {{orch_checkout}} show origin/main:<path>`; act on any delta against current practice; then `python3 -I tools/audit/seat/policy_reread_check.py --stamp {{policy_stamp}} --write-stamp`, and log the re-read in {{seat_ledger}}. While the check prints OWED (exit 1), that is, until `--write-stamp` ran after the newest compaction, this sweep is not clean, whatever the rest of the board says.
 
-(1) Seats. Cloud seats are uncapped. A fixer for a NEW roster group is dispatched only while fewer than 3 handoffs wait without a pull request and 6 to 10 pull requests are open (owner ruling, 2026-10-28; `tools/audit/seat/pr_cap.py` `dispatch-gate` measures its WIP arm); reviews, repairs and openers are never capped, and a ready critical-path group dispatches past every cap (`dev/governance/roles/orchestrator.md` section 5). Resume the next queued seat from {{seat_ledger}}. Dispatch a record pull request's reviewer (triage, roster batches) on sonnet, and a design, code or architecture pull request's reviewer on opus. Seat worktrees live under {{seat_root}}, each named absolute in its brief (`dev/governance/roles/orchestrator.md` section 5). A handed-off seat is not resumed and an unblocked roster group gets a fixer (`dev/governance/roles/nudge.md` steps 14 and 16).
+(1) Seats. Cloud seats are uncapped. A fixer for a NEW roster group is dispatched only while fewer than 3 handoffs wait without a pull request and 6 to 10 pull requests are open (owner ruling, 2026-10-28; `tools/audit/seat/pr_cap.py` `dispatch-gate` measures its WIP arm); reviews, repairs and openers are never capped, and a ready critical-path group dispatches past every cap (`dev/governance/roles/orchestrator.md` section 5). Resume the next queued seat from {{seat_ledger}}. Dispatch a record pull request's reviewer (triage, roster batches) on sonnet, and a design, code or architecture pull request's reviewer on opus. Seat worktrees live under {{seat_root}}, each named absolute in its brief (`dev/governance/roles/orchestrator.md` section 5). A handed-off seat is not resumed and an unblocked roster group gets a fixer (`dev/governance/roles/orchestrator.md` section 5).
 
 (1b) Standing-seat liveness. The two standing seats are `dev/governance/roles/standing-merge.md` and `dev/governance/roles/standing-dispatch.md`. Run `python3 -I tools/audit/seat/pulse.py --repo {{repo}} {{seat_queues}} {{seat_alives}} {{launch_ledger}}`; a seat that is absent from {{seat_ledger}}, that finished with work still owed, or that a `PULSE` line reports `STOPPED` (`seat <name>:`, `DUPLICATE seat <name>:` or `FOREIGN <name>:`, a beat by a process that is not the seat) is restarted in this sweep on its contract with its queue, and the restart is logged in {{seat_ledger}}. Routine work goes to these seats as queue lines, never inline (`dev/governance/roles/orchestrator.md` section 5).
 
-(2) Handoffs. The beat's `opener` and `head-watch` rows (`tools/audit/seat/beat_jobs.py`, run by `tools/audit/seat/beatd.py`) open each handoff that has no pull request through `tools/audit/seat/open_driver.py` and record each moved head: act on every `OWED ... open-refused`, `NEEDS-TITLE`, `STARVED` and `STUCK` line of {{digest}}/digest.txt and every `HEAD-MOVED` and `STUCK` line of {{digest}}/events.txt. Cross-check `git -C {{orch_checkout}} ls-remote --heads origin 'handoff/r{{round}}-*'` against the open pull-request heads, and run `tools/audit/seat/bus.sh orphans`. Queue a line to the dispatch seat (`dev/governance/roles/standing-dispatch.md`) for a handoff ahead of its pull request (`update_pr.sh`), for one the opener refused or left `STUCK` once its reason is answered (`open_pr.sh`), and for a `HEAD-MOVED` line at a reviewed head (a reviewer at the new head); read its report, and run none of them yourself (`dev/governance/roles/orchestrator.md` section 5b; `dev/governance/roles/nudge.md` steps 1, 2 and 8).
+(2) Handoffs. The beat's `opener` and `head-watch` rows (`tools/audit/seat/beat_jobs.py`, run by `tools/audit/seat/beatd.py`) open each handoff that has no pull request through `tools/audit/seat/open_driver.py` and record each moved head: act on every `OWED ... open-refused`, `NEEDS-TITLE`, `STARVED` and `STUCK` line of {{digest}}/digest.txt and every `HEAD-MOVED` and `STUCK` line of {{digest}}/events.txt. Cross-check `git -C {{orch_checkout}} ls-remote --heads origin 'handoff/r{{round}}-*'` against the open pull-request heads, and run `tools/audit/seat/bus.sh orphans`. Queue a line to the dispatch seat (`dev/governance/roles/standing-dispatch.md`) for a handoff ahead of its pull request (`update_pr.sh`), for one the opener refused or left `STUCK` once its reason is answered (`open_pr.sh`), and for a `HEAD-MOVED` line at a reviewed head (a reviewer at the new head); read its report, and run none of them yourself (`dev/governance/roles/orchestrator.md` section 5b; each push takes a heavy slot, `dev/governance/rules/gate-scoping.md`).
 
-(3) Merges. Queue one line per verdicted pull request to the merge seat (`dev/governance/roles/standing-merge.md`) naming the pull request, its verdicted head and mandate {{mandate}}, and read its report: the seat runs the train on the recommended flags (`--overlap --approval-carry --skip-bad --free-holders --bot-prs --pre-flight --mandate {{mandate}}`), joining the live train as its next batch and never starting a second (`dev/governance/roles/nudge.md` step 3; `dev/governance/roles/orchestrator.md` section 11). The open record or autofix pull request merges inside that train through `--bot-prs`, not between pitches. A budget-file or policy head goes the batch's serial route, where `--pre-flight` parks a budget raise or a policy head the owner has not approved at that head under an open mandate (`Train.raise_hold`, `Train.policy_gate`); a parked one merges directly under mandate {{mandate}} (`dev/governance/roles/nudge.md` steps 5 and 7; `CLAUDE.md` rule 2). Between pitches, a record or autofix pull request merges by hand only behind `tools/audit/seat/record_row.py --automerge-check` (`dev/governance/roles/nudge.md` step 6).
+(3) Merges. Queue one line per verdicted pull request to the merge seat (`dev/governance/roles/standing-merge.md`) naming the pull request, its verdicted head and mandate {{mandate}}, and read its report: the seat runs the train on the recommended flags (`--overlap --approval-carry --skip-bad --free-holders --bot-prs --pre-flight --mandate {{mandate}}`), joining the live train as its next batch and never starting a second (`dev/governance/roles/standing-merge.md`; `dev/governance/roles/orchestrator.md` section 11). The open record or autofix pull request merges inside that train through `--bot-prs`, not between pitches. A budget-file or policy head goes the batch's serial route, where `--pre-flight` parks a budget raise or a policy head the owner has not approved at that head under an open mandate (`Train.raise_hold`, `Train.policy_gate`); a parked one merges directly under mandate {{mandate}} (`dev/governance/roles/standing-merge.md`; `CLAUDE.md` rule 2). Between pitches, a record or autofix pull request merges by hand only behind `tools/audit/seat/record_row.py --automerge-check` (`dev/governance/rules/delivery-status-tracking.md`).
 
-(4) After each merge (`dev/governance/roles/nudge.md` steps 12 and 18): read the merge seat's `merged` report and its read-back of the issues the merge closed (`dev/governance/roles/orchestrator.md` section 4), queue `set-stage` for a roster group to the `roster-drain` row, make one #3394 comment through `tools/pr/gh_comment.py` with its read-back, and remove the finished seat's worktrees under {{seat_root}} and its scratch; the `disk` row (step 8) runs `worktree_gc.sh`.
+(4) After each merge (`dev/governance/roles/standing-merge.md`: `tools/audit/seat/postmerge.py` runs after each merge and prints what is still `OWED`): read the merge seat's `merged` report and its read-back of the issues the merge closed (`dev/governance/roles/orchestrator.md` section 4), queue `set-stage` for a roster group to the `roster-drain` row, make one #3394 comment through `tools/pr/gh_comment.py` with its read-back, and remove the finished seat's worktrees under {{seat_root}} and its scratch; the `disk` row (step 8) runs `worktree_gc.sh`.
 
 (4b) Record beat. The beat's `plan-beat` row runs `python3 tools/plan/replan.py --out {{plan_json}} --slots {{plan_slots}} --seats {{plan_seats}} {{plan_coordinator_cap}}`, then `tools/audit/seat/state_docs.py --push --mirror {{state_mirror}} --plan {{plan_json}}`, every 30 minutes, merge or none; it publishes the plan page as `PLAN.html` in the plan table's commit at the state ref and mirrors it as {{plan_page}}, republished at the same path. A `plan-beat: PLAN UNAVAILABLE` line in {{digest}}/digest.txt is the page UNAVAILABLE (the other docs are still pushed; the ref keeps the last good page): answer its reason and re-run that replan, never hand-run `plan_page.py` around the refusal; a `plan-beat: REFUSED` line is the docs push's own refusal. A `plan-beat: PLAN MOVED` line is a page that changed since the last beat: republish it at {{plan_page}} this sweep (owner ruling, 2026-11-06: every sweep updates the plan artifact). The beat's `gantt` row compares that plan with the Gantt baseline through `tools/audit/seat/sweep_gantt.py`: it reads the roster at {{gantt_roster}}, the fire ledger {{fire_ledger}} and the acks file {{gantt_acks}}; each `GANTT-SLIP` line of {{digest}}/digest.txt is owed `act`, `defer` or `accept`, appended to {{gantt_acks}} (owner ruling, 2026-11-01). The beat's `scorecard` row runs `python3 tools/audit/seat/scorecard.py report {{sweep_record}}` (its other arguments are the beat's own), report-only; K prints unread when no sweep record is given.
 
@@ -82,7 +82,7 @@ ORCHESTRATOR SWEEP, round {{round}}, repository {{repo}}. Read {{seat_ledger}} f
 
 (5b) Outside intake. The beat's `outside-intake` row runs `tools/audit/seat/outside_intake.py list --since {{intake_since}}` with its cursor and writes its `OUTSIDE` lines to {{digest}}/digest.txt (`dev/governance/roles/orchestrator.md` section 5): an `owed=triage` line gets a triage or design seat this sweep and ends wired into a roster group through the `roster-drain` queue, with that group's `source` set by a queued `set-source <GROUP> outside` (the plan's top tier reads it), or refused with `outside_intake.py refuse`; an `owed=answer` line is queued to the dispatch seat, which runs `outside_intake.py answer`; an `owed=reply` line is read and answered; `OUTSIDE plan-page UNAVAILABLE` is the public plan page not answering (the `plan-beat` row's Pages dispatch, `tools/audit/seat/plan_public.py`).
 
-(6) Verdicts and CI. Read any moved `review/*` or `probe/*` refs and the cloud runs; queue each verdict's confirmation at its exact head to the dispatch seat (its relay runs `bus.sh confirm`) and read its report (`dev/governance/roles/nudge.md` step 1). A red required check at an open head goes back to its fixer with the line `tools/audit/seat/failure_logs.sh` prints (`dev/governance/roles/nudge.md` steps 4 and 15).
+(6) Verdicts and CI. Read any moved `review/*` or `probe/*` refs and the cloud runs; queue each verdict's confirmation at its exact head to the dispatch seat (its relay runs `bus.sh confirm`) and read its report (`dev/governance/roles/standing-dispatch.md`). A red required check at an open head goes back to its fixer with the line `tools/audit/seat/failure_logs.sh` prints, unless `tools/audit/seat/merge_train.py classify <head> --pr <N>` reads it WAIT, a gate deferral (the required set is ruleset `main-protect-checks`, re-read each sweep; pending is not a pass).
 
 (7) Proposals. A process, tooling or instrument proposal this sweep met (a seat's result, a verdict's optimisation note, your own) is sent to triage on `dev/governance/roles/proposal-triage.md`, never implemented or routed before its ruling; an ACCEPT reaches the roster through the roster seat, citing its ruling.
 
diff --git a/tools/audit/seat/update_pr.sh b/tools/audit/seat/update_pr.sh
index bd00868f07..e6bc7b8513 100755
--- a/tools/audit/seat/update_pr.sh
+++ b/tools/audit/seat/update_pr.sh
@@ -81,7 +81,7 @@ NOTE=""
 if [ "$C" != "-" ]; then $G merge -q --no-edit $C; NOTE="merges the authored code head \`$C\`"; fi
 OLD=$(git rev-parse HEAD)
 # Ruling R4 (Lean flow K12): origin/main is merged only when the pull request is DIRTY or the merge
-# would conflict; a clean head is not moved to absorb main (fixer.md step 6, nudge.md step 9). An
+# would conflict; a clean head is not moved to absorb main (fixer.md step 6, orchestrator.md section 6). An
 # unread merge state is not DIRTY: the merge-tree reading below is the local proof either way.
 ST=$(gh pr view "$N" -R $R --json mergeStateStatus -q .mergeStateStatus 2>/dev/null) || ST=unread
 MAIN=""
diff --git a/tools/ci/selftest_closures.json b/tools/ci/selftest_closures.json
index f5a326bae7..70a75c9568 100644
--- a/tools/ci/selftest_closures.json
+++ b/tools/ci/selftest_closures.json
@@ -4149,7 +4149,6 @@
     "dev/governance/roles/fix-review.md",
     "dev/governance/roles/fixer.md",
     "dev/governance/roles/judge.md",
-    "dev/governance/roles/nudge.md",
     "dev/governance/roles/orchestrator.md",
     "dev/governance/roles/root-cause.md",
     "dev/governance/roles/verifier.md",
@@ -6011,7 +6010,6 @@
   "post-merge-bookkeeping": {
    "run_sha": "7f9730626bce97831ee61c879e8b929c037930447bf2bd8c202bbac5e13ade99",
    "files": [
-    "dev/governance/roles/nudge.md",
     "tests/layout.py",
     "tools/audit/seat/postmerge.py",
     "tools/audit/seat/record_beat.py",
@@ -8385,7 +8383,6 @@
     ".",
     "CLAUDE.md",
     "dev/audit/rca/R10-RCA-OWED-UNACTIONED.md",
-    "dev/governance/roles/nudge.md",
     "dev/governance/roles/orchestrator.md",
     "dev/governance/roles/proposal-triage.md",
     "dev/governance/roles/standing-dispatch.md",
diff --git a/tools/policy/budget_raise_gate.py b/tools/policy/budget_raise_gate.py
index c871a99934..bf6f69f739 100644
--- a/tools/policy/budget_raise_gate.py
+++ b/tools/policy/budget_raise_gate.py
@@ -238,6 +238,7 @@ SCHEMA: dict[str, list[tuple[tuple[str, ...], str]]] = {
         (("roles", "*", "cap"), MAX),
         (("roles", "*", "opens"), SUPERSET),
         (("files", "*"), CAPFILE),
+        (("files_tokens", "*"), CAPFILE),
     ],
     # The machinery ratchet (tools/audit/machinery_ratchet.py,
     # R10-MACHINERY-RATCHETS): both caps and both bands are caps; the window
@@ -865,6 +866,16 @@ def self_test() -> int:
                  head_has=lambda f: f != "old.md"), False)
     check("policy: a per-file cap up is a raise",
           raised(P, p0, {**p0, "files": {"CLAUDE.md": 212, "old.md": 10}}), True)
+    # files_tokens is the per-file token cap beside `files`' line cap, so it
+    # grades alike: with no rule it fell to `frozen` and even a deleted file's
+    # token cap dropped read as a raise.
+    tk0 = {**p0, "files_tokens": {"CLAUDE.md": 3605, "old.md": 120}}
+    check("policy: a deleted file's token cap dropped, a token cap down, are routine",
+          raised(P, tk0, {**tk0, "files_tokens": {"CLAUDE.md": 3600}}, head_has=lambda f: f != "old.md"), False)
+    check("policy: a per-file token cap up is a raise",
+          raised(P, tk0, {**tk0, "files_tokens": {"CLAUDE.md": 3606, "old.md": 120}}), True)
+    check("policy: a token cap removed while its file is in the tree is a raise",
+          raised(P, tk0, {**tk0, "files_tokens": {"CLAUDE.md": 3605}}), True)
     check("policy: the band widened is a raise", raised(P, p0, {**p0, "_band": 600}), True)
     check("policy: a role's sample narrowed is a raise",
           raised(P, p0, {**p0, "roles": {"fixer": {"opens": ["a"], "cap": 5852}}}), True)
diff --git a/tools/pr/prepr.sh b/tools/pr/prepr.sh
index e0ffdff44d..ecc27bcb90 100755
--- a/tools/pr/prepr.sh
+++ b/tools/pr/prepr.sh
@@ -4253,7 +4253,7 @@ say ok "gate priority" "$HPO_GATE_PRIORITY (env, .gate-priority, then the critic
 # --- 1b. the heavy-slot lease (R10-PREPR-CAP, #2267).
 # WHY THIS EXISTS. This run is the heavy thing a seat starts most often, and its
 # steps -- the `--self-test` in 3h, the mutants drive, the closure recordings --
-# are minutes of CPU each. nudge.md §8's cap of four was advisory: the tick
+# are minutes of CPU each. The orchestrator's cap of four was advisory: the tick
 # counted and flagged it and nothing blocked a fifth, so on 2026-10-14 ten ran
 # at once and load1 reached 168 on 8 cores. `tests/gate_lock.py`'s pool is that
 # cap made mechanical (four slots, FIFO, expiry and orphan-steal shared with

## Before you return the verdict (P275)
Run `python3 -I tools/audit/carry_audit.py check --body <PR body file> --comments <file holding [{"id": 0, "body": <verdict.md text>}]>`. Give every reported item its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>`;
an evidence line flagged by its wording takes `Carry: dismissed: evidence, not a finding`. Return the verdict only at rc 0.
