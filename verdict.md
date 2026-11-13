Fix review: merge 428c7b8673127b136d5c34d3adfaa5f5f274a205

bus-nonce: d5e1eea90d530d1a95c6c1d3211621a6

## Scope

Round 4 of this topic (handoffs 82f3cf9759, 6a1966196c, ac5ca58c09, 428c7b8673): a main-conflict repair round. The review covers the delta from the previously reviewed handoff ac5ca58c09440120bcc9e2f25cdd4fdf430f630b, which is one merge commit (parents ac5ca58c09 and origin/main e23124ff6e), and checks its conflict resolution. I did not widen it to a full re-review: the resolution touches no `custom_components/` path (step 12). `review_carry.py` prints FRESH-REVIEW only because the head is not the automatic merge of its parents. I reviewed that hand resolution file by file below. This is a main-merge repair, not a revise cycle, so the round count does not mean a re-cut is owed here.

## Evidence

- Head reviewed: 428c7b8673127b136d5c34d3adfaa5f5f274a205 (ev/HEAD.txt). It matches the body's `## Head` and the body commit's `Code:` trailer (965c2b3006), and is still the tip of handoff/r10-selftest-scope-union-guard at ls-remote.
- Merge with main: `git merge-tree --write-tree origin/main 428c7b86` exits 0. origin/main is e23124ff6e, which is the head's second parent (ev/merge_tree_main.txt).
- Resolution vs the automatic merge: `git merge-tree` of the two parents conflicts on exactly three files: `.claude/workflows/audit-find.js`, `dev/audit/config/bugclasses.json` and `dev/audit/config/finding.schema.json`. The ledgermerge driver refused bugclasses.json because the branch side was not in its writer's own JSON format (ev/automerge_parents.txt). The head differs from the automatic-merge tree f9643f606c only in those three files (ev/resolution_vs_automerge.stat/.diff). The other files, including main's 296-file delta, are as git merged them.
- Both sides kept (ev/union_check.txt). Each set here is the base's set plus both sides' additions, less nothing, and equals the head's set exactly. bugclasses.json class ids: branch adds R10-SELFTEST-TABLE-SHRINK, main adds N-provisional-gate-red-read-final. finding.schema.json class_guess enum: the same two additions. No entry differs from both sides. In `_rca`, only R10-RCA-SELFTEST-SCOPE-DRIFT changed (from the branch), and every other `_`-key is equal across base, branch, main and head. The schema enum equals the non-metadata class ids plus `new`.
- The writer's format holds at the head: bugclasses.json equals `json.dumps(d, indent=2, ensure_ascii=False)` with no trailing newline, as main's file does. ac5ca58c's copy did not, which is what the driver refused. The resolution normalises it.
- Ledger consistency at the head: `fold_ledger.py check` prints `56 classes, 758 instances, ... 0 violation(s)`. `fold_ledger.py sync --dry-run` prints `audit-find.js already carries finding.schema.json`. `node tools/policy/check-wave-script.mjs` prints `226 passed, 0 failed` (ev/ledger_checks.txt).
- The fix's own checks, re-run at the head after the merge (ev/reruns.txt, ev/mutants.log):
  - `selftest_scope.py --self-test` prints `145 checks, 0 failed` rc 0 unset, and the same under `GITHUB_BASE_REF=main SELFTEST_BASE=nonesuch`.
  - `SELFTEST_BASE=origin/main ... static` prints `114 gated step(s), 0 problem(s)` rc 0.
  - `sh tools/ci/selftest_scope_mutants.sh` runs 31 mutants (`== ` lines) and ends `SELFTEST-SCOPE MUTANTS: every mutant refused`, rc 0.
  - Every figure the body quotes for these four commands re-derives at this head.
- Mutation proof and null control: unchanged by this delta, which touches neither `tools/ci/selftest_scope.py` nor its mutants script. I re-ran the mutants script at the head (above). I did not re-run the history null (`evidence/null.py` of af9e2248ef) or `mutant_run.py`'s 43-survivor figure this round. Both were reviewed at earlier heads and the code they measure is identical here (no diff to `tools/ci/selftest_scope*`), so those two figures are carried, not re-derived.
- Body contract: `node tools/policy/policy_lint.mjs --pr-body BODY.md --head 428c7b86 --paths-file <branch paths> --red instrument-self-tests` prints `PR-BODY: 0 error(s)` and `record red-history ... governance / instrument-self-tests` (ev/body_lint.txt).
- CI: no pull request exists yet, so there is no review packet, no check run on this head and no CI to wait on. The owed-reds set (`merge_train.py owed-reds`) is `tests / mutation`, `tests / typing` and `validate / validate-hacs` (ev/owed_reds.txt). No red on this head can be read before the PR opens. The range's earlier `governance / instrument-self-tests` red at ef7e3373e7 is answered in the body's first `## Red checks` section.
- VERSION, the manifest version and the RELEASE_NOTES heading are not touched by the delta's resolution: the three resolved files are its only non-main changes.
- Forward-carry: unchanged from the prior round (R10-NUDGE-RETIRE in dev/programme/rosters/wave-r10-groups.json). The delta does not move it.

## Findings

- The handoff body (965c2b3006, also d21d3fccd9 last round) holds a spliced duplicate tail. A heading reads ``## Forward-carry`.``, followed by a repeat of carries 1–4 and a second `## Red checks` section saying "none", which contradicts the first section's answer for the ef7e3373e7 instrument-self-tests red. `policy_lint.mjs`'s `sections()` keeps only the later of two same-named headings, yet the contract run still passes (ev/body_lint.txt). The defect is cosmetic, but a reader of the posted PR sees two opposite Red-checks answers. The orchestrator or fixer should delete the duplicated block, from ``## Forward-carry`.`` through the second `## Red checks` paragraph, before the PR opens. Carry: dismissed: body-only text defect, no code or gate effect; strip the duplicated tail at PR open

## Friction

none
