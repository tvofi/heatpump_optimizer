Part of #2716. This lands P3's workflow and its measuring half. The roster's `fixes` list for this group is empty, so the body gets no closing keyword (the same reason R10-FAHRENHEIT's body gave); the issue's closure is the roster record step's.

P3 of an audit round did not exist: `audit-verify` produced a class-grouped draft roster and the fix wave consumed it, so no seat owned the architecture, nothing reviewed the plan, and the stamp had no way to say whether a merged dS was one the plan predicted. This lands that stage and its measuring half.

- `.claude/workflows/audit-plan.js` — the P3 workflow, between `audit-verify` and the fix wave: read the draft roster (an input, never dispatched as it stands) and measure the fork's holdouts; the architect's steps 1-4 (component view, quality scenarios, every verified finding triaged exactly once, groups by owning seam); steps 5-9 (ADRs, moves with a predicted dS per metric, fitness functions, the roster, risks); publish the plan on the constant `plan/r<N>`; the plan reviewer attacks that published SHA and returns `Plan review: approve|revise <sha>`, two revise rounds at most, then the owner gets the open points; record the verdict in `REVIEW.md`. It pushes the plan ref and never opens a pull request.
- `tools/audit/seat/plan_audit.py` — `ledger` parses each merged PR's `## Architecture score` block, reconciles it metric by metric against `PLAN.json`'s moves, and demands the moves' sum account for `score.py --diff <fork> <head>`: a merged metric no move names, a planned group with no body, an unexplained dS, an inadmissible reading or WORSENS each fail, so a dS no planned move explains is `metric-gamed` rather than banked. `snapshot`/`compare` record and compare the round's holdouts — `tests/structure.py`'s budgets, the archscore gate-only tripwires, the behaviour inventory (entities, services, option steps, card tabs), the mutation kill rate and change coupling over a fixed 200-merge window — with both sides measured by the base's `archscore.vector` and the base's `tests/structure.py`, and `--allow structure:<metric>` printing a declared exception as `ALLOWED` rather than hiding it. Neither `score.py` nor `vector.py` is re-implemented.
- Wiring: `INSTRUMENTS.md` entries; the `instrument-self-tests` job runs the new `--self-test` and greps its tally; the P3 driver in `tools/policy/check-wave-script.mjs`; two `PUSHERS` entries for the refs the prompts name; `tests/closures.json` records `plan_audit.py` in `tests/entities.py`'s INERT READS, because that script reads the directory (`tools/pr/ci_predict.py --apply-inert` wrote the entry the Linux lane's recording would, and predicts no red once it is there).
- `tests/entities.py` — the py-spy stub behind the `hb:positive_control` retry checks counts its calls with `case $(wc -l < calls)`, and macOS pads that count (` 1`), so the stub always took its last answer and four retry checks read a first-try pass: `4 of 2463 ENTITY CHECKS FAILED`. The count is stripped the way the tree's other callers already do (`tools/pr/push.sh`, `app_push.sh`), and the script prints `ALL 2463 ENTITY CHECKS PASSED`. The gate runs it for this diff in `MODE: FULL`, because the `INERT_EXCEPT` fix below edits `tests/closure.py`.

The fix-review round added three changes, each its own commit:

- **The coupling self-test owns its git identity** (`e16413f5f`). `throwaway_git_init` returns the throwaway environment and the fixture bound it to `env` and then discarded it, while `git()` inherited the caller's: on a runner with no global identity the first `git commit` exited 128, so `25 checks, 0 failed` was environment-dependent. The block now runs under `throwaway_git_environ()` — the tree's own mechanism for a self-test that drives production code making its own git calls — and a new arm pins the identity to `t <t@t>`. The rejected alternative was an `env=` parameter on `git()` threaded into `coupling()`: `coupling()` is production code whose default is the real repository, so that puts a test-only parameter on its signature and still leaves the arm blind on a box that has an identity.
- **The coupling census reads renames by name-status** (`c3ec79823`). `git diff --name-only` collapses a rename onto its destination, which `tests/closure.py`'s census refuses under `RENAME_SITES` because a collapse hides a deleted path from a list the gate scopes on. The census now reads `--name-status -M` and takes the destination, so one rename is one module. The cheaper alternative, `--no-renames`, satisfies the census but splits a rename into a deleted plus an added module and records a co-change nobody made: measured on the self-test's own fixture as `cochange_per_100 33.3333` (detected) against `66.6667` (undetected), and the new arm is what separates them.
- **`audit-plan.js` leaves INERT** (`fd36e08a1`). `tests/entities.py` runs `node --check` over every file `codeql.yml`'s `.claude/workflows/*.js` path-ignore matches, so the gate reads the new workflow; `.claude/` is an INERT prefix, so the file was declared unread while being read. It joins `INERT_EXCEPT` beside `web-fix-wave.js` and `audit-find.js`, and `tests/entities.py`'s recorded closure, via `closure.write_closures` (the one writer). An `inert_reads` entry was rejected: it would keep calling a file the gate reads inert, which is the defect.

## Head

fd36e08a1e06fe84a71e410dbbb91c9ac224980f

## Mutation proof

Every arm below is in the tree and was observed red under its mutation and green on the restored tree. The `plan_audit` battery restores to `plan_audit self-test: 27 checks, 0 failed`.

The twelve predicates in `tools/audit/seat/plan_audit.py` (unchanged by this round, re-stated for the whole instrument):

- `UNEXPLAINED metric` append disabled: `FAIL a merged metric no planned move names is refused`, `FAIL and its flagged run exits non-zero on the same input the passing run exits 0`.
- `if group not in by_group` disabled: `FAIL a merged group the plan never names is refused`.
- structure rise comparison disabled: `FAIL a raised structure metric is a regression`.
- tripwire rise comparison disabled: `FAIL a raised gate-only tripwire is a regression`.
- behaviour removal comparison disabled: `FAIL a removed card page is a holdout regression`.
- `if rate < was` weakened: `FAIL a falling mutation kill rate is a regression`.
- coupling comparison disabled: `FAIL a rising change coupling is a regression`.
- the tolerance comparison disabled: `FAIL a dS the moves do not account for is refused`.
- `OWED body` append disabled: `FAIL a planned move with no merged body is OWED`.
- `INADMISSIBLE` append disabled: `FAIL an inadmissible end-to-end reading fails the round`.
- `WORSENS` append disabled: `FAIL a WORSENS end-to-end reading fails even with no named regression`.
- the `unallowed` allow-filter disabled: `FAIL the plan's declared structure exception allows that one rise`.

The two arms this round added, and their mutations:

- `with throwaway_git_environ(), tempfile.TemporaryDirectory(...)` reduced to `with tempfile.TemporaryDirectory(...)`: `FAIL the fixture commits under the harness's own identity, not the box's tvofi <70032254+tvofi@users.noreply.github.com> ...`, and with the caller's identity stripped the run dies at the first `git` call with `CalledProcessError ... exit status 128` — the CI failure this round fixes.
- `git("diff", "--name-status", "-M", ...)` rewritten to `--name-status --no-renames`: `FAIL a rename alone is one module, so it adds no co-change pair {'window': 50, 'merges': 3, 'pairs': 2, 'occurrences': 2, 'cochange_per_100': 66.6667}`. Rewritten back to `git("diff", "--name-only", ...)`: `python3 tests/closure.py selftest` prints `FAIL no rename-detecting --name-only diff under RENAME_SITES [tools/audit/seat/plan_audit.py:322: ...]` and `1 of 117 closure shrink pins FAILED`.

The closure fix, against one synthetic recording of `tests/entities.py` (its committed closure plus `.claude/workflows/audit-plan.js` read as INERT):

- `INERT_EXCEPT` entry removed: `closure: files on the INERT list are inside a recorded closure (committed tests/closures.json): .claude/workflows/audit-plan.js` (the #357 refusal).
- closure entry removed: `UNDER-SCOPED: tests/entities.py really reads 1 file(s) the committed closure does not list: .claude/workflows/audit-plan.js`.
- both restored: `closure: committed closures cover every file this run touched`.

Thirteen mutations of `.claude/workflows/audit-plan.js` (unchanged by this round):

- empty-draft throw disabled: `FAIL an empty or absent draft roster stops P3`.
- dropped-triage throw disabled: `FAIL a triage that drops a verified finding stops P3`.
- duplicate-triage throw disabled: `FAIL a triage that keeps one finding twice stops P3`.
- unplanned-group throw disabled: `FAIL a group with no move entry stops P3`.
- publish SHA check disabled: `FAIL a publish that is not a 40-hex commit stops P3`.
- reviewer-SHA check disabled: `FAIL a reviewer answering for another tree stops P3`.
- verdict SHA check disabled: `FAIL a recorded verdict that is not a 40-hex commit stops P3`.
- draft path rewritten: `FAIL the read step is pointed at the audit-verify draft and measures the fork holdouts`.
- the review prompt's `ref = sha` line dropped: `FAIL the reviewer is pointed at the published plan ref and its SHA`.
- the `Plan review:` line's SHA dropped: `FAIL the verdict file carries the contract line with the SHA it answers for`.
- the constant ref renamed: `FAIL the verdict push is the constant plan/r11 ref and opens no pull request` and `FAIL the reviewer is pointed at the published plan ref and its SHA` (one mutation, two arms).
- the not-approved sentence dropped: `FAIL and the recorded verdict says the plan is not approved`.
- the two-round bound widened to three: `FAIL two revise rounds at most, then the owner gets the open points (no third review)`.

Both checks were also red while the file was wrong and green after the fix: the driver printed `209 passed, 5 failed` against the first draft of `audit-plan.js` (a backtick inside a prompt template literal closed it early, so the body did not parse), and `219 passed, 0 failed` once fixed; `check-wave-script.mjs` reported `1 failed` on a handoff stub that did not also approve the review, and `0 failed` after the stub was completed.

## Null control

The unmodified tree, over the flow study's range — the reading P3's target is defined against:

    python3 tools/audit/archscore/score.py --diff 399098f63 57f0c9c77
    Architecture score: dS +74.6109 WORSENS (inadmissible: private_cross_module 9->12; literal_clone_copies 178->186; card_clone_copies 99->108; computed_attr_access 31->32)

Both refs are fixed SHAs, so that figure is not a function of `main` and this round's diff cannot move it.

The new holdout check, run on the same two trees, finds one of those four regressions by itself and nothing else that is not a detector drift:

    python3 tools/audit/seat/plan_audit.py snapshot --ref 399098f63 --instrument 399098f63 --out /tmp/pa-fork.json
    python3 tools/audit/seat/plan_audit.py snapshot --ref 57f0c9c77 --instrument 399098f63 --out /tmp/pa-study.json
    python3 tools/audit/seat/plan_audit.py compare --fork /tmp/pa-fork.json --stamp /tmp/pa-study.json
      REGRESSED structure dead_methods: 0 -> 1
      REGRESSED tripwire computed_attr_access: 31 -> 32
    HOLDOUT FAIL

Against this head the same comparison names only `structure dead_methods: 0 -> 1`, the base's older `tests/structure.py` counting a method the stamp's own ratchet counts as 0 (`tests/structure.py` reports `dead_methods 0 <= 0` at this head); declared as the plan's exception it reads `ALLOWED structure dead_methods: 0 -> 1` and `HOLDOUT PASS`, and two snapshots read by different instruments are refused with `HOLDOUT FAIL instrument`.

The coupling flag change is the one part of this round that could move a snapshot, so it is measured at both ends of its input range rather than assumed. `coupling()` recomputed over the same 200-merge window at both refs, under the collapsing `--name-only` diff and under `--name-status -M`, gives the same four numbers — `399098f63` `merges 184, pairs 403, occurrences 586, cochange_per_100 318.4783`; `57f0c9c77` `merges 189, pairs 114, occurrences 145, cochange_per_100 76.7196` — so neither snapshot moves and neither is re-taken. The arm that would have caught a silent move is the self-test's rename fixture, where the two readings do separate: `33.3333` detected against `66.6667` not.

The closure fix's null control is its own recording, run against the tree before and after. The recording is the shape the Linux lane writes for `tests/entities.py` — its committed closure, with `.claude/workflows/audit-plan.js` filed under `inert_reads` because the tree that recorded it still classified the file INERT:

    D=$(mktemp -d)
    python3 -c "import json;t=json.load(open('tests/closures.json'));json.dump({'script':'tests/entities.py','files':t['closures']['tests/entities.py'],'inert_reads':['.claude/workflows/audit-plan.js']},open('$D/tests_entities.py.json','w'))"
    python3 tests/closure.py check --in-dir "$D" --partial

At the reviewed head that prints `INERT READS UNDER-APPROXIMATED ... tests/entities.py: .claude/workflows/audit-plan.js`; at this head it prints `closure: committed closures cover every file this run touched`, because `_load_recording` re-reads the same bytes under the new INERT list and moves the path into that script's reads.

## Figures

`git diff $(git merge-base origin/main HEAD)...HEAD --stat` — ten files, 1027 insertions and 1 deletion, against merge base `484d9902222031f8e081df9f53b52ffd50fcc0af`.
`python3 tests/closure.py select --diff 484d9902222031f8e081df9f53b52ffd50fcc0af --workdir "$D"` — `MODE: FULL -- every test script runs, nothing is scoped out. reason: tests/closure.py changes the gate itself, so every closure is suspect`. The reviewed body's `MODE: SCOPED -- 2 script(s) run, 31 scoped out` was two-dot and used a ref that is not this branch's merge base; the mode is FULL because the `INERT_EXCEPT` fix edits `tests/closure.py`, which is a gate file.
`python3 -I tools/audit/seat/plan_audit.py --self-test` — `plan_audit self-test: 27 checks, 0 failed`; under a caller environment with the identity stripped (`env -u GIT_AUTHOR_NAME -u GIT_AUTHOR_EMAIL -u GIT_COMMITTER_NAME -u GIT_COMMITTER_EMAIL GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1 ...`) the same `27 checks, 0 failed`.
`python3 tests/closure.py selftest` — `ALL 117 closure shrink pins PASSED`.
`python3 tests/closure.py check --in-dir <a recording of tests/entities.py listing .claude/workflows/audit-plan.js in inert_reads> --partial` — `closure: committed closures cover every file this run touched` (prior to the fix: `INERT READS UNDER-APPROXIMATED ...`).
`node tools/policy/check-wave-script.mjs` — `224 passed, 0 failed`, of which 15 are the P3 arms.
`node tools/policy/brief_lint.mjs` — rc 0.
`python3 tests/structure.py` — `STRUCTURE RATCHET PASSED`, every metric at its recorded budget.
`python3 tools/audit/seat/ref_privacy.py --check` — `0 refused`.
`python3 tools/audit/seat/selftest_wiring.py --check` — `98 self-testing, 98 wired, 0 unwired`.
`PYTHONPATH=tests/hastub python3 tests/entities.py` — `ALL 2463 ENTITY CHECKS PASSED`.
The 25-mutation battery above restores to `plan_audit self-test: 27 checks, 0 failed` by the command line on this list; each mutation reddened exactly the arm(s) named above.

## Red checks

Six checks fired at the reviewed head `2f15a24cd`. Each is named here with the answer the root-cause rule requires; the local detector of each fix is green at the head named under `## Head`. Nothing below is claimed green in CI, and no fail-closed behaviour was weakened to move any of them.

- `governance / instrument-self-tests` (job 121982854726, failing step 23, "Show the P3 move ledger and holdout check refusing their own fixtures"): `plan_audit.py:553 git("commit", ...)` raised `CalledProcessError ... exit status 128`, because the fixture inherited the runner's git identity and a runner has none. Cheaper detector: `python3 tools/audit/seat/plan_audit.py --self-test`, about 2 s — the same script this step runs, and the gap is environmental rather than logical (a seat's box has an identity, so it passes there). Fixed by `e16413f5f` plus an arm that is red on a box that *does* have an identity; standing cost of the arm is one `git var` call.
- `tests / closures` (job 121983008811, step 10, "Fail if tests/closures.json under-approximates"): `INERT READS UNDER-APPROXIMATED: tests/entities.py: .claude/workflows/audit-plan.js`. Cheaper detector: `python3 tests/closure.py check --in-dir <recording> --partial`, under 1 s, reproduced locally with CI's exact message before the fix. Fixed by `fd36e08a1`; no new standing cost — the check already exists and CI already runs it.
- `tests / closures-autofix` (job 121990578626, step 9, "Report whether the repair happened"): `AUTOFIX: skip-merge-failed`. The autofix is the cheaper detector here and it did its job — it refused because a blind re-derivation produces the INERT-and-recorded pair #357 refuses, which is why the remedy is a judgement call. Same cause and same fix as `tests / closures`; no separate countermeasure is owed.
- `tests / fast (3.14)` (job 121983008846, step 11, "Run the suite"): `>>> FAILED: python3 tests/closure.py selftest`, preceded by `1 of 117 closure shrink pins FAILED`. Cheaper detector: `python3 tests/closure.py selftest`, about 3 s, and it is red on macOS too — the cheapest detector is the one that fired. Fixed by `c3ec79823`.
- `pr-contract / pr-contract` (job 121993018230, step 10, "Check the body against the contract"): the body said `## Red checks` none while four were red. This section is the answer; the detector is `tools/pr/prepr.sh <body>`, which runs the same body lint locally in seconds.
- `gate` (job 121993189412, step 4, "Judge this head"): `FAIL tests / fast (3.14): failure (this run)`. A cascade of the closure selftest red above; it has no separate cause and no separate detector.

Two of these were read in the logs as different defects before the step conclusions were checked, and the reading is recorded here so the next re-read does not repeat it. The `BAD ... FAIL closed: analysis 11 (actions): HTTP 404` lines in `instrument-self-tests` belong to `tools/pr/local_alerts.py --self-test`, a step that **passed**: its mutant arms deliberately break the reader and the log prints the matching `ok` after each. The `MUTATION TABLE REFUSED -- nothing was measured: ... 1 not started for --budget-minutes` in `tests / fast (3.14)` is likewise a self-test fixture (`NOT RUN x.py:1 CONST`, followed by `ok a budget refusal names a tail-cut site ... all refused, none PASSED`); no mutation budget was touched.

## Forward-carry

`none`

## Friction

`none`
