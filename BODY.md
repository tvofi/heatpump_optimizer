O11 (round 10, part of #201; tvofi's request 2026-10-18): carry-forward made mechanical. `finding-propagation.md` already required every finding to reach an owner, and nothing enforced it. The round-10 finding sweep found 39 of 95 findings with no owner, recorded in a body's `## Friction` or `## Forward-carry`, in a `Fix review:` verdict's non-blocking notes, in the orchestrator's ledger, or as an auto-filed issue no group lists.

What lands:

- **The marker**, in `dev/governance/rules/finding-propagation.md` (Enforcement) and the PR template's `## Forward-carry` and `## Friction` lines. Every finding item a body or verdict records ends with `Carry: <GROUP>|#<issue>|O<n>|dismissed: <reason>`.
- **`tools/audit/carry_audit.py`**: the one parser of the marker. It finds the finding items of a body and of the PR's `Fix review:` comments, and refuses an item with no marker, or with a destination that is gone or done. A gone or done destination is: a group the roster does not hold or holds as done; an issue no live group, carry file or O-brief owns (and, with `gh` reads, one that is closed); an O-brief that does not exist; or a bare `dismissed:`. `sweep` adds three reads: every open issue nothing owns; the carry or brief text one roster ref holds and another lacks; and every line in the orchestrator's ledger that says `FINDING:` or `LESSON:` with no `Carry:`. `owners` is the sweep's own.py, promoted.
- **Wiring.**
  - `pr-contract` runs it on the body as the pull request's own copy, in the job's last step, and `.github/CODEOWNERS` owns it, as it owns `fold_ledger.py`. It is not pinned: a pinned grader must be declared in the pinned `field_coverage.mjs`, so the pull request that adds one cannot pass (#1847). Being the last step, a write to `$GITHUB_ENV` reaches no later step. `roster_lib.py`, which it imports, is restored from the base. In CI an O-brief passes printed UNVERIFIED.
  - `tools/audit/seat/queue_pre_flight.py` gains a `findings` step, which the train's `--pre-flight` runs. It reads the body and every verdict, checks O-briefs in `$HPO_BRIEFS_DIR`, and PARKs a PR whose notes would merge unowned.
  - `governance.yml`'s `instrument-self-tests` runs both self-tests.
  - The weekly and closure sweep from `orchestrator_tick.py` is a fold (Forward-carry), not an edit: handoff/r10-tick-drivers holds that file.

Alternatives considered:
- Extending `policy_lint.mjs`'s `## Forward-carry` check lost: verdict comments and the sweep are read by Python tools (`queue_pre_flight.py`, the tick), so one Python parser serves all three callers instead of two parsers in two languages.
- A ledger key on OWED lost too. It printed 31 lines over SEATS.md and caught one of the sweep's 39 rows; the other 30 were work-queue entries. The key kept is `FINDING:`/`LESSON:`: 1 line over SEATS.md, L16, and no work-queue line.

After this merges, an open PR's `pr-contract` re-runs on its next push or body edit and refuses an unrouted `## Friction` or `## Forward-carry` item, until the body adds its `Carry:`.

## Head

`269a8dfd454aec568a67563ed97844f27184ffdd` (on #2404's head `5cf5786b9`, with origin/main merged in, 2026-10-18). Commits `71a7b6294` and `269a8dfd4` answer the review that blocked `5cf5786b9`. A marker's item id now counts only as `(item <id>)` inside that marker's own segment, so a quoted refusal (`UNROUTED body item <id>`) beside an unrelated marker routes nothing. A `Carry:` inside a code span is now a quoted example, never a marker. A span closes as CommonMark closes one: a backtick run closes only on a run of its own length. prepr's agreement lane refused the first copy, which was the same literal as `tests/entities.py`'s looser span. Each case has a self-test arm with its null control (M12, M13). The reviewer's three probes now read `0 routed, 1 unrouted`. This body passes on its own markers: its `## Red checks` quote of `cb97c3b2` routes nothing. The earlier commit `faf1bf1b1` repaired the two reds below.

## Mutation proof

Each mutant was applied to `tools/audit/carry_audit.py` or `tools/audit/seat/queue_pre_flight.py` alone, the self-test re-run, and the file restored (`git status` clean after):

- M1: `## Friction`/`## Forward-carry` items never flagged. Red: `a planted body with an unrouted Friction finding refuses`, `the same body with a Carry: to a live group passes (null control)`.
- M2: a done group accepted. Red: `a done group is a bad destination`.
- M3: an unowned issue accepted. Red: 4 checks, including `an issue no group lists has no owner (the L20 shape)`.
- M4: the verdict's non-blocking arm dropped. Red: `in a blocked verdict, only the non-blocking item is a finding`.
- M5: lead-paragraph inheritance off. Red: `a verdict's non-blocking lead flags its bullets, not itself and not ## Verified`.
- M6: `dismissed:` reason unchecked. Red: `a bare dismissed is refused`.
- M7: the blocked-verdict rule off. Red: `a blocked verdict: a residual heading is the block; a residual lead and a minor note are not`.
- M8: routing by `(item <id>)` ignored. Red: `an item routed by reference from the body counts as routed`.
- M9: the trailer filter off. Red: `` `n/a: <reason>` and the attribution trailer are not findings ``.
- M11: the ledger key matches nothing. Red: `a ledger LESSON: with no Carry: is unrouted; a work-queue OWED line and a routed FINDING: are not`.
- M12: the id read anywhere in the item again (the pre-review parser). Red: `a quoted refusal beside an unrelated marker routes nothing (#2404's review)`.
- M13: the code-span skip removed. Red: ``a backticked example `Carry:` in a finding's prose does not route it``.
- M10: `findings_gate` call deleted from `PreFlight.entry`. Red: 4 `queue_pre_flight` checks, including `a body whose Friction finding names no destination PARKs on findings`.

## Null control

- A planted body with one unrouted Friction finding refuses. The same body with `Carry: R10-LIVE` passes. With `Carry: R10-INVENTED` it is a bad destination (self-test rows 1-3).
- The roster-drift read with the same ref twice prints no drift line. With `b29cd8d23` against `64b1f82a3` it prints six lines: the sweep's L18 set (R10-SCORES carry and brief, UX-SETUP, ADVISOR, UX-HEALTH and ARCHSCORE-COVERAGE briefs).
- An O-brief owns the issues its file name carries (#2353 via `O10-rca-friction-2331-2353.md`), and no other issue (#2354 refuses).
- Last 20 merged non-record PRs: 76 finding items, all unrouted, since no `Carry:` existed yet. Set against the sweep's 35 rows from those PRs, 34 are hit. The one miss, P42, is an item of a blocked verdict's block, owed inside that PR, so it is correctly not a carry.
  - 46 hits sit on those rows. Of the other 30: 6 are sweep rows the harness's keys do not match (L11 L12 P23 P24 P34 P69), 14 are non-blocking notes or friction the sweep did not classify, 4 are owed actions (tvofi approval, close-by-hand), and 6 are over-fire: confirmations, such as #2360's "comment is accurate", #2371's "precondition holds", and #2320's Verified items.
  - The harness prints each EXTRA line.

## Figures

- `python3 -I tools/audit/carry_audit.py --self-test`: `carry_audit self-test: 39 checks, 0 failed`.
- `python3 tools/audit/seat/queue_pre_flight.py --self-test`: `queue_pre_flight self-test: 37 checks, 0 failed`.
- `python3 tools/audit/seat/merge_train.py --self-test`: `merge_train self-test: 180 checks, 0 failed` (at the base too; before the fake's comments branch was added, head read 2 failed on the two `--pre-flight` checks).
- `python3 dev/audit/harnesses/r10_carry_sweep_rows.py rows39`: `RESULT rows_caught=33 of=33`. These are the sweep's PR-text UNCARRIED rows; the other six (ledger L14-L16, issues L20/L21, roster L18) are below.
- `python3 dev/audit/harnesses/r10_carry_sweep_rows.py last20`: `RESULT rows_caught=34 of=35` and `RESULT last20_hits=76 on_a_row=46 on_no_row=30`.
- `python3 -I tools/audit/carry_audit.py --roster-ref origin/main sweep --issues`: 6 `ISSUE-UNOWNED`, including L20's #2378 and L21's #2381. Two of the six, #2331 and #2353, are owned once `--briefs-dir` names the O-briefs.
- `python3 -I tools/audit/carry_audit.py --roster-ref 64b1f82a3 --roster-ref b29cd8d23 sweep`: 6 `ROSTER-DRIFT` lines (L18). The same ref twice prints 0.
- `python3 -I tools/audit/carry_audit.py --roster-ref origin/main sweep --ledger <SEATS.md>`: 1 `LEDGER-UNROUTED`, l107 (L16).
- Caught over the 39 sweep rows: 37 (33 PR text, L16, L18, L20 and L21). Missed: L14 and L15, ledger prose with no `FINDING:` or `LESSON:` key, which only the convention can reach (Forward-carry).
- `python3 -I dev/audit/rounds/round6/D11/fix/codeowners_gap.py --check`: `RESULT uncovered_files=0 count` (`carry_audit.py` COVERED by its owner).
- `node tools/policy/field_coverage.mjs`: `refused=0` (`dead=0`). The pinned wiring was refused here as unregistered, the reason for the owned last step.
- `node tools/policy/agreement.mjs --only discovery`: `RESULT divergent=0 unregistered=0`. Two shared grammars were removed: the carry file's issue is now read from its `issue` field, which gives the same 8 issues as the file names on the tree and at origin/main; the fence is now a prefix test.
- `python3 tools/pr/ci_predict.py --base origin/main --apply-inert`: `APPLIED inert_reads tests/harness_headers.py: dev/audit/harnesses/r10_carry_sweep_rows.py`, then `CI PREDICT: no closures or fast red predicted`.
- `node tools/policy/policy_lint.mjs --budgets`: `.claude/rules/finding-propagation.md` 100 of 101 lines, 1335 of 1336 tokens; `.github/PULL_REQUEST_TEMPLATE.md` 38 of 38 lines, 303 of 305 tokens.
- `node tools/policy/policy_lint.mjs`: `TOTAL: 0 error(s) across 41 policy file(s)`.
- `node tools/policy/rules_sync.mjs --check`: `RULES-SYNC ok`.
- `python3 tests/structure.py` at the merged head: `STRUCTURE RATCHET PASSED`.
- `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir D`: `MODE: SCOPED -- 2 script(s) run` (`tests/entities.py`, `tests/harness_headers.py`). Both are left to CI because the box load was high (coordinator, 2026-10-18).

## Red checks

- `pr-contract` (job 117682137845 at `713182ca1`): `carry_audit.py check` refused this body. It printed `UNROUTED body item cb97c3b2 (## Forward-carry)`, although the item carried `Carry: O10-policy-fixer-md`. The cause was real: a quoted `Carry: ...` earlier on the same line was matched greedily to the end of the line, swallowing the real marker after it. Fixed: each `Carry:` is now parsed up to the next one, with a self-test arm (`a quoted Carry: ... earlier on a line does not hide the real one after it`). The same body now reads `4 routed, 0 unrouted`. Cheaper detector: the self-test now pins it. The miss was that no fixture had two markers on one line; this body was the first.
- `fast (3.14)` (job 117682154858 at `713182ca1`): `tests/harness_headers.py`, `every inlined walk matches the canonical helper and no depth root remains`, refused `dev/audit/harnesses/r10_carry_sweep_rows.py:33: ROOT = Path(__file__).resolve().parents[3]`. Fixed: the harness inlines `tools/audit/repo_root.py`'s `repo_root`, as the other harnesses do. `harness_headers.inline_scan()` exits 0 at the head; with the old file put back it prints the same `FAIL depth seams` line (null control). Cheaper detector: none. The census runs only in the full harness script, which prepr leaves to CI ("left to CI: tests/harness_headers.py"), and the seat did not run its child scan.

## Forward-carry

- `tools/audit/seat/orchestrator_tick.py`: the weekly and closure carry sweep (`--carry-sweep N` running `carry_audit.py sweep --last N --issues` with both roster refs; a dispatch line when it exits 1; a self-test arm with its null control). The fold text is out of tree, in the O11 seat directory, because handoff/r10-tick-drivers holds the file. Carry: R10-TICK-DRIVERS
- `dev/governance/rules/finding-propagation.md`: the marker also binds a finding the orchestrator records in its own ledger, written `FINDING: ... Carry: ...`, which the sweep's `--ledger` read keys on. That is where L14, L15 and L16 were; L16 says `LESSON:` and is caught, while L14 and L15 are prose. The sentence did not fit the file's cap after this diff (the O11 seat directory holds a fold with the text and the dropped ledger mode's control). Carry: O10-policy-fixer-md

## Friction

- finding-propagation.md: cost: the file had 1 line and 7 tokens of headroom, so the marker sentence cost four prose cuts in the same file (the history sentence in "A comment is not propagation", two reflows, the Enforcement paragraphs merged). Carry: dismissed: paid in this diff
- fix-review.md: unenforced: the reviewer's contract sits at 0 lines and 0 tokens of headroom, so it does not name the marker; finding-propagation.md binds reviewers as every seat. Carry: O10-policy-fixer-md
- finding-propagation.md: cost: the marker's reading rules (an id counts only inside its marker, and a code-span `Carry:` is an example) are written in `carry_audit.py`'s docstring, not in the rule. The rule is at its cap (100 of 101 lines, 1335 of 1336 tokens). Carry: O10-policy-fixer-md

## Approval

Policy, so tvofi's approving review at the head is owed before merge: `dev/governance/rules/finding-propagation.md` (with its generated `.claude/rules/` and `.cursor/rules/` copies) and `.github/PULL_REQUEST_TEMPLATE.md`. Code-owned: `.github/workflows/pr-contract.yml`, `.github/workflows/governance.yml`, `tests/layout.json`, and `.github/CODEOWNERS` (which now names `tools/audit/carry_audit.py`, so any later edit to the check needs tvofi's review). No `*_budgets.json` row changes, and no ci_budgets row is needed: the new pr-contract step is one Python process over one body, inside the job's 5-minute timeout.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
