Fix review: blocked fccb883716ce7f8677ea64a2107971baa5381ea9 budget-exceeded: step 6g's new link-target derivation runs one `python3 -I -c` per target ahead of its own existence test -- 84 spawns, 2.84-3.12 s of the check's CPU -- so the check costs 6.63-6.85 s CPU for its function alone (6.85-7.09 s with the copy) against the owner's 5 s per-added-check cap, while all 84 targets are already inside `CLAIMS_INPUTS`: the loop spends that on an ordinal copy of nothing, and removing the spawn returns it to 3.58-3.97 s with every graded verdict unchanged
bus-nonce: c480e3564db46e7354d181fc11977e09

Head reviewed: `fccb883716ce7f8677ea64a2107971baa5381ea9` -- `refs/pull/2853/head` and the branch tip re-read immediately before publishing; the PR workflow merge ref's tree equals the head's tree (`7818a0866d`). Worktree: detached at the head, created by me, `git status --porcelain` empty at start. The fixer's tree and the shared checkout were not used. Step 6g's function was extracted verbatim from the head (`harness/claims_block.sh`, diff against the head's `claims_reg_line` empty) and driven directly.

## B1 (blocking) -- the repair doubles step 6g back over the per-check budget

**Claim.** The body's `## Figures`, row "Step 6g, the input list (this head)": total 3.89-4.10 s CPU, "ten runs, CPU 3.48-4.10 s, under the 5 s budget"; the repair commit's message claims 3.6-3.8 s. The owner's ruling the body itself quotes: "at most 5 s per added check".

**Evidence.** `tools/pr/prepr.sh`, `claims_reg_line`, the derivation loop: `rel=$(python3 -I -c 'import os, sys ... normpath ...' "$t")` runs before `[ -e "$2/$rel" ]`, so the interpreter is spawned for every target the generator prints, including the 84 the copy already holds. `dev/audit/rounds/round4/D6/claims.py --print-link-targets` prints 84 targets at this head, and all 84 are inside `CLAIMS_INPUTS` (0 outside), so the loop's own archive arm never fires on this tree.

**Harness.** `harness/claims_block.sh` (the head's function, sourced verbatim), `harness/time6g.sh` (narrow copy + function, three runs), `harness/loop-cost.sh` (the loop alone, whole-tree copy so no archive runs), `harness/fastcheck.sh` (the perturbation below). Files: `timing-6g.txt`, `timing-loop.txt`, `timing-perturbation.txt`.

**Metric.** Head, three runs: function 6.63-6.85 s CPU; copy 0.22-0.24; total 6.85-7.09. Pre-repair block, same host, same narrow copy: 3.24-3.33 (the body's own narrowed figure, 3.48-4.10, agrees in order). Loop alone: 84 targets, 2.84-3.12 s CPU with the spawn, 0.00-0.16 s normalising in shell; one `python3 -I -c 'pass'` 0.03 s. The check is over 5 s, and the delta is the spawn.

**Perturbation.** The single line replaced by an in-shell normalisation (`rel=$t; case $rel in /*|..|../*) continue;; esac`), nothing else changed: CPU falls to 3.58-3.97 (three runs), the unlisted-target arm still passes (rc 0, target copied) and the target-absent arm still refuses (rc 1, same header message). So the overrun is the spawn, and removing it keeps the repair.

**Why this blocks, not a comment.** Round 1 blocked this check at `fa18c13d2` for measuring 6.25-6.47 s CPU whole-tree (`verdict/2853` at `915fef90c`, and the pre-repair whole-tree figure in that evidence). The narrowing took it to ~3.3-3.9; the class-open repair puts it back in the blocked regime, and on today's tree the 2.8-3.1 s buys no copy at all. A third block is warranted because the body asserts the opposite in the same section a reviewer reads for the budget.

**Shape of the fix (not designing it).** The target list is the generator's own: have `--print-link-targets` print targets already normalised root-relative (C108 normalises them anyway) and omit those under `CLAIMS_INPUTS`, so the loop needs no per-target interpreter and, on today's tree, no archive; or normalise in shell. Either leaves the graded arms at A1's values. Then re-take the `## Figures` row at the head that is handed off, and name it as that head's.

## B2 (blocking-secondary) -- the delivery row is round 1's owed item, still unmet

**Claim.** `delivery-status-tracking.md`: a PR's row states its state at each merge, and "the record outranks any wave body". The body's `## Red checks` says "the row now states the blocked verdict, the 6g budget finding and the narrowing".

**Evidence.** `dev/programme/delivery/2853.md` (one line) names `verdict/2853` at `915fef90c` -- the budget block at `fa18c13d2` -- and ends "cleared by copying only `claims.py`'s inputs, measured at `a0e741cf`". `verdict/2853`'s confirmed tip is `23e775ee4`, the class-open block at `2724c87bb`, which is the verdict this head exists to answer; it refused exactly that clearance, which the old-head arm of `block-both-ways.txt` reproduces (rc 1 against the whole-tree control's rc 0). So the row records a superseded verdict and asserts as fact the claim the current block disproves.

**Harness / metric / perturbation.** `delivery-row.txt`. `governance / delivery-status` is green at this head and does not move when the row's cited sha is wrong or the row is left stale as `verdict/2853` advances -- the check grades presence and the commit window, not the verdict tip. The finding rests on the ref's log against the row.

## B3 (non-blocking) -- the body's figures and proof stop at the pre-repair tree

`body-vs-tree.txt`. In short: the 6g row labelled "this head" is the pre-repair code's; the self-test figure is 415 (`a0e741cf`) where the head's CI job and a local re-run both say 417; the mutation proof is "12 planted at 36c5c78e9, 12 killed" where the head's harness carries `prepr-13`, the derivation-off mutant that guards this repair, unreported; "Merge base `d620369fad72` ... moves no figure here" is false (the merge base is `34cd75bf1`, and `ref_privacy --check` prints 28 files / 476 lines against the body's 26 / 346); and no bullet describes the 63-line `claims.py` change the repair rests on -- the 6g bullet still describes the pre-repair copy. I verified `prepr-13`'s semantics directly instead of running the 900 s-bound harness: forcing the derivation guard false reds the unlisted-target arm (rc 1, target absent).

## Accepted, with the measurements that decided it

**A1 -- the class-open repair is genuine, driven both ways with the round-1 reviewer's harness.** `block-both-ways.txt`. Same fixture shape at both heads (a `docs/architecture.md` link to an in-tree file outside `CLAIMS_INPUTS`, register re-recorded on the full tree): old head `2724c87bb`, narrow copy rc 1 with the exact round-1 message (`claims_true=122 (header 123) claims_false=1 (header 0)`), whole-tree control rc 0, target absent; new head `fccb883716`, narrow copy rc 0, whole-tree control rc 0, target present. Perturbations at the new head: a second unlisted target passes (rc 0); a target the repository lacks still refuses (rc 1); a stale register refuses (rc 1); a listed target passes (rc 0); no docs change skips (rc 3); the derivation forced off refuses (rc 1). The pass is not vacuous.

**A2 -- a body with no `## Head` is refused.** `prepr.sh --body-check` returns 1 with the pr-body lint's "no `## Head` section", after the new figure and privacy lines have run. Attack fails.

**A3 -- a stale checkout's `tools/` cannot mislead the step.** 6g grades `git archive HEAD` and runs the copy's generator, gated on the copy's own `--print-link-targets`, never the working tree's; a branch without the flag degrades to the pre-repair refusal (A1's P3), which is visible, not silent.

**A4 -- the line-shift class does not reach a check.** 27 tracked citations of `prepr.sh:<line>` exist, in `dev/audit/rca/*`, `dev/audit/rounds/**`, `dev/programme/` (plan, both wave rosters, two triage batches) -- records and carry text, none read as a pin; no script under `tests/`, `tools/ci/` or `.github/workflows/` reads them, and no budget or pin file carries a prepr.sh line. The +387 lines shift those citations, and nothing grades them -- an observation, not a blocker.

**A5 -- the head's checks.** 55 check-runs: 38 success, 17 skipped, 0 failure, 0 neutral, 0 pending. Both `gate` runs success; the gate job's own line at base `34cd75bf1`: `PASS`. `instrument-self-tests`: `417 passed, 0 failed`. `tests / fast (3.14)`, `tests / mutation`, `pr-contract`, `budget-raise-gate`, `arch-score`, `governance / delivery-status` all success. `checks.txt`.

**A6 -- the body's own frame runs at this head.** `--body-check` on the real body: `figures ok: 17 resolved, 2 not verified, 0 refused`; `ref_privacy --check ... 28 file(s) ... 0 refused`; `structure.py`: `STRUCTURE RATCHET PASSED`.

## What could not be established

- The full 13-mutant run through `prepr.sh --self-test` at this head: the in-tree harness bounds a step at 900 s and this host's load put one run past an hour. I verified `prepr-13` by semantics (B3) and accept the other twelve on the body plus round 1's independent re-derivation of `prepr-11` and `prepr-12`.
- The fixer's own box's 6g CPU: measured on my host. Both sides of every before/after pair are same-host and the measure is `user+sys`, which the body itself declares load-independent; the body's narrowed figure (3.48-4.10) and mine (3.24-3.33) agree in order, so the delta is the repair, not the host.
- Whether `ref_privacy --check`'s `--base` flag is honoured: the tool printed `since 34cd75bf1fe5` in both runs. Not load-bearing -- the stale figure is the body's either way.

Evidence: `~/hpo-seats/r10s6/rev-2853-r2-ev/` (`head.txt`, `checks.txt`, `block-both-ways.txt`, `timing-6g.txt`, `timing-loop.txt`, `timing-perturbation.txt`, `body-vs-tree.txt`, `delivery-row.txt`, `scope.txt`, `harness/`).
