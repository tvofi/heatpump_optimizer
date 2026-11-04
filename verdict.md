Fix review: blocked 6e1e8023da5c8f9b8f6b972f20c60dccafbac7a6 body-stale: mutation proof and figures describe lagging() and 41 checks; the head has lag_bound() and 48

bus-nonce: 538ba788dbbaa2d055f600687d0ca765

Round 2. Round 1 never completed. Measured from a detached worktree at 6e1e8023da5c8f9b8f6b972f20c60dccafbac7a6 (base d1e7dbbbb; origin/main now d4e584ec6).

## Block

The code at this head is sound against the finder's harness: 0 of 9 mismatches here, 4 of 9 at origin/main. The block is on the PR body. The fixer repaired the code (bc806747b) but did not re-take the body, so the body's account does not match this head (fix-review.md steps 1, 7 and 8; fixer.md steps 2 to 8 re-execute after a repair):
- `## Mutation proof` mutates `lagging()`, and its Fix paragraph and "the reason text has one owner, `OWN_PENDING`" describe `lagging()` too. `lagging()` is not in tools/ci/gate.py at this head. The head has `lag_bound()`, with `OWN_PENDING` and `OWN_ABSENT`. None of the body's three mutants can be applied as written.
- `## Figures` quotes `gate self-test: 41 checks, 0 failed`. At this head it prints `48 checks, 0 failed` (ev/selftest_head.txt).
- Alternatives: the body rejects "a separate shorter retry bound" and says one shared bound is kept. The head adds that separate bound, `GATE_ABSENT_MAX_S = 2 * POLL_S`, for own-ABSENT reasons.
- The body says nothing about the prelude change (`prelude` + OWN_PENDING when it is listed unfinished; an unlisted prelude stays `FAIL prelude: None` with no wait). Root-cause constraint 3 asks for that disposition. The code's docstring and its null self-test cover it; the body does not.
- `## Head` still describes a6305aa2 on base d7582ed4 in its second paragraph.

To clear the block, re-take the mutation proof, the figures and the alternatives against lag_bound(), and state the prelude disposition in the body. The code needs no change for this verdict.

## Findings

- Surviving mutant: setting `GATE_ABSENT_MAX_S = GATE_WAIT_MAX_S` passes all 48 self-test checks and gives 0 of 9 mismatches on the finder's harness. The two self-test checks that claim "inside the shorter ABSENT bound" assert `<= GATE_ABSENT_MAX_S`, which moves with the constant. Pin it with a literal or with `GATE_ABSENT_MAX_S < GATE_WAIT_MAX_S` when the body is re-taken. Carry: R10-HOTFIX-GATE-STALE-JOBS
- Equivalent mutant, no action: the `if src is not me else f"...{OWN_ABSENT}"` and `...{OWN_PENDING}` conditionals in gate() produce identical text both ways, because `where` is "this run" when `src is me`. Forcing either branch survives the self-test and the finder's harness. The conditionals are redundant, not a defect. Carry: dismissed: equivalent mutant, behaviour identical

## Evidence

- Finder's harness: dev/audit/harnesses/r10_gate_stale_jobs/harness.py from origin/fix/r10-rca-gate-stale (sha in ev/harness_src.txt), run unchanged against `tools/ci` extracted from each tree. RESULT head 6e1e8023d: mismatches 0 of 9. RESULT origin/main d4e584ec6: mismatches 4 of 9 (the 41870314676, two prelude-stale and pr-contract-ABSENT shapes). ev/finder_harness.txt.
- Root-cause constraint 1: the 704 s prelude shape passes after waiting 720 s, and the 800 s shape fails at the bound. The measured 670 s lag fits inside GATE_WAIT_MAX_S 720. The self-test's timeout-fit check passes.
- Constraint 2: an exhausted bound is still FAIL (self-test "own jobs still pending past the bound stay red"; harness "past the bound: stale 800 s"). The hidden real red of 41870522291 reads FAIL `tests / mutation: failure` after the re-read.
- Constraint 3: covered in code (41863133083 and 41876634563 shapes PASS after the re-read; 41094975103 FAIL `prelude: failure`). The disposition is missing from the body (Block).
- Constraint 4: no ordering change in the diff.
- Self-test at the head: `gate self-test: 48 checks, 0 failed`.
- Mutants (ev/mutants.txt; self-test / finder mismatches): lag_bound returns 0 (8 failed / 4); all->any (1 / 0); prelude listed_unfinished False (2 / 2); unlisted prelude waits (1 / 0); deferral bound 0 (6 / 0); lagged note dropped (1 / 0); status dropped from read_api (2 / 2); ABSENT bound = WAIT bound (0 / 0, survivor, Findings); own-tag conditionals (0 / 0, equivalent). The tree was restored and the self-test is green again.
- `git merge-tree --write-tree origin/main 6e1e8023d`: rc 0, no conflict (ev/merge_tree.txt).
- Red checks: the only red in the packet digest is `tests / nightly-status`. The diff (tools/ci/gate.py, dev/programme/delivery/3205.md) does not reach what it reads, so it is not this PR's red (defect-root-cause.md). The body's `## Red checks: none` stands for gate checks.
- CI: `merge_train.py classify` at this head, 20:41:52Z: rc 0 `GREEN 6e1e8023da5c8f9b8f6b972f20c60dccafbac7a6 pending: none red: none` (ev/classify.txt). Head re-read before return: still 6e1e8023da5c8f9b8f6b972f20c60dccafbac7a6.
- Not re-derived: the body's run timestamps (17:35:07Z, 17:36:51Z, 17:37:43Z) come from API reads I did not repeat. The harness's lag figures stand in for them.
