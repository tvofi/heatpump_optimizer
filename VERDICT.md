Fix review: blocked 5009fe47254c6a3f2812b8a0e7eaa5b5df015573 null-control: equiv_probe.py's controls never differ at a tie (0 of 17 away, 0 of 11 optimizer), so the probe cited by both equivalent triage rows has no control on the arm it claims; the equivalence itself holds under the reviewer's tie-only controls

bus-nonce: 2ef701b4d19758b332ec3087c23978c8

Review round 2, PR #1861 (R9-F10.6), fix-review.md. Measured head 5009fe47254c6a3f2812b8a0e7eaa5b5df015573, which is the PR head when posting and is the head the body's `## Head` names. origin/main is 51ce8f2a. My briefs copy is current (the three-dot diff of tools/audit/briefs/ is empty).

Resolution delta: the head tree equals `git merge-tree` of the authored commit 307ecf6c with origin/main 51ce8f2a, plus this PR's own `docs/delivery/1861.md` row. So there is no hand resolution. The authored delta is 307ecf6c only.

## The one thing that blocks

The body (line 22) and both new `survivor_triage` rows rest on `tools/audit/round9/F10/f10_6/equiv_probe.py`. The body says "a differing control on the same line shows the probe can see a difference", and each row quotes its control's count ("differs on 18" and "differs on 11").

Both controls differ only where the mutant cannot differ, which is off the tie:
- away: the GUARD_OFF control changes `last` only when `last < first`. At `last == first` it returns the same tuple as the head.
- optimizer: `idx = last` changes only iterations with `i < last`. At `i == last` it reads the same `wt[last]`.

My instrument `rv_probe_ctl_at_tie.py` measures where the probe's own controls differ:
- `RESULT rv probe-control away differs_at_tie=0 differs_off_tie=18`
- `RESULT rv probe-control optimizer differing_iterations_at_tie=0 off_tie=72`

So the quantified claim, "17 / 11 tied inputs, 0 differing", has no control that would have moved at a tie. A probe that compared outputs wrongly at ties would print the same RESULT lines.

**The conclusion is still right.** Two checks of my own (`rv_equiv_probe.py`) confirm it:
- Ties counted inside the compiled production function, by an append in the comparison itself rather than by recomputing: `away ties_in_function=17 of 49` and `optimizer tie_iterations=11 of 144`. Both match the probe's `ties=` figures.
- Tie-only controls, which change the result only when the two sides are equal, differ on the same grid:
  - away: `if last < first or last == first and (first := first - timedelta(days=1)):` -> `control_differs=17`, which is every tie.
  - optimizer: `idx = i if i < last else (last - 1 if i == last and last > 0 else last)` -> `control_differs=6`. The other 5 tied cases have `last == 0`, where this control cannot move.

**Owed (small):** give `equiv_probe.py` tie-only controls of this kind, so its control exercises the comparison at equality, and re-quote the counts in both triage rows and the body. Nothing else in round 2 needs to change.

## What round 2 fixed (verified)

- Owed item 1, R8: killed. `R8 Lt flips wrong way fails=1`; `h()` pins `<` to `<=`.
- Owed item 2, R5: killed. `fails=3`, including the new C7 check that a comparison spanning two lines yields no site.
- Owed item 3, the equivalents: disclosed in the body, and triaged as `equivalent` under keys that retire exactly those two sites.
  - `--list CMP_BOUND` shows `pinned` only for away.py:558 and optimizer.py:4742, then `946 site(s) in 55 file(s), 944 unpinned, ratcheted`.
  - Ratchet: `4853 unpinned site(s) of 5466 candidate sites, 4855 at the ratchet base 51ce8f2a...; the ledger agrees with the deterministic inventory`, then `MUTATION TABLE PASSED (empty scope)`.
  - Inventory: `head sites=5466 sha1=1ba97b4cecd5 unpinned=4853` and `origin/main sites=4520 sha1=c141b52379cc unpinned=3909`.
  - The equivalence is real: the probe prints `mutant_differs=0` at both sites, and my own tie-only controls above show the grid can see a tie.
- Owed item 4, drain: the body now gives at least 944/40, about 24 nights, and about 944/37, roughly 26 nights, at F10.5's 37-of-40 slice. The arithmetic is correct. I did not re-measure the 37/40 figure.
- Owed item 5, refusal text: it now names comparison bounds (mutation_table.py:2473).
- My mutants.py re-run against this head:
  - Killed: E1 (4 failed), M1 (1), M4 (1), R2 (2), R3 (2), R5 (3), R7 (3), R8 (1), R10 (3).
  - Survivors: R6 and R9, both equivalent as measured in round 1. M0 prints 0 failed.
- `mutation_budgets.json`: `keys_changed=['_comment']`, so no cap moved. VERSION, manifest, RELEASE_NOTES and both claim files are untouched. `git merge-tree` against origin/main: rc 0.
- Code owner: `tests/mutation_table.py` is `@tvofi`'s. The approving review comes under tvofi's mandate, not this verdict.

## CI (check-runs API, every run on 5009fe47; waitci DONE total=35)

The only non-green conclusions:
- `nightly-status=failure`. Its log reads `NIGHTLY ABSENT: ... mutation-ledger, mutation-ledger-push did not run in that scheduled run`. That is main's red, because the nightly predates the fix. This PR's three-dot diff touches no workflow, plan, HANDOVER or foreign delivery row, so the step-11 exemption applies and no Root cause section is owed.
- `pr-contract` and `budget-raise-gate` each have a `cancelled` run, superseded by a `success` run on the same head.
- 307ecf6c and 21fbd8cf carry no red run.

Non-blocking: the body's Figures still names the ratchet base aa7a8119. The base is now 51ce8f2a, and the count is identical, 4855.

Not run locally: entities.py in full, closures, features.py and the goldens. CI ran them on this head and they are green.
