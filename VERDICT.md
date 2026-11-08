Fix review: blocked 88690628b6feb50266cdcdb175b2a9c293db472a mutant-survives: roster_invariants UNREADABLE guards (rc-not-in-(0,1) and OSError) survive their mutants

bus-nonce: 2eaf472221e370b63d40063fc461522f

Round 1 (first-round adversarial fix review). Measured head 88690628b6feb50266cdcdb175b2a9c293db472a; merge base cb5512741638029289deb392b30bc246fa667387. The head was unchanged at the time of the verdict (ls-remote).

## Block

- Two mutants on changed production lines in `tools/audit/seat/orchestrator_tick.py` `roster_invariants` survive the tick self-test (287 checks, 0 failed under each). The brief asks for a mutation proof on every changed production line. (T6) `if rc not in (0, 1) or not summary:` -> `if False:`: a `carry_audit.py roster` that exits 2 (RosterNotFound on a bad `--roster-ref`, or a crash) then prints nothing, so the tick reads clean. That is exactly the silent-green failure that the docstring's "A tool that cannot be read is one UNREADABLE line" promises against. (T8) The `except OSError` branch, which writes the UNREADABLE line, can be replaced by `except ZeroDivisionError: return` without any check failing. The body's `## Unpinned sites` names only the call, the open-issues argument and the null as pinned, so these branches are neither pinned nor dispositioned. Fix: add two tick self-test rows. In the first, the carry stub returns `(2, ["carry_audit: REFUSED cannot list ..."])`, and the row asserts one "roster invariants" UNREADABLE line and no "routing invariants broken". In the second, the stub raises OSError, and the row asserts the UNREADABLE line. Also consider a row for the `gh issue list` non-JSON path (`except ValueError: pass`), asserting that `--open-issues` is absent. Evidence: ev/tick-mutants.txt.
  Carry: built-here

## Findings

## Evidence

- CI: `merge_train.py classify 88690628b6feb50266cdcdb175b2a9c293db472a --pr 3342` -> `GREEN 88690628b6feb50266cdcdb175b2a9c293db472a pending: none red: none`, rc 0. Run twice, at the start and before the verdict (ev/classify1.txt). The packet digest lists no failed check run. `## Red checks` reports only a local prepr entities refusal, and CI has no red to answer.
- Merge: `git merge-tree --write-tree origin/main 88690628b6feb50266cdcdb175b2a9c293db472a` rc 0, no conflict.
- Role contract current: `git diff $(merge-base)...origin/main -- dev/governance/roles/` is empty.
- Named mutation proofs re-run (ev/mutants-named.txt, ev/tick-mutants.txt). T1, removing the `roster_invariants` call: 3 FAIL "REPLAN routing invariants at tick level", killed. `r10_roster_ops_mutants.py W18`: `RESULT mutant=W18 rc=1 fails=1` (FAIL "append-carry refuses text ending in a mark-shaped suffix"), killed. The full ops table at the head is W16 rc=1 fails=8, W17 rc=1 fails=1, W18 rc=1 fails=1, Q13 rc=1 fails=1, Q9 rc=1 fails=1. `r10_roster_sync_mutants.py M9_carry_dedupe_dropped` gives `rc=1 fails=1` at the head and `rc=0 fails=0` at the base, so it survived at the base, as the body says.
- Further reviewer mutants on the new tick code killed: T2 (--open-issues dropped), T3 (rc==1 never flags), T4 (always flags, which fails the null row), T5 (rows not printed), T7 (unconditional early return).
- Null control: T4 fails "null: a clean roster flags nothing from the invariant", so the null row moves under its perturbation. The W18 row also asserts the roster is unchanged after the refusal.
- Integration: the argv the tick builds, run against the real `carry_audit.py --roster-ref origin/handoff/audit-r10-roster roster --open-issues <file>`, gives rc 1 with STRANDED/ISSUE-* lines and a `CARRY-ROSTER:` summary, which is the shape the tick parses. The ISSUE-STRANDED lines for #2855 and #2875 at the roster tip came from a synthetic open-issues file, and both issues are closed. They are not live strandings.
- The append-carry refusal reuses `roster_lib.carry_mark` (one regex, `_CARRY_MARK`). The only non-test caller of `op_append_carry` is `roster_edit`'s dispatcher (`carry_fold.py` goes through the CLI), so no legitimate path appends text that is already marked.
- Self-tests: base tick 283/0, roster_edit 242/0, roster_sync 95/0. Head tick 287/0, roster_edit 243/0, roster_sync 96/0.
- Body figure "carry_audit.py roster at the merge base reports one stranded carry (R10-FLY-GANTT-DRIFT, absorbed)": re-derived, `1 stranded carry(ies)`.
- `tests/structure.py`: STRUCTURE RATCHET PASSED, rc 0 (ev/structure.txt). No `*_budgets.json` in the diff.
- `PYTHONPATH=tests/hastub python3 tests/entities.py` was run plainly and was clean: `ALL 2668 ENTITY CHECKS PASSED`, rc 0 (ev/entities.txt). The body's "3 fail in this container" (workflow-probe) does not reproduce here. Its 2665 baseline count is that container's and was not re-derived.
- Archscore: `score.py --diff cb5512741638 HEAD` -> `Architecture score: dS +0.0000 NULL` (ev/archscore.txt).
- VERSION, the manifest, RELEASE_NOTES.md and tests/closures.json are untouched. The new tracked file is only `dev/programme/delivery/3342.md` (the delivery row, present), and entities passed, so it is classified.
- `## Head` names 88690628b6feb50266cdcdb175b2a9c293db472a, the head reviewed.
- Carries 2-5 were delivered by 87c2852eb (#3250) and are not re-reviewed here. Carries 6 and 8 wait on an orchestrator disposition, as the body states. The issues named (#2855, #2875) are closed now, so nothing is stranded today.
