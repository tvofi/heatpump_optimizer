Fix review: merge 5df5e26cc935dafabdddebf18b5070875f4f00d5

bus-nonce: 3239048c7e948c6e7453667475fa69c9
pending-ci: gate

## Scope

Round 1 (no reviewed head; full review). PR #3680, head 5df5e26cc935dafabdddebf18b5070875f4f00d5, base 6f422812d5d8b918beace0283419c153f6df66ce. Diff (three-dot): `tests/features.py` (+4/-2: the month-edge check's instant built in `_sce_dt.DEFAULT_TIME_ZONE` instead of UTC, comment corrected January -> February) and the delivery row `dev/programme/delivery/3680.md`. No production code, no budget, closure, golden or claim file, no VERSION / manifest / notes heading touched.

## Evidence

- RESULT head: the PR body's head line names 5df5e26cc935dafabdddebf18b5070875f4f00d5, the head measured (`ev/HEAD.txt`).
- RESULT merge-tree: `git merge-tree --write-tree origin/main <head>` exit 0 (tree 1b9c964087d7), no conflict; head is 0 commits behind the main read here (`ev/merge-tree.txt`).
- RESULT cause: production stamps a running-signal edge with `dt_util.now()` (`running_signal.py`, aware in the configured zone), `StartCounter.fold` keys `since.strftime("%Y-%m")` and `ledger.month_key` keys `when.strftime("%Y-%m")`, so both month keys are the configured zone's wall clock, as the body says. A UTC literal 2026-02-28 23:59:50Z is 1 March locally east of UTC; the check, not production, was wrong.
- RESULT null control re-run (`ev/null-control.txt`, `tools/audit/seat/features_block.py` with its `--emit-prelude` prelude, block start `import asyncio as _sce_aio  # noqa: E402`): base 6f422812 gate (TZ=UTC, HASTUB_TZ unset) 21 ok 0 FAIL; UTC 21/0; America/New_York 21/0; Asia/Kolkata, Asia/Tokyo, Europe/Stockholm 20 ok 1 FAIL each, the nightly's check with `[{'2026-03': 1}]`. Head: 21 ok 0 FAIL in all six. Matches every figure in the body's Null control section.
- RESULT other configurations (`ev/extra-zones.txt`): head 21 ok 0 FAIL under Pacific/Kiritimati (UTC+14), Pacific/Pago_Pago (UTC-11), America/Los_Angeles, Australia/Adelaide (half-hour offset).
- RESULT mutation proof re-run at the head (`ev/mutants.txt`), each restored, worktree clean after: M1 (`_book_starts` ledger.add at `dt_util.now()`) FAIL in gate, Asia/Kolkata, America/New_York; M2 (`fold` keys the month of `since + EDGE_DEBOUNCE_S`) FAIL `[{'2026-03': 1}]` in all three. The body's two mutants are killed as claimed. (My first M2 spelling raised NameError on an unimported `timedelta`; the re-run qualifies it and is the one counted.)
- RESULT own mutants M3 (`fold` keys the UTC month) and M4 (`ledger.month_key` keys the UTC month): survive in gate and Asia/Kolkata, killed only under America/New_York. See Findings.
- Figures: block counts re-derived as above. `1 of 5703 FEATURE CHECKS FAILED` (run 43783271327) and `ALL 114 FINITE BOUNDARY CHECKS PASSED` not re-derived: the first is a CI log the body cites, the second a local whole-script run I did not repeat. The body states `host_zone_features.py --suite` was not run; I did not run it either.
- Class (step 6): the body names no enumeration rule; the issue states one seam (one failing check), and the nightly Asia/Kolkata run reported it as its only FAIL among 5703, so a one-seam class under the zone the nightly runs. Not read as compliance under other zones.
- Harness: no committed finder's harness; the finder here is the nightly `slow` step "Zone-sensitive scripts under Asia/Kolkata", whose check is the one fixed, re-run by block above. `features_block.py` is an in-tree instrument; the zone loop (`zones.sh`) is this reviewer's, disclosed as the builder's.
- Red checks: owed-reds set printed by `merge_train.py owed-reds` (`ev/owed-reds.txt`). The body answers `tests / nightly-status` (non-required, not in the owed set) with cause and a recorded refusal of a per-PR zone lane.
- Forward-carry: body says none; none owed by the fix itself.
- CI: `merge_train.py classify` polled at this head from 17:45 to 18:16 UTC, every run WAIT; last line `WAIT 5df5e26cc935dafabdddebf18b5070875f4f00d5 pending: gate red: none` (`ev/classify.txt`), hence `pending-ci: gate`. The live check-runs read at ~17:54 show `tests / nightly-status` failure (non-required; it reports main's Nightly red that this PR fixes, not in the owed-reds set) and the `gate` aggregate's earlier run failure while lanes were still queued; classify, not that listing, decides.
- Head re-read before return: branch tip still 5df5e26cc935dafabdddebf18b5070875f4f00d5 (`ev/head-recheck.txt`).

## Findings

- Follow-up: the zone-keying of the start-counter month and the ledger month is pinned by no lane CI runs. With the fixed check, a mutant keying either month in UTC instead of the configured zone (M3 on `wear.StartCounter.fold`, M4 on `ledger.month_key`) passes the per-PR gate (TZ=UTC) and the nightly Asia/Kolkata lane, and fails only under a zone west of UTC (America/New_York), which no CI lane runs. Pre-existing: the old UTC-literal check could not catch it in the gate either. Not this PR's defect, which only made the check zone-correct. Carry: dismissed: pre-existing coverage gap outside this hotfix's scope, recorded here for the next test-gap round
