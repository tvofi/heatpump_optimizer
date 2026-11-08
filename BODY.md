R10-HANDOFF-PATH part 3 (r10-handoff-path-p3): the four open carries of the opener's and updater's handoff path: 6 (one checkout per PR), 8 (BUSY exit 75 and the relay's key), 12 (retry of refusals that clear without a ref moving), 19 with its duplicate 40 (deterministic `mut:unlock` arm). Part of #201.

## Head

Measured at 92c5c2afe33c82d4bc19ed801cd968c51d767adb, cut from origin/main e36e5327dde86105d66b21fd9ffd3e75eeeecdca (main unmoved since the cut at the time of writing; the owner's 2026-11-07 ruling makes no merge of a moved main owed here).

## Mutation proof

- `bash tools/audit/seat/pr_args.sh --self-test` runs each new arm on copies of the scripts less the named line: `mut:colremove` (the worktree removal in `pr_collect_wt`) and `mut:opcollect` (open_pr.sh's call) leave the opener checkout behind; `mut:elsewhere` lets update_pr.sh go past a branch held in another worktree; `mut:updreusewt` removes and recuts the per-PR checkout; `mut:unpushed` now reads the BUSY (75) exit. Each arm reads red on its mutant.
- `bash tools/audit/seat/cloud_relay.sh --self-test`, run on copies with one line deleted: `mut:retryall` (every class recorded by the retry rule) is red on arms (b); `mut:trylimit` (no three-run limit) is red on arm (c); `mut:backoff` (no backoff wait) is red on "a failed update is tried once" and "the backoff holds a retryable refusal back".

## Null control

- Carry 6: a dirty opener checkout is kept on its branch and reported (`open_pr: KEPT ... it is dirty`), not collected; the unmutated second update reuses the first's worktree (marker in its git dir survives) and cleans leftovers.
- Carry 8: with the branch checked out nowhere else the run reaches its push (not 75).
- Carry 12: arm (a) an `ancestry reds` refusal that then clears updates on the retry; with the default 1800 s backoff a retryable refusal is run once in two passes.
- Carry 19: the unmutated holder is signalled and awaited, and is read gone at the run's return (`update_pr: the lock holder has exited by the time a run returns`).

## Figures

- `bash tools/audit/seat/pr_args.sh --self-test`: `pr_args self-test: 189 checks, 0 failed` at 92c5c2afe33c.
- `bash tools/audit/seat/cloud_relay.sh --self-test`: `cloud_relay self-test: 380 checks, 0 failed` at 92c5c2afe33c.
- `python3 tests/structure.py`: STRUCTURE RATCHET PASSED. `PYTHONPATH=tests/hastub python3 tests/doc_claims.py`: ALL 296 checks PASSED (the one script `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)` scopes in).
- Carry 19's mechanism: the `mut:unlock` copy now polls every 30 s (`sed` on the `mut:watch` line of the copy), so the holder is alive at the read whatever the load, and is then ended with USR1 and awaited with a 10 s bound; the old arm read it inside the holder's 0.2 s poll. The old rate (1 in 9 concurrent, 22 of 22 chained, from the carry) is not re-measured: the arm no longer depends on that window.

## Red checks

`bash tools/pr/prepr.sh` at 92c5c2afe33c refuses one step, `closures` ("failed while being recorded: tests/entities.py (exit 1)"); every other step is ok or skipped, `diff mutants` reads no survivor and `merged structure` passes. The refusal is the sandbox's, not this diff's: `PYTHONPATH=tests/hastub python3 tests/entities.py` prints `3 of 2656 ENTITY CHECKS FAILED` (the Pages-workflow probe among them) on this head and the same line on a detached worktree of origin/main e36e5327dde8, which this diff does not touch. No cheaper detector is owed: the required CI runs the script in its own environment.

## Forward-carry

none: no new finding; the answer to each roster carry is in the next section.

## Carry answers

- Carry 0: dismissed (folded, resolved, duplicate or a status line, per the brief)
- Carry 1: dismissed (folded, resolved, duplicate or a status line, per the brief)
- Carry 2: dismissed (folded, resolved, duplicate or a status line, per the brief)
- Carry 3: done at 788e8ceed2d7251740e46fa7f1568ea284d85d47
- Carry 4: done at 788e8ceed2d7251740e46fa7f1568ea284d85d47
- Carry 5: done at 20cfab74c6aa9d9ff26e81328ebe1af407ed7cdc
- Carry 6: built at 92c5c2afe33c82d4bc19ed801cd968c51d767adb: `open_pr.sh` collects its checkout (`pr_collect_wt`, pr_args.sh) once the PR exists with its row, and `update_pr.sh` resets and reuses its one per-PR checkout; the sweep's disk-floor naming of collectable checkouts is not built (no such floor instrument was found in the tree)
- Carry 7: done at d855180e284c1b121ca77abae042e82098ea24b2
- Carry 8: built at 92c5c2afe33c82d4bc19ed801cd968c51d767adb: update_pr.sh exits 75 (`pr_busy`) for a branch checked out elsewhere and for a worktree holding unpushed commits, and the relay keys cloud-handoff-failed on topic, handoff sha and body sha and keeps the reason
- Carry 9: done at 2a9cd3476dae9f45d3091b546fdd2723bcb0ce4e
- Carry 10: done at d855180e284c1b121ca77abae042e82098ea24b2
- Carry 11: done at d855180e284c1b121ca77abae042e82098ea24b2
- Carry 12: built at 92c5c2afe33c82d4bc19ed801cd968c51d767adb: a refusal of unpinned sites, carry, figures or the body contract is recorded at once; any other reruns after HPO_RELAY_RETRY_BACKOFF (1800 s) up to three runs, then stays owed
- Carry 13: done at 788e8ceed2d7251740e46fa7f1568ea284d85d47
- Carry 14: done at 20cfab74c6aa9d9ff26e81328ebe1af407ed7cdc
- Carry 15: done at d855180e284c1b121ca77abae042e82098ea24b2
- Carry 16: done at d855180e284c1b121ca77abae042e82098ea24b2
- Carry 17: done at d855180e284c1b121ca77abae042e82098ea24b2
- Carry 18: dismissed (folded, resolved, duplicate or a status line, per the brief)
- Carry 19: built at 92c5c2afe33c82d4bc19ed801cd968c51d767adb: the `mut:unlock` arm is deterministic (see Figures)
- Carry 20: dismissed (folded, resolved, duplicate or a status line, per the brief)
- Carry 21: dismissed (folded, resolved, duplicate or a status line, per the brief)
- Carry 22: dismissed (folded, resolved, duplicate or a status line, per the brief)
- Carry 23: dismissed (folded, resolved, duplicate or a status line, per the brief)
- Carry 24: dismissed (folded, resolved, duplicate or a status line, per the brief)
- Carry 25: dismissed (folded, resolved, duplicate or a status line, per the brief)
- Carry 26: dismissed (folded, resolved, duplicate or a status line, per the brief)
- Carry 27: dismissed (folded, resolved, duplicate or a status line, per the brief)
- Carry 28: dismissed (folded, resolved, duplicate or a status line, per the brief)
- Carry 29: dismissed (folded, resolved, duplicate or a status line, per the brief)
- Carry 30: dismissed (folded, resolved, duplicate or a status line, per the brief)
- Carry 31: dismissed (folded, resolved, duplicate or a status line, per the brief)
- Carry 32: dismissed (folded, resolved, duplicate or a status line, per the brief)
- Carry 33: dismissed (folded, resolved, duplicate or a status line, per the brief)
- Carry 34: dismissed (folded, resolved, duplicate or a status line, per the brief)
- Carry 35: dismissed (folded, resolved, duplicate or a status line, per the brief)
- Carry 36: dismissed (folded, resolved, duplicate or a status line, per the brief)
- Carry 37: dismissed (folded, resolved, duplicate or a status line, per the brief)
- Carry 38: dismissed (folded, resolved, duplicate or a status line, per the brief)
- Carry 39: dismissed (folded, resolved, duplicate or a status line, per the brief)
- Carry 40: built at 92c5c2afe33c82d4bc19ed801cd968c51d767adb: the duplicate of carry 19, answered by the same change
- Carry 41: not in the brief snapshot this seat was given (carries 0 to 40); not built here, stays open on the roster

## Unpinned sites

n/a: no Python line is added; the shell lines carry in-tree `# mut:` markers pinned by the self-test arms above.

## Friction

none
