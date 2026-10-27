Fix review: merge eb97437efd6c273745352ee2cdb5c65c970c3c74

Seat: fix-review, local, round 1 for this PR. Measured at head
`eb97437efd6c273745352ee2cdb5c65c970c3c74` (re-read from the PR at
2026-10-27T01:24:42Z, unchanged), merge base `origin/main`
`6fe5170cd7ce01e60ffebfc93e598c216e628fa3`. Record-class batch: no production
or test code, so fixer.md step 1's mutation proof is correctly `n/a` and I
re-derived the body's null control instead. The comparison instruments below
are mine (fix-review step 9): I wrote the roster diff/scan scripts; the
tree's own `roster_sync.py --self-test`, `brief_lint.mjs`, `tests/structure.py`,
`tests/delivery_status.py` and `carry_audit.py` were run as the tree ships them.

RESULT verdict merge
RESULT head eb97437efd6c273745352ee2cdb5c65c970c3c74
RESULT merge-base 6fe5170cd7ce01e60ffebfc93e598c216e628fa3
RESULT three-dot-paths 7 (6 delivery rows, 1 roster)
RESULT merge-tree 0ad737408723b9ec3c974bc92a09788ca83c17c5 rc=0, no MERGE-CLAIM
RESULT blocking-findings 0
RESULT non-blocking-findings 3 (two carried to R10-ORCH-ROSTER-SCHEMA, one carried to R10-ORCH-ROSTER-SCHEMA)
RESULT checks-red-at-head 0

## 1. The checks the tree offers, at the head

Each run from a detached worktree at the head with the seat venv first on
`PATH` and `BASH_ENV` unset where the workflow unsets it.

```
$ env -u BASH_ENV python3 -I tools/audit/seat/roster_sync.py --self-test
roster_sync self-test: 55 checks, 0 failed

$ node tools/policy/brief_lint.mjs dev/programme/rosters/wave-r10-groups.json
== dev/programme/rosters/wave-r10-groups.json ==
  -- 0 error(s), 0 warning(s)
CARRY: 0 carry file(s) (dev/programme/carries/carry-<issue>.json)
TOTAL: 0 error(s) across 1 file(s)

$ python3 tests/structure.py
  ok   class_excess_loc 18079 <= 18079
  ... (25 metrics, all `ok`, every value at its recorded cap)
STRUCTURE RATCHET PASSED

$ python3 tests/delivery_status.py --check
DELIVERY STATUS OK — 204 rowed, 0 pending, 0 overdue (overdue at 12 commits)
  every merge in the window carries a row
```

The body's quoted self-test line reproduces exactly; its `brief_lint` line
reproduces exactly. `tests/structure.py` matches every budget in
`tests/structure_budgets.json` with no headroom spent -- and the diff touches
no budget file, so nothing moved on the instrument.

## 2. `wip-sync/` refs and the commits the roster records

All five refs the batch names exist on `origin`; so do the two older ones the
roster names elsewhere (`wip-sync/ext-wt-1e092393` for R10-RCA-FRICTION and
`wip-sync/ext-wt-e3556a49`, named in R10-BUFFER-STORE's `next_step`), and the
`ext-upd-fix-r10-ci-layout-p2-probe-{A,B1,B2}-*` family R10-CLOSEOUT-CLEANUP
names as a glob (three refs match). No row points at a ref that does not exist.

The recorded *commits* are a different matter. Measured 2026-10-27T01:02:41Z:

| group | `resume.commit` | ref tip then | relation |
|---|---|---|---|
| R10-HOUSE-GRADE | 516d47fd7 | bc9de92b1 | ancestor of the tip |
| R10-ORCH-REVIEW-PACKET | 9c35ddd23 | 0e32d89d8 | ancestor of the tip |
| R10-DIAG-AGES | 6ebc8aaca | 2eb746592 | **not on the ref** |
| R10-BUFFER-STORE | eb46ec47a | 2dc25b125 | **not on the ref** |
| R10-COP-PARTLOAD | 50ef300f7 | 3a4f599bb | **not on the ref** |

Each of the three is a rebased twin, not a lost patch: the recorded commit's
tree equals a commit still on the ref (`b5c9b6f61`, `da2fe10be`, `2c1d39074`),
the author date is unchanged and only the committer date moved. COP-PARTLOAD
was still an ancestor at 00:56Z and had fallen off by 01:02Z -- the refs are
force-moved by the wip-sync instrument, so the field decays while the batch
sits open. `origin` still serves each recorded SHA by direct fetch, so the
record is checkable, but `roster_sync.invalid_commits()` resolves by local
object and would print `RECORD-INVALID` for these three in a fresh clone.

Nothing in the tree reds on it: `roster_sync`'s CI arm is its self-test over
fixtures, `brief_lint` does not read commits, and the `resume.commit`
ancestry rule applies only to a `done` group. Finding F1 below, non-blocking.

## 3. Carry destinations are live

`tools/audit/carry_audit.py` reads the roster; run on the real body it prints:

```
NOTE body item 2f1d1b2d: R10-FLOW-WIP
NOTE body item 2f1d1b2d: R10-ORCH-REVIEW-PACKET
NOTE body item 2f1d1b2d: R10-ORCH-ROSTER-SCHEMA
NOTE body item f51846f0: R10-ORCH-ROSTER-SCHEMA
NOTE body item 82c86bc5: R10-ORCH-ROSTER-SCHEMA
CARRY-AUDIT: 3 finding item(s): 3 routed, 0 unrouted, 0 bad destination(s)
```

The null control is that the same command over an empty body prints
`CARRY-AUDIT: 0 finding item(s)` -- the first attempt of this review saved an
empty body (the `gh` call ran outside a repository) and produced exactly that
vacuous green, so the 3-item line above is the real measurement.

Independently: the body's three destinations are `R10-FLOW-WIP` (not-started),
`R10-ORCH-REVIEW-PACKET` (fixing), `R10-ORCH-ROSTER-SCHEMA` (not-started) --
all live, none `done`. The three are carried by the producing PR, #2867
(triage batch 35), whose body names `Carry: R10-FLOW-WIP`,
`Carry: R10-ORCH-REVIEW-PACKET` and `Carry: R10-ORCH-ROSTER-SCHEMA`; this
batch's `## Forward-carry` records the dependency accurately rather than
pretending they are already appended.

Across the roster, 26 carry strings are new, in 12 live host groups (none
`done`); no carry string was deleted (0 lost in any group); and every explicit
`Carry:` marker inside a new string names a live group.

## 4. The nine added groups and the 27 changed

Census re-derived from the two trees keyed by `group`: `groups 199 208`,
added 9, removed 0, `changed 27`, and the changed set with its moved keys
matches the body line for line (evidence/roster-census.txt). Every group has a
distinct name (208 entries, 208 names). No dangling `after` target, no
self-dependency, no cycle.

**No group's `brief` text changed** -- the 27 moved on `carry`, `resume`,
`files`, `after` and `issues` only -- so the "a changed brief dropped a
control" failure cannot arise here, and the field-level check confirms nothing
was dropped: 0 removals from any `after`, `issues` or `files` list against the
base. The one content change is R10-CEILING-PROBE's `files` widening 2 -> 7
(sysid, draw_range, coordinator, payload, button, sensor, pump_arbiter), which
is a widening only.

Two of the nine added groups carry `issues: []`: R10-PLAN-PRIO and
R10-RECORD-HOLD-APPROVE. `brief_lint` accepts it (57 of 208 groups at the head
have no issue, 55 of 199 at the base), and both briefs name their origin (the
owner's 2026-10-26 dispatch priority; triage P198). My brief's bar was "at
least one issue"; the tree's own rule is weaker, and I do not treat a deviation
from my brief as a defect in the tree. Finding F3, non-blocking.

All 15 issue numbers this batch wires or adds resolve in the tracker; 14 are
OPEN. The fifteenth is #2494, closed COMPLETED at 22:31:43Z -- finding F2.

## 5. Claims and budgets untouched

Three-dot diff (`git diff 6fe5170c...HEAD --name-status`) is exactly:

```
M dev/programme/delivery/2834.md
M dev/programme/delivery/2858.md
M dev/programme/delivery/2862.md
M dev/programme/delivery/2864.md
M dev/programme/delivery/2865.md
A dev/programme/delivery/2866.md
M dev/programme/rosters/wave-r10-groups.json
```

`tests/golden/claimed_drift.txt` and `tests/golden/card_claimed_drift.txt` are
byte-identical to the merge base (same blob), so `env_drift.py --all` has no
fixture to adjudicate and no claim to move. None of the seven `*_budgets.json`
files changed; `VERSION`, the component manifest and `RELEASE_NOTES.md` are
byte-identical to the base. The stamp owns those and nothing here touches them.

The six delivery rows: five flipped `open -> merged` and #2866's own row added
(`**open**`, correct -- the PR is open). Each of the five names a real merge
commit, checked against the API: #2834 `0137c4c` (0137c4cb0), #2858 `3b4180d`
(3b4180dcc), #2862 `149ce54` (149ce54a3), #2864 `6fe5170` (6fe5170cd), #2865
`bfc4a1e` (bfc4a1e29). All five are MERGED.

The head's own composition is as the body says: `HEAD^..HEAD` is one commit
touching only `dev/programme/delivery/2866.md`, and the authored tip
`1e9180dc9113b85354e5a03737f6dd4b9d4bb686` is an ancestor of the head, with
that row the only difference.

## 6. Merge simulation

```
$ git merge-tree --write-tree origin/main HEAD
0ad737408723b9ec3c974bc92a09788ca83c17c5
rc=0
```

No `MERGE-CLAIM` line: the claim files are untouched, so the driver is never
invoked and there is nothing for the orchestrator to resolve. The body's own
figure reproduces too: `git merge-tree --write-tree 6fe5170c 1e9180dc9` prints
tree `8a25ac669cfe5f9352e5e20d35ca3e73ab39b23e`, rc 0.

## Null control and re-derived figures

Roster blob hashes, `git show <rev>:<roster> | git hash-object --stdin`:
base `53414799bdd5549578172f1c101f0ecd4807aed4`, batch-22 head `b15f26339`
`0886357f4d90a6fe489b4212d1e5b8cc1db047b5`, head
`852ec7bdd3d719395863d021e4f0df17fb1b44f7` -- all three reproduce. Over the
authored range: 95 non-merge subjects, `^roster: wire` 6, `^roster: append-group`
6, `^roster: ` 60, `^roster_edit` 27, `^roster_sync` 6, `^record: ` 2 -- all
reproduce. The eight `carries forward item N of batch 23` commits exist as
exactly eight, each adding one carry to the group its subject names.

The repaired stage value reproduces: at the previous head `6f42fc12b` the
roster reads `"stage": "done --at-sha bfc4a1e297fb2899be1c4643ae9d75b8a5829208"`
at line 8207; at the head it is `"stage": "done"` with
`"commit": "bfc4a1e297fb2899be1c4643ae9d75b8a5829208"`. The previous head's
check-runs (55 runs) concluded red on exactly three -- `gate`,
`governance / instrument-self-tests`, `pr-contract / pr-contract` -- which is
the set the body's `## Red checks` names and answers; at the head every
concluded run is success or skipped, `governance / instrument-self-tests`
included.

A restricted version of the body's flag-text scan -- `resume.stage`,
`resume.branch`, `resume.commit`, `resume.pr`, and every `files`, `after`,
`issues` value, over all 12 roster and carry files -- finds 0 hits in 3013
values at the head.

`tests / mutation` is green at the head, but the diff writes no production
line, so the lane drew no mutant; that green is vacuous by construction and I
do not count it as evidence of anything.

## Findings

### `## Friction`

- roster-wip-sync-commit-decays: stale: three of the five `fixing` groups
  record a `resume.commit` that is no longer on the `wip-sync/` ref their
  `resume.branch` names (R10-DIAG-AGES `6ebc8aac`, R10-BUFFER-STORE `eb46ec47a`,
  R10-COP-PARTLOAD `50ef300f7` at 01:02:41Z; COP-PARTLOAD was an ancestor at
  00:56Z). Each is a rebased twin whose tree equals a commit still on the ref,
  and `origin` still serves each SHA by direct fetch, so nothing is lost -- but
  the record is a snapshot of a ref the instrument force-moves, and
  `roster_sync.invalid_commits()` resolves by local object, so a fresh clone
  prints `RECORD-INVALID` for all three. The reconciler derives `resume.stage`
  and not this field; deriving it, or recording the ref-relative fact rather
  than a SHA, is the countermeasure. Carry: R10-ORCH-ROSTER-SCHEMA
- roster-issue-closed-as-done: stale: R10-MERGE-SUBJECT-CASEARM lists #2494,
  closed COMPLETED at 2026-10-26T22:31:43Z (its closure cites `09b1d002c`, an
  ancestor of `origin/main`), while the wire commit `f4ff4cc13` predates the
  closure at 20:27:16Z. The group's other issue #2803 is open, so its
  destination is still live and the group is not finished; the stale entry is
  the closed one. Nothing reads issue state: `brief_lint`, `roster_sync` and
  `delivery_status` all pass. Carry: R10-ORCH-ROSTER-SCHEMA
- added-group-without-issue: permitted: R10-PLAN-PRIO and
  R10-RECORD-HOLD-APPROVE carry `issues: []`. `brief_lint` accepts it and 57 of
  208 groups at the head are the same shape, and each brief names its origin
  (the owner's 2026-10-26 dispatch priority; triage P198); recorded because my
  brief asked for at least one issue per added group and these two do not meet
  that bar. Carry: R10-ORCH-ROSTER-SCHEMA

## What a fixer must repair before this head can merge

Nothing. The three findings are record-quality staleness caused by events that
landed after the branch's last reconciler pass (22:43:52Z): fixer rebases at
22:48:42Z and 22:50:56Z, and a triage closure at 22:31:43Z. All three carry to
R10-ORCH-ROSTER-SCHEMA, which is live and not-started, and a re-sync before
merge would clear the first two.
