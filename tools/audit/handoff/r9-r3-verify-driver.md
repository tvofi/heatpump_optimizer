_Requested by **tvofi**_

Readiness PR R3 of audit round 9 (the round-9 plan, section 3, row R3): the verify driver and the judge's batch re-runner. Stacked on R3a (`handoff/r9-r3a-verify-checker`, code head `9fd82c91`), which is stacked on R1a (merged as #1633); merge order R3a, then this. `wave-script` grades this pull request with R3a's checker once R3a is its base (decision 0013).

`.claude/workflows/audit-verify.js` now runs round 9's shape, as `tools/audit/briefs/verifier.md` and `judge.md` stand after #1627:
- **Panels.** Three verifiers per dimension, each owning one lens (V1 reproduce, V2 independent, V3 reach and class: real Home Assistant, severity, whether the `seam_rule` enumerates the phenomenon's seams, `class_guess` confirmed or corrected), pipelined per dimension. Two `refute` votes, each carrying an executed number, kill at panel; one sends the finding to the judge `disputed`; a refute with no number counts as `unresolved`, as verifier.md step 5 treats a timing-only refute. A dimension over 15 findings (`args.shard_size`) gets another triple, split at a finder-seat boundary (the finding's `scope`, else its id's `D<k>-s<n>`). A null verifier is re-run once; its missing votes can kill nothing.
- **Judge.** `judge/dedup` first, across all dimensions: merge only with the number showing the canonical finding's perturbation moves the other's harness; it writes `JUDGE-INPUT.json` for the re-runner, adding a `judge_batch` override where a header carries no `JUDGE-*` line. Then `judge/runner-<k>` agents run `tools/audit/judge_batch.py` (`--shard k/n` when `args.runners` > 1): they measure and never decide. Then `judge` reads every row, re-runs by hand what is disputed, void, by-hand, out of tolerance or flagged for a re-take, and returns a verdict and a class per canonical finding; merged findings are recorded `merged`.
- **Class sweep.** One seat per class with a survivor (D14.md method steps 3-4); N = judged findings + confirmed sweep instances; RCA owed at N >= 3 or any instance of a barriered class (defect-root-cause.md's audit-class exception).
- **Issues.** The writer drafts one issue per class (`ISSUES.json`) and the draft `.claude/workflows/wave-r9-groups.json`, runs `brief_lint.mjs` and reads its exit code, and files with `gh` only under `args.file` (the Mac seat as tvofi, decision 0011).

`tools/audit/judge_batch.py` is new: per finding it reads the harness header through `tests/harness_headers.py`'s `header_lines` (`JUDGE-RUN`, `-PERTURB`, `-NULL`, `-METRIC`, `-TOLERANCE` lines; `evidence.command` and `evidence.tolerance` as fallbacks) and the expected value through `expected_from`, runs command, perturbation and null control serially from the repository root, each with `tests/gate_lock.py`'s lease renewed (a refused renew releases and queues again, `gate-scoping.md`), and writes one row per finding: `reproduced`, `perturbation` moved / not-moved / wrong-direction / by-hand, `void` (judge.md step 2), `null_value`, and the harness's own `load1` and `thread_factor` (flagged when missing or over 1.05); a `judge_batch` override that is not an object is ignored and flagged on its row rather than aborting the batch. Two properties hold between commands:
- **The tree is put back.** Each command runs against a snapshot (`git status --porcelain`, untracked included, plus the bytes of every already-dirty path); a command that leaves the tree different -- a perturbation editing production on disk, or a harness killed at the timeout before its own restore ran -- is flagged `tree edited by <arm>` and the tree is restored before the next command, so one finding's perturbation cannot move the next finding's number. A path's state is its porcelain index/worktree code plus its bytes, with an unlisted path distinct from an empty one, so a new empty file is a change; a path clean before goes back to HEAD in index and worktree, so a staged edit is not restored from its own index; and the row reads `restore FAILED: <paths>` whenever a re-snapshot after the restore still differs. Off git, every row is flagged `tree unchecked`.
- **The batch holds the lease, not flock.** The child sees `HPO_GATE_LOCK_LABEL`, so a harness going through `tests/run.sh` onto `stress.py`, or through `gate_lock.py flock-wrap`, renews that label and takes flock itself (`run.sh`'s route for a seat's own label). The lease records the batch's pid and outlasts one command's timeout.

`tests/harness_headers.py`: the header's extent is one function, `header_lines`, shared by `expected_from` and the re-runner rather than parsed a second way; its discovery moved from import time into `main()`, so an importer's measured closure is not the whole round-harness corpus. `tests/closure.py` moves `tools/audit/judge_batch.py` out of the `tools/audit/` INERT prefix (`INERT_EXCEPT`), and `tests/entities.py`'s closure is re-recorded to list it and `tests/harness_headers.py`.

Code-owned: `.claude/workflows/audit-verify.js` and `tests/closure.py` are under `@tvofi` in `.github/CODEOWNERS`. Not policy (no file under the `CLAUDE.md` policy list). The delivery row `docs/delivery/<N>.md` is written by the Mac seat once the pull request number exists.

## Head

`bda239b8`

## Mutation proof

Tests first: at `origin/main` with the `tests/entities.py` block alone, `PYTHONPATH=tests/hastub python3 tests/entities.py` failed the four `judge_batch:` checks (the module did not exist) and the three driver checks later moved to R3a's checker.

At this head, each mutant of `tools/audit/judge_batch.py` below fails `PYTHONPATH=tests/hastub python3 tests/entities.py`'s `Round 9: the judge's batch re-runner` section on the checks named:
- `moved()`: equal values return `moved` → `judge_batch: the null control -- a harness whose perturbation does not move is void (judge.md step 2), and one that moves the wrong way is void too`.
- `within()`: `exact` always `yes` → `judge_batch: no perturbation command is left to the judge by hand, never passed; a number outside the header's tolerance is not reproduced`.
- `Lease.__exit__` releases nothing → `judge_batch: every row carries the harness's load1 and thread_factor, one table row per finding, and the lease is released after the batch`.
- no `take` and no `renew` (commands run unleased) → `judge_batch: a harness whose perturbation moves in the stated direction is reproduced and not void, measured under the gate lease`, `judge_batch: every row carries ...`, `judge_batch: a harness that takes flock itself under the batch's label (gate_lock.py flock-wrap, run.sh's route onto stress.py) runs, and does not wait out the timeout`.
- no restore after a command → `judge_batch: a perturbation that edits a tracked file is flagged on its row and put back, so the next finding reads the tree it would read alone, and the tree is clean after the batch`.
- the tree restored but not flagged → the same check.
- an absent path compared as an empty file, or state compared on bytes alone → the check above and `judge_batch: an edit the command STAGED is restored from HEAD, not from the index it staged, and a new EMPTY file (and its new directory) is noticed and removed; the row says restored only when the re-snapshot agrees`.
- a clean-before path checked out from the index instead of HEAD → the same two checks (the staged row reads `restore FAILED: pkg/staged.txt`).
- the re-snapshot after restoring dropped, or the new empty directory left behind → `judge_batch: an edit the command STAGED is restored from HEAD, ...`.
- `to_zero` read as `p < b` → `judge_batch: to_zero means reaching zero -- 3 -> 1 moves the wrong way and is void; a thread_factor over 1.05 is flagged for a re-take, 1.00 is not`; `THREAD_FACTOR_MAX` 1.05 → 0.5 → the same check.
- the absolute bound ignored, or a relative bound read as absolute → `judge_batch: absolute and relative tolerances hold inside the bound and fail outside it (±0.5: 10.4 yes, 10.6 no; ±5 %: 209 yes, 211 no)`.
- `_shard` dropping the first item → `judge_batch: --shard k/n for n = 2 and 3 splits the input into disjoint shards whose union is the input`.
- the non-object `judge_batch` guard removed → the batch raises and every check in the section fails, `judge_batch: a judge_batch override that is not an object is ignored and flagged on its own row, and the batch goes on` among them.
- flock held around the child (the previous route) → `judge_batch: a harness that takes flock itself under the batch's label ...` (the fixture waits out its 30 s timeout) and `judge_batch: every row carries ...`.

The driver's mutants (kill threshold, the no-number rule, `rcaOwed`, sharding, `args.file`, the null-verifier retry, a killed finding reaching the judge) are in R3a's body: its checker grades this driver.

## Null control

The fixture set is its own control. `reads` counts a tracked file and reads 3 on a clean tree; batched after `edits`, whose perturbation writes 9 into that file and never restores it, it must still read 3 with no tree flag. `flat` (perturbation prints the unperturbed number) must come back `not-moved` and void, and `handonly` (no `JUDGE-PERTURB`) `by-hand` with `void` null, beside `moves`, which must come back `moved`, not void, reproduced, with the null arm's value read. `tests/harness_headers.py` unmodified against this head's: the same 91 check lines, compared by `diff <(grep -o "^  [a-zA-Z]* .*" base.log) <(grep -o "^  [a-zA-Z]* .*" head.log) && echo SAME_CHECK_LINES`, which printed `SAME_CHECK_LINES`.

## Figures

- `PYTHONPATH=tests/hastub python3 tests/entities.py` at `bda239b8`: rc 0, `ALL ... ENTITY CHECKS PASSED` (the instrument's own tally line).
- `PYTHONPATH=tests/hastub:custom_components:tests python3 tests/harness_headers.py` at `bda239b8` and at `9fd82c91`: rc 0 both, `ALL ... HARNESS HEADER CHECKS PASSED`, identical check lines (Null control).
- `node .claude/workflows/check-wave-script.mjs` at `bda239b8`: rc 0, 0 failed on its tally line.
- `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"`: `MODE: FULL`, reason `tests/closure.py changes the gate itself`. Run locally instead of the forty-minute full suite: `tests/entities.py` (above), `tests/harness_headers.py` (above), `python3 tests/structure.py` (rc 0, `STRUCTURE RATCHET PASSED`), `python3 tests/closure.py selftest` (rc 0), `python3 tests/closure.py no-copies` (rc 0).
- Classification: `PYTHONPATH=tests python3 -c "import closure as c; print(c.is_inert('tools/audit/judge_batch.py'), c.orphan_files())"` printed `False []`.
- `tests/closures.json`: `./tests/derive_closures.sh --single tests/entities.py` on Linux, in two steps because `every tracked file is either measured or deliberately classified` fails until the table lists `tools/audit/judge_batch.py` (`gate-scoping.md`'s `--single` trap): `--record-only`, then `python3 tests/closure.py merge --in-dir D --partial --allow-failures` (that one check the only failure), then `--single` again, which merged with the recording at rc 0. The recorded closure gains `tests/harness_headers.py` and `tools/audit/judge_batch.py` and nothing else; re-recorded at `bda239b8`, it moved only its `seconds` field, which is not committed.
- `python3 tools/audit/round6/D11/fix/codeowners_gap.py --check` at `bda239b8`: rc 0, `RESULT uncovered_files=0`.
- `node .claude/workflows/policy_lint.mjs`: rc 0.
- `git merge-tree --write-tree origin/main bda239b8` at `origin/main` `c9453921` (R1a merged as #1633): rc 0.

## Red checks

none

## Forward-carry

none

## Friction

- decision-0013: cost: the verify driver's shape change needed its checker landed first (R3a); this is the second of the two.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
