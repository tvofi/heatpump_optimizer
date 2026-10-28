Triage batch 59 rules V185 as P273 and V186 as P274. It is the next rolling batch under V182, after batch 58 (#2934, merge-verdicted at `56e61dc9e`).
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

No product behaviour changes: the diff is one markdown file under `dev/programme/triage/`.

## Head

`a00d97646781b5286a631c4a8f7c0f969e1e866b`; the file is the whole diff against `b0b2d7697f8c5baaef2c082d9bf3242b57249e68`.

## Mutation proof

This file's only consumer is `tools/audit/seat/roster_edit.py`'s triage gate, `ruling_verdict` (line 455).
- On the committed file, it reads P273 as `REJECT` and P274 as `ACCEPT`.
- A text citing `#P273` is refused as `not an ACCEPT ruling (REJECT)`. The P274 carry text passes (`triage_refusal` returns None).

## Null control

- With the file absent, a text citing it returns `the triage ruling dev/programme/triage/s6-batch59.md is not on the roster branch or origin/main`.
- For the ruling's measurement, the comparison was shown able to fail. The coil glyph's arc in an archived copy of origin/main was changed (`c1.3-2.9 2.6-2.9 3.9 0` to `c1.3-2.0 2.6-2.0 3.9 0`) and the figures re-rendered. `hydronic-coil.svg` then differs by 2 lines, and the two figures that draw no coil stay identical.

## Figures

- Render: `HPO_QA_OUTDIR=<out> HPO_QA_PREFIX=hydronic- node tests/setup_qa_render.mjs <plandata>` on `git archive origin/main tests custom_components`, then `cmp` against `git show origin/main:docs/img/model/<name>.svg`. Result: 3 of 3 identical. The setup page draws from `tests/card_rig.mjs`'s topologies, not from plan values.
- Card commits after the last regeneration (`c62c56cb5`) are `99367cbc3`, `c89e5b5db` and `59c744f4c`. None of them touches the setup drawing.
- `git merge-base --is-ancestor 75ac45353 2cc4d5ebc` is false: the pre-study does not contain #2841.
- P274: `git ls-remote origin 'refs/heads/handoff/*'` lists 153 refs, 118 of them fully on main. Commits not on main, by author and committer: 951 tvofi noreply, 28 `noreply@anthropic.com`, 9 github-actions and 2 `seat@users.noreply.github.com`.
- P274: `ref_privacy.py guard --ref x --commits 4a7ccd930 --over origin/main` gives rc 0 on main. V186's `r10-fly-prepr-summary` instance was therefore not refused by main's guard. Of the 35 open refs, 3 fail the guard today, each on a co-author trailer (`audit-r10-arch-s2`, `audit-r10-arch-s3`, `audit-r10-find-B9`).

## Red checks

`none`. A ref with no pull request has no checks.

## Forward-carry

none

## Friction

none
