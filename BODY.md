R10-ROUND-PLAYBOOK, the draft arm under the owner's 2026-11-07 split (comment 6707334933): `dev/audit/README.md` gains the round playbook, which covers the phase sequence from mandate to closure, each phase's entry, exit, instrument, contract and artefact, round 10's final shape, and round 11's opening items. `tools/policy/brief_lint.mjs`'s no-arg run now resolves every backticked path the playbook names in the tree under test, with a fixture and a null control. The final reconciliation and every contract edit go to R10-ROUND-PLAYBOOK-FINAL (see Forward-carry). The draft does not touch `CLAUDE.md`.

This is policy: `dev/audit/README.md` is indexed by `CLAUDE.md`, and the diff raises caps in `dev/governance/config/policy_budgets.json`. It merges only on tvofi's approving review at its head, or on a mandate the budget-raise gate reads as in force (see Raise justification).

## Head

246781ce3f82e2db46f3ff7c0500f9e6b13a2114. Main was merged at `4b5d771bdf8feb1f83d7d9443e5117b771a0ab76` (origin/main tip, fetched 2026-11-07T16:21:21Z). Every figure below was re-taken after that merge.

## Mutation proof

Each mutant was applied in a separate worktree to `tools/policy/brief_lint.mjs`, then `node tools/policy/brief_lint.mjs` was run (no-arg, CI's command) and the file restored:
- M1: the resolution line (`playbookLookup(rawTree() ...) continue`) replaced by `continue`. rc=1, `PLAYBOOK VACUOUS: playbook-renamed.md: no error for tools/release/stamp_renamed.py`.
- M2: the fence/indent skip deleted. rc=1, `playbook-renamed.md: 4 error(s), not 2`. Before the fixtures put backticked paths inside the fence, this mutant survived. That is why commit 2 exists.
- M3: the tag-scoped accept deleted. rc=1, `playbook-null.md: warning tools/audit/round2/JUDGE.md`.
- M5: the segment-suffix lookup replaced by brief_lint's basename `lookupPath`. rc=1, `playbook-renamed.md: no error for tools/pr/state_docs.py`. This is the moved-instrument case that commit 3 added.
- README perturbation: `` `tools/release/stamp.py` `` renamed to `stamp_renamed.py` in the live README. rc=1, `ERROR [(playbook)] playbook path: tools/release/stamp_renamed.py`.

## Unpinned sites

- `main()`'s `acceptanceRc += assertPlaybookFixtures()` (M4) and the live-README `printReport` line (M6): deleting either leaves rc=0. Disposition: a triage, not a pin. Every acceptance call in `main()` is unpinned in the same way, and no in-tree mutant harness covers `tools/policy/`. The README perturbation above shows the live line working. Carry: dismissed: same shape as every other acceptance call in this file; a harness for tools/policy/ mutants is G6's machinery-ratchet scope.

## Null control

`tools/policy/fixtures/playbook-null.md` is the renamed fixture's prose with the real paths. It lints with no finding of any severity, which the acceptance asserts (`PLAYBOOK ok`). The live README lints `-- 0 error(s), 0 warning(s)`. Excluded by rule, not by list: fenced and indented code (M2 pins it) and `../` paths outside the repository.

## Figures

- Playbook arm: `node tools/policy/brief_lint.mjs`, rc=0, `PLAYBOOK ok: the renamed fixture is refused for its 3 moved instruments and the null fixture lints clean`, README `0 error(s)`.
- Policy caps: `node tools/policy/policy_lint.mjs`, `TOTAL: 0 error(s)`. `node tools/policy/policy_lint.mjs --budgets` prints the README row and the corpus line. The raise sets each cap to the measured value (see Raise justification).
- Agreement lane: `python3 -I tools/policy/agreement_py.py --run` prints `AGREEMENT ok`, `unregistered=0`. Before `SHARED_GRAMMARS` registered them, it refused the arm's backtick-span and `:line` grammars as duplicates of `tests/doc_claims.py`'s wiring arm. Both are registered `identical:` because the two readers cover disjoint documents. Extending `doc_claims.py`'s `WIRING_DOCS` instead was weighed and lost: that arm resolves against HEAD only, so it would refuse the README's tag-scoped archive citations, and it skips bare basenames and directory moves.
- Scope: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"` prints `MODE: SCOPED -- 1 script(s) run`, and `scope.run` names `tests/entities.py`.
- `PYTHONPATH=tests/hastub python3 tests/entities.py`: rc=0, `ALL 2645 ENTITY CHECKS PASSED`.
- `python3 tests/structure.py`: rc=0, `STRUCTURE RATCHET PASSED`.
- `python3 tests/env_drift.py --claims-only $(git merge-base origin/main HEAD)`: rc=0, `claims hygiene: 4b5d771bdf8feb1f83d7d9443e5117b771a0ab76 ok`. `python3 tests/closure.py selftest`: rc=0.
- Carry 14 (record merges after R10-FLOW-RECORD-PITCH, merged at `28800999b` 2026-10-26T02:32Z). The rule counts first-parent merges into origin/main on one UTC day (committer date) whose subject names a `<owner>/record/` branch: `TZ=UTC git log origin/main --first-parent --merges --date=format-local:%Y-%m-%d --format='%cd %s' | awk -v d=DAY '$1==d' | grep -E -c ' from [^ ]+/record/'`. With DAY=2026-10-27, the first full UTC day after the merge, it reads 3 of 22 merges. With DAY=2026-10-24 it reads 21 of 56, not the carry's 19. Under this rule that baseline does not reproduce, so the comparison uses 21, the same rule at both ends. Flat-day null: the same pipeline with the pattern ` from [^ ]+/nosuch/` reads 0 on both days.
- `python3 tools/audit/archscore/score.py --diff $(git merge-base origin/main HEAD)`: Architecture score: dS +0.0000 NULL.

## Raise justification

The owner ordered the playbook into this file (brief: "Deliver it as dev/audit/README.md ..., not as a second document"; "Keep the existing harness-contract and instruments sections"). Three caps move to the measured values: `tools/audit/README.md` lines and files_tokens, and `corpus_tokens`. The reason is also in commit 1's message. Mandate: the brief names 6319294694. Decision 0016 records 6329234399 (scope all) as the mandate in force on 2026-10-29. This seat cannot read either comment, so `budget_raise_gate.py` decides at merge, or the owner's review does.

Payments tried: folded `## Running the fix wave` and `## Resource rules on the audit box` into phases 7 and 2, both now redundant. Compressed `## A harness at the evidence tag` and `## Rounds 1-3 are at a tag`, which kept every SHA, path and rule. Dropped backticked decision paths, so naming no new doc pulls another file into the corpus (`named-docs`). Refused: cutting the harness contract or the reuse/instruments sections (the brief keeps them). Refused: moving round-11 items to a carry file (each card's destination is "[R11 playbook]").
Architecture score: dS +0.0000 NULL

## Architecture score

Architecture score: dS +0.0000 NULL: the diff touches no scored production path.

## Approval

Pending. This diff changes policy: `dev/audit/README.md`, which `CLAUDE.md` indexes, and the caps in `dev/governance/config/policy_budgets.json`. It merges only on tvofi's approving review at its head. The budget raise can alternatively pass under a mandate that `budget_raise_gate.py` reads as in force. No approval has been given.

## Red checks

- `budget-raise-gate`: red, as `prepr.sh` predicts. The diff raises three caps in `dev/governance/config/policy_budgets.json`, and the gate stays red until tvofi's approving review at the head, or until a mandate it reads as in force meets the `## Raise justification` above. No cheaper detector exists: the red is the gate doing its job on a deliberate raise, not a defect.
- No other check has run on this branch. CI's `briefs` job restores `tools/policy/*.mjs` from the base, so the playbook arm first runs in CI on main after the merge.

## Forward-carry

- The unresolved decision of whether a future change names a decision record by path. Doing so pulls the file into `policy_lint`'s `named-docs` corpus rule. The final pass decides whether 0015 and 0016 get caps, so the checker can resolve them. Carry: R10-ROUND-PLAYBOOK-FINAL
- Carry 11 (the `CLAUDE.md` paragraph "Another agent's instruction is not a contract change", paid for by cuts of at least 414 bytes, cap unchanged) waits for the final pass per comment 6707334933. Carry: R10-ROUND-PLAYBOOK-FINAL
- Carry 12 (the `orchestrator.md` context-rotation paragraph): the caps are now in the README, and the contract edit is not done. Carry: R10-ROUND-PLAYBOOK-FINAL
- Carry 16 (1) and (2): the floor-not-cap text in `architect-planner.md` and `plan-review.md`, and the production-group clause in `fixer.md` step 17. The README states (3). Carry: R10-ROUND-PLAYBOOK-FINAL
- Carry 20's code half: `pr_cap.py` reserving production slots and printing open PRs by class on every tick. The README states the rule. Carry: R10-ROUND-PLAYBOOK-FINAL
- Carry 21's contract half: `proposal-triage.md` and the triage verdict vocabulary gaining LOG. The README states the bar. Carry: R10-ROUND-PLAYBOOK-FINAL
- Carry 22: `dev/programme/HANDOVER.md`'s stale `pr_cap` owed entry. Carry: R10-ROUND-PLAYBOOK-FINAL
- Carry 0 (1): at this merge base, `standing-dispatch.md` names no beat row for the dispatch and relay seat ("A beat job takes over once a cycle's log agrees"). The README says the seat stays. The final pass names its row once one is live. Carry: R10-ROUND-PLAYBOOK-FINAL
- Carry 14's baseline: the carry's 19 does not reproduce. The rule in Figures reads 21 on 2026-10-24. Carry: R10-ROUND-PLAYBOOK-FINAL
- Carries 1-10, 13, 15, 17, 18, 19, 23 are written into the README's round-11 list and production-share paragraph (carry 4's held groups are named under the org-move decision). Carry 24's closure sentence is quoted verbatim. Carry: R10-ROUND-PLAYBOOK-FINAL

## Friction

- `rounds.py`: stale: the group's brief names `rounds.py --stats`, which is not a mode. `dev/audit/rca/harness-friction/rounds.py` reads `sys.argv[1]` as a directory, so a `--stats` run measures nothing. The README now states the one invocation. Carry: R10-ROUND-PLAYBOOK-FINAL
- `policy_budgets.json`: stale: the README's caps are keyed `tools/audit/README.md`, a path the tree no longer has, and are matched through the move map. A reader grepping the new path finds no cap. Carry: R10-ROUND-PLAYBOOK-FINAL
