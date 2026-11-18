D15-s1 is done. All four of my steps (M1–M4) ran in full, I found five things to report, and nothing is unfinished. The privacy gate as D15.md words it fails even on the clean test bundle (finding 02), so I checked privacy on the replay half instead, as `debug_ingest.py` does. Every step ran on the synthetic test bundle first, then on the owner's 2026-11-16 download. Nothing was committed or pushed, and no value, entity id, entry id or location from the download is written anywhere. The harnesses print only counts and store names.

**Blocked file:** the harness would not let me write `REPORT.md`. Its content is the summary below. `REPORT.json` (in the format `finding.schema.json` describes), the five finding files and eight harnesses are in `dev/audit/rounds/round11/D15/s1/`.

**Carried-over item C1 (M2): examined.** Running `export.violations` over the whole bundle, as D15.md step 2 says, rejects the synthetic test bundle 72 times and the real download 1102 times. None of the real download's rejections is private data. Over the replay half, both bundles come back clean, and a planted credential is caught in all 5 of 5 places I put one.

| step | items | examined | not reached |
|---|---|---|---|
| M1 | 2 | 1 | round 10's 2026-10-14 bundle (this task named only the 2026-11-16 one) |
| M2 | 62 | 62 | none |
| M3 | 24 | 24 | none |
| M4 | 22 | 22 | none |

**Findings** (all results are exact counts, re-run at the baseline):
- **D15-s1-01 (M1, medium):** the step that strips earlier rounds from a finder's tree also removes the file `bundles.json` points to. So the command that lists D15's bundles (`enumerate.py d15-installs`) refuses to run in every D15 finder tree: it printed 1 line before the strip and refuses after. Adding a reference to that file under `tests/` makes it print 1 line again. It is the only one of the 19 listing commands that breaks this way. I listed M1's bundles from a full checkout instead.
- **D15-s1-02 (M2, medium):** D15.md step 2's privacy gate rejects the synthetic test bundle, so every D15 run stops at M2. The rejections are text the integration writes itself: release names, Home Assistant's `**REDACTED**` marker (61 times in the real download) and plan wording. Gating only the replay half brings both bundles to 0. The fix is a wording change to D15.md, which is policy, so it needs the owner's approval before merging.
- **D15-s1-03 (M3, low, cosmetic):** `debug_ingest.py`'s summary line misreports what it checked. It prints 12/12 when only 11 checks ran. With the stores emptied it prints 10/12 when 8 of 10 passed. It also passes the replay privacy check on an empty replay half.
- **D15-s1-04 (M4, medium):** the table of allowed stored values (`store.DOMAINS`) is stricter than what the code actually writes.
  - When no electricity price covered an interval, the code stores an accuracy sample with no predicted cost. The debug log then drops every row carrying such a sample when it reloads after a restart: 0 of 192 rows survive.
  - In the real download, 102 healthy fields are reported as out of range even though their loaders read them fine: the restore-on-off record (1) and old learner keys kept in the weekly snapshots (101).
  - Allowing the empty cost brings the dropped rows back to 192 of 192.
- **D15-s1-05 (M4, medium):** the learned heat-capacity curve saves a measured-heat bucket with a sample count of 0, and its own loader throws that bucket away on restart. In the test, 1 bucket was written and 0 came back. The owner's live store has 1 such bucket, which is not restored, and the snapshots hold 2 more. A loader that accepts a count of 0 loses nothing, and a sample taken at full power is kept normally.

**Leads for other seats:**
- **D15-s3:** both restart gaps, and some upgrades too short to count as gaps, each contain one accuracy sample but no debug row. The first cycle after a restart may be missing from the log.
- **D15-s2:**
  - This download's replay half is filled (24 hours, 28 inputs, clean), so M5 can run without an `export.py` file.
  - The snapshots' `unhealthy_input` field (round 10's carry) is valid in storage; reading what it says is M6's job.
- **Owner unknown:** round 10's request to run `r10_scores_envelope.py --bundle` is outside M1–M4, so I did not run it.

**What held:**
- No credential or full-precision location leaks from the download.
- Every debug row records the release that wrote it, all 9 releases are tagged, and none appears before its tag.
- `debug_ingest.py` passes 11 of 11 checks with no empty-section passes, and rejects the corrupted-accuracy test.
- All 16 stored files load at the right version, with nothing scrubbed and no warnings.

This round's bundle still needs adding to `dev/audit/config/bundles.json` in the round's records pull request.

Files are in `/Users/timmalmstrom/hpo-orch/r10s6/r11/audit-r11-D15-s1/dev/audit/rounds/round11/D15/s1/`:
- REPORT.json
- findings/D15-s1-01.json to D15-s1-05.json
- enum_s1.py
- intake.py
- wall_enum.py
- privacy_gate.py
- ingest_checks.py
- store_replay.py
- domains_drift.py
- capacity_envelope.py