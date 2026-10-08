Fix review: blocked 245468e28908863ee1a12df6176a2b1943e9a705 root-cause-unanswered: fast (3.14) went red, unanswered

bus-nonce: 2aed41abafd5f67974965dd78b88c76d

PR #2049 (R9-CI-1), round 3. Head 245468e28908863ee1a12df6176a2b1943e9a705, unchanged since round 2 and still live at posting. All round-2 measurements stand: the M1–M8 RESULT lines, the closures.json semantic diff, and the policy lint (ev2/mutants/results.txt).
Evidence: /Users/timmalmstrom/hpo-seats/review-2049/ev2

## The round-2 block is cleared

handoff/audit-r9-fixplan is now at c385529213b871dec8073dd90ea513cdf877ab6f.
- R9-RO-9's carry (`groups[100].carry`) now holds the R9-CI-1 follow-up text: the pin drive's ~2000 s per killed site, boost_drift_replay.py timing out as a driver, and the correction naming stamp.py's --self-test cleanup race in place of a3:roster (carry-destination-c3855292.txt).
- No string in the roster begins with `/private/tmp`.
- A semantic diff c716b8f8 → c3855292 changes only `carry`, on groups 100 (R9-RO-9) and 109–111 (R9-UX-5/6/7). Every top-level key is identical and the group count is 155 at both ends.

## The new block

`fast (3.14)` at this head finished **failure** (check-run 113149021777, completed 05:03:08Z): `1 TEST SCRIPT(S) FAILED`, `>>> FAILED: python3 tests/entities.py`, `1 of 2210 ENTITY CHECKS FAILED`. Every other `FAIL` line in that output is one of entities.py's deliberate negative controls. The one real failure is:

  FAIL tools/release/stamp.py's --self-test passes  [... OSError: [Errno 39] Directory not empty: '/tmp/tmp3ta3eh7p/.git/objects/pack']

This is the same stamp.py self-test cleanup race that refused #2048's shard 2. It is not this PR's code:
- tools/release/stamp.py and that check are not in the diff.
- entities.py passes 2210/2210 at this head locally (round 2, M0).
- `fast (3.14)` was green at the round-1 head 04b8b4bd (113131994750).

The body's `## Red checks` was written before this red and does not name it, so step 11 applies.

Repair:
1. Add `fast (3.14)` (113149021777) to `## Red checks`: the cause above, and that it is the flake already carried to R9-RO-9. The cheaper detector is that carry's fix. There is no standing check this PR could add.
2. Re-run `fast` at this head.

This is the race's second sighting in a day (#2048 shard 2, then this run). One more, and `defect-root-cause.md` makes it an RCA rather than a carry line; the orchestrator should watch for it.

## CI at the head (check-runs API; polls at 5-minute spacing, last 05:17Z)

- `coverage`: success (05:13:56Z).
- `fast (3.14)`: failure (above).
- `delivery-status`: red. Main's, and answered in the body.
- Green: `closures` (success 04:58Z), `mutation`, `pr-contract`, and the 20 checks listed in round 2.
- One budget-raise-gate twin cancelled.

Once the body names the fast red and a re-run of `fast` comes back green at this same head, I have nothing further. Every other dispatch item is verified in rounds 1–2.
