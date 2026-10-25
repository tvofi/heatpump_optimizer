Fix review: merge b6df9b2b91bc45b7a2d405716312546f2d4d47d1

bus-nonce: ee2af5889089c385943c97f9d0468184

Round 2, a delta review of the re-cut. Reviewed against `dev/governance/roles/proposal-triage.md` and `fix-review.md` at origin/main `f3ffb1c63`. No role contract changed between the merge base `c9cbe6b45` and origin/main (`ev/contracts_drift.txt`).

## Block findings of round 1: did the re-cut close them?

1. **`Instances:` missing: closed.** Every ruling now carries an `Instances:` line: `grep -c '^Instances:'` gives 8, at `s6-batch31.md` lines 16, 23, 30, 37, 49, 56, 63 and 74 (`ev/fields.txt`). The P177 instance command re-derives: `git grep -l hypothesis -- 'tests/*.py'` prints nothing at `dfcd8d9be`, at origin/main and at the head (`ev/facts.txt`). P181 and P183 say "none measured" and cite nothing. That matches the `s6-batch30.md` precedent the round-1 verdict accepted, because no instance was counted, so there is no figure to cite.
2. **ACCEPT on an unmeasured benefit: closed.** All eight rulings are now `Verdict: DEFER`, and none is ACCEPT. Each DEFER names the measurement that would change its answer, which is what the contract requires ("DEFER names what would change the answer, or the group already owning the item"). Examples are line 13 for P176, the P177 line "the count of round-10 optimizer defects that a stated property ... would have caught", and the P183 line "post-release defects and time-to-detect per stamp". Each cites the re-cut: "(Round-1 re-cut, verdict 6402374814 ...)". The id is the round-1 verdict's PR comment `issuecomment-6402374814`, posted by `hpo-approver[bot]`.
3. **P176 names no owner: closed.** Line 13 reads "Verdict: DEFER -> D11 (governance mechanisms) owns the measurement in round 11". The carry whose item (1) lacked an owner is dropped from the file, with "P183's carry is dropped" at line 5.

The route the owner chose is sound. Line 5 says the owner's acceptance reaches R10-ROUND-PLAYBOOK as an owner-sourced carry rather than through a triage ACCEPT. That carry already exists on `handoff/audit-r10-roster` at `2b7fe35c6`: carry 6 of R10-ROUND-PLAYBOOK reads "Triage batches 27-31 re-ruled the ones it could not measure in round 10 as DEFER ... in triage PRs #2827-#2831. Round-11 planning takes each deferred item as owner-accepted" (`ev/playbook_carry.txt`). So no deferred item is left unpropagated.

## Rulings re-checked

- **Verdict and destination.** All 8 are DEFER, each to a dimension brief that exists: D0, D2, D3, D7, D10, D11, D13 and D14 are all present under `dev/governance/dimensions/`. A dimension is never done or absorbed. The contract lets a DEFER name what would change the answer instead of a group, and each one does.
- **Source.** Each cites the s6 `proposals.md` `## V9x/V10x` entry with its owner tag. The file is out of tree. Carry 6 above records the owner's acceptance of V63-V103 in the tree.
- **Instances.** See block finding 1. These facts re-derive at the head:
  - P176: `fix-review.md` holds the five block classes at lines 12, 28, 46, 88 and 134, unchanged at origin/main.
  - P178: `tests/optimality.py:3` reads "Not an optimality proof", and `:8` is the BLAS-noise headroom.
  - P179: `tests/mutation_budgets.json` has a single `max_survivor_fraction` with no per-module key, and `tests/mutation_ledger/` exists.
  - P180: all three HA instruments exist.
  - P182: `tests/typing_ruler.py:12-14` covers errors, by_code, and type_ignores "a separate hard metric at 0".
  - P183: `defect-root-cause.md:18` is the "reached a released version" trigger, and `tools/release/stamp.py` exists.
  
  All of this is in `ev/facts.txt`.
- **Cost and Binding.** Present on all 8. Each Binding states the round-10 constraint ("Closure saving: 0 h in round 10"), which is consistent with DEFER.
- **Roster.** R10-ROUND-PLAYBOOK and R10-ORCH-REVIEW-PACKET (P176 cites the latter's carry 0 on zero headroom) are both at stage not-started on origin/main and on the roster branch. Neither is done or absorbed (`ev/roster.txt`). The carry 0 text cites `fix-review.md` "at zero headroom".
- **Re-cuts and duplicates.** The batch re-cuts its own round-1 rulings and cites the verdict on every entry. No ruling duplicates another, and none duplicates an existing group (the round-1 keyword search stands, and the delta adds no new subject).

Rulings I would change: none.

## Findings

- Line 7 still reads "A roster op citing an ACCEPT below resolves only once this file is on the roster branch or origin/main". After the re-cut the file holds no ACCEPT, so the sentence is stale boilerplate. It misleads no tool: `roster_edit.ruling_verdict` returns DEFER for every pid. Carry: dismissed: an inert sentence in a ruling record, and a third round to delete it costs more than it buys.

## Evidence

- RESULT head reviewed: `b6df9b2b91bc45b7a2d405716312546f2d4d47d1` (`ev/HEAD.txt`). This is the PR head the API reports. The PR author is `hpo-author[bot]`.
- RESULT scope: the three-dot diff against the merge base `c9cbe6b45` is `dev/programme/delivery/2831.md` (+1) and `dev/programme/triage/s6-batch31.md` (+77) only (`ev/merge.txt`). The re-cut commit touches only the batch file (`ev/recut.diff`).
- RESULT merge: `git merge-tree --write-tree origin/main <head>` exits 0 with tree `746ec7ec5`, so there is no conflict (`ev/merge.txt`).
- RESULT host paths: a grep for `/home|/Users|/tmp|~/` matches nothing in the batch file or the delivery row.
- RESULT body figures:
  - `grep -oE '^Verdict: (ACCEPT|DEFER|REJECT)' | sort | uniq -c` gives 8 DEFER, matching the body.
  - `grep -c '^Instances:'` gives 8, matching the body.
  - The body's per-ruling destinations match the file's lines.
- RESULT null control re-run: `roster_edit.ruling_verdict(text, pid)` gives DEFER for P176-P183 and None for P184, as the body states (`ev/ruling_verdict.txt`).
- RESULT mutation proof: n/a, because the PR changes no code or check. It is a ruling record, and its consumer reads all eight as DEFER.
- CI on the head (`ev/ci.txt`): no required check is red.
  - `governance / delivery-status` failed. Its log names six overdue rows from other PRs, none of them #2831, and states it is NOT a required context and blocks no merge. So the red-check trigger does not apply to this PR.
  - `tests / fast (3.14)`, `typing`, `env-matrix`, `instrument-self-tests`, `coverage-ratchet` and `graders-head-copy` were still running at read time.
  - Every other concluded check passed or was skipped.
