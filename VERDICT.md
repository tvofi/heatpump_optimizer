Design review: approve 576654cce6e4fc0c643a2184e65d030a7fe0decf

Reviewed: `dev/programme/designs/R10-USER-DOCS-FINAL.md` at 576654cce6e4fc0c643a2184e65d030a7fe0decf on `design/R10-USER-DOCS-FINAL`, round 2 of at most 3. The note is one commit on be9f30ec9 and was reviewed as a delta against the round-1 verdict 37371ccebb9ef8b2fa3f44cdc4bbe532a41fe9fc, from a fresh detached worktree at that SHA. The tree is still 14ed13551 outside the note. Roster read at `handoff/audit-r10-roster` aaceb6a3e98fc49e8c0e941f96031d7d0a932061. Token count: not reported by this harness.

## Round-1 revise points

1. **Keyed delta: closed.** Section 2 now specifies `surface_delta(old, new)` and `--surfaces --against FILE` with three sections. `LANDED` holds keys only in new, `REMOVED` holds keys only in old, and `CHANGED` holds keys in both whose label, home-found or default differs, with the fields and the old and new values. A relabel, a lost home and a changed default therefore never read as remove plus add. The red fixtures are one per section, and the default-change fixture must print exactly one `CHANGED` line and nothing else; the null control is identical rows. Both runs set cwd to their own worktree. The key is unique as the note claims. Measured: 0 duplicate `(platform, name)` among 82 entities, 0 duplicate `_OPTION_FIELDS` keys among 205, and one blank key (`building_preset`), which carry `udf-blank-option-key` exempts.
2. **Inline last-cell rule: closed.** Re-run on this tree at README:686 (`evidence/r2_md_tables.out`). With no marker, `doc_orphaned_table_rows=0` and `doc_misrendered_lines=0`. With an own-line marker above the row, both are 1. With the marker inline in the last cell, both are 0. This matches the note's table. Cell readers in both arms strip comments first.
3. **Census tag by wrapper: closed.** The census reads one dict, `WIRING_DOCS` ∪ the six `docs/` user pages, keyed by path, so README is read once and counted once. Each row gets `scope` from whether the match lies inside `<!-- … -->`. The wiring due note and the default `--markers` skip user rows. `--markers --user` prints `N user-doc marker(s), M due` and exits 1 while N > 0. Two misplacements are red: a bare marker on a user-only page, and a wrapped one in `docs/architecture.md` or `dev/README.md`. The premise holds at the current `origin/main` 460d7754: 0 `<!--` in each of README.md, the six pages, `docs/architecture.md` and `dev/README.md`, so the tag reclassifies no existing marker.

## Carry udf-marker-scope: sound

The ARCH-DOCS roster brief resolves "every target marker R10-ARCH-DOCS-FIRST left". Every marker that group left is bare: 0 comment wrappers exist in any wiring doc. So the carry's reading, the wiring rows the default `--markers` prints, covers every marker the brief gives ARCH-DOCS. It removes only markers this group creates, and those go to VERIFY, which owns them by `--markers --user`. ARCH-DOCS's scope does not shrink, and no marker is left without an owner. The default `--markers` skipping user rows is what makes the two end conditions independent.

## Owed by the orchestrator (not revise points)

- Section 3 keeps the R10-ARCH-SHAPES-CLASSIFIER marker "by orchestrator ruling, VERIFY gains an after-edge on that group". At roster aaceb6a3e, R10-USER-DOCS-VERIFY's `after` does not yet contain R10-ARCH-SHAPES-CLASSIFIER. That roster op is still owed.

## Notes for the fixer

- Carry: R10-USER-DOCS-FINAL (item udf-user-marker-path-mask). `doc_wiring_findings` (a) excuses an unresolved backticked path when its unit carries any marker (`_MARKER.search(unit)`). A comment-wrapped user marker on a README unit would therefore also mask a wiring path finding there. Count only `scope == "wiring"` matches for (a), and add a README fixture with a user marker beside a missing path that stays red.
