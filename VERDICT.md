Fix review: blocked af9936d846ff9303c2d019df09f2c74a154c7e36 harness: class-open closure.py check accepts a non-canonical table (recorded-entry key order, top-level key order, indent); the pre-PR writer's own output passes it

bus-nonce: ae6289841c73930bcf3548534e39cfab
Round 1. Measured at af9936d846ff9303c2d019df09f2c74a154c7e36 (merge base dcc77dd0). The live head was re-read before posting and has not moved. Evidence dir: /Users/timmalmstrom/hpo-seats/review-2057/ev

## The block (one item, cheap to fix)
The body says `closure.py check` "refuses a table that is out of that layout". The layout is what `write_closures` writes: `json.dumps(indent=1, sort_keys=True)` at every depth, plus sorted, de-duplicated lists. `layout_errors` checks less than that. It checks only the key order of the three tables and their lists. It does not check the key order inside a `recorded` entry, the top-level key order, or the indent. My probe ran the real `check()` (refusal_probe.py, with a null control):
- RESULT variant='canonical (null control)' check_rc=0
- RESULT variant="inert list unsorted (the PR's own case)" check_rc=1
- RESULT variant="recorded entry keys seconds-before-rc (pre-PR writer's order)" canonical_text=False check_rc=0
- RESULT variant='top-level keys unsorted' canonical_text=False check_rc=0
- RESULT variant='indent=2' canonical_text=False check_rc=0

A real writer reaches this. closures-autofix runs `git checkout $PINNED -- tests/closure.py` with PINNED = pull_request.base.sha, so a run whose base predates this merge uses the old writer. I ran that writer (the merge-base closure.py's `merge --partial`, with a 5x re-timing) on this head's table (oldwriter.py):
- RESULT old_writer_rc=0 layout_errors=[] text_is_canonical=False lines_differing_from_canonical=2 (it writes {"seconds", "rc"})

`check` passes that table, and the next canonical write moves those lines again. This PR exists to stop exactly that kind of churn. Suggested fix: refuse unless the text equals `json.dumps(json.loads(text), indent=1, sort_keys=True) + "\n"` and the lists are sorted and de-duplicated. Pin it with the three variants above, and add the canonical null control.

## Everything else checked, and it holds
1. Replay. My own instrument, replay.py, runs synth.py's population and arms against the pre-study's frozen clone at main tip 816547ef, with this head's own writer as a third arm.
   - Result: RESULT pairs=420 T0=70 NOSEC=14 PR=16 seconds_rewrites_as_written=72 under_band=12.
   - The pre-study's 70 and 14 reproduce exactly. The **PR's writer gives 16/420, not 14**: 14 was the seconds-removed arm, and the band still rewrites 12 of 72 timings (the pre-study said 11).
   - The in-tree harness at today's main prints RESULT pairs=506 semantic=0 conflicts_as_written=87 conflicts_layout=17. The body's 462/74/17 was measured at an earlier main.
   - Four PRs under git's default merge, with no driver (a fresh bare clone, no merge.* config): against origin/main 13b6d121, 2054, 2025, 2010 and 2024 are all clean. Against a simulated main+2057, each conflicts once on tests/closures.json. This is the transition the body discloses, so "all 4 would merge clean" holds only once both sides are in the layout (the harness's heads arm).
   - In each of the 4 transition merges, `ledger_merge.py --resolve tests/closures.json` returned rc=0, left 0 unmerged files and produced canonical text. It lost and added no entry against base/ours/theirs (transition_resolve.txt).
2. Writers. I grepped tests/, tools/, .github/ and .claude/workflows. Every in-tree write of the real file now goes through write_closures: merge (both paths), prune and canonical. The exceptions are apply_under_scoped_recordings' restore, which writes back the previous text, and the ledger driver, which writes FORMATS[0] (sort_keys) and sorts the layout tables. Remaining writers outside the layout are the pinned-base autofix during the transition (above) and any hand edit, and the check hole lets both through.
   - Minor: the driver sorts only lists that pass `_is_str_list`, which requires no duplicates. A merged list with duplicates stays unsorted. check refuses that, so it is visible, not silent.
3. Re-sort content. Compared with the merge base, `recorded` and `_comment` are identical, and closures has 2949 entries on both sides. The one difference is +1 inert_reads entry, tests/harness_headers.py -> dev/audit/harnesses/r9_ci2b_closures_merge.py, which classifies this PR's new file and is earned. The head text is canonical. The body's "no entry changed" is true of the canonical step only.
4. Band. `driver_timeout` = max(1200, 3 x seconds), so a run up to 2x the committed value still fits under 3x. The budget estimate and sweep order tolerate 2x. A >2x change is still rewritten: the selftest pins 200->450, and the driver pins "outside 2x wins". The body and the SECONDS_BAND comment say the only reader "orders a sweep". recorded_seconds() also seeds driver_timeout and budget_seconds. Nothing pins SECONDS_BAND < TIMEOUT_SCALE; please correct the comment and consider adding that pin.
5. Refusal. With `if layout:` mutated to `if False:`, the pin FAIL "check refuses an unsorted table" fires (1 of 52), and the sorted-table null control passes. Failing-first evidence exists for the band pins (failing-first.txt). At head, closure.py selftest prints ALL 52 PASSED and ledger_merge --self-test prints "all passed".
6. CI at af9936d846ff9303c2d019df09f2c74a154c7e36: 40 check-runs, 24 success, 14 skipped, 2 failure. closures and closure-scope are success, and closures-autofix was skipped. The reds are nightly-status (113300181884) and delivery-status (113300036748). Both grade main and the body names and answers both, though it cites the job ids from 17f7e029. The diff does not reach what they read.
