A pull request's own row, `dev/programme/delivery/<N>.md`, is the orchestrator's
and lands before the review (`delivery-status-tracking.md`; `handoff_push.sh`
writes it at open). When it lands *after* the merge verdict, the row commit
moves the head off the one the reviewer measured, and `app_approve.sh --carry`
refuses a commit of the branch's own, so the only recovery is a fresh review --
a whole reviewer round for a one-line record file. This is class E of
`dev/audit/rca/R9-RCA-1990.md`, which refused the other candidate, widening
`--carry` to accept a row-only commit, as widening a governance instrument's
acceptance at about 2 in 57 merges. This change removes the cause instead:
`tools/audit/seat/bus.sh dispatch` now refuses a head whose tree carries no
`dev/programme/delivery/<pr>.md`. A verdict posts only against a dispatch's
nonce (`push-verdict`, `dispatched_to`), so dispatch is the single chokepoint,
and gating it keeps the row from landing late.

## Head

`8961643da111cc7612e1f2c097321171075fdc43`

## Mutation proof

Forcing the row predicate true (`git cat-file -e "$h:$row"` -> `true`) turns the
new self-test arm red; restoring it turns it green:

    $ bash tools/audit/seat/bus.sh --self-test   # row predicate forced true
      FAIL dispatch refuses a head with no delivery row (the ordering, #1990 class E)
    bus self-test: 47 checks, 1 failed
    $ bash tools/audit/seat/bus.sh --self-test   # restored
    bus self-test: 47 checks, 0 failed

The arm was written first and fails on the pre-fix tree for the same reason
(`47 checks, 1 failed`, the same line), so it pins the defect it names.

## Null control

The unmodified tree dispatches the rowless head. At `origin/main` (a detached
worktree) `bus.sh` reads `45 checks, 0 failed` -- no arm -- and accepts the very
head this gate refuses:

    $ (cd WT@origin/main && HPO_BUS_STATE=$(mktemp -d) \
        bash tools/audit/seat/bus.sh dispatch 2075 addd6f45758ff90ab862bcbe62357c1373ed7786 cmsg)
    bus-nonce: 02d1e60dbd8ecc4cb6485a0478d53572   (rc 0)
    $ bash tools/audit/seat/bus.sh dispatch 2075 addd6f45758ff90ab862bcbe62357c1373ed7786 cmsg
    bus: REFUSE: dispatch: #2075's head addd6f45758ff90ab862bcbe62357c1373ed7786 carries no dev/programme/delivery/2075.md; the row lands before the review (delivery-status-tracking.md) -- write it and re-push, then dispatch   (rc 1)

## Figures

- The row's position against the merge verdict, newest 60 pull requests:
  `python3 tools/audit/seat/row_position.py --limit 60` -- 41
  `row-before-verdict`, 17 `no-merge-verdict`, 1 `row-AFTER-verdict` (#2075,
  open), 1 `no-row-in-head`.
- The gate and its null control on the real head, #2075:
  `bash tools/audit/seat/bus.sh dispatch 2075 <sha> cmsg` (above).
- The self-test count: `bash tools/audit/seat/bus.sh --self-test` (45 -> 47).

## Red checks

none on this branch. A local `python3 tests/harness_headers.py` run is red for an
unchanged round-4 harness, `dev/audit/rounds/round4/D6/claims.py`, whose
nested-quote f-string needs Python 3.12 and my local interpreter is 3.11; CI's
3.12/3.14 runners grade it green, and this diff does not touch the file.

## Forward-carry

The ordering is stated in `tools/audit/seat/bus.sh`'s header, where the
orchestrator running `dispatch` reads it. It is not added to
`dev/governance/rules/delivery-status-tracking.md`: that file is policy and
code-owned, so the line is the owner's to approve.

## Friction

delivery-status-tracking: unenforced: the row must land before the review, but
nothing refused a head without one; a row added after the verdict moves the head
off the measured one and costs a re-review (R9-RCA-1990 class E; #2075 open,
#2072 a row-only extra round).
