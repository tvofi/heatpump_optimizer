# Proposal triage, session s14, batch 163 (P577)

This batch rules `s7/triage-queue-s7.txt` line 259. The bar and the denominators are batch 141's.

Sources:
- origin/main `dbd1ab5b07`. Every line number below is at that commit.
- The roster at `origin/handoff/audit-r10-roster` (bc6ecd8e3c), read with `git ls-remote` at 05:16Z.
- The five blocked heads, all present in the local object store. The verdict files are the dispatch
  seat's `verdict-3419.md`, `-3425.md`, `-3427.md`, `-3428b.md` and `-3431.md`.
- `tools/audit/seat/mutant_run.py` at `dbd1ab5b07`, run from a copy. Each run used `--root` on a
  clean tools checkout and its default copy-tree workspace, so no checkout was mutated.
- No GitHub API calls.

## P577: BOTTLENECK-MUTATION-VACUOUS

Verdict: REJECT both arms:
- (a) a handoff REFUSE on an unanswered `mutant_run --diff` survivor;
- (b) a per-group mutant command in `cloud_dispatch.py`'s fixer brief.

The measured catch rate on the five heads is 2 of 11 named sites at prepr's default cap and
3 of 11 uncapped. Measured, it prevents the block on 1 of the 5 PRs. Its precision is low: 47
survivors on the two heads where it catches anything, against the 3 sites the reviewers named.
That is marginal at best.

No new root-cause seat is owed. The class has one: `dev/audit/rca/R10-RCA-MUTATION-VACUOUS.md`.
Its tools/ refusal (lines 111-118) waited on one number, and this ruling measures that number.
The number confirms the refusal.

The self-test-body noise found while measuring is DEFERRED. It is noise from `mutant_run`
mutating self-test assertions, and its terms are below.

Source: queue line 259, 2026-11-11T05:01:31Z, orchestrator s14. It comes from the beat's
bottleneck row at 05:00:23Z: `block-class mutation-vacuous 31% (5/16 blocks) vs 30%`.

Instances: the 11 sites the five verdicts name. Each site was checked against what
`mutant_run.py --diff <merge-base>...<head> --list` generates at the head.
- **Merge bases.** Each is `git merge-base origin/main <head>`:
  - 3419 at 30c785330f;
  - 3425 at d08ed31049;
  - 3427 and 3428 at 63bcdcaad8;
  - 3431 at 40fe1cae2e.
- **What `mutant_run` can generate.** It mutates only added `*.py` lines (`mutant_run.py:209`),
  outside `tests/` and `dev/` (`:66`). Each line gets statement-level operators only
  (`mutate_line`, `:245`):
  - `if`/`elif` statements become `False`;
  - `return` becomes `pass`;
  - comparison bounds;
  - call statements become `pass`;
  - the first numeric or bool constant is swapped.

  It has no conjunct drop. It does not mutate an `if` inside an expression or a comprehension, and
  it does not mutate string literals.
- **PR 3419 at 245ddf78: 1 of 2 sites caught, and only uncapped.**
  - 51 mutants are listed, all in `tools/ci/selftest_scope.py`.
  - Site 1, the `governance.yml` settle line, is YAML. It is not generated.
  - Site 2 is the CLI dispatch `if argv == ["settle"]: return settle_index(root)` (lines
    1459-1460). It is generated as GUARD_OFF and RETURN_DEL, at list positions **50 and 51**.
  - Measured in an isolated copy (`s14-7/mr/run3419.log`):
    - unmutated: `99 checks, 0 failed` rc 0, in 4 s;
    - mutant 1459: `0 failed`, so it SURVIVES;
    - mutant 1460: `0 failed`, so it SURVIVES.
  - Both are beyond prepr's default cap: `--max-mutants "${MUTANT_MAX:-40}"`, `prepr.sh:4491`.
  - 19 of the 51 mutants sit inside `self_test()` (lines 809-1448), and they fill the cap first.
- **PR 3425 at 779c9432: 2 of 2 sites caught.**
  - 58 mutants are listed; 16 of them are in `tools/audit/seat/orchestrator_tick.py`.
  - The reviewer's M3, deleting the `one_pr` clear, is listed as `orchestrator_tick.py:1220
    GUARD_OFF`, at position 16. That is behaviourally the same deletion.
  - The reviewer's M4, the except branch fail-open, is listed as `:1203 CONST_SWAP return False`,
    at position 15. That is the reviewer's exact mutant.
  - The full run with `--cmd "python3 -I tools/audit/seat/orchestrator_tick.py --self-test"` took
    31 s (`s14-7/mr/full.log`). Both mutants are in its SURVIVED list. The other 8 survivors in
    production code are lines 1196-1200, and 2 more are self-test lines.
- **PR 3427 at 7cbfa680: 0 of 2 sites caught.**
  - M2b is in `tools/audit/seat/shims/seat-gh`, which is not `*.py`. It is not generated.
  - M3b drops the conjunct ` and "steps" not in j` from `codescan_wait.py:102`. That line gets
    only RETURN_DEL (`--list`). RETURN_DEL makes `carried_over` falsy everywhere. That is the
    verdict's M3a, which its self-test kills ("M3a carried_over False: 1 failed"). The
    conjunct-drop survivor is not reachable.
- **PR 3428 at 9774026d: 0 of 4 sites caught.**
  - `hot-render` is a conditional expression, `plan_page.py:663-664 ... if r["hot"] else ""`.
  - `hot-gates` and `hot-discharged` are comprehension conjuncts, `plan_page.py:235-236`.
  - `hot-notdone` is a dict-value conjunct, `plan_page.py:297`.
  - None is generated. The 65 listed mutants include no line among 235, 236, 297, 663 or 664
    (`s14-7/mr/list-3428.txt`).
- **PR 3431 at 808a8eeb: 0 of 1 site caught.**
  - `tests/harness.py` is under `SKIP_PREFIXES` (`:66`), so `--list` generates 0 mutants for the
    whole PR.
  - The mutant itself, a `sys.path` anchor reverted to a relative literal, is not an operator in
    any case.
- **Totals.**
  - At the default cap of 40, 2 of 11 sites are caught (18%). Uncapped, 3 of 11 are (27%).
  - Counted by PR, a pre-handoff run would have removed the whole block on 1 of 5 PRs (3425).
    3419 would still have blocked on its YAML site.
  - 8 of the 11 sites are outside the operator set or the path filter. No setting of the cap or
    the command reaches them.
- **Precision on the two heads that catch anything:**
  - 3419: 35 of 51 mutants survive. 19 are in production or `main()` code and 16 in `self_test()`.
  - 3425: 12 of 16 survive, 10 of them in production code.
  - That is 47 survivors to answer, against 3 reviewer-named Python sites.
  - **18 of the 47 (38%) mutate the kill command itself.** They are lines inside the self-test
    function: 16 at 3419 (lines 809-1448) and 2 at 3425 (`:4156`, `:4158`, after `def self_test`
    at 2736). No pin in the code under test can kill them. The CALL_DEL and GUARD_OFF ones delete a
    check, so they survive by construction. For example, `selftest_scope.py:1421 CALL_DEL`,
    `:1422 GUARD_OFF` and `:1426 CALL_DEL` (`s14-7/mr/full-3419.out`).
- **Null control.**
  - The unmutated self-tests pass at both heads: `99 checks, 0 failed` at 3419, and no
    `BASELINE FAILS` line in either full run.
  - A killed mutant is reported as killed: 3419 lists 51 mutants and 35 survive, so 16 are
    killed. The instrument therefore distinguishes kills from survivals.
- **The arms' trigger.** No roster field names a group's self-test command. None of the 439
  groups at bc6ecd8e3c has a key containing `cmd`, `self` or `mutant`. Arm (a)'s condition "when
  the roster group names a self-test command" therefore holds for no group today.
- **Who owns `mutant_run.py`.**
  - At bc6ecd8e3c, no group lists it in its files.
  - The only group owning `tools/audit/seat/` as a whole is R10-REVIEW-CARRY, which is `done`.
  - The groups that built the driver, R10-MUTANT-RUN-DRIVER and R10-FLY-MUTANT-RESTORE, are `done`.
- **Current hand use.** 3 of the 46 dispatch briefs in `s14/seat/dispatch/` name `mutant_run`:
  `brief-3423-repair2`, `brief-3428-repair2` and `brief-3431-repair`.
  - The 3431 brief's run is vacuous: 0 mutants, by `SKIP_PREFIXES`.
  - The 3428 brief's "zero unanswered survivors" cannot show that the verdict's four survivors are
    killed, because none of the four is generated.

Cost:
- **(a) handoff REFUSE.**
  - Benefit: 1 of 5 blocks removed in the sample. That is 1 review round plus 1 repair round, at
    the 111-minute median quoted by the RCA (`R10-RCA-MUTATION-VACUOUS.md` section 5).
  - Standing cost: one `mutant_run --diff` per tools/ handoff, 31-116 s in the sample. It also
    obliges answering every survivor: 35 and 12 at the two catching heads, 18 of them in the
    self-test itself.
  - The refusal turns that list into blocking paperwork on every tools/ PR, including the 4 of 5
    in the sample where it catches nothing.
  - It adds a check to `body_push.sh` or `prepr.sh`, both hot files.
  - It needs a new roster field, which is an edit to the roster schema and lint.
- **(b) the command in the brief.**
  - The same benefit, on the same 1 of 5.
  - The same answering cost without the refusal: prepr's WARN line already says "the body answers
    each" (`prepr.sh:4495`).
  - The per-group command would need deriving in `cloud_dispatch.py`, a hot file, or a new roster
    field.
- **The deferred self-test-body skip.**
  - About 10 lines in `mutant_run.py`: skip added lines inside a `self_test`/`_self_test` function
    span, plus one self-test arm.
  - It would be a new S group, because there is no live owner.
- No capped file is edited by this ruling.

Binding:
- **(a): REJECT.** The binding cost is precision against reach. It prevents the block on 1 PR of
  5. 8 of the 11 sites are outside the operator set, so no tuning reaches them. And it would make
  47 survivors blocking paperwork on the two heads it catches anything on, 38% of them mutations
  of the self-test itself. Its trigger field exists on 0 of 439 groups.
- **(b): REJECT.** It has the same reach of 1 of 5. The answering cost moves to every first-round
  tools/ fixer, and it costs a hot-file change to `cloud_dispatch.py`. That is marginal, not
  clearly positive.
  - The orchestrator's per-repair hand request stays the orchestrator's call, with the two limits
    measured above:
    - a `tests/` diff gets 0 mutants;
    - expression-level sites, conjuncts and non-Python files are never generated, so "zero
      unanswered survivors" from `mutant_run` does not show that a verdict's named survivor is
      killed.
- **Root cause: not newly owed.**
  - `defect-root-cause.md:89-95`'s audit-class clause counts judged findings and sweep seams. It
    does not count review-verdict classes.
  - This class already went through the friction route: `R10-RCA-MUTATION-VACUOUS.md`.
  - That record's population-T refusal is "a refusal that depends on a number nobody has" (line
    116): the cost of a tools/ mutation arm. That number is now measured. An arm exists
    (`mutant_run --diff`). It costs 31-116 s per run and reaches 2-3 of 11 sites at 6% precision
    against reviewer-named sites (3 of 47).
  - The numbers do not reverse the refusal. Population T stays a recorded refusal, now priced.
  - The 5 new instances are 4 in tools/ (population T) and 1 in `tests/`, which neither the
    record's populations nor the instrument covers.
- **The self-test-body skip: DEFER.**
  - Per run it is measured: 18 of 47 survivors (38%) are self-test lines, and at 3419
    they push the one reachable site past the cap of 40.
  - Its benefit across runs is not measured. The instrument is used by hand in 3 repair briefs,
    and their fixers' answer cost is not yet known.
  - It changes on either of two things:
    - a measured fixer cost of answering self-test-body survivors in those 3 repair rounds, read
      from their bodies when they hand off;
    - a live group taking `tools/audit/seat/mutant_run.py` into its files, which would carry it
      for the price of one arm.
