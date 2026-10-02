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

**The writer exists (tvofi, 2026-10-02):** `hpo-ledger` is App 5094721, an `always` bypass actor on both `main-protect` (22628467) and `main-protect-checks` (23698884), and `HPO_LEDGER_APPID` / `HPO_LEDGER_PEM` are set, the names `mutation-ledger-push` reads. So from the first scheduled night after merge the push job commits `killed_by` rows to `main`. A ruleset read cannot prove that bypass admits the push (the rules endpoint is not bypass-aware), so **that first `ci: record nightly kills` push is the live test of the bypass**; were the secrets ever absent, the job reports `skip-no-writer` and stays green. The decision 0011 amendment now records the setup as done, and `.claude/workflows/fixtures/required-contexts.json` records the App on 23698884's bypass list (cb6870bc), which the live change had turned `policy_lint` red on. Code-owned paths here (`tests.yml`, `tests/mutation_table.py`, `tests/nightly_status.py`) need tvofi's approving review at the head.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

https://claude.ai/code/session_01BHvfemczTi3GN1mf4szuHM

## Head

`4f594b42635be021152dec6e3934af1a674cec52` adds one commit to the previous head, containing only this PR's own row, `docs/delivery/1848.md`. The authored code head is `cb6870bc4fea680ef1faf9db2c8e2d8a8a5543c1`.

cb6870bc4fea680ef1faf9db2c8e2d8a8a5543c1

Merged `origin/main` twice since the previous head f3e2e445: a535bf12 (#1838's head e37cefc6), 0f39c486 (main 2b6c5b87, #1838 merged) and 43d4cb23 (main af7660c7, #1843). All three merged clean; **no semantic conflict**: `git diff f3e2e445 HEAD` over `tests/mutation_table.py`, `.github/workflows/tests.yml`, `tests/nightly_status.py` and the decision 0011 file is empty, and main's changes to `tests/entities.py` (#1838's checks, #1843's mandate block) touch none of the drain checks. Two commits of this branch's own since: 728594ec, a check arm (below), and cb6870bc, the fixture re-record and the amendment's setup paragraph (below).

## Mutation proof

Re-run at 43d4cb23 on this Mac (cb6870bc changes neither `tests/mutation_table.py` nor `tests/entities.py`) (Python 3.14): one mutant per new predicate in `tests/mutation_table.py`, applied in place on a committed tree, `PYTHONPATH=tests/hastub python3 tests/entities.py` run, file restored by `git checkout` (runner: `/Users/timmalmstrom/hpo-seats/R9-F10.5/scratch/mut/mutants.py`, out of tree, sha1 a01ae2fe470ec253d08fe13730099834117cc50b; the earlier proof's runner was cloud-only, so these mutants are re-derived, not copied):

- M1 `drain_pool` takes one site per anchor (`group[:1]`): FAIL `--drain drives whole drivable anchors under the cap, fixed per seed, moved by the seed`
- M2 `drain_pool` keeps an anchor no closure reaches (drivers forced non-empty): FAIL the same check
- M3 `drain_pool` ignores the seed (hash key `0:{a}`): FAIL the same check
- M4 `stale_pins` reads only the killing script, not its closure: FAIL `mutation-ledger-push applies a drained slice once, and on a moved main only the pins whose killer read nothing that changed`
- M5 `apply_drained` skips the moved-head filter (`if False:`): FAIL the same check
- M6 `drain_write_set_problems` accepts a modified or deleted row (drops the `??` test): FAIL `the ledger writer may only add killed_by rows, and its job reddens a slice that did not land`
- M7 `drain_report` always green (`ok = True`): FAIL the same check
- M8 `apply_drained` reads `head` and `pins.json` before its status gate: FAIL `mutation-ledger-push applies ...` (after 728594ec; see below)

Each mutant run printed `1 of 2065 ENTITY CHECKS FAILED`, rc=1.

**M8 survived at the merged head before 728594ec.** In the form above (`apply_drained` reads `head` and `pins.json` before its status gate) it passed all checks at 0f39c486: every pass-through arm of the apply check fed `apply_drained` a directory `write_drain` made, which always writes all three files, while `main()`'s `skip-nothing-drivable` branch writes `status` alone. Under the mutant that green status reads as a red `skip-no-measurement`. 728594ec adds a status-only arm; M8 now fails the check. Survivors on the sites touched: none among M1-M8.

## Null control

M0, a comment-only edit in the drain section, run the same way: `ALL 2065 ENTITY CHECKS PASSED`, rc=0. The unmutated head: `ALL 2065 ENTITY CHECKS PASSED`, rc=0. In the f3e2e445 drain demonstration the table's own null control (a comment-only edit, `away.py` NULL_COMMENT) survived every driver.

## Figures

At code head cb6870bc (mutants and the stock at 43d4cb23, whose `tests/` tree is the same), `origin/main` af7660c7, 2026-10-02.

- Stock: `PYTHONPATH=tests python3 -c 'import mutation_table as m; b=m.load_budgets(); s=m.inventory(); u=m.unpinned_sites(b,s); c=m.load_closures(); al=[x for x in m.DEFAULT_SCRIPTS.split(",") if x]; d=[x for x in u if m.drivers_for(x["file"], c, al)]; print(len(s), len(u), len(d), len({x["anchor"] for x in u}))'` -> 4520 candidate sites, 3911 unpinned, 3911 of them reachable by a recorded closure, under 3857 anchors. Null control for "every one reachable": the same expression with `al` left as the unsplit `DEFAULT_SCRIPTS` string printed 0 drivable, so the predicate does return fewer when closures do not reach.
- One night's slice at this head: `drain_pool(<the stock above>, load_closures(), <DEFAULT_SCRIPTS split>, 20261002, 40)` -> 40 sites.
- Demonstration (scratch ref `handoff/r9-f10-gate-infra-5-demo` @ f59380e0, never merged), **measured at f3e2e445 and not re-run here**: `python3 tests/mutation_table.py --scope full --drain OUT --max 40 --jobs 4 --seed 20261002 --scripts <DEFAULT_SCRIPTS minus tests/stress.py>` -> `PIN KILLED: 37 pinned, 3 left unpinned`, `DRAIN: measured`; then `demo_apply.py` (cloud evidence folder `audit-r9/fix/evidence/F10.5-drain-f3e2e445`, sha1 440a6d5b3e2465438066c062c0b9443e1ec001bf) -> `apply 1: changed`, 37 new row files, write-set problems `[]`, the 3 survivors with 0 rows, `apply 2 (same slice): skip-unchanged`. It still describes this head's drain code: the four drain files are byte-identical to f3e2e445 (`git diff --quiet f3e2e445 HEAD -- tests/mutation_table.py .github/workflows/tests.yml tests/nightly_status.py docs/decisions/0011-app-authored-identity.md && echo IDENTICAL-4` -> `IDENTICAL-4`), but the inventory it drained moved with #1839, so its slice and kill fraction are of that tree. It was not re-run on this Mac: the drive runs `features.py` and the solver scripts, whose baseline fails here on BLAS, and a 40-site drive is about an hour on four cores; CI's first nightly is the measurement at this tree.
- Null control of the demonstration: the first run with `tests/stress.py` in the net was REFUSED because stress.py's kernel timing killed the comment-only null on a contended box; `stress.py` was left out of the second, so its kills are CI's to measure. A refusal leaves no status, which the workflow step's `test -s "$out/status"` turns red.
- Nights to drain, by rule: stock / (40 x kill fraction). With this head's stock and the demonstration's 37/40: 3911 / 37 = about 106 nights; both terms are re-derived by the commands above at any head.
- Gate: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir $D` -> `MODE: FULL -- every test script runs, nothing is scoped out.` (`.github/workflows/tests.yml changes the gate itself`). Run locally at cb6870bc: `tests/entities.py` (`ALL 2065 ENTITY CHECKS PASSED`), `tests/structure.py` (`STRUCTURE RATCHET PASSED`), `node .claude/workflows/policy_lint.mjs` (`TOTAL: 0 error(s) across 40 policy file(s)`, rc=0; null control: the same run at 43d4cb23, before the fixture re-record and after tvofi's ruleset change, printed `TOTAL: 5 error(s)`, all five `[required-contexts] ... ruleset 23698884 field bypass_actors[...]`, rc=1). Not run locally, CI's: every other FULL-mode script, `features.py` and the solver goldens (no CI-equivalent numeric stack here), `tests/stress.py`, the closures recording (`PREPR_SKIP_CLOSURES=1`).

## Red checks

none yet at this head; CI has not run. Expected red elsewhere, not from this diff: tvofi's 2026-10-02 bypass addition makes `policy_lint`'s `required-contexts` class red on `main` and on every branch whose fixture still records the deploy key alone, until cb6870bc's re-record reaches `main`. No cheaper detector exists: the class is the detector, and it fired within one run of the live change, as designed.

## Forward-carry

none: no later stage's brief is narrowed. The App setup is the owner's action, named above and in the amendment.

## Friction

- environment: cost: `tests/entities.py` now imports `numpy` through `binary_sensor.py`, so it cannot run on this Mac's bare 3.14 interpreter; it ran in a scratch venv carrying `tests/requirements-ci.txt` (not CI's BLAS build, which no check run here depends on).
- fixer.md: unenforced: the earlier proof's mutants lived in a cloud-only evidence folder, so a Mac re-run after a merge re-derives them; the first proof's exact M8 form is not recoverable here, and the re-derived form survived until 728594ec.

