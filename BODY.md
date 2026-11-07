Part 2 of R10-FLY-STANDING-CONTRACTS: the design's P3, the hooks (design/r10-fly-standing-contracts at 21210036, section 6; P1 merged as #3197). It makes carry 19 section (2), the hooks the orchestrator's sessions depend on, tracked, described and installable. The Bash guard of the orchestrator's checkout (gap 4) is the second arm of the project-level `.claude/hooks/pre-bash.sh`.

Not in this part, by the part-scope carry: design P2 (the standing-*.md policy edits, standing.md, orchestrator.md, CLAUDE.md, pulse.py STANDING, sweep_template.md), because open PRs 3245, 3262 and 3267 edit those files and its gate (every P1 row ok from main for one cycle) is unmeasured; carry 25 (the loop-cwd row), because 3262 and 3267 edit beat_jobs.py and beatd.jobs.json (read here, not edited); carry 19 section (1); the P5 carries.

## Head

131b1358e408954ed0076904bb9a811e5e80fac8 (the code is unchanged since the kept body; the head adds the merge of origin/main 4b5d771bd and the delivery row for #3294; this body-only re-take moves nothing; origin/main has since moved to 364353e67, not merged, so the prepr receipt is from the merge at 4b5d771bd).

## Mutation proof

Five textual mutants of `hooks_setup.py` and `hooks/liveness.py`, each run through `--self-test` in a copy; all five die (a survivor prints FAIL and the run exits non-zero): install skips the backup; install rewrites an unrelated entry (`Stop`); install is not idempotent (drops the `ok` skip); liveness reads no late job (the DEAD arm); liveness reads no stale digest. The guard arm's refusal is pinned by `.claude/hooks/pre-bash.sh --self-test`, whose null controls (read-only git, `show origin/main:`, another repository, no `HPO_STATE_DIR`, no marker file) allow.

## Null control

On a fresh throwaway HOME, `--check` lists every user-level hook as missing; `--install` then `--check` lists none; a second `--install` leaves settings byte-identical and writes no second backup. A healthy beat table prints no DEAD, STALE, ALARM or UNREADABLE line (only the digest and the `ARM:` line). Without `orch-checkout`, all three hooks print nothing. At the base, `.claude/hooks/pre-bash.sh` had no git arm and `git pull` in the orchestrator checkout was allowed.

## Figures

- `python3 -I tools/audit/seat/hooks_setup.py --self-test`: 19 checks, 0 failed (14 fixture cases plus 5 mutants).
- `bash .claude/hooks/pre-bash.sh --self-test`: 35 passed, 0 failed (9 guard cases).
- `python3 -I tools/audit/seat/offline_spy.py tools/audit/seat/hooks_setup.py`: network=0 remote_git=0.
- `python3 -I tools/audit/seat/selftest_wiring.py --check`: 119 self-testing, 119 wired, 0 index gaps (the new governance.yml step wires it).
- `python3 tests/closure.py select --diff 4b5d771bdf8feb1f83d7d9443e5117b771a0ab76` at the head: MODE: SCOPED -- 2 script(s) run, 31 scoped out (tests/entities.py, tests/harness_headers.py). Both passed in CI (`tests / fast (3.14)` success, run 42393649117); this re-take seat's cloud toolchain lacks paho and could not rerun them locally.
- `python3 -I tools/audit/seat/tmp_paths.py --check`: 0 refused; `ref_privacy.py --check`: 0 refused (re-run at the head).
- `tools/pr/prepr.sh` on a committed tree after merging origin/main: see the receipt.
- Open-PR overlap, `gh api repos/tvofi/heatpump_optimizer/pulls/<n>/files` over the 16 open PRs: none edits pre-bash.sh, hooks/ or a hook script; only tests/closures.json (re-derived) and tools/audit/seat/INSTRUMENTS.md (one appended row) are shared.

## Red checks

Concluded reds at head 131b1358e408954ed0076904bb9a811e5e80fac8 (check-runs across all pages, 55 runs), by literal check-run name:

- `tests / nightly-status` (check-run 128466988722, run 42393649117): not caused by this pull request, a lane of the nightly grading `main`. It printed `NIGHTLY FAILED: mutation-ledger (1), mutation-ledger (2), mutation-ledger (3), mutation-ledger (4), mutation-ledger-push, mutation-nightly, slow` from the last concluded verification dispatch, nightly.yml run 42369836867 (head 08fd676, 2026-11-07T11:50Z), whose conclusion is `cancelled`: all seven jobs show `cancelled`, none `failure` (the dispatches 42367391498, 42364230438 and 42357667261 before it were cancelled too). The diff edits `.github/workflows/governance.yml` (7 added lines, a step that wires `hooks_setup.py --self-test`), which the nightly-status job's script `tests/nightly_status.py` does not read: it reads the run history of nightly.yml via the API, and this diff touches neither nightly.yml nor `tests/nightly_status.py`; the seven lanes are nightly.yml jobs the diff does not reach. Cheaper detector: none exists for a cancelled nightly; the standing detector is this check itself, unrequired on `main-protect`. The answer the check asks for is a concluded dispatch on main: run 42382408131 (dispatched 2026-11-07T14:36Z at a37c58e5f) is still in flight, so no verification dispatch has concluded yet and none was started by this pull request. Owner: the orchestrator's nightly dispatch cadence.
- `pr-contract / pr-contract` (check-run 128477471244, run 42393649117, step "Check the body against the contract"): class: body contract, this pull request's own; its error was exactly the `tests / nightly-status` line above with `## Red checks` reading `none`. Answered by this re-taken body. No code changed.
- `gate` (check-run 128477751544, code run 42393649117): class: derived, red only because `pr-contract / pr-contract` above is red (its log: `FAIL pr-contract / pr-contract: failure (this run)`); clears when the body passes.
- `gate` (check-run 128472335664, edit run 42393650538, 17:18:29Z to 17:30:44Z): class: the gate's edit/code deferral race. Its log reads `FAIL run(s) [42393649117] at this head are still being judged; their gate decides`: the edit run's gate waited on the code run 42393649117 while that run was still running. Not a defect of the diff; the code run's gate (128477751544) is the deciding one.

Cleared or superseded reds: the earlier head 298f0c48f (the merge of origin/main) ran code run 42393607451 and edit run 42393611022, both `cancelled` (superseded by the push of the delivery-row commit, not failed); no check concluded `failure` there. The reds of earlier heads before the merge were not re-read here; the kept body recorded none and no other red at the PR head was found.

Everything else at the head is `success` or `skipped`. The first prepr run predicted `tests / closures` INERT READS (repaired by `ci_predict --apply-inert`) and refused a raw `git init` in two files (replaced by tests/throwaway_git helpers); both were caught by prepr before any push.

## Forward-carry

- Carry 19 section (2), the hooks: delivered here. Carry: R10-FLY-STANDING-CONTRACTS
- Remaining for the group: design P2 (policy), carry 25, carry 19 section (1), P5. The first two wait on the open PRs named above. Carry: R10-FLY-STANDING-CONTRACTS
- The liveness hook's alive files are read from `$HPO_STATE_DIR/alive/` and the digest's freshness from digest.txt or the beat journal (digest.txt is rewritten only on a change); P2 should name the alive-file directory in standing.md. Carry: R10-FLY-STANDING-CONTRACTS

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

## Friction

none
