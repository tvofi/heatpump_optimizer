Fix review: merge 708e4679ec512068c69d1f34145b379823c488da

bus-nonce: 3082e2f222540589af92539907307e47

## Summary

This is review round 5 of PR #2968 (group R10-SAV-ACTUATION), after the minimal re-cut. Round 4 blocked `f41e5a5f4` as mutation-vacuous. That block is cleared at this head:

- `supply_tick`'s new-step guard (`pump_arbiter.py:1243`) is now killed by a named test, and I reproduced the kill.
- The ledger pin now names the file that actually kills it, `tests/features.py`.

The production diff has not changed since round 4. The delta f41e5a5f..708e4679 has two branch-only commits, `ee74febe6` (tests/features.py +46) and `e401ef65e` (one ledger row), plus two clean merges.

One thing still has to happen before the train merges this. The required `gate` check is red at this head because `codeql / Analyze (python)` was cancelled at its 45-minute timeout. That leg needs a rerun and the gate needs to go green (see Findings).

## Findings

- The required `gate` check (run 124255886403) is red at this head. Its only FAIL is `codeql / Analyze (python): cancelled (this run)`.
  - That leg (run 124231070581) ran from 18:11:19 to 18:56:29 UTC, 45:10, so it hit `codeql.yml`'s `timeout-minutes: 45`. The workflow's own comment records the same runner-load cancellation three times on 2026-10-20.
  - This round's diff adds a test and a ledger row, which CodeQL's python leg does not take meaningfully longer to analyse. I read this as an infrastructure transient, not a defect in this PR.
  - The body does not name it. It still describes round 4, before this run existed.
  - No rerun appeared in 20 minutes of polling, to 19:26 UTC (`ev/rerun_poll.txt`). Gate-sweep reruns only a red `gate` once a run's own gate is green, so it does not rerun a cancelled CodeQL leg.
  - Root-cause classes are not postable yet: `pr-contract` (19:02:04, success) started before `gate` concluded red (19:03:25).
  - Owed before the merge: rerun the CodeQL python leg so `gate` goes green, or name the timeout as a transient under `## Red checks`. Carry: R10-SAV-ACTUATION
- The body does not describe this head's own change. Round 4 raised the same point.
  - `## Re-cut`, `## Mutation proof`, `## Figures` and `## Unpinned sites` still describe `343f2abcf`: mutant R3, 4621 checks, "No pin is owed".
  - Only `## Head` names `e401ef65e` and `708e4679e`.
  - The mid-step guard check, its GUARD_OFF mutation proof, the null control and the ledger re-pin from `tests/harness_headers.py` to `tests/features.py` are not stated anywhere in the body.
  - `fixer.md` step 7 requires every executed number at the head. The figures below re-derive them, so this does not block. Carry: R10-SAV-ACTUATION
- The re-pinned row's `reason` says GUARD_OFF took `tests/features.py` to `failed=3`. At this head I measured `2 of 4624`: the new check and its null control. The `killed_by` file is correct, and CI's re-verification reproduces it. I did not establish where the third failure came from; it may be a count taken at `e401ef65e` before the main merge. Carry: dismissed: the reason string is narrative, the killer and the kill reproduce at the head
- The duty-ledger residue from earlier rounds is unchanged: the first reading of an OFF step after an ON step is booked from the previous step's tail. The body routes it to #2492, and this PR says `Refs`. Carry: #2492

## Evidence

- RESULT head-measured 708e4679ec512068c69d1f34145b379823c488da (`ev/HEAD.txt`). `git ls-remote` still printed it as the branch head at 19:26 UTC.
- The roles diff since the merge base is empty, so the contract is current. Merge base and origin/main are both `cc930cdd1`.
- RESULT delta. `review_carry.py f41e5a5f4 HEAD` prints FRESH-REVIEW, because of the two code-carrying branch-only commits `ee74febe6` and `e401ef65e` (`ev/review_carry.txt`).
  - The branch's production diff (`custom_components/`, three-dot against each merge base) is identical at `f41e5a5f4` and at this head.
  - `git show --remerge-diff` is empty for both merges `cbbdf6ae1` and `708e4679e`, so neither carries a hand resolution.
- RESULT NULL: `PYTHONPATH=tests/hastub python3 tests/features.py` at the head prints `ALL 4624 FEATURE CHECKS PASSED`, rc=0 (`ev/features_head.log`).
- RESULT GUARD_OFF at `pump_arbiter.py:1243`: `if held.supply is None or held.supply[0] == step:` becomes `if False:` in a separate copy of the head tree (`ev/mutant_GUARD_OFF.diff`).
  - `tests/features.py` prints `2 of 4624 FEATURE CHECKS FAILED`, rc=1 (`ev/features_GUARD_OFF.log`). It fails on exactly two checks:
    - `FAIL the step tick writes nothing inside a step whose boost starts mid-step [{'07:00': ['turn_off'], '07:06': ['turn_on'], '07:10': [], '07:15': []}]`
    - `FAIL null control: the same tick at the next boundary writes the boost's ON [...]`
  - The mutant writes the boost's ON mid-step at 07:06, and then nothing at the 07:15 boundary. That is exactly the behaviour the guard prevents. Unmutated, the null control writes `['turn_on']` at 07:15, so the empty mid-step writes come from the guard and not from a tick that never fired.
- RESULT harness_headers under GUARD_OFF: `ALL 112 HARNESS HEADER CHECKS PASSED`, rc=0 (`ev/harness_headers_GUARD_OFF.log`). This confirms the old pin to `tests/harness_headers.py` was false and the new one is right.
- RESULT CI pin re-verification (`tests / mutation`, run 124231070335, `ev/ci_mutation_log_excerpt.txt`):
  - `PIN RE-VERIFICATION: 8 reproduced, 0 not reproduced`.
  - `ok pump_arbiter.py:1243 GUARD_OFF -- killed by tests/features.py`.
  - `0 survivor(s) of 8 evaluated`, then `MUTATION TABLE PASSED`.
  - Round 4's `PIN NOT REPRODUCED` line is gone.
- No round-4-accepted finding regressed. Production code is byte-identical, and round 4's kills on R1, R3 and R4 rest on checks that stay `ok` in the 4624-check head run. CI re-verified the other pins on this PR's sites: `coordinator.py:7525` GUARD_OFF/BOOLOP, `pump_arbiter.py:377` BOOLOP and `:1222` GUARD_OFF, and `thermal_model.py:1320` and `:1323`.
- RESULT merge: `git merge-tree --write-tree origin/main HEAD` rc=0, tree `b8b5fed15a59`. There is no conflict and no MERGE-CLAIM line (`ev/merge_tree.txt`).
- RESULT version and claims: `VERSION`, `manifest.json`, `RELEASE_NOTES.md` and both claim files are untouched three-dot.
- RESULT structure: `python3 tests/structure.py` prints `STRUCTURE RATCHET PASSED`.
- RESULT CI at the head, read from the check-runs API at 19:05 UTC once every run had concluded (`ev/check_runs.txt`):
  - Success: fast (3.14), closures, coverage, coverage-ratchet, arch-instrument, instrument-self-tests, typing, replay, browser, lane-proofs, graders-head-copy, briefs, closure-scope, mutation, arch-score, budget-raise-gate, env-matrix, policy-docs, wave-script, delivery-status, nightly-status, hassfest, validate-hacs, prelude, pr-contract, and codeql actions and javascript-typescript.
  - Red: `gate` only, from the cancelled `codeql / Analyze (python)` (`ev/gate_log_excerpt.txt`; see Findings).
  - The CI workflow run 41104632649 concluded `cancelled`.
- Review packet: rendered locally (`ev/review-packet.md`). No refusals and no advisories. carry_audit routed 2 of 2. figure_lint resolved 7 of 7. No finder harness is named; earlier rounds disclosed the phase harness as the fixer's own build. I did not re-run it, because production code is unchanged since round 3.
- Not re-derived: the body's figures for `343f2abcf` (4621 checks, R3 at 2 of 4621, the 28-script scoped gate, `ci_predict` output). Round 4's reviewer re-took R3 on the same production code.
- Scope: as the brief directs, this round opened no new scope beyond the delta and the round-4 block.
