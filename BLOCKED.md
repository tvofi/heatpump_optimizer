# BLOCKED: the merged and pinned line is ready, and `handoff/` was frozen by the repair seat while it was built

Question: may bd262a2ada9a10f9afb0e9b395ac4c0fce0f23af be carried onto the frozen handoff head 23961a5d8592e3fde3ac82ff4f705983da01fe04 (`git merge-base --is-ancestor 23961a5d8 bd262a2ad` exits 0, so it fast-forwards), by the orchestrator or `--carry`, or is this seat to push it to `handoff/` and re-take the body whole at it?

Not pushed by this seat: `handoff/r10-duty-switch-restart-learning` and `handoff-body/r10-duty-switch-restart-learning`. The repair seat handed off at 23961a5d8 (body bb74a96ac, `Code: 23961a5d8`, 2026-11-12T00:57Z) after this seat's ruling (merge main, pin, hand off) was given, and `fixer.md` step 6 lets only the orchestrator, the merge-main bot or `--carry` move a head past its handoff. A push of `handoff/` by this seat would also leave bb74a96ac naming a head that is no longer the tip until a second body landed.

## What bd262a2ad is

- 23961a5d8 (the repair step, itself on the pull request's head 84405a2a2), merged with `origin/main` a7887485deb7b41995b20a48fab2ae411d887954, which carries pull request 3466 (`git merge-base --is-ancestor 7a8e1c659add a7887485d` exits 0), plus `killed_by` records only: `git diff --stat 23961a5d8 bd262a2ad -- . ':!tests/mutation_ledger'` lists what the merge of main brought and no file of this group's.
- Its tree equals the parallel seat's 76bd67818 (`git rev-parse bd262a2ad^{tree} 76bd67818^{tree}` prints one id twice); the two seats pinned from both ends and merged each other's lines through this ref.
- `origin/main` has since moved to 47788534daffab7a199a132c5f2ca118951018dc; `git merge-tree --write-tree 47788534d bd262a2ad` exits 0, so nothing forces a second merge.

## Measured at this line

- Pins: every pass was `PYTHONPATH=tests/hastub python3 tests/mutation_table.py --pin-killed --base origin/main --scripts tests/features.py --shard K/N --jobs 4 --budget-minutes M`, each on the committed head it extended. This seat's seven passes each end `PIN KILLED: <n> pinned, 0 left unpinned` with `baseline tests/features.py: rc=0 failed=0` and a surviving null control (`NULL_COMMENT survived tests/features.py`); no pass named a survivor. The driver is restricted to `tests/features.py`, which holds the section: an unrestricted shard of 28 sites did not finish inside a two-hour run and wrote no pin.
- A shard is cut from the sites still unpinned when it starts, so shards 1 to 8 of 8, run one after another, did not cover the diff; two further passes over the remainder did.
- The repair step's edits left pins naming no site (`STALE PIN` lines of `ci_predict.py`); those files were deleted and the edited lines pinned afresh.
- At bd262a2ad, `PYTHONPATH=tests/hastub python3 tools/pr/ci_predict.py --base origin/main --only mutation` prints no `ADDED UNPINNED` and no `STALE PIN` line and ends `CI PREDICT: no closures, fast, governance or instrument red predicted against a7887485deb7`. Control: the same command at 6dac686e2 (main merged, no pin) printed 105 `ADDED UNPINNED` lines.
- `PYTHONPATH=tests/hastub python3 tests/features.py` at 6dac686e2 (the merge of main into bf9707ae0, before the repair step): exit 0, `ALL 5283 FEATURE CHECKS PASSED`; the `combi_type_branch` census that was red at bf9707ae0 is green with 3466. With the repair step merged the script was run only as the pin passes' baseline (rc=0 failed=0).
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`. `PYTHONPATH=tests/hastub python3 dev/audit/harnesses/r10_duty_switch_section.py`: `ALL 51 DUTY-SWITCH SECTION CHECKS PASSED`.

## Not done at this line

`tools/pr/prepr.sh`, the scoped gate, golden drift, the architecture score, the body's mutant spec runs and the reviewer's probe were not run at bd262a2ad, and no body was written for it: bb74a96ac's figures are all taken at 23961a5d8 against merge base cbd23f1c8, and steps 2 to 8 are owed again at a head that merges main. `## Red checks` at that re-take: `tests / fast (3.14)` is answered by the merge (pull request 3466 on main), and `tests / mutation` by these pins.
