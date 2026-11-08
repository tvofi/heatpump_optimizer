Fix review: merge 0046931c781038daa5197422c5d21ffa63dc6f95

bus-nonce: 86d35ef4ac615763700d95b4a0b44c2b

Round: fifth review round of PR 3294 (R10-FLY-STANDING-CONTRACTS part 2). The earlier rounds blocked at 131b1358 and 7359a638 (comment 6718280627). This round reviews the r4 repair 223daee1, merged at head 0046931c781038daa5197422c5d21ffa63dc6f95, from a detached worktree at that head. Under the brief's fifth-round rule, this verdict blocks only on the named block left open or on a finding the r4 repair introduced. Neither applies, so everything new below is carried.

## Findings

- Follow-up: in the RESERVED set the r4 repair adds to `parse()` (pre-bash.sh), only `then` is pinned. If any other single word (`if`, `else`, `elif`, `do`, `while`, `until`, `{`) is dropped from the set, `pre-bash.sh --self-test` still reports 46 passed, 0 failed (ev/mutants_reserved_elements.txt). The behaviour is right at this head: every one of those forms exits 2 end to end (ev/probes_head.txt). What is missing is a self-test case for each word, such as `{ pkill x; }`, `while git -C <orch> pull; do :; done` and an `else` body. Carry: R10-FLY-STANDING-CONTRACTS
- Follow-up: two more compound forms pass, in both arms. `function f { pkill x; }` passes because `function` is recorded as the command word and `{` becomes its argument. `coproc pkill x` passes because `coproc` is neither a WRAP word nor a RESERVED word. Both exit 0 at this head and at 7359a638, so the r4 repair did not introduce them (ev/probes_head.txt, ev/probes_prev_gaps.txt). By contrast, `f() { pkill x; }`, `case`, `select` and `[[ ]] &&` are refused. These belong next to the body's carried `timeout` finding. Carry: R10-FLY-STANDING-CONTRACTS

## Evidence

- Head: 0046931c781038daa5197422c5d21ffa63dc6f95 (ev/HEAD.txt), the head the body's `## Head` names. It merges the authored head 223daee18ab05cc1b41df11148143c9d50cfee5c. The delta from 7359a638 is `.claude/hooks/pre-bash.sh` only: 10 lines added, 3 deleted (ev/checks.txt).
- Roles current: `git diff $(git merge-base origin/main HEAD)...origin/main -- dev/governance/roles/` is empty. The merge base is 5bc009bc82962df5d239cbacc2e570dffd9a9cf9.
- Prior block re-checked first, with the prior verdict's probes and run end to end over the hook's stdin (my own driver, ev/probes.sh, disclosed as mine). All nine of the prior verdict's guard probes now exit 2: if/then, else, elif, for/do, while, until, `{ }`, `pushd && git pull` and `pushd >/dev/null; git reset --hard`. The kill-arm forms `if true; then pkill x; fi`, `{ pkill x; }`, for/do pkill and while/do killall all exit 2. The null controls exit 0: `git -C <orch> status`, `echo then git pull`, `echo then pkill x`, `echo { pkill x }`, `for x in pkill killall; do echo $x; done`, `git log --format='{ then do }'`, `if [ -f x ]; then echo pkill; fi` and `kill 1234`. The positive control, `git pull` in the checkout, exits 2 (ev/probes_head.txt). The block is cured, and the cure adds no false positive among these probes.
- RESULT mutants of the r4 repair, each run on a tree-shaped copy (ev/mutants_r4.txt):
  - N0, a comment-only null control, survives: 46 passed, 0 failed.
  - R1, dropping `or w in RESERVED`, is killed: it fails `pkill after a then is refused` and `guard: a then body is read`.
  - R2, reverting `("cd", "pushd")` to `== "cd"`, is killed: it fails `guard: pushd is followed like cd`.
  - R4, dropping `then`, is killed by the same two cases.
  - R3, dropping `{`, survives. This is the first finding above.
  - The body's own two mutants are confirmed.
- RESULT self-tests at the head: `bash .claude/hooks/pre-bash.sh --self-test` gives 46 passed, 0 failed, matching the body's opening paragraph. The body's `## Figures` bullet still reads 41, which is the 7359a638 figure; it is stale but not material. `r10_bash_kill_hook_drive.py` gives 7/7 CASE ok and 3/3 MUTANT killed=yes. `selftest_wiring.py --check` gives 122 wired and 0 index gaps. `tests/structure.py` gives STRUCTURE RATCHET PASSED (ev/checks.txt).
- Not re-run this round, because the delta does not touch them: `hooks_setup.py --self-test` and the uncapped `mutant_run.py` pass. The previous round re-derived both at 7359a638 (39 checks; 45 survivors), and their inputs are unchanged.
- Merge: `git merge-tree --write-tree origin/main 0046931c781038daa5197422c5d21ffa63dc6f95` exits 0, tree 66b76f50fe71b6fb7b222c4fdacbc1c7fa91c6ab, with no conflict.
- CI: `merge_train.py classify 0046931c781038daa5197422c5d21ffa63dc6f95 --pr 3294` exits 0: `GREEN 0046931c781038daa5197422c5d21ffa63dc6f95 pending: none red: none` (ev/classify.txt). I read all 55 check runs of this head job by job (one page; total_count 55). None concluded failure or cancelled. `codeql / Analyze (python)` 128657884068 succeeded in 33 minutes, under its 45-minute cap.
- Red checks: this head has no red to answer. The body's `## Red checks` names the prior head 7359a638's three CodeQL-cancellation gate reds and its edit-run deferral, and answers them under defect-root-cause.md: a cause, the process state (no cheaper detector) and a recorded refusal. This answers the prior verdict's carried finding. `pr-contract / pr-contract` 128664854686 succeeded at 07:34Z on this body.
- Diff hygiene: the three-dot diff has 10 files and includes dev/programme/delivery/3294.md. It contains no VERSION, manifest, RELEASE_NOTES.md, `*_budgets.json` or claim file. It touches nothing under dev/governance/, nor CLAUDE.md or .claude/rules/, so no CLAUDE.md rule is loosened. New tracked files are classified (`tests / closures` and `tests / closure-scope` succeeded at this head). I did not run tests/entities.py locally, because it needs homeassistant.
- Carries: the roster handoff/audit-r10-roster at 40d18f7804d59fa08e2b161138cd00f54e87a620 holds R10-FLY-STANDING-CONTRACTS with 30 carries. The body leaves several follow-ups open: GIT_DIR/--git-dir, `D=<orch>; git -C $D pull`, `timeout`, MOVERS and the subshell cd. The body names each of them and routes it to the group; the packet's carry_audit reports 9 routed, 0 unrouted. None is silently dropped.
- Policy: tvofi's approving review is still required to merge. This verdict posts no approval.
- Finder's harness: the packet names none. The harness here is the prior verdicts' probe lists, re-run with my own driver (ev/probes.sh).

## Friction

none
