9a0960559ed9e87c679e50f30bce43a599c63459
<!-- ccr-projects-attribution: {"github_login":"tvofi"} -->
_Requested by **tvofi** · [project thread](https://claude.ai/code/project/chan_01EL5jLi4rokGBbkaevYXSJV?thread=cmsg_01EL5jLi4rokGBbkaevYXSJVNnBc94sQQcVgy679F1DM9v)_

Round-9 F10.5, built at the owner's answer to card C5 ("Build"). Part of #201.

Before: the mutation ledger's pre-ratchet stock had no path to a disposition. `mutation-nightly` samples the whole package and records nothing, and `--pin-killed` reaches only the sites a diff adds (R9 RCA I1, residual (a)).

After: a new scheduled job, `mutation-ledger`, drives a 40-site slice of the unpinned stock every night with the table's own kill rule, baseline and null control, and `mutation-ledger-push` commits the `killed_by` rows it earned to `main` as a new ledger-writer App. Survivors are listed in the job summary for a human verdict and never written (`ci-autofix.md`).

How:
- `tests/mutation_table.py --drain OUT_DIR` (with `--scope full`): `drain_pool` takes whole anchors only (a split anchor can never pin, `pin_results`), ordered by a hash of (seed, anchor), skipping anchors no recorded closure reaches; kills go through `pin_results`; `write_drain` writes `status`, `pins.json`, `head` and `survivors.txt` and leaves the checkout's ledger untouched.
- The push half: `apply_drained` applies on the measured head, or on a moved `main` keeps only pins whose killing script and recorded closure saw no change (`stale_pins`), then re-checks every pin against `main`'s inventory through `apply_pins`, so a second apply writes nothing; `drain_write_set_problems` refuses any path but a new file under `tests/mutation_ledger/killed_by/`; `drain_report` reddens every status outside `DRAIN_QUIET`.
- `tests.yml`: both ledger jobs run only on `refs/heads/main`, under `schedule` or a non-recheck `workflow_dispatch`. `mutation-ledger` (no secret, no write grant) uses `--seed $(date -u +%Y%m%d)` so the slice walks the stock; `mutation-ledger-push` runs in `environment: ledger`, runs no driver, mints the App token, applies, checks the write set on the tree and the commits on `origin/main..HEAD` (`drain_push_problems`), commits `ci: record nightly kills`, and pushes fast-forward to `main` (three tries, never forced). It keeps the workflow's `contents: read` floor: the write is the App's own installation token.
- `tests/nightly_status.py`: `REQUIRED_LANES` gains `mutation-ledger` and `mutation-ledger-push`, since `entities.py` refuses a schedule-only lane the reporter does not watch.
- `docs/decisions/0011-app-authored-identity.md`: an amendment names the fourth App (`hpo-ledger`), why none of the three existing identities nor `GITHUB_TOKEN` may carry the push, its write set, subject, target and credential, and what is owed by the owner.

Round 2 answers the #1848 review (`review/1848`, blocked on security): B1 main-only reach, B2 the `ledger` environment and an amendment that states the credential's reach, B3 the reviewer's surviving mutants A2, A3 and A7. Code-owned paths here (`tests.yml`, `tests/mutation_table.py`, `tests/nightly_status.py`) need tvofi's approving review at the head.

## Approval

Owed by tvofi, the owner's setup that this round's code half depends on (decision 0011's amendment, as amended in this round). Code-owned paths here also need tvofi's approving review at the head.

1. Create the Actions environment `ledger` with deployment branches restricted to `main`.
2. Store `HPO_LEDGER_APPID` and `HPO_LEDGER_PEM` in that environment, and **delete the repository-level copies**. GitHub hands repository secrets to every same-repository job, environment jobs included, so the YAML cannot tell the two scopes apart: while repository-level copies exist, any branch's workflow can still mint the `hpo-ledger` token. Only the deletion closes that.
3. Decide on the `main-protect` (22628467) bypass. That ruleset holds only `deletion` and `non_fast_forward`, which a fast-forward push never meets, so the App's `always` entry there grants only force-push and deletion of `main` and buys this workflow nothing. Recommended: remove it. The `main-protect-checks` (23698884) bypass is the one the row push needs.

Fail-closed, stated exactly. Until step 2's deletion, the push job still receives the repository-level secrets (and if `ledger` does not exist yet, GitHub creates it on first use with no branch rule), so the job works and B1's `refs/heads/main` guard is the only bound on this workflow; other branches' workflows can still read the secrets. After the deletion, with the secrets in `ledger` alone, a job outside that environment, or one on a ref other than `main`, gets no credential. If the environment holds none, the mint step finds no credential, the record step reports `skip-no-writer`, the report step reddens it (`skip-no-writer` is no longer in `DRAIN_QUIET`), and `nightly-status` sees a red `mutation-ledger-push` lane. It never falls back to green. The first nightly `ci: record nightly kills` push is the live test of the 23698884 bypass (the rules endpoint is not bypass-aware).

## Head

`9a0960559ed9e87c679e50f30bce43a599c63459` merges the authored code head `1fc1c6cca6bf19e948aed72edfab00852b50e56a` and then merges origin/main `948671af1`, with no hand resolution, into this PR's previous head.

1fc1c6cca6bf19e948aed72edfab00852b50e56a

Since round 1's head 4f594b42: merged `origin/main` aab94eea (#1849, whose `required-contexts.json` change is byte-identical to this branch's cb6870bc; clean, no semantic conflict) at 5cf0f755; failing checks first at 7a1380a2; the fix at f268e3ab; a check arm for P1 at 9ff92b56; the amendment's fail-closed sentence at 1fc1c6cc. `origin/main` has since moved to 2e7422e5 (#1845, #1850, #1853); none of those touches this branch's files and `git merge-tree --write-tree origin/main HEAD` exits 0, so it is not merged here.

## Mutation proof

Failing checks first: at 7a1380a2 (checks only, no fix) `tests/entities.py` printed `5 of 2069 ENTITY CHECKS FAILED`: the reach check (a branch-ref dispatch reached both jobs), the credential check, the commits-sent check (`drain_push_problems` absent), the YAML wiring pin (`m.drain_changed`), and the drain-report check (`skip-no-writer` still quiet). At f268e3ab: `ALL 2069 ENTITY CHECKS PASSED`.

Round-2 mutants, each applied in place on a committed tree, `PYTHONPATH=tests/hastub python3 tests/entities.py`, file restored (runner `/Users/timmalmstrom/hpo-seats/R9-F10.5/scratch/mut/mutants2.py`, out of tree, sha1 1a1911079bc731396cd620cc44392a9731049e17):

- R0 null (comment in the `mutation-ledger` YAML): `ALL 2069 ENTITY CHECKS PASSED`, rc=0
- G1 guard dropped from `mutation-ledger`'s `if:`: FAIL `a branch-ref dispatch reaches neither mutation-ledger nor mutation-ledger-push; main's schedule and dispatch reach both`
- G2 guard dropped from `mutation-ledger-push`'s `if:` (measuring job still guarded): FAIL the same check (the push alone reaches a branch ref)
- G3 guard moved inside an `||` (`github.ref == 'refs/heads/main' || github.event_name == 'workflow_dispatch'`): FAIL the same check
- E1 `environment: ledger` removed: FAIL `the ledger writer's secrets are read by mutation-ledger-push alone, in the ledger environment`
- Q1 `skip-no-writer` put back in `DRAIN_QUIET`: FAIL `the ledger writer may only add killed_by rows, and its job reddens a slice that did not land`
- A2 (the reviewer's form, half one) `ref: main` dropped from the push job's checkout: FAIL `mutation-ledger-push sends one row commit on main's tip, and its diff of the measured head fails closed`
- A2r (half two) `&& git reset -q --hard origin/main` dropped: FAIL the same check
- A2c the `drain_push_problems` call before the push removed: FAIL the same check
- P1 `drain_push_problems` counts `< 1` instead of `!= 1`: SURVIVED at f268e3ab (every two-commit arm also moved `HEAD^` or the diff); 9ff92b56 adds a row-only merge arm, after which FAIL the same check
- P2 the `A`-status test dropped (a rewritten row passes): FAIL the same check
- P3 the subject test disabled: FAIL the same check
- A7 (the reviewer's) `drain_changed` ignores the diff's returncode: FAIL the same check (an unknown measured head gives `[]`, not `None`)
- A3 (the reviewer's) `echo "::add-mask::$tok"` removed: FAIL `the ledger writer's token and auth header are masked before their first use`

Each failing mutant printed `1 of 2069 ENTITY CHECKS FAILED`, rc=1. G1-A3 ran at f268e3ab; P1 again with R0 at 9ff92b56. 1fc1c6cc changes only the decision text.

Round-1 mutants M1-M8 (runner `mutants.py`, sha1 a01ae2fe470ec253d08fe13730099834117cc50b, same form as round 1):

- M1, M2, M3 (`drain_pool`): FAIL `--drain drives whole drivable anchors under the cap, fixed per seed, moved by the seed`
- M4, M5, M8 (`stale_pins`, `apply_drained`): FAIL `mutation-ledger-push applies a drained slice once, and on a moved main only the pins whose killer read nothing that changed`
- M6, M7 (`drain_write_set_problems`, `drain_report`): FAIL `the ledger writer may only add killed_by rows, and its job reddens a slice that did not land`

M0-M3 ran at f268e3ab, M0 and M4-M8 at 9ff92b56 (the first M4 run's restore hit a full disk; see Friction); each failing one printed `1 of 2069 ENTITY CHECKS FAILED`, rc=1.

Survivors on the sites touched: none.

## Null control

R0, a comment-only edit in the `mutation-ledger` job's YAML, and M0, a comment-only edit in the drain section of `tests/mutation_table.py`: both `ALL 2069 ENTITY CHECKS PASSED`, rc=0. The unmutated head: `ALL 2069 ENTITY CHECKS PASSED`.

## Figures

At code head 1fc1c6cc, `origin/main` aab94eea, 2026-10-02.

- Reach, by rule: the reach check evaluates each ledger job's own `if:` (GitHub's `&&`, `||`, `!`, `always()` over literal contexts) for every event in {schedule, workflow_dispatch, push, pull_request} x ref in {refs/heads/main, refs/heads/fix/x, refs/pull/1/merge} x recheck in {true, false}, and requires both jobs reached exactly when the ref is main and the event is schedule or a non-recheck dispatch, and the push refused on any other ref even when `mutation-ledger` is set to `success`. Null control: at 7a1380a2 it listed the branch-ref cases as reached.
- Stock (unchanged code path since round 1, re-derived there): `PYTHONPATH=tests python3 -c '<round 1's command>'` -> 4520 sites, 3911 unpinned, 3911 drivable, 3857 anchors at 43d4cb23; not re-derived at this head (the inventory reads production files, which this round does not touch: `git diff --quiet 43d4cb23 HEAD -- custom_components && echo SAME` -> SAME).
- Demonstration: measured at f3e2e445 on a cloud box (`PIN KILLED: 37 pinned, 3 left unpinned`, apply then `skip-unchanged`) and **not re-run** since; the reviewer re-ran the apply half on the real tree (40 synthetic pins, `apply1 changed`, `apply2 skip-unchanged`) and not the drive.
- Nights to drain, by rule: stock / (40 x kill fraction); with 3911 and 37/40, about 106.
- Gate: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir $D` -> `MODE: FULL` (`tests.yml` changes the gate). Run locally at 1fc1c6cc: `tests/entities.py` (`ALL 2069 ENTITY CHECKS PASSED`), `tests/structure.py` (`STRUCTURE RATCHET PASSED`), `node .claude/workflows/policy_lint.mjs` (`TOTAL: 0 error(s) across 40 policy file(s)`). Not run locally, CI's: the rest of FULL, `features.py` and the solver goldens, `tests/stress.py`, closures (`PREPR_SKIP_CLOSURES=1`).

## Red checks

none at round 1's head (the reviewer's read: 0 failure). This round's head: CI has not run.

## Forward-carry

none: the remaining work is the owner's setup in `## Approval`, recorded in decision 0011's amendment.

## Friction

- environment: cost: `tests/entities.py` imports `numpy` through `binary_sensor.py`, so it runs here only in a seat-local venv carrying `tests/requirements-ci.txt`.
- environment: cost: the Mac's disk filled mid-run (444 MiB free); one mutant's restore (`git checkout`) failed with `No space left on device`, leaving the mutant in the tree until restored by hand; M4-M8 were re-run after.
- fixer.md: unenforced: the round-1 proof had no arm on what a push SENDS (only the working tree), so a reviewer's mutant on the checkout ref survived; this round's check drives a real repository.

