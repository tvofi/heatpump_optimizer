R10-RCA-LIVEHEAD-CANCEL, the root-cause seat. The two whole-run cancels at live heads on #3241 (run 42332985078, attempt 1) and #3232 (run 42329221705, attempt 2) were not `concurrency:` cancels, runner loss or `cancel_superseded.py`. GitHub annotates every cancelled job `The run was canceled by @tvofi.`: a cancel POSTed under the owner's credential, from outside every in-tree canceller, and followed by a rerun under the same credential. The class is routine: 155 such cancels at live heads in 76 h.

This PR lands:
- `dev/audit/rca/r10-livehead-cancel.md`: cause, process state (a), class reach, cost test, countermeasure and refusals;
- `dev/audit/harnesses/livehead_cancels.py`: the detector, which attributes every cancelled `ci.yml` attempt to its canceller and tests it against the live head;
- the class `N-livehead-operator-cancel` and the `_rca` record `R10-RCA-LIVEHEAD-CANCEL` in `dev/audit/config/bugclasses.json`;
- the class id registered in `finding.schema.json`'s `class_guess` enum, and in `.claude/workflows/audit-find.js`'s `CLASS_GUESS` and `FINDING_REPORT`, the readers the `agreement` lane pairs with the ledger;
- one `inert_reads` line in `tests/closures.json`, written by `ci_predict.py --apply-inert`.

The process that sent the cancels cannot be named from GitHub data. The orchestrator's seat transcripts can name it (RCA section 6).

## Head

9bc716deb677f2a4933835782292677caa5245e6. The branch merged origin/main at 294a880dae608502b62055775e34a5db93217b98; the figures were taken at base 355d9965a7a14ec45ef8cd25fb9c75c5ced044f1. The merge brought in no change to `ci.yml`, `cancel_superseded.py` or the harness inputs, which are GitHub API reads over a closed window ending 2026-11-07T04:00:00Z. The figures do not depend on main's tip.

## Mutation proof

Two mutants of `dev/audit/harnesses/livehead_cancels.py`, each restored afterwards (`git status` clean):
- `in_class` without `and BOT not in row["by"]`: `--selftest` prints `selftest: FAILED`, and over the cache `NULLCONTROL-BOT class=204` (unmutated: 0).
- `classify`'s live test replaced by `True`: `--selftest` prints `selftest: FAILED` (`'2/1': ('@github-actions[bot]', True)`), and `CLASS live-head external cancels: 184` (unmutated: 155).

## Null control

- Unmodified, `python3 dev/audit/harnesses/livehead_cancels.py --selftest` prints `selftest: ok`.
- Over the cache, `NULLCONTROL-HEAD live=0 class=0` and `NULLCONTROL-BOT class=0`.
- #3275's runs 42334622520 and 42334625513, cancelled by the in-run `cancel-superseded` job, read `The run was canceled by @github-actions[bot].` and classify as `superseded`, outside the class. So the annotation and the classifier tell the canceller apart.
- Completeness: `total_count` for the window is 1217, equal to the runs read.

## Figures

- `gh api repos/tvofi/heatpump_optimizer/check-runs/<job>/annotations`: `The run was canceled by @tvofi.` on jobs 128283882523 and 128284504740 (run 42332985078/1), and on 128288382623, 128288382597 and 128288382585 (run 42329221705/2).
- `gh api repos/tvofi/heatpump_optimizer/actions/runs/<id>/attempts/<n>`: the next attempts started 03:25:29Z (42332985078/2) and 03:50:51Z (42329221705/3), triggering actor `tvofi`.
- `python3 dev/audit/harnesses/livehead_cancels.py --cache DIR --fetch --since 2026-11-04T00:00:00Z --until 2026-11-07T04:00:00Z --list`, CLASS line, rule in the harness docstring: `CLASS live-head external cancels: 155, minutes lost 2864.7`.
- The same command, FOLLOW lines: restarted 81 (1861.2 min), duplicate 5 (153.0 min), dropped 69 (850.5 min); restart gap median 906 s, 18 within 120 s.
- The same command, CANCELLED lines: 182 `@github-actions[bot]` superseded, 154 `@tvofi` live, 32 timeout live, 17 unattributed live.
- `gh api 'repos/tvofi/heatpump_optimizer/actions/workflows/ci.yml/runs?per_page=1&created=2026-11-04T00:00:00Z..2026-11-07T04:00:00Z' --jq .total_count`: 1217.
- `grep -rn "paused.json\|PAUSE #\|never_pause" tools dev/governance .claude dev/audit/config`: no output at 355d9965 (P267's bounded pause has not landed).
- `python3 tools/audit/fold_ledger.py check`: `0 violation(s)`.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`.
- `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)`: `MODE: SCOPED -- 1 script(s) run, 32 scoped out` (tests/entities.py). `PYTHONPATH=tests/hastub python3 tests/entities.py`: `ALL 2640 ENTITY CHECKS PASSED`.
- The `run_always` lines: `tests/env_drift.py --claims-only origin/main` ok; `tests/closure.py selftest` `ALL 118 closure shrink pins PASSED`; `tests/layout.py` ok; `tests/harness_headers.py` `ALL 112 HARNESS HEADER CHECKS PASSED`.
- `python3 -I tools/policy/agreement_py.py --out F && node tools/policy/agreement.mjs --py-json F`: `AGREEMENT ok`, `divergent=0`. Before the registration it was `divergent=1`, `N-livehead-operator-cancel` absent from the schema enum and from `CLASS_GUESS`.

## Red checks

none

## Forward-carry

The finding changes the orchestrator's next pass: name the process sending `@tvofi` cancels at live heads (RCA section 6), then either land P267's bounded pause or refuse at that seat's cancel path. This seat's write scope is its return refs, so it cannot write that brief.
Carry: R10-CI-PRIORITY-PAUSE (the live group carrying P267's bounded pause; the orchestrator names the sender first, `dev/audit/rca/r10-livehead-cancel.md` section 6).

## Friction

- `frugal-inline-budget`: cost: the routing hook refused a sixth inline read in a turn twice, mid-measurement. Carry: dismissed: delegating reads cleared it each time, no rule changes
- `harness-listing-cap`: unenforced: GitHub's filtered runs listing stops at 1000 without an error. The first fetch read exactly 1000 of 1217. The harness now slices the window and refuses a slice at the cap. Carry: dismissed: repaired in this diff by livehead_cancels.py fetch
