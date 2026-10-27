Part of #2716. This lands P3's workflow and its measuring half. The roster's `fixes` list for this group is empty, so the body gets no closing keyword (the same reason R10-FAHRENHEIT's body gave); the issue's closure is the roster record step's.

P3 of an audit round did not exist: `audit-verify` produced a class-grouped draft roster and the fix wave consumed it, so no seat owned the architecture, nothing reviewed the plan, and the stamp had no way to say whether a merged dS was one the plan predicted. This lands that stage and its measuring half.

- `.claude/workflows/audit-plan.js` — the P3 workflow, between `audit-verify` and the fix wave: read the draft roster (an input, never dispatched as it stands) and measure the fork's holdouts; the architect's steps 1-4 (component view, quality scenarios, every verified finding triaged exactly once, groups by owning seam); steps 5-9 (ADRs, moves with a predicted dS per metric, fitness functions, the roster, risks); publish the plan on the constant `plan/r<N>`; the plan reviewer attacks that published SHA and returns `Plan review: approve|revise <sha>`, two revise rounds at most, then the owner gets the open points; record the verdict in `REVIEW.md`. It pushes the plan ref and never opens a pull request.
- `tools/audit/seat/plan_audit.py` — `ledger` parses each merged PR's `## Architecture score` block, reconciles it metric by metric against `PLAN.json`'s moves, and demands the moves' sum account for `score.py --diff <fork> <head>`: a merged metric no move names, a planned group with no body, an unexplained dS, an inadmissible reading or WORSENS each fail, so a dS no planned move explains is `metric-gamed` rather than banked. `snapshot`/`compare` record and compare the round's holdouts — `tests/structure.py`'s budgets, the archscore gate-only tripwires, the behaviour inventory (entities, services, option steps, card tabs), the mutation kill rate and change coupling over a fixed 200-merge window — with both sides measured by the base's `archscore.vector` and the base's `tests/structure.py`, and `--allow structure:<metric>` printing a declared exception as `ALLOWED` rather than hiding it. Neither `score.py` nor `vector.py` is re-implemented.
- Wiring: `INSTRUMENTS.md` entries; the `instrument-self-tests` job runs the new `--self-test` and greps its tally; the P3 driver in `tools/policy/check-wave-script.mjs`; two `PUSHERS` entries for the refs the prompts name; `tests/closures.json` records `plan_audit.py` in `tests/entities.py`'s INERT READS, because that script reads the directory (`tools/pr/ci_predict.py --apply-inert` wrote the entry the Linux lane's recording would, and predicts no red once it is there).
- `tests/entities.py` — the py-spy stub behind the `hb:positive_control` retry checks counts its calls with `case $(wc -l < calls)`, and macOS pads that count (` 1`), so the stub always took its last answer and four retry checks read a first-try pass: `4 of 2463 ENTITY CHECKS FAILED`. The count is stripped the way the tree's other callers already do (`tools/pr/push.sh`, `app_push.sh`), and the script prints `ALL 2463 ENTITY CHECKS PASSED`. The scoped gate runs it for this diff because the diff touches `governance.yml` and the seat tools.

## Head

96c66df4ba3a243afedd4eba05f98cbc5dd96718

## Mutation proof

The twelve predicates in `tools/audit/seat/plan_audit.py`, each restoring to `plan_audit self-test: 25 checks, 0 failed`:

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

Thirteen mutations of `.claude/workflows/audit-plan.js`:

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

The new holdout check, run on the same two trees, finds one of those four regressions by itself and nothing else that is not a detector drift:

    python3 tools/audit/seat/plan_audit.py snapshot --ref 399098f63 --instrument 399098f63 --out /tmp/pa-fork.json
    python3 tools/audit/seat/plan_audit.py snapshot --ref 57f0c9c77 --instrument 399098f63 --out /tmp/pa-study.json
    python3 tools/audit/seat/plan_audit.py compare --fork /tmp/pa-fork.json --stamp /tmp/pa-study.json
      REGRESSED structure dead_methods: 0 -> 1
      REGRESSED tripwire computed_attr_access: 31 -> 32
    HOLDOUT FAIL

Against this head the same comparison names only `structure dead_methods: 0 -> 1`, the base's older `tests/structure.py` counting a method the stamp's own ratchet counts as 0 (`tests/structure.py` reports `dead_methods 0 <= 0` at this head); declared as the plan's exception it reads `ALLOWED structure dead_methods: 0 -> 1` and `HOLDOUT PASS`, and two snapshots read by different instruments are refused with `HOLDOUT FAIL instrument`.

## Figures

`python3 tools/audit/archscore/score.py --diff 399098f63 57f0c9c77` — `dS +74.6109 WORSENS`, wall time `6:41.14 total` on this box.
`python3 -I tools/audit/seat/plan_audit.py --self-test` — `plan_audit self-test: 25 checks, 0 failed`.
`node tools/policy/check-wave-script.mjs` — `224 passed, 0 failed`, of which 15 are the P3 arms.
The 25-mutation battery at this head: each mutation reddened exactly the arm(s) named above, and the restored tree printed the two tallies on this list.
`PYTHONPATH=tests/hastub python3 tests/entities.py` — `ALL 2463 ENTITY CHECKS PASSED` (before the `tests/entities.py` fix: `4 of 2463 ENTITY CHECKS FAILED`).
`python3 tools/audit/seat/ref_privacy.py --check` — `0 refused`.
`python3 tools/audit/seat/selftest_wiring.py --check` — `98 self-testing, 98 wired, 0 unwired`.
`python3 tests/closure.py select --diff 6fe5170cd7ce01e60ffebfc93e598c216e628fa3` — `MODE: SCOPED -- 2 script(s) run, 31 scoped out`.
`python3 tests/structure.py` — `STRUCTURE RATCHET PASSED`, every metric at its recorded budget.

## Red checks

none

## Forward-carry

none

## Friction

none
