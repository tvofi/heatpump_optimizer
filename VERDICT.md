Fix review: blocked 6e12aeb5bd976a7520361dd05bf9300cb6c77a04 harness: class-open relay_owed keys the probe-ref, handoff-update, approve-held-runs and dispatch OWED rows on the kind token as well, and the record names only handoff-no-pr and carries no class search (root-cause.md 1 and 3)

Round 1 of R10-RCA-HANDOFF-SLIP (#2545). Measured head `6e12aeb5bd976a7520361dd05bf9300cb6c77a04` (still the PR head when this was written). origin/main `57f0c9c77`, roster `handoff/audit-r10-roster` `23ef06dc6`. The contract is current: `dev/governance/roles/` changed since the merge base only in `orchestrator.md`, not `fix-review.md`. Evidence is in `ev/`. I built the replay harness `ev/replay.py` myself. It calls the production `relay_owed`, unmodified, over a hand-written log. The finding has no committed harness.

## Blocking

- **The named cause stops at one kind, and the class search root-cause.md §1 and §3 require is absent.** `relay_owed` keys every OWED row on `f[2]` (`orchestrator_tick.py` 703-706). The record says so for `handoff-no-pr`, but the relay writes five OWED kinds the same way (`cloud_relay.sh` 157, 211, 215, 218/223, 231): `probe-ref`, `handoff-update`, `approve-held-runs`, `dispatch` and `handoff-no-pr`. Replaying through the production method (`ev/relay_owed_class_reach.txt`): a log of 8 rows prints 6 OWED lines. `probe-ref` replays as history the way `handoff-no-pr` does, and the one-shot `handoff-update 2600` and `dispatch 2601` lines stay OWED after `POSTED 2600` and `POSTED 2601`. So the "No POSTED can ever clear" cause reaches the event kinds too, not only levels. Null control: the PR-keyed `owed()` grammar (`OWED <utc> <pr> ...`) is cleared by its POSTED and prints 0. A re-cut owes three things: a cause that names every kind the keying reaches (or one rule that enumerates them), the search stated, and §5 scoped to match. §5.1 extends only `handoff-no-pr`. Carry: R10-RCA-HANDOFF-SLIP
- **The cost test misstates where its defect cost comes from.** §4 says "5.13 seat-hours is measured, not estimated — the R9 RCA … records" it. The R9 RCA says the opposite: "the measurement is the launching seat's session record, **not independently verified by me**" (line 383), and in §7 "I verified the arithmetic … and nothing else" (`ev/cost_provenance.txt`). Under fix-review step 8, a figure no seat could re-derive cannot be quoted as measured. The inequality survives because 1.65-2.4 h is under 5.13 h, and for an audit class the barrier is owed whatever the test says. The provenance still has to be restated, so that a later seat does not read 5.13 h as verified. Carry: R10-RCA-HANDOFF-SLIP
- **Two of the body's carries now point at a finished group.** `R10-ROSTER-OPS` is `done` on the roster at `23ef06dc6` (#2513, merged 15:20Z, roster-edit ops only). The §3(d) brief-pin countermeasure and the `finding-propagation.md` friction item sit in its carry list, which nothing dispatches any more. `carry_audit.py --roster-ref origin/handoff/audit-r10-roster check` over the body now reports 2 bad destinations, both `R10-ROSTER-OPS is done`, rc=1 (`ev/body_carry.txt`). The same body routes 5 of 5 at rc=0 under main's roster, which now carries the round-10 groups. So the body's `## Red checks` premise ("stays red … until those groups are on main's roster") is overtaken, and a pr-contract re-run after the next roster sync refuses for the `R10-ROSTER-OPS` destination instead. These two need a live owner. Carry: R10-RCA-HANDOFF-SLIP

## Non-blocking observations

- The `Ledger extension owed` paragraph in `R10-ORCH-MACHINERY`'s brief carries the claims but not their controls. The content-covered close has no positive or null case named: `ecaf178c`, `git cherry` prints `-`, against a re-applied-but-edited hunk. The exit-code half of §5.6 (rc 1 with ORPHAN rows is a finding, never unavailability) appears only as "never a silent finding", without the 143-pass shape as its red case. `finding-propagation.md`: carry the control, not only the claim. Carry: R10-ORCH-MACHINERY
- Main's `orchestrator.md` §5, changed after this branch's merge base, now says the soft cap never refuses opening an owed handoff (tvofi, 2026-10-20). That is a landed countermeasure to the §3 cap-delay mechanism, and the re-cut record should cite it. Carry: R10-RCA-HANDOFF-SLIP
- The register reader does not refuse an `_rca` entry that its class no longer cites, and does not check `status` values. Planting each of those still prints `0 violation(s)`, while a dropped entry or a dangling `in_tree_home` is refused (`ev/register_plants.txt`). Both gaps fail safe for this PR. Carry: dismissed: fail-safe direction, no wrong record results

## What was verified

- Merge: `git merge-tree --write-tree origin/main 6e12aeb5` exits 0 (`47338ad17`). No claim-file conflict, and the diff touches no golden or claim file.
- `VERSION`, the manifest and the notes heading are untouched (the pr-contract log at this head: "no version edit").
- Mutation proof: n/a as the body says, because there is no production line. Plants on the register in `ev/register_plants.txt`: a dropped `_rca` entry gives `UNKNOWN-RCA`, and a dangling `in_tree_home` gives `DANGLING`, so the register does read the new entry.
- Re-derived figures (`ev/figures.txt`):
  - rca entries 113 at the base and 114 at the head, with 0 violations at both
  - median 45.9, 2.4 h, 1.65 h, 1327, 0.81 GB/day
  - per_round `{'R9': 7}`
  - `git cherry` `-` for `ecaf178c`, with `+` for the null
  - the PR-at-`fix/` answers: #2555, #2561, #2521, #2513, #2545; `[]` for earlycutoff
  - MODE: SCOPED -- 0 script(s) run
- Could not re-derive: the body's `bus.sh orphans` set at `289426c1f`. The refs moved and the earlycutoff handoff refs are deleted. At `57f0c9c` it prints `1 stranded`, `r10-pusher-reap` (`ev/bus_orphans_now.txt`). The §2 and §4 host-log figures (31,303, 143 passes, 198 passes) cannot be read from here, as the body states.
- Red checks at this head (`ev/check_runs.tsv`):
  - `pr-contract`: runs 119236489332 and 119243225219. The later one started after every other run had concluded, and is red only on the carry_audit BAD-DEST step for `R10-ORCH-MACHINERY` and `R10-TICK-OWED-LEVEL`. The body answers it.
  - `nightly-status`: main's, and answered.

## Routing

Each observation above, by id (carry_audit item ids at this text):

Carry: R10-RCA-HANDOFF-SLIP (item c0901458)

Carry: R10-RCA-HANDOFF-SLIP (item fd9e0e70)

Carry: R10-RCA-HANDOFF-SLIP (item d303bfa2)

Carry: R10-ORCH-MACHINERY (item 3985dac8)

Carry: R10-RCA-HANDOFF-SLIP (item dc368e8c)

Carry: dismissed: fail-safe direction, no wrong record results (item 98f76f3a)

RESULT register rca_entries base=113 head=114 violations=0/0
RESULT class_reach kinds_keyed_on_kind_token=5 named_by_record=1 replay_lines=6 null_lines=0
RESULT carry body_under_roster_branch bad_dest=2 (R10-ROSTER-OPS done)
RESULT merge_tree rc=0
RESULT gate MODE=SCOPED scripts=0

bus-nonce: 496da28b706aecb02848b0e88481f32f
