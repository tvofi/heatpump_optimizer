R11-PRE-NO-READ-BUILDERS, parts A and B of the approved design (design/R11-PRE-NO-READ-BUILDERS 9edf64948f7522213ca07a313f5121fe4c20a72a, `Design review: approve` at design-verdict 18fc037aed84d51cfbaa85604db8f106d6c71423): the two reads that make a role contract scorable per clause and a rule scorable by its class's instances (decision 0018 section 3). Cards E11-N-ROLE-CLAUSE and E11-N-RULE-YIELD, re-read at eval/r11 c6ce415b7711d76cf6c08f926f30da91f7bda924 (`review.verdict` approve): both `decision: accepted`, neither rewritten nor dropped.

**Parts C and D are not in this pull request, and cannot be built at this base.** The design orders C after R11-PRE-TOKEN-LEDGER's merge and D after R11-PRE-ROUND-METRICS parts 2 and 3; none is on main (`## Figures`), so the per-session iterator C imports and the `convergence_why` vocabulary and `loop_ledger.py` D changes do not exist at the merge base. The design names A and B as needing neither edge. E11-N-INSTRUMENT-YIELD, E11-N-GATE-CAUSE and the load count of E11-N-RULE-YIELD stay open on the group.

**A. A block's class names its clause.** `.claude/workflows/web-fix-wave.js` gains `VERDICT_CLAUSES` beside `VERDICT_CLASSES`: one key per taught class, its value `<role>.md step N` or `null`. `review_strength.py --by clause` reads it from the `--tree` text, never a copy, and counts a block on its clause's row. A clause resolves when `dev/governance/roles/<role>.md` at `--tree` holds a line opening `N. `; anything else prints `UNRESOLVED <clause>`, in the header and as a row. A `null`, an untaught word, a classless block and a merge keep their own rows. A map whose keys are not exactly the taught classes, or a tree with no map, refuses `--by clause` and leaves every other stratum read. No verdict subject changes, so the round-10 window reads by clause with no re-review.

**B. Instance dates and rule yield, derived.** `fold_ledger.py yield` reads from git at `--ref`, storing nothing: an instance's date is the committer time of the first first-parent commit whose ledger adds its string (one `git log -p` walk following the ledger's own move), a `non_round_instances` row is dated by its leading SHA, and a rule's date is its first add under `git log --follow --diff-filter=A`. Each class gains a `rules` list (empty is a value) that `check` resolves as `MISSING-PATH`. One `RULE` row per rule: classes, instances before, after and undated; `no-class` when no class names it, never 0. A shallow repository refuses.

Four links are written, each from one line of the class's rca document: I2 to `ci-autofix.md` (`dev/audit/rca/R10-RCA-INERT-CLOSURE-RECORDING.md:50` "The process followed is `ci-autofix.md`'s"); I3 to `defect-root-cause.md` (`dev/audit/rca/R9-I3.md:61` "The process is `defect-root-cause.md`"); P11 to `finding-propagation.md` (`dev/audit/rca/R9-RCA-1869.md:121`); N-shared-config to `defect-root-cause.md` (`dev/audit/rca/R9-RCA-1736.md:71`). The rule for a link: the rca document names the rule as the process governing the class's defect, or as where its countermeasure landed. A rule cited only as the authority for the analysis itself, and a change proposed and not landed, is no link.

## Departures from the design note, raised

- **B dates a rule through a copy, where the note says "rename detection only, no copy detection".** The note's own command, `git log --follow --diff-filter=A`, traces copies as well as renames, and the note's measurement (every rule's `--follow` add is earlier than bc0f17ddb6) depends on that: at bc0f17ddb6 the ten rule files were added under `dev/governance/rules/` while `.claude/rules/` stayed as the generated copy, so the move is a copy and a renames-only walk would stop there, which is the path date the note's R3 rejects. The command is kept and the parenthetical is not. The cost is a rule drafted from another file taking that file's date, so a row whose date comes from another path prints `as <path>`. The self-test pins both: a moved rule and a copied one.
- **A maps `conflict` to `null`, as the note lists it, although `fix-review.md` step 13 governs a conflict block.** Changing it is one value in the map.
- **B's instance date is when the ledger recorded the instance.** The ledger was created on 2026-09-24 with rounds 1 to 8 back-filled, so every rule older than that reads `before 0`. The docstring says so.

## Head

prepr: passed rc=0 at 08c41f0a3505d67af9a64bf8d7c19781262c7458

08c41f0a3505d67af9a64bf8d7c19781262c7458, merge base 030a4d377f9f26f5b8befe5721d86aea454f29e0, measured 2026-11-16T15:28:27Z with origin/main at e352724335c136b65562cd3e71f728549ad04a82. `git merge-tree --write-tree origin/main HEAD` exits 0, so main is not merged in.

## Mutation proof

Each mutant is an exact one-occurrence string swap in a second worktree at the head, the named self-test run, the file restored.

`python3 tools/audit/fold_ledger.py --self-test`:
- the walk's comparison, `x > t` to `x >= t`: `FAIL yield: an instance recorded in the commit that adds the rule is before it`.
- `--follow` dropped from the rule's date: `FAIL yield: an instance recorded after the rule's first add under another directory reads after 1 ...`, and two more.
- `--first-parent --diff-merges=first-parent` dropped from the instance walk: `FAIL yield: an instance is dated at the first-parent commit that first holds it: the merge (day 3), never the side commit (day 2), and through the ledger's own move`; `--follow` dropped from that walk: the same check.
- the `no-class` row printing counts: `FAIL yield: a rule no class names reads no-class, never 0; ...`.
- the shallow refusal disabled: `FAIL yield on a shallow clone refuses, never a date read off a truncated history`.
- `check` not reading `rules`: `FAIL check: a rules entry that is no file at the root is MISSING-PATH`.
- a non-round row's SHA not resolved: `FAIL yield: a non-round row is dated by its own SHA's commit; ...`, and four more.

`python3 tools/audit/seat/review_strength.py --self-test`:
- the clause lookup in `stratum` returning the class word: `FAIL: --by clause: the planted harness blocks count on the row of the clause the map names (2 PRs, 2 verdicts, 2 real)`, and six more.
- the resolver accepting any clause: `FAIL: --by clause: a step the role file does not number, a role file that does not exist and a section name read UNRESOLVED`.
- the key-set refusal disabled: `FAIL: verdict_clauses refuses a taught class with no key`, `... a key no class teaches`, `... a class keyed twice`.

The round-10 mutant harness, re-run after A as the design asks: `python3 dev/audit/harnesses/r10_review_strength_mutants.py` over every one-node mutant of `review_strength.py`. Its first full run at the part-A commit 088cd08ed1 ended `RESULT mutants=3634 killed=3524 survived=110 disposed=53 undisposed=57 stale=1`. 43 of the 57 were in the new clause code; each is now killed by a self-test check added for it, removed with the statement order that made it equivalent, or one of four equivalents recorded in the harness's `DISPOSED` table with its reason. Re-run at the head over every mutant whose key opens with `CLAUSES_RE`, `PAIR_RE`, `CLAUSE_RE`, `verdict_clauses`, `clause_rows`, `tree_clauses`, `stratum` or `main @` (1029 mutants): the only undisposed survivors are three in `main`'s model-arm loop. Those three and the other 11 of the 14 left (`MODEL_RE`, `load`'s `CONFIRMED_RE` loop, `guardrail`'s model arm) survive at the merge base too, as does the one `STALE` entry: the same harness functions run on origin/main's file over the keys opening `MODEL_RE`, `load @`, `guardrail @`, `main @` print the same 14. They are the `bus-model` arm's, which this diff does not touch. The full harness was not re-run at the head (about two hours here).

Diff mutants (`fixer.md` step 2): `MUTANT_CMD="sh -c 'python3 -I tools/audit/fold_ledger.py --self-test >/dev/null && python3 -I tools/audit/seat/review_strength.py --self-test >/dev/null'" PREPR_SKIP_CLOSURES=1 bash tools/pr/prepr.sh <body>` draws the first 40 mutants of the added lines. A first draw left three in production lines, each now killed by a check added for it (the walk skipping its newest commit; a non-round SHA the repository lacks refusing instead of reading undated; a path never added). The five it still prints are under `## Unpinned sites`.

## Unpinned sites

All five are lines of `fold_ledger.py`'s own self-test, not of the code it tests; the lines are named by their text, since a line number moves:

- `CALL_DEL` of the `expect("a minted class names no rule yet: ...")` call, and of the `_self_test_yield(expect)` call: a deleted check cannot fail, and the CI step counts no checks for this file (`python3 -I tools/audit/fold_ledger.py --self-test` is read by its exit status). No check inside the self-test can pin its own presence.
- `CONST_SWAP` `sys.path.insert(0, ...)` to `insert(1, ...)`: equivalent. The `tests` directory is the only path entry holding `throwaway_git`, so either position imports it.
- `CONST_SWAP` `range(40)` to `range(41)` in the fixture's file body, and `indent=2` to `indent=3` in the fixture's ledger writer: equivalent. Both only shape fixture files; any body long enough for git to pair a moved file and any JSON layout give the same rows.

## Null control

- A: at origin/main the card's command with `--by clause` exits non-zero with `review_strength: no VERDICT_CLAUSES literal in .claude/workflows/web-fix-wave.js` and prints no clause row. In the self-test a merges-only window prints 0 verdicts on every clause row, the rows present.
- B: `python3 tools/audit/fold_ledger.py check` prints `0 violation(s)` at the merge base and at the head (the card's null control). `yield --ref origin/main` prints every rule `no-class` and `0 linked`. In the self-test a linked rule with no later instance reads `after 0`.

## Figures

<!-- figure-block: scope-line mb=030a4d377f9f26f5b8befe5721d86aea454f29e0 head=08c41f0a3505d67af9a64bf8d7c19781262c7458 -->
~~~text
MODE: FULL -- every test script runs, nothing is scoped out.
~~~
<!-- /figure-block -->
- `python3 tools/audit/seat/review_strength.py --repo . --fetch --tree HEAD --window r10=2026-10-14T13:27:06Z..2026-11-15T05:22:47Z --by clause` (the card's window): 2537 verdicts in the window, as the card's `--by class` read; 10 clause rows, 4 `(no clause)` rows, 165 `(untaught)` rows, one `(merge)` row, no `UNRESOLVED` line. Row counts by `grep -c` over the `## clause` section for `step`, `(no clause)`, `(untaught)`, `(merge)`.
- `python3 tools/audit/fold_ledger.py yield` at the head: its closing line counts 12 rules, 3 linked, and the instances dated and undated; every undated row is a `non_round_instances` row naming no resolvable commit (`python3 tools/audit/fold_ledger.py yield --instances | grep ' undated$' | grep -c -E '^INSTANCE \S+ R[0-9]+ '` prints 0).
- The rules directory move is a copy: `git diff-tree -r -M --name-status bc0f17ddb6^ bc0f17ddb6` lists each `dev/governance/rules/*.md` as `A` and no `R` line for them.
- Predecessors absent at the base: `git merge-base --is-ancestor 28c3ba15ee origin/main` and the same for fae479abae both exit 1; `git grep -c convergence_why origin/main -- tools` prints nothing; `git ls-remote origin 'refs/heads/*token-ledger*'` prints nothing.
- Self-tests at the head: `python3 -I tools/audit/seat/review_strength.py --self-test` ends `review_strength self-test: 141 checks, 0 failed`; `python3 -I tools/audit/fold_ledger.py --self-test` prints 58 `ok` lines and no `FAIL`.
- Other readers of the verdict literal with the second literal present: `node tools/policy/check-wave-script.mjs` ends `249 passed, 0 failed`; `python3 -I tools/policy/agreement_py.py --run` ends `AGREEMENT ok`; `PYTHONPATH=tests/hastub python3 tests/entities.py` (the one script `scope.run` names) ends `ALL 2723 ENTITY CHECKS PASSED` at the head.
- `python3 tools/audit/archscore/score.py --diff 030a4d377f HEAD` prints `Architecture score: dS +0.0000 NULL`. `python3 tests/structure.py` prints `STRUCTURE RATCHET PASSED`; `python3 tests/layout.py` prints `GUARD: 0 refusal(s)`.
- `tools/ci/selftest_closures.json`: the `review-strength-enumerator` step gains `dev/governance/roles/fix-review.md`, measured by `python3 -I tools/ci/selftest_scope.py record --step review-strength-enumerator`; the recorder also deleted entries in other steps, which are not taken. `python3 -I tools/ci/selftest_scope.py select --change M:dev/governance/roles/fix-review.md` now names that step.
- `dev/audit/harnesses/r10_review_strength_mutants.py` skips the new self-test function, copies `dev/governance/roles/fix-review.md` for each mutant and gains the four `DISPOSED` entries.

## Red checks

none

## Forward-carry

- Carry 0 (not built in this handoff): parts C and D of the approved design, with the design note's fixer notes [paths], [d-p2-head], [P1] and [c-deferred] and the verdict's notes runs-json-width, d-hotfile-enumerator and branch-reuse, are unbuilt: the orchestrator dispatches them once R11-PRE-TOKEN-LEDGER (C) and R11-PRE-ROUND-METRICS parts 2 and 3 (D) are on main; lands in the group's row of the round-11 roster on handoff/audit-r10-roster (c9d838fdfc at this writing; not in this tree), D's surface being `tools/audit/seat/round_metrics.py`. Carry: R11-PRE-NO-READ-BUILDERS
- The two departures above (a rule dated through a copy; `conflict` mapped to `null`) await the orchestrator's ruling; same roster row, the surfaces being `tools/audit/fold_ledger.py` and `.claude/workflows/web-fix-wave.js`. Carry: R11-PRE-NO-READ-BUILDERS

## Friction

- ci-autofix: cost: `prepr.sh`'s step 6d predicted `governance / instrument-self-tests` red on "Show the beat's job rows refusing their own fixtures" (rc 1 at the head, 0 at the base) in 2 of 4 runs at this branch and predicted nothing in the other 2, the last of them the clean run at this head. The step itself, `python3 -I tools/audit/seat/beat_jobs.py --self-test`, ended `271 checks, 0 failed` in every one of 12 runs outside `prepr.sh` at the head (3 of them through `bash -eo pipefail` with the step's own `run:` text, 4 under three concurrent self-test loops) and once at origin/main. The failing check was never captured, because the replay discards the step's output; the cause is not established, and this diff changes no file the step's `run:` text names. Carry: dismissed: the cause is not measured, so there is nothing a later stage can act on; the reviewer reads the step on the pull request's own CI
- fixer.md: contradiction: step 2 says to set `MUTANT_IN_PLACE=1` for a self-test that needs a checkout; exported into `prepr.sh`, it reaches prepr's own self-test, whose check "a check needing a git checkout measures nothing in the archive copy, and is refused" then fails (`552 passed, 1 failed` with the variable at 225a7a571e, `553 passed, 0 failed` without it at the same head). Not needed here: the two self-tests pass in the archive copy once `MUTANT_CMD` is wrapped in `sh -c` (a bare `a && b` is not run by a shell and reads `BASELINE FAILS`). Carry: dismissed: no live roster group owns `tools/pr/prepr.sh`; left for the round-end proposal triage
