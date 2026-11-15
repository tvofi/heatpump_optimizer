# BLOCKED: r11-pre-rulings-file

Question: The brief says RULINGS.md's text is "taken from the orchestrator's memory files, each quoted with its date". This cloud container has no orchestrator memory directory (`~/.claude/projects/-home-user-heatpump-optimizer/` holds only this session's transcript; `$HPO_STATE_DIR` is unset; no remote ref carries a MEMORY.md). Please supply the rulings, verbatim with their dates (e.g. as a file pushed to refs/heads/handoff-wip/r11-pre-rulings-file-body or a re-dispatch payload), or rule that the seed may be drawn only from dated tvofi rulings already quoted in the tree. Without one or the other the file would be invented, so it stays empty.

Second, smaller question (answer or confirm): the ruling names "the root policy file, its own role contract and the rulings file in full, and of the instrument pages only those changed since the last proof". It does not name `.claude/rules/`, which the hook read in full until now. This branch reads them **by change** with the instrument pages (neither dropped nor in full). Confirm, or say "rules in full" / "rules dropped".

## Done at the WIP head (mechanism only, not handed off)

- `tools/audit/seat/hooks/liveness.py`: corpus = CORE (`CLAUDE.md`, `dev/governance/roles/orchestrator.md`, `dev/programme/RULINGS.md`) in full + of `.claude/rules/`, `tools/audit/seat/INSTRUMENTS.md`, `tools/audit/seat/instruments/` only blobs differing from the last accepted proof's manifest (`policy-proven.json`, written by `--prove`); no manifest -> every page; a missing core file writes no corpus and prints `POLICY-CORPUS unwritten`.
- `tools/audit/seat/hooks_setup.py --self-test`: 3 new cases + 4 new mutants (by-change disabled, manifest never recorded, changed pages dropped, missing core tolerated), all killed; `hooks_setup self-test: 68 checks, 0 failed`.
- `orchestrator.md` section 0 (rulings file + post-compaction read), section 9 (carry 0: objective record under `dev/audit/yardstick/` as closure criterion), `CLAUDE.md` index entry, `sweep_template.md` step (0), `instruments/hooks_setup.py.md`.
- Not yet run: closure classification of the new file, `structure.py`, policy budgets, `prepr.sh`.
