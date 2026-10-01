<!-- ccr-projects-attribution: {"github_login":"tvofi"} -->
_Requested by **tvofi**_

Part of #201

Round-9 process change PROC-3: items 6 (its `prepr.sh` half), 7 and 5 of the process review tvofi adopted on 2026-10-01.

Before: a handoff body travelled as a commit above the code head under `tools/audit/handoff/`, and resume notes under `handoff/`, so any commit a seat added on top dragged them into the code head; reviewers found every instance. A fixer was told to write its own `docs/delivery/<N>.md` before the handoff, although only the orchestrator learns N when it opens the pull request. `prepr.sh` never ran its own `--self-test`, so a diff that made a row stale went red in CI's `governance` job instead (#1811).

After: `prepr.sh` step 1a refuses any commit since the merge base that adds or edits a file under `tools/audit/handoff/` or `handoff/`, and step 3h runs `prepr.sh --self-test` whenever the diff touches `prepr.sh`, a script path it names, or `.claude/workflows/fixtures/`. The body and any resume note go to an orphan ref, `handoff-body/<topic>`, through the new `tools/audit/seat/body_push.sh`, which appends fast-forward, so a re-bodied handoff needs no force-push and no `-vN` branch. `handoff_push.sh` reads `BODY.md` there first and falls back to the legacy transport commit while open handoffs still carry one. `fixer.md` and `delivery-status-tracking.md` now say the orchestrator writes the delivery row, which `handoff_push.sh` already did.

How: `transport_in_ancestry` reads `git log --full-history -c --diff-filter=ACMRT <base>..HEAD` over both roots. `--full-history` keeps a side branch whose add and delete cancel at a tree-identical merge. `-c` reads a merge's combined diff, which lists only a file matching none of its parents: a body written while resolving a merge of main is refused, and main's own files, which match main's parent, stay out. Deletions pass, so this branch can remove the stray F10.1d `BODY.md` main still carries. A range git cannot read is refused rather than passed. `selftest_owed` derives its inputs from `prepr.sh` itself (every tracked script path it names, plus the fixtures directory), so a new step needs no list kept in step.

**Item 5, the cloud setup script.** `tools/audit/seat/cloud-setup.sh` is a document: nothing in the tree runs it. tvofi pastes it into the project's environment setup script. It installs a current uv from PyPI (the image's uv 0.8.17 has no build past 3.14.0rc), then the interpreter version `tests/typing_budgets.json` records for the typing census (`census.environment.python`, 3.14.7 at this head; 3.14.2 is only `ruler.python_min`) through it, `venv-ci` from `tests/requirements-ci.txt` (first on PATH) and `venv-ha` from `tests/requirements-typing.txt` with `--no-deps`, as the `typing` job installs it (homeassistant and homeassistant-stubs 2026.9.3, mypy), exported as `HPO_TYPING_PYTHON`. The pins are read from the checkout and never restated. The tree-rewriting hooks are the `hiway-kit` plugin's `auto-format.py` (PostToolUse) and `stop-validator.py` (Stop), both running `ruff format` and `ruff check --fix`; they are synced from the account's plugin directory, so turning them off is an account or project settings change for tvofi, written up beside the script and not applied here.

**Item 6, F10.3's I1 ratchet.** It does refuse a new surviving site in CI, even when the total falls. `tests/mutation_table.py` `added_unpinned` keys unpinned sites by content (file, operator, stripped line text), and `main` refuses on `ratchet_refusal(...) == 1 or added` unless `--pin-killed` is passed. The `mutation` job in `.github/workflows/tests.yml` runs on `pull_request`. A surviving mutant has no killing driver to pin, so `mutation-autofix` cannot clear it: only a value check or a written survivor triage does. Retiring local `--pin-killed` in the briefs moved to PROC-1.

**Policy files.** `tools/audit/briefs/fixer.md`, `.claude/rules/delivery-status-tracking.md` and its generated `.cursor/rules/delivery-status-tracking.mdc`. Both source files are paid for inside their own caps: `fixer.md` drops the stale "Seats are LOCAL-ONLY" handoff sentence and compresses the landing paragraph, and no cap is raised.

## Head

96caaf6c8477b3fd962cd3de37613e0974ae410d

A merge of main 411368b6 (PROC-1, #1818) into the round-2 head eff1a2a3; no re-cut, rebase or force-push. `tools/audit/briefs/fixer.md` conflicted in two hunks. Step 5 keeps this branch's sentence (the orchestrator opens the PR as the `hpo-author` App) over main's "Seats are LOCAL-ONLY ... hand the branch and body off locally", which the orphan body ref replaces. The landing paragraph takes main's wording, since PROC-1's merge-not-recut paragraph supersedes this branch's "only merge that ever was" clause. PROC-1 left `fixer.md` at exactly its 4585-token cap, so this branch's step 5 and step 6 additions are recompressed to land at 4585/4585 and 278/280 lines; no cap is raised. Everything else merged cleanly.

Round 1 was blocked at e95150fa (refusal-bypass): `--no-merges` never read a merge commit's own diff, so a body added in a conflict resolution passed step 1a. 6a4a4675 answers it with `-c` and a self-test row, and the same round reads the interpreter version from `tests/typing_budgets.json`, moves the ruff removal above the missing-checkout exit, and adds `counts.mjs` and `render_md.mjs` to the self-test inputs.

Merge base: main 411368b6. The body travels on `handoff-body/r9-proc-3`, built by `body_push.sh`, so the code head carries no transport.

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
- `-c` replaced by `--no-merges` (the round-1 head): FAIL \"transport: a body written in a merge's own resolution is refused (got 0, wanted 1)\"; 145 passed, 1 failed.
- `-c` replaced by `-m`: FAIL \"transport: merging a main that carries a transport file passes (null control) (got 1, wanted 0)\"; 145 passed, 1 failed.
- the explicit `counts.mjs` / `render_md.mjs` line deleted: 146 passed, 0 failed, an equivalent mutant. `selftest_inputs` derives every script path named anywhere in `prepr.sh`, and the self-test row that checks the two modules names them, so the derivation still finds them; the explicit line stays so the list does not depend on a row's wording.

## Null control

The unmodified head: `bash tools/audit/prepr.sh --self-test` prints 146 passed, 0 failed. At main 90335cbd it prints 129 passed, 0 failed; the 17 added rows are eight transport rows (three null controls among them) and nine `selftest_owed` rows (one null control). Each refused transport shape has a passing twin in the same throwaway repository: `clean` (a base carrying a transport file), `tidy` (deleting one) and `merged` (merging a main that carries one).

## Figures

- `bash tools/audit/prepr.sh --self-test` at this head (96caaf6c): 146 passed, 0 failed; at 90335cbd: 129 passed, 0 failed.
- `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"`: `MODE: SCOPED -- 0 script(s) run`; every changed path is INERT or policy.
- `python3 tests/structure.py`: STRUCTURE RATCHET PASSED.
- `PYTHONPATH=tests/hastub python tests/entities.py` (venv-ci from `cloud-setup.sh`): ALL 2026 ENTITY CHECKS PASSED.
- `node .claude/workflows/policy_lint.mjs`: TOTAL 0 errors; `--budgets` prints every capped file within its cap (`fixer.md` 278/280 lines, 4585/4585 tokens; `delivery-status-tracking.md` 603/606 tokens).
- `node .claude/workflows/rules_sync.mjs --check`: RULES-SYNC ok.
- `HPO_KEEP_RUFF=1 HPO_REPO=$PWD HPO_PREFIX=<scratch>/opt-hpo2 HPO_PROFILE=<scratch>/hpo-profile2.sh bash tools/audit/seat/cloud-setup.sh` at eff1a2a3: rc 0, 1 min 31 s wall with pip's cache warm (11 min 22 s cold at 73f33f93); `venv-ha` runs Python 3.14.7. The image's own uv 0.8.17 refused 3.14.2 with "No download found for request: cpython-3.14.2-linux-x86_64-gnu", which is why the script installs a current uv first. `HPO_KEEP_RUFF=1` kept this container's ruff, so the ruff loop was exercised only on a throwaway `ruff` on PATH.
- `<scratch>/opt-hpo2/venv-ha/bin/python tests/ha_contract.py --contracts-only`: ALL 61 contracts PASSED against real Home Assistant 2026.9.3 on Python 3.14.7, in this cloud container.

## Red checks

none

## Forward-carry

`tools/audit/briefs/fixer.md` step 6 carries the orphan-ref rule and the delivery-row hand-over to every fixer. The coordinator's out-of-tree brief add-on that still says to push the body as a transport commit under `tools/audit/handoff/<topic>/` is sent to the coordinator to replace with `body_push.sh`.

## Friction

none
