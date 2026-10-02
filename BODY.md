<!-- ccr-projects-attribution: {"github_login":"tvofi"} -->
_Requested by **tvofi** · [project thread](https://claude.ai/code/project/chan_01EL5jLi4rokGBbkaevYXSJV?thread=cmsg_01EL5jLi4rokGBbkaevYXSJVNnBc94sQQcVgy679F1DM9v)_

Round-9 F10.5, built at the owner's answer to card C5 ("Build"). Part of #201.

Before: the mutation ledger's pre-ratchet stock had no path to a disposition. `mutation-nightly` samples the whole package and records nothing, and `--pin-killed` reaches only the sites a diff adds (R9 RCA I1, residual (a)).

After: a new scheduled job, `mutation-ledger`, drives a 40-site slice of the unpinned stock every night with the table's own kill rule, baseline and null control, and `mutation-ledger-push` commits the `killed_by` rows it earned to `main` as a new ledger-writer App. Survivors are listed in the job summary for a human verdict and never written (`ci-autofix.md`).

How:
- `tests/mutation_table.py --drain OUT_DIR` (with `--scope full`): `drain_pool` takes whole anchors only (a split anchor can never pin, `pin_results`), ordered by a hash of (seed, anchor), skipping anchors no recorded closure reaches; kills go through `pin_results`; `write_drain` writes `status`, `pins.json`, `head` and `survivors.txt` and leaves the checkout's ledger untouched.
- The push half: `apply_drained` applies on the measured head, or on a moved `main` keeps only pins whose killing script and recorded closure saw no change (`stale_pins`), then re-checks every pin against `main`'s inventory through `apply_pins`, so a second apply writes nothing; `drain_write_set_problems` refuses any path but a new file under `tests/mutation_ledger/killed_by/`; `drain_report` reddens every status outside `DRAIN_QUIET`.
- `tests.yml`: `mutation-ledger` (schedule and non-recheck dispatch; no secret, no write grant) uses `--seed $(date -u +%Y%m%d)` so the slice walks the stock; `mutation-ledger-push` runs no driver, mints the App token, applies, checks the write set, commits `ci: record nightly kills`, and pushes fast-forward to `main` (three tries, never forced). It keeps the workflow's `contents: read` floor: the write is the App's own installation token.
- `tests/nightly_status.py`: `REQUIRED_LANES` gains `mutation-ledger`, since `entities.py` refuses a schedule-only lane the reporter does not watch.
- `docs/decisions/0011-app-authored-identity.md`: an amendment names the fourth App (`hpo-ledger`), why none of the three existing identities nor `GITHUB_TOKEN` may carry the push, its write set, subject, target and credential, and what is owed by the owner.

**Owed by tvofi (Mac setup, decision 0011's amendment):** create the `hpo-ledger` App with `contents` read & write, install it, store `HPO_LEDGER_PEM` and `HPO_LEDGER_APPID`, and add it to `main-protect`'s push bypass. Until then the push job reports `skip-no-writer` and stays green; the measured slice survives only as the run artifact. Code-owned paths here (`tests.yml`, `tests/mutation_table.py`, `tests/nightly_status.py`) need tvofi's approving review at the head.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

https://claude.ai/code/session_01BHvfemczTi3GN1mf4szuHM

## Head

f3e2e445bb981eff4fef38242bcb8ac520a7afa6

## Mutation proof

One mutant per new predicate, each applied to `tests/mutation_table.py` in its own worktree at the head, `PYTHONPATH=tests/hastub python3 tests/entities.py` run on each (`audit-r9/fix/evidence/F10.5-drain-f3e2e445/run_mutants.sh`, mutants in `mutants.py` there):

- M1 `drain_pool` takes one site per anchor: FAIL `--drain drives whole drivable anchors under the cap, fixed per seed, moved by the seed`
- M2 `drain_pool` keeps an anchor no closure reaches: FAIL the same check
- M3 `drain_pool` ignores the seed: FAIL the same check (it SURVIVED the first form of the check, whose cap-1 arm had one drivable anchor; the check gained four one-site anchors, commit f3e2e445)
- M4 `stale_pins` reads only the killing script, not its closure: FAIL `mutation-ledger-push applies a drained slice once, and on a moved main only the pins whose killer read nothing that changed`
- M5 `apply_drained` skips the moved-head filter: FAIL the same check
- M6 `drain_write_set_problems` accepts a modified or deleted row: FAIL `the ledger writer may only add killed_by rows, and its job reddens a slice that did not land`
- M7 `drain_report` always green: FAIL the same check
- M8 `apply_drained` reads pins before the status: FAIL `mutation-ledger-push applies ...` (a `skip-nothing-killed` slice would read as `skip-no-measurement`, red)

Survivors on the sites touched: none among M1-M8.

## Null control

M0, a comment-only edit in the drain section, run the same way: `ALL 2060 ENTITY CHECKS PASSED`. In the drain demonstration the table's own null control (a comment-only edit, `away.py` NULL_COMMENT) survived every driver.

## Figures

All at code head f3e2e445, worktree from #1838's head 46a70815.

- Stock: `PYTHONPATH=tests python3 -c 'import mutation_table as m; b=m.load_budgets(); s=m.inventory(); print(len(s), len(m.unpinned_sites(b,s)))'` -> 4518 candidate sites, 3915 unpinned, every one reachable by a recorded closure (`drivers_for` over `DEFAULT_SCRIPTS`).
- Demonstration (scratch ref `handoff/r9-f10-gate-infra-5-demo` @ f59380e0, never merged): `python3 tests/mutation_table.py --scope full --drain OUT --max 40 --jobs 4 --seed 20261002 --scripts <DEFAULT_SCRIPTS minus tests/stress.py>` -> `PIN KILLED: 37 pinned, 3 left unpinned`, `DRAIN: measured`, 69 min on a 4-core cloud box. Then, in that checkout before its commit, `python3 $EXPORT/demo_apply.py` (sha1 440a6d5b3e2465438066c062c0b9443e1ec001bf; `$EXPORT` = the project evidence folder `audit-r9/fix/evidence/F10.5-drain-f3e2e445`) -> `apply 1: changed`, 37 new row files, write-set problems `[]`, unpinned 3915 -> 3878, the 37 anchors covered by a matching disposition, the 3 survivors still unpinned with 0 rows written for them, form/layout/completeness problems `[]`, ratchet verdict `None`, `apply 2 (same slice): skip-unchanged`, and the same-seed slice afterwards overlaps the recorded anchors in 0.
- Null control of the demonstration: the first run with `tests/stress.py` in the net was REFUSED because stress.py's per-call kernel timing (1.93x against 1.80x) killed the comment-only null on this contended box (`drain-run1.txt`); `stress.py` was left out of the second run, so its kills on this slice are CI's to measure. A refusal leaves no status, which the workflow step's `test -s "$out/status"` turns red.
- Nights to drain, by rule: stock / (40 x kill fraction). At the demonstration's 37/40 that is 3915 / 37 = about 106 nights; the stock and the fraction are re-derived by the commands above at any head.
- Gate: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)` -> `MODE: FULL` (tests.yml changes the gate). Run locally: `tests/entities.py` (2060 pass, Python 3.13), `tests/structure.py` (PASSED), `node .claude/workflows/policy_lint.mjs` (0 errors); the rest is CI's.

## Red checks

none yet at this head; CI has not run.

## Forward-carry

none: no later stage's brief is narrowed. The App setup is the owner's action, named above and in the amendment.

## Friction

- environment: cost: the cloud image's `python3` is 3.11 and `tests/entities.py` needs 3.12+; the clone was shallow, which reddens the HANDOVER `updated-for` checks until `git fetch --unshallow origin main` (#1693).

