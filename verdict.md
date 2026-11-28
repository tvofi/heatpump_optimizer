Fix review: merge 70965f42a8cef9c1233940f5375f22599a80594a

bus-nonce: 56dced5496fee9d63c44b2f4aa1cff54
pending-ci: gate

Round 1 (first review at this head; review scope full).

## Evidence

- RESULT setup: `cloud-setup.sh --check` OK; the role diff `git diff $(git merge-base origin/main HEAD)...origin/main -- dev/governance/roles/` is empty, so the contract is current.
- RESULT merge: `git merge-tree --write-tree origin/main 70965f42a8` exit 0 (tree c582374476); origin/main is the PR's base ac9045c223.
- RESULT version: `VERSION`, the manifest and `RELEASE_NOTES.md` are untouched in the three-dot diff; no `*_budgets.json`, golden or claim file is in it.
- RESULT mutation proof (ev/mutation_proof.txt): the new `tests/entities.py` check's block, extracted verbatim from its comment to `_mut_ordpool` and run against the head's `tests/mutation_table.py`, reads OK. All six of the body's mutants read FAIL. So do four of mine: `dear > COSTLY_PIN_DRAWS`, `dear >= COSTLY_PIN_DRAWS - 1`, `return pool[:cap], held` in place of `return drawn, held`, and `len(drawn) > cap`. The restored tree reads OK. Two of mine survive; see Findings.
- RESULT wiring mutant (ev/harness_after_wiring_mutant.txt): with main()'s `args.scope == "changed"` flipped to `!=` in the after checkout, the harness reads `DRIVER tests/features.py runs=11` and `ESTIMATE 9824 s`, which is the before draw. The harness kills it, as the body states.
- RESULT harness, both ends (ev/harness_before.txt, ev/harness_after.txt). The harness is `dev/audit/harnesses/mutation_draw_cost.py`, sha1 c49593fa33174ba8c52c7f2799a74138ef5b2541, matching the body. It runs at ebd70acc5e (#3897's head) with `--cost tests/env_drift.py=397`. Before: 10 sites, 9 pinned to features.py, `DRIVER tests/features.py runs=11`, `ESTIMATE 9772 s` (163 min). After, on the same checkout with the head's `tests/mutation_table.py`: 4 sites drawn, 2 pinned to features.py, 10 `passed over` lines that all name features.py, `DRIVER tests/features.py runs=4`, `ESTIMATE 5396 s` (90 min). The body reads 9745 s and 5376 s; the gap is sleep jitter under `--scale 100`. The site lists and run counts match exactly. Carry: dismissed: evidence, not a finding
- RESULT harness provenance (step 9): the harness was built by the fixer, not a finder. This hotfix's finder is the timed-out CI job the body cites, and the before arm reproduces it. Carry: dismissed: evidence, not a finding
- RESULT class (step 6): the rule is the threshold itself. `recorded_seconds` puts tests/features.py at 1617 s and tests/entities.py at 1067 s over 900 s, and the next is tests/stress.py at 435 s (ev/recorded_seconds.txt). Both costly drivers fall under `costly_pin` by measurement, with no list to keep current. `--scope full` (nightly.yml `--scope full --max 40`) keeps the uncapped draw. Only pinned sites can be passed over, because `costly_pin` returns None for an unpinned site.
- RESULT commit 4c16879e8d → 462e051a84 is comment and docstring only in `tests/mutation_table.py` (non-comment diff lines: none), as the body states.
- RESULT cheap checks at the head (ev/cheap_checks.txt): `STRUCTURE RATCHET PASSED`; `Architecture score: dS +0.0000 NULL`; `MODE: SCOPED -- 3 script(s) run, 31 scoped out.`; `env_drift.py --all` reads `NO UNCLAIMED DRIFT` and `NO STALE FIXTURE` over 56 scenarios.
- RESULT closures.json: its one added line lists the new harness among a read set. That is the classification `tests/entities.py` requires of a new tracked file, and it is earned by that file (step 14).
- RESULT CI: `merge_train.py classify 70965f42a8 --pr 3943` printed `WAIT 70965f42a8cef9c1233940f5375f22599a80594a pending: gate red: none` on every run from 16:22Z to 16:52Z (ev/classify.log). At the last read, `tests / closures`, `tests / coverage` and `governance / instrument-self-tests` were still in progress, and every other required context had passed. Hence the `pending-ci: gate` line. The relay posts this verdict only at GREEN on this head.
- RESULT red checks: `tests / nightly-status` is red, and it is not in the `merge_train.py owed-reds` set, so no answer is owed. `gate` reads failure, and its log says `FAIL run(s) [46163875242] at this head are still being judged; their gate decides`. That is a premature aggregate, not a test red, and classify reads it as pending. `instrument-self-tests` had not concluded at the last read, so whether a red was introduced is left to classify at the relay.
- RESULT `tests / mutation`: the diff writes no `custom_components/` line, so `--scope changed` draws no mutant at this head. Its green therefore evaluates nothing about this change, and the mutation proof above is the one that bears. Carry: dismissed: evidence, not a finding

## Findings

- Surviving mutant: in `costly_pin`, `seconds.get(pin, 0.0)` changed to `seconds.get(pin, 1e9)` passes the new check. No arm drives a pinned site whose driver has no recording. At this head the domain is empty: every `killed_by` script has a recording (ev/recorded_seconds.txt). The `0.0` default also fails open to the pre-PR draw. Carry: dismissed: no pinned killer lacks a recording at this head, and the default fails open to the uncapped pre-PR draw, so the mutant changes no draw today.
- Surviving mutant: `COSTLY_PIN_DRAWS = 3` passes the check, which reads the constant by name. The value 2 is a tuning figure, and it is measured by the harness above (90 min at 2), not pinned by a test. Carry: dismissed: the check is parametric in the cap by design; its value is the harness's measurement, re-taken by anyone who moves it.
