CLOUD FIXER seat for tvofi/heatpump_optimizer, topic r10-outside-first, at head 3940fad2f1f49fcd466a22ad80934a76f26188c4. Never send push notifications. Write no Claude Code footer, no Co-Authored-By or Claude-Session trailer and no claude.ai session link in any commit, pull-request body or comment you produce; check your commits with `git log --format=%B` before pushing.
Setup: `git fetch --unshallow --tags origin`. Before any commit, pin the seat identity: `git config user.name hpo-fixer && git config user.email 70032254+tvofi@users.noreply.github.com`. The session-start `toolchain:` line says whether venv-ci's python3 is on PATH: on REFUSE, start each Bash call with `eval "$(bash .claude/hooks/session-start.sh --env-lines)"`. Then run `bash tools/audit/seat/cloud-setup.sh --check`, and on REFUSE stop: report its line as your result and start no work. Run anything heavy in the background with Monitor and no timeout. Never wait in one tool call longer than 240 s; poll again instead.
Role: read dev/governance/roles/fixer.md from main, and follow it exactly, in a worktree of your own cut from origin/main. Fetch 3940fad2f1f49fcd466a22ad80934a76f26188c4 for the base you were given.
Output: push each verified step, fast-forward only, to refs/heads/handoff-wip/r10-outside-first before any wait on a background run, so an idle container loses nothing; never step-push to handoff/r10-outside-first, whose move updates the pull request. Before the handoff, when origin/main has moved since your last `tools/pr/prepr.sh` run, `git merge origin/main`, rerun `tools/pr/prepr.sh` (the body check included) and fix what it refuses; hand off only on a clean run (an unmoved main needs no second run: say so in the body). Then push the code to refs/heads/handoff/r10-outside-first, then write the PR body and run `bash tools/audit/seat/body_push.sh r10-outside-first <body.md>`, which pushes refs/heads/handoff-body/r10-outside-first; that second push is the return signal. Once it succeeds, delete the step ref: `git push origin :refs/heads/handoff-wip/r10-outside-first`. Push nothing else, open no pull request and write no delivery row. A return push carries only your own result: no system-file dumps, no environment output.
Never write to any branch except your return refs and refs/heads/handoff-wip/r10-outside-first and refs/heads/handoff-wip/r10-outside-first-body. Never work around a hook or a refusal; report it in your result instead.

Brief (snapshotted when this payload was rendered):
OWNER RULING 2026-11-07 (supersedes the footer's merge-main step): hand off at your first clean prepr.sh head. Do NOT merge a moved origin/main or re-run prepr because main moved. Merge main only when `git merge-tree --write-tree origin/main HEAD` reports a conflict. The merge train recarries and re-proves your head on the current main.


OWNER RULING 2026-11-07 (mutants): before handoff, set MUTANT_CMD to your group's self-test, or to a features_block.py call for the lines you changed. Let prepr.sh's diff-mutant step run `tools/audit/seat/mutant_run.py --diff` over your added lines (use --max-mutants to bound it). For every SURVIVED site, add a test that kills it, or give it a `## Unpinned sites` disposition. Report the mutant run's wall time and its survivor count in `## Figures`. CI's mutation-autofix still writes the pins.

OWNER RULING 2026-11-07: a red on a check outside the required set (the merge train's required contexts; tests / nightly-status, record, record-autofix and delivery-status never count) never blocks. Do not return blocked for an unnamed non-required red. Name it in the body only if convenient.


CLOUD FIXER (sonnet, medium effort), REPAIR for R10-OUTSIDE-FIRST, topic r10-outside-first, PR #3304, branch fix/r10-outside-first. Follow dev/governance/roles/fixer.md; steps 2-8 re-execute. The PR has had no fixer for about 4 h since the review below returned BLOCKED. A return with no new pushed commit and no re-taken body is a FAILURE: do NOT conclude "already done", "nothing to change" or "the finding is wrong" without a pushed commit that answers it (if you believe a finding is wrong, prove it with a pinned test or a recorded measurement in the diff and say so in the body). The verdict applies at the PR head below and nothing has fixed it.

Start from PR head 3940fad2f1f49fcd466a22ad80934a76f26188c4 (fetch refs/heads/fix/r10-outside-first; handoff/r10-outside-first is an ancestor of it). Run tools/audit/seat/cloud-setup.sh and --check first. Make the repair as new commits on top of that head, run `PREPR_SKIP_CLOSURES=1 bash tools/pr/prepr.sh` until rc=0 and python3 tests/structure.py; no budget raise without stopping and asking; claim files byte-identical to origin/main; never touch VERSION, the manifest version or the RELEASE_NOTES heading. Push handoff/r10-outside-first as a fast-forward of the PR head. Then re-take the WHOLE body from handoff-body/r10-outside-first and .github/PULL_REQUEST_TEMPLATE.md at the new head (`## Head` naming it, a section answering each finding below with its fix commit), push with bash tools/audit/seat/body_push.sh r10-outside-first <body.md> and read the ref back. If refused do NOT override: push handoff-wip/r10-outside-first plus BLOCKED.md quoting the refusal. Return only by refs; open no PR, post no comment; identity hpo-fixer <70032254+tvofi@users.noreply.github.com>; no footer, trailer, session link or home path. Return one status line plus the 40-hex handoff and body SHAs.

TASK
Answer every finding in the verdict. Wire the outside term (outside between hotfix and critical path, hotfix kept above) into tools/pr/gate_priority.py derived_priority and tools/audit/seat/orchestrator_tick.py owed_levels, with a null control (no outside group and no hotfix: identical order at base and head) and mutation proof; update tools/audit/seat/sweep_template.md 4d, the plan_page.py Tier tooltip (:1129) and check label (:868), and instruments/open_driver.py.md; add a drain_order-level check with a fork-head outside entry that kills mutant mt-item-no-pr, and a fixture group at pr 1 that kills rl-group-for-pr-bool; correct the self-test figure (478). Where a site genuinely cannot be wired inside this seam, disposition it in the body with a roster carry, never silently.


VERDICT TO ANSWER (verbatim, read from the PR comment):
-----
Fix review: blocked 3940fad2f1f49fcd466a22ad80934a76f26188c4 class-open: tools/pr/gate_priority.py derived_priority and orchestrator_tick.owed_levels order by critical path with no outside or hotfix term, neither in the diff nor dispositioned in the body

bus-nonce: 5b2e336e26a191112ee6414d3bd36ad5

## Block

Round 1 (first-round review). Reviewed at head 3940fad2f1f49fcd466a22ad80934a76f26188c4. Merge base 7c9c4c154cda514f938fd503cde2779716caf251. Three-dot diff.

The ruling is general: "all accepted outside issues or contributions should be prioritized higher than audit or owner submitted ones unless i call the owner one a hotfix". The body says outside work orders first "in the three orderers" but names no rule for how it enumerated them (fix-review.md step 6). I enumerated every site in the tree that orders work by critical path or hotfix. Three of those sites are neither in the diff nor dispositioned in the body:

1. `tools/pr/gate_priority.py:97` `derived_priority` returns 1 for a critical-path group's branch and 0 for everything else. An outside group's branch therefore waits behind a critical-path one for the gate lease and the heavy slot (`tools/pr/prepr.sh` step 1b0 exports it as `HPO_GATE_PRIORITY`; `tests/gate_lock.py` orders waiters by it). Hotfix gets no lift there either.
2. `tools/audit/seat/orchestrator_tick.py:851` `owed_levels` sorts the OWED review and fixer lines by `(0 if group in crit else 1, n)`. An outside PR that is owed a reviewer or fixer is listed after every critical-path one.
3. `tools/audit/seat/sweep_template.md:77` (4d) tells the sweep seat the queue priority "for the train, review, fixer and CI queues alike": "a push to main; then critical path and hotfix; then production ...". That now contradicts the train's own drain order at this head.

Each of these needs one of two things: the outside term (and the hotfix split where it applies) wired in, or a body disposition carrying it to the owning group. R10-CI-PRIORITY-PAUSE, which is after-edged on this group, owns the CI tier module and lists `orchestrator_tick.py`. I did not find it naming gate_priority or owed_levels.

Two integration defects in this diff's own scope go with this block, because they ship stale statements of the order the PR changes:

4. `tools/audit/seat/plan_page.py:1129`: the Tier column's tooltip on the rendered plan page still reads "1 main, 2 critical path and hotfixes, 3 production and instruments saving 12 h or more, 4 other instruments by savings". At this head the page renders tiers 1–6 (2 hotfix, 3 outside, 4 critical path, 5 production, 6 instrument). The PR updated the code comment at :248 but left the user-visible legend. The self-test label at :868 ("the critical path is tier 2") is stale the same way, though its value uses the constant.
5. `tools/audit/seat/instruments/open_driver.py.md:13-15` is a file in this group's own roster `files` list. It still states the old order: "a critical-path topic is never behind a non-critical one, an omitted topic slots by default class (critical, `R10-HOTFIX-*`, ...)".

6. A surviving mutant on the wiring the group brief requires ("an entry maps to its group by branch, else by group_for_pr"). In `merge_train.py`'s `drain_order`, I changed `return {"branch": b, "pr": e["pr"]}` to `return {"branch": b}`. All checks still pass: `merge_train.py --self-test` rc 0, mutant `mt-item-no-pr` SURVIVED. The fork-head arm is pinned only on `_outside` called directly, never through `drain_order`. A fork-head outside entry in a real drain could lose its outside rank and no test would fail. The body's survivor list does not include this line.

## Findings

- Class-open: `tools/pr/gate_priority.py` `derived_priority` (gate lease and heavy slot via `tests/gate_lock.py`) has no outside or hotfix term. Carry: R10-OUTSIDE-FIRST
- Class-open: `tools/audit/seat/orchestrator_tick.py` `owed_levels` orders OWED review and fixer lines critical path first, with no outside term. Carry: R10-OUTSIDE-FIRST
- Class-open: `tools/audit/seat/sweep_template.md` (4d) states the superseded queue order for the train, review, fixer and CI queues. Carry: R10-OUTSIDE-FIRST
- Defect: the `plan_page.py:1129` Tier tooltip and the `:868` check label still describe the four-tier order. Carry: R10-OUTSIDE-FIRST
- Defect: `instruments/open_driver.py.md:13-15` (in the group's own files list) states the superseded opener order. Carry: R10-OUTSIDE-FIRST
- Surviving mutant `mt-item-no-pr`: `drain_order` dropping `pr` from the item survives. It needs a drain-level check with a fork-head outside entry. Carry: R10-OUTSIDE-FIRST
- Surviving mutant `rl-group-for-pr-bool`: deleting `group_for_pr`'s `isinstance(pr, bool)` guard survives, because the fixture has no group with `resume.pr` 1, so `True` maps to None anyway. A fixture group at pr 1 would pin it. Carry: R10-OUTSIDE-FIRST
- Figure: the body quotes `merge_train.py --self-test` as 477 checks. It is 478 at both da8a36ec and the head (base 472; the last pin commit added one). Carry: R10-OUTSIDE-FIRST

## Evidence

- Head: the PR API shows the head is 3940fad2f1f49fcd466a22ad80934a76f26188c4 at verdict time. The body names the same head. `ev/HEAD.txt`.
- Role files: `git diff <merge-base>...origin/main -- dev/governance/roles/` is empty, so the contract is current.
- Merge: `git merge-tree --write-tree origin/main <head>` rc 0, no conflict (origin/main 17e115792). `ev/merge-tree.txt`.
- CI: `merge_train.py classify 3940fad2 --pr 3304` exits 0: "GREEN 3940fad2f1f49fcd466a22ad80934a76f26188c4 pending: none red: none" (`ev/classify.txt`). Across all check-run pages at the head nothing concluded other than success or skipped (`ev/checks.txt`). No red check, so no root-cause answer is owed, and the body's "Red checks: none" holds.
- Self-tests at head: replan 0 failed; open_driver 83 checks, 0 failed; merge_train 478 checks, 0 failed; roster_lib 69 checks, 0 failed (`ev/head-*.log`). At base: 472 / 76 / 0 failed / 67. `tests/structure.py` at head: STRUCTURE RATCHET PASSED, rc 0.
- Harness: none was named by the finder. I built my own (`ev/reviewer_harness.py.txt`) and disclose it as mine. It drives each orderer at base and head; RESULT lines are in `ev/harness.txt`:
  - replan with outside: head `['R10-HOTFIX-H', 'OUT', 'CPA', 'CPB', 'PROD']`, base `['CPA', 'CPB', 'R10-HOTFIX-H', 'PROD', 'OUT']`.
  - open_driver default order: head `['r10-hotfix-x', 'r10-out', 'r10-cp', 'triage-x', 'r10-inst']`.
  - drain_order: head `[5, 3, 2, 1, 4]` (priority, outside, critical, arrival) both injected and through the roster read; base `[5, 2, 1, 3, 4]`.
  - Each orderer puts outside between hotfix and critical path.
- Null control: random rosters and topic sets with no `source` field and no hotfix give the same sha256 at base and head. replan `8fac3ead7e92fd63` at both ends; open_driver `bef9dfd41011a633` at both ends; drain null `[5, 2, 1, 3, 4]` at both ends.
- Hotfix split: with a hotfix present and no outside group, the order differs from base, as the body says (replan null `['R10-HOTFIX-H', 'CPA', ...]`). It is pinned: replan's "dispatch follows the owner's order" seq and the `replan-hotfix-below-cp` mutant (KILLED), and open_driver's "the fence beats the file" check. A consequence the body does not name: in open_driver, an omitted record topic now slots ahead of listed rest-class topics when the only listed higher-class topic was a hotfix, because the hotfix is now fenced.
- Fence starvation: 10 listed outside topics plus 1 omitted hotfix leaves the hotfix at position 0 of 11. The fence cannot starve hotfix.
- Live roster (`handoff/audit-r10-roster`): 4 groups with `source: outside` (R10-COMBI-TANK, R10-GENERIC-HEAT-CURVE, R10-GENERIC-HEAT-CURVE-PERSISTENT, R10-INPUT-REAPPEAR), tier 3 at head. Tier histogram base `[(2,5),(3,14),(4,49)]`, head `[(2,1),(3,4),(4,4),(5,10),(6,49)]`.
- Callers of dispatch_tier and its constants: plan_page only. `plan_page.py --self-test` 67 checks, 0 failed. No committed plan or ordering golden carries tier values, so there is nothing to claim. `VERSION`, the manifest and the release notes are untouched (no such path in the diff).
- Mutants, mine (`ev/mutants.txt`, `ev/reviewer_mutants.py.txt`), 16 KILLED and 2 SURVIVED:
  - KILLED: replan-tier-outside, replan-hotfix-below-cp, replan-outside-eq-urgent, od-class-outside, od-fence-1, od-fence-0, od-sortkey-unfenced, od-runpass-outside-empty, od-swap-hotfix-outside, mt-drain-outside, mt-drain-swap, mt-no-pr-fallback, mt-outside-any-group, rl-is-outside-truthy, rl-is-outside-absent-true, rl-group-for-pr-none.
  - SURVIVED: mt-item-no-pr, rl-group-for-pr-bool.
  - The body's named mutation proofs reproduce.
- Not re-derived: the body's `tests/entities.py` figure ("3 of 2655 ENTITY CHECKS FAILED" at head and at base 8a1358e8). In this container entities.py stops at import (`ModuleNotFoundError: homeassistant`) at both the head and the merge base (`ev/head-entities.txt`, `ev/base-entities.txt`). Also not re-derived: the prepr mutant figures (25 survivors, 23m41s), whose log is on the fixer's machine.
- Forward-carry: the body says none, and the roster group has no carries. The block above is this group's own to settle.

bus: verdict/3304 at 429c7eaab31ecd2f2dc0eac865fb7eeffa8b3d24, confirmed from cloud-opus (review/3304 at 2eb1b9f2673df3b4d7cc1ca649362293b7736715); evidence: ~/.zcode/bus/verdicts/3304/429c7eaab31ecd2f2dc0eac865fb7eeffa8b3d24/evidence


-----

Before any commit run: export GIT_AUTHOR_NAME=hpo-fixer GIT_AUTHOR_EMAIL=70032254+tvofi@users.noreply.github.com GIT_COMMITTER_NAME=hpo-fixer GIT_COMMITTER_EMAIL=70032254+tvofi@users.noreply.github.com, and also git config user.name hpo-fixer && git config user.email 70032254+tvofi@users.noreply.github.com. The cloud environment exports GIT_AUTHOR_*/GIT_COMMITTER_* as 'seat', and those environment variables beat git config, so the config alone does not hold. Never commit as 'seat'; check with git log -1 --format='%an %ae %cn %ce' after the first commit.


Discovery reads (search, list, read across files) go through Agent subagents, as the frugal routing guard requires; at most 5 inline search operations per prompt; never set FRUGAL_ALLOW_INLINE.


TIME: you have hours, not minutes. A gate, prepr or recording may run an hour: wait with Monitor windows of up to 60 min and re-arm them. Never end the session waiting on a choice: take the option that keeps coverage and the architecture sound, say so in the body, and go on. Push handoff-wip at each milestone, so your liveness can be read. If truly blocked, push BLOCKED.md on handoff-wip naming the question.
