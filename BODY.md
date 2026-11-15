Records the owner's standing rulings in `dev/programme/RULINGS.md` and has the liveness hook re-read that file after a compaction when it changed. Roster group R11-PRE-RULINGS-FILE.

## Re-cut

Round 4. Owner rulings 2026-11-15 (tvofi): "The rulings file is not policy."; "Orchestrator.md at least should clearly refer to the rulings file. Rulings are binding, even if it is not policy." This body replaces the earlier ones; round history is dropped. What changed in this round: no file calls `RULINGS.md` policy; `orchestrator.md`, `fixer.md` and `proposal-triage.md` each carry one sentence that the owner's rulings in `dev/programme/RULINGS.md` bind though the file is not policy, and `CLAUDE.md`'s index line says the same; `RULINGS.md` stays in `dev/governance/config/corpus_excluded.json` and is in no policy list.

## Approval

Policy change (`CLAUDE.md`, `orchestrator.md`, `fixer.md`, `proposal-triage.md`), for tvofi's approving review at the head; it records the owner's 2026-11-15 rulings quoted in Re-cut. Approvable under mandate 6893738184 where the orchestrator holds it.

## Head

`73fefc820a47594f2e95866f053c405d194b4a33`, on `origin/main` `31117b1029de63938d949e78dcbcd8f9451e5e33` (2026-11-15 UTC); `git merge-tree --write-tree origin/main HEAD` reports no conflict, so main was not merged in.

## Hunks kept and dropped

Every hunk of the earlier diff in a contract, each judged by whether the rulings are relevant to that role (the owner's test):
- `orchestrator.md`, kept: one sentence before the compaction re-read stating the rulings bind the orchestrator and whoever it briefs and where they are; the compaction re-read of the file when changed; section 5's pointer to the soft cap's value in the file; the card-ruling edits (scoped prepr, `--allow-red`, local-seat rule, objective record), each a ruling the orchestrator carries out.
- `orchestrator.md`, dropped: sections 3 and 10 sentences that `root-cause.md`, `defect-root-cause.md` and `finding-propagation.md` already state, to keep the corpus cap's margin (nothing else removed).
- `fixer.md`, kept: the new sentence that the rulings bind a fixer (shortened to "bind you" to fit the per-file cap `tools/audit/briefs/fixer.md` by 4 tokens), since a fixer works under the orchestrator's briefs and the rulings; the 2026-11-15 prepr-scoping ruling in step 5.
- `proposal-triage.md`, kept: the new sentence (the round-end triage applies rulings on machinery, freeze and proposals recorded there); the card P2 machinery paragraph.
- `CLAUDE.md`, kept: the index line, now "they bind every seat, though the file is not policy"; the section "What the repository may carry" (a separate ruling of 2026-11-15 that binds every push).
- Dropped as a duplicate, by earlier rounds: any hunk making the file one of the policy files listed in `CLAUDE.md`'s policy table.

## Instrument changes

All kept; none reads the file's policy status. `tools/audit/seat/hooks/liveness.py` and `hooks_setup.py` (+ `instruments/hooks_setup.py.md`): the post-compaction corpus is `CLAUDE.md`, `orchestrator.md` and every `.claude/rules/` file in full, and of the instrument pages and `RULINGS.md` only what changed since the last accepted proof. They key on a file list, not on the file's classification. `sweep_template.md`: step 0 names the same read. `dev/audit/config/scopes.json` and `tests/layout.json`: classify the new tracked file (`check_scopes.py`, `layout.py` read these; the file is a record, so it is outside the policy lists).

## Mutation proof

`python3 tools/audit/seat/hooks_setup.py --self-test`: every `MUTANTS` entry this branch adds goes red against the live tree, among them `the corpus carries every page, changed or not`, `the rules are read by change`, `the rulings file is read in full`, `a changed rulings file is dropped` and `a missing core file still writes a corpus`. The diff of this round is prose only and moves no mutated line.

## Null control

In the self-test, a PostCompact with nothing changed since the proof writes the core and the rules only (`read-proof: nothing changed since the proof reads the core and the rules only (null control)`); the next case changes `RULINGS.md` and asserts it is in.

## Figures

- policy budgets: `node tools/policy/policy_lint.mjs --budgets` on the merge of this head onto `origin/main` `31117b1029` (a scratch merge commit, the merge-tree result): `corpus: ~69748 tokens, cap 69333 +band 500 = 69833`, `role fixer ~6252 tokens, cap 5852 +band 500 = 6352`, `role policy ~9985 tokens, cap 9958 +band 500 = 10458`; no cap changed. Paid by cutting duplicated prose in `orchestrator.md` (above), never by a raise.
- policy lint: `node tools/policy/policy_lint.mjs` on this head printed `TOTAL: 0 error(s) across 52 policy file(s)`; the previous head (before the fixer sentence was shortened) printed `TOTAL: 1 error(s)`, a `[budgets]` refusal of `tools/audit/briefs/fixer.md` (files_tokens).
- hook self-test: `python3 tools/audit/seat/hooks_setup.py --self-test` printed `hooks_setup self-test: 74 checks, 0 failed`.
- scopes: `python3 -I tools/audit/check_scopes.py --self-test --repo .` printed `SELF-TEST passed (every perturbed scope refused)`.
- structure: `python3 tests/structure.py` printed `STRUCTURE RATCHET PASSED`.
- generated rules: `node tools/policy/rules_sync.mjs --check` printed `RULES-SYNC ok`.
- prepr was run scoped, `PREPR_SKIP_CLOSURES=1 PREPR_SKIP_CODE=1`, for this text-only delta.

## Red checks

Reds carried by earlier commits of this branch, each answered; `governance / policy-docs`, `governance / env-matrix` and `tests / fast (3.14)` are in `merge_train.py owed-reds`' set. None is red on this head by the measurements in Figures (policy lint `TOTAL: 0`; the fast job's template arm keys on that exit code).

- `governance / policy-docs`, `governance / env-matrix` and `tests / fast (3.14)`, at `91f6dc48e2`: the rulings commit replaced decisions 0010's and 0011's paths with bare numbers, which `policy_lint.mjs`'s `[citation-presence]` check refuses; repaired by citing both by path. State (b), the process existed and was not followed at that head: the figure `TOTAL: 0 error(s)` was taken before the cuts that removed the citations. Cheaper detector: `node tools/policy/policy_lint.mjs`, which `prepr.sh` already drives locally. No countermeasure: the detector is already in the local path.
- The same three checks at `03c8a59184`: the merged tree exceeded the corpus cap (`policy_lint.mjs --budgets`), because the branch was measured alone and main had grown. State (c), the process was followed and measured the wrong tree. Cheaper detector: `node tools/policy/policy_lint.mjs --budgets` on `git merge-tree --write-tree origin/main HEAD`, run here and in Figures; its standing cost is one policy-lint run (about a minute). Carry: R11-INTAKE-R10-RESIDUE
- `governance / instrument-self-tests` (not in the owed set): its `check_scopes.py --self-test` refusal of `dev/programme/RULINGS.md` was repaired in `scopes.json` and `SELF-TEST passed (every perturbed scope refused)` printed on this head; its step "Refuse a self-test read set the committed table misses" is inherited from main, owned by R11-HOTFIX-MAIN-SELFTEST-RED.

## Forward-carry

- tvofi's ruling of 2026-11-15 (card "Hold delivery rows for the stamp too", in `dev/programme/RULINGS.md` under "Merges, CI and reds") has the automatic delivery-rows pull request wait and merge only with the stamp batch. The record-autofix automerge path (`tools/audit/seat/record_row.py --automerge-check`) and the board's `RECORD-OWED` line (`beat_jobs.py`, `ledger.py`, `orchestrator_tick.py`, `owed_unactioned.py`) contradict it. Control: a `record/autofix` pull request green and unmerged between stamps raises no line and is not merged; under the train's `--stamp` queue it is admitted with the stamp batch. An instrument change, held by the round-11 freeze for the round-end triage. Carry: R11-INTAKE-R10-RESIDUE

## Friction

none
