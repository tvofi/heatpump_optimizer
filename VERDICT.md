Fix review: merge c32e90ddd730ae1a2fc85a44a52cdbe159fff08f

bus-nonce: 36eb859a4f11d51bad50bc801eab4439

Measured at **c32e90ddd730ae1a2fc85a44a52cdbe159fff08f** — the PR's live `headRefOid` at the time of writing — in a detached worktree at that sha (`/Users/timmalmstrom/hpo-seats/r9-review-2083/wt`), merge base `origin/main` = `7cd5a588c`. Evidence: `/Users/timmalmstrom/hpo-seats/r9-review-2083/evidence/`. The diff is exactly the three files the brief names.

## Head state (API, not `gh pr checks`)

- 39 distinct check-run names, every one `completed`; none `failure`, `cancelled` or timing out — `checkruns-head.tsv`.
- All **17** required contexts of ruleset `23698884` present at the head (re-read from the ruleset, `checkruns-head-summary.txt`); **zero absent**.
- 8 workflow runs at the head, all `pull_request`, all `success`.
- `mergeStateStatus: BLOCKED` is `reviewDecision: REVIEW_REQUIRED` alone (`mergeable: MERGEABLE`).
- `git merge-tree --write-tree origin/main HEAD` → rc 0, no conflicting path and no `MERGE-CLAIM` line.
- `VERSION` 6.7.17 at both ends; both claim files byte-identical to main; `MODE: SCOPED -- 0 script(s) run, 33 scoped out` over exactly these three files.

## Mutation proof — reproduced, per harness

`ci-watch.sh` (suite 8): MW1 delete the `comm -23` arm → exactly `1 failed`, the named W1; MW2 delete `[ "$pending" = 0 ]` → exactly `1 failed`, the named W3; MW3 delete the reds `sort` → exactly `1 failed`, the named W4. `merge_train.py` (suite 98): M1 delete the refusal in `one()` → the one named check; M2 delete it in `admit()` → the one named check; M3 neuter `bot_tip` to `None` → **both** named checks, `2 failed` (the bot-head-behind-main null control correctly still passes). Restored: 98/0 and 8/0. Baseline at `origin/main` `7cd5a588c`: **95 checks, 0 failed** — the body's "95" holds.

## Null control — the two-ends detector, re-run by me on the real input

The body's arm A/B is the load-bearing control and its input is re-derivable, so I did not take it on trust. `7656ef0d4f42cb7490de31a3c9410ad04e89a725` is exactly what `gh api .../commits/63084989…/check-runs --jq '.check_runs[]|[.name,.status,.conclusion,.started_at]|@tsv'` prints today (`checkruns-63084989.tsv`, 30 lines); the v2 baseline `58e1ba8f…` is `origin/main`'s file. Driving both watchers over a fake `gh` (mine, disclosed) on that one input, arm A: v2 prints only `RED: mutation nightly-ha (stable)`, v3 prints that plus the five `ABSENT` names. Arm B (every conclusion forced `success`): v2 prints **nothing and is still looping** after a 6 s bound; v3 exits 1 naming the five. Both claims reproduce, verbatim in `null-control-two-ends.txt`.

## Every other figure re-derived

Fig 1 (17 contexts) ✓; Fig 2–4 (bot heads `63084989`/`a9ba0b88`: 4 dispatch runs, **0** `pull_request`, 30 names, the same 5 absent; recovery `386b7e2f`: 9 runs all `pull_request`, 39 names, none absent) ✓; Fig 6 (pin 08:32:06Z → recovery 17:24:10Z = 8 h 52 m; #2070 still OPEN at `a9ba0b88`) ✓; Fig 7 (`git log origin/main --grep` → 26) ✓; Fig 8 (98/0, 8/0) ✓; Fig 10 `STRUCTURE RATCHET PASSED` ✓; Fig 11/12/13 ✓; Fig 14 (`workflow_dispatch` at `governance.yml:44`; absent from `pr-contract.yml` and `budget-raise-gate.yml`'s `on:`) ✓; Fig 15 (both sha1s) ✓. The self-test's `PRESENT12` is exactly `required ∩ names@63084989`.

## Reported, not blocking

1. **One cell of the premise table is wrong.** Row `386b7e2f…`, column *latest-per-name not green*, reads `—`; it is `mutation` (`completed/failure`, run 37977804238). The row's own claim — all five contexts PRESENT there — is true; only that cell is not. I could not re-derive it as written.
2. **The two-ends companion driver lives only in scratch** (`/Users/timmalmstrom/hpo-seats/autofix-governance/scratch/companion/driver.sh`), which `fixer.md` 18 routes into the PR. The body discloses it and `figure_lint` reports it unverified; I rebuilt the run above so the claim no longer rests on it.
3. **Forward-carry.** Item 1 (the measured arm-A loss, with its control and its precondition) is in the tree at its named destination — R9-CI-1's roster brief, landed at `6a2ab7968` on `handoff/audit-r9-fixplan`; I read it back and it carries the 3-of-5 measurement and "may not spend its budget on it". Items 2–4 are routed to the orchestrator/owner rather than written: `dev/governance/rules/ci-autofix.md`'s held-run sentence is **not** corrected in this diff (policy, owner's), and neither `dev/programme/HANDOVER.md` nor any roster brief or carry file carries the record-lane half or the live #2070 instance. If the merge-time record obligation does not pick items 2–4 up, they evaporate with this body.

## Not measured

`tests/env_drift.py --all` was not run (heavy, ~345 s on a loaded box): the diff's file list is three `tools/audit/seat/` files, so no fixture is reachable, and the claim files and `VERSION` are byte-identical to main — the conclusion is derived, not measured. `prepr.sh` (Fig 9) was not re-run; its contract half is evidenced instead by `pr-contract` being green at the head.
