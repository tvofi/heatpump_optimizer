Fix review: merge 3447a165f6eaa8945bc5077b518845f3b0db7f4c

## Findings
- tools/audit/seat/orchestrator_tick.py:2413 (non-blocking): `roster_invariants` creates the open-issues file with `tempfile.mkstemp(suffix=".json")` and never removes it. No unlink or finally exists in the function, so each tick that reaches it leaves one small file in the temp dir. Add a `finally: os.unlink(tmp)`. The leak is bounded and no check pins it, so I do not block on it.
- tools/audit/seat/orchestrator_tick.py:2411 (non-blocking): `gh issue list --limit 500` truncates silently, so an open-issue list longer than 500 would pass as complete. It is not reachable at the current issue count.
- No other defect found. The diff reads clean: the call placement, the argv order (`--roster-ref REF roster --open-issues FILE`) and the rc/summary/OSError UNREADABLE guards all match the PR's stated intent.

## Evidence
- Setup: `cloud-setup.sh --check` printed `OK python3 is /opt/hpo/venv-ci/bin/python3`. The diff is 5 files, +144/-1, no production line outside the three seat tools. VERSION, the manifest version and the notes heading are untouched.
- Self-tests at 3447a165: orchestrator_tick `292 checks, 0 failed`; roster_edit `243 checks, 0 failed`; roster_sync `96 checks, 0 failed`; r10_roster_ops_mutants `343 checks, 0 failed`.
- Mutation proof, `r10_roster_ops_mutants.py U1 U2 U3 U4 U5 U6 W18`: U1 `rc=1 fails=3`; U2-U6 and W18 `rc=1 fails=1` each; `plants: 7, without a FAIL line: none`. No plant survived.
- `r10_roster_sync_mutants.py M9_carry_dedupe_dropped`: `RESULT mutant=M9_carry_dedupe_dropped rc=1 fails=1`. The pin for M9 kills it.
- Null control: the PR body reports U1-U6 surviving at the previous code head and a clean-roster row. I did not re-run the previous head; I confirmed the clean-roster row passes in the tick self-test.
- Claim files are untouched in this diff, since it changes only seat tooling. I did not run env_drift. There is no CI for this commit, so I skipped CI classification and the body-figure checks that need CI.
