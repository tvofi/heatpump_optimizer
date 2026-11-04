Fix review: blocked 3f7777a59bc0f95fc47885e68e3f6d4e39e60d55 ci-red: the new harness replay.py reddens tests / fast (3.14) on harness_headers.py (depth root at replay.py:40) and tests / closures on an INERT read harness_headers.py makes of it

bus-nonce: 56eece9fc13b9c75685dd629534e3cbc

Round 2 (delta from 563c8e6db against my round-1 `claim-refuted` block). Head measured: 3f7777a59bc0f95fc47885e68e3f6d4e39e60d55 = merge of authored code head e1637032a into 563c8e6db; merge base c3a279e3252a8b57bb00b5a677318cd4fe20387f, origin/main unmoved at c3a279e32. The delta is `tests/ci_ratchet.py` (floor keyed on the window median, only `success` prices, a ran job with no conclusion refuses, docstring), `tests/ci_budgets.json` (22.0 -> 21.983, band 1.3 kept, reason) and the new harness `dev/audit/harnesses/r10_hotfix_ci_critpath_3/{replay.py,runs.json}`.

The round-1 block is settled on the statistic, but the head is red on two required lanes, and both reds come from a file this round added.
- **Statistic, settled.** One 3.2x outlier on each of the three heavy lanes now moves nothing on the real 40 runs (it was +0.183 / +6.95 / +0.0). The same harness against 563c8e6db's ratchet reproduces the round-1 failure.
- **Mutants and figures, settled.** Every mutant on the new floor is killed. The recorded value and the band's need reproduce exactly from a runs.json identical to my independent round-1 gather.

**Does it red `main` on the first push after merge? The ratchet does not; this head as it stands does.**
- **The ratchet passes.** The newest completed ci.yml push run on main is still 41577822624 (c3a279e32), runs.json's newest. So the first post-merge ci-ratchet grades runs.json's newest 16: 20.75 on 21.983 + 1.3 = 23.283, PASS. Its own run is in progress, so it is not in the window.
- **main's current red clears.** main's ci-ratchet log at 41577822624 shows critical_path_minutes as its only GREW.
- **The second push also passes.** Once the post-merge ci-ratchet succeeds, its 96 s starts pricing (see Findings) and the window reads 22.35, 0.93 under the line.
- **But this head would red main anyway.** It carries the `tests / fast (3.14)` and `tests / closures` reds below, and a push to main runs `full`. So merged as-is, main stays red on `gate`: the ratchet's red would be traded for a harness-header and closure red. The repair is local to the new harness, and the delta's statistic needs no change.

## Block

`dev/audit/harnesses/r10_hotfix_ci_critpath_3/replay.py`, new this round, turns two required lanes red at this head (CI run 41790799421).
- **`tests / fast (3.14)`** (job 126444215753): `tests/harness_headers.py` fails `every inlined walk matches the canonical helper and no depth root remains [FAIL depth seams: dev/audit/harnesses/r10_hotfix_ci_critpath_3/replay.py:40: ROOT = HERE.parents[3]`, then `1 of 112 HARNESS HEADER CHECKS FAILED`, `1 TEST SCRIPT(S) FAILED` (ev/ci_job_126444215753.txt). The harness hand-rolls its repository root instead of using the canonical helper.
- **`tests / closures`** (job 126444215740): `INERT READS UNDER-APPROXIMATED ... tests/harness_headers.py: dev/audit/harnesses/r10_hotfix_ci_critpath_3/replay.py` (ev/ci_job_126444215740.txt). harness_headers.py reads the new file, and the committed `inert_reads` does not list it. `tests / closures-autofix` (job 126449845964) also failed and repaired nothing.

The body's "Gate scope ... `MODE: SCOPED -- 1 script(s) run`: `tests/entities.py`" is accurate as printed. It is also the cause: the committed closures did not know `harness_headers.py` reads new harness files, so the scoped local gate never ran the script that reddens. The cheaper detector is `python3 tests/harness_headers.py`, run locally on any diff adding a file under `dev/audit/harnesses/`, which `prepr.sh`/`ci_predict.py` did not predict. The body's Red-checks section does not name either red.

## Findings

- Docstring citations point at a file that does not exist: `tests/ci_ratchet.py:58` and `:665` cite `dev/audit/harnesses/r10_hotfix_ci_critpath_3.py`, but the harness is `dev/audit/harnesses/r10_hotfix_ci_critpath_3/replay.py`. A reader following the citation finds nothing. Carry: R10-HOTFIX-CI-CRITPATH-3
- `OTHER_WORK_FRACTION` is pinned only by a harness CI never runs: the mutant 1/3 -> 1/2 passes the self-test (52 checks, 0 failed) and is killed only by `replay.py` (RESULT: does NOT hold), which no CI job runs. The floor's level has no self-test check. Carry: R10-HOTFIX-CI-CRITPATH-3
- Success-only pricing makes the ratchet's own failure lower the grade, and that is not disclosed. `tests / ci-ratchet` ends every chain and failed in all 16 newest runs (22 failure, 16 success, 2 cancelled over 40), so it prices 0 today. The newest window reads 20.75; with ci-ratchet priced it would read 21.7. After the merge it starts pricing again: the second push reads 22.35 (one 96 s success), still under 23.283. More generally, any chain job that fails stops pricing, so a broken lane under-reads, and a record taken across such a stretch is recorded low. Carry: R10-HOTFIX-CI-CRITPATH-3

## Evidence

- RESULT self-test at head: 52 checks, 0 failed (ev/selftest_head.txt). Matches the body.
- RESULT harness at head, `python3 dev/audit/harnesses/r10_hotfix_ci_critpath_3/replay.py`, exit 0, RESULT: holds (ev/replay_head.txt):
  - grade 20.75; windows 19.967..21.983; record 21.983 = budget; band need 0.55 against band 1.3.
  - Each of these matches the body.
- RESULT harness against 563c8e6db's ratchet and budgets: exit 1, RESULT: does NOT hold (ev/replay_at_563c8e6db.txt).
  - The outliers read +0.183 (closures) and +6.95 (fast), my round-1 figure.
  - The null control holds at both ends as the body states.
- runs.json sha1 5ac806dd6f5e4a80ea8af04ea0b4431a32f153b7 matches the body. It holds the same 40 run ids as my round-1 ev/runs40.json, and 0 runs differ in their (name, started, completed, conclusion) job tuples. The record is therefore re-derived from independently gathered data, not only the fixer's.
- Round-1 perturbations re-run on the new statistic (ev/plants.txt, ev/replay_head.txt):
  - Single 3.2x outlier on closures / fast / arch-instrument: +0.0 / +0.0 / +0.0. A 10x outlier also reads +0.0 on each lane.
  - The median floor's breakdown point is 9 of 16: 3.2x outliers in the newest k runs read +0.0 up to k = 8. At k = 9 they read +1.383 (closures), +6.95 (fast) and +0.0 (arch-instrument). That is the median's own limit, not a defect.
  - 15 of 16 slow (x1.9): +6.417 / +6.95 / +5.167. The docstring and body now disclose this.
  - +300 s in the newest k runs, closures: +0.0 at k = 1, 4, 8; +1.383 at k = 12; +3.233 at k = 15 and 16. Fast: +0.0 until k = 15, then +5.0. This matches the body's lag table, now disclosed. The k = 16 growth arm (≥ 3.0) is asserted as the outlier arm's null.
  - Cancelled or failed lane in the newest run, work unchanged: +0.0 on every lane, new and retired. A cancelled `tests / *` job drops the run.
- Plants that read +8.033 are my artefact, dismissed. These were a failed `fast` cut to 0.4 or 0.9 of its work, and a quick 1100 s `fast` draw in the newest run (ev/plants.txt, ev/chain.txt).
  - Shortening a job's completed_at without moving its dependent's created_at makes `_walk` infer `codeql / Analyze (python)` as ci-ratchet's need. ci-ratchet's needs are `[fast, coverage, closures]` (tests.yml).
  - The retired statistic reads the same +8.033, and no real run in the 40 has codeql on its chain.
  - It is not a property of the delta.
- RESULT mutants on the delta, each applied alone and restored (ev/mutations.txt, ev/mut.sh), giving self-test FAIL count / replay result:

  | mutant | self-test FAIL | replay |
  |---|---|---|
  | median -> max | 1 | does NOT hold |
  | median -> min | 1 | holds |
  | floor removed | 1 | holds |
  | priced `!= "skipped"` | 2 | does NOT hold |
  | priced True | 2 | does NOT hold |
  | no-conclusion guard off | 1 | holds |
  | price max | 5 | does NOT hold |
  | fraction 1/2 | 0 | does NOT hold |

  - Every mutant is killed by at least one instrument.
  - The body's four mutant counts reproduce.
  - The record value depends on success-only pricing: under the `!= "skipped"` mutant it is 22.0 again.
- RESULT merge-tree against origin/main c3a279e32: clean, rc 0, tree 8d770fc5d (ev/merge_tree.txt).
- Gate scope at head: `tests/closure.py select --diff c3a279e32` printed `MODE: SCOPED -- 1 script(s) run, 32 scoped out`. `tests/structure.py` printed STRUCTURE RATCHET PASSED. Both match the body.
- Not re-derived: I did not run `tests/entities.py` locally (no homeassistant module in this seat), so CI is its check here. Nor did I re-run archscore dS, or re-read the per-script 1.85 ratio and the 45.0/18.8 ms solve lines, which the body itself carries from round 1.
- VERSION, the manifest version and the notes heading are untouched. The 3-dot diff is 5 files: the delivery row, ci_budgets.json, ci_ratchet.py and the two harness files.
- Red checks: `tests / nightly-status` is red at render. The diff touches none of what it reads, so that red is main's. `tests / ci-ratchet` red on main is named and answered in the body.
- RESULT CI on this head: `merge_train.py classify 3f7777a59bc0f95fc47885e68e3f6d4e39e60d55 --pr 3180` still exits 3 at the last read: "WAIT 3f7777a59bc0f95fc47885e68e3f6d4e39e60d55 pending: gate red: none" (ev/classify.txt, ev/classify_log.txt, 26 polls from 07:21Z). `gate` has not concluded and one `prelude` is still in progress, so classify does not yet list the lane reds.
  - The check-runs API at this head reads `tests / fast (3.14)` failure, `tests / closures` failure, `tests / closures-autofix` failure and `tests / nightly-status` failure (main's), with `codeql / Analyze (python)` and one `prelude` in progress. The block rests on the two completed required-lane failures, not on classify's verdict.
  - Head and origin/main re-read before return: refs/pull/3180/head 3f7777a59, main c3a279e32, both unmoved.
