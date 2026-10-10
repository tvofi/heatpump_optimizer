Fix review: merge 9b70f367c6381a053eb74366d209ce73e95be2dd

bus-nonce: 1520e7e2cfd29f2ee42193d865a98ba2

Reviewed adversarially from a detached worktree at the PR head
`9b70f367c6381a053eb74366d209ce73e95be2dd` (remote head re-checked before
posting; unchanged). Every measurement below is mine, at that head.

## RESULT lines

- RESULT write-set: HELD. `beat` adds no write outside the guarded surface.
  The state tree is guarded twice (`check_write_set` in `write_tree`, and the
  `diff-tree` re-check in `main()` before any commit exists to push); the
  generators write only to fixed names in a temp staging dir (no roster-derived
  path — inspected `plan_table.py`/`resume_doc.py`/`handover_prompt.py`); the
  tip file's content is an `ls-remote` first token (a hex sha, cannot traverse);
  the mirror writes basenames of the three fixed paths. I drove the beat
  against a sandbox origin/clone I own: state tree after a pass was exactly
  `docs/keep.md` + the three state docs; the driver worktree stayed clean and
  its index untouched; nothing reached `/private/tmp/r9-main` or any live
  checkout. The one push target a caller could mis-aim (`--state-ref`) is a
  caller flag the plain form already had, not a widening by `beat`.
- RESULT mutants: ALL FOUR REPRODUCED at the head, exactly as the body claims.
  A (memo check deleted) rc=1, 5 arms red — the body's verbatim list; through
  the gate: `FAIL tools/audit/seat/state_docs.py --self-test passes, beat arms
  included`, `1 of 2251 ENTITY CHECKS FAILED`. B (tip recorded on refusal)
  rc=1, 2 arms red. C (roster re-fetch removed) rc=1, 5 arms red. D (`if
  True:` one pass and out) rc=1, 2 arms red. File restored after each mutant;
  worktree clean.
- RESULT unmutated head: `state_docs self-test: all checks passed`; gate run
  twice `ALL 2251 ENTITY CHECKS PASSED` (bare, and under closure-record
  tracing).
- RESULT termination/bounds: `--once` returns the pass's rc; the loop survived
  an unchanged tip, landed two successive main moves, pushed a new state commit
  inside the loop on a roster-edit move (carried path `docs/keep.md` kept),
  and exited on signal. A persistent refusal retries at `--interval`, not in a
  tight loop.
- RESULT idempotence: runs 2 and 3 with an unchanged tip printed `unchanged;
  nothing written`, rc 0, state ref byte-identical, mirror untouched, tip file
  unchanged. A trigger-only main move (roster unchanged) took the
  `already current ... nothing to commit or push` path — recorded, no dirty
  write — so the beat cannot re-push forever on identical inputs.
- RESULT classification MEASURED, not asserted: my own Darwin recording of
  `tests/entities.py` names exactly the six `tools/audit/seat/` paths of the
  committed closure (the four new + `record_row.py`, `roster_lib.py`);
  `closure.py check --partial` rc 0 with the body's summary line; sole
  over-scoped entry is `tests/golden/card_claimed_drift.txt`, main's, as the
  body says. `select --diff <merge-base>` gives `MODE: FULL` (GATE_FILES
  touched); a `state_docs.py`-only diff now selects 1 script (INERT_EXCEPT
  effective). `no-copies` passes under the pinned interpreter; the body's red
  was the workstation's 3.11 on a pre-existing f-string, reproduced as such.

## Other contract steps

- Null control re-taken: base `c729bb32` has 0 `beat` lines / 17 `ok("` arms;
  head 47 / 40 — the body's figures exact.
- VERSION, manifest version, `RELEASE_NOTES.md` heading untouched (0 files).
- Claim files: the diff touches no golden or claim file;
  `env_drift.py --claims-only c729bb32` ok.
- Structure: `STRUCTURE RATCHET PASSED`; `policy_lint --budgets` rc 0, corpus
  ~59899 unmoved; `tmp_paths.py --check` 0 refused, 0 stale; archscore
  `dS +0.0000 NULL`. INSTRUMENTS.md entry present in the diff.
- Forward-carry: `none` is right — `orchestrator.md` names no state-doc
  command (0 matches), and the beat's instructions live in the instrument and
  in `INSTRUMENTS.md`, both in this diff.
- Red checks: check-runs at the head — 0 failure (16 success, 2 in progress,
  12 skipped); the authored head's cancelled runs are superseded by the head's
  re-runs. The body's two local refusals are answered and I reproduced the
  cheaper detector passing (`no-copies` under `seat-python3`).
- Class: this body's class is one seam — the beat's landing inside the
  instrument that owns the write set — and the body says so and names its one
  deliberate limit (one watched ref).
- Architecture (fixer.md step 17): sound — the loop lives inside the one
  instrument that owns the write set and the push; no parallel mechanism
  added.

## Verdict

Every number in the body I re-derived came back identical. The instrument
that writes the record did not widen its write set, terminates, and is
idempotent; the gate pin is real and the mutation proof reproduces. Merge.

Round: 1 (first review of this PR).
