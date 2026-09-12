# Round 4 baseline

- baseline: 7dd68dd327fe3dbfb09f3bd0fe38910c58877697
- export (read-only finders): /Users/timmalmstrom/heatpump_optimizer/.claude/worktrees/audit-r4-baseline
- worktrees (isolated finders): D0 /Users/timmalmstrom/heatpump_optimizer/.claude/worktrees/audit-r4-D0, D3 /Users/timmalmstrom/heatpump_optimizer/.claude/worktrees/audit-r4-D3, D9 /Users/timmalmstrom/heatpump_optimizer/.claude/worktrees/audit-r4-D9, D11 /Users/timmalmstrom/heatpump_optimizer/.claude/worktrees/audit-r4-D11
- python: /Library/Frameworks/Python.framework/Versions/3.11/bin/python3 (run from the directory root with PYTHONPATH=tests/hastub)
- node: /Users/timmalmstrom/.nvm/versions/node/v20.10.0/bin/node
- chromium: /Users/timmalmstrom/.cache/pw-browsers/chromium-1148 (PLAYWRIGHT_BROWSERS_PATH=$HOME/.cache/pw-browsers)
- playwright module: install into a scratch prefix, e.g. `npm i --prefix /tmp/pw playwright@1.49.0`, then NODE_PATH=/tmp/pw/node_modules
- gate lock: take it only when tests/closure.py select reports MODE: FULL or names
  tests/stress.py -- that one script is what the lock exists for. Use
  tests/gate_lock.py, never mkdir and a shell pid (#404 replaced that: no lease, so
  tests/run.sh cannot renew it, and no flock, so a crashed holder holds it forever).

      python3 tests/gate_lock.py take --label <your-label>
      HPO_GATE_LOCK_LABEL=<your-label> GATE_SCOPE=auto GOLDEN_MODE=drift \
        GOLDEN_REF=<a ref that is not HEAD> ./tests/run.sh
      python3 tests/gate_lock.py renew --label <your-label>   # between commands
      python3 tests/gate_lock.py release --label <your-label>

- thread pin: OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1

## Round-4 preparation notes (read these before you start)

Two repairs were applied to every finder tree after `prepare_baseline.sh` ran,
because the script as shipped breaks the export. Both are recorded as round-4
findings against the instrument; you do not need to re-find them.

1. **`RELEASE_NOTES.md` was restored to the export.** `prepare_baseline.sh:29`
   deletes it, but `tests/entities.py:12140` reads it unguarded at import, so
   every `entities.py`-based harness died with `FileNotFoundError` and ran 0 of
   1360 checks. With the file restored, 1360 checks run.
2. **`tools/audit/round3/` was removed from every finder tree** (116 files,
   including `ledger/verdicts.tsv` naming 43 earlier findings with their
   verdicts). `COMMON.md`'s wall forbids earlier rounds steering you.

**Known-failing checks in the export, which are export artefacts and not tree
defects.** `PYTHONPATH=tests/hastub python3 tests/entities.py` reports
`3 of 1360 ENTITY CHECKS FAILED`: the two handover checks and the
`updated-for:` ancestry check, all three of which need `.git` (the export has
none). Do not report them.

**If your tree is an isolated worktree** (D0, D3, D9, D11) it is a real git
checkout, so `docs/audit-2026-09.md`, `docs/backlog.md` and
`docs/plan-*.md` ARE present. Do not open them; `COMMON.md`'s wall is the
contract, and for you it is an instruction rather than a missing file. D11's
brief is the one exception and it is scoped to mechanisms, never verdicts.

**Playwright is already installed** at `/private/tmp/hpo-pw/node_modules`
(1.49.0); Chromium is `chromium-1148` under `$HOME/.cache/pw-browsers`. Use
`NODE_PATH=/private/tmp/hpo-pw/node_modules
PLAYWRIGHT_BROWSERS_PATH=$HOME/.cache/pw-browsers` rather than installing again.

**The drift cache is warm** at `~/.cache/heatpump_optimizer/` (32 MB).

**Box conditions.** Two orphaned busy-loop shells from an aborted round-3
measurement were killed before this round started; they had been burning two of
eight cores for 25 hours. Quote the real `load1` beside every timing RESULT
anyway, per `tools/audit/README.md`.
