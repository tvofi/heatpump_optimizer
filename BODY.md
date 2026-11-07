Part 2 of R10-FLY-STANDING-CONTRACTS: the design's P3, the hooks (design/r10-fly-standing-contracts at 21210036, section 6; P1 merged as #3197). It makes carry 19 section (2), the hooks the orchestrator's sessions depend on, tracked, described and installable. The Bash guard of the orchestrator's checkout (gap 4) is the second arm of the project-level `.claude/hooks/pre-bash.sh`.

This round repairs the blocked fix review at 131b1358 (verdict/3294), two blocks:

1. architecture-unsound, design [V4]: the guard arm split a command with its own `re.split` and `shlex`, so `bash -c`, `eval`, `( )` and `$( )` moves of the orchestrator checkout passed. The command-position parser is now its own block, `HPO_PRE_BASH_PARSE_PY`, and `decide` prepends it to each arm through one `arm` function, so neither arm splits a command itself. The parser now records each simple command's argv as well as its word (the kill arm reads the word, the guard reads the argv and follows `cd` in order), and an `eval`'s whole argument list is read as its body (before, only the first word after `eval` was). The guard's own `re.split`/`shlex` loop is deleted.
2. mutation-vacuous: `hooks_setup.py --self-test` gains a case whose `seat_venv.sh --check` refuses (the fixture state holds `orch-checkout` and no `venv-ci`) and asserts the `SEAT-INTERPRETER refused` line, and its in-tree mutant list gains S1 (`if r.returncode == 0:` becomes `if True:`).
3. Found while pinning S1, disclosed here: the in-tree mutant loop of `hooks_setup.py --self-test` was vacuous at 131b1358. It copied `tools/audit/seat` alone, and in that copy the un-mutated self-test was already red (3 cases: no `.claude/settings.json`, no `pre-bash.sh`; with S1, a fourth: no `tests/typing_budgets.json`), so every in-tree mutant counted as killed whatever it did, including the body's five that the review accepted. It now copies what `cases()` reads (`COPY_FOR_MUTANTS`), runs the un-mutated copy first as a null control that must pass, and searches the hook files before `hooks_setup.py`: the stale-digest anchor carries no newline, so it also matched its own literal in the `MUTANTS` list, and that literal took the mutation instead of liveness.py. With the copy repaired, that mutant survived until the search order was fixed.
4. The diff-mutant step (`mutant_run.py --diff`, owner's 2026-11-07 ruling) found unpinned branches in the hooks this PR adds. New cases cover them: liveness.py against a stub `beatd.py` (failed job, `DOWN`, `ALERT`, `STALE-CODE`, a short `JOB` line, exit 2), its alive and digest thresholds half a minute past their defaults, an unparseable `HPO_ALIVE_STALE_MIN`, a missing re-read stamp, a `policy_reread_check.py` that cannot run, an `orch-checkout` naming no directory; seat_interpreter.py against a stub `seat_venv.sh` (passing: silent; refusing: its last line); git_identity.py's `user.name` and a one-line identity file; each hook's bare `--state`; and `hooks_setup`'s check without a project guard, install under a missing directory, and its command line. `_run_hook` now appends `EXIT <rc>` when a hook exits non-zero, so a crash no longer reads as silence.

Alternatives weighed: keeping the guard's splitter and adding `bash -c`/`eval`/`$( )` cases to it lost because it is the duplicate parser [V4] rejects, and it would drift from the kill arm's rules. Making the guard a separate hook lost for the same reason (the design rejected it). Sourcing the parser as a separate `.py` file lost because the hook already carries its python as marked blocks that `extract` reads; one more block keeps the one mechanism.

Not in this part, by the part-scope carry: design P2 (the standing-*.md policy edits, standing.md, orchestrator.md, CLAUDE.md, pulse.py STANDING, sweep_template.md), because open PRs 3245, 3262 and 3267 edit those files and its gate (every P1 row ok from main for one cycle) is unmeasured; carry 25 (the loop-cwd row), because 3262 and 3267 edit beat_jobs.py and beatd.jobs.json (read here, not edited); carry 19 section (1); the P5 carries.

## Head

65f5930251490c4376c8ebca350e7f446cca6333 (four commits on the PR head 131b1358e408954ed0076904bb9a811e5e80fac8; no merge of origin/main: `git merge-tree --write-tree origin/main HEAD` exits 0 with no conflict, and the owner's 2026-11-07 ruling says merge main only on a conflict).

## Mutation proof

The fix review's five probes, each pinned in `bash .claude/hooks/pre-bash.sh --self-test`, each with a mutant applied to a copy of the hook (the real hook untouched) that turns its case red; a one-off driver in scratch, as the reviewer's was:

- P1, the `bash -c` body is never parsed (`if shellc:` becomes `if False:`): KILLED, FAIL `guard: a bash -c body is read`, `guard: a cd inside sh -c is followed`, and the kill arm's `pkill inside bash -c is refused`.
- P2, an `eval`'s words are never collected (`body = []` becomes `body = None`): KILLED, FAIL `guard: an eval body is read`.
- P3, `(` no longer reopens command position (`end(); at = True` becomes `end(); at = False` in the `(` branch): KILLED, FAIL `guard: a subshell's cd is followed`.
- P4, an unquoted `$( )` body is skipped, not parsed: KILLED, FAIL `guard: a $( ) substitution is read` and the kill arm's `kill fed by pgrep in a substitution is refused`.
- P5, the guard ignores `cd` (`cur = under(cur, to[0])` becomes `pass`): KILLED, FAIL `guard: cd then reset is refused`, `guard: a subshell's cd is followed`, `guard: a cd inside sh -c is followed`.
- N0, a comment-only change: SURVIVED, as a null control should.

`hooks_setup.py`'s in-tree mutants, each run in a faithful copy with `--self-test --no-mutants`, naming the case that kills it (a one-off driver in scratch; the in-tree loop runs the same set): null control, the copy un-mutated: rc=0, no FAIL. Install skips the backup: FAIL `install backs the file up first, holding the old bytes`. Install rewrites an unrelated entry: FAIL `install keeps unrelated entries`. Install is not idempotent: FAIL `a second install changes nothing`. Liveness reads no dead loop: FAIL `liveness: a planted dead loop prints DEAD`. Liveness reads no stale digest: FAIL `liveness: a planted stale digest and alive file print STALE` and the 30.5-minute case. S1, seat-interpreter never reports: FAIL `seat-interpreter: a refusing seat_venv.sh --check prints SEAT-INTERPRETER refused` and `the refusal quotes the check's last line`. The null control bites: with `.claude/settings.json` removed from `COPY_FOR_MUTANTS`, `--self-test` prints `FAIL mutant 'null control: the copy un-mutated' is red` and exits 1.

## Null control

At the PR head 131b1358 the reviewer's probe set (verdict/3294 evidence/guard_probes.txt), re-run end to end over the hook's stdin with `HPO_STATE_DIR/orch-checkout` naming a throwaway repository: `git pull` in the checkout rc=2, `git status` rc=0; the five probes all rc=0 (`bash -c 'git pull'`, `eval git pull` from the checkout; `(cd <orch> && git pull)`, `echo x $(git -C <orch> checkout main)`, `sh -c 'cd <orch>; git reset --hard'` from another repository); `echo 'git pull' > notes.txt` and `grep 'git reset' file` rc=0. At 65f59302, the same probes: controls unchanged (2 and 0), the five all rc=2, the two false-positive probes rc=0. At the PR head, S1 survived `hooks_setup.py --self-test` (the reviewer's evidence/mutants.txt), and the un-mutated copy of the in-tree mutant loop was red on 3 cases, so each in-tree mutant's kill was vacuous.

## Figures

- `bash .claude/hooks/pre-bash.sh --self-test`: 41 passed, 0 failed (15 guard cases, of which 5 are the fix review's probes and 1 a new quoted-text null control).
- `python3 -I tools/audit/seat/hooks_setup.py --self-test`: 39 checks, 0 failed (32 fixture cases, the null-control copy and 6 mutants).
- `python3 -I tools/audit/seat/r10_bash_kill_hook_drive.py`: 7 of 7 CASE ok and 3 of 3 MUTANT killed=yes, run from the real settings.json, so the kill arm still refuses through the shared parser.
- Seam census (fixer step 8). The rule that enumerates the class's seams is the parser's own: every separator in `SEP` and the `;`/newline/`&&`/`||`/`|`/`&` branches, the `(`, `$( )` (quoted and unquoted) and backtick recursions, the `SHELLS -c` and `eval` bodies, every `WRAP` word, an assignment prefix, a path-qualified `git`, and `cd`. One `git -C <orch> pull` (or `cd <orch>` then `git pull`) behind each, 25 seams, end to end from another repository, at the PR head then at 65f59302: 11 went rc=0 to rc=2 (closed in this diff: `( )`, `$( )`, `"$( )"`, backticks, `bash -c`, `sh -c`, `zsh -c`, `eval` bare and quoted, `/usr/bin/git`, `cd` then `bash -c`); 13 were rc=2 at both (already guarded: `;`, newline, `&&`, `||`, `|`, `&`, `sudo`, `env X=1`, `command`, `nohup`, `time`, `X=1`, `cd &&`); 1 is rc=0 at both: `timeout 5 git ...`, a distinct finding of the shared parser, named in Forward-carry. Null controls in the same run: `git -C <orch> status`, quoted echo text and a `git pull` in the other repository rc=0 at both; a heredoc body holding the command was rc=2 at the PR head (the old splitter read heredoc lines) and is rc=0 now, because the shared parser drops heredoc bodies. The census is a one-off driver in scratch, as the reviewer's probes were.
- `python3 -I tools/audit/seat/mutant_run.py --diff <merge base>...HEAD --cmd "python3 -I tools/audit/seat/hooks_setup.py --self-test --no-mutants" --max-mutants 0 --report-only`, the uncapped pass over all 211 mutants of the diff's added Python lines: wall time 8m52.7s, 45 survivors, each dispositioned under `## Unpinned sites`. Before this round's cases the same pass left 78 (wall 6m05.7s), and the capped prepr pass (40 mutants) left 17 at e2ddc6ed, then 2 at 42234a71 (wall 1m23.2s).
- `python3 tools/audit/archscore/score.py --diff 131b1358e408954ed0076904bb9a811e5e80fac8 HEAD`: `Architecture score: dS +0.0000 NULL`.
- `python3 -I tools/audit/seat/offline_spy.py tools/audit/seat/hooks_setup.py`: 1 files, 0 refused.
- `python3 -I tools/audit/seat/selftest_wiring.py --check`: 0 index gaps.
- `python3 -I tools/audit/seat/tmp_paths.py --check` and `python3 -I tools/audit/seat/ref_privacy.py --check`: 0 refused.
- `python3 tests/structure.py`: STRUCTURE RATCHET PASSED; no `*_budgets.json` and neither claim file in the diff; VERSION, the manifest version and the RELEASE_NOTES heading untouched.
- `tools/pr/prepr.sh` with `MUTANT_CMD="python3 -I tools/audit/seat/hooks_setup.py --self-test --no-mutants"` on the committed head, with this body: see the receipt. Its capped diff-mutant step (40 of 211, `MUTANT_MAX` default) reports 2 survivors, `hooks/git_identity.py:51` and `hooks/liveness.py:44`, both equivalent and listed below.

## Unpinned sites

Every survivor of the uncapped pass at 65f59302, 45, by class:

- Equivalent, the same return value or exit status: `tools/audit/seat/hooks/git_identity.py:51`, `hooks/liveness.py:132` and `hooks/seat_interpreter.py:41` RETURN_DEL of `return 0` in `main` (falls off to `None`, and `sys.exit(None)` exits 0); `hooks/liveness.py:44` RETURN_DEL of `return None` (falls off to `None`); `hooks/liveness.py:116` RETURN_DEL and `:115` GUARD_OFF (with no state, `report(Path(""))` reads `./orch-checkout`, absent, and returns nothing, then exit 0); `tools/audit/seat/hooks_setup.py:408` RETURN_DEL of the REFUSE path's `return 2` (falls through to the usage path, `return 2`, with REFUSE already on stderr).
- Float equality, unreachable: `hooks/liveness.py:95` and `:99` CMP_BOUND `>` to `>=` (an mtime age exactly equal to the threshold, to the bit); each threshold is pinned half a minute either way by the 120.5- and 30.5-minute cases.
- Formatting only: `hooks_setup.py:135` CONST_SWAP `indent=2` to `indent=3` (the settings file's JSON is unchanged; the byte-identity case compares two writes of the same indent).
- The entry point of the self-test that judges it: `hooks_setup.py:413` GUARD_OFF and `:414` CALL_DEL of `if __name__ == "__main__": sys.exit(main(...))` make `--self-test` do nothing and exit 0.
- The oracle itself, 33 sites in `hooks_setup.py` lines 143 to 390 (`_fixture_state`, `cases()`, `COPY_FOR_MUTANTS`, `self_test`): a mutant of the self-test's own fixture, temp cleanup or mutant loop, which `--no-mutants` skips by construction; the loop is judged by its null control and the six in-tree mutants above.

## Red checks

Every concluded non-success check run at the PR head 131b1358 (`check-runs?filter=all`, both pages, 134 runs), by literal name. The new head carries no CI yet; the merge train re-proves it.

- `tests / nightly-status` (128515447702, 128466988722): failure. Class: outside the required set (the owner's ruling: it never counts). It grades main's last nightly dispatch, whose `mutation-ledger (1..4)`, `mutation-ledger-push`, `mutation-nightly` and `slow` lanes failed; this diff's governance.yml change only wires the `hooks_setup.py --self-test` step, which reads no nightly lane. Answer: not this pull request's own; owned by the nightly lanes' owner on main. No cheaper detector: the check is itself the detector of main's nightly.
- `pr-contract / pr-contract` (128515449967, 128477471244): failure at 17:40:12Z, because the body did not yet name `tests / nightly-status`. Superseded by `pr-contract / pr-contract` 128515052906, success at 20:10:54Z after the body named it. Class: body, repaired. Cheaper detector: `prepr.sh --body-check` reads the same rule offline; it could not see the red before CI raised it.
- `gate` (128467499637 cancelled, 128472335664 failure "run(s) at this head are still being judged", 128477751544 failure on the pr-contract red above): superseded by `gate` 128515245845, 128515449064 and 128515453754, all success after 20:10Z. Class: inherited from the pr-contract red and a run still judging; no detector cheaper than the gate itself.

## Forward-carry

- Carry 19 section (2), the hooks: delivered here. Carry: R10-FLY-STANDING-CONTRACTS
- Remaining for the group: design P2 (policy), carry 25, carry 19 section (1), P5. The first two wait on the open PRs named above. Carry: R10-FLY-STANDING-CONTRACTS
- The liveness hook's alive files are read from `$HPO_STATE_DIR/alive/` and the digest's freshness from digest.txt or the beat journal (digest.txt is rewritten only on a change); P2 should name the alive-file directory in standing.md. Carry: R10-FLY-STANDING-CONTRACTS
- The fix review's follow-up, the design owner's and not this repair's: the design's MOVERS list (`checkout switch reset pull merge rebase stash clean restore`, line 194 of the design note on the branch design/r10-fly-standing-contracts), kept here as the design has it, omits `cherry-pick`, `revert`, `am`, `apply`, `rm`, `mv` and `checkout-index`, which also rewrite the working tree a running script is read from; the design owner judges whether gap 4's class is wider than the list. Carry: R10-FLY-STANDING-CONTRACTS
- The shared parser treats a wrapper's positional argument as the command word, so `timeout 5 git -C <orch> pull` and `timeout 5 pkill x` both pass, in both arms, before and after this diff (the header's known-gap paragraph names the option-taking form, `sudo -u root pkill x`, not this one). A distinct finding of the parser, outside this repair. Carry: R10-FLY-STANDING-CONTRACTS
- The guard follows a `cd` inside `( )` past the close, so `(cd <orch>); git pull` from another repository is refused although bash would run the pull outside the checkout. It can only refuse more, never less; stated in the arm's comment. Carry: R10-FLY-STANDING-CONTRACTS

## Carries

Every other carry of the brief, by 0-based index, with its disposition. None is delivered here; the part-scope carry (Carry 26) names only carry 19 section (2), and every other carry stays open on the roster:

- Carry 0, Carry 1, Carry 2, Carry 3, Carry 4: the standing-*.md contract edits (Wait, Reads, autofix hold, Recycle, merge_pr.sh), design P2, not in this part; stay open.
- Carry 5, Carry 6, Carry 7: pulse.py and sweep_template.md edits, design P1, merged as #3197 or open in #3267; not touched here.
- Carry 8, Carry 9, Carry 10: standing-merge.md and orchestrator.md, design P2 or already landed (design item 9); not touched here.
- Carry 11, Carry 12, Carry 13, Carry 14, Carry 15, Carry 16, Carry 17: seat retirements and dispatch job, routed to R10-ORCH-LEDGER or waiting on the orchestrator's routing; not touched here.
- Carry 18: P4, once #3061 merges; stays open.
- Carry 19: delivered for its section (2) only; section (1) stays open.
- Carry 20, Carry 21: tick-digest and the mechanical jobs, built in P1 (#3197); the seat retirements are design P2; not touched here.
- Carry 22, Carry 23, Carry 24: the generation token and the session lock, design P5; stay open.
- Carry 25: the loop-cwd row, not in this part because open PRs 3262 and 3267 edit beat_jobs.py and beatd.jobs.json; stays open. Carry: R10-FLY-STANDING-CONTRACTS
- Carry 26: this part scope itself, answered above.
- Carry 27: the roster lists a carry past the brief text this part was given; not in this part's scope (Carry 26 names only carry 19 section (2)); stays open. Carry: R10-FLY-STANDING-CONTRACTS
- Carry 28: the roster's echo of this PR's earlier body item 28185cf3 (the Carry 25 disposition above); the same loop-cwd row, stays open with Carry 25.
- Carry 29: the roster's echo of this PR's earlier body item 8a9d989c (the Carry 27 disposition above); stays open with Carry 27.
- Carry 30: `review_packet.py` counts the roster's carries 1-based, 1 to 30, where this list numbers them 0-based, 0 to 29; its carry 30 is Carry 29 above, and its carry 1 is Carry 0. No carry is unanswered under either count.

## Friction

none
