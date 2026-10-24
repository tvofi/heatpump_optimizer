O11 (round 10, part of #201; tvofi's request 2026-10-18): carry-forward made mechanical. `finding-propagation.md` required every finding to reach an owner and nothing enforced it; the round-10 sweep found 39 of 95 findings with no owner.

What it fixes:

- Every finding item a body or a `Fix review:` verdict records ends with `Carry: <GROUP>|#<issue>|O<n>|dismissed: <reason>`, per `dev/governance/rules/finding-propagation.md` (Enforcement) and the PR template's `## Forward-carry` and `## Friction` lines.
- `tools/audit/carry_audit.py` is the one parser of the marker. It refuses an item with no marker and an item whose destination is gone or done: a group the roster does not hold or holds as done, an issue no live group, carry file or O-brief owns, an O-brief that does not exist, a bare `dismissed:`. An item may be routed from elsewhere by `Carry: <dest> (item <id>)`; the id counts only inside that marker's segment, and a `Carry:` in a code span is an example. `sweep` adds three reads: open issues nothing owns, roster refs that disagree on a carry, and orchestrator-ledger `FINDING:`/`LESSON:` lines without a marker.
- Wiring: `pr-contract` runs the check on the body in its last step; `queue_pre_flight.py` gains a `findings` step that PARKs a PR whose notes would merge unowned; `governance.yml`'s `instrument-self-tests` runs both self-tests; `.github/CODEOWNERS` owns the file.
- `dev/audit/harnesses/r10_carry_parser_mutants.py` drives the whole parser. It reads every predicate site from the file's AST, generates one mutant per site, regex alternative and `CARRY_SECTIONS` element, and refuses a site no mutant reaches or a survivor without a written reason. Predicates no input separates were deleted rather than pinned.

## Head

The PR head is `519bb4db971b5d49736fcacdd57d57bff8f6c630`. The code head is `74201dd56bec5ed4b98a09557c1569f0c4e6a13a`, on `handoff/r10-carry-enforce`; the authored commits are `8c666c644` and `6f20f78a3` on top of the earlier rounds, and all later commits on the branch are merges of origin/main. The figures below were taken at `74201dd56`. `e23fa9886` and `519bb4db9` merge origin/main and the handoff head with no resolution (each has exactly the tree `git merge-tree --write-tree` of its parents gives). Two earlier merges were resolved by hand: `a945bb62e` (the three `finding-propagation` rule files, kept main's #2408 wording and this PR's marker paragraph, re-cut to the cap with no raise) and `74201dd56` (`queue_pre_flight.py`, kept main's `raise_hold` step and this PR's `findings` step).

## Mutation proof

`python3 dev/audit/harnesses/r10_carry_parser_mutants.py` applies each mutant to `carry_audit.py` alone, runs the self-test and restores the file. Each boundary is killed alone: M15b (the segment's line-end cut dropped), M16 (the next-`Carry:` cut dropped), M14 (paren form dropped), M15 (segment scope dropped), M13 (code-span skip removed), and the item-ref routing arms R-extend, A-extend and A-union. M10, the `findings_gate` call deleted from `PreFlight.entry`, turns 4 `queue_pre_flight` checks red. One mutant is equivalent: S-span-lo, because a span opens on a backtick, so no `Carry:` starts at a span's first offset.

## Null control

- M0, the file unmutated: `RESULT mutant=M0 failed=0 verdict=baseline`.
- With M16's grammar row deleted, the self-test passes under M16: 0 failed. Likewise M15b with its row deleted. Each row is what kills its mutant.
- With M16 left out of the mutant list the census prints three sites UNMAPPED; with M15b left out, two.
- A planted body with one unrouted Friction finding refuses. With `Carry: R10-LIVE` it passes. With `Carry: R10-INVENTED` it reads as a bad destination.
- The roster-drift read with the same ref twice prints no `ROSTER-DRIFT` line; with `64b1f82a3` against `b29cd8d23` it prints 6.

## Figures

All taken at `74201dd56bec5ed4b98a09557c1569f0c4e6a13a`, origin/main `fa16596c3438ba7010a19138d293d4b6a4379375`, 2026-10-19 05:05 UTC.

- `python3 dev/audit/harnesses/r10_carry_parser_mutants.py`: `RESULT sites=152 unmapped=0 mutants=190 survived=0`.
- `python3 -I tools/audit/carry_audit.py --self-test`: `carry_audit self-test: 144 checks, 0 failed`.
- `python3 tools/audit/seat/queue_pre_flight.py --self-test`: `queue_pre_flight self-test: 41 checks, 0 failed`.
- `python3 tools/audit/seat/merge_train.py --self-test`: `merge_train self-test: 189 checks, 0 failed`.
- `python3 dev/audit/harnesses/r10_carry_sweep_rows.py rows39`: `RESULT rows_caught=33 of=33`. These are the sweep's UNCARRIED rows that live in PR text.
- `python3 dev/audit/harnesses/r10_carry_sweep_rows.py last20`: `RESULT rows_caught=34 of=35` and `RESULT last20_hits=76 on_a_row=46 on_no_row=30`. The harness prints each hit that is on no row.
- `python3 -I tools/audit/carry_audit.py --roster-ref origin/main sweep --issues`: 4 `ISSUE-UNOWNED` (#2429, #2428, #2409, #2265). None is this PR's: the list follows main's roster and open issues, which moved since the last take.
- `python3 -I tools/audit/carry_audit.py --roster-ref 64b1f82a3 --roster-ref b29cd8d23 sweep`: 6 `ROSTER-DRIFT`. With `b29cd8d23` given twice: 0.
- `python3 -I dev/audit/rounds/round6/D11/fix/codeowners_gap.py --check`: `RESULT uncovered_files=0 count`.
- `node tools/policy/field_coverage.mjs`: `FIELD COVERAGE ok` (`refused=0`, `dead=0`).
- `node tools/policy/agreement.mjs --only discovery`: `RESULT divergent=0 unregistered=0 dead=0 refused=0`.
- `python3 tools/pr/ci_predict.py --base origin/main --apply-inert`: `CI PREDICT: no closures or fast red predicted against 06c6f3cf2589`. The inert entry for `dev/audit/harnesses/r10_carry_parser_mutants.py` is already in the tree, so nothing is applied.
- `node tools/policy/policy_lint.mjs`: `TOTAL: 0 error(s) across 41 policy file(s)`.
- `node tools/policy/rules_sync.mjs --check`: `RULES-SYNC ok`.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`.
- `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir D`: `MODE: SCOPED -- 3 script(s) run` (`tests/entities.py`, `tests/harness_headers.py`, `tests/layout.py`). Results: `ALL 2349 ENTITY CHECKS PASSED` (with `env -u BASH_ENV`), `ALL 109 HARNESS HEADER CHECKS PASSED`, `layout self-test: ok`. The `run_always` lines add `python3 tests/closure.py selftest`: `ALL 124 closure shrink pins PASSED`, and `python3 tests/env_drift.py --claims-only fa16596c3438ba7010a19138d293d4b6a4379375`: `claims hygiene: fa16596c3438ba7010a19138d293d4b6a4379375 ok`.
- `python3 -I tools/policy/agreement_py.py --out J` then `node tools/policy/agreement.mjs --py-json J`: `RESULT divergent=0 unregistered=0 dead=0 refused=0`. `node tools/policy/agreement.mjs --self-test`: `SELF-TEST 27 of 27 probes held`.
- `python3 -I -S tests/delivery_status.py --check`: `DELIVERY STATUS OK` with `0 overdue`.

## Red checks

Every red or cancelled run in the commit check-runs API, read for each of the 35 commits `git log origin/main..origin/fix/r10-carry-enforce` lists. The commits not named here carry no failure. The head `519bb4db9` has one run in progress (`composed-proof`) and none red.

- `7167a97d9`: `pr-contract` 117680912578 and 117681016244 (`UNROUTED body item cb97c3b2`). The cause: a quoted `Carry: ...` earlier on a line was matched to the line end, swallowing the real marker after it. The same cause reddened `pr-contract` 117682018192 at `713182ca1`. Fixed in `faf1bf1b1`: each segment is cut at the next `Carry:`; M16 pins that cut (added in a later round). Cheaper detector: the self-test row, which no fixture held before. The eleven runs there concluded `cancelled` (closures, coverage, fast, CodeQL and others) were superseded by the next push, not failures.
- `713182ca1`: `fast (3.14)` 117682154858 (`tests/harness_headers.py` refused `r10_carry_sweep_rows.py:33: ROOT = Path(__file__).resolve().parents[3]`). Fixed: the harness inlines `repo_root`. Cheaper detector: none, the census runs only in the full harness script, which prepr leaves to CI. `pr-contract` 117690102107 on the same commit refused the body because this red was not named in `## Red checks`; this section is the answer.
- `03f1681a3`: `wave-script` 117830428629 and `delivery-status` 117830428746 were main's reds, not this PR's. The agreement lane saw two custom merge subjects (`Merge pull request #2401 (R10-ARCHSCORE-COVERAGE p5)`, `#2379 (R10-SENSOR-PAYLOAD)`) that the readers did not parse alike; #2423 and #2424 gave the readers one grammar. `delivery-status` listed overdue record rows #2413, #2412 and #2407, which #2420 landed. This PR's `governance.yml` hunk is in `instrument-self-tests`, and `tests/delivery_status.py` names `governance.yml` only in comments. Cleared by the main merge: at later heads the agreement lane prints `divergent=0` and `delivery_status` prints 0 overdue. The cheaper detector is the lane itself. `pr-contract` 117830603406 there refused the body for not naming those two.
- `b419463b1`: `pr-contract` 117865632672, `BAD-DEST body item 5978f947: R10-OPENPR-SILENT is not a group of the roster`. The cause: the carry pointed at a group that existed only on `handoff/audit-r10-roster`, while `pr-contract` reads the tree's roster, and I had run `carry_audit.py check` against the roster branch. #2417 landed the roster on main; the head merges it, and `carry_audit.py --roster-ref origin/main check --body` now prints `6 routed, 0 unrouted, 0 bad destination(s)`. The cheaper detector is that same command run with the tree's roster ref before any body edit, about one second; `prepr.sh` did not run it against `origin/main`'s roster, which is the gap.

## Forward-carry

- `tools/audit/seat/orchestrator_tick.py`: the weekly and closure carry sweep. It runs `carry_audit.py sweep --last N --issues` with both roster refs, prints a dispatch line when the sweep exits 1, and has a self-test arm with its null control. Its precondition is this PR merged. R10-TICK-DRIVERS merged as #2390 without it, so the carry went to R10-OPENPR-SILENT, which owns `orchestrator_tick.py`; #2422 delivered `carry_sweep` there (merged `7ab3030b`), and it goes live when this PR merges. Carry: dismissed: delivered by #2422 (7ab3030b); orchestrator_tick.carry_sweep goes live when this PR merges
- `dev/governance/rules/finding-propagation.md`: the marker also binds a finding the orchestrator records in its own ledger, written `FINDING: ... Carry: ...`, which the sweep's `--ledger` read keys on. The sentence does not fit under the file's cap. Carry: O10-policy-fixer-md

## Friction

- finding-propagation.md: cost: the file sits at its cap after #2408, so the marker paragraph is paid for by prose cuts in the same file (100 lines, cap 101; `policy_lint.mjs` prints `TOTAL: 0 error(s)`), with no raise. Carry: dismissed: paid in this diff
- fix-review.md: unenforced: the reviewer's contract has no headroom left, so it does not name the marker; finding-propagation.md binds reviewers, as it binds every seat. Carry: O10-policy-fixer-md
- finding-propagation.md: cost: the marker's reading rules (an id counts only inside its marker's segment, a code-span `Carry:` is an example, every marker naming an item adds its destinations) are written in `carry_audit.py`'s docstring, not in the rule, which is at its cap. Carry: O10-policy-fixer-md
- carry_audit.py: unenforced: the destination check reads the roster's stage, which lags a merge (R10-TICK-DRIVERS read `not-started` after #2390 merged), so a carry to a merged group passes. It should also read the group's merged PR, from its delivery row or a `gh` read as the issue arm does. Carry: O10-policy-fixer-md
- carry_audit.py: stale: round 3's note on the `if ds else []` guard (review 6253086887) names a guard that this diff deletes. Carry: dismissed: guard deleted in this diff (item 7321e737)

## Approval

This PR changes policy, so tvofi's approving review at the head is owed before merge. The policy files are `dev/governance/rules/finding-propagation.md` (with its generated `.claude/rules/` and `.cursor/rules/` copies) and `.github/PULL_REQUEST_TEMPLATE.md`. The code-owned files are `.github/workflows/pr-contract.yml`, `.github/workflows/governance.yml`, `tests/layout.json`, and `.github/CODEOWNERS`, which now names `tools/audit/carry_audit.py`. No `*_budgets.json` row changes.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
