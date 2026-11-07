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

## Friction

none
