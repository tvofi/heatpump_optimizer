Lands the round-11 audit box D3-u1a result on main at the box's re-driven tip. The box pushed result commits to `handoff/audit-r11-find-D3-u1a` with no history shared with main, so it could not be opened as a pull request. This landing carries the tip `48b7c2c08adc927fd240136e452b2a3a666c655d`; an earlier cut of this PR carried the first result commit `a7d585328482`. The box's work branch `handoff-wip/finder-r11-D3-u1a` holds the same files under the box's own `seats/D3-s1/` layout plus its comms logs; the landing takes the `dev/audit/` layout of the result commit.

The box ran the D3-s1 seat's D3.M2 and D3.M3 unpinned-site slice (keys `[000221f3921dd956,3daa55123b452546)`, 309 keys) and carried the earlier D3R and local boxes' M1 and M5 rows. Its report is `dev/audit/rounds/round11/D3/s1/REPORT-D3-u1a.md` with `reports-D3-u1a.json`; the box's own build script also wrote `REPORT-u1a.md` and `REPORT-u1a.json`, which land as written. Coverage: D3.M1 1260 of 1260, D3.M2 333 of 1260 (10 not reached), D3.M3 238 of 271 (33 not reached), D3.M4 214 of 214, D3.M5 23 of 27 (4 not reached). Fast net: 309 driven, 73 killed, 236 survived; full net on the 236: 56 killed, 179 survived, one timeout. The null control lives and the positive control is killed 2 of 2. It carries no new finding. Its `CHECK.txt` reads `ok D3-s1`.

The box tree holds 750 files. `CHECK.txt` and one `__pycache__/*.pyc` are not copied, `finalize.py` differs from the copy on main and is not copied, 145 carry the same bytes as files already on main, and 602 are added here, 532 of them per-site result files under `state/results/`. None overwrites a file on main. Eight differ from the paths main holds, or from the one #3823 lands, and land with a `-D3-u1a` suffix, so no pull request conflicts: `REPORT.md`, `REPORT.json`, `m5_solves.py`, `prescreen.py`, `m4_pending.py`, `state/baselines.json`, `state/null.json` and `state/prescreen.log`. A check of every added path against the heads of #3814, #3819, #3823 and #3824 found `m4_pending.py` the only path another head holds with other bytes. The `report_path` in `reports-D3-u1a.json`, `REPORT-D3-u1a.json` and `REPORT-u1a.json`, and the report writes of `u1a_report.py`, name the suffixed or sibling report paths. The box's build script `build_u1a_report.py` is as the box wrote it. `state/prescreen-D3-u1a.log` is 683 lines and lands as its first 100 and last 200 with a trim marker; the full log stays in the handoff ref. `ref_privacy.py`'s guard over the commit reads clean.

No production code changes; every file sits under `dev/audit/`, which `tests/closure.py` lists as INERT by prefix. This PR does not fold, judge or register anything.

Issues: none drafted or closed.

## Head

`4d2fdf545452162f721f37a7c1aeff6a2154544c` merges main `9d65fe8` into the previous head: an automatic merge by the orchestrator, no resolution. The reviewed code is unchanged.

`3b4a1ba28ee147a085382ece1d8ff67aa5fcc6f6` is this PR's head, unchanged: its code was already in it and main merged cleanly, so the orchestrator's script set this body without a push.

`17ed3be236649b5f85394bab2990cd9fd68f9d98`: the authored head. It adds one commit onto `60cb69de9b1139b3ef4ece398ead2bfaa55812b3` (the first cut, on origin/main `e83a2c919f`) that replaces the first cut's files with the box tip's: the copy and the suffixed paths.

## Mutation proof

n/a: a record PR carries no fix to break.

## Null control

n/a: no behavioural claim.

## Figures

none

## Red checks

`tests / closures` was red at 3b4a1ba (job 135695642071): `INERT READS UNDER-APPROXIMATED`, `tests/harness_headers.py` opened the 7 D3-u1a files this PR lands under `dev/audit/rounds/round11/D3/s1/`, which the committed `inert_reads` did not list. closures-autofix re-recorded them in 47ca46b (`ci: re-record closures`), and `tests / closures` is green at this head (job 135771792070). The cheaper detector is `python3 tools/pr/ci_predict.py --apply-inert` at handoff (`ci-autofix.md`), which writes the entry the Linux recording would; its standing cost is one run per evidence landing.

`governance / wave-script` was red at 47ca46b (job 135737422744): `tools/policy/check-wave-script.mjs` printed `FAIL ownerOnlyRecord reads every declared owner-only brief's id, seat and dimension, and no near-miss []` with `owner-only declared [none]`. That run graded with the base's copy of the grader (main after #3739, merged at e893cd3d1e), which requires an owner-only dimension brief, against a head forked before #3739 that has no `dev/governance/dimensions/DX0.md`. Inherited from main, not this diff: the merge of main at 4d2fdf5 carries both, and `governance / wave-script` is green there (job 135758236678). No cheaper detector exists: base-copy grading is deliberate (`gate-scoping.md`), and merging main is the only cure.

`gate` is red at this head only because it aggregates `pr-contract / pr-contract`, which refused the previous body; it is re-run once this body passes. No separate detector is owed.

main's own gate for `e83a2c919f` was still queued when this was written, and no concluded check on main is red. `tests/features.py` (lift-peak, a BLAS-dependent figure), red earlier, is answered by merged hotfix #3815.

The code-scanning reds are `code-scanning alert 57 (py/overly-permissive-file)`, `code-scanning alert 58 (py/overly-permissive-file)`, `code-scanning alert 59 (js/insecure-temporary-file)`, `code-scanning alert 60 (js/file-system-race)`, `code-scanning alert 61 (py/insecure-temporary-file)`, `code-scanning alert 62 (py/insecure-temporary-file)`, `code-scanning alert 63 (py/insecure-temporary-file)`, `code-scanning alert 64 (py/incomplete-url-substring-sanitization)`, `code-scanning alert 65 (py/incomplete-url-substring-sanitization)`, `code-scanning alert 66 (py/overly-permissive-file)`, `code-scanning alert 67 (py/overly-permissive-file)`. They are inherited from the box seat scripts already on main under `dev/audit/rounds/round11/`, which are evidence and never imported by the integration; no detector cheaper than the code-scanning run exists for them.

The landing adds one 683-line raw log trimmed to 301 lines and no other over 500; `tools/audit/machinery_ratchet.py --check` is re-run by CI on this head, and no budget is raised.

## Forward-carry

none

## Friction

none



