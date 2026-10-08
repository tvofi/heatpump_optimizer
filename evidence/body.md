The root-cause seat for #2028 (`root-cause-unanswered`, recurring). It found that the contract's red-history check does not run in CI, and this PR fixes that.

#1144 added a red-history arm to `pr-contract`. The arm names a red that sits on an earlier commit of the branch. It reads check runs through the API, and it skips when it has no token. The step that runs it, "Check the body against the contract", has no token in its `env:` in any of the 65 workflow revisions that carry it, from a07dd57d (where the arm landed, 2026-09-19) to `origin/main`. All 35 `pr-contract` logs at this round's 19 `root-cause-unanswered` heads print `skip red-history`. #2053 shows the cost. Its body did not name a `closures` red one commit below an autofix head. CI passed it at push. The reviewer blocked on the same red 75 minutes later. With a token, the same program refuses that body at push.

The fix is one `env:` line, `GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}`, on that step. The program it runs is still the base's restored copy, and the job's grants are still reads only. `tests/entities.py` pins the line, with a null control. The analysis is `dev/audit/rca/R9-RCA-2028.md`, with evidence under `dev/audit/rca/2028/`. It covers the cause, process state (c), the cost test, two candidates refused, and one owner decision proposed but not landed.

A second fix is in the same rule. `tools/pr/prepr.sh`'s `body_check` did not pass `--existing-file`. Because of that, `policy_lint` counted the pull request's own new delivery row as a touch of what `delivery-status` reads, and refused a main-graded red that `pr-contract` exempts. This PR's own `open_pr.sh` row push was refused that way. `body_check` now passes the base's paths (`--diff-filter=a`), as the contract does. `prepr.sh --self-test` pins this with a null control.

Closes #2028

## Head

`5964b5836ca3fbaa041964e1c33943b8b852e964` merges the authored code head `3eb8d53a5ae8fb9675426e65b8e15bf61d094474` and then merges origin/main `b296779f0` (an automatic merge by the orchestrator's script; any resolution inside the code head is described below) into this PR's previous head.

The authored code head is `3eb8d53a5ae8fb9675426e65b8e15bf61d094474`. Every local figure below was measured at that head unless it names another commit.

## Mutation proof

Removing the fix's one production line (the `GH_TOKEN` env line) is the tree at `origin/main` `4647321d` plus the new pin. There, `tests/entities.py` reports `1 of 2214 ENTITY CHECKS FAILED`, and the one failure is `the body check holds a token, so red-history is read rather than skipped`. At the head, it reports `ALL 2214 ENTITY CHECKS PASSED`.

Behaviour, replayed on #2053's graded body (section 3 of the RCA). Without a token, `policy_lint.mjs --pr-body` prints `skip red-history` and `PR-BODY: 0 error(s)`. With `GH_TOKEN` it prints ``check `closures` is red and `## Red checks` does not name it`` and exits 1.

For `prepr.sh`: at `af5560f8`, which has the self-test arm but not the fix, `prepr.sh --self-test` reports `211 passed, 1 failed`. The one failure is `pr-body exempts a main-graded red when the diff only ADDS its own delivery row`. At the head it reports `212 passed, 0 failed`. With the fix's `args+=(--existing-file "$ex")` line replaced by `:` at the head, it reports `211 passed, 1 failed`, the same failure.

## Null control

- The pin's own control is `and the same step with its token removed is not (null control)`. It is `ok` at both trees, so the predicate reads the env line and not the step's name.
- `prepr.sh`'s control is `and still owes it when the diff edits a row the base had (null control)`. It is `ok` before and after the fix, so the exemption does not widen to a row the base already had.
- Behaviour: with a token, the same program on #2053's body as answered at 10:55Z prints `record red-history ... closures, delivery-status, fast (3.14)` and `PR-BODY: 0 error(s)`. The arm reads the history, refuses nothing the body answers, and does not pass by skipping.

## Figures

- Entity checks, 1 failed before and 2214 passed after: `PYTHONPATH=tests/hastub python3 tests/entities.py` (Python 3.14 seat venv).
- `prepr.sh` self-test, 211/1 before the fix, 212/0 at the head, 211/1 with the fix line neutralised: `bash tools/pr/prepr.sh --self-test`.
- `tests/layout.py` passes at the head (rc 0) and is refused at `a703959f` (rc 1, one `new-reference`), about 10 s here: `python3 tests/layout.py`.
- `STRUCTURE RATCHET PASSED`: `PYTHONPATH=tests/hastub python3 tests/structure.py`.
- Policy corpus `TOTAL: 0 error(s)`: `node tools/policy/policy_lint.mjs`.
- Scoped gate selection is `MODE: SCOPED -- 2 script(s) run`: `python3 tests/closure.py select --files <the diff's paths>`. `tests/harness_headers.py` is left to CI's run at this head under the heavy-scripts rule.
- 65 revisions of the step, 0 with a token: for each commit in `git log a07dd57d3^..origin/main -- .github/workflows/governance.yml .github/workflows/pr-contract.yml`, the step's `env:` read with `git show <c>:<file>`.
- Replay of #2053, about 0.59 s without the history walk and 5.56 s with it: `node tools/policy/policy_lint.mjs --pr-body <body> --head 6ddb8c4c44d2851dabf6f9f3c19baa1d815d9dbf --red delivery-status`, in a standalone clone with `origin/main` at `470bbd60`.
- 19 `root-cause-unanswered` verdicts on 12 PRs, classes A/B/C/D, and 7 body-only repairs totalling 574 min: `dev/audit/rca/2028/` (the RCA's section 7 names each command).

## Red checks

- `fast (3.14)` was red at `e6e5aea7` (job 113385312852). That was this PR's own red. The always-run `tests/layout.py` refused af5560f8's new self-test fixture line in `tools/pr/prepr.sh` as `new-reference ... cites retired path docs/delivery/`: it wrote `docs/delivery/9999.md`. The fixture now builds its own rows under `dev/programme/delivery/` (branches `rowadd` and `rowedit`), and `tests/layout.py` passes at this head. The cheaper detector is `python3 tests/layout.py`. It takes about 4 s on CI's venv and 10 s here, and it was in no path this seat ran before pushing. It is not in `prepr.sh`, and the scoped selection named only `entities.py` and `harness_headers.py`. The standing cost of running it at every push is those seconds. This seat's push gate did not include it, and that was the miss.
- `nightly-status` was red at `e6e5aea7`, and `delivery-status` and `nightly-status` were red at `539d300b`. Both grade `main`. The only reporter input this diff touches is its own new row, `dev/programme/delivery/2062.md`, which the exemption excludes. They are main's reds, so there is no cheaper detector to name. The `prepr.sh` fix above is what stops the push-time check from refusing them.
- `closures` was green at `e6e5aea7`.

## Forward-carry

The proposed owner decision (hold a `root-cause-unanswered` verdict until the newest `pr-contract` at a settled head has re-graded the body; RCA section 6, item 3) is recorded in `dev/audit/rca/R9-RCA-2028.md`. It changes `fix-review.md` step 11, which is policy, so it is not landed here.

## Friction

none

🤖 Generated with [Claude Code](https://claude.com/claude-code)

