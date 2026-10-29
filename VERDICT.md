Fix review: blocked 3d3d7edd16bb4e291e865973be64e378d49c72fa carry-missing: not carried to R10-FLY-LEDGER-SAMPLE

bus-nonce: 8658c12df550feca44941bcf90172035

## Round

Round 1 (first fix review of #2961).

## Block

fix-review.md step 10 and finding-propagation.md "Enforcement": the producing PR does not merge until a roster carry is in the tree on `handoff/audit-r10-roster`, and the body names that branch SHA. The body's `## Forward-carry` says countermeasure C (mutation-autofix reddens when an added site is left alive; acceptance red on #2817's `4fbe4c6a5` shape `N pinned, 2 left unpinned`, green on `0 left unpinned`, quiet on `skip-head-moved`) "Lands in `dev/programme/rosters/wave-r10-groups.json`, group `R10-FLY-LEDGER-SAMPLE`'s `carry`", but it names no roster SHA, and the carry is not there: group `R10-FLY-LEDGER-SAMPLE`'s `carry` at `origin/main` 279578074 and at `handoff/audit-r10-roster` e9e3f93d279a1c4c6a53086cacafacdfb28442bd holds only the #2712 item and the #2840 measure-first item. No origin ref has a roster with that text in it (`2 left unpinned`). Right now C exists only in this PR's body and in its own record (`dev/audit/rca/R10-RCA-MUTATION-SURVIVOR.md` section 7). The record does not count as propagation. Fix: write C with its control and acceptance into the group's roster entry through `roster_edit.py` on `handoff/audit-r10-roster`, read it back with `brief_lint.mjs`, and cite the branch SHA in the body. Evidence: ev/roster-carry.txt.

## Findings

- The PR's own roster group `R10-FRICTION-MUTATION-SURVIVOR` holds a carry, added 2026-10-29T03:55 (9fbc902ca), before the PR opened at 17:32Z: "`reviewer-head-off` survives `r10_flow_dispatch_mutants.py` ... `dispatch_group`'s \"a reviewer needs --head\" refusal is not pinned by the self-test". The body neither settles it nor dispositions it. It is a `tools/` hand-mutant survivor, the same population the record files under #2579/#2820 with "recorded, nothing built", so either count it in the record or give it its own disposition. Carry: R10-FRICTION-MUTATION-SURVIVOR
- Issue #2942 ("recurring friction: mutation (family)", window v7.0.5..origin/main) was wired into this group's `issues` at 2026-10-29T17:05 (11d198e9e), before the PR opened. The body never names it, and the record's count is taken over the v7.0.4 window under the `mutation-survivor` key only. The family fold (survivor/vacuous/unpinned/untriaged) is exactly the vocabulary the body's last Friction item says it does not fold. #2942 needs its own disposition in the body (refute, fold into this cause, or defer with a destination). Carry: R10-FRICTION-MUTATION-SURVIVOR
- The rule rewording changes `claims-autofix` "reddens on nothing it can return today" to "never reddens". That is stronger than the code. Every status `apply_inherited_claims` returns is in `AUTOFIX_QUIET["claims-autofix"]`, but the job can still go red on a crash, a push failure or a status added later, and "today" carried exactly that hedge. It is a precision loss in a policy file and no seat is misdirected yet. Carry: dismissed: wording precision only; every returned status is quiet at this head (tests/env_drift.py apply_inherited_claims vs tests/closure.py AUTOFIX_QUIET), and the next ci-autofix.md edit can restore "today"

## Evidence

- RESULT: named cause verified in code at the head. `measurement()` (tests/mutation_table.py:1147) uses only group(1) of `PIN_SUMMARY` and discards the `left unpinned` count. `apply_pins()` (:1172) returns `changed` once any pin is added. `closure.AUTOFIX_QUIET["mutation-autofix"]` (tests/closure.py:2403) holds `changed` and `skip-nothing-killed`. So a run that leaves survivors is green on `mutation-autofix`, as the body says (ev/cause-code.txt).
- RESULT: merge with origin/main 279578074: `git merge-tree --write-tree` rc=0, tree c9c219cfff03aaa7767b41c977416419ec095ac3, no conflict and no MERGE-CLAIM line (ev/merge-tree.txt).
- RESULT: `policy_lint.mjs --budgets` `.claude/rules/ci-autofix.md` 1469 of 1469, which matches the body. `rules_sync.mjs --check` RULES-SYNC ok. The generated `.claude/` and `.cursor/` copies match their source.
- RESULT: VERSION, the manifest version and RELEASE_NOTES.md are untouched (three-dot name list, ev/cheap-checks.txt).
- Mutation proof: n/a as the body states. No production, test or check line lands, and `tests / mutation` is green with no production line changed, so it drew no mutant.
- Finder's harness: none is named, and none applies. This is a root-cause record, and its figures come from the scripts it commits under dev/audit/rca/mutation-survivor/.
- Figures not re-derived: the 4 PRs / 6 entries `--stats` count at 88c6ad5bb was still running when this verdict was written. The 28/285 window count, the 91/161/496 min intervals and the 366 runner-minutes were not re-derived. They are taken from the body and are unverified (fix-review.md step 8). figure_lint: 5 resolved, 4 unverified (git flags), 0 refused.
- Policy approval: ci-autofix.md is policy. The body cites the orchestrator's `all`-scope mandate from the group brief, which is the approving review's to confirm, not this seat's.
- CI at 3d3d7edd, read live from the check-runs API: `tests / nightly-status` is failure. It grades main's Nightly, and the diff touches nothing it reads, so it is not this PR's (defect-root-cause.md). The body answers it. Still in_progress when read: `tests / closures`, `tests / coverage`, `codeql / Analyze (python)`, `governance / instrument-self-tests`, `prelude`. Every other concluded run is success or skipped. No `pr-contract` or `gate` run was in the listing at read time. The red-check (step 11) verdict is not taken here, and this block does not depend on it.
- Head: the body's head 3d3d7edd16bb4e291e865973be64e378d49c72fa equals the PR head and the head measured (ev/HEAD.txt).
