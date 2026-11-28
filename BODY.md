R11-PRE-TOKEN-LEDGER part 1 residue. The group's carries 0-6 merged as #3906; this pull request adds one `check_scopes.ledger_round_self_test` arm pinning the closed lower bound of `ledger_unread`'s window (`a <= at(r["t"]) < b`). At origin/main the mutant `a <` survives every arm. The previous seat's BLOCKED.md (which return ref takes the arm) is decided by taking its recommended option: the head merges origin/main into that seat's ref, so `handoff/r11-pre-token-ledger` (closed #3898's head c892a81941) and `handoff-wip/r11-pre-token-ledger` both fast-forward, and BLOCKED.md is deleted. The code diff against main is that arm alone (`git diff origin/main...HEAD --stat`: `tools/audit/check_scopes.py`, 4 insertions).

Carries 0-6, each landed by #3906 (its body's carry list) and re-read at ac9045c223: 0, 1, 2 and 3 (`token_ledger.COLUMNS`, `round_metrics.token_line` reading `tokens.tsv`, `check_scopes --round`'s `ledger_gaps`), 4 (`cloud_dispatch.inherit_part`), 5 (the ledger reads transcripts, not the gh host log), 6 (`token_ledger.sessions()`). None is rebuilt here.

## Head

a600e05c2e7e370d30e3c3398183c11fe0b74273, merge base ac9045c223721608e684c8a2213831aa34c1fa4f (origin/main at the measurement, 2026-11-28 UTC).

## Mutation proof

Mutant: line `win = [r for r in rows if r.get("t") and a <= at(r["t"]) < b]` in `ledger_unread` changed to `a < at(r["t"]) < b` (that line alone, by `sed` on its line number; the same comparison in `ledger_gaps` untouched), bytecode caches cleared, `PYTHONDONTWRITEBYTECODE=1`, then `python3 -I tools/audit/check_scopes.py --repo . --self-test`:

- at origin/main ac9045c223: `SELF-TEST passed (every perturbed scope refused)`, rc 0: the mutant survives.
- at the head a600e05c2e: `SELF-TEST FAILED`, rc 1; the one false arm is `--round null: a seat class whose only row is at the window's first second is read`. Restored, the head prints `SELF-TEST passed`.

Diff mutants: `MUTANT_CMD="python3 -I tools/audit/check_scopes.py --repo . --self-test"`, `python3 tools/audit/seat/mutant_run.py --diff "$(git merge-base origin/main HEAD)...HEAD" --cmd "$MUTANT_CMD" --max-mutants 40 --in-place --report-only`, rc 0, one line: `SURVIVED tools/audit/check_scopes.py:1397 STMT_DEL  pass` (see `## Unpinned sites`).

## Null control

The unmutated head: the check_scopes self-test prints `SELF-TEST passed (every perturbed scope refused)`, rc 0, every ledger arm true. The new arm is itself a null arm: a class whose only row is at the window's first second returns no gap and no unread line.

## Figures

- check_scopes self-test: `python3 -I tools/audit/check_scopes.py --repo . --self-test` prints `SELF-TEST passed` at the head and at origin/main; under the mutant above it fails at the head only.
- structure ratchet: `python3 tests/structure.py` prints `STRUCTURE RATCHET PASSED`.
- scope: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"` prints `MODE: SCOPED`; no suite script's closure holds `tools/audit/check_scopes.py`, whose instrument self-test is the run above.

## Unpinned sites

- `tools/audit/check_scopes.py:1397` STMT_DEL of the new arm's own `arms[...] = ...` assignment: deleting an arm deletes the check, which no arm observes; the behaviour it pins is killed as shown under `## Mutation proof`. The same category #3906 recorded.

## Red checks

- `codeql / Analyze (javascript-typescript)` (job 139320652933, at b15a9f2c, a commit of closed #3898 this head inherits through `handoff/r11-pre-token-ledger`): the job log reads `Uploading results` at 15:54:11Z then `##[error]Server Error` at 15:54:45Z and `CodeQL job status was failure`, so it failed on GitHub's SARIF upload endpoint, not on a finding; neither b15a9f2c's diff nor this one changes JavaScript or TypeScript. No cheaper detector exists: a server error on the upload is not decidable before the upload runs, and the run at this head re-proves the job.

## Forward-carry

none

## Friction

- dispatch-stale-roster: stale: this dispatch (88df26976d) lists carries 0-6 as unbuilt and the roster row reads `stage: not-started`, while #3906 (merge 8f22a3b284) landed all seven; only the lower-bound arm was open. Carry: dismissed: roster_sync derives the stage from the merged pull request.
