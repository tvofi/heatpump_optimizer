Fix review: blocked ce6f6511e693a6c175282796281c304e22cfb52a class-open: tools/ci/sweep.py:115 re-judges only lower-id runs, so the residual red M1 now puts on the higher-id code run is never swept

bus-nonce: 2e06f9974a910557c6790730937b4997

Review round 1 (no earlier verdict ref for #2770). Measured head `ce6f6511e693a6c175282796281c304e22cfb52a`, which was still `fix/r10-gate-defer`'s head when this was written. The merge base with origin/main is `c176ee55d`. The fixer's base is `343fb2a2c`. `git diff c176ee55d...origin/main -- dev/governance/roles/` is empty, so the contract read is current.

## Block

The body's residual says: "Past the bound, the gate still FAILs deferring and `gate-sweep.yml` re-judges it." That is false in the shape this PR's own M1 creates. `sweep.py` acts for a run V whose gate is green. It then re-runs red gates only of runs with `r["id"] < v["id"]` (`tools/ci/sweep.py:115`, ev/id_order_enumeration.txt). With M1, a non-code run's prelude waits for the code run even when the code run has the higher id. The gate that waits, and can expire, is therefore the higher-id code run's gate, and the decider is the lower-id edit run. The decider's sweep never reaches the expired gate. The code run's own sweep skips, because its gate is red (`covers_newest`). The red stays, and that is the defect class this PR exists to remove.

Measured with the finder-shape harness, through a scratch copy that parameterises only the edit run's body-unit span. The copy also adds an edit+code pair with no review run, which is #2754 minus the review. The diff against the committed harness is ev/race_editcode_scratch.diff, and this instrument is mine, not the finder's:

- Head, edit span 518 / 640 / 700 s: the code gate waits 540 / 660 / 720 s and PASSes.
- Head, edit span 760 / 900 s: `run 40119473870 (waited 720 s): FAIL run(s) [40119473491] ... still being judged`, then `run 40119473491: PASS`. That is UNDECIDED-RED 1, held by the higher id, with only a lower-id PASS that could sweep it.
- Base (`c176ee55d`), the same shape: the red sits on the lower id 491 and the PASS on 870. `sweep.py` from 870 reaches 491, so the base recovers where the head strands (ev/editcode_no_review.txt).
- With the review run present (#2754's real shape), the edit span sweep in ev/edit_span_sweep.txt shows the code gate expiring red from 640 s. The review run 40119483652 has the highest id and PASSes, so sweep from it does reach 870. The stranding needs the highest-id decider to be lower than the expired gate's run.

This is class-open under fix-review.md step 6. The body states the class itself ("GitHub numbers a same-second push and body edit out of order"; prelude.py's docstring: "an id alone orders nothing"). It fixes one id-order seam, `prelude.waits_on`, and names no enumeration rule. My rule was `grep '\["id"\] *[<>]' tools/ci/*.py tools/pr/*.py`. It returns three seams:

- `prelude.py:193`: in the diff.
- `ruleset_cutover.py:368`: the newest check run per (name, suite), a per-suite attempt order and not a cross-run order, so it is not this class.
- `sweep.py:115`: neither in the diff nor dispositioned in the body, and the body's residual relies on it.

How reachable it is: the edit body-unit spans I read from first attempts (ev/edit_body_spans.txt, edit runs on 2026-10-24) run from a median of 233 s up to 710 s. The 699 and 710 s spans hold a 578–580 s `pr-contract` that is codescan waiting, which M1 removes. So the 760 s threshold needs a runner-queue stall of several minutes. It is a tail, but it is the tail the body says is covered, and it lands on the critical path.

The likely repair is to let the sweep re-judge every other completed-red run at the head once V covers the newest event, not only the lower ids. Or the body can disposition `sweep.py:115` with that path. Either way it needs a fixture: an edit+code pair, edit numbered lower, edit body span past the bound.

## Findings

- No committed finder's harness predates the fix. `dev/audit/harnesses/r10_gate_defer_race.py` arrives in this PR's first commit (409bbe929, and before that wip-sync 42e82d818), written by the fixer seat. The body calls it "finder-shape", which is a partial disclosure. It does not say plainly that the fixer built it, as fix-review.md step 9 and fixer.md 18 require. Carry: R10-ORCH-LEDGER
- The brief asks for the fixer's UNCERTAINTIES. Neither the PR body, its handoff-body ref (4520e7299 and 611b250f8) nor the commit messages hold an UNCERTAINTIES section, and the PR has no comments. There is nothing to answer, and the brief's premise did not hold at this head. Carry: R10-ORCH-LEDGER
- The body does not size the wait's GitHub API cost. Each poll re-reads the full `read_api` set, which is `pulls/N`, every open PR, the runs at the head and every run's jobs, up to 12 times per deferring gate. It never measures this against the GITHUB_TOKEN hourly budget it shares with the prelude and codescan polls. Carry: dismissed: a rate limit fails closed as `RATE-LIMITED` (gate.py:288, exit 3, never a PASS), the polls run only while deferring, and I found no measured path to exhaustion.

## Evidence

- ev/HEAD.txt: the head reviewed, `ce6f6511e693a6c175282796281c304e22cfb52a`.
- Finder-shape harness, committed copy, all five scenarios (ev/race_head.txt, ev/race_base.txt):
  - Head:
    - `2754: verdicts 3 UNDECIDED-RED 0 MASKED 0 DEADLOCK no gate-wait 660 s`
    - `2754-red: ... UNDECIDED-RED 0 MASKED 0`, every verdict `FAIL tests / closures: failure`
    - `pair: UNDECIDED-RED 0 DEADLOCK no gate-wait 120 s`
    - `cascade: UNDECIDED-RED 0 gate-wait 120 s`
    - `single: UNDECIDED-RED 0 gate-wait 0 s`
  - Base, at both 343fb2a2c and c176ee55d:
    - `2754: UNDECIDED-RED 2`
    - `2754-red: UNDECIDED-RED 2 MASKED 0`
    - `pair: UNDECIDED-RED 2 DEADLOCK yes`
    - `cascade: UNDECIDED-RED 1`
    - `single: UNDECIDED-RED 0`
  - The body's figures re-derive at both ends: first PASS at 1847 s (head) against 1367 s (base), and the longest single wait 600 s.
- Null control for masking: a genuinely red sibling (`2754-red`) is red in every head verdict, with MASKED 0. The harness is sensitive to masking: my mutant G4 (the deferral returns PASS) prints `2754-red: MASKED 2`.
- My mutants (ev/mutants.txt, driver ev/mutants_driver.py) were applied one at a time to the head and restored, and the tree read clean after. All nine were killed:
  - G1 judge never waits: 6 gate fixtures fail, and the harness returns to the base's UNDECIDED-RED and DEADLOCK.
  - G2 unbounded wait: the "past the bound" fixture fails. The harness is unchanged, so only the self-test pins the bound.
  - G3 waits on a decided red: "a decided red never waits" fails.
  - G4 deferral as PASS: 4 gate fixtures fail, and the harness shows MASKED 2.
  - G5 gate waits on judging runs: 4 fixtures fail, and the harness shows `pair DEADLOCK yes`.
  - P1 waits_on in id order only (pre-M1): the prelude "M1: waits for a LATER code run" fails. The harness still shows UNDECIDED-RED 0 but gate-wait 780 s.
  - P2 prelude waits until finished: 2 prelude fixtures fail, and the harness shows `2754 UNDECIDED-RED 2`.
  - P3 prelude never waits: 3 prelude fixtures fail.
  - P4 prelude unbounded: `prelude.py --self-test` never terminates (killed at 300 s), so CI's step would time out red. This killed the mutant.
- The body's mutants M1–M6 map onto my G1, G2, G3, G4, P1 and P2, and give the same failing fixture names.
- `python3 -I tools/ci/gate.py --self-test`: `37 checks, 0 failed`. `python3 -I tools/ci/prelude.py --self-test`: `29 checks, 0 failed`.
- `dev/audit/harnesses/r10_ci_gate_core.py`, run on the unmodified head (ev/gate_core_head.txt):
  - `replay`: `output IDENTICAL to 1371a0a6:measure/rev/gate_replay2.txt`.
  - `mutants`: `RESULT mutants=16 survivors=0`.
  - A first `mutants` attempt refused ("uncommitted edits"), because my mutant driver was running concurrently. I re-ran it on a clean tree.
  - I did not re-run either at the merge base.
- The 720 s bound against the 15-minute `timeout-minutes` of `ci.yml`'s `gate` job, from 31 real gate jobs (ev/gate_job_steps.tsv):
  - Job start to `Judge this head`: median 15 s, max 19 s.
  - One judge read: median 7 s, max 8 s.
  - Post steps: max 3 s.
  - The loop's last sleep begins at no more than 660 s and ends at no more than 720 s, and the final read takes about 8 s. The worst case is about 19 + 728 + 3 = 750 s, under 900 s with about 150 s spare.
  - The self-test pins 720 + 60 + 120 ≤ 900 at equality. Its regex does match the real `gate:` block.
- Claim and version files: the three-dot diff from c176ee55d of `tests/golden/claimed_drift.txt`, `tests/golden/card_claimed_drift.txt`, `VERSION`, `RELEASE_NOTES.md` and the manifest is empty (ev/static.txt).
- `git merge-tree --write-tree origin/main ce6f6511e` exits 0 (tree 9220a0a7c). No MERGE-CLAIM line, since no claim file is touched.
- `tests/closures.json` adds only the new harness to an inert list. This is a classification of a new file, not a moved budget.
- The forward-carries are routed. R10-ORCH-LEDGER is at roster 61446b002 on `handoff/audit-r10-roster`: P82's tick names `GATE_WAIT_MAX_S` (720 s), with removal keyed on this merge, stated as "once it lands". R10-RCA-CODESCAN-WAIT is at roster 216e090fe: M3 is still owed, and M1 and M4 land here.
- CI on this head from the check-runs API at review time (ev/ci_checkruns.tsv): no check concluded red. `tests / closures`, `tests / coverage` and one `prelude` were still in progress. No red check is owed an answer at this time. The `gate` and `mutation` lane logs were not read, because this verdict does not turn on them.
- On a PR the gate job restores `tools/ci/*.py` from the base (ci.yml "Restore the programs from the base"). This PR's own gate therefore runs the old program. The new wait applies only to PRs based on main after this merges.
- The body's `entities.py` result ("4 of 2425 ... identical at both ends", macOS py-spy arms) is not re-derived here; this seat is Linux and the full suite is CI's.
