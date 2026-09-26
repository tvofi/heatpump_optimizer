_Requested by **tvofi**_

Readiness PR R3a of audit round 9 (the round-9 plan, section 3, row R3, first half), stacked on R1a (`handoff/r9-r1a-find-checker`, code head `c6ca4132`), which merges first. `wave-script` restores `.claude/workflows/check-wave-script.mjs` from the pull request's **base** before it grades (decision 0013), and the base's `the verification pass` block pins round 8's shape: one verifier per dimension, every finding to one `judge` call, driven with `pipeline` only. The round-9 driver (R3, `handoff/r9-r3-verify-driver`, stacked on this branch) is red against that whatever it does, so this pull request teaches the checker the round-9 shape first; R1a's route one file over.

- `the round-9 verification pass` runs only when `.claude/workflows/audit-verify.js` carries a `PANEL:BEGIN`/`PANEL:END` block. It evaluates that block alone (`panelOf`, `rcaOwed`, `shardsFor`, `seatOf`) and then drives the driver's body against stubbed agents: three lens verifiers per triple, a dimension over the shard size split into seat-pure triples, the killed finding kept from the judge, `judge/dedup` before `judge/runner-*` (`tools/audit/judge_batch.py`) before `judge`, one sweep per class with RCA at three instances, and issue drafts unless `args.file`. The rules it holds are `tools/audit/briefs/verifier.md` and `judge.md` as #1627 merged them, and `.claude/rules/defect-root-cause.md`'s audit-class exception.
- Round 8's `the verification pass` pins run only while that block is absent, unchanged.
- `the rotation yield` hands the driver `parallel` as well as `pipeline` (the round-9 driver runs its triples and runners through it; round 8's ignores it), and its comment no longer says the find driver's dispatch rule reads the yield or writes coverage through a dedup agent: `rotation.json` keeps the yield beside what `audit-find.js`'s intake records.

Code-owned: no path here is under a `CODEOWNERS` owner pattern (`check-wave-script.mjs` is not listed). Not policy. The delivery row `docs/delivery/<N>.md` is written by the Mac seat once the pull request number exists.

## Head

`9fd82c91`

## Mutation proof

Tests first: at this head the block is inert against `main`'s driver (no `PANEL:BEGIN`); against the R3 driver (`handoff/r9-r3-verify-driver`'s `audit-verify.js`, copied over this head's) it passes, and each one-line mutant of that driver's predicates exits 1 on `node .claude/workflows/check-wave-script.mjs`:
- `refutes >= 2` → `>= 1`: `two refutes with executed numbers kill; one, or one plus a refute without a number, sends it disputed; nothing else kills`, `the killed finding never reaches the judge; the disputed one does, marked`, `one sweep per surviving class, ...`, `a null verifier is re-run once, and a kill needs two refutes actually cast`.
- the no-number clause of `normalise` → `false`: `two refutes with executed numbers kill; ...`.
- `rcaOwed`'s `n >= 3` → `n >= 2`: `owes an RCA at three instances of a class or any instance of a barriered one, not at two or at none`.
- `shardsFor`'s size guard → always one shard: `sixteen findings over two seats make two triples, ...`, `three verifiers per triple, one per lens, and D2's sixteen findings get two triples (9 calls in all)`.
- `fileIssues = args?.file === true` → `true`: `the writer drafts one issue per class and the roster, and files nothing unless args.file`.
- the null-verifier retry removed: `a null verifier is re-run once, and a kill needs two refutes actually cast`.
- a killed finding still pushed to the judge: `the killed finding never reaches the judge; ...`, `one sweep per surviving class, ...`.

## Null control

`main`'s driver at this head: `node .claude/workflows/check-wave-script.mjs` exits 0 with round 8's pins passing and the round-9 block not run. Positive control for the key: `main`'s driver with an empty `// PANEL:BEGIN` / `// PANEL:END` pair appended exits 1, `the round-9 verification pass threw: seatOf is not defined` -- a driver claiming the new shape without its rules fails rather than passing both arms.

## Figures

- `node .claude/workflows/check-wave-script.mjs` at `9fd82c91`: rc 0, 0 failed on the instrument's own tally line (the deliberate `(probe, expected)` line is discounted by the checker).
- The same with `.claude/workflows/audit-verify.js` replaced by `handoff/r9-r3-verify-driver`'s: rc 0, 0 failed. With `.claude/workflows/audit-find.js` also replaced by `handoff/r9-r1-find-driver`'s: rc 0, 0 failed.
- `git merge-tree --write-tree a897272a 592f5d5b` (this change cut from `main`, against R1a) conflicted in `check-wave-script.mjs` at the insertion point both use; stacking on R1a is why the conflict is resolved here and not on merge.
- `python3 tools/audit/round6/D11/fix/codeowners_gap.py --check` at `9fd82c91`: rc 0, `RESULT uncovered_files=0`. The fixtures quote no production path (`in.json`, `t.md`, `r`).
- `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"`: `MODE: SCOPED -- 0 script(s) run`.
- `node .claude/workflows/policy_lint.mjs`: rc 0.
- `git merge-tree --write-tree origin/main 241a480f` (R3's head, which contains this one) at `origin/main` `cb78e997` (#1632 merged since R1a's base `81f2c18c`): rc 0, no conflict; none of #1632's five files is touched here.

## Red checks

none

## Forward-carry

none

## Friction

- decision-0013: cost: a checker restored from the base that drives the artifact it grades makes the artifact's shape change two pull requests; this is the first of R3's two, as R1a was of R1's.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
