Fix review: merge 5964b5836ca3fbaa041964e1c33943b8b852e964
bus-nonce: e99e5ded129789087091c423425c90a9

PR #2062, round 3. Measured at 5964b5836ca3fbaa041964e1c33943b8b852e964. I re-read the live head at posting and it was unchanged.

The delta from e6e5aea:
- 3eb8d53a: the fixture path fix.
- 5a042830: merges 3eb8d53a.
- 5964b583: merges origin/main b296779f, the v6.7.17 stamp.

`git diff --cc` at the head is empty, so no conflict resolution was done by hand. merge-tree against origin/main b296779f gives rc 0. Against the three-dot base, VERSION, the manifest version, the notes heading, both claim files and every budget file are untouched (0 lines). The claim-file change in e6e5aea..HEAD is main's own stamp, inherited.

## The round-2 blocker is cleared
- 3eb8d53a builds its own rows under dev/programme/delivery/: `rowadd` off `fork` adds the row, and `rowedit` off `rowadd` edits it. The cases are now `row_red rowadd fork` → 0 and `row_red rowedit rowadd` → 1. The semantics are preserved: the positive case is a diff that only adds its own row, and the null case edits a row the base had.
- RESULT layout (local, CI venv): `python3 tests/layout.py` rc=0, `layout: GUARD: 0 refusal(s) against b296779f0e96`.
- RESULT CI `fast (3.14)` 113396389610: success. RESULT CI `closures` 113396530637: success.

## prepr self-test and mutants, re-run at this head (my harness, evidence3/run_mutants.sh)
- RESULT head: 212 passed, 0 failed.
- RESULT M_fix_removed (`args+=(--existing-file "$ex")` deleted): 211/1. The failure is `pr-body exempts ... only ADDS its own delivery row (got 1, wanted 0)`.
- RESULT M_null_no_red (`delivery-status` dropped from row_red): 211/1. The null case gives `got 0, wanted 1`, so the control's rc 1 is the delivery-status refusal and is not vacuous.

## Body
- `## Red checks` names `fast (3.14)` red at e6e5aea7 (job 113385312852) as the PR's own red. It gives the cause (layout.py new-reference to the retired docs/delivery/) and the cheaper detector, `python3 tests/layout.py`: about 4 s on CI, standing cost those seconds per push, and not in prepr.sh or the scoped selection. It owns the miss. That answers defect-root-cause.md's second trigger.
- It names nightly-status and delivery-status as main's reporters, exempt.
- Its "closures was green at e6e5aea7" checks out: run 113385453475 concluded success.
- `## Head` names 5964b583 and describes its two merges correctly.
- `Closes #2028` is still on its own line.

## CI at the head (two polls; the second is the settled one)
- Every check is completed except `coverage`, which is not required (coordinator).
- The only red is `nightly-status` 113396389907. It is main's scheduled-run reporter, the diff touches no reporter input except its own new row, and pr-contract's exemption passed: both pr-contract runs, 113396126320 and 113396697695, are success.
- `Analyze (python)` was in progress at the first poll and had settled non-red by the second.

## Carried
Round 1 at 539d300b covered the token on the body-check step, the entities pin with mutants M0 and M1, the six planted variants, the #2053 and #2058 replays, the bus re-derivation and the cost test. Those files are unchanged since then, so those results carry. Round 2's checks on the --existing-file exemption (no widening beyond CI's rule) also carry, because prepr.sh's body_check is unchanged since a6984468.

The round-1 non-blocking notes still stand:
(a) The red-history walk adds GITHUB_TOKEN API calls per contract run and fails closed when a read fails.
(b) The RCA §6 item 3 owner proposal needs surfacing on #201 or in HANDOVER.
(c) The workflow file is code-owned, so it needs the orchestrator's or tvofi's approving review.

Evidence: /Users/timmalmstrom/hpo-seats/review-2062/evidence3
