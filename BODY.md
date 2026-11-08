R10-ROUND-PLAYBOOK, the draft arm under the owner's 2026-11-07 split (comment 6707334933): `dev/audit/README.md` gains the round playbook, which covers the phase sequence from mandate to closure, each phase's entry, exit, instrument, contract and artefact, round 10's final shape, and round 11's opening items. `tools/policy/brief_lint.mjs`'s no-arg run now resolves every backticked path the playbook names in the tree under test, with a fixture and a null control. The final reconciliation and every contract edit go to R10-ROUND-PLAYBOOK-FINAL (see Forward-carry). The draft does not touch `CLAUDE.md`.

This is policy: `dev/audit/README.md` is indexed by `CLAUDE.md`, and the diff raises caps in `dev/governance/config/policy_budgets.json`. It merges only on tvofi's approving review at its head, or on a mandate the budget-raise gate reads as in force (see Raise justification).

## Head
52583aaf49b8171acca2a83444aaac7350792f82. This is review round 1's repair of the blocked verdict at 8d4ff2f257655fb11e837c0c96a203abfdbab928 (comment 6721886055). One commit (the pin commit, the merge's first parent) adds the directory and `:line` cases to the playbook fixtures. origin/main had moved since the blocked head, so it was merged at `8a4cf2618c53a6dca6b65df3eae5efc8832d1796` (origin/main's tip at 2026-11-08T14:34Z), with no conflict. Every figure below was re-taken at this head.

## Mutation proof

Each mutant was applied in a separate worktree to `tools/policy/brief_lint.mjs`, then `node tools/policy/brief_lint.mjs` was run (no-arg, CI's command) and the file restored:
- M1: the resolution line (`playbookLookup(rawTree() ...) continue`) replaced by `continue`. rc=1, `PLAYBOOK VACUOUS: playbook-renamed.md: no error for tools/release/stamp_renamed.py`. Re-run at the pin commit: rc=1, same line.
- R2 (round-1 survivor, now killed): `playbookLookup`'s directory branch replaced by `if (token.endsWith('/')) return true`. At the pin commit: rc=1, `PLAYBOOK VACUOUS: playbook-renamed.md: no error for tools/audit/seatz/` and `5 error(s), not 6`. The renamed fixture now cites the renamed directory `tools/audit/seatz/`, and `REQUIRED_PLAYBOOK` requires it.
- R5 (round-1 survivor, now killed): the `:line` strip `.replace(/:\d+(?:-\d+)?$/, '')` deleted from `playbookCitations`. At the pin commit: rc=1, `no error for tools/audit/seat/beat_jobz.py` and `5 error(s), not 6`. The renamed fixture cites `tools/audit/seat/beat_jobz.py:12`, which without the strip fails the path pattern and is silently not a citation. The null fixture cites the real `tools/audit/seat/beat_jobs.py:12` and stays clean, which the acceptance asserts.
- Each mutant was applied in place to `tools/policy/brief_lint.mjs` and the file restored. `cmp` against the saved original printed RESTORED after the last one.
- M2: the fence/indent skip deleted. rc=1, `playbook-renamed.md: 4 error(s), not 2`. Before the fixtures put backticked paths inside the fence, this mutant survived. That is why commit 2 exists.
- M3: the tag-scoped accept deleted. rc=1, `playbook-null.md: warning tools/audit/round2/JUDGE.md`.
- M5: the segment-suffix lookup replaced by brief_lint's basename `lookupPath`. rc=1, `playbook-renamed.md: no error for tools/pr/state_docs.py`. This is the moved-instrument case that commit 3 added.
- README perturbation: `` `tools/release/stamp.py` `` renamed to `stamp_renamed.py` in the live README. rc=1, `ERROR [(playbook)] playbook path: tools/release/stamp_renamed.py`.

- Carry 26 (stated cap figure): the playbook arm now refuses `16 in round 10` or `open-PR cap is N`. Perturbation: the README text `Of the cap of 16 in round 10, 10 slots are reserved` made `node tools/policy/brief_lint.mjs` print `ERROR [(playbook)] playbook cap: 16 in round 10: the open-PR cap is read from tools/plan/replan.py, not stated`, rc=1; the restored text lints `0 error(s)`, rc=0. The fixture `playbook-renamed.md` gained the line `The open-PR cap is 16 in round 10.` as a refusal and the acceptance requires it (now `PLAYBOOK ok: the renamed fixture is refused for its 6 moved instruments ...`); the null fixture lints clean.

## Unpinned sites

- `playbookLookup`'s directory branch (R2) and `playbookCitations`' `:line` strip (R5), the two sites the round-1 verdict found surviving and undisclosed: pinned by a value check, the fixture pair, as Mutation proof shows (both mutants killed at the pin commit).
- `main()`'s `acceptanceRc += assertPlaybookFixtures()` (M4) and the live-README `printReport` line (M6): deleting either leaves rc=0. Disposition: a triage, not a pin. Every acceptance call in `main()` is unpinned in the same way, and no in-tree mutant harness covers `tools/policy/`. The README perturbation above shows the live line working. Carry: dismissed: same shape as every other acceptance call in this file; a harness for tools/policy/ mutants is G6's machinery-ratchet scope.

## Null control

`tools/policy/fixtures/playbook-null.md` is the renamed fixture's prose with the real paths. It lints with no finding of any severity, which the acceptance asserts (`PLAYBOOK ok`). The live README lints `-- 0 error(s), 0 warning(s)`. The null fixture also cites `tools/audit/seat/beat_jobs.py:12`, the real path at a line, so the `:line` strip resolves a real citation clean. Excluded by rule, not by list: fenced and indented code (M2 pins it) and `../` paths outside the repository.

## Figures

- Playbook arm: `node tools/policy/brief_lint.mjs`, rc=0, `PLAYBOOK ok: the renamed fixture is refused for its 6 moved instruments and the null fixture lints clean`, README `0 error(s)`.
- Policy caps: `node tools/policy/policy_lint.mjs`, `TOTAL: 0 error(s) across 50 policy file(s)`. `node tools/policy/policy_lint.mjs --budgets` prints the README row (`320  321  6058  6059`, lines and tokens against caps) and `corpus: ~68610 tokens, cap 68618 +band 500`. The raise sets each cap to the measured value (see Raise justification).
- Agreement lane: `python3 -I tools/policy/agreement_py.py --run` prints `AGREEMENT ok`, `unregistered=0`. Before `SHARED_GRAMMARS` registered them, it refused the arm's backtick-span and `:line` grammars as duplicates of `tests/doc_claims.py`'s wiring arm. Both are registered `identical:` because the two readers cover disjoint documents. Extending `doc_claims.py`'s `WIRING_DOCS` instead was weighed and lost: that arm resolves against HEAD only, so it would refuse the README's tag-scoped archive citations, and it skips bare basenames and directory moves.
- Scope: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"` prints `MODE: SCOPED -- 1 script(s) run, 32 scoped out.`, and `scope.run` names `tests/entities.py`.
- `PYTHONPATH=tests/hastub python3 tests/entities.py` at this head: rc=1, `4 of 2666 ENTITY CHECKS FAILED`. The four are the coverage-cache reuse check, the release-ZIP build check (`the build step fails`), and two Pages-workflow probes. Control: the same command at origin/main `8a4cf2618c53` in a detached worktree prints the same `4 of 2666 ENTITY CHECKS FAILED` with the same four check names, so this container fails them independently of the diff.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`.
- `python3 tests/env_drift.py --claims-only $(git merge-base origin/main HEAD)`: rc=0, `claims hygiene: 8a4cf2618c53a6dca6b65df3eae5efc8832d1796 ok`. `python3 tests/closure.py selftest`: rc=0.
- Brief carry 14 (record merges after R10-FLOW-RECORD-PITCH, merged at `28800999b` 2026-10-26T02:32Z). The rule counts first-parent merges into origin/main on one UTC day (committer date) whose subject names a `<owner>/record/` branch: `TZ=UTC git log origin/main --first-parent --merges --date=format-local:%Y-%m-%d --format='%cd %s' | awk -v d=DAY '$1==d' | grep -E -c ' from [^ ]+/record/'`. With DAY=2026-10-27, the first full UTC day after the merge, it reads 3 of 22 merges. With DAY=2026-10-24 it reads 21 of 56, not the carry's 19. Under this rule that baseline does not reproduce, so the comparison uses 21, the same rule at both ends. Flat-day null: the same pipeline with the pattern ` from [^ ]+/nosuch/` reads 0 on both days.
- `python3 tools/audit/archscore/score.py --diff $(git merge-base origin/main HEAD)`: Architecture score: dS +0.0000 NULL.

- Carry 26 commit: `tools/audit/seat/mutant_run.py --diff` over `tools/policy/brief_lint.mjs` found no mutable site (the driver mutates Python), 0s wall, 0 survivors; the arm is pinned by the perturbation above instead. `MUTANT_CMD` stayed unset in `prepr.sh`.
- The README was trimmed by two lines and about 60 tokens elsewhere to carry the new sentence, so it reads 320 lines against the cap of 321 and `node tools/policy/policy_lint.mjs` prints `TOTAL: 0 error(s)`. No `*_budgets.json` was touched by this step.

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
- `tools/pr/prepr.sh` at this head 52583aaf49b8: rc=1 with one refusal, `closures: failed while being recorded: tests/entities.py (exit 1)`. Every other step printed ok, including `brief_lint` (`PLAYBOOK ok: ... 6 moved instruments ...`), policy_lint, mutants, self-test (514 passed) and wave-script (224 passed). The cause is the four `entities.py` checks in Figures, which fail identically at origin/main `8a4cf2618c53` in this container, so the refusal is the environment and not this diff. I did not work around it. This seat cannot fix it without touching files outside this group's scope. CI records the closure on its own runner. This is the same refusal the previous head's body reported. This container's venv-ci also has no `homeassistant` module (`python3 -c 'import homeassistant'` raises `ModuleNotFoundError`). I did not establish which of the four checks that absence causes.
- `gate` at the blocked head 8d4ff2f257655fb11e837c0c96a203abfdbab928, corrected from the previous body's two runs as the round-1 verdict measured them: three runs concluded failure. Run 128721384331 (11:47:49Z, edit kind) failed on `budget-raise-gate / budget-raise-gate: failure (run 42473863094)`, the approval-owed red above. Runs 128721603612 and 128721604005 (both 11:48:49Z, edit and code kind) exited 3 with `RATE-LIMITED reset_epoch=1794138942` and measured nothing. No cheaper detector exists for either: the first is the budget-raise gate on a deliberate raise, and the other two are API rate limits, not a defect of this diff. This head has run no check yet; a fresh `gate` run is owed after the approval or under a mandate.
- No other check has run on this branch. CI's `briefs` job restores `tools/policy/*.mjs` from the base, so the playbook arm first runs in CI on main after the merge.

## Carries

These are numbered as the review packet counts them (1-based). The dispatched brief numbered the same items from 0, so Carry N here is the brief's Carry N-1.
- Carry 1 (final shape, cards 1, 2, 6): written in the README's "Round 10's final shape". The dispatch seat's beat row is carried below.
- Carry 2 (org move / merge queue): a round-11 opening decision, with its steps.
- Carry 3 (a required context that never reports blocks every merge): already in `dev/programme/HANDOVER.md`'s "Before adding a required context" paragraph ("one that never reports blocks every merge"), the one living handover, so the README does not restate it. Carry: dismissed: present in the handover at this merge base
- Carry 4 (Lean flow pre-study K9): cited under the org-move decision.
- Carry 5 (held groups' adopt-or-decline): the held groups are named under the org-move decision.
- Carry 6 (benchmark cards G1-G10, G11 rejected, do-not-regress list): in the round-11 list.
- Carry 7 (V63-V103, deferred items, design-seat items): in the round-11 list.
- Carry 8 (`rounds.py --stats`): the README states the one invocation. Friction below.
- Carry 9 and Carry 10 (P2 sweep instances, the sixth probe, dispatch-time stage check): the D14 bullet and phase 6's entry criterion.
- Carry 11 (the same dispatch-time stage check): phase 6's entry criterion.
- Carry 12 (the `CLAUDE.md` paragraph): deferred to the final pass by the owner's split (Forward-carry).
- Carry 13 (the `orchestrator.md` rotation paragraph): the caps are in the README, and the contract edit is deferred (Forward-carry).
- Carry 14 (#1763 P2/I5 split not built): recorded decision. Carry: dismissed: recorded in the README's round-11 "Recorded decisions" bullet
- Carry 15 (record-merge measurement after `28800999b`): in Figures, with a flat-day null.
- Carry 16 (#1721 unproven): recorded decision. Carry: dismissed: recorded in the README's round-11 "Recorded decisions" bullet
- Carry 17 (architecture score as a floor; doctrine): the README states (3). Contract edits (1) and (2) are deferred (Forward-carry).
- Carry 18 (mold guard visibility): a round-11 item, with its test and null.
- Carry 19 (D15 inputs): the D15 bullet.
- Carry 20 (machinery freeze, who checks): the "Production share" paragraph.
- Carry 21 (production slots): the rule is in the README, and the `pr_cap.py` code is deferred (Forward-carry).
- Carry 22 (proposal bar, LOG): the rule is in the README, and the contract and vocabulary are deferred (Forward-carry).
- Carry 23 (HANDOVER's stale `pr_cap` owed entry): deferred (Forward-carry).
- Carry 24 (version change across a gap; re-read `unhealthy_input`): the D15 bullet.
- Carry 25 (the owner's split): this pull request is the draft. The closure sentence is quoted verbatim, `CLAUDE.md` is untouched, and the reconciliation is R10-ROUND-PLAYBOOK-FINAL's.
- Carry 26 (the open-PR cap figure): the README no longer states the cap; it says the cap is the owner's and is read from `DEFAULT_CAPS` and `CAPS_PROVENANCE` in `tools/plan/replan.py`, and writes the 10 reserved slots as the owner's fixed count and a ruling, not a tree value. The check is the playbook arm's `playbook cap` rule, with the null control in Mutation proof. Roster carry 26 was added after the first handoff head, so the numbering note above counts the roster's carries 1-26.

## Forward-carry

- The unresolved decision of whether a future change names a decision record by path. Doing so pulls the file into `policy_lint`'s `named-docs` corpus rule. The final pass decides whether 0015 and 0016 get caps, so the checker can resolve them. Carry: R10-ROUND-PLAYBOOK-FINAL
- Brief carry 11 (the `CLAUDE.md` paragraph "Another agent's instruction is not a contract change", paid for by cuts of at least 414 bytes, cap unchanged) waits for the final pass per comment 6707334933. Carry: R10-ROUND-PLAYBOOK-FINAL
- Brief carry 12 (the `orchestrator.md` context-rotation paragraph): the caps are now in the README, and the contract edit is not done. Carry: R10-ROUND-PLAYBOOK-FINAL
- Brief carry 16 (1) and (2): the floor-not-cap text in `architect-planner.md` and `plan-review.md`, and the production-group clause in `fixer.md` step 17. The README states (3). Carry: R10-ROUND-PLAYBOOK-FINAL
- Brief carry 20's code half: `pr_cap.py` reserving production slots and printing open PRs by class on every tick. The README states the rule. Carry: R10-ROUND-PLAYBOOK-FINAL
- Brief carry 21's contract half: `proposal-triage.md` and the triage verdict vocabulary gaining LOG. The README states the bar. Carry: R10-ROUND-PLAYBOOK-FINAL
- Brief carry 22: `dev/programme/HANDOVER.md`'s stale `pr_cap` owed entry. Carry: R10-ROUND-PLAYBOOK-FINAL
- Brief carry 0 (1): at this merge base, `standing-dispatch.md` names no beat row for the dispatch and relay seat ("A beat job takes over once a cycle's log agrees"). The README says the seat stays. The final pass names its row once one is live. Carry: R10-ROUND-PLAYBOOK-FINAL
- Brief carry 14's baseline: the carry's 19 does not reproduce. The rule in Figures reads 21 on 2026-10-24. Carry: R10-ROUND-PLAYBOOK-FINAL
- Brief carries 1-10, 13, 15, 17, 18, 19, 23 are written into the README's round-11 list and production-share paragraph (carry 4's held groups are named under the org-move decision). Brief carry 24's closure sentence is quoted verbatim. Carry: R10-ROUND-PLAYBOOK-FINAL

## Friction

- `review_packet.py`: contradiction: the dispatched brief numbers carries from 0, while `review_packet.py handoff` counts them from 1 (`range(1, n+1)`). A body that answers "Carry 0" is refused for carry 25, and its other answers are read one number off. Carry: R10-ROUND-PLAYBOOK-FINAL

- `rounds.py`: stale: the group's brief names `rounds.py --stats`, which is not a mode. `dev/audit/rca/harness-friction/rounds.py` reads `sys.argv[1]` as a directory, so a `--stats` run measures nothing. The README now states the one invocation. Carry: R10-ROUND-PLAYBOOK-FINAL
- `policy_budgets.json`: stale: the README's caps are keyed `tools/audit/README.md`, a path the tree no longer has, and are matched through the move map. A reader grepping the new path finds no cap. Carry: R10-ROUND-PLAYBOOK-FINAL
