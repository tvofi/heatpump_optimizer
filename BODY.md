R10-ROSTER-WRITE-SWEEP: the roster write path's residue in `tools/audit/seat/roster_edit.py` and `tools/audit/seat/roster_queue.py`, built carry by carry, each with a self-test arm and a plant. Part of #201.

Built: carries 0, 2, 3, 4 (the op), 5, 6, 7, 10, 11, 12, 13, 14 and 16 (the op). Carry 1's own plants M4-M6 are not in the tree and cannot be reconstructed from the carry, so the group adds W1-W15 and Q1-Q7, each killed by a FAIL line, as the tightening it asks for. Carry 14's LANDED readback is built for inline `append-carry` (first 60 characters against the roster at the pushed sha); its `unwired` sweep reads open issues from a file (`--open-issues FILE`) so no network call lives in the instrument. Carry 13(2)'s drain script is not in the tree; its timeout loss is closed by `run --mark`, which writes each mark as its op pushes. Carry 8's ordering holds: R10-ORCH-ROSTER-SCHEMA is absorbed in the roster.

Dispositions by the review packet's 1-based numbering of the 17 brief carries (the brief's own list starts at 0, so each is one higher than the numbers above): lettered proposal labels, built (Carry 1); the M4-M6 plants, answered by W1-W15 and Q1-Q7 (Carry 2); the stale note, built (Carry 3); closing-destination refusal, built (Carry 4); `pr` in set-resume, built (data edits under Forward-carry) (Carry 5); the overlap refusal and phase branches, built (Carry 6); `append-group @file`, built (Carry 7); the host-path gate, built (Carry 8); ordering after the schema group, holds (Carry 9); the brief-route edit-briefs, its data edits are under Forward-carry (Carry 10); the trailing-comment grammar, built (Carry 11); the word-start comment rule, built (Carry 12); `--mark` and `all`, built (Carry 13); the s9 bulk defects: docstring, incremental marks, comment parse and `--batch` built (Carry 14); the loop and its subcommands, built (Carry 15); the marker guard, withheld pending the owner, see Forward-carry (Carry 16); `absorbed --into`, op built, its data edits are under Forward-carry (Carry 17).

Left for the roster seat and the owner, stated here because this branch writes no roster branch:

- The marker guard on structural ops (brief carry 16 by the packet's count) is withheld: it would make `append-carry`, `set-after`, `edit-brief`, `drop-carry`, `wire-issue` and `unwire-issue` refuse every direct caller, including `dev/audit/harnesses/r10_roster_push_race.sh` and the orchestrator's written procedure, which changes what a seat may do; it waits for the owner's ruling (the carry is "Owner-ordered: no").
- Roster DATA edits these ops enable but this branch cannot make, since they write the roster branch: `set-resume --field pr` for every done group lacking it, starting `R10-FLOW-RECORD-PITCH` = 2836 (carry 4); one `edit-brief` per live group whose brief still names the old handoff route (carry 9); `set-stage <G> absorbed --into <host>` for the ten folded groups of carry 16 and for the 13 absorbed groups with no host. Re-measure each count at the roster seat's own base.

## Head

16536a2a1ca33ce9073dfbcff786bc0937c7e238

## Mutation proof

`python3 tools/audit/seat/r10_roster_ops_mutants.py W1 ... W15 Q1 ... Q7 S7 K8 K12 H2` (the driver restores each file byte for byte). Every plant exits rc=1 with at least one FAIL line, none a crash: W1 lettered label unmatched (12 fails), W2 `@` strip dropped (3), W3 overlap ignores stage (2), W4 `--reason` always admits (1), W5 index exemption dropped (1), W6 closing refusal (3), W7 open-PR WARN (1), W8 `absorbed_into` unnamed (1), W9 `pr` field (2), W10 stale note kept (2), W11 privacy gate uncalled (4), W12, W13 and W14 the `--into` checks (1 each), W15 phase branch (1, roster_lib), Q1 plain `shlex.split` (2), Q2 run-start snapshot written (3), Q3 flag folded into value (1), Q4 held line released with its file absent (2), Q5 wrong line marked (3), Q6 `all` without `--mark` (1), Q7 no self-heal (1). W4 and W13 first survived (W4 crashed instead of failing; W13 had no arm); the W4 plant was re-cut and a self-absorb arm added, and both are now killed. The refactor re-anchored K8, K12, H2 and S7, which are killed again.

## Null control

Each refusal has its passing twin in the same self-test: a numbered label and text naming no proposal land; a hyphenated non-label lands; a bare `append-group` path lands; overlap on the index file only, or with an in-progress or done group, lands; append-carry to an open group with no PR lands with no WARN; set-stage done keeps a note that owes nothing; a scrubbed carry lands; `set-stage absorbed --into` a live group lands; a queue run without `--mark` leaves the queue byte-identical; a batch of one is byte-identical to the single-op roster; a quoted `'a # b'`, `@/p/b#1.txt` and `s6-batch8.md#P70` keep their `#`; a held line whose batch file is absent stays held; every open issue listed reports nothing unwired.

## Figures

- `python3 tools/audit/seat/roster_edit.py --self-test`: 232 checks, 0 failed (191 at the merge base)
- `python3 tools/audit/seat/roster_queue.py --self-test`: 37 checks, 0 failed (17 at the merge base)
- `python3 tools/audit/seat/roster_lib.py --self-test`: 63 checks, 0 failed
- `python3 tools/audit/seat/r10_roster_ops_mutants.py --self-test`: 297 checks, 0 failed
- `python3 tests/structure.py`: STRUCTURE RATCHET PASSED
- `bash tools/pr/prepr.sh` at this head: PRE-PR rc=0; origin/main did not move since the run (7e8939d38), so no second run.
- `python3 tests/closure.py select`: MODE: SCOPED, runs `tests/entities.py` only, which passes.
- Absorbed groups with no `resume.absorbed_into`, python json over the r10 roster at the merge base: 13 of 13. This is why the write-time check is at the op and brief_lint is unchanged: a lint refusing absorbed-without-host would fail the roster as it stands.

## Red checks

none

## Forward-carry

none

## Friction

none
