Lands the round-11 audit box D3-u1b result on main. The box pushed one result commit, `handoff/audit-r11-find-D3-u1b` (`f0e90c2f46`), with no history shared with main, so it could not be opened as a pull request.

The box ran the D3-s1 seat's D3.M2 to D3.M5 unpinned-site slice. Its report is `dev/audit/rounds/round11/D3/s1/REPORT-D3-u1b.md` with `reports-D3-u1b.json`. Coverage: D3.M1 1260 of 1260, D3.M2 343 of 1260 (29 not reached), D3.M3 235 of 268 (36 not reached), D3.M4 225 of 268 (43 not reached), D3.M5 23 of 27 (4 not reached). It carries no new finding. Its `CHECK.txt` reads `ok D3-s1`.

The tree holds 683 files; 561 are added here. 119 carry the same bytes as #3810 and #3814 and add nothing; `CHECK.txt` and one `__pycache__/*.pyc` are not copied. 554 are new paths (about 540 per-site result files under `state/results/`) and are copied as the box wrote them, and none overwrites a file on main. Seven differ from the paths #3810 lands and land with a `-D3-u1b` suffix, so neither PR conflicts: `REPORT.md`, `REPORT.json`, `m5_solves.py`, `prescreen.py`, `state/baselines.json`, `state/null.json` and `state/prescreen.log`. `finalize.py` differs from both #3810 and #3814 and is not copied; theirs stays. The `report_path` in `reports-D3-u1b.json` and `REPORT-D3-u1b.json`, and `build_report_u1b.py`'s writes, name the suffixed report paths. The box's harness `prescreen-D3-u1b.py` carries no fixed parent count. Home paths in the evidence were already `~`; `ref_privacy.py scrub` rewrote none.

No production code changes; every file sits under `dev/audit/`, which `tests/closure.py` lists as INERT by prefix. This PR does not fold, judge or register anything.

Issues: none drafted or closed.

## Head

`63aad5e85032d2f295f3e8acf6a1c1c3526c7c22`: the authored head, on origin/main `cb8edb65a5`. It is one commit: the copy and the suffixed paths.

## Mutation proof

n/a: a record PR carries no fix to break.

## Null control

n/a: no behavioural claim.

## Figures

none

## Red checks

`tests/features.py` (lift-peak, a BLAS-dependent figure) is red on main and is answered by hotfix #3815; this PR touches no file it reads.

The code-scanning reds are `code-scanning alert 57 (py/overly-permissive-file)`, `code-scanning alert 58 (py/overly-permissive-file)`, `code-scanning alert 59 (js/insecure-temporary-file)`, `code-scanning alert 60 (js/file-system-race)`, `code-scanning alert 61 (py/insecure-temporary-file)`, `code-scanning alert 62 (py/insecure-temporary-file)`, `code-scanning alert 63 (py/insecure-temporary-file)`, `code-scanning alert 64 (py/incomplete-url-substring-sanitization)`, `code-scanning alert 65 (py/incomplete-url-substring-sanitization)`, `code-scanning alert 66 (py/overly-permissive-file)`, `code-scanning alert 67 (py/overly-permissive-file)`. They are inherited from the box seat scripts already on main under `dev/audit/rounds/round11/`, which are evidence and never imported by the integration; no detector cheaper than the code-scanning run exists for them.

The landing adds no raw gate log over 500 lines; `tools/audit/machinery_ratchet.py --check` on a simulated merge reads `ok churn_per_kilo_product_lines 35273 <= 34898 + band 3636`, and no budget is raised.

## Forward-carry

none

## Friction

none
