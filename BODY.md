Triage batch 111 records one ruling, P369, from the orchestrator s10's queue line of 2026-11-02T02:55:35Z. The proposal: a nightly `hpo-ledger[bot]` commit (`8247a1ed`, "ci: record nightly kills") moved main while train batch 3's proof was green at `5334150c`, and four pull requests were re-proven. Either the train should accept a record-only main move without a recarry, or bot record pushes should wait while a proof is in flight. It is the rolling batch after batch 110.

- **P369: DEFER, written as LOG under the owner's 2026-11-01 ~19:50Z rule.** No carry and no group.
  - **No production merge is held.** #3147 is the one batch-3 entry under `custom_components/` (2 files). It was delayed by one automatic re-proof, about 1 h, through `merge_train.py`'s `--main-moved-tries` recovery, and was not stopped.
  - **No rate is measured.** The seat ledger names 2 instances (2026-11-01 at `df66556f`, and this one) among 28 `hpo-ledger[bot]` commits on main in round 10. Neither gives a figure above 10%.
  - **Remedy (a) is unsound for these files.** `tests/mutation_table.py`'s `dispositions()` reads every `killed_by` record into the ratchet and the completeness check, so ledger paths are not inert. Re-proving on the new main is what catches a batch entry editing a site the night just pinned.
  - **Remedy (b) extends an existing guard.** `nightly.yml`'s record beat already waits on `refs/heads/train-hold`; `mutation-ledger-push` does not. The hold's stated scope is the record beat (#2302), so this is a design gap, not a defect. Dropping a held night's slice has its own cost to ledger convergence.
  - **What re-opens it.** A count of train re-proofs and skips caused by ledger commits, over all batches in a stated window, at more than 10% of train CI time or of completion time. Or a ledger push that exhausts the main-moved bound on a train holding a `custom_components/` pull request.

No product behaviour changes: the diff is one markdown file under `dev/programme/triage/`. No roster op is queued.

## Head

`52a8841381b0f02c33c6c4f2d01a9cdc403e1b21`; the file is the whole diff against `8247a1ed1`.

## Mutation proof

This file's only consumer is the triage gate in `tools/audit/seat/roster_edit.py`, through `ruling_verdict` and `triage_refusal`.
- On the committed file, `ruling_verdict` reads P369 as `DEFER`, and a text citing `s6-batch111.md#P369` is refused: `is not an ACCEPT ruling (DEFER)`.
- With the verdict flipped to ACCEPT, it reads `ACCEPT` and the refusal is `None`.
- P370 reads `None`: no such entry.

## Null control

- With the file absent, the citing text is refused: `the triage ruling dev/programme/triage/s6-batch111.md is not on the roster branch or origin/main`.

## Figures

- `git show --stat 8247a1ed`: author `hpo-ledger[bot]`, every file under `tests/mutation_ledger/killed_by/`.
- `gh pr view 3147 --json files`: 2 files under `custom_components/`; #3149, #3077 and #3153: none.
- `git log origin/main --first-parent --author=hpo-ledger --since=2026-10-12 --format=%h | wc -l`: 28.
- No capped file is touched; the diff is one markdown file.

## Red checks

`none`. A ref with no pull request has no checks.

## Forward-carry

none

## Friction

none
