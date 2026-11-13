The relay's pending-ci block refused a verdict over a moved head before asking whether the head carried, and refused a RED finally, so reds that cleared with no fixer work (PRs 3425, 3430) stranded their drafts. `probe_arm` ignored `dispose` on `rev-`/`revt-` refs. `noreturn_arm` covered only fixers. This part builds Carries 21, 23, 30 and 7 inside `tools/audit/seat/cloud_relay.sh`.

Carry 21 (moved head): before refusing, the block runs `${HPO_RELAY_CARRY:-python3 -I review_carry.py} <drafted head> <live head> --verdict-only`. CARRY classifies the live head and posts on GREEN, the relay line saying the verdict was carried; FRESH-REVIEW or CANNOT DECIDE keep today's refusal.
Carry 23 (RED): RED returns 75 like WAIT with one `HELD-PENDING-CI-RED #<pr> <head>: <red contexts> (classify RED)` line per pass. The first RED read is recorded in the state dir (`cloud-pending-red`, `<ref> <sha> <head> <epoch>`); a WAIT or GREEN read clears it. Refusal is final only on a moved head review_carry does not carry (Carry 21's arm) or on a RED read `HPO_RELAY_PENDING_RED_SECS` (default 21600) after its first, and prints `cloud_relay: OWED re-dispatch #<pr> <head>` in place of "goes back to its fixer".
Carry 30: `probe_arm` skips a `rev-`/`revt-` ref when the existing `disposed` helper holds at its sha; a moved ref is relayed at the new sha.
Carry 7: `noreturn_arm` also lists `dispatch/reviewer-*`. A reviewer dispatch older than `HPO_RELAY_NORETURN_REVIEWER_SECS` (default 5400 s, the carry's measured figure above the 66 min returner maximum; set separately from the fixer's `HPO_RELAY_NORETURN_SECS`, default 7200) whose PROMPT.md nonce (first 8) names no `probe/rev-*-<n8>` or `probe/revt-*-<n8>` and whose PR head still equals the dispatched head is owed `seat-no-return` on the same level. The comment that called a reviewer's missing verdict reviewer-fire's is corrected.

Architecture: all four extend the seams that exist (the pending-ci block, `probe_arm`'s `disposed` check, `noreturn_arm`'s level) with no parallel mechanism; two small helpers (`pending_red_seen`, `pending_red_clear`) hold the RED record. Alternative refused for 23: recording the clock in `cloud-relayed.refused-why`, which only exists after the refusal it is meant to delay. Policy edits: none.

## Review block answered (round 2, blocked 740e6074 on four surviving mutants)

Each reviewer mutant spec (`ev/mutants.json` of probe/rev-3541-7c9edde1, run unchanged, `mutant_run.py --spec ... --cmd 'bash tools/audit/seat/cloud_relay.sh --self-test' --copy-tree`) before at 740e6074 (ev/mutant_run.*.log) and after at this head. No predicate was unreachable, so none was removed and none is routed elsewhere; production text is unchanged from 740e6074.

- redsecs-validate-off: SURVIVED -> KILLED. Pinned by a non-numeric `HPO_RELAY_PENDING_RED_SECS` at a GREEN head holding (rc 75), saying why and posting nothing; null control: a numeric bound at the same GREEN head posts.
- nr-rev-window-off: SURVIVED -> KILLED. Pinned by reviewer #3402 dispatched 200000 s ago staying silent; null control: #3339 (6000 s) fires in the same pass.
- nr-rev-revt-off: SURVIVED -> KILLED. Pinned by reviewer #3403 returned as `probe/revt-<topic>-<n8>` staying silent; null control: #3339 with no return ref fires.
- nr-rev-lsremote-fail-continue: SURVIVED -> KILLED. Pinned by a pass whose return listing fails (a `git` shell function failing `ls-remote` on `probe/rev-*`) owing no reviewer; null control: the same dispatches fire in the unfailed pass.
- NULL: SURVIVED, as required.

The four arms add 6 checks (482 -> 488). Fixer steps re-opened: 2 (the four mutants above), 5 (`python3 tests/structure.py`, `prepr.sh` below); 3, 4 and 8 describe the same single-file diff and are unchanged.

Roster carries outside this part (part 2 builds only Carry 7, Carry 21, Carry 23 and Carry 30, the set it was dispatched with; the rest are not its findings and none is dropped here): Carry 0, Carry 1, Carry 2, Carry 3, Carry 4, Carry 5, Carry 6, Carry 8, Carry 9, Carry 10, Carry 11, Carry 12, Carry 13, Carry 14, Carry 15, Carry 16, Carry 17, Carry 18, Carry 19, Carry 20, Carry 22, Carry 24, Carry 25, Carry 26, Carry 27, Carry 28, Carry 29, Carry 31, Carry 32.

## Head

7d09eae1ba3ab2ab5a7ed2b84a087d6c5d6ef128, descending from 740e6074cf5bace0302c7f2896b72149c918f010 (the blocked head), cut from origin/main caacd43b4ee1b1ce849fbc92590e0b2191e6c02c, measured 2026-11-13 (`date -u`).

## Mutation proof

Failing test first: the new arms were run against the merge-base production text (the three production hunks reverted, tests kept): `bash tools/audit/seat/cloud_relay.sh --self-test` printed `cloud_relay self-test: 482 checks, 19 failed` (the 19 are every new or changed arm: Carries 21, 23, 30 and 7). At the head the same command prints `cloud_relay self-test: 482 checks, 0 failed`.

`python3 tools/audit/seat/mutant_run.py --spec <spec> --cmd 'bash tools/audit/seat/cloud_relay.sh --self-test' --copy-tree`, one mutant per new predicate and branch, printed:
SURVIVED NULL
KILLED skip-carry-call (Carry 21's named mutant)
KILLED red-die-restored (Carry 23's named mutant)
KILLED red-bound-off
KILLED red-no-record
KILLED wait-keeps-record
KILLED green-keeps-record
KILLED moved-head-always-refuses
KILLED probe-drops-disposed (Carry 30's named mutant)
KILLED noreturn-rev-age-off
KILLED noreturn-rev-ignores-return
KILLED noreturn-rev-ignores-move

## Null control

The unmodified tree at the merge base: `bash tools/audit/seat/cloud_relay.sh --self-test` printed `cloud_relay self-test: 452 checks, 0 failed`. Per carry, inside the self-test: same head + GREEN posts as today and never calls review_carry (21); WAIT holds as before (23); an undisposed `rev-` ref is relayed and a disposed ref whose tip moved is relayed at the new sha (30); the four returned reviewers (#3352, #3353, #3304, #3359), a moved head, a dispatch under 5400 s and a 6000 s fixer dispatch (under 7200 s) stay silent while #3339, #3350, #3297 and #3325 fire (7).

## Figures

- `bash tools/audit/seat/cloud_relay.sh --self-test` at merge base caacd43b4e: 452 checks, 0 failed; at the head: 488 checks, 0 failed (36 new arms, count of `ok` lines the command prints).
- `python3 tests/structure.py`: run at the head, see prepr below.

## Red checks

none

## Forward-carry

none

## Friction

none
