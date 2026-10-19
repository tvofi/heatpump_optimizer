O11 (round 10, part of #201; tvofi's request 2026-10-18): carry-forward made mechanical. `finding-propagation.md` already required every finding to reach an owner, and nothing enforced that. The round-10 finding sweep found 39 of 95 findings with no owner. They were recorded in a body's `## Friction` or `## Forward-carry`, in a `Fix review:` verdict's non-blocking notes, in the orchestrator's ledger, or as an auto-filed issue that no group lists.

What lands:

- **The marker**, in `dev/governance/rules/finding-propagation.md` (Enforcement) and in the PR template's `## Forward-carry` and `## Friction` lines. Every finding item a body or verdict records ends with `Carry: <GROUP>|#<issue>|O<n>|dismissed: <reason>`.
- **`tools/audit/carry_audit.py`**, the one parser of the marker. It reads the finding items of a body and of the PR's `Fix review:` comments. It refuses an item with no marker, and an item whose destination is gone or done:
  - a group the roster does not hold, or holds as done;
  - an issue no live group, carry file or O-brief owns (with `gh` reads, also a closed issue);
  - an O-brief that does not exist;
  - a bare `dismissed:`.

  An item can also be routed from elsewhere by a marker that names it as `Carry: <dest> (item <id>)`. The id counts only inside that marker's own segment, which runs from the `Carry:` to the next `Carry:` or the line end. Every marker that names an item adds its destinations, and each must hold. A `Carry:` inside a code span is a quoted example, not a marker. A span closes as CommonMark closes one: on a backtick run of its own length, on the same line or a later line of the item. `sweep` adds three reads: every open issue nothing owns; carry or brief text one roster ref holds and another lacks; and every orchestrator-ledger line saying `FINDING:` or `LESSON:` that has no `Carry:`. `owners` is the sweep's owner search.
- **Wiring.**
  - `pr-contract` runs the check on the body, as the pull request's own copy, in the job's last step. `.github/CODEOWNERS` owns the file, as it owns `fold_ledger.py`. It is not pinned: a pinned grader must be declared in the pinned `field_coverage.mjs`, so the pull request that adds one cannot pass (#1847). Because it is the last step, nothing it writes to `$GITHUB_ENV` reaches a later step. `roster_lib.py`, which it imports, is restored from the base. In CI an O-brief passes, printed UNVERIFIED.
  - `tools/audit/seat/queue_pre_flight.py` gains a `findings` step, which the train's `--pre-flight` runs. It PARKs a PR whose notes would merge unowned.
  - `governance.yml`'s `instrument-self-tests` runs both self-tests.
- **`dev/audit/harnesses/r10_carry_parser_mutants.py`** is the mutation drive for the whole parser: `items()`, the marker grammar, the routing and the ledger key. It reads every predicate site from the file's AST. A site counts if it is a test, a boolean operand, a comparison, a slice, a cut or match call, a `continue` or `break`, or one of the parser's regex constants. It generates one mutant for each regex alternative and each `CARRY_SECTIONS` element, and runs each mutant alone against the self-test. It refuses a site no mutant reaches. It also refuses a mutant that survives, or one that kills only by crashing, unless `EQUIVALENT` gives a reason.

Alternatives considered:
- Pinning the parser's redundant predicates instead of deleting them lost. The sweep found predicates that no input separates: the CRLF normalisation, the blank-line `kind == "table"` arm, both section strips, the `verdict and` and inherited `kind == "bullet"` conjuncts, the lead's `rstrip`, the dismissed reason's second strip, and the `if ds else []` guard. A row that pinned one of these would pin dead code. Each was deleted instead, and the self-test and the drive pass without it.
- First-wins routing by reference lost to the union. Under first-wins, a second marker naming the same item with a bad destination passed silently. That rule also needed a `not r["dests"] and` conjunct that only one mutant could reach.
- A same-line code span lost to CommonMark's. A backticked example that crosses a line counted as a real marker, which fails open. The CommonMark span fails closed, as a loud refusal.
- Extending `policy_lint.mjs`'s `## Forward-carry` check lost. Python tools (`queue_pre_flight.py`, the tick) read the verdict comments and the sweep, so one Python parser serves all three callers.

After this merges, an open PR's `pr-contract` re-runs on its next push or body edit. It refuses an unrouted `## Friction` or `## Forward-carry` item until the body adds the item's `Carry:`.

## Head

`b419463b18a2a7da70c77b23e912769e4af6afe8` is the PR head. It merges origin/main `06c6f3cf2589cd37fa9fe56cc5ebeef709dc8d3b` and the recarry `bd68cf756ab63a475d37d30fcdf60b35d85a6214` into `03f1681a3e684854b5b934020ec5d44612b2ffd2`, with no conflict beyond the ledger driver's `tests/closures.json` row. The authored code head is unchanged: `6f20f78a3e1d8ae387cd227fa05131f0856ed6e3`, the authored commits `8c666c644` and `6f20f78a3`. Since `bd68cf756` the merges add main's own files only (#2390's tick drivers, #2423 and #2424's merge-subject guard, delivery rows), none of this PR's.

## Mutation proof

`python3 dev/audit/harnesses/r10_carry_parser_mutants.py` applies each mutant to `tools/audit/carry_audit.py` alone, runs the self-test, and restores the file byte for byte. It prints one `RESULT mutant=` line per mutant, with that mutant's FAIL lines. The two boundaries this round was blocked on are each killed alone:

- M15b, the segment's line-end cut dropped (`.split("\n", 1)[0]` removed). Red: `grammar: a segment ends at its line: an id on the next line routes nothing`.
- M16, the segment's next-`Carry:` cut dropped (`text[at:len(text)]`). Red: ``grammar: a segment ends at the next `Carry:`: its id is not the first marker's``.
- M14, the paren form dropped. Red: 3 checks, including ``a bare `item <id>` after a marker on its line routes nothing; only `(item <id>)` does``. M15, the segment scope dropped: red on 3 checks, including ``an `(item <id>)` outside the marker's segment, in the same paragraph, routes nothing``. M13, the code-span skip removed: red on 4 checks, including ``a backticked example `Carry:` in a finding's prose does not route it``.
- R-extend and A-extend, routing back to first-wins inside one item and across items. Red: `grammar: two markers naming one id in one item: each destination must hold` and `grammar: two items naming one id: each destination must hold`. A-union (`or` for `+`): red on `grammar: an item's own marker and a reference to it: each destination must hold`.
- I-para-blank and I-para-indent, each half of the bullet-to-paragraph rule. I-para-blank: red on 5 checks, including `items: an unindented line right after a bullet continues it`. I-para-indent: red on `items: an indented line after a bullet's blank continues it` and the tab row. I-para-tab, alone: red on `items: a tab-indented line after a bullet's blank continues it`.
- V-NONBLOCK-\bminor\b, one generated alternative: red on `items: NONBLOCK reads 'minor' mid-sentence` and `items: a verdict naming a short SHA is read`. Every other alternative has its own row and its own red line in the drive's output.
- M10, the `findings_gate` call deleted from `PreFlight.entry` in `queue_pre_flight.py`: red on 4 checks, including `a body whose Friction finding names no destination PARKs on findings`.

One mutant is equivalent: S-span-lo (`a < at` for `a <= at`). A span opens on a backtick, so no `Carry:` can start at a span's first offset.

## Null control

- M0, the file unmutated: `RESULT mutant=M0 failed=0 verdict=baseline`. A mutant whose pattern is not found exactly once aborts the drive.
- With M16's grammar row deleted and the file otherwise as at this head, the self-test passes unmutated and passes under M16: 0 failed. The same holds for M15b with its row deleted. Each row is what kills its mutant.
- The census refuses a site no mutant reaches. With M16 left out of the mutant list, the census prints three sites UNMAPPED (`i + 1 < len(starts)` as test and as compare, and the `i + 1` index). With M15b left out, it prints two (the `.split` call and its `[0]`).
- A planted body with one unrouted Friction finding refuses. The same body with `Carry: R10-LIVE` passes. With `Carry: R10-INVENTED` it reads as a bad destination.
- The roster-drift read with the same ref twice prints no `ROSTER-DRIFT` line. With `64b1f82a3` against `b29cd8d23` it prints the sweep's L18 set.

## Figures

All re-taken at `b419463b18a2a7da70c77b23e912769e4af6afe8`, origin/main `06c6f3cf2589cd37fa9fe56cc5ebeef709dc8d3b`, 2026-10-19 02:40 UTC.

- `python3 dev/audit/harnesses/r10_carry_parser_mutants.py`: `RESULT sites=152 unmapped=0 mutants=190 survived=0`.
- `python3 -I tools/audit/carry_audit.py --self-test`: `carry_audit self-test: 144 checks, 0 failed`.
- `python3 tools/audit/seat/queue_pre_flight.py --self-test`: `queue_pre_flight self-test: 37 checks, 0 failed`.
- `python3 tools/audit/seat/merge_train.py --self-test`: `merge_train self-test: 180 checks, 0 failed`.
- `python3 dev/audit/harnesses/r10_carry_sweep_rows.py rows39`: `RESULT rows_caught=33 of=33`. These are the sweep's UNCARRIED rows that live in PR text.
- `python3 dev/audit/harnesses/r10_carry_sweep_rows.py last20`: `RESULT rows_caught=34 of=35` and `RESULT last20_hits=76 on_a_row=46 on_no_row=30`. The harness prints each hit that is on no row.
- `python3 -I tools/audit/carry_audit.py --roster-ref origin/main sweep --issues`: 2 `ISSUE-UNOWNED` (#2409, #2410).
- `python3 -I tools/audit/carry_audit.py --roster-ref 64b1f82a3 --roster-ref b29cd8d23 sweep`: 6 `ROSTER-DRIFT`. With `b29cd8d23` given twice: 0.
- `python3 -I dev/audit/rounds/round6/D11/fix/codeowners_gap.py --check`: `RESULT uncovered_files=0 count`.
- `node tools/policy/field_coverage.mjs`: `FIELD COVERAGE ok` (`refused=0`, `dead=0`).
- `node tools/policy/agreement.mjs --only discovery`: `RESULT divergent=0 unregistered=0 dead=0 refused=0`.
- `python3 tools/pr/ci_predict.py --base origin/main --apply-inert`: `CI PREDICT: no closures or fast red predicted against 06c6f3cf2589`. The inert entry for `dev/audit/harnesses/r10_carry_parser_mutants.py` is already in the tree, so nothing is applied.
- `node tools/policy/policy_lint.mjs`: `TOTAL: 0 error(s) across 41 policy file(s)`.
- `node tools/policy/rules_sync.mjs --check`: `RULES-SYNC ok`.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`.
- `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir D`: `MODE: SCOPED -- 3 script(s) run` (`tests/entities.py`, `tests/harness_headers.py`, `tests/layout.py`). Results: `ALL 2349 ENTITY CHECKS PASSED` (with `env -u BASH_ENV`), `ALL 109 HARNESS HEADER CHECKS PASSED`, `layout self-test: ok`. The `run_always` lines add `python3 tests/closure.py selftest`: `ALL 115 closure shrink pins PASSED`, and `python3 tests/env_drift.py --claims-only 06c6f3cf2589cd37fa9fe56cc5ebeef709dc8d3b`: `claims hygiene: 06c6f3cf2589cd37fa9fe56cc5ebeef709dc8d3b ok`.
- `python3 -I tools/policy/agreement_py.py --out J` then `node tools/policy/agreement.mjs --py-json J`: `RESULT divergent=0 unregistered=0 dead=0 refused=0`. `node tools/policy/agreement.mjs --self-test`: `SELF-TEST 27 of 27 probes held`.
- `python3 -I -S tests/delivery_status.py --check`: `DELIVERY STATUS OK` with `0 overdue`.

## Red checks

At the current head `b419463b18a2a7da70c77b23e912769e4af6afe8` no check run is red (`coverage` and `Analyze (python)` were still running when read, 2026-10-19). The previous head `03f1681a3e684854b5b934020ec5d44612b2ffd2` had three red checks in its latest CI. All three were inherited from `main` or came from this body, and the merge of origin/main in `bd68cf756ab63a475d37d30fcdf60b35d85a6214` clears the first two.

- `wave-script` (job 117830428629 at `03f1681a3`): the agreement lane printed `RESULT divergent=2` for the `merge-subject-pr` concept. The corpus held two merge subjects with a custom suffix, `Merge pull request #2401 (R10-ARCHSCORE-COVERAGE p5)` and `Merge pull request #2379 (R10-SENSOR-PAYLOAD)`. `stamp.py` and `delivery_status.py` read the number from them, and the two `policy_lint.mjs` readers returned null. The cause is on `main`: two PRs were merged with a custom subject, and the readers did not agree on a suffixed subject. The red is not this PR's: this diff touches none of the four readers. Cleared by the main merge: #2423 gave the readers one merge-subject grammar (`tools/policy/agreement.mjs`, `tools/policy/agreement_py.py`, `tools/policy/policy_lint.mjs`), and #2424 narrowed the guard to main's first-parent merges. At this head, `python3 -I tools/policy/agreement_py.py --out J` then `node tools/policy/agreement.mjs --py-json J` prints `RESULT divergent=0 unregistered=0 dead=0 refused=0`, and `node tools/policy/agreement.mjs --self-test` prints `SELF-TEST 27 of 27 probes held`. The cheaper detector is the agreement lane itself; it caught the divergence on the PR's first run. Its standing cost is one job in `governance.yml`, which this PR does not change. The countermeasure against a custom subject is the merge-subject guard of #2423 and #2424.
- `delivery-status` (job 117830428746 at `03f1681a3`): it listed `#2413`, `#2412` and `#2407` as `overdue`, the record PRs whose rows `main` had not yet absorbed. The check itself warns that the red may be this PR's own because the diff touches `.github/workflows/governance.yml`. It is not: this diff adds one step to the `instrument-self-tests` job, and `tests/delivery_status.py` names `governance.yml` only in comments (lines 6 and 496), reading nothing from it. Cleared by the main merge: #2420 landed the rows for #2407, #2412 and #2413, among others. At this head, `python3 -I -S tests/delivery_status.py --check` prints `DELIVERY STATUS OK -- 136 rowed, 2 pending, 0 overdue`. Null control: the same lane's log at `03f1681a3` printed the overdue list, so the command does read the window. The check is not a required context.
- `pr-contract` (job 117830603406 at `03f1681a3`): `[pr-body]` refused the body because `wave-script` and `delivery-status` were red and this section did not name them. The two entries above answer that. Nothing else in the job was red.

Two earlier reds, at `713182ca1`, stay answered here:

- `pr-contract` (job 117682137845): `carry_audit.py check` refused this body with `UNROUTED body item cb97c3b2 (## Forward-carry)`, although the item carried `Carry: O10-policy-fixer-md`. The cause was real: a quoted `Carry: ...` earlier on the same line was matched greedily to the end of the line, swallowing the real marker after it. Fixed: each segment is cut at the next `Carry:`. M16 pins that cut. Cheaper detector: the self-test, which now holds the row. No fixture had held two markers on one line.
- `fast (3.14)` (job 117682154858): `tests/harness_headers.py`, `every inlined walk matches the canonical helper and no depth root remains`, refused `dev/audit/harnesses/r10_carry_sweep_rows.py:33: ROOT = Path(__file__).resolve().parents[3]`. Fixed: the harness inlines `repo_root`, as the other harnesses do, and the new harness does the same. Cheaper detector: none. The census runs only in the full harness script, which prepr leaves to CI.

## Forward-carry

- `tools/audit/seat/orchestrator_tick.py`: the weekly and closure carry sweep. It runs `carry_audit.py sweep --last N --issues` with both roster refs, prints a dispatch line when the sweep exits 1, and has a self-test arm with its null control. Its precondition is this PR merged. R10-TICK-DRIVERS merged as #2390 without it, so the carry now sits in the roster entry of R10-OPENPR-SILENT (#2422), which owns `orchestrator_tick.py`. Carry: R10-OPENPR-SILENT
- `dev/governance/rules/finding-propagation.md`: the marker also binds a finding the orchestrator records in its own ledger, written `FINDING: ... Carry: ...`, which the sweep's `--ledger` read keys on. The sentence does not fit under the file's cap. Carry: O10-policy-fixer-md

## Friction

- finding-propagation.md: cost: the file was at its cap, so the marker sentence was paid for by four prose cuts in the same file. Carry: dismissed: paid in this diff
- fix-review.md: unenforced: the reviewer's contract has no headroom left, so it does not name the marker; finding-propagation.md binds reviewers, as it binds every seat. Carry: O10-policy-fixer-md
- finding-propagation.md: cost: the marker's reading rules (an id counts only inside its marker's segment, a code-span `Carry:` is an example, every marker naming an item adds its destinations) are written in `carry_audit.py`'s docstring, not in the rule, which is at its cap. Carry: O10-policy-fixer-md
- carry_audit.py: unenforced: the destination check reads the roster's stage, which lags a merge (R10-TICK-DRIVERS read `not-started` after #2390 merged), so a carry to a merged group passes. It should also read the group's merged PR, from its delivery row or a `gh` read as the issue arm does. Carry: O10-policy-fixer-md

## Approval

This PR changes policy, so tvofi's approving review at the head is owed before merge. The policy files are `dev/governance/rules/finding-propagation.md` (with its generated `.claude/rules/` and `.cursor/rules/` copies) and `.github/PULL_REQUEST_TEMPLATE.md`. The code-owned files are `.github/workflows/pr-contract.yml`, `.github/workflows/governance.yml`, `tests/layout.json`, and `.github/CODEOWNERS`, which now names `tools/audit/carry_audit.py`. No `*_budgets.json` row changes.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

https://claude.ai/code/session_015MUmyakanzTMe3hXgmXbQL


