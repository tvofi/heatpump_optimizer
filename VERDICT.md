Fix review: merge 7b45419f4f6f827026ac6ce7a950428a1f32b5ad

bus-nonce: 080693b0b7efb276e9c483edd09534d8

## Round

This is round 3, a delta review. Round 2 was `refs/heads/verdict/3090`, blocked at 3e6bf423086464ee6207f98adab18861e81871d4 as class-open on train_add's start path. I reviewed from detached worktrees at 7b45419f4f6f827026ac6ce7a950428a1f32b5ad (the live head), at 3e6bf423086464ee6207f98adab18861e81871d4 (the round-2 head) and at f68107fd0c59bdbc71eae71ccec48bb9d6b175bb (the fixer's handoff). I measured with the finder's harness, verdict/3090 `evidence/start_path.py`, `finder_front_vs_drain.py`, `shapes.py` and `mut2.py`. `git diff merge-base...origin/main -- dev/governance/roles/` is empty, because the merge base is origin/main ea59e9a09, so the contract is current.

## Findings

none

## Evidence

- Head. The live PR head is 7b45419f4f6f827026ac6ce7a950428a1f32b5ad, read through the API both before and after CI concluded (`ev/HEAD.txt`), and the body's `## Head` names it. Its first parent is 6b90c99d5, whose tree is identical to f68107fd's tree (3c50e11bc), and f68107fd fast-forwards 3e6bf423. Its second parent is origin/main ea59e9a09. `git merge-tree --write-tree 6b90c99d5 ea59e9a09` produces tree de6677210, which is the head's own tree, with the note `LEDGER-MERGE: resolved tests/closures.json`. So the main merge has no hand resolution. `review_carry.py f68107fd 7b45419f` prints CARRY.
- Block 1 of round 2 is settled. The finder's `start_path.py` gives (`ev/start_path.txt`):
  - Old head 3e6bf423, `priority`: `start_queue=[3, 1, 4]` against `drain_order_of_same=[4, 3, 1]`.
  - This head, `priority`: `start_queue=[4, 3, 1]` and `drain_order=[4, 3, 1]`, so the HOTFIX now runs first.
  - `front`: `[4, 3, 1]` at both ends.
  - Null control (plain add): `[3, 1, 4]` at both ends, equal to drain_order and unchanged.
- One ordering path. Of the production `spool_read(` callers (`ev/callsites.txt`), two build a batch, and both go through `Train.drain_order`:
  - The start path, `train_add`, at merge_train.py:1109, then 1143.
  - `queue_take`, at 3115, then 3120.

  The other callers do not build a batch. `queue_close` (3150) only names leftovers in `NOT RUN`, and `spool_order` (989) prints the read-back. There is no second copy of the sort key. The fixer chose one call to the existing helper over the list the start path already built. That fits fixer.md step 17, and I found no breach of it.
- New self-test arms at merge_train.py:6998–7025, as the three arms named in the body. Mutants planted by hand, single occurrence, each restored afterwards (`ev/mut3.py`, `ev/own_mutants.txt`); `git status` was clean after the run:
  - Unmutated head: `merge_train self-test: 438 checks, 0 failed`, all three start-path arms ok.
  - S1, the start path reverted to the round-2 `[entry] + spooled if front else spooled + [entry]`: KILLED with 438 checks and 2 failed (the P312 start-path arm and the P112 start-path arm). The null arm stays ok under it, so the null control is not vacuous.
  - S2, the start path ignores front (`drain_order(spooled + [entry])`): KILLED with 1 failed (the P112 arm).
  - S3, drain_order on the spool only, with the entry appended: KILLED with 1 failed (the P312 arm).
  - Round-2 mutants R1–R6, B1 and F1–F3 (the finder's `mut2.py`): all KILLED. The failure counts are R1 1, R2 1, R3 2, R4 2, B1 7, R5 5, R6 1, F1 3, F2 2 and F3 2. No mutant survived.
- Self-test count. The body's 421 is the figure at the code head f68107fd, and I re-derived it there (`ev/selftest_f68107fd.txt`: `merge_train self-test: 421 checks, 0 failed`). At the live head the count is 438, because main's merge brings in 225 inserted lines of merge_train.py. The body's mutant failure counts are at 421 checks and mine are at 438. The killed or survived outcome agrees for every mutant.
- Further ordering shapes. On the live train (the finder's `shapes.py`, `ev/shapes_fvd.txt`), every shape has read-back equal to drain, and the results are identical at both ends. The shapes were two fronted, front plus priority, front then remove, new front then front another, and null. The one entry that reorders, `front 1 then add #5 --priority` with drain `[1, 5, 3, 2]`, is P312's stated HOTFIX tiering and prints no read-back.

  On the start path I used my own harness, `ev/start_shapes.py` (disclosed as the reviewer's), with output in `ev/start_shapes.txt`. In every case the start queue equals drain_order of the same entries:
  - several leftovers, a plain add: `[3, 6, 1, 2, 4]`
  - several leftovers, a priority add: `[4, 3, 6, 1, 2]`
  - a leftover HOTFIX plus a priority add: `[5, 4, 3, 1]`
  - a leftover fronted entry plus a priority add: `[1, 4, 3, 2]`
  - `--front --priority` over a leftover HOTFIX: `[4, 5, 3, 1]`
  - `--front` over a leftover fronted entry: `[4, 1, 3]`
  - an empty spool with `--priority`: `[4]`

  With no live train, `--front` of an already-spooled entry only reorders the spool to `[2, 1, 3]` and starts nothing. That is the documented `spool_edit` arm, and it is unchanged from round 2. A later add drains that order. I found no shape where read-back, drain and start queue differ.
- Merge with main. `git merge-tree --write-tree origin/main 7b45419f` returns rc 0 and tree de6677210, the same as the head's tree, because the merge base is origin/main (`ev/checks.txt`).
- Claim files. The three-dot diff and the two-dot diff against origin/main are both empty for `tests/golden/claimed_drift.txt` and `card_claimed_drift.txt`, so they are byte-identical to main. `env_drift.py --claims-only` prints `claims hygiene: origin/main ok`. VERSION, the manifest and RELEASE_NOTES.md are untouched, and no `*_budgets.json` file is touched.
- `python3 tests/structure.py`: STRUCTURE RATCHET PASSED, and there is no budget raise. `policy_lint.mjs --budgets` returns rc 0 (`ev/gate_scope.txt`).
- Scoped gate: `MODE: SCOPED -- 2 script(s) run, 31 scoped out.` (`ev/gate_scope.txt`).
- Delivery row. `dev/programme/delivery/3090.md` is in the three-dot diff.
- Body. The body names the start-path seam and the enumeration rule (`grep -n "spool_read("`, production lines), and the rule's output matches the diff. `## Head`, `## Mutation proof`, `## Null control`, `## Red checks` and `## Approval` are all present. The Approval section says owner approval is owed for standing-merge.md and nudge.md: the PR merges only on tvofi's approving review at its head, or under a mandate in force scoped `all`. `## Forward-carry` is none, because the class closes in this diff.
- CI and red checks. `merge_train.py classify 7b45419f --pr 3090` printed `GREEN 7b45419f4f6f827026ac6ce7a950428a1f32b5ad pending: none red: none` with rc 0 at 17:09:26Z (`ev/classify.txt`). The commit's check-runs API lists 55 runs on one page of 100, and every one concluded success, skipped or neutral (`ev/check_runs.txt`). That includes `pr-contract / pr-contract`, which concluded success. With no red check, step 11 owes nothing. I did not re-run the heavy gate or the mutation table, and I cite CI's results for both.
