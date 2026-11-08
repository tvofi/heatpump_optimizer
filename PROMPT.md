CLOUD FIXER seat for tvofi/heatpump_optimizer, topic r10-fly-cipredict-restoring, at head 926a01499de2a184481a42734fc91bfedc5bb4b1. Never send push notifications. Write no Claude Code footer, no Co-Authored-By or Claude-Session trailer and no claude.ai session link in any commit, pull-request body or comment you produce; check your commits with `git log --format=%B` before pushing.
Setup: `git fetch --unshallow --tags origin`. Before any commit, pin the seat identity: `git config user.name hpo-fixer && git config user.email 70032254+tvofi@users.noreply.github.com`. The session-start `toolchain:` line says whether venv-ci's python3 is on PATH: on REFUSE, start each Bash call with `eval "$(bash .claude/hooks/session-start.sh --env-lines)"`. Then run `bash tools/audit/seat/cloud-setup.sh --check`, and on REFUSE stop: report its line as your result and start no work. Run anything heavy in the background with Monitor and no timeout. Never wait in one tool call longer than 240 s; poll again instead.
Role: read dev/governance/roles/fixer.md from main, and follow it exactly, in a worktree of your own cut from origin/main. Fetch 926a01499de2a184481a42734fc91bfedc5bb4b1 for the base you were given.
Output: push each verified step, fast-forward only, to refs/heads/handoff-wip/r10-fly-cipredict-restoring before any wait on a background run, so an idle container loses nothing; never step-push to handoff/r10-fly-cipredict-restoring, whose move updates the pull request. Before the handoff, when origin/main has moved since your last `tools/pr/prepr.sh` run, `git merge origin/main`, rerun `tools/pr/prepr.sh` (the body check included) and fix what it refuses; hand off only on a clean run (an unmoved main needs no second run: say so in the body). Then push the code to refs/heads/handoff/r10-fly-cipredict-restoring, then write the PR body and run `bash tools/audit/seat/body_push.sh r10-fly-cipredict-restoring <body.md>`, which pushes refs/heads/handoff-body/r10-fly-cipredict-restoring; that second push is the return signal. Once it succeeds, delete the step ref: `git push origin :refs/heads/handoff-wip/r10-fly-cipredict-restoring`. Push nothing else, open no pull request and write no delivery row. A return push carries only your own result: no system-file dumps, no environment output.
Never write to any branch except your return refs and refs/heads/handoff-wip/r10-fly-cipredict-restoring and refs/heads/handoff-wip/r10-fly-cipredict-restoring-body. Never work around a hook or a refusal; report it in your result instead.

Brief (snapshotted when this payload was rendered):
OWNER RULING 2026-11-07 (supersedes the footer's merge-main step): hand off at your first clean prepr.sh head. Do NOT merge a moved origin/main or re-run prepr because main moved. Merge main only when `git merge-tree --write-tree origin/main HEAD` reports a conflict. The merge train recarries and re-proves your head on the current main.

OWNER RULING 2026-11-07 (mutants): before handoff, set MUTANT_CMD to your group's self-test, or to a features_block.py call for the lines you changed. Let prepr.sh's diff-mutant step run `tools/audit/seat/mutant_run.py --diff` over your added lines (use --max-mutants to bound it). For every SURVIVED site, add a test that kills it, or give it a `## Unpinned sites` disposition. Report the mutant run's wall time and its survivor count in `## Figures`.

OWNER RULING 2026-11-07: a red on a check outside the required set never blocks; name it in the body only if convenient.

INTERIM TOOLCHAIN: before any measurement run: `bash tools/audit/seat/cloud-setup.sh` and then `bash tools/audit/seat/cloud-setup.sh --check`. Medium effort.

Return only by refs; open no PR, post no comment; no Claude footers; no host paths.

CLOUD FIXER (sonnet, medium effort), REPAIR round 1 for PR #3301 (R10-FLY-CIPREDICT-RESTORING, topic r10-fly-cipredict-restoring, branch fix/r10-fly-cipredict-restoring). The PR head is 926a01499de2a184481a42734fc91bfedc5bb4b1 (handoff/r10-fly-cipredict-restoring 19f57d01; body ref handoff-body/r10-fly-cipredict-restoring 87160413); base your work on the PR head, never re-cut. A fix review BLOCKED this head (verdict 2026-11-07T22:51:15Z, mutation-vacuous): 9 of 20 reviewer mutants on added ci_predict.py lines survive the full self-test. THE REPAIR: for every surviving mutant named in the verdict below, add the test or self-test arm that kills it (failing test first, then re-run the reviewer's mutants and show each now killed, with a null control that the unmutated head stays green). Then prepr.sh to a clean head, `tools/audit/seat/handoff_push.sh`, re-take the whole body from .github/PULL_REQUEST_TEMPLATE.md starting from the kept body (`## Head` at the new head, every figure re-taken, `## Red checks` naming every concluded red by literal check-run name), `tools/pr/prepr.sh --body-check`, `carry_audit.py check`, then `bash tools/audit/seat/body_push.sh r10-fly-cipredict-restoring <body>`. If a carry needs landing on the roster (CARRY-LANDED / CARRY-MISSING), this seat writes no roster ref: put the printed append-carry ops verbatim in BLOCKED-carry.txt on handoff-wip/r10-fly-cipredict-restoring-carry (parentless commit) and say so in your status line. If anything else refuses, STOP and quote the exact refusal line in BLOCKED.md on handoff-wip/r10-fly-cipredict-restoring.

THE BLOCKED VERDICT:
2026-11-07T22:51:15Z
Fix review: blocked 926a01499de2a184481a42734fc91bfedc5bb4b1 mutation-vacuous: 9 of 20 reviewer mutants on added ci_predict.py lines survive the full self-test, incl. bash run parsing and the pr-contract stand-ins

bus-nonce: e2220f90e06ca9022438f9cd22dc5c01

Round 1 (first-round adversarial fix review), PR #3301, group R10-FLY-CIPREDICT-RESTORING, measured at head 926a01499de2a184481a42734fc91bfedc5bb4b1 from a detached worktree.

## Block

The dispatch asks for "the self-test with mutation proof on every added line". The fixer's named mutants are all killed: M1-M7 reproduce the body's counts exactly (7/1/1/1/4/2/4 FAIL), and Carry 2's R1 fails the new case (1 FAIL). I then mutated the other behavioural lines the diff adds to `tools/pr/ci_predict.py`, each alone (`ev/reviewer_mutants.py`). These 9 survive the **full** `python3 -I tools/pr/ci_predict.py --self-test` (`ci_predict self-test: 0 failed` under each; `ev/reviewer_mutants_full_selftest.txt`):

- I `(?:node|python3(?: -I)?|bash)…\.(?:mjs|py|sh)` reverted to node/python only. This drops `preflight.sh` and `prepr.sh`, two of the issue's named pr-contract programs, from the arm's population. The self-test cannot see it because `made` and `runs` shrink together, and `want` names no `.sh` run.
- K `if PR_BODY in argv and body is None:` -> `if False:` (the GRADER SKIPPED path).
- L `a = ctx.get(a, a)` -> `a = a`: `$PR_BASE`, `$PR_HEAD`, `$PR_TITLE` and the others go unsubstituted.
- O `$INTENDED` stood in as an empty list.
- P the `< /tmp/pr-body.md` stdin redirect is dropped (`stdin = None`).
- E the `"reviews could not be read"` swallow for a PARTIAL run is deleted.
- H `rest = rest.split(">")[0]` is deleted.
- F the collision key `<stem>/<job>` is always the bare job name.
- N `GRADER_EXEMPT[("pr-contract", "codescan_wait.py", ...)]` is deleted.

A tenth, S, survives too: `tail = "repair before the handoff; " + who` unconditionally. It reverts Carry 3(c)'s explicit "do not print 'repair before the handoff' for those lines", and the self-test pins only the per-line `BOOTSTRAP:` suffix, not the summary line (`ev/reviewer_mutant_R1.txt`).

Killed for contrast, in graders_self_test: A, B, M and Q (the PARTIAL note and suffix), C and D (BOOTSTRAP membership), J (PR_TOKENS gap exclusion), T (workflow not passed). G (continuation join) crashes the self-test with a ValueError. See `ev/reviewer_mutants_graders.txt`.

The surviving set is the pr-contract stand-in path: argument substitution, stdin, the body skip and the `.sh` population. It is the machinery that makes the issue's pr-contract case gradable at all, and nothing pins it. The repair is a self-test case with a planted pr-contract-shaped workflow: a `bash x.sh $INTENDED < /tmp/pr-body.md` line, a `--head "$PR_HEAD"` token, a `> out` redirect and a run with no body. It should also add a `want` entry for a `.sh` run and an assertion on the main() summary tail when every red is BOOTSTRAP.

## Findings

- Survivors I, K, L, O, P, E, H, F, N and S above need a killing self-test case before the merge, at this group's next round. Carry: R10-FLY-CIPREDICT-RESTORING | dismissed: this group's own next fix round owes it under this blocked verdict; it is not a later stage
- The forward-carry routes Carry 1, Carry 3(a)/(b), Carry 4 and the per-job verdict-changing plants to R10-FLY-CIPREDICT-RESTORING, the group this PR closes (`Closes #2952`). Once it merges, the group's roster entry is its only owner, and that entry turns `done` with these still owed. The orchestrator should re-home them to a live group or issue before the merge, or state on the roster that the group stays open for them. Carry: R10-FLY-CIPREDICT-RESTORING | dismissed: re-homing is the orchestrator's roster write at this group's merge, raised here so it is not lost
- The enumeration rule (the exact step name "Restore the check source from the base commit") returns the six jobs the issue names, at both the merge base and the head. Seven other steps also check out base copies of programs on a pull request, under other step names: ci.yml prelude, refresh and gate (`tools/ci/*.py`), codeql.yml analyze (`tools/pr/codeql_scope.py`), and tests.yml closures-autofix, claims-autofix and mutation-autofix (`tests/closure.py`, `env_drift.py`, `mutation_table.py`) (`ev/other_restoring_steps.txt`). These are routers, autofixers or API readers, not file graders, and #2952's scope is the rule's six. A PR editing `tools/ci/gate.py` is still graded by the base copy in the required `gate` job and gets no BOOTSTRAP prediction. Carry: dismissed: outside #2952's stated rule and population; these jobs read the checks API rather than grade the diff's files, so a local arm could only ever be PARTIAL for them
- The body's `## Head` is partly stale. "main is not merged here" is false: dcd6c80a8 merges origin/main at dee8b413 (which contains 53273de4d449) into 19f57d012. The code claim holds, though: `git diff 19f57d012 926a01499` is empty on every PR file. Carry: R10-FLY-CIPREDICT-RESTORING | dismissed: body wording, repaired with the next round's body
- The body lists `carry_audit.py` among the plants and #2952 lists it among pr-contract's restored checkers. pr-contract's restore pathspecs do not cover `tools/audit/carry_audit.py` (`ev/restore_specs.txt`), so CI runs the head copy. The arm is correctly silent on a carry_audit edit (`ev/plant_carry.txt`). Carry: dismissed: a wording error in the issue and body; the code is right

## Evidence

- Role contract current: `git diff <merge-base>...origin/main -- dev/governance/roles/` is empty.
- Merge: `git merge-tree --write-tree origin/main 926a01499` exits 0 with tree f2fdfd819 and no conflict, against origin/main 8a1358e84 (`ev/merge_tree.txt`).
- CI: `merge_train.py classify 926a01499… --pr 3301` prints `GREEN … pending: none red: none`, rc 0, re-read at verdict time (`ev/classify_final.txt`). The packet's refusals are none; carry_audit at the head reports 4 routed, 0 unrouted.
- Null control: `ci_predict self-test: 0 failed` at the head, in 1 m 47 s (`ev/selftest.txt`).
- Fixer mutants: `mutants.py .` gives M1 7, M2 1, M3 1, M4 1, M5 4, M6 2 and M7 4 FAIL, matching the body (`ev/fixer_mutants.txt`). I re-ran R1: 1 FAIL. R2-R7 were not re-run (the body says so too).
- Enumeration: at the merge base dee8b413, and at the head, the rule returns 6 jobs (`ev/enumeration.txt`). `restoring_jobs` at the head returns the same 6 keys, and `grader_gaps` is `[]` (`ev/arm_population.txt`). Null control for the rule: none of the other jobs carrying "pinned" or "restore" step names (nightly, the tests.yml proof restores and so on) is listed.
- Real-tree verdict-changing plant, briefs (reviewer-built harness `ev/reviewer_plant.sh`, not the finder's; the finder named none). The head's brief_lint.mjs exits 0 and a malformed roster is added. The head copy gives rc 0; the arm prints `PREDICT briefs GRADER brief_lint.mjs REFUSED by the base's copy … -- BOOTSTRAP: …` and rc 1, with summary `(1 BOOTSTRAP: split or move, not repair)` (`ev/plant_briefs.txt`). Nulls: a comment-only brief_lint edit gives no red, rc 0; the roster alone gives no grader red, rc 0; an unplanted tree gives rc 0.
- Real-tree plant, budget-raise-gate: a structure budget is raised and the head copy exits 0 on `--pr`. The arm prints `GRADER PARTIAL budget-raise-gate: … its result is not a pass` and no pass claim (`ev/plant_brg.txt`). The run's one red, policy-docs `policy_lint.mjs --hooks` over budget_raise_gate.py, correctly carries no BOOTSTRAP, because policy_lint.mjs is not in its over-list.
- A real-tree verdict-changing plant for pr-contract was not made by the fixer or by me. Without `--body`, its body-reading runs are noted `GRADER SKIPPED`, never passed.
- Structure: `python3 tests/structure.py` passes; the three-dot diff touches no `*_budgets.json`, VERSION, manifest, RELEASE_NOTES, closures.json or closure.py.
- Figures: the six-job grep matches. The self-test's job-count assertion is real; mutant M7 kills it. The prepr rc=0 is carried from the fixer's run and was not re-derived here (`prepr.sh` was not re-run).
- Red checks: none on this head; the body's tmp_paths answer was not re-derived.
- Architecture: `restoring_jobs` replaces governance.yml-only keying with a directory enumeration, and `ci_tree_run` takes the workflow. That is sound. The stand-in machinery (`PR_FILES`, `PR_DROPPED`, `PR_TOKENS`, `GRADER_PARTIAL`, and a self-test that mutates `globals()["GRADER_PARTIAL"]` and pops the key afterwards) adds module-global tables to an already large file. That is not a block, but it is noted.

bus: verdict/3301 at ffadb7ee78a22f2e9d4e58c1a9ed297ad5b67f1a, confirmed from cloud-opus (review/3301 at 35cd72ed522a165ebdb271c423ef96091ac3fa83); evidence: ~/.zcode/bus/verdicts/3301/ffadb7ee78a22f2e9d4e58c1a9ed297ad5b67f1a/evidence


Before any commit run: export GIT_AUTHOR_NAME=hpo-fixer GIT_AUTHOR_EMAIL=70032254+tvofi@users.noreply.github.com GIT_COMMITTER_NAME=hpo-fixer GIT_COMMITTER_EMAIL=70032254+tvofi@users.noreply.github.com, and also git config user.name hpo-fixer && git config user.email 70032254+tvofi@users.noreply.github.com. The cloud environment exports GIT_AUTHOR_*/GIT_COMMITTER_* as 'seat', and those environment variables beat git config, so the config alone does not hold. Never commit as 'seat'; check with git log -1 --format='%an %ae %cn %ce' after the first commit.


Discovery reads (search, list, read across files) go through Agent subagents, as the frugal routing guard requires; at most 5 inline search operations per prompt; never set FRUGAL_ALLOW_INLINE.


TIME: you have hours, not minutes. A gate, prepr or recording may run an hour: wait with Monitor windows of up to 60 min and re-arm them. Never end the session waiting on a choice: take the option that keeps coverage and the architecture sound, say so in the body, and go on. Push handoff-wip at each milestone, so your liveness can be read. If truly blocked, push BLOCKED.md on handoff-wip naming the question.
