Fix review: blocked 4f594b42635be021152dec6e3934af1a674cec52 security: the drain push has no main-ref guard, so a branch dispatch writes that branch's measurements to main; the bypass credential is a repository-wide secret, and decision 0011's "exactly this grant" describes the workflow, not the credential

bus-nonce: 46a35f67c9cc400f3eee70b6737ccd32

Round 1. Fix-review seat for #1848 (R9-F10.5). I reviewed from a detached worktree at `4f594b42` (code `cb6870bc` plus `docs/delivery/1848.md`), with the merge base `af7660c7` and three-dot diffs throughout. Policy under `tools/audit/briefs/`, `.claude/rules/` and `CLAUDE.md` has not changed between the merge base and `origin/main`. The prior-review ref the brief names, `handoff/r9-f10-gate-infra-5-review`, does not exist on the remote, so everything below is my own measurement. Evidence is in the `evidence/` directory, and `HEAD.txt` names the head.

## What blocks

### B1: a branch dispatch pushes that branch's measurements to main (code)

`mutation-ledger` runs on `schedule` and on any `workflow_dispatch` whose recheck is not true. `mutation-ledger-push` runs whenever that job succeeds. Neither job checks `github.ref`.

- **What a branch dispatch does.** A dispatch on a branch whose head subject is not `ci:` drives that branch's tree with that branch's `tests/mutation_table.py`. The push job then applies the resulting pins on `main` and pushes them with the bypass token.
- **The moved-head filter does not catch it.** `stale_pins` treats only the killing script and its recorded closure as dependencies. The measuring instrument (`tests/mutation_table.py`, `tests.yml`) is in no closure.
  - `RESULT moved-from af7660c74 changed 7 dropped 0 of 40 status changed rows 40` (`push_harness.py`, real inventory, real ledger, real git). Here the "measured head" is the merge base, so `changed` is this PR's own 7-file diff, which includes `tests/mutation_table.py` and `tests.yml`. All 40 pins pass the filter.
  - A drain fix dispatched on its own branch would therefore push kills that the unreviewed kill rule judged.
- **It has happened with this exact `if:`.** `mutation-nightly` carries the identical condition.
  - Of the last 100 dispatched `Tests` runs, 80 were on non-main branches. In 54 of them the lane existed: it was skipped in 52 and ran in 2 (`dispatched-mn.tsv`).
  - The 2 are runs 34844399348 (`fix/nightly-real-provider-frame-guard`) and 34695172324 (`claude/nightly-verify-dispatch`), both dispatched by tvofi. Under this PR, each of those dispatches would have pushed to `main`.
  - The autofix jobs also dispatch `tests.yml --ref "$HEAD_REF"` and rely on the head subject being `ci:`. A non-`ci:` push that lands in between the autofix push and the dispatch flips recheck to false.
- **The fix is cheap.**
  - Add `github.ref == 'refs/heads/main'` to `mutation-ledger`'s `if:`, or to both jobs.
  - Pin it in the entities check, which today only requires the substring `github.event_name == 'schedule'`.
  - `RESULT A10` (guard added to the push job's `if:`): `ALL 2065 ENTITY CHECKS PASSED`. So the guard breaks nothing.

### B2: the credential is wider than the amendment says (owner setup and amendment text)

**The secret is readable by any branch workflow.**

- `HPO_LEDGER_PEM` and `HPO_LEDGER_APPID` are repository-level Actions secrets. `GET environments` gives `total_count 0` (`repo-secrets-and-envs.txt`).
- GitHub's documented behaviour passes repository secrets to every same-repository run (push, pull_request, dispatch), and only fork runs are excluded. The tree already relies on this: `closures-autofix` mints `HPO_RUNS_PEM` on `pull_request` runs. I did not measure a PR run reading `HPO_LEDGER_PEM` itself.
- So any branch workflow can mint an `hpo-ledger` token, including one authored by `hpo-author`. That App pushed this PR's own `tests.yml` change (author `app/hpo-author`).
- The amendment rules out `hpo-author` *because* "a direct push to `main` would give the author a path around review". The design gives the author that path through the secret.

**The main-protect bypass grants only force-push and deletion.**

- `main-protect` (22628467) has only the `deletion` and `non_fast_forward` rules (`ruleset-22628467.json`). A fast-forward push needs no bypass there.
- So the App's `always` bypass on 22628467 grants exactly the power to force-push and to delete `main`. The amendment says the writer is "never forced".

**What is true and what is not.** "Exactly this grant", "Target: main only, fast-forward, never forced" and "read only by `mutation-ledger-push`" are true of this workflow's YAML. They are not true of what the credential can do.

**The remedy is mostly tvofi's setup.**
- Move both secrets into an Actions environment whose deployment branches are `main` only, and declare `environment:` on `mutation-ledger-push`. That closes B1's credential half as well.
- Remove the App from 22628467's bypass list, unless the amendment records why it needs force-push and deletion.
- Correct the amendment so it states the credential's real reach.

### B3: two unpinned lines bound the push (test gap, on the push half)

- **`RESULT A2` survives** (`ALL 2065 ENTITY CHECKS PASSED`). The mutant drops `ref: main` from the push job's checkout and drops `&& git reset -q --hard origin/main`.
  - `drain_write_set_problems` reads `git status --porcelain`, which is only the working tree. The commits actually pushed (`origin/main..HEAD`) are bounded by those two YAML lines alone, and no check pins either.
  - Under A2, a branch dispatch pushes the branch's own commits to `main` over the bypass.
- **`RESULT A7` survives.** The mutant changes `if diff is not None and diff.returncode == 0` to `if diff is not None`.
  - An unreadable diff then yields `changed=[]`, and every pin is applied on a moved `main`. `apply_drained`'s own `None` arm (A6, killed) is pinned; the YAML that produces `None` is not.
- **`RESULT A3` survives** (`::add-mask::$tok` removed). This is low severity: nothing echoes the token today.

## What reproduces

These are my own runner (`mutants.py`, `run.sh`) and my own forms; each was applied in its own detached worktree at the head and run with `PYTHONPATH=tests/hastub tests/entities.py` (3.14 venv carrying `tests/requirements-ci.txt`, under this seat's root).

- **Unmutated head:** `ALL 2065 ENTITY CHECKS PASSED`, rc=0.
- **M0 (comment-only null):** `ALL 2065 ENTITY CHECKS PASSED`, rc=0.
- **Fixer's M1–M8:** each prints `1 of 2065 ENTITY CHECKS FAILED`, rc=1, on exactly the check the body names:

| Mutant | Check that fails |
|---|---|
| M1, M2, M3 | `--drain drives whole drivable anchors...` |
| M4, M5, M8 | `mutation-ledger-push applies a drained slice once...` |
| M6, M7 | `the ledger writer may only add killed_by rows...` |

- **My own:**
  - Killed:
    - A1: `pull_request` added to `mutation-ledger`'s `if:`. Fails "the reporter watches exactly the lanes a pull request cannot see".
    - A5: closure-directory match removed. Fails the apply check.
    - A6: `changed is None` treated as empty. Fails the apply check.
    - A9: `mutation-ledger` dropped from `REQUIRED_LANES`. Fails the reporter-lanes check.
  - Survived: A2, A3 and A7 (see B3).
  - The `a8:register_once` lines in every log are self-test fixture output in random order, not counted failures. Every rc and total above is the script's own.

**Push half on the real tree** (`push_harness.txt`):
- `RESULT stock 4520 3911 3911 3857` reproduces the body's figures. `RESULT slice20261002 40 anchors 40 whole True`.
- Synthetic pins for the whole slice: `apply1 changed`, 40 porcelain lines, write-set problems `[]`, `apply2 skip-unchanged`, and the porcelain is unchanged after the second apply.
- Moved head: from a 2026-09-25 commit, 2017 paths changed and 40 of 40 pins were dropped (`skip-head-moved`). From the merge base, 0 of 40 were dropped (B1).
- Null control: a README-only diff drops 0. An unreadable diff gives `skip-head-moved`.
- These are apply and filter figures only. I did **not** re-run the 40-site drive (the kill measurement): it needs `features.py` and the solver scripts, whose baseline fails on BLAS on this Mac. The `37 pinned, 3 left` figure is the fixer's, from `f3e2e445`, and I have not verified it.

**Contracts and checks:**
- `tests/structure.py`: `STRUCTURE RATCHET PASSED`.
- `node .claude/workflows/policy_lint.mjs`: `TOTAL: 0 error(s) across 40 policy file(s)`.
- `VERSION`, the manifest, `RELEASE_NOTES.md` and both claim files are untouched (three-dot).
- `git merge-tree --write-tree origin/main <head>` exits 0 against both `af7660c7` and `aab94eea`, the current main (#1849 merged; its fixture change is byte-identical to this PR's).
- The body's `## Head` names `4f594b42` (step 7).

**Amendment facts I confirmed live:**
- 5094721 is `always` on both rulesets.
- The fixture records it.
- `HPO_LEDGER_APPID` and `HPO_LEDGER_PEM` exist (set 13:12Z and 13:13Z).
- The loop-guard claim holds: `mutation-ledger` does not run on `push`.
- `stamp.py` treats a direct `ci:` push as an enumerator-only case (`unattributed_direct_pushes`) and does not refuse on it. A window holding only such pushes refuses the stamp (`enumeration_went_blind`), which is acceptable.

**Not this PR's to fix:** `docs/HANDOVER.md` still says the 22628467 bypass is undocumented and owed "ratify and document it or remove it". After merge that is the orchestrator's handover update; B2 bears on which half applies.

## Head CI (cited, not re-run)

Head check-runs at posting (`checks-at-post-*.json`): 19 success, 9 skipped, 1 cancelled (a superseded `budget-raise-gate`), 3 in progress, 0 failure.
- `Tests` run 37014445686 is still in progress.
- The code head's run 37013886509 is cancelled (superseded by the head run).
- No red check, so step 11 has nothing to answer yet. This verdict does not depend on that run.

## Head liveness

- Measured at `4f594b42635be021152dec6e3934af1a674cec52`.
- `gh pr view 1848` still reads that head at posting.
- `origin/main` moved to `aab94eea` (#1849) under the review. The PR head did not, so this is not head-moved.

## To clear

1. Add the main-ref guard (B1), and pin it plus A2's two lines and A7's returncode condition in the entities check (B3).
2. tvofi: move the secrets to a main-only environment, and remove or justify the 22628467 bypass (B2).
3. Make the amendment state the credential's reach as it actually is.
