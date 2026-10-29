Fix review: merge 284db132ab89d470da353937bb7adf738507d92a

bus-nonce: 50dcf05dcc63f965ab619628e740a858

## Round

First review of this head. Head measured: `284db132ab89d470da353937bb7adf738507d92a`. It is still the PR head at verdict time, and `review_carry.py 284db132ab89d470da353937bb7adf738507d92a 284db132ab89d470da353937bb7adf738507d92a` prints `CARRY`.

## Findings

- review_packet.py refused with `host-path: home-directory in the body` and wrote no packet. The body cites `/root` (this cloud seat's home) on purpose, as carry 3's null control. `ref_privacy.py` documents `root` as a public container account, yet a whole `/root` path still matches the home-directory class. So on the cloud image, a reviewer seat cannot render the packet for any body that discusses the cloud home. This is an instrument behaviour outside this diff, which does not touch `ref_privacy.py` or `review_packet.py`. I gathered the packet's facts by hand (checks, merge-tree, structure, head note). I did not work around the refusal. Carry: dismissed: an instrument false positive on a public account's home, outside this PR's diff and without effect on its correctness; for the orchestrator to route to the ref_privacy/review_packet owner if it recurs.
- The cheaper detector for the `closures` red (a `ci_predict.py` arm reading the `.py` path literals a changed gate script passes to `subprocess`) is named and left unbuilt. The body defers costing it to a root-cause seat. Carry: dismissed: the red-check trigger is answered in the body with the detector and its standing cost, which is all fix-review.md step 11 checks; building or refusing it belongs to a root-cause seat under defect-root-cause.md, not to this merge.
- Carry 2's control (`RATE_LIMIT enumerate after:` minus `before:` equals `enumerate_api_calls.py <last v* tag>` on a quiet push) can only be read from a Nightly log after landing. That is a task owed after the merge. Carry: R10-RECORD-API-O1: the roster's carry 2 already states this control for the landing seat.

## Evidence

- Mutation proof, from my own mutants on the head worktree with `tests/entities.py` (Python 3.14.2 + tests/hastub, as CI's 3.14 lane runs it). Unmutated: `ALL 2475 ENTITY CHECKS PASSED`. Each mutant below gives `1 of 2475 ENTITY CHECKS FAILED`, the named check:
  - M-a, Nightly enumerate-after step deleted: the M0-pair check fails.
  - M-b, `--stats` report condition dropped: the push-arm check fails.
  - M-c, `schedule|workflow_dispatch) REPORT=true` arm deleted: the window-step check fails.
  - M-d, stamp window `HEAD^` changed to `HEAD`: the window-step check fails.
  - M-e, `enum = 0`: the replay check fails.
  - M-f, O-1 cost `w` changed to `w + 3 * p`: the replay check fails.
  - Extras beyond the body: M-g (`|| true` dropped) fails the M0-pair check. M-h (`--sunset` report condition dropped) and M-i (friction filer report condition dropped) each fail the push-arm check.
  - No mutant survived. Logs: `ev/mut_*.txt`.
- `tests/entities.py` does not parse under Python 3.11 (an f-string at line 4265, blamed to a5fda1741, already on base `ce5940c0d`). CI runs 3.13 and 3.14. The cause is not in this diff.
- Figures. The window has grown since the body's `88c6ad5bb` tip, so I re-derived the rule, not the number. `record_api_calls.sh v7.0.5`:
  - head: `TOTAL 69`, `REPORT 192`.
  - base `ce5940c0d`: `--record 69`, `--stats 192`, `--sunset 0`, `TOTAL 261`.
  - Head TOTAL equals base `--record`, and head REPORT equals base `--stats` + `--sunset`. That is the body's 64/177/241 relation at its tip.
  - `--record 69` equals `rev-list --count --first-parent v7.0.5..HEAD` (69).
- `enumerate_api_calls.py v7.0.5`:
  - base: `ENUMERATE 63 call(s) for 63 merge(s)`, one read per merge (M4).
  - head worktree: refuses fail-closed, because the head merge commit itself has no PR. That is correct behaviour off main.
- Empty-window null controls: `record_api_calls.sh origin/main` prints TOTAL 0 (rc 0), and `enumerate_api_calls.py HEAD` prints ENUMERATE 0. This is the same at base and head. The control is vacuous by construction (empty range), as the body describes it.
- Replay, head (`v7.0.4 2026-10-26T04:07:04Z 2026-10-26T05:07:04Z --rest-per-min 18.9 --limit 5000`):
  - M1+M2: `3692 + 919 + 1134 = 5745 of 5000 (114 %)`.
  - O-1: `935 + 919 + 1134 = 2988 of 5000 (59 %)`.
  - The sums are exact and match the body. The percentages are truncated, not rounded (114.9, 59.8), as the body prints them.
  - Without `--rest-per-min/--limit`: rc 2, required-argument refusal.
  - Base harness: record job alone, `M1+M2 5 run(s), 3692 call(s)`. This matches the body.
- `ref_privacy.py --self-test`: `97 checks, 0 failed`.
- Closures repair. `record_burst_replay.py` leaves INERT through `INERT_EXCEPT`, the same route as the U5 harnesses, `record_row.py` and `merge_train.py`. This narrows the inert list rather than widening it. `tests/closures.json` adds the replay to the closures of `tests/entities.py` and `tests/harness_headers.py`, and `enumerate_api_calls.py` to entities.py's `inert_reads`. `harness_headers.py` keeps the replay in its `inert_reads` as well as its closure. That is the same closure-and-inert_reads pair the U5 harnesses already carry (16 such pairs in the table), so it is not new here. CI `tests / closures` concluded success at this head (job 123691602145). `closures-autofix` was skipped.
- `python3 tests/structure.py` at head: `STRUCTURE RATCHET PASSED`.
- VERSION, the manifest, RELEASE_NOTES.md and the golden/claim files are untouched by the three-dot diff.
- Merge with current origin/main `e5ddba1fa`: `git merge-tree --write-tree` exits 0, and `LEDGER-MERGE: resolved tests/closures.json` (`ev/merge_tree.txt`).
- CI at this head, from the check-runs API (`ev/checkruns.tsv`): 37 success, 17 skipped, 1 failure (`tests / nightly-status`). `gate` succeeded twice. `pr-contract` succeeded twice, the later at 20:23:38Z, after the last red concluded at 19:47:06Z, so the body's red-check answers passed the contract. `tests / mutation` is green, and my targeted mutants above stand in for any inconclusive changed-scope table.
- `nightly-status` red is not this pull request's. It reports `slow` in a main dispatch (run 40835853528). The diff's `nightly.yml` hunks fall only in `record-autofix`, and `tests/nightly_status.py` is not in the diff (defect-root-cause.md).
- Head note: `## Head` names `284db132ab89d470da353937bb7adf738507d92a`.
- The body's earlier reds (`closures`, `closures-autofix`, `gate`, `pr-contract` at `464daee15`) are each named and answered with a cause and a cheaper detector, and all four are green at this head.
- Owner review is still required: `governance.yml` and `nightly.yml` are code-owned (budget-raise-gate is green; no budget raised).
