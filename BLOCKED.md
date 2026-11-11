# BLOCKED: R10-HOTFIX-RESTORE-BASE-SKEW

Question: May this group land in two pull requests, the grader admission e8d0311b2f first (alone, onto main) and then the workflow fix 4f9fc83dc7+5ab1c861c8+033d619595 rebased onto it? Or does the owner rule that this PR merges with the two base-graded reds below, which are predicted and cannot be repaired from this branch?

## Why it cannot go green as one pull request

The fix changes every restore site's `PINNED:` value. For example:

    PINNED: ${{ inputs.restore_source || github.event.pull_request.base.sha || ... }}

The new first alternative is the merge commit's first parent, which ci.yml's prelude resolves once per run. Two pinned graders read these lines against exact-form allowlists, and CI runs both from the BASE's copy:

- `dev/audit/rounds/round6/D11/fix/codeowners_gap.py --check` (`PINNED_OK`, `_bad_pinned`). It runs in governance `policy-docs` and is restored from the base there.
- `tools/pr/prepr.sh` step "pinned graders" (the `PIN_AWK` pinstyle regexes). It runs in pr-contract and is restored from the base there.

Measured at 033d619595:
- main's `codeowners_gap.py` on the head's workflows prints `RESULT uncovered_files=19` and `REFUSED`.
- At origin/main dbd1ab5b07 the same command prints `RESULT uncovered_files=0`.
- With the head's own `codeowners_gap.py` (commit e8d0311b2f, which admits the resolver prefix ahead of any admitted form) it prints `RESULT uncovered_files=0` and `SELF-TEST: 58 probe(s), 17 null(s), 0 wrong`.
- Mutating that admission back to the exact-set test prints `uncovered_files=19` and `2 wrong`.

So on this PR's own run, the base's graders refuse it until e8d0311b2f is on main. e8d0311b2f alone only admits additional forms, which no workflow on main uses yet, so it is inert on main.

## State of the fix (on this ref)

- Replay of PR 3424's merge, `dev/audit/harnesses/r10_restore_base_skew.py`:
  - old source d08ed31049: `RESULT exit=1`, `RESULT attributeerror=True`, with "3 file(s) differ", the same as job log line 8819;
  - the head's resolver: `RESULT source=c620ebba96...`, `RESULT exit=0`, `RESULT attributeerror=False`;
  - the workflows at origin/main: `RESULT source=none`, so the defect remains;
  - fresh-base null control: identical under both sources;
  - an event base newer than the merge parent: the resolver prints FAIL.
- `tests/entities.py` at 5ab1c861c8: `ALL 2709 ENTITY CHECKS PASSED`. With pr-contract's site reverted, it fails only the new barrier check (`pr-contract.yml:pr-contract restores from BASESHA`).
- `tests/structure.py`: `STRUCTURE RATCHET PASSED`.
- `ci_predict.py --apply-inert`: no red predicted.
- Not yet re-taken at 033d619595: entities.py and the prepr.sh body check.

Draft body: the `## Head` and the figures still name 5ab1c861c8, and `## Red checks` does not yet name the two base-graded reds.
