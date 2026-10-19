Fix review: merge c12b0562da080854e16e52448b7cdb4f1f242883

bus-nonce: afbc68925ad8420912f95516d058e9fd

Round 2. Round 1 is the `Fix review: blocked 01e08685…` comment, which blocked on the fold-7 regression after #2406/O17. I measured head `c12b0562da080854e16e52448b7cdb4f1f242883` (ev/HEAD). It was still the PR head and the branch tip at 05:23Z. The role contract is current: `git diff <merge-base>...origin/main -- dev/governance/roles/` is empty. I worked from a detached worktree at the head, and `git status --short` was empty after every mutant.

## Round 1's block is closed
- `orchestrator_tick.py --self-test` at head: `150 checks, 0 failed` (ev/selftests.txt). At 01e08685 it raised AttributeError.
- At head, no `DEFAULT_ROSTER_REF` remains in tools/ or tests/ (ev/classrule.txt). The fold-9 class is one seam, and it is closed.
- Live `--only CARRY` at head, with carry_audit.py absent: `UNREADABLE: carry sweep (tools/audit/carry_audit.py absent …)`.
- The same run with #2404's `carry_audit.py` (b419463b) copied in untracked and deleted afterwards: the sweep runs through `_roster_ref` without raising. Here gh is unreachable, so carry_audit exits 1 with `REFUSED` and no summary, and the tick reports that as UNREADABLE, not as a finding (ev/only_carry_head.txt).
- The fix follows O17: `_roster_ref` returns `--roster-ref`, else `rl.default_roster_ref(self.git)` with its note, and PLAN and CARRY share it.

## Mutation proof (my own mutants, ev/mutants.txt)
- R1, the body's form (`self.roster_ref or rl.DEFAULT_ROSTER_REF`): 8 failed. Matches the body.
- R1', replacing `_roster_ref` outright: 10 failed.
- R2, main twice: 3 failed. The body says 2; this form of the mutant also fails the generic argv arm.
- R3, note dropped: 2 failed. Matches the body.
- R4, `--roster-ref` ignored: 5 failed, PLAN arms.
- M5, the age window restored: 1 failed. U2, `--merges` on the first-parent read: 1 failed. C6, exit 1 unflagged: 1 failed. C7, `if False:` (body form): 2 failed. X1, the newest merge skipped in `unrecorded()`: 3 failed.
- M7, the exact-name discharge restored in bus.sh: `bus self-test: 70 checks, 1 failed`.
- Survivors, judged non-blocking:
  - C7b: dropping the `rc not in (0,1)` half while keeping the summary test survives. In #2404's carry_audit.py, the only exit-2 path (`RosterNotFound`) returns before printing `CARRY-SWEEP:`, and an uncaught exception exits 1 with no summary. Either way the summary test alone reports it UNREADABLE, so there is no realistic path.
  - R5: the `rl is None` UNREADABLE guard deleted survives. roster_lib.py is tracked, and losing it would raise rather than guess a ref, so the body's "never a guessed ref" still holds. Unpinned, and minor.
- Failing first, re-run: `pr_args.sh --self-test` at fb46dfc7 prints `31 checks, 17 failed`. Matches the body (ev/failing_first_fb46dfc7.txt).

## Figures re-derived at head (ev/selftests.txt, ev/cheap.txt)
- Self-tests:
  - delivery_row: 5/0
  - pr_args: 46/0 (via both open_pr and update_pr)
  - pr_cap: 12/0
  - orchestrator_tick: 150/0
  - tick_loop: 4/0
  - bus: 70/0
  - proof_watch: 34/0
  
  All match the body.
- Repo checks:
  - agreement: `RESULT divergent=0 unregistered=0 dead=0 refused=0` and `AGREEMENT ok`
  - `STRUCTURE RATCHET PASSED`
  - `ALL 2349 ENTITY CHECKS PASSED` (needs `PYTHONPATH=tests/hastub`; without it, entities.py fails on a missing `homeassistant` import in this container)
  - `MODE: SCOPED -- 0 script(s) run, 33 scoped out`
  - claims hygiene ok
- Fold 5's class rule (`git grep 'Merge pull request #\(|"--merges"'`): 4 production sites at 62d7e1e4; none at head outside the self-test stub; none elsewhere in tools/audit/seat/. Matches the body.
- Not re-derived: the live-board figures in the body (10 OWED handoffs, the 16→19 PR enumeration, the pr_cap 14 open). They depend on the board and on network reads I did not reproduce. They are not verified here.

## Merge, versions, carries
- `git merge-tree --write-tree origin/main <head>`: rc=0, against 2d843030 and against the newer main 913ce1ff (tree 2586d326). No claim driver was needed.
- VERSION, the manifest, RELEASE_NOTES, goldens, the claim files and every `*_budgets.json` are untouched in the three-dot diff.
- The head's last merge, c12b0562 (main 2d843030 into 299c7de4), changes only `dev/programme/delivery/*.md` rows.
- The inbound carry (the roster's R10-OPENPR-SILENT `carry`, the weekly and closure sweep) is delivered. Its control (exit 0 prints no dispatch, exit 1 prints one) is pinned by C6 and by the exit-0 null control.
- The outbound "CI wiring" item is a proposal for new work and does not constrain an unstarted stage, so finding-propagation does not apply. `grep` of .github/workflows confirms no workflow runs these self-tests.
- Note for the orchestrator, not a block: after merge, `open_pr.sh` refuses at ≥6 counted open PRs unless `--over-cap` is passed, and the refusal line names that flag.

## CI on this head (check-runs API, 45 runs)
Every completed run is success, skipped or neutral (CodeQL), with no red, pr-contract included (two runs). The reds on 01e08685 (rate limit) are answered in the body's Red checks section. `closures` concluded success (job 117900954098). `Analyze (python)` (CodeQL) was still in progress at return; the CodeQL aggregate check reads neutral. Head re-read at return: still c12b0562.
