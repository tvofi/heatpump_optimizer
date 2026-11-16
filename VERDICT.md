Fix review: blocked 673af8e9896e4da83ac093b7ac46143d16305a8a class-open: d1-inputs omits the configured entity slot CONF_COMPRESSOR_FREQ_SENSOR, and ten mutants of the enumerator survive its self-test

bus-nonce: 8e96f00649f6a2eff721483f4f47e5d4
pending-ci: gate

Round 1 (first review of this pull request; full scope). Measured from a detached worktree at 673af8e9896e4da83ac093b7ac46143d16305a8a, merge base 5825e1346c14eecace5c87c046558774145a94dc.

## Block

Two grounds, both on the instrument this pull request lands (`tools/audit/enumerate.py`) and its null control. Every item the review found is listed; none is paperwork.

1. `d1-inputs` is short of its population. Its rule is a module-level `CONF_*_ENTITY` of `const.py`; `const.py` also declares `CONF_COMPRESSOR_FREQ_SENSOR`, which `config_flow.py` offers through the entity selector (`_entity_of('sensor', 'frequency')`), `entry_config.py` `_WIRING` keeps across a factory reset as "an entity assignment", and `thermal_model.py` and `quiet_windows.py` read. The universe prints 50 lines; the configured entity slots are 51. D1 step 3 now says "Per line of `enumerate.py d1-inputs`", so a seat reporting examined over that universe reports the actual-frequency feedback sensor as covered without driving it, and the body's `## Forward-carry` discloses the limits of `d9-collections` and `d1-parsers` but not this one. Control: `ev/d1_inputs_population.py` (the reviewer's instrument, not the finder's) compares the universe with two independent enumerations and each names that one key; widening the predicate to `CONF_*_(ENTITY|SENSOR)` moves the count from 50 to 51 (`ev/d1_inputs_population.txt`). Owed: the slot in the universe by a rule that does not depend on the name's suffix (or the suffix rule plus the exception, pinned by a planted arm), and the self-test arm that fails without it.

2. The self-test does not pin the branches that print most of two cited universes. `mutant_run.py --spec ev/mutants.json --cmd "python3 -I tools/audit/enumerate.py --self-test" --in-place` at the head: `SURVIVED NULL`, 26 `KILLED`, 10 `SURVIVED` (`ev/mutant_run_spec.txt`). The ten the body names by hand are among the 26 killed. The survivors, each with what it does to the live universe at the head (`ev/survivor_live_effect.txt`); `--briefs` stays green under each:
   - M2-d1life-LIFE_CALLS-dropped: `or k in LIFE_CALLS` removed. `d1-lifecycle` falls from 41 lines to 16 (25 lost). The planted repo holds no `LIFE_CALLS` call.
   - M4-d1stores-STORE_VERSION-dropped: the `*STORE_VERSION` disjunct removed. `d1-stores` falls from 41 to 23 (18 lost). The planted repo holds only `CONFIG_ENTRY_VERSION`.
   - M5-d1stores-no-earlier-version-line-dropped: the `(no earlier version)` fallback removed. `d1-stores` falls from 41 to 25 (16 lost).
   - M1-d1excepts-label-always-narrow: every handler printed `narrow`. 98 of 256 `d1-excepts` lines change; no arm reads the label D1 step 5's universe is described by ("broad or narrow").
   - M3-d1life-entry-fn-dropped: `async_migrate_entry` dropped from `ENTRY_FNS`. `d1-lifecycle` loses 1 line; `PLANT`'s levels have a pinning arm, `ENTRY_FNS` and `LIFE_CALLS` have none.
   - M8-d1parsers-json-with-args: `and not n.args` removed. No live line moves today; no arm plants a `.json(x)` call.
   - M18-d2-step-shape-not-checked: the `M<n>` step check removed. A register row with a malformed step is accepted; the arm beside it covers an empty id only.
   - M27-d16-any-async_call: the `.services` receiver check removed. No live line moves today; no arm plants an `async_call` on another receiver.
   - M25-imports-from-package-import-name: the `from <package> import name` branch removed. No live line moves; no planted module uses that import shape.
   - M12-d9collections-module-level-self: `and "." in q` removed. No live or planted line moves; either an arm or the guard's deletion, as the body's rule for a guard whose removal changes no outcome.
   The body's `## Mutation proof` says a per-universe guard remains only where its removal changes an outcome and each has a self-test arm; M2, M4, M5 and M1 change the printed universe and no arm sees them. The diff-mode operators (GUARD_OFF, RETURN_DEL, CMP_BOUND, CALL_DEL, CONST_SWAP, STMT_DEL) do not draw a dropped disjunct or a dropped fallback, which is why the capped passes the body cites reported none of these.

## Findings

- Follow-up: `COMMON.md` states no rule that a finder reports examined over a universe, so the sentence is written once per brief (D0, D1, D2, D8, D9; D1, D8 and D12 also each restate the `--ledger` row format). The body's payment (4) declines the single statement because `COMMON.md` belongs to another group; once that group states it, these per-brief sentences are a payment against the rows raised here. Carry: dismissed: the group owning COMMON.md is carries-open and carry_audit lists no live target; the body's payment (4) already records the alternative and the saving is a sentence per brief

## Evidence

- Head re-read before return: `git ls-remote origin refs/heads/fix/r11-pre-briefs-census` prints 673af8e9896e4da83ac093b7ac46143d16305a8a. The body's `## Head` names this sha.
- `git merge-tree --write-tree origin/main 673af8e9896e4da83ac093b7ac46143d16305a8a`: exit 0, tree 790efe614ff81cc088bb46fe6ed2cc22b1fb122e, no conflict.
- `git diff 5825e1346c...origin/main -- dev/governance/roles/`: empty, the frozen contract is current.
- `VERSION`, the manifest, `RELEASE_NOTES.md`, `custom_components/` and `tests/golden/` are untouched by the three-dot diff; no fixture moves and no claim is owed, so `env_drift.py --all` was not run.
- RESULT self-test at the head: `SELF-TEST passed (134 arms)`, rc 0 (`ev/selftest_head.txt`). Matches the body.
- RESULT `--briefs` at the head: rc 0, 15 `ok` lines, D0 2, D1 6, D2 1, D8 1, D9 3, D12 1, D15 1 (`ev/briefs_head.txt`). Matches the body.
- RESULT null control at the merge base: `--briefs` rc 2 `REFUSE: no dimension brief cites a universe`; `d15-installs` and `d2-identities` rc 2 on the missing register (`ev/null_base.txt`). Matches the body.
- RESULT `check-wave-script.mjs` at the head: 223 passed, 0 failed; with `rotation.json` from the merge base: 221 passed, 2 failed, naming D0.M8 and D15.M9 (`ev/wave_head.txt`, `ev/wave_baserotation.txt`). Matches the body.
- RESULT `policy_lint.mjs` at the head: `TOTAL: 0 error(s) across 52 policy file(s)`; with `policy_budgets.json` from the merge base: `TOTAL: 14 error(s)`, all `[budgets]`, the rows the body lists (`ev/policy_lint_basebudgets.txt`). `--budgets` at the head prints each raised row at exactly its measured value and D9's line row at 64 of 65 (`ev/budgets_head.txt`): the raise is the size of the added prose, no more.
- RESULT `check_scopes.py --repo .` rc 0; `tests/layout.py` `layout self-test: ok`; `score.py --diff origin/main`: `Architecture score: dS +0.0000 NULL`.
- RESULT live universes at the head, line counts (`ev/live_universes.txt`): d0-grid 2400 (price-weather plane 40, the 8 by 5 the old D0 text typed), d0-modules 23, d1-lifecycle 41, d1-stores 41, d1-inputs 50, d1-solve-state 28, d1-excepts 256 (an independent `grep -c` of `except` lines over the package also gives 256), d1-parsers 31, d2-identities 30 (587 cells), d8-cells 396, d9-collections 19, d9-attributes 54, d9-solves 21, d12-cells 201 (18897 with pairs), d14-classes 56, d15-installs 1, d16-writes 38, d17-features 307.
- `bundles.json` steps M1, M2, M3, M4, M6, M7 equal `rotation.json` D15 round 10 coverage other than `none`; its evidence path is in the tree.
- Raise judgement (step 14): payments (1) to (6) read against the diff; none found that the body missed inside this group's files. The one outside it is the bullet under `## Findings`.
- Not re-derived: `tools/ci/selftest_closures.json` (the recorder takes about 559 s under strace; CI's lane grades it), the body's two capped diff-mode mutant passes, `tests/entities.py`, `tests/harness_headers.py`, `tests/structure.py` and `prepr.sh` (cited as CI's and the fixer's).
- No finder's harness exists for this group (a pre-round instrument build from evaluation cards); the instrument's own self-test and `--briefs` are the fixer's, and the mutant spec and `ev/d1_inputs_population.py` are the reviewer's.
- CI at this head, `merge_train.py classify 673af8e9896e4da83ac093b7ac46143d16305a8a --pr 3625`: `WAIT 673af8e9896e4da83ac093b7ac46143d16305a8a pending: gate red: none` on every run from 23:25:57Z to 23:55:59Z (`ev/classify_poll.txt`), rc 3 each time; no required check was red, so no `## Red checks` answer is owed at this reading. The block above does not turn on CI.
