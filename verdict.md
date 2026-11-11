Fix review: merge 3861ae76214c26900658bfa52c91d880fe8865a1

bus-nonce: a07d5db61320a9fc168daa78e2a55171

This is round 4 (past the third by the orchestrator's ruling; `fixer.md`'s re-cut is waived by it). Scope: delta against d710f5dd, body-only since round 3. `git diff 7215e37c 3861ae76214c26900658bfa52c91d880fe8865a1` is the main merge plus `dev/programme/delivery/3431.md`; nothing under `custom_components/` moved.

## Evidence

- RESULT null (unmutated head, worktree at 3861ae76214c26900658bfa52c91d880fe8865a1): `ALL 115 HARNESS HEADER CHECKS PASSED`.
- RESULT M1a (`tests` insert reverted to `"tests"`): `2 of 115 HARNESS HEADER CHECKS FAILED`, P2 and P3. Killed, as the body states (ev/mutant-M1a.diff, ev/M1a.txt).
- RESULT M1b (`custom_components` insert reverted): `2 of 115 HARNESS HEADER CHECKS FAILED`, P1 and P3. Killed (ev/M1b.txt).
- Each mutant ran from a git-initialised `git archive` copy of the head. M1 and M3 were not re-run; the two single-insert mutants cover each insert.
- Merge: `git merge-tree --write-tree origin/main 3861ae76214c26900658bfa52c91d880fe8865a1` exits clean, no conflict.
- Red checks. `merge_train.py owed-reds` includes `tests / fast (3.14)` and `pr-contract / pr-contract`. The body's `## Red checks` names `tests / fast (3.14)` with its answer, and the re-run is green. It does not name `pr-contract`. `pr-contract` went red at 11:27Z and 12:39Z on body defects. Its run at 12:53Z (check run 130534199090) started after the last red concluded (12:39Z) and is `success`, so per the contract that run is the evidence. The `gate` job is green in the 12:54Z run.
- Instrument note: `review_packet.py` still refuses `red-unanswered` for `pr-contract`. It counts the superseded earlier-run reds although the latest run is green. I judged by the live run, not the packet's refusal. A `gate` job from a later run (43005948438) was still queued at my read.
- `merge_train.py classify` printed `REFUSE ci: the check runs ... could not be read` (unreadable: rc not usable). The verdict rests on the live check runs read through the API.
- Not re-derived: the scoped gate and `tests/stress.py` figures (CI's heavy runs are cited, not re-run). No claim-file, VERSION or manifest change in the diff.
- Carry audit at the head: 6 routed, 0 unrouted (packet).
