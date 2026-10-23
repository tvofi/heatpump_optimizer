R10-POLICY-LINT-FAMILY. Part of #2410; part of #201. Two instrument fixes and one owed pin, all in `tools/policy/`:

1. **The family arm no longer re-files a member's occasions (#2410).** `statsFamilies` in `tools/policy/policy_lint.mjs` now leaves out every pull request that a member at or over the threshold already files on its own would-open line. It counts the remaining entries per pull request through a new `byPr` map in `bump`. The table row and the would-open line both say what was taken out. The mutation family also gains the four synonyms that #2561 section 5 measured: `test-vacuous`, `vacuous-test`, `vacuous-check` and `mutant-survives`.
2. **`--pr-body` asks the raise gate itself (Triage P-F, recurrence 2).** `budget_raise_gate.py --check-body FILE` runs `justification()` on a body file, prints the reason and exits 0 or 1. `policy_lint.mjs` `raiseJustification` runs it on any body that carries `## Raise justification`. So pr-contract, `body_patch.sh` and `prepr.sh` now refuse what the gate would refuse at merge. `body_patch.sh` is unchanged.
3. **The `--record-known-bad` pin (#2408 carry).** `policy_lint_mutants.mjs` gains a `record-known-bad` arm. It drives `cmdRecord` with its write captured rather than made, at both ends, and kills a mutant that restores #2408's shadowing `const at`.

**#2410's disposition, for the orchestrator's row.** #2410's count depends on the keying rule in `policy_lint.mjs`, and this change moves that rule. The merged bodies are untouched. On the recorded window (`## Figures`), the same input reads 7 at both ends, but over different pull requests:
- at base, 7 = mutation-vacuous's 5, which that member already files, plus #2390 and #2444;
- at head, 7 = #2297, #2360, #2391, #2400, #2376, #2444 and #2390, none of which any member files.

The keying change alone, without the synonyms, reads 2 there, below the threshold, so it prints no family line (`M2`). The live window #2410 now names, `v7.0.4..origin/main` (47 merges), was **not measured**: `GH_TOKEN` is rejected here, and unauthenticated reads stop at 60 an hour, against about 141 reads for that window. Whether #2410 stays over the threshold on that window is the cron's next run to say. This change does not close it. The roster's `fixes` is empty, so this PR uses Part of rather than Closes.

**Design departures, with the reasons.**
- *The trigger is the heading alone, not "or the PR touches a `*_budgets.json`".* 19 of the 26 merges since v7.0.0 that touched a budget file raised nothing (`raises_between`, `## Figures`). An owner's own approval owes no section, so a path trigger would refuse routine re-records. All 4 recorded gate-refused handoff bodies carried the heading.
- *The lint's heading test follows Python's `splitlines()`/`strip()`, not JS's `split('\n')`/`trim()`.* Without that, 13 of the 45 bodies in the agreement corpus part between the two readers (`M5`).
- *One line in the lint mirrors the gate (the heading test), so the concept is registered.* `agreement.mjs` gains `raise-justification`, which compares the gate's reading with the lint's.

**Alternatives that lost.**
- Mirroring `JUSTIFICATION_PAID`/`JUSTIFICATION_SCORE` in the `.mjs`: a mirror drifts, and covers only the clauses someone has already been refused on.
- Calling the gate from `body_patch.sh`: that fixes one of the three callers.
- For the family: suppressing the family whenever any member fires. That loses the occasions no member files, which is 7 of the 12 mutation-obligation PRs on the recorded window.
- For the family: summing member rows instead of taking the union. That breaks the distinct-PR rule the controls window pins.

## Head

`e884b8900b875c5e478cea97899fa9fc603dff8a`, on merge base `a6620c30adcdf0d9529ee66977694bfa2a06d5c3` (`origin/main` at the time of measurement, 2026-10-23T12:07Z).

## Mutation proof

**Failing first.** With the fixtures and pins added and no fix yet, `node tools/policy/policy_lint.mjs` printed:
- `FIXTURE VACUOUS: with mutation over threshold on every occasion the family holds, the family line fired anyway -- the same three pull requests filed twice (#2410) ...`
- `FIXTURE VACUOUS: the double window's family reaches 5 only by re-counting mutation-vacuous's 3 filed occasions, and it printed a family line ...`
- `FIXTURE VACUOUS: the residual window did not print exactly one ``mutation (family)`` line at 3 ...`
- after the raise pin was added, `FIXTURE VACUOUS: the raise-justification arm on prepr/raise/bare-payments.md drew 0 error(s)`

`python3 tools/policy/budget_raise_gate.py --self-test` printed `249 checks, 5 failed`: the four `--check-body` rows that need the mode, and the unreadable-body row.

**Each fix line deleted on the head** (`python3 dev/audit/harnesses/r10_policy_lint_family_mutants.py --agreement-json <agreement_py.py --out>`; it restores each file byte for byte):

- `M1-no-exclusion` (`taken = new Set()`): `rc=1`. The controls, double and residual windows each print `FIXTURE VACUOUS` (the three lines above).
- `M2-no-synonyms` (the four words dropped): `rc=1`. `FIXTURE VACUOUS: the residual window did not print exactly one ``mutation (family)`` line at 3 ...`
- `M3-no-raise-call` (`const raise = null`): `rc=1`. `FIXTURE VACUOUS: the raise-justification arm on prepr/raise/bare-payments.md drew 0 error(s)`
- `M4-check-body-ok` (the gate's `--check-body` verdict forced to pass): `rc=1`. Three gate self-test rows fail, for example `FAIL --check-body: a bare ``Payments tried:`` heading over a list exits 1 and names the clause: got (0, True), want (1, True)`.
- `M5-js-heading-test` (`split('\n')` and `trim()` restored in the heading test): `rc=1`. `RESULT divergent=13`, with these `raise-justification` rows:
  - 3 where Python strips and JS does not: a leading `\x1c` or `\x85`, and a trailing `\x1f`;
  - 9 line breaks Python splits on and JS does not: `\r`, `\v`, `\f`, `\x1c`, `\x1d`, `\x1e`, `\x85`, U+2028, U+2029;
  - 1 that JS trims and Python keeps: U+FEFF.

  The U+00A0, U+3000, U+200B, `\r\n` and leading-tab probes agree under both rules.
- `RESTORED 5 file(s)`.

**The #2408 shadowing mutant** (a `const at = sha` line under `const sha = recordedAtSha()` in `cmdRecord`):
- At base it survives: the base default run reads `rc=0`, `FIXTURE ok: 93 error(s) hold 254 pins`, and base `policy_lint_mutants.mjs` has no arm that reaches `cmdRecord` (`grep -c 'record-known-bad\|cmdRecord'` reads 0).
- At head it is killed: `node tools/policy/policy_lint_mutants.mjs` prints `PIN record record-known-bad with a local ``at`` shadowing ``at(path)``, it threw: at is not a function`.

## Unpinned sites

none: no `custom_components/` file changes, so the CI `mutation` lane draws no mutant from this diff. Every new predicate is pinned by a mutant above that turns its owning check red.

## Null control

- `prepr/raise/good.md` (the gate's accepted shape) and `prepr/good.md` (no section) draw no pr-body error.
- The two recorded r10-scores bodies the gate accepted (`8f564875d`, `52d40a9ac`) draw no raise error.
- The `acceptance` family window still prints exactly one family line per map at 4, with no member over the threshold. The no-family stats windows still carry no family member (pin unchanged).
- The `record-known-bad` arm's unmutated drive writes exactly one ledger document, with a `recorded_at` that resolves as a commit. `git status` shows `dev/governance/config/policy_known_bad.json` unmodified after the lane runs.
- `agreement.mjs` reads `raise-justification: 2 readers, 45 items, 0 divergent`, and 13 divergent under `M5`.

## Figures

- `FIXTURE ok: 93 error(s) hold 256 pins across 12 check classes` at head; 254 pins at base. Command: `node tools/policy/policy_lint.mjs`.
- `budget_raise_gate self-test: 249 checks, 0 failed`. Command: `python3 tools/policy/budget_raise_gate.py --self-test`.
- `MUTANTS ok`, with `record-known-bad` listed in the record lane. Command: `node tools/policy/policy_lint_mutants.mjs`.
- `RESULT divergent=0 unregistered=0 dead=0 refused=0`, including `pair raise-justification: 2 readers, 45 items, 0 divergent`. Commands: `python3 -I tools/policy/agreement_py.py --out <f>` then `node tools/policy/agreement.mjs --py-json <f>`. Also `SELF-TEST 27 of 27 probes held` (`node tools/policy/agreement.mjs --self-test`) and `agreement_py self-test: 7 checks, 0 failed` (`python3 -I tools/policy/agreement_py.py --self-test`).
- **The finder's harness at both ends, on the recorded window.** Command: `node dev/audit/harnesses/r10_family_replay.mjs [<root>]`. It reads `dev/audit/rca/harness-friction/verdict_first_lines.tsv`, which #2561 fetched over `v7.0.0..df6ca4bc`. Every number below comes from that file.
  - Base (`<root>` = an `a6620c30` checkout): `RESULT line=mutation-vacuous count=5`; `RESULT line=mutation (family) count=7`; `CLAUSE counted as DISTINCT pull requests across them (8 entries in all)`. This reproduces #2561's recorded `stats_v7.0.0.txt` rows `5 / 6 mutation-vacuous` and `7 / 8 mutation (family)`.
  - Head: `RESULT line=mutation-vacuous count=5`; `RESULT line=mutation (family) count=7`; `CLAUSE ... (7 entries in all), less the 5 that mutation-vacuous already files on its own line`.
  - Null control, the harness's distinct-PR list per word: `mutation 2390`; `mutation-vacuous 2275,2305,2365,2404,2406`; `mutation-survivor 2444`; `test-vacuous 2297,2360`; `vacuous-test 2391`; `vacuous-check 2400`; `mutant-survives 2376`. The union is 12 PRs. At base the family's 7 are mutation-vacuous's 5 plus 2390 and 2444. At head they are the 12 less those 5.
  - Without the synonyms (`M2`) the head prints no family line: only `RESULT line=mutation-vacuous count=5`.
- **The finder's instance for P-F.** Every commit on `origin/handoff-body/r10-flow-arch-planner` and `origin/handoff-body/r10-scores` (6 bodies), run through `budget_raise_gate.py --check-body` and `--pr-body` at base and head. Commands per body: `python3 tools/policy/budget_raise_gate.py --check-body <b>`, and `node tools/policy/policy_lint.mjs --pr-body <b>` from each checkout, counting `Raise justification` errors. The loop over the six bodies is a one-off, kept in scratch:
  - `9b5742049`, `c6c8fee16`, `f2b98c1df`, `84e2aaf66`: gate rc=1; base raise errors 0; head raise errors 1.
  - `8f564875d`, `52d40a9ac`: gate rc=0; base 0; head 0.
  - So the lint now refuses exactly the bodies the gate refuses, 4 of 4, and passes the 2 it accepts.
- **Path-trigger measurement.** 26 merges in `v7.0.0..a6620c30` touched a `*_budgets.json` (`git log --first-parent --merges v7.0.0..origin/main -- '*_budgets.json'`). 7 of them raised: #2647, #2633, #2585, #2586, #2368, #2311, #2209. 19 did not. Rule: `budget_raise_gate.raises_between(merge-base(^1,^2), ^2)` non-empty. The script is a 20-line probe over the gate's own function, kept in scratch, which is allowed for a one-off.
- **Class seams (step 8)**, from `git grep -n -E 'Raise justification|JUSTIFICATION_(PAID|SCORE|HEADING)|justification\(' -- ':!dev/audit' ':!dev/programme' ':!*.md'`, outside fixtures:
  - `budget_raise_gate.py`: the owner.
  - `merge_train.py:1077`: calls `g.justification` itself; already shared.
  - `policy_lint.mjs`: closed in this diff, by calling the gate.
  - `queue_pre_flight.py:463` and `merge_train.py:546/2618`: fixture bodies, not readers.

  The family fold's seams are the declared families × the two maps. One function, `statsFamilies`, serves all four, and the three family windows pin it.
- **Scoped gate**: `MODE: SCOPED -- 1 script(s) run, 32 scoped out` (`python3 tests/closure.py select --diff a6620c30 --workdir <d>`). It names `tests/entities.py`: `ALL 2406 ENTITY CHECKS PASSED` at the head above. Also `tests/harness_headers.py`, which reads the two new harnesses' `INERT READS`: `ALL 109 HARNESS HEADER CHECKS PASSED`.
  - An earlier entities run, at `08b2e294f`, failed 1 of 2406: `gate lease priority: concurrency control: two waiters released in one poll, exactly one holds the slot`. That is a timing check in `gate_lock.py`'s self-test, which this diff does not touch. It passed on both later runs. Both ran under a Python 3.13 venv with `tests/requirements-ci.txt`, because the seat recipe's CPython 3.14.7 had no download here.
- `run_always` (`tests/run.sh`):
  - `claims hygiene: origin/main ok`. Command: `tests/env_drift.py --claims-only origin/main`.
  - `ALL 112 closure shrink pins PASSED`. Command: `tests/closure.py selftest`.
  - `layout self-test: ok`, rc=0, with `reference 959 finding(s)`, the same count as base. Command: `tests/layout.py`.
  - Before `9ac1676af`, the four `prepr/raise/` fixtures copied `prepr/good.md`'s retired paths, and layout refused 8 new references to them. They now cite `tools/policy/check-wave-script.mjs` and `dev/governance/dimensions/D7.md`.
- `STRUCTURE RATCHET PASSED`. Command: `python3 tests/structure.py`.
- `CI PREDICT: no closures or fast red predicted against a6620c30adcd`. Command: `python3 tools/pr/ci_predict.py --base origin/main`, after `--apply-inert` added the two harnesses' `INERT READS` entries.

## Approval

Owner approval is owed for `tools/policy/` (`POLICY_GLOBS`): `policy_lint.mjs`, `policy_lint_mutants.mjs`, `budget_raise_gate.py`, `agreement.mjs`, `agreement_py.py` and the fixtures. The roster's owner gate merges it on approval under the mandate. None is recorded yet. No `*_budgets.json` changes, so there is no raise.

## Red checks

none

## Forward-carry

none. The runbook carry (#2422: `nudge.md` and `orchestrator.md` name `open_pr.sh` without `--over-cap`) concerns policy files. The carry itself leaves them unedited, and its contract is already held in `tools/audit/seat/INSTRUMENTS.md`, so this PR moves nothing there. The root-cause analysis of the raise-gate grammar is the separate seat r10-rca-raise-gate-grammar, by dispatch.

## Friction

`environment`: `cost`: `GH_TOKEN` is rejected (HTTP 404 on a public read), and `seat_venv.sh` asks uv for a CPython 3.14.7 that has no download. So the live `v7.0.4` window went unmeasured, and the scoped gate ran on a 3.13 venv.
