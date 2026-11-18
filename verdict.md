Design review: revise b71b07bf160d2152a0c9b1bfc9b2060b11d73854 sibling-design-conflict

Reviewer round 1. I read the note at b71b07bf160d2152a0c9b1bfc9b2060b11d73854 from a detached worktree, and the tree at the judged base 1723f9fdc9d8a6e6987190d2887686297a621dd4. The plan is plan/r11 at 50a932de3b (ADR-010, PLAN.json triage rows, the D5 s8 finding files, ISSUES.json). The roster is handoff/audit-r10-roster at 83ef6bc324. The sibling notes are design/R11-PRE-SHARED-FILES at 20cafac7df (approved at 9d71412cc0) and design/R11-SEAM-comments-production at 15dd4f5b3a (approved at 1a27d04c17). I reran no code.

## Revise point

1. design.md section 3 B, row p10, and section 3 C, "D5-s7-01, part p10". p10 is the file `tests/features.py`, and it is released once `R11-PRE-SHARED-FILES` merges, along with five other groups. The approved note design/R11-PRE-SHARED-FILES (20cafac7df, design.md:104 and table row 4 at :154) splits that script into one script per production module, with a committed splitter. Its part 4 therefore lands before p10 can dispatch, so p10 always targets a file that no longer exists. The split scripts are new paths, and no roster row names them, because the five behaviour groups list only `tests/features.py`. The release command as written would print them RELEASED while `R11-OUTSIDE-HONEST-DHW-RUNS`, `R11-CARRY-DRAWMAP`, `R11-SEAM-inputs-freshness`, `R11-SEAM-learners` and `R11-ARCH-fabric-learner` are still open. That breaks ADR-010's acceptance line ("a comment part's diff touches no file whose row in the hot-file order still has an open group"). Fix wanted: define p10 as the features scripts, meaning `tests/features.py` or, after PRE-SHARED-FILES part 4, the files its splitter writes. Make the release command hold every one of them on the `tests/features.py` row of any group that names that path, until the last of those groups merges. Re-anchor D5-s7-01's three names, its count (features.py:6858 at the base) and the 460-unit figures to "whichever split script carries the block". Section 6's end-of-group check must then read the harnesses over the split scripts. The same applies to any other part whose files the split touches (the shared helper module is a new `tests/*.py`).

## Checked with no point raised

- Seam. Every module the note names resolves at 1723f9fd: `tools/audit/text_ledger.py` (`sentences` :57, `units_of` :228), `tests/mutation_table.py` `ratchet_base` :838, `tools/audit/seat/moved_paths.py`, `tests/layout.json`, and all eleven successor paths in section 3 C, including `tools/coverage/partition.py`. The rename targets `pump_arbiter.FeedbackRun.sent_c` (:323, :339) and `_feedback` (:999) exist. One owner holds the 40-word rule. The script moves to this group's p1, and ADR-010 part 2 gives both comment groups that ratchet.
- Shape. Every behaviour change is named by D5-s9-04 (with D5-s7-01..03 merged in), D5-s9-01 (with D5-s9-02, -03 and D5-s8-03 merged in), D5-s8-04 or D5-s8-05. The ratchet script is ADR-010 part 2's, and it is the script the comments-production verdict already approved, with only its scope changed.
- Release table. I ran the release command adapted to `tests/` at 1723f9fd against the roster at 83ef6bc324: 87 RELEASED and 8 HELD. The held files and their holders match rows p4..p10 exactly.
- Sibling sites. The class's other members, D5-s8-01/-02 and D5-s8-06/-07, are deferred to round 12 as instrument text (PLAN.json triage). No other group carries a tests/ comment finding.
- Evidence plan. The self-test plants fail today, because no script exists. The harnesses are the finders' (s7 m4_comments, s8 m4_ledger, s9 comments/stale_paths), and their perturb arms move. Goldens and both claim files stay byte-identical.
- Cost. The note proposes one script plus ten text-only parts, which fits XL once p10 is redefined.

## Routed

- decision: orchestrator. The note moves the shared ratchet script from comments-production p1 (approved at 1a27d04c17 on ADR-010 part 2) to this group's p1, because b3fdb779e7 gave comments-production ten after edges. The approved comments-production note still tells its fixer to write the script. Only a carry delivered to that group's roster brief, or a re-statement of its approved note, prevents two scripts. Confirm the reassignment and the carry's destination before either fixer dispatches.

## Notes for the fixer

- The comments-production release command prefixes every non-`custom` glob with the package path and keeps only top-level package files. Taken literally with `git ls-files tests/`, nothing matches and every file reads RELEASED. Do not prefix `tests/` globs, and accept `.py`/`.mjs`/`.sh` at any depth under `tests/`. Note that fnmatch's `*` matches across `/`, so `tests/*.py` also covers `tests/hastub/`. Carry: R11-SEAM-comments-tests (item release-command-tests-globs)
- Section 3 C lists `docs/delivery` among cites with no successor. D5-s8-03's own claim names its successor, `dev/programme/delivery/`, which is tracked at 1723f9fd. Respell that path instead of pinning it or dropping it. Carry: R11-SEAM-comments-tests (item docs-delivery-successor)

Seat token count: not reported by this harness.
