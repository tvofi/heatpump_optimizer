R10-ROSTER-WRITE-SWEEP, repair after fix-review round 1 (blocked at `21be201c`): the roster write path's residue in `tools/audit/seat/roster_edit.py` and `tools/audit/seat/roster_queue.py`, built carry by carry, each with a self-test arm and a plant. Part of #201.

What the repair changes, by review finding:

1. selftest-red. `roster_queue.py --self-test` crashed under `python3 -I` because `_run_batch` imported `roster_edit` from the edit checkout (absent from the self-test's throwaway clone) and ignored the `editor` it was passed. One resolution now serves both paths: `resolve_editor` is `--editor`, else the `roster_edit.py` beside the script; `load_editor` loads that same file for `run --batch` (refusing, unexecuted, a file that has no `batch_edit`), and the single-op path runs that same file as a subprocess. The edit checkout supplies the roster and the shims only.
2. Red checks: named below, with the cheaper detector.
3. Forward-carry: the deferred items are built where buildable (the marker guard, carry 15, is now built: the carry says "Owner-ordered: no", so nothing waited on an owner), dismissed with a reason, or routed with a `Carry:` and its control stated as a precondition.
4. Carry 8's read-only roster instrument is built: `roster_queue.py show [GROUP] [--ref R] [--stage S]` and `diff REF_A REF_B`, `git show` reads only, `diff` exits 1 when the refs differ, with arms and plants Q10-Q12.

Dispositions by the review packet's 1-based numbering of the 17 roster carries (the review's own labels above and below, "carry 4", "carry 8", "carry 9", "carry 13(2)", "carry 15", "carry 16", are the verdict's and the brief's order, not these): lettered proposal labels, built (Carry 1); the M4-M6 plants, answered by W1-W15 and Q1-Q13 (Carry 2); the stale note, built (Carry 3); closing-destination refusal, built (Carry 4); `pr` in set-resume, built, its data edits are under Forward-carry (Carry 5); the overlap refusal and phase branches, built (Carry 6); `append-group @file`, built (Carry 7); the host-path gate, built (Carry 8); ordering after the schema group, holds, R10-ORCH-ROSTER-SCHEMA being absorbed (Carry 9); the brief-route edit-briefs, data edits under Forward-carry (Carry 10); the trailing-comment grammar, built (Carry 11); the word-start comment rule, built (Carry 12); `--mark` and `all`, built, with the arm for a pass cut short (Carry 13); the s9 bulk defects, docstring, incremental marks, comment parse and `--batch`, built (Carry 14); the loop and its subcommands, plus the read-only `show` and `diff` of this repair, built (Carry 15); the marker guard, now built (Carry 16); `absorbed --into`, op built, data edits under Forward-carry (Carry 17).

Also: carry 13(2) (the drain's timeout loses marks) has its own arm now: a pass that dies mid-queue keeps the marks already written (`run --mark`). The lane marker (`HPO_ROSTER_LANE=queue-runner`) is set by the queue runner, `carry_fold.py` and the two harnesses that call structural ops directly (`dev/audit/harnesses/r10_roster_push_race.sh`, `dev/audit/harnesses/r10_tick_which_roster.py`); `set-stage`, `append-group`, `set-resume` and `mark-carry` stay directly callable, as the carry specifies. A caller that sets the variable by hand is out of scope. This changes what a seat may call directly (policy-adjacent): it needs the owner's approving review before merging.

Merged `origin/main` (30638cf0c, 2026-11-06 16:15 UTC) into the branch cleanly; `tools/pr/prepr.sh` is re-run at the head below.

## Head

2b27bf482e33ab4fd7e1fdb867353a74b8da10a3

## Mutation proof

`python3 tools/audit/seat/r10_roster_ops_mutants.py` (all 105 plants, the driver restores each file byte for byte; it prints `plants: 105, without a FAIL line: ['C6']`). Every plant of this group is killed by at least one FAIL line, none by a crash: W1 12, W2 3, W3 2, W4 1, W5 1, W6 3, W7 1, W8 1, W9 2, W10 2, W11 4, W12 1, W13 1, W14 1, W15 1, Q1 2, Q2 3, Q3 1, Q4 2, Q5 3, Q6 1, Q7 1, S7 2, K8 4, K12 2, H2 1, and the plants this repair adds: Q8 2 (the batch path loads the edit checkout's editor), Q9 1 (the loader executes a file that is no roster_edit), Q10 1 (`diff` blind to removed groups), Q11 3 (`diff` compares a carry by count), Q12 1 (`show --stage` unfiltered), W16 8 (the lane guard dropped), W17 1 (`set-stage` made structural), Q13 1 (the runner does not set the marker).

Failing test first: at the head before the fix, `python3 -I tools/audit/seat/roster_queue.py --self-test` exits 1 with `ModuleNotFoundError: No module named 'roster_edit'` at `_run_batch`; after it, 52 checks, 0 failed.

Inherited, not this diff's: plant C6 (roster_edit.py, from R10-ROSTER-OPS) is `rc=1` with no FAIL line, a crash (`KeyError: 'carry'` in `op_drop_carry` on the mutated tree); the same result at `origin/main` (30638cf0c, `r10_roster_ops_mutants.py C6` in a detached worktree of it). The plant is killed, by a crash in a later arm; two attempts to turn it into a FAIL line crashed in yet another arm and were reverted. Carry: R10-CARRY-RESIDUE-2 (item: C6 killed by crash, not by FAIL line).

## Null control

Each refusal has its passing twin in the same self-test. New here: a `run --batch` with no `--editor` resolves the roster_edit.py beside the script and never the edit checkout (`resolve_editor` arm); a stub editor passed with `--editor` is the file both the batch's fallback and the single-op path run; `diff` of the same ref twice is empty; `show` without `--stage` lists both groups; `show` and `diff` leave the working tree and index unchanged; `set-stage`, `append-group`, `set-resume` and `mark-carry` need no marker; a structural op with the marker is accepted; a marker with another value is not the lane. Earlier nulls hold: a numbered label and text naming no proposal land; a bare `append-group` path lands; overlap on the index file only lands; append-carry to an open group with no PR lands with no WARN; a queue run without `--mark` leaves the queue byte-identical; a batch of one is byte-identical to the single-op roster; a quoted `'a # b'`, `@/p/b#1.txt` and `s6-batch8.md#P70` keep their `#`; a held line whose batch file is absent stays held. The unmodified base (b36679ce) under `python3 -I`: `roster_queue.py --self-test` 17 checks, 0 failed (the base has no batch path).

## Figures

- `python3 -I tools/audit/seat/roster_queue.py --self-test`: 52 checks, 0 failed at the head (17 at the merge base b36679ce)
- `python3 -I tools/audit/seat/roster_edit.py --self-test`: 242 checks, 0 failed (191 at the merge base)
- `python3 -I tools/audit/seat/roster_lib.py --self-test`: 63 checks, 0 failed (60 at the merge base)
- `python3 -I tools/audit/seat/r10_roster_ops_mutants.py --self-test`: 321 checks, 0 failed (231 at the merge base)
- `python3 -I tools/audit/seat/carry_fold.py --self-test`: 6 checks, 0 failed
- `python3 tests/structure.py`: STRUCTURE RATCHET PASSED
- `PYTHONPATH=tests/hastub python3 tests/entities.py`: ALL 2637 ENTITY CHECKS PASSED (run before the merge of `origin/main`; rerun by `prepr.sh` at the head)
- `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)`: MODE: SCOPED, runs `tests/entities.py` only
- Absorbed groups with no `resume.absorbed_into`, python json over the r10 roster at the merge base: 13 of 13. This is why the write-time check is at the op and brief_lint is unchanged.

## Red checks

At PR head `21be201c`, across all 68 check runs (all pages, `ev/check-runs.tsv` of the review):

- `governance / instrument-self-tests` (concluded failure): the `roster_queue.py --self-test` crash under `python3 -I`, finding 1. Cheaper detector: the same command CI runs, `python3 -I tools/audit/seat/roster_queue.py --self-test`, about 10 s locally; standing cost: one line in this handoff's figures. The driver `r10_roster_ops_mutants.py` now runs every target's self-test under `-I` too, so a plant is measured the way CI runs it.
- `pr-contract / pr-contract` (concluded failure): refused because `governance / instrument-self-tests` was red and `## Red checks` did not name it; it clears with the repair and this section.

No other check run concluded failure at `21be201c` (the first-pass `gate` run was superseded; the three later `gate` runs concluded success). No open `code-scanning alert` is known at that head.

## Forward-carry

- Carry 13(2), the drain's timeout: Carry: R10-ROSTER-WRITE-SWEEP | dismissed: the drain script is not in the tree and `run --mark` writes each mark as its op pushes, pinned by the arm "a pass that dies mid-queue keeps the marks already written".
- Roster DATA edits these ops enable, which write the roster branch this seat may not write. Each carries its control as a precondition. Carry: R10-CARRY-RESIDUE-2 (item: carry 4, `set-resume --field pr` for every done group lacking `resume.pr`, starting R10-FLOW-RECORD-PITCH = 2836; precondition: the count of done groups lacking `pr` is measured at the roster seat's own base, and a group's `pr` is read from `dev/programme/delivery/<N>.md`, never guessed).
- Carry: R10-CARRY-RESIDUE-2 (item: carry 9, one `edit-brief` per live group whose brief still names `the seat pushes refs only, through tools/audit/seat/handoff_push.sh`; precondition: a python count of that phrase over live groups' briefs is the control, and reads 0 afterwards; 64 groups carry it in total at the review's base, 1 live).
- Carry: R10-CARRY-RESIDUE-2 (item: carry 16 data, `set-stage <G> absorbed --into <host>` for the ten folded groups of the carry and for the 13 absorbed groups with no host; precondition: afterwards `carry_audit.py roster` reports each group's carries as REROUTED to its host, and the lint refusing an absorbed group with no `absorbed_into` is built only after those data edits land, because it would fail the roster as it stands: 13 of 13 lack the field today).
- Carry: R10-CARRY-RESIDUE-2 (item: plant C6 killed by a crash, not by a FAIL line, as above).

## Friction

none
