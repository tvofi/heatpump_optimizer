Lands the round-11 audit box D3-u1d result on main. The box pushed one result commit, `handoff/audit-r11-find-D3-u1d` (`af1554ca89`), with no history shared with main, so it could not be opened as a pull request. Its work branch `handoff-wip/finder-r11-D3-u1d` (tip `comms: done D3-u1d`) holds the same files under the box's own layout plus its comms logs; the landing takes the `dev/audit/` layout of the result commit.

The box ran the D3-s1 seat's D3.M2 and D3.M3 unpinned-site slice (keys `>= c0ecc8e0b6b66ded` of `u1_keys.txt`, 309 keys) and carried the earlier D3R and local boxes' M1 and M5 rows. Its report is `dev/audit/rounds/round11/D3/s1/REPORT-D3-u1d.md` with `reports-D3-u1d.json`. Coverage: D3.M1 1260 of 1260, D3.M2 337 of 1260 (the remaining keys belong to boxes D3-u1a, D3-u1b and D3-u1c), D3.M3 244 of 277, D3.M4 277 of 277, D3.M5 23 of 27. Fast net: 309 driven, 67 killed, 242 survived; full net on the 242: 241 completed, 53 killed, 187 survived, one timeout classified as resource exhaustion. The null control lives and the positive control is killed 2 of 2. It carries no new finding. Its `CHECK.txt` reads `ok D3-s1`.

The result commit holds 745 files; 625 are added here. 118 carry the same bytes as #3810 (117 also as #3814) and add nothing; `CHECK.txt` and one `__pycache__/*.pyc` are not copied. 616 are new paths (556 per-site result files under `state/results/`) and are copied as the box wrote them; none overwrites a file on main or on #3810, #3814, #3818, #3819 or #3822. Nine differ from the paths those pull requests land and land with a `-D3-u1d` suffix, so none conflicts: `REPORT.md`, `REPORT.json`, `finalize.py`, `m5_solves.py`, `prescreen.py`, `PROGRESS-local.log`, `state/baselines.json`, `state/null.json` and `state/prescreen.log`. The `report_path` in `reports-D3-u1d.json` and `REPORT-D3-u1d.json`, and `build_report_u1d.py`'s writes, name the suffixed report paths. `state/prescreen-D3-u1d.log` is 642 lines and lands as its first 100 and last 200 with a trim marker, as #3818 did; the full log stays in the handoff ref. `ref_privacy.py scrub` rewrote none of the 625 files and its guard over the commit reads clean.

No production code changes; every file sits under `dev/audit/`, which `tests/closure.py` lists as INERT by prefix. This PR does not fold, judge or register anything.

Issues: none drafted or closed.

## Head

`30bde12ebd9a1509ff9d7a78378a460f8b5c2961`: the authored head, on origin/main `e83a2c919f`. It is one commit: the copy and the suffixed paths.

## Mutation proof

n/a: a record PR carries no fix to break.

## Null control

n/a: no behavioural claim.

## Figures

none

## Red checks

No concluded check on main is red for this change; it touches only `dev/audit/`.

The code-scanning reds are `code-scanning alert 57 (py/overly-permissive-file)`, `code-scanning alert 58 (py/overly-permissive-file)`, `code-scanning alert 59 (js/insecure-temporary-file)`, `code-scanning alert 60 (js/file-system-race)`, `code-scanning alert 61 (py/insecure-temporary-file)`, `code-scanning alert 62 (py/insecure-temporary-file)`, `code-scanning alert 63 (py/insecure-temporary-file)`, `code-scanning alert 64 (py/incomplete-url-substring-sanitization)`, `code-scanning alert 65 (py/incomplete-url-substring-sanitization)`, `code-scanning alert 66 (py/overly-permissive-file)`, `code-scanning alert 67 (py/overly-permissive-file)`. They are inherited from the box seat scripts already on main under `dev/audit/rounds/round11/`, which are evidence and never imported by the integration; no detector cheaper than the code-scanning run exists for them.

The landing adds one 642-line raw log trimmed to 301 lines and no other raw log over 500; `tools/audit/machinery_ratchet.py --check` on the simulated merge reads `ok churn_per_kilo_product_lines 35265 <= 34898 + band 3636` and `ok nonproduction_merges 476 <= 478 + band 5`, and no budget is raised.

## Forward-carry

none

## Friction

none
