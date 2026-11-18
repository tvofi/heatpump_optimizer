Fix review: merge 3990b0477a22fd19781298d4071538a87ed9f32f

bus-nonce: 0ae2cc014d5cce4f60cebf23daebe9e6
pending-ci: gate

## Evidence

Round 1, first review, full scope. Head 3990b0477a22fd19781298d4071538a87ed9f32f, base ae0ed64af898d8923ac35afe6e9c031ac1e6b111; the head on origin was still 3990b047 when this verdict was written.

- RESULT roles-current: `git diff $(merge-base)...origin/main -- dev/governance/roles/` is empty.
- RESULT merge-tree: `git merge-tree --write-tree origin/main 3990b047` exits 0 with tree 1ac094d3. No conflict.
- RESULT version: VERSION, the manifest version and RELEASE_NOTES.md are untouched (the three-dot diff over them is empty).
- RESULT null control: at the head, `plan_page.py --self-test` prints 154 checks, 0 failed. `plan_phases.py --check dev/programme/round11/phases.json` exits 0, and that file has no instrument-triage entry (ev/null-control.txt).
- RESULT mutant 1 (instrument-triage dropped from PHASES): 154 checks, 3 failed. This matches the body.
- RESULT mutant 2 (instrument-triage moved after closure): 154 checks, 2 failed. This matches the body.
- RESULT mutant 3, the reviewer's own (instrument-triage moved before stamps): 154 checks, 1 failed. The position check kills it (ev/mutant3.txt). The first run of this mutant read a stale .pyc and was redone with bytecode off; ev/mutants.txt keeps the discarded run.
- RESULT policy budgets: `node tools/policy/policy_lint.mjs` exits 0. With `--budgets`, proposal-triage.md is at 42/42 lines and 589/594 tokens, dev/audit/README.md is at 6058/6059 tokens, and the corpus is about 71490 against 71712. No budget is raised.
- RESULT consumers: the only file outside plan_phases.py that references its phase list is dev/audit/harnesses/r10_plan_page_mutants.py, and only by path. round11/phases.json lists no closure entry, so adding a phase does not break the order check.
- RESULT finder's harness: none is named. This is a policy and instrument change carrying an owner ruling. The in-tree r10_plan_page_mutants.py ran at the head with 57 mutants killed, then aborted with rc 2: its `phases-drawn` anchor occurs 0 times in tools/audit/seat/plan_page.py at the base as well as the head, and neither file is in this diff (ev/r10_plan_page_mutants.txt).
- RESULT class: one seam (the PHASES tuple); the body names no multi-seam class.
- RESULT owed reds: the set (`merge_train.py owed-reds`) is tests / coverage-ratchet, tests / fast (3.14), tests / mutation, tests / typing, validate / validate-hacs and the others it prints. The body answers the red at c257268e: the cheaper detector is `policy_lint.mjs --budgets`, named with its cost. classify reports red: none at this head.
- RESULT CI: `merge_train.py classify` printed WAIT (pending: gate, red: none) from 18:32 to 19:05 UTC (ev/classify.log), hence the pending-ci line.

## Notes

Note: policy-approval: the diff changes owner-coded policy (proposal-triage.md, dev/audit/README.md). It merges only on the owner's approving review at the head (decision 0009 step 6), as the body states.
Note: stale-body: the body's `## Head` section repeats the same sentence for three heads (3990b047, 21df11ae, 2df90159) plus a bare SHA. Only 3990b047 is the measured head. Carry: dismissed: paperwork on this PR's own body, fixed by the author's next body edit

## Findings

- Out of scope: dev/audit/harnesses/r10_plan_page_mutants.py aborts with rc 2 at main. Its phases-drawn anchor is absent from tools/audit/seat/plan_page.py at base ae0ed64a, so the harness's remaining mutants are not evaluated. This is inherited from main; this diff touches neither file. Carry: dismissed: pre-existing harness drift on main outside this PR's diff, reproducible at the base by the same command
