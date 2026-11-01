Root-cause seat for the eight issues a done transition orphaned (#2248, #2249, #2674, #2731, #2492, #2257, #2942, #2998), with its countermeasure. The analysis is `dev/audit/rca/R10-RCA-ROSTER-SYNC-ORPHANS.md`; the issue-facing **Root cause** section is below, for the orchestrator to post (this seat makes no GitHub write).

**Cause.** Ownership of an issue is derived from its group being open (`carry_audit.Dests`, via `roster_lib.is_open`), so the write that closes a group also drops it as owner of every issue it lists. Neither writer of a closed stage reads ownership: `roster_sync.py`'s `derive` MERGED arm writes `done` from the merge alone, and `roster_edit.py`'s `op_set_stage` / `op_set_resume --field stage` write any classified stage. The one detector, `carry_audit.py sweep --issues`, runs later and by hand, and with no `--roster-ref` it reads main's roster copy, not the live ref `origin/handoff/audit-r10-roster` (`git ls-remote` at `806d2db83aa0`) where both writers write.

**Process state: (c).** The sweep (`finding-propagation.md`'s enforcement) existed and was run; its unit, main's copy, did not reach the live record, so it missed 3 of 8, and even its 5 were found tens of hours late. The countermeasure changes the unit and moves the same test to the transition.

**The eight**, through `carry_audit.load_dests(<ref>).owned` at origin/main and at the live tip before the 2026-11-01T09:10Z closes (`84571a150c06`):

| issue | main's copy (the sweep) | live ref | dropped by |
|---|---|---|---|
| #2248, #2249 | UNOWNED: caught | UNOWNED | `roster_sync` R10-STORE-RACES done |
| #2257 | UNOWNED: caught | UNOWNED | `roster_sync` R10-ADVISOR-WHATIF done |
| #2942 | UNOWNED: caught | UNOWNED | `roster_sync` R10-FRICTION-MUTATION-SURVIVOR done |
| #2998 | UNOWNED: caught | UNOWNED | none: no group listed it before `e74e0870a` |
| #2492 | R10-SAV-ACTUATION, `in-progress` on main: missed | UNOWNED | `roster_sync`, then `set-stage` |
| #2731 | R10-FLY-GH-READ-RETRY, `carries-open` on main: missed | UNOWNED | `roster_sync` R10-FLY-GH-READ-RETRY done |
| #2674 | `carry-2674.json`: missed | `carry-2674.json` | none under the rule: a carry file is a destination |

The live ref catches 7 of 8; the transition test reaches 6 of 8 at write time (not #2998, never owned; not #2674, owned by its carry file).

**Countermeasure.** One owned-issue test, `carry_audit.Dests.owns`, now used by `check`, `sweep --issues` and the new `carry_audit.orphaned(dests, group)` (the `--issues` test asked of a closing group on the roster the write leaves; an unreadable state counts as open). `roster_sync.hold_open` writes `carries-open` at the merge commit instead of `done`, printing `HELD: owns open #n`, on the dry run and on the write path's re-derive; groups closing in one pass are judged together. `roster_edit.hold_done` does the same for `set-stage` and `set-resume --field stage`. `carry_audit.py sweep` with no `--roster-ref` reads `roster_lib.reader_ref` (`sweep_ref`). Offline, both writers take `--issue-state FILE`. No roster data file is edited.

## Head

`630b15e45`, which merges origin/main `6421fe135` (it moved from the dispatched base `92588d581fde4ce287af3db5e8bb61461dc28015` by #3075, touching none of this diff's files); every self-test and the scoped gate below were re-run at it.

## Mutation proof

In-tree harnesses, each plant applied alone and the file restored:

- `python3 tools/audit/seat/r10_roster_sync_mutants.py M25_hold_dropped M26_apply_unheld M27_owners_before_close M28_issue_state_ignored`: M25 rc=1 fails=4 (`a merged group owning an open issue nothing else owns is held carries-open ...`, `two groups closing together are not each other's owner: both are held`, `the dry run holds a merged group ...`, `the hold is written: carries-open at the merge commit`); M26 rc=1 fails=1 (`the hold is written ...`); M27 rc=1 fails=4 (the same four as M25); M28 rc=1 fails=3 (`... one whose issue is closed is done (null control)`, `... and closes one whose issue is closed (null control)`, `... and the closed issue's group is done (null control)`).
- `python3 tools/audit/seat/r10_roster_ops_mutants.py H1 H2`: H1 rc=1 fails=2 (`set-stage done holds a group owning an open issue nothing else owns`, `... and so does set-resume --field stage, with any closed stage`); H2 rc=1 fails=1 (the second).
- carry_audit's own sites, by a scratch driver over `python3 -I tools/audit/carry_audit.py --self-test` (`$SCRATCH/ca_plants.py`): CA1 unread state counts closed, rc=1 fails=1 (`... an unreadable state counts as open, ...`); CA2 sweep reads main's copy, rc=1 fails=2 (`a sweep with no --roster-ref reads the round's live roster ref`, `at the live ref a group done there owns nothing; main's stale copy still credits it (#2492's miss)`); CA3 state ignored, rc=1 fails=1 (`... a closed issue is no orphan (null control)`); CA4 owner test dropped, rc=1 fails=3 (`a group closing with an open issue ...`, `... a carry file is another live owner`, `... and an O-brief is too`).

## Unpinned sites

The `carry_audit.py` sites `orphaned`, `sweep_ref` and `Dests.owns`: M28 pins `orphaned`'s state arm through roster_sync's self-test in `r10_roster_sync_mutants.py`; the other three were killed by the scratch driver above, which is not in the tree (`r10_carry_parser_mutants.py` censuses the parser only). Disposition: whatever `prepr.sh` step 6d lists is answered there; a `tools/` site needs an in-tree mutant harness, and adding the CA plants to `r10_roster_sync_mutants.py` would run the wrong self-test for CA1, CA2 and CA4.

## Null control

- `python3 tools/audit/seat/r10_roster_sync_mutants.py --null`: rc=0 fails=0. `python3 tools/audit/seat/r10_roster_ops_mutants.py --null`: rc=0 fails=0. The scratch driver's unplanted run: rc=0 fails=0.
- Every new check that asserts a hold has a null twin in the same fixture that asserts no hold: an issue a live group also lists, a closed issue, a carry file, an O-brief.
- The sweep, online, at origin/main `92588d58`: the base (`python3 -I tools/audit/carry_audit.py sweep --issues` from the base checkout) prints four ISSUE-UNOWNED (#2999, #2998, #2965, #2257); the head prints none; the head with `--roster-ref origin/main` prints the same four, so the difference is the ref.

## Figures

- Self-tests at the head: `python3 -I tools/audit/seat/roster_sync.py --self-test` 83 checks, 0 failed (base 75); `python3 -I tools/audit/carry_audit.py --self-test` 214 checks, 0 failed (base 206); `python3 -I tools/audit/seat/roster_edit.py --self-test` 135 checks, 0 failed (base 131); `python3 -I tools/audit/seat/r10_roster_ops_mutants.py --self-test` 105 checks, 0 failed.
- The defect, replayed on its own instances: the base's and the head's `python3 -I tools/audit/seat/roster_sync.py --checkout $DEMO/co --pr-state $DEMO/prs1.json` dry run, `$DEMO/co` a clone whose origin holds the live roster at `c47931afa` (the parent of R10-FRICTION-MUTATION-SURVIVOR's done, PR #2961): base `stage in-progress -> done at 13871b7aa4a1`; head (`--issue-state` #2840 and #2942 open) `-> carries-open at 13871b7aa4a1 (PR #2961 MERGED) HELD: owns open #2942`; head with #2942 recorded closed: `-> done` (null control). The same at `22622ddf6` with PR #2639, issue state read live from `gh`: base `-> done at 57b7b4994ac7`; head `-> carries-open ... HELD: owns open #2731`.
- The class over round 10: `python3 $SCRATCH/replay3.py $WT origin/handoff/audit-r10-roster $SCRATCH/issues.tsv` (replay3.py sha1 064d1f09be558cad9c570f9639a81d72a10c9a09; issues.tsv sha1 cff944d284d69bc3a92bfed0dbaaf21860839194, the REST `issues?state=all` number, created_at, closed_at, state, read 2026-11-01). Rule: every first-parent version of `dev/programme/rosters/wave-r10-groups.json` on the live ref; a transition is a group whose stage moves from an open stage into `roster_lib.DONE_STAGES`; an orphan event is an issue `carry_audit.orphaned` returns against the post-commit roster, with the issue open at the commit's committer date. Printed: 2382 versions, 264 transitions; 67 orphaning (39 `roster_sync`, 19 `set-stage`, 9 hand commits, all before 2026-10-20), 94 closing with every issue owned or closed, 103 owning none; 86 issue-orphan events over 63 issues and 60 groups; fates 26 re-staged by hand, 33 wired elsewhere, 27 closed, 0 orphaned at the tip; window median 7.75 h, 70 over 1 h, 20 over 24 h, 1754.5 issue-hours. Null control: an independent replay with its own owner logic (`$SCRATCH/replay.py`, sha1 2ac7792379625fb6b3c5bd3d09691fc7e83c6b65) prints the identical 86 event lines (`diff` of the two `ORPHAN` line sets, empty, then `IDENTICAL-EVENTS`).
- Cost test inputs, measured here: one `gh api repos/tvofi/heatpump_optimizer/issues/2731` 0.35-0.37 s; one `roster_edit.py set-stage` op to its lint gate, no push, 10.3 s; `roster_sync.py` dry-run pass 9.27-9.73 s base, 9.55-10.40 s head with one hold read; `roster_lib.reader_ref` 0.06-0.07 s; `carry_audit.py sweep --issues` 0.88-0.93 s. The replay's state reads: 145 of 227 owned-issue references (`replay3.py`'s `issue-state reads` line).

## Cost test

Wall-clock over round 10 (2026-10-17 to 2026-11-01). Standing cost: 145 reads x 0.36 s = 52 s; disposal ops, +1 for a held group a person then disposes otherwise, -1 for one a person re-staged `carries-open` by hand (per transition: `roster_sync` 21 and 18, `set-stage` 17 and 2): +18 ops x 10.3 s = 185 s; the sweep's ref read 0.06 s each. About 237 s a round, 4.1 s per tool-written orphaning transition (58). P(recurrence), measured: 67 of 264 transitions orphaned an issue (58 tool-written), 67 of the 161 that owned one. Cost of the defect: finding and tracing each orphan, and its window (a carry to it refused `#n has no owner`, nothing dispatching it); the disposal decision is owed either way and cancels. Tracing time was not measured; the sweep alone is 0.9 s and missed 3 of 8. Verdict: pays if finding and tracing one orphan costs a seat more than 4.1 s; and the class meets `defect-root-cause.md`'s audit-class count (3+ in one round), so a barrier is owed whatever the test says and the test picks its form. The hold is the cheapest form found: a refusal at `roster_edit` costs the same op (refused, dispose, re-run) and one more where the owner wanted `carries-open`, and at `roster_sync` it leaves a merged group at its pre-merge stage; a warning is (b)'s treatment for a (c) cause; a self-releasing hold would save 36 ops (371 s) but needs a marker telling a sync-held `carries-open` from a person's and a re-read of every held group each beat pass, whose cadence this seat did not measure: not built.

## Scoped gate

`python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir $D`: `MODE: SCOPED -- 1 script(s) run, 32 scoped out`; `scope.run` names `tests/entities.py`, run with `PYTHONPATH=tests/hastub python3 tests/entities.py` at `630b15e45`: ALL 2497 ENTITY CHECKS PASSED, rc 0. `python3 tests/structure.py`: STRUCTURE RATCHET PASSED. `bash tools/pr/prepr.sh` on this body at `630b15e45`: rc=0, every step ok or skip (unpinned sites: "the diff adds no unpinned mutation site"). origin/main has not moved since that run (`6421fe135`), so no second merge or prepr run was owed.

## Red checks

none

## Forward-carry

- The class (an open issue dropped by a done transition, 67 transitions in round 10) meets the audit-class count and is not in `dev/audit/config/bugclasses.json`; registering it, with this RCA as `rca` and the hold as its barrier, is the orchestrator's. Carry: dismissed: the orchestrator owns the bugclasses register and this seat writes none
- An issue filed with no owner at all (#2998, and the two other `[policy] recurring friction` issues the base sweep listed) is out of a transition test's reach; `sweep --issues` stays its detector, now on the live ref. Carry: dismissed: no transition drops it and the sweep already reports it
- #2674's carry file said no live group covered it while R10-STORE-RACES listed it (2026-10-26 to 2026-10-29); whether `brief_lint.mjs`'s refusal of that state runs on the live ref was not measured. Carry: dismissed: not measured here and the carry file is a valid destination today

## Friction

- payload-identity: contradiction: the payload says to pin commit identity `seat <seat@users.noreply.github.com>`; the brief snapshot says `hpo-fixer <70032254+tvofi@users.noreply.github.com>`; the commits carry the brief's, the task-specific one. Carry: dismissed: a dispatch-template disagreement the orchestrator resolves on the next render
- payload-role: contradiction: the payload names `fixer.md` as the role, the brief `root-cause.md`; this seat followed `root-cause.md` for the analysis and `fixer.md`'s gate steps for the code. Carry: dismissed: same template, same owner

## Root cause (for the issue)

State **(c)**: `carry_audit.py sweep --issues` existed and ran, but read main's roster copy, not the live ref, and ran after the fact; neither done writer (`roster_sync` MERGED arm, `roster_edit set-stage`) read ownership. Cost test: about 237 s a round standing (145 issue reads, +18 disposal ops) against 58 tool-written orphaning transitions a round, 86 issue-orphans, a median 7.75 h window, and a sweep that missed 3 of 8; the class meets the audit-class count. Countermeasure: the done transition writes `carries-open` while an owned issue is open with no other live owner (carry_audit's one test), and the sweep reads the live ref. `dev/audit/rca/R10-RCA-ROSTER-SYNC-ORPHANS.md`.
