CLOUD FIXER seat for tvofi/heatpump_optimizer, topic r10-prepr-residue, at head d08ed31049cd3636cde4d2fdeb3bd7cd4b3c842a. Never send push notifications. Write no Claude Code footer, no Co-Authored-By or Claude-Session trailer and no claude.ai session link in any commit, pull-request body or comment you produce; check your commits with `git log --format=%B` before pushing.
Setup: `git fetch --unshallow --tags origin`. Before any commit, pin the seat identity: `git config user.name hpo-fixer && git config user.email 70032254+tvofi@users.noreply.github.com`. The session-start `toolchain:` line says whether venv-ci's python3 is on PATH: on REFUSE, start each Bash call with `eval "$(bash .claude/hooks/session-start.sh --env-lines)"`. Then run `bash tools/audit/seat/cloud-setup.sh --check`, and on REFUSE stop: report its line as your result and start no work. Run anything heavy in the background with Monitor and no timeout. Never wait in one tool call longer than 240 s; poll again instead. Read your policy once, verbatim: `python3 -I tools/policy/role_pack.py render fixer --out $HOME/role-pack.md`, then that file in place of your role contract and INSTRUMENTS.md; on REFUSE read those files as before.
Role: read dev/governance/roles/fixer.md from main, and follow it exactly, in a worktree of your own cut from origin/main. Fetch d08ed31049cd3636cde4d2fdeb3bd7cd4b3c842a for the base you were given.
Output: push each verified step, fast-forward only, to refs/heads/handoff-wip/r10-prepr-residue before any wait on a background run, so an idle container loses nothing; never step-push to handoff/r10-prepr-residue, whose move updates the pull request. Hand off at your first clean `tools/pr/prepr.sh` head (the body check included), fixing what it refuses; a main that has moved since that run needs no re-merge and no second run, because the train re-proves the head on the current main. Merge origin/main and rerun prepr.sh only when `git merge-tree --write-tree origin/main HEAD` reports a conflict. If you must stop on a question, first push `BLOCKED.md` with a `Question:` line to refs/heads/handoff-wip/r10-prepr-residue, even with no code. Then push the code to refs/heads/handoff/r10-prepr-residue, then write the PR body and run `bash tools/audit/seat/body_push.sh r10-prepr-residue <body.md>`, which pushes refs/heads/handoff-body/r10-prepr-residue; that second push is the return signal. Once it succeeds, delete the step ref: `git push origin :refs/heads/handoff-wip/r10-prepr-residue`. When body_push.sh exits 4 (its output ends `body_push: REFUSED CARRY-LANDED`), the carry lands on the roster you may not write: push a BLOCKED.md holding that output to refs/heads/handoff-wip/r10-prepr-residue and stop; the relay folds the carries and re-runs body_push.sh. Push nothing else, open no pull request and write no delivery row. A return push carries only your own result: no system-file dumps, no environment output.
Never write to any branch except your return refs and refs/heads/handoff-wip/r10-prepr-residue and refs/heads/handoff-wip/r10-prepr-residue-body. Never work around a hook or a refusal; report it in your result instead.
Discovery reads (search, list, read across files) go through Agent subagents, as the frugal routing guard requires; at most 5 inline search operations per prompt; never set FRUGAL_ALLOW_INLINE.

Brief (snapshotted when this payload was rendered):
Residue of R10-PREPR-CAP and R10-FLY-CIPREDICT-RESTORING on one seam, the pre-open prediction in tools/pr/prepr.sh and tools/pr/ci_predict.py: body-check parity, the HEAD-ONLY predicting detector, the anchored .gitignore config rule, harness_headers inline scan, the nested-slot livelock, and the INERT-import mislabel. Each carry states its failing test and null control; measure first where the carry says so. Created by the carries-open audit (orchestrator s13, 2026-11-09) from the carries listed in its carry entries; each carry entry names its source group and index.

RULING 2026-11-11T00:40:21Z (orchestrator under mandate 6715477401) R10-PREPR-RESIDUE blocked-stop 87c3ba7353: the group is built in serial parts of at most five carries on its one seam, no new roster group. Part 1 (topic r10-prepr-residue) = carries 0,1,2,3,4, continuing handoff-wip/r10-prepr-residue 87c3ba7353 (carry 4 owes its failing test first). Part 2 (r10-prepr-residue-p2) = 5-9, part 3 = 10-14, part 4 = 15-20 (six, the last two are one-line), each dispatched at the previous part's handoff. Carry 6 (slot livelock) is built only with a planted all-slots-taken fixture reproducing it; unreproduced it is answered 'dismissed: not reproduced' with the fixture as evidence.

Carry 0:
Moved from R10-PREPR-CAP carry 12 (0-based) by the carries-open audit (orchestrator s13, 2026-11-09); its own pull request merged and nothing dispatched this carry. Text verbatim:

STRANDED CARRY 19 (carry-strand audit, orchestrator s9, 2026-10-31)

Source: group R10-FLOW-JIDOKA, index 10; triage id: P-N; roster ref origin/handoff/audit-r10-roster abb47a06cd190e49c9d9da264ea3fab2a71f890d.
Owner-ordered: no.

Why stranded: #2853 Forward-carry: "Carries 11, 12 and 14, the --body-check parity extensions ... plus one grammar owner for ## Forward-carry. Not built".

Fold into: R10-PREPR-CAP (live). Owner of tools/pr/prepr.sh among live groups (the only other is R10-FLY-NO-FOOTERS); PR #3051 is open, so this rides its next PR, not #3051.

Original text, verbatim:
P-N (triage batch 6): extend prepr.sh --body-check (what body_push.sh runs) so a return is refused for the classes open_pr's prepr still refuses it for: (a) run the agreement lane (agreement_py.py, local git only); (b) feed step 6d's unpinned-site list (ci_predict output body_push already holds) to the step-7d '## Unpinned sites' disposal check; (c) predict 'budget-raise-gate not named in ## Red checks' from the diff touching *_budgets.json. Failing fixture first per class, each with a null control (clean head passes, disposed sites pass). Do NOT run full prepr in body_push (M1 rejected in its header). Measure each refusal's base SHA first: a fixer cut before 2fe11ffbc is not a gap. Instances 2026-10-23: ORCH-LEDGER (agreement, 3 unregistered), INPUT-STALENESS (10 unpinned), #2620 r5 (budget-raise-gate unnamed).

Carry: R10-PREPR-CAP

Carry 1:
Moved from R10-PREPR-CAP carry 13 (0-based) by the carries-open audit (orchestrator s13, 2026-11-09); its own pull request merged and nothing dispatched this carry. Text verbatim:

STRANDED CARRY 20 (carry-strand audit, orchestrator s9, 2026-10-31)

Source: group R10-FLOW-JIDOKA, index 13; triage id: none; roster ref origin/handoff/audit-r10-roster abb47a06cd190e49c9d9da264ea3fab2a71f890d.
Owner-ordered: no.

Why stranded: #2853 Forward-carry: "Carries 11, 12 and 14, the --body-check parity extensions ... plus one grammar owner for ## Forward-carry. Not built".

Fold into: R10-PREPR-CAP (live). Owner of tools/pr/prepr.sh among live groups (the only other is R10-FLY-NO-FOOTERS); PR #3051 is open, so this rides its next PR, not #3051.

Original text, verbatim:
RCA R10-RCA-BODY-CHECK-PARITY (handoff-body/r10-rca-body-check-parity 4fd3eef16, state (c), cost test: build). Two programs grade ## Forward-carry with different grammars (policy_lint.mjs isNone accepts `none` + prose; carry_audit.py NONE_ITEM accepts only bare `none` or `n/a: <reason>`, and a path after `Carry:` reads as unrouted), and only one runs before a PR opens. A name-level parity test over pr-contract.yml is necessary but not sufficient: the pre-open twin must run carry_audit's grammar with CI's inputs. Read section 4 of that body for the three requirements this fixer owes.

Carry: R10-PREPR-CAP

Carry 2:
Moved from R10-PREPR-CAP carry 14 (0-based) by the carries-open audit (orchestrator s13, 2026-11-09); its own pull request merged and nothing dispatched this carry. Text verbatim:

STRANDED CARRY 21 (carry-strand audit, orchestrator s9, 2026-10-31)

Source: group R10-FLOW-JIDOKA, index 14; triage id: none; roster ref origin/handoff/audit-r10-roster abb47a06cd190e49c9d9da264ea3fab2a71f890d.
Owner-ordered: no.

Why stranded: #2853 Forward-carry: "Carries 15 and 21 ... Partly answered ... the rest of both jobs is not modelled".

Fold into: R10-PREPR-CAP (live). Owner of tools/pr/prepr.sh among live groups (the only other is R10-FLY-NO-FOOTERS); PR #3051 is open, so this rides its next PR, not #3051.

Original text, verbatim:
From #2639 (body, item 056ddbd0), routed by routing audit 1 (2026-10-24): its destination R10-FLY-GH-READ-RETRY is done and did not implement it (`git grep instrument-self-tests origin/main -- tools/pr/ci_predict.py` is empty). **Root cause for the instrument-self-tests red** (`defect-root-cause.md`'s red-check trigger): `instrument-self-tests` turned this PR red on three instruments that copy or enumerate tracked files the diff adds. `prepr.sh` can run them, and its `ci predict` step does not model them. The cost test's inputs: about 6 minutes (377 s measured) per handoff to run the job locally, against one red PR cycle.

Carry: R10-PREPR-CAP

Carry 3:
Moved from R10-PREPR-CAP carry 20 (0-based) by the carries-open audit (orchestrator s13, 2026-11-09); its own pull request merged and nothing dispatched this carry. Text verbatim:

STRANDED CARRY 27 (carry-strand audit, orchestrator s9, 2026-10-31)

Source: group R10-FLOW-JIDOKA, index 26; triage id: none; roster ref origin/handoff/audit-r10-roster abb47a06cd190e49c9d9da264ea3fab2a71f890d.
Owner-ordered: no.

Why stranded: #2853 Forward-carry: "The round-1 census's HEAD-ONLY class needs a predicting detector. Not built".

Fold into: R10-PREPR-CAP (live). Owner of tools/pr/prepr.sh among live groups (the only other is R10-FLY-NO-FOOTERS); PR #3051 is open, so this rides its next PR, not #3051.

Original text, verbatim:
From R10-FLOW-JIDOKA (#2838): the round-1 census's HEAD-ONLY class needs a predicting detector, not a reading one; step 7c can only read reds on commits already pushed.

Carry: R10-PREPR-CAP

Carry 4:
Moved from R10-PREPR-CAP carry 21 (0-based) by the carries-open audit (orchestrator s13, 2026-11-09); its own pull request merged and nothing dispatched this carry. Text verbatim:

STRANDED CARRY 28 (carry-strand audit, orchestrator s9, 2026-10-31)

Source: group R10-FLOW-JIDOKA, index 27; triage id: none; roster ref origin/handoff/audit-r10-roster abb47a06cd190e49c9d9da264ea3fab2a71f890d.
Owner-ordered: no.

Why stranded: .gitignore config/ trap: neither JIDOKA PR names it; no live carry.

Fold into: R10-PREPR-CAP (live). Owner of tools/pr/prepr.sh among live groups (the only other is R10-FLY-NO-FOOTERS); PR #3051 is open, so this rides its next PR, not #3051.

Original text, verbatim:
From r10-buffer-store (code head 208ab9a54, R10-BUFFER-STORE): .gitignore:28 ignores config/ at any depth, so git add of a TRACKED config file (dev/audit/config/, dev/governance/config/) prints 'The following paths are ignored' and exits 1 while still staging the file, and git add -A silently skips new files there. Both nested config/ directories are tracked and visible to git check-ignore, so the rule is anchored wrong for a repository with policy config directories: a handoff can silently omit a new tracked config file. Anchor the rule (e.g. /config/) or add the exception, with a control that git check-ignore still ignores a root-level config/.

Carry: R10-PREPR-CAP

Continue from handoff-wip/r10-prepr-residue 87c3ba7353; carry 4 owes its failing test first; carries 5-20 are later parts, do not build them, do not answer them in the body beyond naming them as later parts.
