Closes #2272.

## Re-cut

Round 6, one finding: verdict/3078 "Fix review: blocked 67cc0e0a15100eef34848203fdb2bc5c370a830e root-cause-unrecorded", code-scanning alert 47 (py/clear-text-logging-sensitive-data) still firing at `tools/replay/export.py:459`, the `print(f"reading the recorder {rec.label}", file=sys.stderr)` line. Nothing else changed: no refactor, no feature, no retaken figure.

The repair: the line now prints the constant `reading the recorder`; no recorder-derived value reaches that sink, no sanitiser was added, and the value was not moved to another sink. The neighbouring stderr prints were read for the same flow: `left out: entity id(s) under N entry key(s) ... (<key names>)` prints config key names read from the entry, not recorder values, and `price series from the one Tibber price sensor ...` is a constant. Neither is among the alerts named on this PR (47 and 48 only); I did not run CodeQL, so "not flagged" rests on the alert list as the reviewer's verdict gave it.

Consequences handled in the same files, because the label no longer prints on open: `recorder:db_url_credentials_never_printed` and `recorder:sqlite_db_url_named_by_kind_not_path` asserted on the old line and now assert on `reading the recorder`; a new `recorder:sqlite_db_url_refusal_names_kind_not_path` pins that the one place the label still surfaces (the quiet-window refusal) names a db_url SQLite recorder by kind, never its path; the two harness rows that depended on the open line (`URL carried into the recorder label`, `SQLite db_url path carried into the recorder label`) now name the checks that still kill them.

## Head

Handoff head (code): 0cdcc3daa7ed2130a65f1914e712c703ddf28dae, two commits on the PR head 67cc0e0a15100eef34848203fdb2bc5c370a830e (which contains the earlier handoff tip e46ff0a75f1264bb19cbefb444453fb9a91dbaf7). origin/main was f04b25a005f51b9df48154a6544c03e6873ed9de at `date -u` 2026-11-01; `git merge-tree --write-tree origin/main HEAD` exited 0 (clean), so nothing was merged.

## Mutation proof

`HASTUB_TZ=Europe/Stockholm OPENBLAS_NUM_THREADS=1 PYTHONPATH=tests/hastub python3 dev/audit/harnesses/r10_replay_real_day_mutants.py` (FAST tier) at this head: `RESULT killed=34 mutants=34 null_red=0`. REPLAY-tier rows were not re-run: the delta reaches nothing `run_fixture` reads.

- New row, this round: restore `print(f"reading the recorder {rec.label}", file=sys.stderr)`: KILLED, red `recorder:open_line_constant_no_label`.
- Before I repointed the two label rows, the same harness read `killed=31 mutants=33` (survivors: URL carried into the label; SQLite db_url path carried into the label): the label no longer prints on open, so those mutants reached no check. After repointing, both are killed.

## Null control

- Unmutated head: harness `null: red []`; `recorder_checks()` returns 0 failing checks (driver script calling `replay.recorder_checks()` under `PYTHONPATH=tests/hastub`).
- The label is non-empty and distinguishable in the fixture: `SQLite <tmp>/label-canary-recorder.db`, and the check requires `label-canary-recorder.db` absent from stderr. With the interpolation restored the same check reads red with the detail `reading the recorder SQLite /tmp/.../label-canary-recorder.db`.

## Unpinned sites

`prepr.sh` step 6d lists the sites the diff adds. This round adds none under `custom_components/`; the one changed production line is in `tools/replay/export.py`, which the mutation-autofix lane does not mutate, and it is pinned by the in-tree harness row above.

## Figures

- `python3 tests/structure.py`: STRUCTURE RATCHET PASSED.
- Scoped gate, MODE: SCOPED (14 scripts plus `tests/replay.py`), `GOLDEN_MODE=drift`: every script rc=0 except `tests/replay.py`, whose single red is `synthetic-dhw-only.json: cycle_cost [loop_cpu_ratio over its budget 0.143]` (0.1534, 0.1578 and 0.1471 on three runs here). The control: the same fixture at the unchanged PR head 67cc0e0a1 in a separate worktree reads 0.1488, the same red, so the red is this container's CPU class against the recorded budget (the open half of Carry 6, R10-REPLAY-COST-BUDGET), not this delta.
- Alert 47 detector: the repository ships no local CodeQL run for py/clear-text-logging-sensitive-data; the cheaper detector I ran is the dataflow check itself, `recorder:open_line_constant_no_label`, null green and mutant red. The PR's CodeQL run is the authority and has not concluded at this handoff.

## Red checks

- `CodeQL`: red at 67cc0e0a1 for alert 47 (and 48, below). Fixed in code by 0cdcc3daa: the open line prints the constant `reading the recorder`, no recorder-derived value reaches the sink. Cheaper detector: the in-tree dataflow check `recorder:open_line_constant_no_label`, whose mutant (restore `print(f"reading the recorder {rec.label}", file=sys.stderr)`) is KILLED and whose null is green (see Mutation proof); standing cost: one check in `recorder_checks()`, seconds, already in the replay lane. No local CodeQL run exists in the repository; the PR's CodeQL run stays the authority and has not concluded at 0cdcc3daa.
- `code-scanning alert 47 (py/clear-text-logging-sensitive-data)`: the same defect, `tools/replay/export.py:459`; repaired by 0cdcc3daa with the same detector and killed mutant as `CodeQL` above.
- `code-scanning alert 48 (py/clear-text-storage-sensitive-data)`: `tests/replay.py` `_mariadb_install`, a false positive (an invented credential at an invented host inside a `TemporaryDirectory`). No detector can be cheaper than the finding itself; dismissal is owed to the owner, tvofi.
- `tests / fast (3.14)`: red once, at df35202a, where `tests/entities.py` FAILED (run 41269647846; that log keeps the `FAILED` line and not the script's own output, so the exact assertion is not recoverable from it). Not red at 4cccd845, 4c994241, 18bdd5c88 or 67cc0e0a1 (check-runs `success` at each), so a later commit of this branch repaired it and 0cdcc3daa touches nothing it reads. Cheaper detector: `tests/entities.py` itself, which `prepr.sh` runs before the push; standing cost: it already runs in the scoped gate at about 5 minutes, and no new check is proposed.
- `tests / mutation`: red at df35202a, 4cccd845 and 4c994241 for `ADDED UNPINNED` mutants in `custom_components/heatpump_optimizer/replay_doc.py` (lines 336, 401, 403, then 535-580), pinned by later commits of this branch; `tests / mutation` is `success` at 18bdd5c88 and at 67cc0e0a1. Cheaper detector: `prepr.sh` step 6d, which lists the sites a diff adds before the push; standing cost: seconds per handoff, already standing. This round adds no site under `custom_components/` (see Unpinned sites).
- `tests / replay`, `pr-contract / pr-contract`, `gate`: red at earlier commits, answered in the previous bodies and green at 18bdd5c88; `pr-contract / pr-contract` and `gate` were red at 67cc0e0a1 only because alert 47 was unnamed, which this section now does.
- No other red check is known on this branch; 0cdcc3daa has not run CI.

## Carries

The group's eight roster carries (`dev/programme/rosters/wave-r10-groups.json` at origin/handoff/audit-r10-roster), by index. Dispositions are unchanged from the earlier rounds' accepted record; this pass re-took none of them.

- Carry 1 (the real day), Carry 2 (classify the fixture), Carry 3 (#2810), Carry 4 (the R10-DIAG-REDACT precondition on the exported document), Carry 5 (the day choice) and Carry 7 (the owner's export result): done.
- Carry 6 (STRANDED CARRY 57, cost-budget spread): half done, the budget is recorded; the open half, re-centring on the second CI class, is the orchestrator's restatement of R10-REPLAY-COST-BUDGET (see `## Forward-carry`).
- Carry 8 (D15-s1-04, a boolean under a credential-named key): done.

## Forward-carry

- Owed to the orchestrator: restate R10-REPLAY-COST-BUDGET's carry in `dev/programme/rosters/wave-r10-groups.json` as "re-centre the recorded 355.7 / 3740.0 / 0.249 on the second CI class's reading", with its control. Carry: R10-REPLAY-COST-BUDGET
- Carries 4, 6, 8 and 9 (live-bundle reads) are held verbatim by R10-LIVE-BUNDLE-READS in the roster. Carry: R10-LIVE-BUNDLE-READS
- The mold-guard finding is a carry of R10-USER-DOCS-VERIFY in the roster, unchanged. Carry: R10-USER-DOCS-VERIFY
- The widened `not_frozen` rule's blind spot (a published value tracking an input idling at zero that meets one non-zero value and then freezes is not judged; `control:not_frozen` still fires on the two-value case) is a disclosed design trade recorded in `tests/replay.py`'s comment, not a defect. Carry: dismissed: disclosed design trade with its control
- The warm-up claim, export-side masking figures and pump-draw comparison need the owner's untracked export and stay unverified. Carry: dismissed: no seat holds the export

## Friction

none
