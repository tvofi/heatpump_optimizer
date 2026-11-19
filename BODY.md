Lands the round-11 audit box D3-rem result on main. The box pushed one result commit, `handoff/audit-r11-find-D3-rem` (`6ff1235867`), with no history shared with main, so it could not be opened as a pull request.

The box ran the D3-s1 seat's remaining slice after box D3-top6. Its report is `dev/audit/rounds/round11/D3/s1/REPORT-D3-rem.md` with `reports-D3-rem.json`. Coverage: D3.M1 1260 of 1260, D3.M2 34 of 1260 (10 not reached), D3.M3 35 of 35, D3.M4 35 of 35, D3.M5 23 of 27 (4 not reached). It carries ten new findings, D3-s1-62 to D3-s1-71, all low severity, each with a `probe_<key>.py` harness. Its `CHECK.txt` reads `ok D3-s1`.

The tree holds 321 files; 62 are added here. 212 carry the same bytes as #3814 and 119 of those the same as #3810, so they add nothing; `CHECK.txt` is not copied. 54 are new paths and are copied as the box wrote them. Eight differ from the paths #3810 and #3814 land, so they land with a `-D3-rem` suffix and neither PR conflicts: `REPORT.md`, `REPORT.json`, `m5_solves.py`, `prescreen.py`, `state/baselines.json`, `state/prescreen.log`, `state/gates/null.json` and `state/gates/null.log`. The `report_path` in `reports-D3-rem.json` and `REPORT-D3-rem.json`, and `build_report_rem.py`'s writes, name the suffixed report paths. Files that differ from #3814's only by its repo_root fix, scrub or log trim are not repeated. The box's `null.json` and `null.log` differ in content from top6's, being the box's own full-gate null.

The 15 `probe_*.py` harnesses walked a fixed parent count to the root (`parents[6]`), which `tests/harness_headers.py`'s depth-seam scan refuses. Each now inlines `tools/audit/repo_root.py`'s `repo_root`. Home paths in the evidence were rewritten to `~` by `ref_privacy.py scrub`. No production code changes; every file sits under `dev/audit/`, which `tests/closure.py` lists as INERT by prefix. This PR does not fold, judge or register anything; the findings still go through the round's verify and judge steps.

Issues: none drafted or closed.

## Head

`00b7d10d9cb9f3d1367680933715608dbb4eb734`: the authored head, on origin/main `cb8edb65a5`. It is one commit: the copy, the suffixed paths, the repo_root fix, the scrub and the log trim.

## Mutation proof

n/a: a record PR carries no fix to break.

## Null control

n/a: no behavioural claim.

## Figures

none

## Red checks

`tests/features.py` (lift-peak, a BLAS-dependent figure) is red on main and is answered by hotfix #3815; this PR touches no file it reads.

The code-scanning reds are `code-scanning alert 57 (py/overly-permissive-file)`, `code-scanning alert 58 (py/overly-permissive-file)`, `code-scanning alert 59 (js/insecure-temporary-file)`, `code-scanning alert 60 (js/file-system-race)`, `code-scanning alert 61 (py/insecure-temporary-file)`, `code-scanning alert 62 (py/insecure-temporary-file)`, `code-scanning alert 63 (py/insecure-temporary-file)`, `code-scanning alert 64 (py/incomplete-url-substring-sanitization)`, `code-scanning alert 65 (py/incomplete-url-substring-sanitization)`, `code-scanning alert 66 (py/overly-permissive-file)`, `code-scanning alert 67 (py/overly-permissive-file)`. They are inherited from the box seat scripts already on main under `dev/audit/rounds/round11/`, which are evidence and never imported by the integration; no detector cheaper than the code-scanning run exists for them.

The raw gate logs ran about 16k lines each, which would push `tools/audit/machinery_ratchet.py --check` past its churn cap. Nine logs over 500 lines are trimmed to their first 100 lines, a marker line and their last 200 lines (the full logs stay in `handoff/audit-r11-find-D3-rem` at `6ff1235867ed`); the check reads `ok churn_per_kilo_product_lines 35013 <= 34898 + band 3636` and no budget is raised. The cheaper detector is that check run locally at the copy step, about two minutes per evidence landing.

## Forward-carry

none

## Friction

none
