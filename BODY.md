Triage batch 59 rules V185 as P273, V186 as P274, the orchestrator's 2026-10-29T04:14Z carry_audit proposal as P275, its 05:58Z abandoned-merge-worktree proposal as P276, and its P277 (owed family omits verdict levels). It is the next rolling batch under V182, after batch 58 (#2934, merge-verdicted at `56e61dc9e`).
- **P273 (V185, card docs may still show the pre-R10-CARD-VOICE setup drawing): REJECT.**
  - V185 asked for a measurement first and a size-S docs fly-in only if something differed. This seat took the measurement, and nothing differs.
  - The premise comes from the card-symbols pre-study (`2cc4d5ebc`, 2026-10-20), written before #2841 merged (2026-10-26). #2841 itself rewrote `docs/dashboard-card.md` and all three `docs/img/model/hydronic-*.svg`.
  - The spring is the shipped design: the wood tank's disc is the coil's spring while a coil is configured, and dimmed while that coil is not modelled (`heatpump-optimizer-card.js:4002-4008`). The four `spring` hits in the doc describe it.
  - Re-rendered from origin/main's card by `tests/setup_qa_render.mjs`, all three figures are byte-identical to the committed ones.
- **P274 (V186, cloud fixer commits carry identities the privacy guard refuses, found only at the opener): ACCEPT, narrowed, to R10-FLY-NO-FOOTERS.**
  - Prevention: `cloud_dispatch.py`'s fixer and probe setup pins `git config user.name hpo-fixer` and `user.email 70032254+tvofi@users.noreply.github.com`. It lands with or before P253's refusal arm.
  - Detector: `body_push.sh` guards the code ref `handoff/<topic>` over origin/main before it pushes the body, which is the return signal.
  - Measured: 28 commits authored `noreply@anthropic.com` sit on 8 open handoff refs pushed 2026-10-28. Main's guard passes them today; P253's class will refuse each at the opener.
  - One held roster op (`append-carry R10-FLY-NO-FOOTERS`), released once this file is on main.
- **P275 (carry_audit over-fires on verdict lines, and the train PARKs on it): ACCEPT, narrowed, to R10-ORCH-REVIEW-PACKET; option (a) REJECT.**
  - The review packet gives the reviewer the exact `carry_audit.py check` command to run on its own `verdict.md`. The verdict is returned only at rc 0, and `fix-review.md` gains one sentence binding the step.
  - Of the two named PARKs, #2914 `c63349c9` was a correct fire (a "not blocking" note with no `Carry:`). #2887 `da4b2420` was an over-fire ("residual" in a carry title, under `## Evidence`).
  - Option (a) was measured: the low-risk narrowings clear 2 of the 16 `evidence` flags across 396 verdicts. Clearing the rest would also hide #2612 `434dcf9d`, a real unpinned-mutant defect.
  - One held roster op (`append-carry R10-ORCH-REVIEW-PACKET`), released once this file is on main.
- **P276 (abandoned merge worktrees hold a PR's branch): ACCEPT, narrowed, to a new fly-in R10-FLY-ABORT-OWN-MERGE; options (a) and (b) REJECT.**
  - The cause is at two producers. `remerge_main.sh:21` exits on `MERGE CONFLICT` without `git merge --abort` (#2935, #2936: `train.log` then shows `NOT released ... contains modified or untracked files`). `pr_args.sh:105`'s `checkout --detach` fails on a conflicted index (#2917, the `upd-` worktree).
  - Each aborts its own failed merge. Both start from `origin/<branch>` and merge only remote refs, so nothing is lost.
  - (a) would free another seat's dirty state on a snapshot guess, widening the guard P193 kept. (b) misses all three, which are open PRs that `worktree_gc.sh` keeps "ever".
  - One held roster op (`append-group R10-FLY-ABORT-OWN-MERGE`), released once this file is on main.
- **P277 (the tick's MERGE-READY and BLOCKED-UNFIXED lines are outside the owed family): ACCEPT, as a new fly-in R10-FLY-OWED-LEVELS.**
  - `owed_unactioned.py:50`'s `FAMILY` gains both kinds, keyed `#<N>` with `<head8>` as the id, with a self-test arm and mutant for each. `sweep_template.md` already runs the tool, so it needs no change.
  - Measured from the `verdict/*` refs: blocked #2933, #2925 and #2872 and merge-verdicted #2896 and #2939 stood 5-11 h. Main's merges fell from 9 in the 23Z hour to 1-2 an hour.
  - One held roster op (`append-group R10-FLY-OWED-LEVELS`), released once this file is on main.

No product behaviour changes: the diff is one markdown file under `dev/programme/triage/`.

## Head

`5ad92aecd1263af29d00ede9976826c3b7143c5e`; the file is the whole diff against `b0b2d7697f8c5baaef2c082d9bf3242b57249e68`.

## Mutation proof

This file's only consumer is `tools/audit/seat/roster_edit.py`'s triage gate, `ruling_verdict` (line 455).
- On the committed file, it reads P273 as `REJECT`, and P274-P277 as `ACCEPT`.
- A text citing `#P273` is refused as `not an ACCEPT ruling (REJECT)`. The P274 and P275 carry texts and the P276 and P277 group briefs and resume notes pass (`triage_refusal` returns None). A resume note naming `triage P276` without the citation was refused before it was fixed.

## Null control

- With the file absent, a text citing it returns `the triage ruling dev/programme/triage/s6-batch59.md is not on the roster branch or origin/main`.
- For the ruling's measurement, the comparison was shown able to fail. The coil glyph's arc in an archived copy of origin/main was changed (`c1.3-2.9 2.6-2.9 3.9 0` to `c1.3-2.0 2.6-2.0 3.9 0`) and the figures re-rendered. `hydronic-coil.svg` then differs by 2 lines, and the two figures that draw no coil stay identical.

## Figures

- Render: `HPO_QA_OUTDIR=<out> HPO_QA_PREFIX=hydronic- node tests/setup_qa_render.mjs <plandata>` on `git archive origin/main tests custom_components`, then `cmp` against `git show origin/main:docs/img/model/<name>.svg`. Result: 3 of 3 identical. The setup page draws from `tests/card_rig.mjs`'s topologies, not from plan values.
- Card commits after the last regeneration (`c62c56cb5`) are `99367cbc3`, `c89e5b5db` and `59c744f4c`. None of them touches the setup drawing.
- `git merge-base --is-ancestor 75ac45353 2cc4d5ebc` is false: the pre-study does not contain #2841.
- P274: `git ls-remote origin 'refs/heads/handoff/*'` lists 153 refs, 118 of them fully on main. Commits not on main, by author and committer: 951 tvofi noreply, 28 `noreply@anthropic.com`, 9 github-actions and 2 `seat@users.noreply.github.com`.
- P274: `ref_privacy.py guard --ref x --commits 4a7ccd930 --over origin/main` gives rc 0 on main. V186's `r10-fly-prepr-summary` instance was therefore not refused by main's guard. Of the 35 open refs, 3 fail the guard today, each on a co-author trailer (`audit-r10-arch-s2`, `audit-r10-arch-s3`, `audit-r10-find-B9`).

- P275: the verdict files come from the `verdict/*` refs, 396 of them, read by origin/main's `carry_audit.items()`. Of 367 merge verdicts, 82 hold a flagged item with no `Carry:` of its own; since 2026-10-26 it is 17. The narrowing test ran on a scratch copy of `carry_audit.py` (code spans stripped before DEFERRED/NONBLOCK, and "blocks no merge" added to NOT_REQUIRED): `evidence` flags went from 16 to 14.

## Red checks

`none`. A ref with no pull request has no checks.

## Forward-carry

none

## Friction

none
