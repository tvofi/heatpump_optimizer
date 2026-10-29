R10-FRICTION-MUTATION-SURVIVOR: the root-cause record for the recurring-friction key `mutation-survivor` (#2840), at `dev/audit/rca/R10-RCA-MUTATION-SURVIVOR.md`, and the one countermeasure that passes its cost test, landed in `dev/governance/rules/ci-autofix.md` under the orchestrator's mandate (scope `all`, the brief).

- **Count at this base:** 4 PRs / 6 entries (#2579 ×3, #2817, #2820, #2912); the issue's 3 / 5 snapshot predates #2912.
- **The brief's premise holds for two of the four.** #2579 and #2820 are reviewer hand mutants on `tools/` self-tests, outside `--pin-killed`'s `custom_components/` reach and outside any generated class: recorded, nothing built.
- **Named cause (#2817, #2912, and #2832 under `mutation-vacuous`):** every survivor path through `mutation-autofix` is green — `measurement()` discards the `left unpinned` count, `apply_pins()` returns `changed` once any kill lands, and `closure.AUTOFIX_QUIET` holds `changed` and `skip-nothing-killed` — while `ci-autofix.md` told the seat to wait on `tests / mutation` and act only when `mutation-autofix` went red. Bodies wrote "pinned by `mutation-autofix`" for sites CI had already printed `-- lives`.
- **Process state: (c).**
- **Cost test:** 4 of the window's 28 PRs that change `custom_components/*.py` carried such a survivor past handoff; median 161 min block-to-next-verdict. A local `--pin-killed` before every handoff (measured at #2817's head: 0 of 29 mutants decided in 30 min locally; 366 runner-minutes in CI) is refused; the rule correction costs 0 s and 0 net policy tokens; making the survivor loud in `mutation-autofix` costs 0 s and is carried to `R10-FLY-LEDGER-SAMPLE`.

Part of #2840. The brief says this record closes it on delivery, but the roster lists 2840 under the group's `issues` and not its `fixes`, so pr-contract's intended list refuses a closing keyword (Friction below); the orchestrator closes it at delivery, or adds 2840 to `fixes` and this line becomes `Closes`.

## Head

Code head: `94d61e94e521143564951e92a943f57d7ee20623`, on merge base `88c6ad5bbec69bfe157e04597a74d0c9c3e4775c` (`origin/main` when measured, 2026-10-29 UTC). Every figure below was taken on that tree; the window figures are a function of `origin/main` at `88c6ad5bb` and are stamped with it.

## Approval

This diff changes policy: `dev/governance/rules/ci-autofix.md` and its two generated copies. It is made under the orchestrator's mandate, scope `all`, which the group's roster brief at `88c6ad5bb` states ("A countermeasure that edits a policy file is approved under the orchestrator's mandate (scope all); no step waits on tvofi"). The approving review at this head records it and cites the mandate it uses (decision 0013). No budget leaf is raised: `ci-autofix.md` lands at 1469 of its 1469-token cap.

## Mutation proof

n/a: no production code, test or check lands. The landed countermeasure is rule text addressing state (c); the check-shaped countermeasure (C) is carried to `R10-FLY-LEDGER-SAMPLE` with its red/green acceptance (record section 7), and `defect-root-cause.md`'s demonstration is owed by the PR that builds it. The detector the record does exercise, `--pin-killed`, was run at #2817's reviewed head and stopped at the seat's 30-minute limit with 0 of 29 mutants decided (its cost is the measurement, record section 6).

## Null control

- Policy corpus at the merge base: `.claude/rules/ci-autofix.md` 1468 of 1469 tokens; at this head 1469 of 1469 — the added bullet is paid by wording trims that move no claim (`node tools/policy/policy_lint.mjs --budgets`).
- The enumerator's window loop over a path no file matches counts 0 PRs (`nonexistent/*.py`), against 28 for `custom_components/*.py`.
- The site-key regex finds no key in #2579's or #2820's blocks (`sites=0`), whose survivors are `tools/` code: it separates the two populations rather than matching every block.
- `mutblocks.tsv` holds 0 `FETCH-FAILED` rows over the window's 285 PRs.

## Figures

- `mutation-survivor` 4 PRs / 6 entries, 285 merged PRs in the window: `node tools/policy/policy_lint.mjs --stats --since v7.0.4` (copy: `dev/audit/rca/mutation-survivor/stats_v7.0.4.txt`), at `88c6ad5bb`.
- The window's mutation-family blocks and their cited site keys (5 PRs cite a key: #2632, #2817, #2832, #2912, and #2745's metric-gamed block, which is not a mutation verdict and is dispositioned out): `python3 dev/audit/rca/mutation-survivor/mutblocks.py <window PR list>`; the PR list is `git log -1 --format=%s` of each `git rev-list --first-parent --merges v7.0.4..88c6ad5bb`.
- 28 of 285 PRs change `custom_components/*.py`: `git diff --quiet $m^1...$m^2 -- 'custom_components/*.py'` over the same merges; control `nonexistent/*.py` 0.
- #2817 `mutation-pins` concluded 16:39:51Z, `mutation-autofix` success 16:41:11Z at `4fbe4c6a5`; #2832 `mutation-autofix` success at `d076f22c9`: `bash dev/audit/rca/mutation-survivor/pinsbefore.sh 2817 2832 2834`.
- Block-to-next-verdict 91 / 161 / 496 min (#2817 / #2912 / #2832): the `created_at` of each PR's `Fix review:` comments, `gh api repos/tvofi/heatpump_optimizer/issues/<N>/comments`.
- `AUTOFIX_QUIET`'s mutation tuple in its current form since `dc66cc878` (2026-09-24): `git log -S'"skip-nothing-killed", "skip-head-moved"' -- tests/closure.py`.
- `--pin-killed` at #2817's reviewed head `3b437b851` against `f54f40cc1`, `--jobs 4`, Python 3.13 with `tests/requirements-ci.txt`: stopped at 30 min with 0 of 29 mutants decided; baselines 284 s / 463 s / 505 s (`dev/audit/rca/mutation-survivor/pin2817.txt`).
- CI's six `mutation-pins` shards at #2817's `4fbe4c6a5`: 30.9 to 77.9 min each, 366 runner-minutes: each shard's `started_at`/`completed_at`, `gh api repos/tvofi/heatpump_optimizer/commits/4fbe4c6a5/check-runs`.

## Red checks

none. Scoped gate: `MODE: SCOPED -- 1 script(s) run` (`tests/entities.py`), `ALL 2470 ENTITY CHECKS PASSED`; `python3 tests/structure.py` `STRUCTURE RATCHET PASSED`; `node tools/policy/rules_sync.mjs --check` ok.

## Forward-carry

- Lands in `dev/programme/rosters/wave-r10-groups.json`, group `R10-FLY-LEDGER-SAMPLE`'s `carry`. Countermeasure C — `mutation-autofix` reddens when its measurement leaves an added site alive, naming each site in its summary line; acceptance: red on #2817's `4fbe4c6a5` measurement shape (`N pinned, 2 left unpinned`), green on `0 left unpinned`, quiet on `skip-head-moved` — and the answer to the group's own #2840 carry ("the survivors share a cause, in the autofix's status vocabulary, not in `--pin-killed`; #2579 and #2820 are `tools/` hand mutants with no shared cause"): record section 7. Carry: R10-FLY-LEDGER-SAMPLE
- `R10-RCA-FRICTION-RESIDUE` section 6 left #2660's post-`662a380` entry as "residue 1": it is #2832, this cause, and closes with the same countermeasure. Recorded in this record's section 5, which that record's readers reach through #2840. Carry: dismissed: a record recounts, it is not rewritten; the correction lives where the cause is named

## Friction

- `R10-FRICTION-MUTATION-SURVIVOR`: contradiction: the brief says "Closes the issue on delivery" while the roster holds #2840 in `issues` and not `fixes`, so `prepr.sh`'s preflight refuses a closing keyword on that issue ("not in the intended list"). Carry: R10-FRICTION-MUTATION-SURVIVOR

- `.claude/rules/ci-autofix.md`: contradiction: the rule said to act when `mutation-autofix` goes red, and `closure.AUTOFIX_QUIET` keeps it green on every survivor path (#2817, #2832, #2912). Carry: R10-FLY-LEDGER-SAMPLE
- `.claude/rules/ci-autofix.md`: cost: the file sits at its token cap, so the survivor bullet was paid by wording trims across four paragraphs. Carry: dismissed: paid within the cap, no raise
- `tools/policy/policy_lint.mjs`: unclear: one cause spans four class words (`mutation-survivor`, `mutation-vacuous`, `mutation-unpinned`, `mutation-untriaged`) and a rule id, so #2840 filed two of its instances beside two that are not. Carry: dismissed: the untaught-vocabulary fold is `R10-RCA-FRICTION-RESIDUE` section 4's countermeasure
- `seat-environment`: cost: job logs and artifacts for `tests / mutation-pins` answer 403 through this seat's proxy, so the `-- lives` lines are quoted from the reviewer's evidence, not re-read. Carry: dismissed: environment, the check-run conclusions and times were re-read
