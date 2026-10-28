Fix review: merge 45ce3c6e9aa00bab7c57bb1d7ab3bd72f951c52d
bus-nonce: b72b9048d0eaf0f7fbe052b1fc535e4d

# Fix review -- PR #2899, roster: round-10 batch (R10-RCA-FRICTION-RESIDUE fixes wires, immersion-latch re-pin)

Round 2. Round 1 blocked `345daba44` with carry-missing for P200 and P203. Reviewed head:
45ce3c6e9aa00bab7c57bb1d7ab3bd72f951c52d, in a detached worktree at that head, against origin/main
b9e286254. `dev/governance/roles/` has no diff between the merge base and origin/main. The head is
the roster tip `08c0818cd` merged with main twice; `08c0818cd` is an ancestor of the head.

## Results

- The round-1 blocker is answered. Both carries are now on their live destinations, verbatim
  (`ev/carry-routing.txt`):
  - P200 is on `R10-REVIEW-CARRY` (stage `fixing`, files `fix-review.md`, `orchestrator.md` and
    `tools/audit/seat/`). The group goes from 3 carries on origin/main to 4.
  - P203 is on `R10-FLOW-TOOLKIT-MODEL` (stage `not-started`, files `roster_lib.py`,
    `roster_edit.py`, `replan.py` and `INSTRUMENTS.md`). The group goes from 10 carries on
    origin/main to 13.
  - Each new entry is byte-identical to its source entry, `R10-ORCH-REVIEW-PACKET`'s P200 and
    `R10-ORCH-ROSTER-SCHEMA`'s P203, except for the trailing `Carry: <GROUP>` marker. That marker
    is renamed to the new owner, and `strip-marker equal: True` holds for both. The lengths are
    1986 and 2366 characters, as the body says.
  - P200's binding precondition, that the carry pays the cap by deletion or else goes in the brief
    template, travels whole. So do P203's controls: the covered fixture, the owner row, two mutants
    and a null.
- `node tools/policy/brief_lint.mjs dev/programme/rosters/wave-r10-groups.json` prints
  `TOTAL: 0 error(s) across 1 file(s)`, rc 0 (`ev/brief_lint.txt`).
- `carry_audit` at the head (`ev/packet.md`) reports 3 finding items: 3 routed, 0 unrouted and 0 bad
  destinations, to `R10-REVIEW-CARRY`, `R10-FLOW-TOOLKIT-MODEL` and `R10-FLOW-WIP`.
- Groups: origin/main against the head gives `212 212 0 0 18`, and the 18 differing groups are the
  ones the body names (`ev/groups.txt`). `R10-RCA-FRICTION-RESIDUE` `fixes` is
  `[2410, 2593, 2597, 2660, 2784]`.
- `git merge-tree --write-tree origin/main <head>` exits 0 (`ev/merge-tree.txt`). The diff touches
  only the roster JSON (+48/-28) and `delivery/2899.md`.
- Checks (`ev/check-runs.txt`): the head's first `gate` (122595114873) concluded failure on
  `FAIL run(s) [40620831978, 40620903158] at this head are still being judged; their gate decides`
  (`ev/gate-122595114873.log`). That is a deferral to this head's own later runs, not a defect, and
  the final state is recorded in the check-state section below. `VERSION`, the manifest and the
  notes heading are untouched.

## Findings

- F1 (non-blocking): the body says the code head `08c0818cd` is "the tip of
  `handoff/audit-r10-roster`". The roster branch has since moved to `e3bc6128e`, which descends from
  it. The five commits after it (set-stage TRAIN-OVERLAP-GRADE, append-carry FLY-WORKTREE-GC,
  append-group TRIAGE-S6 and two roster_sync derivations) belong to the next roster batch, not this
  PR. Carry: dismissed: snapshot wording; the next roster batch carries them
- F2 (verified, non-blocking): P199 stays on `R10-FLOW-WIP`, as round 1 found.
  Carry: dismissed: verified in the tree at this head

## Check state at this head

Final read, at about 02:53Z (`ev/check-runs.txt`): 68 runs, 43 success, 25 skipped, 0 failure and 0
pending. The later `gate` runs (122600804997, 122601470505 and 122601678298) concluded success. They
supersede the deferring gate 122595114873. Two `pr-contract` runs that started after it, at
02:45:42Z and 02:47:52Z, concluded success. No red is owed an answer.
