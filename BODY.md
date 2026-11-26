Flow card FG-1 (round 11), approved by the owner on 2026-11-26 ("yes to all cards, implementation asap") with an exception to the tooling freeze. Cause 2 of the flow-green study: hand-kept counts, and "N until X" history chains, in files that every module-adding or option-adding pull request edits. Two branches each re-derive the count from their own tree. git then merges the two sentences as text, and the merged tree derives a third number (`rca-pairnote.md`: #3838, #3866, #3870; #3863, #3872 and #3882 were the same class).

This change deletes those counts from the prose and keeps every check deriving and printing them:

- `docs/architecture.md`: the opening sentence and the boundary paragraph state no module count ("fewer than half of the modules", "These modules import", "Every other module").
- `tests/entities.py` #939 block: it prints the derived counts on a `derived:` line. The opening, boundary and HA-free checks assert the tree's own relations: importers are fewer than half the package, the named list equals the AST walk, and the free remainder is the package less the importers and the one toucher. They no longer compare a number the prose carries.
- `tests/deployment_shape.py`: the #1218 note keeps its markers and its empty-closure scripts. It drops the "all N files", the "N of the M script pairs", both "until" chains and the exactly-1.00 list with its shared-file counts. `tests/entities.py`'s #1218 block prints all of these, and refuses a count written back into the note.
- `tests/doc_claims.py`: the four module-count shapes stay in `_PROSE_COUNT_SHAPES`, so a module count written back is still claimed and compared. They are also refused (`_ABSENT_COUNT_SHAPES`), and the corpus-coverage anchor no longer requires them. The derived quantities are printed. The deletion null control moves from architecture.md to README.md, because README.md is now the document that states shapes no other document states.
- `dev/audit/rounds/round4/D6/claims.py`: the header pins invariants only (`claims_false=0`, `arch_map_missing=0`, the new `arch_map_phantom=0` and `ha_importers_unnamed=0`, and the unchanged claim and config-row totals without their chains). `arch_modules_on_disk`, `arch_map_listed` and `ha_module_level_importers` are still printed on every run. C32 reads the "fewer than half" sentence. C33 and C34 carry no count in their results, and C34 now checks that the boundary list names each module once and only modules on disk. `claims.md` and `claims.json` are regenerated.
- The same class found by grep (`git grep -cE "[0-9]+ until "`, outside run logs): `dev/audit/rounds/round3/D5/option_doc_coverage.py` drops the option-field count chains and the two rendered-count RESULT lines. The option-field counts are still printed, and a new printed `option_pages_unrendered=0` is pinned. `dev/audit/rounds/round4/D9/h7_memory_gate.py` drops its two "until" chains. `tools/audit/prose_counts_census.py` drops its "eleven count SHAPES".

No check is removed. The checks that read a number from prose now read a relation that the tree derives. Not policy, no budget.

No issue tracks card FG-1, so this leaves every issue open (#3885 among them).

## Head

df9b66b68a729490753b05b1fa8fd0dd5732114c. It is f4ff2700d0 merged with `origin/main` e91329c2c27c4ce4013b262a8a62986574c02336 (2026-11-26T08:38:44Z). The merge was taken because #3863 landed `dhw_start.py` and re-derived the very counts this change deletes, so all five carrying files conflicted. Every conflict block was resolved to this branch's side. `git diff f4ff2700d0 df9b66b68a` on the eight changed files shows only main's own lines, and the D6 register was regenerated. The `(merged head)` figures below were taken at df9b66b68a. The mutation runs and the `(f4ff2700d0)` figures were taken before the merge, which brought in no line of this diff.

## Mutation proof

There is no production code. Each mutant breaks a derivation or writes a count back, in a separate worktree at this head (`mutA.py`, `mutB.py` in the seat's scratch, not tracked):

- `claims.py`: `if _hit:` changed to `if False:` (the importer derivation reads nothing). The run prints `RESULT claims_false=2` (C32 and C35 FALSE) against the header's `claims_false=0`, which `tests/harness_headers.py` compares.
- `option_doc_coverage.py`: `pages_ok += 1` changed to `pages_ok += 0`. The run prints `RESULT option_pages_unrendered=25` against the header's 0.
- `tests/entities.py`: `_arch_ha_import` returns False. `tests/entities.py`: 6 of 2778 failed. Four are "architecture.md's opening share of homeassistant importers is the tree's", "... HA boundary names exactly the module-level importers", "... one function-level toucher is the only one" and "... HA-free remainder is the tree's".
- `tests/deployment_shape.py`: "all 123 files" written back into the #1218 note, in the same run. It also fails "and the lane's docstring is the selection-cost note, naming this block as the source of its numbers and carrying none of them (#1218, FG-1)" (`hand-kept counts -> ['all 123 files']`). The sixth is the load-dependent late-writer check that also failed at the head (see Figures).
- `tests/doc_claims.py`: `_ABSENT_QUANTITIES = frozenset()`. `tests/doc_claims.py`: 2 of 445 failed, "the reader corpus states no module count; entities.py and claims.py derive and print it (FG-1)" and "a true module count planted in a reader document is refused (null control)".
- Control, with no mutant: architecture.md's old opening ("104 modules, of which 36 import") restored. `tests/doc_claims.py`: 1 of 445 failed, the same refusal, naming `architecture.md:8 modules=104; architecture.md:8 modules_importing_homeassistant=36`. A true count written back is refused.

## Null control

At the merge base (`origin/main` e91329c2c2), `docs/architecture.md` states "105 modules, of which 36", "36 of the 105" and "The other 68", and `tests/deployment_shape.py` states "all 124 files" and "190 of the 561" with both chains. At dbdc71faea, two hours earlier, the same sentences read 104, 67, 123 and 184. On the head, `tests/doc_claims.py`'s planted-count control shows that a true module count is refused: "a true module count planted in a reader document is refused (null control)" passes, and it fails under the `frozenset()` mutant above.

## Figures

- `PYTHONPATH=tests/hastub:custom_components:tests python3 tests/entities.py` (merged head): every FG-1 check passes: the opening-share, boundary, toucher and HA-free-remainder checks, and the #1218 note check. Its `derived:` line reads `package modules=105 ... free of it=68` and its `derived (#1218):` line reads `all 124 production files; 190 of the 561 script pairs`, which are the numbers #3863 hand-wrote on main. The host was starved (2.4 CPU-minutes in 42 wall-minutes). The run is reported up to its last printed check, and CI is the authority for the remainder. It prints `derived:` and `derived (#1218):` lines carrying the numbers the prose dropped.
- `PYTHONPATH=tests/hastub:custom_components:tests python3 tests/entities.py` (f4ff2700d0, before a comment-only re-wrap): `1 of 2778 ENTITY CHECKS FAILED`, and every FG-1 check passes. The red is "a measured script's late-writing descendant is waited for, not recorded as nodata". It drives the coverage stage's descendant-wait bound, which this diff does not touch. The host was at load average 57-75 (`uptime`), and the same check failed in mutant A's run, which mutates nothing it reads.
- `PYTHONPATH=tests/hastub:custom_components:tests python3 tests/doc_claims.py` (merged head): `ALL 445 checks PASSED`.
- `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` (merged head): `claims_false=0`, `arch_map_missing=0`, `arch_map_phantom=0`, `ha_importers_unnamed=0`. It printed `arch_modules_on_disk=105` and `ha_module_level_importers=36`, and the regenerated `claims.md`/`claims.json` carry neither.
- `PYTHONPATH=tests/hastub:custom_components:tests python3 tests/harness_headers.py` (merged head): 33 RESULT comparisons on claims.py, option_doc_coverage.py and h7_memory_gate.py: 32 pass, and "the executed harnesses leave their committed output byte-identical" passes. 13 of 112 failed. Twelve are `sysid_estimator_frontier.py` at rc=124 ("wall limit 900s exceeded", cpu=166.1s), a file this diff does not touch, which was red the same way at f4ff2700d0. The thirteenth is h7's `inject2x_attrib_rule_fires` (printed False). Its input is a PROVISIONAL RSS probe, and the header pins only the boolean. Run alone at the same head (`PYTHONPATH=tests/hastub:custom_components:tests python3 dev/audit/rounds/round4/D9/h7_memory_gate.py`), it prints `inject2x_attrib_rule_fires=True` (`inject2x_attrib_rss_mb_PROVISIONAL=25` against the 20.55 MiB threshold). This diff changes only h7's header text.
- `python3 tests/comment_ratchet.py` (f4ff2700d0): `comment_ratchet: OK`, with long units equal at the base and the head.
- `python3 tests/structure.py` (f4ff2700d0): `STRUCTURE RATCHET PASSED`.
- `PYTHONPATH=tests/hastub python3 tests/deployment_shape.py` (f4ff2700d0): `ALL DEPLOYMENT SHAPE CHECKS PASSED`. `node tests/md_tables.mjs` (f4ff2700d0): `doc_orphaned_table_rows=0`, `doc_misrendered_lines=0`.
- `python3 tests/closure.py select --diff <merge-base>`: `MODE: SCOPED`. Scripts run: `deployment_shape.py`, `doc_claims.py`, `entities.py`, `harness_headers.py`, `md_tables.mjs`, `plan_view.py`, `card_drift.mjs`. plan_view.py and card_drift.mjs read none of the changed text and are left to CI.
- The class's seams, by rule: `git grep -cE "[0-9]+ until "`. Outside run logs and records (`dev/audit/rounds/round11/D3/s1/state/gates/*.log`, `dev/programme/`), it returns claims.py, deployment_shape.py, option_doc_coverage.py, h7_memory_gate.py, `naming_splits.py` (finder evidence, not a count chain: "stays 1 until ... is renamed"), `tools/pr/app_approve.sh` and `tools/audit/seat/record_beat.py` (each a single prose "until", not a count history). The first four are closed in this diff.

## Red checks

none

## Forward-carry

none

## Friction

none
