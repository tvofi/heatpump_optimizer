Fix review: merge 79c54d79eac81ae4ea74e065445dbb5ad11c7633

bus-nonce: 94e40ef254bd5a144047eb6b75381f13

This is round 3 of review for #3658, a delta review over the reviewed head 1f6ea62fd0345ac0759997621fffe315ea11b139. The PR's own delta is a527be6f19. The head 79c54d79ea is a merge of a527be6f19 into 1f6ea62fd0, and its tree is identical to a527be6f19's (ev/merge-commit-tree-equal.txt). The delta changes only the instrument page, the module docstring and the self-test, so the scope stays the delta and is not widened (fix-review.md step 12).

## Evidence

- Head: `git ls-remote origin refs/pull/3658/head` returns 79c54d79eac81ae4ea74e065445dbb5ad11c7633, and the body's `## Head` names it (ev/HEAD.txt).
- Previous finding resolved: the mutant `net-all-pages` (`daily[-1][1] - daily[0][1]` to `hist[-1][1] - hist[0][1]` in `slip_line`) is now KILLED by the new case `closure_slip: the net move is over the daily samples, ...`. NULL SURVIVED. I re-spelled the mutants myself, applying each to `tools/audit/seat/round_metrics.py` and running `--self-test --no-mutants` (ev/mutant_run-r3.txt). Also KILLED: net-first-hist, net-sign, net-second-sample, net-no-day. One SURVIVED: net-abs (see Findings).
- The block's other ask is met. The instrument page and the docstring now both say the net is over the daily samples: the last sample's forecast less the first's (ev/delta.diff).
- Self-test at head: `python3 -I tools/audit/seat/round_metrics.py --self-test` returns rc 0. It prints 100 `ok` lines and 50 `mutant killed` lines, including `slip net daily`, and ends `round_metrics self-test: ok (with mutants)`. That matches the body's figures (ev/selftest-head.txt).
- CI: `merge_train.py classify 79c54d79ea --pr 3658` printed `GREEN 79c54d79eac81ae4ea74e065445dbb5ad11c7633 pending: none red: none`, rc 0, at 22:02Z (ev/classify.log). There is no red, so no `## Red checks` answer is owed. The packet's `tests / nightly-status` failure is outside the required set, and classify reads GREEN.
- Merge: `git merge-tree --write-tree origin/main 79c54d79ea` returns rc 0. No conflict (ev/merge-tree.txt).
- VERSION, the manifest, the notes heading, `custom_components/`, golden files and claim files are all untouched in the three-dot diff (ev/threedot-stat.txt).
- Roles: main changed `dev/governance/roles/COMMON.md` (the finder's contract) since the merge base. `fix-review.md` is unchanged, and I followed main's copy through role_pack (ev/roles-current.txt).
- Figures not re-derived by me: the structure ratchet, archscore `dS +0.0000 NULL` and `MODE: SCOPED -- 0 script(s) run`. These come from CI, which is GREEN at this head.
- The body's three `## Unpinned sites` (lines 302, 338 and 350, from earlier reviewed commits) are disclosed there. They are outside this round's delta.

## Findings

- Residual: mutant `net-abs` survives. It changes `{(daily[-1][1] - daily[0][1]) / DAY_S:+.2f}` to `{abs(daily[-1][1] - daily[0][1]) / DAY_S:+.2f}`. Under it, a round whose forecast closure ends earlier than its first sample prints a positive net. No case has a negative net, so the sign is pinned only for later moves. The line was reviewed in round 2, and this round's delta does not change it, so by step 12 it does not widen this review or block it. A case with a net-earlier history, plus an in-file `MUTANTS` entry, would pin it. Carry: dismissed: outside the round-3 delta scope (fix-review.md step 12); left for the orchestrator to route with the body's listed unpinned sites
