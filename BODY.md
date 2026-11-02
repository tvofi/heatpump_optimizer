R10-ORCH-ROSTER-SCHEMA, the #2733 remainder alone, as carry 31 (triage `dev/programme/triage/s6-batch71.md#P305`) asks. Part of #2733 and #2505; it closes neither (`## Forward-carry`).

**What the pull request does (unchanged since verdict `9070029ac258bc819e486d57b00b84a89e559936`).** One predicate, `roster_lib.pending_carries(group, legacy)`, says which carries a group still owes. A carry is discharged by a mark at its end (`[implemented: <sha>]`, `[moved: <GROUP>]` or `[dismissed: <reason>]`, `roster_lib.carry_mark`), or it is legacy, meaning a closed group held it at the cut-over (`roster_lib.CARRY_CUTOVER`). `closing_stage` writes `done` over a pending carry as `carries-open`. Its readers are `roster_edit.py set-stage`/`set-resume --field stage`, `roster_sync.py`'s merge transition (`derive()` and `apply_plan()`, both given the cut-over set), and `carry_audit.py roster` (STRANDED, ISSUE-STRANDED, ISSUE-UNLISTED). It adds `roster_edit.py mark-carry`, and a brief_lint warning on a live group with no issue.

**This head is a merge resolution, and nothing else.** It adds no finding, so `## Forward-carry` is the reviewed body's, unchanged. The PR head `d4a2f522c` did not merge with main, because #3066 (R10-RCA-ROSTER-SYNC-ORPHANS: `7d0c3835e`, `01e9f825d`) landed a second rule on the same transition: a closed stage whose group owns an open issue that no other live owner holds is written `carries-open` and printed HELD (`roster_edit.hold_done`, `roster_sync.hold_open`, both through `carry_audit.orphaned`). Train 58734 skipped #3054 for that reason. The resolution keeps both rules. Neither rule is weakened, and the review only needs to judge the delta in `## Head`.

## Head

`495ebdd377e1b49c39ed80025b1a86a27d3e5250`. Its first-parent chain from the PR head `d4a2f522c4260a5b48ebd56d990a99c8366a7aa9` is a fast-forward of nine commits. None is a rebase or a re-cut (orchestrator.md section 7). An earlier fire of this seat made the first three and pushed them to the step ref. This fire re-verified them (everything below) and adopted them, so the ref stays fast-forward:

1. `014b492303907051bcd0d8ec1eddfe10b6f513b6` merges origin/main `ca6333333` (after #3066). **This is resolution 1.**
2. `30500df34d354ffbf22cba7766c119d7ebb58621` is a single-parent fix-up of the resolution. It moves M26's anchor to the merged `hold_open(..., legacy)` call and reflows `hold_open`'s docstring (`git diff --stat 014b49230 30500df34`: two files, 5 insertions, 4 deletions).
3. `6cd56e606e2b5973d682b5ee33d1cdf144de0353` merges origin/main `ddf4bfd73`, with no conflict.
4. `d0f582ca187ec3efe949059f0b8f0532cf789a02` merges origin/main `56630e7e6`, with no conflict.
5. `89f188451e106b14c4aaa55ebe0981093d015cfa` merges origin/main `f04b25a00`, with no conflict.
6. `208f61ee3ca9257106f1f5acb9dd1c9ce6349da7` merges origin/main `25c46e76e`, with no conflict. It brings roster data, delivery rows and triage notes only (`git diff --name-only 89f188451 208f61ee3`).
7. `f29d766b1bb03f50f027f7807c530bdb6a140166` merges origin/main `0166aefd7`, with no conflict. It brings production, golden and claim-file changes from main, and none of them is on the roster seam.
8. `d6c5789a776d9ca534d391bae6134dd977e7743c` merges origin/main `78dd34354` (v7.1.1, after #3143 R10-ROSTER-OPS-2 part 1: `set-size` and `set-files`). **This is resolution 2**, made by this fire: `roster_edit.py` and `r10_roster_ops_mutants.py` conflicted (`git merge-tree --write-tree origin/main f29d766b1` exits 1).
9. `495ebdd37` merges origin/main `94d8b47f6` (#3151 `mutant_run`, which changes `tools/pr/prepr.sh` and `tests/closures.json`), with no conflict. `git diff --quiet d6c5789a7 495ebdd37 -- tools/audit/seat/roster_edit.py tools/audit/seat/roster_sync.py tools/audit/seat/r10_roster_ops_mutants.py tools/audit/seat/r10_roster_sync_mutants.py tools/audit/seat/roster_lib.py tools/audit/carry_audit.py` exits 0.

`git diff --quiet 30500df34 f29d766b1 -- tools/audit/seat/roster_edit.py tools/audit/seat/roster_sync.py tools/audit/seat/r10_roster_ops_mutants.py tools/audit/seat/r10_roster_sync_mutants.py` exits 0, so merges 3–7 did not touch the four files resolution 1 resolved. Merge 8 leaves `roster_sync.py`, `r10_roster_sync_mutants.py`, `roster_lib.py` and `carry_audit.py` alone (`git diff --quiet f29d766b1 d6c5789a7 -- <those four>` exits 0). Main's one later change on this seam, `cac9d0a1f` (carry_audit: an owed roster carry outside the carry sections is a finding), merged textually into `carry_audit.py`. Its self-test and the R1–R5 plants are green at this head (`## Mutation proof`).

Merge base `94d8b47f6c6bf6ace1191280ffdd41dba6b13ab4`, which was the tip of origin/main at 2026-11-02T01:52Z (`date -u`). The prepr run in `## Figures` was taken against that tip. **Main moved after it**: at 2026-11-02T02:54Z origin/main is `8247a1ed10f66baaa173d30be1696907c6bbae32`, one commit (`ci: record nightly kills`) that adds only mutation-ledger records under `tests/mutation_ledger/killed_by/` (`git diff --name-only 94d8b47f6 8247a1ed1`). `git merge-tree --write-tree origin/main HEAD` exits 0. Main moved during each of this seat's last four prepr runs (those against `25c46e76e`, `0166aefd7`, `78dd34354` and `94d8b47f6`), and each run takes about forty minutes. So this head is handed off unmerged with that commit, under fixer.md step 6's rule (merge only on a conflict). The brief's rule (merge whenever main moved) is not followed for this last commit.

**Resolution 1's delta, by file and hunk.** The lines below are the ones in the four files resolution 1 resolved that are in neither of its parents, `d4a2f522c` or `ca6333333`. Each file was checked with `grep -nvxF -f <(git show d4a2f522c:F; git show ca6333333:F) <(git show f29d766b1:F)`. Every other line is one side's, verbatim.

- `tools/audit/seat/r10_roster_ops_mutants.py`, `PLANTS`: conflict on the dict's tail. Resolved as a concatenation: the PR's K1–K12, L1–L6, Y1–Y6 and R1–R5 are followed by main's H1 and H2. No line is in neither parent.
- `tools/audit/seat/roster_edit.py`, four hunks:
  - *module docstring, `set-stage`*: both descriptions are kept, the PR's closing rule first and main's HELD rule after it. The only new lines are the rewrap.
  - *`main()` argparse*: main's `--issue-state` is kept, with the PR's `parse_intermixed_args` and `mark-carry` rest handling. Main's `parse_args` is dropped, because the PR replaced the same line.
  - *`edit()` body*: the PR's `legacy` read and `apply_op(..., legacy, rest)` come first. Main's `hold_done` block follows them, on the stage `apply_op` wrote. `hold_done` acts only on a stage in `DONE_STAGES`, so a `done` that the closing rule has already written `carries-open` is not held a second time.
  - *self-test `edit()` signature*: `rest=(), issues="closed"` (new line), so that the PR's `rest` callers and main's `issues` callers both bind.
- `tools/audit/seat/roster_sync.py`, four textual hunks plus one semantic site:
  - *docstring*: both MERGED rules are kept (new lines 21–25).
  - *`sync()` read path*: the PR's `read_legacy` and `derive(roster, prs, legacy)` come first, then main's `issue_reader`/`dests_for` and `hold_open`.
  - *the stage print*: `(<n> pending carries)` shows only when `owed` is non-empty, because a HELD group owes none. The HELD suffix is main's.
  - *the write path's re-derive*: `derive(..., legacy)` followed by `hold_open(..., legacy)`.
  - **Semantic site: `hold_open` takes `legacy`** (new lines 305–306, 313–318, 322). Main's `hold_open` projected the pass with `apply_plan(projected, changes, [])`. The PR's `apply_plan` re-applies `closing_stage` through `op_set_stage`, so without the cut-over set, a legacy-only group that `derive()` closed `done` projects `carries-open`. That makes it live, so it owns its own issue, and `orphaned` then finds nothing. The orphan main's rule exists to catch would pass silently. Both callers now pass `legacy`. This was resolved by reading both callers, as the brief asks, rather than by choosing a side. It is pinned by a new self-test check (lines 874–887, `a legacy-only group owning an orphan open issue is held, the hold reading the cut-over`).
- `tools/audit/seat/r10_roster_sync_mutants.py` (it merged textually, but its anchors moved with the semantic site): M26's and M27's anchors take the `legacy` argument. The new plant `M29_hold_without_legacy` drops it from the projection and is killed by the check above.

**Resolution 2's delta** (`d6c5789a7` against its parents `f29d766b1` and `78dd34354`). `grep -nvxF -f <(git show f29d766b1:F; git show 78dd34354:F) <(git show d6c5789a7:F)` prints only `roster_edit.py` lines 993–994, the joined op-choices tuple. For `r10_roster_ops_mutants.py` it prints nothing.

- `tools/audit/seat/roster_edit.py`, six hunks:
  - *usage*: the `mark-carry` line, then #3143's `set-size`/`set-files` lines.
  - *docstring ops*: `mark-carry`, then `set-size` and `set-files`.
  - *the `op` choices*: the union (the one new line pair).
  - *`--match`*: the branch's help (`drop-carry, mark-carry`), then #3143's `--cite`, `--add`, `--set-files` and `--set-hot`.
  - *argument validation*: the branch's `drop-carry`/`mark-carry` index-or-`--match` rule, then #3143's set-files/`--cite`/`--add` rules and its value test, which exempts `set-files` and an empty `set-size`. That test is #3143's line, and it keeps `a.match is None`, so a `mark-carry --match` (whose value moves into `rest`) passes as before.
  - *`edit()`*: #3143's `set-size`/`set-files` early return through `apply_files_op`, then the branch's `legacy` read for `set-stage`/`set-resume`. The two are disjoint by op.
- `tools/audit/seat/r10_roster_ops_mutants.py`, one hunk: #3143's `CITE_GUARD` and `PLANTS.update({Z1..Z12, R11})` block, then the branch's `parts()` and `target_self_test(target=TARGET)`. Main's no-argument `target_self_test()` is dropped, because the branch's version has a default argument and replaces it. #3143's 2-tuple plants fall to `parts()`'s `roster_edit.py` default.

**Union proof, per file.** Let `n REV FILE` be `git show REV:FILE | grep -oE '^ *def [A-Za-z_0-9]+|^ {4}"[A-Z][A-Za-z0-9_]*": [(\[]|add_argument\("--[a-z-]+"' | sed -E 's/^ +//' | sort -u`, which yields the function names, mutant ids and CLI options. Then `comm -23 <(n d4a2f522c F) <(n HEAD F)` and `comm -23 <(n origin/main F) <(n HEAD F)` print nothing for each of the four files, with `origin/main` at `78dd34354` and `HEAD` at `d6c5789a7`. The mutant ids include #3143's Z1–Z12 and R11:

| file | PR-head `d4a2f522c` names | main `78dd34354` names | lost from PR | lost from main | null: base `1d28de993` in the merge's place (PR / main lost) |
|---|---|---|---|---|---|
| `roster_edit.py` | 72 | 86 | 0 | 0 | 6 / 20 |
| `roster_sync.py` | 48 | 52 | 0 | 0 | 1 / 5 |
| `r10_roster_ops_mutants.py` | 68 | 53 | 0 | 0 | 30 / 15 |
| `r10_roster_sync_mutants.py` | 26 | 30 | 0 | 0 | 0 / 4 |

The null column runs the same command with the merge base in the merge's place. It reports each side's additions as lost, so a resolution that dropped one side would show up as a non-zero count.

## Approval

Unchanged from the reviewed body. The roster's `owner_gate` for this group reads "Policy: tvofi approves at merge (design section 8 rows vii and viii, DONE_STAGES and the roster schema); mandate 6329234399 applies." Neither this diff nor the resolution changes `DONE_STAGES`. The resolution edits no file that `CLAUDE.md` names as policy. Whether row viii covers the carry-mark grammar is the orchestrator's call under the mandate. It is raised here and not decided here.

## Mutation proof

Both tables were run at `d6c5789a7` (resolution 2), whose six roster files are byte-identical to this head's (`## Head` item 9), one at a time, with `env -u BASH_ENV`. Every plant is restored afterwards, and `git status --short` was empty after the runs.

- `env -u BASH_ENV python3 tools/audit/seat/r10_roster_ops_mutants.py`: `plants: 75, without a FAIL line: ['C6']`. All 75 are `rc=1`. C6 dies on the `KeyError: 'carry'` crash that #2880 disclosed, as at the reviewed head.
  - Resolution 2's sites: #3143's plants all die in the merged driver and file: Z1 `rc=1 fails=6`, Z2 5, Z3 4, Z4 1, Z5 8, Z6 10, Z7 4, Z8 1, Z9 2, Z10 1, Z11 5, Z12 4, R11 5. So do the branch's plants on the merged `main()`/`edit()` hunks: P3 (`--match is a drop-carry flag`) 4, K7 2, K8 4, K9 1, K12 2.
  - Resolution 1's sites: main's H1 `rc=1 fails=2` (`set-stage done holds a group owning an open issue nothing else owns`, `... and so does set-resume --field stage, with any closed stage`) and H2 1; the branch's Y1 1, Y2 2, Y3 2, Y4 4, Y5 1 and Y6 1 (taken at `d0f582ca1`; merge 8 leaves `roster_sync.py` byte-identical).
- `env -u BASH_ENV python3 tools/audit/seat/r10_roster_sync_mutants.py`: 28 of 29 `rc=1`, then `restored`. Main's M25–M28 still die on their re-anchored lines. Resolution 1's own `M29_hold_without_legacy` is `rc=1 fails=1` (`a legacy-only group owning an orphan open issue is held, the hold reading the cut-over`, got `stage='done'`), which is its semantic site's mutation proof. `M9_carry_dedupe_dropped` survives (`rc=0 fails=0`), as at the reviewed head and on main before this diff (`## Forward-carry`).

## Null control

- `env -u BASH_ENV python3 tools/audit/seat/r10_roster_ops_mutants.py --null`: `rc=0 fails=0` for each of `carry_audit.py`, `roster_edit.py`, `roster_lib.py` and `roster_sync.py`.
- `env -u BASH_ENV python3 tools/audit/seat/r10_roster_sync_mutants.py --null`: `NULL_no_plant rc=0 fails=0`.
- The unplanted self-tests at this head, each with `env -u BASH_ENV python3 <file> --self-test`: `roster_edit self-test: 191 checks, 0 failed`, `roster_sync self-test: 95 checks, 0 failed`, `roster_lib self-test: 60 checks, 0 failed`, `carry_audit self-test: 227 checks, 0 failed`, `r10_roster_ops_mutants self-test: 231 checks, 0 failed`.
- **No check was lost.** The first-argument source of every `check(...)`/`refuses(...)` call (an `ast` walk over `git show REV:F`) in `roster_edit.py` and `roster_sync.py`: PR head `f29d766b1` 168 and 94, main `78dd34354` 188 and 82, merge 202 and 94. Neither parent has one that the merge lacks. Null: with `0166aefd7` in the merge's place, the walk reports the branch's carry-ledger checks as lost.
- M29's null is main's own hold checks in the same run (`a merged group owning an open issue nothing else owns is held carries-open ...`, `... one whose issue a live group also lists is done (null control)`, `... one whose issue is closed is done (null control)`). They pass both with and without `legacy`, so the new check is the only one that reads the cut-over.

## Figures

Every figure was taken at `495ebdd37` unless a line says otherwise. The mutant tables and the check-name walk were taken at `d6c5789a7` (`## Head` item 9). Each line names its instrument.

- **Union proof**: the `n`/`comm` command in `## Head`, with the table there. The check-name walk is in `## Null control`.
- **Self-tests and both mutant tables**: as `## Mutation proof` and `## Null control`.
- **Scope**: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"` prints `MODE: SCOPED -- 1 script(s) run, 32 scoped out`, and `scope.run` names `tests/entities.py`. `PYTHONPATH=tests/hastub python3 tests/entities.py` prints `ALL 2521 ENTITY CHECKS PASSED`.
- **`python3 tests/structure.py`**: `STRUCTURE RATCHET PASSED`.
- **`python3 -I tools/audit/archscore/score.py --diff $(git merge-base origin/main HEAD) HEAD`**: `Architecture score: dS +0.0000 NULL`.
- **Claim files and version**: `git diff --quiet origin/main HEAD -- tests/golden/claimed_drift.txt tests/golden/card_claimed_drift.txt VERSION RELEASE_NOTES.md custom_components/heatpump_optimizer/manifest.json` exits 0. They are byte-identical to origin/main.
- **`bash tools/pr/prepr.sh <this body>`**, the full run without the closures skip: `PRE-PR: 495ebdd377e1b49c39ed80025b1a86a27d3e5250 0000000000000000000000000000 rc=0`. Every step is `ok` or `skip`, among them `self-test 437 passed, 0 failed`, `closures scoped recordings are covered; left to CI: tests/harness_headers.py`, `CI PREDICT: no closures, fast, governance or instrument red predicted against 94d8b47f6c6b`, `unpinned sites: the diff adds no unpinned mutation site`, `PR-BODY: 0 error(s)`, `CARRY-AUDIT: 9 finding item(s): 9 routed, 0 unrouted, 0 bad destination(s)` and `claim files byte-identical to origin/main`. It was run against merge base `94d8b47f6` at 2026-11-02T02:54Z.

## Red checks

- `governance / instrument-self-tests`: concluded red at earlier heads of this PR, from 2026-11-01T09:41Z to 10:01Z, among them `e8e433751f34a3e7e1c07393b9f113daa8f2bcd3`. The `pr_args.sh` self-test's sleeper null controls (`open_pr: the null control -- an unrelated sleeper survives`, `null control: a normal successful update_pr leaves nothing behind and stops nothing it did not start`) failed on ubuntu-26.04 runners, because uutils `sleep` refuses a renamed symlink. That was main's red, not this diff's, and main fixed it in #3086 (`1a8051350`), which this branch has merged since. The cheaper detector is that self-test itself, which caught it. It was green at `d4a2f522c`.
- No other check concluded red at the PR head `d4a2f522c` (its check runs at 2026-11-01T16:37Z: `gate`, `pr-contract / pr-contract`, `arch-score / arch-score` and `budget-raise-gate / budget-raise-gate` success, the rest success or skipped). The PR is `DIRTY` because of the conflict this head resolves, and a `DIRTY` pull request cannot run (`claim-files.md`), so the conflict itself raised no red check to answer.

## Forward-carry

- **This group's own stage is wrong on the roster.** A group re-dispatched on a branch name whose earlier pull request merged is still matched to that merge (`handoff/r10-roster-schema` answers for #2880). It needs one `set-stage R10-ORCH-ROSTER-SCHEMA carries-open` after this merges. The matching rule (design 6.4, B13) needs a dispatch-time `resume.commit` or a fresh topic. Carry: #2505
- This group's carries that are not built here stay on its carry list once its stage is repaired. The two already on main (`LOCK_RACE_RE` retry, `LINT GATE REFUSED`) need `mark-carry … implemented`. Carry: #2505
- Carry 10 (c)'s invariant-3 tick line belongs in `orchestrator_tick.py` (R10-ORCH-LEDGER). `carry_audit.py roster --open-issues FILE` is the offline instrument it can call. Carry: R10-ORCH-ROSTER-SCHEMA
- `r10_roster_sync_mutants.py`'s `M9_carry_dedupe_dropped` survives on main and at this head. `already_carried` subsumes the exact-text dedupe that the plant drops. Carry: #2505
- The issue arm's first reading (7 ISSUE-STRANDED, 1 ISSUE-UNLISTED at roster `a4c9fa3d6`) is owed a disposition per issue. Carry: R10-ORCH-ROSTER-SCHEMA
- `closing_stage` rewrites only `done`, so `set-stage rca-done`/`absorbed` over pending carries writes the closed stage. Since #3066, `hold_done` does hold `rca-done` over an orphaned issue. A pending carry alone still does not hold it. Carry: R10-ORCH-ROSTER-SCHEMA
- `append-carry` accepts text that already ends in a mark-shaped suffix, and legacy is matched by exact text per group. Carry: R10-ORCH-ROSTER-SCHEMA

## Friction

- fixer.md: unclear: the brief's identity line (`hpo-fixer`) and the payload's setup line (`git config user.name seat`) name different commit identities for one seat. The merge commits use the brief's `hpo-fixer <70032254+tvofi@users.noreply.github.com>`. Carry: #2505
- fixer.md: contradiction: the brief says to merge origin/main whenever it moved since the last prepr run, while fixer.md step 6 says to merge before the handoff only on a conflict. With main moving about hourly and prepr taking about forty minutes, the brief's rule does not terminate. This seat followed it four times and stopped at a conflict-free ledger-only commit (`## Head`). Carry: #2505
- orchestrator.md: cost: an earlier fire of this seat had already pushed a resolution to `handoff-wip/r10-roster-schema-pr` that the re-fire brief did not mention ("never returned a merge"). The re-fire repeated the resolution before it found the step ref. Carry: #2505
