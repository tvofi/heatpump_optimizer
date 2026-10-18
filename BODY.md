Repairs main's red `wave-script` job (agreement lane, pair `merge-subject-pr`). It has been red since 5756f2b1.

**Cause.** #2379 (5756f2b1) and #2401 (07a09406) were merged by hand with a custom `--subject`, `Merge pull request #N (<group>)`, and not with GitHub's template, `Merge pull request #N from <branch>`. `stamp.py pr_from_subject` and `delivery_status.py subject_number` match `^Merge pull request #(\d+)\b`, so both read 2379 and 2401. Both `policy_lint.mjs` readers returned null. `resolvePrFromCommit` (gap recovery) matched `^Merge pull request #(\d+) from `. `enumerateMerges`'s offline mode reads only the squash shape. Its `narrow` declaration in `agreement.mjs`, also keyed on ` from `, did not cover the new tail. Merge commits on main cannot be rewritten, so the readers must change to read them.

**Fix.**
- `policy_lint.mjs`: `MERGE_COMMIT_SUBJECT_RE` is now the Python readers' grammar, `^Merge pull request #(\d+)\b`. `resolvePrFromCommit` therefore reads both custom subjects. Its acceptance pins the custom tail and four subjects that name no pull request.
- `agreement.mjs`: `MERGE_SHAPE` holds the same grammar and is used for two things.
  - The null guard (`mustAnswer`). It was keyed on ` from ` and was blind to these subjects. It is now wider, so the check is stronger, not weaker.
  - `enumerateMerges`'s declared `narrow`. The accepted F11.1 asymmetry stays as it was. The offline mode still reads the squash shape only, its zero still means "could not enumerate" (`enumSkipLine`), and the lane still refuses that reader the moment it answers on the merge shape.
- `agreement.mjs` gets a new **merge-subject guard**, run with its pair, so the defect cannot come back silently:
  - Every first-parent merge on main past 07a09406 must carry one of GitHub's two templates: `Merge pull request #N from <branch>` or `<title> (#N)`. GitHub's own test merge at the runner's HEAD is the one exception.
  - No merge call under `tools/` or `.claude/workflows/` may pass a subject or body (`--subject`/`-t`/`--body`/`-b`/`--body-file`/`-F`, `commit_title`/`commit_message`). A scan that finds no merge call at all is refused.
  - The writers the scan finds today: `tools/audit/seat/merge_pr.sh` (`gh pr merge --merge --match-head-commit`), `tools/audit/seat/merge_train.py` (its two `gh pr merge` calls), the web-* wave scripts and `web-fragments.md` (`merge_method merge`). None passes a subject.
- `agreement_py.py`: the corpus gains both hand subjects (pinned in case the live window moves), the old `Merge pull request #13: ...` shape, and four null controls.

**Why the grammar is not one shared data file.** The preferred design was a single grammar file read by Python and JS, and it lost on three counts:
- The wave-script and policy-docs jobs restore `tools/policy/*.mjs` and `*.py` from the base, but a JSON file would not be restored. A pull request could then change the grammar it is graded by, unless `governance.yml` (code-owned) grows the restore pathspec.
- A new tracked file needs a closure classification.
- The repository already has a barrier for exactly this cross-language copy: discovery requires the copies to be registered (`pair:merge-subject-pr`), and the pair arm drives them against one corpus.

The four textual copies are now identical, and discovery still counts them as one registered grammar (27 shared, 0 unregistered, 0 dead).

**Not widened: `enumerateMerges` offline mode.** The brief asked for this at minimum. I left it narrow because widening it overturns the asymmetry recorded as accepted in `dev/audit/config/bugclasses.json` (I4 barrier) and changes what `enumSkipLine`'s documented zero means during an API outage. The asymmetry is now declared over the same grammar every reader uses, so it no longer misses a merge-shape tail.

**stamp.py notes completeness.** Rule 4 attributes both commits, so the next stamp's notes must name #2379 and #2401 like any other merge. `blind_merges` is empty over `v7.0.0..origin/main` (140 commits, 135 PRs read).

**CI on this pull request.** `wave-script` restores `tools/policy/*` from the base, so this PR's own run grades it with main's readers and stays red on the same two items. That is the restore working as designed: "a pull request cannot change a reader it is graded by". The fix grades on main's push run after the merge. This PR must be merged with GitHub's template subject (via `merge_train.py` or `merge_pr.sh`, with no `--subject`), or the new guard turns main red on its own merge.

## Head

bc69ba0224ba1fea508f94823830c92c3f0cafb7 (merge base 07a09406a1cc97076a6f28581f87f313b322a6b6 = origin/main at 2026-10-18).

## Mutation proof

Each mutant was applied in place, run, then restored.
- M1: `MERGE_COMMIT_SUBJECT_RE` back to `^Merge pull request #(\d+) from `. Agreement: `RESULT divergent=3` on #2401's and #2379's subjects and `Merge pull request #13: ...`, where `resolvePrFromCommit` returns null. `policy_lint.mjs`: `FIXTURE VACUOUS: resolvePrFromCommit [... custom tail ...]`.
- M2: the `narrow` declaration back to ` from `. `RESULT divergent=3` (the same three subjects, with offline mode null against "2401", "2379" and "13").
- M3: the `p.guard?.(report)` call deleted. Self-test `FAIL a pair's guard runs with its pair`.
- M4: `TEMPLATE_SUBJECT`'s merge arm widened to the reader grammar. Self-test `FAIL a hand-written merge subject is refused (#2379, 5756f2b1)`.
- M5: the writer test blinded (`if (false)`). Self-test `FAIL a merge call that passes --subject is refused` and `FAIL a merge call that passes commit_title is refused`.
- M6: `mustAnswer` back to ` from `. Self-test `FAIL merge-subject-pr's null guard covers a hand merge's custom tail, and not a subject naming no pull request`.
- Guard on real history: with `SUBJECT_CUTOFF` set to 86010e8c, the commit before 5756f2b1, the guard refuses exactly 5756f2b15 and 07a09406a (`refused=2`). With the cutoff at dc8aa807, it walks 17 first-parent commits and still refuses only those two; the 15 template merges in that range pass.

## Null control

- The unmodified tree (origin/main, 07a09406): `merge-subject-pr: 4 readers, 808 items, 2 divergent`, the two DIVERGENT lines main's job reports.
- Head, subjects that name no pull request: `Merge pull request from a fork`, `Merge pull request #12x from a/b`, `Record #424 W1-G14 merge in delivery-status` and `Merge branch 'main' into fix/x` read as null in all four readers. The pair compares all four, and the Python side's JSON shows `{'stamp': None, 'delivery_status': None}` for each.
- The guard over the live window past 07a09406 (0 commits at the merge base) refuses nothing. Its 45 merge calls in 9 files carry no subject flag.

## Figures

- Base divergence, at origin/main: `python3 -I tools/policy/agreement_py.py --out <scratch>/base.json && node tools/policy/agreement.mjs --py-json <scratch>/base.json` printed `pair merge-subject-pr: 4 readers, 808 items, 2 divergent` and `RESULT divergent=2`. The rule: every first-parent subject in `v6.5.0..HEAD` plus the fixed shapes, compared across four readers.
- Head: the same command printed `pair merge-subject-pr: 4 readers, 813 items, 0 divergent`, `merge-subject guard: 0 first-parent commit(s) past 07a09406a, 45 merge call(s) in 9 file(s)`, `discovery: 333 governance code files, 1529 distinct grammars, 27 shared by two or more files` and `RESULT divergent=0 unregistered=0 dead=0 refused=0`.
- `node tools/policy/agreement.mjs --self-test`: `SELF-TEST 23 of 23 probes held` (15 before this change).
- `node tools/policy/policy_lint.mjs`: `TOTAL: 0 error(s) across 41 policy file(s)`, `FIXTURE ok: 92 error(s) hold 245 pins`.
- `node tools/policy/field_coverage.mjs`: `RESULT ... blind=0 dead=0 refused=0`. An earlier draft named the two writer files in string literals, which put `tools/audit/seat/merge_pr.sh` on `codeowners_gap.py`'s evaluated surface (F) and reached `refused=1`. The literals were removed. `python3 dev/audit/rounds/round6/D11/fix/codeowners_gap.py` output at head is identical to its base output except for the interpreter warning's path.
- Scope: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir <dir>` printed `MODE: SCOPED -- 1 script(s) run, 32 scoped out`, and the script run is `tests/entities.py`. `PYTHONPATH=tests/hastub python3 tests/entities.py` printed `ALL 2349 ENTITY CHECKS PASSED`.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`.
- Stamp rule 4 over `v7.0.0..origin/main` (`stamp.window_log_args`, `stamp.parse_window`, `stamp.prs_from_window`, `stamp.blind_merges`): window 140, prs 135, 2379 and 2401 present, blind `[]`.
- Class seams (fixer.md step 8). Rule: `git grep -nE 'Merge pull request #' -- 'tools/*.py' 'tools/*.mjs' 'tools/*.js' 'tests/*.py' 'tests/*.mjs'`, keeping the regex definitions. It returns six:
  - `tests/delivery_status.py` `MERGE_SUBJECT`: already guarded (it was already this grammar).
  - `tools/release/stamp.py` `MERGE_SUBJECT_RE`: already guarded (it was already this grammar).
  - `tools/policy/policy_lint.mjs` `MERGE_COMMIT_SUBJECT_RE`: closed here.
  - `tools/policy/agreement.mjs` `MERGE_SHAPE`: closed here.
  - `tools/policy/agreement.mjs` `TEMPLATE_SUBJECT`: the guard. It is deliberately GitHub's narrower template.
  - `tools/audit/seat/orchestrator_tick.py` `MERGE_PR`: a distinct seam, not closed here. It is an unanchored `findall` over `git log --merges --format=%s`, so it reads both hand subjects (2379, 2401). It does not read the `<title> (#N)` template, so the tick's missing-row arm cannot see the record-autofix merges #2413, #2412 and #2407 that `delivery-status` reports overdue. Whether a record-class merge owes a row (#2003) is that other red's question, and the orchestrator ruled it out of this PR.

## Red checks

- `wave-script` (red on main from 5756f2b1, and red on this PR's own run because the readers are restored from the base). Cheaper detector: none existed for the cause, because a hand merge's subject is written at merge time, after every pull-request check has run. The agreement lane on main's push run was the first and cheapest place the history could be read. Countermeasure built here: the merge-subject guard, which names the commit and the rule on main's first push run after such a merge, and refuses any tracked merge writer that passes a subject before it merges. Its standing cost is one `git log` over the commits past the cutoff plus a line scan of about 330 files, inside the agreement step (`seconds=1.0` for the whole lane locally). Process state: (a) the process did not exist. No rule or tool kept a hand merge on GitHub's template, and the readers' grammar had a ` from ` copy that no check compared on this shape until it occurred.
- `delivery-status`, red on #2420 at b0140e47 and the same on #2415 and #2404 per the orchestrator, has another cause. The job prints `DELIVERY STATUS OVERDUE -- 132 rowed, 0 pending, 3 overdue`: the record-autofix merges #2413, #2412 and #2407 have no delivery row. #2379 and #2401 are among the rowed. This diff does not touch what that job reads, so its red is main's (`defect-root-cause.md`), and it is not fixed here.

## Forward-carry

The rule this establishes is that a merge to main keeps GitHub's template subject and never takes `--subject`. It changes how the orchestrator merges, and `dev/governance/roles/orchestrator.md` is policy. That edit is the owner's to approve, so it is not made here. The guard enforces the rule meanwhile, and its refusal line names `merge_train.py` and `merge_pr.sh`. Destination for the orchestrator to carry: `dev/governance/roles/orchestrator.md` (merge section).

## Friction

none
