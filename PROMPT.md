CLOUD FIXER seat for tvofi/heatpump_optimizer, topic r10-prepr-residue-p2, at head 50373173d486faf394b24637c177ab38b691b394. Never send push notifications. Write no Claude Code footer, no Co-Authored-By or Claude-Session trailer and no claude.ai session link in any commit, pull-request body or comment you produce; check your commits with `git log --format=%B` before pushing.
Setup: `git fetch --unshallow --tags origin`. Before any commit, pin the seat identity: `git config user.name hpo-fixer && git config user.email 70032254+tvofi@users.noreply.github.com`. The session-start `toolchain:` line says whether venv-ci's python3 is on PATH: on REFUSE, start each Bash call with `eval "$(bash .claude/hooks/session-start.sh --env-lines)"`. Then run `bash tools/audit/seat/cloud-setup.sh --check`, and on REFUSE stop: report its line as your result and start no work. Run anything heavy in the background with Monitor and no timeout. Never wait in one tool call longer than 240 s; poll again instead. Read your policy once, verbatim: `python3 -I tools/policy/role_pack.py render fixer --out $HOME/role-pack.md`, then that file in place of your role contract and INSTRUMENTS.md; on REFUSE read those files as before.
Role: read dev/governance/roles/fixer.md from main, and follow it exactly, in a worktree of your own cut from origin/main. Fetch 50373173d486faf394b24637c177ab38b691b394 for the base you were given.
Output: push each verified step, fast-forward only, to refs/heads/handoff-wip/r10-prepr-residue-p2 before any wait on a background run, so an idle container loses nothing; never step-push to handoff/r10-prepr-residue-p2, whose move updates the pull request. Hand off at your first clean `tools/pr/prepr.sh` head (the body check included), fixing what it refuses; a main that has moved since that run needs no re-merge and no second run, because the train re-proves the head on the current main. Merge origin/main and rerun prepr.sh only when `git merge-tree --write-tree origin/main HEAD` reports a conflict. If you must stop on a question, first push `BLOCKED.md` with a `Question:` line to refs/heads/handoff-wip/r10-prepr-residue-p2, even with no code. Then push the code to refs/heads/handoff/r10-prepr-residue-p2, then write the PR body and run `bash tools/audit/seat/body_push.sh r10-prepr-residue-p2 <body.md>`, which pushes refs/heads/handoff-body/r10-prepr-residue-p2; that second push is the return signal. Once it succeeds, delete the step ref: `git push origin :refs/heads/handoff-wip/r10-prepr-residue-p2`. When body_push.sh exits 4 (its output ends `body_push: REFUSED CARRY-LANDED`), the carry lands on the roster you may not write: push a BLOCKED.md holding that output to refs/heads/handoff-wip/r10-prepr-residue-p2 and stop; the relay folds the carries and re-runs body_push.sh. Push nothing else, open no pull request and write no delivery row. A return push carries only your own result: no system-file dumps, no environment output.
A red is owed a `## Red checks` answer, and may block, only when its name is in the set `python3 tools/audit/seat/merge_train.py owed-reds` prints (defect-root-cause.md); any other red is neither answered nor a block.
Never write to any branch except your return refs and refs/heads/handoff-wip/r10-prepr-residue-p2 and refs/heads/handoff-wip/r10-prepr-residue-p2-body. Never work around a hook or a refusal; report it in your result instead.
Discovery reads (search, list, read across files) go through Agent subagents, as the frugal routing guard requires: when it refuses inline work, dispatch a haiku or sonnet Agent subagent to do it rather than bypassing the guard; never set FRUGAL_ALLOW_INLINE and never edit .claude/settings.json.

Brief (snapshotted when this payload was rendered):
# Repair round: PR 3547 (R10-PREPR-RESIDUE part 2), mutation-vacuous, third block

Resume from handoff/r10-prepr-residue-p2 (PR head 2a1a7de05b0c080029817dd4208864c5ef7e9f6a). Read the verdict in full first: `git show origin/verdict/3547:VERDICT.md`. This is the same class a third time, so read the two earlier verdicts on that ref as well and answer the cause, not the instance.

Three survivors, each to be KILLED by a self-test arm (a survivor is answered by a test, not by prose; an equivalent mutant needs a `survivor_triage` record with the reason it cannot change behaviour):
1. P13-main-uses-inline-receipt-line: replacing the call to the code-steps line helper in prepr.sh s main path with the old inline receipt line leaves `prepr.sh --self-test` at 550 passed. Add the arm that drives the main path and reads the receipt line it prints.
2. G6-cli-ignores-ref: changing gate_priority.py s CLI to pass no ref leaves its self-test at 21 checks green. Add an arm that runs the CLI with a ref and asserts the ref was used.
3. P12-codesteps-drops-scoped-test: the helper is unchanged since round 2 and no self-test row passes the hotfix caller value. Add that row.
Then run the reviewer s three mutants yourself (the diffs are in the verdict s evidence) plus `python3 tools/audit/seat/mutant_run.py --diff <merge-base>...HEAD` with each self-test as the command, and list every survivor that remains in the body with its answer; none may be left unnamed (one block must list every survivor found). Failing arm first, then the fix where the arm exposes a real defect. Hotfix-scoped prepr, body updated (each verdict item answered, all `Carry N` lines kept), body_push.sh. Merge origin/main only if merge-tree conflicts.

This part: Carries 21 (0-based roster index, text verbatim below).

Carry 0: Moved from R10-PREPR-CAP carry 12 (0-based) by the carries-open audit (orchestrator s13, 2026-11-09); its own pull request merged and nothing dispatched this carry. Text verbatim:

STRANDED CARRY 19 (carry-strand audit, orchestrator s9, 2026-10-31)

Source: group R10-FLOW-JIDOKA, index 10; triage id: P-N; roster ref origin/handoff/audit-r10-roster abb47a06cd190e49c9d9da264ea3fab2a71f890d.
Owner-ordered: no.

Why stranded: #2853 Forward-carry: "Carries 11, 12 and 14, the --body-check parity extensions ... plus one grammar owner for ## Forward-carry. Not built".

Fold into: R10-PREPR-CAP (live). Owner of tools/pr/prepr.sh among live groups (the only other is R10-FLY-NO-FOOTERS); PR #3051 is open, so this rides its next PR, not #3051.

Original text, verbatim:
P-N (triage batch 6): extend prepr.sh --body-check (what body_push.sh runs) so a return is refused for the classes open_pr's prepr still refuses it for: (a) run the agreement lane (agreement_py.py, local git only); (b) feed step 6d's unpinned-site list (ci_predict output body_push already holds) to the step-7d '## Unpinned sites' disposal check; (c) predict 'budget-raise-gate not named in ## Red checks' from the diff touching *_budgets.json. Failing fixture first per class, each with a null control (clean head passes, disposed sites pass). Do NOT run full prepr in body_push (M1 rejected in its header). Measure each refusal's base SHA first: a fixer cut before 2fe11ffbc is not a gap. Instances 2026-10-23: ORCH-LEDGER (agreement, 3 unregistered), INPUT-STALENESS (10 unpinned), #2620 r5 (budget-raise-gate unnamed).

Carry: R10-PREPR-CAP [dismissed: moved to round 11: R10-ROUND-PLAYBOOK-FINAL round-11 opening list carry of 2026-11-12]

Carry 1: Moved from R10-PREPR-CAP carry 13 (0-based) by the carries-open audit (orchestrator s13, 2026-11-09); its own pull request merged and nothing dispatched this carry. Text verbatim:

STRANDED CARRY 20 (carry-strand audit, orchestrator s9, 2026-10-31)

Source: group R10-FLOW-JIDOKA, index 13; triage id: none; roster ref origin/handoff/audit-r10-roster abb47a06cd190e49c9d9da264ea3fab2a71f890d.
Owner-ordered: no.

Why stranded: #2853 Forward-carry: "Carries 11, 12 and 14, the --body-check parity extensions ... plus one grammar owner for ## Forward-carry. Not built".

Fold into: R10-PREPR-CAP (live). Owner of tools/pr/prepr.sh among live groups (the only other is R10-FLY-NO-FOOTERS); PR #3051 is open, so this rides its next PR, not #3051.

Original text, verbatim:
RCA R10-RCA-BODY-CHECK-PARITY (handoff-body/r10-rca-body-check-parity 4fd3eef16, state (c), cost test: build). Two programs grade ## Forward-carry with different grammars (policy_lint.mjs isNone accepts `none` + prose; carry_audit.py NONE_ITEM accepts only bare `none` or `n/a: <reason>`, and a path after `Carry:` reads as unrouted), and only one runs before a PR opens. A name-level parity test over pr-contract.yml is necessary but not sufficient: the pre-open twin must run carry_audit's grammar with CI's inputs. Read section 4 of that body for the three requirements this fixer owes.

Carry: R10-PREPR-CAP [dismissed: moved to round 11: R10-ROUND-PLAYBOOK-FINAL round-11 opening list carry of 2026-11-12]

Carry 2: Moved from R10-PREPR-CAP carry 14 (0-based) by the carries-open audit (orchestrator s13, 2026-11-09); its own pull request merged and nothing dispatched this carry. Text verbatim:

STRANDED CARRY 21 (carry-strand audit, orchestrator s9, 2026-10-31)

Source: group R10-FLOW-JIDOKA, index 14; triage id: none; roster ref origin/handoff/audit-r10-roster abb47a06cd190e49c9d9da264ea3fab2a71f890d.
Owner-ordered: no.

Why stranded: #2853 Forward-carry: "Carries 15 and 21 ... Partly answered ... the rest of both jobs is not modelled".

Fold into: R10-PREPR-CAP (live). Owner of tools/pr/prepr.sh among live groups (the only other is R10-FLY-NO-FOOTERS); PR #3051 is open, so this rides its next PR, not #3051.

Original text, verbatim:
From #2639 (body, item 056ddbd0), routed by routing audit 1 (2026-10-24): its destination R10-FLY-GH-READ-RETRY is done and did not implement it (`git grep instrument-self-tests origin/main -- tools/pr/ci_predict.py` is empty). **Root cause for the instrument-self-tests red** (`defect-root-cause.md`'s red-check trigger): `instrument-self-tests` turned this PR red on three instruments that copy or enumerate tracked files the diff adds. `prepr.sh` can run them, and its `ci predict` step does not model them. The cost test's inputs: about 6 minutes (377 s measured) per handoff to run the job locally, against one red PR cycle.

Carry: R10-PREPR-CAP [dismissed: moved to round 11: R10-ROUND-PLAYBOOK-FINAL round-11 opening list carry of 2026-11-12]

Carry 3: Moved from R10-PREPR-CAP carry 20 (0-based) by the carries-open audit (orchestrator s13, 2026-11-09); its own pull request merged and nothing dispatched this carry. Text verbatim:

STRANDED CARRY 27 (carry-strand audit, orchestrator s9, 2026-10-31)

Source: group R10-FLOW-JIDOKA, index 26; triage id: none; roster ref origin/handoff/audit-r10-roster abb47a06cd190e49c9d9da264ea3fab2a71f890d.
Owner-ordered: no.

Why stranded: #2853 Forward-carry: "The round-1 census's HEAD-ONLY class needs a predicting detector. Not built".

Fold into: R10-PREPR-CAP (live). Owner of tools/pr/prepr.sh among live groups (the only other is R10-FLY-NO-FOOTERS); PR #3051 is open, so this rides its next PR, not #3051.

Original text, verbatim:
From R10-FLOW-JIDOKA (#2838): the round-1 census's HEAD-ONLY class needs a predicting detector, not a reading one; step 7c can only read reds on commits already pushed.

Carry: R10-PREPR-CAP [dismissed: moved to round 11: R10-ROUND-PLAYBOOK-FINAL round-11 opening list carry of 2026-11-12]

Carry 4: Moved from R10-PREPR-CAP carry 21 (0-based) by the carries-open audit (orchestrator s13, 2026-11-09); its own pull request merged and nothing dispatched this carry. Text verbatim:

STRANDED CARRY 28 (carry-strand audit, orchestrator s9, 2026-10-31)

Source: group R10-FLOW-JIDOKA, index 27; triage id: none; roster ref origin/handoff/audit-r10-roster abb47a06cd190e49c9d9da264ea3fab2a71f890d.
Owner-ordered: no.

Why stranded: .gitignore config/ trap: neither JIDOKA PR names it; no live carry.

Fold into: R10-PREPR-CAP (live). Owner of tools/pr/prepr.sh among live groups (the only other is R10-FLY-NO-FOOTERS); PR #3051 is open, so this rides its next PR, not #3051.

Original text, verbatim:
From r10-buffer-store (code head 208ab9a54, R10-BUFFER-STORE): .gitignore:28 ignores config/ at any depth, so git add of a TRACKED config file (dev/audit/config/, dev/governance/config/) prints 'The following paths are ignored' and exits 1 while still staging the file, and git add -A silently skips new files there. Both nested config/ directories are tracked and visible to git check-ignore, so the rule is anchored wrong for a repository with policy config directories: a handoff can silently omit a new tracked config file. Anchor the rule (e.g. /config/) or add the exception, with a control that git check-ignore still ignores a root-level config/.

Carry: R10-PREPR-CAP [implemented: 6e100ef6980216a81eaa0438bdc215d62b19271f]

Carry 5: Moved from R10-PREPR-CAP carry 28 (0-based) by the carries-open audit (orchestrator s13, 2026-11-09); its own pull request merged and nothing dispatched this carry. Text verbatim:

From r10-rca-ci-critpath-3, body item ce268b05: `prepr.sh` should run `harness_headers.inline_scan()`, or at least `depth_root_seams()`, and leave only the timed parts of `harness_headers.py` to CI, so a branch adding a harness under `dev/audit/` cannot reach CI red on a static, sub-second check. Lands in the prepr/gate group R10-PREPR-CAP (`tools/pr/prepr.sh`). Carry: R10-PREPR-CAP (items ce268b05) [moved: R11-INTAKE-R10-RESIDUE]

Carry 6: Moved from R10-PREPR-CAP carry 30 (0-based) by the carries-open audit (orchestrator s13, 2026-11-09); its own pull request merged and nothing dispatched this carry. Text verbatim:

From triage batch 137 (triage: dev/programme/triage/s6-batch137.md#P454), queue line PREPR-SLOT-LIVELOCK, major (11-08 04:44Z: four outer preprs held all four heavy slots, each waiting on its step-3h nested self-test prepr; the critical path stalled 11+ min; second instance after 10-27). tests/gate_lock.py's HPO_SLOT_LABEL already lets a nested heavy step join its caller's slot and prepr.sh exports it, so find where step 3h's nested run loses the label and keep it. Do not add a second marker (HPO_GATE_SLOT_HELD is rejected as a duplicate). Failing test first: an outer prepr holding a slot runs its --self-test nested prepr with every slot taken and completes. Null control: a bare nested run with no label still takes a slot. [dismissed: dismissed in the body of pull request 3479]

Carry 7: Moved from R10-FLY-CIPREDICT-RESTORING carry 4 (0-based) by the carries-open audit (orchestrator s13, 2026-11-09); its own pull request merged and nothing dispatched this carry. Text verbatim:

From this pull request, body item 9615f50a: `tools/pr/ci_predict.py` mislabels an in-process top-level import of an INERT file as INERT READS (the `inert_siblings` arm, with no UNDER-SCOPED prediction from the import arm) and prescribes `--apply-inert`, which cannot clear CI's UNDER-SCOPED; evidence: `## Red checks` above, `tests / closures` on this PR at `a9827ca3e`. Carry: R10-FLY-CIPREDICT-RESTORING (items 9615f50a) [dismissed: moved to round 11: R10-ROUND-PLAYBOOK-FINAL round-11 opening list carry of 2026-11-12]

Carry 8: From r10-rca-open-prepr-slow, body item dfceecd3: body_push.sh carries a receipt from the parent body tip or onto a descendant code head, and app_push.sh reuse_verdict re-proves it. Carry: R10-PREPR-RESIDUE (items dfceecd3) [dismissed: superseded by carries 14 to 17 (carry 19)]

Carry 9: From r10-rca-open-prepr-slow, body item 70f46ea9: body_push.sh's no-trailer line names which receipt condition failed. Carry: R10-PREPR-RESIDUE (items 70f46ea9) [dismissed: superseded by carries 14 to 17 (carry 19)]

Carry 10: From r10-rca-open-prepr-slow, body item ddee73ac: prepr.sh step lines and the PRE-PR line carry elapsed seconds. Carry: R10-PREPR-RESIDUE (items ddee73ac) [dismissed: superseded by carries 14 to 17 (carry 19)]

Carry 11: From r10-rca-open-prepr-slow, body item 8eec61f0: Step 6d: measure per-arm and per-grader wall time on 6671786843 and correct the seconds premise. Leave to CI the grader replays instrument-self-tests already runs, and keep SELF-TEST READS. Carry: R10-PREPR-RESIDUE (items 8eec61f0) [dismissed: superseded by carries 14 to 17 (carry 19)]

Carry 12: From #3401 (r10-hotfix-train-policy-mandate), body item fd81bbe9: ci_predict does not run the `run_always` `tests/harness_headers.py` over a new or changed `dev/audit/harnesses/*.py`. So a harness whose inlined `repo_root` drifts from `tools/audit/repo_root.py` passes prepr step 6d and `body_push.sh`'s predictor, and turns `tests / fast` red in CI (this PR, at f0b75645). Carry: R10-PREPR-RESIDUE (items fd81bbe9) [dismissed: duplicate of carry 20 kept bare; P548 roster_sync re-append]

Carry 13: From the orchestrator (2026-11-10, #3401 cloud receipt round): tools/pr/ci_predict.py's pr-contract carry arm, run in a clone that lacks origin/handoff/audit-r10-roster, grades every roster-branch-only destination as a bad destination (CARRY-AUDIT 0 routed, 3 bad), because roster_lib.default_roster_ref falls back to origin/main. With that ref fetched, the same body reads 3 routed. Control: carry_audit.py check on #3401's body d2714e74 at origin/main with and without the roster ref. Fix shape: when the round's roster branch exists on origin but not locally, fetch it or report UNREADABLE, never bad-destination. [dismissed: moved to round 11: R10-ROUND-PLAYBOOK-FINAL round-11 opening list carry of 2026-11-12]

Carry 14: From 3411, body item 41176b97: C1, from `dev/audit/rca/R10-RCA-OPEN-PREPR-SLOW.md` section 6: - Change: `tools/audit/seat/body_push.sh` `prepr_trailer` takes the receipt from the local `hpo-prepr-receipt`, else from the parent body tip's one `Prepr:` trailer. It writes the receipt when the receipt's sha is an ancestor of the code head and its tree is that sha's tree. - Failing cases: a re-push from a second clone keeps the trailer. A clean merge of main past the receipt keeps it, and `reuse_verdict` returns rc 0. - Null controls, both preconditions: a non-merge commit past the receipt keeps the trailer and `reuse_verdict` returns rc 1, so a carried receipt never skips prepr on unproved code. A receipt on a non-ancestor writes no trailer. - Re-measure the reach with `dev/audit/rca/open_prepr_receipts.py tips` over your own window. It was 7 tips in 4.146 days at origin/main 5d09dedf69eb. - Carry: R10-PREPR-RESIDUE (items 41176b97) [moved: R11-INTAKE-R10-RESIDUE]

Carry 15: From 3411, body item 300fa7f0: C2, from `dev/audit/rca/R10-RCA-OPEN-PREPR-SLOW.md` section 6: - Change: `tools/audit/seat/body_push.sh` names, both in its no-trailer line and in a `Prepr-absent: <reason>` trailer on the body commit, which condition failed: no receipt file in this checkout; a receipt not an ancestor of the code head; a receipt whose tree is not its sha's; or no trailer on the parent tip. - Failing case: each of the four, planted, prints and writes its own reason. Before the fix, all four print one line. - Null control: a valid receipt writes `Prepr:` and no `Prepr-absent:`. - Carry: R10-PREPR-RESIDUE (items 300fa7f0) [moved: R11-INTAKE-R10-RESIDUE]

Carry 16: From 3411, body item fab9d1da: C3, from `dev/audit/rca/R10-RCA-OPEN-PREPR-SLOW.md` section 6: - Change: `tools/pr/prepr.sh`'s step lines carry the step's elapsed seconds from bash's `$SECONDS`, with no spawn, and the final `PRE-PR:` line carries the run's. - Failing case: a step stubbed to sleep 2 s prints an elapsed of at least 2. Before the fix there is no field. - Null control: a no-op step prints 0 or 1, so the field times the step and not the run. - Carry: R10-PREPR-RESIDUE (items fab9d1da) [moved: R11-INTAKE-R10-RESIDUE]

Carry 17: From 3411, body item e0b30357: C4, from `dev/audit/rca/R10-RCA-OPEN-PREPR-SLOW.md` section 6: - Problem: the comment over `predict_line` in `tools/pr/prepr.sh` says step 6d "costs seconds". `bash dev/audit/rca/open_prepr_6d.sh 6671786843` measured 1561 s on a 4-CPU cloud container, against 40 s at the scoped `c19017d6`. - Change: correct the premise, and bound or leave to CI the GRADER replays that `instrument-self-tests` already runs, keeping SELF-TEST READS. - Proof: `open_prepr_6d.sh 6671786843` before and after on one host, with wall time down and `predict_sha1` unchanged (zero PREDICT lines, sha1 da39a3ee5e6b4b0d3255bfef95601890afd80709). At `c19017d6`, `predict_sha1` stays e880deb19085147bd6a6386916845596284cb9a1. - Carry: R10-PREPR-RESIDUE (items e0b30357) [moved: R11-INTAKE-R10-RESIDUE]

Carry 18: From 3411, body item d1d75b8f: Reviewer follow-up, the "never" tips (48 in this snapshot, 49 in round 1's): their process state is not established, and the triggering instances are explained by C-B alone until C2 lands. After C2, extend `dev/audit/rca/open_prepr_receipts.py` to split `never` by the `Prepr-absent:` trailer, and re-take the state per reason. Null control: a tip carrying `Prepr:` is never counted in `never`. Carry: R10-PREPR-RESIDUE (items d1d75b8f) [dismissed: moved to round 11: R10-ROUND-PLAYBOOK-FINAL round-11 opening list carry of 2026-11-12]

Carry 19: From 3411, body item 88c4f531: finding-propagation.md: unenforced: `tools/audit/carry_audit.py` `landed` printed `CARRY-LANDED: 0 missing` for this body because R10-PREPR-RESIDUE's carries 8 to 11 already name this topic as their source, although they still hold round 1's text without controls. It matches on the source, not the text. The orchestrator owes these roster ops on `handoff/audit-r10-roster`: replace carries 8 to 11 with the C1 to C4 items above, append the "never" follow-up, and set the group's `rca` to `R10-RCA-OPEN-PREPR-SLOW`. Carry: R10-PREPR-RESIDUE (items 88c4f531) [dismissed: an instruction to replace carries 8 to 11, done]

Carry 20: ci_predict does not run the `run_always` `tests/harness_headers.py` over a new or changed `dev/audit/harnesses/*.py`. So a harness whose inlined `repo_root` drifts from `tools/audit/repo_root.py` passes prepr step 6d and `body_push.sh`'s predictor, and turns `tests / fast` red in CI (this PR, at f0b75645). Carry: R10-PREPR-RESIDUE [moved: R11-INTAKE-R10-RESIDUE]

Carry 21: PART 2 ITEM unless the R10-PREPR-RESIDUE fixer dispatched 2026-11-11 00:24-00:28Z has not yet handed off when this carry lands: that fixer's brief was rendered before this carry, so a fixer already past handoff leaves it to the group's next part.
From triage batch 141 (triage: dev/programme/triage/s6-batch141.md#P526 at aac4c4a441), queue line HOTFIX-PREPR-SCOPED, owner-directive route (tvofi 2026-11-09, verbatim: "hotfixes should have aggressively scoped or no prepr"). Measured: the main de.json hotfix spent about 40 min in a full prepr while 7 PRs waited. Decide the scope once, in tools/pr/prepr.sh: on a topic named fix/r10-hotfix-* (the branch every hotfix group uses), prepr defaults to PREPR_SKIP_CODE=1 PREPR_SKIP_CLOSURES=1, keeps the merged-tree structure ratchet and the body/contract checks, and prints one line naming the hotfix scope; an explicit caller value still wins. The opener and the fixer prompt then need no edit. Self-test: a hotfix topic runs scoped and prints the line; the null control, a non-hotfix topic, runs the full prepr as today; a mutant on the topic predicate.

Carry 22: PART 2 ITEM unless the R10-PREPR-RESIDUE fixer dispatched 2026-11-11 00:41Z has not yet handed off when this carry lands: that fixer's brief was rendered before this carry, so a fixer already past handoff leaves it to the group's next part.
From triage batch 148 (triage: dev/programme/triage/s6-batch148.md#P557 at a515e249d5), queue line S14-BODY-PUSH-LANDED-MAIN-ONLY, a repair of an observed wrong behaviour. tools/audit/seat/body_push.sh lines 182-184 (CARRY 11, P287) state that a body carry its group does not yet hold 'on main's roster or the round's branch' is refused, but line 187 runs carry_audit.py --roster-ref origin/main landed, and bus.sh does the same at lines 236, 241 and 256; cloud_dispatch renders briefs from the round branch, so a carry added since the last roster landing on main is refused CARRY-LANDED (exit 4) and the relay's carry-fold folds 0 items and re-fails every pass. Source's figures: 3 of 4 returned fixers blocked with no PR (plan-page 4143bf92, tick a5ff6af4, train e3fd6216 x3); at the round ref plan-page reads 0 missing. Fix: tools/audit/carry_audit.py landed counts a carry landed when its group holds it on main's roster OR on the round branch (the ref roster_lib.default_roster_ref names when the clone has it); body_push.sh and bus.sh drop the hard-coded --roster-ref origin/main so one rule serves both. Self-test: a carry on the round branch only passes; on main only passes; null control: on neither is refused exit 4; a mutant on each arm of the or. [moved: R10-CARRY-AUDIT-P5]

Carry 23: PART 2 ITEM unless the R10-PREPR-RESIDUE fixer dispatched 2026-11-11 00:41Z has not yet handed off when this carry lands: that fixer's brief was rendered before this carry, so a fixer already past handoff leaves it to the group's next part.
From triage batch 152 (triage: dev/programme/triage/s6-batch152.md#P563 at 8d9dc31d9b), queue line S14-LANDED-PR-NEEDS-ROSTER-PR, a repair of an observed wrong behaviour. bus.sh carry_landed (line 229 at 63bcdcaad8) runs carry_audit.py landed and land-ops with only --pr "#$1" (line 237), and carry_audit own_group (line 587) skips every '#'-prefixed source (line 593), so a dispatch never resolves the PR's own group: a fresh PR whose body carries a status line on its own group's carries is refused CARRY-MISSING at its first reviewer dispatch. Measured on PR 3424's body (head fix/r10-train-residue 175556657a) at origin/handoff/audit-r10-roster: --pr '#3424' rc 1, 3 missing; --pr '#3424' --topic fix/r10-train-residue rc 0, 0 missing (3 CARRY-STATUS). carry_audit never reads resume.pr, so running roster_sync after open would change nothing. Fix: carry_landed reads .head.ref in its existing gh api pulls/$1 call and passes it as --topic to landed and land-ops, so own_group resolves by pr_group_of (group_for_branch, then without a trailing -pr), as audit --branch does (line 980). Lands beside P557 (s6-batch148.md#P557) in the same carry_landed call, which replaces its hard-coded --roster-ref origin/main. Self-test: the 3424 shape (--pr plus head ref, own-group status line) passes at the round ref; null control: a finding routed to another group that does not hold it is still CARRY-MISSING; a mutant dropping --topic fails the first case. [moved: R10-CARRY-AUDIT-P5]

Carry 24: GATE-LOCK-PRIORITY-ENV-LEAK (triage: dev/programme/triage/s6-batch220.md#P673 at 924a4de8ed), line numbers at 61afd4f2db. tools/pr/prepr.sh :4159-4161 exports HPO_GATE_PRIORITY, and in tests/gate_lock.py `_priority_cases` the `normal` waiter of the two ordering arms (:1628, :1738) enters `take` with no `_Env(None)`, so it inherits the caller's priority. Measured on main: `_priority_cases(g)` fails 2 of 14 ("an urgent waiter takes before an older normal one", "the heavy-slot pool orders by the same rule") with HPO_GATE_PRIORITY=2, so prepr on any hotfix branch is red; it fails 0 of 14 when the variable is unset or 1. Repair: wrap both `normal` waiter starts in `with _Env(None):` (the diff is in archive/handoff-wip/r10-hotfix-restore-base-skew.69b3c17f3701 BLOCKED.md, lines 16-53). Demonstration: both arms fail with HPO_GATE_PRIORITY=2 exported on the base and pass on the fix. Null control: with the variable unset, both pass on base and fix. [moved: R10-PROCESS-SLIM]

Carry 25: R10-PREPR-RESIDUE (triage: dev/programme/triage/s6-batch230.md#P698 at 2ced371c1a), line numbers at 2ced371c1a. tools/pr/ci_predict.py:666-692 `ci_tree_run` clones the checkout with tests/throwaway_git.py:151 `throwaway_git_clone` (plain `git clone --shared`), so the clone's refs/remotes/origin/* are the checkout's LOCAL refs/heads/*; only origin/main is reset to `tip`. A stale local handoff/audit-r10-roster made the predictor read an old roster as origin/ and refuse body_push/open (second instance after P687). Set every origin/* the steps read from the checkout's refs/remotes/origin/* (or fetch them), never from refs/heads/*. Control: a self-test with a local head behind its origin/ twin, where a step reads the origin/ value. [moved: R11-INTAKE-R10-RESIDUE]
