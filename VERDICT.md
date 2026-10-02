Fix review: merge f70cd730c60e1c6b9d505a26d27f0f2e0d14e31f

bus-nonce: ea34f104127ab34186af06d5a9a4f247

Round 2 re-verdict on a body-only edit. The head is unchanged at f70cd730c, and I re-read it when posting. Every measurement in my round-2 verdict (review/1857 111bf3875) was taken at this head and still holds: ALL 2074 entity checks pass, 0 of 11 mutants survive, the real-artifact replay gives 3/3 defects red, 2/2 nulls quiet and 5/5 no-check.txt quiet, policy_lint 0 errors at 1428/1428 tokens with no raise, and merge-tree is clean. The evidence is in evidence-f70cd730c60e1c6b9d505a26d27f0f2e0d14e31f/: cr3.tsv, and body-at-reverdict.md, the body as I read it.

## The round-2 blocker is cleared

- **The body answers it.** `## Red checks` now names `nightly-status`. It gives the cause (NIGHTLY ABSENT for mutation-ledger and mutation-ledger-push, main's), says there is no cheaper detector, and names the owner (the orchestrator, on main).
- **The body's claim is true.** I checked it:
  - Both jobs entered main with e968130b9, which reached main in #1848 (8fa06663c, 16:51Z).
  - The last scheduled Tests run, 36984959667 at 08:36Z on 492d84011, does not contain e968130b9.
  - The same red is on every open PR head: #1862, #1861, #1858, #1856 and #1852.
- **pr-contract** re-ran green (110996486441). The earlier failure (110993238084) and the cancelled run belong to the pre-edit body.

## Check runs at the head (35)

- The only non-green conclusions are:
  - `nightly-status`: failure, answered as above. It grades main.
  - The superseded `pr-contract` failure and cancellation.
  - `budget-raise-gate`: cancelled, superseded; its later run is green.
- `fast (3.14)`, `closures` and `mutation` are green. `closures-autofix` was skipped because closures passed.
- Bootstrap: as the body says, the new status cannot fire here.

## Non-blocking notes for the record

- **The figures still say 2065.** The coordinator's message says "the figures say 2074", but the body's Mutation-proof and Null-control figures still read 2065. They are labelled as taken at 640ef43fa, which is honest for that commit. At the head the count is 2074, all passing, and I measured that myself.
- **The merge base is stale.** `## Head` still gives 5f87e25a1 as the merge base for the code head 640ef43fa. The merge base of f70cd730c is aa7a81192.
- **One gap is left uncovered.** A base `check` that returns 0 while the PR's check printed UNDER-SCOPED stays a quiet `skip-clean`. It needs a PR that changes the comparison logic itself, and the body treats `skip-clean` as out of scope.
- **Approval is still owed.** The PR edits `.claude/rules/ci-autofix.md`, so tvofi's approving review at the head is required before merging. The body's `## Approval` says so.
