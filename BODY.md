R11-SEAM-comments-production part 1 (ADR-010; approved design `design/R11-SEAM-comments-production` at 15dd4f5b3aae9534603cca9939774200d8ad7911, verdict `Design review: approve 15dd4f5b`, sections 3 A, 3 B and 6). Part of #3746 and #3778; it closes neither, because twelve parts remain. This part does two things:

- It extends the shared comment ratchet, `tests/comment_ratchet.py`, to the production scope. That means the package's top-level modules and the card's script. The roster carry on `handoff/audit-r10-roster` says R11-SEAM-comments-tests writes the one script and this group consumes it without writing its own. This part follows the carry and changes `in_scope()`, the gate row's name and the self-test.
- It pays every long unit in the 25 production files that the design's release command prints `RELEASED` for and that carry one. Two more RELEASED files, `log_latch.py` and `slot_drivers.py`, had none.

Findings: D5-s4-01 (C5, partial: the p1 files) and D5-s3-03, merged into D5-s4-01 (partial: the p1 files). D5-s3-02 (`comfort_band.py`) is not in this part. Design ruling 1 puts it in the first part dispatched after R11-SEAM-inputs-guards merges, and the release command still prints `HELD comfort_band.py R11-SEAM-inputs-guards`.

**Roster Carry 0 (the shared 40-word ratchet script)** is answered here. This part writes no ratchet of its own. It consumes R11-SEAM-comments-tests' `tests/comment_ratchet.py` by extending `in_scope()`, the one SCOPE list, to the package's top-level modules and the card's script.

**Stacked on #3808.** `tests/comment_ratchet.py` is not on main yet. This branch merges #3808's head (bdcca2fb9f, then a94deddd62) so that the scope change has the script to change. Until #3808 merges, the three-dot diff shows #3808's 23 files too, and this PR cannot merge before it. After #3808 lands, the diff is this part's own files:
- the 25 production files, which are text only;
- `tests/comment_ratchet.py`;
- one new harness, `dev/audit/harnesses/r11_comments_production_reconcile.py`.

**The text edits.** Every edit splits a long sentence at a clause boundary that is already there. The usual changes are a `;`, `:` or `--` turned into a full stop, or a bold list heading's full stop moved outside the `**`, because `text_ledger.sentences` does not split inside it. Each edit keeps every reason, constraint and number the sentence stated. No sentence was deleted, and every hunk keeps its line count, so line numbers, coverage, closures and `span_loc` do not move. Quoted Swedish source text is left verbatim: the split falls between the quotes, or an id is wrapped in double backticks so that the sentence after it starts a new one.

**Alternatives that lost:**
- Writing this group's own ratchet script, as the design's section 3 A first drew it. The carry and ADR-001 rule that out: one 40-word rule, one script.
- Waiting for #3808 to merge before starting. That would delay the text part, which needs no script, for no gain. The stack costs nothing at merge, because #3808's commits are ancestors of this head.
- A stored per-file budget. That would be a two-sided row that every behaviour PR deleting a long comment would trip (design section 4).

## Head

aabb3d8eab446a45189aae276096cc296676a68c (origin/main cb8edb65a5, 2026-11-19T12:54Z)

## Mutation proof

This part adds no production code. The one predicate it adds is `in_scope()`'s production arm. Command: the five mutants below, each written into `tests/comment_ratchet.py`, followed by `--self-test`, then restored. The driver is a scratch loop, not tracked. Results:
- The production arm off (`return False`, the pre-change scope): KILLED by "SCOPE is the tests, the package's top-level modules and the card, and no other path" and "every tracked production module is in SCOPE".
- The card clause dropped: KILLED by the same two arms.
- The subpackage guard dropped: KILLED by "SCOPE is the tests, ... and no other path".
- The `.py` suffix check dropped: KILLED by the same arm.
- The whole package in scope (`return path.startswith(PKG)`): KILLED by the same arm.

The baseline self-test is OK. #3808's body carries the mutation proof for the shared predicates (`> MAX_WORDS`, the per-file and total compares, the new-file branch, base resolution and the `--text-only` arms), and this part does not change them.

**Failing test first, end to end.** A 41-word comment was planted at the end of `custom_components/heatpump_optimizer/log_latch.py`, which has 0 long units at the base:
- With this head's `in_scope`, `python3 tests/comment_ratchet.py` prints `REFUSE custom_components/heatpump_optimizer/log_latch.py: long units 0 -> 1; new: "word word word ..."` and `comment_ratchet: FAIL`.
- With `in_scope`'s production arm reverted to #3808's scope, the same plant prints `RESULT ... files=96` and `comment_ratchet: OK`. Nothing refuses it.

`prepr.sh`'s `MUTANT_CMD` draws only added `.py` lines outside `tests/` and `dev/`, and this diff adds none.

## Null control

- **The self-test's 40-word sentences** are accepted in a production module and in the card's script.
- **Files outside the part:** the finders' harnesses read every file outside the 25 the same at both ends. `c5_long.py`'s per-file lines differ only in the ten s3-cell p1 files. `comments.py --tsv`'s `FILE` lines differ only in the fifteen s4-cell p1 files, which makes 30 differing lines, two per file.
- **Units unchanged:** both harnesses read the same unit count at both ends (`units=2916` and `units=3420`), so no edit merged or split a unit.
- **The harnesses' own perturbations move:**
  - `c5_long.py --perturb` at this head reads `long_units=325`. That is 345 less the `dhw_planner` drop of 20 (29 to 9).
  - `comments.py --edit` reverting one `wear.py` split in memory reads `long_units=516`, with `wear.py` back to `long=1`.
- **The reconcile harness's `--perturb`,** which appends one 41-word comment to every file read, raises both totals by 97, the number of files read.

## Figures

<!-- figure-block: scope-line mb=cb8edb65a5a9c0940dbe263acee49e02ba5f0b25 head=aabb3d8eab446a45189aae276096cc296676a68c -->
~~~text
MODE: FULL -- every test script runs, nothing is scoped out.
~~~
<!-- /figure-block -->

Commands are run from the repository root. `$EXPORT` is `git archive origin/plan/r11 dev/audit/rounds/round11/D5/s3 dev/audit/rounds/round11/D5/s4`. The finders' harnesses are cited from that export, as `fixer.md` step 3 requires, because they are not in the tree. Their sha1s are `c5_long.py` 2dd30e9415d1860e471729f08335c94bc1a8c1de and `comments.py` da19a3201458b34b687e9c3e7e89760d2251b626.

**The finders' harnesses (D5-s3-03, D5-s4-01):**
- `PYTHONPATH=tests/hastub python3 $EXPORT/dev/audit/rounds/round11/D5/s3/c5_long.py`, run in a worktree at cb8edb65a5 and again at this head, prints `RESULT long_units=372` at the base and `RESULT long_units=345` at the head. The 27 paid units are the ten s3-cell p1 files' units, and each of those files reads 0 at the head.
- `PYTHONPATH=tests/hastub python3 $EXPORT/dev/audit/rounds/round11/D5/s4/comments.py --repo . --ref HEAD`, run at the same two trees, prints `RESULT long_units=562` at the base and `RESULT long_units=515` at the head. The 47 paid units are the fifteen s4-cell p1 files' units, and each of those files reads `long=0` at the head.

**The ratchet:**
- `python3 tests/comment_ratchet.py` at this head prints `RESULT base=cb8edb65a5a9 files=193 long_units_base=2534 long_units_head=2439` and `comment_ratchet: OK`. The difference of 95 is this part's 71 production units plus #3808's 24 tests units. The production split, from `dev/audit/harnesses/r11_comments_production_reconcile.py` below, is 892 at the base and 821 at the head.
- `python3 tests/comment_ratchet.py --self-test`: OK. That is 28 arms, six of them new here.
- `python3 tests/comment_ratchet.py --text-only cb8edb65a5a9c0940dbe263acee49e02ba5f0b25` prints `RESULT code_changed_files=5 line_shifted_hunks=9`. Its CODE lines name #3808's five files only: `closure.py`, `comment_ratchet.py`, `doc_claims.py`, `entities.py` and `run.sh`. No CODE or SHIFTED line names a production file, so the 25 text files change no code token and keep every line.

**Reconcile (the design's section 6, and #3808's hand-off note owed to this part).** The command is `PYTHONPATH=tests/hastub python3 dev/audit/harnesses/r11_comments_production_reconcile.py $EXPORT [--ref REF]`. It imports `c5_long.long_sentences` and `comments.clean` from the export and applies each finder's rule to its own cell:
- At `--ref cb8edb65a5a9c0940dbe263acee49e02ba5f0b25`: `harness_long=934 ratchet_long=892 ratchet_above_harness_files=0`. 934 is 372 + 562, the two harnesses' own totals.
- At this head: `harness_long=860 ratchet_long=821 ratchet_above_harness_files=0`. 860 is 345 + 515.
- The ratchet reads at most the harness on every file. The 42 harness-only units sit in 25 files. Each is a unit where the ratchet's paragraph rule splits, at a list item, an indented code block, a banner or a trailing comment, and the harness's textual splitter runs one sentence across. The design asked for the two sides to agree "to the unit". Under the carry, the ratchet's rule is #3808's, reviewed there, so this part names the difference and does not change the rule. Each part pays its files to 0 on both sides: in p1, three harness-only units (in `dhw_schedule.py`, `learner_progress.py` and `price_model.py`) were reworded until both read 0.

**The gate:**
- `python3 tools/audit/archscore/score.py --diff cb8edb65a5a9c0940dbe263acee49e02ba5f0b25`: `Architecture score: dS +0.0000 NULL`.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`, rc 0.
- `PYTHONPATH=tests/hastub python3 tests/entities.py` did not finish locally: `timeout 1500` killed it (rc 124), with the machine at load1 100 to 142. CI is the authority for it.
- `PYTHONPATH=tests/hastub python3 tests/doc_claims.py` at 7f218357d2: `ALL 441 checks PASSED`, including `no tests/ or production comment or docstring gains a sentence over 40 words (comment ratchet)`. Later commits touch only `tests/closures.json` and `dev/audit/harnesses/`.
- `PYTHONPATH=tests/hastub python3 tests/edge.py` at 7f218357d2: `ALL EDGE CASES PASS`.
- `python3 tools/pr/ci_predict.py` at this head: `no closures, fast, governance or instrument red predicted against cb8edb65a5a9`, after `--apply-inert` added the new harness to `tests/closures.json` (cf77639d6c..aabb3d8eab).
- `python3 -I tools/audit/seat/tmp_paths.py --check`: `0 refused`.
- Closure: `tests/closures.json`'s `tests/doc_claims.py` closure already holds all 97 production files the new scope reads, so no closure is re-recorded for the scope change. The new harness is classified by `tools/pr/ci_predict.py --apply-inert` (above).
- The scope reads `MODE: FULL` (reason: `tests/closure.py changes the gate itself`). The reason is #3808's `closure.py` change in the stack, and CI runs the full suite.
- Goldens: none move, and both claim files are byte-identical to the base.

**The release command** (design section 3 B), run at dispatch against `origin/handoff/audit-r10-roster`, printed 27 RELEASED and 70 HELD files. Its RELEASED list is this part's file set.

## Red checks

- `tests / fast` and `gate`: `tests/features.py`'s lift-peak check is red on main at cb8edb65a5. It is inherited from main, not caused by this diff. The cause is a BLAS-dependent float, and hotfix #3815 is in flight for it. This diff changes no code token in any production file (`--text-only` above), so it cannot move that float. No cheaper detector is owed here; the hotfix carries the root cause.
- `tests / closures`, `tests / closures-autofix` and `tests / fast (3.14)`: red on the stacked predecessor's commits (#3808, `fix/r11-seam-comments-tests`), which this branch carries as ancestry. They are inherited from #3808, not caused by this diff, which adds no code token to any production file. The cheaper detector is the one that already caught them, #3808's own check run; its cause and countermeasure are answered on #3808, so no second detector is owed here, and they clear when #3808 merges and this branch is rebased onto main.
- Any other red #3808's own head carries, such as `pr-contract`, is inherited from the stacked predecessor too. It is answered on #3808, not here.

## Forward-carry

- **To the later parts of this group (p2 to p13), from the approved plan's part list.** Each part reads its files with `dev/audit/harnesses/r11_comments_production_reconcile.py $EXPORT <files>` at its base and its head, and pays both columns to 0. A harness-only unit is paid by rewording, because the end-of-group line asks `c5_long.py` and `comments.py` to read 0. Three things decide whether a sentence splits. A bold heading's full stop has to move outside the `**` (`**Title**.`) to split for either rule. A `:` or `;` never splits. A sentence after a `::` code block joins the example's tokens under the harness rule, so it has to stay short. Carry: dismissed: owed by this group's own later parts, which the approved design names (R11-SEAM-comments-production, item parts-read-reconcile; the carry audit's group pattern does not read a lowercase seam id)
- **D5-s3-02** rides the first part dispatched after R11-SEAM-inputs-guards merges (design ruling 1). Carry: dismissed: design ruling 1 already places it in this group's later part (R11-SEAM-comments-production, item comfort-band-part)

## Friction

- roster-vs-design: contradiction: the approved design's section 3 A has this group write the ratchet script, and the roster carry, an orchestrator decision under mandate 6893738184, has R11-SEAM-comments-tests write it and this group consume it. This part followed the carry, because it is the later record and ADR-001 allows one script only, and it stacks on #3808 to do so. Carry: dismissed: the carry is the later record and this part follows it
