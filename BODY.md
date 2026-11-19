R11-SEAM-comments-tests part 1 (ADR-010; approved design `design/R11-SEAM-comments-tests` at a2823ffea00a570b2cba42ba6f65e3965ea96942, sections 3 A and 6). This part does three things:

- It lands the shared 40-word comment ratchet, `tests/comment_ratchet.py`. Per the carry on `handoff/audit-r10-roster` at 53871a0b84, this group writes it and comments-production consumes it.
- It runs the ratchet as an arm of `tests/doc_claims.py`.
- It pays every long unit in the files the release command prints RELEASED for p1: `tests/hastub/**` and `tests/throwaway_git.sh`.

Findings: D5-s9-04 (C5, partial: the p1 files) and D5-s9-01 (stale paths, the p1 files: none at the base).

**The rule.** `text_ledger.units_of(path, text, "D5")` yields each comment block and docstring. Comment markers are stripped. Each unit is split into paragraphs at blank lines, rule and banner lines, list items, trailing comments on code lines, and indented blocks that open after a blank line or a `:` line. `text_ledger.sentences` then splits each paragraph. A unit is long when one sentence has more than 40 words.

**What the ratchet compares.** The base is `mutation_table.ratchet_base("changed", base)`. The ratchet refuses a file present at both ends that gains long units, and refuses a rise in the scope total. A file new at HEAD is counted only by the total. An unresolvable base refuses.

**How it runs.** `--text-only REF` prints `code_changed_files` and `line_shifted_hunks`. `SCOPE` is the one list comments-production extends (`in_scope`).

**Departure from the design, raised here.** Section 3 B adds a `run` line for the ratchet to `tests/run.sh`. This part runs the ratchet as a `doc_claims.py` arm instead. The comments-production verdict's note `script-runs-row` names that route. A new selectable script adds one recording to every full-case run. `tests/ci_budgets.json` caps `script_runs_per_push` at 54 and `script_runs_full_case_pr` at 68, and there are 33 recorded closures. So in `run.sh`, `comment_ratchet.py` joins both script-accounting exclusion lists, the same shape as `throwaway_git.py`. That is one added line and one name in the ran-check's `case` line, and `entities.py` pins the two lists equal.

**Alternatives that lost:**
- A selectable script plus a `ci_budgets.json` raise. That is a raise where an arm needs none.
- An arm in `entities.py`. Every `tests/` edit would then select an 868 s script, where `doc_claims.py` takes 11 s.
- Reading the head through `git cat-file` to keep the closure small. That hides the dependency: a `tests/`-only change would not select the arm that judges it.

**Closure.** `tools/audit/text_ledger.py` joins `INERT_EXCEPT`. Three INERT entries were read by the ratchet, so they leave the INERT list and move into `doc_claims.py`'s closure: `tests/card_browser.mjs`, `tests/setup_qa_render.mjs` and `tests/throwaway_git.sh`. `comment_ratchet.py` joins `NOT_A_TEST`. `doc_claims.py`'s closure is re-recorded with `derive_closures.sh --single` on Linux.

**Roster carry 0 (the shared ratchet script)** is answered here: this part writes `tests/comment_ratchet.py` as the one script, and comments-production consumes it. No `run.sh` line is added; it runs as a `doc_claims.py` arm.

**Hand-off notes for the next parts (not finding items; the roster ids of these seams hold lowercase letters, which the carry audit's group pattern does not read).**
- **The harnesses cannot read 0 for some units.** The design's end-of-group line asks the three harnesses to read 0. On the units classed above they read a marker as a word or join a banner to prose, so they stay non-zero after every real long sentence is split. Each later part reads its files by the ratchet. On a harness-only unit it records the class from `dev/audit/harnesses/r11_comments_ratchet_reconcile.py` rather than rewording prose that is already under 40 words. Owed to: the R11-SEAM-comments-tests parts after p1.
- **How comments-production consumes the ratchet.** The script is `tests/comment_ratchet.py` and its scope is `in_scope()`. It runs as `doc_claims.py`'s `check_comment_length` arm, with no `run.sh` line. Adding the package's scope makes `doc_claims.py`'s closure read every package module and the card. Re-record it with `--single` and check `inert_reads`. Owed to: the R11-SEAM-comments-production part.
- Design reconcile, section 6 vs the three harnesses section 6 asks the script's per-file totals to equal three harnesses "to the unit", but s7 and s9 count sentences, s8 counts units, and on these cells the three disagree with each other on `#:` markers, banners and bullets (52 harness-only units, classed by `dev/audit/harnesses/r11_comments_ratchet_reconcile.py`) Owed to: the R11-SEAM-comments-production part.

## Head

09d0ec868fa37aa143a2029a270c38d63d1e90ba (origin/main 1723f9fdc9, 2026-11-19T03:05Z)

## Mutation proof

Command: `python3 dev/audit/harnesses/r11_comments_ratchet_mutants.py`, which prints `RESULT baseline_rc=0` and `RESULT killed=9 survived=0`. For each mutant it rewrites `tests/comment_ratchet.py`, runs `--self-test`, prints the FAIL lines and restores the file. Each mutant targets a predicate the design's section 6 names:

- `> MAX_WORDS` becomes `>=`: KILLED by "a 40-word sentence (the null control) is accepted", "a shell comment marker is stripped before the count" and "a rule line is not a word of the sentence after it".
- The per-file compare becomes `> len(old) + 1`: KILLED by "a 41-word sentence planted in a Python comment is refused", "a 41-word sentence planted in a shell comment is refused" and "a file shrinking while another grows is refused per file".
- The total compare becomes `th > tb + 1`: KILLED by "a long unit added in a new file is refused".
- The new-file branch: `old = old or []`, so a new file is compared per file. KILLED by "a long unit moved to a new file is accepted".
- Base resolution: `ref = ref or "HEAD"` in place of returning None. KILLED by "a base the checkout cannot resolve refuses (a shallow clone fails closed)".
- `.sh` marker stripping: `#` dropped from the marker list. KILLED by "a 40-word sentence (the null control) is accepted", "a shell comment marker is stripped before the count", "a rule line is not a word of the sentence after it" and "a list item ends the sentence before it".
- `--text-only` code arm: the docstring blanking removed. KILLED by "a docstring edit does not read as code".
- `--text-only` hunk arm: `and False`. KILLED by "a line-neutral rewrite reads 0 shifted hunks, an added line 1".
- `--text-only` comment strip for `.sh`/`.mjs`: `pass`. KILLED by "a shell comment edit does not read as code, a shell token does".

Every kill is a named arm and none is a crash.

**Failing test first.** A 41-word comment was planted at the end of `tests/edge.py`:
- At 1723f9fdc9 (no ratchet), `PYTHONPATH=tests/hastub:tests:custom_components python3 tests/doc_claims.py` reads `ALL 439 checks PASSED` with the plant in place.
- At this head, `python3 tests/comment_ratchet.py` with the same plant prints `REFUSE tests/edge.py: long units 0 -> 1; new: "word word word ..."` and exits 1.
- `prepr.sh`'s `MUTANT_CMD` draws only added `.py` lines outside `tests/`, and this diff has none.

## Null control

- **The self-test's 40-word sentence** passes in a Python comment and in a shell comment.
- **The unchanged tree** is accepted (`decide(base, base)` is empty).
- **The finders' harness outside the part:** `s9/comments.py` C5-long reads 809 at the base and 809 at the head over every file outside p1, with no file moved.
- **`s9/stale_paths.py`** reads 18 at both ends, all outside the part.
- **`--text-only` controls:** a planted assignment in `const.py` and a planted `export` in `throwaway_git.sh` each read as a code change. A planted blank line reads 1 shifted hunk.

## Figures

<!-- figure-block: scope-line mb=1723f9fdc9d8a6e6987190d2887686297a621dd4 head=09d0ec868fa37aa143a2029a270c38d63d1e90ba -->
~~~text
MODE: FULL -- every test script runs, nothing is scoped out.
~~~
<!-- /figure-block -->

Commands are run from the repository root. `$EXPORT` is `git archive origin/plan/r11 dev/audit/rounds/round11/D5/s7 dev/audit/rounds/round11/D5/s8 dev/audit/rounds/round11/D5/s9`. The harnesses are cited from that export, as `fixer.md` step 3 requires, because they are not in the tree.

**The ratchet:**
- `python3 tests/comment_ratchet.py` at this head: `RESULT base=1723f9fdc9d8 files=96 long_units_base=1638 long_units_head=1614`. The 24 units paid are the p1 files' long units: 24 at the base and 0 at the head.
- `python3 tests/comment_ratchet.py --self-test`: OK, 22 arms.
- `python3 tests/comment_ratchet.py --text-only 1723f9fdc9d8a6e6987190d2887686297a621dd4`: `RESULT code_changed_files=5 line_shifted_hunks=9`. Its CODE lines name the five files of the ratchet's code and pins: `closure.py`, `comment_ratchet.py` (new), `doc_claims.py`, `entities.py` and `run.sh`. No CODE or SHIFTED line names a `tests/hastub/` file or `throwaway_git.sh`, so the 14 text files change no code token and keep every line.

**The finders' harnesses (D5-s9-04, D5-s9-01):**
- `PYTHONPATH=tests/hastub python3 $EXPORT/dev/audit/rounds/round11/D5/s9/comments.py --repo . --ref 1723f9fdc9d8a6e6987190d2887686297a621dd4 --show` prints `RESULT C5-long=824`, 15 of them in p1 files. The same command at `--ref 5047360c746d9c44e3db79c07af5a106382f6ba5` (the head after the text edits) prints `RESULT C5-long=809`, none in p1 files. Later commits touch no comment text in p1 files.
- `PYTHONPATH=tests/hastub python3 $EXPORT/dev/audit/rounds/round11/D5/s9/stale_paths.py --repo . --ref 1723f9fdc9d8a6e6987190d2887686297a621dd4` and the same at `--ref 5047360c746d9c44e3db79c07af5a106382f6ba5` each print `RESULT stale_refs=18`. No STALE line names a p1 file at either end.
- `python3 tools/audit/seat/moved_paths.py tests/throwaway_git.sh $(git ls-files tests/hastub)`: `161 moved path(s) from tests/layout.json, 0 hit(s) in 36 file(s)`.
- The s7 harness (its SEAT_FILES: features, finite_boundary, frontend) and the s8 harness (cells `tests/[a-g]*`) have no cell over a p1 file. Their figures are the reconcile below.

**Reconcile at p1's head.** The command is `PYTHONPATH=tests/hastub python3 dev/audit/harnesses/r11_comments_ratchet_reconcile.py $EXPORT`. It imports each harness's own long-sentence function. It compares, unit by unit on each harness's cells, the units the harness flags against `comment_ratchet.long_units`:
- `RESULT s9_harness=588 s9_script=758`, `s7_harness=478 s7_script=475`, `s8_harness=399 s8_script=381`, `harness_only=52`, `script_only=201`.
- Units only the script flags come from the harnesses' extra sentence breaks: `;` and a line ending `:` (s9), and an indented continuation line (s9 at 3 spaces, s8 at 5). The ratchet does not split there, so on those cells it reads a superset.
- Units only a harness flags are classed by the same harness, which reverts the script's rules in memory, smallest set first: `class_colon=20`, `class_banner=22`, `class_trailing=5`, `class_banner_trailing=1`, `class_banner_rule=3`, and one `UNCLASSED` (`tests/arch_score_head.py:2`, s8: its marker strip removes the docstring's `*` bullets, so seven list items read as one sentence).
  - `colon`: the harness counts the `:` of a `#:` marker as a word.
  - `banner`: the harness joins a `--- title ---` banner to the next sentence.
  - `trailing`: the harness joins trailing `# noqa` comments to the block.
  - `rule`: the harness counts a rule line as a word.
  - In each case the harness reads a marker as prose. The script keeps the D5 rule and records no exception.

**The gate:**
- `python3 tools/audit/archscore/score.py --diff 1723f9fdc9d8a6e6987190d2887686297a621dd4`: `Architecture score: dS +0.0000 NULL`.
- `python3 tests/structure.py`: rc 0.
- `PYTHONPATH=tests/hastub python3 tests/closure.py selftest`: `ALL 118 closure shrink pins PASSED`. Its first run caught the `--no-renames` gap, fixed in abf81272ce.
- `PYTHONPATH=tests/hastub:tests:custom_components python3 tests/doc_claims.py`: `ALL 441 checks PASSED` (the two new arms included).
- `PYTHONPATH=tests/hastub python3 tests/entities.py`: `ALL 2732 ENTITY CHECKS PASSED`, after the first run's 3 reds were repaired in f9dedd0974: the two run.sh exclusion lists, the dst_checks.py re-derive set, and the policy_lint files_tokens cap on tests/README.md, which dropped the README row.
- `python3 tests/layout.py` and `python3 tests/env_drift.py --claims-only origin/main`: rc 0.
- The scope reads `MODE: FULL` (reason: `tests/closure.py changes the gate itself`). That is a diff the gate cannot scope, and CI runs the full suite.
- Goldens: none move, and both claim files are byte-identical to the base.

## Red checks

none

## Forward-carry

none

## Friction

none
