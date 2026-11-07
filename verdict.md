Fix review: blocked 520538ccfad01bee373382e9d56fc036c8c87ea0 settle-unjudged: a higher-id gate that deferred to a lagging lower run whose green gate does not cover the newest event is never re-run

bus-nonce: 2e16118cc29e36b0964fe90175304e15

Round 1 (first-round adversarial review), head 520538ccfad01bee373382e9d56fc036c8c87ea0, merge base b4ec2f332fe3ab8dcf169bd3066276d3bb8848ab.

## Block

Brief focus (2) and (4). `undecided()` re-runs a red gate in two cases. The first is when another run's non-gate job finished after the gate started, using real timestamps. The second is when a HIGHER-id run's gate started while it judged, and then only the lower id is re-run. But `busy()`'s tie-break, in the gate self-test check "busy-defer: the higher deferring edit gate defers at once to the lower whose listing lags", makes the HIGHER run defer to the LOWER one. Neither arm catches that red. It is only re-run when the lower's green gate covers the newest event, through the green branch. If the higher run was created after the lower's gate started (for example, a body edit landing during the lower gate), `covers_newest` is false and the sweep goes to `settle`. There the lower's sources finished before the higher gate started, and the lower id is not higher. So no sweep re-runs the higher's red deferral. It stays red at a head where a later green gate exists, until a human re-runs it. At the base the same gate waited one poll and judged PASS (the removed check "the higher deferring edit gate waits on the lower whose listing lags, then judges, never a red deferral"), so this is a regression the change introduces.

Reproduction (the reviewer's own instrument, disclosed; ev/probe_settle.py over sweep_selftest's World): lower run 1 created 10, units done 40, gate 50-60 green; higher run 2 created 52, gate 55-56 red (the deferral). Swept from run 1: `posts=[] SWEEP-DONE run=1 reruns=0`; swept from run 2: `posts=[] SWEEP-DONE run=2 reruns=0`. Null control: the same with run 2 created at 45, before the lower gate started, so the green branch applies: `posts=['repos/o/r/actions/jobs/20/rerun']`.

To repair it, settle needs to catch the higher side of a lagging pair, or any red gate whose run overlapped another run's gate start in either order, without reintroducing a loop. The fixer and design own the shape. A gate or sweep self-test case for this ordering should fail first.

## Findings

- settle leaves the higher-id deferral to a lagging lower green gate unjudged when that green gate does not cover the newest event (the Block above); repair in this PR. Carry: R10-HOTFIX-GATE-BUSY-DEFER

## Evidence

- RESULT replay at head: `RESULT replay wait_s=0 first=FAIL swept=yes final=PASS`; at base (git archive b4ec2f33 tools/ci tools/pr): `RESULT replay wait_s=720 first=FAIL swept=yes final=PASS` (ev/replay_head.txt, ev/replay_base.txt). The #3282 replay matches the body. Note that the base also ends PASS by the sweep: the base defect the replay reproduces is the 720 s held runner, not a missing re-judge, which agrees with the body's own account of the brief's cause.
- Race harness r10_gate_defer_race.py, head against base: the four fixture rows read wait 0 s at head and 720 s at base for 42367457809 and 42338396358; 42307493684 and 42307798573 read PASS at both ends (ev/race_head.txt, ev/race_base.txt).
- Self-tests at head: gate 77 checks, 0 failed; sweep 33 checks, 0 failed (ev/selftests_head.txt). These match the body.
- Reviewer mutants (ev/mutants.txt): overlap arm removed: sweep 2 failed (matches the body's M4). Late-source arm removed: sweep 3 failed (matches M3). A null mutant (comment line only): 33 checks, 0 failed. A judge-wait mutant did not finish in ~4 min; it was stopped and is not counted. The body's M1 covers that line.
- `git merge-tree --write-tree origin/main HEAD`: rc 0, tree a63dd482, no conflict.
- Roles drift `git diff merge-base...origin/main -- dev/governance/roles/`: empty.
- Diff paths: VERSION, the manifest, RELEASE_NOTES.md and every *_budgets.json are untouched. dev/programme/delivery/3287.md is in the diff. The new harness is classified INERT in tests/closures.json; the fixture lies under tools/ci (MODE FULL, per the body).
- The `## Head` section names 520538cc, the head reviewed.
- CI: `merge_train.py classify` read WAIT (`pending: gate red: none`) on every poll from 15:25Z to 15:28Z. Every check run at the head was queued or skipped (7 check runs, none concluded red). The verdict is returned before CI concluded because the block is a code defect independent of CI, and returning it now keeps the hotfix's critical path moving. The CI state is not judged.
- Not re-derived: the census figures (live API, sliding window) and the race harness table's per-scenario gate-wait seconds beyond the fixture rows above.
