Root-cause record for the recurrence of "API rate limit exceeded for installation" on required checks after M0 to M2 of `dev/audit/rca/install-ratelimit.md` landed (#2629). On 2026-10-26 the bucket-hour from 04:07:04Z ran dry at 04:52:18Z and stayed dry for 14.8 min, reddening #2848, #2849, #2850, #2832, #2843 and main's push run at `b281d0325`. The analysis is `dev/audit/rca/ratelimit-recur.md`. This PR also carries one countermeasure, M4, in `tools/audit/seat/record_row.py`, and a second offline harness, `dev/audit/harnesses/enumerate_api_calls.py`.

- **The bucket is 5,000 calls an hour.** That is the `limit` in every M0 reading (`RATE_LIMIT before:` / `after:` in the record job).
- **Cause.** Two readers walk `<last v* tag>..main` with `GITHUB_TOKEN` on every push to main:
  - Governance's `record` (`W + 3P` after M1): 731 to 743 calls a push.
  - Nightly `record-autofix`'s "Enumerate the window's merges" step (`2M`): 364 to 370 calls a push, with no concurrency group.

  From the M0 readings and the enumerate step times, the 4,478 calls spent by 04:49:40Z split into record 2,205 (49.2 %), enumerate 1,468 (32.8 %) and everything else 805 (18.0 %, 18.9 a minute). The hour held five pushes to main. Its unconstrained demand was about 6,660 calls, 133 % of the bucket. M1 works as built. M2 bounded nothing, because no push arrived while a run was already pending. No stamp has been made since `v7.0.4`, so the window held 185 merges, against 91 when the earlier record measured it, and each merge adds about 6 calls to every later push.
- **Process state: (c).** The earlier record's class search ("No other O(window) reader found") was carried out as written and missed the enumerate. It classified Nightly by the App token the job mints for its writes; the job's reads use `GITHUB_TOKEN`. The enumerate already read that way at the record's own head `04c1dd779`, and has since `72a4d77bb` (2026-10-04). M1, M2 and O-1's instrument (`record_burst_replay.py`) were all sized on the record job alone.
- **Recurrence, measured.** A scan of every record log from 10-23T23:53Z to 10-26T05:04Z found 43 bucket-hours with a reading. Two ran dry (10-26 02:07Z and 04:07Z), and 8 more reached at least 4,000.
- **M4, built: the enumerate reads once per merge.** `/commits/<sha>/pulls` already carries the number, title, state, head ref and merge SHA, so the `/pulls/<n>` read after it was redundant. Per push: 370 → 185 calls. Standing cost is negative (72–87 s less per push). Cost test passes. **M4 alone does not stop it:** about 5,740 for that hour.
- **M3 = decision O-1: its condition is now met, measured** (demand after M1+M2: 6,660 against 5,000). Moving `--stats` and `--sunset` off the push arm saves 555 calls a push: about 3,910 for that hour without M4, and 2,990 with it. Standing cost is negative. The cadence change (#959 option B) is the owner's, so O-1 is drafted and not built here.
- **The load is not irreducible.** Readers other than the two window walks spent about 1,130 calls an hour (23 % of the bucket). P192 arm (b) stays closed.
- **Refused:** a static census of window-walking `GITHUB_TOKEN` steps. Its only catch would be a reader that M0's lines already expose within one bucket-hour. Two such readers appeared in seven weeks, and that P does not cover a ratchet-counted check.

### Issue text, for the orchestrator

> **Root cause (R10-RCA-RATELIMIT-RECUR).** State **(c)**. The class search of `dev/audit/rca/install-ratelimit.md` was followed and missed a reader. It classified each job by the token it mints, so it missed Nightly record-autofix's "Enumerate the window's merges" step, which reads `GITHUB_TOKEN`. On 2026-10-26 04:07Z the 5,000-call bucket ran dry at 04:52:18Z. Governance's record job took 49.2 % of it and that step 32.8 %. M1 and M2 bounded only the record job, and the window had grown to 185 merges with no stamp since `v7.0.4`. Two of the 43 bucket-hours scanned since M1+M2 ran dry. **Cost test** (per dry hour, at least 85 min of PR wall-clock):
> - M4, the enumerate's redundant `/pulls/<n>` read removed (370 → 185 calls a push, standing cost negative), is built in this PR.
> - O-1, `--stats`/`--sunset` off the push arm (−555 calls a push, standing cost negative), has its condition met by measurement and waits on the owner's friction-cadence call.
> - A static census of window walkers is refused (record section 4).
>
> Record: `dev/audit/rca/ratelimit-recur.md`.

## Head

`23e6f7130da334347aec1dc70aefe6cdf295e4f2` adds one commit to the previous head, containing only this PR's own row, `dev/programme/delivery/2852.md`. The authored code head is `b63f27c5c19c53faf1087710c15373a81e09ee07`.

`3045a2db498206f2ff17e9c767a005650df0386b` merges origin/main `11b7a9d73` into the authored code head `b63f27c5c19c53faf1087710c15373a81e09ee07` (an automatic merge by the orchestrator's script; any resolution inside the code head is described below).

`b63f27c5c19c53faf1087710c15373a81e09ee07` on origin/main `b281d0325c6431ebafd933cb962f69e1683669e3` (merge base). Measured `2026-10-26T05:55:07Z`. The run logs were read from the GitHub API for runs created 2026-10-26 03:30Z to 05:30Z, and from every `governance / record` log of `ci.yml` push runs on main created 2026-10-23T23:53Z to 2026-10-26T05:04Z.

## Mutation proof

`python3 tools/audit/seat/record_row.py --self-test`. Each mutant is one edit to the fixed tree, restored after its run:

- At the base (`b281d0325`'s `enumerate_merges` with this PR's test), written first: `1 self-test check(s) failed: enumerate_merges reads one map per merge and nothing else`.
- M4 reverted on the fixed tree (`pr = matched[0]` back to `pr = _api(repo, f"/pulls/{matched[0]['number']}", token)`): the same check fails, `1 self-test check(s) failed: enumerate_merges reads one map per merge and nothing else`.
- The merge-parent guard removed (`if not delivery_status.merge_parents(...): continue`): the self-test dies with `Refuse: merge commit bbbbbbb attributes to no pull request via the REST API; ...`. The direct push in the fixture is then read and refused.

## Null control

- The fixed tree prints `record_row self-test: all checks passed`.
- The new test's own null arm, a window of direct pushes only, reads nothing (`([], [])`). It also passes on the base, so the base fails only the count check.
- `python3 dev/audit/harnesses/enumerate_api_calls.py HEAD` (empty window) prints `ENUMERATE 0 call(s) for 0 merge(s)`.
- `bash dev/audit/harnesses/record_api_calls.sh origin/main` reads 0 by its own refusal rule (the earlier record).

## Figures

- 5,000-call bucket and the nine readings of the 04:07Z hour (used 225 / 1,718 / 1,722 / 2,667 / 2,968 / 4,443 / 4,478 / 5,000 / 5,000): the `RATE_LIMIT before:` and `RATE_LIMIT after:` lines of `governance / record` jobs 121396980262, 121397428343, 121401462617, 121402476913 and 121407579624 (`gh api repos/tvofi/heatpump_optimizer/actions/jobs/<id>/logs`)
- record job 731 / 735 / 739 / 743 calls a push: `bash dev/audit/harnesses/record_api_calls.sh v7.0.4`, run in a checkout whose origin/main is `21b45524d`, `0dfc063fa`, `bdf69a5c3` and `df478d40b` in turn
- enumerate 364 / 366 / 368 / 370 calls a push at the base, and 182 / 183 / 184 / 185 with M4: `python3 dev/audit/harnesses/enumerate_api_calls.py v7.0.4`, at each of those four pushes, with `b281d0325`'s `record_row.py` and then this head's
- enumerate 370 → 185 at this head's window: `python3 dev/audit/harnesses/enumerate_api_calls.py v7.0.4` (this head; and with `git show b281d0325:tools/audit/seat/record_row.py` swapped in)
- enumerate step times 04:23:29–04:26:19, 04:24:10–04:26:47, 04:40:47–04:43:37, 04:44:45–04:47:10: `gh api repos/tvofi/heatpump_optimizer/actions/runs/<id>/jobs` for Nightly runs 40268792382, 40268845407, 40270267094 and 40270568920, job `record-autofix`
- the ledger (2,205 / 1,468 / 805 of 4,478; 49.2 / 32.8 / 18.0 %; 18.9 a minute): `dev/audit/rca/ratelimit-recur.md` section 1.2. Each interval delta, less the record count, less the enumerate count, with the enumerate split by time where a step crosses a reading
- 6,660 unconstrained demand: record 3,691 + enumerate 1,838 + 18.9 × 60. After M4 about 5,740; after O-1 about 3,910; after both about 2,990: section 4
- 185 merges and 189 first-parent commits in `v7.0.4..b281d0325`: `git rev-list --first-parent --merges --count v7.0.4..b281d0325` and `git rev-list --first-parent --count v7.0.4..b281d0325`
- 43 bucket-hours with a reading, 2 dry, 8 at ≥ 4,000: every `governance / record` job of `gh api 'repos/tvofi/heatpump_optimizer/actions/workflows/ci.yml/runs?branch=main&event=push&created=>=2026-10-22T20:30:00Z'`, attempt 1, with its `RATE_LIMIT` lines grouped by `reset`
- reds in the dry interval: `gh api repos/tvofi/heatpump_optimizer/actions/runs/<id>/attempts/1/jobs` for the `ci.yml` runs updated after 04:30Z, with each failed job's log matched against `RATE-LIMITED reset_epoch=1792991224`, `rate limit exceeded for installation` or `GitHubRatelimitException`. The ci-ratchet reds (HTTP 502/500, `0 bytes`) are not this class and are excluded
- #2850 recovery 17.0 min: gate job 121404728189 completed 04:53:57Z; re-run attempt 2 of run 40269661885 updated 05:10:55Z (`gh api repos/tvofi/heatpump_optimizer/actions/runs/40269661885`)
- the enumerate at `04c1dd779` read with `GITHUB_TOKEN`: `git show 04c1dd779:.github/workflows/nightly.yml` (step "Enumerate the window's merges", line 572), and at `72a4d77bb`: `git show 72a4d77bb:.github/workflows/tests.yml` (line 2708)
- class seams, 2 window-walking steps (governance `record`, nightly `record-autofix` enumerate): `grep -nE -- "--since|describe --tags" .github/workflows/*.yml`
- scoped gate: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)` prints `MODE: SCOPED -- 1 script(s) run, 32 scoped out.` (`tests/entities.py`). `tests/entities.py` prints `2 of 2449 ENTITY CHECKS FAILED` at this head and the same 2 at origin/main `b281d0325` in this seat (`gate-sweep.yml: on CI's completion ...` and `graders-head-copy's delivery_status step ...`), so this diff adds no failure: `diff <(grep "^  FAIL" base.txt | cut -c1-120) <(grep "^  FAIL" head.txt | cut -c1-120)`, whose only differing lines are randomised plant names and spin timings inside checks that pass. Run-always checks: `tests/harness_headers.py` prints `ALL 112 HARNESS HEADER CHECKS PASSED` after this head inlined the canonical `repo_root` (the first run refused `parents[3]` in the new harness); `tests/closure.py selftest` and `tests/layout.py` exit 0. `tests/closures.json` carries the new harness as an INERT read of `tests/harness_headers.py` (`python3 tools/pr/ci_predict.py --apply-inert`, which the handoff predictor asked for); `tests/entities.py` re-run after it: the same 2 failures, `diff` of the FAIL lines differing only in spin timings
- `python3 tools/audit/seat/record_row.py --self-test`: `record_row self-test: all checks passed`
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`

## Red checks

none

## Forward-carry

- Decision O-1 (M3): its condition holds by measurement. Move `--stats` and `--sunset` off the record job's push arm to the weekly schedule and the stamp, putting the friction-cadence change (#959 option B) to the owner unless mandate 6329234399 covers it. The dispatch measures demand as record plus enumerate plus rest; `record_burst_replay.py` replays the record job alone and underreads by the enumerate. Carry: R10-RCA-RATELIMIT-RECUR
- A second M0 pair (`gh api rate_limit`, not counted against the limit) around Nightly record-autofix's enumerate step, so its spend prints directly instead of by inference (`ratelimit-recur.md` section 5). Carry: R10-RCA-RATELIMIT-RECUR

## Friction

none

