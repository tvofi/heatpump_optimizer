Fix review: blocked 04efeb4a8e175392acb0f780252ad177ccaef9ed ci-cancelled: code run 42525346328 at this head was cancelled before concluding, so gate is red with no verdict on the code; every point of the prior block is closed

bus-nonce: c42a6a620b10cfb59ed1c02f2ec5e166

Round 2 (delta review of the repair to verdict/3342's block at 88690628b6feb50266cdcdb175b2a9c293db472a). Measured head 04efeb4a8e175392acb0f780252ad177ccaef9ed; merge base daf8b349fd30cc60786eeca333a426b693aa4c5f, which is origin/main's tip. ls-remote shows the head unchanged at verdict time (21:53Z).

## Block

- CI on this head has not concluded. `merge_train.py classify 04efeb4a8e175392acb0f780252ad177ccaef9ed --pr 3342` gives `RED 04efeb4a8e175392acb0f780252ad177ccaef9ed pending: none red: gate`, rc 1, on two reads (21:52:52Z, 21:53:44Z). Run 42525346328 ("CI code pr=3342") is the only code run on this head, and its conclusion is `cancelled`. At 21:48:53-57Z its gate, closures, fast (3.14), coverage, governance / instrument-self-tests, ci-ratchet, coverage-ratchet, lane-proofs, graders-head-copy, claims-autofix and closures-autofix jobs were all cancelled mid-flight. No newer run exists on the branch. The two edit runs' `gate` failures (42525346240, 42525470299) both print only `FAIL run(s) [42525346328] at this head are still being judged; their gate decides`. So the red is a cancelled run, not a failure in this diff, and no root-cause answer is owed for it: no check concluded `failure` on its own merits. The head cannot be judged GREEN either: a red CI never carries. Remedy: re-run 42525346328 (or re-dispatch CI on this head) with no code change. On green, this review's code findings stand, because every one of them is in ## Evidence and none depends on CI. A re-review of the same head then needs only the classify line.
  Carry: built-here

## Findings

## Evidence

- Prior block item (T6, the `rc not in (0, 1) or not summary` guard set to `if False:`): CLOSED. My own hand mutant at this head gives `RESULT mutant=T6 rc=1 fails=3`, failing "exit 2 with no summary (a REFUSED roster ref) is one UNREADABLE line", "exit 2 with a summary is still UNREADABLE (the rc arm alone)" and "exit 0 with no summary is UNREADABLE (the summary arm alone)" (ev/reviewer-mutants.txt).
- Prior block item (T8, `except OSError` replaced by `except ZeroDivisionError: return`): CLOSED. `RESULT mutant=T8 rc=1 fails=1` fails "an OSError from the tool is one UNREADABLE line naming it".
- Prior suggestion (the non-JSON `gh issue list` path): CLOSED. My T10 (ValueError still appends `--open-issues`) gives rc=1 fails=1.
- Extra reviewer mutants, all killed: T1 (call removed) fails=8, T9 (UNREADABLE line dropped on the rc arm) fails=3, T11 (rc set widened to (0, 1, 2)) fails=1, T12 (OSError re-raised) fails=1. Unmutated, and after restore: `orchestrator_tick self-test: 292 checks, 0 failed`, the same under `-I` and under `PYTHONPATH=tests/hastub`.
- Fixer's in-tree plants re-run: `r10_roster_ops_mutants.py U1 U2 U3 U4 U5 U6 W18` gives U1 rc=1 fails=3, U2-U6 and W18 rc=1 fails=1 each, `plants: 7, without a FAIL line: none`. These match the body's figures. Harness self-test: 343 checks, 0 failed (ev/plants.txt).
- The body's null control was re-run. At e3d39d0d5c55eca3aa442765f6ef69f7d7ad51b6 with this head's harness copied in, U1-U6 are all `rc=0 fails=0`, `without a FAIL line: ['U1', ... 'U6']`. The new rows are what kill them (ev/null-oldhead.txt).
- My own null on the harness fix (cddc8988f): with `fail_lines` reverted to unindented-only, its self-test fails "an indented FAIL line is read; an ok line naming FAIL is not", and U4 reads `fails=0` with the FAIL only in the crash tail. So the indentation fix is load-bearing, as the body claims (ev/runner-null.txt).
- Delta scope: the three-dot diff at this head against the one reviewed at 88690628 differs only in the tick self-test rows and `r10_roster_ops_mutants.py` (U1-U6, `fail_lines`, its self-test row) (ev/interdiff-vs-88690628.txt). Non-merge commits since 88690628: 58f2f02b6 and cddc8988f only. No production line changed; the `roster_invariants` method is byte-identical.
- The three-dot diff touches 5 files: dev/programme/delivery/3342.md, orchestrator_tick.py, r10_roster_ops_mutants.py, roster_edit.py and roster_sync.py. VERSION, the manifest, RELEASE_NOTES.md and every `*_budgets.json` are untouched.
- Merge: `git merge-tree --write-tree origin/main 04efeb4a8e175392acb0f780252ad177ccaef9ed` gives rc 0, tree ca382e82f612e999f6b2439ec4f6888e6dd2cdeb, no conflict (ev/merge-tree.txt).
- Role contract current: `git diff $(merge-base)...origin/main -- dev/governance/roles/` is empty.
- `PYTHONPATH=tests/hastub python3 tests/entities.py` was run plainly (no BASH_ENV workaround) and was clean: `ALL 2668 ENTITY CHECKS PASSED`, rc 0 (ev/entities-tail.txt).
- `python3 tests/structure.py`: STRUCTURE RATCHET PASSED, rc 0 (ev/structure.txt).
- PR body: `## Head` names 04efeb4a8e175392acb0f780252ad177ccaef9ed, the head measured. `## Red checks` says "none". No check on this head concluded `failure` on its own, only the cancellation-induced gate reds above, which a re-run settles. The delivery row dev/programme/delivery/3342.md is present and reads "open".
- Other concluded checks on this head: arch-score, budget-raise-gate, CodeQL, codeql analyses, hassfest, validate-hacs, governance policy-docs/env-matrix/wave-script/delivery-status, tests briefs/closure-scope/mutation/browser/typing/arch-instrument and nightly-status all succeeded. Run 42525346328's other jobs are cancelled, as listed in the Block.
- The figures in the body's ## Figures (self-tests 0 failed, STRUCTURE RATCHET PASSED, entities ALL PASSED) were re-derived above. The body's `closure.py select` MODE line was not re-run by me.
- Self-audit: `python3 -I tools/audit/carry_audit.py check --body <PR body> --comments <this verdict>` gives `CARRY-AUDIT: 0 finding item(s): 0 routed, 0 unrouted, 0 bad destination(s)`, rc 0. The brief's path `tools/audit/seat/carry_audit.py` does not exist at this head, and its single-argument form requires `--body`.
