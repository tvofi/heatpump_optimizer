R11-SEAM-comments-tests part 2 (ADR-010; approved design `design/R11-SEAM-comments-tests` at a2823ffea00a570b2cba42ba6f65e3965ea96942, sections 3 B, 3 C and 6). Part 1 (#3808) landed `tests/comment_ratchet.py`. This part does the C5 and C2 text work on the files the design's release command prints RELEASED for p2: the tracked `tests/*.mjs` files.

**The part's files.** The release command in design section 3 B was re-run at this base against `origin/handoff/audit-r10-roster` (3a1a252c2e). It prints 72 RELEASED and 24 HELD. The RELEASED `.mjs` files are `card.mjs`, `card_browser.mjs`, `card_drift.mjs`, `card_rig.mjs`, `dom_stub.mjs`, `md_tables.mjs`, `node_fs_trace.mjs` and `setup_qa_render.mjs`. `node_fs_trace.mjs` holds no long unit and no stale path, so it has no edit.

**The edits.**
- C5: every sentence over 40 words is split at one of its own separators (` -- `, `;`, `:`, `, so`). Each split keeps the reason, constraint, number and unit it stated. Each pair keeps its line count, and every edited line is a comment line.
- C2: the four dangling cites in `card.mjs` are pinned to the SHA that holds the file (design section 3 C, "cites with no successor"). `card_shapes.mjs` is cited at 9d8a979823 (tag `archive/handoff-audit-r10-arch2-s5`, path `dev/audit/rounds/round10/D7/arch2-s5/card_shapes.mjs`). `DESIGN.md` is cited at 7bca8ab36b (tag `archive/handoff/audit-r9-alt`, path `handoff/round9/state/alt/design/DESIGN.md`). Each is checked with `git cat-file -e <sha>:<path>`. The cited symbols are in the pinned file: `char_width_inline` and `finite_inline` (`git show 9d8a979823:dev/audit/rounds/round10/D7/arch2-s5/card_shapes.mjs | grep -c 'char_width_inline\|finite_inline'` prints 4), and `DESIGN.md`'s section 4 is "Plan chart, concept A (R9-UI-4; ...)".
- One sentence under a wrapped banner (`card.mjs`, the `D4-s1-05 / P9-rca3` banner) is split too. Its banner line ends `---`, so the ratchet reads that line as a heading and the run-on below it as under 40 words. The s8 harness joins them and reads the run-on.

Findings advanced: D5-s9-04 (C5, partial: the p2 files), D5-s8-05 (the card.mjs unresolved units, pinned), and the C5 cells of D5-s8 on these files. Class issues #3746, #3777 and #3778 stay open: later parts own the files outside p2.

**Carry 0** (the shared 40-word comment ratchet script) was answered by part 1 (#3808), which wrote `tests/comment_ratchet.py` as the one script. This part adds no ratchet code and no second script.

## Head

2e4260ccd7a1f8d07aeef2bab53c1452e2a544d4 (origin/main 78d3b4022154b2cc2792df8ebf4a5d7753e8ed7f, 2026-11-21T13:20Z)

## Mutation proof

n/a: this part changes no code token. `python3 tests/comment_ratchet.py --text-only 78d3b4022154b2cc2792df8ebf4a5d7753e8ed7f` prints `RESULT code_changed_files=0 line_shifted_hunks=0`. `prepr.sh`'s `MUTANT_CMD` draws only added `.py` lines outside `tests/` and `dev/`, and the diff has none. The design's section 6 assigns mutation targets to p1 only.

**The detector's control at this head.** A local branch was set at this head and passed as `--base`, so the ratchet's base is this part's paid-down tree:
- A 41-word comment appended to `tests/card.mjs`: `python3 tests/comment_ratchet.py --base <that branch>` prints `REFUSE tests/card.mjs: long units 0 -> 1` and `REFUSE scope total: long units 1482 -> 1483`, and exits 1.
- A 40-word comment in the same place (the null control): `comment_ratchet: OK`.

## Null control

- **Outside the part:** `$EXPORT/dev/audit/rounds/round11/D5/s9/comments.py --show` lists the same C5-long rows outside the p2 files at the base and at this head. The two lists are compared with `diff` after filtering out the p2 files, and they are identical.
- **`$EXPORT/dev/audit/rounds/round11/D5/s9/stale_paths.py`** reads `stale_refs=18` at both ends. No STALE line names a p2 file at either end.
- **`node_fs_trace.mjs`** is unedited and reads 0 in the ratchet and in s8 at both ends.

## Figures

<!-- figure-block: scope-line mb=78d3b4022154b2cc2792df8ebf4a5d7753e8ed7f head=2e4260ccd7a1f8d07aeef2bab53c1452e2a544d4 -->
~~~text
MODE: SCOPED -- 5 script(s) run, 28 scoped out.
~~~
<!-- /figure-block -->

Commands are run from the repository root. `$EXPORT` is `git archive origin/plan/r11 dev/audit/rounds/round11/D5/s7 dev/audit/rounds/round11/D5/s8 dev/audit/rounds/round11/D5/s9`, taken at plan/r11 dbdc1d95fe. sha1: `$EXPORT/dev/audit/rounds/round11/D5/s9/comments.py` c6cdf8a829, `$EXPORT/dev/audit/rounds/round11/D5/s9/stale_paths.py` 6ff0d47032, `$EXPORT/dev/audit/rounds/round11/D5/s8/m4_ledger.py` d77b7259bd.

**The ratchet:**
- `python3 tests/comment_ratchet.py`: `RESULT base=78d3b4022154 files=96 long_units_base=1622 long_units_head=1482`. The 140 units paid are the p2 files' long units at the base: `card.mjs` 97, `card_browser.mjs` 21, `card_rig.mjs` 13, `card_drift.mjs` 4, `md_tables.mjs` 2, `dom_stub.mjs` 2 and `setup_qa_render.mjs` 1. The per-file counts come from `python3 tests/comment_ratchet.py --show` at the base, grouped by file. At this head the same command lists no p2 file.
- `python3 tests/comment_ratchet.py --text-only 78d3b4022154b2cc2792df8ebf4a5d7753e8ed7f`: `RESULT code_changed_files=0 line_shifted_hunks=0`.

**The finders' harnesses:**
- `PYTHONPATH=tests/hastub python3 $EXPORT/dev/audit/rounds/round11/D5/s9/comments.py --repo . --ref <ref> --show`: `RESULT C5-long=809` at 78d3b40221 and `RESULT C5-long=805` at this head. The 4 at the base are p2 cells (`md_tables.mjs` 3, `setup_qa_render.mjs` 1), and this head has none.
- `PYTHONPATH=tests/hastub python3 $EXPORT/dev/audit/rounds/round11/D5/s9/stale_paths.py --repo . --ref <ref>`: `RESULT stale_refs=18` at both ends, none in a p2 file.
- `PYTHONPATH=tests/hastub python3 $EXPORT/dev/audit/rounds/round11/D5/s8/m4_ledger.py --repo . --ref <ref> --file tests/<f>.mjs`, one run per p2 file. `long_sentence_units`: `card.mjs` 90 -> 17 and `card_browser.mjs` 2 -> 2, with every other p2 file 0 at both ends. `unresolved_units`: `card.mjs` 4 -> 4, every other p2 file 0.
  - The 19 long units at the head are the part-1 `banner` class. In each one the harness joins a `--- title ---` banner line to the sentence after it, and no sentence below the banner is over 40 words. Enumerator: the harness's own `blocks_of` and `text_ledger.sentences` over the two files' units, printing every sentence over 40 words. Every sentence it printed opens with its banner. The class is from `dev/audit/harnesses/r11_comments_ratchet_reconcile.py`. That reconcile, run at this head, prints `class_banner=28`, `class_banner_rule=3`, `class_banner_trailing=1`, `class_colon=20` and `class_trailing=5`. Its only `UNCLASSED` line is part 1's `tests/arch_score_head.py:2`.
  - The 4 unresolved units are the four pinned cites. The harness's own adjudication rule counts "a citation pinned to a SHA or branch" as not stale. Its `ADJ` table is keyed on the seat's reading at 92d38ecb, so it does not list these four.
- `python3 tools/audit/seat/moved_paths.py` over the eight p2 files: `5 hit(s) in 8 file(s)`. All five are code tokens, not comment text: the `docs/HANDOVER.md` test inputs to `movesClaimable`/`claimsAreThisBranchs` in `card.mjs`, and the `.claude/workflows/vendor/` fallback `require` in `md_tables.mjs`. A text-only part leaves them as they are.
- `$EXPORT/dev/audit/rounds/round11/D5/s7/m4_comments.py` has no `.mjs` file in its `SEAT_FILES`.

**The gate:**
- Scope: `python3 tests/closure.py select --diff 78d3b4022154b2cc2792df8ebf4a5d7753e8ed7f` reads `MODE: SCOPED -- 5 script(s) run, 28 scoped out`. Its `scope.run` names `tests/doc_claims.py` (`ALL 441 checks PASSED`), `tests/plan_view.py` (`plan reason codes, price provenance and slot energy OK`), `node tests/md_tables.mjs` (`doc_misrendered_lines=0`), `node tests/card.mjs` (`ALL CARD CHECKS PASSED`) and `node tests/card_drift.mjs` (`identical in all 45 states`). Each ran with `PYTHONPATH=tests/hastub:tests:custom_components` at 2e4260ccd7^ (af99fdb48b). The last commit edits one `card.mjs` comment line, and `--text-only` reads 0 code changes across the diff.
- The `run_always` scripts: `env_drift.py --claims-only origin/main` (`claims hygiene: origin/main ok`), `closure.py selftest` (`ALL 118 closure shrink pins PASSED`), `layout.py` (`layout self-test: ok`) and `harness_headers.py` (`ALL 115 HARNESS HEADER CHECKS PASSED`).
- `card_browser.mjs` is a comment-only diff and is left to CI (no scope selects it).
- `python3 tools/audit/archscore/score.py --diff 78d3b4022154b2cc2792df8ebf4a5d7753e8ed7f`: `Architecture score: dS +0.0000 NULL`.
- `python3 tests/structure.py`: rc 0.
- Goldens: none move. `git diff --quiet origin/main -- tests/golden/claimed_drift.txt tests/golden/card_claimed_drift.txt` exits 0.

## Red checks

none

## Forward-carry

none

## Friction

none
