Fix review: merge 3d3d7edd16bb4e291e865973be64e378d49c72fa

bus-nonce: 3a2c281a6daa94967ea9f8fcbffbfe36

## Round

Round 2. Round 1 (origin/verdict/2961) blocked on carry-missing for R10-FLY-LEDGER-SAMPLE. The head has not moved, and only the body changed.

## Findings

- Round 1's finding is still unsettled. The carry already on the PR's own roster group (`reviewer-head-off` survives `r10_flow_dispatch_mutants.py`, and `dispatch_group`'s "a reviewer needs --head" refusal is unpinned) is neither counted in the record nor given a disposition in the body. It is still in group R10-FRICTION-MUTATION-SURVIVOR's `carry` at roster tip 19acc911c. It is a `tools/` hand-mutant survivor, the population the record files under #2579/#2820. Carry: R10-FRICTION-MUTATION-SURVIVOR
- Round 1's finding is still unsettled. Issue #2942 (recurring friction: mutation family, window v7.0.5..) is in the group's `issues` at roster tip 19acc911c, and the body still does not name it. Record section 5 shows the family words share this cause, so #2942 needs a disposition: fold it in, refute it, or defer it with a destination. Carry: R10-FRICTION-MUTATION-SURVIVOR
- The ci-autofix.md rewording changes `claims-autofix` "reddens on nothing it can return today" to "never reddens". That is stronger than the code: the job can still go red on a crash or a push failure. This is a wording-precision issue only. Carry: dismissed: every status apply_inherited_claims returns is in AUTOFIX_QUIET at this head, so no seat is misdirected, and the next ci-autofix.md edit can restore "today"

## Evidence

- RESULT: forward-carry verified (step 10). `edd149d14059c2806cc1bf2ccbdbd817ce6ada05` ("roster_edit append-carry R10-FLY-LEDGER-SAMPLE") is on `origin/handoff/audit-r10-roster` and is an ancestor of the tip `19acc911c`. Group R10-FLY-LEDGER-SAMPLE's `carry` there holds "From #2961 (R10-FRICTION-MUTATION-SURVIVOR record), countermeasure C". That item states the same mechanism as the body's Forward-carry line: red when an added site is left alive, naming each site. It also states the same acceptance (red on the `N pinned, 2 left unpinned` shape at `4fbe4c6a5`, green on `0 left unpinned`, quiet on `skip-head-moved`) and the same answer to the group's #2840 carry. It states its control as a precondition: "Re-measure against your own merge base." brief_lint.mjs on the roster before and after edd149d14 gives the same 4 errors, all in other groups (R10-FLY-RELAY-TOOLS-LEVEL and others, a missing triage file), so the carry introduced none (ev/roster-carry.txt).
- RESULT: the named cause is verified in code at the head. `PIN_SUMMARY` (tests/mutation_table.py:1045) captures only N of `N pinned, M left unpinned`. `measurement()` returns `measured`/`skip-nothing-killed`, and `apply_pins()` returns `changed`. `AUTOFIX_QUIET["mutation-autofix"]` (tests/closure.py:2403) holds changed, skip-not-allowed, skip-not-unpinned, skip-nothing-killed and skip-head-moved (ev/cause-code.txt).
- RESULT: re-derived window figures at 88c6ad5bb: 285 first-parent merges in v7.0.4..88c6ad5bb, and 28 of them change `custom_components/*.py`. Both match the body.
- RESULT: `policy_lint.mjs --budgets`: `.claude/rules/ci-autofix.md` is 1468/1469 at 88c6ad5bb and 1469/1469 at the head, which matches the body. No budget file is in the diff. `rules_sync.mjs --check` passes: RULES-SYNC ok (ev/cheap-checks.txt).
- RESULT: VERSION, the manifest version, RELEASE_NOTES.md, the claim files, the structure budgets and closures are all untouched (the three-dot name list is in ev/cheap-checks.txt).
- RESULT: merge with origin/main e5ddba1fa: `git merge-tree --write-tree` rc=0, with no conflict and no MERGE-CLAIM line (ev/merge-tree.txt).
- Mutation proof: n/a, as the body says. No production, test or check line lands. `tests / mutation` is green, and the packet shows no mutation-ledger diff, so no mutant was drawn. No targeted mutant applies.
- Finder's harness: none is named, and none applies to a root-cause record. Its instruments are committed under dev/audit/rca/mutation-survivor/. I built no instrument of my own.
- Figure note (step 8). The body's Figures line says "5 PRs cite a key: #2632, #2817, #2832, #2912, and #2745's metric-gamed block". The committed `mutblocks.py` cannot print #2745, because its family filter excludes `metric-gamed`. I confirmed separately that #2745's metric-gamed block (2026-10-26T19:38Z) does cite `ledger.py:225 GUARD_OFF`. The record's section 5 "Five PRs" counts #2834, a non-verdict, instead. Both totals come to the same four mutation-verdict PRs that `mutblocks.tsv` holds, so the substance agrees and only the fifth item differs.
- Figures not re-derived, so they are unverified: the 4/6 `--stats` count (the run takes about 10 min, and the committed copy was read), the 91/161/496 min intervals, the 366 runner-minutes and the pinsbefore timelines.
- CI at 3d3d7edd, read live from the check-runs API (ev/check-runs.tsv): every run is completed, and all are success or skipped except `tests / nightly-status` (failure, 17:33:39Z). That job checks out the base's `tests/nightly_status.py` and grades main's scheduled Nightly. The diff touches nothing it reads, so it is main's red, not this PR's (defect-root-cause.md). The body answers it anyway. `pr-contract / pr-contract` started at 19:32:13Z, after the last red concluded, and is green. `gate` is green.
- Policy approval: ci-autofix.md is policy. The body cites the orchestrator's mandate (scope all), which the approving review has to confirm. That confirmation is not this seat's.
- Head: the body's head, the PR head and the measured head are all 3d3d7edd16bb4e291e865973be64e378d49c72fa (ev/HEAD.txt). It was re-read before return.
