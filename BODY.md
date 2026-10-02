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

`4a3b49dee17e339058749ed224bf67fa0c19f02d` is `d0c761b545f52e0c841d26634b5dbafb6c021a23` plus two commits. `d0c761b5` merges origin/main `2b6c5b876ec297bf2b0ef4a127d09cf97fc40b5d` (#1838, F10.4) into `2391db77b4878d54e96279dd79301782f57fefa5`, with no conflict and no hand resolution. The first commit (e166a15a) registers `agreement.mjs`, `agreement_py.py` and `tests/structure.py` in `field_coverage.mjs`'s DECLARED list (as `none`, with a reason each) and names `tests/structure*` by glob in the `policy-docs` field-coverage skip guard, because `tools/audit/prepr.sh` refused the merged head on `field coverage` and `pinned graders` (Red checks). The second (4a3b49de) adds an `agreement lane` step to `tools/audit/prepr.sh`, because `pinned graders` also refused `agreement.mjs` and `agreement_py.py` for having no local run there.

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
- Scoped gate, `MODE: SCOPED`, two scripts run (`tests/entities.py`, `tests/harness_headers.py`): `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)`. Both need numpy, which the seat's Mac lacks, so CI is their first run.
- Step-8 enumeration, class I4 seams at `origin/main` 2b6c5b87 and at this head, from an export of each tree overlaid with `origin/handoff/audit-r9-evidence` and `origin/handoff/audit-r9-sweep-s4`: `PYTHONPATH=tests/hastub python3 $EXPORT/tools/audit/round9/D14/sweep/I4/enumerate.py` run with `$EXPORT` as the working directory (sha1 `a9dad811c7ac3d7dda3dbd4dafdcd73560850d62`, `figure_lint` reports it unverified). Rule: it re-runs the four offline finder harnesses and greps `CLASS_GUESS` readers. Result: `dead_methods=0` at both ends (D7-s3-02 closed at base by #1838, guarded here by the pair and the census arm); `i4_reader_sites` 34 at base and 44 at head, the added sites being the registered lane readers; the `CLASS_GUESS` readers are the three-reader `finding-class-id` pair. D11-s1-71 and D11-s1-72 harnesses error at both ends (`eFrontmatter is not defined`, `_GOV_JOBS = _workflow_job_ids(_DS_GOV)` not found), because their text is keyed to source that F11.1 rewrote; the pairs `rule-frontmatter-paths` and `governance-workflow-jobs` are their live detectors. D13-s1-01 needs a live window and is cited from `tools/audit/round9/D13/s1/REPORT.md` as the enumerator says. Disposition: every returned seam is closed in this diff or already guarded; none is a new finding.

## Red checks

No CI run exists yet at this head and no pull request is open. `tools/audit/prepr.sh` at `d0c761b5` refused two steps, both fixed in `e166a15a`:
- `field coverage`: three `pinned` inputs (`agreement.mjs`, `agreement_py.py`, `tests/structure.py`) had no DECLARED entry. Cheaper detector already in place: `field_coverage.mjs` itself, which `prepr.sh` step 3f3 and `policy-docs` run; the earlier handoff at `2391db77` did not run it after the pins were added. No new detector owed.
- `pinned graders` (`unparsed governance.yml:policy-docs tests/structure.py`): the skip guard's `git diff --quiet` line named a pinned `.py` with no interpreter on the line. Fixed by the glob `'tests/structure*'`.

## Approval

Not yet given. This diff touches policy and code-owned paths: one line in `tools/audit/README.md`, `.github/workflows/governance.yml` and `.claude/workflows/audit-find.js`. It merges only on tvofi's approving review at the head; the orchestrator requests it. No approval is claimed here.

## Forward-carry

- `tools/audit/bugclasses.json`: the I4 entry's `barrier` text records the lane's one limit, a second reader with a different grammar for an unregistered concept ("Not reached"), which is the A7 and A8 policy text of R9-F11.5. The F11.5 roster group lives on `handoff/audit-r9-fixplan`, not in this tree, so the destination checked here is the ledger entry.

## Friction

- `gate-scoping: cost`: local `python3` has no numpy, so `tests/entities.py` and `tests/harness_headers.py`, the two scripts the scoped gate selects for this diff, cannot run on the seat's Mac and wait for CI.
- `writing-for-agents: stale`: `wave-r9-groups.json`'s resume entry names `handoff/round9/fix/resume/F11.4.md` on this branch, and the file is not in the tree at 2391db77 or the merged head.
