Design review: approve a2823ffea00a570b2cba42ba6f65e3965ea96942

Reviewer round 2. I read the note at a2823ffea0 from a detached worktree, and the diff from b71b07bf16. I checked it against the tree at the judged base 1723f9fdc9d8a6e6987190d2887686297a621dd4, the roster at origin/handoff/audit-r10-roster 83ef6bc324, plan/r11 PLAN.md, and the sibling note design/R11-PRE-SHARED-FILES at 20cafac7df (approved at 9d71412cc0). The only code I ran was the note's own release command, which reads git state.

## Round-1 point: answered

- p10 is now the features scripts. That means `tests/features.py`, or after the split, every `tests/` file added by the commit that deleted it, which includes the shared helper module. Each of those files is held on the `tests/features.py` row of every open group that names that path (design.md section 3 B, `fam`/`keys`).
- The release command in section 3 B, run from the root at 1723f9fd against roster 83ef6bc324, prints 71 RELEASED and 24 HELD, which matches the note. p4..p10 match their holders. p11 is the 16 files held by `R11-PRE-SHARED-FILES` alone: the 8 named in the note plus 8 more.
- D5-s7-01 is re-anchored by block, not by line. At the base, `features.py:6858` ("eight between-run", inside `_d901_gil_yield_inside_run` :6855), :87592 (`_feedback_sent`), :54916 (`PlantRig`) and :57373 (`w5-partition/partition.py`) all resolve.
- Section 6 reads the harnesses over the split scripts. `m4_comments.py` gets its `SEAT_FILES` through an import with no harness edit. Its null control reproduces 460/1/5 at the base. The end-of-group check sums each `features.py` row over the scripts.
- `run.sh` has no row in PLAN.md's "Hot-file order" table on plan/r11, so p1's single added `run` line keeps ADR-010's acceptance line, and its comment text waits for p11.
- Both round-1 carries are served: `release-command-tests-globs` (no `tests/` prefix, any depth) and `docs-delivery-successor` (respelled to `dev/programme/delivery/`).

## Checked with no point raised

- Seam, shape, sibling sites and cost: sections 1, 2, 4 and 5 are unchanged from round 1, which raised no point on them. p11 adds text-only edits under the same three edits and no code (section 6 mutation targets stay p1 only). It stays within XL.

## Routed

- decision: orchestrator, restated from round 1 and still open. Which group writes the shared ratchet script. The note now holds both p1s until one writer is confirmed and the carry lands in that group's roster brief (section 7). If the script stays in comments-production, this group's p1 shrinks to the scope addition.

## Notes for the fixer

- `fam` takes the files added by the single most recent commit that deleted `tests/features.py`. main merges with merge commits, so that is the branch commit, not the merge. If `R11-PRE-SHARED-FILES` part 4 adds the split scripts or the helper module in a different commit from the one that deletes the old script, `fam` misses them and they read RELEASED. At p10's dispatch, check that `fam` equals the splitter's output list (its committed splitter under `dev/audit/harnesses/`), and stop and report if it does not. Carry: R11-SEAM-comments-tests (item fam-one-commit)

Seat token count: not reported by this harness.
