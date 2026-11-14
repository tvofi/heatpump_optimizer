Root-cause analysis for the weekend red of `tests / fast (3.14)`. A check that
#3444 added (`b6696bd6e6`) lets one arm of its sequence read the runner's real
calendar day and asserts the weekday day type for that arm. So the check is red
on every Saturday and Sunday, on main and on every head. This pull request adds
only the record: `dev/audit/rca/R10-RCA-FEATURES-WEEKEND-CLOCK.md` and its
`_rca` entry in `dev/audit/config/bugclasses.json`. The test fix is
R10-HOTFIX-FEATURES-WEEKEND-CLOCK's. The countermeasure is specified for a
fixer and carried to R10-SUITE-ENV-RESIDUE; it is not built here.

- Process state: (c). R10-SUITE-HOST-DETERMINISM's nightly step changes the
  zone and never the calendar day.
- Class: a suite verdict that follows a host property the gate does not pin.
  It has three instances in round 10 (CPU load, zone, calendar day), so it owes
  a class barrier.
- Cost test: the recommended countermeasure runs the existing nightly Kolkata
  step under `faketime` on the other day type, for about 10 to 20 s a night (an
  estimate). The defect
  costs up to 13.7 runner-hours and stalls 8 gating PRs for up to 48 h, about
  once a round.

## Head

e9974b7b0ba125fb7d7815d469b72e31f1a90214

## Mutation proof

n/a: this change is a record and no code changed. The countermeasure's
detection is demonstrated in the document, section 1: a scratch probe shifts
the hastub live clock onto a chosen day. At `fdb526895c`, the
`_chg_seq` block is red on Saturday and Sunday and green on Wednesday. With
the default arm pinned to a weekday (a local stand-in edit, discarded), the
block is green on Mon, Wed, Fri, Sat and Sun.

## Null control

At `fdb526895c` with the clock shifted onto Wednesday, the block reads
`ALL 3 FEATURES BLOCK PASSED`. The full `tests/features.py` run is shifted to Sunday and to Wednesday by
the same wrapper. The two FAIL lists differ only by this check (section 3).

## Figures

none

## Red checks

none

## Forward-carry

- The nightly Asia/Kolkata step runs under `faketime` on the other day type
  from the real day, with a weekday guard. The demonstration is in section 5
  item 4 of `dev/audit/rca/R10-RCA-FEATURES-WEEKEND-CLOCK.md`. A stub-only
  clock shift is refused, measured: 14 collateral failures. Carry: R11-INTAKE-R10-RESIDUE

## Friction

none
