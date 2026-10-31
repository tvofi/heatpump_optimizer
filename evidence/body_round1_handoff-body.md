train.sh and the merge sweep default to the owner's recommended flag set (P269, V183, tvofi 2026-10-28), each switchable off. The set had three disagreeing homes (standing-merge.md line 9, `AUTO_TRAIN_FLAGS`, train.sh's all-off defaults); it now has one: `RECOMMENDED` in `tools/audit/seat/merge_train.py`.

**POLICY:** `dev/governance/roles/standing-merge.md` changes (names the set by reference); merges only on tvofi's approving review.

- `merge_train.py`: `RECOMMENDED` = overlap, approval-carry, skip-bad, free-holders, bot-prs, pre-flight; replaces `AUTO_TRAIN_FLAGS`. `auto_train_argv` (sweep and `add --auto`) is a bare launch (`--repo --state-dir [--mandate]`), so it gets train.sh's defaults.
- `train.sh`: reads the set from the `RECOMMENDED` line; `--no-<flag>` per flag; old `--<flag>` spellings are no-ops; the launch line prints `set:` and `mandate:`. Mandate: `--mandate ID`, else the one-line `$STATE_DIR/mandate` (digits only, else refuse), else `none (owner reviews only)`; `--no-mandate` turns it off. The gate still reads the id at every merge; no id in code or tree.
- Not changed, noted: `sweep_render.py`/`sweep_template.md` still render an explicit flag list for the sweep seat's prompt; `add --auto` from bus.sh does not read the mandate file itself (the started train.sh does).

**Roster carry (open, not answered by this change).** Carry 1: **not done in this pull request.** The group's roster entry (round roster branch) folded R10-FLOW-POSTMERGE (after-merge bookkeeping in `merge_pr.sh` and `merge_train.py`) in, owed in the same pull request. The fold landed after this seat was dispatched: the dispatch brief was P269 alone at base cf4f6b7a6, so the folded brief and its sub-carries are neither implemented nor measured here. The P269 change is complete and independent of it (argument defaults only, not the post-merge path). The orchestrator either re-dispatches the folded brief onto this branch or splits R10-FLOW-POSTMERGE back out; the reviewer should treat it as open.

## Head

0b79e8de98fbd2b2f2410e8ff56a92766eea74f1 on base cf4f6b7a660f5b61e0f2b933bd18647fe3ba90c7.

## Mutation proof

Mutant: drop `"--pre-flight"` from `RECOMMENDED` (sed on the tuple's tail). Reds: `bash tools/audit/seat/train.sh --self-test` -> `REFUSE: self-test: an explicit --skip-bad/--overlap launch is not the recommended set` (arm 6; the bare-launch arm 8 reads the same list); `merge_train.py --self-test` -> `FAIL RECOMMENDED is the owner's six, each a flag batch accepts`. Restored; both green. Also `r10_flow_autotrain_mutants.sh` S5 is re-pointed at `RECOMMENDED`.

## Null control

An explicit old-style `--skip-bad --overlap` launch has the same child argv as a bare one (train.sh self-test arm 6 asserts the six in RECOMMENDED order; arm 8 the bare launch). `--no-skip-bad` removes exactly `--skip-bad` (arm 8a). A state dir with `mandate` passes `--mandate 4242`, `--no-mandate` none, explicit `--mandate 7` wins, a non-numeric file refuses (arm 8c). The sweep's started argv equals a bare hand launch's (merge_train self-test, "sweep's CLI").

## Figures

- `bash tools/audit/seat/train.sh --self-test` -> prints `effective set of a bare launch: --overlap|--approval-carry|--skip-bad|--free-holders|--bot-prs|--pre-flight` and `ok`.
- `python3 tools/audit/seat/merge_train.py --self-test` -> 381 checks, 0 failed.
- `python3 tests/structure.py` -> STRUCTURE RATCHET PASSED.
- `node tools/policy/policy_lint.mjs` -> TOTAL: 0 error(s) (standing-merge.md held to its token cap).
- `PYTHONPATH=tests/hastub python3 tests/entities.py` -> see Red checks.

## Red checks

`policy-docs` (policy_lint token cap on standing-merge.md, found by entities.py's template-arm check at an earlier tree) was repaired before the handoff by a shorter wording; a cheaper detector already exists (policy_lint.mjs --budgets, ran locally). Seat-venv baseline: `hb:positive_control` timing retries are flaky and unrelated.

## Forward-carry

none

## Friction

none

## Approval

Pending: `dev/governance/roles/standing-merge.md` is policy. The change is the owner's own ruling on P269 (tvofi, 2026-10-28T20:20:27Z, V183); it merges only on tvofi's approving review at this head.
