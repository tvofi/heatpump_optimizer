Fix review: merge 1ef3784ca71ab75966862e4af77b04ad31fc8666

Round 2 (re-scoped; RO-2b split off). Head 1ef3784ca, still the branch head at posting.

Measured, all at 1ef3784ca in /Users/timmalmstrom/hpo-seats/review-1886-r2/wt:

- RESULT closures-repair: head inert_reads["tests/entities.py"]=["LICENSE"] and seconds 182.4 are byte-equal to entities.py.json in the closure-recordings artifact (11299180016) of CI run 37189159395; d2881302..1ef3784 touches only tests/closures.json; every other script's closure identical. Head's file list = artifact's plus tests/golden/card_claimed_drift.txt (grow-only union with the Darwin closure — over-approximation, the safe direction). merge --in-dir --partial is closure.py's own documented shape.
- RESULT mutant: layout.py locate -> `return p`: budget_raise_gate --self-test 2 failed; clean head 202/0.
- RESULT adjacency: planted `git status --short` / `ls` between listing and checkout -> grader NOT pinned; adjacent control pinned. codeowners_gap --self-test 50/9/0; --check uncovered_files=0. (A comment line between stays pinned — inert, executes nothing.)
- RESULT dual_path at head: graders 0/16, neither 0/14, ci 0/16, shadow 0/3, rc 0.
- CI: all completed lanes success; pr-contract red 09:16Z then success 09:19Z (latest); nightly-status is main's scheduled-run state, diff does not touch what it reads, answered in Red checks. fast (3.14) — the entities.py oracle — success. merge-tree clean; VERSION/manifest/notes untouched; claim files byte-identical to merge base (my detached-head env_drift red is the invocation shape, not the PR's).
- Body: prepr 0 errors; carry (Darwin inert_reads trap) in the hand-off RESUME; R9-RO-2b in the roster, wired into RO-3..RO-9 after lists, names what moved.
- Owned diff paths (mandate approval owed): .github/CODEOWNERS, tests/layout.json, tests/layout.py, .claude/workflows/budget_raise_gate.py, tests/delivery_status.py. The known set (closure.py, derive_closures.sh, mutation_table.py) untouched.

Note, not a block: R9-RO-2's own roster brief still carries pre-split text ("new-location-first", "restore steps list both globs") — orchestrator roster hygiene.
