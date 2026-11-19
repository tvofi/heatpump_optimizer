Lands the round-11 audit box D3-u1a result on main. The box pushed one result commit, `handoff/audit-r11-find-D3-u1a` (`a7d585328482`), with no history shared with main, so it could not be opened as a pull request. Its work branch `handoff-wip/finder-r11-D3-u1a` (`883585027729`, `comms: done D3-u1a`) holds the same files under the box's own `seats/D3-s1/` layout plus its comms logs; the landing takes the `dev/audit/` layout of the result commit.

The box ran the D3-s1 seat's D3.M2 and D3.M3 unpinned-site slice (keys `[000221f3921dd956,3daa55123b452546)`, 309 keys) and carried the earlier D3R and local boxes' M1, M4 and M5 rows. Its report is `dev/audit/rounds/round11/D3/s1/REPORT-D3-u1a.md` with `reports-D3-u1a.json`. Coverage: D3.M1 1260 of 1260, D3.M2 333 of 1260 (10 not reached), D3.M3 238 of 271 (33 not reached), D3.M4 271 of 271, D3.M5 23 of 27 (4 not reached). Fast net: 309 driven, 73 killed, 236 survived; full net on the 236: 58 killed, 178 survived. The null control lives and the positive control is killed 2 of 2. It carries no new finding. Its `CHECK.txt` reads `ok D3-s1`.

The tree holds 713 files; 592 are added here. 119 carry the same bytes as #3810 (118 also as #3814) and add nothing; `CHECK.txt` and one `__pycache__/*.pyc` are not copied. 584 are new paths (549 per-site result files under `state/results/`) and are copied as the box wrote them, and none overwrites a file on main. Eight differ from the paths #3810 lands and land with a `-D3-u1a` suffix, so neither PR conflicts: `REPORT.md`, `REPORT.json`, `m5_solves.py`, `prescreen.py`, `state/baselines.json`, `state/null.json`, `state/prescreen.log` and `PROGRESS-local.log`. `finalize.py` differs from both #3810 and #3814 and is not copied; theirs stays. The `report_path` in `reports-D3-u1a.json` and `REPORT-D3-u1a.json`, and `u1a_report.py`'s writes, name the suffixed report paths. `state/prescreen-D3-u1a.log` is 734 lines and lands as its first 100 and last 200 with a trim marker, as #3818 did; the full log stays in the handoff ref. The box's own `/home/user/...` paths in `state/superseded/dirty-tree-u1a-r2-null.out` are the box's, not a host's; `ref_privacy.py scrub` rewrote none of the 592 files and its guard over the commit reads clean.

No production code changes; every file sits under `dev/audit/`, which `tests/closure.py` lists as INERT by prefix. This PR does not fold, judge or register anything.

Issues: none drafted or closed.

## Head

`60cb69de9b1139b3ef4ece398ead2bfaa55812b3`: the authored head, on origin/main `e83a2c919f`. It is one commit: the copy and the suffixed paths. `python3 tools/pr/ci_predict.py --apply-inert` run at the copy step predicts no closures, fast, governance or instrument red and changes nothing.

## Mutation proof

n/a: a record PR carries no fix to break.

## Null control

n/a: no behavioural claim.

## Figures

none

## Red checks

main's own gate for `e83a2c919f` was still queued when this was written, and no concluded check on main is red. `tests/features.py` (lift-peak, a BLAS-dependent figure), red earlier, is answered by merged hotfix #3815.

The code-scanning reds are `code-scanning alert 57 (py/overly-permissive-file)`, `code-scanning alert 58 (py/overly-permissive-file)`, `code-scanning alert 59 (js/insecure-temporary-file)`, `code-scanning alert 60 (js/file-system-race)`, `code-scanning alert 61 (py/insecure-temporary-file)`, `code-scanning alert 62 (py/insecure-temporary-file)`, `code-scanning alert 63 (py/insecure-temporary-file)`, `code-scanning alert 64 (py/incomplete-url-substring-sanitization)`, `code-scanning alert 65 (py/incomplete-url-substring-sanitization)`, `code-scanning alert 66 (py/overly-permissive-file)`, `code-scanning alert 67 (py/overly-permissive-file)`. They are inherited from the box seat scripts already on main under `dev/audit/rounds/round11/`, which are evidence and never imported by the integration; no detector cheaper than the code-scanning run exists for them.

The landing adds one 734-line raw log trimmed to 301 lines and no other over 500; `tools/audit/machinery_ratchet.py --check` on a simulated merge reads `ok churn_per_kilo_product_lines 34569 <= 34898 + band 3636`, and no budget is raised.

## Forward-carry

none

## Friction

none
