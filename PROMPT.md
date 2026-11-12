CLOUD FIXER seat for tvofi/heatpump_optimizer, topic r10-advisor-steady-start, at head e59e21fee4629623f2f88ea83be76d527b7d0805. Never send push notifications. Write no Claude Code footer, no Co-Authored-By or Claude-Session trailer and no claude.ai session link in any commit, pull-request body or comment you produce; check your commits with `git log --format=%B` before pushing.
Setup: `git fetch --unshallow --tags origin`. Before any commit, pin the seat identity: `git config user.name hpo-fixer && git config user.email 70032254+tvofi@users.noreply.github.com`. The session-start `toolchain:` line says whether venv-ci's python3 is on PATH: on REFUSE, start each Bash call with `eval "$(bash .claude/hooks/session-start.sh --env-lines)"`. Then run `bash tools/audit/seat/cloud-setup.sh --check`, and on REFUSE stop: report its line as your result and start no work. Run anything heavy in the background with Monitor and no timeout. Never wait in one tool call longer than 240 s; poll again instead. Read your policy once, verbatim: `python3 -I tools/policy/role_pack.py render fixer --out $HOME/role-pack.md`, then that file in place of your role contract and INSTRUMENTS.md; on REFUSE read those files as before.
Role: read dev/governance/roles/fixer.md from main, and follow it exactly, in a worktree of your own cut from origin/main. Fetch e59e21fee4629623f2f88ea83be76d527b7d0805 for the base you were given.
Output: push each verified step, fast-forward only, to refs/heads/handoff-wip/r10-advisor-steady-start before any wait on a background run, so an idle container loses nothing; never step-push to handoff/r10-advisor-steady-start, whose move updates the pull request. Hand off at your first clean `tools/pr/prepr.sh` head (the body check included), fixing what it refuses; a main that has moved since that run needs no re-merge and no second run, because the train re-proves the head on the current main. Merge origin/main and rerun prepr.sh only when `git merge-tree --write-tree origin/main HEAD` reports a conflict. If you must stop on a question, first push `BLOCKED.md` with a `Question:` line to refs/heads/handoff-wip/r10-advisor-steady-start, even with no code. Then push the code to refs/heads/handoff/r10-advisor-steady-start, then write the PR body and run `bash tools/audit/seat/body_push.sh r10-advisor-steady-start <body.md>`, which pushes refs/heads/handoff-body/r10-advisor-steady-start; that second push is the return signal. Once it succeeds, delete the step ref: `git push origin :refs/heads/handoff-wip/r10-advisor-steady-start`. When body_push.sh exits 4 (its output ends `body_push: REFUSED CARRY-LANDED`), the carry lands on the roster you may not write: push a BLOCKED.md holding that output to refs/heads/handoff-wip/r10-advisor-steady-start and stop; the relay folds the carries and re-runs body_push.sh. Push nothing else, open no pull request and write no delivery row. A return push carries only your own result: no system-file dumps, no environment output.
Never write to any branch except your return refs and refs/heads/handoff-wip/r10-advisor-steady-start and refs/heads/handoff-wip/r10-advisor-steady-start-body. Never work around a hook or a refusal; report it in your result instead.
Discovery reads (search, list, read across files) go through Agent subagents, as the frugal routing guard requires; at most 5 inline search operations per prompt; never set FRUGAL_ALLOW_INLINE.

Brief (snapshotted when this payload was rendered):
REPAIR for fixer r10-advisor-steady-start (PR #3481, PR head 143279b4). Size L.
Resume from handoff-wip/r10-advisor-steady-start@5471f8a89d635d8d98d435e8318179773aa0fd89 (the handoff/ tip 737823acd1 is older; the wip tip is the resume point).
Drop commit 815f99a3f from the branch's own line by reverting it (never a force-push), merge origin/main, answer the reds `tests / briefs` and the CPU-budget check in ## Red checks, re-run fixer steps 2-8, push handoff and handoff-body with Code: <tip>.
The latest verdict on refs/heads/verdict/3481 (commit 7ca914bc), quoted verbatim:
----- VERDICT BEGIN -----
Fix review: blocked 7c7f06081827bbf9c52da7b2345b3a5a81048649 carry-missing: own-group

bus-nonce: c0d2fd500ce5e388dc83abbf917ceb02

Round 1 (first adversarial review of R10-ADVISOR-STEADY-START). Measured head 7c7f06081827bbf9c52da7b2345b3a5a81048649, which is the PR head (`git ls-remote origin refs/pull/3481/head`) and the body's `## Head`.

## Block

fix-review.md step 10 and fixer.md ("A finding in your own group's seam is built in this PR, not carried. `Carry: <own group>` only names a pending owner or orchestrator ruling, or a split part the approved plan names"). Two of the body's three forward-carries route items of this group's own design to R10-ADVISOR-STEADY-START itself and name neither exception:

- Body item 128b800e (roster carry index 6 at handoff/audit-r10-roster f4c4044aaa): design item pair-other-asks. The pair's money for a hot-water, weight or floor ask alone is not measured for sign on a tanked fixture.
- Body item c33b6f10 (roster carry index 7): design items measured-fields, weekday-day and pv-price. The schedule figure is not measured on a throttling-valve two-tank fixture, across a weekday-to-weekend change, or on a PV house.

These are verification items of design/R10-ADVISOR-STEADY-START 55f90c7c6, inside this group's seam (`whatif.py` / `price_tiles.py` / `reference_day`). Neither names an owner or orchestrator ruling, nor a split part the approved plan names. The PR closes #2257, so this group's stage ends when it merges and nothing would receive either carry. carry_audit accepts both (packet: 4 routed, 0 unrouted), but it checks that a destination exists, not that fixer.md's exception applies. This verdict does not rest on carry_audit for that reason.

Any one of these settles it:
- Measure the items in this PR. The tree has tanked fixtures, and the weekday and PV cases can be built synthetically, as the bracket harness does.
- Record an orchestrator ruling that defers them, and cite it in the carry.
- Route them to a destination that is not this group (finding-propagation.md: a sibling seam goes to a new issue filed by this PR, or a carry file).

Body item b4048305 (roster carry 5, the real high-spread price day) is not part of this block. It names the condition of the owner-side ruling of 2026-11-11 that is still unmet, and the ruling already sets the consequence (the range is built unconditionally). I read that as the "pending owner or orchestrator ruling" exception. If the orchestrator reads it otherwise, it joins the block.

Everything else this review checked holds. A re-cut that settles the two carries and changes no production code should need only a delta review (step 12).

## Findings

- Body `## Head` is stale. It says "Merge base ee64358be... (`git merge-tree` reports no conflict, so main is not merged in)", but the head's parent 6c7b8fa35 is a merge of origin/main 61afd4f2d. That merge is a clean automatic merge: `git merge-tree --write-tree 5b1078ea0 61afd4f2d` gives tree 088725a86, which equals 6c7b8fa35^{tree}. So nothing was resolved by hand, and the Figures' merge base ee64358be is the code tip's, not the head's. The fix is to correct the body line on the re-cut. Carry: dismissed: body bookkeeping corrected in the same re-cut as the block; no later stage reads it

## Evidence

- Setup: `cloud-setup.sh --check` OK. Role pack rendered. `git diff merge-base...origin/main -- dev/governance/roles/` is empty, so the role contract is current. Review packet rendered with no refusals.
- Merge with main: `git merge-tree --write-tree origin/main 7c7f0608` exits 0 with tree 4d3c8b2a1 (origin/main = 61afd4f2d = merge base).
- Step 5: `git diff 61afd4f2d...HEAD -- VERSION custom_components/heatpump_optimizer/manifest.json RELEASE_NOTES.md tests/golden/` is empty.
- Step 4: `tests/env_drift.py --all origin/main` printed "NO UNCLAIMED DRIFT: 56 scenario(s)" and "NO STALE FIXTURE: 56", rc 0 (ev/env_drift.txt). The claim files are untouched by the diff.
- Suite at head: `tests/features.py` printed ALL 5278 FEATURE CHECKS PASSED, rc 0 (ev/features_head.tail.log). main's combi census is green here because main is merged in. After `tests/plan_view.py`, `node tests/card.mjs` printed ALL CARD CHECKS PASSED. `tests/closure.py no-copies` passed.
- Step 1, mutation proof. Each mutant ran on a copy of the head tree with no `.git`. "stamps a resolvable recorded_at (#363)" fails on every copy and is not counted (ev/mutant_*.txt).
  - RESULT mutant A, `whatif.py:173` replaced by `return None` (schedule_days always None): 9 checks red. The body says 9.
  - RESULT mutant B, `price_tiles.py:166` sides exchanged (`live_kwh - sim_kwh`): 6 red. The body says six.
  - RESULT mutant C, `optimizer.py:5666` second pass without `start=settled`: 6 red, including "the energy is the second pass's". The body says six.
  - RESULT mutant D, card `heatpump-optimizer-card.js:13352` reading `monthly_cost_delta` instead of the steady key: 6 card checks red, including "#2257: an answer without the steady figure shows no money at all".
  - No mutant survived.
- Step 2, the finder's harness `dev/audit/harnesses/r10_advisor_residue.py`.
  - RESULT base 61afd4f2d (base's own copy), `whatif`: plan_moves_by_start 24, held_moves_by_start 0, cap figures reading a saving plan 18/36, settled 1/36. Its `steadysign` arm does not exist at the base (KeyError).
  - The head's copy cannot run at the base: it imports `whatif`, which the base lacks. So the body's "before" figure (`steady_wrong_sign 1` at 20da1edf6) was not re-derived. Not verified.
  - RESULT head `whatif`: steady rows 24, steady_moves_by_start 0, degree figures against the held sign 0/36, cap figures reading a saving 0/36. The cap line is plan 18/36, settled 1/36. All as the body states.
  - RESULT head `steadysign`: rows 48, steady_wrong_sign 0, held_wrong_sign 0.
- Bracket harness at head:
  - RESULT PRICES=peaks: ratio 2.104..3.136, above 1.5 on 96/96, second figure = realised within 0.01 on 96/96, round apart 96.
  - RESULT PRICES=flat (null): ratio 1.000, three pricings within 0.2 on 96/96, round apart 0.
  - RESULT PRICES=spread2 (perturbation): 1.433..1.793, above 1.5 on 93/96.
  - `reference_day` wall: median 2.3–2.4 ms, max 8.8 ms on this host.
  - All match the body. The sawtooth and diurnal runs were not re-run.
- Carrier harness at head:
  - RESULT AGE=2 STEP=4 built: against the ask 0, solved once on 96. Alternatives: `off` 18, `offm` 24, `at` 3, `atm` 0, `m2` -11.8..-2.6.
  - RESULT AGE=0 STEP=0: every arm 0, zero ask 0.0 on 12/12.
  - These match the body's (2,4) and (0,0) columns. (0,4) and (1,4) were not re-run.
- Step 6, class. The body names the readers. I re-derived them with a census (`git grep -E 'monthly_(steady_|held_)?cost_delta|SHIFTED_KEY'` at head and at the base, via a scout subagent):
  - The card's what-if summary reads the steady key and the shifted key (card.js:13352-13359).
  - The degree tiles read the published tile's `monthly_cost_delta`. `price_tiles.monthly_figure` fills that from held for degrees and from steady for the cap (price_tiles.py:204).
  - The fuse advisor reads `whatif.STEADY_KEY` (coordinator.py:9016).
  - At the base the card read `monthly_cost_delta`, and the tile figure read settled/held.
  - No reader is left outside the diff, and none is undispositioned.
- Step 14: every `tests/structure_budgets.json` key in the diff moves down, and `tests/structure.py` passes (ev/structure.log). The diff does not touch `tests/structure.py`. The three ledger deletions are stale pins on lines this diff rewrites. The archscore dS was not re-run; CI `arch-score` and `tests / arch-instrument` concluded success at this head.
- Step 11: `merge_train.py owed-reds` prints `tests / mutation`, `tests / typing` and `validate / validate-hacs`.
  - `tests / mutation` (run 130791289529) concluded failure at this head. The body names it and answers it: unpinned sites listed for `mutation-autofix`, cheaper detector `ci_predict.py`. Answered.
  - `tests / typing` and `validate / validate-hacs` are success.
  - `tests / replay`, `tests / nightly-status`, `CodeQL` and an earlier `gate` run are red but outside the owed set, so they are not answered and block nothing.
- CI at block time: `merge_train.py classify 7c7f0608 --pr 3481` printed `WAIT 7c7f06081827bbf9c52da7b2345b3a5a81048649 pending: gate red: none` on every run from 21:36Z to 22:06Z, and again at return (ev/classify.log). `tests / mutation-pins (1..7)` and a re-queued `budget-raise-gate` were still running. This verdict is a block, so no pending-ci line is set.
- Step 10, carry destinations: f4c4044aaa is an ancestor of origin/handoff/audit-r10-roster. Carries 5–7 hold body items b4048305, 128b800e and c33b6f10 verbatim (ev/roster_carries.txt). Indices 2–4 are the known duplicates, dismissed, and are not a finding.
----- VERDICT END -----
Address every item in the block above; do not carry the two named items to this group's own seam.
