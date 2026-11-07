Part 2 of R10-FLY-STANDING-CONTRACTS: the design's P3, the hooks (design/r10-fly-standing-contracts at 21210036, section 6; P1 merged as #3197). It makes carry 19 section (2), the hooks the orchestrator's sessions depend on, tracked, described and installable. The Bash guard of the orchestrator's checkout (gap 4) is the second arm of the project-level `.claude/hooks/pre-bash.sh`.

Not in this part, by the part-scope carry: design P2 (the standing-*.md policy edits, standing.md, orchestrator.md, CLAUDE.md, pulse.py STANDING, sweep_template.md), because open PRs 3245, 3262 and 3267 edit those files and its gate (every P1 row ok from main for one cycle) is unmeasured; carry 25 (the loop-cwd row), because 3262 and 3267 edit beat_jobs.py and beatd.jobs.json (read here, not edited); carry 19 section (1); the P5 carries.

## Head

8341329ac9b3d0c6ba9c846dac7ca22a2f4b9ad6 (merged with origin/main a37c58e5f at 2026-11-07T14:13:20Z; prepr rerun after the merge).

## Mutation proof

Five textual mutants of `hooks_setup.py` and `hooks/liveness.py`, each run through `--self-test` in a copy; all five die (a survivor prints FAIL and the run exits non-zero): install skips the backup; install rewrites an unrelated entry (`Stop`); install is not idempotent (drops the `ok` skip); liveness reads no late job (the DEAD arm); liveness reads no stale digest. The guard arm's refusal is pinned by `.claude/hooks/pre-bash.sh --self-test`, whose null controls (read-only git, `show origin/main:`, another repository, no `HPO_STATE_DIR`, no marker file) allow.

## Null control

On a fresh throwaway HOME, `--check` lists every user-level hook as missing; `--install` then `--check` lists none; a second `--install` leaves settings byte-identical and writes no second backup. A healthy beat table prints no DEAD, STALE, ALARM or UNREADABLE line (only the digest and the `ARM:` line). Without `orch-checkout`, all three hooks print nothing. At the base, `.claude/hooks/pre-bash.sh` had no git arm and `git pull` in the orchestrator checkout was allowed.

## Figures

- `python3 -I tools/audit/seat/hooks_setup.py --self-test`: 19 checks, 0 failed (14 fixture cases plus 5 mutants).
- `bash .claude/hooks/pre-bash.sh --self-test`: 35 passed, 0 failed (9 guard cases).
- `python3 -I tools/audit/seat/offline_spy.py tools/audit/seat/hooks_setup.py`: network=0 remote_git=0.
- `python3 -I tools/audit/seat/selftest_wiring.py --check`: 119 self-testing, 119 wired, 0 index gaps (the new governance.yml step wires it).
- `python3 tests/closure.py select` against the merge base: MODE: SCOPED, scripts run: tests/entities.py, tests/harness_headers.py; both pass.
- `python3 -I tools/audit/seat/tmp_paths.py --check` and `ref_privacy.py --check`: 0 refused.
- `tools/pr/prepr.sh` on a committed tree after merging origin/main: see the receipt.
- Open-PR overlap, `gh api repos/tvofi/heatpump_optimizer/pulls/<n>/files` over the 16 open PRs: none edits pre-bash.sh, hooks/ or a hook script; only tests/closures.json (re-derived) and tools/audit/seat/INSTRUMENTS.md (one appended row) are shared.

## Red checks

none. The first prepr run predicted `tests / closures` INERT READS (repaired by `ci_predict --apply-inert`) and refused a raw `git init` in two files (replaced by tests/throwaway_git helpers); both were caught by prepr before any push.

## Forward-carry

- Carry 19 section (2), the hooks: delivered here. Carry: R10-FLY-STANDING-CONTRACTS
- Remaining for the group: design P2 (policy), carry 25, carry 19 section (1), P5. The first two wait on the open PRs named above. Carry: R10-FLY-STANDING-CONTRACTS
- The liveness hook's alive files are read from `$HPO_STATE_DIR/alive/` and the digest's freshness from digest.txt or the beat journal (digest.txt is rewritten only on a change); P2 should name the alive-file directory in standing.md. Carry: R10-FLY-STANDING-CONTRACTS

Every other carry of the brief, by 0-based index, with its disposition. None is delivered here; the part-scope carry (Carry 26) names only carry 19 section (2), and every other carry stays open on the roster:

- Carry 0, Carry 1, Carry 2, Carry 3, Carry 4: the standing-*.md contract edits (Wait, Reads, autofix hold, Recycle, merge_pr.sh), design P2, not in this part; stay open.
- Carry 5, Carry 6, Carry 7: pulse.py and sweep_template.md edits, design P1, merged as #3197 or open in #3267; not touched here.
- Carry 8, Carry 9, Carry 10: standing-merge.md and orchestrator.md, design P2 or already landed (design item 9); not touched here.
- Carry 11, Carry 12, Carry 13, Carry 14, Carry 15, Carry 16, Carry 17: seat retirements and dispatch job, routed to R10-ORCH-LEDGER or waiting on the orchestrator's routing; not touched here.
- Carry 18: P4, once #3061 merges; stays open.
- Carry 19: delivered for its section (2) only; section (1) stays open.
- Carry 20, Carry 21: tick-digest and the mechanical jobs, built in P1 (#3197); the seat retirements are design P2; not touched here.
- Carry 22, Carry 23, Carry 24: seat_gen.py and the session lock, design P5; stay open.
- Carry 25: the loop-cwd row, not in this part because open PRs 3262 and 3267 edit beat_jobs.py and beatd.jobs.json; stays open.
- Carry 26: this part scope itself, answered above.

## Friction

none
