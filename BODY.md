Lands the round-11 audit box D3-top6 result on main. The box pushed one result commit, `handoff/audit-r11-find-D3-top6` (`fdd9e2d827`), with no history shared with main, so it could not be opened as a pull request.

The box ran the D3-s1 seat's D3.M3 slice (T1-T3: full net and full gate over the prescreen survivors). Its report is `dev/audit/rounds/round11/D3/s1/REPORT-D3-top6.md` with `reports-D3-top6.json`: universe 35 survivors, 30 examined, 5 not reached. It carries one new finding, D3-s1-02 (low): no suite check pins the `k <= 0` guard of `tariff._smooth_topk_sum`, and the scalar and batch top-k disagree at `k = 0`. Its `CHECK.txt` reads `ok D3-s1`.

Every file the result commit adds under `dev/audit/rounds/round11/` is copied, 265 files, except `D3/s1/CHECK.txt`; the tree held no `__pycache__/`. None was on main and none overwrites a main file. No production code changes. Every new file sits under `dev/audit/`, which `tests/closure.py` lists as INERT by prefix. This PR does not fold, judge or register anything; D3-s1-02 still goes through the round's verify and judge steps.

The box shares `D3/s1/` with box D3-m5, which #3810 lands. 119 of the shared paths carry the same bytes on both branches, so either merge order adds them once. `D3/s1/finalize.py` takes #3810's blob, which has the canonical `repo_root`. Eight paths differ between the two boxes and land here with a `-D3-top6` suffix, so neither PR conflicts with the other or overwrites its copy: `REPORT.md`, `REPORT.json`, `m5_solves.py`, `prescreen.py`, `state/baselines.json`, `state/null.json`, `state/prescreen.log` and `state/results/c3c6/6e6026d857732e96.json`. The `report_path` in `reports-D3-top6.json` and `REPORT-D3-top6.json`, and the box's own scripts that call or write those files (`box_report.py`, `top6_compose.py`, `t3_drive.sh`, `phase_a.sh`, and the two renamed scripts), name the suffixed paths. Log and JSON evidence text still names the unsuffixed paths, as the box wrote it.

Twelve box harnesses walked a fixed parent count to the root (`parents[6]`, or `HERE.parents[5]`), which `tests/harness_headers.py`'s depth-seam scan refuses. Each now inlines `tools/audit/repo_root.py`'s `repo_root`, and the inline scan is rc 0. The evidence carried this host's home paths; `ref_privacy.py scrub` rewrote them to `~`. The cloud-box paths under `/home/user/` stay, as in 62 round-11 files already on main.

Issues: none drafted or closed.

## Head

`d325ee730d8e755b0fa402cb9f2517d29de6e086`: the authored head, on origin/main `7ae05284d5`. It is one commit: the copy, the renames, the repo_root fix and the scrub.

## Mutation proof

n/a: a record PR carries no fix to break.

## Null control

n/a: no behavioural claim.

## Figures

none

## Red checks

`policy-docs` is expected red on the machinery ratchet: `tools/audit/machinery_ratchet.py --check --base origin/main --head HEAD` reads `FAIL churn_per_kilo_product_lines 49943 <= 34898 + band 3636`. The box's full-gate logs under `D3/s1/state/gates/` are about 16k lines each, and the copy adds 343194 lines.

## Forward-carry

none

## Friction

none
