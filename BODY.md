_Requested by **tvofi**_

R9-F11.4: the I4 barrier, an agreement lane over each concept's real readers, and the owed driver fixes.

Fixes #1650 (I4)
Part of #201

Before: class I4 ("two independent parsers or definitions of one concept disagree") had 26 instances across rounds 2 to 9 and no barrier. Round 9 added D14-s2-03 (`audit-find.js`'s `CLASS_GUESS` was a grammar standing in for the class list), D13-s1-01 (`resolvePrFromCommit` read one of the two merge-subject shapes), D11-s1-72 (`tests/entities.py`'s governance-workflow pin read one file) and D7-s3-02 (`dead_methods` agreed with nothing).

After: `.claude/workflows/agreement.mjs` runs each registered concept's real readers over one corpus of live instances plus the findings' boundary cases, and refuses any disagreement, a reader that throws, an empty corpus, or a live merge commit that every reader answers null for. Grammar discovery refuses a regex source written in two or more governance code files unless it is registered with a disposition, and a stale entry is DEAD. Six pairs are registered: `rule-frontmatter-paths`, `finding-class-id`, `merge-subject-pr`, `dead-member-liveness`, `governance-workflow-jobs` and `entity-names`. The Python readers run first under `python3 -I` (`agreement_py.py`, restored from the base by CI) and hand their answers to `agreement.mjs` as JSON. The lane runs in the `wave-script` job of `governance.yml`, and its `--self-test` runs in `instrument-self-tests`. `tools/audit/bugclasses.json` marks I4 `barriered`.

Carried into this PR by the roster: the N-silent-zero census arm in `field_coverage.mjs` (structure.py's `dead_methods` and `dead_top_level_symbols` get one planted member each and the count must rise by one); `merge_shape_guard` as a lane check; the two #1721 review mutants pinned (`policy_lint_envmatrix.mjs`); the driver `Prepare` fixes in `audit-find.js` and `prepare_baseline.sh`; `scopes.json` and the README line naming `scopes.json` and `check_scopes.py`.

Accepted and declared, not built (tvofi's card C11): a second reader with a different grammar for a concept nobody registered stays undetected beyond the A7 and A8 policy text, which is F11.5's. `policy_lint.mjs`'s offline subject mode reads the squash shape only (`enumSkipLine`), a registered narrow declaration. Disclosed: the `governance-workflow-jobs` pair re-derives `entities.py`'s `_workflow_job_ids` by regex in `agreement_py.py`, a copy of a three-line job-id scan, registered as an `identical:` grammar and null-controlled by the `briefs` job. `structure.py`'s counting-rule self-check, not the `dead-member-liveness` pair, is what detects a bare-name-load liveness rule coming back (D7-s3-02); the pair's boundary probe detects a reader that stops finding dead members.

Not in this diff, for the reviewer: `tools/audit/round9/D14/sweep/I4/enumerate.py` and the D11 and D7 harnesses it calls are outside the tree, so the step-8 enumeration ran from an export (see Figures).

## Round-1 review items

Review prep note: `handoff/round9/fix/resume/F11.4-review.md` on `handoff/r9-f11-governance-4-review` (a07917865, measured at e35026f6).

| round-1 item | where fixed | measured at this head |
|---|---|---|
| 1 BLOCKING: `codeowners_gap.py --check` uncovered 9, rc 1 | 37b1d3038 moves the lane's Python readers into `agreement_py.py`, run by `governance.yml` under `python3 -I`, so `agreement.mjs` no longer loads `structure.py`, `entities.py` and the other eight files itself | `RESULT uncovered_files=0` |
| 2: `dead-member-liveness` class-granular, no boundary case | 2391db77 adds a probe module to the corpus (a class whose members only call each other, and one a live function reaches), and `agreement.mjs` prints the pair's 138 items | control: `dead = sorted(...)` replaced by `dead = []` in `structure.dead_members` gives `divergent=1` on the probe; the unmutated lane gives 0 |
| 2 (disclosure half): which instrument detects D7-s3-02 | this body, third paragraph above, and the I4 `barrier` text | stated |
| 3: `governance-workflow-jobs` reads a copy | 2391db77 registers the job-id scan in `agreement.mjs`'s grammar registry as `identical:`, and says so in the I4 `barrier` text | disclosed above, with the null control named |
| 4: `bugclasses.json` I4 `barrier` lists five pairs, the lane has six | 2391db77 adds `entity-names` | `barrier` text names six; `agreement.mjs` prints six pairs |
| owed at handoff: steps 7, 10 to 13, enumerator, carry | this body and its prepr run | Figures, Red checks, Forward-carry |

## Head

`b05c2a19f24ce514a1f29e9c757038387b2ee9e5` merges the precursor `07b0704b82b57f6c60bdccd1a0e293d51ec09305` (handoff/r9-f11-governance-4-pre: `resolvePrFromCommit` reads both merge shapes, `rulePaths` exported; itself two commits on origin/main `af7660c749a65762934d45b7c91957102253e209`) into `f6af0c50c47ec3e0d1d6de12e85635eb2cc3d9ca` (this PR's head, which carries its delivery row), with no conflict. Two merges and one commit of mine make up the difference: `6edcbaaa` merged the precursor's first head `9d03708b` and made the `agreement lane` step in `governance.yml` skip, with its reason printed, while the base lacks the lane; `b05c2a19` merges the precursor's second head, which replaces a frontmatter regex the lane's own grammar discovery refused in the precursor's first test.

The earlier history: `d0c761b5` merged main `2b6c5b87` (#1838) into `2391db77`; `e166a15a` registered the lane's three pinned files in `field_coverage.mjs` and named `tests/structure*` by glob in the field-coverage skip guard; `4a3b49de` added the `agreement lane` step to `tools/audit/prepr.sh`.

## Mutation proof

Each round-9 instance re-introduced as a mutant, the lane run, the mutant restored (`git status --short` empty after each):

| instance | mutant | lane |
|---|---|---|
| D14-s2-03 | `CLASS_GUESS` back to `/^([PI][0-9]+\|new)$/` in `audit-find.js` | red, `finding-class-id` 15 divergent (12 `N-*` ids refused, 3 phantom ids accepted) |
| D13-s1-01 | `resolvePrFromCommit` reads `MERGE_SUBJECT_RE` only | red, `merge-subject-pr` 405 divergent |
| D11-s1-72 | `_GOV_FILES = [_GOV_WF]` in `tests/entities.py` | red, `governance-workflow-jobs` 4 divergent |
| D7-s3-02 reader gone | `structure.dead_members` returns `dead = []` | red, `dead-member-liveness` 1 divergent (the probe) |

Each mutant touches the predicate the pair reads, not a line past a return.

## Null control

The unmutated tree: `RESULT divergent=0 unregistered=0 dead=0 refused=0`, rc 0, six pairs, 107 governance code files, 27 grammars shared by two or more files, all of them registered. The same lane in `--self-test` holds 13 of 13 probes, among them a grammar in one file (not shared), a registered entry that no longer spans two files (DEAD) and a disposition of no known kind (refused). With no `--py-json` the three Python-backed pairs are REFUSED rather than skipped.

## Figures

- Lane, six pairs, 0 divergent: `python3 -I .claude/workflows/agreement_py.py --out "$X/agreement.json" && node .claude/workflows/agreement.mjs --py-json "$X/agreement.json"`
- Lane self-test, 13 of 13: `node .claude/workflows/agreement.mjs --self-test`
- Census arm, `dead_methods` 0 to 1 and `dead_top_level_symbols` 1 to 2 with one planted member each: `node .claude/workflows/field_coverage.mjs --only census`; self-test: `node .claude/workflows/field_coverage.mjs --self-test`
- codeowners surface, uncovered 0: `python3 tools/audit/round6/D11/fix/codeowners_gap.py --check`
- Field coverage, 0 refused: `node .claude/workflows/field_coverage.mjs`
- Structure ratchet: `python3 tests/structure.py`
- Policy: `node .claude/workflows/policy_lint.mjs`, `node .claude/workflows/policy_lint.mjs --budgets`, `node .claude/workflows/rules_sync.mjs --check`, `node .claude/workflows/check-wave-script.mjs` (151 passed, 0 failed)
- Scoped gate, `MODE: SCOPED`, two scripts run (`tests/entities.py`, `tests/harness_headers.py`): `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)`. Run in a venv with numpy at this head: `tests/harness_headers.py` 94 of 94 pass; `tests/entities.py` 1 of 2060 fails, `the template arm turns the acceptance red ...`, which is the live-ruleset read (`required-contexts` fixture against the live `main-protect-checks` ruleset) and fails identically at pristine `af7660c7`.
- Step-8 enumeration, class I4 seams at `origin/main` 2b6c5b87 and at this head, from an export of each tree overlaid with `origin/handoff/audit-r9-evidence` and `origin/handoff/audit-r9-sweep-s4`: `PYTHONPATH=tests/hastub python3 $EXPORT/tools/audit/round9/D14/sweep/I4/enumerate.py` run with `$EXPORT` as the working directory (sha1 `a9dad811c7ac3d7dda3dbd4dafdcd73560850d62`, `figure_lint` reports it unverified). Rule: it re-runs the four offline finder harnesses and greps `CLASS_GUESS` readers. Result: `dead_methods=0` at both ends (D7-s3-02 closed at base by #1838, guarded here by the pair and the census arm); `i4_reader_sites` 34 at base and 44 at head, the added sites being the registered lane readers; the `CLASS_GUESS` readers are the three-reader `finding-class-id` pair. D11-s1-71 and D11-s1-72 harnesses error at both ends (`eFrontmatter is not defined`, `_GOV_JOBS = _workflow_job_ids(_DS_GOV)` not found), because their text is keyed to source that F11.1 rewrote; the pairs `rule-frontmatter-paths` and `governance-workflow-jobs` are their live detectors. D13-s1-01 needs a live window and is cited from `tools/audit/round9/D13/s1/REPORT.md` as the enumerator says. Disposition: every returned seam is closed in this diff or already guarded; none is a new finding.

## Red checks

Three required checks went red on `f6af0c50`, which this body had said had no CI run. Causes:
- `wave-script`: CI restores `.claude/workflows/*.mjs` and the Python readers from the base, so the lane ran over main's readers. `REFUSED rule-frontmatter-paths: pl.rulePaths is not a function` (main's `policy_lint.mjs` did not export it) and `DIVERGENT merge-subject-pr "fix: a squash (#1234)"` (main's `resolvePrFromCommit` read one shape, D13-s1-01). Both are fixed on main by the precursor (handoff/r9-f11-governance-4-pre), which this head merges in, and the step now skips with a printed reason while the base lacks `agreement.mjs`. Cheaper detector: none that is cheap. `tools/audit/prepr.sh`'s `agreement lane` step runs this PR's own readers, so it passes locally while CI's pinned copy fails; recorded in Friction, no countermeasure built.
- `policy-docs`: EXPECTED, a bootstrap red. Main's base-pinned `field_coverage.mjs` lacks the three DECLARED entries (`agreement.mjs`, `agreement_py.py`, `tests/structure.py`), and they cannot go to main first: alone on main they are DEAD (`DECLARED ... is no longer in the derived set`, measured at `af7660c7`), because the pins they describe arrive in this PR. Any PR that extends the pinned list meets the same red. tvofi merges past it with `--admin` (ruling of 2026-10-02). No cheaper detector exists for a registry entry that is valid only alongside its pin.
- `pr-contract`: it named `wave-script` as red and unanswered; this section answers it.

Local `tools/audit/prepr.sh` at this head refuses `policy_lint`, `mutants` and `field coverage` for a cause outside this diff: the live `main-protect-checks` ruleset (23698884) no longer matches `.claude/workflows/fixtures/required-contexts.json` in `bypass_actors` (5 `required-contexts` errors), and the same 5 errors print at a pristine `af7660c7` checkout. These read the live ruleset through `gh`, so CI's runs read the same live ruleset; whether CI's `policy-docs` also shows it is the orchestrator's to read.

Expected to remain red on this PR: `policy-docs` only (the bootstrap), and anything the live-ruleset drift above turns red in `policy-docs`. `budget-raise-gate` does not apply, since no budget file moves.

## Approval

Not yet given. This diff touches policy and code-owned paths: one line in `tools/audit/README.md`, `.github/workflows/governance.yml` and `.claude/workflows/audit-find.js`. It merges only on tvofi's approving review at the head; the orchestrator requests it. No approval is claimed here.

## Forward-carry

- `tools/audit/bugclasses.json`: the I4 entry's `barrier` text records the lane's one limit, a second reader with a different grammar for an unregistered concept ("Not reached"), which is the A7 and A8 policy text of R9-F11.5. The F11.5 roster group lives on `handoff/audit-r9-fixplan`, not in this tree, so the destination checked here is the ledger entry.

## Friction

- `gate-scoping: contradiction`: `tools/audit/prepr.sh`'s `agreement lane` step (and its `field coverage` step) run this PR's own copies, while CI restores the readers and `field_coverage.mjs` from the base (decision 0013). A local prepr was green on all three steps while CI's `wave-script` and `policy-docs` failed on the same head. Recorded as a process point; no countermeasure built.

- `writing-for-agents: stale`: `wave-r9-groups.json`'s resume entry names `handoff/round9/fix/resume/F11.4.md` on this branch, and the file is not in the tree at 2391db77 or the merged head.
