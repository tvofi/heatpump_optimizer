<!-- ccr-projects-attribution: {"github_login":"tvofi"} -->
_Requested by **tvofi**_

Part of #201

Round-9 process change PROC-3: items 6 (its `prepr.sh` half), 7 and 5 of the process review tvofi adopted on 2026-10-01.

Before: a handoff body travelled as a commit above the code head under `tools/audit/handoff/`, and resume notes under `handoff/`, so any commit a seat added on top dragged them into the code head; reviewers found every instance. A fixer was told to write its own `docs/delivery/<N>.md` before the handoff, although only the orchestrator learns N when it opens the pull request. `prepr.sh` never ran its own `--self-test`, so a diff that made a row stale went red in CI's `governance` job instead (#1811).

After: `prepr.sh` step 1a refuses any commit since the merge base that adds or edits a file under `tools/audit/handoff/` or `handoff/`, and step 3h runs `prepr.sh --self-test` whenever the diff touches `prepr.sh`, a script path it names, or `.claude/workflows/fixtures/`. The body and any resume note go to an orphan ref, `handoff-body/<topic>`, through the new `tools/audit/seat/body_push.sh`, which appends fast-forward, so a re-bodied handoff needs no force-push and no `-vN` branch. `handoff_push.sh` reads `BODY.md` there first and falls back to the legacy transport commit while open handoffs still carry one. `fixer.md` and `delivery-status-tracking.md` now say the orchestrator writes the delivery row, which `handoff_push.sh` already did.

How: `transport_in_ancestry` reads `git log --full-history --no-merges --diff-filter=ACMRT <base>..HEAD` over both roots. `--full-history` keeps a side branch whose add and delete cancel at a tree-identical merge, `--no-merges` keeps main's own files out of a merge's first-parent diff, and deletions pass, so this branch can remove the stray F10.1d `BODY.md` main still carries. A range git cannot read is refused rather than passed. `selftest_owed` derives its inputs from `prepr.sh` itself (every tracked script path it names, plus the fixtures directory), so a new step needs no list kept in step.

**Item 5, the cloud setup script.** `tools/audit/seat/cloud-setup.sh` is a document: nothing in the tree runs it. tvofi pastes it into the project's environment setup script. It installs a current uv from PyPI (the image's uv 0.8.17 has no 3.14.2 build), Python 3.14.2 through it, `venv-ci` from `tests/requirements-ci.txt` (first on PATH) and `venv-ha` from `tests/requirements-typing.txt` with `--no-deps`, as the `typing` job installs it (homeassistant and homeassistant-stubs 2026.9.3, mypy), exported as `HPO_TYPING_PYTHON`. The pins are read from the checkout and never restated. The tree-rewriting hooks are the `hiway-kit` plugin's `auto-format.py` (PostToolUse) and `stop-validator.py` (Stop), both running `ruff format` and `ruff check --fix`; they are synced from the account's plugin directory, so turning them off is an account or project settings change for tvofi, written up beside the script and not applied here.

**Item 6, F10.3's I1 ratchet.** It does refuse a new surviving site in CI, even when the total falls. `tests/mutation_table.py` `added_unpinned` keys unpinned sites by content (file, operator, stripped line text), and `main` refuses on `ratchet_refusal(...) == 1 or added` unless `--pin-killed` is passed. The `mutation` job in `.github/workflows/tests.yml` runs on `pull_request`. A surviving mutant has no killing driver to pin, so `mutation-autofix` cannot clear it: only a value check or a written survivor triage does. Retiring local `--pin-killed` in the briefs moved to PROC-1.

**Policy files.** `tools/audit/briefs/fixer.md`, `.claude/rules/delivery-status-tracking.md` and its generated `.cursor/rules/delivery-status-tracking.mdc`. Both source files are paid for inside their own caps: `fixer.md` drops the stale "Seats are LOCAL-ONLY" handoff sentence and compresses the landing paragraph, and no cap is raised.

## Head

e95150fad380dcac184d5fa8c9d4a9140f13c125

Merge base: main 90335cbd (#1811). The body travels on `handoff-body/r9-proc-3`, built by `body_push.sh`, so the code head carries no transport.

## Approval

Owed before merge: tvofi's approving review at this head. `tools/audit/prepr.sh` and `tools/audit/briefs/fixer.md` are code-owned, and `fixer.md` and `.claude/rules/delivery-status-tracking.md` are policy.

## Mutation proof

Each mutant applied to the committed `tools/audit/prepr.sh`, then `bash tools/audit/prepr.sh --self-test`, then restored:

- `--full-history` removed: FAIL "transport: a resume note hidden behind a tree-identical merge is refused (got 0, wanted 1)"; 141 passed, 1 failed.
- `--diff-filter=ACMRTD` (deletions counted): FAIL "transport: deleting a transport file main carries passes (null control) (got 1, wanted 0)"; 141 passed, 1 failed.
- the empty-output test replaced by `return 0`: FAIL on the three refused shapes (above, cancelled, side); 139 passed, 3 failed.
- the directory-prefix arm of `selftest_owed` disabled: FAIL "a change to a fixture owes the self-test (got 1, wanted 0)"; 141 passed, 1 failed.
- `TRANSPORT_ROOTS` without `handoff/`: FAIL "transport: a resume note hidden behind a tree-identical merge is refused (got 0, wanted 1)"; 141 passed, 1 failed.
- the range `$1..$2` widened to `$2`: FAIL on both null controls (clean, tidy); 140 passed, 2 failed.

## Null control

The unmodified head: `bash tools/audit/prepr.sh --self-test` prints 142 passed, 0 failed. At main 90335cbd it prints 129 passed, 0 failed; the 13 added rows are the six transport rows (two null controls among them) and seven `selftest_owed` rows (one null control). Each refused transport shape has a passing twin in the same throwaway repository: `clean` (a base carrying a transport file) and `tidy` (deleting one).

## Figures

- `bash tools/audit/prepr.sh --self-test` at this head: 142 passed, 0 failed; at 90335cbd: 129 passed, 0 failed.
- `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"`: `MODE: SCOPED -- 0 script(s) run`; every changed path is INERT or policy.
- `python3 tests/structure.py`: STRUCTURE RATCHET PASSED.
- `node .claude/workflows/policy_lint.mjs`: TOTAL 0 errors; `--budgets` prints every capped file within its cap.
- `node .claude/workflows/rules_sync.mjs --check`: RULES-SYNC ok.
- `HPO_REPO=$PWD HPO_PREFIX=<scratch>/opt-hpo HPO_PROFILE=<scratch>/hpo-profile.sh bash tools/audit/seat/cloud-setup.sh` at 73f33f93 (the script before `--no-bin` and the ruff removal were added): rc 0, 11 min 22 s wall; venv-ha imports homeassistant 2026.9.3 and mypy 2.3.1, venv-ci runs Python 3.14.2 with numpy 2.4.6 and scipy 1.17.1. The image's own uv 0.8.17 refused with "No download found for request: cpython-3.14.2-linux-x86_64-gnu", which is why the script installs a current uv first. The two later additions are not re-run end to end: `--no-bin` only stops uv writing `~/.local/bin`, and the ruff loop was exercised on a throwaway `ruff` on PATH.
- `<scratch>/opt-hpo/venv-ha/bin/python tests/ha_contract.py --contracts-only`: ALL 61 contracts PASSED, ALL 4 convention checks PASSED, against real Home Assistant 2026.9.3 in this cloud container.

## Red checks

none

## Forward-carry

`tools/audit/briefs/fixer.md` step 6 carries the orphan-ref rule and the delivery-row hand-over to every fixer. The coordinator's out-of-tree brief add-on that still says to push the body as a transport commit under `tools/audit/handoff/<topic>/` is sent to the coordinator to replace with `body_push.sh`.

## Friction

none
