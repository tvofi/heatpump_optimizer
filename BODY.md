R10-FLY-ORPHANS-REWRITTEN (issue #2721, which the roster lists for this group and does not mark fixed). Two classifiers answered "does main already carry this handoff": `bus.sh orphans`' `content_superseded`, and `ledger.py level`'s `covered`. They disagreed, and both missed landed work. `content_superseded`'s modify arm wanted a byte-identical blob. So a hunk that another pull request landed in a file main later changed read as stranded: r10-earlycutoff-coverage (ecaf178cb) stayed listed 121.8 h after #2397 merged it. The level wrote two lines per topic, one for the code ref and one for the body ref, and owed merged handoffs until someone archived them.

What changes:

- `ledger.landed(git, main, tip, heads)` is now the one owner, and `bus.sh orphans` and the relay's level both use it. It has four arms, checked in order:
  - `ancestor`: `rev-list --count tip --not main heads` is 0.
  - `merges-only`: the roster carry's a457acaf4 shape. `--no-merges` count 0, and every merge outside main and the heads has an empty `diff-tree --cc`.
  - `reverse-apply`: the brief's test. The patch from the merge base applies to main reversed and fails forward. It runs in a throwaway index, never the work tree.
  - `content`: `covered`, extended per path. Same blob at the path; an added file's blob anywhere on main (a moved file, which replaces the old basename-only match); a deletion main already made; otherwise the existing line test.
- `bus.sh orphans` calls `ledger.py landed` once per run (tips on stdin) and deletes `content_superseded`. `ancestor` and `merges-only` count as `ancestor=`; `reverse-apply` and `content` print `SUPERSEDED`.
- Fold: the relay's `handoff-no-pr` level now writes one line per topic. A body ref adds `body=<sha>` to its code ref's line, and `escalate` reads the repair from that. A body ref with no code ref keeps its own line, as before.
- The any-state closer the carry assigns to this group (RCA section 5.1) is now in the relay's level. The relay lists merged PRs (`gh pr list --state merged`) as `<topic> merged=<utc>`. A tip committed at or before that merge is closed. A re-handoff committed after the merge stays owed. If that listing fails, the level stays as it was. This closer is needed because content tests alone miss the handoffs of #2513, #2519 and #2525 (Figures). Each reverse-applies at its own merge commit, but the merge's delivery-row record rewrites the PR's files right afterwards.

Residual, measured below: `bus.sh orphans` reads only refs over the git protocol and has no PR listing, so a merged handoff whose files main has since moved on from still reads `ORPHAN` there (3 of the 6 landed cases at the 22:33 main). The relay's level closes all 6. A merged-PR read for `bus.sh` would need a token it deliberately does not hold. Carry: #2721

Alternatives considered:
- Keep `content_superseded` and add a reverse-apply arm in bus.sh. This lost because it would leave two classifiers of the same fact, which is the second carry's defect.
- Retire bus.sh's content arm in favour of reading the relay's `<log>.level`. This lost because bus.sh runs off-host (`pulse.py`, `ci_probe.py`) where that file does not exist.
- Close on any merged PR of the topic, whatever the tip's age. This lost because a re-handoff to a reused topic after a merge would be closed silently. The `ct <= mergedAt` guard keeps it owed (the null control `L26`).

## Head

b082a93e7934fb56514174ec1958b07644b8ae12, a fast-forward of d0f6de273 (round 2, after the blocked verdict on 9328902). Measured against origin/main beb570c817c4efcae0d5f6f4bba52f3383baf8db at 2026-10-28T18:46Z.

## Mutation proof

`python3 -I tools/audit/seat/r10_ledger_mutants.py`, run at b082a93e7: `plants: 48, without a FAIL line: none`, rc 0 (42 at d0f6de273). These are the plants this diff adds or re-anchors, each with the checks that go red:

- `L5_no_ancestry_close`: `landed: a tip inside main reads ancestor, not merges-only`
- `L6_no_content_close`: `landed: the re-applied hunk is content (reverse-apply cannot: forward applies too)`, plus three level checks
- `L19_no_reverse_apply`: `landed: a patch main holds whose removed line main keeps elsewhere is reverse-apply, not content`
- `L20_forward_not_refused`: `null control: a patch that applies both ways (an unpatched copy remains) is not landed`
- `L21_merges_unchecked`: `null control: a merge carrying its own resolution is not merges-only`
- `L22_merges_with_nonmerges`, the carry's mutant (`--no-merges` dropped): `landed: a merge tip whose parents main and a fix head carry is merges-only`
- `L23_moved_add_unchecked`: `null control: the same add with other bytes is not`
- `L24_body_own_line`: `the level owes the uncovered topic once, at its code ref, and the body-only ref`, plus three more
- `L25_merged_ignored`: `a topic whose PR merged after its tip's commit is closed by the merge (RCA 5.1)`
- `L26_merged_any_time`: `null control: a tip committed after its topic's merge stays owed`
- `R6_merged_unread_clears`: `an unlisted merged set leaves the level as it was, never re-owing what a merge closed`
- `B1_orphans_merges_stranded`: `a tip outside main and the fix heads only by a clean merge is discharged with the ancestry`
- `B2_orphans_no_content`: `a patch that applies to main reversed and not forward is SUPERSEDED`

Round 2 (verdict/2920's block and its four surviving mutants). Each arm was added failing first: with its plant applied, the named check is the one FAIL line (`r10_ledger_mutants.py <plant>`, `fails=1` each); without the plant it passes.
- `L27_deletion_unguarded`, the verdict's block (`if rc_m == 0:` to `if False:` in `covered`'s deletion arm): `null control: a tip deleting a file main still holds is not covered, beside a carried add`. The tip deletes `g.txt` and adds bytes main holds elsewhere, so the deletion guard alone decides it. The check asserts both `covered` is False and `landed` is None.
- `L28_deletion_always_refused`, the opposite mutant, which survived in ledger.py and was killed only by bus.sh: `covered: a deletion main already made is carried`.
- `L29_same_blob_arm_off` (the verdict's `same_blob_arm_off`): `covered: the same bytes at the path are carried, a removed line kept elsewhere notwithstanding`. It is not equivalent. Without the arm, the line test refuses a removed duplicate line that the same blob still holds.
- `L30_merged_strictly_before` (`merged_lt`): `a merge in the tip's own commit second closes it (at or before, not strictly before)`.
- `L31_merged_last_listed` (`merged_max_dropped`): `the topics reader keeps a topic's latest merge, whatever the listing order`. The topics parse moved out of `main()` into `read_topics()` so it is testable. Its behaviour did not change.
- `B3_orphans_classifier_unchecked` (`bus_die_dropped`): `null control: a classifier that fails refuses orphans, never an all-ORPHAN list`. A `python3` shim fails only `ledger.py landed`.

Failing test first: I ran the new `bus.sh` self-test cases against the baseline production code (0b8f8b585's `bus.sh` with only the self-test block added). It printed `bus self-test: 97 checks, 4 failed`. The failing checks were:
- `a hunk main carries in a file that moved on is SUPERSEDED, not stranded (#2397's shape)`
- `a patch that applies to main reversed and not forward is SUPERSEDED`
- `a tip outside main and the fix heads only by a clean merge is discharged with the ancestry`
- `green: with the pull requests pushed nothing is stranded and the run is 0`

## Null control

The unmodified tree: `r10_ledger_mutants.py --null` gives rc=0 and fails=0 for each of `bus.sh`, `cloud_relay.sh`, `ledger.py` and `orchestrator_tick.py`. On the baseline, the harness reads the six landed cases as `MISREAD 5` (main 57f0c9c77) or `MISREAD 6` (main 0b8f8b585). Its `null` case, a commit adding a file main lacks, reads `ORPHAN` and `owed` at both ends.

These null controls show that each new arm closes only what it should:
- A patch main does not hold stays stranded: the `orp-rev3` and `orp-nonm` self-test cases.
- A merge with its own resolution stays stranded: `orp-evil`.
- A patch that applies both ways stays unlanded.
- An add whose bytes main does not hold is not a moved file.

## Figures

- `bash dev/audit/harnesses/r10_fly_orphans_landed.sh <checkout> 57f0c9c77cfd5958e0a2443e158bea8326bedae2` (main at 2026-10-21T22:33+02:00, the evidence's time):
  - baseline 0b8f8b585: bus.sh `MISREAD 5`; level `LEVEL-MISREAD 5`, `LEVEL-LINES 12 for 7 topics`
  - head d0f6de273: bus.sh `MISREAD 3` (earlycutoff, pr2465 and pr2485 SUPERSEDED); level `LEVEL-MISREAD 0`, `LEVEL-LINES 1 for 7 topics`, `body-follows-code=7 carried=1 merged-pr=5 owed=1`
  - The `null` case is ORPHAN/owed at both ends.
  - The pr<N> cases are a simulation, because those handoff refs are gone. Each is the PR head's tree rewritten as one commit on its parents' merge base.
- The same harness at `0b8f8b585daf6a84ae9470389a709d5fec2a4f47`: baseline `MISREAD 6` and `LEVEL-MISREAD 5`; head `MISREAD 4` and `LEVEL-MISREAD 0`.
- The class rule is "every arm of the one classifier is driven by the shared self-tests and pinned by a plant". Seams and dispositions, from `grep -n 'content_superseded\|def covered\|def landed' tools/audit/seat/*.sh tools/audit/seat/*.py` at the head:
  - `content_superseded`: deleted, closed in this diff.
  - `covered`: the per-path arms closed in this diff. The `rem & have` line test is kept, and the reverse-apply arm covers its duplicate-line blind spot (`L19`).
  - `landed`: new, pinned L5, L6, L19 to L26.
- `tests/entities.py` and `tests/harness_headers.py` ran under a Python 3.13 interpreter with `tests/requirements-ci.txt` installed. This host's `python3` lacks those packages.
- Gate, re-run at b082a93e7 (`python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)`): `MODE: SCOPED -- 1 script(s) run, 32 scoped out`. `tests/entities.py` printed `ALL 2467 ENTITY CHECKS PASSED`. The run_always scripts:
  - `tests/env_drift.py --claims-only`: ok
  - `tests/closure.py selftest`: 117 pins passed
  - `tests/layout.py`: ok
  - `tests/harness_headers.py`: 112 passed
  - `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`
- Self-tests at b082a93e7 (d0f6de273's figure in brackets):
  - `bash tools/audit/seat/bus.sh --self-test`: 98 checks, 0 failed (97; 92 on the baseline)
  - `python3 -I tools/audit/seat/ledger.py --self-test`: 77, 0 failed (72)
  - `bash tools/audit/seat/cloud_relay.sh --self-test`: 279, 0 failed (279)
  - `python3 -I tools/audit/seat/orchestrator_tick.py --self-test`: 215, 0 failed (215)
  - `python3 -I tools/audit/seat/r10_ledger_mutants.py --self-test`: 135, 0 failed (118)
  - `r10_ledger_mutants.py --null`: rc=0 fails=0 for each of the four owners
- Harness at b082a93e7, the same command: main 57f0c9c77 gives `MISREAD 3` and `LEVEL-MISREAD 0`. Main beb570c81 gives `MISREAD 4` and `LEVEL-MISREAD 0`. Both match d0f6de273, because round 2 adds tests and one behaviour-neutral extraction. The `null` case is ORPHAN and owed on both mains.
- `dev/audit/harnesses/r10_fly_orphans_landed.sh` is the fixer's own instrument. Issue #2721 names no committed harness, only the reverse-apply test, so no finder's harness exists to run (verdict/2920 finding 4).
- verdict/2920's `prune_refs.py classify()` seam: the reviewer dismissed it. It answers a different question (pruning, with roster-done evidence), it predates this diff, and the class rule does not return it. This diff leaves it alone.
- `python3 tools/audit/archscore/score.py --diff $(git merge-base origin/main HEAD)`: `Architecture score: dS +0.0000 NULL`

## Red checks

none. Round 1's head 9328902 concluded no failed check before the block (verdict/2920, `ev/ci-checkruns.txt`).

## Forward-carry

none

## Friction

none
